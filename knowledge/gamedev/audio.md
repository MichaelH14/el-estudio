# Audio: música y SFX

> **Cuando cargar este archivo:** al diseñar o implementar cualquier sonido del juego — SFX, música, ambiente, mezcla, loops, middleware — o al decidir presupuesto/recursos de audio para un equipo chico. Complementa a [ver: game-feel] (el audio es la mitad del juice).

## Las tres funciones del audio

El audio no es decoración: es un canal de información, un generador de atmósfera y la firma del juego. Winifred Phillips (*A Composer's Guide to Game Music*) enumera funciones concretas de la música: establecer un estado mental en el jugador, actuar como "audiencia virtual" que reacciona a sus logros y fracasos, anunciar personajes/tareas entrantes, y existir dentro del mundo (música diegética). Su meta central: sostener la **inmersión** — el estado donde el jugador olvida que está jugando.

| Función | Qué hace | Ejemplo real |
|---|---|---|
| **Feedback inmediato** | Confirma acciones, comunica estado del juego sin mirar | Overwatch: pilar "Gameplay Information" — cada sonido da datos tácticos; ultimates con línea de voz distinta para aliado vs enemigo |
| **Respuesta pavloviana** | Entrena al jugador: sonido → significado, sin tutorial | Overwatch lo lista como pilar explícito ("Pavlovian response"); tras horas, el jugador reacciona al sonido antes que a la pantalla |
| **Atmósfera / inmersión** | Define el tono emocional del espacio; el ambiente vende el mundo | Silent Hill: la quietud sofocante genera terror psicológico |
| **Identidad de marca** | Un sonido/estilo que ES el juego | DOOM 2016: el synth-metal de Mick Gordon es inseparable del juego; el HONK de Untitled Goose Game es su marketing entero |

Regla derivada: cada sonido debe justificar su existencia en al menos una de estas funciones. "¿Necesita estar ahí? ¿Suma valor?" — si no, fuera (Wayline).

### Diegético vs no diegético

- **Diegético**: existe dentro del mundo del juego (la radio que suena, los pasos, el NPC que canta). Los personajes lo oyen.
- **No diegético**: solo el jugador lo oye (score, stingers, sonidos de UI).
- Phillips destaca la música diegética como función propia: una radio encendible convierte la música en objeto del mundo (Goose Game nació justo así — la radio del tráiler). Cruzar la línea a propósito (la música del mundo se vuelve el score) es una herramienta narrativa barata y potente [ver: narrativa-guion].

## Diseño de SFX

### Capas (layering)

Un SFX pro no es una grabación: es varias capas mezcladas. Un disparo típico = acción mecánica + explosión/report + silbido de bala + reflexión del entorno, grabadas por separado. Beneficios:
- Control fino en la mezcla (subir el "punch" sin subir el brillo).
- **Variación combinatoria**: randomizar qué capas suenan multiplica los resultados — con pocas grabaciones sacas miles de sonidos distintos.

### Variación: el antídoto de la repetición

Mushel da la lógica cualitativa (rangos chicos = natural, rangos grandes = roto) sin cifra fija; los valores de la tabla son la convención más repetida en tutoriales de audio de juegos (NO hay un número único de consenso — tratarlos como punto de partida, ajustar a oído):

| Técnica | Valor típico | Nota |
|---|---|---|
| Muestras alternativas por sonido frecuente | 3–10 grabaciones | Pasos, golpes, impactos, UI |
| Randomización de pitch | ±10% aprox (algunas guías usan rangos en cents, más finos) | Rangos chicos suenan naturales; rangos grandes suenan rotos |
| Randomización de volumen | ±3 dB aprox | Sutileza > drama; valor repetido también en guías de Wwise |
| Round robin | Ciclo secuencial por el array | Lo mínimo aceptable |
| Random no-repeat | Re-tirar si sale el mismo índice | Mejor que random puro: evita el doble-clip |

Patrón Unity (Mushel): `clipIndex = (clipIndex + 1) % clipArray.Length` para round robin; para no-repeat, regenerar el índice mientras coincida con el anterior; `source.pitch = Random.Range(pitchMin, pitchMax)` antes de `PlayOneShot`.

### Prioridad y mezcla: el caso Overwatch (GDC 2016, "The Elusive Goal: Play by Sound")

El estándar de la industria para mezcla dinámica en juegos caóticos:
- En combate hay **12+ sonidos simultáneos** en un área chica. Sin sistema, es ruido.
- La mezcla NO sigue la física ("el más fuerte gana") sino la **importancia de gameplay**: un sistema asigna a cada sonido un valor de importancia **0–120** según amenaza real (tamaño del enemigo en tu pantalla, quién te dispara).
- Los sonidos caen en **4 buckets**: High / Medium / Low / **Cull** (se silencia). Cada bucket ajusta ganancia y filtros en Wwise.
- **Solo 1 sonido puede estar en High a la vez**: lo más importante del momento domina la mezcla.
- Pilares del equipo: mezcla limpia, localización precisa, información de gameplay, voces informativas, respuesta pavloviana.

Traducción para un juego chico: define 3–4 niveles de prioridad (crítico / feedback / ambiente / cosmético), garantiza que lo crítico SIEMPRE se oiga, y acepta silenciar lo cosmético cuando hay caos. El diálogo va por encima de todo — música, SFX y ambiente incluidos.

### Evitar fatiga auditiva

- **Sonidos cortos**: recorta colas; los pasos deberían durar menos de ~1/3 de segundo (GameAnalytics). Colas largas superpuestas = barro. Un toque de reverb disimula el corte.
- **Límites de instancia + cooldowns por objeto**: Untitled Goose Game configura en FMOD cuántas instancias de cada sonido pueden sonar y un tiempo de enfriamiento entre disparos del mismo objeto. Copiable en cualquier motor.
- **RTPC / parámetros**: en Goose Game la velocidad del impacto controla pitch y volumen del golpe — el mismo asset suena distinto según la física.
- Sonido de UI/notificación que suena 200 veces por sesión → el más suave y corto de todo el juego.

### Audio espacial (3D)

- **2D vs 3D**: UI, música y stingers en 2D (sin posición); todo lo que ocurre en el mundo, en 3D con atenuación por distancia. En Unity es el slider Spatial Blend; en FMOD/Wwise, el spatializer del evento.
- **Curvas de atenuación**: definir distancia mínima (volumen pleno) y máxima (inaudible) POR TIPO de sonido — un disparo se oye a 100 m, un paso a 10 m. La curva default del motor rara vez es la correcta para gameplay.
- La localización es información de gameplay: Overwatch la trató como pilar ("Pinpoint Accuracy") e invirtió en oclusión por ray tracing propio (el sonido rodea esquinas de forma creíble) para que el jugador ubique amenazas sin ver la pantalla. Detalle de implementación exacta (canales de delay, ratio distancia/tiempo) NO VERIFICADO en esta pasada — no se pudo confirmar contra el material fuente disponible. Un juego chico no necesita ese nivel, pero sí la versión barata: filtro low-pass + bajada de volumen cuando hay geometría entre fuente y oyente.
- Si el jugador debe reaccionar a lo que no ve (enemigos por la espalda, dirección del peligro), el posicionamiento del audio es mecánica, no cosmética.

### Ambiente: la base del soundscape

- El ambiente (room tone, viento, ciudad lejana) es lo que sostiene el mundo cuando la música calla. Sin él, el "silencio" suena a bug.
- Patrón estándar: **cama (bed) en loop largo + one-shots aleatorios** (pájaro suelto, crujido, coche que pasa) disparados con intervalo y posición randomizados — FMOD lo trae como scatterer instrument; a mano es un timer con `Random.Range`. La cama da continuidad; los one-shots matan la sensación de loop.
- Loops de ambiente largos (60 s+) para que el oído no detecte la repetición; cambiar de ambiente por zona con crossfade, nunca con corte.

## Música adaptativa

### Las dos técnicas base

| Aspecto | Vertical layering | Horizontal resequencing |
|---|---|---|
| Qué es | Una pieza dividida en stems (percusión, cuerdas, melodía) que entran/salen en tiempo real | Piezas o secciones distintas que se encadenan según el estado del juego |
| Cambia | Intensidad/textura, misma pieza | La pieza entera, dirección musical |
| Ideal para | Sigilo→detección, combate impredecible, exploración con tensión gradual | Fases de un boss, cambio de zona, momentos narrativos |
| Costo | Más memoria (stems simultáneos); mezclar todas las combinaciones | Transiciones pueden sonar abruptas si no hay sync points |
| Ejemplo | Journey (Austin Wintory): capas que se funden con el progreso | Celeste (Lena Raine): cada área/desafío con su pista |

- **Híbrido = lo normal en juegos buenos**: Hollow Knight (Christopher Larkin) usa horizontal para temas de zona y vertical para intensidad de combate dentro de la zona. Regla: horizontal para cambios de contexto grandes, vertical para ajuste fino dentro del contexto.
- **Stingers**: frases musicales cortas disparadas por eventos (descubierto, item clave, kill) que suenan POR ENCIMA de la música actual. Baratas de implementar y con mucho retorno. Para que no choquen: componerlos en la tonalidad del track base y (si el middleware lo permite) quantizar su entrada al beat.
- **Transiciones**: el menú de opciones, de más barata a más musical:

| Tipo | Cuándo usarla |
|---|---|
| Corte inmediato | Solo para shocks intencionales (game over, interrupción violenta) |
| Crossfade (0.5–2 s) | Default seguro entre estados de intensidad y zonas |
| Quantizada a beat/bar | Cambios que deben sonar musicales; el middleware espera al próximo compás |
| Frase de transición dedicada | Puente compuesto ex profeso entre sección A y B — lo más caro y lo mejor |

  Regla: probar TODAS las combinaciones de capas y todos los saltos de sección — las transiciones rotas rompen la inmersión más que la música mala. Componer para adaptividad se decide ANTES de escribir la música: pedir al compositor stems separados y secciones loopeables desde el encargo, no después (Phillips: escribir loops, chunks y fragmentos es EL skill diferencial del compositor de juegos).

### Caso maestro: Untitled Goose Game (Dan Golding)

Concepto: "un pianista de cine mudo improvisando sobre lo que pasa en pantalla". Implementación:
- 5 Preludios de Debussy, cada uno cortado en ~**357 fragmentos** (algunos de 0.04 s), grabados en DOS interpretaciones: alta energía y baja energía (más lenta y grave).
- 3 estados: persecución activa → versión alta energía; NPCs alerta → baja energía; nadie sabe nada → **silencio**.
- FMOD decide al final de cada fragmento cuál versión toca el siguiente → transiciones a nivel de frase musical, ~10^60 permutaciones posibles.
- Lección clave de Golding: el silencio hace que la entrada de la música sea el evento. La música que nunca para no comunica nada.

### Caso identidad: DOOM 2016 (Mick Gordon, GDC 2017 "DOOM: Behind the Music")

- El sonido del score (synth-metal distorsionado, proceso antes que preset) se diseñó como identidad del juego, no como acompañamiento.
- Preocupación práctica destacable: lograr que los graves funcionen en equipos malos (TV, laptop) — mezclar para el hardware real del jugador, no para el estudio.

## Cuándo NO poner música: silencio y ambiente

- El error default indie: llenar cada segundo con música. Resultado: los sentidos se adormecen y las señales importantes pierden impacto ("less is more", Wayline).
- El silencio es un **elemento activo** — espacio negativo, como en pintura. Momentos donde gana al score:
  - Horror/tensión: la imaginación del jugador es mejor compositor (Silent Hill).
  - Post-clímax: tras un boss o una escena fuerte, dejar que el peso asiente.
  - Puzzle: micro-silencio tras resolver → sensación de logro.
  - Telegrafía: cortar el audio (dropout) para señalar la ventana de vulnerabilidad de un boss.
- Procedimiento (Wayline): 1) identificar los momentos emocionales críticos, 2) auditar el soundscape actual, 3) quitar/atenuar selectivamente, 4) calibrar duración del silencio, 5) reintroducir sonidos gradualmente, nunca de golpe.
- "Silencio" en juegos casi nunca es silencio absoluto: es **ambiente** (viento, cuarto, tráfico lejano) sin música. El ambiente sostiene el mundo; la música opina sobre él. Si la música opina todo el tiempo, aburre.

