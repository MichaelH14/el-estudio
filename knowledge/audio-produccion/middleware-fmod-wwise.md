# Middleware de audio: FMOD y Wwise

> **Cuando cargar este archivo:** cuando el audio del juego deja de caber cómodo en el pipeline nativo del motor — música adaptativa compleja, cientos de sonidos con comportamiento propio, un sound designer que necesita iterar sin tocar código, o mezcla final en el dispositivo real — y hay que decidir/operar FMOD Studio o Wwise. La implementación nativa en Unity (AudioSource/AudioMixer/PlayScheduled) está en [ver: unity/audio-unity]; la teoría de música adaptativa en [ver: musica-adaptativa] y [ver: gamedev/audio]; la mezcla/dirección en [ver: direccion-audio-mezcla]; la preparación de assets en [ver: audio-a-juego]. Aquí va SOLO qué es el middleware, cuándo se paga solo y cómo se opera.

---

## 1. Qué es un middleware de audio y por qué existe

Un **middleware de audio** es un par [herramienta de autoría + motor de runtime] que se mete ENTRE los archivos de audio y el motor del juego. El sound designer arma todo el comportamiento sonoro (variación, capas, transiciones, mezcla, efectos) en una app tipo DAW, exporta **banks** de datos, y el programador solo dispara **events por nombre**. El audio deja de ser código.

**El problema que resuelve** (lo que el pipeline nativo hace a medias [ver: unity/audio-unity §6]):

| Con audio nativo (Unity) | Con middleware |
|---|---|
| El programador autorea el sonido: pool de sources, pitch aleatorio, PlayScheduled, crossfades a mano en C# | El sound designer autorea en su herramienta; C# solo dispara `event:/...` |
| Cada cambio de un sonido = tocar código o el inspector + recompilar/entrar a Play | El designer itera en la app y hace **Live Update** contra el juego corriendo |
| Música adaptativa = corutinas de PlayScheduled + capas + dspTime (funciona, pero artesanal) | Transiciones por compás, capas verticales y stingers son primitivas nativas de la herramienta |
| Mezcla = AudioMixer del editor, en Play mode | Mixer visual con snapshots/VCAs, editable **en el dispositivo real** mientras juegas |
| Variación = Audio Random Container / pool | Randomización de volumen/pitch/selección integrada en cada sonido |

El AudioMixer de Unity cubre buses, snapshots y ducking (§3 de [ver: unity/audio-unity]) — es "middleware a medias". El middleware de verdad añade: **autoría desacoplada del código**, **música interactiva de primera clase** y **mezcla en vivo en target**.

---

## 2. La tabla de decisión honesta: nativo vs FMOD vs Wwise

| Señal del proyecto | Nativo del motor basta | FMOD se paga solo | Wwise se paga solo |
|---|---|---|---|
| Nº de sonidos | Decenas–bajos cientos | Cientos con comportamiento propio | Miles, con lógica por sonido |
| Música | Por estados/crossfade (PlayScheduled) | Adaptativa con transiciones a compás | Adaptativa AAA, layering profundo, muchos estados |
| Equipo | Dev solo / programador que también hace audio | Sound designer que itera sin bloquear al programador | Estudio con audio dedicado / varios diseñadores |
| Mezcla | Snapshots del AudioMixer bastan | Mezcla final en device con Live Update | Mezcla AAA con HDR, buses jerárquicos, profiling fino |
| Plataformas | 1–2 | Multiplataforma con un solo proyecto de audio | Multi-consola con reuso del proyecto de audio |
| Presupuesto/legal | Cero fricción de licencia | Gratis bajo cierto budget (§3) | Free tier limitado + fees por plataforma (§3) |

