# Sistemas meta: save, economía y servicios

> **Cuando cargar este archivo:** al implementar guardado/carga, monedas/inventario/tienda, IAP, ads, notificaciones locales, analytics/crash reporting o lógica dependiente del tiempo (daily rewards, idle) en un juego Unity. El QUÉ/POR QUÉ de diseño está en [ver: gamedev/psicologia-retencion-negocio] y [ver: gamedev/mecanicas-sistemas]; aquí está el CÓMO en Unity 6.x (estado a julio 2026).

## 1. Arquitectura: el estado del jugador vive en datos, no en MonoBehaviours

Regla central: **todo lo que deba sobrevivir a la sesión es una clase C# plana `[Serializable]`**, sin herencia de `UnityEngine.Object`. Los MonoBehaviours leen/escriben ese estado; nunca SON el estado.

| Capa | Qué es | Ejemplo |
|---|---|---|
| **Definiciones** (inmutables, assets) | ScriptableObjects: qué existe en el juego | `ItemDef`, `CurrencyDef`, `ShopOfferDef` [ver: unity/csharp-patrones] |
| **Estado** (mutable, se serializa) | Clases planas `[Serializable]`, solo campos | `PlayerState { int coins; List<OwnedItem> items; }` |
| **Presentación/lógica** | MonoBehaviours + servicios que operan sobre el estado | `WalletService`, HUD que escucha eventos |

- El estado referencia definiciones por **id estable** (string/GUID propio), nunca por referencia directa al asset: JSON no puede serializar referencias a `UnityEngine.Object` y los nombres de asset cambian.
- Un solo objeto raíz (`SaveFile`) agrega todo el estado → un solo punto de save/load, trivial de versionar y de testear sin escena [ver: testing-qa].
- Reglas de serialización de Unity (qué campos entran, `[SerializeField]`, sin propiedades): [ver: unity/arquitectura-unity].

## 2. Save/load robusto

### Dónde: `Application.persistentDataPath`
Verificado en Unity Manual 6.2 — rutas reales por plataforma:

| Plataforma | Ruta |
|---|---|
| Windows | `%userprofile%\AppData\LocalLow\<CompanyName>\<ProductName>` |
| macOS (player) | `~/Library/Application Support/unity.<company>.<product>` |
| Android | `/storage/emulated/<userid>/Android/data/<packagename>/files` |
| iOS | `.../Containers/Data/Application/<guid>/Documents` |
| Web | IndexedDB del browser (`/idbfs/<hash>`) — probar persistencia REAL en browser, no en Editor |

`Company Name` y `Product Name` (Player Settings) forman la ruta: fijarlos el día 1 [ver: unity/build-plataformas]. En iOS/Android los archivos sobreviven updates de la app; se pierden al desinstalar.

### Formato: JSON con `JsonUtility` (default) o Newtonsoft (si hace falta)

| | `JsonUtility` (built-in) | Newtonsoft (`com.unity.nuget.newtonsoft-json`) |
|---|---|---|
| Soporta | Clases/structs `[Serializable]`, solo **campos** | Dictionaries, propiedades, polimorfismo, `JObject` |
| NO soporta | `Dictionary<>`, propiedades, tipos top-level (primitivos/arrays sueltos), polimorfismo | — |
| Rendimiento | Más rápido que las librerías .NET típicas, GC mínimo (doc oficial) | Más pesado |
| Riesgo en build | Ninguno | **Stripping**: preservar con `link.xml` o revienta solo en IL2CPP [ver: unity/build-plataformas] |

API exacta: `JsonUtility.ToJson(obj, prettyPrint)`, `JsonUtility.FromJson<T>(json)`, `JsonUtility.FromJsonOverwrite(json, obj)` (obligatorio para MonoBehaviour/ScriptableObject). Regla: empieza con `JsonUtility` y modela el save sin diccionarios (listas de pares id/valor); pasa a Newtonsoft solo si necesitas migraciones estructurales o polimorfismo.

### Escritura atómica: temp + rename
Un crash/kill a mitad de `File.WriteAllText` deja el save corrupto. Antídoto: escribir a un temp y reemplazar de forma atómica con `File.Replace` (.NET, deja backup del anterior). Ojo verificado en docs .NET: `File.Replace` lanza `FileNotFoundException` si el destino aún no existe → primera escritura con `File.Move`.

