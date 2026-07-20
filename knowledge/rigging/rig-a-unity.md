# Del rig a Unity: Humanoid, Generic y retargeting

> **Cuando cargar este archivo:** al sacar un personaje/criatura riggeado de Blender hacia Unity y decidir Animation Type (Humanoid vs Generic vs Legacy vs None), configurar el Avatar y su mapeo de huesos, montar retargeting (compartir animaciones, Mixamo), root motion, Optimize Game Objects o Avatar Masks. También al diagnosticar un rig que en Unity deforma mal, no mapea a Humanoid, o llega con huesos basura/escala rara.

Este archivo es el PUENTE rig↔Unity. El export FBX genérico (escala, ejes -89.98, roundtrip de prefab) vive en [ver: blender/import-export]; el consumo de la animación una vez importada (Animator, blend trees, layers, IK, culling) en [ver: unity/animacion-unity]. Aquí solo el flujo específico de esqueleto + Avatar + los settings correctos para que Unity acepte el rig.

## Panorama: las tres decisiones que definen el pipeline

| Decisión | Dónde se toma | Consecuencia |
|---|---|---|
| Qué huesos deforman y cómo se nombran | Blender (armature) [ver: esqueletos-armature] [ver: skinning-weights] | Determina si Humanoid puede auto-mapear |
| Solo-deform + no leaf bones + ejes | Export FBX en Blender | Rig limpio en Unity, sin huesos `_end` ni control bones |
| Humanoid vs Generic | Rig tab del Model importer en Unity | Retargeting sí/no, coste, root motion, IK humanoide |

Regla base: **Humanoid** para bípedos que van a compartir animaciones o usar Mixamo; **Generic** para todo lo demás (animales, mecánicos, cualquier esqueleto). El coste de Generic es menor; Humanoid solo se justifica por retargeting o IK humanoide (`OnAnimatorIK`) [ver: unity/animacion-unity].

---

## 1. Preparar el rig en Blender para que Unity lo acepte

Antes de exportar, el armature tiene que cumplir el contrato de Unity. Nada de esto es opcional si quieres Humanoid limpio.

| Requisito | Por qué | Cómo en Blender |
|---|---|---|
| Solo huesos de deformación viajan | Los control bones (IK, poles, root de control) ensucian el esqueleto de Unity | Marcar deform en los que pesan, `use_armature_deform_only` en export [ver: ik-fk-constraints] |
| Jerarquía bípeda estándar | Humanoid mapea por estructura: 1 hips → spine → chest → neck → head, 2 brazos, 2 piernas | Armar la cadena canónica [ver: esqueletos-armature] |
| Naming claro y simétrico | Sube la tasa de auto-map de Unity ("LeftArm"/"RightForearm" mapean solos) | Sufijos `.L`/`.R`; nombres descriptivos, no `Bone.003` |
| T-pose en el rest (brazos rectos a los lados formando "T") | Unity exige T-pose para calcular el Avatar; A-pose se puede corregir con Enforce T-Pose pero es fricción | Modelar/riggear en T-pose desde el inicio |
| Weights ≤ 4 por vértice | Unity capea a 4 influencias por defecto (Skin Weights = Standard) | Limit Total a 4 + normalizar [ver: skinning-weights] [ver: deformacion] |
| Escala 1 y transforms aplicados | Evita el 100× y deformación torcida | `Ctrl+A ‣ All Transforms` en Object Mode sobre el rest, nunca en pose [ver: blender/import-export] |

**Deform vs control bones:** en Blender cada hueso tiene la propiedad **Deform** (`bone.use_deform`, panel Bone ‣ Deform). Solo los huesos con Deform ON y con vertex group asociado mueven malla. Los huesos de control (IK targets, pole targets, la raíz de control) van con Deform OFF y no deben llegar al FBX. Rigify ya separa esto: solo la capa `DEF-` deforma; `ORG-`/`MCH-`/controles no [ver: rigify].

