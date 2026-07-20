# Producción de sprites

> **Cuando cargar este archivo:** al producir o dirigir CUALQUIER sprite de juego —personaje, prop, item, jefe— de concepto a asset importable en Unity. Cubre el pipeline referencia→limpieza, orientaciones (side / top-down / iso), la anatomía técnica del sprite (pivote, bounding box, padding), variaciones baratas, consistencia de set, naming/organización, resolución de entrega y el checklist game-ready. NO cubre la técnica de dibujar píxel a píxel (dithering, anti-alias, rampas) —eso es [ver: pixel-art]— ni la animación de frames —[ver: animacion-2d]— ni la mecánica de Aseprite —[ver: aseprite-flujo]— ni la spec de import a Unity —[ver: 2d-a-unity].

Este archivo es el equivalente 2D de [ver: modelado/props-armas] + [ver: modelado/organico-personajes]: el método de producción de un asset, no el diseño de arte (que vive en [ver: gamedev/arte-direccion]) ni la lectura de gameplay del nivel ([ver: gamedev/level-design]). Asume el vocabulario de [ver: fundamentos-2d].

---

## 1. El pipeline: de concepto a sprite game-ready

Mismo principio que en 3D: **silueta antes que detalle, forma antes que color, color antes que píxel individual**. Nunca empezar poniendo el detalle final; se construye por capas de compromiso creciente. Saltarse fases produce sprites "bonitos de cerca" que no leen en pantalla.

| Fase | Qué se decide | Salida | Criterio para pasar de fase |
|---|---|---|---|
| **0. Referencia** | Proporciones, pose, materiales, contexto. Nunca dibujar de memoria | Moodboard + turnaround/pose de ref | Tengo ref dimensional Y de apariencia [ver: modelado/blueprints-referencias] |
| **1. Silueta** | Legibilidad a tamaño real. Bloque negro sólido | 1 forma negra sobre fondo | Se reconoce el objeto SOLO por la silueta, al 100% de zoom |
| **2. Formas / blockout** | Masas primarias, subdivisión interna, línea (o line-less) | Formas planas en 2-3 tonos | Las masas leen sin color; la pose se sostiene |
| **3. Color base (flats)** | Paleta, asignación de color a cada masa. Flats planos, sin luz | Cada zona en su color plano | Paleta cerrada [ver: pixel-art]; contraste de valor correcto |
| **4. Sombreado / detalle** | Fuente de luz, volumen, rampas, dither, detalle terciario | Sprite con volumen y textura | Fuente de luz consistente; detalle NO rompe la silueta |
| **5. Limpieza** | Píxeles sueltos, jaggies, banding, doble-píxel, AA de borde | Sprite final limpio | Sin píxeles huérfanos; borde intencional; cabe en el canvas con padding |

Regla operativa: **evaluar SIEMPRE al 100% (1:1)**, no al zoom de trabajo. Un sprite que solo funciona a 800% de zoom no funciona en el juego. Probarlo además sobre el fondo/tile real, no sobre el checker de transparencia [ver: tilesets-mundos].

---

## 2. Sprites de personaje

### 2.1 Pose base
La primera pose es la **idle / T-pose 2D**: neutra, centrada, con el peso plantado. De ella salen todas las demás por edición, no desde cero. Fijar aquí: altura en píxeles, número de "cabezas" de alto (proporción), grosor de línea y paleta. Todo el resto del personaje hereda estas decisiones.

Alturas de personaje comunes (píxeles de canvas, no de pantalla):

| Escala | Alto típico | Uso | Nota |
|---|---|---|---|
| Micro / mascot | 8–16 px | Puzzle, retro estricto, mobile denso | Detalle casi nulo; todo es silueta + 2-3 colores |
| Chibi / arcade | 16–32 px | Plataformas, roguelike, JRPG clásico | El estándar indie; ~2-3 cabezas |
| Estándar | 32–64 px | Metroidvania, RPG de acción | Cabe expresión facial simple; ~4-5 cabezas |
| Alta res / héroe-boss | 64–128+ px | Fighting, cinemáticas, jefes | Anatomía real; caro de animar |

Elegir la escala ANTES de dibujar y no mezclarla dentro de un mismo plano de juego (§8).

