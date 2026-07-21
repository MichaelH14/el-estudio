# Diseño de juegos móviles

> **Cuando cargar este archivo:** al diseñar un juego que nace para teléfono (no un port) — decidir controles táctiles, orientación, largo de sesión, el primer minuto, cómo sobrevive a interrupciones, o qué género encaja en la restricción móvil. Es la especialización móvil que PROFUNDIZA sobre las bases generales de diseño; no repite lo genérico, lo cruza.

## 0. Qué profundiza este archivo (mapa de no-repetición)

Todo lo genérico ya está sembrado en otras bases. Aquí va SOLO el ángulo específico del teléfono como plataforma de juego.

| Tema | Base genérica (no repetir) | Lo que este archivo añade |
|---|---|---|
| Core loop, flow, decisiones, MDA | [ver: gamedev/fundamentos-diseno] | Cómo el loop se recorta a la sesión-snack y a la interrupción |
| Convenciones por género + mercado | [ver: gamedev/generos] | Por qué cada género encaja o no en la restricción táctil/sesión |
| HUD, FTUE, tutoriales, thumb zone | [ver: gamedev/ux-ui-onboarding] | El primer minuto móvil y los controles como MECÁNICA, no como UI |
| Touch targets, safe areas, gestos de app | [ver: ux-ui/mobile-ux] | Gestos y virtual pads como sistema de juego en tiempo real |
| Retención, dailies, dopamina, ética | [ver: gamedev/psicologia-retencion-negocio] | La línea diseño↔explotación aplicada al loop móvil |
| Números de negocio (CPI/ARPDAU/LTV), tiendas | [ver: monetizacion-movil] · [ver: mercado-movil] · [ver: release-movil] | Aquí solo el diseño; los números viven en esas |
| Frame budget, draw calls, batería | [ver: unity-movil-rendimiento] · [ver: unity/rendimiento-unity] | Solo la implicación de DISEÑO del presupuesto (30 fps, thermal) |
| Input táctil en Unity, servicios | [ver: unity-movil-input-servicios] | Aquí el diseño del control; allá su implementación |

**Diagnóstico rápido: síntoma → sección**

| Síntoma | Ir a |
|---|---|
| "El control se siente resbaloso / no responde" | §4 (virtual pad: oclusión, dead zone, sin borde táctil) |
| "Se instala, juega 20 s y desinstala" | §5 (primer minuto) + [ver: gamedev/ux-ui-onboarding] §4 |
| "Nadie vuelve al día siguiente" | §2 (sesión sin cierre-gancho) + §5 |
| "Pierde progreso cuando entra una llamada" | §3 (interrupción no diseñada) |
| "Funciona en mi teléfono pero se traba en gama baja" | §9 (frame budget) + [ver: unity-movil-rendimiento] |
| "El género no cuaja en móvil" | §7 + [ver: gamedev/generos] |

---

## 1. El jugador móvil como restricción de diseño

No es un jugador de consola en pantalla chica: es un contexto de uso distinto. El diseño se deriva del contexto, no al revés.

| Rasgo del contexto | Consecuencia de diseño (no negociable) |
|---|---|
| Juega en huecos: bus, cola, cama, baño, anuncios de la TV | La **unidad de juego debe caber en 1-5 min** y cerrar con sentido (§2) |
| Puede ser interrumpido en cualquier frame (llamada, notificación, parada del bus) | El estado se salva SIEMPRE; matar la app no puede costar progreso (§3) |
| Una mano, a menudo la no-dominante, mientras hace otra cosa (**"un pulgar, un ojo"**) | Controles para un pulgar; nada que exija dos manos de precisión ni mirar fijo |
| Pantalla chica + dedo opaco que tapa lo que toca | Nada crítico debajo del punto de contacto; hitboxes generosas (§4, §6) |
| Sesión "lean-back" (relajarse) más que "lean-forward" (concentración total) | La dificultad media baja; el reto llega por profundidad opcional, no por exigir reflejos de e-sport |
| Compite con WhatsApp, TikTok y la vida real por 30 s de atención | El valor se demuestra en segundos, no en una intro cinemática (§5) |

**Números de contexto (GameAnalytics, 2025 Mobile Gaming Benchmarks, pool ~11.600 juegos):** sesión **mediana 5-6 min** (top 25%: 8-9 min); **~4 sesiones/día** (midcore 6-7); **~22 min de playtime diario** mediano. Traducción de diseño: el jugador te da ~5 min por visita y vuelve ~4 veces — diseña la *visita*, no la *maratón*. [ver: mercado-movil] para el detalle por género.

