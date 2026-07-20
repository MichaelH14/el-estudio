# Principios de animación a nivel producción 3D

> **Cuando cargar este archivo:** al DIRIGIR o EJECUTAR animación 3D de personaje para un juego — cuando hay que decidir cómo posar, cómo distribuir frames, cómo hacer que una acción se lea, o por qué un clip técnicamente correcto se siente muerto/flotante. Es el marco de EJECUCIÓN del animador (poses, breakdowns, spacing, arcos, silueta). El uso de estos principios ORIENTADO A GAME-FEEL (timing como responsividad, anticipación como telegraphing) ya está en [ver: gamedev/animacion] y [ver: gamedev/game-feel] — aquí NO se repite, se cruza. La ejecución concreta en Blender (Action editor, NLA, graph editor, export) es la fase siguiente y aún no existe: no la referencies.

Frontera de este archivo: principios y técnica de animación 3D **agnósticos de herramienta**. Los ciclos de locomoción, el combate, las curvas/graph editor, el mocap/librerías, lo facial, las capas/estados y el movimiento secundario tienen archivo propio en `animacion3d/` — este es el tronco conceptual del que cuelgan. El consumo en Unity (Animator, blend trees, root motion) está en [ver: unity/animacion-unity]; el puente rig→Unity (Humanoid/retargeting) en [ver: rigging/rig-a-unity].

---

## 1. La restricción que lo cambia todo: cine vs juego

Un animador de cine controla la cámara, el tiempo y la lectura: compone UNA toma que se ve UNA vez desde UN ángulo. Un animador de juego entrega un **clip que el motor reproduce**, no una toma. Esa diferencia reescribe cómo se ejecuta cada principio. Todo lo demás en este archivo se deriva de esta tabla.

| Dimensión | Cine (cámara fija, lineal) | Juego (clip en un motor) | Consecuencia para el animador |
|---|---|---|---|
| **Cámara** | El animador la elige; posa para UN ángulo | El jugador la controla; la pose se ve desde cualquier lado | Silueta legible en **360°**, no un hero-shot. Nada de "se ve bien solo de frente" |
| **Duración** | Libre; la toma dura lo que deba | Ciclos loopables + acciones de duración fija que blendean | Primer y último frame de un ciclo deben **casar** (§9); nada de resolver una acción "cuando termine el plano" |
| **Reproducción** | Una vez, de principio a fin | En loop, interrumpida, mezclada con vecinos, a velocidad variable | Poses de contacto/paso alineadas en el mismo tiempo normalizado entre clips o el blend **patina** [ver: unity/animacion-unity] |
| **Control** | Cero; es una película | El input entra a mitad de la animación | El peso va al **final** (follow-through), nunca alargando el arranque [ver: gamedev/animacion] |
| **Continuidad** | El corte es del director | Cualquier frame puede ser el punto de salida a otro estado | Poses "de tránsito" tienen que quedar decentes; evitar frames-basura entre extremos |
| **Rig / proporciones** | Un personaje, un rig | El mismo clip se retargetea a rigs de proporciones distintas (Humanoid) | Autorar en **muscle space** / Humanoid; no clavar poses a distancias absolutas del mundo [ver: rigging/rig-a-unity] |
| **Presupuesto** | Se pule hasta que quede | Cientos de clips; el pulido se reparte | Pose-to-pose (§3): bloquear todo antes de pulir nada; iterar sin terminar |

**Regla madre:** en juego no animas una actuación, animas un **ladrillo de un sistema** (state machine + blend tree). El ladrillo tiene que encajar con sus vecinos por los cuatro costados. Belleza que no encaja se descarta.

---

## 2. Los 12 principios en la silla del animador (ejecución 3D)

Los 12 principios de Thomas & Johnston (*The Illusion of Life*, 1981) y su lectura de juego ya están tabulados en [ver: gamedev/animacion]. Aquí la columna que falta: **qué toca el animador en la escena 3D** para ejecutarlos. No repetir la orientación game-feel; esto es mecánica de producción.

