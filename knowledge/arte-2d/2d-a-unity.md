# Arte 2D a Unity: export, import e integración

> **Cuando cargar este archivo:** al terminar de PRODUCIR arte 2D (pixel art, sprites HD, hojas de animación, tilesets, atlas de personaje) y llevarlo a un proyecto Unity 6 / URP 2D — para exportarlo bien desde Aseprite, importarlo sin retoques y verificar que entra crujiente, batcheado y animable. Es el puente de producción-arte 2D; la teoría de dibujo vive en [ver: pixel-art], [ver: sprites-produccion], [ver: animacion-2d], [ver: tilesets-mundos] y [ver: aseprite-flujo]. El **contrato de spec** (PPU/pivot/formato congelados el día 1) y la teoría de import/cámara/atlas/sorting ya están en [ver: pipeline/arte-a-unity]: este archivo NO lo repite, lo asume y lo baja a la práctica del artista 2D.

## 1. El bucle real: dibujar → exportar → importar → verificar EN juego

El asset no está "listo" cuando se ve bien en Aseprite. Está listo cuando aparece nítido, al tamaño correcto, batcheado y sin flicker en la escena visual-target con la cámara REAL del juego [ver: gamedev/arte-direccion]. El error nº1 del arte 2D es aprobar mirando el editor de arte. La cadena de decisiones que amarra todo se congela ANTES del primer asset de producción y vive en el style guide [ver: pipeline/arte-a-unity §1]:

| Decisión (congelar día 1) | Pixel art | 2D HD (vectorial/pintado) |
|---|---|---|
| **Densidad / PPU** | UN tamaño de tile (16 o 32); PPU = tile | UN PPU global (típico 100) |
| Resolución de referencia | 320×180 / 640×360 | 1920×1080 (o 1080×1920 portrait) |
| Canvas del personaje | Alto en px fijo (ej. 32 o 48 px) | Alto en px fijo (ej. 512 px) |
| Filtro | Point (obligatorio) | Bilinear |
| Escalado | SOLO enteros (2×, 3×, 4×); jamás no-entero cocido | Uniforme; sin cocer escala en la imagen |
| Formato de entrega | PNG-32 sin AA ni semitransparencias sueltas | PNG-32 con alpha real |

**Números de producción de referencia** (práctica común, no dogma — calibrar al proyecto). Fijan el tamaño del canvas y el conteo de frames ANTES de dibujar, para presupuestar el arte:

| Elemento | Pixel art típico | Nota |
|---|---|---|
| Tile / celda | 16×16 o 32×32 px | El PPU sale de aquí |
| Personaje (alto) | 16–48 px (mundo pequeño) hasta 64–96 px (detalle) | UN alto de referencia para todos los personajes |
| Idle | 2–4 frames | Respiración/parpadeo |
| Run/Walk | 6–8 frames | Ciclo cerrado (último enlaza con el primero) |
| Attack | 3–6 frames | Con anticipación + impacto + recuperación [ver: animacion-2d] |
| Hurt/Death | 1–2 / 4–6 frames | Muerte más larga si hay disolución |
| FPS de gameplay | 8–12 fps (Samples del clip) | No 60: el pixel art se lee mejor "a saltos" |

