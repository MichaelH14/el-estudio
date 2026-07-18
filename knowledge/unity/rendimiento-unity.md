# Rendimiento y optimización (Unity 6 + URP)

> **Cuando cargar este archivo:** al diagnosticar frames caídos, stutter, GC spikes o consumo de memoria; antes de decidir técnica de batching; al fijar presupuestos de rendimiento para móvil; y en cualquier pase de optimización previo a un release.

## 1. Metodología: medir antes de optimizar

Regla absoluta: **ninguna optimización sin una medición que la justifique y otra que la confirme**. Cambiar una sola cosa entre medición y medición.

### Presupuesto de frame

| Target | Presupuesto total/frame |
|---|---|
| 30 fps | 33.33 ms |
| 60 fps | 16.67 ms |
| 120 fps | 8.33 ms |

En móvil, no gastar el presupuesto completo: dejar margen para thermal throttling (la práctica citada por Unity es usar ~65% del presupuesto — cifra del e-book oficial de optimización móvil, NO VERIFICADO en esta investigación; el principio de dejar margen sí es doc oficial vía Adaptive Performance).

### Herramientas (cuál usar para qué)

| Herramienta | Para qué |
|---|---|
| **Profiler (Window > Analysis > Profiler)** | Dónde se va el tiempo por frame: módulos CPU Usage, GPU, Memory, Rendering, Physics |
| **CPU Usage module** | Categorías Rendering/Scripts/Physics/Animation/GC/VSync/GI/UI. Columna **GC Alloc** = bytes alocados ese frame (el objetivo en gameplay es 0). Timeline view muestra todos los threads; Hierarchy agrupa por coste |
| **Frame Debugger (Window > Analysis > Frame Debugger)** | Recorre los eventos de render uno a uno: qué shader, qué geometría, y por qué un draw call NO se batcheó con el anterior |
| **Memory Profiler (paquete `com.unity.memoryprofiler`)** | Snapshots de memoria completos, comparación A/B entre snapshots para encontrar leaks y los mayores consumidores. Distinto del módulo Memory del Profiler (que es vista en vivo, menos detalle) |
| **Physics Debug window** | Visualizar colliders, contactos y estado de Rigidbodies |

### CPU-bound vs GPU-bound (lo primero que hay que decidir)

- `Gfx.WaitForPresentOnGfxThread` dominando el frame → **GPU-bound**: la CPU espera a la GPU. Optimizar fill rate, shaders, resolución, vértices.
- `WaitForTargetFPS` alto → el frame va sobrado, está esperando al cap (targetFrameRate/vSync). No hay problema.
- Scripts/Physics/GC dominando → **CPU-bound**: optimizar código, física, allocations, draw call submission.
- GPU-bound se subdivide (doc oficial): **fill rate** (píxeles/overdraw — el limitante típico en móvil), **memory bandwidth** (texturas sin comprimir/sin mipmaps), **vertex processing** (demasiados vértices).

### Profilear EN el dispositivo real

El editor añade overhead propio y su hardware no se parece al target: **los números del editor no valen para decidir**. Flujo oficial:

1. Build Profiles → activar **Development Build** (+ opcional **Autoconnect Profiler**).
2. Correr en el dispositivo; conectar el Profiler por red local, cable o IP.
3. Web solo soporta profiling con Autoconnect activado (no por IP).

**Deep Profiling** instrumenta cada llamada C#: útil para localizar un culpable puntual, pero distorsiona tanto los tiempos que no sirve para medir — activarlo solo en sesiones de búsqueda, nunca para validar.

## 2. Draw calls y batching en URP

El coste de un draw call es sobre todo **CPU**: preparar estado de render y enviar comandos a la GPU. Técnicas disponibles y cuándo aplica cada una:

| Técnica | Qué hace | Requisitos | Gotchas |
|---|---|---|---|
| **SRP Batcher** (default en URP) | No reduce el número de draw calls: reduce los cambios de estado entre ellos, manteniendo datos de material persistentes en GPU | Shader compatible: propiedades de material en cbuffer `UnityPerMaterial` (los shaders de URP y Shader Graph lo son). Se activa/desactiva en el URP Asset | Un `MaterialPropertyBlock` en el renderer lo **rompe** para ese renderer. Una propiedad de material fuera de `UnityPerMaterial` rompe el shader entero. Minimizar variantes de shader |
| **GPU instancing** | Un draw call para N copias del mismo mesh + material | Checkbox "Enable GPU Instancing" en el material. Variaciones por instancia (color, escala) vía `MaterialPropertyBlock` | **Incompatible con SRP Batcher**: en URP, con shader custom solo funciona si ese material/renderer no pasa por el SRP Batcher. No soporta `SkinnedMeshRenderer`. Compensa más en móvil que en desktop |
| **Static batching** | Combina meshes estáticos en buffers grandes (hasta 64 000 vértices por batch) | Marcar objetos como Batching Static (o `StaticBatchingUtility` en runtime) | Cuesta memoria (geometría combinada adicional). Solo objetos que jamás se mueven |
| **Dynamic batching** | Combina en CPU meshes pequeños en movimiento | Mesh ≤ 300 vértices y ≤ 900 atributos de vértice, mismo material | **Doc oficial: ya no se recomienda en general** — el overhead de CPU puede superar el del draw call. Solo considerar en dispositivos muy débiles |
| **Atlasing** | Varias texturas en una → varios objetos comparten material → menos cambios de estado | Sprite Atlas para 2D/UI; atlas manual o texture arrays en 3D | Con SRP Batcher el beneficio es menor (ya tolera muchos materiales del mismo shader), pero sigue siendo clave para UI y sprites |

**Decisión práctica en URP (Unity 6):**
1. Dejar el SRP Batcher activado (default) y usar shaders compatibles → cubre el caso general.
2. Cientos/miles de copias del mismo mesh (vegetación, proyectiles, escombros) → GPU instancing en ese material.
3. Geometría de nivel inmóvil y con memoria de sobra → static batching encima.
4. Verificar SIEMPRE con Frame Debugger: mirar cuántos draws entran en cada "SRP Batch" y la razón que da cuando corta un batch.

**GPU Resident Drawer (URP, Unity 6):** feature nueva que usa la API `BatchRendererGroup` para dibujar `MeshRenderer` compatibles con GPU instancing automático, sin tocar código. Requisitos: **Forward+** como render path (desde Unity 6.1 también Deferred+), API gráfica con soporte de compute shaders (no OpenGL ES), SRP Batcher activado en el URP Asset, "BatchRendererGroup Variants" en **Keep All** (Project Settings > Graphics), y **Static Batching desactivado** (compite y estorba) — checklist completo en [ver: unity6-actualidad]. No reemplaza al SRP Batcher ni al instancing manual: los combina — objetos compatibles caen en un "Hybrid Batch Group" automático; los que no califican, se dibujan por el camino normal. Mayor impacto en escenas grandes con muchos objetos que comparten mesh; el beneficio se nota en Play/build, no tanto en Scene View del editor.

Reducciones de draw calls que no son batching: occlusion culling, far clip plane más corto + skybox, menos luces por píxel en Forward, sombras dinámicas con moderación, lightmapping [ver: rendering-urp].

## 3. Garbage collector: a cero allocs por frame

Unity usa el GC **Boehm–Demers–Weiser en modo incremental por defecto**: reparte el trabajo en varios frames (usa el tiempo ocioso del frame si hay vSync o `targetFrameRate`). Limitaciones: los write barriers añaden un pequeño coste fijo, y si las referencias cambian demasiado entre pasos, cae a una **colección completa bloqueante** (el spike que se quería evitar). En Web no hay GC incremental.

Conclusión operativa: el GC incremental amortigua, no absuelve. El objetivo en gameplay sigue siendo **GC Alloc = 0 B por frame** (columna GC Alloc del CPU Profiler).

### Los sospechosos de siempre (doc oficial)

