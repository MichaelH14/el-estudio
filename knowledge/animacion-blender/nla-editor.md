# El NLA Editor en Blender 5.2

> **Cuando cargar este archivo:** al EJECUTAR en Blender (por MCP/headless o a mano) el montaje no lineal de animación — apilar y secuenciar Actions como *strips* en *tracks*, retimear (mover/escalar/repetir) strips, mezclar con blend in/out y capas additive (Add/Combine), gobernar influencia y extrapolación, mutear/aislar tracks, hornear el stack del NLA a una Action plana, y sobre todo **exportar cada strip/action como un clip separado a Unity** vía FBX. Es el manual OPERATIVO del editor Nonlinear Animation. La TÉCNICA (qué es un buen additive de respiración, cómo se secuencia una cinemática, el diseño del grafo de estados/capas) NO se repite aquí: vive en [ver: animacion3d/capas-estados] y [ver: animacion3d/ciclos-locomocion]. La craft de curvas/tangentes en [ver: animacion3d/keyframes-curvas]. El sistema de Actions/Slots de 5.2 en [ver: sistema-animacion] y [ver: actions-organizacion]; el horneado a fondo en [ver: bake-animacion]; la config de import en Unity en [ver: export-clips-unity] y [ver: unity/animacion-unity].

**Versiones:** Blender **5.2 LTS** (verificado esta sesión: `docs.blender.org/manual/en/latest` sirve las páginas tituladas "Blender 5.2 LTS Manual" — la etiqueta LTS SÍ está confirmada) + **Unity 6**. El sistema de animación cambió en 4.4+ (proyecto Baklava / **Slotted Actions**): lo relevante para el NLA está en §1.

---

## 1. Qué es el NLA en 5.2 (y qué cambió con Slotted Actions)

El NLA edita animación **a nivel de bloque**, no de keyframe: trabaja con **Actions** (segmentos de animación nombrados y reutilizables), como una línea de edición de vídeo donde cada clip es una Action. Es la ejecución en Blender del "clip como ladrillo de un sistema" de [ver: animacion3d/capas-estados §0].

| Pieza | Qué es (5.2) | Nota operativa |
|---|---|---|
| **Action** | El contenedor de la animación. Un data-block reusable (F-Curves + canales) | Se appendea/linkea/exporta como una animación distinta. Base de todo [ver: actions-organizacion] |
| **Slot** | Sub-conjunto DENTRO de una Action que anima un data-block concreto (objeto, material, shape keys…) | **Novedad 4.4+**: una Action puede animar varios data-blocks, uno por slot. El data-block referencia Action **+** Slot |
| **Strip** | Una *instancia* de una Action colocada en el tiempo dentro de un track | Varios strips pueden referenciar la MISMA Action; puede recortar/estirar/repetir la Action |
| **Track** | Una pista que reproduce uno o más strips en secuencia | Funcionan como capas: el track de más arriba tiene precedencia (o se mezcla) |
| **Action Track** | El track superior (cabecera **naranja**), especial: NO contiene strips, contiene la **Action activa** donde caen los keyframes nuevos por defecto | Aquí vive lo que editas en Dope Sheet/Graph. `Push Down` lo convierte en strip |

**Implicación Slotted Actions para el NLA (verificar en scripts):**
- Un strip enlaza **Action + Slot** (`NlaStrip.action_slot` / `NlaStrip.action_slot_handle`). Para un personaje de juego con una Action por animación suele haber **un slot** auto-asignado; el slot debe coincidir con el *tipo* del data-block objetivo o no anima nada.
- Las Actions ya tienen internamente **layers y strips propios**, pero en 5.2 **NO están expuestos en la UI** (preparación para features futuras). **Sí** aparecen en la Python API — un executor por script debe contar con esa estructura al recorrer una Action [ver: sistema-animacion].
- El "NLA layered/aditivo" real de un personaje se sigue montando con **tracks del NLA editor** (esto sí es lo de este archivo), no con las layers internas de la Action.

---

## 2. Anatomía del editor: Action Track, Push Down y Tweak Mode

El flujo canónico: **animas en la Action activa → la empujas (Push Down) a un strip → repites → mezclas los strips**.

