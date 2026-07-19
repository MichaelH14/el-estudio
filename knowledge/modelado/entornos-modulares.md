# Entornos y estructuras modulares

> **Cuando cargar este archivo:** al planificar o modelar el entorno de un nivel — kits modulares de arquitectura (muros, pisos, esquinas), trim sheets y tileables, terreno, vegetación básica — o al decidir grid, pivots y métricas de escala antes de producir la primera pieza.

## 1. Filosofía del kit modular

Un **kit** es un sistema de piezas de arte reutilizables que encajan entre sí sobre un grid. La definición canónica (Joel Burgess & Nate Purkeypile, Bethesda, sobre Skyrim): *"kits are systems"* — un kit de tuberías puede ser solo 4 piezas, pero **"el atributo más importante de un kit es que suma mucho más que sus partes"**. No se modelan niveles: se modela un alfabeto y los niveles se escriben con él.

Por qué TODO juego con niveles usa kits:

| Razón | Detalle |
|---|---|
| Economía de producción | Skyrim: **2 artistas de kits + 8 level designers → 400+ celdas interiores únicas con 7 kits en ~2.5 años**. Un equipo de arte chico alimenta a un equipo de diseño grande |
| Iteración de diseño | El level designer rearma el layout sin pedir arte nuevo; el arte no bloquea al diseño |
| Coherencia visual | Todas las piezas comparten escala, texel density y materiales → el mundo se ve de una sola mano [ver: gamedev/arte-direccion] |
| Rendimiento | Pocas mallas únicas repetidas cientos de veces = instancias y batching baratos (§8) |
| Memoria | Un kit + trim sheets cubre kilómetros de nivel con un puñado de texturas (§4) |

Flujo estándar: **métricas de gameplay congeladas [ver: gamedev/level-design] → greybox del kit → level designer arma espacios de prueba → se aprueba el sistema → recién entonces se detalla y texturiza cada pieza**. El detalle nunca va antes que la validación del sistema.

Economía de piezas (lección de Bethesda): el valor está en las piezas estándar que se usan **"cientos si no miles de veces"**. Las *hero pieces* (piezas únicas elaboradas) consumen tiempo desproporcionado para aparecer una vez — se presupuestan aparte y al final, no al inicio.

## 2. El grid: la decisión que gobierna todo

El grid se decide ANTES de modelar la primera pieza y no se cambia después: cada pieza existente hereda cualquier cambio.

### Módulo base

Con 1 unidad = 1 m [ver: pipeline/arte-a-unity]:

| Módulo base | Uso típico | Trade-off |
|---|---|---|
| 1 m | Interiores densos, pasillos estrechos, detalle fino | Máxima flexibilidad, más piezas que colocar y gestionar |
| 2 m | Interiores estándar (FPS / tercera persona), edificios | El equilibrio habitual: pocas piezas, espacios jugables cómodos |
| 4 m | Exteriores, naves industriales, murallas, calles | Rapidísimo de armar; espacios chicos imposibles sin sub-piezas |

Reglas de dimensionado (fuentes: Skyrim + breakdown 80.lv):

- **Potencias de 2 entre piezas**: los tamaños de las piezas deben ser múltiplos unos de otros. Ejemplo real (kit de desierto en UE, 80.lv): grid de 10 cm, piso de 512 cm, muros de 256 cm — dos muros = un piso, siempre cierra.
- **Footprint** (Skyrim): cada pieza tiene un *footprint* — el volumen completo que ocupa en el grid — y la geometría vive DENTRO del footprint, no en su borde. Footprints múltiplos entre sí = nada queda desalineado.
- Alturas estándar por planta: fijar UNA altura de muro (típico 3 m, ver §6) y que piso + techo + muro sumen exactamente la altura de planta, para poder apilar pisos verticalmente sin gaps.

### Pivots y snapping

