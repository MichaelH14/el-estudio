# Unity 6.x y actualidad (a julio 2026)

> **Cuando cargar este archivo:** al decidir qué versión de Unity/paquetes usar en un proyecto, al evaluar features nuevas del motor (Awaitable, GPU Resident Drawer, Render Graph, ECS), al responder dudas de licencias/costos de Unity, o al justificar la elección de motor. Complementa a [ver: rendering-urp] y [ver: rendimiento-unity].

## Línea de versiones Unity 6: cadencia y LTS

Desde 2024 Unity abandonó el versionado por año (2021.x, 2022.x...). Ahora hay **generación Unity 6** con dos canales:

- **LTS / Supported**: versiones con años de soporte y patches semanales (`6000.X.Yf1`). Para producción.
- **Update / mainline**: releases intermedias (~cada 4 meses) que estrenan features; dejan de recibir soporte cuando sale la siguiente. Para probar features, no para cerrar un juego.

| Versión | Interno | Fecha | Estado a 2026-07 | Titulares |
|---|---|---|---|---|
| **Unity 6.0** | 6000.0 | 17-oct-2024 | LTS, aún con patches (6000.0.71f1+) | GPU Resident Drawer, Render Graph, Build Profiles |
| Unity 6.1 | 6000.1 | 24-abr-2025 | Update, sin soporte ya | Deferred+, DX12 default en Windows, Project Auditor |
| Unity 6.2 | 6000.2 | 14-ago-2025 | Update, sin soporte ya | Unity AI (beta), Mesh LOD, World Space UI |
| **Unity 6.3** | 6000.3 | 4-dic-2025 | **LTS actual — recomendada para producción** (2 años de soporte; 6000.3.12f1+ a mar-2026) | Box2D v3, 3D en el 2D Renderer, paquetes core |
| Unity 6.4 | 6000.4 | 18-mar-2026 | Mainline actual | Canal de features en curso |
| Unity 6.5 | 6000.5 | NO VERIFICADO (fecha exacta de beta/release) | En desarrollo — manual 6000.5 ya publicado en docs.unity3d.com | — |

**Regla de decisión:** proyecto nuevo → **Unity 6.3 LTS** (última LTS). Proyecto ya en 6.0 LTS → quedarse y solo subir de patch (`f` números), migrar a 6.3 solo con motivo concreto. Jamás cerrar producción sobre una mainline (6.4/6.5).

- El número "6000.3" = "Unity 6.3". Los patches (`6000.3.12f1`) son fixes acumulativos, seguros de tomar dentro de la misma minor.
- 6.1 y 6.2 fueron "update releases": sus features acabaron consolidadas en 6.3 LTS.

## Qué trajo cada versión (lo relevante a producción)

### Unity 6.0 (oct-2024) — la base
- **GPU Resident Drawer** y **GPU occlusion culling** (ver sección abajo).
- **Render Graph** como sistema por defecto para passes custom en URP (ver abajo).
- **Adaptive Probe Volumes (APV)** con blending de escenarios de iluminación — sustituto moderno de Light Probe Groups.
- **Build Profiles**: múltiples configuraciones de build por proyecto (dev/release, Android/iOS/PC) sin tocar Player Settings a mano [ver: build-plataformas].
- Multiplayer Center + Multiplayer Widgets; **Netcode for GameObjects 2.0** con Distributed Authority.
- Splash screen de Unity **opcional incluso en Personal** (desde Unity 6).
- Web: WebAssembly 2023; soporte visionOS; Sentis (inferencia ML local); Audio Random Container (playlists aleatorizadas para SFX).

### Unity 6.1 (abr-2025)
- **Deferred+** en URP (cluster-based light culling; con soporte de GPU Resident Drawer, que en 6.0 pedía Forward+).
- **DirectX 12 pasa a ser la API gráfica default en Windows**.
- **GraphicsStateCollection API** (PSO tracing/precompilación): graba los pipeline states en una sesión de juego y los precompila en el arranque → menos shader stutter. Clave en DX12/Vulkan.
- Reducción de variantes de shader compiladas para fog y LOD → builds más rápidas y pequeñas.
- Bicubic lightmap sampling en URP/HDRP; **Project Auditor** (análisis estático de assets/scripts/settings) integrado.
- Android: soporte foldables/pantallas grandes (Resizeable Activity); Vulkan Device Filter.
- Web: **WebGPU experimental** (compute shaders, VFX Graph); Facebook Instant Games.
- Build Profiles: override de graphics y quality settings por perfil.

