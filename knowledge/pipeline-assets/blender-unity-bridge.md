# El puente técnico Blender↔Unity

> **Cuando cargar este archivo:** cuando un asset 3D cruza de Blender a Unity y hay que cerrar el flujo COMPLETO — escala/ejes/unidades definitivos, materiales/colliders/LODs/sockets en el cruce, el roundtrip sin romper prefabs, o automatizar los import settings con un AssetPostprocessor. Es el nodo que UNIFICA el bloque de arte 3D (modelado/blender/texturizado/rigging/animación) con Unity: aquí no se re-explica cada eslabón — se conecta y se cierra. El detalle de cada extremo vive en su base; este archivo es el contrato entre extremos.

## El mapa: quién hace qué en el punta a punta

El puente tiene cinco tramos. Cada tramo tiene un dueño; este archivo es el pegamento y el punto de fallo.

| # | Tramo | Dueño (base) | Qué cierra ESTE archivo |
|---|---|---|---|
| 1 | Modelar/texturizar/riggear en metros, naming limpio | [ver: modelado/topologia] [ver: texturizado/uv-unwrapping] [ver: rigging/esqueletos-armature] | El contrato de naming y pivots que Unity necesita |
| 2 | Exportar FBX (settings, escala, ejes, batch) | [ver: blender/import-export] | La tabla DEFINITIVA de escala/ejes y el checklist anti -89.98 |
| 3 | Importar en Unity (Model tab, materiales, colliders) | [ver: pipeline/arte-a-unity] [ver: unity/assets-pipeline-git] | Qué cruza y qué se reconstruye; automatizarlo por código |
| 4 | Montar el prefab de juego (componentes, física) | [ver: unity/fisica-unity] [ver: pipeline-3d/receta-prop] | El Prefab Variant que sobrevive al re-export |
| 5 | Versionar source vs exportado, git LFS | [ver: unity/assets-pipeline-git] [ver: organizacion-versionado-3d] | Estructura .blend↔FBX y el roundtrip robusto |

**El principio que gobierna todo el puente:** el `.blend` es la FUENTE re-exportable; el `.fbx` en `Assets/` es el binario que Unity consume y trackea; el material, el collider dinámico y los componentes de juego son de UNITY. El FBX es un tubo que transporta geometría + jerarquía + nombres, no un contenedor de la escena final. Todo lo que se "reconstruye en Unity" se automatiza una vez con un AssetPostprocessor y deja de tocarse a mano.

## La tabla DEFINITIVA del handoff (escala · ejes · unidades)

Un solo lugar de verdad. El detalle mecánico (el binario FBX, `apply_scale_options`, el porqué del 100×) está en [ver: blender/import-export]; aquí queda la decisión cerrada y el criterio de aceptación.

| Dimensión | Blender (salida) | FBX (el tubo) | Unity (entrada) | Criterio de aceptación |
|---|---|---|---|---|
| **Unidad** | Escena en **metros**, Unit Scale 1.0, modelar a tamaño real (personaje ≈1.8 m) | `UnitScaleFactor` | Física asume **1 unidad = 1 m** | Instancia junto a un Cube (1 m³): tamaño correcto |
| **Escala (el 100×)** | Export Scale **1.0** + Apply Scalings = **FBX Units Scale** (`FBX_SCALE_UNITS`) | `UnitScaleFactor = 100` (= m) | File Scale **1**, transforms limpios | Model tab: File Scale = 1 (si sale 0.01, faltó FBX Units Scale) |
| **Ejes** | Z-up → export Forward **-Z**, Up **Y** (defaults) | Y-up | Y-up, left-handed, forward **+Z** | El modelo mira a +Z |
| **Transforms** | `Ctrl+A ‣ All Transforms` antes de exportar (en Object Mode, rig en rest pose) | rotaciones/escala horneadas | — | Escala (1,1,1) |
| **Rotación raíz** | Use Space Transform ON mete -90° en X | -90° X en el root | Unity lo muestra como **-89.98°** | Rot (0,0,0) — ver checklist abajo |
| **Pivot** | `Set Origin` donde el juego lo usa (base/bisagra/agarre) | origen del objeto | pivot no editable | Apoya en Y=0 sin offset; gira sobre el punto lógico |

### El checklist que mata el -89.98 de una vez