| Regla | Detalle |
|---|---|
| Pivot consistente en TODO el kit | Misma convención en cada pieza: esquina inferior del footprint o centro-base. Skyrim usa centro a nivel de suelo; kits de tubería pivotan en el borde para encadenar como bisagra. Lo importante no es cuál, es que sea LA MISMA |
| Pivot en coordenada de grid | El pivot cae en una intersección del grid → snap posiciona la pieza perfecta sin ajuste manual |
| Rotaciones de 90° | El kit se diseña para funcionar rotado a 90/180/270°; piezas direccionales (que solo funcionan en una orientación) se documentan como tales |
| Verificación | Dos piezas adyacentes snapeadas: cero gap, cero overlap, sin z-fighting en la costura. Se prueba en las 4 rotaciones |
| Criterio de import | Pieza instanciada con rotación (0,0,0), apoyada en Y=0 por su pivot [ver: pipeline/arte-a-unity §7] |

El snapping es la razón de existir del grid: si el level designer tiene que colocar piezas "a ojo", el kit fracasó como sistema.

## 3. Diseñar el kit: piezas mínimas y proceso

### Lista mínima de un kit arquitectónico

Categorías de pieza (consolidado de Skyrim; los nombres varían, las categorías no):

| Pieza | Notas |
|---|---|
| Muro recto | La pieza que más se repite; 1-2 variantes de superficie desde el día 1 |
| Esquina interior | 90° hacia adentro |
| Esquina exterior | 90° hacia afuera — NO es la interior rotada: la cara visible es otra |
| Muro con puerta | Hueco + marco. **El marco de puerta se estandariza entre TODOS los kits del juego** (Skyrim): permite transiciones entre kits y una sola referencia de animación/métricas |
| Muro con ventana | Hueco + marco; decidir si el vidrio es pieza aparte |
| Piso | Tile del tamaño del módulo (o 2×2 módulos) |
| Techo | Con su grosor real: se ve al apilar pisos |
| Remates (trim) | Zócalos, cornisas, molduras, bordes de techo: esconden costuras y rematan la silueta |
| Escalera / rampa | Con la métrica de escalón del §6; su footprint también snapea |
| Pilar / columna | Tapa esquinas, intersecciones y costuras verticales |

Extensiones cuando el layout las pida: intersecciones 3-way y 4-way de pasillo, habitaciones prefabricadas (chica/grande), piezas de transición entre kits (*glue kits*, Skyrim: piezas de alcance mínimo solo para pegar un sistema con otro), plataformas.

### Proceso: probar el kit ANTES de detallar

Protocolo de stress-test (Skyrim) sobre el kit en greybox:

1. **Armar espacios reales**: un level designer (no el artista) monta habitaciones, pasillos y loops con el kit crudo.
2. **Cerrar loops**: el kit debe poder volver sobre sí mismo pasando por varios sub-kits sin desfase acumulado.
3. **Apilar en vertical**: verifica grosores de piso/techo y altura de planta.
4. **Configuraciones no previstas**: usar piezas "mal" a propósito (pasillos como sala con pilares) — los usos imprevistos son el valor del sistema.
5. **Adyacencias**: toda pieza junto a toda pieza, sin overlaps.

Solo cuando el greybox sobrevive esto se invierte en high-poly, bake y texturas [ver: high-to-low] — el detalle no arregla un sistema roto, lo fosiliza. Señal de alarma de Skyrim: si aparecen **patch-up pieces** (piezas especiales para tapar un problema de layout concreto), el footprint está mal diseñado; se arregla el sistema, no se parchea.

Naming: prefijos consistentes por kit y tipo (`DunCaveWall01`); la lección de Bethesda es balancear brevedad con legibilidad — un sufijo críptico que nadie descifra es deuda para todo el proyecto.

## 4. Tileables y trim sheets para arquitectura

### Los tres tipos de textura de entorno

| Tipo | Qué es | Cuándo |
|---|---|---|
| **Tileable** | Textura que repite en X e Y (ladrillo, concreto, piso) | Superficies grandes y continuas; texel density consistente con el resto [ver: pipeline/arte-a-unity] |
| **Trim sheet** | Una textura de tiras horizontales (molduras, zócalos, marcos, bordes metálicos), cada tira tileable en X; la geometría mapea sus caras a la tira que le toca | Todo el detalle lineal de arquitectura: marcos, cornisas, vigas, rieles |
| **Bake único** | Textura exclusiva de un asset [ver: high-to-low, props-armas] | Solo hero assets que se ven de cerca y una vez |

