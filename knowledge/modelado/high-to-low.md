# High-poly a low-poly y baking

> **Cuando cargar este archivo:** al preparar cualquier asset que pase por bake (high-poly → low-poly → normal map), al decidir si un asset NECESITA high-poly, al diagnosticar artefactos de bake (waviness, skew, seams), o al definir qué mapas bakear para texturizado. Complementa [ver: topologia] (retopo y vertex normals) y [ver: pipeline/arte-a-unity] (specs de entrega al engine).

## 1. El concepto: el detalle vive en la textura, no en la malla

La idea central del game art moderno: se esculpe/modela una versión de **millones de polígonos** (high-poly) con todo el detalle — biseles, tornillos, arrugas, poros — y ese detalle se **transfiere a texturas** proyectadas sobre una malla barata (low-poly) que es la que corre en el juego. El transfer se llama **bake**: el baker lanza rayos desde el low-poly hacia el high-poly y guarda, por cada píxel del mapa, lo que el rayo encontró (dirección de la superficie → normal map; oclusión → AO; etc.), usando las UVs del low-poly (polycount, Texture Baking).

Qué guarda exactamente un normal map: **cada píxel almacena la pendiente (dirección de la normal) de la superficie high-res en ese punto**. Al iluminar, el shader usa esa dirección en vez de la normal interpolada del low-poly → la luz responde como si la superficie tuviera el detalle del high.

**Límites — lo que el normal map NO hace:**

| Límite | Consecuencia práctica |
|---|---|
| **No cambia la silueta** | El contorno del modelo es el del low-poly. Curvas visibles necesitan lados reales [ver: presupuestos-poligonos] |
| **Solo ve dirección, no profundidad** | Caras paralelas a la base no registran nada: un detalle extruido recto con paredes verticales apenas aparece. Detalle con **pendientes/biseles** o no existe (Marmoset) |
| **No ocluye ni auto-sombrea** | Para eso están AO/height/bent normals (§6) |
| Detalle < 1 píxel del mapa no se captura | Mantener tamaño mínimo de biseles; exagerarlos si el asset se ve de lejos (Marmoset) |
| La profundidad real del detalle da igual | Un tornillo que sobresale 5 cm o 5 mm bakea casi igual → acortar detalles altos facilita el cage (Marmoset) |

Consecuencia de diseño: el low-poly se modela **para la silueta y para el bake**, no para "parecerse" al high. El orden concept → blockout → high → low → UV → bake → texturizado está en [ver: gamedev/arte-direccion] §9; la topología del low en [ver: topologia]; el high hard-surface en [ver: hard-surface] y el orgánico en [ver: organico-personajes].

## 2. Normal maps: tangent space, qué guardan, sincronización

### Tangent space vs object space

