# El sistema de animación de Blender: keyframes, Actions con slots y el reloj de la escena

> **Cuando cargar este archivo:** al EJECUTAR animación en Blender 5.2 (via MCP o `blender -b`) — insertar/borrar keyframes sobre propiedades, entender el data-block de animación nuevo (Actions con **slots**, el modelo "Baklava" de 4.4+), fijar el frame range y **el frame rate de la escena** antes de animar, posar el rig frame a frame en Pose Mode, mover/copiar keys en el Dope Sheet, y saber qué del árbol de datos sobrevive al hornear y exportar a Unity. Es el mapa del SISTEMA y el keying operativo. La CRAFT de curvas (interpolación, tangentes, spacing, ciclos) NO se repite aquí: vive en [ver: animacion3d/keyframes-curvas]. El detalle profundo de cada subsistema tiene su archivo hermano: [ver: graph-editor], [ver: actions-organizacion], [ver: nla-editor], [ver: bake-animacion], [ver: export-clips-unity], y el bucle MCP/headless en [ver: animacion-blender-operativo]. La herramienta base (modos, unidades, atajos) en [ver: blender/interfaz-flujo]; el rig que animas en [ver: rigging/rigging-en-blender-operativo].

Stack: **Blender 5.2.0 LTS** (operadores, enums y defaults verificados contra el binario local, build 2026-07-14) + **Unity 6**. Todo dato dependiente de versión va marcado.

---

## 1. ⚠️ El cambio grande: Slotted Actions (Baklava), 4.4+

**El sistema de animación cambió en Blender 4.4** y 5.2 ya corre el modelo nuevo ("Baklava"). Casi todo tutorial de 2.8–4.3 describe el sistema viejo (una Action = un plano de F-curves, ligada a un solo objeto). **No lo repliques como si fuera lo actual.** Estado real verificado en 5.2:

| Concepto | Sistema viejo (≤4.3) | Sistema nuevo (4.4+, verificado en 5.2) |
|---|---|---|
| Action | Plano único de F-curves ligado a UN data-block | Contenedor con **Slots** + **Layers**; puede animar **varios data-blocks a la vez** |
| Dónde viven las F-curves | `action.fcurves` (directo) | Dentro de un **Channelbag**, por slot: `strip.channelbag(slot).fcurves`. En una Action nueva `action.fcurves` **no existe** (verificado) |
| Ligar animación a un objeto | `animation_data.action` | `animation_data.action` **+** `animation_data.action_slot` (a qué slot se engancha) |
| Flag de tipo | — | `action.is_action_layered` / `action.is_action_legacy` (verificado) |

- **Slot** (`ActionSlot`): un "canal de destino" dentro de la Action. Su `identifier` lleva prefijo de tipo (`OBCube` = Object "Cube", `OBArmature`). Props verificadas: `.identifier`, `.target_id_type`, `.handle`, `.users`, `.name_display`. Al keyframear un objeto por primera vez, Blender **crea el slot solo** y lo asigna a `animation_data.action_slot`.
- **Layer / Strip**: la Action tiene `layers`; cada layer tiene `strips`; el strip de tipo `KEYFRAME` (`ActionKeyframeStrip`) contiene los channelbags. En 5.2 el caso normal es **una layer, un strip** — el layering de animación es infra a futuro, no un flujo diario todavía.
- **Por qué importa para un agente:** el código viejo `action.fcurves[...]` **peta** en una Action nueva. Para leer/crear F-curves hay que pasar por el channelbag del slot (§9). El keying de alto nivel (`obj.keyframe_insert(...)`) sigue funcionando idéntico y esconde toda esta plomería — úsalo siempre que puedas.
- ⚠️ La *estructura* está verificada en el binario 5.2; el nombre "Baklava" y la historia de migración provienen del proyecto oficial de 4.4 y **no se re-verificaron contra las release notes esta sesión** (blender.org devolvió 403).

---

## 2. El modelo de datos: propiedad → F-curve → Action

Animar es un contrato: **tú fijas valores en frames concretos; Blender interpola el resto** [ver: animacion3d/keyframes-curvas §1]. La cadena de contención en 5.2:

```
Propiedad animable (obj.location.x, pose.bones["Bone"].rotation_euler …)
   └─ F-curve  (una curva 1D por propiedad-eje: data_path + array_index)
        └─ Channelbag  (agrupa las F-curves de UN slot)
             └─ Strip (KEYFRAME) → Layer → Action  (el data-block)
Objeto ── animation_data ── .action  +  .action_slot   (engancha objeto ↔ slot)
```

| Nivel | Qué es | Acceso API (verificado 5.2) |
|---|---|---|
| `AnimData` | El bloque de animación del objeto | `obj.animation_data` (crear: `obj.animation_data_create()`) |
| `Action` | Data-block que agrupa la animación | `obj.animation_data.action` |
| `ActionSlot` | Destino dentro de la Action | `obj.animation_data.action_slot` |
| `Channelbag` | F-curves de ese slot | `strip.channelbag(slot)` o `anim_utils.action_get_channelbag_for_slot(action, slot)` |
| `FCurve` | Curva de una propiedad-eje | `channelbag.fcurves` (`.data_path`, `.array_index`) |
| `Keyframe` | `(frame, valor)` sobre una F-curve | `fcurve.keyframe_points` (`.co`, `.interpolation`, `.handle_left`…) |

- **Un data_path + un array_index = una F-curve.** `location` genera 3 (`location` idx 0/1/2); `rotation_euler` 3; `rotation_quaternion` 4. Un hueso ≈ 9–10 canales; un personaje, cientos [ver: animacion3d/keyframes-curvas §1].
- **Fake user** (`action.use_fake_user = True`): una Action sin usuarios se borra al guardar. Marca fake user o piérdela. Detalle de organización en [ver: actions-organizacion].
- **Rango de la Action**: `action.use_frame_range` + `action.frame_range` / `action.curve_frame_range`; `action.use_cyclic` para loop manual. Verificados como props de la Action.

---

## 3. Insertar keyframes

### Vías de keying (de UI a código)
| Vía | Qué hace | Operador / API (verificado 5.2) |
|---|---|---|
| Tecla **`I`** sobre una propiedad (hover) | Keyframe de **esa** propiedad | `anim.keyframe_insert_button` |
| Tecla **`I`** en el Viewport | Menú "Insert Keyframe" → set (Location, Rotation, LocRotScale…) | `anim.keyframe_insert_menu(type='DEFAULT')` |
| Botón "Insert" con Keying Set activo | Keyframea el set completo | `anim.keyframe_insert` / `anim.keyframe_insert_by_name(type="<set>")` |
| **Por datos** (headless/MCP) | Keyframe de un data_path exacto | `obj.keyframe_insert(data_path, index, frame, group, options)` → `bool` |
| Borrar | Quita la key de esa propiedad/frame | `obj.keyframe_delete(data_path, index, frame)` / `anim.keyframe_delete_v3d` |

```python
import bpy
o = bpy.data.objects["Cube"]
bpy.context.scene.frame_set(1)
o.keyframe_insert(data_path="location", frame=1)                 # 3 F-curves de golpe
o.location.x = 5
o.keyframe_insert(data_path="location", index=0, frame=24)       # solo locX
# opciones verificadas: options={'INSERTKEY_VISUAL'} (hornea el resultado de constraints, §7)
o.keyframe_delete(data_path="location", index=0, frame=1)
```
- La **primera** inserción crea `animation_data`, la Action, el slot y el channelbag automáticamente (verificado). No hay que montar la plomería a mano para keying normal.
- El retorno **`bool`** es tu evidencia: `True` = insertó. En headless, un `keyframe_insert` que devuelve `False` (p.ej. propiedad no animable) es un fallo silencioso — chequéalo [ver: animacion-blender-operativo].

### Keying Sets — keyframear coherente por dominio
Un Keying Set es una lista nombrada de propiedades que se keyean juntas (evita dejar un eje "colgado" [ver: animacion3d/keyframes-curvas §1 estrategia de keying]). Builtins verificados en `scene.keying_sets_all`: **Available, Location, Rotation, Scale, Location & Rotation, Location Rotation & Scale, Location Rotation Scale & Custom Properties, Location & Scale, Rotation & Scale, Delta Location/Rotation/Scale, Visual Location/Rotation/Scale** (y combos), **B-Bone Shape**. Custom sets: `anim.keying_set_add` + `anim.keying_set_path_add`; activar con `anim.keying_set_active_set` o `scene.keying_sets.active`. Detalle en [ver: actions-organizacion].

