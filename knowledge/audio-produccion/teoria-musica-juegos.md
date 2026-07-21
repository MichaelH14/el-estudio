# Teoría musical para juegos

> **Cuando cargar este archivo:** cuando haya que COMPONER música de un juego desde cero sin formación musical — elegir escala/modo por la emoción, armar una progresión de acordes que funcione, escribir una melodía o un tema (leitmotiv), fijar tempo/compás por la energía, o decidir la paleta de instrumentos para un mood. Es la teoría MÍNIMA y OPERATIVA para producir notas correctas, no un curso de solfeo. Las funciones de la música y la adaptividad están en [ver: gamedev/audio]; de dónde SALE la música (componer/licenciar/IA/contratar) y las herramientas en [ver: crear-musica] y [ver: herramientas-recursos-audio]; producir stems/mezcla en [ver: produccion-musical] y [ver: direccion-audio-mezcla]; el sistema adaptativo en [ver: musica-adaptativa]; renderizar teoría a audio por comando en [ver: hacer-audio-por-codigo]; implementar en el motor en [ver: unity/audio-unity].

Este archivo NO repite qué hace la música ni cómo se estructura la adaptividad (eso es [ver: gamedev/audio]) ni las rutas para conseguirla (eso es [ver: crear-musica]). Aquí está el **cómo suena "bien" y por qué**: la regla que deja que un agente sin oído entrenado escriba música usable eligiendo escala + progresión + tempo + timbre por la emoción del momento. Con teoría mínima y reglas probadas, es muy difícil sonar "mal".

## 1. Lo mínimo: notas, semitonos, octavas, piano roll

- **12 notas** por octava, se repiten: `C  C#  D  D#  E  F  F#  G  G#  A  A#  B` → y vuelve a C una octava arriba. (En español Do Re Mi Fa Sol La Si; se trabaja en cifrado inglés C–B porque es el estándar de DAWs/trackers.)
- **Semitono** = el paso más chico (una tecla a la siguiente, blanca o negra). **Tono** = 2 semitonos. Todo se construye con estos dos ladrillos.
- **Octava** = misma nota, el doble de frecuencia. En un piano roll, la misma nota una fila 12 pasos arriba.
- **Piano roll** (la reja de todo DAW/tracker): eje **X = tiempo**, eje **Y = altura** (pitch). Cada nota es un rectángulo: más arriba = más agudo, más largo = dura más. Un agente compone **colocando rectángulos en la reja** — no hace falta tocar un instrumento. La velocidad (velocity) del rectángulo = qué tan fuerte suena.
- **MIDI note number**: cada nota es un entero. **Do central = C4 = MIDI 60**; **A4 = MIDI 69 = 440 Hz**. +1 = un semitono arriba; +12 = una octava. Fórmula de frecuencia: `f = 440 × 2^((n−69)/12)`.
- ⚠️ **Gotcha del "Do central"**: unos programas llaman C4 al MIDI 60 (Yamaha/estándar científico), otros C3 (algunos DAWs). El MIDI 60 no cambia; la ETIQUETA sí. Si algo suena una octava arriba/abajo de lo esperado, es esto.

### Intervalos: la distancia manda el sentimiento

El "color" de dos notas juntas depende de cuántos semitonos hay entre ellas. Esta es la tabla que convierte teoría en emoción:

| Semitonos | Intervalo | Sensación (convención de scoring) |
|---|---|---|
| 0 | unísono | igual |
| 1 | 2ª menor | choque, terror, acecho (el motivo de *Jaws*/*Tiburón*) |
| 2 | 2ª mayor | paso de escala, neutro, movimiento |
| 3 | 3ª menor | **triste** (define acorde menor) |
| 4 | 3ª mayor | **alegre** (define acorde mayor) |
| 5 | 4ª justa | abierto, suspensión, heroico |
| 6 | tritono | inestable, malvado, *diabolus in musica* — tensión pura |
| 7 | 5ª justa | fuerte, vacío, PODER (el power-chord del metal) |
| 8 | 6ª menor | melancolía, anhelo |
| 9 | 6ª mayor | dulce, esperanza |
| 10 | 7ª menor | bluesy, tensión suave (acordes de 7ª) |
| 11 | 7ª mayor | tensión brillante, jazzy, "flotante" |
| 12 | octava | misma nota, amplitud |

Regla operativa: 3ª mayor (4 semitonos) = feliz; 3ª menor (3) = triste; 5ª justa (7) = poder sin emoción; tritono (6) y 2ª menor (1) = peligro. Un motivo de villano casi siempre esconde un tritono o una 2ª menor.

## 2. Escalas y modos: elegir por el mood

Una **escala** es el subconjunto de notas con las que se compone una pieza. Elegirla PRIMERO es el atajo más grande: si todas las notas salen de la misma escala, es casi imposible tocar una "nota mala". Patrón en tonos (W=2 semitonos) y semitonos (H=1), desde la tónica:

| Escala / modo | Patrón (T=2, S=1) | Familia | Mood típico en juegos |
|---|---|---|---|
| **Mayor** (Ionian) | T T S T T T S | mayor | Alegre, luminoso, pueblo acogedor, victoria |
| **Menor natural** (Aeolian) | T S T T S T T | menor | Triste, serio, tensión, noche, pérdida |
| **Dórico** | T S T T T S T | menor(-ish) | Menor pero "esperanzado"/épico; celta, aventura noble |
| **Frigio** | S T T T S T T | menor | Exótico, oscuro, español/flamenco, amenaza (2ª menor de arranque) |
| **Lidio** | T T T S T T S | mayor | Brillante, etéreo, asombro, "magia" (4ª aumentada) |
| **Mixolidio** | T T S T T S T | mayor(-ish) | Folk, rock, aventura desenfadada (7ª menor, "bluesy") |
| **Locrio** | S T T S T T T | disminuido | Inestable, sin hogar; raro, solo para horror/caos |
| **Menor armónica** | T S T T S (T+S) S | menor | Medio-Oriente, villano dramático, ópera oscura (salto de 3 semitonos) |
| **Pentatónica mayor** | grados 1 2 3 5 6 | — | **Segura**: sin choques, folk, oriental, alegre-ingenuo |
| **Pentatónica menor** | grados 1 ♭3 4 5 ♭7 | — | Segura y melancólica; blues, rock, lamento |
| **Tonos enteros** | T T T T T T (6 notas) | simétrica | **Onírico**, flotante, sueño, ingravidez (Debussy) |
| **Cromática** | S×12 (las 12 notas) | — | Tensión, caos, deslizar, terror; en dosis, no como base |

Notas de honestidad y fuente:
- Los patrones (T/S) son teoría estándar verificada (Wikipedia *Mode (music)*). Los **moods** son la convención de scoring film/game, no una ley: sirven de punto de partida, se ajustan a oído.
- **Mayor vs menor** es el 80% de la decisión: la única diferencia entre C mayor y A menor son las MISMAS 7 notas (todas blancas del piano) empezando en distinta tónica — misma paleta, sentimiento opuesto. Para un agente sin formación: **C mayor** (alegre) y **A menor** (triste) no tienen sostenidos ni bemoles → las más fáciles de escribir en el piano roll.
- **Pentatónica = la red de seguridad**: sin semitonos chocantes, "es imposible cometer un error armónico real" (Wikipedia *Pentatonic scale*). Para improvisar una melodía encima de cualquier acorde de la tonalidad, la pentatónica casi nunca falla. C mayor pentatónica = C D E G A.
- **Tonos enteros** = todo a distancia de tono, sin centro tonal ni sensible → "efecto borroso, ninguna nota destaca"; Debussy la usó para lo onírico/impresionista (Wikipedia *Whole tone scale*). Ideal para secuencias de sueño, mareo, portal. Todos sus acordes son aumentados.

## 3. Melodía: motivo, contorno, tensión y el tema del juego

La melodía es la línea que se tararea. No hace falta inspiración divina: se construye.

- **Motivo** = idea de **2–4 compases**, el ADN de la pieza (las 4 notas de la 5ª de Beethoven; el tema de *Zelda*). Regla de oro: **enunciar → repetir → variar → volver**. Se establece el motivo, se repite (reconocimiento), se varía (interés) y se vuelve (cierre). Estructura de frase típica **AABA**.
- **Contorno** = la FORMA de la línea, más importante que las notas exactas:
  - Ascendente = tensión que crece, esperanza, pregunta.
  - Descendente = relajación, tristeza, respuesta, caída.
  - Arco (sube y baja) = frase completa y satisfactoria.
- **Notas fuertes vs de paso**: en los tiempos fuertes (el "1" de cada compás), aterrizar en **notas del acorde** que suena debajo (tónica/3ª/5ª). Entre medias, notas de la escala como paso. Así la melodía "encaja" con la armonía sin pensarlo.
- **Tensión y resolución** = el motor de toda música:
  - La **7ª nota de la escala (sensible)** "quiere" subir a la tónica; el 4º grado "quiere" bajar al 3º. Dejar esas notas sin resolver = suspenso.
  - Terminar una frase en nota **estable** (1, 3, 5) = descanso. Terminar en **inestable** (2, 4, 6, 7) = "sigue, no terminó". Se usan a propósito: el loop no debe cerrar del todo (ver §7).
- **Tema pegadizo / leitmotiv del juego**: UN tema memorable = la identidad musical del juego (fuente: Wikipedia *Leitmotif* — frase recurrente asociada a personaje/lugar/idea; Wagner, *Star Wars*, *Undertale*). Se **reusa transformado**: en mayor cuando el héroe gana, en menor cuando pierde, lento en el menú, rápido y con brass en el jefe. Es la herramienta narrativa más barata y potente del score [ver: gamedev/narrativa-guion; identidad sonora en gamedev/audio]. Componer PRIMERO el leitmotiv de 4–8 compases y derivar el resto.

## 4. Armonía: acordes y progresiones que funcionan

Un **acorde** = 3+ notas sonando juntas. La **tríada** (3 notas) es la base. Se construye apilando 3as desde una raíz:

| Acorde | Fórmula (semitonos desde raíz) | Ejemplo (raíz C) | Sensación |
|---|---|---|---|
| **Mayor** | 0 – 4 – 7 | C E G | alegre, estable |
| **Menor** | 0 – 3 – 7 | C E♭ G | triste, estable |
| **Disminuido** | 0 – 3 – 6 | C E♭ G♭ | tenso, inestable (tritono) |
| **Aumentado** | 0 – 4 – 8 | C E G♯ | irreal, flotante, onírico |
| **7ª de dominante** | 0 – 4 – 7 – 10 | C E G B♭ | bluesy, "quiere resolver" |
| **7ª mayor** | 0 – 4 – 7 – 11 | C E G B | dulce, jazzy, soñador |
| **7ª menor** | 0 – 3 – 7 – 10 | C E♭ G B♭ | mélancólico, suave, lounge |

### Los acordes de una tonalidad (no hay que memorizar)

Cada escala mayor da 7 acordes fijos por grado. En números romanos (mayúscula=mayor, minúscula=menor, °=disminuido):

- **Tonalidad mayor** (grados I ii iii IV V vi vii°) — en **C mayor**: `C  Dm  Em  F  G  Am  B°`
- **Tonalidad menor** (i ii° III iv v VI VII) — en **A menor**: `Am  B°  C  Dm  Em  F  G`

C mayor y A menor comparten EXACTAMENTE los mismos 7 acordes (son relativos). Elegir uno de estos acordes = garantía de que "pega" con la escala.

### Progresiones probadas (copiar y usar)

Encadenar acordes es la armonía. Estas están verificadas y aparecen en miles de piezas; usarlas es la forma más rápida de sonar bien:

| Progresión | Grados | En C mayor / A menor | Carácter | Uso en el juego |
|---|---|---|---|---|
| **Tres acordes** | I–IV–V | C–F–G | resuelto, base de todo | casi cualquier cosa alegre/folk |
| **Pop / "axis"** | I–V–vi–IV | C–G–Am–F | alegre-agridulce, PEGAJOSO | menú, pueblo, mundo abierto |
| **Sensible / emotivo** | vi–IV–I–V | Am–F–C–G | emotivo, esperanza-con-nostalgia | cinemática, momento emocional |
| **50s / nostalgia** | I–vi–IV–V | C–Am–F–G | inocente, retro, doo-wop | recuerdo, créditos, título |
| **Cadencia jazz** | ii–V–I | Dm–G–C | resolución fuerte, sofisticada | cierre, lounge, puzzle resuelto |
| **Épico menor** | i–VI–III–VII | Am–F–C–G | épico, "en marcha", heroico | combate heroico, jefe, montaje |
| **Andaluza / español** | i–VII–VI–V | Am–G–F–E | flamenco, exótico, tenso | desierto, villano, duelo |
| **Vamp menor** | i–VII (loop 2 acordes) | Am–G | motor, hipnótico, driving | sci-fi, persecución, sigilo |
| **Lamento** | i–iv–i (línea descendente) | Am–Dm–Am | doliente | muerte, derrota, tragedia |

Fuente verificada: la I–V–vi–IV (C–G–Am–F) y su rotación "sensible" vi–IV–I–V (Am–F–C–G) y la 50s I–vi–IV–V están documentadas (Wikipedia *I–V–vi–IV progression*); la "épica" i–VI–III–VII usa los mismos 4 acordes en tonalidad menor. La Andaluza es la cadencia frigia clásica del sonido español.

### Cadencias: cómo abrir y cerrar la tensión

| Cadencia | Movimiento | Efecto |
|---|---|---|
| **Auténtica** | V → I | resolución fuerte, "punto final" |
| **Plagal** | IV → I | resolución suave, "amén", cálida |
| **Semicadencia** | … → V | queda EN suspenso (no cierra) → suspense, pregunta |
| **Rota/engañosa** | V → vi | sorpresa: prometía cierre y sigue → mantiene la tensión |

Para el LOOP de un juego (§7): **evitar la cadencia auténtica V→I en la costura** — cerrar del todo suena a "fin", el jugador nota el reinicio. Usar semicadencia o rota para que el bucle "tire" hacia arriba.

## 5. Ritmo y tempo: energía por BPM y compás

- **BPM** (beats per minute) = velocidad = energía percibida. Términos italianos estándar y su rango (verificado, Wikipedia *Tempo*): Largo 40–66, Adagio 44–66, Andante 56–108, Moderato 108–120, Allegro 120–156, Vivace 156–176, Presto 168–200. Traducido a **contexto de juego** (convención, ajustar a oído):

| Contexto | BPM | Término |
|---|---|---|
| Menú, ambiente, exploración calma | 60–90 | Largo–Andante |
| Pueblo, hub neutral, diálogo | 90–120 | Andante–Moderato |
| Acción, combate estándar | 120–160 | Allegro–Vivace |
| Persecución, jefe frenético, oleada final | 160–200+ | Presto |

- **Compás** = cómo se agrupan los pulsos. El de arriba es cuántos pulsos por compás; el de abajo, la figura que vale un pulso:

| Compás | Sensación | Uso típico |
|---|---|---|
| **4/4** (común) | recto, estable, "default" | 90% de la música de juego: pop, rock, marcha, acción |
| **3/4** (vals) | girando, elegante, whimsical | pueblo pintoresco, caja de música, escena romántica |
| **6/8** (compuesto) | balanceo, galope, rodante | aventura, náutico, celta, cabalgata heroica |
| **2/4** | marcha corta, rápido | arcade, plataformas veloces, chiptune |
| **5/4 · 7/8** (impar) | inestable, inquietante, "cojea" | jefe raro, alien, tensión psicológica |

- **Groove** = la sensación del ritmo, no solo la velocidad. Trucos baratos: acentuar el 2 y el 4 (backbeat) da empuje; **swing** (la 2ª corchea de cada par llega un poco tarde) humaniza y da jazz/shuffle; síncopa (acentos fuera del pulso) da funk/energía. Un patrón de batería estable en 4/4 (bombo en 1 y 3, caja en 2 y 4, hi-hats en corcheas) es el suelo seguro sobre el que todo lo demás encaja.

## 6. Instrumentación y timbre: la paleta del juego

El MISMO conjunto de notas cambia de emoción entero según con qué se toque. La paleta tímbrica ES la mitad de la identidad [ver: gamedev/audio, identidad de marca]. Convención de scoring (ajustar al arte del juego):

| Timbre / instrumento | Evoca | Género/mood |
|---|---|---|
| **Chiptune** (square+triangle+noise) | retro, 8/16-bit, arcade, juguetón | plataformas, roguelike retro [ver: chiptune-trackers] |
| **Piano solo** | íntimo, emocional, melancólico | menú, momento narrativo, indie triste |
| **Orquesta completa** (cuerdas+brass+timpani+coro) | épico, heroico, cinematográfico | fantasía, AAA, jefe, gesta |
| **Cuerdas sostenidas** | emoción, calidez; tremolo = tensión | drama, suspenso, romance |
| **Brass** (trompas, trombones) | heroísmo, fanfarria, poder, peligro | victoria, ejército, villano imponente |
| **Maderas** (flauta, oboe, clarinete) | pastoral, whimsical, misterio | bosque, pueblo, folk, hada |
| **Synths analógicos** (pads, arps, sub-bass) | sci-fi, cyberpunk, sueño, electrónico | espacio, futuro, neón, terror sintético |
| **Guitarra distorsionada** | energía, agresión, poder | acción, metal (lección DOOM), jefe |
| **Guitarra acústica / fiddle / acordeón** | folk, hogar, campamento, europeo | aventura ligera, taberna, oeste |
| **Percusión tribal / taiko** | ritual, guerra, empuje | combate, cacería, tensión primal |
| **Arpa · celesta · glockenspiel · campanas** | magia, chispa, sueño, infancia | cofre, hechizo, cielo, recuerdo |
| **Coro** | sacro, épico; grave = ominoso, agudo = etéreo | catedral, apocalipsis, portal |
| **Étnicos**: koto/shakuhachi/erhu (Asia), oud/duduk (M.Oriente), gaita/tin whistle (celta) | lugar concreto | zona cultural específica |

Reglas de paleta: (1) elegir 3–5 instrumentos que DEFINAN el juego y ser consistente — demasiados timbres = ningún carácter. (2) El **registro** importa tanto como el instrumento: un cello grave = luto; el mismo cello agudo = tensión. (3) Contraste por zona: cambiar la paleta (no solo la melodía) para que cada bioma suene distinto. Cómo sintetizar/producir estos timbres sin librerías caras: [ver: sintesis-y-diseno-sonido] y [ver: produccion-musical].

## 7. Estructura de una pista de juego: intro + loop, no verso-coro

Una canción pop tiene un ARCO que termina (intro–verso–coro–puente–coro–outro). Una pista de juego debe **repetirse para siempre sin cansar ni delatar la costura**. Es otro oficio:

- **Estructura base**: `intro (suena 1 vez) → cuerpo loopeable (repite ∞)`. Opcional `A–B–A–C` para variar dentro del loop y estirar el tiempo antes de que el oído reconozca la repetición.
- **Duración del loop**: apuntar a **60 s+** de material antes de repetir; un loop de 15 s cansa en minutos [ver: gamedev/audio; corte del loop en audio-a-juego].
- **No poner el clímax en el loop base**: un pico dramático que suena cada 30 s se vuelve chiste. Reservar la intensidad para las **capas** del sistema adaptativo (percusión/melodía que entran) — el loop base debe poder sonar 20 minutos de fondo [ver: musica-adaptativa; vertical layering en gamedev/audio].
- **La costura no debe "resolver a casa"**: evitar cadencia auténtica y silencio antes del reinicio; usar semicadencia/vamp para que el final empalme con el inicio con movimiento hacia adelante (§4). El bucle "gira", no "empieza y para".
- **Componer para adaptividad ANTES de escribir**: si el juego usa capas/secciones, se compone en **stems alineados** e **intro+loop** desde el minuto cero, no se trocea después [ver: crear-musica, produccion-musical].

## 8. Componer para el MOOD: la tabla maestra

El flujo de un agente que dirige el audio: nombrar la emoción del momento → leer la fila → escribir. Todo lo anterior condensado:

| Emoción / escena | Escala | BPM | Compás | Progresión | Paleta |
|---|---|---|---|---|---|
| **Alegre / pueblo** | Mayor | 100–130 | 4/4 o 3/4 | I–V–vi–IV · I–IV–V | piano, cuerdas ligeras, glockenspiel, maderas |
| **Triste / pérdida** | Menor natural | 60–85 | 4/4 o 3/4 | i–iv–i · vi–IV–I–V | piano solo, cello, violín, pads |
| **Épico / heroico** | Menor o Dórico | 120–150 | 4/4 (o 6/8 galope) | i–VI–III–VII | orquesta, brass, timpani/taiko, coro |
| **Tenso / jefe / peligro** | Menor · cromática · Frigio | 140–180 | 4/4, 5/4, 7/8 | pedal + tritono/disonancia | cuerdas tremolo/staccato, percusión, brass grave |
| **Exótico / desierto / oriental** | Frigio · menor armónica · pentatónica | 90–130 | 4/4 o 6/8 | Andaluza i–VII–VI–V · drone | oud, duduk, koto, flauta, percusión de mano |
| **Onírico / misterio / etéreo** | Tonos enteros · Lidio | 60–90 | libre o 3/4 | acordes aumentados, sin cadencia | pads, celesta, arpa, coro etéreo, campanas |
| **Retro / arcade / juguetón** | Mayor · pentatónica mayor | 120–160 | 4/4 o 2/4 | I–IV–V · I–V–vi–IV | chiptune (square+triangle+noise) |
| **Sci-fi / cyberpunk** | Menor · Dórico · cromática | 100–140 | 4/4 | vamp i–VII · pedal | synths, arps, sub-bass, pads |
| **Folk / aventura ligera** | Mayor · Mixolidio | 100–140 | 6/8 o 4/4 | I–IV–V · I–♭VII–IV (Mixo) | guitarra acústica, fiddle, flauta, acordeón |
| **Calma / menú / exploración** | Mayor · pentatónica · Lidio | 60–90 | 4/4 o libre | I–IV lento · pedal | piano, pads, arpa, guitarra suave |

## 9. Escribir con teoría mínima (receta para agente sin oído)

El método que hace "difícil sonar mal":

1. **Elegir tonalidad fácil**: **C mayor** (alegre) o **A menor** (triste) → sin sostenidos/bemoles, solo teclas blancas en el piano roll.
2. **Elegir escala por el mood** (§2/§8). Todas las notas de la melodía salen de ahí → cero notas "malas".
3. **Poner una progresión probada** (§4) en loop, 1 acorde por compás, 2–4 compases. Es el suelo armónico.
4. **Escribir la melodía**: en los tiempos fuertes, notas del acorde de ese compás; entre medias, notas de la escala. Contorno con forma (arco/ascendente).
5. **Motivo de 2–4 compases**, repetir y variar (§3). Ese motivo = candidato a leitmotiv del juego.
6. **Ritmo/batería** estable en 4/4 debajo (§5) da groove sin esfuerzo.
7. **Dejar que las reglas ayuden**: quedarse en una escala y una progresión es una red de seguridad, no una jaula. La creatividad va en la melodía y el timbre, no en romper la armonía.

### Verificar la teoría por código (comandos REALES)

Para OÍR una escala/acorde/progresión sin DAW, un agente puede renderizarla por comando. Stack genérico: instalar `sox` y `fluidsynth` por brew; un soundfont General MIDI (p.ej. FluidR3_GM) en la ruta estándar de soundfonts. Pipeline completo en [ver: hacer-audio-por-codigo]. Referencia de notas para SoX (notación `%n`, relativa a **A4 = %0 = 440 Hz**, cada paso = 1 semitono):

| Nota | MIDI | Hz | SoX `%n` |
|---|---|---|---|
| C4 (Do central) | 60 | 261.6 | `%-9` |
| D4 | 62 | 293.7 | `%-7` |
| E4 | 64 | 329.6 | `%-5` |
| F4 | 65 | 349.2 | `%-4` |
| G4 | 67 | 392.0 | `%-2` |
| A4 | 69 | 440.0 | `%0` |
| B4 | 71 | 493.9 | `%2` |
| C5 | 72 | 523.3 | `%3` |

Comandos verificados (sintaxis del man de SoX y FluidSynth):

```bash
# Una nota (La 440, sine, 1 s):
sox -n a4.wav synth 1 sine %0

# Un acorde de Do mayor (C4 E4 G4 = %-9 %-5 %-2): varios osciladores en UN synth = acorde
# ⚠️ sin -c1, SoX escribe UN CANAL POR OSCILADOR (aquí saldría un .wav de 3 canales, no un acorde mezclado): forzar -c1 (o -c2) para que se mezcle a un solo canal, verificado con `soxi`
sox -n -c1 c_major.wav synth 2 pluck %-9 pluck %-5 pluck %-2 fade h 0.02 2 0.1 reverb

# Transponer una grabación 2 semitonos arriba (pitch en cents; 200 cents = 2 semitonos):
sox in.wav out.wav pitch 200

# Renderizar una melodía/progresión compuesta como .mid con un soundfont GM:
fluidsynth -ni -F song.wav -T wav -r 44100 /ruta/soundfonts/FluidR3_GM.sf2 song.mid
```

- `synth [dur] {tipo freq}`: tipos `sine square triangle sawtooth trapezium pluck whitenoise pinknoise brownnoise`; varios pares apilados en un mismo `synth` suenan a la vez = acorde (patrón del propio man: `synth sin %-12 sin %-9 sin %-5 sin %-2` = un acorde) **pero cada oscilador escribe su PROPIO canal si no se fuerza `-c1`/`-c2`** — el ejemplo oficial del man va con `-c1` (`sox -n -c1 out.wav synth ...`); sin eso, SoX escribe un `.wav` multicanal (uno por nota), no un acorde mezclado (verificado con `soxi`: sin `-c1` da 3 canales para 3 osciladores). Para SECUENCIAR notas (melodía), se generan por separado y se concatenan, o se escribe un `.mid` y se renderiza con FluidSynth. El `.mid` se arma con una librería MIDI mínima escribiendo los MIDI numbers de la tabla → receta en [ver: hacer-audio-por-codigo].
- FluidSynth: `-n` sin MIDI-in, `-i` sin shell, `-F` render a archivo, `-T wav` tipo, `-r` sample rate, `-g` gain (0<g<10, default 0.2). Rápido y sin tiempo real.

## Reglas prácticas

- [ ] Elegir **tonalidad + escala ANTES** de escribir una nota; para sin-formación, C mayor (alegre) o A menor (triste): solo teclas blancas, cero notas malas.
- [ ] Emoción del momento → leer la fila de la **tabla maestra §8** (escala + BPM + compás + progresión + paleta) y componer desde ahí, no de la inspiración en blanco.
- [ ] Mayor = alegre, menor = triste: es el 80% de la decisión emocional. Modos y pentatónica para matizar.
- [ ] Usar una **progresión probada** (§4) en loop; 1 acorde por compás. No inventar armonía si no hace falta.
- [ ] Melodía: notas del **acorde** en tiempos fuertes, notas de la **escala** entre medias; darle **contorno** (arco/ascendente), no notas planas.
- [ ] Componer un **motivo de 2–4 compases**, repetirlo y variarlo (enunciar–repetir–variar–volver). Un motivo memorable = leitmotiv del juego, reusable transformado.
- [ ] Tempo por energía: 60–90 calma, 90–120 neutral, 120–160 acción, 160+ frenético.
- [ ] Compás 4/4 por defecto; 3/4 para vals/whimsical, 6/8 para aventura/galope, impares (5/4·7/8) solo para inquietud deliberada.
- [ ] Paleta de **3–5 instrumentos** que definan el juego; cambiarla por zona; cuidar el **registro** (grave vs agudo cambia la emoción del mismo instrumento).
- [ ] Estructura **intro (1 vez) + loop (∞)**, no verso-coro; loop de 60 s+; el clímax va en las capas adaptativas, no en el loop base [ver: musica-adaptativa].
- [ ] La **costura del loop NO resuelve a casa**: evitar cadencia auténtica/silencio antes del reinicio; usar semicadencia o vamp para que empalme con movimiento.
- [ ] Tensión y resolución conscientes: dejar la sensible (7º grado) o el tritono sin resolver = suspenso; aterrizar en 1/3/5 = descanso.
- [ ] Si el juego usa adaptividad, componer en **stems + intro/loop desde el inicio** [ver: crear-musica].
- [ ] **Verificar por oído**: renderizar la escala/acorde/progresión con SoX o FluidSynth (comandos §9) antes de darla por buena. Output vacío ≠ correcto.
- [ ] Licencias: teoría (escalas, progresiones, cadencias) NO es copyrightable — una progresión I–V–vi–IV es libre. Lo que se protege es la GRABACIÓN/arreglo concreto y los SAMPLES/soundfonts usados. Registrar la licencia de cada soundfont/sample [ver: herramientas-recursos-audio].

## Errores comunes

| Error | Antídoto |
|---|---|
| Componer "a lo que salga" sin elegir tonalidad → notas que chocan | Fijar escala primero; todo sale de ahí (C mayor / A menor para empezar) |
| Mezclar notas de dos tonalidades sin querer | Quedarse en una escala; si se cambia, es una modulación DELIBERADA con puente |
| Loop que "termina" (cadencia V→I + silencio) → el reinicio se nota | Cerrar en semicadencia/vamp; la costura empalma con movimiento hacia adelante |
| Loop de 15–20 s → cansa en minutos | 60 s+ de material; variar con A–B–A–C; reservar el pico para capas |
| Clímax dramático dentro del loop base → chiste tras 3 vueltas | El loop base es "de fondo"; la intensidad la aportan los stems adaptativos |
| Melodía plana, sin dirección | Darle contorno (arco/ascendente/descendente); notas de acorde en tiempos fuertes |
| Progresión al azar que suena "rara" | Copiar una progresión probada (§4); son libres y funcionan |
| Demasiados instrumentos → ningún carácter | Paleta de 3–5 que definan el juego; consistencia > variedad |
| Modo equivocado para el mood (mayor épico y sale infantil) | Épico/heroico = menor o Dórico + brass/timpani; mayor puro tiende a alegre/naif |
| Tritono o 2ª menor accidental en música "feliz" | Revisar intervalos; esos son de peligro/villano, no de pueblo alegre |
| Confundir C4 con la etiqueta del DAW (todo suena una octava fuera) | MIDI 60 = Do central fijo; ojo con programas que lo llaman C3 |
| Loop en MP3 → hueco audible cada vuelta | Nunca MP3 en loops; OGG/WAV, cortar en el ataque [ver: audio-a-juego] |
| Acorde con `sox synth` sin `-c1` → sale un .wav de N canales (uno por nota), no un acorde mezclado | Forzar `-c1` (mono) o `-c2` en el comando; verificar canales con `soxi archivo.wav` antes de dar por bueno |
| Creer que "usar una progresión famosa" infringe copyright | La progresión/escala/cadencia es libre; se protege la grabación y los samples, no la teoría |

## Fuentes

- **Mode (music)** — Wikipedia — los 7 modos diatónicos (Ionian…Locrian), su patrón de tonos/semitonos y su carácter (bright/dark, "serious", "inciting anger", "tearful"); mayor-like vs minor-like. Base de la §2.
- **I–V–vi–IV progression** — Wikipedia — la progresión pop en C mayor (C–G–Am–F), su rotación "sensitive female" vi–IV–I–V (Am–F–C–G) y la '50s I–vi–IV–V; verificación de la §4.
- **Pentatonic scale** — Wikipedia — pentatónica mayor = grados 1 2 3 5 6 (C D E G A), sin semitonos = "imposible el error armónico real", asociación folk/Asia oriental.
- **Whole tone scale** — Wikipedia — 6 notas a tono (C D E F♯ G♯ A♯), sin centro tonal ni sensible, "efecto borroso", uso onírico/impresionista de Debussy (*Voiles*) y para secuencias de sueño.
- **Tempo** — Wikipedia — términos italianos y sus rangos de BPM (Largo 40–66 … Presto 168–200) que anclan la tabla de energía de la §5.
- **Leitmotif** — Wikipedia — frase musical recurrente ligada a personaje/lugar/idea (Wagner; *Star Wars*, *Jaws*, *Undertale*), repetición y transformación como recurso narrativo. Base del leitmotiv del juego (§3).
- **SoX — synth / pitch effects** (man page, man.archlinux.org/man/sox.1 y sourceforge) — sintaxis `synth [len] {type freq}`, formas de onda, notación de nota `%0` = A4 = 440 Hz con offsets en semitonos, `pitch` en cents; comandos reales de la §9 verificados.
- **FluidSynth** (man page, man.archlinux.org/man/fluidsynth.1 + UsageGuide) — flags `-n -i -F -T -r -g` para render rápido de un `.mid` con soundfont a WAV; comando de la §9 verificado.
- Cross-ref de teoría de funciones/adaptividad/silencio: [ver: gamedev/audio]; rutas y herramientas para conseguir la música: [ver: crear-musica], [ver: herramientas-recursos-audio].

> **Honestidad:** los patrones de escala, las fórmulas de acorde y los rangos de BPM son teoría estándar verificada contra las fuentes citadas. Los **moods** por escala/modo/instrumento son la convención de scoring film/game (no una ley física): punto de partida sólido, se ajustan a oído y al arte del juego. Los comandos de SoX/FluidSynth están verificados contra sus man pages; las rutas de soundfont son genéricas (configurar la real del entorno).
