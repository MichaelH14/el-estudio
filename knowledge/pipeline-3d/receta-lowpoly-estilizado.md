# Receta: asset low-poly estilizado en Blender

> **Cuando cargar este archivo:** al EJECUTAR en Blender 5.2 un asset low-poly estilizado destinado a Unity 6 — modelar la forma simplificada, colorearlo sin texturas PBR (vertex color o atlas-paleta), congelar el facetado como estética y exportarlo. Es el PUENTE operativo entre la teoría de [ver: modelado/estilizacion-lowpoly] (qué y por qué) y las herramientas de [ver: blender/edicion-malla], [ver: blender/materiales-preview], [ver: blender/import-export] (cómo se opera cada tecla). Aquí solo va la SECUENCIA concreta paso a paso; los operadores en detalle y la teoría NO se repiten, se referencian.

Versión: **Blender 5.2 LTS** (verificado contra manual/API "latest", jul-2026) → **Unity 6 / URP**. Todo dato dependiente de versión va marcado. Lector: un agente que ejecuta por MCP o headless [ver: blender/blender-mcp-operativo] [ver: blender/bpy-scripting].

## 0. Antes de tocar Blender: qué ya tiene que estar decidido

Esta receta NO decide el estilo, lo ejecuta. Prerrequisitos que vienen del style guide y no se improvisan aquí [ver: modelado/estilizacion-lowpoly §5] [ver: gamedev/arte-direccion]:

| Prerrequisito | De dónde sale | Si falta |
|---|---|---|
| Escuela elegida (facetado / suave / PS1 / hand-painted) | [ver: modelado/estilizacion-lowpoly §2] | PARAR — sin escuela no hay decisiones de normals ni de color |
| Método de color (material plano / vertex color / atlas-paleta) | Tabla §1 de este archivo | PARAR |
| Las 5 decisiones (densidad, paleta hex, bevels sí/no, proporción 1-10, outline/shader) | [ver: modelado/estilizacion-lowpoly §5] | PARAR — son parámetros del encargo, no espacio creativo |
| Escena visual-target en Unity con shader+luz | [ver: pipeline/arte-a-unity §10] | El asset no se puede aprobar; se modela igual pero no se cierra |

El pipeline completo de un asset (blockout→limpieza→UV→export) vive en [ver: flujo-modelado-blender]; esta receta es la VARIANTE low-poly estilizada de ese flujo, que se salta high-poly, bake, normal map y texturizado PBR por completo.

## 1. Elegir el método de color (decide todo el resto de la receta)

Tres caminos, del más simple al más flexible. La teoría y los pros/contras están en [ver: modelado/estilizacion-lowpoly §4]; aquí solo cuál dispara qué receta:

| Método | Cuándo | Materiales en Unity | Receta a seguir |
|---|---|---|---|
| **Color por material plano** | ≤4-5 colores por asset, pocos assets | 1 slot por color → varios draw calls; rompe batching | §5 (solo slots, sin vertex paint) |
| **Vertex color** | Gradientes orgánicos; 1 material para TODO; color atado a densidad de malla | 1 material (Shader Graph que lea vertex color) | §6 |
| **Atlas-paleta** | Muchos assets, color plano, recolor global de un archivo | 1 material + 1 textura diminuta compartidos | §7 |

Regla dura: objetivo **1 material para todo el mundo estático** [ver: pipeline/arte-a-unity §7]. Vertex color y atlas-paleta lo cumplen; material-por-color no. Un material nuevo pide justificación por escrito.

## 2. RECETA — la forma simplificada (blockout → masas primarias)

La estilización se decide en la malla ANTES del color [ver: modelado/estilizacion-lowpoly §3]. Secuencia en Blender:

1. **Escena en metros, escala real.** Unidades métricas, modelar al tamaño del juego (personaje ≈1.8 m) [ver: blender/interfaz-flujo] [ver: modelado/fundamentos-3d].
2. **Montar la referencia.** Blueprint/turnaround como Image Empty o en el background del viewport [ver: modelado/blueprints-referencias] [ver: blockout-desde-referencia]. Nunca modelar de memoria.
3. **Blockout de 1-3 masas primarias** con primitivas (`Shift`-`A`): caja, cilindro, esfera, cuña. Test de silueta ANTES de añadir un solo edge: Solid ‣ Flat + Custom negro + fondo claro, orbitar 360° [ver: blender/materiales-preview §5]. Si la silueta no comunica qué es, más polígonos no lo arreglan.
4. **Exagerar la proporción** (una sola vez, según el nivel 1-10 del style guide): agrandar lo funcional (mango, cabeza, boca del cañón), encoger o **eliminar** lo secundario. Borrar es el paso de estilización más barato. Herramienta: escalar masas (`S`), Proportional Editing (`O`) para deformaciones amplias en malla densa — nunca con extrude [ver: blender/edicion-malla §4].
5. **Añadir SOLO los edges que cambian silueta o shading.** Cada loop cut (`Ctrl`-`R`) o bevel (`Ctrl`-`B`) debe justificarse por la silueta; si no cambia el contorno ni el sombreado, sobra [ver: modelado/topologia]. En low-poly cada vértice existe para la silueta.
6. **Limpieza de malla** (obligatoria antes de color/export): Merge by Distance, Delete Loose, Recalculate Outside + overlay Face Orientation, localizar ngons con Select All by Trait ‣ Faces by Sides. Secuencia y snippet bpy completos en [ver: blender/edicion-malla §6].
7. **Aplicar transforms:** `Ctrl`-`A` ‣ All Transforms en Object Mode. Escala ≠ 1 rompe bevels, merges y el export [ver: blender/import-export].

Presupuesto de tris: el que fije el style guide por categoría [ver: modelado/presupuestos-poligonos]. En low-poly estilizado, decenas a pocos cientos de tris por prop es normal.

## 3. RECETA — el facetado como estética (flat shading)

Cuando la escuela es **facetado** (el polígono ES el look: Astroneer, Grow Home), el facetado se marca a propósito, no se deja al default. Cambio de versión clave: la propiedad "Auto Smooth" de los tutoriales ≤4.0 **ya no existe** (eliminada en 4.1); en 5.2 el facetado puro es **Shade Flat** [ver: blender/edicion-malla §5].

| Objetivo | Operación 5.2 | bpy | Resultado |
|---|---|---|---|
| **100% facetado** (todo el asset) | Object ‣ **Shade Flat** | `bpy.ops.object.shade_flat()` | Normales constantes por cara; sin modificador Smooth by Angle. El "auto smooth a 0" de los tutoriales viejos |
| Facetado con algunas zonas suaves | Object ‣ **Shade Auto Smooth** (ángulo bajo, p.ej. 15-20°) | `bpy.ops.object.shade_auto_smooth(angle=0.35)` | Añade modificador Smooth by Angle anclado al final; suaviza solo bajo el umbral |
| Filo suelto a mano | Edge ‣ Mark Sharp | escribe `sharp_edge` | Filo duro en un edge concreto |

- **Verificar el facetado** con matcap, orbitando: `check_reflection_*` o `hard_surface_grey` [ver: blender/materiales-preview §3]. Nunca fiarse del default del DCC — revisar el shading en engine.
- **Costo oculto (saber esto):** un asset 100% facetado tiene MÁS vértices en GPU que el mismo smooth con idéntico conteo de tris, porque cada hard edge duplica vértices [ver: modelado/estilizacion-lowpoly §4] [ver: modelado/fundamentos-3d]. Es low-TRI, no low-VERT. Casi nunca importa al rendimiento; explica por qué el conteo del DCC ≠ el del engine.
- Al exportar, el facetado viaja como custom split normals: `mesh_smooth_type='FACE'` en el FBX conserva los smoothing groups [ver: blender/import-export]. Si hay modificador Smooth by Angle, aplicarlo o exportar con Apply Modifiers ON.

**Cuándo el facetado ES el estilo (y cuándo es un bug):**

