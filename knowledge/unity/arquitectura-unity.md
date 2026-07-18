# Arquitectura de Unity

> **Cuando cargar este archivo:** al estructurar un proyecto Unity (jerarquía de escenas, prefabs, asmdefs), al escribir cualquier MonoBehaviour nuevo (ciclo de vida, orden de ejecución), o al depurar bugs de inicialización, serialización o estado que persiste entre sesiones de Play mode.

Verificado contra docs oficiales de Unity 6.x (docs.unity3d.com, versión 6.5 / 6000.5, julio 2026). Stack objetivo: Unity 6.x + URP.

---

## 1. El modelo de composición: GameObject / Component / Transform

- Un **GameObject** es un contenedor: no hace nada por sí solo. El comportamiento vive en **Components**. Un "tipo de objeto" = una combinación de components (cubo visible = MeshFilter + MeshRenderer + BoxCollider).
- **Transform** siempre existe y no se puede quitar. Define posición/rotación/escala y la jerarquía padre-hijo: los hijos heredan la transformación del padre.
- Un script C# que hereda de `MonoBehaviour` **es un component más**: se adjunta a un GameObject y expone campos serializados al Inspector.
- Filosofía: **composición sobre herencia**. No hagas `EnemigoVolador : Enemigo : Personaje`; haz components pequeños (`Health`, `Mover`, `AIBrain`) y combínalos. [ver: csharp-patrones]

### Estado activo

| API | Significado |
|---|---|
| `gameObject.activeSelf` | El flag propio del objeto |
| `gameObject.activeInHierarchy` | Activo él Y todos sus ancestros — el que importa para saber si "corre" |
| `behaviour.enabled` | El component individual, sin tocar el GameObject |
| `gameObject.SetActive(bool)` | Dispara OnEnable/OnDisable en todos los components del subárbol |

- Desactivar un GameObject apaga Update/render/física de todo su subárbol. `enabled = false` en un MonoBehaviour apaga sus callbacks de frame (Update, etc.) pero **Awake ya se llamó** si el GameObject estaba activo.

### Acceso a components — reglas

- `GetComponent<T>()` en caliente cada frame es un cache-miss evitable: **cachear en Awake**.
- `TryGetComponent<T>(out var x)` en vez de `GetComponent` + null-check (no aloca en el caso null en el Editor).
- `[RequireComponent(typeof(Rigidbody))]` en la clase garantiza la dependencia al añadir el script.
- Comparar tags con `CompareTag("Player")`, nunca `tag == "Player"` (aloca string y falla en silencio con typos).
- Jerarquías profundas con muchos Transforms que se mueven son caras (propagación de dirty flags): mantener la jerarquía plana cuando no hay razón lógica de parenting. [ver: rendimiento-unity]

```csharp
[RequireComponent(typeof(Rigidbody))]
public sealed class Mover : MonoBehaviour
{
    [SerializeField] float speed = 5f;
    Rigidbody rb;
    void Awake() => rb = GetComponent<Rigidbody>(); // cachear aquí, una vez
}
```

---

## 2. Prefabs

Un prefab es un GameObject completo (components + valores + hijos) guardado como asset reutilizable. Todo lo que se instancia más de una vez debe ser prefab — nunca duplicar objetos a mano en la escena.

### Los tres mecanismos

| Mecanismo | Qué es | Cuándo |
|---|---|---|
| **Nested prefab** | Instancia de un prefab dentro de otro prefab | Composición: la torreta (prefab) montada en el tanque (prefab) |
| **Prefab variant** | Prefab que hereda de un base y guarda solo diffs (overrides) | Familias: EnemigoBase → EnemigoRápido, EnemigoTanque. Cambio al base propaga a todos los variants |
| **Instance overrides** | Cambios locales de una instancia en escena sobre su asset | Ajustes puntuales por escena (este pilar es más alto) |

### Overrides — cómo funcionan (Unity 6.x)

