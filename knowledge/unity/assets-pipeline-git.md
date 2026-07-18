# Pipeline de assets y Git

> **Cuando cargar este archivo:** al importar/configurar cualquier asset (sprite, textura, audio, modelo), al montar Sprite Atlas o Addressables, al inicializar el repo de un proyecto Unity, o cuando hay un conflicto de merge en escena/prefab. Verificado contra docs de Unity 6.2 (6000.2) y Addressables 3.1.

## 1. Import settings por tipo

### Sprites (2D)

| Setting | Valor recomendado | Criterio |
|---|---|---|
| Texture Type | `Sprite (2D and UI)` | Obligatorio para SpriteRenderer/UI Image |
| Pixels Per Unit (PPU) | **Un solo valor para TODO el proyecto** (100 es el default que muestra el Inspector; pixel art: PPU = tamaño del tile, p.ej. 16 o 32) | PPU define cuántos píxeles = 1 unidad de mundo. Mezclar PPUs rompe escalas y física. NO VERIFICADO por cita textual en docs (`TextureImporter.spritePixelsPerUnit` no documenta su default); el valor 100 es el que el Inspector precarga en un proyecto nuevo |
| Filter Mode | Pixel art: `Point (no filter)` · Arte HD: `Bilinear` | Point = bordes duros; Bilinear = suavizado. Trilinear solo con mipmaps |
| Mipmaps | **Off** en 2D puro | Mipmaps en sprites 2D solo desperdician 33% de memoria; útiles solo si el sprite se ve a distancias variables en 3D |
| Mesh Type | `Tight` (default; reduce overdraw) · `Full Rect` para sprites con 9-slice/tiling | Sprites <32×32 px usan Full Rect automáticamente |
| Compression | Pixel art/UI nítida: `None` o `High Quality` · resto: `Normal Quality` | La compresión con bloques (ASTC/DXT) mancha el pixel art |
| sRGB | On (color) | Off solo para máscaras/datos |

- Pivot: definirlo en import (presets abajo), no compensarlo con offsets en código.
- Pixel art completo: Point + Compression None + sin mipmaps + PPU = tile + snapping consistente. [ver: gamedev/arte-direccion]

### Texturas (3D / URP)

Formatos por plataforma (docs Unity 6.2, "Choose a GPU texture format by platform"):

| Plataforma | Color RGB | Color RGBA | Normal map | HDR |
|---|---|---|---|---|
| Desktop (DX11+) | DXT1/BC1 (4 bpp) | **BC7** (calidad) o DXT5/BC3 (compila más rápido) — 8 bpp | BC7 o BC5 | BC6H |
| iOS/tvOS | **ASTC** (4×4=8 bpp … 12×12=0.89 bpp) | ASTC | ASTC 4×4/5×5 | ASTC HDR |
| Android moderno | **ASTC** | ASTC | ASTC | ASTC HDR (fallback RGB9e5/RGBA Half) |
| Android viejo (GLES3) | ETC2 | ETC2 | ETC2 | — |

- Regla mobile: default del proyecto en **ASTC 6×6**; subir a 4×4 en texturas hero/UI, bajar a 8×8 en texturas de fondo. Configurar en Platform Override, no por textura suelta. [ver: build-plataformas]
- Max Size: dejar la fuente grande y limitar por override (2048 default; UI y props pequeños suelen vivir bien en 1024/512).
- Crunch compression: formatos "Crunched" (RGB Crunched DXT1, RGBA Crunched DXT5) son "additional **on-disk** Crunch compression" (docs, GPU texture formats reference) — reduce tamaño en disco/descarga; en runtime la GPU sigue viendo DXT/ETC normal, la memoria de video NO baja.
- Read/Write Enabled: **Off** (default) — On duplica la textura en RAM de CPU. Solo On si se lee con `GetPixels`.
- sRGB Off para: normal maps (el tipo Normal Map lo maneja), masks, lookup tables. [ver: rendering-urp]

