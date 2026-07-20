# Animar en Blender por código (MCP/headless) y exportar clips a Unity

> **Cuando cargar este archivo:** siempre que un agente vaya a EJECUTAR animación dentro de Blender 5.2 por código — insertar keyframes programáticos, aplicar F-curve modifiers, hornear (bake) acciones, importar/organizar mocap, limpiar curvas o exportar clips a Unity 6 en lote (FBX/glTF), vía el MCP "blender" o `blender --background`. Es el manual operativo de la EJECUCIÓN. La TÉCNICA (qué hace bueno a un ciclo, timing, spacing, combate, acting) NO vive aquí: vive en `animacion3d/` — aquí va el CÓMO en Blender y el export limpio.

Verificado contra el binario real **Blender 5.2.0 LTS** (Homebrew, build 2026-07-14) por introspección RNA y pruebas funcionales headless en esta sesión, más el **manual de Unity 6** (docs.unity3d.com/6000.2). El stack MCP y bpy están en sus bases: cómo operar el Blender vivo [ver: blender/blender-mcp-operativo], cómo escribir bpy limpio [ver: blender/bpy-scripting]. La integración en Unity de lo que exportes está en [ver: unity/animacion-unity].

---

## 0. El reto: qué SÍ hace un agente ciego y qué necesita ojos

Animar es intrínsecamente **visual y temporal**: la calidad vive en arcos, timing, spacing y acting, cosas que se juzgan mirando el movimiento en el tiempo, no leyendo números. Un agente por código no ve el movimiento; ve datos por frame. De ahí el reparto:

| El agente por código SÍ puede (barato y exacto) | Necesita ojos (humano o render + lectura) |
|---|---|
| Insertar keyframes calculados (pose por frame por fórmula) | Juzgar si un arco "se siente" bien |
| Aplicar F-curve modifiers (Cycles, Noise), extrapolación | Timing artístico, anticipación, follow-through |
| Bake action / samplear, limpiar y decimar curvas | Acting, intención, peso, contacto de pies |
| Importar/renombrar/organizar mocap (Mixamo, librería) | Pulir un clip crudo de mocap para que lea bien |
| Batch export de N clips a FBX/glTF con settings idénticos | Decidir POSES clave de un movimiento nuevo desde cero |
| Verificar: nº de keyframes, rango, fps, valor de una curva por frame | Composición/silueta de una pose (necesita render) |

Regla madre: **el agente monta el andamiaje (importar, batchear, hornear, limpiar, exportar); el humano/artista pule lo expresivo.** Animar un ciclo o un combate "desde cero a ciegas" casi nunca conviene — trae mocap/librería y ajústalo (§8) o pide las poses clave al humano [ver: animacion3d/mocap-librerias].

---

## 1. Sistema de animación de 5.2: Slotted Actions ("Baklava") — NO es el sistema viejo  [ver: sistema-animacion]

El sistema de acciones **cambió** en 4.4 (proyecto "Baklava" / Slotted Actions) y en 5.2 es el sistema por defecto. Muchísimo snippet de la web es pre-4.4 y **está roto**. Estructura real verificada en 5.2:

```text
Action
 ├─ slots[]     (ActionSlot)   → cada slot = un "canal" para UN data-block (Object, Armature, …)
 └─ layers[]    (ActionLayer)  → capas apilables
      └─ strips[]  (ActionKeyframeStrip, type='KEYFRAME')
           └─ channelbags[]  (ActionChannelbag)  ← aquí viven las F-Curves
                └─ fcurves[]  +  groups[]
```

Cambios que rompen scripts viejos (verificado: estas propiedades **ya no existen** en el tipo `Action` en 5.2):

| Antes (≤4.3) | En 5.2 | Cómo llegar ahora |
|---|---|---|
| `action.fcurves` | **eliminado** | fcurves viven en un `ActionChannelbag` por slot |
| `action.groups` | **eliminado** | `channelbag.groups` |
| `action.id_root` | **eliminado** | `slot.target_id_type` (enum: OBJECT, ARMATURE, …) |
| 1 Action ↔ 1 objeto | 1 Action puede animar **varios** data-blocks | un slot por data-block dentro de la misma Action |

