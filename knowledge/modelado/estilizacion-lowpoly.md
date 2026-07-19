# Estilización y low-poly

> **Cuando cargar este archivo:** al decidir o ejecutar el estilo visual 3D de un juego con equipo chico — elegir escuela de low-poly, estilizar formas, texturizar sin texturas (paleta/vertex color), mantener consistencia entre assets, o cerrar el look en el shader/luz del engine. Complementa la elección de estilo de [ver: gamedev/arte-direccion] con el CÓMO de modelado.

## 1. Por qué el estilizado es el estilo racional del indie

La decisión de estilo es económica antes que estética [ver: gamedev/arte-direccion §3]. El estilizado low-poly gana en tres frentes, y hay evidencia publicada de cada uno:

| Argumento | Evidencia real |
|---|---|
| **Coste por asset colapsa** | Astroneer (System Era, 2 artistas full-time): "with the polygonal art direction of Astroneer we can quickly create a game ready asset in just a day or two — if not hours". Eliminaron las texturas por completo del pipeline |
| **Reuso extremo sin verse repetido** | Firewatch: Jane Ng hizo solo **23 árboles únicos** para todo el juego; la variedad sale de colocación, escala y contexto, no de más assets |
| **Equipos mínimos entregan juegos completos** | Grow Home: 8 personas en Ubisoft Reflections, Unity, estilo "minimalist, low poly" deliberado para que la animación procedural fuera la protagonista |
| **Timeless** | El realismo envejece con cada generación de hardware; el estilizado se compara contra su propia coherencia, no contra el fotorrealismo del año. Journey (2012) y Firewatch (2016) no se ven "viejos" [ver: gamedev/arte-direccion] |
| **Esconde limitaciones técnicas** | La geometría simple no exige sculpting, bake ni PBR [ver: high-to-low]; la escuela PS1 convierte los defectos del hardware original (jitter, warping, fog) en estética buscada (§4) |
| **Accesibilidad del pipeline** | Astroneer: el estilo "greatly reduces the barrier to entry" — cualquier nivel de skill (incluidos modders y agentes IA) produce assets on-style |

La trampa que equilibra todo: **la geometría simple no perdona nada**. Sin buena paleta, luz y silueta, el low-poly se ve a "asset store" [ver: gamedev/arte-direccion §3]. El ahorro en modelado se reinvierte en color, composición y shader (§8), no se embolsa.

## 2. Las escuelas del low-poly

"Low-poly" no es un estilo: son al menos cuatro escuelas con pipelines distintos. Elegir UNA y escribirla en el style guide [ver: gamedev/arte-direccion §2].

| Escuela | Look | Técnica clave | Texturas | Referentes | Coste relativo |
|---|---|---|---|---|---|
| **Flat-shaded facetado** | El polígono ES la estética: facetas visibles, cristalino/origami | Hard edges en todo (normal por cara); color por material, vertex color o paleta-atlas | Ninguna o paleta diminuta | Astroneer (terreno), Grow Home | El más barato |
| **Low-poly suave con paleta plana** | Formas simples pero smooth shading; "de juguete", storybook | Smooth normals + colores planos saturados; bevels ligeros para atrapar luz | Ninguna o paleta/gradiente | Untitled Goose Game, Journey, Monument Valley [ver: gamedev/arte-direccion] | Barato (pide más ojo de forma) |
| **Retro PS1 / pixel-texture** | Texturas pixeladas a baja resolución sobre mallas de pocos tris; nostálgico, a menudo horror | Texturas pintadas ≤256px, point filtering; efectos de época en shader (§4) | Sí — pixel painting | Escena revival PS1 (recreación técnica documentada por D. Colson) | Medio: pide skill de pixel art |
| **Hand-painted estilizado** | Luz y material PINTADOS en la textura; fantasía tipo WoW | Difusa pintada a mano sobre AO/bent normals horneados; a menudo sin normal map | Sí — cada textura es una ilustración | World of Warcraft y su escuela (Blizzard) | El más caro de los cuatro |

Hibridación válida y barata: **render 3D a baja resolución + upscale** (A Short Hike) — look pixel-texture sin pintar ni una textura: modelos low-poly con "flat cohesive shading", sin anti-aliasing, y la pixelación la pone el render target (§8). Robinson-Yu: "I wanted to see if I could make a beautiful (and readable) 3D world using as few pixels as possible".

