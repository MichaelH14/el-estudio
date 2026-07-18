# Catálogo de mecánicas y sistemas

> **Cuando cargar este archivo:** al elegir o diseñar las mecánicas de un juego (verbos, economía interna, progresión, RNG, loot), al balancear sistemas existentes, o al diagnosticar por qué un juego se siente plano, roto o degenerado. Complementa [ver: fundamentos-diseno] y [ver: game-feel].

## 1. Verbos del jugador: moveset mínimo, profundidad máxima

Un **verbo** es una regla que le da al jugador la capacidad de cambiar el estado del juego (Anthropy & Clark, *A Game Design Vocabulary*). El moveset es el vocabulario del jugador; todo lo demás (niveles, enemigos, objetos) son frases construidas con él.

Principios verificados:

| Principio | Detalle | Fuente/ejemplo |
|---|---|---|
| Verbos robustos | Un verbo es "robusto" si tiene consecuencias e interactúa con muchos objetos del mundo, no si tiene muchas variantes | Anthropy & Clark |
| Recursos activan verbos | Un recurso vale porque enciende un verbo (munición → disparar). Si un recurso no habilita ningún verbo, es inventario muerto | Anthropy & Clark |
| Zonas seguras de prueba | Dar espacios sin peligro donde el jugador explora los límites de sus verbos antes de exigírselos bajo presión | Anthropy & Clark |
| Sobrecargar un verbo > añadir verbos | Downwell: límite autoimpuesto de 3 inputs (mobile); saltar y disparar comparten un botón (gun boots). Un verbo, múltiples funciones (moverse, atacar, frenar caída) | Fumoto, GDC 2016 |
| El verbo solo no basta | Fumoto explica que las gun boots por sí solas no hacían especial a Downwell: fueron las reglas y mecánicas construidas alrededor las que lo lograron. El moveset brilla por el contenido diseñado a su alrededor, no por el verbo aislado | Fumoto, GDC 2016 |
| Diferenciación ortogonal | Nuevas habilidades/unidades deben diferenciarse **cualitativamente** (hacen algo que nada más hace), no solo cuantitativamente (+10% daño). Cada pieza = la única forma de hacer cierta acción | Harvey Smith, GDC 2003 |

**Cómo elegir el moveset mínimo (proceso):**
1. Define el fantasy central en 1 frase ("saltar por un pozo con botas-pistola").
2. Lista los verbos candidatos. Elimina todo verbo que no interactúe con ≥3 sistemas/objetos del juego.
3. Intenta fusionar pares de verbos en uno (salto+disparo, correr+cargar ataque). Cada fusión crea decisiones (en Downwell disparar frena la caída: atacar = posicionarse).
4. Cada verbo nuevo debe pasar el test ortogonal: ¿habilita algo que ninguna combinación de los existentes logra?
5. Presupuesta: 1-3 verbos para arcade/mobile, 3-6 para plataformas/acción, más solo si el género lo exige (ver familia).

## 2. Catálogo de mecánicas core por familia

Taxonomía de referencia rápida. Los ejemplos son juegos reales canónicos de cada mecánica.

### Movimiento
| Mecánica | Decisión que genera | Ejemplo canónico |
|---|---|---|
| Salto (con control en el aire) | Timing + posicionamiento | Super Mario Bros. |
| Dash (i-frames o no) | Gasto de recurso posicional, cancelar compromiso | Celeste, Hyper Light Drifter |
| Momentum/física | Planificar trayectorias, riesgo-velocidad | Sonic, Tribes (ski) |
| Grapple/swing | Conversión de altura en velocidad | Spider-Man, Just Cause |
| Wall-jump/climb | Verticalidad, rutas alternativas | Celeste |
| Teleport/portal | Reencuadrar el espacio como puzzle | Portal |
| Gravedad variable | Reorientación espacial | VVVVVV, Outer Wilds |