| | Tangent space | Object space |
|---|---|---|
| Color dominante | Azul-violeta (#8080FF neutro) | Arcoíris |
| RGB = | XYZ **relativo a la superficie** (tangente, bitangente, normal por vértice) | XYZ relativo al objeto |
| Deforma (skinning) | ✓ Sí — el estándar para todo | ✗ No sin shader especial |
| Tile / mirror / reuso | ✓ Fácil | ✗ Difícil, mapas únicos por malla |
| Compresión | ✓ Buena (canal azul reconstruible) | ✗ Mala |
| Sensible a vertex normals del low | ✓ Sí — de aquí salen casi todos los artefactos | ✗ Los ignora |

(polycount, Normal Map Technical Details). Object space se usa como **intermedio**: bakear en object space y convertir al tangent space exacto del renderer (herramientas tipo Handplane) es la vía clásica para sincronizar pipelines dispares.

- Color plano = **(128,128,255)**, no 127: 127 crea una normal levemente doblada y se nota como seam en espejos y reflejos (polycount, Normal map).
- R = X (izquierda/derecha), G = Y (arriba/abajo), B = Z (hacia afuera). Los colores distintos a cada lado de un UV seam **son normales**: las islas UV están rotadas y las normales se "tuercen" para compensar; el tangent basis las endereza al renderizar.

### Handedness (canal verde) — tabla de referencia

"Flipear el verde" es el bug de normal map más común. Y+ = OpenGL, Y− = DirectX (polycount, Normal Map Technical Details):

| Software | Verde |
|---|---|
| Blender, Maya, Modo, Toolbag, **Unity** | Y+ |
| 3ds Max, Source, CryEngine, **Unreal** | Y− |

### Tangent space sincronizado (la causa raíz de "en mi baker se ve bien y en el juego no")

Un tangent-space normal map es un **encoding, no un dato absoluto**: para decodificarlo sin error, el shader del juego debe aplicar la inversa EXACTA de la transformación que usó el baker. No existía estándar — cada baker calculaba tangentes distinto, y muchas implementaciones dependían hasta del ORDEN de caras/vértices del archivo — resultado: shading seams "misteriosos" (mikktspace.com). La solución de facto es **MikkTSpace** (Morten Mikkelsen): tangent space determinista e independiente del orden, adoptado por Blender (desde 2.57), xNormal (desde 3.17.5), Unity, Unreal y la mayoría de tools modernas (mikktspace.com; Marmoset).

Reglas operativas:

1. Bakear con el **mismo tangent space que usa el renderer**. Si hay duda: MikkTSpace (Marmoset: "si no sabes cuál usar, Mikk/xNormal es la opción — es lo que usan Unity y Unreal").
2. Exportar el low en un formato que **guarde las tangentes** (FBX/glTF) para que bake y render usen las mismas (polycount) [ver: pipeline/arte-a-unity].
3. **Triangular el low ANTES de bakear** y usar esa misma triangulación en el juego: si cada app parte los quads por su diagonal, el tangent basis cambia → errores de smoothing **en forma de X** sobre los quads (Marmoset; mikktspace.com).
4. **No tocar las UVs después del bake**: rotar/espejar UVs post-bake rompe el matching con el tangent basis (polycount).
5. Workflow NO sincronizado (renderer desconocido/casero): compensar con más hard edges + biseles para que los gradientes del mapa sean menos extremos (Marmoset).

## 3. La regla de oro: hard edge = UV seam

Fundamento: un **hard edge** es un vértice con normales partidas (split vertex normals; "smoothing groups" en Max y "harden edge" en Maya son lo mismo) [ver: fundamentos-3d]. La regla, canon de polycount:

> **Donde haya un hard edge DEBE haber un UV seam. Donde haya un UV seam, PUEDE (y suele convenir) haber un hard edge.**

Por qué en cada dirección (EarthQuake, "Making sense of hard edges…"):

- **Hard edge sin seam** = artefacto garantizado: las dos caras intentan bakear contenido distinto sobre la misma línea de píxeles.
- **Seam con hard edge = gratis**: un UV seam ya duplica los vértices en GPU; añadir el hard edge ahí NO duplica de nuevo. El costo real de un modelo es el vertex count en GPU, y hard edges y seams solo suman cuando no coinciden.
- Con un cage promediado (§4) los hard edges **no afectan en nada** el resultado de la proyección — no hay excusa de bake para evitarlos.

Beneficios de poner hard edges en los UV seams incluso con workflow sincronizado (EarthQuake): gradientes menos extremos en el mapa → mejor compresión de textura, mejor comportamiento en mips bajos y en LODs que comparten el mapa, y menos "resolution based smoothing errors" (triangulitos claros que aparecen cuando la resolución no alcanza para representar un gradiente fuerte).

Guías rápidas:

- Superficies mecánicas: hard edge donde el ángulo pase de **~45°** (polycount, Normal Map Modeling).
- Con sync + soft edges por todas partes también funciona (menos seams de UV) — es un trade válido, pero los gradientes extremos cobran su precio en mips/LODs.
- Alternativa al hard edge: **bisel** (mejora silueta y specular) — pero infla vertex count y crea triángulos finos; hard edge + seam suele rendir mejor (polycount). Biseles con vertex normals editadas: [ver: topologia].
- Automatizar: scripts/opciones de "hard edges from UV borders" existen en todas las DCC — es un paso de 10 segundos, no un arte.

## 4. El proceso de bake

### Preparación (orden canon de polycount, Texture Baking)

1. **Optimizar el high**: decimar sculpts (triángulos más chicos que un píxel del bake solo queman RAM y tiempo); subdivisión "justa" para superficie lisa a la resolución del bake.
2. **Low-poly final**: topología pensada para el bake (§5), silueta acorde al budget.
3. **UVs**: seams en hard edges (§3), espacio entre islas para padding (tabla abajo).
4. **Triangular** el low (antes de espejar).
5. **Espejos y overlaps fuera del 0-1**: el baker renderiza TODO lo que está en el cuadro UV 0-1; islas espejadas/solapadas se mueven exactamente **1 unidad UV** fuera (pueden quedarse ahí — el mapeo no cambia). Solo una copia "forward" queda dentro.
6. Espejar DESPUÉS de triangular, con triangulación espejada; bakear con el modelo COMPLETO (bakear medio modelo dobla las normales del borde hacia el hueco y crea un seam central) (polycount, Normal Map Modeling).
7. **Reset transforms / freeze** del low: transforms sucios = errores de render clásicos.

### Cage y distancia de rayos

Dos métodos de proyección (terminología de EarthQuake, que evita la ambigüedad de "cage"):

| Método | Cómo proyecta | Consecuencia |
|---|---|---|
| **Averaged projection mesh** (cage promediado) — LO CORRECTO | Copia inflada del low; normales del cage **promediadas** ignorando hard edges; rayos hacia adentro desde el cage | Sin gaps ni seams en hard edges. Los hard edges del low no afectan el bake |
| **Explicit mesh normals** (distancia de rayos / ray distance) | Rayos según las normales explícitas del low (con sus splits) a una distancia fija | Cada hard edge = **gap/seam en el bake**. Solo aceptable en mallas 100% soft |

El cage debe **envolver por completo** el high — pero extenderse lo justo: un cage demasiado grande atraviesa piezas vecinas y captura lo que no debe; demasiado chico deja huecos sin proyección (Marmoset). Nota de herramienta: en 3ds Max el cage controla distancia Y dirección de los rayos; en Maya solo la distancia (polycount). Toolbag permite además **pintar** offset (extensión del cage) y skew (dirección) por zona, en el viewport.

### Intersecciones: explode, bake groups, matching por nombre

Piezas que se tocan o están cerca se contaminan entre sí (los rayos de una alcanzan a la vecina — el clásico AO/normal "fantasma" entre los dedos de una mano). Soluciones en orden de calidad/velocidad (polycount):

1. **Malla contigua** donde el budget lo permita (menos overlaps, menos aliasing in-game, mejores UVs).
2. **Limitar la proyección por matching**: cada pieza del low solo "ve" su pieza del high. Es el estándar actual:
   - **Marmoset Toolbag — Quick Loader**: sufijos en el nombre del objeto. Sintaxis `<nombre>_high` / `<nombre>_low` (+ variantes: `arma_high_tornillos`); todo lo que comparte `<nombre>` cae en el mismo **Bake Group**. Case-insensitive.
   - **Substance Painter — Match by Name**: mismo principio con sufijos `_high`/`_low` por defecto.
   - 3ds Max: match por Material ID.
3. **Explode**: separar físicamente las piezas (high y low con LA MISMA separación), bakear, y devolverlas — keyframe del explode para revertir fácil. Convención de los scripts clásicos: prefijos/sufijos idénticos por pieza (`LOW_x`/`HIGH_x`/`CAGE_x`).
4. Multi-bake con distintos cages + composición manual (lento, último recurso).

### Ajustes de salida

| Ajuste | Valor / regla | Por qué |
|---|---|---|
| Bit depth | Bakear a **16-bit**; convertir a 8-bit al final **con dithering** | 8-bit directo = banding (escalones en superficies suaves); el dither lo mata a cambio de ruido leve (Marmoset) |
| Anti-aliasing / supersampling | Activado para el render final (o bakear a 2× y reducir a mitad + re-normalizar) | Bordes del high solapados dentro de una isla UV = dientes de sierra (polycount) |
| **Edge padding** | Mínimos polycount: 256→2px · 512→4px · 1024→8px · 2048→16px; gutter ≥ 2× el padding | Sin padding, el mipmapping mezcla el fondo con la isla = seams que aparecen A DISTANCIA |
| Resolución de test | Bakes de prueba a resolución/samples bajos, iterar, y solo al final full quality | El bake es un loop de diagnóstico, no un botón |
| Verificación final | El mapa se aprueba EN el engine con la luz del juego | El visor del baker no usa tu tangent space ni tus mips [ver: pipeline/arte-a-unity] |

## 5. Diagnóstico de errores de bake

La lección más importante del canon (EarthQuake): **casi todos los errores de bake son errores de GEOMETRÍA del low-poly, no de settings.** Pintar el error en Photoshop, deformar el cage a mano o combinar bakes son "destructive workflows": hay que rehacerlos con CADA re-bake, y el siguiente artista no sabrá reproducirlos. Primero preguntar: ¿puedo acercar el low al high? ¿puedo simplificar el diseño?

| Síntoma | Causa raíz | Fix (en orden de preferencia) |
|---|---|---|
| **Waviness** — líneas onduladas sobre cilindros/curvas | Las vertex normals promediadas del low divergen de la superficie: en esquinas duras los rayos salen a ~45° y la diferencia de curvatura high↔low se imprime como onda | 1) Más lados en el cilindro (lo más efectivo — Marmoset); 2) rediseñar con pendientes en vez de ángulos rectos ("model for your low", EarthQuake: la versión bake-friendly suele usar MENOS geometría); 3) biseles. Un low sin geometría suficiente es **irreparable** por settings |
| **Skewing** — detalles proyectados en diagonal (tornillos "derretidos" cerca de bordes) | Mismo fenómeno: la dirección de proyección sigue las normales promediadas, que se inclinan cerca de cambios de forma | 1) **Loops de soporte** alrededor del detalle para aplanar las normales (EarthQuake); 2) pintar skew correction (Toolbag); 3) bake plano separado del detalle + composición (recordar el costo destructivo) |
| **Seams/gaps en cada hard edge** | Proyección por explicit mesh normals (ray distance) en vez de cage promediado | Usar averaged cage; en xNormal cargar/crear cage en vez de distancias rápidas |
| **Artefactos sobre líneas de hard edges** | Hard edge sin UV seam | Partir las UVs en TODOS los hard edges (§3) |
| **Seams de iluminación en los UV seams (en el engine, no en el baker)** | Tangent space no sincronizado baker↔renderer; o tangentes no exportadas; o UVs tocadas post-bake | Bakear en MikkTSpace/el del engine; exportar FBX con tangentes; re-bakear si las UVs cambiaron (§2) |
| **Luz invertida en un eje** (detalles "hundidos" según ángulo) | Handedness: canal verde al revés | Invertir G o ajustar el import del engine (tabla §2) |
| **Detalle de una pieza impreso en la vecina** | Rayos atraviesan a la pieza de al lado (intersecciones, cage grande) | Bake groups / match by name; explode; cage más ajustado (§4) |
| **Errores en X sobre superficies planas** | Triangulación distinta entre bake y engine (quads re-triangulados) | Triangular antes de bakear y exportar triangulado (§2) |
| **Banding / escalones en superficies suaves** | 8-bit sin dither | 16-bit + dither al bajar a 8 (§4) |
| **Speckles en el specular tras editar el mapa** | Normales des-normalizadas (longitud ≠ 1) por pintura/blend/escala | Re-normalizar el mapa (filtros estándar) tras cualquier edición 2D |
| **Seam central en modelos espejados** | Mirror seam de tangent space (inevitable en espejo centrado) + flat color 127 | Flat 128; offset mirroring (mover el seam a zona oculta) o element mirroring (pieza central con UVs únicas — sin seam); detail map encima lo disimula (polycount, Normal Map Modeling) |
| **Seams que solo aparecen de lejos** | Edge padding insuficiente para los mips | Padding según tabla §4 y rellenar el fondo del mapa con color similar |
| **Píxeles sueltos random** | Overlaps residuales en 0-1, o filtrado del baker con UVs duplicadas | Overlaps fuera del 0-1; revisar opciones de filtrado del baker |
| **Zonas vacías/fondo en el mapa** | Agujeros en el high (el rayo no golpea nada) o cage que no cubre | Tapar los huecos del high ("cap the gaps") o modelarlos también en el low; ampliar cage localmente (Marmoset) |
| **Sombras "flotando" en el AO** | Floating geometry (§6) proyecta sombra sobre la base | Floaters como objeto aparte sin cast shadows / ignorar backfaces en AO; o AO en dos pases (§6) |

