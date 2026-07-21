# Herramientas y recursos de audio

> **Cuando cargar este archivo:** cuando haya que CONSEGUIR o PRODUCIR el audio de un juego — elegir editor/DAW, generar SFX, componer o descargar música, sacar sonidos de una biblioteca, usar IA de audio/voz, o decidir la licencia de un asset antes de meterlo al proyecto. Es el catálogo operativo de herramientas y su estado de licencia a 2026. La TEORÍA de qué sonido poner y por qué está en [ver: gamedev/audio]; el CÓMO implementarlo en el motor en [ver: unity/audio-unity]; el craft fino de fabricar un SFX o una pista en [ver: crear-sfx] y [ver: crear-musica]; cablearlo al juego en [ver: audio-a-juego].

Este archivo cubre el **COMO producir/conseguir/preparar** el audio. No repite la teoría ni el import a Unity — los referencia. Precios y licencias están fechados y marcados; **todo lo que huela a "confírmalo antes de comprometerte" lo digo explícito**, porque una licencia mal leída en un juego que se publica es un problema legal real, no un detalle.

## El toolkit del dev solo (todo gratis, cero excusa para no tener audio)

Un solo desarrollador puede armar el 100% del audio de un juego chico sin gastar un peso ni saber solfeo. Tres piezas:

| Rol | Herramienta base gratis | Qué resuelve |
|---|---|---|
| **Editar/grabar** | Audacity | Recortar, normalizar, quitar ruido, fades, exportar WAV. El "Photoshop del audio" para el solo dev |
| **Generar SFX** | jsfxr / Bfxr / ChipTone / sfxr | Blips, saltos, disparos, monedas, explosiones — un botón, mil variaciones. SFX retro sin grabar nada |
| **Crear música** | BeepBox (rápido), LMMS (completo), un tracker | De una melodía de menú a un soundtrack loopeable |
| **Conseguir SFX/música hechos** | Freesound, Sonniss, Kenney (SFX) · Incompetech, Musopen (música) | Bibliotecas libres — con la letra chica de cada licencia leída |

La regla de fondo la marca la teoría: audio desde el primer prototipo con placeholders, no al final [ver: gamedev/audio]. Estas herramientas hacen ese placeholder barato.

## Editar y grabar: Audacity y alternativas

**Audacity 3.7.8** (verificado 2026-07-20, GPL v3, gratis, Windows/macOS/Linux). Editor multipista de audio. Es lo que usas para todo lo que NO sea generar ni componer: limpiar una grabación, recortar la cola de un SFX, normalizar niveles, hacer un loop, montar capas [ver: gamedev/audio, layering].

Flujo mínimo en Audacity para preparar un asset:
1. Importar/grabar → **recortar** silencios y colas (los pasos deben durar < ~0.3 s [ver: gamedev/audio]).
2. **Noise Reduction** (Effect) si hay ruido de fondo: seleccionar un tramo de solo-ruido → Get Noise Profile → aplicar al todo.
3. **Normalize** o **Loudness Normalization** para nivelar, dejando **headroom** (picos a −9…−12 dB, no a 0 dB — la mezcla final la hace el motor [ver: gamedev/audio, unity/audio-unity]).
4. **Fade In/Out** cortos para matar clicks de arranque/corte.
5. Para loops: cortar en **zero-crossing** (Z), verificar 10+ vueltas [ver: crear-musica].
6. **Export → WAV** (PCM), 44.1 o 48 kHz, 16 o 24-bit. Nunca exportar masters en MP3.
- **Macros** (antes "Chains"): procesar un lote de archivos igual (normalize + fade + export) en batch.
- Extensible con plugins **Nyquist, LADSPA, VST, LV2, Audio Unit**.
- ⚠️ Contexto: Muse Group compró Audacity en 2021; hubo polémica por telemetría → hoy la recolección es opt-in y no bloquea el uso offline. Existe el fork **Tenacity** (sin telemetría) para quien lo prefiera. No afecta la licencia GPL.

Alternativas según necesidad (todas usables por el solo dev):

