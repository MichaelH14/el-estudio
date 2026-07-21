# Chiptune y música con trackers

> **Cuando cargar este archivo:** cuando el juego pide música "8/16-bit" — retro, arcade, pixel art [ver: arte-2d/pixel-art] — y hay que COMPONERLA o dirigirla: elegir el chip/estética (NES, Game Boy, C64), entender por qué se usa un TRACKER en vez del piano roll de un DAW, escribir melodía+bajo+arpegios+percusión dentro de pocos canales, aplicar los trucos clásicos (arpeggio rápido para acordes, slides, vibrato, duty cycle, echo por canal), y exportar al motor. La TEORÍA (funciones, adaptividad, silencio) vive en [ver: gamedev/audio]; la IMPLEMENTACIÓN en Unity en [ver: unity/audio-unity]; las RUTAS y LICENCIAS de música en general en [ver: crear-musica]; el catálogo de herramientas en [ver: herramientas-recursos-audio]; el acabado/loop/formato en [ver: audio-a-juego]; los SFX 8-bit (sfxr/Bfxr/ChipTone) en [ver: crear-sfx]. Aquí va el CRAFT específico del chiptune y el paradigma tracker.

## Regla previa: no repetir lo que ya está resuelto

- **De dónde sale la música y cómo se licencia** → [ver: crear-musica] (componer/CC/licenciar/IA/contratar) + [ver: herramientas-recursos-audio] (registro `CREDITS.md`). No se repite aquí la chuleta CC.
- **Producir stems + intro/loop, loops que empalman por la cola, headroom, WAV≠MP3** → [ver: crear-musica] y [ver: audio-a-juego]. El chiptune sigue esas mismas reglas de entrega.
- **Vertical layering / horizontal resequencing / stingers** → [ver: gamedev/audio]. El chiptune se hace adaptativo con las mismas técnicas (basta exportar cada canal/grupo como stem).
- Este archivo aporta la PROFUNDIDAD que falta: los chips como estética, el paradigma tracker, y las técnicas de composición que son propias del chiptune.

## 1. Qué es el chiptune y por qué encaja con el pixel art

Chiptune = música hecha con (o imitando) los **generadores de sonido programables** de las consolas/computadoras de los 80: formas de onda simples sintetizadas en tiempo real, no samples grabados. Igual que el pixel art, **la restricción ES el estilo** [ver: arte-2d/pixel-art §1]: pocos canales y formas de onda pobres obligan a decidir qué información sobrevive, y esa economía es la firma sonora.

| Paralelo pixel art ↔ chiptune | Visual | Audio |
|---|---|---|
| El límite deliberado | Resolución baja, cada píxel cuenta | Pocos canales, cada voz cuenta |
| La paleta contada | 16-32 colores globales | 3-5 canales / formas de onda fijas |
| El "grano" del hardware | Grilla de píxeles, sin antialias | Onda cuadrada/ruido, sin reverb nativo |
| La coherencia de época | Paleta NES ↔ tiles NES | Sonido 2A03 ↔ arte NES |

Por eso el chiptune es el default sonoro de lo retro/arcade/indie: comparte ADN de restricción con el pixel art, cuesta poco (una persona lo hace), pesa nada (KB), y evoca la época sin licenciar nada de terceros. La decisión de estilo (¿chiptune sí o no?, coherencia con el arte) se toma en dirección [ver: gamedev/arte-direccion]; aquí se ejecuta.

## 2. Los chips como estética (el vocabulario sonoro)

No hay que emular el hardware para sonar a chiptune, pero conocer los chips fija el vocabulario. Especificaciones **verificadas** contra NESdev / Pandocs-Wikipedia / docs del SID:

| Chip (máquina) | Canales | Voces / formas de onda | Firma sonora |
|---|---|---|---|
| **2A03 (NES / Famicom)** | **5** | 2× pulse (duty 12.5/25/50/75%), 1× triangle (32 pasos, 4-bit, **sin control de volumen**), 1× noise (LFSR pseudo-aleatorio), 1× DMC/DPCM (samples 1-bit delta, PCM 7-bit) | El sonido "Mario/Mega Man": pulsos brillantes, bajo de triángulo, percusión de ruido, drums sampleados en DPCM |
| **DMG (Game Boy)** | **4** | 2× pulse (canal 1 con **frequency sweep**, canal 2 solo volumen), 1× **wave channel** (waveform arbitraria en RAM = wavetable), 1× noise | Más "hueco/gris"; el wave channel permite timbres que el NES no tiene; mono por altavoz, estéreo por auriculares |
| **SID 6581/8581 (C64)** | **3** | 3 voces, cada una 4 formas (triangle, sawtooth, **pulse de ancho variable**, noise) + combinadas; **3 ADSR** (una por voz); **filtro multimodo** (LP/HP/BP); **ring modulation**; hard sync | El más "musical" de la era: ADSR real, filtro barredor, ring mod = timbres ricos con solo 3 voces |
| **SNES (S-SMP/S-DSP)** | 8 | Samples **BRLE comprimidos** con envelope + eco por hardware | Ya es sample-based, no "onda pura": el 16-bit "cálido" con reverb del SNES |
| **YM2612 (Genesis/Mega Drive)** | 6 FM (+PSG SN76489 de 4) | Síntesis **FM** (operadores) + 1 canal PCM | El otro 16-bit: FM metálica/agresiva, bajos gordos |

Regla operativa: **elegir el chip por la época que evoca el arte**, no al revés (§9). Para el 8-bit clásico → 2A03. Para lo "portátil/gris" → DMG. Para lo europeo/demoscene → SID. Para 16-bit → SNES (dulce) o Genesis/FM (agresivo).

### Las formas de onda, a nivel de estética

| Forma | Timbre | Uso típico |
|---|---|---|
| **Pulse / square** | Brillante, nasal; el **duty cycle** cambia el color (12.5% = fino/nasal, 50% = lleno/hueco) | Melodía, armonía, arpegios |
| **Triangle** | Suave, redondo, sordo | Bajo, líneas graves; en NES también el "kick" (caída rápida de pitch) |
| **Noise** | Ruido filtrable (blanco / metálico según periodo) | Percusión (hats/snare/kick), viento, explosiones, texturas |
| **Wavetable** (GB/PCE/SCC) | Cualquier waveform corta cargada en RAM; timbres imposibles para el pulse | Leads, bajos, pads "raros" |
| **FM** (YM2612/OPL) | Operadores modulándose → metálico, campanas, bajos densos | 16-bit, arcade, todo el rango |

## 3. Las restricciones que definen el sonido

Tres límites del hardware moldean cómo se compone chiptune. Aunque hoy se ignoren (chiptune "estética", §8), entenderlos es lo que separa un track que *suena* a chip de uno que solo usa ondas cuadradas:

1. **Presupuesto de canales.** Un 2A03 tiene 5 voces para melodía + armonía + bajo + percusión + drums. No sobra ninguna. La composición ES el reparto de canales (§5).
2. **Monofonía por canal.** Cada canal toca **una nota a la vez**. Un acorde de 3 notas ocupa 3 canales... o se finge con un **arpeggio** en uno solo (§6, el truco central del chiptune).
3. **Update rate por frame.** El chip se actualiza una vez por frame de video: **~60 Hz NTSC / ~50 Hz PAL**. Los efectos por tick (arpeggio, vibrato, slides) corren a ese ritmo. Por eso el arpeggio suena "shimmery/burbujeante": cicla las notas 60 veces por segundo. El tracker traduce su *Speed* (ticks por fila) y *Tempo* (BPM) a ese reloj.

## 4. Trackers: el paradigma (y por qué domina el chiptune)

Un **tracker** es un secuenciador donde el tiempo corre **de arriba hacia abajo** por una grilla de texto. No hay notas dibujadas: se escriben con el teclado. Es la anti-tesis del piano roll.

| | **Tracker** | **Piano roll (DAW)** |
|---|---|---|
| Tiempo | Vertical (arriba→abajo) | Horizontal (izq→der) |
| Nota | Texto en una celda (`C-4`) | Barra sobre una grilla de pitch |
| Entrada | **Teclado**, rapidísima | Ratón, dibujar |
| Estructura | **Patterns** (bloques) en un **order list** | Clips en un timeline |
| Un canal = | **una voz del chip** (mapeo directo) | una pista genérica |
| Efectos | **Comandos hex por celda** (mapean a trucos del chip) | Automatización con curvas |
| Determinismo | Total: la fila N siempre hace lo mismo | Depende de automatización/plugins |
| Archivo | Diminuto (.mod/.xm/.it/.ftm), o formato de chip (.nsf/.vgm) | Proyecto pesado + audio |

