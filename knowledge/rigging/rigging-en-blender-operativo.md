# Rigging en Blender: el manual operativo

> **Cuando cargar este archivo:** siempre que vayas a construir, editar o skinnear un rig de personaje/criatura/prop en Blender para llevarlo a Unity — crear el armature, extruir/parentar huesos, pintar pesos, montar constraints/IK, organizar el .blend del rig — y especialmente cuando operes ese flujo por MCP o headless (`blender -b`). Es el CÓMO concreto: qué modo, qué operador, qué setting. La teoría profunda vive en los otros archivos de rigging (abajo); aquí va el flujo y los operadores exactos.

Stack de referencia: **Blender 5.2.0 LTS** (operadores y enums verificados contra el binario local, build 2026-07-14) + **Unity 6 (Mecanim/Humanoid)** + **Auto-Rig Pro 2026**. Los datos dependientes de versión/precio van marcados con fecha. Este archivo NO repite teoría de esqueletos, skinning, deformación, IK/FK, Rigify ni rigs mecánicos — cada una tiene su base:
[ver: esqueletos-armature] · [ver: skinning-weights] · [ver: deformacion] · [ver: ik-fk-constraints] · [ver: rigify] · [ver: rigs-mecanicos] · [ver: rig-a-unity]. Cómo ejecutar bpy y operar el MCP: [ver: blender/bpy-scripting] · [ver: blender/blender-mcp-operativo]. Sacar el rig al motor: [ver: blender/import-export] · [ver: unity/animacion-unity].

---

## 1. El objeto Armature y sus tres modos

Un rig es **un objeto Armature** (dato `bpy.data.armatures`, wrapper `bpy.data.objects` con `.type == 'ARMATURE'`) que deforma una malla mediante un **modificador Armature** + **vertex groups** con el nombre de cada hueso. Todo el trabajo se reparte en tres modos y confundirlos es el error #1 del principiante:

| Modo | Qué se hace | Sobre qué datos | API |
|---|---|---|---|
| **Object Mode** | Mover/rotar/escalar el rig ENTERO en la escena, aplicar transforms, añadir el modificador, parentar la malla | El objeto | `obj.location`, `obj.modifiers` |
| **Edit Mode** | Crear y editar huesos: posiciones **rest** (head/tail/roll), jerarquía, conectar | `armature.edit_bones` (**solo existe en Edit Mode**) | `arm.edit_bones.new(...)` |
| **Pose Mode** | Posar huesos, montar constraints/IK, custom shapes, animar; NO cambia el rest | `obj.pose.bones` + `armature.bones` (read-only de rest) | `obj.pose.bones["x"].rotation_euler`, `.constraints` |

Reglas duras:
- **Edit Mode define el rest pose** (la "T-pose" o "A-pose" de reposo). Pose Mode es una desviación temporal sobre ese rest; `Alt+R/G/S` (o `pose.transforms_clear`) devuelve al rest.
- `armature.edit_bones` **desaparece fuera de Edit Mode** — un script que crea huesos debe entrar a Edit (`bpy.ops.object.mode_set(mode='EDIT')`) y salir a Object para confirmar el data-block [ver: blender/bpy-scripting §Edit Mode tiene su propia copia].
- La escala del OBJETO armature debe ser `(1,1,1)` y estar aplicada antes de exportar; nunca aplicar transforms a huesos en pose — aplicar en Object Mode sobre el rest [ver: blender/import-export §Rotación].
- Display del rig (`armature.display_type`): `OCTAHEDRAL` (default), `STICK`, `BBONE`, `ENVELOPE`, `WIRE`. `show_in_front` es propiedad del **Object**, no del data-block armature — `rig.show_in_front = True` (verificado: `armature.show_in_front` no existe) para ver los huesos a través de la malla (imprescindible al pintar pesos).

---

## 2. Edit Mode: herramientas de huesos (operadores verificados 5.2)