## Implementación práctica

### Loops perfectos

- **MP3 no lupea**: el encoder mete padding de silencio al inicio/final → gap audible en cada vuelta. Para loops usar **OGG Vorbis** (lupea limpio y comprime bien) o WAV/PCM.
- Estructura pro: **intro + loop** (la pista arranca con su intro y luego repite solo la sección loopeable). Herramienta: PyMusicLooper (open source) encuentra loop points automáticamente y exporta intro/loop/outro.
- Cortar el loop en el punto de ataque de un beat, no en un decay; verificar con el loop sonando 10+ vueltas.

### Ducking

- Bajar automáticamente un bus cuando otro necesita espacio: música baja cuando entra diálogo o voz de tutorial; ambiente baja durante stingers.
- FMOD y Wwise lo traen de fábrica (sidechain/auto-duck entre buses). En audio nativo se implementa a mano: al reproducir voz, tween del volumen del bus de música hacia abajo y de vuelta al terminar.
- Punto de partida razonable (ajustar a oído): duck de 4–8 dB con fades de ~0.2–0.5 s. Heurística propia, no de fuente — lo no negociable (fuente: pitfalls de mezcla) es que el diálogo se entienda SIEMPRE.

### Límites de canales y prioridad

- Todo motor tiene un tope de voces reales sonando a la vez; el resto se virtualiza o se descarta.
- Unity (verificado en docs): `AudioSource.priority` va de **0 (máxima) a 256 (mínima)**; al llegar al límite de voces, Unity virtualiza primero las de menor prioridad, y a igual prioridad, la de menor volumen. Música y diálogo → prioridad alta (cerca de 0); partículas y cosméticos → prioridad baja.
- Complemento del lado del diseño: límites de instancias por evento + cooldowns (patrón Goose Game) para que 30 monedas no disparen 30 voces.

