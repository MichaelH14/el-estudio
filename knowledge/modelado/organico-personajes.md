# Modelado orgánico y personajes

> **Cuando cargar este archivo:** al modelar o dirigir CUALQUIER personaje/criatura 3D de juego — elegir la ruta (esculpido vs poly-modeling directo), fijar proporciones y nivel de estilización, retopologizar para animación, o resolver cabezas, manos, pies y ropa.

## 1. Las dos rutas de producción de un personaje

Antes de tocar geometría, decidir la ruta. Es LA decisión que define coste y pipeline:

| Ruta | Flujo | Cuándo | Coste |
|---|---|---|---|
| **Sculpt-based** (estándar AAA/realista/estilizado detallado) | blockout → esculpido high-poly → retopología → UVs → bake → texturizado | El estilo pide formas orgánicas con detalle de superficie (anatomía, folds, arrugas) que se hornea a normal map | Alto: cada fase es un oficio |
| **Poly-modeling directo** (low-poly estilizado, indie) | blockout → refinar silueta low-poly → UVs → texturizado plano/paleta | Estilo low-poly/flat donde la silueta y el color hacen el look; sin bake | Bajo: una sola malla, sin high-poly [ver: estilizacion-lowpoly] |

La ruta la dicta la **escala de estilización 1-10 declarada en el style guide** [ver: gamedev/arte-direccion]: por debajo de ~4 (cartoon plano, low-poly) el esculpido suele ser gasto sin retorno; el detalle que hornearías no se ve con color plano y luz estilizada.

## 2. Pipeline sculpt-based: las fases y qué entrega cada una

Proceso canon documentado por polycount (wiki, página Character):

| Fase | Entrega | Regla de oro |
|---|---|---|
| 1. Blockout | Masas y proporción del personaje, probadas EN el engine con la cámara real | Silueta y escala se validan aquí; el detalle no arregla una masa mal proporcionada [ver: gamedev/arte-direccion §5] |
| 2. Esculpido rough | Formas primarias y secundarias (anatomía grande, masas de ropa) | 80% del tiempo en formas grandes; el detalle fino espera |
| 3. Esculpido final | High-poly con detalle terciario (poros, arrugas, costuras) + polypaint opcional | Solo el detalle que el bake capturará al tamaño en pantalla real |
| 4. Retopología | Malla low-poly nueva que envuelve el sculpt, con topología para deformar | Ver §6; puede partir del nivel bajo de subdivisión del propio sculpt o hacerse de cero (polycount) |
| 5. UVs | Unwrap del low-poly; seams escondidos (interior de brazos/piernas, bajo el pelo, tras las orejas) | Cada seam UV duplica vértices en GPU (polycount): los necesarios, no más |
| 6. Bake | Normal/AO/curvature/ID del high al low | **Triangular el low-poly ANTES de bakear**: si el motor triangula distinto que el baker, el shading hace zig-zag (polycount). Detalle completo del bake: [ver: high-to-low] |
| 7. Texturizado | Mapas PBR o hand-painted sobre los bakes | Se aprueba bajo la luz del juego, no en el visor [ver: pipeline/arte-a-unity] |

- Polycount cuenta en **triángulos, no "polígonos"**: el conteo de quads de la herramienta siempre miente (todo se triangula al importar). Y el **vertex count real** manda sobre el tri count: seams UV, smoothing splits y cambios de material duplican vértices (polycount, Polygon Count).
- Rango documentado por polycount: de 2 tris (billboard) a 40.000+ tris (personaje complejo). Presupuestos por categoría y plataforma: [ver: presupuestos-poligonos]. Un ancla real publicada: el personaje principal estilizado de Thunder Cloud Studio para UE4 se planificó a ~50k tris + pelo aparte (Dzung Phung Dinh, 80.lv, 2016).

## 3. Anatomía PARA juegos: lo mínimo que vende el personaje

No hace falta anatomía médica: hace falta **proporción correcta + los landmarks que el ojo espera**. Si esos dos están, el cerebro del jugador completa el resto.

### Proporciones en cabezas de altura (canon clásico, desde Polykleitos)

La unidad es la cabeza (coronilla→mentón). Números del canon artístico (Wikipedia, Body proportions):