**Regla de oro del contexto:** si tu juego solo funciona con dos manos, sonido obligatorio, 20 min sin interrupción y atención total, no diseñaste un juego móvil — diseñaste un juego de consola que corre en un teléfono. Portéalo con conciencia [ver: unity/build-plataformas], no lo confundas con diseño móvil.

---

## 2. Sesión y ritmo: la "unidad de juego"

La pieza atómica del diseño móvil es la **unidad de juego completable**: un nivel, una carrera, una mano, un run, una oleada. Debe empezar y terminar dentro de la ventana de sesión.

| Principio | Aplicación concreta |
|---|---|
| **Unidad de 1-5 min con cierre claro** | Nivel numerado, partida, run corto. El jugador siente "logré algo" antes de guardar el teléfono |
| **Punto de guardado tras CADA unidad** (mínimo) | Nunca "perdiste el nivel porque saliste"; el progreso se consolida al cerrar cada unidad |
| **Reanudar exactamente** | Al reabrir, cae donde estaba (en la unidad en curso o en el menú con "Continuar" prominente) [ver: gamedev/ux-ui-onboarding] §2 |
| **Cierre = gancho al siguiente** | La pantalla de resultado abre el próximo objetivo (open loop): "siguiente nivel", "falta 1 para el cofre". Cerrar sin gancho = no vuelve |
| **Ritmo interno de la unidad** | Sub-loop de segundos (tap/match/salto) que vive del game feel [ver: gamedev/game-feel]; recompensa visible al terminar |
| **Snackable, no infinito-obligatorio** | Que se PUEDA jugar 30 min seguidos, pero que 3 min basten para avanzar. Lo contrario (progreso solo con sesiones largas) castiga al jugador real |

**Loops anidados en móvil** (aplicación del modelo de [ver: gamedev/fundamentos-diseno] §3 al reloj del teléfono):

| Loop | Duración | Qué lo alimenta |
|---|---|---|
| Momento | segundos | Game feel del tap/swipe/match |
| Unidad/sesión | 1-5 min | Nivel/run/partida → recompensa inmediata |
| Día | ~4 sesiones | Misiones diarias, energía, streak [ver: retencion-liveops] |
| Meta | días/semanas | Colección, progresión de cuenta, temporada [ver: pipeline/sistemas-meta] |

Un casual móvil necesita 2-3 loops bien anclados. Si el loop de día/meta no existe, retienes D1 pero mueres en D7 [ver: gamedev/psicologia-retencion-negocio] §3.

---

## 3. Interrupciones como material de diseño

En móvil la interrupción no es un caso de error: es el modo normal de juego. Se diseña PARA ella, no contra ella. Lo genérico (persistir estado, auto-pausa) está en [ver: ux-ui/mobile-ux] §8; aquí va el ángulo de diseño de juego.

| Decisión de diseño | Por qué en móvil |
|---|---|
| **Elegir tiempo-real vs turnos/async según interruptibilidad** | Turn-based y async (ajedrez, cartas, "tu turno") son NATIVAMENTE interrumpibles: el estado espera al jugador. Tiempo-real necesita pausa+persistencia explícita |
| **Auto-pausa al perder foco** en juegos de reflejo | Una llamada no puede matar al jugador en un plataformas. Al volver: cuenta atrás "3-2-1" antes de reanudar, no reanudar en frío |
| **Puntos de parada naturales frecuentes** | El diseño ofrece salidas dignas cada pocos segundos (fin de oleada, entre manos), no solo cada 10 min |
| **Persistir la unidad EN CURSO, no solo entre unidades** | En un run largo (roguelite móvil), guardar el estado del run para poder cerrarlo y seguir después — o acortar el run a la ventana de sesión |
| **Cero castigo por salir** | Salir a mitad no puede costar vidas/energía/moneda. Si el timer sigue corriendo al fondo, que sea a favor del jugador (energía que recarga), nunca en contra [ver: gamedev/psicologia-retencion-negocio] §2 (contingencias negativas) |
| **Idle/incremental: la interrupción ES la mecánica** | El progreso offline convierte "cerré la app" en parte del loop; al volver, "ganaste X ausente" [ver: gamedev/generos] (idle) |

**Test de interrupción (correr en cada build):** en cualquier frame — llamada entrante, cerrar la app desde el multitask, apagar pantalla, rotar. Al volver: ¿perdí progreso? ¿me mataron por estar ausente? ¿reanudó donde estaba? Si alguna respuesta es mala, el diseño de sesión está roto, no es un bug de QA aislado.

