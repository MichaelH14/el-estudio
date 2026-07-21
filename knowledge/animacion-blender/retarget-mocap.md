# Retargeting de mocap a tu rig en Blender

> **Cuando cargar este archivo:** cuando tienes una animación hecha para OTRO esqueleto (Mixamo `mixamorig:`, un BVH de mocap, una captura de Rokoko/Move.ai) y necesitas EJECUTAR el traspaso a TU rig dentro de Blender — mapear hueso a hueso, arreglar la escala del mocap, alinear rest poses, correr Auto-Rig Pro Remap / Rokoko / constraints manuales, hornear el resultado sobre tus `DEF_` y sacar el clip. También al diagnosticar un retarget que sale a T-pose, a escala 100×, con los pies patinando o con huesos que no mapean.

Este archivo es la **EJECUCIÓN en Blender** del retarget. Lo que NO repite:
- **La decisión y el panorama de herramientas** (mocap sí/no, calidad, Mixamo, IA text-to-motion, el gotcha universal de foot sliding) → [ver: animacion3d/mocap-librerias]. Ahí está el QUÉ; aquí el CÓMO.
- **El Humanoid de Unity como retargeter** (muscle space, Avatar compartido, swap de personaje, root motion en Unity) → [ver: rigging/rig-a-unity §4-6]. La primera decisión de este archivo es *si Unity ya lo resuelve y te saltas Blender entero* (§1).
- **El bake `nla.bake` a fondo** (defaults, `visual_keying`, flujo seguro de duplicar la Action) → [ver: bake-animacion]. Aquí solo el bake COMO paso final del retarget.
- **El export FBX del clip** (`@anim`, escala, Avatar en Unity) → [ver: export-clips-unity] y [ver: blender/import-export].

Versión: **Blender 5.2 LTS** + **Unity 6** (2026). Los defaults `bpy` y los operadores de constraint/bake están verificados contra el manual 5.2; los flujos de addon (ARP Remap, Rokoko) contra su doc oficial (§Fuentes).

---

## 1. Primera decisión: ¿retargeteas en Blender, o Unity ya lo hace?

**No retarguetees en Blender por costumbre.** Si el destino es un **bípedo Humanoid** y el juego es Unity, el Humanoid resuelve el retarget en runtime en *muscle space* y te ahorras todo este archivo [ver: rigging/rig-a-unity §4].

| Situación | Dónde retargetear | Por qué |
|---|---|---|
| Source Mixamo/humanoide → tu **bípedo Humanoid** en Unity | **Unity Humanoid** — sáltate Blender | Importas ambos con `Animation Type = Humanoid`, Avatar compartido, y el clip corre sobre tu personaje sin tocar Blender [ver: rigging/rig-a-unity §4] |
| Target **Generic**: criatura, cuadrúpedo, mecánico, no-humanoide | **Blender** (obligatorio) | El muscle system de Unity solo mapea humanoides; Generic reproduce rotaciones literales → hay que remapear antes [ver: rigging/rig-a-unity §5] |
| Necesitas **editar la animación a mano** antes de Unity (limpiar, capas, retimear) | **Blender** | Editas F-Curves reales sobre tu rig [ver: graph-editor], montas capas [ver: nla-editor], antes de exportar |
| Quieres una **librería de clips sobre UN esqueleto** (mismo Avatar, `@anim`) | **Blender** | Horneas todos los clips sobre tu rig y exportas el patrón `modelo@anim.fbx` [ver: export-clips-unity] |
| El source **no auto-mapea** a Humanoid (naming raro, sin dedos, proporciones extremas) | **Blender** | Mapeas a mano una vez y horneas; luego tu FBX ya es limpio |
| Motor NO-Unity (Godot, custom) sin retargeter de runtime | **Blender** | El retarget vive en el asset, no en el engine |

**Regla:** Blender retarget = cuando el resultado debe **vivir horneado en el FBX** (Generic, edición previa, librería de un solo esqueleto, motor sin Humanoid). Si Unity puede retargetear en vivo y no vas a editar, no dupliques el trabajo.

---

## 2. Las cuatro vías de ejecución en Blender

Todas comparten el mismo contrato: **source armature animado → mapear huesos → resolver por constraints → hornear sobre el target → limpiar constraints → exportar**. Difieren en cuánto automatizan.