### Unity 6.2 (ago-2025)
- **Unity AI (beta)**: Assistant (sustituye a Muse Chat; modos /ask, /run, /code) + Generators (sprites, texturas, sonidos, animaciones, materiales) dentro del editor. Durante la beta, "Unity Points" gratis ilimitados; anunciado que pasará a modelo de pago.
- **Mesh LOD**: generación automática de niveles de detalle al importar mallas.
- **World Space UI** en UI Toolkit (UI posicionada en el mundo 3D) [ver: ui-unity].
- Unity Test Framework pasa a paquete core; Android 16 / SDK 36; monitoreo ANR en Android.

### Unity 6.3 (dic-2025) — LTS actual
- **2D físicas de bajo nivel con Box2D v3**: multi-hilo y debugging visual [ver: fisica-unity].
- **3D dentro del 2D Renderer**: Mesh Renderer y Skinned Mesh Renderer en escenas con 2D URP — mezcla sprites + mallas 3D sin doble cámara.
- **GPU Lightmapper es el backend de bakeo por defecto**.
- Render Graph unificado URP/HDRP; **Render Graph Viewer contra dispositivo** (móvil/XR); bloom con filtros Kawase/Dual (más baratos).
- **Shader Build Settings**: recorte de variantes de shader desde un panel central → builds más rápidas.
- Física: se puede **desactivar/strippear el backend de físicas** que no uses → build más pequeña.
- Editor: toolbar customizable, nueva ventana Hierarchy (preview), Search con índice LMDB (más rápido), pipeline de audio scriptable con procesadores C# + Burst.
- Package Manager: **verificación de firma de paquetes** y `pinnedPackages` (fijar versiones) — relevante para reproducibilidad [ver: assets-pipeline-git].
- Android: **mínimo API level 25** (Android 7.1); Gradle 9.1 / AGP 9.0; HTTP/2 default en UnityWebRequest.
- Web: builds Apple Silicon nativas (sin Rosetta), IL2CPP con metadata compacta → builds web más pequeñas.
- UI Toolkit: filtros USS (blur, grayscale...), Vector Graphics como módulo core, UI Test Framework, soporte Shader Graph para UI.
- Accesibilidad nativa: Narrator (Windows) y VoiceOver (macOS).
- Platform Toolkit unificado (cuentas, saves, achievements multiplataforma) — reporte de GameFromScratch; detalle de API NO VERIFICADO en docs.

### Unity 6.4+ (2026, mainline)
Canal continuo de features; a jul-2026 producción se queda en 6.3 LTS. No se investigó el detalle de 6.4 — verificar su What's New si hiciera falta.

## Awaitable: async nativo del motor

`UnityEngine.Awaitable` es el tipo async oficial del motor (introducido en la línea 2023, estándar en todo Unity 6). Sustituye a coroutines para la mayoría de flujos y a `Task` para código de juego:

- **Pooled**: las instancias se reciclan → casi cero GC, más barato que `Task`.
- ⚠️ Consecuencia del pooling: **solo se puede await UNA vez** cada instancia. Nunca guardarla y re-awaitearla.
- Métodos estáticos: `Awaitable.NextFrameAsync()`, `WaitForSecondsAsync()`, `FixedUpdateAsync()`, `EndOfFrameAsync()`, `FromAsyncOperation()`, `BackgroundThreadAsync()` (salta a thread pool), `MainThreadAsync()` (vuelve al main thread).
- Cancelación con `CancellationToken`; `MonoBehaviour.destroyCancellationToken` cancela solo cuando el objeto se destruye (evita el clásico "async que sigue corriendo tras destruir el GameObject").