**Regla para un dev solo o indie chico:** el stack nativo de [ver: unity/audio-unity] cubre casi todo (variación, música por estados, ducking, mezcla). Middleware es **sobreingeniería** salvo que se cumpla ≥1 de: (a) hay sound designer dedicado, (b) la IDENTIDAD del juego es su audio adaptativo (música que reacciona por capas/compás a N estados), (c) mezcla final en dispositivo real, (d) reuso del audio entre varios motores/plataformas. **FMOD** es la puerta de entrada más suave (más simple, budget-based free). **Wwise** es el estándar AAA: más potente y más pesado de aprender/operar.

---

## 3. Licencias indie a 2026 (⚠️ legal serio — confirmar SIEMPRE en la web oficial)

Publicar un juego con middleware sin el tier correcto es un problema legal. Los términos cambian; verificar el tramo del proyecto ANTES de comprometerse.

### FMOD (Firelight Technologies)

Modelo **por presupuesto de desarrollo del título** (fuente: Wikipedia FMOD, actualizada 2026-07-20; **la página oficial `fmod.com/licensing` no fue accesible al scraper en esta pasada** — confirmar cifras y el trámite vigente ahí):

| Tier | Presupuesto de desarrollo del proyecto | Coste |
|---|---|---|
| **Non-Commercial** | Software no comercial | Gratis |
| **Indie** | < US$600k | Gratis (registrar el proyecto — confirmar el trámite) |
| **Basic** | US$600k – US$1.8M | De pago (fee por título — **monto NO VERIFICADO**, ver fmod.com/licensing) |
| **Premium** | > US$1.8M | De pago (fee mayor — **NO VERIFICADO**) |

- El **plugin FMOD for Unity** es gratis en el Asset Store y soporta Unity 6; la LICENCIA de FMOD es aparte del plugin. **NO VERIFICADO** en esta pasada: versión exacta del plugin y Unity mínima soportada (cambian con cada release — confirmar en el Asset Store).
- Wikipedia no menciona fees por título concretos; el modelo histórico de FMOD es un **fee único por título por tramo de budget** (no royalties). Confirmar.

### Wwise (Audiokinetic)

Modelo **por licencia comercial + tiers**, con free tier limitado. **La página oficial `audiokinetic.com/pricing` devolvió 403 al scraper y Wikipedia no publica cifras** — todo lo numérico aquí es **NO VERIFICADO**; confirmar en la web oficial antes de shippear:

| Tier (estructura histórica) | Para quién | Límite / coste |
|---|---|---|
| **Trial / No comercial** | Aprender, prototipos | Gratis; inserta silencio/ruido tras superar un umbral de assets — no se puede shippear |
| **Wwise Free (comercial)** | Juegos comerciales pequeños | Gratis hasta un **límite de media assets únicos por plataforma** (el número ha cambiado entre versiones — **NO VERIFICADO el vigente 2026**) |
| **Indie** | Indies bajo cierto revenue/budget | Fee por plataforma (**monto NO VERIFICADO**) |
| **Commercial / Pro** | Estudios | Fee por plataforma por título (**NO VERIFICADO**) |

- La integración **Wwise para Unity** se instala vía el **Wwise Launcher** (gratis); el runtime/uso comercial es lo que licencia el tier.
- Wikipedia solo confirma: Wwise es "gratis para uso no comercial y bajo licencia para desarrolladores comerciales". Sin números.

> **Regla honesta:** para cifras exactas de FMOD Basic/Premium y de CUALQUIER tier de Wwise, entrar a la web oficial y leerlas — no fiarse de este archivo para el monto. Lo verificado aquí: los **tramos de budget de FMOD** (Wikipedia 2026-07-20) y que **Indie de FMOD es gratis < $600k**.

---

## 4. FMOD Studio: conceptos y operación

FMOD Studio es "una herramienta de creación de audio para juegos, diseñada como una DAW" (Wikipedia). El sound designer trabaja en la **sesión** (`.fspro`) y exporta **banks**.