| Fuente de basura | Antídoto |
|---|---|
| Concatenación de strings (inmutables: cada `+` aloca) | `StringBuilder` reutilizado; actualizar textos solo cuando cambia el valor |
| Boxing (value type → `object`; "una de las fuentes más comunes en proyectos Unity") | Genéricos, overloads tipados; ojo con interpolación de strings y colecciones no genéricas |
| Closures/lambdas que capturan variables | No capturar en hot paths; métodos estáticos o estado en campos |
| `params` (aloca un array por llamada) | Overloads con aridad fija |
| LINQ en gameplay | Bucles `for` planos |
| `foreach` sobre colecciones vía interfaz (`IEnumerable<T>`) — boxea el enumerator | `for` o `foreach` sobre `array`/`List<T>` concretos (esos no alocan) |
| APIs que retornan arrays: `GetComponents`, `Physics.RaycastAll`, `Mesh.vertices`, `Input.touches` | Overloads con `List<T>` precreada; `Physics.RaycastNonAlloc` con buffer propio; cachear `Mesh.vertices` |
| `yield return new WaitForSeconds(x)` cada vez | Cachear el `WaitForSeconds` en un campo |
| `Instantiate`/`Destroy` en caliente | Object pooling (abajo) |
| `gameObject.tag == "X"` (copia el string) | `CompareTag("X")` |
| `Camera.main` repetido | Unity cachea internamente los GameObjects con tag `MainCamera`, pero el acceso sigue costando como un `GetComponent` (doc oficial; la versión exacta desde la que existe el cache NO VERIFICADA) → cachear en `Awake` igual |

### Pooling con la API oficial

```csharp
using UnityEngine.Pool;

public class BulletPool : MonoBehaviour {
    [SerializeField] Bullet prefab;
    ObjectPool<Bullet> pool;

    void Awake() {
        pool = new ObjectPool<Bullet>(
            createFunc: () => Instantiate(prefab),
            actionOnGet: b => b.gameObject.SetActive(true),
            actionOnRelease: b => b.gameObject.SetActive(false),
            actionOnDestroy: b => Destroy(b.gameObject),
            defaultCapacity: 32, maxSize: 256);
    }

    public Bullet Get() => pool.Get();
    public void Release(Bullet b) => pool.Release(b);
}
```

`UnityEngine.Pool` también trae `ListPool<T>`/`DictionaryPool<K,V>` para colecciones temporales (`using (ListPool<int>.Get(out var list))`).

- `System.GC.Collect()` manual: solo en pantallas de carga / transiciones, nunca en gameplay.
- `GarbageCollector.GCMode` permite desactivar el GC temporalmente (secciones ultra-críticas); exige disciplina total de allocs o la memoria solo crece.

## 4. Scripting: coste real de las operaciones

- **Cachear en `Awake`/`Start`**: `GetComponent`, `Camera.main`, transforms ajenos, hashes de Animator (`Animator.StringToHash`), IDs de shader (`Shader.PropertyToID`). Nada de `GetComponent`/`Find` dentro de `Update`.
- **`GameObject.Find` / `FindObjectsOfType`**: prohibidos en gameplay (escanean la escena). Referencias serializadas, inyección, o registro en un manager [ver: arquitectura-unity].
- **`Update()` vacíos o triviales**: eliminarlos. Cada `Update` cruza la frontera nativo→managed por MonoBehaviour por frame (medido por Unity en su blog "10 000 Update() calls"; unity.com no fetchable en esta investigación, el principio sigue vigente). Miles de instancias → patrón manager: un solo `Update` que itera una lista.
- Orden de magnitud mental: matemática y accesos a campos ≈ gratis; llamadas a la API de Unity (transform, física, render) ≈ decenas-cientos de ns cada una (cruzan a nativo); `GetComponent` ≈ búsqueda; `Instantiate`/`Destroy`/`AddComponent` ≈ caras y alocan; strings/LINQ ≈ caras y alocan. Las cifras exactas dependen del dispositivo: medir con el Profiler, no memorizar números.

### Jobs + Burst: cuándo compensa

**C# Job System**: código multihilo seguro sobre todos los cores. **Burst** compila un subset de C# (HPC#: structs, blittables, `Unity.Mathematics`, sin tipos managed) a nativo vía LLVM con SIMD; se aplica con `[BurstCompile]` sobre el job.

Compensa cuando: miles de elementos con el mismo cálculo (boids, ruido procedural, deformación de mesh, pathfinding en grid, análisis de datos), datos en `NativeArray`, y el resultado no se necesita en mitad del mismo callback. NO compensa para lógica de juego ordinaria (decenas de objetos, mucha interacción con la API de Unity — que no se puede tocar desde un job).

