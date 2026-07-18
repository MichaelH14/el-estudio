# Builds y plataformas

> **Cuando cargar este archivo:** al preparar un build para cualquier plataforma (Android, iOS, Web, desktop/Steam), configurar Player Settings o firma, reducir el tamaño del build, o automatizar builds por línea de comandos / CI.

## Build Profiles (Unity 6) y Player Settings base

Unity 6 reemplaza la ventana Build Settings por **Build Profiles** (`File > Build Profiles`). Cada perfil es un **asset versionable** (va a git) con overrides propios: lista de escenas, scripting defines y overrides de Player Settings por perfil. Se puede tener varios perfiles por plataforma (p. ej. `Android-Dev` y `Android-Release`). "Switch Profile" activa el perfil; algunos toggles (Development Build) son compartidos por plataforma.

Settings que SIEMPRE hay que revisar antes del primer build serio:

| Setting | Dónde (Project Settings > Player) | Qué poner |
|---|---|---|
| Company Name / Product Name | Cabecera | Definen el bundle ID por defecto y la ruta de `persistentDataPath` |
| Version + Bundle Version Code (Android) / Build (iOS) | Other Settings > Identification | Incrementar en CADA subida a tienda; Play rechaza `versionCode` repetido |
| Bundle Identifier | Other Settings > Identification | `com.empresa.juego` — inmutable una vez publicado |
| Scripting Backend | Other Settings > Configuration | IL2CPP para releases de tienda (obligatorio en iOS/Web/Android ARM64) |
| Managed Stripping Level | Other Settings > Optimization | Minimal de arranque (default de IL2CPP); subir solo con pruebas (ver sección stripping) |
| Color Space | Other Settings > Rendering | Linear (default con URP) [ver: rendering-urp] |
| Graphics APIs | Other Settings > Rendering | Auto, o lista explícita por plataforma (ver secciones) |
| Default Orientation | Resolution and Presentation | Fijarla en móvil (Portrait o Landscape, no Auto si el juego no lo soporta) |
| Active Input Handling | Other Settings > Configuration | Input System (New) [ver: input-system] |
| Icons + Splash | Icon / Splash Image | Obligatorios para tiendas; el splash de Unity es removible según licencia |

Regla: **Development Build es para probar** (Profiler, logs); nunca dejarlo activado en el build que se sube a tienda.

## Android

### Formato: AAB vs APK
- Unity construye **APK por defecto**; **Google Play solo acepta AAB** (Android App Bundle) para publicar. Activar `Build App Bundle (Google Play)` en el Build Profile, o `EditorUserBuildSettings.buildAppBundle = true` por script.
- APK sigue siendo el formato para: sideload en dispositivo de prueba, itch.io, tiendas alternativas. Flujo típico: APK para iterar, AAB para subir.

### Arquitecturas y backend
- Docs oficiales (Unity 6): ARM64 "is enabled only when you set Scripting Backend to IL2CPP". **Mono no puede producir ARM64**.
- Google Play **exige soporte 64-bit** (arm64-v8a) para todo código nativo — y un build de Unity siempre lleva código nativo.
- Config de release estándar: **IL2CPP + ARM64** (ARMv7 opcional para dispositivos viejos; AAB entrega a cada dispositivo solo su arquitectura). `Split APKs by Target Architecture` solo aplica si distribuyes APKs.

### Target API level (requisito de Google Play a 2026)
- Unity 6 soporta **mínimo API 23** (Android 6.0) y permite target hasta API 35/36.
- Requisito vigente de Play (jul 2026): apps nuevas y updates deben apuntar a **API 35**. Desde el **31-ago-2026**: **API 36** (Android 16) para apps nuevas y updates (Wear OS/Automotive: 35; TV/XR: 34). Extensión solicitable hasta el 1-nov-2026. Apps existentes deben apuntar ≥35 para seguir visibles a usuarios nuevos.
- En Unity: `Target API Level = Automatic (highest installed)` suele bastar si el SDK instalado está al día; si Play rechaza por target antiguo, fijarlo explícito.