```csharp
public static void SaveAtomic(string json, string path)
{
    string tmp = path + ".tmp";
    File.WriteAllText(tmp, json);              // 1. escribir completo al temp
    if (File.Exists(path))
        File.Replace(tmp, path, path + ".bak"); // 2. swap atómico + backup
    else
        File.Move(tmp, path);                   // primera vez: no hay destino
}

public static string LoadWithFallback(string path)
{
    if (File.Exists(path))
        try { return File.ReadAllText(path); } catch (IOException) { }
    string bak = path + ".bak";                 // corrupto/ilegible → backup
    return File.Exists(bak) ? File.ReadAllText(bak) : null;
}
```

Al cargar: si el JSON no parsea (`try/catch` alrededor de `FromJson`), caer al `.bak` antes de resetear progreso. Cuándo guardar: en cada transacción importante (compra, level complete) y en `OnApplicationPause(true)` en móvil — no confíes en `OnApplicationQuit`, en móvil puede no ejecutarse.

### Versionado y migración
Todo save lleva `int version` desde el día 1. Migración = cascada de pasos v(n)→v(n+1), nunca saltos directos:

```csharp
[Serializable] public class SaveFile { public int version = 3; /* ...estado... */ }

SaveFile Migrate(SaveFile s)
{
    if (s.version < 2) { s.gems += s.oldPremiumPoints; s.version = 2; }
    if (s.version < 3) { s.settings ??= new SettingsState(); s.version = 3; }
    return s; // cada release solo añade UN paso nuevo al final
}
```

- Cambios **aditivos** (campo nuevo con default) son gratis con `JsonUtility`: el campo ausente queda en su valor por defecto — solo súbele la versión.
- Cambios **estructurales** (renombrar, mover, cambiar tipo): deserializar a `JObject` (Newtonsoft) o mantener los campos viejos en la clase un tiempo y copiarlos en el paso de migración.
- Test de regresión: guarda fixtures de saves reales de cada versión publicada y cárgalos en CI [ver: testing-qa].

### PlayerPrefs: qué sí y qué no
Verificado (Unity 6.2): guarda solo `string`/`float`/`int`; backend por plataforma (registro en Windows, `NSUserDefaults` en iOS, `SharedPreferences` en Android, IndexedDB en Web con límite ~1 MB); la doc oficial dice explícito **"Don't use PlayerPrefs data to store sensitive data"**.

| SÍ en PlayerPrefs | NO en PlayerPrefs |
|---|---|
| Settings (volumen, idioma, calidad) | Progresión, monedas, inventario |
| Flags de FTUE ("tutorial visto") | Cualquier cosa que un cheat pueda querer editar |
| Última cuenta/slot usado | Datos > unos pocos KB o estructurados |

Llama `PlayerPrefs.Save()` tras escrituras críticas: el flush automático ocurre al cerrar limpio, un kill del proceso lo pierde.

### Cifrado ligero (anti-edición casual, no seguridad real)
Un JSON legible en `persistentDataPath` se edita con cualquier editor de texto. Para juegos single-player esto es opcional (es SU save); hazlo si hay leaderboards, economía con IAP o logros compartidos:

- **Detección** (suficiente casi siempre): guarda junto al JSON un HMAC — `new HMACSHA256(key).ComputeHash(bytes)` — y recházalo si no cuadra al cargar.
- **Ofuscación**: cifra el JSON con `System.Security.Cryptography.Aes` (clave en el binario). Cualquier clave embebida es extraíble: esto sube la barrera de "cualquiera con Notepad" a "alguien que descompila" — nada más.
- La única protección real es **server-authoritative** (el servidor posee el estado) [ver: multijugador-netcode]. No inviertas más aquí en un juego offline.

## 3. Economía cableada: monedas, inventario, tienda

La teoría (sources/sinks, una moneda por loop, pity, loot tables con pesos) está en [ver: gamedev/mecanicas-sistemas]. Implementación data-driven en Unity:

- **`CurrencyDef` (ScriptableObject)**: id, nombre display, icono, `bool isPremium`. **`ItemDef`**: id, tipo, rareza, refs a assets. **`ShopOfferDef`**: qué da, qué cuesta (ref a `CurrencyDef` + cantidad), condiciones. Diseño balancea en el Inspector sin tocar código [ver: unity/csharp-patrones].
- **Estado**: `List<CurrencyAmount>`/`List<OwnedItem>` en el `SaveFile` (pares id/cantidad — recuerda: `JsonUtility` no serializa `Dictionary`).
- **Un solo punto de mutación**: nadie toca `coins` directo; todo pasa por el servicio, que valida, registra el evento de analytics (sección 6) y guarda.

```csharp
public class WalletService
{
    readonly PlayerState state;                 // del SaveFile
    public event Action<string,int> OnChanged;  // (currencyId, newAmount)

    public bool TrySpend(string currencyId, int amount, string reason)
    {
        int balance = state.GetCurrency(currencyId);
        if (amount <= 0 || balance < amount) return false;
        state.SetCurrency(currencyId, balance - amount);
        Analytics.CurrencySpent(currencyId, amount, reason); // sink trackeado
        OnChanged?.Invoke(currencyId, balance - amount);
        SaveSystem.RequestSave();
        return true;
    }
    // Add(...) simétrico con Analytics.CurrencyGained(id, amount, source)
}
```

- La UI escucha `OnChanged` — nunca hace polling del balance [ver: ui-flujo-completo].
- El parámetro `reason`/`source` en CADA transacción es lo que luego permite auditar sources vs sinks en analytics; sin él, la economía es una caja negra.
- La tienda es una lista de `ShopOfferDef` renderizada: comprar = `TrySpend` + grant. Las ofertas de dinero real delegan en IAP (sección 4) — misma UI, otro backend de pago.

## 4. IAP con Unity IAP (paquete `com.unity.purchasing` 5.x)

Versión actual verificada: **5.4.1 (jul 2026)**. La 5.0 cambió la API entera vs 4.x — si un tutorial usa `IStoreListener` + `ConfigurationBuilder`, es de la era 4.x (sigue existiendo mucho contenido así: verifícalo contra el paquete instalado).

| Paso | API v5 (verificado en changelog oficial y manual UGS) |
|---|---|
| Inicializar servicios | `await UnityServices.InitializeAsync()` (requiere proyecto vinculado a UGS y IAP activado en el dashboard) |
| Punto de entrada | `StoreController` — wrapper unificado sobre `IProductService`, `IPurchaseService`, `IStoreService` |
| Productos | `ProductType.Consumable` (monedas), `NonConsumable` ("quitar ads"), `Subscription` (VIP); definidos en el juego Y en cada consola de tienda con el mismo product id |
| Catálogo | evento `OnProductsFetched` → poblar la tienda con precios localizados de la tienda, nunca hardcodeados |
| Compra | eventos `OnPurchaseConfirmed` / `OnPurchaseFailed` (reemplazan los callbacks de `IStoreListener`) |
| Restore | `RestoreTransactions` + evento `IPurchaseService.OnRestoreTransactions` |

Puntos que las tiendas exigen o que rompen en producción:

- **Validación**: en Apple, StoreKit 2 valida nativo — el `CrossPlatformValidator` clásico ya no es necesario en plataformas Apple (changelog 5.x). En Google Play sigue habiendo validación local (clave licenciada ofuscada) o server-side. Si la compra otorga valor competitivo o hay economía compartida, valida **server-side**; la local solo para juegos offline sin PvP.
- **Restore**: Apple **rechaza en review** apps con non-consumables/suscripciones sin mecanismo visible de restore → botón "Restaurar compras" en settings que dispare `RestoreTransactions`. En Google Play las compras existentes se recuperan al inicializar.
- **Grant idempotente**: el store re-entrega compras pendientes al inicializar (proceso murió entre pago y entrega). Otorgar el contenido debe poder ejecutarse dos veces sin duplicar (chequear "¿ya lo tiene?" antes de dar).
- El grant escribe en el `SaveFile` vía los servicios de la sección 3 y dispara save inmediato — perder una compra pagada por no guardar es el peor bug posible.
- Android + dinero: activar `Filter Touches When Obscured` (anti-tapjacking) [ver: unity/build-plataformas]. Loot boxes de pago → odds publicadas, requisito de ambas tiendas [ver: gamedev/psicologia-retencion-negocio].
- Qué monetizar sin quemar el juego (expresión/contenido/conveniencia, nunca poder ni dolor fabricado): [ver: gamedev/psicologia-retencion-negocio].

