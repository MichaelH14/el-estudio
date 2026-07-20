# IK, FK y constraints

> **Cuando cargar este archivo:** al armar el **rig de control** de un personaje o mecanismo en Blender 5.2 — decidir FK vs IK por miembro, montar constraints en Pose Mode (IK, Copy Rotation, Damped Track, Limit Rotation, Child Of), configurar cadena IK con pole target, poner custom shapes a los controles, o preparar el **bake control→deform** antes de exportar a Unity. Asume que el esqueleto de deformación ya existe [ver: esqueletos-armature] y que los weights ya están pintados [ver: skinning-weights]. La deformación en sí (dual-quat, corrective) vive en [ver: deformacion]; el handoff a Unity en [ver: rig-a-unity].

Versión: **Blender 5.2 LTS** + **Unity 6 (Mecanim/Humanoid)** + **Auto-Rig Pro 2026**. Operadores y propiedades `bpy` verificados contra el manual/API 5.2 (jul-2026).

---

## 1. FK vs IK: qué es cada uno y cuándo

**FK (Forward Kinematics)** — posas de la raíz a la punta: rotas hombro → codo → muñeca, cada hijo hereda la transform del padre. Es cómo funciona un armature *sin* constraints. Control total sobre el ángulo de cada hueso; la punta va "a donde caiga".

**IK (Inverse Kinematics)** — posicionas la *punta* de la cadena (el "goal") y Blender resuelve automáticamente los ángulos de los huesos padres para alcanzarla. "Como mover el dedo de alguien hace que su brazo lo siga" (manual). La punta queda *fija en el mundo* aunque muevas el cuerpo.

| | FK | IK |
|---|---|---|
| Controlas | El **ángulo** de cada hueso | La **posición** de la punta (goal) |
| La punta | Flota, sigue al padre | Se queda clavada donde la pones |
| Bueno para | **Arcos** naturales: brazos que saludan, cola que ondea, ataques amplios, cualquier movimiento donde la mano "vuela" | **Contacto**: pies plantados en el suelo, manos en un volante/arma/pared, empujar algo, trepar |
| Malo para | Mantener un pie quieto mientras el cuerpo baja (hay que corregir cada frame) | Arcos sueltos (la punta "se pega" y el movimiento se siente rígido) |
| Coste de animar | Alto si algo debe quedarse quieto | Bajo para contactos; el codo/rodilla necesita guía (pole) |

**Regla operativa:** piernas casi siempre IK (pies plantados). Brazos: **depende del plano** — combate cuerpo a cuerpo y gestos = FK; apoyarse, cargar, escalar, dos manos en un arma = IK. Por eso un rig de personaje serio ofrece **IK/FK switch** por brazo/pierna (§4). Columna y cuello: normalmente FK (o un IK spline para colas/serpientes [ver: rigs-mecanicos]).

---

## 2. Bone constraints en Pose Mode: los que arman el rig de control

Un constraint controla automáticamente loc/rot/scale de un hueso a partir de un target. Se añaden en **Properties ‣ Bone Constraint** (icono hueso+cadena) en **Pose Mode**, o `Shift`-`Ctrl`-`C` en el viewport. Cada hueso tiene un **stack** que se evalúa de arriba abajo; cada constraint tiene **Influence** (0–1, animable — así se encienden/apagan a lo largo de una animación).

**Visual transform** (clave para entender constraints): el constraint da al hueso una transform *visual* separada de la "base" del panel Transform. Puedes ver el hueso en un sitio mientras sus valores de Location siguen en (0,0,0). Para "congelar" ese resultado en keyframes: **Apply Visual Transform** o el **bake** (§8).

Data API preferida para MCP/headless (evita problemas de contexto de los operadores):

```python
import bpy
arm = bpy.data.objects["Armature"]
pb  = arm.pose.bones["forearm.L"]
c = pb.constraints.new(type='IK')      # crea el constraint en el hueso
c.target = arm; c.subtarget = "IK_hand.L"
```

Los constraints que arman un rig de control (todos verificados en el manual 5.2):