**Por qué el tracker domina el chiptune:**
- **Un columna = una voz del hardware.** El reparto de canales (§5) es literal: se ve el presupuesto de 5 voces del NES como 5 columnas.
- **Los comandos de efecto mapean a trucos del chip** (arpeggio, slide, duty) — el piano roll no tiene esos verbos nativos.
- **Granularidad por tick** = la resolución del chip (§3). Un arpeggio a 60 Hz se escribe con un comando, no automatizando a mano.
- **Exporta al formato nativo** (NSF, VGM, GBS) reproducible por el chip emulado — imposible desde un DAW.
- **Autenticidad + peso**: el módulo pesa KB y suena idéntico en cada máquina.

### Anatomía de una fila de tracker

Cada celda de un canal tiene columnas fijas. Formato típico (FamiTracker/Furnace): `C-4 00 F 3A0`

| Columna | Ejemplo | Qué es |
|---|---|---|
| **Note** | `C-4` | Nota + octava. `C-4`=Do 4ª octava, `===`/`---` = note-off/cut |
| **Instrument** | `00` | Índice del instrumento (define waveform/duty/envelope) |
| **Volume** | `F` | Volumen (hex, 0-F habitual) |
| **Effect** | `3A0` | Comando de efecto + parámetro (ver tabla §7) |

Las filas se agrupan en **patterns** (típico 16/32/64 filas); los patterns se ordenan en el **order list** (la estructura de la canción). *Speed* = ticks por fila (groove); *Tempo* = BPM. Menor Speed = más rápido/preciso.

## 5. Componer chiptune: el reparto de canales

Con 4-5 voces, componer chiptune es sobre todo **asignar roles a canales**. Plantilla clásica NES (2A03):

| Canal | Rol principal | Notas |
|---|---|---|
| **Pulse 1** | Melodía (lead) | Duty 50% = lleno, 25%/12.5% = más fino/cortante |
| **Pulse 2** | Armonía / contra-melodía / **arpegios** | Duty distinto al 1 para separarlos en la mezcla |
| **Triangle** | **Bajo** (+ kick) | Sin volumen: se "apaga" con note-off; el kick = nota grave con caída de pitch rápida |
| **Noise** | **Percusión** (hats/snare) | Periodos cortos = hats, largos = snare/tom; envelope de volumen para el ataque |
| **DPCM** | Drums sampleados / refuerzo | Sample real 1-bit; caro en ROM, se usa con criterio |

- **Regla de economía**: si falta un canal para un acorde, se resuelve con arpeggio (§6), no metiendo un canal que no existe.
- **Bajo + kick en el mismo triángulo**: truco NES clásico — el kick es una nota de triángulo muy grave con un pitch-drop de 1-2 filas; se intercala con el bajo. Requiere coreografiar note-offs.
- **Percusión con noise**: hi-hat = nota de noise corta con volumen que decae rápido; snare = noise de periodo medio + a veces una capa de pulse; se programa el envelope en el instrumento.
- Para música PARA el juego (loops que empalman, stems para adaptividad), aplican las reglas de [ver: crear-musica] y [ver: gamedev/audio]: cada canal se puede exportar como stem para vertical layering.

## 6. El truco de los arpegios (acordes con un canal)

El chiptune no puede tocar un acorde en un canal monofónico. La solución que define el sonido: **arpeggio rápido** — ciclar las notas del acorde a velocidad de tick (60 Hz) para que el oído las funda en un "acorde" burbujeante.

