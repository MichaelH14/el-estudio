# Materiales y evaluación visual (para modelado)

> **Cuando cargar este archivo:** al evaluar visualmente un modelo DENTRO de Blender durante el modelado — elegir modo de viewport shading, matcaps, cavity, chequeo de silueta/topología/normales, montar materiales planos de trabajo (los slots que Unity verá) y decidir cuándo (no) usar EEVEE/Cycles. NO cubre texturizado ni bake (fase aparte) ni la spec de entrega [ver: pipeline/arte-a-unity].

Versión de referencia: **Blender 5.2 LTS** (todo verificado contra el manual 5.2 y la API actual; los cambios 4.x→5.x se marcan explícitos — mucho contenido web de 2.8-4.x ya no aplica).

## 1. El mapa: 4 modos de Viewport Shading

Header ‣ Viewport Shading. Atajos: `Z` abre el pie menu de shading, `Shift-Z` alterna con Wireframe, `Alt-Z` toggle X-Ray.

| Modo | Motor real | Qué te dice | Qué NO te dice |
|---|---|---|---|
| **Wireframe** | Workbench | Solo edges; densidad y flow general | Nada de superficie ni shading |
| **Solid** | Workbench (sin shader nodes) | Forma, superficie, topología, normales — **el modo de trabajo del modelador** | Nada de materiales PBR ni luz real |
| **Material Preview** | **EEVEE + HDRI** | Los materiales con nodos bajo una luz de estudio controlada | La luz del JUEGO; el shader de Unity |
| **Rendered** | El render engine de la escena (EEVEE o Cycles) | El frame final de Blender con luces de escena | Cómo se verá en Unity — jamás |

Regla de operación: **se modela en Solid**; Material Preview es para revisar asignación de materiales; Rendered casi nunca durante modelado. Material Preview no está disponible si el render engine de la escena es Workbench (manual 5.2).

## 2. Solid a fondo (Workbench): el banco de trabajo

Solid usa el motor Workbench: shading simplificado, sin nodos, optimizado para modelar. Todo se controla en el popover del header (dropdown junto a los 4 botones de modo).

### Lighting (3 opciones)

| Lighting | Qué hace | Cuándo usarla |
|---|---|---|
| **Studio** | Hasta 4 luces virtuales predefinidas que siguen la cámara (configurables en Preferences ‣ Lights ‣ Studio Lights); `World Space Lighting` las fija al mundo; `Rotation` las gira en Z | Default de trabajo: neutral y estable |
| **MatCap** | Imagen esférica: el color se elige **según la dirección de la normal respecto a la cámara** (manual 5.2). Botón de doble flecha = Flip horizontal | Inspección de superficie y curvatura (§3) |
| **Flat** | Cero iluminación: solo el color base | **Chequeo de silueta** (§5) y ver colores puros |

### Color (fuente del color por objeto)

Opciones: **Material** (color del panel Material ‣ Viewport Display), **Object**, **Random** (color aleatorio por objeto — el "clown" instantáneo), **Attribute** (color attribute activo), **Texture** (textura del image node activo por UV activo), **Custom** (toda la escena en un solo color). ⚠️ bpy: el enum de `color_type` sigue llamando `'SINGLE'` a lo que la UI 5.x etiqueta "Custom", y `'VERTEX'` a "Attribute".

### Options del popover Solid

| Opción | Uso en modelado |
|---|---|
| **Cavity** | Resalta ridges y valleys. `Type`: **World** (world-space, oclusión de mayor escala, más lento), **Screen** (curvatura fina en screen-space, rápido), **Both** (los dos a la vez). Sliders `Ridge`/`Valley` independientes |
| **Shadow** | Sombra dura direccional (Darkness, Direction, Offset, Focus) — lectura rápida de volúmenes |
| **X-Ray** (`Alt-Z`) | Escena semitransparente; imprescindible para seleccionar a través y revisar interiores |
| **Backface Culling** | Oculta el reverso de las caras — detecta normales invertidas al instante (la cara "desaparece") |
| **Outline** | Contorno por objeto (color configurable) |
| **Specular Highlighting** | Brillos especulares; solo disponible con Studio o con un MatCap que tenga specular pass |
| **Depth of Field** | Usa el DoF de la cámara activa; solo en vista de cámara — apagado para modelar |

