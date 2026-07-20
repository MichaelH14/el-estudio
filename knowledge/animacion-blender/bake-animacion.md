# Hornear animación: constraints, IK, físicas y drivers → keyframes

> **Cuando cargar este archivo:** justo antes de exportar a Unity cualquier animación de Blender 5.2 que NO esté ya en keyframes puros — es decir, casi todas: brazos/piernas movidos por IK, huesos movidos por constraints (Copy Rotation, Damped Track, Child Of), ruedas/paneles movidos por drivers, o secundario simulado (cloth, soft body, rigid body, spring/jiggle bones). Aquí va el **COMO en Blender** de convertir todo eso a F-Curves reales sobre los deform bones, verificarlo y sacar el clip limpio. La TÉCNICA (qué es un buen ciclo, timing, cuánto arrastre) vive en [ver: animacion3d/keyframes-curvas], [ver: animacion3d/movimiento-secundario] y [ver: animacion3d/ciclos-locomocion] — **no se repite**. El armado del rig de control y el bake control→deform conceptual está en [ver: rigging/ik-fk-constraints]; el handoff final (Avatar, `@anim`, root motion) en [ver: rigging/rig-a-unity] y [ver: export-clips-unity]. El formato de acciones/slots en [ver: sistema-animacion] y [ver: actions-organizacion]; la limpieza de curvas en [ver: graph-editor].

Versión: **Blender 5.2 LTS** (docs.blender.org/manual/en/latest = 5.2 LTS a jul-2026; **el sistema de acciones ya es el "slotted"/Baklava** de 4.4+, §2 — no el de una-acción-un-datablock viejo) + **Unity 6**. Firmas `bpy` y defaults verificados contra la **Python API 5.2 real** (jul-2026): valores por defecto tomados de la página de la API, marcados donde el default "en bruto" de la clase no es el útil.

---

## 1. Por qué se hornea: Unity solo lee keyframes por hueso

Unity **no tiene el runtime de Blender**. Su Animator reproduce clips que son, literalmente, **curvas de transform (loc/rot/scale) por hueso y por blend shape**. Nada más. Todo lo que en Blender *calcula* la pose en vez de *almacenarla* como key desaparece al exportar:

| Lo que produce la pose en Blender | ¿Unity lo evalúa? | Qué hay que hacer |
|---|---|---|
| **Keyframes / F-Curves** sobre loc/rot/scale de un hueso | **Sí** — es lo único que lee | Exportar tal cual |
| **IK constraint** (goal + pole resuelven ángulos) | **No** | Hornear el resultado a los deform bones (§5) |
| **Bone constraints** (Copy Rotation/Location, Damped Track, Child Of, Limit…) | **No** | Hornear con **Visual Keying** (§3) |
| **Drivers** (rueda por velocidad, shape key por ángulo) | **No** — Unity no tiene drivers | Hornear el valor manejado; algunos se **re-hacen en Unity** (§7) |
| **Rigid body / cloth / soft body** (simulación) | **No** | Bake a keyframes (rigid body) o a vertex-anim/bones (cloth/soft, §6) |
| **Spring/jiggle bones** movidos por addon/sim | **No** (esos huesos llegan quietos) | Bake de esos huesos con Visual Keying, **o** re-simular en Unity (§6) |
| **Shape keys manejadas por driver** (corrective por ángulo) | El driver **no** exporta nunca; los shapes en sí **⚠️ NO VERIFICADO en FBX Legacy** (§8, nota shape keys) | Hornear la influencia, o re-crear la lógica en Unity (§7) |
| **Armature modifier Preserve Volume** (dual-quaternion) | **No** existe en engines | Desactivarlo; ver la deformación real [ver: rigging/deformacion] |

**La frase base:** el FBX **no guarda constraints ni drivers** — "*The result of using constraints is exported as a keyframe animation however the constraints themselves are not saved in the FBX*" (doc FBX add-on 5.2, sección Missing, verbatim). Hornear es **convertir ese resultado procedural en keys explícitos, controlados y verificables** antes de que el exporter lo haga a su manera (§8).

---

## 2. El sistema de acciones en 5.2 (slotted / Baklava): lo que importa para el bake

En 5.2 una **Action** ya no anima un solo data-block: contiene **Slots**, y un data-block declara *acción + slot* (verificado, manual 5.2 "Actions"). Consecuencias para hornear y scriptear:

| Hecho (manual 5.2) | Implicación al hornear |
|---|---|
| La Action es el **contenedor** de animación; el objeto la "usa" como una malla usa un material | El bake escribe una Action; se puede duplicar/linkear/exportar como clip [ver: actions-organizacion] |
| Cada Action tiene **≥1 Slot**; un data-block usa *acción+slot* | Un solo clip de personaje suele ser 1 acción / 1 slot para el armature |
| Un slot puede almacenar animación de **varios data-blocks** (ej. 100 pelotas → 1 acción con 100 slots) | Útil al hornear muchas sims a una acción; para export a Unity casi siempre quieres **1 armature = 1 slot = 1 clip** |
| Internamente hay **layers y strips**: **NO expuestos en la UI**, "*safely ignore it for now*", **pero SÍ en la Python API** | Al scriptear bake/duplicado hay que ir por la API de slots/layers, no asumir el modelo viejo `object.animation_data.action` = una curva plana [ver: sistema-animacion] |

`bpy.ops.nla.bake` (§3) **sigue funcionando** en este modelo: crea/usa una acción y su slot. Detalle del NLA (combinar strips antes de hornear un clip único) en [ver: nla-editor].

---

## 3. Bake Action: el operador central (`nla.bake`)

**UI:** `Object ▸ Animation ▸ Bake Action…` (Object Mode) o `Pose ▸ Animation ▸ Bake Action…` (Pose Mode). Ambos llaman a **`bpy.ops.nla.bake`** (`startup/bl_operators/anim.py`). Firma y **defaults reales verificados (API 5.2)**:

```python
bpy.ops.nla.bake(
    frame_start=1, frame_end=250, step=1,
    only_selected=True,          # Pose: solo huesos seleccionados
    visual_keying=False,         # ← por defecto OFF; ENCENDER para constraints/IK
    clear_constraints=False,     # ← quita constraints tras hornear
    clear_parents=False,         # solo objetos
    use_current_action=False,    # "Overwrite Current Action"
    clean_curves=False,          # borra keys redundantes tras hornear
    bake_types={'POSE'},         # {'POSE'} y/o {'OBJECT'}
    channel_types={'LOCATION','ROTATION','SCALE','BBONE','PROPS'},
)
```

| UI | `bpy` | Qué hace / cuándo |
|---|---|---|
| **Frame Start / End** | `frame_start` / `frame_end` | Rango a hornear. Igualarlo al rango real del clip (no dejar el 250 default) |
| **Frame Step** | `step` | Cada cuántos frames pone key. **1 = key por frame** (fidelidad máxima, clip pesado, §9). >1 aligera pero puede perder detalle rápido |
| **Only Selected Bones** | `only_selected` | Solo huesos seleccionados (Pose). **Selecciona SOLO los `DEF_`** antes de hornear (§5) |
| **Visual Keying** | `visual_keying` | **"Keyframe from the final transformations (with constraints applied)"** — la clave: hornea el resultado de IK/constraints, no los valores base. **Sin esto, un hueso movido por constraint se hornea en su transform base (0,0,0)** |
| **Clear Constraints** | `clear_constraints` | Quita todos los constraints del hueso/objeto horneado. La doc avisa: "*To get a correct bake with this setting Visual Keying should be enabled*" → **nunca `clear_constraints=True` sin `visual_keying=True`** o el hueso salta a su base |
| **Clear Parents** | `clear_parents` | Solo objetos: hornea y desparenta |
| **Overwrite Current Action** | `use_current_action` | Hornea sobre la acción actual en vez de crear una nueva (útil para hornear solo parte de los huesos por lotes). Para el flujo seguro se prefiere crear acción nueva (§4) |
| **Clean Curves** | `clean_curves` | Tras hornear, borra keys redundantes (equivale al `graph.clean`, §9). Reduce peso; **cambia la forma de la curva** — verificar (§8) |
| **Bake Data** | `bake_types` | `{'POSE'}` (huesos), `{'OBJECT'}` (transform del objeto) o ambos |
| **Channels** | `channel_types` | Qué canales: LOCATION/ROTATION/SCALE/BBONE/PROPS. Quitar SCALE si no animas escala (las **curvas de escala son las más caras** en Unity [ver: unity/animacion-unity]) |

> **Gotcha headless/MCP:** `nla.bake` depende de contexto (área, selección, modo, frame range de escena). En scripts, setear `bpy.context.scene.frame_start/end`, entrar a Pose Mode, seleccionar los huesos correctos y, si falla el contexto, envolver con `context.temp_override(...)`. La selección la haces con `pose_bone.bone.select = True` sobre `armature.data.bones`, no sobre el pose bone.

---

## 4. El flujo seguro: duplicar la acción, hornear la copia, exportar la horneada

`clear_constraints=True` es **destructivo** — borra el rig de control del hueso. **Nunca hornees sobre el único ejemplar de tu animación.** Patrón:

1. Termina la animación con el rig de control completo (IK/FK switch, poles, custom shapes) [ver: rigging/ik-fk-constraints].
2. **Duplica la acción** (o guarda un `.blend` aparte / trabaja en una copia del objeto). La copia es la que se hornea y exporta; el original con controles se conserva.
3. Selecciona **solo los `DEF_`** en Pose Mode.
4. Bake Action con **`visual_keying=True`** (+ `clear_constraints=True` si quieres keys limpios sin el stack).
5. Limita weights a 4/vértice y exporta Only Deform Bones (§8).

