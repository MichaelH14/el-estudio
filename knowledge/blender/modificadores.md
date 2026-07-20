# El stack de modificadores

> **Cuando cargar este archivo:** al construir, ordenar, aplicar o depurar modificadores en Blender para cualquier asset de juego — hard-surface, kit modular, retopo, LODs — o al decidir entre modificador clásico y Geometry Nodes. La teoría de topología/polycount vive en [ver: modelado/topologia] y [ver: modelado/presupuestos-poligonos]; aquí está LA HERRAMIENTA. Verificado contra el manual y release notes de Blender 5.2 LTS.

## 1. Filosofía no-destructiva y cómo evalúa el stack

Un modificador es una operación automática que afecta la geometría **sin tocar la malla base editable** (manual 5.2, Modifiers Introduction). El stack se evalúa **de arriba hacia abajo**; un modificador nuevo siempre entra **al final** (se aplica de último). El orden cambia el resultado: el ejemplo canónico del manual es Mirror + Subdivision Surface — con Mirror al final salen "dos superficies" separadas; con Subdivision al final, primero se espeja y la subdivisión suaviza la malla ya unida en el eje.

Operación básica (nombres exactos de UI, Blender 5.2):

| Acción | Cómo |
|---|---|
| Añadir | Properties ▸ pestaña Modifiers ▸ botón **Add Modifier**, o **Shift-A** dentro de esa pestaña (menú estándar desde 4.0, incluye assets de Geometry Nodes) |
| Reordenar | Arrastrar el icono de agarre (grip) del panel; menú extras: **Move to First/Last** |
| Aplicar | Menú extras del modificador ▸ **Apply** (**Ctrl-A** con el cursor sobre el panel) |
| Duplicar | **Duplicate** (**Shift-D** en el panel) — se inserta justo debajo |
| Copiar a otros objetos | **Copy to Selected** (del activo a todos los seleccionados) |
| Fijar al final | **Pin to Last** — lo mantiene último aunque añadas más (típico para Triangulate) |
| Multi-objeto | Mantener **Alt** al añadir/aplicar/quitar afecta a TODOS los seleccionados |

Toggles de visibilidad por modificador (cabecera del panel): **Realtime** (viewport), **Render**, **Edit Mode** (ver el resultado mientras editas la base) y **On Cage** (editar directamente sobre la geometría modificada; ojo: snapping y el gizmo siguen usando las posiciones originales — manual). Subdivision tiene atajo propio: **Ctrl-1…Ctrl-5** añade/ajusta un Subdivision Surface con ese nivel de viewport.

En bpy los clásicos se crean con `obj.modifiers.new(name, type=...)`; tipos verificados en la API 5.2: `'MIRROR'`, `'SUBSURF'`, `'BEVEL'`, `'BOOLEAN'`, `'ARRAY'` (=Legacy, ver §3), `'SOLIDIFY'`, `'SHRINKWRAP'`, `'DECIMATE'`, `'REMESH'`, `'TRIANGULATE'`, `'DATA_TRANSFER'`, `'WELD'`, `'WEIGHTED_NORMAL'`, `'MULTIRES'`, `'NODES'` (Geometry Nodes). [ver: bpy-scripting]

## 2. El orden del stack: reglas canónicas

Reglas de orden estándar para assets de juego (consecuencia directa de la evaluación top-down):

1. **Mirror temprano** — todo lo que venga después (subdivision, bevel, boolean) actúa sobre la malla ya completa y simétrica; con Merge activo no queda costura en el eje.
2. **Generate antes que shading** — Boolean/Array/Solidify crean geometría; Bevel debe ver esa geometría ya creada para biselar también los cortes.
3. **Bevel tarde, normales al final** — Bevel después de los booleans; Weighted Normal / Smooth by Angle después del Bevel (operan sobre las caras finales).
4. **Deform después de Generate** — Shrinkwrap/Lattice/Armature al final de la parte constructiva: deforman el resultado, no la base.
5. **Triangulate último** (y con Pin to Last) — congela la triangulación exacta que verá el bake y el engine [ver: modelado/topologia].
6. **Subdivision:** para modelado de subdivisión clásico va después de Mirror y de los holding edges/creases; en mid-poly de juego normalmente NO hay subsurf en el stack final.

