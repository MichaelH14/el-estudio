# Crear y conseguir música

> **Cuando cargar este archivo:** cuando haya que PRODUCIR u OBTENER la música de un juego — decidir entre componer, licenciar, música libre, IA o contratar; elegir herramienta para componer sin ser músico; preparar stems/loops para que el motor los use; o verificar la licencia de un track antes de publicar. La TEORÍA (funciones de la música, adaptividad, silencio) está en [ver: gamedev/audio]; la IMPLEMENTACIÓN en Unity en [ver: unity/audio-unity]. Aquí va el CÓMO conseguir el sonido, no el porqué. Para SFX ver [ver: crear-sfx]; catálogo de herramientas y librerías [ver: herramientas-recursos-audio]; preparar el asset para el motor [ver: audio-a-juego].

## Regla previa: no repetir la teoría

Este archivo NO explica qué hace la música ni cómo se estructura la adaptividad — eso ya está resuelto en [ver: gamedev/audio] (vertical layering vs horizontal resequencing, stingers, transiciones, cuándo callar). Aquí se decide de dónde SALE la música y cómo se PREPARA. Antes de producir un solo compás, saber si el juego necesita música adaptativa: eso cambia el encargo entero (se pide en stems desde el día uno, no se trocea después).

## Las 5 rutas para conseguir música

| Ruta | Coste típico | Control / identidad | Esfuerzo del dev | Riesgo de licencia | Cuándo elegirla |
|---|---|---|---|---|---|
| **Componer uno mismo** | $0 + tiempo | Máximo | Alto (aprender) | Ninguno (es tuyo) | Jam, prototipo, dev con oído musical, juego de identidad fuerte y bajo presupuesto |
| **Música libre / CC** | $0 | Bajo (suena a stock) | Bajo | Medio: atribución mal hecha = infracción | Prototipo, game jam, juego donde la música no es protagonista |
| **Licenciar (royalty-free / stock)** | $10–$500 por track/pack | Bajo-medio | Bajo | Bajo si se lee el alcance | Juego comercial chico que necesita calidad sin encargo a medida |
| **IA generativa** | $0–$30/mes | Medio | Bajo-medio | **ALTO** (ver sección IA) | Prototipos y placeholders; para música final publicada = zona minada |
| **Contratar compositor** | $50–$2500 por minuto | Máximo (a medida) | Medio (dirigir) | Bajo si el contrato es claro | Juego comercial donde la música es identidad; hay presupuesto |

Regla de decisión rápida: música = identidad del juego y hay algo de presupuesto → contratar o componer. Música = relleno funcional → licenciar o CC. Nunca dejar la música para el final sin partida presupuestaria [ver: gamedev/audio, sección pitfalls].

---

## Ruta 1 — Componer uno mismo sin ser músico

Se puede hacer música usable sin saber solfeo. La clave es elegir una herramienta con fricción baja y apoyarse en loops/samples ya hechos.

### Herramientas accesibles (verificadas 2026)

| Herramienta | Qué es | Plataforma | Coste | Licencia del SOFTWARE | ¿Tu output es tuyo? |
|---|---|---|---|---|---|
| **BeepBox** (beepbox.co) | Editor de chiptune en el navegador; la canción vive en la URL | Web | Gratis | — (herramienta web de John Nesky) | Sí: "BeepBox does not claim ownership over songs created with it" — la canción es del autor. Exporta a WAV |
| **OpenMPT** (openmpt.org) | Tracker clásico; edita módulos IT/XM/S3M/MOD + soporta VST | Windows | Gratis, open source | Software libre | Sí; ⚠️ los samples que importes deben estar licenciados aparte |
| **Bosca Ceoil** (Terry Cavanagh) | Editor de música para juegos pensado para principiantes absolutos | Win/Mac/Web | Gratis, open source | Verificar versión vigente ("Bosca Ceoil Blue" es la remake moderna) | Sí; NO VERIFICADO en esta pasada — confirmar antes de publicar |
| **LMMS** (lmms.io) | DAW completo gratis: patrones, synths, beats, mezcla | Win/Mac/Linux | Gratis, open source (GPL) | GPL cubre el programa, NO tu música | Sí; ⚠️ revisar licencia de samplepacks incluidos/importados |
| **GarageBand** | Estudio completo con Apple Loops y bateristas de sesión | Mac / iOS | Gratis (con el dispositivo Apple) | Apple SLA | Tu composición sí; los **Apple Loops** son usables en tus obras pero NO redistribuibles como loops sueltos — verificar el Apple SLA vigente |

