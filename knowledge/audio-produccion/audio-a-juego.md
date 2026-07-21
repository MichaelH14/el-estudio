# Preparar el audio para el juego (game-ready)

> **Cuando cargar este archivo:** cuando ya tienes el sonido crudo (grabado, generado o descargado) y hay que DEJARLO LISTO para meterlo al motor — cortar el loop, normalizar niveles, decidir mono/estéreo, formato de entrega, nombrar y documentar la licencia. Es el paso de acabado y **entrega** entre producir el audio y implementarlo. La creación del sonido está en [ver: crear-sfx] y [ver: crear-musica]; el catálogo de herramientas/recursos en [ver: herramientas-recursos-audio]; la teoría (qué sonido y por qué) en [ver: gamedev/audio]; y la implementación en el motor en [ver: unity/audio-unity]. Aquí va SOLO el preparar y entregar.

---

## 1. El puente: qué entrega audio para que Unity lo implemente

El error clásico es tirar una carpeta de WAV sin contexto y que el que implementa adivine. Un set game-ready se entrega con una **hoja de spec** (manifest) que mapea cada archivo a su rol en el motor. Ese documento es lo que hace que [ver: unity/audio-unity] se implemente en horas y no en días.

**Contrato de entrega** — qué debe cumplir cada archivo antes de cruzar la frontera:

| Requisito | Valor de entrega | Por qué (implementación) |
|---|---|---|
| Contenedor | **WAV PCM** (o AIFF), lossless | Unity transcodifica al importar; nunca entregar MP3/OGG como fuente [ver: unity/audio-unity §2] |
| Sample rate | **44.1 kHz** (o 48 kHz si el proyecto lo estandariza) | El import de Unity resamplea/comprime; no entregar 96 kHz (desperdicio) |
| Bit depth | **16-bit** entregado (editar en 24/32-bit float, exportar con dither) | Suficiente para el build; Unity comprime igual |
| Canales | **Mono** para SFX posicional; **estéreo** para música/ambiente/UI | El paneo 3D de Unity necesita mono (§3) |
| Nivel | Consistente entre SFX, con headroom, sin clipping (§4) | Evita que el mix sumado sature; el balance fino se hace en el AudioMixer, no re-normalizando assets |
| Loops | Cortados en zero-crossing; música como **intro + loop** separados (§5) | `PlayScheduled` empalma intro→loop sin gap [ver: unity/audio-unity §5] |
| Nombre | Convención `categoria_objeto_accion_variante` (§7) | El sistema de variación lee `_01/_02/...` [ver: unity/audio-unity §4] |
| Licencia | Documentada por archivo (§8) | Legal serio: un asset sin licencia clara bloquea la publicación |

**La hoja de spec** (una tabla, CSV o markdown junto a los archivos). Ejemplo de filas:

| Archivo | Categoría (mixer group) | 2D/3D | Loop | Variantes | Nota de import |
|---|---|---|---|---|---|
| `sfx_player_footstep_grass_01..04.wav` | SFX | 3D | no | 4 (Shuffle) | mono, ADPCM |
| `sfx_ui_click.wav` | UI | 2D | no | 1 | corto, PCM |
| `mus_level1_intro.wav` + `mus_level1_loop.wav` | Music | 2D | intro+loop | 1 | estéreo, Vorbis, Streaming |
| `amb_forest_day_loop.wav` | Ambience | 2D o 3D | loop | 1 | estéreo, Vorbis, Streaming |
| `vo_narrator_intro_01.wav` | Voice | 2D | no | 1 | mono, Vorbis |

Con esa tabla, el que implementa sabe grupo del mixer, spatialBlend, loop, cuántas variantes y el Load Type sugerido — sin abrir cada clip a ciegas.

---

## 2. Formato de entrega: sample rate, bit depth, contenedor

**Regla base: entregar lossless y dejar que Unity comprima.** La compresión final (Vorbis/ADPCM/PCM) es una decisión POR CLIP en el importer del motor [ver: unity/audio-unity §2] — si entregas ya comprimido, comprimes dos veces y pierdes calidad sin ganar nada.