### Combate
| Mecánica | Decisión que genera | Ejemplo |
|---|---|---|
| Melee con commitment (animación no cancelable) | Riesgo por golpe, lectura del rival | Dark Souls, Monster Hunter |
| Parry/counter en ventana estrecha | Riesgo alto/recompensa alta, ritmo | Sekiro, Punch-Out!! |
| Cobertura + probabilidad | Gestión de posiciones y odds | XCOM |
| Telegraph enemigo total | Puzzle determinista táctico | Into the Breach |
| Combos/cancels | Ejecución + optimización de daño | Street Fighter, Devil May Cry |
| Recurso de agresión (stamina, calor, munición) | Presión por economizar el ataque | Souls, furia/heat en fighting games |
| Deckbuilding de acciones | Sinergia acumulativa run a run | Slay the Spire |

### Colección
| Mecánica | Decisión | Ejemplo |
|---|---|---|
| Coleccionable de ruta (monedas, anillos) | Guía espacial + riesgo opcional | Mario, Sonic |
| Set completion (completar colecciones) | Metas de largo plazo | Pokémon, TCGs |
| Loot con rareza aleatoria | Lotería + optimización de build | Diablo |
| Coleccionable-llave (N estrellas abren puerta) | Elección de qué contenido jugar | Mario 64 |

### Construcción
| Mecánica | Decisión | Ejemplo |
|---|---|---|
| Colocación libre con física/adyacencia | Ingeniería, expresión | Minecraft, Factorio |
| Blueprint/receta (inputs → estructura) | Cadenas de producción | Factorio, Satisfactory |
| Base con layout funcional (defensa, logística) | Trade-off espacio/eficiencia | RimWorld, tower defense |

### Gestión
| Mecánica | Decisión | Ejemplo |
|---|---|---|
| Asignación de trabajadores/recursos escasos | Costo de oportunidad continuo | StarCraft (macro), Frostpunk |
| Colas de producción + tiempo real | Planificar bajo presión | RTS, builders |
| Necesidades en conflicto (dinero vs moral vs tiempo) | Dilemas sin óptimo único | RimWorld, This War of Mine |
| Draft/mercado compartido | Leer y negar al rival | 7 Wonders, autobattlers |

### Puzzle
| Mecánica | Decisión | Ejemplo |
|---|---|---|
| Regla única explorada exhaustivamente | Descubrimiento de implicaciones | Portal, Baba Is You |
| Manipulación de estado con undo | Experimentación sin castigo | Sokoban modernos, Into the Breach (reset) |
| Información oculta a deducir | Hipótesis y verificación | Return of the Obra Dinn, Minesweeper |
| Match/orden espacial | Reconocimiento de patrones bajo presión | Tetris, match-3 |

### Social / multijugador
| Mecánica | Decisión | Ejemplo |
|---|---|---|
| Información asimétrica/roles ocultos | Engaño y lectura social | Among Us, póker |
| Negociación/trueque entre jugadores | Política, alianzas temporales | Catan, EVE Online |
| Economía player-driven (mercado real) | Especulación, oficios | EVE, MMOs sandbox |
| Cooperación con dependencia (roles que se necesitan) | Coordinación y comunicación | MMO trinity, Overcooked |
| Ranking/ligas por temporada | Meta-objetivo competitivo renovable | Juegos competitivos live |

Regla transversal: elige UNA familia como core loop y usa las demás como soporte. Un juego de gestión con combate ligero funciona; dos core loops compitiendo por la atención del jugador, rara vez [ver: generos].

## 3. Economías internas: fuentes, sumideros, inflación, monedas

Modelo base (Machinations, Adams & Dormans, *Game Mechanics: Advanced Game Design*):

| Elemento | Qué hace | Ejemplo |
|---|---|---|
| **Source (faucet)** | Crea recursos de la nada | Matar mob → oro; salario por tiempo |
| **Sink (drain)** | Destruye recursos | Reparaciones, consumibles, impuestos, fees de NPC |
| **Converter** | Transforma X en Y (X se destruye) | Aserradero: 1 árbol → 50 tablas |
| **Trader** | Intercambia propiedad (nada se destruye) | Compra-venta entre jugadores |