Notas de honestidad:
- **BeepBox**: la web no publica términos formales de uso comercial; no restringe explícitamente pero tampoco lo garantiza por escrito. Para un juego publicado, guardar el WAV exportado y documentar que es composición original propia.
- **Bosca Ceoil / "BossaNova"**: el nombre real de la herramienta beginner-friendly de referencia es **Bosca Ceoil**. No pude verificar su estado/licencia 2026 en esta pasada → marcada NO VERIFICADO; confirmar en su repo antes de depender de ella.
- **Apple Loops (GarageBand)**: históricamente el Apple SLA permite usar los loops incluidos dentro de tus propias composiciones comerciales, pero prohíbe distribuir los loops como archivos sueltos o dentro de una librería competidora. Punto legal serio → leer el SLA actual antes de publicar.

### Loops y librerías de samples (materia prima para no-músicos)

Componer "de cero" es duro; ensamblar loops y samples ya hechos es accesible. Pero cada loop trae su propia licencia:

- Loops incluidos en el DAW (Apple Loops de GarageBand, samplepacks de LMMS): usar según el SLA del programa — casi siempre OK dentro de tu obra, casi nunca redistribuibles sueltos.
- Loops de librerías externas (Splice, Loopmasters, etc.): son licencias comerciales; leer si cubren videojuegos y si prohíben "sync" (uso sincronizado a imagen). Muchos loops de música baratos NO cubren uso en juegos por defecto.
- Regla de oro: un loop en tu proyecto = una línea en tu registro de licencias [ver: herramientas-recursos-audio].

### DAWs: ¿cuándo vale aprender uno?

| DAW | Coste 2026 | Curva | Cuándo vale |
|---|---|---|---|
| **GarageBand** | Gratis (Mac/iOS) | Baja | Punto de entrada ideal en Mac; loops + instrumentos listos |
| **LMMS** | Gratis (GPL, multiplataforma) | Media | Alternativa gratis fuera de Mac; workflow de patrones/tracker |
| **REAPER** | **$60** licencia con descuento (ingreso bruto anual < $20,000, o educación/ONG); **$225** licencia comercial. Evaluación **60 días** completa y gratis (reaper.fm) | Media-alta | Cuando vas en serio: barato, potente, sin límite de funciones en la prueba. El estándar de facto del indie con presupuesto ajustado |

Regla: no aprender un DAW "por si acaso". Se aprende cuando (a) vas a componer varias piezas, o (b) necesitas editar/mezclar audio propio más allá de recortar. Para 2-3 loops simples, BeepBox o un tracker alcanzan. La licencia de descuento de REAPER a $60 la hace la opción seria más barata; su prueba de 60 días sin recortes permite terminar un juego chico antes de pagar.

Punto de licencia clave: **ningún DAW reclama tu música**. GPL (LMMS) y las licencias de REAPER/Apple cubren el *programa*; lo que compongas es tuyo. El riesgo está en los *samples/loops/VST presets* que metas dentro, no en el DAW.

---

## Componer PARA el juego (no solo componer)

Aquí es donde el dev-músico se diferencia del músico de canciones. La teoría del sistema adaptativo está en [ver: gamedev/audio]; lo que sigue es cómo se PRODUCE ese material.

### Componer por capas (stems) para vertical layering

- Escribir la pieza y exportar cada instrumento/grupo como **stem separado** que empieza y termina en el mismo punto y comparte tempo/tonalidad: p. ej. `bed` (pad+bajo), `perc`, `melodía`, `tensión`. El motor los sube/baja para cambiar intensidad sin cambiar de pieza.
- Todos los stems deben poder sonar juntos sin barro y cualquier subconjunto debe sonar completo. Se compone pensando en "qué pasa si solo suena el bed" desde el principio.
- Exportar los stems **alineados a la muestra** (mismo largo exacto, mismo punto de inicio) o el layering se desfasa. Este es el error #1 al preparar stems.

### Componer intros + loops para horizontal resequencing

