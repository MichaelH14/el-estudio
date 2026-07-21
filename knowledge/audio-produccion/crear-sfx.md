# Crear efectos de sonido (SFX)

> **Cuando cargar este archivo:** cuando hay que PRODUCIR o CONSEGUIR los efectos de sonido de un juego siendo un equipo chico o solo — sintetizarlos con generadores, grabarlos con foley casero, editarlos de una biblioteca, o elegir packs con la licencia correcta, y dejarlos limpios para el motor. La TEORÍA de qué sonido poner y por qué (funciones del audio, capas, prioridad, ambiente) está en [ver: gamedev/audio]; la IMPLEMENTACIÓN en Unity (pool, variación, import settings, mixer) en [ver: unity/audio-unity]; la música en [ver: crear-musica]; el catálogo de herramientas/recursos en [ver: herramientas-recursos-audio]; y la preparación técnica final del asset en [ver: audio-a-juego]. Aquí va el CÓMO producir/conseguir cada SFX.

## Las cuatro vías de un dev solo

Ninguna es "la buena": un juego real mezcla las cuatro. La regla de decisión es coste-de-tiempo vs identidad-necesaria.

| Vía | Qué es | Cuándo | Coste | Identidad |
|---|---|---|---|---|
| **Síntesis (generador tipo sfxr)** | Un botón genera blips/saltos/explosiones 8-bit procedurales | Jam, prototipo, juego retro/arcade, UI | Minutos, gratis | Genérica-retro (todos usan las mismas) |
| **Foley casero** | Grabar objetos reales con teléfono/micro | Necesitas identidad propia, sonidos orgánicos (pasos, tela, impactos) | Horas, casi gratis | Máxima: nadie tiene tu grabación |
| **Editar samples de biblioteca** | Bajar un WAV y recortarlo/procesarlo/apilarlo | El 80% de los SFX "reales" (armas, motores, naturaleza) | Rápido si sabes editar | Media: layering + proceso la sube |
| **Bibliotecas listas** | Usar el pack tal cual | Ambiente, one-shots de relleno, deadline | Instantáneo | Baja: sonido "stock" reconocible |

Combinar es lo normal: un impacto pro = capa de biblioteca + foley propio + una cola sintetizada, apilados [ver: gamedev/audio, sección layering].

---

## Vía 1 — Síntesis: generadores tipo sfxr

### Qué son y cómo funcionan

sfxr (DrPetter, 2007) es un sintetizador de un solo propósito: SFX de videojuego retro. No grabas nada — mueves ~20 parámetros (forma de onda, envolvente attack/sustain/decay, slide de frecuencia, vibrato, arpegio, filtros) y suena. La gracia son los **botones-preset**: cada uno tira parámetros aleatorios dentro del rango típico de ese tipo de sonido, y el botón **Mutate/Randomize** genera variantes del sonido actual — así sacas 10 monedas ligeramente distintas en segundos [ver: unity/audio-unity, variación].

### Los presets (mapeo acción → botón)

Verificado en jsfxr (sfxr.me). Los mismos botones existen en sfxr, Bfxr y jsfxr:

| Acción del juego | Botón | Ajuste típico después |
|---|---|---|
| Recoger moneda/ítem | **Pickup/Coin** | Subir pitch para objetos "pequeños/valiosos" |
| Disparar | **Laser/Shoot** | Bajar frecuencia + más sustain = arma pesada |
| Explosión, muerte, daño grande | **Explosion** | Subir decay + ruido = más "sucio" |
| Subir de nivel, buff, recompensa | **Powerup** | Arpegio ascendente = "positivo" |
| Golpe recibido, colisión | **Hit/Hurt** | Corto + ruido = impacto seco |
| Salto | **Jump** | Slide de frecuencia hacia arriba |
| Click / seleccionar en menú | **Blip/Select** | El más corto y suave del juego (suena 200×/sesión) |
| Explorar por azar | **Random** | Punto de partida y luego Mutate |

### Herramientas (estado 2026, licencias verificadas)

