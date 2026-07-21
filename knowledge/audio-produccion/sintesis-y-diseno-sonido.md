# Síntesis y diseño de sonido desde cero

> **Cuando cargar este archivo:** cuando hay que FABRICAR un sonido desde primitivas por síntesis — no bajarlo ni grabarlo, sino construirlo con osciladores, envolventes, filtros y modulación — o cuando hay que analizar un sonido de referencia para recrearlo. Aquí va la teoría operativa de la síntesis (bloques, tipos, recetas por sonido de juego) y los comandos concretos para hacerlo por código. Las cuatro **vías** de conseguir SFX y el mapeo acción→preset de los generadores tipo sfxr están en [ver: crear-sfx]; el catálogo de herramientas/licencias en [ver: herramientas-recursos-audio]; el acabado/entrega del asset en [ver: audio-a-juego]; el *qué sonido poner y por qué* (funciones, prioridad, silencio) en [ver: gamedev/audio]; la implementación en Unity en [ver: unity/audio-unity]. El stack de síntesis por código a fondo (SuperCollider/Csound/SoX scripting) en [ver: hacer-audio-por-codigo]. Aquí: **cómo se piensa y se arma un sonido de la nada.**

Regla de encuadre: la síntesis es la vía de **máximo control y cero coste de licencia** — un sonido sintetizado es 100% tuyo, sin CC ni royalties ni entrenamiento-de-IA que auditar [ver: crear-sfx, licencias]. El precio es tiempo y criterio. Para SFX retro/UI, un generador sfxr resuelve en segundos [ver: crear-sfx]; para un sonido con identidad y que no exista en ninguna biblioteca, se sintetiza desde los bloques de abajo.

---

## Los cuatro bloques de toda síntesis

Cualquier synth — hardware, plugin o línea de comando — combina estos cuatro. Entenderlos es entender todo synth que toques después.

### 1. Oscilador y forma de onda (la materia prima = el timbre)

El oscilador genera una vibración periódica. Su **forma de onda** define el contenido armónico, y el contenido armónico ES el timbre (brillante/opaco, hueco/lleno). Hechos de Fourier, no opinión:

| Onda | Armónicos | Suena | Uso típico en juego |
|---|---|---|---|
| **Sine** (senoidal) | Solo el fundamental, nada más | Puro, redondo, "flauta"/sub | Sub-boom de impactos, tono base de UI, la "cola" grave de una explosión, tono de test |
| **Sawtooth** (diente de sierra) | TODOS los armónicos (amplitud 1/n) | Brillante, áspero, lleno | Motores, láseres, brass, bajos agresivos, cuerdas sintéticas |
| **Square** (cuadrada) | Solo armónicos IMPARES (1/n) | Hueco, "clarinete"/8-bit, con cuerpo | Sonido chiptune, saltos retro, tonos de UI con carácter |
| **Triangle** (triangular) | Impares, pero 1/n² → caen rápido | Suave, casi-sine con un pelo de brillo | Bajos suaves, blips delicados, flautas |
| **Pulse/PWM** (cuadrada asimétrica) | Impares + pares según el ancho de pulso | Nasal, "vocal", cambia al modular el ancho | Leads con movimiento, texturas chiptune |
| **Noise** (ruido) | Todas las frecuencias a la vez, no periódico | Siseo/soplo, sin tono | Explosiones, viento, fuego, pasos, percusión, "aire" de un sonido |

Sabores de ruido (importan): **white** = energía plana por Hz (siseo agudo); **pink** = −3 dB/octava, más grave y natural (viento, lluvia, mar); **brown/red** = −6 dB/octava, retumbe grave (motor lejano, trueno). SoX genera los tres: `whitenoise`, `pinknoise`, `brownnoise`.

Truco mental: **más armónicos = más brillante**. Saw es el punto de partida de la síntesis sustractiva justo porque tiene TODO — luego el filtro quita lo que sobra.

### 2. Envolvente ADSR (la forma en el tiempo = la "vida" del sonido)

La envolvente controla cómo cambia un parámetro (normalmente el volumen) a lo largo del tiempo. **Es lo primero que el oído usa para reconocer un sonido** — un piano y una cuerda frotada pueden tener el mismo timbre estacionario, y los distingues solo por el ataque. Cuatro etapas:

| Etapa | Qué es | Corto → | Largo → |
|---|---|---|---|
| **Attack** | Tiempo de silencio a volumen pleno | Percusivo, "clic", golpe (impacto, disparo, blip) | Suave, "sopla hacia adentro" (pad, viento, arranque de motor) |
| **Decay** | Caída del pico al nivel de sustain | Golpe seco que baja rápido | Nota que resuena antes de asentar |
| **Sustain** | **Nivel** (no tiempo) que se mantiene mientras "la tecla está pulsada" | 0 = one-shot que muere (pluck, impacto) | Alto = tono sostenido (motor, drone, alarma) |
| **Release** | Cola tras soltar | Corte seco | Cola larga, reverbera al soltar |

Regla clave: **Sustain es un nivel, A/D/R son tiempos.** Un impacto de juego suele ser AD puro con sustain 0 (attack instantáneo, decay corto, sin sustain, sin release). Un drone de ambiente es A lento, sustain alto, R largo.

En SoX no hay "ADSR" con ese nombre: se aproxima con `fade [type] in stop out` (ataque = fade-in, cola = fade-out) y, para decay percusivo, con `fade t` (triangular/lineal) o encadenando envolventes. Para curva percusiva rápida: `fade h 0 <dur> <dur>` (fade-out de casi toda la duración, forma medio-seno).

### 3. Filtro (esculpir el timbre = quitar frecuencias)

El filtro es el cincel de la síntesis sustractiva: parte de una onda rica (saw/square/noise) y **quita** frecuencias.

| Tipo | Deja pasar | Para qué |
|---|---|---|
| **Low-pass (LP)** | Lo grave, corta lo agudo | El más usado: oscurecer, "alejar", quitar brillo. Filtro que se cierra = sonido que se apaga |
| **High-pass (HP)** | Lo agudo, corta lo grave | Quitar retumbe/barro, adelgazar, hacer "pequeño/lejano" |
| **Band-pass (BP)** | Solo una banda | Efecto "teléfono/radio", aislar una formante (viento, voz robótica) |
| **Notch/band-reject** | Todo menos una banda | Quitar una resonancia molesta, efectos de fase |

Dos parámetros que definen el carácter del filtro:
- **Cutoff (frecuencia de corte):** dónde empieza a cortar. **Modular el cutoff con una envolvente o LFO es el 80% del movimiento tímbrico** de la síntesis (el "wah", el filtro que se abre en un buildup, el bajo que "habla").
- **Resonance (Q):** realza un pico justo en el cutoff. Poca = natural; mucha = silbido/"vocal" y, al extremo, el filtro auto-oscila y se vuelve un oscilador sine. Resonancia alta + cutoff barrido = el sonido "láser/zap" clásico.
- **Slope (pendiente):** 12 dB/oct (2 polos, suave) vs 24 dB/oct (4 polos, el "Moog", más drástico). SoX: `-1` un polo, `-2` dos polos.

SoX: `lowpass [-1|-2] freq[k] [width]`, `highpass ...`, `bandpass freq width`. Para barridos de filtro sofisticados, un synth modular o código [ver: hacer-audio-por-codigo].

### 4. LFO y modulación (movimiento = vida)

Un **LFO** (Low Frequency Oscillator) es un oscilador tan lento (< 20 Hz) que no se oye como tono sino que **mueve otro parámetro**. Modulación = una fuente controla un destino. Los destinos clásicos:

| LFO modula → | Efecto | Ejemplo de juego |
|---|---|---|
| **Pitch** | Vibrato | Voz de personaje, alarma que ondula, magia "inestable" |
| **Amplitud** | Tremolo | Helicóptero, "pulso" de un power-up activo, latido |
| **Filtro (cutoff)** | Wah / auto-wah | Buildup, motor que "respira", agua |
| **Ancho de pulso (PWM)** | Movimiento tímbrico | Lead chiptune que "vibra" sin cambiar de nota |
| **Paneo** | Movimiento espacial | Objeto que rodea al jugador (mejor hacerlo en el motor, 3D) [ver: unity/audio-unity] |

Fuentes de modulación además del LFO: **envolventes** (un cambio de una sola vez, no cíclico — p.ej. envolvente→cutoff para el "pluck" de un bajo), y **velocity/parámetros de gameplay** (la fuerza del golpe → pitch+volumen; RPM del motor → pitch). Esto último es el puente a **RTPC** en middleware: el juego mapea una variable a un parámetro del synth en tiempo real [ver: gamedev/audio; middleware-fmod-wwise]. SoX: `tremolo speed depth` (LFO→amplitud), `bend` y `synth ... fmod` (modulación de frecuencia).