| Herramienta | Qué es | Licencia/precio | Cuándo |
|---|---|---|---|
| **Ocenaudio** | Editor ligero, rápido, gratis (no FOSS) | Gratis, propietario | Ediciones rápidas, VST, preview en vivo |
| **Reaper** | DAW pro completo | De pago **barato** (~US$60 licencia personal/pequeña empresa; eval gratis 60 días) — *verificar tarifa vigente* | El estándar económico del game audio; mezcla, efectos, render por regiones |
| **Cakewalk by BandLab** | DAW completo | Gratis (solo Windows) | Producción musical sin costo en Windows |
| **GarageBand** | DAW de entrada | Gratis (solo macOS) | Música e ideas rápidas en Mac |
| **Ardour** | DAW FOSS | GPL (binarios oficiales de pago; compilable gratis) | DAW libre serio multiplataforma |

Regla: **Audacity o Reaper cubren al solo dev**. El DAW pesado solo si vas a componer/mezclar en serio [ver: crear-musica].

## Generar SFX: la familia sfxr (SFX de la nada, sin grabar)

Generadores procedurales: mueves sliders o aprietas un preset ("Coin", "Laser", "Explosion", "Jump", "Hurt") y sale un SFX; "Mutate"/"Randomize" te da variaciones infinitas del mismo. Ideales para retro/arcade/8-bit y para prototipar cualquier cosa. El craft (qué preset, cómo mutar, cómo capear) está en [ver: crear-sfx].

| Herramienta | Plataforma | Export | Licencia herramienta | Derechos del sonido generado |
|---|---|---|---|---|
| **sfxr** (DrPetter, original) | Escritorio | WAV | Código abierto / dominio público | Tuyo, sin restricción |
| **jsfxr** (sfxr.me) | Navegador | WAV + JSON (gratis); MP3/OGG + zip (Pro) | **Unlicense** | **Uso comercial sin restricción**, free y Pro (verificado) |
| **Bfxr** (increpare/Thomas Vian) | Navegador + escritorio | WAV | Código abierto (basado en sfxr) | Tuyo. *El sitio no publica un texto de licencia del output — trátalo como propio, igual que sfxr* |
| **ChipTone** (SFBGames) | Navegador + escritorio | WAV | Gratis | **CC0** — "free to use for any purpose, commercial or otherwise" (verificado) |

- **Bfxr** añade más formas de onda, mezcla de capas y sintetizadores sobre sfxr → más versátil que jsfxr.
- **ChipTone** es el más completo (synth + sampler + secuenciador) y con la licencia más limpia (CC0).
- Todos generan **WAV** → entra directo al pipeline (WAV master; Unity comprime al importar [ver: unity/audio-unity]).
- Para SFX no-retro (foley, impactos reales), estos generadores no sirven: ahí vas a bibliotecas o grabas [ver: crear-sfx].

## Crear música: BeepBox, LMMS, trackers, DAWs

De más rápido/simple a más potente/complejo:

| Herramienta | Qué es | Licencia/precio | Export | Cuándo |
|---|---|---|---|---|
| **BeepBox** (beepbox.co) | Secuenciador chiptune en navegador; toda la canción va en la URL | Código **MIT**; **BeepBox no reclama la titularidad — "original songs belong to their authors"** (verificado) | Audio + MIDI desde su menú Export; comparte por URL | Melodía de menú, jingle, loop retro en minutos, sin instalar |
| **LMMS** | DAW/estación completa: synths, samples, beats, VST, automatización | **GPL-2.0**, gratis, Win/Mac/Linux (verificado) | WAV/OGG/MP3/MIDI | Soundtrack completo sin pagar DAW |
| **Trackers** (OpenMPT, MilkyTracker, Furnace) | Composición por patrones/samples; archivos diminutos (.xm/.mod/.it/.s3m) | FOSS | Módulo tracker o WAV | Música chiptune/demoscene; Unity importa módulos tracker nativamente [ver: unity/audio-unity] |
| **Reaper / Cakewalk / GarageBand / Ardour** | DAWs (ver tabla anterior) | Ver arriba | WAV/stems | Producción seria, grabación en vivo, música adaptativa por stems |

