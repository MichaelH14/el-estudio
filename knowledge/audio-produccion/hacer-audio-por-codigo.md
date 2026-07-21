# Hacer audio por código: el stack del agente

> **Cuando cargar este archivo:** cuando el agente tiene que GENERAR audio de un juego SIN GUI — sintetizar SFX, componer música, renderizar y convertir — desde la terminal, por código, sin abrir un DAW ni un generador web. Es la guía operativa (el equivalente de un `blender-mcp-operativo` pero para audio): qué herramientas headless usar, los comandos EXACTOS, y cómo verificar el resultado cuando no tienes oídos. El CRAFT de qué SFX/música producir y con qué vías (síntesis, foley, biblioteca, IA, contratar) está en [ver: crear-sfx] y [ver: crear-musica]; el catálogo de herramientas con GUI y sus licencias en [ver: herramientas-recursos-audio]; el acabado/entrega en [ver: audio-a-juego]; la teoría musical traducible a números en [ver: teoria-musica-juegos]; la síntesis pro desde osciladores en [ver: sintesis-y-diseno-sonido]; la teoría de por qué suena así en [ver: gamedev/audio]; la implementación en Unity en [ver: unity/audio-unity]. Aquí va SOLO el CÓMO por código.

## Qué resuelve este archivo

Un agente no puede clicar sliders en jsfxr ni arrastrar clips en un DAW, pero SÍ puede escribir comandos y código. Con cuatro binarios de línea de comandos (todos gratis, todos headless) se puede fabricar el 100% del audio de un juego chico: SFX sintéticos, música MIDI renderizada con un soundfont, y las conversiones de formato — sin tocar una interfaz gráfica. Este flujo produce assets reales, no maquetas.

⚠️ **Estado verificado:** el stack de abajo se instaló y se PROBÓ generando audio real (una pieza musical I–V–vi–IV con piano + cuerdas, y 3 SFX: láser, explosión y más) el 2026-07-21. Los comandos de este archivo son los reales usados, no plantillas inventadas. **Re-verificado por ejecución directa en auditoría posterior (mismo día):** cada receta de SFX de este archivo, el mix (`-m`), la cadena `norm`/`channels 1`, y el pipeline completo `mido`→`fluidsynth`→`ffmpeg`/`ffprobe` se corrieron de punta a punta y produjeron WAV/MP3 válidos con la duración y los parámetros esperados. Si dudas de un flag concreto en tu máquina: `man sox`, `sox --help`, `fluidsynth --help`.

## El stack (headless, gratis)

| Herramienta | Rol | Instala | Qué hace por código |
|---|---|---|---|
| **SoX** (Sound eXchange) | Síntesis y edición de SFX | `brew install sox` | Genera tonos/ruido/barridos y les aplica envolventes y efectos, todo en un comando. "La navaja suiza del audio de terminal" |
| **FluidSynth** | Render MIDI → audio | `brew install fluid-synth` | Toma un `.mid` + un soundfont y saca un WAV: convierte notas en sonido de instrumento real |
| **mido** (Python) | Escribir MIDI por código | `pip install mido` | Construye el archivo `.mid` nota a nota desde Python (program_change, note_on/off) |
| **ffmpeg** | Conversión de formato | `brew install ffmpeg` | WAV↔MP3↔OGG, resample, recorte; también `ffprobe` para inspeccionar |
| **Soundfont GM** | Banco de instrumentos | viene con distros / se baja | Un `.sf2`/`.sf3` General MIDI (p. ej. **FluidR3Mono** o **FluidR3_GM**) en la ruta estándar de soundfonts del sistema. FluidSynth lo necesita para sonar |

- ⛔ Instalar CLIs por **brew**, no npm [ver: herramientas-recursos-audio]. `mido` por pip/pipx en un venv.
- El soundfont GM es el que decide el TIMBRE de la música MIDI. Un GM completo (~140 MB) suena mejor que uno mono/comprimido; para prototipo cualquiera sirve. La ruta estándar de soundfonts del sistema evita pasar el path completo.
- Este stack cubre **SFX sintéticos + música orquestal/MIDI**. Lo que NO cubre: foley/grabación real [ver: foley-grabacion], síntesis pro desde osciladores (ver más abajo, upgrade), y edición fina con GUI [ver: herramientas-recursos-audio].

