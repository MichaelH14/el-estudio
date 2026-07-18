# Animación para juegos

> **Cuando cargar este archivo:** al animar personajes/enemigos (sprite o esqueletal), diseñar ataques y su telegraphing, montar state machines/blend trees, o añadir movimiento procedural (lean, bob, recoil, IK). Complementa [ver: game-feel] (impacto/juice) y [ver: arte-direccion] (estilo visual).

## 1. Los 12 principios de Disney en gameplay

Fuente base: *Game Anim* de Jonathan Cooper (adaptación de Thomas & Johnston, *The Illusion of Life*). La regla general: en cinemáticas aplican como en cine; en gameplay chocan con la responsiveness y hay que adaptarlos.

| Principio | Adaptación en juegos | Peso en gameplay |
|---|---|---|
| **Timing** | El centro del game feel: la duración de cada acción define si algo se siente pesado o ligero (`tiempo = distancia/velocidad`) | ⭐⭐⭐ El más importante |
| **Anticipation** | Conflicto directo: diseño la quiere mínima (responsiveness), animación la quiere larga (peso). En el JUGADOR: mínima (hasta 1 frame). En ENEMIGOS: larga = telegraphing | ⭐⭐⭐ Es diseño, no polish |
| **Follow-through & Overlap** | Vende el peso SIN costar responsiveness: el peso se mete al FINAL de la acción, no al inicio. Poses fuertes en el follow-through ayudan a leer la acción | ⭐⭐⭐ |
| **Exaggeration** | "Real life never looks real enough". Debe leerse desde cualquier ángulo de cámara, no solo uno fijo. Mantener consistencia de estilo entre animadores | ⭐⭐⭐ Clave para legibilidad |
| **Squash & Stretch** | Muchos motores no soportan escalar huesos (coste de memoria). Alternativa: extender extremidades en poses rápidas (salto, aterrizaje) sin escalado real | ⭐⭐ |
| **Slow In / Slow Out** | Mismo conflicto que anticipation. Solución de Cooper: arranque inmediato + peso al final (follow-through) | ⭐⭐ |
| **Secondary Action** | Difícil en clips cortos de gameplay; se implementa con animaciones **additive/partial** superpuestas (respiración, gestos de mano) | ⭐⭐ |
| **Arcs** | Extremidades en curvas naturales. El mocap muestra que romper arcs a propósito (giro de cabeza tras un puñetazo) añade realismo | ⭐⭐ |
| **Solid Drawing** | En 3D se reinterpreta: mecánica corporal — centro de masa, balance, cadenas de reacción. Base del posing convincente | ⭐⭐ |
| **Appeal** | Diseño de personaje + pose. Aplica también a enemigos: silueta reconocible = ataque reconocible | ⭐⭐ |
| **Pose to Pose vs Straight Ahead** | Pose to pose gana en juegos: permite iterar sin terminar la animación (todo puede cambiar en desarrollo) | ⭐ Método de trabajo |
| **Staging** | Sobre todo cinemáticas; en gameplay se traslada a level design (layouts que canalizan la mirada) [ver: level-design] | ⭐ |

**Síntesis operativa:** los tres que gobiernan gameplay son **Timing, Anticipation y Follow-through**. El truco maestro (Cooper): responsiveness se logra permitiendo input ANTES de que la animación termine (cancels/buffer), no recortando la animación.

## 2. Anatomía de un ataque: wind-up, strike, recovery

Todo ataque tiene 3 fases (GDKeys, *Anatomy of an Attack*). El jugador tiene una 4ª implícita previa: el **trigger**, que ya consume tiempo antes del primer frame de animación:

1. Proceso mental de decisión del jugador
2. Presión física del botón
3. Latencia del sistema (input polling, frame en vuelo, display)
4. Recién aquí empieza el wind-up de la animación

Por eso el wind-up del jugador debe ser mínimo: el jugador YA pagó su "anticipación" en los pasos 1–3. El enemigo no tiene trigger — su wind-up es el único aviso que recibe el jugador, y por eso debe ser largo.