| Constraint | `type` | Qué hace | Para qué en el rig |
|---|---|---|---|
| **Inverse Kinematics** | `IK` | Rota toda una cadena para alcanzar el target (§3) | El corazón de brazos/piernas IK |
| **Copy Rotation** | `COPY_ROTATION` | Fuerza la rotación del hueso a la del target; ejes X/Y/Z, **Invert**, **Mix** (Replace/Add/Before/After Original), Order, Target/Owner space | DEF que copia del control FK o IK (base del IK/FK switch); dedos que siguen una palanca |
| **Copy Location** | `COPY_LOCATION` | Copia la posición del target; ejes, Invert, **Offset**. ⚠️ **No hace nada en huesos connected** (su posición la fija el padre) | Pegar un control a un helper; ojos que siguen un empty |
| **Damped Track** | `DAMPED_TRACK` | "Look At"/Aim con **swing puro** (minimiza roll), sin eje Up. **Track Axis** (para huesos: **Y**; negativo = apunta al revés) | Ojos, cabeza que mira, cadenas de tentáculo/cola que apuntan a un goal |
| **Limit Rotation** | `LIMIT_ROTATION` | Clampea el ángulo Euler por eje a un rango (checkbox + min/max por X/Y/Z), Order, **Affect Transform**. ⚠️ **No sirve en huesos bajo IK** — usar el Limit del panel IK del hueso (§3) | Bisagras: rodilla/codo/mandíbula que solo giran en un eje y rango |
| **Child Of** | `CHILD_OF` | Parenta como hijo pero con **Influence animable** → cambiar de padre en el tiempo; Location/Rotation/Scale por eje, **Set Inverse** | Arma que pasa de una mano a otra; prop que se suelta/agarra. No para cadenas de huesos |

Otros que aparecen en rigs y conviene tener presentes: **Copy Transforms** (loc+rot+scale de golpe — se usa para "aplicar constraints después de un IK" copiando el resultado a otra cadena), **Stretch To**, **Locked Track**, **Track To** (con eje Up, a diferencia de Damped), **Armature** (parenting ponderado a varios huesos, mejor que varios Child Of), **Limit Location/Scale**, **Transformation**, **Spline IK** [ver: rigs-mecanicos].

**Owner/Target space** (aparece en casi todos): World / Pose / **Local** / Local With Parent / Custom Space. Para lógica de rig entre huesos casi siempre **Local Space** o Pose Space; World rompe cuando mueves el personaje.

---

## 3. El IK constraint en detalle (settings EXACTOS)

Añadir rápido: seleccionar el **hueso punta** de la cadena → `Shift`-`I` (**Add IK to Bone** = `bpy.ops.pose.ik_add(with_targets=True)`), o crearlo a mano y asignar target. El IK es especial: **ignora su posición en el stack y corre después de todos los demás constraints** del hueso. Para encadenar constraints tras un IK, hay que copiar la transform final a otra cadena con **Copy Transforms**.

Opciones del constraint (UI ‣ propiedad `bpy`, verificadas):

| UI | `bpy` | Qué hace |
|---|---|---|
| **Target** | `target` (+`subtarget`) | Objeto/hueso que la punta persigue. Puede ir **sin target**: entonces mueves la punta libre y solo se constriñen sus ancestros |
| **Pole Target** | `pole_target` (+`pole_subtarget`) | Objeto/hueso que decide el **roll** de la cadena = la **posición del codo/rodilla**. Sin él, el codo puede voltearse solo |
| **Pole Angle** | `pole_angle` | Offset de rotación del pole, rango **±π rad (±180°)**, default **0.0**. Ajústalo hasta que codo/rodilla apunte a donde debe **sin flip** (valores típicos 0, −90° o +90° según cómo esté orientado el hueso raíz) |
| **Iterations** | `iterations` | Máx. iteraciones del solver (default 500; bajar si hay coste, subir si no converge) |
| **Chain Length** | `chain_count` | Nº de huesos afectados desde la punta hacia arriba. **1** = solo ese hueso; **2** = hueso+padre; **0** = toda la cadena hasta la raíz. Para un brazo (upperarm+forearm) → **2** |
| **Use Tail** | `use_tail` | Usar la **cola** del hueso como fin de cadena (default). Off = usar la cabeza |
| **Stretch** | `use_stretch` | Permite que los huesos escalen para alcanzar el target — solo si su **IK Stretch** > 0. ⚠️ El stretch **no lo maneja bien FBX** (§9) |
| **Weight Position** | `use_location`+`weight` | Que la punta iguale la **posición** del target, y con cuánta fuerza frente a otras cadenas (trees) |
| **Rotation** | `use_rotation`+`orient_weight` | Que la punta iguale la **rotación** del target (activar en el goal del pie para plantar la planta al piso) |
| **Influence** | `influence` | Fuerza global 0–1 (animable → base del IK/FK switch) |

