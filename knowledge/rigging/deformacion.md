# Deformación: las zonas difíciles

> **Cuando cargar este archivo:** cuando una malla skinneada colapsa, pincha, se afila o pierde volumen al posar/animar — hombros, codos, rodillas, caderas, muñecas, cuello o dedos — y hay que decidir si el fix va en la topología, en los pesos, en un twist bone o en un corrective shape key. Asume el rig ya montado [ver: esqueletos-armature] y los pesos base ya pintados [ver: skinning-weights]; aquí se resuelven las poses extremas y el handoff correcto a Unity.

## 1. Por qué falla la deformación: la cadena de responsabilidad

La deformación es una cadena de 3 eslabones. El fix va en el eslabón correcto, no en el que tienes abierto:

| Eslabón | Qué aporta | Señal de que el fallo es AQUÍ | Fix |
|---|---|---|---|
| **Topología** | Los loops por donde la malla puede doblar sin estirar caras | El pliegue no tiene loops, o los tiene mal alineados al eje de flexión; ninguna cantidad de peso lo arregla | En la malla [ver: modelado/topologia §5] |
| **Skin weights** | Cómo se reparte cada vértice entre huesos (linear blend) | Hay loops, pero el vértice sigue un solo hueso a lo bruto (candy-wrap, tearing) | Pintar/normalizar pesos [ver: skinning-weights] |
| **Twist / correctivos** | Recupera volumen y torsión que el linear blend NO puede | Loops y pesos correctos, pero la pose extrema aún desinfla o retuerce | Twist bones (§3) o corrective shape keys (§4) |

Regla de oro (destila polycount y Topology Guides [ver: modelado/topologia §5]): **la malla se aprueba POSANDO, no en bind pose.** En T/A-pose todo se ve bien. El diagnóstico es siempre en este orden — topología → pesos → correctivos — porque un corrective sobre topología rota es maquillaje que se descose en el ángulo siguiente. No saltar al eslabón 3 sin descartar el 1 y el 2.

**Lo que Unity NO puede compensar:** Unity deforma con **linear blend skinning, máximo 4 influencias por vértice** (Unity Manual, Modeling optimized characters). No hay dual-quaternion en el runtime estándar. Todo lo que en el viewport de Blender se ve bien "gracias a" opciones que no exportan (§7) es una mentira que se rompe al importar.

## 2. Las zonas críticas, una a una

Orden de dolor real en un personaje de juego. Cada una: el problema físico y la solución de rig concreta. Topología de cada zona: [ver: modelado/organico-personajes §5] (no se repite aquí).

| Zona | Problema físico | Solución de rig |
|---|---|---|
| **Hombro** (la peor) | Mayor rango del cuerpo (brazo arriba/adelante/cruzado); el deltoides colapsa y la axila se cierra en pliegue duro | Rig de **clavícula + upper_arm** (el brazo sube desde la clavícula, no solo el hombro); pesos del deltoides repartidos a los 3 huesos; **corrective shape key** disparado por el ángulo del upper_arm para rellenar el hueco superior (§4). Bind en **A-pose ~45°** reparte el error [ver: modelado/organico-personajes §5] |
| **Codo / rodilla** | Bisagra de 1 eje; el lado interno comprime (pinch) y el externo estira (tearing), y el codo "se afila" como manguera doblada | Varios loops en el pliegue [ver: modelado/topologia §5]; pesos con un **loop-guardia** casi 100% al hueso padre justo antes del pliegue para que la esquina no se hunda; corrective de volumen en flexión >90° si aún desinfla |
| **Cadera / entrepierna** | Deforma en 3 ejes a la vez (sentarse, patada, zancada); el thigh cierra contra el pelvis | Pesos del thigh que suben hasta el glúteo; **probar SENTADO y en zancada máxima**, no solo la pierna al frente; corrective en flexión profunda |
| **Muñeca / tobillo** | **Torsión (pronación)**: girar la palma retuerce el antebrazo entero → *candy-paper wrap* (el antebrazo se estrangula como papel de caramelo) | **Twist bones** que distribuyen la rotación a lo largo del hueso (§3). Es EL caso de uso de los twist |
| **Cuello** | Puente de baja masa entre torso y cabeza; gira, se inclina y se estira; pinch bajo el mentón y en la nuca | 1 (móvil) o 2 (neck + neck.001) huesos de cuello; pesos con degradado suave torso→cuello→cabeza; nunca un salto de peso 0→1 en un solo loop |
| **Dedos** | 15+ huesos, articulaciones muy juntas; se pinchan entre falanges y en los nudillos | 3 huesos por dedo (o 2 si es móvil); loop por nudillo; en juego casi nunca hay corrective — se resuelve con topología + pesos limpios. Peldaños de simplificación (5→4→fusionados→mitten): [ver: modelado/organico-personajes §6] |

