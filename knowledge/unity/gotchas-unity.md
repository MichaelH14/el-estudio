# Gotchas de Unity (errores que todos cometen)

> **Cuando cargar este archivo:** al depurar comportamiento "imposible" (NullReference intermitente, objetos que no mueren, estado que se pierde), antes de escribir código que toque lifecycle/física/serialización/prefabs, y siempre que un build móvil se comporte distinto al Editor.

Formato de cada gotcha: **Síntoma → Causa → Fix**. Verificado contra docs oficiales de Unity 6.2 (6000.2) en 2026-07.

---

## 1. El "fake null": UnityEngine.Object destruido no es null de verdad

**Síntoma:** `if (obj != null)` dice que el objeto existe pero al usarlo explota con `MissingReferenceException`; o al revés: `obj?.DoThing()` ejecuta sobre un objeto destruido; `obj ?? fallback` devuelve el destruido en vez del fallback.

**Causa:** `UnityEngine.Object` sobrecarga `==`/`!=`. Según docs oficiales: además de chequear la referencia managed, "the custom `==` operator in `UnityEngine.Object` also checks if the underlying native object pointer is null". Al hacer `Destroy()`, muere el objeto nativo pero el wrapper C# sigue vivo → un "fake null": compara `== null` como true, pero **no es null para el runtime de C#**.

Los operadores `??`, `?.`, `is null` e `is not null` usan el chequeo de null **puro de .NET** y NUNCA pasan por el operador custom (confirmado por JetBrains/Rider, que lo marca como inspección). Resultado: mienten sobre objetos destruidos.

**Fix:**

```csharp
// ✓ CORRECTO con UnityEngine.Object (pasa por el operador custom):
if (target != null) target.DoThing();
if (target) target.DoThing();          // conversión implícita a bool, equivale

// ✗ PROHIBIDO con UnityEngine.Object:
target?.DoThing();                     // ?. ignora el estado destruido
var t = target ?? fallback;            // ?? igual
if (target is null) ...                // is null igual
```

- Regla mecánica: `?.` `??` `??=` `is null` solo sobre clases C# puras, jamás sobre `MonoBehaviour`, `Component`, `GameObject`, `ScriptableObject` o cualquier derivado de `UnityEngine.Object`.
- Tras `Destroy(x)`, poner `x = null` a mano si la referencia se va a reusar — así el chequeo es barato y honesto.
- El `== null` de Unity es **más caro** que un null-check normal (llama a código nativo — JetBrains lo documenta). En hot loops: chequear una vez fuera del loop y cachear el resultado en un bool.
- Nota Editor: en el Inspector, campos no asignados de tipos Unity contienen un objeto placeholder que compara `== null` pero engaña igual a `?.`/`??` (comportamiento descrito en el blog oficial "Custom == operator, should we keep it", 2014 — NO re-verificado en Unity 6, pero el operador custom sí está en docs actuales).
- `Destroy()` no destruye inmediato: se aplica al final del frame. En el mismo frame el objeto aún "existe" para la física y renderizado.

[ver: csharp-patrones] para políticas de null en código C# puro.

---

## 2. Execution order entre scripts: NO garantizado

**Síntoma:** `NullReferenceException` en `Start`/`Awake` que aparece "a veces", o solo en build, o solo tras cambiar de escena. El clásico: `GameManager.Instance` es null porque el consumidor corrió antes que el manager.

**Causa:** Docs oficiales: "You can't rely on the order in which the same event function is invoked for different GameObjects" y "The order in which Unity calls each GameObject's Awake is not deterministic". El orden puede cambiar entre Editor y build, entre plataformas, y al reordenar la jerarquía.

**Fix (en orden de preferencia):**

1. **Disciplina Awake/Start** (resuelve el 90%): en `Awake` solo auto-inicialización (mis propios `GetComponent`, mis estructuras); en `Start` todo lo que toque OTROS scripts. Unity garantiza que **todos los Awake corren antes que cualquier Start** (de los objetos activos de la escena cargada).
2. **Lazy init** para singletons/servicios:

