# Input táctil y servicios móviles en Unity (producción)

> **Cuando cargar este archivo:** al llevar un juego Unity 6 a iOS/Android real — implementar gestos táctiles y controles en pantalla, cablear IAP/ads/push/analytics/cloud-save contra las tiendas, o resolver consentimiento (ATT/UMP), deep links, referrals e in-app review. Es la **especialización móvil de producción**: NO repite las bases generales, las profundiza. El input genérico (Enhanced Touch, OnScreenStick, gestos DIY) está en [ver: unity/input-system]; el CÓMO de save/IAP/ads/notificaciones en Unity en [ver: pipeline/sistemas-meta]; los requisitos de tienda (ATT/UMP/Data Safety/review) en [ver: pipeline/publicacion-tiendas]; el UX del pulgar/safe areas en [ver: ux-ui/mobile-ux]; los benchmarks de negocio (retención, ARPDAU, CPI) en [ver: mercado-movil] y [ver: gamedev/psicologia-retencion-negocio]. Aquí va SOLO el ángulo móvil-real que esas bases no cubren.

## Versión y contexto (jul 2026)

- Verificado contra: Input System 1.19, Unity IAP `com.unity.purchasing` 5.4.1, LevelPlay `com.unity.services.levelplay` 9.5.0, Mobile Notifications 2.4, docs de Apple/Google y Unity 6 manual — todo referenciado en las bases hermanas y re-verificado aquí lo específico de móvil.
- Los paquetes de servicios (IAP/ads/notifications/analytics/cloud-save) viven en **Unity Gaming Services (UGS)** salvo los de terceros (Firebase, AppsFlyer, Adjust). Requieren proyecto vinculado a UGS y `await UnityServices.InitializeAsync()` una sola vez al arranque.
- ⚠️ Todo lo de este archivo se **prueba en device físico con build IL2CPP**, temprano. El Editor no reproduce: latencia táctil real, lifecycle (background/kill), stripping, permisos del OS, recibos de tienda, ni el prompt ATT. Un "funciona en Play Mode" no es evidencia de nada aquí.

---

## 1. Input táctil en producción (profundiza [ver: unity/input-system])

La API (Enhanced Touch, `Touch.activeTouches`, gestos DIY, `OnScreenStick`) ya está en input-system. Aquí va lo que **solo aparece en el device real**:

### El touch es el input primario — y trae problemas que el mouse no tiene

| Problema móvil-real | Detalle | Antídoto |
|---|---|---|
| **Umbrales de gesto en px NO son portables** | Un swipe de "50 px" es un gesto largo en un teléfono de 320 dpi y un microgesto en uno de 560 dpi | Escalar SIEMPRE por densidad: umbral en **cm físicos** → `px = cm * Screen.dpi / 2.54`. `Screen.dpi` puede venir **0 o mentir** en algunos Android → fallback a un DPI asumido (160) y clamp |
| **Latencia táctil (touch-to-photon)** | El dedo tapa un objeto pequeño; el usuario apunta al centro visible, no al píxel | Hit targets ≥ 44 pt / 48 dp reales (no el glifo) [ver: ux-ui/mobile-ux]; hit-slop invisible; nunca exigir precisión de píxel |
| **UI raycast vs gameplay** en móvil | Un tap sobre un botón HUD **también** llega al mundo si no se filtra | `EventSystem.current.IsPointerOverGameObject(touchId)` — pasar el **`touchId`** (no la sobrecarga sin argumento, que es de mouse). O separar action maps Player/UI |
| **Multi-touch fantasma** | Segundo dedo apoyado (agarre) dispara un touch espurio; joystick + botón a la vez confunde el input de un solo Pointer | Multi-touch con action type **Pass-Through** sobre `<Touchscreen>/touch*/press`; joystick con *Isolated Input Actions* |
| **Palm/borde** | Pantallas sin bisel registran toques del borde de la palma | Ignorar touches nacidos en los insets del safe area; zona muerta en los bordes del joystick flotante |

### Gestos: umbrales de producción (DIY sobre Enhanced Touch)

Valores de partida a calibrar en device — **orientativos**, el sistema no trae reconocedores:

| Gesto | Detección | Umbral inicial (calibrar) |
|---|---|---|
| **Tap** | `Ended` con desplazamiento < umbral y duración corta | < ~0.4 cm de deriva, < 0.2 s (el tap time default del Input System) |
| **Long-press** | `Stationary`/sin soltar > T | 0.4–0.5 s (alineado con `Hold`), + deriva máxima pequeña o se cancela |
| **Swipe/flick** | Al `Ended`, desplazamiento > umbral; dirección = eje dominante | > ~1 cm; distinguir flick (rápido) de drag por velocidad (`delta`/`deltaTime`) |
| **Pinch** | 2 dedos, delta de distancia entre `screenPosition` | Ver receta en [ver: unity/input-system]; escalar el zoom por DPI |
| **Pan/drag** | 1 dedo `Moved`, acumular `delta` | Empezar tras superar un umbral (evita jitter en taps) |

