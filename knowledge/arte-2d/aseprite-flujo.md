# Aseprite: la herramienta

> **Cuando cargar este archivo:** al producir o dirigir pixel art / sprites / animación 2D en Aseprite, montar un pipeline automatizado (CLI / scripting Lua) que exporte spritesheets + JSON para Unity, o decidir qué herramienta 2D usar. Para el arte 2D como disciplina —fundamentos, técnica de pixel, tiles— [ver: pixel-art], [ver: fundamentos-2d], [ver: tilesets-mundos]. Para llevar el export a Unity [ver: 2d-a-unity]. Para dirección de arte y elección de estilo [ver: gamedev/arte-direccion].

Este archivo es la **herramienta y su flujo operativo**. El *criterio* de pixel art (shading, siluetas, densidad) vive en [ver: pixel-art]; aquí está el *cómo* mecánico y, sobre todo, cómo automatizarlo para un agente.

> **Aviso de verificación:** no hay Aseprite instalado ni MCP en este entorno. Todo lo de abajo está verificado contra la documentación oficial (aseprite.org/docs, GitHub `aseprite/api`) y el precio contra la Steam API, el **2026-07-20**. Nada se probó en vivo: atajos y flags pueden variar por versión; verificar contra tu build antes de scriptear en producción.

---

## 1. Por qué Aseprite es el estándar

| Punto | Dato (verificado 2026-07-20) |
|---|---|
| Qué es | "Pixel art tool that lets you create 2D animations for videogames" (Steam) |
| Precio | **US$19.99** en Steam (Steam appdetails API, USD, sin descuento; verificado). En **itch.io** mismo modelo de pago único, pero el número exacto **NO se re-confirmó** en esta sesión (precio no visible en el HTML público de la página) — asumir ~US$19.99 y confirmar en aseprite.itch.io antes de citarlo como dato duro |
| Gratis legalmente | El **código fuente está en GitHub** (`aseprite/aseprite`) bajo una EULA propia: puedes **compilarlo tú mismo gratis** para uso personal, pero NO redistribuir binarios. No es licencia OSI/open-source "libre" |
| Historia de licencia | Fue **GPLv2 hasta ~2016** (antes de v1.1); de ahí forkeó **LibreSprite** (§10). Por eso "open source" es matizado: *source-available*, no *free software* |
| Actualizaciones | Compra incluye toda la serie v1.x; desarrollado por Igara Studio S.A. |

**Por qué domina el pixel art de videojuegos**, no por precio sino por diseño:
- **Layers y frames como conceptos separados** en una sola timeline: animas por capas (cuerpo/ropa/arma) y por frames a la vez.
- **Modo Indexed nativo** con paleta de hasta 256 colores: disciplina de paleta forzada por la herramienta [ver: pixel-art].
- **Herramientas pensadas para píxel**: pixel-perfect strokes, shading ink, dithering ordenado, RotSprite, tiled mode, contour relleno.
- **CLI + scripting Lua** de primera clase: convierte a Aseprite en un *nodo de pipeline* scriptable, no solo un editor con GUI. Esto es lo que lo hace apto para un agente (§8–§9).
- Formato `.aseprite`/`.ase` propio que preserva capas, tags, slices, paleta; export a PNG, GIF, spritesheet + JSON.

---

## 2. Interfaz y flujo base

Cuatro zonas y su concepto:

| Elemento | Qué es | Nota operativa |
|---|---|---|
| **Canvas / Sprite Editor** | Área de dibujo. Se pinta con la herramienta + tinta (ink) + brush activos | Left click = Foreground color, Right click = Background color (casi todas las tools) |
| **Layers (capas)** | Se apilan; cada una independiente. Hay capa **Background** (siempre opaca, sin alpha) y capas transparentes | Capas se pueden agrupar (`Group`); el `--layer "grupo/hija"` del CLI navega jerarquía |
| **Frames** | Fotogramas de la animación, en columnas de la timeline | `Alt+N` frame nuevo copiando el actual; frame vacío por menú `Frame > New Empty Frame` |
| **Cels** | La intersección capa×frame = la imagen concreta ahí. Es la unidad que realmente editas | Un cel puede estar vacío; `--ignore-empty` los salta al exportar |
| **Timeline** | Matriz capas (filas) × frames (columnas). Copiar/mover capas, frames o cels | Play / `Enter` reproduce; navegar frames con `←`/`→` o `,`/`.` |