- Comando **`0xy`** (linaje MOD/ProTracker, presente en casi todos los trackers): en cada tick alterna **nota base → base+`x` semitonos → base+`y` semitonos**, y repite. Para un acorde mayor: `047` (0, +4 = 3ª mayor, +7 = 5ª justa). Menor: `037`. Séptima, sus2, etc., cambiando `x`/`y`.
- Suena "chip" precisamente porque a 60 Hz se oye el ciclado (no es un acorde limpio) — es una firma, no un defecto.
- Un solo canal de Pulse 2 haciendo `047`/`037` da toda la armonía de la pieza, liberando los otros canales.
- En FamiTracker/Furnace el arpeggio también puede vivir en el **instrumento** como una *secuencia* (macro) que corre por frame, además del comando `0xy` por celda.

## 7. Técnicas clásicas (comandos de efecto)

Los comandos heredan del **MOD/ProTracker**; las letras exactas varían por tracker (verificar en las docs del tracker concreto), pero el vocabulario es común:

| Efecto | Comando típico | Qué hace | Uso |
|---|---|---|---|
| **Arpeggio** | `0xy` | Cicla base/+x/+y semitonos por tick | Acordes en 1 canal (§6) |
| **Portamento up** | `1xx` | Sube el pitch `xx` por tick | Slides ascendentes, sirenas |
| **Portamento down** | `2xx` | Baja el pitch | Caídas, "power-down" |
| **Tone portamento** | `3xx` | Desliza (glide) hacia la nota nueva a velocidad `xx` | Legato, bajos que "resbalan" |
| **Vibrato** | `4xy` | Oscila el pitch (x=velocidad, y=profundidad) | Expresión en leads sostenidos |
| **Duty / waveform** | `Vxx` (FamiTracker) | Cambia el duty cycle del pulse (o modo de noise) | Timbre; barrer el duty = "PWM" falsa |
| **Volume slide** | `Axy` | Sube/baja volumen gradual | Fades, swells |
| **Set speed/tempo** | `Fxx` | Cambia Speed/Tempo | Ritmo, ritardando |
| **Jump / skip** | `Bxx`/`Dxx` | Salta de frame o corta la fila | Estructura, loops |

Técnicas compuestas propias del chiptune:
- **Duty cycle como color**: alternar 12.5%/25%/50% en el instrumento da "movimiento" tímbrico sin cambiar de canal; barrer el duty imita un pulse-width modulation.
- **Echo/delay por canal**: los chips no tienen reverb/delay nativo (salvo SNES). El eco se **finge** con un segundo canal que repite la melodía **desplazada 2-4 filas y a menor volumen**. Cuesta un canal — se usa cuando sobra voz.
- **Vibrato/pitch como ataque**: una micro-caída de pitch (`2xx` una fila) al inicio de la nota le da "punch"; el kick de triángulo del NES es exactamente esto.
- **Instrument macros** (FamiTracker/Furnace): el instrumento es una **secuencia por frame** de Volume / Arpeggio / Pitch / Duty. Un buen "instrumento" chiptune es media técnica: el ataque, el vibrato y el color viven ahí.

## 8. Herramientas (estado y para qué) — verificado 2026-07-21