## El modelo mental: dos caminos + verificación ciega

```
SFX      →  SoX synth   →  .wav        ──┐
MÚSICA   →  mido → .mid → FluidSynth   →  .wav ──┼→ ffprobe (validar) → normalizar → .mp3 → HUMANO juzga
                                          ──┘        [audio-a-juego]              [import: unity/audio-unity]
```

Regla base: **el agente monta el andamiaje, el humano juzga el sonido.** El agente no oye — puede garantizar que el archivo es válido (formato, duración, canales, que no está en silencio ni clippeado), pero NO si "suena bien". Ese veredicto lo da siempre un humano escuchando el MP3. Ver §Verificación sin oídos.

---

## 1. SFX por código con SoX

### Anatomía de un comando

```
sox -n  salida.wav  synth <dur> <tipo> <freq>  <efecto1> <efecto2> ...
     │      │          │                          │
   input  output    generador                efectos encadenados (en orden)
   nulo
```

- `-n` = **input nulo**: no lees un archivo, generas desde la nada.
- `synth <dur> <tipo> <freq>` = sintetiza `<dur>` segundos de una onda `<tipo>` a `<freq>` Hz.
- **Barrido de frecuencia:** `<freq1>-<freq2>` hace un sweep (glissando) de freq1 a freq2. Es la clave de láseres, saltos y powerups.
- Todo lo que va DESPUÉS del `synth` son efectos que se aplican en cadena, en orden. El orden importa (filtrar antes o después del fade cambia el resultado).

### Tipos de onda del `synth`

| Tipo | Carácter | Uso típico |
|---|---|---|
| `sine` | Puro, limpio | Blips, tonos de UI, láser suave |
| `square` | Hueco, retro 8-bit | Chiptune, coin, jump clásico |
| `triangle` | Suave, flauta-ish | Tonos dulces, melodías simples |
| `sawtooth` | Áspero, brillante | Zumbidos, motores, agresivo |
| `trapezium` / `pulse` | Entre square y saw | Timbres retro variados |
| `whitenoise` | Ruido plano (todas las frecuencias) | Explosiones, viento, impactos, hi-hats |
| `pinknoise` / `brownnoise` | Ruido con más graves | Truenos, mar, rumble más "natural" |

### Envolvente: el efecto `fade`

`fade <tipo> <fade-in> [<duración-total> [<fade-out>]]`

- `<tipo>`: `q` cuarto de seno, `h` medio seno, `t` lineal/triangular, `l` logarítmico, `p` parábola invertida. `h` es el más usado para SFX (ataque y cola suaves).
- `fade h 0 0.3 0.25` = tipo h, **sin** fade-in (0), termina a los **0.3 s**, con **0.25 s** de fade-out. El fade-out largo da la cola que muere natural — evita el "click" de corte seco [ver: audio-a-juego §5].

### Efectos encadenables (los que más se usan)

| Efecto | Sintaxis | Para qué |
|---|---|---|
| `lowpass <Hz>` | `lowpass 700` | Quita agudos → sonido más "grande/oscuro" (explosión) |
| `highpass <Hz>` | `highpass 300` | Quita graves → sonido más "fino/lejano" |
| `overdrive <gain> <colour>` | `overdrive 20 20` | Distorsión, saturación, "sucio" |
| `reverb [<%>]` | `reverb 50` | Espacio (usar con moderación; el motor espacializa [ver: unity/audio-unity]) |
| `echo`/`echos` | `echo 0.8 0.9 60 0.4` | Eco, ecos múltiples |
| `tremolo <Hz> <depth>` | `tremolo 15 40` | Vibrato de amplitud, "wobble" de powerup |
| `pitch <cents>` | `pitch -300` | Sube/baja tono sin cambiar duración (variantes) |
| `bend` | `bend 0,300,.3` | Glissando aplicado a un sonido ya generado |
| `norm [<dBFS>]` | `norm -3` | Normaliza el pico a -3 dBFS (nivel de entrega [ver: audio-a-juego §4]) |
| `gain <dB>` / `vol <factor>` | `gain -6` | Sube/baja volumen |
| `trim <inicio> [<dur>]` | `trim 0 0.3` | Recorta |
| `pad <seg>` | `pad 0 0.5` | Añade silencio (cola/pre-roll) |