### Auto Keying — grabar mientras posas
| Ajuste (`scene.tool_settings`) | Default verificado | Qué controla |
|---|---|---|
| `use_keyframe_insert_auto` | `False` | El botón rojo "Auto Keying": cada transform inserta key en el frame actual |
| `auto_keying_mode` | `ADD_REPLACE_KEYS` | `ADD_REPLACE_KEYS` (añade/reemplaza) vs `REPLACE_KEYS` (solo reemplaza) |
| `use_keyframe_insert_keyingset` | `False` | Auto Key usa el Keying Set activo en vez de "solo lo que cambió" |
| `keyframe_type` | `KEYFRAME` | Etiqueta/color de la key: Keyframe, Breakdown, Moving Hold, Extreme, Jitter (mapea a extremes/breakdowns de [ver: animacion3d/keyframes-curvas §1]) |

Preferencias que definen **cómo nace** cada key nueva (`bpy.context.preferences.edit`, defaults verificados):
- `key_insert_channels` = `{'ROTATION','LOCATION','SCALE','CUSTOM_PROPS'}` — qué canales entran en el keying "por defecto".
- `keyframe_new_interpolation_type` = `BEZIER`, `keyframe_new_handle_type` = `AUTO_CLAMPED` — la interpolación/handle con que nace cada key (esto explica el look "auto-clamp" que se come el overshoot [ver: animacion3d/keyframes-curvas §5]; para blocking se cambia a `CONSTANT`).
- `use_keyframe_insert_needed` (solo keyea si el valor cambió), `use_visual_keying` (hornea constraints al keyear).

> ⚠️ **Auto Keying es peligroso en un flujo controlado**: un `G` accidental deja una key basura. Para MCP/headless **no** lo uses — keyea explícito por `keyframe_insert`.

---

## 4. Frame rate y tiempo: fíjalo ANTES de animar

El reloj de la escena decide cuántos frames = un segundo. **Es el ajuste más fácil de olvidar y el que más rompe el export a Unity.**

| Ajuste | API (verificado 5.2) | Default | Nota |
|---|---|---|---|
| **FPS** | `scene.render.fps` (int) | **24** | ⚠️ Default = 24 (cine). Los juegos suelen querer **30 o 60** |
| FPS base | `scene.render.fps_base` (float) | 1.0 | FPS efectivo = `fps / fps_base` (verificado: 24/1.0 = 24). Para 29.97 → fps 30, fps_base 1.001 |
| Frame inicial / final | `scene.frame_start` / `scene.frame_end` | 1 / 250 | El rango que reproduce y que hornea el export |
| Frame actual | `scene.frame_current` / `scene.frame_set(n)` | 1 | `frame_set(n, subframe=0.5)` para sub-frame (verificado) |
| Paso | `scene.frame_step` | 1 | Salto del playback |

```python
sc = bpy.context.scene
sc.render.fps = 30          # el fps del juego, ANTES de poner la primera key
sc.render.fps_base = 1.0
sc.frame_start = 1
sc.frame_end = 60           # 60 frames @30fps = 2.0 s exactos
```

**Por qué fijarlo primero (crítico):**
1. Los keyframes viven en **números de frame enteros**, no en segundos. Un ciclo de 24 frames dura 1 s a 24fps pero **0.8 s a 30fps** — cambiar el fps *después* reinterpreta todo tu timing.
2. Unity **samplea por frame**: el FBX horneado guarda un valor por frame al `fps` de la escena (bake step 1.0, §8), y Unity define los clips por rango de frames. Si el fps de Blender ≠ el que espera tu proyecto, la duración en segundos del clip sale mal aunque los frames coincidan. El detalle de resampleo en el motor está en [ver: animacion3d/keyframes-curvas §9] y [ver: unity/animacion-unity].
3. Trabaja siempre en **frames enteros**; keys en `12.4` ensucian el bake y el retime [ver: animacion3d/keyframes-curvas §3].

