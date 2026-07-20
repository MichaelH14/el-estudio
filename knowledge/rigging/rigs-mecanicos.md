# Rigs mecánicos: props, armas, vehículos

> **Cuando cargar este archivo:** al riggear un asset SIN deformación de piel — un prop interactivo (puerta, cofre, palanca), un arma con partes móviles (corredera, gatillo, cargador, tambor, cerrojo) o un vehículo (ruedas, dirección, puertas, suspensión) — y haya que decidir **bones vs jerarquía de objetos**, colocar pivots en el eje mecánico, y entregar el rig que Unity 6 espera. Es el nudo entre [ver: pipeline-3d/receta-arma], [ver: pipeline-3d/receta-vehiculo], [ver: pipeline-3d/receta-prop] (que ya modelan el asset despiezado con pivots) y el handoff de [ver: blender/import-export] + [ver: unity/animacion-unity]. No repite el skinning de personajes ([ver: skinning-weights], [ver: deformacion]) ni la teoría de armature ([ver: esqueletos-armature]); toma de ahí lo que aplica al caso rígido.

Versión: **Blender 5.2 LTS** + **Unity 6** (Mecanim/Generic·Humanoid) + **Auto-Rig Pro 2026**. Operando por MCP/headless, cargar antes [ver: rigging-en-blender-operativo] y [ver: blender/blender-mcp-operativo].

> ⚠️ **Verificación honesta (2026-07-20, auditoría posterior):** `docs.blender.org` sigue sin ser accesible por fetch directo; se verificó contra el código fuente real de Blender en GitHub (rama `main`, `raw.githubusercontent.com`), que sí respondió. Confirmado hoy con el `.cc` completo (ya no truncado): el enum de `object.parent_set` (`object_relations.cc`), `object.vertex_group_normalize_all` y **`object.vertex_group_limit_total`** con su prop `limit` (default 4, rango 1-32) en `object_vgroup.cc`, y `object.empty_add(type=...)` con el enum `PLAIN_AXES` en `object_add.cc`/`rna_object.cc`. En Unity 6 (`docs.unity3d.com`, leído hoy) se confirmaron los defaults de `WheelCollider`, la obligatoriedad del Root node en Generic (`GenericAnimations.html`: "you must tell it which bone is the Root node"; default `None`, hay que elegirlo) y el **Skin Weights** del Rig tab (`Standard` = 4 huesos por default, `Custom` hasta 32; `ModelImporter.maxBonesPerVertex` acepta 1-255; `QualitySettings.skinWeights` tiene `Unlimited`) — el archivo ya corrigió el punto donde presentaba el límite de 4 como techo absoluto del engine. `armature.edit_bones.new`, `driver_add`, `nla.bake` y `constraints.new` siguen sin re-verificación en vivo hoy (API estable de largo recorrido, alta confianza); confirmar en el Blender de trabajo antes de automatizar en producción.

---

## 0. La decisión maestra: ¿armature o jerarquía de objetos?

Un rig mecánico no deforma piel: cada parte es un sólido rígido que **rota o traslada** sobre un eje. Hay dos maneras de entregarlo a Unity, y **las dos exportan bien por FBX**:

| Vía | Qué es | Qué llega a Unity |
|---|---|---|
| **Jerarquía de objetos** | Cada parte = objeto separado, su origen en el eje, parenteados a un root | Un **GameObject por parte**, cada pivot = su transform local. Sin skinning |
| **Armature (bone por parte)** | Una malla + un hueso por parte, skinning **rígido** (peso 1.0 a un solo hueso) | **Un `SkinnedMeshRenderer`** + jerarquía de huesos; se anima con clips Mecanim (Generic/Humanoid) |

**Regla de decisión (la que gobierna todo el archivo):**

- **Empieza por jerarquía de objetos.** Es lo que [ver: pipeline-3d/receta-arma] y [ver: pipeline-3d/receta-vehiculo] ya producen (parte separada + `Origin to 3D Cursor` en el eje). Para la mayoría de props, armas y vehículos de física es **suficiente y más simple**: menos pasos, cero pesos, pivots exactos, y se anima en Unity por código/tween o con clips sobre transforms.
- **Sube a armature SOLO si** se cumple una de estas (si no, el armature es coste sin retorno):

| Necesitas… | Por qué armature |
|---|---|
| **Una sola malla / un solo draw call** para muchas partes | Bones colapsan N renderers en un `SkinnedMeshRenderer` (un material, un batch) |
| **Deformación real** de una pieza continua (correa/sling del arma, cable, antena, oruga de tanque, manguera) | Un objeto rígido no se dobla; eso es piel → huesos + pesos [ver: skinning-weights] |
| **Retarget / blend trees / Avatar** (Generic o Humanoid) | Mecanim opera sobre esqueletos, no sobre jerarquías de objetos sueltos [ver: unity/animacion-unity §1] |
| **Optimize Game Objects** (transforms dentro del Avatar, coste 0 de jerarquía) | Solo aplica a rigs con Avatar (§9) |
| Cadena cinemática con **IK** (brazo robótico, grúa, pata mecánica) | IK/constraints viven en el armature [ver: ik-fk-constraints] |