Antipatrón típico: Bevel antes de Mirror deja el borde del eje de simetría biselado (una arista que no existe en la malla final) — el mismo tipo de error aplica a cualquier modificador que trate bordes abiertos que el Mirror va a cerrar.

## 3. Los canónicos de juego, uno a uno

Opciones con nombre exacto del manual 5.2; solo las que importan en assets de juego.

### Mirror
- **Axis** X/Y/Z (combinables: 2 ejes = 4 copias, 3 = 8), espeja sobre el **Object Origin** o un **Mirror Object** (típicamente un Empty).
- **Bisect** corta la malla por el plano y se queda con un lado (con **Flip** eliges cuál) — sanea mallas que ya cruzan el eje.
- **Clipping** impide que los vértices crucen el plano al editar; **Merge** + **Merge Distance** suelda la costura del eje.
- **Data ▸ Flip UV / UV Offsets**: desplazar los UVs espejados (p. ej. +1 en U) evita que el overlap ensucie el bake [ver: modelado/high-to-low].
- Vertex groups se espejan solo si existe el grupo del lado contrario con sufijo `.L`/`.R` y está vacío (manual).

### Subdivision Surface (`'SUBSURF'`)
- **Catmull-Clark** (suaviza) o **Simple** (solo corta). **Levels Viewport / Render** separados — viewport siempre ≤ render.
- **Advanced ▸ Use Limit Surface**, **UV Smooth** (default suaviza UVs; *None* los deja quietos) y **Use Creases** (respeta los creases de §6).
- Limitación documentada: normales incoherentes (caras volteadas) fuerzan subdivisión "Simple" por zonas — arreglo: `Mesh ▸ Normals ▸ Recalculate Outside` (**Shift-N**).
- Cada nivel multiplica ×4 las caras (un quad → 4): la memoria explota rápido; el propio manual advierte de cuelgues por RAM/VRAM.

### Bevel + Weighted Normal (la pareja mid-poly)
Bevel:
- **Affect** Vertices/Edges; **Width Type** (Offset, Width, Depth, Percent, Absolute) + **Amount**; **Segments** (2 suele bastar en mid-poly).
- **Limit Method**: **Angle** (solo aristas más cerradas que el umbral — el default operativo), **Weight** (atributo `bevel_weight_edge`, §6) o **Vertex Group**.
- **Geometry ▸ Clamp Overlap** evita solapes; **Miter Outer** (Sharp/Patch/Arc) para esquinas; **Loop Slide**.
- **Shading ▸ Harden Normals**: ajusta las normales del bisel para que las caras planas sigan planas (crea el atributo `custom_normal` si no existe). **Mark Seam/Sharp** propaga seams/sharps por el bisel. **Material Index** (-1 = hereda el material vecino). **Face Strength** (None/New/Affected/All) marca las caras del bisel para el Weighted Normal.

Weighted Normal:
- **Weighting Mode**: **Face Area** (default), **Corner Angle**, **Face Area & Angle**; **Weight** (50 = uniforme, más = más contraste hacia caras grandes).
- **Keep Sharp** respeta aristas Sharp; **Face Influence** usa los Face Strength que dejó el Bevel (el manual documenta explícitamente esta pareja Bevel → Weighted Normal).

Es la alternativa moderna al bake de high-poly para hard-surface mid-poly: biseles reales pequeños + normales ponderadas = shading limpio sin normal map [ver: modelado/hard-surface].

