# Arte a Unity: specs e integración

> **Cuando cargar este archivo:** al encargar, generar o recibir CUALQUIER asset visual (sprite, modelo, fuente) para un juego Unity 6/URP — para escribir la spec exacta de entrega y para auditar que el asset entra al proyecto sin retoques. Complementa la teoría de [ver: gamedev/arte-direccion] y el detalle de import de [ver: unity/assets-pipeline-git].

## 1. El contrato: la spec se congela antes del primer asset

El style guide define QUÉ se ve [ver: gamedev/arte-direccion]; este archivo define los NÚMEROS que ese guide debe congelar para que cada asset entre a Unity sin retoques. Un asset "bonito" con PPU distinto, pivot arbitrario o escala en centímetros cuesta más integrarlo que rehacerlo. La spec vive en el style guide (sección "Specs técnicos") y se congela ANTES del primer asset de producción.

Spec mínima que debe existir por escrito (valores de ejemplo, decidir los propios el día 1):

| Campo | 2D (HD) | 2D (pixel art) | 3D |
|---|---|---|---|
| Escala | PPU 100, un solo valor global | PPU = tile (16/32), un solo valor | 1 unidad = 1 m |
| Resolución de referencia | 1920×1080 (o 1080×1920 portrait) | 320×180 / 640×360 | — (texel density fija, p.ej. 512 px/m) |
| Pivot | Por categoría (abajo-centro personajes, centro props) | Custom en Pixels, snap a esquina de píxel | En el origen del modelo, según categoría (§7) |
| Formato de entrega | PNG con alpha | PNG con alpha, sin escalar | FBX (Y-up, metros) + texturas PNG/TGA |
| Presupuesto | Tamaño máx. por sprite (p.ej. 512 px) | Tamaño de tile y de personaje en px | Tris por categoría + nº materiales (ideal 1) |
| Naming | `Prefijo_Nombre_Variante` | ídem + `_LOD0..n` en 3D | ídem [ver: unity/assets-pipeline-git] |

## 2. Sprites 2D: PPU, escala del mundo y cámara

**PPU (Pixels Per Unit) es el contrato mundo↔imagen**: un sprite de `H` px de alto mide `H/PPU` unidades de mundo. Física, velocidades, tamaños de collider y zoom de cámara dependen de que sea UN solo valor en todo el proyecto [ver: unity/assets-pipeline-git §1].

Fórmulas que amarran todo (la cámara ortográfica muestra `orthographicSize` unidades desde el centro hasta el borde superior):

```
altura visible (unidades) = orthographicSize × 2
orthographicSize = altura_referencia_px / (2 × PPU)
```

- HD a 1080p de referencia, PPU 100 → `orthographicSize = 1080 / 200 = 5.4`.
- Pixel art a 320×180, PPU 16 → `orthographicSize = 180 / 32 = 5.625` (11.25 tiles de alto en pantalla).
- El ancho visible lo pone el aspect ratio del dispositivo: `alto visible × aspect`. Diseñar el gameplay para el alto (landscape) o el ancho (portrait) fijo y dejar que el otro eje respire (§6).

**Spec de entrega de un sprite** (lo que se le pide al artista o a la IA generadora):

| Ítem | Valor |
|---|---|
| Formato | PNG-32 con canal alpha real (no fondo blanco/magenta) |
| Tamaño | El de la spec: el sprite llega al tamaño final EXACTO, sin "ya lo escalas tú" |
| Densidad | UNA densidad de píxel por proyecto: un personaje de 32 px no convive con props de 48 px "por detalle" [ver: gamedev/arte-direccion §8] |
| Márgenes | Sin padding cocido en la imagen (el atlas pone el suyo); recorte al bounding box del dibujo |
| Pivot | Documentado por categoría; en pixel art: coordenada de píxel exacta |
| Animación | Frames del mismo tamaño de canvas y pivot idéntico entre frames (si no, el personaje "salta" al animar) |
| Pixel art | Sin anti-aliasing, sin semitransparencias sueltas, paleta del style guide, sin rotaciones/escalas no enteras cocidas |