**No es armadura de personaje.** Rigify es para bípedos/criaturas y no aporta nada a un rig mecánico rígido [ver: rigify]; aquí se arma a mano un esqueleto plano de huesos-pivote, o se usa Auto-Rig Pro en modo Universal solo si el asset lo justifica (§10).

---

## 1. Vía A — jerarquía de objetos (el default mecánico)

Es la continuación directa de las recetas de modelado; aquí solo el contrato de rig y export. El QUÉ (despiece, pivot en el eje real) ya está hecho en [ver: pipeline-3d/receta-arma §4] y [ver: pipeline-3d/receta-vehiculo §5]:

1. **Cada parte móvil = objeto separado**, con su **origen en el eje mecánico** (`Shift-S ▸ Cursor to Selected` sobre el eje → `Object ▸ Set Origin ▸ Origin to 3D Cursor`, `bpy.ops.object.origin_set(type='ORIGIN_CURSOR')` — enum confirmado en las bases).
2. **Aplica transforms** en la malla ANTES de fijar el origen (`Ctrl-A ▸ Rotation & Scale`); ninguna hija exporta con rotación/escala cocida [ver: blender/import-export].
3. **Root limpio** (Empty o el cuerpo fijo) en el origen del mundo; parentea las partes con `Ctrl-P ▸ Object (Keep Transform)` → `bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)` (enum `'OBJECT'` + `keep_transform` verificados hoy en GitHub).
4. **Naming = contrato** (`wheel_FL`, `Rifle_Slide`, `door_L`): no se renombra tras el primer import [ver: blender/import-export].
5. **Export FBX** con `object_types={'EMPTY','MESH','ARMATURE'}` — sin armature aquí, pero EMPTY debe ir (sockets, §8).

En Unity cada parte es un GameObject con su pivot; se anima por código, tween o clips sobre transforms (§7). **Contras:** cada parte es un renderer (más draw calls si no se combinan), y no hay Avatar. **Pros:** lo más simple y robusto, pivots exactos, cero skinning.

---

## 2. Vía B — armature de partes rígidas (bone por parte, skinning rígido)

Una malla, un hueso por parte, **peso 1.0 de cada isla a un solo hueso** (rigid bind: sin blending entre huesos — es lo contrario al skinning orgánico de [ver: skinning-weights]).

### 2.1 Crear el esqueleto (headless-safe, data API)

Colocar cada hueso con la **cabeza (head) EN el pivot** de la parte (perno, eje, bisagra) y la **cola (tail)** apuntando en la dirección "forward" de la parte, para que los ejes locales del hueso sean legibles en Unity. El **roll** del hueso define los ejes X/Z locales: recalcular (`Armature ▸ Bone Roll ▸ Recalculate`, `bpy.ops.armature.calculate_roll`) o fijarlo a mano para que el eje de giro coincida con un eje limpio [ver: esqueletos-armature].

```python
import bpy
from mathutils import Vector

arm = bpy.data.armatures.new("RIG_Rifle")
rig = bpy.data.objects.new("RIG_Rifle", arm)
bpy.context.scene.collection.objects.link(rig)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode='EDIT')

def bone(name, head, tail, parent=None):
    eb = arm.edit_bones.new(name)
    eb.head, eb.tail = Vector(head), Vector(tail)
    eb.use_deform = True                          # hueso que deforma (skinning)
    if parent: eb.parent = arm.edit_bones[parent]
    return eb

bone("root",    (0, 0.00, 0),    (0, 0.10, 0))                       # hueso raíz del arma
bone("slide",   (0, 0.00, 0.05), (0, 0.08, 0.05), parent="root")     # tail sobre el eje +Y (deslizamiento)
bone("trigger", (0,-0.02, 0.00), (0,-0.02,-0.03), parent="root")     # head EN el perno del gatillo
bone("mag",     (0, 0.02,-0.02), (0, 0.02,-0.10), parent="root")     # head donde lo agarra la mano
bpy.ops.object.mode_set(mode='OBJECT')
```

### 2.2 Bind rígido: cada parte a su hueso, peso 1.0

Parentear con **grupos vacíos** (crea un vertex group por hueso + el modificador Armature) y asignar a mano — NO usar auto-weights: los pesos automáticos **mezclan** en las costuras, y en un borde duro mecánico eso hace que una parte "arrastre" a la vecina.

```python
import bpy
mesh = bpy.data.objects["Rifle_MESH"]   # malla única con todas las partes
rig  = bpy.data.objects["RIG_Rifle"]

bpy.ops.object.select_all(action='DESELECT')
mesh.select_set(True); rig.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.parent_set(type='ARMATURE_NAME')   # 'ARMATURE_NAME' = "With Empty Groups" (enum verificado hoy)

def bind_rigid(vert_indices, bone_name):
    vg = mesh.vertex_groups.get(bone_name) or mesh.vertex_groups.new(name=bone_name)
    vg.add(vert_indices, 1.0, 'REPLACE')          # peso 1.0, sin blending
# bind_rigid([<índices de la corredera>], "slide")   # una llamada por parte

# Default de Unity (Rig tab ▸ Skin Weights = "Standard (4 Bones)"): máximo 4 influencias/vértice, normalizado
bpy.ops.object.vertex_group_limit_total(limit=4)      # prop "limit": default 4, rango 1-32 (confirmado en código fuente)
bpy.ops.object.vertex_group_normalize_all(lock_active=False)   # operador confirmado en GitHub
```