```csharp
using UnityEngine;

public class Spawner : MonoBehaviour
{
    async Awaitable SpawnWaveAsync(int count)
    {
        for (int i = 0; i < count; i++)
        {
            SpawnOne();
            // destroyCancellationToken: si el objeto muere, el loop muere
            await Awaitable.WaitForSecondsAsync(0.25f, destroyCancellationToken);
        }
        await Awaitable.EndOfFrameAsync(destroyCancellationToken);
    }

    async Awaitable<Mesh> BakeAsync()
    {
        await Awaitable.BackgroundThreadAsync();   // trabajo pesado fuera del main thread
        var data = HeavyCompute();
        await Awaitable.MainThreadAsync();          // la API de Unity solo en main thread
        return BuildMesh(data);
    }
}
```

Criterio: gameplay secuencial (timers, waves, tweens simples) → `Awaitable` o coroutines; I/O y CPU pesado → `Awaitable` con `BackgroundThreadAsync`. UniTask (third-party) sigue siendo válido y popular, pero con Awaitable ya no es imprescindible en proyectos nuevos [ver: csharp-patrones].

## GPU Resident Drawer y GPU occlusion culling (Unity 6.0+)

**GPU Resident Drawer**: usa BatchRendererGroup para dibujar GameObjects con GPU instancing automático → menos draw calls y menos CPU, sin cambiar tu código. Checklist para activarlo (URP):

1. Project Settings > Graphics > Shader Stripping > **BatchRendererGroup Variants = "Keep All"**.
2. URP Asset: **SRP Batcher ON**.
3. URP Asset: **GPU Resident Drawer = "Instanced Drawing"**.
4. Universal Renderer: Rendering Path = **Forward+** (en 6.0; desde 6.1 también Deferred+).
5. **Desactivar Static Batching** (Player Settings) — compite y estorba.

- Solo actúa sobre **MeshRenderer** (no SkinnedMeshRenderer, no particles); lo demás cae al camino normal.
- Requiere compute shaders (no OpenGL ES). En móvil moderno con Vulkan/Metal funciona.
- Rinde en escenas grandes con muchas copias del mismo mesh; en una escena 2D de sprites no aporta (los sprites no son MeshRenderer).
- Se mide en Play mode, no en Scene view. Sube el tiempo de build (más variantes de shader).
- **GPU occlusion culling** (Rendering Debugger para verificarlo): descarta oclusos en GPU; se activa junto al Resident Drawer en el renderer.

## Render Graph en URP (Unity 6.0+)

Render Graph es la API con la que se escriben passes custom en URP desde Unity 6: declaras recursos (texturas, buffers) y el grafo decide allocation, merge de passes y memoria transient (crítico en GPUs móviles tile-based).

- Un pass custom = `ScriptableRenderPass` implementando **`RecordRenderGraph`** (los viejos `Execute`/`OnCameraSetup` con `SetRenderTarget` son el camino legacy).
- **Compatibility Mode** (URP settings) permite correr passes viejos, pero está en vía de deprecación — código nuevo SIEMPRE en Render Graph. Para casos extremos existe la API "unsafe pass".
- Consecuencia práctica: **assets/tutoriales de renderer features pre-Unity-6 suelen no compilar**. Verificar que cualquier asset de la Store diga "Unity 6 / Render Graph compatible".
- En 6.3, URP y HDRP comparten la misma base de Render Graph y hay Render Graph Viewer conectado a dispositivo para depurar en móvil/XR.
- Detalle de escritura de passes: [ver: rendering-urp].

## Tiempos de build e import: qué mejoró de verdad

| Mejora | Versión | Impacto |
|---|---|---|
| Reducción de variantes fog/LOD | 6.1 | Menos shaders compilados → build más corta |
| GraphicsStateCollection (PSO precompile) | 6.1 | Menos stutter en runtime; warmup en carga |
| Mesh LOD en import | 6.2 | LODs sin trabajo manual |
| Shader Build Settings (recorte central de variantes) | 6.3 | La palanca más grande de tiempo de build de shaders |
| Strip de backend de físicas no usado | 6.3 | Build final más pequeña |
| IL2CPP metadata compacta (Web) | 6.3 | Builds web más pequeñas |
| Search con LMDB | 6.3 | Editor más ágil en proyectos grandes |

Regla: la mayor parte del tiempo de build en proyectos URP son **shader variants** — atacar ahí primero (Shader Build Settings en 6.3, strip de keywords) antes de culpar al código.