| Elemento | Qué hace | Dónde / operador |
|---|---|---|
| **Push Down Action** | Crea un track nuevo bajo el Action Track y mueve la Action activa a él como strip; deja el Action Track vacío | Botón en el Action Track · `bpy.ops.nla.action_pushdown(track_index=-1)` |
| **Tab — Tweak Mode (Full Stack)** | Entra a editar la Action de un strip; deja el resto de tracks activos (ves su efecto) | `Strip ‣ Start Tweaking Strips Actions (Full Stack)` · `nla.tweakmode_enter(use_upper_stack_evaluation=True)` |
| **Tweak Mode (Lower Stack)** | Igual, pero **mutea los tracks de arriba** mientras editas | `Strip ‣ …(Lower Stack)` · `nla.tweakmode_enter()` (default `use_upper_stack_evaluation=False`) |
| **Shift-Tab — Start Editing Stashed Action** | Entra a Tweak Mode **y pone el track en Solo** (mutea todo lo demás) para editar aislado | `Strip ‣ Start Editing Stashed Action` |
| **Pin** (solo en Tweak Mode) | Muestra los keyframes en su tiempo original (frame 1…) en vez del tiempo desplazado por el strip | Icono pin del Action Track |
| **Salir de Tweak** | Vuelve al modo NLA | `Tab` / `Shift-Tab` · `nla.tweakmode_exit()` |

- Tras un Push Down, si insertas un keyframe nuevo Blender **crea automáticamente una Action activa nueva** para alojarlo. Ese es el patrón para acumular un catálogo: animas → Push Down → animas la siguiente → Push Down.
- El Dope Sheet muestra normalmente **solo** la Action activa; para ver/editar otra Action montada en un strip hay que entrar en Tweak Mode.

---

## 3. Strips: tipos y propiedades

### 3.1 Tipos de strip (Add menu del NLA)
| Tipo | Qué hace | Añadir |
|---|---|---|
| **Action Strip** | Reproduce los keyframes de una Action | `Add ‣ Action` (Shift-A) · o `Push Down` |
| **Transition** | Interpola entre dos Action strips vecinos seleccionados | `Add ‣ Transition` (Shift-T) · `nla.transition_add()` |
| **Sound** | Dispara el clip de un Speaker; dura lo que dure el audio (ignora la longitud del strip) | `Add ‣ Sound` (Shift-K) |
| **Meta Strip** | Agrupa varios strips para mover/escalar/copiar como uno | `Strip ‣ Make Meta` (Ctrl-G) · `nla.meta_add()` |

### 3.2 Propiedades del strip (Sidebar N → Strip ‣ Active Strip)
Estos son los diales que un executor toca. Nombres de UI **verificados** + su atributo Python de la API `NlaStrip`.

| Propiedad UI | Atributo Python | Qué controla |
|---|---|---|
| **Frame Start / End** | `frame_start` / `frame_end` | Posición y duración del strip en el timeline global. Mover Frame Start desplaza sin cambiar duración; mover Frame End **recorta o extiende** la Action |
| **Action Clip ‣ Frame Start/End** | `action_frame_start` / `action_frame_end` | Qué tramo de la Action se usa (recorte interno). Reducir Frame End en −1 excluye el último key duplicado de un ciclo |
| **Playback Scale** | `scale` (0.0001–1000) | Acelera (<1) o ralentiza (>1) la Action. Retiming sin re-keyear |
| **Repeat** | `repeat` (0.1–1000) | Repite el rango de la Action N veces dentro del strip |
| **Playback Reversed** | `use_reverse` | Reproduce el strip al revés |
| **Sync Length ‣ Now** | `use_sync_length` | Iguala el largo del strip al primer/último key de la Action |
| **Extrapolation** | `extrapolation` | Qué pasa FUERA del strip (§4) |
| **Blending** | `blend_type` | Cómo se combina con los tracks de abajo (§5) |
| **Blend In / Out** | `blend_in` / `blend_out` | Frames de fade-in/out de la influencia |
| **Auto Blend In/Out** | `use_auto_blend` | Calcula Blend In/Out mirando strips que solapan arriba/abajo |
| **Animated Influence** | `use_animated_influence` + `influence` | Influencia manual/animable por F-Curve (alternativa a Blend In/Out) (§5) |
| **Animated Strip Time** | `use_animated_time`, `use_animated_time_cyclic` | Anima QUÉ frame de la Action se muestrea (retiming por curva); cíclico para repetir |
| **Mute** | `mute` | El strip deja de contribuir (borde punteado) |

### 3.3 Retiming: mover, escalar, extender
| Operación | Atajo / menú | Nota |
|---|---|---|
| **Move** | `G` · `Strip ‣ Transform ‣ Move` | Mueve en tiempo o a otro track |
| **Scale** (retiming) | `S` · `Strip ‣ Transform ‣ Scale` | Escala usando el **Playhead como pivote**. Aplica con `Apply Scale` (Ctrl-A) o resetea con `Clear Scale` (Alt-S) |
| **Extend** | `E` | Empuja solo los strips a un lado del Playhead — para abrir hueco |
| **Split** | `Y` · `nla.split()` | Parte el strip en el frame actual |
| **Swap** | `Alt-F` | Intercambia el orden de dos strips en el track |
| **Snap** | `Strip ‣ Snap` · `nla.snap()` | Al frame/segundo/marker más cercano; toggle de snap en la cabecera |
| **Duplicate** | `Alt-D` | Copia **duplicando la Action** (editar la copia no afecta al original) |
| **Linked Duplicate** | `Shift-D` | Copia **reusando la Action** (editar afecta a ambos; Blender lo resalta en rojo) |
| **Make Single User** | `U` · `nla.make_single_user()` | Da a cada strip su propia Action, para editar sin tocar otros usos |