- **Consumir** el gesto: un `Ended` puede evaluar tap Y swipe — decide uno y descarta el otro por umbral, no dispares los dos.
- La API de Enhanced Touch **no genera GC garbage** (structs) — segura cada frame; el device de bajo perfil sí sufre si además haces `Physics.Raycast` por touch cada frame: cachea.

---

## 2. Controles en pantalla y safe area en Unity (profundiza [ver: ux-ui/mobile-ux])

El mapa del pulgar, thumb-zones y los números de safe area (notch, home indicator) están en mobile-ux. El ángulo **Unity** que falta:

### Safe area con `Screen.safeArea` (no `env()` de CSS — eso es web)

```csharp
// Component en un RectTransform "SafeAreaPanel" que envuelve el HUD
void ApplySafeArea()
{
    Rect sa = Screen.safeArea;               // en px, ya descuenta notch/isla/home indicator
    Vector2 min = sa.position, max = sa.position + sa.size;
    min.x /= Screen.width;  min.y /= Screen.height;
    max.x /= Screen.width;  max.y /= Screen.height;
    rect.anchorMin = min;  rect.anchorMax = max;  // el panel se encoge al área usable
}
```

- Reaplicar en **cada cambio de orientación/resolución** (suscribir o comparar `Screen.safeArea` por frame barato). El notch aparece a izquierda o derecha en landscape.
- **Fondo** del juego hasta el borde (inmersivo); **botones y HUD dentro del safe area**. Igual que en producto, pero aquí se hace con anchors, no con `env(safe-area-inset-*)`.
- Android edge-to-edge (obligatorio al apuntar a API alto): `Screen.safeArea` cubre las barras de gesto; verificar en device con barra de gestos y con botones.

### Joystick virtual: decisiones que solo importan en móvil

| Decisión | Opciones | Recomendación práctica |
|---|---|---|
| **Fijo vs flotante** | Fijo (posición constante) / Flotante (nace donde tocas) | Flotante para twin-stick/movimiento libre (el pulgar no busca un punto fijo); fijo para juegos con layout aprendido |
| **Dead zone** | Radio central inerte | ~10–15% del rango o el drag detecta movimiento involuntario |
| **Zona activa** | Media pantalla izquierda para mover, derecha para acción | Mapear por lado, no por widget diminuto — el pulgar es gordo |
| **Reposicionable por el jugador** | HUD arrastrable + guardar layout | Accesibilidad real en móvil; el "claw grip" y manos distintas lo agradecen. Guardar en el save [ver: pipeline/sistemas-meta] |

- `OnScreenStick`/`OnScreenButton` apuntando a `<Gamepad>/leftStick` etc. reusan el action map de gamepad tal cual [ver: unity/input-system] — el mismo código de gameplay corre en móvil y con mando.
- El botón de acción principal cae en la **zona verde del pulgar** (tercio inferior, lado dominante) [ver: ux-ui/mobile-ux]; nada crítico bajo el home indicator ni en esquinas superiores.
- Fullscreen: usar `dvh` es cosa de web; en Unity nativo el viewport ya es la pantalla — pero probar con teclado del OS abierto (chat, nombre) que no tape el input.

---

## 3. IAP en producción móvil real (profundiza [ver: pipeline/sistemas-meta] §4)

El flujo de código v5 (`StoreController`, `OnPurchaseConfirmed`, restore, grant idempotente, validación StoreKit 2) ya está en sistemas-meta. Aquí, **lo que rompe entre el Editor y una compra real en la tienda**:

### Gates de configuración (sin esto, no hay ni una compra de prueba)

| Tienda | Gate obligatorio antes de testear | Síntoma si falta |
|---|---|---|
| **App Store** | **Paid Apps Agreement** firmado + banca/fiscal en App Store Connect; productos creados con el **mismo product id** que el juego; usuario **Sandbox** | Productos no cargan (`OnProductsFetched` vacío); compra falla silenciosa |
| **Google Play** | App subida a un **track** (interno basta) y firmada con la **misma key**; productos activos; cuenta de **License Testing** (Play Console) | "Item not found"; precios no cargan |
| Ambos | Product ids **idénticos** en el juego y en cada consola; `applicationId`/bundle id correctos | Catálogo vacío en device |

