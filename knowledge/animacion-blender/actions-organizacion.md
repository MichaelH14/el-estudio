# Actions y organización de animaciones en Blender

> **Cuando cargar este archivo:** siempre que crees, nombres, dupliques, protejas u organices las animaciones de un personaje en Blender para llevarlas a Unity — cada idle/walk/run/attack como su propia Action, decidir "una escena con N actions" vs "un .blend por animación", exportar TODOS los clips en un FBX, o entender el sistema **Slotted/Layered Actions** (Baklava, 4.4+) que cambió cómo Blender guarda una animación. Es el CÓMO de la ejecución y del export limpio; especialmente al operar por MCP o `blender -b`.

Stack de referencia: **Blender 5.2.0 LTS** (operadores, enums, defaults y flujos verificados contra el binario local, build 2026-07-14, más round-trips de export/import empíricos) + **Unity 6**. Datos dependientes de versión marcados. 

**Puente — qué NO va aquí:** la TÉCNICA de animación (qué hace bueno un ciclo, timing, spacing, combate, capas de estado) vive en `animacion3d/` — no se repite: [ver: animacion3d/ciclos-locomocion] · [ver: animacion3d/animacion-combate] · [ver: animacion3d/keyframes-curvas] · [ver: animacion3d/capas-estados] · [ver: animacion3d/principios-produccion]. Aquí va el CÓMO en Blender + el export a clips de Unity. El rig que estas Actions animan: [ver: rigging/rigging-en-blender-operativo] (nombre viejo del manual de rigging). Insertar/editar keyframes y curvas: [ver: sistema-animacion] · [ver: graph-editor]. Combinar/preservar en NLA: [ver: nla-editor]. Hornear constraints/IK a keys: [ver: bake-animacion]. Settings FBX completos y lado Unity: [ver: export-clips-unity] · [ver: unity/animacion-unity] · [ver: blender/import-export].

---

## 1. Qué es una Action

Una **Action** (`bpy.data.actions`) es el data-block que guarda **una** animación completa: idle, walk, attack, cada uno es una Action. Contiene las curvas (F-Curves) de todas las propiedades animadas en un rango de frames. Un personaje con 12 animaciones = 12 Actions en el mismo `.blend`.

- La Action **no está "en" el objeto**: es un data-block independiente que un objeto **usa** vía su `animation_data.action`. Por eso una Action sin usuario se puede borrar sola (§5) y por eso se puede compartir/duplicar entre rigs.
- Se edita en el **Action Editor**, que es un **modo del Dope Sheet** (dropdown de modo en el header del Dope Sheet ‣ *Action Editor*). Ahí se ve/cambia la Action **activa** del objeto seleccionado, con el selector de Action (icono de "browse", el `+ New`, el `X` unlink, y el número de usuarios).
- El Dope Sheet muestra los keyframes como puntos en una cuadrícula por canal; el Graph Editor muestra las curvas [ver: graph-editor]. El Action Editor es la vista "una Action a la vez, esta la activa".

---

## 2. ⚠️ El cambio grande: Slotted / Layered Actions (4.4+, "Baklava")

**Esto es lo que más desactualizado está en la web.** Blender **4.4** cambió por defecto el modelo de datos de las Actions (proyecto *Baklava* / *Slotted Actions*). En 5.2 **toda Action nueva es "layered"**; el modelo viejo ("legacy") solo existe al abrir archivos antiguos. Un snippet pre-4.4 que hace `action.fcurves` **falla en una Action nueva de 5.2** — no existe ese atributo a nivel raíz (verificado: `hasattr(action_nueva, 'fcurves')` → `False`).

**Modelo verificado en 5.2** (introspección directa del binario):

