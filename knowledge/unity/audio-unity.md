# Audio en Unity

> **Cuando cargar este archivo:** al implementar cualquier cosa de sonido en Unity 6 — SFX, música, mezcla/volúmenes, import settings de AudioClips, o audio para móvil (latencia, interrupciones, mute de iOS). La teoría de diseño sonoro (qué sonidos poner y por qué) está en [ver: gamedev/audio]; aquí está el CÓMO en el motor.

## 1. Modelo básico: AudioClip → AudioSource → AudioListener

- **AudioClip**: el asset de audio (datos). **AudioSource**: componente que lo reproduce desde un GameObject. **AudioListener**: "el oído" — exactamente **uno activo por escena** (normalmente en la Main Camera; en juegos 3ª persona a veces conviene en el player). Más de uno → warning y comportamiento indefinido.
- Formatos de archivo que Unity importa: `.wav`, `.mp3`, `.ogg`, `.aif`, y tracker modules (`.xm/.mod/.it/.s3m`). Unity **siempre transcodifica** al Compression Format elegido en el importer — el formato del archivo fuente NO es el formato del build. Fuente recomendada: lossless (WAV/AIFF).

### Propiedades clave del AudioSource

| Propiedad | Qué hace | Notas |
|---|---|---|
| `volume` | Amplitud (0–1) a 1 metro de distancia | Lineal; para sliders de usuario usar mixer + dB (§3) |
| `pitch` | Velocidad de reproducción (1 = normal) | Cambia velocidad Y tono a la vez |
| `spatialBlend` | 0 = 2D puro, 1 = 3D puro; interpolable | Default del inspector: 0 (2D). Animable para transiciones |
| `priority` | 0 (más importante) a 255 (menos importante); default 128 | Decide qué voces se roban cuando se agotan las reales |
| `loop` | Repite el clip | Para loops perfectos ver §5 |
| `playOnAwake` | Reproduce al activarse | Apagarlo en SFX; el default es ON |
| `outputAudioMixerGroup` | A qué grupo del mixer va | SIEMPRE asignarlo (Music/SFX/UI/Voice) |
| `dopplerLevel` | Intensidad Doppler (0 = off) | En juegos sin vehículos rápidos: 0 |
| `spread` | Ángulo de dispersión estéreo 0–360° | 0 = puntual |

### 2D vs 3D (spatial blend)

- **2D (`spatialBlend = 0`)**: música, UI, voz de narrador, stingers. Ignora posición y distancia.
- **3D (`spatialBlend = 1`)**: todo lo que existe en el mundo (pasos, disparos, ambiente puntual). Atenúa por distancia y panea por posición relativa al listener.
- **Rolloff** (curva de atenuación 3D): `Logarithmic` (default, realista: cae rápido cerca, lento lejos), `Linear` (llega a 0 exactamente en Max Distance — mejor para gameplay legible), `Custom` (curva a mano).
- **Min Distance**: dentro de ese radio, volumen máximo — súbelo para que un sonido "domine" más área. **Max Distance**: en Linear es donde llega a 0; en Logarithmic es donde DEJA de atenuar (el sonido sigue sonando bajito, no desaparece) — gotcha clásico de "por qué se oye ese sonido desde la otra punta del mapa".
- Los cálculos 3D pasan en el AudioSource ANTES de entrar al mixer; el mixer no espacializa.

## 2. Import settings: la decisión por clip

Se configuran en el inspector del AudioClip (y por plataforma con override). Es la decisión de rendimiento más importante del audio [ver: rendimiento-unity].

### Load Type

| Load Type | Cómo funciona | Memoria | CPU | Usar para |
|---|---|---|---|---|
| **Decompress On Load** | Descomprime todo al cargar | Alta (Vorbis descomprimido ocupa ~10× su tamaño comprimido) | Mínima al reproducir | SFX cortos y frecuentes |
| **Compressed In Memory** | Comprimido en RAM, descomprime al vuelo | Media | Overhead al reproducir (notable con Vorbis; se ve en "DSP CPU" del Profiler) | Clips medianos, muchos clips que no suenan a la vez |
| **Streaming** | Decodifica desde disco en thread aparte | Mínima (~200 KB de overhead por clip aun sin datos cargados) | Disco + "Streaming CPU" en Profiler | Música y ambientes largos; NO para SFX; limitar a 1–2 streams simultáneos |

