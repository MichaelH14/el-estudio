# Animación por capas y máquina de estados

> **Cuando cargar este archivo:** al planear el GRAFO de animación de un personaje 3D de juego — qué clips existen, cómo se organizan en estados/capas/blend trees, qué blendea contra qué, qué se anima a mano vs qué se resuelve procedural en runtime, y cómo nombrar todo para que el Animator no se vuelva spaghetti. Es la fase de DISEÑO DEL SISTEMA de animación (agnóstico de motor). La CONFIGURACIÓN concreta de esos estados/transiciones/masks/blend trees en Unity está en [ver: unity/animacion-unity]. El CONCEPTO motor-agnóstico ya lo esboza [ver: gamedev/animacion §7] — aquí va la profundidad de producción 3D.

## 0. Qué entrega el animador (y qué no es este archivo)

El animador 3D no entrega "un montón de clips". Entrega **un sistema**: una lista de clips + el grafo que los orquesta + las reglas de mezcla. El motor (Animator de Unity, AnimBP de Unreal, AnimationTree de Godot) es solo el consumidor. Este archivo es cómo se **diseña ese sistema** antes de tocar el Inspector.

| Este archivo SÍ cubre | Va en otro sitio |
|---|---|
| La mentalidad state-machine, qué es un estado/transición/parámetro | Config exacta en Unity → [ver: unity/animacion-unity] |
| Capas additive/override, split cuerpo con masks (concepto + qué clips) | 12 principios, anatomía de ataque → [ver: gamedev/animacion] |
| Blend trees: qué CLIPS necesitas para alimentarlos | Impacto/juice/hitstop → [ver: gamedev/game-feel] |
| Autoral vs procedural/IK en runtime; orden del stack | Autoría fina de curvas/keys → [ver: keyframes-curvas] |
| El set de clips completo de un personaje jugable | Ciclos de locomoción a fondo → [ver: ciclos-locomocion] |
| Naming y organización de clips | Clips de combate a fondo → [ver: animacion-combate] |

---

## 1. Mentalidad state-machine: el modelo que el motor consume

Un personaje jugable NO es una línea de tiempo. Es una **máquina de estados finita**: en cada instante está en exactamente UN estado por capa (idle, o corriendo, o atacando, o cayendo), y cambia de estado por eventos. Todos los motores modernos consumen este modelo; diseñarlo bien es 80% del trabajo.

| Pieza | Qué es | En términos de producción |
|---|---|---|
| **Estado** | Reproduce UN clip o UN blend tree | Cada animación distinguible de gameplay es un estado candidato |
| **Transición** | Arco entre dos estados con condición + blend time | El "cuándo" y el "qué tan suave" del cambio |
| **Parámetro** | Variable que el gameplay escribe y las transiciones/blend trees leen | `Speed` (float), `IsGrounded` (bool), `Attack` (trigger), `MoveX/MoveZ` (float 2D) |
| **Capa (layer)** | Máquina de estados independiente que se mezcla con las demás | Base = cuerpo completo; superior = torso/brazos enmascarado |
| **Blend tree** | Mezcla CONTINUA de clips dentro de un estado (un dial, no un switch) | Locomoción por velocidad/dirección |

Regla mental: **una transición es un SWITCH (cambio discreto en el tiempo); un blend tree es un DIAL (mezcla continua por parámetro)**. Confundirlos es el error de arquitectura #1. Idle↔Attack = transición. Idle→Walk→Run = blend tree 1D (es el mismo "estado lógico" de locomoción, solo cambia la intensidad).

**Estado ≠ un clip por fuerza.** Un estado puede ser un blend tree (locomoción), un solo clip (una animación de recarga), o incluso una sub-máquina completa (todo el combate). El grano correcto: agrupar en un estado lo que el gameplay trata como "una cosa".

---

## 2. Cómo dibujar el grafo (antes de cablear nada)

El grafo se diseña en papel/pizarra ANTES del Inspector. Dos disciplinas:

### 2.1 Sub-máquinas por dominio
Con >15 estados el grafo plano se vuelve inauditable [ver: unity/animacion-unity §10]. Agrupar por dominio en sub-máquinas:

```
[Locomotion]   ← blend tree (idle/walk/run/strafe)
[Airborne]     ← sub-máquina: JumpStart → JumpLoop → Land
[Combat]       ← sub-máquina: Attack1→Attack2→Attack3, Block, Dodge
[Reactions]    ← HitLight, HitHeavy, KnockDown, GetUp, Death
[Interact]     ← Pickup, OpenDoor, Lever
```

Estabilizar los estados (que existan y funcionen aislados) ANTES de cablear transiciones — cablear sobre estados que aún cambian es rehacer el grafo tres veces.

### 2.2 Committed vs interrumpible (decisión de diseño, no técnica)
Cada estado se etiqueta con su **cancelabilidad**. Esto ES game design [ver: gamedev/mecanicas-sistemas], se decide con el diseñador y luego el animador lo respeta con ventanas de cancel marcadas en el clip:

| Clase | Puede interrumpirse por | Ejemplos |
|---|---|---|
| **Fully interruptible** | Casi cualquier cosa | Idle, locomoción |
| **Committed con ventana** | Solo tras un frame concreto (cancel window) | Ataques encadenables, dash |
| **Committed total** | Nada hasta terminar | Animaciones de ejecución, cutscene-lock, muerte |
| **Prioritario** | Interrumpe a casi todo | Hit reaction, stagger, muerte |

La ventana de cancel se comunica al motor con un evento/notify en el clip, no con un timer paralelo — así sobrevive a cambios de timing [ver: gamedev/animacion §7].