| El facetado es LA estética | El facetado es un error a corregir |
|---|---|
| Escuela 1 declarada en el style guide (cristalino/origami: Astroneer terreno, Grow Home) | Escuela 2 (low-poly suave/juguete: Goose Game, Journey) — ahí va Shade Smooth + bevels ligeros |
| Superficies que quieres leer como planos duros (rocas, terreno, mecánico anguloso) | Superficies que deben leer como curvas (capó, casco, orgánico) → smooth o weighted normals |
| Decisión #3 del style guide = "esquinas afiladas, sin bevels" | Facetas que aparecieron solas por un Shade Auto Smooth con ángulo mal puesto |
| El conjunto entero es facetado (coherencia) | Un asset facetado suelto entre assets smooth = se lee de otro juego |

Mezclar facetado y smooth solo como código semántico documentado (Astroneer: facetado=natural, liso=artificial), nunca por accidente [ver: modelado/estilizacion-lowpoly §2].

## 4. RECETA — color por vertex color (1 material, gradientes gratis)

En 5.x los "vertex colors" son un **Color Attribute** (verificado, manual 5.2). Secuencia:

**4.1 — Crear el Color Attribute.** Object Data Properties ‣ **Color Attributes** ‣ `+`. Dos decisiones (manual 5.2):

| Parámetro | Opciones | Elegir para low-poly de juego |
|---|---|---|
| **Domain** | `Vertex` (per-vértice, interpola → **gradientes** suaves) · `Face Corner` (per-corner → **color plano y sharp por cara**) | **Face Corner** si quieres color plano por faceta ("useful to achieve sharp edges on low-poly assets", manual); **Vertex** si quieres gradiente orgánico |
| **Data Type** | `Color` (float RGBA) · `Byte Color` (8-bit RGBA) | **Byte Color** — es lo que los engines esperan y lo que viaja en el FBX |

bpy verificado: `bpy.ops.geometry.color_attribute_add(name="Col", domain='CORNER', data_type='BYTE_COLOR', color=(1,1,1,1))`. Domain enum: `'POINT'` (Vertex) / `'CORNER'` (Face Corner). Convertir después: `bpy.ops.geometry.color_attribute_convert(domain=, data_type=)`.

**4.2 — Pintar.** Modo **Vertex Paint** (`bpy.ops.object.mode_set(mode='VERTEX_PAINT')` o `bpy.ops.paint.vertex_paint_toggle()`). Para color plano por cara: activar el **paint mask** de caras en el header, seleccionar caras, y rellenar con el color del pincel: `bpy.ops.paint.vertex_color_set()` (rellena la selección con el color de pincel actual). Con Vertex domain + pincel suave se pintan gradientes; la densidad de malla ES la resolución del color (un gradiente escalona si no hay vértices donde transiciona) [ver: modelado/estilizacion-lowpoly §4].

**4.3 — Fill determinista por código** (preferible para un agente headless — no depende de brush ni de máscara). Escribir el atributo directo:

```python
import bpy
me = bpy.context.object.data
# los hex del style guide, ya en 0..1 lineal o sRGB según el pipeline
PALETA = {"cuerpo": (0.20, 0.25, 0.60, 1.0), "metal": (0.55, 0.55, 0.58, 1.0)}
ca = me.color_attributes.get("Col") or me.color_attributes.new(
        name="Col", type='BYTE_COLOR', domain='CORNER')   # CORNER = per loop
# ejemplo: pintar TODAS las caras del material slot 0 con "cuerpo"
col = PALETA["cuerpo"]
for poly in me.polygons:
    if poly.material_index == 0:
        for li in poly.loop_indices:      # CORNER: un dato por loop
            ca.data[li].color = col
me.update()
```

(Con `domain='POINT'` el bucle es sobre `me.vertices` y `ca.data[v.index]`.) Marcar como render color: `bpy.ops.geometry.color_attribute_render_set(name="Col")`.

**4.4 — Ver el color en Blender.** Solid ‣ Color: **Attribute** (bpy: `shading.color_type='VERTEX'`) [ver: blender/materiales-preview §2]. Para Material Preview/render: nodo **Color Attribute** → Base Color del Principled.