Import en Unity: `Sprite (2D and UI)`, Filter/Compression según estilo — tabla completa y AssetPostprocessor en [ver: unity/assets-pipeline-git §1]. Sorting layers y orden 2D: [ver: unity/rendering-urp].

## 3. Pixel perfect: Pixel Perfect Camera (URP)

En URP el componente **Pixel Perfect Camera** viene incluido (no se instala el package aparte `com.unity.2d.pixel-perfect`, que es para Built-in). Se añade a la Main Camera y calcula el escalado del viewport para que el pixel art quede nítido y estable en movimiento a cualquier resolución. Propiedades (manual Unity 6000.2, URP):

| Propiedad | Qué hace | Valor típico |
|---|---|---|
| **Asset Pixels Per Unit** | Debe COINCIDIR con el PPU de todos los sprites | El PPU global del proyecto |
| **Reference Resolution** | Resolución para la que se diseñaron los assets | 320×180, 640×360… |
| **Crop Frame** | `None / Pillarbox / Letterbox / Windowbox / Stretch Fill` — barras negras para forzar la reference resolution en aspects distintos | `None` (mostrar más mundo) o `Pillarbox/Letterbox` si el diseño exige encuadre fijo |
| **Grid Snapping** | `Pixel Snapping` = snapea SpriteRenderers a la grilla de píxeles en render-time (no mueve transforms). `Upscale Render Texture` = renderiza a (casi) la reference resolution y upscalea — píxeles sin alias ni rotación "sucia" | `Pixel Snapping` por defecto; `Upscale Render Texture` para look retro estricto |
| **Filter Mode** | Solo con Stretch Fill: `Retro AA` (upscale entero + bilinear final, default) o `Point` | Retro AA |
| Current Pixel Ratio | Solo lectura: ratio de escalado actual | Verificar que sea entero en el device target |

**Preparación de sprites obligatoria** (doc oficial "Prepare your sprites"): mismo PPU en todos + Filter Mode `Point` + Compression `None` + pivot `Custom` con Pivot Unit Mode `Pixels` (snapea a esquinas de píxel; en Sprite Mode Multiple, pivot por cada sub-sprite). En el editor: Grid Size de la toolbar Grid and Snap = `1/PPU` por eje (PPU 16 → 0.0625) y grid snapping activo, para que los objetos colocados a mano caigan en píxel.

**Con Cinemachine**: la CinemachineCamera y la Pixel Perfect Camera pelean por el orthographic size — añadir la extensión **Cinemachine Pixel Perfect** a cada cámara virtual. Cámara y Cinemachine en general: [ver: unity/rendering-urp].

## 4. 9-slice: paneles y UI que escalan sin deformarse

9-slicing divide el sprite en 9 zonas: esquinas fijas, bordes que estiran/repiten en un eje, centro que estira/repite en ambos [ver: gamedev/arte-direccion §7].

Receta completa (Unity 6):

1. Import: **Mesh Type = Full Rect** (Tight rompe el slicing) [ver: unity/assets-pipeline-git §1].
2. **Sprite Editor** → arrastrar los 4 handles verdes o poner **Border L/R/T/B** en px → Apply. Eso define las 9 zonas.
3. En mundo (SpriteRenderer): **Draw Mode** `Sliced` (bordes estiran) o `Tiled` (repiten; Tile Mode `Continuous` repite siempre, `Adaptive` estira hasta el umbral Stretch Value y entonces repite). Redimensionar con `SpriteRenderer.size` (tool Rect), NO con `transform.localScale` — la escala deforma todo el sprite, incluidas las esquinas.
4. En UI (Image): **Image Type = Sliced** (+ `Pixels Per Unit Multiplier` para afinar el grosor visual del borde).

Límites documentados (manual 6000.2): solo `BoxCollider2D` y `PolygonCollider2D` soportan 9-slicing; no se pueden editar mientras Draw Mode sea Sliced/Tiled; con Auto Tiling la regeneración puede meter aristas extra en el collider (afecta colisiones).