### Middleware vs audio nativo del motor

| | Audio nativo (Unity/Godot/UE built-in) | Middleware (FMOD Studio / Wwise) |
|---|---|---|
| Costo inicial | Cero setup | Integración + curva de aprendizaje |
| Música adaptativa | A mano (crossfades por código) | Nativo: capas, sync points, quantización a compás |
| Iteración del sound designer | Toca el proyecto del motor | Herramienta propia; edita y mezcla sin tocar código |
| Ducking/mezcla por buses | Parcial (Unity AudioMixer sí tiene ducking) | Completo y visual |
| Licencia indie | Incluida en el motor | FMOD: gratis bajo ~$200k revenue/año y <$500k de funding; Wwise: gratis con presupuesto de producción <$250k, sonidos ilimitados. **Verificar términos vigentes antes de decidir** — cambian |

Decisión práctica: jam/prototipo/juego chico con música simple → nativo alcanza. Música adaptativa seria, mezcla compleja o un sound designer no-programador en el equipo → middleware paga su costo. Goose Game (equipo de 4) usó FMOD; Overwatch usó Wwise.

### Optimización

- Formatos comprimidos (OGG) para música/ambiente largos, con **streaming** en vez de cargar a memoria; SFX cortos descomprimidos o comprimidos en memoria.
- Culling de audio: no procesar sonidos que nadie puede oír (lejos, tapados por la mezcla).
- Exportar assets con headroom: picos ~9–12 dB bajo el máximo (GameAnalytics), para que la suma de sonidos no clippee y la mezcla se haga en el motor.
- Probar la mezcla en el hardware real del jugador: audífonos, TV, altavoz del teléfono (lección DOOM + pitfalls de mezcla).

