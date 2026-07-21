# Release y publicación móvil

> **Cuando cargar este archivo:** al llevar un juego Unity 6 móvil del build firmado a las tiendas — pipeline iOS/Android de punta a punta, keystore/provisioning, tracks de testing y TestFlight, App Privacy / Data Safety / ATT / IARC en clave móvil, presupuesto de descarga (OTA), soft launch y sus métricas, cadencia de updates con review, y el checklist de release móvil. Para el CÓMO técnico genérico del build y la firma [ver: unity/build-plataformas]; para lo legal/comercial de las 4 tiendas [ver: pipeline/publicacion-tiendas]; para benchmarks de mercado (CPI, retención, ARPDAU) [ver: mercado-movil].

**Qué añade este archivo:** SOLO el ángulo móvil que profundiza sobre las bases. Lo genérico (AAB vs APK, keystore, IL2CPP, stripping, tracks de Play, review de Apple, fees, IARC, ATT/UMP) ya está en `unity/build-plataformas` y `pipeline/publicacion-tiendas` — aquí se cruza-referencia y se aporta el detalle específico de un juego móvil real: presupuesto OTA, entrega de assets, notificaciones locales, pre-launch report, soft launch operativo, phased/staged rollout y la cadencia de updates.

Datos con fecha verificados contra docs oficiales el **2026-07-20**. Deadlines, versiones de SDK y límites de tamaño caducan — re-verificar antes de decisiones de dinero o de fecha de lanzamiento.

## 1. El pipeline de release móvil de punta a punta

| Etapa | Android (Google Play) | iOS (App Store) |
|---|---|---|
| Firma | Keystore de upload + **Play App Signing** custodia la clave final [ver: unity/build-plataformas] | Certificado + **provisioning profile** (automático con Xcode); Apple custodia la firma de distribución |
| Formato de subida | **AAB** obligatorio; APK solo sideload/pre-launch | **.ipa** vía Xcode Archive → Organizer → Distribute |
| Máquina de build | Cualquier OS (Unity exporta AAB directo) | **Solo macOS** con Xcode (Unity genera proyecto Xcode) |
| Canal de beta | Tracks: interno / cerrado / abierto | **TestFlight** (interno / externo) |
| Consola | Play Console | App Store Connect |
| Review | Automática + humana; horas–días, sin SLA | Humana; **90% <24h**; cuestionario de edad propio |
| Rollout | **Staged rollout** por % configurable | **Phased release** 7 días (1/2/5/10/20/50/100%) |
| Requisitos previos | Data safety, IARC, target audience, privacy URL, target API | App Privacy, Sign in with Apple si hay social login, usage descriptions, export compliance |

El critical path del calendario móvil no es el build: es la **latencia de cuentas y testing** — cuenta personal de Play nueva exige closed test de 12 testers × 14 días continuos antes de producción [ver: pipeline/publicacion-tiendas §2]. Planificar 3-4 semanas de colchón.

**Orden real de operaciones (juego F2P móvil):**
1. Cuentas developer + verificación de identidad (semanas de latencia).
2. Bundle ID/package name definitivos, keystore de upload, App ID en Apple (inmutables tras publicar).
3. Build IL2CPP en device real desde la semana 1-2 (stripping, permisos, memoria solo se ven ahí).
4. Cablear ANTES del launch: IAP, ads/consent (ATT/UMP), analytics, crash reporting, remote config, notificaciones locales.
5. Track interno (Play) / TestFlight interno (iOS) para iterar; luego cerrado/externo con el requisito de testers.
6. Rellenar todo el Policy/App Privacy: Data safety, IARC, privacy URL, target audience, App Privacy labels.
7. Soft launch en mercado de prueba → medir → iterar por remote config.
8. Producción global con staged/phased rollout; monitorear día 0-7 (§10).

## 2. Android — profundidad móvil

### Firma y símbolos de crash
- Keystore de upload: crear una vez, backup fuera del repo, jamás commitear; Play App Signing para poder resetear la upload key con soporte [ver: unity/build-plataformas].
- **Subir símbolos de debug nativos** (`symbols.zip`, `PlayerSettings.Android.createSymbols`) al publicar el AAB: sin ellos, los crashes de IL2CPP/nativos en **Android vitals** salen como stacks ofuscados e inservibles. Es el paso que casi todo mundo olvida y el que hace que los crashes de producción sean legibles.

