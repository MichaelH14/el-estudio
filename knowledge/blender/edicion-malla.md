# Edición de malla en Blender (Edit Mode)

> **Cuando cargar este archivo:** al operar Blender en Edit Mode — modelar, retopologizar, limpiar o reparar la malla de un asset de juego con las herramientas nativas (extrude, bevel, knife, normales, cleanup). La teoría agnóstica de topología y malla sana vive en [ver: modelado/fundamentos-3d] y [ver: modelado/topologia]; esto es la herramienta.

Verificado contra el manual oficial de **Blender 5.2 LTS** (docs.blender.org "latest", jul-2026) y las release notes oficiales 4.1→5.2. Blender 5.2 LTS salió el 14-jul-2026 (soporte hasta jul-2028). Mucho tutorial web es de 2.8–4.0 y en varios puntos (auto smooth sobre todo) ya no aplica.

## 1. Cambios de versión que invalidan contenido web viejo

| Versión | Cambio relevante en edit mode |
|---|---|
| **4.1** | Eliminada la propiedad "Auto Smooth" de la malla. La reemplazan: modificador node-group **Smooth by Angle** + operador de edit mode **Set Sharpness by Angle** (§5) |
| **4.2** | Nuevo operador **Shade Auto Smooth** (Object Mode) que añade el modificador Smooth by Angle y lo ancla al final del stack; los modificadores ahora se pueden "pin" al fondo |
| **5.0** (18-nov-2025) | Merge by Distance determinista + opción **Centroid** (default on); **Auto Merge** funciona también con Symmetrize y Bevel; el solver booleano "Fast" se renombró a **"Float"** |
| **5.1** | Bevel acepta snap (`Ctrl`) y precisión (`Shift`); selección de loops/rings con **delimitadores** (seam, sharp, material…) en el redo panel; **Corrective Flip Normals** (default on) al aplicar escala negativa; snap a face-center |
| **5.2 LTS** (14-jul-2026) | Operadores del addon Loop Tools integrados nativos: **To Circle**, **Space Edge Loops Evenly**, **Flatten** (menú Mesh ‣ Transform); la selección ahora atraviesa caras con back-face culling; merge interpola custom data de vértices |

## 2. Herramientas core

Atajos con keymap default (inglés). Casi todos los operadores son interactivos: `LMB`/`Return` confirma, `RMB`/`Esc` cancela, y las opciones se re-ajustan después en el panel **Adjust Last Operation** (esquina inferior izquierda).

| Herramienta | Menú exacto | Atajo | Uso típico en assets |
|---|---|---|---|
| Extrude | Mesh ‣ Extrude (menú) | `E` / `Alt`-`E` | Sacar volumen: brazos, cañones, ramas |
| Extrude to Cursor | — | `Ctrl`-`RMB` | Trazar cadenas de edges/caras clic a clic |
| Inset Faces | Face ‣ Inset Faces | `I` | Marco antes de extruir hacia dentro (paneles, ventanas) |
| Bevel | Edge ‣ Bevel Edges / Vertex ‣ Bevel Vertices | `Ctrl`-`B` / `Shift`-`Ctrl`-`B` | Romper filos duros; control loops |
| Loop Cut and Slide | Edge ‣ Loop Cut and Slide | `Ctrl`-`R` | Añadir resolución siguiendo el flujo |
| Knife | Mesh ‣ Knife Topology Tool | `K` | Cortes arbitrarios, rediseñar topología local |
| Connect Vertex Path | Vertex ‣ Connect Vertex Path | `J` | Corte exacto vértice a vértice (parte las caras del camino) |
| Merge | Mesh ‣ Merge / Context Menu ‣ Merge | `M` | Fusionar vértices; cerrar puntas |
| Delete / Dissolve | Mesh ‣ Delete | `X` / `Ctrl`-`X` | Quitar geometría vs. simplificar sin agujeros |
| New Edge/Face from Vertices | Vertex ‣ New Edge/Face from Vertices | `F` | Crear un edge o UN ngon desde la selección |
| Fill | Face ‣ Fill | `Alt`-`F` | Rellenar un loop cerrado con triángulos |
| Grid Fill | Face ‣ Grid Fill | — | Rellenar con rejilla de quads limpia |
| Bridge Edge Loops | Edge ‣ Bridge Edge Loops | — | Conectar dos loops (túneles, mangas, uniones) |