El -89.98 es cosmético (el modelo se ve bien) pero ensucia cada prefab. Elegir UNA vía por tipo de asset y aplicarla siempre:

1. **Blender, siempre:** escena en metros → `Ctrl+A ‣ All Transforms` → export Scale 1.0 + FBX Units Scale + Forward -Z/Up Y.
2. **Props estáticos:** en Unity, importer `bakeAxisConversion = true` (hornea la conversión en vértices → transform limpio). Alternativa en Blender: el contra-giro -90/apply/+90 [ver: blender/import-export].
3. **Characters/rigged:** **NO** hornear ejes en Blender (`bake_space_transform` rompe armatures). Opciones: aceptar el -89.98 (es solo cosmético) o `bakeAxisConversion` en Unity (funciona con rigs). Nunca el contra-giro sobre un armature con pose.
4. **Criterio final:** la instancia recién arrastrada a la escena tiene rot (0,0,0), scale (1,1,1), mira a +Z y apoya en Y=0. Si no → se corrige en el importer o en el export, JAMÁS en `transform.localScale`.

## FBX vs glTF: la decisión final 2026

| Caso de uso | Formato | Por qué |
|---|---|---|
| Pipeline editor→prefab (99% de los assets de juego) | **FBX** | Cadena de import interna de Unity; rig/anim/blendshapes por el flujo Mecanim probado |
| Rigs, animación, blendshapes | **FBX** | Camino canónico (Humanoid/Generic, clips, convención `@`) [ver: unity/animacion-unity] |
| Carga de modelos en **runtime** (UGC, catálogos, mods) | **glTF (.glb)** | `com.unity.cloud.gltfast` carga en runtime; Draco/KTX2/meshopt |
| Pipeline glTF-first o validar fuera de Unity | glTF | PBR metallic-roughness viaja mejor por spec |
| `.blend` directo en `Assets/` | **NUNCA en producción** | Exige Blender en cada máquina/CI; Unity lo convierte a FBX por debajo igual |

Regla cerrada: **FBX para el prefab, glTF solo si el runtime lo carga.** Detalle de settings de ambos exportadores: [ver: blender/import-export].

## Qué cruza el puente y qué se reconstruye en Unity

El contrato exacto. Verificado empíricamente en Blender 5.2 [ver: blender/import-export] y contra el ModelImporter de Unity 6.

| Dato del asset | ¿Cruza en el FBX? | Se reconstruye en Unity |
|---|---|---|
| Malla (verts/tris/UV0) | ✅ | — |
| Custom split normals | ✅ (`LayerElementNormal`) | Normals = Import |
| UV2 (lightmap) | ✅ si existe | o `generateSecondaryUV = true` en el importer |
| Modificadores | ✅ con Apply Modifiers (excepto si hay shape keys) | — [ver: blender/modificadores] |
| Shape keys (blendshapes) | ✅ (Apply Modifiers OFF) | SkinnedMeshRenderer [ver: rigging/rig-a-unity] |
| Rig + skin weights | ✅ (Add Leaf Bones OFF) | Avatar (Humanoid/Generic) [ver: unity/animacion-unity] |
| Animaciones | ✅ (clips o convención `@`) | Clips en el importer / Animator |
| **Materiales** | ❌ solo **nombre + slot** | **El material REAL es de Unity** (§ abajo) |
| Texturas | ❌ (déjalas fuera, Path Mode Auto) | Se asignan al material de Unity [ver: texturizado/texturas-a-unity] |
| **Sockets** (Empties nombrados) | ✅ como GameObjects vacíos | Attach point directo (§ abajo) |
| **Colliders** (`UCX_*`) | ✅ como mallas | Se convierten por postprocessor (§ abajo) |
| **LODs** (`_LOD0..n`) | ✅ como mallas nombradas | LODGroup automático (§ abajo) |
| Geometry Nodes instances | ❌ (malla vacía) | Realize Instances ANTES [ver: blender/geometry-nodes] |

## Materiales en el cruce: el FBX solo lleva la etiqueta

El shader real NO viaja fiable por FBX — solo el **nombre del material y su asignación por slot**. El material de verdad (URP Lit, canales, smoothness) se construye en Unity. Tres vías, de menos a más automatizada:

1. **Extract Materials** (una vez, a mano): en el Model tab, extraer materiales y texturas a assets del proyecto → se desligan del FBX y sobreviven al re-export. Detalle de canales URP Lit y el gotcha roughness→smoothness: [ver: texturizado/texturas-a-unity] y [ver: pipeline/arte-a-unity §7].
2. **Remap por nombre** (semi-auto): `ModelImporter.SearchAndRemapMaterials(ModelImporterMaterialName, ModelImporterMaterialSearch)` busca en el proyecto materiales que coincidan por nombre y los mapea en vez de generar internos. Ideal cuando ya existe la librería de materiales de Unity.
3. **Remap por código** (auto, versionable): `OnAssignMaterialModel` en el postprocessor (código abajo).

Contrato para el artista/agente en Blender: **nombres de material limpios y estables** (`Metal_Brushed`, no `Material.001`), uno por slot esperado. Renombrar un material tras el primer import = materiales desasignados en prefabs existentes.

## Colliders por convención: dónde se hace cada cosa

| Caso | Dónde | Cómo |
|---|---|---|
| Entorno estático simple | Unity importer | `addCollider = true` → MeshCollider (caro; solo entorno) |
| Objeto dinámico | Prefab de Unity | Compound de primitivos (Box/Sphere/Capsule); MeshCollider convex ≤255 tris [ver: unity/fisica-unity] |
| Forma custom que exige malla | Blender + Unity | Malla convexa low-poly nombrada `UCX_<NombreExacto>` junto al render mesh → **postprocessor** la convierte en collider y borra su renderer |

`UCX_`/`UBX_`/`USP_`/`UCP_` es convención de **Unreal** (Epic): **Unity NO la procesa de serie**. Desde Blender el trabajo es idéntico (mallas convexas bien nombradas); en Unity lo cierra el `OnPostprocessModel` (abajo). Sin ese postprocessor, las mallas `UCX_*` se renderizan como geometría normal.

## Sockets / attachment points

Empties (Plain Axes) como hijos del mesh/rig en Blender → llegan a Unity como **GameObjects vacíos con su transform**, listos como puntos de anclaje (mira del arma, cañón, hardpoint, mano, tubo de escape). Prefijo de equipo consistente (`SOCKET_Muzzle`, `SOCKET_Hand_R`) — Unity no exige prefijo, es convención. En el prefab: `transform.Find("SOCKET_Muzzle")` para instanciar el muzzle flash / parentar el arma. Pivot y orientación del Empty en Blender = pivot y orientación del attach point en Unity, así que el Empty se orienta apuntando hacia donde saldrá el objeto. Naming y jerarquía completos: [ver: blender/import-export] · [ver: blender/organizacion-blend].

## LODs: exportar niveles → LODGroup automático

- En Blender: cada nivel es una malla nombrada `Nombre_LOD0` (máx detalle), `_LOD1`, `_LOD2`… dentro del MISMO FBX. Generación de los niveles (decimate/retopo, ~50% tris por nivel): [ver: modelado/presupuestos-poligonos] · [ver: modelado/high-to-low].
- En Unity: al importar el FBX con mallas `_LODn`, **crea el LODGroup automáticamente** (hasta 8 niveles, doc oficial). Los umbrales son **% de altura del objeto en pantalla** (screen relative transition height); último nivel = Culled. Ajuste arrastrando en el componente.
- Regla: pedir los LODs YA nombrados en el FBX. "Luego los hago" = nunca. Solo para props/entorno vistos a distancia variable; cámara fija no necesita LODs.

## AssetPostprocessor: automatizar el import (el patrón de código)

El corazón del puente automatizado. Un `AssetPostprocessor` en `Assets/.../Editor/` fuerza los settings al importar **cada** modelo de una carpeta, convierte los `UCX_` en colliders y remapea materiales — sin tocar el Model tab a mano nunca. APIs verificadas contra la Scripting Reference de Unity 6 (6000.2).

**Los hooks de modelo** (orden de ejecución):