### MatCaps: cuáles y para qué (set 5.x)

⚠️ **Cambio 5.0**: la colección de matcaps se renovó completa — nuevos matcaps con capa specular para mejor legibilidad en superficies oscuras (release notes 5.0). Los nombres clásicos de 2.8-4.x (`jade`, `skin`, `metal_shiny`, `metal_anisotropic`…) **ya no existen**. Set actual (verificado en el repo oficial, `release/datafiles/studiolights/matcap/`):

| MatCap | Uso |
|---|---|
| `basic_bright` / `basic_dark` / `basic_grey` / `basic_side` | Neutros de trabajo; `basic_side` ilumina lateral (lee mejor formas frontales) |
| `check_reflection_horizontal` / `check_reflection_vertical` | ⭐ **El "zebra" de Blender**: franjas reflectivas para inspeccionar curvatura y continuidad (§3) |
| `check_normal+y` | Visualiza normales (verde = +Y de cámara); útil para detectar shading roto |
| `check_gradient`, `check_rim_dark`, `check_rim_light` | Gradiente y rim para leer silueta interna y bordes |
| `clay_brown` / `clay_green` / `clay_studio` / `clay_warm` | Arcilla: el estándar para esculpir y evaluar formas orgánicas [ver: sculpt] |
| `hard_surface_grey` / `hard_surface_red` | Diseñados para hard-surface: specular marcado que delata bevels y paneles [ver: modelado/hard-surface] |
| `fullmetal`, `metal_bronze`, `metal_carpaint` | Metálicos reflectivos — segundo nivel de inspección de superficie |
| `pearl`, `red_wax`, `resin`, `ceramic_dark`, `ceramic_lightbulb`, `toon_dark`, `toon_light` | Alternativas de lectura (cera/cerámica/toon) |

MatCaps custom se cargan en Preferences ‣ Lights ‣ MatCaps. Formato: imagen normal (solo diffuse — tiende a verse metálica) o **OpenEXR multicapa** con layers llamados `diffuse` y `specular` (el specular se suma encima y permite simular más materiales) — manual 5.2.

Limitación estructural del matcap (Polycount: es un spherical environment map alineado a cámara): la imagen reflejada es siempre la misma — **la inspección exige orbitar** para que el patrón fluya sobre la superficie; con cámara quieta no dice nada nuevo.

## 3. Inspección de superficie con matcap reflectivo (protocolo)

Para hard-surface y superficies curvas [ver: modelado/vehiculos] [ver: modelado/hard-surface]:

1. Solid ‣ Lighting: MatCap ‣ `check_reflection_horizontal` (franjas horizontales; la vertical para el otro eje).
2. **Orbitar despacio** alrededor de la zona sospechosa. Leer las franjas:
   - Franjas que fluyen suaves y paralelas = superficie continua.
   - Franja que se **quiebra** = quiebre de tangencia (edge duro no intencional, vértice fuera de superficie).
   - Franjas que se **pellizcan/arremolinan** = pole o densidad desigual [ver: modelado/topologia].
3. Repetir con Flip MatCap (invierte el lado iluminado) y con el matcap rotado de eje.
4. Complementar con `Cavity: Both` — Screen delata detalle fino, World la oclusión grande.
5. Falso positivo clásico: low-poly con shade smooth SIN bevels ni custom normals SIEMPRE muestra banding en el zebra — evaluar contra el estándar del asset (mid-poly con weighted normals vs subdivision), no contra la perfección [ver: modelado/topologia].

## 4. Overlays para evaluar (Header ‣ Overlays, popover)

