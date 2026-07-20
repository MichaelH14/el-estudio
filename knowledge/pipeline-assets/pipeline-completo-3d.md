# El pipeline completo de un asset 3D: de idea a prefab en Unity

> **Cuando cargar este archivo:** al ARRANCAR o ANALIZAR un asset 3D de juego de punta a punta — cuando necesitas el MAPA MAESTRO que une todo el bloque de arte (Blender) con Unity 6 en un solo flujo: referencia → modelado → UV → textura → (rig → animación) → export → import → material → prefab → verificación en el engine. Es el **índice ejecutable** del pipeline 3D: no ejecuta el detalle de cada etapa (eso vive en las bases hermanas) sino que las ORDENA, dice qué archivo cargar en cada una, define el gate acumulativo, ramifica estático vs animado y cierra con el asset ensamblado como prefab. Carga esto primero; salta a la base de la etapa cuando toque ejecutarla.

## 0. Cómo se usa este mapa maestro

Este archivo es el conductor, no el músico. Regla de operación: **en cada etapa, carga la base indicada, ejecútala hasta su estado de salida, corre su checkpoint por código, y solo entonces avanza.** Un asset que no pasa el gate de una etapa NO entra a la siguiente — se repara donde falló. Nada se "arregla un poquito más adelante": la deuda de una etapa se paga multiplicada en la siguiente [ver: pipeline-3d/flujo-modelado-blender §0].

Tres invariantes que gobiernan TODO el flujo y se fijan al inicio (arreglarlos al final es carísimo — arrastran UV, bake, rig, física, iluminación):

1. **Escala métrica** 1u = 1 m desde la Etapa 0 en Blender [ver: pipeline-3d/flujo-modelado-blender §2].
2. **Pivote por uso** = origen del objeto; en Unity ya no se edita [ver: blender/import-export].
3. **Nombres congelados** (objeto/malla/material/hueso): son el CONTRATO con Unity vía GUID en el `.meta`. No se renombran tras el primer import [ver: organizacion-versionado-3d].

El ensamblaje en un engine vivo asume el MCP de Unity montado; en Blender, MCP o headless `--background --python` [ver: blender/blender-mcp-operativo] [ver: blender/bpy-scripting].

## 1. El mapa maestro: todas las etapas en un solo flujo

Cada fila = una etapa. "Cargar" = qué base de conocimiento la ejecuta. "Estado de salida" = qué queda listo. "Gate" = el checkpoint verificable que hay que pasar para avanzar (§5 lo detalla como gate acumulativo). Las etapas 0–6 son BLENDER; 7–11 son UNITY.

| # | Etapa | Cargar (base ejecutora) | Estado de salida | Gate para avanzar |
|---|---|---|---|---|
| 0 | .blend a escala | [ver: pipeline-3d/flujo-modelado-blender §2] | Escena métrica, colecciones `ref/high/low/final`, pivote decidido | Units métricas + colecciones |
| 1 | Referencia / brief | [ver: modelado/blueprints-referencias] | Vistas orto alineadas y calibradas a escala real | Refs en `ref`, cruz cuadra |
| 2 | Blockout | [ver: pipeline-3d/flujo-modelado-blender §4] | Masas con proporción/escala validadas en perspectiva | `dimensions` ≈ spec |
| 3 | Modelado 1º/2º/3º | receta del tipo (§2) + [ver: modelado/topologia] | Malla en quads, silueta, terciario planificado para bake | Silueta ok, tris en rango |
| 4 | Cleanup malla | [ver: pipeline-3d/flujo-modelado-blender §6] | Manifold, sin doubles/ngons/loose, normales fuera | 0 non-manifold, 0 loose |
| 5 | UV | [ver: texturizado/uv-unwrapping] | UV0 sin solapes, 0–1, hard edge = seam, margin ok | Islas empaquetadas, checker limpio |
| 6a | Bake (si high→low) | [ver: texturizado/baking] | Normal (OpenGL/Y+), AO, curvature horneados sin artefactos | Bake sin skirts/waviness |
| 6b | Texturizado PBR | [ver: texturizado/texturizado-blender] o [substance-y-alternativas] | Set de mapas PBR en disco, naming con sufijo | Mapas completos §1 de textura |
| — | **RIG** (solo animado) | [ver: rigging/rig-a-unity §1] | Armature deform-only, T-pose, weights ≤4, transforms aplicados | Deforma bien, ≤4 infl/vért |
| — | **ANIMACIÓN** (solo animado) | [ver: animacion3d/ciclos-locomocion] + [ver: animacion-blender/export-clips-unity §3] | Clips bakeados (IK a keys), loops cerrados, fps = juego | Loop cierra, root motion horneado |
| 7 | Export FBX | [ver: blender/import-export] | FBX con transforms aplicados, FBX Units Scale, naming limpio | Auto-validación por reimport |
| 8 | Import a Unity | [ver: pipeline/arte-a-unity] + §3 | Model importer: escala, normales, materiales, rig configurados | File Scale 1, consola limpia |
| 9 | Material URP | [ver: texturizado/texturas-a-unity §5] | Material Lit con sus mapas, sRGB correcto, smoothness empaquetado | Se ve bien bajo luz real |
| 10 | Prefab (ensamblaje) | §4 de este archivo + [ver: blender-unity-bridge] | Prefab Variant: malla+materiales+LODGroup+colliders+Animator | Prefab instancia sin errores |
| 11 | Verificación en engine | §5 + §9 | Aprobado con luz/cámara/post del nivel, en movimiento | Checklist §9 al 100% |