### Boolean
- **Operation**: Intersect / Union / Difference. **Operand Type**: Object o Collection (cortar con una colección entera de cutters).
- **Solver** — ⚠️ cambios de versión: **Float** (rápido, no soporta geometría solapada; hasta 4.5 se llamaba "Fast", renombrado en 5.0 en UI y API), **Exact** (el más robusto, soporta solapes y **Self Intersection** / **Hole Tolerant**, pero es el lento), **Manifold** (nuevo en 4.5, basado en la Manifold Library: normalmente el más rápido, pero exige que TODAS las mallas sean manifold; única excepción documentada: Difference con un plano).
- Materiales (solver Exact): **Index Based** o **Transfer** (copia slots del cutter).
- Truco documentado: Exact + Collection vacía = elimina las auto-intersecciones de la propia malla.
- Solo mallas manifold garantizan resultado correcto (warning del manual); cutter con agujeros = artefactos.

### Array — ⚠️ renovado en 5.0
Blender 5.0 introdujo un **Array nuevo basado en Geometry Nodes** y renombró el clásico a **"Array (Legacy)"** (release notes 5.0; sigue disponible "por ahora"). El nuevo:
- **Shape**: **Line** (Offset Method: Relative / Offset / Endpoint), **Circle** (Full/Arc, Radius, Central Axis), **Curve** (sigue un Curve Object) o **Transform** (offset arbitrario o transform de otro objeto).
- **Align Rotation** orienta cada copia a la tangente (círculo/curva; mejorado en 5.2), **Randomize** (offset/rotación/escala/flip + Seed, con **Exclude First / Last**).
- **Realize Instances** convierte las instancias en geometría real — **obligatorio** para que funcione **Merge** (soldar copias adyacentes) o un Boolean posterior.
- En bpy: `modifiers.new(type='ARRAY')` crea el **Legacy**; el nuevo es un asset de nodos — se añade por el menú Add Modifier o con `bpy.ops.object.modifier_add_node_group`. Los tutoriales 2.8–4.x (Fixed Count / Relative Offset / caps) describen el Legacy.

### Solidify
- **Mode Simple** (rápido; extruye — falla con aristas de 3+ caras o normales incoherentes) vs **Complex** (garantiza salida manifold, "mucho más lento" según el manual).
- **Thickness** + **Offset** (-1 a 1); ⚠️ warning documentado: con **escala no uniforme el grosor sale desigual** — aplicar la escala antes (`Object ▸ Apply ▸ Scale`).
- **Even Thickness** y **Rim Fill** (el manual pide desactivar Rim si no se necesita: es lento). **Material Offset** para dar otro material al interior/rim.
- Uso de juego: dar grosor real a planos (ropa, chapa, muros de kit) antes de biselar o exportar.

### Shrinkwrap
- **Wrap Method**: **Nearest Surface Point** (default), **Project** (por ejes o normal, con **Face Cull** y **Auxiliary Target**), **Nearest Vertex**, **Target Normal Project** (más suave, "significativamente más lento" — manual).
- **Snap Mode**: On Surface / Outside Surface / **Above Surface** (offset por la normal del target — el bueno para retopo) / Inside / Outside.
- **Offset** separa la retopo de la superficie para que no haya z-fighting mientras trabajas.

### Decimate
- **Collapse**: **Ratio** de caras a conservar — el ratio se calcula en TRIÁNGULOS aunque la malla tenga quads (nota del manual). **Symmetry** (un eje), **Triangulate**, **Vertex Group** + Factor para proteger zonas.
- **Un-Subdivide**: revierte subdivisiones en mallas de rejilla (**Iterations** pares).
- **Planar**: disuelve superficies casi coplanares (**Angle Limit**) con **Delimit** (Normal/Material/Seam/Sharp/UVs) para no romper bordes que importan.
- No previsualiza en Edit Mode (documentado); muestra el conteo de caras resultante en el panel.

### Remesh
- **Mode**: Blocks / Smooth / **Sharp** (con **Octree Depth** + Sharpness) y **Voxel** (OpenVDB, salida manifold que preserva volumen; `voxel_size` en la API controla la resolución, **Adaptivity** reduce caras introduciendo triángulos).
- La entrada debe tener grosor; si es plana, Solidify encima del Remesh (nota del manual).
- Uso real: unificar kitbash/sculpt en una sola malla manifold ANTES de retopo o bake — su salida densa jamás es la low-poly final [ver: sculpt].