### Recetas verificadas (comandos reales)

| SFX | Comando | Idea |
|---|---|---|
| **Láser / disparo** | `sox -n laser.wav synth 0.3 sine 1400-300 fade h 0 0.3 0.25` | Barrido descendente rápido = "pew". Verificado |
| **Explosión / boom** | `sox -n boom.wav synth 0.7 whitenoise fade h 0 0.7 0.5 lowpass 700` | Ruido + lowpass = graves sin agudos = "grande". Verificado |
| **UI blip / click** | `sox -n blip.wav synth 0.08 sine 800 fade h 0 0.08 0.05` | Tono corto y suave. El sonido que suena 200×/sesión [ver: crear-sfx] |
| **Salto / jump** | `sox -n jump.wav synth 0.2 square 300-900 fade h 0 0.2 0.05` | Barrido ASCENDENTE + square = retro |
| **Powerup / buff** | `sox -n powerup.wav synth 0.5 square 400-1400 fade h 0 0.5 0.1 tremolo 12 30` | Ascenso largo + tremolo = "positivo/mágico" |
| **Daño / hurt** | `sox -n hurt.wav synth 0.15 whitenoise fade h 0 0.15 0.1 lowpass 1200` | Ruido corto y filtrado = impacto seco |
| **Coin (dos tonos)** | `sox -n a.wav synth 0.07 square 988` ; `sox -n b.wav synth 0.5 square 1319 fade h 0 0.5 0.4` ; `sox a.wav b.wav coin.wav` | Coin clásico = 2 notas (B5→E6). Se concatenan listando ambos archivos |

El patrón general es siempre: **`synth <dur> <tipo> <freq[-freq2]> fade <envolvente> <efectos>`**. Para variar un mismo sonido: cambiar `<freq>`, invertir el barrido, o añadir `pitch ±cents`.

### Layering y variación por código

- **Mezclar capas (sumar):** `sox -m ataque.wav cuerpo.wav cola.wav impacto.wav` — la `-m` mezcla (suma) los inputs. La regla de 3 capas (ataque + cuerpo + cola) de [ver: crear-sfx] se ejecuta con un solo `-m`.
- **Concatenar en el tiempo:** listar archivos sin `-m`: `sox parte1.wav parte2.wav junto.wav`.
- **Variantes horneadas:** un `for` que reexporta con `pitch` distinto (±100/±200 cents) o `vol` para generar `_01.._04` [ver: audio-a-juego §7]. Pero preferir variación en runtime en el motor [ver: unity/audio-unity].
- **Limpieza de entrega en el mismo comando:** añadir `norm -3` al final del chain para dejar el pico a nivel; `channels 1` para forzar mono en SFX 3D [ver: audio-a-juego §3].

---

## 2. Música por código: mido → FluidSynth → ffmpeg

### Paso A — Escribir el MIDI con mido

MIDI no es audio: es una partitura (qué nota, cuándo, con qué instrumento). mido la construye desde Python.

```python
import mido
from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo

mid = MidiFile()                       # ticks_per_beat por defecto = 480
piano = MidiTrack(); mid.tracks.append(piano)
piano.append(MetaMessage('set_tempo', tempo=bpm2tempo(96)))
piano.append(Message('program_change', program=0, time=0))   # 0 = Acoustic Grand Piano

TPB = mid.ticks_per_beat                # 480 ticks = 1 negra
WHOLE = TPB * 4                         # acorde de 1 compás

# I–V–vi–IV en Do mayor (acordes como listas de notas MIDI, C4=60)
prog = [[60,64,67], [67,71,74], [69,72,76], [65,69,72]]   # C  G  Am  F
for chord in prog:
    for n in chord:                     # note_on de las 3 notas a la vez (time=0)
        piano.append(Message('note_on',  note=n, velocity=72, time=0))
    for i, n in enumerate(chord):       # el primer note_off consume el tiempo del acorde
        piano.append(Message('note_off', note=n, velocity=0, time=WHOLE if i==0 else 0))

mid.save('pieza.mid')
```