**El flujo es un gate acumulativo:** el estado de salida de cada etapa es la ENTRADA de la siguiente. Nunca se salta hacia adelante con deuda pendiente (§5).

## 2. Los dos caminos: estático vs animado (dónde se ramifica)

El flujo se **bifurca dos veces**. Primero en el blockout aprobado (Etapa 2), por TIPO de asset → qué receta de modelado [ver: pipeline-3d/flujo-modelado-blender §9]. Segundo, y el que decide la mitad del pipeline: **¿el asset deforma?**

| | **Asset estático** (prop / entorno / kit) | **Asset animado** (personaje / criatura / mecánico articulado) |
|---|---|---|
| Ruta | 0→6b → **7 export** → 8→11 | 0→6b → **+RIG +ANIM** → 7→11 |
| Etapas extra | ninguna | rigging [ver: rigging/rig-a-unity], animación [ver: animacion-blender/export-clips-unity] |
| Export | 1 FBX (malla + materiales) | `Modelo.fbx` (malla+rig, define Avatar) + `Modelo@clip.fbx` por animación |
| Unity Rig tab | Animation Type = **None** | **Humanoid** (bípedo con retargeting/Mixamo) o **Generic** (todo lo demás) [ver: rigging/rig-a-unity §3] |
| Componentes del prefab | MeshFilter + MeshRenderer + Collider (+ LODGroup) | SkinnedMeshRenderer + **Animator** (Avatar + Controller) + Collider |
| Presupuesto extra | — | + huesos + clips (§6) |
| Riesgo dominante | escala/pivote/materiales | deformación, retargeting, root motion, avatar compartido |

Punto de ramificación operativo: **decides estático vs animado ANTES de la Etapa 3** (afecta topología — los loops concéntricos en zonas que deforman se planifican en el modelado, no se parchean después) [ver: modelado/topologia] [ver: modelado/organico-personajes]. Un prop que "quizás luego se anima" se modela como animado desde el inicio o se acepta rehacer topología.

## 3. El puente técnico Blender → Unity (consolidado)

El detalle exacto de cada travesía vive en la base correspondiente; aquí el **mapa del puente** — qué cruza, con qué setting, y adónde se resuelve. Detalle completo del roundtrip en [ver: blender-unity-bridge].

| Qué cruza | Setting en Blender (export FBX) | Se resuelve/verifica en Unity | Base |
|---|---|---|---|
| Escala 1u=1m | `apply_scale_options='FBX_SCALE_UNITS'` (×100) | `useFileScale`, File Scale = 1 (no 0.01) | [ver: blender/import-export] |
| Ejes Z-up→Y-up | `axis_forward='-Z'`, `axis_up='Y'` | `bakeAxisConversion` (o aceptar el -89.98) | [ver: blender/import-export] |
| Normales/tangentes | `use_tspace=True`, `mesh_smooth_type='FACE'` | `importNormals`, Unity calcula MikkTSpace | [ver: texturizado/texturas-a-unity §7] |
| Normal map convención | bake `normal_g='POS_Y'` (OpenGL/Y+) | tipo Normal map; `flipGreenChannel` solo si DirectX | [ver: texturizado/texturas-a-unity §3] |
| Rig limpio | `use_armature_deform_only=True`, `add_leaf_bones=False` | Rig tab: Humanoid/Generic, sin huesos `_end` | [ver: rigging/rig-a-unity §2] |
| Clips | `bake_anim`, patrón `Modelo@clip.fbx` | Copy From Other Avatar, Loop Match verde | [ver: animacion-blender/export-clips-unity] |
| Identidad (GUID) | naming congelado de objeto/malla/material | `.meta` guarda GUID + import settings | §8, [ver: organizacion-versionado-3d] |