| Figura | Altura en cabezas | Uso |
|---|---|---|
| Humano real promedio | ~7.5 | Realismo crudo (rara vez se usa tal cual) |
| Idealizado | 8 | El default de personaje "normal" — da dignidad a la figura |
| Heroico | 8.5 | Héroes, dioses, tanques; el extra va a pecho y piernas |

Landmarks de proporción del canon (mismo origen):

- La **mitad de la altura** cae en los trocánteres mayores / justo sobre el arco púbico — NO en la cintura. Error clásico: torso largo, piernas cortas.
- Piernas = 3.5–4 cabezas.
- La **mano abierta ≈ la cara** (mentón→nacimiento del pelo). Sirve para escalar manos sin medir.

### Landmarks óseos y musculares que venden la silueta

Puntos donde el hueso toca la piel: son fijos, no cambian con el músculo/grasa, y son lo que el ojo usa para leer "esto es un cuerpo". En el blockout deben existir como cambios de plano, aunque sea con 6 polígonos:

| Zona | Landmarks | Qué venden |
|---|---|---|
| Torso | Clavículas, acromion (esquina del hombro), caja torácica, cresta ilíaca | El "perchero": ancho de hombros vs cadera = género/rol de la silueta |
| Espalda | Escápulas, columna (surco), trapecio | Postura; el trapecio conecta cuello-hombro (sin él, "cabeza clavada en palo") |
| Brazo | Codo (olécranon), muñeca (cabeza del cúbito) | Articulaciones legibles = pose legible |
| Pierna | Rótula, maléolos del tobillo (interno más alto que externo), talón | Sin rótula/tobillo la pierna es un tubo |
| Masas musculares | Deltoides, pectoral/pecho, glúteo, gastrocnemio (pantorrilla), antebrazo (masa cerca del codo, no de la muñeca) | Ritmo de la silueta: las masas alternan lados (pantorrilla alta afuera/baja adentro) |

Regla operativa: **la silueta en negro debe leerse ANTES de esculpir detalle** [ver: gamedev/arte-direccion §5]. Los landmarks son lo que hace que una silueta parezca un cuerpo y no una salchicha con extremidades.

## 4. Estilizado vs realista: reglas de exageración

La estilización NO es "dibujar mal": es redistribuir el presupuesto de detalle hacia lo que define al personaje. Referencias de proporción por estilo:

| Estilo | Cabezas de altura | Rasgos |
|---|---|---|
| Realista | 7.5–8 | Landmarks completos, proporción canon |
| Heroico | 8.5 | Hombros/pecho/manos exagerados, cabeza relativamente chica |
| Anime estándar | ~7–8 (Wikipedia, Super deformed) | Ojos grandes, nariz/boca mínimas, anatomía simplificada |
| Cartoon | ~4–6 | Cabeza y manos grandes, extremidades simplificadas |
| Chibi / super deformed | cabeza = 1/3 a 1/2 de la altura total (≈2–3 cabezas) (Wikipedia) | "Pequeño y regordete, extremidades cortas, ojos y cabeza enormes, mínimo detalle" |

Por qué exagerar funciona (consolidado del canon de readability [ver: gamedev/arte-direccion §5]):

1. **La silueta se lee por proporción, no por detalle**: exagerar proporciones distintas por rol es lo que hace identificable a un personaje a 30 metros o en pantalla chica.
2. **Los rasgos firma se conservan, el resto se simplifica**: la doc del estilo chibi lo dice explícito — el pelo/accesorio distintivo se mantiene prominente mientras los folds de la ropa desaparecen (Wikipedia, Super deformed). Es la regla general de toda estilización.
3. **A menor tamaño en pantalla, más exageración necesaria**: móvil/cámara lejana empuja hacia proporciones cartoon aunque el render sea "realista".
4. En estilizado, el detalle fino vive en la TEXTURA, no en la malla: "big & medium details" en el sculpt, lo fino pintado — más control y flexibilidad (Dzung Phung Dinh, 80.lv).

Regla dura: el nivel de estilización es GLOBAL. Un personaje chibi con manos realistas (o un realista con manos de guante) rompe el estilo al instante — todas las partes del personaje y todos los personajes del juego viven en el mismo punto de la escala [ver: gamedev/arte-direccion §2].

## 5. Topología de personaje: las zonas que deforman

Principios generales de topología (quads vs tris, poles, densidad): [ver: topologia]. Aquí SOLO lo específico de personajes. El canon de polycount (página Topology): *"la topología importa más donde el modelo más deforma: entrepierna/caderas/glúteos, hombros/axilas, comisuras/mejillas, rodillas, codos, manos/dedos"*.