| Fase | Qué es | Reglas |
|---|---|---|
| **Wind-up / Anticipación** | Preparación que avisa | ÚNICA por ataque (pose distintiva + VFX opcional). Sugiere QUÉ ataque viene |
| **Strike / Active** | El impacto | Pocos frames, instantáneo, dirección clara = "snappy". Weapon trails marcan la zona de peligro |
| **Recovery** | Vulnerabilidad | La ventana de oportunidad del rival: castigar, curarse, huir, recargar. De 1 frame (encadenable) a segundos (castigo garantizado) |

### Números clave (verificados)

- **Anticipación enemiga mínima ≈ 18 frames a 30fps (~0.6s)**. Fórmula GDKeys: `anticipación = tiempo de reacción del jugador (~0.25s / 8f) + duración de la acción defensiva (~10f) + buffer de dificultad`.
- **Anticipación del jugador: tan corta como 1 frame** en un golpe rápido — cuanto antes llega el active, más directo se siente el control.
- **Excepción deliberada — commitment como mecánica**: en Monster Hunter el gameplay gira alrededor de medir el timing de las anticipaciones de ataque (Cooper). Ahí las animaciones largas del jugador SON el diseño: cada input es una apuesta. Válido solo si todo el combate se construye alrededor de ese peso; no lo mezcles con expectativas de acción rápida.
- **Input lag total < 100ms** en acciones críticas (nivel Super Meat Boy, Hollow Knight, CoD MW2). ~160ms ya es perceptible y molesto (GTA IV, Battlefield 3). Revisar: frames muertos al inicio del clip, caídas de FPS, lógica que espera un tick de más.
- Caso real — **Hornet (Hollow Knight)**, timings aproximados en frames @30fps:

| Ataque | Wind-up | Active | Recovery | Intención de diseño |
|---|---|---|---|---|
| Dash | 15f (0.5s) | 10f | 10f | Test de reflejos ajustado |
| Throw | 20f | 20f+15f | 10f | Ventana amplia de contraataque |
| Lasso | 20f | 30f | larga | Momento seguro para curarse |
| Dive | muy larga | media | corta | Alto riesgo, muy telegrafiado |

Patrón que ilustra la tabla: **wind-up, active y recovery son diales independientes** y cada combinación produce un rol distinto de ataque (test de reflejos / ventana de castigo / permiso para curarse / amenaza telegrafiada). Diseña el set de ataques de un enemigo variando esos diales, no inventando animaciones sueltas.

### Telegraphing (Mike Stout, Game Developer)

- La pregunta que cada enemigo de evasión le hace al jugador es **"¿puedes evitar mi daño?"** — el telegraph es la pregunta formulada con claridad. Sin pausa pre-ataque, el daño se siente injusto.
- **Capas de telegraph** (sumar según importancia del ataque): animación (wind-up visible) + sonido (carga, grito) + VFX (partículas acumulándose, flash) + voz ("¡Ahora verás!") + force feedback.
- Contexto manda: juego realista → telegraphs sutiles (montar el arma, voz de mando); juego estilizado → telegraphs teatrales (Mega Man X carga el cañón, jefes de Psychonauts anuncian en voz alta).
- Recovery es la mitad olvidada del telegraphing: comunica CUÁNDO atacar tú. Ataques fuertes del enemigo → recovery larga; ataques débiles → recovery corta.

### Hitstop (Sakurai, columna de Famitsu)

- **Hitstop** = congelar a ambos (atacante y golpeado) unos frames en el impacto para vender la potencia. En Smash: escala con el daño + factores por ataque, con un **tope máximo** para no congelar demasiado con armas potentes.
- Trucos concretos de Smash: transición flinch→hurt repartida en **4 frames** durante el hitstop; el atacante no está 100% congelado sino moviéndose a velocidad minúscula (imperceptible frame a frame); la víctima **vibra** (horizontal en suelo, vertical en aire) pero **las hitboxes no se mueven** — la vibración es solo visual.

