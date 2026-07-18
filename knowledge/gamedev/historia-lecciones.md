# Historia del videojuego en lecciones de diseño

> **Cuando cargar este archivo:** al decidir dirección de diseño, scope o modelo de negocio de un juego nuevo; al evaluar si una idea repite un error histórico conocido; o cuando necesites precedente real ("¿quién resolvió ya este problema y cómo?").

Este archivo NO es trivia. Cada juego aparece porque deja una regla aplicable hoy. Formato: era → hito → lección extraíble.

---

## 1. Era arcade (1972–1984): la elegancia brutal

Contexto de diseño: la máquina cobraba por partida. Eso forzó tres propiedades que siguen siendo el estándar de oro de un core loop: legibilidad en 5 segundos, dificultad que escala, muerte que da ganas de reintentar. [ver: fundamentos-diseno]

| Hito | Qué hizo | Lección extraíble |
|---|---|---|
| **Pong** (1972) | Una regla ("evita perder la bola"), un input | Un juego puede sostenerse con UNA verb + UNA condición de fallo. Empieza ahí y suma solo si hace falta |
| **Space Invaders** (1978) | Los aliens aceleran al morir — efecto colateral del hardware: menos sprites que renderizar = frame más rápido. Nishikado lo detectó en playtest y lo DEJÓ | La curva de dificultad emergente nació de un bug adoptado. Regla: cuando un accidente hace el juego mejor, no lo "arregles" — formalízalo. Y: el éxito del jugador puede SER el mecanismo de dificultad (matas más → va más rápido) |
| **Pac-Man** (1980) | Iwatani diseñó contra la fiebre de shooters espaciales post-Space Invaders: tema de comer, estética cute, cero violencia, apuntando a un público que NO jugaba (mujeres, parejas) | Cuando todos persiguen la misma fiebre, el público desatendido es el océano azul. Diferenciarse por audiencia, no solo por mecánica |
| **Donkey Kong** (1981) | Personaje con silueta y motivación legibles en pixeles | El personaje ES información de gameplay: silueta primero, lore después |

### Pac-Man por dentro: complejidad percibida con código mínimo (Pac-Man Dossier)

- Cada fantasma usa el MISMO algoritmo de pathfinding con distinto punto objetivo: Blinky apunta a Pac-Man; Pinky 4 tiles por delante de él; Inky usa la posición de Blinky + offset; Clyde persigue si está a >8 tiles y huye si está cerca. Cuatro "personalidades" memorables = un algoritmo, cuatro parámetros.
- Modos scatter/chase alternados por timer: los fantasmas se retiran a sus esquinas periódicamente. Sin eso, el juego sería injusto; con eso, respira.
- Dificultad progresiva por parámetros, no por contenido: el tiempo de vulnerabilidad post-energizer baja hasta cero en niveles altos.
- **Regla:** antes de escribir más código de IA, pregunta si puedes variar parámetros de un solo sistema. La "ilusión de inteligencia" es más barata y más legible que la inteligencia real. [ver: mecanicas-sistemas]

### El crash de 1983: el primer castigo por saturación

- Ingresos de consolas en EEUU: ~$3.2B (1983) → ~$100M (1985). Caída de ~97%.
- Causas verificadas: sobreproducción (Goldman Sachs 1983: demanda +100%, producción +175%), avalancha de juegos malos indistinguibles de los buenos antes de comprar, cero control de calidad de plataforma, y computadoras caseras (C64) canibalizando por precio.
- E.T. (Atari, 1982): 5.5 semanas de desarrollo, 1 programador, 4 millones de cartuchos fabricados — más que consolas vendidas ese año. Fue símbolo, no causa: el problema era sistémico.
- Consecuencia directa: Nintendo inventó el Seal of Quality y el control férreo de terceros. El "platform holder como curador" nace aquí.
- **Regla:** cuando el mercado no puede distinguir calidad antes de comprar, la confianza colapsa para TODOS, incluidos los buenos. Se repite en 1983 (cartuchos), ~2012 (App Store), ~2017 (Steam Direct), 2022 (hyper-casual). La defensa del dev chico: señales de calidad verificables — demo, reviews, marca personal.

---

## 2. 8/16-bit (1985–1995): diseño bajo restricciones