| Zona | Problema | Solución estándar |
|---|---|---|
| **Hombro** | La articulación de mayor rango del cuerpo; colapsa al subir el brazo | Dos escuelas documentadas (polycount, ShoulderTopology): loops siguiendo el contorno muscular (deltoides) vs anillos concéntricos tipo "bendy straw" (fuelle); existen híbridos. Además: los rigs suben el brazo con clavícula + hombro — modelar el hombro contando con ello |
| **Codo / rodilla** | Un solo loop en el pliegue = codo/rodilla que se afila como manguera doblada | Reservar varios loops paralelos en la zona del pliegue (los ejemplos canon de polycount Limb Topology usan múltiples anillos); el lado externo estira, el interno comprime |
| **Cadera / entrepierna** | Deforma en 3 ejes (sentarse, patada, zancada) | Loops que rodean la pierna donde nace del torso + loops del glúteo; probar sentado ANTES de aprobar |
| **Muñeca / tobillo** | Torsión (pronación) | Loops perpendiculares al hueso, densidad moderada |
| **Cara (si hay expresión)** | Los blendshapes/huesos faciales arrastran vértices | **Anillos concéntricos alrededor de ojos y boca** (los dos agujeros que se abren/cierran) + loop del pliegue nasolabial (ala de la nariz → comisura): es la línea por donde la cara se dobla al sonreír. Es el patrón común de todos los ejemplos del Face Topology Breakdown Guide de polycount (wireframes de Uncharted 2, Mass Effect 3, Gears of War 3) y del diseño de topología facial "hippydrome" (referencia clásica citada por el mismo wiki) |
| **Cara (si NO hay expresión)** | — | No pagar loops faciales: cara rígida = malla mínima que sostenga la silueta y el bake |

Reglas transversales (polycount, Topology):

- **Poles** (vértices de 3 o 5+ aristas): colocarlos en zonas planas y LEJOS de las zonas que deforman.
- **Quads mientras se esculpe/subdivide** (los triángulos pellizcan al subdividir); en el low-poly final de juego los triángulos son válidos — "pero cada arista debe tener una razón".
- Densidad donde hay curvatura y deformación; nada de polígonos que no aportan a silueta, deformación o UVs.
- **Bind pose**: el debate T-pose vs A-pose está documentado en polycount (thread citado por el wiki). Práctica extendida: brazos a ~45° (A-pose) esculpe el hombro a mitad de su rango de movimiento y reparte el error de deformación entre brazo arriba y brazo abajo. Decidirlo CON el rigger antes de retopologizar, no después.
- La retopología (polycount, ReTopologyModeling) puede partir de un nivel bajo de subdivisión del sculpt (colapsar/insertar loops) o hacerse de cero sobre la superficie; ambas son válidas — lo que importa es el resultado: silueta, deformación, seams UV limpios y shading sin saltos de normales.

## 6. Cabezas, manos y pies: por qué duelen y los atajos honestos

Son las tres zonas donde se hunden los cronogramas. Presupuestarlas aparte.

### Cabeza

- Es donde el jugador SIEMPRE mira, y donde el error se percibe aunque no se sepa nombrar (uncanny valley en realismo).
- **Ojos**: esfera separada del cráneo, párpados que la envuelven — es el método documentado en producción (polycount FaceTopology recoge los métodos de Resistance 3 y el "next-gen eye" de Ben Mathis). Jamás esculpir el ojo como parte de la cara si el personaje parpadea o mira.
- **Dientes/boca interior**: solo si el personaje habla en cámara; low-poly y como pieza aparte (ejemplos en polycount FaceTopology). Si nunca abre la boca: no existen.
- **Pelo**: decisión de estilo — masa esculpida sólida (estilizado; el pelo es geometría con silueta fuerte) vs hair cards (realismo; planos con textura alpha). La masa sólida es MUCHO más barata y es la elección correcta por debajo de ~6 en la escala de estilización.
- Atajo honesto: en estilizado, la cara puede vivir casi entera en la TEXTURA (ojos/cejas/boca pintados sobre malla lisa) — válido y barato si no hay lip-sync 3D.

### Manos