```python
import bpy
arm = bpy.data.objects["Armature"]
ad  = arm.animation_data

# 2) duplicar la acción (el datablock) para no destruir el original
src = ad.action
dup = src.copy()                 # nuevo datablock "<nombre>.001"
dup.name = src.name + "_BAKED"
ad.action = dup                  # (en 5.2 recordar: la asignación arrastra su slot)

# 3) seleccionar SOLO los deform bones
bpy.ops.object.mode_set(mode='POSE')
for b in arm.data.bones:
    b.select = b.use_deform      # DEF=True → seleccionado

# 4) hornear el resultado de constraints/IK sobre esos huesos
sc = bpy.context.scene
bpy.ops.nla.bake(
    frame_start=sc.frame_start, frame_end=sc.frame_end, step=1,
    only_selected=True, visual_keying=True, clear_constraints=True,
    bake_types={'POSE'}, channel_types={'LOCATION','ROTATION'},  # sin SCALE si no aplica
)
```

Regla dura: **el rig de control jamás se destruye** — se hornea una *copia*. Si algo salió mal, vuelves al original con controles y re-horneas.

---

## 5. Hornear IK → FK (control → deform)

La mecánica del rig (tres cadenas FK/IK/DEF, el IK/FK switch, por qué solo los DEF se exportan) está en [ver: rigging/ik-fk-constraints §4,§8] — **no se repite**. Aquí, lo operativo del bake:

- El IK/FK switch y los controles **producen** la pose; los `DEF_` la reciben vía Copy Rotation/Copy Transforms + drivers de influencia. Esos DEF **no tienen keys propios** hasta que horneas.
- `visual_keying=True` captura la transform final de cada DEF (ya resuelto el IK, ya mezclado el switch) → keys reales.
- Si dejas `clear_constraints=False`, los DEF quedan con keys **y** los constraints encima (doble control) — para export limpio usa `clear_constraints=True` para que el DEF sea puro keyframe.
- **Nunca** exportes Only Deform Bones con la animación viviendo en los controles y los DEF sin hornear: el exporter descarta los controles (los que se movían) y los DEF llegan quietos → "personaje en T-pose inmóvil en Unity". Ese es el fallo #1 y su antídoto es este bake.

---

## 6. Hornear simulaciones (cloth, soft body, rigid body, spring/jiggle)

El criterio *simular-vs-hornear* y el presupuesto móvil ya están en [ver: animacion3d/movimiento-secundario §7]. Aquí, **por dónde sale cada simulación a keyframes**, porque **no todas se hornean igual** — es el punto que más confunde:

| Simulación | ¿Hay "bake to keyframes"? | Operador / salida | Para exportar a Unity |
|---|---|---|---|
| **Rigid Body** (objeto rígido: caja que cae, engranaje-como-objeto, prop) | **Sí, directo** | `Object ▸ Rigid Body ▸ Bake To Keyframes` = `bpy.ops.rigidbody.bake_to_keyframes(frame_start, frame_end, step)` → **keys de transform del objeto** | Sale como animación de objeto/transform normal |
| **Cloth** (capa, tela por vértice sobre malla) | **NO a keyframes** | Solo **caché** (ptcache): `Bake` en el panel Cache. Es datos de vértice en `.bphys`/memoria, **no F-Curves** | La sim es **vertex animation, no esqueletal**: (a) riguear la tela con una **rejilla de huesos** y BoneCloth, luego hornear esos huesos como spring bones; o (b) exportar vertex-anim por **Alembic** (`wm.alembic_export`) / MDD y usar shader de vertex-anim en Unity — Unity no la lee como clip de huesos [ver: animacion3d/movimiento-secundario §6] |
| **Soft Body** | **NO a keyframes** | Solo caché (ptcache), igual que cloth | Igual que cloth: bones+bake, o Alembic vertex-anim |
| **Spring/Jiggle bones** (pelo/cola movidos por addon Wiggle/Spring, o por constraints físicos) | Indirecto | Esos huesos **se transforman** cada frame → hornéalos con **`nla.bake` `visual_keying=True`** sobre esa collection de huesos | Sale como keys de esos deform bones. **Alternativa recomendada:** NO hornear y re-simular en Unity (Dynamic Bone/Magica) si debe reaccionar a movimiento impredecible [ver: animacion3d/movimiento-secundario §7] |
| **Particles / fluidos** | — | FBX **no soporta** animación de fluido (doc FBX 5.2, Missing). Fuera de scope para clips de personaje | No aplica a skeletal |