- **Música adaptativa** (stems por capa, secciones loopeables): la decisión de componer así se toma ANTES de escribir, y el craft de exportar stems/intro+loop está en [ver: crear-musica]; la teoría de vertical/horizontal en [ver: gamedev/audio].
- **Loops**: exporta a WAV u OGG, **jamás MP3** (el padding del encoder mete gap) [ver: gamedev/audio, unity/audio-unity].

## Bibliotecas de SFX: cuáles y su licencia EXACTA

⚠️ "Descargable gratis" ≠ "usable en tu juego comercial". Lee la licencia de CADA archivo, no de la web.

| Recurso | Qué es | Licencia | La letra chica |
|---|---|---|---|
| **Freesound** (freesound.org) | Comunidad enorme de grabaciones | **Mezcla** por sonido: CC0, CC-BY 4.0, CC-BY-NC 4.0, y Sampling+ (retirada, en archivos viejos) | **Revisar CADA sonido**. Filtrar la búsqueda por licencia. NC = prohibido en juego comercial. Usa tu "attribution list" del perfil para los créditos |
| **Sonniss GameAudioGDC** (sonniss.com) | Bundle anual gratis por la GDC; archivo histórico 200+ GB | Royalty-free, **comercial ilimitado, sin atribución** (verificado) | ✅ Ideal para juegos. **No revender** los archivos sueltos como biblioteca. **Prohibido entrenar IA** con ellos |
| **Kenney** (kenney.nl) | Packs de SFX/UI/impactos estilo casual | **CC0** (verificado en asset) | Libre total, sin atribución. Lo más seguro que hay |
| **OpenGameArt.org** | Assets de comunidad | **Mezcla**: CC0, CC-BY, **CC-BY-SA, GPL** | ⚠️ CC-BY-SA y GPL son **share-alike**: pueden obligarte a licenciar algo tuyo igual. Revisar por asset |
| **Pixabay** (audio) | SFX y música libres | Licencia Pixabay (uso comercial, sin atribución) | No redistribuir el archivo suelto. *Verificar términos vigentes* |
| **Mixkit / ZapSplat / 99Sounds** | Bibliotecas free | Varían: free-con-atribución o free-license propia | Leer la licencia de la web; ZapSplat: gratis con atribución, sin atribución en plan pago |
| **BBC Sound Effects** | ~33k sonidos del archivo BBC | Licencia **RemArc: personal/educativa/investigación** (según la propia BBC; *no reverificado por fetch en esta pasada — página JS-rendered/con geo-bloqueo, confirmar en sound-effects.bbcrewind.co.uk antes de depender de esto*) | ⛔ **NO para juegos comerciales**. Trampa clásica: parecen libres, no lo son |

Regla operativa Freesound: en la barra de búsqueda filtra por licencia (p.ej. solo CC0) para no tener que revisar uno por uno; si usas CC-BY, guarda el nombre del sonido + autor + URL apenas lo descargas.

## Bibliotecas de música: libre, de pago, y cómo verificar la licencia real

| Recurso | Qué es | Licencia | Ojo |
|---|---|---|---|
| **Incompetech** (Kevin MacLeod) | Catálogo enorme royalty-free | **CC-BY** (atribuir) o licencia de pago para omitir atribución | Suena "stock" → cero identidad si lo usan mil juegos [ver: gamedev/audio] |
| **Musopen** | Grabaciones de clásica en **dominio público** | Dominio público / CC | Resuelve el problema "la obra es de Debussy pero la grabación tiene copyright" [ver: gamedev/audio] |
| **Free Music Archive (FMA)** | Música con licencia CC | **Mezcla** CC (BY, BY-NC, BY-SA…) | Revisar cada pista; hay mucho NC (no comercial) |
| **YouTube Audio Library** | Pistas y SFX gratis de Google | Licencia propia de YouTube | ⚠️ Pensada para **video**; verificar si permite juegos antes de asumir |
| **Pixabay Music / OpenGameArt** | Música libre de comunidad | Licencia Pixabay / mezcla CC | Igual que su sección de SFX |
| **Suscripciones "royalty-free"** (Epidemic Sound, Artlist, Soundstripe, Musicbed) | Catálogos de pago por suscripción | Licencia por suscripción | ⚠️ **CRÍTICO**: sus licencias estándar cubren **video/redes/contenido**, NO necesariamente **juegos/apps interactivas** — muchas requieren licencia especial o lo excluyen. **Verificar el uso "in-game" explícitamente antes de suscribirte** |
| **Contratar composición** | Música original, identidad propia | Contrato (work-for-hire vs licencia) | Tarifas y modelo de derechos en [ver: gamedev/audio] — no se repiten aquí |

