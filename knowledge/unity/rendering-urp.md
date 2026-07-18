# Rendering con URP

> **Cuando cargar este archivo:** al configurar el pipeline gráfico de un proyecto Unity 6 (URP Asset, calidad, luces, post-processing), al trabajar con materiales/shaders, cámaras Cinemachine, sorting/iluminación 2D, o al diagnosticar draw calls y overdraw. [ver: rendimiento-unity] para profiling profundo.

## URP como default: qué pipeline usar

Un render pipeline es la serie de operaciones que toma el contenido de la escena y lo dibuja en pantalla (culling → rendering → post-processing). Unity tiene 3:

| Pipeline | Para qué | Cuándo elegirlo |
|---|---|---|
| **URP** (Universal RP) | Gráficos escalables en todas las plataformas; 2D y 3D; fuente C# pública | **Default para casi todo proyecto nuevo.** Especialmente móvil (GPUs tile-based/TBDR) y VR standalone |
| **HDRP** | Fotorrealismo high-end, solo 3D | Solo desktop/Xbox/PlayStation con presupuesto visual AAA. Más complejo de customizar |
| **Built-in (legacy)** | Pipeline viejo, C++ cerrado, recibe pocas updates | Solo mantener proyectos viejos. NO empezar nada nuevo aquí |

- Las plantillas estándar de Unity 6 ("Universal 3D" / "Universal 2D") crean el proyecto ya con URP configurado. Sin un Render Pipeline Asset asignado en Graphics settings, Unity corre Built-in.
- **Elegir pipeline TEMPRANO**: migrar a mitad de desarrollo es muy costoso — los shaders y features no son compatibles entre pipelines (docs oficiales lo advierten explícitamente).
- Shaders de Built-in (Standard) se ven **rosados** en URP. Usar el Render Pipeline Converter (`Window > Rendering > Render Pipeline Converter`) para migrar materiales.

## URP Asset y calidad: qué tocar primero

El **URP Asset** (Project Settings > Graphics, y por nivel de calidad en Project Settings > Quality) es el centro de control. Puede haber un asset distinto por quality level (Low/Medium/High) — así se escala entre móvil y desktop. Cada URP Asset apunta a un **Renderer** (Universal Renderer para 3D, 2D Renderer para 2D — esto decide si el proyecto es "2D lighting" o "3D lighting").

Secciones del asset y qué tocar primero:

| Sección | Setting clave | Guía |
|---|---|---|
| Rendering | **SRP Batcher** | ON siempre (reduce draw calls, ver abajo) |
| Rendering | Depth Texture / Opaque Texture | OFF si ningún shader los usa (cada uno cuesta un pass extra) |
| Quality | **HDR** | ON por default. OFF en móvil low-end si no usas bloom/tonemapping (ahorra bandwidth). HDR Precision: default 32 bit; 64 bit solo si hay banding |
| Quality | **Anti Aliasing (MSAA)** | Default disabled. 4x es el sweet spot en móvil (las GPUs tile-based lo hacen casi gratis); en deferred no aplica |
| Quality | **Render Scale** | 1.0 default. Bajar a 0.7–0.9 en móvil de pantalla densa = la palanca de rendimiento más directa. Upscaling Filter: Automatic/Bilinear/FSR 1.0/STP |
| Lighting | Main Light / Additional Lights | Additional Lights: Per Pixel, Per Vertex (baratas) o Disabled. Per Object Limit: máx 8 |
| Lighting | **Light Probe System** | Unity 6: "Light Probe Groups (legacy)" o **Adaptive Probe Volumes** |
| Shadows | **Max Distance** | Bajarla al mínimo que el juego tolere — concentra resolución de shadow map cerca de cámara |
| Shadows | Cascade Count | 1–4. Móvil: 1–2. Desktop: 3–4 |
| Shadows | Soft Shadows | Low/Medium/High; cuestan; en móvil evaluar Hard |
| Post-processing | Grading Mode / LUT Size | LUT 32 default (balance precisión/costo) |
| Volumes | Volume Update Mode | "Via Scripting" si los volumes no cambian por frame (ahorra CPU) |

