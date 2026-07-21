# Música adaptativa e interactiva

> **Cuando cargar este archivo:** al diseñar, componer o implementar música que REACCIONA al juego — capas que entran/salen por intensidad (layering vertical), secciones que se encadenan por estado (resecuenciación horizontal), stingers de evento, transiciones sin corte, o música procedural/generativa. Es la profundización del sistema: la teoría base (funciones, adaptividad, silencio) está en [ver: gamedev/audio]; la implementación en el motor (AudioMixer, snapshots, PlayScheduled, dspTime) en [ver: unity/audio-unity]; cómo PRODUCIR los stems/loops en [ver: crear-musica] y [ver: produccion-musical]; dejarlos game-ready en [ver: audio-a-juego]; y el detalle de middleware en [ver: middleware-fmod-wwise]. Aquí va el DISEÑO del sistema adaptativo y cómo se cablea, cruzando esos archivos sin repetirlos.

---

## 1. Por qué la música de juego no es lineal

La diferencia estructural con el cine: **una escena de película dura lo que dura; una zona de juego dura lo que el jugador tarde.** El compositor no sabe si el jugador estará 30 segundos o 30 minutos en un sitio, ni cuándo entrará en combate. La música no puede ser un archivo que suena de principio a fin: es un **sistema de estados** que se estira, se encoge y reacciona.

Consecuencia práctica que cambia el encargo entero: el compositor no entrega "la pista", entrega **material modular + reglas de ensamblado** (stems, secciones loopeables, stingers, puntos de transición). Esto se decide ANTES de escribir la primera nota [ver: crear-musica; produccion-musical].

**iMUSE (Interactive MUsic Streaming Engine, LucasArts 1991)** es el origen de la disciplina — Michael Land y Peter McConnell. McConnell lo describía como "una orquesta de foso tocando secciones más cortas o más largas mientras espera que ocurran eventos clave en el motor del juego". El compositor insertaba **branch y loop markers** en la secuencia MIDI; la música cambiaba en esos puntos según las decisiones del jugador. Ejemplo canónico: en *Monkey Island 2* (Woodtick), al entrar a un edificio suena una variación del tema con otra instrumentación, y al salir hay un "floreo de cierre" que devuelve al tema base — transición atada a la acción, no a un cronómetro.

**Los tres ejes de adaptividad** (Wikipedia, *Adaptive music*) — qué se cambia en tiempo real:

| Eje | Qué cambia | Técnica | Sección |
|---|---|---|---|
| **Arreglo / textura** | Densidad e intensidad, MISMA pieza | Layering vertical (re-orquestación) | §2 |
| **Secuencia / forma** | La pieza entera, la dirección musical | Resecuenciación horizontal | §3 |
| **Generación** | El material se crea/ensambla en runtime | Procedural / generativa | §8 |

Sobre esos tres, dos herramientas puntuales: **stingers** (§4, golpe musical de evento) y **transiciones** (§5, cómo se pasa de un estado a otro). Parámetros continuos que cualquier eje puede modular: volumen por capa, tempo, filtro (low-pass = "amortiguar"), reverb.

---

## 2. Layering vertical (re-orquestación aditiva)

**Definición:** una SOLA pieza — misma tonalidad, mismo tempo, mismo compás, mismo largo — dividida en stems que entran y salen. Cambia la **intensidad/textura**, nunca la dirección musical. Todas las capas suenan (o están listas) desde el mismo instante y en fase; lo único que se mueve es su volumen.

### Aditivo vs re-armonización

| Variante | Qué hace | Costo | Cuándo |
|---|---|---|---|
| **Aditivo (layering)** | Las capas se SUMAN sobre un bed. +intensidad = +capas | Bajo | El default. 95% de los casos |
| **Re-orquestación / re-armonización** | Para el mismo grid, se sustituye la orquestación o la armonía (no solo se suma) | Alto (compones N versiones del mismo tramo) | Cuando "más fuerte" no basta y el mood debe cambiar de color sin cambiar de forma |