**Inflación (lecciones de MMOs, AGC 2006 / Sam Lewis, vía Raph Koster):**
- Si los faucets superan los sinks de forma sostenida → hiperinflación: mantener cash pierde valor y los precios player-driven explotan.
- Ultima Online: borrar trillones de oro acumulado **no tuvo efecto** en los precios porque ese oro no circulaba. Lo que importa es la masa monetaria EN CIRCULACIÓN y su velocidad, no el total.
- Asheron's Call: bugs de duplicación colapsaron la moneda; los jugadores migraron a monedas-commodity (llaves, fragmentos). Si tu moneda falla, los jugadores inventan otra.
- EVE Online: economía estable porque casi todo es crafteado por jugadores Y todo puede ser destruido (naves explotan) → sink gigante permanente que obliga a re-comprar. El bucle producción→destrucción→producción es el sink más robusto que existe.
- Sinks que funcionan: consumibles obligatorios, impuesto transaccional en mercados (EQ2), fees de servicios NPC, precios dinámicos de NPC (exploitable, usar con cuidado).
- Para que el comercio sea divertido: mercados imperfectos > competencia perfecta — fragmentación por ubicación, información imperfecta, costos de transacción (Sam Lewis, AGC 2006).

**Múltiples monedas (F2P y no-F2P):**
- Patrón estándar: **soft currency** (abundante, ganada jugando, paga el loop core) + **hard/premium currency** (escasa o comprada, salta tiempo o compra cosmético) (Game Developer, "Types of game currencies in mobile F2P").
- La razón de separar monedas NO es solo monetización: cada moneda aísla un loop y evita que una fuente infle todos los precios. Una moneda por loop mayor (combate, crafteo, PvP, evento) mantiene cada balance independiente.
- Calibración: si una moneda es muy difícil de ganar, el grind expulsa; si es muy fácil, las recompensas pierden valor. Ambos extremos matan la motivación (Machinations.io, F2P economy design).
- En single-player aplica igual: Souls (almas = XP + moneda, con riesgo de pérdida = sink dramático) demuestra que una moneda con sink emocional genera tensión sin inflación.

## 4. Sistemas de progresión

**Capas típicas (de corto a largo plazo):** progresión intra-partida (power-ups, nivel de run) → XP/niveles de personaje → upgrades permanentes → unlocks de contenido → árboles de especialización → prestige/rebirth → colección/metas de completista.

Heurísticas con números (Pecorella, GDC Europe 2016 + serie "The Math of Idle Games"):

| Tema | Heurística |
|---|---|
| Costo vs producción | Costos de upgrades crecen exponencialmente; producción crece polinomialmente → cada generador/etapa tiene un "muro" natural que empuja a la siguiente capa |
| Cuándo ofrecer prestige | Regla práctica: el reset debe dar **+50% a +200%** de la prestige currency acumulada. Menos = no vale la pena; más = el jugador esperó demasiado |
| Fórmula de prestige | Usar raíces/exponentes fraccionarios sobre earnings para domar el crecimiento exponencial: Cookie Clicker = raíz cúbica de lifetime earnings (~8x earnings para duplicar prestige); AdVenture Capitalist ≈ raíz cuadrada (~4x); Egg Inc ≈ exponente 1/7 (~128x, fuerza runs activas) |
| Base del prestige | **Lifetime-based** (acumulado histórico): empuja a llegar más lejos cada run. **Reset-independent** (solo la run actual): permite "farmear" un punto óptimo repetidamente. Elegir según el comportamiento que quieras |
| Para qué sirve el prestige | (1) Sensación de escalera: volver a empezar más fuerte; (2) control técnico: comprime números exponenciales a rangos manejables |

**Unlocks y árboles:**
- Un unlock es una recompensa Y un mecanismo de enseñanza: dosifica la complejidad (el jugador aprende un sistema antes de recibir el siguiente) [ver: ux-ui-onboarding].
- Aplicar diferenciación ortogonal a los nodos del árbol: nodos que dan verbos nuevos > nodos de +X% stats. Los +X% son relleno aceptable entre nodos ortogonales, no el plato principal (Harvey Smith, GDC 2003).
- Cada carta/item/nodo nuevo debe "tener su lugar": si las métricas muestran que nadie lo elige o que siempre se elige, está mal costeado (Giovannetti, GDC 2019).

