# Fundamentos de game design

> **Cuando cargar este archivo:** al diseñar o evaluar CUALQUIER juego desde cero — definir el core loop, decidir mecánicas, ajustar dificultad/balance, o diagnosticar "el juego no es divertido y no sé por qué". Es el marco base; los demás archivos lo asumen.

## 0. Diagnóstico rápido: síntoma → sección

| Síntoma observado | Ir a |
|---|---|
| "No es divertido y no sé por qué" | §2 (debug MDA backward) y §1 (¿qué patrón se aprende?) |
| Los jugadores dejan de jugar tras dominarlo | §1 (patrón agotado) y §3 (falta loop externo) |
| El gameplay aburre sin recompensas | §3 (action débil — gray-box test) |
| Todos juegan igual / "el juego está resuelto" | §6 (estrategia dominante) y §5 (decisiones falsas) |
| El que va ganando siempre gana / partidas decididas temprano | §6 (feedback positivo sin freno) |
| Los jugadores abandonan en picos de dificultad | §4 (curva y DDA) |
| Los jugadores ignoran una feature entera | §5 (decisión no interesante) y §7 (no sirve a su motivación) |
| Producir contenido no da abasto | §8 (pasar de scripted a sistémico) |
| El multijugador se vació o se volvió tóxico | §7 (dinámica de poblaciones de Bartle) |

## 1. Qué hace divertido un juego (Theory of Fun — Raph Koster)

Tesis central: **la diversión es aprendizaje**. El cerebro busca patrones y libera dopamina (que refuerza aprendizaje y memoria) cuando reconoce y domina uno nuevo. Un juego es un sistema de patrones para masterizar: espaciales (ajedrez), de timing (plataformas), sociales, económicos.

Consecuencias operativas:

| Estado del patrón | Sensación del jugador | Qué hacer |
|---|---|---|
| Patrón nuevo, legible | Diversión (aprendiendo) | Nada — es la zona buena |
| Patrón ya masterizado | Aburrimiento | Introducir variación/profundidad, no más de lo mismo |
| Patrón ilegible (demasiado ruido o dificultad) | Frustración/abandono | Simplificar, telegraph, bajar ruido |
| Patrón trivial | Aburrimiento inmediato | Añadir decisiones reales (ver §5) |

- Un juego "muere" para el jugador cuando no queda nada que aprender. Contenido nuevo con el mismo patrón NO revive el juego; profundidad nueva sí.
- El grind es un patrón agotado que se sigue ejecutando por la recompensa, no por aprendizaje — señal de que el loop premia sin enseñar [ver: psicologia-retencion-negocio].
- La diversión no es una sola cosa. Los **8 tipos de diversión** (del paper MDA, compatible con Koster): Sensation (placer sensorial), Fantasy (imaginación/rol), Narrative (drama), Challenge (superar obstáculos), Fellowship (social), Discovery (explorar), Expression (crearse/expresarse), Submission (pasatiempo, desconectar). Un juego apunta a 2-3, no a los 8.

**Aplicación directa:** antes de añadir una feature, pregunta "¿qué patrón nuevo aprende el jugador con esto?". Si la respuesta es "ninguno, pero da recompensas", es relleno.

## 2. MDA framework (Mechanics → Dynamics → Aesthetics)

Del paper de Hunicke, LeBlanc y Zubek (2004). Tres capas:

| Capa | Qué es | Ejemplo (battle royale) |
|---|---|---|
| **Mechanics** | Reglas, datos, algoritmos — lo que el diseñador escribe | Zona que encoge, loot aleatorio, 1 vida |
| **Dynamics** | Comportamiento que emerge cuando el jugador toca las mecánicas | Rotaciones, camping de borde, third-partying |
| **Aesthetics** | Respuesta emocional del jugador | Tensión creciente, clutch, "una más" |

Insight clave: **el diseñador construye M→D→A, pero el jugador lo vive al revés (A→D→M)**. El jugador siente la estética primero, infiere dinámicas, y casi nunca ve las mecánicas.

