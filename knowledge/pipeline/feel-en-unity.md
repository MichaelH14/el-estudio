# Game feel implementado en Unity

> **Cuando cargar este archivo:** al implementar juice/game feel en un proyecto Unity 6 real — hit-stop, screenshake, tweens de feedback, partículas, flashes, knockback, números flotantes, input feel, audio feedback — o al ejecutar el "juice pass" final. La teoría (por qué y cuánto) está en [ver: gamedev/game-feel]; aquí está el CÓMO exacto con APIs de Unity 6.x/URP.

Este archivo asume: valores de calibración (frames de hit-stop, trauma, easings, duraciones) de [ver: gamedev/game-feel]; elección de lib de tweening y Animator vs tween de [ver: unity/animacion-unity]; Cinemachine 3.x e Impulse de [ver: unity/rendering-urp]; SFX/mixer de [ver: unity/audio-unity]. No se repiten — se usan.

## 1. Tweening: la herramienta base del juice

Elección de lib y comparativa completa en [ver: unity/animacion-unity] §5. Default 2026: **PrimeTween** (cero alloc, API estática). Los 10 tweens que cubren el 90% del juice:

| Uso | PrimeTween | DOTween |
|---|---|---|
| Mover (knockback visual, popup) | `Tween.Position(t, endValue, dur, Ease.OutCubic)` / `Tween.PositionY(...)` | `t.DOMove(...)` / `t.DOMoveY(...)` |
| Escalar (spawn, pickup) | `Tween.Scale(t, 1f, 0.25f, Ease.OutBack)` | `t.DOScale(1f, 0.25f).SetEase(Ease.OutBack)` |
| Rotar | `Tween.Rotation(t, Quaternion.Euler(0,0,180), dur)` | `t.DORotate(new Vector3(0,0,180), dur)` |
| Color (tint de daño) | `Tween.Color(spriteRenderer, Color.red, 0.1f)` | `sr.DOColor(Color.red, 0.1f)` |
| Alpha / fade | `Tween.Alpha(spriteRenderer, 0f, 0.3f)` | `sr.DOFade(0f, 0.3f)` |
| Punch (golpe recibido, botón) | `Tween.PunchScale(t, Vector3.one * 0.3f, 0.25f)` | `t.DOPunchScale(...)` |
| Shake local (objeto, no cámara) | `Tween.ShakeLocalPosition(t, strength, dur, frequency: 10)` | `t.DOShakePosition(...)` |
| Valor arbitrario (vignette, exposed param) | `Tween.Custom(0f, 1f, dur, v => x.intensity.value = v)` | `DOTween.To(...)` |
| Delay + callback | `Tween.Delay(0.5f, () => ...)` | `DOVirtual.DelayedCall(...)` |
| Yoyo / pulso (blink de invulnerable) | `cycles: 6, cycleMode: CycleMode.Yoyo` | `.SetLoops(6, LoopType.Yoyo)` |

**Secuencias** (combos de feedback encadenados):

```csharp
// PrimeTween: Chain = después, Group = a la vez, Insert = en un tiempo exacto
Sequence.Create()
    .Chain(Tween.PositionY(t, t.position.y + 1f, 0.3f, Ease.OutQuad))
    .Group(Tween.Scale(t, 1.2f, 0.3f))
    .Chain(Tween.Scale(t, 0f, 0.15f, Ease.InBack));
// DOTween: DOTween.Sequence() + Append / Join / Insert / AppendInterval / AppendCallback
```

**Unscaled time (UI de pausa, hit-stop):** los tweens normales se congelan con `Time.timeScale = 0`. Para menús de pausa y feedback durante hit-stop:
- PrimeTween: `Tween.Scale(t, 1f, new TweenSettings(duration: 0.3f, useUnscaledTime: true))`.
- DOTween: `.SetUpdate(true)` (ignora `Time.timeScale`).

Reglas heredadas de la base (no negociables): ease-out para respuesta a input, 100–300 ms, interrumpible desde el valor actual [ver: gamedev/game-feel] §5; matar tweens del target al destruir/poolear [ver: unity/animacion-unity].