## 3. Twist / roll bones: repartir la torsión

El problema: un solo hueso de antebrazo rota 180° en la muñeca → todos sus vértices giran igual → el antebrazo se estrangula (candy-wrap). El linear blend **no puede** interpolar rotación sobre el largo del hueso; hay que darle huesos intermedios.

**Anatomía del fix:** N huesos de twist a lo largo del antebrazo (y del muslo), cada uno hereda una **fracción** de la rotación de la muñeca. Con 1 twist a mitad, la mitad basal gira 0 y la muñeca gira 100% → el estrangulamiento se reparte en un giro suave.

| Cuántos twist | Dónde | Fuente |
|---|---|---|
| **1 por limb** | Antebrazo, muslo — mínimo viable, y lo recomendado para **Unity Humanoid** | Auto-Rig Pro (doc): "Unity humanoid: 1 twist bone"; Twist Amount ≈ **0.5** para un solo twist |
| **2-3** | Antebrazo largo o cámara cercana; PC | Auto-Rig Pro: hasta 6/limb en proyectos internos |
| **6** | Cine / render offline, no juego | Auto-Rig Pro: "Multiple twist bones totally solve the candy paper wrap issue" |

**Montaje en Blender (twist real, exportable):** el twist es un **deform bone real** en la jerarquía (hijo del antebrazo), movido por un **Copy Rotation constraint** que copia el roll de la mano/muñeca, o por un driver. Su motion NO exporta como constraint — el FBX la **hornea a keyframes** al exportar con Bake Animation [ver: blender/import-export]. El hueso, sus pesos y la geometría sí exportan normal.

Constraint exacto (Bone Constraint ▸ **Copy Rotation**, sobre el twist bone):

| Campo | Valor | Por qué |
|---|---|---|
| Target / Bone | Armature / `hand.L` (o `forearm_tip`) | La fuente de la torsión |
| Axis | Solo el eje del hueso (**Y** en convención Blender) | Copia solo roll, no flexión |
| Influence | **0.5** con 1 twist; escalonado (0.33/0.66) con 2 | Reparte la rotación por el largo |
| Target/Owner space | **Local Space** ambos | Evita heredar la orientación mundial |

- **Rigify y Auto-Rig Pro generan los twist automáticamente**: en Auto-Rig Pro se define el nº de Twist Bones por limb (1-6) y el export los saca solos; Rigify los incluye en los limbs [ver: rigify]. Montarlos a mano solo en rigs custom [ver: rigging-en-blender-operativo].

- Pesos: el twist bone toma ~50% en su zona, mezclando a 0 hacia el codo y hacia la muñeca; el hueso base del antebrazo lleva el resto.
- **Unity Humanoid** además redistribuye torsión con los ajustes de *muscle* del Avatar (Upper Arm Twist / Fore Arm Twist en Muscles & Settings) — por eso 1 twist bone basta ahí. En **Generic** no hay muscle system: los twist explícitos + bake son obligatorios.
- ⚠️ **Bendy Bones (B-Bones) NO son twist bones para juego.** Los `bbone_segments`/`bbone_rollin`/`bbone_curveinx` existen y son geniales en Blender, pero son una evaluación **interna de Blender que no viaja al FBX**. Para Unity: twist bones reales o baked (§7).

## 4. Corrective shape keys (driven): recuperar volumen en pose extrema

Cuando topología + pesos + twist están bien y la pose extrema AÚN pierde volumen (hueco del hombro, codo hiperflexionado), la herramienta es un **shape key correctivo disparado por el ángulo de un hueso** (PSD / pose-space deformation, versión juego).

