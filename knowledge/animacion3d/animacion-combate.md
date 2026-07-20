# Animación de combate y acción (3D)

> **Cuando cargar este archivo:** al animar ataques, golpes, reacciones de daño, muertes, combos, y armas (melee/disparo/recarga) de personajes 3D para un juego. Cubre la PRODUCCIÓN de la animación (poses, arcos, frame de contacto, root motion, capas de reacción, ragdoll, sincronía con eventos). El *diseño* del combate y el juice del impacto están en [ver: gamedev/animacion] y [ver: gamedev/game-feel]; el *cableado* en Unity (Animator, transiciones, anim events) en [ver: unity/animacion-unity]. La ejecución concreta en el editor de animación es fase aparte (aún no documentada).

## Qué aporta este archivo (y qué NO repite)

Las bases ya fijan lo conceptual: [ver: gamedev/animacion] tiene los 12 principios en gameplay, la anatomía wind-up/strike/recovery con números (anticipación enemiga ~18f@30, jugador 1–3f), telegraphing por capas y el hitstop de Sakurai; [ver: gamedev/game-feel] tiene hit-stop, screenshake, knockback y flashes como capa de *engine*. **Aquí va la profundidad de producción 3D**: cómo se POSA y curva un ataque, cómo se autora el frame de contacto y el hold, cómo se baja el root motion de un lunge, cómo se construyen reacciones/muertes/combos como clips y capas, y qué frames marcan la hitbox/SFX/VFX. Cuando un número ya está en la base, se referencia, no se reescribe.

---

## 1. La estructura de un ataque, en poses 3D

El ataque son 3 fases (wind-up → strike → recovery) que mapean 1:1 a los frames de gameplay (startup / active / recovery) [ver: gamedev/animacion]. En 3D cada fase se construye con **poses clave con silueta legible** y **arcos** entre ellas; la fase siguiente (Blender/editor) lo ejecuta, aquí se decide QUÉ poses.

| Fase (anim) | Frame de gameplay | Poses clave a autorar | Regla de producción 3D |
|---|---|---|---|
| **Wind-up / anticipación** | Startup | 1 pose de carga (peso atrás, arma retraída, torsión de cadera opuesta al golpe) | Pose ÚNICA y legible en silueta; el enemigo la *sostiene* (hold) como contrato; el jugador la hace mínima [ver: gamedev/animacion] |
| **Strike / contacto** | Active | Pose de máxima extensión + el **frame de contacto** (sección 2) | Arco amplio de la extremidad/arma; el active dura pocos frames — smear/trail vende la velocidad |
| **Recovery / asentado** | Recovery | Pose de follow-through (el cuerpo se pasa y vuelve al balance) | Aquí va el PESO (overlap, inercia); es la ventana de castigo — su longitud = riesgo del ataque |

Principios de posing que gobiernan el combate (de los 12, [ver: gamedev/animacion]):
- **Timing manda sobre frame count**: holds desiguales (windup sostenido, contacto congelado, recovery que decae) leen mejor que interpolación uniforme.
- **Anticipación es diseño, no adorno**: torsión de cadera + peso atrás. La cadera/pelvis lidera; extremidades y arma llegan **tarde** (overlap, 2–4 frames de retardo hueso hijo respecto al padre) [ver: movimiento-secundario].
- **Contrapposto / línea de acción**: cada pose fuerte tiene una curva corporal clara (C o S). Una pose de combate recta y simétrica se lee muerta.
- **Exageración por legibilidad**: "real life never looks real enough" — el rango del golpe se sobrepasa para que se lea desde el ángulo de cámara del juego, no solo desde un ángulo ideal.

---

## 2. El frame de contacto y el peso: cómo la animación vende el golpe

El impacto NO lo vende el engine solo; la animación pone la mitad y el juice (hitstop, shake, partículas, número flotante) la otra mitad [ver: gamedev/game-feel]. Lo que autora el animador:

| Elemento | Qué es | Cómo se autora |
|---|---|---|
| **Pose de contacto** | El frame exacto de máxima energía en el punto de impacto | Extensión total del arco, extremidad estirada, cuerpo comprometido hacia delante. Test: pausar ese frame → debe leerse "golpe" sin contexto |
| **El hold del contacto** | 1–3 frames sosteniendo (o casi) la pose de contacto | Es la anim reflejando el hitstop del engine. La anim y el hitstop de código deben *coincidir* — si el engine congela 6f pero el clip ya avanzó, se rompe la ilusión |
| **Smear / multi-limb** | Frame(s) de transición al contacto donde el arma/brazo se estira o duplica | En 3D: deformar el mesh del arma en ese frame, o un mesh de "trail" adicional. Barato, vende velocidad en strikes de 1–2 frames |
| **Weapon trail** | Estela geométrica que marca la zona de peligro del arco | Malla generada a lo largo del arco de la punta del arma (ribbon), encendida solo en los frames active. Comunica el hitbox al jugador |
| **Overshoot + settle** | El cuerpo se pasa del contacto y regresa | El follow-through: la percepción de peso se construye AQUÍ, no alargando el windup |

- **Frame de contacto ≠ centro geométrico del swing**: se coloca donde el arco tiene más velocidad angular, ligeramente *antes* del punto muerto para que el impacto sienta que "corta a través".
- **Anti-arco deliberado**: romper el arco justo tras el impacto (la cabeza gira, el arma rebota) añade realismo tipo mocap [ver: gamedev/animacion].
- **La animación no mueve la hitbox**: el collider lógico lo abre un anim event en el frame active, no la deformación visual [ver: unity/animacion-unity]. La vibración/smear es puramente visual (lección Sakurai).
- El handoff completo del "juice" sobre esta pose (hitstop 2–4f normal / 8–15f fuerte, shake, flash, freeze) vive en [ver: pipeline/feel-en-unity] y [ver: gamedev/game-feel]. El animador entrega la pose y el frame; el engine la amplifica.

---

## 3. Telegraphing legible en 3D

El wind-up del enemigo es el único aviso que recibe el jugador — es un contrato [ver: gamedev/animacion]. La producción 3D lo hace legible con:

| Recurso 3D | Cómo |
|---|---|
| **Silueta única por ataque** | Cada wind-up con una pose distinta en negro-sobre-blanco. Si dos ataques comparten silueta, el jugador no puede elegir respuesta. Probar la silueta desde el ángulo de cámara real |
| **Hold del wind-up** | Sostener la pose de carga N frames escala con la letalidad: golpe leve = hold corto, golpe letal = hold largo + más VFX. El hold ES la ventana de reacción |
| **Sobre-rotación de la parte que ataca** | El brazo/arma se retrae MÁS de lo natural para agrandar el arco y hacer obvio de dónde viene |
| **Asimetría de peso** | Peso claramente cargado a un lado/atrás: el cuerpo "avisa" la dirección del golpe |
| **Sync con VFX/color/sonido** | Partículas que se acumulan en el hold, flash de carga, glow del arma — los marca un anim event en el frame de inicio del windup [ver: unity/animacion-unity] |

- **Recovery es telegraph también**: comunica CUÁNDO castigar. Ataque fuerte → recovery larga y legible (pose de desbalance sostenida); débil → recovery corta.
- Contexto de estilo: realista → telegraph sutil (montar el arma, cambio de guardia); estilizado → teatral (sobre-anticipación, poses cartoon). Consistencia entre animadores del mismo enemigo.

---

## 4. Root motion en ataques: lunge vs in-place

Un ataque que avanza (lunge, dash-attack, plunge) puede mover al personaje **desde la animación** (root motion) o dejar que el código lo mueva (in-place). La decisión se toma por-clip y se **hornea en el import del clip** [Unity Manual · Root Motion].

### El modelo de Unity (verificado)
- **Root Transform** = proyección en el plano Y del **Body Transform** (centro de masa); es lo que mueve el GameObject cada frame cuando *Apply Root Motion* está activo en el Animator.
- Cada clip tiene 3 grupos de ajuste de root en el import, cada uno con **Bake Into Pose** (on = el movimiento se queda en la pose, NO mueve el objeto) y **Based Upon** (referencia):

| Ajuste del clip | Bake Into Pose = ON | Bake Into Pose = OFF | Based Upon |
|---|---|---|---|
| **Root Transform Rotation** | La orientación se queda en el cuerpo; el objeto no gira por el clip | La rotación mueve al GameObject | Body Orientation (mocap) · Offset · Original (keyframe) |
| **Root Transform Position (Y)** | La altura se queda en la pose; `gravityWeight`=1 (física manda en Y) | La anim mueve la altura (saltos, plunge); `gravityWeight`=0 | Original · Center of Mass · **Feet** (evita flotar al blendear) |
| **Root Transform Position (XZ)** | Fuerza delta XZ = 0 (idles, ataques in-place sin drift) | La anim mueve en XZ (el lunge avanza) | Original · Center of Mass · Offset |

