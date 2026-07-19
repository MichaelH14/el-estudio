# Estructura de proyecto y productividad en el editor

> **Cuando cargar este archivo:** al crear un proyecto Unity nuevo desde cero (día 0: carpetas, escenas, git, asmdefs), al decidir qué vive en cada escena, o antes de escribir tooling de editor (gizmos, inspectores custom, menu items, configs en ScriptableObject).

Archivo puente: une el proceso de [ver: gamedev/preproduccion] y [ver: gamedev/produccion-proceso] con la técnica de [ver: unity/arquitectura-unity] y [ver: unity/assets-pipeline-git]. Aquí está la plantilla concreta que este estudio usa en todo proyecto y el tooling de editor que la base de Unity no cubre. Verificado contra docs Unity 6.2 (6000.2), julio 2026.

---

## 1. Plantilla canónica de proyecto

### Día 0 — commit 0 (antes del primer asset)

1. `Edit > Project Settings > Editor`: **Asset Serialization = Force Text** y **Visible Meta Files** (ambos default en Unity 6 — verificar solo en proyectos migrados). Line endings de scripts: LF.
2. `git init && git lfs install` — LFS ANTES del primer binario (un binario commiteado sin LFS queda en la historia para siempre).
3. `.gitignore` y `.gitattributes`: usar los canónicos completos de [ver: unity/assets-pipeline-git] §5. Versión mínima operativa si hay prisa (ampliar después NO exime de la completa):

```gitignore
[Ll]ibrary/
[Tt]emp/
[Oo]bj/
[Bb]uild*/
[Ll]ogs/
[Uu]ser[Ss]ettings/
*.csproj
*.sln
.DS_Store
*.apk
*.aab
*.app
```

```gitattributes
*.unity   merge=unityyamlmerge eol=lf
*.prefab  merge=unityyamlmerge eol=lf
*.asset   merge=unityyamlmerge eol=lf
*.cs      eol=lf
*.png filter=lfs diff=lfs merge=lfs -text
*.psd filter=lfs diff=lfs merge=lfs -text
*.wav filter=lfs diff=lfs merge=lfs -text
*.ogg filter=lfs diff=lfs merge=lfs -text
*.fbx filter=lfs diff=lfs merge=lfs -text
*.ttf filter=lfs diff=lfs merge=lfs -text
```

4. SÍ se commitean: `Assets/` (con todos los `.meta`), `ProjectSettings/`, `Packages/manifest.json` + `packages-lock.json`. Jamás `Library/`.

### Carpetas

Estructura por feature bajo una raíz propia (detalle y razones en [ver: unity/assets-pipeline-git] §4):

```
Assets/
  _Game/
    Art/  Audio/  Data/  Prefabs/  Scenes/  UI/
    Code/
      Runtime/   (Game.Core, Game.Gameplay, Game.UI)
      Editor/    (Game.Editor — asmdef Editor-only)
      Tests/     (Game.Tests)
  Plugins/  ThirdParty/  Settings/
```

- `Settings/` guarda URP Assets, Presets de import, Input Actions.
- Nunca carpetas vacías (churn de `.meta` huérfanos); nunca editar dentro de `ThirdParty/`.

### asmdefs

Cinco assemblies al arrancar — `Game.Core` (tipos puros) ← `Game.Gameplay` ← `Game.UI` (UI NO referencia Gameplay directo: eventos), `Game.Editor` (Platforms = Editor only), `Game.Tests`. Ni uno más al inicio: demasiados micro-assemblies añaden overhead. Reglas exactas y asmref en [ver: unity/arquitectura-unity] §5.

### Naming conventions (convención del estudio)

Basada en el Unity Style Guide de justinwasilenko: `Prefijo_Nombre_Variante`, PascalCase, variantes numeradas `_01`.