Flujo de animación canónico (docs): dibujas el frame 1 → `Alt+N` para el siguiente y sigues dibujando → previsualizas con Play/`Enter` → **etiquetas rangos con tags** (§4) → activas **onion skinning** (§5) para usar frames vecinos de referencia.

**Antes de dibujar nada:** fija resolución del canvas y grid/tile size, y elígelos coherentes para todo el juego. Mezclar densidades de píxel (16px junto a 32px) rompe el estilo [ver: pixel-art], [ver: gamedev/arte-direccion §8].

---

## 3. Color y paletas

Tres **color modes** (elegidos al crear el sprite; convertibles después):

| Modo | Estructura del píxel | Uso |
|---|---|---|
| **RGB / RGBA** | 4 canales R,G,B,Alpha independientes por píxel. Alpha 255 opaco, 0 transparente | Sprites con muchos colores, mezclas, referencias importadas |
| **Indexed** | Cada píxel es un **índice 0–255** a una paleta ≤256 colores. Cambiar la paleta cambia TODOS los píxeles que la referencian | Pixel art disciplinado, palette-swap de variantes, GBA/NES-like |
| **Grayscale** | 2 canales: Value (0 negro–255 blanco) + Alpha | Máscaras, ramps de valor, height/normal manuales |

**Indexed — puntos clave (docs):**
- No puedes pintar un color que no esté en la paleta (salvo editándola con `F4` / Edit Palette).
- Índice transparente: normalmente el **0**, configurable en `Sprite > Properties`. Ese índice actúa como "hueco" en capas transparentes.
- Convertir RGB→Indexed usa dithering (§6): `--color-mode indexed` + `--dithering-algorithm`.

**Color bar / gestión de paleta:**
- La color bar muestra la paleta del sprite activo; cada color por índice 0–255. `X` intercambia Foreground/Background.
- En **RGB** la paleta es solo un pickeo sugerido (el sprite no depende de ella); en **Indexed** ES la fuente de verdad.
- Cargar/guardar paletas: la color bar importa/exporta formatos comunes (`.gpl`, `.pal`, `.png`, `.aseprite`, `.ase`, `.act`, `.hex`, etc.); el ícono de warning junto a un color RGB lo añade a la paleta.
- **Paletas del sistema / presets**: Aseprite trae presets integrados (DB16, DB32, etc.). Para paletas curadas externas, **lospec.com/palette-list** es la referencia estándar (miles de paletas descargables en `.gpl`/`.pal`/`.png` que Aseprite importa directo). Elegir una paleta pequeña (8–32 colores) y no violarla es más identitario y barato de mantener [ver: gamedev/arte-direccion §4].
- Por CLI puedes reasignar paleta por sprite: `--palette pal1.png` antes de cada `--save-as` (palette-swap batch, §8).

---

## 4. Frames y tags: organizar animaciones en UNA timeline

Un **tag** marca un rango de frames como una animación con nombre. Con varios tags, un mismo `.aseprite` contiene *todas* las animaciones del personaje (idle, walk, attack, hurt, death) en una sola timeline — el patrón correcto para producción.

| Acción | Cómo (docs) |
|---|---|
| Crear tag | Selecciona rango → `Frame > Tags > New Tag`, o click derecho → New Tag, o `F2` dos veces (1ª crea "Loop", 2ª abre propiedades) |
| Nombre | En propiedades del tag (ej. `walk`, `idle`, `attack`) — el nombre viaja al JSON como `meta.frameTags[].name` |
| **Animation Direction** | **Forward**, **Reverse**, o **Ping-pong** (ida y vuelta). Es la propiedad clave del tag |
| Loop | Un tag "Loop" reproduce en bucle; el loop es semántica de reproducción, no un frame extra |
| Duración por frame | Cada frame tiene su propia duración (ms), editable individualmente; viaja al JSON como `duration` por frame |