## 6. Qué más se bakea (y para qué sirve cada mapa)

El normal map es solo el primero. Del mismo par high/low se extraen mapas de utilidad que alimentan el texturizado por máscaras (generators/smart materials en Painter y equivalentes). Tabla según Marmoset (map types) y polycount:

| Mapa | Qué guarda | Uso en texturizado |
|---|---|---|
| **AO (ambient occlusion)** | Oclusión de luz ambiente (qué tan "metido" está cada punto) | Sombreado ambiente + máscara de suciedad/polvo acumulado. En PBR va SEPARADO del albedo y ocluye solo luz ambiente — mezclado en el diffuse ensucia el modelo (polycount) |
| **Curvature** | Convexidad (bordes) y concavidad (grietas) en un solo mapa o dos | LA máscara reina: edge wear/pintura gastada en convexo, mugre en cóncavo |
| **Position / gradient** | Posición XYZ del mesh → RGB | Gradientes por altura (polvo arriba, humedad abajo, variación de tono vertical) |
| **Thickness / transmission** | Grosor local del high (fino = claro) | Máscara para subsurface scattering (orejas, telas) y para desgaste en zonas finas |
| **ID map** (material/object/UV) | Un color plano por material/objeto/isla del high | Selección instantánea de zonas al texturizar ("todo lo rojo = goma"). Asignar materiales/colores al high ANTES de bakear |
| **Height** | Distancia low↔high en escala de grises (definir distancias inner/outer para centrar el 0 en 50%) | Parallax, blends por altura, detalle fino |
| **Bent normals** | Normales con AO integrado en el vector | Iluminación ambiente más rica en shaders que lo soporten |
| **World/object space normals** | Direcciones absolutas | Máscaras direccionales ("polvo en todas las caras que miran arriba") |
| **Wireframe / alpha** | UVs del low / huecos del high | Debug; máscaras de recorte |