### 2.2 Orientaciones
El género fija la vista, y la vista fija cuántas direcciones hay que dibujar. Costo de animación = frames × direcciones, así que las direcciones son la decisión más cara del proyecto.

| Vista | Géneros | Direcciones a dibujar | Truco de ahorro |
|---|---|---|---|
| **Side-view** (perfil) | Plataformas, fighting, beat'em up | 1 (izq/der por espejo) | Voltear horizontalmente en engine, no redibujar; ojo con asimetrías (parche, arma en un lado) |
| **Top-down 4-dir** | JRPG, Zelda-like, twin-stick | 3 (frente, espalda, lado) + espejo | Lado izq = lado der espejado; frente y espalda comparten cuerpo, cambia cara/pelo |
| **Top-down 8-dir** | Shooters, ARPG modernos | 5 (4 cardinales + 1 diagonal) + espejo | Las diagonales son las caras; espejar da las otras 4 |
| **3/4 top-down** | RPG (estilo SNES) | 4 (N,S,E,O) o 3+espejo | Vista más vendida por indies; combina lectura de cara con lectura de suelo |
| **Isométrico** (dimétrico 2:1) | Estrategia, ARPG iso | 4 u 8 direcciones | Ver §2.4; el eje de la cámara NO es el eje del sprite |

Nota sobre espejar: voltear en engine (flipX del SpriteRenderer / escala X negativa) es gratis y mantiene consistencia, pero rompe cualquier detalle asimétrico y puede desalinear el pivote si el pivote no está centrado en X. Si el personaje es asimétrico, o se dibuja el lado espejado a mano, o se acepta la asimetría "voltee". [ver: 2d-a-unity] para el pivote.

### 2.3 Consistencia entre poses
Cada pose nueva debe respetar el "contrato" de la pose base. Errores típicos: la cabeza cambia de tamaño entre idle y run, el grosor de línea engorda en las poses de acción, la fuente de luz se mueve. Blindaje:

- Trabajar en **capas** (Aseprite): cuerpo base en una capa, ropa/pelo/accesorios en otras. Reusar el cuerpo entre poses [ver: aseprite-flujo].
- Usar **onion skin** para comparar la silueta de cada pose contra la idle.
- Fijar la **línea de suelo** (baseline) y el punto de anclaje en todas las poses: los pies pisan la misma fila de píxeles en idle, y en las de salto/ataque el pivote se mantiene coherente (§4).
- Mantener el **conteo de píxeles clave** (ancho de hombros, alto de cabeza) idéntico salvo deformación intencional de squash/stretch [ver: animacion-2d].

### 2.4 Isométrico: la trampa de los ejes
El pixel art "isométrico" casi nunca es iso real (30°): es **dimétrico 2:1**, donde el tile diamante mide el doble de ancho que de alto (p.ej. 32×16, 64×32) y las líneas de suelo avanzan 2 píxeles en X por 1 en Y (ángulo 26.57°), porque esa pendiente se dibuja limpia sin AA. Consecuencias para el sprite de personaje:

- El personaje se dibuja **de frente pero con el suelo inclinado**: su cuerpo es casi vertical, lo iso lo aporta el tile, no la deformación del cuerpo.
- El **pivote** va al centro de la base del diamante donde pisa, no al centro del bounding box.
- El **orden de dibujo** (sorting) depende de la posición en el diamante, no solo de Y; es problema de implementación [ver: 2d-a-unity], [ver: pipeline/recetas-generos].

---

## 3. Props y objetos

Un prop es más barato que un personaje pero exige la **misma disciplina de consistencia con el set**. Clasificar antes de dibujar: rol (decorativo / interactivo / coleccionable / destructible) + distancia de cámara deciden el presupuesto de detalle.

| Aspecto | Regla |
|---|---|
| **Escala relativa** | El prop se dibuja junto al personaje, no aislado. Una silla debe medir lo que mide una silla respecto al héroe. Montar una "hoja de escala" con el personaje de referencia siempre visible |
| **Coherencia de estilo** | Mismo grosor de línea, misma paleta, misma fuente de luz y misma densidad de detalle que los personajes (§6). Un prop con el doble de detalle "grita" y descompone la escena |
| **Lectura** | Silueta reconocible al 100%. Los interactivos deben distinguirse de los decorativos por color/brillo/contorno —es affordance, no solo estética [ver: gamedev/level-design], [ver: ux-ui/interaccion-microux] |
| **Pivote funcional** | Cofre/puerta/palanca: el pivote va en el eje de la bisagra/rotación o en la base que pisa el suelo, no en el centro geométrico (§4) |
| **Modularidad** | Diseñar props que compartan piezas (mismo tronco para 3 árboles, misma base para 3 cofres) — ver §5 |