| Tipo | Convención | Ejemplo |
|---|---|---|
| Escena | Sin prefijo; sufijo por rol | `Boot`, `MainMenu`, `Level01_Gameplay`, `Level01_Env` |
| Prefab | PascalCase sin prefijo | `PlayerCharacter`, `Enemy_Grunt_01` |
| ScriptableObject (data) | `QuéEs_DeQuién` | `GameConfig`, `EnemyStats_Grunt`, `WaveSet_Level01` |
| Textura | `T_` + sufijo de canal | `T_Rock_BC`, `T_Rock_N`, `T_Button_GUI` |
| Material | `M_` | `M_Rock` |
| Static mesh / skeletal | `SM_` / `SK_` | `SM_Tree_01`, `SK_Hero` |
| Animation clip / controller | `A_` / `AC_` | `A_Run`, `AC_Hero` |
| Audio clip / mixer | `A_` (carpeta lo desambigua) / `MIX_` | `SFX/A_Footstep_01`, `MIX_Master` |
| Partículas / VFX | `PS_` / `VFX_` | `PS_Explosion` |
| Script | = nombre de la clase, 1 clase pública por archivo | `HealthSystem.cs` |
| Campo privado serializado | camelCase + `[SerializeField]` | `[SerializeField] float moveSpeed;` |

Regla dura: sin espacios ni caracteres especiales en paths; la convención se decide el día 0 y NO se renombra masivamente después (cada rename toca GUIDs y diffs).

### Prefab workflow (compresión de [ver: unity/arquitectura-unity] §2)

- Todo lo que aparece más de una vez es prefab. La escena solo contiene **instancias** (posición/rotación); el contenido se edita en **Prefab Mode**, nunca acumulando overrides de instancia.
- Variants para familias (`Enemy_Base` → `Enemy_Fast`); nested para composición (torreta dentro de tanque).
- Referencias a prefabs por campo serializado; cero `Resources.Load`.
- Beneficio de repo: el diff cae en el `.prefab` (archivo chico), no en la `.unity` (archivo gigante) — es la estrategia nº1 anti-conflictos de [ver: unity/assets-pipeline-git] §6.

---

## 2. Composición de escenas

### Las escenas del template

| Escena | Qué vive ahí | Ciclo de vida |
|---|---|---|
| `Boot` | Managers persistentes (tabla abajo) + un `SceneLoader`. Sin cámara de gameplay, sin arte | Escena 0 de la Scene List. Se carga una vez, NUNCA se descarga |
| `UI_Global` | Overlay de fade/loading, popups del sistema, toasts | Cargada aditiva por Boot; persistente |
| `MainMenu` | Menú completo con su UI y su cámara | Single-purpose; se descarga al empezar partida |
| `LevelXX_Gameplay` | Jugador, enemigos, spawners, triggers, lógica del nivel | Aditiva; **active scene** durante la partida |
| `LevelXX_Env` | Geometría estática, props, iluminación del nivel | Aditiva, en paralelo con Gameplay |

- Proyecto chico (jam, prototipo): `Boot` + una escena por pantalla basta; el split Gameplay/Env se introduce cuando la escena pasa de ~1–2k objetos o hay conflictos de merge.
- Regla de particionado: una escena = una responsabilidad = un dueño por branch.

### Managers: persistentes vs por-escena

| Persistentes (viven en `Boot`) | Por-escena (viven en su escena) |
|---|---|
| `GameManager` (estado de sesión, flujo de pantallas) | `LevelManager` (objetivos, win/lose del nivel) |
| `SceneLoader` (única API para cambiar de escena) | Spawners, triggers, puzzle logic |
| `AudioManager` (mixer, música) [ver: unity/audio-unity] | Cámara/Cinemachine rig del nivel |
| `SaveSystem`, `InputReader` | HUD del nivel (si no está en UI_Global) |

- Con escena `Boot` persistente **no hace falta `DontDestroyOnLoad`** — evita la familia entera de bugs de duplicados DDOL ([ver: unity/gotchas-unity]).
- Managers como plain C# + ScriptableObjects donde se pueda; singleton MonoBehaviour solo si necesita ciclo de vida de frame ([ver: unity/csharp-patrones] §5).

