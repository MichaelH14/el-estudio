# Import/export para Unity

> **Cuando cargar este archivo:** siempre que haya que sacar un asset de Blender hacia Unity (FBX o glTF), configurar un export, montar export batch por colecciones, o diagnosticar escala/rotación/normales/materiales rotos tras importar en Unity.

## Panorama 2026: FBX vs glTF hacia Unity

| Criterio | FBX | glTF (.glb) |
|---|---|---|
| Pipeline de editor Unity | **Formato nativo del importador de Unity** ("Unity uses the .fbx file format as its internal importing chain") | Requiere paquete `com.unity.cloud.gltfast` (oficial de Unity, v6.19 a jul-2026); import en editor y runtime |
| Exportador en Blender 5.2 | Add-on Python `io_scene_fbx` (bundled, en `addons_core`), operador `bpy.ops.export_scene.fbx` | Add-on Khronos `glTF-Blender-IO` (bundled desde 2.80), `bpy.ops.export_scene.gltf` |
| Rigs/animación a Unity | Camino probado (Humanoid/Generic, clips, blendshapes) | Funciona vía glTFast pero el flujo Mecanim clásico está pensado para FBX |
| Materiales | Solo nombres/slots fiables; el material real se rehace en Unity | PBR estándar (Principled BSDF → metallic/roughness) viaja mejor, pero glTFast no mapea a Lit/Standard por defecto |
| Carga en runtime (UGC, catálogos) | No | **Sí** — punto fuerte de glTFast (Draco, KTX2, meshopt) |

**Regla de decisión:** para el pipeline de assets de juego editor→prefab, **FBX**. glTF solo si el juego carga modelos en runtime o si el pipeline entero es glTF-first. Unity también abre `.blend` directo, pero exige Blender instalado en CADA máquina y por debajo lo convierte a FBX igual; la propia doc de Unity dice "Don't use proprietary file formats in production". No depender de eso.

## Estado de los exportadores en Blender 5.x (cambios vs 4.x)

- **Export FBX:** sigue siendo el add-on Python de siempre (`File ‣ Export ‣ FBX (.fbx)`, `export_scene.fbx`). No hay reescritura C++ del *export* en 5.2.
- **Import FBX:** desde **Blender 5.0 el importador por defecto es el nuevo nativo en C++** (basado en ufbx, añadido experimental en 4.5; 3-15× más rápido, soporta FBX ASCII y binarios pre-7.1). Operador nuevo: `bpy.ops.wm.fbx_import`. El Python viejo queda como `File ‣ Import ‣ FBX (.fbx) (Legacy)` (`import_scene.fbx`). **El importador nativo NO importa shape keys** (manual 5.2); para roundtrip con blendshapes, importar con el Legacy.
- **Blender 5.1:** el exportador FBX ahora escribe **normales de shape keys** (arregla imports de blendshapes en engines, Unity incluido).
- **Blender 5.2:** el exportador glTF añade compresión meshopt (`EXT_meshopt_compression`) y export de point clouds.
- **Collection Exporters** (desde 4.2): panel `Properties ‣ Collection ‣ Exporters` — mucho contenido web de 2.8-3.x no lo menciona y sigue enseñando export manual uno a uno.
- El manual oficial de la página "FBX (Legacy)" arrastra texto viejo: dice que los shape keys no se exportan ("Missing: Vertex shape keys") — **falso en 5.2, verificado empíricamente** (ver abajo).

## Settings EXACTOS de export FBX para Unity

`File ‣ Export ‣ FBX (.fbx)` — nombres tal cual la UI, con la propiedad Python de `export_scene.fbx`:

| Sección | Opción UI | Propiedad bpy | Valor para Unity | Por qué |
|---|---|---|---|---|
| Include | Limit to: Selected Objects | `use_selection` | ON si exportas selección | Control quirúrgico de qué sale |
| Include | Active Collection | `use_active_collection` | alternativa a selección | — |
| Include | Source Collection | `collection` (string) | nombre de colección | Export headless por colección [ver: bpy-scripting] |
| Include | Object Types | `object_types` | `{'EMPTY','ARMATURE','MESH'}` | Fuera cámaras/luces del asset |
| Transform | Scale | `global_scale` | **1.0** | Con unidades de escena en metros |
| Transform | Apply Scalings | `apply_scale_options` | **`FBX_SCALE_UNITS`** ("FBX Units Scale") | La clave del 100×, ver sección siguiente |
| Transform | Forward | `axis_forward` | **-Z Forward** (default) | Conversión estándar Blender→Y-up |
| Transform | Up | `axis_up` | **Y Up** (default) | ídem |
| Transform | Apply Unit | `apply_unit_scale` | ON (default) | Respeta las unidades de la escena |
| Transform | Use Space Transform | `use_space_transform` | ON (default) | Escribe la conversión de ejes en las rotaciones de objeto |
| Transform | Apply Transform | `bake_space_transform` | **OFF** | Experimental; "known to be broken with armatures/animations" (tooltip oficial) |
| Geometry | Smoothing | `mesh_smooth_type` | **`FACE`** ("Face") | Evita el warning de smoothing groups en Unity; "Normals Only" (default) también vale porque Unity importa custom split normals |
| Geometry | Apply Modifiers | `use_mesh_modifiers` | ON… **salvo que haya shape keys** | Ver "Qué exporta y qué no" |
| Geometry | Triangulate Faces | `use_triangles` | opcional ON | Triangulación reproducible (si no, triangula Unity) |
| Geometry | Tangent Space | `use_tspace` | OFF | Unity calcula Mikktspace por defecto (coincide con los bakes de Blender); ON solo si el pipeline exige tangentes importadas — y "will only work correctly with tris/quads only meshes" |
| Armature | Add Leaf Bones | `add_leaf_bones` | **OFF** | ON (default) mete huesos `_end` basura en el rig de Unity |
| Armature | Only Deform Bones | `use_armature_deform_only` | ON típico | Fuera huesos de control del rig |
| Bake Animation | All Actions | `bake_anim_use_all_actions` | OFF si no quieres un clip por CADA action del .blend | Evita clips basura en Unity |
| Bake Animation | NLA Strips | `bake_anim_use_nla_strips` | según flujo (cada strip = un take/clip) | — |
| Bake Animation | Simplify | `bake_anim_simplify_factor` | 1.0 (default) | Subirlo degrada curvas |

Guardar esto como preset (icono `+` arriba del panel de export) o fijarlo en un Collection Exporter para no repetirlo.

### Animación hacia Unity: clips y la convención `@`

- Cada action/take del FBX llega a Unity como un clip (o se parte en clips desde el Animation tab del importador). Control desde Blender: `bake_anim_use_all_actions` (todas las actions del .blend) vs action activa, y `bake_anim_use_nla_strips` (un take por strip NLA).
- Alternativa limpia y documentada por Unity: **un FBX de modelo + un FBX por animación** con la convención `modelo@anim.fbx` (`goober@idle.fbx`, `goober@walk.fbx`…). "Unity automatically imports all four files and collects all animations to the file without the @ sign in". Los archivos `@` solo necesitan armature + animación (malla fuera = archivos mínimos); mismo esqueleto y mismos nombres de huesos, obligatorio.
- Patrón headless para generarlos: iterar actions, asignar cada una como activa en el armature y exportar con `use_selection=True`, `object_types={'ARMATURE'}`, `bake_anim_use_all_actions=False`, filepath `Modelo@{action.name}.fbx`.
- Same-file o multi-file, el esqueleto no se toca después del primer import: cambiar jerarquía de huesos = reconfigurar Avatar/retarget en Unity.

## Escala: la mecánica real del 100× (verificada)

Blender trabaja en metros; el FBX declara sus unidades con `UnitScaleFactor` (relativo a cm). Verificado exportando desde Blender 5.2.0 y leyendo el binario:

| Apply Scalings | UnitScaleFactor en el FBX | En Unity (Model tab) |
|---|---|---|
| "All Local" (`FBX_SCALE_NONE`, **default**) | 1.0 (= cm) | File Scale **0.01** y escala **100** metida en los transforms → el clásico (100,100,100) |
| **"FBX Units Scale"** (`FBX_SCALE_UNITS`) | 100.0 (= m) | File Scale **1**, transforms limpios (1,1,1) |

Por eso la receta es: escena en metros, `Ctrl+A ‣ All Transforms` antes de exportar, Scale=1.0 + Apply Scalings=FBX Units Scale. En Unity, Scale Factor 1 y Convert Units activo (defaults) quedan bien.

## Rotación: el -89.98 y sus remedios

Blender es Z-up; Unity es Y-up. Con **Use Space Transform** activo (default), el exportador mete la conversión de ejes como una rotación de **-90° en X en los objetos raíz**; Unity la muestra como **-89.98°** por redondeo de float. No es un bug de datos — el modelo se ve bien — pero ensucia el prefab. Remedios, de más a menos recomendado:

1. **Aceptarlo** en assets animados/rigged: es cosmético y es lo único 100% seguro con armatures.
2. **Unity: Bake Axis Conversion** (Model tab, Unity 6): hornea la conversión de ejes en los datos del asset — transform limpio sin tocar Blender.
3. **El truco del contra-giro** (props estáticos): rotar el objeto **-90° en X → `Ctrl+A ‣ Rotation` → rotar +90° en X y NO aplicar**. El export cancela la rotación y Unity muestra 0,0,0.
4. **Apply Transform** (`bake_space_transform`) en el export: funciona para mallas estáticas sueltas, pero es experimental y **rompe armatures/animaciones** (warning oficial). Nunca en characters.

**Antes de cualquier export:** `Object ‣ Apply ‣ All Transforms` (`Ctrl+A`) con los objetos seleccionados. Escala ≠ 1 sin aplicar = normales, físicas y bakes mal en Unity. Excepción: no aplicar transforms a huesos/armature en pose — aplicar en Object Mode sobre el rest.

## Qué exporta el FBX y qué NO (Blender 5.2, verificado)

| Cosa | ¿Viaja al FBX? | Detalle |
|---|---|---|
| Modificadores | ✅ con Apply Modifiers | Se exporta la malla evaluada (mirror, bevel, subsurf… aplicados) [ver: modificadores] |
| Shape keys (blendshapes) | ✅ | Verificado: escribe deformers `BlendShape`/`BlendShapeChannel`. El manual dice lo contrario — texto viejo |
| Shape keys + Apply Modifiers | ❌ **se pierden en silencio** | Verificado: cubo con shape key + Subsurf → malla evaluada OK, 0 shape keys. En characters con blendshapes: aplicar modificadores A MANO antes y exportar con Apply Modifiers OFF |
| Instancias de Geometry Nodes | ❌ **malla vacía (0 verts)** | Verificado. Meter **Realize Instances** al final del node tree (o aplicar el modificador) antes de exportar [ver: geometry-nodes] |
| Linked duplicates (Alt+D) | Se des-instancian | "exported objects do not share data" — cada copia escribe su malla |
| Materiales | Solo nombre + asignación por slot | El shader real NO viaja fiable. Contrato: nombres de material limpios y estables; el material de verdad se construye en Unity [ver: pipeline/arte-a-unity] |
| Texturas | Solo con Path Mode=Copy + Embed Textures | Para el pipeline normal (material en Unity) déjalo en Auto y sin embed |
| Constraints | Solo el resultado bakeado como keyframes | El constraint en sí no existe en FBX |
| Vertex colors | ✅ (`colors_type`, sRGB default) | — |
| Custom split normals | ✅ siempre (`LayerElementNormal`) | Por eso "Normals Only" basta si Unity está en Normals=Import |

## Naming y jerarquía pensados para el prefab