**El `.meta` es la columna vertebral del puente.** Unity crea un `.meta` por cada asset y carpeta; guarda "the unique ID assigned to the asset, and values for all the asset's import settings" (verificado, Unity Manual). Ese GUID es lo que hace que un material apunte a una textura y un Animator a un clip. Consecuencias operativas, verificadas:

- **Nunca separar el asset de su `.meta`.** Si un asset pierde su `.meta`, "any reference to that asset is broken" — materiales sin textura, prefabs con scripts perdidos.
- **Mover/renombrar SIEMPRE dentro del Editor** (Project window): Unity mueve el `.meta` solo. Fuera del Editor hay que mover el `.meta` a mano o se crea un asset nuevo con GUID nuevo y se rompen todas las referencias.
- **Reexportar sobre el MISMO path** (no borrar-y-recrear): conserva el GUID → el prefab, materiales y Animator siguen enganchados (§8).

## 4. El asset como PREFAB en Unity (el ensamblaje)

El FBX importado YA es un objeto tipo prefab de solo-lectura (el "model prefab": malla + jerarquía + Avatar), pero **no se le añaden componentes directamente** — un reimport los borraría. El patrón correcto, verificado contra la doc de Prefab Variants:

> **Crea un Prefab Variant del model prefab.** El variant "inherits properties from a base prefab. Overrides in the variant take precedence over the base values", y esos overrides "persist independently" cuando el base cambia. Traducción: **la malla se actualiza sola en cada reimport del FBX, y tus colliders/LODGroup/Animator/scripts sobreviven** porque viven como overrides del variant, no del model. Es el mecanismo que separa "datos del modelo" (upstream, Blender) de "lógica de juego" (downstream, Unity).

Crear el variant: click derecho en el model prefab → **Create > Prefab Variant**, o arrastrar una instancia del model a `Assets/` y elegir "Prefab Variant". Por código: `PrefabUtility.SaveAsPrefabAsset(instanceRoot, path)` — y **si `instanceRoot` es la raíz de una instancia de prefab, el resultado ES un Prefab Variant** (verificado). Al guardar sobre uno existente, Unity **casa GameObjects por nombre**: nombres únicos en la jerarquía o "you cannot predict which will be matched".

Componentes que ensambla el variant, por tipo de asset:

| Componente | Estático | Animado | Nota |
|---|---|---|---|
| MeshFilter + MeshRenderer | ✅ | — | del model prefab |
| SkinnedMeshRenderer | — | ✅ | del model prefab; Quality = bones/vért coherente |
| **Materiales** | ✅ | ✅ | asignar TUS materiales URP (§9), no los embebidos del FBX |
| **LODGroup** | si el asset se ve a distancia | idem | §4.1 |
| **Collider** | ✅ | ✅ | §4.2 |
| **Animator** | — | ✅ | Avatar (del model) + Animator Controller [ver: unity/animacion-unity] |
| Scripts de gameplay | según diseño | según diseño | overrides del variant |

**Materiales — no uses los del FBX.** El Model Importer ofrece Material Creation Mode = None / Standard (Legacy) / Import via MaterialDescription; con **None**, "Use Unity's default diffuse material instead". La práctica de producción: importar con materiales propios (mode None o Search-and-Remap por naming) y asignar materiales URP Lit hechos a mano — control total del render pipeline. Si el FBX trae materiales embebidos y los quieres extraer: **Extract Materials / Extract Textures**, con la salvedad de que "new imports or changes to the original asset do not affect extracted materials" [ver: texturizado/texturas-a-unity §5].

### 4.1 LODGroup (si el asset se ve a varias distancias)

- **Convención de naming automática:** mallas nombradas `..._LOD0`, `_LOD1`, `_LOD2` en el FBX → Unity arma el LODGroup solo al importar. `LOD0` = más detalle; índices mayores = menos (verificado). Modela/exporta los niveles desde Blender con ese sufijo [ver: blender/import-export].
- **LODGroup** "lets users explicitly specify object size on screen at which a LOD transition occurs per LOD index" — los porcentajes son **altura relativa en pantalla**, no distancia absoluta; a menor % la transición ocurre más lejos. Por código: `LODGroup.SetLODs(LOD[])` + `RecalculateBounds()`.
- Alternativa Unity 6: **Mesh LOD** (menor overhead, "provides the option to create LODs automatically on model import") cuando solo reduces polígonos y no cambias materiales. LODGroup cuando además bajas materiales/renderers.
- Detalle de cuántos tris por nivel: presupuesto (§6) y [ver: modelado/presupuestos-poligonos].