Claves de mido (verificadas contra la doc):
- `time` es **delta en ticks** desde el evento anterior, no absoluto. Notas simultáneas → `time=0`; la duración vive en el `note_off`.
- `ticks_per_beat` (default 480) define la resolución: negra = 480 ticks, corchea = 240, etc.
- `note_off` con `velocity=0` equivale a soltar la nota (idéntico a `note_on velocity=0`).
- **Varias pistas** = varios `MidiTrack` en `mid.tracks` (una por instrumento). Ej.: segunda pista con `program=48` (String Ensemble 1) para las cuerdas.

### Instrumentos GM (`program_change`, 0-indexado)

| program | Instrumento | program | Instrumento |
|---|---|---|---|
| 0 | Acoustic Grand Piano | 48 | String Ensemble 1 |
| 4 | Electric Piano 1 | 56 | Trumpet |
| 24 | Nylon Guitar | 61 | Brass Section |
| 33 | Electric Bass (finger) | 73 | Flute |
| 40 | Violin | 80 | Square Lead (chip) |

- ⚠️ **Percusión = canal 9** (0-indexado; el "canal 10" de GM). En ese canal, la NOTA elige el sonido de batería (36 = bombo, 38 = caja, 42 = hi-hat cerrado) sin importar el `program`. En mido: `Message('note_on', note=36, channel=9, ...)`.
- `program_change` es por canal: instrumentos distintos → canales distintos o pistas distintas.

### Paso B — Renderizar a WAV con FluidSynth

```
fluidsynth -ni -g 0.8 -F out.wav -r 44100  <soundfont.sf3>  pieza.mid
```

| Flag | Significado |
|---|---|
| `-n` | No crear driver de MIDI de entrada (no escuchamos teclado) |
| `-i` | No entrar al shell interactivo (`-ni` juntos = modo batch puro) |
| `-g 0.8` | Ganancia global 0.8 (bajar si clippea; 1.0+ satura fácil) |
| `-F out.wav` | **Fast render (NRT, offline):** renderiza el MIDI a archivo lo más rápido posible, sin reproducir en tiempo real |
| `-r 44100` | Sample rate 44.1 kHz [ver: audio-a-juego §2] |
| orden | `fluidsynth [opciones] <soundfont> <midi>` — soundfont ANTES del MIDI |

El `-F` (`--fast-render`) es lo que lo hace apto para un agente: no espera a que "suene" en tiempo real, escribe el WAV de golpe. Sin `-F`, FluidSynth intentaría abrir un driver de audio y quedarse vivo.

### Paso C — Convertir a MP3 (o dejar WAV)

```
ffmpeg -i out.wav out.mp3          # para MANDAR al humano (ligero)
```

- El **master se archiva en WAV** (lossless); el MP3 es solo para que el humano lo escuche cómodo [ver: audio-a-juego §2].
- ⛔ **Nunca** entregar un LOOP en MP3: el encoder mete padding de silencio → gap en cada vuelta. Loops en WAV/OGG [ver: crear-musica, audio-a-juego §5].
- Para OGG: `ffmpeg -i out.wav -c:a libvorbis out.ogg`.

---

## 3. Aplicar la teoría musical por código

La teoría de escalas/acordes/progresiones [ver: teoria-musica-juegos] se vuelve aritmética de enteros MIDI. Base: **C4 = 60**; +1 = un semitono; +12 = una octava.