## 3. Timing: frames, poses fuertes, snappiness

- **El timing manda sobre el frame count.** 4 frames con holds bien elegidos leen mejor que 12 frames uniformes. Patrón típico pixel art: wind-up rápido (~80ms/frame), **hold del frame de impacto ~300ms**, y hold de anticipación de ataque grande ~400ms antes de soltarlo.
- **Smear frames**: un frame donde el arma/brazo se estira o multiplica vendiendo velocidad — el látigo de Castlevania lo resuelve con ~3 píxeles de smear. Barato y efectivísimo para strikes de 1–2 frames.
- **Snappy vs suave**: gameplay quiere transiciones al active casi instantáneas (snappy); la suavidad se reserva para follow-through, idles y cinemáticas. Sakurai: el "salto" brusco a los startup frames al pulsar botón es correcto — una transición suave ahí se sentiría lenta.
- **Cuphead** demuestra el desacople frame rate de animación vs juego: animado a **24fps "on ones"** (un dibujo por frame) mientras el juego corre a **60fps**. La animación puede ir a su ritmo artístico; la simulación e input, al del hardware.
- Poses fuertes: cada fase debe tener una **silueta legible** en un solo frame (test: pausa cualquier frame del active — ¿se entiende qué pasa?). Cooper: los jugadores leen las poses sostenidas del follow-through más que los frames rápidos del strike.

### Frame counts de referencia por acción (sprites, práctica indie)

| Acción | Frames | Nota |
|---|---|---|
| Idle | 2–4 | Respiración sutil; loop |
| Walk | 4–6 | 8–12 si el estilo pide fluidez |
| Run | 6–8 | Más extremo en poses que walk, no solo más rápido |
| Attack | 3–6 | 1 anticipación + 1–2 extensión (o smear) + 2–3 recovery |
| Jump | 3–5 | Squash despegue + stretch en aire + squash aterrizaje |

Estos números son piso, no techo — con holds bien puestos son suficientes para shippear (la mayoría del indie shippea con esto).

## 4. Sprites (frame a frame) vs esqueletal (Spine y afines)

| Criterio | Frame a frame (sprites) | Esqueletal (Spine/DragonBones/Live2D) |
|---|---|---|
| Coste inicial | Bajo (dibujar y ya) | Alto: trocear el personaje, rig, weights de mesh (~15–60 min por sprite según SPRITETOMESH, arXiv) |
| Coste por animación nueva | ALTO: cada frame se dibuja (walk = 8–12 dibujos; el overhead artístico puede comerse ~80% del tiempo de animación) | Bajo: walk con 4–6 keyframes interpolados |
| Iterar / cambiar diseño | Redibujar TODO el ciclo | Ajustar keyframes; cambiar la skin sin tocar animaciones |
| Memoria / assets | Sprite sheets crecen rápido (file bloat) | Datos de huesos, muy ligeros; mejor para networking |
| Blending / mezclas | No hay: corte seco entre clips | Crossfade, capas, mezclas en runtime |
| Estilo visual | Control total del dibujo, smears, deformación libre por frame | Riesgo de look "de papel recortado" si no se usan meshes/curvas |
| Extras | — | IK, skins intercambiables (customización), retarget de mocap 2D |

**Cuándo cada una** (Charios + foros de Esoteric):
- **Sprites**: pixel art de baja resolución (16×16, 32×32), efectos simples (moneda, vela, explosión), criaturas sin estructura articulada, animaciones únicas no reutilizables. Regla: **"if it doesn't bend, it doesn't need bones"**.
- **Esqueletal**: personajes articulados con **3–4+ animaciones**, varios personajes que comparten rig, customización de equipamiento (skins/attachments en runtime), necesidad de blending suave.
- El caso extremo del frame a frame es **Cuphead**: ~50,000 frames dibujados a mano en el juego base (StudioMDHR), ~25 minutos de trabajo por frame en promedio (dibujar, entintar, escanear, colorear). Con el DLC *The Delicious Last Course* el total sube a **72,000 frames**, cifra que sostiene el récord Guinness ("most hand-drawn frames of animation in a videogame"). Ese es el precio real del look — no lo elijas por accidente.
- Híbrido común y sano: esqueletal para personajes + frame a frame para VFX e impactos.