Notas de la caché de física (manual 5.2 "Baking Physics Simulations"):
- El resultado se **cachea a memoria** al reproducir; **Bake** protege la caché (no puedes cambiar settings hasta **Delete Bake**). **Hay que estar en Object Mode para hornear.**
- La sim solo se calcula entre **Start/End del panel Cache** — súbelos si tu clip dura más que el rango default.
- **Cloth/soft body NUNCA producen keyframes de hueso.** Si necesitas tela como clip esqueletal en Unity, es **bones + bake**, no la sim por vértice.

```python
# Rigid body de un prop/engranaje-objeto → keys de transform
bpy.ops.object.select_all(action='DESELECT')
bpy.data.objects["Gear"].select_set(True)
bpy.context.view_layer.objects.active = bpy.data.objects["Gear"]
bpy.ops.rigidbody.bake_to_keyframes(frame_start=1, frame_end=120, step=1)
```

---

## 7. Hornear drivers: qué se hornea y qué se re-hace en Unity

Un **driver** maneja una propiedad con una función/expresión (manual 5.2: típico para bone transforms, influencia de shape keys, constraints, modificadores, con custom properties de entrada). **Unity no tiene drivers.** Dos destinos distintos:

| Caso de driver | ¿Se puede hornear? | Qué se hace |
|---|---|---|
| **Rueda que rota** por driver ligado a distancia/velocidad | Sí, a keys **para un clip fijo** | Bake la rotación del hueso/objeto rueda (`nla.bake` o `bake_to_keyframes`) para ese clip. **Pero si la rueda debe girar según la velocidad real en juego → NO hornear: re-hacer en Unity** (script que rota por `speed`) — un clip horneado gira siempre igual |
| **Corrective / pose-driven shape key** (influencia por ángulo de codo/hombro) | El **driver (ángulo→influencia) NUNCA exporta**; que el **shape key en sí llegue como blend shape vía FBX Legacy es ⚠️ NO VERIFICADO** — el manual 5.2 lista "Vertex shape keys" en el **Missing** del exportador (§8) | Opciones: (a) hornear la *influencia* del shape key a keys para clips concretos y **probar el export real** antes de asumir que el shape llegó; (b) si no llega, exportar ese mesh por **glTF** (`export_scene.gltf`, sí soporta morph targets) en vez de FBX Legacy; (c) aceptar la pérdida y re-crear con script/Animation Rigging en Unity. La deformación fina correctiva **no viaja "gratis"** [ver: rigging/deformacion] |
| **Influencia de constraint / IK-FK switch** manejada por driver | Sí | Se resuelve al hornear con `visual_keying=True` (el switch ya está aplicado en la pose horneada, §5) |
| **Propiedad custom** que maneja varios huesos | Sí, si su efecto es transform | Hornear los huesos afectados; la custom property en sí no exporta |

Regla: **hornear = congelar el driver para ESTE clip.** Si la lógica del driver es *reactiva a gameplay* (velocidad, input, ángulo dinámico) se **re-implementa en Unity**; si es *determinista dentro del clip* (un mecanismo que siempre hace lo mismo) se hornea.

---

## 8. Export FBX: el exporter también samplea — por qué el bake explícito manda

El exporter FBX de 5.2 es el **add-on** (`Object ▸ Export ▸ FBX`, `bpy.ops.export_scene.fbx`; el `fbx.html` nuevo es solo el *importer* C++, el export sigue en el add-on). Con `bake_anim=True` **el propio exporter samplea la pose final por frame** — incluidos constraints. Entonces, ¿para qué el Bake Action explícito del §3–5? Porque:

1. **Only Deform Bones descarta los huesos animados si la animación vive en los controles.** El exporter samplea, sí, pero si exportas `use_armature_deform_only=True` y no horneaste control→DEF, los huesos que se movían (controles) se van y los DEF quedan planos. **El bake explícito pasa el movimiento a los DEF primero.**
2. **Control del muestreo y reducción de keys** (step, decimate, §9) — el bake del exporter es opaco.
3. **Verificación** (§8b): puedes ver la acción horneada en Blender antes de exportar; el sampling del exporter no lo revisas.
4. **Simulaciones**: el `bake_anim` del exporter **no** captura cloth/soft body/rigid body como esqueletal — esos van por §6 aparte.

Parámetros de animación/armature verificados (`export_scene.fbx`, API 5.2, defaults reales):