Uso práctico:
1. **Diseño forward:** elige 2-3 estéticas objetivo ANTES de escribir mecánicas. Cada mecánica se justifica por la dinámica que produce y la estética que esa dinámica sirve.
2. **Debug backward:** si la estética falla ("se siente tedioso"), no parchees la estética — traza hacia atrás: ¿qué dinámica produce el tedio? ¿qué mecánica genera esa dinámica? Cambia la mecánica.
3. **Predicción de dinámicas:** toda mecánica genera dinámicas no previstas. Playtest para descubrirlas; no se pueden razonar todas en papel.

## 3. Core loop y loops anidados

El core loop es lo que el jugador hace repetidamente durante TODO el juego, en diagrama simple. Estructura mínima de 3 pasos (Mobile Free To Play):

```
ACTION (gameplay: un combate, un nivel, una carrera)
   → REWARD (moneda, recurso, loot, XP)
   → PROGRESS (invertir el reward: upgrade, desbloqueo, avance de mapa)
   → vuelve a ACTION, ahora cambiada por el progreso
```

**Si falta uno de los tres, el loop no funciona.** Y el PROGRESS debe alterar el ACTION (nuevo poder, nuevo enemigo alcanzable); si no, es una barra de relleno.

**Loops anidados:** ciclos pequeños dentro de grandes. Ejemplo típico:
- Loop de momento (segundos): disparar/saltar/matchear — vive del game feel [ver: game-feel]
- Loop de sesión (minutos): completar nivel/partida → reward
- Meta loop (días/semanas): progresión de cuenta, colección, ranking

Un móvil casual necesita 2-3 loops; un MMO puede tener docenas interconectados. Cada loop externo da razón para volver al interno.

**Cómo probarlo:**
- Gray-box: el ACTION a pelo, sin arte ni rewards, ¿aguanta 100 repeticiones? Si necesita rewards para ser tolerable, el problema es el action.
- Señal de loop fuerte vs débil: un loop fuerte sostiene el juego con poco contenido nuevo (Brawl Stars, Clash Royale); un loop débil exige un treadmill infinito de contenido (Candy Crush necesita miles de niveles). Si tu plan es "lo salvamos con más niveles", el loop está fallando.
- "Your game lives and dies based on the design of your core loop" — es lo primero que se prototipa, nunca lo último.

**Cuándo fallan:** loop demasiado complejo o desenfocado (el jugador no sabe qué alimenta qué); reward que no compra nada; progreso que no se siente en el action; punto de parada natural sin gancho al siguiente ciclo.

## 4. Flow aplicado: curvas de dificultad y dificultad adaptativa

Flow (Csikszentmihalyi): estado de absorción total cuando el **desafío ≈ habilidad**. Por encima del canal → ansiedad; por debajo → aburrimiento. La habilidad del jugador SIEMPRE sube, así que la dificultad debe subir con ella — pero no en línea recta.

**Curva práctica:** diente de sierra ascendente — pico de reto, valle de consolidación (usar lo aprendido con holgura), siguiente pico. Los valles no son relleno: son donde el jugador siente su propia mejora. Patrón por mecánica: introducir aislada → combinar → examinar [ver: level-design].

**Dificultad adaptativa (DDA), dos escuelas verificadas:**

1. **Jenova Chen (tesis "Flow in Games", flOw):** DDA player-centric — en vez de que el sistema mida y ajuste, embebe **elecciones subconscientes de dificultad dentro del play** (en flOw, el jugador elige a qué profundidad nadar = elige dificultad sin menú). El jugador autorregula su canal de flow. Barato de implementar y no se siente artificial.