- Cada sección (exploración, combate, boss) = su propia pieza loopeable, más opcionalmente una **frase de transición** entre secciones.
- Estructura de producción: `intro (una vez) → loop (repite) → outro/transición`. La intro arranca la pieza; el loop es la sección que repite indefinidamente.
- Componer las secciones en tonalidades/tempos compatibles para que las transiciones no chirríen. Si el middleware quantiza a compás, marcar los puntos de sincronización.

Decisión de producción que va ANTES de escribir una nota: ¿el juego necesita adaptividad? Si sí, se encarga/compone en stems y en secciones loopeables desde el minuto cero. Rehacer una pieza lineal en stems después cuesta más que componerla bien de entrada [ver: gamedev/audio].

### Loops perfectos: producir el bucle que cierra sin salto

El detalle de preparación para el motor (formato, verificación) está en [ver: audio-a-juego]. Lo que toca al COMPOSITOR:

- Componer el loop para que el **final empalme con el inicio**: la última nota/energía debe fluir hacia el primer compás. El truco clásico: la cola de reverb/decay del final se solapa al principio (grabar/renderizar con "tail" y sumarla al arranque).
- Cortar el loop en el **ataque de un beat**, nunca en un decay a medias.
- Exportar en **OGG Vorbis o WAV/PCM, jamás MP3**: el MP3 mete padding de silencio al inicio/final → hueco audible en cada vuelta.
- Verificar con el loop sonando **10+ vueltas seguidas** antes de darlo por bueno. Herramienta útil: PyMusicLooper (open source) detecta puntos de loop y exporta intro/loop/outro.

---

## Ruta 2 — Música libre / Creative Commons

Gratis, pero "libre" tiene letra chica que puede costar un takedown en Steam si se ignora. La diferencia de licencia es un tema LEGAL, no un detalle.

### Entender las licencias (esto decide si puedes usarla)

| Licencia | ¿Atribución? | ¿Comercial? | Qué significa para tu juego |
|---|---|---|---|
| **CC0** (dominio público) | **No** | Sí | Libertad total: "you can do pretty much what you want... you could even sell the sound". La ideal para un juego |
| **CC-BY** (Attribution) | **Sí, obligatoria** | Sí | Usable comercial, PERO debes acreditar al autor con el formato que pide la licencia. Olvidarlo = infracción |
| **CC-BY-NC** (NonCommercial) | Sí | **No** | ⛔ Prohibida en un juego que se vende o monetiza. Evitar en proyectos comerciales |
| **CC-BY-SA** (ShareAlike) | Sí | Sí | Atribución + obliga a licenciar tu obra derivada bajo la misma licencia → problemática para un juego cerrado. Evitar salvo que entiendas la implicación |
| **Sampling+** (retirada) | Sí | Restringida | Licencia vieja de Freesound con límites en publicidad; ya no recomendada. Tratar con cuidado |

Fuente de las definiciones: Creative Commons (CC0 = "no attribution required"; CC-BY = "must provide credit") y el FAQ de Freesound.

### Fuentes fiables y su licencia real

| Fuente | Qué ofrece | Licencia | Ojo con |
|---|---|---|---|
| **Freesound** (freesound.org) | Enorme banco comunitario (más SFX que música) | **Mezcla**: CC0, CC-BY, CC-BY-NC, Sampling+ | Cada archivo tiene su propia licencia — **hay que revisarla uno por uno**. Filtrar por CC0 para evitar atribución |
| **Incompetech** (Kevin MacLeod) | Catálogo grande de música por género/mood | **CC-BY 4.0** (atribución obligatoria); existe opción de pago para usar SIN crédito | El precio exacto de la licencia sin-atribución NO lo verifiqué esta pasada → confirmar en la fuente. Suena "stock" (aparece en miles de proyectos) |
| **ende.app** (ex filmmusic.io, Sascha Ende) | Música royalty-free | **CC-BY 4.0**; aquí el autor hizo la atribución *voluntaria* pero la licencia base la exige | Cubre explícitamente "indie games, YouTube, TikTok". Aun así, acreditar es lo seguro |
| **Kenney** (kenney.nl) | Packs de audio de juego (Music Jingles, RPG Audio, etc.) | **CC0** (histórico y declarado por Kenney) | Confirmar CC0 en la página del pack; estilo casual/genérico |
| **Sonniss GameAudioGDC** (sonniss.com) | Bundle anual gratis de SFX profesional (no música) | Royalty-free, **sin atribución**, comercial, uso ilimitado | Prohíbe revender los archivos sueltos y **prohíbe entrenar IA** con ellos. Es SFX, ver [ver: crear-sfx] |
| **Pixabay** (pixabay.com) | Música y SFX gratis | Pixabay Content License (uso comercial sin atribución, con restricciones de reventa) | No pude verificar el texto de licencia esta pasada (403) → **leer la licencia vigente antes de usar**, no asumir |

