# Organización y versionado de assets 3D (Blender → Unity, end-to-end)

> **Cuando cargar este archivo:** al montar la estructura de carpetas de un proyecto de arte 3D que va a Unity, al decidir dónde viven los `.blend`/`.psd`/high-poly frente a los FBX/texturas exportados, al fijar el naming que sobrevive el cruce Blender→FBX→Unity, al configurar git+LFS para binarios, al necesitar trazar un prefab de vuelta a su `.blend` fuente, al armar una biblioteca de assets reutilizables entre proyectos, o al versionar/coordinar quién toca qué binario. Esta es la fase que **une** todo el bloque de arte 3D con Unity: aquí va el FLUJO COMPLETO y el puente definitivo; el detalle de cada eslabón vive en las bases hermanas y se enruta con `[ver: ...]`.

Stack objetivo: **Blender 5.2 LTS** + **Unity 6 (6000.x)**. Datos dependientes de versión, explícitos. Verificado contra docs.unity3d.com (Model file formats, LOD Group, AssetPostprocessor, AssetImporter, AssetDatabase) y git-lfs (lock/track). Lo no verificado va marcado.

---

## 1. El mapa: dos árboles, una cadena

Un asset 3D vive en **dos representaciones** que NO son la misma cosa y no se versionan igual:

| | **SOURCE (editable)** | **EXPORTED (consumible)** |
|---|---|---|
| Qué es | `.blend`, `.psd`/`.kra`, high-poly, sculpt, `.spp` (Substance), blueprints | FBX/glTF, texturas PNG/TGA/EXR, material extraído, prefab |
| Dónde | Fuera de `Assets/` (árbol `sources/` o carpeta ignorada) | Dentro de `Assets/` de Unity |
| Herramienta que lo abre | Blender / Photoshop / Substance | Unity (el importer lo procesa) |
| Tamaño | Grande, engorda al iterar | Optimizado para el motor |
| Cambia | Cada sesión de arte | Solo al re-exportar |
| Verdad sobre... | la INTENCIÓN del asset | lo que el jugador ve |

La regla de oro del pipeline: **el source es la fuente de verdad; el exported es un derivado reproducible**. Si se pierde un FBX, se re-exporta del `.blend`. Si se pierde el `.blend`, el asset MURIÓ — no se edita un FBX, se rehace. Por eso el `.blend` se versiona con más cuidado que el FBX.

Cadena canónica (detalle de cada flecha en las bases):

```
.blend (modelado)  ─┐
high-poly ──► bake ─┼─► texturas (PSD→PNG)  ─┐
rig + anim ─────────┘                        ├─► FBX/glTF ─► Unity import ─► Material + Prefab ─► escena
   [ver: modelado/high-to-low, texturizado/baking, rigging/rig-a-unity]   [ver: blender/import-export]  [ver: pipeline/arte-a-unity]
```

## 2. Topología de carpetas end-to-end

Un solo repo del juego, dos zonas. `sources/` es hermana de `Assets/`, **no hija** — Unity solo importa `Assets/` y `Packages/`, así que todo `.blend` fuera de ahí es invisible al importer y no dispara reimports.

```
mi-juego/                          ← raíz del repo (Unity project)
├── Assets/
│   └── _Game/
│       ├── Art/
│       │   ├── Models/            ← FBX exportados (SHIP)
│       │   │   ├── Props/
│       │   │   │   └── crate_wood.fbx  (+ crate_wood.fbx.meta)
│       │   │   └── Characters/
│       │   ├── Textures/          ← PNG/TGA/EXR exportados
│       │   ├── Materials/         ← materiales extraídos (.mat)
│       │   └── Prefabs/           ← el prefab que usa la escena
│       └── Scenes/
├── Packages/                      ← manifest.json + biblioteca UPM local (§7)
├── ProjectSettings/
├── Library/                       ← GENERADO, gitignored [ver: unity/assets-pipeline-git]
└── sources/                       ← FUERA de Assets/: fuente de verdad, LFS
    ├── blender/
    │   ├── prop-crate_wood.blend
    │   └── char-goblin.blend
    ├── highpoly/crate_wood_high.blend
    ├── textures/crate_wood.psd
    └── _library/                  ← .blend biblioteca (kits, materiales, rigs base) [ver: blender/organizacion-blend §6]
```

