# Animación de criaturas y no-bípedos

> **Cuando cargar este archivo:** al animar CUALQUIER cosa que no camine sobre dos piernas — cuadrúpedos (caballo, lobo, oso), aves y voladores, insectos y arácnidos multi-pata, serpientes/gusanos/reptantes, peces y nadadores, y criaturas fantásticas que combinan varios de esos patrones (dragón, hidra, ciempiés gigante). Cubre el HUECO que deja el resto de la base, que asume bípedo humano casi en exclusiva. Aquí va: los gaits y el timing de pisada de cada patrón, cómo se estructura el rig de cada cuerpo, y cuándo procedural vs keyframe vs mocap. Da por sabidos los principios generales ([ver: principios-produccion]), la mecánica del ciclo bípedo ([ver: ciclos-locomocion]) y la anatomía del esqueleto ([ver: rigging/esqueletos-armature]) — los CRUZA, no los repite.

Frontera: esto es animación 3D agnóstica de herramienta (qué poses, qué timing, qué gait). La construcción del hueso concreto vive en rigging; el cableado del motor en [ver: unity/animacion-unity]. La regla madre de [ver: principios-produccion §1] sigue mandando: no animas una actuación, animas un **clip que el motor loopea/blendea** — todo aquí debe cerrar loop ([ver: ciclos-locomocion §6]) y sincronizar fase entre clips o el blend patina.

---

## 1. El criterio de arranque: descomponer antes de animar

La trampa nº1 con criaturas es tratarlas como "un bicho raro". No lo son: **casi toda criatura es una recombinación de patrones de locomoción conocidos**. Antes de poner un solo key:

1. **Identifica el patrón real** de cada parte del cuerpo (¿esa cola es serpiente? ¿esas patas son cuadrúpedo? ¿esas alas son ave o murciélago?).
2. **Consigue video de referencia del animal real** análogo — es INNEGOCIABLE (§12). La locomoción animal es contraintuitiva: nadie sabe de memoria el orden de pisada de un caballo caminando, y los artistas dibujaron el galope MAL durante siglos hasta que Muybridge lo fotografió en 1878 (§12).
3. **Elige el motor de autoría** por parte: keyframe (hero), procedural/IK (multi-pata, colas, terreno irregular), o simulación/spring ([ver: movimiento-secundario]) para lo que cuelga (§11).

| Cuerpo de la criatura | Patrón(es) que hereda | Sección |
|---|---|---|
| Cuadrúpedo (mamífero, dino terópodo apoya distinto) | Gaits de cuadrúpedo | §2–§5 |
| Ave / dragón alado / grifo | Aleteo + planeo + gait terrestre al posarse | §6 |
| Insecto, araña, ciempiés, cangrejo | Multi-pata (tripod/wave/ripple gait) | §7 |
| Serpiente, gusano, anguila terrestre, tentáculo | Ondulación sinusoidal / peristalsis | §8 |
| Pez, tiburón, criatura acuática | Ondulación BCF/MPF, aletas | §9 |
| Dragón, quimera, hidra, mantícora | COMBINACIÓN (el criterio) | §10 |

---

## 2. Cuadrúpedo: la estructura del cuerpo y el rig

Un cuadrúpedo NO es un bípedo con dos brazos extra en el suelo. Diferencias que definen el rig ([ver: rigging/esqueletos-armature] para huesos/roll/naming):

| Parte | Diferencia con el bípedo | Nota de rig |
|---|---|---|
| **Columna horizontal** | La columna trabaja horizontal, se comba y ondula al galope (flexión/extensión sagital = motor extra de zancada) | Cadena de spine larga; el galope necesita que la columna se arquee (bunny-hop). Considerar **spline IK** para cuello/columna largos ([ver: rigging/ik-fk-constraints]) |
| **Patas delanteras ≠ traseras** | **Delanteras**: escápula/hombro + codo (dobla hacia atrás) + carpo ("rodilla" falsa que es la muñeca). **Traseras**: cadera + rodilla + corvejón/hock (el "codo invertido" que dobla adelante) | Delantera y trasera son DOS rigs de pata distintos, no espejo. La "rodilla hacia atrás" del perro/caballo es el **tobillo/talón elevado** (digitígrado/unguligrado), no una rodilla invertida |
| **Apoyo del pie** | Plantígrado (oso, apoya toda la planta), **digitígrado** (perro, gato, sobre los dedos), **unguligrado** (caballo, sobre la punta/casco) | Cambia dónde está el "pie" efectivo y la altura del pivote. El foot IK va al punto de contacto real, no al "tobillo" |
| **Cuello** | Grande, contrapeso móvil; sube/baja con el gait y con la mirada | Cadena propia; a menudo con su bob sincronizado al paso |
| **Cola** | Balance y expresión; overlap puro | Cadena de spring/spline; overlap 2–4 frames por eslabón ([ver: movimiento-secundario]) |
| **Escápula flotante** | El hombro delantero NO está fijo a una clavícula rígida: sube y baja absorbiendo cada pisada delantera | Fuente de gran parte del "peso" del delantero; anímala, no la claves |