- **Un asset = un root** con nombre limpio y estable (`Crate_Wood`, no `Cube.003`). El nombre del objeto/malla es el contrato con Unity: los sub-assets del modelo se enlazan **por nombre**.
- **Pivot = origen del objeto.** Props: origen en la base (contacto con el suelo). Puertas/palancas: origen en la bisagra. `Object ‣ Set Origin` antes de exportar; en Unity el pivot no se edita.
- **Sockets:** Empties (Plain Axes) como hijos del mesh/rig → llegan a Unity como GameObjects vacíos con su transform, listos como attach points (mano, cañón, tubo de escape). Prefijo propio consistente, p.ej. `SOCKET_Hand_R`. Unity no exige prefijo — es convención de equipo.
- **Colliders por nombre:** `UCX_` (convex), `UBX_` (box), `USP_` (sphere), `UCP_` (capsule) + nombre EXACTO del render mesh (`UCX_Crate_Wood`, sufijos `_00`, `_01` para varios) es la convención **de Unreal** (doc oficial de Epic). **Unity NO la soporta de serie**: o se activa Generate Colliders (MeshCollider en todo, caro), o el proyecto Unity lleva un `AssetPostprocessor.OnPostprocessModel(GameObject)` que convierta las mallas `UCX_*` en colliders y borre sus renderers. Desde Blender el trabajo es idéntico: mallas convexas low-poly bien nombradas junto al render mesh [ver: pipeline/arte-a-unity].
- **LODs:** sufijo `_LOD0`, `_LOD1`, … `_LOD7` en cada malla → Unity crea el **LODGroup automáticamente** al importar (doc oficial, máx. 8 niveles).
- Jerarquías profundas de Empties "organizativos" ensucian el prefab: aplanar lo que no aporte transforms útiles. Organización del .blend: [ver: organizacion-blend].

## Export batch: varios assets desde un .blend

**Camino moderno (4.2+): Collection Exporters.** `Properties ‣ Collection ‣ Exporters ‣ Add Exporter` (FBX, glTF, OBJ, USD, PLY, Alembic) — cada colección guarda SU ruta y SUS settings. Re-export: botón **Export All** del panel, o `File ‣ Export All Collections` para todo el .blend de un golpe (`bpy.ops.wm.collection_export_all()`). Es lo que convierte el .blend en fuente de verdad re-exportable en un click.

**Operador FBX en batch:** `batch_mode` del propio `export_scene.fbx` (`'COLLECTION'`, `'SCENE_COLLECTION'`, …) exporta cada colección a un archivo. Menos control fino que los Collection Exporters.

**Headless / MCP** [ver: bpy-scripting] [ver: blender-mcp-operativo] — patrón por colección con el parámetro `collection`:

```python
import bpy, os
OUT = bpy.path.abspath("//export")  # junto al .blend
os.makedirs(OUT, exist_ok=True)
for col in bpy.data.collections:
    if not col.name.startswith("EXP_"):
        continue
    bpy.ops.export_scene.fbx(
        filepath=os.path.join(OUT, col.name[4:] + ".fbx"),
        collection=col.name,
        apply_scale_options='FBX_SCALE_UNITS',
        mesh_smooth_type='FACE',
        add_leaf_bones=False,
        object_types={'EMPTY', 'ARMATURE', 'MESH'},
    )
```

## glTF hacia Unity: cuándo y cómo

Exportador: `File ‣ Export ‣ glTF 2.0 (.glb/.gltf)` — el oficial de Khronos, bundled. Preferir **.glb** (un solo archivo). Settings clave (`export_scene.gltf`):

| Opción UI | Propiedad bpy | Valor para Unity | Nota |
|---|---|---|---|
| Format | `export_format` | glTF Binary (.glb) | Un archivo autocontenido |
| +Y Up | `export_yup` | ON (default) | glTF es Y-up de espec; glTFast resuelve el cambio de handedness |
| Apply Modifiers | `export_apply` | ON (default OFF) | Igual que FBX: aplicar excluye shape keys |
| Tangents | `export_tangents` | OFF (default) | Solo si el consumidor las exige |
| Materials | `export_materials` | `EXPORT` o `PLACEHOLDER` | `PLACEHOLDER` = solo slots/nombres, coherente con "material real en Unity" |
| Geometry Nodes Instances | `export_gn_mesh` | OFF | Marcado **Experimental** en 5.2 — Realize Instances sigue siendo lo fiable |
| Compression | `export_draco_mesh_compression_enable` / meshopt (5.2+) | según pipeline runtime | glTFast soporta Draco/KTX2/meshopt |

