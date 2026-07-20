# Exportar clips de animación a Unity

> **Cuando cargar este archivo:** al sacar CLIPS de animación de personaje desde Blender 5.2 hacia Unity 6 — configurar el Bake Animation del export FBX (o glTF), decidir entre un FBX con todo o el patrón `modelo@anim.fbx`, partir un timeline en clips, cuadrar framerate/root motion/loop, o diagnosticar un clip que en Unity va a otra velocidad, patina, no loopea o llega con bones basura.

Este es el **último tramo del pipeline de animación**: la técnica (qué es un buen ciclo, timing, combate, cerrar loops) vive en `animacion3d/`; el COMO se autora en Blender (keyframes, graph, NLA, bake) en el resto de `animacion-blender/`; el export FBX genérico (escala 100×, ejes -89.98, roundtrip de prefab) en [ver: blender/import-export]; el rig + Avatar + root motion conceptual en [ver: rigging/rig-a-unity]; y el consumo del clip ya dentro del motor (Animator, blend trees, loop match, eventos) en [ver: unity/animacion-unity]. Aquí SOLO: convertir Actions de Blender en clips limpios que Unity reconoce, comparte y loopea. No repito lo de esas bases — las cruzo.

---

## 0. Estado del sistema de animación en Blender 5.2 (Baklava / Slotted Actions)

El sistema de Actions **cambió en 4.4** (proyecto *Baklava*) y 5.2 lo hereda. Mucho tutorial pre-4.4 describe el modelo viejo (una Action = un solo data-block). Lo que importa para exportar clips:

| Concepto 5.2 | Qué es | Impacto en el export a Unity |
|---|---|---|
| **Slotted Action** | Una Action ahora tiene **slots**; cada slot anima un data-block distinto (armature, shape keys, material). Una sola Action puede mover el cuerpo Y la cara a la vez | El exportador FBX sigue emitiendo **un take por Action** (`bake_anim_use_all_actions`); el patrón seguro no cambia |
| **Slot** | Identificado por tipo de ID + nombre; al asignar la Action a un objeto, Blender elige el slot compatible | Si reusas UNA Action multi-slot sobre armature+shapekeys, **verifica el take resultante** en Unity |
| **Legacy Action** | Las Actions viejas se abren como Action de un slot; asignación por `animation_data.action` sigue igual | Roundtrip de .blend viejos: transparente |
| **Layers/strips internos** | El data-model soporta capas dentro de la Action; en 5.2 la UI expone esencialmente una capa | No afecta el clip exportado (se hornea el resultado evaluado) |

> ⚠️ **NO VERIFICADO contra docs.blender.org 5.2** (el sitio bloquea el fetch esta sesión). Lo de Slotted Actions viene del conocimiento del sistema Baklava (4.4, mar-2025) y de la base empírica [ver: blender/import-export]. El **patrón operativo seguro sigue siendo: 1 Action = 1 clip = 1 armature**. Detalle del modelo de datos en [ver: sistema-animacion] y [ver: actions-organizacion].

---

## 1. Las dos rutas: FBX vs glTF

| | **FBX** (el clásico) | **glTF (.glb)** |
|---|---|---|
| Avatar/retargeting Humanoid en Unity | Sí — flujo Mecanim nativo | glTFast importa clips como **Generic** (no arma Avatar Humanoid por defecto) |
| Clips → Unity | Cada take/Action = un clip; Humanoid o Generic | Cada *glTF animation* = un `AnimationClip` (glTFast), Generic |
| Exportador Blender 5.2 | `export_scene.fbx` (add-on bundled) | `export_scene.gltf` (Khronos, bundled) |
| Cuándo | **Default para clips de personaje** editor→prefab | Solo si el juego carga animación en **runtime** o el pipeline es glTF-first |

**Regla:** para clips de personaje que consume el Animator, **FBX**. glTF de animación solo para carga runtime. Decisión completa y settings glTF en [ver: blender/import-export]. glTF de animación clave: `export_animations=True`, `export_animation_mode='ACTIONS'` (un clip por Action). *(enum `export_animation_mode` desde conocimiento; verificar contra el exportador si se usa glTF).*

---

## 2. El gran debate: un FBX con todo vs `modelo@anim` separados