- **Rig en Unity: Generic, NO Humanoid.** El Avatar Humanoid exige ~15 huesos de esqueleto humano ([ver: rigging/esqueletos-armature §7]); un cuadrúpedo/criatura va como **Generic** con un **Root Node** designado, y su root motion sale de ese nodo, no del centro de masa derivado ([ver: rigging/esqueletos-armature §8], [ver: unity/animacion-unity]). Consecuencia: **no hay retargeting Humanoid entre criaturas** — cada especie es su propio rig y sus clips no se reusan entre esqueletos distintos.
- **Rigify** (Blender) trae metarig de cuadrúpedo con muestras de spine/limb aparte del humano — punto de partida a nivel mención (versión exacta NO re-verificada esta sesión; confirmar en la UI) [ver: rigging/rigify].

---

## 3. Los gaits del cuadrúpedo: el corazón del tema

Un gait es un patrón de coordinación de las 4 patas. Se ordenan por velocidad (walk → trot → canter → gallop) y cada uno tiene un **número de tiempos (beats)**, una **secuencia de pisada** y una relación **lateral vs diagonal**. Datos verificados contra *Horse gait* (Wikipedia) y *Gait* (Wikipedia):

| Gait | Beats | Secuencia / pares | Lateral o diagonal | Suspensión (fase aérea) | Pies en el suelo |
|---|---|---|---|---|---|
| **Walk** | 4 | Pata trasera → delantera del MISMO lado, luego el otro lado: **LH → LF → RH → RF** (1-2-3-4) | **Lateral** (secuencia lateral, la de casi todos los mamíferos) | **NO** | Siempre 2 o 3 |
| **Trot** | 2 | Pares **diagonales** juntos: LH+RF, luego RH+LF | Diagonal | **Disputado** (ver nota) | 2 (los diagonales) |
| **Pace** (paso llano) | 2 | Pares **laterales** juntos: LH+LF, luego RH+RF | Lateral | Breve | 2 (los del mismo lado) |
| **Canter / lope** | 3 | Trasera de apoyo → **par diagonal** → delantera líder, luego suspensión. (Right lead: LH → RH+LF → RF) | Transverso (diagonal con líder) | **SÍ** (una) | Alterna 1 y 3 |
| **Gallop** | 4 | El par diagonal del canter **se rompe** en dos tiempos: LH → RH → LF → RF, luego suspensión | Transverso (caballo) o **rotario** (guepardo, galgo) | **SÍ** — momento con **las 4 patas en el aire** | 0 en la suspensión; 1–2 el resto |

Claves para animar cada uno:

- **Duty factor** (fracción del ciclo que un pie está en el suelo): >50% = gait de "caminar" (siempre hay apoyo); <50% = gait de "correr" (aparece suspensión). Es la línea que separa walk/trot de canter/gallop (*Gait*, Wikipedia).
- **Walk = secuencia lateral por defecto.** LH, LF, RH, RF equiespaciados: contactos en tiempos normalizados ≈ **0.0, 0.25, 0.5, 0.75** (§4). La secuencia diagonal (mano y pie opuestos) es propia de primates; para bestias usa la lateral salvo referencia que diga lo contrario.
- **Trot = motor de "peso medio".** Los diagonales caen juntos; la columna estable, el rebote vertical marcado. Es el gait "de trabajo" y el más fácil de leer como cuadrúpedo sano.
- **Canter/gallop = la columna trabaja.** La flexión-extensión de la columna alarga la zancada; el momento de suspensión es con las patas **recogidas bajo el cuerpo** (Muybridge, §12), NO con las patas estiradas adelante-atrás (ese "caballito de carrusel" es el error histórico).
- **Doble suspensión en depredadores rápidos.** Guepardo, perro y gato al galope tienen DOS momentos aéreos por ciclo: uno **extendido** (patas estiradas fuera) y otro **recogido** (patas cruzadas bajo el cuerpo). El caballo tiene una sola (recogida). Anima las dos si es un felino/cánido veloz — es lo que vende la velocidad.
- **Gallop rotario vs transverso**: transverso (caballo) las delanteras pisan en el mismo orden lateral que las traseras; rotario (guepardo/galgo) el orden "rota" (LH→RH→RF→LF) y da más flexión de columna. Elige según el animal real.
- **Suspensión del trote — DISPUTADO, no lo cites como hecho cerrado**: *Horse gait* (Wikipedia) describe el trote básico SIN fase de suspensión real ("drops a bit between beats and bounces up again", explícitamente no es suspensión verdadera). El "trote volador" (flying trot / extended trot de doma, o el trote de carreras de Standardbred) sí exhibe una fase aérea a alta velocidad — es un hecho ampliamente citado en biomecánica equina, pero NO surge de la fuente Wikipedia consultada esta sesión. Trátalo así: trote de trabajo/paso = sin suspensión (fuente confirma); trote extendido/de carrera = probable suspensión breve (convención de biomecánica equina, sin fuente primaria verificada aquí). Si el gameplay solo necesita un trote genérico, anímalo SIN salto — es la versión que sí tiene respaldo directo.

---

## 4. Timing de cada pata y construcción del ciclo