**Spec al artista**: esquinas con todo el detalle (son lo único que jamás se deforma), bordes repetibles en su eje (patrón seamless), centro homogéneo o liso (se estira/repite en ambos ejes), y bordes de grosor documentado en px — ese número ES el Border del Sprite Editor.

## 5. Atlas y sorting: decisiones de proyecto, no por asset

Ambos temas están resueltos en la base — aquí solo la decisión de spec que se congela el día 1:

- **Sprite Atlas**: uno por contexto de uso simultáneo (`UI_HUD`, `Player`, uno por bioma). Settings completos, padding, V2 y trampas con Addressables: [ver: unity/assets-pipeline-git §2]. Los sprites se entregan SUELTOS; el atlas lo arma el proyecto (jamás pedir al artista un spritesheet pre-empacado sin datos de recorte).
- **Sorting Layers**: definir la lista global al inicio (típico: `Background → Props → Enemies → Player → FX → UI`) y documentar en qué layer cae cada categoría de asset; personajes multi-sprite bajo Sorting Group; top-down = Custom Axis (0,1,0) en el 2D Renderer Data. Detalle y orden de prioridad completo: [ver: unity/rendering-urp].

## 6. Resoluciones y aspect ratios móviles

El parque real de dispositivos (estado 2026) va de **4:3** (iPad) a **19.5:9–21:9** (teléfonos). No existe "la resolución del juego": existe una **resolución de referencia** y reglas de qué se adapta.

| Elemento | Estrategia |
|---|---|
| Cámara / mundo | Fijar UN eje (alto en landscape, ancho en portrait) vía orthographic size (§2); el otro eje muestra más o menos mundo según aspect. El gameplay crítico NUNCA depende del eje variable |
| Fondos | Full-bleed con sangrado: cubrir el aspect extremo y componer lo importante en la zona común. Portrait ref 1080×1920: fondo ≥1080×2400 (cubre 20:9) con lo crítico centrado en 1080×1440 (visible en 4:3). Landscape ref 1920×1080: fondo ≥2520×1080 (cubre 21:9), crítico en 1440×1080. (Aritmética de aspectos, no dogma: recalcular con la ref propia) |
| HUD / UI | Canvas Scaler `Scale With Screen Size` + Reference Resolution + Match según eje dominante; TODO lo interactivo dentro del panel SafeArea (`Screen.safeArea`) — receta y script completos en [ver: unity/ui-unity] |
| Elementos 9-slice | Escalan a cualquier tamaño sin re-export (§4) |
| Splash/key art | Entregar en 3 encuadres o como capas separables (fondo bleed + logo anclado) |

- Lo que se ESTIRA: fondos (por sangrado, no por deformación), paneles 9-slice, mundo visible en el eje libre. Lo que NO se estira jamás: sprites de gameplay, tipografía, iconos — escalan uniformes por el Canvas Scaler o no escalan.
- Pixel art: el Crop Frame / Grid Snapping de la Pixel Perfect Camera (§3) decide si los aspects raros ven más mundo, barras negras o upscale.
- Verificación SIEMPRE en Device Simulator con al menos 16:9, 20:9 y 4:3 [ver: unity/ui-unity]. UI final = captura en los 3 aspects, no en uno.

## 7. Modelos 3D: spec de entrega

### Escala, ejes, pivots