### Extrude y sus variantes (`Alt`-`E` abre el menú completo)

- **Extrude Faces** (`E`): crea caras nuevas en el borde y mueve la selección; por defecto por la normal media, `X`/`Y`/`Z` bloquea eje (2ª vez = eje local, 3ª = libre).
- **Extrude Faces Along Normals**: cada vértice se mueve por SU normal (en superficie convexa las caras crecen). Opción **Offset Even** (`S` o `Alt` durante el modal).
- **Extrude Individual Faces**: cada cara se extruye por separado por su propia normal.
- **Extrude Manifold**: como Extrude Faces pero con **Dissolve Orthogonal Edges** activado — al extruir hacia dentro corta y elimina caras adyacentes automáticamente (ideal para hundir volúmenes sin geometría interior).
- **Extrude to Cursor** (`Ctrl`-`RMB`): vértice suelto → edge; edges seleccionados → caras. Encadena clics para trazar. `Shift`-`Ctrl`-`RMB` evita la rotación automática del resultado.
- **Extrude Repeat**: N extrusiones iguales a lo largo de la dirección de vista.
- ⚠️ **Gotcha oficial** (manual, Extrude Faces): al cancelar con `RMB`/`Esc` "the newly created faces will still be there" — la geometría nueva SE QUEDA, duplicada sobre la vieja. Ver §8.

### Inset (`I`)

Modales: `I` de nuevo = **Individual** (por cara), `O` = **Outset** (hacia fuera), `B` = **Boundary** (también en bordes abiertos), `Ctrl` = ajustar **Depth**. **Offset Even** (default) mantiene grosor uniforme. Patrón estándar: `I` (marco) → `E` (extruir el panel).

### Bevel (`Ctrl`-`B` edges, `Shift`-`Ctrl`-`B` vértices)

`Wheel` = segmentos. Opciones modales clave (visibles en la status bar): **Width Type** `M` (Offset/Width/Depth/Percent/Absolute), **Segments** `S`, **Profile Shape** `P` (0.5 = arco circular), **Clamp Overlap** `C` (evita que el bevel se pase de las caras vecinas), **Harden Normals** `H` (custom normals para que el bevel se vea liso sin tocar el resto), **Loop Slide**, **Mark Seams** `U` / **Mark Sharp** `K` (propaga marcas a los edges nuevos), **Miter Outer/Inner** `O`/`I`, **Profile Type** `Z` (Superellipse/Custom con curva). Desde 5.1: `Ctrl` = snap a incrementos, `Shift` = precisión. **El ancho del bevel opera en espacio del objeto: con escala no aplicada sale desigual — aplicar escala primero (§8).**

### Loop Cut and Slide (`Ctrl`-`R`)

Paso 1: hover sobre un edge perpendicular al corte (preview amarillo), `Wheel` o número = cantidad de cortes, `LMB` confirma. Paso 2: deslizar; `LMB` = posición elegida, **`RMB` = exactamente al centro** (el idiom para cortes simétricos). Modales del slide: `E` Even, `F` Flipped, `C` Clamp (permite salirse del loop). **Correct UVs** mantiene las UVs sin distorsión al deslizar. Solo funciona sobre quads — un loop muere en tris/ngons/polos [ver: modelado/topologia].

### Knife (`K`)

Clic a clic o arrastrando; `Return`/`Spacebar` **confirma**, `Esc` cancela, `RMB` cierra el trazo actual y empieza otro. Para cortes que deben pasar EXACTAMENTE por vértices existentes es mejor `J` (Connect Vertex Path): conecta los vértices en el orden de selección partiendo las caras del camino (segunda ejecución cierra el loop); el Knife en cambio corta recto en pantalla. Modales: doble-clic `LMB` = cerrar loop, `C` = Cut Through (atraviesa caras ocultas), `X`/`Y`/`Z` = restricción de eje, `A` = Angle Constraint (2ª vez = relativo a un edge, `R` cambia la referencia), `Shift` = snap a punto medio de edge, `Ctrl` = ignorar snap. `Shift`-`K` = solo geometría seleccionada. **Knife Project** (Mesh ‣ Knife Project) proyecta el contorno de otro objeto como corte. Limitación documentada: clip range muy amplio puede crear vértices duplicados — subir Clip Start.