---

## 4. Controles de juego móvil (el corazón del diseño móvil)

El control táctil es la decisión de diseño más determinante y la que más devs de consola arruinan. La pantalla es a la vez el output y el input, y el dedo tapa el juego.

### 4.1 Virtual joystick y botones virtuales: por qué son problemáticos

Replican un mando físico en cristal. Funcionan, pero arrastran defectos estructurales que NO se pueden pulir del todo — son físicos, no de tuning:

| Defecto estructural | Efecto en el jugador |
|---|---|
| **Sin borde táctil (no hay tope físico)** | El pulgar no sabe dónde está el stick sin mirar; se "resbala" fuera del control y deja de responder a mitad de acción |
| **Oclusión** | El pulgar y la mano tapan justo la esquina donde pasa la acción; en pantalla chica es una fracción grande del juego |
| **Drift / dead zone** | Un stick fijo obliga a poner el pulgar exacto; un stick flotante (aparece donde tocas) ayuda pero introduce ambigüedad de origen |
| **Fatiga del pulgar** | Mantener presión y micro-ajustes finos cansa en minutos; contradice la sesión lean-back (§1) |
| **Roba pantalla** | Dos pads + botones comen las cuatro esquinas de una pantalla ya pequeña |
| **Precisión pobre** | Apuntar/plataformear fino con el pulgar es inherentemente menos preciso que con stick/ratón [ver: ux-ui/mobile-ux] (Fitts) |

**Cuándo el virtual pad SÍ es la respuesta correcta:** midcore que porta una fantasía de consola (shooters, MOBAs, action-RPG) donde el público ACEPTA la fricción a cambio de profundidad (Call of Duty Mobile, Genshin). No es un pecado — es un trade-off consciente para un público que lo tolera.

**Mitigaciones obligatorias si usas virtual pad** (craft consensuado; ninguna lo arregla del todo):
- **Stick flotante** (aparece bajo el pulgar al tocar la zona izquierda) en vez de fijo → elimina el "buscar el stick a ciegas".
- **Auto-apuntado / apuntado asistido** generoso (el equivalente móvil del aim assist de consola) — sin él, apuntar con pulgar es tortura.
- **Reposicionar, escalar y opacar** los controles en settings (guideline motor de accesibilidad, [ver: gamedev/ux-ui-onboarding] §5).
- **Auto-acciones contextuales**: recoger, recargar, saltar el borde — automatizar lo que no aporta decisión, reservar el input a lo que sí.
- Hitboxes y zonas de tap **más grandes que el arte** (hit-slop, [ver: ux-ui/mobile-ux] §3).

### 4.2 Tap, swipe y gestos COMO mecánica (no como UI)

En [ver: ux-ui/mobile-ux] §4 el gesto es un atajo de app con problema de descubribilidad. En un juego el gesto ES el verbo del juego, y ahí la descubribilidad se resuelve con el primer nivel, no con un botón alterno.

| Gesto | Verbo de juego típico | Nota de diseño |
|---|---|---|
| **Tap** | Disparar, colocar, saltar, seleccionar | El verbo por defecto; feedback en <0,1 s o se siente roto [ver: gamedev/game-feel] |
| **Tap-hold / charge** | Cargar fuerza, apuntar | Buen sustituto de gatillo analógico |
| **Swipe direccional** | Mover (2048, Threes), atacar, esquivar (Fruit Ninja) | Reemplaza al d-pad sin oclusión fija |
| **Tap-to-move** (tocar destino) | Mover el avatar al punto tocado | Alternativa clásica al joystick para RPG/point-and-click; menos preciso en tiempo real |
| **Drag** (arrastrar) | Tirar (Angry Birds), trazar ruta, apuntar con predicción | El drag muestra la trayectoria = decisión informada [ver: gamedev/fundamentos-diseno] §5 |
| **Pinch** | Zoom táctico (estrategia/4X móvil) | Solo donde el zoom tiene sentido |
| **Multi-touch** | Dos pulgares (twin-stick, ritmo) | Cuidado: rompe el "un pulgar" (§1); solo si el género lo pide |

Regla: en un juego, el gesto se enseña por diseño de nivel (el nivel 1 solo se puede pasar swipeando) — no necesita el "control visible equivalente" que exige una app, porque el juego ES la escuela del gesto [ver: gamedev/ux-ui-onboarding] §3 (aprender haciendo, George Fan).

### 4.3 One-touch / one-finger design

El extremo del diseño móvil: **todo el juego con un solo punto de contacto**. Es la joya de la corona del casual/hyper-casual y la razón de su alcance.

