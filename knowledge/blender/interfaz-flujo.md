# Interfaz y modelo mental de Blender

> **Cuando cargar este archivo:** antes de operar Blender por primera vez en una sesión (via MCP o headless) o siempre que haya que navegar la UI, seleccionar, transformar, snapear o configurar la escena/preferencias. Es el mapa base de LA HERRAMIENTA; la teoría de modelado vive en [ver: modelado/fundamentos-3d] y la edición de malla profunda en [ver: edicion-malla].

## 1. Versión: Blender 5.x (este stack: 5.2 LTS)

| Versión | Fecha | Nota |
|---|---|---|
| 5.0 | 18-nov-2025 | Salto mayor desde 4.5 LTS; rompe themes custom, cambia I/O |
| 5.1 | 17-mar-2026 | VFX Platform 2026: Python **3.13** embebido |
| **5.2 LTS** | 14-jul-2026 | Soporte hasta **julio 2028**. La que asume esta base |

Cambios 4.x → 5.x que invalidan contenido web viejo (verificados en release notes oficiales):

- **FBX**: el importador C++ es el default; `bpy.ops.import_scene.fbx` quedó legacy → usar `bpy.ops.wm.fbx_import` (5.0). **Collada (.dae) fue ELIMINADO** en 5.0 [ver: import-export].
- **6 modificadores nuevos basados en Geometry Nodes** (5.0): Array, Scatter on Surface, Instance on Elements, Randomize Instances, Curve to Tube, Geometry Input. El Array legacy sigue disponible [ver: modificadores].
- **UV sync selection activo por defecto** y selección UV compartida entre todos los UV maps (5.0).
- El solver "Fast" de booleans se renombró a **"Float"** (operador, modificador y API) (5.0).
- Themes: sistema reescrito en 5.0 (300+ settings eliminados) — themes de 4.5 se rompen.
- Nombres de data-blocks ahora hasta **255 bytes** (antes 63); compresión de .blend activada por defecto (5.0).
- "Full Screen Area" ahora se llama **"Focus Mode"**; menús y popups quedan abiertos hasta hacer clic (hay preferencia para el comportamiento viejo) (5.0).
- Búsqueda dentro de Preferences (5.1); tabs del Sidebar siempre visibles (5.2).
- Headless: logging unificado — `--log-level info|debug|trace` reemplaza a `--verbose` (5.0) [ver: bpy-scripting].

Detalle de la serie 5.x en [ver: blender5-actualidad]. Si un tutorial dice 2.8–4.x: verificar contra docs.blender.org antes de replicar.

## 2. El modelo mental de datos

Jerarquía: **Escena → Colecciones → Objetos → Object Data**. Todo es un **data-block** (mesh, object, material, image, action, collection, workspace…): nombres únicos por tipo dentro del .blend, se referencian entre sí, se pueden linkear entre archivos.

| Nivel | Qué es | Clave operativa |
|---|---|---|
| Scene | Contenedor top-level (unidades, cámara activa, frame range) | Un .blend puede tener varias escenas |
| Collection | Agrupación lógica SIN transform (no es un parent) | Unidad de organización, visibilidad, export e instancing [ver: organizacion-blend] |
| Object | Transform (loc/rot/scale) + origen + referencia a su data | Lo que se mueve en Object Mode |
| Object Data | La malla en sí (Mesh), curva, armature… | **Compartible entre objetos** (instancias reales) |