Un ciclo de cuadrúpedo son **4 sub-ciclos de pata desfasados**. Se construye animando una pata completa y **desfasando (offset)** las otras tres en el tiempo normalizado del contacto:

| Gait | LH | LF | RH | RF | Método |
|---|---|---|---|---|---|
| Walk | 0.0 | 0.25 | 0.5 | 0.75 | Cuatro offsets equiespaciados |
| Trot | 0.0 | 0.5 | 0.5 | 0.0 | Dos pares diagonales en fase |
| Pace | 0.0 | 0.0 | 0.5 | 0.5 | Dos pares laterales en fase |
| Canter (R lead) | 0.0 | ~0.35 | ~0.35 | ~0.7 | Trasera, diagonal, delantera + gap de suspensión |
| Gallop (transv.) | 0.0 | ~0.55 | ~0.15 | ~0.7 | Cuatro tiempos agrupados + gap grande = suspensión |

- Cada **pata** se construye como un mini-ciclo con las mismas fases que la pierna bípeda: contact → down/absorción → passing → push-off ([ver: ciclos-locomocion §2]). La diferencia es la ANATOMÍA (§2), no las fases.
- **El delantero y el trasero se anima distinto**: el trasero EMPUJA (motor), el delantero RECIBE y frena (absorbe con la escápula flotante). No copies el timing de uno al otro.
- **Cabeza/cuello bob**: sube y baja sincronizado con el gait (en el walk el cuello baja al cargar peso en el delantero). Es firma de peso; sin él el cuadrúpedo "flota".
- **Cola**: overlap puro, arrastra 2–4 frames por eslabón; se resuelve a mano o con spring/spline ([ver: movimiento-secundario]).
- **Cierre de loop y sincronía**: las mismas reglas que el bípedo — regla del frame duplicado, tangentes iguales en el seam, y **contactos en el mismo tiempo normalizado en todos los clips de un blend tree** o el gait patina al mezclar ([ver: ciclos-locomocion §6, §8]).

---

## 5. Centro de masa y peso en cuadrúpedos

- El centro de masa está **entre las cuatro patas, más cargado al delantero** (cabeza+cuello+tórax pesan). Debe caer sobre el **polígono de apoyo** (el cuadrilátero/triángulo que forman los pies plantados) o la criatura lee como cayendo — igual que el bípedo pero con base más ancha ([ver: ciclos-locomocion §5]).
- **Graviportal** (elefante, rinoceronte, criatura enorme): patas casi verticales tipo columna, flexión mínima de articulaciones, cadencia lenta, poco rebote pero **hundimiento** (down) profundo y pesado. La masa se vende con lentitud + inercia, no con rebote. Es la plantilla para bestias colosales y jefes.
- **Cursorial** (caballo, perro, guepardo): patas largas y elásticas, mucho rebote, zancada larga, gaits rápidos. La energía se almacena en tendones (spring-mass) — el rebote es enérgico.
- **Foot IK obligatorio** sobre terreno: con 4 patas el riesgo de que un pie flote o atraviese el suelo se cuadruplica. Foot IK que planta cada pie en su contacto y adapta a desniveles ([ver: rigging/ik-fk-constraints], [ver: ciclos-locomocion §8]). En Unity, el paquete **Animation Rigging** da constraints/IK multi-hueso en runtime ([ver: unity/animacion-unity]).

---

## 6. Aves y vuelo

El ciclo de aleteo es un ciclo de locomoción como el walk, pero vertical y en el aire. Verificado contra *Bird flight* (Wikipedia):

| Fase | Qué pasa | Deformación del ala |
|---|---|---|
| **Downstroke** (power stroke) | Genera la mayor parte de sustentación y empuje; el ala barre abajo-y-adelante | Ala **totalmente extendida y rígida** (superficie máxima); ángulo de ataque activo |
| **Upstroke** (recovery stroke) | Recupera para el siguiente golpe; minimiza resistencia | Ala **plegada/flexionada hacia dentro** ("At each up-stroke the wing is slightly folded inwards to reduce the energetic cost") — se dobla por la muñeca/codo |

- **La punta del ala traza un ochо (figure-eight)**, no una línea recta. El colibrí en hover extiende el ala TODO el recorrido y hace un 8 simétrico que produce lift en ambos golpes (up y down) — por eso puede sostenerse.
- **Ángulo de ataque continuo**: el ave lo ajusta dentro de cada aleteo y con la velocidad ("Birds change the angle of attack continuously within a flap, as well as with speed"). No animes el ala como una tabla plana que sube y baja.
- **Plumas = dos funciones** (verificado): **primarias** (ancladas a los huesos de la "mano") = empuje, actúan como hélice en la punta; **secundarias** (sobre el cúbito/ulna) = sustentación, dan la superficie del brazo. La deformación del ala reparte trabajo entre ambas.
- **Planeo / soaring**: alas extendidas fijas, sin aleteo; micro-ajustes de ángulo y de punta. El "aleteo" se sustituye por deriva sutil y correcciones — nunca un ala 100% congelada (lee muerta, como un idle de un frame).
- **Despegue**: salto con las patas + primeros aleteos potentes y profundos (más amplitud, más lentos = "esfuerzo"). **Aterrizaje**: **flare** — cuerpo se endereza, ángulo de ataque alto como freno aerodinámico, alas y cola desplegadas al máximo, patas adelante; el **álula** (bastard wing) se levanta para no entrar en pérdida a baja velocidad.
- **Rig del ala**: cadena hombro → codo → muñeca → "mano"/primarias, con las plumas como huesos o como malla que se pliega/despliega (blendshape o hueso por grupo de plumas) ([ver: rigging/esqueletos-armature], [ver: rigging/deformacion]). Ala de **murciélago/dragón** = membrana entre dedos alargados: se rige con los dedos + una membrana que se deforma con ellos (más cerca de cloth/skin que de plumas).