| UI | `bpy` | Default | Nota game-ready |
|---|---|---|---|
| **Baked Animation** | `bake_anim` | `True` | Deja ON |
| **Key All Bones** | `bake_anim_use_all_bones` | `True` | Fuerza ≥1 key en todos los huesos (algunos targets lo exigen) |
| **NLA Strips** | `bake_anim_use_nla_strips` | `True` | Cada strip → un AnimStack. Combina en NLA si haces multi-clip [ver: nla-editor] |
| **All Actions** | `bake_anim_use_all_actions` | `True` | Exporta **cada acción** como AnimStack. Para el patrón `@anim` (1 clip por FBX) muchas veces conviene **OFF** para exportar solo la asignada [ver: export-clips-unity] |
| **Force Start/End Keying** | `bake_anim_force_startend_keying` | `True` | Key al inicio y fin de cada acción |
| **Sampling Rate** | `bake_anim_step` | `1.0` | Cada cuántos frames evalúa (0.01–100) |
| **Simplify** | `bake_anim_simplify_factor` | `1.0` | Reduce keys (0 = desactivado; más alto = más simplificado). Reducción del exporter, complementa el decimate (§9) |
| **Add Leaf Bones** | `add_leaf_bones` | `True` | **PONER OFF** (`False`) o salen huesos `_end` basura por todo el esqueleto en Unity |
| **Only Deform Bones** | `use_armature_deform_only` | `False` | **PONER ON** (`True`): solo huesos deform (+ no-deform con hijos deform) → tira controles/MCH |
| **Primary/Secondary Bone Axis** | `primary_bone_axis`/`secondary_bone_axis` | `'Y'` / `'X'` | Dejar salvo problema de orientación en el target |
| **Apply Scalings** | `apply_scale_options` | `'FBX_SCALE_NONE'` | Con Unit Scale=1 en Blender no da problemas; para Unity, FBX_SCALE_ALL o Apply Transform con cuidado [ver: blender/import-export] |
| **Apply Transform** | `bake_space_transform` | `False` | **DEJAR OFF**: "*known to be broken with armatures/animations*" (warning oficial) — rompe rigs animados |
| **Apply Modifiers** | `use_mesh_modifiers` | `True` | ⚠️ "*prevents exporting shape keys*" (docstring API): si exportas blend shapes (facial/corrective), **desactívalo** para esa malla — necesario, pero **el manual dice que puede no ser suficiente** (nota debajo) |
| Forward / Up | `axis_forward` / `axis_up` | `'-Z'` / `'Y'` | Convención Unity; validar contra rotación import [ver: unity/animacion-unity] |

> **⚠️ Contradicción documentada en la doc 5.2 — shape keys en FBX Legacy (verificar antes de confiar):** el docstring del operador dice que `use_mesh_modifiers=True` "*prevents exporting shape keys*" (implica que con `False` sí exportan). Pero el manual, sección **Export ▸ Missing** de la página FBX (Legacy) (`files/import_export/fbx_legacy.html`), dice **verbatim**: "*Vertex shape keys – FBX supports them but this exporter does not write them yet.*" Dos fuentes oficiales de la misma doc 5.2 que se contradicen. Antes de depender de este camino para facial/corrective: **desactiva `use_mesh_modifiers` en esa malla Y haz un export de prueba real** con al menos un shape key para confirmar en Unity si llegó. Si no llega, exporta ese mesh por **glTF** (`bpy.ops.export_scene.gltf`, morph targets documentados) en vez de FBX Legacy. NO asumas "Apply Modifiers OFF" = shape keys exportados sin haberlo visto en el Animator de Unity.

```python
bpy.ops.export_scene.fbx(
    filepath="/out/Hero@run.fbx",
    use_selection=True, object_types={'ARMATURE','MESH'},
    add_leaf_bones=False,            # sin huesos _end
    use_armature_deform_only=True,   # solo DEF (tras hornear control→DEF)
    bake_anim=True, bake_anim_step=1.0,
    bake_anim_use_all_actions=False, # solo la acción asignada → 1 clip
    bake_space_transform=False,      # NUNCA True con armature animado
    axis_forward='-Z', axis_up='Y',
)
```

Los ajustes del lado Unity (Strip Bones, Optimize Game Object, Skin Weights Standard=4, Avatar) están en [ver: rigging/ik-fk-constraints §7] y [ver: rigging/rig-a-unity] — no se repiten.

### 8b. Verificar el bake antes de exportar

**Regla: la acción horneada tiene que verse idéntica a la original con el rig de control.** Método operativo:

1. Con el original (controles) en una capa/acción y la horneada en otra, **reproduce ambas** en el mismo rango y compara la silueta y los contactos (pies plantados, mano en el arma). Si el pie patina o el codo flipa → el bake perdió el IK/pole (revisar `visual_keying`).
2. Chequea en el **Graph Editor** que los DEF tienen curvas reales (no planas) en el rango [ver: graph-editor].
3. Si horneaste con `clear_constraints=True`, confirma que **no quedan constraints** en los DEF (`pose_bone.constraints` vacío) y que aun así se mueven.
4. El primer frame del loop debe casar con el último (o el clip salta al reiniciar) [ver: animacion3d/ciclos-locomocion].
5. "Listo" **no** es "el bake corrió sin error": es **haber visto la horneada moverse igual que la original** y, idealmente, deformando en Unity [ver: rigging/rig-a-unity].
6. Si el mesh lleva **shape keys/blend shapes** (facial, corrective): verifica ADEMÁS que llegaron al FBX abriendo el asset en Unity y viendo la lista de Blend Shapes del SkinnedMeshRenderer — la doc 5.2 misma se contradice sobre si el exporter FBX Legacy los escribe (nota en §8); no lo asumas por el nombre del setting.