```csharp
static GameManager instance;
public static GameManager Instance
{
    get
    {
        if (instance == null)
            instance = FindFirstObjectByType<GameManager>();
        return instance;
    }
}
```

3. **Script Execution Order** (Project Settings > Script Execution Order): fija orden explícito por clase. Usar solo para pocos scripts críticos (managers antes que todo, integraciones después) — si hay 20 entradas ahí, la arquitectura está mal. [ver: arquitectura-unity]

Detalles que muerden:
- `Awake` corre aunque el componente esté **disabled** (docs: "Awake is called even if the script is a disabled component of an active GameObject"). `Start` no corre hasta que se habilite.
- `OnEnable` corre entre Awake y Start. Suscribir eventos en `OnEnable`/desuscribir en `OnDisable`, pero cuidado: en el primer frame `OnEnable` puede correr antes que el `Awake` de OTRO objeto.
- Objetos instanciados en runtime: su `Awake`/`OnEnable` corren DENTRO de la llamada a `Instantiate`.

---

## 3. Búsquedas caras en Update + strings mágicos

**Síntoma:** frame time que crece con el tamaño de la escena; profiler lleno de `FindObjectOfType`/`GameObject.Find`; typos en tags/parámetros de animator que fallan en silencio.

**Causa/Fix por API:**

| API | Problema (docs oficiales) | Fix |
|---|---|---|
| `GameObject.Find` | "causes significant performance degradation at scale... especially in MonoBehaviour.Update"; busca TODA la escena, sin caché, y **solo encuentra objetos activos** | Cachear en `Start`/`Awake`; mejor aún: referencia serializada o registro/inyección |
| `GetComponent` en Update | Búsqueda por frame evitable | Cachear en campo en `Awake` |
| `Camera.main` | En Unity 6 usa caché interna de objetos con tag MainCamera, pero "Accessing this property has a small CPU overhead, comparable to calling GameObject.GetComponent" | Cachear en campo si se usa por frame |
| `tag == "Enemy"` | Comparación de strings; typo = false silencioso | `CompareTag("Enemy")`; en Unity 6 existe `TagHandle` reutilizable, "can be faster than the overload which takes a string" |
| `animator.SetBool("isRunning", ...)` | Hash del string en cada llamada; typo = warning fácil de no ver | `static readonly int IsRunning = Animator.StringToHash("isRunning");` — docs: el id "persists between sessions and can be used for networking" |

Patrón general: **cero strings mágicos repetidos** — toda tag, param de animator, nombre de escena o layer vive en una clase de constantes. [ver: animacion-unity] para el patrón completo con Animator.

---

## 4. Instantiate/Destroy en caliente: stutters por GC

**Síntoma:** hitches periódicos (picos de ms cada X segundos) en gameplay con proyectiles/partículas/enemigos; el Profiler muestra `GC.Collect` o `GC.Alloc` por frame.

**Causa:** Docs: el GC corre cuando "a script tries to make an allocation on the managed heap but there isn't enough free heap memory". Ejemplo oficial: 1 KB/frame a 60 FPS = 3.6 MB/minuto en miles de alocaciones pequeñas → colecciones largas. `Instantiate` aloca (objeto + componentes) y `Destroy` genera basura; en caliente es el generador de stutter #1.

**Fix:** pooling. Unity 6 trae `UnityEngine.Pool.ObjectPool<T>` integrado:

```csharp
using UnityEngine.Pool;

ObjectPool<Bullet> pool;

void Awake()
{
    pool = new ObjectPool<Bullet>(
        createFunc: () => Instantiate(bulletPrefab),
        actionOnGet: b => b.gameObject.SetActive(true),
        actionOnRelease: b => b.gameObject.SetActive(false),
        actionOnDestroy: b => Destroy(b.gameObject),
        collectionCheck: true,   // detecta double-release (dejarlo en dev)
        defaultCapacity: 32,
        maxSize: 256);           // Release con pool lleno DESTRUYE la instancia
}
```