| Concepto | Qué es | API |
|---|---|---|
| **Action** | El data-block contenedor | `bpy.data.actions` · `act.is_action_layered` (True en nuevas), `act.is_action_legacy`, `act.is_empty` |
| **Slot** | A **qué data-block** aplican estas curvas. Una Action puede tener **varios slots**, cada uno para un ID distinto (objeto, luz, material…) | `act.slots.new(id_type='OBJECT', name='...')` → `ActionSlot` con `.identifier` (prefijo 2 letras + nombre, p.ej. `OBCube`, `LALamp`), `.target_id_type` (`OBJECT`/`LIGHT`/…), `.handle`. ⚠️ `.users` **es un método, no un atributo** — `slot.users()` devuelve la lista de IDs que usan ese slot (`slot.users` sin paréntesis da el objeto función, no la lista) |
| **Layer** | Capa de animación dentro de la Action (para blending futuro; hoy normalmente 1) | `act.layers.new("Layer")` → `ActionLayer` con `.strips` |
| **Strip** | El tramo de keyframes dentro de la layer | `layer.strips.new(type='KEYFRAME')` → `ActionKeyframeStrip` con `.key_insert`, `.channelbag()`, `.channelbags` |
| **Channelbag** | El saco de F-Curves **de un slot concreto** dentro del strip. **Aquí viven las curvas ahora** | `strip.channelbag(slot, ensure=True).fcurves` |

**La ruta a las F-Curves cambió** — en 5.2 no es `act.fcurves` sino:

```python
fcurves = act.layers[0].strips[0].channelbag(slot).fcurves   # 5.2 layered
```

**Un objeto además de la Action guarda a qué slot se enganchó:** `obj.animation_data.action` (la Action) **y** `obj.animation_data.action_slot` (el `ActionSlot`). Esto es nuevo y es lo que permite que **una sola Action anime varios data-blocks**:

```python
# VERIFICADO: una Action "SharedAction" con 2 slots animando objeto Y luz a la vez
act = bpy.data.actions.new("SharedAction")
layer = act.layers.new("Layer"); strip = layer.strips.new(type='KEYFRAME')
s_obj   = act.slots.new(id_type='OBJECT', name='Cube')   # .identifier -> 'OBCube'
s_light = act.slots.new(id_type='LIGHT',  name='Lamp')   # .identifier -> 'LALamp'
obj.animation_data_create();        obj.animation_data.action = act;        obj.animation_data.action_slot = s_obj
lamp.data.animation_data_create();  lamp.data.animation_data.action = act;  lamp.data.animation_data.action_slot = s_light
# act.users == 2, la MISMA Action maneja ambos
```

**Qué significa para el flujo de juego (lo práctico):**
- **Para un personaje normal no cambia el objetivo:** sigues teniendo **una Action por clip** (idle, walk…), cada una con **un slot** apuntando al armature. El slot lo crea Blender solo al insertar el primer keyframe. No tienes que tocar slots a mano en el flujo típico.
- **Lo que cambia** es (a) el acceso por script a las curvas (channelbag, no `act.fcurves`); (b) que "una Action = un objeto" ya **no** es cierto — una Action puede quedar enganchada a un slot equivocado si la reasignas a otro rig (revisar `action_slot`); (c) los snippets viejos de la web hay que traducirlos.
- **El export a FBX sigue igual de simple:** el exportador itera las Actions y las hornea a takes (§6) — el modelo layered es transparente para el FBX.

**Al insertar un keyframe, Blender crea toda la estructura solo** (verificado): `obj.keyframe_insert("location", frame=1)` con el objeto "Cube" crea una Action layered llamada **`CubeAction`**, con **un slot** `OBCube` (`target_id_type='OBJECT'`), **una layer** `Layer`, un strip, y el channelbag con las curvas de `location`. No hay que armar slots/layers a mano salvo casos avanzados (multi-slot).

---

## 3. Crear, duplicar, nombrar, desvincular Actions

Operadores del **Action Editor** (`bpy.ops.action.*`, verificados en 5.2) y el flujo por datos:

| Acción | Operador / API | Nota |
|---|---|---|
| Nueva Action | `bpy.ops.action.new()` (botón `+ New`) o `bpy.data.actions.new(name)` + asignar | Por datos es más fiable headless (el op depende de contexto del editor) |
| Insertar keyframe (crea la Action si no hay) | `obj.keyframe_insert(data_path, frame=...)` / `pb.keyframe_insert("rotation_euler", frame=...)` | Crea Action layered `<ID>Action` + slot + layer sola |
| Duplicar la Action activa | Selector de Action ‣ botón de **copias** (icono 2 hojas) o `act.copy()` | `act.copy()` devuelve una Action nueva independiente |
| Renombrar | `act.name = "walk"` o doble-click en el selector | El nombre viaja al take del FBX → nombre del clip en Unity (§7) |
| Desvincular del objeto | `bpy.ops.action.unlink()` (botón `X`) o `obj.animation_data.action = None` | **Unlink NO borra la Action** — la deja huérfana (§5) |
| Borrar de verdad | `bpy.data.actions.remove(act)` | Elimina el data-block |