2. **Left 4 Dead — AI Director (Michael Booth, Valve):** el sistema estima la "intensidad emocional" de cada superviviente (daño recibido, enemigos cerca, incapacitaciones) y regula la población de amenazas en 4 fases: **Build Up** (presión total hasta cruzar el pico de intensidad) → **Sustain Peak** (3-5 s más) → **Peak Fade** (amenaza mínima hasta que la intensidad decae y hay pausa natural) → **Relax** (30-45 s o hasta avanzar bastante) → repetir. Principio clave: **ajusta pacing (frecuencia), no dificultad (amplitud)** — el jugador no siente que le regalan nada, siente ritmo.

Regla derivada: si haces DDA, que sea invisible o elegida por el jugador. DDA visible que castiga jugar bien se percibe como trampa del sistema.

**Señales en playtest** (aplicación directa del modelo de flow — heurística, no del paper):

| Señal | Diagnóstico | Ajuste |
|---|---|---|
| Muertes repetidas en el mismo punto + abandono | Ansiedad: reto > skill | Bajar pico, mejorar telegraph, checkpoint más cerca |
| Jugador mira el teléfono / acelera sin mirar | Aburrimiento: skill > reto | Subir presión o introducir patrón nuevo |
| Reintenta inmediatamente tras morir sin frustración | Canal de flow correcto | No tocar — es la zona objetivo |
| Gana pero no puede explicar por qué | Patrón ilegible (ruido) | Clarificar feedback causa-efecto antes de tocar números |

## 5. Decisiones significativas (Sid Meier)

"Un juego es una serie de decisiones interesantes" (Meier, formulado en 1989, desarrollado en su charla GDC 2012). Test negativo primero — una decisión NO es interesante si:
- El jugador elige siempre la misma opción (hay estrategia dominante → ver §6), o
- Elige al azar (las opciones no se distinguen o no hay información).

Una decisión interesante tiene:

| Propiedad | Significado |
|---|---|
| **Trade-off** | Cada opción cuesta algo real (espada cara vs recursos; velocidad vs manejo) |
| **Situacional** | La respuesta correcta depende del estado actual del juego, no es fija |
| **Expresión personal** | Refleja estilo (agresivo vs cauto); no hay "respuesta del diseñador" |
| **Persistencia** | Las consecuencias duran; se puede construir sobre ellas |
| **Informada** | El jugador entiende (aprox.) qué implica cada opción ANTES de elegir |

Tipos recurrentes: **riesgo vs recompensa**, **corto vs largo plazo** (¿maravilla o carro de guerra?), **customización** (hasta nombrar ciudades crea inversión).

Heurísticas de Meier:
- Errar del lado de dar **demasiada** información antes que poca.
- **Feedback en cada decisión**: sonido, visual o texto que reconozca la elección [ver: game-feel].
- Usar convenciones de género para reducir carga cognitiva — innovar donde importa, no en todo.
- Pacing de decisiones: ni avalancha constante ni desierto.
- **Cortar sin piedad**: ~1/3 de las mecánicas que probaba se eliminaban. Prototipar → jugar → cortar.

**Auditoría de una decisión concreta** (aplicar a cada choice del juego):
1. ¿Existe una situación realista donde cada opción sea la mejor? (si no → dominante o relleno)
2. ¿El jugador tiene la información para razonarla? (si no → es azar disfrazado)
3. ¿Cuesta algo elegirla? (sin coste de oportunidad no hay decisión)
4. ¿La consecuencia se nota y persiste? (si se olvida en 10 segundos, no pesó)
5. ¿Dos jugadores con estilos distintos elegirían distinto? (expresión personal)

## 6. Balance: coste/beneficio, estrategias dominantes, feedback loops

Balance (Ian Schreiber, *Game Balance Concepts*): "decidir qué números usar" — todo juego tiene números, explícitos o implícitos.

**Coste/beneficio:** toda opción tiene coste total (recursos, tiempo, riesgo, coste de oportunidad) y beneficio total. Opciones al mismo precio deben rendir parecido en promedio pero distinto según situación — ahí nace la decisión interesante (§5).

