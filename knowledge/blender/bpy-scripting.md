# La API Python (bpy): automatizar y extender Blender

> **Cuando cargar este archivo:** siempre que vayas a escribir o ejecutar codigo Python dentro de Blender (via MCP, consola, Text Editor o headless `--background`), a crear/instalar un addon, o a decidir entre `bpy.data` y `bpy.ops` para una operacion. Version de referencia: Blender 5.x (stack local: 5.2 LTS).

## Por que Blender es automatizable al 100%

- Casi todo boton, menu y atajo de la UI ejecuta un **operador**, y todo operador esta expuesto en `bpy.ops`. Regla de la doc oficial: cualquier ajuste que se pueda cambiar con un boton tambien se puede cambiar con Python. Si un boton NO muestra linea `Python:` en su tooltip, es de lo poquisimo no accesible por script.
- La propia UI te dice el comando:
  - **Preferences ‣ Interface ‣ Display ‣ Developer Extras**: activa Operator Search, y en el menu contextual (RMB) de cualquier control agrega **Online Python Reference** y **Copy Python Command**.
  - **Preferences ‣ Interface ‣ Tooltips ‣ Python Tooltips**: el tooltip de cada propiedad muestra su ruta Python (`bpy.types.Object.location`, `Python: bpy.ops.render.render()`, etc.).
  - `Ctrl-C` con el mouse sobre un boton/item de menu copia su comando `bpy.ops.*` al clipboard.
  - RMB sobre una propiedad ‣ **Copy Data Path** copia la ruta desde el ID data-block hasta la propiedad (ej. `modifiers["Subdivision"].levels`).
- El **Info editor** (incluido en el workspace **Scripting**) graba cada operador ejecutado como linea Python; seleccionas entradas y `Ctrl-C` para copiarlas. Solo registra operadores con la opcion `REGISTER`; para ver TODOS: `blender --debug-wm` o `bpy.app.debug_wm = True`.
- La consecuencia operativa para un agente: cualquier flujo manual de Blender se puede reproducir por script, y por tanto por MCP o headless [ver: blender-mcp-operativo].

## El modelo de la API: bpy.data vs bpy.ops vs bpy.context

| Modulo | Que es | Cuando usarlo |
|---|---|---|
| `bpy.data` | Acceso directo a TODOS los data-blocks del .blend (`objects`, `meshes`, `materials`, `collections`, `node_groups`...) | **Preferido para automatizacion.** Determinista, no depende de seleccion ni de que editor esta activo |
| `bpy.ops` | Operadores (las "herramientas" de la UI) | Cuando no hay equivalente en datos (export, transform_apply, bake, mode_set) o replicas un flujo de usuario |
| `bpy.context` | Estado actual: objeto activo, seleccion, escena, modo | Leer que tiene el usuario seleccionado; en tools interactivas. **Es read-only** |

Hechos clave (doc oficial):

- Los data-blocks **no se instancian**: `bpy.types.Mesh()` lanza TypeError. Se crean/borran via las colecciones: `bpy.data.meshes.new(name="X")` / `bpy.data.meshes.remove(mesh)`.
- Las colecciones aceptan indice y string (`bpy.data.objects["Cube"]`), pero el indice puede cambiar durante la sesion — referencia por **nombre**, no por indice.
- `bpy.context` es de solo lectura: `bpy.context.active_object = obj` falla; `bpy.context.view_layer.objects.active = obj` funciona. Los miembros del context **cambian segun el editor** desde donde se ejecuta (el 3D Viewport tiene miembros que la consola no tiene).
- Los operadores **no aceptan data-blocks como argumentos** (operan sobre el context), devuelven solo `{'FINISHED'}` / `{'CANCELLED'}` (no el resultado), y su `poll()` puede fallar con `RuntimeError: Operator bpy.ops.X.poll() failed, context is incorrect`. Por eso son fragiles en headless.
- Guardas anti-fragilidad con `bpy.ops`:

```python
if bpy.ops.view3d.render_border.poll():   # comprobar antes de llamar
    bpy.ops.view3d.render_border()

# Override de contexto (desde 3.2; el dict-override viejo se ELIMINO en 4.0):
with bpy.context.temp_override(selected_objects=[obj]) as override:
    override.logging_set(True)   # 5.0+: loguea que miembros del context se usan
    bpy.ops.object.delete()
```

