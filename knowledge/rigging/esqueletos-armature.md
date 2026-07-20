# Esqueletos y armatures

> **Cuando cargar este archivo:** al construir o auditar el ESQUELETO (armature) de cualquier personaje o prop articulado para juego — crear huesos, fijar jerarquía padre-hijo, nombrar con simetría, orientar el roll, separar huesos de deformación de los de control, y dejar el rig listo para skinning y para el Humanoid de Unity. La topología de la malla que va DEBAJO del rig no se repite aquí [ver: modelado/organico-personajes]; el reparto de pesos es su propio archivo [ver: skinning-weights]; la mecánica de deformación fina [ver: deformacion]; IK/FK y constraints [ver: ik-fk-constraints]; el flujo bpy paso a paso [ver: rigging-en-blender-operativo].

## 1. Qué es un armature (modelo de datos)

Un armature es un **tipo de objeto** de Blender (como Mesh o Curve) cuya Object Data contiene una colección de **bones** (huesos). Es el andamio que deforma la malla; la malla no se toca, se mueve por debajo [ver: skinning-weights].

| Nivel | Qué es | Dónde se edita |
|---|---|---|
| Armature **Object** | Transform (loc/rot/scale), origen, modificadores | Object Mode |
| Armature **Data** (`bpy.data.armatures`) | Los bones, display type, bone collections | Object Data Properties |
| **Edit Bones** (`obj.data.edit_bones`) | Geometría del hueso: head, tail, roll, parent, connect | **Edit Mode** (`Tab`) |
| **Pose Bones** (`obj.pose.bones`) | Pose/animación: rotación, constraints, drivers | **Pose Mode** (`Ctrl`-`Tab` en armature) |

- **Tres modos, tres verdades distintas** (el error nº1 del principiante): la estructura (huesos, longitudes, jerarquía) se define en **Edit Mode**; la pose/animación en **Pose Mode**; el objeto entero (posición en escena, escala) en **Object Mode**. `edit_bones` solo existe con el armature en Edit Mode; `pose.bones` solo tiene sentido tras salir de Edit. Modelo mental base de Blender: [ver: blender/interfaz-flujo §3].
- **Rest position vs Pose**: `data.pose_position = 'REST'` muestra el esqueleto sin animar (la "bind pose"); `'POSE'` aplica la pose actual. Skinnear y verificar deformación se hace comparando ambos.
- **Display type** (`data.display_type`): `OCTAHEDRAL` (default, muestra dirección y jerarquía), `STICK` (limpio para animar), `BBONE`, `ENVELOPE`, `WIRE`. `object.show_in_front = True` ("In Front") para ver los huesos a través de la malla mientras se riguea.

## 2. Anatomía de un bone: head, tail, roll

Cada hueso es un segmento con dos extremos y una torsión:

| Parte | Qué es | Propiedad bpy | Regla de juego |
|---|---|---|---|
| **Head** (root) | Base del hueso; el punto de **pivote** — el hueso rota alrededor de su head | `edit_bone.head` (Vector) | El head es donde vive la articulación (el codo real, no en medio del antebrazo) |
| **Tail** (tip) | Punta; solo apunta hacia dónde "mira" el hueso y hacia dónde se encadenan los hijos | `edit_bone.tail` | El tail del hueso padre marca dónde empieza el hijo conectado |
| **Length** | Distancia head→tail | `edit_bone.length` (read-derived) | Un hueso de longitud 0 es inválido; Blender no lo permite |
| **Roll** | Rotación del hueso sobre su propio eje longitudinal (Y) | `edit_bone.roll` (radianes) | Define los ejes X/Z locales → §5, crítico para deformación y para IK/constraints |

**Ejes locales del hueso** (la clave que casi nadie explica bien):

- El eje **Y local SIEMPRE va del head al tail** (a lo largo del hueso). No se puede cambiar: es la dirección del hueso.
- **Roll gira los ejes X y Z** alrededor de ese Y. Es decir: dos huesos idénticos en posición pueden tener X/Z apuntando a lados distintos si su roll difiere.
- Esos ejes X/Z locales son los que usan las rotaciones, los constraints, los pole targets de IK y el mirror de pose [ver: ik-fk-constraints]. Un roll inconsistente = un rig que se deforma torcido y en el que "rotar en X" significa cosas distintas en el brazo izquierdo y el derecho.
- Ver los ejes: Object Data Properties ‣ Viewport Display ‣ **Axes** (`data.show_axes = True`).