### AAB + entrega de assets (Play Feature/Asset Delivery)
- El AAB deja que Play entregue a cada device solo su ABI, densidad y formato de textura → descarga más pequeña sin esfuerzo.
- Límite de descarga (verificado, developer.android.com): la suma de **APKs comprimidos** que un device baja para instalar (base + config, o un feature module on-demand) debe ser **≤ 4 GB**. Los **asset packs** no cuentan contra ese límite y tienen sus propios topes (por modo de entrega; ver `answer/9859372#size_limits` — no legibles en esta pasada, **verificar** los MB/GB exactos por pack).
- **Play Asset Delivery (PAD)** — tres modos, cablearlos según el asset:
  - **install-time**: parte de la instalación inicial (contenido imprescindible del arranque).
  - **fast-follow**: se descarga automáticamente justo después de instalar (nivel 2-3, sin que el jugador espere en el arranque).
  - **on-demand**: se baja cuando el juego lo pide (mundos/temporadas posteriores).
- Unity soporta PAD; los assets grandes salen del AAB base y bajan el peso inicial de tienda [ver: unity-movil-rendimiento para el presupuesto de memoria/descarga].

### Target API, tracks y Billing
- Target API a 2026: **API 36 (Android 16)** para apps nuevas y updates desde **31-ago-2026** (extensión pedible hasta 1-nov-2026) [ver: unity/build-plataformas, pipeline/publicacion-tiendas §2].
- Tracks interno→cerrado→producción [ver: pipeline/publicacion-tiendas §2]. El track **interno** está exento de review de políticas y de Data safety: úsalo para iterar builds en minutos.
- **Google Play Billing Library**: **v8 mínimo obligatorio** para apps nuevas y updates desde **31-ago-2026** (extensión pedible hasta 1-nov-2026) — mismo calendario que el target API (verificado, developer.android.com/google/play/billing/deprecation-faq). Unity IAP la trae empaquetada — confirmar que la versión del paquete instalado cumple v8 antes de subir [ver: monetizacion-movil].

### Pre-launch report y Android vitals (mecanismos móvil de Play)
- **Pre-launch report** (Play Console): al subir a un track de testing, Play corre tu build en un parque de **devices reales** (Firebase Test Lab) por unos minutos — detecta crashes, ANRs, problemas de seguridad, accesibilidad y saca capturas por device. Gratis y automático: revisarlo SIEMPRE antes de promover a producción.
- **Android vitals** (verificado, Play Console Help): Play reduce la visibilidad si superas los umbrales de "bad behavior" — **crash rate percibido ≥ 1.09%** o **ANR rate percibido ≥ 0.47%** globalmente, o **≥ 8% en un device concreto** (cualquiera de los dos, global o por-device, dispara la penalización). En móvil, el crash de un device de gama baja te cuesta ranking, no solo una reseña.
- **Play Integrity API** (anti-piratería / anti-cheat): para un juego con dinero real o compras, verifica que el binario es genuino, instalado por Play y en un device no comprometido. Reemplaza al viejo SafetyNet Attestation. Opcional, pero es la defensa estándar contra clientes modificados [ver: monetizacion-movil].

## 3. iOS — profundidad móvil

### Firma, build y símbolos
- Cuenta Apple Developer Program (99 USD/año). Bundle ID debe coincidir con el App ID registrado; provisioning **Automatically manage signing** para equipo chico [ver: unity/build-plataformas].
- IL2CPP únicamente (Apple prohíbe JIT). Compilar con el **Xcode/SDK que Apple exige ese año** — desde 28-abr-2026, Xcode 26 / SDK iOS 26 [ver: unity/build-plataformas].
- **dSYM**: conservar/subir los dSYM del build para simbolizar crashes de IL2CPP en Organizer/servicios de crash. Unity genera código nativo — sin dSYM el crash log es inservible (el equivalente iOS de los símbolos de Android).
- **Export compliance** por build: si solo usas HTTPS estándar, poner `ITSAppUsesNonExemptEncryption = false` en Info.plist evita la pregunta manual en cada subida.