Props de entorno que tilean o se repiten en grid (suelo, pared, decorado de fondo) NO son sprites sueltos: son tiles y viven en [ver: tilesets-mundos].

---

## 4. Anatomía técnica de un sprite de juego

Un sprite no es "una imagen": es una imagen + metadatos que el engine usa para colocarlo, rotarlo y agruparlo. Los tres que importan:

### 4.1 Pivote / anchor
Es el punto (0–1 normalizado) que Unity trata como el **origen** del sprite: la posición del Transform cae ahí, y las rotaciones giran alrededor de él. Es la decisión técnica más impactante del sprite.

| Pivote (preset `SpriteAlignment`) | Valor normalizado | Cuándo |
|---|---|---|
| **Center** | (0.5, 0.5) | Default de Unity. Proyectiles, partículas, objetos que rotan sobre su centro, top-down |
| **Bottom** (Bottom Center) | (0.5, 0.0) | **Personajes de plataformas y todo lo que "pisa el suelo"**: así el sprite se planta en la fila del pie y las poses de distinta altura no flotan |
| **Bottom Left** | (0.0, 0.0) | Tiles, UI anclada a esquina, sistemas que posicionan por esquina |
| **Custom** | arbitrario | Bisagra de puerta/palanca, mango de arma que gira, punta de un brazo articulado |

Reglas de oro:
- **El pivote decide dónde "está" el objeto en el mundo.** Un personaje con pivote Center se hunde/flota medio cuerpo respecto al suelo; con pivote Bottom pisa exacto.
- **Consistencia > todo:** todas las poses/frames de un personaje comparten el MISMO pivote, o la animación tiembla. Se fija una vez y se hereda.
- Se define en el Sprite Editor de Unity (preset o Custom) o se hornea desde Aseprite como **Slice con pivote** exportado en el JSON [ver: aseprite-flujo], [ver: 2d-a-unity].

### 4.2 Bounding box
El rectángulo real del sprite dentro del canvas. Dos criterios en tensión:

- **Canvas fijo por animación:** todos los frames de un ciclo comparten el mismo tamaño de lienzo (p.ej. 64×64) y el personaje se mueve DENTRO de él. Esto mantiene el registro (alineación) frame a frame y es lo normal para animación. NO recortar ("trim") cada frame a su contenido, porque descoloca el registro.
- **Trim para sprites estáticos:** props e items sueltos SÍ se recortan al contenido para empacar mejor en el atlas (Aseprite `--trim`; Unity lo maneja con el mesh Tight). El pivote se recalcula respecto al recorte.

### 4.3 Padding (separación en la hoja)
Al empacar sprites en un sheet/atlas, dejar espacio entre ellos evita el **bleeding** (píxeles de un sprite filtrándose en el vecino por el sampling de la GPU). Es un problema real incluso con Filter Mode = Point cuando hay mipmaps o escalado no entero.

| Padding | Dónde | Aseprite flag | Recomendación |
|---|---|---|---|
| **Border padding** | Borde de toda la hoja | `--border-padding N` | ≥ 0; útil si el atlas final añade margen |
| **Shape padding** | Entre frames | `--shape-padding N` | **≥ 2 px** para pixel art; ≥ el radio del filtro. El Sprite Atlas de Unity usa **4 px por defecto** |
| **Inner padding** | Borde de cada frame | `--inner-padding N` | Para "bleed": duplicar el borde del sprite hacia afuera y evitar costuras en escalado |

El Sprite Atlas de Unity aplica su propio **Padding (default 4 px)** al reempaquetar; no hace falta duplicar el de Aseprite si Unity va a rehacer el atlas, pero si el sheet se consume tal cual (animación por Grid), el padding de Aseprite es el que cuenta [ver: 2d-a-unity].

---

## 5. Variaciones baratas (mucho contenido, poco arte)