**Naming desde el minuto uno** (contrato con Unity): nombra la Action con el nombre exacto del clip que quieres en Unity — `idle`, `walk`, `run`, `attack_01`. Sin espacios raros, consistente. Renombrar después de exportar rehace los nombres de clip en Unity y rompe referencias del Animator [ver: unity/animacion-unity].

---

## 4. El error #1: la Action que "desapareció" — Fake User y usuarios

Blender **borra al guardar/recargar cualquier data-block con 0 usuarios** (garbage collection de orphan data). Una Action que desvinculaste del objeto (unlink) queda con **0 usuarios** → **se pierde en el próximo guardado/reload**. Por eso el idle que animaste "ya no está".

**Fake User** = el botón **escudo** (`F`) junto al nombre de la Action. Marca la Action como "usada" aunque ningún objeto la use, para que sobreviva. Verificado empíricamente en 5.2:

```
orphan = bpy.data.actions.new("orphan")   # users: 0, use_fake_user: False  -> se purga al guardar
orphan.use_fake_user = True               # users: 1, use_fake_user: True   -> se preserva
```

| Situación | Riesgo | Antídoto |
|---|---|---|
| Tienes 8 Actions pero solo la activa está enganchada al rig | Las otras 7 tienen 0 usuarios → **se pierden al guardar** | **Fake User (F) en TODAS**, o **stash**/Push Down a NLA (§8) |
| Duplicaste una Action para variar y desvinculaste la vieja | La vieja queda huérfana | Fake User o borrarla adrede con `actions.remove` |
| El selector muestra un número junto a la Action | Es el **conteo de usuarios**; un `2` significa que 2 IDs la comparten | Si vas a editar solo uno, primero **Make Single User** |

**Regla de oro para un personaje con muchas Actions:** que **todas** tengan Fake User activado, o que estén en el NLA (stash/push down). Una Action "en el aire" sin ninguna de las dos cosas es una animación que vas a perder.

```python
for a in bpy.data.actions:          # blindar todas las animaciones del archivo
    a.use_fake_user = True
```

---

## 5. Stashing y Push Down: preservar sin ensuciar la vista

Dos mecanismos que **guardan la Action en el NLA del objeto** (además de darle un usuario, así que no se pierde). Detalle del NLA en [ver: nla-editor]; aquí lo mínimo para organizar clips:

| Mecanismo | Qué hace | Operador |
|---|---|---|
| **Stash** | Mete la Action activa en un track NLA **silenciado (muted)** y la quita de activa. Guarda la animación "de lado" sin que sume a la evaluación. Es la forma limpia de "aparcar" un clip terminado | `bpy.ops.action.stash()` / `stash_and_create()` (Action Editor) · `bpy.ops.nla.action_unstash` para recuperar |
| **Push Down** | Empuja la Action activa a un **strip NLA nuevo** (no silenciado) y libera la activa. Base para combinar clips en el NLA | `bpy.ops.action.push_down()` (Action Editor) / `bpy.ops.nla.action_pushdown()` (NLA) |

**⚠️ Ambos son poll-gated al contexto de su editor** (verificado: `bpy.ops.action.push_down()` sin un Action Editor abierto → `RuntimeError: poll() failed, context is incorrect`). **Headless/MCP no puede llamarlos directo.** La vía por datos (equivalente exacto, verificada):

```python
# Push Down por datos (headless) — mete la Action activa en un track NLA y libera la activa
ad = obj.animation_data
tr = ad.nla_tracks.new()                                  # NlaTrack
strip = tr.strips.new(name=ad.action.name, start=1, action=ad.action)  # frame_start/end se toman de la Action
# tr.mute = True                                          # <- esto lo vuelve un "stash" (silenciado)
ad.action = None                                          # liberar la activa = efecto push-down
```

Para combinar varias Actions (encadenar walk→attack, capas additive, etc.) el trabajo es en el NLA — [ver: nla-editor]. Aquí basta saber que push down/stash son **cómo se preservan y ordenan** las N Actions de un personaje sin dejarlas huérfanas.

---