### Compression Format

| Formato | Ratio | CPU | Usar para |
|---|---|---|---|
| **PCM** | Sin comprimir (grande) | Mínima | SFX muy cortos donde importa calidad máxima |
| **ADPCM** | ~3.5× más chico que PCM (ratio fijo) | Baja | Sonidos "con ruido" que se disparan en masa: pasos, impactos, casquillos |
| **Vorbis** | El mejor ratio (~3× mejor que ADPCM), calidad ajustable con slider Quality | La más alta al decodificar | Música, diálogo, SFX medianos/largos. Default razonable: Quality ~0.7 y bajar hasta que se note |

### Resto de opciones

- **Force To Mono**: mezcla a mono (con normalize opcional) — mitad de memoria; casi obligatorio en móvil para SFX 3D (el paneo 3D lo hace el motor igual).
- **Load In Background**: carga async sin bloquear el main thread — activar en clips grandes no críticos al arrancar la escena.
- **Preload Audio Data**: ON por default (carga con la escena). Apagarlo en clips raros y cargarlos on-demand.
- **Sample Rate Setting**: `Preserve` / `Optimize` / `Override`. Para SFX móviles sin agudos importantes, Override a 22050 Hz recorta memoria a la mitad (práctica estándar de optimización móvil; ajustar de oído).

**Receta rápida**: SFX corto → PCM o ADPCM + Decompress On Load + Force To Mono (móvil). SFX/diálogo mediano → Vorbis + Compressed In Memory. Música/ambiente largo → Vorbis + Streaming.

## 3. AudioMixer

Asset (`Create > Audio Mixer`) con árbol de **grupos** (buses). Cada AudioSource sale por `outputAudioMixerGroup`; la señal sube por el árbol hasta Master → AudioListener. Se pueden encadenar mixers (salida de uno a un grupo de otro).

- Jerarquía mínima recomendada: `Master ─ Music / SFX / UI / Voice`. Efectos (lowpass, reverb, compresión) se cuelgan por grupo.
- ⚠️ En build **Web (WebGL)**: el manual dice explícito que **"Volume is the only property you can change on Web"** — nada de efectos, filtros ni otros parámetros del mixer funcionan ahí (Web usa una implementación interna de Web Audio API en vez del motor de audio nativo, que depende de threading no disponible en WebGL). Si el target es WebGL, probar temprano y tener plan B con `AudioSource.volume` por categoría.

### Snapshots

Guardan el estado completo del mixer (volúmenes, pitch, send levels, wet mix, settings de efectos). Transición por código:

```csharp
[SerializeField] AudioMixerSnapshot combate, exploracion;
void EntrarCombate() => combate.TransitionTo(1.5f); // interpola 1.5s
```

- Llamar `TransitionTo` de nuevo reinicia la transición desde el estado actual.
- Sirven para estados de mezcla (menú/juego/combate/underwater), NO para fades de música finos: la interpolación del snapshot sobre volumen suena no-lineal (acelerada/frenada) — para fades usar exposed param + conversión log (abajo).

### Exposed parameters y volumen en dB (sliders de opciones)

Cualquier parámetro del mixer se expone con click derecho → "Expose ... to script" y se renombra en la lista Exposed Parameters. Control: `mixer.SetFloat("MusicVol", dB)` / `GetFloat` / `ClearFloat`.

**El fader del mixer trabaja en decibelios (escala logarítmica)**: -80 dB (silencio) a +20 dB, con 0 dB = sin cambio. Un slider lineal mapeado directo a ese rango queda inservible (a mitad de slider ya estás en ~-40 dB, casi mudo). Conversión correcta:

```csharp
// slider.minValue = 0.0001f (nunca 0: Log10(0) = -inf), maxValue = 1
public void SetMusicVolume(float sliderValue)
{
    mixer.SetFloat("MusicVol", Mathf.Log10(sliderValue) * 20f);
}
```

Guardar en PlayerPrefs el valor LINEAL del slider (0.0001–1), no los dB.

**Gotcha (confirmado en múltiples hilos)**: cuando expones un parámetro, los snapshots dejan de controlarlo — manda el último `SetFloat`. `ClearFloat("MusicVol")` "resetea el exposed parameter a su valor inicial" (API oficial) y devuelve el control al mixer. No mezclar snapshot-control y SetFloat sobre el mismo parámetro.

