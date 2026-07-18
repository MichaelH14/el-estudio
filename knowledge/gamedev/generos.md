# Géneros y sus convenciones

> **Cuando cargar este archivo:** al elegir o validar el género de un juego nuevo, al auditar si un diseño cumple las expectativas de su género, o al estimar alcance/mercado de un proyecto según su género. Complementa [ver: fundamentos-diseno] y [ver: psicologia-retencion-negocio].

## Principio rector

Un género es una **promesa al jugador**: un contrato de convenciones que él da por hechas sin que nadie se las explique. Innovar se hace *encima* del contrato, no rompiéndolo por ignorancia. Antes de diseñar en un género: (1) listar sus convenciones innegociables, (2) jugar/estudiar 3-5 referentes actuales, (3) decidir conscientemente cuál convención se rompe y por qué. Romper una convención sin saber que existe es el error de dev nuevo más caro que existe.

## Tabla resumen

| Género | Promesa central | Innegociable #1 | Solo dev viable | Mercado 2026 (resumen) |
|---|---|---|---|---|
| Plataformas | Control perfecto del movimiento | Forgiveness (coyote time, buffering) | Sí (2D) | Saturado, débil comercialmente en Steam |
| Puzzle | El "aha" es mío, no del juego | Undo/reset instantáneo | Sí | Saturado, difícil de vender |
| Roguelike/lite | Cada run cuenta una historia distinta | Muerte justa + replayability real | Sí (ideal) | Nicho sano: 104 action-roguelikes >$1M en Steam |
| RPG / Action-RPG | Progresión y build propios | Save robusto + QoL moderno | Solo con scope brutal | 17% del revenue de Steam; audiencia enorme |
| Shooter | Feedback inmediato al apuntar/disparar | Game feel del arma | Solo single-player | Winner-take-all en multiplayer |
| Idle/Incremental | Progreso incluso ausente | Curva exponencial bien tuneada + prestige | Sí (ideal) | Retención altísima; nicho estable |
| Hyper/hybrid-casual | Entender en 3 segundos | Onboarding cero fricción | Sí, pero el negocio es UA | Hyper puro murió como negocio; hybrid-casual crece |
| Party | Que el grupo se ría | Fricción cero para entrar | Sí (local) | Nicho estable, dominado por Jackbox |
| Deportes/Carreras | Fantasía de competencia justa | Assists invisibles + rubber-banding | Solo arcade | ~1% del revenue Steam; IP licenciada domina sim |
| Estrategia | Mis decisiones importan más que mi reflejo | IA que *parece* inteligente | Solo táctico pequeño | 14% revenue Steam; 4X móvil en boom |
| Horror | Miedo controlado que yo elegí | Atmósfera > sustos; dread sostenido | Sí (ideal) | #1 en éxito para devs pequeños en Steam |
| Multijugador competitivo | Partidas justas cuando yo quiera | Netcode + matchmaking + población | ⛔ Casi nunca | Costo 3-5x; problema huevo-gallina de jugadores |

---

## Plataformas

**Pilares:** el personaje ES el juego. El jugador compra la promesa de que morir siempre fue su culpa y que el control es perfecto. Nivel = secuencia de micro-retos legibles [ver: level-design].

**Convenciones que el jugador da por hechas** (Celeste las implementa todas; documentadas por Maddy Thorson en "Celeste & Forgiveness"):
- **Coyote time**: saltar unos frames después de dejar la plataforma.
- **Jump buffering**: input de salto antes de aterrizar se ejecuta al tocar suelo.
- **Gravedad reducida en el ápex** (Celeste usa mitad de gravedad) para ajustar el aterrizaje.
- **Corner correction**: si golpeas una esquina con la cabeza o en dash, el juego te desplaza para no matarte el momentum.
- **Ventanas amplias**: Celeste permite wall jump a 2 px de la pared, super wall jump a 5 px.
- Salto de altura variable (soltar el botón corta el salto), respawn instantáneo, checkpoints generosos.

**Del GDC "Level Design Workshop: Designing Celeste"**: cada pantalla es una micro-historia autocontenida; cada capítulo introduce ~3 mecánicas nuevas; el juego enseña 40+ mecánicas sin tutorial explícito, por composición de nivel.

**Errores de dev nuevo:** salto "floaty" sin peso; física sin forgiveness ("pero es que técnicamente no tocaste el suelo"); castigar con retroceso largo tras morir; enseñar con texto en vez de con el nivel.

**Solo dev:** 2D totalmente viable (motor + tilemaps es territorio conocido). El costo real está en la CANTIDAD de niveles buenos: presupuestar iteración de niveles, no solo mecánicas.

**Mercado 2026:** débil. En el análisis de hits de Steam de Zukowski (early 2025), plataformas 2D/3D y metroidvanias quedaron SIN representación entre los éxitos. Se compite contra clásicos baratos e infinitos. Solo destacan con hook extremo o ejecución excepcional.