### Audio

| Uso | Compression Format | Load Type | Notas |
|---|---|---|---|
| SFX corto (<~1s, disparos UI, clicks) | PCM | Decompress On Load | Máxima calidad, CPU cero |
| SFX frecuente con ruido (pasos, impactos, armas) | **ADPCM** (3.5:1, CPU baja) | Decompress On Load | Recomendación explícita de docs para este caso |
| SFX medio/largo | Vorbis (Quality ~0.7) | Compressed In Memory | Vorbis descomprimido ocupa ~10× su tamaño comprimido; ADPCM ~3.5× |
| Música / ambiente | Vorbis (Quality 0.5–0.7) | **Streaming** | ~200 KB de overhead por stream, memoria mínima |

- **Force To Mono**: On para SFX 3D/espacializados (el spatializer los reproduce mono igual; ahorra la mitad de memoria). Unity re-normaliza el volumen tras el downmix.
- **Load In Background**: On en clips grandes para no bloquear el main thread.
- **Preload Audio Data**: Off solo si se gestiona la carga por código (p.ej. vía Addressables). [ver: audio-unity]

### Modelos 3D (FBX)

| Setting | Recomendación |
|---|---|
| Scale Factor | Ajustar aquí si la fuente no viene en metros — nunca escalar el Transform para compensar |
| Mesh Compression | Off por defecto; Low/Medium en props si el vertex snapping no se nota |
| Read/Write Enabled | **Off** (ahorra la copia en CPU RAM). On solo para leer/modificar mesh por script |
| Optimize Mesh | `Everything` (default): reordena vértices/triángulos para la GPU |
| Generate Colliders | Solo geometría de entorno estática; NUNCA en objetos dinámicos |
| Normals | `Import` si el DCC trae smoothing correcto; `Calculate` (Angle Weighted) si no |
| Tangents | `Calculate Mikktspace` (default) |
| Index Format | 16-bit (default) salvo mallas >65k vértices |

- Materiales: extraerlos una vez (`Extract Materials`) y desligar del FBX; no editar materiales embebidos.
- Animaciones dentro del FBX: [ver: animacion-unity].

### Presets y AssetPostprocessor — no repetir settings a mano

Dos mecanismos oficiales (docs Unity 6.2, "Presets"):

1. **Preset**: en cualquier importer, botón Preset (slider icon) → `Save current to...`. En **Preset Manager** (Project Settings) se registran como default de importación, con filtros — incluida la aplicación **automática por carpeta** ("Apply default presets to assets by folder"). Es la vía sin código: un preset `SpritePixelArt` aplicado a `Assets/Game/Art/Sprites/`.
2. **AssetPostprocessor**: reglas por código, versionables y a prueba de olvidos. Métodos exactos: `OnPreprocessTexture`, `OnPreprocessAudio`, `OnPreprocessModel`, `OnPreprocessAsset`, `OnPostprocessAllAssets`.

```csharp
// Editor/SpriteImportRules.cs — fuerza settings al importar, solo la primera vez
public class SpriteImportRules : UnityEditor.AssetPostprocessor
{
    void OnPreprocessTexture()
    {
        if (!assetPath.StartsWith("Assets/Game/Art/Sprites/")) return;
        var imp = (UnityEditor.TextureImporter)assetImporter;
        if (!imp.importSettingsMissing) return; // respeta ajustes manuales posteriores
        imp.textureType = UnityEditor.TextureImporterType.Sprite;
        imp.spritePixelsPerUnit = 100;
        imp.filterMode = FilterMode.Point;
        imp.mipmapEnabled = false;
    }
}
```

Regla: el agente configura el preset/postprocessor UNA vez al inicio del proyecto y deja de tocar import settings asset por asset.

## 2. Sprite Atlas

**Por qué**: sprites sueltos = 1 draw call por textura. Un atlas empaqueta todo en una textura y el SpriteRenderer/Canvas puede batchear en un solo draw call. [ver: rendimiento-unity]

