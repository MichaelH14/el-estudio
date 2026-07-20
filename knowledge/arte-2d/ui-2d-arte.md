# Arte 2D para UI y HUD

> **Cuando cargar este archivo:** al **producir o dirigir el arte** de la interfaz de un juego 2D — iconos, botones, marcos, barras, fondos de panel, la tipografía in-game — y llevarlo a Unity como sprites/atlas/9-slice. Es el "cómo se dibujan y exportan" los assets de UI, no el "cómo se diseña la pantalla". El **diseño** de HUD/menús/onboarding vive en [ver: gamedev/ux-ui-onboarding]; los fundamentos visuales (jerarquía, color, contraste, espaciado) en [ver: ux-ui/fundamentos-visuales]; la **implementación** en motor (Canvas, anchors, TMP, atlas, optimización) en [ver: unity/ui-unity]. Aquí solo el asset.

Este archivo es el equivalente 2D del bloque de arte 3D, especializado en UI. Producción general de sprites: [ver: sprites-produccion]. Reglas de pixel art (AA, dithering, paleta): [ver: pixel-art]. Flujo Aseprite: [ver: aseprite-flujo]. Export e import a Unity: [ver: 2d-a-unity]. No repito esos temas: los referencio y me quedo con lo específico de UI.

---

## 1. El estilo visual de la interfaz (qué se dibuja)

Una UI de juego se compone de un puñado de **familias de asset**; cada una tiene reglas de arte distintas:

| Familia | Qué es | Regla de arte dominante |
|---|---|---|
| **Iconos** | Habilidades, ítems, monedas, botones de acción, estados | Legibilidad a tamaño mínimo (§2); grid + grosor consistentes |
| **Botones / chips** | Superficie clicable con label | 9-slice para que escalen con el texto (§3); 4 estados (§6) |
| **Marcos / frames** | Bordes de panel, ventana, retrato, slot de inventario | 9-slice casi siempre; esquina ornamentada = zona fija |
| **Barras** | Vida, maná, XP, carga, cooldown | Fondo + fill separados; el fill se recorta/escala, no se re-dibuja (§3, §9) |
| **Fondos de panel** | Superficie tras el contenido (diálogo, menú, tooltip) | 9-slice o tileable; contraste bajo para no competir con el texto |
| **Divisores / ornamento** | Líneas, esquinas, sellos, flourishes | Decorativos: `Raycast Target off` en Unity [ver: unity/ui-unity] |
| **Cursor / puntero** | En PC/consola con navegación libre | Hotspot definido; pixel-perfect si el juego lo es |

Regla raíz (la que más separa UI amateur de pro): **la UI es un sistema, no una colección de imágenes sueltas**. Antes de dibujar el primer botón, fija en un doc/tablero: paleta de UI, grid de icono, grosor de línea/borde, radios, altura de botón, tamaño de fuente. Eso es el "design system" del arte [ver: ux-ui/sistemas-diseno]; sin él, cada asset diverge y la pantalla se ve armada por piezas de juegos distintos.

---

## 2. Iconografía

El icono es el asset de UI que más falla: se diseña grande y se ve borroso/ilegible al tamaño real. **Diséñalo al tamaño de destino, no ampliado.**

### Tamaños de grid (convención de la industria; elige y no mezcles)

| Grid px | Uso típico |
|---|---|
| **16×16** | Iconos densos de inventario retro, tiles de item, monedas |
| **24×24** | Iconos de HUD medianos, botones de barra |
| **32×32** | Iconos de habilidad/acción, el default cómodo de pixel art |
| **48×48 / 64×64** | Iconos "hero" (moneda grande, botón principal), splash |

(No son estándar oficial: son las potencias/múltiplos que casan con PPU y atlas. Lo importante es **un solo grid por set**.)

### Reglas de legibilidad a tamaño chico