### Triangulate
- **Quad Method**: **Beauty** / Fixed / Fixed Alternate / **Shortest Diagonal** / Longest Diagonal. **N-gon Method**: Beauty / Clip. **Minimum Vertices** = 5 → solo triangula n-gons.
- Al final del stack + Pin to Last: garantiza que bake, export y engine vean la MISMA triangulación (la diagonal de un quad no planar cambia el shading) [ver: modelado/topologia].

### Data Transfer
- Copia datos de otra malla: **Data Types** (Custom Normals, Colors, UVs, vertex groups…), **Mapping** (Topology = por índice, requiere mallas gemelas; o por proximidad/interpolación).
- ⚠️ Gotcha documentado: hay que pulsar **Generate Data Layers** para crear las capas destino — sin eso el transfer no hace nada.
- Uso de juego: transferir custom normals de un proxy liso a la low-poly (follaje, shading de hard-surface), o pasar vertex groups/UVs entre variantes del mismo asset.

### Weld
- **Mode All** (suelda todo, incluidas piezas sueltas) vs **Connected** (solo geometría conectada); **Distance**; **Only Loose Edges** para coser costuras.
- Cierra el stack de kits: suelda las uniones que Mirror/Array dejan duplicadas antes de Triangulate/export.

## 4. Recetas de stacks típicos

Orden = orden real en el stack (arriba → abajo):

| Receta | Stack | Notas |
|---|---|---|
| **Hard-surface mid-poly** | Mirror → (Booleans) → Bevel (Limit: Angle o Weight, 2 segmentos) → Weighted Normal (Keep Sharp) → Triangulate | La receta anti-bake: biseles reales + WN. Si usas Face Strength en el Bevel, activa Face Influence en el WN |
| **Kit modular** | Array (Line/Circle) → Mirror → Weld → Bevel → Weighted Normal | Realize Instances + Merge en el Array; medidas en múltiplos de grid [ver: modelado/entornos-modulares] |
| **Retopo sobre sculpt** | Mirror (Clipping ON) → Subdivision (1–2, opcional) → Shrinkwrap (target: high, Above Surface, Offset pequeño) | Shrinkwrap SIEMPRE último; Edit Mode + On Cage en el Mirror para trabajar pegado a la superficie |
| **Low-poly desde high (honesto)** | Decimate Collapse (+ Symmetry, + Vertex Group para proteger cara/manos) → Weld → Triangulate | Vale para LODs y props estáticos. Para héroes o mallas que deforman, decimate NO sustituye la retopo manual: no produce edge loops [ver: modelado/high-to-low] |

Patrón bpy del stack mid-poly (propiedades verificadas en la API 5.2):

```python
import bpy, math
obj = bpy.context.object
bv = obj.modifiers.new("Bevel", 'BEVEL')
bv.width = 0.004                      # metros
bv.segments = 2
bv.limit_method = 'ANGLE'             # o 'WEIGHT' (usa bevel_weight_edge)
bv.angle_limit = math.radians(30)
bv.use_clamp_overlap = True
wn = obj.modifiers.new("WeightedNormal", 'WEIGHTED_NORMAL')
wn.mode = 'FACE_AREA'                 # o 'CORNER_ANGLE', 'FACE_AREA_WITH_ANGLE'
wn.keep_sharp = True
tri = obj.modifiers.new("Triangulate", 'TRIANGULATE')
```

## 5. Aplicar modificadores: cuándo, cómo, qué se pierde

**Apply** (Ctrl-A en el panel) convierte el resultado en geometría real y borra el modificador. Reglas documentadas (manual 5.2 + código fuente):

