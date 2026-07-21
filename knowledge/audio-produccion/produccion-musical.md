# Producción musical: del MIDI a la pista

> **Cuando cargar este archivo:** cuando ya decidiste COMPONER la música (no licenciar/IA/contratar) y hay que producir una pista de principio a fin — montar el arreglo en MIDI, elegir los sonidos/instrumentos, mezclar para que cada capa tenga su sitio, dejar un master ligero y exportar loops/stems. Cubre el **flujo de producción** dentro de un DAW **y** el flujo equivalente **por código** (para un agente sin GUI: `mido` + `fluidsynth` + `sox`). NO repite de dónde SALE la música ni las licencias (eso es [ver: crear-musica]), ni el acabado game-ready/entrega (eso es [ver: audio-a-juego]), ni la teoría musical de escalas/acordes ([ver: teoria-musica-juegos]), ni la mezcla profunda de todo el juego ([ver: direccion-audio-mezcla]), ni la música adaptativa/stems en el motor ([ver: musica-adaptativa]). Aquí va el CRAFT de fabricar UNA pista.

## Reparto: qué SÍ y qué NO va aquí

| Tema | Dónde vive |
|---|---|
| De dónde sacar la música (componer/CC/licenciar/IA/contratar), licencias | [ver: crear-musica] |
| Escalas, acordes, tonalidad, modos, tensión/resolución para juegos | [ver: teoria-musica-juegos] |
| Mezcla y dirección de audio de TODO el juego (buses, prioridad, ducking) | [ver: direccion-audio-mezcla] |
| Stems/intro-loop **en el motor**, vertical layering, transiciones | [ver: musica-adaptativa], [ver: gamedev/audio] |
| Cortar el loop, normalizar, mono/estéreo, nombrar, entregar game-ready | [ver: audio-a-juego] |
| Trackers y chiptune como flujo de producción alternativo | [ver: chiptune-trackers] |
| Síntesis y diseño de un sonido/instrumento desde cero | [ver: sintesis-y-diseno-sonido] |
| **Aquí:** arreglo MIDI → sonidos → mezcla de la pista → master ligero → export, y el flujo por código | **produccion-musical** |

---

## 1. El flujo de una pista (mapa)

```
IDEA/TEMA → ARREGLO (MIDI) → SONIDOS (instrumentos) → MEZCLA → MASTER ligero → EXPORT (loop/stems)
```

| Fase | Qué se decide | Salida | Error si se salta |
|---|---|---|---|
| **Idea/tema** | Tempo, tonalidad, mood, referencia (3 tracks), rol en el juego | 1 frase + BPM + tono | Componer sin norte → pista genérica |
| **Arreglo (MIDI)** | Notas, progresión, capas, arco/dinámica | proyecto DAW o `.mid` | Todo a la vez, sin arco → aburre al loop 3 |
| **Sonidos** | Qué instrumento suena cada capa (soundfont/VST/synth) | pistas con instrumento asignado | Preset de fábrica sin retoque → suena a demo |
| **Mezcla** | Niveles relativos, paneo, EQ, reverb, low-end | balance interno de la pista | "sube todo" → barro, clipping |
| **Master ligero** | Loudness, headroom, que suene en móvil | 1 archivo estéreo con -1 dBTP y margen | Aplastar a 0 dB → no queda headroom para el motor |
| **Export** | Loop seamless, intro+loop, stems | WAV lossless + stems | MP3/loop mal cortado → hueco cada vuelta [ver: audio-a-juego] |

Decisión que va ANTES de la primera nota: **¿la pista será adaptativa?** Si sí, se compone en **stems** e **intro+loop** desde el minuto cero, no se trocea después [ver: musica-adaptativa]. Rehacer una pista lineal en stems cuesta más que componerla bien de entrada.

---

## 2. El DAW: anatomía (qué es de verdad)

Un **DAW** (Digital Audio Workstation) es el software donde se graba, programa, mezcla y exporta. La lista de cuáles usar y su licencia/coste está en [ver: crear-musica] y [ver: herramientas-recursos-audio]; aquí importa entender sus **partes**, porque son las mismas en todos (LMMS, GarageBand, Reaper, Cakewalk...) y en el flujo por código tienen su equivalente.

