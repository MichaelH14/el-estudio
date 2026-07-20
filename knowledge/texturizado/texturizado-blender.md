# Texturizado en Blender: pintar, procedural y hornear a mapas

> **Cuando cargar este archivo:** al texturizar un asset de juego DENTRO de Blender (sin Substance) — pintar directo sobre el modelo en Texture Paint, generar textura con Shader Nodes procedurales, dirigir wear/dirt con máscaras de geometría (AO/curvature/pointiness), y hornear todo ese árbol de nodos a mapas de imagen para Unity. Es el CÓMO operativo del toolset de Blender: qué nodo, qué operador, qué setting. La teoría PBR vive en [ver: pbr-teoria]; el bake high→low, cage y mesh maps genéricos en [ver: baking]; los UV en [ver: uv-unwrapping]; la decisión de herramienta y el flujo Substance en [ver: substance-y-alternativas]; el hand-painted estilizado en [ver: estilizado-texturas]; la entrega/compresión a Unity en [ver: texturas-a-unity] y [ver: atlas-trim-optimizacion].

Versión de referencia: **Blender 5.2 LTS**. ⚠️ **Nota de verificación honesta:** en esta sesión `docs.blender.org` bloqueó el fetch (HTTP 403), igual que en la auditoría de [ver: blender/geometry-nodes]. Los operadores y settings de Blender de este archivo vienen de conocimiento de manual + API bpy (estables desde 3.x/4.x), **no re-verificados contra la fuente en vivo hoy** — donde algo depende de versión reciente se marca. Lo verificado hoy contra fuente web es el lado Unity/PBR (URP Lit, import de texturas, normal maps, formatos de compresión, teoría PBR — ver Fuentes). Antes de confiar en un nombre exacto de socket/enum en la sesión real, listarlo por bpy (`dir(nodo.inputs)`, etc.).

## 1. Los cuatro caminos de textura en Blender (mapa mental)

Blender puede producir la textura de un asset por cuatro vías, combinables. Todas terminan igual: **un mapa de imagen conectado al Principled BSDF, que se hornea y se exporta**. Unity no recibe nodos ni pinceladas — recibe PNG/TGA [ver: blender/geometry-nodes "lo que viaja al FBX"] [ver: pipeline/arte-a-unity].

| Camino | Qué es | Cuándo | Sale a Unity vía |
|---|---|---|---|
| **Texture Paint** | Pintar a mano sobre la malla (§3) | Detalle de autor, hand-painted, retoques, máscaras pintadas | Ya es un mapa de imagen |
| **Shader Nodes procedurales** | Generar textura con noise/voronoi/gradientes + capas (§4) | Materiales tileables, variación, estilizado, wear procedural | **Bake** a imagen (§7) |
| **Máscaras por geometría** | AO/curvature/pointiness dirigen wear/dirt (§6) | Envejecer bordes/cavidades sin pintar | **Bake** a imagen (§7) |
| **Bake de high-poly** | Transferir detalle esculpido a normal/AO | Normal maps, mesh maps | Detalle genérico en [ver: baking] |

Regla de encaje: Blender **basta** para estilizado, procedural/tileable, indie y hero de complejidad media; para realista con muchas capas y smart materials, el estándar sigue siendo Substance (§8, §9) [ver: substance-y-alternativas]. Este archivo cubre lo que Blender hace bien y sus límites.

## 2. Requisito previo innegociable: UVs antes de textura

Nada de esto funciona sin UVs. Pintar necesita saber dónde cae cada píxel; el bake escribe en el layout UV; el procedural tileable se coloca por coordenadas UV. El unwrap, seams, packing y márgenes son un tema propio [ver: uv-unwrapping] [ver: blender/edicion-malla]. Aquí solo el gancho operativo:

- El objeto necesita **al menos un UV Map activo** (Object Data Properties ‣ UV Maps). Sin él, `bpy.ops.object.bake` falla y Texture Paint pinta en negro.
- Para bake: UV0 sin solapes (islas que se pisan → texeles corruptos). Para lightmap en Unity: UV2 aparte [ver: pipeline/arte-a-unity §7].
- **Island Margin** al empaquetar (Pack Islands ‣ Margin) evita que el bleed de un mapa contamine la isla vecina; se combina con el Margin del bake (§7) y el padding del atlas [ver: atlas-trim-optimizacion].