- Custom properties: `obj["mi_prop"] = 42` en cualquier ID; solo tipos basicos (int/float/string/arrays/dict con claves string); se guardan en el .blend y sirven para metadata de pipeline (ej. marcar assets exportables). Limite duro de anidamiento: 1024 niveles (5.2).

## Gotchas que rompen scripts (doc oficial de Gotchas)

- **Datos desactualizados (stale data):** tras cambiar `obj.location`, `obj.matrix_world` NO se recalcula solo. Llama `bpy.context.view_layer.update()` antes de leer resultados dependientes (constraints, drivers, parenting).
- **Edit Mode tiene su propia copia de la malla:** `obj.data` esta desincronizado mientras el objeto esta en Edit Mode. Opciones: salir de Edit Mode antes (`bpy.ops.object.mode_set(mode='OBJECT')`), o trabajar sobre el edit-mesh con `bmesh.from_edit_mesh()`.
- **Tres vias de acceso a caras:** `mesh.polygons` (Object Mode, rigido, bueno para export), `mesh.loop_triangles` (solo lectura, para export triangulado), `bmesh.types.BMFace` (la mejor para crear/manipular geometria) [ver: edicion-malla].
- **Crashes por referencias muertas:** no guardes referencias Python a datos de Blender a traves de borrados, undo/redo o reallocaciones (agregar muchos items a una coleccion invalida referencias previas). Guarda **nombres o indices** y re-accede. Para localizar la linea que crashea: modulo `faulthandler`.
- **Threads de Python no soportados** para tocar datos de Blender. Para trabajo largo sin congelar la UI: modal operators, `bpy.app.timers` o `bpy.app.handlers`.
- **No se puede redibujar durante un script** (Blender queda bloqueado hasta que termina). El hack `bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)` existe pero esta oficialmente desaconsejado y sin garantias.
- Cambios de UI (`Window.workspace`, `Area.type`...) se aplican diferido, al siguiente redraw — el codigo inmediatamente posterior no los ve.

## Averiguar la API que no conoces (patron de descubrimiento)