### Qué NO es realmente libre (las trampas)

- **"Royalty-free" ≠ gratis ≠ dominio público**: significa "pagas/obtienes una vez, sin regalías por uso". Casi siempre hay un alcance (¿comercial? ¿atribución? ¿reventa prohibida?). Leerlo SIEMPRE.
- **Música de YouTube "no Content ID"**: que no dispare un claim en YouTube NO significa que tengas licencia para meterla en un juego. Son cosas distintas.
- **Clásica de dominio público**: la *composición* (Debussy, Bach) puede ser dominio público, pero **cada grabación tiene su propio copyright**. Usar una grabación ajena de Bach = infracción; hay que grabar/renderizar la tuya (así hizo Untitled Goose Game con Debussy) [ver: gamedev/audio].
- **CC-BY sin acreditar** = misma infracción que piratear. La atribución no es opcional en CC-BY.
- **Assets "gratis" en foros/Discord sin licencia escrita**: sin licencia documentada, no tienes derechos. Si no hay licencia, no se usa.

Regla operativa: por CADA track/sample que entra al juego, una fila en un registro de licencias (archivo, autor, licencia, URL, texto de atribución exacto). Sin esa fila, el asset no entra [ver: herramientas-recursos-audio].

---

## Ruta 3 — IA generativa de música (2026): úsala sabiendo dónde pisas

La IA de música (Suno, Udio, y modelos similares) produce piezas convincentes en segundos. El problema NO es la calidad — es la **licencia y los derechos**. Para un placeholder es genial; para música publicada en Steam es zona minada. Hay que ser honesto con los tres riesgos.

### El estado real de las herramientas

- **Suno** y **Udio** son las dos referencias de generación texto→canción a 2026. Calidad alta, especialmente para música de fondo/ambiente; menos control fino que un compositor.
- Sirven excelente para: **prototipos, placeholders, explorar direcciones musicales** que luego encargas a un humano. Pésima idea depender de ellas para el soundtrack final publicado sin entender lo de abajo.

### Riesgo 1 — Términos: ¿puedes usarlo comercialmente?

| Suno (suno.com/terms, verificado) | Qué dice |
|---|---|
| **Free / Basic** | Suno **retiene** la propiedad; solo uso "personal y no comercial" **y con atribución a Suno**. ⛔ No usable en un juego comercial |
| **Pro / Premier (pago)** | Suno **asigna** la propiedad del output al usuario y permite uso comercial. PERO: "makes no representation or warranty to you that any copyright will vest in any Output" — es decir, te lo cede pero NO garantiza que exista copyright que ceder |

- **Udio**: términos detrás de login, NO los pude verificar esta pasada. En general los planes de pago conceden derechos comerciales, pero **cambian seguido** → leer los términos vigentes antes de publicar. NO ASUMIR.
- Traducción: aun pagando, "es tuyo" viene con asterisco. Para música final, el plan gratis de cualquiera de estas queda descartado (no comercial + atribución forzada).

### Riesgo 2 — Copyright: aunque puedas usarlo, quizá no lo puedas proteger

- La **US Copyright Office** (copyright.gov/ai, reporte 2025) es clara: el output **puramente generado por IA no es registrable** — el copyright exige autoría humana. Solo las porciones con aporte creativo humano demostrable se protegen.
- Consecuencia práctica para tu juego: puedes *usar* la música IA, pero **no puedes impedir que otro la copie**. Tu "soundtrack exclusivo" no es exclusivo ni protegible. Para música de identidad de marca, eso es un problema real.

### Riesgo 3 — Datos de entrenamiento y litigios (el que puede tumbarte)