```python
import bpy
obj = bpy.context.object
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.02)  # rad ≈ 66°
# alternativa por seams marcadas: bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.02)
bpy.ops.object.mode_set(mode='OBJECT')
```

## 3. Texture Paint: pintar directo sobre el modelo

### Montaje (lo que falla si se salta)

Texture Paint pinta sobre una **imagen que ya existe y está conectada** al material. Dos formas de crear ese destino:

1. **Add Texture Paint Slot** (Active Tool & Workspace ‣ *Texture Slots* ‣ `+`): elige canal (Base Color, Roughness, Normal…), crea la imagen del tamaño elegido y **cablea automáticamente** el Image Texture node al input correcto del Principled BSDF. La vía recomendada: no deja el nodo suelto.
2. **Manual**: crear un `Image Texture` node, `New` imagen, conectarlo al Base Color, y en Texture Paint elegir *Mode: Single Image* con esa imagen. Más control, más pasos.

Dos superficies para pintar, la misma imagen: el **3D Viewport** (modo Texture Paint, pintas sobre la malla y proyecta a UV) o el **Image Editor / UV Editor** (modo Paint, pintas sobre el plano UV plano). El 3D viewport es lo natural para forma; el editor plano para arreglar seams y detalle en el layout.

```python
import bpy
obj = bpy.context.object
bpy.ops.object.mode_set(mode='TEXTURE_PAINT')
# listar slots/paint mode reales en la sesión:
print(obj.data.uv_layers.active, obj.material_slots[:])
```

### Brushes (⚠️ son Brush Assets desde 4.3)

Cambio grande: en **4.3 los brushes pasaron a ser assets** (Brush Assets) — viven en el **Asset Shelf** y en bibliotecas de brushes, no en la lista vieja de datablocks. Tutoriales ≤4.2 muestran un selector distinto. Brushes base de paint: **Paint** (Draw), **Soften**, **Smear**, **Clone**, **Fill**, **Mask**.

Ajustes por brush (Tool settings): **Radius**, **Strength**, **Color** (+ Secondary, `X` intercambia), **Blend** (Mix/Add/Subtract/Multiply/Screen/Overlay… — pintar por canal usa esto), **Falloff**, **Spacing**, presión de tableta.

### Stencils, texturas de brush y máscaras

| Recurso | Qué hace | Dónde |
|---|---|---|
| **Brush Texture** | Estampa una imagen con cada pincelada (grunge, alfabeto de detalle) | Tool ‣ Texture, con **Mapping**: View Plane / Tiled / 3D / Random / **Stencil** |
| **Stencil** | La textura flota fija sobre la vista y pintas "a través" de ella como plantilla | Mapping = Stencil; mover/rotar/escalar el stencil con `RMB` / `Ctrl-RMB` / `Shift-RMB` |
| **Texture Mask** | Segunda textura que modula la opacidad del trazo (independiente de la Brush Texture) | Tool ‣ Texture Mask, con su propio Mapping (incl. Stencil) |
| **Paint Mask (face select)** | Restringe el pintado a las caras seleccionadas — imprescindible para no manchar islas vecinas | Botón de máscara de caras en el header de Texture Paint |
| **Cavity Mask** | Concentra o excluye el trazo en cavidades por geometría | Options ‣ Cavity |
| **Symmetry** | Espeja el trazo en X/Y/Z (o por radial) | Tool ‣ Symmetry |

### El problema de pintar cruzando islas (seams) y el antídoto

Al pintar en el 3D viewport, un trazo que cruza una **seam** cae sobre caras que en el UV están en islas separadas y distantes: el trazo se ve continuo en 3D pero en la textura queda partido, y al aplicar mipmaps/compresión la costura se hace visible como una línea. Antídotos operativos:

- **Bleed / Margin**: Texture Paint ‣ Options ‣ **Bleed** (en px) — extiende el pintado más allá del borde de cada isla, de modo que los texeles justo fuera de la isla también se pintan y la costura no muestra el color de fondo al filtrar. Es el mismo principio que el Margin del bake (§7). Subirlo cuando aparezcan líneas en seams.
- Pintar el cruce de seam **con Clone o Soften**, o retocar en el Image Editor plano donde se ve el corte real.
- Colocar las **seams en zonas ocultas/poco vistas** desde el unwrap [ver: uv-unwrapping] — la mejor costura es la que no se pinta encima.
- Para hand-painted serio (luz pintada en la difusa, orden de capas) el detalle está en [ver: estilizado-texturas §3-4]; aquí solo el mecanismo.

## 4. Materiales procedurales con Shader Nodes (textura sin pintar)

Generar textura por matemática de nodos: infinito, sin resolución fija hasta el bake, tileable, y paramétrico. La base de un procedural es **texturas generadoras → remap → mezcla en capas**.

### Nodos generadores (verificar `Type`/enums por versión)

| Nodo | bpy idname | Para qué | Salidas clave |
|---|---|---|---|
| **Noise Texture** | `ShaderNodeTexNoise` | Rugosidad, grunge, base de casi todo | Fac, Color; params Scale/Detail/Roughness/Lacunarity/Distortion, dimensión 1D–4D |
| **Voronoi Texture** | `ShaderNodeTexVoronoi` | Celdas, escamas, piedras, cuarteado, poros | F1/F2/Smooth F1/**Distance to Edge**/N-Sphere Radius; Randomness |
| **Gradient Texture** | `ShaderNodeTexGradient` | Rampas, degradados dirigidos | Linear/Quadratic/Radial/Spherical… |
| **Wave / Magic / Brick / Checker** | `ShaderNodeTexWave` etc. | Vetas de madera, ladrillo, patrones | según nodo |
| **Gabor** | `ShaderNodeTexGabor` | Ruido de banda controlada (⚠️ nuevo en 4.3) | anisotropía fina |

⚠️ **Version killers**: el nodo **Musgrave desapareció en 4.1** — sus tipos (fBM, Multifractal, Hybrid…) se fundieron en un dropdown *Type* del **Noise Texture**. Tutoriales con nodo Musgrave son ≤4.0. El **MixRGB** clásico se reemplazó por el nodo unificado **Mix** (`ShaderNodeMix`, `data_type='RGBA'`) en 3.4 — scripts viejos con `ShaderNodeMixRGB` fallan.

### Remap y capas (el "Photoshop de nodos")