Menú `Armature` y `Bone` del header, o menú contextual (RMB). Nombres de operador confirmados contra el binario; los atajos son el keymap por defecto (verificables con tooltip/Info editor [ver: blender/bpy-scripting §descubrir API]).

| Herramienta | Operador (`bpy.ops.armature.*`) | Atajo | Nota operativa |
|---|---|---|---|
| Añadir hueso suelto | `bone_primitive_add(name, length, use_deform=True)` | Add ‣ Single Bone | `use_deform=True` = cuenta como hueso de deformación |
| Extrude (nuevo hueso hijo desde la punta) | `extrude_move` (macro extrude+translate) | `E` | La forma normal de "crecer" la cadena; hijo conectado |
| Extrude bifurcado | `extrude_forked` | `Shift+E` | Dos hijos de la misma punta (clavículas, dedos) |
| Extrude a punto (click) | `click_extrude` | `Ctrl+RMB` | Extruye hacia donde clicas |
| Subdividir hueso | `subdivide(number_cuts=1)` | RMB ‣ Subdivide | Parte un hueso en N conservando la cadena |
| **Symmetrize** | `symmetrize(direction='NEGATIVE_X')` | Armature ‣ Symmetrize | Copia el lado `.L`↔`.R` a través de **X global**. `direction`: `NEGATIVE_X` (default, +X→−X) o `POSITIVE_X`. Exige naming `.L/.R` |
| **Recalculate Roll** | `calculate_roll(type='POS_X', axis_flip, axis_only)` | `Ctrl+N` | Reorienta el eje del hueso (ver §3) |
| Clear Roll | `roll_clear` | — | Roll a 0 |
| Duplicar | `duplicate_move` | `Shift+D` | Copia huesos + relaciones |
| Fill (crear hueso entre dos puntas/heads) | `fill` | `F` | Conecta dos huesos seleccionados |
| Merge | `merge` | — | Funde huesos de una cadena en uno |
| Dissolve | `dissolve` | `Ctrl+X` | Elimina un hueso reconectando la cadena (no deja hueco) |
| Delete | `delete` | `X` | Borra sin reconectar |
| Split / Separate | `split` / `separate` (`P`) | — | `separate` saca huesos a OTRO objeto armature |
| Switch Direction | `switch_direction` | `Alt+F` | Invierte head↔tail (arregla cadenas al revés) |
| Parent / Unparent | `parent_set` / `parent_clear` | `Ctrl+P` / `Alt+P` | `parent_set` ofrece **Connected** (punta pegada) u **Offset** (mantiene hueco) |
| Auto-name L/R | `autoside_names(type='XAXIS')` / `flip_names` | — | Pone `.L/.R` por posición en X — requisito para Symmetrize |

Flujo típico de Edit Mode: modelar la cadena con `E` de la raíz hacia afuera, nombrar con sufijo `.L`, poner cada hueso en su sitio (head/tail sobre las articulaciones de la malla [ver: modelado/organico-personajes]), y `Symmetrize` para clonar el lado. Naming coherente `.L/.R` no es cosmético: Symmetrize, flip pose y el retarget Humanoid de Unity dependen de él.

**Crear un armature por datos (headless, verificado):**

```python
import bpy
arm = bpy.data.armatures.new("Hero_Arm")
rig = bpy.data.objects.new("Hero_Rig", arm)
bpy.context.collection.objects.link(rig)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode='EDIT')          # edit_bones SOLO existe en Edit Mode
eb = arm.edit_bones
root  = eb.new("root");  root.head=(0,0,0);   root.tail=(0,0,0.1)
spine = eb.new("spine"); spine.head=(0,0,1);  spine.tail=(0,0,1.4)
spine.parent = root                            # sin use_connect = parent con offset
bpy.ops.object.mode_set(mode='OBJECT')         # salir confirma los cambios al data-block
print(len(arm.bones), "bones:", [b.name for b in arm.bones])
```