### 4.2 Colliders (nunca el render mesh)

- **Primitivos** (Box/Sphere/Capsule): "simple shapes… scale to approximately the same size and shape"; baratos; combínalos en **compound collider** para formas complejas. Default para casi todo.
- **Mesh Collider**: "exactly match the shape of the GameObject's Mesh… more accurate… but require more computational resources". Convex obligatorio si el objeto es dinámico (Rigidbody).
- Regla de oro: **collider primitivo o malla de colisión simplificada (UCX_ desde Blender), JAMÁS el render mesh directo** — un Mesh Collider sobre la malla de render mata la física. La malla `UCX_` viaja en el FBX [ver: blender/import-export]; `addCollider` del importer solo para props estáticos triviales.

## 5. El gate acumulativo: estado de salida + checkpoint por etapa

Cada etapa tiene un **estado de salida verificable** (el contrato con la siguiente) y un **checkpoint que corre sin ojos humanos**. El agente ejecuta el checkpoint por MCP/headless (Blender) o por MCP de Unity; `assert`/lectura que falla = etapa no superada. Los snippets de cada checkpoint viven en su base; aquí el ÍNDICE del gate acumulativo.

| Etapa | Estado de salida (contrato) | Checkpoint (dónde) |
|---|---|---|
| 0 escala | units métricas, colecciones, pivote | [ver: pipeline-3d/flujo-modelado-blender §10-A] |
| 2 blockout | `dimensions` ≈ spec, transforms aplicados | §10-C (bmesh dims) |
| 3 modelado | quads, tris ≤ budget, silueta | §10-C + wireframe |
| 4 cleanup | 0 non-manifold, 0 loose, 0 ngons, normales fuera | §10-D (bmesh) |
| 5 UV | UV0 sin solapes, hard edge=seam | checker + área UV [ver: texturizado/uv-unwrapping] |
| 6 textura | set de mapas completo, normal OpenGL, smoothness empaquetado | verif en Unity [ver: texturizado/texturas-a-unity §8] |
| rig | ≤4 infl/vért, deform-only, T-pose | validación en Unity [ver: rigging/rig-a-unity §10] |
| anim | loop cierra (Loop Match verde), fps=juego, root motion horneado | Loop Match + reproducir [ver: animacion-blender/export-clips-unity §8] |
| 7 export | reimport: malla no vacía, dims<100 (no ×100), scale 1 | auto-validación [ver: blender/import-export] |
| 8 import | File Scale 1, Rig ok, consola limpia | leer ModelImporter por MCP |
| 10 prefab | instancia sin errores, materiales asignados, collider/LOD/Animator | instanciar y leer transform |
| 11 engine | aprobado bajo luz/cámara/post reales, en movimiento | §9 completo |

**La disciplina del gate acumulativo:** si la Etapa 8 revela File Scale 0.01, el fix NO es escalar en Unity — es volver a la Etapa 7 (export) o la 0 (escala). Cada síntoma en Unity apunta a una etapa upstream concreta; se repara ahí, no se parchea downstream. Parchear downstream crea drift permanente [ver: texturizado/texturas-a-unity §8].

## 6. Presupuesto por asset acumulado (tris + texturas + huesos + clips)

El presupuesto no es solo tris: un asset animado carga **cuatro presupuestos a la vez**, y todos suman al costo de runtime. Cifras concretas por categoría y plataforma en [ver: modelado/presupuestos-poligonos]; aquí el marco de qué se cuenta y cómo medirlo.

| Presupuesto | Se mide en | Estático | Animado | Dónde vive el detalle |
|---|---|---|---|---|
| **Geometría** | tris del engine (loop triangles) | prop, entorno, kit | + costo de skinning por vért | [ver: modelado/presupuestos-poligonos] |
| **Texturas** | nº de sets × resolución × formato | 1 set típico | 1–N sets | [ver: unity/rendimiento-unity], [ver: texturizado/atlas-trim-optimizacion] |
| **Materiales** | draw calls (SRP Batcher) | 1 por prop objetivo | 1–pocos | [ver: unity/rendering-urp] |
| **Huesos** | nº de huesos deform, ≤4 infl/vért | — | escala con complejidad del rig | [ver: rigging/rig-a-unity §1] |
| **Clips** | nº × largo × sample rate × compresión | — | locomoción + acciones | [ver: animacion-blender/export-clips-unity §8] |