### Snippets bpy verificados (Blender 5.2)

Crear armature y un hueso raíz de deform, headless:

```python
import bpy
bpy.ops.object.armature_add(enter_editmode=True, location=(0, 0, 0))
arm = bpy.context.object
arm.name = "Armature_Hero"
eb = arm.data.edit_bones
root = eb[0]; root.name = "Hips"; root.head = (0, 0, 1.0); root.tail = (0, 0, 1.15)
spine = eb.new("Spine"); spine.head = root.tail; spine.tail = (0, 0, 1.4); spine.parent = root
for b in eb:
    b.use_deform = True          # marcar deform en los huesos que pesan
bpy.ops.object.mode_set(mode='OBJECT')
```

Parentear la malla al armature con pesos automáticos (heat map). El orden importa: malla(s) seleccionadas, armature ACTIVO al final:

```python
mesh = bpy.data.objects["Hero_Body"]
mesh.select_set(True); arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.parent_set(type='ARMATURE_AUTO')   # Parent > With Automatic Weights
```

Limitar y normalizar pesos para el cap de 4 de Unity (Object Mode, malla activa):

```python
bpy.context.view_layer.objects.active = mesh
bpy.ops.object.vertex_group_limit_total(limit=4)              # Limit Total: máx 4 huesos/vértice
bpy.ops.object.vertex_group_normalize_all(lock_active=False) # que cada vértice sume 1.0
```

Los pesos automáticos son punto de partida, no final: casi siempre hay que pintar a mano codos, hombros, cadera y axilas [ver: skinning-weights] [ver: rigging-en-blender-operativo].

---

## 2. Export FBX con armature: settings específicos del rig

Los settings generales de escala/ejes/roundtrip están en [ver: blender/import-export]. Aquí SOLO lo que cambia por tener armature. `bpy.ops.export_scene.fbx`:

| Sección | Opción UI | Propiedad bpy | Valor rig→Unity | Nota |
|---|---|---|---|---|
| Include | Object Types | `object_types` | `{'ARMATURE','MESH','EMPTY'}` | Fuera cámaras/luces |
| Armature | **Only Deform Bones** | `use_armature_deform_only` | **ON** | Descarta control/IK bones; solo lo que deforma llega a Unity |
| Armature | **Add Leaf Bones** | `add_leaf_bones` | **OFF** | ON (default) mete huesos `_end` basura por cada punta; rompe conteos y ensucia el mapeo |
| Armature | **Primary Bone Axis** | `primary_bone_axis` | **Y** (default) | Eje a lo largo del hueso |
| Armature | **Secondary Bone Axis** | `secondary_bone_axis` | **X** (default) | Eje del roll |
| Armature | Armature FBXNode Type | `armature_nodetype` | `NULL` (default) | `Root`/`LimbNode` solo si otro DCC lo exige |
| Transform | Apply Transform | `bake_space_transform` | **OFF** | Experimental; "known to be broken with armatures/animations" — JAMÁS con rig |
| Bake Animation | Bake Animation | `bake_anim` | ON si exportas clips | Ver convención `@` en [ver: blender/import-export] |

**Primary/Secondary Bone Axis — la verdad calibrada:** los huesos de Blender apuntan a lo largo de su Y local; el FBX guarda su orientación con estos dos ejes. Para **Humanoid** el ajuste es casi irrelevante: el muscle system normaliza la orientación de cada hueso contra el Avatar, así que diferencias de roll/eje se abstraen (por eso Humanoid "perdona" rigs de orígenes distintos). Para **Generic** sí importan: un eje mal puesto puede dar rotaciones raras porque Generic reproduce la orientación literal del hueso. Recomendación: **dejar los defaults (Primary Y, Secondary X)** salvo que el destino exija otra cosa; no tocarlos "por si acaso".