Reglas de elección:

- Sin artista 2D en el equipo → escuelas 1 o 2 (cero texturas). Con skill de pixel art → 3. Hand-painted (4) solo con ilustrador dedicado — mismo razonamiento que Cuphead en 2D [ver: gamedev/arte-direccion §3].
- Las escuelas NO se mezclan dentro de un juego sin decisión explícita: un prop facetado junto a uno smooth del mismo tamaño se lee como error (§5).
- Para clasificar una imagen de referencia en su escuela, mirar 3 señales en orden:
  1. ¿Se ven las facetas de los polígonos? → sí: escuela 1 (o terreno de Astroneer). No → seguir.
  2. ¿Se ven los píxeles de una textura? → sí: escuela 3 (o el híbrido de render pixelado tipo A Short Hike — se distingue porque los píxeles pixelan TODO, incluidos los bordes de la silueta, no solo la superficie).
  3. ¿La luz/sombra está pintada en la superficie (no cambia con la cámara)? → sí: escuela 4. No → escuela 2.
- Astroneer sí mezcla con intención: terreno natural facetado vs módulos artificiales "less faceted" — la diferencia de escuela CODIFICA natural vs artificial. Mezclar vale solo si comunica algo.

## 3. Reglas de estilización de forma

La estilización se decide en la malla, antes de tocar color o shader. El lenguaje de formas (círculo/cuadrado/triángulo) y el test de silueta vienen de [ver: gamedev/arte-direccion §1 y §5]; aquí su aplicación al modelado:

1. **Simplificar a formas primarias.** Todo objeto se reduce a 1-3 masas primarias legibles (esfera, caja, cilindro, cuña) antes de cualquier detalle. Si el blockout no comunica qué es el objeto, más polígonos no lo van a arreglar [ver: blueprints-referencias] [ver: fundamentos-3d].
2. **Exagerar proporción con intención.** Lo importante se agranda (cabeza/manos en personajes chibi, la boca de un cañón, el mango de una herramienta), lo secundario se encoge o se elimina. El nivel de exageración es UNA decisión global del style guide (escala 1-10), no por asset.
3. **Silueta > detalle.** Nielsen (character artist de Blizzard): "you need to have something that reads well even at a distance"; el sobre-detalle "crea muddiness" y tapa los focal points. En low-poly cada vértice existe para la silueta: edge que no cambia la silueta ni el shading = edge que sobra [ver: topologia].
4. **Redondear o afilar con intención.** Curvo = amigable/orgánico, anguloso = agresivo/artificial — la decisión bevels/chaflanes vs esquinas duras es de estilo tanto como de coste (§5), y debe seguir el lenguaje de formas del juego (aliados redondos, enemigos angulosos).
5. **Detalle por contraste, no por cantidad.** Áreas de descanso (planos limpios) hacen que el poco detalle que hay se lea (Nielsen: "areas of rest and areas of more concentrated detail"). En low-poly el "detalle" es densidad local de geometría: se concentra donde la cámara mira [ver: props-armas].
6. **Eliminar antes que simplificar.** El paso de estilización más barato es borrar el elemento: Firewatch reduce un bosque a 23 árboles; Goose Game elimina la CARA de los personajes y la emoción sale del body language — menos assets Y más identidad.

### Estilización por categoría de asset

Las reglas anteriores aterrizan distinto según qué se modela:

| Categoría | Dónde se estiliza | Notas de la categoría |
|---|---|---|
| **Personajes** | Proporción global (cabeza/manos/pies), postura de la silueta, cara simplificada o eliminada | La exageración de proporción es LA decisión: cambiar el ratio cabeza:cuerpo después de producir rompe rigs y animaciones [ver: organico-personajes]. Goose Game: sin cara = sin pipeline facial |
| **Props** | Masa primaria chunky, mangos/asas engordados, detalle solo en la cara que ve la cámara | El prop hereda la proporción del personaje que lo usa (regla 4 del §5): mano cartoon ⇒ herramienta gorda [ver: props-armas] |
| **Entorno / arquitectura** | Siluetas de techo/muro simplificadas, módulos que exageran lo estructural (vigas gordas, puertas anchas) | El kit modular multiplica cualquier decisión de estilo: un error de bevel en el muro base se repite mil veces [ver: entornos-modulares] |
| **Vegetación** | Copas como masas sólidas (esferas/conos deformados) en vez de alpha cards; troncos de 5-6 lados | Firewatch: los pinos son de lo más difícil de estilizar bien (Ng los hizo a mano); presupuestar la vegetación como asset difícil, no como relleno |
| **Vehículos / máquinas** | Volúmenes primarios exagerados (ruedas más gordas, cabina más grande), panelado sugerido con pocos edges | El facetado favorece lo mecánico; decidir si las superficies curvas (capó, fuselaje) van facetadas o smooth es la decisión 3 del §5 aplicada [ver: vehiculos] [ver: hard-surface] |