- **Precios SIEMPRE los localizados** que devuelve la tienda (`product.metadata.localizedPriceString`), nunca "$1.99" hardcodeado — cada país/moneda difiere y las tiendas lo exigen [ver: pipeline/sistemas-meta].
- Testear en **device real**: el sandbox de Apple y el License Testing de Google no funcionan en el Editor. El IAP simulado del Editor solo valida tu lógica de grant, no el pago.

### Lo que solo pasa en la tienda real

| Caso | Qué es | Manejo |
|---|---|---|
| **Compra pendiente/diferida** | "Ask to Buy" (control parental iOS), pago pendiente de banco | La compra llega **después**, en otra sesión: el grant debe re-ejecutarse al re-init y ser **idempotente** (¿ya lo tiene? → no duplicar) |
| **Restore (Apple lo exige)** | Non-consumables/subs deben restaurarse o **rechazo en review** | Botón "Restaurar compras" visible en settings → `RestoreTransactions` [ver: pipeline/publicacion-tiendas §3, guideline 3.1.1] |
| **Grant perdido** | El proceso murió entre pago y entrega | Save inmediato tras grant; la compra pendiente se re-entrega en el próximo init — perder una compra pagada es el peor bug |
| **Reembolso/refund** | Apple/Google pueden revocar (server notifications) | Solo detectable server-side; para eso y para PvP con valor competitivo → **validación server-side** |

### Validación: cuándo local basta y cuándo no

- **Offline single-player**: la validación local (StoreKit 2 nativo en Apple; clave licenciada ofuscada en Google) basta — es SU juego.
- **Valor competitivo / economía compartida / leaderboards**: **server-side obligatorio**. El servidor recibe el recibo (App Store: `transactionId`/JWS de StoreKit 2; Google: purchase token) y lo verifica contra la **App Store Server API** / **Google Play Developer API** antes de acreditar. Un cliente comprometido puede fabricar "compras" locales.
- Loot boxes de pago → **odds publicadas** (requisito de ambas tiendas) [ver: gamedev/psicologia-retencion-negocio]. Android + dinero → `Filter Touches When Obscured` anti-tapjacking [ver: unity-movil-rendimiento].

---

## 4. Ads + consentimiento: el ORDEN de cableado es todo (profundiza [ver: pipeline/sistemas-meta] §5)

LevelPlay 9.5.0 y las clases `LevelPlayRewardedAd`/`Interstitial`/`Banner` están en sistemas-meta. El mecanismo ATT/UMP está en publicacion-tiendas. Lo que **ninguna de las dos dice: el orden importa y romperlo te cuesta ingreso o el rechazo**.

### Secuencia de arranque obligatoria (iOS + Android)

```
1. UnityServices.InitializeAsync()
2. [iOS] ATT prompt (ATTrackingManager) → esperar la respuesta del usuario
3. [Android/EEA/UK] UMP: consentInfo.Update() → LoadAndShowConsentFormIfRequired()
4. RECIÉN AHORA: LevelPlay.Init(appKey)  ← nunca antes del consentimiento
5. Crear/precargar rewarded e interstitial
```

- **Init del SDK de ads ANTES del consentimiento = fuga de datos sin permiso** → rechazo de Apple (5.1.2) y violación GDPR. El prompt ATT va **antes** de tocar el IDFA o inicializar cualquier SDK que trackee.
- **ATT (iOS 14.5+)**: denegado → IDFA en ceros; los ads **siguen saliendo** pero sin personalizar → **eCPM menor**. Prohibido bloquear el juego o incentivar el permiso; fingerprinting como workaround = rechazo [ver: pipeline/publicacion-tiendas §6].
  - Impacto de negocio: la tasa de opt-in de ATT y su golpe al eCPM son **orientativos** (comúnmente citados ~20–30% opt-in; caída de ingreso variable) — verificar con benchmarks de AppsFlyer/Adjust del trimestre, no dar por dato duro. [ver: mercado-movil]
- **UMP (EEA/UK, GDPR)**: `Update()` en **cada arranque** + `LoadAndShowConsentFormIfRequired()`; el form solo aparece donde la región lo exige. Cablear el consentimiento a **todos** los SDKs (LevelPlay y cualquier adapter), no solo a uno.
- **SKAdNetwork / AdAttributionKit** (iOS): la atribución privada de Apple que reemplaza al IDFA para medir instalaciones desde ads sin identificar al usuario. Los SDKs de ads y de atribución la gestionan; tú declaras conversion values. **AdAttributionKit** es la evolución (iOS 17.4+) — verificar soporte de tu SDK. No es opcional si haces UA pagada en iOS.