| | **FBX único** (malla + todas las anims) | **model@anim** (`hero.fbx` + `hero@walk.fbx` + `hero@run.fbx`…) |
|---|---|---|
| Estructura | Un archivo con N takes (All Actions / NLA) | 1 FBX de malla+rig (sin anim) + 1 FBX **por clip** (solo armature+anim) |
| Cómo comparten Avatar | Todos los clips salen del mismo modelo | El `.fbx` sin `@` define el Avatar; los `@` van en **Copy From Other Avatar** → mismo esqueleto [ver: rigging/rig-a-unity] |
| Reconocimiento en Unity | Un solo import | "Unity automatically imports all files and collects all animations to the file without the @ sign in" — Unity los junta por el nombre antes del `@` |
| **Coste de reimport** | Tocas un clip → reexportas y Unity reimporta **TODO** (malla incluida) + re-slice | Tocas un clip → reexportas **solo ese `@`** → Unity reimporta un archivo pequeño; los demás intactos |
| Malla en los archivos de anim | Va repetida (peso, tiempo) | **Fuera** — los `@` solo llevan armature; activar **Preserve Hierarchy** en el import si excluyes malla |
| Slicing | Manual (Start/End en Unity) o takes | Automático: **1 archivo = 1 clip**, sin cortar nada |
| Riesgo | Un `.blend` lleno de Actions → docena de clips basura por FBX | Muchos archivos; disciplina de naming |

**Veredicto:** para producción con muchos clips, **`model@anim`**. Un archivo por clip = reimports mínimos, avatar compartido limpio, cero slicing manual, y cada animación versionable por separado. El FBX único sirve para prototipos o personajes con 2-3 anims. **El esqueleto y los nombres de hueso son idénticos entre el `.fbx` base y todos los `@`** — obligatorio (si cambian, se rompe el Avatar copiado) [ver: rigging/rig-a-unity].

---

## 3. Preparar el clip en Blender ANTES de exportar

El FBX hornea el **resultado evaluado** de la Action. Lo que no sea keyframes puros hay que bakearlo primero.

| Paso | Por qué | Cómo (5.2) |
|---|---|---|
| **Bakear constraints / IK a keyframes** | Constraints e IK **no viajan** al FBX — solo el resultado bakeado [ver: blender/import-export] | `Pose ‣ Animation ‣ Bake Action` (op `nla.bake`), `visual_keying=True`, `bake_types={'POSE'}` |
| **Root/traj bone con el desplazamiento** | Unity lee el root motion de UN hueso (Generic Root Node) o del Body (Humanoid) [ver: rigging/rig-a-unity §6] | Que el avance real esté horneado en el hueso raíz, no repartido |
| **fps de escena = el que espera Unity** | El FBX declara su framerate; mismatch = clip a otra velocidad y foot sliding (§7) | `scene.render.fps` (30/60) antes de exportar |
| **Cerrar el loop** | Frame final = frame inicial (o duplicado del primero) para que Loop Match dé verde [ver: animacion3d/ciclos-locomocion] | Regla del frame duplicado; tangentes limpias en el seam [ver: graph-editor] |
| **Rango de frames exacto** | El clip en Unity toma el `frame_start`–`frame_end` de la escena/Action | `scene.frame_start` / `frame_end` ceñidos al clip |

Bakear IK/constraints a hueso (headless), sobre el armature en Pose Mode:

```python
import bpy
bpy.ops.object.mode_set(mode='POSE')
bpy.ops.pose.select_all(action='SELECT')
bpy.ops.nla.bake(
    frame_start=bpy.context.scene.frame_start,
    frame_end=bpy.context.scene.frame_end,
    step=1,
    only_selected=True,
    visual_keying=True,       # captura el resultado de constraints/IK
    clear_constraints=True,   # quita los constraints ya horneados
    use_current_action=True,  # escribe sobre la Action activa
    bake_types={'POSE'},
)
```
*(Operador `nla.bake` verificado por conocimiento del menú Bake Action de 5.2; confirmar defaults si el resultado sorprende. Nunca aplicar transforms al armature en pose — solo en Object Mode sobre el rest [ver: blender/import-export].)*

Cuadrar fps y rango antes de exportar:

```python
sc = bpy.context.scene
sc.render.fps = 30            # = sample rate = lo que Unity espera
sc.frame_start = 1
sc.frame_end = 32             # exacto al clip (32 frames a 30fps ≈ 1.07s)
```