**Estrategia dominante:** una opción que siempre es la mejor. Mata todas las decisiones cercanas (nadie elige lo demás). Detección: telemetría o playtest — si el pick rate de una opción se dispara, o los jugadores fuertes convergen en una sola línea, hay dominante. Fix: subir su coste, bajar su efecto, o darle un counter.

**Mecánicas intransitivas (piedra-papel-tijera):** ningún elemento domina; A>B>C>A. Herramienta estándar para unidades de RTS/fighting. Ajustar los valores de victoria cambia las frecuencias óptimas de uso — se puede balancear la meta tocando payoffs sin tocar el ciclo.

**Feedback loops:**

| Tipo | Efecto | Ejemplo verificado | Úsalo para | Riesgo |
|---|---|---|---|---|
| **Positivo** (el que gana, gana más) | Amplifica ventajas, acorta la partida | Monopoly: más propiedades → más renta → más propiedades | Cerrar partidas, sensación de snowball/poder | El perdedor queda eliminado de facto mucho antes del final; partida decidida temprano |
| **Negativo** (el que pierde recibe ayuda) | Comprime diferencias, alarga la tensión | Mario Kart: ítems mejores cuanto más atrás vas (rubber-banding, blue shell) | Mantener a todos en la pelea, multijugador casual | Castiga jugar bien; jugadores competitivos lo detestan si es fuerte/visible |

Un juego sano suele combinar: negativo durante la partida (que nadie quede fuera), positivo al final (que la partida cierre).

**Advertencia de Schreiber:** subastas, kill-the-leader y mecánicas "que los jugadores balanceen" usadas como parche esconden el problema de raíz en vez de arreglarlo. Balancea los números, no delegues el balance.

**Otras palancas:** determinismo vs azar (el azar evita que el juego se "resuelva" y comprime diferencias de skill), información perfecta vs oculta (lo oculto crea profundidad vía incertidumbre y bluff), y el metagame (lo que pasa entre partidas — mazos, builds — también se balancea).

## 7. Tipos de jugador y motivación

**Taxonomía de Bartle** (paper "Hearts, Clubs, Diamonds, Spades", origen: MUDs multijugador). Dos ejes: actuar↔interactuar × jugadores↔mundo:

| Tipo | Quiere | Se le sirve con |
|---|---|---|
| **Achiever** (♦) | Puntos, niveles, estatus | Progresión medible, rankings, logros |
| **Explorer** (♠) | Entender cómo funciona el sistema, descubrir | Secretos, profundidad de sistemas, rincones del mundo |
| **Socialiser** (♥) | Relaciones; "el mundo es solo el escenario" | Chat, gremios, actividades cooperativas |
| **Killer** (♣) | Imponerse SOBRE otras personas | PvP, dominación con consecuencias reales |

Dinámica de poblaciones (multijugador): killers dependen de achievers como presa (equilibrio: demasiados killers espantan a los achievers y luego se aburren y se van); socialisers son los más volátiles — se atraen entre sí (feedback positivo) pero huyen en masa ante killers; explorers son los más estables. Palancas de diseño para mover la mezcla: sistemas de comunicación (→ jugadores), tamaño/profundidad del mundo (→ mundo), libertad de acción (→ actuar), claridad de información (→ interactuar). Caveat: taxonomía descriptiva de mundos virtuales multijugador — úsala como lente de audiencia, no como spec.

**Self-Determination Theory aplicada (Ryan, Rigby & Przybylski, 2006 — modelo PENS):** el disfrute y la intención de seguir jugando se predicen por la satisfacción de 3 necesidades psicológicas (validado empíricamente en varios estudios con juegos reales):

| Necesidad | En el juego | Mecánicas que la sirven |
|---|---|---|
| **Competence** | Sentirse capaz y en crecimiento | Reto calibrado (§4), feedback claro, mastery visible |
| **Autonomy** | Elegir con sentido, no ser arrastrado | Decisiones reales (§5), múltiples estrategias válidas, metas opcionales |
| **Relatedness** | Conexión con otros (o con NPCs que responden) | Co-op, gremios, NPCs que reconocen al jugador |

