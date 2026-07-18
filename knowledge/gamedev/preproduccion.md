# Preproducción: de la idea al plan

> **Cuando cargar este archivo:** al evaluar si una idea merece convertirse en juego, escribir un pitch/one-pager/GDD, decidir qué prototipar primero, definir hitos (first playable, vertical slice, MVP) o recortar el scope de un proyecto — especialmente para equipos de 1 persona o un agente trabajando solo.

## Mapa de la fase

La preproducción existe para **eliminar incertidumbre antes de gastar en producción**. Mark Cerny (método "Method", D.I.C.E. 2002, base del proceso de Naughty Dog/Insomniac/Sony): la preproducción debe ser **freeform y sin timeline rígido** — no se puede calendarizar el descubrimiento creativo — y termina cuando existe una **"publishable first playable"** que demuestra que el juego funciona. Si esa versión no emociona a quien la juega, el proyecto se cancela ahí, antes de quemar el presupuesto.

| Etapa | Artefacto | Pregunta que responde |
|---|---|---|
| Idea → concepto | Filtros + hooks | ¿Merece existir? ¿Se puede vender en una frase? |
| Concepto → papel | One-pager / pitch | ¿Se entiende? ¿Vale la pena hacerlo? |
| Papel → prototipo | Paper prototype / greybox digital | ¿El core loop es divertido? |
| Prototipo → plan | GDD ligero + macro design + hitos | ¿Qué se construye, en qué orden, con qué riesgos? |
| Fin de preproducción | First playable | ¿Kill o producción completa? |

Además del first playable, la preproducción de Cerny produce el **macro design**: el diseño a nivel macro del juego completo (estructura de niveles/mundos, progresión de mecánicas, qué aparece dónde) que sirve de plan de producción. El detalle fino (micro design) se decide durante producción, cerca de cuando se construye — nunca todo por adelantado. Para un solo dev esto se traduce en: al salir de preproducción debes tener (1) un prototipo que demuestra que el core divierte y (2) una lista macro de todo el contenido del juego con tamaños estimados. Nada más.

## De la idea al concepto: filtros

Una idea NO es un juego hasta que tiene un **core loop**: la secuencia de acciones que el jugador repite (percibir → decidir → actuar → feedback → recompensa → repetir) [ver: fundamentos-diseno]. Filtros antes de invertir un minuto de desarrollo:

**Filtro 1 — ¿Cuál es el loop?** Si no puedes describir qué HACE el jugador cada 30 segundos, tienes un tema o una ambientación, no un juego. Brian Upton (GDC 2017): las historias no venden juegos, el gameplay sí; el backstory se menciona en una frase y se avanza.

**Filtro 2 — ¿Divertido al minuto 1 y al minuto 10?** Dos tests distintos:
- **Minuto 1**: la acción básica se siente bien SIN contexto — el "toy". El Experimental Gameplay Project (EGP, Carnegie Mellon: decenas de juegos con Kyle Gabler, Kyle Gray y equipo, cada uno en <7 días — Gabler prototipó *Tower of Goo*, origen de *World of Goo*, en 4 días — regla "Build the Toy First"): empieza con la mecánica central sin objetivos; si el juguete no engancha, ningún meta-sistema lo salvará.
- **Minuto 10**: el loop repetido con variación y un objetivo integrado sigue interesando. EGP: "Build Toward a Well Defined Goal" — un objetivo integrado al gameplay (no un timer pegado encima) es lo que convierte el toy en game.

**Filtro 3 — ¿Tiene hooks?** Ryan Clark (Crypt of the NecroDancer): un hook es "un dato interesante sobre el juego que empuja a la gente a probarlo o comentarlo" ANTES de jugarlo. NecroDancer tenía varios: "roguelike rítmico" (sonaba imposible), nombre-juego-de-palabras, compositor conocido, esqueletos bailando en pixel art. Darkest Dungeon tenía hooks aún más fuertes (concepto "¿cómo se SENTIRÍA de verdad explorar un dungeon?", narrador excepcional) y Clark predijo correctamente que duplicaría los resultados. Su regla: **el 99% de las ideas fallan este filtro; esperar un mes más por una idea mejor es mucho más barato que ejecutar una débil**.