| Tool | Plataforma | Exporta | Licencia del sonido generado | Nota |
|---|---|---|---|---|
| **jsfxr** (sfxr.me) | Navegador | WAV + JSON gratis; MP3/OGG/sfxr/ZIP en Pro | **UNLICENSE (dominio público); uso comercial sin restricción** (verificado sfxr.me) | El más cómodo; Pro añade packs y sync |
| **Bfxr** (bfxr.net) | Navegador + descarga | WAV (Ctrl+E), .bfxr (Ctrl+S) | Herramienta bajo **Apache 2.0**; increpare permite usar los sonidos libremente. **Verificar la nota de la web antes de publicar** | Más parámetros que sfxr; incluye Footsteppr para pasos |
| **ChipTone** (SFBGames, itch.io) | HTML5 + Win/macOS | Descarga de audio | **Sonidos CC0** — "FREE to use for any purpose, commercial or otherwise" (verificado en la página) | Gratis; sumando sampler/sequencer |
| **sfxr / rFXGen** (escritorio) | Win/Linux/macOS | WAV | Original sfxr = dominio público; rFXGen (raysan5) es el port moderno mantenido | Offline, sin depender de web |

### Cuándo bastan (y cuándo no)

- **Bastan**: game jam, prototipo, juego con estética retro/pixel/arcade declarada, y SIEMPRE para SFX de UI (clicks, hover, error, confirmar) aunque el juego no sea retro — un blip corto de sfxr para la UI es invisible y perfecto.
- **No bastan**: cuando el juego busca realismo o identidad sonora propia. El sonido sfxr es reconocible ("esto salió de sfxr") y aparece en miles de jams. Ahí toca foley o biblioteca procesada.
- Truco de camuflaje: pasa un sonido sfxr por reverb/EQ/bitcrush en Audacity y deja de sonar tan "crudo-sfxr".

---

## Vía 2 — Foley casero

El foley entero de *Untitled Goose Game* se grabó en la casa y el patio de Em Halberstadt (un guante de goma para las patas del ganso) [ver: gamedev/audio]. Un teléfono y una habitación silenciosa dan resultados publicables.

### Equipo, de menos a más

| Equipo | Calidad | Nota |
|---|---|---|
| **Micro del teléfono** (app de grabadora de voz) | Usable | Grabar en WAV/sin comprimir si la app deja; acercarse mucho a la fuente |
| **App tipo grabadora + auriculares** | Usable+ | Monitorear para oír ruido de fondo que el oído ignora |
| **Micro USB** (cardioide, tipo Blue Yeti / Samson) | Buena | El salto de calidad más grande por el dinero; USB directo, sin interfaz |
| **Micro dinámico + interfaz / grabadora de campo** (Zoom H1/H4) | Pro | Solo si el audio es central en el juego |

Regla: **acercar el micro más que subir la ganancia**. Ganancia alta = ruido de fondo alto. Micro cerca (5–20 cm) = señal fuerte y limpia.

### El cuarto silencioso (tratamiento gratis)

El enemigo no es el eco, es el **ruido de fondo constante** (nevera, aire, calle, PC) y la **reverb del cuarto**.

- Grabar de noche, apagar nevera/aire/ventiladores, teléfono en modo avión.
- Contra la reverb: grabar dentro de un **clóset lleno de ropa**, o rodear el micro de almohadas/mantas, o meterse bajo un edredón. La ropa absorbe las reflexiones → sonido "seco" que luego puedes espacializar en el motor.
- Nunca grabar en un baño o cuarto vacío con eco: esa reverb queda "horneada" y no se quita.
- Grabar 2–3 s de **room tone** (silencio del cuarto) para que la reducción de ruido de Audacity tenga de dónde aprender el perfil.

### Objetos que suenan a otra cosa (sustituciones foley clásicas)

El truco central del foley: la fuente real casi nunca suena bien; un objeto cotidiano suena mejor. Estas son sustituciones estándar de la industria:

| Sonido buscado | Objeto que lo produce |
|---|---|
| Fuego / llamas | Arrugar papel celofán o bolsa plástica lento |
| Lluvia | Sal/arroz cayendo sobre papel o sartén; freír algo |
| Trueno / lámina de metal | Sacudir una lámina de metal fina o cartón grueso |
| Huesos rotos, ramas, crujidos | Partir apio, zanahoria o palitos de madera |
| Pasos en nieve | Apretar una bolsa de maicena (fécula de maíz) rítmicamente |
| Pasos en pasto/tierra | Pisar cinta de casete enredada, o una esponja húmeda |
| Puñetazo / impacto de carne | Palmear un filete crudo, golpear un repollo o sandía |
| Aleteo de alas | Sacudir un par de guantes o abrir/cerrar un paraguas |
| Espada desenvainada | Deslizar un cuchillo por el borde de una sartén/metal |
| Cascos de caballo | Dos mitades de coco (o tazas) sobre una superficie |
| Ropa / cuero de personaje | Apretar guantes de cuero cerca del micro |
| Chapoteo / burbujas | Soplar con una pajilla dentro de un vaso de agua |
| Cristal roto | Dejar caer un puñado de cubiertos + un vaso real, mezclados |