El arte es el recurso más caro de un juego 2D; multiplicarlo sin redibujar es la palanca de producción clave [ver: gamedev/produccion-proceso].

| Técnica | Cómo | Costo | Ejemplo |
|---|---|---|---|
| **Palette swap / recolor** | Mismo sprite, distinta paleta. En Aseprite con paleta indexada (`Edit > Replace Color` o cambiar la rampa); en Unity con `SpriteRenderer.color` (tinte simple) o un shader de reemplazo por índice | Casi 0 | Enemigo verde → rojo "élite"; jugador 2; rareza de item |
| **Part swap / modularidad** | Base compartida + capas intercambiables (pelo, ropa, arma, cabeza). Cada capa se dibuja una vez y se combina | Bajo, alto retorno | Sistema de vestuario, NPCs variados, equipamiento visible |
| **Reuso de silueta** | Mismo blockout, distinto detalle/color: 3 cofres, 3 árboles, 5 pociones desde una base | Bajo | Familias de props coherentes por diseño |
| **Espejado / rotación** | Voltear en engine (flipX) o rotar sprites simétricos | 0 | Direcciones, decorado simétrico |
| **Recombinar frames** | Un frame de idle reusado como base de otra animación | 0 | Ahorra en ciclos [ver: animacion-2d] |

Para modularidad seria: diseñar el personaje **desde el principio** en capas alineadas (mismo pivote, mismo canvas, mismos puntos de anclaje de cada pieza), no intentar despiezarlo después. El palette swap exige que los sprites compartan **la misma rampa/índices**; si cada sprite tiene su paleta suelta, el swap no es programable [ver: pixel-art].

---

## 6. Consistencia del set (el sello que hace que "sea un juego")

Lo que hace que 200 sprites de gente distinta parezcan del mismo juego son 5 ejes que deben ser IDÉNTICOS en todo el set. Un solo eje roto delata el asset (típico de arte generado suelto o de assets comprados mezclados).

| Eje | Regla | Síntoma si se rompe |
|---|---|---|
| **Grosor de línea** | Mismo grosor (1 px suele bastar) en todo el set; o todo con línea, o todo line-less. Nada de mezclar | Un sprite "más grueso/pesado" que el resto |
| **Fuente de luz** | Una sola dirección para TODO el juego (lo común: arriba, o arriba-izquierda). Sombras y brillos coherentes | Objetos iluminados desde direcciones distintas en la misma escena |
| **Densidad de detalle** | Mismo "presupuesto de píxeles ocupados". Si el personaje es simple, los props también | Un prop hiperdetallado junto a un personaje plano "grita" |
| **Paleta** | Paleta global compartida; los sub-sets usan rampas de esa paleta, no colores nuevos sueltos | Un asset con colores que "no son de aquí" [ver: pixel-art] |
| **Escala / proporción** | Misma relación px↔mundo y mismas "cabezas de alto" dentro de un plano | Personajes de distinto tamaño de píxel en la misma capa (§8) |

Herramienta de control: montar un **contact sheet** (todos los sprites del set en una hoja, al 100%) y revisarlos juntos, no de uno en uno. Los desajustes solo se ven en conjunto.

---

## 7. Organización, naming y archivos

### 7.1 Un archivo por qué
| Unidad | Formato de trabajo | Formato de entrega |
|---|---|---|
| Personaje completo (todas sus anims) | 1 `.aseprite` con capas + tags por animación | Sprite sheet PNG + JSON, o PNG por frame |
| Prop/item suelto | 1 `.aseprite` (o compartir uno de "props") | PNG recortado |
| Tileset | 1 `.aseprite` en grid | PNG en grid [ver: tilesets-mundos] |

En Aseprite, cada **tag** = una animación (idle, run, jump); al exportar con `--split-tags` y `--list-tags`, el JSON lleva los rangos de frames por animación, que Unity/el engine consume para trocear. **Un sprite por archivo vs sheet:** trabajar en un solo `.aseprite` (fuente única), exportar a sheet para runtime. Detalle del flujo en [ver: aseprite-flujo].