- Suno y Udio están demandados (RIAA / sellos, 2024 en adelante) por haber entrenado con grabaciones con copyright. El caso sigue abierto a 2026.
- Riesgo derivado: un output podría parecerse demasiado a material protegido, o el servicio podría cambiar términos/retirar contenido según cómo termine el litigio. Construir tu soundtrack sobre esa base es asumir un riesgo legal vivo.

### Riesgo 4 — Steam / publicación

- Steam (Valve) exige que **atestigües que tienes los derechos de TODO el contenido** del juego. Desde 2024 tiene un cuestionario de **divulgación de contenido IA** (categorías "Pre-Generated" y "Live-Generated"): hay que declarar que usaste IA y confirmar que tienes los derechos sobre los datos/salidas. Los detalles exactos del proceso cambian → **verificar la política vigente en Steamworks** antes de subir (no la memoricé al detalle esta pasada).
- Otras tiendas y plataformas de streaming del soundtrack (Spotify, etc.) tienen sus propias reglas anti-IA que hay que revisar por separado.

### Veredicto honesto sobre IA de música

| Uso | ¿Recomendable? |
|---|---|
| Placeholder / prototipo / explorar dirección | ✅ Sí, es su mejor uso |
| Música final de un juego comercial pequeño, plan de pago, leído todo | ⚠️ Posible pero riesgoso; documentar todo y aceptar que no es protegible |
| Música de identidad/marca del juego | ⛔ No: no la puedes proteger y el riesgo legal no compensa |
| Plan gratuito en cualquier cosa que se venda | ⛔ Prohibido por los términos (no comercial + atribución) |

---

## Ruta 4 — Contratar a un compositor

Cuando la música es identidad y hay presupuesto, un humano gana a todo lo anterior: piezas a medida, sin riesgo de licencia, y protegibles.

### Dónde encontrarlos

- Portafolios: comunidades de audio de juego, Bandcamp/SoundCloud de compositores de juegos, foros y Discords de game audio, plataformas de freelance especializadas. Escuchar antes de contactar.
- Señal de buen fit: que ya haya compuesto para juegos (entiende loops, stems, adaptividad) — no todos los músicos saben producir para interactividad [ver: gamedev/audio].

### Qué pedir en el encargo (checklist)

- [ ] **Referencias sonoras**: 3-5 tracks de otros juegos que definan el tono buscado (mood, instrumentación, energía).
- [ ] **Entregables por pista**: ¿master estéreo? ¿**stems separados** (para layering)? ¿versión **intro+loop**? ¿stingers? Se pide ANTES de que componga, no después.
- [ ] **Formato y specs**: WAV/OGG, sample rate, y picos con headroom (~9-12 dB bajo el máximo) para mezclar en el motor.
- [ ] **Derechos por escrito**: definir **work-for-hire** (el juego es dueño de la música) vs **licencia** (el compositor retiene la obra y te licencia el uso). Esto afecta soundtrack en streaming, DLC, ports y secuelas.
- [ ] **Buyout vs royalties**: ¿pago único que cierra todo (buyout) o el compositor cobra por ventas? El buyout simplifica; las royalties pueden salir caras si el juego pega.
- [ ] **Créditos y uso promocional**: cómo aparece en los créditos y si puedes usar la música en tráilers/marketing.
- [ ] **Revisiones**: cuántas rondas incluye el precio.

### Rango de coste (verificado 2025, ver [ver: gamedev/audio])

| Nivel | Tarifa por minuto de música terminada |
|---|---|
| Principiante / hobbyista | $50–150 |
| Intermedio con créditos | $200–1000 |
| Benchmark profesional | ~$1000 |
| Rango total del mercado indie | $50–2500 |

- Soundtrack indie completo: típicamente **$1,000–10,000**. Rush fees: +25–50%.
- Presupuesto de audio total razonable: **5–15% del proyecto** (incluye SFX y música).

---

## La decisión honesta según presupuesto y tipo de juego

| Situación | Ruta recomendada |
|---|---|
| **Game jam / prototipo, $0** | CC0 (Kenney, Freesound-CC0) o BeepBox/tracker propio. IA solo como placeholder |
| **Juego chico, música = relleno funcional, presupuesto mínimo** | Licenciar royalty-free (Incompetech CC-BY con crédito, o packs baratos). Registrar cada licencia |
| **Dev con oído musical, poco presupuesto, identidad importa** | Componer uno mismo en REAPER ($60) / LMMS / GarageBand. Máximo control, cero riesgo de licencia |
| **Juego comercial, música = identidad, hay algo de presupuesto** | Contratar compositor (buyout, stems, work-for-hire). Es la inversión que más se nota |
| **Necesitas explorar direcciones antes de encargar** | IA generativa como bocetador → luego el humano compone la versión final protegible |
| **Cualquier caso** | Nunca dejar la música para el final sin presupuesto ni tiempo asignado [ver: gamedev/audio] |