### Keystore y firma
- Sin keystore custom Unity firma con **debug key**: sirve para el dispositivo, NO para publicar. Crear keystore en `Player Settings > Publishing Settings` (o `keytool`).
- Unity **no guarda las contraseñas en disco**: hay que reintroducirlas tras reiniciar el Editor (o setearlas por script en CI: `PlayerSettings.Android.keystoreName/keystorePass/keyaliasName/keyaliasPass`).
- **Perder la keystore de upload = problema serio.** Usar Play App Signing (Google custodia la clave de firma final; la de upload se puede resetear con soporte) y aun así guardar backup de la keystore + contraseñas fuera del repo. La keystore JAMÁS se commitea.

### Permisos
- Unity genera el `AndroidManifest.xml` y **añade permisos automáticamente** según las APIs usadas (p. ej. `Microphone` → RECORD_AUDIO). `Internet Access: Require` fuerza INTERNET; `Auto` lo añade solo si hace falta.
- Permisos extra: `Assets/Plugins/Android/AndroidManifest.xml` custom.
- Permisos "peligrosos" requieren además petición en runtime (API ≥23):

```csharp
using UnityEngine.Android;

if (!Permission.HasUserAuthorizedPermission(Permission.Camera))
{
    var callbacks = new PermissionCallbacks();
    callbacks.PermissionGranted += _ => InitCamera();
    callbacks.PermissionDenied += _ => ShowFallbackUI();
    Permission.RequestUserPermission(Permission.Camera, callbacks);
}
```

### Resto de settings Android
- **Graphics APIs**: Vulkan + OpenGL ES 3.x (GLES ≤2.0 ya no está soportado en Unity 6). Dejar ambos salvo razón concreta.
- **Texture compression**: ASTC para dispositivos modernos; ETC2 como fallback de compatibilidad. [ver: assets-pipeline-git]
- **Minify (R8/ProGuard)**: opcional; si se activa y hay plugins Java/Kotlin, puede requerir reglas proguard custom.
- `Filter Touches When Obscured`: anti-tapjacking, activarlo en apps con dinero/compras.

## iOS

### Flujo
1. Unity **genera un proyecto Xcode** (no un .ipa directo). 2. Xcode compila, firma y sube. Solo se puede en **macOS**.
2. Al rebuildar sobre la misma carpeta: **Append** conserva cambios manuales del proyecto Xcode (subdirectorio `classes`); **Replace** regenera todo. Si modificaste el proyecto Xcode a mano, usa Append o automatiza los cambios con `[PostProcessBuild]`.

### Player Settings mínimos
- **Bundle Identifier** (debe coincidir con el App ID registrado), **Signing Team ID** + `Automatically Sign`, **Target minimum iOS Version**, y **todas las usage descriptions** que apliquen (Camera Usage Description, Microphone Usage Description, etc.). Acceder a cámara/micrófono sin su string = crash inmediato en runtime y rechazo en review.
- iOS es **IL2CPP únicamente** (Apple prohíbe JIT). No hay opción Mono.

### Firma y provisioning
- Requiere cuenta del **Apple Developer Program** (99 USD/año) para dispositivo real y App Store.
- Con `Automatically manage signing` en Xcode, los certificados y provisioning profiles se gestionan solos (lo normal para un equipo pequeño). Manual solo si hay CI con certificados exportados o entitlements raros.

### TestFlight y App Store
- Flujo: Xcode > Product > Archive → Organizer → Distribute App → App Store Connect. El build procesa y aparece en TestFlight.
- TestFlight: testers **internos** (hasta 100, sin review, inmediato) y **externos** (hasta 10 000, requiere Beta App Review).
- Requisito vigente (oficial Apple): desde el **28-abr-2026** todo upload a App Store Connect debe compilarse con **Xcode 26 / SDK de iOS 26**. Traducción práctica: mantener Xcode actualizado en la máquina de build; Unity 6.x genera proyectos compatibles.
- Apple exige **privacy manifests** (`PrivacyInfo.xcprivacy`) para APIs "required reason" desde 2024; las versiones recientes de Unity incluyen el suyo, pero los SDKs de terceros (ads, analytics) deben traer el propio — auditarlos antes de subir (los detalles finos: NO VERIFICADO en esta sesión, confirmar en docs de Apple/Unity al momento de subir).
- Para la ficha: capturas por tamaño de pantalla, App Privacy (qué datos recolectas), y la pregunta de export compliance (`ITSAppUsesNonExemptEncryption = false` si solo usas HTTPS estándar la exime).