### TestFlight (el beta móvil de Apple)
- **Interno**: hasta 100 testers (miembros del equipo), sin review, disponible en minutos tras procesar el build.
- **Externo**: hasta 10 000 testers, requiere **Beta App Review** (más ligero que el review de App Store, pero existe) y links públicos/por email.
- Los **builds de TestFlight expiran a los 90 días** — para un beta largo hay que subir builds nuevos periódicamente.
- El build tarda en **procesar** tras subir (minutos–hora); planificarlo, no subir a última hora antes de una demo.
- **App Review Information**: si el juego tiene login/servidor, poner **credenciales demo** y notas para el reviewer — sin ellas es rechazo automático. **Expedited review** pedible para un bug crítico en producción o un evento con fecha (usarlo con moderación).

### Review de Apple: rechazos típicos de JUEGOS móviles
Las guidelines genéricas (2.1, 2.3.x, 3.1.1, 4.3, 5.1.x) están en [ver: pipeline/publicacion-tiendas §3]. Patrones que muerden específicamente a juegos móviles:

| Rechazo | Detalle móvil | Antídoto |
|---|---|---|
| **2.1 completeness** (40%+ de rechazos) | El reviewer juega TU build en un device real, a veces viejo/pequeño; crash en iPhone SE = rechazo | Probar en device matrix real, no solo simulador [ver: unity-movil-rendimiento] |
| **IAP no testeable** | Los productos IAP deben subirse/adjuntarse con el binario y estar "Ready to Submit"; si el reviewer no los ve, es 2.1 | Adjuntar los IAP a la versión; probar en sandbox de StoreKit [ver: monetizacion-movil] |
| **3.1.1** desbloqueos por IAP | Loot boxes con **odds publicadas antes de comprar**; **botón restore** obligatorio; monedas compradas no expiran | [ver: monetizacion-movil, pipeline/publicacion-tiendas §3] |
| **4.8 Sign in with Apple** | Si el juego ofrece login social (Google/Facebook), **debe** ofrecer también Sign in with Apple | Añadir Sign in with Apple o quitar el social login |
| **5.1.2 ATT** | SDK de ads leyendo IDFA sin el prompt ATT = rechazo | Prompt ATT antes de tocar IDFA; cablear el consentimiento a TODOS los SDKs [ver: monetizacion-movil] |
| **5.1.1 borrado de cuenta** | Si hay cuentas, borrado in-app obligatorio (no "escribe a soporte") | Flujo de delete account dentro del juego |
| **2.3.2/2.3.3 screenshots** | Solo gameplay real, no key art ni cinemática | Capturas del juego en uso |

## 4. Requisitos móvil: privacy, consentimiento, ratings, notificaciones

Lo conceptual (qué formularios, qué declara cada uno) está en [ver: pipeline/publicacion-tiendas §5-6]. Ángulo móvil-operativo:

- **App Privacy (Apple) / Data Safety (Play)**: declarar lo que hacen TUS SDKs (ads, analytics, attribution), no solo tu backend — los SDKs transmiten identifiers aunque no tengas servidor. Usar las guías por-SDK de cada vendor; declaración inexacta = updates bloqueados o removal.
- **Privacy manifests iOS** (`PrivacyInfo.xcprivacy`): obligatorios para APIs "required reason" desde 2024; Unity 6 incluye el suyo, pero cada SDK de terceros debe traer el propio — auditarlos antes de subir [ver: unity/build-plataformas].
- **ATT + UMP**: prompt ATT (iOS) y UMP consent form (GDPR) en cada arranque, cableados a la red de ads [ver: monetizacion-movil, pipeline/publicacion-tiendas §6].
- **IARC**: un cuestionario en Play genera ESRB/PEGI/USK/etc.; apuestas simuladas (slots sin dinero real) suben el rating; mentir = removal [ver: pipeline/publicacion-tiendas §5].
- **Notificaciones (engagement/liveops móvil)** — **Unity Mobile Notifications** (paquete `com.unity.mobile.notifications`, v2.3.2 verificada): programa notificaciones **locales** one-time/repetibles en iOS y Android. Requisitos móvil:
  - Android 8+: toda notificación necesita un **notification channel** registrado o no se muestra.
  - Android 13+ (API 33): permiso **`POST_NOTIFICATIONS`** en runtime — pedirlo explícitamente o las notificaciones no salen.
  - iOS: pedir **autorización** al usuario antes de programar; sin permiso, nada.
  - Push remoto (server-driven) necesita APNs (iOS) / FCM (Android) — otro servicio; las locales bastan para recordatorios de energía/eventos [ver: retencion-liveops para el QUÉ notificar y la cadencia sana].
  - La **integración runtime** de estos servicios (permisos, IAP, notificaciones, analytics) vive en [ver: unity-movil-input-servicios]; este archivo cubre solo lo que la TIENDA exige de ellos en el release.