Verdad incómoda: la música IA "gratis y buena" tiene el peor perfil de riesgo/protección para algo que publicas y vendes. Para un juego real, o la compones, o la licencias con licencia clara, o la encargas. La IA brilla como herramienta de exploración, no como fuente del soundtrack final.

---

## Reglas prácticas

- [ ] Decidir la ruta (componer/CC/licenciar/IA/contratar) con partida presupuestaria ANTES de producir, no al final.
- [ ] Definir si el juego necesita música adaptativa ANTES de escribir/encargar: si sí, todo se produce en **stems + intro/loop** desde el minuto cero [ver: gamedev/audio].
- [ ] Un **registro de licencias** con una fila por CADA track/sample/loop: archivo, autor, licencia exacta, URL, texto de atribución. Sin fila, el asset no entra.
- [ ] En Freesound revisar la licencia archivo por archivo; filtrar por **CC0** para evitar atribución obligatoria.
- [ ] CC-BY = acreditar SIEMPRE con el formato que pide la licencia; ⛔ nunca usar CC-BY-NC en un juego comercial.
- [ ] Exportar loops en **OGG o WAV, jamás MP3**; estructura intro+loop; verificar **10+ vueltas** seguidas [ver: audio-a-juego].
- [ ] Stems alineados a la muestra (mismo largo/inicio exacto) o el vertical layering se desfasa.
- [ ] Componer el loop para que la cola empalme con el inicio (solapar el decay); cortar en el ataque de un beat.
- [ ] Exportar con headroom (~9-12 dB bajo el máximo) para mezclar en el motor [ver: unity/audio-unity].
- [ ] Clásica de dominio público: componer/grabar TU interpretación; nunca usar una grabación ajena.
- [ ] Apple Loops (GarageBand) / samplepacks del DAW: verificar el SLA — usables en tu obra, NO redistribuibles sueltos.
- [ ] IA de música: plan gratuito = ⛔ no comercial. Plan de pago = leer términos vigentes; asumir que el output **no es protegible** (US Copyright Office) y que hay litigio abierto sobre datos de entrenamiento.
- [ ] Antes de subir a Steam: atestiguar derechos de TODO el audio; si usaste IA, completar la divulgación IA vigente en Steamworks.
- [ ] Al contratar: pedir referencias, definir entregables (stems/loops), y cerrar derechos por escrito (work-for-hire o licencia; buyout o royalties).
- [ ] Elegir DAW por necesidad real: 2-3 loops → BeepBox/tracker; varias piezas o edición seria → REAPER (prueba 60 días) / LMMS / GarageBand.
- [ ] Guardar los proyectos fuente (`.rpp`, `.mmp`, módulos, stems) además del render final — para poder rehacer/ajustar sin recomponer.

## Errores comunes

| Error | Antídoto |
|---|---|
| Usar CC-BY sin acreditar (o acreditar mal) | Es infracción igual que piratear; incluir el texto de atribución exacto que pide la licencia y mantener el registro |
| Meter CC-BY-NC en un juego que se vende | NonCommercial prohíbe monetizar; filtrar esas pistas fuera del proyecto comercial |
| Asumir que "royalty-free" = gratis y sin condiciones | Leer el alcance: comercial, atribución, reventa. Royalty-free solo dice "sin regalías por uso" |
| Confiar en la música IA gratis para el soundtrack final | Plan gratis es no-comercial + atribución forzada; y el output IA no es protegible. Usar IA solo como placeholder/bocetador |
| Publicar en Steam sin declarar la IA usada | Steam exige divulgación de contenido IA y atestiguar derechos; completar el cuestionario vigente |
| Usar una grabación ajena de música clásica "porque es dominio público" | La composición puede serlo, la grabación no. Renderizar/grabar la tuya |
| Componer una pieza lineal y querer "hacerla adaptativa" después | Decidir adaptividad antes; producir en stems + intro/loop desde el inicio |
| Loop con hueco o "hipo" en cada vuelta | OGG/WAV (nunca MP3), empalmar cola con inicio, cortar en el ataque, probar 10+ vueltas |
| Stems que se desfasan al mezclarse en el motor | Exportarlos alineados a la muestra, mismo largo e inicio |
| Descargar assets "gratis" de un Discord sin licencia escrita | Sin licencia documentada no hay derechos; si no hay licencia, no se usa |
| Encargar música sin pedir stems ni cerrar derechos | Definir entregables (stems/loops) y derechos (work-for-hire/licencia, buyout/royalties) POR ESCRITO en el encargo |
| Aprender un DAW pesado "por si acaso" para 2 loops | Calibrar la herramienta a la necesidad: BeepBox/tracker para poco, DAW cuando compones varias piezas |
| Perder los proyectos fuente y quedarte solo con el WAV | Guardar los `.rpp`/módulos/stems para poder ajustar sin recomponer |