---

## 9. El coste del bake y la reducción de keyframes

`step=1` pone **una key por frame en cada hueso** → un clip de 60 f con 40 DEF = miles de keys. Pesa en memoria de clip y en tiempo de evaluación [ver: unity/rendimiento-unity]. Reducir **después** de hornear (verificado, Graph Editor / F-Curves 5.2):

| Herramienta | UI | `bpy` | Qué hace |
|---|---|---|---|
| **Decimate (Ratio)** | `Key ▸ Density ▸ Decimate (Ratio)` | `graph.decimate(mode='RATIO', factor=0.333)` | Borra un % de keys quitando los que menos afectan la forma. `factor` default **0.333** (quita ~⅓) |
| **Decimate (Allowed Change)** | `Key ▸ Density ▸ Decimate (Allowed Change)` | `graph.decimate(mode='ERROR', remove_error_margin=…)` | Borra el máximo de keys manteniendo la desviación bajo un margen — **el más seguro** para no romper la curva |
| **Clean Keyframes** | `Key ▸ Density ▸ Clean Keyframes` (`X`) | `graph.clean(threshold=0.001, channels=False)` | Quita keys redundantes (mismo valor que los vecinos). Ideal tras hornear todos los huesos: borra keys inútiles en los que no se movieron. **Cambia la forma** → úsalo con criterio |
| **Bake Keyframes** | `Key ▸ Density ▸ Bake Keyframes` (`Shift Alt O`) | `graph.bake_keys()` | Lo contrario: key en cada frame entre los seleccionados (densificar, raro tras un bake) |
| **Samples → Keys** | — | `graph.samples_to_keys()` | Convierte curvas *sampleadas* en keyframes editables |
| En el propio bake | `Clean Curves` | `nla.bake(clean_curves=True)` | Reducción integrada al hornear (equivale a un clean posterior) |
| En el export | `Simplify` | `export_scene.fbx(bake_anim_simplify_factor=…)` | Reducción del exporter, última pasada |

Estrategia: hornear a `step=1` (fidelidad), luego **Decimate (Allowed Change)** o **Clean** hasta que el clip aligere **sin que se note** en reproducción, y dejar el `Simplify` del exporter como red final. **Verifica la reproducción tras reducir** — cada reducción cambia la curva. Evita hornear/keyframear **escala** salvo necesidad: las curvas de escala son las más caras en Unity [ver: unity/animacion-unity].

---

## Reglas prácticas