| Herramienta | Chip(s) | Plataforma | Licencia / coste | Para qué |
|---|---|---|---|---|
| **Furnace** (tildearrow) | **Multi-chip** (200+ presets: NES+expansión, C64, GB/GBA, Virtual Boy, Genesis/YM2612, YM2151, AY-3-8910, SN76489, PCE, SCC…), hasta 128 canales | Win/Mac/Linux | **GPLv2+/GPLv3, gratis, open source** | **El default moderno.** Compatible con módulos DefleMask, exporta VGM/ZSM/audio. Lo más completo y activo |
| **DefleMask** | Genesis, SMS(+FM), GB, PCE, NES(+VRC7,+FDS), C64, Arcade, NeoGeo, MSX2 | Win/Mac/móvil | **De pago** (Steam/App/Play); versión **legacy 32-bit gratis** (demo) | El pionero multi-sistema; hoy Furnace lo cubre y supera siendo gratis. Exporta VGM/WAV/ROM/vídeo |
| **Dn-FamiTracker** | NES/Famicom (2A03, VRC7, FDS, N163, OPLL) | Windows | **GPLv3+, gratis, open source** | **El estándar NES vivo.** Fork activo de 0CC-FamiTracker (**0CC sin releases desde 2018-05, no usar como base nueva**). Exporta **NSF** |
| **0CC-FamiTracker** | NES | Windows | Gratis, open source (**no archivado en GitHub, pero sin actividad desde 2018**) | Histórico; sus features se continuaron en Dn-FamiTracker. Para proyectos legacy |
| **LSDj (Little Sound Dj)** | Game Boy (4 canales) | GB real (flashcart) / emulador (BGB, SameBoy) | **Gratis + donación voluntaria** | Composición GB "de verdad", corre en hardware. Cultura chiptune en vivo. Nintendo no lo autoriza (irrelevante si renderizas a WAV; relevante si distribuyes ROM) |
| **BeepBox** (John Nesky) | "Chip" web (no un chip real) | Web | **MIT; no reclama la titularidad de las canciones** | Melodía/loop en minutos, sin instalar; canción en la URL; exporta WAV+MIDI. El más fácil para empezar |
| **JummBox** (fork de BeepBox) | Web | Web | Open source (verificar LICENSE del repo) | BeepBox con más instrumentos/efectos; mismo flujo web |
| **Bosca Ceoil Blue** | Sintes tipo chip (step sequencer) | Win/Mac/Linux/Web | **MIT, gratis, open source** (Godot 4.3; v3.1.2, 2025) | Port moderno del Bosca Ceoil de Terry Cavanagh; ultra-beginner, sin trackear |
| **OpenMPT / MilkyTracker** | Módulos (MOD/XM/IT/S3M) + samples/VST | Win (OpenMPT) / multi (Milky) | Gratis, open source | Tracker "clásico" sample-based; útil si mezclas chip con samples propios [ver: herramientas-recursos-audio] |

Elección rápida: **empezar sin fricción** → BeepBox / Bosca Ceoil Blue. **Chiptune real multi-chip** → **Furnace** (gratis, cubre casi todo). **NES puro con NSF** → **Dn-FamiTracker**. **Game Boy en hardware** → LSDj. Las herramientas son mayormente permisivas y **tu composición es tuya**; el riesgo de licencia solo aparece con **samples/soundfonts importados** al tracker (misma regla que loops en [ver: crear-musica]) — cada sample importado, una fila en `CREDITS.md` [ver: herramientas-recursos-audio].

## 9. Export para el juego

Dos caminos; para un juego real casi siempre el primero:

| Vía | Cómo | Cuándo |
|---|---|---|
| **Render a WAV/OGG** | Exportar la pieza a audio desde el tracker (todos lo hacen) y tratarla como cualquier música: loop, headroom, formato | **Default para un motor moderno** (Unity/Godot/web). El motor no necesita saber que es chiptune |
| **Formato de chip** (NSF/VGM/GBS/SID) | El motor emula el chip y toca el registro-log en tiempo real | Autenticidad extrema, tamaño mínimo, o para plataformas/fantasy consoles que lo soportan |
| **Módulo tracker** (.mod/.xm/.it) | Reproducir el módulo con una librería (p.ej. libopenmpt) | Peso mínimo + música generativa; **el soporte nativo del engine varía — verificar** (no asumir que Unity importa módulos) |

- El acabado (cortar el loop en zero-crossing, empalmar la cola, headroom, WAV≠MP3, verificar 10+ vueltas) es idéntico al de cualquier música → [ver: audio-a-juego]. El chiptune renderizado no es especial en la entrega.
- Para música **adaptativa**: exportar cada canal (o grupo: melodía / armonía / bajo / percusión) como **stem alineado a la muestra** y hacer vertical layering [ver: gamedev/audio, crear-musica]. Furnace/FamiTracker permiten mutear canales y renderizar por separado.
- Implementación en el motor (AudioSource, PlayScheduled para intro+loop, mixer, móvil) → [ver: unity/audio-unity].

## 10. Chiptune moderno vs purista