- 4 tipos de override en instancia: **valor de propiedad**, **component añadido**, **component quitado**, **GameObject hijo añadido**.
- Un valor overrideado en la instancia **siempre gana** sobre el valor del asset: cambios posteriores al asset NO tocan esa propiedad en esa instancia. Fuente frecuente de "cambié el prefab y no pasó nada".
- Position/Rotation del Transform raíz (y Width/Height/Anchors/Pivot de RectTransform) NO cuentan como overrides — cada instancia tiene los suyos por diseño.
- En nested prefabs/variants, "Apply" pregunta el **target**: aplicar al asset del prefab anidado o al del raíz. Elegir mal contamina el prefab equivocado.
- En un variant, TODO lo que edites se guarda como override sobre el base; "Apply all to Prefab Variant parent" empuja los cambios al base (úsalo solo si de verdad quieres afectar a todos los variants).

### Flujo de trabajo correcto

1. Editar prefabs en **Prefab Mode** (abrir el asset), no acumulando overrides en una instancia de escena y aplicando después. Los overrides de instancia son para excepciones, no para editar.
2. Variants para variaciones de gameplay/arte; nested para composición estructural.
3. **Unpack** solo cuando el objeto deja de tener sentido como prefab (rompe el link, irreversible). "Unpack Completely" también desanida los nested.
4. Instanciar a runtime con `Object.Instantiate(prefab, pos, rot)` referenciando el prefab por campo serializado — nunca `Resources.Load` por string como práctica por defecto.
5. Los prefabs son YAML: revisar diffs en git antes de commitear "Apply All" masivos. [ver: assets-pipeline-git]

---

## 3. Scenes y carga aditiva

### Modos de carga

| Modo | Efecto | Uso |
|---|---|---|
| `LoadSceneMode.Single` | Descarga todo lo cargado y carga la nueva (llama `Resources.UnloadUnusedAssets`) | Cambio total de contexto: menú → partida |
| `LoadSceneMode.Additive` | Suma la escena a las ya cargadas | Streaming de mundo, separar capas (UI / gameplay / iluminación), escena bootstrap persistente |

- `SceneManager.LoadScene` NO carga inmediato: carga **al frame siguiente**, y fuerza a completar cualquier `AsyncOperation` pendiente (incluso con `allowSceneActivation = false`). Regla: **usar siempre `LoadSceneAsync`** salvo en scripts triviales de arranque.
- **Active scene**: donde caen los GameObjects nuevos (`Instantiate` sin padre) y de donde se toman los lighting settings a runtime. Con aditivas, setear explícito: `SceneManager.SetActiveScene(scene)`.
- Referencias serializadas **entre escenas distintas no están soportadas** — el Editor las bloquea. Entre escenas se cablea a runtime por código (evento, service locator, `RuntimeInitializeOnLoadMethod`). NO VERIFICADO en la página actual de docs 6.5 (la reestructuraron en hub), pero es comportamiento estable del Editor documentado históricamente y vigente.
- Patrón recomendado: escena **Bootstrap** (managers, audio, save system) que carga el resto aditivamente y nunca se descarga.

```csharp
IEnumerator LoadLevel(string name)
{
    var op = SceneManager.LoadSceneAsync(name, LoadSceneMode.Additive);
    op.allowSceneActivation = false;            // retener activación (op se queda en 0.9)
    while (op.progress < 0.9f) yield return null;
    op.allowSceneActivation = true;
    yield return op;
    SceneManager.SetActiveScene(SceneManager.GetSceneByName(name));
    yield return SceneManager.UnloadSceneAsync(previousScene);
}
```

- Baking de luces con multi-escena: se hornea con el set de escenas abierto juntas; los lightmaps quedan por escena. [ver: rendering-urp]

---

## 4. Ciclo de vida de MonoBehaviour

Orden dentro de un frame (docs Unity 6.5, "Order of execution for event functions"):