| Concepto | Qué es |
|---|---|
| **Event** | La unidad que dispara el juego (`event:/SFX/Explosion`). Contiene tracks, instrumentos, parámetros, automatización y efectos. Un event = un "sonido" con toda su lógica dentro |
| **Instrument** | Lo que suena dentro de un track del event. Tipos: *Single*, *Multi* (elige entre varios clips), *Scatterer* (dispersa clips en el tiempo/espacio), *Event* (anida otro event), *Programmer* (audio resuelto en runtime — diálogo/localización), *Plugin* |
| **Parameter** | La entrada del juego que modula el event. **Local** (por instancia) o **global** (compartido). **Continuous** (0–1, RPM, velocidad), **discrete/labeled** (enum: "Grass"/"Wood"), o **built-in** (Distance, Direction, Elevation, Speed, Event Cone Angle — el motor los rellena solos) |
| **Bank** (`.bank`) | El paquete que exporta Studio y carga el juego: metadata de events + datos de sample. Siempre existen **Master.bank** y **Master.strings.bank** (nombres de events). Se dividen para cargar/descargar por zona |
| **Snapshot** | Instantánea de mezcla que se dispara como un event (§6) |
| **VCA** | Fader que controla el volumen de varios buses a la vez (ej. "todo el SFX") |

### Integración con Unity (código real)

```csharp
using FMODUnity;
using FMOD.Studio;

// One-shot fire-and-forget (sin handle, no se puede parar) — equivale a PlayOneShot
RuntimeManager.PlayOneShot("event:/SFX/Explosion", transform.position);

// Event con estado (motor, música, loop): se controla por handle
EventInstance motor = RuntimeManager.CreateInstance("event:/Vehiculos/Motor");
motor.set3DAttributes(RuntimeUtils.To3DAttributes(transform)); // posición/velocidad 3D
motor.start();
motor.setParameterByName("RPM", rpm);            // parámetro LOCAL por nombre
motor.stop(STOP_MODE.ALLOWFADEOUT);              // respeta el fade autorado en el event
motor.release();                                  // OBLIGATORIO: libera la instancia

// Parámetro GLOBAL (afecta a todos los events)
RuntimeManager.StudioSystem.setParameterByName("HoraDelDia", 0.5f);

// Cargar un bank a mano (si no está en Initial Banks del FMOD Settings)
RuntimeManager.LoadBank("SFX", true);
```

- Componente sin código: **StudioEventEmitter** (arrastra un event a un GameObject, dispara por Play/Trigger/Collision).
- El programador NUNCA sabe qué suena dentro del event — solo el path y los nombres de parámetros. Ese es el desacople (§8).
- Gotcha: cada `CreateInstance` que arranca hay que `release()`; olvidarlo fuga instancias (se ve en el Profiler §9).

---

## 5. Wwise: conceptos y operación

Wwise (Wave Works Interactive Sound Engine) es autoría gráfica + motor cross-platform (Wikipedia). Trabaja con **Game Syncs** (la interfaz juego↔audio) y exporta **SoundBanks**.

| Concepto | Qué es |
|---|---|
| **Event** | Lo que el juego postea (`Play_Footstep`, `Stop_Music`). Un event dispara *Actions* (play/stop/pause/set volume…) sobre objetos de la jerarquía |
| **RTPC** (Real-Time Parameter Control) | Un valor continuo del juego (Health, Speed, RPM) mapeado a una curva que controla cualquier propiedad (volumen, pitch, filtro, LFO). El equivalente al *parameter continuous* de FMOD |
| **Switch** | Elección **discreta por objeto**: "¿qué variante?" — ej. superficie del paso (Grass/Wood/Metal). Cambia qué sub-track suena |
| **State** | Estado **global** de mezcla/música: Explore/Combat/Menu. Puede fijar volúmenes de buses y disparar música (equivale a snapshot + selector de música) |
| **Actor-Mixer Hierarchy** | Donde viven los SFX: Sound objects → Random/Sequence/Switch/Blend Containers → Actor-Mixers (grupos con propiedades heredadas) |
| **Interactive Music Hierarchy** | Sistema de música dedicado (§6), separado del Actor-Mixer |
| **SoundBank** (`.bnk`) | El paquete cargable: estructura + eventos + (opcional) media `.wem` codificada. **Init.bnk** se carga SIEMPRE primero (config global, buses, states) |

