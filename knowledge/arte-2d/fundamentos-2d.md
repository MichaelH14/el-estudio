# Fundamentos de arte 2D para juegos

> **Cuando cargar este archivo:** al arrancar la producción de arte 2D de un juego (pixel art, sprites, tiles, animación 2D), al elegir la resolución base y el PPU, al definir el estilo/paleta/escala que todos los assets deben respetar, o al orientarte sobre qué archivo del bloque `arte-2d` abrir para una tarea concreta. Es el hub del bloque: los fundamentos transversales viven aquí; cada técnica profunda vive en su sibling. Equivalente 2D de [ver: modelado/fundamentos-3d]. El *qué* estético (emoción, pilares, estilo×equipo) lo decide [ver: gamedev/arte-direccion]; esto es el *cómo* de producción 2D.

## 1. Mapa del bloque arte-2d (a dónde ir)

Este archivo cubre lo transversal. Para el detalle, ir al sibling:

| Necesito… | Archivo |
|---|---|
| Técnica de pixel (shading, ramps, dithering, anti-alias manual, outlines/selout, hue-shift) | [ver: pixel-art] |
| Producir el set de sprites de un personaje/enemigo (poses, model sheet, hoja de export, pivotes) | [ver: sprites-produccion] |
| Animar en 2D (frame a frame, cutout/esqueletal, frame counts, timing) | [ver: animacion-2d] |
| Tilesets, autotiling, mundos y parallax | [ver: tilesets-mundos] |
| Operar Aseprite (atajos, tags, slices, export, CLI, scripts Lua) | [ver: aseprite-flujo] |
| Importar y montar todo en Unity (PPU, Pixel Perfect Camera, Sprite Atlas, Tilemap, 2D lights) | [ver: 2d-a-unity] |
| Arte de UI/HUD 2D (9-slice, iconos, fuentes bitmap) | [ver: ui-2d-arte] |
| Dirección de arte, paleta como identidad, readability teórica, estilo×equipo | [ver: gamedev/arte-direccion] |
| UX/onboarding, jerarquía de HUD, accesibilidad | [ver: gamedev/ux-ui-onboarding], [ver: ux-ui/accesibilidad] |
| Implementar el género (plataformas, top-down, etc.) en Unity | [ver: pipeline/recetas-generos] |

Regla del hub: no repetir lo que ya está en `gamedev/arte-direccion` (dirección) ni en los siblings (técnica). Aquí solo lo que ata todo: resolución/PPU, readability al tamaño real, paleta maestra, composición en capas, escala y el *style lock*.

## 2. Estilos 2D: coste real de producción (para dev solo)

La matriz estilo×equipo y el "coste del asset #200" están en [ver: gamedev/arte-direccion §3] — no se repiten. Aquí el ángulo de **producción 2D**: entrega nativa, coste de animación y herramienta.

| Estilo | Entrega / resolución nativa | Coste de animación | Herramienta base | Riesgo de producción | Cuándo (dev solo) |
|---|---|---|---|---|---|
| **Pixel art** | Baja fija (p.ej. sprites 16–48 px), 1 densidad, escalado entero | Frame a frame: cada frame es trabajo manual; escala mal a muchos frames | Aseprite | "Barato" es mito a alta fidelidad; mezclar densidades rompe el look al instante | Base 2D sólida, resolución baja y consistente, pocos frames bien elegidos |
| **Hand-drawn / cartoon** | Alta (vector o raster grande), luego escala a pantalla | El más caro en 2D: cada frame es una ilustración completa | Krita / Procreate / Toon Boom | Se ahoga en volumen de animación (Cuphead necesitó equipo) | Solo con artista dedicado y scope de animación acotado |
| **Vector / flat** | Independiente de resolución; se rasteriza o se importa como SVG/mesh | Bajo si se anima por transform/tween; alto si se redibuja | Inkscape / Affinity / Figma | Monotonía; se ve genérico sin diseño gráfico fuerte | Puzzle/móvil, UI-heavy, claridad > textura, sin ilustrador |
| **Painted** | Raster grande (fondos), sprites pintados | Muy alto por frame; se suele reservar a fondos estáticos + personajes cutout | Krita / Photoshop | Frame-by-frame pintado es inviable en volumen | Fondos y key art pintados + gameplay resuelto por otra vía |
| **Cutout / esqueletal** | Piezas separadas (torso, brazos, cabeza) a resolución nativa | Amortiza: 1 rig → muchas animaciones, blending, re-timing barato | Spine / DragonBones / Unity 2D Animation | Se nota "papel recortado" si el estilo pide deformación dibujada | Necesitas volumen de animación con equipo mínimo. Detalle en [ver: animacion-2d] |