## 5. Presupuesto de descarga (OTA) — específico móvil

El peso de descarga es una palanca de **conversión de instalación**, no solo un número: en móvil, sobre datos celulares, el peso decide si el usuario instala ahora o "luego" (y nunca).

| Plataforma | Límite duro | Límite blando (OTA / conversión) |
|---|---|---|
| **iOS** | App uncompressed **≤ 4 GB**; ejecutable **≤ 80 MB** (verificado, Apple) | Apps por encima de **~200 MB** no se descargan por **datos móviles** sin que el usuario cambie el ajuste — histórico 100→150→**200 MB**; **verificar el valor vigente** |
| **Android** | Base + config APKs comprimidos **≤ 4 GB**; asset packs aparte (verificado) | Play muestra el tamaño en la ficha; cuanto menor, mejor conversión de instalación |

Palancas móvil para bajar el peso inicial (el detalle técnico en las bases):
- Compresión de textura por-plataforma (**ASTC** en móvil moderno) y Max Size honesto [ver: unity-movil-graficos, unity/build-plataformas].
- **Entrega diferida** de contenido: **Play Asset Delivery** (Android) y **On-Demand Resources / ODR** (iOS) o **Addressables** con descarga remota → el AAB/IPA base queda pequeño, el resto baja después [ver: unity-movil-rendimiento].
- Auditar el build report tras cada build gordo; vigilar `Resources/` [ver: unity/build-plataformas].
- Regla operativa móvil: apuntar el **primer download** por debajo del umbral OTA de datos (≈200 MB iOS) siempre que se pueda — el juego se instala en el momento, no "en casa con WiFi".

Mecanismos de entrega diferida, comparados:

| Mecanismo | Plataforma | Cuándo baja | Uso típico |
|---|---|---|---|
| Play Asset Delivery — install-time | Android | Con la instalación | Assets del arranque que no caben en el base |
| Play Asset Delivery — fast-follow | Android | Justo tras instalar, automático | Niveles 2-3, sin bloquear el primer arranque |
| Play Asset Delivery — on-demand | Android | Cuando el juego lo pide | Temporadas/mundos posteriores |
| On-Demand Resources (ODR) | iOS | Bajo demanda, gestionado por el OS | Equivalente iOS de PAD on-demand |
| Addressables + descarga remota | Ambas | Cuando el código lo pide | Contenido servido desde tu CDN/bucket, control total |

Elegir según control vs. simplicidad: PAD/ODR los hostea la tienda (gratis, sin CDN propio); Addressables remoto te da control pero exiges tu propio hosting y versionado [ver: unity-movil-rendimiento].

## 6. Soft launch — el mercado de prueba antes del global

El soft launch móvil es un lanzamiento REAL, limitado por país, para medir con dinero de UA real antes de escalar global. No aplica a premium single-player sin economía; es la norma en F2P/casual/idle [ver: monetizacion-movil, retencion-liveops].

**Mercados de prueba típicos** (elegir por parecido de audiencia y CPI barato):
- **Anglo, comportamiento ~US**: Canadá, Australia, Nueva Zelanda — señal de retención/monetización trasladable a US/UK, sin gastar el CPI de US.
- **CPI barato para volumen de retención**: Filipinas, Vietnam, Indonesia, Brasil, India — mucho install barato para leer curvas de retención/funnel; la monetización NO es trasladable a occidente.
- Nórdicos / Países Bajos: audiencia de alto valor, buena señal de ARPDAU.