**Mecanismo exacto (verificado en Blender 5.2):** un shape key esculpido en la pose problemática + un **driver** en su `value`, leyendo la rotación del hueso:

- Variable tipo **`ROTATION_DIFF`** entre 2 huesos = ángulo (radianes) entre ellos → el disparo natural del codo (upper_arm ↔ forearm) o rodilla.
- O variable tipo **`TRANSFORMS`** con `transform_type='ROT_Y'` leyendo el roll de un solo hueso → disparo de twist/hombro.

```python
import bpy
obj = bpy.data.objects["Body"]
arm = bpy.data.objects["Armature"]
kb  = obj.data.shape_keys.key_blocks["elbow_fix_L"]   # shape esculpido en flexión
drv = kb.driver_add("value").driver
drv.type = 'SCRIPTED'
v = drv.variables.new(); v.name = "ang"; v.type = 'ROTATION_DIFF'
v.targets[0].id = arm; v.targets[0].bone_target = "upper_arm.L"
v.targets[1].id = arm; v.targets[1].bone_target = "forearm.L"
# ang va de ~0 (extendido) a ~pi (doblado); remap+clamp a 0..1:
drv.expression = "max(0.0, min(1.0, (ang - 1.4) / 0.9))"
```

⚠️ **El handoff a Unity — el gotcha crítico:** el shape key **sí exporta al FBX como blendshape** (verificado, Blender 5.2 [ver: blender/import-export]), pero **el driver NO exporta**. En Unity el blendshape llega inerte (weight 0). Dos salidas:

| Salida | Cómo | Cuándo |
|---|---|---|
| **Hornear en los clips** | Al exportar animaciones con Bake Animation, el shape key animado por el driver se hornea en cada clip como curva de blendshape | Animaciones autoradas fijas (locomoción de artista) |
| **Script en Unity** | Un `MonoBehaviour` lee el ángulo del hueso (`Vector3.Angle` entre transforms) cada frame y setea `SkinnedMeshRenderer.SetBlendShapeWeight()` | Poses proceduralmente variables (ragdoll, IK) [ver: unity/animacion-unity §8] |

- Presupuesto: 1 blendshape por vértice-set correctivo. En juego se reserva a hombro y codo/rodilla de héroes; NPCs y móvil casi nunca los pagan (coste de memoria + curva por clip).
- ⚠️ **Apply Modifiers + shape keys = pérdida silenciosa** al exportar: aplicar modificadores a mano ANTES y exportar con Apply Modifiers OFF [ver: blender/import-export].

## 5. Loops de soporte en articulaciones: cuántos y dónde

Teoría de topología: [ver: modelado/topologia §5] (no se repite). Lo específico del rig:

- **Mínimo de juego por bisagra (codo/rodilla): 2-3 loops** en la zona del pliegue. El **loop central cae sobre el eje de pivote del hueso** (donde la Bone head/tail dobla), no desviado — si el loop y el pivote no coinciden, el pliegue se abre en el sitio equivocado.
- Los loops de articulación se **extienden más allá del pliegue** hacia la superficie plana vecina para absorber ángulos extremos [ver: modelado/topologia §5].
- Densidad ↔ presupuesto de huesos: más loops NO cuestan huesos, cuestan vértices [ver: modelado/presupuestos-poligonos]. Es el ajuste barato — antes de añadir un helper bone, probar un loop más.
- Alinear el vertex flow al **eje de flexión**: loops perpendiculares al hueso. Un loop cruzado colapsa por mucho peso que tenga.

### Orden de pesos limpio para deformación (antes de exportar)

Detalle de pintado: [ver: skinning-weights]. El orden que evita el 90% de los colapsos:

1. **Bind con Automatic Weights** (`parent_set(type='ARMATURE_AUTO')`) como base.
2. **Posar la zona y pintar** solo donde colapsa, en Weight Paint con `Auto Normalize` ON.
3. **Smooth** en los saltos duros (cuello, hombro): `vertex_group_smooth(factor=0.5, repeat=2)`.
4. **Limit Total a 4** (`vertex_group_limit_total(limit=4)`) — el tope de Unity.
5. **Normalize All** (suma = 1.0) y **Clean** (borra pesos residuales que pasan basura a Unity).
6. Repetir el gate de poses (§8); iterar solo la zona que aún falla.

