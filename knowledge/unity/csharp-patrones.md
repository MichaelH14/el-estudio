# Patrones C# para Unity

> **Cuando cargar este archivo:** al escribir o revisar cualquier script C# de gameplay/sistemas en Unity 6 — arquitectura con ScriptableObjects, eventos, corrutinas/async, pooling, state machines, singletons, null-checks de UnityEngine.Object, allocations en hot paths o caching de componentes.

## 1. ScriptableObjects como arquitectura (Ryan Hipple, Unite 2017)

Tres principios de la charla "Game Architecture with Scriptable Objects": **modular** (escenas que funcionan solas, sin managers globales), **editable** (el juego se ajusta con assets, sin recompilar), **debuggable** (cada pieza se prueba aislada en el Inspector).

Un ScriptableObject (SO) es un asset serializado que hereda de `UnityEngine.Object` y NO vive en un GameObject. Se crea con `[CreateAssetMenu]` + Assets > Create.

### Persistencia — la trampa clave

| Contexto | Cambios en runtime al SO |
|---|---|
| Editor, Play mode | **PERSISTEN al salir de Play** (el asset sigue cargado en memoria) — puede contaminar tus datos de diseño |
| Build | Viven solo en memoria; NUNCA se guardan a disco |
| Editor, cambios por script en Edit mode | Requieren `EditorUtility.SetDirty()` para guardarse |

Antídoto en Editor: tratar los SO de estado runtime como "reset on enable" (campo `initialValue` + `runtimeValue` que se resetea en `OnEnable`/al cargar escena), o clonar con `Instantiate(so)` al arrancar.

### Patrón 1 — Variables como assets

```csharp
[CreateAssetMenu(menuName = "Variables/Float")]
public class FloatVariable : ScriptableObject
{
    public float Value;
}
```

`PlayerHP` es un asset; la barra de vida de la UI y el player referencian el MISMO asset. Cero acoplamiento entre sistemas: la UI no conoce al player. Para diseñador: campos separados `[SerializeField] private FloatReference hp;` que permiten elegir constante o variable-asset (patrón `FloatReference` de la charla).

### Patrón 2 — Event channels (canales de eventos como assets)

Código real del repo de la charla (github.com/roboryantron/Unite2017), comprimido:

```csharp
[CreateAssetMenu]
public class GameEvent : ScriptableObject
{
    private readonly List<GameEventListener> listeners = new();
    public void Raise()
    {
        for (int i = listeners.Count - 1; i >= 0; i--)  // hacia atrás: un listener puede desregistrarse durante el Raise
            listeners[i].OnEventRaised();
    }
    public void RegisterListener(GameEventListener l)   { if (!listeners.Contains(l)) listeners.Add(l); }
    public void UnregisterListener(GameEventListener l) { listeners.Remove(l); }
}

public class GameEventListener : MonoBehaviour
{
    public GameEvent Event;
    public UnityEvent Response;                 // cableado por diseñador en Inspector
    void OnEnable()  => Event.RegisterListener(this);
    void OnDisable() => Event.UnregisterListener(this);
    public void OnEventRaised() => Response.Invoke();
}
```