**4.5 — Exportar (FBX).** El color viaja con `colors_type='SRGB'` (default; verificado). `'NONE'` no exporta, `'LINEAR'` alternativa de espacio de color. Si hay varias capas, `prioritize_active_color=True`. glTF (verificado, API actual): `export_vertex_color` (`'MATERIAL'`/`'ACTIVE'`/`'NAME'`/`'NONE'`, default `'MATERIAL'`) exporta el color solo si un material lo usa — **pero** dos flags con default **True** cubren el caso típico de un asset sin ese hookup: `export_all_vertex_colors=True` ("Export all vertex colors, even if not used by any material"; si ninguno lo usa, crea un COLOR_0 falso) y `export_active_vertex_color_when_no_material=True` (exporta el color activo si el objeto no tiene material). Con los defaults actuales el vertex color plano YA sale sin tocar nada; poner `export_vertex_color='ACTIVE'` a mano solo hace falta si alguien desactivó `export_all_vertex_colors`. Settings de export completos en [ver: blender/import-export].

**4.6 — Leerlo en Unity.** El URP Lit/Simple Lit estándar **ignora** el vertex color → el modelo importa "gris". Hay que darle un **Shader Graph** (Unlit o Lit) con el nodo **Vertex Color** (output Vector4) enchufado a Base Color [ver: pipeline/arte-a-unity §7]. Verificar el color EN el engine, no en el viewport de Blender: el espacio de color (sRGB/linear) puede diferir y el vertex color escala por gamma — es la causa #1 de "se ve distinto que en Blender" [ver: modelado/estilizacion-lowpoly §4].

## 5. RECETA — color por material plano (el más simple)

Sin vertex paint ni UVs: un slot de material por zona de color. Cada slot = un Principled BSDF plano (Base Color + Metallic + Roughness), nombre `M_*` en inglés; asignación por caras en Edit Mode ‣ Material Properties ‣ Assign. Snippet y detalle en [ver: blender/materiales-preview §6]. Contra: cada material extra es un draw call y rompe el batching [ver: pipeline/arte-a-unity §7] — solo para assets con muy pocos colores o cuando el nº de assets es chico. El shader real se hace en Unity (Simple Lit/Unlit); los nodos procedurales de Blender NO viajan al FBX.

## 6. RECETA — el atlas-paleta (1 material + 1 textura para TODO el juego)

La técnica más escalable: una textura diminuta de bloques de color, y las UVs de cada cara colapsadas a un puntito del color deseado. Teoría en [ver: modelado/estilizacion-lowpoly §4]; ejecución en Blender:

1. **Crear la textura-paleta UNA vez.** Image chica (**128-256 px basta**; más es overkill — 1K de paleta ≈ memoria de ~40k vértices). Poblar los bloques con los hex EXACTOS del style guide + 3-6 tiras de gradiente (terreno oscuro→claro, vegetación, metal). La textura ES la paleta hecha archivo.
2. **Material único** compartido por todos los assets: Principled BSDF con un **Image Texture** (la paleta) → Base Color. Fijar **Interpolation: Closest** en el nodo Image Texture — con Linear los colores de celdas vecinas se mezclan en el borde ("bleed").
3. **Texturizar cada cara colapsando su UV a la celda.** En el UV Editor: seleccionar la isla del grupo de caras → `S` `0` `Enter` (colapsa la isla a un punto) → `G` moverla sobre el centro de la celda de color. Sin unwrap real, sin seams, sin texel density. Para color plano basta el punto; para profundidad barata, mapear la isla a lo LARGO de una tira de gradiente en vez de a un punto.
4. **Todos los assets comparten ESTE material y ESTA textura.** Variantes de color = duplicar la fila en la paleta, no el modelo. Recolorear la paleta = re-skin global del juego entero de un solo archivo.
5. **Export:** las UVs viajan normales en el FBX; el material lleva solo el nombre + la asignación de slot (el shader real se rehace en Unity, pero aquí SÍ importa que la textura acompañe: Path Mode y la textura en potencia de 2) [ver: blender/import-export].
6. **En Unity:** la textura-paleta con **Filter Mode: Point** y, para evitar bleed entre celdas, **mip maps off** o padding generoso alrededor de cada celda; un solo material Unlit/Simple Lit con esa textura para todos los assets [ver: pipeline/arte-a-unity §7].