- **Object ≠ Mesh**: `Shift`-`D` (Duplicate) copia la malla pero LINKEA materiales; `Alt`-`D` (Duplicate Linked) comparte la malla — editar una edita todas. Qué se copia/linkea al duplicar es configurable en Preferences.
- **Apply transforms** (`Ctrl`-`A` → Location/Rotation/Scale) transfiere el transform a la geometría y resetea a 0/0/1. Si la data es compartida, Blender exige hacerla **Single User** primero. Aplicar rotation & scale antes de exportar es regla de oro [ver: import-export].
- **Origen del objeto**: `Object ‣ Set Origin` (Geometry to Origin / Origin to Geometry / Origin to 3D Cursor / Origin to Center of Mass). El origen ES el pivot que ve el engine [ver: pipeline/arte-a-unity].
- Colecciones: `M` Move to Collection, `Shift`-`M` Link to Collection (un objeto puede vivir en varias), `Ctrl`-`G` crea colección nueva. Cada colección tiene panel **Exporters** (re-export repetible a glTF/OBJ/USD/FBX Legacy/PLY/Alembic) — oro para pipeline de juego.

## 3. Object Mode vs Edit Mode (y los demás modos)

| Modo | Qué edita | Entrada |
|---|---|---|
| Object Mode | Posición/rotación/escala de objetos, duplicar, parenting, modificadores | default |
| Edit Mode | La geometría (vértices/edges/caras; control points en curvas) | `Tab` |
| Sculpt Mode | Forma por brushes (solo meshes) [ver: sculpt] | `Ctrl`-`Tab` pie |
| Vertex/Weight/Texture Paint | Vertex colors / pesos / texturas | `Ctrl`-`Tab` pie |
| Pose Mode | Posado de armatures | `Ctrl`-`Tab` en armature |

- `Ctrl`-`Tab` abre el **pie menu de modos** (en armatures alterna Object/Pose directamente).
- El modo cambia header, Toolbar, atajos y hasta qué editores funcionan (el UV Editor solo muestra UVs con el viewport en Edit Mode).
- **Multi-object editing**: seleccionar varios objetos y entrar a Edit/Pose los edita juntos (no se pueden crear edges entre objetos; Properties solo muestra la data del activo).
- `Alt`-`Q` cambia al objeto bajo el cursor SIN salir del modo (o clic en el punto junto al objeto en el Outliner).
- Lo que se hace en Edit Mode se "hornea" en la malla; lo de Object Mode queda en el transform. Un scale ≠ 1.0 en Object Mode es una bomba de tiempo para export y modificadores.

## 4. Workspaces y editores

Workspaces = layouts predefinidos de áreas, guardados EN el .blend (al abrir, "Load UI" decide si usar los del archivo). Los que importan para asset de juego: **Layout** (general), **Modeling**, **UV Editing**, **Texture Paint**, **Shading** [ver: materiales-preview], **Geometry Nodes** [ver: geometry-nodes], **Scripting** [ver: bpy-scripting]. `Ctrl`-`PageUp`/`PageDown` cambia de workspace.

Editores esenciales (cualquier área puede mostrar cualquier editor, selector en la esquina del header):

| Editor | Para qué |
|---|---|
| 3D Viewport | Modelar, transformar, todo. Toolbar `T`, Sidebar `N` (Item: transform numérico; View: 3D Cursor) |
| Outliner | Árbol escena/colecciones/objetos; visibilidad (ojo), selectabilidad, render; modo "Blend File" para ver TODOS los data-blocks |
| Properties | Tabs por contexto: Render, Output, Scene (**Units**), Object, Modifiers, Object Data, Material |
| UV Editor | UVs (con el 3D Viewport en Edit Mode) |
| Shader Editor | Materiales por nodos |
| Spreadsheet | Valores crudos de atributos/geometría — verificación real para un agente |
| Python Console / Info | Probar bpy en vivo; Info muestra el Python de cada acción de UI |
| Asset Browser | Librerías de assets marcados |

## 5. Atajos esenciales (default keymap)

Los ~30 que cubren el 90% (todos verificados en el manual 5.2). Existe también el keymap "Industry Compatible" — esta base asume SIEMPRE el default.

