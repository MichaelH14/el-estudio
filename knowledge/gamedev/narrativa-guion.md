# Narrativa y guion

> **Cuando cargar este archivo:** al escribir historia, diálogo, lore, quests o cinemáticas de un juego; al elegir estructura narrativa o herramienta de branching (Ink/Yarn/Twine); al detectar que la historia y la mecánica se contradicen.

## 1. Estructuras narrativas: cuál usar y cuándo

Las tres estructuras base no compiten: operan a escalas distintas y sirven a juegos distintos.

| Estructura | Esqueleto | Sirve para | Ejemplo |
|---|---|---|---|
| **3 actos** | Setup → Confrontación → Resolución | Default universal. Campañas lineales, action-adventure, cualquier juego con historia "de principio a fin". Es el lenguaje común del equipo | La mayoría de AAA narrativos |
| **Viaje del héroe (monomito)** | Mundo ordinario → llamada → pruebas → ordalía → retorno transformado | RPGs y campañas largas donde el jugador ES el héroe y hay arco de personaje. El mapeo jugador=héroe es natural | Skolnick lo trata como plantilla base para game writers |
| **Kishōtenketsu** | Ki (introducción) → Shō (desarrollo) → Ten (giro) → Ketsu (conclusión) | Estructura SIN conflicto obligatorio. Puzzle games, juegos cozy, y sobre todo **micro-narrativa de nivel**: enseñar una mecánica | Niveles de Super Mario 3D World (Hayashida) |

**Los 3 actos mapeados a juego** (heurística de oficio sobre la base de Skolnick):

- Acto 1 (setup): hook + tutorial integrado. El incidente que arranca la trama debería coincidir con el momento en que el jugador domina los controles básicos.
- Acto 2 (confrontación): el grueso del gameplay. Aquí vive casi todo el contenido; el guion debe escalar stakes al ritmo que escalan las mecánicas, o la historia se queda atrás del juego.
- Acto 3 (resolución): clímax jugable + desenlace corto. Riesgo clásico: quitarle el control al jugador justo en el clímax (cinemática final larga) — el clímax debe JUGARSE.

**Monomito condensado** (etapas útiles para juegos; el detalle completo es la plantilla de Campbell/Vogler que Skolnick adapta):

1. Mundo ordinario → establece el "normal" que se va a romper (y sirve de tutorial).
2. Llamada a la aventura + rechazo → motivación del protagonista; en juegos el rechazo suele comprimirse o eliminarse (el jugador YA quiere jugar).
3. Mentor y cruce del umbral → entrega de herramientas/mecánicas iniciales; punto de no retorno.
4. Pruebas, aliados, enemigos → el acto 2: cada dungeon/misión es una prueba.
5. Ordalía central → midpoint: la derrota o revelación que recontextualiza todo.
6. Recompensa, camino de vuelta, resurrección → clímax final: el protagonista (y el jugador, con su skill acumulada) demuestra el cambio.
7. Retorno con el elixir → desenlace; en juegos, además, es donde se paga lo sembrado por las decisiones (§4).

**Claves operativas:**

- Evan Skolnick (*Video Game Storytelling*): el conflicto es el combustible de la historia; los 3 actos y el monomito importan menos como fórmula que como **lenguaje común** para que todo el equipo (no solo el writer) discuta narrativa.
- Jerarquía de exposición de Skolnick — memorízala: **1) deja que el jugador LO HAGA, 2) si no, MUÉSTRALO, 3) solo como último recurso, CUÉNTALO.** Los jugadores esperan estar jugando a los pocos segundos (máximo 1-2 minutos) de arrancar.
- Kishōtenketsu aplicado a diseño (Koichi Hayashida, Nintendo): cada nivel = 1) mecánica nueva en entorno seguro, 2) escenario algo más complejo, 3) **giro**: la mecánica usada de forma inesperada, 4) conclusión/examen que combina todo. Cada nivel es un showcase autocontenido de ~5 minutos. [ver: level-design]
- El "ten" (giro) es la herramienta anti-monotonía más barata que existe: no requiere enemigos nuevos ni assets, solo recontextualizar lo que ya hay.
- Regla de escala: 3 actos / monomito para el arco GLOBAL del juego; kishōtenketsu para el arco de CADA nivel o quest. Conviven sin problema.