- ⚠️ **Aplicar un modificador que no es el primero lo evalúa como si fuera el primero** (warning literal del manual) — puede dar un resultado distinto al que ves. Para congelar el stack entero en orden: aplicar de arriba hacia abajo, o mejor `Object ▸ Apply ▸ Visual Geometry to Mesh` / `bpy.ops.object.convert(target='MESH')`, que congela todo de una vez.
- **Data multiusuario**: si la malla la comparten varios objetos, Blender pide hacerla **Single User** primero (popup).
- **Shape keys**: aplicar un modificador que cambia topología sobre una malla con shape keys falla con el error `"Modifier cannot be applied to a mesh with shape keys"` (verificado en `object_modifier.cc`). Los deform puros ofrecen **Apply as Shape Key** / **Save as Shape Key** en su lugar.
- Qué se pierde al aplicar: el paramétrico. Ya no puedes ajustar el ancho del bevel, mover el eje del mirror ni bajar la subdivisión. **Regla: el .blend de trabajo conserva el stack vivo; lo aplicado vive solo en copias o en el export.**

**Apply en export vs apply real** [ver: import-export]: el exportador FBX (`File ▸ Export ▸ FBX (.fbx)`, `bpy.ops.export_scene.fbx`) tiene **Apply Modifiers** — exporta la malla evaluada (el stack completo calculado) sin tocar el .blend. Comportamiento verificado en el código del exportador (`export_fbx_bin.py`):

- El modificador **Armature NO se aplica** (pone el rig en rest pose y conserva los vertex groups): el skinning sobrevive.
- ⚠️ Con Apply Modifiers activo, una malla que además tenga **shape keys** exporta la versión evaluada **sin** shape keys (la malla evaluada ya no los lleva, esto es cierto siempre: Apply Modifiers = una sola malla, ya no hay blend shapes que exportar). Personaje con blend shapes: su stack debe estar aplicado de verdad ANTES de exportar, dejando solo el Armature.
- **Export Subdivision Surface** desactiva el último Subdivision Catmull-Clark y lo escribe como dato de subdivisión FBX en lugar de geometría.
- ⚠️ **Contradicción real sin resolver, NO VERIFICADO con un export real**: la página del manual 5.2 para este exportador (`docs.blender.org/manual/en/5.2/addons/import_export/scene_fbx.html`, título en el propio manual: **"FBX (Legacy)"**) lista en su sección **Export ▸ Missing**: *"Vertex shape keys – FBX supports them but this exporter does not write them yet"* — es decir, el manual afirma que el exportador NO escribe shape keys en absoluto, ni siquiera con Apply Modifiers desactivado y solo el Armature en el stack. Esto contradice la práctica extendida en producción (Blender→FBX con blend shapes es un flujo común hacia Unity/Unreal) y lo que sugiere el código del exportador. Antes de depender de este camino para un personaje con blend shapes: hacer un export FBX real de prueba con un shape key simple y verificar en el motor destino que el blend shape llegó — no asumir ninguno de los dos lados.

```python
# Congelar el stack en una copia y dejar el original intacto:
bpy.ops.object.duplicate()
bpy.ops.object.convert(target='MESH')          # aplica TODO el stack en orden
# Aplicar uno solo (firma 5.2):
bpy.ops.object.modifier_apply(modifier="Bevel")
```

## 6. Crease y bevel weight como alternativa a holding edges

En 5.x el crease y el bevel weight son **atributos genéricos** de la malla: `crease_edge`, `bevel_weight_edge`, `bevel_weight_vert` (nombres confirmados por el manual del Bevel y la API). Se editan en Edit Mode:

- **Crease**: seleccionar aristas → **Shift-E** (o Sidebar ▸ Transform ▸ crease). Subdivision Surface lo respeta con **Use Creases**: crease 1.0 = arista dura bajo subdivisión sin añadir loops.
- **Bevel weight**: valor 0–1 por arista; el Bevel con **Limit Method: Weight** bisela solo las aristas marcadas, con ancho proporcional al peso.

