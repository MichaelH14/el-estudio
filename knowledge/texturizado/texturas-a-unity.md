# Del texturizado a Unity: import y material

> **Cuando cargar este archivo:** cuando ya tienes los mapas PBR horneados/pintados y toca meterlos a Unity 6/URP — decidir sRGB por mapa, arreglar el normal verde, empaquetar smoothness, montar el material Lit y verificarlo bajo shader y luz reales. Es el último tramo del pipeline de textura: viene después de [ver: baking] y [ver: texturizado-blender]/[ver: substance-y-alternativas], y aterriza en la spec de [ver: pipeline/arte-a-unity §7]. La teoría de canales PBR está en [ver: pbr-teoria]; el detalle de compresión/plataforma en [ver: unity/rendimiento-unity].

Este archivo NO repite la teoría PBR ni cómo se hornea/pinta un mapa — asume que ya tienes el set de mapas en disco. El valor está en los **settings exactos de import** y en el **material URP** para que el asset se vea en el juego igual que en el DCC. Un "render bonito de Blender/Painter" no cuenta como aprobado [ver: pipeline/arte-a-unity §10].

## 1. El handoff: qué mapas salen y qué espera URP Lit

Set típico de un asset PBR metallic para el shader **URP Lit** (workflow Metallic, el default). Canales exactos verificados contra el manual del Lit Shader:

| Mapa que entregas | Va al slot URP Lit | Canal(es) | Color space | Obligatorio |
|---|---|---|---|---|
| Albedo / Base Color | **Base Map** | RGB (A = transparencia solo si Surface Type = Transparent / Alpha Clipping) | **sRGB** | Sí |
| Metallic (+ Smoothness en A) | **Metallic Map** | RGB = metallic (grayscale); **A = smoothness** | **Lineal** | Sí (o valor constante) |
| Normal (tangent, OpenGL/Y+) | **Normal Map** | RGB = XYZ | Especial (tipo Normal) | Casi siempre |
| Height / Parallax | **Height Map** | Grayscale | **Lineal** | Opcional (parallax) |
| Ambient Occlusion | **Occlusion Map** | Grayscale | **Lineal** | Opcional |
| Emission | **Emission Map** | RGB (admite HDR >1 → alimenta Bloom) | **sRGB** | Solo si emite |

- URP Lit **no usa un "mask map" empaquetado** al estilo HDRP: Metallic, Occlusion y Height son slots separados. El único empaquetado que hace directo es **smoothness en el alpha del Metallic Map** (o del Base Map). Ver §4.
- La tabla de canales resumida ya vive en [ver: pipeline/arte-a-unity §7]; aquí está para amarrar el import de §2.
- 1 material por prop como objetivo; el shader más barato que dé el look (Unlit > Baked Lit > Simple Lit > Lit) [ver: unity/rendering-urp]. Estilizado sin PBR: no entregues metallic/roughness que nadie verá [ver: estilizado-texturas].

## 2. Import settings por tipo de mapa

La regla madre: **sRGB ON solo para lo que es COLOR percibido por el ojo** (albedo, emisión). Todo lo demás es **dato numérico lineal** (normal, metallic, roughness, AO, height, masks) → **sRGB OFF**, o Unity le aplica una curva gamma y los valores entran mal (metal lavado, roughness corrida).

| Mapa | Texture Type | sRGB (Color Texture) | Alpha Is Transparency | Compresión (ver nota) |
|---|---|---|---|---|
| Albedo / Base | Default | **ON** | ON solo si el alpha es transparencia real | Alta calidad con alpha |
| Emission | Default | **ON** | Off | Normal |
| **Normal** | **Normal map** | (lo maneja el tipo) | Off | Especializada para normales |
| Metallic (+smoothness A) | Default | **OFF** | Off (el alpha es DATO, no transparencia) | Alta calidad (el alpha guarda smoothness) |
| Roughness suelto | Default | **OFF** | Off | Normal |
| Occlusion (AO) | Default | **OFF** | Off | Normal |
| Height / Displacement | Default | **OFF** | Off | Normal |
| Mask empaquetado (R/G/B/A datos) | Default | **OFF** | Off | Alta calidad |