**`.blend` dentro de `Assets/` vs fuera** — decisión de arquitectura, no de gusto:

| | `.blend` DENTRO de `Assets/` | `.blend` en `sources/` (FUERA) — **recomendado** |
|---|---|---|
| Cómo llega a Unity | Auto-import: Unity lo convierte a FBX al vuelo | Export manual/Collection Exporter → FBX en `Assets/` |
| Requisito | **Blender instalado en CADA máquina y en CI** (proprietary format) | Nadie más que el artista necesita Blender |
| Determinismo | El FBX interno cambia con la versión de Blender de cada quien | El FBX es un artefacto fijo, idéntico para todos |
| Qué se importa | TODO el `.blend` (incluidas colecciones `-high`/`-wip`/`-ref` si no se aíslan) | Solo la colección `-final` que exportaste |
| Reimport | Pesado, se dispara al tocar el `.blend` | Barato, controlas cuándo |
| Paso manual | Cero (pro) | Un export (mitigado por Collection Exporters `Export All`) |

> Unity: los archivos `.ma/.mb/.max/.c4d/.blend` **"fail to import unless you have the corresponding 3D modeling software installed"**, y Unity los **convierte a `.fbx` internamente**. Recomendación textual del manual: *"Don't use proprietary file formats in production and export to the `.fbx` format wherever possible."* → **exportar FBX es lo correcto para producción**; `.blend` en `Assets/` solo para prototipo rápido de un dev que ya tiene Blender.

**Truco híbrido:** si quieres el `.blend` fuente *adyacente* al FBX pero sin que Unity lo importe, mételo en una carpeta terminada en `~` dentro de `Assets/` (p. ej. `Assets/_Game/Art/Models/Props/Source~/crate_wood.blend`). Unity ignora carpetas cuyo nombre termina en `~` o empieza con `.` (comportamiento del importer de hidden assets) — el `.blend` viaja junto al FBX y no genera `.meta` ni reimport. *NO RE-VERIFICADO esta sesión contra el manual 6.x; comportamiento histórico estable de Unity.*

## 3. Naming cross-tool: el nombre que sobrevive el pipeline

El mismo asset se llama IGUAL en Blender, en el FBX y en Unity. Un nombre que se rompe en un eslabón rompe el remapeo al iterar. Lo que cruza:

| En Blender | Viaja por el FBX como | Unity lo materializa como |
|---|---|---|
| **Object name** (`GEO-crate_wood`) | node name | `GameObject` en la jerarquía del prefab importado |
| **Mesh / object data name** | mesh name | **Mesh sub-asset** del modelo (lo que referencia el `MeshFilter`) |
| **Material name** (`M_crate_wood`) | material name | Material remapeado **por nombre** al extraer/asignar |
| Parenting / empties | node hierarchy | Transform hierarchy |
| Sufijo **`_LOD0` … `_LOD7`** | mesh node names | **`LODGroup` auto-generado** (§4) |

Consecuencias operativas:

- **El objeto y su malla tienen nombres independientes en Blender** [ver: blender/organizacion-blend §2]: Unity muestra AMBOS (el objeto → jerarquía; la malla → asset de mesh). Nombrar la malla igual que el objeto evita un `crate_wood` con malla `Cube.003` colgando.
- **Remapeo de materiales por nombre**: el Model Importer de Unity mapea el material del FBX a un `.mat` del proyecto buscándolo **por nombre** (Material Creation/Search en el importer). Si el material del `.blend` se llama `Material.001`, cada re-export puede crear un material nuevo o romper el link. Por eso el naming sucio (`.001`, `Cube`, `Material.003`) explota justo aquí — es el mismo aviso de la base de Blender, ahora con su consecuencia en Unity [ver: blender/organizacion-blend §2].
- **Convención única extremo a extremo** (destilada de las dos bases): `snake_case` para el asset (`crate_wood`), prefijos de propósito en Blender (`GEO-/RIG-/HLP-`) [ver: blender/organizacion-blend §2], prefijos de tipo en Unity (`SM_` static mesh, `SK_` skeletal, `M_` material, `T_` textura, `P_`/prefab) [ver: unity/assets-pipeline-git §4]. El **namespace del asset** (`crate_wood`) aparece en TODOS: `.blend`, objeto, malla, material, FBX, textura, `.mat`, prefab. Un solo `grep crate_wood` encuentra la cadena completa.
- Nombre de ARCHIVO del `.blend`: `prop-crate_wood.blend` (no-caps-no-gaps, prefijo de categoría). Nombre del FBX: `crate_wood.fbx` (sin el prefijo de categoría — la carpeta ya lo dice). Mantener el core `crate_wood` idéntico.