```csharp
using Unity.Burst; using Unity.Jobs; using Unity.Collections; using Unity.Mathematics;

[BurstCompile]
struct VelocityJob : IJobParallelFor {
    [ReadOnly] public NativeArray<float3> velocity;
    public NativeArray<float3> position;
    public float deltaTime;
    public void Execute(int i) => position[i] += velocity[i] * deltaTime;
}
// Schedule: new VelocityJob{...}.Schedule(n, 64).Complete();
```

Regla: `Schedule` temprano en el frame, `Complete()` lo más tarde posible (deja a los workers trabajar mientras el main thread sigue). `Complete()` inmediato desperdicia el paralelismo.

## 5. Física barata

[ver: fisica-unity] para el sistema completo; aquí solo el ángulo de coste.

- **Fixed Timestep** (Project Settings > Time): default 0.02 s (50 Hz). Cada paso corre la simulación entera: bajar la frecuencia (p. ej. 0.02 → 0.0333 para un juego móvil a 30 fps sin física fina) es la palanca más grande. **Maximum Allowed Timestep** (default 0.1 s) limita cuántos pasos se recuperan en un frame lento — evita la espiral de la muerte (frame lento → más pasos de física → frame más lento).
- **Colliders**: primitivos (Sphere < Capsule < Box) >> `MeshCollider`. Si hay que usar MeshCollider en objeto dinámico: convex (límite 255 triángulos) y revisar las cooking options. Componer 2-3 primitivos suele ganar a un mesh collider "exacto".
- **Layer Collision Matrix** (Project Settings > Physics): desmarcar todo par de layers que no deba interactuar — recorta pares en broadphase, es gratis y se olvida siempre. Proyectiles-vs-proyectiles y debris-vs-debris son los clásicos a desactivar.
- **Raycasts y queries**: siempre con `layerMask` y distancia finita; versiones `NonAlloc` con buffer reutilizado; no lanzar N raycasts por frame por enemigo — espaciarlos (cada 3-5 frames con offset por instancia).
- **Rigidbody sleeping**: dejar que duerman (no aplicar micro-fuerzas continuas que los mantengan despiertos). Solver iterations: bajar si la escena lo tolera.
- No mover transforms con física a mano cada frame (`transform.position` en un Rigidbody fuerza resync); usar `Rigidbody.MovePosition`/fuerzas y evitar depender de `Physics.autoSyncTransforms`.

## 6. Móvil

- **`Application.targetFrameRate`**: default -1 → en iOS/Android con `vSyncCount = 0` Unity renderiza a **30 fps** para ahorrar batería. Para 60 fps hay que pedirlo explícito: `Application.targetFrameRate = 60;`. Unity redondea al divisor más cercano del refresh de pantalla. Si `vSyncCount != 0`, `targetFrameRate` se ignora. En móvil el vSync de QualitySettings no aplica como en desktop: la palanca es `targetFrameRate`.
- **Thermal throttling**: el rendimiento pico dura minutos; el sostenible es el que importa. Profilear sesiones LARGAS (10-15 min) con el dispositivo ya caliente. El paquete **Adaptive Performance** (`com.unity.adaptiveperformance`) expone estado térmico y de batería, avisa antes del throttling y trae scalers automáticos de calidad (LOD, resolución, framerate).
- **Resolución**: en URP la palanca directa de fill rate es **Render Scale** en el URP Asset (bajar de 1.0 en pantallas de alta densidad es poco perceptible; probar 0.7-0.9 y medir — valores heurísticos, no doc). Alternativas Unity 6: **Dynamic Resolution** ("Allow Dynamic Resolution" en la Camera + `ScalableBufferManager.ResizeBuffers`) y upscaling **STP** (Spatial-Temporal Post-processing) en URP.
- **Batería**: cap de framerate (30 donde 60 no aporta), `OnDemandRendering` para menús/juegos por turnos (renderizar menos frames sin parar la lógica), y menos luces/sombras en tiempo real.
- **Fill rate es el cuello típico en móvil** (doc oficial): overdraw de partículas/UI/sprites superpuestos, fragment shaders caros. Shaders simples o Unlit donde se pueda.
- **Presupuestos orientativos por gama** — ⚠️ NO VERIFICADO contra fuente en esta investigación (unity.com/Arm inaccesibles); tratar como punto de partida y validar con Profiler en el dispositivo target real:

| Gama | Tris en pantalla | Draw calls/SetPass | Texturas |
|---|---|---|---|
| Baja (~2019-, GPU débil) | ~100 k | < 100 | ASTC 6x6/8x8, max 1024 |
| Media | 100-500 k | 100-300 | ASTC 6x6, max 2048 |
| Alta (flagship) | 500 k-1 M+ | 300-600 | ASTC 4x4/6x6, max 2048-4096 |

Lo que SÍ es doc oficial: el límite se descubre midiendo fill rate / bandwidth / vertex processing en el dispositivo, no con tablas.

## 7. UI y rendimiento (resumen — detalle en [ver: ui-unity])

Fuente: guía oficial "Optimizing Unity UI" (Unity Learn), aplica a UGUI:

- Cuando **cualquier** elemento dibujable de un Canvas cambia, el Canvas regenera sus batches completos → **separar canvases**: uno para lo estático, otro(s) para lo que cambia cada frame (contadores, barras de vida).
- Layout Groups recalculan constantemente: para estructuras simples, anchors/RectTransform a mano.
- Desactivar **Raycast Target** en todo Graphic que no reciba input (imágenes decorativas, textos).
- Overdraw de UI: no apilar paneles transparentes; deshabilitar (no solo tapar) la UI invisible.
- Scroll largos: pooling de celdas + `RectMask2D` para excluir lo no visible.

## 8. Memoria

Las **texturas son el mayor consumidor típico** de memoria en un juego. Orden de ataque: compresión por plataforma → tamaños máximos → mipmaps/streaming → carga/descarga con Addressables.

### Compresión por plataforma (doc oficial Unity 6)

| Plataforma | Formato recomendado | Nota |
|---|---|---|
| Android | **ASTC** | Soportado por casi toda GPU con OpenGL ES 3.1 o Vulkan. Fallback **ETC2** para dispositivos viejos |
| iOS/tvOS | **ASTC** | Desde chip A8 (2014). ETC2 para A7; PVRTC solo legacy |
| Windows/desktop | **DXT1** (RGB, 4 bpp), **BC7** (RGBA calidad) o **DXT5** (RGBA rápido), 8 bpp | HDR: **BC6H** |

- ASTC permite elegir tamaño de bloque: **4x4 = 8 bpp** (más calidad) hasta **12x12 = 0.89 bpp** (más compresión). 6x6 es el punto medio habitual para albedo móvil.
- Configurar en el importer con **platform overrides** (pestañas por plataforma en el inspector de la textura) [ver: assets-pipeline-git].
- Una textura sin comprimir (RGBA32 = 32 bpp) cuesta 4-8x más memoria y bandwidth que comprimida: nunca "None" en builds.

### Mipmaps y streaming

- Mipmaps: **+33% de memoria y disco**, pero mejoran rendimiento (menos cache misses/bandwidth) y calidad a distancia en 3D. **Activar en texturas 3D, desactivar en UI/2D pixel-perfect** (ahí el 33% es puro desperdicio).
- **Mipmap Streaming**: carga solo los mip levels necesarios según distancia de cámara — recorta VRAM en escenas grandes.

### Addressables para cargar/descargar

- Addressables gestiona memoria por **ref-counting**: cada `LoadAssetAsync` debe tener su `Release` espejo. Sin `Release`, el asset no se libera nunca.
- La memoria se libera de verdad **al descargar el AssetBundle entero**, no al soltar un asset: un bundle con 10 assets retiene los 10 mientras 1 siga referenciado (problema de granularidad → agrupar en bundles por patrón de uso, p. ej. por nivel).
- **Asset churn**: soltar el último asset de un bundle y volver a cargar otro del mismo bundle al instante = unload + reload del bundle completo. Detectarlo con el módulo de Addressables en el Profiler.
- `Resources/` es el anti-patrón: todo lo que hay dentro entra al build y complica la gestión de memoria; migrar a Addressables o referencias directas.

### Flujo con Memory Profiler

1. Snapshot en el dispositivo (Development Build) en el punto caliente.
2. Vista de mayores consumidores → casi siempre texturas mal comprimidas o duplicadas.
3. Snapshot A/B (antes/después de una escena o ciclo de gameplay) → diff = leaks (assets que debieron descargarse y siguen).

## Reglas prácticas