## 6. Bones de volumen / músculo: concepto (juego casi nunca)

Escalera de "huesos que no son del esqueleto base", de común a exótico:

| Tipo | Qué hace | ¿Juego? |
|---|---|---|
| **Twist bones** | Reparten torsión (§3) | **Sí**, estándar |
| **Helper / corrective bones** | Un hueso extra movido por driver/constraint que empuja vértices en una pose (alternativa al shape key, p.ej. sube el hombro) | A veces (héroes); cada uno cuesta como bone (§7) |
| **Roll/cushion bones** | Rellenan pliegue de codo/rodilla al doblar | Raro; normalmente se prefiere shape key |
| **Muscle-sim bones (JCM avanzado, flexión muscular)** | Simulan abultamiento de bíceps, etc. | **Casi nunca** — es cine/offline; el coste de skinning no compensa |

Criterio: en juego, **shape key correctivo > helper bone** cuando el fix es de forma pura (no necesita seguir físicas), porque el shape no suma a las 4 influencias/vértice ni al conteo de huesos activos. El helper bone se elige cuando el fix debe encadenarse con IK/físicas en runtime.

## 7. El presupuesto de huesos: cada bone cuesta

El único límite **duro** verificado es de influencias, no de conteo:

| Límite | Valor | Fuente |
|---|---|---|
| **Influencias por vértice** | **4** (linear blend). Más exige `Quality = Auto` + Project Settings ▸ Skin Weights = **Unlimited** | Unity Manual (Modeling optimized characters; Skinned Mesh Renderer ▸ Quality: Auto / 1 / 2 / 4 Bones) |
| **Skinned Mesh Renderers por personaje** | **1** — "dos mallas skinneadas ≈ duplican el tiempo de render" | Unity Manual |
| **Coste por hueso** | "15 huesos extra sobre un rig de 30 ≈ **+50%** de operaciones en modo Generic" | Unity Manual |

El **conteo de huesos** es una curva de coste, no un tope. Convenciones de la industria (no de una spec — tratar como orientación, no como número de origen [ver: modelado/presupuestos-poligonos]):

| Plataforma | Deform bones típicos | Skin Weights |
|---|---|---|
| **Móvil** | ~20-40 (cuerpo simple, manos con dedos fusionados) | 2 Bones (Quality) para bajar coste |
| **PC / consola** | ~50-80 (dedos individuales + 1-2 twist/limb) | 4 Bones |
| **Cine (referencia de escala)** | MetaHuman: **713 joints en LOD0**, 12 influencias | fuera de presupuesto de juego |

- En cada LOD bajan JUNTOS tris, huesos activos e influencias — MetaHuman: 713→26 joints y 12→4 influencias de LOD0 a LOD7 [ver: modelado/presupuestos-poligonos]. El skinning **no se abarata con batching**; `SkinnedMeshRenderer` ni siquiera soporta GPU instancing [ver: unity/rendimiento-unity].
- Export limpio: **Add Leaf Bones OFF** (mete huesos `_end` basura) y **Only Deform Bones ON** (fuera los huesos de control del rig) [ver: blender/import-export]. Marcar el flag deform de cada hueso (`use_deform`) es lo que decide quién exporta.

### Lo que NO sobrevive el FBX a Unity (tabla de la verdad)

| Feature de Blender | ¿Llega a Unity? | Consecuencia si te confías |
|---|---|---|
| **Preserve Volume** del Armature modifier (dual-quat, `use_deform_preserve_volume`) | ❌ | El viewport de Blender miente; Unity usa linear blend → el codo/hombro se ve peor en engine |
| **Bendy Bones** (B-Bones) | ❌ | La curvatura suave desaparece; usa twist bones reales (§3) |
| **Drivers** (correctivos §4) | ❌ | El blendshape llega inerte; hornear en clip o script (§4) |
| **Constraints** (twist, IK) | Solo **horneados** a keyframes por Bake Animation | Sin bake, el twist no se mueve en Unity |
| **Shape keys / blendshapes** | ✅ | (salvo con Apply Modifiers ON, §4) |
| **Pesos + jerarquía de deform bones** | ✅ | — |