## 3. Roll y orientación de ejes (por qué importa para Unity)

Cada hueso tiene su Y local **a lo largo del hueso** (head→tail); el **roll** gira los ejes X/Z alrededor de esa Y. Un roll inconsistente hace que la misma rotación produzca giros distintos por hueso — mata IK, mirror pose y retarget. `calculate_roll` (`Ctrl+N`) reorienta con `type` (enum verificado 5.2):

`POS_X` (default), `POS_Z`, `NEG_X`, `NEG_Z` (eje local hacia el mundo), `GLOBAL_POS_X/Y/Z`, `GLOBAL_NEG_X/Y/Z` (alinea a un eje global), `ACTIVE` (alinea al hueso activo), `VIEW`, `CURSOR`. Flags: `axis_flip` (voltea), `axis_only` (solo alinea el eje, sin cambiar el resto).

- Convención habitual de personaje: brazos/piernas con roll consistente (`GLOBAL_POS_Z` o alineado al plano de flexión) para que el codo/rodilla doble en un solo eje limpio.
- Un rig con rolls sucios se ve bien en rest pero se retuerce al animar. Si el retarget en Unity da poses raras sin ser un problema de mapping, sospechar del roll [ver: ik-fk-constraints].

## 4. Pose Mode: posar, constraints, custom shapes, organizar

**Posar** (por datos, NO por operador modal — clave para headless/MCP):

```python
import math
pb = rig.pose.bones["upper_arm.L"]
pb.rotation_mode = 'XYZ'                 # o 'QUATERNION' (default). Cadenas simples: euler es legible
pb.rotation_euler.x = math.radians(35)
bpy.context.view_layer.update()          # recalcula matrices antes de leer/medir [ver: blender/bpy-scripting]
```

**Constraints** (`pose.constraint_add(type=...)` o `pb.constraints.new(type=...)`). Enum de tipos verificado 5.2; los que se usan en rigging:

| type | Para qué |
|---|---|
| `IK` | Cadena inversa (pierna/brazo hacia un target). `chain_count`, `target`, `pole_target` |
| `COPY_ROTATION` / `COPY_LOCATION` / `COPY_TRANSFORMS` | Un hueso sigue a otro (mecánica de FK a control) |
| `DAMPED_TRACK` / `TRACK_TO` / `LOCKED_TRACK` | Apuntar (ojos, cañón, cabeza) |
| `STRETCH_TO` | Estiramiento con preservación de volumen (squash&stretch, tentáculos) |
| `LIMIT_ROTATION` / `LIMIT_LOCATION` / `LIMIT_SCALE` | Topes de articulación (rodilla que no hiperextiende) |
| `CHILD_OF` (default) / `ARMATURE` | Parentado dinámico / bind multi-hueso |

```python
pb = rig.pose.bones["shin.L"]
ik = pb.constraints.new(type='IK')       # constraint por DATOS, no modal
ik.target = bpy.data.objects["IK_foot.L"]
ik.chain_count = 2                        # shin + thigh
```

**Custom shapes** (widgets para animar cómodo — no viajan al FBX, se ignoran al exportar): `pb.custom_shape = bpy.data.objects["WGT_circle"]`, `pb.custom_shape_scale_xyz`, `bone.show_wire = True`. Convención: una colección `WGT_` con la geometría de los controles, excluida del render.

**Bone Collections** (Blender **4.0+** reemplazó los viejos *bone layers* y *bone groups* por una sola cosa: `armature.collections`, verificado — el atributo `bone_collections` NO existe). Organizan el rig en capas mostrables/ocultables/solo:

```python
arm = rig.data
defo = arm.collections.new("DEF")         # huesos de deformación
ctrl = arm.collections.new("CTRL")        # controles
for b in arm.bones:
    (defo if b.use_deform else ctrl).assign(b)   # assign toma un Bone (bones/edit_bones)
ctrl.is_visible = True
```