- ⚠️ **Escalar un strip NO re-samplea la curva**: cambia la velocidad de muestreo de la Action. Al exportar con sampling por frame (§6) eso se hornea; en el DCC sigue siendo la misma Action. Retimear "keys juntas ≠ lento" sigue aplicando [ver: animacion3d/keyframes-curvas §5].

---

## 4. Extrapolación: qué hace el strip fuera de sus límites

Gobierna los frames **antes/después** del strip (relevante al secuenciar y al mezclar). Atributo `extrapolation`; default `HOLD`.

| Modo | `extrapolation` | Efecto |
|---|---|---|
| **Hold** | `HOLD` | Mantiene el valor del primer key hacia atrás y del último hacia adelante (hasta el siguiente strip). Default |
| **Hold Forward** | `HOLD_FORWARD` | Solo mantiene el valor del ÚLTIMO key hacia adelante |
| **Nothing** | `NOTHING` | Fuera del strip las propiedades vuelven a su valor por defecto |

- **Regla de secuenciación**: para encadenar strips en una sola pista (cinemática), casi siempre `Hold` o `Hold Forward`, para que no haya "vacíos" que devuelvan el rig a la pose default entre clips.
- **Regla de capas additive**: un additive que solo debe sumar *dentro* de su ventana usa `Nothing` (o Blend In/Out a 0 en los bordes) para no sostener el delta indefinidamente.
- Mientras la Action sigue siendo la **activa** (Action Track), se usa `Hold` sin importar el ajuste; la extrapolación elegida aplica una vez hecho Push Down.

---

## 5. Tracks, orden y blending (las "capas" del NLA)

### 5.1 Orden y control de tracks
- **Evaluación de abajo hacia arriba**: el track más alto tiene **precedencia** sobre los de abajo (o los mezcla según su `blend_type`). Igual que capas de imagen.
- Controles por track (cabecera): **Mute** (deja de contribuir, borde punteado), **Solo** (icono estrella: mutea TODO lo demás, incluido el Action Track), **Lock** (candado: bloquea cambios). El toggle **Disable NLA stack** (cabecera azul del objeto) mutea todos los tracks menos el Action Track.
- Operadores: `Track ‣ Add` (bajo el Action Track), `Track ‣ Add Above Selected`, `Track ‣ Move To Top/Up/Down/To Bottom` (PageUp/Down), `Track ‣ Delete`, `Track ‣ Remove Empty Animation Data`. API: `ad.nla_tracks.new(prev=None)` / `nla.tracks_add(above_selected=False)`.

### 5.2 Blending: cómo se combina cada strip con lo de abajo
Atributo `blend_type` (default `REPLACE`). Fórmula base: `result = mix(previous, previous (op) value, influence)`.

| Blending | `blend_type` | Qué hace | Uso |
|---|---|---|---|
| **Replace** | `REPLACE` | Sobrescribe lo de abajo (con Influence<1, interpola lineal previous↔nuevo) | Secuenciar clips que se sustituyen; base override [ver: animacion3d/capas-estados §5.2] |
| **Add / Subtract / Multiply** | `ADD` / `SUBTRACT` / `MULTIPLY` | Suma/resta/multiplica el valor del strip sobre lo de abajo | **Additive layers**: respirar, lean, recoil, aim offset |
| **Combine** | `COMBINE` | Elige la matemática correcta por tipo de canal (ver abajo) — el additive "que no rompe" | Additive sobre rotaciones/escala sin deformar |

**Combine, por tipo de canal (verificado):**
| Canal | Fórmula |
|---|---|
| Rotación Axis/Angle | `result = previous + value × influence` |
| Rotación Quaternion | `result = previous × value ^ influence` (math de cuaternión en los 4 canales a la vez) |
| Escala (proporcional) | `result = previous × (value / default) ^ influence` |
| Otros | `result = previous + (value − default) × influence` |

- ⚠️ **Combine + cuaternión fuerza los 4 canales**: siempre driva `WXYZ` juntos y "Insert Single Keyframe" mete los 4 keys. Cuenta con esto al hornear/exportar [ver: animacion3d/keyframes-curvas §7].
- **Additive en NLA = equivalente conceptual a las additive layers de Unity** [ver: animacion3d/capas-estados §5.1]: un delta sobre una pose de referencia. La diferencia clave: en el NLA el "delta" lo produce `Add`/`Combine` sobre el track base; en Unity el clip additive se marca como additive en el import. Si vas a exportar el additive como clip suelto a Unity, **autóralo como delta** en su Action, no confíes en que el `blend_type` del NLA viaje (NO viaja al FBX — §6).

