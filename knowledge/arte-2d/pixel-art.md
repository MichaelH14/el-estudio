# Pixel art

> **Cuando cargar este archivo:** al producir o dirigir arte en pixel art para un juego real — elegir resolución de sprite y paleta, dibujar líneas limpias, sombrear, hacer dithering/anti-aliasing a mano, animar frame a frame, y dejarlo nítido dentro de Unity. Es el manual de PRODUCCIÓN pixel art. La decisión de estilo (¿pixel art sí o no?, coste, coherencia) está en [ver: gamedev/arte-direccion]; los sprites/animación/tiles como piezas de producción en [ver: sprites-produccion], [ver: animacion-2d], [ver: tilesets-mundos]; el flujo Aseprite en [ver: aseprite-flujo]; la implementación en engine en [ver: 2d-a-unity] y [ver: unity/rendering-urp].

## 1. Qué hace al pixel art pixel art

No es "arte de baja resolución con filtro retro". Es una disciplina definida por dos restricciones que el artista impone a propósito:

1. **Resolución baja deliberada** — pocos píxeles, cada uno significativo. El límite obliga a decidir qué información sobrevive.
2. **Control píxel a píxel** — cada píxel se coloca a mano y se justifica. El programa no interpola, no antialiasa solo, no suaviza: si un píxel está fuera de sitio, se ve.

Corolario práctico (regla que un agente rompe primero): **nada de escalar, rotar en ángulos libres, ni transformar con filtrado** una vez fijada la grilla. Rotar un sprite 37° o escalarlo ×1.5 genera píxeles de tamaños distintos y mata el estilo al instante. Toda transformación es entera (×2, ×3, ×4) y sin interpolación [ver: gamedev/arte-direccion §8].

Lo que distingue pixel art de "arte pequeño":
- Un asset a baja resolución **hecho con pincel suave y luego reducido** NO es pixel art: tiene bordes borrosos, cientos de colores, ruido. Pixel art tiene bordes controlados, paleta contada y clusters limpios.
- La prueba: si al ampliar ×800 cada píxel es una decisión (no un promedio de un filtro), es pixel art.

## 2. Resolución y canvas

Decidir el tamaño del sprite ANTES de dibujar nada, y no cambiarlo. Es la decisión más cara de revertir.

| Resolución del sprite (personaje) | Referencia histórica / de estilo | Trade-off |
|---|---|---|
| **16×16** | NES, Game Boy; enemigos/props | Máxima economía, animación baratísima; casi no hay sitio para detalle ni expresión facial |
| **16×24 / 24×24** | Personajes NES/SNES tempranos | Suficiente para una silueta clara y 1-2 acentos de color |
| **32×32** | SNES, Genesis; el "sweet spot" indie | Detalle legible + animación aún manejable; el default sensato para un solo dev |
| **48×48 / 64×64** | Pixel art moderno HD (Hyper Light, Blasphemous) | Mucho detalle; cada frame de animación cuesta 3-4× más que a 32px |
| **≥ 96px** | Dead Cells, bosses, splash | Ya es semi-ilustración; solo con pipeline que amortice (3D→sprites) [ver: gamedev/arte-direccion §8] |

Reglas de canvas:
- **Consistencia de resolución en TODO el juego.** La densidad de píxel (cuántos píxeles de pantalla mide un píxel de arte) tiene que ser única. Un personaje de 32px junto a un tile cuyo píxel mide la mitad = dos resoluciones en pantalla = amateur inmediato. Fijar una "unidad de píxel" global y auditar todo asset importado de packs contra ella.
- **El tile es la unidad del mundo**: elegir tamaño de tile (habitual **16×16 o 32×32**) junto con el tamaño de personaje, porque definen la escala de todo [ver: tilesets-mundos].
- **Resolución de juego (virtual)**: se diseña para una ventana lógica baja — p.ej. **320×180** (16:9) o **384×216**, escalada entera hasta el monitor. Esa cifra fija cuántos tiles/personajes caben en pantalla y es lo que configura la Pixel Perfect Camera (§9).
- Trabajar a 100% mientras dibujas para juzgar el resultado real; usar el zoom solo para colocar píxeles, no para evaluar.

## 3. Paletas, ramps y hue shifting