**Filtro 4 — ¿Hay mercado alcanzable?** Clark distingue jugadores "monógamos" (viven dentro de UN juego: LoL, DOTA2 — desplazarlos exige hooks extraordinarios) de "polígamos" (consumen muchos juegos de 5-20 h — mercado accesible para indies). Para híbridos de género, el mercado real es el **overlap** de las dos audiencias, no la suma. Estimación conservadora: no multiplicar jugadores × precio; mirar históricos de descuentos y bundles en SteamDB [ver: psicologia-retencion-negocio].

**Filtro 5 — La triple intersección de Derek Yu.** Elegir ideas que crucen las tres: (1) quiero HACER este juego (el proceso), (2) quiero HABERLO hecho (el resultado), (3) SÉ hacerlo (capacidad real). Faltando una, el proyecto muere a mitad de camino.

## Pitch y one-pager

Brian Upton ("Thirty Things I Hate About Your Game Pitch", GDC 2017, tras cientos de pitches en Sony Santa Monica): un pitch responde exactamente **dos preguntas — "¿vale la pena hacer este juego?" y "¿puede este equipo hacerlo?"** Todo lo que no aporte a una de las dos, fuera.

| Elemento del pitch | Contenido | Anti-patrón |
|---|---|---|
| Hook | Qué hace único al juego, en 1-2 frases | Lista de features estándar ("tiene inventario, crafteo...") |
| Gameplay | Qué hace el jugador, qué siente | Backstory largo; "es como X pero con historia profunda" |
| Comparables | Género + referencias reales de mercado | Comparar proyecciones con World of Warcraft |
| Prueba de concepto | Demo/prototipo de lo que es DIFERENTE y DIFÍCIL del juego | Prototipo de lo que ya se sabe que funciona |
| Arte | 1-2 assets excelentes, placeholders marcados como tales | Mucho arte mediocre; mezclar placeholder con final sin avisar |
| Números | Presupuesto, tiempo, personal, horas de gameplay | "Ya lo veremos"; no saber el costo de tu propio juego |
| Riesgo técnico | Ambición OK **con plan de mitigación** | Tecnología nueva "porque está de moda" (VR/AR sin motivo) |

**One-pager** (destilado del pitch, formato Librande): título + logline (1 frase), género y plataforma, core loop en 3-5 pasos, 2-3 hooks, referencia visual (1 imagen o fake screenshot), scope estimado, riesgo principal. Si no cabe en una página, el concepto no está claro todavía.

Plantilla (síntesis de Librande + Upton, rellenable en 30 minutos):

```
TÍTULO — logline de 1 frase (verbo + fantasía + giro)
Género / plataforma / referencia: "X meets Y" con juegos reales
CORE LOOP: 1. ... → 2. ... → 3. ... → (vuelve a 1 con más ...)
HOOKS (máx 3): qué haría que alguien lo comparta sin haberlo jugado
IMAGEN: fake screenshot o mockup del momento clave
SCOPE: nº niveles/horas estimadas + qué NO tiene el juego
RIESGO #1: la única cosa que no sé si funciona + cómo la pruebo
```

La línea "qué NO tiene el juego" es deliberada: declarar los recortes por adelantado (sin multiplayer, sin narrativa ramificada, sin generación procedural) evita renegociarlos con uno mismo cada semana.

## GDD moderno: ligero, vivo, orientado a decisiones

