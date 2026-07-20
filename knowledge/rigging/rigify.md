# Rigify: rig automático

> **Cuando cargar este archivo:** al riggear un personaje (biped o no-biped) con Rigify para llevarlo a Unity — generar el rig desde un metarig, skinnearlo, o resolver el problema de que Rigify produce cientos de huesos de control/mecanismo que NO deben ir al motor. También al decidir Rigify vs rig manual vs Auto-Rig Pro.

Verificado contra **Blender 5.2 LTS** (Rigify es add-on **integrado y gratis** — activarlo, no instalarlo [ver: blender/addons-ecosistema]), **Unity 6** (Humanoid/Generic/Mecanim) y **Auto-Rig Pro 2026**. Rigify vive en `scripts/addons_core/rigify`; se activa en `Preferences ▸ Add-ons ▸ buscar "Rigify" ▸ Enable`. Este archivo es el flujo de rig concreto: la teoría de armatures, weights, deformación e IK/FK está en sus archivos [ver: esqueletos-armature] [ver: skinning-weights] [ver: deformacion] [ver: ik-fk-constraints].

---

## 1. Qué es y qué NO es

Rigify convierte un **metarig** (armature simple, un esqueleto de referencia) en un **rig completo** con controles, IK/FK, snapping y una UI en la barra lateral — en un clic. Principio de diseño clave del manual: **una vez generado, el rig ya no necesita Rigify** — se puede distribuir a máquinas sin el add-on y sigue funcionando (todo es constraints/drivers nativos).

Lo que Rigify **NO** hace (manual, textual): *"Rigify only automates the creation of the rig controls and bones. It does not attach the rig to a mesh, so you still have to do skinning etc. yourself."* → el skinning/weight paint es tuyo [ver: skinning-weights]. Tampoco retargetea animación ni auto-skinnea (ahí gana Auto-Rig Pro, §8).

---

## 2. El flujo en 3 pasos (manual: "Basic Rig Generation")

1. **Add ▸ Armature** (`Shift-A`) → elegir un metarig predefinido.
2. **Ajustar** las posiciones de los huesos del metarig al mesh.
3. En **Properties ▸ Armature (Object Data) ▸ Generate Rig** → genera el rig.

Operador de generación: `bpy.ops.pose.rigify_generate()` (con el metarig activo). La generación tarda de segundos a ~1 minuto; el UI de Blender se congela hasta terminar (es Python) — esperar a que aparezca el `rig`.

### Metarigs disponibles (menú Add ▸ Armature)

| Metarig | Tipo | Nota |
|---|---|---|
| **Human** | Biped completo | Cuerpo + cara + dedos. El caballo de batalla |
| **Basic Human** | Biped | Sin cara ni dedos (más ligero para juegos) |
| **Basic Quadruped** | No-biped | Base para cuadrúpedos |
| **Cat / Wolf / Horse / Shark** | No-biped | Metarigs de animales listos [ver §7] |

Un metarig es un ensamblaje de **sub-rigs** (brazo, pierna, espina, dedos…); se pueden mezclar libremente ("cinco brazos y una pierna" — el manual lo dice literal). Construir uno propio: partir de `Add ▸ Armature ▸ Single Bone`, nombrarlo `metarig`, y en `Edit Mode` añadir samples (`Armature tab ▸ Rigify panel ▸ Add sample`) o asignar tipos por hueso (`Pose Mode ▸ Bone ▸ Rigify Type`).

### Ajustar el metarig al mesh

- **Escala:** Rigify asume **1 unidad = 1 metro** (un humano ≈ 2 unidades de alto). Si el personaje está a otra escala, escalarlo en Object Mode y **aplicar la escala** (`Ctrl+A ▸ Scale`) ANTES de posicionar huesos — la escala sin aplicar arruina la deformación y el export [ver: blender/import-export].
- **Dos métodos** (manual): **Pose Mode** (rotar/escalar/mover huesos, luego `Pose ▸ Apply ▸ Apply Pose As Rest Pose` = `bpy.ops.pose.armature_apply()`) o **Edit Mode** (mover cabezas/colas directamente; activar X-Ray + Display ▸ Wireframe + Armature ▸ Axes para ver rolls).
- **Tips de alineación humana:** piernas rectas en vista frontal con una **ligera flexión** en rodilla/codo (Rigify infiere el eje de flexión de ahí — desde v0.5 ya no hay que alinear rolls a mano en las extremidades). Espina lo más recta posible.
- **Cara:** si vas a animar la cara con **shape keys/blendshapes** (lo normal en juegos [ver: blender/import-export]), los huesos de cara son casi inútiles → **borrarlos**: seleccionar todo en la bone collection `Face` y eliminar en Edit Mode. Reduce drásticamente el conteo de huesos.
- **Merge points:** donde cabezas/colas de varios huesos coinciden, deben seguir coincidiendo tras mover — romperlos genera controles duplicados o errores de generación.