| Atajo | Acción |
|---|---|
| `G` / `R` / `S` | Move / Rotate / Scale (modal) |
| `X`,`Y`,`Z` en transform | Bloquear a eje (2ª vez: alterna Global↔Local); `Shift`-`X` = plano SIN X |
| números en transform | Valor exacto: `G` `Z` `2` `Return` mueve 2 m en Z |
| `Tab` / `Ctrl`-`Tab` | Edit Mode / pie de modos |
| `1` `2` `3` (Edit) | Vertex/Edge/Face select (`Shift` acumula modos, `Ctrl` expande/contrae selección) |
| `A` / `Alt`-`A` / `Ctrl`-`I` | Todo / nada / invertir |
| `B` / `C` / `W` | Box / Circle select / ciclar herramientas de selección (Tweak→Box→Circle→Lasso) |
| `L` (hover) / `Ctrl`-`L` / `Shift`-`L` | Select Linked (isla conectada) / desde selección / deselect |
| `Alt`-`LMB` / `Ctrl`-`Alt`-`LMB` | Edge loop / edge ring |
| `Shift`-`D` / `Alt`-`D` | Duplicar / duplicar linkeado (comparte malla) |
| `X` o `Delete` | Borrar (X pide menú/confirmación) |
| `Shift`-`A` | Menú Add (el objeto nuevo aparece en el 3D Cursor) |
| `E` / `I` / `F` | Extrude Region / Inset Faces / New Edge/Face from Vertices |
| `Ctrl`-`B` / `Shift`-`Ctrl`-`B` | Bevel edges / bevel vertices |
| `Ctrl`-`R` / `K` | Loop Cut and Slide / Knife |
| `M` | Object Mode: Move to Collection · Edit Mode: **Merge** — ojo al contexto |
| `P` / `Ctrl`-`J` | Separate (Edit) / Join objetos (Object) |
| `Ctrl`-`A` | Apply (Location/Rotation/Scale) |
| `Alt`-`G` / `Alt`-`R` / `Alt`-`S` | Limpiar location / rotation / scale |
| `Ctrl`-`P` / `Alt`-`P` | Parent / clear parent |
| `H` / `Shift`-`H` / `Alt`-`H` | Ocultar / ocultar lo NO seleccionado / revelar |
| `Numpad1`/`3`/`7` (+`Ctrl` opuesta, +`Shift` eje local) | Vistas Front/Right/Top |
| `Numpad5` / `Numpad0` | Orto↔perspectiva / vista de cámara |
| `NumpadSlash` | Local View (aislar selección) |
| `Home` / `NumpadPeriod` | Frame All / Frame Selected |
| `Z` / `Shift`-`Z` / `Alt`-`Z` | Pie de shading / toggle Wireframe / X-Ray |
| `O` | Proportional Editing |
| `Shift`-`S` | Pie/menú Snap (cursor↔selección) |
| `Period` / `Comma` | Pie de Pivot Point / de Transform Orientation |
| `Shift`-`Tab` / `Ctrl` (hold) | Toggle snapping / snapping temporal durante transform |
| `F2` / `F3` / `F9` | Renombrar / **buscar CUALQUIER operador por nombre** / reabrir Adjust Last Operation |
| `Ctrl`-`Z` / `Shift`-`Ctrl`-`Z` | Undo / Redo |

Otros pies: `AccentGrave` = navegación de vista; `Alt`-`W` = fallback tool; `Q` = Quick Favorites (personalizable via clic derecho en cualquier operador); `Shift`-`Spacebar` = toolbar popup.

Durante cualquier transform modal: `Ctrl` = snap a incrementos, `Shift` = precisión fina, `Shift`-`Ctrl` = incrementos finos, `RMB`/`Esc` = cancelar, `MMB` = elegir eje moviendo el mouse.

**F3 es el salvavidas del agente**: si no se sabe el atajo, `F3` busca el operador por su nombre exacto de menú (Menu Search). Hover + `Ctrl`-`C` sobre cualquier botón copia su comando Python — puente directo de UI a bpy [ver: blender-mcp-operativo].