**El anti-patrón del GDD de 100 páginas:** especificar todo el juego antes de que nada sea jugable. Todo es una suposición, las suposiciones caducan al primer prototipo, y las decisiones importantes se ahogan en detalle. Stone Librande (GDC 2010, EA/Riot): "nadie lee más allá de la primera página de un GDD grande". Codecks añade dos fallas más: **falsa confianza** (algo puede leerse fantástico en papel y no ser divertido — solo el prototipo lo revela) y desactualización inmediata (el juego cambia a diario; el doc no).

**Solución Librande — one-page designs:** cada sistema del juego en UNA página como **diagrama anotado** (no prosa): el mapa de relaciones se ve de un vistazo. Lo usó en Diablo III, Spore y The Simpsons Game. Insight clave que rescata del GDD clásico: "escribir el documento ES diseñar el juego" — el valor está en el acto de sintetizar, no en el archivo resultante.

**Estructura recomendada de GDD moderno** (síntesis Codecks + Librande + práctica indie):

| Sección | Contenido | Tamaño |
|---|---|---|
| Visión | Qué debe SENTIR el jugador; 3-5 principios de diseño que resuelven disputas futuras | ½ página |
| Core loop | Diagrama del loop + loops secundarios | 1 página |
| Sistemas | Un one-pager (diagrama) por sistema, SOLO los ya decididos | 1 pág c/u |
| Contenido | Lista viva de niveles/enemigos/items con estado (idea/decidido/hecho/cortado) | tabla |
| Referencias | Fake screenshot + moodboard + comparables | 1 página |
| Riesgos y recortes | Qué se corta primero si hay que recortar (decidido EN FRÍO, por adelantado) | ½ página |

Reglas de mantenimiento: el GDD vive donde vive el trabajo (wiki/cards del gestor de proyecto, no un .docx aparte); **solo se detalla una sección cuando la decisión está tomada** — no documentar features que quizá se corten; cuando el diseño cambia, el doc cambia el mismo día; el GDD que dejó de cambiar es el que nadie lee. Codecks: "el juego ES tu GDD" — Curious Expedition se hizo con un doc extremadamente minimalista el primer año. Calibre: **1 página para solo dev o jam; 5-15 páginas enfocadas para equipo indie pequeño**. Los lectores reales del GDD: onboarding de gente nueva, publishers (contratos) y organismos de financiamiento — escribir para ellos, no para uno mismo.

## Visualizar antes de producir: mockups, wireframes, fake screenshots

Producir assets es caro; dibujar pantallas es barato. Antes de producir:

- **Fake screenshot** (técnica documentada por Charles Boury): un "master concept" que muestra un momento clave del juego COMO SE VERÁ EN PANTALLA, a través de la cámara real. Resuelve el problema de que moodboards y concepts sueltos dejan espacio a interpretación — con un fake screenshot todo el equipo (o el agente en sesiones futuras) ve el mismo juego final. Se usa como fuente de verdad durante producción: en cada hito se comparan screenshots reales contra el fake y se corrigen discrepancias [ver: arte-direccion].
- **Wireframes de UI**: cajas grises de cada pantalla y el flujo entre ellas ANTES de tocar arte. Detecta pantallas faltantes y flujos rotos cuando cambiarlos cuesta minutos. Lista mínima de pantallas que casi todo juego necesita y casi nadie wireframea a tiempo: título/menú, HUD in-game, pausa, settings (audio/controles), game over/derrota, victoria/resultados, confirmación de salir, loading. Un juego con progresión suma: selección de nivel, upgrades/tienda, save slots [ver: ux-ui-onboarding].
- **Storyboard/animatic**: para secuencias (intro, cinemáticas, momentos scripted), viñetas dibujadas con timing aproximado. Solo para juegos que las necesiten — no storyboardear lo que es sistémico.
- **Mockup de screenshot de tienda**: dibujar los 4-5 screenshots que irían en la página de Steam. Si no se pueden imaginar screenshots vendedores, el juego tiene un problema de hook, no de marketing (heurística derivada de Clark: el juego debe ser promocionable vía trailer/descripción como criterio de selección de diseño).