Uso: PENS explica el POR QUÉ engancha (necesidades), Bartle el A QUIÉN sirves (segmentos). Diseña para las 3 necesidades siempre; segmenta con Bartle solo si es multijugador. Motivación intrínseca (las 3 necesidades) retiene más que recompensas extrínsecas puras [ver: psicologia-retencion-negocio].

## 8. Sistemas emergentes vs contenido scripted

**Emergente** = reglas globales consistentes que interactúan; las situaciones las genera el jugador. **Scripted** = momentos autorados uno a uno (niveles diseñados a mano, set-pieces, cutscenes).

Caso canon emergente — **Zelda: Breath of the Wild (GDC 2017, Nintendo):** "multiplicative gameplay". En vez de N soluciones scripted, motores de física + "química" cuyas reglas se multiplican entre sí. El chemistry engine es una calculadora de ESTADOS basada en 3 reglas: (1) los elementos (fuego, agua, hielo, electricidad, viento) cambian el estado de los materiales; (2) los elementos cambian el estado de otros elementos (agua apaga fuego); (3) los materiales no cambian el estado de otros materiales. Clave adicional: basaron las reglas en expectativas del mundo real (el fuego quema madera, el metal conduce rayos, las rocas ruedan cuesta abajo) → **no necesitan tutorial**; el jugador experimenta y las reglas se enseñan solas. Los immersive sims (Deus Ex, System Shock) siguen la misma filosofía: reglas globales consistentes, mínimas excepciones scripted, ninguna solución impuesta.

| Criterio | Sistemas emergentes | Contenido scripted |
|---|---|---|
| Coste por hora de juego | Alto al inicio, luego el contenido se multiplica solo | Lineal: cada hora nueva se paga entera (treadmill) |
| Replayability | Alta | Baja (se consume una vez) |
| Control del diseñador | Bajo — habrá exploits y momentos rotos | Total — ritmo y drama exactos |
| Riesgos | Exploits, balance imprevisible, complejidad que abruma | Costoso de producir, se agota, jugador pasivo |
| Ideal para | Sandbox, roguelike, sim, multijugador competitivo | Narrativa, set-pieces, tutorial, momentos firmados |

**Cuándo cada uno:**
- Equipo pequeño / solo dev / agente: **prioriza sistemas**. Pocas reglas ortogonales que interactúen rinden más contenido por línea de código que niveles a mano. Regla BOTW: mejor 3 reglas que se multiplican que 30 casos especiales.
- Scripted donde el momento exacto importa: apertura del juego, beats narrativos, enseñanza de una mecánica concreta [ver: narrativa-guion] [ver: ux-ui-onboarding].
- El estándar real es **híbrido**: esqueleto scripted (arcos, misiones clave) + carne sistémica (combate, economía, mundo). Lo sistémico genera las anécdotas que el jugador cuenta ("me pasó X"); lo scripted genera los momentos que todos comparten.
- Prueba de consistencia sistémica: si una regla funciona en un sitio y no en otro sin razón visible ("este fuego quema, este no"), la confianza del jugador en el sistema muere y deja de experimentar.

## Reglas prácticas