## 5. Aleatoriedad: input vs output, RNG justo, pity, loot tables

**Input vs output randomness (Keith Burgun, "Randomness and Game Design"):**
- **Input randomness**: lo aleatorio se revela ANTES de decidir (mapa generado, mano robada, spawns visibles). El jugador responde a la situación → skill.
- **Output randomness**: ruido inyectado ENTRE la decisión y el resultado (tirada de dado al atacar, % de acierto). Distorsiona el feedback: el jugador no puede saber si decidió bien o tuvo suerte.
- Regla de Burgun: en juegos de estrategia/aprendizaje, evitar output randomness; el input randomness da variedad sin robar autoría del resultado.
- Caso de estudio: Into the Breach elimina el % de acierto y muestra exactamente qué hará cada enemigo → todo es input randomness, cada derrota es culpa tuya. XCOM usa output randomness (75% y fallas) → tensión y drama, a costa de frustración. Ambos son diseños válidos; elige según la emoción objetivo.

**RNG "justo" (trucar los dados a favor de la percepción):**
- XCOM 2 (todas las dificultades salvo Legend) miente a favor del jugador: multiplicador oculto de ~1.2x al hit chance en Rookie, **streak breaker** de +10 aim acumulativo por cada fallo consecutivo en tiros >50%, bonus si te quedan <4 soldados, y penalización de puntería a los aliens tras hits consecutivos (documentado por la comunidad de mods; confirmado por un dev de Firaxis).
- Lección: los humanos perciben las rachas negativas como injustas aunque sean estadísticamente normales. Si usas output randomness en un juego orientado a la emoción (no al esport), amortigua las rachas. En competitivo puro, no toques los dados y hazlo saber.

**Pity timers (garantías sobre RNG):**
| Juego | Sistema | Números |
|---|---|---|
| Genshin Impact | Soft pity + hard pity | Base 0.6% de 5★; soft pity ~pull 74 (la probabilidad sube fuerte cada pull); hard pity garantizado en 90. Media real: ~62 pulls |
| Hearthstone | Pity fijo por rareza | Legendaria garantizada a más tardar en el pack 40; épica cada 10 packs; timers separados POR expansión |

- Patrón: prob. base baja + rampa creciente cerca del límite + garantía dura. La rampa hace que casi nadie llegue al hard pity, pero su existencia elimina el peor caso (y la peor prensa).

**Loot tables (Daniel Cook, Lostgarden):**
- Estructura: bucket de items con **pesos** (no porcentajes) + entradas **null** ("no cae nada"). Roll = aleatorio sobre la suma de pesos. Usar pesos hace trivial añadir items sin recalcular toda la tabla; con porcentajes, cada item nuevo rompe el balance.
- Variantes útiles:
  - **Peso -1 / always drop**: el item cae siempre (quest items).
  - **Sin reemplazo** (bag system): al caer un item se reduce su peso → garantiza variedad. Tetris reparte piezas así.
  - **Pity por decaimiento**: tras cada roll fallido, reducir el peso de las entradas no deseadas en X% donde X = 100 / N (N = máximo de rolls que toleras sin el drop).
  - **Tablas jerárquicas**: una tabla referencia sub-tablas (ej. sub-tabla de monedas con tope diario) → permite constraints por recurso.
  - **Drops condicionales y modificadores**: validar condición (daño mínimo, nivel) o escalar cantidad/peso por lógica externa (magic find, buffs).
- El mismo sistema modela cartas (mazo = tabla sin reemplazo) y dados (dado = tabla de pesos iguales), y sirve para procgen y selección de comportamiento de IA.

## 6. Sinergia entre mecánicas: qué funciona y anti-patrones