---

## Los tipos de síntesis: cuál para qué sonido

No hay "la buena". Cada método es bueno para una familia de timbres. Elegir por el sonido objetivo:

| Tipo | Cómo funciona | Fuerte en | SFX de juego típicos | Coste/dificultad |
|---|---|---|---|---|
| **Sustractiva** | Osc rico → filtro → amp+envolvente. La base histórica (Minimoog) | Todo lo "analógico": bajos, leads, motores, láseres, viento, pads | El caballo de batalla — empieza aquí | Baja, intuitiva |
| **FM (modulación de frecuencia)** | Un oscilador (modulador) modula la frecuencia de otro (portador); el **ratio** define el timbre | Metálicos, campanas, e-piano, glass, cristal, mordientes | Campanas de UI, pickups "brillantes", metal, robots | Media; poco intuitiva pero poderosa |
| **Aditiva** | Sumar muchas sines, cada una con su amplitud/envolvente | Órganos, timbres armónicos precisos, control total sobre cada parcial | Drones tonales, "coros" sintéticos | Alta (muchos parciales que gestionar) |
| **Wavetable** | Recorre una tabla de formas de onda de un ciclo; barrer la tabla = morphing tímbrico | Timbres en evolución, digital moderno, movimiento | Power-ups que "crecen", texturas sci-fi, buildups | Media (Vital/Serum lo hacen fácil) |
| **Granular** | Corta el audio en granos de 1–100 ms y los reordena/estira | Texturas, atmósferas, time-stretch extremo, "polvo" sonoro | Ambientes alienígenas, magia, transiciones, drones evolutivos | Media-alta; muy experimental |
| **Física (physical modeling)** | Simula el mecanismo real (cuerda, tubo, membrana). Karplus-Strong = ruido → delay + filtro en lazo | Cuerdas punteadas, percusión, instrumentos "reales" con variación natural | Arpa/cuerda, marimba, gotas, madera | Baja para plucks (SoX lo trae), alta para modelos complejos |

Reglas de decisión rápidas:
- **¿Metálico, campana, "ding" brillante?** → FM. Un portador + un modulador con **ratio no entero** (p.ej. 1 : 1.4) da inarmonicidad = metal/campana. **Ratio entero** (1 : 2, 1 : 3) = armónico, más "musical" (e-piano, brass).
- **¿Bajo, lead, motor, láser, viento?** → Sustractiva.
- **¿Cuerda punteada, gota, madera, percusión afinada?** → Física (Karplus-Strong). SoX: `synth <len> pluck <nota>`.
- **¿Textura, atmósfera, algo que "evoluciona" raro?** → Granular o wavetable.
- **¿Órgano, timbre armónico exacto?** → Aditiva.

FM en la práctica sin plugin: SoX cascada `synth ... sine <portadora> synth ... sine fmod <moduladora>` da una FM simple (un operador). Para FM real estilo DX7 (6 operadores, algoritmos) usar **Dexed** (gratis, emula el DX7) o un tracker con chips FM como **Furnace** (YM2612/OPL) [ver: chiptune-trackers]. FM auténtica de chip es la firma de la Sega Genesis.

---

## Cómo piensa un sound designer: descomponer para recrear

Un sonido reconocible = la suma de cuatro dimensiones. Para **recrear** un sonido de referencia (o inventar uno), se decide cada una por separado:

| Dimensión | Preguntas | Se controla con |
|---|---|---|
| **Pitch** | ¿Fijo? ¿Sube o baja? ¿Glissando rápido o lento? ¿Con vibrato? | Oscilador + sweep de frecuencia + LFO |
| **Envolvente** | ¿Percusivo (golpe seco) o sostenido? ¿Ataque instantáneo o suave? ¿Cola larga o corta? | ADSR / fades |
| **Timbre** | ¿Brillante o opaco? ¿Puro o áspero? ¿Hueco o lleno? ¿Metálico o cálido? | Forma de onda + filtro (cutoff/Q) + tipo de síntesis (FM=metal) |
| **Textura** | ¿Limpio o con "aire"/ruido? ¿Suave o distorsionado/sucio? | Capa de ruido + distorsión + saturación |

