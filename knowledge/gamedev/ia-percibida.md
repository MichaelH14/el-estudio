# IA percibida: diseñar enemigos que se SIENTAN inteligentes

> **Cuándo cargar este archivo:** al diseñar el comportamiento de cualquier NPC, enemigo o criatura y decidir *qué debe sentir el jugador* — antes de elegir FSM, behavior tree o planner. También al depurar un enemigo que "funciona pero se siente tonto", al repartir el presupuesto entre IA y diseño de nivel, o al evaluar meter un LLM en un NPC. Aquí está el QUÉ/POR QUÉ de la inteligencia aparente; el CÓMO implementarla (NavMesh, FSM/BT, percepción, spawns, rendimiento) está completo en [ver: pipeline/ia-enemigos].

La tesis de todo el archivo, y está firmada por quien programó la IA más elogiada del género: **el jugador no puede ver el algoritmo, solo el comportamiento**. Jeff Orkin, autor de la IA de *F.E.A.R.*, lo dice sin anestesia: *"all A.I. ever do is move around and play animations"* — ir a cubierto es moverse a una posición y reproducir una animación de agacharse. La inteligencia no está en el código; está en la lectura que hace el jugador. Diseñar IA es diseñar esa lectura.

Corolario incómodo pero liberador para un equipo chico: **subir la complejidad del algoritmo tiene rendimientos decrecientes muy rápido**; subir la legibilidad del comportamiento, no. Casi siempre rinde más gastar en el nivel, la telegrafía y el audio que en un planner más listo.

## 1. Reglas simples + composición: el caso Pac-Man (1980)

Los cuatro fantasmas de *Pac-Man* comparten **exactamente el mismo algoritmo**: cada uno tiene una casilla objetivo y en cada intersección elige la dirección que minimiza la distancia a ella. No hay cuatro IAs. Hay una IA y cuatro maneras de elegir el objetivo (reglas del *Pac-Man Dossier* de Jamey Pittman):

| Fantasma | Casilla objetivo en modo chase | Lo que el jugador percibe |
|---|---|---|
| Blinky (rojo) | La casilla actual de Pac-Man | Te persigue, es implacable |
| Pinky (rosa) | 4 casillas por delante de tu dirección | Te corta el paso, te embosca |
| Inky (celeste) | Toma un punto 2 casillas delante de Pac-Man y **duplica el vector que va desde Blinky hasta ese punto** | Impredecible; se envalentona cuando Blinky está cerca |
| Clyde (naranja) | A más de 8 casillas: la casilla de Pac-Man. A menos de 8: su esquina | Tímido, "hace lo suyo", te deja escapar |

Detalles que multiplican el efecto y cuestan casi nada:

- **Scatter mode**: cada cierto tiempo los cuatro dejan de perseguir y apuntan a una esquina. El objetivo de esquina está en un punto que **nunca pueden alcanzar** — por eso orbitan ahí. El respiro rítmico es lo que hace legible la persecución.
- **Cruise Elroy**: Blinky acelera cuando quedan pocos puntos en el nivel. La tensión sube sola al final de cada ronda, sin sistema de dificultad.
- La consecuencia de la regla de Inky es una relación *emergente* entre dos enemigos: parecen coordinarse y nadie programó coordinación.

**La lección transferible:** para que un grupo parezca coordinado, no programes coordinación — dale a cada miembro una **regla de objetivo distinta** sobre el mismo motor de movimiento. El cerebro del jugador construye la conspiración solo. Cuatro reglas de dos líneas rinden más que un sistema de squad.

## 2. El jugador completa lo que falta

- **Goomba (*Super Mario Bros.*, 1985):** camina recto; si choca con una pared, se da la vuelta. Eso es todo. Generaciones de jugadores creyeron que iba a por ellos.
- **Fauna ambiental (las cucarachas de *Half-Life*):** huyen si te acercas, mueren si las pisas, se refugian en rincones, se acercan a los cadáveres. Cuatro reglas y el cerebro ve **un bicho vivo**, no un script. La IA que no intenta matarte suele ser la que más hace por la sensación de mundo habitado, y es de las más baratas del juego.
- Regla de reparto de presupuesto: **antes de subir de FSM a behavior tree en tu enemigo principal, mete tres criaturas ambientales de cuatro reglas**. El retorno en "este mundo está vivo" es mayor.