- Concentran más articulaciones que el resto del cuerpo junto: 15+ huesos si los dedos son individuales, con su coste de skinning y animación — Unity documenta que cada hueso extra cuesta (15 huesos extra sobre un rig de 30 = ~50% más operaciones en modo Generic; Unity Manual).
- Escalera de atajos honestos, de más caro a más barato — elegir según cámara y estilización:
  1. 5 dedos individuales (solo si hay primeros planos o manos protagonistas).
  2. 4 dedos (convención cartoon de larga tradición; nadie cuenta los dedos en juego).
  3. **Dedos fusionados**: índice separado + los otros tres como bloque (permite señalar/apretar gatillo con mínimo coste).
  4. **Manita en guante/mitten**: pulgar + masa única. Consistente con chibi/cartoon ("extremidades cortas, mínimo detalle" — Wikipedia, Super deformed).
- La mano se modela semiflexionada (dedos con curva natural), no en tabla: la pose de reposo plana obliga al rig a trabajar más para toda pose útil.
- Escala rápida: mano ≈ cara (canon, §3). Manos chicas se leen como error antes que manos grandes — en la duda, +10%.

### Pies

- El atajo con siglos de uso: **el personaje lleva zapatos**. Un zapato/bota es un bloque con suela — sin dedos, sin arcos, sin anatomía. Modelar pies descalzos detallados solo si el diseño lo exige.
- El pie descalzo estilizado: cuña con talón y maléolos marcados; dedos como masa única o solo el pulgar separado.
- El pivot del personaje va en la BASE, entre los pies [ver: pipeline/arte-a-unity §7].

## 7. Ropa y accesorios

- **Se modela SOBRE el cuerpo terminado**: la ropa hereda la forma. Método documentado (tutorial de folds de Selwy, referenciado por polycount): construir las piezas de ropa como mallas nuevas sobre el cuerpo mid-res (quads para subdividir bien), proyectar/ajustar al cuerpo, y esculpir folds encima.
- **El cuerpo bajo ropa opaca SE ELIMINA** en el low-poly final: torso bajo una chaqueta cerrada, piernas bajo pantalón. Razones: (a) polígonos invisibles que pagan skinning y render, y (b) la causa #1 de clipping — dos superficies deformando casi pegadas SIEMPRE se atraviesan al animar. Se conserva solo la piel que asoma (cuello, manos, tobillos) con margen de solape oculto bajo el borde de la tela. Guardar el cuerpo completo en el archivo fuente (capa oculta): los rediseños de vestuario lo necesitan.
- **Capas**: cada capa de ropa suma coste de deformación y riesgo de clipping. Regla: la capa inferior solo existe donde se ve. Un abrigo sobre camisa sobre camiseta = modelar el abrigo + los trozos visibles de lo demás.
- **Folds (pliegues)**: el objetivo no es simular tela, es la ilusión — *"no vas a hacer tela real; vas a hacer que el espectador crea que es lo que piensa que es"* (Selwy). Los folds nacen de los puntos de tensión (hombros, codos, entrepierna, rodillas) y cuelgan por gravedad; estudiar referencias antes de esculpir. En estilizado: pocos folds, grandes y de diseño (la doc del estilo chibi los elimina casi por completo).
- Simulación de tela (categoría Marvelous Designer/simuladores): produce el high-poly de la ropa con folds físicos — útil en realismo; la salida SIEMPRE se retopologiza como cualquier sculpt.
- **Accesorios rígidos** (armaduras, hebillas, correas, props colgados): son hard-surface adosado al personaje [ver: hard-surface]; piezas rígidas se skinnean a UN hueso (100% de peso) para que no se doblen como goma.
- Presupuesto de materiales: el personaje entero idealmente en 1-2 materiales; Unity documenta que 2 skinned meshes en vez de 1 ≈ duplica el tiempo de render del personaje — fusionar mallas y atlasear texturas [ver: pipeline/arte-a-unity].

## 8. Esculpido digital: conceptos operativos

Agnóstico de herramienta: todo sculptor serio (ZBrush, Blender, Mudbox) tiene estos dos modos de trabajo y las mismas familias de brushes.

### Los dos modos de malla al esculpir