Emisor hace `onPlayerDied.Raise()` sin saber quién escucha. Para eventos con payload: variante genérica `GameEvent<T>` con `UnityEvent<T>` (misma estructura). Úsalo para eventos de *juego* cross-sistema (muerte, pickup, cambio de fase); NO para comunicación intra-sistema de alta frecuencia (ahí, C# events — sección 2).

### Patrón 3 — Runtime sets

Sustituyen a `FindObjectsByType`/tags: un SO con la lista de instancias activas.

```csharp
[CreateAssetMenu]
public class EnemyRuntimeSet : ScriptableObject
{
    public List<Enemy> Items = new();
    public void Add(Enemy e)    { if (!Items.Contains(e)) Items.Add(e); }
    public void Remove(Enemy e) { Items.Remove(e); }
}
// En Enemy: OnEnable => set.Add(this); OnDisable => set.Remove(this);
```

Cualquier sistema (spawner, UI de minimapa, victoria) itera `set.Items` sin buscar en escena. Limpiar la lista al cargar escena si usas Editor (persistencia, ver arriba). [ver: arquitectura-unity]

## 2. Eventos: C# events vs Action vs UnityEvents

| | `event Action<T>` (C#) | `UnityEvent` |
|---|---|---|
| Invoke | Rápido, **0 GC** por invocación | 2.25x–40x más lento (benchmark Jackson Dunstan; viejo pero la dirección se mantiene: reflexión + persistent calls) |
| Cableado | Solo código (`+=`/`-=`) | Inspector (persistent listeners) + `AddListener` en runtime |
| Serialización | No | Sí — el diseñador conecta respuestas sin código |
| Args | Cualquier firma | `UnityEvent<T0..T3>` (máx. 4 argumentos tipados) |
| Riesgo | Olvidar `-=` → leak + callbacks a objetos destruidos | Referencias serializadas rotas fallan silenciosamente |

Criterio:
- **Hot path / alta frecuencia / interno de sistema** → `event Action` o delegado C#. Siempre desuscribir en `OnDisable`/`OnDestroy` lo suscrito en `OnEnable`/`Start`.
- **Punto de extensión para diseñador** (botón UI, trigger de nivel, respuesta a GameEvent) → `UnityEvent`. Es el estándar en UGUI. [ver: ui-unity]
- **Cross-sistema desacoplado** → event channel de SO (sección 1).
- `?.Invoke()` sobre un delegado C# es correcto (un delegado no es `UnityEngine.Object`; la prohibición de `?.` es solo para objetos Unity — sección 7).
- Desde Unity 6, un `UnityEvent` se puede `await` en métodos async (docs oficiales de `UnityEngine.Events.UnityEvent`).
- Declarar `public event Action X;` y no `public Action X;` — `event` impide que otros hagan `X = null` o invoquen desde fuera.

## 3. Corrutinas vs async/await vs Awaitable (Unity 6)

| | Corrutina (`IEnumerator`) | `async` + `Task` | `async` + `Awaitable` (Unity 6) |
|---|---|---|---|
| Ligada al objeto | Sí: para con `Destroy` y con `SetActive(false)` del GameObject. **`enabled = false` NO la para** | No — sigue tras Destroy y tras salir de Play mode en Editor | No automáticamente — cancelar con tokens |
| Devuelve valor | No | Sí | Sí (`Awaitable<T>`) |
| Allocations | Aloca por `StartCoroutine` y por cada `new WaitForSeconds(...)` (cachear yield instructions) | `Task` aloca en cada llamada | Instancias **pooled**, allocations mínimas |
| Hilo | Main thread siempre | ThreadPool posible | `BackgroundThreadAsync()` / `MainThreadAsync()` explícitos |

APIs estáticas de `Awaitable`: `NextFrameAsync()`, `EndOfFrameAsync()`, `FixedUpdateAsync()`, `WaitForSecondsAsync(float)`, `FromAsyncOperation()`, `BackgroundThreadAsync()`, `MainThreadAsync()` — todas aceptan `CancellationToken`.

### Reglas duras de Awaitable (docs oficiales 6000.x)

1. **NUNCA hacer `await` dos veces sobre la misma instancia de `Awaitable`** — están pooled; el reuso es "undefined behavior such as an exception or a deadlock". Si necesitas multi-await, usa `Task`/`ValueTask`.
2. Las continuaciones de `Awaitable` corren **sincrónicamente** al completarse (mismo frame), a diferencia de `Task`.
3. `Awaitable.Cancel()` lanza `System.OperationCanceledException` en quien lo espera.

### Cancelación y lifetime — el patrón correcto

Un método async NO muere con el MonoBehaviour. Sin token, sigue tocando un objeto destruido (→ `MissingReferenceException` o peor). Tokens nativos:

- `this.destroyCancellationToken` (MonoBehaviour) — se cancela al destruirse el componente. No accederlo después de destruido (la doc exige capturarlo antes).
- `Application.exitCancellationToken` — se cancela al salir de Play mode (Editor) o cerrar la app. Para lógica no ligada a un objeto.

```csharp
async Awaitable FlashAsync()
{
    try
    {
        var ct = destroyCancellationToken;          // capturar ANTES de cualquier await
        while (true)
        {
            sprite.enabled = !sprite.enabled;
            await Awaitable.WaitForSecondsAsync(0.2f, ct);
        }
    }
    catch (OperationCanceledException) { /* salida limpia esperada */ }
}
```

Criterio: **corrutina** para secuencias visuales simples atadas al objeto (su auto-stop es una feature); **Awaitable** cuando necesitas valor de retorno, composición, try/catch real o saltar a background thread; **Task** solo para interop con librerías .NET. Muchas corrutinas concurrentes ligeras siguen siendo competitivas — la ventaja de Awaitable "disminuye al correr muchas en paralelo" (docs). `async void` solo en event handlers de última milla: sus excepciones no son capturables por el caller.

## 4. Object pooling: `UnityEngine.Pool.ObjectPool<T>`

Nativo desde Unity 2021; en Unity 6 sin cambios de API. Para proyectiles, VFX, enemigos, hit-labels — todo lo que se instancia/destruye en ráfaga (Instantiate/Destroy generan GC y spikes).

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
        collectionCheck: true,      // detecta doble Release (dejar true en dev, false en release build)
        defaultCapacity: 32,
        maxSize: 256);              // Release con pool lleno => DESTRUYE la instancia (actionOnDestroy)
}
```

- El objeto pooled debe **auto-resetearse** en `actionOnGet`/`OnEnable` (velocidad, trail, HP): un pool devuelve objetos sucios.
- El objeto necesita una vía de volver al pool (callback o referencia al pool); nunca `Destroy` directo sobre un pooled.
- Mismo namespace: `ListPool<T>`, `DictionaryPool<K,V>`, `HashSetPool<T>`, `GenericPool<T>` para colecciones temporales (`using (ListPool<int>.Get(out var tmp)) { ... }`) — clave para hot paths (sección 8).
- Pre-calentar (`Get`+`Release` en bucle en una pantalla de carga) si el primer spike de spawns importa. [ver: rendimiento-unity]

## 5. State machines para gameplay

Escalera de complejidad (Nystrom, *Game Programming Patterns*):

1. **Enum + switch** — suficiente para 3-6 estados con poca data propia (puerta, pickup, fase de spawner). Todo en un archivo, fácil de leer. Se degrada cuando cada estado acumula lógica y datos.
2. **Clases-estado** — un objeto por estado con `Enter()/Exit()/Tick()`; el dueño delega. Úsalo para player controllers y AI con 5+ estados o transiciones con setup/teardown.

```csharp
public abstract class State
{
    protected readonly PlayerController player;
    protected State(PlayerController p) => player = p;
    public virtual void Enter() {}
    public virtual void Exit() {}
    public abstract void Tick();   // llamado desde Update del dueño
}