## 5. Ads: LevelPlay (rewarded como default sano)

Estado 2026 verificado en docs oficiales: la mediación de Unity es **Unity LevelPlay** (paquete `com.unity.services.levelplay`, versión 9.5.0; en Package Manager aparece como "Ads Mediation"). Trae los adapters de Unity Ads e ironSource Ads por defecto desde la 8.8.1. El paquete legacy `Advertisement` (Unity Ads directo) está en salida: desde el 1-abr-2026 Unity avisa de "reduced ad performance" para quien siga en él — proyecto nuevo = LevelPlay directamente.

Flujo mínimo (API verificada):

```csharp
using Unity.Services.LevelPlay;

LevelPlay.OnInitSuccess += _ => CreateRewarded();
LevelPlay.OnInitFailed  += e => Debug.LogWarning($"Ads off: {e}");
LevelPlay.Init("appKey"); // appKey del dashboard LevelPlay

LevelPlayRewardedAd rewarded;
void CreateRewarded()
{
    rewarded = new LevelPlayRewardedAd("adUnitId");
    rewarded.OnAdRewarded += (ad, reward) => GrantReward(); // otorga AQUI
    rewarded.OnAdClosed  += _ => rewarded.LoadAd();          // precargar la próxima
    rewarded.LoadAd();
}
// En el botón: if (rewarded.IsAdReady()) rewarded.ShowAd();
```

- Clases por formato: `LevelPlayRewardedAd`, `LevelPlayInterstitialAd`, `LevelPlayBannerAd`; métodos `LoadAd()`/`ShowAd()`/`IsAdReady()`/`DestroyAd()`; eventos `OnAdLoaded`, `OnAdLoadFailed`, `OnAdDisplayed`, `OnAdRewarded`, `OnAdClosed`.
- **Mediación en una frase**: LevelPlay subasta cada impresión entre varias redes (Unity Ads, AdMob, Meta…) y sirve la que más paga — más eCPM que una red sola a cambio de configurar adapters. Los adapters se gestionan con el LevelPlay Network Manager integrado; `LevelPlay.LaunchTestSuite()` verifica la integración en device.
- **UX**: rewarded opt-in integrada al loop (revivir, doblar premio) puede SUMAR retención; interstitial paga su eCPM en churn — nunca en primera sesión ni sobre pantallas de recompensa; banner casi nunca. Números y evidencia: [ver: gamedev/psicologia-retencion-negocio].
- El botón de rewarded necesita estado "no hay ad disponible" (gris + reintento), no un botón muerto: `IsAdReady()` es false sin fill o sin red.
- iOS: ads con tracking implican el prompt de App Tracking Transparency; los SDKs de ads traen su privacy manifest — auditar antes de subir [ver: unity/build-plataformas].

## 6. Notificaciones locales, analytics y crash reporting

### Notificaciones push locales (paquete `com.unity.mobile.notifications` 2.4)
Verificado: requiere Unity 2021.3+, compilar con Android API 33+ / iOS SDK 15.2+. Todo es **local** (programado en el device); push remoto real necesita backend aparte (Firebase Cloud Messaging u otro).

| Qué | Android (`Unity.Notifications.Android`) | iOS (`Unity.Notifications.iOS`) |
|---|---|---|
| Permiso | `PermissionRequest` (Android 13+ exige POST_NOTIFICATIONS) | `AuthorizationRequest` en corrutina; flags `AuthorizationOption.Alert \| Badge` |
| Canal (obligatorio Android 8+) | `AndroidNotificationChannel` + `AndroidNotificationCenter.RegisterNotificationChannel()` | — |
| Programar | `AndroidNotification { FireTime = ... }` + `AndroidNotificationCenter.SendNotification()` | `iOSNotification` + trigger (`iOSNotificationTimeIntervalTrigger` / `iOSNotificationCalendarTrigger`) + `iOSNotificationCenter.ScheduleNotification()` |
| Cancelar | `AndroidNotificationCenter.CancelNotification()` | API equivalente del center |
| Timing exacto | `AndroidNotificationCenter.UsingExactScheduling` / `RequestExactScheduling()` (Android difiere alarmas por batería) | los triggers son exactos |