| Parte | Qué es | Equivalente por código |
|---|---|---|
| **Pista MIDI** | Notas (qué/cuándo/qué fuerte), NO audio. Se puede reeditar libremente | evento `note_on`/`note_off` en `mido` |
| **Pista de audio** | Onda ya renderizada (grabación o bounce). Se edita como sample | archivo WAV que sale de `fluidsynth`/`sox` |
| **Virtual instrument** | El "instrumento" que convierte MIDI en sonido (sampler, synth, soundfont) | soundfont `.sf2` cargado por `fluidsynth`, o SynthDef de SuperCollider |
| **Piano roll** | Rejilla donde se dibujan/editan las notas MIDI (altura×tiempo) | lista de `Message` con `note`, `velocity`, `time` |
| **Plugin / VST** | Efecto (EQ, reverb, compresor) o instrumento externo que se inserta en una pista | efecto de `sox` / filtro de `ffmpeg` |
| **Mixer** | Faders, paneo, sends y buses por pista → suma al master | render + `sox`/gain por stem |
| **Bus / send** | Canal auxiliar donde varias pistas comparten un efecto (p. ej. una reverb) | un `sox reverb` aplicado al submix |
| **Automation** | Curvas que mueven un parámetro en el tiempo (volumen, filtro) | volumen por evento / CC MIDI (`control_change`) |

**MIDI vs audio — la distinción que todo lo demás asume:** el MIDI es una *partitura editable* (cambias una nota, el tempo o el instrumento sin recomponer); el audio es la *foto revelada* (ya no cambias las notas, solo lo editas como onda). Se compone y arregla en MIDI el máximo tiempo posible y se "revela" a audio (bounce/render) lo más tarde posible. En código: se trabaja el `.mid`, y solo al final se renderiza a WAV.

**Elegir uno (resumen, detalle en [ver: crear-musica]):** GarageBand (Mac, gratis, loops listos) para arrancar en Mac; LMMS (gratis, GPL, multiplataforma) fuera de Mac con flujo de patrones; Reaper (prueba 60 días completa, licencia con descuento) cuando vas en serio. **Cakewalk**: el histórico "Cakewalk by BandLab" cambió (BandLab lo migró a "Sonar"/"Next") — **confirmar el estado y la licencia 2026 en bandlab.com antes de recomendarlo** (NO VERIFICADO en esta pasada). No aprender un DAW pesado "por si acaso" para 3 loops: BeepBox/tracker/código alcanzan [ver: chiptune-trackers].

---

## 3. MIDI y virtual instruments: notas, sonidos, humanización

### Programar las notas
El material mínimo de una pista MIDI: **nota** (altura, 0–127; 60 = Do central/C4), **velocity** (fuerza, 0–127), **inicio** y **duración** (en ticks). En el DAW se dibuja en el piano roll; por código son `note_on`/`note_off` (§7).

### Elegir el sonido (el instrumento que suena la nota)

| Opción | Qué es | Para el agente | Licencia/ojo |
|---|---|---|---|
| **SoundFont GM (`.sf2`)** | Banco de samples multi-instrumento con el mapa **General MIDI** (128 instrumentos + kit de batería) | ✅ lo que carga `fluidsynth`; instantáneo, sin GUI | Usar un SF2 con licencia clara (muchos GM libres; verificar la del archivo) [ver: herramientas-recursos-audio] |
| **VST/AU gratis** | Instrumento plugin (synths, pianos, orquesta) dentro del DAW | ❌ necesita GUI/host | Revisar EULA: casi todos permiten uso comercial del audio, pero confirmar |
| **Synth del DAW** | Osciladores integrados (LMMS: TripleOscillator/ZynAddSubFX; GarageBand: instrumentos) | ❌ GUI | El audio que produces es tuyo |
| **Sampler propio** | Cargar tus grabaciones/foley como instrumento | Parcial (samples + mapeo) | Los samples deben estar licenciados [ver: foley-grabacion] |

**General MIDI (GM):** estándar de 128 programas con nombres fijos, así una pista suena "parecida" en cualquier SF2/sintetizador GM. Los números de *program change* son **0-indexados** (el nº del GM spec menos 1). Útiles:

| Program (0-idx) | Instrumento GM | Program (0-idx) | Instrumento GM |
|---|---|---|---|
| 0 | Acoustic Grand Piano | 48 | String Ensemble 1 |
| 4 | Electric Piano (Rhodes) | 56 | Trumpet |
| 24 / 25 | Nylon / Steel Guitar | 73 | Flute |
| 32 / 33 | Acoustic / Electric Bass (finger) | 80 / 81 | Lead square / sawtooth |
| 40 | Violin | 88 / 89 | Pad new age / warm |

**Percusión = canal 10.** En GM, el **canal MIDI 10** (índice **9** en `mido`, 0-based) es siempre batería: ahí el *número de nota* elige el tambor, no la altura. Mapa GM estándar: 36 bombo, 38 caja, 42 hi-hat cerrado, 46 hi-hat abierto, 49 crash, 51 ride. (En `mido`: `Message('note_on', channel=9, note=36, ...)`.)

### Humanizar (que no suene a máquina)
MIDI perfectamente cuantizado suena robótico. Tres palancas:

| Palanca | Qué hacer | Valor típico |
|---|---|---|
| **Velocity** | Variar la fuerza nota a nota (acentos en tiempos fuertes) | ±5 a ±15 sobre la base |
| **Timing** | Correr las notas unos ticks fuera de la rejilla | ±10–30 ticks (con TPB 480) |
| **Swing** | Retrasar cada corchea/semicorchea par | 8–20% del valor de la nota |

Regla: la batería y el bajo pueden ir más "tight" (poco jitter); pads, teclas y leads toleran/agradecen más humanización. Cuantizar primero al 100% y luego "des-cuantizar" a mano un poco es más rápido que tocar perfecto.

---

## 4. Arreglo por capas y el arco de la pista

Una pista de juego se construye por **capas con roles**, no como una masa. Cada capa ocupa un registro de frecuencia y una función:

| Capa | Rol | Registro (aprox) | Nota de producción |
|---|---|---|---|
| **Bajo (bass)** | Fundamento tonal + groove | 40–250 Hz | Casi siempre **mono**; una nota por acorde basta [ver: §6 low-end] |
| **Armonía (chords/pads)** | Colchón, define el acorde y el mood | 200 Hz–4 kHz | Pads sostienen; teclas/guitarra rítmica dan pulso |
| **Melodía (lead)** | Lo que se tararea, la identidad | 500 Hz–5 kHz | Una sola voz protagonista; que no compita con la armonía |
| **Percusión (perc/drums)** | Pulso, energía, ritmo | full-range (kick sub, hats agudos) | El motor de la dinámica; entra/sale para subir/bajar intensidad |
| **Textura (fx/atmósfera)** | Aire, transición, "sal" | agudos/ruido | Risers, impactos, ambiences finos [ver: sintesis-y-diseno-sonido] |

### El arco: añadir y quitar capas = dinámica
La intensidad de una pista NO se controla subiendo el volumen, sino **cuántas capas suenan**. Este es también el principio del *vertical layering* adaptativo [ver: musica-adaptativa].

- **Empezar quitando, no añadiendo:** compón la versión "llena" y luego decide qué se calla en las secciones bajas. Regla de oro: si al mutear una capa la pista *sigue teniendo sentido*, el arreglo está sano.
- Arco típico de un loop de exploración: `bed (bajo+pad)` → +percusión suave → +melodía → sección plena → vuelta al bed. Cada quita/pon debe caer en un límite de compás.
- **Contraste por registro, no por volumen:** para "subir energía", añade agudos (hats, lead) y ataque, no solo dB.
- Para adaptativo se compone pensando "¿qué pasa si solo suena el bed?" desde el inicio, y se exporta cada capa como **stem alineado** (§8).

---

## 5. Mezcla de la pista: que cada instrumento tenga su sitio

Mezclar no es "subir todo": es **hacer sitio**. Cuatro herramientas, en este orden. (La mezcla profunda de todo el juego —buses, prioridad, sidechain global— está en [ver: direccion-audio-mezcla]; aquí, la pista sola.)

### 1) Niveles relativos (balance)
- Fijar primero el **elemento ancla** (normalmente batería o bajo) y balancear el resto contra él, no al revés.
- Mezclar a volumen **bajo-medio**: si suena bien flojo, suena bien fuerte. Mezclar fuerte engaña al oído (todo parece "bueno").
- Jerarquía: melodía y percusión al frente; bajo presente pero no tapando; pads/texturas de fondo. Dejar **headroom** en el master (§6), no llevar el mix a 0 dB.