**Panel del hueso (Properties ‣ Bone ‣ Inverse Kinematics, Pose Mode)** — restringe los grados de libertad de cada hueso de la cadena (la página del manual está en stub, pero las propiedades `bpy` son estándar):

| Propiedad | `bpy` (pose bone) | Uso |
|---|---|---|
| **Lock IK X/Y/Z** | `lock_ik_x/y/z` | Bloquear ejes: una rodilla/codo debe girar en **un solo eje** (bisagra) → lockear los otros dos |
| **Limit / Min-Max X/Y/Z** | `use_ik_limit_x` + `ik_min_x`/`ik_max_x` | Rango angular por eje (rodilla no se dobla hacia atrás) |
| **Stiffness X/Y/Z** | `ik_stiffness_x/y/z` | Resistencia a doblar en ese eje (reparte el bend por la cadena) |
| **IK Stretch** | `ik_stretch` | 0 = sin estirar (lo normal para juego); >0 habilita el Stretch del constraint |

**Solver:** Properties ‣ Armature ‣ Inverse Kinematics = **Standard** (usar este casi siempre) o **iTaSC** (multi-constraint, distancia/simulación; nicho). **Auto IK** (Pose Mode ‣ Tool ‣ Pose Options ‣ Auto IK) = IK temporal sin constraints para *posar* rápido una cadena FK; no es un rig, no se exporta.

```python
# Brazo IK completo (headless/MCP). Hueso punta = forearm.L
arm = bpy.data.objects["Armature"]
pb  = arm.pose.bones["forearm.L"]
ik = pb.constraints.new(type='IK')
ik.target, ik.subtarget = arm, "IK_hand.L"      # goal de la muñeca
ik.pole_target, ik.pole_subtarget = arm, "POLE_elbow.L"
ik.pole_angle = -1.5708                          # -90° en radianes; ajustar hasta que no haya flip
ik.chain_count = 2                               # upperarm + forearm, no toca el hombro
# hinge del codo: solo dobla en X
fb = arm.pose.bones["forearm.L"]
fb.lock_ik_y = fb.lock_ik_z = True
fb.use_ik_limit_x = True; fb.ik_min_x, fb.ik_max_x = 0.0, 2.6  # rad
```

---

## 4. IK/FK switch (a nivel concepto)

Un rig de producción no elige IK *o* FK de una vez: ofrece **ambos por miembro** y un interruptor. El patrón canónico (el que implementa Rigify [ver: rigify]):

1. **Tres cadenas** por miembro: `FK_*` (controles de rotación), `IK_*` (goal + pole), y `DEF_*` (los huesos de deformación con weights).
2. Los `DEF_*` no se animan directo: cada uno lleva un **Copy Rotation/Copy Transforms** desde su equivalente FK **y** otro desde el IK, con la **Influence cruzada** por un **driver** ligado a una custom property `IK_FK` (0 = FK, 1 = IK).
3. Cambiar la propiedad mezcla suave entre ambos modos. El **snap** (saltar de FK a IK sin que el brazo "salte") requiere igualar la pose antes de switchear — Rigify trae operadores de snap; en rigs a mano es un script.

Para el motor esto es **irrelevante**: solo los `DEF_*` se hornean y exportan (§7–8). El switch existe únicamente para *producir* la animación en Blender.

---

## 5. Control rig vs deform rig: la separación que define todo

Dos poblaciones de huesos en el mismo armature:

| | **Deform bones** (`DEF_*`) | **Control bones** (controles, `CTRL_/IK_/POLE_/FK_/MCH_`) |
|---|---|---|
| Tienen weights | **Sí** (deforman la malla) [ver: skinning-weights] | **No** |
| Los mueve el animador | No directo (los mueven constraints/controles) | **Sí** — es lo que agarra |
| Flag Deform | `bone.use_deform = True` | `use_deform = False` |
| Van a Unity | **Sí** | **No** — se descartan (§7) |
| Custom shape | No (o stick) | **Sí** — widgets (§6) |
| Collection | "DEF"/"Deform" | "CTRL", "MCH" (mechanism), "Widgets" |

Organizar con **Bone Collections** (5.x; el reemplazo de las viejas "layers") y prefijos consistentes es lo que hace exportable el rig: el bake y el export filtran por el flag Deform / la collection. Los helper bones internos (`MCH_`, targets de constraint) tampoco deforman y tampoco se exportan.