**Convención recomendada:** un `.aseprite` por personaje/objeto; tags en minúscula sin espacios (`walk`, `attack_up`) para mapear limpio a estados de animación en Unity [ver: 2d-a-unity], [ver: unity/animacion-unity]. El CLI exporta un tag suelto con `--tag "walk"` o parte todos con `--split-tags` (§8).

---

## 5. Onion skinning

Ver frames vecinos translúcidos como referencia mientras dibujas el actual.

- **Toggle:** `F3` o el ícono en la timeline.
- **Configurable:** cuántos frames **previos** y **siguientes** mostrar, y el **tinte rojo/azul** (rojo = frames anteriores, azul = posteriores; convención de animación tradicional) desde el menú del ícono.
- Uso: reduce prev/next a 1–2 para timing fino; súbelo para ver el arco completo de un ciclo. Se combina con el Preview Window (Play en loop) para juzgar el movimiento real, no el frame estático [ver: animacion-2d].

---

## 6. Herramientas de pixel art

**Painting tools** (docs — `Drawing`):

| Tool | Tecla | Para qué |
|---|---|---|
| Pencil | `B` | Trazo 1px duro, el caballo de batalla del pixel art (sin anti-alias) |
| Line | `L` | Líneas rectas |
| Curve | `Shift+L` | Curvas bézier |
| Rectangle / Ellipse | `U` / `Shift+U` | Formas; Corner Radius en context bar |
| **Contour** | `D` | Traza contorno a mano y lo puede **rellenar** (filled contour) |
| Polygon | `Shift+D` | Contorno poligonal |
| Eraser / Eyedropper | `E` / `Alt`,`I` | Borrar / capturar color |
| Paint Bucket | — | Relleno; Tolerance 0–255, Contiguous on/off, Stop-at-grid |

**Modificadores que definen el resultado (context bar):**

- **Pixel-perfect mode**: checkbox en la context bar del Pencil (y otras painting tools). Elimina los "dobles píxeles" en las esquinas de un trazo diagonal → líneas limpias de 1px sin escalones dobles. **Imprescindible activarlo** para line art de pixel art. (Es un modo de trazo, no un brush.)
- **Ink** (tinta) — cambia CÓMO pinta la tool:
  - *Simple Ink* (default): opaco si alpha=255; compone si 0<alpha<255; borra si alpha=0 (color Mask).
  - *Alpha Compositing*: mezcla FG con la superficie según alpha.
  - *Copy Alpha+Color*: reemplaza el píxel destino tal cual (sin compositing).
  - *Lock Alpha*: conserva el alpha original, solo cambia RGB (pintar dentro de una silueta sin desbordar).
  - **Shading ink** (§abajo).
- **Shading ink** (pixel art): seleccionas un **conjunto de colores (un ramp) en la color bar**; **left click mueve el píxel un paso hacia el lado oscuro** del ramp, **right click hacia el claro**. Sombrear/iluminar respetando la rampa sin elegir color a mano — clave para shading consistente [ver: pixel-art].
- **Dithering**: patrón de dos colores para simular un tercero / degradado sin añadir colores.
  - En **conversión RGB→Indexed** por CLI/menú: `--dithering-algorithm none|ordered|old` con `--dithering-matrix bayer8x8|bayer4x4|bayer2x2` (matrices Bayer del extension `bayer-matrices`).
  - Para dithering *a mano* en pixel art se usa un **custom pattern brush** (`Ctrl+B` / `Edit > New Brush`) o brushes de patrón; la técnica y cuándo usarla, en [ver: pixel-art].
- **Brushes**: tipos round (default) / square / line (con ángulo). Custom brushes (guardar forma/patrón). Se guardan parámetros: size, angle, ink, opacity, shade gradient, **Pixel-Perfect state**.
- **Dynamics**: presión (solo pen/tablet) y velocidad (pen o mouse) modulan size/shape/gradient; **Stabilizer** suaviza el trazo. Útil para hand-drawn 2D, menos para pixel art duro.
- **RotSprite**: algoritmo de rotación específico para pixel art (menos artefactos que rotación bilineal); citado en features de Steam.
- **Symmetry / Tiled mode**: espejo en vivo (personajes simétricos) y modo tileado para diseñar tiles/patrones sin costura [ver: tilesets-mundos].