Caso maestro del aditivo: **Dead Space 2** organiza la música en cuatro capas de "miedo" (*fear layers*) mezcladas dinámicamente según la proximidad de los enemigos (Wikipedia). Journey (Austin Wintory) funde capas con el progreso [ver: gamedev/audio].

### Mapa de intensidad → capas (plantilla)

| Intensidad (0–1) | Estado | Capas activas |
|---|---|---|
| 0.0 | Exploración tranquila | `bed` (pad + bajo) |
| 0.3 | Alerta / tensión | + `perc_soft` (pulso suave) |
| 0.6 | Combate | + `perc_hard` + `brass/riff` |
| 1.0 | Clímax | + `lead/coro` (o re-orquestación) |

Dispararlo de dos maneras:
- **Continuo (RTPC):** un parámetro `intensity`/`threat` 0..1 mapea el volumen de cada capa por una curva. Suave, cinematográfico. Es el modo natural en middleware [ver: middleware-fmod-wwise].
- **Escalonado (estados discretos):** N snapshots del mixer (explore/alerta/combate/clímax) y `TransitionTo(t)` entre ellos [ver: unity/audio-unity §3]. Más simple, suficiente para indie.

### Reglas de composición del layering (las duras)

- **Todas las capas comparten tempo, compás, tonalidad y largo exacto** — alineadas a la muestra (mismo start/end). Es el error #1 de producción [ver: produccion-musical; crear-musica].
- **Cualquier subconjunto debe sonar completo.** El bed solo no puede sonar "a medias": se compone pensando "¿qué pasa si solo suena el bed?".
- **Reparto de frecuencias, no apilar melodías.** Cada capa ocupa su rango (bed = graves/pads, perc = transientes, lead = medios-agudos). Layering es arreglo orquestal, no cinco melodías compitiendo por el mismo hueco → barro.
- **Empezar TODAS a la vez y solo modular volumen** — nunca re-lanzar una capa a mitad, o entra fuera de fase. En nativo: `PlayScheduled` de todas al mismo `dspTime` [ver: unity/audio-unity §5].
- **Costo:** N stems sonando = N streams/N× memoria. En móvil, vigilar el módulo Audio del Profiler [ver: unity/audio-unity §2].

---

## 3. Resecuenciación horizontal (branching)

**Definición:** piezas o secciones DISTINTAS encadenadas según el estado del juego (exploración → tensión → combate → victoria/derrota). Cambia la pieza entera, la dirección musical. Cada estado es su propia pieza loopeable — `intro → loop → outro` [ver: audio-a-juego §5; crear-musica].

Ejemplos: **Celeste** (Lena Raine) — cada área/desafío su pista; **Hollow Knight** (Christopher Larkin) — horizontal por zona, con layering vertical dentro de la zona para el combate (el híbrido es lo normal en juegos buenos) [ver: gamedev/audio].

### Máquina de estados de música

El sistema es una FSM cuyos estados son piezas y cuyas aristas son transiciones (§5):

```
        ┌──────────────┐   enemigo cerca    ┌────────────┐
        │ EXPLORACIÓN  │ ─────────────────▶ │  TENSIÓN   │
        │  (loop)      │ ◀───────────────── │  (loop)    │
        └──────┬───────┘   sin amenaza      └─────┬──────┘
               │                                  │ combate
               │ victoria/derrota ◀──────┐        ▼
               ▼                    ┌─────┴──────────────┐
        ┌──────────────┐            │      COMBATE       │
        │ STINGER win/ │ ◀──────────│      (loop)        │
        │ lose (§4)    │  fin combate└────────────────────┘
        └──────────────┘
```

Regla de reparto: **horizontal para cambios de contexto grandes** (zona, fase de boss, momento narrativo); **vertical para el ajuste fino dentro del contexto**.

### Puntos de transición (lo que hace que no suene a corte)

No se salta de sección en cualquier sample: se espera a un **límite musical**. De más barato a más musical:

| Punto de salida (quantize) | Latencia percibida | Sensación |
|---|---|---|
| Immediate (corte seco) | 0 | Brusco — solo para shocks intencionales |
| Next beat | hasta 1 pulso | Ágil, sirve para reacciones rápidas |
| Next bar (compás) | hasta 1 compás | El default musical seguro |
| End of phrase / exit cue | hasta N compases | Lo más limpio; requiere marcar la frase |