Operadores UI equivalentes: `armature.collection_create_and_assign`, `collection_assign`, `collection_unassign`, `collection_move`. Los controles en su colección + huesos deform en otra deja el rig limpio para el animador y facilita exportar solo deform.

---

## 5. Skinning: parentar la malla al armature

El bind se hace en **Object Mode**: seleccionar la **malla primero**, el **armature al final** (queda activo), `Ctrl+P`. Opciones (`object.parent_set(type=...)`, enum verificado 5.2):

| `type` | UI "Set Parent To" | Qué crea |
|---|---|---|
| `ARMATURE_AUTO` | With Automatic Weights | Modificador Armature **+ vertex groups con pesos auto** (bone heat / algoritmo de distancia). El punto de partida normal |
| `ARMATURE_ENVELOPE` | With Envelope Weights | Pesos por envolturas de hueso (rápido, tosco; útil de arranque en criaturas) |
| `ARMATURE_NAME` | With Empty Groups | Modificador + grupos **vacíos** (para pintar todo a mano) |
| `ARMATURE` | (Object) | Solo el modificador, sin grupos |

```python
import bpy
mesh = bpy.data.objects["Hero_Mesh"]; rig = bpy.data.objects["Hero_Rig"]
for o in bpy.context.selected_objects: o.select_set(False)
mesh.select_set(True); rig.select_set(True)
bpy.context.view_layer.objects.active = rig       # el armature DEBE ser el activo
bpy.ops.object.parent_set(type='ARMATURE_AUTO')   # crea modifier Armature + vertex groups auto
```

El **modificador Armature** (`mesh.modifiers.new("Armature", 'ARMATURE')`, `.object = rig`) tiene `use_vertex_groups=True` (default) y `use_bone_envelopes=False` (default). Solo deforman los huesos con `bone.use_deform=True` que tienen un vertex group del mismo nombre. Alternativa al parent: `paint.weight_from_bones(type='AUTOMATIC')` (o `'ENVELOPES'`) reproyecta pesos desde los huesos sobre una malla ya bindeada.

**Límite de influencias para Unity:** Unity importa por defecto hasta **4 huesos por vértice** (skinWeights). Recortar en Blender evita sorpresas:

```python
bpy.context.view_layer.objects.active = mesh
bpy.ops.object.vertex_group_limit_total(limit=4)   # máx 4 influencias/vértice (verificado, default 4)
bpy.ops.object.vertex_group_normalize_all()        # re-normaliza a 1.0 tras el recorte
```

## 6. Weight Paint: pesos a mano

Se entra **desde la malla**: seleccionar la malla, cambiar a **Weight Paint** (dropdown de modo o `Ctrl+Tab`). Para probar la deformación mientras pintas, el patrón es tener el armature en Pose Mode a la vez: seleccionar el armature → Pose Mode → seleccionar la malla y entrar a Weight Paint; con **Ctrl+click sobre un hueso** lo haces el grupo activo y posas para ver el efecto. `rig.show_in_front = True` (propiedad del Object, no del armature data) para ver los huesos.

Escala de color: **azul = 0** (sin influencia) → **rojo = 1** (influencia total). Herramientas (brushes): **Draw**, **Blur**, **Average**, **Smear**, **Gradient** (`paint.weight_gradient`). Ajustes de brush: Weight (valor objetivo), Strength, Radius; modos Add/Subtract/Mix.

Overlays imprescindibles (header ‣ Overlays de Weight Paint): **Weight Contours**, **Zero Weights** (marca vértices sin peso — los que se quedan pegados al origen), y ver el armature con **show_in_front**. Opciones de brush: **Auto Normalize** (mantiene la suma de pesos = 1 al pintar), **Restrict to selection**, **X Mirror** (pinta simétrico usando naming `.L/.R`).