- **Un solo verbo, profundidad por timing/contexto:** Flappy Bird (tap = aletear), Crossy Road (tap = avanzar), un runner (tap = saltar/cambiar carril). La dificultad viene de CUÁNDO tocas, no de cuántos botones.
- **Comprensible en el primer frame**, sin tutorial [ver: gamedev/generos] (hyper/hybrid-casual). El diseño y el anuncio son la misma cosa (§5).
- **Accesible por definición:** un dedo, sin precisión fina, jugable con una mano ocupada — cubre el contexto móvil entero (§1, §6).
- Límite: la profundidad tiene que salir de la interacción del verbo con el sistema (velocidad creciente, obstáculos que combinan), o se agota en minutos [ver: gamedev/fundamentos-diseno] §1 (patrón agotado).

### 4.4 Auto-play / auto-battle

Patrón nativo móvil (idle-RPG, gacha, muchos midcore): el juego se juega solo y el jugador **decide y optimiza**, no ejecuta.

- Desplaza la diversión del loop de momento (ejecución) al loop de meta (build, equipo, upgrades) — encaja con lean-back y con la sesión interrumpible (puedes mirar de reojo).
- Riesgo de diseño: si el auto-play trivializa TODO, no queda decisión y el juego es un dashboard [ver: gamedev/fundamentos-diseno] §5. Reserva momentos donde el input manual importe (jefes, PvP).
- Es una herramienta de accesibilidad y de respeto al tiempo, pero también el terreno donde vive la monetización de skip [ver: monetizacion-movil]; diséñalo del lado del jugador, no del dolor fabricado [ver: gamedev/psicologia-retencion-negocio] §2.

### 4.5 Portrait vs landscape: decisión de diseño, no de última hora

| | Portrait (vertical) | Landscape (horizontal) |
|---|---|---|
| **Agarre** | Una mano, pulgar (§1) | Dos manos, teléfono acostado |
| **Contexto** | Micro-sesión, de pie, en el bus, jugando "de lado" con otra cosa | Sesión dedicada, sentado, atención plena |
| **Encaja con** | Hyper/hybrid-casual, puzzle, idle, arcade one-touch, cartas | Midcore, shooters, MOBA, plataformas, racing |
| **Coste** | HUD apretado en ancho; menos campo de visión horizontal | Rompe el reflejo de "sacar el teléfono con una mano"; sube la barrera de entrada |
| **Señal de mercado** | La mayoría del casual de más alcance es portrait (menor fricción de arranque) | El midcore de sesión larga tolera y prefiere landscape |

Decide la orientación **antes** de diseñar el HUD y los controles; no es un flag que se cambia luego. Si soportas ambas, ambos layouts deben estar realmente pensados, no uno estirado [ver: ux-ui/mobile-ux] §5. Respeta safe areas en las dos [ver: ux-ui/mobile-ux] §6.

---

## 5. El primer minuto móvil

El FTUE genérico y sus números viven en [ver: gamedev/ux-ui-onboarding] §4 (valor en 2-3 min, ~77% de churn D1, funnel instrumentado). Aquí el ángulo específicamente móvil: el minuto es MÁS brutal que en cualquier otra plataforma.

- **No pagó por entrar** (F2P): no tiene sunk cost, no te debe nada, la desinstalación cuesta un toque. En Steam el jugador que pagó $20 te da 30 min; el de móvil te da segundos.
- **Diseña el primer frame jugable, no la intro:** cero splash largo, cero login, cero pedir cuenta/notificaciones/permisos antes del primer momento de diversión (esos permisos se piden DESPUÉS de dar valor — regla de [ver: gamedev/ux-ui-onboarding] §4, y en iOS el prompt de ATT también va tras el valor [ver: release-movil]).
- **El "hook" es en segundos:** en hyper/hybrid-casual el jugador entiende el juego en el primer frame o se va; la meta sourced honesta es *demostrar valor en 2-3 min* (GameAnalytics FTUE), pero el enganche del casual se juega en los primeros ~10 s. Trata "10 s" como heurística de diseño, "2-3 min" como el umbral con dato.
- **Match anuncio↔juego (playable ads):** el creative del anuncio ES parte del diseño. Si el anuncio promete un verbo, el segundo 0 del juego debe entregar ESE verbo, o el jugador que instaló se siente estafado y desinstala [ver: gamedev/generos] (hyper-casual: "el juego es su anuncio"). El desajuste anuncio↔juego es la fuga #1 del casual.
- **Early wins densos:** en los primeros minutos, level-ups frecuentes, umbrales bajos, recompensa cada pocos segundos; el ritmo de progreso al inicio va comprimido y se estira después [ver: gamedev/ux-ui-onboarding] §4.
- **Descarga diferida:** si hay assets grandes, entra al juego con lo mínimo y descarga el resto de fondo; Apple exige avisar el tamaño de descarga antes de bajar recursos en el primer arranque (App Store Review Guideline 4.2.3). Un jugador esperando una barra de descarga antes de jugar es un jugador que ya se fue.

