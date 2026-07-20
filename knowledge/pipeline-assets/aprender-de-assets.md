# Aprender de assets de Unity existentes

> **Cuando cargar este archivo:** cuando tienes un asset ya hecho (un FBX, un prefab, una mesh, un material, un atlas 2D, un AnimatorController) y necesitas EXTRAER sus convenciones técnicas para producir arte consistente con él — igualar el estándar de un pack, de un asset de referencia del cliente, o de lo que ya está en el proyecto. Es la fase de INGENIERÍA INVERSA del bloque de arte 3D: no produce el asset, produce la **ficha de convenciones** que sirve de spec. El flujo de producción punta a punta está en [ver: pipeline-completo-3d]; el puente técnico Blender↔Unity (escala, ejes, roundtrip) en [ver: blender-unity-bridge]; dónde vive cada archivo en [ver: organizacion-versionado-3d].

Este archivo NO reexplica cómo se modela/texturiza/riggea (eso son las bases hermanas) ni cómo se configura un import desde cero ([ver: pipeline/arte-a-unity]). Su valor único: dado un asset TERMINADO, **cómo leerlo por código** y volcar sus números en una spec reproducible. La regla madre: un asset de referencia se aprende midiéndolo, nunca "a ojo" ni por lo que diga su README.

## 1. El objetivo: la ficha de convenciones

El producto de esta fase es UNA ficha (§10) que responde, con números medidos, a: ¿cuántos tris/verts? ¿qué texel density? ¿qué escala y pivote? ¿qué naming? ¿qué shader y empaquetado de canales? ¿qué tipo de rig, cuántos huesos, qué clips? Con eso, cualquier asset nuevo entra al mismo molde y no desentona ([ver: modelado/presupuestos-poligonos] para leer el polycount, [ver: texturizado/texturas-a-unity] para el material, [ver: rigging/rig-a-unity] para el rig).

Lo que se aprende son **convenciones técnicas** (el estándar), no el contenido. Ver §11: medir un asset licenciado para replicar su estándar es legítimo; copiar su geometría/texturas y redistribuirlas no.

## 2. Las tres superficies de inspección

Un asset de Unity se lee por tres vías, cada una con lo que sí y lo que no revela. Combinarlas: el `.meta` da la INTENCIÓN de import, la malla da la REALIDAD geométrica, el prefab da el ENSAMBLE.

| Superficie | Qué es | Cómo se lee (sin/con Unity) | Qué revela | Qué NO revela |
|---|---|---|---|---|
| **`.meta`** (texto YAML) | Import settings + GUID, uno por asset | `Read`/grep directo; o `AssetImporter.GetAtPath` en editor | Scale factor, normals, rig type, sRGB, compresión, PPU, clips definidos, materiales | Geometría real (tris/UVs); solo la config de import |
| **La malla / FBX** | Geometría, UVs, huesos, materiales-slot | Reimportar a Blender por `bpy` y medir; o editor-script sobre el `Mesh` importado | Tris/verts reales, escala/dims, pivote, nº UV sets, huesos, blendshapes | Los import settings de Unity (esos están en el `.meta`) |
| **`.prefab` / `.unity`** (texto YAML) | Ensamble: GameObjects, componentes, refs | `Read`/grep directo; o `AssetDatabase.LoadAssetAtPath` + `GetComponent` | Componentes, LODGroup, colliders, refs a mesh/material por GUID, jerarquía | Nada del binario del mesh/textura (solo referencias) |

Regla de oro del agente: **texto primero, editor después.** El `.meta` y el `.prefab` son texto YAML — se leen con `Read`/grep en segundos sin abrir nada. Solo la geometría real y la verificación bajo shader exigen Blender o Unity vivos.

## 3. Leer el `.meta` (import settings sin abrir Unity)

Unity crea un `.meta` por asset y por carpeta; contiene "el ID único asignado al asset y los valores de todos sus import settings" (Unity Manual, *Meta files*). Es texto YAML → **grep directo**. El `guid` de la primera líneas es la identidad del asset: por él lo referencian prefabs/escenas, por eso el `.meta` va SIEMPRE a control de versiones ([ver: organizacion-versionado-3d]).

Campos que delatan el estándar, por tipo de asset:

| Asset | Campos clave del `.meta` | Lo que aprendes |
|---|---|---|
| **Textura** | `sRGBTexture`, `textureType` (0=default, 1=normalmap, 8=sprite), `textureCompression`, `maxTextureSize`, `spritePixelsPerUnit`, `spriteBorder`, `alphaIsTransparency`, `mipmaps` | Convención sRGB (color vs dato), PPU 2D, si el normal es OpenGL/DirectX (`flipGreenChannel`) [ver: texturizado/texturas-a-unity §2-3] |
| **Modelo (FBX)** | `globalScale`/`useFileScale`, `importNormals`, `bakeAxisConversion`, `generateSecondaryUV`, `animationType`, `optimizeGameObjects`, `materialImportMode` | Escala 1m, ejes, si genera lightmap UV, tipo de rig (§7), política de materiales |
| **Modelo con rig** | `humanDescription` (mapa de huesos), `skinWeights`/`maxBonesPerVertex`, bloque `clipAnimations` (nombre, `firstFrame`/`lastFrame`, `loopTime`, `keepOriginalOrientation`) | Humanoid vs Generic, cap de influencias, qué clips y cuáles loopean |

Grep útil sobre un árbol de assets de referencia (detecta la convención dominante de golpe):

```bash
# ¿sRGB on/off por tipo de mapa? ¿qué scale? ¿Humanoid o Generic?
grep -rl "sRGBTexture: 0" Assets/Ref/            # texturas tratadas como dato lineal
grep -rE "animationType: [0-9]" Assets/Ref/**/*.fbx.meta   # 1=Legacy 2=Generic 3=Humanoid
grep -rE "(globalScale|useFileScale|bakeAxisConversion):" Assets/Ref/**/*.fbx.meta
```

Valores enumerados verificados que hay que saber leer: `animationType` **1=Legacy, 2=Generic, 3=Humanoid** (0=None); `textureType` **0=Default, 1=NormalMap, 8=Sprite**; `sRGBTexture` **1=color (sRGB ON), 0=dato lineal**. El resto de import settings y su semántica: [ver: pipeline/arte-a-unity], [ver: unity/assets-pipeline-git].

## 4. Leer el `.prefab` / `.unity` (YAML de ensamble)

Escenas y prefabs son "un subset custom de YAML" (Unity Manual, *Format description*). Estructura:

- Cada objeto abre con `--- !u!<classID> &<fileID>`: `!u!1` = GameObject, `&6` = su fileID local dentro del archivo.
- Un GameObject lista sus componentes en `m_Component: - component: {fileID: N}`.
- Referencia interna: `{fileID: N}`. Referencia a **otro asset**: `{fileID: N, guid: <guid>, type: 3}` — ese `guid` casa con el `.meta` de la mesh/material/textura referenciada (así rastreas qué material usa el prefab sin abrir Unity).

Class IDs comunes que hay que reconocer al grepear (Unity *YAML Class ID Reference*):

| classID | Componente | classID | Componente |
|---|---|---|---|
| 1 | GameObject | 137 | SkinnedMeshRenderer |
| 4 | Transform | 205 | **LODGroup** |
| 33 | MeshFilter | 114 | MonoBehaviour (script) |
| 23 | MeshRenderer | 1001 | PrefabInstance |
| 65 | BoxCollider | 21 | Material (como asset) |

Lo que un prefab te enseña del estándar:

- **LODGroup** (`!u!205`): cuántos niveles y los `screenRelativeTransitionHeight` de cada uno → la política de LOD del proyecto [ver: modelado/presupuestos-poligonos §4].
- **Colliders**: si los dinámicos usan primitivos compuestos (Box/Sphere/Capsule) o MeshCollider → la convención de física [ver: pipeline/arte-a-unity §7].
- **Materiales**: los `guid` en `m_Materials` → cuántos materiales por asset (¿1 por prop?).
- **Sockets / jerarquía**: Empties hijos como attach points, naming de la jerarquía.

Grep de arranque:

```bash
grep -c "^--- !u!205" Prefabs/Ref/*.prefab      # ¿tienen LODGroup?
grep -A3 "m_Materials:" Prefabs/Ref/Hero.prefab  # cuántos materiales referencia
grep -E "^--- !u!(64|65|135|136|137)" Prefabs/Ref/*.prefab  # colliders / skinned mesh
```

## 5. Medir la malla: la realidad geométrica

El `.meta` dice la INTENCIÓN; solo la malla dice la verdad de tris, verts, escala y UVs. Dos caminos.