---

## 7. Export: spritesheet + JSON de datos

`File > Export Sprite Sheet` (GUI) o el CLI (§8). Un export produce **dos artefactos**: la **textura** (PNG) y el **JSON de datos** que un engine lee para recortar frames.

**Sheet types** (`--sheet-type`): `horizontal`, `vertical`, `rows`, `columns`, `packed`. `packed` (= `--sheet-pack`) minimiza espacio con packing; útil para atlas, **pero** cuidado en Unity si esperas grid regular — para slice-by-cell conviene `rows`/`columns` de tamaño fijo [ver: 2d-a-unity].

**Padding** (evita bleeding entre frames al escalar/filtrar):
- `--border-padding N` (borde del sheet), `--shape-padding N` (entre frames), `--inner-padding N` (dentro del frame), `--extrude` (duplica el borde 1px de cada frame — el antídoto real al *texture bleeding* en engine).
- Regla: para pixel art en Unity con filtrado Point, `--shape-padding 2` + `--extrude` evita líneas fantasma entre tiles/frames.

**Escala**: `--scale N` reescala en export (entero). Para pixel art, **exportar a escala 1x** y escalar en el engine con Point/no-filter; escalar en Aseprite solo si el pipeline destino lo exige. Nunca escalar por factores no enteros.

**Estructura del JSON** (`--data file.json`, `--format json-hash` [default] o `json-array`):
- `frames`: en `json-hash` es un **objeto** con clave por frame (`"sprite 0.ase"`); en `json-array` es una **lista** con campo `filename` en cada uno. Cada frame trae `frame {x,y,w,h}`, `rotated`, `trimmed`, `spriteSourceSize`, `sourceSize`, `duration` (ms).
- `meta`: `app`, `version`, `image`, `format`, `size {w,h}`, `scale`, y —si añades los flags— `frameTags` (name, from, to, direction), `layers`, `slices`.
- **Tags al JSON**: `--list-tags` mete los tags en `meta.frameTags`. **Capas**: `--list-layers` / `--list-layer-hierarchy` → `meta.layers`. **Slices**: `--list-slices` → `meta.slices`.
- **Pivots**: Aseprite **no** exporta un pivot por-frame nativo. La vía canónica es un **Slice con pivot** (`Slice tool`, define pivot y opcional 9-slice center): con `--list-slices` el pivot y el `center` (9-slice) viajan en `meta.slices` y un importador los aplica en Unity [ver: 2d-a-unity], [ver: ui-2d-arte].
- **stdout**: `--data=""` (filename vacío) escribe el JSON a stdout — útil para pipear a un script/agente sin tocar disco.

Formatos de salida de imagen: PNG (sheet o secuencia), GIF (animación), y por-frame/por-tag/por-layer con `--split-*` (§8).

---

## 8. CLI: automatizar export/batch (núcleo del pipeline con agente)

`aseprite [OPTIONS] [FILES]`. Los flags **posicionales importan**: se aplican a los sprites/estado *previos* en la línea. `-b`/`--batch` = sin UI (obligatorio para scripts headless).

**Flags de mayor uso (verificados en aseprite.org/docs/cli):**