## 2. Worldbuilding económico (sin lore-dumps)

Principio central: **el jugador solo retiene la información que es relevante para lo que puede hacer.** La exposición por la exposición se ignora o se salta.

| Técnica | Cómo | Ejemplo real |
|---|---|---|
| Lore opcional y fragmentado | El mundo se cuenta en descripciones de ítems, libros opcionales, diálogo opcional de NPCs — nunca en monólogos obligatorios | Dark Souls: cero exposition-dumps; el jugador arma el puzzle y eso genera satisfacción |
| Contexto en vez de explicación | Mostrar las consecuencias, no la historia: un ex-rico viviendo en la calle con moneda que nadie acepta cuenta el colapso económico sin una sola línea de lore | Principio "show don't tell" aplicado a mundos |
| Goteo ligado al loop | Repartir la historia en dosis pequeñas atadas al ciclo de juego, no en bloques al inicio | Hades: cada run entrega 1-2 conversaciones nuevas |
| Lore bible ≠ contenido del juego | La biblia de mundo es documento interno de consistencia. El jugador ve el 10%; el resto sostiene la coherencia desde atrás | Práctica estándar de estudios (narrative bible vs lore bible) |

**Heurísticas:**
- Si un NPC explica algo que el jugador podría descubrir jugando, corta la línea.
- Todo lore-dump obligatorio de >30 segundos es un bug de diseño: fragmentarlo, hacerlo opcional, o convertirlo en espacio jugable (ver §5).
- Debe ser **posible perderse cosas**: "It has to be possible to miss some things to make finding them meaningful" (Harvey Smith). Lore 100% garantizado = lore que no se siente descubierto.
- Escribe el mundo por sus reglas (qué se puede/no se puede hacer, quién manda, qué escasea), no por su cronología. Las reglas generan gameplay; las cronologías generan wikis.

## 3. Diálogo para juegos

### Principios de escritura

- **Brevedad radical.** El diálogo de juego compite con el gameplay por la atención. Línea que no cabe cómoda en un subtítulo de 2 renglones: reescribir. (Heurística de oficio, no de fuente única.)
- **Voz de personaje:** test de tapar el nombre — si al ocultar quién habla no distingues los personajes, no tienen voz. Dale a cada uno: vocabulario propio, ritmo propio (frases largas vs telegráficas), y una actitud default ante los problemas.
- Cada línea debe hacer ≥2 trabajos a la vez: avanzar trama + revelar personaje, o dar info + subir tensión. Línea que solo hace uno: candidata a corte.
- El silencio es una opción válida de diálogo: Firewatch la ofrece explícitamente y no responder ES caracterización.
- Diálogo interactivo con timer (Firewatch, Telltale) mantiene el ritmo y hace que elegir se sienta como conversar, no como leer un menú.

### Barks y su sistema (el estándar Valve)

Barks = líneas contextuales cortas, no interactivas, que disparan los sistemas. Taxonomía típica a presupuestar por personaje:

| Categoría | Ejemplos de trigger |
|---|---|
| Combate | ver enemigo, recargar, sin munición, granada, kill |
| Estado | salud baja, aliado caído, curado, buff/debuff |
| Navegación | llegar a zona, ver punto de interés, puerta bloqueada |
| Social/idle | saludo, comentario ambiental, chismes entre NPCs |
| Reactividad al jugador | jugador apunta a NPC, roba, vuelve tras mucho tiempo |
| Trama | callbacks a decisiones y eventos previos (la capa que hace el mundo "consciente", §4) |

Los barks NO se escriben como árbol: se escriben como **base de datos de reglas** (Elan Ruskin, GDC 2012, sistema de L4D/Portal/Dota 2):