El color es donde el pixel art amateur se delata más rápido. La restricción es una ventaja: paleta limitada = decisiones más fuertes y estilo más identitario [ver: gamedev/arte-direccion §4].

### Paleta limitada y ramps
- **Paleta global acotada**: 16-32 colores para todo el juego es un rango sano; muchos clásicos vivían con 16. Menos colores = más cohesión y menos trabajo de mantenimiento.
- Aseprite: trabajar en **modo Indexed** ata el sprite a la paleta (máx. 256 colores, cada píxel es un índice 0-255); cambiar un color de la paleta reactualiza todos los píxeles que lo usan — recolorear el juego entero es editar la paleta [ver: aseprite-flujo].
- Un **ramp** es una rampa de valor: la secuencia de colores de un mismo material de sombra→luz. Se dibuja pensando en ramps, no en colores sueltos. Regla de Slynyrd: **~9 swatches por ramp** es un punto de partida sólido; el brillo sube de izquierda (sombra) a derecha (luz).
- **Colores compartidos entre ramps** (una sombra que sirve a varios materiales) reduce la paleta y unifica la imagen. La saturación no debe reventarse: pica en los **valores medios**, no en los extremos — brillo alto + saturación alta = colores que queman el ojo (Slynyrd).

### Hue shifting (la técnica que cambia todo)
No oscurecer un color bajándole solo el brillo. **Desplazar el TONO (hue) además del valor**:
- **Sombras → hacia colores fríos** (azul/violeta), reduciendo brillo.
- **Luces → hacia colores cálidos** (amarillo/naranja), subiendo brillo.
- Slynyrd cuantifica su método: **hue positivo ~20° entre swatch y swatch** al subir brillo; el resultado es que las luces se calientan y las sombras se enfrían de forma natural, y todos los colores quedan rodeados de vecinos que armonizan.
- Un ramp sin hue shift (solo más oscuro/más claro del mismo hue) se ve plano, plástico, muerto. Con hue shift se ve vivo. Es el salto #1 de calidad tras aprender a dibujar la línea.