### 2) Panorama (estéreo)
- **Centro (mono):** bajo, bombo/caja, y la voz/lead protagonista. Lo grave y lo importante va al centro.
- **A los lados:** pads, hats, arpegios, dobles, texturas — dan anchura sin robar el centro.
- Regla del low-end: **todo lo grave al centro**; graves paneados descuadran la imagen y molestan en altavoces mono (móvil).

### 3) EQ para carving (que no se peleen dos capas)
Cada capa vive en su banda; se recorta lo que estorba, no se sube lo que falta.

| Instrumento | High-pass (cortar debajo) | Cuidar / recortar | Presencia |
|---|---|---|---|
| Bajo | 30–40 Hz (rumble) | Barro 200–400 Hz | Ataque 700 Hz–1 kHz |
| Bombo | 30 Hz | 300–500 Hz (cartón) | Click 3–5 kHz |
| Pads/armonía | 100–200 Hz (dejar sitio al bajo) | Nasal 500 Hz–1 kHz | Aire 8–12 kHz |
| Melodía/lead | según registro | competencia con pads en 1–3 kHz | 2–5 kHz |
| Hats/perc aguda | 300–500 Hz | — | brillo 10 kHz+ |

Truco de carving: si dos capas se pelean en una banda, **baja una** ahí en vez de subir la otra. Y **high-pass todo lo que no sea bajo/bombo** para despejar los graves.

### 4) Reverb y espacio (profundidad)
- Usar la reverb como **send/bus compartido**, no una por pista: manda varias capas a la misma reverb → suenan en el "mismo cuarto".
- Más reverb = más lejos; seco = al frente. La melodía suele ir más seca que los pads.
- **No ahogar en reverb:** en un juego, buena parte del espacio lo pone el motor (reverb zones, oclusión) [ver: unity/audio-unity]. La pista se entrega con la reverb *musical* justa, no con la *ambiental* del sitio del juego.

### El low-end: la trampa nº1
- **Un solo elemento manda en el sub** (bombo *o* bajo dominante en cada momento; si chocan, sidechain el bajo al bombo). Dos cosas peleando bajo 100 Hz = barro que se come el headroom.
- **Bajo en mono** bajo ~120 Hz siempre.
- El sub (< 60 Hz) **no existe en el altavoz del móvil**: poner el "cuerpo" reconocible de bajo/bombo en los **medios-graves (80–250 Hz)** para que sobreviva (lección DOOM) [ver: audio-a-juego §6].

---

## 6. Master ligero de la pista

No es masterizar un disco; es dejar la pista **legible en cualquier altavoz y con headroom para el motor**. El acabado game-ready (formato, dither, loop, entrega) está en [ver: audio-a-juego]; aquí, la cadena musical.

| Paso | Qué | Objetivo |
|---|---|---|
| **High-pass del mix** | Cortar < 30–40 Hz | Quitar sub inútil que roba headroom |
| **Compresión de bus (suave)** | Ratio ~2:1, poca reducción | Pegar el conjunto, no aplastarlo |
| **Limitar/normalizar el pico** | Techo **-1 dBTP** | Sin clipping tras compresión lossy |
| **Loudness** | Integrado moderado, **con headroom** | No competir con el master de streaming; el mix final del juego se hace in-engine |
| **Test multi-salida** | Auriculares + móvil real + laptop/TV | Que el móvil no se coma la info |

- **Headroom para el motor:** entregar la música con **picos ~6–9 dB bajo el máximo** (o normalizada a ~-1 dBTP pero sin sobre-comprimir), porque el volumen final lo pone el AudioMixer con SFX y voz sumados encima [ver: direccion-audio-mezcla], [ver: unity/audio-unity]. Aplastar la música a 0 dB deja al mezclador del juego sin margen.
- **No hay UN LUFS obligatorio** para música de juego como el -14 de streaming; el loudness real se decide en el master bus del juego corriendo, no en la pista suelta [ver: audio-a-juego §4].

---

## 7. Hacer música POR CÓDIGO (agente, sin DAW GUI)