**Qué medir antes del global** (los umbrales concretos por género están en [ver: mercado-movil]; aquí, el marco de release):
- **Retención D1 / D7 / D30** — la señal #1 de si el core loop retiene. Si D1 no llega al umbral del género, ningún gasto de UA lo salva.
- **Session length y sesiones/día** — engagement del loop.
- **Funnel de onboarding** (FTUE completion, paso donde cae la gente) [ver: diseno-movil].
- **Conversión a pagador, ARPDAU, LTV temprano** vs **CPI** — la ecuación LTV > CPI decide si escalas [ver: monetizacion-movil].
- **Crash-free users / ANR** por device — un crash de gama baja envenena la retención medida.

**Medición de UA (post-ATT)**: con la mayoría de usuarios iOS negando ATT, el IDFA no sirve para atribuir instalaciones — la señal viene de **SKAdNetwork / AdAttributionKit** (Apple) y del **Install Referrer** (Google Play), agregados y con retraso. Un **MMP** (mobile measurement partner: AppsFlyer, Adjust, Singular) unifica esa atribución con los eventos in-game; cablearlo antes del soft launch o no sabrás qué campaña rinde [ver: monetizacion-movil].

**Cómo se opera**: iterar economía, dificultad y precios con **remote config** sin re-release ni review [ver: pipeline/publicacion-tiendas §10]; el soft launch dura semanas–meses hasta que las métricas cruzan el umbral; solo entonces se abre a producción global y se enciende el gasto de UA. **Benchmarks de negocio (CPI/retención/ARPDAU): con fuente real, [ver: mercado-movil]; no fijar metas de memoria.**

## 7. Primer lanzamiento vs updates: cadencia y review

- **Cada binario nuevo pasa review** en ambas tiendas (Apple ~24h, Play horas–días). Lo que NO pasa review: cambios de **remote config** (números, flags, eventos on/off) [ver: pipeline/publicacion-tiendas §10, retencion-liveops]. De ahí que el F2P móvil cablee remote config antes del launch: el evento semanal no puede depender de un review.
- **Cadencia móvil típica**:
  - F2P/live: builds cada 2-6 semanas (contenido, features), eventos entre medias por remote config.
  - Premium/casual sin liveops: updates por bugs y por el **target API anual** de Play (subir `targetSdkVersion` al retomar cualquier juego dormido, o deja de ser instalable en devices nuevos).
- **Rollout controlado en cada update** — usarlo SIEMPRE en un juego con tracción:
  - **Play staged rollout**: liberar al 1/5/10/…% configurable; **halt rollout** si Android vitals detecta un pico de crashes → frena antes de llegar al 100%.
  - **Apple phased release**: 7 días automáticos (1/2/5/10/20/50/100%), pausable hasta 30 días, "Release to All" para forzar; el usuario que actualiza a mano recibe la versión igual (verificado, Apple).
- **Publicación coordinada (timed/managed release)**: ambas tiendas permiten aprobar el build y **retener la publicación** hasta que TÚ le das al botón (Apple: "Manually release this version"; Play: **Managed publishing**). Imprescindible para coordinar el launch iOS+Android el mismo día, o para alinear con un trailer/press embargo — no dejar que Apple publique automáticamente al aprobar mientras Play sigue en review.
- **Version code / build number** sube en cada subida y nunca se repite [ver: unity/build-plataformas].

## 8. ASO en el release — qué se congela y qué se itera

El ASO profundo (keywords, iconos, mercado) está en [ver: mercado-movil]. Ángulo del momento-release:

- **Se congela al publicar** (no se cambia sin dolor o nunca): **Bundle ID / package name** (inmutable tras publicar), el primer nombre de app, el país de la cuenta.
- **Se itera después con herramientas nativas de tienda**:
  - **Play**: **Store Listing Experiments** (A/B nativo de icono/screenshots/descripción con reparto de tráfico) y **custom store listings** por país/segmento.
  - **Apple**: **Product Page Optimization** (A/B de hasta 3 tratamientos de icono/screenshots/preview) y **Custom Product Pages** (hasta 35 variantes con URL propia para campañas de UA).