Propiedades nuevas útiles (verificadas): `action.is_action_legacy` / `action.is_action_layered` (una Action recién creada por keyframe es **layered**), `action.slots`, `action.layers`, `action.use_frame_range`, `action.use_cyclic`, `action.frame_start/frame_end`, `action.frame_range`, `action.curve_frame_range`.

**Acceso correcto a las F-Curves en 5.2** (helper oficial en `bpy_extras.anim_utils`):

```python
import bpy
from bpy_extras import anim_utils
ad   = obj.animation_data          # None si el objeto no tiene animación
act  = ad.action
slot = ad.action_slot              # el slot asignado a ESTE objeto (POINTER)
cbag = anim_utils.action_ensure_channelbag_for_slot(act, slot)  # crea/obtiene el channelbag
for fc in cbag.fcurves:
    print(fc.data_path, fc.array_index, len(fc.keyframe_points))
locz = cbag.fcurves.find("location", index=2)   # una curva concreta
```

Helpers verificados en `anim_utils`: `action_ensure_channelbag_for_slot`, `action_get_channelbag_for_slot`, `animdata_get_channelbag_for_assigned_slot`, `action_get_first_suitable_slot`. `AnimData` expone: `action`, `action_slot`, `action_slot_handle`, `action_suitable_slots`, `nla_tracks`, `action_blend_type` (REPLACE/COMBINE/ADD/SUBTRACT/MULTIPLY), `action_extrapolation` (NOTHING/HOLD/HOLD_FORWARD), `action_influence`, `use_nla`.

---

## 2. Insertar keyframes por código — animación procedural  [ver: animacion3d/principios-produccion]

`bpy_struct.keyframe_insert(data_path, index=-1, frame=<frame actual>, group="", options=set())` existe en **cualquier** ID/PoseBone. Al primer keyframe, Blender crea sola una Action **layered** con un slot (identificador = prefijo de 2 letras del tipo + nombre, p.ej. `OBCube`) y una capa `Layer`. Verificado.

```python
import bpy, math
obj = bpy.data.objects["Cube"]
for f in range(1, 49):                       # ciclo de 48 frames
    t = (f - 1) / 48.0
    obj.location.z    = 0.5 * math.sin(t * 2*math.pi)   # bob senoidal
    obj.rotation_euler.z = t * math.radians(360)        # giro
    obj.keyframe_insert("location",       index=2, frame=f)   # solo eje Z
    obj.keyframe_insert("rotation_euler", index=2, frame=f)
# index=-1 (default) keyea los 3 ejes de un vector de golpe
```

**Huesos:** `pose_bone.keyframe_insert("rotation_quaternion", frame=f)` genera el data_path `pose.bones["Nombre"].rotation_quaternion` (4 curvas). El slot sigue siendo `target_id_type='OBJECT'` (se anima el Object, no el data-block Armature). Verificado. Nunca escribas el data_path a mano si puedes llamar `keyframe_insert` sobre el propio pose bone. La técnica de rig/pose está en [ver: rigging/esqueletos-armature].

`options` — set válido **verificado en 5.2**: `{'INSERTKEY_NEEDED', 'INSERTKEY_VISUAL', 'INSERTKEY_REPLACE', 'INSERTKEY_AVAILABLE', 'INSERTKEY_CYCLE_AWARE'}`. ⚠️ `INSERTKEY_XYZ_TO_RGB` de scripts viejos **ya no es válido** y lanza error. `INSERTKEY_VISUAL` keyea el resultado tras constraints (útil para mocap/IK); `INSERTKEY_NEEDED` solo inserta si el valor cambió.

**Cuándo tiene sentido keyear por código:** movimiento paramétrico puro donde la fórmula ES la animación — idle breathing, bob de flotante, giro constante, pulso, pistón, órbita, oleaje. Para eso el código gana: exacto, reproducible, cero tedio. Para acting/locomoción con peso: NO — eso es mocap + pulido humano (§8, §10).

---

## 3. Graph Editor / F-Curves por código  [ver: graph-editor]

Todo lo del Graph Editor es data-API, no necesita ojos. Enums verificados en 5.2:

| Propiedad | Valores (5.2) |
|---|---|
| `keyframe.interpolation` | CONSTANT, LINEAR, BEZIER, SINE, QUAD, CUBIC, QUART, QUINT, EXPO, CIRC, BACK, BOUNCE, ELASTIC |
| `keyframe.easing` | AUTO, EASE_IN, EASE_OUT, EASE_IN_OUT |
| `fcurve.extrapolation` | CONSTANT, LINEAR |
| `fmodifier.type` | NULL, GENERATOR, FNGENERATOR, ENVELOPE, CYCLES, NOISE, LIMITS, STEPPED, SMOOTH |

```python
# Hacer que un ciclo se repita eternamente SIN copiar keyframes: F-modifier Cycles
m = locz.modifiers.new(type='CYCLES')          # verificado
m.mode_before = 'REPEAT'; m.mode_after = 'REPEAT'   # NONE/REPEAT/REPEAT_OFFSET/MIRROR
# Cambiar interpolación de todas las llaves a lineal (locomoción de robot, mocap crudo)
for kp in locz.keyframe_points:
    kp.interpolation = 'LINEAR'
locz.update()                                   # recompone handles tras editar por código
```

`REPEAT_OFFSET` acumula el delta cada ciclo (útil para un walk que avanza en root); `MIRROR` hace ping-pong. `NOISE` sirve para temblor/vida secundaria procedural. La TEORÍA de por qué una curva lee como buen movimiento (slow-in/out, spacing) está en [ver: animacion3d/keyframes-curvas]; aquí solo el operador.

Limpieza de curvas (operadores verificados, útiles tras mocap o bake denso):

| Operador | Params (5.2) | Uso |
|---|---|---|
| `bpy.ops.graph.clean` | `threshold=0.001`, `channels=False` | quita keyframes redundantes |
| `bpy.ops.graph.decimate` | `mode∈{RATIO,ERROR}`, `factor=0.333`, `remove_error_margin=0.0` | reduce densidad conservando forma |
| `bpy.ops.graph.euler_filter` | (sin params) | arregla gimbal flips en rotaciones Euler de mocap |

⚠️ Son operadores del Graph Editor: exigen contexto de área. Vía MCP o headless, envuélvelos en `bpy.context.temp_override(area=...)` o prefiere el bake (§6) que sí corre sin área [ver: blender/bpy-scripting].

---

## 4. Actions: organizar, renombrar, limpiar, stash  [ver: actions-organizacion]

Andamiaje 100% automatizable — el pan de cada día del agente:

```python
import bpy
# Renombrar clips con convención de proyecto y protegerlos de purga
for act in bpy.data.actions:
    act.name = "A_" + act.name.removeprefix("A_")
    act.use_fake_user = True          # sobrevive aunque ningún objeto lo use ahora
    print(act.name, "layered" if act.is_action_layered else "legacy",
          "range", tuple(act.frame_range))
```

- `use_fake_user = True` es **crítico**: una Action sin usuario y sin fake user se pierde al guardar/recargar. Todo clip que vayas a exportar o stashar necesita fake user o un usuario vivo.
- Una Action puede reunir **varios slots** (varios data-blocks). Para juegos suele preferirse **una Action por clip** (idle, walk, attack) para exportarlas limpias a Unity; usa slots múltiples solo si mantienes una escena de trabajo compartida.
- "Stash" = empujar la Action activa a una pista NLA para conservarla sin que esté activa: `bpy.ops.nla.action_pushdown(track_index=-1)` (verificado) — ver §5.
- Assets externos llegan con Actions basura y nombres feos: renómbralas y borra las que no exportes (filtrando por prefijo, nunca un purge global) [ver: blender/blender-mcp-operativo §6].

---

## 5. NLA: apilar y organizar clips  [ver: nla-editor]

El NLA (Non-Linear Animation) apila Actions como **strips** en **tracks** para combinarlas/reordenarlas. Para un agente sirve sobre todo como **almacén organizado** de clips y como fuente para el export por-NLA:

- `obj.animation_data.nla_tracks` (colección). Un track tiene strips; cada strip referencia una Action con su `frame_start`/`frame_end`.
- `bpy.ops.nla.action_pushdown(track_index=-1)` empuja la Action activa a una pista nueva (deja el slot de acción libre para la siguiente).
- El export FBX puede hornear cada strip NLA como take (`bake_anim_use_nla_strips`, §9); glTF tiene modo `NLA_TRACKS` (§9).
- La MEZCLA fina de capas (additive, influence, blending de layers para "herido + camina") es trabajo de artista/diseño de animación — cross-ref [ver: animacion3d/capas-estados]; el equivalente en Unity son layers + avatar masks [ver: unity/animacion-unity §3].

---

## 6. Bake Action: hornear a keyframes puros  [ver: bake-animacion]

Bake = convertir animación **derivada** (constraints, IK, drivers, físicas, F-modifiers, NLA) en keyframes explícitos por frame. **Imprescindible antes de exportar a Unity**: Unity no entiende constraints/IK/drivers de Blender — solo curvas por hueso. El operador de UI "Object ‣ Animation ‣ Bake Action" es `bpy.ops.nla.bake`. Params **verificados en 5.2**:

| Param | Default | Nota |
|---|---|---|
| `frame_start` / `frame_end` | 1 / 250 | rango a hornear |
| `step` | 1 | cada cuántos frames samplear (1 = todos) |
| `only_selected` | True | solo huesos seleccionados (POSE) |
| `visual_keying` | False | **True** para hornear el resultado VISUAL (IK/constraints) — casi siempre lo que quieres en mocap/rig |
| `clear_constraints` | False | borra constraints tras hornear (deja el rig "plano") |
| `clear_parents` | False | — |
| `use_current_action` | False | sobrescribe la Action actual en vez de crear una nueva |
| `clean_curves` | False | limpia keys redundantes al terminar |
| `bake_types` | `{'POSE'}` o `{'OBJECT'}` | enum: POSE, OBJECT |
| `channel_types` | LOCATION,ROTATION,SCALE,BBONE,PROPS | qué canales hornear |

⚠️ `bpy.ops.nla.bake` depende de contexto (objeto activo + selección + modo). En headless/MCP es más robusto el **helper Python** `bpy_extras.anim_utils.bake_action` (sin dependencia de área):

```python
from bpy_extras import anim_utils
opts = anim_utils.BakeOptions(
    only_selected=False, do_pose=True, do_object=False,
    do_visual_keying=True, do_constraint_clear=False, do_parents_clear=False,
    do_clean=True, do_location=True, do_rotation=True, do_scale=True,
    do_bbone=True, do_custom_props=False)          # dataclass, campos verificados
anim_utils.bake_action(obj, action=None, frames=range(1, 49), bake_options=opts)
# variante multi-objeto: anim_utils.bake_action_objects([(obj, action), ...], frames=..., bake_options=...)
```

No confundir con `bpy.ops.object.bake` (eso es **render bake** de texturas — otra cosa). El bake de animación es `nla.bake` / `anim_utils.bake_action`.

---

## 7. Traer animación de fuera (Mixamo / librería) y procesar por código  [ver: animacion3d/mocap-librerias]

Casi siempre mejor que animar desde cero. Flujo del agente:

```python
import bpy
bpy.ops.import_scene.fbx(filepath="/mocap/walk.fbx", automatic_bone_orientation=True)
# Mixamo nombra los huesos "mixamorig:Hips", etc. y trae 1 Action por archivo.
for act in bpy.data.actions:
    act.name = act.name.replace("mixamorig:", "").replace("|", "_")
```

Realidades y pasos típicos:
- Mixamo/mocap FBX = 1 clip por archivo, escala en cm (escala global 0.01), huesos con prefijo `mixamorig:`. Aplica escala y normaliza [ver: blender/bpy-scripting], luego `graph.euler_filter` si hay flips.
- **Retarget** (mover el mocap a TU rig): decisión técnica de rigging — herramientas y decisión en [ver: animacion3d/mocap-librerias]; el retarget Humanoid en [ver: rigging/rig-a-unity]; aquí el agente ejecuta el bake final (§6, `visual_keying=True`) y el export (§9).
- Batch: importar N FBX, renombrar Actions, hornear, exportar clips (§9) — todo scripteable sin ojos. El pulido de cada clip crudo (contactos, deslizamiento de pies) es del humano (§10).
- La elección de librería/Mixamo vs animar, y qué clips necesita un personaje de juego, es TÉCNICA → [ver: animacion3d/mocap-librerias]. Aquí solo el procesado.