### Transition segments (bridges)

Una frase compuesta **ex profeso** para el salto A→B: cierra A y prepara B. Es lo más musical y lo más caro (compones material que solo suena en la transición). En middleware es un objeto de primera clase (Wwise: *transition segment*; FMOD: *transition region/timeline*) [ver: middleware-fmod-wwise]. En nativo se emula reproduciendo un clip-puente entre el fin de A y el inicio de B con `PlayScheduled`.

---

## 4. Stingers y accents

**Definición:** frase MUSICAL corta (≈0.5–3 s) disparada por un evento puntual, que suena **por encima** de la música actual sin reemplazarla. No es un SFX: está en la tonalidad y el tempo del score.

| Evento | Stinger típico |
|---|---|
| Victoria / nivel superado | Cadencia mayor resuelta, floreo ascendente |
| Muerte / derrota | Caída cromática, cluster disonante, campana grave |
| Descubrimiento / secreto | Arpegio de arpa/campanas ascendente (el "¡ta-da!") |
| Peligro / boss aparece | Hit de brass/percusión, acorde de tensión |
| Pickup clave / logro | Motivo corto reconocible (el jingle de item) |

Reglas para que no choque:
- **Componerlo en la tonalidad del track base** (o en una nota/acorde común). Un stinger fuera de tono arruina el momento.
- **Cuantizar la entrada al beat/bar** — que caiga en tiempo, no en medio de un pulso [ver: unity/audio-unity §5, cálculo contra dspTime].
- **Dejar que decaiga sobre la música**; opcionalmente **duck** breve de la música bajo el stinger [ver: unity/audio-unity §3 ducking; direccion-audio-mezcla].
- Se reproducen en **2D** (no posicional) porque son score, no mundo.

**Es el primer escalón de adaptividad para un dev solo:** barato de producir e implementar, altísimo retorno emocional. Loops planos + tres stingers (victoria/muerte/descubrimiento) ya se sienten "vivos".

---

## 5. Transiciones: pasar de A a B sin corte feo

El menú completo, con valores y cuándo (profundiza la tabla de [ver: gamedev/audio]):

| Tipo | Valor típico | Cuándo usarla |
|---|---|---|
| **Corte seco** | 0 s | Game over, interrupción violenta, shock intencional |
| **Crossfade** | 0.5–2 s | Default seguro entre intensidades y zonas; el mínimo viable |
| **Cuantizado a beat/bar** | espera ≤1 compás | Cambios que deben sonar musicales; el sistema espera el límite |
| **Transition segment (bridge)** | frase dedicada | Lo más musical; puente compuesto A→B |
| **Sustain / hold + release** | indefinido | La música se "estaciona" en un punto hasta que el juego libera (puzzle, diálogo, menú) |

### La matriz de transición

Para cada par **(origen → destino)** se decide tres cosas:
1. **Exit point del origen** — cuándo sale (immediate / next beat / next bar / exit cue).
2. **Sync point del destino** — dónde entra (entry cue / mismo punto del compás que tocaba / inicio).
3. **Fade** — corte, crossfade N ms, o vía bridge.

Un juego con 4 estados de música tiene hasta 4×4 combinaciones; no todas necesitan regla propia, pero **cada salto que ocurra en el juego se prueba** — una transición rota rompe la inmersión más que la música mala. Middleware da esta matriz visual; en nativo se codifica a mano [ver: unity/audio-unity §5].

### Componer para que empalme

- **Cadencias que resuelvan** al final de cada loop, para poder re-entrar limpio.
- **Anacrusa / pick-up:** el destino puede arrancar con una nota de aproximación que "recoge" la salida del origen.
- **Notas/acordes comunes** entre las tonalidades de secciones adyacentes, o pasar por un **bridge neutro** (pedal, percusión sola) que borra la tonalidad antes de establecer la nueva [ver: teoria-musica-juegos].

---

## 6. Implementación: nativo (Unity) vs middleware

Decisión rápida (detalle en [ver: unity/audio-unity §6] y [ver: middleware-fmod-wwise]):

