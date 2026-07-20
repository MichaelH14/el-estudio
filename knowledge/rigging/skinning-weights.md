# Skinning y weight painting

> **Cuando cargar este archivo:** al pesar (skinnear) la malla de un personaje o criatura a su armature en Blender — hacer el bind inicial, pintar y limpiar weights, simetrizarlos, corregir deformación en articulaciones, y dejar los pesos listos para Unity (≤4 influencias, normalizados). El esqueleto y su jerarquía viven en [ver: esqueletos-armature]; la teoría de por qué una articulación deforma bien o mal, en [ver: deformacion]; la topología que hace posible la buena deformación, en [ver: modelado/organico-personajes §5]. Esto es el flujo concreto de pesar la malla.

Verificado contra el manual/UI de **Blender 5.2 LTS**, **Unity 6** (Manual + Scripting API) y la doc de **Auto-Rig Pro** (Artell). Los operadores `bpy.ops.object.vertex_group_*` y `parent_set` se citan por su nombre de API; docs.blender.org bloqueó el fetch en vivo durante la redacción, así que esos nombres salen de conocimiento del modelo cross-chequeado con la base ya verificada [ver: blender/edicion-malla] — probar en un `.blend` desechable si un operador vía MCP no responde como se describe.

## 1. Qué es el skinning

- **Skinning** = asociar cada vértice de la malla a uno o más huesos, con un **peso** (0.0–1.0). Al posar el hueso, el vértice se mueve una fracción proporcional a su peso. En Blender esto se guarda en **vertex groups**: un grupo por hueso, con el **mismo nombre exacto** que el hueso deform (§4).
- El algoritmo por defecto de Blender/Unity es **Linear Blend Skinning (LBS)**: la posición final del vértice es la media ponderada de las transformaciones de sus huesos influyentes. De ahí los dos problemas clásicos: **collapse/candy-wrapper** al torcer y **pérdida de volumen** al doblar (§6).
- **La suma de pesos de un vértice debe normalizarse a 1.0.** Si suma 0.5, el vértice solo recibe la mitad del movimiento (se "queda atrás"); si suma >1 se sobre-mueve. Blender puede autonormalizar al vuelo (Auto Normalize, §3) y al exportar; Unity **renormaliza** las 4 (o N) mayores. Normalizar explícito antes de exportar (§5) evita sorpresas.
- **Vértice sin ningún peso** = huérfano: queda clavado en su posición de rest mientras el resto se mueve (el síntoma "un pico de la malla se estira solo"). Detectarlo con **Fix Deforms** / Select > All by Trait, no a ojo.

## 2. El bind inicial: las cuatro rutas de `parent_set`

Seleccionar **primero la malla (o mallas), luego Shift-clic al armature** (activo al final), `Ctrl-P` → menú **Armature Deform**. Las cuatro variantes y su operador:

| Ruta (menú `Ctrl-P`) | `parent_set(type=…)` | Qué crea | Cuándo |
|---|---|---|---|
| **With Empty Groups** | `ARMATURE_NAME` | Un vertex group VACÍO por hueso deform, sin peso | Vas a pintar TODO a mano desde cero, o transferir weights de otra malla. Control total, cero automático |
| **With Envelope Weights** | `ARMATURE_ENVELOPE` | Peso por distancia a la cápsula (envelope) de cada hueso | Blockout, props mecánicos, criaturas simples. Rápido, tosco, poco control [ver: rigs-mecanicos] |
| **With Automatic Weights** | `ARMATURE_AUTO` | Bone-heat: proyecta "calor" de cada hueso a la superficie cercana | **El default para orgánicos.** Punto de partida que SIEMPRE se corrige a mano (§8) |
| **Armature Deform** (solo) | `ARMATURE` | Solo el modificador Armature; NINGÚN grupo | La malla YA tiene sus vertex groups (importada, o pesada aparte) |

Las cuatro añaden un **modificador Armature** apuntando al armature. Verificar en el modificador: **Vertex Groups** ON (usa los grupos), **Bone Envelopes** OFF salvo que uses envelopes de verdad (si ambos ON, se SUMAN y descuadran los pesos), **Preserve Volume** según §6.

```python
import bpy
# malla activa = objeto seleccionado primero; armature = objeto activo
mesh = bpy.data.objects["Character"]
arm  = bpy.data.objects["Armature"]
bpy.ops.object.select_all(action='DESELECT')
mesh.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm     # el activo es el PADRE
bpy.ops.object.parent_set(type='ARMATURE_AUTO') # With Automatic Weights
```