| Principio | Ejecución concreta en 3D (qué HACE el animador) |
|---|---|
| **Timing** | Elige el número de frames de cada tramo = velocidad = peso/fuerza. Es una decisión de tabla, no de curva → §4 |
| **Spacing** (slow in/out) | Distribuye DÓNDE caen los frames intermedios (juntos = lento, separados = rápido). Se ejecuta con spacing charts + tangentes del graph editor [ver: keyframes-curvas], no solo contando frames → §4 |
| **Pose to pose / Straight ahead** | Método de trabajo: bloquear extremos vs animar frame a frame. En 3D casi siempre pose-to-pose → §3 |
| **Anticipación** | Key de preparación con el centro de masa (COG) desplazado en dirección OPUESTA a la acción; contra-movimiento antes del golpe → §6 |
| **Follow-through & overlap** | *Successive breaking of joints*: la cadena no llega a la vez. Retrasa 2–4 frames los huesos hijos respecto al padre (cadera→pecho→hombro→codo→muñeca→dedos). El "drag" se hornea en poses o se deja a springs [ver: movimiento-secundario] |
| **Squash & stretch** | En 3D del juego casi nunca se escalan huesos (coste; muchos motores no lo soportan bien, [ver: gamedev/animacion]). Se finge con **rotación/compresión de la cadena**: columna que se comba, rodillas que flexan en el impacto, extremidad que se extiende en el frame veloz. Volumen constante conceptual. Facial: blendshapes [ver: rigging/deformacion] |
| **Arcos** | Verifica que CADA control describe un arco limpio; los revela el graph editor / editor de trayectoria → §7 |
| **Secondary action** | Capa que suma sin competir con la acción principal (respiración, mirada, gesto de mano). En juego se hace con **additive layers** enmascaradas, no duplicando clips [ver: capas-estados] |
| **Exageración** | Empuja poses más allá del natural para que lean a la distancia y ángulo del juego → §8 |
| **Solid drawing / posing** | Volumen, balance sobre el COG, peso creíble; evitar *twinning* (lados simétricos), buscar contraste y línea de acción → §5 |
| **Staging** | Con cámara libre del jugador se traduce en **claridad de silueta omnidireccional** e intención legible; en gameplay parte del staging es level design [ver: gamedev/level-design] |
| **Appeal** | Silueta reconocible = personaje/ataque reconocible; también en enemigos (cada ataque, una silueta distinta) [ver: animacion-combate] |

---

## 3. El pipeline pose-to-pose en 3D: blocking → breakdown → spline → polish

En 3D casi todo se anima **pose-to-pose**: pones las poses clave primero y el resto se rellena. Es lo correcto para juego porque permite **iterar sin terminar** (todo puede cambiar en desarrollo) y porque los blends/loops necesitan extremos limpios y controlados. El *straight-ahead* (frame a frame, sin plan) queda para tramos caóticos e impredecibles: pelo suelto, tela, fuego, un efecto orgánico, un latigazo secundario — y hoy eso suele resolverse con simulación/springs, no a mano.

Las cuatro pasadas estándar de producción 3D:

| Pasada | Qué se hace | Modo de tangentes | Criterio de "listo" |
|---|---|---|---|
| **1. Blocking** | Solo las **poses clave** (extremos). Se trabaja en **stepped/constant** (sin interpolar) para juzgar timing y poses sin que las curvas mientan | Stepped/Hold | Cada pose fuerte y legible; el timing entre extremos ya cuenta la acción |
| **2. Breakdowns** | Poses **intermedias** que definen el CAMINO entre extremos (no el punto medio automático): arcos, overlap, favoring | Stepped todavía | La trayectoria y el peso ya se leen aun a pasos; sin breakdowns el spline "flota" |
| **3. Spline** | Se pasa a interpolado (spline/Bézier) y se **arreglan las curvas**: eases, arcos, eliminar oscilaciones que mete el interpolador | Spline/Auto→ajustado | Nada patina, sin pops, arcos limpios en el graph editor (§7) |
| **4. Polish** | Overlap fino, moving holds, textura (dedos, mirada, respiración), settle final | Manual | Aguanta cámara cercana y loop; nada muerto |

Conceptos de ejecución dentro del pipeline:

- **Stepped primero, siempre.** Bloquear en interpolado esconde errores de timing: el motor de curvas "rellena bonito" y crees que funciona cuando la pose está mal. Juzga poses y timing en stepped; solo entonces splinea.
- **El breakdown no es el punto medio.** Es donde tú decides que esté, *favoreciendo* (favoring) hacia una de las poses para controlar el ease y el overlap. Un breakdown a mitad exacta da movimiento robótico; corrido hacia el extremo final da peso y anticipación.
- **Successive breaking (el látigo).** En una acción con fuerza, las poses de breakdown rompen la cadena en orden: primero se mueve la cadera, luego el pecho arrastra, luego el brazo, y la mano/arma llega tarde. Eso es overlap ejecutado a mano en las poses, no solo con springs.
- **Iterar barato.** Como el juego cambia (diseño toca el timing, el combate cambia la ventana de cancel), quedarse en blocking/breakdown el mayor tiempo posible: repulir spline es caro, rebloquear es barato.

---

## 4. Timing y spacing: el corazón del peso y la fuerza

Son **dos cosas distintas** y confundirlas es la causa #1 de animación 3D "flotante". (Distinción canónica de Richard Williams, *The Animator's Survival Kit*.)

| | **Timing** | **Spacing** |
|---|---|---|
| Qué es | CUÁNTOS frames dura un tramo | CÓMO se distribuyen los frames dentro del tramo |
| Controla | La velocidad global y el peso/masa | La aceleración: el ease-in/ease-out, el "snap" |
| Se ejecuta con | La tabla de frames (dónde caen los extremos) | El spacing chart y las **tangentes** del graph editor [ver: keyframes-curvas] |
| Si está mal | Todo va demasiado rápido/lento | Todo va "a velocidad constante" = muerto, robótico, sin peso |

**El peso vive en el spacing, no en el timing.** Dos animaciones con el MISMO número de frames se sienten una ligera y otra pesada según cómo estén espaciados los intermedios. Reglas de ejecución:

- **Objeto pesado** → arranca lento (frames muy juntos al inicio: cuesta moverlo), acelera, y **frena largo** (muchos frames para asentar). Poco o ningún snap.
- **Objeto ligero / golpe rápido** → poquísimos frames en la acción (spacing amplio = velocidad), y **holds** largos antes y después. El impacto es casi instantáneo.
- **Fuerza = contraste de spacing.** Un puñetazo con fuerza tiene la anticipación espaciada lento, la acción en 1–2 frames con spacing enorme (casi teleport), y el follow-through frenando. Spacing uniforme mata la fuerza.

Spacing chart (herramienta mental de ejecución; la distribución de los intermedios entre dos extremos A y B):

```
LENTO al entrar, RÁPIDO al medio, LENTO al salir (ease both):
A · ·  ·   ·    ·   ·  · · B      ← frames juntos en A y B, separados en medio

GOLPE (arranque suave, salida explosiva):
A ·  ·   ·    ·      ·          B  ← se abre hacia B: acelera y NO frena
```

- **Holds vivos (moving holds).** Un hold congelado en 3D se ve MUERTO (peor que en 2D, porque el ojo espera micro-movimiento en un modelo realista). Un hold de producción **deriva ligeramente**: la pose sigue asentándose 2–3 unidades, sigue respirando. Nunca dos keys idénticas seguidas sin deriva.
- **Timing sobre frame count** (regla compartida con [ver: gamedev/animacion]): 4 poses con holds bien elegidos leen mejor que 12 frames uniformes. El frame count es piso, no calidad.
- Cuidado en juego: el spacing lo puede pisar el motor. Si el clip corre a velocidad variable (blend tree por `speed`) o con `Time.timeScale`, tu ease-in cuidado se estira. Autora el spacing para la velocidad NOMINAL del clip y deja que locomoción module con blend, no reanimando.

---

## 5. Poses fuertes, silueta legible y línea de acción

La pose es la unidad de valor: en pose-to-pose, si las poses clave son fuertes, la animación ya funciona antes de splinear. Ejecución del posing sólido:

| Herramienta de pose | Cómo se ejecuta | Test |
|---|---|---|
| **Línea de acción** | Una sola curva (C o S) que recorre el cuerpo de cabeza a pie define la energía de la pose. Posa la columna a esa línea PRIMERO, los miembros después | ¿Puedes trazar una línea limpia sobre la pose? Si son varias líneas peleando, la pose está confusa |
| **Silueta** | La pose se lee en **negro plano**, sin detalle interno. Separa miembros del torso, mano fuera de la cadera, arma fuera del cuerpo | Rellena la pose de negro (o mira contraluz): ¿se entiende la acción? En juego, desde **varios ángulos** |
| **Contraste / anti-twinning** | Evita *twinning* (los dos brazos/piernas haciendo lo mismo simétrico = robótico, aburrido). Rompe la simetría: un lado adelantado, cadera y hombros en ejes opuestos | ¿Los dos lados hacen lo mismo? Rómpelo |
| **Line of action + hips/shoulders opuestos** | El eje de caderas y el de hombros inclinados en sentidos contrarios (contrapposto) = peso y vida. Paralelos = maniquí | Mira caderas y hombros: ¿planos y paralelos? Inclínalos |
| **Balance / centro de masa** | El COG cae sobre la base de apoyo (o fuera, a propósito, si está cayendo/lanzándose). Un rig posa creíble cuando el peso está resuelto | ¿Se caería el personaje? Si no es intencional, corrige el COG |
| **Negative space** | El hueco ENTRE miembros y torso también comunica. Huecos claros = pose legible | ¿Los huecos son formas limpias o papilla? |

- **Definición canónica (Thomas & Johnston):** *solid drawing* = entender las formas en espacio 3D, darles volumen y peso; *staging* = presentar la idea de forma completa e inequívocamente clara. En 3D del juego, "inequívocamente clara" implica **desde el ángulo del jugador, no del animador**.
- **Appeal ≠ bonito.** Es claridad de intención y silueta reconocible. Un enemigo con appeal tiene una silueta de ataque que el jugador aprende [ver: animacion-combate].
- La silueta también depende de la **topología y el volumen del modelo**: si la malla colapsa al posar, ninguna pose fuerte se salva [ver: rigging/deformacion] [ver: modelado/topologia].

---

## 6. Anticipación → acción → follow-through, ejecutado frame a frame

Toda acción con fuerza tiene tres tiempos. En [ver: gamedev/animacion] están como diseño de combate (wind-up/active/recovery, con números de juegos reales). Aquí, cómo el animador **ejecuta las poses** de esos tres tiempos. Ejemplo de trabajo: **mandoble descendente a dos manos**, plantilla ilustrativa de autoría a 30 fps (NO medida de un juego shipeado; los frames exactos se calibran contra el diseño de combate — ver los diales de wind-up/active/recovery en [ver: gamedev/animacion]).

| Tiempo | Poses clave | Ejecución 3D |
|---|---|---|
| **Anticipación** | Contra-pose: arma ARRIBA y ATRÁS, COG desplazado hacia atrás, columna en C invertida a la acción, hombros cargados | Espaciado **lento** (se carga la fuerza). Cuanto más peso quieras vender, más y más lenta la anticipación. En juego del JUGADOR: comprimida a 1–3 frames (el peso va al final), del ENEMIGO: larga = telegraph |
| **Acción** | El golpe: arma abajo, cuerpo volcado hacia delante, línea de acción invertida respecto a la anticipación | 1–2 frames con **spacing enorme** (casi teleport); pose de contacto muy extendida. Un **smear/stretch** por rotación de cadena vende la velocidad sin escalar huesos |
| **Impacto / hold** | Frame de contacto sostenido: máxima extensión, rodillas flexadas absorbiendo | **Hold** breve para que el ojo registre el golpe (hermana visual del hitstop, [ver: gamedev/game-feel]). Silueta del impacto = la más legible del clip |
| **Follow-through** | El arma pasa el punto de impacto y sigue; el cuerpo se recupera; overlap de brazos/tela llegando tarde | Espaciado **frenando** (ease-out largo). AQUÍ va el peso, no en la anticipación. *Successive breaking*: mano y arma se asientan últimas |
| **Settle / recovery** | Vuelta a la guardia con un **overshoot** (pasa la pose de guardia y regresa) + moving hold | Overshoot pequeño = vida; llegar seco a la guardia = robótico. La ventana de cancel/recovery la define diseño [ver: animacion-combate] |

Puntos de ejecución transversales:

- **El COG es el actor principal.** Anima primero la trayectoria del centro de masa (cadera), luego cuelga los miembros. Peso = cómo se mueve el COG, no cómo se mueven las manos.
- **Contra-movimiento obligatorio.** Nada arranca "desde parado" hacia su dirección: primero un micro-movimiento opuesto (anticipación). Sin él, la acción aparece de la nada y se siente ligera.
- **Overshoot en las llegadas.** Miembros y cámara pasan su destino y vuelven. Es follow-through ejecutado con curvas [ver: keyframes-curvas].