Notas de producción cruzadas con [ver: gamedev/arte-direccion §3]:
- El pipeline **híbrido 3D→sprites** (Dead Cells) es la salida cuando el volumen de animación 2D te ahoga: model sheet → rig 3D → render por frame a resolución mínima sin AA → sprites. Una persona anima todo el bestiario.
- El estilo se prueba **en engine, con la cámara real, en movimiento** — nunca aprobado en el canvas de Aseprite ampliado.

## 3. Resolución base y PPU (el número que gobierna todo)

Es la decisión más irreversible del arte 2D. Se fija **antes** de producir un solo asset. Todo lo demás (tamaño de sprite, tile, paleta, densidad de detalle) cuelga de aquí.

### 3.1 PPU: el puente píxel↔mundo

- **PPU (Pixels Per Unit)** = cuántos píxeles de la textura equivalen a 1 unidad de mundo en Unity ("the number of pixels of width/height in the Sprite image that correspond to one distance unit in world space" — Unity, Sprite import). El **default de Unity es 100** (pensado para arte no-pixel, tipo vector/painted escalado).
- Convención pixel art: **PPU = tamaño del tile**. Si tu tile/celda es 16 px, PPU = 16 → 1 tile = 1 unidad de mundo → la física, la cámara y el level design piensan en tiles enteros. Con tile 32 → PPU 32.
- **Consistencia obligatoria**: todos los sprites del juego con el MISMO PPU, y ese PPU = `Asset Pixels Per Unit` de la Pixel Perfect Camera ("Match this value to the Pixels Per Unit values of all Sprites" — Unity, Pixel Perfect Camera). Mezclar PPU = mezclar densidades = look roto. Detalle de import en [ver: 2d-a-unity].

### 3.2 Elegir la resolución interna (virtual) del juego

Se renderiza a una resolución interna baja y se escala por **múltiplos enteros** a la pantalla. Escalas no-enteras = píxeles deformados (unos de 2px, otros de 3px). Escaleras 16:9 que dan 1080p/4K exactos por entero:

| Resolución interna | ×3 | ×4 | ×5 | ×6 | Nota |
|---|---|---|---|---|---|
| **320×180** | 960×540 | 1280×720 | 1600×900 | **1920×1080** | La más común; ×12 = 4K exacto |
| **384×216** | 1152×648 | 1536×864 | **1920×1080** | 2304×1296 | Un poco más de campo visual |
| **480×270** | 1440×810 | **1920×1080** | 2400×1350 | 2880×1620 | Sprites con más detalle |
| **640×360** | **1920×1080** | 2560×1440 | 3200×1800 | 3840×2160 | Casi "HD pixel"; sprites grandes |

Referencias de hardware histórico (especificaciones conocidas, útiles como norte estético): NES 256×240, SNES 256×224, Game Boy Advance 240×160, Game Boy 160×144. No son 16:9 — usar solo como brújula de densidad, no como resolución de un juego moderno widescreen.

Heurística: **más chica la resolución interna → más "retro" y más barato animar** (menos píxeles que mover por frame) pero menos detalle y menos campo visual. Elegir por el género y por cuánto puedes animar, no por gusto estético aislado.

### 3.3 Autoría a resolución nativa (regla de oro)

- Dibujar **a 1×**, al tamaño real que tendrá en pantalla. Nunca dibujar grande y "reducir": el detalle sub-píxel se pierde y el resultado se ve sucio.
- Nunca escalar un sprite terminado por un factor **no entero** ni con filtrado. Escalado solo ×2, ×3, ×4 con **Filter Mode = Point (no filter)** ("The texture appears blocky up close" — Unity).
- Un personaje "grande" no es un sprite grande escalado: es un sprite con **más píxeles de alto** dentro de la misma densidad. Personaje de 16 px vs 32 px de alto = distinta cantidad de píxeles, misma resolución de píxel.

### 3.4 Presupuesto de píxeles por asset

Fijar y no violar (ejemplo para base tile 16 px):

