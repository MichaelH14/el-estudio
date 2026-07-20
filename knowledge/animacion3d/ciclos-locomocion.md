# Ciclos de locomoción (walk / run / idle)

> **Cuando cargar este archivo:** al producir el set de movimiento de un personaje jugable 3D — construir o corregir un walk/run/idle, sincronizar la velocidad del ciclo con la del juego (foot sliding), decidir in-place vs root motion, montar el set mínimo de locomoción (turn/strafe/start-stop/crouch/jump), o limpiar clips de mocap/Mixamo para que loopeen y no patinen. Fase de ANIMACIÓN 3D general (técnica y principios, agnóstica de herramienta). La ejecución concreta en Blender es fase aparte. El consumo en Unity está en [ver: unity/animacion-unity].

Este archivo NO repite los 12 principios ni el recetario procedural de lean/bob/spring (eso está en [ver: gamedev/animacion]) ni el modelo input→responsiveness ([ver: gamedev/game-feel]). Aquí va la **profundidad de producción 3D**: cómo se construye físicamente un ciclo, cómo se cierra el loop, y cómo se acopla a la velocidad del gameplay sin patinar.

---

## 1. Qué es un ciclo y por qué se cicla

Un **ciclo** es la unidad mínima de movimiento repetible: un paso completo del pie izquierdo + uno del derecho vuelve a la pose inicial. Se anima UNA vez y se loopea indefinidamente (Wikipedia, *Walk cycle*: "the walk cycle is looped over and over, thus avoiding having to animate each step again"). Todo lo demás de la locomoción (girar, arrancar, frenar) son transiciones o variaciones alrededor de ese núcleo cíclico.

- El modelo físico de UN paso (inclinarse = caída controlada → contacto = frenar la caída → empuje arriba) ya está desarrollado en [ver: gamedev/animacion §6]. Aquí se asume y se construye encima.
- En 3D de juego el ciclo se muestrea de forma **continua** (interpolado a 30/60 fps por el motor), no "on twos" como el 2D dibujado — el frame-count de abajo es la resolución de *keys*, no de dibujos. Contraste con el desacople de Cuphead (2D on-ones) en [ver: gamedev/animacion §3].
- Un ciclo tiene dos verdades que gobiernan todo: **(a)** primer y último frame deben cerrar sin salto (§6) y **(b)** su velocidad implícita de avance debe casar con la del juego o los pies patinan (§8).

---

## 2. El walk cycle: las 4 poses clave