## 3. Jerarquía padre-hijo: connected vs free

El armature es un **árbol**: cada hueso tiene 0 o 1 padre y N hijos. Al posar/animar, el hijo hereda la transformación del padre (rotar el hombro arrastra todo el brazo). Hay **dos formas** de relación padre-hijo, y confundirlas es un clásico:

| Relación | `use_connect` | Comportamiento | Cuándo |
|---|---|---|---|
| **Connected** | `True` | El **head del hijo queda soldado al tail del padre** — no se puede mover por separado. Cadena rígida continua | Columna, dedos, cadenas donde no hay hueco entre huesos |
| **Keep Offset / Free** (disconnected) | `False` | El hijo hereda la transformación del padre pero su head es **libre** (puede haber un hueco). Sigue siendo hijo | Clavícula→brazo, cadera→pierna, hueso raíz→hips: donde hay separación física |

Operadores (Edit Mode):

| Acción | Atajo / menú | Operador bpy |
|---|---|---|
| Extruir hijo **connected** desde el tail seleccionado | `E` | `armature.extrude_move` |
| Extruir bifurcado (dos hijos) | `Shift`-`E` | `armature.extrude_forked` |
| Emparentar (selecc. hijos, luego padre activo) → **Connected** | `Ctrl`-`P` ‣ Connected | `armature.parent_set(type='CONNECTED')` |
| Emparentar → **Keep Offset** (free) | `Ctrl`-`P` ‣ Keep Offset | `armature.parent_set(type='OFFSET')` |
| Quitar padre (limpiar) | `Alt`-`P` ‣ Clear Parent | `armature.parent_clear(type='CLEAR')` |
| Desconectar del padre pero **mantener** la relación | `Alt`-`P` ‣ Disconnect Bone | `armature.parent_clear(type='DISCONNECT')` |
| Añadir hueso suelto en el 3D cursor | `Shift`-`A` | `armature.bone_primitive_add(name="Bone")` |

- Extruir con `E` crea **automáticamente un hijo connected** — es la forma rápida de trazar una cadena (columna, dedos).
- La convención de árbol se hereda del modelo mental de parenting general de Blender (`Ctrl`-`P`/`Alt`-`P`) [ver: blender/interfaz-flujo §5].

## 4. Naming conventions: la disciplina que ahorra horas

Los nombres de huesos NO son cosmética: activan la simetría de Blender **y** el auto-mapeo del Humanoid de Unity. Dos contratos que cumplir a la vez.

### 4a. Sufijos .L/.R para simetría en Blender

Blender reconoce tokens **Left/Right** con separador, insensible a mayúsculas, como prefijo o sufijo. Los recomendados para juego:

| Forma | Ejemplo | Nota |
|---|---|---|
| `.L` / `.R` (punto) | `Hand.L`, `Hand.R` | **La convención canónica de Blender**; la que usan Rigify y los operadores de auto-nombrado |
| `_L` / `_R` (guion bajo) | `Hand_L` | Válida; algunos engines/exporters la prefieren |
| `.Left`/`.Right`, `-L/-R`, ` L`/` R` | — | Reconocidas pero menos usadas |

Separadores válidos: `.`, `_`, `-`, espacio. Lo que **rompe** la simetría es un nombre sin token pareado (`LeftHand` sin separador antes de la parte lateral, o `armL` pegado) o mezclar convenciones dentro del mismo rig.

Operadores de simetría que dependen del naming (Edit Mode):

| Acción | Menú | Operador bpy |
|---|---|---|
| Auto-nombrar según posición en X (añade `.L`/`.R`) | Armature ‣ Names ‣ Auto-Name Left/Right | `armature.autoside_names(type='XAXIS')` |
| **Symmetrize** (duplica el lado seleccionado al opuesto, renombrando) | Armature ‣ Symmetrize | `armature.symmetrize(direction='NEGATIVE_X')` |
| Voltear nombres (`.L`↔`.R`) | Armature ‣ Names ‣ Flip Names | `armature.flip_names()` |
| **X-Axis Mirror** en Edit Mode (editar un lado edita el espejo) | header ‣ Options ‣ X-Axis Mirror | `data.use_mirror_x = True` |
| X-Axis Mirror en Pose Mode (posar simétrico) | Pose ‣ opción de mirror | `pose.use_mirror_x = True` |