| Hook | Firma | Cuándo | Uso |
|---|---|---|---|
| `OnPreprocessModel` | `void OnPreprocessModel()` | Al inicio del import | Setear ModelImporter (escala, normales, material mode, collider, UV2) |
| `OnAssignMaterialModel` | `Material OnAssignMaterialModel(Material src, Renderer r)` | Antes de asignar materiales | Remap al material real del proyecto (`null` = lógica default) |
| `OnPostprocessMeshHierarchy` | `void OnPostprocessMeshHierarchy(GameObject root)` | Jerarquía importada | Filtrar/ajustar objetos de la jerarquía |
| `OnPostprocessModel` | `void OnPostprocessModel(GameObject root)` | Import completo | Convertir `UCX_*` en colliders, limpiar |

```csharp
// Assets/_Game/Code/Editor/ModelImportRules.cs
using UnityEditor;
using UnityEngine;

public class ModelImportRules : AssetPostprocessor
{
    const string ROOT = "Assets/_Game/Art/Models/";

    // 1) Settings del importer — solo la primera vez (respeta ajustes manuales posteriores)
    void OnPreprocessModel()
    {
        if (!assetPath.StartsWith(ROOT)) return;
        var imp = (ModelImporter)assetImporter;
        if (!imp.importSettingsMissing) return;

        imp.globalScale   = 1f;
        imp.useFileScale  = true;                              // File Scale del FBX (1 si exportaste con FBX Units Scale)
        imp.bakeAxisConversion = true;                         // hornea Y-up → transform limpio, adiós -89.98
        imp.importNormals  = ModelImporterNormals.Import;      // Blender ya trae split normals
        imp.importTangents = ModelImporterTangents.CalculateMikk;
        imp.materialImportMode = ModelImporterMaterialImportMode.None; // el material real se hace en Unity
        imp.addCollider   = false;                             // colliders por UCX_ o primitivos en el prefab
        imp.isReadable    = false;                             // sin copia en CPU RAM salvo que un script lea la mesh
        imp.generateSecondaryUV = true;                        // UV2 lightmap si el asset recibe bake
    }

    // 2) Remap de materiales al material REAL del proyecto por nombre de slot
    public override Material OnAssignMaterialModel(Material source, Renderer renderer)
    {
        if (!assetPath.StartsWith(ROOT)) return null;
        foreach (var guid in AssetDatabase.FindAssets($"t:Material {source.name}",
                                                      new[] { "Assets/_Game/Art/Materials" }))
        {
            var m = AssetDatabase.LoadAssetAtPath<Material>(AssetDatabase.GUIDToAssetPath(guid));
            if (m != null && m.name == source.name) return m; // remap
        }
        return null; // sin match → Unity usa su lógica default
    }

    // 3) Convertir mallas UCX_/UBX_ (convención Unreal) en colliders y borrar su render
    void OnPostprocessModel(GameObject root)
    {
        if (!assetPath.StartsWith(ROOT)) return;
        foreach (var mf in root.GetComponentsInChildren<MeshFilter>(true))
        {
            var n = mf.gameObject.name;
            if (!n.StartsWith("UCX_") && !n.StartsWith("UBX_")) continue;
            var mc = mf.gameObject.AddComponent<MeshCollider>();
            mc.sharedMesh = mf.sharedMesh;
            mc.convex = true;
            Object.DestroyImmediate(mf.GetComponent<MeshRenderer>());
            Object.DestroyImmediate(mf);
        }
    }
}
```

- `importSettingsMissing` (heredada de `AssetImporter`) es true solo en el primer import → el postprocessor NO pisa ajustes que un artista tocó a mano después. Mismo patrón que los sprites [ver: unity/assets-pipeline-git §1].
- `OnAssignMaterialModel` es `virtual` (lleva `override`); los demás son mensajes por reflexión (sin `override`). `sourceMaterial` se destruye tras el callback — no guardar referencias a él, solo devolver el material del proyecto.
- Un asset que pasa por la carpeta correcta queda configurado sin intervención. Preset por carpeta es la alternativa sin código para casos simples [ver: unity/assets-pipeline-git §1].

## El roundtrip robusto: re-exportar sin romper el prefab

El re-export es donde el puente se rompe si no se cuida. La regla madre: **el GUID vive en el `.meta`, y el `.meta` se ancla al PATH del archivo.** Sobrescribir el mismo `.fbx` en el mismo path → mismo GUID → todos los prefabs/escenas/variantes que lo referencian sobreviven.