- En Unity: instalar `com.unity.cloud.gltfast` (paquete oficial). Import de editor y runtime; **export desde Unity: experimental**. Soporta Built-in/URP/HDRP con sus shaders propios (no mapea a Lit/Standard estándar por defecto).
- Caso de uso real: contenido cargado en runtime, pipelines glTF-first, o validar assets fuera de Unity. Para el prefab clásico de juego, FBX.

## El roundtrip sin romper prefabs en Unity

1. **Sobrescribir SIEMPRE el mismo archivo** en `Assets/` (mismo path). El `.meta` conserva el GUID → todos los prefabs/escenas que referencian el modelo sobreviven. Consejos de foros de "borra y reimporta" destruyen el GUID: si el import parece cacheado, click derecho ‣ **Reimport** en Unity, no borrar.
2. **No renombrar a la ligera** objetos, mallas ni materiales en Blender: Unity re-enlaza los sub-assets del modelo por nombre; renombrar = MeshFilters vacíos y materiales desasignados en prefabs existentes.
3. **No editar el model prefab directamente**: montar un **Prefab Variant** (o prefab normal que anida el modelo) con los componentes del juego. Los overrides sobreviven al re-export.
4. Los ajustes del Model tab (Scale Factor, Bake Axis Conversion, Normals, etc.) viven en el `.meta` — persisten entre re-exports.
5. Mover/renombrar el asset SOLO dentro de Unity (para que el `.meta` viaje), nunca en el Finder/terminal.
6. Con blendshapes: recordar que el importador FBX nativo de Blender 5.x no los reimporta — el roundtrip de vuelta a Blender (si el .blend se perdió) va por el importador Legacy.

## Auto-validación headless del export (sin abrir Unity)

Antes de mandar el FBX al proyecto, un agente puede detectar los fallos gordos reimportándolo en una escena vacía de Blender (importador nativo 5.x) y midiendo:

```python
import bpy
FBX = "/ruta/asset.fbx"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.fbx_import(filepath=FBX)
for ob in bpy.data.objects:
    if ob.type != 'MESH':
        continue
    assert len(ob.data.vertices) > 0, f"{ob.name}: malla vacia (¿instancias GN sin realizar?)"
    dims = ob.dimensions
    assert max(dims) < 100, f"{ob.name}: {tuple(dims)} — ¿escala x100?"
    assert all(abs(s - 1.0) < 1e-4 for s in ob.scale), f"{ob.name}: scale {tuple(ob.scale)} != 1"
    print("OK", ob.name, "verts:", len(ob.data.vertices), "dims(m):", tuple(round(d, 3) for d in dims))
```

Límites del método: no detecta el -89.98 (el importador de Blender deshace la conversión de ejes) ni valida blendshapes (el importador nativo no los lee — usar `import_scene.fbx` Legacy para ese check). La validación definitiva es SIEMPRE en Unity (vía MCP de Unity si está disponible: importar el asset y leer transform/normales/materiales del prefab resultante).

## Checklist de validación post-export (abrir el FBX en Unity)