**Cuándo**: siempre que haya >5–10 sprites que se dibujan juntos (UI de una pantalla, tiles de un nivel, animación de un personaje). Agrupar por *uso simultáneo*, no por tipo: un atlas `UI_HUD`, un atlas `Player`, un atlas por bioma.

**Cómo** (Unity 6.2): `Assets > Create > 2D > Sprite Atlas` → arrastrar carpetas o sprites a **Objects for Packing** (acepta carpetas: todo lo de dentro se empaqueta).

| Propiedad | Valor | Nota |
|---|---|---|
| Type | `Master` | `Variant` = copia reescalada del master (p.ej. atlas HD/SD) |
| Include in Build | On (default) | Off solo para late binding manual vía API |
| Allow Rotation | On, **pero Off si el atlas contiene sprites de UI** (la rotación rompe la orientación en Canvas — advertencia explícita de docs) | |
| Tight Packing | On (default), **Off si hay 9-slice/tiling** | |
| Padding | 4 px (default); subir a 8 si sangran bordes con mipmaps/escalado | |

- El atlas **sobreescribe** compresión, filter mode, mipmaps y sRGB de los sprites empaquetados: configurar calidad EN el atlas, no en cada sprite fuente.
- Sprite Atlas V2 es el modo activo **por defecto desde Unity 2022.2+** (incluye Unity 6); V1 queda como legacy y no recibe atlas nuevos. V2 migra assets V1 automáticamente (quedan incompatibles con V1) y permite elegir si el atlas es la fuente de textura en Edit/Play mode o solo en build. API runtime (`SpriteAtlasManager`) permite late binding.
- Con Addressables: el atlas es el asset addressable; no marcar los sprites sueltos además del atlas (duplica la textura en bundles).

## 3. Carga de assets: Addressables vs Resources vs AssetBundles

### Resources — prohibido (razones oficiales, docs Unity 6.2)

- La memoria del sistema Resources escala con el número de objetos **aunque no estén cargados**; "hace más difícil el manejo de memoria".
- Frena el arranque: inicializar un sistema Resources con 10.000 assets toma **varios segundos en móviles de gama baja** (cita de docs).
- Todo lo que hay en `Resources/` entra SIEMPRE al build (no se puede stripear, ni variar por plataforma, ni parchear sin rebuild completo).
- Unity mismo recomienda AssetBundles/Addressables para cualquier proyecto no trivial.
- Uso tolerable: prototipos y assets diminutos vivos toda la sesión. En producción: **cero `Resources.Load`** — referencias directas serializadas para lo que va con la escena, Addressables para lo dinámico.

### AssetBundles legacy

Es el mecanismo de bajo nivel (empaquetar assets fuera del build, cargar en runtime). Usarlos a mano obliga a gestionar dependencias entre bundles, rutas y refcounts manualmente. **Addressables está construido encima de AssetBundles** y automatiza exactamente eso — no hay razón para AssetBundles crudos en un proyecto nuevo.

### Addressables (paquete `com.unity.addressables`, 3.x en Unity 6)

Conceptos:
- **Address**: string único con el que se carga el asset (independiente de su path).
- **Group**: unidad de organización en el Editor (los groups no existen en runtime; para descubrir en runtime se usan **labels**). Cada group define Build Path / Load Path (con profile variables) y **Bundle Mode**: `Pack Together` (1 bundle por group), `Pack Separately` (1 bundle por entry — para carpetas addressables), `Pack Together By Label`.
- **Catalog**: el índice address → ubicación que se genera al hacer el build de Addressables (build de contenido separado del build del player).

Carga y liberación — regla de oro de docs: **"cada load se espeja con un release"**:

```csharp
AsyncOperationHandle<GameObject> _handle;

async Awaitable SpawnBoss()
{
    _handle = Addressables.LoadAssetAsync<GameObject>("Boss_Final");
    GameObject prefab = await _handle.Task;
    Instantiate(prefab);
}

void OnDestroy()
{
    if (_handle.IsValid()) Addressables.Release(_handle); // espejo del load
}
```

Para instanciar directo: `Addressables.InstantiateAsync(address)` + `Addressables.ReleaseInstance(instance)` (libera y destruye).

Memoria (docs Addressables 3.1, "Managing asset memory"):
- Reference counting por asset Y por bundle: un asset liberado **no se descarga** hasta que el refcount del bundle que lo contiene llega a 0. Liberar 2 de 3 assets de un bundle deja el bundle entero en memoria.
- Evitar *asset churn*: liberar y recargar enseguida el mismo asset/bundle degrada rendimiento; mantener cargado lo que se va a reusar pronto.
- Diagnóstico: **Addressables Profiler module** (muestra refcounts y qué mantiene vivo cada bundle). [ver: rendimiento-unity]

Setup mínimo para un juego local (sin CDN): instalar paquete → `Window > Asset Management > Addressables > Groups` → marcar assets/carpetas como Addressable → todo en el Default Local Group (Pack Together por pantalla/nivel) → el build de player dispara el build de Addressables (o `Build > New Build > Default Build Script`). Con CDN remoto: [ver: build-plataformas].

## 4. Estructura de carpetas estándar

Organizar **por feature, no por tipo de asset** (guías de estilo de la comunidad, p.ej. Unity-Style-Guide de justinwasilenko), y TODO el contenido propio bajo una carpeta raíz con el nombre del juego — evita colisiones al importar third-party:

```
Assets/
  _Game/                  ← todo lo propio vive aquí (el _ lo sube arriba)
    Art/        (Sprites/, Models/, Materials/, Animations/, Fonts/)
    Audio/      (Music/, SFX/)
    Code/       (Runtime/, Editor/  ← con asmdefs propios)
    Prefabs/
    Scenes/
    Data/       (ScriptableObjects, configs)
    UI/
  Plugins/                ← SDKs nativos/DLLs
  ThirdParty/             ← assets de la Asset Store, SIN tocar por dentro
  Settings/               ← URP assets, Presets, Input Actions
```

- Carpetas con significado especial para Unity (no usar esos nombres a la ligera): `Editor`, `Resources`, `StreamingAssets`, `Plugins`, `Gizmos`, `Editor Default Resources`.
- Scripts propios separados de third-party con Assembly Definitions → compilaciones incrementales más rápidas. [ver: arquitectura-unity]
- Nomenclatura consistente tipo `Prefijo_Nombre_Variante` (`T_Player_N`, `M_Rock`, `SM_Tree_01`) — lo que importa es elegir UNA convención y automatizarla.
- No dejar carpetas vacías: git no las trackea pero Unity les genera `.meta` → churn de metas huérfanos entre máquinas.

## 5. Git para Unity

### Configuración del proyecto (una vez, antes del primer commit)

`Edit > Project Settings > Editor`:
- **Asset Serialization Mode = Force Text** (default en Unity 6): escenas/prefabs/assets en YAML diffeable. Sin esto no hay merge posible.
- **Version Control = Visible Meta Files** (default).
- Activar "Reduce version control noise" (escribe el YAML en una línea por estructura cuando puede → diffs más limpios).
- Line endings de scripts: Unix (LF) para no pelear entre macOS/Windows; reforzado por `.gitattributes` (abajo).

### Por qué los .meta se commitean SIEMPRE

Cada asset tiene un `.meta` con su **GUID**. TODAS las referencias entre assets (script en prefab, textura en material, escena en build settings) se guardan por GUID, no por path. Si un `.meta` no llega al repo, Unity genera uno nuevo en la otra máquina → GUID distinto → **todas las referencias a ese asset se rompen** (missing script/reference). Regla: asset y su `.meta` viajan **en el mismo commit**, siempre — también al mover/renombrar (mover desde el Editor o con `git mv` ambos archivos, nunca desde el Finder solo el asset).

