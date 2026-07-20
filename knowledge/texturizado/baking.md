# Baking de mapas: del high-poly a las texturas

> **Cuando cargar este archivo:** al ejecutar un bake concreto (en Blender 5.2, Marmoset Toolbag o Substance Painter) y necesitar los settings exactos; al decidir qué mapas hornear para el texturizado; al configurar el color space / bit-depth de los archivos de salida; al sincronizar tangent space Blender↔Unity; o al bakear máscaras (AO/curvature/thickness) desde la propia low sin high-poly. La TEORÍA del bake — qué guarda un normal map, cage promediado vs explícito, causa raíz de waviness/skew, hard edge = UV seam, tangent space como encoding, floaters, mid-poly como alternativa — ya está en [ver: modelado/high-to-low] y NO se repite aquí; este archivo es el manual operativo por herramienta y el puente al texturizado y a Unity.

## 1. Dónde encaja el bake en el pipeline de textura

El bake convierte dos modelos (high + low con UVs) en un **set de imágenes** que el texturizado consume: unas van directas al material (normal), otras son **materia prima para máscaras** (AO, curvature, position, thickness, ID). Orden real:

```
high-poly + low-poly (UVs, triangulado)  →  BAKE  →  set de mapas
   →  texturizado por máscaras (Substance / Blender)  →  export  →  Unity
```