### Ducking (sidechain)

Bajar música cuando habla la voz/narrador:

1. En el grupo **Music**: `Add Effect > Duck Volume`.
2. En el grupo **Voice**: `Add Effect > Send`, y en el Send elegir como destino el Duck Volume de Music; subir el Send level (default -80 dB = no manda nada).
3. En el Duck Volume ajustar: **Threshold** (nivel de la señal sidechain que dispara el duck, p.ej. -30 dB), **Ratio**, **Attack time** (~100 ms) y **Release time** (~500 ms para que la música vuelva suave). (Nombres del inspector; la página del efecto no está en el manual actual — verificado el mecanismo Send→Duck en el manual del mixer.)

El orden de efectos dentro del grupo importa (la señal los recorre en orden del inspector).

## 4. SFX: disparo, variación y pooling

### PlayOneShot y sus límites

`source.PlayOneShot(clip, volumeScale)`: dispara un clip que se **solapa** con lo que ya suene en ese source ("PlayOneShot does not cancel clips that are already being played by PlayOneShot and Play" — doc oficial). `volumeScale > 1` puede causar clipping. Limitaciones: un one-shot individual no tiene handle — no puedes pausarlo, pararlo ni cambiarle el pitch a mitad. Para SFX que necesiten Stop/loop (motor, lluvia, canal de carga), usar `Play()` en un source dedicado.

`AudioSource.PlayClipAtPoint(clip, pos)` crea un GameObject temporal con AudioSource y lo destruye al terminar: cómodo para prototipos, pero genera garbage y no deja asignar mixer group — en producción, pool propio.

### Pool de AudioSources + variación

Un solo source no basta (los one-shots comparten pitch/salida del source). Patrón estándar: N sources round-robin bajo un manager [ver: csharp-patrones]:

```csharp
public class SfxPlayer : MonoBehaviour
{
    [SerializeField] AudioMixerGroup sfxGroup;
    [SerializeField] int voices = 8;
    AudioSource[] pool; int next;

    void Awake()
    {
        pool = new AudioSource[voices];
        for (int i = 0; i < voices; i++)
        {
            pool[i] = gameObject.AddComponent<AudioSource>();
            pool[i].outputAudioMixerGroup = sfxGroup;
            pool[i].playOnAwake = false;
        }
    }

    public void Play(AudioClip clip, float vol = 1f)
    {
        var s = pool[next]; next = (next + 1) % voices;
        s.pitch = Random.Range(0.94f, 1.06f);       // mata la metralleta repetitiva
        s.PlayOneShot(clip, vol * Random.Range(0.85f, 1f));
    }
}
```

Pitch ±5–10% + volumen ±15% + 2–4 clips alternativos = el mismo golpe nunca suena idéntico [ver: gamedev/audio].

### Audio Random Container (Unity 6)

Asset nativo (`Create > Audio > Audio Random Container`, introducido en 2023.1, presente en Unity 6) que hace esa variación sin código: lista de clips con randomización de **volumen y pitch por rangos**, modos de reproducción **Sequential / Shuffle** (no repite hasta agotar la lista) **/ Random**, trigger **Manual** (suena con `AudioSource.Play()`) o **Automatic** (Pulse = intervalo fijo, Offset = pausa entre clips), y conteo de loops. Se asigna directo en el campo AudioClip del AudioSource; su volumen es aditivo con el del source. Úsalo para pasos, impactos, ambientes con variantes.

### Voces y prioridad

Project Settings > Audio: **Max Real Voices** (voces audibles simultáneas; cada frame ganan las más fuertes) y **Max Virtual Voices** (gestionadas sin sonar). Defaults del editor: 32 reales / 512 virtuales (confirmar en Project Settings del proyecto). Si un SFX crítico "se corta" con mucha carga, bájale el número de `priority` (0 = nunca robado) y sube el de los ambientales.

## 5. Música: loops, intro+loop, crossfade, timing exacto

### Reloj correcto: AudioSettings.dspTime

`double` basado en samples procesados por el sistema de audio: más preciso que `Time.time`, independiente del framerate, y **no avanza mientras el juego está pausado o suspendido** (los sonidos se pausan con él; al reanudar NO hay que reprogramar nada — doc oficial). Todo timing musical se hace contra dspTime, nunca contra Time.time.