### Formato y su impacto (el porqué medido está en negocio)

| Formato | Uso sano | Regla dura |
|---|---|---|
| **Rewarded** (opt-in) | Revivir, doblar premio, girar de nuevo — integrado al loop | Grant en `OnAdRewarded`. Sin fill → botón "no disponible" (`IsAdReady()` false), **nunca botón muerto** [ver: unity/input-system, botones muertos] |
| **Interstitial** | Entre niveles, con moderación | JAMÁS en la primera sesión ni sobre pantallas de recompensa — el churn se lo come [ver: gamedev/psicologia-retencion-negocio] |
| **Banner** | Casi nunca en juegos | Contamina UI por centavos |

- ARPDAU de ads casual ~$0.05–0.15 (fuente en [ver: gamedev/psicologia-retencion-negocio] / [ver: mercado-movil]); sin volumen enorme el modelo ads-only no cierra. El estándar 2026 es **híbrido** (rewarded + IAP de conveniencia) [ver: monetizacion-movil].
- `LevelPlay.LaunchTestSuite()` verifica adapters en device antes de subir.

---

## 5. Notificaciones: local vs remota — dos arquitecturas (profundiza [ver: pipeline/sistemas-meta] §6)

Mobile Notifications 2.4 (local, cross-ref sistemas-meta) programa en el device. **Push remota es otro sistema entero** que sistemas-meta solo menciona:

| | **Local** (Unity Mobile Notifications) | **Remota** (FCM + APNs) |
|---|---|---|
| Qué dispara | El juego, programado en el device | Tu backend / consola FCM |
| Necesita servidor | No | **Sí**: Firebase Cloud Messaging; iOS enruta vía **APNs** (certificado/key de Apple) |
| Casos | Energía llena, evento local termina, streak en riesgo, "vuelve mañana" | Eventos live-ops, mensajes segmentados, "tu clan te necesita", noticias de temporada |
| Timing Android | `RequestExactScheduling()` — Android difiere alarmas por batería | Entrega best-effort del OS |
| SDK | `com.unity.mobile.notifications` | Firebase SDK for Unity (no es UGS) |

- **Permiso (Android 13+ / iOS)**: pedirlo **en contexto** (cuando el jugador activa algo que lo usa), no en el primer arranque. La primera notificación irrelevante quema el permiso para siempre [ver: gamedev/psicologia-retencion-negocio]. iOS soporta **autorización provisional** (llegan silenciosas a la bandeja sin prompt) como estrategia de opt-in suave.
- **Reprogramar el set completo** en cada `OnApplicationPause(true)` / foreground: cancelar todo y reagendar según el estado actual, o notificas algo ya resuelto [ver: pipeline/sistemas-meta].
- Remota: al recibir con la app abierta, **decidir si mostrarla** (no molestar en pleno gameplay); deep-link del payload → sección 8. El token FCM cambia y se refresca — subirlo al backend en cada cambio.

---

## 6. Analytics y crash en producción móvil (profundiza [ver: pipeline/sistemas-meta] §6)

El QUÉ (eventos mínimos, opciones, crash-free ≥99.5%) está en sistemas-meta. El ángulo **móvil-producción**:

- **Consentimiento gate**: en EEA/UK, analytics de terceros también requiere consentimiento (el mismo UMP/CMP de la sección 4). No enviar eventos hasta tener consentimiento; UGS Analytics exige flujo de consentimiento explícito [ver: pipeline/publicacion-tiendas §6].
- **Símbolos IL2CPP en CADA release**: sin subir los símbolos (dSYM en iOS, `symbols.zip`/mapping en Android), los stack traces nativos de crashes son ilegibles. Firebase Crashlytics es el estándar de facto móvil; Unity Cloud Diagnostics es la opción UGS integrada [ver: pipeline/sistemas-meta].
- **Eventos de atribución/instalación**: `first_open`, fuente de instalación (Install Referrer §8), y los eventos de embudo del FTUE — instrumentados **antes** del soft launch o no hay D1/D7 que diagnosticar. Los benchmarks contra los que comparar (D1 mediana ~22%, D7 ~3.4–3.9%, GameAnalytics 2025) están en [ver: gamedev/psicologia-retencion-negocio] y [ver: mercado-movil] — no se repiten aquí.
- **Privacy manifests**: los SDKs "commonly used" (ads, analytics, atribución) traen su privacy manifest; el build de iOS los agrega y tú respondes por lo que declaran en los App Privacy labels [ver: pipeline/publicacion-tiendas §6].

---

## 7. Remote config en producción móvil (profundiza [ver: pipeline/publicacion-tiendas] §10)