## IL2CPP vs Mono y managed stripping

| | Mono | IL2CPP |
|---|---|---|
| Compilación | JIT en runtime | AOT: IL → C++ → binario nativo |
| Disponible en | Standalone Win/macOS/Linux, Android (solo ARMv7) | Todas las plataformas |
| Obligatorio en | — | iOS, Web, Android ARM64, consolas |
| Tiempo de build | Rápido (ideal para iterar) | Lento (compila C++) |
| Rendimiento runtime | Bueno | Generalmente mejor |
| Stripping | Puede desactivarse (Disabled) | Siempre activo (mínimo Minimal) |
| Limitaciones | — | Sin `Reflection.Emit` ni codegen dinámico (AOT) |

- Opciones IL2CPP en el Build Profile: **IL2CPP Code Generation** (`Faster runtime` vs `Faster (smaller) builds` — la segunda usa genéricos compartidos: build más pequeño y rápido de compilar, runtime algo más lento) y **C++ Compiler Configuration** (Debug/Release/Master; Master para el build de tienda, compila más lento pero optimiza más).
- **Strip Engine Code** (IL2CPP): elimina módulos nativos de Unity no usados. Activado reduce bastante; si algo se carga solo por reflection/AssetBundle puede necesitar preservación.
- Unity 6.2+ tendría cross-compiler de Linux IL2CPP (compilar el player Linux desde Windows/macOS sin editor Linux, útil para servidores dedicados) — **NO VERIFICADO** en esta sesión (no se pudo confirmar contra docs.unity3d.com; verificar en el Manual de la versión exacta antes de depender de esto).

### Managed stripping y link.xml
El Unity linker hace **análisis estático** del código en build time y elimina lo que no ve referenciado. Todo lo que se alcanza **solo por reflection** (serializadores JSON, DI containers, `Type.GetType(string)`, event handlers por nombre) es invisible para el análisis → se strippea → rompe **solo en el build**, no en el Editor.

- Niveles (`Managed Stripping Level`), verificado en Unity Manual 6.2: **Disabled** (solo disponible con Mono; no elimina nada) → **Minimal** (default de IL2CPP; solo busca código no usado en UnityEngine y librerías .NET, preserva todo el código propio — la menos propensa a romper algo) → **Low** (marcado para deprecación futura en la doc oficial: evitar en proyectos nuevos) → **Medium** (busca parcialmente en todos los assemblies, más riesgo de comportamiento inesperado) → **High** (búsqueda extensiva de todos los assemblies, prioriza tamaño sobre estabilidad; requiere `[Preserve]`/link.xml probados a fondo). Default: Mono = Disabled, IL2CPP = Minimal. A más nivel, menos peso y más riesgo. Subir de nivel solo probando el build real después.
- Síntomas de stripping roto: `MissingMethodException` / `TypeLoadException` / JSON que deserializa a objetos vacíos o null, exclusivamente en device/build IL2CPP.
- Antídotos: atributo `[UnityEngine.Scripting.Preserve]` sobre tipos/miembros propios, o `link.xml` en `Assets/` (aplica a cualquier assembly, incluidos de terceros):

```xml
<linker>
  <!-- Assembly completo (típico: serializadores) -->
  <assembly fullname="Newtonsoft.Json" preserve="all"/>
  <!-- Solo tipos concretos del propio juego -->
  <assembly fullname="MiJuego.Core">
    <type fullname="MiJuego.Core.SaveData" preserve="all"/>
  </assembly>
</linker>
```

Valores de `preserve`: `all`, `fields`, `methods`, `nothing` (solo la declaración). Puede haber varios link.xml (uno por paquete/feature).