## 2. Hit-stop

Semántica de `Time.timeScale` (Scripting API 6000.2): escala `Time.deltaTime`; con `timeScale = 0` **no corren `FixedUpdate` ni corrutinas suspendidas en `WaitForSeconds`** — por eso el timer del hit-stop debe ser unscaled. `Time.fixedDeltaTime` NO se auto-escala: para slow-motion sostenido (no hit-stop), escalar también `fixedDeltaTime *= timeScale` o la física se ve a tirones.

**Vía 1 — global (simple, para la mayoría de juegos):**

```csharp
public class HitStop : MonoBehaviour
{
    float pending; Coroutine running;
    // A 60 fps: 2-4 frames ≈ 0.03-0.07s (golpe normal), 8-15 ≈ 0.13-0.25s (kill/fuerte)
    public void Do(float seconds)
    {
        if (seconds <= pending) return;              // no acumular: gana el freeze mayor
        pending = seconds;
        if (running != null) StopCoroutine(running);
        running = StartCoroutine(Freeze());
    }
    IEnumerator Freeze()
    {
        Time.timeScale = 0f;
        yield return new WaitForSecondsRealtime(pending);   // corre en tiempo real
        Time.timeScale = 1f;                          // si usas slow-mo: restaurar el valor previo, no 1
        pending = 0f; running = null;
    }
}
```

**Vía 2 — selectivo (solo los implicados, el mundo sigue vivo — lo que recomienda [ver: gamedev/game-feel] §3):** congelar por entidad: `animator.speed = 0f` + guardar `rb.linearVelocity` (nombre Unity 6; `velocity` está deprecado) y ponerla a cero (o `rb.simulated = false` en 2D), restaurar tras el timer unscaled. Más código, mejor resultado en juegos con muchas entidades simultáneas.

Interacciones que hay que decidir a propósito:
- **Partículas**: con Main module → `Delta Time = Unscaled` siguen vivas durante el freeze (el mundo "respira" alrededor del golpe). Dejar `Scaled` en partículas de gameplay que sí deben congelarse.
- **Audio**: `timeScale = 0` NO pausa el audio — el SFX del golpe suena durante el freeze (deseable) [ver: unity/audio-unity].
- **Animator de UI**: Update Mode `Unscaled Time` [ver: unity/animacion-unity].
- **Tweens**: los scaled se congelan (correcto para gameplay); los de UI van unscaled (§1).

## 3. Screenshake: trauma sobre Cinemachine 3.x

Dos mecanismos complementarios sobre la misma CinemachineCamera (setup base de Impulse en [ver: unity/rendering-urp]):

| Mecanismo | Para qué | Cómo |
|---|---|---|
| **Impulse** (`CinemachineImpulseSource` + extensión `CinemachineImpulseListener`) | Eventos discretos direccionales: disparo, explosión puntual, aterrizaje. Equivale al "camera kick" | `impulse.GenerateImpulseWithVelocity(dir * fuerza)` — la dirección importa; firmas exactas en [ver: unity/rendering-urp] |
| **Noise** (`CinemachineBasicMultiChannelPerlin`) | Shake continuo acumulable — aquí vive el **sistema de trauma** | Componente Noise de la CinemachineCamera con un Noise Profile asset (el paquete trae varios presets listos; nombre exacto NO VERIFICADO, elegir uno con clic derecho → New al crear el componente); `AmplitudeGain`/`FrequencyGain` son controlables por script en runtime (doc del paquete) |

El sistema de trauma de Eiserloh ([ver: gamedev/game-feel] §4) implementado sobre el Noise:

```csharp
using Unity.Cinemachine;
public class TraumaShake : MonoBehaviour
{
    [SerializeField] CinemachineBasicMultiChannelPerlin noise;  // en la CinemachineCamera
    [SerializeField] float decay = 1.2f, maxAmplitude = 1.5f, frequency = 2f;
    [Range(0f, 1f)] public float userIntensity = 1f;            // slider de accesibilidad
    float trauma;

    public void Add(float amount) => trauma = Mathf.Clamp01(trauma + amount); // hit 0.2, explosión 0.5

    void Update()
    {
        trauma = Mathf.Max(0f, trauma - decay * Time.deltaTime);   // decae LINEAL
        float shake = trauma * trauma;                              // se aplica al CUADRADO
        noise.AmplitudeGain = shake * maxAmplitude * userIntensity;
        noise.FrequencyGain = frequency;
    }
}
```