| | **Purista (chip real)** | **Estética chiptune (libertad de DAW)** |
|---|---|---|
| Restricción | Canales/ondas del chip real; corre/emula en hardware | Usa los sonidos, ignora los límites |
| Canales | Fijos (5 NES, 4 GB, 3 SID) | Ilimitados |
| Post-proceso | Ninguno (salvo el del chip: SID filter, SNES reverb) | Reverb, delay, EQ, sidechain, compresión libres |
| Formato | NSF/VGM/SID/GBS, autenticidad total | WAV/OGG; a veces chip + batería real/samples ("chip-hop", nintendocore) |
| Herramienta | FamiTracker/LSDj/Furnace en modo chip | Furnace/DAW + VST de chip (Plogue chipsynth, Magical 8bit) |
| Cuándo | El juego evoca 8-bit "de verdad", jam retro, cred chiptune | La mayoría de indies: quieren el *sabor* 8-bit con producción moderna |

Ninguno es "mejor": es una decisión de dirección. La mayoría de juegos indie "chiptune" son **estética con libertad** (chip + reverb + más de 5 canales). Ser purista es una declaración; costear la autenticidad (probar en hardware, respetar el presupuesto de canales) solo vale si el juego lo pide.

## 11. El puente con el pixel art (coherencia audio↔visual)

El error de coherencia más común: arte 8-bit con música que "hace trampa" de fidelidad, o al revés. La regla es **igualar el nivel de restricción del audio al del arte** [ver: arte-2d/pixel-art] [ver: arte-2d/fundamentos-2d]:

| Arte visual | Audio coherente |
|---|---|
| Pixel art NES (paleta ~54 colores, tiles 8×8, sprites 16px) | 2A03 purista o casi (5 canales, ondas puras) |
| Game Boy (4 tonos verdes) | DMG (4 canales, wave channel), o su look mono/gris |
| Pixel art 16-bit (SNES/Genesis, 32px, más colores) | SNES sample-based (dulce) o Genesis/FM (agresivo), o chiptune-estética con reverb |
| Pixel art HD moderno (64px+, cientos de colores, Hyper Light/Dead Cells) | Chiptune-estética con libertad total, o híbrido chip + instrumentos reales — **NO** un NSF purista (leería como mismatch) |

- **Los canales son la "resolución" del audio**: pocos canales/ondas puras = el equivalente sonoro de baja resolución + paleta contada. Subir la fidelidad visual sin subir la sonora (o viceversa) rompe la ilusión igual que mezclar dos densidades de píxel [ver: arte-2d/pixel-art §2].
- **La época manda**: si el arte cita al NES, la música cita al 2A03, no al SNES. La coherencia de época audio↔visual es lo que hace "creíble" el retro [ver: gamedev/arte-direccion].
- Los **SFX** del juego deben vivir en el mismo mundo: generadores 8-bit tipo sfxr/Bfxr/ChipTone [ver: crear-sfx] combinan con chiptune; un SFX foley realista sobre música 2A03 chirría.

## 12. Runbook: un loop chiptune de cero al juego

1. **Definir chip/estética** por coherencia con el arte (§11): p.ej. 2A03 si es pixel art NES. Decidir purista vs estética (§10).
2. **Herramienta**: Furnace (multi-chip gratis) o Dn-FamiTracker (NES+NSF); BeepBox/Bosca Ceoil si es un loop rápido de menú.
3. **Repartir canales** (§5): Pulse1=melodía, Pulse2=armonía/arps, Triangle=bajo(+kick), Noise=percusión.
4. **Instrumentos**: definir duty/envelope/macro de cada voz (el ataque y el color viven en el instrumento, §7).
5. **Escribir el pattern**: melodía; luego bajo; luego armonía como **arpeggio `0xy`** (§6); luego percusión de noise. Ajustar Speed/Tempo.
6. **Estructura loopeable**: order list con intro (una vez) + loop; que la última fila fluya a la primera [ver: crear-musica].
7. **Adaptativo (si aplica)**: mutear y renderizar cada canal/grupo como **stem alineado** [ver: gamedev/audio].
8. **Export**: render a **WAV** (48 kHz, headroom) para el motor; o NSF/VGM si se emula el chip (§9).
9. **Acabado**: cortar el loop en zero-crossing, empalmar la cola, verificar **10+ vueltas** [ver: audio-a-juego].
10. **Import + implementar** en Unity (loop, PlayScheduled intro→loop, mixer) [ver: unity/audio-unity]; **registrar licencia** de cualquier sample importado [ver: herramientas-recursos-audio].

## Reglas prácticas