- Fija el flag por lote: `for b in arm.data.bones: b.use_deform = b.name.startswith("DEF")`
- El export FBX con **Only Deform Bones** (`use_armature_deform_only=True`) tira controles y mechanism solo — pero exige que los DEF estén bien marcados [ver: blender/import-export].

---

## 6. Custom bone shapes (widgets): un rig usable

Un control con forma de hueso octaédrico es imposible de agarrar. Se le asigna una malla como **template visual** (círculo para rotación FK, cubo para el goal IK, flecha para el pole…). Panel **Bone ‣ Viewport Display ‣ Custom Shape** (Object/Pose Mode). Verificado en el manual:

| UI | `bpy` (pose bone) | Nota |
|---|---|---|
| **Custom Object** | `custom_shape` | La malla-widget que representa el hueso |
| Translation / Rotation / Scale | `custom_shape_translation/_rotation_euler/_scale_xyz` | Ajuste visual del widget |
| **Scale to Bone Length** | `use_custom_shape_bone_size` | Escala el widget por el largo del hueso (haz el template de 1 unidad en Y) |
| **Override Transform** | `custom_shape_transform` | Otro hueso define dónde se dibuja el widget |
| **Wireframe / Wire Width** | `bone.show_wire`† / `custom_shape_wire_width` | Widget en wire aunque el viewport esté sólido |

† `show_wire` vive en el **Bone** (datablock del armature: `arm.data.bones["forearm.L"].show_wire`), no en el pose bone — a diferencia de todas las demás filas de esta tabla, que sí son propiedades del **pose bone** (`pb.custom_shape`, etc.). Verificado contra `bpy.types.Bone`/`bpy.types.PoseBone` en Blender 5.2 real (no hay `pose_bone.use_custom_shape_wire`, esa propiedad no existe).

Reglas del sistema (manual): **los custom shapes nunca se renderizan** (solo viewport), la transform del template se ignora, el **origen del widget se coloca en la raíz del hueso** y su **eje Y se alinea con la dirección del hueso**. Convención: una collection **"WGT"** oculta con todas las mallas-widget (prefijo `WGT-`), fuera del export.

```python
wgt = bpy.data.objects["WGT-circle"]
pb  = arm.pose.bones["FK_upperarm.L"]
pb.custom_shape = wgt
pb.use_custom_shape_bone_size = True
```

---

## 7. Por qué Unity NO necesita el control rig

Unity anima **los deform bones y nada más**. El control rig (IK, poles, switches, widgets) es andamiaje para *generar* la animación en Blender; una vez horneada (§8), el motor solo ve keyframes sobre los DEF. Además Unity **descarta jerarquía de más** activamente:

| Ajuste (Model ‣ Rig, Unity 6) | Efecto | Valor game |
|---|---|---|
| **Animation Type** | Humanoid (2 brazos/2 piernas, retarget + IK) vs **Generic** (root node, más barato) | Generic si no necesitas retargeting; Humanoid si compartes clips entre esqueletos [ver: unity/animacion-unity] |
| **Avatar Definition** | Create From This Model / Copy From Other Avatar | Un solo Avatar para el modelo; los FBX `@anim` copian ese Avatar |
| **Skin Weights** | Máx. huesos por vértice; **Standard = 4** (recomendado) | Limitar a 4 en Blender antes de exportar (§8) |
| **Strip Bones** | Solo añade al SkinnedMeshRenderer huesos **con weights** | ON → los controles sin weight ni entran |
| **Optimize Game Object** | **Elimina la jerarquía de Transforms** y la guarda en Avatar+Animator; los SMR usan el **esqueleto interno** de Unity → mucho más rápido | ON para characters de gameplay; expón sockets con **Extra Transforms to Expose** |

Es decir: aunque colaras controles, **Strip Bones + Optimize Game Object** los borran. Un Humanoid Avatar mapea la malla a **≥15 huesos** requeridos en pose **T** (Configure ‣ Enforce T-Pose); los muscles (Muscles & Settings, Translate DoF) definen el rango de movimiento. Nada de esto quiere tus IK handles. Detalle del handoff (Avatar, retarget, root motion) en [ver: rig-a-unity].

---

## 8. Bake del control rig a los deform bones (antes de exportar)