- [ ] Medir SIEMPRE antes y después; una sola variable por experimento; en el dispositivo real con Development Build.
- [ ] Decidir primero CPU-bound vs GPU-bound (`Gfx.WaitForPresentOnGfxThread` = GPU; Scripts/Physics/GC = CPU).
- [ ] GC Alloc = 0 B/frame en gameplay estable (columna GC Alloc del CPU Profiler es el contrato).
- [ ] SRP Batcher activado + shaders compatibles; nada de `MaterialPropertyBlock` en renderers que deban batchear (usa material compartido o instancing).
- [ ] Frame Debugger tras cualquier cambio de materiales/shaders: verificar que los batches no se rompieron.
- [ ] GPU instancing para masas del mismo mesh+material; static batching solo con memoria de sobra; dynamic batching: no.
- [ ] Pooling (`UnityEngine.Pool`) para todo lo que nace y muere en gameplay: balas, VFX, enemigos, celdas de UI.
- [ ] Cachear en `Awake`: componentes, `Camera.main`, `Shader.PropertyToID`, `Animator.StringToHash`, `WaitForSeconds`.
- [ ] Cero `GameObject.Find`/`GetComponent`/LINQ/concatenación de strings en `Update`.
- [ ] Eliminar `Update()` vacíos; con muchas instancias, patrón manager con una lista.
- [ ] Física: Layer Collision Matrix recortada, colliders primitivos, raycasts con layerMask + distancia, `NonAlloc`.
- [ ] Móvil: fijar `Application.targetFrameRate` explícito (el default es 30); profilear con el dispositivo caliente (10+ min).
- [ ] Fill rate primero en móvil: Render Scale, overdraw de partículas/UI, shaders simples.
- [ ] Texturas: ASTC en móvil con override por plataforma, mipmaps solo en 3D, tamaño máximo por gama.
- [ ] Cada `LoadAssetAsync` con su `Release`; bundles agrupados por patrón de uso.
- [ ] `System.GC.Collect()` solo en pantallas de carga.
- [ ] Jobs+Burst solo para trabajo masivo paralelizable sobre `NativeArray`; `Schedule` temprano, `Complete` tarde.
- [ ] Canvases divididos estático/dinámico; Raycast Target off por defecto [ver: ui-unity].
- [ ] Snapshot de Memory Profiler antes de cada milestone: los 10 mayores consumidores, justificados o arreglados.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Optimizar por intuición ("seguro son los draw calls") | Profiler primero; la causa real suele estar en otra categoría |
| Medir en el editor y dar por buenos los números | Development Build en dispositivo real; el editor miente en CPU y en memoria |
| Validar rendimiento con Deep Profile activado | Deep Profile solo para LOCALIZAR; medir sin él |
| Poner `MaterialPropertyBlock` "para variar el color" y matar el SRP Batcher | Con shaders URP: instancing para masas, o materiales distintos del mismo shader (el SRP Batcher los tolera bien) |
| Activar GPU instancing y asumir que funciona | El SRP Batcher tiene prioridad si el shader es compatible; verificar en Frame Debugger qué camino tomó |
| Confiar en el GC incremental y alocar alegremente | El incremental cae a colección completa bloqueante bajo presión; la meta sigue siendo 0 allocs |
| `new WaitForSeconds` en cada iteración de corutina | Cachear la instancia en un campo |
| Cachear `Physics.RaycastAll` como patrón (aloca array nuevo cada llamada) | `RaycastNonAlloc` con buffer propio reutilizado |
| Móvil "va a 30 y no sé por qué" | Es el default de Unity con vSyncCount 0; setear `targetFrameRate = 60` |
| Juego fluido 5 minutos, luego stuttering | Thermal throttling: presupuesto sostenible, Adaptive Performance, profilear en caliente |
| MeshCollider no-convex en objetos dinámicos | Primitivos compuestos o convex; el mesh exacto casi nunca se nota |
| Todos los layers colisionan con todos | Layer Collision Matrix: desmarcar pares imposibles el día 1 |
| Contador de puntos animado en el canvas principal → toda la UI se rebatchea cada frame | Canvas propio para elementos que cambian cada frame |
| Texturas 4K sin comprimir "porque se ve mejor" | ASTC 6x6 + max size por plataforma; comparar en pantalla real, no en el inspector |
| Mipmaps activados en atlas de UI | Desactivar: +33% de memoria sin beneficio en UI |
| `Release` de Addressables olvidado → memoria solo sube | Espejo load/release estricto; diff de snapshots del Memory Profiler entre escenas |
| Burst/Jobs para 20 enemigos | El overhead de schedule supera el trabajo; Jobs es para miles de elementos |
| `Complete()` justo después de `Schedule()` | Programar temprano, completar tarde; si no, es single-thread con extra pasos |