## 8. Test de deformación: las poses que revelan el problema ANTES de animar

Nunca aprobar una malla/rig en bind pose. Gate obligatorio (amplía [ver: modelado/organico-personajes §5]):

| Pose extrema | Qué revela |
|---|---|
| **Brazo arriba (100%)** + cruzado al pecho | Colapso de hombro/axila — la #1 |
| **Codo y rodilla > 90°** (hiperflexión) | Pinch interno, afilado, pérdida de volumen |
| **Sentadilla profunda / sentado** | Cadera y entrepierna en 3 ejes |
| **Palma arriba↔abajo (pronación 180°)** | Candy-wrap del antebrazo → ¿faltan twist? |
| **Cabeza girada 90° + inclinada** | Pinch de cuello |
| **Puño cerrado + mano abierta a tope** | Nudillos y membranas de dedos |

Flujo operativo del agente: posar el rig al máximo del juego → mirar el **volumen y la silueta** en esa pose → si desinfla/pincha, subir por la cadena del §1 (¿loops? ¿pesos? ¿twist/corrective?). Verificar con `Object Data ▸ Viewport Display ▸ In Front` del armature apagado y face orientation/matcap para ver el volumen real. Para animación real en engine, la validación definitiva es en Unity con el clip corriendo [ver: unity/animacion-unity].

## Snippets bpy operativos (Blender 5.2, verificados)

```python
import bpy
# --- Crear armature y parentar la malla con pesos automáticos ---
bpy.ops.object.armature_add(enter_editmode=False)          # armature base
# ... editar/colocar huesos, marcar use_deform en los que deforman ...
# Seleccionar malla primero, armature ACTIVO al final, luego:
bpy.ops.object.parent_set(type='ARMATURE_AUTO')            # Automatic Weights
#   ARMATURE_ENVELOPE = por envelopes | ARMATURE_NAME = por vertex groups existentes

# --- Higiene de pesos para Unity: máx 4 influencias + normalizar ---
bpy.ops.object.vertex_group_limit_total(limit=4)           # respeta el tope de Unity
bpy.ops.object.vertex_group_normalize_all(lock_active=False)  # suma de pesos = 1.0
bpy.ops.object.vertex_group_clean(limit=0.0, keep_single=False)  # borra pesos ~0

# --- Suavizar un salto de peso feo (cuello, hombro) ---
bpy.ops.object.vertex_group_smooth(factor=0.5, repeat=2)   # en Weight Paint, grupo activo

# --- Transferir pesos de una malla ya pesada a otra (ropa, LOD) ---
bpy.ops.object.data_transfer(data_type='VGROUP_WEIGHTS',
    vert_mapping='POLYINTERP_NEAREST',
    layers_select_src='NAME', layers_select_dst='NAME')

# --- Aplicar la pose actual como nuevo rest (rebind) ---
bpy.ops.pose.armature_apply(selected=False)

# --- Corrective Smooth modifier: limpia jitter de deformación sin tocar pesos ---
m = bpy.data.objects["Body"].modifiers.new("CorrSmooth", 'CORRECTIVE_SMOOTH')
```

## Reglas prácticas