Combinable: atlas-paleta para el color base + vertex color como máscara de variación/AO barato — solo si el shader del juego lo soporta y está en el style guide.

Montar el material-paleta por código (verificado: `ShaderNodeTexImage.interpolation`, `node_tree.links.new`):

```python
import bpy
img = bpy.data.images.new("PAL_Game", 256, 256)   # poblar las celdas aparte
mat = bpy.data.materials.new("M_PaletteAtlas"); mat.use_nodes = True
nt = mat.node_tree
tex = nt.nodes.new("ShaderNodeTexImage")
tex.image = img
tex.interpolation = 'Closest'                      # sin bleed entre celdas de color
bsdf = nt.nodes["Principled BSDF"]
nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
# cada asset del juego: obj.data.materials.append(mat)  -> UN material para todos
```

## 7. Consistencia entre assets (las 5 decisiones, aplicadas en Blender)

Para un agente que produce en serie, las 5 decisiones de [ver: modelado/estilizacion-lowpoly §5] se traducen a checks operativos en Blender:

| Decisión | Check concreto en Blender |
|---|---|
| **Densidad** | Statistics overlay con el asset entero seleccionado; comparar tris contra el presupuesto de su categoría [ver: modelado/presupuestos-poligonos]. El nº final es el del engine tras export |
| **Paleta** | Color exacto por construcción: hex del style guide en el Color Attribute o en la celda del atlas — NUNCA re-pickeados a ojo |
| **Bevels sí/no** | Una decisión global: o todos los filos con bevel de 1 segmento (`Ctrl`-`B`, `Wheel`=1), o todos con esquina afilada. No mezclar entre assets |
| **Proporción** | El nivel de exageración (1-10) aplicado igual a toda la familia; medir con Measurement overlay contra la referencia [ver: blender/materiales-preview §4] |
| **Outline/shader** | No se ve en Blender — se valida en la escena visual-target de Unity con el toon/outline reales |

Ningún asset se aprueba en el viewport de Blender: solo colocado en la escena visual-target de Unity, con cámara, shader, outline, fog y luz reales, junto a assets vecinos de su categoría [ver: pipeline/arte-a-unity §10] [ver: modelado/estilizacion-lowpoly §8].

## 8. Cuándo esta receta NO ahorra tiempo

El mito "low-poly = fácil" se rompe en varios sitios [ver: modelado/estilizacion-lowpoly §7]:

- **Personaje que anima:** la topología de deformación (loops en hombro/codo/cadera/cara) no se negocia aunque tenga 600 tris. Esta receta NO aplica al rig — ese asset va por [ver: receta-personaje] [ver: modelado/topologia], no por aquí.
- **Menos polígonos = cada vértice pesa más:** no hay textura que tape una silueta muerta o una proporción fea. El tiempo se traslada de "detallar" a "decidir bien la forma", que no es más rápido.
- **El look se termina en el engine:** shader toon + outline + fog + luz + post son días de trabajo que el pipeline "sin texturas" concentra, no elimina.
- **Escuelas PS1 y hand-painted** devuelven todo el coste de textura 2D — no elegirlas "porque son low-poly" sin skill de pixel/ilustración.

## 9. El handoff: el estilo se cierra en Unity, no en Blender

La malla low-poly es la mitad del look; la otra mitad vive en el shader y la luz de Unity [ver: modelado/estilizacion-lowpoly §8] [ver: pipeline/arte-a-unity]. Lo que Blender entrega vs lo que hace Unity:

| Blender entrega | Unity termina |
|---|---|
| Geometría facetada/suave con normales correctas | Toon/cel shading en bandas, rim light |
| Vertex color o UVs sobre atlas-paleta | El Shader Graph que LEE ese color (Unlit/Simple Lit) |
| Slots de material con nombre `M_*` limpio | El material real, outline (inverted hull o post), fog, saturación de luz |
| Escala 1 m, pivots, ejes correctos | La escena visual-target donde se aprueba el asset |