### 5a. Reimportar el FBX a Blender y medir por `bpy`

Headless, importador nativo 5.x, sin tocar la escena de trabajo. Base del patrón en [ver: blender/import-export] (auto-validación); aquí ampliado a extracción de convenciones ([ver: blender/bpy-scripting], [ver: blender/blender-mcp-operativo] para correrlo por MCP):

```python
import bpy, bmesh
FBX = "/ruta/Ref_Prop.fbx"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.fbx_import(filepath=FBX)
for ob in [o for o in bpy.data.objects if o.type == 'MESH']:
    me = ob.data
    bm = bmesh.new(); bm.from_mesh(me)
    tris = sum(len(f.verts) - 2 for f in bm.faces)   # tris tras triangular n-gons
    bm.free()
    print(ob.name,
          "tris:", tris,
          "verts(DCC):", len(me.vertices),          # OJO: el engine parte más (§5c)
          "dims(m):", tuple(round(d, 3) for d in ob.dimensions),
          "scale:", tuple(round(s, 3) for s in ob.scale),
          "uv_sets:", len(me.uv_layers),
          "mats:", [m.name for m in me.materials],
          "origin(m):", tuple(round(c, 3) for c in ob.location))
```

Qué sale y qué convención revela:

| Métrica | De dónde | Convención que fija |
|---|---|---|
| **Tris** | suma de `len(f.verts)-2` por cara | Poly budget de la categoría [ver: modelado/presupuestos-poligonos §1] |
| **Verts (DCC)** | `len(me.vertices)` | Referencia; el engine los parte 2-3× por seams/hard-edges/materiales (§5c) |
| **Dims (m)** | `ob.dimensions` | Escala real: un personaje ≈1.8 m; una taza ≈0.1 m. Si sale ×100, el asset venía mal escalado |
| **Pivote** | `ob.location` / origen | Base entre los pies / bisagra / centro — la convención de pivote [ver: blender/import-export] |
| **UV sets** | `len(me.uv_layers)` | 1 (UV0) o 2 (UV0+lightmap). Si hay UV2 → recibe bake |
| **Materiales-slot** | `me.materials` | Nº de materiales objetivo (¿1 por prop?) |
| **Naming** | `ob.name`, `me.name`, sufijos `_LOD0..n` | El esquema de nombres del proyecto |

### 5b. Medir el mesh ya importado en Unity (editor-script / UnityMCP)

Si Unity está conectado por MCP, `execute_code` corre un editor-script que lee el `Mesh` importado directamente — más fiel que Blender porque mide lo que el engine realmente usa ([ver: unity/unity-mcp-flujo]):

```csharp
// Mide malla + material de un asset de referencia. AssetDatabase + Mesh + Material.
using UnityEditor; using UnityEngine;
var mesh = AssetDatabase.LoadAssetAtPath<Mesh>("Assets/Ref/Prop.fbx");
int tris = mesh.triangles.Length / 3;                 // triangles.Length/3 = tri count
Debug.Log($"verts:{mesh.vertexCount} tris:{tris} sub:{mesh.subMeshCount} " +
          $"bounds:{mesh.bounds.size} uv2:{mesh.uv2.Length>0} " +
          $"blendshapes:{mesh.blendShapeCount} bindposes:{mesh.bindposeCount}");
foreach (var m in AssetDatabase.LoadAllAssetsAtPath("Assets/Ref/Prop.fbx"))
    if (m is Material mat) Debug.Log($"mat:{mat.name} shader:{mat.shader.name}");
```

`Mesh.vertexCount` es **el conteo real del engine** (con los splits) — el número que de verdad audita el presupuesto [ver: modelado/presupuestos-poligonos §1]. `mesh.bounds.size` da las dimensiones; `subMeshCount` ≈ nº de materiales; `blendShapeCount`/`bindposeCount` delatan blendshapes y rig.

### 5c. Texel density (si hay textura + UVs)

Métrica que iguala la nitidez entre assets. **TD (px/m) = resolución_textura × largo_UV_de_una_arista / largo_mundo_de_esa_arista.** Medición práctica: toma una cara conocida, su longitud en el mundo (m) y su longitud en UV (0-1), multiplica por el lado de la textura en px. Si el pack de referencia corre a ~512 px/m en props y ~1024 en héroes, ese es el estándar a declarar en la ficha [ver: texturizado/texturas-a-unity], [ver: pipeline/arte-a-unity §7]. Addons de Blender (Texel Density Checker) automatizan la lectura; el número, no la herramienta, es lo que va a la ficha.