**Combinaciones probadas:**
| Combinación | Por qué funciona | Ejemplo |
|---|---|---|
| Verbo de movimiento = verbo de ataque | Cada acción resuelve 2 problemas → decisiones densas | Downwell (disparo frena caída), Doom 2016 (glory kill cura → correr HACIA el peligro) |
| Riesgo ↔ recompensa acoplados en el mismo acto | El jugador se auto-calibra la dificultad | Souls (almas se pierden al morir), Tribes/Sonic (velocidad vs control) |
| Piezas ortogonales que se multiplican | N elementos cualitativamente distintos → N² interacciones sin coste de producción extra | Slay the Spire (cartas × reliquias), inmersive sims (Smith: OUD) |
| Economía + colección + presión de tiempo | Cada recurso gastado es costo de oportunidad | Roguelikes con tiendas, drafts |
| Información oculta + comunicación limitada | La mecánica genera la dinámica social sola | Among Us, póker |
| Randomness de input + herramientas deterministas | Variedad infinita, ejecución justa | Into the Breach, Tetris (bag + control total) |

**Diseño de sinergias a escala (Slay the Spire, Giovannetti GDC 2019):**
- Instrumenta desde el prototipo: Mega Crit montó un servidor de métricas que registraba cada decisión del jugador desde etapas tempranas; con cientos de cartas e interacciones, el balance intuitivo no escala.
- Cada carta debe tener un lugar (algún arquetipo/build donde brilla); evitar efectos siempre-correctos que aplastan la diversidad de estrategias.
- En un roguelike single-player, un combo roto RARO es positivo (momento memorable, no daña a nadie); en multijugador el mismo combo es un bug de balance. El contexto decide la tolerancia.

**Anti-patrones:**
| Anti-patrón | Síntoma | Antídoto |
|---|---|---|
| Estrategia degenerada | Una forma de jugar garantiza éxito explotando las reglas y hace el juego menos divertido; no tiene counter accesible | Detectarla con métricas (win rate/pick rate), añadir counter o costo, no parchear con castigos arbitrarios |
| Estrategia dominante | Una opción es mejor sin importar lo que haga el rival → las demás opciones son ilusión | Costeo asimétrico, counters en triángulo, situacionalidad (cada opción brilla en algún contexto) |
| Mecánicas que compiten por el mismo slot | Dos sistemas resuelven el mismo problema → uno queda muerto | Test ortogonal: si B no habilita nada que A no haga, fusionar o cortar |
| Stacking multiplicativo sin tope | Sinergias % × % × % explotan el techo de balance | Sumar en vez de multiplicar, caps, diminishing returns |
| Moneda única para todos los loops | Una fuente descontrolada infla todos los precios del juego | Una moneda por loop mayor (sección 3) |
| Feature sin verbo | Sistema que el jugador observa pero no toca | Convertirlo en decisión o cortarlo |

## 7. Profundidad vs complejidad: emergencia con pocas reglas

Definiciones operativas (daniel.games; Game Design Advance):
- **Complejidad** = carga cognitiva: cantidad de reglas, excepciones, iconos, números que el jugador debe tragar.
- **Profundidad** = riqueza del espacio de decisión: cuántas situaciones estratégicamente distintas emergen.
- **Elegancia** = ratio profundidad/complejidad alto. La complejidad es un PRESUPUESTO: cada regla nueva debe pagarse con profundidad desproporcionada ("la complejidad adicional debe permitir gameplay exponencialmente mayor").

Principio central: **"La profundidad estratégica debe surgir de la interacción de muchas partes simples, no de la complejidad interna de pocas partes complejas."** Go es el caso extremo: un puñado de reglas, profundidad milenaria. El anti-caso es la "shallow complexity": reglas que cargan al jugador sin enriquecer nada.