Orden de trabajo del look en engine y por qué (shader→luz→paleta→outline): [ver: modelado/estilizacion-lowpoly §8]. El "feel" y la cámara del juego: [ver: pipeline/feel-en-unity]. Regla dura: el asset "bonito en el viewport de Blender" no existe como dato hasta verse con el shader y la luz del juego.

## 10. Walkthrough completo: un prop facetado con vertex color, de cero a FBX

Secuencia master para un agente — un prop estático (p.ej. un barril o cajón estilizado), escuela facetada, color por vertex color, 1 material. Cada paso remite al detalle:

| # | Paso | Operación 5.2 / bpy | Verificar |
|---|---|---|---|
| 1 | Escena en metros, referencia montada | unidades métricas; Image Empty [ver: modelado/blueprints-referencias] | tamaño real |
| 2 | Blockout de 1-3 masas primarias | `Shift`-`A` primitivas; `S`/`G` para proporción | silueta en Flat negro, orbitar 360° [ver: blender/materiales-preview §5] |
| 3 | Estilizar: exagerar lo funcional, eliminar lo decorativo | escalar masas, `X` borrar, `O` proportional | la silueta comunica qué es |
| 4 | Añadir solo los edges que cambian silueta/shading | `Ctrl`-`R`, `Ctrl`-`B` (1 seg si bevels ON) | cada edge justificado [ver: modelado/topologia] |
| 5 | Limpieza de malla | Merge by Distance, Delete Loose, Recalculate Outside [ver: blender/edicion-malla §6] | Face Orientation todo azul, 0 ngons |
| 6 | Facetar | `bpy.ops.object.shade_flat()` | matcap orbitando [ver: blender/materiales-preview §3] |
| 7 | Color Attribute (Byte Color, Face Corner) | `bpy.ops.geometry.color_attribute_add(domain='CORNER', data_type='BYTE_COLOR')` | Solid ‣ Color: Attribute |
| 8 | Pintar por caras / por código | Vertex Paint + `vertex_color_set()`, o escribir `ca.data[li].color` (§4.3) | color exacto = hex del style guide |
| 9 | Aplicar transforms | `Ctrl`-`A` ‣ All Transforms | escala (1,1,1) |
| 10 | Pivot donde el juego lo necesita | Object ‣ Set Origin (base del prop) | apoya en Y=0 |
| 11 | Export FBX | `apply_scale_options='FBX_SCALE_UNITS'`, `mesh_smooth_type='FACE'`, `colors_type='SRGB'` [ver: blender/import-export] | reimport headless: verts>0, dims en m, scale=1 |
| 12 | (Opcional) captura de verificación headless | render Workbench Flat/Attribute [ver: blender/materiales-preview §8] | silueta + color correctos sin abrir viewport |
| 13 | En Unity: Shader Graph con nodo Vertex Color → Base Color; colocar en la escena visual-target | [ver: pipeline/arte-a-unity §10] | estilo/paleta/detalle coinciden con vecinos |

El asset no está "listo" en el paso 11 (el export no dio error ≠ correcto): está listo tras el paso 13, aprobado en la escena visual-target de Unity con shader y luz reales.

## Reglas prácticas