### Técnica de grabación

- Grabar **muchas tomas** de cada acción (para variación y para elegir la mejor). Pasos: 8–12 tomas del mismo pie.
- Dejar un segundo de silencio antes y después de cada toma → recortes limpios.
- Exagerar: el foley que suena "demasiado" en la grabación suele sonar justo en el juego con música encima.
- Grabar a volumen sano sin clipear (picos que no toquen el techo; si la app muestra rojo, alejarse o bajar ganancia). Un clip grabado ya viene roto y no se arregla [ver: audio-a-juego].

---

## Vía 3 — Editar samples (Audacity y afines)

La mayoría de los SFX "reales" salen de bajar un WAV de biblioteca y **editarlo**. Editor de facto gratis: **Audacity 3.7.8, GPLv3, gratis, Win/macOS/Linux** (verificado audacityteam.org). Alternativas: **ocenaudio** (gratis, ligero, multiplataforma, no open source) para ediciones rápidas; **Tenacity** (fork de Audacity sin telemetría, para quien la prefiera).

### Operaciones básicas (menú Effect de Audacity)

| Operación | Dónde | Para qué |
|---|---|---|
| **Recortar / trim** | Seleccionar + suprimir, o Edit > Trim | Quitar silencio inicial (ataque tardío = SFX que llega tarde) y cola sobrante |
| **Normalizar** | Effect > Normalize | Llevar el pico a un nivel fijo (ej. −3 a −1 dB) y quitar DC offset (opción del efecto) |
| **Amplify / ganancia** | Effect > Amplify | Subir/bajar un sonido concreto sin re-normalizar todo |
| **Fade in / out** | Effect > Fade In / Fade Out | Evitar el "click" al principio/fin (arranques y cortes en no-zero-crossing chasquean) |
| **Cambiar pitch (sin cambiar duración)** | Effect > Change Pitch | Variantes, o afinar un SFX tonal a la tonalidad de la música [ver: gamedev/audio] |
| **Cambiar tempo (sin cambiar pitch)** | Effect > Change Tempo | Acortar/alargar sin agudizar |
| **Cambiar velocidad (pitch + tempo juntos)** | Effect > Change Speed | El truco viejo: bajar velocidad = más grave y grande (monstruo); subir = pequeño/rápido |
| **Reducción de ruido** | Effect > Noise Reduction | 1) Seleccionar room tone → "Get Noise Profile"; 2) seleccionar todo → aplicar. No pasarse: exceso = sonido "submarino/robótico" |
| **EQ** | Effect > Filter Curve EQ / Graphic EQ | Cortar graves de retumbe (<80 Hz), quitar sibilancia, dar "cuerpo" o "brillo" |
| **Compresor** | Effect > Compressor | Emparejar dinámica de un SFX con picos muy dispares |
| **Reverb** | Effect > Reverb | Dar espacio; usar con MUCHA moderación — mejor espacializar en el motor [ver: unity/audio-unity] |

### Layering (apilar capas en pistas)

Un SFX con cuerpo casi nunca es un archivo — son varias capas mezcladas [ver: gamedev/audio, layering]. Regla de las 3 capas para un impacto:

| Capa | Función | Fuente típica |
|---|---|---|
| **Ataque / transient** | El "punch", el golpe inicial | Foley seco, click sintético, sub-boom corto |
| **Cuerpo / crunch** | El carácter, la textura del medio | Sample de biblioteca (madera, metal, carne) |
| **Cola / decay** | El espacio, cómo muere | Reverb, un whoosh, un zumbido bajo |

En Audacity: cada capa en su pista, alinear los ataques, ajustar volumen relativo, y **Tracks > Mix > Mix and Render** a un WAV. Guardar el proyecto .aup3 por si hay que remezclar. Beneficio extra: randomizar qué capas suenan multiplica variantes [ver: unity/audio-unity].