**Paleta y color (decisión día 1, se hornea en el PNG).** Unity no maneja paletas: el color va cocido en la textura, así que la coherencia se resuelve en Aseprite. Una sola paleta por proyecto (o por bioma), fijada en el style guide [ver: pixel-art]. Bajar paletas de [lospec.com/palette-list](https://lospec.com/palette-list) (base de miles de paletas; descargas en PNG, JASC PAL, Photoshop `.ASE`, GIMP `.GPL`, `.HEX` — verificado) e importarlas a Aseprite (`.gpl`/`.ase`/`.png`). Con la paleta cargada, `Sprite ▸ Color Mode ▸ Indexed` bloquea el trabajo a esos colores. Paletas de referencia por conteo: **PICO-8** (16), **Sweetie-16** (16), **Endesga-32** (32), **AAP-64/Resurrect-64** (64) — a más colores, más suave el degradado y más pesa la disciplina de estilo.

## 2. Export desde Aseprite: qué archivo entregar

Regla base: **entregar sprites al tamaño final EXACTO** (Aseprite: `Scale 100%`; nunca "ya lo escalas en Unity") y **sin padding cocido** en la imagen (el atlas pone el suyo). `File ▸ Export Sprite Sheet` es la vía (verificado en docs Aseprite: exporta capas visibles o una capa, y frames por tags). Automatizable por línea de comandos (verificado, Aseprite CLI):

| Flag CLI | Qué hace | Uso para Unity |
|---|---|---|
| `--sheet out.png` | Escribe la hoja | Salida a la carpeta de arte del repo |
| `--sheet-type` | `horizontal` \| `vertical` \| `rows` \| `columns` \| `packed` | **`rows`/`columns`** para grid regular (Unity slicea por grid); `packed` solo si acompaña `--data` |
| `--data out.json` | Metadatos de frames/tamaños | Fuente del slicing y de los frames de animación |
| `--format` | `json-hash` (default) \| `json-array` | `json-array` conserva orden de frames |
| `--list-tags` | Mete `frameTags` (nombre, from, to, direction) en el JSON | Un tag = una animación (Idle/Run/Jump) |
| `--list-slices` | Mete `slices` (incl. pivot por slice) en el JSON | Pivot y 9-slice sin re-medir en Unity |
| `--split-layers` | Una capa = un archivo | Separar personaje base / equipo / normal map |
| `--split-tags` | Un tag = un archivo | Un clip por archivo cuando conviene |
| `--trim` | Recorta bordes vacíos | ⚠️ **NO** en grid regular: rompe el tamaño de celda uniforme |
| `--border-padding` / `--shape-padding` / `--inner-padding` | Márgenes externo / entre frames / dentro del frame | Dejar el padding al Sprite Atlas de Unity; mantener 0 en la hoja de grid |
| `--scale N` | Reescala TODO por N | Casi nunca: entrega a 1× y deja el upscale a la cámara |

- **Grid regular vs packed:** para pixel art de personaje, exportar con `--sheet-type rows` o `columns`, **misma celda para todos los frames**, `--trim` OFF y padding 0 → Unity lo sliceza por grid en un paso (§4). El `packed` ahorra textura pero exige que Unity lea el `--data` JSON para recolocar, más frágil en el pipeline de arte.
- **Frames sueltos vs hoja:** para animación por swap en Unity, ambos valen. Hoja + slice por grid es lo más simple; frames sueltos (`--split-tags` o export por frame) si el equipo prefiere un PNG por frame.
- **Tags = animaciones:** nombrar los tags en Aseprite EXACTO como los clips de Unity (`Idle`, `Run`, `Jump`, `Hurt`). Direcciones verificadas: `Forward`, `Reverse`, `Ping-pong` (la de Aseprite; Unity no la lee — el loop/pingpong se recrea en el Animator).
- **Scripting Lua** (aseprite.org/api) existe para batch más complejo que la CLI (procesar por capas, generar variantes); no inventar operadores sin verificarlos contra la doc — cuando la CLI alcanza, usar la CLI (más estable en CI). Detalle del flujo Aseprite en [ver: aseprite-flujo].

**El JSON de datos y qué lee Unity.** Con `--data --list-tags --list-slices`, Aseprite emite (forma verificada del CLI): `frames` con `frame{x,y,w,h}` por celda, y `meta` con `size`, `frameTags[{name,from,to,direction}]` y `slices[{name, keys:[{bounds, pivot}]}]`. Unity **no** lee este JSON de fábrica: se usa (1) como referencia humana para el slicing por grid, o (2) lo consume un **AssetPostprocessor** propio que aplica sub-rects, pivots y rangos de tags al importar la hoja [ver: unity/assets-pipeline-git]. Sin ese puente, el pivot y los tags se recrean a mano en Unity. Un archivo por personaje mantiene el JSON manejable.

## 3. Import en Unity: settings de textura (sprite)

Al caer en Unity, cada PNG pasa por el Texture Importer. Valores verificados (Unity 6000.2, `Texture Type = Sprite (2D and UI)`). El detalle de plataforma y la automatización con Preset/AssetPostprocessor están en [ver: unity/assets-pipeline-git §1] — aquí la tabla que el artista debe reconocer:

| Setting | Pixel art | 2D HD | Nota verificada |
|---|---|---|---|
| **Texture Type** | Sprite (2D and UI) | Sprite (2D and UI) | Obligatorio para que sea sprite |
| **Sprite Mode** | Single / Multiple | Single / Multiple | Multiple = hoja con varios sprites (§4) |
| **Pixels Per Unit** | = tamaño de tile (16/32) | 100 (o el global) | "px de ancho/alto que equivalen a 1 unidad de mundo" |
| **Mesh Type** | Full Rect | Tight (o Full Rect en 9-slice) | Sprites **<32×32 px usan Full Rect automáticamente** |
| **Filter Mode** | **Point (no filter)** | Bilinear | Point = píxel crujiente; Bilinear = borroso en pixel art |
| **Compression** | None | Normal (override ASTC en móvil) | None evita artefactos de bloque en pixel art |
| **Generate Mip Maps** | Off | Off en 2D estándar | Mips = sprite borroso al alejar; 2D no las necesita |
| **sRGB (Color Texture)** | On | On | Off SOLO en máscaras/normal maps (datos, no color) |
| **Alpha Source** | Input Texture Alpha | Input Texture Alpha | El PNG ya trae alpha real |
| **Alpha Is Transparency** | On | On | Dilata el color bajo el alpha → sin halo oscuro al filtrar |
| **Wrap Mode** | Clamp | Clamp (Repeat en texturas tileables) | Repeat solo para patrones seamless |
| **Read/Write** | Off | Off | On solo si lees píxeles por código (duplica RAM) |

La tríada innegociable de pixel art nítido: **Point + Compression None + PPU = tile**. Faltando cualquiera → borroso o con bandas. El look estable en movimiento lo cierra la Pixel Perfect Camera (§6).

## 4. Sprite Editor: slicing y pivots

`Sprite Mode = Multiple` habilita el **Sprite Editor** (botón en el importer, paquete `com.unity.2d.sprite`). Ahí se corta la hoja en sub-sprites y se fija el pivot de cada uno.

**Slice (menú Slice del editor):**

| Type | Cuándo | Parámetros |
|---|---|---|
| **Grid By Cell Size** | Frames de tamaño conocido (ej. 32×32) — el caso normal de pixel art | Pixel Size X/Y, Offset, Padding |
| **Grid By Cell Count** | Sé cuántas columnas×filas hay, no el px exacto | Column & Row |
| **Automatic** | Sprites de tamaños irregulares en una hoja HD | Detecta islas por alpha; revisar a mano |

- **Method del slice:** `Delete Existing` (borra y recorta de cero — usar al re-slicear una hoja limpia), `Smart` (intenta conservar/ajustar sprites ya definidos) y `Safe` (solo añade los nuevos, no toca los existentes). En una hoja de grid nueva: Delete Existing. Al re-importar una hoja editada manteniendo sub-sprites: Safe.
- **Pivot por sprite:** el dropdown Pivot ofrece presets (Center, Bottom, Bottom Left…) o **Custom**. Personajes de plataformas/top-down: pivot en los **pies** (Bottom o Custom) para que el sorting por Y y la posición del transform sean coherentes [ver: pipeline/recetas-generos]. Pixel art: `Pivot Unit Mode = Pixels` snapea el pivot a una **coordenada de píxel exacta** — el mismo píxel en todos los frames o el personaje "salta" al animar.
- **Consistencia entre frames = ley:** todos los frames del mismo canvas y el mismo pivot. Si en Aseprite el personaje se movió dentro del canvas entre frames, en Unity "vibra". Slice por grid con celda fija lo garantiza; por eso `--trim` OFF en la hoja (§2).
- **Slices de Aseprite → pivots:** si la hoja se exportó con `--list-slices` y el pivot marcado en cada slice, ese dato viaja en el JSON; en Unity aún hay que aplicar el pivot (a mano o con un AssetPostprocessor que lea el JSON) [ver: unity/assets-pipeline-git]. El editor de Unity no importa el pivot de Aseprite automáticamente sin ese puente.

## 5. Sprite Atlas: empacar y bajar draw calls

Los sprites se entregan **sueltos**; el atlas lo arma el proyecto (nunca pedir al artista un spritesheet pre-empacado sin datos de recorte). Un Sprite Atlas combina varias texturas en una → **una draw call en vez de muchas** (verificado). Decisión de arte-producción, no por asset:

- Uno por **contexto de uso simultáneo**: `Player`, `UI_HUD`, uno por bioma/tileset. Sprites que se dibujan juntos en el mismo frame → mismo atlas = batchean.
- Settings clave (verificados): **Objects for Packing** (qué entra), **Include in Build**, **Allow Rotation** (OFF en UI para no rotar iconos), **Tight Packing** (OFF si va a servir de 9-slice), **Padding** (deja el margen que evita bleeding entre vecinos al filtrar).
- **Type: Master / Variant** — el Variant referencia a un Master a otra escala (ej. atlas a media resolución para gama baja) sin re-exportar arte.
- **Tamaño del atlas:** vigilar el Max Texture Size resultante; en móvil de gama baja mantener las páginas ≤ 2048×2048 (partir en varios atlas si no cabe) y usar override ASTC en el import de las texturas [ver: unity/assets-pipeline-git].
- **No sobre-agrupar:** meter en un atlas sprites que nunca se dibujan en el mismo frame no ahorra draw calls y sí carga textura de más en memoria; agrupar por co-ocurrencia real en pantalla.
- Deep dive (V2, Sprite Packer modes, trampas con Addressables, presupuesto): [ver: unity/assets-pipeline-git §2] y [ver: unity/rendimiento-unity]. Verificar que batchea con el Frame Debugger antes de dar por buena una escena.

## 6. Pixel Perfect y sorting: lo justo (el detalle está en las hermanas)

- **Pixel Perfect Camera** (incluida en URP, se añade a la Main Camera): da el look crujiente y estable en movimiento. Su **Asset Pixels Per Unit debe COINCIDIR** con el PPU de todos los sprites, y su Reference Resolution con la del arte (320×180…). Tabla completa de propiedades (Crop Frame, Grid Snapping, Upscale Render Texture, Filter Mode) y el conflicto con Cinemachine: [ver: pipeline/arte-a-unity §3]. Consecuencia para el artista: **un solo PPU en todo el proyecto**; un sprite a 48 px conviviendo con otros a 32 px rompe el pixel-perfect.
- **Sorting:** Sorting Layers (`Background → Props → Enemies → Player → FX → UI`) + Order in Layer; personaje multi-sprite bajo un **Sorting Group**; top-down "el de abajo tapa" = Transparency Sort Axis (0,1,0) en el **2D Renderer Data** + Sprite Sort Point = Pivot con pivot en los pies. Orden de prioridad completo: [ver: unity/rendering-urp] y [ver: pipeline/recetas-generos]. Decisión de arte: en qué sorting layer cae cada categoría, documentado el día 1.
- **Eje de profundidad (Z) en 2D:** en un juego 2D el orden lo mandan Sorting Layer / Order in Layer / eje de sort, **no la Z del transform** — mover un sprite en Z para "ponerlo delante" pelea con el pixel-perfect y con la cámara. Mantener Z=0 y ordenar por capas; usar Z solo para parallax deliberado de fondos.

## 7. Animación 2D: los dos caminos y qué entrega el arte

Unity anima 2D de dos formas; elegir por proyecto ANTES de producir la animación. El detalle de máquina de estados/parámetros está en [ver: unity/animacion-unity]; los principios de animación en [ver: animacion-2d].

| | **A) Sprite swap (frame a frame)** | **B) Skeletal (bones)** |
|---|---|---|
| Qué es | Cambiar el Sprite renderizado por keyframes | Deformar un sprite recortado por huesos |
| Arte que se entrega | **Cada frame dibujado** (hoja/frames): 4–8 frames típicos por ciclo de pixel art | **UN personaje en capas** (.psb): cabeza, torso, brazos… separados |
| Herramienta | Aseprite → hoja + tags | Photoshop/Aseprite por capas → **.psb** |
| Import Unity | Multiple + slice; keys de sprite en el Animator, o **Sprite Resolver** | **PSD Importer** (`com.unity.2d.psdimporter`) genera un Prefab de sprites por capa |
| Componentes | SpriteRenderer + Animator; opcional Sprite Library / Sprite Resolver | **Sprite Skin** + Skinning Editor (huesos, pesos) + Animator |
| Cuándo | Pixel art, look clásico, pocos frames | HD, muchas animaciones desde un solo dibujo, deformación fluida |
| Coste de arte | Alto por animación (redibujar frames) | Alto de rig una vez, barato por animación nueva |