| Concepto | Traducción a código |
|---|---|
| Nota | Entero MIDI. `C4=60, C#4=61, D4=62 ... B4=71, C5=72` |
| Escala | La raíz + una lista de offsets. Mayor = `[0,2,4,5,7,9,11]`; menor natural = `[0,2,3,5,7,8,10]`; pentatónica menor = `[0,3,5,7,10]` |
| Acorde | Lista de notas. Tríada mayor = `raíz + [0,4,7]`; menor = `[0,3,7]`; 7ª dominante = `[0,4,7,10]` |
| Progresión | Lista de acordes. I–V–vi–IV en C = `[[60,64,67],[67,71,74],[69,72,76],[65,69,72]]` (el "four-chord song") |
| Tempo | `set_tempo=bpm2tempo(bpm)`; duración de nota en ticks = `ticks_per_beat * (4/valor)` |
| Melodía | Recorrer índices de la escala; grado→nota = `raíz + escala[grado % 7] + 12*(grado // 7)` |

Con esto, un helper de ~15 líneas genera cualquier progresión, la transporta (sumar N a todas las notas), o la vuelve menor (cambiar la lista de offsets). La progresión de tensión/combate, los stingers y los modos (dórico, frigio) de [ver: teoria-musica-juegos] son todos listas de offsets distintas — la maquinaria mido/FluidSynth no cambia.

---

## 4. Verificación sin oídos (el agente no escucha)

El agente NO puede juzgar si "suena bien". Puede y DEBE verificar que el archivo es técnicamente válido antes de mandarlo, y separar eso del juicio sonoro humano.

### Qué SÍ puede verificar el agente

| Comprobación | Comando | Qué confirma / bandera roja |
|---|---|---|
| Formato, duración, canales, sample rate | `ffprobe -v error -show_entries stream=codec_name,sample_rate,channels -show_entries format=duration -of default=noprint_wrappers=1 out.wav` | Que el WAV existe y tiene la duración/canales esperados. Duración 0 o inesperada = el render falló |
| Info rápida | `soxi out.wav` | Sample rate, canales, duración, bits — de un vistazo |
| ¿Silencio? ¿Clipping? | `sox out.wav -n stat` | Campos **Maximum amplitude** (≈0 = silencio → algo falló) y si el pico llega a 1.0 / hay recorte |
| Estadística de nivel | `sox out.wav -n stats` | RMS/peak dBFS; sirve para saber si hay que `norm` o si viene saturado |

- **Silencio = fallo, no éxito.** Un WAV de la duración correcta pero con amplitud máxima ≈0 significa que el soundfont no cargó, el MIDI estaba vacío, o el canal/instrumento no sonó. `sox stat` lo detecta sin oír. Output vacío ≠ éxito (regla general de verificación).
- Duración esperada: si compusiste 4 compases a 96 BPM en 4/4 → 4×4×(60/96) = 10 s. Si `ffprobe` dice 0.2 s, el `note_off` se escribió mal.

### Qué NO puede verificar (lo juzga el humano)

Si suena bien, si el timbre es el correcto, si la mezcla molesta, si el láser "se siente" a láser. **Siempre** enviar el MP3 al humano para el veredicto final [ver: dar copia accesible]. El agente entrega: el archivo válido + qué generó + cómo verificarlo; el humano aprueba el sonido. No declarar "quedó el SFX" — declarar "generé el WAV, válido (duración X, mono, pico -3 dB); escúchalo y dime".

---

## 5. Síntesis pro desde cero (upgrade — no instalado por defecto)

SoX sintetiza formas de onda básicas + efectos; alcanza para SFX retro/arcade. Para **diseñar cualquier sonido desde osciladores, filtros, envolventes y modulación por código** (el equivalente de un synth modular, todo scriptable y headless), el upgrade es:

| Herramienta | Qué es | Render headless | Nota |
|---|---|---|---|
| **SuperCollider** (`sclang`) | Lenguaje + servidor de audio para síntesis en tiempo real y **NRT (Non-Real-Time)** | `Score.recordNRT` renderiza a WAV sin tarjeta de sonido | Gratis, GPL. El más potente para diseño sonoro procedural [ver: sintesis-y-diseno-sonido] |
| **Csound** | Lenguaje de síntesis clásico (orquesta + score) | `csound -o out.wav proyecto.csd` renderiza offline | Gratis, LGPL. Muy estable para render por lotes |