| Vía | Coste | Auto-map | Rest pose / offsets | Root motion | Bake | Cuándo |
|---|---|---|---|---|---|---|
| **Auto-Rig Pro — Remap** | De pago | Presets Mixamo/Rokoko/XSens + name-match | **Redefine Rest Pose** (auto-match de orientación) | Root Bone + IK pole (anti-slide) | Automático a keys | El más completo; producción seria, mucho volumen |
| **Rokoko Studio Live** | **Gratis** | **Build Bone List** + Auto Detect | Exige **misma pose** en ambos (T-pose) | Vía escala + hips | **Retarget Animation** hornea | La opción gratis por defecto |
| **Copy Rotation manual** | Gratis (nativo) | Ninguno — mapeas a mano | Lo manejas tú (matching o offset) | Copy Location / Child Of en hips | `nla.bake visual_keying=True` explícito | Sin addons, control total, entender qué pasa, headless/agente |
| **Unity Humanoid passthrough** | Gratis | Automap del Avatar | T-pose en el Avatar | En Unity (Root Motion) | N/A (runtime) | Sáltate Blender (§1) [ver: rigging/rig-a-unity] |

El panorama de alto nivel de estas herramientas ya está en [ver: animacion3d/mocap-librerias §5] — aquí bajamos a la ejecución paso a paso de cada una (§5-8).

---

## 3. Pre-flight: lo que se arregla ANTES de mapear un solo hueso

Retargetear sobre datos sucios propaga la basura. Cuatro cosas se resuelven primero, en este orden:

### 3a. Escala — el clásico del mocap (Mixamo "0.01" / 100×)

El mocap casi nunca comparte unidad con tu rig. **Mixamo importado a Blender llega comúnmente con el armature a escala `0.01`** (los datos de geometría vienen ×100 en cm y el importer compensa con `scale = 0.01` en el objeto), o físicamente ~100× según settings de importación. Si retargeteas con esa discrepancia, la animación sale a tamaño absurdo o con offsets.

> El número exacto (`0.01`/100×) es comportamiento **reportado consistentemente por la comunidad Blender/Mixamo, NO confirmado aquí contra una fuente primaria de Adobe/Mixamo** (no tiene doc oficial de import a Blender). Lo que SÍ está verificado: Auto-Rig Pro y Rokoko traen ambos un botón **Auto-Scale** dedicado a corregir justo este mismatch — no existirían si source y target compartieran escala de forma fiable. Trátalo como "escala casi seguro distinta, valor típico ~100×" y verifica con `armature.scale` / comparando alturas, no des el `0.01` por dogma en un rig que no hayas medido.

| Antídoto | Cómo |
|---|---|
| **Aplicar escala en el source** | Object Mode, seleccionar el armature source, `Ctrl+A ▸ Scale` → deja `scale = 1.0` con la geometría corregida. Hacerlo ANTES de retargetear |
| **Que source y target compartan Unit Scale** | Ambos en unidades de Blender coherentes (`Scene ▸ Units`), o ambos con transforms aplicados [ver: blender/import-export] |
| **Dejar que el addon escale** | ARP **Auto-Scale** / Rokoko **Auto Scale** ajustan el source al tamaño del target automáticamente — es su razón de existir (source y target rara vez comparten escala) |
| **Import correcto del FBX** | En el FBX (Legacy) importer, revisar **Scale** y **Manual Orientation / Automatic Bone Orientation** para que el esqueleto entre orientado y a tamaño real (§3c) |

> ⚠️ **Nunca uses Apply Transform (`bake_space_transform`) para arreglar escala con armature animado** — "known to be broken with armatures/animations" (warning oficial del import/export FBX 5.2). La escala se arregla con `Ctrl+A ▸ Scale` en el rest, Object Mode, o con el Auto-Scale del addon. Detalle en [ver: bake-animacion §8] y [ver: blender/import-export].

### 3b. Rest pose alignment — el problema REAL del retarget manual

El retarget copia rotaciones. Si el **rest pose** del source (T-pose de Mixamo) y el de tu target difieren (A-pose, o brazos en otro ángulo), una copia de rotación "cruda" mete el offset del rest y el resultado sale torcido. Por eso:

- **Rokoko** exige verbatim: *"Ensure both armatures are in the same pose for accurate retargeting"* — pones ambos en T-pose antes de Retarget Animation.
- **ARP** trae **Redefine Rest Pose**: seleccionas los huesos mal alineados y **Copy Selected Bones Rotation** los rota para que coincidan con el source, con **Preserve** para no dañar el armature original.
- **Manual**: o alineas el rest de tu target al del source, o resuelves el offset por espacio del constraint (§8).