## Puzzle

**Pilares:** la moneda del género es el momento "aha", y tiene que sentirse GANADO por el jugador, no regalado ni forzado. Referencia canónica: Elyot Grant, "30 Puzzle Design Lessons From The World's Greatest Puzzle Communities" (GDC 2021, hay versión extendida de 3h en YouTube) — destila métodos de comunidades de puzzles (escape rooms, crosswords, chess compositions) aplicables a videojuegos.

**Convenciones innegociables:**
- **Undo y reset instantáneos y sin castigo** (estándar del género moderno: Baba Is You, Stephen's Sausage Roll).
- Toda la información necesaria visible: nada de pixel-hunting ni soluciones que dependan de info oculta.
- Curva: introducir mecánica → explorar sus consecuencias → combinarla con las anteriores → twist.
- Saltarse un puzzle atascado (selección de niveles no lineal) o sistema de hints.
- El puzzle enseña su propia regla con un primer nivel trivial que la aísla.

**Errores de dev nuevo:** puzzles que se resuelven por fuerza bruta (el espacio de estados es tan chico que probar todo es más rápido que pensar); dificultad = tedio (más pasos, no más insight); enamorarse de un puzzle que solo el autor entiende; no hacer playtest ciego (el diseñador NO puede evaluar dificultad de su propio puzzle).

**Solo dev:** ideal en producción (arte y audio mínimos), pero el diseño de contenido es el 90% del trabajo y no se puede delegar ni generar barato.

**Mercado 2026:** saturado y de precio bajo en PC (ausente de los hits de Steam early 2025 según Zukowski). En móvil, puzzle casual vive de UA y liveops, no del diseño. Vender puzzle premium requiere estética/hook fuerte.

## Roguelike / Roguelite

**Pilares** (fuente: Josh Ge, "How to Make a Roguelike", Roguelike Celebration 2018, versión texto en Grid Sage Games): gameplay primero — permadeath + generación procedural son los elementos tradicionales, pero lo central es que **cada run sea interesante por sí misma**. Test de Ge: *"If your game only has this mechanic, is it fun?"* — la diversión minute-to-minute debe salir de la mecánica core, no de sistemas secundarios.

**Convenciones innegociables:**
- **Muerte justa**: el jugador debe poder rastrear su muerte a SUS decisiones, no al RNG puro.
- **Replayability real**: variedad de builds/items/situaciones que interactúan (sinergias), no solo mapas barajados.
- Roguelite además: **meta-progresión** entre runs (desbloqueos, mejoras permanentes) para que ninguna run se sienta perdida — Vampire Survivors lo ejecuta con recompensas multicapa (oro en la run → mejoras entre runs → achievements que empujan a variar personaje/estrategia).
- Información suficiente para decidir: logs, tooltips, preview de peligro.
- Runs con duración objetivo clara (VS: ~30 min; Slay the Spire: ~45-60 min).

**Errores de dev nuevo (directo de Ge):** desarrollar en múltiples direcciones a la vez en vez de ir directo al loop jugable mínimo; intentar el "roguelike soñado" como primer proyecto; procgen antes que gameplay. Su jerarquía de scope: Tier 1 movimiento + mapa procedural + loop básico → Tier 2 combate/items/progresión → Tier 3 lo demás, solo tras validar. Otro error: tema "otra mazmorra de fantasía" — temas subutilizados (piratas, tanques WW2, cyberpunk) son hook gratis; ejemplo de Ge: Armoured Commander, hecho en 1 año por un dev sin experiencia.

**Solo dev:** el género MÁS amigable para 1 persona: assets reutilizados al máximo por el procgen, contenido = sistemas, comunidad de apoyo enorme (r/RoguelikeDev, 7DRL jam como forcing function). Vampire Survivors: 1 dev, motor Phaser, assets comprados/gratis, una sola mecánica core (caminar + auto-ataque).

**Mercado 2026:** el nicho indie más sano de Steam según GameDiscoverCo: **104 action-roguelikes han pasado $1M de revenue, 70+ lanzados desde 2020** — hay demanda continua y espacio para entradas nuevas, a diferencia de los géneros winner-take-all.

## RPG y Action-RPG

**Pilares:** progresión de personaje + build ownership ("MI personaje") + un mundo que responde. Sub-género fija expectativas exactas: un jugador de turn-based espera turn-based; un jugador de ARPG espera loot con rareza, stats comparables y combate con peso [ver: mecanicas-sistemas].

**Convenciones innegociables:**
- **Save robusto y conveniente**: autosave + save manual rápido. Save points lentos o escasos hoy se leen como falta de respeto.
- QoL moderno: fast travel, gestión de inventario decente, mapa con marcadores, comparación de equipo en tooltip.
- Curva de progresión sin muros de grind obligatorio no anunciado.
- En ARPG: feedback físico del golpe (hit-stop, sonido, números si el estilo lo pide) [ver: game-feel].
- Decisiones de build que importan y se pueden respec (o al menos entender antes de comprometerse).

**Errores de dev nuevo:** subestimar el contenido — un RPG es el género más caro por hora de juego (quests, diálogo, items, balance, mundo); sistemas profundos sobre un combate aburrido; economía rota porque nadie hizo la hoja de cálculo [ver: mecanicas-sistemas]; ignorar QoL "porque los clásicos no lo tenían".

**Solo dev:** solo con recorte brutal de scope o años de vida. El caso extremo documentado: Stardew Valley — Eric Barone hizo TODO (código, arte, música, escritura) en 4.5 años a ~10 h/día, 7 días/semana; 50M+ copias a feb 2026. Es el outlier que prueba la regla, no el plan a imitar. Alternativa realista: RPG corto y sistémico (10-15 h), o action-roguelike con progresión RPG.

**Mercado 2026:** Role-Playing = 17.11% del revenue histórico de Steam (GameDiscoverCo); dentro del género, Action RPG es el sub-género top (26.45%, $3.89B), seguido de MMORPG ($3.69B) y CRPG ($2.69B). Audiencia enorme y hambrienta, pero espera cantidad y pulido.

## Shooter

**Pilares:** el arma es el personaje. Todo se juzga en los primeros 30 segundos de disparar: respuesta del input, retroceso, sonido, impacto en el enemigo [ver: game-feel, audio].

**Convenciones innegociables:**
- Feedback de impacto en capas: hitmarker/reacción del enemigo + sonido distinto en headshot + kill confirm.
- Recarga con animación cancelable o al menos predecible; contador de munición legible.
- Headshot premiado; hitboxes coherentes con el modelo visual.
- Sensibilidad de aim configurable (y en consola, aim assist — todos los shooters de consola lo llevan).
- TTK (time-to-kill) consistente: morir debe ser explicable ("me flanquearon"), no aleatorio.

**Errores de dev nuevo:** armas que se sienten iguales entre sí; IA enemiga que solo corre en línea recta al jugador; hacerlo multijugador "porque los shooters son multijugador" (ver sección Multijugador competitivo — es otra disciplina y otro presupuesto).

**Solo dev:** single-player corto tipo boomer-shooter es viable (nicho retro-FPS activo, herramientas maduras). Multijugador: no.

**Mercado 2026:** GameDiscoverCo lo muestra crudo: los arena shooters son el sub-género #1 en revenue de Steam ($9.52B histórico, liderado por Counter-Strike 2), pero solo **29 juegos en la historia** han pasado $1M en arena/battle royale/hero shooter, y apenas **3 desde 2020** pasaron $25M. Es el género más winner-take-all que existe: el revenue gigante es de 5 juegos, no del género.

## Idle / Incremental

**Pilares** (referencia canónica: Anthony Pecorella, "Idle Games: The Mechanics and Monetization of Self-Playing Games", GDC 2015, con métricas de Kongregate — donde los idle tenían las mejores retenciones de la plataforma): progreso que continúa sin el jugador + números que siempre suben + decisiones de optimización.

**Convenciones innegociables:**
- **Generadores** que producen moneda + **upgrades multiplicadores** + **coste exponencial** por compra (factor típico de crecimiento ~1.15x por unidad comprada; la serie "The Math of Idle Games" de Game Developer cubre las matemáticas). El PACING de esa curva es el juego: mal tuneada = juego muerto.
- **Offline progress**: al volver, el juego te dice cuánto ganaste ausente. Es LA promesa del género.
- **Prestige loop**: reset voluntario a cambio de multiplicadores permanentes que aceleran la siguiente pasada. Extiende el juego órdenes de magnitud.
- Cada pocos minutos al principio (y cada sesión después) debe haber ALGO que comprar o decidir.
- Notación legible de números grandes (K, M, B, T… o notación científica configurable).

**Errores de dev nuevo:** curva lineal o mal balanceada (se acaba en una hora o se estanca en un muro); prestige que no compensa (resetear y tardar lo mismo); primera sesión lenta — el hook del idle es la explosión inicial de compras; monetización que vende el juego entero (time-skips que trivializan la curva matan la retención que es todo el negocio).

**Solo dev:** ideal. Arte mínimo, contenido = matemática en una spreadsheet. El trabajo duro es tuning, no producción.

**Mercado 2026:** nicho estable en móvil (con ads+IAP) y en Steam/web. Retención altísima sigue siendo el argumento del género. Competencia alta en móvil por UA; en Steam el idle premium/gratis con DLC tiene su público fiel.

## Hyper-casual y casual móvil

**Pilares:** comprensión en 3 segundos desde el primer frame, sesiones de <2 min, input de un dedo. El "diseño" incluye el ad creative: el juego ES su anuncio.

**Convenciones innegociables:**
- Onboarding cero: se aprende jugando el nivel 1 sin texto [ver: ux-ui-onboarding].
- Fail state suave: perder cuesta segundos, retry instantáneo.
- Progresión visible inmediata (niveles cortos numerados, skins).
- Hybrid-casual además: metagame de retención (colecciones, upgrades, misiones diarias) + IAP encima de ads.

**Errores de dev nuevo:** creer que es un negocio de diseño — es un negocio de **UA (user acquisition)**: CPI vs LTV; sin presupuesto de ads y pipeline de prototipos descartables (los publishers testean decenas y matan casi todos), no hay negocio; copiar un hit hyper-casual 6 meses tarde; ignorar que el modelo ad-only se rompió.

**Solo dev:** hacer EL juego es fácil; hacer EL NEGOCIO requiere publisher o presupuesto de marketing. Prototipar rápido y testear CPI antes de pulir.

**Mercado 2026** (PocketGamer.biz, Udonis, Deconstructor of Fun "State of Mobile 2026"): hyper-casual siguió liderando descargas (22.05B installs en 2025) y revivió algo por mejores CPMs, pero **el modelo ad-only murió como negocio**; la transición a **hybrid-casual es LA tendencia móvil de 2026**: único segmento casual que creció IAP (+20%, $4.2B en el año; top-10 títulos con +67-100% YoY), ARPDAU 4-7x superior al hyper puro ($0.15-0.50 vs $0.03-0.08). Proyección del sector: hyper-casual puro <5% del revenue casual hacia 2027. Casual tradicional en declive de ingresos; ningún juego móvil nuevo alcanzó $1B en 2025.

## Party games

**Pilares** (referencia: los "Jack Principles" de Jackbox Games): el objetivo real no es ganar — es que el grupo se ría. Diseñar para el sofá y para el espectador, no solo para el que tiene el control.

**Convenciones innegociables:**
- **Fricción cero para entrar**: Jackbox lo resolvió con teléfono como controller + room code en navegador, sin app. Cualquier solución propia debe igualar ese estándar: un no-gamer debe estar jugando en <60 segundos.
- Una tarea a la vez, opciones limitadas, siempre claro qué hacer ahora (principio Jackbox de "mantener el ritmo").
- Rondas cortas con momentos de revelación grupal (todos miran la pantalla compartida).
- Que perder sea gracioso: el último lugar también se divierte.
- Escalar de 3 a 8 jugadores sin romperse; opciones de accesibilidad (Jackbox añadió subtítulos, modo sin timer, room code leído en voz alta).
- Contenido "family-friendly toggle" si hay humor subido de tono.

**Errores de dev nuevo:** requerir que todos tengan el juego/hardware; profundidad mecánica que excluye al casual (Jackbox diseña para "la amplitud de Seinfeld": adultos sin experiencia gamer); ignorar streaming — los party games viven de Twitch/YouTube, con participación de audiencia como feature (Jackbox soporta miles de espectadores votando).

**Solo dev:** viable en local/streaming (sin netcode serio). El costo oculto es el CONTENIDO (prompts, preguntas, variedad) y el playtesting grupal constante.

**Mercado 2026:** nicho estable dominado por Jackbox; picos estacionales (fiestas). Vía indie realista: un formato nuevo con hook streameable.

## Deportes y carreras

**Pilares:** fantasía de competencia donde el resultado se siente justo y el vehículo/atleta responde a la intención. Espectro sim ←→ arcade: elegir punto exacto y ser consistente.

**Convenciones innegociables:**
- **Assists como intérprete de intención**: todos los juegos de carreras, incluso los sims, llevan una capa entre el input y la simulación que interpreta lo que el jugador QUIERE (gamedesignskills: si frena girando, probablemente quiere drift). Assists desactivables por niveles (línea de carrera, ABS, control de tracción).
- **Rubber-banding** en arcade: mantener la carrera disputada. La versión bien hecha (Game Developer, "Rubber-Banding as a Design Requirement") no es solo ajustar velocidad — la IA debe adaptarse de formas variadas o el jugador lo nota y se siente estafado.
- Sentido de velocidad (FOV, motion blur, audio) [ver: game-feel]; minimapa/posiciones siempre visibles; rewind o retry rápido en fallos.
- En deportes: reglas del deporte real respetadas (o desviación claramente arcade), stats legibles, temporadas/torneos como estructura de progresión.

**Errores de dev nuevo:** física de manejo "realista" que se siente horrible (la diversión está en la mentira bien contada); rubber-banding solo-velocidad que castiga jugar bien; competir de frente contra IP licenciada (FIFA/EA FC, NBA 2K, Forza poseen la fantasía "oficial").

**Solo dev:** arcade chico sí (kart minimalista, pool, golf, deporte inventado estilo físico). Sim serio o deporte licenciado: no.

**Mercado 2026:** Sports es ~1% del revenue de Steam (GameDiscoverCo) — el dinero del género vive en consola con licencias. Nicho indie que funciona: deportes arcade con twist físico/multijugador local y sim-racing de nicho profundo.

## Estrategia

**Pilares:** las decisiones pesan más que los reflejos; información y planificación son el gameplay. Sub-géneros con contratos muy distintos: RTS (macro+micro en tiempo real), 4X (explorar/expandir/explotar/exterminar en capas), grand strategy, táctico por turnos, tower defense, autobattler.

**Convenciones innegociables:**
- **IA que PARECE inteligente**: la lección clave del diseño de IA para turn-based (Game Developer, "Designing AI Algorithms for Turn-Based Strategy Games") — es casi imposible que la IA venza a un jugador experimentado sin trampa; el objetivo es que sus jugadas parezcan pensadas. Dificultades altas con bonuses transparentes son aceptadas; IA idiota no.
- UI de información: tooltips en TODO, colas de producción, alertas de lo que pasó fuera de pantalla, undo donde no rompa el juego.
- Legibilidad del estado: quién gana, por qué, y qué hacer al respecto.
- Partida nueva ≠ partida idéntica: mapas/facciones/situaciones que varían.
- Automatización de lo tedioso en late game (el micromanagement que era divertido en el turno 10 es tortura en el 200).

**Errores de dev nuevo:** subestimar la IA (es el sistema más caro del género y se nota de inmediato); UI de programador; balance simétrico aburrido o asimétrico roto; scope 4X completo como primer juego (economía + diplomacia + combate + tech tree + IA de todo eso).

**Solo dev:** táctico chico por turnos, tower defense, autobattler o un 4X minimalista (pocas mecánicas, muy interconectadas). Un 4X/RTS completo: no.

**Mercado 2026:** Strategy = 13.97% del revenue histórico de Steam (GameDiscoverCo; MOBA 19.23% del género, RTS 15.33%, Grand Strategy 9.7%, 4X 8.45%). En PC la audiencia es fiel y de nicho profundo. En móvil, los 4X (Last War, Whiteout Survival) lideraron el boom de estrategia de 2025 (Deconstructor of Fun) — pero ese es un negocio de UA masiva, no de diseño indie. Los 4X tradicionales de PC estuvieron ausentes de los hits early 2025 (Zukowski).

## Horror

**Pilares** (fuente principal: Thomas Grip, Frictional Games, "9 Years, 9 Lessons on Horror"): el miedo es una emoción que el jugador ELIGIÓ sentir, como una montaña rusa — debe estar controlado. La imaginación del jugador es el motor: el juego provee materia prima, la mente del jugador hace el resto.

**Las 9 lecciones de Grip, comprimidas:**
1. El horror no es "agradable" — jumpscares en exceso molestan, no asustan.
2. Los jugadores trabajan contra ti: optimizan el miedo fuera del juego (explotan la IA) y luego se quejan de que no asusta. Diseñar anticipando el abuso.
3. Los sustos solos no bastan: Alien/El Exorcista tienen pocos sustos — el trabajo lo hacen anticipación, atmósfera y dread. Espaciar los picos.
4. **El gameplay divertido es contraproducente**: combate fluido y puzzles absorbentes distraen del miedo (Dead Space dominado = emocionante, no aterrador). Amnesia quitó el combate y los jugadores empezaron a reaccionar a sonidos que en otro juego ignorarían.
5. La narrativa es esencial: el contexto convierte un pasillo neutro en uno aterrador [ver: narrativa-guion].
6. El mundo debe parecer real: inconsistencias (glitches, IA absurda) rompen el terror.
7. Mantener vaguedad: sistemas ambiguos (salud poco clara, cordura difusa) asustan más que barras exactas.
8. El jugador necesita un rol definido: protagonista con motivaciones concretas > avatar genérico.
9. La agencia amplifica: el túnel oscuro OPCIONAL asusta más que el obligatorio.

**Convenciones innegociables:** audio como sistema principal de amenaza [ver: audio]; recursos escasos o vulnerabilidad real; safe zones que luego se traicionan; pacing en olas (tensión → alivio → tensión mayor); estructura de mapa que genere ansiedad (los hubs no lineales de Amnesia asustaban más que los mapas lineales de SOMA).

**Errores de dev nuevo:** jumpscare cada 2 minutos (habitúa y aburre); enseñar el monstruo pronto y de cuerpo entero; hacer el combate divertido; iluminar demasiado; ignorar que el streamer es el segundo público (reacciones streameables venden el juego).

**Solo dev:** ideal — el género premia atmósfera y diseño sobre cantidad de contenido; juegos de 2-4 horas son aceptados y hasta preferidos en el nicho.

**Mercado 2026:** **el género con mejor tasa de éxito para devs pequeños en el análisis de Chris Zukowski** ("14 Reasons why every indie game developer should make at least one horror game", howtomarketagame.com): de los juegos tag Horror lanzados en 2022, 88 de 1,341 (6.5%) llegaron a 1,000+ reseñas, con mediana de revenue ~$1,200 — contra 32 de 1,428 (2.2%) en Plataformas, mediana ~$467. Demanda alimentada por streamers, pico estacional en Halloween (Q3-Q4). NO VERIFICADO si ese diferencial se sostiene igual en años posteriores a 2022; el dato es puntual, no una serie de 3 años.

## Multijugador competitivo

**Pilares:** partidas justas, disponibles cuando el jugador quiera, con progresión de skill visible. Es un SERVICIO, no un producto: lanzarlo es el principio del trabajo, no el final.

**Convenciones innegociables:**
- Netcode digno (predicción, compensación de lag, reconciliación); server-authoritative si hay dinero/ranking en juego. El netcode técnico se cubre en la base `pipeline/` (multijugador), no aquí.
- Matchmaking por skill + partidas en <1-2 min de espera.
- Anti-cheat, moderación, reconexión a partida en curso.
- Ranked con temporadas, y contenido nuevo constante (el jugador competitivo consume el juego como servicio).

**El problema real — números citados por la comunidad dev (DevIndieGame, Code Monkey):** multiplayer online cuesta **3-5x** más que el equivalente single-player; lo que sería 6-12 meses se vuelve 2-3 años; y encima del costo técnico está el **problema huevo-gallina**: pocos jugadores → no hay match → los nuevos se van → menos jugadores. Un juego competitivo bueno puede morir SOLO por población, y la mayoría muere de eso, no de calidad.

**Errores de dev nuevo:** "mi juego es como Valorant pero..." como primer proyecto; añadir multiplayer al final ("lo hago single-player y luego le meto online" — el netcode se diseña desde el día 1); subestimar servidores/soporte/moderación como costo permanente; lanzar sin plan para los primeros 1,000 concurrentes.

**Solo dev:** competitivo matchmade: ⛔ prácticamente inviable. Alternativas que SÍ funcionan para 1 persona: co-op por invitación (estilo Lethal Company: P2P/relay, sin matchmaking, los amigos traen a los amigos), asíncrono (ghosts, leaderboards), o local/couch.

**Mercado 2026:** winner-take-all extremo (ver datos de arena shooters en Shooter). El revenue del género es gigante y está encerrado en menos de 10 títulos vivos.

---

## Estado del mercado por género — foto 2026

Datos de GameDiscoverCo (revenue histórico Steam, solo juegos >$1M), análisis de Chris Zukowski (howtomarketagame) y Deconstructor of Fun (móvil):

| Señal | Dato | Implicación para 1 dev |
|---|---|---|
| Revenue Steam por género | Action 58.4%, RPG 17.1%, Strategy 14%, Sim 9.8%, Sports ~1% | El dinero grande está en action/RPG, pero concentradísimo |
| Género más sano para indies | Action roguelike: 104 juegos >$1M, 70+ desde 2020 | Hay espacio real para entradas nuevas |
| Género trampa | Arena/hero shooter/BR: 29 juegos >$1M en la historia | Revenue enorme ≠ oportunidad; es lotería |
| #1 para devs pequeños | Horror (últimos 3 años, análisis Zukowski) | Corto + atmosférico + streameable = fórmula viva |
| En alza Steam 2025 | Simulation (job sims de cuello azul), narrativa (visual novels/walking sims, hits duplicados), crafting/building | Steam premia lo que pocos hacen |
| Tasa de éxito por nicho | Open world survival craft ~24.5% supera 1,000 reseñas; farming ~20.8% (análisis citado por Cloutboost sobre datos Steam) | Nichos "crafty" convierten mejor que la media |
| Débiles en hits Steam 2025 | Plataformas, metroidvania, puzzle, 4X tradicional, city builder puro | No imposibles, pero remar contra corriente |
| Tasa de éxito Horror vs Plataformas (2022) | Horror: 88/1,341 juegos (6.5%) llegó a 1,000+ reseñas, mediana $1,200. Plataformas: 32/1,428 (2.2%), mediana $467 (Zukowski) | El género correcto es la palanca #1 de descubribilidad — mismo esfuerzo, resultado 3x distinto |
| Móvil 2026 | Hybrid-casual único segmento casual creciendo IAP (+20%, $4.2B); 4X móvil en boom; ningún juego nuevo llegó a $1B en 2025 | Móvil = negocio de UA y liveops; sin capital, mejor PC/Steam |
| Dato curioso demos | Hits que mantienen demo post-launch: review score 94.7% vs 84.6% (Zukowski, early 2025) | Demo buena correlaciona con calidad percibida |

**Heurística de selección para un solo dev (síntesis de las fuentes):** elegir géneros donde (a) la audiencia de Steam es hambrienta y la oferta de calidad es baja (horror, sim de nicho, crafting), o (b) el contenido lo generan los sistemas y no la producción (roguelite, idle, puzzle sistémico). Evitar géneros donde se compite por producción (RPG AAA-like, sim racing) o por población (multijugador competitivo). GameDiscoverCo: "los juegos pequeños enfocados en el nicho correcto son los grandes ganadores".

## Reglas prácticas

1. Antes de diseñar: lista las 10 convenciones del género y marca cuáles cumples, cuáles rompes A PROPÓSITO y por qué.
2. Juega/estudia 3-5 referentes ACTUALES del género (no solo los clásicos): las expectativas de QoL las fijó el último hit, no el fundador del género.
3. Plataformas: implementa coyote time, jump buffering y corner correction ANTES de diseñar niveles. Sin eso, todo playtest miente.
4. Puzzle: playtest ciego obligatorio; si 2 de 3 testers resuelven por fuerza bruta o se atascan sin pista, el puzzle está roto.
5. Roguelike: aplica el test de Josh Ge — ¿la mecánica core sola es divertida 10 minutos? Si no, no hay procgen que lo salve.
6. Roguelite: ninguna run puede terminar con las manos vacías — siempre progreso meta (oro, desbloqueo, achievement).
7. RPG: presupuesta el contenido en horas de juego × costo/hora ANTES de comprometerte; es el género más caro por hora [ver: preproduccion].
8. Idle: la curva va en spreadsheet primero (~1.15x coste por compra como punto de partida) y se tunea contra sesiones reales; el prestige debe hacer la segunda pasada notablemente más rápida.
9. Horror: regla de Grip — si una mecánica es demasiado divertida, está robando miedo. Recorta el "fun" que compite con el dread.
10. Horror: espacia los sustos; el tiempo ENTRE sustos, con el jugador imaginando, es donde vive el género.
11. Party: cronometra el onboarding real — de "abro el juego" a "todos jugando" en <60 s, incluyendo a la persona que no juega videojuegos.
12. Shooter/acción: invierte en el game feel del arma/golpe antes que en contenido; 30 segundos de disparo venden (o matan) el juego [ver: game-feel].
13. Estrategia: la IA no necesita ganar al experto — necesita que sus jugadas parezcan pensadas; dificultad extra con bonuses transparentes es aceptable.
14. Carreras/deportes arcade: assists que interpreten intención + rubber-banding variado (nunca solo-velocidad).
15. Multiplayer: si no puedes responder "¿de dónde salen mis primeros 1,000 jugadores concurrentes?", haz el juego co-op por invitación, asíncrono o single-player.
16. Multiplayer: netcode se decide el día 1 de arquitectura, jamás se "añade después".
17. Mercado: antes de comprometerte, revisa cuántos juegos de ese sub-género pasaron 1,000 reseñas en los últimos 3 años (SteamDB/GameDiscoverCo); si el número es ínfimo, no es nicho — es desierto o lotería.
18. Híbridos: cruzar dos géneros hereda las convenciones OBLIGATORIAS de ambos (roguelike-deckbuilder debe funcionar como roguelike Y como juego de cartas); el hook es la cruza, el trabajo es doble contrato.
19. Móvil casual: valida CPI con prototipo y ads antes de pulir nada; si no hay presupuesto de UA, cambia de plataforma o de género.
20. Al portar/elegir plataforma: cada género tiene su casa (horror/sim/estrategia → Steam; hybrid-casual → móvil; party → consola/streaming). No pelear contra la corriente de la plataforma.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Romper una convención sin saber que existía ("mi plataformas no necesita coyote time") | Checklist de convenciones del género antes de la primera línea de código |
| Elegir género por revenue total ("los shooters generan billones") | Mirar el CONTEO de juegos que triunfan, no el revenue: 29 arena shooters >$1M vs 104 action roguelikes >$1M |
| Primer proyecto = el juego soñado del género (el 4X completo, el MMO) | Regla de Josh Ge: proyectos chicos primero; ir directo al loop mínimo jugable y validar |
| Procgen/sistemas antes de que el core loop sea divertido | Test "¿solo esta mecánica es divertida?"; prototipo desechable primero [ver: preproduccion] |
| Horror con gameplay divertido (combate pulido, puzzles absorbentes) | Lección 4 de Grip: recortar diversión que compite con el miedo; el aburrimiento tenso es una herramienta |
| Jumpscares como plan A | Anticipación + atmósfera + dread; sustos espaciados y ganados |
| RPG que ignora QoL moderno "por fidelidad clásica" | Save conveniente, fast travel, tooltips: el estándar lo fija 2026, no 1995 |
| Idle con curva improvisada en código | Spreadsheet de economía primero; tuning contra datos de sesión reales |
| Multiplayer añadido al final del desarrollo | Netcode es arquitectura del día 1; si no, co-op por invitación o asíncrono |
| Lanzar competitivo sin plan de población | El juego muere por matchmaking vacío, no por calidad; población es EL riesgo #1 |
| Puzzle calibrado por el propio diseñador | El autor no puede medir la dificultad de su puzzle; playtest ciego siempre |
| Party game que exige hardware/cuentas a cada jugador | Teléfono como controller / pantalla compartida / entrar en <60 s (estándar Jackbox) |
| Rubber-banding solo-velocidad que castiga ir primero | IA con adaptaciones variadas; el jugador que domina merece ganar |
| Copiar el hit de hace 6 meses (survivors-like #400, hyper-casual clonado) | Entrar a un nicho con demanda probada + UN twist claro de tema o mecánica (ej. Armoured Commander: roguelike de tanques) |
| Estimar el RPG/estrategia como si fuera un plataformas | El costo va en contenido e IA, no en mecánicas; presupuestar por sistemas y horas de contenido |
| "El género X está muerto, seré el renacimiento" | Los datos de hits recientes mandan; renacer un género es apuesta de estudio grande, no de 1 dev |

## Fuentes

- **How to Make a Roguelike — Josh Ge (Grid Sage Games / Roguelike Celebration 2018)** — primer canónico del género: scope por tiers, test de mecánica core, diferenciación por tema. Leído en texto completo (gridsagegames.com/blog/2018/10/how-to-make-a-roguelike).
- **Celeste & Forgiveness — Maddy Thorson (Medium)** — las 10 mecánicas de forgiveness con números exactos (2 px, 5 px, media gravedad en ápex); la biblia del feel plataformero moderno.
- **Level Design Workshop: Designing Celeste — Maddy Thorson (GDC 2017)** — pantalla como micro-historia, ~3 mecánicas por capítulo, 40+ mecánicas enseñadas por composición.
- **9 Years, 9 Lessons on Horror — Thomas Grip (Frictional Games, 2019)** — las 9 lecciones del diseñador de Amnesia/SOMA; base de toda la sección de horror. Leído completo.
- **Which genres have 'ruled' Steam? — GameDiscoverCo newsletter (2025)** — revenue por género/sub-género de Steam (>$1M), el contraste arena shooter (29 juegos) vs action roguelike (104): la tabla de mercado sale de aquí. Leído completo.
- **The hit games of early 2025 — Chris Zukowski (howtomarketagame.com)** — géneros presentes/ausentes en los hits de Steam, narrativa en alza, dato de demos post-launch. Leído completo.
- **14 Reasons why every indie game developer should make at least one horror game — Chris Zukowski (howtomarketagame.com, oct. 2023)** — dato duro verificado: de 1,341 juegos Horror lanzados en 2022, 88 (6.5%) llegaron a 1,000+ reseñas (mediana $1,200), contra 32/1,428 (2.2%, mediana $467) en Plataformas. Es un dato de un solo año (2022), no una serie de 3 años — corregido tras verificación directa del artículo.
- **Idle Games: The Mechanics and Monetization of Self-Playing Games — Anthony Pecorella (GDC 2015, Kongregate)** — retención y loops del género idle; referencia canónica.
- **The Math of Idle Games (serie) — Game Developer** — matemática de curvas exponenciales y prestige; el ~1.15x de coste por compra como baseline.
- **30 Puzzle Design Lessons From The World's Greatest Puzzle Communities — Elyot Grant (GDC 2021)** — referencia canónica de diseño de puzzles (hay Director's Cut de 3h en YouTube); consultada vía resúmenes, no transcripción completa.
- **State of Mobile 2026 — Deconstructor of Fun** — móvil 2026: hybrid-casual y 4X móvil en alza, casual tradicional en declive, ningún juego nuevo a $1B en 2025. Leído completo.
- **What happened to hypercasual? — PocketGamer.biz / Udonis / Game Growth Advisor (2025-2026)** — 22.05B installs hyper-casual 2025, muerte del modelo ad-only, hybrid-casual +20% IAP ($4.2B), ARPDAU comparado.
- **The Jack Principles y diseño de Jackbox — Built In Chicago + Jackbox Games blog** — fricción cero, teléfono como controller, humor sobre victoria, accesibilidad de party games. Leído (Built In Chicago) completo.
- **Vampire Survivors: cobertura de desarrollo — Game Developer + The Conversation (2022-2023)** — solo dev con Phaser y assets baratos, una mecánica core, recompensas multicapa (psicología de recompensa documentada por investigadores).
- **How Stardew Valley creator Eric Barone coped with a four year dev cycle — Game Developer** — el techo real del scope solo-dev en RPG: 4.5 años, todas las disciplinas, jornadas de 10 h.
- **Rubber-Banding as a Design Requirement — Game Developer** + **Racing Game Design — gamedesignskills.com** — assists como intérprete de intención; rubber-banding bien y mal hecho.
- **Designing AI Algorithms for Turn-Based Strategy Games — Game Developer** — la IA de estrategia debe parecer inteligente, no ganar al experto.
- **Why Indie Developers Should Avoid Online Multiplayer Games — DevIndieGame + Code Monkey (unitycodemonkey.com)** — estimaciones 3-5x costo, 6-12 meses → 2-3 años, problema huevo-gallina de población.