- El objeto pooleado debe **resetear su estado** en `actionOnGet` (velocidad, trail, timers) — el bug clásico del pooling es un proyectil reciclado que conserva velocidad vieja.
- Objetivo oficial de alocación en gameplay: "ideally to 0 bytes per frame".
- Otras fuentes de basura por frame: concatenación de strings en UI, LINQ en Update, closures que capturan, boxing. [ver: rendimiento-unity]

---

## 5. Movimiento: deltaTime, física y transform vs Rigidbody

**Síntoma:** velocidad del juego atada al frame rate; jitter en objetos físicos; colliders que se atraviesan; el personaje "vibra" contra paredes.

**Causas y fixes:**

| Error | Por qué está mal | Fix |
|---|---|---|
| Mover sin `Time.deltaTime` | A 120 FPS va el doble de rápido que a 60 | `pos += speed * Time.deltaTime` |
| Física/fuerzas en `Update` | La simulación corre a paso fijo (default 0.02 s = 50 Hz); `FixedUpdate` "may be called zero, one, or multiple times per frame" | Fuerzas y movimiento de Rigidbody SIEMPRE en `FixedUpdate` |
| Usar `fixedDeltaTime` a mano en FixedUpdate | Innecesario | Docs: dentro de `FixedUpdate`, `Time.deltaTime` "returns Time.fixedDeltaTime" — usar `deltaTime` en ambos lados y es correcto siempre |
| Mover el `transform` de un GameObject con Rigidbody dinámico | Teletransporta el body saltándose la simulación: sin interpolación, colisiones mal resueltas, tunneling | Dinámico: `AddForce`/`linearVelocity`. Kinemático: `Rigidbody.MovePosition` en `FixedUpdate` — docs: "complies with the interpolation settings"; para teleport real usar `Rigidbody.position` |
| Leer input en `FixedUpdate` | `GetKeyDown`/`GetButtonDown` son por-frame; FixedUpdate puede correr 0 veces ese frame → input perdido, o 2+ veces → duplicado | Leer input en `Update`, guardarlo en un campo, consumirlo en `FixedUpdate`. [ver: input-system] |
| Cámara que sigue a un Rigidbody y vibra | Cámara actualiza en Update/LateUpdate, body en paso fijo | Activar **Interpolate** en el Rigidbody del jugador |

[ver: fisica-unity] para el playbook completo de Rigidbody/colliders.

---

## 6. Serialización: lo que no se guarda y por qué

**Síntoma:** un campo no aparece en el Inspector; valores configurados que "se pierden"; un Dictionary que nunca persiste; tweaks hechos probando el juego que desaparecen.

**Reglas (docs oficiales, Unity 6.2):** un campo serializa solo si es `public` o tiene `[SerializeField]`, y NO es `static`, `const` ni `readonly`. Serializan: primitivos, enums (≤32 bits), tipos Unity (Vector3, Color...), referencias a `UnityEngine.Object`, clases/structs custom con `[Serializable]`, y `array`/`List<T>` de lo anterior.

**No serializan:** propiedades (solo su backing field si es serializable), `Dictionary`, arrays multidimensionales/jagged, contenedores anidados (`List<List<T>>`).

