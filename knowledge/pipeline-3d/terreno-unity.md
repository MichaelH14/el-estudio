# Terreno y splat maps en Unity

> **Cuando cargar este archivo:** cuando el nivel necesita paisaje natural grande (colinas, valles, planicies, bosque) y hay que decidir e implementar el sistema **Terrain de Unity 6** — esculpir/importar el heightmap, pintar texturas con Terrain Layers y splatmaps, mezclar pasto/tierra/roca, poblar hierba y árboles, y hacer que rinda (incluido móvil). Es el detalle Unity-side del hueco que [ver: modelado/entornos-modulares §5] abre a nivel de teoría (terreno vs mallas) y que [ver: pipeline-3d/receta-kit-modular] NO cubre (ese es arquitectura modular). Para el pipeline gráfico donde vive el Terrain Lit shader: [ver: unity/rendering-urp]; para el coste en teléfono: [ver: movil/unity-movil-rendimiento].

Este archivo NO repite: la frontera conceptual terreno-heightmap vs mallas (cuevas/voladizos/arquitectura son mallas — [ver: modelado/entornos-modulares §5]); la teoría de vegetación por cards/atlas/overdraw ([ver: modelado/entornos-modulares §7]); el marco de optimización de entorno ([ver: modelado/entornos-modulares §8]); ni URP/SRP Batcher/Draw Instanced en general ([ver: unity/rendering-urp], [ver: unity/rendimiento-unity]). Aquí van el sistema Terrain concreto y sus números.

## 1. Terrain vs mallas: la decisión, ya con criterio Unity

La regla base es de [ver: modelado/entornos-modulares §5]: **un heightmap = una altura por punto del plano** → no hay cuevas, voladizos ni verticales limpias. Añadido Unity-específico:

| Usa **Unity Terrain** cuando | Usa **mallas modeladas** cuando |
|---|---|
| Paisaje natural amplio (campo, colina, desierto, isla) | Interiores, ciudad, arquitectura precisa → kit modular [ver: pipeline-3d/receta-kit-modular] |
| Quieres pintar capas de material (pasto/tierra/roca) que se mezclan solas | Cuevas, túneles, arcos, voladizos, acantilados verticales |
| Necesitas hierba/árboles instanciados pintables encima con LOD automático | Control artístico total de la silueta y la topología |
| Terreno editable por diseño sin volver al DCC | Target **móvil** con presupuesto ajustado (terreno de Unity es caro — §8) |
| Grandes extensiones con tiles vecinos auto-conectados | El "terreno" es pequeño y estilizado (una malla low-poly rinde y se ve mejor) |

**Híbrido, lo normal en producción:** Terrain para la base del paisaje + **mallas de roca/acantilado** tapando las verticales y **la costura malla-terreno escondida** con rocas/vegetación, nunca peleada ([ver: modelado/entornos-modulares §5]). Caminos y calles precisas: malla/decal encima, no pintura de heightmap (no da bordes limpios).

## 2. Anatomía del sistema Terrain en Unity 6

`GameObject > 3D Object > Terrain` crea **un GameObject** con tres piezas:

| Pieza | Qué es |
|---|---|
| **Terrain** (component) | Renderiza el paisaje desde el heightmap; expone la barra de herramientas y los settings |
| **TerrainData** (asset en disco) | Los DATOS: heightmap, splatmaps/control textures, mapas de detalle, lista de árboles. Reutilizable/versionable |
| **Terrain Collider** (component) | Colisión que calca el heightmap (§9) |

Arranca como un plano grande y plano. La barra del Inspector agrupa los modos: **Sculpt** (altura), **Materials / Paint Texture** (texturas), **Foliage** (Paint Trees + Paint Details), **Neighbor Terrains** (tiles adyacentes con Grouping ID + Auto Connect) y **Custom Brushes**. El terreno es **una sola malla generada** desde el heightmap con LOD interno por `Pixel Error` (§8) — no son miles de objetos.