- Pausar el juego: `AudioListener.pause = true` congela dspTime y todos los sources (`Time.timeScale = 0` NO pausa el audio). Los sonidos de UI que deben seguir sonando: `uiSource.ignoreListenerPause = true`.

### Loop perfecto (seamless)

- `source.loop = true` con un clip bien cortado (empieza y termina en zero-crossing, sin silencio) loopea sin gap.
- ⚠️ Gotcha multi-confirmado: **archivos fuente MP3 meten silencio de padding** al inicio/final por cómo funciona el encoder → gap audible en el loop. Fuente para música loopeable: **WAV** (Unity la transcodifica a Vorbis igual, ver §2).

### Intro + loop sin gap (PlayScheduled)

`Play()` "cuando termine la intro" via corutina/Invoke SIEMPRE deja gap (depende del frame). Lo correcto: dos AudioSources y `PlayScheduled`, que es "el método preferido para concatenar clips" (doc oficial):

```csharp
[SerializeField] AudioSource introSrc, loopSrc; // mismo mixer group

void StartMusic()
{
    double start = AudioSettings.dspTime + 0.2;              // margen de preparación
    double introLen = (double)introSrc.clip.samples / introSrc.clip.frequency;
    introSrc.PlayScheduled(start);                            // exacto en samples
    loopSrc.loop = true;
    loopSrc.PlayScheduled(start + introLen);                  // entra clavado al terminar la intro
}
```

- Duración con `(double)clip.samples / clip.frequency`, NO con `clip.length` (float, impreciso).
- Programar con ≥ ~1 s de antelación permite a Unity precargar incluso clips en Streaming sin pico de CPU.
- `SetScheduledEndTime` corta un clip programado sin click, para encadenar segmentos.
- Stingers/eventos a compás: `barLength = 60.0 / bpm * beatsPorCompas;` y programar al próximo múltiplo desde dspTime (patrón del ejemplo oficial de PlayScheduled).

### Crossfade entre pistas

Dos sources (o dos grupos del mixer): fade-out de A y fade-in de B a la vez. El método con mejor resultado (comparativa de J. L. French): lerp del **volumen del mixer group** en corutina **con conversión logarítmica** — el motor suaviza entre frames y no escalona a FPS bajos; el fade directo de `AudioSource.volume` escalona con framerate bajo, y el fade por snapshot suena no-lineal siempre:

```csharp
IEnumerator FadeMixer(string param, float from, float to, float secs)
{
    for (float t = 0; t < secs; t += Time.unscaledDeltaTime)
    {
        float v = Mathf.Lerp(from, to, t / secs);             // lineal 0.0001–1
        mixer.SetFloat(param, Mathf.Log10(Mathf.Max(v, 0.0001f)) * 20f);
        yield return null;
    }
    mixer.SetFloat(param, Mathf.Log10(Mathf.Max(to, 0.0001f)) * 20f);
}
```

Para música que sobrevive cambios de escena: source en un GO con `DontDestroyOnLoad` (patrón "MusicManager" singleton) [ver: arquitectura-unity].

## 6. Middleware (FMOD/Wwise) vs audio nativo

| Criterio | Audio nativo Unity | FMOD / Wwise |
|---|---|---|
| Quién autorea | El programador (inspector + código) | Sound designer en herramienta propia (FMOD Studio / Wwise Authoring), sin tocar Unity |
| Música adaptativa | A mano (PlayScheduled, capas, crossfades §5) | Nativa: transiciones por marcadores, capas por parámetro, cues |
| Mezcla en vivo | Play mode del editor | Live update conectado al juego corriendo en el dispositivo |
| Eventos/variación | Pool + AudioRandomContainer | Sistema de eventos con randomización integral y banks |
| Costo | 0; sin dependencias | Curva de aprendizaje + build size + pipeline de banks; licencia |

**Criterio práctico**: para un juego indie/mobile con música por estados, SFX con variación y ducking, el stack nativo de este archivo cubre todo — middleware es sobreingeniería. FMOD/Wwise se justifican cuando: (a) hay un sound designer dedicado que necesita iterar sin programador, (b) música adaptativa compleja (transiciones por compás entre N estados, capas verticales), o (c) mezcla final en dispositivo real con live update.