Flujo real para producir música sin abrir una GUI, **verificado en esta máquina** (macOS, 2026-07-21): `mido` escribe el MIDI, `fluidsynth` lo renderiza con un soundfont, `sox`/`ffmpeg` hacen el post. Es el equivalente headless del DAW: `mido` = piano roll, `.sf2` = virtual instrument, `fluidsynth` = bounce, `sox` = mixer/master. Detalle ampliado en [ver: hacer-audio-por-codigo].

### Stack (genérico, sin rutas de usuario)
```
brew install fluid-synth sox ffmpeg     # fluidsynth 2.5.x, sox, ffmpeg
python3 -m venv venv && venv/bin/pip install mido   # mido 1.3.x, MIDI puro en Python
# + un soundfont General MIDI .sf2 con licencia clara en una ruta conocida
```
> ⚠️ El paquete brew se llama `fluid-synth`; el binario es `fluidsynth`. Trae un SF2 de ejemplo dentro de su Cellar (`share/fluid-synth/sf2/…`), pero para producir usa un GM completo con licencia verificada [ver: herramientas-recursos-audio].

### Paso 1 — Escribir el MIDI con `mido` (API real, verificada)
```python
from mido import Message, MidiFile, MidiTrack, MetaMessage, bpm2tempo

TPB = 480                                   # ticks por negra (resolución)
mid = MidiFile(ticks_per_beat=TPB)

bass = MidiTrack(); mid.tracks.append(bass)
bass.append(MetaMessage('set_tempo', tempo=bpm2tempo(100), time=0))   # BPM → µs/negra
bass.append(Message('program_change', program=33, time=0))            # 33 → Electric Bass
for root in [45, 41, 48, 43]:               # Am F C G (una nota por compás)
    bass.append(Message('note_on',  note=root, velocity=80, time=0))
    bass.append(Message('note_off', note=root, velocity=0,  time=TPB*4))  # 4 negras

mid.save('track.mid')
```
- **`time` es delta (ticks desde el evento anterior)**, no absoluto: `time=0` = simultáneo; `note_off` con `time=TPB*4` = dura 4 negras. Este es el error nº1 con `mido`.
- `ticks_per_beat` (TPB) fija la resolución (480 es estándar). `bpm2tempo(bpm)` da el tempo en µs/negra que espera `set_tempo`.
- Percusión: mismo patrón pero `Message('note_on', channel=9, note=36, ...)` (canal 10 GM, nota = tambor).
- Humanizar: `velocity=80+random.randint(-8,8)` y sumar/restar unos ticks al `time` (§3).

### Paso 2 — Renderizar a WAV con `fluidsynth` (flags verificados, v2.5.6)
```bash
fluidsynth -ni -g 0.6 -r 44100 -F track.wav  soundfont.sf2  track.mid
```
| Flag | Qué hace (verificado en `--help`) |
|---|---|
| `-F <file>` / `--fast-render` | Renderiza el MIDI a archivo (modo offline, sin reproducir) |
| `-n` / `--no-midi-in` | No abrir driver de entrada MIDI |
| `-i` / `--no-shell` | No abrir el shell interactivo (juntos: `-ni`, salir limpio) |
| `-r 44100` / `--sample-rate` | Sample rate de salida |
| `-g 0.6` / `--gain` | Master gain (0 < g < 10, **default 0.2** = muy bajo; subir con cuidado) |
| `-T wav` / `--audio-file-type` | Forzar tipo (si no, se infiere de la extensión `.wav`) |
| `-O s16` / `--audio-file-format` | Bit depth/formato (s16, s24, float…) |
| `-R 0 -C 0` | **Apagar reverb y chorus** (ON por defecto) → render seco para stems |

Táctica de niveles: renderizar a `-g` moderado y **normalizar con `sox` después** (más control que subir el gain y arriesgar clip).