El concepto (tunear economía/dificultad/flags sin re-release ni review) está en publicacion-tiendas. El ángulo de implementación móvil:

- **Defaults locales SIEMPRE**: el juego arranca y es jugable sin red (el móvil vive con conexión intermitente [ver: ux-ui/mobile-ux]). Los valores remotos entran por la misma capa de datos que los ScriptableObjects [ver: pipeline/sistemas-meta].
- **Cuándo hacer el fetch**: al arranque, no bloqueante — cachear el último config recibido y usarlo mientras llega el nuevo; aplicar el nuevo en el siguiente punto seguro (no a mitad de partida).
- **Staged rollout / A/B**: Unity Remote Config (Game Overrides: segmentos, %, environments dev/prod) o Firebase Remote Config. Cada cambio remoto es un release de facto — probar en environment dev antes de tocar prod.
- Límite: cambia **números y flags**, no código ni assets. Contenido nuevo = build o Addressables + descarga [ver: unity-movil-rendimiento]. Compensa en F2P/idle con economía viva; en premium single-player, casi nunca [ver: retencion-liveops].

---

## 8. Cloud save y cuentas: sincronizar progreso entre devices (NUEVO)

El save local atómico está en [ver: pipeline/sistemas-meta] §2. Sincronizar entre el teléfono y la tablet del mismo jugador es un sistema aparte que ninguna base cubre:

| Opción | Qué da | Notas |
|---|---|---|
| **UGS Cloud Save** | Key-value JSON por jugador en la nube; requiere **UGS Authentication** | Requiere player id (anónimo o cuenta); límites de tamaño por item/write — **verificar en docs UGS** (no leídos en esta pasada) |
| **Game Center** (iOS) / **Google Play Games Services** (Android) | Auth + saved games nativos + logros/leaderboards | Nativo, pero **por plataforma** — no sincroniza iOS↔Android entre sí |
| **iCloud / Play Games auto-backup** | Backup del sandbox por el OS | Opaco, sin control de conflictos; no confiar como único mecanismo |
| **Backend propio** | Control total, cross-platform | Solo si ya hay backend por otras razones [ver: pipeline/multijugador-netcode] |

Reglas de un cloud save que no corrompe progreso:

- **Autenticación primero**: sin identidad no hay a quién sincronizar. Patrón sano: **login anónimo/guest** al arranque (juega ya, sin fricción) y ofrecer **vincular cuenta** (Apple/Google/email) después, para no perder el progreso al cambiar de device o reinstalar.
- **Resolución de conflictos explícita**: dos devices editan offline → al reconectar hay dos versiones. Decidir la política: "mayor progreso gana" (monedas/nivel más alto), timestamp más reciente, o merge por campos. **Nunca** sobrescribir a ciegas — es la queja nº1 de reviews ("perdí mi cuenta").
- **Local como source of truth en sesión, nube como respaldo**: jugar sobre el estado local, sincronizar a la nube en puntos seguros (background, fin de nivel); al arrancar en un device nuevo, bajar de la nube.
- **Merge guest → cuenta**: cuando un guest con progreso vincula una cuenta que YA tiene progreso, decidir la política de merge de antemano (no descartar el que más invirtió).
- El save cifrado/HMAC anti-edición casual [ver: pipeline/sistemas-meta] no protege la nube: la seguridad real de progreso con valor es server-authoritative.

---

## 9. Deep links, referrals e integración con las tiendas (NUEVO)

Cómo el jugador entra al juego desde fuera y cómo se mide de dónde vino. Área que ninguna base cubre:

### Deep linking en Unity 6 (verificado en el manual)

- `Application.absoluteURL` guarda la URL del deep link en **cold start** (app cerrada, se abre por el link) — leerla al arrancar.
- `Application.deepLinkActivated` es el **evento** que dispara en **warm start** (app ya corriendo) con la URL como parámetro; `absoluteURL` se actualiza a la vez.
- Patrón: un singleton que en `Awake` chequea `absoluteURL` (cold) **y** se suscribe a `deepLinkActivated` (warm), parsea (`unitydl://open?scene=shop&id=42`) y navega. Soportado en iOS, Android, UWP, macOS, Web.
- **Setup por plataforma** (fuera de Unity): iOS **URL scheme** + **Universal Links** (`apple-app-site-association` en el dominio); Android **intent filter** + **App Links** (`assetlinks.json` con `autoVerify`). Universal/App Links abren el juego desde una URL `https://` real (mejor que un scheme custom, que falla si la app no está instalada).

### Deferred deep linking y atribución (post-install)