### El caso canon: "The Ultimate Trim" (Sunset Overdrive, GDC 2015)

Insomniac texturizó **una ciudad de ~1400 × 2400 m con 8-12 environment artists** con esta técnica (Morten Olsen). Sistema:

- Un **layout de trim estandarizado**: mismas proporciones de tiras en TODOS los materiales (varias tiras horizontales de distintas alturas + una fila inferior de detalles/caps: tornillos, placas, círculos).
- **Biseles de 45° en el normal map a lo largo de todos los bordes** de cada tira: la geometría low con hard edges mapeada al trim luce como high-poly biselado sin geometría extra.
- Por cada tipo de material, **un par trim + tileable liso**: con esos dos "podemos cubrir cualquier superficie del juego".
- Como el layout es idéntico entre materiales, **cambiar el material de un edificio entero es cambiar una textura** — todos los bordes siguen cayendo en su sitio.
- Variación por encima: vertex color multiplicado por máscaras de brochazos procedurales para romper uniformidad sin nuevas texturas.

Reglas de aplicación del trim (deck de Olsen + práctica reportada en el foro de Polycount):

- Los biseles deben ser 45° exactos y las islas UV necesitan **padding** real contra las tiras vecinas — sin padding hay seams y sangrado de mips.
- **Hard edges** en la geometría donde el bevel del normal map hace la transición (normales promediadas arruinan el efecto).
- Funciona a distancia media (arquitectura, props de calle); inspección extrema de cerca revela el truco; no es para orgánico.
- Las UVs pueden salirse del rango 0-1 a lo ancho (las tiras tilean en X) y una misma cara puede cortarse y desplazarse a otra zona de la tira para variar el desgaste.

### Romper la repetición

Un tileable perfecto se delata por repetición. Arsenal (en orden de coste):

| Técnica | Detalle |
|---|---|
| Decals | Manchas, grietas, grafitis, posters proyectados sobre el módulo — rompen el patrón sin tocar la textura base |
| Props | Cajas, tuberías, cables, basura contra los muros: interrumpen la lectura del tile y dan escala |
| Variantes de módulo | 2-3 versiones del muro estándar (limpio / dañado / con detalle) mezcladas al colocar |
| Vertex color / máscaras | Tinte y desgaste por instancia sobre el mismo material (el sistema de brushstrokes de Sunset Overdrive) |
| Kit-bashing | Mezclar piezas de kits distintos (Skyrim: pasillos dwemer + cueva de hielo) cambia la atmósfera reutilizando arte |
| Iluminación | Variar luz y sombra por zona: el mismo pasillo leído distinto |

La motivación es real: con >100 h de juego medianas (Skyrim), la repetición visible fatiga — la respuesta nunca es copy-paste del mismo bloque de habitación, es variar la capa de detalle sobre la misma arquitectura.

## 5. Terreno del engine vs geometría (mallas)

Los sistemas de terreno de engine (Unity Terrain, UE Landscape) son **heightmaps**: una altura por punto del plano. Eso define exactamente qué pueden y qué no.

| Se hace con TERRENO | Se hace con MALLAS |
|---|---|
| Colinas, valles, planicies esculpidas con brushes | Cuevas, túneles, voladizos, arcos (imposibles en heightmap: una sola altura por punto) |
| Pintado de capas de material (pasto/tierra/roca) con blending | Acantilados y paredes verticales (el heightmap estira los texels en pendientes extremas; se tapan con mallas de roca) |
| Vegetación y detalle instanciado (pasto, piedras) pintado encima | Toda la arquitectura: edificios, muros, calles con precisión, puentes |
| Grandes extensiones con LOD automático y tiles vecinos | Rocas y peñascos modulares (3-5 rocas rotadas/escaladas pueblan un mapa entero) |