| Flag | Efecto |
|---|---|
| `-b`, `--batch` | Corre sin UI y termina; base de todo pipeline |
| `--save-as <file>` | Guarda el último sprite en otro formato (`.png`,`.gif`…). Con `{frame}`,`{layer}`,`{tag}` en el nombre parte implícitamente |
| `--sheet <png>` | Exporta spritesheet de los frames previos |
| `--data <json>` | Escribe el JSON de metadata del sheet (`--data=""` → stdout) |
| `--format json-hash\|json-array` | Formato del JSON |
| `--sheet-type rows\|columns\|packed\|horizontal\|vertical` | Layout del sheet |
| `--sheet-columns N` / `--sheet-rows N` | Grid fijo (predecible para slice en Unity) |
| `--sheet-pack` / `--shape-padding N` / `--extrude` | Packing / separación / anti-bleed |
| `--split-layers` | Cada capa como imagen aparte (va **antes** del sprite) |
| `--split-tags` | Cada tag a un archivo (`anim-{tag}.gif`) |
| `--tag "walk"` / `--frame-range from,to` | Exporta solo ese tag / rango |
| `--layer "grupo/hija"` / `--ignore-layer "Guides"` / `--all-layers` | Selección de capas (incluye ocultas con `--all-layers`) |
| `--scale N` / `--trim` / `--crop x,y,w,h` | Reescala / recorta bordes / recorta rect |
| `--list-tags` / `--list-layers` / `--list-slices` | Inyecta tags/capas/slices en `meta` del JSON |
| `--filename-format '{title}-{tag}-{tagframe000}.{extension}'` | Plantilla de nombres (`{frame}` desde 0, `{frame1}`/`{frame001}`, `{tagframe}`, `{layer}`, `{tag}`, `{duration}`) |
| `--color-mode rgb\|indexed\|grayscale` + `--dithering-algorithm` | Cambia modo (con dithering en RGB→Indexed) |
| `--script <file.lua>` + `--script-param k=v` | Ejecuta script Lua (§9); params en `app.params` |
| `--shell` | REPL Lua interactivo |
| `-v` / `--preview` | Verbose / dry-run (muestra qué haría sin escribir) |

**Recetas listas (verificadas contra la sintaxis de las docs):**

```sh
# 1) Spritesheet grid + JSON con tags, para importar en Unity
aseprite -b player.aseprite \
  --sheet player.png --sheet-type rows --shape-padding 2 --extrude \
  --list-tags --list-slices \
  --data player.json --format json-array

# 2) Un GIF por animación (parte por tags)
aseprite -b player.aseprite --split-tags --save-as anim-{tag}.gif

# 3) Palette-swap batch (mismo template, 2 paletas)
aseprite -b ryu-template.png \
  --palette pal1.png --save-as ryu_p1.png \
  --palette pal2.png --save-as ryu_p2.png

# 4) Cada capa por frame como PNG suelto
aseprite -b --all-layers hero.aseprite --save-as out-{layer}-{frame}.png

# 5) Dry-run: ver qué haría sin escribir nada
aseprite -b --preview player.aseprite --sheet x.png --data x.json
```

Detalle de plataforma (docs): en macOS el binario está dentro del `.app` — la ruta típica es `/Applications/Aseprite.app/Contents/MacOS/aseprite`. En Steam conviene `--noinapp` en batch para no contar playtime. Verificar la ruta real antes de meterla en un script.

---

## 9. Scripting Lua: Aseprite como nodo programable

Desde **v1.2.10**, Aseprite corre scripts **Lua 5.3** (API en GitHub `aseprite/api`, MIT los ejemplos en `aseprite/Aseprite-Script-Examples`). Es lo que convierte a Aseprite en un motor de generación de assets dirigible por un agente: procesar en lote, generar variantes, exportar con reglas propias, o extender el editor con diálogos.

**Objetos globales y clases clave (verificados en el README del API):**

| Namespace / Clase | Para qué |
|---|---|
| `app` | Punto de entrada: `app.sprite` (sprite activo, `nil` en Home), `app.open(file)`, `app.params` (los `--script-param`), `app.command.*` (ejecutar cualquier comando del menú), `app.fs` (filesystem), `app.pixelColor`, `app.version` |
| `Sprite()` | Crea un sprite nuevo y lo activa; `Sprite:saveCopyAs()` exporta a disco |
| `Image`, `ImageSpec`, `Cel` | Pixeles y su ubicación (capa×frame) |
| `Layer`, `Frame`, `Tag` | Estructura de la animación; `Tag` con `AniDir` (Forward/Reverse/Ping-pong) |
| `Palette`, `Color`, `ColorSpace` | Paleta y color programático |
| `Slice`, `Tileset`, `Tile` | Slices (pivots/9-slice) y tilemaps |
| `Dialog` | UI: mostrar controles al usuario, pedir valores (plugins) |
| `json` | Parse/stringify JSON dentro del script |
| `Plugin` | Registrar comandos nuevos en menús (extensiones `.aseprite-extension`) |