- **Silueta primero**: si el icono no se lee en negro sólido (solo su forma), no se leerá a 16px. Prueba el *silhouette test* — rellena todo de un color y comprueba que aún se distingue "espada" de "hacha".
- **Grosor de línea uniforme**: define un grosor (p. ej. 1px de outline en 16-grid, 2px en 32-grid) y respétalo en TODO el set. Grosores mixtos es el tell #1 de un set incoherente.
- **Menos detalle, no más**: a 16-24px, cada píxel cuenta. Un icono legible tiene 1 idea, 1-2 colores de acento y contorno claro; el detalle interno se sugiere, no se dibuja.
- **Contraste con el fondo del HUD**: el icono debe cumplir contraste contra la superficie donde vive, no contra blanco. Outline oscuro o halo de 1px lo despega de fondos variables [ver: ux-ui/fundamentos-visuales para números WCAG].
- **Padding interno consistente**: deja 1-2px de aire dentro del grid en todo el set, o unos iconos tocarán el borde y otros no → se ven de tamaños distintos aunque el canvas sea igual.
- **Peso visual igual**: dos iconos en la misma barra deben "pesar" parecido. Un icono que llena el grid junto a uno diminuto rompe la fila. Ajusta a ojo (optical sizing), no por bounding box matemático.
- **Ángulo/perspectiva consistente**: todos frontales, o todos en la misma isométrica ligera. Mezclar frontal con 3/4 delata el set.

### Estados de color de un mismo icono

Un icono suele necesitar variantes: **activo** (full color), **inactivo/no disponible** (desaturado o gris), **en cooldown** (oscurecido + overlay de barrido). Prodúcelas como capas/tags en el mismo archivo, no como dibujos separados, para que compartan silueta exacta [ver: aseprite-flujo].

---

## 3. 9-slice / 9-patch: sprites que escalan sin deformar

Botones y paneles cambian de tamaño según el texto/contenido. Si estiras un sprite entero, las esquinas se deforman. **9-slice** parte el sprite en 9 regiones y escala solo el interior.

### Cómo se comporta cada región (verificado, doc Unity)

| Región | Draw Mode **Sliced** | Draw Mode **Tiled** |
|---|---|---|
| **4 esquinas** | Dimensiones originales, **nunca** se deforman | Igual: sin cambios |
| **Bordes arriba/abajo** | Se estiran **solo horizontal** | Se **repiten** horizontal |
| **Bordes izq/der** | Se estiran **solo vertical** | Se **repiten** vertical |
| **Centro** | Se estira en ambos ejes | Se repite en ambos ejes |

Elegir Sliced vs Tiled es una decisión de **arte**: un borde liso o degradado → Sliced (estirar no se nota); un borde con textura/patrón (madera, remaches, pixel art donde estirar borronea) → Tiled (repetir mantiene el detalle). El pixel art casi siempre quiere **Tiled** en bordes texturados para no interpolar píxeles.

### Cómo marcar los bordes en el arte

- **En Aseprite** (verificado): la herramienta **Slice** (Shift+C) tiene en sus propiedades un **9-Slices / 9-Patch Center** — un rectángulo interno que define qué parte es "centro" (escalable) y qué es borde/esquina (fijo). Ese dato viaja en el JSON de export (`--data`) con las coordenadas del center. También lleva un **Pivot** por slice.
- **En Unity** (verificado): en el **Sprite Editor** arrastras los 4 controladores de **Border (L/R/T/B)** sobre el sprite; esos valores en px definen las 9 zonas. Requisito: el sprite necesita border > 0 para que Sliced/Tiled hagan algo.
- **Diseña la zona fija con margen**: el borde debe contener TODO lo que no puede deformarse (grosor del marco, esquina ornamentada, sombra interna) y ni un píxel del área que sí estira. Un ornamento que cruza la línea de slice se corta o se repite feo.
- **El centro puede ser 1×1 px** si es un color/degradado plano: minimiza el sprite. Para un botón sólido, un center de 1px basta y el asset pesa nada.

### Regla de tamaño mínimo

Un sprite 9-slice **no puede renderizarse más pequeño que la suma de sus bordes** (izq+der de ancho, arriba+abajo de alto) sin que las esquinas se solapen/aplasten. Diseña las esquinas para el botón más pequeño real. Si necesitas botones diminutos, reduce el border, no el asset.

En Unity el asset llega al componente **Image** con **Image Type = Sliced** (o **Tiled**), con opción **Fill Center** (apagar si el centro debe ser transparente, p. ej. un marco hueco) y **Pixels Per Unit Multiplier** para ajustar el grosor aparente del borde sin re-exportar. Detalle de implementación: [ver: unity/ui-unity], [ver: 2d-a-unity].

---

## 4. Sprites de UI vs sprites de mundo