Trucos y trampas:

- **Floating geometry** (detalles del high "flotando" sobre la superficie sin fusionar): ahorra muchísimo tiempo de modelado y bakea normales perfectas — el normal map guarda dirección, no profundidad. PERO rompe los mapas que dependen de distancia (height, position) y mancha el AO con sombras; floaters como objetos aparte sin cast shadows (polycount, Normal Map Modeling).
- **AO en dos pases (método EarthQuake)**: AO del high explotado (detalle fino) + AO del low SIN explotar (contacto entre piezas, silueta real del low) compuestos en 2D. El AO del low ajusta mejor porque su sombra coincide con la silueta que el jugador ve de verdad (polycount, Ambient occlusion map).
- AO entre piezas móviles: excluir del AO cruzado las partes que animan (cargador de un arma, puertas) o quedarán sombras horneadas de una pose (Marmoset, Ignore Groups/Exclude) [ver: props-armas].

## 7. Cuándo NO hace falta high-poly

El bake completo es caro (dos modelos + UVs + iteración). Alternativas legítimas y usadas en producción AAA:

| Camino | Cómo funciona | Cuándo usarlo | Fuente/precedente |
|---|---|---|---|
| **Mid-poly + weighted normals** | UN solo modelo con biseles reales y **face-weighted normals** (las caras grandes dominan las normales → shading limpio sin bake). Sin retopo, sin bake de normales; los mapas de utilidad (§6) se bakean del propio mid-poly | Hard-surface con muchas superficies planas y bordes; producción que itera geometría a menudo (cambiar el modelo no invalida ningún bake); presupuestos de vértices holgados (los biseles suman) | 80.lv (Angelic/UE5, artista con créditos en Halo Infinite y Valorant): sin duplicar mallas, UVs sin partir cada 90° porque no hay bake que proteger, más tiempo para materiales |
| **Mid-poly + mesh decals** | Base mid-poly con chamfers y normales custom + **planos flotantes** pegados a la superficie con detalles bakeados en atlas (tornillos, panel lines, textos): decals que modifican solo normales, o normales+albedo+roughness | Vehículos/naves/entornos hard-surface GRANDES donde una resolución única de bake jamás alcanzaría | Star Citizen (GDC 2015, "Visual Effects in Star Citizen", A. Brown) y Alien: Isolation (gbuffer decals que sobreescriben solo normales), detallado en el hilo canon de polycount [ver: vehiculos] |
| **Trim sheets / atlas** | Detalle bakeado UNA vez en tiras reutilizables; las mallas mapean sus caras a la tira | Entornos y kits modulares [ver: entornos-modulares] | Canon de entornos; ver también [ver: gamedev/arte-direccion] §9 |
| **Estilo flat / low-poly estilizado** | Sin normal map: color por material, vertex colors, luz y silueta hacen el look | Dirección de arte estilizada [ver: estilizacion-lowpoly]; [ver: gamedev/arte-direccion] §3 | — |