Medir el costo REAL de un FBX (para presupuestar o auditar un asset ajeno, §7) por bpy — reimporta y cuenta tris reales, no polígonos:

```python
import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath="/ruta/asset.fbx")
for ob in bpy.data.objects:
    if ob.type == 'MESH':
        me = ob.data
        me.calc_loop_triangles()                       # tris reales (no me.polygons)
        print(ob.name, "dims(m):", tuple(round(d, 3) for d in ob.dimensions),
              "| tris:", len(me.loop_triangles),
              "| materiales:", len(ob.material_slots),
              "| UV sets:", len(me.uv_layers))
    elif ob.type == 'ARMATURE':
        print(ob.name, "| huesos:", len(ob.data.bones))
```
*(APIs `calc_loop_triangles`/`loop_triangles`, `dimensions`, `material_slots`, `uv_layers`, `armature.bones` son reales de Blender 5.2; corre una vez por headless para confirmar antes de fiarte del número en producción.)*

## 7. Aprender de assets reales (la metodología)

La forma más rápida de calibrar "qué es game-ready para este juego" es **diseccionar assets que ya funcionan**: importar un FBX de referencia (de un pack, de Mixamo, del propio proyecto) y LEER sus números en vez de adivinar. El método y los casos concretos en [ver: aprender-de-assets]; el marco:

1. **Mide, no mires.** Corre el snippet de §6 sobre el FBX de referencia: tris, dims, materiales, UV sets, huesos. Compara contra tu asset. Un "se ve parecido" no dice si el tuyo tiene 3× los tris.
2. **Lee el import en Unity.** ModelImporter del asset de referencia: `useFileScale`, `materialImportMode`, `generateSecondaryUV`, `animationType`, `meshCompression` — copia el criterio que usó alguien que ya shippeó.
3. **Disecciona el prefab.** Qué componentes lleva, cuántos materiales, si usa LODGroup, qué tipo de collider, cómo está el Animator. El prefab de un asset shippeado es un checklist §9 ya resuelto.
4. **Rig y clips.** Para animados: nº de huesos, si es Humanoid/Generic, cuántos clips, root motion sí/no. Mixamo es el banco de referencia gratis de rigs Humanoid [ver: rigging/rig-a-unity §4].

Regla: **la disección alimenta tu presupuesto (§6) y tu gate (§5)**, no se hace por curiosidad. Un asset de referencia con 8k tris y 1 material te da el budget real de esa categoría en ese juego mejor que cualquier tabla genérica.

## 8. Iteración: re-editar el .blend y propagar a Unity sin rehacer el prefab

El pipeline se recorre muchas veces. La clave de iterar barato es que **el prefab (lógica) y el modelo (datos) están desacoplados** por el Prefab Variant (§4) y la estabilidad del GUID (§3). El loop de iteración:

1. **Edita el `.blend`** (source) — malla, UV, textura, un clip.
2. **Reexporta al MISMO path del FBX** (mismo nombre, mismos nombres de objeto/malla/material/hueso). No borres el FBX ni el `.meta` — eso mataría el GUID y rompería el prefab, materiales y Animator [ver: organizacion-versionado-3d].
3. **Unity reimporta** el FBX (auto al detectar cambio, o `AssetDatabase.ImportAsset(path)` / `AssetDatabase.Refresh()` por código). El model prefab se actualiza.
4. **El Prefab Variant hereda** la malla nueva; tus colliders/LODGroup/Animator/scripts (overrides) sobreviven. No rehaces el prefab.

Qué propaga limpio y qué NO:

| Cambio en Blender | Propaga solo al reimport | Requiere acción en Unity |
|---|---|---|
| Editar geometría (mismos nombres) | ✅ malla nueva en el variant | — |
| Re-bakear/repintar textura (mismo path) | ✅ material la re-lee | purgar caché si CDN [ver: texturizado/atlas-trim-optimizacion] |
| Ajustar un clip (`Modelo@clip.fbx`, mismo path) | ✅ solo ese archivo reimporta | — |
| **Renombrar** objeto/malla/material/hueso | ❌ | rompe: MeshFilter vacío, Avatar inválido, curvas perdidas |
| Añadir un submesh / material nuevo | parcial | asignar el material nuevo en el variant |
| Cambiar escala/ejes del export | ❌ silencioso | re-verificar File Scale y transforms |