## 6. Leer un material / shader: el estándar de textura

Con el material cargado (`AssetDatabase.LoadAssetAtPath<Material>` o desde el FBX), la API de `Material` expone todo:

| Qué | Cómo | Qué aprendes |
|---|---|---|
| Shader | `mat.shader.name` | `Universal Render Pipeline/Lit` vs `Simple Lit`/`Unlit`/custom → el nivel de PBR del proyecto [ver: unity/rendering-urp] |
| Mapas asignados | `mat.GetTexturePropertyNames()` → `mat.GetTexture(name)` | Qué slots usa: `_BaseMap`, `_BumpMap`, `_MetallicGlossMap`, `_OcclusionMap`, `_EmissionMap` |
| Valores escalares | `mat.HasProperty(n)` → `mat.GetFloat("_Metallic")`, `GetFloat("_Smoothness")`, `GetColor("_BaseColor")` | Si el look es por textura o por constantes |
| Empaquetado de canales | ¿hay `_MetallicGlossMap`? → smoothness va en su **alpha** (`_SmoothnessTextureChannel`) | La convención MetallicSmoothness [ver: texturizado/texturas-a-unity §4] |
| Keywords | `mat.enabledKeywords` / `mat.shaderKeywords` | Features activas: `_NORMALMAP`, `_EMISSION`, `_ALPHATEST_ON` |
| sRGB por mapa | del `.meta` de CADA textura (`sRGBTexture`) | La regla sRGB del proyecto: color ON, normal/metallic/AO OFF [ver: texturizado/texturas-a-unity §2] |

El material te dice el **contrato de canales**: qué mapas espera, cómo empaqueta smoothness (alpha del metallic), qué convención de normal usa (mirar `flipGreenChannel` en el `.meta` del normal → OpenGL vs DirectX). Con eso replicas el set de mapas exacto que el pack asume.

## 7. Leer un rig y sus clips

### El esqueleto y el Avatar

Desde el `ModelImporter` del FBX (propiedades verificadas, Unity ScriptReference):