### Integración con Unity (código real)

```csharp
// Disparar un Event por nombre (o por constante generada AK.EVENTS.Play_Footstep)
uint playingId = AkSoundEngine.PostEvent("Play_Footstep", gameObject);

// RTPC: valor continuo, por objeto (o global si se omite el gameObject)
AkSoundEngine.SetRTPCValue("Health", 80f, gameObject);

// Switch: elección discreta POR objeto (qué variante suena)
AkSoundEngine.SetSwitch("Surface", "Grass", gameObject);

// State: estado GLOBAL (mezcla/música)
AkSoundEngine.SetState("Music", "Combat");

// Cargar SoundBank (Init.bnk debe ir primero, normalmente en bootstrap)
AkSoundEngine.LoadBank("Main", out uint bankID);
```

- ⚠️ En Wwise 2023.1+ la clase de integración se renombró de `AkSoundEngine` a **`AkUnitySoundEngine`** (mismos métodos). **NO VERIFICADO** el nombre exacto en la versión que uses — confirmar en el Wwise Launcher/docs.
- Componentes sin código: **AkEvent**, **AkAmbient**, **AkBank**, **AkState**, **AkSwitch**, **AkGameObj** (registra el GameObject como objeto de audio), **AkAudioListener**, **AkRoom/AkRoomPortal** (spatial audio).
- Todo objeto que emita sonido posicional necesita un **Game Object** registrado (el `gameObject` que pasas a PostEvent); Wwise trackea posición por él.

---

## 6. Tabla de equivalencias FMOD ↔ Wwise (para no perderse)

| Necesito… | FMOD Studio | Wwise |
|---|---|---|
| Disparar algo por nombre | **Event** (`event:/...`) | **Event** (`Play_...`) |
| Valor continuo en runtime | **Parameter** continuous (local/global) | **RTPC** |
| Elegir variante discreta por objeto | **Parameter** labeled/discrete | **Switch** |
| Estado global de juego (mezcla/música) | **Parameter** global / **Snapshot** | **State** |
| Paquete de datos cargable | **Bank** (`.bank`) | **SoundBank** (`.bnk`) |
| Media codificada | (dentro del bank) | `.wem` |
| Bus de mezcla | Group / Return **Bus** | Audio Bus / Auxiliary Bus |
| Control de volumen cross-bus | **VCA** | RTPC/State sobre buses |
| Instantánea de mezcla | **Snapshot** | **State** de mezcla |
| Editar la mezcla en el juego corriendo | **Live Update** | **Connect/Remote** (Profiler) |

---

## 7. Música adaptativa: el punto fuerte del middleware

Es LA razón técnica para adoptar middleware. Lo que en Unity nativo es corutinas de PlayScheduled + capas manuales [ver: unity/audio-unity §5], aquí es primitivo. La teoría (horizontal vs vertical, stingers, silencio) está en [ver: musica-adaptativa] y [ver: gamedev/audio] — no se repite; aquí va CÓMO lo hace cada herramienta.

| Técnica | FMOD Studio | Wwise (Interactive Music Hierarchy) |
|---|---|---|
| **Layering vertical** (capas que entran/salen) | Varios tracks en el timeline, volumen automatizado contra un parameter | **Music Track** tipo *Switch* con sub-tracks + RTPC/State sobre volúmenes |
| **Reorquestación horizontal** (secciones que cambian) | Transition regions/markers + destination markers movidos por parameter | **Music Playlist Container** (secuencia/loop de segmentos) + **Music Switch Container** (mapea State/Switch → playlist) |
| **Unidad musical** | Timeline con tempo + loop regions | **Music Segment** con **entry cue** y **exit cue** |
| **Transiciones a compás** | Quantization: el salto espera al próximo compás/beat/marker | **Transitions** con sync: Immediate / Next Bar / Next Beat / Next Cue / Exit Cue (+ segmento de transición y fades) |
| **Stinger** (frase corta encima) | Instrument/transition alineado a marker | **Stinger**: Trigger que reproduce una frase alineada a un sync point sin cortar la música |