Operadores de limpieza de pesos (Object o Weight Paint mode, verificados 5.2):

| Operador | Efecto |
|---|---|
| `object.vertex_group_normalize` / `vertex_group_normalize_all` | Escala pesos para que sumen 1.0 (uno / todos) |
| `object.vertex_group_limit_total(limit=4)` | Deja las N influencias más fuertes por vértice |
| `object.vertex_group_clean(limit=0.01)` | Borra pesos por debajo de un umbral (elimina influencias basura) |
| `paint.weight_from_bones(type='AUTOMATIC')` | Re-calcula pesos desde los huesos |

> **Weight paint por MCP/headless es el punto débil.** El brush `paint.weight_paint` es un **operador modal** (necesita trazos de mouse): NO es operable ni por MCP ni por `blender -b` [ver: blender/blender-mcp-operativo §operadores modales]. Sin ojos, las vías reales son: (a) auto weights por `parent_set(type='ARMATURE_AUTO')`; (b) pesos por datos con `vertex_group.add([idx], peso, 'REPLACE')`; (c) los operadores NO modales de arriba (normalize/limit/clean); (d) `weight_from_bones`. El ajuste fino a pincel se le deja al humano.

## 7. Verificación sin ojos humanos

La deformación se **mide**, no se adivina. Tres capas de evidencia (patrón de [ver: blender/blender-mcp-operativo §kit de evidencia]):

**a) Posar por código y medir cuánto se movió la malla** (verificado headless en 5.2 — un hueso rotado 90° mueve la punta √2≈1.414 m):

```python
import bpy, math
def punta_mundo(mesh):
    dg = bpy.context.evaluated_depsgraph_get()      # malla EVALUADA con el modifier Armature
    ev = mesh.evaluated_get(dg); m = ev.to_mesh()
    top = max(m.vertices, key=lambda v: (mesh.matrix_world @ v.co).z)
    co = mesh.matrix_world @ top.co; ev.to_mesh_clear(); return co
mesh = bpy.data.objects["Hero_Mesh"]
antes = punta_mundo(mesh)
rig.pose.bones["upper_arm.L"].rotation_euler = (math.radians(90),0,0)
bpy.context.view_layer.update()
print("delta:", round((punta_mundo(mesh)-antes).length,3), "-> deforma" )  # ~0 = el hueso NO deforma esa zona
```

**b) Auditar huesos y vertex groups por script** (el fallo más común: hueso deform sin su grupo, o vértices sin peso):

```python
arm = rig.data
deform = [b.name for b in arm.bones if b.use_deform]
vgs = {vg.name for vg in mesh.vertex_groups}
print("bones:", len(arm.bones), "| deform:", len(deform))
print("deform SIN vertex group (no deforman):", [b for b in deform if b not in vgs])
print("vertex groups SIN hueso (basura):", [v for v in vgs if v not in {b.name for b in arm.bones}])
for v in mesh.data.vertices:
    if not v.groups or sum(g.weight for g in v.groups) < 1e-4:
        print("VÉRTICE SIN PESO:", v.index, "(se pega al origen)"); break
```

**c) Render de evidencia del rig posado** desde 2–4 ángulos (Workbench/EEVEE a archivo, leer la imagen) — para ver reventones de codo/rodilla, pinch en axilas, caras invertidas [ver: blender/blender-mcp-operativo §screenshot vs render]. Un rig NO está "listo" sin al menos una evidencia numérica (a/b) y una visual (c) de la misma sesión.

## 8. Auto-Rig Pro: la alternativa de pago (game-ready)

Addon de Blender de pago que colapsa el flujo entero — rig + skin + retarget + export a motor — en pocos clics [ver: blender/addons-ecosistema]. Verificado contra su doc oficial (lucky3d.fr/auto-rig-pro/doc, jul-2026):