**A) Sprite swap — deliverable y montaje:**
- Entregar la hoja con **tags = clips** y frames de tamaño/pivot idénticos (§2, §4). En Unity: arrastrar los frames de un tag a la escena crea un clip + Animator automáticamente, o poner keyframes de `Sprite` en el Animation window.
- **Sprite Library + Sprite Resolver** (verificado, paquete 2D Animation): el **Sprite Library Asset** guarda sprites en **Categories** y **Labels**; el **Sprite Library component** dice qué asset usa el GameObject y el **Sprite Resolver component** pide un sprite por Category+Label. Sirve para (1) animar cambiando la Label por keyframe y (2) **variantes** (skins) sin duplicar clips: mismo clip, distinto Sprite Library.
- Frame rate: fijar el **Samples** del clip para que 4–8 frames den el tempo buscado (pixel art suele ir a 8–12 fps de gameplay, no 60). Loop/ping-pong se marca en el clip de Unity (la dirección del tag de Aseprite es referencia, no se importa).

**B) Skeletal — deliverable y montaje:**
- Entregar **.psb** con cada parte en su capa y con solape suficiente en las articulaciones (para que el hueso no muestre bordes al doblar). El **PSD Importer** genera un prefab de sprites basado en las capas del archivo (verificado). `.psb` = mismas funciones que `.psd` con soporte de imágenes mucho más grandes (verificado).
- Rig en el **Skinning Editor** (dentro del Sprite Editor del .psb): crear huesos, auto-geometría, pintar pesos; el **Sprite Skin** en runtime deforma la malla del sprite. Animar los huesos en el Animation window.
- Regla: skeletal para personajes con MUCHAS animaciones desde un dibujo; para 3 enemigos de 4 frames, sprite swap es más barato de principio a fin.