## Fuentes

Consultadas directamente en esta investigación (2026-07-18), todas contra Unity 6.0 (docs 6000.0) salvo indicación:

- **Scriptable Render Pipeline Batcher** — Unity Manual — qué combina el SRP Batcher y sus requisitos.
- **Make a GameObject incompatible with the SRP Batcher** — Unity Manual — confirma que `MaterialPropertyBlock` y propiedades fuera de `UnityPerMaterial` rompen la compatibilidad.
- **Optimizing draw calls / Draw call batching** — Unity Manual — límites exactos (static 64 k vértices/batch; dynamic 300 vértices/900 atributos) y la desrecomendación oficial de dynamic batching.
- **GPU instancing** — Unity Manual — requisitos, incompatibilidad con SRP Batcher, sin soporte SkinnedMeshRenderer.
- **Incremental garbage collection** — Unity Manual — Boehm incremental por defecto, write barriers, fallback a colección completa, sin soporte Web.
- **Reference type management / Optimizing code for managed memory** — Unity Manual — sospechosos de allocations (strings, boxing, closures, params, arrays retornados) y `UnityEngine.Pool`.
- **Collect performance data on a target platform** — Unity Manual — Development Build + Autoconnect, por qué no medir en editor.
- **CPU Usage Profiler module** — Unity Manual — markers `Gfx.WaitForPresentOnGfxThread`/`WaitForTargetFPS`, columna GC Alloc, Timeline vs Hierarchy.
- **Frame Debugger window** — Unity Manual — inspección evento a evento del frame.
- **Memory Profiler** — docs del paquete `com.unity.memoryprofiler` 1.1 — snapshots y análisis.
- **Optimize the physics system for CPU usage** — Unity Manual — timestep, colliders, Layer Collision Matrix, sleeping, solver iterations.
- **Application.targetFrameRate** — Unity Script Reference — default 30 fps en móvil con vSyncCount 0, interacción con vSync.
- **Camera.main** — Unity Script Reference — cacheado interno, coste comparable a `GetComponent`.
- **Dynamic resolution** — Unity Manual — Allow Dynamic Resolution, `ScalableBufferManager`, STP en URP.
- **Adaptive Performance** — docs del paquete `com.unity.adaptiveperformance` 5.1 — estado térmico, prevención de throttling, scalers.
- **Choose a GPU texture format by platform** — Unity Manual — ASTC/ETC2/DXT/BC7 por plataforma, bloques ASTC 4x4→12x12 (8→0.89 bpp).
- **Mipmaps introduction** — Unity Manual — +33% memoria, cuándo sí/no, Mipmap Streaming.
- **Memory management** — docs de Addressables 2.6 — ref-counting, granularidad de bundles, asset churn.
- **Job system / Burst** — Unity Manual + docs del paquete `com.unity.burst` 1.8 — HPC#, LLVM, restricciones.
- **Graphics performance fundamentals** — Unity Manual — taxonomía CPU-bound vs GPU-bound (fill rate/bandwidth/vertex), OnDemandRendering.
- **Optimizing Unity UI** — Unity Learn — rebuild de Canvas, división de canvases, Raycast Target, pooling de scroll.
- **GPU Resident Drawer** — Unity Manual (URP, Unity 6) — requisitos (Forward+, compute shaders, SRP Batcher on, BatchRendererGroup Variants = Keep All) y relación con SRP Batcher/instancing manual.
- **"10 000 Update() calls"** — Unity Blog (2015) — coste de la frontera nativo→managed por Update; NO re-fetcheado en esta investigación (unity.com 403), principio confirmado por la práctica general.
- Presupuestos de tris/draw calls por gama: **sin fuente verificable en esta investigación** (unity.com y developer.arm.com inaccesibles) — marcados como orientativos en el texto.