Canon de Richard Williams (*The Animator's Survival Kit*) y Preston Blair: un paso (medio ciclo) se construye con **4 poses clave**, y el paso opuesto es su espejo. Full cycle = 8 poses clave (4 × 2 pies).

| # | Pose | Qué pasa | Altura de cadera | Peso |
|---|---|---|---|---|
| 1 | **Contact** | Piernas abiertas al máximo (extremo): talón del pie delantero apoya, punta del trasero aún toca. Brazos en su extremo opuesto | **Media** | Repartido, transfiriéndose al pie delantero |
| 2 | **Down / Recoil** | El peso cae sobre el pie delantero ya plantado; la rodilla se flexiona para absorber. Punto más bajo del cuerpo | **Mínima** (el "hundimiento") | Sobre el pie de apoyo, absorbiendo el impacto |
| 3 | **Passing** | La pierna libre pasa por debajo del cuerpo; la de apoyo es la más recta; peso 100% sobre ella | **Media-alta** (subiendo) | Todo sobre un solo pie (single support) |
| 4 | **Up / High-point** | La pierna de apoyo se extiende y empuja con la bola del pie; punto más alto justo antes del siguiente contacto | **Máxima** | Empujando hacia arriba y adelante |

Después de la pose 4 viene el **Contact del pie opuesto** → se repite espejado. La secuencia de altura de cadera dibuja **dos rebotes por ciclo** (down→up por cada paso): es la firma vertical del walk. Si la cadera no sube y baja, el personaje "flota".

### Mecánica corporal que acompaña (lo que vende un walk vs. un maniquí)

- **Swing de brazos opuesto a piernas**: brazo derecho adelante cuando la pierna izquierda va adelante (contrapeso). Sin esto, "paso de zombi".
- **Rotación de caderas (twist en Y)**: la cadera rota adelantando el lado de la pierna que avanza.
- **Contra-rotación de hombros**: los hombros giran OPUESTO a las caderas (la columna hace de torsión). Caderas y hombros en fase = robot.
- **Tilt de cadera (roll)**: la cadera cae del lado de la pierna LIBRE (la que no soporta peso) — el clásico ladeo de pelvis.
- **Shift lateral de peso**: la cadera se traslada LATERALMENTE sobre el pie plantado en cada paso (vaivén izq-der). Es lo primero que falta cuando algo "camina sobre hielo".
- **Overlap**: cabeza, pelo, manos, accesorios llegan tarde a cada pose ([ver: movimiento-secundario]).

### Frame counts (conveniencias, NO absolutos)

Dependen del fps del proyecto y del carácter. Referencia Williams: un walk natural es **un paso cada 12 frames a 24 fps** → **full cycle = 24 frames** (2 pasos, ~1 s). Escala:

| Tempo | Frames por paso @24fps | Full cycle | Lectura |
|---|---|---|---|
| Stroll / pesado / cansado | 16 | 32 | Lento, grave |
| **Walk natural (default Williams)** | **12** | **24** | Neutro |
| Brisk / decidido | 8 | 16 | Rápido, ligero |
| Sneak / marcha militar | variable | según intención | Estilizado |

- A 30 fps de juego, los equivalentes suben proporcional (~30 frames full cycle para un walk natural). Da igual el número exacto: lo que importa es que el **timing lea el peso** y que los contactos caigan en tiempos normalizados limpios (§6, §8).
- Personaje pesado → cadencia más lenta, rebote menor pero hundimiento (down) más profundo. Ligero → cadencia rápida, más rebote.

---

## 3. Run cycle: qué cambia respecto al walk

No es "un walk más rápido": cambia la **física de contacto**.

| Rasgo | Walk | Run |
|---|---|---|
| **Fase aérea** | NUNCA (siempre ≥1 pie en el suelo) | **SÍ**: hay frames con AMBOS pies en el aire (flight/aerial phase). Es la diferencia definitoria |
| **Contacto** | Talón primero (heel strike), pie rueda | Bola del pie / metatarso primero; el talón casi no toca |
| **Inclinación del torso** | Casi vertical, ligero adelanto | **Marcado adelante** (cuanto más rápido, más lean) — el cuerpo "cae" hacia delante y las piernas lo alcanzan |
| **Brazos** | Swing relajado, casi rectos | Codos flexionados ~90°, bombeo enérgico |
| **Rebote vertical** | Suave | Más pronunciado (el vuelo sube la cadera más) |
| **Zancada** | Corta | Larga, extremos más extendidos |
| **Rodillas** | Flexión moderada | Rodilla libre sube alto (recogida) |

- **Poses clave del run**: mismas etiquetas (Contact → Down/recoil → Passing → Up) PERO el "Up" se convierte en la **fase aérea** (el push-off lanza el cuerpo y ambos pies dejan el suelo). Preston/Williams: el run tiene contacto, recoil (absorción), high-point aéreo, passing.
- **Frames (conveniencia)**: más rápido que el walk. Referencia Williams: un run va **de 6 a 8 frames por paso** → full cycle ~12–16 frames @24fps. En juegos a 30 fps se ven ~16–24 frames full cycle. De nuevo: rango, no ley.
- **Jog / trote**: punto intermedio walk↔run (a veces YA con micro-fase aérea). En un blend tree suele ser el clip del medio (idle→walk→jog→run→sprint) [ver: capas-estados].
- **Sprint**: lean máximo, zancada máxima, fase aérea larga, brazos altos. Es el extremo del eje de velocidad, no un sistema aparte.

---

## 4. Idle: por qué NUNCA es estático

Un idle de un solo frame lee como "juego pausado / roto". Un personaje vivo respira y se reajusta aunque esté quieto.

| Capa del idle | Qué es | Detalle de producción |
|---|---|---|
| **Breathing** | Pecho/hombros suben y bajan; columna y cabeza acompañan sutil | Ciclo lento, ~1 respiración cada 3–5 s. Ideal como capa **additive** para que siga bajo aim/combate ([ver: capas-estados], [ver: movimiento-secundario]) |
| **Weight shift / sway** | Micro-traslado de peso entre pies, balanceo mínimo | Evita el "maniquí clavado". Amplitud pequeña |
| **Micro-movimientos** | Parpadeo, micro-giros de cabeza, dedos | Barato, sube muchísimo la percepción de vida |
| **Idle breaks / fidgets / variations** | Acciones mayores ocasionales: estirarse, mirar alrededor, revisar el arma, impacientarse | Se disparan tras N segundos en idle (o aleatorio), se reproducen UNA vez y **vuelven al idle base**. Dan personalidad |

- **Loop largo**: el idle base conviene largo (2–6 s) para que el loop no se note "tic-tic". Un breathing de 2 frames ya bate a un frame fijo, pero cuanto más largo el ciclo, menos evidente la repetición.
- **Desfasar la fase entre NPCs**: si 20 guardias respiran al unísono, delata el clip. Arrancar cada Animator con un offset de tiempo aleatorio (`Play(state, 0, Random.value)`) rompe el sincronismo — [ver: unity/animacion-unity].
- **Idle direccional / de estado**: idle armado ≠ idle desarmado ≠ idle herido ≠ idle crouch. Cada estado gameplay quiere su idle (o su capa additive sobre uno base).
- El idle es también el destino de "start/stop": arrancar y frenar desembocan en el idle (§9).

---

## 5. Weight y balance: el centro de masa manda

La diferencia entre un personaje que "tiene peso" y uno que "flota" es dónde está el centro de masa y qué hace la base de apoyo. En Unity esto es literal: el **Body Transform representa "the character's mass center"** y de él se deriva el Root (Unity Manual, *Root Motion*) — [ver: unity/animacion-unity §Root Motion].

| Concepto | Regla | Síntoma si se rompe |
|---|---|---|
| **Centro de masa (pelvis/cadera)** | Debe mantenerse sobre la **base de apoyo** (pie o pies plantados) o el personaje lee como cayendo | Personaje que parece a punto de tumbarse |
| **Rebote vertical de cadera** | Baja al recibir peso (down), sube al empujar (up). La cantidad LEE el peso: pesado = poco rebote, hundimiento profundo, lento; ligero = mucho rebote, rápido | Sin rebote → flota; rebote parejo pesado y ligero → todos pesan igual |
| **Shift lateral** | La cadera se traslada sobre el pie de apoyo cada paso | Sin shift → "camina sobre hielo" |
| **Foot plant (contacto sin deslizamiento)** | El pie plantado NO se mueve respecto al suelo mientras soporta peso; se pega y actúa de pivote | **Foot sliding** = el pecado capital (§8) |
| **Anticipación de peso** | El cuerpo se prepara antes de mover peso grande (agacharse antes de saltar, cargar antes de empujar) | Movimiento sin esfuerzo aparente |

- El **contact** es la pose que sostiene el peso (el "hold" que lo hace legible); el **down** es la que vende el impacto de ese peso al aterrizar. Son las dos poses que más comunican masa.
- Balance en giros: el cuerpo se **inclina hacia el interior** de la curva; el centro de masa se desplaza hacia dentro. Un giro sin lean lee como patinaje.
- El foot plant se garantiza en producción con **foot IK / foot locking**: se fija el pie a su punto de contacto durante la fase de apoyo y el IK absorbe desniveles y micro-desajustes ([ver: rigging/ik-fk-constraints]).

---

## 6. Ciclos loopables perfectos: cerrar el loop

Un loop malo produce un **hitch** (tirón) cada vuelta. Reglas para que sea invisible:

- **Regla del frame duplicado**: la pose de INICIO y la pose de "un frame DESPUÉS del último" deben ser idénticas; el frame final dibujado NO debe ser igual al primero, o el motor reproduce la misma pose dos veces → tartamudeo. Es decir: animas frames `0..N`, el motor loopea `0 → N → 0`, tratando `N` como el punto de wrap (== `0`). Nunca hagas `frame_final == frame_0` como fotogramas distintos.
- **Continuidad de las curvas, no solo de las poses**: aunque la pose case, si la **tangente/velocidad** en el último frame no empalma con la del primero, hay un micro-tirón en la aceleración. Igualar tangentes en el seam (graph editor) — [ver: keyframes-curvas].
- **Contactos en tiempos normalizados limpios**: para que blends y sincronía funcionen, el pie izquierdo debe contactar SIEMPRE en el mismo tiempo normalizado en todos los clips de locomoción (p.ej. izq en 0.0, der en 0.5). Es requisito para blend trees — [ver: unity/animacion-unity §Blend Trees].
- **En Unity (verificación concreta)**: en el importer del clip, `Loop Time` + `Loop Pose` ON, y el **Loop Match indicator debe estar en verde** (mide cuánto difieren pose de inicio y fin; verde = casa). `Cycle Offset` desplaza dónde arranca el loop. `Root Transform Position (XZ) Bake Into Pose` para que un idle no derive en XZ. [ver: unity/animacion-unity].
- **Técnica de construcción**: animar 1.5 ciclos y recortar al rango que casa, o copiar el keyframe inicial al final y ajustar el interior; en mocap, buscar dos instantes de la toma con la misma fase y cortar entre ellos (§10).

---

## 7. In-place vs con desplazamiento (root motion)

Dos formas de que el clip exprese el avance. La elección define quién manda: la animación o el gameplay.

| | **In-place** | **Root motion** |
|---|---|---|
| Qué es | El personaje "corre en el sitio": el clip NO avanza en el mundo; el código/física mueve el transform | El avance está HORNEADO en la animación; el motor mueve el GameObject con el movimiento del clip |
| Quién manda | El gameplay (velocidad exacta, aceleración, físicas) | La animación (va exactamente adonde el clip dice) |
| Foot sliding | Riesgo ALTO si la velocidad del código ≠ cadencia del clip (§8) | Cero por construcción — SI nada más mueve al personaje |
| Precisión de control | Total (responsivo, ideal para plataformas/acción) | Menor; el control se "negocia" con la animación |
| Uso típico | La mayoría de juegos de acción/plataforma; blend trees por velocidad | Mocap-driven realista (giros con peso, ataques con desplazamiento, cinemáticas), stop/start con settle exacto |

**En Unity** (mecánica exacta en [ver: unity/animacion-unity]; resumen operativo aquí):

- El **Root Transform** es "a projection on the Y plane of the Body Transform"; sus cambios por frame se aplican al GameObject (Unity Manual, *Root Motion*).
- **Bake Into Pose** "transfiere el movimiento del Root Transform al Body Transform" → ese eje deja de mover el GameObject. Se usa por eje: `Rotation (Baked)` (no rota el objeto), `Position (Y) (Baked)` (no cambia altura), `Position (XZ) (Baked)` (evita drift — típico de idles).
- **Humanoid**: el Root sale del Body/mass-center. **Generic**: se usa el transform de **Root Node**; todo lo por debajo del root motion bone queda relativo al Root (Unity Manual).
- Toggle **`Animator.applyRootMotion`**: aplica (o no) el root motion al GameObject. **No tiene efecto si el script implementa `OnAnimatorMove()`** (Unity Scripting API).
- Vía **`OnAnimatorMove()`** el código intercepta `animator.deltaPosition` / `animator.deltaRotation` y los escala/reemplaza antes de aplicarlos (Unity Scripting API) — el patrón para "root motion asistido": el clip da la dirección/peso, el código ajusta la magnitud (evita patinar Y mantiene control). Con Rigidbody se pasa por `rb.velocity` preservando gravedad en Y.

---

## 8. Velocidad del ciclo vs velocidad del juego: el foot sliding

**Foot sliding (foot skating)** = el pie plantado se desliza sobre el suelo porque el avance de la ANIMACIÓN (zancada × cadencia) no coincide con la velocidad REAL del personaje en el mundo. Es el pecado capital de la locomoción: rompe la ilusión de peso al instante. En Unity el síntoma clásico del blend mal sincronizado ya está listado como "el blend patina" — [ver: unity/animacion-unity §Errores].

**Regla física**: `velocidad_de_avance_del_clip = longitud_de_zancada × cadencia`. Para no patinar, esa velocidad debe igualar la velocidad de traslación en el juego. Formas de garantizarlo:

| Método | Cómo | Cuándo / límites |
|---|---|---|
| **Escalar play speed a la velocidad** | Multiplicar la velocidad de reproducción del clip ∝ velocidad real (`playSpeed = worldSpeed / clipRefSpeed`) | Barato, pero estirar de más → "moonwalk" (muy lento) o "Benny Hill" (muy rápido). Válido en un rango pequeño alrededor de la velocidad nativa del clip |
| **Blend tree por velocidad con thresholds MEDIDOS** | Clips walk/jog/run authored a su velocidad nativa; thresholds = velocidad REAL de avance de cada clip (medida del root motion), no a ojo. Unity: `Compute Thresholds` desde Velocity | El estándar de producción. Cada clip suena a su cadencia; el blend interpola cadencia + zancada juntas |
| **Stride warping / stride matching** | Escalar proceduralmente la ZANCADA (no la cadencia) para casar la velocidad exacta; absorbe el desajuste residual entre los thresholds del blend | Motores modernos lo traen (Unreal 5 Stride Warping / Motion Warping). En Unity se implementa con IK/procedural. Evita el moonwalk del play-speed |
| **Root motion authority** | La animación conduce el movimiento; el gameplay se adapta a lo que el clip avanza | Locomoción mocap-driven realista (estilo Naughty Dog). Máxima fidelidad, control menos "arcade" (§7) |
| **Foot lock IK** | Fijar el pie a su punto de contacto durante el apoyo; el IK impide que resbale aunque haya micro-desajuste | Capa de seguridad SIEMPRE recomendable encima de cualquiera de los anteriores ([ver: rigging/ik-fk-constraints]) |

- **Combinación de producción típica**: blend tree por velocidad (thresholds medidos) **+** foot lock IK **+** un pequeño escalado de play speed dentro de cada tramo. Root motion para giros/paradas con peso.
- **Medir la velocidad nativa de un clip**: avance del root (o de la cadera si es in-place) ÷ duración. Ese número es el threshold correcto y la `clipRefSpeed` del escalado — nunca inventarlo.
- **Aceleración/desaceleración**: alimentar los parámetros del blend con **damping** (`SetFloat(hash, v, dampTime, dt)`) para que no haya snaps al cambiar de velocidad — [ver: unity/animacion-unity §Blend Trees].

---

## 9. El set mínimo de locomoción de un personaje jugable

Depende del **modelo de control**:

- **"El personaje mira hacia donde se mueve"** (Mario / aventura 3D): no necesita strafe; necesita **turn-in-place** y **skid/pivot**. Blend 1D por velocidad.
- **"El personaje mira independiente del movimiento"** (shooter TPS/FPS, MOBA, twin-stick): necesita **strafe** en todas las direcciones. Blend 2D direccional ([ver: unity/animacion-unity §Blend Trees 2D]).

| Clip | Por qué | Notas |
|---|---|---|
| **Idle** (+ variations/breaks) | Estado base; nunca estático (§4) | Direccional/estado si aplica (armado, crouch, herido) |
| **Walk fwd** | Movimiento base lento | |
| **Run / Jog / Sprint fwd** | Eje de velocidad | Blend por velocidad con thresholds medidos (§8) |
| **Strafe L/R** (+ walk/run) | Solo modelo "mira independiente" | 8-way o blend 2D freeform directional |
| **Back-pedal** | Caminar/correr hacia atrás | Cadencia distinta; ojo con foot sliding |
| **Turn-in-place 90° / 180° L/R** | Girar parado sin patinar los pies | Modelo "mira hacia el movimiento"; con paso cruzado real |
| **Start / arranque** | Idle→movimiento con anticipación de peso (inclinarse, primer paso) | Evita el "arranque teletransporte". Root motion ayuda mucho |
| **Stop / frenada (skid, settle)** | Movimiento→idle con desaceleración y asentamiento | El plant final vende el peso; sin él, freno de robot |
| **Pivot / quick-turn 180** | Cambio brusco de dirección corriendo | Con plant y contra-lean |
| **Crouch idle + crouch walk** | Sigilo/cobertura | Set reducido propio (idle, walk, quizá strafe) |
| **Jump set** | Aéreo (§10) | Estados separados |
| **Land / fall** | Aterrizaje y caída | Absorción proporcional a la altura |

- Empezar con el **núcleo mínimo jugable**: idle, walk, run, start, stop, turn, jump/land. Strafe y crouch se añaden si el diseño los pide. No animar 8-way strafe "por si acaso" si el personaje siempre mira al movimiento.
- Los start/stop y turn-in-place son los que MÁS separan un prototipo de un juego pulido: sin ellos, el personaje cambia de estado con pops y patina al arrancar/frenar.

---

## 10. Jump: anticipación, launch, air, land, recovery

Un salto tiene **5 fases**; el error clásico es meterlas en UN clip de duración fija cuando el tiempo en el aire es variable.

| Fase | Qué es | Responsividad |
|---|---|---|
| **Anticipation** | Flexión/carga previa (crouch, wind-up) | En el JUGADOR: mínima (1–3 frames) o procedural — más que eso se siente lag ([ver: gamedev/game-feel], [ver: gamedev/animacion §2]) |
| **Launch / Push-off** | Extensión explosiva de piernas, despegue | Snappy |
| **Air / Rise + Apex + Fall** | Cuerpo en vuelo; apex flotado; caída | DEBE decouplarse de la duración del clip |
| **Land / Impact** | Contacto y absorción (flexión de rodillas) | Absorción ∝ altura de caída |
| **Recovery** | Reasentarse y volver a locomoción | Cancelable (permitir moverse enseguida) |

**Un clip vs estados separados:**

| | Un clip baked | Estados separados (recomendado gameplay) |
|---|---|---|
| Estructura | Una animación de salto completa | `JumpStart` (anticip.+launch, one-shot) → `JumpAir/Loop` (pose de vuelo, LOOP sostenido) → `Land` (impacto) → `Recovery`→locomoción |
| Tiempo en el aire | Fijo por el clip | **Variable**: el loop aéreo se sostiene por un bool `IsGrounded`, no por el tiempo del clip — funciona para cualquier altura/duración |
| Cuándo | Salto scriptado de altura fija, cinemática | Salto físico con altura variable (lo normal) |

- La transición `Air → Land` la dispara el **contacto con el suelo** (raycast / `IsGrounded`), no el fin de un clip — así el aterrizaje siempre cae en el frame real del contacto.
- **Coyote time, jump buffer, gravedad asimétrica y apex flotado** son gameplay/feel, no animación: [ver: gamedev/game-feel §8]. La animación solo los REFLEJA (apex flotado = pose de apex sostenida).
- La absorción del land debe escalar con la velocidad vertical de impacto (caída corta = flexión leve; caída larga = flexión profunda, hasta roll). Un blend o un parámetro de "hardness" del land.
- Root motion en salto: normalmente NO (la parábola la manda la física); sí puede aportar el desplazamiento horizontal del launch en saltos direccionales scriptados.

---

## 11. Mocap y librerías (Mixamo) para locomoción — resumen

Depuración detallada de mocap en [ver: mocap-librerias]; aquí solo lo que toca a ciclos:

- **Retargeting**: el sistema **Humanoid Avatar** de Unity mapea los huesos a un esqueleto estándar (requiere T-pose) y permite **reusar los mismos clips de locomoción en personajes de proporciones distintas** — "as long as all the files use the same bone structure, you can re-use that Avatar" (Unity Manual, *Configuring the Avatar*). El sistema muscular (`Muscles & Settings`) acota rangos y "entiende" la estructura ósea para el retarget (Unity Manual, *Muscle Definitions*). [ver: rigging/rig-a-unity].
- **Mixamo** ofrece librería de walk/run/idle/jump ya capturados y auto-rig. Tiene una opción **"In Place"** para descargar el clip sin desplazamiento (para in-place + código) vs. con desplazamiento (root motion). ⚠️ *No pude re-verificar la página de ayuda de Mixamo en esta sesión (timeouts); los nombres exactos de opciones —In Place, with/without skin, FBX, fps— son ampliamente documentados pero trátalos como conocimiento previo no re-verificado hoy. Confirmar en la propia UI de Mixamo antes de afirmar detalles finos.*
- **Todo mocap de locomoción necesita cleanup para ciclar**: la toma no loopea sola. Hay que (a) encontrar dos fases idénticas y cortar entre ellas, (b) igualar pose Y tangentes en el seam (§6), (c) corregir foot sliding residual con foot lock IK (§8), (d) verificar que los contactos caen en tiempos normalizados limpios para que blendee (§6).
- Mocap crudo trae **ruido** y **drift**; un ciclo de juego suele quedar mejor con mocap como *base* + pases de keyframe encima ([ver: principios-produccion], [ver: keyframes-curvas]).

---

## Reglas prácticas

1. Construye el walk con las **4 poses clave** (contact / down / passing / up) y espeja para el paso opuesto; el full cycle son 8 keys.
2. La cadera **sube y baja dos veces por ciclo** (down tras cada contacto, up en cada push-off). Sin ese rebote, flota.
3. Mete **shift lateral de cadera** sobre el pie de apoyo cada paso — es lo primero que falta cuando "camina sobre hielo".
4. Caderas y hombros **contra-rotan**; brazos **opuestos** a las piernas. Nunca en fase (robot).
5. El run se define por su **fase aérea** (ambos pies fuera del suelo) + lean adelante + contacto con la bola del pie. No es un walk acelerado.
6. Frame counts como **rango**, no ley: walk natural ~24 frames full cycle @24fps (paso cada 12), run ~12–16. Deja que el timing lea el peso; confirma con el fps del proyecto.
7. El idle **nunca es un frame fijo**: breathing (additive) + sway + micro-movimientos, y idle breaks tras N segundos.
8. Desfasa la fase de los idles entre NPCs (offset de tiempo aleatorio) para que un grupo no respire al unísono.
9. Cierra el loop con la **regla del frame duplicado**: pose de inicio == "un frame después del último"; nunca dupliques el frame de inicio como final.
10. Iguala **tangentes** en el seam, no solo las poses — o hay micro-tirón de velocidad cada vuelta.
11. Contactos en **tiempos normalizados iguales** en todos los clips de locomoción (izq 0.0, der 0.5) para que blendeen sin patinar.
12. Mide la **velocidad nativa** de cada clip (avance del root ÷ duración) y usa ese número como threshold del blend y como `clipRefSpeed` — nunca lo inventes.
13. Contra el foot sliding: **blend por velocidad (thresholds medidos) + foot lock IK + escalado de play speed en rango pequeño**. Root motion para giros/paradas con peso.
14. Escala la velocidad de reproducción solo en un **rango pequeño** alrededor de la nativa; para rangos grandes, blend entre clips (evita moonwalk / Benny Hill).
15. Alimenta los parámetros del blend con **damping** para no snappear al acelerar/frenar.
16. Set mínimo jugable primero: idle, walk, run, **start, stop, turn, jump/land**. Strafe y crouch solo si el modelo de control los pide.
17. Anima el **jump como estados separados** con un loop aéreo sostenido por `IsGrounded`, no como un clip de duración fija.
18. La transición aire→land la dispara el **contacto real** (raycast/grounded), no el fin de un clip; escala la absorción del land con la velocidad de impacto.
19. Anticipación del salto del jugador **mínima** (1–3 frames o procedural); el peso se vende en launch, land y recovery, no alargando el startup ([ver: gamedev/game-feel]).
20. Foot IK / foot lock **encima de todo** para pegar los pies al suelo y a los desniveles ([ver: rigging/ik-fk-constraints]).

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| **Foot sliding** (pie plantado que resbala) | Casar `zancada × cadencia` con la velocidad del juego: blend por velocidad con thresholds MEDIDOS + foot lock IK; no estirar un solo clip a cualquier velocidad |
| Escalar un clip de walk a velocidad de sprint (moonwalk / Benny Hill) | Blend entre walk/jog/run/sprint; play-speed solo dentro de un rango pequeño por clip |
| Thresholds del blend puestos "a ojo" | Medir el avance real del root de cada clip; `Compute Thresholds` desde velocity |
| Loop con tartamudeo cada vuelta | Regla del frame duplicado: no repetir el frame de inicio como final; motor loopea `0→N→0` |
| Pose casa pero hay micro-tirón | Igualar también las tangentes/velocidad en el seam (graph editor) |
| Blend de locomoción que patina | Contactos en el MISMO tiempo normalizado en todos los clips (izq 0.0, der 0.5) |
| Personaje que "flota" al caminar | Rebote vertical de cadera (down/up) + shift lateral de peso; centro de masa sobre el pie de apoyo |
| "Camina sobre hielo" | Falta el shift lateral de cadera sobre el pie plantado |
| Run que es solo un walk rápido | Añadir fase aérea (ambos pies fuera), lean adelante, contacto de metatarso |
| Idle de un solo frame ("juego pausado") | Breathing additive + sway + idle breaks; loop largo (2–6 s) |
| 20 NPCs respirando al unísono | Offset de tiempo aleatorio al arrancar cada idle |
| Caderas y hombros rotando en fase | Contra-rotación de columna; brazos opuestos a piernas |
| Jump de un clip fijo → aterriza en el aire o "flota" en saltos altos | Estados separados: air LOOP sostenido por `IsGrounded`; land disparado por contacto real |
| Anticipación de salto larga en el jugador → control gomoso | Anticipación mínima/procedural; peso en launch/land/recovery |
| Arranque/frenada con pop (teletransporte de estado) | Clips de start/stop con anticipación de peso y settle; considerar root motion |
| Root motion peleando con el código (doble movimiento o freno) | Un solo dueño del avance por estado; con control fino, `OnAnimatorMove` escalando `deltaPosition` |
| Mocap de Mixamo que no loopea ni casa | Cortar entre dos fases idénticas, igualar seam, foot lock IK, verificar tiempos normalizados |
| Idle que deriva en el suelo (drift XZ) | `Root Transform Position (XZ)` → Bake Into Pose |

## Fuentes

**Bases de El Estudio sintetizadas (no repetidas, referenciadas):**
- [ver: gamedev/animacion] — 12 principios en gameplay, anatomía de ataque, recetario procedural (lean/bob/spring), modelo físico del paso (Little Polygon), frame counts de sprites, Rosen/Overgrowth. Este archivo asume ese material y aporta la producción 3D del ciclo.
- [ver: gamedev/game-feel] — responsiveness (<100 ms), coyote time, jump buffer, gravedad asimétrica/apex flotado, tweening/easing.
- [ver: unity/animacion-unity] — mecánica exacta de Animator, blend trees 1D/2D, layers/masks, root motion, culling, StringToHash. Este archivo da el ángulo de artesanía; ese da la implementación.

**Fuentes web (verificadas por fetch esta sesión, jul-2026):**
- **Root Motion** — Unity Manual 6000.2 (`RootMotion.html`) — Root Transform como proyección en Y del Body Transform; Body Transform = "character's mass center"; Bake Into Pose por eje (Rotation/Position Y/Position XZ); Humanoid (Body→Root) vs Generic (Root Node); Based Upon options.
- **Animator.applyRootMotion** — Unity Scripting API — toggle de aplicar root motion; "no effect if your script implements OnAnimatorMove"; cambiarlo en runtime reinicializa el Animator.
- **MonoBehaviour.OnAnimatorMove** — Unity Scripting API — intercepción de `animator.deltaPosition` / `deltaRotation` para escalar/reemplazar el root motion (patrón con y sin Rigidbody, preservando gravedad en Y).
- **Configuring the Avatar** — Unity Manual 6000.2 (`ConfiguringtheAvatar.html`) — Avatar como capa de mapeo de huesos, requisito de T-pose, reuso del mismo Avatar entre archivos con la misma estructura ósea → retargeting de locomoción (p.ej. Mixamo) entre proporciones distintas.
- **Muscle Definitions & Settings** — Unity Manual 6000.2 (`MuscleDefinitions.html`) — rangos de músculo que acotan el movimiento (ej. Head-Nod/Tilt −40..40°), el sistema "entiende" la estructura ósea para retarget; coste extra si se habilitan grados de traslación.
- **Walk cycle** — Wikipedia — las 4 poses (contact/passing × 2), el loop reutilizable ("looped over and over…"), in-betweens dibujados o interpolados, necesidad de brazos/cabeza/torsión.

**Canon de animación (nivel concepto, ampliamente documentado):**
- **The Animator's Survival Kit** — Richard Williams — las 4 poses clave del walk (contact/down/passing/up), tempos (paso cada 12 frames = walk natural; run en 6–8 frames), mecánica de rebote de cadera, contra-rotación, run con fase aérea. Citado a nivel de concepto (no re-verificado contra el libro esta sesión).
- **Preston Blair, *Cartoon Animation*** — poses de walk/run, timing y peso (concepto).
- **Mixamo** (Adobe) — librería de mocap walk/run/idle/jump + auto-rig; opción "In Place" (in-place vs con desplazamiento). ⚠️ Página de ayuda NO re-verificada esta sesión (timeouts); nombres de opciones = conocimiento previo, confirmar en la UI antes de afirmar detalles.
- **Stride Warping / Motion Warping** — concepto de motores modernos (Unreal 5) para casar la zancada a la velocidad exacta y absorber foot sliding sin cambiar cadencia. Referenciado a nivel de concepto (docs de Epic no extraíbles por fetch esta sesión — render JS).

*Gaps / a verificar en la siguiente pasada: (1) confirmar nombres exactos de opciones de Mixamo contra la ayuda de Adobe; (2) frame counts de locomoción específicos de estudios AAA (varían por proyecto/fps — aquí van como rangos); (3) detalle técnico de Stride Warping en Unreal 5 y su equivalente procedural en Unity.*