```
[carga de escena]
Awake → OnEnable                (por objeto, al activarse/instanciarse)
Start                           (antes del primer Update, solo si enabled)
[loop de física]  FixedUpdate → callbacks de física (0..N veces por frame)
[loop principal]  Update → yield null/coroutines → LateUpdate
[animación]       OnAnimatorMove / OnAnimatorIK
[render]          callbacks de cámara / OnRenderObject
[fin de frame]    WaitForEndOfFrame
OnDisable → OnDestroy → OnApplicationQuit
```

### Qué va en cada uno

| Callback | Para qué | Detalles críticos |
|---|---|---|
| `Awake` | Auto-inicialización: cachear components propios, setear estado interno | Se llama UNA vez por vida de la instancia. Se llama **aunque el component esté disabled** (si el GameObject está activo). GameObject inactivo → Awake NO corre hasta que se active. No puede ser corrutina |
| `OnEnable` | Suscribirse a eventos, registrarse en managers | Corre cada vez que se activa. Par simétrico con OnDisable (suscribir/desuscribir SIEMPRE en pareja) |
| `Start` | Inicialización que depende de OTROS objetos ya despiertos | Corre una vez, antes del primer Update, solo si enabled. Puede ser `IEnumerator` (corrutina) |
| `FixedUpdate` | Física: fuerzas, Rigidbody | Corre 0..N veces por frame a paso fijo (`Time.fixedDeltaTime`, default 0.02 s). NO usar `Time.deltaTime`-por-frame aquí (dentro de FixedUpdate, `Time.deltaTime` devuelve el fixed delta) [ver: fisica-unity] |
| `Update` | Lógica de juego por frame, input | Multiplicar magnitudes por `Time.deltaTime` |
| `LateUpdate` | Cámaras que siguen, ajustes post-movimiento/animación | Corre tras todos los Update del frame |
| `OnDisable` | Desuscribir eventos | También corre justo antes de OnDestroy |
| `OnDestroy` | Liberar recursos no gestionados | Solo se llama en objetos que llegaron a estar activos (tuvieron Awake) |

- **Callbacks de física** (`OnCollisionEnter`, `OnTriggerStay`...): corren en el paso interno de física; su posición depende de `Physics.simulationMode` (default `FixedUpdate`; existe `Update` y `Script` con `Physics.Simulate()` manual — Unity 2022.2+).
- **Regla de oro Awake/Start**: en Awake solo tocar lo PROPIO; en Start ya puedes hablar con otros scripts (todos los Awake de la escena ya corrieron). El orden de Awake **entre objetos distintos es no determinista** — jamás asumir que el Awake de A corre antes que el de B sin declararlo.
- **Corrutinas**: `yield return null` reanuda después de Update; `WaitForFixedUpdate` tras la física; `WaitForEndOfFrame` al final del frame. Las Tasks de .NET reanudan en la fase Update.

### Script Execution Order

- `Edit > Project Settings > Script Execution Order`, o `[DefaultExecutionOrder(-100)]` en la clase. Menor corre antes (−200 antes que −100 antes que Default antes que +50). Afecta el orden relativo de los callbacks entre scripts, **incluido Awake**.
- Uso típico: managers/singletons a −100 para que existan antes que sus consumidores. No abusar: si necesitas SEO en 20 scripts, el diseño de dependencias está mal (usa eventos o inicialización explícita).

### Domain reload y estado estático

- Al entrar a Play mode, el Editor por defecto hace **domain reload**: recarga el dominio C# y resetea todos los statics — simula un arranque limpio.
- Con **Enter Play Mode Settings** (domain reload OFF) la entrada a Play es mucho más rápida, pero: **las variables estáticas y los suscriptores de eventos estáticos PERSISTEN entre sesiones de Play**. Bug clásico: handlers duplicados, contadores que no vuelven a cero.
- Antídoto oficial (runtime): resetear en `[RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]`. En Editor-only: `[InitializeOnEnterPlayMode]`. Verificado en docs 6.5 (Domain Reloading, Manual): existen además `[AutoStaticsCleanup]` (reset automático por code generation al entrar a Play mode) y su contraparte `[NoAutoStaticsCleanup]` para excluir un campo puntual del reset automático, más `[OnEnteringPlayMode]`/`[OnExitingPlayMode]` para reset manual — confirmar que el proyecto está en una versión de Unity 6.x que ya los trae antes de depender de ellos como único mecanismo.