| Overlay | Dónde | Qué revela |
|---|---|---|
| **Statistics** | Guides | Objects seleccionados/total + Geometry (verts, edges, faces, **tris**). ⚠️ El conteo **depende de la selección actual** (manual 5.2). El número contractual del presupuesto es el del ENGINE tras exportar, no este [ver: modelado/presupuestos-poligonos] |
| **Wireframe** (Geometry) | Geometry | Edges encima del shading actual. Slider threshold: bajo = oculta edges de zonas casi planas, `1.0` = todos; + slider Opacity. **Topología sobre forma = wireframe sobre Solid con matcap**, el chequeo estándar antes de aprobar una malla |
| **Face Orientation** | Geometry | Reverso de caras en **rojo** = normal invertida → `Mesh ‣ Normals ‣ Recalculate Outside` (`Shift-N`) [ver: edicion-malla] |
| **Creases / Sharp / Bevel / Seams** | Mesh Edit Mode | Edge data marcada (crease subdiv, sharp, bevel weight, UV seams) |
| **Measurement** (Edge Length / Edge Angle / Face Area / Face Angle) | Mesh Edit Mode | Medidas reales de lo seleccionado — verificar escala física [ver: modelado/fundamentos-3d] |
| **Normals** (vertex / split / face) | Mesh Edit Mode | Dirección de normales con tamaño ajustable y `Constant Screen Size` |
| **Mesh Analysis** | Mesh Edit Mode | Overlay de análisis (overhang/thickness/intersections/distortion/sharp) |
| **Retopology** | Shading (Edit Mode) | Malla editada semitransparente sobre el sculpt de referencia, con `Offset` hacia cámara |
| **Reference Spheres** | Guides (solo Material Preview) | 2 esferas (glossy + diffuse) que reaccionan a la luz — lookdev. ⚠️ Renombrado en 5.0: antes se llamaba "HDRI Preview" |

Nuevo en 5.1: overlay de estadísticas de **performance timing** del viewport (release notes 5.1) — para diagnosticar viewport lento, no para presupuesto de asset.

## 5. Chequeos visuales del modelado (recetas)

**Silueta (flat negro).** La silueta debe leerse sola [ver: modelado/props-armas]. Receta UI: Solid ‣ Lighting: Flat ‣ Color: Custom (negro) ‣ Background: Custom (blanco/gris claro). Orbitar 360° y mirar solo el contorno. Por bpy:

```python
import bpy
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        sh = area.spaces.active.shading
        sh.type = 'SOLID'
        sh.light = 'FLAT'
        sh.color_type = 'SINGLE'        # UI 5.x: "Custom"
        sh.single_color = (0, 0, 0)
        sh.background_type = 'VIEWPORT' # UI: "Custom"
        sh.background_color = (1, 1, 1)
```

**Curvatura/superficie**: protocolo del §3 (zebra + orbitar).

**Formas y detalle**: `Cavity: Both` + matcap clay; subir `Valley` para leer hendiduras. Con Shadow activado se leen los volúmenes grandes.

**Topología**: overlay Wireframe (threshold 1.0) sobre Solid; en Edit Mode revisar poles y flow [ver: modelado/topologia]. N-gons/tris ocultos: seleccionar por trait (`Select ‣ Select All by Trait ‣ Faces by Sides`) [ver: edicion-malla].

**Normales/caras invertidas**: Face Orientation (nada rojo por fuera) + Backface Culling activado un momento.

**Tris reales**: Statistics con TODO el asset seleccionado; el veredicto final lo da el import en Unity [ver: pipeline/arte-a-unity].

**Escala**: Measurement ‣ Edge Length contra las medidas del blueprint [ver: modelado/blueprints-referencias].

## 6. Materiales básicos de trabajo (lo único de "materiales" en esta fase)

Durante el modelado NO se texturiza. Se definen **zonas de material**: un slot por cada material que el asset tendrá en Unity (objetivo: 1 por prop; 2-3 solo en hero assets [ver: pipeline/arte-a-unity]). Cada slot = un **Principled BSDF plano** (sin texturas): Base Color aproximado + Metallic + Roughness. El Principled BSDF 5.x está basado en el modelo **OpenPBR Surface** (manual 5.2) y es el shader default de todo material nuevo. ⚠️ Cambio 4.0: el nodo se reorganizó (coat/sheen/emission agrupados) — screenshots 2.8-3.x del nodo no coinciden con el actual.