### 5.3 Influencia
- **Blend In/Out** (o **Auto Blend**): rampa automática de influencia en los bordes del strip — para cruces suaves entre strips solapados (crossfade tipo vídeo).
- **Animated Influence** (`use_animated_influence`): F-Curve de influencia 0–1 dibujable a mano (visible en el Graph Editor con *Show Control F-Curves*). Úsalo cuando el fade no es lineal o la capa entra/sale varias veces. Es el control fino equivalente al peso de capa animado de [ver: animacion3d/capas-estados §5.2].

---

## 6. El NLA como exportador de MÚLTIPLES clips a Unity (FBX)

Este es el caso de producción #1 del NLA para juegos: **cada strip (o cada Action) se exporta como un clip separado**. El exportador FBX (add-on clásico, `File ‣ Export ‣ FBX`) los escribe como **AnimStacks**, y Unity lee **cada AnimStack como un `AnimationClip`** [ver: export-clips-unity].

### 6.1 Panel *Bake Animation* del FBX exporter (verificado, tooltips de `export_scene.fbx`)
| Opción UI | Parámetro Python | Qué hace (literal del tooltip) |
|---|---|---|
| **Key All Bones** | `bake_anim_use_all_bones` | "Force exporting at least one key of animation for all bones (needed with some target applications, like UE4)" |
| **NLA Strips** | `bake_anim_use_nla_strips` | "Export each **non-muted NLA strip** as a separated FBX's AnimStack, if any, instead of global scene animation" |
| **All Actions** | `bake_anim_use_all_actions` | "Export each **action** as a separated FBX's AnimStack… animated objects get all actions compatible with them" |
| **Force Start/End Keying** | `bake_anim_force_startend_keying` | "Always add a keyframe at start and end of actions for animated channels" |
| **Sampling Rate** | `bake_anim_step` (0.01–100) | "How often to evaluate animated values (in frames)" |
| **Simplify** | `bake_anim_simplify_factor` (0–100) | "How much to simplify baked values (0.0 to disable, higher = more simplified)" |

### 6.2 Las dos rutas de exportación multi-clip (elegir UNA)
| Ruta | Config | Cada clip sale de | Cuándo |
|---|---|---|---|
| **All Actions** | `bake_anim_use_all_actions=True`, `use_nla_strips=False` | Cada **Action** del .blend compatible con el armature | **Flujo de juego típico**: un catálogo de Actions sueltas (Walk, Run, Jump…). No necesitas montar el NLA para exportar clips separados |
| **NLA Strips** | `bake_anim_use_nla_strips=True`, `use_all_actions=False` | Cada **strip no muteado** del NLA | Cuando cada clip es un montaje (retiming, repeticiones, additive horneado, un tramo recortado de una Action) que no existe como Action suelta |

- **Regla de oro**: para exportar clips a Unity **casi siempre basta `All Actions`** con las Actions bien nombradas y con **Manual Frame Range** por Action (§7). El NLA solo hace falta cuando el clip es un *resultado montado*, no una Action tal cual.
- ⚠️ **El `blend_type`, la influencia y el stack de tracks NO viajan al FBX** tal cual. `NLA Strips` exporta cada strip **por separado** (no el resultado mezclado del stack). Si el clip que quieres es la MEZCLA de varios tracks (base + additive), primero **hornea** (§7) y exporta esa Action; no esperes que Unity reconstruya el blend.
- **Nombres**: el AnimStack toma el nombre de la Action/strip → ese es el nombre del clip en Unity. Aplica `Categoria_Accion_Variante` desde el DCC [ver: animacion3d/capas-estados §8]. La convención `modelo@animacion.fbx` de Unity y el split de clips se cubren en [ver: export-clips-unity].
- **Rango**: si una Action tiene **Manual Frame Range** activo, el exporter usa ese rango; si no, deriva del rango de keyframes de cada Action.

### 6.3 Snippet — export multi-clip por Actions (headless/MCP)
```python
import bpy
# Selecciona el armature (y su malla) antes de exportar.
bpy.ops.export_scene.fbx(
    filepath="/ruta/Hero@anims.fbx",
    use_selection=True,
    object_types={'ARMATURE', 'MESH'},
    add_leaf_bones=False,            # Unity: evita huesos hoja basura
    primary_bone_axis='Y', secondary_bone_axis='X',
    bake_anim=True,
    bake_anim_use_all_actions=True,  # 1 clip por Action
    bake_anim_use_nla_strips=False,
    bake_anim_use_all_bones=True,
    bake_anim_force_startend_keying=True,
    bake_anim_step=1.0,              # 1 muestra por frame
    bake_anim_simplify_factor=0.0,   # 0 = sin simplificar; deja que Unity reduzca
    apply_unit_scale=True, global_scale=1.0, axis_forward='-Z', axis_up='Y',
)
```
- `add_leaf_bones=False` y `simplify_factor=0.0` son las opciones sanas para Unity (la reducción de keys se decide en el import de Unity, no aquí) [ver: export-clips-unity], [ver: animacion3d/keyframes-curvas §9].
- Para exportar por **strips** en su lugar: `bake_anim_use_nla_strips=True` y `bake_anim_use_all_actions=False`.