**Método para clonar una referencia** (misma lógica que analizar un sprite antes de dibujarlo [ver: arte-2d/pixel-art]):
1. Escúchala 5 veces y pon en palabras cada dimensión ("pitch baja rápido; ataque instantáneo; cola de 0.3 s; brillante-áspero; con un toque de ruido").
2. Identifica la **envolvente primero** (es lo que más define). ¿Es un one-shot percusivo o algo sostenido?
3. Elige el **oscilador** por el timbre (opaco→sine/triangle; áspero→saw; metálico→FM; ruidoso→noise).
4. Arma la **capa de tono** y la **capa de ruido** por separado, luego mézclalas (sección *Layering*, abajo).
5. Ajusta filtro y modulación hasta que "camine" como la referencia.
6. Contrasta A/B con la referencia a igual volumen. El oído se autoengaña con el volumen — iguala loudness antes de comparar.

---

## Recetas: diseñar sonidos de juego desde primitivas

Comandos **verificados** contra `man sox` del binario instalado (SoX 14.4.x) y ejecutados: producen WAV válido. `synth` genera a 0 dBFS → **seguir siempre con `gain -N`** para dejar headroom (regla del propio SoX) [ver: audio-a-juego]. Nota de sintaxis de barrido: `freq1-freq2` con `-`, `:`, `+` o `/` entre frecuencias hace un sweep (`:` lineal Hz/s, `/` exponencial semitonos/s, `-` exponencial "steppeado"). Frecuencia en Hz, en `%semitonos` desde A440, o notación científica (`C5`, `E2`).

| Sonido | Anatomía | Comando SoX de arranque |
|---|---|---|
| **Láser / disparo** | Barrido de pitch descendente + decay rápido + resonancia | `sox -n laser.wav synth 0.4 sine 1800-200 fade h 0 0.4 0.35 gain -3` |
| **Salto** | Envolpe de pitch ASCENDENTE, corto, onda con cuerpo (square) | `sox -n jump.wav synth 0.15 square 220-660 fade h 0 0.15 0.12 gain -6` |
| **Impacto / explosión** | Ruido burst + sine grave (boom) mezclados + decay + distorsión | `sox -n impact.wav synth 0.25 brownnoise synth 0.25 sine mix 90-50 fade h 0 0.25 0.22 overdrive 15 gain -3` |
| **Power-up / recompensa** | Arpegio ASCENDENTE (tonos en orden), tono limpio | tres tonos concatenados: `sox -n a.wav synth .07 pluck C5; sox -n b.wav synth .07 pluck E5; sox -n c.wav synth .07 pluck G5; sox -n d.wav synth .12 pluck C6; sox a.wav b.wav c.wav d.wav powerup.wav gain -3` |
| **UI blip / click** | Tono corto, envolvente rápida, el sonido más suave del juego (suena 200×/sesión) | `sox -n blip.wav synth 0.05 sine 1000 fade h 0.002 0.05 0.02 gain -6` |
| **Motor** | Sawtooth grave (RPM) + ruido (combustión) + LFO tremolo + low-pass; pitch atado a la velocidad en runtime | `sox -n engine.wav synth 2 sawtooth 80 synth 2 pinknoise mix 80 tremolo 30 60 lowpass 400 gain -4` |
| **Viento** | Pink noise a través de band-pass + LFO lento en amplitud (respiración) | `sox -n wind.wav synth 3 pinknoise bandpass 600 400 tremolo 0.3 40 gain -6` |
| **Fuego** | Brown/pink noise + band-pass grave (rugido) + crepitar (ráfagas cortas de ruido agudo por encima) | base: `sox -n fire.wav synth 3 brownnoise lowpass 800 tremolo 8 30 gain -8` + capa de crackle (ráfagas de whitenoise cortas) |
| **Campana / ding** | FM: portador sine + modulador `fmod` con ratio inarmónico, cola larga | `sox -n bell.wav synth 1.5 sine 400 synth 1.5 sine fmod 250 fade h 0 1.5 1.4 gain -3` |
| **Pasos** | Ruido corto filtrado por superficie (madera=mid, hierba=HP con crackle), 3–10 variantes | `sox -n step.wav synth 0.08 pinknoise lowpass 1200 fade h 0 0.08 0.07 gain -8` + variar pitch/filtro por toma |