## ECS / DOTS: qué es y cuándo

**DOTS** = Entities (ECS) + Jobs System + Burst compiler + Collections. ECS separa datos (components puros) de lógica (systems) en memoria contigua → cache-friendly y paralelizable.

Estado a 2026-07:
- Entities llegó a 1.0 en 2023; línea 1.x hasta **1.4.2 (sep-2025)**, último standalone (mínimo editor 2022.3.20f1).
- Desde finales de 2025 **Entities es paquete core embebido en el editor** con versionado alineado (changelog: "core package" desde 6.4.0, oct-2025; versión 6.6.0 a jul-2026). Igual sus satélites: Entities Graphics, Unity Physics, **Netcode for Entities**.
- Producción real: se usa casi siempre el combo Entities + Entities Graphics + Unity Physics, no Entities solo.

| | Veredicto |
|---|---|
| **SÍ ECS** | Decenas de miles de entidades activas (bullet hell masivo, RTS, sims, boids), servidor autoritativo de alta escala (Netcode for Entities), sistemas de simulación aislados dentro de un juego normal |
| **NO ECS** | Juego 2D/3D móvil+PC de equipo chico típico: gameplay normal, UI, menús, cámaras — GameObjects + MonoBehaviour sobran. La curva de aprendizaje, el tooling más áspero y el ecosistema (tutoriales, assets) siguen centrados en GameObjects |
| **Punto medio (el sweet spot del dev chico)** | **Jobs + Burst SIN ECS**: paralelizar un hot path concreto (pathfinding, mesh deformation, spawner masivo) con `IJobParallelFor` + `NativeArray` dentro de un proyecto MonoBehaviour normal. 80% del beneficio, 20% del costo |

Para este stack: default GameObjects; considerar Jobs+Burst cuando el Profiler señale un hot path CPU [ver: rendimiento-unity]; ECS completo solo con un motivo de escala demostrado.

## Paquetes esenciales del registry (estado a 2026-07)

| Paquete | Versión (docs latest) | Estado / notas |
|---|---|---|
| **Input System** (`com.unity.inputsystem`) | 1.19 | El sistema de input default de Unity 6; project-wide Actions (`InputSystem.actions`). El Input Manager viejo es legacy [ver: input-system] |
| **Cinemachine** (`com.unity.cinemachine`) | 3.1.7 en canal 3.1; @latest ya apunta a 6.6 (core, alineado al editor) | CM3: namespace **`Unity.Cinemachine`**, `CinemachineVirtualCamera` → **`CinemachineCamera`**, filtrado por **Channels** (no layers). API incompatible con CM2: scripts se migran a mano; escenas/prefabs con el **Cinemachine Upgrader** (sin undo a nivel proyecto — backup antes). Proyecto viejo estable en CM2 → puede quedarse |
| **Addressables** (`com.unity.addressables`) | 3.1 | Estándar para carga asíncrona de contenido y DLC/remote content; sustituye a Resources/AssetBundles a mano |
| **Netcode for GameObjects** (`com.unity.netcode.gameobjects`) | 2.13 | Multiplayer casual/co-op sobre GameObjects; desde 2.0 (Unity 6) con Distributed Authority |
| **Netcode for Entities** (`com.unity.netcode`) | 6.6 (core-aligned) | Server-authoritative de alta escala; exige comprarse todo el stack ECS |
| **Entities** (`com.unity.entities`) | 6.6.0 (core) | Ver sección ECS |
| **2D** (Sprite Editor, Tilemap, PSD/Aseprite importers) | Integrados/core | 6.1: auto-generación de Tilemaps desde PSD/Aseprite, Tile Set asset; 6.2: 2D Enhancers en Sprite Editor; 6.3: físicas Box2D v3 + meshes 3D en 2D Renderer |
| **Unity Test Framework** | Core desde 6.2 | Play/Edit mode tests sin instalar nada |

Cambio estructural en 6.3+: varios paquetes clave pasaron a ser **core packages embebidos** con versión alineada al editor (confirmado en el changelog de Entities; los redirects @latest de Cinemachine y Netcode for Entities apuntan a 6.6). Efecto práctico: menos matriz de compatibilidad paquete↔editor que vigilar; la versión del editor manda.