### Variación (generar variantes)

Los sonidos frecuentes necesitan 3–10 variantes para no fatigar [ver: gamedev/audio; unity/audio-unity]. Dos caminos:

- **En runtime (preferido)**: exportar 1 clip y dejar que el motor randomice pitch ±5–10% y volumen ±15% (Audio Random Container / pool en Unity). Menos assets, más variación.
- **Horneadas**: exportar 3–5 WAV con Change Pitch a ±1–3 semitonos o distintas tomas de foley. Úsalo cuando la variación deba sonar deliberada (no solo pitch), o para pasos con superficies distintas.

---

## Vía 4 — Bibliotecas: usar el pack, pero con la licencia correcta

⚠️ **La licencia es un tema legal serio en un juego que se publica.** "Gratis de bajar" ≠ "libre de usar en tu juego comercial". Verificar SIEMPRE la licencia del archivo concreto (no del sitio) y guardar registro escrito.

### Bibliotecas y sus licencias (verificadas 2026)

| Recurso | Qué es | Licencia | Atribución | Comercial |
|---|---|---|---|---|
| **Sonniss #GameAudioGDC** (sonniss.com) | Bundle anual gratis por GDC; archivo de ~10 años de packs | Royalty-free, uso ilimitado; **NO revender los archivos crudos como librería**; **prohibido entrenar IA con ellos** (verificado) | **No requerida** | Sí (juegos, cine, apps, ads) |
| **Kenney.nl** | Packs de SFX casual (UI, impactos, sci-fi, RPG, casino…) | **CC0 (dominio público)** (verificado kenney.nl/support) | No requerida (agradecida) | Sí, sin restricción |
| **Freesound.org** | Comunidad enorme, calidad y licencia **variables por archivo** | **CC0 / CC-BY / CC BY-NC** + legado Sampling+ (verificado) | Depende: CC0 no; CC-BY sí | CC0/CC-BY sí; **CC BY-NC NO** |
| **ChipTone / jsfxr / Bfxr** | Generadores (Vía 1) | CC0 / dominio público según tool | No | Sí |

### La regla de licencias (lo que no se puede ignorar)

| Licencia | Puedes | Debes | Ojo |
|---|---|---|---|
| **CC0 / dominio público** | Todo: usar, modificar, comercial | Nada | Lo más seguro para un juego que vende |
| **CC-BY (Attribution)** | Usar, modificar, comercial | **Acreditar**: `"nombre" por usuario (URL) — CC-BY 4.0` | Sirve una pantalla de créditos o un archivo CREDITS/readme, no hace falta acreditar en cada disparo (verificado Freesound) |
| **CC BY-NC (NonCommercial)** | Uso no comercial | Acreditar | ⛔ **Inservible para un juego que cobra o monetiza.** Evitar |
| **Royalty-free (Sonniss, packs comerciales)** | Usar una vez comprado/bajado, ilimitado | Leer el alcance | Casi siempre **prohíbe revender el archivo crudo** como pack; sí permite incrustarlo en tu juego |

- ⚠️ **Ojo, esto NO es igual para todas las licencias** (error común): bajo **CC0 el propio Freesound dice explícitamente "you could even sell the sound"** — revender el archivo crudo está permitido, solo no puedes reclamar que tú lo creaste (verificado freesound.org/help/faq). Bajo **CC-BY** también puedes comercializar/revender, pero con atribución. La prohibición estricta de **revender/redistribuir el archivo crudo como librería** es una cláusula **contractual de los packs royalty-free** (Sonniss GameAudioGDC lo prohíbe explícitamente) — no una restricción de las licencias Creative Commons en sí. No confundir ambos regímenes.
- **Filtrar Freesound por CC0** te ahorra la contabilidad de atribuciones. Si usas CC-BY, mantén el crédito desde el día uno o luego es un infierno rastrear cuál sonido era de quién.

### Registro de licencias (obligatorio)

Un `CREDITS.md` / hoja con **una fila por asset de audio usado**: archivo, autor, URL de origen, licencia, fecha. Sin esto, en el lanzamiento no puedes probar que tienes derecho a usar cada sonido, y una reclamación te obliga a rehacer audio a último minuto [ver: audio-a-juego].

---

## IA generativa de audio (estado 2026): úsala con los ojos abiertos