| Modo | Qué es | Cuándo |
|---|---|---|
| **Teselación adaptativa** (Dyntopo en Blender, DynaMesh en ZBrush) | La malla se re-tesela/subdivide DURANTE el trazo — la topología es descartable, la forma es libre; el detalle puede ser relativo al zoom, constante, o por tamaño de brush (Blender Manual, Dyntopo) | Concepting y formas primarias: cambiar proporciones y masas sin que la topología estirada lo impida |
| **Niveles de subdivisión** (Multires en Blender, subdivision levels en ZBrush) | Malla base fija + niveles de subdivisión editables; se puede bajar a niveles bajos para cambios amplios ("Sculpt Base Mesh" deforma la base viendo el detalle alto — Blender Manual, Multires) y subir para detalle fino | Detalle medio/fino sobre formas ya aprobadas; ES el formato correcto para el bake (low = nivel base, high = nivel máximo) |

Flujo estándar: **adaptativa para encontrar la forma → retopo o remesh a base limpia → subdivisión para detallar y bakear**. La teselación adaptativa destruye UVs y orden de vértices — nunca sobre una malla ya unwrapped que quieras conservar.

### Familias de brushes (conceptuales — cada software las nombra distinto)

| Familia | Función | Momento |
|---|---|---|
| Build-up tipo clay | Acumular/quitar materia en capas, como arcilla | Formas primarias y masas musculares |
| Move/grab | Empujar masas enteras — proporción y silueta | Blockout; el brush más importante y el menos usado por novatos |
| Crease/dam | Cortes y surcos definidos (pliegues, separación de piezas) | Formas secundarias |
| Flatten/planos | Aplanar — construir los planos faciales y óseos | Clave para que la forma no sea "globosa": *"no todo es tan redondo como parece"* (Selwy) |
| Smooth | Relajar ruido | Constante, con moderación (el abuso funde los planos) |
| Pinch/inflate | Afilar aristas / hinchar volúmenes | Detalle y correcciones |

### Cuándo NO esculpir

- Estilo low-poly/flat (escala de estilización baja): el detalle horneado no se verá — ir directo a §9.
- Assets secundarios/lejanos: NPC de fondo no paga sculpt de poros.
- Cuando la textura resuelve: en estilizado, esculpir solo "big & medium" y pintar lo fino da más control (Dzung Phung Dinh, 80.lv).
- Presupuesto/plazo: un personaje con buena proporción y silueta SIN detalle esculpido siempre gana a uno detallado con proporciones rotas. El detalle es lo último y lo primero que se recorta.

## 9. Low-poly estilizado SIN esculpido: el método directo indie

La ruta 2 del §1 en detalle mínimo (el estilo completo vive en [ver: estilizacion-lowpoly]):

1. **Referencias y blueprint** del personaje (front/side) [ver: blueprints-referencias]; proporciones estilizadas decididas ANTES (tabla del §4).
2. **Box modeling / extrusión**: partir de primitivas (caja/cilindro por extremidad, o extrusión continua desde el torso); espejo de simetría activo todo el proceso.
3. **La silueta ES el asset**: cada vértice se gasta en silueta y landmarks (§3), cero en superficie interior. Evaluar en negro y desde la cámara real del juego.
4. **Topología mínima pero deformable**: aunque sean 800 tris, las zonas del §5 (hombro, codo, rodilla, cadera) necesitan sus loops — un low-poly que no deforma bien es un low-poly fallido igual.
5. **Sin bake**: color por material/vertex color/paleta-gradiente [ver: gamedev/arte-direccion §9]; UVs triviales (islas al color de la paleta).
6. **Shading decidido, no accidental**: flat shading (facetado como estética) o smooth con hard edges donde la silueta lo pide — se elige por style guide, no por default del software.
7. Triángulos permitidos desde el minuto uno (polycount: en low-poly de juego los tris son válidos); la disciplina de quads es para la ruta con subdivisión.

Esta ruta produce un personaje jugable en horas en vez de semanas, y escala a equipos de una persona. El coste real se muda a: paleta, iluminación y animación.

## Reglas prácticas