**Regla:** ambos rigs mirando la MISMA dirección (normalmente −Y forward de Blender) y en la MISMA pose base. Modela/riggea en **T-pose** desde el inicio para que esto sea gratis [ver: rigging/rig-a-unity §1] [ver: rigging/esqueletos-armature].

### 3c. Import limpio del source (FBX/BVH)

| Opción del importer FBX (Legacy) | Valor para mocap | Por qué |
|---|---|---|
| **Automatic Bone Orientation** | ON (Mixamo/mocap) | Reorienta los huesos a la convención de Blender → mapeo y edición más fáciles (ARP recomienda ON para retarget) |
| **Ignore Leaf Bones** | ON | Descarta los huesos `_end` de punta (`HeadTop_End`, `LeftToe_End`) que no deforman ni mapean |
| **Force Connect Children** | según rig | Conecta puntas a bases; útil para cadenas limpias, cuidado con hips |
| **Scale / Manual Orientation** | ajustar a tamaño real | Ver 3a; que el source entre a escala del mundo |

Para BVH usa `File ▸ Import ▸ Motion Capture (.bvh)` (escala y "Forward/Up" en el importer). BVH trae solo esqueleto+animación, sin malla — perfecto como source de retarget.

### 3d. Naming — de dónde sale (o no) el auto-map

El auto-map de todos los addons empareja por **nombre**. Cuanto más estándar el naming, menos trabajo manual:
- **Mixamo**: prefijo `mixamorig:` en todo (`mixamorig:Hips`, `mixamorig:LeftArm`…). Los presets de ARP/Rokoko lo reconocen; ARP tiene **Replace Namespace** (search-and-replace) si el prefijo estorba.
- **Tu rig**: naming simétrico `.L`/`.R` y descriptivo sube el match. Rigify usa `DEF-` en los deform (`DEF-upper_arm.L`) [ver: rigging/rigify].

---

## 4. El mapeo de huesos: emparejar source → target

El corazón del retarget es una tabla source→target. Mixamo es el source más común; su esqueleto es fijo y conocido. Mapeo de los **deform bones** que importan (los `_End` se ignoran):

| Mixamo (`mixamorig:`) | Slot Humanoid | Rigify DEF típico | Tu rig |
|---|---|---|---|
| `Hips` | Hips | `DEF-spine` (raíz) | tu raíz de pelvis |
| `Spine` / `Spine1` / `Spine2` | Spine / Chest / UpperChest | `DEF-spine.001/.002/.003` | tu cadena de columna |
| `Neck` / `Head` | Neck / Head | `DEF-neck` / `DEF-head` | tu cuello/cabeza |
| `LeftShoulder` | LeftShoulder | `DEF-shoulder.L` | tu clavícula.L |
| `LeftArm` / `LeftForeArm` / `LeftHand` | LeftUpperArm / LeftLowerArm / LeftHand | `DEF-upper_arm.L` / `DEF-forearm.L` / `DEF-hand.L` | tu brazo.L |
| `LeftUpLeg` / `LeftLeg` / `LeftFoot` / `LeftToeBase` | LeftUpperLeg / LeftLowerLeg / LeftFoot / LeftToes | `DEF-thigh.L` / `DEF-shin.L` / `DEF-foot.L` / `DEF-toe.L` | tu pierna.L |
| (espejo `Right*`) | (espejo Right) | (`.R`) | (espejo) |
| Dedos `LeftHandIndex1…` | dedos (opcionales) | `DEF-f_index.01.L…` | dedos si tu rig los tiene |

**Huesos que sobran / faltan** (la fricción real):
- **Sobran en el source**: `mixamorig:HeadTop_End`, `LeftToe_End`, dedos si tu rig no los tiene → **no los mapees** (déjalos sin destino).
- **Faltan en el source**: `UpperChest`, twist bones, huesos de control, cheek/jaw → tu rig los tiene pero el mocap no los mueve; quedan en su rest pose (bien) o se derivan de vecinos.
- **Cadenas de distinta longitud**: si tu columna tiene 4 huesos y Mixamo 3, repartes (Spine→spine.001, Spine1→spine.002+.003, o dejas uno sin animar). El mocap no se rompe por esto, pero el fraseo de la columna cambia.
- **Twist bones**: Mixamo no los tiene; en tu rig se resuelven por driver/constraint del twist a partir del hueso padre, no por el mocap [ver: rigging/rigify].