## 3. El heightmap: esculpir e importar

### Resolución y tamaño (Mesh Resolution en Terrain Settings)

| Setting | Valor / rango (Unity 6) | Nota |
|---|---|---|
| **Heightmap Resolution** | **potencia de dos + 1** (ej. 513, 1025, 2049) | Densidad de la malla de altura; más = más detalle y más memoria/CPU |
| Terrain Width / Length | 1–100 000 u (metros) | Huella en el mundo (X / Z) |
| Terrain Height | 1–10 000 u | Rango vertical: de Y=0 a Terrain Height. El heightmap 0→1 mapea a 0→Height |
| Detail Resolution Per Patch | 8–128, **recomendado 16** | Tamaño del parche de detalle (culling por parche) |
| Detail Resolution | mapa de detalle (grande = más memoria) | Densidad de la grilla de hierba/detalles |

La altura es un valor normalizado 0–1 escalado por Terrain Height: sube Terrain Height y las montañas crecen sin re-esculpir.

### Herramientas de escultura (modo Sculpt)

| Herramienta | Qué hace |
|---|---|
| **Raise or Lower Terrain** | Sube (click) o baja (Shift+click) altura con el brush; el pincel pinta como en 2D |
| **Set Height / Paint Height** | Fija la altura a un valor objetivo (mesetas, plataformas a cota exacta); útil para nivelar |
| **Smooth Height** | Suaviza/promedia — quita picos y aliasing tras esculpir o importar |
| **Stamp Terrain** | **Estampa** una forma (brush/heightmap) sobre la altura actual — sella montañas/cráteres repetibles a partir de una textura de brush |
| **Paint Holes** | Recorta **agujeros** en el terreno (entrada de cueva, precipicio); requiere shader que soporte holes y el collider los respeta (§9) |

**Brushes:** cada tool usa un brush (textura), con **opacity/strength** y **size** en el overlay de atributos. Los **stamps** no son más que brushes de heightmap: montañas, dunas o cráteres pre-hechos que se estampan; se acumulan y se suavizan. El paquete **Terrain Tools** añade más (Bridge, Clone, Terrace, Noise, erosión — §5/§10).

### Importar heightmaps externos (World Machine / Gaea / Houdini)

`Terrain Settings ▸ engranaje ▸ Import Raw / Export Raw`:

| Parámetro | Valor | Nota |
|---|---|---|
| Formato | **RAW** (grayscale 16-bit) | Compatible con casi todo editor de terreno/imagen |
| Depth | **16-bit** (2 bytes) o 8-bit | 16-bit = sin banding en pendientes suaves; usar 16-bit |
| Byte Order | Windows / Mac | Relevante en 16-bit; si el terreno sale "escalonado/roto", suele ser el byte order al revés |
| Resolution / Terrain Size | según el heightmap | Debe cuadrar con la resolución exportada por la herramienta |
| Flip Vertically | on/off | Si el relieve sale espejado en el eje equivocado |

**Flujo real:** modelar el macizo en **World Machine / Gaea / Houdini** (erosión hidráulica, ríos, estratos — imposibles a mano en Unity), exportar heightmap 16-bit + los **splatmaps** (máscaras de pasto/roca/nieve) que la herramienta genera, e importar ambos: el heightmap en Import Raw y los splatmaps como control textures (el **Terrain Toolbox** del paquete Terrain Tools importa/exporta splatmaps y heightmaps en batch — §5). Unity documenta explícitamente este pipeline con Houdini y World Machine; Gaea es del mismo tipo. Detalle de nivel de mención, no un manual de esas apps.

## 4. Terrain Layers y el splatmap (el control map)

### Qué es un Terrain Layer

Un **Terrain Layer** es un **asset reutilizable** (aplicable a varios tiles) que describe una superficie:

| Propiedad | Qué es |
|---|---|
| **Diffuse (Albedo)** | Textura de color base; su canal Alpha depende del pipeline y de si hay Mask Map |
| **Normal Map** + Normal Scale (−1 a 2) | Relieve fino de la superficie; Scale ajusta la fuerza |
| **Mask Map (RGBA)** | **R=Metallic · G=Ambient Occlusion · B=Height · A=Smoothness** (o Density si Diffuse Alpha activo) — un canal RGBA de máscaras como el Mask Map de HDRP Lit, pero **no idéntico**: aquí B=Height (para el height-blend, §5), en el Mask Map genérico de HDRP Lit B=Detail Mask [ver: texturizado/pbr-teoria] |
| Channel Remapping | Reajusta min/max de cada canal RGBA sin re-exportar la textura |
| Tiling: **Size / Offset** | Escala de la textura en el mundo (Size 8 = el tile de textura cubre 8 m). Size distinto por layer = pasto fino, roca grande |

### El splatmap = control texture: cómo se mezclan

- El **primer** Terrain Layer que agregas **flood-fillea** el terreno entero (capa base). Los siguientes se **pintan** con Paint Texture (click/drag), con **Target Strength** y opacity de brush; pintar cruzando bordes mezcla de forma orgánica.
- El motor guarda los pesos en el **control texture (splatmap)**, una textura **RGBA**: **4 pesos de layer por splatmap** (un canal por layer). Los pesos de un texel se **normalizan para sumar 1** → el color final es la mezcla ponderada de las layers presentes ahí ("blend por peso"). Un 5.º layer asigna un **segundo** splatmap.
- **Control Texture Resolution** (Texture Resolutions en settings): la resolución del splatmap. Baja = transiciones borrosas/escalonadas entre materiales; alta = bordes finos pero más memoria y coste de pintado.
- **Base Texture Resolution**: la textura compuesta de baja resolución que el terreno usa **de lejos** (más allá de Base Map Distance, §8) en lugar de mezclar todas las layers per-pixel.
- **Cuántos layers**: "depende de tu render pipeline" (doc de Paint Texture). El mecanismo de 4-por-splatmap es transversal; el **máximo por tile y el coste por grupo extra** es pipeline-dependiente (§6). Regla de producción: **menos layers = más barato**; un paisaje entero suele resolverse con 4–6.

## 5. Blend por altura, pendiente y altitud — la parte que se malentiende

Hay DOS "blends por altura" y se confunden:

| Mecanismo | Qué hace de verdad | NO hace |
|---|---|---|
| **Height-based Blend** (Terrain Lit, §6) | Mezcla por la **altura del material** (canal B del Mask Map) con `Height Transition`: en un texel **gana el layer con mayor height** (grava asomando entre arena) | NO lee la altura del MUNDO ni la pendiente |
| Blend por **peso** (splatmap, §4) | Mezcla suave por los pesos pintados | Es lo que pintas a mano |

**Que la roca aparezca sola en pendientes y la nieve en altura NO es una función nativa del Terrain por pendiente/altitud del mundo.** Vías reales:

| Vía | Cómo | Cuándo |
|---|---|---|
| **Pintar a mano** | Paint Texture: pintas roca en los taludes y nieve en las cimas | Rápido, control total, no se auto-actualiza si re-esculpes |
| **Terrain Tools — Brush Mask Filters** | El paquete añade filtros de máscara de brush (altura, pendiente, concavidad, ruido) que **restringen dónde pinta** el brush → pintas "solo en pendientes > X" | Semi-automático dentro de Unity; requiere el paquete *(confirmar el set exacto de filtros en tu versión del paquete)* |
| **Shader de splat por reglas** (asset) | **MicroSplat / CTS / MapMagic**: shaders que texturizan por **world normal.y (pendiente)** y **world Y (altitud)** automáticamente, con blend por height | Paisaje grande que se re-esculpe seguido; el estándar de la industria para auto-texturing |
| **Terrain Lit custom / Shader Graph** | Un shader que lee `Normal.y` (pendiente) y la posición Y del pixel y mezcla layers por regla | Control propio sin dependencia de asset [ver: vfx-shaders/shader-graph-fundamentos] |