| Módulo | Qué hace |
|---|---|
| **Smart** (auto-detección) | Colocas unos markers (barbilla, muñecas, tobillos…) y "Match to Rig" genera el esqueleto completo con IK/FK, faciales y controles |
| **Skin / Bind** | Bindeo automático con su propio algoritmo (mejor que auto weights nativo en mallas densas) |
| **Remap** (retarget) | Transfiere animación/mocap entre esqueletos distintos (Mixamo → tu rig, etc.) |
| **Game Engine exporter** | Exporta FBX **deform-only** con tipos `Universal` / `Humanoid` / `Unreal`: renombra huesos (p.ej. a Mannequin de Unreal o mapa Humanoid), añade **root bone** único, hornea *bend bones*, y limpia el rig de control — resuelve de una la danza de settings de FBX (Only Deform Bones, Add Leaf Bones OFF…) |

**Cuándo se paga solo:** producción de personajes en volumen, pipelines con retarget de mocap, y equipos que exportan seguido a Unity/Unreal (el Game Engine exporter ahorra horas de configurar y depurar el FBX manualmente [ver: blender/import-export §settings FBX]). **Cuándo NO:** un rig simple y único → Rigify nativo (gratis, incluido) [ver: rigify] cubre humanoides estándar sin coste.

**Precio (jul-2026):** de pago, vendido en **Superhive Market** (ex-Blender Market) + Gumroad, con la versión completa (Auto-Rig Pro) y una **Quick Rig** más barata (rig+export sin faciales/remap). El monto exacto **no se pudo verificar en esta sesión** (el marketplace bloqueó el fetch) — confirmar en la página de compra antes de citarlo. NO inventar la cifra.

## 9. Organización del .blend del rig

Estructura sugerida (alineada con [ver: blender/organizacion-blend]):

```text
Scene Collection
└── hero                     ← colección raíz = nombre del asset (lo que se exporta)
    ├── hero-final           ← malla low-poly + el objeto Armature (lo único que va a Unity)
    ├── hero-widgets         ← WGT_ custom shapes (Disable in Renders; no exporta)
    └── hero-ref             ← blueprints/referencia (no seleccionable)
```

- **Naming:** el objeto Armature con nombre limpio y estable (el esqueleto es contrato con Unity: renombrar huesos tras el primer import = reconfigurar el Avatar [ver: unity/animacion-unity]). Huesos con sufijo `.L/.R`; deform con prefijo o `use_deform` marcado, controles en su bone collection.
- **Un rig = un armature dentro de la colección del asset**; la malla y el armature juntos en `-final`. Los widgets fuera del render.
- El pivote/origen del objeto en el suelo entre los pies (root motion en Unity parte de ahí [ver: unity/animacion-unity §Root Motion]).

## 10. Al motor: lo mínimo que este rig necesita para Unity

El detalle completo del export está en [ver: blender/import-export] y el lado Unity en [ver: unity/animacion-unity] — aquí solo el puente que toca al rigger:

| Punto | Ajuste |
|---|---|
| Huesos basura `_end` | Export FBX con **Add Leaf Bones OFF** (`add_leaf_bones=False`) |
| Fuera controles/widgets | **Only Deform Bones** (`use_armature_deform_only=True`) — solo huesos con `use_deform` |
| Influencias/vértice | Limitar a **4** en Blender (`vertex_group_limit_total(limit=4)`) — lo que Unity espera |
| Humanoid retarget | Unity necesita **≥15 huesos** en jerarquía tipo humano; mapping verde=OK / rojo=falla; **Enforce T-Pose** antes de generar el Avatar (verificado, doc Unity) |
| Generic vs Humanoid | Criaturas/mecánicos → **Generic** con **Root Node** para root motion; bípedos con retarget → **Humanoid** |
| Nunca | `bake_space_transform` (Apply Transform) con armature: rompe el rig (warning oficial) [ver: blender/import-export] |