Guarda el mapeo como **preset** (ARP: exportar preset; Rokoko: build list reutilizable; manual: un `.blend` o un dict en tu script) — lo reusas en cada clip del mismo par source→target.

---

## 5. Vía A — Auto-Rig Pro Remap (paso a paso)

Addon de pago; el más completo (mapea + alinea rest + maneja root/IK + hornea). Workflow verificado contra la doc oficial de ARP Remap:

1. **Importar** el skeleton animado (BVH/FBX). En FBX activar **Automatic Bones Orientations**.
2. **Zero-out** el target: `Alt+G` (location) y `Alt+R` (rotation) para que no arrastre offset.
3. **Asignar Source** y **Target** en sus campos del panel Remap.
4. **Auto-Scale** para ajustar la escala del source al target (o escala a mano con `S`). **In Place** ON para loops (walk/run) — quita el desplazamiento raíz.
5. **Build Bones List** → genera el mapeo source→target por nombre; **verificar** cada fila.
6. **Preset**: botón de flecha abajo → importar preset **Mixamo / Rokoko / XSens** si el source es uno de esos. **Replace Namespace** si el prefijo difiere.
7. **Redefine Rest Pose** si los rest poses difieren: **Preserve** ON, elegir base (Rest/Current/Saved), seleccionar huesos mal alineados, **Copy Selected Bones Rotation**, **Apply**.
8. **Bone settings**: marcar el **Root Bone** (hips/pelvis) para root motion; **IK** en manos/pies para precisión de traslación; asignar **pole** y modo (Absolute / Relative Target / Relative Chain / IK World Space para personajes que giran) contra el sliding.
9. **Re-Target** → transfiere y **hornea a keyframes** sobre el target automáticamente.
10. **Interactive Tweaks** post-bake: `Additive Location`, `Location Multiplier` (ej. 0.5) por hueso para corregir penetraciones/patinaje; revertir con la X.
11. **Multiple Source Anim…** para retargetear un lote de clips de una.

El resultado ya es una Action horneada sobre tu rig, lista para limpiar (§9) y exportar. El export game-ready de ARP (Humanoid/Universal, Units ×100, `c_traj`→Root Node "root") está en [ver: rigging/rig-a-unity §9].

---

## 6. Vía B — Rokoko Studio Live (gratis, paso a paso)

Plugin gratis y open-source (GitHub, Blender 2.80+; sidebar `N` ▸ pestaña **Rokoko**). Sirve para retarget aunque no uses su hardware. Workflow verificado contra el README oficial:

1. Tu personaje en **T-pose** (requisito duro).
2. Abrir el panel **Retargeting** de la pestaña Rokoko.
3. **Source armature** = armature con la animación; **Target armature** = el que la recibe.
4. **Build Bone List** → auto-detecta el mapeo. **Verificar** y corregir filas mal mapeadas o vacías (botón **Auto Detect** para reintentar).
5. **Auto Scale** ON si difieren de tamaño (o ajustar a mano).
6. **Use Pose**: asegurar que AMBOS armatures estén en la MISMA pose (T-pose) — es el punto que más rompe el resultado.
7. **Retarget Animation** → hornea la animación sobre el target.

Rápido y suficiente para volumen indie. Menos control fino de IK/pole que ARP (más propenso a sliding si las proporciones son muy distintas), pero gratis y con auto-map decente. Tras retargetear: limpiar (§9) y exportar.

---

## 7. Vía C — Copy Rotation manual (sin addon, para entender y para agentes)

El método nativo, sin dependencias. Es lento a mano pero **scripteable** (clave headless/MCP) y te enseña qué hacen los addons por dentro. Se apoya en dos constraints nativos verificados (manual 5.2):

| Constraint | Rol en el retarget | Opciones clave |
|---|---|---|
| **Copy Rotation** | Cada hueso del target copia la rotación del hueso source correspondiente | **Target** (armature+bone), **Axis** X/Y/Z, **Mix** (Replace/Add/Before/After Original), **Target/Owner space** (World/Local/Pose), **Influence** |
| **Copy Location** | El **hips** copia la traslación del hips source (root motion / desplazamiento) | Igual espacio; a veces con multiplicador de escala si las proporciones difieren |
| **Child Of** | Alternativa para "colgar" el target del source con Influence animable | **Set Inverse** para fijar el offset correcto; Location/Rotation/Scale por eje |