---

## 7. Arcos en 3D y cómo el graph editor los revela

Casi toda acción natural sigue un **arco**; el movimiento en línea recta se ve mecánico (excepto lo mecánico de verdad). En 3D los arcos que a mano parecen bien se **rompen al interpolar** — el interpolador spline mete rectas y sobre-oscilaciones que el ojo lee como "flotante" o "resbaloso". Detectarlos y arreglarlos es trabajo de graph editor / editor de trayectoria. Detalle de curvas y tangentes: [ver: keyframes-curvas].

| Síntoma | Qué pasa en las curvas | Fix de ejecución |
|---|---|---|
| Mano/pie "flota" o va en línea recta | Trayectoria world del control es recta o quebrada | Añadir/mover un **breakdown** que empuje el path a un arco; revisar en el editor de trayectoria (motion path) |
| "Patina" / foot sliding | El pie de apoyo se desliza en world durante el contacto | Clavar el pie: pos constante durante el apoyo (o IK); en juego, sincronizar la fase del pie entre clips del blend [ver: ciclos-locomocion] |
| Oscilación rara tras un key | Tangentes auto/spline generan overshoot no deseado | Aplanar la tangente en el extremo o pasar a tangente lineal/manual en ese tramo |
| Pop en el loop | Primer y último key no casan en valor Y tangente | Copiar el primer key al último e igualar tangentes; usar Loop Pose/Loop Match del motor [ver: unity/animacion-unity] |
| Movimiento robótico | Todas las tangentes en lineal/constante uniforme | Ease-in/out con tangentes; romper la uniformidad |

- **Arcos rotos a propósito.** El mocap muestra que romper un arco añade realismo: la cabeza gira BRUSCA tras un puñetazo, no en curva suave (dato de [ver: gamedev/animacion]). Es una decisión, no un accidente del interpolador.
- **Menos keys, mejores arcos.** Un control con demasiados keys es imposible de curvar limpio. Poses fuertes + interpolación (la lección de la animación procedural de Rosen, [ver: gamedev/animacion]) también aplica al keyframe a mano: pocas poses buenas splinean mejor que muchas mediocres.
- **Curvas de escala son caras en runtime** [ver: unity/animacion-unity] y [ver: unity/rendimiento-unity]; una razón más para fingir squash & stretch con rotación de cadena, no con escala real.

---

## 8. Exageración para la distancia de lectura del juego

"Real life never looks real enough" ([ver: gamedev/animacion]). En cámara de juego —lejana, en movimiento, con acción rápida y a veces docenas de personajes— una animación "correcta y natural" **se pierde**. El animador de producción exagera deliberadamente para que la acción lea a la distancia y el ángulo reales.

| Qué exagerar | Cómo | Por qué en juego |
|---|---|---|
| **Poses** | Empujar la línea de acción, extender más los miembros en los extremos, más contraste hombros/caderas | A distancia, una pose tímida no se distingue de un idle |
| **Timing/spacing** | Snap más agresivo hacia el active, holds más marcados | Con cámara lejana y acción rápida, transiciones suaves se leen como "no pasó nada" |
| **Silueta de ataque** | Cada wind-up con pose ÚNICA y silueta distinta | El jugador elige respuesta leyendo la silueta [ver: animacion-combate] |
| **Reacciones** | Hit reactions más grandes que la vida; knockback claro | Vende que el golpe conectó desde cualquier ángulo [ver: gamedev/game-feel] |

- **Calíbralo a la cámara real.** No exageres mirando la vista del viewport del animador (cercana, de tres cuartos): revisa desde la **cámara de gameplay** (lejana, cenital, sobre el hombro — la que sea). Lo que se ve "demasiado" de cerca suele quedar justo a la distancia de juego.
- **Estilo consistente entre animadores.** La exageración es una perilla de estilo: si un animador exagera al 120% y otro al 80%, el set de clips se siente inconsistente. Definir el nivel de exageración como decisión de dirección de arte [ver: gamedev/arte-direccion], no por gusto individual.
- **El mocap casi nunca exagera solo.** La captura da realismo plano; el valor del animador es empujarla a lectura de juego (§10).

---

## 9. Autorar con la restricción de juego: loops, multi-ángulo, root motion, interrumpible