## 8. Tilesets y mundos: preparar el arte para Tilemap

La IMPLEMENTACIÓN (Grid, Tile Palette, Rule Tiles, TilemapCollider2D + CompositeCollider2D, procgen) está a fondo en [ver: pipeline/recetas-generos]. Aquí lo que el ARTE debe garantizar para que ese sistema funcione:

- **Grid alineado:** todos los tiles al **mismo tamaño de celda** (16 o 32, = PPU) y dibujados dentro de la celda. Importar el tileset como **Multiple + Grid By Cell Size** con esa celda. Un tile de 17 px o dibujado a caballo entre celdas rompe el snap.
- **Bordes seamless:** los tiles que se repiten deben teselar sin costura visible; los bordes/esquinas del terreno se dibujan pensando en cómo se encuentran con los vecinos.
- **Autotiling (Rule Tile):** en vez de dibujar cada combinación a mano, entregar el **set de bordes/esquinas** que un Rule Tile necesita. Cuánto arte hace falta según la ambición del terreno:

  | Enfoque | Piezas a dibujar | Cubre |
  |---|---|---|
  | Blob de 47 (canónico) | 47 tiles | Todas las combinaciones de 8 vecinos, esquinas interiores incluidas |
  | Wang / 16-tile "borde" | 16 tiles | Bordes de 4 lados sin esquinas interiores (terreno simple) |
  | Rule Tile con Rotated + Mirror | ~5–13 reglas base | Lo mismo que el blob, dejando que Unity rote/espeje en runtime [ver: pipeline/recetas-generos] |

  Decidir con el implementador qué enfoque ANTES de dibujar: el Rule Tile con Rotated+Mirror ahorra ~75% del arte de tiles frente al blob a mano.