---

## 8. Verificación sin ojos (y con render cuando hace falta)  [ver: blender/blender-mcp-operativo §7]

Tres niveles, del más barato al que sí necesita imagen:

**a) Numérico — la evidencia base (gratis, exacta):**

```python
from bpy_extras import anim_utils
ad = obj.animation_data; cbag = anim_utils.action_ensure_channelbag_for_slot(ad.action, ad.action_slot)
locz = cbag.fcurves.find("location", index=2)
print("keys:", len(locz.keyframe_points),
      "range:", tuple(locz.range()),                 # (primer_frame, último_frame)
      "@f12:", round(locz.evaluate(12), 4),          # valor de la curva en un frame
      "@f25:", round(locz.evaluate(25), 4))
print("action range:", tuple(ad.action.frame_range), "fps:", bpy.context.scene.render.fps)
```

Checks estándar de un clip: nº de keyframes esperado, `frame_range` correcto, la curva pasa por los valores que calculaste (`fc.evaluate(f)`), fps de escena (default 24 — **fija el fps a lo que espera Unity antes de exportar**). Esto atrapa el 80% de los errores (curva plana, rango vacío, clip que no se creó).

**b) Muestrear el movimiento por frames** (perfil de una propiedad para ver si "sube y baja" como toca): recorrer `range(start, end)` y `print(f, round(fc.evaluate(f),3))` — una tabla de números ya te dice si el arco existe, aunque no si es bonito.

**c) Render de un rango a imágenes y leerlas** (única forma de "ver" el movimiento sin humano):

```python
import bpy
sc = bpy.context.scene
sc.render.engine = 'BLENDER_WORKBENCH'                 # o BLENDER_EEVEE (5.x id, no _NEXT)
sc.render.image_settings.media_type = 'IMAGE'          # 5.0+: ANTES de file_format
sc.render.image_settings.file_format = 'PNG'
sc.render.resolution_x, sc.render.resolution_y = 640, 360
for f in (1, 12, 24, 36, 48):                          # frames clave del ciclo
    sc.frame_set(f)                                    # evalúa la animación en ese frame
    sc.render.filepath = f"/evidencia/clip_{f:03d}.png"
    bpy.ops.render.render(write_still=True)
    print("render", f, sc.render.filepath)
```

Luego el agente **lee** esas PNG con su tool de imagen y compara poses entre frames (¿la pierna cambió? ¿el arco se ve?). Sirve para "el clip se mueve / no se mueve" y silueta de poses clave; NO sustituye el ojo humano para calidad de acting. Vía MCP con GUI, `get_viewport_screenshot` da un vistazo rápido pero es la pantalla literal [ver: blender/blender-mcp-operativo]. Un playblast (viewport render de secuencia) es `bpy.ops.render.opengl(animation=True)` — solo Workbench/EEVEE.

---

## 9. Export limpio de clips a Unity 6  [ver: export-clips-unity] · [ver: unity/animacion-unity]

### Preparar ANTES de exportar (checklist obligatorio)
1. Modo OBJECT (`bpy.ops.object.mode_set(mode='OBJECT')`) [ver: blender/bpy-scripting].
2. **Bake** toda animación derivada (IK/constraints/NLA/F-modifiers) a keyframes (§6).
3. Escala aplicada, transform limpio; `scale=(1,1,1)`. Unity importa a metros.
4. **fps de escena = fps objetivo de Unity** (default Blender 24): fija `scene.render.fps` y el rango de escena al del clip.
5. `use_fake_user` en toda Action a exportar.

### FBX — el camino robusto para rigs. Params `export_scene.fbx` verificados (5.2):