| Ítem | Spec | Verificación en Unity |
|---|---|---|
| Escala | **1 unidad = 1 m** — la física de Unity lo asume ("1 m in the game world = 1 unit in the imported file", manual del FBX Importer). Personaje ≈ 1.8 de alto | Importar y comparar contra un Cube (1 m³). Si no cuadra: corregir **Scale Factor / Convert Units** en el importer, JAMÁS el `localScale` del Transform |
| Ejes | Unity es **Y-up, left-handed, forward = +Z**. Blender es Z-up: exportar FBX con conversión de ejes del exporter, o activar **Bake Axis Conversion** en el importer (hornea la conversión en los vértices; desactivado, Unity compensa con rotación en el root — la clásica rotación X = -89.98 en archivos de Blender) | Instancia recién importada: rotación **(0,0,0)**, escala **(1,1,1)**, el modelo mira a +Z |
| Pivot | En el origen (0,0,0) del archivo. Personajes/edificios/árboles: en la BASE (entre los pies). Props agarrable: punto de agarre. Puerta: la bisagra. Módulos de kit: esquina o centro consistente para snapping en grilla | Colocar en Y=0: debe apoyar en el suelo sin offsets. Rotar: debe girar sobre el punto lógico |
| Formato | **FBX** (recomendación oficial; "don't use proprietary file formats in production"). Nunca `.blend`/`.max` al repo: exigen el DCC instalado en cada máquina. Alternativa oficial: glTF via package **Unity glTFast** (`com.unity.cloud.gltfast`, import/export runtime y editor, soporta URP). glTF entrega roughness (ver abajo) | El FBX abre sin warnings de import; materiales extraídos [ver: unity/assets-pipeline-git §1] |
| UVs | UV0 sin solapes para texturas; **UV2 (lightmap)** si el asset recibirá luz baked — o activar `Generate Lightmap UVs` en el importer | Lighting bake sin warnings de UV overlap [ver: unity/rendering-urp] |

### Materiales y texturas (URP Lit, metallic workflow)

Canales exactos del shader **URP Lit** (manual 6000.2) — la spec de texturas se escribe con esto:

| Mapa | Canales | Nota |
|---|---|---|
| Base Map | RGB color; A = transparencia (solo Surface Type Transparent / Alpha Clipping) | sRGB On |
| Metallic Map | Escala de grises | Solo workflow Metallic (el default) |
| **Smoothness** | Canal **A del Metallic Map** o **A del Base Map** (propiedad Smoothness Source: `Metallic Alpha` / `Albedo Alpha`) | ⚠️ URP usa **smoothness = 1 − roughness**. Substance/glTF exportan roughness: pedir al artista el preset "Unity URP (Metallic Smoothness)" o invertir el canal |
| Normal Map | Formato normal map (marcar tipo en import; sRGB lo maneja el tipo) | Tangent space, MikkTSpace [ver: unity/assets-pipeline-git §1] |
| Occlusion Map | Escala de grises | Opcional |
| Emission Map | RGB, admite HDR (>1 alimenta el Bloom) | Solo si el asset emite luz [ver: unity/rendering-urp] |

- **1 material por modelo** como objetivo (props); máximo 2-3 en hero assets. Cada material extra = draw call/estado extra y rompe el batching [ver: unity/rendimiento-unity]. Entorno: trim sheets/atlas compartidos [ver: gamedev/arte-direccion §9].
- Shader más barato que logre el look: `Unlit > Baked Lit > Simple Lit > Lit` [ver: unity/rendering-urp]. Estilizado low-poly: color por vértice o paleta-textura + Simple Lit/Unlit — sin texturas PBR que nadie verá.
- Tamaños de textura potencia de 2 (512/1024/2048); texel density consistente entre assets (declararla en la spec: p.ej. 512 px/m props, 1024 px/m hero).

### Colliders

- El FBX NO trae colliders útiles: `Generate Colliders` del importer crea MeshColliders — solo aceptable en geometría de ENTORNO estática [ver: unity/assets-pipeline-git §1].
- Objetos dinámicos: compound de primitivos (Box/Sphere/Capsule) armado en el prefab de Unity; MeshCollider convex tiene límite de 255 triángulos [ver: unity/fisica-unity].
- Si la forma exige malla de colisión custom: pedirla como mesh extra ultra-simplificado dentro del FBX (sufijo `_COL`, convención del proyecto — Unity no lo procesa solo: se referencia a mano en el MeshCollider y se desactiva su renderer).

### LODs básicos