La sección §1 dio el marco; aquí la ejecución. Un clip de juego se autora contra requisitos que en cine no existen:

### Ciclos loopables
- **Primer frame = último frame** (misma pose y tangentes) o el loop *poppea*. Técnica: animar el ciclo, copiar frame 1 al frame N, ajustar el medio. Detalle de ciclos completos: [ver: ciclos-locomocion].
- **Fase del pie consistente entre clips.** Todos los clips de locomoción que van al mismo blend tree deben pisar en el **mismo tiempo normalizado** (ej. pie izq contacta en 0.0, der en 0.5 en walk, run y sprint) o el blend patina [ver: unity/animacion-unity]. Es una restricción de AUTORÍA, no algo que se arregle después.
- **Moving holds, no holds muertos** (§4): un idle no es una pose congelada; respira y deriva, o el personaje parece un maniquí en pausa.

### Multi-ángulo / omnidireccional
- Silueta legible en 360° (§5). En un juego con cámara libre, una pose que solo funciona de perfil es un bug.
- Sets direccionales: locomoción suele necesitar strafe/backpedal además de forward — 8 direcciones o un blend 2D. Cada dirección es un clip que debe casar con sus vecinos en el blend.

### Interrumpible / blend-friendly
- Cualquier frame puede ser el punto donde el motor corta a otro estado. Evita frames intermedios impresentables; las poses de tránsito deben aguantar ser un punto de salida.
- Transiciones responsivas = permitir input ANTES de que el clip termine (cancels/buffer), no recortar el clip [ver: gamedev/animacion]. El animador entrega el clip COMPLETO; el sistema decide dónde se puede cortar.

### Root motion vs in-place (decisión de autoría)
El desplazamiento puede vivir en la animación (root motion) o en el código (in-place). Se decide y se AUTORA distinto. Settings exactos del motor: [ver: rigging/rig-a-unity] y [ver: unity/animacion-unity].

| | Root motion (el clip mueve al personaje) | In-place (el código mueve; el clip pisa en sitio) |
|---|---|---|
| Autoría | El root/cadera se desplaza en el clip; el pie no patina porque el mundo avanza con él | El personaje corre "en una cinta"; el pie DEBE clavar sin deslizar |
| Bueno para | Ataques con desplazamiento, esquivas, animaciones fieles al mocap, sin foot sliding | Locomoción con velocidad variable por código, blend trees por `speed` |
| Gotcha del animador | El motor separa Root Transform (proyección en Y del COG) del Body; hay que autorar/hornear bien el root (Bake Into Pose de rotación/Y/XZ según el clip: Idles hornean XZ, saltos NO hornean Y) | Sincronizar la velocidad de pie del clip con la velocidad real o patina |

### Retargeting y mocap como materia prima
- En Humanoid, el clip se autora/retargetea en **muscle space** (normalización de rotaciones por músculo, rango por hueso; ej. Head-Nod/Head-Tilt por defecto −40°..40°) y se aplica a rigs de proporciones distintas vía el **Avatar** (requiere T-pose y mapeo de huesos correcto). Esto es lo que permite reusar una librería (Mixamo) en tu personaje [ver: rigging/rig-a-unity] [ver: mocap-librerias].
- **Mixamo** (Adobe, gratis con cuenta): auto-rigger por ML + librería de animaciones de mocap pulidas a keyframe; export FBX con/sin skin. Es punto de partida, no producto final: hay que limpiar, exagerar (§8) y hacer loopable/blend-friendly. (Fuse y Face Plus discontinuados; el auto-rigger y la librería siguen.) Detalle y flujo: [ver: mocap-librerias].
- **Facial**: el estándar de retarget facial de la industria es ARKit (Apple `ARFaceAnchor.BlendShapeLocation`, 52 coeficientes 0.0–1.0) sobre blendshapes. Flujo completo en [ver: animacion-facial].

---

## Reglas practicas