Ajustes transversales (mismos nombres que expone el `TextureImporter`):

- **`sRGBTexture`** (checkbox "sRGB (Color Texture)"): el switch de arriba. Verificado: "Whether this texture stores data in sRGB (also called gamma) color space."
- **`isReadable`** (Read/Write): **OFF** por defecto — ON duplica la textura en memoria de CPU; solo si un script la lee en runtime [ver: unity/rendimiento-unity].
- **`mipmapEnabled`**: **ON** para texturas 3D (objetos a distancia variable); off para UI/sprites pixel-perfect.
- **`textureCompression`** + formato por plataforma (ASTC móvil, BC7/BC5 desktop): decisión de plataforma, tabla completa en [ver: unity/rendimiento-unity] y [ver: atlas-trim-optimizacion]. Tamaños potencia de 2 (512/1024/2048).
- **`alphaIsTransparency`**: ⚠️ en el Metallic Map el alpha es **smoothness (dato)**, NO transparencia — déjalo **off** o Unity "sangra" color en zonas de smoothness bajo.
- El alpha que guarda smoothness exige una compresión que **preserve el alpha** (DXT5/BC7, no DXT1/BC1 que descarta alpha). Si el smoothness sale "bandeado", es la compresión comiéndose el canal alpha.

## 3. Normal map: OpenGL vs DirectX (el error verde)

**El hecho duro** (manual de Unity, textual): *"Unity uses Y+ normal maps, sometimes known as OpenGL format."* El canal verde (Y) apunta **hacia arriba**. En RGB se guardan X,Y,Z del vector con Z = "up" del vector (no del mundo).

Convención (verificado contra Marmoset Toolbag): dos familias según handedness —

| Convención | Handedness | Canal Verde (Y) | Software/engine típico |
|---|---|---|---|
| **OpenGL** | Right (Y+) | Apunta **arriba** | **Unity**, Maya, Blender (default), Marmoset con tangent OpenGL |
| **DirectX** | Left (Y−) | Apunta **abajo** | Unreal, 3DS Max, Substance Painter (salida por defecto) |

**Cómo lo reconoces:** el normal se ve "invertido" — los bumps se hunden donde deberían resaltar, la luz golpea al revés. No es un bug de la malla ni de la luz: es el verde volteado.

**Los fixes** (elige UNO, no los dos — se cancelan):

1. **Hornear/exportar directo en OpenGL** (preferido — el archivo ya nace correcto):
   - Blender bake: swizzle `normal_g = 'POS_Y'` (default). Ver §7.
   - Substance Painter: en el export, preset/normal con **OpenGL** (voltear el verde ahí), no DirectX. Detalle del export de Painter: [ver: substance-y-alternativas].
   - Marmoset: **Flip Y** off para OpenGL (o "invert the green channel of your normal map in an image editing application").
2. **Voltear en el import de Unity**: en el Normal Map importer, **`Flip Green Channel`** — verificado: *"Inverts the Y channel, helpful when source data uses different conventions than Unity expects."* Úsalo cuando el archivo ya vino en DirectX y no puedes re-exportar.

Regla operativa: **decide OpenGL como estándar del proyecto el día 1** y hornea/exporta todo así; deja `Flip Green Channel` como parche para assets de terceros que llegan en DirectX. Nunca mezcles ambos convenios en el mismo proyecto.

**Otros settings del tipo Normal Map** (verificados): `Create From Grayscale` (solo si conviertes un heightmap a normal — con malla real NO se usa), `Bumpiness` y `Filtering` (Sharp/Smooth) solo aparecen con Create From Grayscale activo. Marcar el tipo como **Normal map** hace que Unity reencode a su compresión de normales (mejor que un RGB genérico) y lo trate como dato lineal — no toques el sRGB a mano.

## 4. Smoothness vs Roughness: dónde y cómo se empaqueta