| Parámetro | Entrega recomendada | Detalle |
|---|---|---|
| Contenedor | WAV (PCM) | Universal, sin pérdida, sin padding. AIFF equivale en Mac |
| Sample rate | 44.1 kHz | 48 kHz si el proyecto lo fija (común en console/video). Consistente en TODO el set |
| Bit depth (edición) | 24-bit o 32-bit float | Headroom para procesar sin acumular ruido de cuantización |
| Bit depth (entrega) | 16-bit **con dither** | Al bajar de 24→16 aplicar dither (Audacity lo hace al exportar; usar "shaped") |
| Mono/estéreo | Según §3 | No estéreo "por si acaso" en SFX 3D |

- **Nunca MP3 como fuente**, y menos en loops: el encoder MP3 mete padding de silencio al inicio/final → gap audible en cada vuelta [ver: gamedev/audio; unity/audio-unity §5].
- **48 vs 44.1:** decidir UNO al arrancar el proyecto y no mezclar. Un set con sample rates mezclados da resampleos inconsistentes.
- Herramienta de conversión/export por lotes: **Audacity** (Project Rate abajo-izquierda + File > Export; Macros para batch) [ver: herramientas-recursos-audio].

---

## 3. Mono vs estéreo: la decisión que rompe el 3D

Es el error de entrega más frecuente. Un SFX posicional entregado en estéreo NO se espacializa bien: Unity espera **mono** para paneo 3D (o lo fuerza con Force To Mono, gastando el doble de disco entretanto) [ver: unity/audio-unity §2].

| Tipo de audio | Canales | Motivo |
|---|---|---|
| SFX posicional (pasos, disparos, impactos, puertas) | **Mono** | El motor genera el paneo/atenuación por posición; un estéreo aquí se ignora o suena raro |
| Música | **Estéreo** | Imagen estéreo es parte de la producción; va en 2D |
| Ambiente / bed | **Estéreo** (o mono si es una fuente puntual 3D) | La cama de fondo es 2D estéreo; un "grillo en el árbol" puntual es mono 3D |
| UI / stingers / narrador 2D | Estéreo o mono | 2D; estéreo si tiene ancho intencional |
| Voz de personaje en el mundo | **Mono** | Es una fuente 3D posicional |

- **Diseñar en estéreo, entregar mono** el SFX 3D: mezcla a mono en Audacity (`Tracks > Mix > Mix Stereo Down to Mono`) o deja `Force To Mono` en Unity. Entregar mono es explícito, la mitad de peso y no depende de que alguien recuerde marcar el checkbox.
- ⚠️ Al colapsar a mono, revisar cancelación de fase: si el estéreo tenía material fuera de fase, mono puede adelgazar o mutear el sonido. Escuchar el resultado mono, no asumir.

---

## 4. Normalización, niveles, headroom y clipping

Objetivo doble: (a) que los SFX suenen **consistentes entre sí** (que un click de UI y un impacto no estén a 30 dB de diferencia por accidente) y (b) que **nunca clipeen** ni solos ni sumados.

### Nivel por asset

- **Peak-normalizar** cada SFX a un techo común con headroom: p. ej. picos a **-3 a -6 dBFS** (Audacity: `Effect > Volume and Compression > Normalize`, target -3 dB, con "Remove DC offset" activado). Deja aire para que muchas voces sumen sin saturar el master.
- Consistencia percibida ≠ solo pico: dos sonidos con el mismo pico pueden sonar a volúmenes muy distintos. Ajustar de oído o con **Loudness Normalization** (`Effect > Volume and Compression > Loudness Normalization`, target RMS/LUFS) para igualar percepción, luego revisar que ningún pico pase el techo.
- **No maximizar** SFX individuales (no aplastarlos a 0 dBFS): eso mata el headroom del mix. El balance fino de volúmenes se hace DENTRO del juego con el AudioMixer [ver: unity/audio-unity §3], no re-exportando assets.

### Headroom del mix