**Cómo verificar una licencia de música antes de usarla** (procedimiento):
1. Identifica la licencia EXACTA de esa pista (no "la web es gratis" — la pista).
2. ¿Permite **uso comercial**? Un juego que publicas/monetizas SIEMPRE es comercial.
3. ¿Permite **uso interactivo / en juego / en software**? (aquí caen las suscripciones de video).
4. ¿Requiere **atribución**? ¿Dónde debe ir (créditos, store)?
5. ¿Hay **share-alike** (SA/GPL)? Si sí, entiende qué te obliga.
6. **Guarda copia** del texto de licencia + URL + fecha, por si la página muere. Regístralo (CREDITS, abajo).

## IA de audio a 2026: útil, pero con riesgos de licencia reales

La IA generativa de audio ya sirve para SFX, música y voz de calidad usable. El problema **no es la calidad, es la procedencia y los derechos**. Estado verificado 2026-07-20:

| Herramienta | Qué genera | Datos de entrenamiento | Uso comercial del output | Riesgo |
|---|---|---|---|---|
| **ElevenLabs Sound Effects** | Texto → SFX | No divulgado | **Pago: comercial royalty-free. Free: solo no-comercial** (verificado) | Bajo si pagas y respetas términos; no puedes usar el output para hacer un competidor |
| **Stable Audio** (Stability AI, v2.x) | Texto → música/SFX (hasta ~3 min, 44.1k estéreo) | **Dataset licenciado de AudioSparx (800k+ archivos), con opt-out de artistas** (verificado) | Comercial en planes de pago (revisar ToS) | **El más bajo en procedencia**: entrenado con licencia, se posiciona como "commercially safe" |
| **Suno** | Texto → canción | Contestado (litigio) | **Pago: tú eres dueño del output. Free: solo no-comercial** (verificado) | ⚠️ Suno **"no garantiza que exista copyright sobre el output"**; atribución a Suno requerida; demandado por la RIAA (jun 2024) |
| **Udio** | Texto → canción | Migrando a "solo música licenciada" | Revisar tras el cambio | ⚠️ **Universal Music lo demandó y llegó a acuerdo (oct 2025)**; Udio migra a modelo licenciado + streaming y dio a usuarios **48 h para descargar** sus creaciones (verificado) → **plataforma inestable, no dependas de ella** |
| **Meta MusicGen / AudioGen** (AudioCraft) | Texto → música / SFX | — | ⛔ **Pesos bajo CC-BY-NC 4.0 = NO comercial** (código MIT, pesos NC) (verificado) | No puedes shippear su output en un juego comercial |
| **Adobe (audio generativo, Firefly)** | SFX/audio | Marketed como datos licenciados/Adobe Stock | Posicionado "commercially safe" | *Verificar producto/términos vigentes — la oferta cambia rápido* |

**Los 5 riesgos honestos de la IA de audio (léelos antes de meter IA en un juego que publicas):**
1. **Procedencia del entrenamiento**: si el modelo se entrenó con audio con copyright sin licencia, tu output puede ser obra derivada infractora. Litigios abiertos (RIAA vs Suno/Udio, jun 2024; daños pedidos hasta US$150k por obra). Modelos con datos **licenciados** (Stable Audio/AudioSparx, Adobe) mitigan esto.
2. **Copyright del output**: en EEUU, una obra puramente generada por IA sin autoría humana suficiente **no es registrable** → no puedes protegerla y otro podría usarla. Suno lo admite en sus términos.
3. **Términos por tier**: casi todos: **free = no comercial, pago = comercial**. Un juego que vendes, monetizas con anuncios o IAP, o publicas bajo tu marca = **comercial siempre**.
4. **Estabilidad de plataforma**: Udio le movió el piso a sus usuarios con 48 h de aviso. No construyas un pipeline que dependa de un servicio que puede cambiar términos o cerrar.
5. **Voz IA**: clonar la voz de una persona real sin consentimiento es ilegal (fraude/derechos de personalidad); voces de celebridades y figuras públicas están protegidas.