Regla de decisión: si el asset es hard-surface, se ve a distancia media, y su detalle es principalmente **bordes + paneles + tornillos** → mid-poly (+decals) probablemente gana. Si el detalle es orgánico/esculpido (personajes, criaturas, rocas) → high-poly y bake siguen siendo el camino [ver: organico-personajes]. El costo del mid-poly se paga en vértices: verificar contra [ver: presupuestos-poligonos].

## 8. Height / displacement vs normal vs bump

"Bump map" es la categoría paraguas: cualquier textura que finge relieve sin cambiar la geometría real. Normal map y height map son dos formas de guardar ese dato (Unity Manual):

| Mapa | Formato | Qué guarda | Qué hace en el juego |
|---|---|---|---|
| **Bump (clásico)** | Grises 8-bit | Altura relativa | Legado; hoy se convierte a normal map en import |
| **Normal map** | RGB (tangent space) | DIRECCIÓN de la superficie por píxel | El estándar: modifica la iluminación, costo fijo, no cambia silueta |
| **Height map (parallax)** | Grises | ALTURA por píxel (blanco = alto) | Parallax/parallax occlusion: desplaza las UVs según la vista para fingir profundidad REAL (los detalles se ocluyen entre sí). Más caro que normal; se usa ENCIMA del normal map en materiales que lo ameritan |
| **Displacement map** | Grises **16/32-bit float** (8-bit pierde niveles y produce escalones) | Altura real para desplazar vértices | Mueve geometría de verdad (necesita malla densa/teselación) — SÍ cambia silueta. En juegos: terrenos y hero assets con teselación; en el pipeline de asset normal, es una textura de sculpt/intercambio, no de runtime (polycount, Displacement map) |