- Convención citada en game audio: exportar assets con **picos 9–12 dB bajo el máximo** para que la suma de sonidos simultáneos no clipee y la mezcla final se haga en el motor [ver: gamedev/audio]. Compatible con lo anterior: los SFX muy prominentes pueden ir más arriba (-3 a -6), los frecuentes/de fondo más abajo.
- **True peak / inter-sample:** al comprimir a lossy (Vorbis/MP3) aparecen picos entre muestras que pueden clipear aunque el WAV marque < 0 dBFS. Dejar **~-1 dBTP** de margen evita distorsión post-compresión.

### Loudness de referencia (a nivel práctico)

- **No existe UN estándar LUFS único obligatorio para juegos** como el -14 LUFS de las plataformas de streaming. La medición correcta se hace en el **master bus del juego corriendo** (in-engine), no asset por asset, porque el mix suma decenas de voces variables.
- Las **certificaciones de plataforma** (Sony, Microsoft, Nintendo) tienen sus propios requisitos de loudness/true-peak — verificar en el programa de cert del target antes de masterizar el mix.
- Convención práctica de referencia (punto de partida, **NO VERIFICADO** contra un doc oficial en esta pasada — confirmar con la cert de la plataforma): master integrado en el rango **-18 a -24 LUFS** y **true peak ≤ -1 dBTP**. Medir con un medidor de loudness sobre el juego real, ajustar los faders del mixer, no los assets.

---

## 5. Loops perfectos: el punto de empalme y el click

Un loop malo se delata en la segunda vuelta: un "hipo", click o gap. Causas y arreglo:

### El click en el empalme

Un click aparece cuando la muestra final y la inicial **no coinciden** (discontinuidad de amplitud) — el altavoz salta de golpe.

1. **Cortar en zero-crossing** los DOS extremos: el punto donde la onda cruza el cero. En Audacity, seleccionar y pulsar **`Z`** (Select > At Zero Crossings) ajusta los bordes al cruce más cercano. Elimina la mayoría de los clicks.
2. **Micro-fades en el empalme:** un fade de 1–5 ms al final y otro al inicio (`Effect > Fading > Fade In/Out`) suaviza cualquier discontinuidad residual sin que se note el corte.
3. **DC offset:** quitarlo (`Normalize` con "Remove DC offset") — un offset de continua garantiza click en el loop.

### Loop de música sin costura

La música con reverb/cola es más difícil: cortar seco deja la cola de reverb truncada (se oye el "chop").

- **Técnica del solape (crossfade tail):** renderiza la pista con una cola extra, y superpón esa cola de reverb del final sobre el inicio con un crossfade, de modo que el decay del final alimente la cabeza del loop. Así la reverb "da la vuelta" sin cortarse.
- **Herramienta automática: PyMusicLooper** (open source) — encuentra puntos de loop sample-accurate por correlación y exporta **intro / loop / outro** listos. Es lo más rápido para música ya compuesta [ver: herramientas-recursos-audio].
- Verificar SIEMPRE con el loop sonando **10+ vueltas seguidas** (Audacity: play en modo loop) antes de dar por bueno un loop.

### Intro + loop separados

Muchas pistas quieren arrancar con una intro que NO se repite y luego loopear solo una sección. **Entregar dos archivos**: `..._intro.wav` y `..._loop.wav`. La implementación los empalma sin gap con `PlayScheduled` (programando el loop para que entre exactamente al terminar la intro) [ver: unity/audio-unity §5]. El loop debe cumplir §5 (zero-crossing, seamless); la intro puede terminar en cualquier punto porque el empalme lo maneja el motor por samples.

---

## 6. Mastering ligero para que suene en cualquier dispositivo

No es masterizar un disco: es dejar el audio **legible en el peor altavoz** (speaker de móvil, laptop, TV barata) sin romper los auriculares.