- Naming oficial: `Nombre_LOD0` (detalle máximo), `_LOD1`, `_LOD2`… dentro del mismo FBX → **Unity crea el LOD Group automáticamente al importar** (manual "importing LOD meshes").
- Los umbrales del LOD Group son **% de la altura del objeto en pantalla** (screen relative transition height): p.ej. LOD1 al 50% = se activa cuando el objeto ocupa la mitad del alto de pantalla. Ajustar arrastrando en el componente; último nivel = Culled.
- Práctica común (no dogma oficial): 2-3 niveles + culled, reduciendo ~50% de tris por nivel; solo para props/entorno que se ven a distancias variables — un juego de cámara fija no necesita LODs.
- Spec: pedir los LODs YA nombrados en el FBX; "luego los hago yo" = nunca se hacen.

## 8. Tipografía: TMP e idiomas

TMP (integrado en `com.unity.ugui` 2.0 en Unity 6) es la única opción para texto nuevo; settings de Font Asset, atlas SDF, Static vs Dynamic y Auto Size: [ver: unity/ui-unity §6]. Aquí la spec de entrega y el multi-idioma:

**Spec de entrega de una fuente:**

| Ítem | Valor |
|---|---|
| Formato | TTF u OTF (el archivo fuente, no "la fuente instalada") |
| Licencia | Verificada para embed en juego (OFL/comercial con redistribución); guardar el archivo de licencia junto al .ttf |
| Cobertura declarada | Idiomas del juego por escrito: español = ASCII + `áéíóúüñÁÉÍÓÚÜÑ¿¡` mínimo; cada idioma extra amplía el set |
| Roles | Fuente de título + fuente de cuerpo (máx. 2-3 familias); cuerpo legible al tamaño mínimo real del juego en el device más chico |
| Números | Si hay HUD con contadores: tabular figures (ancho fijo) o monospace para que no bailen |

**Idiomas y fallbacks** (doc oficial TMP, `com.unity.ugui@2.0`):

- Cadena de búsqueda de un glifo: Font Asset del texto → sus **Fallback Font Assets** (recursivo) → Sprite Asset del texto → **fallbacks globales** de TMP Settings (recursivo) → Default Sprite Asset → Default Font Asset → carácter de "missing glyph". Detecta referencias circulares (cada asset se busca una vez).
- Latín completo: atlas Static con el character set del idioma horneado [ver: unity/ui-unity §6]. CJK (chino/japonés/coreano): el alfabeto no cabe en un atlas — repartir en varios font assets encadenados por fallback, o atlas Dynamic (población en runtime) con `Clear Dynamic Data on Build`.
- Cada fuente de fallback USADA = draw calls extra; cadena corta y todo lo previsible en el atlas principal.
- Localización de strings y flujo de idiomas del juego: [ver: narrativa-localizacion].

## 9. Checklist de import por tipo de asset

El detalle completo (valores, tablas por plataforma, Presets/AssetPostprocessor para automatizarlo) está en [ver: unity/assets-pipeline-git §1] — esto es el resumen operativo al recibir un asset:

| Asset | Los 3 checks críticos |
|---|---|
| Sprite HD | Type `Sprite (2D and UI)` · PPU global · Bilinear + compresión Normal |
| Sprite pixel art | PPU = tile · Point + Compression None + mipmaps Off · pivot Custom/Pixels |
| Sprite 9-slice | Mesh Type Full Rect · Borders definidos en Sprite Editor · atlas con Tight Packing Off |
| Textura 3D | Plataforma móvil → ASTC · sRGB Off en masks/normales · Read/Write Off |
| Modelo FBX | Escala 1 m verificada · rotación (0,0,0) al instanciar · materiales extraídos |
| Audio | [ver: unity/assets-pipeline-git §1] y [ver: unity/audio-unity] |
| Fuente | Licencia + cobertura de idioma · Font Asset Static con set completo · fallbacks configurados |

Automatizar con Preset por carpeta o AssetPostprocessor UNA vez y dejar de revisar a mano [ver: unity/assets-pipeline-git §1].

## 10. Auditar un asset recibido (runbook)