## 3. El nivel es la mitad de la IA: el caso F.E.A.R. (2005)

⚠️ **Corrección de un mito muy repetido** (incluido en divulgación reciente): la IA de *F.E.A.R.* **no es una FSM grande**. Es un **planner GOAP** (Goal-Oriented Action Planning, inspirado en STRIPS) sobre una FSM de solo tres estados: `Goto`, `Animate` y `UseSmartObject` — y Orkin aclara que el tercero es una variante data-driven del segundo, "así que en realidad hablamos de una FSM de dos estados". La FSM ejecuta; el planner decide, encadenando acciones por precondiciones y efectos con A* sobre estados del mundo (el mismo A* que usan para navegar, con otros nodos y aristas).

Pero lo que hizo famosa a esa IA no fue el planner. Fue esto:

**La filosofía de nivel de Monolith** (cita del paper): *"el trabajo del diseñador es crear espacios interesantes para el combate, repletos de oportunidades para que la IA las explote"* — muebles que sirven de cobertura, ventanas de cristal por las que lanzarse, múltiples entradas para flanquear. Los diseñadores **no scriptean** el comportamiento individual. La misma IA en un pasillo vacío se ve tonta; no porque piense distinto, sino porque no tiene nada que explotar.

**El flanqueo que nadie programó.** Orkin es explícito: *"la verdad es que no teníamos NINGÚN comportamiento de escuadrón complejo en F.E.A.R."*. Lo que ve el jugador emerge del cruce entre la decisión de escuadrón y la individual:

- El escuadrón ordena "id a cubierto válido". Si hay un muro entre la IA y su única cobertura conocida, toma la ruta trasera y reaparece por el costado. *"Parece que la IA está flanqueando, pero de hecho es solo un efecto colateral de moverse a la única cobertura válida que conoce."*
- Con `Advance-Cover`, cada IA avanza a la cobertura más cercana a la amenaza. Si el mobiliario las manda por lados opuestos, *"parece que ejecutan un ataque de pinza coordinado, cuando en realidad solo van a la cobertura más cercana, que resulta estar a cada lado del jugador"*. Las retiradas emergen igual.

**El diálogo es la capa que hace visible el pensamiento.** Orkin describe el comportamiento del soldado como un "dip de siete capas"; la última — la que "resalta el sabor" — es el diálogo. Y aquí están las tres reglas más rentables de todo este archivo:

1. *"No tiene sentido implementar comportamientos de escuadrón si al final la coordinación no es aparente para el jugador."* Un comportamiento que el jugador no percibe **no existe**.
2. *"Vocalizar intenciones a veces puede bastar, sin ninguna implementación real del comportamiento asociado."* Cuando muere el penúltimo miembro de un escuadrón, el superviviente grita "necesito refuerzos". **No implementaron refuerzos.** El jugador asume que los siguientes enemigos que aparecen son esos refuerzos.
3. **Usa el diálogo para explicar la falta de acción.** Una IA bajo fuego que no consigue reposicionarse parece tonta; si dice "¡no tengo a dónde ir!", parece consciente de su situación. El fallo se convierte en carácter.

Detalle de oficio: prefieren **diálogo entre dos personajes** antes que anuncios de uno solo — en vez de gritar de dolor, otro pregunta el estado y el herido responde. Y el veredicto de Orkin sobre un jugador que en un foro alucinaba con que *"no solo se dan órdenes, ¡es que además las cumplen!"*: **"la realidad es que es todo humo y espejos, y todas las decisiones sobre qué decir se toman a posteriori, una vez que el comportamiento de escuadrón ya decidió qué van a hacer."**

## 4. Director que sabe + agente que busca: el caso Alien: Isolation (2014)

Arquitectura de dos sistemas, y el reparto de información es el diseño entero:

| Sistema | Qué sabe | Qué hace |
|---|---|---|
| **Director** | Siempre sabe dónde estás | Gestiona el "menace gauge": cuánta presión aplicar y cuándo. Pacing, no caza |
| **IA del alien** | **NO sabe dónde estás.** "Nunca se le permite hacer trampa" | Te busca con sentidos: oye pasos y disparos, detecta el motion tracker a ~1.5 m, mira; incluye ray traces cortos hacia atrás para que no puedas caminar pegado a su espalda |