public class StateMachine
{
    public State Current { get; private set; }
    public void ChangeState(State next)
    {
        Current?.Exit();
        Current = next;
        Current.Enter();
    }
    public void Tick() => Current?.Tick();
}
```

3. **Estados como ScriptableObject** — cuando el *diseñador* debe componer comportamientos sin código (patrón "Pluggable AI" de Unity: SO-estados con listas de SO-acciones y SO-transiciones). Overkill para un player controller de un solo programador.

Extensiones cuando duela: jerárquicas (superestado "Grounded" comparte jump entre Idle/Run) y pushdown automata (stack: push Firing sobre Running, pop y vuelves) — ambas en el capítulo State de Nystrom. FSM aplica cuando el comportamiento se divide en opciones rígidas y pequeñas; para AI compleja evaluar behavior trees / utility. Las animaciones tienen su propia FSM en el Animator — no duplicar estados de gameplay ahí. [ver: animacion-unity]

## 6. Singletons y alternativas

Problemas (Nystrom): estado global ilegible, acoplamiento invisible (todo puede tocar todo), imposible de testear aislado, rígido si mañana necesitas 2 instancias. En Unity además: orden de inicialización entre escenas y duplicados al recargar.

Si aun así usas uno (aceptable para `AudioManager`/`GameManager` únicos de verdad):

```csharp
public class GameManager : MonoBehaviour
{
    public static GameManager Instance { get; private set; }
    void Awake()
    {
        if (Instance != null && Instance != this) { Destroy(gameObject); return; }
        Instance = this;
        DontDestroyOnLoad(gameObject);
    }
}
```

Alternativas, de menor a mayor maquinaria:
- **Referencias por ScriptableObject** (sección 1): sustituye al 80% de los singletons — el "global" es un asset asignado en el Inspector, testeable escena por escena.
- **Static class** sin estado de escena (matemática, settings puros): más simple y honesta que un singleton (Nystrom la prefiere).
- **Service locator**: registro central `Services.Get<IAudioService>()`; permite swap por mocks/null-services. Sigue siendo acceso global — documentar qué se registra y cuándo.
- **DI ligera** (VContainer, Extenject/Zenject): solo si el proyecto ya es grande y el equipo la conoce; para un juego pequeño-mediano es maquinaria de más.

Regla: primero pregunta si el sistema puede ser un asset SO o pasarse por referencia serializada; el singleton es el último recurso, no el default.

## 7. El "fake null" de Unity

`UnityEngine.Object` sobrecarga `==`/`!=`: además del null real de C#, chequea si el **objeto nativo del engine fue destruido**. Tras `Destroy(obj)`, la referencia C# sigue viva (fake null) pero `obj == null` devuelve `true`. Eso solo funciona con los operadores sobrecargados.

**`??`, `?.`, `is null`, `is not null` y `Object.ReferenceEquals` NO usan el operador custom** (el lenguaje C# no invoca operadores sobrecargados ahí) → sobre un objeto destruido dicen "no es null" y el siguiente acceso revienta. Los analizadores oficiales de Microsoft para Unity lo codifican como reglas: UNT0007 (no `??` con objetos Unity) y UNT0008 (no `?.`).

```csharp
Destroy(enemy);
// enemy == null            → true   ✓ (operador custom)
// enemy ?? backup          → devuelve enemy (destruido) ✗
// enemy?.transform         → NullReferenceException/MissingReferenceException después ✗
// enemy is null            → false ✗
if (enemy != null) { ... }  // ✓ forma correcta
if (enemy) { ... }          // ✓ conversión implícita a bool = "existe y no está destruido"
```

- La prohibición es SOLO para tipos que heredan de `UnityEngine.Object` (MonoBehaviour, Component, GameObject, ScriptableObject, Material...). En clases C# puras, delegados, strings: `?.`/`??` con libertad.
- Eventos: un objeto destruido suscrito a un `event Action` NO se vuelve null en la lista del delegado — por eso desuscribir en `OnDestroy`/`OnDisable` es obligatorio.
- Campo serializado sin asignar en Inspector ≠ null real: también es fake null comparable con `== null`.
- No guardes referencias a objetos destruidos "por si acaso": tras `Destroy`, poner tu campo a `null` real evita retener memoria managed.

## 8. Evitar allocations en hot paths (Update, colisiones por frame, loops de AI)

GC de Unity: Boehm–Demers–Weiser, **no generacional, no compactante** (existe modo incremental que trocea las pausas, no las elimina). Objetivo oficial: **0 bytes alocados por frame** en gameplay estable — 1 KB/frame a 60 fps son 3.6 MB/min de basura (cifras de docs 6000.x).

| Fuente de basura | Antídoto |
|---|---|
| Concatenar strings por frame (`"HP: " + hp`) | Solo actualizar el texto cuando el valor CAMBIA; separar label estático de valor dinámico; `StringBuilder` reusado para composiciones |
| `gameObject.tag == "Player"` | `CompareTag("Player")` — leer `.tag` aloca un string nuevo |
| LINQ en runtime (`Where`, `Select`, `ToList`) | Prohibido en hot paths (delegados + iteradores + boxing). Loop `for` explícito. LINQ OK en init/editor/tools |
| Boxing (value type → `object`, interfaces sobre structs) | Genéricos con constraints; el GC no generacional digiere especialmente mal esta basura pequeña y frecuente (docs) |
| Closures que capturan locales | La lambda que captura genera una clase → allocation. En hot paths: cachear el delegado en un campo, o pasar estado por parámetro |
| `foreach` sobre `IEnumerable<T>`/interfaz | Boxing del enumerator struct. `foreach` sobre `List<T>`/arrays/`Dictionary` concretos NO aloca (enumerator struct sin box) |
| APIs de Unity que devuelven arrays (`mesh.vertices`, `GetComponents<T>()`, `Physics.RaycastAll`) | Devuelven una COPIA por acceso → cachear fuera del loop; usar overloads con `List<T>` (`GetComponents(results)`) y `Physics.RaycastNonAlloc` / `OverlapSphereNonAlloc` con buffer pre-alocado |
| `new List<>`/`new WaitForSeconds`/`new Vector3[]` por frame | Reusar con `Clear()`; `ListPool<T>`; cachear yield instructions en campos |
| Instantiate/Destroy en ráfaga | `ObjectPool<T>` (sección 4) |

Verificación: Profiler > CPU > columna GC Alloc sobre el frame de gameplay real; cualquier valor estable ≠ 0 en tu código es un bug de rendimiento. [ver: rendimiento-unity] · [ver: gotchas-unity]

## 9. GetComponent y caching de referencias

- `GetComponent` en `Update`/hot path: prohibido. Cachear en `Awake` (no en `Start` si otros scripts lo usan desde su propio `Start`).

```csharp
Rigidbody rb;
Animator anim;
void Awake()
{
    rb = GetComponent<Rigidbody>();
    anim = GetComponentInChildren<Animator>();
}
```

- **`TryGetComponent<T>(out var c)`** para componentes opcionales: no aloca en el Editor cuando el componente falta (GetComponent sí genera basura en ese caso por el fake-null message) y deja el branch explícito. Preferir siempre la versión genérica de ambas APIs (evita `typeof` + cast).
- `GetComponentInChildren`/`InParent` recorren jerarquía: solo en init, jamás por frame.
- Referencias entre objetos: preferir `[SerializeField]` asignado en Inspector > buscar en runtime. `GameObject.Find`/`FindObjectsByType` solo en tooling/init puntual; para "todos los enemigos vivos" usa un runtime set (sección 1).
- `Camera.main`: cachearla en un campo en `Awake` igual que cualquier referencia; no llamarla por frame en código sensible.
- Componentes de otros GameObjects que pueden morir: revalidar con `if (cached != null)` (fake null, sección 7) antes de usar en callbacks tardíos.

## Reglas practicas

1. Datos compartidos entre sistemas → asset `ScriptableObject`, no singleton ni static.
2. En Editor, los cambios de Play mode a un SO persisten: separa `initialValue`/`runtimeValue` o clona al arrancar.
3. Evento cross-sistema cableable por diseñador → GameEvent (SO) + listener con `UnityEvent`; evento interno de alta frecuencia → `event Action` C#.
4. Todo `+=` a un evento tiene su `-=` espejo en `OnDisable`/`OnDestroy`. Sin excepciones.
5. `UnityEvent` máx. 4 args tipados (`UnityEvent<T0..T3>`); no usarlo en hot paths (2.25x–40x más lento que C# events).
6. Nunca `await` dos veces la misma instancia de `Awaitable` (pooled → undefined behavior).
7. Todo método async que toque un MonoBehaviour pasa `destroyCancellationToken` a cada espera y captura `OperationCanceledException`; lógica global usa `Application.exitCancellationToken`.
8. Corrutinas: paran con `Destroy` y `SetActive(false)` del GameObject, NO con `enabled = false`. Cachear `WaitForSeconds` en un campo.
9. Instantiate/Destroy repetitivos → `ObjectPool<T>` con `maxSize` calibrado; el objeto se resetea a sí mismo en `actionOnGet`.
10. Colecciones temporales en hot paths → `ListPool<T>`/`DictionaryPool<K,V>` o campo reusado con `Clear()`.
11. 3-6 estados simples → enum + switch; con setup/teardown o data por estado → clases con `Enter/Exit/Tick`; diseñador componiendo → estados-SO.
12. Comparar `UnityEngine.Object` SOLO con `== null`/`!= null` o `if (obj)`. `??`, `?.`, `is null` prohibidos con objetos Unity (UNT0007/UNT0008).
13. Presupuesto de GC en gameplay: 0 B/frame en tu código; verificar con la columna GC Alloc del Profiler, no a ojo.
14. `CompareTag` en vez de `.tag ==`; `RaycastNonAlloc`/overloads con `List<T>` en vez de APIs que devuelven arrays.
15. LINQ, closures que capturan, boxing y concatenación de strings: fuera de `Update`/física/loops por frame.
16. `GetComponent` solo en `Awake`; `TryGetComponent` para opcionales; referencias por `[SerializeField]` antes que `Find*`.
17. "Todos los X activos" → runtime set (SO + registro en `OnEnable`/`OnDisable`), no `FindObjectsByType` por frame.
18. `event Action`, no `Action` público: evita que otros asignen null o invoquen tu evento.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Tunear un SO jugando en el Editor y "perder" los valores originales | Los cambios SÍ se guardaron (esa es la trampa): usar patrón initial/runtime value o `Instantiate(so)`; git diff de los .asset antes de commitear |
| `enemy?.TakeDamage()` sobre un MonoBehaviour destruido no lanza y luego explota en otro lado | Nunca `?.`/`??` con tipos UnityEngine.Object; `if (enemy != null)` (operador custom) |
| Async method sigue corriendo tras `Destroy` o tras salir de Play mode y toca objetos muertos | `destroyCancellationToken`/`Application.exitCancellationToken` en CADA espera; try/catch `OperationCanceledException` |
| Guardar un `Awaitable` en un campo y esperarlo desde dos sitios | Está pooled: 1 instancia = 1 await. Refactor a `Task` si de verdad necesitas multi-await |
| Corrutina "fantasma" que sigue tras `enabled = false` | `enabled = false` no para corrutinas; parar explícito con `StopCoroutine` o desactivar el GameObject |
| Doble `Release` al pool → el mismo objeto entregado a dos usuarios | `collectionCheck: true` en dev lo detecta y lanza; flujo único de devolución (un solo dueño llama Release) |
| Bala pooled reaparece con el trail/velocidad de su vida anterior | Reset completo en `actionOnGet`/`OnEnable` del pooled: velocity, trails (`Clear()`), HP, timers |
| Suscribir en `OnEnable` un objeto que se destruye sin pasar por `OnDisable` limpio → listener muerto en un GameEvent | El par Register/Unregister de Hipple va en `OnEnable`/`OnDisable` SIEMPRE; el Raise itera hacia atrás para tolerar bajas durante el evento |
| UI que concatena `"Score: " + score` cada frame | Solo escribir el texto al cambiar el valor; separar label fijo de número |
| `foreach (var e in enemiesAsIEnumerable)` aloca cada frame | Tipar la colección concreta (`List<Enemy>`) o `for` con índice |
| `GetComponent` dentro de `OnTriggerStay`/`Update` | Cachear en `Awake`; en colisiones, `collision.collider.TryGetComponent` una vez y guardar si se repite |
| Singleton `Instance` null porque otra escena arrancó primero | Bootstrap scene con los managers + `DontDestroyOnLoad`, o migrar el dato a un SO que no depende de orden de escena |
| Animator como segunda state machine de gameplay desincronizada de la FSM de código | La FSM de código manda; el Animator solo refleja (`SetBool/SetTrigger` desde `Enter()` de cada estado) |

## Fuentes

- **Awaitable (API) + "Asynchronous programming with async, await y Awaitable"** — docs.unity3d.com 6000.x (Manual: async-await-support, async-awaitable-introduction, async-awaitable-examples; ScriptReference: Awaitable) — la autoridad sobre pooling de Awaitable (nunca await dos veces), continuaciones síncronas y métodos estáticos.
- **MonoBehaviour.destroyCancellationToken / Application.exitCancellationToken** — docs.unity3d.com 6000.x ScriptReference — los dos tokens nativos de cancelación y sus semánticas exactas.
- **Coroutines** — docs.unity3d.com 6000.x Manual — condiciones reales de parada de corrutinas (Destroy/SetActive sí, enabled=false no) y yield instructions.
- **ObjectPool<T0>** — docs.unity3d.com 6000.x ScriptReference (UnityEngine.Pool) — parámetros del constructor, comportamiento al superar maxSize (destruye), collectionCheck.
- **ScriptableObject** — docs.unity3d.com 6000.x Manual (class-ScriptableObject) — persistencia Editor vs build, CreateAssetMenu, SetDirty.
- **Object.operator ==** — docs.unity3d.com 6000.x ScriptReference — semántica exacta del fake null (chequeo del puntero nativo además de la referencia managed).
- **Garbage collector + GC best practices** — docs.unity3d.com (6000.x Manual performance-garbage-collector: objetivo 0 B/frame, cifra 1 KB/frame = 3.6 MB/min; Manual performance-incremental-garbage-collection: motor Boehm-Demers-Weiser, no compactante, modo incremental trocea pausas; best practices en Manual 2022.3, vigentes) — strings/boxing/closures/arrays-copia.
- **Events.UnityEvent** — docs.unity3d.com 6000.x ScriptReference — persistent vs runtime listeners; UnityEvent awaitable en Unity 6.
- **Component.TryGetComponent** — docs.unity3d.com 6000.x ScriptReference — no aloca en Editor cuando falta el componente.
- **Game Architecture with Scriptable Objects (Unite Austin 2017)** — Ryan Hipple (Schell Games); repo github.com/roboryantron/Unite2017 (código GameEvent/GameEventListener leído del fuente) — origen de variables-asset, event channels y runtime sets.
- **Event Performance: C# vs UnityEvent** — Jackson Dunstan (jacksondunstan.com/articles/3335) — benchmark 2.25x–40x; C# events 0 GC en invoke. Benchmark antiguo (Mono): tomar los ratios como orden de magnitud, no como cifras actuales.
- **Game Programming Patterns: Singleton y State** — Robert Nystrom (gameprogrammingpatterns.com) — crítica canónica al singleton y escalera enum → clases-estado → jerárquicas/pushdown.
- **Microsoft.Unity.Analyzers UNT0007/UNT0008** — Microsoft (github.com/microsoft/Microsoft.Unity.Analyzers) — reglas oficiales que prohíben `??` y `?.` con objetos Unity.