1. Aprueba SIEMPRE posando al máximo del juego, jamás en bind/T-pose. La malla y el rig se validan doblados.
2. Diagnostica por la cadena: topología → pesos → twist/corrective. No maquilles con un corrective lo que es falta de loops.
3. Bind en **A-pose ~45°** (acordado con quien modela) para repartir el error del hombro entre brazo arriba y abajo.
4. Hombro = clavícula + upper_arm subiendo el brazo; el deltoides pesa a los 3 huesos; hueco superior = corrective por ángulo.
5. Codo/rodilla: varios loops en el pliegue, el central sobre el pivote del hueso, y un loop-guardia casi 100% al padre antes del pliegue.
6. Twist bones para toda torsión de antebrazo/muslo: **1/limb** para Unity Humanoid (Twist Amount ~0.5), 2-3 en PC de cámara cercana.
7. Twist reales, no Bendy Bones: los B-Bones no exportan. Todo lo que anima un twist se hornea a keyframes en el FBX (Bake Animation).
8. Corrective shape key disparado por driver `ROTATION_DIFF` (codo/rodilla) o `TRANSFORMS`/ROT (twist/hombro); remap+clamp a 0..1 en la expresión.
9. El driver del corrective NO llega a Unity: hornéalo en el clip o léelo con un script que setee `SetBlendShapeWeight`.
10. Nunca apliques modificadores con shape keys presentes al exportar (se pierden en silencio): aplica a mano y exporta con Apply Modifiers OFF.
11. `vertex_group_limit_total(limit=4)` + `normalize_all` + `clean` antes de exportar: Unity solo respeta 4 influencias.
12. Cuello con degradado suave torso→cuello→cabeza; jamás un salto de peso 0→1 en un loop.
13. Un solo `SkinnedMeshRenderer` por personaje; fusionar mallas y atlasear (2 mallas ≈ 2× render).
14. NO confíes en Preserve Volume (dual-quat) para el look final: Unity es linear blend, se verá distinto en engine.
15. Presupuesto de huesos: móvil ~20-40 / Skin Weights 2; PC ~50-80 / Skin Weights 4 — como orientación, no como spec.
16. Loops cuestan vértices, no huesos: prueba un loop más antes de meter un helper bone.
17. Helper bone solo si el fix debe encadenar IK/físicas en runtime; si es forma pura, shape key correctivo.
18. En cada LOD bajan juntos huesos, influencias y tris — el auto-LOD ignora skin weights [ver: modelado/presupuestos-poligonos].
19. Export: Add Leaf Bones OFF, Only Deform Bones ON, `use_deform` marcado solo en los huesos que deforman.
20. La verificación final del rig es en Unity con el clip corriendo, no en el viewport de Blender.

## Errores comunes

| Pitfall | Síntoma | Antídoto |
|---|---|---|
| Corrective sobre topología rota | El fix aguanta una pose y se descose en la siguiente | Subir por la cadena (§1): primero loops, luego pesos, el corrective al final |
| Antebrazo estrangulado al girar la palma (candy-wrap) | El antebrazo se retuerce como papel de caramelo | Twist bones repartiendo la rotación (§3) |
| Usar Bendy Bones como twist "para juego" | En Blender perfecto, en Unity el twist desapareció | B-Bones no exportan: twist bones reales + Bake Animation |
| Blendshape correctivo inerte en Unity | El shape existe pero weight siempre 0 | El driver no exportó: hornear en clip o script `SetBlendShapeWeight` |
| Preserve Volume ON creyéndolo el look final | Hombro/codo peor en engine que en el viewport | Desactivar y juzgar en linear blend; el fix va en pesos/corrective |
| Apply Modifiers ON con shape keys | El SkinnedMeshRenderer llega sin blendshapes | Aplicar modificadores a mano, exportar con Apply Modifiers OFF |
| >4 influencias por vértice | Deformación distinta en Blender vs Unity (Unity recorta a 4) | `vertex_group_limit_total(limit=4)` + `normalize_all` antes de exportar |
| Pesos sin normalizar | Vértices que "flotan" o se encogen al posar | `normalize_all` (suma = 1.0) + `clean` de pesos residuales |
| Loop central del pliegue desviado del pivote | El codo dobla en el sitio equivocado, esquina hundida | Alinear el loop de flexión al eje/pivote del hueso |
| Salto de peso 0→1 en el cuello | Pinch duro bajo el mentón / nuca | Degradado suave sobre 2+ loops; `vertex_group_smooth` |
| Hombro pesado solo al upper_arm | Axila que se cierra en pliegue y hueco al subir el brazo | Repartir deltoides a clavícula+hombro+brazo + corrective de ángulo |
| Aprobar el rig en T-pose | Explota al animar (foot slide, colapsos) | Gate de poses extremas (§8) como criterio de aceptación |
| Twist con constraint pero export sin bake | El twist no se mueve en Unity | Exportar con Bake Animation (los constraints solo viajan horneados) |
| Add Leaf Bones ON | Huesos `_end` basura por todo el esqueleto en Unity | `add_leaf_bones=False` [ver: blender/import-export] |
| Helper bones para todo (rig de cine en móvil) | Presupuesto de huesos reventado, +ops de skinning | Shape key correctivo para forma pura; helper solo si encadena runtime |
| Twist con Influence 1.0 (copia el 100% del roll) | El twist gira igual que la muñeca — no reparte nada | Influence 0.5 (1 twist) o escalonada; solo el eje de roll en Local Space |
| Pesos residuales (0.001) que no se limpian | Vértices que "tiran" hacia huesos lejanos en Unity | `vertex_group_clean` tras `limit_total` + `normalize_all` |
| Confiar en el look del viewport de Blender | Se aprueba algo que en engine deforma distinto | Validar en Unity con el clip; Blender puede usar features que no exportan (§7) |

