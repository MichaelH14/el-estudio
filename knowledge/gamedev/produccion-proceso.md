# Producción e iteración

> **Cuando cargar este archivo:** al planificar o revisar el proceso de un juego en desarrollo — definir milestones, organizar playtests, decidir si cortar/pivotar/perseverar, controlar scope creep, ejecutar el polish pass final, o calibrar ritmo de trabajo sostenible (especialmente dev solo).

## Milestones estándar y criterios de salida

Pipeline canónico (síntesis de Tim Cain — 30+ años, Fallout/Outer Worlds — y práctica de industria). Cada milestone necesita: entregable concreto, dueño del sign-off, y criterio de entrada al siguiente.

| Milestone | Qué es | Criterio de salida (exit) |
|---|---|---|
| **Test rooms** | Niveles aislados que prueban UNA feature (sala de combate para IA, sala de diálogo para triggers) | La feature funciona aislada; sabes sus parámetros |
| **Prototype** | Juego jugable mecánicamente, sin arte final. "Probar todas las features juntas" | El core loop es divertido con arte placeholder. Si no lo es aquí, no lo será nunca |
| **Beautiful corner** | Área pequeña muy pulida, no jugable (solo cámara/caminar) | El equipo/publisher ve cómo se VERÁ el juego final |
| **First playable / Vertical slice** | Una sección con casi todas las features y arte "virtualmente" final. Cerny lo llama "publishable first playable" | Demuestra exactamente cómo se verá Y jugará el final. **Cerny: si esta versión no emociona a jugadores externos, se archiva la idea** |
| **Horizontal slice** | Ortogonal al vertical: TODAS las áreas jugables, ninguna terminada | Ves conectividad entre niveles y estimas duración total real |
| **Alpha (feature complete)** | Todas las features implementadas; todas las áreas con su contenido principal; jugable de inicio a fin. Bugs y desbalance permitidos | "Se puede probar todo lo que un jugador potencialmente puede hacer". **Feature freeze**: después de alpha no entran features nuevas |
| **Content complete** | Todo el contenido (niveles, arte, audio, texto) está dentro, aunque sin pulir | Cero placeholders. Solo queda fix, balance, polish |
| **Beta** | Todo dentro; foco exclusivo en correcciones, balance, optimización. Testing externo a escala | Cero bugs bloqueantes conocidos; performance en targets; localización cerrada |
| **Release candidate / Gold** | Build estable y completo, candidato a publicarse tal cual | Pasa el pase de certificación/QA final sin bugs de rechazo. Es lo que se shippea |
| **Post-launch** | Parches, DLC, contenido vivo | (ciclo continuo — presupuestar ANTES del launch, ver burnout abajo) |

Nota de términos: aquí "first playable / vertical slice" se trata como UN milestone de calendario (síntesis de Cain/Cerny); el desglose fino de first playable vs vertical slice vs MVP como artefactos distintos está en [ver: preproduccion]. Los nombres varían entre estudios — lo que no varía: cada hito necesita criterio de salida explícito ANTES de empezarlo.

Reglas duras sobre milestones:
- **Preproducción no se calendariza como producción** (Cerny, DICE 2002): la fase creativa es impredecible; se le pone presupuesto, no fechas de entregables detallados. La producción (post first-playable) sí se planifica con fechas. [ver: preproduccion]
- Alpha = features; content complete/beta = contenido. Mezclar los dos gates es la vía clásica al retraso infinito.
- "Jugable de inicio a fin" significa literalmente eso: con placeholder está bien, con huecos no.

## Playtesting

### El método Valve (referencia de industria)

Documentado en Portal, Half-Life 2, Left 4 Dead, HL: Alyx (vía GMTK, "Valve's Secret Weapon"):

- **Frecuencia**: semanal, o cada vez que hay contenido nuevo significativo. Ciclo de Portal: playtest viernes → discusión lunes → aplicar cambios en la semana → volver a testear viernes.
- **Testers frescos**: alguien que NUNCA ha visto el juego, sentado a jugarlo de principio a fin. Cada capítulo de HL2 pasó por ~100 playtesters.
- **Quién observa**: los propios diseñadores, no un departamento externo. Ver sufrir al jugador con tu puzzle "obvio" motiva el fix como ningún reporte.
- **Regla de silencio absoluto**: cero pistas, cero ayuda, cero respuestas durante la sesión. Si tienes que explicar algo, ese es el bug.
- **Feedback = validación de hipótesis, no mandato**. El playtest te dice DÓNDE duele; la solución la diseñas tú.
- Origen de la devoción: Half-Life 1 — a ~2 meses del lanzamiento previsto Valve concluyó que el juego no era bueno, lo retrasó cerca de un año y lo rehízo. El playtest sistemático existe para no volver a llegar ahí.