Ambos permiten un pipeline puro-código para SFX que SoX no puede (FM, granular, físico). El detalle de diseño (osciladores, ADSR, filtros, modulación) va en [ver: sintesis-y-diseno-sonido]. Instalarlos solo si el juego pide un diseño sonoro que la síntesis básica de SoX no da.

---

## 6. Conectar a un DAW real (opción — requiere setup del usuario)

Para manejar un DAW como se maneja Blender por MCP (proyecto, pistas, plugins, mezcla programática):

| Vía | Scriptable | Coste / licencia | Realidad |
|---|---|---|---|
| **REAPER + ReaScript (Python/Lua)** | Sí, API completa | REAPER: eval 60 días; licencia con descuento / comercial [ver: crear-musica] | El DAW scriptable de facto. ReaScript maneja pistas, ítems, FX, render desde Python. Requiere que el usuario instale REAPER y habilite Python |
| **Ableton Live + `ableton-mcp`** | Sí, vía servidor MCP | ⚠️ **Ableton Live es de PAGO** (Intro/Standard/Suite). `ableton-mcp` es un proyecto MCP de terceros — **verificar su licencia y estado antes de depender** | Control de Live por MCP (crear clips, MIDI, escenas). No verificado en esta pasada; tratar precios/estado como a confirmar |
| **GarageBand** | **NO** | Gratis en Mac | ⛔ GarageBand **no es scriptable** (sin API/AppleScript útil para esto). No sirve para el flujo del agente |

- Este camino NO es necesario para producir audio de un juego chico — SoX + FluidSynth + mido lo cubren sin DAW. El DAW scriptable aporta mezcla/plugins profesionales cuando hay un humano que ya lo usa.
- Precisión de licencias: **verificar términos y precios vigentes** de REAPER/Ableton antes de comprometerse [ver: crear-musica]. `ableton-mcp` de terceros: leer su licencia. Nada de esto está instalado por defecto.

---

## 7. El pipeline completo del agente

```
1. GENERAR      SoX (SFX)  /  mido→FluidSynth (música)   →  .wav master
2. VERIFICAR    ffprobe/soxi/sox stat  → válido? duración/canales/no-silencio/no-clip
3. PREPARAR     norm, mono/estéreo, loop zero-cross, headroom   [ver: audio-a-juego]
4. CONVERTIR    ffmpeg → .mp3 para el humano  /  WAV|OGG para el motor
5. JUZGAR       humano escucha el MP3 y aprueba el SONIDO       (el agente NO oye)
6. ITERAR       ajustar freq/envolvente/instrumento y repetir 1–5
7. IMPORTAR     WAV final → Unity (mono SFX 3D, load type, mixer)  [ver: unity/audio-unity]
```

- Los pasos 3 y 7 NO se reinventan aquí: normalización/mono/loops/naming en [ver: audio-a-juego]; import/compresión/mixer en [ver: unity/audio-unity].
- El bucle 1→5→6 es donde vive el trabajo real: el agente genera rápido y barato, el humano filtra por oído, el agente corrige. Sin el paso 5 no hay "listo".

---

## Reglas prácticas

