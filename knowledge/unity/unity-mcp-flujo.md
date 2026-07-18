# Operar Unity via MCP (agente IA)

> **Cuando cargar este archivo:** siempre que haya un editor Unity conectado por MCP (herramientas `manage_scene`, `read_console`, etc. disponibles) y vayas a tocar escenas, scripts, assets o a verificar estado del juego. Es la guía operativa: qué herramienta usar, en qué orden, y cómo verificar sin ojos.

Verificado contra CoplayDev/unity-mcp v10.x (docs julio 2026) y docs oficiales Unity 6.x (6000.2). Stack objetivo: Unity 6.x + URP.

---

## 1. Qué es mcp-for-unity

- **CoplayDev/unity-mcp** ("MCP for Unity", MIT, open source): un servidor **Model Context Protocol** que expone el editor de Unity a un agente IA. El agente no "escribe código a ciegas": opera el editor real — crea GameObjects, edita scripts, corre tests, lee la consola.
- Arquitectura en dos piezas:
  1. **Package de Unity** (bridge, instalado via Package Manager con git URL `https://github.com/CoplayDev/unity-mcp.git?path=/MCPForUnity#main`): corre dentro del editor y ejecuta las operaciones.
  2. **Servidor Python** (3.10+, gestionado con `uv`): habla MCP con el cliente (Claude Code, Cursor, VS Code, etc.) y enruta al bridge.
- Transports: **HTTP** (default, endpoint `http://localhost:8080/mcp`, multi-cliente con `client_id` por sesión, bind a loopback por defecto) y **stdio** (un proceso Python por cliente, bridge TCP legacy hacia el editor).
- Soporta **Unity 2021.3 LTS → 6.x**. Está en beta: comportamiento puede cambiar entre versiones (última release verificada: v10.1.0, 13-jul-2026).
- No confundir con otros servers "unity mcp" (hay varios forks). Los nombres de herramienta de abajo son los del catálogo oficial v10; si el server conectado difiere, inventaría sus tools reales antes de asumir nada.

### Multi-instancia

- Cada editor conectado tiene ID estable `Name@hash` (Name = `productName` del proyecto, hash = 8 chars derivados de la ruta).
- El resource `mcpforunity://instances` lista los editores conectados (ID, ruta de proyecto, transport, puerto).
- **1 editor conectado** → routing automático. **2+ editores** → el server da error hasta que llames `set_active_instance("MyGame@a1b2c3d4")` (acepta hash prefix o, en stdio, número de puerto tipo `"6401"`).
- Cada tool call individual admite `unity_instance` para enrutar solo esa llamada sin cambiar el default de sesión.
- Regla de agente: **trabaja contra UNA instancia a la vez**. Pin explícito con `set_active_instance` al inicio si hay más de una; nunca alternar instancias a mitad de una operación multi-paso.

## 2. Catálogo de herramientas (v10: ~48 tools en 10 grupos)

Solo el grupo `core` viene activo por defecto. Los demás se activan con `manage_tools(action="activate", group="...")` (y `list_groups` para ver estado). Si una tool esperada "no existe", probablemente su grupo está desactivado — activarlo, no improvisar.