| Asset | Alto típico (px) |
|---|---|
| Tile / celda | 16 (u 8 / 32) |
| Personaje chibi/pequeño | 16–24 |
| Personaje "heroico" jugable | 24–48 |
| Enemigo grande / mini-jefe | 48–96 |
| Jefe / pieza única | 96–256+ |
| Icono de UI | múltiplo del tile (16/24/32) |

## 4. Readability al tamaño de juego (no al zoom)

La teoría de siluetas, contraste equipo→clase→arma y test de escala de grises está en [ver: gamedev/arte-direccion §5] — no se repite. Aquí lo específico de 2D a resolución baja:

- **Todo se juzga a 1×**, en la pantalla y densidad reales — no al 800% de Aseprite. Lo que se lee al zoom puede ser papilla a tamaño de juego. Test permanente: ventana de preview a 100% al lado del canvas.
- **Silueta primero**: rellenar el sprite de un color plano; si no se distingue de otro rol o del fondo, rediseñar antes de detallar. En pixel art, la silueta se construye con contorno neto — a 16 px no hay lugar para forma ambigua.
- **Contraste de valor > hue**: a resolución baja el ojo lee masas de luz/sombra antes que color. Sprite y fondo deben separarse en escala de grises. Fondo desaturado y de bajo contraste; sprite jugable con el contraste alto.
- **Outline como separador figura-fondo**: negro puro, oscuro coloreado, o *selout* (outline selectivo que aclara donde da la luz). El outline debe garantizar lectura contra el fondo **más ruidoso y el más oscuro** del juego. Técnica en [ver: pixel-art].
- **Móvil / pantalla pequeña**: el sprite compite con dedos, DPI alto y tamaño físico chico. Elemento jugable mínimo legible ≈ que ocupe suficientes píxeles físicos tras el escalado; iconos de HUD nunca por debajo del tamaño de toque cómodo. Detalle de UI y accesibilidad en [ver: ui-2d-arte], [ver: ux-ui/accesibilidad].
- **Áreas de descanso**: zonas planas sin detalle. A baja resolución el detalle solo lee por contraste con vacío; sprite todo texturizado = ruido ilegible.

## 5. Paleta maestra del juego

Limitar el color es a la vez **estética, identidad y disciplina de producción**. Una paleta cerrada hace que assets de distintas sesiones (o distintos artistas / un agente IA) se vean del mismo juego. El diccionario funcional del color (rojo=daño, etc.) está en [ver: gamedev/arte-direccion §4] — no se repite; aquí la construcción técnica.

### 5.1 Paletas de referencia (Lospec, verificadas)

| Paleta | Colores | Autor / origen | Uso |
|---|---|---|---|
| **PICO-8** | 16 | Fantasy console Lexaloffle | "La" paleta de arranque; enorme cantidad de combos con 16 |
| **Sweetie 16** | 16 | GrafxKid (default de TIC-80) | Proyectos chicos, cálida y balanceada |
| **Endesga 32** | 32 | ENDESGA (creada para NYKRA) | Muy popular para game art general |
| **Resurrect 64** | 64 | Kerrie Lake | Uso general amplio; ~342k descargas en Lospec |
| **AAP-64** | 64 | Adigun A. Polack | Paleta general grande, bien rampada |

Lospec Palette List: base de datos de **~4.380** paletas (a jul-2026) entre hardware histórico y paletas de artistas. Elegir una hecha (o partir de ella) es más rápido y más coherente que inventar color a ojo.

### 5.2 Cuántos colores

- **Muy limitada (≤16)**: máxima identidad y coherencia, más barato de mantener; te obliga a reusar color y a resolver con valor. Ideal dev solo / low-res.
- **Media (32–64)**: margen para varios biomas/ramps sin perder unidad. La mayoría de juegos pixel modernos.
- Regla: primero fijar el **total del juego**, luego repartir en ramps. No agregar un color nuevo por asset — eso es *palette drift* [ver: gamedev/arte-direccion].

### 5.3 Ramps de color (la unidad de trabajo, no el color suelto)

Un *ramp* es una rampa de valores del mismo material (p.ej. piel: sombra→medio→luz). Se pinta y se sombrea eligiendo el siguiente escalón del ramp, no un color arbitrario.

- **3–5 escalones por ramp** cubre la mayoría de materiales a resolución baja.
- **Hue shifting**: al subir el valor, girar el matiz hacia cálido (amarillo) en las luces y hacia frío (azul/púrpura) en las sombras — nunca oscurecer bajando solo el brillo del mismo hue. Da vida y cohesión. Técnica detallada en [ver: pixel-art].
- **Ramps compartidos entre assets** = coherencia automática y palette-swap barato para variantes de enemigo.