---

## 7. Insectos y multi-pata (6, 8, muchas)

**Locomoción terrestre multi-pata** — gaits por número de patas en el suelo. El **tripod gait** está verificado (hexapod robotics, Wikipedia: "3 legs on the ground at a time"); wave y ripple son conceptos estándar de biomecánica/robótica (patrón metacrónico) que no re-verifiqué contra fuente primaria esta sesión — trátalos como convención documentada:

| Gait (hexápodo) | Patas moviéndose | En el suelo | Velocidad | Estabilidad |
|---|---|---|---|---|
| **Tripod** | 3 a la vez (delantera+trasera de un lado + media del otro): L1,R2,L3 oscilan mientras R1,L2,R3 aguantan; luego alternan | 3 siempre | **Rápido** | Estática (trípode = 3 puntos) |
| **Ripple** | 2 en un patrón escalonado tipo ola | 4 | Medio | Alta |
| **Wave / metacrónico** | 1 a la vez, las patas se levantan en una **ola** de atrás hacia delante | 5 | **Lento** | Máxima |

- **El tripod es el default del insecto que camina/corre**: dos trípodes alternos, siempre 3 patas plantadas → nunca se cae. Anímalo como DOS grupos en anti-fase (offset 0.5).
- **Arañas (8 patas)**: mismo principio, grupos alternos; patas largas con mucho overlap y "delay" — se leen elegantes si cada segmento arrastra. La araña rara vez tiene fase aérea; casi siempre hay patas en el suelo.
- **Ciempiés/milpiés (muchas patas)**: **ola metacrónica** — las patas se levantan en secuencia formando una onda visible que recorre el cuerpo. Se anima idealmente **procedural** (una función seno con offset de fase creciente por par de patas), no a mano pata por pata.
- **Vuelo de insecto**: frecuencias de aleteo altísimas — libélula ~38 Hz, avispón 100 Hz, y músculo **asíncrono** (mosquito, mosca pequeña) **>1000 Hz** (*Insect flight*, Wikipedia). **Consecuencia de producción: NO keyframees el ala insecto golpe a golpe** — es demasiado rápida y se ve borrosa en la realidad. Usa un ciclo de aleteo muy corto en loop + blur, o un par de poses de ala + un shader/plano semitransparente que finja el borrón. El cuerpo (hover, dardos, giros) sí se anima; las alas son "vibración".

---

## 8. Serpentino y reptar: la ola sinusoidal

Locomoción **ondulatoria** — una onda viajera recorre el cuerpo. Verificado contra *Undulatory locomotion* (Wikipedia): "a rostral to caudal wave that travels down their body" — la onda viaja de la cabeza a la cola y empuja lateralmente contra el entorno.

**Modos de serpiente** (verificado):

| Modo | Cómo | Cuándo lo usa | Coste |
|---|---|---|---|
| **Lateral undulation** | Ondas S de flexión lateral cabeza→cola; empuja contra puntos de apoyo. Cada punto del cuerpo **sigue la trayectoria que trazó la cabeza** | Superficie con irregularidades/obstáculos | Base |
| **Sidewinding** | Lanza bucles del cuerpo lateralmente, solo 2 puntos tocan a la vez | Arena suelta, superficie lisa | **El más bajo** |
| **Concertina** | Ancla una parte (acordeón), estira la otra, re-ancla | Túneles, trepar, espacios estrechos | **Muy alto** |
| **Rectilinear** | Línea recta, ondas de escamas ventrales, sin flexión lateral visible | Serpientes grandes, acecho | Bajo |

- **Producción**: la lateral undulation es casi siempre **procedural** — una onda seno que recorre una cadena de huesos de columna (spline IK ideal), con **amplitud creciente hacia la cola** y velocidad de onda > velocidad de avance. A mano es tedioso y propenso a que "patine" lateralmente; procedural garantiza que el cuerpo siga su propia estela. Herramientas: spline IK ([ver: rigging/ik-fk-constraints]) manejado por un driver seno, o Noise/ciclos en las F-curves ([ver: keyframes-curvas]).
- **Gusanos (peristalsis)** — verificado contra *Earthworm* (Wikipedia): dos capas musculares en oposición — **circular** (contrae → el segmento se alarga y adelgaza, alcanza hacia delante) y **longitudinal** (contrae → el segmento se acorta y engorda, **ancla** con las setas/cerdas). Una **ola de contracción recorre el cuerpo**; las setas impiden que resbale hacia atrás. Anímalo como una onda de **estirar-anclar** que viaja por segmentos; el truco es el anclaje (sin él, resbala como gelatina). Orugas: similar pero con prolegs que agarran.
- **Tentáculos / trompas / colas prensiles**: misma familia — spline IK + spring para el sobre-movimiento. No hay gait; hay ola + overlap.