---

## 6. Dificultad y accesibilidad móvil

El móvil impone tres limitaciones que la curva de dificultad debe asumir (encima de la curva genérica de [ver: gamedev/fundamentos-diseno] §4 y [ver: gamedev/psicologia-retencion-negocio] §4):

| Limitación móvil | Ajuste de diseño |
|---|---|
| **Imprecisión del pulgar** | Hitboxes/ventanas más generosas que en consola; forgiveness táctil (coyote time, buffering — [ver: gamedev/generos] plataformas); no exigir píxel-perfect |
| **Sin retroalimentación táctil** (no hay botón que se sienta) | Feedback visual y de vibración (haptics) para confirmar cada input; el jugador no "siente" el tap [ver: gamedev/game-feel] |
| **Distracción y ruido ambiental** | Jugable en silencio (el audio es un plus, no un requisito): información crítica nunca solo por sonido; sesión que tolera mirar de reojo |
| **Una mano / mano ocupada** | El pico de dificultad no debe exigir dos manos de precisión de golpe; que la maestría sea opcional, no obligatoria para avanzar |
| **Gama de dispositivos enorme** | En gama baja el juego corre más lento; la dificultad no puede depender de un framerate que la gama baja no alcanza (§9) |

- **Dificultad opt-in granular** encaja doble en móvil (público amplio, no-gamers): estilo Assist Mode de Celeste, no easy/normal/hard ciego [ver: gamedev/psicologia-retencion-negocio] §4.
- **Auto-play/auto-aim** (§4) son también features de accesibilidad: dejan jugar a quien no tiene destreza fina.
- Accesibilidad base del teléfono: targets ≥44 pt/48 dp, nada bajo el notch/home indicator, reposicionar controles [ver: ux-ui/mobile-ux] §3, §6.

---

## 7. Géneros en móvil: el ángulo de la restricción

El mercado por género vive en [ver: gamedev/generos] y [ver: mercado-movil]. Aquí SOLO el porqué de diseño: cada género encaja o no según tres filtros — **¿cabe en 5 min? ¿se juega con un pulgar? ¿sobrevive a la interrupción?**

| Género | Sesión | Control | Interrumpible | Veredicto móvil |
|---|---|---|---|---|
| **Hyper/hybrid-casual** | ✅ segundos | ✅ one-touch | ✅ total | Nativo. El diseño ES el anuncio; negocio de UA [ver: gamedev/generos] |
| **Puzzle (match-3, etc.)** | ✅ por nivel | ✅ tap/swipe | ✅ entre movimientos | Nativo. Rey de la retención a medio plazo (GameAnalytics) |
| **Idle / incremental** | ✅ y offline | ✅ tap | ✅ la ausencia ES mecánica | Nativo. Retención altísima, arte mínimo [ver: gamedev/generos] |
| **Casual arcade / runner** | ✅ corta | ✅ one-touch/swipe | ✅ por partida | Nativo. Lidera D1 (GameAnalytics) |
| **Cartas / mesa / async** | ✅ por turno | ✅ tap | ✅✅ el turno espera | Nativo. Turnos = interrupción gratis |
| **Midcore (RPG, estrategia 4X, shooter, MOBA)** | ⚠️ sesión larga | ⚠️ virtual pad | ⚠️ requiere pausa/async | Viable con público que tolera la fricción; negocio de UA masiva y live-ops [ver: retencion-liveops]. Landscape (§4.5) |
| **Plataformas de precisión** | ✅ por nivel | ❌ el pulgar no da precisión | ✅ | Rema contra la corriente; solo con controles repensados (auto-run + tap, no d-pad) |
| **Sim/estrategia profunda de PC** | ❌ sesión de horas | ❌ mil inputs precisos | ❌ | Su casa es Steam, no el teléfono [ver: gamedev/generos] |
| **Multijugador competitivo en tiempo real** | ⚠️ | ⚠️ | ❌ (una partida no se pausa) | Doble problema: control táctil + población + netcode [ver: gamedev/generos]. Casi nunca para equipo chico |

