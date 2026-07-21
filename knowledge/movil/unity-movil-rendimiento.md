# Rendimiento móvil en Unity (Unity 6, iOS/Android 2026)

> **Cuando cargar este archivo:** cuando el target es un juego MÓVIL real y hay que sostener frame rate en un device de gama baja, domar el thermal throttling, no fundir la batería, caber en el presupuesto de RAM/tamaño de la tienda, o profilear en el teléfono. Este archivo PROFUNDIZA el ángulo móvil sobre las bases generales [ver: unity/rendimiento-unity] y [ver: unity/build-plataformas] — no repite draw calls/GC/batching/stripping, los da por leídos y aporta la capa móvil.

## 1. La premisa que cambia todo: el device de gama baja es el target

El error mental número uno es desarrollar y "verificar" en el teléfono que uno tiene en el bolsillo (casi siempre gama alta reciente). El mercado móvil real es una **cola larga de miles de modelos Android** y de iPhones de varios años. El jugador mediano no tiene el flagship; el que decide si tu juego "va bien o va mal" es el device de 2-4 años, 3-4 GB de RAM, GPU débil y pantalla de alta densidad (que castiga el fill rate sin dar potencia extra).

Consecuencias operativas (el resto del archivo):
- El **presupuesto de rendimiento se fija contra el device de gama baja del público objetivo**, no contra el pico. Elegir 1-2 devices reales de gama baja como "minimum spec" y tenerlos físicamente [ver: mercado-movil] para la elección de mínimos según tu geografía.
- Los números del editor y del flagship **no sirven para decidir** [ver: unity/rendimiento-unity §1]. En móvil esto es más grave: el editor no tiene ni la GPU tiled, ni el termal, ni el LMK del teléfono.
- "Va a 60 en mi Pixel" ≠ "va a 60". Va a 60 los primeros 4 minutos en tu Pixel; el veredicto es el device barato tras 15 minutos caliente.

## 2. Thermal throttling: por qué el frame rate se cae solo a los minutos

El SoC móvil no tiene disipación activa. Bajo carga sostenida sube de temperatura y, para no dañarse, el sistema **baja las frecuencias de CPU/GPU** (throttling). El resultado es la firma clásica: el juego corre fluido al arrancar y a los pocos minutos empieza el stutter — sin que hayas cambiado nada en escena.

- **Rendimiento pico ≠ sostenido.** El pico dura minutos; lo que importa es el **frame rate sostenido** con el teléfono ya caliente. Google documenta que, sin diseñar para el térmico, el deterioro de frame rate típicamente aparece a los **45-50 minutos** de juego continuo (developer.android.com/games/optimize) — pero en un device de gama baja mal presupuestado puede ser en 3-5.
- **Estados térmicos del sistema (Android `PowerManager`, 7 niveles):** `NONE → LIGHT → MODERATE → SEVERE → CRITICAL → EMERGENCY → SHUTDOWN`. A partir de `LIGHT/MODERATE` ya conviene bajar carga; en `SEVERE` el sistema ya te está throttleando. iOS expone `ProcessInfo.thermalState` con 4 niveles (`nominal / fair / serious / critical`).
- **ADPF (Android Dynamic Performance Framework)** y el **Thermal API** dan la señal temprana para reaccionar ANTES de que el hardware te la baje.

### La palanca de diseño: presupuestar para lo sostenible, no para el pico

| Palanca | Efecto térmico | Cuándo |
|---|---|---|
| **Cap a 30 fps** (`Application.targetFrameRate = 30`) | El que más ahorra: menos trabajo/segundo = menos calor = frame rate estable indefinido | Juegos por turnos, casual, puzzle, cartas, la mayoría del catálogo casual |
| **60 fps** | El doble de trabajo/frame → más calor → más riesgo de throttling a los minutos | Solo si el género lo EXIGE (acción rápida, shooters, rhythm) y el presupuesto por-frame deja margen térmico |
| **Dejar margen del presupuesto de frame** | No gastar los 33 ms (30 fps) o 16 ms (60 fps) completos: apuntar a ~65% deja aire para cuando el SoC throttlee y no caer bajo el cap | Siempre en móvil [ver: unity/rendimiento-unity §1] |
| **Adaptive Performance / scalers** | Baja calidad automáticamente cuando sube la temperatura, en vez de dejar que el sistema throttlee a lo bruto | Cualquier juego 3D con carga variable |