### Paso 3 — Post con `sox` / `ffmpeg` (verificado)
```bash
sox --i track.wav                              # info (canales, SR, duración)
sox track.wav master.wav highpass 40 gain -n -1  # HPF 40 Hz + normalizar pico a -1 dBFS
sox master.wav -n stats                        # medir: Pk lev dB, RMS lev dB, DC offset
# loop/intro:
sox master.wav intro.wav trim 0 4              # primeros 4 s (intro)
sox master.wav loop.wav  trim 4                # de 4 s al final (loop)
sox loop.wav loop_f.wav fade t 0.01 0 0.05     # micro-fade in/out (matar clicks)
sox intro.wav loop.wav joined.wav              # concatenar
sox loop.wav dry.wav reverb 30                 # reverb (0–100)
sox in.wav out.wav tempo 1.10                  # tempo +10% sin cambiar pitch
sox loop.wav loop.ogg                          # → OGG Vorbis (sox lo escribe directo)
ffmpeg -i loop.wav -c:a libopus -b:a 128k loop.opus   # → Opus
```
- `gain -n` normaliza; `-n -1` deja el pico en **-1 dBFS**. En mi corrida: `Pk lev dB -1.00`, `RMS lev dB -21.54`, `DC offset 0.0` (medido con `sox -n stats`).
- **OGG para loops:** `sox in.wav out.ogg` funciona. Con `ffmpeg`, si el build **no trae `libvorbis`** (frecuente en brew) usa el vorbis nativo con `-c:a vorbis -strict experimental` (peor calidad) o `libopus`; o deja que `sox` escriba el OGG. Nunca MP3 en loops (padding = hueco) [ver: audio-a-juego §5].
- El bit depth/dither final y el corte fino del loop (zero-crossing, crossfade de cola, PyMusicLooper) son de acabado → [ver: audio-a-juego §5].

### Síntesis pura (alternativa, más avanzada)
Cuando no quieres el "sonido soundfont" y buscas timbres propios, la ruta es **síntesis por código**:

| Herramienta | Qué | Nota |
|---|---|---|
| **SuperCollider** (`sclang`) | Motor de síntesis; `SynthDef` define instrumentos, render offline con `Score`/NRT | Potente, curva alta. **No ejecutado en esta pasada** (no instalado aquí); la API `SynthDef{...}.add` es estándar. Detalle en [ver: sintesis-y-diseno-sonido] |
| **Sonic Pi** | Live-coding en Ruby, mucho más fácil que SC para melodías/loops | Bueno para prototipos rápidos |
| **csound** | Síntesis clásica por scoring | Muy preciso, sintaxis vieja |

Para el 90% del audio de un juego (música tonal con instrumentos reconocibles), **`mido` + `fluidsynth` gana**: es el camino que produce una pista usable con menos fricción. La síntesis pura es para diseño de timbre e identidad sonora [ver: sintesis-y-diseno-sonido].

---

## 8. Loops y stems: exportar la pista lista para el juego

La producción del asset termina aquí; el corte fino y la implementación en el motor están en [ver: audio-a-juego] y [ver: musica-adaptativa]. Lo que toca al que PRODUCE:

- **Loop seamless:** componer para que la cola empalme con el inicio (solapar el decay/reverb del final sobre el arranque). Cortar en el ataque de un beat, verificar **10+ vueltas** [ver: audio-a-juego §5]. Por código: renderizar con una cola extra y sumarla al inicio con `sox`.
- **Intro + loop:** exportar `_intro.wav` (una vez) y `_loop.wav` (repite) separados; el motor los empalma sin gap con `PlayScheduled` [ver: unity/audio-unity], [ver: musica-adaptativa].
- **Stems para adaptativo:** exportar cada capa (bed/perc/melodía/tensión) como archivo **alineado a la muestra** (mismo largo, mismo inicio, mismo tempo/tono). Desde el DAW: silenciar todo menos una capa y bounce; **desde código: escribir un `.mid` por capa** (o renderizar el mismo MIDI aislando pistas) y `fluidsynth` cada uno → stems perfectamente alineados por construcción. Renderizar los stems **secos** (`-R 0 -C 0`) para que el motor ponga el espacio.
- Guardar SIEMPRE el proyecto fuente (`.mid`, `.rpp`, `.mmp`, script) además del render, para poder ajustar sin recomponer.

---

## 9. Producir con recursos (sin ser instrumentista)

No hace falta tocar un instrumento para producir una pista decente. Ensamblar > tocar. (Catálogo de fuentes y su licencia: [ver: herramientas-recursos-audio]; rutas y licencias de música: [ver: crear-musica].)