| Gotcha | Fix |
|---|---|
| Campo privado invisible en Inspector | `[SerializeField] float speed = 5f;` — privado + serializado es el default correcto |
| `public` solo para exponer al Inspector | Mal: expone API. Usar `[SerializeField] private` + propiedad de solo lectura |
| Dictionary no persiste | Dos `List<>` paralelas + `ISerializationCallbackReceiver` (el ejemplo oficial de esa API es exactamente este caso). ⚠️ Docs: el serializer "runs on a different thread from most of the Unity API" — dentro de `OnBeforeSerialize`/`OnAfterDeserialize` NO llamar API de Unity, solo transformar los propios campos |
| Clase custom `[Serializable]` sin `[SerializeReference]` | Serializa **inline por valor**: sin null (se materializa un objeto default), sin polimorfismo, sin referencias compartidas. Si se necesita null/herencia/grafos → `[SerializeReference]` |
| **Cambios en Play Mode se pierden** | Docs: "In Play mode, any changes you make are temporary and are reset when you exit Play mode" (el Editor oscurece la UI como aviso — Play Mode tint). Tweaks buenos: copiar el componente en Play (Copy Component) y pegarlo saliendo (Paste Component Values), o anotar los valores ANTES de salir |
| Estado privado no serializable se resetea en hot reload | Al recompilar en Play, Unity serializa/deserializa lo que puede; lo no serializable vuelve a default. No confiar en estado vivo a través de recompilaciones |

```csharp
[Serializable]
public class SerializableDict<K, V> : ISerializationCallbackReceiver
{
    [SerializeField] List<K> keys = new();
    [SerializeField] List<V> values = new();
    public Dictionary<K, V> dict = new();

    public void OnBeforeSerialize()
    {
        keys.Clear(); values.Clear();
        foreach (var kv in dict) { keys.Add(kv.Key); values.Add(kv.Value); }
    }
    public void OnAfterDeserialize()
    {
        dict.Clear();
        for (int i = 0; i < keys.Count; i++) dict[keys[i]] = values[i];
    }
}
```

---

## 7. Prefabs: overrides accidentales y referencias rotas

**Síntoma:** cambias el prefab asset y una instancia en escena ignora el cambio; un prefab pierde referencias al arrastrarlo a otra escena; "Apply All" pisó el prefab con basura de una instancia de prueba.

**Causas (docs oficiales):**
- "An overridden property value on a prefab instance always takes precedence over the value from the prefab asset" — cualquier tweak en la instancia (marcado con **línea azul** en el Inspector, badge +/− en componentes/hijos añadidos) desconecta ESA propiedad del asset para siempre, hasta Apply o Revert.
- Un prefab **asset** no puede referenciar objetos de escena (viven en mundos distintos). En la instancia puedes asignar la referencia como override, pero no se puede aplicar al asset — al usar el prefab en otra escena, esa referencia no existe.

**Fixes:**
- Higiene: tras tunear una instancia, decidir explícito — **Apply** (el cambio es para todos) o **Revert** (era experimento). Revisar el dropdown Overrides antes de commitear una escena. [ver: assets-pipeline-git]
- Nunca "Apply All" a ciegas: aplica TODOS los overrides, incluidos los accidentales (posición movida sin querer, un componente de debug).
- Referencias prefab→escena: resolver en runtime (`FindFirstObjectByType` en Start, una sola vez), inyectar desde un script de escena que sí conoce ambos lados, o desacoplar con un `ScriptableObject` como canal de eventos/registro. [ver: arquitectura-unity]
- Docs: si borras/renombras el script que declaraba una propiedad con override, el override queda huérfano (basura en la escena) — limpiar con el menú Overrides.

---

## 8. DontDestroyOnLoad: duplicados al volver a la escena inicial

**Síntoma:** dos AudioManagers sonando a la vez, dos GameManagers peleándose — tras volver al menú principal o recargar la escena 1.

**Causa:** el objeto marcado `DontDestroyOnLoad` sobrevive el cambio de escena, pero al RE-cargar la escena que lo contenía, se instancia una copia nueva. Además, docs: "Object.DontDestroyOnLoad only works for root GameObjects or components on root GameObjects".

**Fix (patrón guard, es el que muestra el propio ejemplo oficial):**

```csharp
static AudioManager instance;

void Awake()
{
    if (instance != null) { Destroy(gameObject); return; }
    instance = this;
    DontDestroyOnLoad(gameObject);   // el GO debe ser root
}
```