### Paletas famosas (referencia)
No hace falta inventar paleta: partir de una probada y editarla. Todas en [lospec.com/palette-list](https://lospec.com/palette-list) (~4.382 paletas al 2026-07), descargables como .ase/.gpl/.pal/.png.

| Paleta | Colores | Origen / uso |
|---|---|---|
| **PICO-8** | 16 (verificado) | Fantasy console Lexaloffle; el "16 default" moderno, muy usado en jams |
| **DawnBringer 16 (DB16)** | 16 (verificado) | DawnBringer; propósito general, el más icónico de 16 |
| **DawnBringer 32 (DB32)** | 32 (en el nombre) | Extensión de DB16; el general-purpose de 32 más famoso |
| **Endesga 32 (EDG32)** | 32 (en el nombre) | Paleta artista-moderna muy popular para juegos |
| **Sweetie 16** | 16 (en el nombre) | GrafxKid; cálida, muy legible |
| **AAP-64 / Resurrect 64** | 64 (en el nombre) | Paletas grandes con rampas ya montadas para trabajo detallado |

(El conteo de cada una está en su propio nombre salvo PICO-8; el de PICO-8 y DB16 los confirmé contra su página de Lospec, el resto no los abrí uno a uno.)

## 4. Líneas y clusters

La línea limpia es la base. Un cluster es un grupo de píxeles del mismo color que forma una forma.

### Pixel-perfect lines
- Una diagonal limpia avanza en **tramos regulares** (1-1-1, o 2-2-2, o 3-3-3 píxeles) — la pendiente es constante. Un tramo de 2 seguido de uno de 1 en la misma curva produce un **jaggie** (escalón roto) que el ojo capta como suciedad.
- **Doubles / "esquinas L"**: un píxel extra que sobresale en la esquina de una diagonal, formando una L de 3 píxeles. Rompen la línea de 1px. Se eliminan a mano o con la opción **Pixel-perfect** de las herramientas freehand de Aseprite (checkbox en la barra de opciones del lápiz), que evita esos dobles píxeles/esquinas mientras trazas en modo 1px [ver: aseprite-flujo]. (No inventar atajo: es una opción de la barra de contexto del Pencil, documentada en Aseprite.)
- **Jaggies y cómo suavizar la curva a mano**: para que una curva "acelere" bien, los tramos deben decrecer de forma monótona hacia la parte más vertical (p.ej. 4-3-2-1), nunca alternar (3-1-2). Corregir el tramo, no tapar con anti-aliasing.

### Clusters
- Evitar **píxeles huérfanos** (un solo píxel de un color rodeado de otro) salvo como acento intencional: leen como ruido.
- Evitar el **jaggy de cluster**: bordes de una mancha de color con escalones irregulares. Un cluster limpio tiene borde regular.
- El grosor de outline y de línea interior debe ser **constante** (normalmente 1px a resolución nativa). Líneas que engordan y adelgazan sin querer = falta de control.

## 5. Anti-aliasing manual (AA)

AA en pixel art es **manual y selectivo**: colocar a mano píxeles de un valor intermedio en los "escalones" de una curva para engañar al ojo y suavizarla. No es el AA automático del motor (ese, en pixel art, se APAGA — filtro Point, §9).

Cuándo SÍ:
- Suavizar **curvas y diagonales suaves** donde el escalón se ve feo (rostros, cascos, arcos grandes).
- Bordes internos de formas dentro del sprite (no siempre el outline externo).

Cuándo NO (el look "crujiente" / crisp):
- Estilo de baja resolución que busca el look nítido NES: AA mínimo o nulo. A 16-24px el AA muchas veces **emborrona** más que suaviza.
- **Nunca antialiasar contra el fondo transparente** el borde externo del sprite si el sprite se mueve sobre fondos variados: esos píxeles semitono quedan como halo sucio sobre el fondo equivocado. AA externo solo si el fondo es fijo y conocido.

Reglas de AA a mano (Pixel Logic / saint11):
- **Selective / hinting**: no rellenar toda la curva de semitonos; poner AA solo en el punto donde el escalón es más visible. Sobre-antialiasar (AA en todas partes) devuelve el borrón que querías evitar y desperdicia colores de la paleta.
- El color de AA sale del **ramp** entre los dos que separa (el valor intermedio de la rampa), no un gris cualquiera.
- **No romper la silueta**: el AA no debe engordar la forma ni comerle esquinas.
- Un solo nivel de AA (1 píxel de transición) suele bastar; dos niveles solo en curvas grandes.

## 6. Dithering

Dithering = alternar dos colores en un patrón para simular un tercero o un **gradiente** con pocos colores. Es el truco para degradados sin ampliar la paleta.

| Patrón | Uso |
|---|---|
| **Checkerboard 50%** (damero) | Transición dura entre dos valores; textura |
| **Gradiente graduado** (de denso a disperso) | Simular un degradado suave (cielo, esfera grande) |
| **Bayer / ordenado** | Tramas regulares tipo consola retro |

Cuándo usarlo:
- Superficies grandes y planas que necesitan volumen sin meter colores (cielos, fondos, esferas grandes).
- Estética retro deliberada (evoca hardware limitado).

Cuándo NO:
- **Sprites pequeños en movimiento**: el patrón "hierve" (shimmer) al animar y ensucia. Menos dithering cuanto más pequeño y más movido el sprite.
- Como muleta para no elegir un color intermedio: si un color nuevo resuelve mejor el gradiente y la paleta lo permite, ese color gana al dithering.
- Regla práctica: dithering **entre dos valores contiguos del ramp**, no entre valores lejanos (el salto se nota como banda).

## 7. Shading en pixel art

Sombrear = construir volumen con la rampa de valor, siguiendo una **fuente de luz definida**.

### Pillow shading (el error clásico) vs luz direccional
- **Pillow shading**: sombrear desde los bordes hacia un centro claro, como si la luz saliera del centro del objeto en todas direcciones. Resultado: todo parece un almohadón inflado, sin dirección, sin volumen real. Es el error #1 del principiante.
- **Antídoto**: fijar **UNA dirección de luz** para todo el juego (típico: arriba-izquierda o arriba) y aplicarla consistente. Las luces caen en las caras que miran a la luz; las sombras en las opuestas. El volumen aparece solo cuando hay dirección.

### Banding (a evitar)
- **Banding**: dos bandas de color paralelas que siguen la misma diagonal escalonada, creando una línea gruesa fea donde se tocan (los escalones se alinean y forman un "borde" que no debería existir).
- **Antídoto**: romper la alineación — que el cambio de valor no siga exactamente el mismo contorno escalonado que el borde anterior; desfasar los clusters de sombra respecto al outline.

### Buenas prácticas de shading
- Empezar con **pocos valores** (base + sombra + luz = 3) y añadir solo si hace falta. Muchos ramps de personaje viven con 3-5 valores.
- **Contraste concentrado**: más contraste de valor donde la luz pega fuerte y en los bordes de lectura; menos en zonas planas [ver: gamedev/arte-direccion §5].
- **Ambient occlusion pixel**: oscurecer los recovecos donde dos formas se juntan da profundidad barata.
- El outline puede ser **selective outline (selout)**: outline coloreado (no negro puro) que se aclara en la zona iluminada y se oscurece en la sombra, integrando el sprite con la luz en vez de encerrarlo en negro (técnica de saint11/Pedro Medeiros).

## 8. Sub-pixel animation

El detalle que hace que la animación pixel art se sienta suave a pesar de tener pocos píxeles: **mover partes del cuerpo aunque el movimiento sea de menos de un píxel "aparente"**, redistribuyendo píxeles para sugerir un desplazamiento menor que la grilla.

- **Sub-pixel**: en un idle o una caminata, mover el pecho/cabeza 1px arriba/abajo y ajustar los píxeles vecinos para que la transición se lea como medio píxel. Da vida sin repintar todo el frame (saint11 tiene tutorial dedicado a "subpixel").
- **Economía de frames** (convención de producción, no cifra oficial): menos frames bien elegidos > muchos frames flojos [ver: animacion-2d].

| Animación | Frames típicos | Notas |
|---|---|---|
| Idle | 2-4 | Respiración: sub-pixel de pecho/cabeza; loop suave |
| Walk cycle | 4-8 | Clásico de 4 poses (contact, down, passing, up) espejado |
| Run | 6-8 | Más estirado y con más aire que el walk |
| Ataque | 3-6 | 1 frame de anticipación + 1 de impacto marcado [ver: gamedev/game-feel] |
| Salto | 2-3 estados | Ascenso / cénit / caída (no siempre loop) |

- **Timing en Aseprite**: la duración se fija por frame en milisegundos en el timeline; un frame clave (impacto, cénit) puede durar más para dar peso — no todos los frames duran igual [ver: aseprite-flujo].
- **Onion skinning** de Aseprite (ver el frame anterior/siguiente semitransparente) es la herramienta central para que el sub-pixel sea coherente entre frames [ver: aseprite-flujo].
- Mantener la **silueta legible en cada pose clave**: la animación no puede romper la lectura del personaje en el frame que más se ve [ver: gamedev/arte-direccion §5].
- Cuidado con el "hervor": si demasiados píxeles cambian por frame en zonas planas, el ojo lee ruido, no movimiento. Animar el borde y los acentos, dejar quietas las masas planas.

## 9. Pixel-perfect en el engine (Unity 6)

El pixel art se arruina en el último metro: mal importado en Unity se ve borroso, con píxeles de tamaños distintos o con "jitter" al moverse. Objetivo: **escalado entero y píxeles nítidos**. Detalle de implementación en [ver: 2d-a-unity].

### Import del sprite (Texture Type: Sprite 2D and UI)
| Setting | Valor pixel art | Por qué |
|---|---|---|
| **Filter Mode** | **Point (no filter)** | Bilinear/Trilinear interpolan y emborronan; Point deja el píxel duro (Unity: "appear blocky up close") |
| **Compression** | **None** | La compresión inventa colores fuera de la paleta y ensucia bordes |
| **Generate Mip Maps** | Off | Los mips emborronan a distancia; no aplican a sprites 2D fijos |
| **Pixels Per Unit (PPU)** | **igual para TODOS** los sprites | PPU = píxeles del sprite por 1 unidad de mundo; default de Unity = 100. En pixel art se suele fijar al tamaño de tile (p.ej. **16** o **32**) para que 1 tile = 1 unidad. Mezclar PPU = mezclar densidades de píxel (§2) |
| **Mesh Type** | Full Rect (o Tight) | Full Rect evita recortes raros en sprites con mucho alpha |

### Pixel Perfect Camera (paquete 2D Pixel Perfect / 2D Renderer URP)
Propiedades reales del componente (Unity 6, verificadas contra el manual):

| Propiedad | Qué hace |
|---|---|
| **Asset Pixels Per Unit** | Píxeles que forman 1 unidad de escena. Debe **coincidir con el PPU de import** de los sprites |
| **Reference Resolution** | Resolución baja original para la que diseñaste (p.ej. 320×180). El motor calcula el escalado entero hacia el monitor |
| **Upscale Render Texture** | Renderiza a una RT cercana a la Reference Resolution y luego la agranda: el look más limpio y estable |
| **Pixel Snapping** | Ancla los Sprite Renderers a una grilla en world space al renderizar (solo disponible con Upscale RT **desactivado**) |
| **Crop Frame** | Recorta el viewport con barras negras para respetar la Reference Resolution en el eje marcado |
| **Stretch Fill** | Con Crop Frame en X e Y, expande el viewport manteniendo aspect ratio |
| **Run In Edit Mode** | Previsualiza los cambios en el editor; muestra **Current Pixel Ratio** (relación de escala real) |

Regla de oro del engine: **la cámara nunca produce un ratio de escala no entero.** Si el Current Pixel Ratio sale 2.5, la resolución de ventana no encaja con la Reference Resolution y aparecen píxeles de tamaños distintos ("pixel wobble"). Ajustar Reference Resolution / usar Upscale RT hasta que el ratio sea entero.

### Tiles, atlas y luz
- **Tilemap** (Grid + Tilemap): pinta niveles con tiles sobre una grilla; el cell size del Grid debe casar con el tamaño de tile del arte. Auto-tiling con **Rule Tiles** (paquete 2D Tilemap Extras) [ver: tilesets-mundos, unity/rendering-urp].
- **Sprite Atlas**: empaqueta muchos sprites en una sola textura → reduce el número de draw calls (batching) para los sprites que comparten atlas y material, en vez de uno por textura suelta. En pixel art: Filter Mode **Point**, compresión **None**, y **padding** suficiente para evitar bleeding entre tiles (default de Unity: **4px**).
- **Luces 2D (URP 2D Renderer)**: sprites y tiles usan el shader **Sprite-Lit-Default**, compatible con las Light 2D (Freeform, etc., con falloff y volumétrico). Permiten iluminación dinámica sobre pixel art; requiere **normal maps** por sprite (Secondary Textures en el Sprite Editor) para que el relieve reaccione a la luz. Ojo: la luz suave puede pelear con el look duro del pixel art — usar con intención [ver: unity/rendering-urp].

### Aseprite → Unity
- Exportar **sprite sheet** (packed) + JSON desde Aseprite, o el .aseprite directo con el importer de la comunidad; laminar por tags de animación [ver: aseprite-flujo, 2d-a-unity].
- Slicing en el **Sprite Editor**: Automatic (por transparencia), **Grid By Cell Size** (lo normal para pixel art: fijar 16×16/32×32), Grid By Cell Count, o Isometric Grid; pivotes consistentes (bottom-center para personajes que pisan suelo).

## 10. Runbook: un sprite de personaje de cero a Unity

1. Decidir resolución (p.ej. **32×32**) y tamaño de tile (p.ej. 16×16) del juego; anotarlo como spec fija [ver: gamedev/arte-direccion §2].
2. Elegir/adaptar paleta de Lospec (p.ej. DB32); montar los ramps con hue shifting antes de dibujar; trabajar en modo **Indexed**.
3. Dibujar la **silueta** en 1 color y validar la lectura antes que el detalle (test de silueta) [ver: gamedev/arte-direccion §5].
4. Línea limpia (Pixel-perfect on), luego color base plano, luego shading con dirección de luz global (3 valores → más si hace falta).
5. AA selectivo y selout solo donde el escalón se ve feo; auditar contra pillow shading y banding.
6. Animar por tags con onion skin; empezar por idle y walk; sub-pixel para suavidad.
7. Export sprite sheet + JSON (o .aseprite) [ver: aseprite-flujo].
8. Import en Unity: Filter **Point**, Compression **None**, PPU = tamaño de tile; slice **Grid By Cell Size**; pivote bottom-center.
9. Escena con Pixel Perfect Camera (Asset PPU = import PPU, Reference Resolution con ratio entero); verificar en Play a 1×, 2×, 3×.
10. Revisar EN el juego, en movimiento, contra el fondo más oscuro y el más ruidoso [ver: 2d-a-unity].

## Reglas prácticas

1. Fija resolución de sprite y tamaño de tile ANTES de dibujar; no los cambies a mitad de producción.
2. Una sola densidad de píxel en todo el juego: audita cada asset (y cada pack comprado) contra tu "unidad de píxel" global.
3. Transformaciones solo enteras (×2, ×3, ×4) y sin filtrado; cero rotaciones libres, cero escalados fraccionarios sobre la grilla.
4. Paleta global acotada (16-32 colores); parte de una paleta probada de Lospec y edítala, no inventes de cero.
5. Piensa en ramps, no en colores sueltos; ~9 swatches por ramp, saturación pico en los valores medios (Slynyrd).
6. Hue shifting siempre: sombras hacia frío, luces hacia cálido (~20° de hue por paso), nunca solo subir/bajar brillo.
7. Trabaja en modo Indexed en Aseprite para que la paleta sea editable globalmente.
8. Líneas de pendiente constante (1-1-1 / 2-2-2); elimina doubles y esquinas-L con la opción Pixel-perfect del lápiz.
9. Cero píxeles huérfanos salvo acento intencional; grosor de outline/línea constante (1px nativo).
10. AA a mano y selectivo (hinting): solo en los escalones más visibles, con el valor intermedio del ramp; nunca AA externo sobre fondos variables.
11. En sprites pequeños y muy movidos: menos AA y menos dithering (hierven al animar).
12. Dithering solo entre valores contiguos del ramp, para superficies grandes o estética retro; no como muleta.
13. Una única dirección de luz global; mata el pillow shading fijando de dónde viene la luz.
14. Empieza el shading con 3 valores (base/sombra/luz); añade solo si el volumen lo pide.
15. Rompe el banding desfasando los clusters de sombra respecto al contorno anterior.
16. Silueta legible en cada pose clave de la animación; anima bordes y acentos, deja quietas las masas planas.
17. Economía de frames: pocos frames bien elegidos (walk 4-8) > muchos flojos; usa onion skin para el sub-pixel.
18. Import en Unity: Filter Mode **Point**, Compression **None**, mismo **PPU** para todos los sprites (= tamaño de tile).
19. Pixel Perfect Camera con Asset PPU = PPU de import y Reference Resolution que dé **ratio de escala entero** (usa Upscale RT).
20. Aprueba todo a 100% y EN el juego, con la cámara real, en movimiento — nunca ampliado en el canvas.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Dibujar a resolución alta con pincel suave y reducir → "pixel art" borroso | Dibujar a resolución nativa, píxel a píxel, con paleta contada; cada píxel es una decisión |
| Mezclar 32px con tiles de otra densidad de píxel | Fijar unidad de píxel global; auditar packs importados; mismo PPU en Unity |
| Rotar/escalar sprites en ángulos o factores no enteros | Solo transformaciones enteras sin filtrado; para rotaciones, redibujar frames |
| Sombrear bajando solo el brillo (color plástico, muerto) | Hue shifting: sombra→frío, luz→cálido, además del valor |
| Pillow shading (todo inflado, sin dirección) | Fijar UNA dirección de luz global y aplicarla consistente |
| Banding: bandas paralelas que engordan el borde | Desfasar los clusters de sombra respecto al contorno escalonado anterior |
| Jaggies: diagonales con tramos irregulares (2-1-3) | Tramos de pendiente constante o monótona; corregir el tramo, no tapar con AA |
| Doubles / esquinas-L en líneas de 1px | Opción Pixel-perfect del lápiz de Aseprite + limpieza a mano |
| Sobre-antialiasar (AA en toda la curva) → vuelve el borrón | AA selectivo/hinting solo en el escalón más visible; 1 nivel suele bastar |
| AA externo sobre fondos variados → halo sucio | AA externo solo con fondo fijo; si el sprite se mueve, borde duro |
| Dithering "hirviendo" en sprites chicos animados | Menos dithering cuanto más pequeño/movido; entre valores contiguos del ramp |
| Paleta abierta de cientos de colores sin cohesión | 16-32 colores globales, ramps con colores compartidos (Indexed en Aseprite) |
| Píxeles huérfanos y outlines de grosor variable | Limpiar clusters; grosor 1px constante; selout coloreado en vez de negro plano |
| Sprite borroso en Unity | Filter Mode Point, Compression None, Generate Mip Maps off |
| "Pixel wobble" / píxeles de tamaños distintos al moverse | Pixel Perfect Camera con ratio de escala ENTERO; Upscale Render Texture on |
| Aprobar el sprite ampliado en el canvas | Evaluar a 100%, en el juego, en movimiento, con la cámara real |

## Fuentes

- **Aseprite — Docs: Color Mode** — aseprite.org/docs/color-mode/ — modos RGB/Indexed/Grayscale; Indexed = máx. 256 colores (índice 0-255), editar un color de paleta reactualiza todos los píxeles; base del flujo de paleta editable.
- **Aseprite — Docs: Tilemap** — aseprite.org/docs/tilemap/ — capa de tilemap (Layer > New > New Tilemap Layer), tileset como colección de tiles indexados, modos Draw Pixels/Draw Tiles y Manual/Auto/Stack.
- **Aseprite — Docs: Animation** — aseprite.org/docs/animation/ — frames (Alt+N), tags, onion skinning, preview window, Play/Enter; base de la animación frame a frame y el sub-pixel.
- **Aseprite — Scripting API (Lua)** — github.com/aseprite/api — API Lua 5.3; objetos Sprite/Image/Cel/Layer/Palette/Dialog/app; automatización de export, recolor y batch.
- **Unity 6 — Manual: Pixel Perfect Camera** (paquete 2D Pixel Perfect / 2D Renderer URP) — docs.unity3d.com — propiedades verificadas: Asset Pixels Per Unit, Reference Resolution, Upscale Render Texture, Pixel Snapping, Crop Frame, Stretch Fill, Run In Edit Mode, Current Pixel Ratio.
- **Unity 6 — Manual: Sprite Editor + Sprite import (Texture Type: Sprite)** — docs.unity3d.com — slicing Automatic / Grid By Cell Size / Grid By Cell Count / Isometric; Filter Mode Point/Bilinear/Trilinear (Point = "blocky up close"), Mesh Type Full Rect/Tight, Pixels Per Unit, Generate Mipmap.
- **Unity 6 — Manual: Sprite Atlas** — docs.unity3d.com — empaqueta sprites en una textura para reducir draw calls (batching); Filter Mode Point, sin compresión y padding (default 4px) para pixel art.
- **Unity 6 — Manual: Tilemap y URP 2D lights** — docs.unity3d.com — Grid + Tilemap para niveles 2D (Tile Anchor default 0.5,0.5,0), shader Sprite-Lit-Default compatible con Light 2D (Freeform, falloff, volumétrico) y sorting layers.
- **Lospec — Palette List** — lospec.com/palette-list — base de ~4.382 paletas de pixel art; PICO-8 = 16 colores (verificado) y DawnBringer 16 = 16 (verificado); DB32/Endesga 32/Sweetie 16/AAP-64/Resurrect 64 con el conteo en el nombre.
- **Lospec — Pixel Art Tutorials** — lospec.com/pixel-art-tutorials — índice curado; incluye "Pixel Logic — A Guide to Pixel Art" (Michael Azzi: líneas, dithering, AA, color), "Shading" (Pedro Medeiros), "Palettes — A Beginner Guide".
- **Slynyrd — Pixelblog 1: Color Palettes** — slynyrd.com (Raymond Schlitter) — hue shifting cuantificado (~20° de hue positivo por swatch al subir brillo), ~9 swatches por ramp, saturación pico en valores medios.
- **Pixel Art Tutorials — Pedro Medeiros / saint11** — saint11.art — +90 tutoriales gratis (Outlines/selout, Shading, Subpixel, etc.); ya citado en [ver: gamedev/arte-direccion]. Los conteos de frames de animación son convención de producción, no cifras oficiales de una fuente única.