FBX **no lleva constraints** — solo el **resultado horneado como keyframes** (verificado [ver: blender/import-export]). Si exportas sin hornear, los DEF (movidos por constraints, no por keys) llegan a Unity **quietos**. El bake convierte visual transform → keyframes reales sobre los DEF:

**`Pose ‣ Animation ‣ Bake Action`** = `bpy.ops.nla.bake(...)` (firma verificada):

```python
bpy.ops.nla.bake(
    frame_start=1, frame_end=60,
    only_selected=True,          # selecciona ANTES solo los huesos DEF
    visual_keying=True,          # CLAVE: hornea el resultado de los constraints
    clear_constraints=True,      # quita los constraints tras hornear (deja keys puros)
    clear_parents=False,
    use_current_action=True,
    bake_types={'POSE'},
)
```

Flujo game-ready:
1. Termina la animación con el rig de control completo.
2. **Duplica** la acción (o el .blend) — el bake es destructivo con `clear_constraints`.
3. Selecciona **solo los DEF** en Pose Mode; Bake Action con `visual_keying=True`.
4. Limita weights a 4 por vértice: `bpy.ops.object.vertex_group_limit_total(limit=4)` (en Object Mode sobre la malla) — coincide con Skin Weights = Standard de Unity.
5. Exporta con **Only Deform Bones** + **Add Leaf Bones OFF** (`add_leaf_bones=False`) [ver: blender/import-export].
6. Para varios clips: convención **`Modelo@idle.fbx` / `Modelo@walk.fbx`** — cada uno solo armature + acción horneada, mismo esqueleto y nombres [ver: rig-a-unity].

⚠️ **Nunca** apliques transforms (Apply Rotation/Scale) al armature en pose ni `bake_space_transform` con rigged assets — rompe el rig (warning oficial). Aplica solo en Object Mode sobre el rest pose.

---

## 9. Auto-Rig Pro (ARP) 2026: el atajo con exporter propio

Addon de pago para Blender que autogenera un rig completo (control + deform) con detección "Smart", y — lo importante para juego — trae un **exporter dedicado** que hace el bake control→deform y el remap por ti. Verificado en la doc oficial (jul-2026):

- **`File ‣ Export ‣ Auto-Rig Pro FBX/GLTF`**: exporta esqueleto **Humanoid** (mapea al Avatar de Unity) o **Universal** (cualquier rig). Formato FBX o GLTF (GLTF requiere Blender ≥3.4). "Full support in Unity, Unreal (FBX), Godot".
- **Hornea el rig de control a los deform bones automáticamente** al exportar. Los custom bones (ropa, pelo, props) **no se exportan salvo que los marques**: prefijo **`cc_`**, botón dedicado, o propiedad `cc`/`custom_bone`. Si están parentados a un control FK, el exporter **re-parenta al deform bone** correspondiente solo (`cc_watch` bajo `c_forearm_fk` → sale bajo `forearm_stretch`).
- **Requisitos que replican los de esta base:** escena con **Unit Scale = 1**, personaje a ~1 unidad = 1 m; **desactivar "Preserve Volume"** en el Armature modifier (dual-quaternion no existe en engines) para ver la deformación real; **stretch off** (o usar Soft-Link / No Parents) porque **FBX no maneja stretch/scale no uniforme** en cadenas.
- **Precio: NO VERIFICADO al jul-2026** (Blender Market/Superhive devolvió 403). Históricamente addon de pago en el rango de decenas de USD; confirmar en superhive.com/blendermarket antes de citar cifra. Alternativas: **Rigify** (gratis, bundled) [ver: rigify], Mixamo (auto-rig web gratis, humanoides).

ARP no cambia los principios: sigue habiendo control rig que NO se exporta y deform bones que sí. Solo automatiza el bake y el naming.

---

## Reglas prácticas