## 5. Follow-through, secondary motion y overlap: vida gratis

Principio operativo: todo lo que pase DESPUÉS del momento de input es gratis para el gameplay — ahí es donde se mete el peso y la vida.

- **Follow-through**: la acción no muere en seco; el cuerpo/arma continúa y asienta. Cooper: la percepción de peso de un golpe se construye aquí, no alargando el wind-up.
- **Overlap**: no todo llega a la pose final a la vez — capa, pelo, brazo secundario llegan tarde. En esqueletal: retrasar 2–4 frames los huesos hijos respecto a los padres.
- **Secondary motion procedural (cero coste de autor por animación)**: jiggle bones / springs en pelo, tela, accesorios; se calculan solos sobre cualquier animación. En sprites: 1–2 frames extra de "asentamiento" tras el aterrizaje o el golpe.
- **Additive/partial animations** (Cooper): capa superior que suma sobre la base — respiración sobre el idle, flinch de daño sobre la carrera, sway del arma sobre todo. Es la forma estándar de tener secondary action sin duplicar clips.
- Cuidado con el presupuesto: follow-through visual sí, pero si bloquea input demasiados frames, se convierte en recovery de gameplay. Decidir conscientemente qué parte es cancelable.

## 6. Animación procedural básica

Referencias: GDC 2014 "An Indie Approach to Procedural Animation" (David Rosen, Overgrowth) y Little Polygon *Procedural Animation: Locomotion*.

### La idea de Rosen (Overgrowth)
- Con **muy pocas poses clave** (cifra recurrente en writeups del talk: ~13 en total) animó todo un personaje (correr, saltar, pelear): pocas poses fuertes + **interpolación cúbica** entre ellas ≈ resultado casi idéntico a animación keyframeada a mano. La inversión va a la CALIDAD de cada pose, no a la cantidad. ⚠️ El abstract oficial de GDC Vault solo confirma "very few key frames"; la cifra exacta de 13 no se pudo verificar contra la charla completa (de pago), viene de resúmenes de terceros consistentes entre sí — trátala como orden de magnitud, no como dato duro.
- Walk cycle con **2 poses**: un ciclo básico de 4 momentos (contacto izq, paso, contacto der, paso) se comprime en 2 poses de pierna que se espejan para obtener las otras 2. La interpolación cúbica hace el resto.
- El movimiento nace de la física del juego, no al revés: la animación LEE velocidad/aceleración y reacciona (lean al acelerar, inclinación en pendientes). Esto la hace responsive por construcción — nunca hay un clip "en curso" que bloquee el input.

### Modelo mental de la locomoción (Little Polygon)
Un paso es un ciclo de tres eventos físicos — útil para razonar cualquier locomoción, animada o procedural:
1. **Inclinarse hacia adelante** = iniciar una caída controlada
2. **Contacto del pie** = frenar esa caída
3. **Empuje hacia arriba** mientras se recoge el pie trasero

El lean, el bob y el roll de las recetas de abajo son la traducción directa de esas tres fases a osciladores y springs.

### Recetario implementable (fórmulas de Little Polygon, verificadas)