---

## 3. La estructura generada: ORG / DEF / MCH / controles

Al generar, aparece un objeto armature llamado `rig` con **cientos de huesos** organizados en capas (bone collections). Solo una fracción deforma el mesh. Los cuatro roles, por **prefijo de nombre** y **bone collection**:

| Prefijo | Bone collection | Rol | ¿Deforma? | ¿Va a Unity? |
|---|---|---|---|---|
| *(sin prefijo)* | Colecciones visibles (Torso, Arm.L, Fingers…) | **Controles** — lo que agarra el animador: `torso`, `chest`, `hand_ik.L`, `upper_arm_fk.L`, `root` | No | **No** |
| `ORG-` | `ORG` (oculta) | **Original** — copias de los huesos del metarig; capa de referencia intermedia entre controles y deform | No | **No** |
| `MCH-` | `MCH` (oculta) | **Mechanism** — huesos auxiliares de la maquinaria: solvers IK, pole, stretch, switching FK/IK | No | **No** |
| `DEF-` | `DEF` (oculta) | **Deform** — los **únicos** con el flag Deform activo; llevan los vertex groups/weights | **Sí** | **Sí — solo estos** |

Confirmado por el manual: *"All the deforming bones are in the DEF bone collection"* (basics) y se nombran las colecciones internas `ORG`, `DEF` y `MCH` (metarigs). Las expansiones quedan confirmadas en el **código fuente** de Rigify (`rigify/utils/naming.py`, repo `blender-addons`): `ORG_PREFIX = "ORG-"  # Prefix of original bones.` / `MCH_PREFIX = "MCH-"  # Prefix of mechanism bones.` / `DEF_PREFIX = "DEF-"  # Prefix of deformation bones.` / `ROOT_NAME = "root"`.

**El `root`:** todo rig de Rigify tiene un hueso `root` (colección `Root`) que es padre de todo, en el origen del objeto. Es el que Unity puede usar como raíz del esqueleto / root motion [ver: rig-a-unity].

**Cadena de mando (por qué hay tantos huesos):** el animador mueve un **control** → una red de huesos `MCH-`/`ORG-` con constraints traduce eso → los `DEF-` copian el resultado y deforman el mesh. Los `DEF-` de una extremidad suelen venir **segmentados** (`DEF-upper_arm.L`, `DEF-upper_arm.L.001`…) para repartir el twist, y usan **Bendy Bones** para curvar suave. Esa segmentación y los B-Bones son la fuente de fricción al exportar (§5–§6).

---

## 4. Skinning al rig de Rigify

Rigify **no** skinnea — lo haces tú [ver: skinning-weights]. Flujo game-ready:

1. Seleccionar el **mesh**, luego con `Shift` el **rig** (rig activo).
2. `Ctrl+P ▸ With Automatic Weights` → `bpy.ops.object.parent_set(type='ARMATURE_AUTO')`. Blender añade el Armature modifier y crea vertex groups **solo para los huesos con Deform on** = los `DEF-` (nunca ORG/MCH/controles). Por eso los grupos que ves son los `DEF-`.
3. Weight paint / corregir [ver: skinning-weights]. El manual: automatic weights funciona bien "if you correctly place your bones and there is enough topology".
4. Para juegos: **limitar a 4 influencias por vértice** y normalizar (Unity usa 4 huesos/vértice por defecto). Ver snippet §9.

⚠️ Los huesos de ojos/dientes de la cara *legacy* NO deforman: se bindean con constraints `Child Of`, no con weights.

---

## 5. El problema del export game-ready (el núcleo)

Rigify genera **cientos** de huesos (control + ORG + MCH + DEF). Un FBX crudo del rig completo mete TODA esa jerarquía en Unity: esqueleto gigantesco, imposible de mapear a Humanoid, coste de skinning/animación disparado. **Regla: a Unity solo deben llegar los `DEF-`.**