1. Piernas → IK (pies plantados); brazos → IK/FK switch por el plano de acción; columna/cuello → FK. No pongas todo en IK "por si acaso".
2. Marca **`use_deform`** correcto en cada hueso desde el principio: DEF = True, controles/MCH = False. Es lo que hace exportable el rig.
3. Separa poblaciones en **Bone Collections** con prefijos (`DEF_`, `CTRL_`/`IK_`/`FK_`, `MCH_`, `WGT-`) — el bake y el export filtran por ahí.
4. IK de brazo/pierna: **Chain Length = 2** (no arrastres el hombro/cadera), **pole target** siempre, ajusta **Pole Angle** hasta que no haya flip.
5. Rodilla/codo = bisagra: **Lock IK** en dos ejes + **Limit** de rango en el eje que dobla; no dejes que hiperextienda.
6. `Limit Rotation` **no funciona bajo IK** — usa el Limit del panel IK del hueso. `Copy Location` **no afecta huesos connected**.
7. Damped Track para aim/ojos/tentáculos con **Track Axis = Y**; Track To solo si necesitas eje Up controlado.
8. Child Of (Influence animable) para props que cambian de mano; para varios padres ponderados, prefiere el constraint **Armature**.
9. Ponle **custom shape** a TODO control que el animador agarre; widgets en collection `WGT-` oculta, template de 1 unidad en Y con Scale to Bone Length.
10. Constraints entre huesos en **Local/Pose Space**, nunca World (se rompe al mover el personaje).
11. Guarda el .blend/acción antes del bake: `clear_constraints=True` es destructivo.
12. **Bake Action con `visual_keying=True`** sobre solo los DEF antes de exportar — sin esto los DEF llegan quietos a Unity.
13. Limita weights a **4/vértice** (`vertex_group_limit_total(limit=4)`) = Skin Weights Standard de Unity.
14. Export: **Only Deform Bones + Add Leaf Bones OFF**; en Unity **Strip Bones + Optimize Game Object ON**.
15. Nunca Apply Rotation/Scale ni `bake_space_transform` en el armature con animación; aplica solo en rest, Object Mode.
16. Un clip por FBX `@`: mismo esqueleto y nombres, solo armature + acción horneada.
17. Si usas ARP: marca custom bones con `cc_`, desactiva Preserve Volume, stretch off; el resto lo hornea su exporter.
18. Todo "rig listo" = animación de prueba **horneada, exportada y vista deformando en Unity**, no "los constraints se ven bien en Blender".

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Exportas y el personaje llega a Unity en T-pose inmóvil pese a tener animación | Los DEF los movían constraints, no keys: **Bake Action `visual_keying=True`** sobre los DEF antes de exportar; FBX no lleva constraints |
| El codo/rodilla se voltea (flip) al mover el goal IK | Falta **Pole Target**, o el **Pole Angle** está mal: asigna pole y ajusta el ángulo (0/−90/+90°) hasta que apunte estable |
| El IK arrastra el hombro/cadera entera | **Chain Length** demasiado alto: brazo = 2, no 0 |
| La rodilla se dobla hacia atrás o hiperextiende | **Lock IK** en 2 ejes + **Limit** min/max en el eje bisagra (panel IK del hueso) |
| `Limit Rotation` "no hace nada" en un hueso de la cadena IK | No funciona bajo IK: usa el **Limit** del panel Inverse Kinematics del hueso |
| `Copy Location` sin efecto en un hueso | Está **connected**: su posición la fija el padre; desconéctalo o usa otro hueso |
| Controles (IK handles, poles) aparecen como huesos en Unity | `use_deform` mal marcado: fíjalo; export **Only Deform Bones**; en Unity **Strip Bones + Optimize Game Object** |
| Huesos `_end` basura por todo el esqueleto en Unity | **Add Leaf Bones ON** (default): exporta con `add_leaf_bones=False` |
| El brazo "salta" al cambiar de IK a FK | Falta snap: iguala la pose antes de switchear (Rigify trae el operador; a mano, script de snap) |
| Deformación con volumen raro en Unity que en Blender se ve bien | **Preserve Volume** (dual-quat) activo en el Armature modifier: desactívalo — engines no lo soportan |
| Brazos/piernas estiradas se rompen o rotan mal en el FBX | El **stretch** no lo maneja FBX: pon IK Stretch/Auto-Stretch a 0, o Soft-Link/No Parents (ARP) |
| El rig se deforma al aplicar transforms antes de exportar | Nunca Apply Rotation/Scale en el armature animado ni `bake_space_transform`; aplica solo en rest |
| Vértices tironeados por un 5º hueso en Unity | Weights sin limitar: `vertex_group_limit_total(limit=4)` y normaliza [ver: skinning-weights] |
| Los controles son imposibles de seleccionar/agarrar | Sin custom shapes: asigna widgets; oculta la collection `WGT-` |
| `bpy.ops.pose.constraint_add` falla en headless | Problema de contexto de operador: usa la data API `pose_bone.constraints.new(type=...)` |

## Fuentes