Automatización del import (para no configurar sRGB/escala/rig a mano en cada asset): un **AssetPostprocessor** de modelo aplica las reglas del proyecto en cada (re)import. `OnPreprocessModel` corre antes de importar (setea el `ModelImporter`); `OnPostprocessModel(GameObject root)` corre "before the final Prefab is created and before it is written to disk" y da acceso al root importado (verificado — ⚠️ las referencias a meshes se invalidan tras el import: no crees un prefab externo que apunte a meshes del FBX desde ahí).

```csharp
// Assets/Editor/ModelImportRules.cs — reglas de import por carpeta/nombre. Corre en cada (re)import.
using UnityEngine;
using UnityEditor;

public class ModelImportRules : AssetPostprocessor
{
    void OnPreprocessModel()
    {
        if (!assetPath.Contains("/_Game/Models/")) return;
        var mi = (ModelImporter)assetImporter;

        mi.useFileScale = true;                         // File Scale del FBX (viene ×100 → 1 en Unity)
        mi.materialImportMode = ModelImporterMaterialImportMode.None; // materiales URP propios, no los del FBX
        mi.generateSecondaryUV = true;                  // UV de lightmap para estáticos
        mi.addCollider = false;                         // collider se pone en el Prefab Variant, no auto

        // rig: los @clip son Generic/Humanoid según naming; el base define el Avatar
        if (System.IO.Path.GetFileName(assetPath).Contains("@"))
            mi.animationType = ModelImporterAnimationType.Generic; // ajustar a Human si el proyecto es Humanoid
    }
}
```
*(Nombres de propiedad verificados contra ModelImporter Scripting API 6000.2: `useFileScale`, `materialImportMode`, `generateSecondaryUV`, `addCollider`, `animationType`. Confirma el valor de `animationType` contra tu convención antes de fiarte — Humanoid vs Generic lo decide §2.)*

Para lotes grandes: `AssetDatabase.StartAssetEditing()` / `StopAssetEditing()` envuelve N imports en un batch (pausa el import automático); `AssetPathToGUID`/`GUIDToAssetPath` para resolver identidad estable [ver: organizacion-versionado-3d].

## 9. El checklist game-ready UNIFICADO final

La lista COMPLETA que un asset debe pasar antes de entrar al juego. Consolida los gates de malla, UV, textura, rig, clips y prefab de las cuatro bases en una sola auditoría. Falla uno → se devuelve a la etapa que lo produjo (§5), no se completa a medias.

**Malla y escala**
- [ ] Escala 1u=1m; File Scale = 1 en Unity (no 0.01/×100); mide lo que la spec.
- [ ] Transforms aplicados (rot 0, scale 1); pivote por uso; apoya en Z=0.
- [ ] Manifold: 0 non-manifold (salvo bordes por diseño), 0 doubles, 0 ngons finales, 0 loose, 0 caras internas.
- [ ] Topología en quads, cada edge justificado; poles fuera de zonas que deforman.
- [ ] Tris del engine ≤ budget de su categoría (§6).
- [ ] Triangulación congelada antes de bake/export (baker y engine triangulan igual).

**UVs y texturas**
- [ ] UV0 sin solapes fuera de tiles intencionales, en 0–1; margin ok; hard edge = seam.
- [ ] UV2 de lightmap si es estático que recibe luz horneada (`generateSecondaryUV`).
- [ ] Set de mapas completo (Base, MetallicSmoothness, Normal casi siempre; AO/Height/Emission si aplican).
- [ ] Normal en convención del proyecto (OpenGL/Y+); no mezclado con DirectX.
- [ ] Smoothness empaquetado (1−roughness) en el alpha correcto; sRGB ON solo en color.
- [ ] Nombres con sufijo de la convención (`_BaseColor/_Normal/_MetallicSmoothness/…`).

**Rig y clips (solo animado)**
- [ ] Deform-only, sin huesos `_end`/control; T-pose; ≤4 influencias por vértice.
- [ ] Animation Type correcto (Humanoid con Avatar válido / Generic con Root Node).
- [ ] Deformación limpia (codos/hombros/cadera/axilas) bajo luz, reproduciendo un clip.
- [ ] Clips comparten Avatar (Copy From Other Avatar); Loop Match verde; fps=juego.
- [ ] Root motion según diseño (Bake Into Pose + Apply Root Motion coherentes).