## Recursos para devs chicos

### SFX

| Recurso | Qué es | Licencia |
|---|---|---|
| **Sonniss GameAudioGDC** | Bundle anual gratuito por GDC (2026: ~7.5 GB, 347 WAV de Boom Library, Krotos, etc.); archivo histórico 200+ GB | Royalty-free, comercial, sin atribución; prohíbe entrenar IA con los archivos |
| **freesound.org** | Comunidad enorme de grabaciones | Licencias CC variadas — filtrar por CC0 para evitar atribución; revisar cada archivo |
| **Kenney.nl** | Packs de SFX/assets estilo casual | CC0 |
| **sfxr / Bfxr / jsfxr / ChipTone** | Generadores procedurales de SFX retro (blips, saltos, explosiones 8-bit) — un botón, mil variaciones | Libres; el sonido generado es tuyo |
| **Foley casero** | Grabar tú mismo: el foley entero de Goose Game se grabó en la casa/patio de Em Halberstadt (guante de goma para las patas del ganso) | Tuyo; un teléfono + habitación silenciosa da resultados usables |

### Música

- **Bibliotecas royalty-free**: Incompetech (Kevin MacLeod) y similares — gratis con atribución. Riesgo: música que suena a "stock" y aparece en mil juegos = cero identidad.
- **Contratar composición** (rangos verificados 2025, Ninichi/GameSoundCon/Twine):