Patrón operativo: al irse la app a background (`OnApplicationPause(true)`), cancela TODO lo programado y reprograma según el estado actual (energía llena en X, evento termina en Y); al volver, cancela de nuevo. Así nunca notificas algo ya resuelto. Pide el permiso **en contexto** (cuando el jugador activa algo que lo necesita), no en el primer arranque; la primera notificación irrelevante cuesta el permiso para siempre [ver: gamedev/psicologia-retencion-negocio].

### Analytics
| Opción | Qué es | Notas |
|---|---|---|
| **Unity Analytics** (UGS, `com.unity.services.analytics`) | Eventos estándar + custom, funnels, audiencias, A/B | Se inicializa con `UnityServices.InitializeAsync()`; exige flujo de **consentimiento** (doc oficial); free tier con límites, cobra por uso a escala |
| **Firebase Analytics** | Estándar móvil de Google, gratis | Solo Android/iOS; SDK aparte |
| **GameAnalytics** | Gratis, orientado a juegos | La fuente de los benchmarks de retención de [ver: gamedev/psicologia-retencion-negocio] |

Eventos mínimos para poder diagnosticar D1/D7/D30 después (instrumentar ANTES del soft launch):

| Evento | Parámetros | Diagnostica |
|---|---|---|
| Pasos del FTUE/tutorial | step_id | Funnel de onboarding → D1 |
| `level_start` / `level_complete` / `level_fail` | level_id, duración, intentos | Muros de dificultad, pacing |
| `currency_gained` / `currency_spent` | currency, amount, source/reason | Inflación, sinks muertos (sección 3) |
| Compra IAP / rewarded vista | product_id / placement | Monetización real |
| session con versión del juego y device | — | Segmentar todo lo anterior |

### Crash reporting
- **Unity Cloud Diagnostics** (UGS): crashes + excepciones manejadas, integrado al dashboard de Unity (detalle fino de límites: la doc estaba inaccesible al escribir esto — confirmar en docs.unity.com).
- **Firebase Crashlytics**: el estándar de facto móvil, gratis, Android/iOS (verificado en su doc oficial).
- Con IL2CPP, sube los símbolos en cada release o los stack traces nativos son ilegibles; `Debug.LogException` aparece como excepción no-fatal en ambos.
- Métrica objetivo: **crash-free rate ≥ 99.5%** antes de escalar adquisición; un juego que crashea no tiene retención que medir.

## 7. Tiempo: reloj local vs servidor, offline rewards, anti-cheat básico

- **Siempre `DateTime.UtcNow`**, nunca `DateTime.Now`: el timezone del device cambia con viajar. Guarda timestamps como UTC (ticks o ISO 8601) en el save.
- `Time.realtimeSinceStartup` solo mide DENTRO de la sesión; para "cuánto pasó desde la última vez" se compara `UtcNow` contra el `lastSeenUtc` guardado.
- **El reloj local es del jugador**: adelantar la hora del sistema completa timers, streaks y cofres. Decide cuánto te importa: en un idle premium sin leaderboard, poco; con economía IAP o competitivo, mucho.

Escalera anti-cheat de reloj (de gratis a robusto):

1. **Clamp de retroceso**: si `UtcNow < lastSeenUtc`, el reloj viajó al pasado → usa `lastSeenUtc` como "ahora" y no acredites tiempo negativo.
2. **Cap de acumulación offline**: recompensas offline topadas a 8-24 h. Además de sano para el balance (fuerza sesiones), convierte el adelanto de reloj en ganancia mínima. La matemática de tasas/prestige del idle: [ver: gamedev/mecanicas-sistemas].
3. **Hora de servidor**: para daily rewards/eventos/tienda rotativa que importen, obtén la hora de una fuente que no controle el jugador — tu backend, o el header `Date` de cualquier respuesta HTTPS propia (`UnityWebRequest.GetResponseHeader("Date")`). Cachea el offset servidor-local una vez por sesión y opera con él. Sin red → deja jugar el core, pospón solo lo dependiente de hora confiable (no bloquees el juego offline).