- **FMOD for Unity**: plugin gratis en Asset Store, soporta Unity 6 — NO VERIFICADO el número de versión exacto y la versión mínima de Unity soportada (cambian con cada release; confirmar en el Asset Store antes de instalar). Licencia FMOD por presupuesto del proyecto: Indie gratis < $600k de presupuesto; Basic $600k–$1.8M; Premium > $1.8M (fuente secundaria Wikipedia; confirmar cifras vigentes en fmod.com/licensing antes de comprometerse).
- **Wwise** (Audiokinetic): pricing actual NO VERIFICADO (web inaccesible durante la investigación); históricamente tier gratuito limitado por cantidad de assets.
- Middleware reemplaza al pipeline de audio de Unity (AudioSource/Mixer dejan de usarse para lo que gestione el middleware); no se mezclan a medias.

## 7. Audio móvil

### Latencia (DSP buffer)

- La latencia de salida ≈ `bufferLength × numBuffers / sampleRate`. Valores reales del dispositivo: `AudioSettings.GetConfiguration().dspBufferSize` y `AudioSettings.GetDSPBufferSize(out len, out num)`.
- Se configura en **Project Settings > Audio > DSP Buffer Size**: `Best Latency` (responde más rápido, más CPU/recursos), `Default`, `Good Latency` (balance), `Best Performance` (delay perceptible, sistema más eficiente) — texto exacto del inspector, confirmado en el manual. NO VERIFICADO: la doc no publica un umbral en ms a partir del cual los cambios de parámetros "dejan de sonar suaves"; en juegos de ritmo/feedback táctil, cualquier latencia perceptible ya es mala — medir con `GetConfiguration()` y ajustar de oído en el dispositivo real, no fiarse de un número sin fuente.
- Para juegos donde el tap debe sonar YA (ritmo, arcade): `Best Latency` y perfilar CPU de audio en el Profiler (módulo Audio). Cambiar en runtime: `var c = AudioSettings.GetConfiguration(); c.dspBufferSize = 256; AudioSettings.Reset(c);` — ⚠️ `Reset` reinicia el sistema de audio y PARA todo lo que sonaba; hay que relanzar la música después.
- Android: la latencia real varía muchísimo por dispositivo (driver/OS); no prometer sync de ritmo perfecto sin calibración por usuario (patrón estándar: pantalla de calibración con offset ajustable).

### Interrupciones (llamadas, alarmas, cambio de output)

- Al suspenderse la app (llamada entrante, background), el audio y `dspTime` se pausan juntos; al reanudar, **no hay que reprogramar los PlayScheduled** (doc oficial de dspTime). Verificar igual en dispositivo real: es el punto que más regresiones da.
- `AudioSettings.OnAudioConfigurationChanged(bool deviceWasChanged)`: se dispara al desconectar auriculares, cambiar a Bluetooth, o tras `AudioSettings.Reset`. `deviceWasChanged == true` → dispositivo de salida cambió: los sources pueden quedar parados; reanudar con `Play()` (patrón del ejemplo oficial). Suscribirse en el AudioManager del juego.

### iOS específico

- **Mute switch / volumen 0**: `AudioSettings.Mobile` (iOS/Android): `muteState`, evento `OnMuteStateChanged`, y `stopAudioOutputOnMute` para apagar el thread de audio cuando el dispositivo está muteado (ahorra batería). `StartAudioOutput()/StopAudioOutput()` manual. ⚠️ Gotcha documentado: al reanudar, los sonidos siguen desde donde se pausaron — en juegos donde el audio debe ir sincronizado con gameplay, resincronizar la música al reactivar en vez de dejarla continuar.
- **Player Settings iOS**: `Mute Other Audio Sources` — ON: tu app calla el audio de fondo (Spotify etc.); OFF: conviven (lo correcto para juegos casuales: dejar que el usuario oiga su música y ofrecer toggle de música in-game). `Prepare iOS for Recording` baja latencia de micrófono pero re-rutea la salida a auriculares — no activarlo si no grabas.
- Cortesía estándar de juego móvil: botones separados de mute para Música y SFX (dos exposed params del mixer), estado persistido en PlayerPrefs.

### Import para móvil (resumen §2 aplicado)