No son la misma clase de asset y no deben mezclarse en el mismo atlas ni compartir PPU a ciegas.

| Aspecto | Sprite de mundo (personaje, tile) | Sprite de UI (icono, botón) |
|---|---|---|
| **Resolución** | Atada al PPU del juego y al tamaño en pantalla al gameplay | Atada al tamaño en el HUD; a menudo mayor densidad |
| **PPU** | El PPU global del proyecto (típ. 16/32/64/100) [ver: sprites-produccion] | En uGUI la UI se mide en px de pantalla; el PPU importa vía `Reference Pixels Per Unit` del Canvas Scaler (default 100) [ver: unity/ui-unity] |
| **Atlas** | Atlas de mundo/personaje, cargado con la escena | **Atlas de UI propio**, cargado con el HUD, casi siempre residente |
| **Filtrado** | Point (no filter) si es pixel art | Point si es pixel art; puede ser Bilinear si la UI es de alta resolución |
| **Cambio de estado** | Por animación de gameplay | Por interacción (hover/press) → frecuencia distinta |

Por qué atlas separado (verificado, guía de rendimiento uGUI): un atlas = un material = batches grandes; **mezclar sprites de UI con sprites de mundo en un atlas** los carga juntos aunque no aparezcan a la vez y rompe el batching de la UI. La UI cambia con otra frecuencia y otro material → su propio Sprite Atlas [ver: unity/ui-unity §9, 2d-a-unity].

**Regla de PPU:** mantén el PPU **consistente entre todos los sprites del mismo grupo**. Sprites del mundo con PPU mezclado se ven de escalas distintas; la **Pixel Perfect Camera** (URP 2D) asume un `Assets Pixels Per Unit` único para todo el arte de mundo — si un sprite tiene otro PPU, sale borroso o de tamaño equivocado. La UI en Screen Space - Overlay no pasa por esa cámara, pero sí por `Reference Pixels Per Unit`; mantenlo alineado con el grid de tus assets de UI. (Ajustes exactos de Pixel Perfect Camera: [ver: unity/rendering-urp] / doc URP — no verificados en detalle esta sesión.)

---

## 5. Fuentes y tipografía en el juego (el arte del texto)

El texto es ~80% de una UI [ver: ux-ui/fundamentos-visuales]. En un juego 2D hay dos caminos de arte y NO son intercambiables:

| Camino | Qué es | Cuándo | Coste |
|---|---|---|---|
| **Pixel / bitmap font** | Cada glifo dibujado píxel a píxel, atlas rasterizado | Pixel art; estética retro donde el texto ES parte del look | Se ve nítido solo a múltiplos enteros de su tamaño nativo |
| **TMP / SDF** | Signed Distance Field: vectorial-like, nítido a cualquier escala/rotación | UI de alta resolución, texto que escala/rota/anima | Suaviza los bordes → **borronea** un pixel font (pelea con el look) |

### Producir/usar un pixel font correctamente

- **Diséñalo a una altura fija** (p. ej. mayúsculas de 5-7px es el clásico legible). Menos de 5px de altura de caja rara vez es legible en cuerpo.
- **Point filter, sin anti-aliasing**: el glifo debe caer en la rejilla de píxeles. Filtrado bilineal o AA de SDF lo emborrona y mata la estética.
- **Escala solo a múltiplos enteros** (1×, 2×, 3×): a 1.5× los píxeles se parten y aparecen filas de distinto grosor. Esto ata la UI de pixel art al escalado entero [ver: §8].
- **Incluir el charset del idioma**: para español, `á é í ó ú ü ñ ¿ ¡` además de ASCII; dibujar los acentos, no dejar que falten → tofu/□ en runtime [ver: unity/ui-unity §6].
- **En Unity**: TMP puede generar un atlas **raster/bitmap** además del SDF; para un pixel font usa el modo raster point-filtered a tamaño entero, o una bitmap font clásica. El SDF por defecto (SDFAA) suaviza y NO conserva el pixel-perfect. Verifica el modo de render exacto en el Font Asset Creator [ver: unity/ui-unity §6]. Muchos pixel fonts .ttf traen su tamaño nativo documentado (ej. "usar a 8/16/24") — respétalo.
- **Legibilidad > estilo** en textos funcionales (números de daño, cantidades, tiempos): una fuente decorativa muy pixelada puede confundir 8/B, 0/O, 1/l/I. Reserva la display font para títulos; usa una legible para datos.