| Recurso | Cómo se usa | Riesgo de licencia |
|---|---|---|
| **Loops de librería** | Arrastrar/pegar loops ya tocados (batería, bajo, riffs) y combinar | ⚠️ Muchos loops NO cubren uso en juego ("sync"); leer el alcance |
| **Samplepacks / one-shots** | Cargar hits/notas como instrumento y programar el MIDI | Verificar SLA; los del DAW suelen ir dentro de tu obra, no sueltos |
| **Presets de synth/instrumento** | Partir de un preset y retocarlo (no de fábrica crudo) | El audio es tuyo; el preset a veces tiene términos |
| **SoundFonts GM** | Todo el arreglo con un SF2 (§7) | Usar SF2 con licencia clara |
| **MIDI de dominio público** | Partir de un `.mid` de una pieza clásica (composición PD) y renderizarlo tú | La **composición** puede ser PD, pero renderiza TU audio; una grabación ajena tiene copyright [ver: crear-musica] |

Regla operativa (legal serio): **una fila en el registro de licencias por cada loop/sample/preset/SF2** que entra (archivo, autor, licencia, URL, atribución). Sin fila, no entra. La chuleta CC (CC0/CC-BY/⛔NC/⚠️SA) y el registro `CREDITS.md` están en [ver: herramientas-recursos-audio] y [ver: crear-musica]. Middleware (FMOD/Wwise) no toca la producción de la pista, solo su reproducción adaptativa → [ver: middleware-fmod-wwise], [ver: musica-adaptativa].

---

## Reglas prácticas

- [ ] Decidir ANTES de la primera nota: BPM, tonalidad, mood, referencia (3 tracks) y **si será adaptativa** (si sí → stems + intro/loop desde el inicio) [ver: musica-adaptativa].
- [ ] Trabajar en **MIDI** el máximo tiempo; "revelar" a audio (bounce/render) lo más tarde posible.
- [ ] Componer la versión llena y luego **quitar capas** para las secciones bajas; si al mutear una capa la pista sigue teniendo sentido, el arreglo está sano.
- [ ] Dinámica = **cuántas capas suenan**, no el fader del master; los cambios caen en límite de compás.
- [ ] Humanizar velocity (±5–15) y timing (±10–30 ticks); batería/bajo más "tight", pads/leads más sueltos.
- [ ] Percusión GM en **canal 10** (índice 9); nota = tambor (36 kick, 38 snare, 42 hat).
- [ ] Mezclar a volumen **bajo-medio**; anclar en batería/bajo y balancear el resto contra el ancla.
- [ ] **Todo lo grave al centro y en mono** (< ~120 Hz); un solo elemento manda en el sub.
- [ ] **High-pass todo lo que no sea bajo/bombo**; carving = bajar la capa que estorba, no subir la otra.
- [ ] Reverb como **send compartido**, con moderación (el espacio del sitio lo pone el motor).
- [ ] Cuerpo de bajo/bombo en **medios-graves (80–250 Hz)** para que sobreviva el móvil (lección DOOM).
- [ ] Master ligero: HPF < 40 Hz, compresión de bus suave (2:1), pico **-1 dBTP**, y dejar **headroom (~6–9 dB)** para el mezclador del juego.
- [ ] Por código: `mido` (recordar que `time` es **delta en ticks**) → `fluidsynth -ni -g 0.6 -r 44100 -F out.wav sf2 mid` → `sox`/`ffmpeg` para normalizar/loop/OGG.
- [ ] Stems por código: un `.mid` por capa → `fluidsynth` cada uno **seco** (`-R 0 -C 0`) → alineados por construcción.
- [ ] Loop en **OGG/WAV, nunca MP3**; verificar 10+ vueltas; intro+loop separados [ver: audio-a-juego].
- [ ] Guardar el proyecto fuente (`.mid`/`.rpp`/script) además del render final.
- [ ] Una fila de registro de licencias por cada loop/sample/preset/SF2 que entra; verificar que el loop cubra uso "in-game/sync".

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| `mido`: notas encimadas o duración rara | `time` es **delta en ticks** desde el evento previo, no absoluto: `time=0` = simultáneo, `note_off time=TPB*4` = 4 negras |
| Bounce a audio demasiado pronto, luego querer cambiar una nota | Quedarse en MIDI hasta el final; solo renderizar cuando el arreglo está cerrado |
| "Subir todo" para dar energía → barro y clipping | Energía = añadir/quitar capas y agudos; carving con EQ; anclar niveles |
| Dos elementos peleando en el sub-bass | Un solo dueño del sub por momento; sidechain el bajo al bombo; bajo en mono |
| Graves paneados | Todo lo grave al centro; los graves fuera de fase se cancelan en mono (móvil) |
| Ahogar la pista en reverb | Reverb como send moderado; el motor pone el espacio del juego [ver: unity/audio-unity] |
| MIDI 100% cuantizado → suena a máquina | Humanizar velocity y timing; cuantizar y luego des-cuantizar un poco |
| Aplastar la música a 0 dB "para que pegue" | Dejar headroom (~6–9 dB); el mix final se hace in-engine con SFX+voz encima |
| `fluidsynth` casi mudo | Default `-g 0.2`; subir `-g` con cuidado o normalizar con `sox gain -n -1` |
| `ffmpeg` falla al escribir OGG (`Unknown encoder libvorbis`) | Ese build no trae libvorbis: usar `sox in.wav out.ogg`, o `-c:a vorbis -strict experimental`, o `libopus` |
| Stems que se desfasan en el motor | Renderizar cada capa del mismo MIDI/tempo, alineados a la muestra; por código = 1 `.mid` por capa |
| Loop con hueco cada vuelta | OGG/WAV (nunca MP3), empalmar cola con inicio, cortar en el ataque, probar 10+ vueltas [ver: audio-a-juego §5] |
| Usar un loop de librería sin leer el alcance | Muchos no cubren "sync"/in-game; verificar la licencia y registrarla antes de meterlo |
| Renderizar un `.mid` de música clásica y usar ese audio como "libre" | La composición puede ser PD, pero renderiza TU audio; una grabación ajena tiene copyright [ver: crear-musica] |