```csharp
public static class GameEvents
{
    public static event Action<int> OnScore;

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
    static void ResetStatics() => OnScore = null;   // domain reload OFF: sin esto, se acumulan handlers
}
```

---

## 5. Assemblies y asmdef

- Sin asmdefs, todo tu código compila en **Assembly-CSharp**: cualquier cambio en cualquier script recompila TODO el proyecto. Un `.asmdef` en una carpeta crea un assembly propio con esa carpeta y subcarpetas; solo se recompila un assembly cuando cambia su código o el de sus dependencias.
- Beneficios: iteración más rápida en proyectos medianos/grandes, dependencias explícitas (un assembly solo ve lo que referencia — imposible acoplar por accidente), separación limpia de código Editor.

### Cómo partir (recomendación práctica)

| Assembly | Contenido | Referencias |
|---|---|---|
| `Game.Core` | Tipos puros, datos, utilidades sin dependencias de gameplay | — |
| `Game.Gameplay` | Mecánicas, MonoBehaviours del juego | Core |
| `Game.UI` | Pantallas, HUD | Core (idealmente NO Gameplay directo: comunicar por eventos) |
| `Game.Editor` | Tooling, inspectores custom | los que necesite; **Platforms = Editor only** |
| `Game.Tests` | Tests | + asmdefs de test framework |

- Empezar con 3–5 assemblies. **Advertencia oficial**: demasiados assemblies pequeños AÑADEN overhead de compilación y de carga — no hacer un asmdef por carpeta.
- No se permiten referencias circulares entre assemblies. Si Gameplay necesita llamar a UI y UI a Gameplay → extraer interfaces/eventos a Core.
- Código Editor-only: assembly aparte restringido a plataforma Editor (o carpeta `Editor/` clásica si no usas asmdefs). Código editor dentro de un assembly de runtime rompe el build de plataforma.
- **Auto Referenced**: si está ON (default), Assembly-CSharp lo referencia automático. Apagarlo en librerías que no quieres expuestas al código suelto.
- **asmref** (Assembly Definition Reference): mete una carpeta en un assembly YA existente definido en otro lado (p. ej. extender el assembly de un package).
- Define Constraints / Version Defines: compilar el assembly solo si existe cierto símbolo o cierta versión de un package (útil para integraciones opcionales).
- Cambiar un script dispara recompilación + **domain reload** en el Editor (segundos de espera): el tamaño del assembly tocado determina el costo. Los asmdefs reducen la parte de compilación, no el reload en sí.

---

## 6. Serialización de Unity

Es lo que alimenta: Inspector, prefabs, escenas, ScriptableObjects, `Instantiate` (clona vía serialización) y el hot reload del Editor.

### Qué serializa un campo (reglas exactas, docs 6.5)

Se serializa si cumple TODO:
1. Es `public` **o** tiene `[SerializeField]`.
2. NO es `static`, `const` ni `readonly`.
3. Su tipo es serializable:
   - primitivos, `string`, enums (de 32 bits o menos);
   - tipos de Unity (`Vector3`, `Color`, `AnimationCurve`, `LayerMask`...);
   - referencias a tipos derivados de `UnityEngine.Object` (GameObject, Component, ScriptableObject, Material...) — se guardan como referencia al asset/objeto, no inline;
   - structs/clases custom con `[System.Serializable]` — se guardan **inline, por valor**;
   - `T[]` y `List<T>` de cualquiera de los anteriores.

### Qué NO serializa