**El -89.98 y el rig:** la rotación de -90° en X (conversión Z-up→Y-up) es cosa del objeto raíz, no del esqueleto, y con armatures se ACEPTA o se resuelve con **Bake Axis Conversion** del Model tab en Unity 6 — nunca con Apply Transform en el export (rompe el rig). Detalle completo en [ver: blender/import-export].

---

## 3. El Rig tab del Model importer (Unity 6)

Al seleccionar el `.fbx` en `Assets/`, pestaña **Rig**. El campo maestro es **Animation Type**:

| Animation Type | Qué es | Cuándo |
|---|---|---|
| **None** | Sin animación; solo malla | Props, escenografía, cualquier modelo estático [ver: blender/import-export] |
| **Legacy** | Sistema de animación viejo (Unity 3.x, `Animation` component) | Solo mantenimiento de proyectos antiguos; NO usar en proyectos nuevos |
| **Generic** | Mecanim sobre CUALQUIER esqueleto, sin semántica humana | Animales, mecánicos, criaturas, bípedos que no comparten animación |
| **Humanoid** | Mecanim + Avatar + muscle system, semántica bípeda | Personajes humanoides con retargeting / Mixamo / IK humanoide |

Campos que aparecen según el tipo:

| Campo | Aplica a | Función |
|---|---|---|
| **Avatar Definition** | Generic, Humanoid | `Create From This Model` (genera Avatar propio) vs `Copy From Other Avatar` (reusa el Avatar de otro modelo — clave para que N clips compartan esqueleto) |
| **Root node** | **Generic** | Qué hueso es la raíz de animación/root motion (ver §6) |
| **Configure…** | **Humanoid** | Abre el editor del Avatar (mapeo de huesos). Solo con `Create From This Model` |
| **Skin Weights** | ambos | Cap de influencias por vértice: `Standard` (4) o `Custom` (1–32) |
| **Strip Bones** | ambos | Excluye del SkinnedMeshRenderer los huesos sin peso |
| **Optimize Game Objects** | ambos | Colapsa la jerarquía de Transforms de huesos (ver §7) |

Los archivos de **animación** (`modelo@walk.fbx`) que comparten esqueleto se ponen en **`Copy From Other Avatar`** apuntando al Avatar del modelo base: así todos usan el MISMO Avatar y las animaciones son intercambiables [ver: blender/import-export].

---

## 4. Humanoid a fondo: Avatar, muscles y el superpoder del retargeting

### El Avatar y el mapeo de huesos
El **Avatar** es la tabla de correspondencia entre TUS huesos y el esqueleto abstracto humano de Unity. Se configura con **Configure…** (entra a Avatar Configuration mode):

- Unity exige **≥15 huesos** organizados como un esqueleto humano. **Required** (círculo sólido): Hips, Spine, Head, y por lado Upper/Lower Leg, Foot, Upper/Lower Arm, Hand. **Optional** (círculo punteado): Chest, UpperChest, Neck, Shoulders, Toes, dedos, ojos, mandíbula — mejoran calidad pero no son obligatorios.
- Mapeo correcto = **verde**; incorrecto = **rojo**; un **check junto a Configure** en el Rig tab significa que todos los required matchean.
- Botones de rescate si el auto-map falla: **Mapping ‣ Automap** (deduce del pose inicial), **Mapping ‣ Clear**, **Pose ‣ Sample Bind-Pose**, **Pose ‣ Enforce T-Pose**. También se arrastran huesos a mano desde la Hierarchy.
- **Human Template (`.ht`)**: guarda el mapeo hueso→Avatar para reusarlo en personajes con el mismo naming — oro si tienes una convención de rig estable.
- Pestañas: **Mapping** (los huesos) y **Muscles & Settings**.

### El muscle system
En vez de rotaciones crudas por hueso, Humanoid describe la pose en **muscle space**: valores normalizados por rango de movimiento articular. Eso es lo que hace posible el retargeting (una pose "brazo arriba" es la misma en cualquier cuerpo). En **Muscles & Settings**:

- **Muscle Group Preview**: mueve grupos enteros para ver el rango.
- **Per-Muscle**: limita el rango de cada articulación (p.ej. Head-Nod/Head-Tilt vienen -40 a 40°, se pueden estrechar para evitar deformaciones feas).
- **Additional Settings ‣ Translate DoF**: activa traslación (no solo rotación) en Chest, UpperChest, Neck, Upper Legs, Shoulders. **Cuesta rendimiento** (paso extra de retargeting) — activarlo SOLO si los clips realmente traen traslación en esos huesos.

### Retargeting: el superpoder
Como Humanoid trabaja en muscle space, **la misma animación corre en cualquier personaje Humanoid** aunque las proporciones difieran. Requisitos:

- Ambos modelos en **Humanoid** con Avatar válido.
- Comparten el **Animator Controller**; cada modelo lleva su propio `Animator` + su propio Avatar.

Patrón de intercambio de personaje (de la doc de retargeting):

```
CharacterRoot (scripts, CharacterController)
 ├─ ModelA (Animator → Avatar A) ── mismo Animator Controller
 └─ ModelB (Animator → Avatar B) ── mismo Animator Controller
```

`GetComponentInChildren<Animator>()` para hallar el activo; ajustar el CharacterController a las proporciones de cada modelo.

**Mixamo (Adobe, gratis):** auto-rigger + librería de animaciones humanoides. Flujo: descargas el FBX de Mixamo, en Unity pones **Animation Type = Humanoid**, y sus clips retargetean a TU personaje vía Avatar compartido. Es la fuente de retargeting gratis más usada. (Los rigs de Mixamo son A-pose-friendly y mapean solos a Humanoid por su naming estándar `mixamorig:`.)

---

## 5. Generic a fondo: cualquier esqueleto, sin magia semántica

Generic corre Mecanim sin entender qué hueso es qué: reproduce las rotaciones literales del esqueleto. Es la opción correcta para:

- Animales / cuadrúpedos, criaturas, bípedos no-humanos.
- Rigs mecánicos (brazos robóticos, torretas, maquinaria) [ver: rigs-mecanicos].
- Bípedos humanoides que **nunca** compartirán animación (un solo personaje con sus propios clips): Generic es más barato.

Lo que Generic NO da: retargeting automático entre esqueletos distintos ni IK humanoide (`OnAnimatorIK` con `AvatarIKGoal`). Para IK sobre Generic se usa el paquete **Animation Rigging** (Two Bone IK, Multi-Aim) [ver: unity/animacion-unity].

Lo único que Generic pide: **Root node** — el hueso que actúa como raíz para blending y root motion (ver §6). Si dos clips Generic deben mezclarse coherentemente, tienen que declarar el mismo Root node.

---

## 6. Root motion

**Root motion** = el movimiento del personaje sale de la animación, no de un script que mueve el transform. Conceptos:

| Término | Qué es |
|---|---|
| **Body Transform** | Centro de masa del personaje; el modelo de desplazamiento más estable. En Humanoid se guarda en muscle space |
| **Root Transform** | Proyección del Body Transform sobre el plano Y (horizontal), calculada en runtime. Su delta por frame mueve el GameObject |
| **Root Node** (Generic) | Reemplaza al Body Transform: Generic usa este hueso para computar el Root Transform |
| **Apply Root Motion** | Checkbox del componente `Animator`: si ON, la animación mueve el GameObject; si OFF, el movimiento del root se ignora (lo mueve tu código) |

En el **Inspector del clip** (Model ‣ Animation ‣ el clip), tres controles de proyección con su **Bake Into Pose**:

| Control | Bake Into Pose ON = | Uso típico |
|---|---|---|
| **Root Transform Rotation** | La orientación queda en la pose; el GameObject NO gira por el clip | Clips donde el giro lo maneja el código |
| **Root Transform Position (Y)** | El movimiento vertical queda en la pose; sin cambios de altura (además dirige `Animator.gravityWeight`) | Idles, walks que no deben subir/bajar el objeto |
| **Root Transform Position (XZ)** | El desplazamiento horizontal queda en la pose | **Idles**: evita el drift posicional a lo largo del loop |