**URP usa Smoothness, no Roughness. Y `smoothness = 1 − roughness`.** El manual del Lit lo confirma: "0 provides a wide, rough highlight, and 1 provides a small, sharp highlight like glass" (relación inversa a roughness).

Dónde lo lee el shader — propiedad **Smoothness Source**:

| Smoothness Source | Lee smoothness de… | Cuándo |
|---|---|---|
| **Metallic Alpha** (default) | canal **A del Metallic Map** | Lo normal: empaquetas un "MetallicSmoothness" |
| **Albedo Alpha** | canal **A del Base Map** | Si el material no usa metallic map pero sí varía smoothness, o para ahorrar una textura |

**El problema:** Substance Painter, glTF y la mayoría de horneadores exportan **roughness** (mapa suelto, sin invertir). URP quiere **smoothness en un alpha**. Hay que **invertir y empaquetar** en el DCC ANTES de importar.

**Cómo empaquetar el MetallicSmoothness (RGB = metallic, A = 1−roughness):**

- **Substance Painter:** usa un preset de export tipo Unity que ya arma el mapa MetallicSmoothness (metallic en RGB + smoothness invertido en alpha). Es el camino directo — confirma el nombre exacto del preset en tu versión de Painter y que el normal salga OpenGL [ver: substance-y-alternativas].
- **Blender / manual:** hornea metallic y roughness por separado [ver: baking], luego en el compositor o en un editor: metallic → RGB, `1 − roughness` (nodo Invert / Math Subtract) → canal Alpha, y guarda un PNG-32 lineal.
- **Acuérdalo con el artista ANTES de la primera entrega**: "entrégame el MetallicSmoothness ya empaquetado (smoothness = 1−roughness en el alpha), normal OpenGL". Si llega roughness suelto, o lo inviertes tú o el material se ve plástico/lavado [ver: pipeline/arte-a-unity §10].

Pitfall clásico: meter el **roughness tal cual** en el Metallic Alpha → todo lo mate se ve brilloso y viceversa. El síntoma "el metal se ve raro/lavado" casi siempre es roughness donde iba smoothness.

## 5. Configurar el material URP Lit

Pasos (Inspector del material, shader `Universal Render Pipeline/Lit`):

1. **Surface Options** → Workflow Mode = **Metallic** (default). Surface Type = Opaque salvo vidrio/follaje (Transparent o Alpha Clipping). Render Face = Front (Both solo follaje de doble cara).
2. **Surface Inputs**:
   - **Base Map** → tu albedo. El color-picker al lado multiplica (déjalo blanco si el color va en la textura).
   - **Metallic Map** → tu MetallicSmoothness. Si no hay mapa, usa los sliders **Metallic** y **Smoothness** constantes.
   - **Smoothness Source** = **Metallic Alpha** (o Albedo Alpha según §4).
   - **Normal Map** → tu normal; slider de intensidad 0–1 (1 = tal cual horneado).
   - **Height Map** (parallax), **Occlusion Map**: solo si los tienes; ambos con slider de intensidad.
   - **Emission**: activa el toggle, asigna Emission Map / color HDR (>1 para que el Bloom lo agarre [ver: unity/rendering-urp]).
3. **Tiling/Offset**: escala/posición del UV a nivel material (no confundir con las UVs de la malla). Tiling >1 repite; útil en trim sheets/tileables [ver: atlas-trim-optimizacion]. Déjalo 1/0 para texturas de asset único.
4. **Advanced** → **Enable GPU Instancing = ON** para props que se repiten muchísimo (rocas, vallas). Combina con SRP Batcher y, en Unity 6, GPU Resident Drawer [ver: unity/rendering-urp]. ⚠️ No uses `MaterialPropertyBlock` en estos materiales: rompe el SRP Batcher.

Diseño de materiales: **pocos shaders, muchos materiales** — el SRP Batcher hace baratos los materiales distintos del mismo shader, así que no metas todo en un material gigante ni uses 6 materiales "para organizar" un prop [ver: unity/rendering-urp].