## 4. Texturizar sin texturas: flat shading, vertex colors y paleta-atlas

El pipeline más barato que existe: saltarse high-poly, bake, UV por asset y texturizado [ver: gamedev/arte-direccion §9]. Tres técnicas, de más simple a más flexible:

| Técnica | Cómo funciona | Pros | Contras |
|---|---|---|---|
| **Color por material** | Un material de color plano por zona del modelo | Cero UVs, trivial | Cada material extra = draw call extra; rompe batching con pocos assets [ver: pipeline/arte-a-unity §7] |
| **Vertex colors** | El color se pinta en los vértices y viaja dentro de la malla (FBX/glTF lo transportan); el rasterizador interpola entre vértices → gradientes suaves gratis | 1 material para TODO el juego; gradientes orgánicos; cero texturas | Requiere shader que lea vertex color (los shaders lit estándar suelen ignorarlo → shader custom/graph); resolución de color atada a la densidad de la malla |
| **Paleta-atlas (color o gradientes)** | UNA textura diminuta de bloques de color o tiras de gradiente compartida por todos los assets; las UVs de cada cara se colapsan a un puntito/tira del color deseado | 1 material + 1 textura para el juego entero; cambiar la paleta re-colorea TODO; UVs triviales | Una textura de paleta 1K ya es overkill — el artículo de 80.lv sobre gradient texturing estima que 1K consume memoria comparable a ~40k vértices; usar 128-256px |

**Runbook: montar la paleta-atlas del juego** (workflow documentado en 80.lv / addon Palette Grid):

1. Crear UNA textura chica (128-256px basta; el flujo documentado usa de 512px a 4K, pero la resolución solo importa si hay muchas tiras) organizada en filas: bloques de color plano arriba, tiras de gradiente abajo.
2. Poblar los bloques con la paleta EXACTA del style guide (hex del diccionario de color [ver: gamedev/arte-direccion §4]) — la textura es la paleta hecha archivo.
3. Definir 3-6 tiras de gradiente para lo que necesita profundidad barata: terreno (oscuro abajo → claro arriba), vegetación, cielo/agua, metal.
4. Texturizar cada asset colapsando las UVs de cada grupo de caras a su bloque (color plano) o mapeándolas a lo largo de una tira (gradiente). Sin unwrap real, sin seams, sin texel density [ver: fundamentos-3d].
5. Todos los assets comparten ESTE material y ESTA textura. Variantes de color = duplicar la fila en la paleta, no el modelo.
6. Al ajustar la paleta (post-visual-target), TODO el juego se recolorea desde un solo archivo — el mecanismo de consistencia de los packs low-poly comerciales: copiar las tiras entre paletas mantiene assets de orígenes distintos en el mismo look.

**Runbook: vertex colors** (cuando se prefiere gradiente orgánico por malla en vez de atlas):

1. Pintar los colores por vértice en el DCC (modo vertex paint); el color viaja dentro del FBX/glTF — cero archivos de textura.
2. Densidad de malla = resolución de color: un gradiente suave necesita vértices intermedios donde transiciona; planear los loops también por color [ver: topologia].
3. Asignar en el engine un shader que LEA vertex color (unlit/custom/graph) — los lit estándar lo ignoran y el modelo importa "gris".
4. Verificar el color en el engine, nunca en el viewport del DCC (gamma/espacio de color pueden diferir) [ver: pipeline/arte-a-unity §10].
5. Combinable con la paleta-atlas: atlas para el color base + vertex color como máscara de variación/AO barato — pero solo si el shader del juego lo soporta y está documentado en el style guide.

**Flat shading — el costo oculto que hay que saber:**