### 7.2 Naming (convención, no ley — pero consistente)
- `snake_case`, minúsculas, sin espacios ni acentos, con índice de frame de ancho fijo (`_00`, `_01`).
- Patrón: `categoria_nombre_estado_frame`. Ej: `char_hero_idle_00.png`, `char_hero_run_00`…`_07`, `prop_chest_closed.png`, `enemy_slime_green_hurt_02.png`.
- Sheets: indicar el conteo/layout en el nombre: `hero_run_strip8.png`, `slime_sheet.png` + `slime_sheet.json`.
- Aseprite `--filename-format` con variables `{title}`, `{layer}`, `{tag}`, `{frame}` genera esto en batch [ver: aseprite-flujo].

### 7.3 Carpetas (ejemplo)
```
art/
  characters/hero/hero.aseprite  → export/ hero_sheet.png + .json
  characters/enemies/...
  props/
  tiles/          [ver: tilesets-mundos]
  ui/             [ver: ui-2d-arte]
  export/         ← lo que entra a Unity (Assets/Art/...)
```
La estructura dentro de Unity y el control de versiones (LFS para binarios, .meta) es [ver: unity/assets-pipeline-git].

---

## 8. Resolución de entrega y qué NO hacer

### 8.1 Resolución nativa y PPU
El pixel art se entrega a **resolución nativa** (los píxeles reales que dibujaste) y se ESCALA en el engine, nunca en la imagen. Reglas:

- **Pixels Per Unit (PPU)** en Unity = cuántos píxeles del sprite equivalen a 1 unidad de mundo. Default de Unity = **100**. Para pixel art conviene fijarlo al **tamaño del tile** para que 1 tile = 1 unidad (tile 16 px → PPU 16; tile 32 px → PPU 32). Todos los sprites del juego deben compartir PPU coherente [ver: 2d-a-unity].
- **Import de pixel art en Unity:** Filter Mode = **Point (no filter)**, Compression = **None**, Mip Maps = **off** (para 2D no escalado). Esto lo detalla [ver: 2d-a-unity]; sin esto, el pixel art sale borroso.
- **Pixel Perfect Camera** (paquete `com.unity.2d.pixel-perfect`, incluido en URP 2D): fija **Asset Pixels Per Unit** (debe igualar el PPU de los sprites) y **Reference Resolution** (la resolución de diseño). Con `Upscale Render Texture` y las opciones de crop se garantiza escalado entero. Ejemplo canónico: Reference Resolution **320×180** escala limpio a 720p (×4) y 1080p (×6). Otras comunes: 384×216, 256×144, 480×270.

Reference Resolutions y su escalado entero:

| Reference Res | ×2 | ×3 | ×4 | ×6 |
|---|---|---|---|---|
| 320×180 | 640×360 | 960×540 | 1280×720 | 1920×1080 |
| 384×216 | 768×432 | — | 1536×864 | 2304×1296 |
| 256×144 | 512×288 | 768×432 | 1024×576 | 1536×864 |

### 8.2 Lista de lo que NO se hace
| Prohibido | Por qué | En su lugar |
|---|---|---|
| **Escalar hacia arriba el pixel art en la imagen** (32→64 en el editor) | Duplica píxeles o interpola: rompe la retícula, borde borroso o "mixel" (píxeles de tamaños distintos) | Escalar en el engine con PPU + Pixel Perfect Camera, escala entera |
| **Escalado no entero** (×1.5, ×2.3) | Rota/deforma píxeles, filas de distinto grosor | Solo múltiplos enteros (×2, ×3, ×4) |
| **Mezclar resoluciones de píxel** en un mismo plano | Un sprite 16 px junto a uno 32 px = dos "tamaños de píxel" en pantalla, se ve amateur | Un solo tamaño de píxel por capa de juego; fondos a otra res van en su propia capa/cámara con criterio |
| **Rotar pixel art libremente** en runtime | Introduce AA y píxeles rotos | Pre-render de ángulos, o aceptar el look (con `Upscale Render Texture` off) |
| **Reescalar sprites ya animados** sin rehacer registro | Descoloca el pivote y el canvas | Fijar la res al inicio del asset |
| **Comprimir con pérdida / JPEG** | Artefactos en los bordes duros | PNG (lossless) siempre |

---

## 9. Checklist game-ready de un sprite

Un sprite está listo para producción SOLO si cumple todo esto (verificar en Unity, no solo en Aseprite) [ver: 2d-a-unity]:

- [ ] **Resolución nativa** correcta, sin upscaling en la imagen; un solo tamaño de píxel.
- [ ] **PPU** definido y coherente con el resto del set (y con el tile si aplica).
- [ ] **Pivote** puesto y correcto para su uso (Bottom para lo que pisa, Center para lo que rota) e **idéntico en todos los frames** de una animación.
- [ ] **Canvas / bounding box** consistente entre frames de la misma animación (sin trim que descoloque el registro); props sueltos sí recortados.
- [ ] **Paleta** compartida con el set; sin colores sueltos; rampas reutilizables si va a haber palette swap.
- [ ] **Padding** suficiente en el sheet (≥2 px shape padding; atlas Unity 4 px) para evitar bleeding.
- [ ] **Fuente de luz y grosor de línea** coinciden con el set (§6).
- [ ] **Sin píxeles huérfanos**, jaggies no intencionales ni banding en la limpieza.
- [ ] **Formato PNG** (lossless), fondo transparente, sin matte de color.
- [ ] **Naming** consistente (`char_hero_run_00.png`) y en su carpeta.
- [ ] **Import settings en Unity** verificados: Filter = Point, Compression = None, Sprite Mode correcto, Mip Maps off.
- [ ] **Probado al 100% sobre el fondo/tile real**, no sobre el checker.

---

## Reglas prácticas

1. **Silueta primero, siempre.** Si no lee en negro sólido al 100 %, no lee en el juego. El detalle no arregla una silueta mala.
2. **Evaluar a 1:1**, sobre el fondo real, no al zoom de trabajo ni sobre el checker de transparencia.
3. **Fijar escala, grosor de línea, fuente de luz y paleta ANTES del primer sprite** y no negociarlos después: son el contrato del set.
4. **Pivote Bottom para todo lo que pisa el suelo**; Center para lo que rota. El mismo pivote en TODOS los frames de un personaje.
5. **Canvas fijo por animación**: no recortar frames de un ciclo; sí recortar props sueltos.
6. **Escalar en el engine, nunca en la imagen**, y solo por múltiplos enteros.
7. **Un solo tamaño de píxel por plano de juego.** No mezclar 16 px con 32 px en la misma capa.
8. **PPU = tamaño de tile** para que 1 tile = 1 unidad; PPU coherente en todo el set.
9. **Filter = Point, Compression = None, Mip Maps off** para pixel art en Unity, o sale borroso.
10. **≥2 px de shape padding** en sheets (4 px el atlas de Unity) para matar el bleeding.
11. **Trabajar en capas** (cuerpo / ropa / accesorios) para reuso entre poses y para modularidad y palette swap.
12. **Fuente única `.aseprite`**, export a sheet+JSON para runtime; nunca editar el PNG de entrega a mano.
13. **Naming consistente con índice de ancho fijo** (`_00`, `_01`); automatizar con `--filename-format`.
14. **Diseñar variaciones desde el principio** (rampa compartida, capas alineadas), no despiezar después.
15. **Contact sheet del set completo** para cazar inconsistencias que solo se ven en conjunto.
16. **PNG lossless, transparencia real**, nunca JPEG ni fondo de color "que luego quito".
17. **Verificar en Unity, no en Aseprite**: import 200 OK ≠ sprite bien plantado. Meterlo en escena y mirarlo.

---

## Errores comunes