### .gitignore canónico (base: github/gitignore Unity.gitignore)

```gitignore
# Generado por Unity — NUNCA commitear
[Ll]ibrary/
[Tt]emp/
[Oo]bj/
[Bb]uild/
[Bb]uilds/
[Ll]ogs/
[Uu]ser[Ss]ettings/
[Mm]emoryCaptures/
[Rr]ecordings/

# IDE / OS
.vs/
.idea/
*.csproj
*.sln
*.user
*.DotSettings.user
.DS_Store

# Crash / misc
sysinfo.txt
mono_crash.*
*.pidb
*.booproj

# Artefactos de build
*.apk
*.aab
*.unitypackage
*.unitypackage.meta
*.app

# Addressables (lo generado, no la config)
/[Aa]ssets/[Aa]ddressable[Aa]ssets[Dd]ata/*/*.bin*
/[Ss]erver[Dd]ata/
/[Aa]ssets/[Ss]treamingAssets/aa*

# Auto-generados por tests/visual scripting
/[Aa]ssets/[Ii]nit[Tt]est[Ss]cene*.unity*
/[Aa]ssets/[Ss]ceneDependencyCache*
```

**SÍ se commitean**: `Assets/` completo (con metas), `ProjectSettings/`, `Packages/manifest.json` y `Packages/packages-lock.json`. `Library/` se regenera solo — jamás al repo.

### Git LFS (.gitattributes)

Binarios grandes van por LFS; los YAML de Unity son TEXTO y se quedan en git normal con el merge driver de Unity (patrón del .gitattributes de referencia de la comunidad, gist de nemotoo):

```gitattributes
# YAML de Unity: texto, LF, merge inteligente
*.unity   merge=unityyamlmerge eol=lf
*.prefab  merge=unityyamlmerge eol=lf
*.asset   merge=unityyamlmerge eol=lf
*.meta    eol=lf
*.cs      eol=lf

# Binarios → LFS
*.png  filter=lfs diff=lfs merge=lfs -text
*.jpg  filter=lfs diff=lfs merge=lfs -text
*.psd  filter=lfs diff=lfs merge=lfs -text
*.tga  filter=lfs diff=lfs merge=lfs -text
*.exr  filter=lfs diff=lfs merge=lfs -text
*.wav  filter=lfs diff=lfs merge=lfs -text
*.mp3  filter=lfs diff=lfs merge=lfs -text
*.ogg  filter=lfs diff=lfs merge=lfs -text
*.mp4  filter=lfs diff=lfs merge=lfs -text
*.fbx  filter=lfs diff=lfs merge=lfs -text
*.blend filter=lfs diff=lfs merge=lfs -text
*.ttf  filter=lfs diff=lfs merge=lfs -text
*.dll  filter=lfs diff=lfs merge=lfs -text
*.unitypackage filter=lfs diff=lfs merge=lfs -text
```

`git lfs install` una vez por máquina ANTES del primer commit de binarios (un binario commiteado sin LFS queda en la historia para siempre). Ojo: algunos `.asset` son binarios (Terrain, NavMesh, lighting) incluso con Force Text — si un `.asset` binario da problemas, moverlo a LFS por path específico.

### UnityYAMLMerge / Smart Merge