## 6. Muchas animaciones en un personaje → todos los clips a Unity

El objetivo del pipeline: **cada clip = su Action**, y exportar **todas** en un FBX que Unity parta en clips. Dos rutas y una decisión de settings.

### Ruta A — Un FBX con TODAS las Actions ("All Actions")
El exportador FBX puede hornear **cada Action del archivo como un take separado**. Settings (`bpy.ops.export_scene.fbx`, defaults verificados en 5.2):

| Arg | Default | Para qué |
|---|---|---|
| `bake_anim` | `True` | Master switch de animación |
| `bake_anim_use_all_actions` | `True` | **Cada Action → su propio take** (= un clip por Action en Unity). El caballo de batalla |
| `bake_anim_use_nla_strips` | `True` | Exporta también los strips del NLA como takes |
| `bake_anim_use_all_bones` | `True` | Keyea todos los huesos deform |
| `bake_anim_force_startend_keying` | `True` | Fuerza key en el primer y último frame de cada take (evita clips recortados) |
| `bake_anim_step` | `1.0` | Frames por muestra (1 = cada frame; súbelo para aligerar) |
| `bake_anim_simplify_factor` | `1.0` | Simplifica curvas horneadas (0 = sin simplificar) |

**Verificado empíricamente** (round-trip export→import en 5.2): 4 Actions con Fake User (`idle`,`walk`,`run`,`attack`) + `bake_anim_use_all_actions=True` → el FBX contiene **4 takes**, cada uno **con el nombre de su Action**. Con `bake_anim_use_all_actions=False` y una sola Action activa → **un solo take, nombrado por la Escena** (no por la Action). Conclusión dura: **para clips nombrados en Unity, `bake_anim_use_all_actions=True`.**

```python
bpy.ops.export_scene.fbx(
    filepath="/out/hero.fbx",
    object_types={'ARMATURE','MESH'},
    use_armature_deform_only=True,      # fuera controles/widgets [ver: rigging/rigging-en-blender-operativo]
    add_leaf_bones=False,               # nada de huesos _end basura en Unity
    bake_anim=True,
    bake_anim_use_all_actions=True,     # <- TODAS las Actions como takes
    bake_anim_use_nla_strips=False,     # evita takes duplicados si ya usas All Actions
    bake_anim_simplify_factor=0.0)      # curvas fieles (súbelo si el FBX pesa)
```

> **Doble take:** si dejas `use_all_actions` **y** `use_nla_strips` ambos en `True` y además tienes las Actions pusheadas al NLA, puedes obtener **takes duplicados**. Elige uno: All Actions (Actions sueltas con Fake User) **o** NLA Strips (todo organizado en el NLA). Detalle del export en [ver: export-clips-unity].

### Ruta B — Un `.blend`/FBX por animación (`model@animation`)
Exportas el **modelo con el rig** en un FBX y **cada animación en su propio FBX**, usando la convención de Unity `nombreModelo@nombreAnim.fbx`:

- `hero.fbx` (malla + esqueleto), `hero@idle.fbx`, `hero@walk.fbx`, `hero@attack.fbx` (solo animación).
- Unity **importa los cuatro y agrupa todas las animaciones bajo el archivo sin `@`** (verificado en doc Unity). Los `@` heredan el avatar del modelo base.
- En los FBX de solo-animación conviene **excluir la malla** (activar *Preserve Hierarchy* en Unity) para que pesen poco.

### Decisión A vs B (pros/contras para juegos)

| | A — Un FBX, N Actions | B — Un FBX por animación (`@`) |
|---|---|---|
| Nº de archivos | 1 (fácil de mover) | 1 + N (más ruido en el proyecto) |
| Editar 1 clip | Reexportas TODO el FBX | Reexportas solo ese `@archivo` |
| Trabajo en equipo | Conflictos: 1 archivo lo toca todo el mundo | Cada animador su `@archivo`, cero pisadas |
| Añadir un clip nuevo | Nueva Action + reexport completo | Nuevo `hero@nuevo.fbx`, Unity lo recoge solo |
| Mixamo / packs de mocap | Los importas como Actions y reexportas | Cada mocap ya viene como su `@archivo` [ver: animacion3d/mocap-librerias] |
| Avatar en Unity | Uno solo (Create From This Model) | Modelo base = Create; los `@` = **Copy From Other Avatar** + Source al avatar base |
| Recomendado para | Personaje con set de clips estable, solo-dev | Producción en volumen, muchos clips, equipo, mucho mocap |