- **Blender 5.2 LTS Manual — Inverse Kinematics Constraint** (`animation/constraints/tracking/ik_solver.html`) — Blender Foundation — Target/Pole Target/Iterations/Chain Length/Use Tail/Stretch/Weight, `Shift`-`I`, IK corre tras todos los constraints, Standard vs iTaSC.
- **Blender 5.2 Manual — Constraints: Introduction, Copy Rotation, Copy Location, Damped Track, Limit Rotation, Child Of** (`animation/constraints/...`) — opciones exactas de cada constraint, stack + Influence, visual transform / Apply Visual Transform, notas (Limit Rotation no bajo IK, Copy Location no en connected, Damped swing-only).
- **Blender 5.2 Manual — Armatures ‣ Posing ‣ Inverse Kinematics (introduction)** — FK vs IK, Auto IK en Pose Mode, panel Armature IK Solver (Standard/iTaSC).
- **Blender 5.2 Manual — Bones ‣ Properties ‣ Viewport Display (Custom Shape)** — Custom Object, Scale to Bone Length, Override Transform, reglas (origen en la raíz, Y a lo largo del hueso, no se renderizan).
- **Blender 5.2 Python API** — `bpy.ops.pose.ik_add(with_targets=True)`, `bpy.ops.pose.constraint_add(type=…)`, `bpy.ops.nla.bake(...)` (firma: visual_keying/clear_constraints/only_selected/bake_types), `bpy.ops.object.vertex_group_limit_total(limit=4)`, `bpy.ops.object.parent_set(type='ARMATURE_AUTO')`, `bpy.types.KinematicConstraint` (`pole_angle` rango ±π default 0, `chain_count`, `use_tail`, `use_stretch`, `pole_target`), `bpy.types.PoseBone`/`bpy.types.Bone` (custom shape props, `show_wire`, `use_deform`, `lock_ik_*`/`ik_min_max_*`/`ik_stiffness_*`/`ik_stretch`) — todo instanciado y comprobado en **Blender 5.2.0 LTS real (headless local, jul-2026)**, no solo leído de la doc: valores por defecto reales al crear el constraint son `iterations=500` y `use_tail=True` (la página de la API muestra el default "en bruto" de la clase RNA, 0/False, que no es el valor real que trae el constraint recién creado).
- **Blender 5.2 LTS Manual — Bone Locations ‣ Properties ‣ Viewport Display** (`animation/armatures/bones/properties/display.html`) — texto exacto de Custom Shape: Override Transform/Affect Gizmo/Use As Pivot, Scale to Bone Length, **Wireframe** (bool) + **Wire Width**, origen del widget en la raíz + eje Y a lo largo del hueso, custom shapes nunca se renderizan.
- **Unity 6.5 Manual — FBX Importer Rig tab** (`FBXImporter-Rig.html`) — Animation Type (Generic/Humanoid), Avatar Definition, Root node, **Skin Weights (Standard 4 Bones)**, **Strip Bones**, **Optimize Game Object**, Extra Transforms to Expose.
- **Unity 6.5 Manual — Importing a model with humanoid animations / Configuring the Avatar** — mapeo de huesos al Avatar, ≥15 huesos requeridos, T-Pose (Enforce/Sample Bind-pose/Automap), reuso de Avatar entre FBX de animación.
- **Unity 6.5 Manual — Avatar Muscle & Settings tab** — Muscle Group/Per-Muscle, rangos, Translate DoF y su coste.
- **Auto-Rig Pro Documentation — Game Engine Export** (`lucky3d.fr/auto-rig-pro/doc/ge_export_doc.html`) — exporter Humanoid/Universal, bake control→deform, custom bones `cc_`/re-parent a deform, desactivar Preserve Volume, stretch (Soft-Link/No Parents), Unit Scale 1. Precio: NO VERIFICADO (store 403).
- **Bases sintetizadas de este repo:** [ver: blender/import-export] (FBX: constraints solo horneados, Add Leaf Bones/Only Deform Bones, `@anim`, apply transforms, `bake_space_transform` rompe armatures), [ver: blender/interfaz-flujo] (Pose Mode, Rigify bundled, F3), [ver: unity/animacion-unity] (Humanoid vs Generic cost, IK Pass, Animation Rigging, avatar mask). Cruces internos: [ver: esqueletos-armature], [ver: skinning-weights], [ver: deformacion], [ver: rigify], [ver: rigs-mecanicos], [ver: rig-a-unity].