### Orden de carga

1. `Boot` (índice 0 en Build Profiles > Scene List) → sus managers hacen `Awake/Start`.
2. `SceneLoader` carga `UI_Global` y `MainMenu` con `LoadSceneAsync(..., LoadSceneMode.Additive)`.
3. Al darle Play a una partida: descarga `MainMenu`, carga `LevelXX_Gameplay` + `LevelXX_Env`, y `SceneManager.SetActiveScene(gameplay)` — la active scene decide dónde caen los `Instantiate` sin padre y de qué escena salen los lighting settings.
4. Cambio de nivel: descargar las dos del nivel viejo (`UnloadSceneAsync`), cargar las dos nuevas. Nunca `LoadScene` síncrono ([ver: unity/arquitectura-unity] §3).

Dependencias entre escenas: las referencias serializadas cross-scene no existen — todo cableado entre escenas pasa por los managers de Boot, eventos o ScriptableObjects compartidos.

### Bootstrapper: darle Play a CUALQUIER escena

Patrón comunitario estándar sobre API documentada (`RuntimeInitializeOnLoadMethod`): sin esto, probar `Level03_Gameplay` exige pasar por Boot → menú → nivel cada vez.

```csharp
// Runtime/Boot/Bootstrapper.cs
using UnityEngine;
using UnityEngine.SceneManagement;

public static class Bootstrapper
{
    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
    static void EnsureBootScene()
    {
        for (int i = 0; i < SceneManager.sceneCount; i++)
            if (SceneManager.GetSceneAt(i).name == "Boot") return;
        SceneManager.LoadScene("Boot", LoadSceneMode.Additive);
    }
}
```

Requisitos: `Boot` en la Scene List del build, y managers **idempotentes** (si ya existen, no duplicarse). Con Enter Play Mode Options sin domain reload, los statics además necesitan reset explícito ([ver: unity/arquitectura-unity] §4).

---

## 3. Editor scripting de productividad

Todo el código de esta sección vive en `Code/Editor/` (assembly `Game.Editor`, Editor-only) — salvo `OnDrawGizmos*`, que va en el MonoBehaviour de runtime.

### 3.1 Gizmos y Handles — debug visual en Scene view

`OnDrawGizmos()` se llama en cada repaint del Scene view; `OnDrawGizmosSelected()` solo con el objeto seleccionado (preferirlo: menos ruido). Editor-only: no ejecutan en builds. API `Gizmos` (docs 6.2): `DrawLine`, `DrawRay`, `DrawWireSphere`, `DrawWireCube`, `DrawSphere`, `DrawCube`, `DrawIcon`, `DrawMesh`, `DrawFrustum`; estado con `Gizmos.color` y `Gizmos.matrix` (para dibujar en espacio local).

```csharp
// En el MonoBehaviour de runtime (Game.Gameplay)
void OnDrawGizmosSelected()
{
    Gizmos.color = Color.yellow;
    Gizmos.DrawWireSphere(transform.position, detectionRadius);
    Gizmos.color = Color.red;
    Gizmos.DrawLine(transform.position, patrolTarget);
#if UNITY_EDITOR   // Handles es UnityEditor: guard obligatorio en código de runtime
    UnityEditor.Handles.Label(transform.position + Vector3.up, $"HP {maxHealth}");
#endif
}
```

Qué merece gizmo SIEMPRE en este estudio: radios de detección/ataque, waypoints y rutas de patrulla, spawn points, zonas de trigger, dirección de facing, límites de cámara. Es la forma nº1 de que un humano (o un screenshot pedido por el agente) verifique el setup de una escena de un vistazo.

`Handles` (clase de `UnityEditor`) añade lo que `Gizmos` no tiene: `Label`, `DrawWireDisc`, `DrawBezier`, y controles **interactivos** (`PositionHandle`, `RadiusHandle`, `Slider`, `Button`, `FreeMoveHandle`) — estos últimos van en `OnSceneGUI()` de un custom editor (3.2), no en `OnDrawGizmos`.