### Bitmap font vs TMP: la decisión de arte

- Look retro coherente y resolución fija → **pixel/bitmap font** (el texto se ve "del mismo mundo").
- UI multi-resolución, mucho texto, rotaciones/animaciones, localización con CJK → **TMP/SDF**.
- Híbrido común: **títulos y HUD en pixel font** (identidad), **cuerpos largos y diálogo en TMP** (legibilidad y escalado). Siempre que ambos compartan paleta y peso para no chocar.

---

## 6. Estados visuales del botón como arte

Un control interactivo necesita comunicar su estado **visualmente** [ver: ux-ui/interaccion-microux para el timing/feedback]. El arte entrega los sprites/variantes; el motor los intercambia.

| Estado | Tratamiento de arte típico | Nota |
|---|---|---|
| **Normal (idle)** | Base | El "reposo" |
| **Hover / focus** | +brillo, +outline, leve elevación/sombra, o glow | En consola/PC = el elemento con foco [ver: gamedev/ux-ui-onboarding §2] |
| **Pressed (down)** | Se hunde: -1/-2px de offset, sombra reducida, tono más oscuro | Sensación de empuje físico |
| **Disabled** | Desaturado + baja opacidad/oscurecido; sin outline de foco | Nunca solo "más gris" ambiguo: debe leerse "no puedo tocarlo" |
| **Selected / toggled on** | Estado persistente distinto (marco encendido, check) | Diferénciate de hover: hover es transitorio, selected persiste |

Reglas de producción:
- **Un archivo, varias capas/tags** por estado (Aseprite): garantiza que todos comparten la misma silueta y solo cambia el tratamiento. Exporta como sprite sheet o sprites nombrados por estado [ver: aseprite-flujo, sprites-produccion].
- **Consistencia del delta**: el "hundido" del pressed debe ser el MISMO offset/tinte en todos los botones. Estados inventados por botón = incoherencia.
- **No dependas solo del color** para disabled/enabled (accesibilidad): añade opacidad, desaturación o icono [ver: ux-ui/accesibilidad].
- **Muchos botones = 9-slice + 1 set de estados**, no un sprite por botón: el marco 9-slice se reusa y solo el label/icono cambia. Escala mucho mejor que dibujar 40 botones.
- Alternativa barata: **un solo sprite normal** y derivar hover/pressed por **tint/escala/offset en el motor** (color multiply, scale 0.96, y-offset). Reserva sprites dedicados para estados que el arte no logra por transform (glow, marco distinto).

---

## 7. Coherencia UI ↔ juego: que la interfaz se sienta del mismo mundo

El error que hace ver "asset flip": HUD de un estilo, mundo de otro. La UI debe pertenecer al mismo universo visual [ver: gamedev/arte-direccion para la dirección de arte global].

Palancas de coherencia (todas verificables a ojo):

| Palanca | Cómo se alinea |
|---|---|
| **Paleta** | La UI usa la MISMA paleta que el mundo (o un subconjunto). No un set de grises corporativos pegado a un juego colorido [ver: pixel-art para paletas] |
| **Resolución / grosor de píxel** | Si el mundo es pixel art a X px, la UI es pixel art al mismo tamaño de píxel aparente. Un HUD hi-res vectorial sobre mundo pixelado grita "dos artes" |
| **Outline / grosor de línea** | Mismo criterio de contorno que los sprites del mundo |
| **Iluminación/sombra** | Misma dirección de luz y estilo de sombra que el arte del juego |
| **Ornamento y tema** | Marco de madera para un juego medieval; chapa/holograma para sci-fi. El marco cuenta el mundo |
| **Tipografía** | La display font casa con el tono (gótica ≠ arcade) [ver: §5] |

Método operativo: **construye una paleta de UI derivada de la paleta del juego** y un mini style-tile (un botón, un icono, una barra, un frame) ANTES de producir el set completo; apruébalo contra un screenshot real del gameplay, no en blanco. Lospec tiene 4.382 paletas curadas de pixel art (ej. **PICO-8 = 16 colores**, **DawnBringer 16 = 16 colores**) que sirven como base común mundo+UI [ver: pixel-art].

---

## 8. Assets de UI escalables para multi-resolución y móvil