- [ ] Define 2-3 estéticas objetivo (de los 8 tipos de fun) ANTES de la primera mecánica; escribe cada mecánica junto a la dinámica que debe producir.
- [ ] Prototipa el core loop primero y en gray-box; si el ACTION no aguanta 100 repeticiones sin arte ni rewards, no sigas construyendo encima.
- [ ] Verifica que el loop tiene los 3 pasos (action → reward → progress) y que el progress CAMBIA el action.
- [ ] Dibuja el diagrama del core loop en ≤6 cajas; si no cabe, está desenfocado.
- [ ] Por cada decisión que ofrezcas, pásale el test de Meier: ¿alguien elegiría cada opción en alguna situación? Si una opción nunca se elige o siempre se elige, elimínala o rebalancéala.
- [ ] Da información de sobra antes de cada decisión y feedback inmediato después (sonido/visual/texto).
- [ ] Toda feature nueva debe enseñar un patrón nuevo; si solo añade rewards, es relleno — córtala o convierte en profundidad.
- [ ] Curva de dificultad en diente de sierra: pico de reto → valle de consolidación; nueva mecánica siempre aislada antes de combinarla.
- [ ] Si implementas DDA: invisible (regula pacing/frecuencia, no amplitud, estilo AI Director) o elegida en el play (estilo flOw). Nunca DDA visible que castigue jugar bien.
- [ ] Busca estrategias dominantes con datos (pick rates, convergencia de jugadores fuertes), no con intuición.
- [ ] Estructura counters como ciclo intransitivo (A>B>C>A) antes que como lista plana de stats.
- [ ] Combina feedback negativo durante la partida (mantener a todos vivos) con positivo al cierre (que la partida termine).
- [ ] Cubre las 3 necesidades SDT en todo juego: competence (reto+feedback), autonomy (estrategias válidas múltiples), relatedness (social o NPCs que responden).
- [ ] En multijugador, decide qué mezcla de Bartle quieres y revisa qué palancas (comunicación, mundo, PvP, información) la empujan.
- [ ] Con equipo chico: pocas reglas globales consistentes > mucho contenido a mano. Reserva scripted para apertura, tutorial y beats narrativos.
- [ ] Basa las reglas sistémicas en expectativas del mundo real para que se enseñen solas sin tutorial.
- [ ] Presupuesta cortar ~1/3 de las mecánicas prototipadas; si nunca cortas nada, no estás playtesteando de verdad.
- [ ] Cuando "no es divertido", debug MDA hacia atrás: emoción fallida → qué dinámica la causa → qué mecánica causa la dinámica. Cambia solo la mecánica.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Parchear la estética directamente ("añade partículas, será más fun") cuando la dinámica está rota | Debug MDA backward: la causa siempre está en una mecánica; game feel amplifica un loop bueno, no arregla uno malo |
| Core loop que se sostiene solo por rewards (el action aburre) | Gray-box test del action a pelo; si falla, rediseñar el action, no subir los rewards |
| Salvar un loop débil con treadmill de contenido ("faltan niveles") | El contenido se consume; la profundidad no. Añadir interacciones entre reglas, no volumen |
| Estrategia dominante sin detectar (todos juegan igual y "el juego se resolvió") | Telemetría de pick rates + mirar a los jugadores fuertes; coste↑, efecto↓ o counter nuevo |
| Feedback positivo sin freno: partida decidida al 30% pero dura 100% | Feedback negativo suave en medio + condiciones de cierre rápido cuando la ventaja es irreversible |
| Rubber-banding fuerte y visible en juego competitivo | Reservar feedback negativo agresivo para casual/party; en competitivo, comprimir con matchmaking, no dentro de la partida |
| Dificultad lineal siempre ascendente sin valles | Diente de sierra; los valles son donde el jugador siente que mejoró |
| DDA que baja la dificultad de forma visible al morir | Regular pacing (frecuencia de amenazas) o dar la elección dentro del play; la amplitud no se toca a ojos del jugador |
| Decisiones "falsas": opciones que no se distinguen o sin información para elegir | Test de Meier (¿siempre igual? ¿al azar?) + dar más información de la que crees necesaria |
| Diseñar solo para achievers (progresión y números) e ignorar el resto de motivaciones | Checklist SDT (competence/autonomy/relatedness) + revisar qué tipos Bartle alimenta cada sistema |
| Sistemas emergentes con excepciones inconsistentes ("este fuego no quema") | Las reglas globales no tienen excepciones silenciosas; si necesitas una excepción, hazla visible y diegética |
| Mecánicas acumuladas que nadie corta ("ya la programamos, se queda") | Cuota de corte estilo Meier (~1/3); el coste hundido no es argumento de diseño |
| Balance delegado en mecánicas parche (kill-the-leader, subastas) sin arreglar los números | Los parches esconden la raíz; primero cost/benefit real de cada opción, después mecánicas sociales |