### Merge (`M`)

**At Center** / **At Cursor** / **Collapse** (cada isla a un vértice) / **At First** / **At Last** (solo en vertex mode y dependen del ORDEN de selección — usarlas justo tras seleccionar) / **By Distance** (clusters más cercanos que el umbral; default 0.0001 m). Opciones de By Distance: **Unselected** (permite fusionar con no-seleccionados), **Sharp Edges** (preserva filos si hay custom normals), **Centroid** (5.0+, posición media; off = usa el vértice original más cercano).

### Delete vs Dissolve (`X`)

| Operación | Qué hace | Resultado |
|---|---|---|
| Delete Vertices/Edges/Faces | Elimina la selección y lo que dependa de ella | **Agujero** en la malla |
| Only Edges & Faces / Only Faces | Elimina dejando vértices (y edges) huérfanos | Agujero + geometría suelta residual |
| **Dissolve** Vertices/Edges/Faces (`Ctrl`-`X`) | Elimina el elemento y FUSIONA las caras vecinas | Superficie **cerrada**, normalmente un ngon |
| **Limited Dissolve** | Disuelve todo lo casi-coplanar bajo **Max Angle** | Reducción brutal de polys en zonas planas |
| Collapse Edges & Faces | Colapsa cada parche conectado a un vértice, interpolando UVs/atributos | Reducción manual de detalle sin ngons |
| Edge Loops | Disuelve loops enteros (equivale a deshacer un loop cut) | Loop fuera, superficie intacta |

- Dissolve Edges tiene **Preserve Quads** (mantiene estructura de quads al disolver la diagonal de dos tris).
- Limited Dissolve tiene **Delimit**: Normal / Material / Seam / Sharp / UVs — imprescindible para no fundir bordes de material o de UV al decimar. Es un decimador rápido para props low-poly, pero deja ngons: triangular o re-quadificar después [ver: modelado/estilizacion-lowpoly].
- Regla mental: **agujero → Delete; simplificar → Dissolve**.

### Fill, Grid Fill, F y Bridge

- **`F`** (New Edge/Face from Vertices): 2 vértices → edge; 3+ → UNA cara (ngon). ⚠️ Sobre caras ya existentes `F` las **disuelve** (Dissolve Existing Faces).
- **Fill** (`Alt`-`F`): rellena un loop cerrado con **triángulos** (soporta agujeros interiores). Para tapar rápido, no para topología final.
- **Grid Fill**: rejilla de **quads** entre un loop rectangular o dos lados opuestos; opciones **Span** (columnas) y **Offset** (rota qué vértice es la esquina, parte del vértice activo), **Simple Blending** para superficies planas. Mejor con el mismo número de vértices por lado. El error "Loops are not connected by wire/boundary edges" significa: las cadenas seleccionadas no forman un circuito cerrado — conectar antes.
- **Bridge Edge Loops**: borra las caras seleccionadas y conecta 2+ loops. **Connect Loops** (Open/Closed/Loop Pairs), **Merge** (+Merge Factor) para fusionar en vez de puentear, **Twist** corrige torsión, **Number of Cuts** + **Interpolation** (Linear / Blend Path / Blend Surface) para puentes suaves. Los loops pueden tener distinto número de vértices.
- Tapa de cilindro game-ready: Grid Fill (o triangle fan con `F`+Poke) — nunca un ngon gigante [ver: modelado/topologia].

### Utilidades ex-Loop Tools (nativas desde 5.2)

En Mesh ‣ Transform, integradas desde el addon Loop Tools (release notes 5.2 — antes había que habilitar el addon):