**Heurística:** un juego encaja en móvil cuando aprueba los tres filtros de golpe. Cada "❌" o "⚠️" es una batalla de diseño que hay que ganar explícitamente (o cambiar de plataforma), no un detalle a resolver después.

---

## 8. Loops de retención en el DISEÑO (la línea, no la explotación)

El detalle de dailies, energía, gacha, battle pass, dopamina y la ética completa está en [ver: gamedev/psicologia-retencion-negocio] §2-5 y [ver: retencion-liveops]. Aquí, la síntesis de DISEÑO: qué loop de retención construir sin cruzar a explotación.

| Loop de retención | Diseño sano (engancha) | Diseño tóxico (explota) |
|---|---|---|
| **Daily / streak** | Arranca el hábito los primeros días; con "perdón" ocasional para no castigar romper la racha | Castigo por no conectarse (contingencia negativa); racha imposible de recuperar |
| **Energía / vidas** | Techo suave que invita a volver; recarga a favor del jugador | Muro que corta la diversión para vender el skip (dolor fabricado) |
| **Colección** | Meta de largo plazo intrínseca (completar, expresarse) | Gacha con odds ocultas apuntadas a dinero real = apuesta |
| **Appointment (cosecha/timer)** | Opcional, un hook entre varios | Único motor; dicta CUÁNDO jugar y mata autonomía; lee como diseño de 2012 |
| **Auto-play** | Respeta el tiempo, mueve la diversión a la decisión (§4.4) | Trivializa el juego para vender el "skip del skip" |

**El test de diseño (no de negocio):** ¿el jugador vuelve porque QUIERE (competencia, colección, "a ver qué sigue") o porque TEME perder algo (racha, cosecha, FOMO)? Los tres loops que retienen de verdad a largo plazo son intrínsecos: maestría, colección propia y social [ver: gamedev/fundamentos-diseno] §7 (SDT). Los extrínsecos (daily, energía) arrancan el hábito; no lo sostienen. Un juego cuyo único gancho a D30 es un login bonus está muerto y solo lo disimula.

- **Ads y su UX son parte del DISEÑO del loop:** rewarded opt-in integrada (revivir, doblar premio, girar otra vez) puede SUMAR retención; interstitial forzado en pantalla de recompensa o en la primera sesión es un impuesto que se paga en churn [ver: gamedev/psicologia-retencion-negocio] §5. Apple exige que todo interstitial tenga botón de cierre visible y no engañe al tap (App Store Review Guideline 2.5.18) — cúmplelo por diseño, no por parche [ver: release-movil].

---

## 9. Frame budget como decisión de diseño

Lo técnico (draw calls, batching, LODs, memoria) vive en [ver: unity-movil-rendimiento], [ver: unity-movil-graficos] y [ver: modelado/presupuestos-poligonos]. Aquí, la única parte que es DECISIÓN DE DISEÑO:

- **Unity renderiza a 30 fps por defecto en móvil** (con `Application.targetFrameRate = -1` y `vSyncCount = 0`, tanto iOS como Android) **para ahorrar batería**, independiente del refresco nativo de la pantalla (Unity ScriptReference). Subir a 60 fps es una decisión de diseño con coste: más batería y más calor.
- **Batería y calor son restricciones de diseño, no solo de ingeniería:** una sesión de 5 min tolera 60 fps; un idle que corre horas de fondo o un midcore de sesiones largas debe cuidar el thermal throttling (el SoC baja la frecuencia al calentarse y el juego se ralentiza a mitad de sesión). El presupuesto de arte y efectos [ver: arte-movil] se fija contra el dispositivo objetivo, no contra tu teléfono de gama alta.
- **La gama baja fija la dificultad y el game feel reales:** si el diseño depende de reflejos a 60 fps, en el teléfono mediano de tu público (que corre a 30-40) el juego se siente y se juega distinto. Define el dispositivo mínimo objetivo temprano y diseña el game feel contra ÉL [ver: unity-movil-rendimiento].

---

## Reglas prácticas