Reglas de frontera:

- **La costura malla-terreno se esconde**, no se pelea: rocas, vegetación o una falda de geometría en la base del edificio tapan la intersección.
- Calles y caminos precisos: malla sobre el terreno (o sistema de splines/decals del engine), no pintura de heightmap — el heightmap no da bordes limpios.
- Si el juego es interior o de espacios construidos, probablemente no necesita terreno: todo mallas modulares.

## 6. Escala arquitectónica para gameplay

**Los espacios de juego no son humanos.** Un pasillo a medida real se siente claustrofóbico con cámara de juego; las métricas se derivan del personaje, la cámara y las mecánicas — no de un plano de arquitecto [ver: gamedev/level-design]. Métricas de referencia (The Level Design Book):

| Elemento | Unity (1 u = 1 m) | Unreal (cm) | Quake/Source (in) | Vida real (in) |
|---|---|---|---|---|
| Jugador (ancho × alto) | 1.0 × 1.8 | 60 × 176 | 32 × 72 | 20 × 69 |
| Altura de ojos | 1.5-1.7 | 152 | 64 | 66 |
| Muro (grosor × alto) | 0.1 × **3.0** | 20 × 300 | 16 × 128 | 6 × 96 |
| Pasillo mínimo (ancho) | **2.0** | 150 | 64 | 48 |
| Puerta (ancho × alto) | **1.25 × 2.5** | 110 × 220 | 56 × 112 | 36 × 80 |
| Escalón (alto × huella) | 0.1 × 0.15 | 15 × 25 | 8 × 12 | 7 × 11 |

Nota: el juego usa muros de ~3 m y puertas de ~1.25 × 2.5 m contra los ~2.4 m y 0.9 × 2 m reales — **todo más ancho y más alto que la realidad**.

Principios (Level Design Book + Skyrim):

- **Pasillo ≥ 2× el ancho del jugador** como mínimo absoluto; Skyrim fijaba el espacio transitable mínimo en 2 anchos de personaje para que la IA pudiera esquivarse.
- Cámara en tercera persona exige aún más holgura que primera persona (la cámara orbita detrás y colisiona con los muros).
- Escaleras cómodas: pendiente de **30-35°**; más empinado transmite tensión (usable como herramienta, no como default).
- Pendientes para IA (Skyrim): 60° máximo navegable, pero 30-45° para que la animación no se vea rota.
- La validación es jugada, no matemática: se recorre el greybox con el controller real y se ajusta hasta que "se siente bien"; las tablas son punto de partida.
- Estas métricas se congelan ANTES de diseñar el kit (§2): el hueco de puerta del kit ES la métrica de puerta del juego.

## 7. Vegetación básica

La vegetación de juego no se modela hoja por hoja: se construye con **cards** (planos con textura de alpha) sobre un atlas de follaje.

- **Atlas de follaje**: una textura con clusters de hojas/ramas + alpha. Las cards del árbol/arbusto muestrean regiones del atlas; un solo material para toda la especie.
- **Card ≠ quad**: la silueta de la card se ajusta al contenido (más vértices, menos área transparente). Cada pixel de alpha transparente se paga igual que uno visible — el coste dominante de la vegetación es **overdraw** (capas de transparencia apiladas en pantalla), no el polycount. Los impostors "tight-fitting" que minimizan pixels transparentes existen exactamente por esto (Simplygon).
- **Jerarquía de LOD vegetal**: malla completa (tronco geometría + cards) → cards reducidas → **billboard/impostor** (1-2 planos que encaran a la cámara o billboard cloud pre-horneado) → culled. Los generadores automáticos (Simplygon) reducen el tronco por triángulos y convierten el follaje en billboards con texturas horneadas.
- **Colocación instanciada**: la vegetación se pinta con el sistema de foliage del engine, nunca colocando actores sueltos — en UE, el Static Mesh Foliage agrupa instancias en batches por hardware instancing (un draw call por cluster) mientras que el foliage de actores cuesta como actores individuales. Configurar **cull distance** (inicio/fin) por especie y fade por instancia para que el pasto desaparezca sin pop; el LOD cambia por cluster completo, no por instancia.
- El pasto denso solo existe cerca de la cámara (cull distance corta); los árboles persisten lejos como billboards.
- Práctica extendida adicional — normales de las cards transferidas desde una forma envolvente simple (domo/esfera) para que el follaje se ilumine como volumen y no como planos sueltos: NO VERIFICADO en las fuentes consultadas para este archivo (la wiki de Polycount estaba caída); confirmar antes de darlo como regla.