## Fuentes

- **mido — MIDI Objects for Python** (mido.readthedocs.io) — API `MidiFile`/`MidiTrack`/`Message`/`MetaMessage`, `time` como delta en ticks, `bpm2tempo`, `ticks_per_beat`. **Verificado ejecutando mido 1.3.3** en esta máquina (genera `.mid` válido: 2 pistas, TPB 480).
- **FluidSynth — Command Line Options** (fluidsynth.org/api/CommandLineOptions.html) — `-F/--fast-render`, `-r/--sample-rate`, `-g/--gain` (0<g<10, default 0.2), `-O/--audio-file-format`, `-T/--audio-file-type`, `-i/--no-shell`, `-n/--no-midi-in`, `-R/--reverb`, `-C/--chorus`. **Verificado con `fluidsynth --help` (runtime 2.5.6)** y renderizando MIDI→WAV 44.1k/16-bit estéreo.
- **SoX — Sound eXchange docs** (sox.sourceforge.net/sox.html) — efectos `gain -n`, `highpass`, `trim`, `fade`, `reverb`, `tempo`, `stats`, `--i`, salida `.ogg`. **Verificado ejecutando sox** (normalización a `Pk lev dB -1.00`, `RMS -21.54`, DC offset 0).
- **FFmpeg — Encoders** (ffmpeg.org/ffmpeg-codecs.html) — `libvorbis`/`vorbis`/`libopus`; en el build local `libvorbis` ausente, `vorbis` (experimental) y `libopus` presentes. **Verificado con `ffmpeg -encoders`.**
- **General MIDI 1 — Sound Set & Percussion Map** (MIDI Manufacturers Association, midi.org) — 128 programas nombrados (0-indexados en program change) y mapa de percusión en canal 10 (36 kick, 38 snare, 42 hi-hat…). Teoría musical estándar.
- **SuperCollider Documentation** (doc.sccode.org) — `SynthDef`, `Out.ar`, `EnvGen`, render offline (Score/NRT). API estándar; **no ejecutado en esta pasada** (sclang no instalado aquí).
- Rutas para conseguir música, licencias (CC0/CC-BY/NC/SA), DAWs y sus costes, IA generativa: [ver: crear-musica], [ver: herramientas-recursos-audio].
- Acabado game-ready, mono/estéreo, dither, loops zero-crossing, loudness in-engine: [ver: audio-a-juego].
- Teoría (escalas/acordes/tensión), mezcla de todo el juego, adaptividad y middleware: [ver: teoria-musica-juegos], [ver: direccion-audio-mezcla], [ver: musica-adaptativa], [ver: middleware-fmod-wwise], [ver: gamedev/audio].