Honestidad: el Terrain Lit de URP **sí** trae Height-based Blend, pero es blend por height del mask map, no por pendiente/altitud. El auto-texturing por pendiente/altitud vive en Terrain Tools (máscaras) o en shaders de terceros.

## 6. El material de terreno en URP: Terrain Lit shader

El terreno se renderiza con un **Material** asignado en Terrain Settings; en URP el default es **Terrain Lit** ("una versión más simple del Lit" — [ver: unity/rendering-urp]).

| Aspecto | Comportamiento (URP Terrain Lit) |
|---|---|
| Blend de layers | Por **pesos del splatmap** (§4), salvo que actives Height-based Blend (§5) |
| **Enable Per-pixel Normal** | Muestrea el normal generado del heightmap **por pixel** (relieve más fino en pendientes). **Requiere Draw Instanced ON** en Terrain Settings |
| Mask Map | Toma **height del canal B** del Mask Map de la layer para el height-blend |
| Normal maps de layer | Cada layer aporta su Normal Map (Normal Scale por layer) sobre la base del terreno |
| **Nº de layers = coste** | Base + **add passes**: pasado el grupo de 4 layers, el terreno se dibuja en pasadas extra → más layers = más draw/pixel work. El máximo por tile es pipeline-dependiente |
| Reflection Probes | Off / Blend Probes / Blend + Skybox / Simple (Terrain Settings) |

Criterio: **el shader más barato que dé el look** (regla general de [ver: unity/rendering-urp]). Muchos layers + per-pixel normal + Draw Instanced es bonito en desktop; en móvil pesa (§8). Los materiales built-in (Standard Terrain) se ven rosados en URP → reasignar Terrain Lit / usar el Render Pipeline Converter [ver: unity/rendering-urp].

## 7. Detail y Tree: hierba, detalles y árboles

Teoría de vegetación (cards, atlas por especie, el enemigo es el **overdraw**, LOD → billboard) en [ver: modelado/entornos-modulares §7]. Aquí, el sistema del Terrain.

### Paint Trees

| Propiedad | Detalle |
|---|---|
| Prototipos | `Edit Trees ▸ Add Tree`: prefabs; **SpeedTree** (`.spm`/`.st8`) o Tree Editor. Exportar a FBX/OBJ **pierde el shader de viento** de SpeedTree |
| Densidad | **Tree Density por brush stroke, no por área** → repetir el trazo en el mismo sitio densifica |
| Variación | Random Tree Rotation (bosque natural con LOD trees), rangos de height/width (0.01–2× del original), Color Variation (`_TreeInstanceColor`) |
| LOD / billboards | SpeedTree usa LOD groups (First = cerca/alta calidad, Last = lejos/billboard, Custom). **Billboard Start** = distancia donde el árbol 3D pasa a billboard; **Fade Length** = transición; **Max Mesh Trees** = tope de árboles 3D visibles |
| Colisión | Los árboles pueden tener collider → `Enable Tree Colliders` del Terrain Collider (default ON, **caro** §9) |
| Viento | Wind Zones + Bend Factor (Tree Editor) / shader de viento (SpeedTree) |

### Paint Details (hierba y detalles)

| Tipo de detalle | Qué es |
|---|---|
| **Grass Textures** | Quads con textura de hierba desde una imagen, sin malla propia; con **Billboard** encaran a la cámara (oculta que son 2D) |
| **Detail Mesh — Instanced Mesh** | Lo recomendado para mallas arbitrarias (piedritas, flores): GPU instancing |
| Detail Mesh — Vertex Lit | Combina instancias en una malla sin GPU instancing |
| Detail Mesh — Grass | Iluminación simplificada como Grass Texture, **se mueve con el viento** |