```python
import bpy

def mat_zona(nombre, color, metallic=0.0, rough=0.6):
    m = bpy.data.materials.get(nombre) or bpy.data.materials.new(nombre)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = rough
    # Color que muestra Solid con Color: Material (Viewport Display)
    m.diffuse_color = (*color, 1.0)
    return m

obj = bpy.context.object
obj.data.materials.append(mat_zona("M_Body", (0.20, 0.25, 0.60)))
obj.data.materials.append(mat_zona("M_Metal", (0.55, 0.55, 0.58), metallic=1.0, rough=0.35))
# Asignación por caras: Edit Mode > seleccionar > Material Properties > Assign
```

**Clown/ID colors** para separar partes visualmente:

- Entre OBJETOS: Solid ‣ Color: **Random** — cero setup, cada objeto un color (capacidad nativa de Workbench, manual 5.2).
- Entre ZONAS de un mismo objeto: un color chillón distinto en el `diffuse_color` (Viewport Display) de cada material + Solid ‣ Color: Material. Sirve además de ID visual para verificar que cada cara está en el slot correcto antes de exportar.
- Nombres de material con prefijo (`M_`) y en inglés: sobreviven al FBX y son lo que el dev ve en Unity [ver: pipeline/arte-a-unity] [ver: import-export].

Qué NO hacer aquí: nodos procedurales/complejos "para que se vea mejor" — no viajan a Unity (el FBX lleva slots y poco más), y varios nodos son EEVEE-only. El look final se decide en el engine [ver: gamedev/arte-direccion] o con flat colors/paleta si el estilo es low-poly [ver: modelado/estilizacion-lowpoly].

## 7. Material Preview vs Rendered: qué te dice cada uno

**Material Preview** = EEVEE + HDRI de lookdev, con el popover:

- `Scene Lights` / `Scene World` (default **off**): apagados usan luz virtual + HDRI elegido — evaluación NEUTRA e independiente de la escena. Encendidos = ensayo de la iluminación propia.
- `HDRI Environment` + `Rotation` + `Strength` + `World Opacity` + `Blur`. HDRIs incluidos (verificados en el repo oficial): `city`, `courtyard`, `forest`, `interior`, `night`, `studio`, `sunrise`, `sunset`. Custom en Preferences ‣ Lights ‣ HDRIs.
- `Render Pass`: ver un pass aislado (AO, Normal, Diffuse Color…) — depurar geometría/material sin la mezcla final.
- Panel Material ‣ Preview: probar el material sobre Shape estándar (Plane/Sphere/Cube/Hair/Shader Ball/Cloth/Fluid).

**Rendered** = el engine de la escena con sus luces reales. Para modelado casi nunca; para lookdev de marketing, sí.

**Lo que NINGUNO te dice**: cómo se ve el asset en Unity. EEVEE ≠ URP/HDRP: otro tonemapping (Blender usa su propia gestión de color/vista), otras luces, otros shaders, otro AA. Y EEVEE es raster con efectos en screen-space: solo considera lo visible en pantalla y un solo layer de depth (manual 5.2, Limitations) — sus reflejos/AO no son los del juego. Un material "bonito en Material Preview" es una hipótesis, no un resultado.

## 8. EEVEE vs Cycles en 5.x (2026, para game dev)

| | EEVEE | Cycles |
|---|---|---|
| Qué es | Raster realtime PBR (reescrito en 4.2 — el "EEVEE Next"; desde entonces es EL EEVEE) | Path tracer físico de producción |
| Para modelar | Ya lo usas sin saberlo (Material Preview) | No |
| Para validar un asset de juego | Tampoco — se valida en Unity [ver: pipeline/arte-a-unity] | Menos todavía |
| Cuándo SÍ | Preview de materiales/luz dentro de Blender; renders rápidos de proceso | **Portfolio, key art, marketing del juego**: renders offline donde la física de la luz vende |
| bpy engine id | ⚠️ 5.0 renombró `BLENDER_EEVEE_NEXT` → `BLENDER_EEVEE` (release notes 5.0). Scripts 4.2-4.5 con el id viejo se rompen | `CYCLES` |