El pixel art se defiende con **escalado entero**; la UI hi-res se defiende con **densidad múltiple**. Elige el modelo según el arte.

### Modelo A — pixel art (escala entera)

- Autor a 1× nativo; el juego lo muestra a 2×/3×/4× **enteros** (point filter). Nunca escala fraccionaria: rompe la rejilla y aparecen píxeles de distinto grosor.
- La **Pixel Perfect Camera** (URP 2D) resuelve el escalado entero del mundo a una Reference Resolution; la UI pixel se maneja aparte con el Canvas Scaler a múltiplos enteros. Multi-resolución = elegir el múltiplo entero más grande que quepa, con letterbox si sobra [ver: unity/ui-unity §3].
- Coste: no todas las resoluciones caben en múltiplo entero exacto → aceptar bordes (letterbox/pillarbox) o un margen de fondo tileable que rellene.

### Modelo B — UI de alta resolución (móvil moderno)

- Autor el asset **grande** (para la densidad más alta, tipo @3×) y deja que el motor lo reduzca; reducir se ve bien, ampliar no. Alternativamente exporta @1×/@2×/@3× [ver: ux-ui/mobile-ux para densidades].
- **9-slice reduce la necesidad de multi-res**: un botón/panel 9-slice escala a cualquier tamaño con esquinas nítidas; produce el asset grande una vez.
- **¿Vector?** Unity uGUI consume **sprites** (rasterizados), no SVG runtime nativo. El vector (Illustrator/Figma) es la **fuente**: se exporta a PNG a las densidades necesarias. Ventaja del vector como source: reexportas a cualquier tamaño sin pérdida. (El paquete Vector Graphics / SVG Importer existe pero es aparte y no es el flujo estándar de UI de juego — no asumirlo sin verificar.)
- **Iconografía a escala**: para móvil hi-res, dibuja iconos a un grid grande (128/256) y deja que bajen; para pixel art, dibuja al grid final y no escales fraccionario.

Regla transversal: **el touch target no es el sprite**. El área tocable mínima es 44pt iOS / 48dp Android aunque el icono dibujado sea más chico [ver: ux-ui/mobile-ux, gamedev/ux-ui-onboarding §6]. El arte llena una parte del target; el resto es padding invisible.

---

## 9. Pipeline: del arte de UI a Unity

Orden operativo (detalle de import/atlas en [ver: 2d-a-unity], detalle de componentes en [ver: unity/ui-unity]):

1. **Autor en Aseprite** a resolución nativa, en RGBA (o Indexed ≤256 colores si el juego es paleta fija; verificado). Un archivo por familia de asset (iconos, botones, frames), estados como capas/tags.
2. **Marca los 9-patch** en los sprites que escalan (Slice tool → 9-Slices/Patch Center + Pivot). Estos datos van al JSON de export.
3. **Exporta**: Export Sprite Sheet (layouts horizontal/vertical/matriz, con **padding** entre frames para evitar bleeding) + **JSON** (`--data`) con frames, tags y slices (verificado). Para iconos sueltos, PNGs individuales o un sheet con grid regular.
4. **Import en Unity**: Texture Type = **Sprite (2D and UI)**; Sprite Mode = **Multiple** para hojas (recortar en el Sprite Editor por Grid By Cell Size/Count) o **Single** por asset; **Filter Mode = Point (no filter)** y **Compression = None** para pixel art (evita blur y artefactos); PPU consistente con el grupo.
5. **Border 9-slice en el Sprite Editor**: arrastra L/R/T/B (o importa desde el JSON de Aseprite si usas un importer que lo lea). Verifica que la zona fija cubre el ornamento entero.
6. **Sprite Atlas de UI propio**: agrupa los sprites de UI (no los de mundo) en un `Sprite Atlas` con padding suficiente; un atlas = un material = menos draw calls [ver: unity/ui-unity §9].
7. **En la escena**: componente **Image** con Image Type = **Sliced/Tiled** para botones/paneles, **Simple** para iconos; `Fill Center` según si el marco es hueco; barras con fondo + fill (`Image.type = Filled` o escala con pivot). Decorativos con `Raycast Target off`.
8. **Verifica multi-viewport** en Device Simulator: que las esquinas 9-slice no se aplasten en el botón más pequeño ni el ornamento se repita raro en el más grande [ver: unity/ui-unity §7].