Flujo estándar: riguear SOLO el lado izquierdo con `.L`, luego `armature.symmetrize()` para generar el derecho `.R` idéntico. El mismo naming propaga después al **mirror de weights** en skinning (los vertex groups también son `.L`/`.R`) [ver: skinning-weights].

### 4b. Naming que el Humanoid de Unity pueda mapear

Unity auto-mapea el esqueleto a su Avatar por **posición en la jerarquía + nombres descriptivos**. Verificado (Unity Manual, *Using Humanoid Characters*):

- Nombrar los huesos por la parte del cuerpo: `LeftArm`, `RightForearm`, etc. — descriptivo, no `Bone.042`.
- Para pares, convención consistente tipo `arm_L` / `arm_R` **"mejora el éxito del auto-match del Avatar"**.
- La jerarquía debe seguir la estructura anatómica natural: **`HIPS → spine → chest → shoulders → arm → forearm → hand`**.
- **Importante (Unity Manual, *Retargeting*):** una vez configurado el Avatar, retargetear entre personajes NO exige renombrar ni reestructurar — el Avatar desacopla nombres de datos. Es decir: el naming consistente ayuda al **auto-mapeo inicial**, no al retarget posterior. Aun así, nombres limpios se pagan solos: el auto-map falla → mapeo manual hueso por hueso.

## 5. Orientación y roll: por qué importa

El roll (§2) fija los ejes X/Z locales del hueso. Por qué un TD lo cuida:

1. **Deformación:** al mirror-copiar weights o pose, Blender asume que los ejes de `Hueso.L` y `Hueso.R` son espejo. Si el roll no es coherente entre lados, la pose espejada se tuerce.
2. **IK y constraints:** los pole targets, los límites de rotación y los ejes de "bend" de un IK dependen del eje local. Un antebrazo con roll arbitrario dobla el codo hacia un lado imprevisto [ver: ik-fk-constraints].
3. **Twist bones:** los huesos de torsión (antebrazo, muslo) reparten la rotación sobre su Y — solo funcionan si el roll está alineado con el hueso padre [ver: deformacion].
4. **Engine:** en un rig **Generic** de Unity los ejes locales del hueso viajan tal cual y determinan cómo rota cada bone. En **Humanoid**, Unity reconstruye su propio "muscle space" normalizado, así que abstrae parte del roll — pero un roll roto sigue apareciendo como pose de descanso torcida que ensucia el auto-map. No es excusa para descuidarlo.

**Recalcular roll** (Edit Mode, seleccionar huesos): `Ctrl`-`N` → `armature.calculate_roll(type=...)`. Tipos útiles:

| `type` | Alinea el eje Z del hueso a… | Uso |
|---|---|---|
| `GLOBAL_POS_Z` | +Z global (arriba) | Piernas, columna — el estándar más común |
| `GLOBAL_POS_X` | +X global | Brazos en T-pose |
| `POS_X` / `POS_Z` | +X / +Z local relativo | Ajuste fino |
| `ACTIVE` | El roll del hueso activo | Igualar una cadena al hueso de referencia |
| `VIEW` / `CURSOR` | La vista / el 3D cursor | Casos manuales |

Regla operativa: recalcular todo el esqueleto a una convención única (típico: `GLOBAL_POS_Z` para el cuerpo, brazos aparte a un eje coherente) y verificar visualmente con los ejes activados. El roll manual se ajusta en `N` ‣ Item ‣ Roll o con `Ctrl`-`R` (Set Roll) en algunos keymaps.

## 6. Deform bones vs control/mechanism bones

No todos los huesos deforman la malla. Un rig serio separa capas:

| Tipo | `use_deform` | Función | ¿Va al export? |
|---|---|---|---|
| **Deform** (`DEF-` en Rigify) | `True` | Deforman la malla; tienen vertex group asociado | **SÍ — los únicos que van** |
| **Control** (`CTRL`/widgets) | `False` | Los que el animador agarra (IK handles, master, root de control) | NO |
| **Mechanism** (`MCH-`) | `False` | Cálculo interno del rig (splines, correctores) | NO |
| **Original** (`ORG-`) | `False` | Referencia intermedia de Rigify | NO |