Aviso importante: **Rigify de Blender 5.2 NO tiene botón "Rigify to game engine".** Ese script existía en la era 2.7x y desapareció. Hoy hay tres caminos honestos:

### Camino A — Export "Only Deform Bones" (vanilla, gratis, 0 addons)

El exportador FBX filtra por el flag Deform: activar **Armature ▸ Only Deform Bones** (`use_armature_deform_only=True`) exporta **solo los `DEF-`** y descarta control/ORG/MCH. Los constraints que mueven los DEF se **hornean a keyframes** en el export (bake animation), así que la animación sobrevive sin la maquinaria. Combinar SIEMPRE con `add_leaf_bones=False` [settings completos ver: blender/import-export].

- **Ventaja:** cero dependencias, la fuente sigue siendo el rig full-Rigify (animas cómodo, exportas limpio).
- **Límites:** los `DEF-` segmentados (`.001`) SÍ se exportan como huesos reales (suben el conteo, pero conservan el twist); la **curvatura Bendy Bone NO se exporta** — el FBX no soporta B-Bones, Unity recibe deformación lineal (§6). El esqueleto DEF resultante no siempre tiene la jerarquía anatómica "limpia" que Humanoid espera → a veces requiere Generic o limpieza.

### Camino B — Game Rig Tools (addon community, CGDive)

Addon **gratis (pay-what-you-can en Gumroad; ~$15 en otros markets)** que **extrae un "Game Rig" a partir de un Control Rig existente** (incluido Rigify): genera un esqueleto deform limpio y trae **Action Bakery** para hornear las animaciones al Game Rig y exportarlas a "Unreal, Unity, Godot etc." Sus defaults "hacen el 80–90% del trabajo". Es el puente estándar de la comunidad cuando el Camino A se queda corto. (Precios/detalles caducan — verificar en su página antes de recomendar.)

### Camino C — Auto-Rig Pro (de pago, nace game-ready)

ARP tiene exportador de juego **dedicado** (`File ▸ Export ▸ Auto-Rig Pro FBX/GLTF`) que produce el esqueleto deform directamente (§8). Si haces varios personajes, es lo que muchos estudios usan.

---

## 6. Rigify → Unity: Humanoid vs Generic

Una vez el FBX deform-only está en Unity, en **Model importer ▸ Rig tab ▸ Animation Type**:

| | **Humanoid** | **Generic** |
|---|---|---|
| Qué hace | Mapea el esqueleto a un **Avatar** estándar humano → retargeting entre personajes, IK humanoide, Mecanim | Usa el esqueleto **tal cual**, sin retarget |
| Requisitos | ≥ **15 huesos** conformando un humano; personaje en **T-pose**; huesos nombrados por parte del cuerpo | Ninguno especial; se elige **Root node** |
| Coste runtime | Más caro (recalcula músculos cada frame) | **Más barato** [ver: unity/animacion-unity] |
| Cuándo | Personaje humano que comparte animaciones / usa packs de mocap | No-biped, o biped que no necesita retarget |
| Root motion | Usa el **Body Transform** (centro de masa) | Usa el hueso del **Root Node** |

**Configurar el Avatar Humanoid:** `Avatar Definition = Create From This Model` (por defecto) → **Configure…** entra al Avatar Mapping. Check verde = mapeo automático OK; **X roja** = falló y no se crea el Avatar. Los DEF de Rigify mapean bien porque siguen la anatomía humana. Herramientas: `Pose ▸ Enforce T-Pose` (Rigify genera en la pose de reposo del metarig — si no es T-pose exacta, forzarla), círculos **sólidos** = huesos requeridos, **punteados** = opcionales (Unity los interpola). Guardar el mapeo con `Mapping ▸ Save` (`.ht`) para reusarlo en el resto de personajes con el mismo esqueleto.

**Twist bones:** los `DEF-...001` de twist de Rigify van a los slots **opcionales** UpperArm/LowerArm/Thigh/Calf Twist del Avatar (o quedan sin mapear y deforman igual como huesos sueltos). El aviso de ARP aplica también aquí: Humanoid tiene **soporte limitado de huesos extra** y no siempre respeta todos los twist — si el twist es crítico, evaluar **Generic**.

**Optimize Game Objects** (Rig tab, checkbox): elimina la jerarquía de GameObjects del esqueleto (menos Transforms = más rápido) y expone solo los que declares en **Extra Transforms to Expose** — ahí van los sockets/attach points [sockets ver: blender/import-export]. Recomendado para personajes de juego.