Force To Mono en SFX 3D + Vorbis con Quality bajada de oído + Override sample rate 22050 Hz en SFX sin agudos + música en Streaming = la memoria de audio deja de ser problema en un juego mediano. [ver: build-plataformas]

## Reglas prácticas

1. Un solo AudioListener activo (cámara o player); todo AudioSource con `outputAudioMixerGroup` asignado — nada ruteado "suelto" a Master.
2. Fuentes de audio en WAV/AIFF en el repo; jamás MP3 como fuente de un loop (padding → gap).
3. Load Type por tipo: SFX corto = Decompress On Load; mediano = Compressed In Memory; música/ambiente = Streaming (máx 1–2 streams a la vez).
4. Formato: ADPCM para SFX masivos con ruido; Vorbis para música/diálogo (Quality ~0.7 y bajar de oído); PCM solo para clips diminutos.
5. Móvil: Force To Mono en SFX 3D + considerar 22050 Hz; revisar el total en el Audio module del Profiler.
6. `spatialBlend` = 0 para música/UI, 1 para el mundo; rolloff Linear si necesitas que el sonido MUERA en Max Distance (Logarithmic no llega a 0).
7. SFX repetitivos: pool de 6–10 AudioSources round-robin + pitch ±5–10% + volumen ±15%, o Audio Random Container en modo Shuffle.
8. `PlayOneShot` solo para fire-and-forget; cualquier sonido que haya que parar/loopear va con `Play()` en source propio.
9. Slider de volumen: rango 0.0001–1, `Mathf.Log10(v) * 20` hacia el exposed param del mixer; persistir el valor lineal en PlayerPrefs.
10. Un parámetro del mixer: o lo controlan snapshots o lo controla `SetFloat` — nunca ambos; `ClearFloat` para devolver control.
11. Ducking música-bajo-voz: Duck Volume en Music + Send desde Voice; release ~500 ms para retorno natural.
12. Timing musical SIEMPRE con `AudioSettings.dspTime` + `PlayScheduled` (programado ≥ ~1 s antes); duraciones con `(double)samples / frequency`, nunca `clip.length`.
13. Pausa de juego = `AudioListener.pause = true` (+ `ignoreListenerPause` en el source de UI); `Time.timeScale = 0` no pausa audio.
14. Crossfades/fades: corutina sobre volumen del mixer group con conversión log, con `Time.unscaledDeltaTime` (funciona en pausa).
15. Música persistente entre escenas: MusicManager con `DontDestroyOnLoad`, único.
16. Suscribirse a `AudioSettings.OnAudioConfigurationChanged` y reanudar sources si `deviceWasChanged` (auriculares/Bluetooth).
17. Juego de ritmo o feedback táctil en móvil: DSP Buffer Size = Best Latency + calibración de offset por usuario en Android.
18. iOS: decidir explícitamente `Mute Other Audio Sources` (OFF para casual games) y ofrecer mute de Música y SFX por separado.
19. Antes de ship: pasada con auriculares + altavoz de móvil real; probar interrupción por llamada y desconexión de auriculares.
20. Middleware solo con sound designer dedicado o música adaptativa compleja; si no, stack nativo.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Loop de música con gap audible | La fuente era MP3 (padding del encoder) o el corte no está en zero-crossing → fuente WAV bien cortada + `loop = true`; Unity la comprime a Vorbis igual |
| Intro+loop con `Invoke(introLength)` — gap o solape aleatorio | Dos sources + `PlayScheduled(start)` y `PlayScheduled(start + samples/frequency)` |
| Slider de volumen "todo o nada" (a mitad ya no se oye) | El fader es logarítmico: `Mathf.Log10(slider) * 20`, slider 0.0001–1 — jamás lerp lineal -80→0 dB |
| `SetFloat` a un exposed param y después los snapshots "no funcionan" | Exponer un parámetro se lo quita a los snapshots; `ClearFloat` lo devuelve |
| Fade por snapshot que suena apurado/frenado | La interpolación del snapshot no es perceptualmente lineal en volumen → fade por exposed param con conversión log |
| SFX importantes que se cortan con mucha acción | Se agotaron las voces reales: subir Max Real Voices o bajar `priority` (número) de los sonidos críticos |
| Toda la música en Decompress On Load — pico de memoria de cientos de MB | Vorbis descomprimido ocupa ~10× → música y ambientes largos en Streaming |
| `PlayClipAtPoint` en producción | Crea y destruye GameObjects (garbage, sin mixer group) → pool propio de sources |
| Metralleta de disparos idénticos, fatiga inmediata | Pitch/volumen aleatorios + varios clips (pool o Audio Random Container Shuffle) [ver: gamedev/audio] |
| Pausa con `Time.timeScale = 0` y la música sigue / el audio-timing usa `Time.time` | `AudioListener.pause = true`; timing con `dspTime` (se congela junto al audio y no requiere reprogramar al reanudar) |
| Al desconectar auriculares (o volver de una llamada) el juego queda mudo | Handler de `OnAudioConfigurationChanged` que re-lanza la música; probar interrupciones en dispositivo real |
| `AudioSettings.Reset` en runtime "para bajar latencia" y se calla todo | Reset PARA todo el audio: hacerlo solo en bootstrap/menú y relanzar música después |
| Doppler raro en sonidos que se mueven con el player | `dopplerLevel = 0` en sources parented a objetos rápidos |
| Sonido 3D audible desde toda la mapa | Rolloff Logarithmic nunca llega a 0 tras Max Distance → rolloff Linear o curva custom que muera en Max Distance |
| Mixer roto solo en build Web | En WebGL el AudioMixer solo deja cambiar volumen ("Volume is the only property you can change on Web") — efectos/filtros no funcionan → probar audio en build Web temprano |