Estado 5.x verificado: 4.5 puso Vulkan a la par de OpenGL (OpenGL seguía default); 5.0 trajo HDR/wide gamut con Vulkan (Windows/Linux+Wayland), matcaps nuevos y EEVEE 4× más rápido compilando materiales; 5.1 aceleró más la compilación; 5.2 LTS rehizo el screen-space raytracing y arregló Fast GI/AO (cambia el look de archivos viejos que los usaban). Traducción operativa: para un flujo de assets de juego, **Workbench/Solid + Material Preview puntual cubre el 95%**; Cycles se reserva para el render de marketing.

**Workbench como engine de render final** (para capturas de verificación, también headless): Properties ‣ Render ‣ Render Engine: Workbench; sus settings viven en Properties ‣ Render ‣ Lighting/Options (mismas opciones que el popover de Solid). Por bpy:

```python
import bpy
sc = bpy.context.scene
sc.render.engine = 'BLENDER_WORKBENCH'
sh = sc.display.shading            # SceneDisplay.shading: mismo View3DShading
sh.light = 'STUDIO'
sh.show_cavity = True
sh.cavity_type = 'BOTH'
sc.render.filepath = "//check_asset.png"
bpy.ops.render.render(write_still=True)
```

Esto permite a un agente sin viewport producir la "foto de evaluación" (silueta, clay, clown) de forma reproducible [ver: blender-mcp-operativo] [ver: bpy-scripting].

## 9. Luces neutras de evaluación (no engañarse)

Juzgar forma y material bajo luz dramática miente. Dos setups honestos:

**A. HDRI neutro (el rápido).** Material Preview con `Scene World` off + `studio` o `interior` como HDRI, `Strength 1.0`, rotando el HDRI (`Rotation`) para mover la luz alrededor del asset. Evitar `sunset`/`sunrise`/`night` para evaluar: tiñen todo. En 5.1 volvió la opción de **view space lighting** del HDRI de lookdev y mejoró la rotación (release notes 5.1) — rotar la luz es barato; úsalo.

**B. 3 puntos clásico (cuando hace falta luz de escena).** Key fuerte a ~45°, fill suave opuesto a media energía, rim trasero para despegar la silueta:

```python
import bpy
def luz(nombre, tipo, loc, rot, energia, size=1.0):
    d = bpy.data.lights.new(nombre, type=tipo); d.energy = energia
    if tipo == 'AREA': d.size = size
    o = bpy.data.objects.new(nombre, d)
    o.location, o.rotation_euler = loc, rot
    bpy.context.collection.objects.link(o); return o

luz("Key",  'AREA', (3, -3, 3),  (0.9, 0, 0.8),  500, size=2)
luz("Fill", 'AREA', (-3, -2, 2), (1.1, 0, -0.9), 150, size=3)
luz("Rim",  'SPOT', (0, 4, 3),   (-1.0, 0, 3.14), 400)
```

Reglas: luces blancas (sin tinte) para evaluar; fondo gris medio; encender `Scene Lights` en Material Preview para verlas. Es un rig de EVALUACIÓN — se borra o se deja fuera del export [ver: organizacion-blend] [ver: import-export].

## 10. La trampa del render bonito

La iluminación de Blender no es la de Unity. Un asset puede verse impecable en Material Preview y romperse en el juego: smoothness invertido (URP usa smoothness = 1−roughness), tonemapping distinto, luces reales del nivel, shader más barato, mips y compresión de textura. Por eso el criterio de aceptación de un modelo NUNCA es un render de Blender:

1. En Blender se valida **geometría**: silueta, superficie (zebra), topología, normales, escala, slots de material con nombre correcto (§5-6).
2. El veredicto visual se da **en Unity con el shader real del juego y la luz real de la escena** [ver: pipeline/arte-a-unity]. "Probar bajo la LUZ real del juego, no en un viewport neutro" es parte del checklist de entrega de esa base.
3. El render Cycles bonito es un entregable de MARKETING, no una verificación. Si el asset solo se ve bien en Cycles, el asset no está bien.

## Reglas prácticas

- [ ] Modela en **Solid** (Workbench); `Z` para cambiar de modo, `Shift-Z` wireframe, `Alt-Z` X-Ray.
- [ ] Silueta antes que detalle: Flat + Custom negro + fondo claro, orbitar 360°.
- [ ] Superficies curvas: matcap `check_reflection_horizontal`/`vertical` + **orbitar** — franja quebrada = tangencia rota.
- [ ] Formas y hendiduras: Cavity `Both` (Screen = detalle fino, World = oclusión grande) + matcap clay.
- [ ] Topología: overlay Wireframe (threshold 1.0) sobre Solid antes de aprobar cualquier malla.
- [ ] Face Orientation on al cerrar el modelado: nada rojo por fuera; `Shift-N` si aparece.
- [ ] Statistics overlay siempre visible; recordar que cuenta según la selección y que el número final es el del engine.
- [ ] 1 material = 1 zona que Unity verá: Principled BSDF plano (Base Color/Metallic/Roughness), nombre `M_*` en inglés.
- [ ] Clown check antes de exportar: Solid ‣ Color: Material con colores chillones por slot (o Random entre objetos) — cada cara en su slot.
- [ ] Nada de node-trees complejos en fase de modelado: no viajan al FBX.
- [ ] Material Preview solo con HDRI neutro (`studio`/`interior`) y `Scene World/Lights` off para evaluar; rotar el HDRI, no fiarse de un solo ángulo.
- [ ] Reference Spheres on en lookdev (Overlays, solo Material Preview) para calibrar la luz.
- [ ] Cycles solo para portfolio/marketing; jamás como criterio de aceptación de un asset.
- [ ] Capturas de verificación reproducibles (headless/MCP): engine `BLENDER_WORKBENCH` + `scene.display.shading`.
- [ ] En scripts 5.x: EEVEE es `'BLENDER_EEVEE'` (no `_NEXT`), color Custom es `color_type='SINGLE'`, fondo Custom es `background_type='VIEWPORT'`.
- [ ] Si un matcap no carga por nombre, listar los reales: `[s.name for s in bpy.context.preferences.studio_lights]` (el set cambió en 5.0).
- [ ] Veredicto final del asset: en Unity, con el shader y la luz del juego [ver: pipeline/arte-a-unity].

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Evaluar el modelo solo de frente y quieto | La silueta y el zebra solo funcionan orbitando; girar SIEMPRE 360° y en picado/contrapicado |
| "Se ve bien con este matcap" (uno solo, difuso) | Los matcaps difusos esconden defectos de curvatura; pasar SIEMPRE por `check_reflection_*` y un specular (`hard_surface_grey`) |
| Script/tutorial 4.x: `studio_light='metal_shiny.exr'` o similar falla en 5.x | El set de matcaps se renovó en 5.0; usar los nombres nuevos o listarlos por bpy |
| `render.engine = 'BLENDER_EEVEE_NEXT'` rompe en 5.x | Renombrado a `BLENDER_EEVEE` en 5.0 (release notes oficiales) |
| Dar por bueno el polycount del Statistics overlay | Cuenta lo seleccionado y en unidades del DCC; el contrato es tris/vértices del engine tras export [ver: modelado/presupuestos-poligonos] |
| Zebra "sucio" en un low-poly con shade smooth y creer que la malla está mal | El banding es esperable sin bevels/weighted normals; evaluar contra el estándar del workflow elegido [ver: modelado/hard-surface] |
| Materiales de trabajo con nodos procedurales elaborados | No exportan al FBX; en Unity llega el slot pelado. Flat Principled y el look se hace en el engine o en texturizado |
| Aprobar el asset por un render Cycles precioso | Cycles no representa el runtime; validación = Unity con shader real (§10) |
| Evaluar color/material bajo `sunset`/`night` o luces con tinte | HDRI neutro (`studio`/`interior`) o 3 puntos blanco; la luz dramática es para marketing |
| Buscar el toggle "HDRI Preview" (tutoriales 4.x) | Se llama **Reference Spheres** desde 5.0 (Overlays ‣ Guides, solo Material Preview) |
| Backface Culling olvidado encendido y "faltan caras" | Es el overlay, no la malla: apagarlo antes de diagnosticar agujeros reales (non-manifold se chequea aparte [ver: modelado/fundamentos-3d]) |
| Juzgar sombras/AO de EEVEE como verdad | EEVEE es screen-space (solo lo visible, 1 layer de depth — Limitations del manual); el AO del juego lo da Unity/bake |