---

## 7. Hornear (Bake) el NLA a una Action plana

Cuando el resultado depende del **stack** (varios tracks additive), de **F-Curve modifiers** (Cycles/Noise), **drivers** o **constraints**, la Action cruda no contiene el movimiento final. **Bake Action** lo evalúa y crea un key en **cada frame** [ver: bake-animacion].

**`Object ‣ Animation ‣ Bake Action…`** (Object/Pose Mode) o **`Strip ‣ Bake Action`** en el NLA. Operador `bpy.ops.nla.bake`.

| Parámetro UI | Python | Nota |
|---|---|---|
| Start / End Frame | `frame_start` / `frame_end` | Rango a hornear |
| Frame Step | `step` | Frames a saltar por muestra (1 = todos) |
| Only Selected Bones | `only_selected` | Solo huesos seleccionados (Pose) |
| Visual Keying | `visual_keying` | Keyframea la transformación **final** (con constraints aplicados) |
| Clear Constraints | `clear_constraints` | Borra constraints tras hornear (activar junto con Visual Keying para un bake correcto) |
| Clear Parents | `clear_parents` | Hornea la animación heredada del parent sobre el objeto y luego **desvincula el parent** (solo objetos, no huesos) |
| Overwrite Current Action | `use_current_action` | Hornea sobre la Action actual en vez de crear una nueva |
| Clean Curves | `clean_curves` | Elimina keys redundantes tras hornear |
| Bake Data | `bake_types` | `{'POSE'}` (huesos) o `{'OBJECT'}` |
| Channels | `channel_types` | `{'LOCATION','ROTATION','SCALE','BBONE','PROPS'}` |

```python
import bpy
bpy.ops.nla.bake(
    frame_start=1, frame_end=48, step=1,
    only_selected=False,
    visual_keying=True,          # captura constraints/IK resueltos
    clear_constraints=False,
    use_current_action=False,    # crea Action nueva "…_baked"
    clean_curves=True,
    bake_types={'POSE'},
    channel_types={'LOCATION','ROTATION','SCALE','BBONE','PROPS'},
)
```

- **Cuándo hornear antes de exportar**: stack additive complejo, ciclos con modificador Cycles/Noise (no viajan al FBX [ver: animacion3d/keyframes-curvas §8-9]), IK/constraints, o cualquier clip que sea el *resultado mezclado* de varios tracks. Horneas → obtienes una Action plana → la exportas con `All Actions`.
- **Cuándo NO**: si cada animación ya es una Action limpia keyframeada a mano (walk/run/attack sueltos), hornear solo infla el clip. El sampling por frame del FBX exporter (`bake_anim_step`) ya "hornea" lo necesario al exportar.
- ⚠️ Bake produce **un key por frame** → curvas densas. Deja que Unity haga Keyframe Reduction en el import en vez de subir el ruido [ver: export-clips-unity].

---

## 8. Casos de uso reales (recetas operativas)

### 8.1 Ciclo de caminar + additive de respirar
La técnica del additive (delta sobre pose de referencia) está en [ver: animacion3d/capas-estados §5.1]. En Blender:
1. Track base: strip `Walk` (Replace). Ciclo con contactos en fase [ver: animacion3d/ciclos-locomocion].
2. Track encima: strip `Breathe` con **`blend_type='ADD'`** (o `COMBINE`). La Action `Breathe` debe ser un **delta** (diferencia respecto a la pose neutra), no una pose absoluta.
3. `Nothing` de extrapolación o Blend In/Out para que el delta no se sostenga fuera de su ventana.
4. Si vas a exportar el resultado como **un** clip "walk que respira": **hornea** (§7) el stack a una Action y expórtala. Si en Unity prefieres additive nativo, exporta `Breathe` como clip aparte y móntalo como additive layer allá [ver: unity/animacion-unity §3].

### 8.2 Secuenciar una cinemática
1. Un track, varios Action strips en fila: `Idle → Draw → Swing → Sheathe`.
2. Extrapolación `Hold`/`Hold Forward` para no dejar vacíos.
3. Cruces suaves: solapar los strips y usar **Auto Blend** o strips **Transition** (Add ‣ Transition) entre pares.
4. Retimear con `S` (pivote = Playhead) y `G`; `Set Preview Range` (P) para iterar un tramo.
5. Exportar como **un** clip: hornear el track a una Action y exportar; o como clips separados: `NLA Strips` (cada strip → AnimStack).