- **Sprite Atlas del bioma:** los tiles de un mapa comparten atlas para no romper el batching [ver: unity/rendimiento-unity].
- **Pivot y Point:** mismos settings de pixel art (§3); Point Filter también en tiles o se ven bordes borrosos en las uniones.
- Tiles animados (agua, antorchas): frames como sprites → **Animated Tile** / regla Animation del Rule Tile [ver: tilesets-mundos].

## 9. Luces 2D: qué cambia en el arte

El sistema de Light 2D (URP 2D Renderer), tipos de luz (Global, Spot, Freeform, Sprite), Blend Styles, ShadowCaster2D y la regla "una Global por sorting layer" están verificados y a fondo en [ver: unity/rendering-urp §Luces 2D]. Implicaciones para el ARTE 2D:

| Look | Material del sprite | Qué entrega el arte |
|---|---|---|
| **Unlit** (color plano, el arte YA trae su luz) | Sprite-Unlit-Default | Solo el sprite; las luces 2D no lo tocan. Default de la mayoría de pixel art |
| **Lit** (las luces del motor lo iluminan) | Sprite-Lit-Default | Sprite + opcional **normal map** y **mask map** |

- **Decisión de estilo:** si el pixel art ya tiene sombreado dibujado (lo normal), va **Unlit** y las luces se usan como ambiente/glow, no para modelar volumen. Meter luces Lit sobre arte que ya trae su propia luz "aplana" el dibujo. El pixel-art lit con normal maps es un look deliberado, no el default.
- **Normal map 2D:** para que un sprite reaccione a la dirección de la luz, se entrega un **normal map** del sprite y se asigna como **Secondary Texture** con nombre `_NormalMap` en el Sprite Editor (pestaña **Secondary Textures**). Se puede generar (Aseprite, Sprite DLight u otras herramientas) pero es trabajo extra por sprite — presupuestarlo. El normal map va con **sRGB OFF** (es dato, no color) [ver: unity/assets-pipeline-git].
- **Mask map (opcional):** un `_MaskTex` como Secondary Texture marca qué zonas del sprite reciben qué Blend Style de luz (ej. solo la lámpara emite glow). Es un mapa de datos, no de color: sRGB OFF también.
- **Emisión/glow:** el pixel art no tiene canal de emisión como el 3D; el "glow" se logra con luces 2D (Sprite Light sobre la zona) o Bloom de post-proceso alimentado por colores muy claros del sprite [ver: unity/rendering-urp].
- ⚠️ Gotcha clásico: al pasar a 2D Renderer todo se ve **negro** porque los materiales Lit no tienen luz — falta una Global Light 2D en los sorting layers [ver: unity/rendering-urp]. Si el juego no usa luces, poner Default Material Type = **Unlit** en el 2D Renderer Data.