Contexto: NES = 8 sprites por scanline, 3 colores por sprite de 8×8, cartuchos de KB. La restricción no fue obstáculo — fue el motor del diseño.

### Mario como manual de restricciones (Miyamoto, Iwata Asks / entrevistas)

- Bigote: dibujar nariz + bigote ahorra dibujar la boca. Gorra: evita dibujar pelo, frente, cejas — y animar pelo al saltar. Overol: hace visibles los brazos para leer la animación de correr. En 16×16 píxeles, CADA rasgo existe por una razón funcional.
- **Regla:** el estilo memorable sale de resolver la restricción, no de ignorarla. Antes de pelear contra tu límite técnico (presupuesto, equipo de 1, arte programmer-art), pregúntate qué identidad visual/mecánica ese límite te REGALA. [ver: arte-direccion]

### Super Mario Bros. 1-1: el tutorial invisible

- Miyamoto: "simulábamos lo que el jugador haría". Mario arranca en el borde izquierdo mirando a la derecha (te invita a avanzar); el primer bloque ? está donde saltarás naturalmente; el hongo viene hacia ti para que aprendas que un power-up no muerde.
- El Goomba fue INVENTADO porque el Koopa (que exige saltar + patear) era demasiado complejo como primer enemigo. Diseñaron un enemigo nuevo solo para que la primera lección fuera de un paso.
- **Regla:** enseña con la disposición del nivel, no con texto. Si tu primer enemigo requiere dos habilidades, diseña uno que requiera una. [ver: level-design] [ver: ux-ui-onboarding]

### Street Fighter II (1991): el género que nació de un bug

- Capcom hizo el input de specials más permisivo (buffer más tolerante). Efecto colateral: podías cancelar la animación de un normal en un special antes de que el rival reaccionara. Lo iban a arreglar; probaron; era más divertido; lo dejaron. Todo fighting game desde entonces tiene sistema de combos.
- **Regla (segunda aparición — patrón confirmado):** los exploits que premian ejecución y conocimiento son profundidad gratis. Antes de parchear un exploit, pregunta: ¿rompe el juego o crea un skill ceiling?

### Sega: cómo se pierde una guerra de plataformas sin perder en hardware

- 32X (1994): pedirle al consumidor comprar un puente (32X) y el destino (Saturn) a la vez. Capcom y Konami cancelaron sus juegos de 32X en meses.
- Saturn (E3 1995): lanzamiento sorpresa 4 meses antes de lo anunciado, a $399, avisando a retailers y desarrolladores al mismo tiempo que al público. KB Toys se negó a venderla; los terceros no llegaron con juegos al lanzamiento.
- **Regla:** una plataforma (o un juego con UGC/mods/comunidad) vive de la confianza de sus socios y jugadores. Sorprender al mercado con decisiones logísticas destruye más valor que cualquier ventaja de timing. Roadmaps: comunica antes de mover fechas.

---

## 3. El salto al 3D (1993–2000): problemas nuevos, soluciones canónicas

### Doom (1993): distribución y apertura como decisiones de DISEÑO

- Shareware: el episodio 1 completo gratis, distribúyelo libremente. Rentable desde el día 1. El "demo generoso que se comparte solo" precede al F2P por 20 años.
- Carmack y Romero separaron motor (doom.exe) de datos (.WAD) DELIBERADAMENTE para que la gente moddeara, contra las objeciones legales/comerciales internas. El modding mantuvo Doom vivo 30+ años y normalizó el modding en toda la industria.
- **Regla:** la arquitectura data-driven no es solo ingeniería limpia — es una decisión de longevidad. Contenido en archivos de datos, motor aparte. Y: regalar tu mejor primera hora es marketing que no puedes comprar.

### Super Mario 64 → Ocarina of Time: los dos problemas del 3D y sus soluciones

| Problema | Síntoma real documentado | Solución canónica |
|---|---|---|
| Cámara en 3D | SM64: la cámara necesitó un personaje (Lakitu) y aun así leer un letrero era dar vueltas alrededor sin poder alinearse (los ejes de cámara y personaje no coinciden) | Cámara como sistema con presupuesto propio de diseño; nunca "se ajusta al final" |
| Apuntar/encarar en 3D | Alinear el facing del personaje con un objetivo era frustrante — cámara, movimiento y facing son 3 cosas que el jugador no puede controlar a la vez | Z-targeting (OoT): lock-on que fija cámara y facing en el objetivo, dejando al jugador solo el movimiento. Inspirado en un show de espadachines (enemigos atacan de a uno) en Toei Kyoto Studio Park |