Cómo se fabrica emergencia en la práctica:
1. Pocas reglas, aplicadas uniformemente a TODO (en Baba Is You o Minecraft las reglas no tienen excepciones por objeto; cada excepción mata interacciones).
2. Sistemas que comparten un medio común (fuego quema madera venga de donde venga; el agua moja a todos) → las mecánicas se comunican sin código extra.
3. Piezas ortogonales (sección 6): la profundidad crece con las COMBINACIONES, la complejidad crece con las PIEZAS. Añade piezas que multiplican, no que suman.
4. Test de corte: si quitas la regla y ninguna decisión interesante desaparece, la regla era complejidad pura. Córtala (daniel.games: el diseño mejora quitando).
5. La emergencia no se diseña directamente: se diseñan las reglas y se JUEGA para descubrirla. Presupuesta tiempo de playtest para encontrar lo que tus reglas ya contienen [ver: preproduccion].

## Reglas prácticas

- [ ] Define el fantasy en 1 frase antes de elegir verbos; cada verbo debe servir a esa frase.
- [ ] Máximo de verbos core: los que puedas enseñar en los primeros minutos; fusiona antes de añadir (Downwell: 3 inputs).
- [ ] Todo verbo nuevo pasa el test ortogonal: habilita algo que ninguna combinación existente logra.
- [ ] Todo recurso del juego debe encender al menos un verbo; si no, elimínalo.
- [ ] Da una zona segura donde probar cada verbo antes de exigirlo bajo presión.
- [ ] Mapea la economía como sources/sinks/converters/traders ANTES de implementar; busca el desbalance faucet>sink en papel.
- [ ] Todo faucet nace con su sink emparejado; si añades una fuente de oro, añade en el mismo cambio dónde se gasta.
- [ ] Sink más robusto: que las cosas se destruyan con el uso y haya que reponerlas (modelo EVE).
- [ ] Una moneda por loop mayor; nunca dejes que el loop de farmeo infle los precios del loop de crafteo.
- [ ] Progresión: costos exponenciales contra producción polinomial → muros naturales que empujan a la siguiente capa.
- [ ] Prestige: ofrece el reset cuando rinda +50%–200% de prestige currency; usa raíz cuadrada/cúbica sobre earnings.
- [ ] Nodos de árbol: mayoría ortogonales (verbos/reglas nuevas), los +X% solo como conectores.
- [ ] Decide por emoción: input randomness para juegos de maestría; output randomness solo si quieres drama, y entonces amortigua las rachas (streak breakers estilo XCOM).
- [ ] Toda recompensa aleatoria importante lleva pity (rampa + garantía dura); calcula el peor caso y decide si es publicable.
- [ ] Loot tables con pesos, nunca porcentajes; incluye entradas null y sub-tablas con topes.
- [ ] Instrumenta métricas de balance (pick rate, win rate por item/carta) desde el prototipo, no al final.
- [ ] Cada item/carta/nodo debe tener un lugar: 0% de uso = mal costeado; 100% = dominante.
- [ ] Reglas sin excepciones por objeto: cada excepción mata interacciones emergentes.
- [ ] Test de corte periódico: quita la regla; si ninguna decisión interesante muere, no vuelve.

## Errores comunes