1. **Concepto**: el evento que pide línea ("vi un enemigo", "recargo", "aliado herido").
2. **Criterios**: hechos del estado del mundo (`quién habla`, `dónde`, `salud<30%`, `ya-dijo-X`).
3. **Reglas**: concepto + set de criterios → respuesta. **Gana la regla más específica que matchee** (más criterios cumplidos); si ninguna específica aplica, cae a un fallback genérico.
4. **Memoria**: disparar una línea escribe hechos ("ya lo dije") → cooldowns y no-repetición. El Response System de Valve documenta flags de norepeat.

Consecuencias prácticas:
- La "ramificación" emerge de las condiciones, no de un árbol dibujado: estructura auto-ramificante que escala a miles de líneas.
- Escribe SIEMPRE el fallback genérico primero (cobertura al 100%), luego añade capas específicas (más criterios = más sabor). El juego nunca se queda mudo.
- Firewatch (equipo de Campo Santo, GDC 2017, "Do You Copy?") evolucionó de un sistema de barks con interrupciones a conversaciones largas por radio que pueden **reanudarse** tras interrupción — si tu juego es conversacional, diseña la interrupción y la reanudación desde el día 1, no como parche.
- Hades: triggers contextuales (p.ej. salud baja al llegar con un personaje selecciona un diálogo específico) + **cola con prioridades y pesos**: los eventos importantes de trama tienen prioridad sobre el flavor, y la aleatoriedad ponderada evita repetición entre runs.
- Presupuesta variantes: cada bark frecuente necesita 3-5+ variantes o el jugador lo notará en la primera hora. [ver: audio]

## 4. Narrativa ramificada

### Patrones estructurales (Sam Kabo Ashwell, "Standard Patterns in Choice-Based Games")

| Patrón | Qué es | Costo autoral | Rejugabilidad | Úsalo si |
|---|---|---|---|---|
| **Time cave** | Ramificación total, nada re-converge | Explota exponencialmente | Alta | Historias cortas de posibilidad abierta |
| **Gauntlet** | Hilo lineal con ramas que mueren/regresan rápido | Bajo | Baja | Una historia canónica en mundo hostil |
| **Branch & bottleneck** | Ramas que re-convergen en eventos comunes; el estado acumula diferencias | Alto (state tracking) | Media | Historias de crecimiento donde las decisiones se acumulan (Long Live the Queen) |
| **Quest** | Clusters de nodos por geografía, pocos finales | Alto | Media | Mundos consistentes y viajes (80 Days) |
| **Open map** | Geografía estática navegable, viaje reversible | Medio | Media | Exploración sin presión narrativa |
| **Sorting hat** | Rama temprana fuerte decide qué "juego" te toca | Muy alto (escribes N juegos) | Media | Rutas románticas / facciones (Katawa Shoujo) |
| **Floating modules** | Sin tronco: módulos que se activan por estado | Muy alto | Alta | Juegos quality-based (StoryNexus) |
| **Loop & grow** | Ciclo que se repite; el estado desbloquea opciones nuevas por vuelta | Alto | Media | Rutinas, time loops, roguelikes narrativos (Hades encaja aquí) |
| **Hub & spoke** | Ramas que salen de y vuelven a un nodo central | Medio | Media | Bases/campamentos entre misiones; también a nivel de conversación (rueda de diálogo que vuelve a la raíz, estilo Mass Effect) |

Nota sobre **storylets / quality-based narrative** (el modelo de floating modules): la unidad no es el nodo en un árbol sino la pieza de contenido autocontenida con requisitos de entrada (qualities/estado) y efectos de salida. Escala muy bien en contenido y muy mal en control de pacing; exige mucho contenido y tiende a incentivar grinding de stats (Ashwell sobre StoryNexus y afines).

### Branching real vs ilusión de elección