El trade-off **30 vs 60** en móvil no es "más fps mejor": 30 fps SÓLIDO y sostenido se siente mejor que 60 que se derrumba a 40-45 con stutter a los 6 minutos. Elegir 30 estable es una decisión de calidad, no una rendición. Si vas a 60, tienes que **ganártelo** sosteniéndolo caliente.

### Unity Adaptive Performance (`com.unity.adaptiveperformance`)

Paquete oficial que da feedback del **estado térmico y de energía** del device y permite reaccionar a la tendencia de temperatura para "mantener frame rate constante y prevenir el thermal throttling" (docs Unity, verificado 2026-07-20). Piezas:
- **Provider por vendor** (Samsung/genérico via ADPF): expone `ThermalMetrics` (warning level, temperature trend, throttling imminent) y `PerformanceMetrics`.
- **Indexer + Scalers**: cuando sube el warning level, baja automáticamente palancas de calidad. Scalers típicos: **resolución dinámica, framerate objetivo, LOD bias, densidad de sombras, calidad de post/LUT, VFX**. Priorizas cuáles bajar primero.
- El flujo: escuchar `ThermalEvent` / warning level y actuar temprano (bajar render scale, apagar sombras dinámicas, capar fps) ANTES de que el hardware throttlee. ⚠️ Versión del paquete: el contenido de este archivo se verificó contra la doc de **5.1** (2026-07-20); la versión vigente en el Package Manager a esta fecha es **6.0**, cuyo manual redirige al Unity Manual consolidado. Los nombres exactos de enums/propiedades: confirmar en la doc del paquete instalado al integrar (no re-verificados campo por campo en esta sesión).

Patrón mínimo de reacción térmica (sin Adaptive Performance, sólo Unity core — degradar antes de que el SO throttlee):

```csharp
// Reacción a presión térmica: primero baja render scale, luego capa fps.
void OnThermalWarning(int level) { // 0=ok, 1=warning, 2=throttling inminente
    var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
    switch (level) {
        case 1: urp.renderScale = 0.8f; break;             // menos fill rate
        case 2: urp.renderScale = 0.7f;
                Application.targetFrameRate = 30; break;    // sacrifica fps para sostener
        default: urp.renderScale = 1.0f; break;
    }
}
// En menús/turnos: renderizar menos sin parar la lógica.
UnityEngine.Rendering.OnDemandRendering.renderFrameInterval = 3; // 1 de cada 3 frames
```

### Frame pacing: la consistencia se siente más que el número

En móvil, **30 fps parejos se sienten mejor que 45 fps con jitter**. El ojo detecta la varianza del frame time (unos frames a 20 ms, otros a 40 ms) como tirones, aunque el promedio sea alto. Palancas:
- **Optimized Frame Pacing** (Android Player Settings > Resolution and Presentation): activa la librería de frame pacing de Android (Swappy) para entregar frames a intervalos parejos y alineados al vSync de la pantalla. Combinar con el **Frame Pacing API** de Android que Google recomienda para evitar buffers sobrecargados (developer.android.com/games/optimize).
- Elegir un cap que sea **divisor del refresh** de la pantalla (Unity redondea `targetFrameRate` al divisor más cercano): 30 en pantalla de 60 Hz, 60/120 en pantallas de 120 Hz. Un cap que no divide limpio produce judder.
- Pantallas de alto refresh (90/120 Hz) prometen más pero **calientan más**: subir a 90/120 sólo si se sostiene; si no, capar a 60 y que sea parejo.

## 3. Batería: no fundir el teléfono

Un juego que calienta el teléfono y le come 30% de batería en 20 minutos tiene reseñas de 1 estrella y desinstalos, aunque el frame rate sea perfecto. Batería y térmico son la misma moneda: lo que drena batería genera calor.

