# Tilesets y mundos 2D

> **Cuando cargar este archivo:** al producir el arte de un mundo 2D con tiles — elegir tamaño de tile y grid, dibujar un tileset seamless, resolver bordes y esquinas con autotiling, montar terreno con transiciones, armar fondos con parallax, poblar con props, y llevar todo a un Tilemap de Unity con iluminación 2D. El equivalente 2D de los kits modulares [ver: modelado/entornos-modulares]. Para el pixel art en sí [ver: pixel-art]; para sprites/animación [ver: sprites-produccion], [ver: animacion-2d]; el flujo de Aseprite en [ver: aseprite-flujo]; el import a Unity en [ver: 2d-a-unity].

Este archivo es PRODUCCIÓN de arte 2D de entorno. El diseño artístico general (paleta maestra, dirección) está en [ver: gamedev/arte-direccion]; el diseño de nivel jugable en [ver: gamedev/level-design]; la implementación de géneros en Unity en [ver: pipeline/recetas-generos]; el rendering 2D (luces, sorting, atlas, overdraw) en [ver: unity/rendering-urp]. Aquí: cómo se hace el arte del mundo y cómo encaja en el sistema de tiles. Cross-referencia, no repite.

## 1. El tile: la pieza modular del 2D

Un **tile** es una imagen cuadrada reutilizable que, colocada sobre un grid, construye el mundo. Es el mismo principio que el kit modular 3D [ver: modelado/entornos-modulares §1]: no se pinta "el nivel" como una imagen gigante — se pinta un **alfabeto** de piezas y el nivel se escribe con él. Las razones son idénticas a las del kit 3D, trasladadas a 2D:

| Razón | En 2D |
|---|---|
| Economía de producción | Un tileset de ~40 tiles pinta kilómetros de nivel; el level designer arma sin pedir arte nuevo |
| Memoria / rendimiento | Pocos tiles únicos en un atlas → 1-2 draw calls por tilemap con batching [ver: unity/rendering-urp §Sprite Atlas] |
| Iteración | El diseño rearma el layout tile a tile sin tocar el arte |
| Coherencia | Todos los tiles comparten grid, paleta y densidad de detalle → el mundo se lee de una sola mano [ver: gamedev/arte-direccion] |

Diferencia clave con el 3D: el tile 2D no rota libremente. Una pieza que en 3D se reutiliza en 4 rotaciones, en 2D suele necesitar variantes dibujadas (una esquina superior-izquierda NO es la inferior-derecha volteada si la luz viene de arriba — la sombra queda mal). El autotiling (§4) es la respuesta a ese problema de bordes.

## 2. Tamaño de tile, grid y PPU

La primera decisión, congelada antes del primer tile: **tamaño de tile en píxeles**. Gobierna la densidad de detalle, la escala del personaje y el PPU de Unity. No se cambia después (cada tile existente lo hereda).

| Tile | Look / era | Cuándo |
|---|---|---|
| **8×8 px** | Ultra-retro (Atari, primeras NES), minimalista | Puzzle abstracto, estética deliberadamente cruda; detalle casi nulo por tile |
| **16×16 px** | El clásico (NES/SNES, la mayoría del indie pixel art) | **Default seguro.** Balance detalle/legibilidad; personaje típico de 1-2 tiles de alto |
| **32×32 px** | Pixel art de más resolución (mucho indie moderno) | Cuando el personaje/props piden detalle; el mundo se ve más "denso" |
| **48×48 / 64×64 px** | Hi-res pixel art (estilo Dead Cells, Hyper Light) | Detalle fino, degradados, más colores por tile; más costo de producción por pieza |

Reglas:

- **Potencias de 2** para el tamaño base (8/16/32/64): encajan limpio en atlas, mipmaps y GPU. 48 es la excepción común (múltiplo de 16 pero no potencia de 2) — válido, solo cuídalo en el atlas.
- **Consistencia total**: TODO el tileset (y idealmente todo el arte del juego) comparte el mismo grid. Mezclar tiles de 16 y 32 en el mismo mundo rompe la escala salvo decisión de estilo explícita.
- El tamaño de tile fija la escala del personaje: un sprite de héroe de "2 tiles de alto" mide 32 px con tiles de 16, 64 px con tiles de 32. Decide el ratio personaje:tile temprano [ver: sprites-produccion].
- **Resolución interna del juego**: el mundo se diseña para una resolución base baja (ej. 320×180, 384×216, 256×224) y se escala entero a la pantalla (§12). El tamaño de tile × cuántos caben en pantalla = esa resolución base.

### PPU y el grid de Unity

**Regla de oro: PPU = lado del tile en píxeles.** Tile de 16 px → **Pixels Per Unit = 16** en el import de todos los sprites → 1 tile = **1 unidad de mundo** de Unity → el **Grid** con Cell Size (1,1,0) (default) cae perfecto sobre los tiles. Con esto, 1 unidad Unity = 1 tile, y toda la física, cámara y snapping trabajan en unidades enteras de tile.