---

## 5. Timeline, Dope Sheet y marcadores

Dos editores para el mismo dato de tiempo (el **valor** de las curvas se edita en el Graph Editor → [ver: graph-editor]):

| Editor | Para qué | Operaciones típicas |
|---|---|---|
| **Timeline** | Playback + rango + frame actual + markers | `Spacebar` play/stop, `←/→` frame a frame, `↑/↓` salta entre keys; setear Start/End |
| **Dope Sheet** | El **timing**: cuándo hay keys (diamantes en rejilla) | Mover (`G`), escalar (`S`, retime), duplicar (`Shift+D`), copiar/pegar (`Ctrl+C`/`V`), borrar (`X`) keys y bloques |

- El Dope Sheet es el **editor central del timing**: box-select un bloque de keys y `S` para estirar/comprimir la acción entera sin re-keyear; `G` para desfasar (overlap). La forma de la curva no se toca aquí — eso es Graph Editor.
- **Modos del Dope Sheet**: Dope Sheet (todo), **Action Editor** (una Action/slot — donde se nombran y gestionan las Actions [ver: actions-organizacion]), Grease Pencil, Shape Key Editor.
- **Marcadores** (`scene.timeline_markers`, verificado): puntos nombrados en el tiempo. `new(name, frame=n)`, `remove(m)`, `clear()`. Usos: marcar frames de contacto, inicio/fin de una fase de combate, o **bind a cámara** (`Ctrl+B` sobre un marker liga una cámara — para cinemáticas). Los markers **no** se exportan a Unity como eventos; los Animation Events se ponen del lado Unity [ver: unity/animacion-unity].

```python
sc.timeline_markers.clear()
sc.timeline_markers.new("contact_L", frame=8)
sc.timeline_markers.new("contact_R", frame=20)
```

---

## 6. Pose Mode + animación: posar el rig frame a frame

El flujo pose-a-pose ([ver: animacion3d/keyframes-curvas §6]) se ejecuta en **Pose Mode** sobre el armature [ver: rigging/rigging-en-blender-operativo §4].

- **Un slot por armature, no por hueso** (verificado): keyframear cualquier hueso de `Armature` crea **un** slot `OBArmature`; todas las F-curves de todos los huesos viven en su channelbag, con `data_path` = `pose.bones["Bone"].rotation_euler` (verificado). El objeto Armature es la unidad de animación, no el hueso.
- **Posar por datos** (headless/MCP — NO por operador modal de transform):

```python
import math
bpy.ops.object.mode_set(mode='POSE')
pb = rig.pose.bones["upper_arm.L"]
pb.rotation_mode = 'XYZ'                       # euler legible en cadenas simples; quaternion = default
sc.frame_set(1);  pb.keyframe_insert("rotation_euler", frame=1)
pb.rotation_euler.x = math.radians(35)
sc.frame_set(20); pb.keyframe_insert("rotation_euler", frame=20)
bpy.ops.object.mode_set(mode='OBJECT')
```

- Relación bones↔keyframes: cada `pose.bones[...]` es una **desviación sobre el rest pose** (definido en Edit Mode [ver: rigging/rigging-en-blender-operativo §1]). `Alt+R/G/S` (o `pose.transforms_clear`) devuelve al rest sin borrar keys del frame.
- **Rotación**: quaternion evita gimbal pero no representa giros >180°; euler admite giros grandes con gimbal. Elige por eje y sé consciente de que Unity **resamplea Euler→quaternion** al importar [ver: animacion3d/keyframes-curvas §7 y §9].
- **Whole-character keying**: en blocking, keyea TODOS los canales por pose (Key All / un Keying Set de cuerpo entero) para no dejar huesos "colgados a medias" [ver: animacion3d/keyframes-curvas §1].

---

## 7. Evaluación: lo que ves ≠ lo que hay en las F-curves

La pose en pantalla es el resultado de **evaluar** las F-curves **y encima** los constraints y drivers del rig. Esto es la trampa central del export:

- Un hueso movido por un **constraint IK** (o Copy Rotation, Child Of…) [ver: rigging/rigging-en-blender-operativo §4] **no tiene F-curves propias** en su rotación final: el valor es calculado en vivo. En el Graph Editor esa curva "no existe".
- **Consecuencia:** exportar tal cual manda al FBX las curvas de los *controladores*, no el movimiento *visible* del hueso deform. Para que Unity vea el movimiento real hay que **hornear** (bake) la pose evaluada a keyframes duras en los huesos de deformación — es lo que hace `nla.bake` con `visual_keying=True` (§8, detalle en [ver: bake-animacion]).
- Lo mismo aplica a **drivers**, **modificadores de F-curve** (Cycles, Noise) [ver: animacion3d/keyframes-curvas §8] y **NLA** [ver: nla-editor]: son evaluación en vivo que Unity **no importa** — hornear o resolver antes.
- **Verificación sin ojos**: mide la malla evaluada con el depsgraph (`obj.evaluated_get(depsgraph)`), no confíes en "el script corrió" [ver: rigging/rigging-en-blender-operativo §7], [ver: animacion-blender-operativo].

---

## 8. Al motor: hornear y exportar clips limpios a Unity

Puente resumido; el detalle vive en [ver: bake-animacion] y [ver: export-clips-unity].

### Hornear (bake) — `bpy.ops.nla.bake` (params y defaults verificados 5.2)
| Param | Default | Para export a Unity |
|---|---|---|
| `frame_start` / `frame_end` | 1 / 250 | El rango del clip |
| `step` | 1 | 1 = un key por frame (lo que Unity samplea) |
| `only_selected` | `True` | Selecciona los huesos a hornear |
| `visual_keying` | `False` | **`True`** para hornear el resultado de constraints/IK (§7) |
| `clear_constraints` | `False` | `True` deja huesos con keyframes puras, sin IK residual |
| `bake_types` | — | `{'POSE'}` para armature, `{'OBJECT'}` para objeto |
| `channel_types` | — | `{'LOCATION','ROTATION','SCALE','BBONE','PROPS'}` |
| `clean_curves` | `False` | Quita keys redundantes tras hornear |

Alternativa por canales seleccionados: `bpy.ops.anim.channels_bake(use_scene_range=True, step=1.0, interpolation_type='BEZIER'|'LIN'|'CONST', bake_modifiers=True)` (verificado) — hornea F-curves con modificadores a keys reales.

### Exportar FBX — `bpy.ops.export_scene.fbx` (params de animación verificados 5.2)
| Param | Default | Ajuste game-ready |
|---|---|---|
| `bake_anim` | `True` | Deja ON — exporta la animación horneada |
| `bake_anim_step` | 1.0 | 1.0 = muestrea cada frame al `fps` de la escena |
| `bake_anim_simplify_factor` | 1.0 | 0.0 = sin simplificar (fidelidad máx); subir aligera |
| `bake_anim_use_all_actions` | `True` | Cada Action → una "take"/clip en el FBX |
| `bake_anim_use_nla_strips` | `True` | Incluye strips de NLA [ver: nla-editor] |
| `bake_anim_force_startend_keying` | `True` | Fuerza key en start/end (evita clips recortados) |
| `add_leaf_bones` | `True` | **`False`** — evita huesos `_end` basura en Unity |
| `use_armature_deform_only` | `False` | **`True`** — solo huesos deform, fuera controles/IK |
| `bake_space_transform` | `False` | **Déjalo OFF con armature** (rompe el rig) [ver: rigging/rigging-en-blender-operativo §10] |
| `axis_forward` / `axis_up` | `-Z` / `Y` | Deja los defaults; Unity los reorienta |

> Nota versión: en 5.x la **importación** de FBX usa `bpy.ops.wm.fbx_import` (importer C++ nuevo) y Collada fue eliminado; la **exportación** sigue siendo `bpy.ops.export_scene.fbx` (verificado que existe en 5.2) [ver: blender/interfaz-flujo §1], [ver: blender/import-export].