- **Branching real es carísimo**: cada rama divergente multiplica contenido que la mayoría no verá. Resérvalo para 2-4 decisiones estructurales.
- Presupuesto antes de escribir: dibuja el grafo completo de nodos y calcula cuánto contenido ve UNA partida vs cuánto escribes. En un time cave puro de profundidad 10 con 2 opciones, una partida ve 10 nodos de 1023: ratio 1%. Branch & bottleneck con estado puede bajar el desperdicio a casi cero. El patrón ES el presupuesto.
- **La ilusión bien hecha es legítima y barata** (Telltale, The Walking Dead): "Clementine will remember that" — las elecciones apenas cambian la trama; cambian **quién es el protagonista y sus relaciones**. El reconocimiento (un callback de una línea) da sensación de mundo reactivo a costo casi cero.
- La fórmula de costo: paga la consecuencia donde es barata (una línea de diálogo, una mirada, un ítem), no donde es cara (un nivel nuevo). Reserva el contenido caro para el final (finales múltiples concentran el branching real donde más se nota).
- Peligro: si prometes consecuencias y el jugador descubre que nada cambió NUNCA, la confianza se rompe (crítica estándar a Telltale). Mezcla: muchas consecuencias cosméticas + pocas reales y visibles.

### Consecuencias diferidas

- El patrón Witcher 3 (Bloody Baron, GDC 2017, Paweł Sasko): la decisión se toma en una quest y sus consecuencias aterrizan **quests o actos después** (Return to Crookback Bog; destinos del Barón, Anna y Tamara). La distancia temporal hace la consecuencia memorable e impide el save-scumming inmediato.
- inkle (Jon Ingold, "Narrative Sorcery", GDC 2017): en mundo abierto, consecuencias **persistentes** + **lógica defensiva** — el sistema escribe hechos y el contenido posterior los consulta; toda escena debe funcionar sin importar el orden de llegada, con fallbacks que garantizan que la historia se cuenta y tiene sentido igual.
- Implementación mínima: un store global de flags/hechos (`baron_vivo`, `mentiste_a_X`) + contenido posterior que chequea. Es exactamente el modelo de barks del §3 a escala de trama.

## 5. Narrativa ambiental: contar con el espacio

Base: Worch & Smith, "What Happened Here? Environmental Storytelling" (GDC 2010).

- Definición operativa: el espacio como dispositivo narrativo que el jugador **interpreta activamente** — infiere qué pasó en vez de que se lo cuenten. La inferencia crea inversión: lo que el jugador deduce lo cree más que lo que le dicen.
- Herramientas: props y su disposición (staging), texturas/desgaste, iluminación, composición de escena, telegraphing, y **sistemas del juego que reaccionan** (la reacción sistémica también narra).
- La escena fuerte plantea una pregunta ("¿qué pasó aquí?") con respuesta reconstruible: cadáver + puerta atrancada desde dentro + arañazos = historia completa sin una palabra.
- Debe poder perderse: contenido ambiental garantizado deja de ser descubrimiento (Harvey Smith).
- Dark Souls es el caso extremo: mundo + ítems cargan casi todo el peso del lore (§2); la arquitectura misma (verticalidad, atajos que reconectan) narra decadencia y conexión.
- Sinergia con level design: la narrativa ambiental es gratis en cuanto a sistemas — son decisiones de set dressing y layout que el equipo de arte/niveles toma igual. Dales intención. [ver: level-design] [ver: arte-direccion]

## 6. Ludonarrativa: armonía y disonancia

- **Disonancia ludonarrativa** (Clint Hocking, 2007, sobre BioShock): el **contrato lúdico** ("busca poder y progresarás" — las mecánicas premian el interés propio) contradice el **contrato narrativo** ("ayuda a Atlas" — la historia impone lo contrario sin opción). Las mecánicas enseñan valores; si la historia predica otros, el jugador lo siente aunque no sepa nombrarlo.
- Caso citado clásico: héroe afable de cinemática que masacra a cientos en gameplay (la crítica estándar a Uncharted, recogida en la discusión posterior al ensayo de Hocking).
- **Armonía = alinear la experiencia del jugador con la historia** (Greg Kasavin sobre Hades, paráfrasis de declaraciones en prensa — no cita textual): el roguelike ES la historia — Zagreus intenta escapar una y otra vez, muere, y **los personajes reconocen el ciclo** (el jefe recuerda quién ganó la última vez, la muerte alimenta conversaciones nuevas). La frustración mecánica del género se convierte en curiosidad narrativa: la muerte deja de ser un castigo y pasa a ser el motor que revela más historia.
- Auditoría práctica (hazla en preproducción y en cada milestone):
  1. Lista los 3-5 verbos core del juego. [ver: fundamentos-diseno]
  2. Lista lo que la historia dice del protagonista y del mundo.
  3. ¿El sistema de recompensas premia lo que la historia celebra? Si el juego paga por matar y la historia va de pacifismo, tienes un problema de diseño, no de guion.
  4. La fricción o la repetición mecánica ¿tiene lectura narrativa posible? (Hades la usó a favor.)