- El facetado se logra con **hard edges** (normal por cara). Cada vértice solo puede tener UNA normal, así que un hard edge duplica los vértices en la costura. El manual de Unity lo dice explícito: "keep the number of UV mapping seams and hard edges (doubled-up vertices) as low as possible".
- Consecuencia contraintuitiva: **un modelo 100% facetado tiene MÁS vértices en GPU que el mismo modelo smooth** con idéntico conteo de tris. El "low-poly facetado" es low-TRI pero no low-VERT. Para el rendimiento real casi nunca importa (los conteos son ínfimos), pero explica por qué el conteo del DCC no cuadra con el del engine [ver: fundamentos-3d] [ver: presupuestos-poligonos].
- El look facetado + vertex color hereda el modelo de sombreado de los 90: color plano por cara (flat) o interpolado (Gouraud). Es literalmente el pipeline PS1 sin sus limitaciones.

**La escuela PS1, en datos reales** (recreación técnica documentada por David Colson):

| Limitación original | Efecto visual | Cómo se recrea hoy |
|---|---|---|
| GTE: ~90.000 polígonos/seg con textura+luz+smooth shading | Mallas de MUY pocos tris | Presupuesto autoimpuesto, no límite real |
| Texture pages máx. 256×256 (común 128×128) | Texturas pixeladas, point filtering | Texturas ≤256px pintadas + filtro Point |
| Sin rasterización subpixel; salida 320×240 | Vértices "saltan" al grid de píxel → jitter | Vertex snapping en el vertex shader |
| Affine texture mapping (sin corrección de perspectiva) | Texturas que se doblan/nadan en ángulos picados | Shader con interpolación affine opcional |
| Sin z-buffer (ordering tables manuales) | Polígonos que parpadean/se atraviesan | Normalmente NO se recrea (molesta sin aportar) |
| Depth cueing (fog) para tapar el draw distance corto | Niebla densa característica | Fog agresivo — dobla como herramienta de mood |

Lección de la escuela PS1: es un estilo de **shader + textura pixelada**, no de malla — la malla es low-poly normal. Si no hay skill de pixel painting en el equipo, elegir otra escuela o la vía A Short Hike (§2).

## 5. Consistencia entre assets: las 5 decisiones que definen el estilo

Un asset "bonito" que rompe estas 5 se ve fuera de juego aunque esté bien modelado. Se congelan por escrito en el style guide [ver: gamedev/arte-direccion §2] y todo asset nuevo se audita contra ellas en la escena visual-target [ver: pipeline/arte-a-unity §10]:

| # | Decisión | Qué se congela | Cómo se rompe (síntoma) |
|---|---|---|---|
| 1 | **Densidad poligonal** | Tamaño de faceta / nivel de detalle relativo al tamaño del asset; presupuesto por categoría [ver: presupuestos-poligonos] | Un barril de 2.000 tris junto a una casa de 800: el barril se ve "de otro juego" |
| 2 | **Paleta** | Hex exactos, idealmente UNA paleta-atlas compartida (§4) | Un asset con colores propios "porque quedaba mejor" desentona en todas las escenas |
| 3 | **Bevels sí/no** | Esquinas duras vs chaflán/bevel de 1 segmento en TODOS los bordes duros; hard edges vs autosmooth | Props con bevels que atrapan luz junto a props de esquina infinitamente afilada |
| 4 | **Proporción** | Nivel de exageración global (1-10) + reglas por categoría (personajes chibi ⇒ props chunky: mangos gordos, puertas anchas) | Personaje cartoon abriendo una puerta de proporciones reales |
| 5 | **Outline / shader** | Toon bands sí/no, outline sí/no y su grosor, fog, saturación de la luz (§8) | Un asset aprobado en viewport neutro que en el juego (con toon shader) muestra facetas que nadie vio |

Regla operativa para un agente que genera assets en serie: las 5 decisiones son PARÁMETROS fijos del encargo, no espacio creativo. La creatividad vive dentro de ellas (silueta, forma, pose), jamás en ellas. Coherencia > calidad individual [ver: gamedev/arte-direccion §1].

### Runbook: montar un estilo low-poly desde cero

Secuencia completa para arrancar la fase de arte 3D de un juego estilizado (asume que la dirección de arte ya definió emoción, pilares y paleta [ver: gamedev/arte-direccion §2]):