- **GPU Instancing** (buffers persistentes) mejora CPU/GPU pero **desactiva el ruido de color Healthy/Dry** y exige shader compatible.
- **Distribución**: Perlin noise (Noise Seed / Noise Spread) para tamaño/color; **Position Jitter 0–100%** (ordenado→caótico); **Detail Density** escala instancias.
- **Coste real = overdraw + culling por parche** ([ver: modelado/entornos-modulares §7]): la hierba densa vive **cerca** (Detail Distance corta, §8); lejos no se dibuja.

## 8. Rendimiento del terreno (y el caso móvil)

Palancas, en orden de impacto. Cifras exactas del panel Terrain Settings de Unity 6:

| Palanca | Setting | Efecto |
|---|---|---|
| **Draw Instanced** | Terrain Settings | Rendering instanciado del terreno → menos CPU. **Necesario** para Per-pixel Normal (§6). Actívalo casi siempre |
| **Pixel Error** | 1–200 (aprox) | LOD de la malla del terreno: **más alto = más simplificación** (más barato, más "flota" el relieve de lejos); el mínimo que el juego tolere |
| **Base Map Distance** | metros | Más allá, el terreno usa la Base Texture compuesta en vez de mezclar layers per-pixel → **bajarla** ahorra mucho fill |
| Heightmap / Control Texture Resolution | §3/§4 | Bajarlas reduce memoria y coste de mezcla; suben con el tamaño real del terreno, no "por si acaso" |
| Nº de Terrain Layers | §4/§6 | Cada grupo de 4 = pasada extra; recórtalo (4–6 típico) |
| **Detail Distance / Density** | Tree & Detail Objects | Distancia de culling de hierba/detalle y factor de densidad — las palancas #1 del coste de foliage |
| **Tree Distance / Billboard Start / Max Mesh Trees** | Tree & Detail Objects | Cuántos árboles 3D antes de billboard y cuántos visibles |
| Cast Shadows | Off/On/Two-Sided/Shadows Only | El terreno proyectando sombra es caro; evalúa Off en móvil |

**Móvil: el terreno de Unity es caro.** El splat blending per-pixel, muchas layers, per-pixel normal, la hierba con overdraw y las sombras del terreno pegan fuerte en GPUs tile-based (TBDR) [ver: movil/unity-movil-rendimiento], [ver: movil/unity-movil-graficos]. Consecuencia práctica:

- En móvil, **a menudo una malla de terreno simple (low-poly, 2–3 layers por vertex blend) rinde y se ve mejor** que Unity Terrain (§10) [ver: movil/arte-movil].
- Si usas Terrain: pocas layers, Detail/Tree Distance cortas, Draw Instanced ON, sombras del terreno recortadas, Base Map Distance corta, y **medir en el device real más débil** — los draw calls/fillrate del editor no representan una GPU móvil ([ver: unity/rendering-urp], [ver: movil/unity-movil-rendimiento]).

## 9. Colliders y gameplay sobre el terreno

| Aspecto | Detalle |
|---|---|
| **Terrain Collider** | Calca la geometría del heightmap; **el collider más preciso** para terreno. Necesita el TerrainData |
| Physics Material | Fricción/rebote de la superficie; sin él, defaults del proyecto |
| **Enable Tree Colliders** | Genera colliders de los árboles pintados; **default ON** y **más caro** — apágalo si el gameplay no lo necesita |
| Holes | Paint Holes (§3) recorta el collider también → caes por el agujero (entrada de cueva) |
| Overrides de layer | Include/Exclude Layers para controlar qué colisiona con el terreno |

**Colocar cosas sobre el terreno por código** (spawns, props, IA): no adivines la Y — muestrea la altura real.

```csharp
// Altura del terreno en un punto del mundo (independiente de la física)
Terrain t = Terrain.activeTerrain;
float y = t.SampleHeight(worldPos) + t.transform.position.y;

// O por raycast contra el Terrain Collider (respeta holes)
if (Physics.Raycast(worldPos + Vector3.up * 100f, Vector3.down, out var hit, 200f))
    spawnPos = hit.point;
```