En Unity: Rig tab → Animation Type (Humanoid/Generic) → Avatar Definition **Create From This Model** (o **Copy From Other Avatar** para reusar esqueleto). Humanoid abre **Muscles & Settings** (topes por músculo, **Translate DoF** solo en Chest/UpperChest/Neck/UpperLeg/Shoulder). **Avatar Mask** para animar por partes o aligerar clips. **Optimize Game Objects** aplana la jerarquía de huesos para rendimiento (exponer solo los transforms que gameplay necesita) [ver: unity/rendimiento-unity].

---

## Reglas prácticas

1. Antes de tocar nada: ¿en qué modo estás? Edit = huesos/rest, Pose = poses/constraints, Object = el rig entero. Confundirlos es el bug #1.
2. `armature.edit_bones` solo vive en Edit Mode: los scripts entran a Edit, editan, y salen a Object para confirmar.
3. Naming `.L/.R` desde el principio (`autoside_names`): Symmetrize, flip pose y el retarget Humanoid lo exigen.
4. Construir un lado, `symmetrize(direction='NEGATIVE_X')` para el otro — nunca modelar los dos a mano.
5. Roll consistente antes de skinnear (`calculate_roll`, `Ctrl+N`): rolls sucios se ven bien en rest y se retuercen al animar.
6. Bind = malla seleccionada + armature ACTIVO + `parent_set(type='ARMATURE_AUTO')`; los auto weights son el punto de partida, no el final.
7. Solo deforman los huesos con `use_deform=True` que tienen vertex group del mismo nombre — auditarlo por script.
8. Recortar a 4 influencias/vértice (`vertex_group_limit_total`) + `vertex_group_normalize_all` antes de exportar a Unity.
9. Pose y constraints por DATOS (`pose.bones[...].rotation_euler`, `.constraints.new`), nunca por operadores modales de transform — así funciona headless/MCP.
10. Weight paint a pincel es modal → imposible sin ojos: por MCP usar auto weights, `vertex_group.add`, y los ops no modales (normalize/limit/clean); el pulido fino, al humano.
11. Verificar deformación midiendo: posar por código y medir el desplazamiento de la malla evaluada (depsgraph), no confiar en "el script corrió".
12. Custom shapes en una colección `WGT_` excluida del render; no viajan al FBX.
13. Bone Collections (`armature.collections`, 4.0+) para separar DEF/CTRL — no los viejos "bone layers/groups".
14. Export con Add Leaf Bones OFF + Only Deform Bones ON; jamás Apply Transform con armature.
15. No renombrar huesos tras el primer import a Unity: rompe el Avatar y hay que reconfigurarlo.
16. Rig simple → Rigify (gratis); volumen/mocap/export a motor recurrente → evaluar Auto-Rig Pro.
17. "Listo" = una evidencia numérica (deform medida + audit de grupos) y una visual (render posado) de esta sesión.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Crear huesos por script y "no aparecen" | `edit_bones` solo en Edit Mode; entrar a Edit antes, salir a Object para confirmar el data-block |
| La malla no se mueve con el hueso | Falta el vertex group con el nombre exacto del hueso, o el hueso tiene `use_deform=False`; auditar con el script §7b |
| Vértices que se quedan pegados al origen | Sin peso alguno: overlay **Zero Weights** + `vertex_group_normalize_all`; revisar §7b |
| Symmetrize no copia nada | Falta naming `.L/.R`: correr `autoside_names` primero; y se refleja por **X global** |
| El rig se retuerce al animar aunque el rest se ve bien | Rolls inconsistentes: `calculate_roll` a un eje común (`Ctrl+N`) antes de skinnear |
| Deformación a "estrella"/pinch en articulaciones | Auto weights tosco: pintar/blur a mano o subir subdivisiones de la malla en codos/rodillas [ver: skinning-weights] |
| Weight paint por MCP no hace nada | El brush es modal: usar auto weights / `vertex_group.add` / ops no modales; el pincel es para el humano |
| Huesos `_end` basura en Unity | Add Leaf Bones OFF en el export FBX (`add_leaf_bones=False`) |
| Unity mete controles del rig como huesos | Only Deform Bones ON (`use_armature_deform_only=True`) |
| Avatar Humanoid no valida (mapping rojo) | Falta jerarquía de ≥15 huesos tipo humano o naming/pose incorrectos; **Enforce T-Pose** y remapear |
| El personaje "patina" o no avanza con la animación | Root motion mal: Generic necesita **Root Node**; revisar Bake Into Pose / Based Upon [ver: unity/animacion-unity] |
| Más de 4 influencias por vértice → deformación distinta en Unity | Recortar con `vertex_group_limit_total(limit=4)` en Blender |
| Snippet de la web con "bone layers"/"bone groups" que no existen | 4.0+ los unificó en `armature.collections`; verificar contra 5.2 [ver: blender/bpy-scripting §cambios 5.x] |