- Ambos garantizan que el cambio caiga **en tiempo musical** (no un crossfade a media frase) — eso es lo caro de hacer a mano.
- El juego solo mueve un parameter/RTPC ("Intensity 0→1") o setea un State ("Combat"); la partitura reacciona sola.

---

## 8. Mezcla y buses en middleware

El mixer visual del middleware es superior al AudioMixer de Unity [ver: unity/audio-unity §3] en que se edita **con el juego corriendo en el device** y guarda estados como assets de audio. Conceptos de mezcla generales (headroom, LUFS, ducking) en [ver: direccion-audio-mezcla] — aquí el CÓMO en la herramienta.

| Mecanismo | FMOD | Wwise |
|---|---|---|
| **Ruteo** | Buses en el Mixer; Return buses + Sends para reverb compartida | Master-Mixer Hierarchy: Audio Bus + Auxiliary Bus (envs/reverb) |
| **Snapshots** (estado de mezcla) | Snapshot = un event; se dispara y **blende por intensidad**; modo *overriding* (fija) o *blending* (suma) | **State** con propiedades de bus (volúmenes, RTPC) por estado global |
| **Ducking** música-bajo-voz | Sidechain: manda la señal de Voz al **compresor** del bus de Música (sidechain input) | **Auto-ducking**: pestaña Ducking del bus — un bus baja a otros cuando tiene señal activa (sin cablear sends) |
| **Control macro** | **VCA** (un fader gobierna varios buses) | RTPC/State sobre buses |
| **Loudness/dinámica** | Efectos por bus (limiter, compresor); medidor | **HDR** (High Dynamic Range mixing), metering, limiter |
| **Sliders de opciones** | VCA/bus expuesto → el juego setea su volumen | RTPC "MusicVolume" → curva de volumen del bus |

- El ducking en Wwise es una **propiedad del bus** (más directo que el Send→Duck de Unity); en FMOD es el patrón sidechain→compresor.
- Snapshots/States sustituyen los AudioMixerSnapshots de Unity — mismo concepto (menú/combate/underwater), pero editables en vivo.

---

## 9. El flujo de trabajo: el desacople designer ↔ programador

El valor central del middleware NO es sonido "mejor", es **quién hace qué y cuándo**:

```
Sound designer (FMOD Studio / Wwise Authoring)
   arma events, parámetros, música, mezcla  ──► exporta BANKS ──►
Programador (Unity/Unreal)
   dispara events POR NOMBRE, setea parámetros ──► el juego suena
```

| Contrato entre roles | Detalle |
|---|---|
| Lo que acuerdan | Una **lista de nombres**: events (`event:/SFX/Jump`, `Play_Jump`), parámetros/RTPCs (`Speed`, `Health`), states/switches (`Combat`, `Grass`) |
| Lo que el programador NO sabe | Qué clips suenan, cuántas variantes, qué efectos, cómo transiciona la música — todo vive en el bank |
| Iteración | El designer cambia el sonido y re-exporta el bank; el código no cambia. Con **Live Update/Connect**, ni re-exporta: edita contra el juego corriendo en el device |
| Riesgo | Si el nombre de un event cambia en la herramienta y no en el código → sonido mudo. Acordar convención de nombres estable y bloquear renombres (misma disciplina que [ver: audio-a-juego §7]) |

Este desacople es lo que justifica el middleware en equipo. Para un **dev solo** que hace las dos cosas, el desacople no aporta nada — el mismo cerebro toca herramienta y código.

---