- Enum de `parent_set` (verificado contra `object_relations.cc`): `'OBJECT'`, `'BONE'`, `'BONE_RELATIVE'`, `'ARMATURE'` (deform), `'ARMATURE_NAME'` (empty groups), `'ARMATURE_ENVELOPE'`, `'ARMATURE_AUTO'` (automatic weights). Para rig rígido: **`ARMATURE_NAME`** + asignación manual, nunca `ARMATURE_AUTO`.
- `vertex_group_limit_total(limit=...)` — confirmado contra `object_vgroup.cc` (`RNA_def_int(ot->srna, "limit", 4, 1, 32, ...)`): la prop se llama **`limit`**, default **4**, rango 1-32. Con bind 1.0-a-un-hueso el límite se cumple solo; se incluye como higiene para rigs mixtos.
- **4 NO es un techo absoluto del engine, es el *default*:** el Rig tab del Model Importer tiene **Skin Weights** = `Standard (4 Bones)` (recomendado por rendimiento) o `Custom` con **Max Bones/Vertex** de 1 a 32; a nivel script, `ModelImporter.maxBonesPerVertex` acepta 1-255, y `QualitySettings.skinWeights` tiene una opción `Unlimited`. Para rig mecánico rígido (1 hueso por vértice) esto es irrelevante — se cumple solo — pero no describas el 4 como un límite que "Unity ignora en silencio" sin más: es el estándar del proyecto, no una ley física del formato (fuente: Unity 6 Manual, `FBXImporter-Rig.html` §Skin Weights, y `ScriptReference/SkinWeights`, leídas hoy).
- Verificar que ninguna isla quedó a peso 0 o a dos huesos: en Weight Paint, aislar cada vertex group; una parte gris/parcial = costura mal asignada [ver: skinning-weights].

### 2.3 Verificar la mecánica en pose antes de exportar

Entrar en Pose Mode y mover cada hueso por su recorrido: `slide` traslada en +Y, `trigger` rota en su perno, `mag` sale del pozo. Si una parte "cojea" o arrastra geometría vecina, el pivot del hueso o el peso está mal. Es el equivalente en armature al QA de recorridos de [ver: pipeline-3d/receta-arma §11].

---

## 3. Tabla de decisión bones vs objetos (por caso real)

| Asset / parte | Movimiento | Vía recomendada | Nota |
|---|---|---|---|
| Puerta de cofre, tapa, portón | Rotación en bisagra | **Objeto** (origen en la bisagra) | Interacción → se anima en Unity (§7) [ver: pipeline-3d/receta-prop] |
| Palanca / interruptor | Rotación en el fulcro | **Objeto** | Ídem |
| Corredera / cerrojo / gatillo / cargador / tambor | Traslación o rotación corta | **Objeto** (default) u **armature** si quieres clips Generic retargetables entre armas | [ver: pipeline-3d/receta-arma §4] |
| Rueda de vehículo | Rodadura + dirección + suspensión | **Objeto** (la mueve Unity, §6) | Rara vez armature |
| Correa/sling del arma, cable, manguera | Se **dobla** | **Armature** (cadena de huesos + pesos) | Es piel, no rígido [ver: deformacion] |
| Oruga de tanque | Deforma sobre ruedas + scroll | **Armature** para la geo visible + UV scroll en Unity | Mixto (§6) |
| Brazo robótico / grúa / pata mecánica | Cadena articulada, a veces IK | **Armature** (huesos en cada pasador, IK opcional) | [ver: ik-fk-constraints] |
| Antena / whip / pelo de mascota del vehículo | Movimiento secundario | **Armature** + Damped Track / physics bones | Blender para clip, o física en Unity |

Regla corta: **rota/traslada rígido → objeto; se dobla o quieres Mecanim/Avatar/IK → armature.**

---

## 4. Props interactivos (puentea receta-prop)

- **Puerta / tapa / cofre:** pivote (origen del objeto, o cabeza del hueso) **exactamente en el eje de la bisagra** — dos vértices del canto de la bisagra → `Cursor to Selected` → `Origin to 3D Cursor`. El hueco que destapa la puerta debe existir modelado (marco, canto interior); si al abrir aparece un agujero, la ilusión se rompe [ver: pipeline-3d/receta-prop] [ver: modelado/props-armas].
- **Palanca / válvula:** pivote en el fulcro/eje de giro real, no en el centro del objeto.
- **Casi siempre jerarquía de objetos:** una rotación simple por interacción del jugador se resuelve mejor con un tween/código en Unity que con un clip (§7) [ver: unity/animacion-unity §4].
- El **socket** donde el jugador "agarra" (pomo, manija) puede ser un Empty hijo para VFX/anclajes (§8).

---