Cambios reales salidos de playtest: Portal simplificó sus ambientes a paredes blancas porque los testers ignoraban los elementos clave entre el ruido visual; la gravity gun de HL2 se movió a más temprano en el juego; Left 4 Dead añadió siluetas de compañeros a través de paredes.

### Cuánta gente y con qué frecuencia

| Objetivo | Gente | Base |
|---|---|---|
| Encontrar problemas de usabilidad/claridad (cualitativo) | ~5 testers frescos por ronda encuentran ~85% de los problemas | Nielsen/Landauer; válido si el público es homogéneo |
| Problemas de baja frecuencia | 9–18 | Games User Research; los juegos son más complejos que las webs del estudio original |
| Balance/benchmarks cuantitativos | 20–40+ (o telemetría) | NN/g cuantitativo; Slay the Spire usó servidor de métricas + Discord |
| Frecuencia | Semanal o por cada contenido nuevo significativo | Valve |

Heurística: muchas rondas pequeñas con gente fresca > una ronda grande. Un tester quemado (ya conoce el juego) solo sirve para balance, no para claridad/onboarding.

### Qué preguntar (y qué no)

Marco de Schell (*The Art of Game Design*, cap. de playtesting — las seis preguntas): **por qué** testeas (qué hipótesis/riesgo concreto), **quién** (público objetivo, no amigos devs), **cuándo**, **dónde**, **qué** buscas observar, **cómo** lo evalúas sin interrumpir la experiencia.

- Antes de la sesión: escribe la hipótesis ("el jugador entenderá X sin tutorial"). Sin hipótesis, el playtest es entretenimiento.
- Durante: observa y anota — dónde se atasca, qué ignora, cuándo mira el teléfono (aburrimiento), qué repite (diversión). No hables.
- Después, preguntas abiertas sobre EXPERIENCIA, no sobre diseño: "¿qué estaba pasando ahí?", "¿qué intentabas hacer?", "¿cuándo te sentiste perdido/poderoso?", "¿dónde dejarías de jugar?". Evita "¿te gustó?" (todos dicen que sí) y "¿qué cambiarías?" (los jugadores diagnostican bien y recetan mal).
- Los datos de conducta pesan más que las opiniones: lo que HIZO > lo que DICE.

### Protocolo de una sesión (síntesis operativa de Valve + Schell)

**Antes:**
1. Escribe la hipótesis y los 1–3 riesgos que esta sesión debe despejar (el "por qué" de Schell).
2. Build estable dedicado (nunca el working build), con saves/atajos para saltar a la zona bajo prueba si la sesión no es full-run.
3. Recluta testers del público objetivo que no hayan visto el juego. Amigos devs solo si tu público son devs.
4. Prepara hoja de observación: columnas típicas — timestamp, dónde se atascó, qué ignoró, qué repitió, emoción visible, cita textual.

**Durante:**
5. Una frase de encuadre y nada más: "juega como en tu casa; piensa en voz alta si te sale natural; no te puedo ayudar".
6. Silencio. No respondas preguntas ("¿y ahora qué hago?" se anota, no se contesta). Rescata solo ante bug bloqueante real.
7. Anota conducta con timestamp; si puedes, graba pantalla + cara. La cara dice aburrimiento antes que la boca.

**Después:**
8. Preguntas abiertas de experiencia (ver arriba), de lo general a lo específico. Última pregunta útil: "¿le dirías a un amigo que lo juegue? ¿cómo se lo describirías?" — la descripción revela qué juego CREE que jugó.
9. Triage el mismo día o al siguiente (ciclo Portal: viernes test, lunes discusión): cada observación se clasifica en bug / fricción / claridad / diseño, con severidad por cuántos testers tropezaron.
10. Decide cambios como hipótesis nuevas y re-testea la semana siguiente con gente fresca. Un fix de claridad no está "listo" hasta que un tester nuevo pasa sin tropezar.

### Cadencia semanal de iteración