1. Decide la RUTA (sculpt vs directo) por la escala de estilización del style guide antes de abrir el software; por debajo de ~4, no esculpas.
2. Fija cabezas de altura y escríbelo: 8 normal, 8.5 heroico, 2–3 chibi; TODOS los personajes del juego en proporciones coherentes.
3. Blockout con landmarks (clavículas, codos, cresta ilíaca, rótulas, tobillos) validado por silueta en negro y EN el engine antes de detallar.
4. Mitad del cuerpo en la entrepierna (trocánteres), no en la cintura; mano ≈ cara; piernas 3.5–4 cabezas.
5. Exagera lo que define el rol del personaje, simplifica el resto; conserva los rasgos firma en todo nivel de estilización.
6. En sculpt: 80% del tiempo en formas grandes con move/clay; el detalle fino solo si el bake y el tamaño en pantalla lo van a mostrar.
7. Teselación adaptativa para concepting → base limpia → niveles de subdivisión para detalle y bake; nunca adaptativa sobre malla con UVs que quieras conservar.
8. Retopología con loops donde deforma: anillos en ojos/boca + nasolabial (si hay expresión), varios loops en codos/rodillas, solución de hombro elegida CON el rigger (y bind pose acordada: T vs A ~45°).
9. Poles en zonas planas, lejos de articulaciones; quads mientras subdividas, tris válidos en el low final con cada arista justificada.
10. Cara sin expresión = sin loops faciales; boca que no abre = sin dientes; presupuesto solo a lo que anima.
11. Ojos SIEMPRE como esferas separadas si el personaje parpadea o mira.
12. Manos: elige el peldaño honesto (5 dedos → 4 → fusionados → mitten) según cámara y estilo; modélalas semiflexionadas; en la duda de escala, +10%.
13. Pies = zapatos salvo que el diseño exija lo contrario; pivot en la base entre los pies.
14. Ropa sobre el cuerpo terminado; cuerpo bajo ropa opaca SE BORRA en el low final (con margen de solape bajo los bordes); cuerpo completo guardado en el fuente.
15. Folds solo desde puntos de tensión y con referencias; en estilizado, pocos y de diseño.
16. Piezas rígidas (armadura, hebillas) skinneadas 100% a un hueso; personaje en 1-2 materiales y una sola malla skinneada.
17. Triangula el low-poly antes de bakear; los seams UV/smoothing splits duplican vértices — colócalos donde no se ven y donde la topología ya rompe.
18. Aprueba deformando: brazo arriba, sentadilla, sonrisa extrema — ANTES de dar por buena la retopo; un personaje se aprueba en pose, jamás solo en T-pose.
19. Modela con simetría de espejo activa de principio a fin; las asimetrías del diseño (accesorios, cicatrices, pose) se agregan como último paso sobre la malla ya aprobada.
20. Todo número de presupuesto (tris, texturas, huesos) sale de [ver: presupuestos-poligonos] y de la spec del proyecto [ver: pipeline/arte-a-unity], no de la costumbre.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Esculpir detalle sobre proporciones rotas ("ya lo arreglo después") | La proporción se congela en blockout con silueta validada; move/grab a nivel de masa, después no hay arreglo barato |
| Torso largo/piernas cortas (mitad del cuerpo en la cintura) | Mitad = entrepierna/trocánteres; medir en cabezas, no a ojo |
| Personaje "salchicha": sin landmarks óseos | Clavículas, codos, cresta ilíaca, rótulas y tobillos como cambios de plano desde el blockout |
| Mezclar niveles de estilización (cuerpo chibi + manos realistas; héroe cartoon junto a NPC realista) | La escala de estilización es global — por personaje y por elenco [ver: gamedev/arte-direccion] |
| Esculpir un personaje low-poly flat "para que quede mejor" | Si el estilo no hornea detalle, el sculpt es coste puro: ruta directa §9 |
| Un solo loop en codo/rodilla; codo que se afila al doblar | Varios loops paralelos reservados en cada pliegue; probar el rango completo antes de aprobar |
| Cara con loops espirales/aleatorios que "se ve bien" quieta | Anillos concéntricos en ojos y boca + nasolabial; la topología facial se aprueba con la sonrisa extrema, no en reposo |
| Pole de 6 aristas en plena axila o comisura | Poles a zonas planas (polycount); en zona de deformación solo grid limpio |
| Ojo esculpido como parte de la cara | Esfera separada + párpados; si no, no hay parpadeo ni mirada posibles |
| Manos de tabla (dedos rectos en plano) | Modelar semiflexionado: la pose de reposo natural reduce el trabajo del rig en TODAS las poses |
| Cuerpo completo bajo la ropa "por si acaso" en el modelo de juego | Se borra lo cubierto (clipping + coste); el "por si acaso" vive en el archivo fuente |
| Ropa que atraviesa el cuerpo al animar | Capa inferior solo donde se ve + margen de solape oculto; probar con las animaciones extremas del juego |
| Armadura rígida skinneada a varios huesos que se dobla como goma | Piezas rígidas 100% a un hueso |
| Personaje en 6 mallas y 8 materiales "para organizar" | 1 malla skinneada, 1-2 materiales (Unity: 2 mallas ≈ 2× render); atlas |
| Bake con shading en zig-zag | Triangular antes de bakear; misma triangulación en baker y engine (polycount) [ver: high-to-low] |
| Retopo aprobada en T-pose que explota al animar | Checklist de poses extremas (brazo arriba, sentadilla, giro de cabeza) como gate de aprobación |
| Contar "polígonos" del software y creerse dentro de presupuesto | Contar TRIángulos y vértices en el engine; los quads reportados mienten (polycount) |