## Web (WebGL)

### Límites reales (docs oficiales Unity 6)
| Área | Límite |
|---|---|
| Threads C# | `System.Threading` NO funciona (WASM). El threading nativo C/C++ es experimental y exige headers COOP/COEP/CORP |
| Red | Sin sockets/`System.Net`; solo `UnityWebRequest` y WebSockets (via plugin JS). Sin ping/ICMP |
| Reflection | Sin `Reflection.Emit` (es AOT/IL2CPP) |
| Audio | Solo funcionalidad básica vía Web Audio API; y los browsers bloquean audio hasta el primer gesto del usuario → arrancar/resumir audio tras el primer input [ver: audio-unity] |
| Gráficos | WebGL 2 requerido (browser 64-bit con WASM). WebGPU existe en Unity 6.x como soporte experimental — verificar estado en la versión concreta antes de depender de él |
| Móvil | Soporte OFICIAL desde Unity 6: Safari iOS 15+ y Chrome Android. Sigue siendo el escenario más frágil (memoria) |
| Física | Resultados pueden divergir de otras plataformas (precisión float de WASM) [ver: fisica-unity] |
| Debug | Sin debugger de Visual Studio; instrumentar con logs |

### Memoria
- El heap WASM es un bloque **contiguo** que crece en runtime, hasta 4 GB según `Maximum Memory Size` (Player Settings > Web). Si el browser no puede alocar el bloque al crecer → crash. Menos heap = más estable.
- En **móvil**: configurar `Initial Memory Size` al uso típico real de la app (medirlo con el Profiler) en vez de depender del growth. Presupuesto de memoria móvil: agresivamente bajo.
- `Data Caching` (IndexedDB) evita re-descargar `.data` en visitas siguientes.

### Compresión y hosting
- `Player Settings > Web > Publishing Settings > Compression Format`:
  - **Gzip** (default): builds más grandes que Brotli pero compatible con todo (HTTP y HTTPS).
  - **Brotli**: mejor ratio, build más lento; Chrome/Firefox solo lo descomprimen nativo sobre **HTTPS**.
- El server debe mandar `Content-Encoding: gzip` (.gz) o `br` (.br). Si NO controlas los headers del hosting → activar **Decompression Fallback** (descomprime en JS; loader más pesado y carga más lenta, pero funciona en cualquier server).
- Servir `.wasm` con `Content-Type: application/wasm` habilita streaming compilation (compila mientras descarga: mejora notable de carga).
- **itch.io**: subir ZIP con `index.html` en la raíz. Límites: 500 MB descomprimido, 200 MB por archivo, 1000 archivos, paths ≤240 chars, case-sensitive, rutas relativas. Su CDN aplica gzip automático y sirve `.br` con headers correctos → los builds Unity Gzip/Brotli funcionan. Marcar "Mobile Friendly" solo si de verdad corre en móvil. Subidas automatizadas: CLI `butler push`.

## Desktop y Steam