- [ ] No arrancar sin escuela, método de color y las 5 decisiones ya congeladas en el style guide — son parámetros del encargo, no espacio creativo.
- [ ] Escena en metros, escala real; `Ctrl`-`A` ‣ All Transforms antes de color y de export.
- [ ] Silueta en Flat negro + orbitar 360° ANTES de detallar; si no comunica qué es, no seguir.
- [ ] Cada edge nuevo cambia silueta o shading; si no, sobra. Exagerar lo funcional, eliminar lo decorativo antes de simplificarlo.
- [ ] Objetivo 1 material para todo el mundo estático: vertex color o atlas-paleta, no material-por-color.
- [ ] Facetado puro en 5.2 = **Shade Flat** (`bpy.ops.object.shade_flat()`); la propiedad "Auto Smooth" de tutoriales ≤4.0 ya no existe.
- [ ] Recordar: facetado es low-TRI pero NO low-VERT (cada hard edge duplica vértices en GPU); el conteo del DCC ≠ el del engine.
- [ ] Vertex color = Color Attribute: **Byte Color** + domain **Face Corner** para color plano sharp por cara, **Vertex** para gradiente; verificado en manual 5.2.
- [ ] Gradiente de vertex color exige vértices donde transiciona: la densidad de malla es la resolución del color.
- [ ] Para un agente headless: escribir el Color Attribute por código (per-loop en CORNER, per-vertex en POINT), no depender de brush/máscara.
- [ ] FBX exporta vertex color con `colors_type='SRGB'`; glTF con los defaults actuales (`export_all_vertex_colors=True`, `export_active_vertex_color_when_no_material=True`) ya exporta el vertex color plano sin tocar nada — `export_vertex_color='ACTIVE'` solo si alguien desactivó esos flags.
- [ ] Unity NO lee vertex color en el Lit estándar: hace falta un Shader Graph con el nodo **Vertex Color** → Base Color. Verificar el color EN el engine (gamma difiere).
- [ ] Atlas-paleta: textura **128-256 px**, Image Texture **Interpolation: Closest** en Blender y **Filter Mode: Point** en Unity; UV de cada isla colapsada con `S 0` sobre la celda.
- [ ] Recolorear la paleta (Color Attribute o celda del atlas) re-skinea todo — nunca colores "aproximados" por asset.
- [ ] Limpieza de malla completa (§2.6) antes de color y de export, en ese orden.
- [ ] Personaje que anima NO va por esta receta: topología de deformación completa vía [ver: receta-personaje].
- [ ] Aprobar el asset SOLO en la escena visual-target de Unity, junto a assets vecinos, con shader/luz/outline reales.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Buscar la propiedad "Auto Smooth" para facetar (tutoriales ≤4.0) | Eliminada en 4.1; en 5.2 facetado puro = Object ‣ Shade Flat; suavizado parcial = Shade Auto Smooth (modificador Smooth by Angle) [ver: blender/edicion-malla §5] |
| Modelo importa "gris" en Unity pese al vertex color | El shader estándar lo ignora: asignar Shader Graph con nodo Vertex Color; confirmar que el FBX salió con `colors_type` ≠ 'NONE' |
| glTF sale sin vertex color (caso raro) | Solo pasa si alguien puso `export_all_vertex_colors=False` y `export_active_vertex_color_when_no_material=False`; con los defaults (ambos True) ya exporta el color activo aunque ningún material lo use — revisar esos dos flags antes de forzar `export_vertex_color='ACTIVE'` |
| Vertex color se ve distinto en Unity que en Blender | Diferencia de espacio de color/gamma: verificar SIEMPRE en engine; probar export 'LINEAR' vs 'SRGB' y ajustar en el Shader Graph [ver: modelado/estilizacion-lowpoly §4] |
| Gradiente de vertex color que "escalona" | La malla no tiene vértices donde transiciona: añadir loops, o pasar ese tramo a una tira de gradiente del atlas |
| Celdas de la paleta que se "sangran" (bleed) entre colores | Interpolation Closest en Blender + Filter Mode Point y mips off (o padding) en Unity; la UV colapsada exactamente al centro de la celda |
| Cada asset con su propio material/colores | Atlas-paleta o vertex color con UN material para todo; auditar nº de materiales en el import [ver: pipeline/arte-a-unity] |
| Color "aproximado" por asset | Hex del style guide en el Color Attribute o la celda; jamás re-pickear a ojo — el color exacto es por construcción |
| Facetado "a medias" (solo donde el ángulo pasó el umbral) | Decisión explícita: Shade Flat total, o Shade Auto Smooth con ángulo pensado; revisar el shading con matcap orbitando [ver: blender/materiales-preview §3] |
| Sobre-detallar "para que se vea trabajado" | Silueta > detalle; en low-poly el upgrade es proporción/color, no más geometría [ver: modelado/estilizacion-lowpoly §3] |
| Escala sin aplicar → bevels y merges desiguales, escala 100× en Unity | `Ctrl`-`A` ‣ All Transforms + export con `apply_scale_options='FBX_SCALE_UNITS'` [ver: blender/import-export] |
| Personaje low-poly modelado como prop (sin loops de deformación) | La topología de animación no se negocia; ese asset va por [ver: receta-personaje] |
| Aprobar el asset en el viewport de Blender | No existe como dato hasta verse con el shader/outline/luz del juego en la escena visual-target [ver: pipeline/arte-a-unity §10] |