| No soportado | Workaround |
|---|---|
| `Dictionary<K,V>` | Dos listas paralelas + `ISerializationCallbackReceiver` (reconstruir el dict en `OnAfterDeserialize`) |
| Arrays multidimensionales / jagged (`int[,]`, `int[][]`) | Clase wrapper `[Serializable]` con el array interno, y lista de wrappers |
| Contenedores anidados (`List<List<T>>`) | Igual: wrapper intermedio |
| Properties | Solo campos. Auto-property: `[field: SerializeField] public int HP { get; private set; }` |
| Polimorfismo en clases inline | `[SerializeReference]` (abajo) |

- Clases custom inline: **no hay null** — Unity crea instancias vacías al deserializar. Y si varios campos apuntan a la misma instancia, al serializar se convierten en **copias separadas** (pierdes identidad compartida).
- Ciclos indirectos en tipos inline: Unity corta a **10 niveles de recursión** y descarta el resto — un tipo autorreferencial inline infla el asset exponencialmente. Para grafos: `SerializeReference`.

### [SerializeReference]

- Serializa el campo **por referencia** dentro del mismo host object: soporta **polimorfismo** (una `List<IAbility>` con implementaciones distintas conserva el tipo concreto y sus campos), **null real** e **identidad compartida** entre campos del mismo host.
- Límites: el tipo referenciado NO puede derivar de `UnityEngine.Object` (para esos ya existe la referencia normal); las referencias no cruzan de un host object a otro; cuesta más en storage, memoria y tiempos de load/save que el inline por valor. Usarlo cuando hace falta (árboles, grafos, configs polimórficas), no por defecto.

```csharp
[Serializable] public abstract class Ability { public float cooldown; }
[Serializable] public class Dash : Ability { public float distance; }
[Serializable] public class Shield : Ability { public float duration; }

public class Player : MonoBehaviour
{
    [SerializeReference] List<Ability> abilities = new();  // conserva Dash vs Shield
}
```

- Hot reload (recompilar con el Editor abierto): Unity serializa todo, recarga el dominio y deserializa. **Todo campo no serializable vuelve a su default** (se pierden dictionaries, delegates, referencias cacheadas no serializadas). Diseñar los MonoBehaviours para poder reconstruir ese estado.
- Renombrar un campo serializado pierde los datos guardados: usar `[FormerlySerializedAs("oldName")]` (namespace `UnityEngine.Serialization`) durante la transición.

---

## 7. PlayerLoop (conceptual)

- El PlayerLoop es la lista real de subsistemas que Unity ejecuta cada frame. Los callbacks de MonoBehaviour son hooks colgados de sus fases. Fases principales (API `UnityEngine.LowLevel`):

```
Initialization → EarlyUpdate → FixedUpdate (loop física) → PreUpdate
→ Update (scripts Update + corrutinas) → PreLateUpdate (LateUpdate)
→ PostLateUpdate (render, WaitForEndOfFrame) → TimeUpdate
```

- API: `PlayerLoop.GetCurrentPlayerLoop()` devuelve el árbol de `PlayerLoopSystem` (cada nodo: `type`, `updateDelegate`, `subSystemList`); modificas el árbol y lo aplicas con `PlayerLoop.SetPlayerLoop()`. `GetDefaultPlayerLoop()` da el original sin modificar.
- Para qué sirve en la práctica:
  - **Managers sin MonoBehaviour**: un sistema custom insertado en Update que itera N objetos plain-C# es más barato y controlable que N `Update()` mágicos.
  - Insertar lógica en fases sin callback público (EarlyUpdate para input propio, PostLateUpdate para captura).
  - Es como UniTask corre async/await sin threads: inyecta sistemas en cada fase (`PlayerLoopTiming.Update`, `.PostLateUpdate`, etc.).

```csharp
static void InsertSystem()
{
    var loop = PlayerLoop.GetCurrentPlayerLoop();
    var mySystem = new PlayerLoopSystem {
        type = typeof(MyManagers), updateDelegate = MyManagers.Tick
    };
    // localizar la fase Update y añadir mySystem a su subSystemList (copiar array + append)
    // ...
    PlayerLoop.SetPlayerLoop(loop);
}
```