- Técnicas de armonía comprobadas:
  - **La mecánica como metáfora**: el ciclo de juego cuenta lo mismo que la trama (en Hades morir y volver ES la historia del hijo que no puede salir de casa).
  - **El mundo reconoce el sistema**: el diseño de Kasavin trata el roguelike como una narrativa con continuidad — cada jefe "recuerda" el resultado del encuentro anterior, y esa cuenta (quién ganó esta vez, quién la vez pasada) se vuelve parte de la ficción, no solo del state tracking (paráfrasis, no cita textual).
  - **Recompensas alineadas**: el sistema paga exactamente el comportamiento que la historia celebra (inverso exacto del problema de las Little Sisters que señala Hocking).
  - **Conocimiento del jugador = conocimiento del personaje**: lo que el jugador aprende entre runs (patrones, mapas, matchups) se refleja en cómo el personaje habla de ello (Kasavin: alinear lo que el jugador arrastra entre runs con lo que el personaje vive).
- La disonancia deliberada existe como recurso (juegos que critican sus propias mecánicas), pero debe ser una decisión, nunca un accidente.

## 7. Del concepto al guion: pipeline y documentos

Orden de trabajo (cada paso valida el anterior antes de invertir más):

| Paso | Entregable | Tamaño | Qué valida |
|---|---|---|---|
| 1. Premisa | Logline: 1-2 frases | 1-2 frases | ¿La idea sostiene un juego? La quest del Bloody Baron nació de un logline simple: Geralt conoce a un Barón que quiere que mate a un monstruo y ofrece información sobre Ciri a cambio (anécdota de origen de Sasko, paráfrasis) |
| 2. Sinopsis | Historia completa en prosa | ½-2 páginas | Arco global, protagonista, stakes, final |
| 3. Biblia narrativa | Personajes, mundo, reglas, tono | Documento vivo | Consistencia; separa lore bible (mundo/IP) de narrative bible (esta historia) |
| 4. Escaleta (beat sheet) | Lista ordenada de beats con intensidad | 1 línea por beat | Pacing: grafica la intensidad por beat y corrige valles/mesetas |
| 5. Diseño de quest/misión | Doc por misión: objetivo, beats, espacios, estados | Variable — se reporta que el diseño de Family Matters (Witcher 3) rondó ~40 páginas ANTES de escribir una línea de diálogo (cifra de cobertura de prensa sobre la charla de Sasko, NO VERIFICADA contra la fuente primaria) | Que la narrativa sea jugable: qué HACE el jugador en cada beat |
| 6. Script | Diálogo final. Cinemáticas en formato guion; diálogo sistémico/barks en spreadsheet (ID, personaje, contexto, línea, trigger) | — | Listo para grabación de VO e implementación |

- Documento paraguas útil (práctica de estudio, p.ej. Blind Squirrel): un **Narrative Design Doc** que lista ubicación, naturaleza y función de CADA elemento narrativo del juego — el mapa de dónde vive la historia.
- El spreadsheet de diálogo es formato de producción, no de lectura: cada línea con ID estable (para VO, localización e implementación) y columna de contexto para el actor. Columnas mínimas: `ID | personaje | línea | contexto/dirección de actor | trigger/condición | estado (draft/grabada/implementada)`. [ver: produccion-proceso]
- Formato de beat en la escaleta: una línea por beat = `quién + hace qué + qué cambia + intensidad (1-5)`. Si un beat no cambia nada, no es un beat.