| Lo que drena batería | Por qué | Antídoto |
|---|---|---|
| **GPU / pantalla a full** | Renderizar 60 fps con overdraw alto es el mayor consumidor | Cap de fps, `render scale` <1.0, menos overdraw (partículas/UI translúcida), shaders simples [ver: unity-movil-graficos] |
| **CPU a full en todos los cores** | Maxear los big cores calienta rápido; Jobs+Burst en TODOS los cores puede ser contraproducente en móvil | Repartir, no saturar; trabajo corto a los cores lentos [ver: §7]; no quemar el frame entero |
| **Radio (red)** | Encender la radio celular/WiFi para cada request la mantiene despierta (tail energy); polling frecuente es carísimo | Batchear requests, backoff, no polling agresivo; sincronizar en ráfagas [ver: unity-movil-input-servicios] |
| **Wakelocks / no dejar dormir** | Renderizar en menús/pantallas estáticas gasta igual que en gameplay | `OnDemandRendering.renderFrameInterval` para menús y juegos por turnos: renderiza menos frames sin parar la lógica |
| **Sensores/GPS/vibración** | Giroscopio, ubicación, haptics continuos | Usarlos sólo cuando aportan; apagarlos fuera de foco |
| **Frames de más en background** | Seguir renderizando sin foco | Bajar `targetFrameRate` al perder foco (`OnApplicationPause/Focus`) o pausar |

Regla práctica: en menús, pausa, pantallas de espera y juegos por turnos, **renderizar menos** (`OnDemandRendering` + `targetFrameRate` bajo) es dinero directo en batería y estrellas.

## 4. Memoria: el mayor limitante real en móvil

En móvil la memoria mata más builds que el frame rate. No hay swap útil, y cuando te pasas, el SO **te cierra la app sin avisar**: en Android el **Low Memory Killer (LMK)** libera memoria matando procesos; en iOS el **jetsam** mata la app si excede su límite (que depende del RAM físico del device, más estricto en devices viejos). Un crash por OOM en el device barato = reseña de 1 estrella y churn.

- **Las texturas son el mayor consumidor típico** [ver: unity/rendimiento-unity §8]. Ángulo móvil: en el device de gama baja el techo se alcanza rápido, así que la compresión ASTC + `Max Size` honesto por asset no es "optimización", es requisito para no crashear.
- **Presupuesto de RAM por gama** (orientativo — depende de RAM física, del SO y de cuántas apps hay abiertas; VERIFICAR con Memory Profiler en el device target):

| Gama | RAM física típica 2026 | Presupuesto seguro para el juego* |
|---|---|---|
| Baja | 2-4 GB | ~0.5-1 GB (el SO + otras apps se comen el resto; el LMK/jetsam pega antes de agotar) |
| Media | 4-6 GB | ~1-1.5 GB |
| Alta | 8-16 GB | ~2-3 GB (aun así, no confiarse: iOS jetsam no te da todo el RAM) |

*Cifras orientativas de referencia de la industria, NO fuente única verificable en esta sesión; el número que vale es el que mide el Memory Profiler en el device concreto antes de que salte el LMK/jetsam.

- **Señales de presión de memoria — escuchar y liberar:** `Application.lowMemory` (Unity) para soltar assets no esenciales, bajar calidad de texturas y forzar descargas; Android **Memory Advice API** para adaptar gameplay al estado de memoria; `onTrimMemory`. No esperar al crash.

```csharp
void Awake() { Application.lowMemory += OnLowMemory; }
void OnLowMemory() {                    // el SO avisa: soltar YA o el LMK/jetsam mata la app
    Resources.UnloadUnusedAssets();     // libera lo no referenciado
    QualitySettings.globalTextureMipmapLimit = 1; // Unity 6 (antes masterTextureLimit): mitad de resolución
    // + liberar Addressables de contenido no visible en escena
}
```
- **Addressables para cargar/descargar por nivel** [ver: unity/rendimiento-unity §8]: en móvil la disciplina es más dura — un `LoadAssetAsync` sin su `Release` no es un leak "que se limpia luego", es el device barato que crashea a los 20 minutos. Agrupar bundles por nivel/escena y descargar el nivel anterior ANTES de cargar el siguiente cuando la RAM aprieta (aceptar un pequeño hitch de carga a cambio de no morir por OOM).
- **`Resources/` es peor en móvil**: todo su contenido se carga y ocupa; auditarlo [ver: unity/build-plataformas].