- **Deferred deep link**: el usuario toca un link → no tiene la app → instala desde la tienda → al primer arranque debe aterrizar en el contenido del link (oferta, sala, referral). El deep link normal se pierde en el salto por la tienda; el **deferred** lo recupera.
- **Android — Google Play Install Referrer API** (verificado): devuelve `ReferrerDetails` con `installReferrer` (los parámetros de campaña), `referrerClickTimestampSeconds` e `installBeginTimestampSeconds`, y `googlePlayInstantParam`. Disponible **90 días**, no cambia salvo reinstalación. **Llamarla una sola vez** en el primer arranque post-install. Es la base de la atribución y del deferred deep link en Android.
- **iOS**: sin equivalente directo del referrer; la atribución privada va por **SKAdNetwork / AdAttributionKit** (sección 4). El deferred deep link en iOS lo resuelven los SDKs de atribución con sus métodos (fingerprint probabilístico está prohibido por ATT).
- ⚠️ **Firebase Dynamic Links MURIÓ**: se apagó el **25-ago-2025** (verificado en el FAQ oficial) — todos los links devuelven 404. No usarlo en proyecto nuevo. Alternativas: SDKs de terceros con paridad de features (**AppsFlyer, Adjust, Branch, Airbridge**) o **App Links (Android) + Universal Links (iOS)** nativos hosteados donde sea (opcionalmente Firebase Hosting) para el caso post-install simple.
- **SDKs de atribución** (AppsFlyer/Adjust/Branch): unifican Install Referrer + SKAdNetwork + deep/deferred links + medición de campañas de UA. Necesarios si haces adquisición pagada; para un dev orgánico sin UA, App/Universal Links nativos + Install Referrer bastan.

### Referrals (invitar amigos)

- Flujo: el jugador comparte un link con su id → el invitado instala → el Install Referrer (Android) / el SDK de atribución (iOS) recupera el id del invitador en el primer arranque → acreditar la recompensa a ambos, **server-side** (idempotente, anti-abuso: un device no puede reclamarse a sí mismo, cap por cuenta).

### In-app review (pedir la reseña sin sacar al jugador)

| Plataforma | API | Límite / reglas (verificado) |
|---|---|---|
| **Android** | **In-App Review API** (Play Core 1.8.0+, soporte Unity) | Cuota temporal de Google: llamar `launchReviewFlow` **más de una vez en ~un mes puede no mostrar nada**. **No** hacer un botón "Valóranos" que lo dispare (el usuario puede haber agotado cuota → experiencia rota); redirigir a la ficha en ese caso. No hay callback de si reseñó |
| **iOS** | `requestReview()` (StoreKit) | Apple **throttlea**: máximo 3 veces por año por usuario (verificado en Apple Developer Docs, jul 2026). No garantiza que aparezca |
| Ambos | — | **Prohibido incentivar** (moneda/premio por reseñar), **gatear** funcionalidad o **forzar**. Pedir **tras un momento de valor** (nivel superado, logro), nunca al arrancar |

- Unity no trae API nativa de review — usar el plugin de cada plataforma (Play Core para Android; binding de StoreKit para iOS) o un asset que envuelva ambos.

---

## Reglas prácticas