Frente a holding edges (loops de soporte reales, [ver: modelado/topologia]): creases/weights mantienen la malla base limpia y editable, pero **son datos de Blender** — el crease solo sobrevive el export FBX como dato de subdivisión (el exportador escribe `use_creases` del subsurf); para el engine lo que cuenta es la geometría final ya evaluada. En mid-poly de juego, el flujo robusto es bevel weights + Bevel modifier (el bisel se vuelve geometría real al exportar); los creases son más útiles mientras esculpes la forma con subsurf que en el asset final.

⚠️ Cambio de versión (4.1): **Auto Smooth ya no existe** como checkbox de la malla. Lo reemplaza el modificador **Smooth By Angle** — un asset de Geometry Nodes de la librería "Essentials" que `Object ▸ Shade Auto Smooth` añade automáticamente (release notes 4.1 + manual 5.2). El estado base de una malla suave equivale al viejo Auto Smooth a 180°. Tutoriales pre-4.1 que digan "activa Auto Smooth" = añadir Smooth By Angle o marcar Sharp manualmente.

## 7. Geometry Nodes como modificador vs los clásicos

Un node group de Geometry Nodes ES un modificador más (**Geometry Nodes Modifier**, tipo `'NODES'`): recibe la geometría del paso anterior por Group Input y devuelve por Group Output, en cualquier posición del stack [ver: geometry-nodes]. Desde 4.0 el menú Add Modifier lista assets de node groups junto a los built-in; **Move to Nodes** convierte un Geometry Nodes Modifier en grupo reutilizable.

⚠️ Blender 5.0 empezó la "nodificación" de los clásicos — seis modificadores nuevos basados en nodos (release notes 5.0): **Array** (§3), **Scatter on Surface**, **Instance on Elements**, **Randomize Instances**, **Curve to Tube** y **Geometry Input** (trae la geometría final de otro objeto al inicio del stack). Cuándo cada cosa:

| Situación | Herramienta |
|---|---|
| Bevel, mirror, boolean, decimate, shading de normales | Clásicos — más simples, menos overhead mental, API estable |
| Distribución/instancias (props sobre terreno, tiles, randomización) | Los nuevos GN (Array, Scatter on Surface) o node groups propios |
| Lógica paramétrica reutilizable (cercas, cables, edificios modulares) | Geometry Nodes propio guardado como asset |
| Un solo objeto, edición puntual | Edit Mode directo — no todo necesita ser procedural [ver: edicion-malla] |

Regla de juego: la salida GN con instancias debe pasar por **Realize Instances** antes de Weld/Boolean/export de malla única.

## 8. Performance del stack

| Qué pesa | Dato verificado | Mitigación |
|---|---|---|
| Subdivision Surface | ×4 caras por nivel; warning de RAM/VRAM en el manual | Viewport 1–2 / Render aparte; **Optimal Display**; preferencia **GPU Subdivision** (Preferences ▸ Viewport ▸ Subdivision; ojo: interpola normales/tangentes en vez de recalcular) |
| Boolean Exact | "Much slower" (manual); en 5.1 el Exact se aceleró >35% con muchos atributos | Usar **Manifold** si todas las mallas son manifold (4.5+: "usualmente el más rápido"); Float para cortes simples sin solapes |
| Solidify Complex | "Much slower" que Simple (manual); Rim Fill y Flat Faces marcados como lentos | Simple salvo geometría patológica; Rim solo si se ve |
| Shrinkwrap Target Normal Project | "Significantly slower" que Nearest Surface Point (manual) | Nearest Surface Point + Above Surface para retopo |
| Decimate | Sin preview en Edit Mode; recálculo completo al tocar Ratio | Ajustar en copias o al final del proceso |
| Stack profundo en general | 5.0 usa "implicit sharing" en datos de modificadores: undo más rápido y menos memoria (release notes 5.0) | Toggle **Realtime** para apagar los caros mientras editas; colapsar paneles no ayuda al rendimiento, apagar sí |

Flujo fluido: mantener los modificadores caros (Boolean Exact, Subdiv alto) apagados en viewport mientras editas la base, encenderlos para revisar, y verificar el conteo real de triángulos con Statistics en el viewport (el stack multiplica geometría que el contador de Edit Mode no muestra).