## 6. Automatizar el import (AssetPostprocessor)

Configurar sRGB/tipo/compresión a mano en cada textura no escala y se te olvida en una. Un **AssetPostprocessor** con `OnPreprocessTexture()` lo hace por **sufijo de nombre** o **carpeta**. Verificado: corre "just before the texture importer is run"; se accede al importer casteando `assetImporter` a `TextureImporter`; `assetPath` permite lógica condicional.

Convención de naming de entrega (acuérdala con el artista): `Prop_Nombre_BaseColor`, `_Normal`, `_MetallicSmoothness`, `_Occlusion`, `_Emission`, `_Height`.

```csharp
// Assets/Editor/TextureImportRules.cs — settea sRGB/tipo por sufijo. Corre en cada (re)import.
using UnityEditor;

public class TextureImportRules : AssetPostprocessor
{
    void OnPreprocessTexture()
    {
        // solo texturas bajo la carpeta de arte del proyecto
        if (!assetPath.Contains("/_Game/Textures/")) return;
        var t = (TextureImporter)assetImporter;

        if (assetPath.EndsWith("_Normal.png"))
        {
            t.textureType = TextureImporterType.NormalMap; // tipo Normal → lineal + compresión de normales
            // t.flipGreenChannel = true; // SOLO si el proyecto recibe normales DirectX
        }
        else if (assetPath.Contains("_BaseColor") || assetPath.Contains("_Emission"))
        {
            t.sRGBTexture = true;  // color percibido → sRGB ON
        }
        else // MetallicSmoothness, Occlusion, Roughness, Height, masks: DATO lineal
        {
            t.sRGBTexture = false; // ⛔ sRGB OFF o los valores entran con gamma mal aplicada
            t.alphaIsTransparency = false; // el alpha es smoothness, no transparencia
        }

        t.mipmapEnabled = true;   // 3D: sí
        t.isReadable = false;     // no duplicar en memoria CPU
    }
}
```

- Alternativa sin código: **Presets** por carpeta (un `.preset` de TextureImporter aplicado a la carpeta) — más fácil de mantener para equipos, mismo efecto [ver: unity/rendimiento-unity].
- Reglas por sufijo > por carpeta cuando conviven varios tipos de mapa en la misma carpeta del asset.
- Este postprocessor y el de sprites/FBX viven juntos; el patrón completo de auto-import está en [ver: pipeline/arte-a-unity §9].

## 7. Snippets bpy: hornear y exportar pensando en Unity

El bake real (cage, ray distance, anti-aliasing, denoise) es tema de [ver: baking]; el unwrap es [ver: uv-unwrapping]. Aquí solo los **parámetros que tocan la entrada a Unity**, verificados contra la API de Blender 5.2.

**Unwrap mínimo** (params y estrategia real en [ver: uv-unwrapping]):

```python
import bpy
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project()   # o unwrap con seams marcados — ver uv-unwrapping
bpy.ops.object.mode_set(mode='OBJECT')
```

**Bake de normal tangent en OpenGL (lo que Unity espera):** `normal_g='POS_Y'` es el default y ES OpenGL/Y+. Para DirectX se pondría `'NEG_Y'` — no lo hagas si el estándar del proyecto es OpenGL (§3).

```python
bpy.context.scene.render.engine = 'CYCLES'
# low-poly ACTIVA + high-poly seleccionada; nodo Image Texture destino activo en el material
bpy.ops.object.bake(
    type='NORMAL',
    normal_space='TANGENT',                       # default; correcto para malla que anima
    normal_r='POS_X', normal_g='POS_Y', normal_b='POS_Z',  # OpenGL / Y+ = Unity
    use_selected_to_active=True,
    use_cage=True, cage_extrusion=0.05,           # o max_ray_distance si no usas cage
    margin=16, margin_type='EXTEND',              # margin evita seams por mip/filtering
)
# roughness: type='ROUGHNESS'  ·  AO: type='AO' (Ambient Occlusion)  ·  emisión: type='EMIT'
```