Automatización: Aseprite tiene **API de scripting Lua** y **CLI** (`--data`, `--split-slice`, `--sheet`) para exportar sin abrir la GUI (verificado; los detalles de CLI en la doc están marcados work-in-progress — confirma flags contra la versión instalada). Útil para regenerar todo el set de UI en el build [ver: aseprite-flujo]. **No hay Aseprite ni MCP instalado en esta sesión**: los operadores/scripts se verifican contra la doc oficial, no se inventan.

---

## Reglas prácticas

1. La UI es un **sistema**: fija paleta, grid de icono, grosor, altura de botón y fuente ANTES de dibujar el primer asset.
2. Diseña iconos **al tamaño de destino** (16/24/32 grid), nunca ampliados; un solo grid por set.
3. **Silhouette test**: si el icono no se lee en negro sólido, no se lee a 16px. Silueta antes que detalle.
4. Grosor de línea/outline **uniforme** en todo el set; padding interno consistente; peso visual óptico igual.
5. Botones y paneles = **9-slice**: esquinas fijas, bordes estiran (Sliced) o repiten (Tiled); pixel art texturado → Tiled para no interpolar.
6. La zona fija (border) contiene TODO el ornamento; el centro puede ser 1px plano. El asset no puede ser menor que la suma de sus bordes.
7. Marca el 9-patch en el arte (Aseprite Slice → 9-Patch Center); en Unity, Border L/R/T/B en el Sprite Editor.
8. Sprites de UI en **atlas propio**, separado del mundo; PPU consistente dentro del grupo; Filter Point + Compression None para pixel art.
9. Pixel font: altura fija (≥5px caja), point filter sin AA, escala **solo entera**, charset con `áéíóúüñ¿¡`.
10. SDF/TMP borronea pixel fonts: usa raster/bitmap point-filtered para el look retro; SDF para UI hi-res que escala/rota.
11. Los 4-5 estados de botón (normal/hover/pressed/disabled/selected) = **capas de un mismo archivo**, mismo delta en todos; o derívalos por tint/scale/offset en el motor.
12. Disabled y estados **nunca solo por color**: opacidad/desaturación/icono también.
13. Coherencia UI↔juego: misma paleta, mismo tamaño de píxel aparente, misma luz y outline; aprueba un style-tile contra un screenshot real antes de producir el set.
14. Pixel art → escala **entera** + letterbox; UI hi-res → autor grande (@3×) y reduce, o 9-slice para no multi-exportar.
15. El **touch target** (44pt/48dp) es independiente del tamaño dibujado del icono: rellena con padding invisible.
16. Barras = fondo + fill separados; el fill se recorta/escala (`Filled`/pivot), no se re-dibuja por valor.
17. Export desde Aseprite con **padding** entre frames (evita bleeding en el atlas) + JSON de datos; automatiza con CLI/Lua si el set es grande.
18. Verifica el 9-slice en **Device Simulator** al botón más pequeño y al más grande, no solo al tamaño de diseño.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Iconos diseñados grandes → borrosos/ilegibles al tamaño real | Autor al grid de destino (16/24/32); silhouette test; menos detalle |
| Set de iconos con grosores y estilos mezclados (se ve "de varios juegos") | Un grid, un grosor de línea, misma perspectiva/luz para todo el set |
| Estirar un botón entero → esquinas deformadas, texto que revienta el marco | 9-slice: esquinas fijas, centro escala; border cubre el ornamento |
| 9-slice con el ornamento cruzando la línea de slice → se corta/repite feo | La zona fija (border) contiene el ornamento completo; centro limpio |
| Renderizar un 9-slice más pequeño que sus bordes → esquinas aplastadas | Diseñar esquinas para el botón mínimo real; reducir border, no el asset |
| Pixel font a escala 1.5× → filas de píxeles de distinto grosor | Solo escala entera (1×/2×/3×); point filter, sin AA |
| Pixel font en TMP SDF por defecto → texto borroso que rompe el look | Raster/bitmap point-filtered a tamaño entero para el look retro |
| Acentos españoles faltantes → tofu/□ en runtime | Incluir `áéíóúüñ¿¡` en el charset del font [ver: unity/ui-unity §6] |
| Sprites de UI mezclados con sprites de mundo en un mismo atlas | Atlas de UI propio; un atlas = un material = batches limpios |
| Filter Bilinear + Compression en pixel art de UI → blur y artefactos | Point (no filter) + Compression None; PPU consistente |
| Estados de botón dibujados uno por uno con deltas distintos | Capas de un archivo con el MISMO offset/tinte; o transform en el motor |
| Disabled comunicado solo con "un poco más gris" (ambiguo) | Opacidad + desaturación + (si aplica) icono; no solo color |
| HUD hi-res vectorial pegado a un mundo pixelado (asset flip) | Misma resolución de píxel aparente, misma paleta; style-tile aprobado sobre gameplay real |
| Touch target = el sprite chico del icono → difícil de tocar en móvil | Área tocable 44pt/48dp con padding invisible alrededor del arte |
| "Se ve bien a tamaño de diseño" y en runtime el 9-slice se rompe | Probar en Device Simulator al mínimo y al máximo tamaño del control |
| Barra de vida re-dibujada por cada valor / sprite por porcentaje | Fondo + fill; recortar/escalar el fill (`Filled`/pivot), un solo asset |