## 10. Coste real de adoptar middleware (para un dev solo/indie)

Honesto: para uno solo, el middleware suele **costar más de lo que rinde**, salvo que el audio adaptativo sea la identidad del juego.

| Coste | Detalle |
|---|---|
| **Curva de aprendizaje** | FMOD: moderada (más simple, budget-free). Wwise: alta (workflow AAA, muchos conceptos). Se mide en sesiones de estudio, no en tardes |
| **Pipeline de banks** | Paso extra en cada build: exportar/generar banks y mantenerlos sincronizados con el código. Un bank desactualizado = sonidos mudos o viejos |
| **Build size + runtime** | Plugin + runtime nativo por plataforma; banks pesan; hay que gestionar carga/descarga por zona |
| **Licencia por plataforma** | Verificar el tier por cada plataforma de ship (§3) — trámite legal real antes de publicar |
| **Debug** | Un fallo de audio ahora vive en DOS sitios (herramienta y código); toca aprender el Profiler propio (§11) |
| **Lo que se GANA solo** | Autoría desacoplada, música interactiva de primera clase, mezcla en device. Si no usas nada de eso, pagaste complejidad por nada |

**Veredicto de la memoria del proyecto:** juego indie/mobile con música por estados + SFX con variación + ducking → **stack nativo** [ver: unity/audio-unity]. Middleware SOLO si (a) sound designer dedicado, (b) música adaptativa compleja como sello del juego, o (c) mezcla final en device. Entre los dos, **FMOD** para empezar (más simple, free por budget); **Wwise** si el proyecto es AAA o ya hay experiencia en el equipo.

---

## 11. Profiling y perfil de memoria del audio

Los dos traen un profiler propio que se conecta al juego corriendo (algo que el AudioMixer de Unity no da igual de fino). Perfilar es obligatorio antes de shippear: el audio es de los primeros en romper el budget de memoria/CPU en móvil [ver: unity/audio-unity §7].

| Qué medir | FMOD Profiler | Wwise Profiler |
|---|---|---|
| Conexión al juego | **Live Update / Profiler session** (graba y reproduce) | **Connect** (Capture Log + Performance Monitor) |
| CPU | DSP / update / streaming CPU | Performance Monitor (CPU total, plug-ins) |
| Voces | Real vs virtual, instancias activas por event | **Voices tab** del Advanced Profiler (activas/virtuales, por qué se virtualizó) |
| Memoria | Banks cargados, sample data residente vs streaming | Memoria por SoundBank, media residente vs streamed |
| Fugas | Instancias sin `release()` se acumulan (contador subiendo) | Objetos/voces que no paran |

**Perfil de memoria — reglas:**
- Los **banks/SoundBanks residentes** ocupan RAM (metadata + sample data). Cargar/descargar por zona; no tener todo en memoria a la vez.
- **Música y ambientes largos = streaming** (igual que Streaming en Unity); SFX cortos = residentes en bank.
- **Init.bnk (Wwise) / Master.strings (FMOD)** cargan primero y quedan; mantenerlos ligeros.
- **Límites de voces**: ambos virtualizan voces por debajo de un umbral de volumen (como Max Real/Virtual Voices de Unity) — configurar el límite y verificar en el Profiler que los SFX críticos no se virtualizan bajo carga.
- Medir en **dispositivo real**, no en editor: el perfil de memoria/CPU del móvil es el que importa.

---

## Reglas prácticas