## 6. Selección en Edit Mode

- **Modos** `1`/`2`/`3` (vertex/edge/face). Subir de modo (vertex→face) conserva solo elementos completos; bajar conserva todo. `Ctrl` al subir EXPANDE (incluye parciales).
- **Loops y rings**: `Alt`-`LMB` edge loop (línea topológicamente recta); `Ctrl`-`Alt`-`LMB` edge ring (paralelas cruzando la face row). En Face mode `Alt`-`LMB` sobre un edge selecciona el face loop perpendicular. `Shift`+ cualquiera acumula. Doble clic en un edge loop cuando Emulate 3 Button Mouse rompe `Alt`-`LMB`.
- **Select Linked**: `L` con hover selecciona la isla conectada (delimitable por Seam/Sharp/Material/UVs/Normal); `Ctrl`-`L` desde la selección actual.
- **Shortest Path**: `Ctrl`-`LMB` entre dos elementos — sirve además para marcar seams/sharp/crease en cadena (opción Edge Tag).
- Menú Select: Select Similar `Shift`-`G`, Checker Deselect, More/Less `Ctrl`-`NumpadPlus`/`NumpadMinus`, Select All by Trait (**non-manifold, loose geometry** — auditoría de malla rota [ver: modelado/fundamentos-3d]), Select Loops ‣ Boundary Loops.
- **X-Ray** (`Alt`-`Z`): sin él, box/circle/lasso solo toman lo VISIBLE — para seleccionar "a través" del mesh, activarlo primero. En mallas densas sin X-Ray, la selección por región puede saltarse vértices ocultos (limitación documentada).

## 7. Transformaciones: pivots y orientaciones

**Pivot Point** (`Period`): decide el centro de R y S.

| Pivot | Uso típico |
|---|---|
| Median Point (default) | Centro promedio de la selección |
| 3D Cursor | Rotar/escalar alrededor de un punto arbitrario colocado a propósito |
| Individual Origins | Escalar/rotar N caras u objetos CADA UNO sobre su propio centro (insets masivos, shrink de caras) |
| Active Element | Pivotar sobre el último seleccionado |
| Bounding Box Center | Centro del bounding box |

**Transform Orientation** (`Comma`): Global, Local, **Normal** (Z = normal de la selección en Edit Mode — mover una cara "hacia afuera" = `G` `Z` `Z` o Normal), Gimbal, View, Cursor, Parent. Se pueden crear **custom orientations** (botón "+" del panel) desde un objeto o cara — imprescindible para trabajar sobre superficies inclinadas.

## 8. El 3D Cursor: herramienta seria, no estorbo

Tiene **posición Y rotación**. Es: punto de aparición de todo `Shift`-`A`, pivot opcional, orientación de transform opcional, y centro de tools como Spin/Bend/Mirror.

- Colocarlo: `Shift`-`RMB` (rápido); tool Cursor del Toolbar (con opción de alinearse a la normal de la superficie); numéricamente en Sidebar `N` ‣ View ‣ 3D Cursor.
- Con precisión via `Shift`-`S`: **Cursor to Selected / Cursor to Active / Cursor to World Origin / Cursor to Grid**, y de vuelta **Selection to Cursor** (con u sin offset).
- Patrón estrella (origen de pivot para juego): seleccionar el vértice/cara donde debe ir el pivot → `Shift`-`S` Cursor to Selected → Object Mode → `Object ‣ Set Origin ‣ Origin to 3D Cursor` [ver: pipeline/arte-a-unity].
- `Shift`-`C` = Center Cursor and Frame All (resetea cursor al origen del mundo y encuadra todo).

## 9. Snapping

Toggle `Shift`-`Tab`; **`Ctrl` mantenido = snap temporal** durante el transform (lo más usado). Config en el imán del header:

| Concepto | Opciones | Nota |
|---|---|---|
| Snap Base (qué punto de MI selección) | Closest / Center / Median / Active | Center usa el pivot — combinado con 3D Cursor da control total |
| Snap Target (a qué) | Increment / Grid / **Vertex** / Edge / **Face** / Volume / Edge Center / Edge Perpendicular / Face Center | Face = retopología; se combinan varios con `Shift`-`LMB` |
| Individual | Face Project / Face Nearest | Proyectar cada vértice sobre otra superficie (conformar una pieza a otra) |
| Affect | Move / Rotate / Scale | Por defecto solo Move |
| Extra | Align Rotation to Target, Backface Culling, Absolute Grid Snap | Align Rotation orienta el Z de la pieza a la normal del target — colocar props sobre terreno |

Increment snapea en pasos del grid RELATIVOS a la posición inicial; Absolute Grid Snap ancla AL grid — para kits modulares se quiere absoluto [ver: modelado/entornos-modulares].

## 10. Unidades y escala: metrico 1.0 desde el minuto cero

`Properties ‣ Scene ‣ Units`: **Unit System = Metric, Unit Scale = 1.0, Length = Metros** (1 unidad Blender = 1 m, la convención que espera el pipeline a Unity [ver: import-export]).

- **Unit Scale solo cambia la VISUALIZACIÓN** de los números, no el comportamiento interno (las físicas lo ignoran — documentado). No usarlo para "arreglar" escala: modelar a tamaño real y punto.
- Rotation en Degrees. Los campos aceptan unidades tipeadas: `25cm`, `3'`.
- El daño de escala típico no viene de Units sino de **scale ≠ 1.0 en el objeto**: verificar con `N` ‣ Item y aplicar `Ctrl`-`A` ‣ Rotation & Scale antes de exportar.

```python
import bpy
# Setup de escena game-ready (patrón para MCP/headless)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
scene.unit_settings.length_unit = 'METERS'
scene.unit_settings.system_rotation = 'DEGREES'
# Selección por modo en Edit Mode: (vertex, edge, face)
bpy.context.tool_settings.mesh_select_mode = (False, True, False)
```

## 11. Preferencias que importan para game dev (Edit ‣ Preferences)

| Sección | Ajuste | Por qué |
|---|---|---|
| Save & Load | **Auto Save** ON + Timer bajo (minutos) | Recuperación tras crash; guarda a la carpeta temporal |
| Save & Load | Save Versions ≥ 2 | Backups .blend1/.blend2 junto al archivo |
| System ‣ Memory & Limits | **Undo Steps** alto + Global Undo ON | Sesiones largas de modelado; Global Undo OFF rompe Adjust Last Operation |
| Navigation | **Orbit Around Selection** ON, **Zoom to Mouse Position** ON, Auto Depth ON | Navegación que no se pierde en assets chicos |
| Navigation | Auto Perspective ON (default) | Orto automática al alinear vista |
| Input | Emulate Numpad solo si el teclado no tiene numpad | Los números normales pasan a ser vistas y DEJAN de cambiar vertex/edge/face |
| Input | ⚠️ Emulate 3 Button Mouse rompe `Alt`-`LMB` (loops) | Preferir mouse real de 3 botones |
| System ‣ Network | Allow Online Access ON (si se usarán Extensions) | Sin esto no hay repositorio remoto |
| Interface | Developer Extras + Python Tooltips ON | Cada control muestra su path bpy en el tooltip — esencial para un agente que scriptea |

Guardar: las preferencias se auto-guardan (o "Save Preferences" del menú hamburguesa); la escena default se fija con `File ‣ Defaults ‣ Save Startup File` — dejar ahí units métricas y el layout preferido.