```csharp
// Ajustar render scale en runtime (ej. opción de calidad in-game)
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
urp.renderScale = 0.8f; // 1.0 = resolución nativa
```

## Rendering paths y límites de luces

Se elige en el **Universal Renderer asset** (propiedad Rendering Path): Forward, **Forward+**, Deferred, Deferred+.

- **Forward** (default): cada objeto se ilumina con las luces que lo afectan. Límite por objeto: **1 Main Light + 8 Additional Lights** per-pixel.
- **Forward+**: divide la pantalla en tiles y culls luces por tile — **elimina el límite por objeto** (queda solo límite por cámara). Ignora los settings Additional Lights/Per Object Limit del asset. Requerido por GPU Resident Drawer en 6.0 (desde 6.1 este también acepta Deferred+).
- **Deferred / Deferred+**: muchas luces en escenas densas 3D; no compatible con MSAA ni con algunas features. Para la mayoría de juegos indie, Forward+ es la mejor opción por defecto en 3D.
- Límite de Additional Lights **por cámara** en URP: **256** desktop/consola, **32** móvil, **16** en OpenGL ES 3.0 o anterior (cifras exactas de "Light limits in URP", manual Unity 6).
- Notable en el renderer: **Depth Priming** (Auto/Forced; incompatible con deferred, MSAA y móviles TBDR) y Depth Texture Mode "After Transparents" (recomendado en móvil por bandwidth).

## Materiales y shaders

Shaders que trae URP (elegir el MÁS BARATO que logre el look):

| Shader | Qué es | Cuándo |
|---|---|---|
| **Lit** | PBR completo (metallic/specular workflow) | Default 3D realista |
| **Simple Lit** | Iluminación no-PBR (Blinn-Phong), mucho más barato | Móvil, estilizado |
| **Baked Lit** | Solo recibe lightmaps + probes, cero luces realtime | Escenografía 100% baked |
| **Unlit** | Sin iluminación | UI en mundo, skyboxes, VFX, estilo flat |
| **Complex Lit** | Lit + features caras (clear coat); forward only | Casos puntuales (carros, cerámica) |
| **Sprite-Lit-Default** | Sprites que reciben Light 2D | Default del 2D Renderer |