### Recetas para ataques
| Ataque | Rotation | Position Y | Position XZ | Por qué |
|---|---|---|---|---|
| **Lunge / dash-attack** (avanza) | Bake ON (no rota) | Bake ON (sin salto) | Bake OFF (avanza desde anim) | El desplazamiento sale del clip → sensación de compromiso físico, imposible de sobre-explotar |
| **Ataque en el sitio** (in-place) | Bake ON | Bake ON | **Bake ON** | Fuerza XZ=0; el jugador no se desliza; útil para combos donde el código controla la posición |
| **Plunge / ataque aéreo** | Bake ON | Bake OFF (cae desde anim) | según diseño | La altura la maneja la animación |

- **In-place + código** da control total (buscar al enemigo, warping a la distancia exacta) pero puede sentirse "flotante" si el desplazamiento no coincide con los pasos → foot sliding. **Root motion** ata el movimiento al pie y se siente con peso, pero es rígido (avanza SIEMPRE lo mismo).
- **Combate de acción moderno**: híbrido — root motion como base + *motion warping* (escalar/rotar el desplazamiento del root en runtime para alcanzar el objetivo). El animador debe autorar el root avanzando en línea limpia para que el warp no rompa.
- **Curved attacks**: si el ataque gira (giro de 180°, barrido), Rotation Bake OFF y autorar el giro en el root; verificar Based Upon = Body Orientation para mocap.
- Riesgo: mezclar clips con root motion y sin él en el mismo Animator produce saltos de velocidad; decidir por-estado y ser consistente [ver: unity/animacion-unity].

---

## 5. Hit reactions, flinches, hitstun y knockback

La reacción de daño es la respuesta legible a "me golpearon". Se construye como **clips direccionales** y/o **capas additive**, según cuánto deba interrumpir.

| Tipo de reacción | Construcción | Cuándo |
|---|---|---|
| **Flinch aditivo** | Clip additive corto (torso/cabeza) que SUMA sobre la anim base (correr, atacar) sin cortarla | Daño leve que no debe frenar la acción; "chip" de golpes rápidos [ver: capas-estados] |
| **Hit reaction full-body** | Clip completo que interrumpe el estado actual; el personaje se dobla/retrocede | Golpe medio que sí frena; entra por transición con Interruption Source [ver: unity/animacion-unity] |
| **Direccional (4/8 dir)** | Set de clips: golpe desde front/back/left/right (mínimo 4). El código elige por el ángulo atacante→víctima | Combate que premia flanquear; vende de dónde vino el golpe |
| **Knockback / launch** | Clip de vuelo + caída, o root motion de retroceso, o impulso físico + pose additive | Golpe fuerte/finisher; el desplazamiento puede ser root motion, código, o ragdoll parcial |
| **Stagger / stun largo** | Reacción sostenida con recovery larga = ventana de castigo | Romper la "poise"/armadura del enemigo (abajo) |

- **Hitstun** = frames en que la víctima no puede actuar tras el golpe; en anim es la *duración* del clip de reacción. En fighting games el hitstun encadena combos; en action-RPG define la ventana de seguir pegando [ver: gamedev/animacion].
- **Poise / hyperarmor**: no todo golpe dispara reacción. Enemigos pesados absorben (siguen su ataque, quizá con flinch additive sutil) hasta que se acumula daño → stagger. Modelarlo: reacción additive siempre, reacción full-body solo al superar umbral.
- **Transición flinch→hurt en ~4 frames** durante el hitstop (Sakurai): la víctima no salta en seco a la pose de daño, se reparte [ver: gamedev/game-feel].
- **Directional additive** es la técnica clave de eficiencia: una capa additive de "empuje" en la dirección del golpe se suma sobre cualquier estado sin duplicar clips por cada combinación acción×dirección [ver: capas-estados].
- **Knockback anim vs física**: para un empuje ligero, root motion/código + clip; para un lanzamiento aparatoso, transición a ragdoll (sección 6). El VFX de knockback (líneas de velocidad, polvo) lo dispara un anim event.

---

## 6. Muertes: ragdoll vs animado vs híbrido