Regla mental: **Bake Into Pose = "que esto NO salga del clip al GameObject"**. Un walk con root motion real deja Position (XZ) sin bakear (para que avance) pero suele bakear Rotation e Y.

**Based Upon** (origen de referencia): `Body Orientation` (forward del cuerpo, default para mocap), `Original` (respeta el offset autorado), `Feet` (solo Position Y, evita flotar al blendear), `Mass Center`, `Offset` (ajuste manual). Además **Loop Match**/Loop Pose blende las diferencias de pose inicio↔fin en el marco del Root Transform.

**Generic + root motion con Auto-Rig Pro:** ARP hornea la animación del controlador de trayectoria (`c_traj`) al objeto armature al exportar, y en Unity pones **Root Node = "root"** en el Rig tab para que el root motion funcione (ver §8).

---

## 7. Optimize Game Objects: rendimiento vs acceso

**Optimize Game Objects** (Rig tab) borra la jerarquía de Transforms de los huesos del prefab importado: el skeleton pasa a vivir en una estructura interna optimizada del sistema de animación en vez de un GameObject por hueso. Gran ahorro de CPU (menos Transforms que actualizar por frame) — importante con muchos personajes en pantalla [ver: unity/rendimiento-unity].

**Trade-off:** sin GameObjects de hueso NO puedes, desde script/escena:
- Anclar objetos a un hueso (arma en la mano, casco en la cabeza).
- Poner colliders/ragdoll o targets de Animation Rigging sobre huesos.
- Leer/escribir la Transform de un hueso.

**Solución quirúrgica: Extra Transforms to Expose.** Al activar Optimize aparece la lista **Extra Transforms to Expose**: marcas SOLO los huesos que necesitas como Transform (mano derecha, cabeza, un par de attach points) y esos sobreviven; el resto se colapsa. Es lo mejor de ambos: rig optimizado + los pocos anclajes que el gameplay usa.

Complementos del mismo panel:
- **Strip Bones**: quita del SkinnedMeshRenderer los huesos que no tienen peso (menos ruido).
- **Skin Weights = Standard (4)** salvo que el rig necesite más (Custom hasta 32, más caro).

Toggle por script (editor/runtime): `AnimatorUtility.OptimizeTransformHierarchy(go, exposedPaths)` y `DeoptimizeTransformHierarchy(go)` — útil para exponer temporalmente un hueso y re-optimizar.

---

## 8. Avatar Mask: animar por capas / stripear curvas

Un **Avatar Mask** define qué partes del cuerpo participan en una animación. Dos usos [ver: unity/animacion-unity]:

1. **En layers del Animator**: layer base = cuerpo completo; layer superior con mask de torso/brazos = disparar/lanzar mientras camina.
2. **En el import del clip** (Model ‣ Animation ‣ Mask): stripea permanentemente las curvas de las partes excluidas → menos memoria y CPU.

Dos formas de definir el mask según el tipo de Avatar:

| Modo | Para | Cómo |
|---|---|---|
| **Humanoid body** | Avatares Humanoid | Diagrama del cuerpo: verde = incluir, rojo = excluir, sobre 8 zonas (Head, L/R Arm, L/R Hand, L/R Leg, Root) + toggles de IK para manos/pies. Doble-click en vacío = todo/nada |
| **Transform hierarchy** | Generic / no-humanoid | Asignar el Avatar de referencia, **Import Skeleton**, y marcar los huesos concretos a incluir |

En la lista de layers, la **"M"** indica que la layer tiene máscara activa. El peso de layer 0 = la layer se salta entera (gratis) [ver: unity/animacion-unity].

---

## 9. Atajo con Auto-Rig Pro (2026)