## 5. Tamaño de build al límite: el APK/AAB/IPA chico

En móvil el tamaño no es sólo disco: **cada MB extra cuesta instalaciones**. Google reportó (blog Google Play, 2017 — no re-verificado en esta sesión) que la tasa de conversión de instalación cae ~**1% por cada ~6 MB** de aumento de tamaño; el efecto es mayor en mercados emergentes con datos caros y devices con poco almacenamiento. Y hay un muro duro: pasar el umbral de descarga por datos móviles frena la instalación hasta que el usuario encuentra WiFi (y muchos nunca vuelven).

### Límites reales de las tiendas (verificado 2026-07-20)

| Límite | Valor | Fuente |
|---|---|---|
| **Google Play — APKs de instalación (base + config, comprimido)** | ≤ **4 GB** | developer.android.com/guide/app-bundle |
| Google Play — módulo on-demand + config (comprimido) | ≤ **4 GB** | developer.android.com/guide/app-bundle |
| Google Play — juegos > **200 MB** deben usar **Play Asset Delivery** (no OBB) | umbral 200 MB | developer.android.com/guide/playcore/asset-delivery |
| Google Play — asset packs | límites propios (no cuentan al 4 GB); install-time exige 2× su tamaño en disco libre | id. |
| **Apple — tamaño máximo de app (descomprimida, iOS 9+)** | **4 GB** | developer.apple.com (maximum build file sizes) |
| **Apple — sección `__TEXT` del ejecutable (iOS 9+)** | **≤ 80 MB** total | id. — **gotcha IL2CPP, ver abajo** |
| Apple — App Clip | ≤ 15 MB (iOS 16), 100 MB sólo-digital (iOS 17) | id. |
| Apple — descarga por datos móviles sin WiFi | **500 MB** (subió de 200 MB en 2022) — reportado ampliamente; **no confirmado contra fuente Apple en esta sesión, verificar** | — |

- **Gotcha IL2CPP en iOS — el límite de 80 MB de `__TEXT`:** IL2CPP genera C++ y el binario puede inflar la sección `__TEXT`. Un juego grande con mucho código/genéricos puede chocar con el tope de 80 MB del ejecutable aunque la app total quepa de sobra. Antídotos: **Managed Stripping Level más alto** con `link.xml`/`[Preserve]` probados, **IL2CPP Code Generation = "Faster (smaller) builds"** (genéricos compartidos), y auditar librerías de terceros [ver: unity/build-plataformas].

### Palancas de tamaño específicas de móvil

1. **Texturas primero, siempre** (dominan el build [ver: unity/build-plataformas]): **ASTC** con override por plataforma, bloque más agresivo donde se tolere (6x6 albedo, 8x8+ para lo que no se mira de cerca), `Max Size` honesto (casi nada necesita 2048). ETC2 sólo como fallback de compatibilidad [ver: arte-movil].
2. **Play Asset Delivery (Android) / On-Demand Resources / Background Assets (iOS)**: sacar del binario de instalación lo que no se necesita en el primer arranque (niveles avanzados, idiomas, cinemáticas) y entregarlo bajo demanda. Baja el peso inicial → mejor conversión y sortea el muro de datos móviles.
3. **Managed stripping + Strip Engine Code** [ver: unity/build-plataformas].
4. **Audio**: Vorbis, mono para SFX, no todo a 44.1 kHz.
5. Objetivo práctico de peso inicial: mantenerlo **bajo** para no perder conversión y no chocar el muro celular (apuntar a la banda baja, no al límite de la tienda) — el "peso inicial ideal" concreto depende de tu público [ver: release-movil], pero el principio es: cada MB por debajo del umbral de datos móviles compra instalaciones.

## 6. Presupuestos reales por gama de device (2026)