**Add-ons en 5.x**: solo quedan **5 bundled** documentados en el manual — **Node Wrangler** (activarlo YA: atajos de Shader Editor como Ctrl-Shift-clic para preview [ver: materiales-preview]), **Rigify**, **glTF 2.0** (activado por defecto), Manage UI Translations y VR Scene Inspection. Todo lo demás que los tutoriales viejos llaman "addon incluido" (LoopTools, F2, Extra Objects, Bool Tool…) vive ahora en **extensions.blender.org** (Preferences ‣ Get Extensions) [ver: addons-ecosistema]. Add-ons legacy (.py/.zip sueltos): Add-ons ‣ Install from Disk.

## Reglas prácticas

1. Al abrir un .blend ajeno o nuevo: verificar `Scene ‣ Units` (Metric, 1.0, metros) ANTES de modelar nada.
2. Escena default propia con units + autosave + undo alto guardada via `File ‣ Defaults ‣ Save Startup File`.
3. Todo objeto entregable: rotation 0,0,0 y scale 1,1,1 (aplicar con `Ctrl`-`A`) y origen puesto a propósito (3D Cursor + Set Origin).
4. `Alt`-`D` para instancias que deben seguir juntas; `Shift`-`D` para copias independientes — decidir SIEMPRE cuál de las dos.
5. Antes de aplicar transform o modificador: comprobar si la malla es multiusuario (número junto al nombre de la data) — aplicar exige Single User.
6. Organizar en colecciones por función (geo/ref/helpers) desde el principio; `M` para mover, nunca dejar todo en Scene Collection [ver: organizacion-blend].
7. No saber el operador = `F3` y buscarlo por nombre; nunca inventar un atajo.
8. Hover + `Ctrl`-`C` sobre un botón para capturar su comando Python exacto antes de scriptearlo.
9. Seleccionar a través del mesh: activar X-Ray (`Alt`-`Z`) primero; si no, box select solo toma lo visible.
10. Loops con `Alt`-`LMB`, rings con `Ctrl`-`Alt`-`LMB`, islas con `L` — antes de seleccionar cara por cara, pensar cuál de los tres resuelve.
11. Pivot de trabajo: `Period` y elegir; para rotar alrededor de un punto exacto, 3D Cursor colocado con `Shift`-`S` ‣ Cursor to Selected.
12. Mover "hacia afuera" de una cara = orientación Normal (`G` `Z` `Z`), no adivinar con Global.
13. Snapping para ensamblar: `Ctrl` mantenido + Snap Target Vertex; para retopo/conformar: Face o Face Project.
14. Kits modulares: Absolute Grid Snap, no Increment [ver: modelado/entornos-modulares].
15. Valores exactos siempre tipeados (`G` `X` `1.5`) o en Sidebar `N` ‣ Item — nunca "a ojo" para trabajo de precisión.
16. Tras cada operación modal revisar el panel **Adjust Last Operation** (`F9`): ahí están las opciones que la mayoría olvida (segmentos del bevel, Centroid del merge…).
17. Verificar geometría con Statistics overlay o el Spreadsheet, no con la impresión visual.
18. En 5.x: exportar/importar FBX con el path nuevo (`bpy.ops.wm.fbx_import` / los export de siempre) y jamás depender de Collada.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Modelar con scale ≠ 1 en Object Mode y "verse bien" hasta el export | `N` ‣ Item para auditar; `Ctrl`-`A` ‣ Rotation & Scale antes de bevel/modificadores/export |
| Subir Unit Scale para "agrandar" la escena | Unit Scale es solo display (físicas lo ignoran); modelar a tamaño real en metros |
| Editar una malla y cambiar "otra" sin querer | Era un `Alt`-`D` (data compartida); revisar contador de usuarios del data-block; Object ‣ Relations ‣ Make Single User |
| `M` en Edit Mode esperando "move to collection" | En Edit Mode `M` = Merge; Move to Collection es de Object Mode |
| Box select que "no agarra" los vértices de atrás | X-Ray apagado: `Alt`-`Z` y repetir |
| `Alt`-`LMB` no selecciona loops | Emulate 3 Button Mouse activo (Alt quedó tomado): desactivarlo o doble clic |
| Números 1/2/3 no cambian vertex/edge/face | Emulate Numpad activo los convirtió en vistas |
| Objetos nuevos aparecen "en cualquier sitio" | Aparecen en el 3D Cursor: `Shift`-`C` lo resetea al origen |
| Perder una pieza de vista tras aislar | Estaba en Local View: `NumpadSlash` para salir; u oculta: `Alt`-`H` |
| Tutorial 2.8–4.x: addon "incluido" que no aparece | En 5.x solo 5 add-ons bundled; el resto se instala desde Get Extensions (requiere Allow Online Access) |
| Script viejo con `import_scene.fbx` o Collada falla en 5.x | FBX: `bpy.ops.wm.fbx_import`; Collada eliminado — convertir a FBX/glTF/USD |
| Theme/config 4.x importado se ve roto | El sistema de themes se reescribió en 5.0; partir del default y re-personalizar |
| Rotar N caras y que colapsen hacia el centro común | Pivot era Median Point; usar Individual Origins |
| "Deshacer no funciona" tras operaciones de objeto | Global Undo desactivado en Preferences ‣ System; reactivarlo |
| Confiar en que el snap por Increment alinea un kit modular | Increment es relativo a la posición inicial; activar Absolute Grid Snap |