1. Todo lo procedural (IK, constraints, drivers, sim) se **hornea a keys sobre los `DEF_`** antes de exportar — Unity no evalúa nada de eso.
2. **Duplica la acción / trabaja en copia**: `clear_constraints=True` es destructivo; el rig de control jamás se hornea sobre su único ejemplar.
3. `Bake Action` con **`visual_keying=True`** siempre que haya constraints/IK: sin él, el hueso se hornea en su transform base (0,0,0).
4. **Nunca `clear_constraints=True` sin `visual_keying=True`** (aviso oficial) — el hueso saltaría a su base.
5. Selecciona **solo los `DEF_`** antes de hornear (`only_selected=True`); marca la selección en `armature.data.bones[...].select`, no en el pose bone.
6. Iguala **Frame Start/End** al rango real del clip; no dejes el 250 default.
7. **Rigid body** → `rigidbody.bake_to_keyframes` (keys de objeto). **Cloth/soft body** NO dan keyframes de hueso: rejilla de huesos + bake, o Alembic vertex-anim.
8. **Spring/jiggle bones**: hornéalos con `visual_keying=True`, **o** re-simúlalos en Unity si deben reaccionar a gameplay impredecible [ver: animacion3d/movimiento-secundario].
9. **Drivers**: hornea si son deterministas dentro del clip; **re-haz en Unity** si son reactivos (rueda por velocidad, corrective por ángulo).
10. Export FBX: **Add Leaf Bones OFF** (`add_leaf_bones=False`) + **Only Deform Bones ON** (`use_armature_deform_only=True`).
11. **`bake_space_transform=False` siempre** con armature animado (roto con armatures/animaciones, warning oficial).
12. Si exportas blend shapes (facial/corrective) por FBX Legacy, **desactiva Apply Modifiers** en esa malla (`use_mesh_modifiers=False`) — es necesario, pero el manual 5.2 dice que este exporter "*does not write [vertex shape keys] yet*" (contradice el docstring del operador): **haz un export de prueba y verifica el shape en Unity**; si no llega, usa glTF (`export_scene.gltf`) para ese mesh.
13. Para el patrón `@anim` de un clip por FBX, considera **All Actions OFF** y exportar solo la acción asignada [ver: export-clips-unity].
14. **Verifica el bake**: la horneada debe reproducirse **idéntica** a la original antes de exportar; contactos y pies plantados intactos.
15. Reduce keys tras hornear: **Decimate (Allowed Change)** o **Clean Keyframes**, y reproduce de nuevo para confirmar que no se rompió.
16. Evita hornear **escala** si no la animas (`channel_types` sin SCALE); curvas de escala = las más caras.
17. Loop: el último frame debe casar con el primero antes de hornear/exportar.
18. En 5.2, al scriptear el bake recuerda el modelo **slotted** (acción+slot; layers/strips solo en Python API) — no asumas el modelo de acción viejo [ver: sistema-animacion].
19. "Bake OK" = **visto moverse igual y, si es posible, deformando en Unity**, no "el operador no dio error".

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Personaje llega a Unity en T-pose inmóvil pese a tener animación | Los DEF los movían constraints/controles, no keys: **Bake Action `visual_keying=True` control→DEF** antes de exportar |
| Horneaste, pero el hueso saltó a (0,0,0) / perdió el IK | Faltó `visual_keying=True` (o pusiste `clear_constraints` sin él): re-hornea con visual keying encendido |
| Horneaste sobre la única acción y perdiste el rig de control | Siempre **duplicar la acción / .blend** antes; el bake con clear_constraints es destructivo |
| Exportas Only Deform Bones y no se mueve nada | La animación vivía en los controles (que el export descarta) y los DEF sin hornear: **hornea a los DEF primero** |
| Cloth/soft body "no se exporta" a Unity como animación | No producen keyframes de hueso: son vertex-sim → rejilla de huesos+bake, o Alembic/MDD vertex-anim [ver: animacion3d/movimiento-secundario §6] |
| La rueda con driver gira en el clip pero no según la velocidad en juego | Un clip horneado gira siempre igual: **re-hacer el spin en Unity** por script de velocidad |
| Corrective shape por ángulo se ve bien en Blender, se pierde en Unity | El shape exporta pero **el driver no**: hornea la influencia para clips fijos o re-crea la lógica en Unity |
| Clip enorme, memoria/eval alta | `step=1` puso key por frame: **Decimate (Allowed Change) / Clean Keyframes**, Simplify del exporter, quitar SCALE |
| Huesos `_end` basura por todo el esqueleto en Unity | `add_leaf_bones=False` en el export |
| Rig se deforma raro tras exportar | `bake_space_transform=True` roto con armatures: déjalo **False**; apply transforms solo en rest, Object Mode |
| Blend shapes (facial) no salen al FBX | Primero `use_mesh_modifiers=False` en esa malla. Si aun así no llegan: el manual 5.2 lista "Vertex shape keys" como **Missing** en el exportador FBX Legacy (contradice el docstring del operador) — exporta ese mesh por **glTF** (`export_scene.gltf`) en vez de FBX |
| El bake corrió pero el pie patina / el codo flipa | El bake no capturó el IK/pole: revisa `visual_keying=True` y que seleccionaste la cadena correcta; **verifica reproduciendo** |
| Physics "horneada" pero la caché no está protegida y cambia sola | En física es caché (ptcache): pulsa **Bake** (protege) y estás en **Object Mode**; sube Start/End del panel Cache si el clip dura más |
| Script de bake falla en headless | Contexto: setea `scene.frame_start/end`, entra a Pose Mode, selecciona en `data.bones`, usa `temp_override`; recuerda el modelo slotted al tocar la acción |

## Fuentes