**Export FBX para Unity** (params verificados de `bpy.ops.export_scene.fbx`):

```python
bpy.ops.export_scene.fbx(
    filepath="/ruta/Prop_LOD0.fbx",
    use_selection=True,
    use_tspace=True,          # exporta tangentes → normal maps correctos en Unity (default False)
    mesh_smooth_type='FACE',  # exporta smoothing (default 'OFF' pierde grupos de suavizado)
    apply_unit_scale=True,
    axis_forward='-Z', axis_up='Y',
    bake_anim=False,
)
```

- La **escala** (1 unidad = 1 m) y la **conversión de ejes** se rematan del lado de Unity (Scale Factor / Convert Units / Bake Axis Conversion en el FBX Importer) — criterio y verificación en [ver: pipeline/arte-a-unity §7]. `use_tspace=True` es lo que evita normales rotos por tangentes ausentes.
- Las texturas se exportan **aparte** (PNG/TGA), nunca embebidas en el FBX (`embed_textures=False`, default).

## 8. Verificación en Unity (bajo shader y luz reales)

El render del DCC **no cuenta**. Un normal/smoothness solo se aprueba en Unity, con el material Lit y la luz del juego [ver: pipeline/arte-a-unity §10]:

1. **Nada rosado**: rosado = shader Built-in en proyecto URP → Render Pipeline Converter [ver: unity/rendering-urp].
2. **Color spaces**: albedo con color natural (no lavado ni oscuro de más = sRGB mal); metal/roughness respondiendo bien = data en lineal.
3. **Normal**: gira una luz direccional alrededor del asset — los bumps deben resaltar hacia la luz. Si se hunden al revés → verde volteado (§3).
4. **Smoothness**: mueve la cámara y una luz — el highlight debe apretarse/abrirse coherente; metal reflejando el entorno (Reflection Probe/skybox) [ver: unity/rendering-urp]. "Todo plástico" = roughness donde iba smoothness (§4).
5. **Bajo la luz REAL del nivel** (no un viewport neutro): a la escena visual-target, con post-proceso real. Emisión: confirma que el Bloom la agarra (HDR + emission >1).
6. **Batching/materiales**: 1 material por prop, GPU Instancing donde toque; el Frame Debugger confirma que batchea [ver: unity/rendering-urp].

## Checklist de entrega: asset texturizado completo (game-ready)

Antes de marcar un asset como "listo para Unity", audita el paquete completo — no solo las texturas. Malla y UVs se detallan en [ver: modelado/fundamentos-3d] y [ver: uv-unwrapping]; aquí solo la lista de verificación que amarra ese trabajo con el handoff de textura (§1) y el material (§5):

- [ ] **Malla**: LOD0 exportado con `use_tspace=True` (tangentes) y `mesh_smooth_type` correcto (§7); escala/ejes van a corregirse en el FBX Importer de Unity, no en el export [ver: pipeline/arte-a-unity §7].
- [ ] **UVs**: un solo set (UV0) sin solapes fuera de tiles intencionales, 0–1 space; detalle de unwrap/margin en [ver: uv-unwrapping].
- [ ] **Set de mapas** completo según la tabla de §1 para el workflow del asset: Base Map siempre; MetallicSmoothness (o metallic/smoothness constante); Normal casi siempre; Occlusion/Height/Emission solo si aplican.
- [ ] **Normal en convención del proyecto** (OpenGL/Y+, §3) — no mezclado con DirectX en el mismo set.
- [ ] **Smoothness ya empaquetado** en el alpha correcto (Metallic o Albedo, §4) — nunca roughness suelto sin invertir.
- [ ] **Nombres con sufijo** de la convención (§6) para que el AssetPostprocessor/Preset los reconozca sin tocar nada a mano.
- [ ] **Material URP Lit** creado y configurado (§5): Workflow Mode, Smoothness Source, Tiling/Offset, GPU Instancing si aplica.
- [ ] **Verificado en Unity** bajo el Lit real y la luz del nivel (§8) — no aprobado desde el render del DCC.
- [ ] **1 material por prop** (o el mínimo justificado); sin `MaterialPropertyBlock` si usa GPU Instancing.