---

## 9. Nado y peces

Verificado contra *Fish locomotion* (Wikipedia). Dos familias según qué genera el empuje:

- **BCF (body-caudal fin)** — la mayoría: el empuje sale de una **onda que recorre el cuerpo hasta la aleta caudal (cola)**. La aleta caudal "provides raw power for propelling the fish forward".
- **MPF (median-paired fin)** — pez caja, caballito, mantarraya: usa aletas pectorales/medianas para nadar; **lento pero muy maniobrable**.

**Modos BCF** ordenados por cuánta parte del cuerpo ondula (de todo → solo la cola):

| Modo | Ejemplo | Cuánto ondula | Firma |
|---|---|---|---|
| **Anguilliform** | Anguila | **Todo el cuerpo**, amplitud casi constante de cabeza a cola | Ola serpentina completa (idéntico a §8) |
| **Subcarangiform** | Trucha | Mitad trasera hace la mayoría del trabajo | Ola creciente hacia atrás |
| **Carangiform** | Jurel | Solo el **tercio trasero** + cola oscilan rápido | Cuerpo rígido delante, cola veloz |
| **Thunniform** | Atún | **Casi solo la cola** (crescent), cuerpo casi rígido | Alta velocidad de crucero |
| **Ostraciiform** | Pez caja | **Sin onda de cuerpo**, solo la cola oscila | Cuerpo tieso, cola tipo remo |

- **Reparto de aletas** (verificado): caudal = potencia; **pectorales = pivotes** para girar rápido; **dorsal y anal = anti-guiñada/balanceo** (estabilizan yaw/roll). Un pez que solo mueve la cola y tiene las demás aletas clavadas se ve muerto — anima micro-ajustes de pectorales/dorsal aunque nade recto.
- **La onda del cuerpo viaja hacia atrás más rápido que el pez avanza** (empuja el agua hacia atrás → reacción hacia delante). Amplitud creciente hacia la cola.
- **Producción**: igual que la serpiente, **procedural** (onda seno por la cadena de columna) para el crucero; keyframe para gestos hero (ataque, giro brusco, salto fuera del agua). El empuje NO es constante: acelera en la fase de coletazo, desliza entre golpes ([ver: keyframes-curvas], spacing = peso).

---

## 10. Criaturas fantásticas: el criterio de combinar

No existe referencia real de un dragón. Pero **cada parte SÍ tiene análogo real** — el trabajo es descomponer y aplicar a cada parte su regla, luego coserlas:

| Parte del dragón | Análogo real | Regla aplicada |
|---|---|---|
| Cuerpo/patas en tierra | Cuadrúpedo graviportal (pesado) o terópodo bípedo | Gait lento pesado (§3, §5); si es enorme, columna-pata vertical |
| Alas | Murciélago (membrana entre dedos), no ave | Aleteo down/up + membrana que se deforma con los dedos (§6) |
| Cola | Serpiente + spring | Ola/overlap + spring bones (§8, [ver: movimiento-secundario]) |
| Cuello largo | Serpiente/cisne | Spline IK, ola suave, contrapeso de las alas |
| Aliento/ataque | — (gameplay) | Anticipación→acción→recovery ([ver: animacion-combate]) |

- **El problema del peso volador**: una criatura del tamaño de un dragón NO podría volar de verdad. Se **finge** con alas desproporcionadamente grandes, aleteos **lentos y profundos** (lento lee pesado), y batidos "trabajados" (esfuerzo visible). Un aleteo rápido y ligero hace ver la criatura pequeña. El timing es la perilla del tamaño percibido.
- **Coherencia de peso entre modos**: si el dragón camina pesado (graviportal) pero vuela como una golondrina, se rompe. El mismo "peso" debe leerse en tierra y en aire — aleteos lentos, giros amplios, inercia.
- **Multi-cabeza / multi-miembro (hidra, kraken)**: cada cabeza/tentáculo es una cadena procedural (spline IK + noise de fase distinta por cadena) para que no se muevan en sincronía robótica — desfasa la fase igual que los idles de NPCs ([ver: ciclos-locomocion §4]).
- **Regla**: nunca inventes una locomoción "porque es fantástico". Fantástico = **combinación novedosa de mecánicas reales**, no física imposible sin criterio. La credibilidad viene de que cada parte obedece a un animal que el ojo reconoce.

---

## 11. Procedural vs keyframe vs mocap para criaturas