**Material, prefab y engine**
- [ ] 1 material por prop objetivo; URP Lit configurado (Workflow, Smoothness Source, GPU Instancing si aplica).
- [ ] Prefab Variant ensamblado: materiales asignados + Collider (no render mesh) + LODGroup si aplica + Animator si animado.
- [ ] Naming congelado (objeto/malla/material/hueso); `.meta`/GUID intactos.
- [ ] Consola de Unity limpia (sin warnings del importer).
- [ ] **Aprobado en el engine** con la luz, cámara y post del nivel, en movimiento — no desde el render del DCC.

## Reglas prácticas

1. Este archivo conduce; cada etapa la ejecuta su base. Carga la base indicada, ejecuta, corre su checkpoint, y solo entonces avanza.
2. Escala 1u=1m, pivote por uso y nombres congelados se fijan al inicio; arreglarlos al final arrastra todo el pipeline.
3. Decide estático vs animado ANTES de la Etapa 3: la topología de deformación se planifica en el modelado, no se parchea.
4. El gate es acumulativo: el estado de salida de una etapa es la entrada de la siguiente; nunca avances con deuda.
5. Un síntoma en Unity apunta a una etapa upstream concreta; repáralo ahí, no lo parchees en Unity (crea drift).
6. El asset entra a Unity como Prefab Variant del model prefab: malla se actualiza sola, tus componentes sobreviven.
7. Asigna materiales URP propios; no uses los embebidos del FBX (Material Creation Mode = None o Search-and-Remap).
8. Collider = primitivo o malla simplificada (`UCX_`), nunca el render mesh; convex si es dinámico.
9. LODGroup por naming `_LOD0/_LOD1/…`; los % son altura en pantalla, no distancia.
10. El `.meta`/GUID es el contrato de identidad: mueve/renombra dentro del Editor; reexporta al mismo path; nunca borres el `.meta`.
11. Iterar barato = reexportar al mismo path con los mismos nombres → reimport → el variant hereda; no rehagas el prefab.
12. Automatiza el import con un AssetPostprocessor de modelo (`OnPreprocessModel`); a mano no escala.
13. Presupuesta los cuatro ejes (tris + texturas + huesos + clips), no solo tris; mide el FBX real por bpy.
14. Aprende de assets shippeados: mide sus números y lee su import/prefab antes de adivinar tu budget.
15. Naming: objeto/malla/material/hueso congelados tras el primer import — renombrar rompe el GUID/Avatar.
16. Animado: clips en Copy From Other Avatar, esqueleto idéntico entre `.fbx` base y todos los `@`.
17. Verifica geometría/normales/rig por código (bmesh/MCP), no por impresión visual.
18. "Listo" = asset instanciado en Unity, bajo luz y cámara reales, en movimiento, checklist §9 al 100% — no "el export no dio error".

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Añadir colliders/LODGroup al model prefab directo | Se borran al reimport; ponlos en un **Prefab Variant** del model (§4) |
| Escalar/rotar en Unity para "arreglar" el FBX | El fix es upstream (Etapa 0/7); escalar en Unity arrastra física/UV/rig |
| Usar los materiales embebidos del FBX | Material Creation Mode = None + materiales URP propios (§4) |
| Mesh Collider sobre el render mesh | Primitivo/compound o `UCX_` simplificado; mata la física si no |
| Borrar el FBX/`.meta` para "refrescar" | GUID nuevo → prefab/materiales/Animator rotos; reexporta al MISMO path |
| Renombrar objeto/malla/material/hueso tras importar | Congelar naming; renombrar = MeshFilter vacío, Avatar inválido, curvas perdidas |
| Mover assets fuera del Editor sin el `.meta` | Mover/renombrar SIEMPRE en el Project window (Unity mueve el `.meta`) |
| Decidir animar un prop ya modelado sin loops de deformación | Estático vs animado se decide antes de la Etapa 3; si no, se rehace topología |
| Configurar sRGB/escala/rig a mano por asset | AssetPostprocessor de textura y de modelo por carpeta/sufijo (§8) |
| Presupuestar solo por tris | Cuenta también texturas, huesos y clips (§6); un animado carga los cuatro |
| Avanzar de etapa con el checkpoint anterior en rojo | Gate acumulativo (§5): se repara donde falló, no se avanza |
| Aprobar el asset desde el render de Blender/Painter | Solo cuenta en el engine con luz/cámara/post del nivel, en movimiento (§9) |
| Crear el prefab desde una malla con nombres duplicados | `SaveAsPrefabAsset` casa por nombre; nombres únicos en la jerarquía |
| `LOD1/LOD2` sin el sufijo `_LOD` esperado | Nombra las mallas `_LOD0/_LOD1/…` para que Unity arme el LODGroup solo |