Postura práctica: **IA como acelerador de placeholders y de ideas, sí; como fuente final de assets comerciales, solo con herramientas de datos licenciados y en plan de pago, y documentando la licencia**. Ante duda legal, un SFX de Sonniss o una pista comisionada es terreno más firme.

## Voz: TTS, grabación, clonado — y sus derechos

| Vía | Herramientas | Derechos / coste |
|---|---|---|
| **TTS de sistema/offline** | `say` (macOS), SAPI (Windows), **eSpeak-NG** (GPL, robótico), **Piper** (neural, offline, MIT, buena calidad) | Gratis. Piper es ideal para voz robótica de personaje o placeholder de narrador |
| **TTS en la nube** | Azure AI Speech, Google Cloud TTS, Amazon Polly | De pago por carácter; **derechos comerciales incluidos en el plan** — bueno para narrador, UI, scratch de localización |
| **Voz IA / clonado** | **ElevenLabs** (TTS + clonado: **Instant** 1–5 min para prototipo, **Professional** 30+ min para juegos) | **Clonar exige consentimiento explícito del dueño de la voz** (verificado); comercial en planes de pago |
| **Grabación propia (DIY)** | Mic USB (Blue Yeti, Rode NT-USB), clóset con mantas, Audacity/Reaper | Tuyo. Graba a 48 kHz/24-bit, trata la sala. La opción con más control y cero problema de derechos |
| **Actores de voz** | Casting: Voices.com, Casting Call Club, Fiverr | Contrato: **work-for-hire vs licencia**, y **alcance del uso** (juego + tráiler + ports + secuelas). La voz de una persona es un derecho de personalidad — contrato escrito siempre [ver: gamedev/audio] |

Nota: TTS neural gratis (Piper) suena bien para robots/IA-de-juego; para voz humana creíble de personaje, o pagas nube/ElevenLabs o grabas/contratas. Localización de voz a escala → nube por carácter.

## Middleware vs nativo: solo el estado de licencias (el concepto va aparte)

La **decisión** middleware vs audio nativo (cuándo cada uno) está en [ver: unity/audio-unity] y [ver: gamedev/audio]. Aquí solo el estado de licencia 2026, porque es un "recurso" con letra chica:

| Opción | Free tier | Umbral | Estado verificación |
|---|---|---|---|
| **AudioMixer nativo de Unity** | Incluido, sin licencia extra | — | Cubre SFX con variación, música por estados, ducking [ver: unity/audio-unity] |
| **FMOD** | **Indie = GRATIS (US$0)** para presupuesto de desarrollo **< US$600k**; No-comercial gratis | Basic US$600k–US$1.8M; Premium > US$1.8M (de pago) | Tiers verificados (FMOD/Wikipedia 2026); **tarifas exactas de Basic/Premium NO verificadas** — confirmar en fmod.com/licensing |
| **Wwise** (Audiokinetic) | Gratis para uso no comercial; para comercial hay licencia indie/limitada por cantidad de assets | Cifras exactas 2026 **NO VERIFICADAS** (audiokinetic.com devolvió 403) | Confirmar en audiokinetic.com/pricing antes de comprometerse |

Middleware solo si hay sound designer dedicado o música adaptativa compleja; si no, el stack nativo alcanza [ver: unity/audio-unity]. **Verifica los umbrales vigentes antes de decidir** — cambian (FMOD cambió su modelo a base-presupuesto).

## Formatos y export: entrega WAV, la compresión la decide el motor

- **Trabaja y archiva en WAV (PCM) lossless**, 44.1 o 48 kHz, 16 o 24-bit. Es tu master; de ahí sale todo.
- **Nunca** masteres/loops en **MP3** (lossy + padding del encoder = gap en el loop y pérdida acumulada al reeditar) [ver: gamedev/audio, unity/audio-unity].
- Export con **headroom**: picos a −9…−12 dB, no a 0 dB. La suma de sonidos se mezcla dentro del motor; si exportas al máximo, clippea [ver: gamedev/audio].
- **SFX 3D en mono** (el motor hace el paneo; Unity puede forzar mono al importar); música en estéreo [ver: unity/audio-unity].
- La **compresión final** (Vorbis / ADPCM / PCM) y el **load type** (Decompress / Compressed / Streaming) NO los eliges al exportar: **los decide el importer de Unity por clip** [ver: unity/audio-unity]. Tú entregas WAV; Unity transcodifica. No pre-comprimas a OGG "para ahorrar" salvo loops donde quieras controlar el corte.