## 8. Optimización de entorno

Marco canónico ("Beautiful, Yet Friendly", Guillaume Provost): el coste de una escena es **densidad de vértices × densidad de textura × espectro de visibilidad**, y cada superficie tiene dos costes en paralelo — transformar vértices y llenar pixels — donde **el más lento de los dos manda** (transform-bound vs fill-bound).

| Palanca | Cómo se usa en entornos |
|---|---|
| **Espectro de visibilidad** | El factor #1: cuanto menos se ve desde cada punto de cámara, más detalle cabe en lo que sí se ve. Se encoge con puertas, esquinas en S, zonas de transición, fog y distancia de dibujado. Se diseña en el layout, no se parchea después |
| **Instancias** | El mismo módulo/prop repetido con el mismo material se dibuja en 1 draw call (GPU instancing; pensado para "cosas que aparecen muchas veces: árboles, arbustos" — y módulos de kit). Requisito: misma malla + mismo material → NO romper el material de un módulo por variar (variar por instancia: vertex color, material properties) |
| **Los instanciados se optimizan primero** | Provost: un objeto repetido multiplica su coste por cada copia — optimizar la malla que aparece 500 veces rinde 500× |
| **Occlusion culling** | No dibujar lo tapado. Solo la geometría estática ocluye; requiere bake; rinde cuando el proyecto es GPU-bound por overdraw y la escena tiene espacios bien separados (cuartos y pasillos). En escenas abiertas sin oclusores grandes puede costar más de lo que ahorra |
| **Distancia de dibujado** | Cull distance por categoría de objeto (props chicos mueren antes que edificios), fog que justifica el horizonte, billboards para lo lejano (§7) |
| **LODs** | 2-3 niveles + culled para todo lo que se ve a distancias variables; entregados con el asset, no "después" [ver: pipeline/arte-a-unity §7] |
| **Presupuesto** | Tris y materiales por categoría de pieza, fijados en el style guide [ver: presupuestos-poligonos] |

Regla de diseño de kit derivada: **menos materiales = más batching**. Un kit entero compartiendo 1 trim + 2-3 tileables no solo es coherente visualmente — es la diferencia entre cientos y miles de draw calls.

La topología del módulo importa menos que su coste sistémico: un muro de kit es geometría simple [ver: hard-surface, topologia]; el rendimiento del entorno se gana en visibilidad, instancias y materiales, no quitando 20 tris a una pieza [ver: fundamentos-3d].

## Reglas prácticas