### Storyboards y previs para cinemáticas

- Storyboard: escenas y shots numerados (Shot 1A, 1B…), **una acción clara por frame**, flechas para movimiento de cámara y sujeto, frame en el aspect final (16:9). Nuevo panel solo si cambia el ángulo de cámara o la acción altera la escena; si una flecha lo explica, no dibujes otro panel.
- Thumbnails rápidos > dibujos pulidos: el storyboard es herramienta de decisión, no arte final.
- **Previs** (blocking 3D low-poly con cámara) antes de animar: cortar un shot en previs cuesta minutos; cortarlo después de animado quema semanas. Regla: ningún shot entra a animación sin aprobarse en previs.
- Reserva storyboard/previs para cinemáticas y momentos clave scripted; el resto de la narrativa (barks, ambiental, sistémica) no se storyboardea, se especifica en el doc de misión.
- Antes de la cinemática pregunta la jerarquía de Skolnick (§1): ¿puede el jugador HACERLO en vez de verlo? La mejor cinemática es a menudo un momento jugable scripted.

## 8. Herramientas de branching: Ink, Yarn Spinner, Twine

| | **Ink** (inkle) | **Yarn Spinner** | **Twine** |
|---|---|---|---|
| Modelo | Lenguaje de scripting puro texto; sintaxis de "weave" (el flujo se teje en el propio texto) | Nodos de texto plano estilo guion de cine/teatro; lenguaje Yarn | Editor visual de nodos; exporta HTML jugable |
| Estado | Variables + **tracking automático de contenido visto** (sabe qué leíste; oculta por defecto opciones ya elegidas — hubs/loops casi gratis) | Variables, condiciones y comandos hacia el engine | Variables con macros; el manejo de estado es más manual |
| Integración | Runtime C# para Unity; ports comunitarios para otros engines y web (inkjs). Motor de los juegos de inkle (80 Days, Heaven's Vault); open source desde 2016 | Plugin-intérprete dentro del engine (origen Unity; usado en Night in the Woods, A Short Hike, DREDGE, Lost in Random, Escape Academy) | Pensado para standalone HTML; integrarlo a un engine requiere trabajo extra |
| Fuerte en | Prosa ramificada densa, mucha lógica, redraft rápido; escala a juegos completos | Diálogo de personajes dentro de un juego con gameplay propio | Prototipado ultra rápido, IF standalone, aprender estructura |
| Débil en | No trae conceptos de personaje/audio/UI: todo eso lo implementa tu código | El documento es lineal aunque la historia no: visualizar ramas cuesta | Escalar a proyectos grandes y pipeline de producción |

- Decisión rápida: ¿el texto ES el juego o casi? → Ink (o Twine si es un prototipo/jam). ¿El diálogo es una parte de un juego con mecánicas propias? → Yarn Spinner o Ink embebido. ¿Validar una estructura en una tarde? → Twine.
- Las tres son gratuitas/open source. Lo que compras con la elección es el **workflow del escritor**: Katharine Neil (comparación práctica) pesa la experiencia de autor por encima de la superioridad técnica — si tu writer no es técnico, eso decide, no las features.
- Sea cual sea: el contenido narrativo vive en archivos de datos (no hardcodeado), con IDs estables para localización y VO.

## Reglas prácticas