Un asset que falta cualquiera de estos puntos no está "game-ready" — se devuelve al paso que falló, no se completa a medias en Unity.

## Reglas prácticas

1. sRGB ON **solo** en albedo y emisión; **OFF** en normal (lo maneja el tipo), metallic, roughness, AO, height y cualquier mask — son datos lineales.
2. Marca el normal como Texture Type = **Normal map**; no toques su sRGB a mano.
3. Estándar del proyecto: **normales OpenGL/Y+** (lo que Unity espera). Hornea/exporta así; `Flip Green Channel` solo para assets DirectX de terceros. Nunca mezcles convenios.
4. URP usa **smoothness = 1 − roughness**. Empaqueta MetallicSmoothness (metallic RGB + smoothness en A) en el DCC; el roughness suelto se invierte antes de importar.
5. Material Lit: **Smoothness Source = Metallic Alpha** (o Albedo Alpha); confírmalo, es de donde el shader lee el brillo.
6. El alpha del Metallic Map es **dato** → `alphaIsTransparency` OFF y compresión que preserve alpha (BC7/DXT5, nunca BC1/DXT1).
7. Read/Write **OFF** siempre que no lo lea un script; mipmaps ON para todo lo 3D.
8. Nombra los mapas con sufijo fijo (`_BaseColor/_Normal/_MetallicSmoothness/_Occlusion/_Emission/_Height`) y deja que un **AssetPostprocessor** o Preset configure el import — no lo hagas a mano por textura.
9. `use_tspace=True` al exportar FBX; sin tangentes exportadas los normal maps salen rotos.
10. Escala y ejes se corrigen en el **FBX Importer de Unity**, no peleando el export [ver: pipeline/arte-a-unity §7].
11. 1 material por prop objetivo; pocos shaders + muchos materiales (SRP Batcher). GPU Instancing en props muy repetidos; jamás `MaterialPropertyBlock` en ellos.
12. Tiling/Offset del material para tileables/trim sheets; 1/0 para asset único.
13. Emisión: HDR + valor >1 para que alimente el Bloom [ver: unity/rendering-urp].
14. Tamaños potencia de 2; compresión y formato por plataforma (ASTC móvil / BC desktop) [ver: unity/rendimiento-unity], [ver: atlas-trim-optimizacion].
15. Aprobación **solo en Unity**, con el material Lit real, luz y post del nivel, en movimiento — nunca el render del DCC.
16. Un asset que falla la verificación (§8) se devuelve con el paso que falló; no se "arregla un poquito" en Unity — eso crea drift permanente.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Albedo se ve lavado/oscuro de más | sRGB mal: albedo/emisión = sRGB **ON**; el resto **OFF** |
| Metal "lavado" o roughness corrida | Data map con sRGB **ON** (gamma sobre un dato). Apagar sRGB en metallic/roughness/AO/height/mask |
| Bumps del normal hundidos al revés / luz al revés | Verde volteado (DirectX en proyecto OpenGL): hornear OpenGL o `Flip Green Channel` en el import (uno solo) |
| Normal se ve "plano" o con artefactos en bordes | Falta `use_tspace=True` en el export FBX (sin tangentes) o mal margin en el bake |
| "Todo se ve plástico / metal apagado" | Metieron **roughness** donde URP quiere **smoothness**; empaquetar `1−roughness` en el alpha del Metallic |
| Smoothness bandeado/sucio | Compresión que descarta alpha (BC1/DXT1) o `alphaIsTransparency` ON comiéndose el canal; usar BC7/DXT5 y apagarlo |
| El material no reacciona al metallic/smoothness | Smoothness Source apuntando al alpha equivocado (Metallic vs Albedo); o el mapa no tiene alpha |
| Material rosado al asignar | Shader Built-in en proyecto URP → Render Pipeline Converter [ver: unity/rendering-urp] |
| Emisión no brilla / sin Bloom | Emission <1 o sin HDR; subir emisión >1 y activar Bloom [ver: unity/rendering-urp] |
| Cada textura configurada a mano y una queda mal | AssetPostprocessor/Preset por sufijo o carpeta; dejar de tocar el importer a mano |
| Normal invertido "arreglado" dos veces (export OpenGL + Flip en Unity) | Se cancelan: elegir UN fix, no ambos |
| Aprobar viendo el render de Blender/Painter | Solo cuenta en Unity con el Lit real y la luz del nivel [ver: pipeline/arte-a-unity §10] |
| Prop con 6 materiales "para organizar los mapas" | 1 material/prop; SRP Batcher hace baratos los materiales del mismo shader [ver: unity/rendering-urp] |