| Setting | Valor | Por qué |
|---|---|---|
| Sprite import: **Pixels Per Unit** | = tamaño de tile (16/32/48) | 1 tile = 1 unidad → grid limpio |
| Sprite import: **Filter Mode** | **Point (no filter)** | Bilinear emborrona el pixel art [ver: 2d-a-unity] |
| Sprite import: **Compression** | None | La compresión mete artefactos en pixel art [ver: 2d-a-unity] |
| Grid component: **Cell Size** | (1,1,0) default | Con PPU = tile, el tile llena exactamente una celda |
| Sprite: **Mesh Type** | Full Rect para tiles (opacos, sin recorte) | Tiles son cuadrados llenos; Tight es para sprites con transparencia [ver: unity/rendering-urp §overdraw] |

Detalle de import en [ver: 2d-a-unity]; el efecto de la cámara Pixel Perfect en §12.

## 3. Tiles seamless (que repitan sin costura)

Un tile de superficie (pasto, agua, pared, piso) debe **tilear**: al colocarlo en cuadrícula, el borde derecho continúa en el izquierdo del vecino y el inferior en el superior, sin línea visible de corte. Dos problemas separados:

**A. Que no haya costura (seamless).** El píxel del borde derecho debe encadenar con el del borde izquierdo. Técnica de edición:

- **Preview tileado**: en Aseprite, `View > Tiled Mode` (Both / X / Y) muestra el canvas repetido mientras pintas — pintas cruzando el borde y ves el resultado tileado en vivo. Es la herramienta #1 para cerrar costuras.
- **Sin líneas rectas de contraste** cruzando el borde: una diagonal fuerte o un highlight que topa el borde crea una reja visible al repetir. Los detalles fuertes viven hacia el centro del tile.
- **Sin gradiente global** en un tile que tilea: un degradado de claro-arriba a oscuro-abajo genera bandas obvias al apilar. La luz global va en otra capa (§11), no horneada en el tile de superficie.

**B. Que no se note la repetición (breaking the grid).** Un tile seamless perfecto igual se delata: el ojo detecta el patrón cada N celdas. Arsenal, en orden de costo (mismo principio que el 3D [ver: modelado/entornos-modulares §4]):

| Técnica | Detalle |
|---|---|
| **Variantes del mismo tile** | 3-5 versiones del tile base (limpio / con piedrita / con grieta / con mancha) mezcladas al pintar. La forma más directa; el motor las coloca aleatoriamente (Random Tile / Weighted Random, §5) |
| **Detalle disperso, no denso** | El detalle marcado (flor, roca) va en POCAS variantes, no en todas — si cada tile tiene una flor, la flor ES el patrón |
| **Props/overlay encima** | Objetos sueltos (matas, piedras, charcos) en una capa de decoración rompen la lectura de la grilla (§10) |
| **Anti-tiling matemático** | Grietas/manchas que NO respetan el borde del tile, atravesando varias celdas (decals, no tiles) |
| **Evitar el "cluster" repetido** | Un grupo de píxeles muy reconocible (3 píxeles en L, un highlight en punta) que se repite es lo que el ojo caza; romper esos clusters distintivos (lección de pixel art: cuidar el *banding* y los clusters, Saint11 / Pixel Logic) |

Regla: nunca copy-paste de un bloque grande de mundo ya pintado — es la forma más rápida de que se vea repetido. Variar la capa de detalle sobre el mismo tileset.

## 4. Autotiling: el problema de los bordes y esquinas

El problema central del terreno 2D: cuando un tipo (pasto) toca otro (tierra/vacío), el **borde** entre ambos necesita un tile distinto del centro. Y las **esquinas** (interior vs exterior) necesitan los suyos. Dibujar y colocar eso a mano es lento y frágil. El **autotiling** elige automáticamente el tile correcto según los vecinos.

Cuántos tiles necesita un terreno según el método (números canónicos del gamedev/pixel art):

| Método | Tiles | Cómo funciona | Trade-off |
|---|---|---|---|
| **Solo bordes (4-bit)** | **16** | Bitmask de 4 vecinos ortogonales (N/E/S/O), 2⁴ = 16 combinaciones | Resuelve bordes rectos y esquinas exteriores; **NO** distingue esquinas interiores (dos bordes que se juntan hacia adentro) |
| **Blob completo (8-bit)** | 256 crudas → **47 únicas** | Bitmask de 8 vecinos, 2⁸ = 256; pero un vecino diagonal solo importa si sus DOS ortogonales están presentes → colapsa a 47 tiles distintos | El estándar "blob"/47-tile: transiciones perfectas incluyendo esquinas interiores. Más arte que dibujar |
| **Dual-grid (esquinas)** | **16** | Los tiles se colocan en un grid desplazado media celda; cada tile visible se define por sus **4 esquinas** (2⁴ = 16 combos), no por sus bordes | Transiciones tipo blob con solo 16 piezas; requiere el offset de medio tile. Técnica moderna eficiente |

Claves:

- **16 tiles** es lo mínimo para que un borde se vea decente, pero deja las esquinas interiores feas. Para terreno "de verdad" quieres el set blob (**47**) o el enfoque **dual-grid** (16, con esquinas correctas).
- El autotiling NO se hace en Aseprite — Aseprite pinta el **tileset** (las 16/47 piezas); la lógica de "qué tile va según vecinos" vive en el **motor** (Rule Tile de Unity, §5) o en el código del juego.
- **Wang tiles / corner tiles**: familia de métodos donde los bordes/esquinas se codifican con colores que deben coincidir entre vecinos; el blob y el dual-grid son casos de esta familia.
- Presupuesto de arte: cada tipo de terreno con transición a otro multiplica los tiles. Prioriza qué pares de terreno de verdad se tocan en el juego antes de dibujar 47 tiles × cada combinación.

## 5. Autotiling en Unity: Rule Tile (2D Tilemap Extras)

Unity resuelve el autotiling con el paquete **com.unity.2d.tilemap.extras** (v9.0.0, release 19-may-2026 — verificado contra `@latest` en docs.unity3d.com esta sesión; se instala vía Package Manager, no viene por defecto). La pieza central es el **Rule Tile**.

**Rule Tile** — un tile que decide qué sprite mostrar según sus vecinos, evaluando una **grilla 3×3** (el centro es el tile mismo; las 8 celdas alrededor son los vecinos). Cada vecino se marca con una de tres condiciones:

| Condición | Significado |
|---|---|
| **This** | Esa celda debe contener el MISMO Rule Tile (matchea) |
| **Not This** | Esa celda NO debe contener este Rule Tile |
| **Don't Care** | Esa celda se ignora (sin flecha/marca) |

Cuando todos los vecinos cumplen su condición, la regla matchea y se aplica su salida. Otros parámetros verificados del Rule Tile:

- **Rule Transform** (cómo se reusa una regla para varias orientaciones): **Fixed** (solo la config exacta), **Rotated** (prueba rotaciones de 90°), **Mirror X / Y / XY** (prueba espejados). Con Rotated, UNA regla cubre las 4 rotaciones de un borde → menos reglas que escribir.
- **Output** (qué dibuja cuando matchea): **Fixed** (un sprite), **Random** (uno al azar de varios, con opción de rotación aleatoria — para romper repetición, §3), **Animation** (secuencia de sprites a una velocidad — agua, lava).
- **Extend Neighbors**: expande la evaluación más allá del 3×3 para reglas más precisas.
- **Variantes de grid**: **Rectangle** (default), **Hexagonal** e **Isometric** Rule Tiles.

Otros scriptable tiles/brushes del paquete (v9.0.0):

| Elemento | Qué hace |
|---|---|
| **Rule Override Tile** | Reemplaza los sprites/GameObjects de un Rule Tile existente SIN reescribir sus reglas (reskin de un terreno ya reglado) |
| **Advanced Rule Override Tile** | Overridea un subconjunto de reglas, dejando el resto intacto |
| **Animated Tile** | Recorre una lista de sprites en secuencia (animación cuadro a cuadro sin lógica de vecinos) |
| **GameObject Brush** | Instancia y posiciona GameObjects sobre la escena (props con lógica, no solo sprites) |
| **Random Brush** | Pinta tiles aleatorios de un set |
| **Line Brush / Group Brush** | Línea de tiles entre dos puntos / selección de grupos por posición relativa |

Flujo típico: dibujar el tileset en Aseprite → cortar en sprites (Sprite Editor, Grid By Cell Size) → crear un Rule Tile → cargar las reglas (borde/esquina/centro) usando This/Not This + Rotated → pintar con el Tile Palette y el motor elige el sprite solo. Detalle de import y Tile Palette en [ver: 2d-a-unity].

## 6. Tilesets de terreno: transiciones y capas

Un mundo con varios tipos de suelo (pasto, tierra, agua, roca) no se resuelve con un solo autotile — se resuelve con **capas y prioridad**.

- **Un tipo por capa de tilemap**, apiladas por prioridad visual. Ejemplo top-down: capa `Tierra` (base, llena todo) → capa `Pasto` encima (con su autotile de borde que se difumina hacia la tierra) → capa `Agua`. El borde pasto→tierra lo dibuja el autotile del pasto sobre la tierra que asoma debajo. Así N terrenos necesitan N autotiles de "X sobre lo de abajo", no N×N combinaciones.
- **Orden de apilado = jerarquía natural**: lo que "queda encima en la realidad" va en la capa superior (pasto sobre tierra, nieve sobre pasto). El agua suele ir debajo con una orilla dibujada.
- **Tiles de transición explícitos** para pares que el autotile no cubre (playa entre agua y arena): un puñado de tiles dibujados a mano, colocados manualmente o con reglas específicas.
- **Un solo Grid, varios Tilemaps** (§7): todas las capas comparten el mismo Grid component de Unity → alineadas por construcción.

## 7. El Tilemap de Unity: Grid, Tilemap y Renderer

La jerarquía de Unity para pintar el mundo: un **Grid** (GameObject padre, define Cell Size/Layout) con uno o varios **Tilemap** hijos (cada uno una capa: fondo, colisión, decoración, frente), cada Tilemap con un **Tilemap Renderer**.

**Cell Layout** del Grid: Rectangle (default), Hexagon, Isometric, Isometric Z as Y. Cell Size default (1,1,0) (§2).

**Tilemap Renderer — Mode** (decisión de rendimiento vs composición, verificado en docs):