## Paper prototyping: cuándo y cómo

Tracy Fullerton (*Game Design Workshop*, enfoque "playcentric"): un juego no se evalúa por lo listo que se lee en papel sino por cómo se siente al jugarlo — testear temprano y con frecuencia, ANTES del polish, porque **el polish esconde malas decisiones**.

| Sirve para | NO sirve para |
|---|---|
| Sistemas por turnos, deckbuilders, economías | Reflejos, timing, twitch — exige tiempo real |
| Reglas de combate por turnos, balance inicial de números | Game feel (peso, aceleración, juice) [ver: game-feel] |
| Flujos de UI y estructura de pantallas | Cámara, controles análogos, física |
| Loops de decisión (¿qué elige el jugador y por qué?) | Todo lo que dependa de ejecución motora |

Cómo hacerlo rápido (proceso de una tarde, no de una semana):

1. **Aislar la decisión a probar**: una sola pregunta por prototipo ("¿elegir entre 3 cartas por turno es interesante?"), no "¿es divertido mi juego?".
2. **Materiales mínimos**: fichas, dados, post-its, cartas escritas a mano, una grilla dibujada. Cero producción — si estás maquetando cartas bonitas, estás puliendo, no prototipando.
3. **El diseñador es la computadora**: ejecuta las reglas a mano, resuelve casos no cubiertos improvisando y ANOTA cada improvisación — esas son reglas que faltaban.
4. **Cambiar reglas ENTRE partidas, no a mitad** (salvo que la partida esté rota); 3-5 partidas por variante bastan para ver si las decisiones son interesantes.
5. **Observar, no explicar**: en cuanto haya otro jugador disponible, callarse y mirar dónde duda, qué ignora y cuándo se aburre (playtesting playcentric de Fullerton).

Si el core del juego es acción en tiempo real, saltar el papel e ir directo al prototipo digital — el papel solo validaría la parte equivocada. Uso híbrido válido: papel para la capa de decisiones (economía, upgrades, mapa) aunque el momento-a-momento sea de acción.

## Prototipo digital: el core loop en gris

Objetivo: probar la hipótesis de diversión con el mínimo de código y CERO arte final. Jesse Schell (*The Art of Game Design*), **Rule of the Loop**: "cuantas más veces testeas y mejoras tu diseño, mejor será tu juego" — los buenos juegos no se diseñan, se descubren iterando. Todo lo que acorte el ciclo de iteración vale oro.

**Qué probar primero, en orden:**

1. **El verbo central en greybox**: mover, saltar, disparar, arrastrar — la acción que el jugador ejecuta más veces. Un cubo sobre planos grises basta.
2. **El feedback del verbo**: sonido placeholder + respuesta visual mínima. Sin esto no se puede evaluar si el verbo se siente bien (el juice mínimo del EGP).
3. **La primera decisión interesante**: el momento en que el jugador elige entre opciones con trade-off real.
4. **El loop completo una vez**: acción → recompensa → nueva situación. Un "nivel" de 60-90 segundos.
5. **El loop repetido con variación**: ¿la tercera repetición sigue interesando? Aquí se decide el test del minuto 10.

Timebox: el EGP demostró que un prototipo evaluable se hace en **menos de 7 días por una persona** — y que no hay correlación entre tiempo invertido y calidad del resultado ("Enforce Short Development Cycles"). Un prototipo que lleva un mes sin respuesta clara es un proyecto disfrazado. Presupuesto sano para un solo dev: 1-7 días por hipótesis, varias hipótesis en paralelo si hay más de una idea candidata ("Develop in Parallel" mitiga el apego a una sola idea).

Reglas del EGP ("How to Prototype a Game in Under 7 Days") aplicables a cualquier prototipo:

- **Build the Toy First**: primero la mecánica sin objetivos; goals después.
- **Fake It If You Can**: drop shadow en vez de iluminación real, bitmaps estirados en vez de splines, trucos en vez de sistemas "correctos". "Nobody Cares About Your Great Engineering" — nadie verá la ingeniería del prototipo; priorizar velocidad.
- **Cut Your Losses**: reconocer rápido la idea fallida y abandonarla sin drama.
- **Make It Juicy**: feedback constante y abundante (rebotes, sonidos, respuesta visual) — incluso en gris, el prototipo necesita suficiente juice para evaluar si la mecánica se siente bien [ver: game-feel].
- **Heavy Theming Will Not Salvage Bad Design**: si el gameplay es malo, el tema no lo salva; **But Overall Aesthetic Matters**: música/arte provisional que marque la dirección emocional sí ayuda (el EGP usaba concept art y música como "objetivos emocionales" antes de codear).
- **Complexity Is Not Necessary for Fun**: Tetris y Pac-Man; "Experimental" ≠ "Complex".
- Dato de contexto EGP: brainstorming formal tuvo 0% de éxito en sus 50+ juegos; las ideas buenas salieron de restricciones temáticas + simulación mental, no de sesiones de pizarra.

### Criterios de kill/continue

| Señal | Decisión |
|---|---|
| El toy es divertido sin objetivos; testers piden "una más" | CONTINUE — añadir goal y variación |
| "Se pondrá divertido cuando agregue X, Y, Z" | KILL o replantear — el core no sostiene |
| Divertido min 1, aburrido min 10 | Iterar variación/objetivo; si 2-3 iteraciones no lo arreglan, KILL |
| Solo el autor lo disfruta | Playtest externo antes de decidir; señal amarilla fuerte |
| First playable no emociona a jugadores frescos | KILL (regla de Cerny: cancelar antes de producción) |

Cultura de referencia: Supercell ha matado 30+ juegos ("kill early, succeed big"), muchos antes de anunciarlos. Su pipeline: equipo pequeño con autonomía → playtest interno con toda la empresa → soft launch en un mercado (Canadá) → global solo si retiene. La decisión de matar la toma **el propio equipo**, y se celebra con un brindis — se premia el coraje de intentar y el aprendizaje, no se castiga el fallo. Mataron Hay Day Pop al notar que decidían por métricas sin conexión genuina con el género: sin interés natural en el tipo de juego, las decisiones se vuelven mecánicas. Lección para un solo dev/agente: predefinir el criterio de kill ANTES de encariñarse, y matar en prototipo es victoria barata, no derrota [ver: historia-lecciones].

## First playable vs vertical slice vs MVP

Definiciones (glosario de askagamedev + uso de Cerny; los términos varían algo entre estudios):

| Artefacto | Qué es | Qué demuestra | Calidad de assets |
|---|---|---|---|
| **Prototipo** | Un solo sistema jugable | Que la mecánica central funciona/divierte | Greybox, placeholder total |
| **MVP** | El critical path mínimo del juego completo, de punta a punta | Que el juego ENTERO existe en bruto y es viable | Baja; lo mínimo que cumpla criterios de aceptación |
| **First playable** | Hito que cierra preproducción y abre producción | Que el juego emociona y se puede planificar la producción | Media; en el modelo Cerny debe ser "publishable" en calidad de experiencia |
| **Vertical slice** | Una porción del juego con TODOS los sistemas integrados a calidad final | Cómo se verá/sentirá el juego terminado (para publishers/funding) | Final en esa porción |
| **Demo** | Build recortada para mostrar (ferias, tienda) | Vende el juego a jugadores/ejecutivos | Final |

Orden típico: prototipo → MVP → first playable / vertical slice → demo. Nota: askagamedev trata first playable y vertical slice como casi sinónimos (el primero como hito de calendario, el segundo como artefacto); otros estudios usan "first playable" para algo más crudo que el slice. Al planificar, definir explícitamente qué significa cada hito EN ESTE proyecto y qué pregunta responde — el nombre importa menos que el criterio de salida.