Orden fijo; un asset que falla un paso NO avanza al siguiente (se devuelve con el número del paso que falló).

**Sprites:**

1. **Archivo**: PNG con alpha real, tamaño exacto de spec, naming correcto. Animaciones: todos los frames mismo canvas y pivot.
2. **Densidad**: alto del sprite en px ÷ alto esperado en unidades = ¿PPU del proyecto? Pixel art: ¿el píxel del asset mide lo mismo que el píxel de los assets existentes?
3. **Import**: pasa por el Preset/postprocessor de su carpeta (si cae en la carpeta correcta, esto es automático).
4. **En juego**: colocarlo en la escena visual-target con la cámara REAL del juego [ver: gamedev/arte-direccion] — ¿coincide estilo, paleta y nivel de detalle? ¿se lee contra el peor fondo?
5. **Movimiento**: si anima o scrollea — ¿sin flicker ni shimmer? (pixel art: verificar con la Pixel Perfect Camera activa, Current Pixel Ratio entero).
6. **Sorting/atlas**: asignado a su Sorting Layer y su atlas; Frame Debugger confirma que batchea [ver: unity/rendering-urp].

**Modelos 3D:**

1. **Archivo**: FBX (o glTF), sin dependencias del DCC, texturas aparte en potencia de 2.
2. **Escala y ejes**: instanciar junto a un Cube de 1 m — tamaño correcto, rotación (0,0,0), escala (1,1,1), mira a +Z, apoya en Y=0 por su pivot.
3. **Presupuesto**: tris dentro del budget de su categoría; nº de materiales ≤ spec; UV2 presente si va a recibir bake.
4. **Materiales**: nada rosado; URP Lit/Simple Lit con smoothness donde toca (¿invirtió el roughness?); probar bajo la LUZ real del juego, no en un viewport neutro.
5. **LODs y colliders**: `_LOD*` presentes si la spec los pedía (LOD Group auto-creado); colliders del prefab armados con primitivos.
6. **En juego**: a la escena visual-target, con la cámara y post-proceso reales.

Validador mínimo para el paso 3 de sprites (correr tras cada tanda):

```csharp
// Editor/AuditSprites.cs — lista sprites fuera de spec en la carpeta de arte
using UnityEditor;
using UnityEngine;

public static class AuditSprites
{
    const float PPU = 100f; // el PPU global del proyecto
    [MenuItem("Tools/Audit/Sprites fuera de spec")]
    static void Run()
    {
        foreach (var guid in AssetDatabase.FindAssets("t:Texture2D", new[] { "Assets/_Game/Art" }))
        {
            var path = AssetDatabase.GUIDToAssetPath(guid);
            if (AssetImporter.GetAtPath(path) is not TextureImporter imp) continue;
            if (imp.textureType != TextureImporterType.Sprite)
                Debug.LogWarning($"{path}: no es Sprite ({imp.textureType})");
            else if (!Mathf.Approximately(imp.spritePixelsPerUnit, PPU))
                Debug.LogWarning($"{path}: PPU {imp.spritePixelsPerUnit} != {PPU}");
        }
        Debug.Log("Auditoría de sprites terminada.");
    }
}
```

## Reglas prácticas