### 8.3 Reusar una Action en varios contextos
- Varios strips referenciando la **misma** Action (Linked Duplicate, Shift-D) → editar los keys en una actualiza todas. Para desligar una copia: `Make Single User` (U) o `Duplicate` (Alt-D).
- Recortar/estirar por contexto con `action_frame_start/end`, `scale` y `repeat` sin tocar la Action original.

---

## 9. ¿NLA o Actions sueltas? (para un flujo de juego)

| Situación | Recomendación |
|---|---|
| Catálogo de clips de personaje (walk/run/jump/attacks) para Unity | **Actions sueltas** + export `All Actions`. El NLA es innecesario — el exportador ya hace 1 clip por Action |
| Cinemática montada (secuencia, retiming, crossfades) | **NLA** (secuenciar strips) → hornear → exportar |
| Additive layered horneado a un clip | **NLA** (`Add`/`Combine`) → **Bake** → exportar la Action horneada |
| Additive que se resolverá en el motor | **Actions sueltas** (delta) → export → montar la additive layer en Unity [ver: animacion3d/capas-estados §5] |
| Un tramo/variante recortado de una Action existente sin duplicar keys | **NLA** (strip con `action_frame_*`, `scale`, `repeat`) |
| Reusar la misma Action con timings distintos | **NLA** (Linked Duplicate + retiming) |

**Sesgo por defecto para juego:** *actions sueltas + `All Actions` bastan*. El NLA gana cuando el clip que necesitas es un **resultado montado** (mezcla, secuencia, retiming, repetición) que no existe ya como Action tal cual. No montes un NLA solo para "tener clips separados": eso ya lo hace el exportador.

---

## 10. Snippet — montar un stack NLA por API (MCP/headless)

```python
import bpy
obj = bpy.context.object                         # armature con animation_data
ad  = obj.animation_data or obj.animation_data_create()

walk    = bpy.data.actions["Walk"]
breathe = bpy.data.actions["Breathe"]            # autorada como delta

# Track base
base = ad.nla_tracks.new()                        # (prev=None)
base.name = "Base"
s_walk = base.strips.new(name="Walk", start=1, action=walk)  # (name, start:int, action)
s_walk.blend_type   = 'REPLACE'
s_walk.extrapolation = 'HOLD'
s_walk.repeat = 4                                 # 4 ciclos

# Track additive encima
add = ad.nla_tracks.new(prev=base)               # nuevo track por encima del base
add.name = "Additive"
s_br = add.strips.new(name="Breathe", start=1, action=breathe)
s_br.blend_type = 'ADD'                            # o 'COMBINE'
s_br.use_auto_blend = True
# 5.2 Slotted Actions: si la Action tiene varios slots, fija el correcto:
# s_br.action_slot = breathe.slots[0]
```
- `nla_tracks.new(prev=None)` añade sobre el `prev` dado (orden = precedencia). `strips.new(name, start, action)` crea un Action strip. Verificado en la API `NlaTracks`/`NlaStrips` de 5.2.
- Para Push Down por operador (necesita contexto de área NLA): `bpy.ops.nla.action_pushdown(track_index=-1)`.

---

## Reglas prácticas