1. Deriva el diseño del contexto: 1-2 manos, sesión de 5 min, interrumpible, un ojo. Si tu juego no sobrevive a eso, es un port, no un diseño móvil (§1).
2. Diseña la **unidad de juego completable en 1-5 min** con cierre claro y guardado tras cada una; nunca castigues salir (§2, §3).
3. El cierre de cada unidad abre el siguiente objetivo (open loop); cerrar sin gancho = no vuelve (§2).
4. Corre el **test de interrupción** en cada build: llamada / cerrar app / apagar pantalla / rotar → cero pérdida de progreso, cero muerte por ausencia (§3).
5. Prefiere turnos/async donde el género lo permita: son interrumpibles gratis (§3, §7).
6. Antes del virtual pad, pregunta si el juego se puede hacer con **tap/swipe/one-touch**; el pad es el último recurso, no el primero (§4).
7. Si usas virtual pad: stick flotante, auto-aim generoso, controles reposicionables/escalables/opacables, auto-acciones para lo que no es decisión (§4.1).
8. Enseña el gesto por diseño de nivel (el nivel 1 solo se pasa con el gesto), no con un muro de texto (§4.2).
9. Decide **portrait vs landscape ANTES** del HUD y controles; encájalo con el contexto y el género (§4.5).
10. Diseña el **primer frame jugable**, no la intro: cero login/permisos/ads antes del primer momento de diversión; valor demostrado en 2-3 min (§5).
11. Match anuncio↔juego: el segundo 0 entrega el verbo que prometió el creative (§5).
12. Asume la **imprecisión del pulgar**: hitboxes y ventanas generosas, forgiveness, feedback visual+haptic de cada input (§6).
13. Jugable en silencio: información crítica nunca solo por audio (§6).
14. Ofrece dificultad **opt-in granular** (Assist-Mode-style), no easy/normal/hard ciego; auto-play/auto-aim como accesibilidad (§4.4, §6).
15. Aplica los **tres filtros de género** (¿5 min? ¿un pulgar? ¿interrumpible?) antes de comprometerte; cada ❌ es una batalla explícita (§7).
16. Construye 2-3 loops de retención, con al menos uno intrínseco (maestría/colección/social); los extrínsecos arrancan el hábito, no lo sostienen (§8).
17. Ads como diseño: rewarded opt-in integrada al loop; interstitial nunca en pantalla de recompensa ni primera sesión; botón de cierre visible (§8).
18. Fija el **dispositivo mínimo objetivo** temprano y diseña el game feel y la dificultad contra ÉL, no contra tu gama alta (§9).
19. 30 fps por defecto en móvil (batería); subir a 60 es decisión con coste térmico — justifícala por género de sesión (§9).
20. Respeta safe areas y thumb zone en TODA orientación; targets ≥44 pt/48 dp; nada crítico bajo el dedo, el notch o el home indicator [ver: ux-ui/mobile-ux].

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Portar un juego de consola y llamarlo "juego móvil" (dos manos, sesión larga, audio obligatorio) | Rediseñar desde el contexto: pulgar, 5 min, interrumpible, mudo (§1) |
| Virtual joystick como primer reflejo de control | Probar tap/swipe/one-touch primero; el pad es el último recurso y siempre flotante + con auto-aim (§4.1) |
| Stick fijo que el pulgar pierde a ciegas | Stick flotante que aparece bajo el pulgar; hit-slop grande (§4.1) |
| Controles en las esquinas tapados por la propia mano | Nada crítico bajo el punto de contacto; auto-acciones para lo oclusible (§4.1) |
| Perder progreso cuando entra una llamada | Persistir la unidad en curso + auto-pausa con cuenta atrás al volver (§3) |
| Timer que corre en contra del jugador mientras está fuera | Timers solo a favor (energía que recarga); cero contingencia negativa (§3, §8) |
| Intro cinemática / login / permisos antes de jugar | Primer frame jugable; permisos y ATT tras dar valor (§5) |
| Anuncio que promete un juego distinto al que instala | Match anuncio↔juego: el verbo del creative es el verbo del segundo 0 (§5) |
| Exigir precisión de píxel con el pulgar | Hitboxes/ventanas generosas + forgiveness táctil; feedback haptic (§6) |
| Información crítica solo por sonido en un juego que se juega en el bus | Jugable en silencio; redundar audio con visual (§6) |
| Elegir un género de PC (sim/estrategia profunda) y forzarlo al teléfono | Pasar los tres filtros de género antes; si falla, cambiar de plataforma (§7) |
| Retención montada solo sobre daily + energía + FOMO | Añadir un loop intrínseco (maestría/colección/social); los extrínsecos no sostienen D30 (§8) |
| Interstitial en la pantalla de recompensa o en el minuto 1 | Rewarded opt-in integrada; interstitial fuera de recompensas y primera sesión (§8) |
| Diseñar el game feel en un iPhone de gama alta a 60 fps | Fijar dispositivo mínimo objetivo y diseñar contra su 30-40 fps real (§9) |
| Portrait/landscape decidido al final y un layout estirado | Decidir orientación antes del HUD; si son dos, dos layouts pensados (§4.5) |