Herramienta oficial que hace merge semántico de escenas/prefabs (por objeto, no por línea). Viene con el Editor (docs Unity 6.2):
- Windows: `C:\Program Files\Unity\Editor\Data\Tools\UnityYAMLMerge.exe` (con Unity Hub: `C:\Program Files\Unity\Hub\Editor\<versión>\Editor\Data\Tools\`)
- macOS: `/Applications/Unity/Unity.app/Contents/Tools/UnityYAMLMerge` (vía Hub: `/Applications/Unity/Hub/Editor/<versión>/Unity.app/Contents/Tools/`)

Config en `.git/config` o `~/.gitconfig` (snippet oficial de docs):

```ini
[merge]
    tool = unityyamlmerge
[mergetool "unityyamlmerge"]
    trustExitCode = false
    cmd = '<ruta a UnityYAMLMerge>' merge -p "$BASE" "$REMOTE" "$LOCAL" "$MERGED"
```

- El `merge=unityyamlmerge` del `.gitattributes` requiere además definir el driver: `git config merge.unityyamlmerge.driver "'<ruta>' merge -p %O %B %A %A"` (o simplemente invocar `git mergetool` cuando haya conflicto).
- Comportamiento configurable en `mergerules.txt` (junto al ejecutable) y modos Off/Premerge/Ask en Project Settings > Version Control.
- Límite real (confirmado por docs y práctica): si dos ramas tocaron **el mismo GameObject/componente**, UnityYAMLMerge no puede resolverlo — ahí aplica la sección 7.

## 6. Estrategia de branches con escenas compartidas

Una escena `.unity` es un archivo gigante que concentra conflictos. Estrategia en orden de eficacia:

1. **Prefab como unidad de trabajo.** La escena solo contiene instancias de prefabs (posición/rotación). Todo cambio de contenido se hace DENTRO del prefab (Prefab Mode) → el diff cae en el `.prefab`, no en la `.unity`. Dos personas pueden trabajar "en la misma escena" sin tocarla, cada una en prefabs distintos.
2. **Escenas aditivas por responsabilidad.** Dividir el nivel en subescenas (`Level1_Gameplay`, `Level1_Art`, `Level1_Lighting`) cargadas con `SceneManager.LoadScene(..., LoadSceneMode.Additive)` — multi-scene editing es soporte de primera clase en Unity 6. Cada branch/persona es dueña de UNA subescena. [ver: arquitectura-unity]
3. **Ownership de escena por convención.** Si una escena no se puede dividir: un solo dueño a la vez. Con equipos: file locking (LFS `git lfs lock` o herramientas tipo Anchorpoint); en solitario/agente: nunca editar la misma escena en dos branches vivas a la vez.
4. **Branches cortas, integración frecuente.** Cuanto más vive una branch con cambios de escena, más imposible el merge. Rebase/merge de main a diario mínimo.
5. Cambios de settings (`ProjectSettings/`, Addressables config) en commits/PRs propios y pequeños — también son YAML conflictivo.

## 7. Cuando un merge de escena/prefab explota

Procedimiento, en orden:

1. **No resolver YAML a mano a ciegas.** Primero `git mergetool` para que UnityYAMLMerge intente el merge semántico. En la mayoría de conflictos "distinto objeto, misma zona del archivo" lo resuelve limpio.
2. Si UnityYAMLMerge deja conflictos (mismo GameObject tocado en ambos lados): **elegir un lado completo** — `git checkout --theirs Assets/.../Escena.unity` (o `--ours`) + su `.meta` si aplica. Criterio: conservar el lado con más trabajo o más difícil de rehacer; el otro lado se re-aplica A MANO en el Editor (los diffs de git de ambos lados dicen exactamente qué re-aplicar: posiciones, valores de componentes, objetos añadidos).
3. Abrir la escena en el Editor ANTES de commitear: consola limpia, sin "Missing Prefab", sin referencias rotas, la escena se guarda sin re-serializar medio archivo.
4. Verificar pares asset/.meta: `git status` no debe mostrar `.meta` huérfanos ni assets sin meta.
5. Commitear escena + metas juntos. Si el merge tocó prefabs de los que la escena depende, abrir también esas instancias.
6. **Prevención post-mortem:** si esto pasó, la escena estaba demasiado gorda — extraer a prefabs o dividir en subescenas (sección 6) antes de seguir.

Caso extremo (YAML corrupto, Unity no abre la escena): descartar el merge del archivo (`git checkout MERGE_HEAD -- <escena>` o el lado bueno), verificar que abre, y rehacer el resto. Una escena que no deserializa no se "arregla" borrando bloques YAML al ojo: cada bloque tiene `fileID` referenciados desde otros bloques.

## Reglas prácticas

- [ ] Primer commit del repo: `.gitignore` + `.gitattributes` + `git lfs install` ANTES de añadir assets.
- [ ] Force Text + Visible Meta Files confirmados (son default en Unity 6, pero verificar en proyectos migrados).
- [ ] Cada asset viaja con su `.meta` en el mismo commit; renombrar/mover solo desde el Editor o con `git mv` de ambos.
- [ ] `Library/`, `Temp/`, `obj/`, `Logs/`, `UserSettings/` jamás al repo; `ProjectSettings/` y `Packages/*.json` siempre.
- [ ] UN valor de PPU para todo el proyecto, definido el día 1.
- [ ] Import settings via Preset per-folder o AssetPostprocessor — nunca a mano asset por asset.
- [ ] Pixel art: Point + Compression None + mipmaps Off.
- [ ] Mobile: ASTC como formato default del proyecto; override por plataforma, no por textura.
- [ ] Read/Write Enabled Off en texturas y meshes salvo necesidad demostrada por script.
- [ ] Música = Vorbis + Streaming; SFX frecuentes = ADPCM Decompress On Load; SFX 3D = Force To Mono.
- [ ] Sprite Atlas por grupo de uso simultáneo; Allow Rotation Off si hay UI; calidad configurada en el atlas.
- [ ] Cero `Resources.Load` en código de producción; lo dinámico va por Addressables.
- [ ] Cada `Addressables.LoadAssetAsync` tiene su `Addressables.Release` espejado (y `InstantiateAsync` su `ReleaseInstance`).
- [ ] Escenas: composición de prefabs; el contenido se edita en Prefab Mode.
- [ ] Una escena = un dueño por branch; branches cortas, integrar a diario.
- [ ] Conflicto de escena → `git mergetool` con UnityYAMLMerge primero, nunca editar el YAML al ojo.
- [ ] Tras cualquier merge que tocó escenas/prefabs: abrirlas en el Editor y verificar consola limpia antes de commitear.
- [ ] No dejar carpetas vacías en `Assets/` (churn de `.meta` huérfanos).

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Commitear asset sin su `.meta` (o al revés) → GUID nuevo en otra máquina → referencias rotas en cascada | Asset + meta siempre juntos; revisar `git status` antes de cada commit |
| Binarios commiteados antes de configurar LFS → repo inflado para siempre | LFS y `.gitattributes` en el commit 0; si ya pasó, `git lfs migrate import` reescribe historia (destructivo — coordinar) |
| `Library/` en el repo (repos de gente que ignoró el gitignore) | Añadir al `.gitignore` y `git rm -r --cached Library` |
| Editar el mismo GameObject en dos branches esperando que UnityYAMLMerge lo salve | No puede. Ownership por escena/prefab + branches cortas |
| Resolver conflicto de escena aceptando hunks línea a línea en un editor de texto | El YAML de escena tiene `fileID` cruzados; hunks sueltos = escena corrupta. Usar mergetool o lado completo + re-aplicar |
| Mezclar PPUs (sprites a 100, tiles a 32) | PPU global día 1; postprocessor que lo fuerza |
| Compresión default (block-based) sobre pixel art → sprites "sucios" | Compression None/High Quality + Point en la carpeta de pixel art |
| Mipmaps On en juego 2D puro | Off: +33% memoria sin beneficio en 2D |
| Vorbis + Decompress On Load en música → pico de ~10× memoria | Streaming para música/clips largos |
| Marcar como Addressables los sprites Y su atlas | Solo el atlas: si no, la textura se duplica en bundles |
| Liberar assets Addressables y asumir que la memoria baja | El bundle vive hasta refcount 0; verificar con Addressables Profiler |
| Usar `Resources/` "solo para este prefab rapidito" | Entra al build siempre y crece el startup; referencia directa o Addressables |
| Generate Colliders activado en modelos dinámicos | Solo entorno estático; los dinámicos llevan colliders primitivos [ver: fisica-unity] |
| Third-party assets moviéndolos/editándolos dentro de su carpeta | Se pierde al actualizar el paquete; aislarlos en `ThirdParty/` y extender desde `_Game/` |
| Renombrar assets desde el explorador del OS (sin el Editor) | El `.meta` no sigue al archivo → GUID nuevo; siempre desde el Editor o `git mv` ambos |

## Fuentes

- Smart merge (UnityYAMLMerge) — Unity Manual 6.2, docs.unity3d.com — config oficial del mergetool, rutas del ejecutable, mergerules.txt, modos Off/Premerge/Ask.
- Unity.gitignore — github/gitignore (repo oficial de GitHub) — base canónica del gitignore, incluye entradas de Addressables y VisualScripting.
- Sprite (2D and UI) import settings — Unity Manual 6.2 — PPU, Filter Mode, Mesh Type (Tight, <32×32 → Full Rect), Extrude/Pivot.
- Audio Clip import settings — Unity Manual 6.2 — Load Types con costos de memoria concretos (Vorbis ~10×, ADPCM 3.5×, streaming ~200 KB), recomendaciones por tipo de sonido.
- Sprite Atlas (landing + reference + V2 landing) — Unity Manual 6.2, `sprite/atlas/sprite-atlas-reference.html` y `sprite/atlas/v2/v2-landing.html` — draw calls, propiedades (Padding 4, Allow Rotation vs UI, Tight Packing), overrides de textura del atlas, Master/Variant; V2 default desde 2022.2+, migración automática desde V1.
- Loading Resources at Runtime — Unity Manual 6.2 — downsides oficiales de Resources (memoria, startup de varios segundos con 10k assets en mobile low-end, sin patching) y recomendación de Addressables.
- Addressables 3.1: overview, Groups, Managing asset memory — docs.unity3d.com/Packages/com.unity.addressables@3.1 — address/group/catalog, bundle modes, regla load↔release, refcount por bundle, asset churn, Addressables Profiler.
- Editor settings (class-EditorManager) — Unity Manual 6.2 — Asset Serialization Force Text default, "Reduce version control noise", line endings.
- Version control integration — Unity Manual 6.2 — Visible Meta Files default, integración con VCS externos.
- Model tab (FBX Importer) — Unity Manual 6.2 — Scale Factor, Mesh Compression, Read/Write, Optimize Mesh, normals/tangents Mikktspace.
- GPU texture formats reference (antes "Choose a GPU texture format by platform") — Unity Manual 6.2, `texture-formats-reference.html` — BC1/BC7/BC6H desktop, ASTC iOS/Android, fallbacks ETC2, ASTC HDR; confirma Crunch como compresión "on-disk" (RGB/RGBA Crunched DXT1/DXT5).
- Presets — Unity Manual 6.2 — presets de importer, Preset Manager, aplicación automática por carpeta.
- AssetPostprocessor — Unity Scripting API 6.2 — nombres exactos de OnPreprocess*/OnPostprocess*.
- Multi-Scene editing — Unity Manual 6.2 — escenas aditivas como workflow colaborativo.
- Git with Unity — Anchorpoint (blog técnico) — límites reales de UnityYAMLMerge (mismo GameObject), file locking, práctica de "trabajar en prefabs, no en la escena".
- .gitattributes para Unity + LFS — gist de nemotoo (referencia comunitaria ampliamente usada) — qué extensiones a LFS y `merge=unityyamlmerge eol=lf` para .unity/.prefab/.asset.
- Unity Style Guide — justinwasilenko (GitHub) — estructura de carpetas por feature bajo carpeta raíz del proyecto, convenciones de nombres, aislamiento de third-party.