Práctica: para un asset de juego estándar el orden de necesidad es **normal map siempre → height solo si el material gana con parallax (suelos de piedra, rejillas) → displacement casi nunca en runtime**. Al convertir height→normal en 2D, la fuente debe ser un height map real: convertir una foto/albedo pintado da resultados pobres (polycount, Normal map). Detalle fino 2D (poros, tela) se genera de height pintado y se **mezcla** sobre el normal bakeado — el método más correcto es RNM (Re-oriented Normal Mapping); tras cualquier blend, re-normalizar (§5).

## Reglas prácticas

1. El normal map guarda dirección, no profundidad ni silueta: curvas visibles = lados reales; detalle bakeable = con pendiente/bisel, nunca paredes verticales puras.
2. Bakea con el tangent space del renderer (MikkTSpace por defecto) y exporta el low con tangentes (FBX/glTF); verifica el resultado EN el engine, nunca solo en el baker.
3. Triangula el low antes de bakear y usa ESA triangulación en el juego; espeja después de triangular, con triangulación espejada.
4. Hard edge ⇒ UV seam, siempre; y pon hard edges en tus UV seams (son gratis en vertex count y mejoran compresión, mips y LODs).
5. Superficies mecánicas: hard edge a partir de ~45° de ángulo; el resto soft con soporte de geometría.
6. Proyecta SIEMPRE con cage promediado (averaged projection mesh), nunca con ray distance + normales explícitas.
7. El cage envuelve todo el high pero lo justo: ni gaps (chico) ni contaminación entre piezas (grande).
8. Nombra por convención desde el DCC: `pieza_high` / `pieza_low` por cada grupo — el matching por nombre (Toolbag/Painter) elimina el explode en la mayoría de los casos.
9. Overlaps y espejos: fuera del cuadro 0-1 (exactamente 1 unidad UV) antes de bakear; solo una copia forward dentro.
10. Bakea con el modelo espejado COMPLETO, no con la mitad.
11. Reset transforms del low antes de bakear; UVs congeladas después del bake (cambiar UVs = re-bake).
12. Bakea a 16-bit y baja a 8-bit con dithering; anti-aliasing/supersampling activado en el render final.
13. Edge padding por resolución: 2px@256 / 4px@512 / 8px@1024 / 16px@2048, gutters al doble.
14. Ante waviness o skew, la respuesta está en el LOW: más lados, loops de soporte, diseño con pendientes — no en el cage ni en Photoshop (todo hack manual se rehace en cada re-bake).
15. Decima el high antes de bakear: triángulos menores que un píxel del mapa solo queman tiempo y RAM.
16. Bakea el set completo de utilidad en una pasada: AO, curvature, position, thickness, ID (con materiales asignados al high ANTES) — es la materia prima del texturizado.
17. AO separado del albedo, ocluyendo solo luz ambiente; piezas que animan excluidas del AO cruzado.
18. Floaters: sí para normales (ahorro enorme), como objetos aparte sin sombras para AO, y sabiendo que height/position salen mal donde flotan.
19. Antes de esculpir un high, pregunta si el asset lo necesita: hard-surface de bordes y paneles → evalúa mid-poly + weighted normals (+ decals); orgánico → high-poly casi siempre.
20. Height/parallax solo donde el material lo pague; displacement runtime casi nunca — el default es normal map solo.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| "El bake salió mal, ajusto el cage / lo pinto en Photoshop" | Diagnóstico primero (§5): 90% es geometría del low. Los hacks manuales se rehacen en CADA re-bake y nadie más puede reproducirlos |
| Cilindro de pocos lados con waviness "imposible de quitar" | No hay setting que lo arregle: más lados o rediseño con pendientes; biseles ayudan pero menos |
| Tornillos/detalles sesgados cerca de bordes (skew) | Loops de soporte que aplanen las normales alrededor del detalle; skew painting si la herramienta lo da |
| Hard edges sin partir UVs (o partir UVs creyendo que DEBEN llevar hard edge… con proyección explícita) | Regla §3 + cage promediado; scripts de "hard edges from UV borders" |
| Normal map perfecto en el baker, seams en el engine | Tangent space sin sincronizar, tangentes no exportadas, o triangulación cambiada en import — checklist §2 |
| Detalles iluminados "al revés" según el ángulo | Canal verde (handedness) invertido para ese engine — tabla §2 |
| Piezas contaminándose (AO fantasma entre dedos, normales de la pieza vecina) | Bake groups / match by name / explode — nunca subir la ray distance "hasta que funcione" |
| Bakear la mitad del modelo espejado "para ahorrar" | Las normales del borde se doblan hacia el hueco = seam central; bakear el modelo completo con espejos offseteados en UV |
| Flat color 127 en ediciones/parches del mapa | 128,128,255 es el neutro real; 127 = seam en espejos y reflejos |
| Seams que aparecen solo de lejos, "el bake está bien" | Padding insuficiente para mips — tabla §4; rellenar fondo del mapa |
| Convertir el albedo pintado a normal map con un filtro 2D | El filtro espera un height map real; el detalle 2D se pinta como height y se mezcla (RNM) sobre el bake |
| Editar/mezclar el normal map y no re-normalizar | Speckles en specular; re-normalizar tras toda edición 2D |
| Esculpir high-poly de TODO por rutina (paneles, cajas, tuberías) | Mid-poly + weighted normals + decals/trims cubre gran parte del hard-surface con una fracción del costo (§7) |
| Bakear AO con floaters proyectando sombras | Floaters sin cast shadows / ignorar backfaces; o el AO en dos pases de EarthQuake |
| Aprobar el bake mirando el mapa en 2D | El mapa se aprueba sobre el modelo, con la luz del juego, a la distancia real de cámara [ver: pipeline/arte-a-unity] |