| Nivel | Tarifa por minuto de música terminada |
|---|---|
| Principiante/hobbyista | $50–150 |
| Intermedio con créditos | $200–1000 |
| Benchmark profesional | ~$1000 |
| Rango total del mercado indie | $50–2500 |

- Presupuesto típico de soundtrack indie completo: **$1,000–10,000**. Presupuesto de audio total razonable: **5–15% del proyecto** (GameAnalytics). Rush fees: +25–50%.

### Derechos (lo mínimo que hay que saber)

- **Royalty-free ≠ gratis ≠ dominio público**: significa "pagas/obtienes una vez, sin regalías por uso". Leer SIEMPRE el alcance: ¿comercial? ¿atribución? ¿reventa del asset prohibida?
- Al contratar: aclarar por escrito si es **work-for-hire** (el juego es dueño de la música) o **licencia** (el compositor retiene la obra y te licencia el uso). Afecta soundtrack en streaming, DLC, ports y secuelas.
- Música clásica: la composición puede ser dominio público (Debussy), pero **cada grabación tiene su propio copyright** — Goose Game grabó sus propias interpretaciones.
- Contenido con cláusulas anti-IA (p. ej. Sonniss): usable en el juego, no para entrenar modelos.

## Reglas prácticas

- [ ] Audio desde el primer prototipo, no al final: placeholder desde el día uno, con tracking de estado (rojo=falta, naranja=roto, amarillo=cambiar, verde=final).
- [ ] Cada sonido justifica su existencia: feedback, atmósfera o identidad. Si no, se elimina.
- [ ] Todo sonido que suena >5 veces por sesión tiene ≥3 variaciones + pitch ±10% + volumen ±3 dB, con random no-repeat.
- [ ] Sonidos frecuentes cortos (pasos < ~0.3 s), colas recortadas.
- [ ] Sistema de prioridad de 3–4 niveles; lo crítico para gameplay siempre se oye; lo cosmético se sacrifica primero.
- [ ] Diálogo/voz por encima de todo en la mezcla, con ducking automático de música.
- [ ] Límite de instancias + cooldown por evento de sonido (que 30 pickups no sean 30 voces).
- [ ] Música adaptativa: horizontal para cambios de contexto, vertical para intensidad dentro del contexto; stingers para eventos puntuales.
- [ ] Transiciones musicales quantizadas a compás; probar TODAS las combinaciones de capas y saltos.
- [ ] Presupuestar silencio: identificar los momentos donde la música NO debe sonar y protegerlos. El ambiente sostiene esos huecos.
- [ ] Toda zona tiene su cama de ambiente (loop 60 s+) con one-shots aleatorios encima; transición entre zonas con crossfade.
- [ ] Sonidos del mundo en 3D con curvas de atenuación definidas por tipo; UI/música/stingers en 2D.
- [ ] Loops en OGG o WAV, jamás MP3; estructura intro+loop; verificar 10+ vueltas seguidas.
- [ ] Exportar assets con picos 9–12 dB bajo el máximo; mezclar dentro del motor.
- [ ] Probar la mezcla en ≥3 salidas: audífonos, altavoces de TV/monitor, altavoz de teléfono.
- [ ] SFX tonales afinados a la tonalidad de la música (evitar disonancia accidental).
- [ ] Sliders de volumen separados como mínimo: master / música / SFX (/ voz si hay).
- [ ] Middleware solo si el proyecto lo amerita (música adaptativa seria o sound designer dedicado); verificar términos de licencia vigentes.
- [ ] Presupuesto: ~5–15% del proyecto a audio; guardar registro escrito de la licencia de CADA asset de audio usado.
- [ ] Pedir feedback de audio en playtests explícitamente (¿qué sonido cansa? ¿qué no se oye?).

## Errores comunes