Constantes útiles: `ColorMode`, `SpriteSheetType`, `SpriteSheetDataFormat`, `AniDir`, `Ink`, `BlendMode`. Restricciones de seguridad: `os.execute`, `io.open` **piden permiso** al usuario; `os.exit`/`os.tmpname` no disponibles → un pipeline 100% headless debe evitar depender de ellos o pre-aprobar permisos.

**Patrón de automatización con agente:**
1. El agente escribe/edita el `.lua` (batch export, generación de variantes, atlas custom).
2. Lo corre: `aseprite -b --script build.lua --script-param out=dist/`.
3. Lee `app.params["out"]` dentro del script; procesa `app.sprite` o `app.open`.
4. Exporta con `Sprite:saveCopyAs()` o comandos, escribe su propio JSON con `json`.

Los seis puntos de partida oficiales: transformar el sprite activo · crear sprite nuevo · abrir archivos existentes · guardar el resultado · mostrar un Dialog · añadir opciones a un menú (plugin). Para un agente, los relevantes son abrir→transformar→guardar en lote.

> Los operadores exactos de cada clase (métodos/propiedades) **no se transcriben aquí sin verificarlos**: consultar `github.com/aseprite/api` por clase antes de escribir el script. Este archivo garantiza el *mapa*, no cada firma.

---

## 10. Puente a Unity (resumen; detalle en 2d-a-unity)

Aseprite → Unity 6 (2D Renderer / URP). Números concretos y el paso a paso viven en [ver: 2d-a-unity]; aquí solo el handshake:

| En Aseprite | En Unity (import) | Por qué |
|---|---|---|
| Export sheet a **1x**, grid `rows`/`columns` fijo, `--extrude` | Sprite Mode **Multiple** + slice by Cell/Grid | Recorte predecible, sin bleeding |
| PNG sin filtrar | Filter Mode **Point (no filter)**, Compression **None** | Píxeles nítidos, sin blur |
| Tile/sprite base de N px | **Pixels Per Unit** = N (coherente en todo el proyecto) | Escala consistente; alinea con Pixel Perfect Camera |
| Tags en `meta.frameTags` | Estados del Animator / `.anim` | Un importador (Aseprite Importer package de Unity, o script propio que lee el JSON) genera clips por tag [ver: unity/animacion-unity] |
| Slices con pivot / 9-slice | Pivot del sprite / Sprite con borders (9-slice UI) | Pivots consistentes; UI escalable [ver: ui-2d-arte] |

Además: **2D Pixel Perfect Camera** (component de URP 2D) con *Assets Pixels Per Unit* y *Reference Resolution* para que el pixel art no vibre al moverse [ver: unity/rendering-urp], [ver: pipeline/arte-a-unity]. Nota: Unity tiene un **Aseprite Importer** oficial (package) que importa `.aseprite` directo con capas y tags — evalúalo antes de montar CLI propio; el CLI da más control, el importer menos fricción [ver: 2d-a-unity].

---

## 11. Alternativas y cuándo usarlas

| Herramienta | Coste | Rol / cuándo | Nota |
|---|---|---|---|
| **Aseprite** | US$19.99 (o compilar gratis) | Estándar pixel art + animación frame-a-frame + CLI/Lua | Default para este pipeline |
| **LibreSprite** | Gratis (GPLv2) | Fork libre del último Aseprite GPL (~2015). Si no puedes/quieres pagar ni compilar | Se quedó atrás en features vs Aseprite moderno; sin muchas mejoras post-2016 |
| **Piskel** | Gratis, web/desktop | Pixel art rápido en navegador, cero instalación, export PNG/GIF/spritesheet | Sin CLI/scripting; débil para pipelines grandes. Bueno para bocetos/onboarding |
| **Krita** | Gratis, open source | Painting digital: concepts, fondos, sprites **hand-painted** (no pixel art puro) | Para 2D no-pixel [ver: gamedev/arte-direccion §8] |
| **Photoshop** | Suscripción | Pintura/edición general; algunos lo usan para pixel con Nearest Neighbor | Caro y sin herramientas pixel dedicadas; no recomendado como primario |
| **Pyxel Edit / GraphicsGale / GIMP** | Varía / gratis | Alternativas históricas; Pyxel Edit fuerte en tilesets | Menor tracción/soporte que Aseprite hoy |