| Operador | Qué hace | Uso típico |
|---|---|---|
| **To Circle** | Redondea la selección a un círculo perfecto | Preparar un boolean circular, arreglar boquetes ovalados antes de Bridge |
| **Space Edge Loops Evenly** | Redistribuye los vértices de los loops a espaciado uniforme | Loops apretados tras varios loop cuts deslizados |
| **Flatten** | Aplana la selección a un plano | Caras que deben quedar coplanares (bases, monturas) |

## 3. Selección avanzada

| Acción | Cómo | Nota operativa |
|---|---|---|
| Edge loop | `Alt`-`LMB` (añadir: `Shift`-`Alt`-`LMB`) | Con Emulate 3 Button Mouse: doble-clic `LMB` |
| Edge ring | `Ctrl`-`Alt`-`LMB` | En vertex mode selecciona el face loop |
| Face loop | `Alt`-`LMB` sobre un edge en face mode | Perpendicular al edge clicado |
| Linked | `Ctrl`-`L` (o `L` con hover; `Shift`-`L` deseleccionar) | **Delimit**: Seam/Sharp/Material/UVs/Normal — aísla islas |
| Shortest Path | `Ctrl`-`LMB` sobre el destino | Select ‣ Select Linked ‣ Shortest Path |
| Select Similar | `Shift`-`G` | Menú según modo (ver abajo) |
| Checker Deselect | Select ‣ Checker Deselect | Patrón alterno; solo afecta la isla del elemento ACTIVO |
| Select All by Trait | Select ‣ Select All by Trait | Diagnóstico de malla (§6) |
| Loops → región | Select ‣ Select Loops ‣ Select Loop Inner-Region | Caras dentro de un loop cerrado |
| Boundary Loops | Select ‣ Select Loops ‣ Boundary Loops | Expande a todo el borde abierto |

- **Shortest Path** hace más que seleccionar: en el redo panel, **Edge Tag** permite `Tag Seam` / `Tag Sharp` / `Tag Crease` / `Tag Bevel` directamente sobre el camino — la forma rápida de marcar seams de UV a lo largo de una ruta. `Shift`-`Ctrl`-`LMB` = Fill Region (todos los caminos posibles). **Topology Distance** cuenta edges en vez de distancia.
- **Select Similar** (`Shift`-`G`) por modo — vértices: Normal, Amount of Adjacent Faces, Vertex Groups…; edges: Length, Direction, Face Angles, Seam, **Sharpness**…; caras: **Material**, Area, **Polygon Sides**, Normal, Coplanar, Flat/Smooth. Con Compare Equal/Greater/Less + Threshold. Ejemplo real: seleccionar una cara de 5 lados → `Shift`-`G` ‣ Polygon Sides = todos los ngons de ese tamaño.
- **Checker Deselect** (API: `select_nth`): base de operaciones periódicas (borrar loops alternos para decimar un cilindro).
- 5.1+: los select de loop/ring/face-loop aceptan **delimitadores** (seam, sharp, material, esquinas de boundary) en el redo panel.
- **Select All by Trait ‣ Non Manifold solo aparece en vertex/edge mode** — si se opera por script/MCP, fijar antes `bpy.ops.mesh.select_mode(type='EDGE')`.

## 4. Proportional Editing

- Toggle `O` (icono en el header). Durante el transform: `Wheel`/`PageUp`/`PageDown` cambia el radio (círculo gris), `Shift`-`O` pie de falloff (Smooth default; Constant, Linear, Sharp, Sphere, Root, Random, Inverse Square).
- **Connected Only** (`Alt`-`O`): el falloff viaja por la topología, no por distancia 3D — editar un dedo sin arrastrar los demás. Solo en Edit Mode.
- **Projected from View**: ignora la profundidad (útil para terreno visto desde arriba).
- **Cuándo sí**: ajustes orgánicos amplios sobre malla densa (silueta de terreno, inflar un cachete, corregir proporción sin sculpt [ver: sculpt]). **Cuándo no**: hard-surface de precisión, y NUNCA con extrude (el propio manual: mueve las caras vecinas junto con la extrusión, "not very useful").
- ⚠️ Es un estado global pegajoso: quedó activado → "muevo un vértice y media malla lo sigue". Chequear el icono/`O` antes de culpar a otra cosa.