- **Automatic Weights (bone heat)** solo pesa a **huesos con Deform ON** (Bone Properties ‣ Deform). Huesos de control/IK con Deform OFF no ensucian los pesos [ver: ik-fk-constraints]. Falla ruidosamente en geometría **non-manifold, con caras interiores o piezas que se solapan**: error *"Bone Heat Weighting: failed to find solution for one or more bones"* → limpiar la malla [ver: blender/edicion-malla §6] o pasar a Voxel Heat (§8).
- **Envelopes:** el radio de influencia se ajusta en Pose/Edit Mode del armature con `Ctrl-Alt-S` (Scale Envelope) o en Bone Properties ‣ Deform ‣ Envelope (Head/Tail Radius, Distance). Útil para dar un peso base rápido que luego se hornea a vertex groups.

### El modificador Armature (lo que el bind deja en la malla)
| Opción | Efecto | Valor para juego |
|---|---|---|
| **Object** | El armature que deforma | El rig del personaje |
| **Vertex Groups** | Usa los grupos por nombre de hueso | **ON** (es donde viven tus pesos) |
| **Bone Envelopes** | Suma la influencia por envelope | **OFF** salvo rig de envelopes; con Vertex Groups ON los dos se SUMAN |
| **Preserve Volume** | Dual-quaternion skinning | Según §6 (anti candy-wrapper; puede inflar) |
| **Multi Modifier** | Mezcla con otro Armature | Raro en juego |

El armature alterna **Rest Position ↔ Pose Position** (Object Data ‣ Skeleton). En Rest, la malla vuelve a bind pose aunque haya pose puesta — el sitio seguro para editar geometría/UVs sin la deformación encima.

## 3. Weight Paint mode

Seleccionar la malla → **modo Weight Paint** (dropdown de modo, o `Ctrl-Tab`). El armature en Pose Position permite posar mientras pintas; **seleccionar un hueso con `Ctrl`-clic** en weight paint activa su vertex group (pintas sobre ese hueso).

### Leer el peso (código de color)
Espectro fijo: **azul = 0.0**, cian/verde = 0.25–0.5, amarillo = 0.75, **rojo = 1.0**. Overlay **Zero Weights ‣ Active** (marca en negro/rojo los vértices sin peso en el grupo activo) es el detector de huérfanos.