## Fuentes

Bases sintetizadas (el detalle de operadores/settings vive en ellas; este archivo las une y enruta):
- [ver: pipeline-3d/flujo-modelado-blender] — mapa de las 7 etapas de modelado, checkpoints por código (§10), ramificación por tipo, gate game-ready de malla.
- [ver: texturizado/texturas-a-unity] — import settings por mapa, sRGB, normal OpenGL/DirectX, MetallicSmoothness, material URP Lit, AssetPostprocessor de textura, verificación en engine.
- [ver: rigging/rig-a-unity] — Rig tab (Humanoid/Generic/None), Avatar, retargeting, root motion, Optimize Game Objects, Avatar Mask, checklist de rig en Unity.
- [ver: animacion-blender/export-clips-unity] — Bake Animation del FBX, patrón `Modelo@clip.fbx`, framerate, Loop Match, compresión de clips, root motion.
- Puentes internos de este bloque: [ver: blender-unity-bridge], [ver: aprender-de-assets], [ver: organizacion-versionado-3d]; a las bases: [ver: modelado/presupuestos-poligonos], [ver: modelado/topologia], [ver: modelado/organico-personajes], [ver: texturizado/uv-unwrapping], [ver: texturizado/baking], [ver: texturizado/atlas-trim-optimizacion], [ver: blender/import-export], [ver: unity/animacion-unity], [ver: unity/rendering-urp], [ver: unity/rendimiento-unity], [ver: pipeline/arte-a-unity], [ver: animacion3d/ciclos-locomocion].

Web (Unity Manual/ScriptReference 6000.2, verificadas por WebFetch esta sesión):
- **AssetPostprocessor.OnPostprocessModel** — Unity ScriptReference 6000.2 — "when a model has completed importing"; corre "before the final Prefab is created and before it is written to disk"; `root` = root GameObject; referencias a meshes se invalidan tras el import.
- **Level of Detail / LODGroup** — Unity Manual 6000.2 — LOD0 = más detalle; LODGroup "lets users explicitly specify object size on screen at which a LOD transition occurs per LOD index"; Mesh LOD auto-import.
- **Meta files / Import process** — Unity Manual 6000.2 — el `.meta` guarda "the unique ID assigned to the asset, and values for all the asset's import settings"; separarlo rompe todas las referencias; mover dentro del Editor conserva el `.meta`.
- **ModelImporter** — Unity ScriptReference 6000.2 — `globalScale`, `useFileScale`, `bakeAxisConversion`, `importNormals`, `normalCalculationMode`, `materialImportMode`, `materialLocation`, `generateSecondaryUV`, `meshCompression`, `optimizeMeshVertices/Polygons`, `isReadable`, `addCollider`, `importAnimation`, `animationType`.
- **PrefabUtility.SaveAsPrefabAsset** — Unity ScriptReference 6000.2 — firma `SaveAsPrefabAsset(GameObject, string[, out bool])`; si el input es raíz de una instancia de prefab, el resultado es un **Prefab Variant**; casa GameObjects por nombre al sobrescribir.
- **Prefab Variants** — Unity Manual 6000.2 — "inherits properties from a base prefab. Overrides in the variant take precedence over the base values"; overrides persisten cuando el base cambia; workflow de variant desde un model importado para añadir componentes y preservar reimports.
- **Model Importer — Materials tab** — Unity Manual 6000.2 — Material Creation Mode None/Standard(Legacy)/Import via MaterialDescription; Extract Materials/Textures; Search and Remap; "new imports or changes to the original asset do not affect extracted materials".
- **Colliders overview** — Unity Manual 6000.2 — primitivos (Box/Sphere/Capsule) baratos y combinables; Mesh Collider "exactly match the shape… more accurate… but require more computational resources".
- **AssetDatabase** — Unity ScriptReference 6000.2 — `ImportAsset`, `Refresh`, `StartAssetEditing`/`StopAssetEditing` (batch), `AssetPathToGUID`/`GUIDToAssetPath`, `LoadAssetAtPath`, `CreateAsset`, `SaveAssets`.
- **Creating Prefabs** — Unity Manual 6000.2 — arrastrar un GameObject a `Assets/` crea el Prefab; si el GameObject arrastrado ya es una instancia de prefab, Unity muestra un diálogo para confirmar si crear un prefab nuevo o un **Prefab Variant**.