- Regla móvil: las **2 primeras screenshots** y el **icono** cargan casi toda la conversión de la ficha; entran al submit pero se A/B-testean vivo — no obsesionarse con "la perfecta" el día 1, sí tener algo decente y experimentos listos [ver: mercado-movil].

## 9. Device matrix testing — antes del submit

El presupuesto de rendimiento por gama está en [ver: unity-movil-rendimiento]; aquí, la matriz mínima de release:

- **Android (fragmentación real)**: probar en **gama baja** (2-3 GB RAM, GPU Mali/Adreno vieja), gama media y alta; varios **aspect ratios** (notch, agujero, plegables). El **pre-launch report** de Play cubre una pasada automática; complementar con Firebase Test Lab o devices físicos para el core loop.
- **iOS (menos devices, más control)**: el **más viejo soportado** (tu `Target minimum iOS Version`), el más chico (SE) y el más grande (Pro Max/iPad si aplica). El reviewer suele probar en algo modesto — si crashea ahí, es rechazo 2.1.
- **Safe areas y aspect ratios**: notch/isla dinámica, esquinas redondeadas, plegables y tablets — verificar que HUD y botones no queden bajo el notch ni fuera de pantalla en 20:9 o en plegable abierto [ver: diseno-movil].
- Verificar en **device real**, no solo simulador/editor: stripping IL2CPP, permisos, memoria y térmica solo se ven en hardware [ver: unity/build-plataformas].
- Regla de prioridad: probar primero el **device más flojo que dices soportar** (el que fija tu `minSdkVersion`/`Target minimum iOS Version`) — ahí revientan memoria, térmica y stripping, y ahí prueba el reviewer.

## 10. Monitoreo post-launch (día 0-7)

El release no termina al pulsar "publicar" — las primeras 48-72h deciden si el rollout sigue o se frena. Tener el tablero listo ANTES de publicar:

- **Crash reporting cableado desde el día 1** (Firebase Crashlytics, Unity Cloud Diagnostics o equivalente) — con símbolos/dSYM subidos (§2, §3) para stacks legibles. Un crash nuevo en un device específico se ve aquí antes que en las reseñas.
- **Vitals / crash-free users** por device y OS: si un modelo concreto crashea, **halt** del staged rollout (Play) o pausa del phased release (Apple) antes de llegar al 100%.
- **Funnel del día 0** (instalación → FTUE → primera sesión → D1) contra el soft launch: una caída aquí suele ser un bug de build de producción (config remota mal, endpoint de prod caído) [ver: diseno-movil].
- **Primeras reseñas y rating**: el rating inicial pesa mucho en ASO; responder crashes reportados rápido. Un update de hotfix entra por el mismo review (Apple ~24h) — por eso el staged rollout compra tiempo.
- **Métricas de negocio en vivo** (ARPDAU, conversión, retención D1) vs lo proyectado en soft launch; divergencia grande = revisar UA/mercado o un problema de build [ver: monetizacion-movil, mercado-movil].
- Regla móvil: **no escalar el gasto de UA** hasta ver crash-free estable y D1 en el rango del soft launch — el pico de tráfico revela crashes que el beta no vio.

## Reglas practicas