1. Jerarquía de exposición: que el jugador lo haga > mostrarlo > contarlo. "Contarlo" es último recurso (Skolnick).
2. El jugador debe estar jugando en <1-2 minutos desde el arranque; nada de prólogos de lore obligatorios.
3. Estructura global (3 actos / monomito) + kishōtenketsu por nivel/quest: introducir, desarrollar, girar, concluir.
4. Elige el patrón de branching (Ashwell) ANTES de escribir: el patrón determina el costo total del contenido.
5. Máximo 2-4 decisiones con branching real y caro; el resto, reconocimiento barato (callbacks de una línea estilo "X will remember that").
6. Toda decisión importante paga consecuencia diferida: flag ahora, aterrizaje 1+ quests después (patrón Bloody Baron).
7. Lógica defensiva en mundo abierto: toda escena funciona en cualquier orden de llegada, con fallback (Ingold).
8. Barks como base de datos de reglas: fallback genérico primero (cobertura 100%), capas específicas después; gana la regla más específica (Ruskin).
9. Cada bark frecuente: 3-5+ variantes escritas y cooldown/no-repeat activado.
10. Test de voz: tapa los nombres del guion; si no distingues quién habla, reescribe.
11. Línea de diálogo que no cabe en ~2 renglones de subtítulo: cortarla o partirla.
12. Cada línea hace ≥2 trabajos (trama+personaje, info+tensión) o se corta.
13. Lore obligatorio de >30 segundos: fragmentar, hacer opcional, o convertir en escena ambiental.
14. Narrativa ambiental: cada escena clave plantea "¿qué pasó aquí?" con respuesta reconstruible desde props/staging/luz; y debe poder perderse.
15. Auditoría ludonarrativa por milestone: ¿las recompensas premian lo que la historia celebra? Si no, cambia recompensas o cambia historia.
16. Pipeline en orden: logline → sinopsis → escaleta con curva de intensidad → doc de misión → script. No escribas diálogo antes de que la quest esté diseñada (Witcher 3: reportado ~40 páginas de diseño antes del primer diálogo, cifra no verificada en fuente primaria).
17. Ningún shot de cinemática entra a animación sin previs aprobado; matar shots en previs, no después.
18. Diálogo en datos con IDs estables (spreadsheet o Ink/Yarn), nunca hardcodeado — VO y localización lo exigen.
19. Antes de escribir una cinemática: ¿puede ser un momento jugable scripted? Si sí, hazlo jugable.
20. La muerte/repetición del loop, si existe (roguelike, souls-like), debe tener lectura narrativa — que el mundo la reconozca (Hades).

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Lore-dump de apertura: 3 minutos de historia antes de tocar un botón | Empezar in media res jugando; el lore se gotea después, opcional y ligado a lo que el jugador hace |
| Time cave accidental: ramificar todo "para dar libertad" y morir en la explosión combinatoria | Elegir patrón consciente (branch & bottleneck o gauntlet suelen bastar); re-converger pronto y acumular diferencias en estado, no en ramas |
| Prometer consecuencias que nunca llegan: el jugador descubre que nada cambia y deja de elegir en serio | Mezclar callbacks baratos frecuentes + 2-3 consecuencias reales visibles; nunca vender cosmético como estructural |
| Barks repetidos: el NPC dice la misma línea 4 veces en 10 minutos | Variantes múltiples + memoria de líneas dichas + cooldowns desde el primer día del sistema |
| Todos los personajes hablan igual (la voz del writer) | Ficha de voz por personaje (vocabulario, ritmo, actitud) + test de tapar nombres antes de grabar |
| Disonancia ludonarrativa accidental: la historia predica X, las recompensas pagan Y | Auditoría mecánicas-vs-historia en preproducción; las mecánicas enseñan valores lo quieras o no (Hocking) |
| Escribir diálogo antes de diseñar la quest | Diseño de misión primero (qué hace el jugador en cada beat); el diálogo es la última capa |
| Cinemática para todo | Jerarquía de Skolnick; cinemática solo cuando ni hacerlo ni mostrarlo jugando es viable |
| Narrativa ambiental decorativa: escenarios bonitos que no cuentan nada | Cada set dressing clave responde "¿qué pasó aquí?"; dar intención narrativa a decisiones de arte que se toman igual |
| Guion en el código: strings hardcodeados por todo el proyecto | Ink/Yarn/spreadsheet con IDs desde el prototipo; migrar después cuesta 10x |
| Ignorar la interrupción: el sistema de conversación se rompe cuando el gameplay interrumpe | Diseñar interrupción y reanudación como caso de primera clase (lección de Firewatch) |
| Confundir biblia con juego: intentar meter toda la lore bible en pantalla | La biblia es andamio interno; al jugador le llega ~10% por ítems, espacio y diálogo opcional |
| Quitarle el control al jugador en el clímax con una cinemática larga | El clímax se juega; la cinemática va antes (setup) o después (desenlace) |
| Elegir herramienta de branching por features en vez de por el escritor | El workflow del autor decide (Neil): writer no técnico → Twine/editor visual; writer-programador → Ink |