## 5. Normales y shading (estado 4.1+ / 5.x)

### Operaciones base

| Operación | Menú | Atajo |
|---|---|---|
| Recalcular hacia fuera | Mesh ‣ Normals ‣ Recalculate Outside | `Shift`-`N` |
| Recalcular hacia dentro | Mesh ‣ Normals ‣ Recalculate Inside | `Shift`-`Ctrl`-`N` |
| Voltear selección | Mesh ‣ Normals ‣ Flip | — |
| Marcar filo | Edge ‣ Mark Sharp (popover: `Ctrl`-`E`) | — |
| Sharp por ángulo (edit) | Edge ‣ Set Sharpness by Angle | — |
| Shade Smooth/Flat por cara | Face ‣ Shade Smooth / Shade Flat | — |
| Menú Normals popover | — | `Alt`-`N` |

- Diagnóstico visual: overlay **Face Orientation** del viewport (azul = fuera, rojo = dentro). Recalculate funciona aunque la malla no sea un volumen cerrado, pero en geometría non-manifold puede decidir mal — ahí Flip manual.
- La marca **Sharp** se guarda en el atributo `sharp_edge` y la usan: el shading (vértice con 2+ edges sharp = filo duro), el modificador **Smooth By Angle**, **Weighted Normal**, **Edge Split**, y el **export de smoothing groups a FBX/OBJ** — marcar sharp no es cosmético, viaja al engine [ver: modelado/fundamentos-3d].

### Auto Smooth: el cambio 4.1 y el estado actual en 5.x

| Época | Mecanismo |
|---|---|
| ≤ 4.0 | Propiedad "Auto Smooth" + ángulo en Object Data Properties (lo que enseñan los tutoriales viejos — **ya no existe**) |
| 4.1 | Reemplazada por el node-group **Smooth by Angle** (asset de modificador). El estado base de toda malla equivale a "Auto Smooth on a 180°": mezcla sharp/smooth ya genera split normals solos |
| 4.2 → 5.2 (actual) | **Object ‣ Shade Auto Smooth** añade el modificador **Smooth By Angle** anclado al final del stack (Angle = umbral). **Object ‣ Shade Smooth y Shade Flat ELIMINAN ese modificador** (con opción Keep Sharp Edges). En Edit Mode, **Edge ‣ Set Sharpness by Angle** hace lo mismo pero destructivo (escribe `sharp_edge` una vez, no sigue la geometría) |

Receta para un asset de juego en 5.2: `Shade Auto Smooth` con ángulo ~30–45°, revisar filos con matcap [ver: materiales-preview], ajustar edges concretos con Mark Sharp/Clear Sharp, y **aplicar u hornear el modificador antes de exportar** si el exportador no evalúa modificadores [ver: import-export]. API verificada: `bpy.ops.object.shade_auto_smooth(angle=...)`, `bpy.ops.object.shade_smooth_by_angle`, `bpy.ops.mesh.set_sharpness_by_angle(angle=..., extend=...)`.

### Custom split normals

Menú `Alt`-`N`: Set From Faces, Rotate, Point to Target, Merge, Split, Average, Smooth Vectors, Reset Vectors. Dos advertencias del manual: **Flip y Recalculate NO tocan las custom split normals** (una malla importada con custom normals puede seguir viéndose mal tras recalcular — límpialas en Object Data Properties ‣ Geometry Data ‣ Clear Custom Split Normals Data); y Merge/Split de normales aplican además smooth/flat + marcas sharp. Para foliage/anime se editan a propósito (Point to Target, Data Transfer desde una esfera).

## 6. Limpieza de malla

Secuencia estándar sobre malla completa (`A` = seleccionar todo) antes de UVs/export — el porqué de cada punto en el checklist de malla sana de [ver: modelado/fundamentos-3d]:

1. **Mesh ‣ Merge ‣ By Distance** (doubles fuera; subir umbral con cuidado — 0.0001 default).
2. **Mesh ‣ Clean up ‣ Delete Loose** (vértices/edges huérfanos; caras sueltas opcional).
3. **Mesh ‣ Clean up ‣ Degenerate Dissolve** (edges/caras de tamaño ~0 que Merge by Distance no coge por no estar conectados).
4. **Select ‣ Select All by Trait ‣ Interior Faces** → inspeccionar y borrar (caras accidentales dentro del volumen; detecta edges con 3+ caras).
5. **Select ‣ Select All by Trait ‣ Non Manifold** (en edge mode): Wire, Boundaries (agujeros), Multiple Faces, Non Contiguous (dos caras con normales opuestas = flip pendiente).
6. **Mesh ‣ Clean up ‣ Fill Holes** (Sides = 0 rellena todos) si el asset debe ser cerrado.
7. `Shift`-`N` Recalculate Outside + overlay Face Orientation.
8. **Select ‣ Select All by Trait ‣ Faces by Sides** > 4 → localizar ngons restantes.
9. Object Mode: aplicar escala/rotación (`Ctrl`-`A` ‣ Rotation & Scale).

Patrón bpy equivalente (operadores verificados en la API 5.x):

```python
import bpy
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_mode(type='EDGE')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.remove_doubles(threshold=0.0001)   # Merge by Distance
bpy.ops.mesh.delete_loose(use_verts=True, use_edges=True, use_faces=False)
bpy.ops.mesh.dissolve_degenerate()
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)  # Recalculate Outside
# diagnóstico, no destruye: dejar seleccionado lo problemático
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.mesh.select_non_manifold(use_wire=True, use_boundary=True,
                                 use_multi_face=True, use_non_contiguous=True)
bpy.ops.object.mode_set(mode='OBJECT')
```

Tras el `select_non_manifold`, contar la selección (p. ej. `sum(v.select for v in mesh.vertices)` tras `mode_set(mode='OBJECT')`) — si no es 0 en una malla que debía ser cerrada, investigar antes de seguir [ver: bpy-scripting].

Otros de Mesh ‣ Clean up: **Decimate Geometry** (ratio de tris, con simetría), **Make Planar Faces**, **Split Non-Planar Faces**, **Split Concave Faces** — útiles antes de export a colisiones que exigen caras planas/convexas [ver: pipeline/arte-a-unity].

## 7. Retopología con herramientas nativas

Flujo documentado por el manual (página Retopology): objeto nuevo sobre el high-poly → overlay **Retopology** (ver la malla nueva a través de la vieja sin el ruido de X-Ray) → **Poly Build** + **Snapping** + **Auto Merge**.

- **Snapping** (`Shift`-`Tab` toggle; popover en el header): Snap Target **Face** = "pegar a superficie" clásico mientras mueves; **Face Project** proyecta cada vértice individualmente a lo largo de la vista; **Face Nearest** pega cada vértice a la cara más cercana (funciona con geometría ocluida). Activar **Backface Culling** en las opciones de snap para no pegarse a la cara trasera. Para congelar el resultado no-destructivamente: modificador **Shrinkwrap** [ver: modificadores].
- **Auto Merge** (Sidebar ‣ Tool ‣ Options): fusiona automáticamente al soltar un vértice sobre otro (Threshold configurable) — esencial en retopo para soldar sin pasar por `M`. Desde 5.0 también lo respetan Symmetrize y Bevel. ⚠️ Apagarlo al terminar: activado globalmente destruye geometría en edición normal.
- **Poly Build** (Toolbar): `Ctrl`-`LMB` añade vértice/tri (preview azul), `Shift`-`LMB` borra (resalta rojo), arrastrar un edge lo extruye a quad, arrastrar un vértice lo mueve. Con **Create Quads** activado convierte pares de tris en quads solo.
- Remesh automático (Voxel/Quad en Properties ‣ Data ‣ Remesh) ≠ retopo: el propio manual avisa de que ninguna herramienta automática produce topología de deformación — para personajes animados la retopo es manual [ver: modelado/high-to-low].
- **Addons** (estado jul-2026): **RetopoFlow** (CGCookie/Orange Turbine) sigue activo — v3.4.10 (ene-2026), código GPL-3.0, gratis desde GitHub Releases y de pago con soporte en Superhive Market (ex-Blender Market); su tabla oficial dice "Blender 3.6 or later", compatibilidad concreta con 5.2 NO VERIFICADA — probar en un .blend desechable antes de confiarle trabajo. En extensions.blender.org no hay (a jul-2026) una suite de retopo dominante equivalente. Para assets low/mid-poly de juego, Poly Build + snap + Shrinkwrap suele bastar sin addons.