1. Elegir la escuela (§2) contra el skill real del equipo/agente y el género del juego.
2. Congelar las 5 decisiones de este capítulo por escrito en el style guide.
3. Construir la paleta-atlas (runbook del §4) desde los hex del style guide.
4. Modelar 3-4 assets piloto de categorías distintas (1 personaje o criatura, 1 prop, 1 pieza de entorno, 1 elemento de vegetación) siguiendo las reglas del §3.
5. Montar el look completo en engine: shader (toon/unlit/lit simple), outline si aplica, fog, luz direccional y post-proceso (§8) — con los 4 pilotos dentro.
6. Iterar paleta/shader/luz sobre esa escena hasta que UN screenshot comunique la identidad del juego; esa escena queda como visual target [ver: gamedev/arte-direccion §1].
7. Derivar la spec de entrega técnica (escala, pivots, presupuesto de tris por categoría, nº de materiales) [ver: pipeline/arte-a-unity §1] [ver: presupuestos-poligonos].
8. Recién entonces: producción en serie, cada asset auditado contra el visual target y las 5 decisiones.
9. Toda excepción aprobada (un asset que rompe una decisión con razón) se documenta el mismo día o se convierte en drift.

## 6. Referentes canon y qué aprender de cada uno

| Juego / escuela | Qué aprender (verificado en la fuente) |
|---|---|
| **Astroneer** (System Era) | Cero texturas como decisión de pipeline, no de look: "we completely removed the necessity for creating textures". Facetado natural vs limpio artificial como código semántico. Con 2 artistas: asset game-ready en horas-días |
| **Firewatch** (Campo Santo) | Traducir un estilo gráfico 2D (Olly Moss) a 3D: color y atmósfera cargan el peso, no el detalle. 23 árboles únicos + colocación/escala inteligente = bosque entero. "Feel real" ≠ ser realista |
| **A Short Hike** (A. Robinson-Yu) | Pixelación del render como estética (baja resolución + sin AA + "flat cohesive shading"); outline suave para que todo lea con pocos píxeles; la baja resolución "deja que la imaginación rellene el detalle". Pixel size ajustable por el jugador |
| **Grow Home** (Ubisoft Reflections) | 8 personas: el minimalismo visual libera presupuesto para el sistema protagonista (animación procedural). El estilo sirve al gameplay, no compite con él |
| **Untitled Goose Game** (House House) | Low-poly smooth sin texturas, look storybook; personajes sin cara → toda la emoción por body language y animación — recorte de assets que SUMA identidad |
| **Journey** (thatgamecompany) | "Do the most with the least"; paleta y luz como identidad; el norte de la escuela 2 [ver: gamedev/arte-direccion] |
| **Escuela PS1 revival** | Las restricciones ajenas adoptadas como estética propia; el estilo vive en el shader (§4), la malla es normal |
| **Escuela hand-painted (WoW/Blizzard)** | La luz pintada EN la textura hace al asset independiente de la iluminación dinámica → envejece poco; formas que leen a distancia por encima de todo (Nielsen) |
| **Monument Valley** (ustwo) | Geometría mínima + paleta como todo el contenido visual; la arquitectura ES el puzzle — norte del flat/vector aplicado a 3D [ver: gamedev/arte-direccion §3] |
| **Team Fortress 2** (Valve) | No es low-poly, pero es el canon de estilización legible: siluetas por clase, rim light en vez de outline, detalle concentrado donde el jugador mira [ver: gamedev/arte-direccion §5] |

## 7. Cuando el low-poly NO ahorra tiempo

El mito: "low-poly = fácil". Dónde se rompe:

- **Personajes animados**: la topología de deformación no se negocia — loops en hombros/codos/caderas y edge flow correcto hacen falta igual con 800 tris que con 30k [ver: topologia] [ver: organico-personajes]. Nielsen: la geometría debe "deform properly when you hand your model off to an animator". Un personaje low-poly mal topologizado se dobla igual de mal, y con menos vértices para disimularlo.
- **Menos polígonos = cada vértice pesa más.** No hay textura ni normal map que tape una proporción fea o una silueta muerta; el error de forma queda desnudo. El tiempo se traslada de "detallar" a "decidir bien", que no es más rápido para quien no domina forma.
- **Hand-painted es low-poly y es el estilo CARO**: cada textura es una ilustración con luz pintada (§2). Elegirla "porque WoW es low-poly" es el error de presupuesto clásico.
- **La escuela PS1 exige pixel painting**: pintar una textura de 128px que lea bien es un skill específico, no una versión fácil de texturizar.
- **El look se termina en el engine (§8)**: shader, outline, luz y post-proceso son días de trabajo que el pipeline "sin texturas" no elimina — los concentra. Astroneer no ahorró en dirección de arte: ahorró en producción POR asset.
- **Facetado ≠ optimizado**: hard edges duplican vértices (§4); y un juego low-poly puede morir igual por draw calls si cada prop trae su material propio — la paleta-atlas única existe para eso [ver: pipeline/arte-a-unity §7].