- Prerrequisitos que este archivo asume resueltos: UVs sin overlaps en 0-1 y padding [ver: uv-unwrapping]; hard edge = UV seam, triangulación, espejos fuera de 0-1, cage promediado [ver: modelado/high-to-low §3–§4].
- Qué hace el texturizado con cada mapa: [ver: texturizado-blender], [ver: substance-y-alternativas]. Teoría PBR de los canales: [ver: pbr-teoria].
- El bake es un **loop de diagnóstico**, no un botón: bakes de prueba a baja resolución/samples, iterar, full quality al final ([polycount, Texture Baking](http://wiki.polycount.com/wiki/Texture_Baking)).

## 2. El set de mapas: qué se bakea y qué hace en el texturizado

Del mismo par high/low salen todos. La columna "consumo" es la razón de existir de cada uno en la etapa de textura (mask generators / smart materials).

| Mapa | Qué guarda | Consumo en texturizado | Color space salida |
|---|---|---|---|
| **Normal (tangent)** | Dirección de superficie por píxel | Va DIRECTO al material (no es máscara) | Non-Color / Normal map |
| **AO** | Oclusión de luz ambiente | Máscara de mugre/polvo en cavidades; multiplica el ambiente (SEPARADO del albedo) | Non-Color / linear |
| **Curvature** | Convexidad (bordes) + concavidad (grietas) | LA máscara reina: edge-wear en convexo, dirt en cóncavo | Non-Color / linear |
| **Position (gradient)** | XYZ del mesh → RGB | Gradientes por altura (polvo arriba, humedad abajo) | Non-Color / linear |
| **Thickness (transmission)** | Grosor local (fino = claro) | Máscara de SSS (orejas, tela) y desgaste en zonas finas | Non-Color / linear |
| **ID / Material mask** | Un color plano por material del high | Selección instantánea de zonas ("todo lo rojo = goma") | sRGB (se lee como color) |
| **Height** | Distancia low↔high, grises | Blends por altura, parallax, detalle fino | Non-Color / 16-bit |
| **Bent normals** | Normales con AO integrado | Iluminación ambiente rica en shaders que lo soporten | Non-Color |

Detalle de para-qué-sirve cada uno y sus trampas (floaters rompen height/position, AO en dos pases, AO de piezas que animan): [ver: modelado/high-to-low §6]. El **base color / albedo** no se bakea del high (se pinta en el texturizado); si acaso se transfiere de un sculpt con polypaint. Cómo cada máscara alimenta un smart material: [ver: substance-y-alternativas].

## 3. Bake en Blender 5.2 (Cycles) — settings exactos

Motor **Cycles** obligatorio (EEVEE no bakea). Panel **Properties ‣ Render ‣ Bake** (todo verificado contra el manual 5.2).

### Setup mínimo

1. `Render Engine = Cycles`.
2. La low-poly necesita **UV map** y, en su material, un **Image Texture node** con una imagen nueva **seleccionado y activo** — es el target del bake.
3. La imagen target: para normal/AO/máscaras poner su **Color Space = Non-Color** (si no, Cycles aplica gamma y corrompe el dato).
4. Seleccionar **primero el high, luego el low** (el low queda como objeto activo) y activar **Selected to Active**.

### Panel Bake — campos y valores

| Campo | Valores / regla | Nota (manual 5.2) |
|---|---|---|
| **Bake Type** | `Combined · Ambient Occlusion · Shadow · Position · Normal · UV · Roughness · Emit · Environment · Diffuse · Glossy · Transmission` | ⚠️ NO existe curvature, thickness, ID ni bent normals nativos (§5) |
| **Selected to Active** | On | Rayos desde el low hacia adentro, hacia el high |
| **Max Ray Distance** | Distancia del raycast hacia adentro | Solo disponible **sin** cage |
| **Cage** | On (recomendado) | Copia inflada (ballooned) del low; sin cage los rayos siguen las normales del low → glitches en los bordes |
| **Cage Object** | Malla-cage manual (opcional) | Debe tener **misma topología**: mismo nº de caras y mismo orden de caras que el low |
| **Cage Extrusion** | Distancia del raycast con cage | La copia extruida ignora Edge Split; evitar hard splits (rompen las normales del cage) |
| **Normal ‣ Space** | `Tangent` (default) / `Object` | Tangent para todo lo que deforma y para reuso |
| **Normal ‣ Swizzle R/G/B** | Default `+X / +Y / +Z` | +Y = **OpenGL/Y+** = lo que espera Unity (§6) |
| **Margin ‣ Type** | `Adjacent Faces` (preferido) / `Extend` | Adjacent Faces rellena cruzando seams; Extend estira el borde |
| **Margin ‣ Size** | px según resolución (tabla [ver: modelado/high-to-low §4]) | Evita seams por mip-mapping |
| **Output ‣ Target** | `Image Textures` / `Active Color Attribute` | Image Textures = al nodo Image Texture activo |
| **Clear Image** | On en la 1ª pasada | Limpia antes de hornear |

- **Sin high-poly aparte** — detalle esculpido en un **Multiresolution**: panel **Bake from Multires** (On). Compara `Viewport Levels` (= low) contra `Render Levels` (= high) y hornea la diferencia. Bake Type aquí: `Normals / Displacement / Vector Displacement`. Es el camino directo desde un sculpt sobre malla limpia [ver: blender/sculpt].
- **Memoria**: cada objeto-fuente tiene footprint fijo de CPU; con muchos highs, **Join** antes de bakear para no crashear (manual).
- El visor de Blender **no** valida tangent space del engine: el mapa se aprueba en Unity [ver: texturas-a-unity].

### bpy — automatizar el bake (firmas verificadas 5.2)

```python
import bpy
scene = bpy.context.scene
scene.render.engine = 'CYCLES'

bake = scene.render.bake              # bpy.types.BakeSettings
bake.use_selected_to_active = True
bake.use_cage        = True
bake.cage_extrusion  = 0.05           # unidades de objeto; sube si el high asoma
bake.margin_type     = 'ADJACENT_FACES'
bake.margin          = 16             # px (2048 → 16)
bake.normal_space    = 'TANGENT'
bake.normal_r, bake.normal_g, bake.normal_b = 'POS_X', 'POS_Y', 'POS_Z'  # OpenGL/Unity
bake.use_clear       = True
bake.target          = 'IMAGE_TEXTURES'

# high seleccionado + low activo, con su Image Texture (Non-Color) activo:
bpy.ops.object.bake(type='NORMAL')    # 'AO', 'POSITION', 'DIFFUSE', 'ROUGHNESS'...
```

Operador completo (defaults reales): `bpy.ops.object.bake(type='COMBINED', width=512, height=512, margin=16, margin_type='EXTEND', use_selected_to_active=False, max_ray_distance=0.0, cage_extrusion=0.0, cage_object='', normal_space='TANGENT', normal_r='POS_X', normal_g='POS_Y', normal_b='POS_Z', target='IMAGE_TEXTURES', use_clear=False, use_cage=False, uv_layer='')`. Guardar la imagen tras bakear: `img.filepath_raw=...; img.file_format='PNG'; img.save()`. Los `bpy.ops.object.bake` exigen que el nodo Image Texture esté activo en el material — en headless preparar el node tree por API [ver: blender/bpy-scripting].

## 4. Bake dedicado: Marmoset Toolbag y Substance Painter

### Por qué muchos NO usan el bake de Blender

| Razón | Blender Cycles | Marmoset / Substance |
|---|---|---|
| **Mapas que faltan** | Sin curvature/thickness/ID/bent nativos (§3) | Todos de fábrica, un click |
| Velocidad | CPU/GPU vía render de rayos, sin preview interactivo | **GPU**, rebake solo del área tocada, preview en tiempo real (Marmoset) |
| Corrección de errores | Rehacer geometría o cage manual | **Skew/offset painting** en el viewport (Marmoset) → arregla skew sin tocar el low |
| Matching high/low | Selected-to-Active + join/explode manual | **Bake Groups / Match by Name** automáticos |
| Iteración de textura | — | Substance textura EN LA MISMA app tras bakear |

Regla: assets sueltos o pipeline gratis → Blender alcanza para normal + AO + position. Producción con muchos props, hard-surface con skew, o texturizado en Substance → el baker dedicado se paga solo (curvature/thickness/ID + skew painting ahorran horas).

### Marmoset Toolbag 5.02 — flujo ([marmoset.co, Baking Tutorial](https://marmoset.co/posts/toolbag-baking-tutorial/))

- **Quick Loader** (icono de árbol en Geometry): lee los nombres del archivo y arma **Bake Groups** solo. Sintaxis `<nombre>_<high/low>_<variación>`, **no** case-sensitive: `Myobject1_high`, `Myobject1_high_bolt`, `Myobject1_low` → grupo `Myobject1`. Todo lo que comparte `<nombre>` cae en el mismo grupo → sin explode.
- **Geometry tab**: `Smooth Cage` (promedia normales del cage — esencial, sin gaps en hard edges) · `Ignore Back Faces` · `Ignore Transforms` (asume todo en 0,0,0 — permite mover el low al lado para preview) · `Use Hidden Meshes`.
- **Cage/skew por bake group**: `Paint Offset` (Min/Max = negro/blanco; `Estimate Offset` autocalcula) y `Paint Skew` (negro = corrección total, blanco = ninguna; mezcla per-pixel normales de cara vs cage). Mapas fijos 512×512, se retienen si las UVs no cambian.
- **Output**: `Size` hasta 8192² · `Samples` = calidad de AA · `Format` = bit-depth · `Multi-Layer PSD` (outputs en un PSD con máscaras por material) · `Padding` `none/moderate/extreme` (auto, sin valor px explícito).
- **Normals**: tangent space; flip R/G/B; toggle dithering. **AO**: `Ignore Groups` (echa AO entre bake groups para asentar las piezas) + `Exclude When Ignoring Groups` en el Low de las piezas que animan (cargador, cerrojo) para que no reciban AO horneado de una pose.
- **Tangent basis**: usa el del mesh (`Tangent Space` dropdown, o `Edit ‣ Preferences ‣ Content ‣ Default Tangent Space`). Si no sabes cuál: **Mikk/xNormal** (lo que usan Unity y Unreal). Handedness override = `Flip Y`.

### Substance 3D Painter 2026 — Bake Mesh Maps

- Baker integrado (menú **Texture Set Settings ‣ Bake Mesh Maps**, o modo Baking). Mesh maps que hornea: **Normal, World Space Normal, ID, Ambient Occlusion, Curvature, Position, Thickness** — exactamente los que alimentan sus generators/smart materials.
- **Match by Name**: mismo principio que los Bake Groups; sufijos `_low` / `_high` por objeto evitan proyección cruzada ([polycount confirma "Substance 3D Painter has Match by Name"](http://wiki.polycount.com/wiki/Texture_Baking)).
- Parámetros comunes del baker (según docs Adobe Substance; **no re-verificados en vivo 2026-07-20**, Adobe bloqueó el fetch — confirmar nombres exactos en la doc actual): `Output Size`, `Dilation Width` (= padding), `Antialiasing/Subsampling` (None/2×2/4×4/8×8), `Match` (Always / By Mesh Name), `High Definition Meshes`, `Max Frontal Distance` / `Max Rear Distance` (= el cage por distancia), `Average Normals`, `Ignore Backface`, `Self Occlusion`.
- Ventaja real: bakeas y **texturas en la misma app** sin exportar el set de mapas a mano.

### Explode: cuando el matching por nombre no basta

Bake Groups / Match by Name resuelven la proyección cruzada en el 90% de los casos. El **explode** sigue siendo la red de seguridad para intersecciones que el matching no aísla (piezas del MISMO grupo que se tocan, o herramientas sin matching):

1. Separar físicamente las piezas del high **y** del low con **la misma traslación** (para que sigan alineadas).
2. Bakear.
3. Devolver las piezas a su sitio (keyframe del explode para revertir en un click; hay scripts dedicados).
4. Convención de nombres para los scripts: prefijos idénticos por pieza (`LOW_x` / `HIGH_x` / `CAGE_x`).

En Blender el explode es manual (mover objetos + bakear + deshacer); Marmoset lo evita con `Ignore Transforms` + Bake Groups (mueves el low al lado y sigue bakeando contra su high). Detalle y precedentes: [ver: modelado/high-to-low §4].

### Precios (verificados 2026-07-20)

| Herramienta | Precio | Fuente |
|---|---|---|
| **Blender** | Gratis (GPL) | blender.org |
| **Marmoset Toolbag 5.02 — Individual** | Suscripción **$18.99/mes** (−12% anual) · Perpetua **$399** (solo updates 5.x) | [marmoset.co](https://marmoset.co/toolbag/) |
| **Marmoset — Studio** | Suscripción **$49.99/seat/mes** · Perpetua **$1,299/seat** | [marmoset.co](https://marmoset.co/toolbag/) |
| **Marmoset — Academic** | **$119.99/seat/año** | [marmoset.co](https://marmoset.co/toolbag/) |
| **Substance 3D Painter** | Suscripción Adobe (plan Texturing) · perpetua en Steam | ⚠️ NO verificado en vivo 2026-07-20 (Adobe bloqueó fetch) — confirmar en adobe.com |
| **xNormal** | Históricamente gratis | ⚠️ no re-verificado hoy |

## 5. Mapas que Blender Cycles NO hornea nativo (y el workaround)

El Bake Type de Cycles (§3) no incluye curvature, thickness, ID ni bent normals. Es LA razón técnica de peso para ir a Marmoset/Substance. Si te quedas en Blender:

| Mapa faltante | Workaround en Blender |
|---|---|
| **ID / material mask** | Asignar un material de **Emission** (o Diffuse) de color plano por zona en el high → Bake Type `Emit` (o `Diffuse` solo Color) |
| **Curvature** | Nodo **Geometry ‣ Pointiness** → ColorRamp → Emission, y bakear `Emit`; o generarlo en Substance desde el normal ya bakeado |
| **Thickness** | Sin pass nativo — bakear en Marmoset/Substance/xNormal, o aproximar con AO invertido de normales interiores |
| **Bent normals** | Sin pass nativo — baker dedicado |

Substance además **genera** curvature/AO desde el normal + world-space normal ya horneados, así que un normal + position + AO desde Blender suele bastar como entrada.

## 6. Tangent space sincronizado: Blender → Unity

La teoría (encoding que exige la inversa exacta, MikkTSpace) está en [ver: modelado/high-to-low §2]. Lo operativo Blender↔Unity:

| Punto | Blender 5.2 | Unity 6 / URP |
|---|---|---|
| Tangent basis | **MikkTSpace** (desde 2.57) | **MikkTSpace** — coinciden ✓ |
| Handedness (verde) | Bakea **Y+ / OpenGL** por default (`normal_g = POS_Y`) | Unity espera **Y+** → **NO flipear verde** Blender→Unity |
| Tangentes en el archivo | Exportar FBX/glTF con tangentes | Unity las lee; triangular ANTES de exportar |
| Import del normal | — | Texture Type = **Normal Map** (sRGB lo maneja el tipo); opción **Flip Green Channel** si hiciera falta |

- **Blender→Unreal** en cambio SÍ exige **Y−** (flipear verde) — por eso el swizzle importa. Tabla de handedness por engine: [ver: modelado/high-to-low §2].
- Unity puede **generar** un normal desde un heightmap gris en import (`Create From Grayscale` + `Bumpiness` + Filtering `Sharp/Smooth`), pero eso es para bump legacy, no sustituye un bake real.
- El resto del handoff (escala, ejes, materiales URP): [ver: pipeline/arte-a-unity §7], [ver: texturas-a-unity].

## 7. Bake sin high-poly: máscaras desde la propia low

Para texturizar un asset **mid-poly o sin high** (hard-surface con weighted normals, low-poly estilizado) igual se hornean mapas de utilidad **desde la misma malla** — son la entrada de los generators:

- **En Substance**: al bakear con "Use Low Poly Mesh as High Poly" (o sin high asignado), calcula **AO, Curvature, Thickness, Position** desde la geometría de la propia low. Da los edge-wear y dirt masks sin duplicar modelo.
- **En Blender**: `Bake Type = Ambient Occlusion` con Selected-to-Active **apagado** hornea el AO de la malla sobre sí misma; curvature vía Pointiness (§5).
- Es el flujo estándar para el mid-poly + weighted normals (los mapas de utilidad salen del propio mid, sin bake de normales) [ver: modelado/high-to-low §7] y para estilizado [ver: estilizado-texturas].
- Trim sheets/atlas: el detalle se hornea UNA vez y se reusa; el bake de la tira es normal+AO como cualquier otro [ver: atlas-trim-optimizacion].

## 8. Salida: color space, bit-depth y resolución de los archivos

Lo que rompe el material en Unity casi siempre es el **color space** del archivo, no el contenido:

| Mapa | Bit-depth bake | Color space del archivo | Import Unity |
|---|---|---|---|
| Base color / Albedo | 8-bit | **sRGB** | Default, sRGB **On** |
| ID / material mask | 8-bit | sRGB (se lee como color) | Default, sRGB On |
| **Normal** | 8-bit (16 si hay banding) | **Non-Color / linear** | **Normal Map** |
| AO · Curvature · Metallic · Roughness · Thickness · Position | 8-bit | **Non-Color / linear** | Default, sRGB **Off** |
| Height / Displacement | **16-bit** | Non-Color / linear | sRGB Off |

- Bakear a **16-bit y bajar a 8 con dithering** mata el banding en superficies suaves [ver: modelado/high-to-low §4].
- **URP metallic workflow**: Metallic (grises) con **Smoothness en su canal Alpha** (`Smoothness Source = Metallic Alpha`, el default), Occlusion aparte. URP usa **smoothness = 1 − roughness**: si el baker/Substance da roughness, **invertir** o exportar con preset Unity. Se puede empacar Metallic+Occlusion+Smoothness en una RGBA (channel-packed) [ver: pipeline/arte-a-unity §7], [ver: texturas-a-unity].
- Resoluciones potencia de 2; texel density consistente con el resto del asset [ver: atlas-trim-optimizacion].

## 9. Errores de bake: dónde vive el diagnóstico

La tabla completa de síntoma→causa→fix (waviness, skew, seams en hard edges, luz invertida, contaminación entre piezas, errores en X, banding, seams de lejos) está en [ver: modelado/high-to-low §5] — **casi todo error de bake es geometría del low, no settings**. Lo específico de la etapa de textura/herramienta:

| Síntoma (lado textura) | Causa | Fix |
|---|---|---|
| Normal "lavado"/plano tras bakear en Blender | Image target en sRGB en vez de Non-Color | Color Space = Non-Color en la imagen antes de bakear (§3) |
| Máscara de curvature/AO da tono raro en el material | El archivo se importó como sRGB | sRGB Off en Unity; Non-Color al bakear (§8) |
| Detalles al revés según ángulo en Unity | Verde flipeado (bakeaste para Unreal/Y−) | Blender bakea Y+ por default; para Unity NO flipear (§6) |
| Skew en Blender que no puedes quitar sin rehacer geo | Blender no tiene skew painting | Loops de soporte en el low, o pasar a Marmoset (`Paint Skew`) (§4) |
| Falta curvature/thickness/ID y no aparecen en Blender | Cycles no los hornea | Workaround §5 o baker dedicado |
| Seam de mip a distancia aunque el bake "está bien" | Margin/padding corto para los mips | Adjacent Faces + tamaño por resolución (§3) |
| AO con sombra de una pieza que animará | Falta excluir del AO cruzado | Marmoset `Exclude When Ignoring Groups`; en Blender bakear esa pieza aparte |

## Reglas prácticas

1. Bakea con Cycles (EEVEE no hornea); la imagen target del normal/AO/máscaras SIEMPRE en Color Space **Non-Color** antes de bakear.
2. Selected to Active = high seleccionado, low activo con su Image Texture node activo; con muchos highs, **Join** para no quedarte sin memoria.
3. Usa **Cage** (promediado/Smooth) siempre; sin cage los rayos siguen las normales del low y dan glitches en los bordes.
4. Cage Object manual = misma topología (nº y orden de caras) que el low; si no, deforma la proyección.
5. Margin **Adjacent Faces** + tamaño por resolución (16px@2048); nunca dejes padding corto o saldrán seams de lejos.
6. Blender bakea **Y+ / OpenGL** por default = lo que espera Unity: **no flipees el verde** Blender→Unity; sí para Unreal (Y−).
7. Triangula y exporta con tangentes (FBX/glTF) ANTES de bakear; no toques las UVs después del bake.
8. Recuerda que Cycles NO hornea curvature, thickness, ID ni bent normals: workaround (Pointiness/Emit por color) o baker dedicado.
9. Nombra por convención `pieza_high` / `pieza_low` desde el DCC: Quick Loader (Marmoset) y Match by Name (Substance) arman los grupos solos y evitan el explode.
10. En Marmoset arregla skew/offset **pintando en el viewport** (per bake group), no rehaciendo el cage a mano.
11. AO: `Ignore Groups` para asentar piezas, pero **excluye** las que animan (cargador, cerrojo) o quedan sombras de una pose.
12. Bakea a 16-bit y baja a 8 con dithering; height/displacement **siempre 16-bit**.
13. Cada mapa con su color space de salida (tabla §8): normal/AO/curvature/metallic/roughness = linear; albedo/ID = sRGB.
14. URP: smoothness = 1 − roughness en el **Alpha del Metallic** (Metallic Alpha); invierte el roughness de Substance o usa el preset Unity.
15. Sin high-poly: hornea AO/curvature/thickness desde la propia low (Substance "Use Low as High"; Blender AO sin Selected-to-Active) para tener máscaras de wear/dirt.
16. Bakes de prueba a baja res/samples, iterar, full quality al final; el bake es un loop, no un click.
17. Aprueba el mapa **en Unity** con la luz del juego, no en el visor del baker (no usa tu tangent space ni tus mips).
18. Guarda el .blend/scene del high por separado: es tu fuente de re-bakes futuros.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Normal bakeado en Blender sale plano/lavado | La imagen target estaba en sRGB: Color Space = Non-Color antes de bakear |
| Máscara (AO/curvature) con tono raro en el material | Se importó como sRGB: sRGB Off en Unity y Non-Color al hornear |
| Esperar curvature/thickness/ID del Bake Type de Cycles | No existen nativos: Pointiness→Emit / colores por material→Emit, o Marmoset/Substance |
| Flipear el verde "por si acaso" al ir a Unity | Blender ya bakea Y+ = Unity; flipear rompe la luz. El flip es para Unreal |
| Subir Max Ray Distance "hasta que funcione" contra la contaminación entre piezas | Bake Groups / Match by Name / explode — no la distancia |
| Cage Object con topología distinta al low | Mismo nº y orden de caras; si no, la proyección se deforma |
| Pintar el skew en Photoshop o deformar el cage a mano | Skew painting de Marmoset (no destructivo) o loops de soporte en el low [ver: modelado/high-to-low §5] |
| Roughness de Substance metido tal cual en URP | URP usa smoothness = 1 − roughness: invertir o preset Unity |
| Aprobar el bake mirando la imagen 2D | Sobre el modelo, en Unity, con luz/cámara reales |
| Bakear medio modelo espejado "para ahorrar" | Modelo completo con espejos offseteados 1 unidad UV [ver: modelado/high-to-low §4] |
| Pagar Marmoset/Substance para un prop suelto | Blender alcanza para normal+AO+position; el dedicado se paga con volumen y skew/curvature |

## Fuentes

- **Render Baking (Cycles)** — [Blender 5.2 LTS Manual](https://docs.blender.org/manual/en/latest/render/cycles/baking.html) — Blender Foundation — setup (UV + Image Texture activo), Bake Types exactos (Combined/AO/Shadow/Position/Normal/UV/Roughness/Emit/Environment/Diffuse/Glossy/Transmission), Bake from Multires (Viewport=low / Render=high), Selected to Active, Cage/Cage Object/Cage Extrusion/Max Ray Distance, Normal Space Tangent/Object + Swizzle R/G/B, Margin Extend/Adjacent Faces, Clear Image. Verificado 2026-07-20.
- **bpy.types.BakeSettings / bpy.ops.object.bake** — [Blender Python API (current)](https://docs.blender.org/api/current/bpy.types.BakeSettings.html) — Blender Foundation — nombres y defaults exactos de propiedades (`use_selected_to_active`, `use_cage`, `cage_extrusion`, `max_ray_distance`, `margin`, `margin_type`, `normal_space`, `normal_r/g/b` default POS_X/POS_Y/POS_Z, `target`, `use_clear`) y firma del operador. Verificado 2026-07-20.
- **The Toolbag Baking Tutorial** — [marmoset.co](https://marmoset.co/posts/toolbag-baking-tutorial/) — Marmoset — GPU/rebake por área, Bake Groups + Quick Loader (`_high`/`_low`/variación, case-insensitive), Smooth Cage / Ignore Back Faces / Ignore Transforms, offset & skew painting (512², per group), map types (Normal, Height inner/outer, Position, Curvature, Concavity, Thickness, Bent Normals ±object, AO con Ignore/Exclude Groups, Material ID, Wireframe), tangent basis Mikk/xNormal, Flip Y, floaters, triangulación. Verificado 2026-07-20.
- **Marmoset Toolbag** — [marmoset.co/toolbag](https://marmoset.co/toolbag/) — Marmoset — versión 5.02 y precios (Individual $18.99/mes o $399 perpetua; Studio $49.99/seat/mes o $1,299/seat; Academic $119.99/seat/año). Verificado 2026-07-20.
- **Normal Map texture Import Settings** — [Unity Manual 6000.2](https://docs.unity3d.com/6000.2/Documentation/Manual/texture-type-normal-map.html) — Unity — Create From Grayscale + Bumpiness + Filtering Sharp/Smooth, Flip Green (Y) channel, Y+ esperado. Verificado 2026-07-20.
- **Lit Shader (URP)** — [Unity Manual 6000.2](https://docs.unity3d.com/6000.2/Documentation/Manual/urp/lit-shader.html) — Unity — canales exactos: Metallic Map (grises), Smoothness Source = Metallic Alpha (default) / Albedo Alpha, Normal Map, Occlusion, Emission, y textura RGBA channel-packed para metallic/smoothness/occlusion. Verificado 2026-07-20.
- **Texture Baking** — [polycount wiki](http://wiki.polycount.com/wiki/Texture_Baking) — raycast low→high, triangular antes de espejar, overlaps/espejos fuera de 0-1 (1 unidad), no cambiar UVs post-bake, anti-aliasing, 16-bit, edge padding, explode, y confirmación de que Marmoset usa Bake Groups / Substance usa Match by Name / 3ds Max Material ID. Verificado 2026-07-20.
- **Bases sintetizadas (no repetidas aquí):** [ver: modelado/high-to-low] — teoría del normal map, cage promediado vs explícito, causa raíz de waviness/skew, hard edge = UV seam, tangent space como encoding, floaters, mid-poly, height/displacement, tabla completa de diagnóstico y de qué-se-bakea; [ver: blender/sculpt] — Multires y Decimate como par high/low para bake; [ver: pipeline/arte-a-unity] — escala/ejes, URP Lit, smoothness = 1 − roughness, import de normal.