- [ ] Instalar el stack por **brew** (sox, fluid-synth, ffmpeg) y `mido` por pip en venv; ⛔ nunca npm.
- [ ] Confirmar que hay un **soundfont GM** en la ruta estándar antes de renderizar música; sin soundfont, FluidSynth saca silencio.
- [ ] SFX = `sox -n out.wav synth <dur> <tipo> <freq[-freq2]> fade <env> <efectos>`. Barrido `freq1-freq2` para láser/jump/powerup.
- [ ] Cerrar todo SFX con un `fade` (cola) para evitar el click de corte seco [ver: audio-a-juego §5].
- [ ] Explosión/impacto = `whitenoise` + `lowpass`; UI/blip = `sine`/`square` corto; el orden de efectos importa.
- [ ] Layering con `sox -m capa1 capa2 ... out.wav`; concatenar listando archivos sin `-m`.
- [ ] Música = mido escribe `.mid` (program_change GM + note_on/off con `time` en **ticks delta**) → `fluidsynth -ni -g 0.8 -F out.wav -r 44100 <sf> pieza.mid`.
- [ ] Recordar `-F` (fast-render) en FluidSynth: sin él intenta reproducir en tiempo real y se cuelga.
- [ ] Percusión GM = **canal 9** (0-indexado) y la NOTA elige el instrumento (36 bombo, 38 caja, 42 hi-hat).
- [ ] Traducir teoría a enteros: C4=60, escalas como offsets, acordes como listas, progresiones como listas de acordes [ver: teoria-musica-juegos].
- [ ] **Verificar SIEMPRE con `ffprobe`/`soxi`** que el archivo tiene la duración, canales y sample rate esperados antes de darlo.
- [ ] Chequear con `sox out.wav -n stat` que NO es silencio (amplitud máx ≈0 = fallo) ni está clippeado.
- [ ] Master en **WAV** (lossless); MP3 solo para mandar al humano; ⛔ nunca loop en MP3 (gap por padding) [ver: audio-a-juego].
- [ ] **El humano juzga el sonido.** El agente entrega archivo válido + evidencia de verificación, no un "quedó" sin escuchar nadie.
- [ ] Preparar antes de entregar: `norm -3`, mono para SFX 3D, headroom; el resto del acabado en [ver: audio-a-juego].
- [ ] Síntesis pro (FM/granular/físico) = upgrade a SuperCollider/Csound [ver: sintesis-y-diseno-sonido]; no instalados por defecto.
- [ ] DAW scriptable = REAPER+ReaScript (o Ableton+MCP, de pago); GarageBand NO es scriptable. Verificar licencias vigentes.
- [ ] Los assets generados por síntesis propia son **tuyos, sin problema de licencia** — a diferencia de bibliotecas/IA [ver: crear-sfx, herramientas-recursos-audio].

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| FluidSynth saca silencio o error | Falta el soundfont o la ruta está mal; pasar el `.sf2/.sf3` explícito antes del `.mid` |
| FluidSynth se queda colgado "sonando" | Falta `-F out.wav` (fast render); sin él intenta reproducir en tiempo real. Añadir `-ni -F` |
| WAV con la duración correcta pero SILENCIO | Verificar con `sox stat` (amplitud máx ≈0). MIDI vacío, instrumento en canal equivocado o `note_off` mal → el render "funcionó" pero no suena |
| SFX con un "click" al final | Falta cola: cerrar el `synth` con `fade h 0 <dur> <fade-out>` |
| Notas de un acorde suenan una tras otra, no juntas | En mido, las simultáneas van con `time=0`; la duración va en el `note_off`, no en cada `note_on` |
| La música dura una fracción de lo esperado | `time` en mido es **delta en ticks**, no segundos ni absoluto; recalcular contra `ticks_per_beat` |
| El MP3 del loop tiene un "hipo" cada vuelta | MP3 mete padding → gap. Loops en WAV/OGG; MP3 solo para escucha del humano [ver: audio-a-juego §5] |
| Declarar "listo el SFX" sin que nadie lo escuchó | El agente no oye: verifica el archivo (ffprobe), pero el veredicto sonoro es del humano. Mandar el MP3 |
| SFX 3D exportado en estéreo | `channels 1` (o `norm ... channels 1`) en el chain; el paneo lo hace el motor [ver: audio-a-juego §3, unity/audio-unity] |
| Batir la cabeza con SoX para un timbre complejo (FM, granular) | SoX no llega ahí: subir a SuperCollider/Csound [ver: sintesis-y-diseno-sonido] |
| Intentar scriptear GarageBand | No tiene API útil; usar REAPER+ReaScript si hace falta un DAW por código |
| Ganancia de FluidSynth muy alta → mezcla saturada | Bajar `-g` (0.5–0.8); verificar clipping con `sox stats` y `norm` al final |