Balance honesto del ahorro:

| Dónde SÍ ahorra | Dónde NO ahorra |
|---|---|
| Props y entorno estáticos: sin high-poly, sin bake, sin texturas [ver: high-to-low] | Personajes animados: topología + rig + animación cuestan igual |
| Iteración: rehacer un asset cuesta horas, no días (Astroneer) | Dirección de arte: paleta, luz y shader piden MÁS criterio, no menos |
| Variantes: recolor de paleta / re-proporción del mismo modelo | Escuelas 3 y 4: la textura pintada devuelve todo el coste 2D |
| Onboarding: cualquier skill produce on-style (Astroneer lo cita hasta para modders) | Vegetación convincente: sigue siendo de lo más difícil (Firewatch) |
| Peso de build y memoria: paleta única, texturas mínimas | Look final: días de shader/outline/luz/post que ningún estilo regala |

## 8. Puente al render: el estilo se termina en el shader y la luz

La malla low-poly es la mitad del look; la otra mitad vive en el engine. En low-poly la iluminación hace ~50% del resultado [ver: gamedev/arte-direccion §3]. Piezas del look final:

| Pieza | Qué hace | Referencia técnica |
|---|---|---|
| **Toon/cel shading** | Luz en bandas duras en vez de gradiente: step/smoothstep sobre el modelo de iluminación; especular thresholded; rim light solo en el lado iluminado (receta documentada por Roystan, con Breath of the Wild como referente: 2 bandas + rim + specular) | Shader custom o Shader Graph |
| **Outline** | Separa siluetas y "dibuja" el mundo; A Short Hike usa un outline suave para mantener legible el render a baja resolución. Alternativa sin outline: rim light (vía TF2) [ver: gamedev/arte-direccion §5] | Inverted hull o post-proceso por bordes |
| **Fog / depth cueing** | Herencia PS1: tapa draw distance Y define mood y profundidad de la paleta por distancia | Fog del engine, color coordinado con la paleta |
| **Render a baja resolución** | Pixelación como estética (A Short Hike): render target chico + upscale sin filtrado, sin AA | Render texture + point filtering |
| **Shader barato correcto** | Vertex color / paleta piden Unlit o Simple Lit, no PBR completo que nadie verá | [ver: pipeline/arte-a-unity §7] |
| **Dithering / banding** | Herencia PS1: patrones de dither y bandas de color en gradientes; refuerza el look retro | Post-proceso o shader; solo en la escuela 3 |
| **Luz y post** | Dirección de luz que modele las facetas, color grading de la paleta | [ver: gamedev/arte-direccion §4] |

Orden de trabajo del look en engine: primero shader base + luz direccional (¿las facetas/bandas leen?), después paleta bajo esa luz (los colores cambian con el grading), después outline/fog/post, y al final los ajustes finos de la paleta-atlas — que recolorean todo el juego de un tiro (§4). Iterar en otro orden obliga a repintar la paleta varias veces.

Regla dura: **ningún asset se aprueba fuera del engine.** El visor del DCC no tiene el toon shader, el outline, el fog ni la paleta de luz del juego — el asset "bonito en el viewport del DCC" no existe como dato [ver: pipeline/arte-a-unity §10]. El visual target en engine se construye ANTES de la producción en serie [ver: gamedev/arte-direccion §1].

## Reglas prácticas

