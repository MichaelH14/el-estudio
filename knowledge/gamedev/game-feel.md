# Game feel y juice

> **Cuando cargar este archivo:** al implementar o pulir cualquier interacción en tiempo real — movimiento de personaje, combate, impactos, cámara, feedback de UI de juego — o cuando el juego "funciona pero se siente muerto/flotante/blando" y hay que diagnosticar por qué.

## 1. Qué es game feel (Steve Swink)

Definición de Swink (*Game Feel: A Game Designer's Guide to Virtual Sensation*, 2008): **control en tiempo real de objetos virtuales en un espacio simulado, con interacciones enfatizadas por polish**. Es la intersección de tres componentes — si falta uno, no hay game feel en sentido estricto:

| Componente | Qué es | Umbral / detalle |
|---|---|---|
| **Real-time control** | El juego responde dentro del "correction cycle" del jugador: percibir → decidir → actuar → nuevo feedback | Respuesta en **< 100 ms** desde el input; por encima, el jugador percibe lag y el feel se rompe |
| **Simulated space** | Mundo 2D/3D con movimiento y colisión: velocidad, gravedad, peso, física | Sin colisiones/espacio, hay control pero no "sensación física" |
| **Polish** | Efectos que amplifican sentidos: animación, partículas, sonido, shake | No cambia la mecánica; cambia la *percepción* de la mecánica |

Consecuencias prácticas:
- El feel es **percepción de fisicalidad**: peso, tracción, inercia. Se construye con los tres componentes a la vez — arreglar solo polish sobre un control lagueado no salva nada.
- El libro aplica sobre todo a géneros de acción (plataformas, shooters, racing); en juegos por turnos o de puzzle sin timing, el marco aplica parcialmente (queda el polish y la respuesta de UI).
- Diagnóstico: si algo "se siente mal", revisar en orden: (1) latencia input→respuesta visible, (2) curvas de aceleración/física del avatar, (3) capa de polish. [ver: animacion] [ver: ux-ui-onboarding]

## 2. El repertorio de juice

"Juice" (Jonasson/Purho): **máximo output por mínimo input** — cada acción del jugador dispara feedback abundante sin cambiar las reglas del juego. Repertorio base:

| Técnica | Qué comunica | Cómo se hace bien |
|---|---|---|
| **Screenshake** | Impacto, potencia, peso | Sistema de trauma + Perlin noise (sección 4). Nunca lineal con el evento: shake = trauma² o trauma³ |
| **Hit-stop / freeze frames** | El golpe CONECTÓ | Congelar a ambos (atacante y víctima) 2–20 frames según fuerza del golpe (sección 3) |
| **Squash & stretch** | Peso, elasticidad, velocidad | Deformar según velocidad (estirar en dirección de movimiento) y al impactar (aplastar); conservar volumen: si escalas x×1.3, escala y×~0.7. Volver con tween elástico. [ver: animacion] |
| **Partículas** | Materialidad, permanencia | Distintas por superficie/material; chispas al impacto, humo al destruir, trail tras objetos rápidos. Los restos que QUEDAN en el suelo (permanence) valen más que los que desaparecen |
| **Flashes** | Daño recibido/infligido | Sprite a blanco 1–3 frames al recibir hit; flash de pantalla solo para eventos mayores (parpadeos frecuentes de pantalla completa fatigan y son riesgo de fotosensibilidad) |
| **Knockback** | Fuerza del golpe, dirección | Empujar a la víctima en la dirección del golpe; también micro-retroceso del ATACANTE/cámara al disparar (kick). Vlambeer: el arma empuja al jugador hacia atrás al disparar |
| **Números flotantes** | Magnitud del daño, progresión | Aparecen en el punto de impacto, suben y desvanecen con ease-out; críticos más grandes/otro color; usar object pooling si hay muchos. Convención de ARPGs/RPGs — opcional en juegos que quieren ocultar la matemática |
| **Muzzle flash / anticipación** | El disparo/acción ocurrió YA | 1–2 frames de flash en la boca del arma venden el disparo más que la bala misma |
| **Sonido por evento** | Confirmación instantánea de TODO | Cada acción con su SFX; variar pitch en hits sucesivos (sección 7) |

Regla de dosificación del talk de Jonasson/Purho: añadir más feedback del que parece razonable y luego recortar — es más fácil calibrar bajando que subiendo desde cero.

## 3. Hit-stop en detalle

Fuente principal: columna de Sakurai en Famitsu (vía Source Gaming) + SmashWiki + análisis de Celia Wagar (CritPoints).

- **Qué hace**: congela a atacante y víctima en el frame de colisión. Vende que el golpe ocurrió, da a los ojos tiempo de registrarlo, y hace el impacto más potente.
- **Escala con el daño**: la fórmula exacta varía por juego de la saga (no hay "una" fórmula única) pero la forma es siempre la misma — constante base + daño/divisor, todo multiplicado por factores del ataque, con floor en cada paso: Melee `⌊⌊⌊d/3 + 3⌋·e⌋·c⌋`; Brawl/Smash 4 `⌊⌊(d·0.3846 + 5)·h·e⌋·c⌋` (h = multiplicador propio del move, e = eléctrico, c = crouch-cancel). **Cap duro**: 20 frames en Melee, 30 frames desde Brawl en adelante (20 para la víctima si hace crouch-cancel). Traducción práctica para un juego propio: **base fija (3–6 frames) + daño/divisor, con multiplicador por tipo de golpe y un cap duro** para que armas fuertes no congelen el juego.
- **Calibración por ataque** (Sakurai): la punta de la espada de Marth tiene más hitstop que el resto; proyectiles llevan hitstop REDUCIDO (disparan muchos — congelar cada uno arruinaría el ritmo); ataques eléctricos llevan hitstop aumentado.
- **Vibración durante el freeze**: en Smash el atacante también vibra; personajes en tierra vibran horizontal, en aire vertical. La víctima no está congelada del todo: transición de 4 frames de flinch a animación de daño.
- **Efecto secundario histórico**: en Street Fighter 2, el hitstop (~10 frames congelando a ambos) extendió la ventana de cancel de los normales (5 primeros frames cancelables) → nacieron los "2-in-1 cancels" y los combos por cancel. El hitstop también es la ventana natural para hit-confirm en fighting games modernos (SF6: golpes pesados = más hitstop = más tiempo de confirmar).
- **En un action game genérico**: empezar con 2–4 frames en golpes normales, 8–15 en golpes fuertes/kills, y aplicar time-scale 0 (o casi 0) solo a los implicados, no a partículas/cámara — que el mundo siga vivo alrededor del freeze.

## 4. Screenshake bien hecho (sistema de trauma)

Fuente: Squirrel Eiserloh, "Math for Game Programmers: Juicing Your Cameras With Math" (GDC 2016). El screenshake ingenuo (offset random proporcional al evento) se siente barato. El sistema correcto:

```
trauma ∈ [0,1]           // estado único de la cámara
evento dañino → trauma += 0.2..0.5 (clamp a 1)
trauma decae LINEALMENTE con el tiempo
shake = trauma² (o trauma³)   // mapeo perceptual no lineal
```

Por qué trauma² / trauma³: percepción no lineal — con trauma³, trauma 0.3 → 3% de shake, 0.6 → 22%, 0.9 → 73%. Golpes pequeños apenas mueven; golpes grandes explotan. Y los eventos se ACUMULAN (dos explosiones seguidas = más trauma), en vez de pisarse.

Aplicación del shake:

```
// 2D: traslación + rotación (la combinación es lo que se siente bien)
angle   = maxAngle  * shake * noise1(seed,  t*freq)
offsetX = maxOffset * shake * noise1(seed2, t*freq)
offsetY = maxOffset * shake * noise1(seed3, t*freq)

// 3D: SOLO rotacional (yaw/pitch/roll); trasladar la cámara en 3D
// atraviesa geometría y se siente fatal
yaw = maxYaw * shake * PerlinNoise(seed, t)
```

- **Perlin/smooth noise, no random puro**: se siente mejor (movimiento continuo, no teletransporte por frame), respeta pausa y slow-motion (es función del tiempo), permite ajustar frecuencia, y es reproducible en replays.
- Veredicto de Eiserloh por dimensión: 2D rotacional solo = "kinda lame", 2D traslacional = "nice", **2D trasl.+rot. = awesome**; 3D traslacional = "super lame", **3D rotacional = nice**.
- Complementos de Vlambeer: además del shake, **camera kick** (empujón direccional de la cámara en la dirección del disparo/impacto) y recoil del jugador. Shake ≠ kick: el shake es ruido, el kick es direccional.
- Accesibilidad: exponer slider/toggle de screenshake. El conflicto visual-vestibular (la cámara se mueve, el cuerpo no) marea a parte de los jugadores (Keren, sección 6).

## 5. Tweening y easing

Nada que se mueva por código debe moverse linealmente (salvo intención deliberada). Familias estándar (easings.net, funciones de Penner) y cuándo usar cada una:

| Curva | Carácter | Úsala para |
|---|---|---|
| **Linear** | Mecánico, muerto | Casi nunca; rotaciones continuas, cintas transportadoras |
| **Sine / Quad out** | Suave, discreto | Movimiento de UI, fades, cámaras — el default seguro |
| **Cubic / Quart / Quint out** | Arranque explosivo, frenado suave | Respuesta a input: lo que el jugador dispara debe empezar RÁPIDO (ease-out = responsivo) |
| **Expo out** | Latigazo | Popups, apariciones dramáticas |
| **Ease-in (cualquiera)** | Acelera hacia el final | Salidas, anticipación, objetos que caen/escapan — nunca para responder a input (se siente lag) |
| **Back (out)** | Overshoot: pasa y regresa | Botones, coleccionables, spawn de piezas — juguetón |
| **Elastic (out)** | Oscilación de resorte | Squash&stretch de retorno, wobble de la bola/paddle |
| **Bounce (out)** | Rebotes físicos | Objetos que caen al suelo, drops |

Heurísticas:
- **Regla de oro**: respuesta a input = ease-out (rápido→lento); anticipación/salida = ease-in; el inOut para movimientos autónomos de cámara/cinemáticas.
- Duraciones de juice: cortas. 100–300 ms para feedback de golpe/UI; más de ~400 ms en algo frecuente se vuelve fricción.
- Todo tween interrumpible: si el evento se repite antes de acabar el tween, reiniciar o encadenar desde el valor actual, nunca desde el valor "ideal" (evita pops).
- En el demo de Jonasson/Purho casi todo el juice ES tweening: bloques que caen rotando y encogiéndose, paredes de goma, la bola que se estira según velocidad y rota hacia su dirección, wobble tras impacto, todos los bloques reaccionando un poco a cualquier impacto.

## 6. Cámaras

### 2D — vocabulario de Itay Keren ("Scroll Back", GDC 2015)

Tres pilares que toda cámara debe balancear: **atención** (mostrar lo importante), **interacción** (no robar sensación de control) y **confort** (no marear: el conflicto visual-vestibular causa náusea).

| Técnica | Qué hace | Ejemplo |
|---|---|---|
| **Position-locking** | Cámara clavada al jugador | Terraria; simple pero nervioso si el avatar vibra |
| **Camera-window (deadzone)** | El jugador se mueve libre dentro de una ventana; la cámara solo sigue cuando toca el borde | Jump Bug, Sonic |
| **Lerp-smoothing** | Interpolación continua cámara→objetivo; elimina arranques bruscos | Super Meat Boy |
| **Physics-smoothing** | La cámara es una entidad con aceleración propia que persigue al objetivo | Never Alone |
| **Lookahead (projected-focus)** | Adelanta la cámara extrapolando la velocidad del jugador: se ve lo que VIENE | Luftrausers |
| **Dual-forward-focus** | Dos anclas; al girar de dirección la cámara transiciona para mostrar más espacio hacia delante | Super Mario World, Cave Story |
| **Platform-snapping** | La vertical solo se recentra al ATERRIZAR, no durante el salto | Super Mario World, Rayman |
| **Speedup zones** | La cámara acelera si el jugador corre hacia el borde | Super Mario Bros (~25% off-center) |
| **Region-based anchors** | Cada zona del nivel define su encuadre/ancla | Donkey Kong Country, Mushroom 11 |
| **Cue-focus / attractors** | Objetos importantes (jefes, secretos) atraen el encuadre gradualmente | Insanely Twisted Shadow Planet, Limbo |
| **Position-averaging / zoom-to-fit** | Multi-target: centrar el promedio y ajustar zoom para encuadrar a todos | Smash Bros, Samurai Gunn |
| **Manual control** | Input dedicado para mirar (abajo/arriba, mira del ratón) | Spelunky (agacharse mira abajo), Jazz Jackrabbit 2 |

Receta base para un plataformas 2D: **deadzone horizontal + lookahead en la dirección de movimiento + platform-snapping vertical + lerp-smoothing sobre todo**. Nunca mover la cámara frame-perfect con cada micro-movimiento del avatar.

### 3D y smoothing genérico (Eiserloh)

- Seguimiento: **asymptotic averaging** — `pos += (target - pos) * f` por frame. A 60 FPS: f=0.01 lento, f=0.1 razonablemente rápido, f=0.5 casi instantáneo. Multiplicar por timeScale para respetar slow-motion. (Nota: este lerp por frame es frame-rate-dependent; con delta variable usar la forma con `1-pow(1-f, dt*60)` o smooth-damp del engine.)
- Follow-cam 3D: deadzone y lookahead aplican igual (en el plano de la pantalla); shake SOLO rotacional; colisión de cámara con geometría antes que clipping.
- Todo movimiento de cámara no comandado por el jugador debe ser lento, suave y predecible; los movimientos bruscos se reservan como lenguaje de impacto (shake/kick).

## 7. Sonido: la mitad del feel

Dicho de la industria (heredado del cine, atribuido a George Lucas): "el sonido es la mitad de la experiencia" — el porcentaje exacto es retórico, el efecto es real y demostrable: en el demo de Jonasson/Purho, añadir solo SFX transforma la percepción de fisicalidad del juego más que cualquier efecto visual individual. El audio es además el feedback de latencia más baja que percibe el jugador.

Reglas (Jonasson/Purho + audiogamejam.org):
- **Todo evento de gameplay suena**: golpe, salto, aterrizaje, pickup, disparo, muerte, click de UI. Un evento mudo se siente roto.
- **Sonido distinto por material/contexto**: pared ≠ bloque ≠ paddle. La variación vende el mundo físico.
- **Variar pitch** (±5–15%) en sonidos repetidos para evitar la metralleta monótona; Jonasson/Purho suben el pitch en hits sucesivos para crear efecto armónico ascendente (combo que "canta").
- **Capas**: un impacto gordo = golpe seco + cuerpo grave + cola (debris/ring). Vlambeer: bajarle graves ("more bass") a los disparos los hace sentir más potentes.
- **Prioridad y mezcla**: los sonidos de feedback del JUGADOR dominan la mezcla; ducking de música en momentos clave; limitar voces simultáneas del mismo SFX (no 30 explosiones idénticas a la vez).
- **Consistencia**: el mismo evento siempre suena reconocible — el jugador aprende a jugar de oído (también es accesibilidad).
- **Latencia mínima**: el SFX dispara en el mismo frame que el evento; en web/móvil, pre-cargar y usar el API de baja latencia (Web Audio, no tags `<audio>`). [ver: audio]

## 8. Input feel

### Forgiveness: mentir a favor del jugador (Celeste, Maddy Thorson)

Las 10 mecánicas de perdón de Celeste — todas amplían ventanas de timing/posición a favor del jugador. Un juego "difícil pero justo" está lleno de estas trampas invisibles:

| Mecánica | Qué hace |
|---|---|
| **Coyote time** | Puedes saltar durante unos frames DESPUÉS de dejar el borde (valor típico en la práctica: ~0.05–0.15 s; Celeste no publica la cifra exacta) |
| **Jump buffering** | Si pulsas salto un poco antes de aterrizar, el salto sale en el frame exacto del aterrizaje |
| **Apex con media gravedad** | Manteniendo el botón, la cima del salto tiene gravedad reducida a la mitad → más tiempo de ajuste en el aire |
| **Corner correction (salto)** | Si la cabeza golpea una esquina, el juego te desliza lateralmente para rodearla |
| **Corner correction (dash)** | Dash lateral que roza una esquina te sube encima de la plataforma |
| **Semi-solid popping** | Atravesar plataforma semisólida en dash te coloca encima |
| **Lift momentum storage** | El impulso de una plataforma móvil se conserva unos frames tras dejar de moverse: el salto sigue saliendo boosted |
| **Wall-jump leniency** | Wall jump válido hasta a 2 px de la pared; super wall-jump hasta 5 px |
| **Stamina refund** | Ventana para convertir un salto vertical costoso en wall jump horizontal |

Filosofía: el jugador nunca ve estas mecánicas; solo siente que el juego "responde a lo que quiso hacer". Cuando el input del jugador está a 1 frame o 1 píxel de funcionar, **hacer que funcione**.

- Buffering en general: aceptar y encolar inputs durante estados que no los admiten (aterrizando, en hitstop, en recovery) y ejecutarlos en el primer frame válido. En fighting games el hitstop mismo actúa de ventana de buffer (SF2 → cancels). Nunca descartar un input por llegar 2 frames antes.

### Aceleración y curvas de movimiento

- El feel de un avatar vive en sus curvas: tiempo hasta velocidad máxima, fricción al soltar, cambio de dirección (turn-around) más rápido que el arranque. Responsivo = acelerar rápido (pocos frames a v-max) y frenar rápido; "pesado/flotante" = curvas largas — es decisión de diseño, no error, pero elígela conscientemente (Swink: la simulación ES parte del feel tanto como el polish).
- Gravedad asimétrica estándar en plataformas: caída más rápida que subida, y apex flotado (Celeste) — el salto simétrico "de física real" se siente globo.

### Deadzones de stick (Josh Sutphin, "Doing Thumbstick Dead Zones Right")

| Tipo | Qué hace | Cuándo |
|---|---|---|
| **Axial** | Deadzone por eje independiente | Facilita movimiento puro en un eje; distorsiona diagonales |
| **Radial** | Descarta el vector si su magnitud < umbral | Correcto direccionalmente, pero salta de 0 al umbral (escalón) |
| **Scaled radial** | Radial + remapear magnitud: del borde de la deadzone a 1.0 se remapea a 0→1 | **El default correcto para movimiento analógico** — arranque suave sin drift |
| **Bowtie** | La deadzone del eje contrario crece con el input del eje dominante | Apuntado fino donde importa mantener línea recta |

- Tamaño típico: ~0.2–0.25 de radio (el default recomendado de XInput para el stick izquierdo ≈ 0.24). Sin deadzone hay drift; sin remapeo (radial puro) hay escalón perceptible.
- Exponer sensibilidad/deadzone en opciones si el juego es de precisión.

## 9. Las charlas canon, destiladas

### "Juice it or lose it" — Martin Jonasson & Petri Purho (GDC Europe 2012)

Demo: un clon de Breakout transformado por capas de juice sin tocar una regla del juego. Su repertorio, en orden de impacto:
1. **Tweening todo** (bloques que entran/caen con ease, paredes de goma, bola que rota y se estira con la velocidad, wobble tras impacto).
2. **Sonido** (por tipo de colisión + pitch ascendente en rachas) y **música**.
3. **Partículas** (por superficie, trail de la bola, restos que caen).
4. **Screen shake** (con noise, no random).
5. **Color y flashes** (bola a blanco al impactar, bloques que se oscurecen al morir).
6. **Personalidad** (ojos en el paddle — barato, efecto desproporcionado).

Principios: máximo output por mínimo input; el juice se pone encima de un juego que ya funciona (pulir al final, no en prototipo); pasarse y luego recortar.

### "The art of screenshake" — Jan Willem Nijman, Vlambeer (INDIGO Classes 2013)

Demo: un shooter 2D soso → excelente en ~30 pasos acumulativos. Los pasos, agrupados:
- **Base**: animaciones y sonido; enemigos con menos HP (mueren rápido = más feedback); más cadencia de fuego; más enemigos.
- **Armas que se sienten armas**: balas más grandes y más rápidas; muzzle flash; MENOS precisión (spread aleatorio = orgánico); delay mínimo entre trigger e impacto visual; recoil visual del arma; casquillos que saltan y QUEDAN en el suelo.
- **Impactos**: efecto + animación de impacto; knockback del enemigo; hit-stop breve al matar/recibir daño (su ejemplo: un `sleep(20)` — pausa de milisegundos); explosiones grandes con aleatoriedad.
- **Cámara**: lerp hacia delante de la mirada (posición según hacia dónde apuntas), screenshake, camera kick al disparar, retroceso del jugador al disparar.
- **Permanencia**: cadáveres, casquillos, cráteres y humo que PERMANECEN — el mundo recuerda lo que hiciste.
- **Sonido**: más graves.
- **Y el cierre**: nada de esto sustituye el diseño — la muerte del jugador debe significar algo y el juego debe estar balanceado; el juice amplifica un buen juego, no arregla uno malo (misma advertencia del contra-talk "Don't Juice It or Lose It").

## Reglas prácticas

1. Input→respuesta visible en < 100 ms; el SFX en el mismo frame del evento.
2. Ease-out para todo lo que responde a input; ease-in solo para salidas/anticipación; nada lineal salvo intención.
3. Tweens de feedback: 100–300 ms, interrumpibles, reiniciando desde el valor actual.
4. Todo evento de gameplay tiene sonido; pitch aleatorizado ±5–15% en SFX repetidos.
5. Screenshake con sistema de trauma: trauma ∈ [0,1], decae lineal, shake = trauma², aplicado con Perlin noise.
6. Shake 2D = traslación + rotación; shake 3D = solo rotación.
7. Añadir camera kick direccional además del shake en disparos/impactos fuertes.
8. Hit-stop en cada golpe que conecta: 2–4 frames normal, 8–15 fuerte, con cap; reducido en proyectiles frecuentes.
9. Flash blanco de 1–3 frames en el sprite golpeado; flashes de pantalla completa solo en eventos mayores.
10. Squash & stretch con conservación de volumen y retorno elástico.
11. Partículas y restos con permanencia: el mundo conserva marcas de lo ocurrido (con pooling y cap de entidades).
12. Cámara 2D: deadzone + lookahead + snap vertical al aterrizar + lerp; jamás clavada al pixel del avatar.
13. Coyote time y jump buffering en TODO juego con salto — no son opcionales.
14. Corner correction: si el jugador falla por 1-2 px, empujarlo a que funcione.
15. Gravedad asimétrica: caer más rápido que subir; apex flotado si se mantiene el botón.
16. Sticks analógicos: scaled radial deadzone (~0.2–0.25) con magnitud remapeada.
17. Buffer de inputs durante estados bloqueados; ejecutar en el primer frame válido.
18. Opciones de accesibilidad: toggles/sliders para screenshake y flashes.
19. Juicear al final, sobre un core loop que ya funciona; pasarse y recortar.
20. Calibrar jugando: cada valor de este archivo es punto de partida, el número final se decide con el mando en la mano.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Screenshake lineal y por random puro (cámara teletransportándose cada frame) | Sistema de trauma + Perlin noise; magnitud = trauma² |
| Shake traslacional en 3D (atraviesa paredes, marea) | Solo rotacional en 3D |
| Shake/flashes sin opción de desactivar | Sliders de accesibilidad; el conflicto visual-vestibular marea de verdad |
| Juicear un juego que aún no es divertido | El juice amplifica, no arregla (Vlambeer, "Don't Juice It or Lose It"); primero el core loop [ver: fundamentos-diseno] |
| Ease-in en respuestas a input | Se percibe como lag; usar ease-out |
| Tween no interrumpible que "poppea" al reiniciarse | Encadenar desde el valor actual |
| Hit-stop igual para todo (o global, congelando también partículas y música) | Escalar con el daño; congelar solo a los implicados |
| Salto simétrico con física "realista" | Gravedad asimétrica + apex flotado + coyote + buffer |
| Input descartado por llegar 2 frames antes | Buffering: encolar y ejecutar en el primer frame válido |
| Cámara position-locked frame-perfect | Deadzone + smoothing; la cámara nunca replica el ruido del avatar |
| Lerp de cámara con fracción fija ignorando delta time | `1-pow(1-f, dt*60)` o smooth-damp del engine |
| Radial deadzone sin remapear magnitud | Scaled radial: escalón de 0→0.25 se nota en movimiento fino |
| SFX idéntico repetido en ráfaga | Pitch/sample aleatorio + límite de voces simultáneas |
| Partículas/casquillos infinitos sin pooling | Object pooling + cap; permanencia con presupuesto |
| Feedback mudo (evento sin sonido) | Auditar: cada evento de gameplay debe sonar |
| Números flotantes ilegibles apilados | Offset aleatorio de spawn, ease-out, fade, pooling |

## Fuentes

- **Game Feel: A Game Designer's Guide to Virtual Sensation** — Steve Swink (libro, 2008; vía review de Liz England, Wikipedia y CritPoints) — la definición canónica: real-time control + simulated space + polish; correction cycle < 100 ms.
- **"Juice it or lose it"** — Martin Jonasson & Petri Purho (GDC Europe 2012; vía notas de heisarzola.com, GameJuice y roblog.co.uk) — el demo canónico de juicear un Breakout: tweening, sonido, partículas, shake, personalidad.
- **"The art of screenshake"** — Jan Willem Nijman, Vlambeer (INDIGO Classes 2013; vía transcripción-índice de theengineeringofconsciousexperience.com) — los ~30 pasos para que un shooter se sienta bien: balas grandes, permanencia, kick, hit-stop, "más graves".
- **"Scroll Back: The Theory and Practice of Cameras in Side-Scrollers"** — Itay Keren (GDC 2015; artículo completo en Game Developer/Gamasutra) — el vocabulario entero de cámaras 2D: deadzone, lookahead, snapping, attractors; pilares atención/interacción/confort.
- **"Math for Game Programmers: Juicing Your Cameras With Math"** — Squirrel Eiserloh (GDC 2016; slides/texto en archive.org) — sistema de trauma, shake = trauma², Perlin vs random, traslación vs rotación, asymptotic averaging con valores concretos.
- **"Celeste & Forgiveness"** — Maddy Thorson (maddymakesgames.com) — las 10 mecánicas de perdón con números (2 px, 5 px, media gravedad en apex).
- **"Thinking About Hitstop"** — Masahiro Sakurai, columna de Famitsu vol. 490 (traducción de Source Gaming) — calibración profesional de hit-stop: escala con daño, cap, proyectiles reducidos, vibración direccional.
- **Hitlag** — SmashWiki + **"Hitstop/Hitfreeze/Hitlag/Hitpause"** — Celia Wagar (CritPoints, 2017) — fórmula de frames de Smash y el origen de los cancels de SF2 en el hitstop.
- **"Doing Thumbstick Dead Zones Right"** — Josh Sutphin (third-helix/Game Developer, 2013) — axial vs radial vs scaled radial vs bowtie, con el scaled radial como default correcto.
- **easings.net** — Andrey Sitnik & Ivan Solovev — catálogo de referencia de las familias de easing (sine→quint, expo, back, elastic, bounce) y su carácter.
- **"Audio feedback in games"** — audiogamejam.org — principios de claridad, consistencia, capas y priorización del feedback sonoro (también como accesibilidad).
- **"Game Feel: Why Your Death Animation Sucks"** — Nicolae Berbece (GDC Europe 2015) — reconstrucción en vivo de una animación de muerte con los mismos principios (referenciada; consultada solo por resúmenes).