| Proceso | Qué hacer | Herramienta (Audacity) |
|---|---|---|
| **High-pass** en SFX | Cortar rumble/subgraves inútiles < 60–80 Hz (no en música/bajo intencional) | `Effect > EQ and Filters > High-Pass Filter` |
| **Domar dureza** | Bajar un poco 2–5 kHz si el SFX es chillón/fatiga | `Filter Curve EQ` |
| **Compresión suave** | Solo en buses de música/ambiente para pegar el rango dinámico; ratio bajo (2:1), poco | `Effect > Volume and Compression > Compressor` |
| **Test multi-salida** | Escuchar en ≥3 salidas: auriculares, altavoz de móvil real, laptop/TV | — |

- **Lección DOOM (Mick Gordon):** mezclar para el hardware real del jugador, no para el estudio. El speaker de móvil **no reproduce graves** — si la info importante de un sonido vive solo en el sub-bass, en el móvil desaparece. Poner el "cuerpo" reconocible del sonido en medios (200 Hz–4 kHz) [ver: gamedev/audio].
- **Menos es más:** no meter reverb/compresión en todo. Procesar con intención; el efecto sirve al espacio del juego. El grueso de la reverb/espacialización la pone el motor, no el asset [ver: unity/audio-unity].
- El mastering fino del MIX (no del asset) se hace en el AudioMixer con el juego corriendo, con snapshots y efectos por bus [ver: unity/audio-unity §3].

---

## 7. Nombrado y organización de archivos

El nombre no es cosmético: el sistema de variación del motor **lee el sufijo numérico** y el pipeline agrupa por prefijo. Un set bien nombrado se implementa solo.

### Estructura de carpetas (dentro de `Assets/Audio/`)

```
Audio/
  SFX/        sfx_*        (efectos)
  Music/      mus_*        (pistas, intro+loop)
  Ambience/   amb_*        (camas + one-shots)
  VO/         vo_*         (voz/diálogo)
  UI/         ui_*         (clicks, notificaciones)
```

### Convención de nombre

`categoria_objeto_accion_[cualidad]_NN.wav` — todo **minúsculas**, sin espacios ni acentos, separador `_`, número **con cero a la izquierda** (`_01`, no `_1`).

| Ejemplo | Lectura |
|---|---|
| `sfx_player_footstep_grass_01.wav` | SFX, jugador, paso, sobre hierba, variante 1 |
| `sfx_weapon_pistol_shot_03.wav` | SFX, arma, pistola, disparo, variante 3 |
| `mus_boss_intro.wav` / `mus_boss_loop.wav` | Música, boss, par intro+loop |
| `amb_cave_drip_loop.wav` | Ambiente, cueva, goteo, loop |
| `vo_guard_alert_02.wav` | Voz, guardia, alerta, toma 2 |
| `ui_menu_confirm.wav` | UI, menú, confirmar |

### Naming para el sistema de variación

- Las variantes de un mismo sonido van con **el mismo nombre base + `_NN` correlativo** (`_01`, `_02`, `_03`...). Ese set es lo que carga un **Audio Random Container** (modo Shuffle) o un pool round-robin en Unity [ver: unity/audio-unity §4].
- Regla: **3–10 variantes** para cualquier sonido que suene >5 veces por sesión (pasos, impactos, UI) [ver: gamedev/audio].
- No dejar huecos en la numeración (`_01, _02, _04` confunde al importador y a quien busca). Correlativo y sin saltos.
- Consistencia > belleza: el mismo esquema en TODO el set. Un solo archivo con otro patrón obliga a caso especial.

---

## 8. Licencias: documentar la de CADA asset (⚠️ legal serio)

Un juego que se publica es un producto comercial. Un solo asset con licencia turbia puede forzar un takedown o una demanda. **Registrar por escrito la licencia de cada archivo de audio** (una columna en la hoja de spec, o un `CREDITS/LICENSES.md`). "Lo bajé de internet" no es una licencia.

### Las licencias que vas a ver (verificar SIEMPRE la del archivo concreto)