### 3.2 Custom inspectors

`[CustomEditor(typeof(X))]` sobre una clase que hereda de `Editor`; `[CanEditMultipleObjects]` para multi-selección. Patrón obligatorio: `serializedObject.Update()` → `EditorGUILayout.PropertyField(...)` → `serializedObject.ApplyModifiedProperties()` — trabajar vía `SerializedProperty` da undo, multi-edición y prefab overrides gratis; tocar `target` directo, no.

```csharp
// Editor/SpawnPointEditor.cs (Game.Editor)
using UnityEditor;
using UnityEngine;

[CustomEditor(typeof(SpawnPoint)), CanEditMultipleObjects]
public class SpawnPointEditor : Editor
{
    public override void OnInspectorGUI()
    {
        serializedObject.Update();
        EditorGUILayout.PropertyField(serializedObject.FindProperty("enemyStats"));
        EditorGUILayout.PropertyField(serializedObject.FindProperty("patrolTarget"));
        serializedObject.ApplyModifiedProperties();
    }

    void OnSceneGUI() // handle interactivo: mover patrolTarget en el Scene view
    {
        var sp = (SpawnPoint)target;
        EditorGUI.BeginChangeCheck();
        Vector3 pos = Handles.PositionHandle(sp.patrolTarget, Quaternion.identity);
        if (EditorGUI.EndChangeCheck())
        {
            Undo.RecordObject(sp, "Move Patrol Target"); // ANTES de modificar
            sp.patrolTarget = pos;
            PrefabUtility.RecordPrefabInstancePropertyModifications(sp);
        }
    }
}
```

- `Undo.RecordObject(obj, name)` se llama ANTES del cambio; si `obj` es instancia de prefab, añadir `PrefabUtility.RecordPrefabInstancePropertyModifications` (requisito documentado en docs de Undo).
- Docs 6.2 recomiendan UI Toolkit (`CreateInspectorGUI()` devolviendo `VisualElement`) para extensiones de editor nuevas; para tooling chico de un solo dev, IMGUI (`OnInspectorGUI`) sigue soportado y es menos código. No mezclar: UI Toolkit no corre dentro de IMGUI.
- Cuándo escribir un inspector custom: cuando el default estorba de verdad (botón "Preview wave", validación visible, handle en escena). No por estética.

### 3.3 Property drawers básicos

`PropertyDrawer` + `[CustomPropertyDrawer(typeof(T))]` customiza cómo se dibuja un tipo `[Serializable]` o un campo con un `PropertyAttribute` custom — en TODOS los inspectores a la vez (mejor inversión que un custom inspector por clase).

```csharp
[System.Serializable]
public struct IntRange { public int min, max; }

[CustomPropertyDrawer(typeof(IntRange))]
public class IntRangeDrawer : PropertyDrawer
{
    public override void OnGUI(Rect pos, SerializedProperty prop, GUIContent label)
    {
        var min = prop.FindPropertyRelative("min");
        var max = prop.FindPropertyRelative("max");
        pos = EditorGUI.PrefixLabel(pos, label);
        var half = new Rect(pos.x, pos.y, pos.width / 2 - 2, pos.height);
        EditorGUI.PropertyField(half, min, GUIContent.none);
        half.x += pos.width / 2 + 2;
        EditorGUI.PropertyField(half, max, GUIContent.none);
    }
}
```

- Reglas de docs: en drawers IMGUI usar `EditorGUI` (con `Rect`), NO `EditorGUILayout` (no soportado por rendimiento); altura custom con `GetPropertyHeight`; versión UI Toolkit con `CreatePropertyGUI(SerializedProperty)`.
- Antes de escribir un drawer, agotar los attributes built-in: `[Range]`, `[Min]`, `[Tooltip]`, `[Header]`, `[TextArea]`.

### 3.4 [MenuItem] — automatizar tareas repetidas