## 5. Armas (puentea receta-arma)

[ver: pipeline-3d/receta-arma] ya entrega el arma **despiezada con pivots + sockets** por jerarquía de objetos — para la mayoría de casos eso es el rig completo. Este archivo añade **cuándo el arma necesita un armature**:

| Situación | Rig |
|---|---|
| Arma con recarga/disparo como **clips de artista** reutilizables entre armas de la familia | **Armature** Generic: un hueso por parte (`slide`, `trigger`, `mag`, `hammer`, `cylinder`, `bolt`, `charging_handle`), clips en los huesos → Unity los importa como AnimationClips [ver: blender/import-export §@] |
| Arma con **correa/sling** que se dobla | **Armature** (cadena de huesos en la correa + pesos) — es lo único del arma que es piel |
| Arma FP simple, animada en código o con clips por transform | **Objeto** (default de la receta) |

- **Bones = las mismas partes móviles** que la receta ya separó (corredera, gatillo, cargador, tambor, cerrojo, manija de carga): cada hueso con la cabeza en el eje mecánico (§2.1). La **jerarquía** (`root ▸ slide/trigger/mag…`) es la que anima recarga y disparo.
- **Blowback de la corredera** al disparar: o dentro del clip de disparo, o por código en Unity ligado al evento de fire [ver: unity/animacion-unity §9] (Animation Event).
- **Apuntado (ADS) y agarre:** la mano del personaje al arma es IK del **rig del personaje** en Unity (Two Bone IK / Multi-Aim de Animation Rigging), no del arma [ver: unity/animacion-unity §8]. El arma solo aporta el **socket de agarre** y la mira alineada [ver: pipeline-3d/receta-arma §6].
- **Sockets del arma** (mira, óptica, boca, cargador, expulsión, muzzle flash): Empties o huesos (§8).

---

## 6. Vehículos (puentea receta-vehiculo)

[ver: pipeline-3d/receta-vehiculo] entrega el vehículo por jerarquía de objetos (`car_root ▸ body + wheel_FL.. + door_L/R`), cada rueda separada con **pivot en el eje (X)**. El punto clave del rig de vehículo es **qué NO se anima en Blender:**

| Parte | Quién la mueve | Detalle (fuente Unity 6, leída hoy) |
|---|---|---|
| **Rueda: rodadura + dirección + suspensión** | **Unity `WheelCollider`** (física), NO Blender | El `WheelCollider` es un collider separado; la **malla visual** de la rueda se sincroniza en código con `WheelCollider.GetWorldPose(out Vector3 pos, out Quaternion quat)` — "gets the world space pose of the wheel accounting for ground contact, suspension limits, steer angle, and rotation angle" |
| **Suspensión** | `WheelCollider` (Suspension Distance 0.3 m def, spring 35000 N/m, damper 4500, Target Position 0.5) | El modelador solo garantiza **wheel well con holgura** en +Z; no se modela ni anima el resorte salvo que se vea [ver: pipeline-3d/receta-vehiculo §5.5] |
| **Puerta** | Clip de Blender **o** tween/código en Unity | Animación fija de artista → clip; interacción → código (§7) |
| **Torreta apuntando** | Unity (código / Animation Rigging) | Apunta a un target runtime, no un clip fijo |
| **Oruga de tanque** | Unity: **UV scroll / shader** para el rodaje + geo por bones si la oruga se dobla visiblemente | El "movimiento" del tread es textura, no huesos |

Patrón de código Unity para la rueda visual (de la doc de `GetWorldPose`, hoy):

```csharp
wheelCollider.GetWorldPose(out Vector3 pos, out Quaternion rot);
wheelVisual.SetPositionAndRotation(pos, rot);   // rodadura + steer + suspensión, todo del collider
```

- **El modelador NUNCA anima la rodadura de la rueda en Blender.** Depende de la velocidad en runtime; cualquier driver/clip de giro sería basura para un coche de física (§7).
- **Coche arcade / kinematic** (sin `WheelCollider`): la rodadura sí se hace por código (`wheelVisual.Rotate(speed * Time.deltaTime / radius, 0, 0)`), no por driver exportado. Igual: **nada de rodadura en Blender.**
- **Dirección visual:** si no usas `GetWorldPose`, el nudillo de dirección puede ser un pivote/objeto padre de la rueda que rota en Z por código; pero con `WheelCollider` el `GetWorldPose` ya incluye el steer.
- **Armature en vehículo:** raro. Solo si quieres una malla única / clips Generic (p.ej. un transformer, un mech con muchas articulaciones) — entonces hueso en el eje de cada rueda/puerta como §2.

---

## 7. Qué se anima en Blender y qué en Unity

La regla que decide dónde vive cada movimiento:

| Movimiento | Dónde | Por qué |
|---|---|---|
| Rueda rodando (roll) | **Unity** (`WheelCollider.GetWorldPose` o código) | Depende de la velocidad runtime; un driver de Blender **no se exporta** |
| Dirección / suspensión de rueda | **Unity** (`WheelCollider`) | Física e input en runtime |
| Torreta / cañón apuntando a un objetivo | **Unity** (código / Animation Rigging Multi-Aim) | Target dinámico [ver: unity/animacion-unity §8] |
| Puerta de prop, cofre, palanca (interacción) | **Unity** (tween/código, ángulo fijo) | Feedback simple → tween, no clip [ver: unity/animacion-unity §4] |
| Recarga / disparo de arma (coreografía) | **Blender** → clip exportado | Movimiento autorado por artista sobre huesos/objetos |
| Puerta de coche abriendo como animación fija | **Blender** clip **o** Unity | Si es una animación de artista repetible → clip; si es interacción → código |
| Oruga / cinta transportadora (scroll) | **Unity** (UV/shader) | Runtime, sin fin |
| Pieza que se dobla (correa, cable, antena) | **Blender** (clip por huesos) o física en Unity | Deformación real |

**Principio:** todo lo que dependa de **velocidad/input/target en runtime** se hace en Unity; solo la **coreografía fija de artista** (recarga, disparo, una apertura scriptada) se anima en Blender y se exporta como clip [ver: blender/import-export §@] [ver: unity/animacion-unity].

---

## 8. Drivers y constraints: automatizan en Blender, NO se exportan

Los **drivers** (relación property↔property: `roll = avance / (2π·r)`, pistón que sigue a la biela, manija que gira con la palanca) y los **constraints** (Copy Rotation, Damped Track, Limit Rotation, Child Of, Transformation) son oro para **autorar y verificar** la mecánica en Blender — y **cero** en el engine:

- **FBX/glTF no tienen concepto de driver ni de constraint.** [ver: blender/import-export] lo confirma: "Constraints: solo el resultado **bakeado** como keyframes". Un driver que no se hornea, se pierde en silencio.
- Tres destinos posibles para una mecánica hecha con drivers/constraints:
  1. **Previz / verificación** en Blender y ya (no se exporta) — p.ej. comprobar que el pistón no clipa.
  2. **Hornear a keyframes** si quieres el movimiento como **clip exportable** (coreografía fija): `bpy.ops.nla.bake(...)` con `visual_keying=True` para capturar el resultado del constraint/driver, y `clear_constraints=True` para dejar solo las keys.
  3. **Reproducir la relación en Unity por código** — obligatorio para todo lo que dependa de runtime (rodadura de rueda, apuntado, scroll).

```python
import bpy
wheel = bpy.data.objects["wheel_FL"]
RADIUS = 0.33
# DRIVER conceptual (útil solo dentro de Blender; NO viaja al FBX):
fc = wheel.driver_add("rotation_euler", 0)        # índice 0 = eje X local
d = fc.driver; d.type = 'SCRIPTED'
v = d.variables.new(); v.name = "y"
v.targets[0].id = bpy.data.objects["car_root"]
v.targets[0].data_path = "location.y"
d.expression = f"y / {RADIUS}"                     # radianes = avance / radio

# Si fuera coreografía fija y quisieras exportarla como CLIP, hornear:
# bpy.ops.nla.bake(frame_start=1, frame_end=120, only_selected=True,
#                  visual_keying=True, clear_constraints=True, bake_types={'OBJECT'})
# Para un coche de JUEGO: no exportar nada de esto — la rodadura va en Unity (§6, §7).
```

- **Bones mecánicos con constraints** (una biela con Damped Track a la manivela, un limitador con Limit Rotation): mismo trato — se hornean con `bake_types={'POSE'}` si van como clip, o se recrean en Unity. Los constraints de Blender **no** se convierten en constraints de Unity [ver: ik-fk-constraints].
- **La rodadura de rueda por driver es la trampa clásica:** se ve perfecta en Blender y llega vacía a Unity. Nunca se exporta; siempre código en Unity (§6).

---

## 9. Attachment sockets: Empty vs bone

Puntos de anclaje (mira, óptica, boca del cañón, cargador, expulsión de casquillo, muzzle flash; puntos de enganche de accesorios de vehículo):

| Opción | Cómo | Cuándo |
|---|---|---|
| **Empty (Plain Axes)** hijo del root | `bpy.ops.object.empty_add(type='PLAIN_AXES')` → parent al root | Rig por **objetos** (default). Llega a Unity como **GameObject vacío** con su transform [ver: blender/import-export] |
| **Bone** en el armature | Un hueso extra (no-deform o deform) en la posición/orientación del socket | Rig por **armature**: el socket viaja dentro del esqueleto, accesible por nombre |

- **Orientación importa:** rotar el Empty/hueso para que un eje conocido apunte en la dirección de montaje (p.ej. +Y hacia la boca en `SOCKET_Muzzle`); Unity hereda esa rotación [ver: pipeline-3d/receta-arma §8].
- **Prefijo consistente** (`SOCKET_`, `cc_`), convención de equipo — Unity no lo exige.
- **Export:** los Empties exigen `object_types` incluyendo `'EMPTY'` en el FBX, o no llegan [ver: blender/import-export].
- ⚠️ **Con Optimize Game Objects** (§10) la jerarquía de transforms se colapsa en el Avatar y **los sockets-hueso desaparecen como GameObjects**: hay que añadir cada uno a **"Extra Transforms to Expose"** en el Rig tab para poder anclar accesorios en Unity (fuente Unity 6, leída hoy).