| Método | Cómo | Pros | Contras |
|---|---|---|---|
| **Muerte animada (keyframe)** | Clip(s) de muerte autorados; se elige por dirección del golpe final | Control artístico total, poses dramáticas, consistente | No reacciona al entorno; se repite; necesita varios clips por dirección |
| **Ragdoll puro** | En el frame de muerte se apaga el Animator y toma control la física | Único cada vez, reacciona a geometría/impulso | Puede verse "trapo sin huesos"/blando; poco control de la lectura |
| **Blend-to-ragdoll (híbrido)** | Arranca un clip de muerte corto y se *blendea* a ragdoll, o se pasa el momento (velocidad) del hueso al Rigidbody | Lo mejor de ambos: pose inicial legible + caída física creíble | Más setup; hay que sincronizar el traspaso hueso→rigidbody |
| **Active ragdoll** | El ragdoll es dirigido por motores hacia una pose objetivo animada | Reacción física + intención animada | Complejo; costo de física continuo |

### Setup de ragdoll (Unity, verificado)
- **Ragdoll Wizard** (`GameObject > 3D Object > Ragdoll…`) mapea los huesos y añade por miembro: **Rigidbody**, **Collider** (box/capsule) y **Character Joint** (con ejes **Twist / Swing 1 / Swing 2** que limitan el rango) [Unity Manual · Ragdoll Wizard].
- Traspaso a la muerte: apagar/`enabled=false` el Animator, `isKinematic=false` en los Rigidbodies, y opcionalmente inyectar la velocidad de los huesos del último frame animado a los Rigidbodies para que el impulso del golpe se conserve (blend-to-ragdoll).
- El VFX/SFX de muerte (colapso, sangre, "poof") lo dispara el anim event del clip de muerte o el código al iniciar el ragdoll.
- Presupuesto: el ragdoll es física continua por hueso; limitar ragdolls activos simultáneos y dormirlos (`sleep`) al asentarse [ver: unity/animacion-unity].

---

## 7. Combos y encadenados: autorar para cancelar/enlazar

Un combo son ataques que **enlazan** dejando cancelar la recovery de uno hacia el startup del siguiente, dentro de una **ventana de cancel**. La responsiveness NO se logra recortando animaciones, sino permitiendo input antes de que terminen [ver: gamedev/animacion].

| Concepto | Qué es | Producción de la anim |
|---|---|---|
| **Cancel window** | Rango de frames de un ataque donde otro input lo interrumpe | Se marca con anim events (open/close) en el clip, o por-estado; suele abrir cerca del fin del active y cerrar antes del recovery total [ver: unity/animacion-unity] |
| **Link / chain** | El fin de un clip fluye al inicio del siguiente sin corte visible | Autorar la pose final de A cerca de la pose inicial de B (o blend corto). Un set de combo se diseña con poses de traspaso compatibles |
| **Committed vs cancelable** | Un ataque puede ser no-cancelable (te comprometes) o cancelable | Decisión de diseño POR frame: el finisher pesado es committed (recovery larga sin cancel); los jabs son cancelables |
| **Buffer** | Encolar el input del combo durante hitstop/recovery y ejecutarlo en el primer frame válido | La anim no lo hace, pero debe *permitirlo*: dejar la ventana y no bloquear con exit time [ver: gamedev/game-feel] |
| **Branching** | El mismo ataque N enlaza a distintos N+1 según input (ligero/pesado/direccional) | Cada rama es una transición attack→attack con Interruption Source = Next State [ver: unity/animacion-unity] |

- **El hitstop ES ventana de cancel natural**: históricamente (SF2) el hitstop extendió la ventana cancelable → nacieron los combos por cancel [ver: gamedev/game-feel]. Aprovecharlo: el confirm del combo cae dentro del freeze del golpe.
- **Poses de traspaso**: diseñar el árbol de combo por sus poses de enlace, no como clips sueltos. Si A termina con el peso adelante y B empieza con peso atrás, el enlace se ve roto — reautorar A o B.
- **Snappy al enlazar**: el blend attack→attack es corto o 0 (transición casi instantánea al startup del siguiente); la suavidad se reserva para volver a idle [ver: unity/animacion-unity].

---

## 8. Armas y su animación: sincronía con el gameplay

Cada tipo de arma tiene su gramática. La constante: los momentos de gameplay (daño, disparo, munición) los marcan **anim events**, no timers paralelos [ver: unity/animacion-unity].