Modelo compuesto de los ciclos documentados de Portal (test viernes → discusión lunes → cambios en semana) y Slay the Spire (update semanal + Discord + métricas):

| Día | Actividad |
|---|---|
| 1 | Triage del playtest anterior; elegir hipótesis de la semana; actualizar lista de corte |
| 2–4 | Implementar cambios; contenido nuevo solo si el core de la semana pasada quedó validado |
| 5 | Build de playtest + sesión con testers frescos (y/o push del update de Early Access) |
| Continuo | Recoger telemetría/Discord; anotar, no reaccionar en caliente |

Para dev solo la cadencia semanal también es heartbeat de moral: un playtest o build compartido por semana evita los túneles de meses sin contacto con jugadores reales, que es donde el scope y el autoengaño crecen.

## Iteración: kill your darlings, pivotar vs perseverar

| Señal | Decisión | Caso real |
|---|---|---|
| El first playable no emociona a jugadores externos | **Archivar la idea** antes de quemar producción | Regla central del método Cerny |
| El core loop no es divertido tras N iteraciones honestas de prototipo | Pivotar el core o matar el proyecto — el contenido no arregla un core aburrido | Cerny; Derek Yu #5 |
| El juego completo "no es bueno" cerca del final | Pivote duro: retrasar y rehacer es más barato que shippear un muerto | Half-Life 1 (delay ~1 año → clásico) |
| Una minoría vocal odia una feature que TÚ verificaste que sirve a la visión y funciona en juego | **Perseverar** | Darkest Dungeon: sistema de corpses/heart attacks en Early Access — backlash vocal, Red Hook lo mantuvo (cita textual de su defensa NO VERIFICADA en esta sesión) y el juego triunfó. Añadieron un toggle después: perseverar ≠ ignorar |
| Las métricas contradicen tu intuición | Investigar antes de obedecer: "metrics can be misleading if not carefully interpreted" | Slay the Spire (GDC 2019) |
| El código "es un desastre, mejor empiezo de cero" | **Nunca reiniciar el proyecto**. "Tu código siempre será un desastre" — se refactoriza lo que duele, no se reescribe el juego | Derek Yu #11 |
| Idea nueva brillante a mitad de desarrollo | Anotarla para el SIGUIENTE juego, no meterla en este | Derek Yu #12 |
| Abandonaste un proyecto | El siguiente se hace MÁS pequeño, no más ambicioso | Derek Yu #14 |

Kill your darlings operativo: mantén una **lista de corte** viva, ordenada por (costo de terminar × poco aporte al core). Cuando el calendario apriete, se corta desde arriba de esa lista sin renegociar la visión. Cortar una feature completa > dejar cinco a medias — una feature a medias es deuda visible; una cortada es invisible.

## Scope creep: cómo se cuela y cómo cortarlo

Dato duro (Ara Shirinian, "Dissecting the Postmortem", Game Developer/Gamasutra — análisis de 24 postmortems publicados feb-2008 a ene-2010, verificado leyendo el artículo completo): **71% (17/24) reportó problemas de scope** (falta de tiempo/recursos o diseño de más que hubo que cortar repetidamente); **38% (9/24) reportó crunch explícito** (duración: de 6 meses a "casi un año completo", probablemente subreportado — un postmortem no menciona crunch no significa que no lo hubo); **38% (9/24) recibió extensión de plazo**. Un estudio académico independiente sobre una muestra mayor —Washburn, Sathiyanarayanan, Nagappan, Zimmermann & Bird, "'What Went Right and What Went Wrong': An Analysis of 155 Postmortems from Game Development" (ICSE 2016 Companion, RIT + Microsoft Research)— confirma que scope y proceso/gestión son los fallos dominantes en una muestra más grande; sus cifras exactas no se verificaron en esta sesión (paper de acceso cerrado), por eso no se citan porcentajes de ese paper aquí. El scope irrealista es el fallo más repetido de la muestra verificada, y el crunch es su síntoma-amplificador más citado.