## Fuentes

- **BeepBox** — beepbox.co — editor de chiptune en el navegador; "BeepBox does not claim ownership over songs created with it" (el output es del autor); canción en la URL, exporta WAV.
- **LMMS** — lmms.io — DAW gratis, open source (GPL), Win/Mac/Linux; la licencia cubre el software, no tu música.
- **OpenMPT** — openmpt.org — tracker libre para Windows (edita IT/XM/S3M/MOD, soporta VST); v1.32.10, mayo 2026.
- **REAPER purchase** — reaper.fm/purchase — licencia con descuento $60 (ingreso bruto < $20k/año, o educación/ONG), comercial $225, evaluación 60 días completa y gratis.
- **GarageBand** — apple.com/mac/garageband — estudio de música gratis en Mac/iOS con Apple Loops; verificar el Apple SLA para uso comercial de los loops.
- **Suno Terms of Service** — suno.com/terms — free/basic: Suno retiene propiedad, uso no comercial + atribución; pro/premier: propiedad asignada al usuario y uso comercial, sin garantía de que exista copyright ("no representation or warranty that any copyright will vest").
- **US Copyright Office — AI** — copyright.gov/ai (reporte 2025, Parte 2) — el output puramente generado por IA no es registrable; solo las porciones con autoría humana demostrable se protegen.
- **Freesound FAQ (licenses)** — freesound.org/help/faq — CC0 (sin atribución, comercial), CC-BY (atribución obligatoria, comercial), CC-BY-NC (prohíbe comercial), Sampling+ (retirada); revisar cada archivo.
- **Creative Commons — CC0** — creativecommons.org/public-domain/cc0 — CC0 = renuncia total de derechos, sin atribución; CC-BY = retiene copyright y exige crédito.
- **Sonniss GameAudioGDC** — sonniss.com/gameaudiogdc — bundle anual gratis de SFX; royalty-free, sin atribución, comercial ilimitado; prohíbe revender archivos sueltos y entrenar IA con ellos.
- **Kenney (Audio)** — kenney.nl/assets/category:Audio — packs de audio de juego (Music Jingles, RPG Audio, etc.); CC0 (confirmar en la página del pack).
- **ende.app (ex filmmusic.io, Sascha Ende)** — ende.app/faq — música royalty-free CC BY 4.0; cubre "indie games, YouTube, TikTok"; atribución voluntaria en este sitio pero exigida por la licencia base.
- **jsfxr / sfxr** — sfxr.me — generador de SFX 8-bit; open source (UNLICENSE), uso comercial sin restricción, el output es tuyo (es SFX, ver crear-sfx).
- **Bfxr** — bfxr.net — generador de SFX de juego basado en sfxr; gratis, open source (verificar LICENSE del repo).
- **Incompetech (Kevin MacLeod)** — incompetech.com — música CC-BY 4.0 (atribución obligatoria) con opción de pago para usar sin crédito; precio exacto NO verificado esta pasada.
- **Steam / contenido IA (Valve, 2024→)** — política de divulgación de contenido IA en Steamworks (Pre-Generated / Live-Generated) + atestación de derechos; detalles exactos a verificar en la fuente vigente (NO verificado al detalle esta pasada).
- Base de teoría, adaptividad, middleware y tarifas de composición: [ver: gamedev/audio].