- El Perlin del profile ya cumple "smooth noise, no random puro". En 2D el shake correcto es traslación + rotación en Z; en 3D solo rotación — se ajusta en el noise profile (canales de posición vs rotación).
- Nunca mover el transform de la Camera con Cinemachine activo: el Brain lo pisa cada frame [ver: unity/rendering-urp].
- Durante hit-stop global el shake queda congelado con el resto (el freeze dura milisegundos; en la práctica no se nota — verificar en juego).
- `userIntensity` expuesto en opciones: obligación de accesibilidad [ver: gamedev/game-feel].

## 4. Squash & stretch, punch y flashes

**Squash & stretch con tween** (conservar volumen: x↑ ⇒ y↓ [ver: gamedev/game-feel] §2):

```csharp
public void OnLand()   // aplastar al aterrizar y volver elástico
{
    transform.localScale = new Vector3(1.3f, 0.7f, 1f);
    Tween.Scale(transform, Vector3.one, 0.3f, Ease.OutElastic);
}
// Estirar en movimiento rápido: escalar el eje de la velocidad ~1.1-1.2 mientras |v| > umbral
```

Punch de daño/pickup: `Tween.PunchScale(transform, Vector3.one * 0.3f, 0.25f)`. Importante: tween de escala sobre un transform que NO anime escala el Animator (conflicto documentado en [ver: unity/animacion-unity] §4 — usar un hijo "Visual" si hace falta).

**Flash blanco de daño** — el gotcha primero: `SpriteRenderer.color` es tint **multiplicativo** (el shader por defecto multiplica), así que sirve para teñir a rojo/negro pero **nunca llega a blanco puro**. Flash a blanco = shader con propiedad de mezcla: Shader Graph (Sprite Lit/Unlit) con `Lerp(color base, blanco, _FlashAmount)` — patrón listado en [ver: unity/rendering-urp] §Shader Graph.

Cómo setear `_FlashAmount` por instancia — dos opciones con trade-off real:

| Opción | Coste | Cuándo |
|---|---|---|
| `MaterialPropertyBlock` + `Renderer.SetPropertyBlock` | La doc oficial advierte: **no compatible con SRP Batcher** — en URP puede costar rendimiento | Pocos renderers flasheando a la vez (un boss, un puñado de enemigos): irrelevante en la práctica |
| Instancia de material (`renderer.material`) | Crea copia del material (liberar al destruir); con SRP Batcher muchos materiales del mismo shader son baratos | Muchos objetos flasheando o proyecto que ya cuida draw calls [ver: unity/rendering-urp] |

```csharp
static readonly int FlashId = Shader.PropertyToID("_FlashAmount");
[SerializeField] SpriteRenderer sr;
Material mat;                    // instancia propia (opción 2)
void Awake() => mat = sr.material;
public void Flash() =>           // 1-3 frames ≈ 0.03-0.05s en blanco y volver
    Tween.Custom(1f, 0f, 0.15f, v => mat.SetFloat(FlashId, v), Ease.OutQuad);
```

**Flashes de pantalla / daño al jugador**: no un quad blanco fullscreen — pulso de Vignette (o Chromatic Aberration) vía Volume override en runtime: `volume.profile.TryGet(out vignette)` + tween de `vignette.intensity.value` de 0.45 → base (receta y snippet en [ver: unity/rendering-urp] §Post-processing). Reservar para eventos mayores (fatiga/fotosensibilidad).

## 5. Knockback y números flotantes

**Knockback** (dirección del golpe = posición víctima − posición atacante):