## Licencias a 2026 y el Runtime Fee

Historia del Runtime Fee en 4 líneas:
1. **sep-2023**: Unity anuncia cobro por instalación ("Runtime Fee") → rechazo masivo; estudios (Innersloth, Mega Crit) amenazan con migrar de motor.
2. **22-sep-2023**: retrocede a medias (excepciones, tope 2.5% revenue); el CEO John Riccitiello sale en oct-2023.
3. **may-2024**: Matthew Bromberg asume como CEO.
4. **12-sep-2024**: Bromberg **cancela el Runtime Fee por completo**; vuelta al modelo de suscripción por asiento, con subidas de precio anuales como política declarada.

Licencias vigentes (desde 1-ene-2025):

| Tier | Quién debe usarla | Costo |
|---|---|---|
| **Personal** | Ingresos/funding < **$200,000 USD**/año | **Gratis**. Splash screen "Made with Unity" **opcional** desde Unity 6. Todas las features del motor |
| **Pro** | > $200k/año, o publicar en consolas cerradas (PlayStation/Xbox/Switch) | **$2,200 USD/asiento/año** (subida del 8% en ene-2025) |
| **Enterprise** | > $25M/año | Precio custom (subió 25% en 2025) |

Para un equipo chico: **Personal cubre todo** hasta $200k de ingresos anuales — motor completo, sin splash, sin royalties. No hay ningún porcentaje de revenue share en Unity (a diferencia de Unreal).

## Estado de la empresa Unity (2025-2026), lo que afecta a un dev

- La crisis de confianza 2023-2024 quedó atrás en lo contractual (fee cancelado, términos estables), pero dejó marca: el uso de Unity en la Global Game Jam cayó de 61% (2023) a 36% (2024). En 2024 hubo una reestructuración fuerte con recorte de ~25% de plantilla (ampliamente reportado en prensa; no verificado en esta investigación contra fuente primaria).
- **CVE-2025-59489** (parcheado el 2-oct-2025): vulnerabilidad de ejecución de código en el runtime que afectaba builds desde Unity 2017.1 en Android/Windows/macOS/Linux. Obligó a re-publicar juegos con editor parcheado. Lección operativa: **mantenerse en el último patch de tu LTS y poder rebuildear rápido**.
- **Unity AI** (6.2+) está en beta con "Points" gratis; Unity anunció que pasará a pago — no diseñar un pipeline de producción que dependa de esos generators sin plan B de costo.
- Política declarada de **subidas de precio anuales** en Pro/Enterprise: presupuestar el asiento de Pro como costo creciente.
- Negocio de ads/mediación integrado en el editor (LevelPlay en el menú Services desde 6.3) — relevante si el juego monetiza con ads. El rediseño del modelo de ads ("Unity Vector", 2025) es NO VERIFICADO en esta investigación.
- Cadencia de releases 2024-2026 cumplida y regular (6.0→6.5 en 18 meses): el motor está activamente mantenido y la generación 6 es una base estable.

## Unity vs Godot vs Unreal (honesto y corto)

| | Unity 6 | Godot 4.x | Unreal Engine 5 |
|---|---|---|---|
| Costo | Gratis < $200k/año; Pro $2,200/asiento | Gratis, MIT, sin límites | Gratis; **5% royalty** sobre gross > $1M por juego |
| 2D | Muy bueno (Tilemap, Sprite tools, 2D URP, Box2D v3 en 6.3) | Muy bueno, ligero | Flojo — no es su terreno |
| 3D móvil | **Punto más fuerte**: URP escala de gama baja a alta | Correcto, menos maduro en gama baja | Posible pero pesado (builds y runtime grandes) |
| Lenguaje | C# maduro + ecosistema .NET | GDScript (C# de segunda clase; export web con C# aún limitado) | C++ y Blueprints |
| Consolas | Con licencia Pro y proceso establecido | Vía porters externos (W4 Games etc.) | Soporte de primera |
| Ecosistema (assets, tutoriales, hiring, LLM knowledge) | El más grande | Creciendo rápido, aún menor | Grande, sesgado a AAA/3D |
| Riesgo | Empresa cotizada, historial 2023 de cambio de términos (revertido) | Cero riesgo contractual | Royalty + engine pensado para otro perfil |