- Standalone (Win/macOS/Linux): Mono para iterar, IL2CPP + `C++ Compiler Configuration: Master` para release. Arquitectura x64 (+ Apple Silicon/Universal en macOS). macOS fuera del App Store requiere firma + **notarización** de Apple para no asustar a Gatekeeper.
- **Steamworks.NET** (wrapper C# estándar del SDK): instalar por UPM con git URL (`https://github.com/rlabrecque/Steamworks.NET.git?path=/com.rlabrecque.steamworks.net`). Coloca `steam_appid.txt` (tu AppId, UTF-8 sin BOM) en la raíz del proyecto para poder probar desde el Editor. Usar el `SteamManager` de ejemplo como bootstrap de `SteamAPI.Init()`.
- Subida a Steam: **SteamPipe** con `steamcmd +login <user> +run_app_build <ruta>/app_build_<appid>.vdf +quit` — el .vdf define depots y la carpeta del build. Se configura una vez y queda scriptable.
- **Steam Deck** como target (recomendaciones oficiales de Valve):
  - Pantalla 1280×800 (16:10): probar UI y **legibilidad de texto** a ese tamaño físico [ver: gamedev/ux-ui-onboarding].
  - **Controller-first**: la config default de mando debe dar acceso a TODO el juego; soporte nativo de gamepad o Steam Input; teclado en pantalla automático para inputs de texto.
  - **Vulkan** recomendado como API gráfica (rendimiento y batería).
  - Singleplayer jugable **offline**; Steam Cloud para saves; no sincronizar settings gráficos entre máquinas; evitar launchers de terceros.
  - No hace falta build Linux nativo: los builds de Windows corren bajo **Proton** y así es como la mayoría de juegos Unity obtienen Deck Verified. Aun así, probar en hardware real o pedir el review de compatibilidad de Valve (categorías: Verified / Playable / Unsupported).

## Tamaño de build: auditar y reducir

1. **Medir antes de optimizar.** Tras cada build, el **Editor Log** (Console > menú ⋮ > Open Editor Log) incluye el build report: assets por tipo ordenados por peso. Programático: `BuildPipeline.BuildPlayer` devuelve `BuildReport` (`report.summary.totalSize`, módulos, pasos). El paquete **Build Report Inspector** da vista de UI.
2. Lo que domina casi siempre: **texturas**, luego audio y animaciones. Código, escenas y shaders pesan poco.
3. Técnicas en orden de retorno:
   - Texturas: compresión por plataforma (ASTC móvil) y **Max Size** honesto por asset — la mayoría no necesita 2048. El formato fuente (.psd vs .png) NO afecta: Unity re-encodea todo. [ver: assets-pipeline-git]
   - Audio: Vorbis comprimido, Force To Mono para SFX, no todo necesita 44.1 kHz.
   - **Carpeta `Resources/`**: TODO lo que esté ahí entra al build, usado o no. Auditarla siempre; preferir Addressables/referencias directas.
   - Managed Stripping Level más alto (con pruebas + link.xml).
   - Mesh Compression y compresión de AnimationClips.
   - `Api Compatibility Level: .NET Standard 2.1` (subset más chico que .NET Framework).
   - IL2CPP: `Faster (smaller) builds` + Strip Engine Code.

## Builds por línea de comandos y CI

Flags clave (docs oficiales Unity 6):

| Flag | Función |
|---|---|
| `-batchmode` | Sin interacción humana (obligatorio en CI) |
| `-quit` | Salir al terminar |
| `-nographics` | Sin device gráfico (headless; no puede bakear lightmaps) |
| `-projectPath <ruta>` | Proyecto a abrir |
| `-executeMethod <Clase.Metodo>` | Ejecuta un método estático (el build script) |
| `-logFile <ruta>` | Log a archivo (imprescindible para depurar CI) |
| `-buildTarget <android\|ios\|win64\|linux64\|webgl>` | Plataforma activa |
| `-activeBuildProfile <ruta.asset>` | Unity 6: activa un Build Profile |
| `-build <ruta>` | Unity 6: construye el player con el perfil activo, sin C# custom |
| `-accept-apiupdate` | Permite correr el API Updater en batchmode |

```csharp
// Assets/Editor/CIBuild.cs
using UnityEditor;
using UnityEditor.Build.Reporting;

public static class CIBuild
{
    public static void BuildAndroid()
    {
        EditorUserBuildSettings.buildAppBundle = true; // AAB para Play
        var opts = new BuildPlayerOptions
        {
            scenes = new[] { "Assets/Scenes/Main.unity" },
            locationPathName = "Builds/Android/juego.aab",
            target = BuildTarget.Android,
            options = BuildOptions.None
        };
        BuildReport report = BuildPipeline.BuildPlayer(opts);
        if (report.summary.result != BuildResult.Succeeded)
            EditorApplication.Exit(1); // el job de CI debe fallar
    }
}
```

```bash
Unity -batchmode -nographics -quit -projectPath /ruta/proyecto \
  -buildTarget Android -executeMethod CIBuild.BuildAndroid -logFile build.log

# Unity 6, vía Build Profile (sin C# custom):
Unity -batchmode -quit -projectPath /ruta/proyecto \
  -activeBuildProfile "Assets/Settings/Build Profiles/Android.asset" \
  -build "Builds/Android/juego.aab" -logFile build.log
```

Nociones de CI para Unity:
- **GameCI** es el estándar open source: imágenes Docker con el Editor + GitHub Actions (`unity-builder`, `unity-test-runner`); también GitLab/CircleCI/self-hosted.
- La CI necesita **activar la licencia de Unity** en la máquina (GameCI trae acciones para el flujo de activación).
- Cachear `Library/` entre jobs: sin cache, cada build reimporta el proyecto entero.
- Usar EXACTAMENTE la misma versión de Unity que el proyecto (el hash está en `ProjectSettings/ProjectVersion.txt`).
- Builds de iOS en CI requieren un runner **macOS** con Xcode (Unity genera el proyecto; `xcodebuild` archiva y sube).
- Correr los tests (EditMode/PlayMode) en el mismo pipeline antes del build. Desde el editor con MCP también se puede lanzar el build (manage_build) para iterar [ver: unity-mcp-flujo].

## Reglas practicas

- [ ] Fijar Bundle Identifier, Company/Product Name y orientación el día 1 — cambiarlos después de publicar no se puede (bundle ID) o duele.
- [ ] Probar un build IL2CPP en dispositivo real TEMPRANO (semana 1-2), no la semana del lanzamiento: stripping, permisos, rendimiento y memoria solo se ven ahí.
- [ ] Android release = IL2CPP + ARM64 + AAB; APK solo para sideload/itch.
- [ ] Target API Level según el requisito vigente de Play: API 35 hoy; API 36 desde el 31-ago-2026.
- [ ] Keystore: crearla una vez, backup (archivo + contraseñas) fuera del repo, jamás commitearla; usar Play App Signing.
- [ ] Incrementar Bundle Version Code (Android) / Build number (iOS) en cada subida.
- [ ] iOS: rellenar TODAS las usage descriptions que el juego pueda tocar; sin string = crash + rechazo.
- [ ] iOS: compilar con el Xcode que Apple exige ese año (desde 28-abr-2026: Xcode 26 / SDK iOS 26).
- [ ] Todo lo que se use por reflection (JSON, DI, plugins) → link.xml o `[Preserve]` ANTES de subir el stripping level.
- [ ] Web: Gzip si el hosting es simple, Brotli si controlas HTTPS y headers; Decompression Fallback solo como parche; `Content-Type: application/wasm` siempre.
- [ ] Web móvil: `Initial Memory Size` calibrado con el Profiler, no el default.
- [ ] Auditar el build report (Editor Log / BuildReport) tras cada build gordo; vigilar `Resources/`.
- [ ] Development Build apagado en el build de tienda.
- [ ] Steam: probar a 1280×800, con mando exclusivamente, y offline, antes del review de Deck.
- [ ] CI: misma versión de Unity que `ProjectVersion.txt`, licencia activada, cache de `Library/`, log a archivo, y exit code ≠ 0 si el build falla.
- [ ] Verificar el binario final en la plataforma real (device, browser, Deck), no solo que "el build terminó".

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Funciona en Editor, revienta en device con `MissingMethodException` o JSON vacío | Es stripping. link.xml / `[Preserve]` para lo alcanzado por reflection; bajar stripping level para confirmar el diagnóstico |
| Subir APK a Google Play | Play solo acepta AAB: activar Build App Bundle |
| Play rechaza por "same versionCode" o target API viejo | Incrementar Bundle Version Code; subir Target API Level al requisito del año |
| Keystore perdida u olvidada la contraseña | Prevención única: backup + gestor de contraseñas + Play App Signing. Sin upload key ni Play App Signing no hay update posible |
| Crash iOS al abrir cámara/micrófono | Faltó la Usage Description en Player Settings; añadirla y rebuild |
| Cambios manuales al proyecto Xcode desaparecen | Se buildó con Replace. Usar Append, o automatizar con `[PostProcessBuild]` |
| Web no carga: error de `Content-Encoding` o descarga eterna | Headers del server mal configurados para .gz/.br; configurarlos o activar Decompression Fallback |
| Web sin audio | Autoplay policy del browser: iniciar/resumir el audio tras el primer click/tap |
| Web crashea en móvil con "out of memory" | Heap contiguo no pudo crecer: bajar consumo, fijar Initial Memory Size realista, texturas más chicas |
| Código con `System.Threading` o sockets portado a Web | No existe en WASM: rediseñar con corrutinas/async sobre el main loop y UnityWebRequest/WebSockets |
| "Build and Run" web funciona pero el hosting real no | El server embebido no cachea `.data`/AssetBundles y tapa problemas de headers: probar siempre en un server real |
| Build gigante sin saber por qué | Editor Log build report: casi siempre texturas sin Max Size o una carpeta `Resources/` engordada |
| CI compila pero el juego sale roto (escenas faltantes, defines mal) | El build de CI debe usar el mismo Build Profile que el build local, no una lista de escenas hardcodeada divergente |
| Batchmode falla en runner nuevo sin error claro | Licencia sin activar o versión de Unity distinta a `ProjectVersion.txt`; revisar `-logFile` |
| Probar solo Mono en desktop y shippear IL2CPP | El comportamiento AOT difiere (reflection, genéricos): el candidato de release se prueba en IL2CPP |

## Fuentes

- Target API level requirements — Google Play / developer.android.com — deadlines exactos: API 35 vigente, API 36 desde 31-ago-2026.
- Meet Google Play's 64-bit requirement — developer.android.com — obligación de arm64-v8a para código nativo.
- Android build process / Player Settings Android / Requirements and compatibility — Unity Manual 6.2 (docs.unity3d.com) — APK default vs AAB, keystore no persistida, ARM64 solo con IL2CPP, min API 23, Vulkan/GLES3.
- Requesting Android permissions — Unity Manual 6.2 — API `UnityEngine.Android.Permission` (HasUserAuthorizedPermission, RequestUserPermission, PermissionCallbacks).
- iOS build process — Unity Manual 6.2 — generación del proyecto Xcode, Append vs Replace, settings previos.
- Upcoming requirements — Apple Developer News — Xcode 26 / SDK iOS 26 obligatorio para uploads desde 28-abr-2026.
- Managed code stripping + Link XML formatting + Configure managed code stripping — Unity Manual 6.2 — análisis estático del linker, sintaxis exacta de link.xml, valores de `preserve`, y descripción verificada por nivel (Disabled solo Mono, default Mono=Disabled/IL2CPP=Minimal, Low marcado para deprecación).
- Scripting backends (Mono/IL2CPP) — Unity Manual 6.2 — IL2CPP requerido donde no hay JIT; cross-compiler Linux en 6.2.
- Web technical limitations / browser compatibility / memory / deploying — Unity Manual 6.2 — sin threads C#, sin sockets, WebGL2, móvil oficial (Safari 15+/Chrome Android), heap hasta 4 GB, Brotli/Gzip y headers.
- HTML5 games docs — itch.io — límites (500 MB/200 MB/1000 archivos), gzip automático del CDN, soporte `.br`.
- Steam Deck compatibility recommendations — Valve / partner.steamgames.com — controller-first, Vulkan, offline, aspect ratios, review de compatibilidad.
- Steamworks.NET installation — steamworks.github.io — instalación UPM, steam_appid.txt, SteamManager.
- Editor command line arguments — Unity Manual 6.2 — flags exactos incl. `-activeBuildProfile` y `-build` (nuevos de Unity 6).
- BuildPipeline.BuildPlayer — Unity Scripting API 6.2 — firma, BuildPlayerOptions, BuildReport/BuildSummary.
- Reducing the output file size — Unity Manual 6.2 — build report del Editor Log, texturas dominan, trampa de `Resources/`, .NET Standard.
- Build Profiles — Unity Manual 6.2 — perfiles como assets versionables con overrides.
- GameCI docs — game.ci — Docker + GitHub Actions (unity-builder/unity-test-runner), activación de licencia en CI.