```python
import bpy
bpy.ops.export_scene.fbx(
    filepath="/export/hero@walk.fbx",
    use_selection=True,                    # exporta solo la selección (rig + clip actual)
    object_types={'ARMATURE', 'MESH'},
    add_leaf_bones=False,                  # ⚠️ default True mete huesos "_end" basura en Unity
    bake_anim=True,
    bake_anim_use_all_actions=False,       # False = SOLO la acción activa (1 clip por archivo)
    bake_anim_use_nla_strips=False,
    bake_anim_force_startend_keying=True,  # keys en primer y último frame (evita clips recortados)
    bake_anim_step=1.0,
    bake_anim_simplify_factor=1.0,         # 0.0 = sin simplificar (fidelidad máxima)
    primary_bone_axis='Y', secondary_bone_axis='X',   # defaults de Blender
)
```

| Param FBX | Default | Para Unity |
|---|---|---|
| `bake_anim` | True | debe quedar True |
| `bake_anim_use_all_actions` | True | **False** si quieres 1 clip por archivo (patrón `model@anim`); True mete todas las Actions como takes |
| `bake_anim_use_nla_strips` | True | hornea strips NLA como takes |
| `bake_anim_force_startend_keying` | True | déjalo True: garantiza el rango |
| `bake_anim_simplify_factor` | 1.0 | baja a 0 si el mocap pierde detalle |
| `add_leaf_bones` | True | **pon False**: los leaf bones ensucian el avatar en Unity |
| `use_armature_deform_only` | False | True descarta huesos de control no-deform (rig más limpio) |

### glTF — alternativa moderna. Params `export_scene.gltf` verificados (5.2):

`export_animations=True`, `export_animation_mode∈{ACTIONS, ACTIVE_ACTIONS, BROADCAST, NLA_TRACKS, SCENE}` (default `ACTIONS`), `export_frame_range`, `export_force_sampling=True` (samplea = hornea al vuelo), `export_nla_strips=True`, `export_optimize_animation_size=True`, `export_anim_slide_to_zero`, `export_negative_frame∈{SLIDE,CROP}`, `export_current_frame`. Batch por colección igual que assets estáticos [ver: blender/bpy-scripting].