---

## 10. Handoff a Unity: rig type, Avatar, Optimize (fuentes Unity 6, hoy)

En el **Rig tab** del Model Importer (`FBXImporter-Rig`), **Animation Type** define cómo Unity trata el asset:

| Rig entregado | Animation Type | Ajuste |
|---|---|---|
| Jerarquía de objetos, animado en Unity por código/tween | **None** | Sin Avatar; cada parte es un GameObject |
| Jerarquía de objetos con clips por transform | **Generic** | Avatar Definition "Create From This Model" |
| Armature mecánico (arma/vehículo/mech) | **Generic** | Elegir **Root node** = el hueso raíz del rig (obligatorio en Generic) |
| Bípedo mecanoide con proporciones humanas | **Humanoid** | Solo si quieres retarget humanoide; para mecánico casi nunca |

Detalles verificados hoy:

- **Generic** es "everything else" (no humanoide) y **exige designar un Root node** — "a transform in an animation hierarchy that allows Unity to establish consistency between Animation clips". Es el nodo que ancla el sistema de animación y el root motion. Auto-Rig Pro, para Generic, transfiere la animación de su controlador `c_traj` **al objeto armature** porque "the armature (rig) object itself must be animated, since this is the root node of the FBX file" (doc ARP, hoy).
- **Avatar Definition:** "Create From This Model" (genera el Avatar) vs "Copy from Other Avatar" (comparte esqueleto entre variantes — misma jerarquía y nombres de hueso obligatorios).
- **Optimize Game Objects:** casilla que "removes the GameObject Transform hierarchy... and stores it in the Avatar and Animator instead", mejora el rendimiento. Solo aparece con Avatar Definition = "Create From This Model". **Efecto:** los transforms de partes/sockets dejan de existir como GameObjects → para conservar uno (socket del arma, hueso de rueda que otro sistema toca), añadirlo a **"Extra Transforms to Expose"**.
- **SkinnedMeshRenderer siempre anima** aunque esté fuera de cámara salvo que apagues *Update When Offscreen*; en rigs mecánicos con armature aplica el mismo culling de [ver: unity/animacion-unity §1].
- Escala, ejes, `-89.98`, naming, colliders `UCX_`, LODs `_LODn` — todo el runbook de export/validación está en [ver: blender/import-export]; no se repite. La aprobación es **en Unity** con la cámara y física reales, no en el viewport [ver: pipeline/arte-a-unity].

---

## 11. Auto-Rig Pro 2026 para rigs mecánicos

ARP es **character-first** (bípedos/criaturas), pero su pipeline de export a game engine sirve a assets mecánicos que además tengan parte de criatura, o cuando quieres su exporter (doc ARP, leída hoy):

- **Export Types:** **Humanoid** (esqueleto humano, retargetable) y **Universal** ("any creature type — bipeds, quadrupeds, spiders, or centaurs"; más flexible, sin retarget). Para un mech/vehículo articulado → **Universal**.
- **Custom / mechanical bones:** huesos que no son de deformación estándar (props, mecánica) se **taggean** con prefijo **`cc_`** (ej. `cc_sword`) o una custom property `cc`/`custom_bone`, si no, no se exportan. El exporter re-parentea huesos custom colgados de controles FK a huesos de deform.
- **Generic/root motion:** transfiere la animación de `c_traj` al objeto armature (el root node del FBX, §10). Opciones: **Selected Bones Only**, **Selected Objects Only**, **Units x100** (escala a Unity), **Root Motion**.
- **Cuándo NO usar ARP:** para un prop/arma/vehículo puramente rígido, un armature a mano (§2) o directamente jerarquía de objetos (§1) es más simple y sin dependencia de add-on de pago.
- **Precio:** ARP es un add-on **de pago** (Blender Market / Superhive). **Precio actual NO VERIFICADO esta sesión** (WebSearch agotado, tienda no consultada) — comprobar en la tienda antes de citar cifra; no inventar el número.

---

## Reglas prácticas