Para un equipo de 1: el vertical slice clásico (porción a calidad final) es sobre todo una herramienta de pitch a publishers. Si no se busca funding, suele rendir más la ruta **prototipo → MVP → pulir en pasadas horizontales** (todo el juego sube de calidad junto), porque evita pulir a nivel final contenido que luego se corta. Derek Yu: no gastar demasiado en ninguna parte hasta que el juego entero sea jugable de principio a fin.

Plan de hitos tipo para un solo dev (síntesis de las fuentes, calibrar a cada proyecto):

| Hito | Criterio de salida | Decisión |
|---|---|---|
| Prototipo del verbo | El toy divierte en gris a un tester externo | kill/continue |
| Prototipo del loop | 3 repeticiones del loop sostienen interés | kill/continue |
| MVP / critical path | El juego entero se juega de inicio a fin, feo pero completo | congela el scope: de aquí en adelante solo se corta |
| Content complete | Todo el contenido del macro design está dentro | empieza el "último 10%" real |
| Polish + release | Menús, saves, balance, builds, página de tienda | ship |

## Scoping para equipo de 1

**La métrica de scope no es tu habilidad técnica: es el scope del último juego que TERMINASTE** (Derek Yu). Primer juego: pequeño y "sloppy", terminado y publicado rápido; el siguiente, un poco más grande y menos sloppy. Upton coincide desde el lado del pitch: empezar con algo tan pequeño que el prototipo quede cerca del juego terminado.

**La regla del juego más pequeño posible:** encontrar la versión mínima que TODAVÍA contiene el hook, y construir esa. Todo lo demás es contenido opcional que se añade solo si sobra tiempo. Método práctico de recorte brutal:

1. Escribir el hook en una frase.
2. Listar todas las features soñadas.
3. Tachar todo lo que no sea indispensable para que el hook funcione (la lista suele quedar en 3-5 features).
4. De lo tachado, mover lo mejor a una lista "v2 / secuela" — Derek Yu: guardar ideas para el siguiente juego duele menos que cortarlas a secas, y terminar no te quita la oportunidad de expresarlas después.
5. Estimar el resto y multiplicar: **"el último 10% es realmente el 90%"** (Derek Yu) — los detalles del final (menús, saves, bugs raros, balance, builds) consumen una fracción enorme del proyecto y no aparecen en la estimación ingenua.

**Presupuesto de riesgo:** un proyecto de 1 persona soporta UN riesgo grande, no cinco. Clasificar cada elemento como riesgo de diseño (¿es divertido?), técnico (¿puedo construirlo?), de arte (¿puedo producirlo a este nivel?) o de mercado (¿alguien lo querrá?). La preproducción ataca el riesgo más grande PRIMERO con el prototipo más barato posible (es exactamente para lo que Cerny define la fase); Upton acepta ambición técnica solo con plan de mitigación explícito. Si hay más de un riesgo grande, recortar hasta que quede uno.

**Trampas mentales que matan proyectos de 1 persona** (Derek Yu): confundir preparación (engine propio, tooling, research infinito) con empezar; reescribir código a mitad del proyecto por perfeccionismo; reiniciar el proyecto "ahora que sé cómo hacerlo bien"; añadir ideas nuevas sin cortar viejas. Antídotos: no crear tecnología propia innecesaria; prototipar primero; usar deadlines externas (jams, festivales); cuando te atores en una parte, avanzar en otra; cortar contenido sin piedad. **Si de verdad hay que abandonar: el siguiente proyecto se escala HACIA ABAJO, nunca hacia arriba.**

## Reglas prácticas