## Fuentes

- **Binario Blender 5.2.0 LTS local** (build 2026-07-14) — verificación directa: nombres de operador de `bpy.ops.armature.*` y `bpy.ops.pose.*`, enums y defaults de `calculate_roll` (`type` POS_X…CURSOR, `axis_flip`, `axis_only`), `symmetrize` (`direction` NEGATIVE_X/POSITIVE_X), `subdivide` (`number_cuts`), `bone_primitive_add`, `object.parent_set` (`type` ARMATURE_AUTO/ENVELOPE/NAME…), `object.vertex_group_limit_total` (`limit`=4), `paint.weight_from_bones` (AUTOMATIC/ENVELOPES), `pose.constraint_add` (enum de tipos), API de datos (`armature.edit_bones`, `armature.collections`, `pose.bones[].constraints`, modificador Armature `use_vertex_groups`/`use_bone_envelopes`, `display_type`), y prueba empírica de deformación posada por código (bend 90° → punta se mueve √2).
- **Unity Manual — Configuring the Avatar** (docs.unity3d.com/Manual/ConfiguringtheAvatar.html) — mínimo de 15 huesos tipo humano, mapping verde/rojo, Enforce T-Pose, pestaña Muscles & Settings.
- **Unity Manual — Avatar Creation and Setup** (AvatarCreationandSetup.html) — Animation Type Humanoid, Avatar Definition Create From This Model vs Copy From Other Avatar, reuso de esqueleto.
- **Unity Manual — Muscle Definitions / Muscles & Settings** (MuscleDefinitions.html) — músculos vs huesos, topes por músculo, **Translate DoF** (Chest/UpperChest/Neck/UpperLeg/Shoulder) y su coste.
- **Unity Manual — Avatar Mask** (class-AvatarMask.html) — máscara por partes del cuerpo (humanoid) y por transforms (generic), usos import/layer.
- **Unity Manual — Root Motion** (RootMotion.html) — Body/Root Transform, Bake Into Pose, Based Upon (Body/Feet/Original), Root Node para rigs Generic.
- **Auto-Rig Pro — documentación oficial** (lucky3d.fr/auto-rig-pro/doc) — Smart auto-detección, skinning, Remap/retarget, Game Engine exporter (Universal/Humanoid/Unreal, renombrado de huesos, root bone). Precio no verificado esta sesión (marketplace bloqueó el fetch).
- **Bases sintetizadas de El Estudio:** [ver: blender/bpy-scripting] (modos Object/Edit, stale data, modales, headless), [ver: blender/blender-mcp-operativo] (bucle de evidencia, límite de operadores modales, render de verificación), [ver: blender/import-export] (settings FBX de armature: Add Leaf Bones OFF, Only Deform Bones, Apply Transform prohibido con rig), [ver: unity/animacion-unity] (Humanoid/Generic, Avatar Mask, IK, costes de rig en Mecanim), [ver: blender/organizacion-blend] (colecciones y naming).