- El flag: Bone Properties ‣ **Deform** checkbox (`edit_bone.use_deform`). Solo los deform generan influencia de skinning; un control con Deform ON crearía un vertex group fantasma.
- **Al exportar a Unity solo salen los deform.** En el FBX export: **Only Deform Bones** ON (`use_armature_deform_only=True`) y **Add Leaf Bones** OFF (`add_leaf_bones=False`, si no mete huesos `_end` basura) — settings exactos y por qué en [ver: rig-a-unity] y [ver: blender/import-export §"Settings EXACTOS de export FBX"].
- Organizar las capas con **Bone Collections** (Blender 4.0+ reemplazó las 32 "bone layers"; los tutoriales viejos que enseñan `M` → mover a capa están obsoletos): `armature.collections.new("DEF")` y asignar. Se ocultan/muestran por colección mientras se riguea. La generación completa de estas capas la hace Rigify sola [ver: rigify].

## 7. Jerarquía estándar de un bípedo (mapa a Unity Humanoid)

Esqueleto mínimo de personaje y su correspondencia con los slots del Humanoid. Unity exige **≥ 15 huesos "que se ajusten aproximadamente a un esqueleto humano real"** (verificado, Unity Manual *Configuring the Avatar*). Los 15 obligatorios (conjunto estándar de Unity) marcados **REQ**:

| Hueso (convención) | Slot Unity Humanoid | Obligatorio |
|---|---|---|
| `Root` (a 0,0,0) | — (no es hueso Humanoid; sirve de raíz para root motion) | recomendado |
| `Hips` / `Pelvis` | Hips | **REQ** |
| `Spine` | Spine | **REQ** |
| `Chest` | Chest | opcional |
| `UpperChest` | Upper Chest | opcional |
| `Neck` | Neck | opcional |
| `Head` | Head | **REQ** |
| `Shoulder.L/.R` (clavícula) | Left/Right Shoulder | opcional |
| `UpperArm.L/.R` | Left/Right Upper Arm | **REQ** (×2) |
| `Forearm.L/.R` | Left/Right Lower Arm | **REQ** (×2) |
| `Hand.L/.R` | Left/Right Hand | **REQ** (×2) |
| `Thigh.L/.R` (UpperLeg) | Left/Right Upper Leg | **REQ** (×2) |
| `Shin.L/.R` (LowerLeg) | Left/Right Lower Leg | **REQ** (×2) |
| `Foot.L/.R` | Left/Right Foot | **REQ** (×2) |
| `Toe.L/.R` | Left/Right Toes | opcional |
| Dedos (3 huesos ×5 ×2 manos) | Left/Right fingers | opcional |
| `Eye.L/.R`, `Jaw` | Eyes / Jaw | opcional |

Cuenta de los REQ: Hips + Spine + Head (3) + brazos UpperArm/Forearm/Hand ×2 (6) + piernas Thigh/Shin/Foot ×2 (6) = **15**. Todo lo demás (chest, cuello, hombros, dedos, dedos del pie, ojos, mandíbula) es opcional pero mejora el retarget. *(La enumeración exacta de los 15 es el conjunto estándar de Unity; la página que la tabula no se pudo abrir esta sesión — ver `gaps`.)*

- **Bind pose:** modelar y riguear en **T-pose** (brazos rectos a los lados formando "T"). Unity la recomienda: da espacio a la geometría de axilas y facilita colocar el rig dentro de la malla (verificado, Unity Manual). El debate T-pose vs A-pose (~45°) se decide CON el modelador antes de retopologizar [ver: modelado/organico-personajes §5].
- **Piezas rígidas** (armadura, hebillas, props): un solo hueso adicional, weight 100% a él, sin deformar — coherente con [ver: modelado/organico-personajes §7] y [ver: rigs-mecanicos].

## 8. El hueso Root y el root motion

- Un **hueso raíz único** en el **origen del mundo (0,0,0)**, alineado a los ejes, del que cuelga todo (empezando por `Hips`). Es el estándar para que el engine tenga un ancla de esqueleto limpia.
- **Root motion en Unity** (verificado, Unity Manual *Root Motion*): el movimiento de la animación mueve el GameObject en vez de un script.
  - **Humanoid**: Unity calcula el "Root Transform" como proyección sobre el plano Y del **Body Transform** (centro de masa) — no necesitas designar hueso, lo deriva.
  - **Generic**: hay que designar un **Root Node** (el hueso raíz) como centro del esqueleto; todo lo demás queda relativo a él. Aquí el hueso Root del armature ES lo que eliges.
  - Se activa con **Apply Root Motion** en el Animator; el reparto entre pose y desplazamiento se controla con **Bake Into Pose** (Rotation / Position Y / Position XZ) por clip. Detalle de esos toggles en [ver: unity/animacion-unity §1 Update mode] y [ver: rig-a-unity].