- [ ] Antes de nada: escribe el core loop en 3-5 pasos. Si no puedes, no tienes juego todavía.
- [ ] Test doble: ¿la acción básica engancha al minuto 1 (toy)? ¿el loop con objetivo sostiene al minuto 10?
- [ ] Cuenta los hooks: si no hay al menos 1 claramente comunicable en una frase, espera una idea mejor (el 99% falla — Clark).
- [ ] Verifica la triple intersección de Yu: quiero hacerlo + quiero haberlo hecho + sé hacerlo.
- [ ] One-pager antes que GDD: logline, loop, hooks, referencia visual, riesgo principal. Una página, ni una más.
- [ ] Pitch = 2 preguntas de Upton: ¿vale la pena hacerlo? ¿puede este equipo? Borra todo lo demás.
- [ ] Conoce tus números antes de pitchear: presupuesto, tiempo, horas de gameplay, plan de personal.
- [ ] GDD como one-pagers por sistema (diagramas, no prosa); solo documenta decisiones tomadas; actualízalo el mismo día que cambia el diseño.
- [ ] Haz un fake screenshot del momento clave del juego y úsalo como fuente de verdad visual en cada hito.
- [ ] Wireframea TODAS las pantallas y su flujo antes de producir arte de UI.
- [ ] ¿Core por turnos o de decisiones? → paper prototype (horas, no días). ¿Core de acción/tiempo real? → directo a greybox digital.
- [ ] Prototipa el toy primero (sin objetivos) y prioriza lo DIFERENTE y DIFÍCIL de tu juego, no lo que ya sabes que funciona (Upton); añade goal solo si el toy engancha.
- [ ] En prototipos: fake it (trucos > sistemas correctos), cero arte final, pero SÍ juice mínimo para evaluar feel.
- [ ] Define el criterio de kill ANTES de empezar el prototipo; escribe qué tendría que pasar para continuar.
- [ ] Playtest con gente fresca antes de decidir continue — "solo el autor lo disfruta" es señal amarilla.
- [ ] Scope = tu último juego terminado + un poco (sin juegos terminados: haz uno diminuto y sloppy primero); recorta hasta la versión mínima que aún contiene el hook, lo cortado va a la lista "v2".
- [ ] Un solo riesgo grande por proyecto; atácalo primero con el prototipo más barato.
- [ ] Presupuesta el final: el último 10% es el 90% — menús, saves, bugs, balance y builds no están en tu estimación ingenua.
- [ ] Escribe el criterio de salida de cada hito ANTES de empezarlo; al cerrarlo, congela el scope: solo se corta, no se añade.
- [ ] Al salir de preproducción ten exactamente dos cosas: prototipo que demuestra el core + macro design del contenido completo.

## Errores comunes

| Error | Antídoto |
|---|---|
| GDD de 100 páginas antes de prototipar | One-pager + prototipo; detalle solo tras decisión tomada; el doc que dejó de cambiar es el que nadie lee |
| Enamorarse del tema/lore y no del loop | Filtro: describe qué hace el jugador cada 30 s sin mencionar la historia; el backstory en 1 frase (Upton) |
| "Se pondrá divertido cuando agregue X" | El core debe divertir en gris y sin contexto; si necesita 3 sistemas más para ser divertido, kill |
| Pulir el prototipo (arte, engine, arquitectura) | Fake it; nadie ve la ingeniería del prototipo (EGP); polish esconde malas decisiones (Fullerton) |
| Theming pesado para salvar diseño flojo | "No puedes pulir una porquería" (EGP); arregla el loop o mata la idea |
| Prototipar lo fácil y conocido | Prototipa lo diferente y difícil — es lo único que reduce incertidumbre real |
| Paper prototype de un juego de reflejos | El papel no simula tiempo real; úsalo solo para decisiones/turnos/UI |
| Vertical slice a calidad final siendo solo dev sin publisher | Ruta MVP + pasadas horizontales; el slice es herramienta de pitch, no de desarrollo |
| Scope por ambición, no por historial | Métrica de Yu: tu último juego TERMINADO define el techo del siguiente |
| Reiniciar el proyecto "ahora que sé cómo hacerlo" | Trampa de perfeccionismo (Yu): termina esta versión; las lecciones van al próximo juego |
| Ideas nuevas entran, nada sale | Toda idea nueva a la lista "v2"; el scope solo se mueve hacia abajo |
| Matar tarde por costo hundido | Kill early, succeed big (Supercell); matar en prototipo es victoria barata; predefine el criterio |
| Decidir por métricas sin conexión con el género | Caso Hay Day Pop: sin interés genuino, las decisiones se vuelven mecánicas; elige géneros que te importen |
| Estimar sin contar el cierre | Último 10% = 90% (Yu); duplica la estimación y planifica menús/saves/builds desde el día 1 |