## La regla de oro: NUNCA uses audio sin verificar su licencia — documenta cada asset

Esto no es burocracia: es lo que te evita un takedown, una demanda o rehacer el audio a última hora.

- **"Gratis de descargar" ≠ "libre de usar" ≠ "libre comercial" ≠ "libre sin atribución".** Son cuatro cosas distintas. Verifica las cuatro.
- **Tu juego = uso comercial siempre** que lo publiques o monetices (incluso free-to-play con anuncios/IAP; incluso gratis bajo tu marca).
- Chuleta de licencias comunes:

| Licencia | Puedes en juego comercial | Atribución | Trampa |
|---|---|---|---|
| **CC0 / dominio público** | ✅ Sí | No | Ninguna — lo más seguro |
| **CC-BY** | ✅ Sí | **Sí, obligatoria** | Si no atribuyes, incumples |
| **CC-BY-SA** | ⚠️ Sí, con cuidado | Sí | **Share-alike**: puede obligarte a licenciar tu obra igual |
| **CC-BY-NC / Sampling+ / cualquier "NC"** | ⛔ **NO** | — | "NonCommercial" = fuera de un juego que vendes/monetizas |
| **GPL** (en un asset) | ⚠️ | Sí | Copyleft — implicaciones sobre lo que enlaza; evitar salvo que la entiendas |
| **Royalty-free (de pago)** | ✅ Según alcance | Según licencia | "Royalty-free" solo significa "sin regalías por uso", NO "gratis" ni "sin límites". Lee el alcance |

- **Documenta CADA asset desde que lo descargas** en un registro (`CREDITS.md` o `attributions.csv`). Reconstruirlo antes de publicar es un infierno. Campos:

  `archivo | fuente | autor | URL | licencia | ¿atribución? | texto exacto de atribución`

  Ejemplo de fila: `sfx_ui_click_01.wav | Freesound | usuario123 | https://freesound.org/s/12345 | CC-BY 4.0 | Sí | "click by usuario123 (freesound.org/s/12345) CC BY 4.0"`

- Pon las **atribuciones requeridas** dentro del juego (pantalla de créditos) y/o en el store listing. Freesound te da tu **attribution list** lista para copiar.
- **Guarda copia local del texto de la licencia** + fecha, por si la web muere.
- **Clásica**: la composición puede ser dominio público, pero **cada grabación tiene su propio copyright** → usa Musopen (grabaciones de dominio público) o graba la tuya [ver: gamedev/audio].
- **IA**: registra qué herramienta, qué plan (free/pago) y guarda el snapshot de sus términos — es la evidencia de que tenías derecho a usar ese output.

## Organización de los assets de audio del proyecto

- **Estructura** (dentro de `Assets/Audio/`): `Music/`, `SFX/`, `Ambience/`, `UI/`, `Voice/`. Subdivide `SFX/` por categoría (`Player/`, `Enemies/`, `Weapons/`, `Impacts/`).
- **Nombres**: minúsculas, `snake_case`, prefijo por tipo + variación numerada. Consistente y ordenable:
  - `sfx_weapon_shot_01.wav`, `sfx_ui_click.wav`, `mus_level1_loop.wav`, `mus_boss_intro.wav`, `amb_forest_day.wav`, `vo_narrator_intro_es.wav`.
  - Las variaciones (`_01`, `_02`, `_03`) alimentan el round-robin / Audio Random Container [ver: unity/audio-unity].