## Reglas prácticas

1. Stack de arriba a abajo = orden de evaluación; el resultado depende del orden. Mirror arriba, shading (Weighted Normal) abajo, Triangulate último con Pin to Last.
2. Verifica la versión de lo que leas en la web: solver "Fast" (=Float desde 5.0), "Auto Smooth" (muerto en 4.1) y el Array viejo (Legacy desde 5.0) delatan contenido 2.8–4.x.
3. Mirror: origen del objeto en el eje de simetría (o Mirror Object), Clipping ON al editar, Merge ON siempre.
4. Bevel mid-poly: Limit Method Angle (~30°) para empezar; pasar a Weight (`bevel_weight_edge`) cuando el ángulo no discrimine bien; Clamp Overlap ON.
5. Weighted Normal después del Bevel; Keep Sharp ON; Face Influence solo si el Bevel marca Face Strength.
6. Boolean: solver Manifold si todo es manifold, Exact si hay solapes o dudas, Float solo para cortes rápidos limpios. Cutters en una Collection para stacks grandes.
7. Array 5.x: Realize Instances ON antes de Merge, Weld o Boolean sobre las copias.
8. Solidify y cualquier grosor/offset: aplicar la escala del objeto primero (escala no uniforme = grosor desigual, documentado).
9. Shrinkwrap de retopo: último del stack, Above Surface, Offset pequeño (~0.002 m); jamás aplicarlo hasta cerrar la retopo.
10. Decimate es para LODs y props estáticos; malla que deforma (personaje, ropa) exige retopo manual — decimate no crea edge loops.
11. Nunca apliques el stack en tu .blend de trabajo "para exportar": usa Apply Modifiers del FBX, o congela en una copia (`duplicate` + `convert(target='MESH')`).
12. Malla con shape keys: deja SOLO el Armature en el stack antes de exportar — el exportador no puede aplicar modificadores y conservar los blend shapes a la vez.
13. Aplicar un modificador fuera de orden (no-primero) cambia el resultado: congela todo con Visual Geometry to Mesh si necesitas el resultado exacto del viewport.
14. Antes de aplicar sobre data compartida entre objetos, acepta el Make Single User o revisa qué más usa esa malla.
15. Subdivision viewport ≤ render, y en asset de juego pregunta primero si de verdad necesita subsurf en el stack final.
16. Normales incoherentes rompen Subdivision y Boolean: Shift-N (Recalculate Outside) antes de culpar al modificador.
17. Cuenta triángulos con el stack activo (Statistics/engine), no con el conteo de Edit Mode: el stack multiplica geometría invisible al contador base.
18. Para operar por bpy/MCP: `modifiers.new()` para clásicos, `modifier_add_node_group` para los GN nuevos, `modifier_apply(modifier="...")` para aplicar uno — nombres de tipo del §1 [ver: blender-mcp-operativo].

## Errores comunes