| Propiedad | Da | Convención |
|---|---|---|
| `animationType` | None/Legacy/Generic/**Humanoid** | La decisión maestra del rig [ver: rigging/rig-a-unity] |
| `humanDescription` | mapa hueso→Avatar humano (`.human`, `.skeleton`) | El naming de huesos y el mapeo Humanoid |
| `skinWeights` / `maxBonesPerVertex` | cap de influencias por vértice | `skinWeights` = Standard (≤4, GPU skinning) o Custom; `maxBonesPerVertex` fija el número exacto en Custom |
| `optimizeGameObjects` | jerarquía de huesos colapsada sí/no | Política de rendimiento [ver: rigging/rig-a-unity §7] |
| `sourceAvatar` | Avatar copiado de otro modelo | Si los clips comparten esqueleto (Copy From Other Avatar) |

Conteo de huesos y jerarquía: en Blender por `bpy` (`len(armature.data.bones)`, y los nombres) tras reimportar; en Unity, el `SkinnedMeshRenderer.bones.Length` del prefab o `mesh.bindposeCount`. Naming (`mixamorig:`, `.L/.R`, `DEF-`) delata el origen del rig (Mixamo, Rigify, custom) [ver: rigging/rig-a-unity §1].

### Los clips

Un modelo importado expone sus clips como `AnimationClip` (via `AssetDatabase.LoadAllAssetsAtPath`). Propiedades verificadas:

| Propiedad | Da |
|---|---|
| `length`, `frameRate` | Duración (s) y fps de muestreo |
| `humanMotion` | `true` si maneja un rig humanoide (clip Humanoid) |
| `hasGenericRootTransform`, `hasMotionCurves` | Si tiene root/root-motion |
| `empty` | Clip sin curvas |

El estado de **loop** de un clip importado NO está en la propiedad del clip sino en el import: `ModelImporter.clipAnimations[i].loopTime` (`ModelImporterClipAnimation`). Para saber "¿el walk loopea? ¿el idle?", se lee ahí o en el bloque `clipAnimations` del `.meta` (§3). Root motion y su configuración: [ver: rigging/rig-a-unity §6], [ver: animacion3d/principios-produccion]. Un **AnimatorController** (`.controller`, también YAML) revela estados, transiciones y máscaras — su lectura por texto sigue la misma lógica de §4.

## 8. Leer un atlas / spritesheet 2D

Para un asset 2D empaquetado, todo sale del `TextureImporter` del `.meta` y de la API de sprite:

| Métrica | De dónde | Convención |
|---|---|---|
| **PPU** | `TextureImporter.spritePixelsPerUnit` (`spritePixelsPerUnit` en el `.meta`) | El contrato mundo↔imagen [ver: pipeline/arte-a-unity §2] |
| **Layout / sub-sprites** | `TextureImporter.spritesheet` (array de `SpriteMetaData`: `rect`, `pivot`, `alignment`) | Grid o packing, cuántos frames, pivote por sprite |
| **Border (9-slice)** | `spriteBorder` / `SpriteMetaData.border` | Si hay 9-slicing y su grosor [ver: pipeline/arte-a-unity §4] |
| **Padding / packing** | `SpriteAtlas` asset (`.spriteatlas`, YAML): `packingSettings` (padding, rotation, tight) | La política de atlas del proyecto [ver: unity/assets-pipeline-git] |
| **Filter / compresión** | `filterMode` (Point=pixel art), `textureCompression`, `mipmapEnabled` | Pixel art vs HD [ver: pipeline/arte-a-unity §3] |

`filterMode: 0` (Point) + `Compression None` + `mipmaps off` = pixel art; ese trío en el `.meta` identifica el estándar sin abrir la imagen.

## 9. El runbook del agente (herramientas)

Orden de menor a mayor coste; parar en cuanto la ficha esté completa:

1. **Texto (siempre primero, gratis):** `Read`/grep sobre `.meta`, `.prefab`, `.controller`, `.spriteatlas`. Saca escala, rig type, sRGB, PPU, LODGroup, nº materiales, clips y loops. El 60% de la ficha sale de aquí sin abrir nada.
2. **Blender headless por `bpy`/MCP** ([ver: blender/blender-mcp-operativo]): reimportar el FBX y medir tris/verts/dims/pivote/UVs/huesos (§5a). Para geometría y escala reales.
3. **Unity por UnityMCP** ([ver: unity/unity-mcp-flujo]): `manage_asset` para leer import settings vía API; `execute_code` para un editor-script que mide `Mesh`/`Material`/clips con los conteos reales del engine (§5b) y verifica el material bajo el Lit y luz reales (nada aprobado desde un viewport neutro [ver: texturizado/texturas-a-unity §8]).
4. **Volcar a la ficha (§10)** con CADA número y su origen (archivo:campo o comando). Sin evidencia, el dato no entra.

Regla: la malla real (Blender/Unity) manda sobre lo que diga el `.meta`; y el `Mesh.vertexCount` del engine manda sobre el vert count del DCC.

## 10. La ficha de convenciones (output)

Plantilla del entregable — cada celda con número medido y su fuente, "no medido" donde falte (nunca inventar) [ver: pipeline-completo-3d] la usa como spec de producción:

```
FICHA — <nombre del asset/pack de referencia>            fecha · fuente(licencia)
── Malla ────────────────────────────────────────────────
categoría        : prop / héroe / arma / vehículo / módulo
tris (LOD0)      : N            (fuente: Mesh.triangles/3 en Unity)
verts (engine)   : N            (Mesh.vertexCount)
LODs             : n niveles, ratios _____   (LODGroup del prefab)
escala           : 1 u = 1 m (dims X×Y×Z m)  (bpy ob.dimensions)
pivote           : base/bisagra/centro       (bpy origin)
UV sets          : UV0 [+UV2 lightmap]
naming           : Prefijo_Nombre_LOD0..n
── Textura / Material ───────────────────────────────────
shader           : URP/Lit | Simple Lit | Unlit | custom
mapas            : Base, Normal(OpenGL/DX), MetallicSmoothness, AO, Emission
empaquetado      : smoothness en alpha de _MetallicGlossMap
sRGB             : color ON · normal/metallic/AO OFF  (.meta sRGBTexture)
texel density    : ~___ px/m
resolución       : 512/1024/2048 · compresión ___
nº materiales    : N por asset
── Rig / Animación ──────────────────────────────────────
animationType    : Humanoid | Generic  (ModelImporter)
huesos           : N   naming: mixamorig:/.L.R/DEF-
avatar           : Create From This | Copy From Other
clips            : idle(loop), walk(loop), ...  (loopTime)
── 2D (si aplica) ───────────────────────────────────────
PPU · layout · border(9-slice) · padding · filter(Point/Bilinear)
```

Un dato sin fuente NO va a la ficha. La ficha aprobada se congela como spec y todo asset nuevo se audita contra ella con el runbook de [ver: pipeline/arte-a-unity §10].

## 11. Ética y licencia

- Aprender las **convenciones técnicas** (polycount, texel density, naming, empaquetado de canales, tipo de rig) es legítimo y es el punto de esta fase: son estándares, no propiedad.
- **No** copiar ni redistribuir la geometría, las texturas ni las animaciones de un asset comprado/licenciado. Medirlo para igualar su estándar ≠ reusar sus bits.
- Un asset del **Asset Store / marketplace** viene con licencia: respetar sus términos (uso en TU proyecto sí; reventa/redistribución del asset o de derivados casi siempre no). Ante duda, leer la licencia antes de tocar el archivo.
- La ficha (§10) contiene **números y convenciones**, no assets: es seguro compartirla y versionarla. Los archivos de referencia licenciados, no.

## Reglas prácticas

1. El objetivo es la FICHA de convenciones (§10) con cada número medido y su fuente — no una impresión "a ojo" del asset.
2. Texto primero: `.meta`/`.prefab`/`.controller` son YAML; grep saca escala, rig, sRGB, PPU, LODs y clips sin abrir Unity.
3. El `guid` del `.meta` es la identidad del asset; por él lo referencian los prefabs (`{fileID, guid, type}`) — así rastreas qué material/mesh usa cada prefab.
4. `animationType`: 2=Generic, 3=Humanoid en el `.meta` — la decisión maestra del rig se lee en una línea.
5. Cuenta tris SIEMPRE en el engine: `Mesh.triangles.Length/3`; audita verts con `Mesh.vertexCount` (el real, con splits), no el del DCC [ver: modelado/presupuestos-poligonos §1].
6. Escala real por `ob.dimensions` en Blender: personaje ≈1.8 m, prop chico ≈0.1 m; si sale ×100, el asset venía mal.
7. Texel density se MIDE (res × largo_UV / largo_mundo) y se declara en px/m; iguala nitidez entre assets.
8. Del material: `shader.name` + `GetTexturePropertyNames()` + `GetFloat` = shader, mapas y si el look es por textura o constantes.
9. Empaquetado: si hay `_MetallicGlossMap`, el smoothness va en su alpha; el normal es OpenGL/DirectX según `flipGreenChannel` del `.meta` [ver: texturizado/texturas-a-unity §3-4].
10. sRGB por mapa se lee en cada `.meta` (`sRGBTexture`): color=1, dato=0 — esa es la regla del proyecto.
11. Nº de materiales por asset = `subMeshCount`/`m_Materials` del prefab: confirma si el estándar es 1 por prop.
12. LODs: cuenta `!u!205` y lee los `screenRelativeTransitionHeight` del prefab para la política de LOD [ver: modelado/presupuestos-poligonos §4].
13. Clips: `length`/`frameRate`/`humanMotion` del `AnimationClip`; el **loop** está en `ModelImporter.clipAnimations[i].loopTime`, no en el clip.
14. La malla real manda sobre el `.meta`; el vert count del engine manda sobre el del DCC.
15. Verifica el material aprendido bajo el Lit y la luz reales antes de darlo por bueno, nunca desde un viewport neutro [ver: texturizado/texturas-a-unity §8].
16. Aprende convenciones, no assets: medir para igualar el estándar es legítimo; copiar/redistribuir geometría o texturas licenciadas, no (§11).

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Deducir el polycount "a ojo" o del README del pack | Medir: `bpy` sobre el FBX o `Mesh.triangles.Length/3` en Unity |
| Fiarse del vert count del DCC | El engine parte 2-3× por seams/hard-edges/materiales; usar `Mesh.vertexCount` [ver: modelado/presupuestos-poligonos §1] |
| Abrir Unity para leer un import setting | El `.meta` es texto: grep `sRGBTexture`/`animationType`/`globalScale` en segundos |
| Asumir Humanoid/Generic por cómo se ve | `animationType` en el `.fbx.meta` (2=Generic, 3=Humanoid) lo dice exacto |
| Copiar el shader "URP Lit" sin ver el empaquetado | Revisar `_MetallicGlossMap` (smoothness en alpha) y `flipGreenChannel` del normal; el contrato de canales importa más que el nombre del shader |
| Igualar texturas sin medir texel density | Medir px/m de una cara conocida y declararlo; si no, el asset nuevo se ve más/menos nítido que el pack |
| Tomar el naming de un asset como universal | Confirmar el patrón en varios assets del pack antes de fijarlo como convención |
| Ficha con números sin fuente | Cada celda lleva archivo:campo o comando; "no medido" donde falte — nunca inventar |
| Leer el loop en la propiedad del clip | El loop de un clip importado está en `clipAnimations[i].loopTime` del importer |
| Copiar la geometría/texturas del asset licenciado "porque las medí" | Se aprende el estándar, no los bits; redistribuir el asset viola su licencia (§11) |

## Fuentes

- **AssetImporter.GetAtPath** — Unity ScriptReference 6000.2 — recupera el importer del asset en `path`; se castea a `TextureImporter`/`ModelImporter`/`AudioImporter` para leer/escribir import settings desde editor.
- **ModelImporter (Scripting API)** — Unity ScriptReference 6000.2 — propiedades verificadas: `animationType`, `globalScale`, `useFileScale`/`fileScale` (read-only), `humanDescription`, `clipAnimations`/`defaultClipAnimations`, `materialImportMode`, `meshCompression`, `optimizeGameObjects`, `sourceAvatar`, `skinWeights`, `generateSecondaryUV`, `importNormals`.
- **AssetDatabase (Scripting API)** — Unity ScriptReference 6000.2 — `FindAssets`, `GUIDToAssetPath`, `AssetPathToGUID`, `LoadAssetAtPath`, `LoadAllAssetsAtPath`, `GetDependencies`.
- **Mesh (Scripting API)** — Unity ScriptReference 6000.2 — `vertexCount` (conteo real del engine, read-only), `triangles` (`Length/3` = tris), `subMeshCount`, `bounds`, `uv`/`uv2`, `normals`, `tangents`, `boneWeights`, `bindposeCount`, `blendShapeCount`.
- **Material (Scripting API)** — Unity ScriptReference 6000.2 — `shader`/`shader.name`, `GetTexture`, `GetTexturePropertyNames`, `GetFloat`, `GetColor`, `HasProperty`, `enabledKeywords`/`shaderKeywords`, `mainTexture`.
- **AnimationClip (Scripting API)** — Unity ScriptReference 6000.2 — `length`, `frameRate`, `wrapMode`, `humanMotion`, `hasGenericRootTransform`, `hasMotionCurves`, `empty`.
- **Meta files / Import metadata** — Unity Manual 6000.2 (`AssetMetadata.html`) — `.meta` uno por asset/carpeta, contiene GUID + todos los import settings; texto; el GUID rastrea referencias y debe ir a control de versiones.
- **Description of the format (text scenes/prefabs)** — Unity Manual 6000.2 (`FormatDescription.html`) — subset de YAML, `--- !u!<classID> &<fileID>`, `m_Component`/`{fileID}`, referencias externas `{fileID, guid, type}`.
- **YAML Class ID Reference** — Unity Manual 6000.2 (`ClassIDReference.html`) — mapeo classID→tipo (1 GameObject, 4 Transform, 33 MeshFilter, 23 MeshRenderer, 137 SkinnedMeshRenderer, 205 LODGroup, 114 MonoBehaviour, 1001 PrefabInstance).
- **Bases sintetizadas** — [ver: modelado/presupuestos-poligonos] (tris/verts del engine, splits, LOD ratios), [ver: texturizado/texturas-a-unity] (sRGB por mapa, MetallicSmoothness, normal OpenGL/DX, verificación bajo Lit), [ver: rigging/rig-a-unity] (Humanoid vs Generic, Avatar, clips/loop, root motion, Optimize Game Objects), [ver: blender/import-export] (reimport headless por `bpy`, escala/ejes, roundtrip por GUID), [ver: pipeline/arte-a-unity] (spec de entrega, runbook de auditoría §10). Puentes en pipeline-assets: [ver: pipeline-completo-3d], [ver: blender-unity-bridge], [ver: organizacion-versionado-3d]. Herramientas: [ver: unity/unity-mcp-flujo], [ver: blender/blender-mcp-operativo], [ver: blender/bpy-scripting].