```csharp
// Con Rigidbody2D (nombres Unity 6)
rb.linearVelocity = Vector2.zero;                          // resultado consistente golpe a golpe
rb.AddForce(dir.normalized * fuerza, ForceMode2D.Impulse);

// Con character controller propio: canal de velocidad aditivo con decay
knockback = dir.normalized * fuerza;                                        // al recibir el golpe
knockback = Vector2.MoveTowards(knockback, Vector2.zero, decel * Time.deltaTime); // cada frame
velocidadFinal = input * speed + knockback;                                 // el input nunca se bloquea del todo
```

AddForce vs velocity, y las 3 vías de character controller: [ver: unity/fisica-unity]. El micro-retroceso del ATACANTE al disparar (Vlambeer) es el mismo canal `knockback` con fuerza pequeña + el kick de cámara del §3.

**Números flotantes de daño** — pooling obligatorio (`ObjectPool<T>`, semántica completa en [ver: unity/csharp-patrones] §4) + TextMeshPro world-space [ver: unity/ui-unity]:

```csharp
public class DamageNumbers : MonoBehaviour
{
    [SerializeField] TMP_Text prefab;      // TextMeshPro (3D/world), no UGUI
    ObjectPool<TMP_Text> pool;
    void Awake() => pool = new ObjectPool<TMP_Text>(
        () => Instantiate(prefab, transform),
        t => t.gameObject.SetActive(true),
        t => t.gameObject.SetActive(false), maxSize: 64);

    public void Show(Vector3 worldPos, int dmg, bool crit)
    {
        var t = pool.Get();
        t.text = dmg.ToString();
        t.transform.position = worldPos + (Vector3)(Random.insideUnitCircle * 0.3f); // no apilar
        t.fontSize = crit ? 8f : 5f;  t.color = crit ? Color.yellow : Color.white;
        t.alpha = 1f;
        Tween.PositionY(t.transform, t.transform.position.y + 1f, 0.6f, Ease.OutCubic);
        Tween.Custom(1f, 0f, 0.6f, a => t.alpha = a).OnComplete(() => pool.Release(t));
    }
}
```

En 3D, el prefab lleva un script billboard (mirar a la cámara en `LateUpdate`). Convención de género y cuándo NO usarlos: [ver: gamedev/game-feel] §2.

## 6. Particle System (Shuriken) a fondo

El hueco de la base — módulos con nombre exacto (Manual 6000.2) y para qué sirven en juice:

| Módulo | Qué controla | Uso de juice típico |
|---|---|---|
| **Main** | Estado inicial: Duration, Looping, Start Lifetime/Speed/Size/Rotation/Color, Gravity Modifier, Simulation Space (Local/World/Custom), Simulation Speed, **Delta Time (Scaled/Unscaled)**, Play On Awake, Max Particles, **Stop Action** (Disable/Destroy/**Callback**), **Ring Buffer Mode**, Culling Mode | La base de todo; ver recetas abajo |
| **Emission** | Rate over Time, Rate over Distance, **Bursts** (Time, Count, Cycles, Interval, Probability) | Juice = casi siempre **burst**, no rate: impacto → 1 burst de 10–30 |
| **Shape** | Volumen/superficie de emisión (Cone, Sphere, Circle, Edge…) | Cone estrecho = chispas direccionales; Circle = anillo de aterrizaje |
| **Velocity / Force over Lifetime** | Empuje durante la vida | Debris que sale disparado y cae |
| **Limit Velocity over Lifetime** | Frena partículas (drag) | Explosión que "se asienta" |
| **Color over Lifetime** | Gradiente por edad | Fade-out SIEMPRE (nunca partículas que desaparecen en seco) |
| **Size over Lifetime** | Curva de tamaño | Chispas que encogen; humo que crece |
| **Noise** | Turbulencia | Humo/fuego orgánico |
| **Collision** | Colisión con mundo (Planes o World); Dampen/Bounce; Send Collision Messages → `OnParticleCollision` | Debris que rebota en el suelo y se queda |
| **Sub Emitters** | Sistemas hijos disparados por **Birth / Collision / Death / Trigger / Manual** (`ParticleSystem.TriggerSubEmitter`) | Proyectil (trail en Birth) que explota (burst en Death) |
| **Texture Sheet Animation** | Frames desde grid o modo Sprites | Explosiones animadas; sprites del atlas del juego [ver: arte-a-unity] |
| **Trails** | Estelas por partícula (Trail Material aparte en el Renderer) | Trail de proyectiles/dash |
| **Renderer** | Render Mode (Billboard/Stretched/Mesh), Material, Sort Mode, **Sorting Layer ID + Order in Layer**, Sorting Fudge, Masking (Sprite Mask) | Integración 2D (abajo) |

**Receta impacto estándar** (golpe/muerte): Looping OFF, Duration ~0.5, burst de 12–24, Shape Cone (o Circle en 2D), Start Speed 3–8 con rango, Start Size con rango, Gravity Modifier ~1, Size over Lifetime decreciente, Color over Lifetime → alpha 0, Simulation Space **World** (las partículas no siguen al emisor si este se mueve o muere).

**Permanencia barata** (casquillos, cráteres [ver: gamedev/game-feel] §2): Start Lifetime alto + **Ring Buffer Mode = Pause Until Replaced** — las partículas quedan pausadas al final de su vida y solo se reciclan cuando Max Particles obliga: permanencia con presupuesto fijo, sin scripts.

**2D**: Renderer → Sorting Layer ID + Order in Layer igual que un sprite (ponerlas en la capa FX); Sorting Fudge para desempatar contra otros transparentes; material con la textura/sprite del juego (Texture Sheet Animation en modo Sprites usa el atlas). El overdraw de partículas es el asesino en móvil — pocas, chicas, sin quads gigantes casi transparentes [ver: unity/rendering-urp] §overdraw.

**Pooling de sistemas** (nunca `Instantiate`/`Destroy` por impacto [ver: unity/csharp-patrones]):

```csharp
// Prefab: Play On Awake OFF, Looping OFF, Stop Action = Callback
public class PooledVfx : MonoBehaviour
{
    public ObjectPool<PooledVfx> Pool;   // lo inyecta el manager al crear
    ParticleSystem ps;
    void Awake() => ps = GetComponent<ParticleSystem>();
    public void PlayAt(Vector3 pos) { transform.position = pos; ps.Play(); }
    void OnParticleSystemStopped() => Pool.Release(this);  // dispara gracias a Stop Action = Callback
}
```

Al reciclar a mano: `ps.Stop(true, ParticleSystemStopBehavior.StopEmittingAndClear)`. Para emitir sin re-play: `ps.Emit(20)` (o `Emit(emitParams, count)` para posición/color por llamada) sobre un sistema único compartido — aún más barato que poolear GameObjects.

**VFX Graph — qué es y cuándo** (Manual: "Choosing your particle system solution"): corre en **GPU**, escala a **millones** de partículas (Shuriken: miles, CPU), requiere plataformas con **compute shaders** y URP/HDRP. Contras para juice: sin interacción con la física CPU (colisiona contra depth buffer y elementos definidos en el graph), C# limitado a propiedades expuestas y eventos — no lees/escribes partículas individuales ni recibes `OnParticleCollision`. Criterio: **feel de gameplay (impactos, hits, debris que interactúa) = Particle System; espectáculo ambiental masivo (lluvia, enjambres, magia de pantalla completa) = VFX Graph**. Un juego indie típico no lo necesita.

## 7. Input feel: buffering y coyote time

El patrón completo (timestamps de eventos, robusto frente al desfase Update/FixedUpdate) ya está en [ver: unity/input-system] §buffering — cargarlo al implementar. Lo esencial que NO se puede omitir:

- Buffer window 0.1–0.2 s; coyote 0.05–0.15 s; **consumir** el buffer al usarlo o un press dispara dos saltos.
- Nunca `WasPressedThisFrame()` dentro de `FixedUpdate` (pierde/duplica presses): latch en `Update` o timestamps con `ctx.time`.
- El buffering también aplica a acciones en recovery/hit-stop: encolar y ejecutar en el primer frame válido [ver: gamedev/game-feel] §8.
- Coyote + buffer + gravedad asimétrica + corner correction son el paquete mínimo de cualquier juego con salto — no opcionales.

## 8. Audio feedback

Implementación completa (pool de AudioSources, Audio Random Container, mixer) en [ver: unity/audio-unity]; diseño en [ver: gamedev/audio]. Lo específico del feel:

- SFX en el **mismo frame** del evento — `PlayOneShot` directo en el handler del hit, jamás "cuando llegue la animación".
- Variación anti-metralleta: pitch ±5–10% + volumen ±15% + 2–4 clips (pool round-robin o Audio Random Container en Shuffle).
- **Pitch ascendente en combos** (Jonasson/Purho — el combo "canta"): subir un semitono por hit consecutivo:

```csharp
source.pitch = Mathf.Pow(1.05946f, Mathf.Min(comboCount, 12));  // 2^(1/12) por semitono, cap a la octava
```

- **Capas por intensidad**: un golpe = clip seco siempre + capa grave si daño > umbral + cola/debris si kill. Tres `PlayOneShot` simultáneos del pool, no un mega-clip.
- El audio sigue sonando durante hit-stop (timeScale no lo pausa) — es feedback gratis; en pausa real usar `AudioListener.pause` [ver: unity/audio-unity].

## 9. El juice pass: checklist ejecutable

Orden de impacto (síntesis Vlambeer + Jonasson/Purho [ver: gamedev/game-feel] §9), sobre un juego que YA es divertido apagado. Ejecutar de arriba a abajo; probar en juego tras cada paso:

| # | Paso | Herramienta Unity | Sección |
|---|---|---|---|
| 1 | Curvas de movimiento del avatar (aceleración, gravedad asimétrica) + coyote/buffer | Controller propio + Input System | §7, [ver: unity/fisica-unity] |
| 2 | SFX en TODO evento + variación de pitch | Pool de sources / Audio Random Container | §8 |
| 3 | Tweenear todo lo que aparece/muere/se toca (ease-out, 100–300 ms) | PrimeTween/DOTween | §1 |
| 4 | Partículas de impacto + muerte, por material/superficie | Particle System pooled, bursts | §6 |
| 5 | Hit-stop escalado con el daño | `HitStop.Do()` | §2 |
| 6 | Screenshake (trauma) + camera kick direccional | Noise Perlin + Impulse | §3 |
| 7 | Flash blanco en el golpeado + knockback | Shader `_FlashAmount` + AddForce/canal | §4, §5 |
| 8 | Squash & stretch en saltos/aterrizajes/golpes | Tween de escala, OutElastic | §4 |
| 9 | Permanencia: debris/casquillos/marcas que quedan | Collision module + Ring Buffer | §6 |
| 10 | Cámara: deadzone + lookahead + damping | Position Composer | [ver: unity/rendering-urp] |
| 11 | Números flotantes (si el género los pide [ver: gamedev/generos]) | TMP + ObjectPool + tween | §5 |
| 12 | Post-procesado puntual: pulso de vignette al daño, bloom en proyectiles | Volume overrides runtime | §4, [ver: unity/rendering-urp] |
| 13 | Personalidad (ojos, idle animado, reacciones baratas) | Sprites/tweens | [ver: gamedev/game-feel] §9 |
| 14 | Opciones de accesibilidad: sliders de shake y flashes | `userIntensity` + toggles persistidos | §3 |

Pasarse y luego recortar; calibrar con el mando en la mano. El juice se hace al final del proyecto, no en prototipo [ver: pipeline-completo] [ver: produccion-solo-dev].

## Reglas practicas

1. Una sola lib de tweening por proyecto (default: PrimeTween); tweens de UI de pausa con `useUnscaledTime` / `.SetUpdate(true)`.
2. Todo tween de feedback: ease-out, 100–300 ms, interrumpible, y matado al destruir/poolear el target.
3. Hit-stop con timer en `WaitForSecondsRealtime` — nunca `WaitForSeconds` (se congela con timeScale 0 y no vuelve).
4. Hit-stop no acumulable: gana el freeze mayor; restaurar el timeScale PREVIO (no 1 fijo) si hay slow-mo en el juego.
5. Slow-motion sostenido: escalar también `Time.fixedDeltaTime` con el timeScale; hit-stop de milisegundos: no hace falta.
6. Partículas que deben vivir durante hit-stop: Main → Delta Time = Unscaled; el resto Scaled.
7. Screenshake: trauma ∈ [0,1] acumulable, decae lineal, `AmplitudeGain = trauma² × max × sliderUsuario`.
8. Eventos direccionales (disparo, explosión cercana): Impulse con velocity direccional ADEMÁS del trauma; jamás mover el transform de la Camera.
9. Flash a blanco = shader con `_FlashAmount` (el tint de SpriteRenderer es multiplicativo, no llega a blanco); tint a rojo/oscuro sí vale con `.color`.
10. `MaterialPropertyBlock` rompe SRP Batcher (doc oficial): en URP a escala, preferir instancias de material; MPB solo con pocos renderers afectados.
11. Knockback con Rigidbody: resetear `linearVelocity` antes del `AddForce(..., ForceMode2D.Impulse)`; con controller propio: canal aditivo con decay, sin bloquear el input.
12. Juice de impacto con partículas = Emission por **Bursts**, Simulation Space **World**, Color over Lifetime con fade a alpha 0.
13. VFX de impacto pooled: Play On Awake OFF + Stop Action Callback + `OnParticleSystemStopped` → Release; o `ps.Emit(n)` sobre un sistema compartido.
14. Permanencia (casquillos, restos): Ring Buffer Mode Pause Until Replaced con Max Particles como presupuesto.
15. Partículas 2D: Sorting Layer/Order in Layer en el Renderer module; vigilar overdraw en móvil antes que cualquier otra optimización.
16. VFX Graph solo para masa ambiental GPU (requiere compute shaders); el feel de gameplay se queda en Particle System.
17. Números flotantes: `ObjectPool<T>` + offset aleatorio de spawn + fade con release al pool — cero Instantiate por golpe.
18. Coyote + jump buffer + consumo del buffer: paquete mínimo obligatorio de cualquier salto (patrón exacto en [ver: unity/input-system]).
19. SFX del golpe en el mismo frame; pitch ±5–10%; combos con pitch ascendente por semitonos con cap.
20. Ejecutar el juice pass del §9 en orden, jugando tras cada paso; sliders de shake/flash en opciones antes de ship.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Hit-stop con `WaitForSeconds` → el juego queda congelado para siempre | `WaitForSecondsRealtime` (las corrutinas con WaitForSeconds no avanzan con timeScale 0 — doc oficial) |
| Dos golpes seguidos: el segundo hit-stop corta al primero y el freeze se siente aleatorio | Manager único: gana el freeze mayor, una sola corrutina viva |
| Hit-stop restaura `timeScale = 1` y pisa el slow-mo activo | Guardar y restaurar el valor previo |
| Slow-mo con física a tirones | `fixedDeltaTime` no se auto-escala: multiplicarlo por el timeScale |
| Tween de UI de pausa que no se mueve | Está en tiempo scaled: `useUnscaledTime` / `SetUpdate(true)` |
| Shake moviendo `Camera.transform` con Cinemachine | El Brain lo pisa: Impulse + Noise (`AmplitudeGain` por trauma) |
| Shake proporcional lineal al evento (se siente barato) | Sistema de trauma: acumular, decaer lineal, aplicar al cuadrado [ver: gamedev/game-feel] |
| `SpriteRenderer.color = Color.white` "no hace nada" como flash | Es tint multiplicativo: shader con `_FlashAmount` para llegar a blanco |
| Flashes por MPB en decenas de renderers URP y bajan los FPS | MPB rompe SRP Batcher: instancias de material del mismo shader |
| Knockback inconsistente (a veces vuela, a veces nada) | La velocity previa se suma: resetear `linearVelocity` antes del impulso |
| Partículas de impacto que siguen al enemigo muerto / al emisor | Simulation Space Local: cambiarlo a World |
| Partículas de golpe con Rate over Time (chorro continuo) | Impacto = Burst único con Count alto |
| `Instantiate`/`Destroy` de un VFX por cada golpe → GC spikes | Pool con Stop Action Callback, o `Emit()` sobre sistema compartido |
| Partículas invisibles en el juego 2D (detrás del fondo) | Renderer module → Sorting Layer FX + Order in Layer, como cualquier sprite |
| VFX Graph elegido "porque es más nuevo" y las partículas no colisionan ni avisan a C# | GPU sin física CPU ni per-particle C#: volver a Particle System para gameplay |
| Números de daño apilados ilegibles en el mismo punto | Offset aleatorio de spawn + pooling + fade corto |
| El salto "no responde" en los bordes | Falta coyote + buffer; y el buffer sin consumir dispara doble salto [ver: unity/input-system] |
| Ráfaga de SFX idénticos (metralleta) | Pitch/volumen aleatorios, varios clips, cap de voces [ver: unity/audio-unity] |
| Juicear un prototipo que aún no es divertido | El juice amplifica, no arregla: primero el core loop [ver: gamedev/fundamentos-diseno] |

## Fuentes

- **Time.timeScale** — Unity Scripting API 6000.2 (docs.unity3d.com) — semántica exacta: deltaTime escalado, FixedUpdate y WaitForSeconds detenidos a 0, fixedDeltaTime no auto-escalado.
- **Particle System modules** — Unity Manual 6000.2 (`ParticleSystemModules.html`) — inventario completo de módulos con su función.
- **Main module** — Unity Manual 6000.2 (`PartSysMainModule.html`) — Delta Time Scaled/Unscaled, Stop Action (Disable/Destroy/Callback), Ring Buffer Mode, Simulation Space, Culling Mode: nombres exactos.
- **Emission module** — Unity Manual 6000.2 (`PartSysEmissionModule.html`) — Rate over Time/Distance y Bursts (Time, Count, Cycles, Interval, Probability).
- **Sub Emitters module** — Unity Manual 6000.2 (`PartSysSubEmitModule.html`) — condiciones Birth/Collision/Death/Trigger/Manual y `ParticleSystem.TriggerSubEmitter`.
- **Renderer module** — Unity Manual 6000.2 (`PartSysRendererModule.html`) — Render Modes, Sort Mode, Sorting Layer ID/Order in Layer, Sorting Fudge, Masking con Sprite Mask.
- **Choosing your particle system solution** — Unity Manual 6000.2 — Shuriken (CPU, miles, física, C# total) vs VFX Graph (GPU, millones, compute shaders, C# limitado a propiedades/eventos).
- **Cinemachine Impulse overview** — docs del paquete com.unity.cinemachine@3.1 — arquitectura Source/Listener, canales, tipos de source.
- **CinemachineBasicMultiChannelPerlin** — docs del paquete com.unity.cinemachine@3.1 — Noise Profile, Amplitude/Frequency Gain animables en runtime: la percha del sistema de trauma.
- **PrimeTween README** — GitHub KyryloKuzyk/PrimeTween — firmas de Tween.*, Sequence Chain/Group/Insert, TweenSettings con useUnscaledTime, StopAll, cycles/yoyo.
- **DOTween documentation** — dotween.demigiant.com — SetUpdate(isIndependentUpdate), Sequence Append/Join/Insert, shortcuts DO*, SetEase/SetLoops, Kill.
- **MaterialPropertyBlock** — Unity Scripting API 6000.2 — uso con SetPropertyBlock y advertencia oficial de incompatibilidad con SRP Batcher.
- Archivos de la base sintetizados: **gamedev/game-feel.md** (toda la teoría y calibración), **unity/animacion-unity.md** (libs de tweening, Animator vs tween, unscaled), **unity/rendering-urp.md** (Cinemachine 3.x/Impulse, Shader Graph, Volumes, overdraw, SRP Batcher), **unity/audio-unity.md** (pool de SFX, variación, pausa de audio), **unity/input-system.md** (patrón de buffer/coyote), **unity/csharp-patrones.md** (`ObjectPool<T>`).