## Fuentes

- **Unity Manual — "9-slicing" (docs.unity3d.com/Manual/sprite/9-slice/9-slicing.html)** — verificado: comportamiento de las 9 regiones (esquinas fijas; bordes arriba/abajo estiran/repiten horizontal; izq/der vertical; centro ambos) en Draw Mode Sliced vs Tiled; limitación de colliders (solo Box/Polygon Collider 2D).
- **Unity Manual — Sprite Editor (sprite-editor-landing / window reference)** — verificado el árbol de pestañas (Sprite Editor, Custom Outline, Physics Shape, Secondary Textures) y que recorta texturas en múltiples sprites; border L/R/T/B y slicing Grid By Cell Size/Count son las herramientas de recorte (detalle de campos no todo en la landing).
- **Unity Manual — UI Image / uGUI (com.unity.ugui)** — Image con Source Image, Raycast Target, Preserve Aspect verificados en la página; Image Type (Simple/Sliced/Tiled/Filled), Fill Center y Pixels Per Unit Multiplier citados como propiedades conocidas del componente (la página fetch no listó todas). Implementación cruzada en [ver: unity/ui-unity].
- **Aseprite Docs — Slices (aseprite.org/docs/slices)** — verificado: herramienta Slice (Shift+C), propiedades Bounds / 9-Slices-9-Patch Center / Pivot; export de datos vía JSON (`--data`, File > Export Sprite Sheet) y `--split-slice`.
- **Aseprite Docs — Color Mode (aseprite.org/docs/color-mode)** — verificado: RGBA / Indexed (hasta 256 colores, índice 0 típicamente transparente) / Grayscale; la restricción de paleta como base del pixel art.
- **Aseprite Docs — Export Sprite Sheet + Tilemap + índice de docs (aseprite.org/docs)** — verificado: layouts horizontal/vertical/matriz, padding entre frames, selección por tags/capas; existencia de CLI (marcada work-in-progress) y API de scripting; tilemap = tileset + tilemap layer.
- **Lospec Palette List (lospec.com/palette-list)** — verificado: 4.382 paletas curadas, tamaños típicos 4/8/16/32; **PICO-8 = 16 colores** (fantasy console) y **DawnBringer 16 = 16 colores** (artist) confirmados en sus páginas.
- **Pedro Medeiros / Saint11 — Pixel Art Tutorials (saint11.art)** — confirmado el sitio y su serie de tutoriales compactos 512×512 (AA, dithering, outlines/selout, readability, color, animación); referencia canónica de técnica de pixel art. Detalle de cada técnica en [ver: pixel-art].
- **Pixel Logic — Michael Azzi** — referencia establecida sobre legibilidad, grosor de outline y color en pixel art (citada por conocimiento de la obra; no fetch esta sesión).
- Nota de verificación: **Pixel Perfect Camera** (URP 2D) — sus ajustes exactos (Assets Pixels Per Unit, Reference Resolution, Upscale Render Texture, Pixel Snapping, Crop Frame) NO se pudieron abrir esta sesión (la página de la doc dio 404 en varias rutas); tratados a alto nivel y cruzados a [ver: unity/rendering-urp] — confirmar contra la doc URP antes de depender de valores concretos.