- **NavMesh**: el terreno se marca Navigation Static y se hornea como cualquier geometría; los holes y las pendientes definen lo navegable (pendiente máx navegable / cómoda: [ver: modelado/entornos-modulares §6], [ver: gamedev/level-design]).
- **Física**: `SampleHeight` / `TerrainData.GetInterpolatedHeight` no dependen del collider; el raycast sí (y respeta holes). Usa el que corresponda al caso.

## 10. Alternativas al Terrain de Unity

| Alternativa | Cuándo | Cómo |
|---|---|---|
| **Terreno modelado a mano** (Blender) | Control artístico total, estilizado, **móvil**, o hace falta voladizo/cueva | Sculpt del relieve + retopo/decimate → malla low-poly; texturizar con **tileables + trim** ([ver: modelado/entornos-modulares §4], [ver: texturizado/atlas-trim-optimizacion]) y **vertex-blend shader** para mezclar 2–3 materiales por vertex color. Exportar como cualquier malla [ver: blender/import-export]. La costura con el resto se esconde igual (§1) |
| **Assets de terreno** | Paisaje grande con auto-texturing y erosión sin construir el shader | **MicroSplat/CTS** (shaders de splat por pendiente/altitud, §5), **Gaia/MapMagic** (generación procedural), **Terrain Tools** oficial (erosión, brush masks, Terrain Toolbox). Verificar coste en el target antes de casarse con uno |
| **Heightmap externo → Unity Terrain** | Realismo de erosión/ríos | World Machine/Gaea/Houdini → RAW 16-bit + splatmaps → Import Raw (§3). Lo mejor de ambos: relieve realista, edición posterior en Unity |

Regla: si el "terreno" es chico o estilizado, **una malla low-poly casi siempre gana** al Terrain de Unity en control y en coste móvil. El Terrain brilla en extensiones grandes con edición por diseño.

## Reglas prácticas