## Fuentes

- Audio Clip Import Settings — Unity Manual 6000.2 (docs.unity3d.com) — load types con números de memoria (~10× Vorbis, 3.5× ADPCM, ~200 KB streaming) y formatos.
- Audio file compression / Audio files — Unity Manual 6000.2 — transcodificación al importar, formatos soportados, recomendación de fuente lossless.
- AudioSource component reference + `AudioSource.spatialBlend` — Unity Manual/Scripting 6000.2 — propiedades, rolloff, priority 0 (alta)–255 (baja), semántica 2D/3D.
- Audio Mixer overview + Audio Mixer (landing) — Unity Manual 6000.2/2022.3 — grupos, routing, snapshots (qué guardan), exposed params, ducking con Send.
- WebGL Audio — Unity Manual 6000.2 — cita exacta "Volume is the only property you can change on Web"; motivo (WebGL sin threading, Web usa Web Audio API interna en vez del motor nativo).
- `AudioMixerSnapshot.TransitionTo`, `AudioMixer.ClearFloat` — Unity Scripting API 6000.2 — semántica exacta de transiciones y reset de exposed params.
- `AudioSource.PlayScheduled`, `AudioSource.PlayOneShot`, `AudioSettings.dspTime` — Unity Scripting API 6000.2 — timing sample-accurate, comportamiento de one-shots, dspTime congelado en pausa/suspensión.
- Audio Random Container — Unity Manual 6000.2 — randomización nativa de clips (modos, triggers, loops) en Unity 6.
- Audio settings (class-AudioManager) + `AudioConfiguration.dspBufferSize` + `AudioSettings.GetDSPBufferSize` — Unity Manual/Scripting 6000.2 — DSP Buffer Size (4 presets), voces virtuales/reales, cómo leer la latencia real con `GetConfiguration()`.
- `AudioSettings.Mobile` + `AudioSettings.OnAudioConfigurationChanged` — Unity Scripting API 6000.2 — mute state iOS/Android, ahorro de batería, cambio de dispositivo de salida.
- iOS Player Settings — Unity Manual 6000.2 — Mute Other Audio Sources, Prepare iOS for Recording.
- "The right way to make a volume slider in Unity" — John Leonard French — fórmula Log10×20 y rango 0.0001–1, por qué falla el mapeo lineal.
- "Ultimate Guide to PlayScheduled in Unity" — John Leonard French — stitching sin gaps, duración por samples, compases con dspTime, AudioListener.pause.
- "How to fade audio in Unity: I tested every method" — John Leonard French — comparativa fade source vs mixer vs snapshot; ganador: mixer + conversión log.
- FMOD — Wikipedia + FMOD for Unity (Unity Asset Store) — tiers de licencia por presupuesto (Indie < $600k), plugin gratis, min Unity 2019.4.