Detalles que separan un SFX pobre de uno con pegada:
- **Láser:** cuanto más rápido el barrido descendente, más "pequeño/rápido" el arma; barrido lento y grave = arma pesada. Añadir `overdrive` = plasma/energía.
- **Salto:** el pitch SUBE (asociación universal: subir=arriba). Aterrizaje = lo inverso, pitch que baja + un toque de ruido de impacto.
- **Impacto:** las tres capas clásicas (abajo). El "sub-boom" grave (sine 40–80 Hz) es lo que da el golpe físico en subwoofer; en altavoz de móvil no se oye, así que el punch NO puede depender solo del sub [ver: gamedev/audio, test multi-salida].
- **Power-up:** arpegio que sube = positivo; que baja = negativo/derrota. Terceras/quintas mayores suenan "felices" [ver: teoria-musica-juegos].
- **Motor:** el asset base es un loop; en el motor el **pitch se ata a la velocidad** (RTPC/parámetro) y se cruzan capas idle/mid/full [ver: gamedev/audio; middleware-fmod-wwise].

---

## Layering: la anatomía de un SFX con pegada

Un SFX sintetizado con impacto casi nunca es un oscilador — son 2–3 capas con roles distintos, alineadas por el ataque y mezcladas. La regla de las tres capas está en [ver: crear-sfx, layering]; aquí, cómo **sintetizar cada capa** en vez de samplearla:

| Capa | Rol | Cómo sintetizarla |
|---|---|---|
| **Ataque / transient** | El "clic", el punch de los primeros ~20 ms. Es lo que hace que el sonido "llegue" | Ruido muy corto (`synth 0.02 whitenoise`), un click de onda, o un sine grave con ataque instantáneo |
| **Cuerpo / tono** | El carácter y el pitch reconocible | El oscilador principal + filtro (la receta de arriba) |
| **Cola / decay** | Cómo muere: el espacio y el "peso" | Reverb, un sine grave que decae lento, o ruido filtrado que se apaga |

Sintetizar cada capa por separado, exportar, y mezclar con SoX (`sox -m capa1.wav capa2.wav out.wav`) o en Audacity apilando pistas [ver: crear-sfx]. Beneficio extra: randomizar en el motor qué transient suena sobre qué cuerpo multiplica variantes con pocos assets [ver: unity/audio-unity].

**El transient es lo más importante y lo más ignorado.** Dos sonidos con el mismo cuerpo pero distinto ataque se perciben como sonidos totalmente distintos. Un impacto sin transient suena "de goma"; con un click seco de 5 ms encima, "pega".

---

## Procesado: efectos como herramientas de diseño (no de rescate)

El procesado no es maquillaje al final — es parte del diseño. Cada efecto es una decisión tímbrica. Los seis que más trabajan (todos en SoX, todos en cualquier DAW):

| Efecto | Qué hace al diseño | SoX | Ojo |
|---|---|---|---|
| **Pitch / speed** | Bajar = más grande/lento/monstruo; subir = pequeño/rápido. El truco más viejo del foley digital | `pitch <cents>` (sin tocar duración), o `speed <factor>` (pitch+tempo juntos) | `speed` altera duración; `pitch` la conserva |
| **Distorsión / saturación** | Añade armónicos = agresión, energía, "suciedad". Convierte un sine limpio en algo con garra | `overdrive [gain [colour]]` | Poco tiñe, mucho destruye; empuja el nivel → seguir con `gain` |
| **Reverb** | Da espacio y "cola". Un toque disimula cortes de loop; mucho aleja y ensucia | `reverb [reverberance [HF-damp [room-scale ...]]]` | Para SFX 3D, mejor la reverb del **motor** (posicional), no hornearla [ver: unity/audio-unity] |
| **Delay / echo** | Repeticiones = eco, "sci-fi", ritmo. Delays cortos = flanger/robótico | `echos gain-in gain-out delay decay ...` | Delay sincronizado al tempo si va con música |
| **EQ / filtro** | Esculpir: cortar barro (<80–100 Hz HP), quitar sibilancia, dar cuerpo/brillo | `bass`, `treble`, `equalizer f q g`, `highpass`, `lowpass` | Cortar antes que realzar; el HP grave limpia casi todo SFX |
| **Compresión** | Empareja dinámica, sube el "cuerpo", agrega punch al transient | `compand` (attack,decay transfer-fn) | Fácil de sobre-usar; para un one-shot, muchas veces no hace falta |

Orden mental típico de una cadena: **oscilador → filtro → distorsión → EQ → compresión → reverb/delay**. No es dogma, pero distorsionar ANTES de filtrar suena distinto a filtrar antes de distorsionar (probar ambos).

---

## Herramientas de síntesis

### Por código (headless — lo que un agente puede correr)