**Por qué Unity para este stack** (2D/3D móvil+PC, equipo chico): es el único de los tres con primera línea simultánea en 2D **y** 3D **y** móvil; C# con tooling maduro; URP diseñado para escalar en hardware móvil; ecosistema de assets/documentación/respuestas gigante (incluye el conocimiento de los LLM que asisten el desarrollo); y a la escala de un equipo chico la licencia es gratis. Godot sería el plan B razonable para 2D puro; Unreal solo si el proyecto fuera 3D high-end para PC/consola.

## Reglas prácticas

- [ ] Proyecto nuevo → **Unity 6.3 LTS** (6000.3.x, último patch f). Nunca producción en mainline (6.4/6.5) ni en beta.
- [ ] Tomar patches (`6000.3.Xf1`) con regularidad — el caso CVE-2025-59489 demostró que hay que poder rebuildear con editor parcheado.
- [ ] Pipeline: URP siempre para este stack (plantilla Universal 2D o 3D) [ver: rendering-urp].
- [ ] Passes de render custom: SIEMPRE Render Graph (`RecordRenderGraph`); no escribir código nuevo en Compatibility Mode.
- [ ] Assets de la Store que toquen rendering: confirmar compatibilidad "Unity 6 / Render Graph" antes de comprar/instalar.
- [ ] Escena 3D con muchos objetos repetidos → activar GPU Resident Drawer (BRG Variants "Keep All" + SRP Batcher + Forward+/Deferred+ + Static Batching OFF).
- [ ] Async de gameplay → `Awaitable` con `destroyCancellationToken`; nunca await dos veces la misma instancia.
- [ ] Trabajo CPU pesado → primero Jobs + Burst en el hot path medido; ECS completo solo con necesidad de escala real (decenas de miles de entidades).
- [ ] Input nuevo → Input System (1.19) con project-wide Actions; no usar el Input Manager legacy [ver: input-system].
- [ ] Cámaras → Cinemachine 3.x (`Unity.Cinemachine`, `CinemachineCamera`); no seguir tutoriales de CM2 (`CinemachineVirtualCamera`) al pie de la letra.
- [ ] Contenido dinámico/carga asíncrona → Addressables 3.x, no `Resources/`.
- [ ] Multiplayer casual/co-op → Netcode for GameObjects 2.x; competitivo de alta escala → evaluar Netcode for Entities (con todo el costo ECS).
- [ ] Tiempo de build alto → atacar shader variants primero (Shader Build Settings en 6.3, strip de fog/LOD de 6.1).
- [ ] Fijar versiones de paquetes en proyectos serios (`pinnedPackages`, 6.3) y commitear `Packages/manifest.json` + lock [ver: assets-pipeline-git].
- [ ] Android en 6.3: mínimo API 25; revisar Gradle 9.1/AGP 9.0 si hay plugins nativos [ver: build-plataformas].
- [ ] Presupuesto de licencias: Personal gratis hasta $200k/año de ingresos; consolas o >$200k → Pro ($2,200/asiento/año, sube anual).
- [ ] No apoyar el pipeline de producción de assets en Unity AI Generators sin plan de costo (los Points gratis son de la beta).

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Empezar producción en la mainline (6.4/6.5) "porque es la más nueva" y comerse regresiones sin soporte largo | LTS (6.3) para todo lo que vaya a shippear; mainline solo para probar features |
| Copiar un `ScriptableRenderPass` de un tutorial 2021/2022 y que no compile o no dibuje en Unity 6 | Es el cambio a Render Graph: reescribir con `RecordRenderGraph`; buscar la versión Unity 6 del tutorial |
| Activar GPU Resident Drawer y "no hace nada" | Checklist completo: BRG Variants "Keep All" + Forward+/Deferred+ + SRP Batcher ON + Static Batching OFF; solo MeshRenderer; medir en Play mode |
| Guardar un `Awaitable` y awaitearlo dos veces (o desde dos sitios) | Están pooled: un await por instancia. Para difundir un resultado, exponer un evento o `Awaitable`/`Task` nuevo por consumidor |
| Async loop que sigue corriendo tras destruir el GameObject (NullReference en cadena) | Pasar `destroyCancellationToken` a cada `Awaitable.*Async` |
| Instalar Cinemachine 3 sobre un proyecto CM2 y que exploten scripts, timelines y prefabs | Leer la guía de upgrade: namespace y tipos renombrados; usar el Cinemachine Upgrader con backup previo (el upgrade de proyecto entero no tiene undo); o quedarse en CM2 |
| Adoptar ECS "por rendimiento" en un juego que no lo necesita y ahogarse en boilerplate | ECS solo por escala demostrada; el hot path puntual se resuelve con Jobs + Burst dentro de MonoBehaviours |
| Seguir tutoriales viejos con `Input.GetAxis`/Input Manager en un proyecto con Input System activo | El proyecto define el backend en Player Settings (Active Input Handling); escribir contra Input System 1.19 [ver: input-system] |
| Asumir que Unity cobra revenue share como Unreal | No hay royalty: Personal gratis < $200k/año; Pro es cuota por asiento |
| Creer que el Runtime Fee sigue vigente (info de 2023) | Cancelado el 12-sep-2024; modelo actual = suscripción por asiento |
| Shipear y olvidarse del editor: no poder rebuildear cuando sale un parche de seguridad | Congelar la versión EXACTA del editor en el repo (ProjectVersion.txt), CI o receta de build reproducible |
| Confiar en versiones de paquetes de memoria ("Entities 1.x", "Cinemachine 3 standalone") tras 6.3 | En 6.3+ los paquetes core van alineados al editor (Entities/Cinemachine/N4E en 6.x); comprobar en el Package Manager del proyecto |