1. Todo lo de este archivo se prueba en **device físico con build IL2CPP** temprano; el Editor no reproduce touch real, lifecycle, permisos, recibos ni ATT.
2. **Umbrales de gesto en cm físicos**, escalados por `Screen.dpi` con fallback (DPI puede venir 0/mentir en Android); nunca en px absolutos.
3. Tap sobre HUD que no debe llegar al mundo: `IsPointerOverGameObject(touchId)` con el **touchId**, o separar action maps Player/UI.
4. **Safe area con `Screen.safeArea`** aplicada a un panel raíz del HUD y reaplicada al rotar; fondo al borde, botones dentro del inset; acción primaria en la zona verde del pulgar.
5. Joystick flotante para movimiento libre, dead zone ~10–15%, HUD reposicionable guardado en el save; `OnScreenStick`→`<Gamepad>/...` para reusar el action map.
6. **IAP: gates de tienda antes de testear** (Paid Apps Agreement / License Testing, product ids idénticos, build firmado en un track) y probar en device — el Editor no cobra.
7. IAP: precios **localizados de la tienda** siempre; grant **idempotente** (compras pendientes se re-entregan); botón **restore** visible (Apple lo exige); save inmediato tras grant.
8. IAP con valor competitivo/economía compartida → **validación server-side** (App Store Server API / Google Play Developer API); local solo para offline single-player.
9. **Orden de arranque de ads sagrado**: InitializeAsync → ATT (iOS) → UMP (EEA/UK) → recién ahí `LevelPlay.Init` → precargar. Init del SDK antes del consentimiento = rechazo + GDPR.
10. Rewarded opt-in integrada al loop con grant en `OnAdRewarded` y estado "no disponible" sin fill; interstitial jamás en primera sesión ni sobre recompensas; SKAdNetwork/AdAttributionKit si hay UA en iOS.
11. **Push: local ≠ remota** — local con Mobile Notifications, remota con FCM/APNs + backend; permiso **en contexto**; reprogramar el set completo en cada background/foreground.
12. Analytics: **no enviar eventos sin consentimiento** en EEA/UK; instrumentar el embudo FTUE + fuente de instalación antes del soft launch; subir símbolos IL2CPP en cada release.
13. **Remote config con defaults locales** que aguantan sin red; fetch no bloqueante, cachear el último; cada cambio remoto probado en dev antes de prod.
14. **Cloud save exige autenticación**: guest al arranque + vincular cuenta después; **política de conflicto explícita** (nunca sobrescribir a ciegas); local source-of-truth en sesión, nube respaldo.
15. **Deep links**: cold start por `Application.absoluteURL`, warm por `deepLinkActivated`; Universal Links (iOS) + App Links (Android) sobre schemes custom.
16. **Firebase Dynamic Links está apagado (25-ago-2025)** — no usarlo; deferred deep link/atribución con Install Referrer (Android, llamar 1 vez, dura 90 días) + SDK de atribución o links nativos.
17. Referrals acreditados **server-side**, idempotentes y con anti-abuso (no autoreferido, cap por cuenta).
18. **In-app review**: pedir tras un momento de valor, jamás incentivar/gatear/forzar; en Android no hacer botón que dispare `launchReviewFlow` (cuota mensual); respetar el throttle.
19. Los **números de negocio** (retención, ARPDAU, CPI, opt-in ATT) no se inventan aquí: viven sourced en [ver: mercado-movil] y [ver: gamedev/psicologia-retencion-negocio]; lo dependiente de trimestre se marca "verificar".

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Swipe/tap con umbral en px → gesto distinto en cada densidad de pantalla | Umbral en cm, escalado por `Screen.dpi` con fallback y clamp |
| `IsPointerOverGameObject()` sin argumento en móvil (es la sobrecarga de mouse) → el filtro no funciona con touch | Pasar el `touchId` del touch concreto |
| HUD tapado por el notch / botones bajo el home indicator | `Screen.safeArea` en el panel raíz, reaplicado al rotar; probar con y sin notch, portrait y landscape |
| "Los productos IAP no cargan" en device | Falta un gate: Paid Apps Agreement / License Testing, product id distinto, build sin firmar o no en un track |
| Precio "$1.99" hardcodeado | Usar `localizedPriceString` de la tienda; cada país difiere y las tiendas lo exigen |
| Compra pagada perdida (proceso murió, o "Ask to Buy" diferido) | Grant idempotente re-ejecutado al re-init + save inmediato; probar compra pendiente |
| App rechazada por no poder restaurar compras | Botón restore visible que llama `RestoreTransactions` |
| SDK de ads inicializado antes del prompt ATT/UMP | Fuga de datos sin consentimiento = rechazo Apple 5.1.2 + GDPR; respetar el orden de arranque |
| Bloquear el juego o dar premio por aceptar ATT | Prohibido; el juego funciona igual sin permiso, los ads salen sin personalizar |
| Interstitial en la primera sesión "para monetizar ya" | El churn se lo come; rewarded opt-in primero [ver: gamedev/psicologia-retencion-negocio] |
| Push remota tratada como "una notificación local más" | Remota necesita FCM + APNs + backend; el token se refresca y hay que resubirlo |
| Pedir permiso de notificaciones en el primer arranque | En contexto; la primera notificación irrelevante quema el permiso para siempre |
| Analytics enviando eventos sin consentimiento en EEA/UK | Gatear tras UMP/CMP; UGS Analytics exige flujo de consentimiento |
| Cloud save que sobrescribe a ciegas → jugador pierde progreso | Política de conflicto explícita + autenticación; local source-of-truth en sesión |
| Progreso sin cuenta → se pierde al reinstalar/cambiar device | Guest al arranque + vincular cuenta después; sincronizar a la nube |
| Usar Firebase Dynamic Links en 2026 | Apagado desde 25-ago-2025; App/Universal Links nativos o SDK de atribución |
| Deferred deep link roto en Android | Install Referrer API llamada una vez en el primer arranque (dura 90 días) |
| Botón "Valóranos" que llama la In-App Review API de Android | La cuota mensual puede no mostrar nada → experiencia rota; redirigir a la ficha, no botonear el flow |
| Incentivar reseñas con moneda del juego | Prohibido por ambas tiendas; pedir tras momento de valor, sin premio |