- **Regla:** cuando el jugador debe controlar N cosas simultáneas y tiene 2 pulgares, automatiza N-2. El lock-on, el auto-aim, la cámara asistida no son "casualizar": son resolver un problema de grados de libertad. Todo action game 3D usa descendientes del Z-targeting. [ver: game-feel]

### Half-Life (1998): narrativa sin quitarle el control al jugador

- Cero cutscenes (salvo una), cero walls of text: todo pasa en el mundo, en primera persona, con secuencias scripteadas mientras conservas el control. Valve construyó herramientas de scripting específicamente para esto. 50+ premios GOTY; definió cómo cuentan historias los FPS.
- **Regla:** cada segundo que le quitas el control al jugador cobras un impuesto de inmersión. Antes de hacer una cutscene, pregunta si el evento puede ocurrir EN el mundo mientras el jugador mira (o no mira — eso también es diseño). [ver: narrativa-guion]

---

## 4. Online y la era HD (2000–2012): audiencias, no specs

| Hito | Lección |
|---|---|
| **World of Warcraft** (2004) y la fiebre de "WoW-killers" | WildStar (2014): 9 años de desarrollo persiguiendo un mercado que ya había cambiado; posicionamiento "hardcore" para una audiencia que había envejecido; suscripción → F2P → cierre (2018). Regla: si tu plan es "X pero mejor", cuando lances competirás contra el X de DENTRO de N años + su ventaja de red. No persigas al líder por su flanco fuerte |
| **Wii** (2006) | Nintendo abandonó la carrera de specs y apuntó a NO-jugadores (familias, mayores). Iwata: "otros ponen el dinero en la pantalla; nosotros en la experiencia". Consola menos potente de su generación; la más vendida. Regla: la potencia técnica no es ventaja competitiva si el rival define el tablero — cambia de tablero (blue ocean) |
| **Demon's Souls / Dark Souls** (2009/2011) | Miyazaki: "creemos en juegos desafiantes, no en injustos o deshonestos"; la muerte como herramienta de aprendizaje; sin tutoriales exhaustivos porque "me gusta que la gente descubra el mundo por sí misma". Creó el subgénero soulslike cuando la industria entera iba hacia lo accesible. Regla: la fricción DISEÑADA (legible, consistente, con culpa siempre del jugador) es una propuesta de valor, no un defecto. Lo contraintuitivo bien ejecutado abre géneros |

---

## 5. La revolución indie (2008–2016): qué demostró cada uno

| Juego | Equipo | Qué demostró (verificado) | Regla para ti |
|---|---|---|---|
| **Braid** (2008) | Jonathan Blow | Un puzzle-platformer de autor podía venderse en consola (XBLA). Blow rechazó la petición de Microsoft de añadir pistas: el juego debía exigir resolución real | Una visión coherente sin diluir es el activo. Los gatekeepers piden suavizar; evalúa si eso mata la propuesta |
| **Minecraft** (2009) | Notch, solo | Alpha pagada (€9.95, con todas las futuras actualizaciones incluidas) desde mayo 2009 en TIGSource; desarrollo dirigido por feedback — hasta polls públicos para decidir la siguiente feature (farming ganó con 39%) | Cobra temprano, itera en público, deja que la comunidad co-diseñe. El early access es un modelo de DESARROLLO, no solo de financiación |
| **Undertale** (2015) | Toby Fox | Un RPG donde puedes no matar a nadie: la mecánica (mercy) ES el mensaje moral, con 3 rutas que reaccionan a tu conducta | La innovación barata está en cuestionar el verbo por defecto del género ("¿y si atacar fuera opcional?") |
| **Stardew Valley** (2016) | Eric Barone, 4.5 años | Un solo dev cubriendo código, pixel art, música y diseño puede superar a la franquicia que imita (Harvest Moon) si itera más años que nadie | El solo dev compite por profundidad y cariño acumulado, no por volumen. El tiempo es tu recurso diferencial |