| Acción en el roundtrip | Hacer | No hacer |
|---|---|---|
| Volver a exportar | Sobrescribir el **mismo path** en `Assets/`; Unity reimporta y conserva GUID | Borrar el `.fbx` y reimportar (GUID nuevo → todo roto) |
| Refrescar un import cacheado | Click derecho ‣ **Reimport** (o `AssetDatabase.ImportAsset(path)`) | Borrar para "refrescar" |
| Nombres de objeto/malla/material | **Congelarlos** tras el primer import (Unity re-enlaza sub-assets por nombre) | Renombrar en Blender a la ligera → MeshFilters vacíos, materiales sueltos |
| Componentes de juego (rigidbody, scripts, colliders dinámicos) | En un **Prefab Variant** que anida el model prefab; los overrides sobreviven al re-export | Editar el model prefab directo |
| Mover/renombrar el asset | Solo dentro del Editor (el `.meta` viaja) o `git mv` de ambos | Desde el Finder/terminal (el `.meta` se queda) |
| Ajustes del Model tab | Viven en el `.meta`, persisten entre re-exports | — |

**APIs de AssetDatabase para el roundtrip por código** (verificadas):

| Método | Uso en el puente |
|---|---|
| `ImportAsset(path)` | Forzar reimport de un FBX recién sobrescrito |
| `Refresh()` | Reimportar todo lo cambiado en disco |
| `AssetPathToGUID(path)` / `GUIDToAssetPath(guid)` | Verificar que el GUID no cambió tras re-export |
| `LoadAssetAtPath<T>(path)` | Cargar el prefab/material para validar |
| `StartAssetEditing()` / `StopAssetEditing()` | Batchear el reimport de muchos FBX (una sola pasada) |
| `GetAssetDependencyHash(path)` | Detectar si el contenido cambió de verdad |

El `.blend` puede quedar como fuente re-exportable de un click con **Collection Exporters** (Blender 4.2+): cada colección guarda su ruta al `Assets/` de Unity y sus settings → `Export All` regenera todos los FBX [ver: blender/import-export]. Con blendshapes: recordar que el importador FBX nativo de Blender 5.x no los reimporta de vuelta (usar Legacy si se perdió el `.blend`).

## Estructura: source (.blend) vs exportado (FBX) + git LFS

Dos mundos separados. El `.blend` es taller; el `.fbx` es producto que Unity trackea.

```
proyecto/
  art-source/                      ← FUERA del proyecto Unity (repo aparte o carpeta hermana)
    models/personaje.blend         ← la FUENTE re-exportable (git LFS)
    textures/*.psd, *.substance
  UnityProject/
    Assets/_Game/Art/
      Models/personaje.fbx         ← el exportado + personaje.fbx.meta (GUID estable, git LFS)
      Materials/*.mat              ← materiales REALES de Unity
      Textures/*.png               ← (git LFS)
    Assets/_Game/Prefabs/
      Personaje.prefab             ← Prefab Variant con componentes de juego
```

- **`.blend` NUNCA dentro de `Assets/`** — exige Blender en cada máquina/CI y acopla a la versión local. `Assets/` recibe solo el FBX exportado [ver: pipeline/arte-a-unity §7].
- **git LFS obligatorio** para `.fbx`, `.blend`, `.png`, `.tga`, `.exr` — el `.gitattributes` canónico ya los cubre; `git lfs install` antes del primer commit de binarios [ver: unity/assets-pipeline-git §5].
- **El `.fbx` y su `.meta` viajan en el mismo commit**, siempre — perder el `.meta` = GUID nuevo = referencias rotas en cascada [ver: unity/assets-pipeline-git §5].
- Naming `Prefijo_Nombre_Variante` consistente (`SM_Crate_Wood`, `SK_Hero`); source y exportado comparten el nombre base. Organización interna del `.blend`: [ver: blender/organizacion-blend]. Versionado 3D a fondo: [ver: organizacion-versionado-3d].

## Validación end-to-end (el gate antes de "listo")

Ningún "listo" sin haber abierto el asset EN Unity. Dos capas:

1. **Pre-vuelo headless en Blender** (barato, atrapa lo gordo): reimportar el FBX en una escena vacía y medir dims/escala/mallas vacías — código en [ver: blender/import-export]. No detecta el -89.98 ni valida blendshapes.
2. **Validación real en Unity** (definitiva, vía MCP si está [ver: unity/unity-mcp-flujo]): importar el FBX, instanciar el prefab y leer del resultado:
   - Transform: rot (0,0,0) o -89.98 conocido/aceptado, scale (1,1,1), File Scale = 1.
   - Tamaño real contra un Cube de 1 m; apoya en Y=0 por su pivot.
   - Un material slot por material esperado, nombres correctos, nada rosado bajo la LUZ real del juego.
   - Sockets presentes; sin Empties basura; sin huesos `_end` (si hay → Add Leaf Bones OFF y re-exportar).
   - Clips esperados y solo esos; blendshapes en el SkinnedMeshRenderer si aplica.
   - `UCX_*` convertidos por el postprocessor; LODGroup creado si hay `_LODn`.
   - Consola de Unity limpia de warnings del importador.

Metodología de aprender de assets ya integrados (leer un FBX/prefab bueno para deducir su spec): [ver: aprender-de-assets]. El flujo completo de producción 3D del que este puente es el cierre: [ver: pipeline-completo-3d].

## Reglas prácticas

1. El `.blend` es la fuente re-exportable; el `.fbx` en `Assets/` es el producto trackeado; el material/collider dinámico/componentes son de Unity.
2. Blender en metros, Unit Scale 1.0, modelar a tamaño real; en Unity **1 unidad = 1 m** verificado contra un Cube.
3. `Ctrl+A ‣ All Transforms` antes de CADA export (rig en rest pose, Object Mode).
4. Export Scale 1.0 + Apply Scalings = **FBX Units Scale** → File Scale 1 en Unity (nunca escalar el Transform para compensar).
5. -89.98: props → `bakeAxisConversion` en Unity o contra-giro en Blender; rigged → aceptarlo o `bakeAxisConversion`, JAMÁS `bake_space_transform` con armatures.
6. Criterio de aceptación de ejes: instancia rot (0,0,0), scale (1,1,1), mira +Z, apoya en Y=0.
7. FBX para el prefab; glTF solo si el juego carga modelos en runtime.
8. Materiales: nombre limpio y estable por slot en Blender; el material REAL se construye/remapea en Unity (Extract, SearchAndRemapMaterials u OnAssignMaterialModel).
9. Colliders: `UCX_<NombreExacto>` en Blender + `OnPostprocessModel` en Unity; dinámicos = primitivos en el prefab; MeshCollider solo entorno estático.
10. Sockets: Empties nombrados y orientados hacia la salida del objeto → attach points en Unity.
11. LODs: mallas `_LOD0..n` en el mismo FBX → LODGroup automático; pedirlos ya nombrados en la entrega.
12. Automatizar los import settings con un `AssetPostprocessor` por carpeta (o Preset), UNA vez — nunca configurar el Model tab a mano asset por asset.
13. `importSettingsMissing` en el preprocessor para no pisar ajustes manuales posteriores.
14. Roundtrip: sobrescribir el MISMO path (GUID en el `.meta`); Reimport para refrescar, nunca borrar.
15. Congelar nombres de objeto/malla/material tras el primer import; renombrar = migración consciente.
16. Componentes de juego en un Prefab Variant que anida el model prefab, no en el model prefab directo.
17. `.blend` FUERA de `Assets/`; git LFS para `.fbx`/`.blend`/texturas; `.fbx` + `.meta` en el mismo commit.
18. Todo "listo" = FBX abierto en Unity y el gate pasado (transform, material, sockets, LOD, consola limpia), no "el export no dio error".

## Errores comunes