- **Masters WAV y proyectos** (`.aup3` de Audacity, `.rpp` de Reaper, stems): guárdalos **fuera del pipeline de import de Unity** (Unity importa todo lo que esté en `Assets/`). Patrón: carpeta `_AudioSource/` en el repo (o fuera de `Assets/`) con masters y mezclas; solo los **WAV finales** van en `Assets/Audio/` [ver: unity/assets-pipeline-git, pipeline/estructura-proyecto].
- **CREDITS.md / attributions.csv** junto a la carpeta de audio, mantenido al día (regla de oro, arriba).
- **Versionado**: binarios de audio con **Git LFS** [ver: unity/assets-pipeline-git].
- **Estado por color** desde el placeholder (rojo=falta, naranja=roto, amarillo=cambiar, verde=final) para saber qué audio aún es temporal [ver: gamedev/audio].

## Reglas prácticas

- [ ] Audio con placeholders desde el primer prototipo; estas herramientas gratis lo hacen barato [ver: gamedev/audio].
- [ ] Editar en Audacity (o Reaper); **masteres siempre en WAV**, nunca MP3.
- [ ] Exportar con headroom (picos −9…−12 dB); la mezcla final se hace en el motor.
- [ ] SFX retro/prototipo → generadores (jsfxr/Bfxr/ChipTone); guardar el WAV como master.
- [ ] Música rápida → BeepBox; soundtrack → LMMS o un DAW; loops en WAV/OGG, jamás MP3.
- [ ] **Antes de descargar cualquier asset, leer SU licencia** (no la de la web). ¿Comercial? ¿Interactivo/juego? ¿Atribución? ¿Share-alike?
- [ ] Freesound: filtrar por licencia; evitar todo lo **NC** en juego comercial; anotar autor+URL al descargar.
- [ ] Preferir **CC0** (Kenney, ChipTone) y **royalty-free sin atribución** (Sonniss) cuando exista — menos fricción legal.
- [ ] Suscripciones de música (Epidemic/Artlist/…): **confirmar que la licencia cubre juegos/apps**, no solo video, ANTES de suscribirse.
- [ ] BBC SFX y similares "de archivo": verificar que no sean solo personal/educativo (RemArc ⛔ comercial).
- [ ] IA de audio: solo output de plan de **pago** en juego comercial, preferir modelos de **datos licenciados** (Stable Audio, Adobe); guardar snapshot de términos.
- [ ] ⛔ No shippear pesos NC (MusicGen/AudioGen CC-BY-NC) en un juego comercial.
- [ ] Voz clonada: solo con **consentimiento escrito**; nunca voces de personas reales/celebridades sin derechos.
- [ ] Contratar voz/música: contrato con **work-for-hire vs licencia** y alcance de uso explícito [ver: gamedev/audio].
- [ ] Mantener un **CREDITS.md/attributions.csv** con archivo, fuente, autor, URL, licencia y texto de atribución de **cada** asset, actualizado desde el día 1.
- [ ] Poner las atribuciones requeridas en la pantalla de créditos y/o store antes de publicar.
- [ ] Masteres/proyectos de audio fuera del import de Unity; solo WAV finales en `Assets/Audio/`, con nombres `tipo_contexto_nn.wav` y Git LFS.
- [ ] Middleware (FMOD/Wwise): verificar el **umbral de licencia vigente** antes de decidir; para el solo dev el nativo suele bastar [ver: unity/audio-unity].
- [ ] Grabación propia: 48 kHz/24-bit, sala tratada — la vía con cero problema de derechos.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| "Lo bajé gratis, es libre" → usar un CC-BY-NC en un juego que se vende | NC = prohibido comercial. Leer la licencia del archivo; preferir CC0/Sonniss/Kenney |
| Master o loop en MP3 → gap en el loop y pérdida al reeditar | Master siempre en WAV; loops WAV/OGG [ver: unity/audio-unity] |
| Exportar al máximo (0 dB) y que la mezcla clippee en el motor | Headroom −9…−12 dB; la mezcla se hace en el motor [ver: gamedev/audio] |
| Suscribirse a Epidemic/Artlist y meter la música en el juego sin más | Sus licencias son para video/redes; verificar cobertura **in-game** antes |
| Usar BBC Sound Effects en un juego comercial | Licencia RemArc = personal/educativa; no comercial |
| IA de música en free tier dentro de un juego que monetizas | Free = no comercial en Suno/ElevenLabs; usar plan de pago y guardar términos |
| Shippear output de MusicGen "porque es open source de Meta" | Código MIT, pero **pesos CC-BY-NC = no comercial** |
| Construir el pipeline sobre un servicio IA de audio inestable | Udio movió el piso con 48 h; no depender de un servicio que puede cambiar/cerrar |
| Clonar una voz real sin permiso | Consentimiento escrito obligatorio; celebridades protegidas por derechos de personalidad |
| Assets de audio sin registro de licencia → pánico antes de publicar | `CREDITS.md`/`attributions.csv` desde el día 1, con URL y texto de atribución |
| Grabación de clásica ajena "porque Debussy es dominio público" | La obra sí, la **grabación** no; Musopen o grabar propia |
| Masteres pesados dentro de `Assets/` inflando el import de Unity | Masteres/proyectos fuera del pipeline; solo WAV finales en `Assets/Audio/` + Git LFS |
| Nombres inconsistentes → imposible armar round-robin o encontrar nada | `tipo_contexto_nn.wav`, snake_case, variaciones numeradas |