1. Congela la spec (PPU/escala, resolución de referencia, pivots, budgets, naming) ANTES del primer asset de producción; vive en el style guide.
2. UN PPU global; todo sprite se entrega al tamaño final exacto y a esa densidad — nada de "ya lo escalas tú".
3. Calcula el orthographic size con la fórmula `altura_ref / (2 × PPU)` y documéntalo; no lo ajustes a ojo.
4. Pixel art completo o nada: PPU = tile, Point, Compression None, pivot Custom en Pixels, Pixel Perfect Camera con Asset PPU idéntico, snap grid 1/PPU.
5. Con Cinemachine + Pixel Perfect Camera: extensión Cinemachine Pixel Perfect en cada cámara virtual, siempre.
6. 9-slice: Full Rect + Borders en Sprite Editor; redimensiona con `SpriteRenderer.size` o el Rect tool, jamás con `localScale`.
7. Spec 9-slice al artista: esquinas detalladas, bordes seamless, centro liso, grosor de borde en px documentado.
8. Sorting Layers definidos el día 1 con la categoría de cada asset documentada; sprites sueltos al proyecto, el atlas lo arma Unity.
9. Móvil: fija un eje de cámara, sangra los fondos hasta el aspect extremo (4:3 ↔ 21:9), HUD dentro del SafeArea; verifica en 16:9, 20:9 y 4:3 con Device Simulator.
10. 3D: 1 unidad = 1 m verificado contra un Cube; escala se corrige en el importer (Scale Factor/Convert Units), nunca en el Transform.
11. Criterio de aceptación de ejes: instancia con rotación (0,0,0) y escala (1,1,1) mirando a +Z, apoyada en Y=0 por su pivot.
12. FBX al repo, nunca .blend/.max; materiales extraídos del FBX una sola vez.
13. Spec de texturas en canales exactos de URP Lit; si el artista entrega roughness (Substance/glTF), se invierte a smoothness en el alpha — acordarlo ANTES de la primera entrega.
14. 1 material por prop como objetivo; trim sheets para entorno; el shader más barato que logre el look.
15. LODs nombrados `_LOD0..n` dentro del FBX (Unity crea el LOD Group solo); colliders dinámicos = primitivos en el prefab, no MeshCollider.
16. Fuentes: TTF/OTF con licencia archivada y cobertura de idioma declarada; atlas Static con el set completo del idioma; cadena de fallbacks corta.
17. Todo asset se aprueba EN el juego: escena visual-target, cámara real, luz y post-proceso reales, en movimiento — nunca en el visor de la herramienta.
18. Automatiza el import (Preset por carpeta / AssetPostprocessor) y la auditoría (script tipo AuditSprites); revisar a mano no escala.
19. Asset que falla la auditoría se devuelve con el paso exacto que falló; no se "arregla un poquito" en Unity — eso crea drift permanente.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Cada asset llega con su propio PPU/escala y "se ajusta" con localScale | PPU/escala global en la spec; corregir en importer; el validador lo detecta |
| Pixel art borroso o que "nada" al moverse | Falta la tríada: Point + Compression None + Pixel Perfect Camera con Asset PPU correcto y pivots en píxel |
| Pixel Perfect Camera + Cinemachine dando tirones de zoom | Ambos pelean el orthographic size: extensión Cinemachine Pixel Perfect |
| Panel 9-slice con esquinas deformadas | Escalaron con localScale o Mesh Type quedó Tight; usar SpriteRenderer.size + Full Rect |
| Collider de un 9-slice tileado se comporta raro | Solo BoxCollider2D/PolygonCollider2D lo soportan y Auto Tiling puede meter aristas extra; verificar la forma tras redimensionar |
| UI perfecta en el editor 16:9, rota en 20:9/iPad | Se diseñó a UNA resolución: fondo con sangrado + SafeArea + Device Simulator en 3 aspects |
| Fondo estirado para llenar un aspect distinto | Los fondos se sangran (se recortan), no se deforman; entregar sobredimensionados |
| Modelo que llega gigante o miniatura (cm/pulgadas del DCC) | Convert Units/Scale Factor en el importer; test del Cube de 1 m en la auditoría |
| Modelo de Blender con rotación X = -89.98 en el root | Ejes Z-up sin convertir: exportar FBX con conversión o Bake Axis Conversion; el criterio es rot (0,0,0) |
| Pivot en el centro del modelo: edificios flotando, puertas girando por el medio | Pivot por categoría en la spec (base/bisagra/agarre); se audita apoyando en Y=0 y rotando |
| Material plateado/lavado: "el metallic se ve raro" | Entregaron roughness donde URP espera smoothness (1−roughness en el alpha); invertir canal o re-export con preset Unity |
| Materiales rosados | Shader Built-in en proyecto URP → Render Pipeline Converter [ver: unity/rendering-urp] |
| Hero prop con 6 materiales "para organizar las texturas" | Presupuesto de materiales en la spec (1 por prop); atlas/trim sheets |
| Tofu (□) en áéíóúñ¿¡ o en el idioma nuevo | Character set incompleto en el Font Asset estático; hornear el rango del idioma y probar con textos reales [ver: unity/ui-unity] |
| CJK metido a la fuerza en un atlas 1024 | No cabe: multi-asset por fallback o atlas Dynamic con Clear Dynamic Data on Build |
| Asset aprobado viendo el archivo suelto, desentona en el juego | Aprobación solo en la escena visual-target con cámara/luz/post reales [ver: gamedev/arte-direccion] |
| "Los LODs los agrego después" | Nunca llegan: exigir `_LOD*` en el FBX de entrega; Unity monta el LOD Group gratis en import |