### 5.4 Indexed mode en Aseprite (disciplina técnica)

- Modo **Indexed**: cada píxel guarda un índice (0–255) a la paleta; hasta **256 colores**. Cambiar un color de la paleta **recolorea al instante** todos los píxeles que lo usan (Aseprite docs) → editar la paleta maestra propaga a todo el arte.
- Índice 0 = transparente por defecto (configurable en Sprite Properties).
- Trabajar en Indexed **impone** la paleta: no puedes pintar un color fuera de ella por accidente. Es la garantía técnica del *palette lock*. Setup en [ver: aseprite-flujo].

## 6. Composición de pantalla 2D y capas

La composición espacial vs de plano y el guiado del ojo (landmarks, luz como imán, jerarquía por contraste) están en [ver: gamedev/arte-direccion §6] — no se repiten. Aquí la mecánica de **capas 2D**:

| Capa | Contenido | Tratamiento visual | En Unity |
|---|---|---|---|
| **Background (fondo)** | Cielo, montañas, skyline | Menor contraste y saturación, valores agrupados, poco detalle | Sorting Layer trasera, parallax lento |
| **Midground** | Ambiente lejano no colisionable | Intermedio; separa por valor del gameplay | Sorting Layer media |
| **Gameplay plane** | Tiles sólidos, personaje, enemigos, pickups | Máximo contraste y saturación; aquí vive la lectura | Tilemap + sprites, colisión |
| **Foreground** | Vegetación/columnas delante del jugador | Silueta oscura, puede desenfocar/oscurecer; parallax rápido | Sorting Layer delantera, orden mayor |
| **UI / HUD** | Vida, score, botones | Fuera del mundo, contraste intocable | Canvas aparte [ver: ui-2d-arte] |

Reglas 2D:
- **Profundidad por valor y saturación**, no por perspectiva: capas lejanas más claras/desaturadas/azuladas (perspectiva atmosférica), gameplay al frente con el punch. Si el fondo compite con el personaje, aplanar el fondo, no gritar más el sprite.
- **Parallax**: velocidad de scroll por capa proporcional a la "distancia"; fondo casi quieto, foreground más rápido que el gameplay. Vende profundidad sin 3D. Producción de capas en [ver: tilesets-mundos].
- **Orden de dibujo**: en Unity se resuelve con **Sorting Layers** + **Order in Layer** (y en top-down, orden por Y). Un pixel bien pintado en la capa equivocada se ve mal. Detalle en [ver: 2d-a-unity], [ver: unity/rendering-urp].
- **Foco**: el punto jugable importante debe ser el de mayor contraste local de la pantalla. Guiar el ojo con contraste y color reservado, no con líneas de composición (el jugador no juega el screenshot que compusiste — [ver: gamedev/arte-direccion §6]).
- **2D lights (URP)** como refuerzo de composición: tipos **Global** (ilumina todo por igual, uno por blend style y sorting layer), **Spot**, **Sprite** y **Freeform** (Unity URP). La luz hunde el fondo y levanta el foco sin repintar assets. Detalle en [ver: 2d-a-unity].

## 7. Escala y proporción de personajes/objetos 2D

La proporción se mide en **cabezas** (altura total / altura de la cabeza). Fijar el nivel para TODO el elenco antes de dibujar; mezclar proporciones sin querer rompe la unidad.

| Estilo de proporción | Cabezas (aprox.) | Lectura | Ejemplo de uso |
|---|---|---|---|
| **Chibi / super-deformed** | 2–3 | Cabeza enorme, cuerpo mínimo; máxima "cuteness" y expresividad facial | RPG/casual, sprites 16–32 px |
| **Mid / cartoon jugable** | 4–5 | Balance acción/carisma; estándar de plataformas pixel | Plataformas, action |
| **Heroico** | 6–7 | Atlético, imponente; menos "tierno" | Beat'em up, action-RPG |
| **Realista** | 7.5–8 | Adulto proporcional; caro de leer a baja resolución | Poco común en pixel low-res |