| Pitfall | Síntoma | Antídoto |
|---|---|---|
| Detallar antes de resolver la silueta | Sprite "bonito de cerca" que no lee en pantalla | Fases §1: silueta→formas→color→detalle→limpieza |
| Evaluar solo a 800 % de zoom | Se ve bien en el editor, mal en el juego | Revisar a 1:1 sobre el fondo real, siempre |
| Pivote en Center para un personaje de plataformas | El personaje flota o se hunde en el suelo; las poses de distinta altura no alinean | Pivote Bottom (0.5, 0), igual en todos los frames |
| Pivote distinto entre frames | La animación tiembla / el personaje "resbala" | Fijar pivote una vez y heredarlo; hornearlo como Slice en Aseprite |
| Recortar (trim) cada frame de una animación | El personaje salta de posición frame a frame (registro roto) | Canvas fijo por ciclo; trim solo en props estáticos |
| Escalar el pixel art en la imagen (32→64) | Píxeles duplicados/borrosos, "mixels", borde emplastado | Escalar en engine con PPU + Pixel Perfect Camera, escala entera |
| Escala no entera (×1.5) o rotación libre | Filas de píxeles de distinto grosor, AA sucio | Solo múltiplos enteros; pre-render de ángulos si hace falta rotar |
| Mezclar resoluciones de píxel en un plano | Dos "tamaños de píxel" en pantalla, look amateur | Un solo tamaño de píxel por capa de juego |
| Cada sprite con su paleta suelta | El palette swap no es programable; el set no "pega" | Paleta global + rampas compartidas indexadas |
| Fuente de luz o grosor de línea inconsistente | Un asset "grita" y descompone la escena | 5 ejes de consistencia §6; contact sheet |
| Sin padding en el sheet | Bleeding: bordes de sprites vecinos aparecen en el frame | shape-padding ≥2 px; atlas de Unity 4 px |
| Filter Mode Bilinear en pixel art | Todo borroso al importar a Unity | Filter = Point, Compression = None, Mip off |
| Prop dibujado aislado, sin escala de referencia | Props de tamaño incoherente respecto al personaje | Dibujar con el personaje de ref siempre visible (hoja de escala) |
| JPEG / fondo de color | Artefactos en bordes duros; halo al quitar el fondo | PNG lossless con transparencia real desde el inicio |

---

## Fuentes

- **Aseprite — CLI reference** (aseprite.org/docs/cli): flags de export verificados — `--sheet`, `--sheet-type` (horizontal/vertical/rows/columns/packed), `--sheet-pack`, `--data`, `--format` (json-hash/json-array), `--border-padding`, `--shape-padding`, `--inner-padding`, `--trim`, `--split-layers`, `--split-tags`, `--list-tags`, `--list-layers`, `--filename-format`, `--scale`, `--ignore-empty`.
- **Aseprite — Sprite Sheet docs** (aseprite.org/docs/sprite-sheet): export vía File > Export Sprite Sheet, selección por capas/tags, padding en import.
- **Aseprite — Lua Scripting API** (aseprite.org/api): objetos `app`, `Sprite`, `Layer`, `Cel`, `Frame`, `Image`, `Palette`, `Tag`, `Slice`, `Tileset`; automatización de export/paleta; `Sprite:saveCopyAs()`. Detalle de flujo en [ver: aseprite-flujo].
- **Unity 6 — Sprite Editor** (docs.unity3d.com/6000.0, sprite/sprite-editor/use-editor): Sprite Mode Single/Multiple; slicing Automatic / Grid By Cell Size / Grid By Cell Count / Isometric Grid.
- **Unity 6 — Sprite Atlas reference** (docs.unity3d.com/6000.0, sprite/atlas/sprite-atlas-reference): Padding (default **4 px**), Allow Rotation, Tight Packing, Read/Write, Generate Mip Maps, Filter Mode (Point/Bilinear/Trilinear), Max Texture Size.
- **Unity — 2D Pixel Perfect package** (docs.unity3d.com, com.unity.2d.pixel-perfect): Asset Pixels Per Unit, Reference Resolution, Upscale Render Texture, Pixel Snapping, Crop Frame, Stretch Fill; ejemplo PPU 100 → snap 0.01.
- **Lospec — Palette List** (lospec.com/palette-list): paletas comunitarias por tamaño (tag 16 colores, etc.). Referencia de paletas canónicas y restricción de color — detalle en [ver: pixel-art].
- **Pixel Logic – A Guide to Pixel Art**, Michael Azzi (referencia canónica de pixel art; principios de silueta, línea, luz y consistencia — NO consultada en vivo esta sesión).
- **Saint11 / Pedro Medeiros — Pixel Art Tutorials** (saint11.org): tutoriales canon de dithering, AA, líneas y sprites (referenciado, no fetch en vivo esta sesión).

> Verificado contra docs oficiales de Aseprite y Unity 6 el 2026-07-20 vía WebFetch. Los valores marcados "no consultada en vivo" (Pixel Logic, Saint11) se citan como referencias canónicas conocidas, sin números atribuidos. Los conteos de paleta y anatomía técnica de pixel art se amplían en [ver: pixel-art]; el import y setup en Unity, en [ver: 2d-a-unity].