1. Elige la escuela (facetado / suave / PS1 / hand-painted) según el skill 2D real del equipo: sin artista de textura → escuelas sin textura (1-2).
2. Escribe las 5 decisiones (densidad, paleta, bevels, proporción, outline/shader) en el style guide ANTES del primer asset de producción; para un agente son parámetros fijos del encargo.
3. Monta el look completo en engine (shader + outline + fog + luz) con 3-4 assets ANTES de producir en serie; toda aprobación posterior es contra esa escena.
4. Blockout de masas primarias primero; si la silueta en negro no comunica qué es el objeto, no sigas detallando [ver: blueprints-referencias].
5. Cada edge nuevo debe cambiar silueta o shading; si no, sobra [ver: topologia].
6. Exagera lo funcional (lo que se agarra, dispara o toca) y elimina lo decorativo antes de simplificarlo — borrar es el paso de estilización más barato.
7. Texturiza con UNA paleta-atlas (128-256px) compartida por todo el juego; caras a punto de color plano o a tira de gradiente; recolorear la paleta = re-skin global.
8. Vertex colors solo con un shader que los lea (unlit/custom/graph); verifica en engine, no en el viewport del DCC.
9. Objetivo: 1 material para todo el mundo estático; un material nuevo necesita justificación por escrito [ver: pipeline/arte-a-unity §7].
10. Decide hard edges vs autosmooth UNA vez para todo el juego; recuerda que cada hard edge duplica vértices en GPU — el conteo del DCC no es el del engine.
11. Escuela PS1: texturas ≤256px con point filtering + vertex snapping y affine en shader + fog; el jitter es estética, el z-fighting no — no recrees la falta de z-buffer.
12. Personaje que anima = topología de deformación completa aunque tenga 600 tris; el ahorro low-poly NO aplica al rig [ver: organico-personajes].
13. Mezclar escuelas solo como código semántico documentado (Astroneer: facetado=natural, liso=artificial); nunca por accidente.
14. Aprueba cada asset colocándolo en la escena visual-target con cámara, shader y luz reales, junto a assets existentes de su misma categoría y tamaño.
15. Variantes por recolor de paleta o re-proporción del mismo modelo antes que assets nuevos: 23 árboles bien colocados hacen un bosque (Firewatch).
16. Presupuesta días para el shader/outline/luz del look: el pipeline "sin texturas" concentra ahí el trabajo de estilo, no lo elimina.
17. Vegetación estilizada como masas sólidas (copas de esfera/cono deformado), no alpha cards, y presupuestada como asset difícil — los árboles convincentes son de lo más duro del estilo (Firewatch).
18. En low-poly la fase high-poly/bake se salta por defecto [ver: high-to-low]; si un asset "necesita" normal map, cuestiona primero si pertenece a este estilo.
19. El screenshot de la escena visual-target es el contrato: si un asset nuevo no podría aparecer en ese screenshot sin delatarse, se devuelve — el juicio es contra la escena, no contra el gusto.
20. Documenta cada excepción de estilo aprobada el mismo día; excepción sin documentar = drift garantizado.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| "Low-poly porque es fácil" y elegir hand-painted o PS1 sin skill 2D | Matriz de escuelas §2: el coste está en la textura, no en los tris; sin artista 2D → escuelas sin textura |
| Look "asset store": modelos correctos, juego sin identidad | El estilo vive en paleta+luz+shader (§8); montar el look en engine antes de producir; robar del canon (§6), no del marketplace |
| Cada asset con su propio material/colores | Paleta-atlas única (§4); auditar nº de materiales en el import [ver: pipeline/arte-a-unity] |
| Assets que no pegan entre sí aunque cada uno "se ve bien" | Las 5 decisiones (§5) congeladas + aprobación solo en la escena visual-target junto a assets vecinos |
| Facetado a medias: autosmooth por defecto dejó facetas solo donde el ángulo pasó el umbral | Decisión explícita de normals por asset y por juego; revisar shading en engine, no confiar en el default del DCC |
| Vertex colors invisibles al importar ("se importó gris") | El shader estándar no los lee: asignar el shader del juego que sí; verificación en engine parte del checklist de import |
| Sobre-detallar "para que se vea trabajado" → muddiness | Silueta > detalle (Nielsen); áreas de descanso; el detalle solo lee por contraste (§3) |
| Personaje low-poly modelado como prop (sin loops de deformación) | La topología de animación no se negocia [ver: topologia]; presupuestar el rig igual que en cualquier estilo |
| Recrear TODAS las limitaciones PS1 (incluido el z-fighting) | Recrear solo las que aportan estética: snapping, affine, texturas pixeladas, fog; el resto molesta sin nostalgia |
| Aprobar assets en el viewport del DCC con su luz neutra | Ningún asset existe hasta verse con el toon shader/outline/fog/luz del juego (§8) |
| Outline uniforme que ensucia a distancia o desaparece en el pixelado | Calibrar grosor a resolución de juego y probar a distancia real; A Short Hike usó outline SUAVE precisamente por la baja resolución |
| Escalar el detalle con más geometría en vez de mejor forma | En low-poly el upgrade es proporción/silueta/color; si un asset "necesita más polys para verse bien", el problema es de forma |
| Paleta "aproximada": cada asset usa un tono parecido pero no idéntico | La paleta-atlas única hace el color exacto por construcción; sin atlas, hex del style guide copiados, jamás re-pickeados a ojo |
| Vegetación de relleno hecha en 10 minutos que abarata todo el entorno | Presupuestarla como asset difícil (§3); pocas plantas buenas reusadas > muchas malas (los 23 árboles de Firewatch) |
| Gradientes de vertex color que "escalonan" porque la malla no tiene vértices donde transicionar | La densidad de malla es la resolución del color: añadir loops donde el gradiente los necesita, o pasar ese asset a tira de gradiente del atlas |
| Estilo aprobado con un asset suelto en fondo neutro | El estilo solo existe como CONJUNTO en la escena visual-target; la aprobación unitaria no detecta drift de las 5 decisiones |