## Fuentes

- **MDA: A Formal Approach to Game Design and Game Research** — Robin Hunicke, Marc LeBlanc, Robert Zubek (paper, 2004; PDF en cs.northwestern.edu) — el framework M/D/A, los 8 tipos de fun y el método de diseño forward / debug backward. Leído directo del PDF.
- **A Theory of Fun for Game Design** — Raph Koster (libro, 2004; ideas centrales vía resúmenes múltiples y artículo de aniversario) — fun = aprendizaje de patrones; aburrimiento al masterizar; base dopaminérgica.
- **"Raph Koster's Theory of Fun, ten years on"** — Game Developer (Gamasutra), 2013 — Koster mismo revisita la tesis: la ciencia posterior la valida; dopamina refuerza aprendizaje y memoria.
- **"Interesting Decisions"** — Sid Meier, GDC 2012 (vía crónica de Game Developer) — test negativo de decisiones, propiedades (trade-off, situacional, expresión, persistencia, información), tipos, y la heurística de cortar ~1/3 de mecánicas.
- **Game Balance Concepts, Level 1** — Ian Schreiber (curso abierto, gamebalanceconcepts.wordpress.com) — balance como números, determinismo/solvabilidad, información, intransitividad (RPS), advertencia sobre mecánicas-parche, metagame.
- **"Feedback Loops in Games"** — Systems & Us + fuentes secundarias (GameDev Gems, Machinations.io) — Monopoly como feedback positivo canónico; Mario Kart/blue shell como negativo (rubber-banding) y sus trade-offs.
- **Flow in Games** — Jenova Chen (tesis MFA, USC, 2006; jenovachen.com/flowingames) — flow de Csikszentmihalyi aplicado; DDA player-centric con elecciones embebidas en el play; validado con flOw.
- **The AI Systems of Left 4 Dead** — Michael Booth, Valve (presentación, 2009; PDF en steamcdn) — Adaptive Dramatic Pacing: estimador de intensidad + fases Build Up / Sustain Peak (3-5 s) / Peak Fade / Relax (30-45 s); ajusta pacing, no dificultad.
- **Hearts, Clubs, Diamonds, Spades: Players Who Suit MUDs** — Richard Bartle (paper, 1996; mud.co.uk) — los 4 tipos, los 2 ejes, dinámica de poblaciones y palancas de diseño para mover la mezcla. Leído directo.
- **The Motivational Pull of Video Games: A Self-Determination Theory Approach** — Ryan, Rigby & Przybylski (2006) + modelo PENS (selfdeterminationtheory.org) — competence/autonomy/relatedness predicen disfrute e intención de seguir jugando; base empírica multi-estudio.
- **"Crafting A Strong Core Loop"** — Mobile Free To Play (Adam Telfer) — estructura action→reward→progress, "el juego vive o muere por su core loop", loop fuerte vs treadmill de contenido (Candy Crush vs Brawl Stars). Leído directo.
- **"Change and Constant: Breaking Conventions with BOTW"** — Nintendo (Fujibayashi/Dohta/Takizawa), GDC 2017 (vía crónicas de Thumbsticks/Engadget) — multiplicative gameplay; chemistry engine (3 reglas de elementos/materiales); reglas basadas en la realidad para eliminar tutoriales.
- **Emergent vs scripted gameplay** — Blood Moon Interactive + Wikipedia (Emergent gameplay) + The Artifice (systemic games) — trade-offs (replayability/control/exploits), immersive sims como reglas globales con mínimas excepciones, enfoque híbrido como estándar.