Auto-Rig Pro es un addon de pago para Blender que genera rig humanoide/universal con Smart auto-detección y trae su propio exportador FBX pensado para engines. (Addon de pago en Blender Market; **precio y versión exacta 2026 NO verificados en esta sesión** — confirmar en la store antes de citar.)

`File ‣ Export ‣ Auto-Rig Pro FBX/GLTF` con el armature seleccionado. Settings relevantes:

| Opción ARP | Función | Equivalente manual |
|---|---|---|
| **Humanoid** (export type) | Renombra/reordena huesos a estructura que Unity Humanoid mapea solo; transfiere pesos de huesos faciales/metacarpianos | Naming + jerarquía bípeda a mano |
| **Universal** | Cualquier criatura (cuadrúpedos, etc.) → Unity Generic | Rig genérico |
| **Selected Bones Only** | Controla qué huesos de deform exportan; transfiere pesos al padre al excluir | `use_armature_deform_only` |
| **Units x100** | Escala ×100 → escala inicial 1.0 en Unity | `apply_scale_options='FBX_SCALE_UNITS'` [ver: blender/import-export] |
| **Bake Axis Conversion** | Ejes/escala para cumplir el Bake Axis Conversion de Unity | Aceptar/bakear el -89.98 en Unity |
| **Rename Bones** | Mapeo de nombres vía `.txt`/text block: `base = nuevo` | Renombrar huesos a mano |

**Unity Tips de ARP:** Humanoid "no soporta huesos extra por defecto" ni twist bones nativos (workaround con masks o plugins); asegurar ≤4 huesos por vértice o subir Skin Weights a Unlimited. Para root motion Generic, ARP hornea `c_traj` y pide **Root Node = "root"** en Unity.

---

## 10. Checklist de validación EN Unity (no basta con "el export no dio error")

1. **Rig tab**: check verde junto a Configure (Humanoid) o Root node asignado (Generic).
2. **Escala**: root del modelo (1,1,1), Model tab File Scale = 1 (si 0.01, faltó FBX Units Scale) [ver: blender/import-export].
3. **Sin huesos basura**: ningún `_end`/leaf en la jerarquía (si aparecen: reexportar con Add Leaf Bones OFF) ni control/IK bones (Only Deform Bones OFF).
4. **Mapeo Humanoid**: todos los required en verde; T-pose correcta (Enforce T-Pose si hace falta); comparar contra un cubo de 1 m / cápsula 2 m.
5. **Deformación**: reproducir un clip y mirar codos/hombros/cadera/axilas bajo luz — sin colapsos ni candy-wrapper (si mal: repintar weights en Blender, no parchear en Unity) [ver: skinning-weights].
6. **Skin Weights**: ≤4 por vértice (o Custom consciente); Quality del SkinnedMeshRenderer coherente.
7. **Retargeting**: si es Humanoid, meter una animación de Mixamo/otro personaje y verificar que corre sin romperse.
8. **Root motion**: `Apply Root Motion` según diseño; el personaje avanza/gira como el clip (o el código lo mueve si baked).
9. **Optimize Game Objects**: si está ON, confirmar que los attach points necesarios están en Extra Transforms to Expose.
10. **Consola limpia**: sin warnings del importer ("no valid humanoid", "Transform ... not found", conflictos de nombres).

---

## Reglas prácticas