Cómo se cuela (vectores clásicos):
1. Features "pequeñas" ("es solo un toggle") — el costo real es feature × testing × UI × balance × bugs.
2. Feedback de playtest tratado como lista de deseos en vez de síntomas.
3. Reinventar tecnología: motor propio, editor propio, netcode propio (Derek Yu #3: usa herramientas existentes; la prioridad es el juego, no la infraestructura).
4. "Restart syndrome": reescribir lo que ya funcionaba.
5. Comparar tu juego en desarrollo contra juegos AAA terminados y "corregir" la distancia.
6. Diseño sin visión comunicada: 38% de los postmortems reportaron problemas de comunicación, típicamente confusión sobre la visión/dirección — cada quien agranda su parte.

Señales tempranas (si detectas 2+, ya tienes scope creep):
- El "juego mínimo" de hoy tiene features que el pitch original no tenía.
- Llevas más de una semana en un sistema que ningún playtest pidió.
- La fecha de alpha se ha movido más de una vez sin cortar nada a cambio.
- Hay N features "al 80%" y ninguna cerrada.
- Estás escribiendo herramientas/motor en vez de juego (Yu #3).
- El diseño crece en documentos pero el build jugable lleva semanas igual.

Antídotos:
- **Feature freeze en alpha, content freeze en content complete.** Escritos, con fecha, sin excepciones sin trade (entra X ⇒ sale Y de igual costo).
- Deadline externo real: competencia, festival, fecha de publisher (Derek Yu #8: las jams/IGF funcionan como plazos y comunidad).
- Presupuesto de tedio: "mucho de hacer juegos es tedioso" (Yu #7) — menús, transiciones, save/load, settings van al plan desde el día uno; si no caben, el juego es más chico de lo que crees.
- La pregunta de corte de Derek Yu (#13): la restricción fuerza creatividad — quita todo lo que el core no necesita.

## El polish pass: qué toca y en qué orden

Derek Yu #15: **"el último 10% es el 90% del esfuerzo"** — el polish no es un fin de semana, es una fase con presupuesto propio.

Orden recomendado (síntesis operativa — el orden exacto no es canon de una sola fuente; los conceptos sí lo son):

| # | Pase | Qué toca | Por qué en este orden |
|---|---|---|---|
| 1 | **Estabilidad** | Crashes, bloqueos de progresión, save corrupto | Un crash invalida todo lo demás |
| 2 | **Fricción ("oil")** | Todo lo que hace COSTOSO el input: menús lentos, confirmaciones de más, controles ambiguos, cargas, deadzones | Quitar dolor antes de añadir placer; el juice sobre fricción irrita. NO VERIFICADO: el término "oil" para fricción de input se usa aquí como síntesis operativa — no se encontró un artículo fuente independiente con ese nombre |
| 3 | **Juice / game feel** | Feedback máximo por input mínimo: screenshake, partículas, tweens, squash & stretch, SFX, hit-stop ("Juice it or Lose it", Jonasson & Purho, GDC Europe 2012). Tuning → juicing → streamlining | Es lo que se siente "vivo". [ver: game-feel] |
| 4 | **Consistencia de contenido** | Texto (typos, tono), iconografía, paleta, volúmenes de audio, transiciones entre escenas, estados vacíos | Lo que grita "amateur" en reviews |
| 5 | **Onboarding** | Primeros 10 minutos con testers 100% frescos — es lo último que se pule porque todo lo anterior lo cambia | [ver: ux-ui-onboarding] |
| 6 | **Performance** | Frame time estable en hardware mínimo, tiempos de carga, memoria | Al final porque el contenido ya no cambia (pero con budgets vigilados desde el vertical slice) |

Advertencia con fuente: Jonasson & Purho, en la misma charla ("Juice it or Lose it", GDC Europe 2012), advierten que el juice no sustituye al diseño — amplifica un buen core, no arregla uno malo.

## Lecciones que más se repiten en postmortems reales

Todas con origen verificable (ver Fuentes):

1. **El scope irrealista es el fallo #1** — 71% de los postmortems lo reportan; conclusión textual de Shirinian: "one of the most common and disturbing trends is the inability for game development projects to be properly scoped and scheduled".
2. **El crunch es síntoma y amplificador, nunca solución** — 38% lo reporta explícitamente (probablemente subreportado); todos saben que es un problema y sigue ocurriendo porque es el efecto colateral de los demás fallos.
3. **La visión no comunicada mata equipos** — 38% reporta fallos de comunicación (confusión de visión/dirección); ~50% problemas de gestión de equipo.
4. **Playtest semanal con gente fresca es el arma secreta** — Valve institucionalizó el proceso tras casi shippear un Half-Life malo; Portal es su producto más puro.
5. **La preproducción termina con un playable que emociona, no con un documento** — método Cerny: "publishable first playable" o la idea se archiva.
6. **El prototipo prueba diversión, no tecnología** — Tim Cain: el prototype existe para "probar todas las features juntas" antes del arte.
7. **Early Access funciona con cadencia + datos** — Slay the Spire: updates semanales, Discord y servidor de métricas → 1M+ copias en su primer año aún en Early Access.
8. **Las métricas sin interpretación mienten** — advertencia explícita del equipo de Slay the Spire.
9. **Aguanta a la minoría vocal cuando la feature sirve a la visión** — Darkest Dungeon mantuvo corpses/heart attacks contra el backlash y acertó; ofrecer un toggle después desactivó el conflicto.
10. **No reinventes el motor** (Yu #3) y **no reinicies el proyecto** (Yu #11) — los dos suicidios lentos favoritos del dev técnico.
11. **El último 10% es el 90%** (Yu #15) — presupuesta el polish como fase, no como sobrante.
12. **Shippear te convierte en desarrollador** — Derek Yu: terminar es una SKILL que se entrena terminando; el juego lanzado imperfecto enseña más que el perfecto abandonado.
13. **El éxito no elimina el burnout, lo acelera** — Eric Barone (Stardew Valley): ~70h/semana × 4.5 años en solitario; a los pocos meses del launch (con el juego siendo un éxito masivo) cayó en burnout total por la presión de parches, con all-nighters cuyos parches "creaban tantos problemas como resolvían".
14. **Sobrevivir > pegarla** — Jake Birkett (GDC 2016, "How to Survive in Gamedev for Eleven Years Without a Hit"): 11 años y 10+ juegos rentables sin un solo hit. Mensaje central (vía resúmenes de terceros, sin cita textual verificada): la inmensa mayoría de devs nunca shippea un hit, y aun así se puede vivir de esto con la estrategia correcta.

## Sostenibilidad para dev solo

El burnout mata más proyectos que la falta de talento. Datos y tácticas de las fuentes:

- **El caso Barone es advertencia, no modelo**: 10h/día, 7 días/semana, 4.5 años. Funcionó una vez de forma célebre Y AUN ASÍ terminó en burnout post-launch. Un agente/dev que planifique así está planificando el colapso.
- **Derek Yu #10**: la salud mental y física es infraestructura del proyecto — descuidarla sabotea la creatividad y la motivación que el proyecto necesita.
- **Tácticas Birkett** (supervivencia sin hit): portafolio de varios juegos pequeños > un juego enorme; un género que dominas e iterar sobre él; vender en muchas tiendas (hasta las pequeñas); ingresos paralelos legítimos (contratos, enseñanza) sin culpa; redefinir éxito como "vivir de hacer lo que amas", no como hit.
- **Elige proyectos que puedas terminar** (Yu #1): que disfrutes hacerlo + que quieras haberlo terminado + género donde tienes experiencia. Dos de tres no basta.
- **Post-launch se presupuesta antes del launch**: parches, soporte, comunidad. El día 1 no es la meta, es el cambio de fase (lección Barone).
- Ritmo concreto: sesiones de trabajo con final definido, hitos pequeños semanales (un playtest semanal es también un heartbeat de moral), y avanzar por otra sección cuando te atasques en una (Yu #9) en vez de forzar la pared.

Chequeo de sostenibilidad al planificar (aplícalo a cualquier plan de proyecto):

| Pregunta | Si la respuesta es no… |
|---|---|
| ¿El plan cabe en ≤40–45h/semana sostenidas? | Recorta scope, no sueño. El plan a 70h/semana es el plan del colapso (caso Barone) |
| ¿Hay runway financiero para TODO el plan + margen? | Birkett: recorta el juego o añade ingreso paralelo ANTES de quedarte sin caja, no después |
| ¿Puedes shippear algo (demo, EA, juego chico) en los próximos meses? | Proyecto multi-año sin releases intermedios = riesgo máximo de abandono para un solo dev |
| ¿El género/alcance es uno donde ya shippeaste algo? | Yu #1 y Birkett: itera sobre lo que dominas; el salto de ambición se paga en años |
| ¿Sigue habiendo vida fuera del juego (ejercicio, gente, sueño)? | Yu #10: la salud es infraestructura del proyecto, no un lujo post-launch |

## Reglas prácticas

- [ ] Define TODOS los milestones con criterio de salida escrito antes de producción; alpha = feature freeze, content complete = content freeze.
- [ ] Preproducción sin fechas rígidas (presupuesto sí); producción con fechas solo DESPUÉS del first playable que emociona.
- [ ] Si el prototipo con arte placeholder no es divertido, no entres a producción. Punto.
- [ ] Playtest semanal (o por contenido nuevo) con testers 100% frescos; ~5 por ronda para claridad, 20+ o telemetría para balance.
- [ ] En playtest: silencio absoluto, observa conducta, anota atascos. Preguntas después, abiertas, sobre experiencia — nunca "¿te gustó?".
- [ ] Cada playtest tiene hipótesis escrita ANTES de la sesión.
- [ ] Feedback = síntoma válido + solución sospechosa. Diagnóstico del jugador sí, receta del jugador no (hasta verificarla).
- [ ] Mantén una lista de corte viva ordenada por costo/aporte; cuando apriete el calendario, corta desde arriba sin drama.
- [ ] Feature nueva a mitad de proyecto → al documento del SIGUIENTE juego.
- [ ] Nunca reescribas el proyecto de cero; nunca cambies de motor a mitad de camino sin causa mortal verificada.
- [ ] Entra X al scope ⇒ sale Y de costo igual. Sin trade no entra.
- [ ] Presupuesta el "tedio" (menús, saves, settings, transiciones) desde el día uno.
- [ ] Polish en orden: estabilidad → fricción → juice → consistencia → onboarding → performance.
- [ ] Reserva fase explícita de polish: el último 10% del juego = ~90% del esfuerzo percibido.
- [ ] Ante minoría vocal contra una feature: verifica con datos/playtests frescos; si sirve a la visión, persevera y considera un toggle.
- [ ] Deadline externo real (jam, festival, fecha pública) para cada proyecto.
- [ ] Ritmo sostenible: si el plan requiere 70h/semana, el plan está mal — recorta scope, no sueño.
- [ ] Presupuesta el post-launch (parches/soporte) antes de lanzar.
- [ ] Termina y shippea: un juego pequeño lanzado > un juego grande abandonado. Terminar es una skill que se entrena.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Llamar "alpha" a un build sin todas las features ("alpha marketing") | Alpha = feature complete jugable de inicio a fin; usa los nombres con su gate real |
| Calendarizar la preproducción como si fuera producción | Presupuesto sí, fechas detalladas no, hasta tener first playable (Cerny) |
| Ayudar al tester atascado ("es que ahí tienes que…") | Silencio total; el atasco ES el dato. Si necesitó tu voz, el juego falla solo |
| Testear siempre con los mismos amigos/devs | Testers frescos cada ronda; los quemados solo sirven para balance |
| Preguntar "¿te gustó?" / "¿qué cambiarías?" | Preguntas de experiencia ("¿qué intentabas hacer ahí?") + observación de conducta |
| Implementar literalmente cada sugerencia de playtest | Tratar feedback como síntoma; diseñar la solución tú; re-testear |
| Obedecer métricas sin contexto | Interpretar antes de actuar (lección explícita de Slay the Spire) |
| Revertir una feature central por backlash vocal de Early Access | Verificar con datos/testers frescos; si sirve a la visión, mantener + toggle (Darkest Dungeon) |
| "Solo es una feature pequeña" | Costo real = feature × UI × testing × balance × bugs; pasa por el trade X⇒Y |
| Motor/engine/editor propio "porque lo necesito" | Herramienta existente; la prioridad es el juego (Yu #3) |
| Reescribir el proyecto porque el código "es un desastre" | El código siempre es un desastre; refactor local, nunca restart (Yu #11) |
| Juicear un core loop aburrido | El juice amplifica, no arregla; vuelve al prototipo del core |
| Polish "cuando sobre tiempo" | Fase con presupuesto propio: es el 90% del esfuerzo del último 10% |
| Pulir onboarding temprano | Onboarding al final del polish, con testers frescos — todo lo anterior lo invalida |
| Planificar crunch ("el último mes apretamos") | El crunch es el síntoma #1 de scope mal cortado (71% de postmortems); recorta scope ahora |
| Modelo Stardew ("si trabajo 70h/semana 4 años, triunfo") | Sesgo de superviviente + el propio Barone terminó en burnout; scope al ritmo sostenible |
| Tratar el launch como la meta final | Presupuestar parches/soporte/comunidad pre-launch; el día 1 es cambio de fase |

## Fuentes

- **"Finishing a Game" — Derek Yu (makegames, 2010)** — el texto canónico indie sobre terminar juegos; origen de los 15 consejos citados (core divertido primero, no reinventar tecnología, no reiniciar, cortar features, el último 10% = 90%).
- **"Valve's Secret Weapon" — Mark Brown / GMTK (Substack)** — el proceso de playtesting de Valve documentado: ciclo semanal de Portal, ~100 testers por capítulo de HL2, regla de silencio, casos concretos (paredes blancas de Portal, gravity gun, Left 4 Dead), y el origen en el casi-desastre de Half-Life 1.
- **"9 stages of game production according to Tim Cain" — Game World Observer (2023)** — pipeline de milestones con definiciones operativas (test rooms, beautiful corner, prototype, vertical/horizontal slice, alpha, beta) de un veterano de Fallout.
- **Método "Method" — Mark Cerny (D.I.C.E. Summit 2002)** — separación preproducción/producción y el gate del "publishable first playable"; si no emociona, la idea se archiva.
- **"Dissecting the Postmortem: Lessons Learned From Two Years Of Game Development Self-Reportage" — Ara Shirinian (Game Developer/Gamasutra, 2010)** — análisis de 24 postmortems publicados feb-2008 a ene-2010, leído completo en esta sesión. Fuente VERIFICADA de las cifras: 71% (17/24) scope, 38% (9/24) crunch explícito, 38% (9/24) extensión de plazo, ~50% (11/24) gestión de equipo, 38% (9/24) comunicación/visión.
- **"'What Went Right and What Went Wrong': An Analysis of 155 Postmortems from Game Development" — Washburn, Sathiyanarayanan, Nagappan, Zimmermann & Bird (ICSE 2016 Companion, RIT + Microsoft Research)** — estudio académico independiente, muestra mayor (155), confirma scope y gestión de proceso como fallos dominantes. NO VERIFICADO en esta sesión (paper de acceso cerrado): sus porcentajes exactos no se citan en este archivo por esa razón.
- **"'Slay the Spire': Metrics Driven Design and Balance" — Anthony Giovannetti (GDC 2019)** — Early Access con updates semanales, Discord y servidor de métricas; 1M+ copias en el primer año; advertencia sobre métricas mal interpretadas.
- **"Darkest Dungeon: A Design Postmortem" — Tyler Sigman & Chris Bourassa (GDC 2016) + cobertura Kotaku del Early Access** — el caso corpses/heart attacks: perseverar contra la minoría vocal cuando la feature sirve a la visión, y desactivar el conflicto con un toggle.
- **The Art of Game Design (cap. de playtesting) — Jesse Schell** — las seis preguntas del playtest (por qué/quién/cuándo/dónde/qué/cómo) y evaluar sin interrumpir la experiencia.
- **"Why You Only Need to Test with 5 Users" — Jakob Nielsen (NN/g) + Games User Research** — la regla de 5 usuarios ≈ 85% de problemas de usabilidad, y sus límites en juegos (9–18 para problemas raros, 20–40 para cuantitativo).
- **"Juice it or Lose it" — Martin Jonasson & Petri Purho (GDC Europe 2012)** — juice (máximo output por input, placer); tuning → juicing → streamlining; advertencia de no usar juice como sustituto de diseño. El término "oil" (fricción de input) usado en este archivo es síntesis operativa — NO VERIFICADO como artículo/charla independiente con ese nombre.
- **"How to Survive in Gamedev for Eleven Years Without a Hit" — Jake Birkett (GDC 2016)** — supervivencia sin hit: portafolio, un género iterado, muchas tiendas, ingresos paralelos, redefinir éxito.
- **Blood, Sweat, and Pixels — Jason Schreier (2017) + Game Developer sobre Eric Barone** — el caso Stardew Valley: ~70h/semana × 4.5 años en solitario, burnout post-éxito, parches que creaban tantos problemas como resolvían; y el patrón general de que todo juego se shippea en crisis.

Relacionados: [ver: preproduccion] (qué pasa antes del first playable), [ver: game-feel] (el detalle del juice), [ver: historia-lecciones] (más casos históricos), [ver: ux-ui-onboarding] (el pase de onboarding), [ver: psicologia-retencion-negocio] (post-launch y comunidad).