## Fuentes

- **One-Page Designs** — Stone Librande, GDC 2010 — el ataque canónico al GDD-biblia: diseño como diagramas anotados de una página; ejemplos de Diablo III, Spore y The Simpsons Game.
- **Method (proceso de desarrollo)** — Mark Cerny, D.I.C.E. Summit 2002 — define preproducción como fase freeform que termina en "publishable first playable" y legitima cancelar ahí; base del proceso de los estudios first-party de Sony.
- **How to Prototype a Game in Under 7 Days** — Kyle Gabler, Kyle Gray, Matt Kucic, Shalin Shodhan (Experimental Gameplay Project / Gamasutra, 2005) — las reglas de prototipado rápido (toy first, fake it, juicy, cut your losses) destiladas de 50+ juegos en un semestre; origen de Tower of Goo → World of Goo.
- **Finishing a Game** — Derek Yu (Make Games / derekyu.com) — la métrica de scope por juegos terminados, las trampas mentales, "el último 10% es el 90%", y qué hacer al abandonar.
- **Thirty Things I Hate About Your Game Pitch** — Brian Upton, GDC 2017 — las 2 preguntas del pitch, qué incluir/omitir, y la exigencia de conocer tus propios números.
- **What Makes an Indie Hit?: How to Choose the Right Design** — Ryan Clark (Game Developer/Gamasutra) — teoría de hooks con casos reales (NecroDancer, Darkest Dungeon), mercado monógamo vs polígamo, y el filtro del 99%.
- **Game Dev Glossary: Prototype, Vertical Slice, First Playable, MVP, Demo** — askagamedev (desarrollador AAA anónimo, Tumblr) — definiciones de trabajo y orden de los hitos tal como se usan en estudios.
- **Quality is worth killing for: Supercell's ruthless approach / What We've Learned from Failures** — Game Developer + Supercell.com — cultura kill-early con 30+ juegos cancelados, pipeline de playtest interno → soft launch, y el caso Hay Day Pop.
- **Writing Modern Game Design Documents** — Codecks (blog) — el GDD como sistema vivo en la herramienta de trabajo, "el juego es tu GDD", caso Curious Expedition.
- **Fake-screen it until you make it** — Charles Boury — la técnica del fake screenshot como master concept y fuente de verdad visual durante producción.
- **Game Design Workshop: A Playcentric Approach** — Tracy Fullerton — formalización del paper prototyping y el playtesting temprano y continuo; "testear antes del polish porque el polish esconde malas decisiones".
- **The Art of Game Design: A Book of Lenses** — Jesse Schell — la Rule of the Loop: más iteraciones de test-y-mejora = mejor juego; los juegos se descubren, no se diseñan de una.
- **How to Write a Game Design Document (GDD) That You Will Actually Use** — generalistprogrammer.com (2026) — calibres de tamaño de GDD moderno (1 página solo dev, 5-15 equipo indie) y reglas de mantenimiento.
- **Limitations of paper prototypes** — *Practical Game Design* (Packt) + UXPin blog — límites del papel para mecánicas en tiempo real/twitch y qué preguntas sí responde bien.