- [ ] Antes de tocar un control, decide si el clip es **loop, acción fija que blendea, o root-motion** — cambia toda la autoría (§1, §9).
- [ ] Bloquea SIEMPRE en **stepped/constant**; juzga poses y timing sin interpolar; splinea solo cuando las poses ya funcionen (§3).
- [ ] Pon las **poses clave fuertes** primero; si el blocking se lee, la animación ya existe. Belleza de spline sobre poses débiles = perder el tiempo.
- [ ] Los **breakdowns** definen el camino (arcos, overlap) y van *favoreciendo* hacia un extremo — nunca a mitad exacta por defecto (§3).
- [ ] Separa **timing** (frames = peso) de **spacing** (distribución = aceleración); el peso vive en el spacing (§4).
- [ ] Anima el **centro de masa (cadera)** primero; cuelga los miembros después. El peso es cómo se mueve el COG.
- [ ] **Successive breaking**: retrasa 2–4 frames los huesos hijos respecto al padre en toda acción con fuerza (§2, §6).
- [ ] Todo arranque lleva **contra-movimiento** (anticipación); el peso del golpe va al **follow-through**, no alargando el startup (§6).
- [ ] **Overshoot** en las llegadas de miembros y cámara; **moving holds** (deriva) en vez de holds congelados (§4, §6).
- [ ] Test de **silueta en negro y en 360°** en cada pose clave; rompe el **twinning** (simetría de lados); inclina caderas y hombros en ejes opuestos (§5).
- [ ] Verifica **arcos** en el editor de trayectoria; arregla foot sliding clavando el pie de apoyo (§7) [ver: keyframes-curvas].
- [ ] **Exagera calibrando desde la cámara de GAMEPLAY**, no desde el viewport cercano del animador (§8).
- [ ] Fija el nivel de exageración como **decisión de dirección**, consistente entre animadores (§8) [ver: gamedev/arte-direccion].
- [ ] Ciclos: **primer frame = último** (valor y tangentes); usa Loop Pose/Loop Match para el pop (§9).
- [ ] Clips de un mismo blend tree: **fase de pie en el mismo tiempo normalizado** o el blend patina (§9) [ver: unity/animacion-unity].
- [ ] **Squash & stretch por rotación/compresión de cadena**, no por escala de hueso (coste runtime + soporte del motor) (§2, §7).
- [ ] Entrega el clip **completo**; deja los cancels/ventanas de interrupción al sistema, no recortes la animación (§9).
- [ ] Autora en **Humanoid/muscle space** para que el clip retargetee; verifica el Avatar (T-pose + mapeo) antes de culpar a la animación (§9) [ver: rigging/rig-a-unity].
- [ ] Trata **Mixamo/mocap como materia prima**: limpiar + exagerar + hacer loopable, nunca shippear crudo (§8, §9) [ver: mocap-librerias].

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Bloquear en interpolado (spline) desde el principio | Stepped/constant siempre en blocking; el spline miente sobre el timing (§3) |
| Confundir timing con spacing → animación "flotante" a velocidad constante | Distinguir: frames = peso (timing), distribución = aceleración (spacing); el peso vive en el spacing (§4) |
| Holds congelados (dos keys idénticas seguidas) | Moving holds: la pose deriva/respira; nunca hold muerto en un modelo 3D (§4) |
| Posar para el viewport del animador (tres cuartos, cerca) | Silueta legible desde la cámara de gameplay y en 360°; revisar en negro (§5, §8) |
| Twinning: los dos lados haciendo lo mismo simétrico | Romper simetría; caderas y hombros en ejes opuestos; contraste (§5) |
| Animar manos/pies y olvidar el centro de masa | Animar el COG (cadera) primero; los miembros cuelgan de él (§6) |
| Meter peso alargando la anticipación del JUGADOR → control gomoso | El peso va al follow-through; startup corto (§6) [ver: gamedev/animacion] |
| Arcos que se rompen al splinear (flota, patina) | Editor de trayectoria: añadir breakdown que fuerce el arco; clavar pie de apoyo (§7) |
| Escalar huesos para squash & stretch | Fingirlo con rotación/compresión de cadena; la escala es cara y mal soportada (§2, §7) |
| Ciclo con pop en el loop | Primer frame = último (valor y tangentes); Loop Pose/Loop Match (§9) |
| Clips de locomoción con fase de pie distinta → blend patina | Sincronizar el tiempo normalizado del contacto entre todos los clips del blend (§9) |
| Autorar poses a distancias absolutas del mundo → no retargetea | Trabajar en Humanoid/muscle space; validar el Avatar (T-pose, mapeo) (§9) |
| Shippear mocap/Mixamo crudo (realista pero plano y sin loop) | Limpiar, exagerar a lectura de juego, hacer loopable/blend-friendly (§8, §9) |
| Root motion mal horneado (Y de un salto horneada, o XZ de un idle sin hornear) | Bake Into Pose por eje según el clip (Idles: XZ; saltos: Y no) (§9) [ver: rigging/rig-a-unity] |
| Pulir a spline un clip que diseño aún va a cambiar | Quedarse en blocking/breakdown mientras el timing de gameplay no esté cerrado (§3) |