1. Root del modelo: rotación (0,0,0) — o el -89.98 conocido y aceptado — y escala (1,1,1).
2. Model tab: File Scale = 1 (si sale 0.01, faltó FBX Units Scale).
3. Tamaño real contra un cubo de 1 m o una cápsula (2 m) en escena.
4. Normales: sin caras negras/invertidas bajo luz rasante (en Blender, pre-export: Overlays ‣ Face Orientation todo azul, `Shift+N` recalcular).
5. Un material slot por material esperado, con el nombre correcto (sin `Material.001`).
6. Jerarquía: sockets presentes, sin Empties basura, sin huesos `_end` (si hay: reexportar con Add Leaf Bones OFF).
7. Animaciones: los clips esperados y solo esos; blendshapes en el SkinnedMeshRenderer si el asset los lleva.
8. Mallas `UCX_*`/colliders procesados según el pipeline del proyecto; LODGroup creado si hay `_LODn`.
9. Consola de Unity limpia de warnings del importador.

## Reglas prácticas

1. FBX para el pipeline editor→prefab; glTF solo para runtime loading o pipeline glTF-first.
2. Escena SIEMPRE en metros, unit scale 1.0; modelar a tamaño real.
3. `Ctrl+A ‣ All Transforms` antes de CADA export (salvo el contra-giro deliberado).
4. Scale 1.0 + Apply Scalings = **FBX Units Scale** → File Scale 1 en Unity.
5. Forward -Z, Up Y (defaults); Apply Transform (experimental) JAMÁS con armatures.
6. Object Types: EMPTY + ARMATURE + MESH; nada de cámaras/luces en assets.
7. Smoothing = Face; Tangent Space OFF (Unity calcula Mikktspace).
8. Add Leaf Bones OFF en todo export con rig.
9. Character con blendshapes: aplicar modificadores a mano, exportar con Apply Modifiers OFF.
10. Geometry Nodes: Realize Instances antes de exportar, siempre.
11. Materiales: nombre limpio y estable por slot; el shading real se hace en Unity.
12. Nombres de objeto/malla = contrato con Unity: no renombrar tras el primer import.
13. Pivot donde el juego lo necesita (base/bisagra) — en Unity ya no se mueve.
14. Colliders: mallas convexas `UCX_<NombreExacto>` + postprocessor en Unity; LODs con `_LODn`.
15. Un asset (o familia) por colección con prefijo `EXP_` + Collection Exporter configurado = re-export de un click.
16. Roundtrip: sobrescribir el mismo archivo, Reimport si hace falta, Prefab Variant para componentes.
17. Todo "listo" = FBX abierto en Unity y checklist pasada, no solo "el export no dio error".
18. Ante docs/tutoriales viejos (2.8-4.x): verificar contra el manual 5.2 y las release notes — importador FBX, Collection Exporters y glTF cambiaron [ver: blender5-actualidad].

## Errores comunes

| Pitfall | Síntoma en Unity | Antídoto |
|---|---|---|
| Export con Apply Scalings default ("All Local") | Escala (100,100,100), File Scale 0.01 | `apply_scale_options='FBX_SCALE_UNITS'` |
| Transforms sin aplicar en Blender | Tamaños/rotaciones absurdos, normales raras, mirrors volteados | `Ctrl+A ‣ All Transforms` pre-export |
| Rotación -89.98 en X | Prefab "sucio" (visualmente correcto) | Aceptar, Bake Axis Conversion en Unity, o contra-giro -90/apply/+90 en props |
| Apply Transform con armature | Rig/animación rotos o doblados | Nunca `bake_space_transform` con rigged assets (warning oficial) |
| Shape keys desaparecidos | SkinnedMeshRenderer sin blendshapes | Había Apply Modifiers ON: aplicar modificadores a mano y reexportar sin él |
| GN sin Realize Instances | Malla vacía o solo el mesh base | Realize Instances al final del árbol [ver: geometry-nodes] |
| Add Leaf Bones ON (default) | Huesos `_end` por todo el esqueleto | `add_leaf_bones=False` |
| All Actions ON con .blend lleno de actions | Docena de clips basura por FBX | `bake_anim_use_all_actions=False`, gestionar por NLA |
| "Bola de discoteca" / sombreado facetado | Normales duplicadas o smoothing perdido | Smoothing=Face + normales limpias; en Unity Normals=Import |
| Renombrar mallas/materiales en Blender | Prefabs con Mesh "Missing", materiales sueltos | Congelar nombres tras el primer import; renombrar = migración consciente |
| Borrar el FBX y reimportar "para refrescar" | Todas las referencias rotas (GUID nuevo) | Sobrescribir mismo path; Reimport desde Unity |
| Confiar en el import directo de .blend | Rompe en máquinas sin Blender / CI; acoplado a la versión local | Exportar FBX explícito; .blend fuera de `Assets/` |
| Esperar UCX_ nativo en Unity | Mallas UCX renderizadas como geometría normal | Es convención de Unreal: en Unity, AssetPostprocessor propio o Generate Colliders |
| Tutorial 2.8-3.x como referencia de settings | Opciones que ya no existen o defaults cambiados | Contrastar con manual 5.2 / release notes [ver: blender5-actualidad] |