Método **static** + `[MenuItem("Ruta/Con/Slash")]` (mínimo un `/`). Sintaxis exacta (docs 6.2):

| Elemento | Sintaxis | Nota |
|---|---|---|
| Hotkey | `"Tools/Game/Validar %#v"` | `%`=Ctrl/Cmd · `#`=Shift · `&`=Alt · `_g`=tecla sola. Espacio antes del hotkey obligatorio |
| Validación | Segundo método con `[MenuItem(ruta, true)]` que devuelve `bool` | `false` = ítem gris |
| Orden | Tercer parámetro `priority` | Ítems de `GameObject/` con priority 10 para salir en el dropdown de Hierarchy |
| Menú contextual de component | `"CONTEXT/Rigidbody/..."` | Aparece en el ⋮ del component |
| Menú del Project window | `"Assets/..."` | También en right-click de Project |

```csharp
public static class GameTools
{
    [MenuItem("Tools/Game/Validar escena abierta %#v")]
    static void ValidateScene()
    {
        int errores = SceneValidator.Run(); // refs null, spawns fuera de NavMesh, layers mal
        Debug.Log(errores == 0 ? "Escena OK" : $"{errores} errores — ver consola");
    }

    [MenuItem("Tools/Game/Validar escena abierta %#v", true)]
    static bool ValidateSceneEnabled() => !UnityEditor.EditorApplication.isPlaying;
}
```

Menú `Tools/Game/` canónico del estudio (crecerlo por proyecto): validar escena, validar configs (SO con campos vacíos/fuera de rango), reimportar/rebuild de atlas, capturar screenshot del Game view, abrir el set de escenas de un nivel (`EditorSceneManager.OpenScene` aditivo). Cada tarea manual que se repite 3+ veces se convierte en MenuItem — y queda invocable por el agente vía `execute_menu_item` ([ver: unity/unity-mcp-flujo]).

### 3.5 ScriptableObject como asset de configuración

La arquitectura completa (eventos SO, runtime sets, variables compartidas — Hipple) está en [ver: unity/csharp-patrones] §1. Aquí, el uso mínimo obligatorio del template: **cero números mágicos en MonoBehaviours; todo tuning vive en assets bajo `_Game/Data/`**.

```csharp
[CreateAssetMenu(menuName = "Game/Enemy Stats", fileName = "EnemyStats_")]
public class EnemyStats : ScriptableObject
{
    [Min(1)] public int maxHealth = 10;
    public float moveSpeed = 3f;
    public IntRange damage;   // dibujado por el drawer de 3.3
}
```

- `[CreateAssetMenu]` (parámetros exactos: `menuName`, `fileName`, `order`) da el entry en `Assets > Create` — docs 6.2.
- Por qué importa para el flujo: balancear = editar un `.asset` YAML chico y diffeable, sin tocar escenas ni recompilar. El diseñador (o el agente) itera datos sin riesgo de romper lógica.
- Los SO son assets compartidos: mutar sus campos en runtime persiste en el Editor (no en build) — para estado mutable, clonar con `Instantiate(so)` o separar config (SO) de estado (clase runtime).

---

## 4. Convenciones agente-friendly