```csharp
public int SecondsSinceLastSeen(SaveFile s)
{
    var now = DateTime.UtcNow;
    var last = new DateTime(s.lastSeenUtcTicks, DateTimeKind.Utc);
    if (now < last) { now = last; }            // reloj retrocedió: clamp
    double elapsed = (now - last).TotalSeconds;
    return (int)Math.Min(elapsed, s.offlineCapHours * 3600.0); // cap
}
// Al guardar SIEMPRE: s.lastSeenUtcTicks = DateTime.UtcNow.Ticks;
```

4. El paso final es server-authoritative (el servidor calcula recompensas y timers) — solo si ya hay backend por otras razones [ver: multijugador-netcode].

## Reglas prácticas

- [ ] Estado del jugador = clases planas `[Serializable]` bajo un único `SaveFile` raíz con `int version`; MonoBehaviours nunca son el estado.
- [ ] Definiciones en ScriptableObjects, estado referencia por id estable; nada de referencias a assets dentro del JSON.
- [ ] Save en `Application.persistentDataPath`, escritura atómica (temp + `File.Replace` con `.bak`), carga con fallback al backup si el parse falla.
- [ ] Guardar en cada transacción importante y en `OnApplicationPause(true)`; no confiar en `OnApplicationQuit` en móvil.
- [ ] Migraciones como cascada v(n)→v(n+1); fixtures de saves viejos cargados en tests de regresión.
- [ ] `JsonUtility` primero (sin `Dictionary`, solo campos); Newtonsoft solo con `link.xml` que lo preserve.
- [ ] PlayerPrefs solo settings y flags; jamás progresión ni nada sensible (lo dice la doc oficial).
- [ ] Cifrado del save = HMAC/AES anti-edición casual como mucho; la seguridad real solo existe server-side.
- [ ] Toda mutación de moneda/inventario pasa por un servicio único que valida, emite evento de analytics con `source`/`reason` y agenda save.
- [ ] IAP: precios siempre los localizados que devuelve la tienda (`OnProductsFetched`); nunca hardcodear "$1.99".
- [ ] IAP: botón de restore visible (Apple lo exige), grant idempotente, save inmediato tras grant, validación server-side si hay valor competitivo.
- [ ] Ads: LevelPlay (el paquete legacy Advertisement está en salida desde abr-2026); rewarded opt-in como formato default; interstitial jamás en primera sesión ni sobre recompensas.
- [ ] Rewarded sin fill = botón en estado "no disponible", nunca botón muerto.
- [ ] Notificaciones: reprogramar el set completo en cada background/foreground; pedir el permiso en contexto, no en el arranque.
- [ ] Analytics instrumentado ANTES del soft launch: funnel FTUE, level start/complete/fail, currency gained/spent, IAP, ads.
- [ ] Crash reporting desde la primera beta; símbolos IL2CPP subidos en cada release; objetivo crash-free ≥ 99.5%.
- [ ] Tiempo: solo `UtcNow`, clamp de retroceso, cap de offline rewards, hora de servidor para lo que toque dinero o eventos.
- [ ] Probar save/load, IAP y notificaciones en DEVICE real con build IL2CPP temprano — stripping y lifecycle móvil no se ven en el Editor [ver: unity/build-plataformas].

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Progresión guardada en campos de MonoBehaviours repartidos por la escena | Un `SaveFile` raíz plano; los componentes leen/escriben vía servicios |
| `File.WriteAllText` directo al save → corrupto tras un kill a mitad de escritura | Temp + `File.Replace` + `.bak`; fallback de carga al backup |
| Save funciona en Editor, JSON llega vacío/null en device IL2CPP | Stripping del serializador: `link.xml` con `preserve="all"` para Newtonsoft o `[Preserve]` en los tipos [ver: unity/build-plataformas] |
| `Dictionary<string,int>` en el save "porque es cómodo" | `JsonUtility` lo ignora en silencio: listas de pares serializables, o Newtonsoft consciente |
| Añadir campos al save sin versión → releases futuros no pueden migrar | `int version` desde el primer build publicado, aunque sea `= 1` |
| Monedas en PlayerPrefs editables con cualquier editor de plist/registro | Progresión al save cifrable; PlayerPrefs solo settings |
| Tutorial de IAP con `IStoreListener`/`ConfigurationBuilder` sobre el paquete 5.x | Es API 4.x: en 5.x el flujo es `StoreController` + eventos (`OnPurchaseConfirmed`…) |
| Consumable comprado pero el juego crasheó antes del grant → jugador pagó y no recibió | Grant idempotente ejecutado al re-entregarse la compra pendiente en la siguiente init |
| App rechazada en App Store review por no poder restaurar compras | Botón "Restaurar compras" que llama `RestoreTransactions`, visible en settings |
| Interstitials desde el minuto 1 "para monetizar ya" | El churn medido lo come todo: rewarded opt-in primero [ver: gamedev/psicologia-retencion-negocio] |
| Notificación llega anunciando algo que el jugador ya resolvió | Cancelar + reprogramar todo el set en cada transición background/foreground |
| Daily reward reclamable infinitas veces adelantando el reloj del device | Clamp + hora de servidor para el reset diario; cap en offline rewards |
| `DateTime.Now` en timestamps → streaks rotos al cruzar timezone | UTC en todo lo persistido; conversión a local solo en UI |
| Analytics añadido después del launch "cuando haya usuarios" | Sin funnel del FTUE ni eventos de economía no hay diagnóstico posible; va antes del soft launch |