| Arma | Fases de la anim | Frames que se marcan con evento | Notas de producción 3D |
|---|---|---|---|
| **Melee** | windup → swing (active) → recovery | Abrir hitbox (inicio active) · cerrar hitbox (fin active) · SFX de swoosh · encender weapon trail | El arma sigue el arco de la mano; trail solo en active; contacto con hold (sección 2) |
| **Disparo (hitscan/proyectil)** | fire → recoil → settle | Frame de disparo (spawn bala + muzzle flash + SFX) · pico de recoil | Recoil = impulso a un spring-damper reutilizable entre armas [ver: gamedev/animacion]; muzzle flash 1–2 frames vende el disparo más que la bala |
| **ADS (apuntar)** | hip→aim (transición) · aim idle · aim→hip | — (es estado, no evento) | El arma va a un rig de cámara aparte, no 1:1 al esqueleto del cuerpo; view-model tiene sus propios grados de libertad [ver: gamedev/animacion] |
| **Recarga** | sacar cargador → insertar → montar/cerrojo | Ocultar/mostrar mesh del cargador · SFX por sub-fase · frame en que la munición se vuelve efectiva | Las manos siguen el cargador con IK; el cargador es un mesh que se re-parenta (mano ↔ arma). Recarga táctica (con bala) vs vacía (con cerrojo) = clips distintos |
| **Envainar/cambiar** | guardar → sacar | Attach/detach del mesh del arma al hueso de la mano/espalda | Sockets: el arma se parenta a un hueso; el swap se dispara por evento |

- **IK de la mano de apoyo** al guardamanos/empuñadura: mantiene las dos manos coherentes con el arma aunque el clip base no sea perfecto; peso interpolado, nunca 0→1 seco [ver: unity/animacion-unity] [ver: rigging/ik-fk-constraints].
- **Delay mínimo trigger→impacto visible**: la percepción de "arma potente" exige que el flash/impacto salga en el mismo frame o el siguiente al input [ver: gamedev/game-feel].
- **Sincronía anim↔lógica**: el frame donde la munición baja, donde la bala nace, donde el melee daña — todos anclados al clip. Si el clip se re-timea, los eventos siguen pegados a su frame [ver: unity/animacion-unity].

---

## 9. Mocap y librerías para combate (Mixamo, retargeting)

El mocap da peso y realismo "gratis"; el combate estilizado casi siempre lo **retoca a keyframe** en el contacto y el hold (el mocap suaviza justo lo que el golpe necesita crudo) [ver: mocap-librerias] [ver: keyframes-curvas].

- **Retargeting Humanoid (Unity, verificado)**: un mismo clip mueve distintos personajes humanoides sin renombrar huesos, vía el **Avatar** (interfaz de retargeting) y el sistema de **Muscles** (abstracción que normaliza cada hueso a un rango de movimiento, ej. Head-Nod/Head-Tilt −40°..40°), que además impide poses imposibles [Unity Manual · Retargeting, Muscle Definitions]. Esto permite reusar un set de ataques entre varios enemigos humanoides. **Generic** es más barato pero no retargetea entre esqueletos distintos [ver: unity/animacion-unity].
- **Mixamo** (Adobe): auto-rigger (subes el mesh → sale rigged humanoide) + librería de clips mocap (locomoción, melee, reacciones, muertes). Opción **In Place** = quita la traslación del root para que el motor mueva al personaje (equivale a Bake Into Pose XZ). Descarga como **FBX** *con skin* (mesh+anim) o *sin skin* (solo anim, para añadir a un personaje ya rigged). ⚠️ *No verificado en esta sesión* (las páginas de Mixamo no cargaron por WebFetch): confirmar frame rate exacto, reducción de keyframes y formatos vigentes contra la doc de Adobe antes de depender de un valor concreto.
- **Flujo típico**: base mocap/Mixamo para el gross motion → limpieza (romper foot sliding, arreglar arcos) → **pase de keyframe** en las poses de contacto, holds y siluetas de wind-up → exportar clips. La ejecución (limpieza, curvas, export) es fase de editor [aún no documentada].
- Combate rara vez es mocap puro: el peso mocap + la exageración/legibilidad keyframe es el estándar de acción moderno.

---

## 10. El handoff a Unity: qué frames disparan qué

El animador entrega los clips MÁS los frames marcados; el resto lo cablea el implementador [ver: unity/animacion-unity]. Contrato de eventos por clip:

| Frame del clip | Dispara | Garantía |
|---|---|---|
| Inicio del active | Abrir hitbox / spawn de bala / muzzle flash | Anim event |
| Fin del active | Cerrar hitbox | **Además** cerrar en el salir del estado (red de seguridad), no solo por evento — si el clip se interrumpe, el evento del último frame puede no correr [ver: unity/animacion-unity] |
| Frame de contacto | SFX de impacto, trigger de hitstop/shake (juice) | Anim event → el engine amplifica [ver: pipeline/feel-en-unity] |
| Inicio/fin de cancel window | Abrir/cerrar la ventana de combo | Anim event o por-estado |
| Pisadas (walk/run/dash) | Footstep SFX + polvo | Anim event |
| Inicio de windup enemigo | VFX de carga + SFX de telegraph | Anim event |

- **Anclar al clip, no a timers**: los eventos viven en el frame; si el timing del clip cambia, siguen correctos. Un timer paralelo se desincroniza al primer re-timeo [ver: unity/animacion-unity].
- **Todo lo que ABRE tiene cierre garantizado** fuera del evento (al salir del estado), porque un evento en los últimos frames puede saltarse si una transición corta el clip antes [ver: unity/animacion-unity].
- La firma del evento (Unity, verificado): método público en un componente del **mismo GameObject** que el Animator, con 0 o 1 parámetro (float/int/string/Object/AnimationEvent) [Unity Manual · Animation Events].

---

## Reglas prácticas

1. Presupuesta cada ataque en poses: 1 de windup (carga), 1–2 de extensión + el frame de contacto, 1 de follow-through. Escribe los frames antes de posar.
2. Cada wind-up con silueta ÚNICA y legible desde el ángulo de cámara real; si dos ataques comparten silueta, reautora.
3. El peso va al final (follow-through, overshoot+settle), nunca alargando el windup del jugador [ver: gamedev/animacion].
4. Autora el frame de contacto en el punto de máxima velocidad angular; sostenlo 1–3 frames (hold) y haz que coincida con el hitstop del engine.
5. La animación no mueve la hitbox: el collider lo abre un anim event en el active; smear/vibración es solo visual.
6. Weapon trail encendido solo en frames active; marca la zona de peligro real.
7. Root motion por-clip decidido con la tabla de la sección 4: lunge = XZ Bake OFF; ataque en el sitio = XZ Bake ON; no mezcles clips con/sin root motion en el mismo estado sin querer.
8. Hit reactions: additive para daño leve (no corta la acción), full-body direccional (mín. 4 dir) para daño que frena; reparte flinch→hurt en ~4f.
9. Modela poise/hyperarmor: reacción additive siempre, full-body solo al superar umbral de daño.
10. Muertes: blend-to-ragdoll (pose animada corta → física) salvo que necesites lectura 100% controlada; traspasa la velocidad del hueso al Rigidbody para conservar el impulso.
11. Combos: diseña el árbol por sus poses de enlace, no por clips sueltos; blend attack→attack corto o 0.
12. Marca la cancel window con anim events (open/close); deja que el buffer del engine ejecute en el primer frame válido — no recortes la anim.
13. Armas: marca con evento el frame de disparo (bala+flash+SFX), el pico de recoil, y en recarga la sub-fase y el frame de munición efectiva.
14. Recoil/sway como spring-damper additive reutilizable entre armas, no un clip por arma [ver: gamedev/animacion].
15. IK de la mano de apoyo al arma con peso interpolado; el cargador se re-parenta mano↔arma por evento.
16. Mocap de combate = base + pase keyframe en contacto, holds y siluetas; nunca shippees el mocap crudo en los golpes.
17. Retargeting Humanoid para reusar un set de ataques entre enemigos; Generic si no necesitas retarget (más barato).
18. Todo evento que ABRE (hitbox, i-frames) cierra también al salir del estado, no solo por evento del último frame.
19. Ancla SIEMPRE eventos al clip, jamás a timers paralelos.
20. Calibra jugando: cada número heredado de las bases es punto de partida; el final se decide con el mando en la mano [ver: gamedev/game-feel].

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Meter peso alargando el windup del jugador → control gomoso | Peso al final (follow-through/overshoot); startup corto [ver: gamedev/animacion] |
| Frame de contacto sin hold → el golpe "pasa de largo" sin impacto | Hold 1–3f coincidiendo con el hitstop del engine |
| La deformación visual del ataque mueve el collider lógico | Separar transform visual del lógico; hitbox por anim event, no por mesh |
| Dos wind-ups enemigos con silueta parecida | Pose distinta por ataque; sobre-rotar la parte que ataca hasta distinguirse |
| Lunge con in-place + código que patina (foot sliding) | Root motion, o warping sobre root limpio; sincroniza desplazamiento con pasos |
| Mezclar clips con/sin root motion en un estado → saltos de velocidad | Decidir root motion por-estado y ser consistente |
| Un solo clip de reacción para todo → daño ilegible de dónde vino | Reacciones direccionales (4–8) + additive para chip |
| Todo golpe interrumpe al enemigo → se siente sin peso ni amenaza | Poise/hyperarmor: additive siempre, full-body solo al superar umbral |
| Ragdoll puro que se ve "trapo blando" | Blend-to-ragdoll: pose animada corta primero + traspaso de velocidad al Rigidbody |
| Combo diseñado como clips sueltos → enlaces que "saltan" | Poses de traspaso compatibles entre A y B; blend corto |
| Recortar animaciones para ganar responsiveness | Cancel windows + input buffer; la anim completa existe para quien no cancela |
| VFX/SFX/hitbox por timers paralelos al clip | Anim events en el frame; sobreviven a re-timeos [ver: unity/animacion-unity] |
| Evento de cierre en el último frame que a veces no dispara | Cerrar también en el salir del estado (StateMachineBehaviour) |
| Recoil como clip por arma → duplicación y rigidez | Impulso → spring-damper additive compartido |
| Mocap crudo en los golpes → contacto blando, sin snap | Pase keyframe en contacto, hold y wind-up sobre la base mocap |
| Reload sin re-parentar el cargador → cargador flotando/duplicado | Attach/detach del mesh por evento; manos con IK al cargador |