1. **Default = jerarquía de objetos.** Sube a armature solo por una razón concreta (una malla/draw call, deformación real, Mecanim/Avatar, IK, Optimize) — si no, es coste sin retorno (§0).
2. Cada parte móvil = objeto o hueso con su **pivot/cabeza EN el eje mecánico real** (bisagra, perno, eje de rueda), nunca en el centro del objeto.
3. `Ctrl-A ▸ Rotation & Scale` en la malla **antes** de fijar origen; ninguna hija exporta con transform cocida [ver: blender/import-export].
4. Skinning mecánico = **rígido**: peso 1.0 de cada isla a **un solo hueso**; `parent_set(type='ARMATURE_NAME')` + asignación manual, **nunca `ARMATURE_AUTO`** (mezcla en las costuras).
5. Tras bind: `vertex_group_limit_total(limit=4)` + `vertex_group_normalize_all` (Unity Rig tab, Skin Weights = `Standard`: 4 influencias por default, `Custom` permite hasta 32).
6. Bone roll fijado para que el eje de giro/deslizamiento caiga en un eje limpio; verificar la mecánica en **Pose Mode** antes de exportar.
7. **Rodadura de rueda: SIEMPRE en Unity** (`WheelCollider.GetWorldPose` en física, o código en arcade). Nunca un driver/clip exportado.
8. Suspensión y dirección de rueda las hace `WheelCollider`; el modelador solo garantiza **wheel well con holgura** (§6).
9. **Drivers y constraints NO se exportan**: úsalos para autorar/verificar; si el movimiento es coreografía fija, **hornéalo** (`nla.bake`, `visual_keying=True`); si depende de runtime, **recréalo en Unity por código**.
10. Coreografía de artista (recarga, disparo, apertura scriptada) → clip en Blender; movimiento reactivo a input/velocidad/target → Unity (§7).
11. Sockets = Empties (rig por objetos) o huesos (rig por armature), orientados a la dirección de montaje; `'EMPTY'` en `object_types` del FBX o no llegan.
12. Con **Optimize Game Objects**, añade cada socket/transform que otro sistema toca a **"Extra Transforms to Expose"** o desaparece.
13. Armature mecánico → **Animation Type = Generic** en Unity y **elegir Root node** = hueso raíz (obligatorio); Humanoid solo para mecanoides humanoides.
14. **Naming = contrato** (`wheel_FL`, `Rifle_Slide`, `door_L`, `SOCKET_Muzzle`): se congela tras el primer import [ver: blender/import-export].
15. La mano del personaje al arma/volante es IK del **rig del personaje** en Unity (Animation Rigging), no parte del rig del arma/vehículo [ver: unity/animacion-unity §8].
16. Pieza que **se dobla** (correa, cable, oruga, antena) = armature con pesos (es piel), no un objeto rígido [ver: deformacion].
17. Aprobar SIEMPRE en Unity con física/cámara reales; el veredicto no es el viewport de Blender [ver: pipeline/arte-a-unity].

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Armar un armature "porque es un rig" cuando la jerarquía de objetos bastaba | Empezar por objetos; armature solo por una razón de §0 (draw call, deformación, Mecanim, IK, Optimize) |
| Auto-weights (`ARMATURE_AUTO`) en partes mecánicas → una parte arrastra a la vecina en la costura | Bind **rígido**: `ARMATURE_NAME` + peso 1.0 a un solo hueso por isla (§2.2) |
| Pivot/cabeza del hueso en el centro del objeto → la parte "cojea" al rotar | Cabeza EN el eje mecánico (Cursor to Selected sobre el perno/eje → origen/cabeza ahí) |
| Animar la **rodadura de la rueda con un driver** en Blender | Se ve bien en Blender y llega **vacía** a Unity; hacerla en Unity (`GetWorldPose`/código) (§6, §8) |
| Esperar que un **constraint/driver** llegue a Unity | No se exportan: hornear a keyframes (`nla.bake`, `visual_keying`) o recrear en código (§8) |
| Exportar la mecánica de suspensión modelada a mano | `WheelCollider` la simula; solo garantizar wheel well con holgura [ver: pipeline-3d/receta-vehiculo §5.5] |
| Vehículo/arma exportado como **una sola malla soldada** | Despiezar en objetos o skinnear con un hueso por parte; sin partes independientes no hay rig |
| Generic sin **Root node** asignado → animación inconsistente en Unity | Elegir el hueso raíz en el Rig tab; ARP lo resuelve pasando `c_traj` al armature (§10) |
| Sockets perdidos con **Optimize Game Objects** activo | Añadirlos a "Extra Transforms to Expose" (§9, §10) |
| Sockets olvidados en el export (sin `'EMPTY'` en Object Types) | Incluir `'EMPTY'` en `object_types` del FBX [ver: blender/import-export] |
| Más de 4 influencias por vértice con Skin Weights en `Standard` (Unity las recorta al importar) | `vertex_group_limit_total(limit=4)` + normalizar antes de exportar; si el proyecto necesita más, `Custom` (hasta 32) en el Rig tab — no asumir que 4 es un techo físico del formato |
| Roll de hueso sin fijar → ejes locales torcidos, giro en un eje raro en Unity | Recalcular/fijar roll para que el eje de giro sea limpio [ver: esqueletos-armature] |
| Rig del arma intentando controlar la mano del personaje | La mano es IK del rig del personaje en Unity; el arma solo da socket + mira [ver: unity/animacion-unity §8] |
| Renombrar huesos/partes tras el primer import a Unity | Rompe Avatar/retarget y MeshFilters; el nombre es el contrato, se congela |
| Usar Rigify o un rig de personaje para un asset mecánico rígido | Armar un esqueleto plano de huesos-pivote a mano (§2) o ARP Universal (§11); Rigify no aplica |

## Fuentes

Web verificadas en vivo hoy (2026-07-20):