Reglas:
- A **resolución baja, proporciones bajas (chibi/mid)**: con 16–32 px de alto no caben 8 cabezas legibles; la cabeza necesita píxeles para la cara. Por eso el pixel art tiende a chibi/mid.
- **Escala relativa consistente** entre personaje, enemigos, props y tiles: un cofre, una puerta y el héroe deben respetar la misma "regla de metros por píxel". Un prop fuera de escala se lee como bug.
- La **cabeza y el arma/manos** son donde el jugador mira: concentrar ahí contraste y color (hereda de la jerarquía de lectura, [ver: gamedev/arte-direccion §5]).
- Model sheet con la altura marcada en píxeles como referencia de todo el cast en [ver: sprites-produccion].

## 8. Consistencia entre assets: el *style lock* 2D

El style guide general (pilares, do's & don'ts, visual target) está en [ver: gamedev/arte-direccion §2]. Aquí la **hoja de specs 2D** concreta que congela el estilo. Si dos assets de dos sesiones cumplen esto y no se distinguen, funciona.

| Decisión | Qué fijar (ejemplo) |
|---|---|
| Resolución interna / PPU | 320×180 · PPU 16 |
| Tamaño de tile | 16×16 |
| Alturas de personaje | héroe 32 px, enemigo base 24 px, jefe 96 px |
| Paleta maestra | Endesga 32 (hex exactos, ramps definidos) |
| Grosor de línea / outline | 1 px, negro coloreado, política de *selout* sí/no |
| Anti-aliasing | manual, solo curvas clave / prohibido — decidir uno |
| Dithering | permitido para gradientes / prohibido — decidir uno |
| Ángulo de luz | top-left constante en todo el juego |
| Nivel de detalle | "medio bajo": áreas de descanso obligatorias |
| Perspectiva | side-view / top-down 3⁄4 / isométrica — una sola |
| Frame counts base | idle, walk, run, attack (rangos en [ver: animacion-2d]) |
| Export | tamaño de canvas, pivote, atlas, naming (en [ver: sprites-produccion], [ver: aseprite-flujo]) |

Lo que más rompe la consistencia en 2D (auditar siempre):
- **Densidades de píxel mezcladas** (sprite 16px junto a uno 32px, o un asset importado de un pack a otra escala) → el error #1 del pixel art.
- **Ángulo de luz inconsistente** entre assets → sombras que "no cuadran".
- **Outline en unos sí y en otros no**, o grosor variable.
- **Colores fuera de la paleta** → trabajar en Indexed lo previene (§5.4).

## 9. Puente con dirección de arte, UI y Unity

- **Dirección ↔ producción**: [ver: gamedev/arte-direccion] decide emoción, pilares, paleta-como-marca, estilo×equipo y readability teórica. Este bloque `arte-2d` **ejecuta** eso en píxeles. El estilo elegido allí se aterriza aquí en resolución/PPU/paleta/specs.
- **↔ UI**: el arte de HUD/menús/iconos es [ver: ui-2d-arte]; la UX, jerarquía de HUD y onboarding son [ver: gamedev/ux-ui-onboarding] y [ver: ux-ui/patrones-ui]. La UI hereda la MISMA paleta y el mismo diccionario de color del juego; nada de look "default de engine".
- **↔ Unity / implementación**: import, PPU, Pixel Perfect Camera, Sprite Atlas (junta texturas en un draw call), Tilemap, 2D lights → [ver: 2d-a-unity], [ver: unity/rendering-urp], [ver: unity/assets-pipeline-git]. El género (cómo se monta el juego) → [ver: pipeline/recetas-generos], [ver: pipeline/produccion-solo-dev].
- **↔ animación**: principios y ciclos comparten teoría con 3D → [ver: animacion-2d], [ver: animacion3d/ciclos-locomocion].

## Reglas prácticas