**Criterio práctico:** solo-dev con un set fijo de ~10 clips → **Ruta A** (un `.blend`, todas las Actions con Fake User, All Actions ON). Equipo, o retarget de mocap constante, o clips que cambian seguido → **Ruta B** (`@animation`). En ambos casos el **esqueleto es el mismo** y Unity comparte el Avatar [ver: unity/animacion-unity §Avatar].

---

## 7. Naming: de Action a clip de Unity

- El **nombre de la Action** → nombre del **take** en el FBX (`use_all_actions`) → nombre del **clip** en el Model Importer de Unity (pestaña Animation, lista de Clips; renombrable ahí, pero mejor que salga bien de Blender).
- Convención game-ready: minúsculas, sin espacios, sufijos numéricos para variantes — `idle`, `idle_02`, `walk`, `run`, `attack_01`, `attack_02`, `hit`, `death`. Que el nombre **describa el estado del Animator** que lo va a consumir [ver: animacion3d/capas-estados].
- En Unity la lista de Clips permite **partir** un FBX de una sola animación larga en varios clips por rango de frames (`+`, Start/End), pero si en Blender ya tienes Actions separadas **no hace falta** — cada take ya es un clip limpio. Partir por frames es el plan B para animación continua importada de fuera.
- Loop: Unity NO lo hereda de Blender — **Loop Time** (y **Loop Pose**, **Cycle Offset**) se marca en el clip en Unity para idle/walk/run [ver: unity/animacion-unity §import]. La técnica de que el ciclo empalme está en [ver: animacion3d/ciclos-locomocion].

---

## 8. Pose Library: reusar poses clave (Asset Browser)

La **Pose Library** moderna vive en el **Asset Browser** (los viejos "Pose Library" basados en Action con pose markers quedaron deprecados). Una pose se guarda como un **asset de tipo Action** de un frame y se aplica/mezcla sobre el rig. Operadores verificados (`bpy.ops.poselib.*`):

| Operador | Qué hace |
|---|---|
| `poselib.create_pose_asset` | Crea un asset de pose desde los huesos seleccionados en Pose Mode |
| `poselib.apply_pose_asset` | Aplica la pose del asset activo al rig (con `blend_factor`, flipped) |
| `poselib.blend_pose_asset` | Mezcla interactiva hacia la pose (0→100%) |
| `poselib.pose_asset_select_bones` | Selecciona en el rig los huesos que la pose afecta |
| `poselib.copy_as_asset` / `paste_asset` | Copiar/pegar poses entre archivos |
| `pose.blend_with_rest` / `pose.blend_to_neighbor` | Mezclar la pose actual con el rest o con el keyframe vecino (útil al bloquear) |

Uso en juegos: guardar poses clave reutilizables (contact/passing/down/up de un ciclo, la pose de impacto de un attack, expresiones faciales base) y reponerlas al armar variantes o al bloquear un clip nuevo — acelera el "pose-to-pose" [ver: animacion3d/principios-produccion]. Organización del `.blend` y marcado de assets: [ver: blender/organizacion-blend].

---

## 9. Bake Action: aplanar constraints/IK/mocap a keyframes limpios

Antes de exportar, cualquier animación que dependa de **constraints, IK, drivers o strips NLA** debe **hornearse** a keyframes por hueso, porque el FBX solo lleva rotaciones/posiciones directas, no constraints. Operador **Bake Action** = `bpy.ops.nla.bake` (menú *Object ‣ Animation ‣ Bake Action…* en Object Mode, o *Pose ‣ Animation*). Args verificados en 5.2:

| Arg | Default | Nota |
|---|---|---|
| `frame_start` / `frame_end` | `1` / `250` | Rango a hornear (ponerlo al rango real de la Action) |
| `step` | `1` | Muestra cada N frames |
| `only_selected` | `True` | Solo huesos seleccionados (seleccionar TODOS los deform antes) |
| `visual_keying` | `False` | **`True` imprescindible con IK/constraints** — keyea la pose *resultante*, no los valores locales |
| `clear_constraints` | `False` | Borra los constraints tras hornear (útil para dejar el clip "plano") |
| `use_current_action` | `False` | `True` = hornea sobre la Action activa en vez de crear una nueva |
| `clean_curves` | `False` | Quita keyframes redundantes |
| `bake_types` | `{'POSE'}` / `{'OBJECT'}` | Huesos (POSE) u objeto |
| `channel_types` | `LOCATION,ROTATION,SCALE,BBONE,PROPS` | Qué canales hornear |