Por eso entra en una habitación y **no te encuentra**: te estaba buscando de verdad. La tensión no sale de que sea listo, sale de que **se le puede engañar** — y de que el director impide que la búsqueda se vuelva aburrida o injusta.

**La ilusión de aprendizaje, sin aprendizaje.** Partes del árbol de comportamiento (100+ nodos, ~30 en el nivel superior) están **bloqueadas al empezar** y se desbloquean cuando el jugador repite una táctica: si te escondes mucho en taquillas, se desbloquea registrar taquillas; si abusas de los conductos, se desbloquea meterse en ellos. El jugador jura que la criatura aprendió. No aprendió: se le abrió una rama.

⚠️ **Salvaguarda imprescindible** (y la parte que casi nadie copia): los desbloqueos **no se disparan con la muerte del jugador**. Si murieras y eso hiciera al enemigo más capaz, el juego castigaría al que va perdiendo — la espiral de frustración. Se desbloquea por táctica repetida **con éxito**, no por fracaso del jugador. Mismo principio que el director de *Left 4 Dead*: modular frecuencia, no dificultad [ver: pipeline/ia-enemigos §8].

## 5. La ilusión sale más barata en el motor de lo que crees

Traducción de todo lo anterior a decisiones concretas de implementación [ver: pipeline/ia-enemigos]:

| Efecto percibido | Implementación real | Coste |
|---|---|---|
| "Me está cazando" | Repath constante + nunca detenerse. Los NextBots de *Left 4 Dead* (motor Source, heredados por Garry's Mod) pasaban por mucho más listos que un NPC normal: solo usaban mejor navmesh y recalculaban ruta sin parar, en vez de nodos rígidos | Bajo |
| "Se coordinan" | Una regla de objetivo distinta por enemigo (§1) + barks entre dos personajes | Bajo |
| "Sabe que la cagó" | Una línea de diálogo que explica la inacción ("no tengo a dónde ir") | Muy bajo |
| "Está aprendiendo" | Desbloquear ramas de comportamiento por táctica repetida del jugador, nunca por su muerte | Medio |
| "Está pensando" | Pausa antes de actuar + animación de duda/mirar alrededor. El tiempo de reacción humano ES el tell de inteligencia | Muy bajo |
| "Improvisa" | Replanificar tras un fallo. En *F.E.A.R.*: si bloqueas la puerta con el cuerpo, la IA intenta abrir → falla → patea la puerta → falla → se lanza por la ventana | Alto (planner) |
| "Es un bicho vivo" | 3-4 reglas reactivas y cero combate (§2) | Muy bajo |

El audio hace la mitad del trabajo y suele ser lo último que se mira: un enemigo que gruñe al perderte de vista comunica un cambio de estado interno que ninguna animación transmite igual [ver: unity/audio-unity], [ver: gamedev/audio].

## 6. Lo que ROMPE la ilusión

La inteligencia percibida es frágil y asimétrica: se construye lento y se cae en un segundo. Los rompedores, por orden de gravedad:

- **Omnisciencia visible.** El enemigo reacciona a algo que no pudo ver ni oír. Un solo caso destruye la credibilidad de todo el sistema. Antídoto: percepción real con sentidos, y que el director (si lo hay) module presión, no información [ver: pipeline/ia-enemigos §6].
- **Amnesia instantánea.** Pierde la línea de visión medio segundo y vuelve a patrullar silbando. Antídoto: última posición conocida + estado de búsqueda + tiempo de "sospecha" que decae despacio.
- **Telepatía de grupo.** Matas a uno en silencio y los diez del mapa se enteran. Antídoto: la información se propaga por un canal explicable (grito, cuerpo hallado, radio) y con retardo.
- **Quedarse atascado.** Un enemigo trabado contra una esquina es el recordatorio más eficaz de que es un programa. Antídoto: watchdog que detecta no-progreso y fuerza replan/teleport fuera de cámara.
- **Reacción perfecta.** Puntería instantánea al primer píxel de visión: se lee como tramposo, no como listo. Antídoto: rampa de sospecha y wind-up legible [ver: pipeline/ia-enemigos §7].
- **Idle muerto.** Un NPC parado en T-pose emocional mata el mundo más que una mala decisión táctica.

## 7. NPCs con modelos de lenguaje: qué aporta y qué no (estado 2026)

El cambio real: en vez de elegir una línea de una lista, el NPC **genera** la respuesta según lo que el jugador dice. Hay demos y prototipos funcionando y cada conversación sale distinta.

Lo que sigue sin estar resuelto, y hay que decirlo antes de prometérselo a nadie:

- **Latencia y coste**: cada línea es una inferencia. En combate no hay presupuesto para esperar; en conversación pausada, sí.
- **Coherencia y control autoral**: un NPC que puede decir cualquier cosa puede contradecir el lore, spoilear o soltar un disparate. El guion existe para controlar el ritmo narrativo [ver: gamedev/narrativa-guion].
- **Memoria**: recordar conversaciones anteriores y el estado del mundo es un problema de sistemas, no del modelo.
- **Actuación**: la voz grabada tiene una calidad interpretativa que la síntesis todavía no iguala, y hay un problema laboral real con los actores.

**Criterio práctico:** un LLM resuelve *variedad conversacional*, no *inteligencia táctica*. Lo que hace que un enemigo se sienta listo en combate sigue siendo lo de las §§1-5, y es órdenes de magnitud más barato. Si metes un LLM, mételo donde la conversación ES la mecánica, no como capa de charla encima de un shooter. Y ojo con lo que dice Orkin sobre *F.E.A.R.*: el sistema de diálogo estaba **completamente separado** del planner y enganchado a mano, y eso ya bastaba para el efecto — antes de un LLM, agota los barks bien escritos.

## Reglas prácticas

- [ ] Define **qué debe sentir el jugador** antes de elegir la arquitectura. "Que se sienta acorralado" es un objetivo; "que use behavior trees" no lo es.
- [ ] Un comportamiento que el jugador no puede percibir no existe: o lo haces visible (audio, animación, diálogo, telegrafía) o no lo implementes.
- [ ] Grupo que parece coordinado = una regla de objetivo distinta por miembro sobre el mismo motor de movimiento (Pac-Man), no un sistema de escuadrón.
- [ ] Antes de subir la complejidad del cerebro, gasta en el **nivel**: coberturas, rutas alternativas, ventanas, múltiples entradas. La misma IA en un pasillo vacío parece tonta [ver: gamedev/level-design].
- [ ] Barks para hacer visible la intención, y **barks para explicar la inacción** ("no tengo a dónde ir"). Diálogo entre dos personajes antes que anuncios sueltos.
- [ ] Puedes vocalizar una intención sin implementar el comportamiento — pero solo si nada en pantalla la contradice.
- [ ] Mete una pausa de reacción antes de actuar: el tiempo humano de respuesta es lo que se lee como "está pensando".
- [ ] Si hay director de pacing, que sea el director quien sabe dónde está el jugador y el agente quien lo busca con sentidos. El agente no hace trampa.
- [ ] Progresión de capacidades por táctica repetida del jugador, **jamás por sus muertes**.
- [ ] Presupuesta 3-4 criaturas ambientales de cuatro reglas antes que un cerebro más listo para el enemigo principal.
- [ ] Watchdog anti-atasco en todo NPC: sin progreso durante X segundos → replan o reubicación fuera de cámara.
- [ ] Auditoría de la ilusión: graba una pelea, míralas en cámara lenta y anota en qué segundo exacto se rompió el hechizo. Ahí está el trabajo, no en el algoritmo.
- [ ] LLM en NPCs solo si la conversación es la mecánica; nunca como sustituto de la §§1-5.

## Errores comunes

| Error | Síntoma | Antídoto |
|---|---|---|
| Subir la complejidad del algoritmo para arreglar "se siente tonto" | Semanas en un planner y el enemigo sigue sin impresionar | El problema casi siempre es el nivel o la legibilidad, no el cerebro (§3) |
| Implementar coordinación real de escuadrón desde el día 1 | Coste enorme, y el jugador no nota la diferencia | Reglas distintas por miembro + barks; la coordinación compleja emerge (§3) |
| Comportamiento sofisticado sin señal externa | La IA hace algo brillante y el jugador no se entera | Toda decisión importante se anuncia: audio, pose, diálogo |
| Enemigo que reacciona a información que no pudo percibir | "Me vio a través de la pared", sensación de tramposo | Sentidos reales; el director modula presión, no información (§4) |
| Dificultad que sube cuando el jugador muere | Espiral de frustración, abandono | Desbloqueos por táctica exitosa del jugador, no por su fracaso (§4) |
| Copiar "F.E.A.R. tenía la mejor FSM" | Se construye una FSM gigante buscando ese resultado | Era GOAP sobre 3 estados — y el mérito era del nivel y los barks (§3) |
| Enemigos idénticos multiplicados | Cinco copias del mismo comportamiento se leen como cinco bots | Varía la regla de objetivo, no el modelo 3D |
| IA perfecta en el tracking | Puntería inhumana; el jugador siente injusticia, no reto | Error de apuntado, wind-up y tiempo de reacción explícitos |
| Un LLM para "arreglar" NPCs sosos | Latencia, coste, incoherencias, y el combate sigue igual | Barks escritos primero; LLM donde hablar sea la mecánica (§7) |
| NPC atascado contra geometría | Un solo caso destruye la credibilidad de todo el sistema | Watchdog de no-progreso obligatorio (§6) |

## Fuentes

- **"Three States and a Plan: The A.I. of F.E.A.R."** — Jeff Orkin, Monolith Productions / M.I.T. Media Lab, GDC 2006 (PDF original leído) — FSM de tres estados (`Goto`/`Animate`/`UseSmartObject`), GOAP sobre STRIPS con A* en estados del mundo, "all A.I. ever do is move around and play animations", la filosofía de nivel de Monolith, el "dip de siete capas", la ausencia total de squad behaviors complejos, el flanqueo y la pinza como efectos colaterales, las reglas de diálogo (coordinación aparente, vocalizar sin implementar, explicar la inacción) y el "todo es humo y espejos".
- **The Pac-Man Dossier** — Jamey Pittman (gamedeveloper.com) — reglas exactas de targeting de los cuatro fantasmas, el bug de overflow de Pinky/Inky con Pac-Man mirando hacia arriba, scatter mode y esquinas inalcanzables, Cruise Elroy, y que las cuatro "personalidades" salen del objetivo elegido, no de algoritmos distintos.
- **"The Perfect Organism: The AI of Alien: Isolation"** — análisis técnico (gamedeveloper.com; trabajo de Tommy Thompson / AI and Games) — separación director/alien, el alien "nunca hace trampa", sentidos (pasos, disparos, motion tracker a ~1.5 m, ray traces hacia atrás), árbol de 100+ nodos con ~30 en el nivel superior, desbloqueo progresivo de ramas como ilusión de aprendizaje y la exclusión explícita de la muerte del jugador como disparador.
- **"¿Por qué los NPCs parecen inteligentes?"** — TheProphet, YouTube, 2026-07-31 (transcripción completa leída) — origen de este archivo y de los casos elegidos: Pac-Man, Goombas, cucarachas de Half-Life, NextBots, The Forest, F.E.A.R., Alien: Isolation y NPCs con LLM. ⚠️ Divulgación, no fuente técnica: atribuye a *F.E.A.R.* "una buena FSM" (era GOAP) — corregido en §3 contra el paper de Orkin.
- **The Forest — IA social de los caníbales** (observan antes de atacar, patrullas con líder cuya muerte dispara pánico o furia, exploradores que reportan y aumentan la presión al día siguiente): reportado en la fuente de divulgación anterior. **NO VERIFICADO** contra documentación del desarrollador (Endnight) — usar como inspiración de diseño, no citar como implementación confirmada.
- **Base sintetizada:** [ver: pipeline/ia-enemigos] (toda la implementación: NavMesh, FSM/BT/utility, percepción, AI Director de Left 4 Dead, rendimiento), [ver: gamedev/level-design] (encounter design), [ver: gamedev/narrativa-guion] (barks y control autoral), [ver: gamedev/game-feel] + [ver: gamedev/animacion] (telegrafía, wind-up), [ver: gamedev/fundamentos-diseno] (flow, dificultad justa).