## Fuentes

- **Viewport Shading — Blender 5.2 LTS Manual** (docs.blender.org/manual, Editors ‣ 3D Viewport ‣ Display) — la referencia exacta de los 4 modos, Solid options, Cavity, Material Preview y Rendered; base de §1-2 y §7.
- **Viewport Overlays — Blender 5.2 LTS Manual** (docs.blender.org/manual) — Statistics, Wireframe, Face Orientation, Measurement, Mesh Edit overlays, Retopology, Reference Spheres; base de §4.
- **Workbench (Introduction, Lighting, Options) — Blender 5.2 LTS Manual** (docs.blender.org/manual/render/workbench) — Workbench como engine, studio lights/matcaps, random color, cavity como settings de render; base de §2 y §8.
- **EEVEE (Introduction + Limitations) — Blender 5.2 LTS Manual** (docs.blender.org/manual/render/eevee) — EEVEE raster/PBR, y la lista oficial de limitaciones screen-space que fundamenta §7 y §10.
- **Cycles Introduction — Blender 5.2 LTS Manual** (docs.blender.org/manual/render/cycles) — definición de path tracer de producción; §8.
- **Preferences ‣ Lights — Blender 5.2 LTS Manual** (docs.blender.org/manual/editors/preferences) — studio lights editables, matcaps custom (EXR multicapa diffuse/specular), HDRIs de Material Preview; §2 y §9.
- **Principled BSDF — Blender 5.2 LTS Manual** (docs.blender.org/manual/render/shader_nodes) — modelo OpenPBR Surface y estructura de capas; §6.
- **Blender Python API: View3DShading, View3DOverlay, SceneDisplay, StudioLights, Material** (docs.blender.org/api/current) — nombres y enums exactos de todos los snippets (`color_type='SINGLE'`, `background_type='VIEWPORT'`, `show_stats`, `scene.display.shading`…).
- **Blender 5.0 Release Notes — EEVEE & Viewport + User Interface** (developer.blender.org/docs/release_notes/5.0) — matcaps renovados con specular, rename `BLENDER_EEVEE_NEXT`→`BLENDER_EEVEE`, rename "HDRI Preview"→"Reference Spheres", HDR con Vulkan; fecha release 18-nov-2025.
- **Blender 5.1 y 5.2 LTS Release Notes — EEVEE & Viewport** (developer.blender.org/docs/release_notes) — lookdev HDRI view-space + rotación mejorada, overlay de performance timing (5.1); overhaul de screen-space raytracing y Fast GI/AO (5.2).
- **Blender 4.2 LTS Release Notes — EEVEE** y **4.5 LTS — EEVEE & Viewport** (developer.blender.org/docs/release_notes) — la reescritura de EEVEE ("Next") y el estado de Vulkan; contexto de §8.
- **Repo oficial blender/blender — `release/datafiles/studiolights/`** (projects.blender.org) — lista literal de matcaps y HDRIs incluidos en 5.x (nombres de §2 y §7 verificados archivo por archivo).
- **Polycount Wiki — Spherical Environment Map (MatCap)** (wiki.polycount.com, vía archivo) — qué es un matcap (lookup por normal, imagen fija alineada a cámara) y su limitación estructural; fundamenta el protocolo de orbitar de §3.