## 4. El puente técnico: qué cruza el FBX/glTF y qué no

El detalle de opciones de export (ejes, Apply Transform, Path Mode, Draco, glTF vs FBX) vive en **[ver: blender/import-export]**; el detalle de import settings (Scale Factor, Mesh Compression, Normals/Tangents, Extract Materials) en **[ver: unity/assets-pipeline-git §1]**. Aquí solo el puente y sus trampas:

| Cruza el FBX/glTF | Regla de puente |
|---|---|
| **Escala / unidades** | 1 unidad Blender (metro) = 1 unidad Unity. Se resuelve en export/import, **NUNCA** escalando el `Transform` de Unity ni el scale del objeto en Blender: **aplicar transform** (`Ctrl-A`) en Blender antes de exportar; ajustar `Scale Factor`/`Convert Units` en el importer si algo baila [ver: unity/assets-pipeline-git §1]. El clásico factor 0.01/100× es el eje/unidad del FBX mal resuelto |
| **Ejes** | Blender (+Z up, −Y forward) ≠ Unity (+Y up, +Z forward). El export/import lo convierte; verificar que el asset importa "de pie" y mirando +Z, no acostado |
| **Malla** | Aplicar modificadores destructivos o dejar que el export los aplique; triangulación la hace el motor/exporter. Presupuesto de polys se decide antes [ver: modelado/presupuestos-poligonos] |
| **LODs** | Nombrar las mallas `nombre_LOD0..._LOD7` → **Unity crea el `LODGroup` automáticamente** al importar (máx. 8 niveles; LOD0 = más detalle). Sin necesidad de configurar el componente a mano |
| **Materiales** | Extraer una vez en Unity (`Extract Materials`) y desligar del FBX; editar el `.mat`, no el material embebido [ver: unity/assets-pipeline-git §1] |
| **Texturas** | NO embeber en el FBX: exportarlas aparte a `Assets/.../Textures/` y dejar que el material las referencie [ver: texturizado/texturas-a-unity] |
| **Colliders** | No cruzan bien: se ponen en Unity (primitivos en dinámicos; `Generate Colliders` solo en entorno estático) |
| **Rig / animación** | El armature y las clips cruzan; Avatar y retargeting se configuran en Unity [ver: rigging/rig-a-unity, unity/animacion-unity] |

**glTF vs FBX para Unity:** FBX es el estándar interno de Unity y lo que el importer entiende nativamente; glTF necesita un paquete importador. Para el pipeline a Unity, **FBX por defecto**; glTF cuando el destino es web/USD o cuando quieres instancing/PBR estándar. Ambos salen del mismo `.blend` vía Collection Exporter [ver: blender/import-export].

Sanity-check del contenido a exportar por bpy, ANTES de sacar el FBX (poly count real + tamaño en metros; una intención por llamada si vas por MCP [ver: blender/blender-mcp-operativo]):

```python
import bpy
dg = bpy.context.evaluated_depsgraph_get()
tris = 0
for o in bpy.data.collections["crate_wood-final"].all_objects:
    if o.type != 'MESH':
        continue
    me = o.evaluated_get(dg).to_mesh()                 # post-modificadores
    tris += sum(len(p.vertices) - 2 for p in me.polygons)  # ≈ triángulos (fan)
    print(o.name, "dims_m", tuple(round(d, 3) for d in o.dimensions))
    o.evaluated_get(dg).to_mesh_clear()
print("export_tris", tris)                             # evidencia antes de exportar
```

## 5. Git para binarios: un solo repo, dos regímenes

Todo el racional de `.gitignore` de Unity, `.meta`/GUID, LFS de YAML vs binario y merge de escenas vive en **[ver: unity/assets-pipeline-git §5]**; el racional del `.blend` binario en **[ver: blender/organizacion-blend §7]**. Consolidado para el pipeline unido:

- **`Library/` jamás al repo** (se regenera del import). `sources/`, `Assets/`, `ProjectSettings/`, `Packages/*.json` SÍ.
- **Un `.meta` por asset, en el mismo commit que el asset.** El FBX y su `.meta` viajan juntos — el `.meta` guarda el GUID y TODOS los import settings (Scale, LODGroup, materiales, `userData` de §6). Perder el `.meta` = re-importar con GUID nuevo = referencias rotas en cascada.
- **Git LFS para TODO binario grande**, en el commit 0 (`git lfs install` una vez por máquina; un binario commiteado sin LFS queda en la historia para siempre). `.gitattributes` unificado, cubre AMBOS árboles:

```gitattributes
# Sources (fuera de Assets/) y exports (dentro) — mismo LFS
*.blend  filter=lfs diff=lfs merge=lfs -text
*.fbx    filter=lfs diff=lfs merge=lfs -text
*.psd    filter=lfs diff=lfs merge=lfs -text
*.exr    filter=lfs diff=lfs merge=lfs -text
*.png    filter=lfs diff=lfs merge=lfs -text
*.tga    filter=lfs diff=lfs merge=lfs -text
*.wav    filter=lfs diff=lfs merge=lfs -text
*.ogg    filter=lfs diff=lfs merge=lfs -text

# YAML de Unity: TEXTO, no LFS, merge inteligente [ver: unity/assets-pipeline-git §5]
*.unity  merge=unityyamlmerge eol=lf
*.prefab merge=unityyamlmerge eol=lf
*.asset  merge=unityyamlmerge eol=lf
*.meta   eol=lf
```

- **`.gitignore`** añade, además del canónico de Unity, los backups de Blender que NO son fuente: `*.blend1`, `*.blend2`, `*_autosave.blend` [ver: blender/organizacion-blend §7].
- **Un solo repo** (sources + Unity) es lo correcto para dev solo o equipo chico: trazabilidad trivial (rutas paralelas), un solo historial, un solo `git lfs`. Separar en dos repos (art-source vs game) solo si el árbol de sources pesa cientos de GB o lo tocan personas que no tocan Unity.

## 6. Trazabilidad: del prefab de vuelta al `.blend`

El `.blend` NO está en `Assets/`, así que Unity no conoce el link — hay que documentarlo. Tres mecanismos, de más barato a más robusto:

1. **Naming espejo (gratis):** `Assets/_Game/Art/Models/Props/crate_wood.fbx` ↔ `sources/blender/prop-crate_wood.blend`. Mismo core `crate_wood`; un `grep -r crate_wood sources/` encuentra la fuente. Suficiente para dev solo si la convención se respeta al 100%.
2. **Sidecar en el `.meta` vía `AssetImporter.userData`** (string libre que persiste en el `.meta`, verificado en docs): grabar la ruta del source al importar. Sobrevive renombres del FBX y queda versionado con el asset.
3. **Manifest del proyecto** (`sources/ASSET_MAP.md` o un `.json`): tabla `asset → .blend → responsable → última exportación`. Para equipos y para auditar qué falta re-exportar.

Postprocessor que estampa el source en el `.meta` (verificado: `OnPostprocessModel`, `assetImporter`, `assetPath`, `userData`):

```csharp
// Editor/StampSource.cs — graba la ruta del .blend fuente en el .meta del FBX
public class StampSource : UnityEditor.AssetPostprocessor
{
    void OnPostprocessModel(UnityEngine.GameObject root)
    {
        if (!assetPath.StartsWith("Assets/_Game/Art/Models/")) return;
        if (!string.IsNullOrEmpty(assetImporter.userData)) return; // no pisar
        string name = System.IO.Path.GetFileNameWithoutExtension(assetPath);
        assetImporter.userData = "{\"source\":\"sources/blender/prop-" + name + ".blend\"}";
    }
}
```

Para leer el path del asset seleccionado en Editor: `AssetDatabase.GetAssetPath(obj)` devuelve la ruta relativa al proyecto (verificado). El GUID que enlaza todo (prefab→FBX→material→textura) es el del `.meta` [ver: unity/assets-pipeline-git §5].

## 7. Biblioteca de assets reutilizables entre proyectos

Dos bibliotecas paralelas, una por lado del puente:

| Lado | Qué reusar | Mecanismo | Detalle |
|---|---|---|---|
| **Blender (source)** | Kits modulares, materiales, node groups, rigs base, poses | **Asset Browser** + carpeta registrada en `File Paths ‣ Asset Libraries` | `[ver: blender/organizacion-blend §6]` — `Mark as Asset`, catálogos, `blender_assets.cats.txt` |
| **Unity (exported)** | Prefabs, materiales, shaders, scripts de un kit | **Paquete UPM local/git** (`Packages/com.studio.kit/`) o `.unitypackage` | Referenciado desde `Packages/manifest.json`; reusable entre proyectos sin copiar |

- **Kits modulares** (paredes, pisos, props de set): el `.blend` biblioteca vive en `sources/_library/`; se exporta el kit completo a un paquete UPM que varios juegos importan [ver: pipeline-3d/receta-kit-modular]. Un solo grid/snap y un solo naming para que las piezas encajen [ver: modelado/entornos-modulares].
- **Materiales base y rigs base**: un `.blend` de materiales marcados como asset + un `.blend` de rig base (armature genérico) que cada personaje appenda/linkea [ver: rigging/esqueletos-armature].
- **NO ligar proyectos por copia manual**: la reutilización es por PAQUETE (UPM/biblioteca registrada), no arrastrando archivos de un repo a otro — así una mejora del kit se propaga por versión del paquete, no por copiar-pegar que diverge.

## 8. Versionado de UN asset a lo largo de su vida

Working files SIN versión en el nombre (git/LFS lleva la historia); versión explícita `_v001` SOLO en releases/entregas [convención Blender Studio, ver: blender/organizacion-blend §7].

| Momento | Source (`.blend`) | Exported (Unity) |
|---|---|---|
| Iteración de arte | `git commit` del `.blend`; `.blend1` es el backup local del último save | — (no se re-exporta cada save) |
| Antes de cirugía (boolean masivo, apply de stack) | `Ctrl-S` + `Ctrl-Alt-S` (Save Incremental) [ver: blender/organizacion-blend §7-8] | — |
| Hito estable | commit etiquetado; opcional export `_v001` para review | re-export FBX → commit del FBX + `.meta` |
| Entrega a review externo | export a `sources/renders/asset_v001.fbx` | prefab del hito |

- **Nunca editar el FBX para "arreglar rápido"** — se edita el `.blend` y se re-exporta. El FBX es derivado; un fix directo se pierde al siguiente export y rompe la trazabilidad.
- **Recuperación** (`.blend1`, autosave, `quit.blend`) y sus límites (autosave se aplaza durante operadores modales): [ver: blender/organizacion-blend §8]. El `.blend` es lo irremplazable; el FBX se regenera.
- **LFS no des-engorda historia pasada**: activar LFS desde el primer commit. Si ya se commiteó binario sin LFS, `git lfs migrate import` reescribe historia (destructivo, coordinar).

## 9. Colaboración: no pisar binarios

Los binarios NO mergean: dos personas editando el mismo `.blend`, `.psd` o `.unity` = uno pierde su trabajo, sin resolución posible. Por eso arte usa **locking**, no merge.

- **File locking con LFS** (verificado): `git lfs track --lockable "*.blend" "*.psd" "*.fbx"` marca esos patrones como *lockable* → quedan **read-only en el working copy hasta que los bloquees**. Flujo:
  - `git lfs lock sources/blender/char-goblin.blend` — lo reclama en el servidor; a los demás les queda read-only y el push que lo modifique se rechaza.
  - editar → commit → push → `git lfs unlock sources/blender/char-goblin.blend`.
  - `git lfs locks` lista quién tiene qué bloqueado. `--not-lockable` revierte el patrón.
  - Requiere un servidor LFS que soporte locking (GitHub sí).
- **Ownership por convención** cuando no hay locking: un dueño por asset/escena a la vez; branches cortas; integrar a diario [ver: unity/assets-pipeline-git §6].
- **Escenas**: el trabajo se hace en PREFABS (Prefab Mode), no en la `.unity`, para que dos personas "en la misma escena" no colisionen [ver: unity/assets-pipeline-git §6].
- **Multi-instancia / multi-máquina** (varias sesiones del agente sobre la misma infra): antes de tocar un binario, `git lfs locks` o verificar que nadie más lo está iterando; nunca dos exports del mismo FBX en paralelo.

## 10. Aprender de un asset existente (ingeniería inversa de organización)