1. Elegir el chip por la **época que evoca el arte** (§11), no por gusto suelto; coherencia audio↔visual [ver: arte-2d/pixel-art].
2. Tratar el **presupuesto de canales** como el presupuesto real: 5 voces NES = melodía + armonía + bajo + percusión + drums, ni una más.
3. Acordes con **arpeggio `0xy`** en un canal (§6), nunca "inventar" un canal que el chip no tiene.
4. Usar el **triangle para el bajo** (y el kick con pitch-drop); noise para percusión con envelope de ataque.
5. El **duty cycle** es color: alternarlo/barrerlo da movimiento sin gastar canal.
6. Distinguir los canales en la mezcla con **duties distintos** (Pulse1 vs Pulse2).
7. **Echo/delay = un canal repetido** desplazado 2-4 filas a menor volumen; solo si sobra voz (el chip no tiene reverb).
8. El **instrumento es media técnica**: ataque, vibrato y color viven en su macro por frame (FamiTracker/Furnace).
9. Herramienta según fricción: **Furnace** (multi-chip gratis) el default; **Dn-FamiTracker** para NES+NSF; **BeepBox/Bosca Ceoil** para empezar; **0CC sin desarrollo desde 2018**, no basar proyectos nuevos en él.
10. **Render a WAV/OGG** para un motor moderno; NSF/VGM solo si emulas el chip (§9). No asumir que el engine importa módulos: verificar.
11. Loop chiptune se acaba igual que cualquier música: zero-crossing, empalme de cola, WAV≠MP3, **10+ vueltas** [ver: audio-a-juego].
12. Música adaptativa: exportar **cada canal/grupo como stem alineado**; el chiptune hace vertical layering igual [ver: gamedev/audio].
13. Igualar la **fidelidad sonora a la visual** (§11): NES-art→2A03; HD-pixel→chiptune-estética, no NSF purista.
14. Tu **composición es tuya**; el único riesgo de licencia son **samples/soundfonts importados** al tracker → una fila en `CREDITS.md` [ver: herramientas-recursos-audio].
15. Guardar el **proyecto fuente** (.ftm/.fur/.mod) además del WAV, para reeditar sin recomponer.
16. Purista vs estética (§10) es decisión de **dirección**, tomada antes de componer, no a mitad.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Arte NES con música que usa 12 canales y reverb (mismatch de fidelidad) | Igualar restricción audio↔visual; NES-art → pocos canales, ondas puras (§11) |
| Querer un acorde en un canal monofónico | Arpeggio `0xy` (§6): cicla las notas del acorde por tick |
| Pulse 1 y Pulse 2 con el mismo duty → se empastan | Duties distintos para separarlos en la mezcla |
| Olvidar que el **triangle no tiene volumen** y esperar dinámica ahí | La dinámica del bajo se hace con note-offs/pitch, no con volumen |
| Buscar reverb/delay nativo en el chip | No existe (salvo SNES): fingir el eco con un canal repetido desplazado |
| Basar un proyecto nuevo en **0CC-FamiTracker** | Sin releases desde 2018 (no archivado en GitHub, pero sin desarrollo); usar **Dn-FamiTracker** (fork activo) |
| Pagar DefleMask sin mirar alternativas | **Furnace** es gratis (GPL), multi-chip y más activo; cubre lo mismo y más |
| Componer sin repartir canales primero (todo en Pulse 1) | Definir el rol de cada voz antes de escribir notas (§5) |
| Percusión de noise plana (sin ataque) | Envelope de volumen en el instrumento: decae rápido = hat, medio = snare |
| Exportar el loop a **MP3** | MP3 mete padding = hueco en cada vuelta; WAV/OGG y verificar 10+ vueltas [ver: audio-a-juego] |
| Meter samples/soundfonts sin licencia al tracker | Cada sample importado tiene su licencia; registrarla o no usarlo [ver: crear-musica] |
| Asumir que Unity importa el módulo .xm/.it nativamente | Verificar el soporte del engine; lo seguro es renderizar a WAV/OGG (§9) |
| Ser purista "por defecto" y pelear con el presupuesto de canales sin motivo | Purista solo si el juego lo pide; la mayoría quiere estética con libertad (§10) |

## Fuentes