Patrón de la era: la distribución digital (XBLA, Steam) eliminó al publisher como cuello de botella; lo que quedó como filtro fue la IDEA diferenciada. Ninguno de estos cuatro ganó por producción — ganaron por una premisa que un AAA no podía o no quería tomar.

---

## 6. Móvil y F2P (2008–hoy): la retención como diseño

- **Candy Crush / King:** no venden contenido, venden PROGRESO (boosts, movidas extra en el mapa). Curva de dificultad calibrada con A/B testing masivo para crear puntos de fricción resolubles con compras pequeñas, manteniendo progreso gratis viable. Una década de vigencia por iteración continua, no por lanzamiento.
- **Clash of Clans / Supercell:** timers + IAP + luego suscripción (Gold Pass). La monetización sigue al engagement, nunca al revés: sin retención no hay nada que monetizar. [ver: psicologia-retencion-negocio]
- **Ciclo hyper-casual (2016–2022):** boom por CPI bajo y ads → saturación → descargas -24% en 2022 (a 2.7B) → el modelo murió y renació como **hybrid-casual**: mismo hook simple + meta-progresión + economía IAP + pase de temporada. Según reportes de la industria (Unity, Deconstructor of Fun): 4-7× revenue por usuario activo y 2-3× retención vs hyper-casual puro; único segmento casual creciendo IAP en 2025 (+20%, $4.2B).
- **Regla:** en móvil el juego es el top of funnel; el producto es la retención D1/D7/D30. Si haces móvil en 2026: hook de hyper-casual + profundidad de mid-core es la fórmula dominante, y el mercado castiga el hook solo.

---

## 7. Live-service (2013–2026): pivotes, muertes y la resaca

| Caso | Qué pasó (verificado) | Regla |
|---|---|---|
| **Fortnite** (2017) | Save the World (PvE de pago) era EL juego; el modo Battle Royale — pivote tardío de 2017 sobre tecnología ya construida — se comió al original y definió una era. STW no fue free-to-play hasta 2026 | Construye tecnología y equipo capaces de pivotar rápido. El juego que lanzas puede no ser el juego que te salva |
| **No Man's Sky** (2016) | Sobre-promesa masiva → lanzamiento sin lo prometido → investigación de la autoridad publicitaria UK → Hello Games calló, dejó de prometer y solo habló con updates GRATIS ya hechos (desde Foundation, nov 2016) → Steam pasó de "overwhelmingly negative" a "very positive" (96% en recientes) en ~8 años | La redención existe pero cuesta años de trabajo regalado. Más barato: no vendas el juego que imaginas, vende el que existe. Comunica con builds, no con adjetivos |
| **Anthem** (2019) | Schreier/Kotaku: 6+ años anunciado pero preproducción sin decidir QUÉ juego era hasta ~2017; mencionar a Destiny era tabú (no aprendieron del género que competían); herramientas Frostbite sin soporte; fe en la "BioWare magic" (crunch final que 'siempre' lo salva) como plan; stress leave generalizado. Cerró definitivamente enero 2026 | La preproducción no es opcional: si no puedes decir qué es tu juego en una frase, no tienes juego. Estudiar al líder del género es obligatorio, no traición. La "magia" de fin de proyecto es deuda con interés. [ver: preproduccion] [ver: produccion-proceso] |
| **Concord** (2024) | Hero shooter de $40 lanzado 8 años tarde (desarrollo desde 2016) contra rivales free-to-play con network effects; sin ningún diferenciador; pico de 697 jugadores concurrentes en Steam; cerrado a los 14 días — costo reportado ~$400M (cifra no confirmada oficialmente). Sony admitió falta de user testing y evaluación interna | Triple check antes de entrar a un género PvP establecido: (1) ¿por qué alguien deja su juego actual — donde están sus amigos y su progreso — por el tuyo?, (2) ¿tu modelo de precio compite con "gratis"?, (3) ¿tu fecha compite contra el mercado de HOY o el de cuando empezaste? |
| **La resaca 2025–2026** | De 19 grandes lanzamientos live-service de 2025, la mayoría perdió 80–99% de jugadores para inicios de 2026; 52 títulos apagados a mitad de 2026 (cifras de trackers de industria); ~53% de jugadores prefiere single-player; los publishers están reconstruyendo equipos single-player | El slot de "tu juego como segundo trabajo del jugador" ya está ocupado por 4-5 títulos. El premium single-player terminado y finito es hoy el espacio MENOS saturado |