Flujo y casos (mocap retargeteado, IK a FK, drivers) en detalle: [ver: bake-animacion]. Regla: **con IK/constraints, siempre `visual_keying=True`**, o el clip horneado no reproduce la pose que veías.

```python
bpy.ops.nla.bake(frame_start=1, frame_end=int(act.frame_range[1]),
                 only_selected=True, visual_keying=True,
                 bake_types={'POSE'}, use_current_action=True, clean_curves=True)
```

---

## Reglas prácticas

1. **Una animación = una Action**; N clips del personaje = N Actions en el mismo `.blend`. Nómbralas con el nombre exacto del clip de Unity (`idle`, `walk`, `attack_01`) desde el minuto uno.
2. En 5.2 **toda Action nueva es layered**: las F-Curves viven en `layer.strips[0].channelbag(slot).fcurves`, **no** en `act.fcurves` (no existe). Traducir cualquier snippet pre-4.4.
3. Insertar el primer keyframe (`keyframe_insert`) ya crea la Action + slot + layer — no armes slots a mano salvo multi-slot avanzado.
4. **Fake User (F/escudo) en TODAS las Actions** que no estén enganchadas al rig, o piérdelas al guardar (0 usuarios = purgada). Alternativa: stash / push down al NLA.
5. Unlink (`X`) **no borra** la Action, la deja huérfana; borrar de verdad es `bpy.data.actions.remove`.
6. Preservar/aparcar un clip terminado: **stash** (track NLA muted) o **push down** (strip NLA). Headless: hazlo por datos (`nla_tracks.new` + `strips.new`), los operadores son poll-gated al editor.
7. Export a Unity: **`bake_anim_use_all_actions=True`** para que cada Action sea un take nombrado. Con `False` sale un solo take con nombre de escena.
8. No dejes `use_all_actions` **y** `use_nla_strips` ambos en True si las Actions también están en el NLA → takes duplicados. Elige una organización.
9. Export siempre con `add_leaf_bones=False` + `use_armature_deform_only=True` (contrato de rig con Unity) [ver: rigging/rigging-en-blender-operativo].
10. Antes de exportar, **hornea** (`nla.bake`) todo lo que dependa de IK/constraints/drivers/NLA, con **`visual_keying=True`**.
11. Ruta A (un FBX, N Actions) para solo-dev con set estable; Ruta B (`model@animation`) para equipo, muchos clips o mocap constante — y en Unity los `@` usan **Copy From Other Avatar**.
12. El mismo esqueleto en todos los FBX: renombrar un hueso tras el primer import rompe el Avatar de Unity [ver: unity/animacion-unity].
13. Loop no viaja de Blender a Unity: marca **Loop Time** en el clip en Unity para ciclos.
14. Poses clave reutilizables → **Pose Library** en el Asset Browser (`poselib.create_pose_asset` / `apply_pose_asset`), no la vieja pose-library por Action.
15. Al compartir una Action entre rigs, revisa `animation_data.action_slot`: puede quedar apuntando al slot equivocado. **Make Single User** antes de editar una Action con >1 usuario.
16. Verifica el export de verdad: reimporta el FBX en una escena vacía y cuenta las Actions/takes — "el script corrió" no es evidencia [ver: rigging/rigging-en-blender-operativo §verificación].

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| "Mis otras animaciones desaparecieron al reabrir" | 0 usuarios = purgadas: **Fake User** en todas, o stash/push down al NLA |
| Snippet de la web con `action.fcurves` da `AttributeError` en 5.2 | Action layered: usar `strip.channelbag(slot).fcurves`; `act.fcurves` no existe en nuevas [ver: sistema-animacion] |
| El FBX exporta **un solo clip** llamado como la escena | Faltó `bake_anim_use_all_actions=True`; con False solo sale la Action activa como take único |
| Aparecen clips **duplicados** en Unity | `use_all_actions` **y** `use_nla_strips` ambos True con Actions en el NLA — desactiva uno |
| El clip horneado no reproduce la pose (IK/constraints) | `nla.bake` con **`visual_keying=True`**; sin él keyea valores locales, no la pose resultante [ver: bake-animacion] |
| `bpy.ops.action.push_down()` falla con "poll() failed" en headless | Es poll-gated al Action Editor: usar la vía por datos (`nla_tracks.new` + `strips.new`, luego `action=None`) |
| Reasigné una Action a otro rig y anima raro/nada | El `action_slot` quedó en el slot equivocado; reasignar `animation_data.action_slot`, y **Make Single User** si comparten |
| Los clips `@animation` no encuentran el rig en Unity | Avatar Definition de los `@` mal: **Copy From Other Avatar** + Source al avatar del modelo base |
| Huesos `_end` / controles del rig aparecen como huesos en Unity | Export con `add_leaf_bones=False` + `use_armature_deform_only=True` [ver: export-clips-unity] |
| El idle/walk no hace loop en Unity | Loop no viaja del FBX: marcar **Loop Time**/**Loop Pose** en el clip en el Model Importer |
| Nombres de clip feos (`Armature|Take 001`) en Unity | Nombra las **Actions** antes de exportar y usa `use_all_actions`; el nombre de la Action es el del take |
| Edité una Action y cambió en otro objeto también | Tenía >1 usuario (compartida): **Make Single User** antes de editar |

## Fuentes

- **Binario Blender 5.2.0 LTS local** (build 2026-07-14) — verificación directa e introspección: modelo layered/slotted (`Action.slots`/`.layers`/`is_action_layered`/`is_action_legacy`/`is_empty`; `ActionSlot.identifier`/`target_id_type` con prefijos OB/LA; `ActionLayer.strips`; `ActionKeyframeStrip.channelbag`/`key_insert`; ausencia de `act.fcurves` en Action nueva; `animation_data.action_slot`), operadores `bpy.ops.action.*` (`new`,`unlink`,`push_down`,`stash`,`stash_and_create`,`duplicate`) y `bpy.ops.nla.*` (`action_pushdown`,`bake`,`tweakmode_enter/exit`,`tracks_add`), args y defaults de `export_scene.fbx` (`bake_anim*`, `add_leaf_bones`, `use_armature_deform_only`, ejes) y de `nla.bake` (`visual_keying`,`only_selected`,`bake_types`,`channel_types`), API NLA por datos (`nla_tracks.new`, `strips.new(name,start,action)`, `track.mute`), operadores `bpy.ops.poselib.*`, y comportamiento de Fake User (0 usuarios → purga; `use_fake_user` → 1 usuario). **Round-trips empíricos:** 4 Actions + `use_all_actions=True` → 4 takes nombrados por Action al reimportar; `use_all_actions=False` → 1 take con nombre de escena; una Action con 2 slots animando objeto+luz (`act.users==2`).
- **Unity Manual — Splitting animations** (docs.unity3d.com/Manual/Splittinganimations.html) — lista de Clips, `+`, rangos Start/End, clips múltiples predefinidos, y la convención `modelName@animationName.fbx` (Unity recoge todas las anims al archivo sin `@`; *Preserve Hierarchy* para excluir la malla).
- **Unity Manual — Model Importer animation clip settings** (docs.unity3d.com/Manual/class-AnimationClip.html) — Loop Time, Loop Pose, Cycle Offset, Root Transform Rotation/Position(Y)/Position(XZ) con Bake Into Pose y Based Upon.
- **Unity Manual — Avatar Creation and Setup** (docs.unity3d.com/Manual/AvatarCreationandSetup.html) — Avatar Definition Create From This Model vs Copy From Other Avatar + Source, reuso de avatar para archivos `@animation` con el mismo esqueleto.
- **Bases sintetizadas de El Estudio:** [ver: rigging/rigging-en-blender-operativo] (armature, modos, verificación, settings FBX de rig: deform-only, add_leaf_bones OFF), [ver: unity/animacion-unity] (Animator, clips, Avatar Humanoid/Generic, root motion, import de animación), y los cross-refs de técnica en [ver: animacion3d/ciclos-locomocion] · [ver: animacion3d/animacion-combate] · [ver: animacion3d/keyframes-curvas].
</content>
</invoke>