**Escala y ejes:** las reglas de FBX (Apply Scalings = FBX Units Scale, `Ctrl+A` transforms, Add Leaf Bones OFF, el -89.98° aceptable en rigged) están en [ver: blender/import-export] — no se repiten aquí. El detalle del handoff de animación (clips, convención `modelo@anim.fbx`, Animator/blend trees) en [ver: unity/animacion-unity].

---

## 7. Rigify para no-bípedos (mención)

Metarigs `Cat`, `Wolf`, `Horse`, `Shark` + `Basic Quadruped` cubren cuadrúpedos y criaturas. Mismo flujo (ajustar, generar, DEF-only al exportar). En Unity un no-biped va casi siempre a **Generic** (Humanoid exige anatomía humana). Para criaturas fuera de los presets, ensamblar un metarig propio con sub-rigs (`spine`, `limbs.leg`, `limbs.simple_tentacle` para colas/tentáculos, `spines.basic_tail`). Rigs de máquinas/props sin anatomía → normalmente rig manual, no Rigify [ver: rigs-mecanicos].

---

## 8. Rigify vs rig manual vs Auto-Rig Pro (comparativa honesta)

| Criterio | **Rig manual** [ver: rigging-en-blender-operativo] | **Rigify** (integrado, gratis) | **Auto-Rig Pro** (~US$40–50, jul-2026 [ver: blender/addons-ecosistema]) |
|---|---|---|---|
| Coste | 0 | 0 (viene con Blender) | De pago |
| Velocidad de rig | Lento, todo a mano | Rápido (metarig → 1 clic) | El más rápido (**Smart** auto-detecta huesos con pocos clics) |
| Curva | Total control, mucho conocimiento | "Developer tool", curva empinada, errores de generación frecuentes | La más amigable |
| Auto-skinning | Manual | **No** (skinning es tuyo) | **Sí** — Easy Weight Binding, evita errores de bone heat |
| Retargeting | Manual | **No** | **Sí** (Remap) |
| Export a juego | Tú decides el esqueleto (más simple) | **Sin exportador dedicado** → Camino A/B (§5) | **Exportador de juego dedicado**, nace game-ready |
| Cara | A mano | Cara predefinida modular | Extiende la cabeza para facial |
| Cuándo | Esqueleto simple/mecánico, control absoluto, pocos huesos | Un personaje o pocos, presupuesto 0, ya tienes Blender | Varios personajes, pipeline de juego serio, quieres retarget+auto-skin |

**Veredicto (CGDive, resumido):** ARP gana claramente en **game dev** por export dedicado + auto-skin + retarget; Rigify gana si necesitas **gratis** y no requieres esas tres cosas. Para **un** personaje con presupuesto 0, Rigify + Camino A es perfectamente válido. Para producción con muchos personajes, ARP se paga solo [ver: blender/addons-ecosistema].

### Limitaciones de Rigify para juegos (por qué estudios van a ARP)

1. **Sin export game-ready nativo** — hay que limpiar a mano (DEF-only) o meter un addon (§5).
2. **Bendy Bones no viajan** — la deformación suave DEF se pierde en el FBX; Unity ve deformación lineal.
3. **Conteo de huesos alto** aun en DEF-only (segmentos de twist) — vigilar el límite de bones/skin de la plataforma móvil.
4. **No auto-skinnea ni retargetea** — dos pasos manuales que ARP automatiza.
5. **Curva/errores** — la generación falla con posiciones "raras" del metarig (merge points rotos, ejes mal).

---

## 9. Snippets bpy (headless / MCP) [ver: rigging-en-blender-operativo]

```python
import bpy

# --- 1. Añadir metarig Human y generar ---
# id confirmado en el codigo fuente (rigify/metarig_menu.py, create_metarig_ops):
#   op_type.bl_idname = "object.armature_" + name + "_metarig_add"  (name="human" para Human)
# Patrón general: object.armature_<nombre_archivo_metarig>_metarig_add
bpy.ops.object.armature_human_metarig_add()      # Human (biped completo)
metarig = bpy.context.active_object
metarig.name = "metarig"
# ... aquí: ajustar posiciones de huesos al mesh (Edit/Pose Mode) ...
bpy.ops.pose.rigify_generate()                    # genera el objeto 'rig'
rig = bpy.context.active_object                   # el rig queda activo
```

```python
# --- 2. Aplicar escala del personaje ANTES de posicionar (1 u = 1 m) ---
mesh = bpy.data.objects["Character"]
bpy.context.view_layer.objects.active = mesh
mesh.select_set(True)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
```