1. Congela métricas de gameplay (jugador, puerta, pasillo, escalón) ANTES de diseñar el kit; el kit las materializa [ver: gamedev/level-design].
2. Elige el módulo base (1/2/4 m) según la densidad de espacios del juego y no lo cambies tras producir piezas.
3. Tamaños de pieza en potencias de 2 y footprints múltiplos entre sí; la geometría vive dentro del footprint.
4. Una sola altura de muro estándar; piso + muro + techo suman la altura de planta exacta (verifícalo apilando).
5. Pivot con la MISMA convención en todo el kit (esquina o centro-base), sobre coordenada de grid; pieza recién importada: rotación (0,0,0), apoyada en Y=0 [ver: pipeline/arte-a-unity].
6. Marco de puerta único estandarizado para TODOS los kits del juego.
7. Kit mínimo antes de ampliar: muro, esquina interior, esquina exterior, muro-puerta, muro-ventana, piso, techo, remate, escalera, pilar.
8. Greybox del kit y stress-test (loops, apilado vertical, adyacencias, usos imprevistos) ANTES de high-poly y texturas; quien prueba el kit es quien armará niveles con él.
9. Si necesitas una pieza-parche para un caso concreto, el footprint está mal: arregla el sistema.
10. Presupuesta las hero pieces al final; el tiempo va a las piezas que se repiten cientos de veces.
11. Texturiza arquitectura con trim sheet + tileables compartidos; bake único solo para hero assets.
12. Trim sheet: biseles 45° exactos, padding entre tiras, hard edges en la geometría donde el normal map hace el bevel.
13. Estandariza el layout del trim entre materiales: cambiar el look de un edificio = cambiar una textura.
14. Rompe la repetición en capas: decals + props + variantes de módulo + vertex color/máscaras + kit-bashing; nunca copy-paste de bloques enteros.
15. Terreno solo para lo que un heightmap puede: cuevas, voladizos, acantilados y arquitectura son mallas; la costura malla-terreno se tapa con rocas/vegetación.
16. Vegetación: cards con silueta ajustada al alpha (el enemigo es el overdraw), atlas por especie, pintada con el sistema de foliage instanciado del engine, con cull distance y fade configurados.
17. Mismo módulo + mismo material = instancia barata: no rompas el material por pieza; varía por instancia (vertex color, decals).
18. Diseña el espectro de visibilidad en el layout (puertas, esquinas, fog): es la palanca de rendimiento #1 de un entorno.
19. Optimiza primero lo que más se repite: el muro estándar amortiza cada tri que le quites por cada una de sus mil copias.
20. Todo se valida EN el engine con la cámara y luz reales del juego, recorriéndolo con el controller — no en el viewport del DCC [ver: gamedev/arte-direccion].

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Modelar "el nivel" como malla única gigante | Kit modular sobre grid; el nivel es un arreglo de piezas, no un asset |
| Detallar las piezas antes de probar el sistema | Greybox + stress-test de Skyrim (§3); el detalle fosiliza los errores de footprint |
| Cada pieza con su propio tamaño "porque el concept lo pedía" | Potencias de 2 y footprints múltiplos; el concept se adapta al grid, no al revés |
| Pivots inconsistentes (uno al centro, otro en esquina) | Convención única de pivot en el kit; auditar apoyando en Y=0 y snapeando dos piezas |
| Gaps o z-fighting en las costuras al snapear | Verificación de adyacencia en las 4 rotaciones antes de aprobar cada pieza; remates/pilares tapan costuras legítimas |
| Puertas de cada kit con su propio tamaño | Marco de puerta estandarizado a nivel de juego (Skyrim) |
| Espacios a escala real que se sienten enanos en juego | Métricas de juego (§6): puertas ~1.25 × 2.5 m, pasillos ≥ 2× el jugador, muros ~3 m; validar recorriendo |
| Texturizar cada módulo con bake único | Trim + tileables compartidos; el bake único no escala a un entorno |
| Trim sheet con seams y bordes sucios | 45° exactos, padding contra sangrado de mips, hard edges en la transición |
| Muro tileable impecable que se ve a repetición a 10 m | Capas de ruptura (§4): decals, props, variantes, vertex color; presupuestarlas desde el diseño del kit |
| Cavar cuevas o voladizos en el terreno del engine | Heightmap no puede: cuevas/overhangs son mallas; el terreno se perfora y se tapa con geometría |
| Costura malla-terreno a la vista | Rocas, faldas de geometría o vegetación sobre la intersección |
| Pasto y árboles colocados como objetos sueltos | Sistema de foliage instanciado del engine + cull distances por especie; actores sueltos = un draw call cada uno |
| Cards de vegetación como quads gigantes casi todos transparentes | Silueta de card ajustada al contenido; overdraw es el coste real de la vegetación |
| Variar módulos duplicando el material ("muro_rojo", "muro_azul") | Mismo material + variación por instancia (vertex color/máscaras); duplicar materiales mata instancias y batching |
| Confiar el rendimiento al occlusion culling en un mapa abierto sin oclusores | El culling rinde en cuartos/pasillos y proyectos GPU-bound; en abierto: cull distance, LODs, billboards y diseño de visibilidad |