| Mode | Qué hace | Cuándo |
|---|---|---|
| **Chunk** | Renderiza muchos tiles juntos en batches → máximo rendimiento y sorting consistente. Pero NO deja que otros objetos se intercalen entre tiles de distinta profundidad. No compatible con SRP Batcher | Capas de fondo/suelo estáticas donde nada se mete entremedio |
| **Individual** | Ordena tiles y sprites juntos → personajes y objetos pueden aparecer ENTRE tiles de distinta profundidad. Más costoso (cada sprite se dibuja aparte) | Capas donde el jugador pasa por delante/detrás de tiles (columnas, vegetación alta) — Y-sort |
| **SRP Batch** | Batched vía SRP Batcher (URP) para mejor rendimiento con batching | Default recomendado en URP para el grueso de las capas |

Otras propiedades del Renderer: **Sort Order** (dirección de dibujado; default **Bottom Left**), **Detect Chunk Culling Bounds** (Auto/Manual), **Sorting Layer** + **Order in Layer** (integran el tilemap en el sorting 2D global, [ver: unity/rendering-urp §sorting]), **Mask Interaction**, **Material** (default `Sprite-Lit-Default` → recibe luces 2D, §11).

- **Colisión aparte del arte**: la capa de colisión es un Tilemap con **TilemapCollider2D** + **CompositeCollider2D** (Merge/Outlines) — no todos los tiles visuales colisionan. Patrón de plataformas en [ver: pipeline/recetas-generos].
- **Mapas grandes**: dividir en varios Tilemaps por zona y activar/desactivar por distancia, en vez de un tilemap monolítico; todos los tiles del mismo atlas para no romper el batching [ver: unity/rendimiento-unity].

## 8. Aseprite: pintar el tileset

Aseprite (feature de tilemap estable desde la 1.3; versión actual 2026) pinta tilesets nativamente. Conceptos verificados de la doc oficial:

| Concepto | Qué es |
|---|---|
| **Tilemap Layer** | Capa especial (`Layer > New > New Tilemap Layer`) donde cada celda del canvas referencia un tile del tileset (como un índice de paleta apunta a un color) |
| **Tileset** | Colección de tiles del mismo tamaño; cada tile tiene un índice y se reutiliza en varias celdas |
| **Draw Pixels vs Draw Tiles** | Dos modos: *Draw Pixels* modifica el CONTENIDO (píxeles) de los tiles; *Draw Tiles* coloca/toma tiles sin editar su contenido (edita el mapa, no el arte) |

Submodos al dibujar píxeles (cómo se crean/actualizan tiles):

| Submodo | Comportamiento |
|---|---|
| **Auto** (default) | Simula una capa normal: ajusta el tileset automáticamente — si pintas algo nuevo, crea/reusa tiles solo |
| **Manual** | Modifica el contenido del tile SIN reorganizar el tileset |
| **Stack** | Crea un tile nuevo por cada modificación, sin alterar los existentes |

Consecuencia clave (la ventaja de trabajar así): **editar un tile del tileset actualiza TODAS sus instancias** en el tilemap a la vez — cambias la textura del pasto una vez y todo el mundo cambia. Es el equivalente 2D de "editar la malla del kit y que se propague a las 500 copias". Combinado con `View > Tiled Mode` para el seamless (§3). El flujo completo de Aseprite (export, slices, animación) en [ver: aseprite-flujo].

⚠️ No hay Aseprite instalado ni MCP para verificar operadores en vivo en este entorno; los atajos de teclado específicos no se documentan aquí para no inventarlos — los modos anteriores están verificados contra la doc, no así combinaciones de teclas concretas.

## 9. Fondos y parallax

El **parallax** da profundidad moviendo capas de fondo a distinta velocidad que la cámara: lo lejano se mueve lento, lo cercano rápido — como mirar por la ventana de un carro. Es el recurso #1 de profundidad en un mundo 2D.

Estructura típica (número de capas: **3-6**; menos de 3 se ve plano, más de ~6 rinde poco extra):

| Capa | Velocidad relativa a cámara (ejemplo) | Contenido |
|---|---|---|
| Cielo / gradiente | 0.0–0.1 (casi fijo) | Fondo lejano, degradado, sol/luna |
| Montañas / skyline lejano | ~0.2–0.3 | Silueta grande, poco detalle, poco contraste |
| Media distancia | ~0.5–0.6 | Árboles/edificios de fondo, algo de detalle |
| Cercana (detrás del gameplay) | ~0.8–0.9 | Vegetación/props grandes cerca del plano de juego |
| **Plano de juego (tiles)** | **1.0** | El tilemap jugable — velocidad de referencia |
| Foreground (delante del jugador) | >1.0 | Ramas/rejas que pasan por delante, dan encuadre |

Las velocidades exactas son de oficio, no ley — se afinan mirándolas en movimiento. Reglas de arte:

- **Cuanto más lejos, menos contraste y menos saturación** (perspectiva atmosférica): la capa lejana tiende al color del cielo; el contraste se reserva para el plano de juego, donde está la acción [ver: gamedev/arte-direccion]. Si el fondo compite en contraste con los enemigos, el jugador pierde legibilidad.
- **Capas de fondo tilean horizontalmente** (seamless en X, §3) para hacer scroll infinito; en Unity, un sprite ancho repetido o un `SpriteRenderer` en Draw Mode **Tiled**.
- **Menos detalle atrás**: el fondo lejano es formas grandes, no pixel art fino — se mueve poco y no aguanta inspección.
- Implementación (mover cada capa = `cámara.x × factor`) en [ver: pipeline/recetas-generos] y [ver: pipeline/feel-en-unity]; en 2D top-down puro no hay parallax de scroll pero sí capas de profundidad por sorting.

## 10. Props y decoración del mundo

Los props (objetos sueltos: matas, rocas, barriles, carteles, hongos) son lo que convierte una grilla de tiles en un lugar. No son tiles de terreno — van en una capa de decoración encima.

| Principio | Detalle |
|---|---|
| **Variación > cantidad** | 5 rocas distintas rotadas/volteadas pueblan más creíble que 1 roca repetida 50 veces. Pocas piezas, muchas combinaciones (mismo principio que el 3D [ver: modelado/entornos-modulares §7]) |
| **Densidad con ritmo** | Ni desierto vacío ni sopa de props. Agrupar (cluster de plantas cerca del agua) y dejar respirar (zonas limpias donde el gameplay pasa) [ver: gamedev/level-design] |
| **Props rompen la grilla** | Colocados fuera del snap del tile (medio píxel, ligeramente rotados si el estilo lo permite) disimulan la cuadrícula (§3) |
| **Legibilidad primero** | Un prop decorativo NO debe parecer interactivo/coleccionable si no lo es (evitar botones muertos visuales) [ver: gamedev/ux-ui-onboarding]. El contraste fuerte se reserva para lo jugable |
| **Colocación en Unity** | **GameObject Brush** (props con lógica/collider) o un Tilemap de decoración con Random Tile (props puramente visuales). Vegetación densa: no colocar objetos uno a uno si son cientos — instanciar/batchear [ver: unity/rendimiento-unity] |

## 11. Iluminación 2D a nivel de arte

Las luces 2D de URP (Light 2D, sistema completo en [ver: unity/rendering-urp §Luces 2D]) cambian cómo se PINTA el arte del mundo. La decisión de producción, tomada temprano:

**¿El arte trae la luz horneada, o la pone el motor?** Son dos filosofías incompatibles de mezclar sin cuidado:

| Enfoque | Cómo se pinta el tileset | Material | Cuándo |
|---|---|---|---|
| **Arte plano + luz dinámica** | Tiles en **tono medio neutro**, sin sombras direccionales fuertes horneadas (la luz vendrá del motor) | `Sprite-Lit-Default` | Juego con luces que se mueven (antorchas, día/noche, linterna). El arte se ve "plano" solo en el editor sin luz |
| **Luz horneada en el arte** | Cada tile YA trae su sombreado y ambiente pintados (pixel art clásico) | `Sprite-Unlit-Default` | Estética retro fiel, sin luces dinámicas. Meter una Light 2D encima "dobla" la luz y se ve mal |

Consecuencias prácticas:

- Si vas a usar luces 2D dinámicas, **no hornees sombras marcadas** en los tiles de superficie — chocan con la sombra que proyecta la luz. Pinta el ambiente, deja la dirección al motor.
- **Normal maps para tiles/sprites**: un sprite puede traer un normal map (Secondary Texture `_NormalMap` en el Sprite Editor) para que la luz 2D reaccione al relieve (ladrillos que se iluminan por un lado según la antorcha). Propiedad **Normal Map Quality** en la Light 2D [ver: unity/rendering-urp]. Cuesta producción (pintar/derivar el normal por tile) — solo si el look dinámico lo justifica.
- **Setup mínimo** para que un mundo Lit no se vea negro: una **Global Light 2D** de ambiente (intensity ~0.2–0.5) + luces Spot/Freeform puntuales; sin la global, todo lo `Sprite-Lit` sale negro [ver: unity/rendering-urp §Luces 2D].
- **Emisión / glow**: para neones, lava, cristales — HDR + Bloom en el Volume, con los píxeles brillantes por encima del threshold [ver: unity/rendering-urp §post-processing]. El pixel art brillante NO glowea solo; el glow lo pone el post.

## 12. Llevar el mundo a Unity: Pixel Perfect

Para que el mundo de tiles se vea nítido y estable (sin píxeles "temblando" o de tamaños desiguales), URP trae el **Pixel Perfect Camera** (componente en la Camera). Propiedades verificadas:

| Propiedad | Qué hace |
|---|---|
| **Asset Pixels Per Unit** | Los píxeles que forman una unidad de escena. **Debe coincidir con el PPU de import de todos los sprites/tiles** (§2) |
| **Reference Resolution** | La resolución para la que está diseñado el arte (ej. 320×180). El componente escala a la pantalla real manteniendo la nitidez |
| **Upscale Render Texture** | Renderiza a una textura cercana a la Reference Resolution y luego la escala → píxeles sin alias ni artefactos de rotación |
| **Pixel Snapping** | (Solo si Upscale Render Texture está OFF) Snapea los Sprite Renderers a un grid en world space al renderizar → mata el movimiento sub-píxel |
| **Crop Frame** (X / Y) | Recorta el viewport con barras negras para respetar la Reference Resolution en ese eje |
| **Stretch Fill** | (Con X e Y activos) Estira el viewport a la resolución de pantalla respetando el aspect ratio |
| **Run In Edit Mode** | Previsualiza el efecto en el editor (muestra **Current Pixel Ratio**) |