### Brushes (familias; desde 4.3 son **brush assets** de la librería)
| Brush | Qué hace | Uso |
|---|---|---|
| **Draw** (Paint) | Pinta hacia el valor **Weight** del header | El caballo de batalla: subir/bajar influencia |
| **Blur** | Promedia con los vecinos | Suavizar transiciones en la articulación (el antídoto #1 del deform duro) |
| **Average** | Iguala al peso medio bajo el brush | Aplanar una zona a un valor uniforme |
| **Smear** | Arrastra los pesos en la dirección del trazo | Empujar un borde de influencia sin repintar |

Ajustes del header/tool: **Weight** (0–1, el valor objetivo del Draw), **Radius**, **Strength**, y **Blend** (Mix/Add/Subtract/Multiply/Lighten/Darken…). **Sample Weight** (cuentagotas) copia el peso bajo el cursor al slider Weight.

### Gradiente
Tool **Gradient** (toolbar) o `bpy.ops.paint.weight_gradient(type='LINEAR')` / `'RADIAL'`: arrastrar traza un degradado de peso entre el valor inicial y 0 (o entre dos valores con la rampa activa). Ideal para el falloff largo de un hueso de torso o una cola.

### Opciones que cambian TODO (header ‣ Options / Weights)
| Opción | Efecto | Recomendado |
|---|---|---|
| **Auto Normalize** | Tras cada trazo, renormaliza el vértice a 1.0 repartiendo en los OTROS grupos deform | **ON** casi siempre para orgánicos (mantiene la suma sana mientras pintas) |
| **Lock-Relative** | Trata los grupos bloqueados como fijos y normaliza solo el resto | ON cuando "congelas" un hueso ya bueno y ajustas su vecino |
| **Multi-Paint** | Pinta sobre VARIOS grupos seleccionados como si fueran uno | Ajustar una región (varios dedos) de golpe |
| **Front Faces Only** | No atraviesa a la cara trasera | ON para no pintar el otro lado de una manga |
| **Falloff Shape** | Sphere (3D) vs Projected (2D, atraviesa profundidad) | Projected para pintar de lado a lado un miembro |

### Simetría X (obligatoria en bípedos)
Panel **Symmetry** ‣ **Mirror X** (o Y/Z). Con la malla **simétrica en el origen** y huesos nombrados `.L`/`.R`, pintar en el brazo izquierdo se refleja al derecho **en su grupo espejo** automáticamente. **Topology Mirror** hace el espejo por topología (no por coordenada) cuando la malla no es perfectamente simétrica en posición pero sí en conectividad — más lento, salva mallas ligeramente asimétricas.

## 4. Vertex groups y el contrato nombre↔hueso

- Panel **Object Data Properties ‣ Vertex Groups**. Un hueso deform mueve un vértice **solo si existe un grupo con su nombre EXACTO** (`upperarm.L` mueve al grupo `upperarm.L`). Renombrar un hueso sin renombrar el grupo rompe el skin en silencio.
- En **Edit Mode** se asignan/quitan pesos a mano: seleccionar vértices, elegir grupo, fijar **Weight** y **Assign** / **Remove**; útil para meter un valor exacto (1.0 a una pieza rígida).
- El **candado (Lock)** del grupo lo protege de Normalize/Clean/pintura — bloquear los huesos ya validados antes de tocar un vecino.
- **Piezas rígidas** (hebillas, placas de armadura, ojos, dientes): un solo grupo al 100% del hueso que las porta — nunca repartidas, o se doblan como goma [ver: modelado/organico-personajes §7]. Con Auto Normalize ON, seleccionar la pieza en Edit Mode → Weight 1.0 → Assign al hueso, y Clean el resto.

## 5. Limpieza de weights (el paso que hace el skin exportable a Unity)

Todo esto vive en el menú **Weights** de Weight Paint mode. `group_select_mode='BONE_DEFORM'` restringe la operación a los grupos de huesos deform (ignora grupos utilitarios).

| Operación | `bpy.ops.object.…` | Parámetros clave | Para qué |
|---|---|---|---|
| **Normalize All** | `vertex_group_normalize_all` | `group_select_mode`, `lock_active=True` | Suma de cada vértice = 1.0 en todos los grupos deform |
| **Limit Total** | `vertex_group_limit_total` | `limit=4` | **Recorta a ≤4 influencias por vértice — el límite de Unity** [ver: rig-a-unity] |
| **Clean** | `vertex_group_clean` | `limit=0.01`, `keep_single=True` | Borra pesos ínfimos (ruido) por debajo del umbral; `keep_single` evita dejar un vértice en cero |
| **Quantize** | `vertex_group_quantize` | `steps=4` | Redondea a escalones (útil para look toon/mecánico duro) |
| **Smooth** | `vertex_group_smooth` | `factor`, `repeat`, `expand` | Relaja los pesos con los vecinos (suaviza sin pintar) |
| **Levels** | `vertex_group_levels` | `offset`, `gain` | Sube/baja o contrasta el peso de un grupo entero |
| **Fix Deforms** | `vertex_group_fix` | — | Mueve vértices mal pesados a la posición deform correcta (diagnóstico) |
| **Limpiar huérfanos** | (Clean con `keep_single=False`) | — | Elimina grupos vacíos/pesos sueltos residuales del bind auto |

**Secuencia de cierre estándar antes de exportar** (verificada como orden operativo; ver el porqué del 4 en §10):

```python
import bpy
ob = bpy.context.object
bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
# 1) recorta a 4 influencias — límite de Unity
bpy.ops.object.vertex_group_limit_total(group_select_mode='BONE_DEFORM', limit=4)
# 2) borra el ruido que dejó el bind automático
bpy.ops.object.vertex_group_clean(group_select_mode='BONE_DEFORM', limit=0.001, keep_single=True)
# 3) renormaliza a 1.0 (Limit y Clean desbalancean la suma)
bpy.ops.object.vertex_group_normalize_all(group_select_mode='BONE_DEFORM', lock_active=False)
bpy.ops.object.mode_set(mode='OBJECT')
```

⚠️ **El orden importa:** Limit Total y Clean rompen la normalización → Normalize All va SIEMPRE al final. Si normalizas primero y recortas después, la suma vuelve a ≠1.

## 6. Calidad de deformación

La topología manda: sin loops en el pliegue, ningún peso salva el codo [ver: modelado/organico-personajes §5] [ver: deformacion]. Con la topología correcta, los weights la explotan:

- **Transiciones suaves en articulaciones:** en un codo, el peso debe pasar de 1.0 (antebrazo) a 0.0 (brazo) **repartido en varios loops**, no de golpe en un edge. Un salto duro = codo que se afila. Antídoto: brush **Blur** a lo largo del pliegue, o **Smooth** con repeat.
- **Candy-wrapper (envoltorio de caramelo):** la muñeca/antebrazo se pellizca al torcer 180° porque LBS interpola linealmente entre dos orientaciones opuestas. Tres remedios, combinables:
  1. **Huesos de twist/roll** que reparten la rotación en 2–3 tramos a lo largo del hueso (el peso de la torsión se distribuye) — la solución robusta para juego [ver: esqueletos-armature].
  2. **Preserve Volume** en el modificador Armature = **dual-quaternion skinning**: evita el colapso de volumen al torcer/doblar. Contra: puede **inflar** articulaciones; probar por personaje.
  3. **Corrective shape keys** disparadas por ángulo (driver) para el caso concreto — caro, solo héroes en cámara.
- **B-Bones (Bendy Bones):** subdividen un hueso en segmentos curvables para deformación tipo curva (dedos, cola, columna). Coste extra; en juego, la curvatura es una feature de render/deform de Blender que el formato de hueso FBX no representa — al exportar a Unity el hueso llega como transform recto normal y se pierde el bend (comportamiento esperado del pipeline FBX; **NO VERIFICADO contra una nota de release concreta** — probar el export en un caso real antes de depender de esto para un personaje).
- **Pérdida de volumen al doblar:** la parte interna del codo/rodilla se hunde. Se corrige con pesos que dejen algo de volumen (no llevar el interior a 0 tan rápido) + Preserve Volume, o corrective shapes.

Regla: **primero se arregla con topología y huesos de apoyo, después con pesos, y solo al final con shape keys.** Un peso no inventa geometría que no existe.

## 7. Simetrizar weights

Con malla **simétrica respecto al origen X** y huesos `.L`/`.R`:

- **Weights ‣ Mirror** → `bpy.ops.object.vertex_group_mirror(mirror_weights=True, flip_group_names=True, all_groups=False, use_topology=False)`. Copia el lado pintado al opuesto y cruza los nombres (`.L`↔`.R`). `all_groups=True` espeja TODOS los grupos de una vez (el flujo normal: pintar un lado entero, `all_groups` una vez).
- Si la malla no es perfectamente simétrica en coordenadas pero sí en topología, `use_topology=True` (Topology Mirror) hace el match por conectividad.
- Alternativa al pintar en vivo: **Mirror X** activo en el Symmetry panel (§3) refleja cada trazo al vuelo; Weights ‣ Mirror es el "espejar todo lo ya pintado" en un paso.
- **Naming `.L`/`.R`:** imprescindible. Sin el sufijo estándar, el espejo no encuentra el grupo destino. Convención de nombres de huesos: [ver: esqueletos-armature].

## 8. Weights por herramienta: auto vs manual

| Motor | Qué es | Fuerte / débil |
|---|---|---|
| **Blender Automatic Weights (bone heat)** | Nativo, `parent_set` `ARMATURE_AUTO`; calor desde el hueso a la superficie geodésica | Rápido y decente en malla limpia y cerrada. **Falla** con piezas solapadas, ropa por capas, geometría non-manifold (error de bone heat) |
| **Auto-Rig Pro ‣ Bind** | Botón **Bind** (malla + Shift armature). Motores: **Heat Maps** (default, malla estanca), **Voxelized** (topología compleja/ropa por capas; menos preciso en dedos), y opción **Voxel Heat Diffuse** (addon 3ero) | Opciones dirigidas: **Split Parts**, **Optimize High Res**, **Voxel Resolution**, **Refine Head Weights**, **Smooth Twist Weights**, **Improve Hips/Heel Weights**. Su doc dice explícito: tras el bind, **pintar a mano cada grupo** |
| **Voxel Heat Diffuse Skinning** (mesh-online) | Voxeliza el volumen y difunde el calor por el **voxel grid**, no por la superficie | Resuelve lo que el bone-heat de Blender no puede: **múltiples piezas separadas, geometría solapada/interior, non-manifold**. Versión/precio: NO VERIFICADO aquí (Superhive/GitHub; confirmar en la tienda) |

Ninguno entrega weights finales. **El auto es el 80%; el 20% de las articulaciones (hombro, cadera, axila, entrepierna, dedos) se corrige a mano** con Draw + Blur y test poses (§9). Auto-Rig Pro versión/precio 2026: confirmar en Blender Market/Superhive — NO VERIFICADO aquí.

### Transferir weights de otra malla (reuso)
Cuando ya tienes un cuerpo bien pesado y añades ropa, variantes o un LOD, no repintes: **transfiere**. `Weights ‣ Transfer Weights` en Weight Paint, o el modificador **Data Transfer** para hacerlo no-destructivo. Seleccionar la malla FUENTE (pesada) + la DESTINO como activa:

```python
import bpy
# activo = destino; el otro seleccionado = fuente
bpy.ops.object.data_transfer(
    data_type='VGROUP_WEIGHTS',
    vert_mapping='POLYINTERP_NEAREST',   # interpola por cara más cercana
    layers_select_src='NAME',            # empareja grupos por nombre de hueso
    layers_select_dst='ALL',
)
```

`vert_mapping='NEAREST'` (vértice más cercano) es más rápido pero salta; `POLYINTERP_NEAREST` suaviza. Tras transferir: Limit Total + Normalize (§5) y **retocar los bordes** donde la ropa se separa del cuerpo. Reglas de ropa que deforma sin clipping: [ver: modelado/organico-personajes §7].

## 9. Verificar la deformación posando (test poses ANTES de animar)

El skin no se aprueba en rest pose. En **Pose Mode** del armature, rotar huesos (`R`) al rango extremo y mirar la malla:

- **Checklist de poses** (las mismas que aprueban la retopo [ver: modelado/organico-personajes]): **brazo arriba** (hombro/axila), **sentadilla** (cadera/rodilla/entrepierna), **codo/rodilla a 90°+** (sin afilar ni hundir), **muñeca torcida** (candy-wrapper), **giro de cabeza** (cuello sin estirar la cara), **puño cerrado** (dedos).
- Buscar: pellizcos, vértices que se quedan clavados (huérfanos, §1), volumen que colapsa, la malla que atraviesa la ropa [ver: modelado/organico-personajes §7].
- Corregir en Weight Paint SIN salir de la pose (pintas viendo el defecto en vivo), volver a rest, re-probar. Iterar.
- **Volver el armature a Rest Position** (Object Data ‣ Skeleton) o resetear la pose (`Alt-R`/`Alt-G`) antes de exportar — no exportar con una pose de test aplicada.

Poner una pose de test headless (vía MCP) para renderizar y auditar el deform sin UI:

```python
import bpy, math
arm = bpy.data.objects["Armature"]
bpy.ops.object.mode_set(mode='POSE')
pb = arm.pose.bones["forearm.L"]
pb.rotation_mode = 'XYZ'
pb.rotation_euler = (0.0, math.radians(140), 0.0)  # doblar el codo 140°
bpy.context.view_layer.update()
# …render/screenshot y medir el pliegue; luego resetear:
bpy.ops.pose.select_all(action='SELECT')
bpy.ops.pose.transforms_clear()   # equivale a Alt-G/Alt-R/Alt-S
```

## 10. Skinning para Unity (el puente)

Los pesos que pintas solo llegan a Unity si respetan sus límites. Detalle del export FBX y sus flags en [ver: blender/import-export]; el rig completo hacia Mecanim/Humanoid en [ver: rig-a-unity].

| Concepto | Valor Unity | Consecuencia en Blender |
|---|---|---|
| **Skin Weights (Rig tab del importador)** | Default **Standard (4 Bones)**; Custom permite 1–32 huesos/vértice con umbral | Pesar por encima de 4 influencias es tirar trabajo: Unity descarta las menores. **Limit Total a 4** (§5) para que lo exportado = lo que Unity renderiza |
| **QualitySettings.skinWeights** (global) | `SkinWeights`: OneBone / TwoBones / **FourBones** / Unlimited | El nivel de calidad del proyecto **clampa** todo skinned mesh en runtime. Si el proyecto está en TwoBones, tu vértice de 4 influencias se ve con 2 |
| **SkinnedMeshRenderer.quality** (por renderer) | `SkinQuality`: **Auto** (usa el global) / Bone1 / Bone2 / Bone4 | Override por personaje: un héroe a Bone4 aunque el proyecto esté en 2 |
| **Humanoid Avatar** | Necesita **≥15 huesos** tipo humano; **T-pose** recomendada para el mapeo | Bind pose (T vs A) se acuerda con el rigger ANTES de pesar [ver: esqueletos-armature]; el Avatar remapea nombres, pero los pesos viajan por vertex group |
| **Optimize Game Objects** (Rig tab) | Quita la jerarquía de Transforms y la guarda en el Avatar | El skin sigue funcionando por el esqueleto interno; huesos expuestos como "extra transforms" solo los que necesites (sockets) |

**Contrato de export (flags que tocan el skin, detalle en [ver: blender/import-export]):** `add_leaf_bones=False` (no mete huesos `_end` basura), `use_armature_deform_only=True` (solo huesos deform → los grupos que pesaste; excluye control/IK). Aplicar transforms del armature en Object Mode sobre el **rest**, nunca con una pose puesta.

## Reglas prácticas

- [ ] Bind orgánico = **With Automatic Weights** (`ARMATURE_AUTO`); a mano desde cero = **With Empty Groups**; mecánico/blockout = **Envelopes**.
- [ ] Solo huesos con **Deform ON** reciben peso: control/IK con Deform OFF antes de bindear.
- [ ] Malla limpia (manifold, sin caras interiores, escala aplicada) ANTES del bind — el bone heat falla en lo sucio [ver: blender/edicion-malla §6].
- [ ] **Auto Normalize ON** mientras pintas orgánicos; la suma por vértice = 1.0 siempre.
- [ ] **Mirror X** + huesos `.L`/`.R` + malla simétrica: pinta un lado, espeja con Weights ‣ Mirror (`all_groups`).
- [ ] Piezas rígidas: 1 grupo al **100%** de su hueso, nunca repartidas.
- [ ] Transiciones de articulación **repartidas en varios loops** con Blur/Smooth, no saltos duros en un edge.
- [ ] Candy-wrapper → huesos de twist primero, **Preserve Volume** (dual-quat) después, corrective shapes al final.
- [ ] Cierre pre-export, **en este orden**: Limit Total 4 → Clean → **Normalize All al final**.
- [ ] **Limit Total = 4** siempre para Unity (Standard 4 Bones); pesar más es descartado por el engine.
- [ ] Verificar `QualitySettings.skinWeights` del proyecto Unity: si está en TwoBones, tus 4 influencias se ven con 2.
- [ ] **Aprobar posando:** brazo arriba, sentadilla, codo/rodilla, muñeca torcida, giro de cabeza, puño — NUNCA solo en rest.
- [ ] Detectar huérfanos con overlay Zero Weights / Fix Deforms; cero vértices sin peso al terminar.
- [ ] Auto (Blender/ARP/Voxel Heat) es el 80%: el hombro, cadera, axila, entrepierna y dedos SIEMPRE se corrigen a mano.
- [ ] Resetear a **Rest Position** y limpiar la pose de test antes de exportar; `add_leaf_bones=False`, `use_armature_deform_only=True`.
- [ ] Vía MCP/headless: tras cada operador de weights, contar influencias por vértice / comprobar la suma — un operador que "no hizo nada" también es bug [ver: rigging-en-blender-operativo].

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| *"Bone Heat Weighting: failed to find solution"* al bindear | Malla non-manifold / caras interiores / piezas solapadas → limpiar [ver: blender/edicion-malla §6], o usar Voxelized (ARP) / Voxel Heat Diffuse |
| Un pico de la malla se estira solo al posar | Vértice **huérfano** (suma 0). Overlay Zero Weights → pintar/Assign su hueso; Normalize All |
| La malla se mueve solo a medias, "se queda atrás" | Suma de pesos <1 → **Normalize All** (Auto Normalize estaba OFF al pintar) |
| Codo/rodilla se **afila** al doblar | Peso salta de golpe en un edge + faltan loops → Blur el pliegue; si no hay loops, es topología [ver: modelado/organico-personajes §5] |
| Muñeca/antebrazo se **pellizca** al torcer (candy-wrapper) | Huesos de twist que repartan la rotación; Preserve Volume (dual-quat) como refuerzo |
| Articulación **inflada** tras activar Preserve Volume | El dual-quat sobre-conserva; bajar, o volver a LBS + twist bones + corrective shape |
| El brazo derecho no refleja lo pintado en el izquierdo | Malla no simétrica en X, o huesos sin `.L`/`.R`, o Mirror X off → Topology Mirror / renombrar huesos |
| Deformación distinta en Unity vs Blender | Unity clampa a `skinWeights` del proyecto (o al 4 del importador). **Limit Total 4 + Normalize** en Blender y alinear la calidad del proyecto |
| Pieza de armadura que se **dobla como goma** | Estaba repartida en varios huesos → 1 grupo al 100% de su hueso |
| Huesos de control/IK "moviendo" la malla o grupos basura | Tenían Deform ON → apagar Deform y re-bindear, o `use_armature_deform_only=True` al exportar |
| Suma ≠1 tras "limpiar" los pesos | Limit/Clean rompen la normalización → **Normalize All SIEMPRE al final** |
| Exporté con una pose de test puesta y el rig sale deformado | Rest Position + `Alt-R`/`Alt-G` antes de exportar; aplicar transforms sobre el rest |
| Ambos Vertex Groups y Bone Envelopes ON en el modificador → pesos raros | Se suman; dejar solo Vertex Groups salvo que uses envelopes de verdad |
| Bind automático "listo" sin revisar | El auto es el 80%; sin test poses no está pesado — aprobar posando (§9) |

## Fuentes

- **Auto-Rig Pro — Documentation (Skinning)** — lucky3d.fr/auto-rig-pro/doc/auto_rig.html (Artell) — botón **Bind**, motores **Heat Maps / Voxelized / Voxel Heat Diffuse**, opciones (Split Parts, Optimize High Res, Voxel Resolution, Refine Head/Improve Hips/Heel/Smooth Twist), y la indicación explícita de corregir a mano tras el bind. Versión/precio 2026: NO VERIFICADO (confirmar en Blender Market/Superhive).
- **Auto-Rig Pro — Documentation (index)** — lucky3d.fr/auto-rig-pro/doc/ — estructura (Skinning, Game Engine Export, Remap, Quick Rig); footer © 2016–2023 Artell.
- **Unity Manual — Configuring the Avatar** — docs.unity3d.com/Manual/ConfiguringtheAvatar.html — Humanoid requiere ≥15 huesos tipo humano, T-pose para el mapeo, Skin Weights limita a 4 huesos por vértice por defecto.
- **Unity Manual — Rig tab (Model Importer)** — docs.unity3d.com/Manual/FBXImporter-Rig.html — Animation Type (Humanoid/Generic/Legacy/None), **Skin Weights = Standard (4 Bones)** default, Custom 1–32, **Optimize Game Objects** (quita la jerarquía de Transforms al Avatar/Animator).
- **Unity Manual — Quality Settings** — docs.unity3d.com/Manual/class-QualitySettings.html — Skin Weights ("número de huesos que afectan a un vértice durante la animación") como ajuste global de calidad.
- **Unity Scripting API — SkinnedMeshRenderer.quality / SkinQuality** — docs.unity3d.com/ScriptReference/SkinnedMeshRenderer-quality.html — `SkinQuality` (Auto/Bone1/Bone2/Bone4) por renderer; `QualitySettings.skinWeights` como default de proyecto; coste por encima de 4.
- **Voxel Heat Diffuse Skinning (mesh-online)** — Superhive/GitHub — skinning por difusión de calor en voxel grid (resuelve piezas separadas, geometría solapada y non-manifold que el bone-heat de Blender no puede); citado también por la doc de ARP como motor alternativo. Versión/precio: NO VERIFICADO.
- **Base propia sintetizada:** [ver: blender/edicion-malla] (limpieza de malla y operadores `bpy.ops.mesh.*` verificados contra Blender 5.2; convención de nombres de operadores), [ver: modelado/organico-personajes] (topología de zonas que deforman, poses de aprobación, piezas rígidas a un hueso, bind pose T vs A, 4 influencias máx. Unity), [ver: blender/import-export] (flags de export FBX: `add_leaf_bones`, `use_armature_deform_only`, transforms sobre rest), [ver: unity/animacion-unity] (Humanoid vs Generic, coste de skinning, Optimize).