## Fuentes

- **SoX (Sound eXchange) — manual/wiki** (sox.sourceforge.net, `man sox`) — efecto `synth` (tipos sine/square/triangle/sawtooth/trapezium/whitenoise/pinknoise/brownnoise; barrido `freq1-freq2`), efecto `fade` (tipos q/h/t/l/p; orden fade-in/stop/fade-out), filtros `lowpass`/`highpass`, `norm`, `overdrive`, `reverb`, `tremolo`, `pitch`, input nulo `-n`, `soxi`, `stat`/`stats`. Sintaxis verificada contra la doc oficial **y re-ejecutada línea por línea en auditoría posterior** (todas las recetas de SFX, `-m` mix, `norm`/`channels 1`): todas produjeron WAV válidos.
- **FluidSynth — Command Line Options** (fluidsynth.org/api/CommandLineOptions.html) — `-n/--no-midi-in`, `-i/--no-shell`, `-g/--gain`, `-F/--fast-render`, `-r/--sample-rate`, orden `fluidsynth [opts] <soundfont> <midi>`. Verificado contra la doc y contra `fluidsynth --help` real; el pipeline `mido`→`fluidsynth`→`ffmpeg` completo se re-ejecutó en auditoría posterior con un soundfont GM real, sin errores.
- **mido — MIDI Objects for Python** (mido.readthedocs.io) — `MidiFile`, `MidiTrack`, `Message('program_change'/'note_on'/'note_off')`, `time` como delta en ticks, `ticks_per_beat` (default 480), `MetaMessage('set_tempo')`, `bpm2tempo`. Verificado contra la doc y contra una ejecución real del snippet de este archivo (mido 1.3.3): generó un MIDI de 10 s exactos para 4 compases a 96 BPM, como predice la fórmula de §4.
- **General MIDI (GM 1) — Sound Set & Percussion Map** (MIDI Manufacturers Association, midi.org) — números de instrumento (0 Piano, 48 String Ensemble 1, etc.), canal 10/percusión, mapa de batería (36 kick, 38 snare, 42 closed hi-hat). Estándar.
- **FFmpeg — Documentation** (ffmpeg.org/documentation.html) — `-i`, conversión WAV↔MP3/OGG (`-c:a libvorbis`), `ffprobe -show_entries`. Estándar.
- **Notación MIDI de altura / scientific pitch (C4 = 60)** — convención estándar de teoría→MIDI usada en [ver: teoria-musica-juegos].
- **SuperCollider** (supercollider.github.io) — `sclang`, render NRT (`Score.recordNRT`) para síntesis headless. Base de [ver: sintesis-y-diseno-sonido].
- **Csound** (csound.com) — render offline `csound -o out.wav proyecto.csd`.
- **REAPER — ReaScript** (reaper.fm; cockos.com/reaper/sdk/reascript) — API Python/Lua para automatizar el DAW; licencia y precios en [ver: crear-musica]. `ableton-mcp` (proyecto de terceros) y Ableton Live (de pago): **estado/licencia NO verificados en esta pasada** — confirmar antes de depender.
- **FluidR3 / FluidR3Mono GM soundfont** — soundfont General MIDI libre comúnmente distribuido; usado como banco por defecto de FluidSynth.
- Nota de honestidad (Regla #0): la sintaxis de SoX/FluidSynth/mido/ffmpeg de este archivo fue re-ejecutada de punta a punta en auditoría posterior (2026-07-21) sobre el stack real instalado (sox 14.4.2, fluidsynth 2.5.6, mido 1.3.3, ffmpeg 8.0.1) — todos los comandos corrieron sin error y produjeron WAV/MP3 válidos. Lo NO verificado en ninguna pasada: la licencia/estado vigente de `ableton-mcp` (proyecto de terceros) y los precios actuales de REAPER/Ableton Live — tratar como a confirmar antes de depender de esa vía.