1. Dev solo / indie chico con audio "normal" (SFX con variación + música por estados + ducking) → **stack nativo** [ver: unity/audio-unity]; no metas middleware por defecto.
2. Adopta middleware SOLO si se cumple ≥1: sound designer dedicado, música adaptativa como identidad, mezcla en device, o reuso multi-motor.
3. Entre los dos: **FMOD** para empezar (más simple, Indie gratis < $600k); **Wwise** para AAA o equipo con experiencia.
4. Antes de comprometerte, **lee la licencia en la web oficial** por CADA plataforma de ship — no te fíes de cifras de segunda mano (§3).
5. FMOD verificado: Indie gratis < US$600k, Basic $600k–$1.8M, Premium > $1.8M (budget del título). Wwise: free tier con límite de assets — **confirmar el número vigente**.
6. Acuerda con el programador una **lista estable de nombres** (events, parámetros, states/switches) y no la renombres a la ligera — un rename sin sincronizar = sonido mudo.
7. FMOD: por cada `CreateInstance` que arranca, `stop()` + `release()`. Fugar instancias se ve en el Profiler.
8. Usa **one-shot** (`PlayOneShot`/`PostEvent` sin handle) para fire-and-forget; **instancia con handle** para todo lo que haya que parar/modular (motor, música, loops).
9. Parámetro **continuo** (RTPC/parameter) para valores graduales (Health, Speed); **discreto** (Switch/labeled) para elegir variante; **global/State** para estado de juego.
10. Música adaptativa: deja que la herramienta haga la transición **a compás** (quantization/sync points); el juego solo mueve un parámetro o setea un State [ver: musica-adaptativa].
11. Ducking: en Wwise es propiedad del bus (Auto-ducking); en FMOD es sidechain→compresor; en ambos, release ~500 ms para retorno natural [ver: direccion-audio-mezcla].
12. Mezcla en snapshots/States (menú/combate/underwater) editada con **Live Update/Connect** en el dispositivo real, no de oído en el editor.
13. Banks: divide por zona, música/ambiente en **streaming**, SFX residentes; carga **Init.bnk/Master banks primero**.
14. Perfila con el Profiler propio en **dispositivo real** antes de ship: CPU de DSP, voces reales vs virtuales, memoria de banks.
15. Configura límites de voces y verifica que los SFX críticos no se virtualizan bajo carga.
16. Mantén una convención de nombres de assets/events (misma disciplina de entrega de [ver: audio-a-juego]).
17. El plugin de integración es gratis (FMOD Asset Store / Wwise Launcher); lo que se licencia es el **uso comercial del runtime**, no el plugin.
18. No mezcles pipeline nativo y middleware para lo mismo: si el middleware gestiona el audio, AudioSource/AudioMixer de Unity dejan de usarse para eso [ver: unity/audio-unity §6].

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Meter FMOD/Wwise "porque es más pro" en un juego chico de un solo dev | El desacople designer↔programador no aporta a quien hace ambos; usa nativo salvo audio adaptativo real |
| Publicar sin verificar el tier de licencia por plataforma | Leer fmod.com/licensing o audiokinetic.com/pricing por cada plataforma ANTES de ship (legal serio) |
| Asumir cifras de licencia de un blog/tercero | Las verificadas aquí: tramos de budget FMOD (Wikipedia). Wwise numérico = NO VERIFICADO → web oficial |
| `CreateInstance` sin `release()` en FMOD → fuga de instancias | Siempre `stop()` + `release()`; vigilar el contador de instancias en el Profiler |
| Renombrar un event en la herramienta y no en el código → sonido mudo | Lista de nombres acordada y estable; buscar todos los callers antes de renombrar |
| Bank/SoundBank desactualizado → suena viejo o mudo | Regenerar banks en cada build; automatizar el paso de export en el pipeline |
| Todo el audio en banks residentes → pico de memoria en móvil | Música/ambiente en streaming; dividir banks por zona; cargar/descargar bajo demanda |
| SFX crítico que se corta bajo mucha acción | Se virtualizó por límite de voces → subir prioridad/límite y verificar en el Voices tab del Profiler |
| Crossfade de música a media frase (feo) | Usar quantization/sync points de la herramienta para transicionar a compás, no un fade ciego |
| Esperar que el nativo de Unity haga música adaptativa AAA a mano | Layering/transiciones a compás/stingers son primitivos en middleware; a mano en Unity es artesanal [ver: unity/audio-unity §5] |
| Mezclar de oído en el editor y que suene mal en el device | Live Update/Connect: ajustar la mezcla con el juego corriendo en el dispositivo real |
| Wwise: sonido posicional sin Game Object registrado | Todo emisor 3D necesita su GameObject registrado (AkGameObj / el objeto que pasas a PostEvent) |