⚠️ Los números duros de tris/draw calls **no tienen fuente única verificable** (Unity/Arm publican rangos que cambian por device y por lo que hace la GPU); tratar como **punto de partida** y VALIDAR el techo real midiendo fill rate / bandwidth / vertex en el device target [ver: unity/rendimiento-unity §6, modelado/presupuestos-poligonos]. Lo que SÍ es doctrina oficial: el límite se descubre midiendo, no con la tabla.

| Recurso | Baja (2-4 GB, GPU débil) | Media (4-6 GB) | Alta (flagship) |
|---|---|---|---|
| Tris en pantalla | ~100 k | 100-500 k | 500 k-1 M+ |
| Draw calls / SetPass | < 100 | 100-300 | 300-600 |
| Texturas (ASTC / max size) | 6x6-8x8, ≤ 1024 | 6x6, ≤ 2048 | 4x4-6x6, ≤ 2048-4096 |
| RAM para el juego | ~0.5-1 GB | ~1-1.5 GB | ~2-3 GB |
| Target fps realista | 30 sostenido | 30-60 | 60 (ganado, sostenido) |

- El **cuello típico en móvil es el fill rate** (píxeles × overdraw), no los vértices, por la GPU tiled y las pantallas de altísima densidad [ver: unity/rendimiento-unity §6, unity-movil-graficos]. Bajar `render scale` suele dar más que recortar polígonos.
- **Por qué manda el fill rate — la GPU móvil es tiled (TBDR):** divide la pantalla en tiles pequeños y los procesa en memoria on-chip para ahorrar bandwidth (el recurso más caro en móvil). Consecuencia de rendimiento: lo que **rompe el tile** cuesta carísimo — leer el framebuffer a mitad de frame, camera stacking, post-procesado que hace resolve/reload, cambiar render target muchas veces. Regla móvil: minimizar resolves, no leer el color/depth a media escena, y aprovechar que MSAA es **barato** en tiled (se resuelve dentro del tile) frente a bajar resolución. El detalle de shaders/render features va en [ver: unity-movil-graficos]; aquí basta saber que el presupuesto de bandwidth es tan real como el de tris.
- Diseñar **tiers de calidad** (low/mid/high) que el juego elige en runtime según el device, no un único preset [ver: §8].

## 7. CPU móvil: menos cores, más lentos, y big.LITTLE

El CPU móvil no es un desktop chico: es una arquitectura **big.LITTLE** (unos cores rápidos "big" y varios lentos "LITTLE" de bajo consumo). Implicaciones:

- **El main thread es el rey.** Unity ejecuta gameplay + generación de comandos de render en el main thread. Si el main thread se pasa del presupuesto de frame, no hay GPU que te salve. Google recomienda un **mínimo de 2 threads** (game thread + **render thread**) para que el juego ocupe **≥2 CPUs a la vez** — en Unity, activar el **Multithreaded Rendering** (Player Settings Android) es la palanca base.
- **CPU affinity**: el trabajo corto y no crítico conviene mandarlo a los cores lentos (típicamente índices 0-3) para ahorrar energía/calor; el trabajo pesado del frame a los big cores. Esto lo gestiona el scheduler del SO, pero saturar todos los big cores con Jobs es lo que dispara el térmico.
- **Jobs + Burst en móvil — matiz respecto a la base** [ver: unity/rendimiento-unity §4]: siguen valiendo para trabajo masivo paralelizable, pero en móvil **maxear todos los cores calienta y throttlea**. El objetivo no es "usar el 100% de los cores", es **terminar el frame dentro del presupuesto dejando margen térmico**. Burst (SIMD/LLVM) ayuda porque hace más con menos ciclos → menos energía por unidad de trabajo, que es exactamente lo que quieres en móvil.
- **UI**: apuntar a **2-3 ms** de tiempo de UI por frame (Google); el rebuild de Canvas se paga carísimo en el CPU lento [ver: unity/rendimiento-unity §7, ux-ui/mobile-ux].
- Gama alta tiende a ser **CPU-bound**; los entry-level a menudo **I/O-bound** (carga desde disco lento) — optimizar la carga/streaming en gama baja (Google, developer.android.com/games/optimize).