| Error | Antídoto |
|---|---|
| Audio al final del desarrollo, sin presupuesto ni tiempo | Guía sonora en preproducción junto a la visual; placeholders desde el prototipo [ver: preproduccion] |
| Un solo sample repetido (pasos-metralleta "de drum machine 80s") | Variaciones + round robin + randomización de pitch/volumen |
| Música wall-to-wall que nunca calla | Estados de silencio/ambiente; la música como evento, no como fondo permanente |
| Mezcla plana: todo al mismo volumen, diálogo enterrado | Buses + prioridades + ducking; el diálogo gana siempre |
| Loop con gap o "hipo" en cada vuelta | OGG/WAV, loop points en el ataque del beat, probar 10+ repeticiones |
| Sobre-procesamiento: reverb/compresión en todo | Procesar con intención; el efecto sirve al espacio del juego, no al ego del diseñador |
| WAVs gigantes sin comprimir cargados a memoria en móvil | OGG + streaming para pistas largas; culling de sonidos inaudibles |
| Mezclar solo con audífonos de estudio | Probar en TV, laptop y teléfono — el hardware real del jugador (lección DOOM) |
| SFX stock reconocibles que matan la identidad | Layering/procesado propio sobre las bibliotecas, o foley casero (Goose Game) |
| Ignorar derechos: música "bajada de internet", grabaciones de clásica ajenas | Registro de licencias; composición = dominio público ≠ grabación libre |
| Sin controles de volumen separados | Sliders música/SFX/voz — también es accesibilidad [ver: ux-ui-onboarding] |
| Botear el feedback sonoro de acciones core (golpe sin sonido = golpe débil) | El audio es la mitad del game feel; cada acción core tiene su capa de sonido [ver: game-feel] |

## Fuentes

- **Overwatch — The Elusive Goal: Play by Sound** — Blizzard audio team, GDC 2016 (writeup en Awesome Game Audio) — el sistema de mezcla por importancia (0–120, 4 buckets) que define el estándar de prioridad de SFX.
- **Making Your Game's Music More Dynamic: Vertical Layering vs. Horizontal Resequencing** — The Game Audio Co — comparativa directa de las dos técnicas base con ejemplos (Journey, Celeste, Hollow Knight) y consejos de transición.
- **5 Audio Pitfalls Every Game Developer Should Know** — The Game Audio Co — los errores estructurales (audio tardío, loops repetitivos, mezcla pobre, optimización, feedback).
- **Behind the charming sound design for Untitled Goose Game** — A Sound Effect (entrevista a Em Halberstadt) — foley casero, RTPC, límites de instancia y cooldowns en FMOD.
- **Honk! (música de Untitled Goose Game)** — Gameplay.co (sobre el sistema de Dan Golding) — 357 stems por preludio, 2 intensidades, 3 estados, el silencio como estado musical.
- **The Power of Silence: Mastering Audio Deprivation in Game Design** — Wayline — cuándo y cómo usar silencio; procedimiento de 5 pasos.
- **Sound Effect Variation in Unity** — Andrew Mushel — round robin, random no-repeat y randomización de pitch/volumen con código concreto.
- **9 Sound Design Tips to Improve your Game's Audio** — GameAnalytics — heurísticas numéricas: duración de SFX, headroom de exportación (9–12 dB), presupuesto 5–15%, tracking por colores.
- **DOOM: Behind the Music** — Mick Gordon, GDC 2017 (writeups en Sockrotation y 80.lv; charla completa en GDC YouTube) — identidad sonora como diseño y mezcla para hardware real.
- **A Composer's Guide to Game Music** — Winifred Phillips, MIT Press (vía reseña de Sound on Sound y MIT Press) — funciones de la música, inmersión, loops/chunks/fragmentos generativos como skills del compositor de juegos.
- **AudioSource.priority** — Unity Documentation (ScriptReference) — prioridad 0–256 y virtualización de voces, verificado.
- **Licencias FMOD/Wwise indie** — Bugnet, GameFromScratch, Game Developer — umbrales de las licencias gratuitas (FMOD ~$200k revenue; Wwise $250k budget).
- **Sonniss GameAudioGDC** — sonniss.com / gdc.sonniss.com — bundle anual royalty-free sin atribución; archivo 200+ GB; cláusula anti-IA.
- **Tarifas de composición indie** — Ninichi Music, GameSoundCon, Twine — rangos por minuto y presupuestos totales de soundtrack.
- **Loops sin gaps** — PyMusicLooper (GitHub), hilos de OC ReMix y html5gamedevs — el gap de MP3 y la estructura intro+loop en OGG.