### Lado Unity (verificado, Manual Unity 6)
- **Split de clips**: un FBX con un timeline continuo se corta en el **Animation tab** con la lista de **Clips** (botón `+`) y un **rango Start/End** por clip (en frames o segundos). Alternativa: convención de archivos **`modelo@anim.fbx`** (`goober@idle.fbx`, `goober@walk.fbx`) — Unity los une como clips del `goober`.
- **Rig tab**: Animation Type **Generic** (criaturas/mecánicos, requiere **Root node**) o **Humanoid** (bípedos con retarget); Avatar Definition **Create From This Model** / **Copy From Other Avatar** [ver: rigging/rigging-en-blender-operativo §10].
- **Compresión / resample**: `Anim. Compression` = Off / **Keyframe Reduction** / Keyframe Reduction and Compression (Legacy) / **Optimal** (Generic/Humanoid); umbrales **Rotation Error** (grados), **Position/Scale Error** (%); **Resample Curves** convierte Euler→quaternion **una key por frame** (ON por defecto si detecta Euler). Verifica el clip **ya importado**, no solo en Blender [ver: animacion3d/keyframes-curvas §9].
- **Clips importados = solo lectura**: para editar, copiar keyframes a un clip nuevo, o volver a Blender (verificado).

---

## 9. bpy operativo: keying de bajo nivel (headless/MCP)

Cuando `keyframe_insert` no basta (crear una Action desde cero, poblar F-curves por datos, animar sin objeto seleccionado), se baja al channelbag. **Verificado headless en 5.2:**

```python
import bpy
from bpy_extras import anim_utils

# 1) Action + slot + channelbag manuales
act  = bpy.data.actions.new("Run")
slot = act.slots.new(id_type='OBJECT', name="Hero")        # ActionSlot .identifier -> "OBHero"
cb   = anim_utils.action_ensure_channelbag_for_slot(act, slot)   # crea layer+strip+channelbag

# 2) F-curve por data_path + índice, y keys por (frame, valor)
fc = cb.fcurves.new("location", index=2)                   # locZ
fc.keyframe_points.insert(frame=1,  value=0.0)
fc.keyframe_points.insert(frame=12, value=2.0)
fc.keyframe_points.insert(frame=24, value=0.0)
for kp in fc.keyframe_points:
    kp.interpolation = 'BEZIER'                            # ver enum abajo
fc.update()

# 3) Enganchar la Action al objeto por slot
o = bpy.data.objects["Hero"]
o.animation_data_create()
o.animation_data.action = act
o.animation_data.action_slot = slot
```

Enums verificados de `keyframe_points[i]` / `fcurve`:
- `interpolation`: `CONSTANT, LINEAR, BEZIER, SINE, QUAD, CUBIC, QUART, QUINT, EXPO, CIRC, BACK, BOUNCE, ELASTIC` (blocking = `CONSTANT` [ver: animacion3d/keyframes-curvas §6]).
- `handle_left_type` / `handle_right_type`: `FREE, ALIGNED, VECTOR, AUTO, AUTO_CLAMPED`.
- `easing`: `AUTO, EASE_IN, EASE_OUT, EASE_IN_OUT`.
- `fcurve.extrapolation`: `CONSTANT, LINEAR`.
- `fcurve.modifiers.new(type=...)`: `GENERATOR, FNGENERATOR, ENVELOPE, CYCLES, NOISE, LIMITS, STEPPED, SMOOTH` (los NO destructivos que Unity **no** importa — hornéalos, §8).

Helpers verificados en `bpy_extras.anim_utils`: `action_ensure_channelbag_for_slot`, `action_get_channelbag_for_slot`, `action_get_first_suitable_slot`, `animdata_get_channelbag_for_assigned_slot`, `bake_action`, `BakeOptions`, `AutoKeying`. El detalle del bucle MCP (evidencia, operadores modales, render de verificación) en [ver: animacion-blender-operativo].

---

## Reglas prácticas