## Fuentes

- **Blender 5.2.0 LTS (binario local, `--factory-startup`)** — Blender Foundation — verificación empírica de operadores y RNA: `object.armature_add`, `object.parent_set` (enum incl. `ARMATURE_AUTO`/`ARMATURE_ENVELOPE`/`ARMATURE_NAME`), `object.vertex_group_limit_total` (default `limit=4`), `vertex_group_normalize_all`/`_clean`/`_smooth`, `object.data_transfer` (`VGROUP_WEIGHTS`), `paint.weight_from_bones`, `pose.armature_apply`; propiedades `Bone.use_deform`/`bbone_segments`/`bbone_rollin`/`envelope_*`; `ArmatureModifier.use_deform_preserve_volume`; drivers `DriverVariable.type` = `ROTATION_DIFF`/`TRANSFORMS` y `DriverTarget.transform_type` = `ROT_X/Y/Z`; modifier `CORRECTIVE_SMOOTH`. Consultado 2026-07-20.
- **Unity Manual — Modeling optimized characters** (`ModelingOptimizedCharacters.html`) — Unity Technologies — linear blend skinning con máx. 4 influencias/vértice, 1 Skinned Mesh Renderer por personaje (2 mallas ≈ 2× render), "15 huesos extra sobre 30 ≈ +50% ops en Generic", materiales al mínimo.
- **Unity Manual — Skinned Mesh Renderer** (`class-SkinnedMeshRenderer.html`) — Unity Technologies — Quality (Auto / 1 / 2 / 4 Bones), >4 requiere Auto + Quality Settings ▸ Skin Weights = Unlimited; Update When Offscreen, Root Bone, Bounds, Skinned Motion Vectors.
- **Unity Manual — Configuring the Avatar / Avatar Mapping** (`ConfiguringtheAvatar.html`, `class-Avatar.html`) — Unity Technologies — mapeo humanoid, huesos requeridos (círculo lleno) vs opcionales (punteado), T-Pose y "Enforce T-Pose", existencia de la pestaña Muscles & Settings (twist muscular). No se verificaron de primera mano los defaults de los sliders Upper Arm/Fore Arm Twist — se cita solo la existencia del sistema.
- **Auto-Rig Pro — Documentation (home, `auto_rig.html`)** — lucky3d.fr — Smart (auto-detección de neck/chin/shoulders/wrists/spine/ankles), Twist Bones 1-6 por limb, "Multiple twist bones totally solve the candy paper wrap issue", Bind (Heat Maps / Voxelized), Soft IK contra el popping de codo/rodilla. Consultado 2026-07-20.
- **Auto-Rig Pro — Game Engine Export** (`ge_export_doc.html`) — lucky3d.fr — Humanoid vs Universal, checkbox Export Twist + Twist Amount (~0.5 para un twist), recomendación "Unity humanoid: 1 twist bone", Units x100, Root Motion (c_traj), Bake Animations, Mannequin Axes. Consultado 2026-07-20.
- Bases sintetizadas (no se repite su teoría): **[ver: modelado/topologia]** (loops de deformación, poles fuera de articulaciones, eje de flexión, aprobar posando), **[ver: modelado/organico-personajes §5-6]** (zonas que deforman, escuelas de hombro, bind pose A vs T, manos/dedos), **[ver: blender/import-export]** (qué exporta el FBX: shape keys sí, constraints solo horneados, Add Leaf Bones OFF, Apply Modifiers + shape keys = pérdida), **[ver: modelado/presupuestos-poligonos]** (MetaHuman 713→26 joints y 12→4 influencias por LOD; el skinning no se abarata con batching), **[ver: unity/animacion-unity]** (blendshapes por Direct blend tree, IK, validación con clip).
```
