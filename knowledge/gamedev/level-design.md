# Level design

> **Cuando cargar este archivo:** al diseñar o construir niveles/mapas/mundos — layout, tutorialización implícita, pacing, colocación de enemigos y secretos, blockout y playtesting de un nivel. Complementa [ver: fundamentos-diseno] (loops) y [ver: game-feel] (sensación momento a momento).

## Modelo mental

Un nivel no es un escenario: es un **argumento sobre las mecánicas** del juego. Cada nivel debe responder "¿qué idea de gameplay explora ESTE nivel que ningún otro explora?". Si no hay respuesta, el nivel sobra o debe fusionarse con otro.

Los 10 principios de Dan Taylor (GDC 2013, Square Enix Montreal) como checklist de alto nivel — un buen nivel:

| # | Principio | Aplicación concreta |
|---|-----------|---------------------|
| 1 | Es divertido de navegar | Flow intuitivo por layout, luz y lenguaje visual (Mirror's Edge guía hasta con detalles de ambiente) |
| 2 | No depende de palabras | Narrativa implícita por mise-en-scène (BioShock cuenta Rapture con carteles, grafiti y daño ambiental) |
| 3 | Dice QUÉ hacer, nunca CÓMO | Objetivo cristalino, método libre (contratos de la Dark Brotherhood en Skyrim) |
| 4 | Enseña constantemente | Cada nivel introduce o recontextualiza una mecánica (cada dungeon de Zelda = tutorial del ítem nuevo) |
| 5 | Sorprende | Cambios de ritmo, mecánica aplicada distinto (Dead Space 2: 15 min sin monstruos = tensión máxima) |
| 6 | Empodera al jugador | Momentos de dominio, no solo de castigo |
| 7 | Es fácil, medio y difícil a la vez | Capas de reto: camino base accesible, opcionales exigentes |
| 8 | Es eficiente | Reusar espacios/mecánicas con variación antes de fabricar contenido nuevo |
| 9 | Crea emoción | Diseñar la curva emocional, no solo la de dificultad |
| 10 | Está guiado por las mecánicas | El layout nace de lo que el avatar puede hacer (salto, dash, cobertura), no al revés |

## Enseñar jugando: kishotenketsu (el patrón Nintendo)

Estructura de 4 actos que Koichi Hayashida (director de Super Mario 3D Land/World) tomó de la narrativa japonesa de 4 paneles, vía Miyamoto. Es EL patrón para tutorializar sin texto:

| Acto | Nombre | Qué pasa | Ejemplo (nivel "Cakewalk Flip", SM3DW) |
|------|--------|----------|------------------------------------------|
| 1 | Ki — introducción | La mecánica se presenta en un contexto SEGURO: fallar no mata | Paneles que alternan rojo/azul al saltar, sobre suelo plano |
| 2 | Sho — desarrollo | Misma mecánica, escenario algo más complejo | Los paneles forman escalera para subir un risco (se añade verticalidad) |
| 3 | Ten — giro | Algo inesperado recontextualiza la mecánica; se quita la red de seguridad | Ondas de choque obligan a saltar (y por tanto a alternar paneles) bajo presión |
| 4 | Ketsu — conclusión | El jugador demuestra dominio; clímax + cierre | Ejecución final combinando todo, luego bandera |

Reglas de aplicación:
- **Una mecánica nueva por nivel** (o una combinación nueva). El nivel entero orbita esa idea.
- **Introducir siempre en zona segura**: primer encuentro con el peligro donde el fallo cuesta poco (pozo poco profundo, enemigo solo, checkpoint al lado).
- **El giro es lo que hace memorable el nivel**: no basta con escalar dificultad; hay que cambiar el ángulo (invertir la gravedad de la mecánica, combinarla con otra, usarla para navegar en vez de atacar...).
- **Demostración final = examen sin palabras**. Si el jugador pasa el acto 4, aprendió. No hace falta popup.
- Sirve igual en shooters, puzzles y horror: es una estructura de aprendizaje, no de plataformas. Más sobre onboarding explícito en [ver: ux-ui-onboarding].

## Pacing: curvas de intensidad

Principio (validado empíricamente por Valve en Left 4 Dead): **el combate constante fatiga, la calma constante aburre**. Se diseña una onda: picos de intensidad separados por valles de descanso.

Algoritmo del AI Director de L4D (Mike Booth, Valve — útil como receta manual aunque tu juego no tenga director dinámico):
1. **Build up**: presión creciente hasta que la intensidad estimada del jugador cruza el umbral de pico.
2. **Sustain peak**: mantener presión solo 3-5 segundos tras el pico (no más).
3. **Peak fade**: retirar amenazas nuevas; dejar que el combate en curso se resuelva solo.
4. **Relax**: 30-45 segundos de mínima amenaza, o hasta que el jugador avance suficiente hacia el siguiente objetivo. Volver a 1.

Clave de Booth: el director ajusta **frecuencia, no amplitud** — el pacing no es dificultad. Un valle no es "enemigos débiles", es ausencia de presión: loot, vista panorámica, narrativa ambiental, respiro.

Herramientas de pacing estático (sin director):
- **Beat chart / gráfico de intensidad**: lista cada sala/encuentro del nivel con intensidad estimada 1-10; dibujar la curva. Debe subir en dientes de sierra hacia un clímax, nunca ser plana ni monótonamente creciente. Mike Stout aplica exactamente esto analizando los dungeons de Zelda: cada sala rampea combinando tipos de enemigo y geometría, **sin repetir jamás un encuentro idéntico**.
- **Valle post-clímax**: tras un boss o set-piece, siempre espacio seguro (tienda, cinemática, zona de loot).
- **Loops anidados de Halo** (Jaime Griesemer): un loop de 3 segundos (apuntar-disparar-moverse) dentro de uno de 30 segundos (un encuentro: abrir con granada, limpiar, reposicionarse) dentro de uno de 3 minutos (la batalla: oleadas, refuerzos, retirada). La cita real de "30 seconds of fun" tiene segunda mitad que todos olvidan: esos 30 segundos se repiten **en contextos siempre distintos** — otro entorno, otras armas, otros vehículos, otras combinaciones de enemigos. Repetir el loop sin variar el contexto NO es el patrón Halo.
- Secuenciación de retos: introducir enemigo/reto nuevo aislado → combinarlo con conocidos → usarlo en el clímax. Igual que kishotenketsu pero a escala de campaña.

## Composición espacial

### Vocabulario (Kevin Lynch, vía Totten — "An Architectural Approach to Level Design")
Los jugadores construyen mapas mentales con 5 elementos: **paths** (rutas), **edges** (límites), **districts** (zonas con identidad visual propia), **nodes** (intersecciones/plazas donde se decide), **landmarks** (referencias visibles). Un nivel legible tiene los 5; un nivel confuso suele tener districts indistinguibles y cero landmarks.

### Weenies y landmarks
- **Weenie** (término de Walt Disney): landmark grande, visible a distancia con sightlines largas, que TIRA del jugador hacia él (el castillo de Disneyland; la Citadel de Half-Life 2; las torres de BotW). Promete payoff por el viaje.
- Regla de Romero (Doom): cada mapa necesita **landmarks reconocibles** para orientarse; sin ellos el jugador no puede razonar "ya pasé por aquí".
- Half-Life 2 encuadra la Citadel con marcos de puerta y pájaros volando hacia ella: la composición dirige la mirada. Principios: el jugador mira hacia donde se mueve, no mira arriba sin estímulo, y su atención va al **contraste** (color, luz, forma, movimiento).

### La regla del triángulo (Nintendo, BotW — CEDEC 2017)
El triángulo/pirámide es la unidad base del mundo abierto: o subes al pico o lo rodeas — ambas opciones son interesantes, y ambas ocultan lo que hay detrás (sorpresa al revelar). Tres escalas con funciones distintas:

| Escala | Función |
|--------|---------|
| Grande (montañas) | Landmark/weenie: orientación y meta a largo plazo |
| Mediana (colinas) | Obstruir la vista: ocultar sorpresas, forzar decisión de ruta |
| Pequeña (montículos) | Tempo: micro-variación del movimiento |

- **"Gravedad"**: la topografía empuja al jugador hacia los puntos de interés como una canica hacia el valle — se guía sin flechas.
- **Nunca sightline completa de A a B**: si el jugador ve el landmark entero desde el inicio, el viaje no revela nada. Curvar caminos, revelar por capas.

### Contraste (reglas de Romero para Doom, generalizables)
- Cambiar altura de suelo al cambiar textura de suelo (da forma y legibilidad).
- Alternar claro/oscuro y estrecho/abierto — el contraste espacial ES el ritmo visual del nivel.
- **Prospect-refuge** (Totten): los humanos disfrutan ver espacio abierto (prospect) desde un lugar protegido (refuge). Alternar refugios con vistas = tensión/alivio espacial. Un balcón antes de la arena grande deja "leer" el reto antes de saltar.

### Gating y loops de atajo
- **Lock & key** (Zelda): el camino crítico es casi lineal, pero las llaves están en ramas opcionales → sensación de exploración sin perderse. En el dungeon 4 de Zelda 1 los diseñadores bloquean la sala 6 hasta obtener la escalera de la sala 8: el gate garantiza que el jugador tiene la herramienta antes del reto que la exige. Gating por habilidad del avatar (metroidvania) > gating por llave literal: la "llave" es una mecánica que además abre juego nuevo en TODO el mapa.
- **Loops de atajo** (Dark Souls): el nivel avanza alejándose del hub y de pronto una puerta/ascensor conecta de vuelta al inicio — geometría real, no teleport. Efecto triple: recompensa ("¡esto conecta AQUÍ!"), reduce el costo de la muerte (checkpoint efectivo), y enseña el espacio (el mapa mental se cierra). Regla: diseñar el loop ANTES que las salas; el atajo se abre solo desde el lado lejano (puerta con barra, ascensor que baja).
- Ramas de Zelda 1 (Stout): bifurcaciones concentradas al inicio (2-3 decisiones), salas opcionales colgando del camino crítico, atajos escondidos tras paredes destructibles — el jugador "se siente listo" al encontrarlos sin romper la claridad direccional.

### Wayfinding: escala de certeza (The Level Design Book)
Elegir la herramienta según cuánta certeza de ruta necesitas:

| Certeza | Herramientas |
|---------|--------------|
| Sutil (~1-20%) | Detalle arquitectónico, NPC que camina, anomalía visual, audio direccional |
| Media (~35-60%) | Sightlines/composición, luz y color como guía, señalética in-world, narrativa ambiental |
| Alta (~70-93%) | Secuencia guionada, rastro de recursos (breadcrumbing: la línea de plátanos de Donkey Kong Country), amenaza activa que empuja |
| Total (~95-98%) | Barreras sólidas, UI persistente (marcador de objetivo) |

Usar la MÍNIMA certeza que funcione: cada escalón hacia arriba resta autonomía. Para zonas "salvajes" deliberadas, anti-wayfinding: quitar señales para que orientarse SEA la mecánica.

## Encounter design

Principios destilados de Halo, DOOM 2016 y Zelda:

- **La arena es parte del enemigo.** El mismo grupo de enemigos en pasillo vs. arena abierta con flancos es un encuentro distinto. Diseñar geometría y composición enemiga juntas. Nunca repetir la misma combinación geometría+enemigos dos veces (Stout sobre Zelda).
- **Arquetipos de IA legibles** (DOOM 2016): cada tipo de enemigo fuerza un verbo distinto del jugador (el que carga te mueve, el francotirador te hace cerrar distancia, el escudo te hace flanquear). Un encuentro se diseña como mezcla de verbos, no como suma de HP.
- **Push-forward combat** (id Software, GDC 2018 — Kurt Loudy & Jake Campbell): si el jugador se esconde tras un muro a esperar recuperarse, el encuentro falló. En DOOM los recursos (vida/munición vía glory kills) salen de AGREDIR: la arena premia moverse hacia el peligro. Aunque tu juego use coberturas, la regla generaliza: **el encuentro debe incentivar el comportamiento que tu juego quiere ver** — si quieres agresión, recompensa agresión con recursos; si quieres tactical, castiga el descubierto.
- **Arenas**: entradas/salidas claras, ≥2 rutas entre zonas (flanqueo posible para ambos bandos), cobertura orientada (protege del frente A, expone al flanco B — cobertura omnidireccional mata el movimiento), verticalidad con riesgo/recompensa (altura = vista pero exposición), y "juguetes" de arena (barriles, torretas, vehículos) que crean el giro del encuentro.
- **Apertura del encuentro**: dejar leer la arena antes del combate (prospect-refuge: entrada elevada o ventana previa). El jugador que planea su apertura (la granada inicial de Halo) siente autoría; el que es emboscado sin lectura previa siente injusticia — reservar la emboscada como giro puntual, no como dieta.
- **Colocación**: primer contacto a distancia media visible (no spawn a la espalda); refuerzos anunciados (sonido/animación de entrada); el último enemigo de la oleada no debe ser un escondido pasivo que alarga el limpiado (anticlimax).
- **Escala de 3 min** (Halo): pensar la batalla completa — oleadas, momento de retirada del enemigo, refuerzos — no solo el tiroteo. La IA decide en la ventana de 30 s; el diseñador guioniza la de 3 min.

## Secretos y recompensa por exploración

- Romero incluía áreas secretas como regla fija de cada mapa de Doom. Un secreto bien hecho: **insinuado, no invisible** — textura desalineada, luz distinta, hueco visible en el minimapa, sonido. El jugador debe poder deducirlo; el secreto por barrido de paredes al azar es relleno.
- Jerarquía de secretos: (1) caramelo cercano — nicho con recursos a 5 s del camino, mantiene el hábito de mirar; (2) secreto de habilidad — requiere ejecutar bien una mecánica (salto difícil); (3) secreto de conocimiento — requiere información de otra zona o volver con una herramienta nueva (re-usa el nivel, patrón metroidvania); (4) secreto profundo — nivel/jefe secreto, para la comunidad más que para un jugador.
- **La recompensa debe ser proporcional a la fricción**: desvío de 10 s → recursos; puzzle opcional → mejora permanente o pieza de lore relevante. Recompensar exploración con basura entrena a NO explorar.
- Ramas opcionales de Zelda: cuelgan del camino crítico y devuelven a él rápido — explorar nunca cuesta minutos de retraversía. La "falsa libertad" (ramas cortas + camino crítico lineal) da sensación de exploración sin jugadores perdidos.
- En mundo abierto, el patrón BotW: el terreno oculta el secreto (triángulo mediano) y la curiosidad lo revela — la sorpresa detrás de la colina es la recompensa del desvío. Presupuestar densidad: algo que encontrar en cada "celda" de vista, aunque sea pequeño.
- Los niveles secretos completos (Doom) pagan doble: replayability para el jugador y capital social para la comunidad (guías, boca a boca). Vale la pena aunque solo un % pequeño los encuentre — el resto se entera de que existen, y eso también vende la profundidad del juego.
- Contador de secretos al final del nivel (patrón Doom: "Secrets: 2/5"): convierte el secreto no hallado en razón de rejugar. Usarlo solo si rejugar niveles es parte del diseño.
- La estructura de Zelda 1 crea una "falsa sensación de libertad de exploración" (Stout): el jugador CREE que explora libremente, pero las llaves en las ramas hacen la exploración obligatoria de facto. Es un truco legítimo — la sensación de libertad importa más que la libertad real, siempre que el jugador no detecte el truco.

## Greyboxing / blockout

Regla económica central: **es barato tirar geometría gris; es carísimo tirar arte terminado**. Todo layout se valida jugándose en gris antes de recibir arte. Valve lo institucionalizó con "orange maps" (textura naranja en paredes, gris en suelos) en Half-Life 2.

Métricas de partida (The Level Design Book — ajustar a tu juego midiendo al avatar real):
| Métrica | Valor inicial |
|---------|---------------|
| Grid | 1-2 m en Unity (jugador ~1 m ancho); 50-100 uu en Unreal (jugador ~60 uu); 32-64 u en Doom/Quake |
| Altura de paredes | 150-200% de la altura del jugador |
| Ancho de paso/pasillo | mínimo 2× el ancho del jugador |
| Spawn→objetivo (MP) | 8-12 s de recorrido (referencia de Dirty Bomb) |

Workflow: sketch del layout (cualquier garabato desbloquea) → suelo + figura de escala + paredes → **jugarlo en engine con colisión y gravedad reales, jamás solo volar en editor** → iterar. Herramientas: ProBuilder (Unity), CubeGrid/Modeling Tools (Unreal), TrenchBroom (formato .map).

- Error #1 del blockout: **escala incorrecta**. Antídoto: figuras de escala por todas partes y jugar cada iteración. Muy chico → expandir muros exteriores; muy grande → comprimir/eliminar salas.
- El blockout ya debe responder: ¿se encuentra el camino crítico sin perderse? ¿el massing comunica qué lugar es? ¿el pacing de la curva funciona? Si la respuesta exige el arte final, la pregunta era de arte, no de layout.
- Proceso Valve (GDC 2006): construir ~15 minutos de gameplay en bruto → playtest → priorizar el trabajo de la siguiente semana con lo observado → repetir en incrementos de 1-2 semanas. Los cabals de HL2: equipos de 4-5 (mitad level designers, mitad programadores); más grandes diluían las sesiones de diseño.
- Excepción honesta: juegos donde el arte ES el gameplay (narrativos tipo Firewatch) sacan menos provecho del gris puro.
- **2D/top-down (plataformas, twin-stick, etc.)**: las cifras de la tabla son de FPS/3D — NO VERIFICADO un equivalente numérico para 2D en las fuentes consultadas. Aplican los mismos principios sin cifra fija: grid = tile size del proyecto, pasillo/hueco ≥2× el ancho del personaje, altura de salto medida con la física real del juego (no estimada), y jugarlo con el controller real antes de dar por buena cualquier medida.

## Playtesting de niveles

Método Valve (Phil Co / GDC): "todo lo que hacemos en la semana apunta al viernes" — playtest semanal con gente EXTERNA al equipo, cada nivel de HL2 pasó por más de 100 playtesters. El nivel se termina cuando los testers dejan de atascarse, no cuando el diseñador está conforme.

Tipos de test según fase:
| Tipo | Quién | Cuándo | Detecta |
|------|-------|--------|---------|
| Self-playtest | Tú mismo (o el agente ejecutando el juego) | Diario | Lo obvio: escala, colisiones, softlocks |
| Critique | Devs con experiencia | Tras cada fase (layout → blockout → arte) | Problemas estructurales |
| Público | Gente ajena al gamedev | Post-arte | Problemas invisibles para expertos |
| Blind test | Público sin ninguna guía | Final | La experiencia real de lanzamiento |

Protocolo de observación (Level Design Book + Valve):
1. Definir ANTES qué preguntas debe responder la sesión.
2. Briefing mínimo — sobre-instruir contamina el dato.
3. Observar sin intervenir: no explicar, no disculparse, no rescatar (salvo bloqueo total). Anotar dónde duda, dónde muere, dónde mira.
4. Debrief con preguntas de comprensión concretas ("¿viste la luz naranja sobre la puerta? ¿qué creíste que significaba?") y subjetivas ("¿el combate se sintió fácil o difícil?").
5. Actuar sobre PATRONES (≥2-3 testers con el mismo problema), no anécdotas. Y regla de oro: cuando un tester sugiere una solución, su solución suele ser mala pero **el problema que la motivó es real** — arreglar el problema, no implementar la sugerencia.

Telemetría barata que un agente puede instrumentar: posiciones de muerte (heatmap), tiempo por sala, % que encuentra cada secreto, dónde se gasta cada recurso, tasa de finalización. Con 20 jugadores ya salen patrones accionables.

Advertencias sobre el dato (de Adriaan de Jongh, GDC 2017 "Playtesting: Avoiding Evil Data", vía The Level Design Book):
- Testers novatos son demasiado amables (no verbalizan problemas); testers expertos exageran detalles menores. Calibrar el peso de cada perfil.
- Observación directa > encuestas: los formularios distraen y producen respuestas socialmente deseables. Mejor grabación de pantalla + think-aloud.
- Referencia fundacional del método: Mike Ambinder (Valve), GDC 2009 "Valve's Approach to Playtesting".

## Pipeline de un nivel (de idea a terminado)

Fases y criterio para avanzar a la siguiente (síntesis del proceso de Valve y The Level Design Book):

| Fase | Producto | Criterio de salida |
|------|----------|--------------------|
| 1. Concepto | Una frase: qué mecánica/idea explora el nivel + dónde cae en la curva de la campaña | La frase no se solapa con otro nivel |
| 2. Sketch / papel | Layout top-down con camino crítico, ramas, gates, loops y beat chart | El flujo se entiende sin explicarlo |
| 3. Blockout | Geometría gris jugable con colisión, escala y encuentros placeholder | Testers navegan sin perderse; pacing observado ≈ beat chart; critique de devs pasada |
| 4. Scripting/encounters | Encuentros reales, economía de recursos, secretos colocados | Cada encuentro distinto; sin softlocks; telemetría instrumentada |
| 5. Art pass | Arte sobre la geometría VALIDADA (no antes) | La legibilidad sobrevive al arte: landmarks siguen dominando, wayfinding intacto |
| 6. Polish | Iluminación final, audio, micro-ajustes por playtest ciego | Blind testers completan sin atascos |

Notas de proceso:
- **El orden importa más que las fases**: el error caro es adelantar la fase 5. Todo lo anterior a arte se tira barato (regla de los orange maps).
- Cadencia Valve: iterar en incrementos de 1-2 semanas, cada incremento cierra con playtest externo, y lo observado prioriza la semana siguiente — el backlog del nivel lo escribe el playtest, no el diseñador.
- Tras el alpha del juego completo, presupuestar un pase global de calidad sobre todos los niveles (HL2 dedicó ~4 meses): los niveles se diseñan aislados pero se juegan en secuencia — el pacing ENTRE niveles solo se ve ahí.
- Para un dev solo o agente: las fases 3-4 son donde vive el 70% del valor; un blockout bien testeado con arte mediocre es mejor juego que arte hermoso sobre layout roto. Ver [ver: produccion-proceso] para el encaje en el plan general.

## Reglas prácticas

- [ ] Cada nivel responde "¿qué idea de gameplay explora este nivel?" en una frase. Si no, córtalo o fusiónalo.
- [ ] Estructura kishotenketsu: introducir (seguro) → desarrollar → girar → examinar. Una mecánica nueva o combinación nueva por nivel.
- [ ] Primer contacto con toda mecánica/enemigo nuevo: aislado y con castigo mínimo por fallo.
- [ ] Dibuja el beat chart del nivel (intensidad 1-10 por sala): dientes de sierra hacia clímax; valle de 30-45 s tras cada pico; nunca sostener el pico más de unos segundos.
- [ ] Nunca repitas un encuentro idéntico (misma geometría + misma composición enemiga).
- [ ] Un landmark/weenie visible que tire del jugador; nunca sightline completa del landmark desde el punto A — revela por capas.
- [ ] Contraste como ritmo espacial: alterna abierto/cerrado, claro/oscuro, alto/bajo. Cambia altura de suelo cuando cambies de material/zona.
- [ ] Cada zona (district) con paleta/identidad visual propia; nodos de decisión legibles.
- [ ] Wayfinding con la mínima certeza necesaria: luz/composición antes que flechas; flechas antes que teletransporte.
- [ ] Gating: garantiza por construcción que el jugador tiene la herramienta ANTES del reto que la exige (gate físico, no fe).
- [ ] Diseña al menos un loop de atajo que conecte de vuelta al hub/checkpoint, abierto desde el lado lejano.
- [ ] Arenas: ≥2 rutas, cobertura direccional (no omnidireccional), entrada con lectura previa del espacio, un "juguete" que habilite el giro.
- [ ] Los recursos del encuentro incentivan el comportamiento que quieres ver (agresión → loot por agredir).
- [ ] Cada nivel con ≥1 secreto insinuado (pista visual/sonora), recompensa proporcional a la fricción.
- [ ] Ramas opcionales cortas que devuelven al camino crítico; nada de retraversía obligatoria larga.
- [ ] Blockout en gris jugado con colisión real ANTES de cualquier arte; figura de escala en cada sala.
- [ ] Métricas base: paredes 150-200% de la altura del avatar; pasos ≥2× su ancho; grid consistente.
- [ ] Playtest cada iteración; observa sin intervenir; corrige patrones, no anécdotas.
- [ ] Instrumenta desde el blockout: muertes, tiempo por sala, % de secretos hallados.
- [ ] El nivel está listo cuando testers frescos lo terminan sin atascarse — no cuando a ti te gusta.

## Errores comunes

| Pitfall | Antídoto |
|---------|----------|
| Tutorial por popup de texto para algo que el espacio podía enseñar | Kishotenketsu: zona segura + repetición con giro. Texto solo para lo que el espacio no puede decir |
| Dificultad monótonamente creciente (sin valles) | Curva en dientes de sierra; valle de 30-45 s tras cada pico (patrón L4D) |
| "30 segundos de diversión" repetidos en el mismo contexto | La segunda mitad de la cita de Griesemer: variar entorno, armas, enemigos, combinaciones en cada repetición |
| Nivel-pasillo bonito: arte primero, layout después | Blockout gris jugado y playtesteado antes de un solo asset final (orange maps de Valve) |
| Escala rota (salas gigantes vacías o pasillos claustrofóbicos sin querer) | Figuras de escala + jugar cada iteración con el controller/character real |
| Jugador perdido: zonas idénticas, cero landmarks | Los 5 elementos de Lynch; un weenie por zona; contraste de districts |
| Jugador guiado con pintura amarilla en todo | Escala de certeza: empezar sutil (luz, composición, breadcrumbs) y subir solo si el playtest lo exige |
| Cobertura omnidireccional y arenas de una sola entrada | Cobertura direccional, ≥2 rutas, flancos para ambos bandos |
| Encuentro que premia esconderse cuando el juego quiere agresión | Alinear economía del encuentro con el comportamiento deseado (push-forward de DOOM) |
| Spawns a la espalda, refuerzos sin anuncio, último enemigo escondido | Primer contacto legible, refuerzos anunciados, cierre de oleada activo |
| Secretos solo hallables por fuerza bruta (rozar todas las paredes) | Todo secreto insinuado: anomalía visual, sonido, geometría sospechosa |
| Recompensar un desvío largo con basura | Recompensa proporcional a la fricción, o el jugador deja de explorar |
| Gating por suposición ("ya habrá conseguido el doble salto") | Gate físico que garantiza la herramienta antes del reto |
| Retraversía larga tras cada muerte o exploración | Loops de atajo estilo Dark Souls, abiertos desde el lado lejano |
| Implementar literalmente la sugerencia del playtester | Extraer el problema real detrás de la sugerencia y resolverlo a tu manera |
| Playtest solo con el propio equipo | Testers externos frescos por iteración (Valve: >100 por nivel); el equipo ya no puede "no saber" |
| Declarar el nivel terminado por opinión propia | Criterio de salida: testers frescos lo completan sin atascos y el beat chart observado coincide con el diseñado |

## Fuentes

- **"The secret to Mario level design"** — Game Developer (entrevista a Koichi Hayashida, director SM3D Land/World) — la fuente primaria del kishotenketsu aplicado a niveles y su origen en Miyamoto.
- **Super Mario 3D World's 4 Step Level Design** — análisis del patrón (Game Maker's Toolkit y cobertura de MCV/Nintendo Life sobre el mismo material) — ejemplo Cakewalk Flip paso a paso.
- **The Level Design Book** (book.leveldesignbook.com, Robert Yang et al.) — capítulos Blockout, Wayfinding y Playtesting — métricas concretas de greybox, escala de certeza de wayfinding, protocolo de playtest; la referencia práctica más densa y actual.
- **"The AI Systems of Left 4 Dead"** — Mike Booth, Valve (keynote 2009, PDF oficial) — algoritmo de pacing build-up/sustain(3-5 s)/fade/relax(30-45 s); "ajustar frecuencia, no amplitud".
- **"Ten Principles of Good Level Design"** — Dan Taylor, GDC 2013 + su artículo en 2 partes en Gamasutra/Game Developer — el checklist de alto nivel de la primera sección.
- **"Classic Postmortem: The Making of Half-Life 2"** — Game Developer — cabals de 4-5 personas, orange maps, pase de calidad de ~4 meses post-alpha.
- **"Valve's Design Process for Creating Half-Life 2"** — GDC 2006 (slides oficiales) — ciclos de 1-2 semanas, ~15 min de gameplay en bruto por iteración, >100 playtesters por nivel.
- **"Learning From The Masters: Level Design in The Legend of Zelda"** — Mike Stout, Game Developer — camino crítico + ramas, lock & key con gates físicos, ramp de encuentros sin repetición.
- **"Half-Minute Halo: An Interview with Jaime Griesemer"** — Engadget — la cita completa de "30 seconds of fun" y los loops anidados 3 s / 30 s / 3 min (de la charla GDC 2002 "The Illusion of Intelligence").
- **"Embracing Push Forward Combat in DOOM"** — Kurt Loudy & Jake Campbell, id Software, GDC 2018 — filosofía de encounter design que incentiva agresión vía economía de recursos.
- **Cobertura CEDEC 2017 de Breath of the Wild** (Kotaku, 80 Level, Nintendo Life) + **"Open world level design: spatial composition and flow in BotW"** — Robert Yang, Radiator Blog — regla del triángulo en 3 escalas, "gravedad" del terreno, sightlines parciales.
- **Reglas de level design de John Romero para Doom** (documentadas en Doom Wiki, análisis de Chubzdoomer y otros) — contraste, altura de suelo, landmarks, áreas secretas como regla fija.
- **"An Architectural Approach to Level Design"** — Christopher Totten (CRC Press) — Kevin Lynch aplicado a niveles (paths/edges/districts/nodes/landmarks), weenies, prospect-refuge. Consultado vía índice y material de la editorial, no lectura completa.
- **"What Mario Learned from Mickey Mouse — Part 3: Decision Making and Weenies"** — Game Developer — el weenie de Disney como herramienta de decisión y wayfinding en juegos.
- **Análisis del diseño interconectado de Dark Souls** (TheGamer; James Roha, Medium) — loops de atajo con geometría real, estructura vertical, hub radial (Firelink Shrine).