## Fuentes

- **The Art of Astroneer: Low Poly** — Paul Pepera, System Era Softworks (blog oficial de Astroneer) — la justificación de primera mano del estilo: 2 artistas, cero texturas, asset game-ready en horas-días, facetado natural vs artificial, accesibilidad del pipeline.
- **Environmental artist Jane Ng only made 23 unique trees for Firewatch** — Game Developer (cobertura de su charla en NYU Game Center) — el dato de los 23 árboles, reuso por colocación/escala, "feel real" sin realismo, árboles a mano por falta de SpeedTree en Unity.
- **Inside the art design of Firewatch** — Jane Ng (Campo Santo), GDC 2015, vía Game Developer — traducir el estilo gráfico 2D de Olly Moss a entornos 3D estilizados que se sienten reales.
- **Crafting a tiny open world: A Short Hike** — Adam Robinson-Yu, PlayStation Blog (2021) — pixelación del 3D como estética: baja resolución + flat shading + sin AA + outline suave; pixel size ajustable; "let your imagination fill in the details".
- **Grow Home** — Wikipedia (sección de desarrollo) — equipo de 8 en Ubisoft Reflections, Unity, estilo minimalista low-poly al servicio de la animación procedural.
- **Building a PS1 style retro 3D renderer** — David Colson (david-colson.com, 2021) — los datos técnicos de la estética PS1: GTE ~90k polígonos/seg, texture pages 256×256, salida 320×240 sin subpixel (jitter), affine texture mapping, sin z-buffer (ordering tables), flat/Gouraud, depth cueing.
- **Elevating Gradient Texturing to a Standard Workflow in Blender** — 80.lv (Rayen Bahri, addon Palette Grid) — la paleta-atlas de tiras de gradiente: estructura, snapping de UVs a tiras, coste de memoria (1K ≈ ~40k vértices), consistencia copiando tiras entre paletas.
- **Talking About Stylized Character Art** — Natacha Nielsen (character artist, Blizzard), 80.lv — silueta a distancia sobre todo, sobre-detalle = muddiness, luz pintada sobre AO/bent normals horneados, áreas de descanso, topología que deforma para el animador.
- **Toon Shader tutorial** — Roystan (roystan.net) — anatomía del cel shading: bandas por step/smoothstep, especular thresholded, rim en el lado iluminado; Breath of the Wild como referente de 2 bandas.
- **Optimizing graphics performance** — Unity Manual — hard edges y UV seams = "doubled-up vertices": el conteo de vértices GPU supera al del DCC; base del coste oculto del flat shading.
- **Cobertura de Untitled Goose Game** — GamesIndustry.biz / Game Developer (Road to the IGF, House House) — low-poly liso sin texturas, look storybook, personajes sin cara con emoción por body language (claims mantenidos al mínimo de lo cubierto).
- Bases propias: [ver: gamedev/arte-direccion] (elección de estilo, lenguaje de formas, silueta, luz/color, visual target) y [ver: pipeline/arte-a-unity] (materiales/shaders URP, auditoría de import, aprobación en engine).