## Fuentes

- 2D Pixel Perfect Camera (intro + component reference + Prepare your sprites) — Unity Manual 6000.2, sección URP (`urp/2d-pixelperfect-*.html`) — propiedades exactas (Asset PPU, Reference Resolution, Crop Frame None/Pillarbox/Letterbox/Windowbox/Stretch Fill, Grid Snapping Pixel Snapping/Upscale Render Texture, Filter Mode Retro AA/Point) y requisitos de sprites (Point, Compression None, pivot Custom/Pixels, grid 1/PPU).
- 2D Pixel Perfect package 5.0 — docs.unity3d.com/Packages/com.unity.2d.pixel-perfect@5.0 — tabla de propiedades de la variante Built-in y la solución oficial al conflicto con Cinemachine (extensión Cinemachine Pixel Perfect).
- 9-slicing sprites — Unity Manual 6000.2 (`sprite/9-slice/9-slicing.html`) — comportamiento de las 9 zonas y límites de colliders (solo BoxCollider2D/PolygonCollider2D; no editables en Sliced/Tiled; aristas extra con Auto Tiling).
- Model tab (FBX Importer) — Unity Manual 6000.2 (`FBXImporter-Model.html`) — "1 m = 1 unit" esperado por física, Convert Units, Bake Axis Conversion (hornear vs compensar en el root), Generate Lightmap UVs.
- Model file formats — Unity Manual 6000.2 (`3D-formats.html`) — FBX como formato interno recomendado; formatos propietarios (.blend/.max) desaconsejados en producción.
- Importing LOD meshes — Unity Manual 6000.2 (`importing-lod-meshes.html`) — convención `_LOD0..n` y creación automática del LOD Group al importar.
- LOD Group component — Unity Manual 6000.2 (`class-LODGroup.html`) — umbrales como % de altura del objeto en pantalla, ajuste de transiciones, Recalculate Bounds/Lightmap Scale.
- Lit Shader (URP) — Unity Manual 6000.2 (`urp/lit-shader.html`) — workflow Metallic/Specular y canales exactos: Metallic grayscale, Smoothness Source = Metallic Alpha / Albedo Alpha, Base/Normal/Occlusion/Emission.
- Font Asset Fallback — docs TMP en com.unity.ugui@2.0 — orden de búsqueda completo de la cadena de fallbacks (local → sprite asset → global → defaults), detección de referencias circulares, multi-asset para CJK.
- Unity glTFast — docs.unity3d.com/Packages/com.unity.cloud.gltfast@6.13 — package oficial `com.unity.cloud.gltfast`: import/export glTF 2.0 en runtime y editor, soporte URP/HDRP/Built-in.
- Base sintetizada: [ver: gamedev/arte-direccion] (style guide, visual target, pipelines 2D/3D, readability), [ver: unity/assets-pipeline-git] (import settings completos, Sprite Atlas, Presets/AssetPostprocessor, naming), [ver: unity/rendering-urp] (sorting 2D, materiales/shaders URP, Cinemachine), [ver: unity/ui-unity] (Canvas Scaler, safe area, TMP a fondo), [ver: unity/fisica-unity] (colliders, convex ≤255 tris).