Para **tilemaps agnósticos de engine** (diseñar el mapa, no el arte del tile), **Tiled** complementa a Aseprite [ver: tilesets-mundos]. Para **animación esqueletal 2D** (rig por partes, no frame-a-frame), Spine/DragonBones — otra rama, [ver: animacion-2d], [ver: gamedev/arte-direccion §8].

---

## Reglas prácticas

1. Fija **color mode**, resolución de canvas y grid/tile size ANTES de dibujar; una sola densidad de píxel en todo el juego.
2. Un `.aseprite` por personaje/objeto, con **todas** sus animaciones como **tags** (`idle`,`walk`,`attack`) en una timeline.
3. Nombra tags en minúscula sin espacios: mapean 1:1 a estados de Unity y a `--filename-format`.
4. Activa **Pixel-perfect mode** para todo line art de pixel; sin él, los trazos diagonales dejan dobles píxeles.
5. Usa **Indexed** cuando quieras disciplina de paleta y palette-swap; RGB cuando necesites color libre. Elige/importa una paleta pequeña (8–32) de lospec y no la violes.
6. Sombrea con **shading ink** sobre un ramp de la color bar, no eligiendo colores a mano: consistencia garantizada.
7. Exporta a **1x**; escala en el engine con **Point/no-filter**. Nunca factores no enteros.
8. Añade `--shape-padding 2` + `--extrude` al exportar sheets que van a un engine con filtrado: mata el texture bleeding.
9. Prefiere `--sheet-type rows`/`columns` con grid fijo si vas a slice-by-cell en Unity; `packed` solo si tu importador lee el JSON de posiciones.
10. Siempre exporta **sheet + JSON juntos** (`--sheet` + `--data`), con `--list-tags --list-slices` para que tags y pivots viajen en `meta`.
11. Para pivots, define **Slices con pivot / 9-slice**, no confíes en un pivot por-frame (no existe nativo).
12. En batch usa `-b` siempre, y `--preview` como dry-run antes del run real; en Steam añade `--noinapp`.
13. Recuerda el **orden posicional** del CLI: `--split-layers`, `--layer`, `--ignore-layer`, `--all-layers` van **antes** del archivo.
14. Automatiza export/variantes con `--script build.lua --script-param k=v`; lee `app.params`, exporta con `Sprite:saveCopyAs()`.
15. Verifica cada firma de la API Lua contra `github.com/aseprite/api` antes de escribir el script: no inventes métodos.
16. Onion skinning `F3`, 1–2 frames prev/next para timing fino; juzga el movimiento en Preview Window (loop), no en frame estático.
17. Evalúa el **Aseprite Importer oficial de Unity** antes de montar CLI propio: menos control pero menos fricción.
18. Guarda siempre el `.aseprite` fuente (capas + tags + slices intactos); el PNG/JSON son derivados regenerables.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Escalar el sprite en Aseprite y luego otra vez en Unity → doble filtrado, blur | Exportar 1x, escalar solo en el engine con Point/no-filter |
| Líneas fantasma entre tiles/frames al mover la cámara (bleeding) | `--extrude` + `--shape-padding` en el export; Point filter + Compression None en Unity |
| Flags del CLI "no hacen nada" | Es el **orden posicional**: `--split-layers`/`--layer`/`--all-layers` deben ir ANTES del archivo |
| Tags y pivots no llegan al engine | Faltan `--list-tags` / `--list-slices`; sin ellos `meta.frameTags`/`meta.slices` no se escriben |
| `packed` sheet + slice-by-grid en Unity → recortes desalineados | Usar `rows`/`columns` grid fijo, o un importador que lea las posiciones del JSON |
| Doble píxel en diagonales del line art | Activar **Pixel-perfect mode** en la context bar |
| Sombras sucias/inconsistentes eligiendo color a mano | Shading ink sobre un ramp de paleta (left oscurece, right aclara) |
| "Aseprite es open source, lo bajo gratis compilado" | El binario se paga (US$19.99); solo el **source** es gratis para compilar tú mismo — o usa LibreSprite (fork GPL) |
| Mezclar 16px y 32px, o rotaciones no enteras, "porque se ve bien" | Una densidad de píxel; RotSprite para rotar; specs fijos [ver: pixel-art] |
| Depender de `os.execute`/`io.open` en un pipeline headless | Piden permiso al usuario; diseñar el script para no necesitarlos o pre-aprobar |
| Inventar métodos de la API Lua de memoria | Verificar clase por clase en `github.com/aseprite/api`; nada sin verificar |
| Perder capas al entregar solo el PNG | Versionar el `.aseprite` fuente; PNG/JSON son derivados |
| Editar la paleta en Indexed y "romper" colores que ya usabas | En Indexed, cambiar un índice cambia todos sus píxeles: editar con intención, o trabajar en RGB si quieres colores independientes |