## 8. Profilear EN el device real (y en el barato, y caliente)

La base ya fija el principio [ver: unity/rendimiento-unity §1]. El ángulo móvil añade tres reglas que se saltan siempre:

1. **Profilear en el device de gama BAJA del target, no en el flagship.** Un frame que sobra en tu teléfono puede estar 3× por encima del presupuesto en el barato. El veredicto lo da el mínimo-spec.
2. **Thermal-aware profiling: sesiones LARGAS con el device ya caliente** (10-15+ min). El primer minuto miente. Medir el frame rate SOSTENIDO, no el pico de arranque. Vigilar el estado térmico (`ProcessInfo.thermalState` / `PowerManager` / Adaptive Performance) durante la captura.
3. **Development Build + Profiler por red/cable** [ver: unity/rendimiento-unity §1]; y para GPU móvil usar las herramientas del vendor:

| Herramienta | Para qué |
|---|---|
| **Unity Profiler + Memory Profiler** (Development Build en device) | CPU/GPU/memoria por frame; snapshots de memoria en el punto caliente |
| **Arm Mobile Studio / Streamline** (Mali) | Contadores de GPU en Android Arm: fill rate, bandwidth, cycles |
| **Snapdragon Profiler** (Adreno/Qualcomm) | Contadores de GPU en Android Qualcomm |
| **Xcode Instruments + Metal System Trace / GPU Frame Capture** (iOS) | GPU, memoria, energía y estado térmico en iPhone/iPad |
| **Android GPU Inspector (AGI)** | Trazas de GPU/frame en Android |

- **Frame Debugger** para ver por qué se rompe un batch [ver: unity/rendimiento-unity §2] sigue valiendo, pero el "por qué va lento" en móvil suele ser GPU (fill rate/bandwidth) → los contadores del vendor son los que te lo dicen.

## 9. Escalar el trabajo a la gama del device (resolución dinámica y tiers)

La técnica que hace que un mismo build corra decente en el barato Y aproveche el flagship: **no un preset único, sino escalar en runtime**.

| Técnica | Qué hace | Ángulo móvil |
|---|---|---|
| **Render Scale** (URP Asset) | Renderiza a menor resolución interna y escala a pantalla | La palanca de fill rate #1 en móvil; bajar de 1.0 en pantallas de alta densidad casi no se nota (probar 0.7-0.9 y medir) [ver: unity/rendimiento-unity §6] |
| **Dynamic Resolution** (Allow Dynamic Resolution + `ScalableBufferManager`) | Ajusta la resolución interna frame a frame según carga | Mantiene el fps objetivo bajando resolución cuando el frame se pasa; ideal para sostener 30/60 cuando sube el térmico |
| **STP (Spatial-Temporal Post)** (URP, Unity 6) | Upscaling temporal de mejor calidad que el escalado plano | Recupera nitidez tras bajar render scale |
| **Device tiering en runtime** | Detectar gama (RAM, GPU, modelo) al arrancar y aplicar preset low/mid/high | Texturas, sombras, VFX, LOD bias, fps y render scale distintos por tier; una sola build sirve a todo el mercado |
| **Adaptive Performance scalers** | Bajan calidad automáticamente al subir la temperatura | La versión "reactiva" del tiering: no sólo por gama, sino por estado térmico en vivo [ver: §2] |
| **LOD bias / Quality Settings por tier** | Menos detalle a distancia y menos calidad global en gama baja | Combinar con mipmap streaming para recortar VRAM |

Bootstrap de tiering al arrancar (heurística barata; refinar con una tabla de GPUs conocidas):

```csharp
// Clasifica el device al primer arranque y fija el preset. Guardar el tier elegido.
int mem = SystemInfo.systemMemorySize;        // MB de RAM física
int tier = mem < 4000 ? 0 : (mem < 6000 ? 1 : 2); // 0=low, 1=mid, 2=high (orientativo)
QualitySettings.SetQualityLevel(tier, true);      // presets con texturas/sombras/LOD por tier
Application.targetFrameRate = tier == 0 ? 30 : 60; // ganar 60 sólo donde se sostiene
var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
urp.renderScale = tier == 0 ? 0.75f : 1.0f;
// SystemInfo.graphicsDeviceName / processorCount afinan la clasificación en casos límite.
```