| Error | Antídoto |
|---|---|
| Añadir verbos para "dar contenido" (moveset inflado que nadie domina) | Sobrecargar verbos existentes con contexto; contenido = nuevas situaciones para los mismos verbos (Fumoto) |
| Diferenciar unlocks solo con números (+5%, +10%…) | Diferenciación ortogonal: cada unlock relevante habilita una acción nueva (Smith) |
| Economía sin sinks ("los jugadores odiarán perder cosas") | La inflación destruye más diversión que cualquier sink; UO/Asheron's Call lo demuestran. Sinks desde el día 1 |
| Combatir inflación borrando oro acumulado inactivo | No funciona (UO): actúa sobre la moneda EN CIRCULACIÓN — impuestos a transacciones, consumibles, destrucción de items |
| Una sola moneda para todo el juego | Cada loop mayor con su moneda; los tipos de cambio entre ellas son tu panel de control |
| Prestige tacaño (reset rinde <50%) o eterno (el jugador espera semanas) | Banda +50%–200%; simular la curva en hoja de cálculo antes de implementar (worksheets de Pecorella) |
| % de acierto visibles y honestos en juego dramático single-player | Los jugadores perciben injusticia en rachas normales; amortigua (multiplicador oculto, streak breaker) o elimina el % (Into the Breach) |
| Gacha/loot raro sin garantía | Peor caso = jugador con 200 pulls sin premio publicándolo en Reddit; pity con rampa + hard cap |
| Porcentajes fijos en loot tables | Pesos: añadir un item no obliga a recalcular la tabla entera (Cook) |
| Balancear un juego de sinergias a ojo | No escala con N² interacciones; servidor de métricas desde el prototipo (Mega Crit) |
| Matar todo combo fuerte en un single-player | Combos rotos raros son momentos memorables en roguelikes SP; solo son bugs en multijugador (Giovannetti) |
| Ignorar una estrategia degenerada "porque es legal" | Si garantiza éxito y hace el juego menos divertido, es un bug de diseño: añade counter accesible o costo |
| Confundir complejidad con profundidad (más reglas = más juego) | Presupuesto de complejidad: cada regla se paga con profundidad desproporcionada; corta lo que no multiplica |
| Diseñar "emergencia" con sistemas cerrados llenos de excepciones | Reglas uniformes + medios compartidos (fuego, agua, física) que conecten los sistemas entre sí |

## Fuentes

- *A Game Design Vocabulary* — Anna Anthropy & Naomi Clark (libro, 2014) — marco de verbos/objetos, verbos robustos, recursos que activan verbos, zonas seguras.
- "Polishing the Boots: Designing 'Downwell' Around One Key Mechanic" — Ojiro Fumoto, GDC 2016 — moveset mínimo por restricción (3 inputs), fusión salto+disparo, el verbo brilla por su contexto.
- "Orthogonal Unit Differentiation" — Harvey Smith, GDC 2003 — diferenciación cualitativa vs cuantitativa; más gameplay sin más coste de producción.
- "Randomness and Game Design" — Keith Burgun, Game Developer — definición input/output randomness y su efecto en el feedback de aprendizaje.
- Notas del panel de economías MMO, Austin GC 2006 (Sam Lewis) — raphkoster.com — faucets/drains, hiperinflación, casos UO y Asheron's Call, sinks que funcionan, mercados imperfectos.
- "Loot Drop Tables" — Daniel Cook, Lostgarden (2014) — sistema completo de tablas con pesos, null drops, sin reemplazo, pity por decaimiento, tablas jerárquicas.
- "The Math of Idle Games, Part I–III" / "Quest for Progress" — Anthony Pecorella, Game Developer + GDC Europe 2016 — fórmulas de prestige (Cookie Clicker, AdVenture Capitalist, Egg Inc), regla +50–200%, crecimiento exponencial vs polinomial.
- "'Slay the Spire': Metrics Driven Design and Balance" — Anthony Giovannetti (Mega Crit), GDC 2019 — métricas desde el prototipo, cada carta con su lugar, tolerancia a combos rotos en SP.
- "The Depth:Complexity Ratio" — daniel.games — presupuesto de complejidad, elegancia, profundidad por interacción de partes simples.
- *Game Mechanics: Advanced Game Design* — Ernest Adams & Joris Dormans (+ Machinations, machinations.io) — taxonomía sources/sinks/converters/traders, simulación de economías.
- "Types of game currencies in mobile free-to-play" — Game Developer; + Machinations.io "Game economy design in F2P" — soft/hard currency, calibración del grind.
- Documentación comunitaria de XCOM 2 (XCOM Wiki / mods "Remove Aim Assists") — modificadores ocultos de puntería: 1.2x, streak breaker +10, ajustes por bajas; confirmado por un dev de Firaxis.
- Guías de sistemas pity (dotgg.gg, esports.gg, Hearthstone Wiki) — números de Genshin (0.6%, soft 74, hard 90, media ~62) y Hearthstone (legendaria/40 packs, épica/10, timer por expansión).
- "What is 'Degenerate'?" — Game Developer; + Skeleton Code Machine "What is a degenerate game state?" — definición de estrategia degenerada/dominante y su tratamiento.