- [ ] Para exportar clips separados a Unity, **`All Actions` con Actions sueltas** es la ruta por defecto; el NLA solo si el clip es un resultado montado.
- [ ] Nombra cada Action = nombre del clip en Unity (`Categoria_Accion_Variante`); el AnimStack hereda ese nombre [ver: animacion3d/capas-estados §8].
- [ ] Define **Manual Frame Range** por Action para que el exporter tome el rango correcto (y excluya frames basura).
- [ ] Export a Unity: `add_leaf_bones=False`, `bake_anim_step=1.0`, `bake_anim_simplify_factor=0.0`; deja la reducción de keys al import de Unity [ver: export-clips-unity].
- [ ] Elige UNA ruta multi-clip: `bake_anim_use_all_actions` **o** `bake_anim_use_nla_strips`, no ambas.
- [ ] El `blend_type`/influencia/stack del NLA **no viaja al FBX**: si el clip es la mezcla de tracks, **hornea** primero y exporta la Action plana.
- [ ] Additive en NLA = `Add` o `Combine`, y la Action debe ser un **delta** respecto a la pose de referencia, nunca pose absoluta.
- [ ] `Combine` para additive de rotaciones/escala (elige la math correcta); cuenta con que cuaternión driva los 4 canales.
- [ ] Extrapolación: `Hold`/`Hold Forward` al secuenciar; `Nothing` (o Blend a 0) para additive acotado.
- [ ] Retiming: `Scale` (S) pivota en el Playhead; `Apply Scale` (Ctrl-A) para fijar; recorta con `action_frame_start/end`, no re-keyees.
- [ ] Reuso: `Linked Duplicate` (Shift-D) comparte la Action; `Make Single User` (U) la desliga antes de editar.
- [ ] Orden de tracks = precedencia (arriba manda). Usa **Solo** (estrella) para inspeccionar un track aislado sin borrar nada.
- [ ] Editar la Action de un strip: `Tab` (Tweak Mode); usa **Lower Stack** o **Solo** para no ver el ruido de tracks superiores.
- [ ] Hornea (Bake Action) con `visual_keying=True` cuando hay constraints/IK/drivers/modifiers de curva que no viajan al export.
- [ ] Tras hornear, `clean_curves=True`; hornear crea 1 key/frame — no lo confundas con animación limpia.
- [ ] 5.2: al recorrer Actions por script cuenta con **Slots** (Action + Slot) y con las layers/strips internas expuestas solo en la API [ver: sistema-animacion].
- [ ] Verifica el clip **ya importado en Unity**, no solo el stack del NLA: lo que exporta es el sampling por frame, no tus tangentes finas [ver: animacion3d/keyframes-curvas §9].

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Montar un NLA elaborado solo para "tener clips separados" | El exporter ya hace 1 clip por Action con `All Actions`; usa Actions sueltas |
| Exportar con `NLA Strips` esperando el resultado MEZCLADO del stack | `NLA Strips` exporta cada strip **por separado**; hornea el stack a una Action y expórtala |
| Additive que deforma el modelo (dobla doble) | La Action additive es pose absoluta; recréala como **delta** respecto a la pose de referencia [ver: animacion3d/capas-estados §5.1] |
| El additive se "queda pegado" fuera de su ventana | Extrapolación en `Nothing` o Blend In/Out; no dejes `Hold` en un delta |
| Ciclo con modificador Cycles/Noise que llega plano a Unity | Los F-Curve modifiers no viajan al FBX: **hornea** a keys reales [ver: animacion3d/keyframes-curvas §8] |
| Constraints/IK que no aparecen en el clip exportado | Bake Action con `visual_keying=True` (y `clear_constraints` si procede) |
| Editar los keys de un strip y romper otro sin querer | Era `Linked Duplicate` (Action compartida): `Make Single User` (U) antes de editar |
| Clip en Unity con nombre `Armature|Action`/`Take 001` | Nombra la Action antes de exportar; el AnimStack hereda el nombre |
| Rango de export incluye frames de más o de menos | Activa **Manual Frame Range** por Action; o `Force Start/End Keying` |
| Huesos hoja basura / rotaciones raras en Unity | `add_leaf_bones=False`, `primary_bone_axis='Y'`, `secondary_bone_axis='X'` |
| Curvas densísimas tras hornear todo "por si acaso" | No hornees Actions ya limpias; deja el sampling al exporter y la reducción a Unity |
| Escalar un strip y creer que "va más lento" por keys juntas | El scale cambia la velocidad de muestreo; la lentitud es cambio de valor/frame [ver: animacion3d/keyframes-curvas §5] |
| Script que ignora Slots y no anima nada (5.2) | El strip enlaza Action **+ Slot**; asigna `action_slot`/`action_slot_handle` al del tipo correcto |

## Fuentes

**Bases sintetizadas (repo El Estudio) — cross-referenciadas, no repetidas:**
- [ver: animacion3d/capas-estados] — additive vs override, delta sobre pose de referencia, el grafo de estados/capas; este archivo es su ejecución en el NLA de Blender + export.
- [ver: animacion3d/keyframes-curvas] — craft de curvas/tangentes, modificadores de ciclo, y qué sobrevive al sampling del import de Unity.
- [ver: animacion3d/ciclos-locomocion] · [ver: animacion3d/animacion-combate] — la técnica de los clips que aquí se montan/exportan.
- [ver: unity/animacion-unity] — consumo del clip en Unity (Animator, layers, blend trees, import).
- Hermanos en animacion-blender: [ver: sistema-animacion], [ver: actions-organizacion], [ver: bake-animacion], [ver: export-clips-unity], [ver: graph-editor], [ver: animacion-blender-operativo].