- [ ] **Fija `scene.render.fps` (30/60) ANTES de la primera key** — el default es 24 (cine); cambiarlo después reinterpreta todo el timing.
- [ ] Fija `frame_start`/`frame_end` al rango real del clip antes de animar; trabaja en **frames enteros**.
- [ ] Usa `obj.keyframe_insert(data_path, frame=...)` para keying normal — crea Action, slot y channelbag solo; chequea el `bool` de retorno como evidencia.
- [ ] En 5.2 las F-curves viven en `strip.channelbag(slot).fcurves`, **no** en `action.fcurves` — el código viejo peta; usa `anim_utils.action_*_channelbag_for_slot`.
- [ ] Recuerda el par `animation_data.action` **+** `animation_data.action_slot`: sin slot asignado la Action no anima el objeto.
- [ ] En blocking, keyea **cuerpo entero** por pose (Key All / Keying Set) y pon la interpolación en `CONSTANT`; convierte a `BEZIER` en el paso de spline [ver: animacion3d/keyframes-curvas §6].
- [ ] Un **slot por armature**, no por hueso: el objeto Armature es la unidad; posa por datos (`pose.bones[...].rotation_euler`), nunca por operador modal en headless.
- [ ] Retime y overlap en el **Dope Sheet** (mover/escalar keys); forma de curva en el **Graph Editor** [ver: graph-editor].
- [ ] Marca `use_fake_user` en Actions que quieras conservar; una Action sin usuarios se borra al guardar.
- [ ] Antes de exportar, **hornea** lo evaluado: constraints/IK/drivers/modificadores/NLA no viajan al FBX → `nla.bake(visual_keying=True)` [ver: bake-animacion].
- [ ] Export FBX: `bake_anim=True`, `bake_anim_step=1.0`, `add_leaf_bones=False`, `use_armature_deform_only=True`, `bake_space_transform=False` con armature.
- [ ] Split de clips en Unity por rango de frames **o** por convención `modelo@anim.fbx`; un clip = un rango o una Action.
- [ ] Verifica el clip **ya importado en Unity** (compresión/Resample pueden aplanar tu ease) — API 200 ≠ animación correcta [ver: animacion3d/keyframes-curvas §9].
- [ ] `Auto Keying` OFF para MCP/headless: keyea explícito, nunca dependas del botón rojo.
- [ ] "Listo" = evidencia numérica (retorno `bool`, medición de deform con depsgraph) + visual (render posado) de la misma sesión [ver: animacion-blender-operativo].

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Seguir un tutorial pre-4.4 y usar `action.fcurves` → `AttributeError` en 5.2 | Sistema Slotted: F-curves en el channelbag del slot; usa `anim_utils.action_get_channelbag_for_slot` |
| Animar a 24fps (default) y el juego esperaba 30/60 → timing en segundos mal | Fijar `render.fps` **antes** de keyear; frames enteros al fps objetivo |
| Cambiar el fps a mitad de animación esperando que "se ajuste" | Las keys están en números de frame, no en segundos: cambiar fps reinterpreta la duración |
| Action creada y asignada pero el objeto no anima | Falta `animation_data.action_slot` — el slot engancha objeto ↔ curvas |
| Exportar con IK/constraints y en Unity el hueso no se mueve | No tenían F-curves propias (evaluación en vivo): hornear con `visual_keying=True` antes de exportar |
| Modificador Cycles/Noise que da vida en Blender y desaparece en Unity | Los modificadores no se importan: hornear a keys (`channels_bake`) o resolver con Loop Time [ver: animacion3d/keyframes-curvas §8] |
| `keyframe_insert` devuelve `False` y el script "sigue bien" | Propiedad no animable / índice mal: el `bool` es tu chequeo, trátalo como error |
| Huesos `_end` basura y controles del rig como huesos en Unity | `add_leaf_bones=False` + `use_armature_deform_only=True` en el FBX |
| Keys en frames fraccionarios (`12.4`) tras un retime a ojo | Snap a frames enteros; escalar en Dope Sheet con pivote y valores exactos |
| Auto Keying deja keys basura tras un `G` accidental | En flujo controlado/headless mantener `use_keyframe_insert_auto = False` |
| Editar la curva sobre el clip ya importado en Unity (read-only) | Volver a Blender, o copiar keyframes a un clip nuevo [ver: unity/animacion-unity] |
| Action borrada al guardar el .blend | Sin usuarios se purga: `action.use_fake_user = True` |
| `bake_space_transform=True` con un armature → rig roto | Dejarlo OFF con rigs; aplicar transforms en Object Mode sobre el rest |

## Fuentes