## Fuentes

**Verificadas en esta pasada (jul 2026):**
- **Deep Linking — Unity 6 Manual** (docs.unity3d.com/6000.0) — `Application.absoluteURL` (cold start), evento `Application.deepLinkActivated` (warm start), patrón singleton, esquema `unitydl://`, plataformas soportadas y setup por plataforma.
- **Play Install Referrer Library — developer.android.com** — `ReferrerDetails` (installReferrer, referrerClickTimestampSeconds, installBeginTimestampSeconds, googlePlayInstantParam), disponibilidad **90 días**, llamar una sola vez post-install; usos: atribución y deferred deep linking.
- **Firebase Dynamic Links FAQ — firebase.google.com** — shutdown confirmado el **25-ago-2025** (todos los links → 404); alternativas oficiales: SDKs de terceros (Adjust/Airbridge/AppsFlyer/Branch) o App Links (Android) + Universal Links (iOS).
- **Play In-App Review API — developer.android.com** (re-verificado, cita textual) — *"calling the `launchReviewFlow` method more than once during a short period of time (for example, less than a month) might not always display a dialog"*; recomienda explícitamente no usar un botón CTA que dispare el flujo y redirigir a la Play Store en su lugar. Dependencia sigue siendo **Play Core library 1.8.0+** (confirmado vigente, jul 2026), soporte Unity, sin callback de si reseñó.
- **App Tracking Transparency / App Store user privacy — developer.apple.com** (verificado completo en esta pasada) — permiso ATT obligatorio antes de acceder al IDFA; **prohibido gatear o incentivar** el consentimiento (guideline **5.1.2(i)**) y prohibido manipular/forzar el consentimiento (guideline 5.1.1(iv)).
- **Requesting App Store reviews / SKStoreReviewController — developer.apple.com** (verificado en esta pasada) — el sistema muestra el prompt **máximo 3 veces por año** por usuario; prohibido incentivar, gatear o forzar la reseña.
- **Google Play target API level (referencia, fuera de alcance de este archivo)** — verificado: desde el **31-ago-2026** las apps nuevas/actualizaciones deben apuntar a **Android 16 (API 36)** (Wear OS/Automotive: API 35; TV/XR: API 34), con extensión posible hasta 1-nov-2026. Detalle vive en [ver: pipeline/publicacion-tiendas] o [ver: unity/build-plataformas], no repetido aquí — este archivo solo referencia "API alto" en el contexto de edge-to-edge (§2).

**Referenciadas indirectamente (verificar antes de decisiones de dinero/versión):**
- **UGS Cloud Save — docs.unity.com/ugs** — key-value por jugador, requiere Authentication; límites de tamaño por item/write NO leídos en esta pasada (la página devolvió 404) — verificar en la doc actual.
- **SKAdNetwork / AdAttributionKit — Apple** — atribución privada iOS que reemplaza al IDFA; AdAttributionKit desde iOS 17.4+ (verificar soporte del SDK usado).
- **Opt-in de ATT e impacto en eCPM** — orientativo, comúnmente citado ~20–30% opt-in; **sin fuente primaria verificada en esta sesión** — confirmar con benchmarks de AppsFlyer/Adjust del trimestre. [ver: mercado-movil]

**Bases hermanas que este archivo profundiza (no repite):**
- [ver: unity/input-system] — Enhanced Touch, `Touch.activeTouches`, gestos DIY, `OnScreenStick`/`OnScreenButton`, action maps, botones muertos: el input genérico que aquí se lleva al device real.
- [ver: pipeline/sistemas-meta] — IAP 5.4.1 (`StoreController`, restore, grant idempotente, StoreKit 2), LevelPlay 9.5.0, Mobile Notifications 2.4, analytics/crash, save local atómico: el CÓMO en Unity que aquí se vuelve producción de tienda.
- [ver: pipeline/publicacion-tiendas] — ATT/UMP, Data Safety, App Privacy labels, Remote Config concepto, guidelines de review (restore/odds/tracking): los requisitos de tienda que aquí se cablean.
- [ver: ux-ui/mobile-ux] — thumb zones, touch targets (44 pt/48 dp), safe areas conceptuales, gestos como no-único-camino: el UX que aquí se implementa en Unity.
- [ver: gamedev/psicologia-retencion-negocio] y [ver: mercado-movil] — retención D1/D7/D30, ARPDAU, CPI, rewarded vs interstitial (GameAnalytics 2025 y demás, sourced): los números de negocio que aquí NO se inventan.