**Fuentes web verificadas (curl 200 esta sesión, 2026-07-20; docs.blender.org/manual/en/latest = Blender 5.2):**
- **Blender Manual — NLA Introduction** (`editors/nla/introduction.html`) — editor de acciones, stack de tracks (arriba manda o mezcla), Action Track naranja = acción activa, Tweak Mode (Tab), Add menu (Action/Transition/Sound/Selected Objects), Snap, Animated Influence.
- **Blender Manual — NLA Tracks** (`editors/nla/tracks.html`) — Mute/Solo/Lock, Disable NLA stack, Action Track, **Push Down Action**, Pin.
- **Blender Manual — NLA Strips** (`editors/nla/strips.html`) — Action/Transition/Sound/Meta strips; un strip puede recortar/estirar/repetir su Action.
- **Blender Manual — Editing Strips** (`editors/nla/editing/strip.html`) — Move/Extend/Scale/Split/Swap/Duplicate/Linked Duplicate/Make Single User/Make Meta/Toggle Muting, y **Bake Action** con todos sus parámetros.
- **Blender Manual — Editing Tracks** (`editors/nla/editing/track.html`) — Add / Add Above Selected / Move / Delete / Remove Empty Animation Data.
- **Blender Manual — NLA Sidebar** (`editors/nla/sidebar.html`) — Active Strip (Frame Start/End, Blend In/Out, Auto Blend, Reversed, Cyclic Strip Time), **Blending** (Replace/Add/Subtract/Multiply/Combine con fórmulas), **Extrapolation** (Nothing/Hold/Hold Forward), Influence, Animated Influence/Strip Time, Action Clip (Action/Slot/Frame Start-End/Sync Length/Playback Scale/Repeat), Modifiers.
- **Blender Manual — Actions** (`animation/actions/index.html`) — Actions como contenedor, **Action Slots** (Slotted Actions 4.4+), layers/strips internos NO en UI pero SÍ en Python API, Manual Frame Range, Cyclic Animation, Replace Action / Remap Users.
- **Blender Manual — FBX / FBX (Legacy) exporter** (`files/import_export/fbx.html`, `fbx_legacy.html`) — panel Bake Animation, "Saving Just Animations" (solo takes), Key All Bones / NLA Strips / All Actions.
- **Blender Python API 5.2** (`bpy.ops.export_scene`, `bpy.ops.nla`, `bpy.types.NlaTracks`/`NlaStrips`/`NlaStrip`) — firmas y tooltips **exactos**: `export_scene.fbx(bake_anim_use_nla_strips/…_all_actions/…_all_bones/…_force_startend_keying/…_step/…_simplify_factor)`; `nla.bake(frame_start,end,step,only_selected,visual_keying,clear_constraints,clear_parents,use_current_action,clean_curves,bake_types,channel_types)`; `nla.action_pushdown(track_index)`, `nla.tweakmode_enter(isolate_action,use_upper_stack_evaluation)/tweakmode_exit`; `nla_tracks.new(prev)`, `strips.new(name,start,action)`; atributos `NlaStrip.blend_type`/`extrapolation`/`influence`/`use_animated_influence`/`blend_in`/`blend_out`/`use_auto_blend`/`action_frame_start`/`action_frame_end`/`scale`/`repeat`/`use_sync_length`/`use_reverse`/`use_animated_time`/`action_slot`/`action_slot_handle`.

**No verificado esta sesión (honestidad):**
- El comportamiento exacto del **import de cada AnimStack como AnimationClip en Unity 6** se apoya en el lenguaje del propio exporter ("separated FBX's AnimStack") + las bases; la config de import (split, read-only, compresión) se detalla y verifica en [ver: export-clips-unity] / [ver: unity/animacion-unity], no re-verificada contra docs.unity.com aquí.

**Corregido en la auditoría (2026-07-20), verificado contra `docs.blender.org` en vivo (curl, esta sesión):**
- La etiqueta **"LTS"** de Blender 5.2 SÍ está confirmada: las páginas del manual `latest` titulan literalmente "Blender 5.2 LTS Manual" (`fbx.html`, `sidebar.html`, `actions.html`, `fbx_legacy.html`).
- El atributo correcto es **`NlaStrip.action_slot_handle`**, no `slot_handle` (`bpy.types.NlaStrip` — el nombre corto no existe).
- `nla.tweakmode_enter()` **sin argumentos** usa el default `use_upper_stack_evaluation=False`, que es el comportamiento de **Lower Stack**, no Full Stack; para Full Stack (Tab, comportamiento por defecto de la UI) hay que pasar `use_upper_stack_evaluation=True` explícitamente.
- `bpy.ops.nla.bake()` tiene además el parámetro `clear_parents` (bool) — "Bake animation onto the object then clear parents (objects only)" — no listado antes en la tabla de §7.
- El panel *Bake Animation* del exportador FBX vive hoy en la página del manual **"FBX (Legacy)"** (`files/import_export/fbx.html#export` remite a `fbx_legacy.html`); la página "FBX" nueva documenta solo el **Import**. El operador Python sigue siendo el mismo `bpy.ops.export_scene.fbx` — no cambia nada operativo, pero explica por qué la prosa narrativa del panel es escasa (solo *All Actions* tiene descripción en el manual; el resto son tooltips del operador, como ya anotaba este archivo).