- [ ] Cuenta de Play creada semanas antes: closed test 12 testers × 14 días continuos es el critical path del calendario [ver: pipeline/publicacion-tiendas].
- [ ] Android release = IL2CPP + ARM64 + **AAB**; subir **símbolos de debug nativos** (`symbols.zip`) con cada AAB para crashes legibles.
- [ ] Target API al requisito del año (API 36 desde 31-ago-2026); subirlo es lo primero al retomar un juego dormido.
- [ ] Revisar el **pre-launch report** de Play antes de promover a producción; vigilar Android vitals (crash/ANR) — afectan ranking, no solo reseñas.
- [ ] iOS: conservar **dSYM** para simbolizar crashes IL2CPP; `ITSAppUsesNonExemptEncryption=false` si solo hay HTTPS.
- [ ] TestFlight: interno (100, sin review) para iterar; externo (10 000, Beta App Review) para beta pública; builds expiran a 90 días.
- [ ] Adjuntar los **IAP** al binario y probarlos en sandbox (StoreKit/Play Billing) — si el reviewer no los ve, es rechazo 2.1.
- [ ] Sign in with Apple si hay login social; borrado de cuenta in-app si hay cuentas; restore de compras visible.
- [ ] Notificaciones locales: notification channel (Android 8+), permiso `POST_NOTIFICATIONS` (Android 13+), autorización iOS — o no salen.
- [ ] App Privacy / Data Safety declarando lo que hacen los SDKs (ads/analytics/attribution), con las guías del vendor; ATT + UMP cableados a toda la red de ads.
- [ ] Presupuesto de descarga: apuntar el primer download bajo el umbral OTA de datos (~200 MB iOS, verificar); diferir contenido con PAD / ODR / Addressables.
- [ ] Soft launch en mercado de prueba (Canadá/AU/NZ para señal trasladable; CPI barato para volumen) antes del global; medir D1/D7/D30, ARPDAU, CPI, crash-free; escalar solo al cruzar el umbral [ver: mercado-movil].
- [ ] Remote config con defaults locales cableado antes del launch para tunear economía/eventos sin review [ver: pipeline/publicacion-tiendas §10].
- [ ] Cada update pasa review; usar **staged rollout** (Play, con halt) y **phased release** (Apple, 7 días) en todo juego con tracción; version code/build number siempre ↑.
- [ ] Icono + 2 primeras screenshots decentes al submit, con experimentos de ficha (Play Store Listing Experiments / Apple PPO) listos para iterar vivo.
- [ ] Verificar el binario en **device real** (gama baja incluida), no en simulador; el reviewer prueba en hardware modesto.
- [ ] Crash reporting (con símbolos/dSYM) y tablero de vitals listos ANTES de publicar; monitorear día 0-7 y no escalar UA hasta crash-free estable.
- [ ] Publicación coordinada iOS+Android con timed/managed release; no dejar que Apple publique solo al aprobar mientras Play sigue en review.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Crashes de producción ilegibles (stack ofuscado) | Faltaron los símbolos: subir `symbols.zip` (Android) y conservar dSYM (iOS) con cada release |
| Rechazo 2.1 por crash que "en mi teléfono no pasa" | El reviewer usa un device modesto/viejo; probar la device matrix real, no solo el simulador o tu flagship |
| IAP invisibles para el reviewer | Adjuntar los productos IAP al binario en "Ready to Submit" y probar en sandbox antes de enviar |
| Notificaciones locales que nunca aparecen (Android 13+) | Falta el permiso `POST_NOTIFICATIONS` en runtime y/o el notification channel |
| Login social sin Sign in with Apple | Guideline 4.8: añadir Sign in with Apple o quitar el social login |
| Data safety / App Privacy "no recolecta" con ads+analytics dentro | Los SDKs transmiten identifiers; declararlo con la guía del vendor o es removal/updates bloqueados |
| Juego de 300 MB que "no descarga" en celular | Umbral OTA de datos (~200 MB iOS): diferir assets con PAD/ODR/Addressables y bajar el download inicial |
| Escalar UA global desde el día 1 sin soft launch | Sin señal de retención/LTV se quema presupuesto; soft launch en mercado barato, escalar al cruzar umbrales [ver: mercado-movil] |
| Update al 100% de golpe que introduce un crash masivo | Staged rollout (Play, con halt) / phased release (Apple, 7 días): el crash se ve en el 1-5% y se frena |
| Balancear economía a punta de builds con review | Remote config con defaults locales: el ajuste de números deja de pagar review [ver: pipeline/publicacion-tiendas §10] |
| Retomar un juego dormido y subir un update que Play rechaza | Target API caducó; subir `targetSdkVersion` al requisito del año ANTES de tocar nada más |
| TestFlight externo que "no llega" a los testers | Requiere Beta App Review; y los builds expiran a 90 días — subir uno nuevo |
| Obsesionarse con el icono/screenshot "perfecto" el día 1 | Entran al submit pero se A/B-testean vivo (Play Experiments / Apple PPO): shippear algo decente y experimentar |
| Publicar y descubrir el crash masivo por las reseñas de 1 estrella | Crash reporting con símbolos desde el día 1 + staged/phased rollout: el problema se ve en el 1-5%, no en el rating |
| Apple aprueba y publica solo mientras Play aún está en review | Timed/managed release en ambas: aprobar y retener hasta soltar los dos a la vez |