## Fuentes

- **Aseprite Docs — Command Line Interface (CLI)** — aseprite.org/docs/cli — lista completa y verificada de flags (`--sheet`, `--data`, `--format json-hash/json-array`, `--split-*`, `--sheet-type`, padding, `--filename-format`, `--script`/`--script-param`, `--list-tags/layers/slices`) con ejemplos oficiales.
- **Aseprite Docs — Sprite Sheets / Export** — aseprite.org/docs/sprite-sheet — import/export de spritesheets, texture atlas, tipos de sheet.
- **Aseprite Docs — Color, Color Mode, Color Bar** — aseprite.org/docs/color · /color-mode · /color-bar — RGB/Indexed/Grayscale, paleta ≤256, índice transparente, gestión de paleta.
- **Aseprite Docs — Animation, Tags, Onion Skinning** — aseprite.org/docs/animation · /tags · /onion-skinning — timeline, tags (Forward/Reverse/Ping-pong), F2/F3, tinte rojo/azul.
- **Aseprite Docs — Drawing, Ink, Shading, Context Bar, Brushes, Dynamics** — aseprite.org/docs/drawing · /ink · /shading · /context-bar · /brushes · /dynamics — tools (Pencil/Contour), pixel-perfect mode, shading ink, tintas, custom/pattern brushes, dithering matrices Bayer.
- **Aseprite Scripting API** — github.com/aseprite/api (README) + aseprite.org/docs/scripting — Lua 5.3, objetos `app`/`Sprite`/`Image`/`Cel`/`Layer`/`Frame`/`Tag`/`Palette`/`Slice`/`Dialog`/`json`, `app.params`, permisos de `os`/`io`.
- **Aseprite en Steam** — store.steampowered.com/app/431730 (appdetails API) — precio **US$19.99 USD** y descripción de features (verificado 2026-07-20).
- **aseprite.itch.io/aseprite** — canal alterno de compra, mismo modelo pago único (precio exacto NO reconfirmado en esta sesión — el HTML no expone el número; contra aseprite.org/download solo se confirmó que itch.io/Paddle son los métodos de pago alternos, no el monto).
- **github.com/aseprite/aseprite (source) + LibreSprite** — código fuente compilable bajo EULA; historia GPLv2 pre-2016 y el fork LibreSprite.
- **lospec.com/palette-list** — repositorio estándar de paletas pixel art importables (.gpl/.pal/.png).
- **Pixel Logic — A Guide to Pixel Art (Michael Azzi)** y **Pixel Art Tutorials (Pedro Medeiros / saint11, saint11.art)** — referencias canónicas de técnica pixel (shading, dithering, pixel-perfect, tiles); el *criterio* detallado vive en [ver: pixel-art], aquí se citan como autoridad de la disciplina.
- **Unity Docs — 2D (Sprite Editor, Sprite Atlas, 2D Animation, Aseprite Importer, 2D Pixel Perfect Camera, Tilemap)** — docs.unity3d.com / Unity 6 — para el lado engine; números y pasos en [ver: 2d-a-unity], [ver: unity/rendering-urp], [ver: unity/animacion-unity]. (No re-verificado línea a línea aquí; es cross-ref, no fuente primaria de este archivo.)