---

## 8. Innovaciones que definieron géneros — y POR QUÉ funcionaron

| Innovación | Juego origen | Por qué funcionó (el principio, no el feature) |
|---|---|---|
| Dificultad emergente por éxito del jugador | Space Invaders | El desafío escala exactamente al ritmo de la habilidad demostrada |
| IA por parámetros con personalidades | Pac-Man | Legibilidad: el jugador puede modelar y predecir a cada enemigo |
| Tutorial por arquitectura de nivel | Super Mario Bros. | Aprender haciendo > leer; la lección correcta en el momento exacto |
| Combos / cancels | Street Fighter II | Skill expression: distancia visible entre novato y experto con las mismas reglas |
| Modding como plataforma | Doom (.WAD) | Convierte consumidores en productores; el contenido escala sin tu equipo |
| Narrativa en primera persona sin cutscenes | Half-Life | El control ininterrumpido preserva la inmersión que la historia necesita |
| Lock-on / gestión de grados de libertad | Ocarina of Time (Z-targeting) | Automatiza lo que el jugador no puede controlar con 2 pulgares |
| Fricción diseñada + muerte como maestra | Demon's/Dark Souls | Logro proporcional al obstáculo; la consistencia hace la dureza justa |
| Mecánica = mensaje moral | Undertale | El sistema dice lo que la historia predica: coherencia ludonarrativa |
| Early access dirigido por comunidad | Minecraft | Feedback real > diseño especulativo; financia la iteración larga |
| Vender progreso, no contenido | Candy Crush | El deseo ya existe (avanzar); la compra solo quita la fricción |
| Pivote sobre tecnología propia | Fortnite BR | La velocidad de reacción vale más que el plan original |
| Mundo abierto 3D como plataforma de minijuegos | GTA III (2001) | No inventó el sandbox (ya existía en 2D) — lo llevó a 3D con streaming de mundo (cargar geometría/audio sin cortes) y cámara en tercera persona. 97/100 Metacritic, más vendido de EEUU en 2001, 14.5M copias a 2008. Consolidó piezas dispersas en una fórmula reproducible (Mafia, Saints Row, Watch Dogs la copiaron) — la lección: el género lo gana quien empaqueta primero, no siempre quien inventa primero |

---

## 9. Patrones cíclicos de la industria

El mismo ciclo se repite con distinto disfraz: **innovador gana → fiebre de imitadores → saturación → crash/consolidación → los supervivientes definen la era siguiente.**

| Ciclo | Fiebre | Crash | Superviviente y por qué |
|---|---|---|---|
| Cartuchos (1977–83) | Clones de Pac-Man, licencias basura | Crash del 83 (-97%) | Nintendo: control de calidad de plataforma |
| Shooters espaciales (1978–80) | Todo era naves | Saturación arcade | Pac-Man: audiencia distinta |
| MMOs (2004–14) | "WoW-killers" con presupuestos AAA | WildStar, decenas más | Los que NO imitaron a WoW (EVE, OSRS, FFXIV tras reinventarse) |
| Hero shooters / live-service (2016–24) | Todo publisher quería su Fortnite/Overwatch | Concord, Anthem, ola de cierres 2025-26 | Los 4-5 incumbentes con network effects |
| Hyper-casual (2016–22) | Miles de clones por CPI barato | -24% descargas 2022 | Hybrid-casual: hook + profundidad |
| Empleo AAA (2020–26) | Sobrecontratación COVID + dinero barato | ~45,000 despidos 2022–2025; Embracer: ~8,000 y 40+ estudios cerrados | Equipos chicos de veteranos formando estudios nuevos |