## Fuentes

- **Polycount Wiki — Topology / Character / ReTopologyModeling / Polygon Count** — polycount.com (canon comunitario del game art; consultadas las páginas el 2026-07) — principios de topología (zonas de deformación exactas, poles, quads vs tris, densidad/silueta), pipeline completo de personaje, definición de retopología, tris vs vertex count reales, triangular antes del bake, rango 2 tris–40k+.
- **Polycount Wiki — FaceTopology / BodyTopology / ShoulderTopology / Limb Topology** — polycount.com — galerías canon de wireframes de producción (Uncharted 2, Mass Effect 3, Gears of War 3, Bayonetta), escuelas de hombro (muscle-contour vs bendy-straw, Pior Oberson), métodos de ojo (Resistance 3, Ben Mathis), debate de bind pose, referencia al diseño facial "hippydrome".
- **The Art of Moving Points / HippyDrome** — hippydrome.com — referencia clásica de topología para articulación/animación citada repetidamente por el wiki de polycount; el sitio hoy solo conserva la portada, que redirige a su contenido publicado como libro en Apple Books bajo ese mismo título. NO VERIFICADO de primera mano el nombre/título profesional del autor (las páginas instructivas del sitio dan 404 y no se localizó una bio fiable) — se cita únicamente como la referencia que el wiki de polycount señala para el patrón de topología facial.
- **Secrets of Human Shaders in UE4** — Dzung Phung Dinh (Thunder Cloud Studio), entrevista en 80.lv — pipeline estilizado real (ZBrush→Maya→xNormal→Substance/BodyPaint→UE4), personaje principal planificado a ~50k tris, filosofía "big & medium details en sculpt, lo fino en textura", "no me importa fakearlo si se ve bien".
- **Body proportions** — Wikipedia (consultado 2026-07) — canon de cabezas de altura (7.5 real, 8 idealizado, 8.5 heroico), mitad del cuerpo en los trocánteres, piernas 3.5–4 cabezas, mano ≈ cara, origen en Polykleitos.
- **Super deformed (chibi)** — Wikipedia (consultado 2026-07) — definición y proporciones del estilo (cabeza = 1/3–1/2 de la altura), anime estándar 7–8 cabezas, simplificación de folds y conservación de rasgos firma.
- **Blender Manual — Dyntopo** — docs.blender.org (Sculpt Mode) — teselación dinámica durante el trazo, métodos de detalle (relative/constant/brush/manual), subdivide/collapse — la mitad conceptual "adaptativa" del esculpido.
- **Blender Manual — Multiresolution Modifier** — docs.blender.org — niveles de subdivisión, Sculpt Base Mesh, y bake normal/displacement/vector-displacement desde multires (viewport level 0 como low) — la mitad conceptual "niveles" y su rol en el bake.
- **ZBrush Clothes Tutorial** — Benjamin "Selwy" Leitgeb (selwy.com; citado por polycount CharacterSculpting) — folds creíbles: ilusión sobre simulación, piezas de ropa construidas en quads sobre el cuerpo mid-res, proyección, flatten ("no todo es tan redondo como parece"), estudio de referencias.
- **Modeling characters for optimal performance** — Unity Manual (docs.unity3d.com) — 1 solo Skinned Mesh Renderer por personaje (2 mallas ≈ 2× render), máximo 4 influencias de hueso por vértice, coste por hueso (15 extra sobre 30 ≈ +50% operaciones en Generic), mínimo de materiales.
- Base propia sintetizada: [ver: gamedev/arte-direccion] (silueta, escala de estilización, visual target, pipeline 3D general) y [ver: pipeline/arte-a-unity] (spec de entrega, pivots, materiales URP, LODs `_LOD0..n`).