## Fuentes

**Web (verificadas jul-2026):**

- **Vertex Paint — Introduction, Blender 5.2 LTS Manual** (docs.blender.org/manual, sculpt_paint/vertex_paint) — vertex paint almacena un Color Attribute; se ve en Solid ‣ Attribute Color (Workbench) y con el nodo Color Attribute en un material.
- **Object Data Properties — Color Attributes, Blender 5.2 LTS Manual** (docs.blender.org/manual, modeling/meshes/properties/object_data) — creación del Color Attribute: Domain (Vertex / Face Corner) y Data Type (Color / Byte Color); la nota literal de que Face Corner "is useful to achieve sharp edges in the color attribute on low-poly assets".
- **Object ‣ Shading (Shade Smooth / Shade Flat / Shade Auto Smooth), Blender 5.2 LTS Manual** (docs.blender.org/manual, scene_layout/object/editing/shading) — Shade Flat = normales constantes (facetado); Shade Smooth elimina Smooth by Angle; Shade Auto Smooth añade el modificador anclado al final.
- **Blender Python API — bpy.ops.geometry** (docs.blender.org/api/current) — firma verificada de `color_attribute_add(name, domain='POINT', data_type='FLOAT_COLOR', color)`, `color_attribute_convert`, `color_attribute_render_set`.
- **Blender Python API — bpy.ops.paint** (docs.blender.org/api/current) — `vertex_color_set(use_alpha)` (rellena la capa activa con el color de pincel) y `vertex_paint_toggle()`.
- **Blender Python API — bpy.ops.export_scene (fbx / gltf)** (docs.blender.org/api/current, verificado por curl 20-jul-2026) — `colors_type` ('NONE'/'SRGB'/'LINEAR', default 'SRGB') y `prioritize_active_color` del FBX; `export_vertex_color` ('MATERIAL'/'ACTIVE'/'NAME'/'NONE', default 'MATERIAL'), `export_all_vertex_colors` (default **True**) y `export_active_vertex_color_when_no_material` (default **True**) del glTF — firmas completas confirmadas contra la página en vivo.
- **Blender Python API — bpy.ops.object (shade_flat / shade_auto_smooth / shade_smooth_by_angle)** (docs.blender.org/api/current, verificado por curl 20-jul-2026) — `shade_auto_smooth(use_auto_smooth=True, angle=0.523599)` y `shade_smooth_by_angle(angle=0.523599, keep_sharp_edges=True)` confirmados como operadores distintos y activos en 5.x.
- **Blender Python API — bpy.types.AttributeGroupMesh** (docs.blender.org/api/current, verificado por curl 20-jul-2026) — `color_attributes.new(name, type, domain)` confirmado (firma posicional exacta usada en el snippet 4.3); `color_attribute_add(name, domain='POINT', data_type='FLOAT_COLOR', color=(0,0,0,1))` confirmado con default real.
- **Vertex Color Node — Unity Shader Graph 17.0 Manual** (docs.unity3d.com/Packages/com.unity.shadergraph) — el nodo que expone el vertex color de la malla (output Vector4) para enchufar a Base Color; confirma que el vertex color necesita un Shader Graph, no el Lit estándar.

**Bases sintetizadas (no repetidas aquí):** [ver: modelado/estilizacion-lowpoly] (escuelas, texturizar sin texturas, 5 decisiones, referentes, el look en el shader), [ver: blender/edicion-malla] (extrude/bevel/loop cut, normales y Shade Flat en 5.x, limpieza de malla), [ver: blender/materiales-preview] (viewport shading, matcaps, chequeo de silueta, slots de material, Color: Attribute), [ver: blender/import-export] (settings FBX/glTF a Unity, escala 100×, qué viaja y qué no).