Metodología para replicar cómo está montado un asset/kit de referencia (asset store, sample project) y absorber su pipeline — el detalle vive en **[ver: aprender-de-assets]**; aquí el gancho:

- **Mesh/LOD**: abrir el FBX en Unity, leer el `LODGroup` (nº de niveles, % de transición) y los `_LODn`; medir poly count por LOD [ver: modelado/presupuestos-poligonos].
- **Texturas/materiales**: qué maps trae, resolución, cuántos materiales por asset, si comparte atlas [ver: texturizado/atlas-trim-optimizacion].
- **Naming**: qué convención de nombres sobrevivió en mesh/material/prefab — copiar el esquema, no el asset.
- **Organización**: cómo separan source de exported, si traen `.blend` o solo FBX, cómo agrupan por feature.

## Reglas prácticas

1. Source (`.blend`/`.psd`/high-poly) FUERA de `Assets/` (árbol `sources/`); exports (FBX/tex/mat/prefab) DENTRO. Nunca al revés.
2. `.blend` en producción → se EXPORTA FBX; `.blend` dentro de `Assets/` solo prototipo (exige Blender en cada máquina + CI).
3. Un solo namespace por asset (`crate_wood`) presente en `.blend`, objeto, malla, material, FBX, textura, `.mat`, prefab — un `grep` encuentra la cadena.
4. Malla nombrada igual que su objeto; cero `Cube`/`Material.001` en lo que se exporta (rompe el remapeo de materiales por nombre en Unity).
5. Aplicar transform (`Ctrl-A`) en Blender antes de exportar; ajustar escala en el importer, jamás en el `Transform` de Unity ni en el scale del objeto.
6. LODs nombrados `nombre_LOD0..._LOD7` → Unity crea el `LODGroup` solo. LOD0 = más detalle, máx. 8.
7. Extraer materiales del FBX una vez; editar el `.mat`, no el material embebido. Texturas aparte, no embebidas en el FBX.
8. `git lfs install` + `.gitattributes` (LFS para `.blend/.fbx/.psd/.png/.exr/.wav`; YAML de Unity como texto con `unityyamlmerge`) en el commit 0.
9. Asset + su `.meta` en el MISMO commit, siempre; mover/renombrar desde el Editor o con `git mv` de ambos.
10. `.blend1`/`.blend2`/`*_autosave.blend` al `.gitignore`; `Library/` jamás al repo.
11. Trazabilidad prefab→`.blend`: naming espejo + `AssetImporter.userData` con la ruta del source (postprocessor una vez).
12. Reuso entre proyectos por PAQUETE (UPM local/git en Unity, Asset Library en Blender), nunca copiar archivos de un repo a otro.
13. Working files sin `_vNNN`; versión explícita solo en releases/entregas para review.
14. Nunca editar un FBX para un fix rápido — editar el `.blend` y re-exportar; el FBX es derivado.
15. Binarios que varios tocan (`.blend`, `.psd`, `.unity`) → `git lfs track --lockable` + `git lfs lock`/`unlock`; o ownership por convención.
16. Import settings por Preset per-folder o `AssetPostprocessor`, nunca asset por asset [ver: unity/assets-pipeline-git §1].
17. Antes de exportar: sanity-check bpy (poly count + `dimensions` en metros) — que el asset tenga el tamaño real correcto.
18. LFS desde el primer commit; si ya se coló binario sin LFS, `git lfs migrate import` (destructivo, coordinar).

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Poner `.blend` en `Assets/` y que el build de CI falle | Proprietary format exige Blender instalado; exportar FBX y dejar el `.blend` en `sources/` (o carpeta `Source~/`) |
| `.blend` dentro de `Assets/` arrastra `-high`/`-wip`/`-ref` al import | Aislar en Blender (Exclude from View Layer) o —mejor— exportar solo la colección `-final` |
| Material se re-crea/rompe en cada re-export | El material se llamaba `Material.001`: nombrarlo `M_asset` en Blender; Unity remapea por NOMBRE |
| Asset importa a escala 100× o acostado | Eje/unidad del FBX: aplicar transform en Blender, ajustar `Scale Factor`/`Convert Units` en el importer, nunca el Transform |
| Editaste el FBX/mesh en Unity y se perdió al re-exportar | El FBX es derivado; el cambio va en el `.blend`. Todo edit en el source |
| No sabes de qué `.blend` salió un prefab | Naming espejo roto + sin sidecar: usar `userData` + manifest desde el día 1 |
| Repo de git gigante | Binario sin LFS: `git lfs track` en el commit 0; LFS no des-engorda historia ya escrita |
| Dos artistas editaron el mismo `.blend`, uno perdió todo | Binarios no mergean: `git lfs lock` (lockable) u ownership; nunca dos en el mismo binario |
| FBX sin su `.meta` → LODGroup/materiales/settings reconfigurados en otra máquina | Asset + `.meta` juntos; el `.meta` guarda GUID + import settings [ver: unity/assets-pipeline-git §5] |
| Kit reusado copiando archivos entre repos y luego divergen | Reuso por paquete UPM/Asset Library, no copiar-pegar |
| LODs no generan `LODGroup` | El sufijo debe ser exacto `_LOD0.._LOD7` en el NOMBRE de la mesh; revisar naming en Blender |
| Perdiste el `.blend` y solo queda el FBX | El source es irremplazable: versionarlo con más cuidado que el FBX, `.blend1` + commits frecuentes |