| Efecto | Técnica | Parámetros de partida |
|---|---|---|
| **Lean** (inclinarse al acelerar) | Eje de rotación = `up × aceleración` (cross product), suavizado con damped spring | multiplicador ~0.64, ángulo máx 45°, smoothing ~0.25s |
| **Bob** (cadera/cámara al andar) | Oscilador senoidal sobre la cadera; fase avanza con `velocidad_normalizada * dt` | roll lateral a MITAD de frecuencia del bob vertical (izquierda-derecha = 1 ciclo cada 2 pasos) |
| **Modulación por velocidad** | `speed_norm = min(1, |v| / v_max)` escala amplitud y frecuencia de todo | parado = quieto, sprint = máximo |
| **Recoil de arma** | Impulso por disparo alimentando un **spring-damper** (misma matemática que una suspensión de coche): el muelle devuelve al punto neutro, el damper filtra | la cámara sigue parcialmente el recoil; sway/idle como capas additive reutilizables entre armas |
| **Foot IK simple** | Posición del pie → raycast al terreno → reproyectar y pasar al solver IK (two-bone basta) | evita pies flotando en cuestas/escaleras |
| **Smoothing universal** | Damped spring: `omega = 2/duración`, decae con `e^(-omega*dt)` | fricción rápida: `coef ≈ 4/segundos_de_frenado` |

**Nota de alcance — first-person view-model (armas en primera persona):** ADS (aim-down-sights), viewkick y sway de un shooter FPS son un subcaso con más grados de libertad (el arma no va ligada 1:1 al esqueleto del cuerpo, sino a un rig de cámara aparte). Las charlas específicas de Overwatch sobre esto (GDC 2017) no se pudieron extraer con detalle técnico verificable — la receta de recoil/sway de esta tabla (spring-damper) es la base común y válida, pero un FPS serio necesita profundizar aparte en el rig de view-model.

Damped spring de referencia (Little Polygon), el smoothing universal para lean/recoil/cámara:

```
// suaviza Value hacia Target con muelle críticamente amortiguado (sin rebote)
Omega  = 2.0 / DuracionSegundos
Exp    = e^(-Omega * DeltaTime)
Change = Value - Target
Temp   = (Speed + Omega * Change) * DeltaTime
Speed  = (Speed - Omega * Temp) * Exp
Value  = Target + (Change + Temp) * Exp
```

- Orden de capas típico: clip base (o poses interpoladas) → additive (respiración, sway) → procedural (lean, bob, recoil) → IK (pies, manos al arma) — el IK siempre al final, corrige sobre el resultado.
- La animación procedural NUNCA debe alterar hitboxes/posición lógica sin decisión explícita (lección del hitstop de Sakurai: la vibración es visual, las hitboxes quietas).

## 7. Blend de animaciones y árboles de estados (concepto)

Aplica igual en Unity (Animator), Unreal (AnimBP), Godot (AnimationTree) — aquí solo el concepto.

- **State machine** = estados mutuamente excluyentes (no puedes estar walking y jumping a la vez): idle/locomotion/airborne/combat. Cada estado reproduce un clip o un blend space; las **transiciones** llevan condición (`speed > x`, `IsGrounded`, "animación terminó", trigger de evento) y **blend time**.
- **Blend tree / blend space** = mezcla CONTINUA dentro de un estado lógico: idle→walk→run→sprint según `speed` (1D), o dirección+velocidad (2D). No es una transición, es un dial.
- **Todo sistema de locomoción de producción usa ambos**: state machine por fuera, blend tree dentro del estado de locomoción.
- **Blend times**: ~0.2s es el punto de partida para locomoción; combate quiere menos (snappy, a veces 0 hacia el active); volver a idle tolera más (suave). El blend time ES parte del game feel — revisarlos uno a uno, no dejar el default.
- **Layers**: cuerpo completo en la capa base + capa superior (torso/brazos) para disparar/gesticular mientras se corre, con máscara por huesos. Es la versión sistematizada del additive de Cooper.
- **Combate**: modelar explícitamente qué estados son *committed* (no cancelables) vs *interrumpibles*, con ventanas de cancel definidas por frames/eventos — esto es diseño [ver: mecanicas-sistemas], no un detalle técnico.
- Escala: con 15+ estados, jerarquizar en submáquinas por dominio (Locomotion, Combat, Reactions). Estabilizar los estados ANTES de cablear transiciones.
- Eventos de animación (anim events / notifies): el frame activo del ataque, el paso que suena, el spawn del VFX — se marcan EN el clip, no con timers paralelos, para que sobrevivan a cambios de timing.

Esqueleto mínimo de un personaje de acción (patrón, no motor):