| Necesidad | Nativo Unity basta | Middleware paga su costo |
|---|---|---|
| Layering de 2–3 capas por estado | ✅ | opcional |
| Stingers cuantizados | ✅ | opcional |
| Horizontal con crossfade | ✅ | opcional |
| Transiciones por compás entre N estados + bridges | trabajoso | ✅ |
| Sound designer no-programador que itera solo | ❌ | ✅ |
| Mezcla en vivo en el dispositivo | ❌ | ✅ |

### Recetas nativas (Unity) — el cómo, sin repetir el código de [ver: unity/audio-unity]

- **Layering vertical:** un `AudioSource` por stem, TODOS con `PlayScheduled(mismoDspTime)` → siempre en fase. Cada stem sale por su grupo del mixer; se sube/baja con el exposed param y conversión log (`Mathf.Log10(v)*20`) en corutina, o con **snapshots** para escalones discretos (`TransitionTo`) [ver: unity/audio-unity §3, §5].
- **Horizontal:** calcular el próximo compás — `barLength = 60.0/bpm * beatsPorCompas` — y `PlayScheduled` del siguiente clip en ese múltiplo desde `AudioSettings.dspTime`; `SetScheduledEndTime` corta el actual sin click.
- **Stinger:** `PlayOneShot` en un source 2D, programado al próximo beat calculado contra `dspTime`.
- **Arquitectura:** un `MusicDirector` singleton con `DontDestroyOnLoad` que guarda el estado actual, el `bpm`/tempo map y el reloj musical, y expone `SetState(x)` / `SetIntensity(f)` / `FireStinger(y)` [ver: unity/audio-unity §5; hacer-audio-por-codigo].

### Middleware — está HECHO para esto [ver: middleware-fmod-wwise]

> Los mecanismos de abajo son de la documentación oficial de Wwise/FMOD (sistemas canónicos y estables). Los **nombres exactos de enum pueden variar por versión** y NO se re-verificaron en vivo en esta pasada (las docs bloquean el fetch); confirmar en la versión que uses.

**Wwise — Interactive Music Hierarchy:**
| Objeto | Rol |
|---|---|
| **Music Segment** | Unidad base; tiene *pre-entry / entry cue / exit cue / post-exit* (la parte "tocable" va entre cues) |
| **Music Track** | El audio dentro del segmento. Tipos: *normal*, *random step*, *sequence step*, *switch track* (← el switch track hace layering vertical por State/Switch) |
| **Music Playlist Container** | Secuencia segmentos → resecuenciación horizontal |
| **Music Switch Container** | Cambia de playlist/segmento según un State o Switch → control top-level del mood |

Transiciones: **matriz origen→destino** con *exit source at* (immediate / next grid / next bar / next beat / next cue / exit cue), *sync to* del destino, *transition segment* opcional y fades. **Stingers:** un *Trigger* dispara un segmento sincronizado a un *sync point*. **States** = mood global (combate/explora), **Switches** = por objeto, **RTPC** = parámetro continuo (p. ej. volumen de una capa).

**FMOD Studio:**
- Evento con **timeline**; **parámetros** local/global, tipo *continuous* / *labeled* / *discrete*, y *built-in* (Distance, Direction…).
- **Layering vertical:** automatizar el volumen de tracks/instruments sobre un parámetro (`intensity`).
- **Horizontal:** *loop regions*, *transition regions* y *transition timelines* con *destination markers*; *tempo markers* + *quantization* al compás.
- **Sustain points** para "estacionar" hasta que el juego libere; *multi instrument* y *scatterer instrument* para variación. **Seek speed** suaviza saltos de parámetro.

---

## 7. Componer los stems para que encajen (checklist de compatibilidad)

Cruza con [ver: produccion-musical] (producción) y [ver: crear-musica] (obtención); aquí la parte específica de adaptividad:

- **Mismo BPM** en todo el set (fijo). Si hay rubato/tempo variable, todos los stems y secciones comparten el mismo *tempo map*.
- **Mismo compás** y **mismo largo de loop** en compases enteros.
- **Misma tonalidad** para capas verticales; para horizontal, tonalidades de secciones adyacentes emparentadas (misma, relativa o dominante) o unidas por bridge [ver: teoria-musica-juegos].
- **Puntos de loop alineados a la muestra** — mismo start/end exacto entre capas, o el layering se desfasa (error #1) [ver: audio-a-juego §5].
- **Grid maestro:** componer todo contra un mismo click/tempo, exportar todos los stems desde el compás 1 del mismo proyecto.
- **Headroom por stem:** cada capa con margen porque van a SUMARSE; no maximizar assets individuales [ver: audio-a-juego §4; direccion-audio-mezcla].
- **Entregables:** master + stems etiquetados + `intro/loop/outro` + stingers + hoja de spec (qué capa = qué grupo del mixer, qué evento dispara cada stinger) [ver: audio-a-juego §1].

---

## 8. Música procedural / generativa (a nivel concepto)

**Definición:** la música se **genera o ensambla en runtime** desde piezas pequeñas + reglas, en vez de reproducir una pista pre-renderizada (Wikipedia: *algorithmic generation*, el tercer eje). Espectro de menos a más ambicioso:

| Enfoque | Qué es | Caso real |
|---|---|---|
| **Recombinación de fragmentos** | Trocear una obra en muchos fragmentos y encadenarlos por reglas | *Untitled Goose Game*: 5 preludios de Debussy en ~357 fragmentos × 2 intensidades, FMOD elige el siguiente al final de cada uno [ver: gamedev/audio] |
| **Recombinación de stems compuestos** | Un compositor escribe material, el motor lo samplea y re-ensambla en vivo | *No Man's Sky*: 65daysofstatic componen 10 tracks; se disgregan en snippets y el motor procedural los recombina por planeta (audio director Paul Weir) |
| **Generación por sistema de reglas** | Software musical genera notas/frases en tiempo real desde samples-semilla | *Spore*: Brian Eno + Peter Chilvers con **Pure Data** (Miller Puckette); Kent Jolly y Aaron McLeran diseñaron las composiciones generativas por etapa |
| **Reactivo al gameplay** | La generación responde a la intensidad/acción del jugador | *Ape Out*: batería de jazz algorítmica que reacciona a la violencia en pantalla |
| **Estocástico cuantizado a escala** | Elegir notas de una escala/acordes con probabilidad, cuantizadas al beat | Patrón "nunca suena mal" para ambient generativo de dev solo |

**Para un dev solo:** la **recombinación de fragmentos** y el **estocástico cuantizado a escala** son alcanzables (una lista de clips + reglas de encadenado + quantize a `dspTime`). La generación tipo Spore (motor de reglas con Pure Data) es un proyecto en sí mismo, no un "feature de audio".

**Licencia:** música procedural *artesanal* (tú compones el material y las reglas) es tuya. **NO es lo mismo que música generada por IA** en runtime — si metes un modelo generativo, aplican los riesgos de licencia/propiedad (output no exclusivo, términos por tier) [ver: herramientas-recursos-audio; audio-a-juego §8]. Y si el material base es una obra ajena (clásica), la composición puede ser dominio público pero **cada grabación tiene su copyright** — Goose Game grabó sus propias interpretaciones de Debussy [ver: gamedev/audio].

---

## 9. El presupuesto realista para un dev solo

Escalera de esfuerzo — el 80% del valor está en los primeros peldaños. **Elegir el más bajo que cumpla, no el más impresionante:**

| Nivel | Qué haces | Esfuerzo | Cuándo parar aquí |
|---|---|---|---|
| 0 | Un loop por zona + **silencio** en momentos clave | Mínimo | Juego corto/narrativo; el silencio ya es diseño [ver: gamedev/audio] |
| 1 | + **Stingers** de evento (victoria/muerte/descubrimiento) | Bajo | La mayoría de juegos chicos: máximo retorno por hora |
| 2 | + **Layering vertical** de 2–3 capas (explore/combat) | Medio | **El sweet spot indie.** Aquí para casi todo el mundo |
| 3 | + **Horizontal** por estados con crossfade cuantizado | Medio-alto | Juego con fases claras (boss, zonas de tensión) |
| 4 | + **Transition segments** compuestos + FSM completa | Alto | Justifica middleware |
| 5 | **Procedural** real (motor de reglas) | Proyecto dedicado | Solo si la generatividad ES el juego |

Reglas de calibración:
- **La mayoría de indies no pasan del nivel 2.** Layering simple basta. No construir una FSM de 8 estados para un juego de 3 pantallas.
- **Más adaptividad = más minutos que pagar/componer.** Un loop de 2 min en 3 capas ≈ producir ~6 min de material [ver: crear-musica, tarifas por minuto].
- **Middleware solo desde el nivel ≥4** o si hay un sound designer dedicado; por debajo, el stack nativo de Unity cubre todo [ver: unity/audio-unity §6; middleware-fmod-wwise].
- Presupuestar el **silencio** como parte del sistema: no es "falta de música", es un estado más de la FSM [ver: gamedev/audio].

---

## Reglas prácticas

- [ ] Decidir el **nivel de adaptividad (§9) ANTES de componer/encargar** — cambia el encargo entero (stems + secciones + stingers desde el minuto cero).
- [ ] Elegir el nivel MÁS BAJO que cumpla; para casi todo juego chico eso es **loops + stingers + 2–3 capas verticales**.
- [ ] Layering vertical: todas las capas **mismo tempo/tonalidad/compás/largo**, alineadas a la muestra; cualquier subconjunto suena completo.
- [ ] Componer el layering como **arreglo por rangos de frecuencia**, no melodías apiladas (bed=graves, perc=transientes, lead=medios-agudos).
- [ ] Lanzar todas las capas a la vez (`PlayScheduled` al mismo `dspTime`) y solo modular volumen — **nunca re-lanzar** una capa a mitad (se desfasa) [ver: unity/audio-unity §5].
- [ ] Horizontal: cada estado = pieza `intro/loop/outro` loopeable; transición en un **límite musical** (next beat/bar/cue), no en cualquier sample.
- [ ] Definir la **matriz de transición** (exit del origen + sync del destino + fade) y **probar cada salto** que ocurre en el juego.
- [ ] Stingers: en la **tonalidad del score**, cuantizados al beat, en 2D, con duck breve opcional de la música.
- [ ] Crossfade 0.5–2 s como transición por defecto; corte seco solo para shocks; bridge compuesto solo si el nivel lo justifica.
- [ ] Un **MusicDirector** singleton (`DontDestroyOnLoad`) que mantiene estado, tempo y reloj musical; API `SetState/SetIntensity/FireStinger` [ver: unity/audio-unity §5].
- [ ] Middleware (FMOD/Wwise) **solo desde nivel ≥4** o con sound designer dedicado; confirmar enum/versiones en las docs vigentes [ver: middleware-fmod-wwise].
- [ ] Cada stem con **headroom** (van a sumarse); balance fino en el mixer, no re-exportando assets [ver: audio-a-juego §4].
- [ ] Entregar master + stems etiquetados + intro/loop/outro + stingers + **hoja de spec** (capa→grupo del mixer, evento→stinger) [ver: audio-a-juego §1].
- [ ] Procedural artesanal alcanzable para dev solo = **recombinación de fragmentos** o **estocástico cuantizado a escala**; el motor de reglas tipo Spore es un proyecto aparte.
- [ ] Tratar el **silencio como un estado** de la máquina, no como ausencia [ver: gamedev/audio].
- [ ] Música generada por **IA** en runtime ≠ procedural artesanal: aplican riesgos de licencia/propiedad; clásica = composición libre pero grabación con copyright [ver: audio-a-juego §8].

## Errores comunes

| Error | Antídoto |
|---|---|
| Componer una pieza lineal y querer "hacerla adaptativa" después | Decidir el nivel (§9) antes; producir en stems + secciones desde el inicio [ver: crear-musica] |
| Capas verticales que se desfasan al mezclarse | Alinearlas a la muestra (mismo largo/inicio) y lanzarlas todas al mismo `dspTime`; nunca re-lanzar a mitad |
| Layering = apilar 5 melodías → barro | Reparto por rangos de frecuencia; cada capa su hueco, es arreglo orquestal |
| Cambio de sección "en cualquier momento" → corte a mitad de compás | Cuantizar la salida a beat/bar/cue; crossfade 0.5–2 s mínimo |
| Stinger que choca (fuera de tono o a destiempo) | Componerlo en la tonalidad del score y cuantizar la entrada al beat |
| Sobre-ingeniería: FSM de 8 estados para un juego de 3 pantallas | Calibrar al nivel más bajo que cumpla; casi siempre loops + stingers + 2–3 capas basta |
| Meter middleware por defecto "porque hace adaptativa" | Solo desde nivel ≥4 o con sound designer dedicado; nativo cubre lo demás [ver: unity/audio-unity §6] |
| N capas en Decompress On Load → pico de memoria en móvil | Streaming para material largo; vigilar el módulo Audio del Profiler [ver: unity/audio-unity §2] |
| Transiciones sin probar → una suena rota en producción | Recorrer la matriz completa; cada salto real del juego se escucha |
| "Procedural" = tirar un modelo de IA en runtime sin leer la licencia | IA ≠ procedural artesanal; documentar plan/propiedad/no-exclusividad [ver: audio-a-juego §8] |
| Usar una grabación de clásica ajena creyéndola "dominio público" | Composición libre ≠ grabación libre; grabar propia o licenciar la grabación (lección Goose Game) |
| Olvidar el silencio: música wall-to-wall que nunca calla | El silencio es un estado de la FSM; la música vuelve como evento [ver: gamedev/audio] |

## Fuentes

- **Adaptive music** — Wikipedia — definición, historia (Space Invaders 1978, Frogger, Monkey Island 2) y los tres ejes: vertical orchestration (Dead Space 2, cuatro *fear layers*), horizontal re-sequencing, algorithmic generation (Spore, Ape Out). Verificado 2026-07-21.
- **iMUSE** — Wikipedia — Michael Land y Peter McConnell (LucasArts, ~1991, patente 1994); "pit orchestra" tocando secciones mientras espera eventos; branch/loop markers; ejemplo Woodtick de *Monkey Island 2*. Verificado 2026-07-21.
- **No Man's Sky** (sección música) — Wikipedia — 65daysofstatic + audio director Paul Weir; 10 tracks compuestos, sampleados/disgregados y recombinados en runtime por el motor procedural; álbum *Journeys* (2025) ensamblado solo de loops/snippets del motor. Verificado 2026-07-21.
- **Spore (2008 video game)** (sección música) — Wikipedia — Brian Eno + Peter Chilvers con **Pure Data** (Miller Puckette) para la música generativa; Kent Jolly y Aaron McLeran diseñaron composiciones generativas por etapa a partir de samples de Eno. Verificado 2026-07-21.
- **Wwise Interactive Music** — Audiokinetic (documentación oficial; docs bloquean WebFetch, mecanismos canónicos conocidos, enum exactos a confirmar en la versión vigente) — Music Segment (cues), Music Track (incl. switch track = layering), Playlist/Switch Containers, matriz de transición, stingers, States/Switches/RTPC. Detalle en [ver: middleware-fmod-wwise].
- **FMOD Studio — Parameters / Music** — FMOD (documentación oficial; misma limitación de fetch) — parámetros local/global y continuous/labeled/discrete, automatización de volumen de tracks (layering), transition regions/timelines, tempo markers + quantization, sustain points, scatterer/multi instrument, seek speed. Detalle en [ver: middleware-fmod-wwise].
- **Bases ya verificadas del bloque** (no re-derivar aquí): comparativa vertical/horizontal, stingers, transiciones, silencio y los casos Journey / Celeste / Hollow Knight / Untitled Goose Game (Dan Golding; Em Halberstadt) / DOOM (Mick Gordon) en [ver: gamedev/audio]; implementación con AudioMixer/snapshots/PlayScheduled/dspTime y crossfade log (John Leonard French; Unity docs) en [ver: unity/audio-unity]; producción de stems alineados e intro+loop en [ver: crear-musica] y [ver: audio-a-juego].