Lo que hace un proyecto operable por un agente IA (sin ojos, con MCP o editando YAML/C# en disco — [ver: unity/unity-mcp-flujo]):

1. **Nombres estables y únicos**: los GameObjects raíz de cada escena y los managers tienen nombres únicos y NUNCA se renombran a la ligera — son las anclas de `find_gameobjects` y de los scripts de validación.
2. **Prefabs sobre escenas**: un cambio de contenido = diff en un `.prefab` de 200 líneas, no en una `.unity` de 20.000. Menos contexto que leer, merges triviales, cambios verificables.
3. **Datos en ScriptableObjects**: balance y configuración como `.asset` YAML — el agente los lee/edita/diffea como texto sin abrir el Editor.
4. **Escenas chicas y de responsabilidad única**: caben en contexto, se validan rápido, y dos tareas paralelas no chocan.
5. **Cero conocimiento oral**: cualquier paso de setup manual ("acuérdate de regenerar X") se convierte en MenuItem o AssetPostprocessor versionado. Si no está en el repo, no existe.
6. **Validación como código**: `Tools/Game/Validar...` + tests en `Game.Tests` — el agente los corre tras cada cambio en vez de "mirar" la escena. Consola limpia = contrato (cero errores Y cero warnings propios).
7. **Gizmos como evidencia visual**: con gizmos bien puestos, un solo screenshot del Scene view responde "¿está bien colocado el spawn?" sin inspeccionar objeto por objeto.
8. **Convención sobre configuración**: paths predecibles (`_Game/Data/Enemies/EnemyStats_Grunt.asset`) — el agente encuentra las cosas por convención, sin buscar.

---

## Reglas practicas

- [ ] Commit 0: Force Text + Visible Meta Files confirmados, `git lfs install`, `.gitignore` + `.gitattributes` canónicos — antes del primer asset.
- [ ] Todo bajo `Assets/_Game/`; third-party aislado; sin carpetas vacías.
- [ ] 5 asmdefs (`Core/Gameplay/UI/Editor/Tests`); código editor SOLO en `Game.Editor` (Editor-only).
- [ ] Naming del día 0: tabla de prefijos de §1 aplicada por convención + AssetPostprocessor; no renombrar en masa después.
- [ ] Escena `Boot` en índice 0; managers persistentes ahí, no en `DontDestroyOnLoad`.
- [ ] Una escena = una responsabilidad; split Gameplay/Env cuando crezca o haya conflictos.
- [ ] `SceneLoader` es la ÚNICA vía de carga: `LoadSceneAsync` aditivo + `SetActiveScene` + `UnloadSceneAsync`.
- [ ] Bootstrapper con `RuntimeInitializeOnLoadMethod` para poder darle Play a cualquier escena; managers idempotentes.
- [ ] Todo objeto repetido es prefab; contenido editado en Prefab Mode, no en la escena.
- [ ] Radios, rutas, spawns y triggers con `OnDrawGizmosSelected` desde el día que se crean.
- [ ] Inspector custom solo con motivo (botón, handle, validación); siempre vía `serializedObject.Update/ApplyModifiedProperties`.
- [ ] Handles interactivos: `EditorGUI.BeginChangeCheck` + `Undo.RecordObject` antes del cambio (+ `RecordPrefabInstancePropertyModifications` en instancias de prefab).
- [ ] Property drawer para tipos `[Serializable]` repetidos; agotar `[Range]/[Min]/[Tooltip]` antes.
- [ ] Tarea manual repetida 3+ veces → `[MenuItem("Tools/Game/...")]` con validación.
- [ ] Tuning y configs en ScriptableObjects bajo `_Game/Data/`; cero números mágicos en MonoBehaviours.
- [ ] Estado mutable NUNCA directo en un SO compartido: clonar o separar config/estado.
- [ ] MenuItem de validación de escena/configs corrido antes de cada commit que tocó contenido.
- [ ] Consola limpia (0 errores, 0 warnings propios) como definición de "escena sana".

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Managers con `DontDestroyOnLoad` que se duplican al volver al menú | Escena `Boot` persistente + managers idempotentes; DDOL no hace falta en este template |
| Play directo a una escena de nivel revienta por managers ausentes | Bootstrapper de §2 (carga `Boot` aditiva si falta) |
| `Instantiate` cae en la escena equivocada con carga aditiva | `SetActiveScene` explícito tras cargar el nivel |
| Referencia serializada entre dos escenas "que se rompe sola" | No existe cross-scene: cablear vía managers de Boot, eventos o SO compartidos |
| `Handles`/`UnityEditor` en un script de runtime → el build no compila | Guard `#if UNITY_EDITOR` en `OnDrawGizmos*`; todo lo demás a `Game.Editor` |
| Gizmos de todo el mundo a la vez → Scene view ilegible | `OnDrawGizmosSelected` por defecto; `OnDrawGizmos` solo para lo crítico |
| Custom inspector escribiendo en `target` directo | Sin undo, sin multi-edit, overrides de prefab rotos: usar `serializedObject` |
| Handle interactivo que no se puede deshacer / no marca override | `Undo.RecordObject` ANTES del cambio + `RecordPrefabInstancePropertyModifications` |
| `EditorGUILayout` dentro de un PropertyDrawer | No soportado: `EditorGUI` con `Rect` (o `CreatePropertyGUI` en UI Toolkit) |
| `[MenuItem]` en método de instancia, o ruta sin `/` | Solo métodos static y ruta con al menos un submenú |
| Hotkey de MenuItem que no dispara | Falta el espacio antes del hotkey: `"...Do _g"`, no `"...Do_g"` |
| Balance hardcodeado en MonoBehaviours (números mágicos) | SO de config en `_Game/Data/`; balancear = editar el asset |
| Runtime muta un SO y "el cambio se quedó guardado" | Es persistencia de asset en Editor: clonar el SO o separar config/estado |
| Renombrar GameObjects/paths que scripts o el agente buscan por nombre | Nombres = API estable; renombrar solo con búsqueda de usos previa |
| Setup manual no versionado ("hay que acordarse de...") | MenuItem/postprocessor en el repo o no existe |

## Fuentes

- MonoBehaviour.OnDrawGizmos / OnDrawGizmosSelected — Unity Scripting Reference 6.2 — cuándo corre cada uno, pickabilidad, editor-only.
- Gizmos — Unity Scripting Reference 6.2 — API exacta de dibujo (`DrawWireSphere`, `DrawIcon`...), `color` y `matrix`.
- Handles — Unity Scripting Reference 6.2 — controles interactivos (`PositionHandle`, `RadiusHandle`, `Button`), `Label`, `DrawingScope`, uso en `OnSceneGUI`.
- Create a Custom Inspector (editor-CustomEditors) — Unity Manual 6.2 — `[CustomEditor]`, `OnInspectorGUI`, patrón `serializedObject.Update/ApplyModifiedProperties`, `[CanEditMultipleObjects]`, `OnSceneGUI`, recomendación oficial de UI Toolkit para extensiones.
- PropertyDrawer — Unity Scripting Reference 6.2 — `[CustomPropertyDrawer]`, `OnGUI(Rect,...)`, `GetPropertyHeight`, `CreatePropertyGUI`, prohibición de `EditorGUILayout`.
- MenuItem — Unity Scripting Reference 6.2 — firmas, sintaxis de hotkeys (`% # & _` + espacio), validación con `bool`, priority, rutas `CONTEXT/`/`Assets/`/`GameObject/`, solo static.
- Undo.RecordObject — Unity Scripting Reference 6.2 — registrar antes de modificar, snapshot por frame, `PrefabUtility.RecordPrefabInstancePropertyModifications` en instancias de prefab.
- CreateAssetMenuAttribute — Unity Scripting Reference 6.2 — parámetros exactos `menuName`/`fileName`/`order`.
- Unity Style Guide — justinwasilenko (GitHub) — tabla de prefijos por tipo de asset, `Prefijo_Nombre_Variante`, PascalCase, reglas de carpetas.
- unity/arquitectura-unity.md (base propia) — ciclo de vida, escenas aditivas/active scene, asmdefs, serialización, `RuntimeInitializeOnLoadMethod` — sintetizado en §1–2.
- unity/assets-pipeline-git.md (base propia) — gitignore/gitattributes canónicos, LFS, UnityYAMLMerge, carpetas, estrategia anti-conflictos — sintetizado en §1.
- unity/csharp-patrones.md (base propia) — ScriptableObjects como arquitectura (Hipple), singletons y alternativas — referenciado en §2–3.

[ver: pipeline-completo] · [ver: testing-qa] · [ver: arte-a-unity] · [ver: unity/unity-mcp-flujo] · [ver: unity/gotchas-unity]