### El lado Unity (verificado, manual 6000.2)
- **Convención `model@animation.fbx`**: `hero@idle.fbx`, `hero@walk.fbx`, `hero@jump.fbx`. Unity **junta todas las animaciones en el archivo base sin `@`** (`hero.fbx`) automáticamente. Los archivos de anim no necesitan malla, pero activa **Preserve Hierarchy** en el importer si la omites.
- **Un solo timeline con varios clips**: pestaña **Animation** del Model Importer → lista de **Clips** con botón `+`, cada clip con **Start**/**End** (frames) arrastrables. Por clip: **Loop Time**, **Loop Pose**, **Cycle Offset**, **Root Transform Rotation / Position (Y) / Position (XZ)** con **Bake Into Pose** + **Based Upon**, **Mask**, **Curves**, **Events**.
- **Rig tab**: **Animation Type** = Humanoid / Generic / Legacy. Humanoid pide ≥15 huesos y crea un **Avatar**; **Avatar Definition** = *Create From This Model* o *Copy From Other Avatar* (+ **Source**) para compartir avatar entre archivos de clip. **Configure…** valida el mapeo (check = ok, cruz = falló). Humanoid habilita **retargeting** (mismo clip a otro personaje); Generic es más barato si no necesitas retarget [ver: unity/animacion-unity §1]. La configuración de Animator/blend trees/eventos ya en Unity está en [ver: unity/animacion-unity].

Nomenclatura de archivos y estructura de carpetas del pipeline: [ver: pipeline/arte-a-unity].

---

## 10. El flujo realista agente + humano

| Fase | Quién | Qué |
|---|---|---|
| Andamiaje | **Agente** | importar mocap/librería, renombrar, escalar, `euler_filter`, organizar Actions/NLA |
| Procedural puro | **Agente** | idle breathing, flotantes, giros, pistones por fórmula (§2) + Cycles modifier |
| Bake + export batch | **Agente** | hornear IK/constraints, exportar N clips FBX/glTF con settings idénticos (§6, §9) |
| Verificación estructural | **Agente** | nº keys, rango, fps, `evaluate`, render de frames clave (§8) |
| Pulido expresivo | **Humano/artista** | arcos, timing, contactos de pies, acting, corrección de mocap crudo |
| Juicio final | **Humano** | ¿se siente bien el movimiento? (el render de frames ayuda pero no decide) |

El agente **nunca** declara "animación lista" por calidad — solo declara "andamiaje montado y verificado estructuralmente" con evidencia numérica + render, y entrega para pulido. La calidad la firma un ojo.

---

## Reglas practicas

1. Antes de tocar nada: ¿la Action es `is_action_layered`? En 5.2 lo normal es SÍ; snippets con `action.fcurves` están rotos — usa el channelbag del slot.
2. F-Curves se leen SIEMPRE vía `anim_utils.action_ensure_channelbag_for_slot(action, slot).fcurves`, nunca `action.fcurves`.
3. Keyframe por código: `obj.keyframe_insert(data_path, index=, frame=)`; para huesos, sobre el `pose_bone`, no escribas el data_path a mano.
4. `options` de keyframe_insert solo admite {NEEDED, VISUAL, REPLACE, AVAILABLE, CYCLE_AWARE}; `INSERTKEY_XYZ_TO_RGB` ya no existe.
5. Procedural (idle/bob/giro/pistón) por fórmula + Cycles F-modifier; acting/locomoción con peso → mocap + humano, no código.
6. Fija `scene.render.fps` y el rango de escena al del clip ANTES de exportar; el default 24 rara vez es lo que quiere Unity.
7. `use_fake_user = True` en toda Action a conservar/exportar, o se pierde al recargar.
8. Bake TODA animación derivada (IK, constraints, drivers, NLA, F-modifiers) antes de exportar; Unity solo entiende curvas por hueso.
9. Bake robusto en headless/MCP: `anim_utils.bake_action` (helper Python), no el operador `nla.bake` que pide contexto de área.
10. Operadores del Graph Editor (`graph.clean/decimate/euler_filter`) exigen área: `temp_override` o evítalos vía bake.
11. FBX a Unity: `add_leaf_bones=False`, `bake_anim=True`, `bake_anim_use_all_actions=False` para 1 clip por archivo, `bake_anim_force_startend_keying=True`.
12. Un clip por archivo con patrón `hero@walk.fbx`; Unity los agrupa en `hero.fbx` solo.
13. Comparte Avatar entre archivos de clip con *Copy From Other Avatar* + Source (no regeneres avatar por clip).
14. Verifica cada clip con números (keys, rango, fps, `evaluate`) + render de 3-5 frames clave; "corrió sin error" NO es evidencia.
15. El agente entrega "andamiaje verificado", nunca "animación de calidad lista": el pulido expresivo y el visto bueno son del humano.
16. Modo OBJECT + escala aplicada antes de cualquier export [ver: blender/bpy-scripting].
17. Cualquier snippet de animación anterior a Blender 4.4 se asume roto (cambió el sistema de acciones) hasta probarlo en 5.2.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| `action.fcurves` / `action.groups` / `action.id_root` lanzan AttributeError | Eliminados en 5.x: fcurves viven en `channelbag` por slot; usa `anim_utils.action_ensure_channelbag_for_slot` |
| Script pre-4.4 "no encuentra" las curvas de una acción | Slotted Actions: recórrelas por `action.layers[].strips[].channelbags[].fcurves`, o por el helper del slot |
| `keyframe_insert(..., options={'INSERTKEY_XYZ_TO_RGB'})` falla | Enum recortado en 5.2; usa solo {NEEDED, VISUAL, REPLACE, AVAILABLE, CYCLE_AWARE} |
| Clip exportado a Unity "no mueve" nada / mueve raro | Faltó bake: IK/constraints/drivers/NLA no viajan; hornea a keyframes antes |
| Huesos "_end" basura en el avatar de Unity | `add_leaf_bones=False` en el export FBX |
| Todas las animaciones caen en un solo clip enorme en Unity | `bake_anim_use_all_actions=False` (1 clip/archivo) o divide por Start/End en el Model Importer |
| Personaje 100× o 0.01× de tamaño / gira 90° | Escala sin aplicar y ejes; aplica transform y respeta `primary/secondary_bone_axis` |
| Animación va a otra velocidad en Unity | fps de escena Blender ≠ fps del proyecto Unity; fíjalos iguales antes de exportar |
| Action desaparece tras guardar/recargar | Sin usuario y sin `use_fake_user`; márcalo True |
| `graph.decimate`/`euler_filter` da "context is incorrect" en headless | Operador de área: `temp_override(area=VIEW/GRAPH)` o hornea/limpia con `clean_curves` del bake |
| Gimbal flips feos en rotación de mocap | `bpy.ops.graph.euler_filter` sobre las curvas Euler, o keyea en quaternion |
| Declarar "animación lista" porque el bake corrió | El bake solo garantiza keyframes; la calidad la juzga un ojo (render de frames + humano) |
| Confundir `object.bake` con hornear animación | `object.bake` es render bake de texturas; animación es `nla.bake` / `anim_utils.bake_action` |
| Retarget de Mixamo sin renombrar `mixamorig:` | Renombra huesos/Actions y aplica escala 0.01 antes de hornear |

## Fuentes

- **Blender 5.2.0 LTS (binario real, Homebrew build 2026-07-14)** — introspección RNA + pruebas funcionales headless en esta sesión: estructura de Slotted Actions (`Action.is_action_legacy/is_action_layered/slots/layers`, `ActionSlot`, `ActionLayer`, `ActionKeyframeStrip.channelbags`, `ActionChannelbag.fcurves`, `AnimData.action_slot`); `keyframe_insert` opciones válidas; `bpy.ops.nla.bake` params exactos; `anim_utils.bake_action`/`BakeOptions`/`action_ensure_channelbag_for_slot`; enums de `Keyframe.interpolation/easing`, `FCurve.extrapolation`, `FModifier.type`, `FModifierCycles`; `graph.clean/decimate/euler_filter`; params de `export_scene.fbx` (bake_anim*, add_leaf_bones, ejes) y `export_scene.gltf` (export_animations, export_animation_mode, …); export FBX real de clip (archivo no vacío).
- **Blender 4.4 Release Notes — Animation (Slotted Actions / "Baklava")** — developer.blender.org/docs/release_notes/4.4 — introducción del sistema de acciones con slots y layers (contexto de versión; el estado real en 5.2 se verificó contra el binario porque docs.blender.org bloqueó el fetch directo).
- **Unity 6 Manual — Splitting animations** (`Splittinganimations.html`, docs.unity3d.com/6000.2) — convención `model@animation.fbx`, agrupación automática en el archivo base, lista de Clips con Start/End, Preserve Hierarchy.
- **Unity 6 Manual — Animation tab / AnimationClip import** (`class-AnimationClip.html`) — Loop Time, Loop Pose, Cycle Offset, Root Transform Rotation/Position(Y)/Position(XZ) con Bake Into Pose + Based Upon, Mask/Curves/Events.
- **Unity 6 Manual — Configuring the Avatar / Rig tab** (`ConfiguringtheAvatar.html`) — Animation Type (Humanoid/Generic/Legacy), Avatar Definition (Create From This Model / Copy From Other Avatar + Source), Configure, retargeting humanoide, ≥15 huesos.
- **Base sintetizada — `blender/bpy-scripting.md`** — modelo bpy.data/ops/context, headless flags, export batch por colección, gotcha de `export_apply` con shape keys, cambios 5.x que rompen scripts (acciones → slots + channelbag), `view_layer.update`, modo OBJECT antes de exportar.
- **Base sintetizada — `blender/blender-mcp-operativo.md`** — render Workbench/EEVEE a PNG como evidencia visual, `media_type` antes de `file_format`, id `BLENDER_EEVEE` (no `_NEXT`), `print()` como único canal en `execute_blender_code`, trocear por timeout de 180 s, screenshot antes/después.
- **Base ojeada — `unity/animacion-unity.md`** — destino de los clips exportados: Animator Controller, blend trees, humanoid vs generic, StringToHash, Animation Events (no repetido aquí).