## Fuentes

- **Standard Patterns in Choice-Based Games** — Sam Kabo Ashwell (These Heterogenous Tasks, 2015) — taxonomía canon de estructuras de branching (time cave, gauntlet, branch & bottleneck, etc.) con costos y usos.
- **Rule Databases for Contextual Dialog and Game Logic** — Elan Ruskin, Valve (GDC 2012; + writeups de Radiator Blog y Emily Short; Response System en Valve Developer Wiki) — el sistema de barks por reglas/criterios usado en L4D, Portal y Dota 2.
- **Ludonarrative Dissonance in Bioshock** — Clint Hocking (Click Nothing, 2007) — ensayo que acuñó el término; contrato lúdico vs contrato narrativo.
- **What Happened Here? Environmental Storytelling** — Matthias Worch & Harvey Smith (GDC 2010) — técnicas de narrativa ambiental y el jugador como intérprete activo.
- **Video Game Storytelling: What Every Developer Needs to Know about Narrative Techniques** — Evan Skolnick (2014) — 3 actos, monomito, conflicto como combustible, jerarquía hacer>mostrar>contar.
- **Kishōtenketsu en el level design de Nintendo** — Koichi Hayashida (cobertura en Game Developer/Gamasutra y análisis derivados de Super Mario 3D World) — estructura de 4 pasos sin conflicto aplicada a niveles.
- **Do You Copy? Dialog System and Tools in Firewatch** — equipo de Campo Santo (GDC 2017; nombres exactos de ponentes NO VERIFICADOS en esta pasada) — evolución de barks a conversaciones largas reanudables; tooling data-driven.
- **Narrative Sorcery: Coherent Storytelling in an Open World** — Jon Ingold, inkle (GDC 2017) — consecuencias persistentes y lógica defensiva; contexto del lenguaje Ink (open source 2016).
- **Cobertura de Hades y Greg Kasavin** — "How Supergiant weaves narrative rewards into Hades' cycle of perpetual death" (Game Developer) + GDC Podcast (entrevista sobre Hades, episodio NO VERIFICADO) — muerte como progreso narrativo, triggers contextuales, prioridades y pesos. Las frases atribuidas a Kasavin en este archivo son paráfrasis traducidas, no citas textuales verificadas palabra por palabra.
- **The Walking Dead y la ilusión de elección** — análisis en GamesBeat/Bitmob y Game Developer ("The Walking Dead, Choices, and Kenny") — las elecciones definen relaciones y protagonista más que trama; el valor del reconocimiento barato.
- **Diseño de la quest del Bloody Baron** — Paweł Sasko, CD Projekt RED (GDC 2017; cobertura GamesRadar+, no leída íntegra — la cifra de ~40 páginas es del titular/snippet, NO VERIFICADA contra la charla original) — origen en un logline simple, consecuencias diferidas entre quests.
- **Authoring interactive narrative in Twine 2 vs Ink vs Yarn** — Katharine Neil (Medium) — comparación práctica de workflow de autor entre las tres herramientas.
- **Narrative Design Series: Planning & Ideation** — Blind Squirrel Entertainment — pipeline de entregables narrativos y Narrative Design Doc.
- **Dark Souls como worldbuilding inmersivo** — Heavyshelf y análisis afines — lore opcional en ítems y espacio, sin exposition dumps.
- **Prácticas de storyboard/previs para cinemáticas** — guías de producción (Game Developer "How to Build a Better Cutscene", MoCap Online, guías de storyboarding) — shots numerados, una acción por frame, matar shots en previs.