| Grupo | Default | Tools clave |
|---|---|---|
| `core` | ✅ ON | `manage_scene`, `manage_gameobject`, `find_gameobjects`, `manage_components`, `manage_prefabs`, `manage_asset`, `manage_material`, `manage_camera`, `manage_physics`, `manage_graphics`, `manage_packages`, `manage_build`, `manage_editor`, `execute_menu_item`, `read_console`, `refresh_unity`, `batch_execute`, `set_active_instance` + toda la familia de scripts (`create_script`, `apply_text_edits`, `script_apply_edits`, `validate_script`, `delete_script`, `find_in_file`, `get_sha`, `manage_script_capabilities`) |
| `testing` | off | `run_tests` (async, devuelve `job_id`), `get_test_job` (polling) |
| `scripting_ext` | off | `execute_code` (C# arbitrario en el editor), `manage_scriptable_object` |
| `docs` | off | `unity_docs` (docs.unity3d.com), `unity_reflect` (reflexión sobre la API viva) |
| `ui` | off | `manage_ui` (UI Toolkit: UXML/USS/UIDocument) |
| `animation` | off | `manage_animation` (Animator, AnimationClips) |
| `vfx` | off | `manage_shader`, `manage_texture`, `manage_vfx` (ParticleSystem, VFX Graph, LineRenderer) |
| `profiling` | off | `manage_profiler` (sesiones, counters, memoria, Frame Debugger) |
| `probuilder` | off | `manage_probuilder` (requiere el package) |
| `asset_gen` | off | `generate_image/audio/model`, `import_model` (proveedores externos con API key; no contar con ellos) |

Convenciones transversales:
- **Paths relativos a `Assets/`** salvo indicación contraria, siempre con forward slashes (`Scripts/Player/Health.cs`).
- **Resources para leer, tools para mutar**: estado del editor (`editor_state`, `project_info`, tests disponibles) se lee por resources MCP; las tools ejecutan acciones. Leer antes de mutar.
- `batch_execute` agrupa varios comandos en un round-trip — úsalo para setups repetitivos (crear 10 objetos, setear 10 propiedades), no para encadenar pasos que dependen de compilación entre medio.

## 3. Flujos de las operaciones principales

| Operación | Flujo |
|---|---|
| Escena nueva | `manage_scene` (create) → añadir SIEMPRE una Camera y una Directional Light (una escena creada por código viene vacía) → `manage_scene` (save) |
| Cargar/consultar escena | `manage_scene` (load / get info: jerarquía, escena activa) |
| Crear objeto | `manage_gameobject` (create, con nombre/parent/posición) → `manage_components` (add + set de propiedades) |
| ScriptableObject | definir la clase (ciclo §4) → `manage_scriptable_object` (grupo `scripting_ext`): crea el asset y setea campos por paths de SerializedObject |
| Buscar objetos | `find_gameobjects` por nombre, tag, layer, tipo de componente o path — la herramienta de "ver" la escena |
| Prefab | armar el GameObject → `manage_prefabs` para crear/actualizar el asset; instanciar desde el prefab, no duplicar a mano |
| Script nuevo | `validate_script` (opcional pre-check) → `create_script` → **ciclo de compilación (§4)** → recién ahí `manage_components` (add) con el tipo nuevo |
| Editar script | `find_in_file`/`get_sha` para localizar sin leer todo → `script_apply_edits` (edición estructurada por método/clase, límites seguros) o `apply_text_edits` (texto plano) → ciclo de compilación (§4) |
| Assets | `manage_asset` (import/create/modify/delete); materiales con `manage_material` |
| Play mode | `manage_editor` (entrar/salir de play, estado del editor, tags/layers) — ver límites en §6 |
| Menú | `execute_menu_item` con el path exacto ("File/Save Project") — evita los que abren ventanas modales (§6) |
| Tests | `run_tests` → guarda el `job_id` → `get_test_job` en polling hasta terminar (§5) |
| Consola | `read_console` (get con filtro por tipo Error/Warning/Log, o clear) — el instrumento central de verificación |

## 4. EL CICLO SAGRADO tras tocar código

Este es el flujo más importante del archivo. Unity compila C# en el editor y hace **domain reload** (recarga del dominio de scripting) cuando detecta scripts cambiados en el asset refresh. Hasta que esa compilación termina **sin errores**, los tipos nuevos NO existen para el editor.

```text
1. Editar/crear script   → create_script / script_apply_edits / apply_text_edits
2. Forzar refresh        → refresh_unity (pide asset refresh + compilación)
3. Esperar compilación   → poll del resource editor_state, campo isCompiling,
                           hasta que sea false (equivale a EditorApplication.isCompiling)
4. Leer consola          → read_console filtrando Error: ¿hay errores CS####?
5a. SIN errores          → seguir: añadir el componente, correr tests, entrar a play
5b. CON errores          → arreglar el script y volver al paso 2. NUNCA avanzar.
```

Por qué saltárselo rompe todo:

- **El tipo no existe todavía.** `manage_components(add, "PlayerHealth")` inmediatamente después de `create_script` falla o añade un script "Missing": el assembly con `PlayerHealth` aún no se compiló. Solo tras compilación exitosa los tipos nuevos son usables (documentado explícitamente por el propio proyecto unity-mcp).
- **Un error de compilación deja el editor en estado bloqueado**: no se puede entrar a Play mode ni usar ningún tipo del assembly roto, y cada operación posterior devuelve resultados engañosos. Un solo `;` faltante invalida todo lo que hagas después.
- **El domain reload resetea estado**: valores de campos no serializados, variables `static` y suscripciones a eventos `static` se pierden (Unity 6 Manual, "Domain Reloading"). Cualquier estado que el agente "recordaba" del editor puede haber cambiado tras recompilar.
- **El bridge vive dentro del editor**: durante el domain reload el lado Unity se recarga y las tool calls pueden fallar o colgar momentáneamente. Si una llamada justo después de editar código da timeout/error de conexión, no es un bug tuyo: espera y reintenta, luego verifica `isCompiling`.
- Errores acumulados de sesiones anteriores contaminan la señal: si la consola trae ruido viejo, `read_console(clear)` ANTES de editar, para que lo que leas después sea atribuible a TU cambio.

`validate_script` reduce iteraciones: el validador estructural (default) atrapa errores de sintaxis básicos antes de escribir; con Roslyn habilitado (define `USE_ROSLYN` + NuGet Microsoft.CodeAnalysis en el proyecto) hace análisis semántico completo (namespaces/tipos/métodos inexistentes) sin esperar la compilación de Unity. Útil, pero **no sustituye** el ciclo: la compilación real de Unity es el veredicto final.

## 5. Verificar sin ojos

El agente no ve la pantalla. "Debería funcionar" no es evidencia; esto sí:

| Qué verificar | Cómo |
|---|---|
| Compiló sin errores | `read_console` filtro Error tras `isCompiling == false` (§4) |
| El objeto/estado existe de verdad | `find_gameobjects` + `manage_gameobject` (get: componentes, propiedades, transform) — leer de vuelta lo que acabas de crear |
| La escena quedó como debía | `manage_scene` (get info: jerarquía completa) |
| Lógica de runtime | `run_tests` (EditMode/PlayMode) → `get_test_job(job_id)` hasta status final → leer pases/fallos reales |
| Comportamiento en vivo | `manage_editor` (play) → dejar correr → `read_console` buscando errores/`Debug.Log` de instrumentación → salir de play |
| Un valor puntual en el editor | `execute_code` (grupo `scripting_ext`): C# ad-hoc que inspecciona y reporta |
| Una API que no recuerdas | `unity_docs` / `unity_reflect` (grupo `docs`) — contra la API viva del proyecto, no de memoria |

Patrón de verificación con `execute_code` (assert barato sin escribir un test):

```csharp
var player = GameObject.Find("Player");
if (player == null) { Debug.LogError("VERIFY: Player no existe"); return; }
var health = player.GetComponent<PlayerHealth>();
Debug.Log($"VERIFY: health={(health != null ? health.MaxHealth.ToString() : "SIN COMPONENTE")}, " +
          $"pos={player.transform.position}");
```
Luego `read_console` y leer el `VERIFY:` — eso es evidencia; la ausencia de error no lo es.

Tests — EditMode vs PlayMode (Unity Test Framework):
- **EditMode**: corren en el editor, en el loop de `EditorApplication.update`; acceso a `UnityEditor`; **no soportan coroutines** — para lógica pura y tooling.
- **PlayMode**: corren en play mode (o en un player); `[UnityTest]` corre como coroutine y puede `yield return null` para saltar frames — para gameplay real. El código a testear debe vivir en un asmdef propio (no se puede referenciar `Assembly-CSharp` desde tests de player).
- Preferir `[Test]` (NUnit síncrono) salvo que necesites frames/tiempo. [ver: csharp-patrones]
- Un run de tests puede disparar domain reload y play mode: por eso `run_tests` es **async con job** — hacer polling con `get_test_job`, no asumir resultado inmediato.

Snippet mínimo de PlayMode test (para que `run_tests` tenga algo que correr):

```csharp
using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;

public class PlayerHealthTests
{
    [UnityTest]
    public IEnumerator TakeDamage_ReducesHealth()
    {
        var go = new GameObject("player", typeof(PlayerHealth));
        var health = go.GetComponent<PlayerHealth>();
        yield return null;                    // dejar correr Awake/Start un frame
        health.TakeDamage(10);
        Assert.AreEqual(90, health.Current);
        Object.Destroy(go);
    }
}
```
El asmdef del test referencia el asmdef del código de juego + `nunit.framework.dll`. Sin asmdef propio para el código, los tests de player no pueden referenciarlo.

Caveats de `execute_code`:
- Corre en el main thread del editor, contra los assemblies YA compilados: un tipo recién creado sin pasar el ciclo §4 tampoco existe para `execute_code`.
- Código de larga duración congela el editor (mismo thread que todo lo demás): fragmentos cortos, sin loops de espera ni `Thread.Sleep`.
- Es la navaja suiza para leer estado que ninguna tool estructurada expone — pero para mutaciones, preferir las tools dedicadas (dejan rastro más claro y validan input).

**Screenshots:** el catálogo core v10 NO incluye una tool de screenshot. Si el server conectado expone una (fork o custom tool del proyecto), úsala. Alternativa: `execute_code` con `ScreenCapture.CaptureScreenshot("shot.png")` durante play mode y leer el archivo del disco — funciona para el Game View; en edit mode no cuentes con ello.

### Play mode como banco de pruebas

Flujo seguro para "correr el juego y mirar":

```text
1. manage_scene (save)            — guardar ANTES de entrar a play
2. read_console (clear)           — línea base limpia
3. manage_editor (enter play)     — ojo: dispara domain reload por defecto (lento)
4. esperar N segundos de gameplay — el juego corre solo; no martillar tools
5. read_console (get)             — errores, excepciones, tus Debug.Log de instrumentación
6. find_gameobjects / execute_code — inspeccionar estado runtime si hace falta
7. manage_editor (exit play)      — SIEMPRE salir al terminar
```

- **Todo cambio hecho DURANTE play mode se revierte al salir** (comportamiento estándar de Unity): no edites escena/componentes en play esperando que persista — anota los valores buenos y aplícalos en edit mode.
- Instrumentar antes de correr: si el objetivo es verificar la mecánica X, mete `Debug.Log` con prefijo (`"VERIFY:"`) en los puntos clave ANTES de entrar a play; la consola es tu única ventana.
- Excepciones en runtime (`NullReferenceException` y compañía) NO detienen el play mode: aparecen en consola y el juego sigue cojo. Consola sin leer = verificación que no ocurrió.

## 6. Límites: dónde el agente se queda ciego o atascado

- **Diálogos modales bloquean todo.** `EditorUtility.DisplayDialog` es modal: congela el main thread del editor hasta que un HUMANO haga click — y el bridge corre en ese thread, así que TODAS las tool calls cuelgan. Causas típicas: `execute_menu_item` sobre menús que abren ventanas (Build Settings con confirmaciones, imports con wizard), popups de "Script has compile errors, enter play mode anyway?", diálogos de packages. Si todo empieza a dar timeout de golpe: sospecha modal abierto y avisa al humano — no reintentes en loop.
- **Ventanas nativas del OS** (file pickers, color pickers) son igual de bloqueantes e inoperables por MCP.
- **Play mode**: entrar dispara por defecto un domain reload (lento, y desconecta el bridge momentáneamente). Con Enter Play Mode Settings (Project Settings > Editor) el proyecto puede tener el reload desactivado — entonces los `static` NO se resetean al entrar a play: no asumas estado limpio, verifica. [ver: gotchas-unity]
- **Imports pesados**: `refresh_unity` sobre una carpeta con muchos assets nuevos (texturas grandes, modelos, un package) puede tardar minutos y bloquear el editor mientras importa. `AssetDatabase.Refresh` además dispara garbage collection de assets (`Resources.UnloadUnusedAssets` implícito). No lo llames "por si acaso" en loop.
- **Operaciones largas + timeouts**: builds (`manage_build`), light baking (`manage_graphics`), test suites grandes. Usar las variantes async cuando existan (tests) y polling; para el resto, esperar sin martillar.
- **El bridge muere con el editor**: crash de Unity, editor cerrado, o proyecto sin el package = tools fallan. Verificar `mcpforunity://instances` antes de diagnosticar "bugs" fantasma.
- **Sin ojos para lo visual-subjetivo**: MCP dice que el material está asignado; no dice si se VE bien. Juicios estéticos (iluminación, feel, layout) requieren screenshot + criterio o al humano. [ver: gamedev/game-feel]

## 7. Buenas prácticas de agente

- **Cambios chicos, verificación frecuente.** Un script → ciclo §4 → verificar → siguiente. Nunca 5 scripts nuevos y "a ver qué pasa": con 30 errores de compilación mezclados no sabes cuál cambio rompió qué.
- **Leer antes de escribir**: `manage_scene` (get) / `find_gameobjects` antes de crear (evita duplicados "Player (1)"); `find_in_file`/`get_sha` antes de editar un script (edición sobre contenido real, no recordado).
- **Ediciones estructuradas > reescritura total**: `script_apply_edits` (por método/clase) minimiza el riesgo de romper el resto del archivo; `apply_text_edits` para cambios puntuales. Reescribir el archivo entero solo si es corto o nuevo.
- **No dispares reimports masivos**: nada de refresh tras cada micro-cambio de texto; agrupa las ediciones de una tarea y un solo `refresh_unity` al final del lote (pero SIEMPRE antes de usar los tipos).
- **Consola con higiene**: `read_console(clear)` antes de una operación que vas a verificar; filtrar por Error primero, Warning después. Warnings de deprecación en Unity 6 suelen anticipar el próximo break.
- **`execute_menu_item` como último recurso**: preferir la tool específica (`manage_scene` save > menú File/Save) — las tools devuelven resultado estructurado, el menú no devuelve casi nada y puede abrir modales.
- **Guardar explícito**: escena tocada → `manage_scene` (save); no depender de que el humano guarde. Cambios de assets → verificar que el archivo existe en disco.
- **Un proyecto/instancia a la vez** (§1). En paralelo con otro agente sobre el mismo editor: no — el estado del editor es global y compartido.
- **Packages con `manage_packages`**, no editando `manifest.json` a mano: instalar un package dispara recompilación completa — ciclo §4 después, siempre.

## 8. Híbrido: MCP vs editar .cs directo en disco

El agente suele tener también filesystem (Read/Edit/Write) y git sobre el proyecto. Editar `.cs` en disco es válido: Unity detecta el cambio en el próximo asset refresh (al recuperar foco la ventana, o forzado con `refresh_unity`) y recompila igual.

| Situación | Usar |
|---|---|
| Refactor multi-archivo, mover código, ediciones grandes | **Disco** (herramientas de archivo del agente + git) — más rápido y diffeable |
| Crear/editar 1-2 scripts dentro de un flujo de editor | **MCP** (`create_script`/`script_apply_edits`) — el bridge dispara el refresh solo |
| Escenas, prefabs, materiales, componentes, ScriptableObjects | **MCP siempre** — son assets serializados de Unity (YAML); editarlos a mano en disco es frágil y propenso a corromper GUIDs [ver: assets-pipeline-git] |
| Ver errores de compilación, correr tests, play mode, estado de escena | **MCP siempre** — el disco no te dice nada de eso |
| Editor sin foco y editaste en disco | `refresh_unity` via MCP para forzar el import + compilación — si no, Unity ni se entera |

Regla de oro del híbrido: **edites donde edites, el ciclo §4 es el mismo** — refresh, esperar `isCompiling == false`, `read_console`, y solo entonces continuar. La compilación y su veredicto viven en el editor; sin MCP (o sin mirar el editor) estás compilando a ciegas.

## Reglas prácticas

1. Al conectar: lista `mcpforunity://instances`; si hay 2+ editores, `set_active_instance` antes de cualquier otra tool.
2. Grupo de tools "faltante" → `manage_tools(action="list_groups")` y activar; solo `core` viene ON por defecto.
3. Paths siempre relativos a `Assets/`, con `/`, nunca backslashes ni rutas absolutas.
4. Tras CUALQUIER cambio de código (MCP o disco): refresh → poll `isCompiling` hasta false → `read_console` (Error) → recién entonces usar los tipos nuevos.
5. Cero errores de compilación antes de: añadir componentes nuevos, entrar a play, correr tests, declarar nada terminado.
6. `read_console(clear)` antes de la operación que vas a verificar; así cada error que aparezca es atribuible.
7. Nunca declarar "listo" sin evidencia leída: consola limpia + estado inspeccionado (`find_gameobjects`/get) o test verde de `get_test_job`.
8. Un cambio → una verificación. Prohibido apilar 5 cambios sin compilar entre medio.
9. Escena nueva por MCP = vacía: añadir Camera y Directional Light siempre.
10. Leer antes de crear: buscar si el objeto/script/asset ya existe (evitar duplicados y pisar trabajo).
11. `validate_script` antes de escribir scripts largos; con errores CS recurrentes, sugerir instalar Roslyn (`USE_ROSLYN`).
12. `run_tests` es async: guardar `job_id` y hacer polling con `get_test_job`; jamás asumir el resultado.
13. `batch_execute` para lotes independientes; nunca para pasos separados por una compilación.
14. Timeouts repentinos en TODAS las tools = editor en domain reload o modal abierto: esperar/reintentar una vez, luego avisar al humano — no loop de reintentos.
15. Guardar escena (`manage_scene` save) tras cada bloque de cambios de escena.
16. No editar escenas/prefabs/materiales como texto en disco; para eso existe MCP.
17. Imports pesados y builds: esperarlos, no dispararlos en ráfaga; `refresh_unity` una vez por lote de cambios.
18. Play mode: entrar, verificar con consola/estado, salir. No dejar el editor en play al terminar la tarea.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| `create_script` → `manage_components(add)` inmediato → "type not found" o script Missing | El tipo no existe hasta compilar: ciclo §4 completo entre medio |
| Avanzar con 1 error CS "que no parece relacionado" | Un error bloquea todo el assembly (y el play mode); arreglar SIEMPRE antes de seguir |
| Leer consola con ruido viejo y atribuirse (o perderse) errores | `read_console(clear)` antes del cambio; leer después filtrando Error |
| Asumir que los `static` conservan valores tras editar código | Domain reload los resetea (campos static, eventos static, no-serializados); releer estado tras cada recompilación |
| Asumir estado limpio al entrar a play en proyecto con domain reload desactivado (Enter Play Mode Settings) | Los static NO se resetean ahí: verificar estado, no asumirlo |
| Tool calls colgadas e ir reintentando en loop | Modal abierto o domain reload: un reintento, luego reportar al humano (§6) |
| `execute_menu_item` a un menú que abre ventana/modal | Usar la tool estructurada equivalente; menús solo para acciones sin UI |
| Editar .cs en disco y "no pasa nada" | El editor sin foco no refresca: `refresh_unity` para forzar import + compilación |
| Editar la escena (.unity) o prefab como YAML en disco | Frágil (GUIDs, formato serializado): usar `manage_scene`/`manage_prefabs` |
| Crear escena por código y "no se ve nada" en play | Escena nueva no trae Camera ni luz: añadirlas siempre |
| Verificar con "el comando no dio error" | Éxito de la tool ≠ resultado correcto: leer de vuelta el estado (get) o un `Debug.Log` de verificación |
| `run_tests` y reportar el resultado sin esperar el job | Es async: polling de `get_test_job` hasta estado final |
| Refresh/reimport tras cada micro-edición | Agrupa ediciones, un refresh por lote; el refresh importa assets y dispara GC de assets (caro) |
| Trabajar contra la instancia equivocada con 2 editores abiertos | `set_active_instance` explícito al inicio; `unity_instance` por llamada si necesitas comparar |
| Editar escena/componentes DURANTE play mode y perderlo todo al salir | Los cambios en play se revierten (comportamiento estándar de Unity): anotar valores y aplicarlos en edit mode |
| Quedarse en play mode al terminar la tarea | `manage_editor` (exit play) siempre; el editor en play distorsiona toda operación posterior |
| Dar por hecho que existe tool de screenshot | El core v10 no la trae: fork/custom tool, o `ScreenCapture.CaptureScreenshot` via `execute_code` en play mode |
| `execute_code` con un tipo recién creado sin compilar | Mismo ciclo §4: `execute_code` compila contra los assemblies existentes, el tipo nuevo aún no está |

## Fuentes

- **MCP for Unity — README** — CoplayDev/unity-mcp (GitHub) — qué es, arquitectura package+servidor Python, Unity 2021.3→6.x, clientes soportados, v10.0.0, MIT.
- **Tool Reference (48 tools, 10 grupos)** — coplaydev.github.io/unity-mcp/reference/tools — catálogo completo con nombres exactos y descripciones de cada tool citada aquí.
- **Guía Tool Groups** — coplaydev.github.io/unity-mcp/guides/tool-groups — solo `core` ON por defecto; `manage_tools` activate/deactivate/list_groups/reset.
- **Guía Multi-Instance Routing** — coplaydev.github.io/unity-mcp/guides/multi-instance — IDs `Name@hash`, resource `mcpforunity://instances`, `set_active_instance`, `unity_instance`, error con 2+ editores sin pin.
- **Arquitectura Transports** — coplaydev.github.io/unity-mcp/architecture/transports — HTTP default `localhost:8080/mcp`, `client_id` por sesión, stdio con bridge TCP, bind loopback.
- **Guía Roslyn** — coplaydev.github.io/unity-mcp/guides/roslyn — `validate_script` estructural vs semántico, `USE_ROSLYN`, setup NuGet, límites.
- **Instrucciones del servidor UnityMCP** (server instructions MCP en vivo) — flujo oficial post-edición de scripts: `read_console` para errores de compilación, poll de `editor_state.isCompiling`, tipos usables solo tras compilar, paths relativos a `Assets/`, Camera+Light en escenas nuevas.
- **Domain Reloading** — Unity Manual 6000.2 (docs.unity3d.com) — qué resetea el reload (static, no-serializados, eventos static), cuándo ocurre (play mode y asset refresh con scripts cambiados), Enter Play Mode Settings.
- **AssetDatabase.Refresh** — Unity ScriptReference 6000.2 — importa assets cambiados y dispara GC de assets implícito (`Resources.UnloadUnusedAssets`).
- **EditorApplication.isCompiling** — Unity ScriptReference 6000.2 — flag read-only "¿el editor está compilando?" (lo que expone `editor_state.isCompiling`).
- **Edit Mode vs Play Mode tests** — Unity Manual 6000.2 (Test Framework) — EditMode en `EditorApplication.update` sin coroutines; PlayMode con `[UnityTest]` como coroutine; asmdef requerido.
- **EditorUtility.DisplayDialog** — Unity ScriptReference 6000.2 — "This method displays a modal dialog": base de por qué los modales congelan el bridge.