**Bases sintetizadas (repo El Estudio) — referenciadas, no repetidas:**
- [ver: animacion3d/keyframes-curvas] — la CRAFT de curvas: interpolación, tangentes, spacing, overshoot, blocking→spline, ciclos, y qué sobrevive al sampling de Unity. Este archivo es su EJECUCIÓN en Blender.
- [ver: blender/interfaz-flujo] — versión 5.2, modelo de data-blocks, modos, unidades, FBX import `wm.fbx_import` / Collada eliminado.
- [ver: rigging/rigging-en-blender-operativo] — el objeto Armature, los tres modos, Pose Mode, constraints/IK, y los settings FBX de armature (Add Leaf Bones OFF, Only Deform Bones, Apply Transform prohibido).
- [ver: unity/animacion-unity] — consumo en motor: Animator, blend trees, root motion, avatar, eventos.

**Fuentes verificadas esta sesión (jul-2026):**
- **Binario Blender 5.2.0 LTS local** (build 2026-07-14) — verificación directa: estructura Slotted Actions (`action.slots`/`layers`/`is_action_layered`/`is_action_legacy`, `ActionSlot.identifier`, `strip.channelbag(slot).fcurves`), `obj.keyframe_insert`/`keyframe_delete` (retorno bool, `group`, `options={'INSERTKEY_VISUAL'}`), operadores `bpy.ops.anim.*` (keyframe_insert_menu/by_name, keying_set_*), builtins de `keying_sets_all`, `tool_settings` de Auto Keying (`use_keyframe_insert_auto`, `auto_keying_mode`, `keyframe_type`), prefs de keying (`key_insert_channels`, `keyframe_new_interpolation_type=BEZIER`, `keyframe_new_handle_type=AUTO_CLAMPED`), `scene.render.fps=24`/`fps_base=1.0`/`frame_start=1`/`frame_end=250`, `frame_set(n, subframe)`, `timeline_markers`, un slot por armature (`OBArmature`, data_path `pose.bones[...]`), `nla.bake` (params+defaults), `anim.channels_bake` (params), `export_scene.fbx` (params de `bake_anim_*`, `add_leaf_bones`, etc.), enums de `keyframe_points` (interpolation/handle/easing) y `fcurve` (extrapolation/modifiers), `bpy_extras.anim_utils` (helpers de channelbag + bake).
- **Unity Manual (6000.0) — Animation Import Settings** (`class-AnimationClip.html`) — Anim. Compression Off/Keyframe Reduction/(+Compression Legacy)/Optimal; Rotation Error (grados), Position/Scale Error (%); Resample Curves (Euler→quaternion, key por frame, ON con Euler).
- **Unity Manual (6000.0) — Rig tab** (`FBXImporter-Rig.html`) — Animation Type None/Legacy/Generic/Humanoid, Avatar Definition, Optimize Game Object, Root node (Generic), Skin Weights (Standard 4 / Custom 1–32), Strip Bones.
- **Unity Manual (6000.0) — Splitting animations** (`Splittinganimations.html`) — Animation tab, lista de Clips (`+`), rangos Start/End en frames/segundos, convención `modelo@anim.fbx`.
- **Unity Manual (6000.0) — Importing animation from external sources** (`AnimationsImport.html`) — clips importados read-only, edición por copia de keyframes a clip nuevo, formatos .mb/.ma/.max/.blend/FBX.
- **Unity Manual (6000.0) — Introduction to animation clips** (`AnimationClips.html`) — tipos de clip importables y múltiples clips por archivo (contenido general).

**NO verificado esta sesión (marcado por honestidad):**
- **Blender release notes 4.4 — Animation & Rigging / "Baklava"** (developer.blender.org) y **Blender Manual — Actions / Keyframes / Timeline / Dope Sheet / Bake** (docs.blender.org) — **HTTP 403** en todos los fetch esta sesión. La ESTRUCTURA del sistema Slotted Actions está verificada directamente en el binario 5.2 (arriba); el nombre "Baklava", la fecha de introducción (4.4) y la narrativa de migración provienen del proyecto oficial y NO se re-verificaron contra la página hoy — confirmar en developer.blender.org antes de citar detalles de la transición legacy→layered.