## Fuentes

- **Lit Shader (URP)** — Unity Manual 6000.2 (`urp/lit-shader.html`) — Workflow Metallic/Specular, Base/Metallic/Normal/Height/Occlusion/Emission, **Smoothness Source = Metallic Alpha / Albedo Alpha**, relación inversa smoothness↔roughness, Tiling/Offset, Advanced → **Enable GPU Instancing**.
- **Normal map texture type** — Unity Manual 6000.2 (`texture-type-normal-map.html`) — **Flip Green Channel** ("Inverts the Y channel… when source data uses different conventions than Unity expects"), Create From Grayscale, Bumpiness, Filtering.
- **Normal map / bump (Standard)** — Unity Manual 6000.2 (`StandardShaderMaterialParameterNormalMap.html`) — textual: *"Unity uses Y+ normal maps, sometimes known as OpenGL format"*; RGB guarda XYZ con Z = "up" del vector.
- **TextureImporter (Scripting API)** — Unity 6000.2 ScriptReference — `sRGBTexture`, `textureCompression`, `alphaSource`, `alphaIsTransparency`, `mipmapEnabled`, `wrapMode`, `filterMode`, `isReadable` (tipos y semántica exactos).
- **AssetPostprocessor.OnPreprocessTexture** — Unity 6000.2 ScriptReference — corre "just before the texture importer is run", cast de `assetImporter` a `TextureImporter`, `assetPath.Contains(...)` para reglas por nombre.
- **Render Baking (Cycles)** — Blender Manual latest (`render/cycles/baking.html`) — Bake Types (Combined, Normal, Roughness, AO, Emit, Diffuse…), Normal **Space Tangent/Object**, **Swizzle R/G/B**, Selected to Active, Extrusion / Max Ray Distance / **Cage / Cage Object**, Margin (Extend/Adjacent Faces).
- **`bpy.ops.object.bake` y `bpy.ops.export_scene.fbx`** — Blender Python API (docs.blender.org/api/current) — firmas y defaults verificados: bake `type='COMBINED'`, `normal_space='TANGENT'`, `normal_r/g/b='POS_X/POS_Y/POS_Z'`, `margin=16`, `margin_type='EXTEND'`, `use_selected_to_active`, `cage_extrusion`; fbx `use_tspace=False`, `mesh_smooth_type='OFF'`, `apply_unit_scale`, `axis_forward='-Z'`, `axis_up='Y'`.
- **Toolbag Baking Tutorial** — Marmoset (`marmoset.co/posts/toolbag-baking-tutorial`) — handedness: OpenGL/Y+ = right/Maya vs DirectX/Y− = left/3DS Max; **Flip Y** e invertir el canal verde para convertir; tangent space.
- **Bases sintetizadas** — [ver: pipeline/arte-a-unity] (spec de entrega 3D, canales URP Lit, runbook de auditoría §10), [ver: unity/rendering-urp] (URP Lit vs Simple Lit/Unlit, SRP Batcher, GPU Instancing, Bloom/HDR, materiales rosados). Puentes internos: [ver: pbr-teoria], [ver: baking], [ver: uv-unwrapping], [ver: texturizado-blender], [ver: substance-y-alternativas], [ver: estilizado-texturas], [ver: atlas-trim-optimizacion], [ver: unity/rendimiento-unity].