Regla: el juego debe **elegir su nivel de trabajo**, no imponerlo. El flagship se ve bonito; el barato se mantiene jugable. Ambos con el mismo binario. Y siempre dejar un **override manual** de calidad en ajustes (el jugador conoce su teléfono) [ver: ux-ui/mobile-ux].

## Reglas prácticas

- [ ] Fijar el **minimum-spec real** (1-2 devices de gama baja físicos del público objetivo) y profilear ahí, no en el flagship [ver: mercado-movil].
- [ ] `Application.targetFrameRate` explícito (el default móvil es 30) [ver: unity/rendimiento-unity §6]; elegir 30 sostenido salvo que el género exija 60 ganado.
- [ ] Presupuestar al **~65% del frame** para dejar margen térmico; medir el frame rate **sostenido** con el device caliente (10-15+ min), no el pico.
- [ ] Integrar Adaptive Performance (o leer estado térmico) y **bajar calidad ANTES** de que el SoC throttlee.
- [ ] En menús/turnos/pausa: `OnDemandRendering` + fps bajo; bajar `targetFrameRate` al perder foco. Batería = estrellas.
- [ ] Texturas: **ASTC** con override por plataforma + `Max Size` honesto — no es opcional, es lo que evita el OOM en gama baja.
- [ ] Escuchar `Application.lowMemory` / Memory Advice API y liberar; **cada `LoadAssetAsync` con su `Release`**; descargar el nivel anterior antes de cargar el siguiente.
- [ ] Snapshot de Memory Profiler en el device en el punto caliente; los mayores consumidores casi siempre son texturas.
- [ ] Fill rate primero: `render scale` <1.0, dynamic resolution para sostener fps, menos overdraw [ver: unity-movil-graficos].
- [ ] Multithreaded Rendering + **Optimized Frame Pacing** activados; cap que divide el refresh de pantalla (frames parejos > fps altos con jitter).
- [ ] Jobs+Burst para trabajo masivo, pero **sin maxear todos los cores** (calienta); objetivo = frame dentro de presupuesto con margen térmico.
- [ ] Peso de build por debajo del umbral de datos móviles; sacar lo no-inicial a **Play Asset Delivery / On-Demand Resources / Background Assets**.
- [ ] iOS: vigilar la sección `__TEXT` (≤ 80 MB) — stripping alto + "Faster (smaller) builds" si el binario IL2CPP infla [ver: unity/build-plataformas].
- [ ] Device tiering en runtime (low/mid/high) + Quality Settings por tier; una build, todo el mercado.
- [ ] Profilear GPU con la herramienta del vendor (Arm Streamline / Snapdragon Profiler / Xcode Instruments), no sólo el Unity Profiler.
- [ ] Verificar en el device real, caliente y de gama baja — no "el build terminó" ni "va bien en mi teléfono".

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| "Va a 60 en mi teléfono" (flagship, frío, 3 min) | El veredicto es el device barato, caliente, 15 min; profilear ahí |
| 60 fps que se derrumba a 40 con stutter a los minutos | Es thermal throttling; elegir **30 sostenido** o presupuestar con margen y Adaptive Performance |
| Gastar el presupuesto de frame entero (33/16 ms) | Dejar ~35% de margen para cuando el SoC throttlee |
| Maxear todos los cores con Jobs "porque hay que usar la CPU" | Calienta y throttlea; objetivo es terminar el frame con margen térmico, no usar el 100% |
| Renderizar 60 fps en el menú estático | `OnDemandRendering` + fps bajo; funde batería y calienta gratis |
| Texturas sin comprimir o 2048 por todo → OOM en gama baja | ASTC + `Max Size` honesto; el LMK/jetsam cierra la app sin avisar |
| `LoadAssetAsync` sin `Release` "se limpia luego" | En móvil es el crash por OOM a los 20 min; espejo load/release estricto |
| Build que pasa el umbral de datos móviles | Conversión de instalación se desploma; Play Asset Delivery/ODR para lo no-inicial |
| iOS rechaza/infla por `__TEXT` > 80 MB con IL2CPP | Stripping alto + link.xml probado + "Faster (smaller) builds" |
| Un único preset gráfico para todo el mercado | Device tiering en runtime: low/mid/high con render scale, texturas y fps distintos |
| Recortar polígonos cuando el cuello es fill rate | Bajar `render scale`/resolución dinámica da más que quitar tris [ver: unity-movil-graficos] |
| Profilear sólo con el Unity Profiler y no ver el cuello GPU | Contadores del vendor (Streamline/Snapdragon/Instruments) para fill rate y bandwidth |
| Ignorar el estado térmico durante el profiling | Medir con el device caliente y leer `thermalState`/warning level a la vez |
| fps alto pero con tirones (jitter) | Activar Optimized Frame Pacing y capar a un divisor del refresh; 30 parejo > 45 con jitter |