## 10. UI y 9-slice: qué entrega el arte 2D

La UI la construye [ver: unity/ui-unity] y el diseño está en [ver: gamedev/ux-ui-onboarding]; el 9-slice a fondo en [ver: pipeline/arte-a-unity §4]. Lo que el ARTE 2D debe entregar y cómo importa distinto de un sprite de mundo:

- **Iconos:** al tamaño real de pantalla (ej. 64/128 px), en su propio **Sprite Atlas de UI** (Allow Rotation OFF), Filter según estilo (Point si es pixel art, Bilinear si HD). Mesh Type Full Rect si van en `Image`.
- **9-slice (paneles/botones):** entregar con **esquinas detalladas** (nunca se deforman), **bordes seamless** en su eje y **centro liso**; documentar el **grosor de borde en px** — ese número ES el Border del Sprite Editor. Import: **Mesh Type = Full Rect** (Tight rompe el slicing), atlas con Tight Packing OFF. En `Image`: Image Type = Sliced. Detalle y límites de collider: [ver: pipeline/arte-a-unity §4].
- **Barras (vida/mana/carga):** entregar fondo + relleno como piezas separadas; el relleno se vacía con `Image.type = Filled` o pivot en un extremo, no escalando la textura. Marco 9-slice aparte si crece.
- **Fuentes bitmap vs TMP:** el pixel art suele querer tipografía de píxel; opciones — fuente `.ttf` de píxel horneada en un **Font Asset TMP** (con Point y sin AA en el atlas) o un Sprite Font. Cobertura de idioma y fallbacks: [ver: unity/ui-unity §6] y [ver: ui-2d-arte].

## 11. Handoff: checklist e import automatizado

El asset que cae en la carpeta correcta debería importarse solo. **Naming y carpetas** (2D): `Prefijo_Nombre_Variante` — `Chr_Hero_Idle`, `Tile_Forest_Ground`, `UI_Btn_Play`, `FX_Explosion`; una carpeta por familia (`Art/Characters/`, `Art/Tiles/`, `Art/UI/`) para que el Preset/postprocessor de esa carpeta aplique los settings correctos [ver: unity/assets-pipeline-git §1] (pixel art vs HD vs UI necesitan reglas distintas). Automatizar con **Preset por carpeta** o **AssetPostprocessor** (settings de §3 sin tocar a mano). Runbook de aprobación (un asset que falla un paso se devuelve con el número del paso, no se "arregla un poquito" en Unity):

1. **Archivo:** PNG-32 con alpha real, tamaño final exacto, sin `--trim` en grid, naming `Prefijo_Nombre_Variante`. Animación: mismo canvas y pivot en todos los frames.
2. **Densidad:** alto en px ÷ alto esperado en unidades = PPU del proyecto. Pixel art: ¿el píxel del asset mide lo mismo que el de los assets existentes?
3. **Import:** Type Sprite (2D and UI), PPU global, Point+None (pixel art) o Bilinear+Normal (HD), mipmaps off. Idealmente vía Preset/postprocessor.
4. **Slice/pivot:** Multiple slicedo por grid; pivot por categoría (pies en personajes), en píxel exacto en pixel art.
5. **Atlas/sorting:** asignado a su Sprite Atlas y su Sorting Layer; Frame Debugger confirma que batchea.
6. **En juego:** en la escena visual-target con la cámara real. Pixel art: con la Pixel Perfect Camera activa y **Current Pixel Ratio entero**; mover el sprite y confirmar **cero flicker/shimmer**.
7. **Animación:** clips con los tags correctos, sin salto entre frames, tempo (Samples) correcto.

Automatizar el paso 2-3 con un validador de editor (tipo `AuditSprites`: lista sprites cuyo `spritePixelsPerUnit` ≠ PPU global o cuyo `textureType` ≠ Sprite) — correrlo tras cada tanda en vez de revisar a mano [ver: pipeline/arte-a-unity §10].

## Reglas prácticas