```python
# --- 3. Skinning: parent con pesos automáticos (crea grupos DEF-) ---
mesh = bpy.data.objects["Character"]; rig = bpy.data.objects["rig"]
bpy.ops.object.select_all(action='DESELECT')
mesh.select_set(True); rig.select_set(True)
bpy.context.view_layer.objects.active = rig       # el rig debe ser el activo
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
```

```python
# --- 4. Game-ready: limitar a 4 influencias y normalizar ---
bpy.context.view_layer.objects.active = mesh
bpy.ops.object.vertex_group_limit_total(group_select_mode='ALL', limit=4)
bpy.ops.object.vertex_group_normalize_all(group_select_mode='ALL', lock_active=False)
```

```python
# --- 5. Export FBX deform-only (solo DEF-) para Unity ---
bpy.ops.object.select_all(action='DESELECT')
mesh.select_set(True); rig.select_set(True)
bpy.ops.export_scene.fbx(
    filepath=bpy.path.abspath("//export/Character.fbx"),
    use_selection=True,
    object_types={'ARMATURE', 'MESH'},
    add_leaf_bones=False,                 # sin huesos _end basura
    use_armature_deform_only=True,        # <-- SOLO los DEF-; descarta control/ORG/MCH
    apply_scale_options='FBX_SCALE_UNITS',
    mesh_smooth_type='FACE',
    bake_anim=True,                        # hornea los constraints de Rigify a keyframes
)
```

Operadores verificados como estables: `pose.rigify_generate`, `pose.armature_apply`, `object.parent_set('ARMATURE_AUTO')`, `object.vertex_group_limit_total`, `export_scene.fbx`. El id `armature_human_metarig_add` está confirmado contra el **código fuente** de `rigify/metarig_menu.py` (no solo inferido); si el add de OTRO metarig falla, el patrón es `object.armature_<nombre_archivo_del_metarig>_metarig_add` (ej. `basic_quadruped`, `wolf`) — confirmar con hover si hay duda de nombre exacto de archivo.

---

## Reglas practicas

- [ ] Activar Rigify en `Preferences ▸ Add-ons` (integrado, no se instala) [ver: blender/addons-ecosistema].
- [ ] Personaje a **1 unidad = 1 metro** y **escala aplicada** (`Ctrl+A ▸ Scale`) ANTES de posicionar el metarig.
- [ ] Elegir el metarig más ligero que sirva: **Basic Human** o **borrar los huesos de cara** si la cara va por blendshapes.
- [ ] Ligera flexión en codo/rodilla en el metarig (Rigify infiere el eje IK); respetar merge points.
- [ ] Guardar el `.blend` con el metarig y el rig juntos: re-generar (`pose.rigify_generate`) reusa modificadores/constraints; nunca borres el metarig.
- [ ] Skinning: `Ctrl+P ▸ With Automatic Weights` → los grupos son los `DEF-` (los únicos con Deform on).
- [ ] Limitar a **4 influencias/vértice** + normalizar antes de exportar (límite de Unity).
- [ ] A Unity **solo los `DEF-`**: FBX con `use_armature_deform_only=True` + `add_leaf_bones=False`.
- [ ] Aplicar reglas de FBX/escala/ejes [ver: blender/import-export]; validar en Unity, no solo "el export no dio error".
- [ ] Unity: **Humanoid** si hay retarget/mocap (T-pose + ≥15 huesos + Configure); **Generic** si no-biped o twist crítico o quieres menos coste.
- [ ] Activar **Optimize Game Objects** y exponer solo los sockets necesarios.
- [ ] Guardar el mapeo Humanoid (`.ht`) para reusarlo en el resto de personajes del mismo esqueleto.
- [ ] Si el Camino A (deform-only) se queda corto: **Game Rig Tools** (gratis) o **Auto-Rig Pro** (de pago) — no reinventar el limpiado a mano.
- [ ] No-biped → casi siempre **Generic** en Unity.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Exportar el rig Rigify completo → esqueleto de cientos de huesos en Unity | `use_armature_deform_only=True`: solo llegan los `DEF-` |
| Buscar el botón "Rigify to game engine" | No existe en 5.2 (era de 2.7x): usar Camino A/B/C (§5) |
| Mapear a Humanoid falla (X roja) | Faltan ≥15 huesos o no está en T-pose: `Pose ▸ Enforce T-Pose`, o pasar a Generic |
| Deformación "acartonada"/lineal en Unity vs Blender | Los Bendy Bones no viajan al FBX; es limitación conocida — aceptar o añadir más geometría/twist bones DEF |
| Weights repartidos entre ORG/MCH/control | Imposible con Automatic Weights (solo crea grupos DEF); si aparecen, alguien pintó a mano en huesos equivocados |
| Escala del personaje sin aplicar antes de rig | Deformación y export rotos: `Ctrl+A ▸ Scale` primero (1 u = 1 m) |
| Twist raro / codo colapsa en Unity Humanoid | Humanoid ignora/limita huesos extra: mapear los `DEF-...001` a los slots Twist o usar Generic |
| Borrar el metarig tras generar | Se pierde poder re-generar y adaptarse a versiones nuevas de Blender/Rigify — conservarlo |
| Vértices con >4 influencias | `vertex_group_limit_total(limit=4)` + normalizar antes de exportar |
| Merge points del metarig rotos al posicionar | Generan controles duplicados o abortan la generación: mantener cabezas/colas coincidentes |
| Root motion no avanza en Unity | Humanoid usa el Body Transform; Generic el Root Node — configurar el Root correcto y `Apply Root Motion` [ver: unity/animacion-unity] |