- **Blender 5.2 LTS Manual — Actions** (`animation/actions.html`) — VERIFICADO vía curl (2026-07-20): las acciones son el contenedor de animación; **Slots** (acción+slot por data-block; un slot puede animar varios data-blocks; ≥1 slot por acción); nota clave: **layers y strips NO están en la UI ("safely ignore it for now") pero SÍ en la Python API**. Confirma que es el sistema slotted/Baklava (4.4+), no el viejo.
- **Blender 5.2 LTS Manual — Physics ▸ Baking Physics Simulations** (`physics/baking.html`) — VERIFICADO: la sim se **cachea** (ptcache), Bake protege la caché hasta Delete Bake, hay que estar en **Object Mode**, la sim solo corre entre Start/End del panel Cache; Disk Cache `.bphys`. (Cloth/soft body → caché, **no** keyframes.)
- **Blender 5.2 LTS Manual — Rigid Body** (`physics/rigid_body/introduction.html`) — VERIFICADO: menú **Object ▸ Rigid Body**; existe **Bake To Keyframes** (única sim con bake directo a keys de transform).
- **Blender 5.2 LTS Manual — Drivers ▸ Introduction** (`animation/drivers/introduction.html`) — VERIFICADO: driver = función/expresión que controla una propiedad; F-Curve del driver mapea salida→propiedad; usado para bone transforms, influencia de shape keys / action constraints / modificadores, con custom properties de entrada. (Unity no tiene drivers → hornear o re-hacer.)
- **Blender 5.2 LTS Manual — Editors ▸ Graph Editor ▸ F-Curves ▸ Editing** (`editors/graph_editor/fcurves/editing.html`) — VERIFICADO: **Decimate** (Ratio: Remove %; Allowed Change: Max Error Margin), **Clean Keyframes** (`X`, keys redundantes), **Bake Keyframes** (`Shift Alt O`, key por frame).
- **Blender 5.2 LTS Manual — Files ▸ Import/Export ▸ FBX (add-on/legacy)** (`files/import_export/fbx_legacy.html`; el `fbx.html` nuevo — re-verificado hoy vía curl, título "FBX - Blender 5.2 LTS Manual" — es solo el **importer C++** y termina en "*Export ¶ To export FBX files use the FBX Add-on*" con link "Next: FBX (Legacy)", confirmando la URL de la página legacy) — VERIFICADO: sección **Armatures** (Primary/Secondary Bone Axis, Only Deform Bones, Add Leaf Bones), **Bake Animation** (Key All Bones, NLA Strips, All Actions, Force Start/End Keying, Sampling Rate, Simplify) y, verbatim en **Export ▸ Missing**: "*Constraints – The result of using constraints is exported as a keyframe animation however the constraints themselves are not saved in the FBX*"; "*Animated fluid simulation – FBX does not support this kind of animation*"; **y también, mismo bloque**: "*Vertex shape keys – FBX supports them but this exporter does not write them yet*" — esto **contradice** el docstring de `use_mesh_modifiers` en la Python API ("*prevents exporting shape keys*", que implica que sí se exportan si se desactiva). Tratado en el archivo como contradicción documentada sin resolver por test real (§8, checklist #12, pitfall correspondiente) — NO se afirma que los blend shapes salgan del FBX Legacy sin verificarlo en Unity.
- **Blender 5.2 Python API** (`api/current/`) — VERIFICADO vía curl: `bpy.ops.nla.bake` (firma completa y defaults reales: `visual_keying=False`, `clear_constraints=False`, `step=1`, `only_selected=True`, `bake_types={'POSE'}`, `channel_types`; docstring "*correct bake ... Visual Keying should be enabled*"; file `bl_operators/anim.py`); `bpy.ops.rigidbody.bake_to_keyframes(frame_start=1, frame_end=250, step=1)`; `bpy.ops.ptcache.bake(bake)`; `bpy.ops.graph.decimate(mode, factor=0.333, remove_error_margin)`, `graph.clean(threshold=0.001, channels)`, `graph.bake_keys()`, `graph.samples_to_keys()`; `bpy.ops.export_scene.fbx(...)` firma completa (`bake_anim*`, `add_leaf_bones=True`, `use_armature_deform_only=False`, `bake_space_transform=False` "*known to be broken with armatures/animations*", `use_mesh_modifiers=True` "*prevents exporting shape keys*", `axis_forward='-Z'`, `axis_up='Y'`); `wm.alembic_export` (vertex-anim para cloth/soft body).
- **Bases sintetizadas de este repo:** [ver: rigging/ik-fk-constraints §4,§7,§8] (control vs deform, IK/FK switch, bake control→deform, Only Deform Bones/Add Leaf, Strip Bones/Optimize Game Object en Unity, `nla.bake` visual_keying), [ver: animacion3d/movimiento-secundario §6,§7] (cloth vs huesos, baked-vs-runtime, rejilla de huesos + BoneCloth, huesos dinámicos como deform sin keys), [ver: unity/animacion-unity] (Unity reproduce clips de curvas por hueso, coste de curvas de escala, culling). Cruces internos animacion-blender: [ver: sistema-animacion], [ver: actions-organizacion], [ver: nla-editor], [ver: graph-editor], [ver: export-clips-unity], [ver: animacion-blender-operativo]; externos: [ver: rigging/rig-a-unity], [ver: rigging/deformacion], [ver: blender/import-export], [ver: animacion3d/keyframes-curvas], [ver: animacion3d/ciclos-locomocion], [ver: unity/rendimiento-unity], [ver: pipeline/arte-a-unity].