### 2.3 Reglas de las transiciones que el animador debe conocer
El animador no configura el Inspector, pero SÍ decide (y le dice al programador):
- **Blend time por transición** (no el default): ~0.15–0.25 s para locomoción; ~0.05–0.10 s hacia el active de un ataque (snappy); más largo (0.3 s+) al volver a idle. El blend time ES game feel — se revisa uno a uno.
- **Punto de salida** (exit time): en locomoción, salir en el **contacto del pie** para que la siguiente anim empalme sin patinar.
- **Qué puede cortar qué**: combos necesitan que el ataque actual sea interrumpible por el siguiente (en Unity, `Interruption Source`; el default no-interrumpible es la causa #1 de "el personaje no responde") [ver: unity/animacion-unity §1].

---

## 3. Blend trees: qué CLIPS necesitas para alimentarlos

Un blend tree mezcla clips **similares** simultáneamente según parámetros. El requisito duro, agnóstico de motor: **todos los clips del árbol deben tener los pies en fase** — pie izquierdo apoya en el mismo tiempo normalizado en TODOS los clips (ej. 0.0 y 0.5). Si no, el blend "patina" (foot sliding) y ningún threshold lo arregla; se reeditan los clips [ver: ciclos-locomocion].

### 3.1 Locomoción 1D (por velocidad) — el clásico
Un solo parámetro (`Speed`) mezcla idle→walk→run→sprint. Los thresholds definen a qué valor cada clip tiene peso 1.0; el motor mezcla los dos clips más cercanos al valor actual. Automate/Compute Thresholds los reparte o los deriva de la velocidad real del root motion de cada clip (opción Speed) — mejor eso que ponerlos a ojo.

**Clips mínimos que debes producir para un 1D de locomoción:**
| Clip | Nota de autoría |
|---|---|
| Idle | Loop; respiración sutil. Base del árbol (threshold 0) |
| Walk (fwd) | Loop; contacto de pie en tiempos normalizados fijos |
| Run (fwd) | Loop; MÁS EXTREMO en poses que walk, no solo más rápido [ver: ciclos-locomocion] |
| Sprint (opcional) | Loop; zancada máxima |

### 3.2 Locomoción 2D direccional (strafe / apuntar y moverse)
Cuando el personaje puede moverse en una dirección MIENTRAS mira otra (shooters, action-RPG con lock-on), necesitas un blend 2D con dos parámetros (`MoveX`, `MoveZ` = velocidad local relativa a hacia dónde mira). Tipos y cuándo (verificado, Unity Manual):

| Tipo 2D | Cuándo | Restricción de clips |
|---|---|---|
| **Simple Directional** | Un clip por dirección (walk N/S/E/O) | NO puede haber dos clips en la misma dirección (no walk+run fwd) |
| **Freeform Directional** | Varias magnitudes por dirección (walk+run fwd) | **Obligatorio** un clip en (0,0) — el idle |
| **Freeform Cartesian** | X e Y no son direcciones (ej. velocidad angular vs lineal: "walk fwd no turn" vs "run fwd turn right") | — |

**El "strafe set" completo que debes producir** (patrón estándar third-person shooter, un anillo por tier de velocidad):
- Centro: **Idle** (0,0) — obligatorio en Freeform Directional.
- Anillo walk (8 direcciones): Walk_Fwd, Walk_Back, Walk_Left, Walk_Right, y las 4 diagonales (Walk_FwdLeft, Walk_FwdRight, Walk_BackLeft, Walk_BackRight).
- Anillo run (mismas 8 direcciones) para Freeform Directional con dos magnitudes.

Un set direccional serio son **1 idle + 8 walk + 8 run = 17 clips** solo de locomoción. Por eso se usa mocap/Mixamo para generarlos consistentes [ver: mocap-librerias]; animarlos a mano en fase es carísimo. Alternativa barata: 4 direcciones (cardinales) + dejar que las diagonales las mezcle el árbol — se nota más patinaje pero cuesta la mitad.

Las posiciones 2D de cada clip se pueden derivar del root motion (Velocity XZ, Speed And Angular Speed) en vez de arrastrarlas a ojo — usar eso.

### 3.3 Root motion vs in-place: decisión que cambia qué clip entregas
Un clip de locomoción se autora de dos formas incompatibles; hay que decidir ANTES:

| Modo | El clip contiene | El motor mueve al personaje con | Cuándo |
|---|---|---|---|
| **In-place** | El personaje corre "en su sitio" (root quieto) | Script/física (velocidad) | Shooters, plataformas, control preciso; el blend tree pide in-place |
| **Root motion** | El desplazamiento real está horneado en la raíz | La animación (el root avanza) | Melee con pisadas exactas, giros, Souls-like; evita foot sliding pero cuesta control |

En Unity el "root transform" es la proyección en el plano Y del "body transform" (centro de masa); el **Bake Into Pose** decide qué se queda en la pose y qué mueve al GameObject (verificado, Unity Manual):
- **Root Transform Rotation → Bake Into Pose** para walk/run rectos (orientación constante).
- **Root Transform Position (Y) → Bake Into Pose** en clips que NO deben cambiar la altura; **desactivar** en saltos (controla `gravityWeight`).
- **Root Transform Position (XZ) → Bake Into Pose** en idles para que no haya deriva posicional.

Regla de producción: **un blend tree de locomoción mezcla mejor con clips in-place** (el desplazamiento lo da el código); reservar root motion para acciones sueltas donde la pisada exacta importa. No mezclar los dos modos en el mismo árbol.

---

## 4. Blending y transiciones: qué mezcla limpio y el problema del pop

El **pop** = un salto visual brusco cuando dos poses no coinciden en el momento del blend. Es el defecto más común y el más barato de evitar si se planea.

**Qué blendea limpio (poses compatibles):**
- Clips del MISMO arquetipo de pose y en fase (todos los de locomoción con el pie izq en 0.0).
- Clips que empiezan/terminan cerca de una pose común (todo lo que sale de idle debe empezar cerca del idle).
- Additive sobre cualquier base (por construcción — ver §5).

**Qué NO blendea limpio (produce pop o interpenetración):**
- Poses opuestas (brazo arriba ↔ brazo abajo) mezcladas 50/50 → el brazo pasa por el medio, atraviesa el cuerpo.
- Clips con distinta velocidad de fase (walk lento contra run rápido sin sincronizar) → patinaje.
- Clips con root en posiciones muy distintas → salto de posición.

**Antídotos (todos de autoría, no de config):**
| Causa del pop | Antídoto |
|---|---|
| Poses de inicio/fin no coinciden | Autora los clips con una **pose de anclaje común** (ej. todos los ataques salen y vuelven a una guardia neutra) |
| Foot sliding en locomoción | Sincroniza el contacto de pie al mismo tiempo normalizado en todos los clips del árbol |
| Salto al entrar/salir de un ataque | Exit time y transición en el contacto de pie; blend time corto pero ≠ 0 |
| Loop que salta al reiniciar | Primer y último frame idénticos (o el motor iguala la pose sobre el rango, "loop pose") |
| Blend de dos direcciones opuestas atraviesa el cuerpo | Añade clips intermedios (diagonales) para que el árbol nunca mezcle 180° opuestos |

El **blend time** es un dial de game feel, no un default: corto = snappy (combate), largo = pesado (volver a idle). Revisar cada transición; jamás dejar el número que trae el motor [ver: gamedev/game-feel].

---

## 5. Animación por capas: additive vs override

Las capas dejan que distintas partes/aspectos del cuerpo corran máquinas de estado independientes que se **mezclan**. Dos modos de mezcla, y hay que elegir bien:

| Modo | Qué hace | Cuándo | Requisito de autoría |
|---|---|---|---|
| **Override** | La capa REEMPLAZA a las de abajo (dentro de su máscara) | Split cuerpo: torso dispara mientras piernas corren | Enmascarar a las partes que reemplaza; sin máscara pisa el cuerpo entero |
| **Additive** | La capa SUMA un delta encima de lo que haya debajo | Respiración, lean, sway de arma, flinch, "aim offset" | El clip debe ser un **delta respecto a una pose de referencia**, no una pose absoluta |

### 5.1 Additive: el delta sobre una pose de referencia
Additive es la técnica más malentendida. Un clip additive **no es una animación normal**: es la DIFERENCIA entre una animación y una **pose de referencia** (normalmente el primer frame o una T/idle). El motor suma esa diferencia sobre la capa base. Por eso:
- Un clip additive de "respiración" autorado como delta funciona sobre idle, sobre walk, sobre apuntar — sobre cualquier base.
- Si autoras el additive como pose absoluta en vez de delta, deforma el modelo (dobla el doble, gira raro). Antídoto: definir la pose de referencia correcta al crear el clip; en Unity el clip additive "debe contener las mismas propiedades" que las capas previas (verificado, Unity Manual).

**Casos canónicos de additive** (vida gratis, se autora una vez, aplica a todo):
| Additive | Delta sobre | Efecto |
|---|---|---|
| Respiración / idle-breath | Pose neutra | El personaje "respira" en cualquier estado |
| Aim offset (pitch de apuntado) | Pose de apuntar al frente | Sube/baja el arma según a dónde miras, sin clips por ángulo |
| Lean (inclinación al girar/acelerar) | Pose recta | Peso en curvas [ver: movimiento-secundario] |
| Flinch / hit-react ligero | Pose actual | Sacudida de daño sin cortar la locomoción |
| Recoil de arma | Pose de disparo | Retroceso sumado, reutilizable entre armas [ver: gamedev/animacion §6] |

### 5.2 Override + máscara: el split cuerpo (disparar mientras corres)
El patrón "upper/lower body split" es override con **avatar mask**:
- **Capa base**: locomoción cuerpo completo (piernas mandan).
- **Capa superior (override)**: clips de brazos/torso (disparar, recargar, lanzar), **enmascarada al tren superior** para no tocar las piernas.

La máscara humanoide agrupa el cuerpo en partes seleccionables (verificado, Unity Manual): **Head, Left/Right Arm, Left/Right Hand, Left/Right Leg, Root** (la "sombra" bajo los pies), más un toggle de **IK** para manos/pies. Para rigs genéricos (no humanoides) se enmascara por jerarquía de transforms (Import Skeleton + check por hueso). Beneficio extra: las partes no activas no cargan sus curvas → menos memoria y CPU.

**Receta shoot-while-running (agnóstica):**
1. Base: blend tree de locomoción (in-place) cuerpo completo.
2. Layer "UpperBody" (override, máscara torso+brazos): sub-máquina Idle-aim / Fire / Reload.
3. Additive "Aim Pitch" encima para el ángulo vertical del arma.
4. Runtime: IK de la mano de apoyo al guardamanos + look/aim procedural (ver §6 de este archivo).

El **peso de capa** (0–1) enciende/apaga la capa; animarlo con un tween pequeño para que no haga pop (subir la capa de disparo de 0→1 en ~0.1 s, no seco). Peso 0 = coste cero [ver: unity/animacion-unity §3].

### 5.3 Sync layers: variantes de estado (herido, con antorcha)
Una capa puede **replicar la estructura** de otra pero con clips distintos: misma máquina de estados (idle/walk/run) pero cojeando (herido). Se cruza-mezcla por peso según la vida. Evita duplicar la lógica del grafo; solo cambian los clips [ver: unity/animacion-unity §3].

---

## 6. Autoral vs procedural/IK en runtime: quién resuelve qué

No todo se anima a mano. Regla de reparto: **anima a mano el gesto y la intención; resuelve en runtime lo que depende del mundo y no puedes prever al autorar.**

| Se ANIMA a mano (autoral) | Se resuelve en RUNTIME (procedural/IK) |
|---|---|
| Ciclos de locomoción, ataques, reacciones, gestos | **Pies en el terreno** (foot IK: raycast al suelo, reproyectar) — cuestas, escaleras |
| Poses de personalidad, timing, silueta | **Look-at / aim** (girar cabeza/torso/arma al objetivo) |
| Lo que define el estilo del personaje | **Mano al arma / al asa** (two-bone IK a un target) |
| El delta de additive (respiración, recoil) | **Lean/bob por velocidad**, jiggle de pelo/tela (springs) [ver: movimiento-secundario] |

Por qué: el animador no sabe la pendiente exacta del terreno ni dónde estará el enemigo. Esos se corrigen sobre la animación autorada, cada frame, con IK. Lo autoral da la INTENCIÓN; lo procedural la ADAPTA al mundo.

**Orden del stack de animación (siempre este orden):**
```
1. Clip base / blend tree (locomoción)         ← autoral
2. Capas override enmascaradas (torso dispara) ← autoral
3. Capas additive (respiración, aim, lean)     ← autoral (delta) + parámetro runtime
4. IK y procedural (pies al suelo, mirar, mano al arma) ← runtime, CORRIGE al final
```
El IK va **al final**: corrige sobre el resultado ya mezclado, si no, las capas de arriba lo pisan. Los pesos de IK/look-at siempre interpolados (nunca 0→1 seco). La config de IK en Unity (`OnAnimatorIK`, IK Pass, Animation Rigging) está en [ver: unity/animacion-unity §8]; los constraints de rig en [ver: rigging/ik-fk-constraints].

Importante: **la animación procedural nunca debe mover hitboxes/posición lógica sin decisión explícita** — el bob/lean es visual; las hitboxes quietas [ver: gamedev/game-feel].

---

## 7. El set de clips de un personaje jugable completo

La lista real que produces para un personaje de acción third-person. Organizada por categoría (así se organiza también en el proyecto y en el grafo):

### Locomoción (blend trees)
| Clip | Loop | Notas |
|---|---|---|
| Idle | ✔ | Base; + variantes idle aleatorias (bostezo, mirar reloj) via blend Direct |
| Walk fwd (+ back/left/right + 4 diagonales si strafe) | ✔ | En fase; in-place para el árbol |
| Run fwd (+ set direccional si strafe) | ✔ | Poses más extremas |
| Sprint | ✔ | Zancada máxima |
| Crouch idle / crouch walk | ✔ | Sub-árbol de agachado |
| Turn in place (L/R 90°/180°) | — | Para que no patine parado girando |

### Transiciones de locomoción (one-shot, no loop)
| Clip | Notas |
|---|---|
| Idle→Walk / Walk→Idle start-stop | Evita el "arranque de patín"; en juegos AAA es un blend tree aparte |
| Plant & turn (frenar y girar) | Souls/action; caro pero vende el peso |
| Jog stop (pie que frena) | — |

### Aéreo
| Clip | Loop | Notas |
|---|---|---|
| Jump start | — | Despegue (squash) |
| Jump loop / fall loop | ✔ | Mientras está en el aire |
| Land (soft / hard) | — | Aterrizaje; hard con recovery |
| Airborne additive (flail) | — | Additive sobre el fall |

### Acciones / combate (one-shot, la mayoría committed) [ver: animacion-combate]
| Clip | Notas |
|---|---|
| Attack 1/2/3 (combo) | Con ventana de cancel marcada por evento |
| Heavy attack (wind-up largo) | — |
| Block / parry / dodge-roll | Dodge con i-frames marcados por evento |
| Reload / equip / holster | Enmascarados al tren superior (override) |
| Interact (pickup, lever, door) | — |
| Aim idle + Fire (upper body) | Capa override + additive de pitch |

### Reacciones (prioritarias, interrumpen casi todo)
| Clip | Notas |
|---|---|
| Hit light (front/back/left/right) | Additive o full según fuerza |
| Hit heavy / stagger | Committed corto |
| Knockdown → Ground idle → Get up | Cadena |
| Death (varias variantes por dirección) | Committed total |

### Additive / partial (deltas)
| Clip | Notas |
|---|---|
| Breathe additive | Sobre cualquier base |
| Aim pitch offset | Sobre aim idle |
| Lean additive | Curvas/aceleración |
| Recoil additive | Por disparo |

**Orden de magnitud:** un personaje jugable "completo" son fácilmente **60–120 clips**. Un enemigo simple, 15–30. Presupuestar esto ANTES de decidir mocap vs a mano [ver: mocap-librerias].

---

## 8. Naming y organización (para que el grafo sea manejable)

Un grafo de 80 estados con clips llamados `mixamo.com`, `Take 001`, `Armature|Action` es ingobernable. Convención desde el minuto cero:

**Naming de clips** — `Categoria_Accion_Variante_Direccion`:
```
Loco_Walk_Fwd        Loco_Run_FwdLeft     Loco_Idle
Combat_Attack_01     Combat_Dodge_Roll    Combat_Block_Idle
React_Hit_Light_F    React_Death_Back     React_Knockdown
Add_Breathe          Add_AimPitch         Add_Recoil
Air_Jump_Start       Air_Fall_Loop        Air_Land_Hard
```
Reglas: prefijo de categoría (agrupa y ordena alfabéticamente solo), snake/PascalCase consistente, dirección al final (`_Fwd`, `_BackLeft`), variantes numeradas con cero a la izquierda (`_01`, `_02` para que ordenen bien).

**Organización de assets** (carpetas espejo de las categorías):
```
Animations/
  Locomotion/   Combat/   Reactions/   Additive/   Airborne/   Interact/
  _Source/      ← FBX crudos de Mixamo/mocap sin tocar
```

**Organización del grafo:**
- Sub-máquinas por dominio (§2.1), no un plano gigante.
- Parámetros nombrados por lo que significan en gameplay (`Speed`, `IsGrounded`, `AttackTrigger`), no `float1`.
- Una capa = un propósito (Base, UpperBody, Additive-Breathe, Additive-Aim). No apilar propósitos en una capa.
- Cachear parámetros por hash en código, no strings [ver: unity/animacion-unity §1].

El coste de una convención floja no se paga al crearla — se paga al mes cuando nadie sabe qué clip alimenta qué estado y cada cambio rompe una ruta oculta.

---

## Reglas prácticas

- [ ] Diseña el grafo en papel ANTES del Inspector: lista de estados → capas → parámetros → transiciones. Estabiliza estados antes de cablear.
- [ ] Distingue SWITCH (transición, cambio discreto) de DIAL (blend tree, mezcla continua). Locomoción = blend tree; idle↔attack = transición.
- [ ] Etiqueta cada estado como interruptible / committed-con-ventana / committed-total / prioritario. Marca la ventana de cancel con un evento en el clip, no con timer.
- [ ] Todos los clips de un blend tree en fase: contacto de pie al mismo tiempo normalizado. Si patina, reedita el clip, no ajustes thresholds a ojo.
- [ ] Deriva thresholds/posiciones del blend tree de la velocidad real del root motion (Compute/Automate), no a ojo.
- [ ] Decide in-place vs root motion ANTES de animar; no los mezcles en el mismo árbol. Blend tree de locomoción → in-place.
- [ ] Root motion: Bake Into Pose de rotación en walk/run rectos, de Y en clips sin cambio de altura, de XZ en idles; Y desactivado en saltos.
- [ ] Autora los clips que salen de idle empezando/terminando cerca de la pose de idle (pose de anclaje común) para que no hagan pop.
- [ ] Additive = delta respecto a una pose de referencia definida, nunca pose absoluta. Verifica que no deforma sobre distintas bases.
- [ ] Split cuerpo = capa override + avatar mask al tren superior; additive para el pitch de apuntado. Peso de capa animado, nunca 0→1 seco.
- [ ] Peso de capa 0 = gratis; apaga capas no usadas bajando su weight.
- [ ] Reparto autoral/runtime: anima gesto e intención; resuelve pies-al-suelo, look-at y mano-al-arma con IK en runtime.
- [ ] Orden del stack: base → override enmascarado → additive → IK/procedural. El IK SIEMPRE al final, pesos interpolados.
- [ ] Procedural (bob/lean) solo en el transform visual; nunca mueve hitboxes/posición lógica sin decisión explícita.
- [ ] Presupuesta el set completo (60–120 clips personaje jugable, 15–30 enemigo) antes de elegir mocap vs a mano.
- [ ] Naming `Categoria_Accion_Variante_Direccion` desde el primer clip; carpetas espejo de las categorías; `_Source/` para los FBX crudos.
- [ ] Con >15 estados por capa: sub-máquinas por dominio. Parámetros nombrados por su significado de gameplay.
- [ ] Blend time por transición revisado a mano (~0.15–0.25 s locomoción, ~0.05–0.10 s hacia el active, más largo a idle); jamás el default del motor.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Meter idle→walk→run como transiciones separadas (el personaje "escalona" de velocidad) | Es un DIAL: un blend tree 1D por `Speed`, no tres estados con transiciones |
| Blend tree que patina (foot sliding) | Clips en fase (pie izq mismo tiempo normalizado) + in-place + thresholds desde velocidad real |
| Clip additive deforma el modelo (dobla doble, gira raro) | Está autorado como pose absoluta; recréalo como delta respecto a la pose de referencia correcta |
| Capa de disparo tapa también las piernas | Falta la avatar mask al tren superior en la capa override |
| Pop al entrar/salir de un ataque | Autora ataques que salen y vuelven a una guardia neutra común; blend time corto pero ≠0, exit en contacto de pie |
| Blend de dos direcciones opuestas atraviesa el cuerpo | Añade clips diagonales; el árbol nunca debe mezclar 180° opuestos a 50/50 |
| Loop de walk que "salta" al reiniciar | Primer=último frame (o usa loop pose que iguala sobre el rango) |
| Mezclar clips in-place y root-motion en el mismo árbol | Elige un modo por árbol; el desplazamiento lo da el código (in-place) o la anim (root motion), no ambos |
| IK de pies pisado por las capas de arriba | El IK va al final del stack, después de todas las capas de clips |
| Combo que no encadena / "no responde" | El estado de ataque no es interrumpible por el siguiente; marca ventana de cancel + permite la interrupción |
| Root motion no avanza (el personaje se queda) o avanza doble | Un solo dueño del desplazamiento: o el script o el root motion, nunca ambos sobre el mismo eje |
| 80 clips llamados `mixamo.com`/`Take 001` y grafo ingobernable | Convención `Categoria_Accion_Variante_Direccion` + sub-máquinas por dominio desde el minuto cero |
| Animar 8 direcciones × 2 velocidades a mano (17 clips) y quemar el presupuesto | Mocap/Mixamo para sets direccionales consistentes; a mano solo lo que da personalidad [ver: mocap-librerias] |
| Procedural que mueve el collider (hitbox sigue al bob) | Separa transform visual del lógico; el procedural solo toca lo visual |

## Fuentes

- **Animation Layers** — Unity Manual 6000.2 (`AnimationLayers.html`) — override vs additive, ejemplo lower-body/upper-body, avatar masks (símbolo M), sync layers (símbolo S) con clips distintos y misma estructura, checkbox Timing. Fetch directo.
- **Avatar Mask** — Unity Manual 6000.2 (`class-AvatarMask.html`) — 8 partes humanoides (Head, L/R Arm, L/R Hand, L/R Leg, Root), toggle de IK, enmascarado por Import Skeleton en genéricos, reducción de memoria/CPU al excluir partes. Fetch directo.
- **2D Blending / Blend Trees** — Unity Manual 6000.2 (`BlendTree-2DBlending.html`) — Simple Directional (un clip por dirección, sin dos en la misma), Freeform Directional (varias magnitudes, obligatorio clip en (0,0)), Freeform Cartesian (X/Y no direcciones), Direct; Compute Positions (Velocity XZ, Speed And Angular Speed). Fetch directo.
- **1D Blending** — Unity Manual 6000.2 (`BlendTree-1DBlending.html`) — parámetro único, thresholds como picos de pirámide (peso 1), mezcla de las dos motions adyacentes sumando 1.0, Automate Thresholds (reparto uniforme), Compute Thresholds from Speed/Velocity/Angular. Fetch directo.
- **Root Motion** — Unity Manual 6000.2 (`RootMotion.html`) — body transform (centro de masa) vs root transform (proyección en Y), Bake Into Pose de rotación (walk/run rectos), de posición Y (controla gravityWeight; off en saltos), de XZ (idles, evita deriva), loop pose distribuido 0–100%. Fetch directo.
- **Retargeting the Same Animations to Different Character Models** — Unity Manual 6000.2 (`Retargeting.html`) — el Avatar humanoide (muscle system) mapea animaciones entre esqueletos de igual estructura; retargeting solo posible en humanoid con Avatar configurado; mismo Animator Controller para varios modelos. Fetch directo. Base para consumir mocap/Mixamo [ver: mocap-librerias].
- **Mixamo** — Adobe (mixamo.com; FAQ como SPA no renderiza a fetch) — auto-rigger + librería de animaciones humanoides, descarga FBX con opción in-place, consumidas en Unity vía retargeting humanoide. Detalle de specs/precios → [ver: mocap-librerias] (no re-verificado aquí por SPA).
- **The Animator's Survival Kit** — Richard Williams (libro canon) — mecánica de walk/run cycles y contactos de pie a nivel concepto (por qué el contacto de pie es el ancla de fase de un ciclo). Referencia conceptual.
- **[ver: unity/animacion-unity]** (base sintetizada) — configuración exacta en Unity de layers/masks/sync layers, blend trees 1D/2D, transiciones e Interruption Source, IK (OnAnimatorIK/Animation Rigging), costes de Mecanim.
- **[ver: gamedev/animacion]** (base sintetizada) — 12 principios en gameplay, anatomía de ataque (wind-up/active/recovery), concepto motor-agnóstico de state machine + blend space + layers + additive, recetario procedural (lean/bob/recoil/foot-IK).
- **[ver: gamedev/fundamentos-diseno]** (base sintetizada) — MDA, core loop y decisiones significativas: marco de por qué existen los estados (committed vs interrumpible es diseño, no técnica).