## Fuentes

- **Blender 5.0 Release Notes** (developer.blender.org/docs/release_notes/5.0/ + subpáginas Core, User Interface, Modeling & UV, Pipeline & I/O) — Blender Foundation — fecha de release, FBX C++ default, Collada eliminado, themes reescritos, nombres 255 bytes, modificadores GN, UV sync default, logging nuevo.
- **Blender 5.1 Release Notes** (developer.blender.org/docs/release_notes/5.1/ + User Interface) — Blender Foundation — Python 3.13/VFX 2026, búsqueda en Preferences, mejoras de sidebar.
- **Blender 5.2 LTS Release Notes** (developer.blender.org/docs/release_notes/5.2/ + User Interface) — Blender Foundation — fecha, ventana LTS hasta jul-2028, cambios de UI 5.2.
- **Blender 5.2 Manual — Default Keymap** (docs.blender.org/manual/en/latest/interface/keymap/blender_default.html) — atajos generales, F-keys, modales de drag.
- **Manual — Scene Layout**: Collections, Object Modes, Object Origin, Apply, Duplicate/Duplicate Linked, Join, Clear, Parent, Snap (`Shift`-`S`) — modelo de datos y operaciones de objeto con sus atajos exactos.
- **Manual — Files: Data-Blocks** — qué es un data-block, unicidad de nombres, compartición y linking.
- **Manual — 3D Viewport**: Modes, Navigation/Viewpoint/Projections/Local View, Viewport Shading, Pivot Point, Transform Orientation, Snapping, Proportional Editing, 3D Cursor — todo el capítulo de controles del viewport.
- **Manual — Modeling/Meshes Selecting**: Introduction (modos 1/2/3), Select Loops, Select Linked — selección con delimitadores y gotchas de X-Ray/n-gons.
- **Manual — Modeling/Meshes Editing**: Extrude Region, Inset, Bevel, Loop Cut, Knife, Merge, Separate, Make Edge/Face, Primitives (`Shift`-`A`) — atajos de edición verificados uno a uno.
- **Manual — Preferences**: Save & Load, System, Navigation, Input, Add-ons, Get Extensions — autosave, undo, navegación, riesgo de Emulate 3 Button Mouse, sistema de extensiones.
- **Manual — Scene Properties (Units)** — Metric/Unit Scale (solo display)/Length/Rotation.
- **Manual — Interface**: Workspaces, Editors, Tool System (W cycling, Quick Favorites, fallback tool), Undo & Redo, Industry Compatible Keymap, Defaults (Save Startup File) — sistema de ventanas y herramientas.