## Fuentes

- **Blender 5.2 Manual — Rigify: Introduction / Basic Usage / Generated Rig Features / Creating Meta-rigs / Bone Positioning Guide** — docs.blender.org (`addons/rigify/*`) — qué es Rigify, flujo add-ajustar-generate, `pose.rigify_generate`, colección `DEF` = deform, colecciones internas `ORG`/`DEF`/`MCH`, `root`, metarigs (Human/Basic Human/Basic Quadruped/Cat/Wolf/Horse/Shark), 1 u = 1 m, Apply Pose As Rest Pose, borrar cara, merge points.
- **Rigify — código fuente (verificado esta sesión vía `projects.blender.org/blender/blender-addons`, commit `b42d68627734`)**: `rigify/utils/naming.py` — `ORG_PREFIX`/`MCH_PREFIX`/`DEF_PREFIX` con comentarios textuales "original bones"/"mechanism bones"/"deformation bones" y `ROOT_NAME = "root"`; `rigify/metarig_menu.py` (función `create_metarig_ops`) — construcción exacta del `bl_idname` de los operadores Add Metarig: `"object.armature_" + name + "_metarig_add"`, confirmando `object.armature_human_metarig_add` para el metarig Human.
- **Unity Manual (Unity 6) — Configuring the Avatar** (`ConfiguringtheAvatar.html`) — Animation Type Humanoid, Avatar Definition, Configure, ≥15 huesos, T-pose, Enforce T-Pose, check verde / X roja.
- **Unity Manual (Unity 6) — Avatar Mapping tab** (`class-Avatar.html`) — huesos requeridos (sólidos) vs opcionales (punteados), Mapping ▸ Save/Load `.ht`, Pose tools, Muscles & Settings.
- **Unity Manual (Unity 6) — Root Motion** (`RootMotion.html`) — Root Transform, Bake Into Pose, Humanoid Body Transform vs Generic Root Node.
- **Auto-Rig Pro — Documentation (Overview + Game Engine Export)** — lucky3d.fr (`ge_export_doc.html`) — Smart auto-detección, export Humanoid vs Universal, Check/Fix Rig, Rename for UE, Root Motion (c_traj), Full Facial, Limit Total Vertex Groups a 4, aviso de soporte limitado de huesos extra/twist en Humanoid.
- **CGDive — Game Rig Tools (Blender addon)** — cgdive.com — extrae un Game Rig de un Control Rig existente (Rigify incluido), Action Bakery, export a Unreal/Unity/Godot, pay-what-you-can.
- **CGDive — Rigify vs Auto-Rig Pro comparison** — cgdive.com — comparativa honesta: gratis vs ~US$40, export de juego, Smart Mode, auto-skinning, Remap/retarget, cara, veredicto para game dev.
- **Base sintetizada:** [ver: blender/addons-ecosistema] (Rigify integrado/gratis, ARP como addon de rigging para juegos), [ver: blender/import-export] (settings FBX exactos, Only Deform Bones, Add Leaf Bones OFF, escala/ejes, sockets), [ver: unity/animacion-unity] (Humanoid vs Generic, coste, avatar mask, Animator/blend trees, IK).