| Pitfall | Síntoma en Unity | Antídoto |
|---|---|---|
| Export con Apply Scalings default ("All Local") | Escala (100,100,100), File Scale 0.01 | `FBX_SCALE_UNITS` en el export |
| Transforms sin aplicar en Blender | Tamaños/rotaciones absurdos, mirrors volteados | `Ctrl+A ‣ All Transforms` pre-export |
| Rotación -89.98 aceptada como bug de datos | Se "arregla" tocando el transform y descuadra | Es cosmético: `bakeAxisConversion` o contra-giro, nunca el Transform |
| `bake_space_transform` con armature | Rig/animación rotos | Hornear ejes solo en props estáticos; rigged va por Unity |
| Confiar en materiales del FBX | Materiales rosados o genéricos | El material real es de Unity: Extract/remap; nombres estables por slot |
| Esperar que Unity procese `UCX_` solo | Mallas de colisión renderizadas como geometría | Es convención de Unreal: `OnPostprocessModel` propio o `addCollider` |
| Escalar el Transform para corregir tamaño | Física/normales mal, LODs desalineados | Corregir en el importer (globalScale/useFileScale), nunca en `localScale` |
| Borrar el FBX y reimportar "para refrescar" | Todas las referencias rotas (GUID nuevo) | Sobrescribir el mismo path; Reimport / `ImportAsset` |
| Renombrar mallas/materiales en Blender | MeshFilters vacíos, materiales sueltos en prefabs | Congelar nombres tras el primer import |
| Editar el model prefab directo | Los cambios se pierden al re-export | Prefab Variant que anida el modelo |
| `.blend` dentro de `Assets/` | Rompe en máquinas/CI sin Blender, acoplado a la versión | `.blend` fuera; exportar FBX explícito |
| Binario commiteado sin LFS | Repo inflado para siempre | `git lfs install` + `.gitattributes` en el commit 0 |
| Configurar el Model tab a mano en cada asset | Drift de settings, imports inconsistentes | `AssetPostprocessor` por carpeta, una vez |
| Postprocessor sin `importSettingsMissing` | Pisa ajustes que un artista tocó a mano | Guard con `importSettingsMissing` |
| "Los LODs los hago después" | Nunca llegan | Exigir `_LOD*` en el FBX de entrega; Unity monta el LODGroup gratis |
| Aprobar el asset viendo el FBX suelto | Desentona en el juego | Gate en la escena real, cámara/luz/post reales, en Unity |

## Fuentes

- **Unity Scripting API 6000.2 — `AssetPostprocessor`** — docs.unity3d.com — mensajes de modelo (`OnPreprocessModel`, `OnAssignMaterialModel`, `OnPostprocessMeshHierarchy`, `OnPostprocessModel`, `OnPostprocessAllAssets`) y propiedades `assetPath`/`assetImporter`/`context`.
- **Unity Scripting API 6000.2 — `AssetPostprocessor.OnAssignMaterialModel`** — docs.unity3d.com — firma `Material OnAssignMaterialModel(Material, Renderer)`; devolver Material remapea, `null` = lógica default; el `sourceMaterial` se destruye tras el callback.
- **Unity Scripting API 6000.2 — `ModelImporter`** — docs.unity3d.com — propiedades exactas: `globalScale`, `useFileScale`, `bakeAxisConversion`, `importNormals`, `normalCalculationMode`, `importBlendShapes`, `importAnimation`, `animationType`, `materialImportMode`, `materialLocation`, `addCollider`, `isReadable`, `meshCompression`, `optimizeMeshPolygons/Vertices`, `generateSecondaryUV`, `importTangents`.
- **Unity Scripting API 6000.2 — `ModelImporter.SearchAndRemapMaterials`** — docs.unity3d.com — firma `bool SearchAndRemapMaterials(ModelImporterMaterialName, ModelImporterMaterialSearch)`; busca materiales del proyecto por nombre y los mapea en vez de los internos.
- **Unity Scripting API 6000.2 — `AssetDatabase`** — docs.unity3d.com — `ImportAsset`, `Refresh`, `ForceReserializeAssets`, `AssetPathToGUID`/`GUIDToAssetPath`, `LoadAssetAtPath`, `StartAssetEditing`/`StopAssetEditing`, `GetAssetDependencyHash` (roundtrip y estabilidad de GUID).
- **Bases sintetizadas:**
  - [ver: blender/import-export] — mecánica del export FBX/glTF, el 100× y el `UnitScaleFactor`, el -89.98 y sus remedios, qué exporta y qué no (verificado en Blender 5.2), Collection Exporters, validación headless.
  - [ver: pipeline/arte-a-unity] — spec de entrega 3D (escala/ejes/pivots), canales URP Lit, colliders, LODs, runbook de auditoría de assets.
  - [ver: unity/assets-pipeline-git] — import settings por tipo, Presets/AssetPostprocessor, estructura de carpetas, git + LFS + `.meta`/GUID, UnityYAMLMerge.