- Un juego con locomoción in-place (blend tree de velocidad) puede NO usar root motion; entonces el Root sigue siendo útil como ancla, pero el desplazamiento lo maneja el CharacterController. Decidirlo por diseño, no por defecto.

## 9. Escala del armature = escala del mesh

Regla dura de pipeline: **el armature y la malla comparten escala 1.0 y rotación 0**, en metros.

- Aplicar transforms **en Object Mode** sobre la rest pose: `Ctrl`-`A` ‣ All Transforms al armature y a la malla ANTES de exportar. Un armature con scale ≠ 1 rompe la animación y multiplica la escala en Unity (el clásico ×100) [ver: blender/import-export §"Escala" y §"Rotación"].
- **Nunca** aplicar transforms al armature en Pose Mode ni con la malla ya deformada — solo sobre el rest, en Object Mode.
- Orden correcto: escena métrica [ver: blender/interfaz-flujo §10] → modelar a tamaño real → riguear → `Ctrl`-`A` All Transforms a malla + armature → parent con weights → export FBX con `apply_scale_options='FBX_SCALE_UNITS'`.
- El **modificador Armature** en la malla (no un parent normal) es lo que la deforma: se crea solo al hacer `Ctrl`-`P` ‣ With Automatic Weights. Su opción `use_deform_preserve_volume` activa dual-quaternion (menos "efecto pajita" en torsiones) [ver: deformacion].

## 10. bpy operativo: recetas cortas (verificadas contra la API estable 4.x/5.x)

```python
import bpy
from math import radians

# --- Crear armature con un hueso raíz en el origen ---
bpy.ops.object.armature_add(enter_editmode=True, align='WORLD', location=(0, 0, 0))
arm = bpy.context.object
arm.name = "RIG_Character"
arm.show_in_front = True                      # ver huesos a través de la malla
eb = arm.data.edit_bones
root = eb[0]; root.name = "Root"
root.head = (0, 0, 0); root.tail = (0, 0, 0.2)   # hueso corto plano en el suelo

# --- Añadir hips como hijo FREE (con offset) del root ---
hips = eb.new("Hips")
hips.head = (0, 0, 1.0); hips.tail = (0, 0, 1.15)
hips.parent = root
hips.use_connect = False                      # free: hay hueco root→hips
hips.use_deform = True

# --- Encadenar columna CONNECTED (el tail del padre = head del hijo) ---
spine = eb.new("Spine")
spine.head = hips.tail; spine.tail = (0, 0, 1.35)
spine.parent = hips
spine.use_connect = True                       # soldado

# --- Recalcular roll de la selección a +Z global ---
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.armature.select_all(action='SELECT')
bpy.ops.armature.calculate_roll(type='GLOBAL_POS_Z')

# --- Auto-nombrar L/R por posición y espejar el lado ya rigueado ---
bpy.ops.armature.autoside_names(type='XAXIS')          # añade .L/.R según X
bpy.ops.armature.symmetrize(direction='NEGATIVE_X')    # duplica izq→der

# --- Organizar en bone collections (4.0+, reemplaza bone layers) ---
defs = arm.data.collections.new("DEF")
for b in arm.data.bones:
    if b.use_deform:
        defs.assign(b)
```

```python
# --- Parent malla → armature con pesos automáticos (crea modificador Armature + vertex groups) ---
bpy.ops.object.mode_set(mode='OBJECT')
mesh = bpy.data.objects["Character_Mesh"]
bpy.ops.object.select_all(action='DESELECT')
mesh.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm            # armature = objeto activo
bpy.ops.object.parent_set(type='ARMATURE_AUTO')        # 'With Automatic Weights'
# Otras variantes: 'ARMATURE_NAME' (grupos vacíos), 'ARMATURE_ENVELOPE' (envelopes)

# --- Limitar a 4 influencias por vértice (el máximo que respeta Unity) ---
bpy.context.view_layer.objects.active = mesh
bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
bpy.ops.object.vertex_group_limit_total(limit=4)       # Weights ‣ Limit Total
bpy.ops.object.vertex_group_normalize_all(lock_active=False)
```