## Fuentes

- **FMOD — Wikipedia** (en.wikipedia.org/wiki/FMOD, actualizada 2026-07-20) — tiers de licencia por presupuesto: Non-Commercial gratis, Indie < US$600k, Basic $600k–$1.8M, Premium > $1.8M; FMOD Studio "audio creation tool designed like a DAW"; Studio run-time API vs low-level API; integraciones Unity/Unreal 2.5–5/CryEngine/GameMaker. **Verificado 2026-07-21.**
- **Audiokinetic Wwise — Wikipedia** (en.wikipedia.org/wiki/Audiokinetic_Wwise) — Wwise = autoría gráfica + motor cross-platform; import/procesado, mezcla en tiempo real, game states, entornos, spatial audio (Windows Spatial/Dolby Atmos), live authoring; "gratis para no comercial, bajo licencia para comercial" (sin cifras). **Verificado 2026-07-21.**
- **FMOD Studio manual — Events / Parameters / Banks / Mixer / Profiler** (fmod.com/docs, FMOD Studio 2.03) — conceptos de event, instrument (single/multi/scatterer/event/programmer), parameter (local/global, continuous/discrete/labeled/built-in), bank (.bank, Master + Master.strings), snapshot, VCA, Live Update. ⚠️ Las páginas de docs son JS-rendered y devolvieron vacío al scraper en esta pasada — contenido según documentación estándar de FMOD, **confirmar en fmod.com/docs**.
- **FMOD for Unity — integración** (fmod.com/docs, plugin Unity Asset Store) — `RuntimeManager.PlayOneShot/CreateInstance`, `EventInstance.setParameterByName/set3DAttributes/stop/release`, `StudioEventEmitter`, carga de banks. **Plugin gratis; versión/Unity mínima NO VERIFICADO** — confirmar en Asset Store.
- **Wwise — documentación (Interactive Music, RTPC, States/Switches, SoundBanks, Profiler)** (audiokinetic.com/library) — Interactive Music Hierarchy (Music Segment con entry/exit cues, Music Playlist/Switch Containers, transitions con sync, stingers), Game Syncs (Events, RTPC, States, Switches), Master-Mixer Hierarchy, auto-ducking en bus, SoundBanks (.bnk + .wem, Init.bnk), Advanced Profiler (Voices/Memory). ⚠️ audiokinetic.com devolvió **403** al scraper — contenido según documentación estándar de Wwise, **confirmar en audiokinetic.com**.
- **Wwise para Unity — integración** (audiokinetic.com, vía Wwise Launcher) — `AkSoundEngine.PostEvent/SetRTPCValue/SetSwitch/SetState/LoadBank`; componentes AkEvent/AkAmbient/AkBank/AkGameObj/AkAudioListener. ⚠️ Rename a `AkUnitySoundEngine` en versiones recientes **NO VERIFICADO** — confirmar según versión.
- **fmod.com/licensing** y **audiokinetic.com/pricing** — páginas oficiales de precios. ⚠️ **Inaccesibles al scraper en esta pasada (FMOD vacío / Wwise 403)** — fuente obligatoria para cualquier cifra de fee/límite antes de publicar.
- Cross-refs internos: [ver: unity/audio-unity] (implementación nativa: AudioMixer §3, PlayScheduled §5, middleware §6, móvil §7), [ver: audio-a-juego] (entrega/naming), [ver: musica-adaptativa] (teoría horizontal/vertical/stingers), [ver: direccion-audio-mezcla] (mezcla/ducking/LUFS), [ver: gamedev/audio] (teoría de audio de juego).