| Herramienta | Qué es | Licencia | Para qué aquí |
|---|---|---|---|
| **SoX** ("Swiss Army knife of sound") | CLI: `synth` (osc+sweep+ruido), filtros, efectos, cascada de synth | GPL/LGPL, gratis, brew | Generar/procesar SFX por línea de comando; recetas de arriba. Detalle de scripting [ver: hacer-audio-por-codigo] |
| **FluidSynth** | Renderiza MIDI a WAV con un **SoundFont** (banco de instrumentos GM) | LGPL, gratis, brew | Convertir una melodía MIDI en audio con instrumentos reales sin DAW [ver: crear-musica; hacer-audio-por-codigo] |
| **SuperCollider** | Lenguaje + servidor de síntesis en tiempo real; síntesis modular pro | GPLv3, gratis | Síntesis compleja y generativa por código. `{ SinOsc.ar(440) * 0.2 }.play;` = el "hola mundo". Detalle [ver: hacer-audio-por-codigo] |
| **Csound** | Sistema de síntesis por texto (orchestra + score); opcodes (`oscili`, `foscil` FM) | LGPL, gratis | Síntesis precisa y reproducible por archivo de texto. Detalle [ver: hacer-audio-por-codigo] |

FluidSynth, patrón genérico (instalar `fluidsynth` y `sox` por brew, y un SoundFont GM — p.ej. un `.sf2` de dominio público — en una ruta del proyecto):
```
fluidsynth -ni banco.sf2 melodia.mid -F salida.wav -r 44100
```
(`-n` sin driver MIDI, `-i` sin shell interactiva, `-F` render a archivo, `-r` sample rate. Verificado: FluidSynth 2.5.x). Luego se procesa con SoX. Todo el pipeline de audio-por-código, con soundfonts y ejemplos completos, va en [ver: hacer-audio-por-codigo].

### Con interfaz (GUI — para diseñar a oído)

| Herramienta | Qué es | Licencia | Nota |
|---|---|---|---|
| **Surge XT** | Synth híbrido completo (sustractiva + FM + wavetable), pro, muchísimos filtros | **GPLv3, 100% gratis, todo incluido**, Win/Mac/Linux — **verificado en github.com/surge-synthesizer/surge** | El synth gratis más completo; sin tiers de pago. Recomendado por defecto |
| **Vital** | Synth wavetable moderno, visual, con modulación por arrastre | Motor fuente **GPLv3 verificado** (github.com/mtytel/vital). Tier **Basic/free**: sinte completo con todas las funciones, 75 presets, 25 wavetables. **Plus** (pago): 250 presets, 70 wavetables. **Pro** (pago): 400+ presets, 150 wavetables, text-to-wavetable ilimitado, skins, Discord — **verificado en vital.audio, precios en USD no capturados aquí: confirmar antes de presupuestar** | Excelente para timbres en evolución; build propio desde el repo GPL no incluye marca/presets de fábrica |
| **Dexed** | Emulación del Yamaha DX7 (FM 6 operadores) | GPLv3, gratis | La vía directa a FM auténtica: campanas, e-piano, metal |
| **sfxr / jsfxr / Bfxr / ChipTone / rFXGen** | Generadores de un propósito: SFX retro con ~20 parámetros | Libres / CC0 según tool | Para UI y retro NO se sintetiza a mano — se usan estos [ver: crear-sfx, Vía 1] |
| **Furnace / OpenMPT** | Trackers con chips reales (FM YM2612, PSG, wavetable) | Gratis, open source | Síntesis de chip para chiptune [ver: chiptune-trackers] |

Cuándo GUI vs código: **diseñar a oído** (explorar, "buscar" un sonido) → GUI, es iterativo y visual. **Producir en lote, reproducible, o que un agente lo genere** → código (SoX/SC/Csound), versionable y automatizable.

---

## Recrear vs grabar vs sintetizar: cuándo cada vía

Las cuatro vías generales (síntesis / foley / editar biblioteca / pack) y su regla coste-vs-identidad están en [ver: crear-sfx]. Aquí, específicamente cuándo **sintetizar** gana:

| Situación | Vía recomendada | Por qué |
|---|---|---|
| SFX de UI, retro, chiptune, 8-bit | **Sintetizar** (sfxr/tracker) | Es literalmente el sonido que se busca; grabar sería absurdo |
| Láser, sci-fi, magia, energía, "no existe en el mundo real" | **Sintetizar** | No hay qué grabar; el synth ES la fuente |
| Motor, drone, alarma, tono electrónico | **Sintetizar** (o layering síntesis+grabación) | Control total, loop perfecto, sin ruido de fondo |
| Pasos, tela, madera, impactos orgánicos, voz | **Grabar (foley)** | Lo orgánico sintetizado suena falso; el mundo real tiene detalle imposible de sintetizar [ver: foley-grabacion] |
| Arma real, naturaleza, ciudad, ambiente realista | **Biblioteca editada** (+ capa sintética de refuerzo) | Grabarlo bien es carísimo; la biblioteca da la base, la síntesis añade el sub/cola [ver: crear-sfx] |
| Necesitas 40 variantes de algo y control por parámetro | **Sintetizar** | Cero coste marginal por variante; parametrizable |

El híbrido gana casi siempre: un impacto "real" = capa de biblioteca (cuerpo) + foley propio (carácter) + **sub sintetizado** (el boom que la grabación no tiene) + cola de reverb. Sintetizar rara vez es el 100% del sonido; casi siempre es **una capa** que aporta lo que grabar no da: el sub, la cola limpia, el barrido imposible.

---

## Reglas prácticas

- [ ] Antes de sintetizar, **descomponer** el sonido objetivo en las 4 dimensiones (pitch / envolvente / timbre / textura) y decidir cada una por separado.
- [ ] Elegir oscilador por timbre: opaco→sine/triangle, áspero/lleno→saw, hueco/8-bit→square, metálico→FM, sin tono→noise.
- [ ] Elegir tipo de síntesis por el sonido: sustractiva de base; FM para metal/campanas; física (`pluck`) para cuerda/gota; granular/wavetable para texturas.
- [ ] La **envolvente define el reconocimiento**: definir A/D/S/R antes que el timbre. Impacto = AD con sustain 0; drone = A lento + sustain alto + R largo.
- [ ] Modular el **cutoff del filtro** (con envolvente o LFO) para dar movimiento — es el 80% de la vida tímbrica.
- [ ] FM: ratio **entero** = armónico (e-piano, brass); ratio **no entero** = inarmónico (campana, metal).
- [ ] Construir SFX con pegada por **capas** (transient + cuerpo + cola); el transient de ~5–20 ms es lo que hace que "pegue" [ver: crear-sfx].
- [ ] El **sub-boom** grave da golpe en subwoofer pero desaparece en móvil: el punch no puede depender solo del sub [ver: gamedev/audio].
- [ ] Tras cada `synth` de SoX, **seguir con `gain -N`** (synth sale a 0 dBFS = clipping asegurado al mezclar).
- [ ] Pitch sube = "arriba/positivo/pequeño"; pitch baja = "abajo/negativo/grande". Usar la asociación (salto sube, aterrizaje baja).
- [ ] Recrear una referencia: igualar loudness antes de comparar A/B; el volumen engaña al oído.
- [ ] Diseñar a oído → GUI (Surge/Vital/Dexed); producir en lote/reproducible/por agente → código (SoX/SC/Csound).
- [ ] Sintetizar como **capa**, no como sonido entero: aporta lo que grabar no da (sub, cola limpia, barrido imposible).
- [ ] SFX tonales (blip, campana, power-up) afinados a la tonalidad de la música para evitar disonancia [ver: teoria-musica-juegos].
- [ ] Variar por runtime (pitch/volumen/qué capa) antes que hornear 10 WAV [ver: unity/audio-unity].
- [ ] Exportar mono para SFX 3D, WAV lossless con headroom; el acabado y naming en [ver: audio-a-juego].

## Errores comunes