| Licencia | Qué permite | Atribución | Comercial | Trampa |
|---|---|---|---|---|
| **CC0** (dominio público) | Casi todo | No | Sí | La más segura; aun así confirmar que quien la subió tenía derecho |
| **CC-BY** | Uso comercial | **Sí, obligatoria** | Sí | Olvidar el crédito = incumplimiento. Guardar título, autor, URL, licencia |
| **CC-BY-NC** | Solo NO comercial | Sí | **No** | ⛔ Inservible para un juego que se vende. Filtrar y descartar |
| **Sampling+** (retirada) | Restringía uso publicitario | Sí | Parcial | Licencia vieja de Freesound ya retirada por CC; algunos archivos antiguos la tienen |
| **Royalty-free comercial** | Uso ilimitado sin regalías | Depende | Sí | "Royalty-free" ≠ gratis ≠ dominio público. Leer el alcance |

### Recursos concretos y su estado (2026 — verificado en esta pasada)

| Recurso | Licencia / términos | Notas verificadas |
|---|---|---|
| **Freesound** (freesound.org) | CC0, CC-BY, CC-BY-NC por archivo | Filtrar por **CC0** para evitar atribución. Desde jul-2026 hay panel de **preferencias de IA generativa** por autor (puede prohibir uso en modelos) |
| **Sonniss GameAudioGDC** | Royalty-free, comercial, **sin atribución**, proyectos ilimitados de por vida | ⛔ Prohíbe **entrenar IA/ML** con los archivos y **revenderlos** como librería |
| **Kenney** (kenney.nl) | **CC0** | Packs de audio (UI, impactos, sci-fi, RPG, música jingles...). Confirmado en la página de un pack concreto (`Impact Sounds`: sección License = "Creative Commons CC0"); la página de LISTADO de assets no renderiza la licencia por pack — igual confirmar el `license.txt` incluido al descargar, por si un pack puntual difiere |
| **jsfxr** (sfxr.me) | Herramienta UNLICENSE (dominio público); **sonidos de uso comercial sin restricción** | Genera SFX retro; export WAV (Pro añade MP3/OGG) |
| **Bfxr** (bfxr.net) | Open source (base sfxr de increpare) | Navegador; export WAV (Ctrl+E). Confirmar términos del sonido en el repo si hay duda |
| **BeepBox** (beepbox.co) | Herramienta MIT; **no reclama propiedad de las canciones — son tuyas** | Sketch de música chip; exporta a WAV/MIDI |
| **LMMS** (lmms.io) | Software libre (GPL), gratis, multiplataforma | DAW completa; tus composiciones son tuyas. Cuidado con presets/samples de terceros incluidos: revisar su licencia |
| **Audacity** (audacityteam.org) | GPLv3, gratis; v3.7.8 (Audacity 4 en beta) | Editor de prep. Trae plugins de IA opcionales (OpenVINO: separación, reducción de ruido) bajo descarga aparte |

### IA generativa de audio/música — riesgos de licencia (honesto)

La IA de audio 2026 sirve, pero el terreno legal es resbaloso. Marcar SIEMPRE el riesgo:

| Herramienta | Comercial en juego | Trampas reales (verificadas) |
|---|---|---|
| **Suno** (música) | Solo con **plan de pago** (Pro/Premier): te asigna la propiedad del output. **Free = Suno es dueño, solo uso personal no comercial** | ⚠️ Advertencia en sus términos: el output **puede no ser único** entre usuarios; **tú indemnizas a Suno** por reclamos de terceros. Además, hay litigios de copyright abiertos en la industria de IA musical — riesgo de fondo |
| **ElevenLabs Sound Effects** (SFX) | Solo con **cuenta de pago**: SFX royalty-free para uso comercial. **Free = solo no comercial** | No usar el output para "desarrollar productos competidores"; confirmar términos vigentes antes de publicar |

Reglas de oro con IA de audio:
1. **Nunca** uses el tier gratuito de un generador para un juego que se vende — casi todos restringen el free a uso no comercial y/o retienen la propiedad. Comprobar el tier exacto.
2. Guarda **prueba del plan/fecha** de generación por si hay que demostrar los derechos.
3. Asume que el output **no es exclusivo** (otro puede generar algo casi igual) — mal para música de identidad de marca [ver: gamedev/audio].
4. El panorama legal de la IA generativa está en disputa (demandas activas). Para un juego comercial, IA para prototipo/placeholder es seguro; IA como asset final publicado es una decisión de **riesgo asumido** — documentarla.