- **Furnace (tildearrow)** — github.com/tildearrow/furnace — *verificado 2026-07-21*: tracker multi-sistema compatible con DefleMask; **GPLv2+/GPLv3, gratis**, Win/Mac/Linux; 200+ presets de chips (NES+expansión, C64, Game Boy/GBA, Virtual Boy, YM2612/YM2151, AY-3-8910, SN76489, PC Engine, SCC…), hasta 128 canales; export VGM/ZSM/audio.
- **NESdev Wiki — APU** — nesdev.org/wiki/APU — *verificado*: 2A03 = **5 canales** (2 pulse, 1 triangle de 32 pasos/4-bit **sin volumen**, 1 noise LFSR, 1 DMC/DPCM 7-bit desde deltas 1-bit).
- **NESdev Wiki — APU Pulse** — nesdev.org/wiki/APU_Pulse — *verificado*: duty cycles **12.5% / 25% / 50% / 25% negado (75%)**.
- **Wikipedia — Game Boy (sound hardware)** — en.wikipedia.org/wiki/Game_Boy — *verificado*: **4 canales** — Pulse 1 (sweep + volumen), Pulse 2 (solo volumen), **Wave channel** (waveform arbitraria en RAM), Noise; mono por altavoz / estéreo por auriculares.
- **Wikipedia — MOS Technology 6581 (SID)** — en.wikipedia.org/wiki/MOS_Technology_6581 — *verificado*: **3 voces**, cada una 4 formas (triangle/sawtooth/pulse de ancho variable/noise) + combinadas; **3 ADSR**; filtro multimodo LP/HP/BP (12 dB/oct LP-HP, 6 dB/oct BP); **3 ring modulators**; hard sync.
- **DefleMask** — deflemask.com — *verificado*: tracker multi-sistema (Genesis, SMS+FM, GB, PCE, NES+VRC7+FDS, C64, Arcade, NeoGeo, MSX2); **de pago** (Steam/App/Play) con **legacy 32-bit gratis**; export VGM/WAV/ROM/vídeo.
- **Little Sound Dj (LSDj)** — littlesounddj.com — *verificado*: secuenciador de **Game Boy** (4 canales), corre en hardware real (flashcart) o emulador (BGB/SameBoy); **gratis + donación voluntaria**; Nintendo no lo autoriza.
- **Dn-FamiTracker** — github.com/Dn-Programming-Core-Management/Dn-FamiTracker — *verificado*: fork **activo** de 0CC-FamiTracker (0CC: github.com/HertzDevil/0CC-FamiTracker, **`archived:false` vía GitHub API, pero sin releases desde 2018-05-20** — no técnicamente archivado, sí sin desarrollo); NES/Famicom (2A03/VRC7/FDS/N163/OPLL); Windows; **GPLv3+**; export **NSF**.
- **Bosca Ceoil Blue (Yuri Sizov)** — github.com/YuriSizov/boscaceoil-blue — *verificado*: port moderno (Godot 4.3) del Bosca Ceoil de Terry Cavanagh; **MIT, gratis, open source**; Win/Mac/Linux/Web; v3.1.2-stable (2025).
- **BeepBox (John Nesky)** — beepbox.co — *verificado (también en [ver: crear-musica])*: editor chiptune web, **MIT**, no reclama la titularidad de las canciones ("belong to their authors"); canción en la URL; export WAV+MIDI. JummBox = fork con más instrumentos (verificar su LICENSE).
- **Comandos de efecto MOD/ProTracker** — tradición estándar de trackers (OpenMPT/MilkyTracker docs; FamiTracker manual) — *conocimiento canónico, NO re-fetcheado esta pasada*: `0xy` arpeggio, `1xx`/`2xx` portamento, `3xx` tone portamento, `4xy` vibrato; las **letras exactas varían por tracker** → confirmar en las docs del tracker concreto.
- Teoría/adaptividad/tarifas: [ver: gamedev/audio]. Rutas y licencias de música: [ver: crear-musica]. Catálogo y registro `CREDITS.md`: [ver: herramientas-recursos-audio]. Acabado/loop/formato: [ver: audio-a-juego]. Implementación en motor: [ver: unity/audio-unity].