Existen generadores de SFX/voz/música por texto (ElevenLabs Sound Effects, Stable Audio, Meta AudioCraft/AudioGen/MusicGen open-weights, Suno/Udio para música, entre otros). Son útiles para bocetar o rellenar, pero el riesgo es **legal, no técnico**. Estado a inicio de 2026 (verificar cada punto antes de publicar — este campo cambia rápido y no se pudo re-verificar con fuentes frescas en esta pasada):

| Riesgo | Qué mirar |
|---|---|
| **Datos de entrenamiento** | Modelos entrenados con audio sin licenciar arrastran disputas. Suno y Udio fueron demandados por sellos discográficos (2024); a inicio de 2026 el asunto no estaba resuelto públicamente. Preferir tools que declaren datos **licenciados** (ej. Stable Audio dice entrenar con catálogo licenciado — confirmar términos vigentes) |
| **Derechos del output** | Que la web te genere un sonido no significa que puedas venderlo. Leer el **ToS**: ¿te ceden uso comercial? ¿del plan gratis o solo de pago? Muchos limitan comercial al tier pagado |
| **Licencia de los pesos (open-weights)** | Meta liberó modelos con licencias que en algunos casos fueron **no comerciales** para ciertos pesos (ej. MusicGen). Usar el modelo ≠ derechos comerciales sobre lo generado. Verificar la licencia del checkpoint concreto |
| **Copyright de lo generado** | La Copyright Office de EE. UU. sostiene que obra **puramente** generada por IA **no es registrable** — no puedes reclamar propiedad exclusiva de ese SFX; cualquiera podría reusar uno idéntico |
| **Voz** | Clonar voces reales sin permiso es campo minado (derecho de imagen/voz). Freesound añadió en 2026 un panel de preferencias anti-IA con protección específica para grabaciones de voz (verificado) |

Recomendación honesta: para SFX, sfxr + foley + biblioteca CC0 te dan cobertura legal total y suficiente calidad; la IA generativa de audio hoy **añade riesgo legal a cambio de comodidad**. Si la usas, que sea de una tool con ToS que ceda uso comercial explícito, guarda captura del ToS con fecha, y trátalo como boceto a reemplazar, no como asset final blindado.

---

## El set mínimo de SFX de un juego

Antes de producir, listar lo que el juego NECESITA sonar. La regla base: **cada acción del jugador tiene su sonido** — un golpe sin sonido es un golpe débil [ver: gamedev/game-feel]. Set mínimo por categoría:

| Categoría | SFX típicos | Vía recomendada |
|---|---|---|
| **UI / menús** | Hover, click/confirmar, atrás/cancelar, error, abrir/cerrar panel, notificación | sfxr (blips cortos) |
| **Acciones del jugador** | Saltar, aterrizar, correr/pasos, atacar, disparar, recargar, dash, usar ítem | Foley (pasos) + biblioteca/sfxr (armas) |
| **Feedback / consecuencia** | Recibir daño, morir, recoger ítem/moneda, subir nivel, checkpoint, victoria/derrota | sfxr (pickup/powerup) + layering |
| **Mundo / entidades** | Enemigo aparece/muere, puerta, cofre, trampa, botón/palanca, romper objeto | Biblioteca + foley |
| **Ambiente** | Cama de room tone/viento/ciudad en loop + one-shots (pájaro, gota, crujido) | Biblioteca (loops largos) [ver: gamedev/audio] |

Priorizar: primero los sonidos de las acciones **core** que el jugador repite miles de veces (pasos, ataque, UI). Esos merecen variación y cuidado; el resto puede ser placeholder hasta el final [ver: gamedev/audio, tracking por colores].

---

## Formato y limpieza para el motor

El asset que exportas debe entrar limpio al juego. Detalle fino de import (Load Type, compresión, Force To Mono) en [ver: unity/audio-unity]; preparación/naming/pipeline en [ver: audio-a-juego]. Lo esencial al exportar el SFX:

| Regla | Valor | Por qué |
|---|---|---|
| **Fuente en WAV** (lossless) | 16-bit PCM basta para SFX | El motor re-comprime igual; guardar el master sin pérdida. Nunca partir de MP3 (padding/artefactos) |
| **Mono para SFX posicional/3D** | 1 canal | El paneo 3D lo hace el motor; estéreo en un sonido 3D es memoria tirada. Estéreo solo para UI/2D con imagen ancha |
| **Sample rate** | 44.1 kHz estándar; 22.05 kHz aceptable para SFX sin agudos (móvil) | Recorta memoria a la mitad sin pérdida audible en sonidos graves/opacos |
| **Headroom, sin clipping** | Picos ~**−9 a −12 dB** bajo el máximo (o al menos −3 dB) | La suma de muchos SFX + música no debe clipear; la mezcla se hace en el motor [ver: gamedev/audio] |
| **Recortar silencio inicial** | Ataque al ~inicio del archivo | Silencio delante = SFX que suena tarde tras el trigger; mata el game feel |
| **Fade micro en los extremos** | 2–10 ms fade in/out | Un corte en no-zero-crossing produce un "click" audible |
| **Quitar DC offset** | Opción de Normalize | Offset = clicks y pérdida de headroom |
| **Recortar colas largas** | Sonidos frecuentes cortos (pasos < ~0.3 s) | Colas superpuestas = barro; un toque de reverb disimula el corte [ver: gamedev/audio] |

---

## Reglas prácticas

- [ ] Antes de producir, listar el **set mínimo** por categoría (UI / acciones / feedback / mundo / ambiente) y marcar cuáles son acciones core repetidas.
- [ ] Cada acción del jugador tiene su sonido desde el prototipo, aunque sea placeholder sfxr [ver: gamedev/game-feel].
- [ ] UI y SFX retro → sfxr/jsfxr/Bfxr/ChipTone; pasos y sonidos orgánicos → foley; armas/naturaleza → biblioteca editada.
- [ ] Combinar vías: los SFX con cuerpo se apilan (ataque + cuerpo + cola), no se bajan de un archivo [ver: gamedev/audio].
- [ ] Foley: acercar el micro antes que subir ganancia; grabar en clóset/con almohadas contra la reverb; capturar 2–3 s de room tone.
- [ ] Grabar muchas tomas por sonido (variación + elegir la mejor), con silencio antes/después para recortar limpio.
- [ ] Editar en Audacity/ocenaudio: recortar silencio inicial, normalizar (−3 a −1 dB) + quitar DC offset, fade micro en los extremos.
- [ ] Reducción de ruido con perfil del room tone; sin pasarse (exceso = sonido submarino).
- [ ] Variación por runtime (pitch ±5–10%, volumen ±15% en el motor) antes que hornear muchos WAV [ver: unity/audio-unity].
- [ ] Exportar **mono** todo SFX 3D/posicional; estéreo solo UI/2D.
- [ ] WAV lossless como master; sample rate 44.1 kHz (22.05 kHz para SFX opacos en móvil); picos −9 a −12 dB, sin clipping.
- [ ] Verificar la **licencia del archivo concreto** (no del sitio) antes de usar cualquier sample; preferir CC0.
- [ ] ⛔ Descartar CC BY-NC en juegos que monetizan; acreditar todo CC-BY en un CREDITS desde el día uno.
- [ ] Mantener un `CREDITS.md` con una fila por asset: archivo, autor, URL, licencia, fecha.
- [ ] IA generativa de audio solo como boceto, con ToS que ceda uso comercial explícito + captura fechada; nunca como asset final blindado.
- [ ] Camuflar el sonido "sfxr crudo" con EQ/reverb/bitcrush si el juego no es abiertamente retro.
- [ ] SFX tonales afinados a la tonalidad de la música (Change Pitch) para evitar disonancia [ver: gamedev/audio].

## Errores comunes