### El proceso

1. Importar y alinear source y target (§3): misma escala, misma dirección, rest poses lo más parecidos posible.
2. En el **target**, Pose Mode: por cada deform bone, añadir **Copy Rotation** con Target = armature source, Bone = el source mapeado (tabla §4).
3. **hips**: además de Copy Rotation, **Copy Location** del hips source (para que el personaje se desplace / root motion). Si `In Place`, omitir la Location.
4. **Espacio del constraint = el nudo del rest pose**:
   - Si source y target comparten **rest orientation** (ambos T-pose bien alineados): **Copy Rotation en World/World** (o Pose/Pose) copia la orientación mundial exacta → correcto.
   - Si los rest **difieren**: la copia mundial arrastra el offset del rest. Solución robusta: **igualar el rest pose del target al del source primero** (align + `Ctrl+A` de la pose como rest si hace falta), y entonces World/World funciona. Es exactamente lo que ARP automatiza con *Redefine Rest Pose*.
5. Reproducir: el target debe seguir al source frame a frame. Corregir ejes con **Invert** o el **Order** de Euler si algún hueso gira al revés.
6. **Hornear** con Visual Keying (obligatorio: los DEF no tienen keys propios, los mueve el constraint) → detalle completo en [ver: bake-animacion §3-5].
7. **Borrar los constraints** tras hornear (`clear_constraints=True`, que EXIGE `visual_keying=True`) → el target queda con keyframes puros [ver: bake-animacion §4].

### Snippet bpy — cablear + hornear (agente-friendly)

```python
import bpy
src = bpy.data.objects["mixamo_source"]
tgt = bpy.data.objects["Armature_Hero"]

# Mapeo source(mixamorig) -> target(tu rig). Ajusta a tu naming.
MAP = {
    "mixamorig:Hips": "DEF-spine",
    "mixamorig:Spine": "DEF-spine.001", "mixamorig:Spine1": "DEF-spine.002",
    "mixamorig:LeftArm": "DEF-upper_arm.L", "mixamorig:LeftForeArm": "DEF-forearm.L",
    "mixamorig:LeftUpLeg": "DEF-thigh.L", "mixamorig:LeftLeg": "DEF-shin.L",
    # ... completar espejo y resto
}

bpy.context.view_layer.objects.active = tgt
bpy.ops.object.mode_set(mode='POSE')
for s_name, t_name in MAP.items():
    pb = tgt.pose.bones.get(t_name)
    if not pb or s_name not in src.pose.bones:
        continue
    c = pb.constraints.new('COPY_ROTATION')
    c.target = src; c.subtarget = s_name
    c.target_space = 'WORLD'; c.owner_space = 'WORLD'   # requiere rest poses alineados (§3b)
    if t_name == "DEF-spine":                            # hips: además traslación
        cl = pb.constraints.new('COPY_LOCATION')
        cl.target = src; cl.subtarget = s_name
        cl.target_space = 'WORLD'; cl.owner_space = 'WORLD'

# Hornear el resultado a keys sobre el target y limpiar constraints (ver: bake-animacion)
for b in tgt.data.bones:
    b.select = b.use_deform
sc = bpy.context.scene
bpy.ops.nla.bake(frame_start=sc.frame_start, frame_end=sc.frame_end, step=1,
                 only_selected=True, visual_keying=True, clear_constraints=True,
                 bake_types={'POSE'}, channel_types={'LOCATION', 'ROTATION'})
```

Verificación numérica (sin ojos): evaluar F-Curves de un DEF post-bake y confirmar que no son planas; comparar silueta contra el source [ver: animacion-blender-operativo]. Los defaults reales de `nla.bake` y el flujo seguro (duplicar la Action antes de `clear_constraints`) en [ver: bake-animacion §3-4].

---

## 8. Hornear el resultado y exportar

El retarget produce una animación en TU rig. A partir de aquí es el pipeline normal de salida:

1. **Hornear** (si no lo hizo el addon): `nla.bake visual_keying=True` sobre los `DEF_`, sobre una **copia** de la Action [ver: bake-animacion §4]. ARP y Rokoko ya entregan keys horneados; el método manual lo requiere explícito.
2. **Organizar** cada clip como su propia Action con Fake User y naming de take [ver: actions-organizacion].
3. **Loop**: casar primer y último frame si cicla [ver: animacion3d/ciclos-locomocion].
4. **Reducir keys**: el bake pone 1 key/frame por hueso (denso). Decimate (Allowed Change) / Clean, reproduciendo tras cada reducción [ver: bake-animacion §9] [ver: graph-editor].
5. **Exportar** FBX game-ready: `Only Deform Bones ON`, `Add Leaf Bones OFF`, patrón `modelo@anim.fbx`, framerate = fps del juego [ver: export-clips-unity].
6. **Root motion**: en Unity, Bake Into Pose / Based Upon = Body Orientation para locomoción [ver: rigging/rig-a-unity §6].

**Ojo con la escala en el bake:** si aplicaste escala en el source pero no en el target (o viceversa), las curvas de Location del hips salen escaladas. Ambos rigs a Unit Scale 1.0 ANTES de hornear (§3a).

---

## 9. Limpiar tras retargetear: proporciones que rompen contactos

El retarget resuelve la **orientación** de los huesos, no los **contactos con el suelo/objetos**. Proporciones distintas entre actor y personaje = foot sliding y penetración casi garantizados. La lista completa de cleanup (foot IK, jitter, densidad, drift, loop) está en [ver: animacion3d/mocap-librerias §6] — **no se repite**. Lo específico del post-retarget:

| Síntoma tras retargetear | Causa | Antídoto en Blender |
|---|---|---|
| **Foot sliding** (el #1) | Piernas de otra longitud que el actor → el paso no cubre la misma distancia | Plantar pies con foot IK/lock y keys de contacto, luego re-hornear; o corregir en Unity con foot IK en la capa [ver: rigging/ik-fk-constraints] |
| **Penetración** (manos en el cuerpo, pies bajo el suelo) | Torso/brazos de distinto grosor/largo | Corregir a mano los frames de contacto; ARP **Interactive Tweaks** (Additive Location / Multiplier) |
| **Deriva del hips en el loop** | Root motion horneado con offset de escala | Bake Into Pose XZ en idles [ver: rigging/rig-a-unity §6]; re-anclar contactos |
| **Jitter / ruido** heredado del mocap | El source ya venía sucio (markerless/IMU) | Filtro (Butterworth/Gaussian) o reducción de keys sobre las curvas ya en tu rig [ver: graph-editor] |
| **Falta de holds / appeal** | El mocap es literal | Pase de game-feel a mano encima [ver: animacion3d/keyframes-curvas] |

Nunca trates el retarget como "terminado": es el paso que **traslada** el material en bruto a tu rig; el pulido sigue siendo tuyo.

---

## 10. Flujo agente-friendly: qué se automatiza y qué necesita ojo

Reparto claro para un agente (MCP / `blender --background`) — el detalle de verificación sin ojos está en [ver: animacion-blender-operativo].

| Se automatiza por script/addon | Necesita ojo humano (o verificación numérica + render) |
|---|---|
| Importar el FBX/BVH del mocap (batch de una carpeta) | Juzgar si el clip retargeteado "se siente" bien (arcos, peso, appeal) |
| Aplicar escala, zero-out, fijar `scene.frame_start/end` | Decidir el mapeo de las cadenas que no auto-mapean (columna 3↔4, dedos) |
| Cablear el mapeo (dict → Copy Rotation por hueso) o correr el preset del addon | Alinear rest poses si difieren de forma no trivial |
| `nla.bake visual_keying=True` + `clear_constraints` | Detectar/arreglar penetraciones y foot sliding por proporción |
| Reducir keys, organizar Actions, exportar `@anim` en lote | Aprobar el loop y el pase de game-feel final |
| **Verificar**: `fc.evaluate()` que los DEF no son planos; render Workbench a PNG y leer la silueta vs el source | — |

**"Retarget listo" NO es "el operador no dio error":** es haber **visto (o medido) el target moverse como el source**, con pies plantados y sin explotar, y — idealmente — deformando en Unity [ver: rigging/rig-a-unity §10].

---

## Reglas prácticas

- [ ] Antes de nada, pregúntate si Unity Humanoid ya retargetea en runtime y te saltas Blender — solo retargetea aquí si el target es Generic, editas antes de Unity, o haces librería de un esqueleto (§1).
- [ ] Aplica **escala en el source** (`Ctrl+A ▸ Scale`) para dejarlo a Unit Scale 1.0 antes de mapear; Mixamo suele llegar a `0.01`/100× (§3a).
- [ ] **Nunca** arregles escala con Apply Transform (`bake_space_transform`) en armature animado — roto oficialmente; usa `Ctrl+A` en el rest o el Auto-Scale del addon.
- [ ] Pon source y target en la **misma dirección** y la **misma pose base** (T-pose) antes de retargetear — el rest pose desalineado es la causa #1 de resultados torcidos (§3b).
- [ ] Importa el source con **Automatic Bone Orientation ON** e **Ignore Leaf Bones ON** (fuera los `_End`).
- [ ] Guarda el **mapeo como preset/dict** y reúsalo en cada clip del mismo par source→target (§4).
- [ ] Los huesos que sobran (leaf, dedos si no los tienes) **no se mapean**; los que faltan (twist, UpperChest) se quedan en rest o se derivan, no del mocap.
- [ ] **ARP Remap**: Build Bones List → preset (Mixamo/Rokoko) → Redefine Rest Pose si difieren → Root Bone + IK/pole contra sliding → Re-Target (§5).
- [ ] **Rokoko** (gratis): T-pose ambos → Build Bone List → verificar mapeo → Auto Scale → misma pose → Retarget Animation (§6).
- [ ] **Manual**: Copy Rotation por hueso (World/World con rest alineados) + Copy Location en hips; hornear con **`visual_keying=True`** y borrar constraints (§7).
- [ ] Hornea SIEMPRE sobre una **copia** de la Action; `clear_constraints=True` es destructivo y exige `visual_keying=True` [ver: bake-animacion §4].
- [ ] Tras hornear: reduce keys, casa el loop, exporta `@anim` con Only Deform ON / Add Leaf OFF [ver: export-clips-unity].
- [ ] Espera **foot sliding** siempre que las proporciones difieran; resuélvelo con foot IK/lock + keys de plantado, no con el retargeter (§9).
- [ ] Deja Unit Scale 1.0 en AMBOS rigs antes de hornear, o las curvas de Location del hips salen escaladas.
- [ ] Un agente automatiza importar/mapear/hornear/exportar; deja para ojo humano el mapeo ambiguo, la alineación de rest y los contactos (§10).
- [ ] "Retarget listo" = visto/medido moverse como el source con contactos intactos, no "corrió sin error".

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Retargeteas en Blender un Mixamo→bípedo Humanoid que Unity ya resolvía solo | Sáltate Blender: importa ambos Humanoid, Avatar compartido [ver: rigging/rig-a-unity §4] |
| Personaje sale a tamaño gigante/minúsculo tras retargetear | Escala del source sin aplicar (Mixamo 0.01): `Ctrl+A ▸ Scale` en el source, o Auto-Scale del addon (§3a) |
| Resultado torcido / brazos girados aunque el mapeo es correcto | Rest poses desalineados: iguala la pose base (T-pose ambos) o usa Redefine Rest Pose de ARP (§3b) |
| Copy Rotation en Local space con rests distintos → pose rota | Alinea rest poses y usa World/World; o Redefine Rest Pose antes (§7) |
| Huesos `_End` (`HeadTop_End`, `LeftToe_End`) ensucian el mapeo | Ignore Leaf Bones ON al importar; no los mapees (§3c) |
| El personaje llega a Unity en T-pose inmóvil pese al retarget | Faltó hornear: los DEF los movía el constraint, no keys → `nla.bake visual_keying=True` antes de exportar [ver: bake-animacion] |
| Horneaste y el hueso saltó a su base / perdió la pose | `visual_keying=False` (o `clear_constraints` sin él): re-hornea con visual keying ON [ver: bake-animacion §4] |
| Pies patinan tras el retarget | Proporciones distintas actor↔personaje: foot IK/lock + keys de plantado, no el retargeter (§9) |
| El hips no se desplaza / el personaje "corre en el sitio" | Faltó Copy Location en el hips (o In Place estaba ON cuando querías root motion) (§7) |
| La columna de 4 huesos se ve rígida con un source de 3 | Cadenas de distinta longitud: reparte el mapeo o deja un hueso derivado; el fraseo cambia, no se rompe (§4) |
| Curvas de Location del hips a escala rara tras hornear | Source y target con Unit Scale distinto: iguala a 1.0 antes de hornear (§8) |
| Agente declara "retarget hecho" porque el bake no dio error | No es evidencia: mide `fc.evaluate()` / render y compara con el source (§10) |
| Twist bones quietos tras retargetear desde Mixamo | Mixamo no tiene twist; se resuelven por driver/constraint del padre, no del mocap [ver: rigging/rigify] |

## Fuentes

- **Auto-Rig Pro — Remap** (`lucky3d.fr/auto-rig-pro/doc/remap_doc.html`) — Lucky3D — VERIFICADO vía WebFetch (2026-07-21): Source/Target armature, Auto-Scale, In Place, **Build Bones List**, presets **Mixamo/Rokoko/XSens**, **Replace Namespace**, **Redefine Rest Pose** + **Copy Selected Bones Rotation** + Preserve, **Root Bone**, IK/pole modes (Absolute / Relative Target / Relative Chain / IK World Space), **Re-Target**, **Interactive Tweaks** (Additive Location, Location Multiplier), Multiple Source Anim; hornea a keyframes sobre el target. Precio/versión exacta 2026 NO verificados aquí — addon de pago en Blender Market.
- **Rokoko Studio Live — Blender plugin (README)** (`github.com/Rokoko/rokoko-studio-live-blender`) — Rokoko — VERIFICADO vía curl (2026-07-21): panel **Retargeting**, Source/Target armature, **Build Bone List**, Auto Detect, **Auto Scale**, **Use Pose** (verbatim *"Ensure both armatures are in the same pose for accurate retargeting"*), **Retarget Animation**; requisito T-pose; gratis/open-source, Blender 2.80+.
- **Blender 5.2 LTS Manual — Copy Rotation Constraint** (`animation/constraints/transform/copy_rotation.html`) — Blender Foundation — VERIFICADO vía curl (2026-07-21): *"forces an object or bone to match the rotation of a target"*; Target, Order (Euler), Axis, Invert, **Mix** (Replace/Add/Before Original/After Original/Offset legacy), **Target/Owner space** (World/Local/Pose), Influence.
- **Blender 5.2 LTS Manual — Child Of Constraint** (`animation/constraints/relationship/child_of.html`) — Blender Foundation — VERIFICADO vía curl (2026-07-21): parenting animable (Influence), Location/Rotation/Scale por eje, **Set Inverse / Clear Inverse**; nota: no apto para cadenas de huesos conectadas.
- **Blender 5.2 LTS Manual — FBX (Legacy) Import** (`files/import_export/fbx_legacy.html`) — Blender Foundation — VERIFICADO vía curl (2026-07-21): Transform **Scale**, **Manual Orientation** (Forward/Up), **Apply Transform** ("*known to be broken with armatures/animations*"), Armature **Ignore Leaf Bones**, **Force Connect Children**, **Automatic Bone Orientation**, Primary/Secondary Bone Axis.
- **NO VERIFICADO** — el valor exacto de escala de Mixamo (`0.01`/100×, §3a) es comportamiento reportado consistentemente por la comunidad Blender/Mixamo; no encontré doc primaria de Adobe/Mixamo sobre su import a Blender que lo confirme numéricamente (WebSearch agotado 200/200 en esta sesión). Anclado en las funciones **Auto-Scale** de ARP y Rokoko, ambas sí verificadas contra su doc oficial arriba.
- **Bases sintetizadas de El Estudio** (no repetir, referenciar):
  - [ver: animacion3d/mocap-librerias] — decisión mocap/keyframe, Mixamo, IA text-to-motion, panorama de herramientas de retarget, cleanup completo (foot sliding, jitter, densidad, drift).
  - [ver: rigging/rig-a-unity] — Humanoid vs Generic, Avatar/muscle space como retargeter de runtime, root motion, export ARP game-ready. La razón por la que a veces te saltas Blender (§1).
  - [ver: bake-animacion] — `nla.bake` (defaults, `visual_keying`, flujo seguro de duplicar la Action, reducción de keys). El paso de hornear el retarget.
  - [ver: export-clips-unity] · [ver: blender/import-export] — salida del clip (FBX, `@anim`, escala, framerate).
  - [ver: rigging/ik-fk-constraints] · [ver: rigging/rigify] · [ver: rigging/esqueletos-armature] — control vs deform, DEF-/twist, T-pose. [ver: graph-editor] · [ver: actions-organizacion] · [ver: nla-editor] · [ver: animacion-blender-operativo] — limpieza de curvas, organización de clips, ejecución headless/verificación sin ojos. [ver: animacion3d/ciclos-locomocion] · [ver: animacion3d/keyframes-curvas] — loop y pase de game-feel sobre el mocap.