| Error | Antídoto |
|---|---|
| Empezar por el timbre y olvidar la envolvente | La envolvente (A/D/S/R) es lo primero que el oído reconoce: definirla antes que el oscilador |
| Sonido "plano/de goma", sin pegada | Falta el **transient**: añadir un click/ruido corto de 5–20 ms al inicio (capa de ataque) |
| Usar sine para todo → sonidos débiles y opacos | Sine solo tiene el fundamental; para brillo/cuerpo usar saw/square y esculpir con filtro |
| Intentar campana/metal con sustractiva y no salir | El metal es inarmónico: usar **FM con ratio no entero** (o Dexed), no filtros |
| `synth` de SoX y el resultado clippea al mezclar | `synth` sale a 0 dBFS: seguir SIEMPRE con `gain -3` (o menos) |
| Inventar flags de SoX que "suenan lógicos" | Verificar contra `man sox`; los tipos son `sine/square/triangle/sawtooth/trapezium/exp/[white/pink/brown]noise/pluck`, combine `create/mix/amod/fmod` |
| Punch que depende solo del sub-boom grave | En móvil el sub no suena: poner el carácter también en medios/agudos; probar en ≥3 salidas [ver: gamedev/audio] |
| Reverb "horneada" en un SFX 3D | Para 3D usar la reverb posicional del motor; hornear solo para 2D/UI [ver: unity/audio-unity] |
| Sintetizar pasos/voz/tela orgánica y que suene falso | Lo orgánico se **graba** (foley); sintetizar solo lo que no existe en el mundo real [ver: foley-grabacion] |
| Un solo SFX sintetizado sin variación (efecto metralleta) | Randomizar pitch/volumen/capa en runtime o exportar 3–10 variantes [ver: unity/audio-unity] |
| Comparar tu recreación con la referencia a distinto volumen | Igualar loudness primero; si no, el más fuerte "gana" siempre por sesgo del oído |
| Sobre-procesar (distorsión+reverb+comp en todo) | Cada efecto es una decisión tímbrica con intención; cortar (EQ/HP) antes que realzar |

## Fuentes

- **SoX — Sound eXchange, man page** (sox.sourceforge.net) — sintaxis del efecto `synth` (tipos de onda, combine, barridos `: + / -`, notación de nota/semitono), y de `fade/overdrive/reverb/echos/tremolo/bend/pitch/lowpass/highpass/bandpass/gain/compand`. **Verificado contra `man sox` del binario instalado (SoX 14.4.x)**; todas las recetas fueron ejecutadas y producen WAV válido.
- **FluidSynth** (fluidsynth.org) — render de MIDI+SoundFont a WAV; `fluidsynth -ni banco.sf2 in.mid -F out.wav -r 44100`. **Verificado: FluidSynth 2.5.6 instalado.**
- **Sound On Sound — "Synth Secrets" (Gordon Reid, serie de 63 partes)** (soundonsound.com) — referencia canónica de síntesis: osciladores y contenido armónico, ADSR, filtros (cutoff/resonancia/pendiente), LFO/modulación, síntesis sustractiva/FM/aditiva. Base de la teoría de los cuatro bloques.
- **John Chowning — "The Synthesis of Complex Audio Spectra by Means of Frequency Modulation" (JAES, 1973)** — el paper fundacional de la síntesis FM; ratio portador:modulador → armonicidad. Base del criterio "ratio entero=armónico, no entero=inarmónico".
- **Karplus & Strong — "Digital Synthesis of Plucked-String and Drum Timbres" (Computer Music Journal, 1983)** — algoritmo de síntesis física de cuerda punteada (ruido→delay+filtro en lazo); es lo que implementa `synth ... pluck` de SoX.
- **Curtis Roads — "Microsound" (MIT Press, 2001)** — referencia canónica de síntesis granular (granos de 1–100 ms, texturas).
- **Surge XT** (surge-synthesizer.github.io; github.com/surge-synthesizer/surge) — synth híbrido open source, **GPL-3.0 confirmado por WebFetch al repo**, gratis y completo, sin tiers de pago.
- **Vital** (vital.audio, Matt Tytel; github.com/mtytel/vital) — synth wavetable; **motor GPL-3.0 confirmado por WebFetch al repo**; tier Basic/free con el sinte completo (75 presets/25 wavetables) y tiers Plus/Pro de pago con más contenido — **confirmado por WebFetch a vital.audio esta sesión; el monto en USD de cada tier no quedó capturado, confirmar antes de presupuestar**.
- **Nota de verificación:** en la sesión de investigación original, WebSearch estaba agotado y WebFetch caído; esta auditoría posterior sí tuvo WebFetch disponible y usó esa ventana para verificar en vivo licencia y tiers de Surge XT (GitHub) y Vital (GitHub + vital.audio) — ambos confirmados GPL-3.0, sin discrepancias con lo redactado. El resto de la teoría de síntesis se apoya en conocimiento estándar/textbook (fuentes canónicas arriba) y la sintaxis de herramientas sigue verificada contra los **binarios reales instalados** (SoX, FluidSynth; recetas de la sección de recetas re-ejecutadas en esta auditoría, todas producen WAV válido sin error). Los términos de licencia de middleware [ver: middleware-fmod-wwise] siguen sin re-verificar aquí.