## Fuentes

**Bases sintetizadas (no repetidas, referenciadas):**
- [ver: gamedev/animacion] — anatomía wind-up/strike/recovery con números (anticipación enemiga ~18f@30, jugador 1–3f), telegraphing por capas (Mike Stout), los 12 principios en gameplay (Jonathan Cooper, *Game Anim*), hitstop de Sakurai, frame counts, cancels y buffer.
- [ver: gamedev/game-feel] — hit-stop escalado, screenshake por trauma, knockback/kick, flashes, freeze frames; el "juice" que amplifica el frame de contacto (Swink, Vlambeer, Jonasson/Purho).
- [ver: unity/animacion-unity] — el cableado: Animator, transiciones (Has Exit Time, Interruption Source), blend trees, layers/avatar mask, anim events, StateMachineBehaviour, root motion en el Animator.

**Fuentes web verificadas esta sesión (Unity Manual 6000.2):**
- **Root Motion** (`RootMotion.html`) — Body/Root Transform, Apply Root Motion, Bake Into Pose y Based Upon para Rotation / Position Y / Position XZ, y su uso en lunges e idles.
- **Ragdoll Wizard** (`wizard-RagdollWizard.html`) — componentes por miembro (Rigidbody, Collider, Character Joint) y ejes Twist / Swing 1 / Swing 2.
- **Retargeting** (`Retargeting.html`) — Avatar como interfaz de retargeting; un clip Humanoid sobre varios personajes sin renombrar huesos.
- **Configuring the Avatar** (`ConfiguringtheAvatar.html`) — mapeo de huesos, mínimo ~15 huesos, pestaña Muscles & Settings.
- **Muscle Definitions** (`MuscleDefinitions.html`) — muscles como abstracción de rango de movimiento por hueso (ej. Head-Nod/Tilt −40°..40°), Muscle Group Preview.
- **Animation Events** (`script-AnimationWindowEvent.html`) — añadir evento en un frame; firma (componente en el mismo GameObject, 0–1 parámetro float/int/string/Object/AnimationEvent); uso para footsteps, hitbox, VFX.

**Mencionada, NO verificada esta sesión:**
- **Mixamo** (Adobe) — auto-rigger, librería mocap, opción *In Place*, descarga FBX con/sin skin. Las páginas no cargaron por WebFetch (timeout); frame rate, reducción de keyframes y formatos vigentes deben confirmarse contra la doc de Adobe antes de depender de un valor concreto.