## Fuentes

- What's new in Unity 6.0 — Manual oficial (docs.unity3d.com/6000.0) — lista autoritativa de features de 6.0 (GPU Resident Drawer, Render Graph, APV, Build Profiles, NGO 2.0).
- What's new in Unity 6.1 — Manual oficial (docs.unity3d.com/6000.1) — Deferred+, DX12 default, GraphicsStateCollection, reducción de variantes.
- What's new in Unity 6.2 — Manual oficial (docs.unity3d.com/6000.2) — Unity AI, Mesh LOD, World Space UI, UTF core.
- What's new in Unity 6.3 (LTS) — Manual oficial (docs.unity3d.com/6000.3) — confirmación de LTS y features 6.3 (Box2D v3, 3D en 2D Renderer, Shader Build Settings, pinnedPackages, Android API 25).
- Awaitable — Scripting API oficial (docs.unity3d.com/ScriptReference/Awaitable.html) — métodos exactos, pooling, single-await, cancelación.
- GPU Resident Drawer — Manual URP oficial (docs.unity3d.com/6000.1, urp/gpu-resident-drawer) — requisitos y pasos de activación exactos.
- Render graph system — Manual URP oficial (docs.unity3d.com/6000.1, urp/render-graph) — API de passes custom y camino legacy.
- Entities CHANGELOG — docs oficiales del paquete (com.unity.entities@6.6) — línea 1.0→1.4.2→core 6.x con fechas; transición a core package.
- Cinemachine 3.1 manual + guía "Upgrading from Cinemachine 2.x" — docs oficiales del paquete — renombres, namespace, Upgrader sin undo.
- Redirects @latest de paquetes (docs.unity3d.com/Packages) — versiones vigentes a 2026-07: inputsystem 1.19, netcode.gameobjects 2.13, addressables 3.1, cinemachine 6.6, netcode 6.6.
- "Unity is killing its controversial Runtime Fee" — Game Developer (gamedeveloper.com, sep-2024) — cancelación, $200k Personal, $2,200 Pro, +25% Enterprise, splash opcional.
- Unity (game engine) — Wikipedia — historia Runtime Fee, fechas de releases 2026 (6000.4/6000.5), CVE-2025-59489, caída de uso en Global Game Jam.
- "Unity 6.1 Released" / "Unity 6.2 Released" / "Unity 6.3 Released" — GameFromScratch — fechas exactas de release (24-abr-2025, 14-ago-2025, 4-dic-2025) y titulares; contraste con docs oficiales.