Insertar un key de root a mano (ej. bakear avance a un traj bone), para automatizar:

```python
arm = bpy.data.objects["Armature_Hero"]
root = arm.pose.bones["root"]
root.location = (0.0, 0.0, 0.0)
root.keyframe_insert(data_path="location", frame=1)
root.location = (0.0, 2.0, 0.0)   # avanza 2 m en Y local a lo largo del clip
root.keyframe_insert(data_path="location", frame=32)
```

---

## 4. Settings EXACTOS del Bake Animation en el export FBX

`File ‣ Export ‣ FBX (.fbx)` — panel **Bake Animation** de `export_scene.fbx`. Los settings generales (escala `FBX_SCALE_UNITS`, ejes -Z/Y, Add Leaf Bones OFF, Only Deform Bones) están en [ver: blender/import-export] y [ver: rigging/rig-a-unity]; aquí SOLO la animación:

| Opción UI | Propiedad bpy | Default | Para clips a Unity | Qué hace |
|---|---|---|---|---|
| **Bake Animation** | `bake_anim` | ON | **ON** | Master del bake de animación; OFF = FBX sin clips |
| **Key All Bones** | `bake_anim_use_all_bones` | ON | **ON** | Fuerza ≥1 key en TODOS los huesos (algunos targets lo exigen; evita huesos "sin animar") |
| **NLA Strips** | `bake_anim_use_nla_strips` | ON | según flujo | Cada strip NLA no-muteado = un take (AnimStack) separado [ver: nla-editor] |
| **All Actions** | `bake_anim_use_all_actions` | ON | **OFF** para `@anim` / clip único | ON = un take por CADA Action del .blend → clips basura en Unity |
| **Force Start/End Keying** | `bake_anim_force_startend_keying` | ON | **ON** | Añade key al inicio y fin de la Action en los canales animados → largo de clip exacto y loop limpio |
| **Sampling Rate** | `bake_anim_step` | 1.0 | **1.0** | Cada cuántos frames se evalúa el valor animado. 1.0 = un sample por frame al fps de escena. <1 supersamplea, >1 subsamplea |
| **Simplify** | `bake_anim_simplify_factor` | 1.0 | **0.0–1.0** | Cuánto simplifica los valores horneados. 0 = sin simplificar (curvas fieles); subirlo borra keys y degrada el movimiento |

**Interacción NLA Strips ↔ All Actions:**
- Quieres **un clip = una Action** → `use_all_actions=False`, `use_nla_strips=False`, con esa Action **activa** en el armature (se exporta como la animación global de escena = un solo take).
- Quieres **un clip por Action** en un FBX único → `use_all_actions=True`.
- Compones takes a mano con strips → `use_nla_strips=True` [ver: nla-editor].

> **Verificación de esta tabla:** propiedades, defaults y descripciones contra la base empírica [ver: blender/import-export] (dump RNA de `export_scene.fbx` en Blender 5.2.0) **y confirmadas esta sesión leyendo el código fuente real del exportador** (`io_scene_fbx/__init__.py`, repo `blender-addons` en `projects.blender.org`): los seis defaults de la tabla (`bake_anim`, `bake_anim_use_all_bones`, `bake_anim_use_nla_strips`, `bake_anim_use_all_actions`, `bake_anim_force_startend_keying` = `True`; `bake_anim_step`, `bake_anim_simplify_factor` = `1.0`) y sus tooltips coinciden exactamente. `docs.blender.org` sigue bloqueando el fetch esta sesión (403) — no verificado ahí, pero el código fuente del addon es la fuente primaria de estos valores. Detalle del bake en [ver: bake-animacion].

---

## 5. Generar los `modelo@anim.fbx` (patrón headless)

Un archivo por Action, solo armature, con la Action activa. `use_selection=True` sobre el armature:

```python
import bpy, os
OUT = bpy.path.abspath("//export")
os.makedirs(OUT, exist_ok=True)
arm = bpy.data.objects["Armature_Hero"]
MODEL = "Hero"                       # nombre base = el del .fbx de malla (sin @)

# solo el armature seleccionado
bpy.ops.object.select_all(action='DESELECT')
arm.select_set(True)
bpy.context.view_layer.objects.active = arm

for action in bpy.data.actions:
    arm.animation_data.action = action          # activar esta Action
    bpy.context.scene.frame_start = int(action.frame_range[0])
    bpy.context.scene.frame_end   = int(action.frame_range[1])
    bpy.ops.export_scene.fbx(
        filepath=os.path.join(OUT, f"{MODEL}@{action.name}.fbx"),
        use_selection=True,
        object_types={'ARMATURE'},              # sin malla → archivo mínimo
        apply_scale_options='FBX_SCALE_UNITS',  # File Scale 1 en Unity
        add_leaf_bones=False,                    # sin huesos _end
        use_armature_deform_only=True,           # solo huesos de deform
        bake_anim=True,
        bake_anim_use_all_actions=False,         # esta Action, un solo take
        bake_anim_use_nla_strips=False,
        bake_anim_force_startend_keying=True,
        bake_anim_step=1.0,
        bake_anim_simplify_factor=0.0,           # curvas fieles
    )
```

En Unity: el `Hero.fbx` (malla+rig) crea el Avatar (`Create From This Model`); cada `Hero@*.fbx` va en **`Copy From Other Avatar` → Avatar de Hero** [ver: rigging/rig-a-unity §3]. Con malla excluida, activar **Preserve Hierarchy** en el import de los `@`.

---

## 6. Múltiples clips de un FBX: takes vs slicing manual

Dos maneras de tener varios clips en un solo FBX:

| Vía | Cómo | Resultado en Unity |
|---|---|---|
| **All Actions / NLA (takes)** | `bake_anim_use_all_actions=True` o un strip por clip [ver: nla-editor] | Unity muestra un clip por take, ya cortado |
| **Timeline único + slicing manual** | Un timeline largo con todas las anims seguidas; frame ranges anotados | En el **Animation tab** del importer: lista de Clips, botón `+`, setear **Start**/**End** por clip |

Slicing manual en el importer (Manual Unity: "animation cutting tools… select the frame range for each clip"): en la lista de Clips, `+` para añadir, arrastrar los handles o teclear **Start** / **End** frame, renombrar. Automatizable con `ModelImporterClipAnimation` (`name`, `firstFrame`, `lastFrame`, `loopTime`, …).

**Preferencia:** el patrón `@anim` (§5) evita todo esto — 1 archivo = 1 clip, sin cortar. El slicing manual es para cuando te llega UN timeline monolítico (mocap, un .blend heredado).

---

## 7. Framerate: el fps de Blender = el sample rate = lo que Unity espera

Cadena que **tiene que cuadrar**: `scene.render.fps` (Blender) → `bake_anim_step=1` (un key por frame) → framerate declarado en el FBX → clip en Unity a ese fps.

- Si Blender está a 24 y el juego corre a 30/60, el clip **no** se rompe (Unity resamplea por tiempo, no por frame), pero:
  - El **largo en segundos** del clip es `frames / fps_de_Blender`. fps mal = clip más corto/largo de lo pensado → **la velocidad del ciclo no cuadra con la velocidad de gameplay → foot sliding** [ver: animacion3d/ciclos-locomocion].
- Foot sliding por mismatch se ataca en Unity con blend por velocidad y thresholds MEDIDOS (no a ojo), stride warping o foot-lock IK — todo eso vive en [ver: animacion3d/ciclos-locomocion] y [ver: unity/animacion-unity]. Desde Blender, la parte que te toca es: **fps de escena = fps objetivo del juego** y `bake_anim_step=1`.
- Unity muestra el framerate como **Sample Rate** del clip. Compresión y resample: [ver: §8] y [ver: animacion3d/keyframes-curvas] (qué sobrevive al import).

---

## 8. En Unity: el clip, el avatar y la compresión

Settings del clip en el **Animation tab** del importer (`class-AnimationClip`), lo operativo:

| Setting | Qué hace | Cuándo |
|---|---|---|
| **Loop Time** | "Play the animation clip through and restart when the end is reached" | ON en idle/walk/run y todo ciclo |
| **Loop Pose** | "Loop the motion seamlessly" — blendea el delta pose inicio↔fin en el marco del Root Transform | ON si el seam aún salta pese a cerrar el loop en Blender |
| **Cycle Offset** | "Offset to the cycle… if it starts at a different time" | Desfasar el punto de arranque del ciclo |
| **Mirror** | "Mirror left and right in this clip" | Generar el espejo sin reanimar |
| **Additive Reference Pose / Pose Frame** | Frame base para clips additive (respiración, lean) | Capas additive [ver: unity/animacion-unity] |
| **Root Transform** (Rotation / Position Y / Position XZ) | Bake Into Pose + Based Upon por eje (§9) | Root motion |

**El indicador de loop (Loop Match):** al lado de Loop Time/Loop Pose Unity pinta un semáforo **verde/amarillo/rojo** según cuánto difieren el primer y último frame. Rojo = el ciclo NO cierra → volver a Blender a cuadrar el seam [ver: animacion3d/ciclos-locomocion]. La técnica de cerrar loops (frame duplicado, contactos en tiempos normalizados) es de la base; aquí solo se **valida** con el semáforo.

**Avatar compartido:** los `@anim` en `Copy From Other Avatar` apuntando al Avatar del modelo base → todos los clips intercambiables, sin regenerar Avatar por clip [ver: rigging/rig-a-unity].

**Compresión y fidelidad** (top del Animation tab / `ModelImporter`): **Anim. Compression** = `Off` / `Keyframe Reduction` / `Optimal`; con reducción, **Rotation Error / Position Error / Scale Error** controlan cuánto se puede desviar (`ModelImporter.animationRotationError` — "Allowed error of animation rotation compression", en grados; análogo para Position/Scale). **Resample Curves** (`resampleCurves`) resamplea las curvas al importar salvo que se desactive. Curvas muy pulidas (overshoot, settle) pueden aplanarse si el error es alto — qué sobrevive al import y cómo protegerlo está en [ver: animacion3d/keyframes-curvas]. ⚠️ **NO VERIFICADO:** el default numérico exacto de los tres Error (se citaba 0.5 de memoria) y si `resampleCurves` nace ON — la Scripting API 6000.2 documenta qué hace cada propiedad pero no expuso el default en el fetch de esta sesión; confirmar en el Animation tab real antes de asumir el número.

---

## 9. Root motion en el export → Unity

El **desplazamiento del personaje** tiene que llegar como root motion, no perderse. Reparto de responsabilidades:

| Dónde | Qué se hace |
|---|---|
| **Blender** | El avance real horneado en el **hueso raíz** (o traj bone) — no repartido entre huesos. In-place vs con desplazamiento se decide en [ver: animacion3d/ciclos-locomocion] |
| **Export FBX** | El hueso raíz viaja como cualquier hueso de deform; nada especial salvo que exista y lleve el movimiento |
| **Unity — Rig tab** | **Generic:** asignar **Root Node** = ese hueso. **Humanoid:** usa el **Body Transform** automático [ver: rigging/rig-a-unity §6] |
| **Unity — clip** | **Bake Into Pose = "esto NO sale al GameObject"**. Walk que avanza: **Position (XZ) sin bakear**. Idle: **Position (XZ) bakeado** (anti-drift). Rotación/Y según diseño |
| **Unity — Animator** | `Apply Root Motion` ON si la animación mueve al personaje; OFF si lo mueve tu código |

**Based Upon** (origen de referencia por eje, del clip inspector): `Body Orientation` (default, va bien para mocap), `Original` (respeta el offset autorado), `Center of Mass`, `Feet`, `Root Node`. La tabla lunge/in-place/plunge para ataques (con su Bake Into Pose) está en [ver: animacion3d/animacion-combate]; el detalle Body/Root Transform en [ver: rigging/rig-a-unity].

---

## Reglas prácticas

1. **1 Action = 1 clip = 1 armature** es el patrón seguro también en 5.2 (Slotted Actions no lo cambia para game export).
2. Producción con muchos clips → **`modelo@anim.fbx`** (un archivo por clip): reimports mínimos, avatar compartido, cero slicing.
3. Esqueleto y nombres de hueso **idénticos** entre el `.fbx` base y todos los `@` (si cambian, se rompe el Copy From Other Avatar).
4. `@` van en **Copy From Other Avatar** al Avatar del modelo base; malla fuera de los `@` + **Preserve Hierarchy** ON.
5. **Bakear IK/constraints a keyframes** (`nla.bake`, `visual_keying=True`) antes de exportar — no viajan al FBX.
6. `scene.render.fps` = fps objetivo del juego, y `bake_anim_step=1.0` — evita clip a otra velocidad y foot sliding.
7. `bake_anim_force_startend_keying=True` → largo de clip exacto y loop limpio.
8. `bake_anim_use_all_actions=False` para `@anim`/clip único; ON solo si quieres a propósito un take por Action en un FBX gordo.
9. `bake_anim_simplify_factor=0.0` para curvas fieles; subirlo solo si el clip pesa demasiado y lo aceptas.
10. Add Leaf Bones OFF + Only Deform Bones ON en todo export con rig [ver: rigging/rig-a-unity].
11. `apply_scale_options='FBX_SCALE_UNITS'` → File Scale 1 en Unity [ver: blender/import-export].
12. Cerrar el loop en Blender (frame duplicado, seam limpio) y **validar el semáforo verde de Loop Match** en Unity [ver: animacion3d/ciclos-locomocion].
13. Root motion: hueso raíz con el avance horneado; **Root Node** (Generic) o Body (Humanoid); Bake Into Pose = "no sale al GameObject" (idle bakea XZ, walk no).
14. `Apply Root Motion` en el Animator ON solo si la animación mueve al personaje.
15. Anim. Compression / Error thresholds conscientes; curvas pulidas se aplanan si el error es alto [ver: animacion3d/keyframes-curvas].
16. Tocar un clip = reexportar SOLO su `@` (mismo path) → Unity reimporta ese archivo; no borrar y reimportar (mata el GUID) [ver: blender/import-export].
17. Todo "listo" = clip abierto en Unity, corriendo, loopeando, a velocidad correcta y sin bones extra — no "el export no dio error".

## Errores comunes

| Pitfall | Síntoma en Unity | Antídoto |
|---|---|---|
| Constraints/IK sin bakear | El personaje no se mueve como en Blender; huesos "muertos" | `nla.bake` con `visual_keying=True` antes de exportar |
| `bake_anim_use_all_actions=True` con .blend lleno de Actions | Docena de clips basura por FBX | `False`; una Action activa por archivo, o patrón `@anim` |
| fps de escena ≠ fps del juego | Clip a otra velocidad → foot sliding | `scene.render.fps` = objetivo, `bake_anim_step=1` |
| Loop Match en rojo | El ciclo salta en el seam | Cerrar el loop en Blender (frame duplicado, tangentes en el seam) [ver: animacion3d/ciclos-locomocion]; Loop Pose ON como parche |
| Idle que deriva de posición | El personaje se va desplazando parado | Root Transform Position (XZ) → **Bake Into Pose ON** |
| Walk que "corre en el sitio" | No avanza pese a tener desplazamiento | Position (XZ) **sin** bakear + `Apply Root Motion` ON + Root Node asignado |
| Cada `@` genera su propio Avatar | Retargeting/blending roto entre clips | Poner los `@` en **Copy From Other Avatar** al Avatar base |
| Nombres de hueso cambiados entre `.fbx` base y `@` | Avatar inválido, curvas perdidas | Congelar el naming del rig tras el primer import |
| Add Leaf Bones ON (default) | Huesos `_end` por todo el esqueleto | `add_leaf_bones=False` |
| Simplify alto | Movimiento "aplastado", overshoot perdido | `bake_anim_simplify_factor=0.0`; o bajar Anim. Compression Error en Unity |
| Malla incluida en los `@` | Archivos pesados, reimports lentos, duplicados | `object_types={'ARMATURE'}` + Preserve Hierarchy ON en el import |
| Borrar el FBX del clip para "refrescar" | Referencias del Animator rotas (GUID nuevo) | Sobrescribir mismo path; Reimport desde Unity [ver: blender/import-export] |
| Reusar una Action multi-slot (5.2) sobre armature+shapekeys | Take inesperado o canales de más | Verificar el take en Unity; separar en Actions por data-block si confunde |

## Fuentes

- **Unity Manual 6000.2 — Import animations using multiple model files** (`Splittinganimations.html`) — Unity Technologies — convención `modelo@anim.fbx`, "Unity automatically imports all files and collects all animations to the file without the @ sign in", malla excluida + Preserve Hierarchy. *(WebFetch OK)*
- **Unity Manual 6000.2 — Root Motion** (`RootMotion.html`) — Unity Technologies — Body vs Root Transform, Root Node (Generic), Bake Into Pose por eje, Based Upon (Body Orientation/Original/Center of Mass/Feet), Loop Pose. *(WebFetch OK)*
- **Unity Manual 6000.2 — Animation Clip import settings** (`class-AnimationClip.html`) — Unity Technologies — lista de Clips + Start/End, Loop Time, Loop Pose, Cycle Offset, Mirror, Additive Reference Pose, Root Transform Rotation/Position (Y)/(XZ). *(WebFetch OK)*
- **Unity Manual 6000.2 — Importing animations** (`AnimationsImport.html` / `class-FBXImporter.html`) — Unity Technologies — múltiples takes en un timeline y las "animation cutting tools" para elegir frame range por clip. *(WebFetch OK)*
- **Unity Scripting API 6000.2 — `ModelImporterClipAnimation`** — Unity Technologies — `name`, `firstFrame`, `lastFrame`, `loopTime`, `loopPose`, `cycleOffset`, `lockRootRotation`/`lockRootHeightY`/`lockRootPositionXZ`, `keepOriginal*`, `heightFromFeet`, `mirror`, `maskType` (automatizar el slicing). *(WebFetch OK)*
- **Unity Scripting API 6000.2 — `ModelImporter`** — Unity Technologies — `animationCompression` (Off/KeyframeReduction/KeyframeReductionAndCompression/Optimal), `resampleCurves`, `animationRotationError`/`PositionError`/`ScaleError`, `importConstraints`, `optimizeGameObjects`. *(WebFetch OK)*
- **Base sintetizada — [ver: blender/import-export]** — export FBX verificado empíricamente contra Blender 5.2.0 (dump RNA de `export_scene.fbx`: `bake_anim*`, `apply_scale_options`, `add_leaf_bones`, `use_armature_deform_only`; escala 100×/FBX Units Scale; -89.98/Bake Axis Conversion; convención `@`; roundtrip de prefab por GUID).
- **Base sintetizada — [ver: rigging/rig-a-unity]** — Rig tab (Humanoid/Generic), Avatar, Copy From Other Avatar, Root Node, Bake Into Pose, Only Deform/Add Leaf Bones.
- **Base sintetizada — [ver: unity/animacion-unity]** — consumo del clip: Animator, blend trees, Loop, eventos, culling.
- **Base sintetizada — [ver: animacion3d/ciclos-locomocion] / [keyframes-curvas] / [animacion-combate]** — cerrar loops, foot sliding y sus antídotos, qué sobrevive al import/compresión, root motion en ataques (Bake Into Pose).
- **Sistema Baklava / Slotted Actions (Blender 4.4, mar-2025)** — conocimiento del proyecto de animación; slots por data-block, legacy Actions, layers internos. ⚠️ **NO re-verificado contra docs.blender.org 5.2** (el sitio devuelve 403 a WebFetch esta sesión) — el patrón operativo "1 Action = 1 clip" es lo seguro. Detalle en [ver: sistema-animacion] y [ver: actions-organizacion].
- **Exportador FBX de Blender — panel Bake Animation** (`io_scene_fbx`, bundled 5.2) — nombres/props/tooltips (`bake_anim`, `bake_anim_use_all_bones`, `bake_anim_use_nla_strips`, `bake_anim_use_all_actions`, `bake_anim_force_startend_keying`, `bake_anim_step`, `bake_anim_simplify_factor`) desde la base empírica + **código fuente confirmado esta sesión** vía `projects.blender.org/blender/blender-addons` (`io_scene_fbx/__init__.py`, rama `main`) — defaults y descripciones exactas. ⚠️ `docs.blender.org` sigue sin ser accesible por fetch esta sesión (403).
- **Unity Scripting API 6000.2 — `ModelImporter-animationRotationError.html` / `ModelImporter-resampleCurves.html`** — confirmado esta sesión: describen el comportamiento pero NO exponen el default numérico; el "0.5" y "ON por defecto" citados en versiones previas de esta base quedan como NO VERIFICADO hasta confirmar en el Animation tab real.
- **glTF-Blender-IO (Khronos), repo GitHub** — confirmado esta sesión (`gltf2_blender_ui.py`): `export_animation_mode` acepta al menos `"ACTIONS"`, `"ACTIVE_ACTIONS"`, `"BROADCAST"` como valores de enum — corrobora la mención de `'ACTIONS'` en §1, aunque no se recuperaron todas las descripciones.