1. Terreno solo para lo que un heightmap puede (colinas/planicies); cuevas, voladizos, verticales limpias y arquitectura son mallas [ver: modelado/entornos-modulares §5].
2. Esconde la costura malla-terreno con rocas/vegetación; nunca la pelees.
3. Heightmap Resolution en **potencia de 2 + 1** (513/1025/2049); súbela por el tamaño real del terreno, no por defecto.
4. Esculpe con Raise/Lower + Set Height, y **Smooth** para matar picos/aliasing tras esculpir o importar.
5. Importa relieve serio (erosión, ríos) desde World Machine/Gaea/Houdini como **RAW 16-bit**; si sale escalonado, revisa Byte Order/Flip.
6. Primer Terrain Layer = capa base (flood-fill); los demás se pintan; el splatmap mezcla por **peso normalizado** (4 layers por control texture RGBA).
7. **Menos layers = más barato**: apunta a 4–6; cada grupo de 4 añade pasada. Size de tiling distinto por layer para escala natural.
8. Roca-en-pendiente / nieve-en-altitud **no es nativo por pendiente**: píntalo, usa Brush Mask Filters (Terrain Tools) o un shader de splat (MicroSplat/CTS/Shader Graph). Height-based Blend mezcla por height del Mask Map, no por altitud del mundo.
9. URP: material **Terrain Lit**; Per-pixel Normal exige **Draw Instanced ON**. Nada de Standard Terrain built-in (sale rosado).
10. Draw Instanced ON casi siempre; Pixel Error al máximo que el juego tolere; Base Map Distance corta.
11. Árboles: SpeedTree con LOD→billboard (Billboard Start/Fade Length/Max Mesh Trees); densidad es por trazo, no por área.
12. Hierba/detalle: Instanced Mesh + Detail Distance corta; el coste es **overdraw**, no polys [ver: modelado/entornos-modulares §7].
13. `Enable Tree Colliders` default ON y caro: apágalo si el gameplay no lo pide.
14. Coloca objetos por `SampleHeight`/raycast, nunca adivinando la Y; el raycast respeta los holes.
15. NavMesh: terreno Navigation Static + bake; holes y pendientes definen lo navegable [ver: gamedev/level-design].
16. **Móvil:** el Terrain de Unity es caro — evalúa una malla low-poly con vertex-blend antes de usarlo; si lo usas, recorta layers/distancias/sombras y **mide en el device real** [ver: movil/unity-movil-rendimiento].
17. TerrainData es el asset con los datos: versiónalo y no lo dupliques por accidente entre escenas [ver: unity/assets-pipeline-git].
18. Valida SIEMPRE en el engine con la cámara y luz del juego, recorriéndolo con el controller — no en un screenshot del editor.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| "Height-based Blend pondrá roca en las pendientes solo" | No: mezcla por height del Mask Map, no por pendiente/altitud del mundo. Pinta, usa brush masks o un shader de splat (§5) |
| Heightmap importado sale escalonado o roto | Byte Order al revés o 8-bit: reimporta RAW **16-bit** con el Byte Order correcto; Flip si está espejado |
| Terreno "flota"/se deforma de lejos | Pixel Error demasiado alto: bájalo hasta que el relieve lejano aguante |
| Transiciones de textura borrosas/escalonadas | Control Texture Resolution baja: súbela (cuesta memoria) o repinta con brush más fino |
| Materiales del terreno rosados en URP | Standard Terrain built-in en proyecto URP: asignar **Terrain Lit** / Render Pipeline Converter |
| Per-pixel Normal activado y no cambia nada | Falta **Draw Instanced ON** en Terrain Settings (requisito) |
| 10+ layers y el terreno se arrastra | Cada grupo de 4 = pasada extra; recorta a 4–6, agrupa materiales |
| FPS al piso en móvil "solo por el terreno" | Splat per-pixel + hierba (overdraw) + sombras del terreno; recorta todo o pasa a malla low-poly; medir en device real [ver: movil/unity-movil-rendimiento] |
| Hierba/árboles hasta el horizonte matan el frame | Detail Distance / Tree Distance / Billboard Start cortas; Density baja |
| Personajes/props flotando o clavados en el suelo | No adivinaste la Y: `SampleHeight` o raycast contra el Terrain Collider |
| Físicas lentas con muchos árboles | `Enable Tree Colliders` ON sin necesidad: apágalo |
| SpeedTree sin viento tras exportar | Se exportó a FBX/OBJ (pierde el shader de viento): usar `.spm`/`.st8` |
| Caminos con bordes sucios pintados en el heightmap | El heightmap no da bordes limpios: malla/decal de camino encima [ver: modelado/entornos-modulares §5] |
| Duplicar la escena y editar "otro" terreno cambia ambos | Comparten el mismo **TerrainData** asset: duplica el TerrainData si quieres divergir |
| "Listo" = el terreno se ve bien en el editor | No: recorrido con el controller real, en el device más débil del target, con la luz del juego |

## Fuentes