## Fuentes

- **Application.persistentDataPath — Unity Scripting API 6.2** (docs.unity3d.com) — rutas exactas por plataforma, rol de Company/Product Name, persistencia en updates, WebGL=IndexedDB.
- **PlayerPrefs — Unity Scripting API 6.2** (docs.unity3d.com) — backend por plataforma, tipos soportados, límite ~1 MB en Web, advertencia oficial de no guardar datos sensibles.
- **JSON Serialization — Unity Manual** (docs.unity3d.com) — API exacta de JsonUtility, qué no soporta (Dictionary, propiedades, top-level, polimorfismo), rendimiento y GC.
- **File.Replace — Microsoft Learn (.NET)** — firma, comportamiento (reemplazo con backup), excepciones (FileNotFoundException si el destino no existe) — la base del save atómico.
- **In App Purchasing 5.4 — changelog oficial** (docs.unity3d.com/Packages/com.unity.purchasing@5.4) — 5.4.1 (jul 2026), StoreController, servicios IProductService/IPurchaseService/IStoreService, eventos que reemplazan IStoreListener, StoreKit 2 sin CrossPlatformValidator, OnRestoreTransactions.
- **Unity IAP overview — manual UGS** (docs.unity.com) — v5, UnityServices.InitializeAsync, ProductType, validación local ofuscada vs server-side, RestoreTransactions en iOS.
- **LevelPlay Unity package integration — docs.unity.com/grow** — `com.unity.services.levelplay` 9.5.0, LevelPlay.Init + OnInitSuccess/OnInitFailed, adapters por defecto desde 8.8.1, LaunchTestSuite, requisitos de plataforma.
- **Migrate from Unity Ads to LevelPlay — docs.unity.com/grow** — clases LevelPlayRewardedAd/Interstitial/Banner con métodos y eventos exactos; aviso oficial de "reduced ad performance" para el paquete Advertisement legacy desde el 1-abr-2026.
- **Mobile Notifications 2.4 — manual del paquete** (docs.unity3d.com, páginas índice/Android/iOS) — 2.4.3, requisitos (Unity 2021.3+, API 33+, iOS SDK 15.2+), AndroidNotificationCenter/canales/PermissionRequest/exact scheduling, AuthorizationRequest/iOSNotification/triggers.
- **Unity Analytics overview — manual UGS** (docs.unity.com) — capacidades, requisito de consentimiento, free tier con cobro por uso.
- **Firebase Crashlytics (Unity) — firebase.google.com** — soporte oficial Android/iOS del SDK Unity.
- **gamedev/psicologia-retencion-negocio.md** (base propia) — todo el POR QUÉ de ads/monetización/retención que este archivo cablea: formatos y su churn medido, dark patterns, session hooks, métricas.
- **gamedev/mecanicas-sistemas.md** (base propia) — economías internas (sources/sinks, monedas por loop), matemática idle/prestige, loot tables: el diseño que la sección 3 y 7 implementan.
- **unity/build-plataformas.md** (base propia) — stripping/link.xml, privacy manifests, Filter Touches When Obscured, permisos: los requisitos de build que estos servicios disparan.