---

## Reglas prácticas

1. Entregar **WAV PCM 44.1 kHz / 16-bit** (editar en 24/32-bit, dither al exportar). Jamás MP3/OGG como fuente, y nunca MP3 en un loop.
2. Una decisión de sample rate (44.1 **o** 48 kHz) para TODO el proyecto; no mezclar.
3. SFX posicional → **mono**; música/ambiente/UI → **estéreo**. Colapsar a mono y escuchar (revisar fase).
4. Peak-normalizar SFX con headroom (picos ~-3 a -6 dBFS los prominentes; más abajo los frecuentes); nunca aplastar assets a 0 dBFS.
5. Igualar loudness percibido entre SFX (no solo pico); el balance fino va en el AudioMixer, no re-exportando.
6. Loop: cortar los DOS extremos en **zero-crossing** (`Z` en Audacity) + quitar DC offset + micro-fade 1–5 ms si queda click.
7. Loop de música con reverb: **crossfade de la cola** sobre la cabeza, o **PyMusicLooper** para puntos automáticos.
8. Verificar cada loop **10+ vueltas** antes de aprobarlo.
9. Música con intro que no repite → entregar **`_intro.wav` + `_loop.wav`** separados (el motor los empalma con PlayScheduled).
10. Mastering ligero: high-pass < 60–80 Hz en SFX, domar 2–5 kHz si chilla, compresión suave solo en música. Poner el cuerpo del sonido en **medios** (sobrevive al speaker de móvil).
11. Probar el set en **≥3 salidas** reales: auriculares, altavoz de móvil, laptop/TV.
12. Nombrar `categoria_objeto_accion_NN.wav`, minúsculas, sin espacios/acentos, número con cero a la izquierda, correlativo sin huecos.
13. Variantes = mismo nombre base + `_01/_02/...`; 3–10 para todo sonido que suene >5 veces por sesión (alimenta Audio Random Container / pool).
14. Carpetas por tipo: `SFX / Music / Ambience / VO / UI`, prefijo acorde.
15. Entregar la **hoja de spec** (archivo → grupo del mixer, 2D/3D, loop, variantes, load hint) junto a los WAV.
16. **Documentar la licencia de CADA asset** por escrito (columna en la spec o `LICENSES.md`); descartar CC-BY-NC para uso comercial.
17. Filtrar Freesound por **CC0**; si es CC-BY, guardar título/autor/URL/licencia para el crédito.
18. Sonniss/Kenney/jsfxr/Bfxr/BeepBox/LMMS: verificar el archivo de licencia incluido antes de shippear; ninguno para entrenar IA (Sonniss lo prohíbe explícito).
19. IA generativa (Suno/ElevenLabs): **nunca el tier gratis** en un juego comercial; asumir output no exclusivo; documentar plan/fecha; tratar el asset final como riesgo asumido.
20. Loudness: medir en el **master bus in-engine** (no por asset), true peak ≤ -1 dBTP, y verificar el requisito de la **certificación de la plataforma** target.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Entregar MP3/OGG "para ahorrar espacio" | Unity comprime al importar; entregar WAV lossless. MP3 en loop = gap por padding del encoder |
| SFX 3D entregado en estéreo → no se espacializa / doble peso | Entregar mono (o Force To Mono en Unity); revisar fase al colapsar |
| SFX aplastados a 0 dBFS "para que suenen fuerte" | Mata el headroom; el mix sumado clippea → picos con margen, balance en el AudioMixer |
| Click/hipo en cada vuelta del loop | Extremos fuera de zero-crossing o DC offset → `Z` + Remove DC offset + micro-fade |
| Loop de música que corta la reverb ("chop") | Crossfade de la cola sobre la cabeza, o PyMusicLooper |
| Intro pegada al loop en un solo archivo → gap al repetir | Separar `_intro` + `_loop`; empalme por PlayScheduled en el motor |
| Todo suena bien en auriculares, nada en el móvil | Info en subgraves que el speaker no reproduce → cuerpo en medios; test en móvil real (lección DOOM) |
| Numeración con huecos o `_1` sin cero | Rompe el sistema de variación y el orden → `_01` correlativo sin saltos |
| Carpeta de WAV sin contexto → el que implementa adivina | Entregar la hoja de spec (grupo, 2D/3D, loop, variantes) |
| Asset con licencia sin registrar | `LICENSES.md`/columna por archivo; sin licencia clara no se publica |
| Usar CC-BY-NC en un juego que se vende | NC = no comercial: descartar; filtrar Freesound por CC0 |
| Música de IA del tier gratis como asset final | Free casi siempre = no comercial / propiedad del proveedor → plan de pago + documentar; asumir no-exclusividad |
| "Royalty-free" tratado como dominio público | Leer el alcance: puede exigir atribución o prohibir reventa. Royalty-free ≠ gratis ≠ CC0 |