## Fuentes

- **Texture Baking** — polycount wiki — el proceso canon completo: raycast, workflow de 16 pasos, cages (distance vs cage), UVs/espejos fuera de 0-1, triangulación, explode, anti-aliasing, wavy lines.
- **Normal map** — polycount wiki (Eric Chadwick et al.) — definición (dirección por píxel, "la silueta no cambia"), flat color 128 vs 127, re-normalizado, RNM/blending, workflow 2D.
- **Normal Map Technical Details** — polycount wiki — synced workflow, tangent basis explicado, tangent vs object space (tabla pros/cons), handedness/swizzle por software, conversión entre espacios (Handplane).
- **Normal Map Modeling** — polycount wiki — mallas contiguas, espejado (center/offset/element mirroring, triangulación espejada), smoothing groups y hard edges (~45°), biseles vs hard edges, floating geometry, sloped extrusions.
- **Edge padding** — polycount wiki — por qué el mipmapping crea seams y los mínimos de padding por resolución (2/4/8/16 px).
- **Ambient occlusion map** — polycount wiki — AO separado del albedo en PBR, problema de floaters (4 métodos), método de doble AO de EarthQuake.
- **Displacement map** — polycount wiki — height/displacement en float 16/32-bit; por qué 8-bit pierde información.
- **The Toolbag Baking Tutorial** — Joe "EarthQuake" Wilson, marmoset.co — cages smoothed/unsmoothed, offset y skew painting, Quick Loader (`_high`/`_low`), TODOS los map types con su uso, tangent basis y handedness, slopes/bevels/floaters/detail size, "cap the gaps", errores en X por triangulación, banding y dithering.
- **Understanding averaged normals and ray projection / Who put waviness in my normal map?** — Joe "EarthQuake" Wilson, polycount forum (2011) — la explicación de referencia de waviness y skew desde las vertex normals promediadas; "model for your low"; por qué los fixes manuales son deuda.
- **You're making me hard. Making sense of hard edges, uvs, normal maps and vertex counts** — Joe "EarthQuake" Wilson, polycount forum (2012) — averaged vs explicit projection, la regla hard edge/UV seam, vertex count real en GPU, beneficios de hard edges en seams con workflow sincronizado, destructive baking workflows.
- **mikktspace.com** — Morten S. Mikkelsen — por qué el tangent space es un encoding que exige inversa exacta, order-dependencies, el estándar MikkTSpace (Blender 2.57+, xNormal 3.17.5+), el caveat de triangulación de quads.
- **Decal technique from Star Citizen** — polycount forum (2015; incluye el PDF de GDC 2015 "Visual Effects in Star Citizen" de Alistair Brown y confirmación de un dev de Alien: Isolation) — mid-poly con chamfers + custom normals + mesh decals para panel lines/tornillos; gbuffer decals que sobreescriben solo normales.
- **Creating Assets Within the Mid Poly Workflow in UE5** — Malte Resenberger-Loosmann (créditos: Halo Infinite, Valorant, Suicide Squad), 80.lv (2022) — mid-poly + face-weighted normals en producción: sin doble modelo, UVs más conectadas, mapas de utilidad bakeados del propio mid.
- **Normal map (Bump mapping)** — Unity Manual — bump como categoría; height (grises, altura) vs normal (RGB, dirección); conversión height→normal en import; cómo el normal map altera la iluminación sin tocar geometría.