- Caveats: registrar la inserción en `[RuntimeInitializeOnLoadMethod]`; con domain reload activo la modificación se pierde en cada reload (hay que re-registrar), con domain reload OFF persiste entre sesiones de Play — otra razón para inicialización idempotente. Modificar el loop mal (perder subsistemas al reconstruir arrays) rompe el frame entero: siempre partir de `GetCurrentPlayerLoop` y preservar lo existente.

---

## Reglas practicas

1. Composición: components pequeños de responsabilidad única; nada de árboles de herencia de gameplay.
2. Cachear `GetComponent` en Awake; `TryGetComponent` para chequeos; `CompareTag` en vez de `==`.
3. Awake = estado propio; Start = hablar con otros; OnEnable/OnDisable = par simétrico suscribir/desuscribir.
4. Jamás depender del orden de Awake/Update entre objetos sin `[DefaultExecutionOrder]` o Script Execution Order explícito.
5. Física solo en FixedUpdate; input y lógica por frame en Update; cámaras en LateUpdate.
6. Todo objeto repetido es prefab; editar en Prefab Mode; overrides de instancia solo para excepciones puntuales.
7. Variants para familias (base + diffs); nested para composición; Unpack solo si se abandona el prefab.
8. Al hacer Apply en nested/variants, verificar el TARGET del apply antes de confirmar.
9. `LoadSceneAsync` siempre; con aditivas, `SetActiveScene` explícito y descargar con `UnloadSceneAsync`.
10. Escena Bootstrap persistente para managers; gameplay/UI/entorno en escenas aditivas si el proyecto crece.
11. Nada de referencias serializadas entre escenas: cablear a runtime por eventos o registro.
12. 3–5 asmdefs al empezar (Core/Gameplay/UI/Editor/Tests); código Editor SIEMPRE en assembly Editor-only.
13. Campos privados + `[SerializeField]` por defecto; `public` solo si otra clase lo necesita de verdad.
14. `[FormerlySerializedAs]` al renombrar campos serializados; nunca renombrar y aplicar sin él.
15. `[SerializeReference]` solo para polimorfismo/grafos/null real; el resto, inline por valor.
16. Dictionary no serializa: listas paralelas + `ISerializationCallbackReceiver`.
17. Todo static mutable con reset en `[RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]` — obligatorio si Enter Play Mode Options desactiva domain reload.
18. Un manager con un solo Update (o sistema de PlayerLoop) que ticka N objetos > N MonoBehaviours con Update propio, cuando N es grande.
19. Verificar cambios de escena/prefab en el estado serializado real (el .unity/.prefab en git), no solo en el Inspector. [ver: assets-pipeline-git]

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| NullReference en Awake porque otro objeto "aún no existe" | Mover la dependencia externa a Start, o fijar orden con `[DefaultExecutionOrder]` |
| Awake no corre y "el objeto no se inicializa" | El GameObject estaba inactivo en escena: Awake corre al primer SetActive(true), no al cargar |
| Component disabled pero su Awake corrió igual | Es lo documentado: disabled solo bloquea Start/Update/callbacks de frame, no Awake |
| Eventos que se disparan N veces tras varios Play | Domain reload OFF + statics sin reset: limpiar en `SubsystemRegistration`; desuscribir en OnDisable |
| "Cambié el prefab y la instancia no cambió" | Esa propiedad tiene override de instancia (gana siempre): Revert en la instancia |
| Apply All contaminó el prefab base desde un variant | Apply selectivo mirando el target; en variants, el apply va al parent del variant |
| Movimiento a tirones con física | Lógica en Update en vez de FixedUpdate, o cámara en Update en vez de LateUpdate; interpolar Rigidbody [ver: fisica-unity] |
| Freeze al cambiar de escena | `LoadScene` síncrono con escenas pesadas; además fuerza a completar los async pendientes → `LoadSceneAsync` |
| Objetos instanciados caen en la escena equivocada | Con carga aditiva no se seteo `SetActiveScene`; Instantiate cae en la active scene |
| Recompilar tarda una eternidad en proyecto grande | Todo en Assembly-CSharp: partir con asmdefs; pero no crear decenas de micro-assemblies (overhead inverso) |
| Build de plataforma falla por `UnityEditor` | Código editor fuera de assembly/carpeta Editor: moverlo y aislarlo con asmdef Editor-only |
| Datos del Inspector desaparecen tras renombrar campo | Renombre sin `[FormerlySerializedAs]`: los datos serializados van por nombre de campo |
| `List<Ability>` pierde los tipos derivados al guardar | Serialización inline no soporta polimorfismo: `[SerializeReference]` |
| Dictionary configurado en código se vacía "solo" en el Editor | Hot reload: no es serializable, se pierde en cada domain reload; reconstruir en `OnAfterDeserialize`/Awake |
| Asset gigante o datos truncados con clases autorreferenciales | Inline corta a 10 niveles de recursión: usar `[SerializeReference]` para grafos |
| Referencia entre dos escenas que "se rompe sola" | Cross-scene references no soportadas: resolver a runtime |