## Fuentes

- **2025 Mobile Gaming Benchmarks — GameAnalytics** (pool ~11.600 juegos móviles) — sesión mediana 5-6 min, ~4 sesiones/día, ~22 min de playtime diario, retención por género; la base de los números de contexto de §1-2. Verificado vía la base hermana [ver: gamedev/psicologia-retencion-negocio], que lo cita directo.
- **"10 Tips for a Great First Time User Experience (FTUE) in F2P Games" — GameAnalytics** — demostrar valor en 2-3 min, funnel de tutorial instrumentado, early wins, open loops; ancla el umbral sourced del primer minuto (§5).
- **"Mobile game player retention" — Mistplay + guías FTUE de Udonis/Keewano** — ~77% de churn en el día 1, D1 mediana ~22-24%; el contexto brutal del primer minuto móvil (§5). Vía base hermana verificada.
- **State of Mobile 2026 — Deconstructor of Fun** — hyper/hybrid-casual y 4X móvil, negocio de UA y live-ops; encaje de género (§7). Vía base hermana.
- **"What happened to hypercasual?" — PocketGamer.biz / Udonis (2025-2026)** — 22.05B installs de hyper-casual en 2025, muerte del modelo ad-only, hybrid-casual como tendencia; contexto de one-touch y del anuncio-como-diseño (§4.3, §5). Vía base hermana.
- **"How Do Users Really Hold Mobile Devices?" — Steven Hoober, UXmatters (2013, 1.333 observaciones de campo)** — ~49% agarre a una mano, ~75% de interacciones con el pulgar; base empírica del "un pulgar" (§1, §4). Verificado en [ver: ux-ui/mobile-ux].
- **"How I Got My Mom to Play Through Plants vs. Zombies" — George Fan, GDC 2012** — aprender haciendo, dosificar mecánicas, ~8 palabras en pantalla; base del "enseñar el gesto por diseño de nivel" (§4.2, §5). Verificado en [ver: gamedev/ux-ui-onboarding].
- **"Onboarding" — Roblox Creator Hub** — "get to the fun quickly / teach the essentials / leave players wanting more"; el gancho de segundos (§5). Vía base hermana.
- **Application.targetFrameRate — Unity ScriptReference (docs.unity3d.com)** — *fuente primaria, verificada directamente por WebFetch:* con `targetFrameRate = -1` y `vSyncCount = 0`, iOS y Android renderizan a **30 fps fijos para ahorrar batería**, independiente del refresco nativo; subir el framerate se recomienda ajustar para no sobrecalentar. Base de §9.
- **App Store Review Guidelines — Apple (developer.apple.com/app-store/review/guidelines)** — *fuente primaria, verificada directamente por WebFetch:* 4.2 minimum functionality (no templates/copycats), 4.2.3 (avisar tamaño de descarga antes del primer arranque), 2.5.18 (interstitials con botón de cierre visible, sin engañar el tap). Constraints de diseño de §5 y §8; el detalle de tienda en [ver: release-movil].
- **Bases hermanas del plugin (conocimiento ya verificado):** [ver: gamedev/fundamentos-diseno] (core loop, flow, SDT, decisiones), [ver: gamedev/generos] (encaje por género y mercado), [ver: gamedev/ux-ui-onboarding] (FTUE, HUD, thumb zone), [ver: gamedev/psicologia-retencion-negocio] (retención, dopamina, ética, ads), [ver: gamedev/game-feel] (feedback), [ver: ux-ui/mobile-ux] (touch targets, safe areas, gestos de app). Este archivo cruza y profundiza sobre ellas, no las repite.

> **Nota de honestidad:** WebSearch estaba agotado en esta sesión (200/200) y varias URLs de diseño de controles no se pudieron localizar sin buscador. Los NÚMEROS de negocio/benchmark provienen de fuentes reales publicadas (GameAnalytics 2025, Deconstructor of Fun 2026, Hoober 2013, Mistplay/Udonis) ya verificadas en las bases hermanas; los dos primarios técnicos (Unity ScriptReference, Apple Review Guidelines) se verificaron en vivo por WebFetch. Los principios de diseño de controles (virtual pad, one-touch, gestos, auto-play) son craft consensuado de la industria expuesto como razonamiento, sin cifras inventadas. Pendiente de una pasada con buscador: una fuente primaria dedicada de diseño de controles táctiles (GDC/Deconstructor of Fun) para citar mecanismos con atribución exacta.