**Qué significa para un dev chico en 2026:**
1. NUNCA entres a una fiebre en su fase de saturación: si el género ya tiene un dominante F2P con años de contenido, tu clon llega muerto (Concord es el memento mori). Cuando la prensa declara la fiebre, ya es tarde.
2. Los crashes son la ventana del chico: talento liberado, publishers retraídos de las apuestas grandes, audiencia hambrienta de lo que la fiebre NO daba. El premium single-player finito está menos saturado hoy que en una década.
3. La historia premia dos posiciones: el primero en un espacio nuevo (Minecraft, Dark Souls) o el más diferenciado en audiencia (Pac-Man, Wii, Stardew). Nunca al tercero-mejor-clon.
4. Koster (A Theory of Fun): la diversión es aprender patrones; un juego muere cuando se agota su patrón. Los ciclos de género son esto a escala de industria — la audiencia "masteriza" el género y se aburre. Los géneros saturados no necesitan más contenido: necesitan un patrón nuevo.

---

## 10. Micro-lecciones adicionales (todas con fuente)

| Dato verificado | Lección operativa |
|---|---|
| Doom fue rentable el DÍA 1 de su release shareware (dic 1993) | El costo de distribución cero + demo generosa cambia la economía del lanzamiento: no necesitas marketing masivo si el producto se comparte solo |
| id liberó el código fuente de Doom en 1997 (GPL en 1999) → source ports lo mantienen vivo y moderno | Abrir tecnología vieja extiende la vida del contenido décadas; el motor no es la joya, el juego sí |
| Blinky (Pac-Man) entra en modo "Cruise Elroy": más agresivo cuando quedan pocos dots | Micro-escalada dentro del nivel (no solo entre niveles) mantiene la tensión en el final de cada loop |
| Los cartuchos de E.T. enterrados en New Mexico fueron excavados y confirmados en 2014 | Los mitos de la industria a veces son ciertos — pero verifica: E.T. fue síntoma del crash, no su causa |
| Anthem, meses finales: programadores con "tunnel vision", incapaces de evaluar el juego holísticamente en sesiones de 40-80h | Reserva jugadores frescos (o tiempo tuyo con distancia) para evaluar la experiencia completa; el equipo quemado no puede juzgar su propio juego |
| WildStar arruinó también su transición a F2P: no dio pruebas visibles de haber arreglado sus problemas | Un relanzamiento/pivote solo funciona si el cambio es VISIBLE y verificable para el jugador que se fue (contrastar: No Man's Sky enseñaba cada update) |
| Hello Games con Foundation (nov 2016): el update entregó MÁS de lo anunciado | Post-crisis, invierte la política: under-promise, over-deliver. Es la única forma de recomprar confianza |
| Estudios del caso Wii: el rendimiento del hardware no mostró efecto significativo en la preferencia del consumidor de su audiencia | Los specs importan solo para la audiencia que compara specs; define primero QUIÉN compra |
| Koster, el "mastery problem": diseña el juego alrededor de una lección/patrón central que se aprende antes de que el sistema aburra | Declara cuál es el patrón central de TU juego; cuando el jugador lo domine, el juego terminó — planifica esa duración honestamente |
| Save the World (el Fortnite original) al pasar a free-to-play en 2026 rompió el récord de concurrencia del juego | El contenido viejo con audiencia nueva es un activo dormido; el precio es una palanca de relanzamiento |
| Ola de cierres 2026: Anthem (12-ene), The Sims Mobile (20-ene), Elder Scrolls: Blades (30-jun) | Todo juego online-only tiene fecha de muerte que tú no controlas; si eres chico, diseña para que el juego funcione offline o con servidores triviales de mantener |
| 1 de cada 10 devs perdió su empleo en el último año medido (2024-25); narrativa y arte los más golpeados | Para el dev chico: hay talento senior disponible para colaboraciones puntuales como nunca antes en la década |

---

## Reglas prácticas

- [ ] Tu core loop debe ser explicable en una frase y legible en 5 segundos de gameplay (estándar arcade).
- [ ] Un accidente/bug que hace el juego más divertido: formalízalo, no lo parchees (Space Invaders, SFII).
- [ ] Variedad de enemigos = un sistema + parámetros distintos, antes que N sistemas (fantasmas de Pac-Man).
- [ ] Primera pantalla = tutorial invisible: la geometría enseña, el texto estorba (SMB 1-1). Si el primer reto exige 2 habilidades, rediséñalo para que exija 1.
- [ ] Lista tus 3 restricciones más duras (equipo, presupuesto, skill) y pregunta qué identidad te regala cada una (bigote de Mario).
- [ ] En 3D: cámara y targeting son sistemas de diseño con presupuesto propio desde el día 1, no polish final (SM64 → Z-targeting).
- [ ] Si el jugador debe atender N cosas con 2 pulgares, automatiza N-2 (lock-on, auto-cámara, aim assist).
- [ ] Cutscene solo si el evento no puede ocurrir en el mundo con el jugador en control (Half-Life).
- [ ] Motor y contenido separados (data-driven) aunque seas un solo dev: te da modding, iteración rápida y longevidad (Doom .WAD).
- [ ] Antes de entrar a un género: nombra al líder actual, juega sus 10 primeras horas, y escribe por qué alguien lo abandonaría por tu juego. Sin respuesta escrita convincente, no entres (Anthem/Concord).
- [ ] PvP multijugador nuevo en 2026: free-to-play o no existes; y necesitas plan para el problema del frío (matchmaking sin masa crítica).
- [ ] Preproducción termina cuando puedes decir QUÉ es el juego en una frase y tienes un vertical slice divertido — no antes de escalar el equipo/scope (Anthem).
- [ ] Vende el juego que existe, no el que imaginas: comunica con builds jugables, no con promesas (No Man's Sky).
- [ ] Cobra temprano e itera en público si tu juego es de sistemas (Minecraft); los juegos narrativos, en cambio, se queman al mostrarse — elige el modelo según el género.
- [ ] Fricción y dificultad: tan duras como quieras, pero consistentes, legibles y con la culpa siempre del lado del jugador (Miyazaki: "desafiante, no injusto").
- [ ] Monetización SIEMPRE detrás de retención: si D7 es malo, monetizar más no arregla nada (F2P móvil).
- [ ] Detecta en qué fase del ciclo está tu género objetivo (nacimiento / fiebre / saturación / resaca) antes de comprometer un año de trabajo.
- [ ] La audiencia desatendida vale más que la mecánica novedosa: pregunta QUIÉN no está siendo servido por la fiebre actual (Pac-Man, Wii, Stardew).

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| "X pero mejor" contra un incumbente con network effects | Compites contra su versión de dentro de 2-3 años + los amigos y el progreso que el jugador ya tiene ahí. Cambia de audiencia o de tablero |
| Confiar en la "magia" de fin de proyecto (crunch que lo salva todo) | La historia documentada (Anthem) dice que la magia era supervivencia con suerte. Vertical slice divertido ANTES de producción a escala |
| Prometer en marketing lo que la build no tiene | ASA investigó a No Man's Sky; la confianza tarda años en volver. Enseña gameplay real capturado, siempre |
| Parchear todo exploit por reflejo | Evalúa primero: ¿rompe el juego o premia maestría? Los combos de SFII eran un bug |
| Tratar la cámara 3D como detalle de polish | Es de los problemas más difíciles del gamedev; Nintendo necesitó dos juegos y un viaje a un show de samuráis. Prototípala primero |
| Tutorial de texto/popups porque "no hay tiempo de diseñarlo en el nivel" | El tutorial de texto es deuda de diseño visible: reordena el primer nivel para que enseñe él (SMB 1-1) |
| Ignorar al líder del género "para no contaminarse" (el tabú-Destiny de Anthem) | Estudiar al incumbente es trabajo obligatorio de diseño competitivo |
| Entrar a la fiebre cuando ya es titular de prensa | A esa altura estás en la cohorte del crash, no en la de los pioneros |
| Medir tu juego contra specs (gráficos, tamaño de mundo, feature count) | Wii ganó su generación siendo la consola menos potente. La experiencia diferenciada vence al spec sheet |
| Juego live-service porque "es donde está el dinero" | En 2025-26 la mayoría de lanzamientos live-service perdió 80-99% de sus jugadores en meses. El dinero está donde tu equipo puede sostener la promesa: para un equipo chico, eso casi siempre es premium finito |
| Diseñar dificultad "hardcore" como identidad sin consistencia interna | Dark Souls funciona porque es justo y legible, no porque es duro. WildStar era duro sin más — y murió |
| Como solo dev, competir en volumen de contenido | Compite en profundidad, coherencia y años de iteración (Stardew: 4.5 años, un hombre, todas las disciplinas) |

## Fuentes

- **The Pac-Man Dossier** — Jamey Pittman, Game Developer (gamedeveloper.com) — desglose técnico completo de la IA de fantasmas y la dificultad por parámetros; leído directo.
- **Iwata Asks: Ocarina of Time 3D** — Nintendo (iwataasks.nintendo.com) — el problema del letrero de SM64 y el origen del Z-targeting contado por el equipo original.
- **Iwata Asks: New Super Mario Bros. Wii ("The Reason Mario Wears Overalls")** + entrevistas de Miyamoto (NPR, shmuplations) — el diseño de Mario como respuesta a límites de píxeles y el diseño de 1-1 simulando al jugador.
- **Video game crash of 1983** — Wikipedia + Video Game Console Library — cifras del crash ($3.2B→$100M), Goldman Sachs, E.T., origen del Seal of Quality.
- **Space Invaders accidentally invents difficulty curves** — Fawzi Mesmar (fawzi.zone) + Atari Archive — el speedup por límite de hardware que Nishikado conservó.
- **Monsters from the Id: The Making of Doom** — Game Developer — decisión deliberada de separar motor/.WAD y el modelo shareware.
- **How BioWare's Anthem Went Wrong** — Jason Schreier, Kotaku — el postmortem definitivo de preproducción fallida, "BioWare magic" y el tabú-Destiny.
- **Concord: análisis del cierre en 14 días** — cobertura 2024-2026 (fantasticnerdom, ofzenandcomputing, stratpack.blog, declaraciones de Sony) — pricing vs F2P, 697 concurrentes, falta de diferenciación.
- **No Man's Sky: redemption story** — Club386, KitGuru, Wikipedia — timeline verificable del lanzamiento, la investigación de la ASA y la remontada por updates gratis.
- **Former Sega Boss on the "Huge Strategic Blunder" of 32X and Saturn** — Time Extension + Wikipedia (Sega Saturn) — el lanzamiento sorpresa de E3 1995 y la pérdida de confianza de retailers/terceros.
- **Nintendo Wii — Blue Ocean Strategy case** — blueoceanstrategy.com + paper Universidad de Palermo — la apuesta por no-jugadores frente a la carrera de specs.
- **Entrevistas y perfiles de Hidetaka Miyazaki** — Wikipedia + ixbt.games (2025) — "desafiante, no injusto", muerte como aprendizaje, descubrimiento sin tutoriales.
- **Lessons learned from the development of Minecraft** — Habrador (blog) + Minecraft Wiki — alpha pagada 2009, precios escalonados, polls a la comunidad.
- **Candy Crush / Clash of Clans monetization analyses** — Stepico, Juego Studio, Mobile Free To Play — vender progreso, A/B testing, monetización tras engagement.
- **Mobile Gaming's Shift from Hyper to Hybrid-Casual** — Unity Blog + PocketGamer.biz + Deconstructor of Fun (2025) — cifras del ciclo hyper-casual y la transición hybrid.
- **2022–2026 video game industry layoffs** — Wikipedia + PC Gamer + Game Developer coverage — ~45,000 despidos, Embracer, formación de estudios nuevos.
- **La ola de cierres live-service 2025-2026** — Red Hare Studios, trackers de shutdowns (expcarry), Alinea Analytics, Deconstructor of Fun — retención 80-99% perdida, 52 cierres a mitad de 2026, resurgimiento single-player. Cifras de blogs/trackers de industria: tratarlas como orden de magnitud.
- **A Theory of Fun for Game Design** — Raph Koster — tesis central: diversión = aprendizaje de patrones; el juego muere cuando el patrón se agota.
- **Fortnite: Save the World free-to-play (2026)** — PC Gamer, Push Square — confirmación del pivote BR de 2017 y el destino del modo original.
- **WildStar postmortems** — Massively Overpowered, MMORPG.com — 9 años de desarrollo, posicionamiento hardcore, cierre 2018.
- **NES Limitations** — NESdev Wiki + Mega Cat Studios — 8 sprites/scanline, 3 colores/sprite: el contexto técnico real de la era.
- **Half-Life retrospectivas** — Wikipedia + Den of Geek — secuencias scripteadas sin cutscenes y su impacto en el FPS.
- **Grand Theft Auto III** — Wikipedia — streaming de mundo, cámara en tercera persona, cifras de ventas/reseñas, e influencia sobre el género sandbox 3D.