| Enfoque | Cuándo para criaturas | Límite |
|---|---|---|
| **Keyframe (a mano, desde video ref)** | El grueso del trabajo hero: gaits de cuadrúpedo, aleteos, ataques, gestos. La animación de criatura es **abrumadoramente keyframe** | Caro; exige referencia real (§12) |
| **Procedural / IK** | Multi-pata (arañas, ciempiés), colas/cuellos/tentáculos (spline IK + seno), foot placement en terreno irregular, ondulación de peces/serpientes, undulación repetitiva | No da "actuación"; da movimiento base repetitivo |
| **Simulación / spring** | Lo que CUELGA: colas, orejas, membranas, papada, plumas secundarias ([ver: movimiento-secundario]) | Cosmético, nunca autoritativo en red |
| **Mocap** | **Escaso y caro para animales.** No puedes dirigir a un león; el mocap de caballo existe pero es limitado y requiere animal entrenado + setup especial | La razón nº1 por la que criaturas ≈ keyframe |

- **Por qué poco mocap de animales**: no se le pone un traje a un dragón, y un animal real no actúa a demanda ni hace la acción de gameplay que necesitas. El catálogo de mocap animal es una fracción minúscula del humano ([ver: mocap-librerias]). Resultado práctico: para criaturas, **keyframe desde video de referencia** es el default, con procedural para lo repetitivo.
- **Híbrido típico**: gait base keyframe (o procedural para muchas patas) + IK de contacto de pies en runtime + spring en la cola. El motor blendea gaits por velocidad (walk→trot→canter→gallop) en un blend tree 1D exactamente como el bípedo, con thresholds MEDIDOS del avance real de cada clip ([ver: capas-estados], [ver: ciclos-locomocion §8]).
- **IA text-to-motion**: prácticamente todo entrenado en humanos; para cuadrúpedos/criaturas es aún greybox, no hero (estado 2026, [ver: mocap-librerias]).

---

## 12. Referencia de video: por qué es innegociable

La locomoción animal es **contraintuitiva y nadie la recuerda bien**. Es el caso más fuerte de "reference video imprescindible" de toda la base ([ver: principios-produccion §8 sobre exageración calibrada a lo real]):

- **Muybridge zanjó el galope en 1878** (verificado, *Eadweard Muybridge*, Wikipedia): con 12 cámaras disparadas por cables al paso de la yegua *Sallie Gardner*, demostró que el caballo al galope tiene **las 4 patas en el aire** — pero **cuando están recogidas bajo el cuerpo**, no estiradas adelante-atrás como pintaban TODOS los artistas antes. *Animal Locomotion* (1887): 781 láminas, ~20.000 fotos de decenas de animales. Sigue siendo referencia de animadores desde entonces.
- **Lección operativa**: sin referencia, casi seguro pondrás mal el orden de pisada (¿sabías de memoria que el walk es LH-LF-RH-RF lateral?), el número de suspensiones del galope, o el pliegue del ala en el upstroke. Consigue **cámara lenta** del animal análogo ANTES de bloquear.
- **Exagera desde la cámara de gameplay**, no desde la ref cruda: el video da el timing y la secuencia correctos; el peso y la lectura se empujan para la distancia del juego ([ver: principios-produccion §8]).

---

## Reglas prácticas