| Error | Síntoma | Antídoto |
|---|---|---|
| Subdivision antes de Mirror | Costura visible / dos mitades separadas en el eje | Mirror arriba del Subdiv (ejemplo literal del manual); Merge ON |
| Bevel antes de Mirror/Boolean | Aristas del eje o del corte sin biselar (o biseles fantasma en el eje) | Bevel después de todo lo constructivo |
| Aplicar un modificador del medio del stack | La malla resultante no coincide con lo que veías | Se evalúa como si fuera el primero (warning del manual); congelar todo con Visual Geometry to Mesh |
| "Modifier cannot be applied to a mesh with shape keys" | Apply falla en malla con shape keys | Aplicar antes de crear los shape keys; deform puros: Apply as Shape Key |
| Export FBX con Apply Modifiers y blend shapes | Los blend shapes desaparecen en Unity | Aplicar el stack real antes (dejar solo Armature), Apply Modifiers OFF para esa malla — y aun así hacer un export de prueba: el manual del exportador (sección Legacy) dice que no escribe shape keys en absoluto, sin verificar en vivo no se sabe si sobreviven (§5) |
| Boolean con cutter no manifold | Caras basura, agujeros, resultado impredecible | Cerrar el cutter (manifold); Exact + Hole Tolerant solo como último recurso |
| Solver Manifold sobre malla con agujeros | El boolean no opera | Manifold exige todo manifold (4.5+); usar Exact |
| Solidify/Bevel con escala sin aplicar | Grosor/bisel distinto por lado | Object ▸ Apply ▸ Scale antes |
| Buscar "Auto Smooth" en 4.1+ | El checkbox no existe | Shade Auto Smooth (añade el asset Smooth By Angle) o marcar Sharp + Shade Smooth |
| Tutorial viejo de Array (Fixed Count/caps) | La UI no coincide con el Array 5.x | Es el Array (Legacy); el nuevo usa Shape Line/Circle/Curve/Transform |
| Weighted Normal sin efecto visible | Shading no cambia | La malla necesita zonas smooth (WN edita custom normals); revisar Keep Sharp y que esté DESPUÉS del último generate |
| Data Transfer "no hace nada" | Capas destino vacías | Pulsar Generate Data Layers (documentado: no es automático) |
| Decimate Ratio 0.5 no da la mitad de caras | Conteo mayor al esperado | El ratio cuenta triángulos, no quads (nota del manual); activar Triangulate para conteo real |
| Mirror + bake con UVs solapados | Artefactos en el bake | Data ▸ UV Offsets +1.0 en U para el lado espejado |
| Stack lento al editar | Viewport a tirones | Apagar Realtime en Boolean Exact/Subdiv mientras editas; GPU Subdivision ON |

## Fuentes

- **Blender 5.2 Manual — Modifiers: Introduction & The Modifier Stack** — docs.blender.org — evaluación top-down, interfaz (Apply Ctrl-A, Pin to Last, On Cage), warning de apply fuera de orden, ejemplo Mirror/Subsurf.
- **Blender 5.2 Manual — páginas de cada modificador** (Bevel, Boolean, Mirror, Subdivision Surface, Weighted Normal, Smooth By Angle, Decimate, Remesh, Triangulate, Data Transfer, Weld, Shrinkwrap, Solidify, Array, Common Options) — docs.blender.org — todas las opciones y nombres exactos de UI citados en §3–§6.
- **Blender 5.0 Release Notes — Modeling & UV** — developer.blender.org — los 6 modificadores GN nuevos, Array (Legacy), rename Fast→Float, implicit sharing.
- **Blender 5.1 / 5.2 Release Notes — Modeling** — developer.blender.org — Exact >35% más rápido; LoopTools integrados y mejora de Align Rotation del Array; confirma 5.2 LTS (14-jul-2026).
- **Blender 4.5 Release Notes — Modeling** — developer.blender.org — solver Manifold (Manifold Library), condiciones y rendimiento.
- **Blender 4.1 Release Notes — Modeling** — developer.blender.org — eliminación de Auto Smooth y su reemplazo por el asset de nodos.
- **Blender 4.0 Release Notes — Modeling** — developer.blender.org — menú Add Modifier estándar con Shift-A y assets GN.
- **Código fuente de Blender: `object_modifier.cc`** — projects.blender.org (mirror GitHub) — error literal de apply con shape keys.
- **Código fuente del exportador FBX: `export_fbx_bin.py`** — projects.blender.org (mirror GitHub) — Apply Modifiers = malla evaluada, excepción Armature (rest pose), manejo del último subsurf, escritura de shape keys y creases.
- **Blender Python API 5.2** — docs.blender.org/api/current — enum de tipos de modificador, firmas de `modifier_apply` / `convert` / `modifier_add_node_group`, propiedades de Bevel/WeightedNormal/Shrinkwrap/Remesh usadas en los snippets.
- **Blender 5.2 Manual — Preferences: Viewport (GPU Subdivision), Object Apply, FBX import/export** — docs.blender.org — GPU Subdivision y su nota de normales interpoladas; Visual Geometry to Mesh; opciones del exportador FBX.