## Fuentes

- Order of execution for event functions — Unity Manual 6.5 (docs.unity3d.com/Manual/execution-order.html) — orden exacto del ciclo de vida, física según `Physics.simulationMode`, timing de corrutinas.
- MonoBehaviour.Awake — Unity Scripting Reference 6.5 — semántica exacta de Awake (disabled, una vez por vida, orden no determinista entre objetos).
- Script Execution Order settings — Unity Manual 6.5 (class-MonoManager.html) — SEO afecta Awake; valores negativos primero; `[DefaultExecutionOrder]`.
- Prefabs — Unity Manual 6.5 — modelo general: nested, variants, prefab mode, unpack.
- Prefab Variants — Unity Manual 6.5 — herencia base→variant, precedencia de overrides, apply al parent.
- Instance Overrides — Unity Manual 6.5 — los 4 tipos de override, precedencia absoluta, targets de apply en nested, Transform/RectTransform excluidos.
- Multi-Scene editing — Unity Manual 6.5/6000.0 — casos de uso de aditivas, baking multi-escena, active scene.
- SceneManager.LoadScene — Unity Scripting Reference 6.5 — carga al frame siguiente, fuerza async pendientes, Single llama UnloadUnusedAssets.
- SceneManager.SetActiveScene — Unity Scripting Reference 6.5 — cita textual verificada: la active scene es el target de `Instantiate` sin padre y "de qué escena se toman los lighting settings" a runtime.
- Assembly definition files — Unity Manual 6.5 — propósito, Assembly-CSharp default, asmref, auto-referenced, overhead de demasiados assemblies.
- Script serialization + Serialization rules — Unity Manual 6.5 — reglas exactas de campos, tipos soportados/no soportados, límite de 10 niveles, properties.
- SerializeReference — Unity Scripting Reference 6.5 — polimorfismo, null, identidad compartida, límites (no UnityEngine.Object, overhead).
- Domain Reloading — Unity Manual 6000.0 y 6.5 — statics/eventos persisten con reload OFF; atributos exactos de reset.
- PlayerLoop — Unity Scripting Reference 6.5 (UnityEngine.LowLevel) — Get/SetPlayerLoop, estructura PlayerLoopSystem, inserción de sistemas.
- GameObjects — Unity Manual 6.5 — modelo contenedor + components, Transform obligatorio.
- Game Objects and Scripts — Jasper Flick, Catlike Coding — fundamentos de composición y scripts-como-components (tutorial pre-Unity-6; los conceptos verificados vigentes contra docs 6.5).
- UniTask README — Cysharp (github.com/Cysharp/UniTask) — uso real del PlayerLoop: fases expuestas e inyección de sistemas custom.

[ver: csharp-patrones] · [ver: fisica-unity] · [ver: rendimiento-unity] · [ver: gotchas-unity] · [ver: unity6-actualidad] · [ver: assets-pipeline-git] · [ver: unity-mcp-flujo]