## Fuentes

Consultadas directamente en esta investigación (2026-07-20), salvo lo marcado:

- **App Bundle download size** — developer.android.com/guide/app-bundle — base APK + config APKs comprimidos ≤ 4 GB; módulo on-demand + config ≤ 4 GB; asset packs con límites propios.
- **Play Asset Delivery** — developer.android.com/guide/playcore/asset-delivery — juegos > 200 MB deben usar PAD (no OBB); install-time exige 2× su tamaño en disco libre; fast-follow/on-demand pocos cientos de MB extra. (Números exactos por tipo de asset pack: support.google.com/googleplay/.../9859372 — no renderizable en esta sesión, verificar.)
- **Maximum build file sizes** — developer.apple.com (App Store Connect help) — app descomprimida iOS 9+ ≤ 4 GB; ejecutable `__TEXT` ≤ 80 MB; App Clip ≤ 15 MB (iOS 16) / 100 MB sólo-digital (iOS 17).
- **Optimize your game** — developer.android.com/games/optimize — estados térmicos `PowerManager` (NONE→SHUTDOWN, 7 niveles), ADPF/Thermal API, deterioro de frame rate típico a 45-50 min, UI 2-3 ms, mínimo 2 threads (game+render, ≥2 CPUs), CPU affinity a cores lentos, Frame Pacing API, Memory Advice API, entry-level I/O-bound vs high-end CPU-bound.
- **Adaptive Performance** — docs.unity3d.com (com.unity.adaptiveperformance@5.1, verificado 2026-07-20) — feedback de estado térmico y de energía, reacción a tendencia de temperatura para mantener frame rate y prevenir throttling; Indexer/scalers. ⚠️ La versión vigente en el Package Manager a 2026-07-20 es **6.0** (su manual redirige al Unity Manual consolidado, no re-verificado campo por campo en esta sesión); confirmar Indexer/Scalers/enums en la doc del paquete instalado al integrar.
- **Base hermana** — knowledge/unity/rendimiento-unity.md — targetFrameRate default 30 móvil, Adaptive Performance, Render Scale/Dynamic Resolution/STP, ASTC/mipmaps, Addressables ref-counting, tabla orientativa de tris/draw calls, Jobs+Burst.
- **Base hermana** — knowledge/unity/build-plataformas.md — IL2CPP/stripping/link.xml, texture compression por plataforma, reducción de tamaño de build, trampa de `Resources/`, AAB vs APK.
- Apple — límite de descarga por datos móviles **500 MB** (subió de 200 MB en 2022): reportado ampliamente, **no confirmado contra fuente Apple en esta sesión — verificar** antes de depender del número.
- Google Play — caída de conversión ~1% por ~6 MB de tamaño: blog Google Play "Shrinking APKs, growing installs" (2017), **no re-verificado en esta sesión**; tratar como orientativo.
- Presupuestos de tris/draw calls/RAM por gama y umbrales de RAM (LMK/jetsam): **sin fuente única verificable**; orientativos, validar con Memory Profiler y contadores de GPU en el device target.