## Fuentes

- **Unity Manual 6 — Model file formats / Importing models** (`docs.unity3d.com/Manual`, `3D-formats.html`, `models.html`) — Unity — proprietary `.blend/.ma/.mb/.max/.c4d` "fail to import unless you have the corresponding 3D modeling software installed", conversión interna a FBX, recomendación textual de exportar a `.fbx` en producción; modelos creados en app externa contienen meshes/materials/textures.
- **Unity Manual 6 — LOD Group / configure LOD** (`lod-group-configure.html`) — Unity — sufijo `_LODX`, Unity crea el `LODGroup` automáticamente al importar el FBX con ese naming, máx. 8 niveles, LOD0 = más detalle.
- **Unity Scripting API 6 — AssetPostprocessor** (`ScriptReference/AssetPostprocessor.html`) — Unity — firmas verificadas: `OnPreprocessModel()`, `OnPostprocessModel(GameObject)`, `OnPostprocessMeshHierarchy(GameObject)`, `OnAssignMaterialModel(Material, Renderer)`, `OnPreprocessMaterialDescription(...)`.
- **Unity Scripting API 6 — AssetImporter.userData** (`ScriptReference/AssetImporter-userData.html`) — Unity — `public string userData`, dato de usuario libre que persiste con los import settings del asset (en el `.meta`).
- **Unity Scripting API 6 — AssetDatabase.GetAssetPath** (`ScriptReference/AssetDatabase.GetAssetPath.html`) — Unity — devuelve la ruta relativa al proyecto donde está el asset; string vacío si no existe.
- **git-lfs — `git lfs lock` man** (`git-lfs/git-lfs` docs/man) — Git LFS — `git lfs lock <path>` reclama el path contra el servidor y bloquea que otros lo modifiquen; `unlock`, `locks`, `locksverify`.
- **git-lfs — `git lfs track` man** (`git-lfs/git-lfs` docs/man) — Git LFS — `git lfs track --lockable "*.psd"` marca patrones como lockable → read-only en el working copy hasta bloquearlos; `--not-lockable` revierte.
- **BASE sintetizada — `blender/organizacion-blend`** — colecciones `-final/-high/-ref/-wip`, naming de data-blocks (objeto≠malla, prefijos GEO/RIG/HLP, `.001` sucio), purge, Asset Browser/catálogos, `.blend` binario + LFS + `.blend1`, Save Incremental, recuperación/autosave.
- **BASE sintetizada — `unity/assets-pipeline-git`** — import settings FBX (Scale Factor, Extract Materials, Optimize Mesh), `.meta`/GUID, `.gitignore` de Unity, LFS de YAML vs binario, `unityyamlmerge`, estructura `_Game/` por feature, prefab como unidad de trabajo, ownership de escena.

*NO VERIFICADO esta sesión (search budget agotado; enrutado a bases): opciones exactas del exportador FBX/glTF de Blender 5.2 (ejes, Apply Transform, Path Mode, Draco) — viven en `[ver: blender/import-export]`; nombres exactos `AssetDatabase.AssetPathToGUID/GUIDToAssetPath` (existen en la API pero no re-confirmados aquí); el comportamiento de carpeta `Source~/` ignorada por el importer (histórico estable, no re-confirmado contra el manual 6.x).*