## Fuentes

- **Audacity — Download** (audacityteam.org) — versión 3.7.8, GPL v3, plataformas y features (verificado 2026-07-20).
- **Freesound — FAQ / licencias** (freesound.org) — CC0, CC-BY 4.0, CC-BY-NC 4.0 y Sampling+ (retirada); cómo ver la licencia por sonido y la attribution list.
- **Sonniss — GameAudioGDC** (sonniss.com) — bundle anual, royalty-free, comercial ilimitado, sin atribución, no reventa suelta, **prohibido entrenar IA**.
- **Kenney — Impact Sounds / Audio** (kenney.nl) — licencia **CC0** confirmada en asset.
- **jsfxr** (sfxr.me) — herramienta bajo Unlicense; **uso comercial sin restricción** del sonido generado; export WAV/JSON (free), MP3/OGG (Pro).
- **Bfxr** (bfxr.net) — generador open source basado en sfxr (increpare/Thomas Vian); export WAV.
- **ChipTone** (sfbgames.itch.io/chiptone) — gratis; sonidos **CC0** ("free for any purpose, commercial or otherwise").
- **BeepBox** (beepbox.co) — código MIT; **no reclama la titularidad de las canciones** ("original songs belong to their authors").
- **LMMS — LICENSE.txt** (github.com/LMMS/lmms) — **GPL-2.0** (el archivo de licencia es el texto de la GPLv2).
- **FMOD** (en.wikipedia.org/wiki/FMOD) — tiers: No-comercial gratis, **Indie < US$600k**, Basic US$600k–US$1.8M, Premium > US$1.8M (tarifas exactas de pago no verificadas).
- **ElevenLabs — Sound Effects** (elevenlabs.io/sound-effects) — pago: comercial royalty-free; free: solo no-comercial; no usar output para competir.
- **ElevenLabs — Voice Cloning** (elevenlabs.io/voice-cloning) — Instant vs Professional; **clonar exige consentimiento explícito**; celebridades protegidas.
- **Stability AI — Stable Audio 2.0** (stability.ai) — entrenado **exclusivamente en dataset licenciado de AudioSparx (800k+)** con opt-out de artistas; posicionado como comercialmente seguro.
- **Suno — Terms** (suno.com/terms) — pago: dueño del output; free: solo no-comercial; **no garantiza que exista copyright sobre el output**; atribución a Suno.
- **Meta AudioCraft — MusicGen/AudioGen** (github.com/facebookresearch/audiocraft) — **código MIT, pesos CC-BY-NC 4.0** → uso comercial de los pesos no permitido.
- **Udio** (en.wikipedia.org/wiki/Udio) — demanda RIAA jun 2024 (daños hasta US$150k/obra); **acuerdo con Universal Music oct 2025**, migración a música licenciada + streaming, 48 h para descargar creaciones.
- **BBC Sound Effects / RemArc** (sound-effects.bbcrewind.co.uk) — licencia personal/educativa/investigación citada de memoria del dominio; **NO reverificada por fetch en esta pasada** (página JS-rendered + geo-bloqueo UK impidieron confirmarla). Confirmar el texto exacto de la licencia antes de descartar o usar este archivo en un proyecto comercial.