## Fuentes

- **Audacity — Download** (audacityteam.org/download) — v3.7.8, GPLv3, gratis, multiplataforma; plugins de IA OpenVINO opcionales; Muse Group; Audacity 4 en beta. Verificado 2026-07-20.
- **Freesound — FAQ / licencias** (freesound.org/help/faq) — CC0, CC-BY, CC-BY-NC; Sampling+ retirada; panel de preferencias de IA generativa por autor (jul-2026). Verificado 2026-07-20.
- **Sonniss — GameAudioGDC** (sonniss.com/gameaudiogdc) — royalty-free, comercial, sin atribución, proyectos ilimitados de por vida; prohíbe entrenamiento IA/ML y reventa como librería. Verificado 2026-07-20.
- **Kenney — Assets: Audio** (kenney.nl/assets) — packs de audio (UI, impactos, sci-fi, RPG, jingles...); CC0 confirmado en la página del pack `Impact Sounds` (kenney.nl/assets/impact-sounds, sección License = "Creative Commons CC0"). La página de listado general no renderiza la licencia por pack — confirmar el `license.txt` de cada descarga. Verificado 2026-07-20.
- **jsfxr** (sfxr.me) — generador SFX retro en navegador; herramienta UNLICENSE (dominio público); sonidos de uso comercial sin restricción; export WAV (Pro: MP3/OGG). Verificado 2026-07-20.
- **Bfxr** (bfxr.net) — generador SFX open source (base sfxr de increpare); navegador; export WAV (Ctrl+E). Verificado 2026-07-20.
- **BeepBox** (beepbox.co) — herramienta MIT, gratis; no reclama propiedad de las canciones creadas; exporta WAV/MIDI. Verificado 2026-07-20.
- **LMMS** (lmms.io) — DAW libre/open source (GPL), gratis, Windows/macOS/Linux; VST/SoundFont. Verificado 2026-07-20.
- **ElevenLabs — Sound Effects** (elevenlabs.io/sound-effects) — SFX por IA de texto; pago = royalty-free comercial; **free = solo no comercial**; sin productos competidores. Verificado 2026-07-20.
- **Suno — Terms** (suno.com/terms) — pago (Pro/Premier) = propiedad asignada al usuario + comercial; **free = Suno dueño, solo personal/no comercial**; advertencia de output no único e indemnización. Verificado 2026-07-20.
- **FMOD — licensing** (Wikipedia/FMOD) — Non-Commercial gratis; Indie < US$600k; Basic $600k–$1.8M; Premium > $1.8M (tiers de presupuesto; confirmar fees vigentes en fmod.com/licensing). Detalle de middleware en [ver: unity/audio-unity §6].
- **9 Sound Design Tips** — GameAnalytics — headroom de exportación (picos 9–12 dB bajo el máximo), duración de SFX. (Vía [ver: gamedev/audio].)
- **PyMusicLooper** (GitHub) — detección automática de puntos de loop y export intro/loop/outro. (Vía [ver: gamedev/audio].)