- **Unity 6 Manual — WheelCollider** (`class-WheelCollider.html`) — Unity Technologies — propiedades (Radius 0.5 m def, Suspension Distance 0.3 m, spring 35000 N/m, damper 4500, Target Position 0.5), modelo spring-damper de suspensión; la malla visual se sincroniza aparte.
- **Unity 6 Scripting API — `WheelCollider.GetWorldPose`** — Unity Technologies — firma `GetWorldPose(out Vector3 pos, out Quaternion quat)`, "world space pose accounting for ground contact, suspension limits, steer angle, and rotation angle"; patrón de sincronización de la rueda visual (la rodadura va en el engine, no en Blender).
- **Unity 6 Manual — Generic animations / Root node** (`GenericAnimations.html`) — Unity Technologies — Generic = no humanoide ("everything else"); obligación de designar un Root node como ancla de consistencia entre clips.
- **Unity 6 Manual — Rig tab del Model Importer** (`FBXImporter-Rig.html`) — Unity Technologies — Animation Type (None/Legacy/Generic/Humanoid), Avatar Definition (Create From This Model / Copy from Other Avatar), **Optimize Game Object** (colapsa la jerarquía de transforms en el Avatar), **Extra Transforms to Expose** y **Skin Weights** (`Standard (4 Bones)` default recomendado por rendimiento vs `Custom` con Max Bones/Vertex 1-32).
- **Unity 6 Scripting API — `ModelImporter.maxBonesPerVertex`** y **`SkinWeights`** — Unity Technologies — rango de script 1-255 y enum `None/OneBone/TwoBones/FourBones/Unlimited`: el límite de 4 influencias es el *default* de rendimiento, no un techo absoluto del formato/engine.
- **Blender `main` — `source/blender/editors/object/object_relations.cc`** (raw.githubusercontent.com) — Blender Foundation — enum real de `object.parent_set` verificado: `'OBJECT'`, `'BONE'`, `'BONE_RELATIVE'`, `'ARMATURE'`, `'ARMATURE_NAME'` (empty groups), `'ARMATURE_ENVELOPE'`, `'ARMATURE_AUTO'` (automatic weights).
- **Blender `main` — `source/blender/editors/object/object_vgroup.cc`** (raw.githubusercontent.com) — Blender Foundation — `object.vertex_group_normalize_all` confirmado (prop `lock_active`); **`object.vertex_group_limit_total`** confirmado con `RNA_def_int(ot->srna, "limit", 4, 1, 32, ...)` — prop **`limit`**, default 4, rango 1-32.
- **Blender `main` — `source/blender/editors/object/object_add.cc` + `makesrna/intern/rna_object.cc`** (raw.githubusercontent.com) — Blender Foundation — `object.empty_add(type=...)` confirmado, enum `rna_enum_object_empty_drawtype_items` incluye `'PLAIN_AXES'` ("Plain Axes").
- **Auto-Rig Pro — Documentation (index + Game Engine Export)** (`lucky3d.fr/auto-rig-pro/doc/`) — Artell — Export Types Humanoid/Universal, custom bones con prefijo `cc_` / property `cc`, transferencia de `c_traj` al armature para Generic root node, Units x100. **Precio actual NO VERIFICADO esta sesión.**

⚠️ **No accesibles esta sesión:** `docs.blender.org` (manual y API) → sigue sin responder a fetch directo; `blender.stackexchange.com` → bloqueado. Los operadores `bpy` de los snippets no re-verificados hoy en vivo (`armature.edit_bones.new`, `driver_add`, `nla.bake`, `constraints.new`) son API estable de alta confianza — **confirmar en el Blender de trabajo antes de automatizar en producción**.

Bases sintetizadas (el QUÉ/CÓMO que este archivo no repite):

- [ver: pipeline-3d/receta-arma] — despiece del arma con pivots en el eje mecánico, sockets, QA de recorridos, export FBX (base del rig por objetos).
- [ver: pipeline-3d/receta-vehiculo] — vehículo despiezado, pivot de rueda en el eje, wheel well, `WheelCollider`, jerarquía root→body→ruedas/puertas.
- [ver: pipeline-3d/receta-prop] — props interactivos, pivote en la bisagra, hueco que revela el movimiento *(asumida)*.
- [ver: blender/import-export] — FBX a Unity 6 (escala, ejes, `-89.98`), sockets como Empties, "Constraints: solo el resultado bakeado como keyframes", convención `@` para clips, naming/jerarquía.
- [ver: unity/animacion-unity] — Animator/clips, culling del SkinnedMeshRenderer, Animation Rigging (IK de agarre/apuntado), tween vs clip para props, Animation Events.
- Rigging (asumidas, misma base): [ver: esqueletos-armature] (bones, roll), [ver: skinning-weights] (vertex groups, límite 4, weight paint), [ver: deformacion] (armature modifier, bind), [ver: ik-fk-constraints] (constraints, Child Of, IK de cadenas mecánicas), [ver: rigify] (por qué no aplica a mecánico), [ver: rig-a-unity] (Avatar/Generic/Optimize), [ver: rigging-en-blender-operativo] (operadores `bpy` de rigging).
- Modelado/pipeline (asumidas): [ver: modelado/props-armas], [ver: modelado/vehiculos], [ver: blender/modificadores], [ver: blender/blender-mcp-operativo], [ver: pipeline/arte-a-unity].