**SRP Batcher** (la razón #1 por la que URP rinde): no fusiona draw calls — reduce los cambios de render-state entre ellos, agrupando por shader variant. Con él activo puedes usar muchos **materiales distintos del mismo shader** sin costo extra por material.
- Regla: pocos shaders, muchos materiales.
- ⚠️ `MaterialPropertyBlock` **rompe** la compatibilidad con SRP Batcher para ese renderer. Para variar propiedades por instancia: materiales distintos (baratos con SRP Batcher) o shader con GPU instancing.
- Shaders custom compatibles = propiedades por material en un CBUFFER `UnityPerMaterial` (Shader Graph lo genera solo).

## Shader Graph básico

- Crear: `Assets > Create > Shader Graph > URP >` **Lit / Unlit / Sprite Lit / Sprite Unlit** Shader Graph (el sub-target correcto importa: Sprite Lit para 2D con luces).
- Flujo: nodos → **Master Stack** (bloques Vertex/Fragment: Base Color, Normal, Emission, Alpha…). Propiedades expuestas se declaran en el **Blackboard** y aparecen en el material inspector.
- Un material usa el graph como cualquier shader; cambiar propiedades por script con `material.SetFloat("_MiProp", x)` (usar la Reference del Blackboard, no el display name).
- Patrones típicos de juego: flash blanco de daño (Lerp a blanco por propiedad), dissolve (noise + Alpha Clip), outline 2D, scroll de UVs. Mantener graphs chicos; cada feature suma costo por pixel.
- Emission > 1 con HDR activo es lo que alimenta el Bloom (glow selectivo).

## Luces 3D: realtime, baked, mixed

Modo de cada Light (propiedad **Mode**):

| Modo | Qué aporta | Costo runtime | Para qué |
|---|---|---|---|
| **Baked** | Directa + indirecta pre-calculada en lightmaps/probes | Casi cero | Escenografía estática. No afecta objetos dinámicos directamente (via probes sí), sin specular |
| **Realtime** | Directa + sombras cada frame; SIN luz indirecta (sombras negras) | Alto (más con shadows) | Luces que se mueven/cambian, pocas y controladas |
| **Mixed** | Directa realtime + indirecta baked | Medio | El grueso de las luces principales de un nivel |

**Lighting Mode** del proyecto (Lighting window) define cómo se comportan TODAS las mixed:

| Lighting Mode | Sombras estáticos | Sombras dinámicos | Cuándo |
|---|---|---|---|
| **Baked Indirect** | Realtime | Realtime | Mejor calidad de sombra realtime; hardware con presupuesto |
| **Shadowmask** | Baked (máx 4 luces solapadas por objeto; textura shadowmask con mismo UV que lightmap) | Realtime | Balance calidad/costo, escenas grandes |
| **Subtractive** | Baked | Realtime solo de la Directional principal | Lo más barato: móvil low-end, cel shading, escenas simples |

Flujo de bake: marcar geometría estática con **Contribute GI** (Static flags) → mesh import "Generate Lightmap UVs" si el modelo no trae UV2 → `Window > Rendering > Lighting` → Generate Lighting (Progressive Lightmapper CPU o **GPU**, mucho más rápido). Lightmap Resolution controla densidad de texels (calidad vs tamaño de bake).

## Lightmaps, probes y reflections

- **Objetos dinámicos no reciben lightmaps** — reciben luz indirecta via probes.
- **Adaptive Probe Volumes (APV)** — el sistema moderno en Unity 6 URP: coloca probes automáticamente e ilumina **per-pixel** (los Light Probe Groups legacy son manuales y per-object). Activar en URP Asset > Lighting > Light Probe System. Soporta Baking Sets multi-escena, streaming para mundos grandes y lighting scenarios. Para proyectos nuevos con luz baked: APV.
- **Reflection Probes**: capturan una vista esférica en Cubemap para materiales reflectivos. Baked casi siempre; realtime solo si es imprescindible (carísimos). URP Asset habilita **Probe Blending** y **Box Projection** (interiores).

## Luces 2D (Light 2D)

Requiere el **2D Renderer** asignado en el URP Asset (plantilla Universal 2D lo trae). Sistema coplanar propio: luces 3D NO afectan renderers 2D y viceversa. El pipeline dibuja las luces en render textures por sorting layer y luego los sprites las muestrean (batchea sorting layers consecutivos con el mismo set de luces — menos layers con luces distintas = más rápido).

Tipos de **Light 2D**:

| Tipo | Qué es | Propiedades clave |
|---|---|---|
| **Global** | Ilumina todo en sus sorting layers | ⚠️ Solo UNA global por Blend Style y por sorting layer |
| **Spot** (point) | Cono/círculo | Radius Inner/Outer, Inner/Outer Spot Angle |
| **Freeform** | Polígono editable con spline | Falloff, Falloff Strength |
| **Sprite** | Un sprite como máscara de luz (cookies 2D) | Sprite |

Comunes: Intensity (default 1), Color, **Target Sorting Layers** (qué capas ilumina), Blend Style, Overlap Operation (Additive/Alpha Blend), Shadow Strength (0–1, con componentes **ShadowCaster2D** en los objetos), Volumetric Intensity, Normal Map Quality (Disabled/Fast/Accurate — sprites con normal maps reaccionan a la dirección de la luz).

En el **2D Renderer Data**: Default Material Type (Lit = sprites nuevos usan Sprite-Lit-Default; Unlit si el juego no usa luces 2D), **Light Blend Styles** (hasta 4: multiply, additive, etc.), Camera Sorting Layer Texture (para shaders custom de distorsión/agua), Depth/Stencil buffer (desactivable en móvil si no usas Sprite Mask).

Setup mínimo de un juego 2D con luces: 1 Global Light blanca a intensity ~0.2–0.5 (luz ambiente; sin ella todo lo Lit se ve negro) + luces Spot/Freeform puntuales.

## Post-processing con Volumes

URP trae post-processing integrado via el **Volume framework** (⛔ el package "Post Processing Stack v2" NO es compatible con URP — no instalarlo).

Mecánica:
- **Volume** (componente) → referencia un **Volume Profile** (asset) → contiene **Volume Overrides** (Bloom, Vignette, Tonemapping…). Solo las propiedades con checkbox activo overridean.
- **Global Volume** afecta siempre; **local** (Box/Sphere/Convex Mesh Volume) solo cuando la cámara está dentro/cerca (Blend Distance interpola). Priority resuelve conflictos; los 2 default volumes (uno project-wide en Graphics settings y uno por quality en el URP Asset) tienen la prioridad más baja — cualquier volume tuyo los pisa.
- La cámara necesita **Post Processing** activado en su inspector.

Efectos y criterio (menos es más — un juego entero pasa con 3-4 efectos):

| Efecto | Para qué | Guía |
|---|---|---|
| **Bloom** | Glow de zonas brillantes (neones, proyectiles) | Defaults: Threshold 0.9, Scatter 0.7, Intensity 0 (=off; subir a 0.5–2). Requiere HDR para brillar selectivo (emission > 1). Móvil: High Quality Filtering OFF, Downscale Quarter, bajar Max Iterations (default 6) |
| **Vignette** | Oscurecer bordes, foco, tensión | Intensity 0.2–0.4; más solo como efecto puntual (daño) |
| **Color Adjustments** | Post-Exposure, Contrast, Saturation, Color Filter | El "grading" básico. Saturation -100 = flashback B/N |
| **Tonemapping** | Mapear HDR→pantalla | ACES = look cinemático (desatura); Neutral = respeta el arte. Elegir uno y todo el arte se calibra con él |
| Depth of Field | Desenfoque | Caro. Móvil low-end: Gaussian, nunca Bokeh |
| Motion Blur / Chromatic Aberration / Lens Distortion | Efectos puntuales | ⛔ Los tres prohibidos en VR (mareo). Motion blur caro en móvil |

Eficientes en móvil según docs oficiales: Bloom (HQ off), Chromatic Aberration, Color Grading, Lens Distortion, Vignette.

```csharp
// Modificar un override en runtime (ej. vignette al recibir daño)
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

[SerializeField] Volume volume;
Vignette vignette;

void Awake() => volume.profile.TryGet(out vignette);
public void FlashDamage() => vignette.intensity.value = 0.45f; // luego lerp de vuelta
```

## Cámaras: URP + Cinemachine 3.x

Cámaras URP: **Base** (renderiza la escena) + **Overlay** (se apilan encima — camera stacking — para UI 3D, armas FPS). Cada cámara extra cuesta: culling + passes completos; limitar el Culling Mask de cada una y no apilar por gusto en móvil.

**Cinemachine 3.x** (package `com.unity.cinemachine` 3.x): una sola `Camera` real con **CinemachineBrain**; N **CinemachineCamera** (GameObjects virtuales) compiten por prioridad y el Brain blendea entre ellas. Cambiar de plano = activar/priorizar otra CinemachineCamera, nunca mover la Camera a mano.

⚠️ Cinemachine 3.x renombró TODO respecto a 2.x (los tutoriales viejos confunden): namespace `Unity.Cinemachine` (antes `Cinemachine`), `CinemachineVirtualCamera` → **CinemachineCamera**, campos sin prefijo `m_`, filtrado por layers → **Channels**.

Componentes de comportamiento sobre la CinemachineCamera:
- **Position Composer** (2D/ortho el más usado): mantiene el target en una posición de pantalla. **Dead Zone** (zona donde el target se mueve sin mover cámara), **Damping** por eje (retraso tipo operador humano; subir = cámara pesada), **Lookahead Time/Smoothing** (adelanta la cámara hacia donde se mueve el target; con animación ruidosa mete jitter — subir smoothing o bajar time).
- **Rotation Composer** / **Orbital Follow**: apuntar/orbitar en 3D (tercera persona).
- **CinemachineConfiner2D** (extensión): confina la cámara a un `Collider2D` (típico CompositeCollider2D del nivel). Damping para esquinas, Slowing Distance para frenar cerca del borde. Si el polígono cambia en runtime → `InvalidateBoundingShapeCache()`; si cambia el Orthographic Size/FOV → `InvalidateLensCache()`.
- **Impulse** = screen shake bien hecho [ver: gamedev/game-feel]: `CinemachineImpulseSource` (o `CinemachineCollisionImpulseSource`) en el objeto que golpea + extensión `CinemachineImpulseListener` en la CinemachineCamera.

```csharp
using Unity.Cinemachine;

[SerializeField] CinemachineImpulseSource impulse;

public void OnExplosion(Vector3 at, float fuerza)
{
    // GenerateImpulseAt() (sin "PositionWithVelocity") es legacy — reemplazada por esta:
    impulse.GenerateImpulseAtPositionWithVelocity(at, Vector3.down * fuerza);
    // o impulse.GenerateImpulseWithForce(fuerza); si no importa la posición
}
```

## Sorting en 2D

Orden de decisión de Unity para renderers 2D (de mayor a menor prioridad):

1. **Sorting Layer** (capas globales ordenadas: Background → Props → Player → FX → UI…)
2. **Order in Layer** (int dentro de la capa)
3. Render Queue del material/shader
4. **Distancia a cámara** — según Transparency Sort Mode: en ortho, distancia a lo largo del eje de vista; con **Custom Axis** se ordena por un eje custom
5. Empate → orden interno (incontrolable — nunca depender de él)

- **Y-sort top-down** ("el que está más abajo tapa"): Transparency Sort Mode = Custom Axis con eje **(0, 1, 0)**. ⚠️ En URP con 2D Renderer esto se configura en el **2D Renderer Data asset**, NO en Project Settings > Graphics (eso es Built-in).
- **Sorting Group**: agrupa todos los renderers bajo un root para que se ordenen como UNA unidad frente al resto (personaje multi-sprite: cuerpo, brazos, arma). Sin él, los pedazos de dos personajes se intercalan. Sorting Groups anidados = costo extra; usar con moderación.
- La Z en 2D solo importa como distancia a cámara (punto 4) — usar sorting layers, no Z, como mecanismo principal.

## Sprite Atlas, draw calls y overdraw

**Sprite Atlas** (`Create > 2D > Sprite Atlas`): empaqueta sprites en una sola textura → sprites consecutivos del mismo atlas se dibujan en menos draw calls.
- **Objects for Packing** acepta carpetas completas. **Include in Build** ON por default (dejarlo).
- Agrupar por USO simultáneo (atlas "gameplay", atlas "UI"), no por tipo de asset — mezcla de atlases en la misma escena rompe el batching.
- Un sprite en DOS atlases = duplicado en memoria y ambigüedad. Padding default 4px (evita bleeding entre sprites vecinos; subir si hay mipmaps).
- ⚠️ Read/Write Enabled duplica la memoria de la textura. Para sprites de Canvas/UI: desactivar Rotation en el packing.
- Master/Variant atlases = mismo layout a distinta resolución (calidad por plataforma).

**Overdraw** (dibujar el mismo pixel varias veces) — el asesino silencioso en 2D/móvil:
- Todo sprite es transparente (alpha blend): no escribe depth y se dibuja SIEMPRE, tape lo que tape. Capas de fondo gigantes + niebla + partículas encima = 4-6x overdraw.
- GPUs móviles (tile-based) lo sufren especialmente: bandwidth quemado en pixeles que no se ven.
- Antídotos: Sprite Import > Mesh Type **Tight** (no Full Rect) para recortar zonas transparentes; menos capas fullscreen superpuestas; partículas chicas y pocas que cubran poca pantalla; nada de quads fullscreen con alpha casi-0 "por si acaso". Ver overdraw: Rendering Debugger / Scene view modo Overdraw.
- Frame Debugger (`Window > Analysis > Frame Debugger`) responde "¿por qué tengo 300 draw calls?" paso a paso [ver: rendimiento-unity].

## Unity 6: Render Graph, GPU Resident Drawer, GPU Occlusion Culling

Qué aporta cada uno (nivel: saber qué son y cuándo activarlos):

- **Render Graph**: desde Unity 6 URP compila el frame como un grafo declarativo de passes → merge de passes y menos memoria/bandwidth. Afecta a quien escribe **custom passes**: `ScriptableRenderPass` ahora se implementa con `RecordRenderGraph()` y APIs como `AddBlitPass`; el código legacy (Execute/SetRenderTarget) requiere **Compatibility Mode** (Graphics > URP > Render Graph). Assets de la Store viejos con renderer features pueden exigir ese modo. Debug: **Render Graph Viewer**.
- **GPU Resident Drawer**: dibuja GameObjects via `BatchRendererGroup` con instancing automático → menos draw calls y menos CPU sin tocar código. Activarlo: URP Asset > Rendering > GPU Resident Drawer = **Instanced Drawing** + SRP Batcher ON + Rendering Path **Forward+** (o Deferred+ desde 6.1) + Project Settings > Graphics > BatchRendererGroup Variants = **Keep All** + Static Batching OFF (compite). Solo MeshRenderer (no sprites, no skinned como instanced), no OpenGL ES. Checklist canónico: [ver: unity6-actualidad]. Vale la pena en 3D con muchos objetos repetidos (bosques, ciudades, props).
- **GPU Occlusion Culling**: la GPU descarta objetos tapados usando el depth del frame anterior. Requiere GPU Resident Drawer + Render Graph activo (sin Compatibility Mode); checkbox **GPU Occlusion** en el Universal Renderer. Ayuda en escenas con mucha oclusión real; en escenas abiertas sin oclusión puede COSTAR más de lo que ahorra.
- **STP** (Spatial Temporal Post-processing): upscaler temporal integrado, opción del Upscaling Filter en el URP Asset (render scale < 1 con mejor calidad visual).
- Para un juego 2D o un 3D chico, estos sistemas aportan poco — no activarlos "porque están" [ver: unity6-actualidad].

## Reglas practicas

1. Proyecto nuevo = URP. Plantilla Universal 2D para 2D (trae 2D Renderer), Universal 3D para 3D. No cambiar de pipeline a mitad de proyecto.
2. SRP Batcher ON siempre; diseñar con pocos shaders y muchos materiales; nunca `MaterialPropertyBlock` en renderers que quieres batcheados.
3. Un URP Asset por quality level; escalar con: Render Scale, shadow distance/cascadas, Additional Lights per-vertex, MSAA.
4. 3D: Rendering Path **Forward+** salvo razón concreta (quita el límite de 8 luces por objeto).
5. Elegir el shader más barato que dé el look: Unlit > Baked Lit > Simple Lit > Lit > Complex Lit.
6. Luz de un nivel estático: luces **Mixed** + bake (Contribute GI en la geometría estática) + APV para los dinámicos. Realtime puro solo en lo que de verdad se mueve.
7. Móvil low-end: Lighting Mode **Subtractive**; medio: **Shadowmask**; desktop: **Baked Indirect**.
8. Sombras: Max Distance lo más corta posible; es la palanca de calidad de sombra más barata.
9. 2D con luces: 2D Renderer + una sola Global Light por sorting layer como ambiente + Spot/Freeform puntuales; Target Sorting Layers explícitos.
10. Post-processing: HDR ON si hay Bloom; máximo 3-5 overrides (Bloom + Vignette + Color Adjustments + Tonemapping cubren el 90%); en móvil HQ filtering OFF y sin Motion Blur/DoF Bokeh.
11. La cámara real no se toca: CinemachineBrain + una CinemachineCamera por "plano"; cambiar de cámara = prioridades, transiciones = blends del Brain.
12. Plataformas/2D: Position Composer con Dead Zone y damping bajo en X; Confiner2D con CompositeCollider2D del nivel.
13. Screen shake SIEMPRE con Impulse (source + listener), nunca moviendo el transform de la cámara [ver: gamedev/game-feel].
14. Sorting 2D por Sorting Layers + Order in Layer; personajes multi-sprite bajo un Sorting Group; top-down = Custom Axis (0,1,0) en el 2D Renderer Data.
15. Un Sprite Atlas por contexto de uso (gameplay/UI); verificar el batching real con el Frame Debugger, no asumirlo.
16. Sprites con mucha área transparente: Mesh Type Tight; vigilar overdraw con el modo Overdraw antes de optimizar otra cosa.
17. Verificar SIEMPRE en el device real más débil del target: los números de draw calls/fillrate del editor no representan una GPU móvil.
18. 3D con miles de props repetidos en Unity 6: GPU Resident Drawer (Forward+ + Keep All variants) antes de inventar un sistema de instancing propio.

## Errores comunes

| Error | Antídoto |
|---|---|
| Materiales rosados al importar assets | Shader Built-in en proyecto URP → Render Pipeline Converter o reasignar shader URP |
| Instalar Post Processing Stack v2 en URP | No es compatible; URP trae Volumes integrado |
| Bloom "no se ve" | Intensity default es 0; y sin HDR (o sin emission > threshold 0.9) no hay qué bloomear |
| Todo el juego 2D se ve negro al pasar a 2D Renderer | Los sprites Lit necesitan luz: agregar Global Light 2D a los sorting layers |
| Luces 3D puestas en un juego 2D (o viceversa) no hacen nada | Sistemas separados: Light 2D solo afecta renderers 2D, Light 3D solo 3D |
| "Agregué la 9ª luz y desaparece" en Forward | Límite per-object (main + 8). Pasar a Forward+ |
| Cambio Transparency Sort Axis en Project Settings y no pasa nada | En URP 2D se configura en el 2D Renderer Data asset |
| Sprites de un personaje se intercalan con otro personaje | Falta Sorting Group en el root de cada personaje |
| Ordenar 2D moviendo la Z | Frágil (empates, camera mode); usar sorting layers/order |
| Sombras baked y realtime "dobles" o que no cuadran | Lighting Mode mal elegido; en Subtractive es limitación conocida — ajustar Realtime Shadow Color o subir a Shadowmask |
| Editar lightmaps y "no cambia nada" | Falta re-bake (Generate Lighting) o el objeto no tiene Contribute GI / UV2 |
| Objetos dinámicos negros en escena baked | Sin probes: activar APV (o colocar Light Probe Groups legacy) |
| Tutorial Cinemachine 2.x: `CinemachineVirtualCamera`, `m_Lens`, namespace `Cinemachine` | Todo renombrado en 3.x: `CinemachineCamera`, sin `m_`, `Unity.Cinemachine` |
| Screen shake moviendo transform de la Camera con Cinemachine activo | El Brain lo pisa cada frame; usar Impulse |
| Confiner2D ignora el nuevo colisionador del nivel | Cache: llamar `InvalidateBoundingShapeCache()` tras cambiar el polígono |
| FPS bajos en móvil con "solo sprites" | Overdraw por capas fullscreen alpha + partículas; medir con modo Overdraw, Mesh Type Tight |
| GPU Resident Drawer activado y no hace nada | Requiere Forward+, SRP Batcher, BatchRendererGroup Variants = Keep All, y solo cubre MeshRenderer |
| Renderer feature de la Store rota en Unity 6 ("render graph error") | Feature legacy pre-render-graph: activar Compatibility Mode o actualizar el asset |
| Camera stacking alegre en móvil | Cada Overlay camera re-cull y re-renderiza; limitar culling masks o eliminar la capa extra |
| Un solo URP Asset para todas las calidades | Imposible escalar móvil↔desktop; un asset por quality level |

## Fuentes

- Render pipelines / Choosing a render pipeline — Unity Manual 6000.2 (docs.unity3d.com) — definición de pipeline, URP vs HDRP vs Built-in y criterio de elección.
- Universal Render Pipeline Asset — Unity Manual 6000.2, sección URP — inventario exacto de settings (HDR 32/64 bit, MSAA, Render Scale, upscalers, Light Probe System APV, Volumes default).
- Rendering paths (Universal Renderer) + Light limits in URP — Unity Manual 6000.2 — Forward vs Forward+/Deferred+, límites exactos: main + 8 per-object; 256/32/16 additional lights por cámara.
- Shaders in URP (prebuilt shaders) — Unity Manual 6000.2 — roster Lit/Simple Lit/Baked Lit/Complex Lit/Unlit.
- SRP Batcher — Unity Manual 6000.2 — qué batchea de verdad (render-state por shader variant) y compatibilidad.
- Light Modes introduction + Lighting Mode (Mixed) — Unity Manual 6000.2 — Baked/Realtime/Mixed y Baked Indirect/Shadowmask/Subtractive con costos y casos de uso.
- Lightmapping / Progressive Lightmapper — Unity Manual 6000.2 — flujo de bake, Contribute GI, Generate Lightmap UVs.
- Adaptive Probe Volumes (URP) — Unity Manual 6000.2 — APV: colocación automática, per-pixel, baking sets/streaming.
- Reflection Probes in URP — Unity Manual 6000.2 — cubemaps de reflexión, blending y box projection.
- Introduction to Lights 2D + Light 2D properties + 2D Renderer Data — Unity Manual 6000.2 (URP) — tipos de luz 2D, propiedades exactas, blend styles, regla "una global por blend style y sorting layer", pipeline de light textures.
- Volumes + Post-processing in URP + Bloom reference — Unity Manual 6000.2 — framework de Volumes, defaults numéricos de Bloom, efectos eficientes en móvil, prohibidos en VR, incompatibilidad con PPv2.
- Camera stacking — Unity Manual 6000.2 (URP) — Base/Overlay y costo (culling masks).
- 2D Renderer sorting / Sorting Groups — Unity Manual 6000.2 — orden de prioridad completo del sorting 2D y Transparency Sort Axis (nota URP: en el renderer asset).
- Sprite Atlas reference — Unity Manual 6000.2 — packing, padding 4px, Include in Build, Read/Write x2 memoria, master/variant.
- GPU Resident Drawer + GPU occlusion culling + Render graph — Unity Manual 6000.2 (URP) — requisitos exactos de activación, qué mejoran, limitaciones.
- Cinemachine 3.1 package docs (upgrade from 2.x, Position Composer, Confiner2D, Impulse) + API `CinemachineImpulseSource` — docs.unity3d.com/Packages/com.unity.cinemachine@3.1 — renombres 3.x, propiedades y firmas exactas (`GenerateImpulseAtPositionWithVelocity`, `GenerateImpulseWithForce`, `GenerateImpulseWithVelocity` vigentes; `GenerateImpulse(...)`/`GenerateImpulseAt(...)` sin sufijo son overloads legacy).
- Shader Graph 17.x — Getting Started — docs.unity3d.com/Packages/com.unity.shadergraph — flujo asset→nodos→Master Stack→material, targets URP.
- Unity Overdraw: Improving GPU Performance — TheGamedev.Guru (Rubén Torres) — qué es overdraw, por qué la transparencia lo dispara en GPUs tile-based y estrategias (tight meshes, menos capas).