| Error | Antídoto |
|---|---|
| Bajar un archivo "gratis" y usarlo sin mirar la licencia | Verificar CC0/CC-BY/BY-NC del archivo concreto; CREDITS con una fila por asset |
| Usar un sonido **CC BY-NC** en un juego que se vende | BY-NC prohíbe uso comercial: filtrar por CC0/CC-BY; reemplazar antes de lanzar |
| Asumir que "no revender el crudo" aplica igual a toda licencia | Es cláusula de los **packs royalty-free** (Sonniss lo prohíbe explícito); **CC0 sí permite revender el crudo** (Freesound: "you could even sell the sound", solo no reclamar autoría); CC-BY lo permite con atribución |
| Todo el juego suena "sacado de sfxr" | sfxr para UI/retro; foley/biblioteca procesada para el resto; camuflar con EQ/reverb |
| Foley con ruido de fondo constante (nevera, calle, PC) | Grabar de noche, modo avión, clóset con ropa; capturar room tone y reducir ruido |
| Grabar con clipping (picos en rojo) | El clip viene roto y no se arregla: alejar micro / bajar ganancia y regrabar |
| Reverb del cuarto "horneada" en la grabación | Grabar seco (ropa/almohadas) y espacializar en el motor, no en la grabación |
| SFX con silencio delante → suena tarde tras el trigger | Recortar el silencio inicial; el ataque va al inicio del archivo |
| "Click" al inicio/fin del SFX | Fade micro 2–10 ms en los extremos; cortar en zero-crossing |
| Exportar estéreo un SFX 3D | Mono: el paneo lo hace el motor; estéreo es memoria y espacialización tirada |
| Exportar al tope (0 dB) y clipping al sumar con música | Dejar headroom −9 a −12 dB; la mezcla final se hace en el motor [ver: gamedev/audio] |
| Sobre-procesar (reverb/compresión en todo) | Procesar con intención; el efecto sirve al espacio del juego |
| Confiar en IA generativa como asset final sin leer ToS/derechos | Tratarla como boceto; verificar cesión comercial + copyright del output; guardar ToS fechado |
| Un solo clip de pasos repetido (efecto metralleta) | 3–10 tomas de foley + variación de pitch/volumen en runtime [ver: unity/audio-unity] |

## Fuentes

- **jsfxr** — sfxr.me (Chris McCormick, port de sfxr de DrPetter/Eric Fredricksen) — presets (Pickup, Laser, Explosion, Powerup, Hit, Jump, Blip), export WAV/JSON (Pro: MP3/OGG/ZIP), licencia UNLICENSE / uso comercial sin restricción. Verificado 2026.
- **Bfxr** — bfxr.net (increpare) + github.com/increpare/bfxr — generador basado en sfxr, export WAV (Ctrl+E) / .bfxr (Ctrl+S), Footsteppr para pasos; código Apache 2.0. Verificado 2026.
- **ChipTone** — sfbgames.itch.io/chiptone (SFBGames) — generador gratis; sonidos generados **CC0**, uso comercial libre (cita literal de la página). Verificado 2026.
- **Audacity** — audacityteam.org — editor multipista gratis, v3.7.8, GPLv3, Win/macOS/Linux; efectos Change Pitch/Tempo/Speed, Noise Reduction, Normalize, Fade, EQ, Compressor. Verificado 2026.
- **BeepBox / LMMS** — beepbox.co (MIT; el autor no reclama las canciones) y lmms.io (DAW libre open source, 16 sintes, VST/SoundFont) — herramientas de música, detalle en [ver: crear-musica]. Verificado 2026.
- **Freesound** — freesound.org/help/faq — licencias CC0 / CC-BY / CC BY-NC (+ legado Sampling+); atribución de CC-BY (formato y ubicación flexible); **CC0 sí permite revender el crudo** ("you could even sell the sound", sin reclamar autoría — cita literal de la FAQ, no confundir con la prohibición de reventa de los packs royalty-free); panel anti-IA añadido en 2026. Verificado 2026.
- **Sonniss #GameAudioGDC** — sonniss.com/gameaudiogdc — bundle anual gratis, royalty-free, sin atribución, sin revender crudos, **prohibido entrenar IA**. Verificado 2026.
- **Kenney** — kenney.nl/support y kenney.nl/assets/category:Audio — packs de SFX **CC0**, comercial sin atribución (agradecida). Verificado 2026.
- **Middleware (FMOD/Wwise) y sus licencias** — tratadas en [ver: gamedev/audio] y [ver: unity/audio-unity]; verificar cifras vigentes en fmod.com/licensing y audiokinetic.com antes de decidir (páginas no accesibles vía fetch en esta pasada; NO re-verificadas aquí).
- **IA generativa de audio 2026** — estado general a conocimiento de inicio de 2026 (demandas Suno/Udio 2024 sin resolución pública; licencias no comerciales en algunos pesos open-weights; postura de la US Copyright Office sobre obra puramente-IA no registrable). NO re-verificado con fuentes frescas en esta pasada — tratar cada afirmación como punto a confirmar antes de publicar.