1. **Descompón la criatura** en patrones reales (cuadrúpedo/ave/insecto/serpiente/pez) ANTES de poner un key; anima cada parte con su regla y cóselas (§1, §10).
2. **Consigue video de referencia del animal análogo** — es innegociable; la locomoción animal es contraintuitiva (§12).
3. Cuadrúpedo en Unity = **Generic con Root Node**, nunca Humanoid; sus clips no retargetean a otra especie (§2).
4. Pata **delantera ≠ trasera**: distinta anatomía y distinto rol (trasera empuja, delantera recibe con escápula flotante). No las espejes (§2, §4).
5. Elige el **gait por velocidad** y conoce sus beats: walk 4 (lateral LH-LF-RH-RF), trot 2 (diagonal), canter 3, gallop 4 con **suspensión de 4 patas al aire recogidas** (§3).
6. Construye el ciclo cuadrúpedo como **4 patas desfasadas** en tiempo normalizado (walk ≈ 0/0.25/0.5/0.75); mismos contactos normalizados en todos los clips del blend o patina (§4).
7. **Duty factor**: >50% = camina (siempre apoyo), <50% = corre (suspensión). Es la línea walk/trot vs canter/gallop (§3).
8. Depredadores rápidos (felino/cánido) al galope: **doble suspensión** (extendida + recogida). Caballo: una sola (§3).
9. Bestia colosal = **graviportal**: patas verticales, poco rebote, hundimiento profundo, lento. El peso se vende con lentitud + inercia (§5).
10. Ave: **downstroke = ala extendida (power)**, **upstroke = ala plegada hacia dentro (recovery)**; la punta traza un **ocho**; ángulo de ataque nunca constante (§6).
11. Aterrizaje de ave = **flare** (endereza, ángulo alto, todo desplegado, patas adelante, álula arriba); despegue = salto + aleteos profundos (§6).
12. Insecto que camina = **tripod gait** (2 trípodes alternos, siempre 3 patas al suelo). Ciempiés = ola metacrónica procedural (§7).
13. **NO keyframees el ala de un insecto golpe a golpe** (>1000 Hz en músculo asíncrono): ciclo cortísimo en loop + blur/borrón (§7).
14. Serpiente/pez/gusano = **onda sinusoidal procedural** (seno por la cadena de columna, amplitud creciente hacia la cola, velocidad de onda > avance); spline IK + driver, no a mano (§8, §9).
15. Gusano: la clave es el **anclaje** (setas) entre las olas de estirar-contraer; sin él resbala como gelatina (§8).
16. Pez: la **caudal es potencia, pectorales pivotan, dorsal/anal estabilizan**; mueve micro-aletas aunque nade recto (§9). Empuje no constante: coletazo acelera, desliza entre golpes.
17. Colas/cuellos/tentáculos = **spline IK + spring/overlap** (2–4 frames por eslabón); desfasa la fase entre cadenas múltiples (§8, §10).
18. Criatura voladora enorme: **finge el vuelo** con alas grandes y aleteos **lentos y profundos** — el timing lento = tamaño y peso percibidos (§10).
19. Criaturas = **keyframe desde ref** por defecto (mocap animal es escaso/caro); procedural para lo multi-pata/repetitivo; spring para lo que cuelga (§11).
20. **Foot IK en las 4+ patas** para plantar contactos y adaptar a terreno; en Unity, paquete Animation Rigging (§5).

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Tratar al cuadrúpedo como bípedo con 2 brazos abajo | Delantera y trasera son rigs distintos; la "rodilla hacia atrás" es el talón/hock elevado, no una rodilla invertida (§2) |
| Meter el cuadrúpedo como Humanoid en Unity | Generic + Root Node; Humanoid es solo esqueleto humano de ~15 huesos (§2) |
| Galope con las patas estiradas adelante-atrás (caballito de carrusel) | Suspensión con las patas **recogidas bajo el cuerpo** (Muybridge); ese fue el error histórico (§3, §12) |
| Orden de pisada del walk inventado | Secuencia lateral LH→LF→RH→RF, contactos ≈ 0/0.25/0.5/0.75 (§3, §4) |
| Cuadrúpedo que "flota" | Cuello/cabeza bob sincronizado al gait + escápula flotante que absorbe cada delantera + hundimiento de peso (§4, §5) |
| Clips de gait que patinan al mezclar | Contactos en el mismo tiempo normalizado en todos los clips del blend; thresholds medidos del avance real (§4) |
| Ala de ave que sube y baja plana como tabla | Downstroke extendido / upstroke plegado; ángulo de ataque variable; punta en ocho (§6) |
| Ave que aterriza sin frenar (la atraviesa el suelo) | Flare: ángulo alto, todo desplegado, patas adelante, álula (§6) |
| Keyframear el ala de mosca/abeja golpe a golpe | Demasiado rápida (>1000 Hz): loop cortísimo + blur (§7) |
| Ciempiés animado pata por pata a mano | Ola metacrónica procedural (seno con offset de fase creciente) (§7) |
| Serpiente/pez que patina de lado o va a velocidad constante | Onda que sigue su propia estela + amplitud creciente a la cola + empuje pulsado (spacing = peso) (§8, §9) |
| Gusano que resbala como gelatina | Modelar el anclaje (setas) entre olas de contracción (§8) |
| Pez con solo la cola moviéndose y todo lo demás clavado | Micro-ajustes de pectorales/dorsal aunque nade recto (§9) |
| Dragón que camina pesado pero vuela ligero (incoherente) | Mismo peso en tierra y aire: aleteos lentos, giros amplios, inercia (§10) |
| Multi-cabeza/tentáculos moviéndose en sincronía robótica | Fase distinta por cadena (offset), como los idles de NPCs (§10) |
| Esperar mocap de la criatura | Casi no existe mocap animal útil; keyframe desde video ref es el default (§11) |
| Animar de memoria sin referencia | La locomoción animal es contraintuitiva; cámara lenta del animal real ANTES de bloquear (§12) |

## Fuentes

**Bases de El Estudio sintetizadas (referenciadas, no repetidas):**
- [ver: ciclos-locomocion] — el ciclo bípedo (4 poses, cierre de loop, foot sliding, blend por velocidad, root motion). Este archivo hereda toda esa mecánica y la extiende a N patas / alas / ondulación.
- [ver: principios-produccion] — 12 principios, timing/spacing como peso, exageración calibrada a la cámara, referencia. Se cruza (§12), no se repite.
- [ver: rigging/esqueletos-armature] — huesos/roll/naming/Root/Generic vs Humanoid. La estructura del rig de cada criatura se apoya aquí.
- [ver: rigging/ik-fk-constraints] — foot IK, spline IK, pole targets: el motor procedural de patas múltiples, colas y ondulación.
- [ver: movimiento-secundario] — spring bones y overlap para colas, orejas, membranas, plumas.
- [ver: mocap-librerias] — por qué el mocap animal es escaso; keyframe desde ref como default.
- [ver: capas-estados] · [ver: unity/animacion-unity] — blend tree por gait, Generic root motion, paquete Animation Rigging. [ver: rigging/deformacion] · [ver: rigging/rigify] — membranas de ala/aleta, metarig de cuadrúpedo. [ver: animacion-combate] · [ver: keyframes-curvas] — ataques de criatura y curvas/Noise para ondas.