1. Humanoid solo si hay retargeting / Mixamo / IK humanoide; si no, Generic (más barato). None para estáticos, Legacy nunca en proyectos nuevos.
2. Modelar y riggear en **T-pose** desde el inicio: ahorra el Enforce T-Pose y evita Avatares torcidos.
3. Solo huesos con **Deform ON** pesan; export con **Only Deform Bones ON** + **Add Leaf Bones OFF**, siempre, en cualquier rig.
4. Primary/Secondary Bone Axis: dejar defaults (Y/X); Humanoid los abstrae, Generic los respeta — no tocarlos sin razón.
5. **Apply Transform (`bake_space_transform`) JAMÁS con armature** (rompe rig/animación) — el -89.98 se resuelve con Bake Axis Conversion en Unity [ver: blender/import-export].
6. Naming simétrico y descriptivo (`.L`/`.R`, "LeftArm") = auto-map de Humanoid casi gratis; guardar el mapeo como Human Template `.ht` para reusar.
7. Weights: **Limit Total 4 + Normalize All** en Blender antes de exportar; Skin Weights = Standard salvo necesidad real.
8. Clips de animación (`modelo@anim.fbx`) → **Copy From Other Avatar** al Avatar del modelo base: mismo esqueleto, animaciones intercambiables.
9. Root motion: **Bake Into Pose = "esto no sale al GameObject"**. Idles: bakear XZ (anti-drift). Walk que avanza: XZ sin bakear.
10. `Apply Root Motion` en el Animator ON solo si la animación mueve al personaje; si lo mueve tu código, OFF.
11. Generic: declarar **Root node** coherente entre clips que blendean; sin él, no hay root motion ni blending consistente.
12. **Optimize Game Objects** para muchos personajes; exponer SOLO los huesos que el gameplay ancla (mano, cabeza) en Extra Transforms to Expose.
13. Avatar Mask por capas para tren superior/inferior; en Humanoid por zonas del cuerpo, en Generic por jerarquía de huesos [ver: unity/animacion-unity].
14. Translate DoF (Muscles & Settings) OFF salvo que los clips traigan traslación real: cuesta rendimiento.
15. No renombrar huesos tras el primer import: rompe el Avatar y todos los clips que lo copian [ver: blender/import-export].
16. Validar en Unity de verdad (deformar, retargetear, mover) — no dar por bueno un rig porque el FBX importó sin error.

## Errores comunes

| Pitfall | Síntoma en Unity | Antídoto |
|---|---|---|
| Add Leaf Bones ON (default) | Huesos `_end` por cada punta; conteos raros | `add_leaf_bones=False` |
| Control/IK bones exportados | Esqueleto lleno de huesos que no deforman; mapeo confuso | `use_armature_deform_only=True` + Deform OFF en controles [ver: ik-fk-constraints] |
| Rig en A-pose sin corregir | Humanoid no valida o brazos torcidos | Pose ‣ Enforce T-Pose, o modelar en T-pose |
| Required bones en rojo / "no valid humanoid" | Check gris, retargeting imposible | Mapear a mano los required; naming descriptivo; Automap |
| >4 influencias por vértice con Skin Weights=Standard | Deformación pierde influencias, se ve "tieso" | Limit Total 4 en Blender, o Skin Weights=Custom/Unlimited (coste) |
| Weights automáticos sin repintar | Axilas/codos/cadera colapsan al animar | Pintar weights a mano post auto-weights [ver: skinning-weights] |
| Apply Transform con armature | Rig/animación doblados o rotos | Nunca `bake_space_transform`; Bake Axis Conversion en Unity |
| Optimize Game Objects sin exponer huesos | El arma/casco no se puede anclar; Animation Rigging sin targets | Extra Transforms to Expose para los huesos que el gameplay usa |
| Root motion no avanza / patina | Personaje "corre en el sitio" o derrapa | Revisar Bake Into Pose de Position XZ y `Apply Root Motion` en el Animator |
| Idle que deriva de posición en loop | El personaje se va desplazando parado | Root Transform Position (XZ) → Bake Into Pose ON |
| Generic sin Root node | Sin root motion, blending inconsistente | Asignar el hueso raíz en Root node (ARP: "root") |
| Cada clip genera su Avatar | Retargeting roto entre clips del mismo personaje | Clips en Copy From Other Avatar apuntando al Avatar base |
| Translate DoF ON innecesario | Coste de retargeting extra sin beneficio | Dejarlo OFF salvo traslación real en los clips |
| Renombrar huesos tras importar | Avatar inválido, MeshFilters/curvas perdidas | Congelar naming del rig tras el primer import |
| Confiar en el import de `.blend` para rigs | Rompe en CI/máquinas sin Blender; acoplado a la versión local | Exportar FBX explícito [ver: blender/import-export] |