- **Unity Manual — Terrain (Using Terrains / Creating and editing Terrains)** — docs.unity3d.com (6000.2) — Unity Technologies — crear Terrain (component + TerrainData), modos Sculpt/Materials/Foliage/Neighbor/Custom, brushes y overlays de opacity/size.
- **Unity Manual — Terrain Settings** — docs.unity3d.com (6000.2) — Grouping ID/Auto Connect, **Draw Instanced**, **Pixel Error**, **Base Map Distance**, Cast Shadows, Reflection Probes; Mesh Resolution (Width/Length 1–100 000, Height 1–10 000, Detail Res Per Patch 8–128 rec. 16); **Heightmap Resolution = potencia de 2 + 1 (513)**; Control/Base Texture Resolution; Tree & Detail Objects (Detail/Tree Distance, Density, Billboard Start, Fade Length, Max Mesh Trees); Wind.
- **Unity Manual — Terrain Layers (class-TerrainLayer)** — docs.unity3d.com (6000.2) — asset reutilizable; Diffuse/Normal (Normal Scale −1..2) / **Mask Map RGBA = Metallic/AO/Height/Smoothness (A=Density con Diffuse Alpha)**, Channel Remapping, Tiling Size/Offset; relación con el material del terreno.
- **Unity Manual — Paint Texture tool** — docs.unity3d.com (6000.2) — el primer layer flood-fillea; pintado y blend orgánico; "**el número de Terrain Layers por tile depende del render pipeline**" (→ Rendering performance).
- **Unity Manual — Import/Export heightmaps (Raw)** — docs.unity3d.com (6000.2) — Import Raw/Export Raw, **RAW 16-bit grayscale**, Depth 8/16-bit, Byte Order, Flip; flujo externo **Houdini/World Machine → heightmap → Unity**.
- **Unity Manual — Paint Trees** — docs.unity3d.com (6000.2) — prototipos SpeedTree/Tree Editor, densidad por trazo, Random Rotation/scale, Color Variation, LOD First/Last/Custom, billboards, viento (`.spm`/`.st8` conservan el shader de viento; FBX/OBJ lo pierden).
- **Unity Manual — Paint Details (grass & detail meshes)** — docs.unity3d.com (6000.2) — Grass Textures vs Detail Mesh (Instanced Mesh / Vertex Lit / Grass), Billboard, GPU Instancing (desactiva color noise), Perlin noise seed/spread, Position Jitter 0–100%, Detail Density.
- **Unity Manual — Terrain Collider (class-TerrainCollider)** — docs.unity3d.com (6000.2) — collider que calca el heightmap (el más preciso), Physics Material, **Enable Tree Colliders (default ON, más caro)**, holes, include/exclude layers.
- **URP — Terrain Lit shader** — docs.unity3d.com (URP, 6000.x) — Unity Technologies — "versión simple del Lit"; blend por **pesos del splatmap**; **Enable Height-based Blend** (renderiza el layer de mayor **height del Mask Map**, con Height Transition — NO altitud del mundo); **Enable Per-pixel Normal requiere Draw Instanced**.
- **Unity — Terrain Tools package (com.unity.terrain-tools)** — docs.unity3d.com (Packages) — herramientas de erosión, sculpting y **Brush Mask Filters**; **Terrain Toolbox** para crear/importar terreno desde presets/heightmaps y importar/exportar splatmaps en batch. *(El set exacto de brush mask filters — altura/pendiente/concavidad/ruido — confirmar en la versión del paquete instalada.)*
- **Bases sintetizadas de El Estudio:** [ver: modelado/entornos-modulares] (terreno vs mallas §5, vegetación §7, optimización §8, escala/pendientes §6); [ver: unity/rendering-urp] (URP, Terrain Lit como Lit simplificado, Draw Instanced/SRP Batcher, materiales rosados); [ver: unity/rendimiento-unity]; [ver: movil/unity-movil-rendimiento] + [ver: movil/unity-movil-graficos] + [ver: movil/arte-movil] (coste móvil); [ver: texturizado/pbr-teoria] (empaque Mask Map); [ver: pipeline-3d/receta-kit-modular] (la otra mitad del entorno: arquitectura modular).
- *Nota de honestidad: el **4-layers-por-splatmap RGBA** y el **add-pass por grupo extra** son la arquitectura estándar de control texture de Unity, coherente con TerrainData/alphamaps; el **máximo exacto de layers por tile y el coste por pasada son pipeline/versión-dependientes** — la doc de Paint Texture lo remite explícitamente a "tu render pipeline". Verificar el número concreto en la versión de URP/HDRP del proyecto antes de fijarlo como límite.*