1. Fija **resolución interna + PPU + tamaño de tile ANTES** de producir un solo asset; es la decisión más irreversible. Escoge de la escalera 16:9 (320×180 es el default seguro).
2. **Un solo PPU** en todo el juego, igual al `Asset Pixels Per Unit` de la Pixel Perfect Camera; PPU = tamaño de tile por convención.
3. Escala **solo por múltiplos enteros** (×2/×3/×4) con **Filter Mode = Point**; nunca factores no enteros ni filtrado bilineal en pixel art.
4. Dibuja **a resolución nativa (1×)**; jamás dibujar grande y reducir. Un personaje grande = más píxeles de alto, no un sprite escalado.
5. Juzga **todo a 100%** en la pantalla real, en movimiento, con la cámara del juego — no al zoom de Aseprite ni como imagen estática.
6. **Test de silueta** (relleno plano) antes de detallar cualquier personaje/enemigo; si no se distingue de otro rol o del fondo, rediseña.
7. **Contraste de valor manda a baja resolución**: sprite jugable con contraste alto, fondo desaturado y de bajo contraste; verifica en escala de grises.
8. Outline garantiza lectura contra el **fondo más oscuro y el más ruidoso** del juego.
9. Define la **paleta maestra cerrada** (parte de una de Lospec: PICO-8/Sweetie-16 16 col, Endesga-32 32, Resurrect-64/AAP-64 64) con hex y ramps; no agregues color por asset.
10. Trabaja en **Indexed mode** para que la paleta sea imposible de violar; editar la paleta recolorea todo.
11. Sombrea por **ramps de 3–5 escalones con hue shifting** (cálido a la luz, frío a la sombra), no bajando brillo del mismo hue.
12. Compón en **capas** (fondo/midground/gameplay/foreground/UI) separadas por valor y saturación; profundidad por perspectiva atmosférica + parallax, no por líneas.
13. **Ángulo de luz único** en todo el juego (p.ej. top-left); auditar assets que no lo respeten.
14. **Escala relativa consistente**: personaje, enemigos, props y tiles bajo la misma "regla de metros por píxel".
15. Fija **una proporción de cabezas** para todo el elenco (chibi 2–3 / mid 4–5 / heroico 6–7); a baja resolución tiende a chibi/mid.
16. Escribe la **hoja de specs 2D** (§8) y compara cada asset nuevo contra ella y contra el visual target, no contra "¿se ve bien solo?".
17. Auditar siempre **densidades de píxel mezcladas** (assets de packs, escalados sueltos): el error #1 del pixel art.
18. Concentra **contraste y color en cabeza + arma/manos**; deja áreas de descanso planas (el detalle solo lee por contraste con vacío).
19. La **UI hereda paleta y diccionario de color** del juego; contraste de texto intocable, cero look de engine.
20. Si el volumen de animación te ahoga, evalúa **cutout/esqueletal o pipeline 3D→sprites** antes de recortar contenido [ver: animacion-2d].

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Elegir la resolución/PPU tarde y ya con assets hechos | Fijarlo en el día 0; reescalar assets después es rehacerlos |
| PPU distinto entre sprites, o ≠ al de la Pixel Perfect Camera | Un solo PPU global = `Asset Pixels Per Unit`; auditar imports |
| Escalado no entero o filtrado bilineal → píxeles deformados | Solo múltiplos enteros, Filter Mode Point, resolución interna que dé 1080p/4K exacto |
| Dibujar grande y reducir "para tener detalle" | Autoría a 1×; el detalle sub-píxel se pierde al reducir |
| Aprobar el arte al 800% de zoom | Preview a 100% permanente; validar en engine en movimiento |
| Mezclar densidades de píxel (16px junto a 32px, packs a otra escala) | Specs de densidad únicos; auditar todo asset importado |
| Personaje que se pierde sobre ciertos fondos | Test de silueta + escala de grises + outline; aplanar el fondo, no gritar el sprite |
| Paleta que crece un color por asset (drift) | Total del juego fijo primero; trabajar en Indexed; ramps compartidos |
| Sombrear bajando brillo del mismo hue (barro muerto) | Ramps con hue shifting: cálido a la luz, frío a la sombra |
| Fondo tan contrastado/saturado como el gameplay → todo plano | Perspectiva atmosférica: fondo claro/desaturado/azulado, gameplay al frente |
| Todo el sprite texturizado → ruido ilegible a tamaño real | Áreas de descanso planas; detalle solo donde hay lectura (cara/arma) |
| Ángulo de luz distinto entre assets | Un ángulo único declarado en la hoja de specs |
| Props/enemigos fuera de escala relativa | Regla de "metros por píxel" común; model sheet con alturas |
| Querer 8 cabezas realistas en un sprite de 24 px | Bajar la proporción (chibi/mid); a baja resolución no caben cabezas legibles |
| UI "default de engine" pegada sobre arte con identidad | UI hereda paleta, formas y diccionario de color [ver: ui-2d-arte] |
| Elegir hand-drawn/painted sin medir el coste de animación por frame | Matriz de §2 + [ver: gamedev/arte-direccion §3]; cutout o 3D→sprites si hace falta volumen |