## Fuentes

- **Manual Blender 5.2 LTS — FBX** (`files/import_export/fbx.html`) — Blender Foundation — importador FBX nativo: features, opciones y límites (sin shape keys).
- **Manual Blender 5.2 LTS — FBX (Legacy)** (`files/import_export/fbx_legacy.html`) — Blender Foundation — referencia completa del exportador FBX actual (opciones Transform/Geometry/Armature/Bake Animation, sección Compatibility; contiene texto desactualizado sobre shape keys).
- **Manual Blender 5.2 LTS — Collections** (`scene_layout/collections/collections.html`) — Blender Foundation — panel Exporters, Export All y `File ‣ Export All Collections`.
- **Manual Blender 5.2 LTS — glTF 2.0** (`addons/scene_gltf2.html`) — Blender Foundation — mapeo Principled BSDF→PBR y opciones del exportador glTF.
- **Release notes 4.2 — Import & Export** — developer.blender.org — introducción de Collection Exporters.
- **Release notes 4.5 — Pipeline & I/O** — developer.blender.org — nuevo importador FBX en C++ (ufbx), rendimiento y cobertura.
- **Release notes 5.0 / 5.1 / 5.2 — Pipeline & I/O** — developer.blender.org — importador nativo como default (5.0), export de normales de shape keys (5.1), meshopt en glTF (5.2).
- **Blender 5.2.0 LTS local (binario + fuente `io_scene_fbx` en `addons_core`)** — verificación empírica: dump RNA de `export_scene.fbx`/`export_scene.gltf` (nombres, defaults, enums), `UnitScaleFactor` 1.0 vs 100.0 en el binario FBX, shape keys sí/no según Apply Modifiers, instancias GN perdidas sin Realize.
- **Unity Manual (Unity 6.5) — Model tab import settings** — Unity Technologies — Scale Factor, Convert Units, Bake Axis Conversion, Tangents (Calculate Mikktspace default).
- **Unity Manual — 3D formats** — Unity Technologies — FBX como cadena interna de import; .blend requiere Blender instalado y se convierte a FBX; aviso contra formatos propietarios en producción.
- **Unity Manual — Configure mesh LODs** (`lod-group-configure.html`) — Unity Technologies — convención `_LODn` y LODGroup automático.
- **Unity Scripting API — `AssetPostprocessor.OnPostprocessModel`** — Unity Technologies — hook para colliders por convención de nombre.
- **glTFast (`com.unity.cloud.gltfast` v6.19)** — docs oficiales del paquete Unity — import editor/runtime, export experimental, soporte de render pipelines.
- **glTF-Blender-IO** — github.com/KhronosGroup — el exportador glTF bundled es el oficial de Khronos; soporte 4.5/5.0/5.1/5.2.
- **Unity Manual — Import animations using multiple model files** (`Splittinganimations.html`) — Unity Technologies — convención `modelo@anim.fbx` vigente.
- **"Blender to Unity: Correct Scale and Rotation"** — Immersive Limit — el -89.98/escala 100 por defecto, receta FBX Units Scale y contra-giro.
- **FBX Static Mesh Pipeline** — Epic Games (dev.epicgames.com) — definición original de `UCX_`/`UBX_`/`USP_`/`UCP_` y su regla de naming.