## Fuentes

- **Unity Manual 6000.2 — Rig tab (Model importer)** (`FBXImporter-Rig.html`) — Unity Technologies — Animation Type (None/Legacy/Generic/Humanoid), Avatar Definition (Create/Copy), Root node, Skin Weights, Strip Bones, Optimize Game Objects, Extra Transforms to Expose, botón Configure.
- **Unity Manual 6000.2 — Configuring the Avatar** (`ConfiguringtheAvatar.html`) — Unity Technologies — mínimo ~15 huesos, required vs optional, verde/rojo, T-pose, Automap/Clear/Sample Bind-Pose/Enforce T-Pose, naming recomendado.
- **Unity Manual 6000.2 — Avatar Mapping tab** (`class-Avatar.html`) — Unity Technologies — círculos sólidos/punteados, Human Template `.ht`, acceso a Muscles & Settings.
- **Unity Manual 6000.2 — Muscle Definitions / Muscles & Settings** (`MuscleDefinitions.html`) — Unity Technologies — muscle space, Muscle Group Preview, rangos por músculo (Head-Nod/Tilt -40..40), Translate DoF y su coste.
- **Unity Manual 6000.2 — Retargeting** (`Retargeting.html`) — Unity Technologies — misma animación en modelos distintos, requisito de Avatar Humanoid, patrón parent+child con Animator Controller compartido.
- **Unity Manual 6000.2 — Root Motion / Root Transform** (`RootMotion.html`) — Unity Technologies — Body vs Root Transform, Apply Root Motion, Bake Into Pose (Rotation/Y/XZ), Based Upon, Loop Pose, Root Node en Generic.
- **Unity Manual 6000.2 — Avatar Mask** (`class-AvatarMask.html`) — Unity Technologies — Humanoid body (8 zonas) vs Transform hierarchy (Import Skeleton), uso en layers y en import.
- **Unity Manual 6000.2 — Skinned Mesh Renderer** (`class-SkinnedMeshRenderer.html`) — Unity Technologies — Quality (bones/vértice), Update When Offscreen, Root Bone, Bounds.
- **Auto-Rig Pro — Game Engine Export** (`lucky3d.fr/auto-rig-pro/doc/ge_export_doc.html`) — Lucky3D — export Humanoid vs Universal, Units x100, Bake Axis Conversion, Rename Bones, Selected Bones Only, root motion Generic (`c_traj`→Root Node "root"), Unity Tips (huesos extra/twist, ≤4 influencias). Precio/versión 2026 NO verificados aquí.
- **Base sintetizada — [ver: blender/import-export]** — export FBX (escala 100×/FBX Units Scale, -89.98/Bake Axis Conversion, convención `modelo@anim.fbx`, roundtrip de prefab, Add Leaf Bones/Only Deform).
- **Base sintetizada — [ver: unity/animacion-unity]** — Animator, layers + Avatar Mask, IK humanoide (`OnAnimatorIK`), Animation Rigging, culling, coste Humanoid vs Generic.
- **Blender Manual 5.2 — Armatures / Bones (Deform) / Rigify** — Blender Foundation — propiedad Deform, DEF-/ORG-/MCH- de Rigify, parent With Automatic Weights. (No accesible por WebFetch en esta sesión — 403; operadores `armature_add`, `parent_set(type='ARMATURE_AUTO')`, `vertex_group_limit_total`, `vertex_group_normalize_all` y flags de `export_scene.fbx` verificados contra la referencia de la base y conocimiento de Blender 5.2; ver también [ver: esqueletos-armature] [ver: skinning-weights] [ver: rigify].)