## Fuentes

- **Aseprite — Documentation** (aseprite.org/docs): estructura de features (Color Mode, Layers, Animation, Onion Skinning, Tilemap, Slices, Sprite Sheets, CLI). **Color Mode** (aseprite.org/docs/color-mode): RGBA / **Indexed (hasta 256 colores, índice→paleta, editar paleta recolorea todo, índice 0 transparente)** / Grayscale. **CLI** (aseprite.org/docs/cli): batch `-b`, `--sheet`, `--data`, `--sheet-type`, `--split-layers`, `--tag`, `--scale`, `--trim`. Verificado esta sesión.
- **Aseprite — Scripting API** (aseprite.org/api): objetos Sprite, Layer, Cel, Image, Palette, Tag, Tileset/Tile, Frame, Selection; namespaces `app`, `app.command`, `app.fs`, `json`. Verificado.
- **Unity — Sprite (2D and UI) import settings** (docs.unity3d.com, Manual `texture-type-sprite`): PPU = píxeles del sprite por unidad de mundo (default 100); Filter Mode Point ("blocky up close"); Mesh Type Full Rect (auto en sprites <32×32); Pivot; Mipmaps off para pixel art. Verificado.
- **Unity — 2D Pixel Perfect / Pixel Perfect Camera** (com.unity.2d.pixel-perfect manual): `Asset Pixels Per Unit` (igualar al PPU de todos los sprites), `Reference Resolution`, `Upscale Render Texture`, `Pixel Snapping`, `Crop Frame` (X/Y), `Stretch Fill`, `Run In Edit Mode`, `Current Pixel Ratio`. Verificado.
- **Unity — Tilemap** (docs.unity3d.com, Manual tilemap reference): Grid GameObject + Tilemap component, Tile Palette, Tile Anchor (default 0.5,0.5,0), Orientation, Animation Frame Rate, Color/tint. Rule Tile vive en el paquete Tilemap Extras (com.unity.2d.tilemap.extras) — detalle en tilesets-mundos. Verificado (excepto Rule Tile, conocido no re-verificado aquí).
- **Unity — Sprite Atlas** (docs.unity3d.com, Manual atlas landing): combina múltiples texturas en una → un solo draw call para todos sus sprites; V2, variantes por plataforma, carga en runtime. Verificado.
- **Unity — 2D Lights / URP 2D Renderer** (Manual urp Lights-2D-intro): tipos **2D Spot Light, 2D Sprite Light, 2D Freeform Light, 2D Global Light** (uno global por blend style + sorting layer, sin atenuación). Verificado.
- **Unity — 2D Animation package** (com.unity.2d.animation manual): rig y animación de personajes 2D, integración con PSD Importer (importa capas de .psb como Prefab de sprites, "actor"), Asset Upgrader. Skinning Editor/bones/weights/IK: existen pero no detallados en la página intro — ver animacion-2d. Verificado a nivel intro.
- **Lospec — Palette List** (lospec.com/palette-list, ~4.380 paletas a jul-2026) y fichas: **PICO-8 16 col** (Lexaloffle), **Sweetie 16 16 col** (GrafxKid, default TIC-80), **Endesga 32 32 col** (ENDESGA), **Resurrect 64 64 col** (Kerrie Lake), **AAP-64 64 col** (A. A. Polack). Counts verificados contra las fichas individuales.
- **Pixel Art Tutorials — Pedro Medeiros / saint11** (saint11.art, artista de Celeste y TowerFall): ~80+ tutoriales gratis: Fundamentals, Shading, Outlines, Subpixel, Silhouette, Tiles, Modular, Parallax, UI-9-Slice, Isometric, ciclos (Walk, Run, Jump), VFX. Índice de temas verificado.
- **Pixel Logic: A Guide to Pixel Art — Michael Azzi**: guía de referencia reconocida en la comunidad (resolución, paletas, ramps, dithering, anti-aliasing, outlines/selout, animación, tiles). Citada como canon del pixel art; la página de venta no abrió esta sesión (404), así que ningún número concreto de este archivo se atribuye a ella — todos los settings provienen de Aseprite/Unity/Lospec verificados arriba.
- **Cruce interno**: dirección de arte, readability teórica, color-como-lenguaje, estilo×equipo y pipeline 3D→sprites en `gamedev/arte-direccion` (ya en este repo) — no reproducidos aquí.