- `parent_set(type='ARMATURE_AUTO')` = *With Automatic Weights* (bone heat) — punto de partida, casi siempre hay que corregir a mano [ver: skinning-weights].
- **4 huesos por vértice es el DEFAULT, no un techo absoluto** (verificado vía Unity Manual, *Quality Settings* §Skin Weights y FBX Importer §Rig tab): Unity limita a 4 bones/vértice por defecto, pero la propiedad **Skin Weights** (Project Settings ‣ Quality, y por-modelo en el Rig tab del FBX Importer) acepta 1/2/4/**Unlimited**. Para compatibilidad máxima (mobile, otros engines, mínimo costo de skinning) el objetivo sigue siendo **4**: exportar con más y dejarlo en manos del import setting es frágil. `vertex_group_limit_total(limit=4)` + normalizar antes de exportar SIEMPRE, y si de verdad se necesitan >4 (melena, ropa suelta) subir "Skin Weights" a Unlimited a propósito, no por descuido.
- El flujo completo de rigueo por MCP/headless (crear widgets, verificar deformación, exportar) vive en [ver: rigging-en-blender-operativo]. Auto-Rig Pro automatiza todo esto con markers [ver: §11].

## 11. Automatizar: Rigify y Auto-Rig Pro (nivel mención)

- **Rigify** (bundled en Blender 5.x, uno de los 5 add-ons de serie [ver: blender/interfaz-flujo §11]): meta-rig editable → genera un rig completo con IK/FK, controles y capas `DEF-`/`MCH-`/`ORG-`. Solo los `DEF-` deforman y exportan. Detalle: [ver: rigify].
- **Auto-Rig Pro** (add-on de pago; verificado en su doc oficial, versión mostrada **3.77**, copyright 2016-2023 — a jul-2026 probablemente más reciente, versión y precio NO verificados esta sesión): auto-detección por markers + one-click rig, módulo **Quick Rig**, **Remap** (retargeting de animación), **Check-Fix Rig**, y export a **game engines** con integración específica Unreal/Unity y preset de roundtrip del Mannequin de UE. Su export ya escupe un rig deform-only con naming humanoid-friendly — resuelve de una lo de §6/§7. Precio histórico ~40 USD en el marketplace (superhivemarket, ex-Blender Market); confirmar antes de citar.

## Reglas prácticas

1. Estructura en **Edit Mode**, pose en **Pose Mode**, escala/posición en **Object Mode**: nunca confundir qué modo edita qué.
2. Head del hueso = la articulación real (codo, rodilla), no en medio del segmento; el tail solo apunta.
3. Cadenas sin hueco = **Connected** (`E` para extruir); con hueco (clavícula→brazo, cadera→pierna) = **Keep Offset / free**.
4. Riguear un solo lado con `.L`, luego `armature.symmetrize()` para el `.R` — jamás rigar los dos lados a mano.
5. Sufijo `.L`/`.R` (o `_L`/`_R`) consistente en TODO el rig; mezclar convenciones rompe simetría y auto-map.
6. Nombres descriptivos por parte del cuerpo y jerarquía anatómica `Hips→Spine→Chest→Shoulder→Arm→Forearm→Hand` para que el Humanoid de Unity auto-mapee.
7. Recalcular el roll de todo el esqueleto a una convención única (`GLOBAL_POS_Z` para el cuerpo) y verificar con los ejes visibles.
8. Marcar **Deform** solo en los huesos que deforman; controles y mecanismos con Deform OFF.
9. Organizar en **bone collections** (no bone layers, obsoletas desde 4.0): DEF / CTRL / MCH separadas.
10. Un **hueso Root único** en (0,0,0) alineado a ejes, con `Hips` como primer deform que cuelga de él.
11. Esqueleto humano ≥ 15 huesos con los 15 obligatorios de Unity presentes si el target es Humanoid.
12. Bind pose en **T-pose** (o A-pose acordada con el modelador); decidirlo ANTES de retopo.
13. **4 influencias por vértice** como objetivo (el default de Unity; ajustable a Unlimited en Quality Settings/Rig tab, pero no es la opción segura por defecto): `vertex_group_limit_total(limit=4)` + normalizar antes de exportar.
14. `Ctrl`-`A` ‣ All Transforms a malla y armature (sobre el rest, en Object Mode) antes de exportar; escala 1.0 en metros.
15. La malla se deforma con el **modificador Armature** (lo crea el parent With Automatic Weights), no con un parent normal.
16. Export: **Only Deform Bones** ON + **Add Leaf Bones** OFF; solo los deform llegan al FBX [ver: rig-a-unity].
17. No renombrar ni reestructurar huesos después del primer import en Unity: reconfiguras el Avatar/retarget [ver: blender/import-export].
18. Verificar la deformación en pose (brazo arriba, sentadilla, giro) ANTES de dar el rig por bueno — no solo en T-pose.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Editar longitud/jerarquía en Pose Mode (no pasa nada o se corrompe) | La estructura se edita en **Edit Mode**; Pose Mode solo posa |
| Head del hueso a mitad del hueso (codo se dobla en el sitio equivocado) | El head va EN la articulación; el tail solo apunta al siguiente |
| Cadena toda "connected" con la clavícula pegada al esternón | Clavícula→brazo y cadera→pierna son **free** (Keep Offset), no connected |
| Roll distinto entre `Hueso.L` y `Hueso.R` → pose espejada torcida | `Ctrl`-`N` recalcular roll a convención única antes de skinnear/animar |
| Rigar los dos lados a mano y que queden asimétricos | Rigar izquierda, `symmetrize(direction='NEGATIVE_X')` |
| Nombres `Bone.001`/`Bone.042` → Unity no auto-mapea el Humanoid | Nombrar por parte del cuerpo + jerarquía anatómica; sufijos `.L/.R` |
| Mezclar `.L` con `_R` o `LeftHand` sin separador → simetría rota | Una sola convención de sufijo en todo el rig |
| Huesos de control con Deform ON → vertex groups fantasma en Unity | Deform solo en los DEF; controles/MCH con Deform OFF + Only Deform Bones al exportar |
| Add Leaf Bones ON → huesos `_end` basura por todo el rig en Unity | `add_leaf_bones=False` en el export FBX |
| Buscar "bone layers" y el menú `M` que enseñan los tutoriales viejos | Desde 4.0 son **Bone Collections** (`armature.collections`); las layers ya no existen |
| Armature con scale ≠ 1 → animación rota / escala ×100 en Unity | `Ctrl`-`A` All Transforms sobre el rest en Object Mode antes de exportar |
| Aplicar transforms al armature en Pose Mode | Solo en Object Mode sobre la rest position; nunca en pose |
| 5+ huesos influyendo un vértice → el import (Rig tab) o Quality Settings recorta a 4 y deforma distinto a lo visto en Blender | `vertex_group_limit_total(limit=4)` + normalizar; si se necesitan más a propósito, subir "Skin Weights" a Unlimited explícitamente |
| Malla "parented" sin modificador Armature → no deforma | Usar `Ctrl`-`P` ‣ With Automatic Weights (crea el modificador), no parent normal |
| Rig aprobado solo en T-pose que explota al animar | Probar poses extremas (brazo arriba, sentadilla, giro de cabeza) como gate |
| Root motion no avanza / personaje patina | Humanoid deriva root del centro de masa; Generic exige designar Root Node; revisar Apply Root Motion + Bake Into Pose [ver: unity/animacion-unity] |
| Sin hueso Root en el origen → esqueleto sucio para el engine | Un Root único en (0,0,0) alineado, Hips colgando de él |

## Fuentes

- **Blender Manual 5.2 LTS — Armatures / Bones** (`docs.blender.org/manual/en/latest/animation/armatures/…`: Introduction, Bones ‣ Structure [head/tail/roll, ejes locales], Editing ‣ Parenting [Connected vs Keep Offset, `Ctrl`-`P`/`Alt`-`P`], Editing ‣ Naming [tokens L/R, separadores, autoside], Editing ‣ Bone Roll [`calculate_roll`], Skinning ‣ Parenting [With Automatic Weights], Bone Collections) — Blender Foundation. *Referencia autoritativa de operadores y settings; docs.blender.org devolvió 403 a la herramienta de fetch en esta sesión — el contenido de operadores proviene de la API bpy estable (sin cambios 4.x→5.x) verificada previamente y cruzada con estas páginas.*
- **Blender Python API — `bpy.ops.armature.*` y `bpy.types.EditBone/Bone`** (`docs.blender.org/api/current/`) — nombres y parámetros de `armature_add`, `extrude_move`, `parent_set(type=)`, `parent_clear(type=)`, `calculate_roll(type=)`, `symmetrize(direction=)`, `autoside_names`, `flip_names`, `vertex_group_limit_total`, propiedades `head/tail/roll/use_connect/use_deform`, `data.collections`.
- **Unity Manual 6 — Using Humanoid Characters** (`docs.unity3d.com/Manual/UsingHumanoidChars.html`) — VERIFICADO vía fetch: mínimo 15 huesos, nombres descriptivos (`LeftArm`/`RightForearm`), pares `arm_L`/`arm_R` mejoran el auto-match, jerarquía `HIPS→spine→chest→shoulders→arm→forearm→hand`, recomendación de T-pose, Humanoid vs Generic (Root node).
- **Unity Manual 6 — Configuring the Avatar** (`ConfiguringtheAvatar.html`) — VERIFICADO: "al menos 15 huesos que se ajusten aproximadamente a un esqueleto humano", flujo Rig→Humanoid→auto-map→configure, huesos requeridos vs opcionales, Enforce T-Pose y el aviso "Character not in T-Pose", pestaña Muscles & Settings.
- **Unity Manual 6 — Avatar Creation and Setup** (`AvatarCreationandSetup.html`) — VERIFICADO: propósito del Avatar (mapear partes del cuerpo), base del retargeting por similitud de estructura ósea.
- **Unity Manual 6 — Retargeting** (`Retargeting.html`) — VERIFICADO: el Avatar desacopla nombres/estructura; retargetear "sin reestructurar esqueletos ni renombrar huesos"; ambos modelos necesitan tipo Humanoid + Avatar válido.
- **Unity Manual 6 — Root Motion** (`RootMotion.html`) — VERIFICADO (fetch directo, sesión de auditoría 2026-07-20): Body Transform (centro de masa) vs Root Transform (proyección en plano Y, calculada en runtime); Humanoid deriva root del COM (única curva en world-space del clip), Generic exige Root Node; Apply Root Motion; Bake Into Pose (Rotation/Position Y/Position XZ) confirmados palabra por palabra.
- **Unity Manual 6 — Quality Settings §Skin Weights** y **Configuring the Avatar §Skin Weights (Rig tab del FBX Importer)** — VERIFICADO (fetch directo 2026-07-20): "By default, this property limits influence to four bones"; la propiedad Skin Weights (Project Settings ‣ Quality y por-modelo en el Rig tab) acepta 1/2/4/Unlimited — el límite de 4 es el **default configurable**, no un techo absoluto de Unity. Matiza y corrige la simplificación previa del archivo.
- **Auto-Rig Pro — documentación oficial** (`lucky3d.fr/auto-rig-pro/doc/`) — VERIFICADO vía fetch (sesión de investigación y re-confirmado en fetch directo de esta auditoría, 2026-07-20, mismo resultado): smart auto-detection + one-click rig, Quick Rig, Remap/retargeting, Check-Fix Rig, export a game engines con integración Unreal/Unity y preset UE Mannequin roundtrip; versión mostrada **3.77** (copyright 2016-2023) en ambas sesiones. Precio NO VERIFICADO ninguna de las dos veces (superhivemarket.com devuelve 403 a la herramienta de fetch).
- **Bases sintetizadas del propio repo:** [ver: modelado/organico-personajes] (topología de deformación, bind pose T vs A, 4 influencias/vértice, piezas rígidas a un hueso, Unity coste por hueso), [ver: blender/interfaz-flujo] (modos Object/Edit/Pose, `Ctrl`-`P`/`Alt`-`P`, escena métrica, add-ons bundled incl. Rigify), [ver: blender/import-export] (Only Deform Bones, Add Leaf Bones OFF, apply transforms, escala ×100, naming como contrato con Unity), [ver: unity/animacion-unity] (Humanoid vs Generic, avatar mask, root motion caro, IK). Cross-refs internos de rigging: [ver: skinning-weights], [ver: deformacion], [ver: ik-fk-constraints], [ver: rigify], [ver: rigs-mecanicos], [ver: rig-a-unity], [ver: rigging-en-blender-operativo].