## Reglas prácticas

- [ ] Antes de editar: escala aplicada (`Ctrl`-`A` ‣ Rotation & Scale en Object Mode). Bevel, Inset y los umbrales de merge operan mal con escala ≠ 1.
- [ ] Todo operador interactivo: confirmar `LMB`/`Return`, cancelar `RMB`/`Esc` — y recordar que **cancelar un extrude NO borra la geometría creada**.
- [ ] Tras cualquier `Esc` dudoso en extrude: `M` ‣ By Distance inmediato.
- [ ] Ajustar parámetros SIEMPRE en Adjust Last Operation, no repitiendo el operador a ojo.
- [ ] Loop cut al centro exacto: `Ctrl`-`R` → `LMB` → `RMB`.
- [ ] Agujero → Delete; simplificar → Dissolve (`Ctrl`-`X`); decimar zonas planas → Limited Dissolve con Delimit Seam+Sharp+Material.
- [ ] `F` con caras seleccionadas DISUELVE en vez de crear — deseleccionar caras antes de rellenar.
- [ ] Filos de juego: Shade Auto Smooth (30–45°) + Mark Sharp puntual; nunca buscar la propiedad "Auto Smooth" de los tutoriales ≤4.0 — ya no existe.
- [ ] Sharp marcado = smoothing groups en FBX/OBJ: revisar filos ANTES de exportar [ver: import-export].
- [ ] Normales: `Shift`-`N` + overlay Face Orientation como reflejo tras cualquier modelado con extrudes/bridges; en mallas importadas, limpiar custom split normals si el shading no responde.
- [ ] Checklist de limpieza (§6) completo antes de UVs y de export — en ese orden.
- [ ] Select All by Trait es el detector: Non Manifold (edge mode), Interior Faces, Loose Geometry, Faces by Sides, Poles by Count (los polos pellizcan con Subdivision).
- [ ] Marcar seams por rutas largas: `Ctrl`-`LMB` shortest path + Edge Tag ‣ Tag Seam.
- [ ] Proportional editing (`O`) y Auto Merge son estados globales pegajosos: verificar su estado al entrar y salir de una tarea.
- [ ] Retopo: overlay Retopology + snap Face (+Backface Culling) + Auto Merge + Poly Build; congelar con Shrinkwrap [ver: modificadores].
- [ ] Vía script/MCP: usar solo operadores verificados en la API (§6); tras cada operación destructiva, contar vértices/caras y comparar con lo esperado — un operador que "no hizo nada" también es un bug [ver: blender-mcp-operativo].
- [ ] En 5.2, antes de buscar un addon para redondear/espaciar loops: To Circle, Space Edge Loops Evenly y Flatten ya son nativos (Mesh ‣ Transform).

## Errores comunes