- **Consistencia PPU**: si el import de los tiles es PPU 16 pero el Pixel Perfect Camera dice Asset PPU 32, los píxeles salen de tamaños distintos. Un solo número de PPU para todo el proyecto.
- Detalle de cámara/import y gotchas de pixel art en Unity (filtrado, atlas, snapping de movimiento) en [ver: 2d-a-unity].
- Un tileset pintado a 16 px NO se arregla escalándolo a 2× en Unity — se importa a su tamaño nativo y el Pixel Perfect Camera hace el upscale entero. Escalar el asset rompe el pixel art.

## 13. Composición de un nivel 2D con tiles

Esta sección es la bisagra entre el arte (§1-§12) y el diseño de nivel jugable, cuyo detalle de mecánica/ritmo/dificultad vive en [ver: gamedev/level-design]. Aquí: qué implica, PARA EL ARTE, que el nivel se construya con las piezas de este archivo.

- **Presupuesto de tiles por pantalla**: con la resolución interna ya fijada (§2, ej. 320×180 con tile de 16 px = 20×11.25 tiles visibles), ese es el lienzo real que el jugador lee de una vez. El arte (variantes, props, autotile) se diseña para que ESA ventana no se vea vacía ni saturada — no para un mapa completo abstracto.
- **Capas = profundidad de lectura**: el mismo apilado de §6 (terreno) + §9 (parallax) + §10 (props) es lo que compone cada pantalla: fondo lejano (contexto, sin jugabilidad) → capa media (props no interactivos) → plano de juego (tiles con los que el jugador colisiona, máximo contraste) → foreground opcional (encuadre). El arte jugable SIEMPRE gana el contraste sobre el decorativo [ver: gamedev/arte-direccion].
- **Silueta antes que detalle**: al bloquear (blockout) un nivel con el tileset, primero se valida que la silueta de plataformas/paredes se lea en blanco y negro o a distancia de miniatura — si la geometría no se lee sin color, ningún nivel de detalle del tile la arregla después [ver: gamedev/level-design].
- **El tileset debe cubrir los casos que el nivel realmente usa**: antes de dibujar el set de autotile completo (47/blob o dual-grid, §4), recorre el diseño de nivel (aunque sea en gris) y confirma qué combinaciones de terreno/plataforma aparecen de verdad — evita gastar producción en transiciones que el nivel nunca pide (mismo principio que §4, presupuesto de arte).
- **Chunking para niveles grandes**: la división en varios Tilemaps/zonas por distancia (§7, "Mapas grandes") no es solo rendimiento — también es producción: cada chunk se puede iterar/re-dressear (cambiar props, densidad) sin tocar el tileset base de los demás.
- **Legibilidad de lo interactivo**: igual que un prop decorativo no debe parecer coleccionable (§10), un tile de terreno "normal" no debe parecer plataforma/peligro si no lo es — el jugador lee la geometría del tileset como reglas de juego implícitas; cambiar el arte de un tile cambia lo que el jugador espera que haga [ver: gamedev/ux-ui-onboarding].

Esta sección NO reemplaza el diseño de nivel (ritmo de dificultad, backtracking, checkpoints, curva de introducción de mecánicas) — eso vive íntegro en [ver: gamedev/level-design]. Aquí solo se cubre cómo las decisiones de arte de este archivo (tile, autotile, capas, props) sirven o rompen esa composición.

## Reglas prácticas