## Fuentes

Bases de la propia knowledge sintetizadas (referenciadas, no repetidas):
- **[ver: gamedev/animacion]** — los 12 principios orientados a game-feel (timing/anticipación/follow-through como diseño), anatomía de ataque con números de juegos reales, animación procedural. Este archivo aporta la capa de EJECUCIÓN de animador que aquella cruza pero no desarrolla.
- **[ver: gamedev/game-feel]** — juice, hitstop, screenshake, easing: el polish que amplifica la animación. Aquí se cruza (impacto/hold), no se repite.
- **[ver: unity/animacion-unity]** — consumo en Unity 6: Animator, blend trees (sincronía de fase de pie), root motion, layers/masks. La autoría de este archivo apunta a esas restricciones.

Canon de animación (nivel concepto):
- **The Illusion of Life: Disney Animation** — Frank Thomas & Ollie Johnston (1981), vía *Twelve basic principles of animation* (Wikipedia) — definiciones canónicas de straight-ahead vs pose-to-pose, timing, slow-in/slow-out (spacing), arcos, anticipación, follow-through/overlap, exageración, staging, solid drawing, appeal. Fetch verificado.
- **The Animator's Survival Kit** — Richard Williams — origen de la distinción **timing vs spacing**, los spacing charts, breakdowns favoreciendo, moving holds, successive breaking of joints. Citado a **nivel concepto** (no se fetcheó el libro); las definiciones concretas usadas coinciden con el canon verificado en la fuente Wikipedia anterior y con la práctica estándar de producción 3D.
- **Game Anim: Video Game Animation Explained** / gameanim.com — Jonathan Cooper — sitio y libro de referencia sobre animación de personaje de juego (interactiva, loopable, multidireccional, interrumpible); también publica el AZRI Rig gratuito (100k+ descargas). Homepage fetcheada; el detalle por-principio ya está sintetizado en [ver: gamedev/animacion].

Docs de Unity 6 (Mecanim/Humanoid) — todas fetch verificado 2026-07-20:
- **Retargeting** (`Manual/Retargeting.html`) — el Avatar como interfaz de retarget; requisitos (Humanoid + Avatar + mismo Animator Controller); autoría reusable entre rigs de proporciones distintas.
- **Root Motion / Root Transform** (`Manual/RootMotion.html`) — Body vs Root Transform (proyección en Y del COG); Bake Into Pose de rotación/Y/XZ; Based Upon (Body/Original/Feet/Mass Center); `gravityWeight`; Loop Pose.
- **Configuring the Avatar** (`Manual/ConfiguringtheAvatar.html`) — T-pose obligatoria, huesos mandatorios vs opcionales, indicadores verde/rojo, Enforce T-Pose, por qué un Avatar correcto es base del retargeting.
- **Muscle Definitions / Muscles & Settings** (`Manual/MuscleDefinitions.html`) — muscle space, rango por músculo (ej. Head-Nod/Head-Tilt −40°..40°), Muscle Group Preview, Per-Muscle, Translate DoF.
- **Animation Clips** (`Manual/AnimationClips.html`) — el clip como "unidad de movimiento" (Idle/Walk/Run); propiedades animables.

Librerías / mocap / facial (2026):
- **Mixamo** — vía *Mixamo* (Wikipedia) — auto-rigger por ML + librería de mocap pulida a keyframe, propiedad de Adobe (2015), gratis con cuenta; Fuse y Face Plus discontinuados; auto-rigger y librería vigentes. Fetch verificado.
- **ARKit — ARFaceAnchor.BlendShapeLocation** (Apple) — estándar de facto del retarget facial por blendshapes: 52 coeficientes, rango 0.0–1.0. La página de Apple es una SPA JS y **no se pudo fetchear su cuerpo esta sesión**; el número (52) y el rango son el estándar ARKit ampliamente documentado — el detalle operativo de facial vive en [ver: animacion-facial], que debe verificar la lista completa contra fuente primaria.