```
[Idle/Locomotion]  ← blend space 1D por speed (idle→walk→run)
   │ !IsGrounded            │ AttackPressed
   ▼                        ▼
[Airborne]              [Attack N]  ← committed hasta ventana de cancel
   │ Land (trigger)         │ fin de clip o cancel → combo/locomotion
   ▼                        ▼
[Land] → auto → [Idle/Locomotion]
[HitReaction]  ← interrumpe casi todo; vuelve a locomotion
```

Con eso + una capa superior enmascarada (torso) cubres la mayoría de juegos de acción; lo demás son refinamientos.

## Reglas prácticas

- [ ] Presupuesta cada ataque en 3 fases explícitas (wind-up / active / recovery) con frames escritos ANTES de animar.
- [ ] Anticipación de enemigo ≥ reacción del jugador (~0.25s) + duración de su acción defensiva + buffer de dificultad. Punto de partida: ~18f @30fps.
- [ ] Anticipación del jugador: mínima (1–3 frames en golpes rápidos). El peso se vende en el follow-through, nunca alargando el startup del jugador.
- [ ] Input-to-visual < 100ms en acciones core. Mide (grabación a 60fps contando frames), no asumas.
- [ ] Cada wind-up enemigo con pose ÚNICA y silueta distinta — si dos ataques comparten wind-up, el jugador no puede elegir respuesta.
- [ ] Telegraph en capas: animación + SFX + VFX; súmalas según lo letal del ataque.
- [ ] Recovery calibrada al riesgo: ataque enemigo fuerte → recovery larga (ventana de castigo); débil → corta.
- [ ] Hitstop en golpes importantes (pocos frames, escalado con daño, con tope). Congela lo visual, no las hitboxes.
- [ ] Test de silueta: pausa en cualquier frame del active — si no se lee la acción, falta pose fuerte o smear.
- [ ] Timing sobre frame count: holds desiguales (impacto ~300ms, windup corto) antes que añadir dibujos.
- [ ] Sprites: walk 4–6, attack 3–6, idle 2–4 frames como base; smear frame para strikes veloces.
- [ ] Elige esqueletal si el personaje tiene 3–4+ animaciones o habrá customización; frame a frame si es pixel art low-res, VFX o "no dobla".
- [ ] Responsiveness = cancels y ventanas de input buffer, no animaciones cortadas a lo bruto.
- [ ] Secondary motion procedural (springs/jiggle) para pelo/tela/accesorios: vida gratis, cero clips extra.
- [ ] Capa additive para respiración/sway/flinch en vez de duplicar clips por estado.
- [ ] Lean por aceleración (`up × accel` + spring) y bob senoidal modulado por velocidad: 20 líneas que transforman el feel de la locomoción.
- [ ] Recoil = impulso → spring-damper, no clips por arma; sway/idle additive reutilizables entre armas.
- [ ] IK de pies al final del stack de animación; raycast al suelo por pie.
- [ ] Revisa cada blend time a mano (~0.2s locomoción, menos en combate); el default del motor no es una decisión.
- [ ] Eventos de gameplay (frame activo, sonidos, VFX) anclados al clip con anim events, no con timers externos.

## Errores comunes