- **ColorRamp** (`ShaderNodeValToRGB`): remapea un Fac a color/valor por stops — el nodo que convierte noise crudo en máscara nítida o en degradado de color.
- **Map Range** (`ShaderNodeMapRange`): reescala numéricamente (from/to min-max) — afinar contraste de una máscara.
- **Mix** (`ShaderNodeMix`, RGBA): apila capas — cada capa es un Mix cuyo **Factor** es una máscara (otra textura, una AO, un pointiness). Así se construye "óxido sobre metal sobre pintura".
- **Texture Coordinate** (`ShaderNodeTexCoord`: Generated/Object/**UV**) + **Mapping** (`ShaderNodeMapping`): colocan y escalan el procedural. Para textura que se hornea al UV del asset → usar la salida **UV**.
- **Bump** / **Normal Map**: convierten una altura procedural en relieve para el Normal del Principled.

Modelo mental: `Generador(es) → ColorRamp/Map Range (a máscara) → Mix apila capas → entra a Base Color / Roughness / Normal del Principled`. Para geometría procedural (no textura) el sistema paralelo es Geometry Nodes [ver: blender/geometry-nodes] — no confundir: Shader Nodes hacen color/superficie, Geometry Nodes hacen malla.

## 5. Flujo PBR en Blender: Principled BSDF y ver el resultado

El destino de todos los mapas (pintados, procedurales, bakeados) es el **Principled BSDF** (`ShaderNodeBsdfPrincipled`), shader default, modelo OpenPBR en 5.x. Conexiones que importan para juego:

| Input Principled | Qué se conecta | Colorspace de la imagen |
|---|---|---|
| **Base Color** | Albedo pintado/procedural/bakeado | **sRGB** |
| **Metallic** | Máscara metal (0/1) | **Non-Color** |
| **Roughness** | Mapa de rugosidad | **Non-Color** |
| **Normal** | Normal map vía nodo **Normal Map** (no directo) | **Non-Color** |
| **Emission Color/Strength** | Zonas emisivas | sRGB (color), lineal (strength) |

Reglas de conexión: un normal/roughness/metallic mal marcado como sRGB sale lavado o con la superficie equivocada — **Non-Color obligatorio en todo lo que no sea color**. El montaje del árbol, el preview en EEVEE/Material Preview y por qué EEVEE ≠ Unity ya están cubiertos [ver: blender/materiales-preview §6-7, §10]: **un material bonito en Material Preview es hipótesis, no resultado** — el veredicto es en Unity con el shader real. Aquí solo se añade que la textura final debe **hornearse** (§7); el árbol de nodos no viaja al FBX.

## 6. Máscaras basadas en geometría: wear, edge-wear y dirt procedurales

La clave del envejecido creíble sin pintar: dejar que la **forma del modelo** decida dónde hay desgaste. Tres fuentes, cada una con su nodo, todas remapeables con ColorRamp/Map Range y usadas como **Factor de un Mix** entre material limpio y material gastado.

| Fuente | Nodo / origen | Qué máscara da | ⚠️ Motor |
|---|---|---|---|
| **Pointiness** | `ShaderNodeNewGeometry` ‣ salida **Pointiness** | Curvatura: >0.5 = bordes convexos (edge-wear), <0.5 = cavidades (dirt) | **Cycles only** — en EEVEE devuelve plano/0 |
| **Ambient Occlusion** | `ShaderNodeAmbientOcclusion` | Suciedad en recovecos y contacto (AO de material) | EEVEE + Cycles |
| **Bevel** | `ShaderNodeBevel` (rounded normals) | Realce de brillo/luz en filos | **Cycles only** |
| **AO / Curvature bakeados** | mapas horneados (§7) o mesh maps [ver: baking] | Lo mismo pero **usable en EEVEE** y en Unity | agnóstico |

Receta edge-wear procedural (metal pintado que descascara en filos):

```
Geometry ‣ Pointiness → Map Range (from 0.45–0.55 → 0–1) → ColorRamp (endurecer)
   → Factor de Mix(Base Color): [pintura]  ↔  [metal expuesto]
   (misma máscara, invertida o no, a Metallic y Roughness para que el filo lea a metal)
Añadir Noise Texture al Factor (Multiply) para romper el filo perfecto → desgaste natural.
```

**El puente EEVEE/Unity que hay que entender:** Pointiness y Bevel son **Cycles-only** — un edge-wear armado con ellos no se ve en EEVEE ni existe en Unity. Solución: **hornear la máscara a imagen** (bake Pointiness→Emit, o bake AO, §7) y ya como textura funciona en cualquier motor. Para juego, el destino de estas máscaras es SIEMPRE un mapa horneado, no el nodo en vivo. La versión "smart mask" madura (curvature/AO dirigiendo generadores con control fino) es de Substance [ver: substance-y-alternativas §3-4]; Blender hace la versión honesta y suficiente para estilizado/indie.

## 7. Hornear el árbol procedural a mapas de imagen (baking)

El paso que convierte nodos/pinceladas en los PNG que Unity importa. Este archivo cubre el **bake de un solo objeto (texture bake del propio material)**; el bake high→low con cage, ray distance y mesh maps genéricos vive en [ver: baking].

### Requisitos (si falta uno, el bake falla o sale negro)

1. **Render Engine = Cycles** (`scene.render.engine = 'CYCLES'`) — el operador de bake de textura es de Cycles.
2. El material tiene un **Image Texture node**, con una **imagen creada y asignada**, y ese nodo está **seleccionado y activo** (el bake escribe en el nodo activo).
3. El objeto tiene **UV activo** sin solapes y está **seleccionado + activo**.
4. La imagen destino con el **colorspace correcto** (sRGB para color; **Non-Color** para normal/roughness/metallic/máscaras) y bit-depth: 8-bit PNG para color, **16-bit** para normal/height (evita banding).

### Tipos de bake y ajustes (Properties ‣ Render ‣ Bake)

| Bake Type (bpy `type`) | Uso |
|---|---|
| **DIFFUSE** (Influence: solo **Color**, sin Direct/Indirect) | Hornear el **Base Color** puro (sin luz) |
| **EMIT** | ⭐ **El comodín**: enchufa CUALQUIER salida (una máscara, un roughness procedural, pointiness) a un **Emission** y hornéala como Emit → así se hornea lo que no tiene bake type propio (curvature, máscaras) |
| **NORMAL** | Normal map (Space: Tangent; swizzle R+ G+ Z+ = OpenGL, que es lo que Unity quiere, §9) |
| **ROUGHNESS** | Mapa de rugosidad |
| **AO** | Ambient occlusion de la propia malla |
| **COMBINED / GLOSSY / TRANSMISSION / POSITION / UV / SHADOW / ENVIRONMENT** | Casos específicos / mesh maps [ver: baking] |

⚠️ **No hay bake type "Curvature"** nativo: se hornea el **Pointiness vía Emit** (o con un add-on). AO sí es nativo.

Ajustes que importan: **Selected to Active** (transferir de high a low — detalle en [ver: baking]), **Extrusion** + **Max Ray Distance** / **Cage Object** (proyección high→low), **Margin** (px de bleed fuera de cada isla — el mismo antídoto de seams del §3; típico 8–16 px según resolución) con **Margin Type** *Adjacent Faces* o *Extend*, y **Clear Image** (limpia antes de hornear).

### Resolución y formato de salida

- **Resolución**: potencia de 2 (1024/2048/4096) según texel density del asset — el presupuesto se decide en [ver: atlas-trim-optimizacion §5], no "4K por defecto".
- **Formato a Unity**: **PNG** (lossless, alpha) o **TGA**; **EXR/16-bit** para normal/height si hay banding. Guardar la imagen tras hornear (no queda en disco sola): `Image ‣ Save As`.
- **Empaquetado de canales** (metallic RGB + smoothness en alpha, ORM, etc.): se decide y arma para Unity en [ver: atlas-trim-optimizacion §8] y [ver: texturas-a-unity]; Blender puede pre-combinar con nodos **Combine/Separate Color** antes del bake.

### bpy: hornear base color y máscara, y guardar

```python
import bpy
obj = bpy.context.object
mat = obj.active_material
nt  = mat.node_tree

# 1) imagen destino + Image Texture node, seleccionado y activo
img = bpy.data.images.new("T_Asset_BaseColor", 2048, 2048, alpha=True)
tex = nt.nodes.new('ShaderNodeTexImage')
tex.image = img
for n in nt.nodes: n.select = False
tex.select = True
nt.nodes.active = tex

# 2) Cycles + settings de bake
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.render.bake.margin = 16
sc.render.bake.use_selected_to_active = False

# 3) hornear base color puro (Diffuse, solo Color)
sc.render.bake.use_pass_direct   = False
sc.render.bake.use_pass_indirect = False
sc.render.bake.use_pass_color    = True
bpy.ops.object.bake(type='DIFFUSE')

# 4) guardar (colorspace: sRGB para color; poner 'Non-Color' antes de hornear datos)
img.filepath_raw = "//textures/T_Asset_BaseColor.png"
img.file_format = 'PNG'
img.save()
```

Para hornear una **máscara/valor cualquiera** (p. ej. el edge-wear del §6): conectar esa salida a un `ShaderNodeEmission` → Material Output temporalmente, imagen Non-Color, y `bpy.ops.object.bake(type='EMIT')`. Verificar SIEMPRE el resultado abriendo la imagen (no asumir que horneó bien): revisar seams, islas vacías, negro total = algún requisito falló.

## 8. Add-ons de texturizado para Blender y sus límites

Blender de fábrica pinta y hace procedural; los add-ons rellenan lo que Substance da nativo (capas con máscaras, smart materials, bake de mesh maps cómodo). Panorama — verificar compatibilidad con 5.2 antes de comprar/instalar, y catálogo completo en [ver: blender/addons-ecosistema] [ver: substance-y-alternativas §7]:

| Add-on | Qué aporta | Límite honesto |
|---|---|---|
| **Layer Painter** / paint layer add-ons | Sistema de capas con máscaras estilo Substance dentro de Blender | No iguala smart masks ni la librería de materiales de Substance |
| Bake managers (p. ej. herramientas de bake por lotes) | Bakear mesh maps y sets sin montar el árbol a mano | Sigue siendo el bake de Cycles por debajo |
| Node/material libraries (Node Wrangler ya viene incluido) | Acelerar el armado de nodos (`Ctrl-Shift-T` para PBR set) | Utilidad, no un sistema de texturizado |

**Por qué Substance sigue siendo el estándar de la industria** (desarrollado en [ver: substance-y-alternativas §1]): capas no destructivas con smart masks dirigidas por mesh maps, smart materials reutilizables, librería enorme, bake integrado por texture set, y export presets a cada engine. Blender + add-ons se acerca pero con más fricción y menos ecosistema. La ventaja de Blender: **gratis, todo en un archivo, y suficiente** para muchos targets.

## 9. Cuándo Blender basta y cuándo saltar a Substance

Decisión operativa (la versión larga, con coste/licencia 2026, en [ver: substance-y-alternativas §11]):

| Blender basta | Saltar a Substance |
|---|---|
| **Estilizado / hand-painted** (luz pintada, el motor no la calcula) [ver: estilizado-texturas] | **Realista PBR** con muchas capas físicas |
| **Procedural / tileable / trim** que se resuelve con nodos [ver: atlas-trim-optimizacion] | **Wear complejo** dirigido por curvature/AO con control fino |
| **Indie / dev solo**, presupuesto cero, pocos assets | **Producción con volumen** de assets y consistencia de smart materials |
| Máscaras de geometría simples (§6) | Librería de smart materials + reuso entre proyectos |
| Retoques, máscaras pintadas, detalle puntual | Pipeline de equipo con export presets estandarizados |

Regla: si el estilo es estilizado o el asset es procedural, **Blender-only es la respuesta correcta, no una limitación**. Si es realista con capas y el tiempo de artista importa, Substance amortiza. No meter Substance "porque es lo pro" en un juego low-poly.

## 10. La entrega a Unity: lo que rompe el texturizado de Blender

El texturizado termina cuando los mapas entran a Unity sin retoques. Los canales exactos de URP Lit, el import por tipo de mapa y la compresión están en [ver: texturas-a-unity], [ver: pipeline/arte-a-unity §7] y [ver: atlas-trim-optimizacion §6]; aquí solo las **tres trampas específicas del que hornea en Blender** (verificadas contra docs Unity, ver Fuentes):

1. **Smoothness = 1 − Roughness.** Blender/glTF exportan **roughness**; URP Lit espera **smoothness** en el alpha del Metallic (o del Base) map. Un roughness metido crudo sale invertido (todo mate o todo espejo). Antídoto: invertir el canal antes de hornear (`1 - roughness` con un Math node) o al empaquetar para Unity [ver: atlas-trim-optimizacion §8]. Acordar el canal ANTES de la primera entrega.
2. **sRGB off en mapas de datos.** En Unity, normal/metallic/roughness/mask son **datos, no color**: import con **sRGB (Color Texture) desmarcado**. Solo Base Color y Emission llevan sRGB on. Mismo principio que el Non-Color del §5/§7.
3. **Normales Y+ (OpenGL).** Unity usa **normal maps Y+ (formato OpenGL)**, neutro `#8080FF`. El bake de normal de Blender por defecto ya es +X +Y +Z = OpenGL, así que **coincide** — no invertir el canal verde. Import como Texture Type **Normal map**.

## 11. bpy: export a Unity con texturas al lado

```python
import bpy
# tras hornear y guardar los mapas en //textures/ (§7):
bpy.ops.export_scene.fbx(
    filepath="//export/SM_Asset.fbx",
    use_selection=True,
    apply_scale_options='FBX_SCALE_ALL',   # escala coherente
    mesh_smooth_type='FACE',               # exportar sharp/normales
    use_tspace=True,                       # tangentes para normal map
    path_mode='COPY', embed_textures=False # texturas como archivos al lado, no embebidas
)
# Verificar: reimportar el FBX o abrir la carpeta y confirmar que los PNG salieron.
```

El FBX lleva slots de material y referencias; los **mapas van como archivos aparte** (potencia de 2, naming del proyecto). El bake, no el árbol de nodos, es lo que Unity ve [ver: blender/geometry-nodes] [ver: pipeline/arte-a-unity].

## Reglas prácticas

- [ ] UVs primero: sin UV Map activo no hay paint ni bake [ver: uv-unwrapping]. Island Margin al empaquetar.
- [ ] Crear el destino de pintado con **Add Texture Paint Slot** (cablea el nodo solo), no a mano, salvo que necesites control fino.
- [ ] Brushes son **Brush Assets desde 4.3**: buscarlos en el Asset Shelf, no en la lista vieja.
- [ ] Pintar cruzando seams: subir **Bleed/Margin**, colocar seams en zonas ocultas, retocar el corte en el Image Editor plano.
- [ ] Usar **Paint Mask (face select)** para no manchar islas vecinas al pintar zonas.
- [ ] Procedural: filtrar tutoriales por versión — nodo **Musgrave = ≤4.0** (hoy es Type del Noise), **MixRGB = ≤3.3** (hoy `ShaderNodeMix` RGBA).
- [ ] Cadena procedural: `generador → ColorRamp/Map Range → Mix apila capas`; la salida **UV** del Texture Coordinate para lo que se horneará.
- [ ] Non-Color obligatorio en normal/roughness/metallic/máscaras; sRGB solo en Base Color y Emission (en Blender y en Unity).
- [ ] Edge-wear con **Pointiness** (Cycles) es solo preview: **hornearlo a imagen** para que exista en EEVEE y Unity.
- [ ] Romper filos/máscaras perfectas con Noise multiplicado — el desgaste matemático limpio se nota falso.
- [ ] Bake: Cycles + Image Texture node **activo** + imagen creada + UV activo, o falla en negro.
- [ ] Hornear valores sin bake type propio (curvature, máscaras) con el truco **Emit**.
- [ ] Margin del bake 8–16 px (por resolución) + Margin Type; el bleed es lo que mata las costuras.
- [ ] Guardar la imagen tras hornear (`Image ‣ Save As`); 16-bit para normal/height.
- [ ] Verificar el mapa horneado abriéndolo: seams, islas vacías, negro total = requisito faltó. Nunca asumir.
- [ ] Roughness→**invertir a smoothness** para Unity URP; acordarlo antes de la primera entrega.
- [ ] Blender-only para estilizado/procedural/indie; Substance para realista con capas y volumen — no al revés [ver: substance-y-alternativas].
- [ ] Veredicto final del texturizado: en Unity con el shader y la luz reales, no en Material Preview [ver: blender/materiales-preview §10].

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Texture Paint pinta negro / bake sale negro | Falta UV activo o el Image Texture node no está seleccionado+activo; Cycles no está de engine |
| Seams visibles como líneas al aplicar mipmaps | Bleed/Margin bajo: subirlo en paint (Options ‣ Bleed) y en bake (Output ‣ Margin) |
| Trazo que cruza una seam queda partido en la textura | Es inherente a islas separadas: pintar el cruce con Clone/Soften o en el Image Editor, y ocultar seams al unwrap |
| Buscar los brushes en la lista de datablocks (tutorial ≤4.2) | Son Brush Assets desde 4.3: Asset Shelf / biblioteca de brushes |
| Seguir un procedural con nodo **Musgrave** | Removido en 4.1: usar el dropdown *Type* del Noise Texture |
| Script con `ShaderNodeMixRGB` falla | Reemplazado por `ShaderNodeMix` (`data_type='RGBA'`) en 3.4 |
| Normal/roughness/metallic marcados sRGB → superficie lavada o rara | **Non-Color** en Blender; **sRGB off** en el import de Unity |
| Edge-wear con Pointiness no aparece en EEVEE ni en Unity | Pointiness y Bevel son **Cycles-only**: hornear la máscara a imagen (§7) |
| No existe bake type "Curvature" y se busca en el menú | Hornear Pointiness vía **Emit**, o add-on/mesh map [ver: baking] |
| Islas UV solapadas → texeles corruptos al hornear | UV0 sin solapes; lightmap en UV2 aparte [ver: pipeline/arte-a-unity] |
| Hornear y cerrar sin guardar → imagen perdida | La imagen del bake vive en RAM hasta `Image ‣ Save As`; guardar siempre |
| Roughness crudo a Unity → todo mate o espejo | URP usa smoothness = 1 − roughness: invertir el canal |
| Normal map con verde invertido en Unity | Blender exporta Y+ (OpenGL) por defecto = lo que Unity quiere; no invertir G |
| Aprobar el texturizado en Material Preview de Blender | EEVEE ≠ URP: validar en Unity con shader y luz reales [ver: blender/materiales-preview] |
| Meter Substance en un juego low-poly estilizado | Blender-only basta y es más rápido ahí; Substance solo cuando amortiza (§9) |
| Exportar FBX con `embed_textures` y esperar archivos sueltos | `path_mode='COPY'`, `embed_textures=False` para PNG al lado; potencia de 2 |

## Fuentes

- **URP Lit Shader — Unity Manual 6000.2** (docs.unity3d.com, `urp/lit-shader.html`, consultado 2026-07-20) — canales exactos: Base/Metallic/Normal/Occlusion/Emission, **Smoothness Source = Metallic Alpha / Albedo Alpha**, y que un solo RGBA puede empaquetar metallic+smoothness+occlusion; base del §5 y §10.
- **Texture importer: Texture Type — Unity Manual 6000.2** (docs.unity3d.com, `class-TextureImporter-type-and-shape.html`, consultado 2026-07-20) — lista de Texture Types (Default, **Normal map**, Single Channel, Sprite…); §10.
- **Normal map / Standard Shader Normal Map — Unity Manual 6000.2** (docs.unity3d.com, consultado 2026-07-20) — Unity usa **normal maps Y+ (OpenGL)**, neutro `#8080FF`, RGB = vector (no color, no sRGB); §7 (swizzle del bake) y §10.
- **Importing Textures — Unity Manual 6000.2** (docs.unity3d.com, `ImportingTextures.html`, consultado 2026-07-20) — overview de import, formatos soportados, overrides por plataforma; §10.
- **GPU texture format by platform — Unity Manual 6000.2** (docs.unity3d.com, `texture-choose-format-by-platform.html`, consultado 2026-07-20) — ASTC (bloques 4×4…12×12) iOS/Android, BC7/DXT1/DXT5/BC6H desktop, ETC2 — contexto del formato de salida del §7 (detalle en [ver: atlas-trim-optimizacion]).
- **LearnOpenGL — PBR Theory** (learnopengl.com/PBR/Theory, consultado 2026-07-20) — microfacet, conservación de energía, workflow metallic-roughness (albedo/metallic/roughness/normal/AO) y la nota de que **algunos motores usan smoothness = 1 − roughness**; fundamenta §10 y el encaje con [ver: pbr-teoria].
- ⚠️ **Blender 5.2 Manual — Texture Paint, Cycles Bake, Shader Nodes (Noise/Voronoi/Geometry-Pointiness/Principled BSDF)** (docs.blender.org) — **NO re-fetchable esta sesión (HTTP 403)**; los operadores/nodos/enums de §3-7 provienen de conocimiento de manual + API bpy (estables 3.x-5.x), no re-verificados en vivo hoy. Confirmar nombres exactos por bpy en la sesión real antes de asumir.
- Bases sintetizadas: [ver: blender/materiales-preview] (Principled/OpenPBR, preview EEVEE, EEVEE≠Unity, el veredicto en Unity), [ver: blender/geometry-nodes] (Shader Nodes vs Geometry Nodes, qué viaja al FBX, Store Named Attribute UVs), [ver: pipeline/arte-a-unity] (spec de entrega 3D, canales URP Lit, escala/ejes, colliders/LOD).