## Fuentes

- **Skyrim's Modular Approach to Level Design** — Joel Burgess & Nate Purkeypile (Bethesda), Gamasutra/Game Developer 2013 (companion de su charla GDC 2013) — el canon de kits: definición de kit como sistema, footprints, pivots, marcos de puerta estandarizados, stress-testing, glue kits, kit-bashing, art fatigue, hero pieces, patch-up pieces; números de producción (2 artistas + 8 LDs, 400+ celdas, 7 kits, ~2.5 años; personaje 128 unidades ≈ 6 ft; espacio mínimo 2 anchos de personaje; pendientes 60°/30-45°).
- **The Ultimate Trim: Texturing Techniques of Sunset Overdrive** — Morten Olsen (Principal Environment Artist, Insomniac Games), GDC 2015; PDF oficial en media.gdcvault.com (leído directo) — layout de trim estandarizado + biseles 45° en normal map, par trim + tileable por material, swap de materiales con UVs estandarizadas, brushstroke masks con vertex color; ciudad ~1400 × 2400 m con 8-12 environment artists.
- **Hilo "The Ultimate Trim technique" — foro de Polycount** (polycount.com/discussion/160794) — práctica aplicada del trim: 45° exactos, padding contra mip bleeding, hard edges, límites (distancia media, no orgánico).
- **The Level Design Book — Metrics** — Robert Yang et al. (book.leveldesignbook.com) — tabla de métricas por engine (Unity/Unreal/Quake-Source/vida real): jugador, muro, pasillo, puerta, escalón; pasillo ≥ 2× jugador, escaleras 30-35°, "video game spaces are not human".
- **Beautiful, Yet Friendly** — Guillaume Provost (Game Developer Magazine 2003; copia en ericchadwick.com) — canon de optimización de entornos: coste = densidad de vértices × densidad de textura × espectro de visibilidad; transform-bound vs fill-bound; encoger la visibilidad con puertas/fog; optimizar primero lo instanciado.
- **Building a Desert Scene with Modular Kit & Trim Sheets** — Chris Sims, 80.lv — breakdown moderno: grid de 10 cm en UE, piso 512 cm / muros 256 cm (potencias de 2), un trim sheet para marcos y molduras reutilizado en toda la escena.
- **Unity Manual — Terrain (Using Terrains)** — docs.unity3d.com — sistema de terreno heightmap: esculpido con brushes, pintado de texturas, árboles y detalle, tiles vecinos; base de la frontera terreno vs mallas.
- **Unity Manual — Occlusion Culling** — docs.unity3d.com — qué es (renderers tapados no se dibujan), relación con frustum culling, requisitos (estático + bake por celdas), cuándo rinde (GPU-bound por overdraw, cuartos/pasillos) y cuándo no.
- **Unity Manual — GPU Instancing** — docs.unity3d.com — misma malla + mismo material = un draw call; caso de uso declarado "árboles y arbustos"; límites por plataforma y pipeline.
- **Unreal Engine Documentation — Foliage Mode** — dev.epicgames.com — Static Mesh Foliage con hardware instancing por clusters vs Actor Foliage (coste de actor), Start/End Cull Distance, fade por instancia, LOD por cluster, foliage.DensityScale.
- **Simplygon — Vegetation Optimization** — simplygon.com — billboard clouds para follaje, impostors "tight-fitting" que minimizan pixels transparentes para bajar overdraw, reducción de tronco por triángulos + follaje a billboards en cadenas de LOD.
- Bases ya sintetizadas: [ver: gamedev/arte-direccion] (trim sheets/modularidad como principio, visual target), [ver: pipeline/arte-a-unity] (pivots, escala 1 m, LODs `_LOD*`, texel density, specs de entrega), [ver: gamedev/level-design] (métricas y layout).