1. **Hazlo a mano una vez en la UI** y lee el Info editor: cada accion queda como linea `bpy.ops.*` con sus argumentos reales. Copia y parametriza.
2. **Tooltip / Copy Data Path** para propiedades: te da la ruta exacta desde el ID (`bpy.context.active_object.` + ruta copiada).
3. **Consola Python** (editor propio, con historial): autocompletado con `Tab` — la herramienta #1 de exploracion (`bpy.data.` + Tab lista todo). `C` y `D` son alias de `bpy.context` y `bpy.data`. **Copy as Script** (`Shift-Ctrl-C` en la consola) vuelca la sesion entera como script reutilizable.
4. **docs.blender.org/api/current/**: cubre `bpy.types` (lo que ves via `bpy.context`/`bpy.data`). Como leerla: cada pagina de tipo lista propiedades y al final una seccion **References** con desde donde se accede ese tipo — asi se compone la ruta (ej. de `Texture.contrast` subes por references hasta `tool_settings.sculpt.brush.texture.contrast`). `bpy.data` aparece documentado como `bpy.types.BlendData` (es una instancia). `bmesh`, `mathutils`, `gpu`, `aud` tienen docs aparte en el mismo sitio.
5. **Operator Cheat Sheet** (con Developer Extras): genera la lista completa de operadores con sus defaults en sintaxis Python.
6. Los scripts que trae Blender son la mejor referencia de estilo real: `scripts/startup/bl_ui` (interfaz) y `scripts/startup/bl_operators` (operadores).

## Automatizar lo repetitivo: patrones listos

**Renombrar en lote (solo bpy.data, cero contexto):**

```python
import bpy
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        obj.name = "SM_" + obj.name.removeprefix("SM_")
        obj.data.name = obj.name  # el data-block de malla, con el mismo nombre
```

**Aplicar rotacion/escala a todas las mallas (operador ⇒ preparar seleccion + activo):**

```python
import bpy
if bpy.context.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')
meshes = [o for o in bpy.context.view_layer.objects if o.type == 'MESH']
for obj in bpy.context.view_layer.objects:
    obj.select_set(obj in meshes)
if meshes:
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
```

**Export batch por coleccion a .glb** (parametros verificados contra Blender 5.2.0 LTS; el exportador acepta `collection="Nombre"` como fuente directa, sin tocar la seleccion) [ver: import-export]:

```python
import bpy, os
out = bpy.path.abspath("//export")  # carpeta junto al .blend
os.makedirs(out, exist_ok=True)
for col in bpy.data.collections:
    if col.name.startswith("EXPORT_"):
        bpy.ops.export_scene.gltf(
            filepath=os.path.join(out, col.name.removeprefix("EXPORT_") + ".glb"),
            export_format='GLB',
            collection=col.name,   # exporta SOLO esa coleccion
            export_apply=True,     # aplica modificadores
        )
```

(FBX equivalente: `bpy.ops.export_scene.fbx(..., collection=col.name)`; tambien tiene `batch_mode='COLLECTION'` para partir automatico.)

- **Cuidado con `export_apply=True`:** aplica modifiers (menos Armature) a costa de excluir shape keys del export — si el asset tiene shape keys, no uses `export_apply` (deja los modifiers ya aplicados en la malla antes, o exporta sin aplicar).

**Validar escala/normales antes de exportar (QA de assets):**

```python
import bpy
for obj in bpy.data.objects:
    if obj.type != 'MESH':
        continue
    if any(abs(s - 1.0) > 1e-6 for s in obj.scale):
        print(f"[ESCALA] {obj.name}: scale={tuple(obj.scale)} sin aplicar")
    if obj.matrix_world.determinant() < 0:
        print(f"[NEGATIVA] {obj.name}: escala negativa -> normales invertidas al exportar")
    if obj.data.validate():   # True = habia datos invalidos (y los corrigio)
        print(f"[GEOMETRIA] {obj.name}: mesh.validate() corrigio datos invalidos")
```

## Text Editor, consola y scripts externos

| Herramienta | Para que | Claves |
|---|---|---|
| Workspace **Scripting** | Todo junto: Text Editor + consola + Info editor | Pestaña del Topbar |
| **Text Editor** | Scripts multi-linea, addons en desarrollo | **Run Script** = `Alt-P`. Menu **Templates ‣ Python** trae ejemplos oficiales (operador, panel, modal, addon...) |
| **Consola Python** | Exploracion y one-liners | Autocomplete `Tab`, historial, `Copy as Script` |
| Terminal del sistema | Ver `print()` y tracebacks completos; `Ctrl-C` mata un script colgado | Lanza Blender DESDE una terminal cuando desarrolles |
| Editor externo / IDE | Proyectos serios | Stub de 2 lineas en el Text Editor: `filename = "/ruta/script.py"; exec(compile(open(filename).read(), filename, 'exec'))` — o importar como modulo con `importlib.reload(myscript)` en cada corrida |

## Escribir un addon minimo

Un addon es solo un modulo Python con `register()`/`unregister()` (lo unico que Blender llama). Formato clasico (**legacy**, con `bl_info`) — sigue soportado en 5.x pero esta **deprecated** desde 4.2:

```python
bl_info = {"name": "Move X Axis", "blender": (2, 80, 0), "category": "Object"}
import bpy

class ObjectMoveX(bpy.types.Operator):
    """My Object Moving Script"""          # tooltip
    bl_idname = "object.move_x"            # id unico -> bpy.ops.object.move_x()
    bl_label = "Move X by One"             # nombre visible (y en busqueda F3)
    bl_options = {'REGISTER', 'UNDO'}      # aparece en Info editor + soporta undo

    def execute(self, context):
        for obj in context.scene.objects:
            obj.location.x += 1.0
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(ObjectMoveX.bl_idname)

def register():
    bpy.utils.register_class(ObjectMoveX)
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    bpy.utils.unregister_class(ObjectMoveX)

if __name__ == "__main__":
    register()   # permite probarlo con Run Script sin instalar
```

- Paneles: subclase de `bpy.types.Panel` con `bl_space_type`/`bl_region_type`/`bl_context` y metodo `draw()`. Props persistentes: `bpy.props.*` dentro de `PropertyGroup`.
- Desde Python se pueden definir: operadores, paneles, menus, keymaps, property groups, render engines (`bpy.types.RenderEngine`). **No** se pueden definir tipos nuevos de modificador, objeto o nodo shader (eso exige C/C++; para "modificadores custom" la via practica es Geometry Nodes [ver: geometry-nodes]).
- **Formato actual (4.2+): Extension.** El `bl_info` se sustituye por un `blender_manifest.toml` junto al `__init__.py` (campos minimos: `schema_version`, `id`, `version`, `name`, `tagline`, `maintainer`, `type = "add-on"`, `blender_version_min`, `license`). El paquete se arma con `blender --command extension build` (y `... extension validate` para chequear). Imports internos **relativos** (`from . import utils`) y preferencias con `bl_idname = __package__` (el modulo real pasa a llamarse `bl_ext.<repo>.<id>`).
- **Instalar:** Preferences ‣ Add-ons — "Install from Disk" para extensiones (.zip) y "Install legacy Add-on" para .py sueltos. Rutas reales de instalacion: `import addon_utils; print(addon_utils.paths())`. Dependencias de terceros: se empaquetan como **wheels** en el manifest, nunca pip al Python del sistema [ver: addons-ecosistema].
- Un addon que necesite escribir en disco usa `bpy.utils.extension_path_user(__package__, create=True)`, no su propio directorio.

## Headless: la base de la automatizacion por agente

```bash
blender --background archivo.blend --python script.py
blender -b --python-expr "import bpy; print(len(bpy.data.objects))"
blender -b archivo.blend --python export.py -- --preset juego   # tras "--", args libres via sys.argv
```

| Flag | Efecto |
|---|---|
| `-b`, `--background` | Sin UI (el modo del agente; audio desactivado por defecto) |
| `-P`, `--python <file>` | Ejecuta un script .py |
| `--python-expr "<code>"` | Ejecuta una expresion/script inline (puede ser multi-linea) |
| `--python-exit-code <n>` | Exit code 1-255 si el script lanza excepcion — **imprescindible en CI**; sin esto Blender sale con 0 aunque tu script reviente |
| `--factory-startup` | Ignora startup.blend y preferencias del usuario (corridas reproducibles) |
| `--addons a,b,c` | Habilita addons extra (lista separada por comas, sin espacios) |
| `--python-console` | REPL interactivo en terminal |
| `--debug-wm` | Loguea todos los operadores ejecutados |
| `--log-level <nivel>` | fatal/error/warning/info/debug/trace |
| `--` | Fin de opciones de Blender; el resto llega intacto a `sys.argv` |

- **El orden de los argumentos importa** (se ejecutan en secuencia): `blender --background test.blend --render-output /tmp --render-frame 1` funciona; poner `--render-frame` antes del output o el output antes del .blend, no. Mismo principio con `--python`: el .blend se carga ANTES del script.
- 5.2+: en background el GPU no se inicializa; si el script necesita el modulo `gpu`, llamar `gpu.init()` (nuevo en 5.2).
- El formato del log de background **cambio en 5.0** — parsers de render farms viejos pueden romperse.
- **Alternativa: `pip install bpy`** (modulo precompilado oficial). Equivale a `--background --factory-startup`; arranca con la escena default (cubo+camara+luz — usa `bpy.ops.wm.read_factory_settings(use_empty=True)` para vacio); un solo .blend a la vez; `import bpy` siempre antes que `mathutils`/`gpu`; no soporta `importlib.reload`. Util para pipelines Python puros; para operar el Blender real del proyecto, mejor el binario [ver: blender-mcp-operativo].

## Scripts viejos en 5.x: cambios que rompen (verificados en release notes oficiales)

| Cambio | Antes (2.8–4.x) | En 5.x |
|---|---|---|
| Override de contexto | `bpy.ops.x(ctx_dict)` | Eliminado en **4.0** → `context.temp_override(...)` |
| Addons | `bl_info` + Install | Deprecated desde **4.2** → Extensions con `blender_manifest.toml` |
| Props de addon via dict | `scene['cycles']`, `obj['mi_addon']['x']` | **5.0**: props de `bpy.props` ya NO son accesibles como custom properties (storage separado) |
| Compositor | `scene.use_nodes = True`; `scene.node_tree` | **5.0**: `scene.node_tree` eliminado → `scene.compositing_node_group`; `use_nodes` (scene/material/world) deprecated, siempre True |
| Acciones | `action.fcurves`, `action.groups`, `action.id_root` | **5.0**: eliminados → slots + channelbag (`bpy_extras.anim_utils.action_ensure_channelbag_for_slot()`) |
| EEVEE id | `BLENDER_EEVEE_NEXT` (4.2-4.5) | **5.0**: vuelve a ser `BLENDER_EEVEE` |
| Brushes | `brush.sculpt_tool` | **5.0**: `brush.sculpt_brush_type` (sufijo `_tool` → `_brush_type`) |
| Grease Pencil | `bpy.data.grease_pencils_v3` / `GreasePencilv3` | **5.0**: `bpy.data.grease_pencils` / `GreasePencil`; lo viejo `grease_pencils` ahora son Annotations |
| BGL | modulo `bgl` deprecated | **5.0**: eliminado → modulo `gpu` |
| Modifier de Geometry Nodes | `modifier["identifier"] = 5.0` | **5.2**: `modifier.properties.inputs.identifier.value = 5.0` (RNA de verdad) |
| Python bundled | 3.11 | **5.1**: Python 3.13 (VFX Platform 2026) |
| mathutils | Vector interno float64 | **5.0**: buffer protocol nativo, float32 |

Regla operativa: cualquier snippet de internet anterior a 2024 se asume roto hasta probarlo; la fuente de verdad es `docs.blender.org/api/current/` + las release notes de 5.x [ver: blender5-actualidad].

## Modificar Blender de verdad: los niveles

| Nivel | Cubre | Costo |
|---|---|---|
| 1. Script suelto / MCP | Automatizacion, QA, export batch | Minutos |
| 2. Addon/Extension | Tools con UI, integrarse al flujo del artista | Horas |
| 3. `pip install bpy` | Blender dentro de pipelines Python externos | Facil |
| 4. Fork del C/C++ | Tipos nuevos de nodo/modificador/space, cambios de core | **Casi nunca se justifica** |

- El 99% de las necesidades de un estudio de juegos vive en niveles 1-2. El nivel 4 solo cuando la API Python no expone lo que necesitas Y Geometry Nodes tampoco lo resuelve.
- **Compilar Blender** (concepto): es open source (GPL, repo en `projects.blender.org`). Build con **CMake**; el wrapper `make` del repo automatiza todo: `make update` (codigo + libs precompiladas), `make` (binario en `../build_<plataforma>/bin`), `make test`. Compiladores oficiales actuales: GCC 14.2 (Linux), Xcode 26 (macOS), MSVC 2022 (Windows). Para depurar crashes de scripts existe la build option `WITH_PYTHON_SAFETY` ("Enable internal API error checking to track invalid data to prevent crash on access", a costa de eficiencia — solo para desarrollo, `OFF` por defecto).
- **Contribuir upstream:** pull requests en projects.blender.org (Gitea). Requisitos: aceptar el contributor agreement (una vez), commits con el style guide, un tema por PR, y para features hablar ANTES con los developers del modulo (design task primero). Los reviewers finales son los module owners. Fixes pequeños: PR directo.

## Reglas practicas

1. `bpy.data` primero; `bpy.ops` solo cuando no hay via de datos (export, apply, bake, mode_set).
2. Antes de un `bpy.ops` dudoso: `bpy.ops.X.poll()` y, si el contexto no cuadra, `context.temp_override(...)`.
3. Referencia data-blocks por **nombre**, nunca guardes referencias Python a traves de borrados/undo.
4. Tras mutar transforms/relaciones y antes de leer `matrix_world`: `bpy.context.view_layer.update()`.
5. Asegura `mode='OBJECT'` antes de tocar `obj.data` o exportar; en Edit Mode usa `bmesh.from_edit_mesh()`.
6. Headless siempre con `--factory-startup` (reproducible) y `--python-exit-code 1` (CI honesta).
7. El orden de flags de CLI es de ejecucion: `.blend` primero, luego settings, luego la accion.
8. Para descubrir API: accion manual → Info editor → copiar; propiedad → tooltip / Copy Data Path; explorar → consola con `Tab`.
9. Activa Developer Extras + Python Tooltips en cualquier Blender donde trabajes.
10. Nombres de operador vienen del tooltip, del Info editor o de docs — **jamas inventados de memoria**.
11. Scripts de terceros: comprueba la fecha; si es pre-4.2, audita contra la tabla de cambios de arriba antes de correrlo.
12. Addons nuevos: formato Extension (`blender_manifest.toml`), imports relativos, `__package__` para prefs, wheels para dependencias.
13. Lanza Blender desde terminal cuando desarrolles: ahi viven los `print()` y los tracebacks.
14. Loops largos: nunca bloquees la UI; timers/modal, o directamente headless.
15. Custom properties (`obj["clave"]`) para metadata de pipeline: sobreviven al guardado y viajan con el objeto.
16. Un script que "termino sin error" no es evidencia: imprime conteos/resultados y verifica el output (archivo exportado existe, tamaño > 0).

## Errores comunes

| Pitfall | Antidoto |
|---|---|
| `poll() failed, context is incorrect` en headless | Ese operador exige un area/modo concreto: usa `temp_override`, o mejor busca la via `bpy.data`. Con `override.logging_set(True)` (5.0+) ves que miembros pide |
| Script corre en la consola pero no via MCP/headless | Dependencia oculta del context (seleccion, area activa). Reescribe contra `bpy.data` y pasa objetos explicitos |
| Crash de Blender al iterar y borrar a la vez | Recolecta nombres primero, borra despues; nunca mutar la coleccion que iteras |
| `obj.data` "ignora" los cambios del usuario | Estaba en Edit Mode: los datos viven en el edit-mesh hasta salir del modo |
| `matrix_world` viejo tras mover el objeto | Falta `view_layer.update()` |
| Export .glb vacio o incompleto | El exportador respeta filtros (`use_selection`, `collection`); verifica que pasaste la fuente correcta y que los objetos no estan ocultos al render |
| CI en verde con script roto | Blender devuelve exit 0 por defecto ante excepciones Python: usa `--python-exit-code 1` |
| Addon funciona instalado pero no con Run Script (o al reves) | `bl_info`/manifest solo aplican instalado; `if __name__ == "__main__": register()` es lo que permite probar con Run Script |
| `bpy.context.active_object = X` lanza AttributeError | Context es read-only: `bpy.context.view_layer.objects.active = X` |
| Copiar snippet 2.8-4.x y que "no exista" el atributo | Renombrado en 5.x (tabla de arriba); busca el nombre nuevo en docs/api/current o con `Tab` en la consola |
| `import bpy` falla en pip-bpy tras importar mathutils | Orden: `bpy` siempre primero |
| Modulo `gpu` falla en `--background` | 5.2+: llama `gpu.init()` antes |

## Fuentes

- **Quickstart, API Overview, API Reference Usage, Tips and Tricks, Gotchas (+subpaginas de operators/meshes/crashes/threading/internal data), Blender as a Python Module** — docs.blender.org/api/current (doc oficial de la API, version current = 5.x) — la base de todo el modelo bpy.data/ops/context, gotchas y patrones de descubrimiento.
- **Manual oficial: Command Line Arguments + Extension Arguments** — docs.blender.org/manual — flags exactos de headless y `--command extension build/validate`.
- **Manual oficial: Info Editor / Python Console / Text Editor** — docs.blender.org/manual/editors — grabacion de operadores, autocomplete `Tab`, `Alt-P`, Templates.
- **Manual oficial: Preferences ‣ Interface** — docs.blender.org/manual — definicion exacta de Developer Extras y Python Tooltips.
- **Manual oficial: Add-on Tutorial (advanced/scripting)** — estructura del addon legacy, instalacion, `addon_utils.paths()`.
- **Manual oficial: Extensions — Getting Started + Add-ons** — docs.blender.org/manual/advanced/extensions — manifest TOML, legacy vs extension, `__package__`, wheels.
- **Release notes oficiales Python API 4.0, 5.0, 5.1 y 5.2** — developer.blender.org/docs/release_notes — cada cambio de la tabla de breaking changes, con fechas: 5.0 (18-nov-2025), 5.2 LTS (14-jul-2026).
- **Developer Handbook: Building Blender + Contributing Code** — developer.blender.org/docs/handbook — CMake/make wrapper, compiladores, proceso de PR y contributor agreement.
- **Dump de parametros de `export_scene.gltf` / `export_scene.fbx` generado en Blender 5.2.0 LTS local** — verificacion directa en el binario de los argumentos usados en los snippets de export (`collection`, `export_apply`, `batch_mode`).