| Error | Antídoto |
|---|---|
| Meter peso alargando el wind-up del JUGADOR → control gomoso | El peso va al final (follow-through, hitstop, screen shake); startup corto siempre |
| Enemigo ataca sin pausa previa → daño que se siente injusto | Pre-attack delay obligatorio; fórmula de anticipación mínima (sección 2) |
| Todos los wind-ups del enemigo parecidos → jugador no puede leer | Una pose distintiva por ataque; exagerar hasta que se distingan en silueta |
| Elegir frame a frame "porque se ve mejor" sin presupuestarlo | Cuphead costó ~25 min/frame y 50,000 frames; calcula tus dibujos totales antes de decidir |
| Esqueletal con piezas rígidas → look "marioneta de papel" | Meshes con weights, curvas de interpolación, frames de smear dibujados para strikes |
| Interpolación uniforme entre keyframes → animación flotante sin peso | Holds desiguales + ease agresivo hacia el impacto; snappy al active, suave al salir |
| Recortar animaciones para ganar responsiveness | Ventanas de cancel + input buffer; la animación completa sigue existiendo para quien no cancela |
| Animación procedural que mueve colliders/hitboxes sin querer | Separar transform visual del transform lógico; vibración/bob solo en el visual |
| Blend times por defecto en todo el Animator/AnimBP | Pasada dedicada de blend times; combate más corto que locomoción |
| Transiciones cableadas antes de estabilizar los estados | Primero estados sólidos y nombrados por dominio; jerarquizar a partir de ~15 estados |
| VFX/sonido/hitbox activados por timers paralelos al clip | Anim events en el propio clip: sobreviven a cambios de timing |
| Secondary action animada a mano en cada clip | Additive layers + springs procedurales; se escribe una vez, aplica a todo |
| Copiar el peso de Monster Hunter/Souls en un juego de acción rápida (o viceversa) | El commitment de animación es una decisión de identidad del combate: elige un punto del espectro snappy↔pesado y aplica TODO el juego a ese punto |

## Fuentes

- **The 12 Principles of Animation (In Video Games)** — Jonathan Cooper, extracto de *Game Anim: Video Game Animation Explained* (gameanim.com / Gamasutra, 2019) — el canon de los 12 principios de Disney traducidos a juegos, con los conflictos gameplay-vs-estética y sus soluciones.
- **Keys to Combat Design: Anatomy of an Attack** — GDKeys — la mejor fuente numérica sobre fases de ataque: fórmula de anticipación mínima, timings de Hornet (Hollow Knight), umbrales de input lag.
- **Enemy Attacks and Telegraphing** — Mike Stout (Game Developer/Gamasutra) — reglas de telegraphing por capas y la pregunta "¿puedes evitar mi daño?"; ejemplos de Psychonauts y Mega Man X.
- **Thinking About Hitstop** — Masahiro Sakurai, columna de Famitsu vol. 490 (trad. Source Gaming, 2015) — mecánica exacta del hitstop en Smash Bros.: escalado, tope, vibración visual con hitboxes fijas.
- **Animation Bootcamp: An Indie Approach to Procedural Animation** — David Rosen (Wolfire Games), GDC 2014 — ~13 keyframes para todo un personaje; interpolación cúbica entre poses; lean por aceleración. Consultado vía GDC Vault, resumen de gameanim.com y writeups derivados.
- **Procedural Animation: Locomotion (Part 1)** — Little Polygon (blog) — fórmulas implementables: lean con cross product y spring, osciladores de cadera, foot IK, parámetros concretos.
- **Phaser: Spritesheet vs Skeletal Animation** — Charios (blog técnico) — comparación de costes reales sprite vs esqueletal, frame counts, regla "if it doesn't bend, it doesn't need bones".
- **Spine** — Esoteric Software (sitio oficial) — capacidades de la animación esqueletal 2D: meshes con weights, IK, skins en runtime, runtimes por motor.
- **SPRITETOMESH** (paper, arXiv 2026) — dato del cuello de botella de producción esqueletal: 15–60 min de creación de mesh por sprite.
- **Cuphead: proceso de animación** — cobertura de GamesRadar ("The Making of Cuphead"), Guinness World Records (récord #508061) y VGMS — ~50,000 frames a mano en el juego base (72,000 con el DLC, cifra del récord Guinness), ~25 min/frame, 24fps "on ones" desacoplado del juego a 60fps.
- **Animation State Machine: UE5 + Unity** — MoCap Online — conceptos motor-agnósticos: estados vs blend spaces, blend times (~0.2s), submáquinas jerárquicas, estados committed vs interrumpibles.
- **Guías de animación pixel art** — Sprite-AI (blog) — frame counts típicos por acción, holds desiguales, smear frames (⚠️ fuente de menor autoridad; los números coinciden con la práctica indie estándar).