1. Congela densidad/PPU, resolución de referencia, tamaño de canvas y pivots ANTES del primer asset; vive en el style guide [ver: pipeline/arte-a-unity].
2. UN PPU global. Pixel art: PPU = tamaño de tile. Un sprite a otra densidad rompe el pixel-perfect y el batching.
3. Entrega al tamaño final EXACTO a 1×; el upscale lo hace la Pixel Perfect Camera, jamás `--scale` cocido ni escala no-entera.
4. Aseprite → hoja con `--sheet-type rows/columns`, `--trim` OFF, padding 0, celda uniforme; el padding lo pone el Sprite Atlas de Unity.
5. Nombra los tags de Aseprite EXACTO como los clips de Unity; `--list-tags` para llevar los rangos en el JSON.
6. Tríada de pixel art nítido en el import: **Point + Compression None + PPU = tile**; mipmaps off, Alpha Is Transparency on.
7. Sprite Mode Multiple + slice **Grid By Cell Size** con la celda real; pivot en los **pies** para personajes, `Pivot Unit Mode = Pixels`.
8. Mismo canvas y mismo pivot en todos los frames de una animación, o el sprite "vibra" al reproducir.
9. Sprites SUELTOS al repo; el Sprite Atlas lo arma el proyecto (uno por contexto simultáneo); verifica el batch con Frame Debugger.
10. Elige el camino de animación por proyecto: **sprite swap** (pixel art, pocos frames) vs **skeletal/.psb** (HD, muchas animaciones desde un dibujo) — no mezcles a mitad.
11. Variantes/skins sin duplicar clips: **Sprite Library Asset** (Categories/Labels) + **Sprite Resolver**.
12. Skeletal: entrega `.psb` con partes en capas y solape en articulaciones; riggea en el Skinning Editor, deforma con Sprite Skin.
13. Tilesets: misma celda que el PPU, bordes seamless, y acuerda con el implementador qué piezas necesita el **Rule Tile** antes de dibujar el blob de 47.
14. Decide el look de luz: pixel art con sombreado dibujado → **Unlit** + luces solo de ambiente/glow; **Lit** + normal maps es un look deliberado y caro por sprite.
15. Si el juego 2D se ve negro tras pasar a 2D Renderer: falta Global Light 2D, o pon Default Material Type = Unlit.
16. Automatiza el import con Preset/AssetPostprocessor por carpeta; deja de tocar settings a mano [ver: unity/assets-pipeline-git].
17. Aprueba SIEMPRE en la escena visual-target con cámara real y en movimiento; nunca en el visor de Aseprite ni con el sprite suelto.
18. Paletas desde [lospec.com](https://lospec.com/palette-list): importa `.gpl`/`.ase`/`.png` a Aseprite; una sola paleta por proyecto la fija el style guide [ver: pixel-art].
19. UI en su propio Sprite Atlas (Allow Rotation OFF); 9-slice con Full Rect + borde en px documentado; barras con `Image.type = Filled`, no escalando la textura.
20. El color se hornea en el PNG: una paleta indexada por proyecto en Aseprite; Unity no reindexa ni corrige color en el import.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Pixel art borroso en Unity | Filter Mode quedó Bilinear; poner **Point** + Compression None + mipmaps off |
| Bandas/artefactos de bloque en el sprite | Compression ≠ None en pixel art; ponerla **None** |
| Sprite se ve nítido parado pero "nada"/tiembla al moverse | Falta Pixel Perfect Camera con Asset PPU = PPU del arte, o pivots no están en píxel [ver: pipeline/arte-a-unity §3] |
| El personaje "salta" entre frames de una animación | Frames con distinto canvas o pivot; slice por grid con celda fija y `--trim` OFF |
| Sprites a distintas densidades (32 y 48 px "por detalle") | UN PPU global; el de otra densidad se rehace, no se escala con transform |
| Halo oscuro alrededor del sprite al filtrar | Alpha Is Transparency OFF; activarlo (dilata el color bajo el alpha) |
| Muchas draw calls con decenas de sprites | Sin Sprite Atlas o sprites de un mismo frame en atlas distintos; agrupar por contexto y verificar en Frame Debugger |
| Iconos de UI rotados raros en el atlas | Allow Rotation ON en un atlas de UI; apagarlo |
| `--trim` activo rompió el grid del spritesheet | En hojas de grid, `--trim` OFF y celda uniforme; trim solo para packed con `--data` |
| Todo el juego 2D negro tras cambiar a 2D Renderer | Materiales Lit sin luz: Global Light 2D en los sorting layers, o Default Material Type = Unlit |
| Pixel art lit se ve "aplanado" | El arte ya traía su luz dibujada: usar Unlit; Lit+normal map es un look aparte, no el default |
| Pivot de Aseprite "no llegó" a Unity | Unity no importa el pivot del slice de Aseprite solo; aplicarlo en el Sprite Editor o con un postprocessor que lea el JSON |
| Riggeé skeletal para 3 enemigos de 4 frames | Sobre-ingeniería: sprite swap es más barato de punta a punta para pocos frames |
| Tileset con costuras entre tiles | Bordes no seamless o Filter ≠ Point en los tiles; redibujar bordes y poner Point |
| Panel 9-slice con esquinas deformadas | Mesh Type quedó Tight o se escaló con transform; Full Rect + Image Type Sliced / `SpriteRenderer.size` [ver: pipeline/arte-a-unity §4] |
| Fuente de píxel sale borrosa | Font Asset TMP con AA/Bilinear; hornear el atlas con Point y sin AA [ver: unity/ui-unity §6] |
| Iconos de UI en el mismo atlas que los sprites de mundo | Atlas de UI separado; se batchea con el resto del HUD, no con el gameplay |
| Memoria de texturas 2D disparada | Read/Write ON (dobla RAM), mipmaps ON en 2D, o atlas sobre-agrupados; apagar Read/Write y mips, agrupar por co-ocurrencia |
| Aprobar el sprite viéndolo suelto y desentona en juego | Aprobar solo en la escena visual-target con cámara/luz reales, en movimiento [ver: gamedev/arte-direccion] |

## Fuentes

- Texture Import Settings / **Sprite (2D and UI)** reference — Unity Manual 6000.2 (`class-TextureImporter.html`, `texture-type-sprite.html`) — Sprite Mode Single/Multiple/Polygon, Pixels Per Unit, Mesh Type Full Rect/Tight (**<32×32 px usa Full Rect automáticamente**), Filter Mode Point/Bilinear/Trilinear, sRGB, Alpha Source, Alpha Is Transparency, Wrap Mode.
- **Sprite Editor** window reference — Unity Manual 6000.x (`sprite/sprite-editor/…`) — Sprite Editor tab, Custom Outline, Custom Physics Shape, Secondary Textures; slicing por grid y pivots por sprite.
- **Sprite Atlas** (landing + V2) — Unity Manual 6000.2 (`sprite/atlas/atlas-landing.html`) — combina texturas en una para **una draw call**; Objects for Packing, Include in Build, Allow Rotation, Tight Packing, Padding, Type Master/Variant.
- **2D Animation** package + **PSD Importer** — docs `com.unity.2d.animation` / `com.unity.2d.psdimporter` — rig y animación 2D; PSD Importer genera un Prefab de sprites desde las capas de un **.psb** (imágenes más grandes que .psd). ⚠️ Número de versión sin congelar aquí: la doc `@10.0` está fijada a Unity 2023.1, y la build de paquetes vigente al verificar esta fuente (2026-07-20) ya está en `@16.0` — confirmar en el Package Manager del proyecto cuál trae el Unity 6 real antes de citar una versión exacta.
- **Sprite Swap** — docs `com.unity.2d.animation` (`SpriteSwapIntro`) — Sprite Library Asset (Categories/Labels), Sprite Library component, Sprite Resolver component; para frame-a-frame y variantes de personaje.
- **Aseprite — Exporting Sprite Sheets** y **CLI** — aseprite.org/docs (`sprite-sheet`, `cli`) — `File ▸ Export Sprite Sheet` (capas visibles/una capa, frames por tags); flags `--sheet`, `--sheet-type horizontal/vertical/rows/columns/packed`, `--data`, `--format json-hash/json-array`, `--sheet-pack`, `--trim`, `--border/shape/inner-padding`, `--scale`, `--split-layers/tags`, `--list-tags/slices`.
- **Aseprite — Tags** — aseprite.org/docs (`tags`) — crear tag sobre un rango (`Frame ▸ Tags ▸ New Tag`); Animation Direction **Forward / Reverse / Ping-pong**. API Lua de scripting: aseprite.org/api.
- **Lospec Palette List** — lospec.com/palette-list — base de paletas de pixel art (4.382 al 2026-07-20); descargas PNG, JASC PAL, Photoshop .ASE, Paint.net .TXT, GIMP .GPL, .HEX.
- Referencias de pixel art reconocidas: **Pixel Logic** (Michael Azzi) y los tutoriales de **Saint11 / Pedro Medeiros** — principios de densidad de píxel consistente, sin AA automático y paleta limitada que aquí solo se aplican al import; teoría en [ver: pixel-art].
- Base sintetizada (verificada en las hermanas, no repetida): [ver: pipeline/arte-a-unity] (spec/contrato, Pixel Perfect Camera a fondo, 9-slice, atlas y sorting como decisión de proyecto, resoluciones móviles), [ver: pipeline/recetas-generos] (Tilemap, Rule Tiles, TilemapCollider2D+CompositeCollider2D, procgen), [ver: unity/rendering-urp] (Light 2D, Sprite-Lit/Unlit-Default, Blend Styles, sorting 2D), [ver: unity/assets-pipeline-git] (import a fondo, Sprite Atlas V2, Preset/AssetPostprocessor, naming), [ver: unity/animacion-unity] (Animator/clips), [ver: unity/rendimiento-unity] (draw calls/batching).