## Fuentes

**Verificadas esta sesión (2026-07-20):**
- Maximum build file sizes — developer.apple.com/help/app-store-connect — iOS app uncompressed ≤ 4 GB, ejecutable ≤ 80 MB (iOS 9+).
- Release a version update in phases — developer.apple.com/help/app-store-connect — phased release 7 días (1/2/5/10/20/50/100%), pausa hasta 30 días, update manual siempre disponible, un solo review.
- About Android App Bundles — developer.android.com/guide/app-bundle — descarga comprimida (base + config, o feature module on-demand) ≤ 4 GB; asset packs con límites propios.
- Play Asset Delivery — developer.android.com/guide/app-bundle/asset-delivery — modos install-time / fast-follow / on-demand; límites por pack en `answer/9859372#size_limits` (no legible en esta pasada — verificar los MB/GB).
- Mobile Notifications package (com.unity.mobile.notifications 2.3.2) — docs.unity3d.com — notificaciones locales iOS/Android, notification channels (Android 8+), autorización iOS, requiere Android SDK 33+ / iOS 15.2+.
- In-App Purchasing (com.unity.purchasing 5.0.4) — docs.unity3d.com — IAP multi-tienda (versión de paquete verificada; detalles de Billing Library / StoreKit no legibles en la página — verificar).
- Target API level requirements — developer.android.com/google/play/requirements/target-sdk — API 36 (Android 16) para apps nuevas y updates desde 31-ago-2026, extensión pedible hasta 1-nov-2026.
- Google Play Billing Library deprecation FAQ — developer.android.com/google/play/billing/deprecation-faq — **v8 mínimo obligatorio desde 31-ago-2026** (extensión a 1-nov-2026); v9 con deadline 31-ago-2028.
- Android vitals thresholds — support.google.com/googleplay/android-developer (Play Console Help) — crash rate percibido ≥1.09%, ANR rate percibido ≥0.47% (global), ≥8% por device concreto.
- TestFlight overview — developer.apple.com/testflight/ — 100 testers internos, 10 000 externos, hasta 100 builds compartidos, 30 devices por tester.

**Cross-referenciadas de las bases hermanas (sus fuentes viven allí):**
- [ver: unity/build-plataformas] — AAB/keystore/IL2CPP/stripping, target API 36, Xcode 26/iOS 26 (28-abr-2026), símbolos, reducción de tamaño.
- [ver: pipeline/publicacion-tiendas] — cuentas, tracks de Play (12 testers × 14 días), review de Apple (90% <24h, 2.1 = 40%+), IARC, Data safety, App Privacy, ATT/UMP, remote config, fees.
- [ver: mercado-movil] — benchmarks de CPI/retención/ARPDAU por género (con fuente real), ASO/keywords profundo.
- [ver: monetizacion-movil] — IAP/ads/consentimiento técnico, odds de loot boxes, restore, ecuación LTV/CPI.
- [ver: retencion-liveops] — qué notificar y la cadencia sana de eventos; liveops.
- [ver: unity-movil-rendimiento] — presupuesto de memoria/descarga y device matrix por gama.
- [ver: unity-movil-graficos] — compresión de textura (ASTC) por plataforma.
- [ver: diseno-movil] — FTUE/onboarding cuyo funnel se mide en soft launch.

**Pendientes de verificación (marcados en el texto):**
- Tope OTA de datos celulares de Apple (histórico 100→150→200 MB; valor vigente 2026 no verificado — página de Apple sobre reducción de tamaño de app no expone el número via WebFetch esta sesión, y el WebSearch de la sesión estaba agotado).
- Límites exactos por pack de Play Asset Delivery (answer/9859372#size_limits, SPA no legible por WebFetch esta sesión tampoco).