**Fuentes web (WebFetch verificado, jul-2026):**
- **Horse gait** — Wikipedia (`en.wikipedia.org/wiki/Horse_gait`) — walk 4-beat lateral (LH-LF-RH-RF, 2–3 pies al suelo, sin suspensión); trot 2-beat diagonal **SIN fase de suspensión real** (la fuente es explícita: el rebote entre beats "no es una verdadera suspensión" — el trote extendido/de carrera SÍ tiene fase aérea según biomecánica equina general, pero eso no viene de esta fuente, ver §3); pace 2-beat lateral; canter 3-beat con suspensión; gallop hasta 4-beat con **momento de las 4 patas en el aire**; el par diagonal del canter se rompe en el galope.
- **Gait** — Wikipedia (`en.wikipedia.org/wiki/Gait`) — duty factor >50% = walk, <50% = run; gaits simétricos vs asimétricos ("leaping gaits" con fase suspendida); secuencia por velocidad walk→run→gallop; modelo pendular (walk) vs spring-mass (run).
- **Bird flight** — Wikipedia (`en.wikipedia.org/wiki/Bird_flight`) — downstroke genera lift/empuje con ala extendida; upstroke pliega el ala hacia dentro para reducir coste; ángulo de ataque continuo dentro del aleteo y con la velocidad; punta en figura de ocho; colibrí en hover con 8 simétrico y lift en ambos golpes; primarias (mano) vs secundarias (ulna).
- **Insect flight** — Wikipedia (`en.wikipedia.org/wiki/Insect_flight`) — músculo directo vs indirecto; frecuencias de aleteo (libélula ~38 Hz, avispón 100 Hz, asíncrono **>1000 Hz**); dos medios golpes con flips de supinación/pronación; clap-and-fling (Weis-Fogh) en insectos diminutos.
- **Undulatory locomotion** — Wikipedia (`en.wikipedia.org/wiki/Undulatory_locomotion`) — onda rostral→caudal que viaja por el cuerpo; los 5 modos de serpiente (lateral undulation, sidewinding [menor coste], concertina [mayor coste], rectilinear, slide-pushing); cada punto sigue la trayectoria de la cabeza; amplitud creciente hacia la cola.
- **Fish locomotion** — Wikipedia (`en.wikipedia.org/wiki/Fish_locomotion`) — BCF vs MPF; los 5 modos BCF (anguilliform→subcarangiform→carangiform→thunniform→ostraciiform) por cuánto ondula el cuerpo; caudal = potencia, pectorales = pivotes, dorsal/anal = anti-yaw/roll.
- **Earthworm** — Wikipedia (`en.wikipedia.org/wiki/Earthworm`) — peristalsis: circular (alarga) vs longitudinal (acorta y ancla); setas como anclas que evitan el resbalón; ola de contracción que recorre el cuerpo; mucus lubricante.
- **Eadweard Muybridge** — Wikipedia (`en.wikipedia.org/wiki/Eadweard_Muybridge`) — 1878, 12 cámaras, yegua *Sallie Gardner*: el galope tiene las 4 patas al aire **recogidas bajo el cuerpo**, no estiradas; *Animal Locomotion* (1887), 781 láminas; referencia de animadores desde entonces.

**Verificado parcialmente / NO re-verificado esta sesión (tratar con cautela):**
- **Tripod gait** confirmado en *Hexapod (robotics)* (Wikipedia): "3 legs on the ground at a time". **Wave y ripple gait** (patrón metacrónico) son conceptos estándar de biomecánica/robótica de hexápodos que NO se pudieron extraer de fuente primaria esta sesión (la página de robótica no los detalla) — trátalos como convención documentada, confirmar en fuente entomológica/robótica antes de citar cifras finas.
- **Gallop rotario vs transverso** y **doble suspensión en felinos/cánidos**: biomecánica ampliamente documentada, citada a nivel concepto (no re-verificada contra fuente primaria esta sesión).
- **Unity Animation Rigging** (paquete de constraints/IK runtime) y **Rigify metarig de cuadrúpedo**: existen; versión exacta y nombres de módulos NO re-verificados esta sesión — confirmar en la UI/docs antes de afirmar detalles finos.

*Gaps / a verificar en la próxima pasada: (1) fuente primaria para wave/ripple gait con % de patas y velocidades relativas; (2) el offset de fase exacto del canter/gallop varía por animal y "lead" — los números de §4 son convención, medir contra ref; (3) dirección exacta de la onda peristáltica del gusano (retrógrada vs directa) por especie; (4) versión y nombres actuales del Rigify quadruped metarig en Blender 5.2 y del paquete Animation Rigging en Unity 6; (5) suspensión del trote — *Horse gait* niega suspensión real en el trote básico, pero el trote extendido/de carrera (flying trot, Standardbred) clásicamente sí tiene fase aérea; falta fuente biomecánica primaria que lo cierre (§3, corregido esta pasada de "hecho" a "disputado").*