Alternativa más limpia: una escena "Boot" que carga los managers UNA vez y nunca se recarga; el resto de escenas se cargan aditivas o con `LoadScene` normal. [ver: arquitectura-unity]

---

## 9. Corrutinas: quién las mata y quién no

**Síntoma:** una corrutina sigue corriendo cuando "debería" haber muerto (o al revés); `MissingReferenceException` dentro de una corrutina tras un Destroy.

**Reglas exactas (docs Unity 6.2):**

| Acción | ¿Mata la corrutina? |
|---|---|
| `Destroy(gameObject)` o destruir el MonoBehaviour | SÍ |
| `SetActive(false)` en el GameObject | SÍ — y NO se reanuda al reactivar; hay que relanzarla |
| `enabled = false` en el script | **NO** — "Disabling the MonoBehaviour script by setting enabled to false doesn't stop coroutines" |
| `StopCoroutine` / `StopAllCoroutines` | SÍ (solo las de ese MonoBehaviour) |

Gotchas derivados:
- **El runner es el dueño.** `otherObject.StartCoroutine(MyRoutine())` corre en `otherObject`: sobrevive a la muerte del objeto que la lanzó, y muere si muere el runner. Corrutinas de larga vida (fades, transiciones de escena) → lanzarlas en un runner persistente (el manager con DontDestroyOnLoad), no en el enemigo que va a morir.
- Una corrutina puede sobrevivir a los objetos que USA: tras un `yield`, valida las referencias con `!= null` (el de Unity, sección 1) antes de tocarlas.
- `StopCoroutine(MyRoutine())` con string o creando un IEnumerator nuevo no para la instancia original — guardar el handle: `Coroutine c = StartCoroutine(...); StopCoroutine(c);`
- `yield return new WaitForSeconds(...)` en un loop aloca cada vez (es un objeto C#) → cachear: `static readonly WaitForSeconds Wait01 = new(0.1f);`
- Corrutinas corren en el main thread (docs) — no son threading; un cálculo pesado dentro bloquea el frame igual.

---

## 10. Floating point: == es una trampa

**Síntoma:** una condición `if (progress == 1.0f)` que nunca dispara; un contador que acumula error; física ligeramente distinta entre corridas.

**Causa:** Docs: "Floating point imprecision makes comparing floats using the equals operator inaccurate. For example, (1.0 == 10.0 / 10.0) might not return true every time."

**Fix:**
- Igualdad: `Mathf.Approximately(a, b)` (compara con epsilon) o umbral propio explícito: `Mathf.Abs(a - b) < 0.001f` cuando el epsilon de Approximately es demasiado fino para magnitudes de gameplay.
- Umbral de llegada, no igualdad: `if (Vector3.Distance(pos, target) < 0.01f)` — y mejor `(pos - target).sqrMagnitude < 0.0001f` (evita la raíz cuadrada).
- Acumulación: no sumar `deltaTime` a un float durante minutos para cronómetros críticos — usar `Time.time`/`Time.timeSinceLevelLoad` como referencia absoluta, o acumular en `double`.
- Posiciones lejos del origen (>10k unidades) pierden precisión → jitter visual/físico. Mundos grandes: floating origin. [ver: fisica-unity]

---

## 11. Escenas aditivas: la active scene manda

**Síntoma:** al cargar una escena aditiva, la iluminación/skybox/fog "se ven mal"; objetos instanciados aparecen en la escena equivocada y mueren al descargarla.

**Causa (docs oficiales):** la active scene es "the Scene which will be used as the target for new GameObjects instantiated by scripts" y de ella "the lighting settings are used". `LoadSceneMode.Additive` NO cambia la active scene. "There must always be one Scene marked as the active Scene", y "the active Scene has no impact on what Scenes are rendered" (todas las cargadas se renderizan).

**Fix:**
- Tras cargar el nivel aditivo: `SceneManager.SetActiveScene(scene)` — ojo, "Returns false if the Scene is not loaded yet" → hacerlo en el callback de `sceneLoaded` o tras esperar el `AsyncOperation`.
- Todo `Instantiate` cae en la active scene salvo que se mueva (`SceneManager.MoveGameObjectToScene`). Si el "loader" queda activo, tus enemigos nacen en la escena loader y NO se descargan con el nivel.
- Lighting bakeado multi-escena: bakear con el set de escenas cargado igual que en runtime (docs de multi-scene editing cubren bake conjunto de lightmaps/NavMesh/occlusion). [ver: rendering-urp]

---

## 12. Móvil: lo que el Editor no te enseña

| Síntoma | Causa (verificada en docs 6.2) | Fix |
|---|---|---|
| El juego va "capado" a 30 FPS en iOS/Android | Con `targetFrameRate = -1` (default): "Android and iOS: Content is rendered at fixed 30 fps to conserve battery power". Además "Mobile platforms always ignore QualitySettings.vSyncCount" | `Application.targetFrameRate = 60;` en el boot (o el refresh nativo). Decisión consciente: FPS vs batería/térmica |
| Pides 45 FPS y salen 30 | El valor se redondea HACIA ABAJO al divisor del refresh: "If the specified rate does not evenly divide the current refresh rate... rounded down" (ej. oficial: pedir 25 en pantalla de 60 Hz → 20) | Pedir divisores del refresh real: 30/60/120 |
| Touches en coordenadas locas tras rotar | Docs: "touch positions are rotated clockwise or counter-clockwise" al cambiar la orientación lógica | No cachear conversiones de pantalla a través de rotaciones; recalcular en el frame de uso |
| La app rota a orientaciones prohibidas | `Screen.orientation = AutoRotation` respeta los flags `Screen.autorotateToPortrait` etc. y los Player Settings | Fijar orientación en Player Settings; en runtime tocar los flags de autorotate, no solo `orientation` |
| Timers/estado corruptos al volver del background | El SO pausa la app. `OnApplicationPause(true)` llega al irse a background. Gotcha Android documentado: con el teclado en pantalla, Home NO dispara `OnApplicationFocus`, solo `OnApplicationPause`. Y al arrancar, `OnApplicationPause(false)` llega justo tras `Awake` | Guardar estado/partida en `OnApplicationPause(true)` (no confiar en OnApplicationQuit en móvil); recalcular timers con timestamps reales al volver, no con deltaTime acumulado |
| RenderTextures negras/corruptas al volver a la app | Docs: "render texture contents can become 'lost' on certain events, like loading a new level, system going to a screensaver mode, in and out of fullscreen"; la RT vuelve a estado "not yet created" | Chequear `rt.IsCreated()` al volver de pausa y regenerar el contenido (re-render), no asumir que persiste |

`OnApplicationPause`/`OnApplicationFocus` NO son simulables con fidelidad en Editor — probar en dispositivo real. [ver: build-plataformas] para el resto del pipeline móvil.

---

## Reglas practicas

1. Nunca `?.`, `??`, `??=`, `is null` sobre nada que derive de `UnityEngine.Object` — solo `== null` / `!= null` / `if (obj)`.
2. Tras `Destroy(x)`, asignar `x = null` si la variable sigue viva.
3. `Awake` = auto-init (mis GetComponent, mis datos). `Start` = todo lo que toca a otros scripts. Cross-refs en Awake = bug latente.
4. Singleton accedido por otros en init → lazy property o Script Execution Order explícito para el manager.
5. `GetComponent`, `GameObject.Find`, `Camera.main`, `FindFirstObjectByType`: jamás en `Update` — cachear en `Awake`/`Start`.
6. Tags → `CompareTag` (o `TagHandle` en Unity 6); params de Animator → `Animator.StringToHash` en `static readonly int`; cero strings mágicos repetidos.
7. Todo lo que se spawnea >1 vez/segundo (balas, VFX, enemigos, hit numbers) → `ObjectPool<T>`, con reset de estado en `actionOnGet`.
8. Presupuesto de GC en gameplay: 0 B/frame como objetivo; verificar con el Profiler, no a ojo.
9. Movimiento por frame × `Time.deltaTime`, siempre. Fuerzas y Rigidbody en `FixedUpdate`. Input en `Update` (bufferizado hacia FixedUpdate).
10. GameObject con Rigidbody dinámico: prohibido escribirle al `transform`; kinemático se mueve con `MovePosition`/`MoveRotation`.
11. Campos de Inspector: `[SerializeField] private`, nunca `public` solo por verlos.
12. Dictionary persistente → dos listas + `ISerializationCallbackReceiver` (sin llamar API de Unity dentro de los callbacks).
13. Salir de Play Mode = perder todos los tweaks; valores buenos → Copy Component / anotar ANTES de salir.
14. Tras tunear una instancia de prefab: Apply o Revert explícito; revisar el dropdown Overrides antes de commitear la escena; nunca "Apply All" a ciegas.
15. Prefab asset nunca referencia objetos de escena: resolver en runtime o desacoplar con ScriptableObject.
16. Todo objeto `DontDestroyOnLoad` lleva guard anti-duplicado en `Awake` (y debe ser root).
17. Corrutina de larga vida → lanzarla en un runner persistente; tras cada `yield`, revalidar referencias a objetos que pueden morir.
18. Nunca `==` entre floats: `Mathf.Approximately` o umbral explícito; distancias con `sqrMagnitude`.
19. Multi-escena: tras cargar aditivo, `SetActiveScene` (cuando ya cargó) — de ella salen lighting settings y ahí caen los `Instantiate`.
20. Primer script de un proyecto móvil: setear `Application.targetFrameRate` a un divisor del refresh; guardar estado en `OnApplicationPause(true)`; probar pausa/resume en dispositivo real.

## Errores comunes

- **"Lo chequeé con `?.` y explotó igual"** → `?.` no ve el fake null. Antídoto: regla 1; activar las inspecciones de Rider/ReSharper para Unity que lo marcan solas.
- **"Funciona en Editor, NullReference en build"** → orden de Awake/Start distinto entre Editor y build. Antídoto: disciplina Awake/Start + lazy init; no "arreglarlo" moviendo componentes en la jerarquía (orden no documentado = no contrato).
- **"Puse la física en Update porque se veía más suave"** → se ve suave a 120 FPS en tu máquina y se rompe a 45 en el teléfono. Antídoto: física en FixedUpdate + Interpolate en el Rigidbody visible.
- **"El juego stutterea cada ~10 s"** → GC por alocaciones por frame (Instantiate/Destroy, strings, LINQ). Antídoto: Profiler → GC.Alloc por frame → pooling y cachés; no subir el heap "para que pase menos".
- **"Configuré 50 valores probando y los perdí al salir de Play"** → Play Mode nunca persiste. Antídoto: regla 13; para tuning largo, ScriptableObjects de config (persisten ediciones en Editor incluso hechas en Play, porque son assets).
- **"Cambié el prefab y a la mitad de las instancias no les llegó"** → overrides accidentales pisando el asset. Antídoto: auditoría del dropdown Overrides; en equipo, revisar diffs de escena en el PR. [ver: assets-pipeline-git]
- **"Mi manager global se duplicó"** → volviste a cargar su escena de origen. Antídoto: guard de instancia + escena Boot que no se recarga.
- **"Paré la corrutina desactivando el script"** → `enabled = false` no las para. Antídoto: guardar el `Coroutine` handle y `StopCoroutine(handle)`, o `SetActive(false)` sabiendo que MATA (no pausa) todas las del objeto.
- **"El fade murió a mitad porque destruí al enemigo"** → la corrutina vivía en el enemigo. Antídoto: efectos que sobreviven a su causante corren en un runner persistente.
- **"En iOS va a 30 FPS y en Editor a 200"** → default móvil documentado. Antídoto: regla 20; perfilar SIEMPRE en dispositivo, el Editor no representa nada en móvil. [ver: rendimiento-unity]
- **"Volví del background y el minijuego de la RenderTexture salió negro"** → contexto gráfico perdido. Antídoto: `IsCreated()` + re-render al resumir.
- **"El agente/LLM inventó que Dictionary serializa con [Serializable]"** → no serializa, punto (docs 6.2). Antídoto: sección 6; cualquier duda de serialización se resuelve contra `script-serialization-rules` en docs, no contra tutoriales de 2019.

## Fuentes

Consultadas 2026-07 contra Unity 6.2 (6000.2):

- Order of execution for event functions — Unity Manual (docs.unity3d.com) — la garantía exacta de qué orden existe y cuál no entre scripts.
- MonoBehaviour.Awake — Unity Scripting Reference — Awake con script disabled, orden no determinista, guía Awake vs Start.
- UnityEngine.Object.operator == — Unity Scripting Reference — el operador custom chequea el puntero nativo (base del fake null).
- Avoid null comparisons against UnityEngine.Object subclasses — JetBrains resharper-unity wiki — por qué `??`/`?.` esquivan el operador y el costo del null-check de Unity.
- Serialization rules — Unity Manual — reglas exactas de qué serializa y qué no (Dictionary, propiedades, SerializeReference).
- ISerializationCallbackReceiver — Unity Scripting Reference — workaround oficial de Dictionary con dos listas + advertencia de threading del serializer.
- Prefab instance overrides — Unity Manual — precedencia de overrides, indicadores visuales, Apply/Revert, overrides huérfanos.
- Object.DontDestroyOnLoad — Unity Scripting Reference — restricción root-only y patrón anti-duplicados del ejemplo oficial.
- Coroutines — Unity Manual — qué mata una corrutina (SetActive sí, enabled=false no), main thread.
- Time.deltaTime — Unity Scripting Reference — deltaTime devuelve fixedDeltaTime dentro de FixedUpdate.
- MonoBehaviour.FixedUpdate — Unity Scripting Reference — 0.02 s default, 0..N llamadas por frame.
- Rigidbody / Rigidbody.MovePosition — Unity Scripting Reference — MovePosition para kinemáticos en FixedUpdate, interpolación, teleport con .position.
- Mathf.Approximately — Unity Scripting Reference — la trampa de == con floats (ejemplo oficial 1.0 == 10.0/10.0).
- GameObject.Find — Unity Scripting Reference — degradación a escala, sin caché, solo objetos activos.
- Camera.main — Unity Scripting Reference — caché interna en Unity 6 + overhead comparable a GetComponent.
- Component.CompareTag — Unity Scripting Reference — TagHandle reutilizable en Unity 6.
- Animator.StringToHash — Unity Scripting Reference — ids persistentes entre sesiones.
- Garbage collector overview — Unity Manual — cuándo corre el GC, ejemplo 1 KB/frame, objetivo 0 B/frame.
- Pool.ObjectPool<T> — Unity Scripting Reference — API completa del pool integrado (collectionCheck, maxSize destruye).
- Introduction to Object Pooling — Unity Learn — el patrón activar/desactivar en vez de Instantiate/Destroy.
- SceneManager.SetActiveScene — Unity Scripting Reference — la active scene define lighting settings y destino de Instantiate.
- Application.targetFrameRate — Unity Scripting Reference — 30 FPS default en iOS/Android, vSync ignorado en móvil, redondeo a divisores.
- Screen.orientation — Unity Scripting Reference — rotación de coordenadas touch, flags de autorotación.
- MonoBehaviour.OnApplicationPause — Unity Scripting Reference — gotcha del teclado Android, llamada tras Awake.
- RenderTexture — Unity Scripting Reference — pérdida de contenido de RTs y recuperación con IsCreated.
- Game view (Play Mode) — Unity Manual — cambios en Play Mode son temporales y se resetean.