| Síntoma | Causa | Fix |
|---|---|---|
| Shading rayado/raro en un borde; Merge by Distance reporta "Removed N vertices" inesperados | **Doubles por extrude cancelado con `Esc`** — la geometría nueva quedó superpuesta (documentado en el manual) | `A` → `M` ‣ By Distance; prevención: cancelar y además `Ctrl`-`Z` |
| Caras negras/invisibles en el engine o con backface culling; bake con manchas | **Normales invertidas** | Overlay Face Orientation → `Shift`-`N` (o Flip selectivo); si persiste: custom split normals heredadas → Clear Custom Split Normals Data |
| Bevel desigual (más ancho en un eje), umbrales de merge que no cuadran | **Escala no aplicada** (p. ej. 1, 1, 3) | Object Mode: `Ctrl`-`A` ‣ Rotation & Scale. Con escala NEGATIVA, 5.1+ voltea normales solo (Corrective Flip Normals, default on); en versiones previas quedaban invertidas |
| "Muevo un vértice y media malla lo sigue" | Proportional Editing quedó activado | `O` (o icono del header); radio con `Wheel` durante el transform |
| Vértices que se "tragan" a otros al moverlos | Auto Merge activado de una sesión de retopo | Sidebar ‣ Tool ‣ Options ‣ desactivar Auto Merge |
| `Alt`-`LMB` no selecciona loops | Emulate 3 Button Mouse se come el `Alt` | Doble-clic `LMB`, o desactivar la emulación en Preferences ‣ Input |
| Loop cut no cruza toda la malla | El loop muere en un tri, ngon o polo | Localizar con Faces by Sides / Poles by Count y reparar el flujo [ver: modelado/topologia] |
| Grid Fill: "Loops are not connected by wire/boundary edges" | Las cadenas seleccionadas no forman circuito cerrado | Conectar los extremos (F) o seleccionar exactamente dos lados opuestos |
| Tras dissolve, Subdivision/Bevel pellizcan | El dissolve dejó ngons | Faces by Sides > 4 → re-cortar con Knife/Connect Vertex Path |
| El modelo exportado pierde los filos suaves/duros | Smooth By Angle sin aplicar u opciones de export sin smoothing | Aplicar el modificador (o export que evalúe modificadores) + revisar smoothing groups [ver: import-export] |
| Knife crea vértices duplicados | Clip range demasiado amplio (limitación documentada) | Subir Clip Start del viewport y repetir el corte |
| "Interior Faces no encuentra la cara interna que estoy viendo" | El operador solo detecta caras con vecinos anómalos (edges de 3+ caras), no toda cara "dentro" | Complementar con Select Linked por islas y X-Ray + box select |

## Fuentes

- **Blender 5.2 Manual — Editing Mesh Objects** (extrude, bevel, inset, loop cut, knife, merge, delete & dissolve, fill/grid fill, bridge, normals, cleanup, shading) — docs.blender.org/manual/en/latest/modeling/meshes/editing/ — Blender Foundation. Fuente primaria de cada operador, menú y atajo citado; versión "latest" = 5.2 (verificado jul-2026).
- **Blender 5.2 Manual — Selecting (meshes)** — docs.blender.org …/modeling/meshes/selecting/ — Checker Deselect, Select Similar, Select Linked/Shortest Path, All by Trait, Loops/Boundary Loops.
- **Blender 5.2 Manual — 3D Viewport Controls: Proportional Editing y Snapping** — docs.blender.org …/editors/3dview/controls/ — falloffs, Connected Only, Snap Base/Target, Face Project/Nearest.
- **Blender 5.2 Manual — Poly Build, Retopology, Tool Settings (Auto Merge), Object Shading, Apply** — docs.blender.org — flujo de retopo nativo, Shade Auto Smooth/Smooth By Angle en 5.x, Corrective Flip Normals.
- **Blender 4.1 Release Notes — Modeling** — developer.blender.org/docs/release_notes/4.1/ — la eliminación de Auto Smooth y sus reemplazos exactos (la fuente del cambio que invalida los tutoriales viejos).
- **Blender 4.2 Release Notes — Modeling & UV** — developer.blender.org — operador Shade Auto Smooth + pin de modificadores.
- **Blender 5.0 / 5.1 / 5.2 Release Notes** — developer.blender.org/docs/release_notes/ — fechas de release, Merge by Distance/Centroid, Auto Merge en Symmetrize/Bevel, bevel snap, delimitadores de loops, Loop Tools nativos en 5.2.
- **Blender Python API (current) — bpy.ops.mesh / bpy.ops.object** — docs.blender.org/api/current/ — verificación de cada nombre de operador y parámetro del snippet (remove_doubles, normals_make_consistent, set_sharpness_by_angle, select_non_manifold, etc.).
- **RetopoFlow — repo CGCookie/retopoflow (GitHub)** — README, releases (v3.4.10, ene-2026) y licencia — estado real del addon de retopo de referencia.
- **extensions.blender.org** — búsqueda "retopology" (jul-2026) — panorama de retopo en la plataforma oficial de extensiones.