1. Congela el **tamaño de tile** (8/16/32/48) antes del primer tile; 16 es el default seguro. No se cambia después.
2. **PPU = tamaño de tile** en el import de todo → 1 tile = 1 unidad Unity → Grid Cell Size (1,1,0).
3. Import de pixel art: **Point filter, sin compresión**, Full Rect para tiles opacos [ver: 2d-a-unity].
4. Tiles de superficie **seamless**: usa `View > Tiled Mode` de Aseprite y evita líneas de contraste tocando el borde y gradientes globales horneados.
5. Rompe la repetición en capas: 3-5 **variantes** del tile base + props + detalle disperso; nunca copy-paste de bloques de mundo.
6. Terreno con transiciones: decide 16 tiles (bordes), 47 (blob completo con esquinas interiores) o dual-grid (16 con esquinas) según cuánto arte puedes pagar.
7. El autotiling se dibuja en Aseprite pero se RESUELVE en el motor: **Rule Tile** de 2D Tilemap Extras (instalarlo; no viene por defecto).
8. Rule Tile: usa **This / Not This / Don't Care** en el 3×3 y **Rule Transform: Rotated** para cubrir 4 orientaciones con una regla; **Output: Random** para romper repetición.
9. Multi-terreno = **capas apiladas por prioridad** (tierra → pasto → agua) sobre UN solo Grid; N autotiles, no N×N.
10. Un **Grid** con varios **Tilemaps** (fondo / colisión / gameplay / frente); la colisión es un Tilemap aparte con TilemapCollider2D + CompositeCollider2D.
11. Tilemap Renderer: **Chunk/SRP Batch** para fondo estático; **Individual** solo donde el jugador se intercala con los tiles (Y-sort).
12. Parallax: **3-6 capas**, más lejos = más lento + menos contraste/saturación; capas de fondo tilean en X (Draw Mode Tiled).
13. Props: **variación > repetición** (5 rocas volteadas, no 1 ×50), agrupados con ritmo, fuera del snap del grid para romper la cuadrícula.
14. Decide temprano: **arte plano + luz dinámica** (tono neutro, `Sprite-Lit`) vs **luz horneada** (`Sprite-Unlit`) — no los mezcles sin querer.
15. Con luces 2D dinámicas, **no hornees sombras direccionales fuertes** en los tiles; normal map solo si el look lo justifica.
16. Mundo Lit no negro: una **Global Light 2D** de ambiente + puntuales [ver: unity/rendering-urp].
17. **Pixel Perfect Camera**: Asset PPU = PPU de import; Reference Resolution baja (ej. 320×180); Upscale Render Texture ON para nitidez.
18. Un tileset se importa a su tamaño nativo; el upscale lo hace la cámara, NUNCA escalando el asset.
19. Editar un tile en Aseprite propaga a todas sus instancias — aprovecha esto: itera el tileset, no cada colocación.
20. Todos los tiles del mundo comparten **atlas** para 1-2 draw calls por tilemap [ver: unity/rendering-urp §Sprite Atlas].
21. Diseña el tileset para la **pantalla real** (tiles visibles a la resolución interna, §2), no para un mapa abstracto; valida la silueta de la geometría en blanco y negro antes de invertir en detalle [ver: gamedev/level-design].
22. Antes de dibujar el set de autotile completo, recorre el nivel (aunque sea blockout gris) y confirma qué transiciones de terreno se usan de verdad — no dibujes las 47 combinaciones si el nivel solo toca 5.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Mezclar tiles de 16 y 32 px en el mismo mundo | Un solo tamaño de tile/grid para todo el proyecto; congelarlo antes de producir |
| PPU de import ≠ Asset PPU del Pixel Perfect Camera | Un solo número de PPU en todo el proyecto = tamaño de tile |
| Filtro Bilinear / compresión en pixel art → borroso o con artefactos | Point filter, Compression None [ver: 2d-a-unity] |
| Costura visible al tilear | `Tiled Mode` de Aseprite para pintar cruzando el borde; sin líneas de contraste ni gradiente global en el tile |
| Mundo que se ve repetido pese a tiles seamless | Variantes del tile base (Random Tile) + props + detalle disperso; romper los clusters distintivos |
| Autotile de 16 tiles con esquinas interiores feas | 16 solo resuelve bordes; para esquinas interiores usa el set blob (47) o dual-grid |
| Intentar autotiling dentro de Aseprite | Aseprite pinta el tileset; el autotiling vive en el motor (Rule Tile) |
| Escribir una regla por cada rotación del borde | Rule Transform: **Rotated**/**Mirror** cubre las orientaciones con una regla |
| N×N tiles para N terrenos que se tocan | Capas apiladas por prioridad: el borde de la capa de arriba se difumina sobre la de abajo |
| Personaje que no puede pasar por delante de una columna del tilemap | Esa capa en Individual mode (Y-sort), no Chunk |
| Todo el mundo 2D negro al pasar a Sprite-Lit | Falta una Global Light 2D de ambiente [ver: unity/rendering-urp] |
| Sombras horneadas en los tiles + luz dinámica encima ("luz doble") | Con luces dinámicas: tiles en tono neutro sin sombra direccional horneada |
| Fondo de parallax que compite en contraste con enemigos | Fondo lejano: menos contraste y saturación; el contraste es para el plano de juego |
| Fondo lejano con corte visible al hacer scroll | Capa seamless en X + Draw Mode Tiled / sprite ancho repetido |
| Escalar un tileset de 16 px a 2× en Unity para "verlo más grande" | Importar a tamaño nativo; el upscale lo hace el Pixel Perfect Camera |
| Colocar cientos de props de vegetación como GameObjects sueltos | Random Tile en capa de decoración o instancing/batch; sueltos = draw call cada uno [ver: unity/rendimiento-unity] |
| Prop decorativo que parece coleccionable/interactivo | Reservar el contraste fuerte para lo jugable; decoración más apagada [ver: gamedev/ux-ui-onboarding] |
| Tiles de varios atlases mezclados en la escena | Todos los tiles del mundo en un mismo atlas por uso → batching [ver: unity/rendering-urp] |
| Dibujar el set de autotile completo (47/dual-grid) antes de saber qué transiciones usa el nivel | Recorrer el blockout del nivel primero; presupuestar arte a lo que de verdad se toca [ver: gamedev/level-design] |
| Geometría de nivel que no se lee en silueta, tapada por detalle de tile | Validar la silueta en blanco y negro / a distancia de miniatura antes de invertir en detalle [ver: gamedev/level-design] |

## Fuentes

Verificadas contra doc oficial esta sesión (WebFetch 2026-07-20):

- **Aseprite — Tilemap & Tileset docs** (aseprite.org/docs/tilemap) — Tilemap Layer, Tileset, índice de tiles, modos Draw Pixels vs Draw Tiles, submodos Auto (default)/Manual/Stack, edición de un tile propagando a todas las instancias. Feature estable desde Aseprite 1.3.
- **Unity — Rule Tile** (docs.unity3d.com, com.unity.2d.tilemap.extras@9.0, v9.0.0) — grilla 3×3 de vecinos, condiciones This/Not This/Don't Care, Rule Transform (Fixed/Rotated/Mirror), Output (Fixed/Random/Animation), Extend Neighbors, variantes Rectangle/Hexagonal/Isometric. Re-verificado en esta auditoría: contenido técnico idéntico al reportado por el investigador, solo la etiqueta de versión estaba desactualizada (era v4.0.2, la actual al 2026-07-20 es v9.0.0).
- **Unity — 2D Tilemap Extras (index)** (com.unity.2d.tilemap.extras@9.0) — inventario del paquete v9.0.0: Rule Tile, Rule Override Tile, Advanced Rule Override Tile, Animated Tile; brushes GameObject/Group/Line/Random; GridInformation.
- **Unity — Tilemaps (introduction + reference)** (docs.unity3d.com/Manual/tilemaps) — Grid + Tilemap + Tilemap Renderer, Cell Layout/Cell Size, Tile Palette, colisión, hex/iso.
- **Unity — Tilemap Renderer reference** (docs.unity3d.com/Manual/tilemaps) — Mode Chunk vs Individual vs SRP Batch (trade-off batching vs composición), Sort Order (default Bottom Left), Detect Chunk Culling Bounds, Sorting Layer/Order in Layer, Mask Interaction, Material default Sprite-Lit-Default.
- **Unity — Pixel Perfect Camera** (docs.unity3d.com, URP 2D) — Asset Pixels Per Unit, Reference Resolution, Upscale Render Texture, Pixel Snapping, Crop Frame X/Y, Stretch Fill, Run In Edit Mode, Current Pixel Ratio.
- **Lospec — Palette List** (lospec.com/palette-list) — catálogo (~4.382 paletas al 2026-07-20), filtrado por conteo exacto/min/max de colores y tags (hardware/artist/gameboy).
- **Saint11 / Pedro Medeiros — Pixel Art Tutorials** (saint11.art) — colección de tutoriales gratuitos incluyendo "Tiles", "Outlines", "Fundamentals", "Shading", "Alignment" (referencia canónica de técnica de pixel art).

Referencias reconocidas del oficio (conocimiento establecido, NO re-verificadas por fetch esta sesión — ver gaps):

- **Números de autotiling** 16 (4-bit, solo bordes) / 256→47 (blob 8-bit) / 16 (dual-grid por esquinas) — canon de gamedev/pixel art (cr31 "Tilesets", Boris the Brave "Blob Tileset / Terrain autotiling").
- **Pixel Logic** — Michael Azzi (MortMort) — manual de pixel art (clusters, banding, tiling, paletas).
- **Paletas de referencia** por conteo (catalogadas en Lospec): PICO-8 = 16, DawnBringer-16 = 16, DawnBringer-32 = 32, Sweetie-16 = 16, Endesga-32 = 32, AAP-64 = 64, Resurrect-64 = 64.
- **§13 (Composición de un nivel 2D con tiles)**: criterio de producción/oficio (silueta antes que detalle, presupuesto de tiles por pantalla, blockout antes de dibujar el set de autotile completo), en la misma categoría que §3/§9/§10 — no proviene de una doc puntual; la mecánica/ritmo de nivel en sí está en [ver: gamedev/level-design], no repetida aquí.

**Corrección de auditoría (2026-07-20, esta revisión):** el investigador reportó el paquete `com.unity.2d.tilemap.extras` como v4.0.2 al 2026-07. Re-verificado contra `docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@latest` (redirige a `@9.0`) y su changelog: la versión vigente es **9.0.0**, release 19-may-2026. El contenido técnico (Rule Tile, 3×3, This/Not This/Don't Care, Rule Transform, Output, brushes) es idéntico entre versiones — solo la etiqueta de versión estaba desactualizada; corregida en §5 y en Fuentes. El Cell Size (1,1,0) de Grid/Tilemap se re-confirmó como el valor de ejemplo usado por la doc oficial de Unity (class-Grid), no como "default" documentado explícitamente — la distinción no cambia el consejo práctico.

Bases ya sintetizadas (cross-ref, no repetir): [ver: modelado/entornos-modulares] (kits modulares 3D, romper repetición, seamless/trim), [ver: unity/rendering-urp] (Luces 2D, sorting, Sprite Atlas, overdraw, post-processing), [ver: pipeline/recetas-generos] (Tilemap+Collider en plataformas, parallax en Unity), [ver: gamedev/level-design] (composición y ritmo del nivel), [ver: gamedev/arte-direccion] (paleta, contraste, perspectiva atmosférica). Dentro de arte-2d: [ver: pixel-art], [ver: sprites-produccion], [ver: aseprite-flujo], [ver: 2d-a-unity].
