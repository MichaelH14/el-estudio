# Sculpt Mode: esculpido digital para assets de juego

> **Cuando cargar este archivo:** siempre que vayas a entrar en Sculpt Mode (organico, personajes, criaturas, rocas, detalle high-poly para bake), a decidir entre Dyntopo / Multires / Voxel Remesh, o a convertir un sculpt en asset de juego. Version de referencia: Blender 5.x (stack local: 5.2 LTS). Teoria de cuando esculpir: [ver: modelado/organico-personajes].

## Cuando esculpir y cuando no

| Caso | Camino | Por que |
|---|---|---|
| Personaje/criatura organica | Sculpt → retopo | La forma manda; la topologia se hace despues limpia [ver: modelado/high-to-low] |
| Roca, tronco, escombro (prop estatico) | Sculpt → Decimate o retopo rapida | No deforma; la topologia fea se tolera |
| Detalle de superficie (arrugas, danio, tela) sobre un modelo ya topologizado | Multires encima del low | El bake de normal map sale directo del multires |
| Hard-surface mecanico, arquitectura, props con aristas exactas | Poly-modeling directo, NO sculpt | Bevels y medidas exactas se controlan mejor con edicion de malla [ver: edicion-malla] |
| Low-poly estilizado con presupuesto muy bajo | Poly-modeling directo | Esculpir para luego tirar 99% del detalle es desperdicio |
| Blockout/silueta rapida de algo organico | Sculpt con Voxel Remesh | Iterar silueta es mas rapido que mover vertices |

Regla: **el sculpt nunca es el asset final de juego**. Siempre termina en retopo + bake, o en decimate + bake, o se descarta como referencia. El flujo esculpido→retopo vs modelado directo esta desarrollado en [ver: modelado/organico-personajes].

## Cambios 4.x → 5.x que invalidan tutoriales viejos

Mucho contenido web es de 2.8–4.2. Verificado contra manual 5.2 LTS y release notes oficiales:

| Cambio | Version | Detalle |
|---|---|---|
| Brushes = assets | 4.3 | Los brushes viven en asset libraries (la "Essentials" trae 130). Se eligen en el **Asset Shelf** (franja inferior del viewport) o popup con `Shift`-`Spacebar` / click en el thumbnail del brush. El toolbar ya no es la via principal |
| `bpy.ops.paint.brush_set` ELIMINADO | 4.3 | Reemplazo: `bpy.ops.brush.asset_activate(...)` (snippet abajo) |
| Rewrite de performance | 4.3 | Entrar a Sculpt Mode ~5x mas rapido, brushes ~8x, memoria −30% |
| Brush **Plane** unifica Flatten/Fill/Scrape | 4.4 | Un solo brush type con Height/Depth y estabilizacion. Los tutoriales que dicen "Flatten brush" → hoy es Plane |
| Trim tools con solver **Manifold** | 4.5 | Nueva opcion de Solver (junto a Exact y Float), normalmente la mas rapida pero solo funciona en mallas manifold; cual es el default exacto en 5.2 no esta confirmado en el manual — revisar el dropdown Solver en Tool Settings antes de asumirlo |
| Brush size = **diametro**, no radio | 5.0 | Rompe scripts viejos que seteaban `size` pensando en radio |
| Simetria radial por-objeto (mesh property) | 5.0 | Antes era de escena |
| Pressure toggles quitados de Grab, Snake Hook, Elastic Deform, Pose, Boundary, Thumb, Rotate | 5.0 | Esos brushes no soportan presion de tableta |
| Brush **Blur** dedicado | 5.1 | Nuevo asset esencial |
| Mask brush temporal con `Alt`-`LMB` | 5.1 | `Ctrl`-`Alt`-`LMB` = borrar mascara temporal |
| Brush **Scene Project** + Add Primitive tools en Sculpt Mode | 5.2 | Proyectar contra otros objetos (tipo Shrinkwrap); anadir Cube/Cone/etc. sin salir del modo |
| Voxel remesher interpola atributos (color) | 5.2 | Antes escoger el punto mas cercano "scrambleaba" el vertex paint |

## Los tres caminos de densidad

Fuente: manual 5.2, seccion "Adaptive Resolution". Son mutuamente excluyentes en gran parte: **Voxel Remesh no funciona con Multires**, y Dyntopo y Voxel Remesh comparten atajos porque no coexisten.

| | Voxel Remesh | Dyntopo | Multires (modificador) |
|---|---|---|---|
| Que hace | Reconstruye TODA la malla con densidad uniforme a partir del volumen | Teselacion dinamica bajo el brush durante el stroke | Subdivision tipo Catmull-Clark editable por niveles |
| Atajos | `R` = voxel size (grid interactivo, `Shift` = precision), `Ctrl`-`R` = ejecutar | `R` = detail size, `Ctrl`-`R` = Detail Flood Fill (solo Constant/Manual) | `Alt`-`1` bajar nivel, `Alt`-`2` subir, `Ctrl`-`0`..`Ctrl`-`5` fijar nivel/crear modificador |
| Pros | Uniforme, elimina overlaps, resultado manifold; reproyecta mask/face sets/colores | Detalle donde lo necesitas sin pensar en resolucion; ideal blockout de formas complejas | Niveles: proporciones en nivel 1, detalle en nivel 4+; viewport en nivel bajo; bake directo de normal/displacement |
| Contras | Pierde data layers del mesh; exige volumen cerrado (huecos > voxel size lo rompen); ignora modificadores/shape keys | Mas lento; **pierde/corrompe UVs, Color Attributes y Face Sets**; malla irregular | Exige base mesh limpio (quads, sin caras non-manifold); NO tocar la topologia base tras subdividir (corrompe niveles); >5 niveles degrada performance |
| Para que fase | Blockout/formas primarias, fusionar partes | Formas con Snake Hook/Clay Strips/Density, esculpido exploratorio | Detalle secundario/terciario sobre malla final o retopo |
| Config | Tool Settings ‣ Remesh (header) o Sidebar ‣ Tool ‣ Remesh; Adaptivity>0 desactiva Fix Poles | Sidebar ‣ Tool ‣ Dyntopo; Refine Method: Subdivide/Collapse/ambos; Detail: Relative/Constant/Brush/Manual | Modificador Multiresolution: Subdivide, Unsubdivide, Delete Higher, Apply Base, Conform Base (5.0+), Rebuild Subdivisions |

Detalles operativos verificados:

- **Voxel Remesh con huecos**: rellenar antes con Edit Mode o con **Mask ‣ Mask Slice** + Fill Holes (sin mascara activa, solo rellena huecos).
- **Multires para un sculpt ya denso**: *Rebuild Subdivisions* reconstruye niveles inferiores y genera un base mesh optimizado (solo disponible si el modificador aun no tiene niveles creados).
- **Multires + Shrinkwrap** (wrap Project, snap Above Surface, Negative on) reproyecta detalle de otro sculpt — es el truco estandar para transferir detalle al retopo.
- **Sculpt Base Mesh** (opcion del Multires): deforma el nivel base mientras previsualizas el nivel alto — cambios amplios sin ruido.
- Dyntopo en 5.2 ya no pide confirmacion al reactivarse al volver a Sculpt Mode.
- Draw Sharp NO remalla bajo Dyntopo; con Dyntopo usa Crease para cortes afilados (nota del propio manual).

## Brushes clave (nombres exactos 5.2)

Seleccion: Asset Shelf (abajo del viewport) o `Shift`-`Spacebar`. Controles universales: `F` = size interactivo, `Shift`-`F` = strength, `Ctrl` mientras esculpes = invertir direccion (Add↔Subtract), `Shift` mantenido = Smooth temporal, `Alt`-`LMB` = Mask temporal (5.1+).

| Brush | Que hace (manual 5.2) | Fase |
|---|---|---|
| **Clay Strips** | Clay con punta cuadrada (Tip Roundness bajo); construye/quita volumen aplanando detalle; "fast rough pass" de todo el sculpt | Primaria/secundaria — EL brush de construccion |
| **Grab** | Mueve los vertices bajo el radio al inicio del stroke; sin presion de tableta (5.0). Opciones: Grab Active Vertex (low-poly), Grab Silhouette, falloff Projected = grab 2D infinito | Primaria — silueta y proporciones |
| **Snake Hook** | Arrastra soltando/recogiendo geometria; Magnify >0.5 conserva volumen; Rake rota; modo Elastic | Primaria — cuernos, mechones, extremidades. Ideal con Dyntopo |
| **Draw** | Add/subtract generico; el que se customiza con texturas y stroke methods (alphas VDM) | Secundaria/terciaria |
| **Draw Sharp** | Draw desde coordenadas originales + falloff Sharper; Subtract por defecto. Arrugas de tela, pelo estilizado, aristas hard-surface. **Equivale al Dam Standard de ZBrush** | Terciaria (mallas densas) |
| **Crease** | Draw + Pinch: hendiduras/crestas afiladas, pulir creases existentes; parametro Pinch (0 = Draw puro) | Secundaria/terciaria. Con Dyntopo, preferido sobre Draw Sharp |
| **Smooth** | Suaviza y encoge superficies, quita ruido; se invoca sosteniendo `Shift` | Todas |
| **Plane** (4.4+) | Empuja vertices hacia/desde un plano virtual; Height/Depth limitan el rango; Stabilize Normal/Plane para pasadas largas. Sustituye Flatten, Fill y Scrape | Secundaria — planos faciales, hard-surface esculpido |
| **Inflate** | Infla/encoge; controlar grosor de formas cilindricas | Secundaria |
| **Pinch** | Junta vertices hacia el centro; afilar transiciones | Terciaria |
| **Scrape Multiplane** | Raspa con dos planos en angulo; aristas mecanicas | Secundaria hard-surface |
| **Blur** (5.1+) | Suavizado dedicado sin el shrink del Smooth | Pulido |
| **Mask** / **Draw Face Sets** | Pintan mascara / face sets a mano | Organizacion |
| **Elastic Deform / Pose / Boundary / Cloth** | Deformaciones globales elasticas, posado con pivote, bordes, simulacion de tela | Ajustes gruesos y tela |
| **Layer** | Altura acumulativa con tope (persistent base) | Detalle mecanico/placas |
| **Scene Project** (5.2+) | Proyecta vertices contra superficies de otros objetos de la escena | Conformar piezas |

En la Essentials library los assets pueden tener nombres derivados: el asset "Crease Polish" usa el brush type Crease (renombrado en 4.3 para diferenciarlo); existen "Crease Sharp", "Grab 2D", "Grab Silhouette", "Elastic Snake Hook", "Pull", "Plateau", "Trim" como variantes preconfiguradas (4.3+).

## Flujo de bloqueo: primario → secundario → terciario

Jerarquia estandar del oficio (la aplica Blender Studio en su curso de personajes: blockout con primitivas → formas → pulido → retopo):

| Fase | Objetivo | Densidad | Brushes |
|---|---|---|---|
| **Primaria (silueta)** | Proporciones y masas grandes; se juzga EN silueta (matcap plano o vista a contraluz) | Bajisima: 10–50k voxel remesh; remesh frecuente con `Ctrl`-`R` | Grab, Snake Hook, Clay Strips grande, Move/Trim gestures |
| **Secundaria (planos)** | Planos anatomicos, grupos musculares, pliegues grandes | Media: 100k–1M (voxel remesh mas fino o primeros niveles de Multires) | Clay Strips, Plane, Inflate, Crease grande, Scrape Multiplane |
| **Terciaria (detalle)** | Arrugas, poros, danio, costuras — solo lo que sobrevive al bake de normal map | Alta: Multires niveles 3–5 | Draw Sharp, Crease, Pinch, Draw con alphas/texturas, Layer |

Reglas del flujo (practicas de produccion del curso de Blender Studio + manual):

1. **Bloquear con primitivas separadas** (cabeza, torso, extremidades como objetos aparte) — cada objeto mantiene su propia resolucion; se fusionan (Join + Voxel Remesh) cuando la silueta esta aprobada.
2. **No subir de densidad hasta agotar la fase actual.** El detalle fino sobre proporciones malas se tira entero.
3. Congelar silueta antes de planos; congelar planos antes de detalle.
4. Simetria activa hasta que el diseno pida asimetria; romperla lo mas tarde posible.
5. Para juego: la fase terciaria vive en Multires sobre el retopo (o sobre el sculpt a bake-ar) — nunca inviertas horas de detalle en una malla que vas a remallar.

## Setup de sesion y herramientas globales

- El template **Sculpting** (File ‣ New ‣ Sculpting) arranca con una malla lista y overlays de sculpt activados por defecto (5.0+). Para evaluar forma: matcap plano/clay y girar a contraluz; para evaluar creases: matcap con specular [ver: materiales-preview]. El curso de Blender Studio publica matcaps y base meshes de produccion.
- **Filters** (herramientas de toolbar, actuan sobre TODA la malla o lo no mascarado): Mesh Filter (`bpy.ops.sculpt.mesh_filter`, type INFLATE/SMOOTH/etc.), Cloth Filter (gravedad/simulacion global), Color Filter. Utiles para "asentar" un sculpt completo sin strokes.
- **Transforms en Sculpt Mode**: Move/Rotate/Scale operan sobre lo no mascarado con pivote configurable (`bpy.ops.sculpt.set_pivot_position`) — posar sin salir del modo.
- **Add Primitive** (5.2+): Add Cube/Cone/Cylinder etc. directamente en Sculpt Mode para kitbash de blockout.
- **Multi-objeto**: Sculpt Mode NO tiene multi-object editing (a diferencia de Edit Mode); el manual recomienda `Alt`-`Q` apuntando a otro objeto para cambiar de objeto sin salir del modo. Repartir la geometria entre varios objetos ademas mejora el rendimiento; al hacer Join, cada pieza recibe su Face Set automaticamente (si ya usabas Face Sets).

## Mascaras y Face Sets: trabajar por partes

Mascara = vertices protegidos (NO editables — modelo invertido respecto a seleccion). Face Sets = grupos de caras coloreados para aislar/ocultar rapido.

| Accion | Atajo 5.2 |
|---|---|
| Pie de mascara (Clear, Invert, filtros Grow/Shrink/Smooth/Contrast) | `A` |
| Invertir mascara | `Ctrl`-`I` |
| Limpiar mascara | `Alt`-`M` (o via `A`) |
| Box Mask | `B` (con `Shift` o `MMB` = restar) |
| Lasso Mask | `Ctrl`-`RMB` (cambio de keymap; en 2.8–3.x era otro gesto) |
| Mask brush temporal / borrar | `Alt`-`LMB` / `Ctrl`-`Alt`-`LMB` (5.1+) |
| Expand Mask by Topology (modal, falloff Geodesic; `1`–`4` cambian falloff) | `Shift`-`A` |
| Expand Face Set | `Shift`-`W` |
| Pie de Face Sets (crear de masked/visible, visibilidad, invert) | `Alt`-`W` |
| Grow / Shrink face set bajo el cursor | `Ctrl`-`W` / `Ctrl`-`Alt`-`W` |
| Ocultar face set bajo cursor / aislar (o mostrar todo) | `H` / `Shift`-`H` |
| Pie de Auto-Masking | `Alt`-`A` |

- Operadores de menu utiles: **Mask ‣ Mask from Cavity** (mascara por curvatura — base para suciedad/danio), Mask by Color, Mask from Mesh Boundary, **Mask Extract** (extrae la zona mascarada como objeto nuevo — ropa/armadura kitbash), **Mask Slice** (corta/rellena).
- **Face Sets ‣ Initialize Face Sets** genera sets por Loose Parts / Materials / UV Seams / Sharp Edges, etc. — la via rapida para trabajar por piezas un mesh importado.
- **Auto-Masking** (`Alt`-`A`, global o por brush): Topology (solo la isla tocada — clave para dientes/placas), Face Sets, Mesh Boundary, Face Sets Boundary, Cavity (+Inverted), View Normal (Occlusion es LENTO), Area Normal. Se combinan entre si.
- Ocultar geometria tambien mejora el rendimiento del viewport (manual).

## Simetria y radial

Panel: Toolbar ‣ Tool ‣ Symmetry (Sculpt Mode).

- **Mirror X/Y/Z**: espeja strokes en ejes locales (X activo por defecto en mallas nuevas — verificar siempre antes del primer stroke). El manual aclara que para alterar la direccion real de esos ejes hay que rotar la malla en **Edit Mode**: rotar el objeto en Object Mode NO cambia a que apuntan los ejes de simetria (siguen el espacio local del mesh, no la orientacion visible en world space) — fuente de confusion si esperas que "rotar el objeto" reoriente la simetria.
- **Radial X/Y/Z**: repite el stroke N veces en 360° alrededor del eje — engranajes, coronas, criaturas radiales. Desde 5.0 es propiedad del mesh (por objeto, no por escena).
- **Feather**: atenua el stroke donde cruza el plano de simetria. **Lock**: bloquea deformacion en un eje. **Tiling**: repite strokes a intervalos (patrones).
- **Symmetrize** (boton en el mismo panel; `bpy.ops.sculpt.symmetrize(merge_tolerance=...)`): copia un lado sobre el otro segun Direction — imprescindible tras Dyntopo, que desincroniza los lados. Un sculpt "simetrico" a ojo NO lo es a nivel de datos: symmetrize antes de retopo/bake si el asset lo requiere.

## Performance de sculpt en 5.x

Numeros oficiales (release notes 4.3 + blog del refactor, hardware de referencia Ryzen 7950X):

- Entrar a Sculpt Mode: 11 s → 1.9 s con malla de **16M de caras** (~5x).
- Evaluacion de brush: 2.9 s → 0.36 s esculpiendo la mayoria de una malla de **6M de caras** (~8x). Memoria −30%, memoria GPU ~2x menos. 4.5 mejoro ademas multires y base mesh en mallas de alto vertex count.
- 5.0: undo de deformaciones comprimido (≥2x menos memoria).

Guia practica derivada (recomendacion, no cifra oficial): en una maquina normal actual, esculpir base mesh de 1–5M de vertices va fluido en 4.3+; el blockout vive comodo en 50–500k. Si necesitas mas de ~10M para detalle, usa Multires y trabaja mostrando un nivel bajo en viewport — no subas la malla base a esa densidad.

Que degrada el rendimiento (manual):

- Multires con **>5 niveles** de subdivision: peor performance y cambio de nivel lento; bajar Quality (Advanced) ayuda en high-poly.
- Dyntopo es el camino mas lento de los tres.
- Auto-masking View Normal con **Occlusion** activado es mucho mas lento; Cavity con Blur >6 tambien cuesta.
- Mascara residual sin uso: Properties ‣ Object Data ‣ Geometry Data ‣ **Clear Sculpt-Mask Data** la libera.
- Ocultar lo que no editas (`H`/`Shift`-`H`) acelera el viewport.

## De sculpt a game asset

Detalle completo del pipeline high→low y bake en [ver: modelado/high-to-low]; el viaje del asset terminado a Unity en [ver: pipeline/arte-a-unity]. Aqui lo especifico de Blender:

| Camino | Cuando | Como en Blender |
|---|---|---|
| **Retopo manual** | Personajes y todo lo que deforma | Sculpt final (symmetrize primero) → nueva malla con Snapping a superficie → Multires + Shrinkwrap para reproyectar detalle → bake |
| **Decimate para low de props** | Rocas, escombros, estatuas — estatico | Modificador **Decimate** modo Collapse: Ratio por triangulos, opcion Symmetry y Triangulate. Topologia fea pero valida sin deformacion |
| **Decimate del high para bake** | El sculpt de 10M ahoga el baker externo | Decimate Collapse 0.1–0.3 sobre el high: el normal bake apenas cambia y el archivo baja 10x |
| **Multires como par high/low** | Detalle anadido sobre malla ya limpia | El nivel base (o bajo) = low; bake de normal/displacement desde los niveles altos |

- El output del Voxel Remesher **nunca** es topologia de juego: densa, sin UVs, sin edge flow. Es una malla de trabajo.
- **Trim Box/Lasso/Line/Polyline** (con solver Manifold 4.5+: rapido pero exige malla manifold) y **Mask Extract** son para kitbash del high, no para el low.
- Dyntopo destruye UVs y face sets: cualquier malla con UVs que quieras conservar NO pasa por Dyntopo.
- Antes de exportar o bake-ar: aplicar escala, revisar manifold, y [ver: import-export] para FBX/glTF.

## Patrones bpy

Activar un brush (4.3+; `paint.brush_set` ya no existe — ejemplo literal de las release notes):

```python
bpy.ops.brush.asset_activate(
    asset_library_type='ESSENTIALS',
    asset_library_identifier="",
    relative_asset_identifier="brushes/essentials_brushes-mesh_sculpt.blend/Brush/Blob",
)
# Mismo patron para los demas: cambia el nombre final ("Brush/<Nombre>")
```

Remesh + decimate headless (prop estatico, sin UI):

```python
import bpy
obj = bpy.data.objects["Rock_sculpt"]
bpy.context.view_layer.objects.active = obj
obj.data.remesh_voxel_size = 0.02          # unidades de objeto; menor = mas denso
obj.data.remesh_voxel_adaptivity = 0.0     # >0 triangula y desactiva Fix Poles
bpy.ops.object.voxel_remesh()              # pierde data layers del mesh
mod = obj.modifiers.new("LowPoly", 'DECIMATE')
mod.ratio = 0.05
bpy.ops.object.modifier_apply(modifier=mod.name)
```

Otros operadores clave (firmas verificadas en la API 5.2): `bpy.ops.object.multires_subdivide(modifier="Multires", mode='CATMULL_CLARK')`, `bpy.ops.sculpt.symmetrize(merge_tolerance=0.0005)`, `bpy.ops.paint.mask_flood_fill(mode='VALUE', value=0.0)` (limpiar mascara), `bpy.ops.sculpt.face_sets_init(mode='LOOSE_PARTS')`, `bpy.ops.sculpt.trim_box_gesture(..., trim_solver='MANIFOLD')`, `bpy.ops.sculpt.sculptmode_toggle()`. Los strokes de brush por script (`bpy.ops.sculpt.brush_stroke`) exigen contexto de viewport: en headless preferir modificadores/geometry nodes [ver: bpy-scripting].

## Reglas practicas

1. Antes de esculpir, decide el destino: ¿retopo, decimate o solo referencia? Eso fija cuanto detalle vale la pena.
2. Blockout con primitivas como objetos separados; fusiona con Join + Voxel Remesh cuando la silueta este aprobada.
3. Silueta primero: matcap plano y juzgar el contorno; no subir densidad hasta cerrar cada fase.
4. Voxel Remesh (`R` + `Ctrl`-`R`) temprano y a menudo en blockout; malla cerrada antes de remesh (Mask Slice + Fill Holes si hay huecos).
5. Dyntopo solo en mallas sin UVs/face sets/colores que conservar.
6. Multires: base mesh de quads limpio, y NUNCA editar la topologia base despues de subdividir.
7. Maximo ~5 niveles de Multires; viewport en nivel bajo, detalle en nivel alto.
8. Clay Strips para construir, Grab/Snake Hook para mover, Plane para planos, Draw Sharp/Crease para cortes: no intentes hacerlo todo con Draw.
9. `Shift` = Smooth y `Ctrl` = invertir son la mitad del esculpido; usalos en vez de cambiar de brush.
10. Verifica la simetria (Mirror X) ANTES del primer stroke; tras Dyntopo, Symmetrize.
11. Aisla por partes: Face Sets + `H`/`Shift`-`H`, o auto-masking Topology para piezas sueltas (dientes, placas).
12. Mascara para proteger, no para seleccionar: Clear + Invert (`A`) es el patron para "editar solo esto".
13. Detalle terciario solo si sobrevive al bake: si el normal map no lo va a capturar a la resolucion de textura objetivo, no lo esculpas.
14. Symmetrize + escala aplicada + chequeo manifold antes de retopo/decimate/bake.
15. Decimate para props estaticos; retopo manual para todo lo que deforma.
16. Guarda el .blend del sculpt high por separado del asset final — el high es tu fuente de bakes futura.
17. En scripts: recuerda que size = diametro (5.0+) y que los brushes se activan por asset, no por nombre de tool.
18. Un stroke feo se corrige con `Ctrl`-`Z`, no con Smooth encima: alisar sobre error acumula mush.

## Errores comunes

| Pitfall | Antidoto |
|---|---|
| Detallar sobre proporciones sin aprobar | Congelar fases: silueta → planos → detalle. El detalle fino no arregla masas malas |
| Voxel Remesh se come orejas/dedos finos | El voxel size debe ser menor que la pieza mas fina; o sube resolucion solo para el remesh final de fusion |
| Voxel Remesh "no hace nada" o da resultado roto | Malla con huecos o no cerrada: rellenar antes (Mask Slice + Fill Holes); recuerda que ignora modificadores y shape keys |
| Perder UVs/vertex colors al activar Dyntopo | Dyntopo corrompe/pierde esos atributos SIEMPRE; usa Voxel Remesh (reproyecta mask/face sets/colores) o Multires |
| Editar la malla base con Multires ya subdividido | Los niveles se corrompen. Cambios amplios: opcion Sculpt Base Mesh, o Apply/Conform Base con intencion |
| Multires sobre triangulos y poles sucios | Artefactos de subdivision: base de quads limpia (el manual lo exige explicitamente) |
| Esculpir sin mirar la simetria y descubrir tarde que estaba apagada (o en el eje equivocado) | Chequear panel Symmetry al entrar; los ejes son locales al mesh y NO cambian si rotas el objeto en Object Mode (el manual lo advierte explicito) — si necesitas otra direccion, rota la malla en Edit Mode |
| "Flatten/Fill/Scrape no existen" siguiendo tutorial viejo | Desde 4.4 son el brush **Plane** (Height/Depth/Inversion Mode) |
| Buscar los brushes en el toolbar (tutoriales ≤4.2) | Desde 4.3: Asset Shelf abajo o `Shift`-`Spacebar` |
| Script viejo con `paint.brush_set` o size como radio | Eliminado en 4.3 → `brush.asset_activate`; size = diametro desde 5.0 |
| Smooth compulsivo que derrite los planos | Blur (5.1+) para suavizar sin encoger; Plane con Stabilize para alisar conservando el plano |
| Sculpt de 15M como "asset" | El sculpt nunca es el asset: retopo o decimate + bake [ver: modelado/high-to-low] |
| Lag creciente sin razon aparente | Mascara residual (Clear Sculpt-Mask Data), overlays, auto-masking Occlusion activado, >5 niveles multires |
| Trim tools lentos o fallando | Solver Manifold (4.5+) suele ser el mas rapido pero solo funciona con malla manifold; si la malla no lo es, cambiar manualmente el dropdown Solver a Exact (mas lento, soporta overlaps) o Float (no hay fallback automatico) |

## Fuentes

- **Blender 5.2 LTS Manual — Sculpting & Painting** (docs.blender.org/manual/en/latest): paginas Adaptive Resolution, Dyntopo, Remesh, Sculpt Brush Types (+ paginas individuales de Draw Sharp, Crease, Clay Strips, Grab, Snake Hook, Plane), Mask, Face Sets, Expand, Visibility/Masking/Face Sets, Auto-Masking, Symmetry, Brush Settings — Blender Foundation — fuente primaria de todos los nombres de operadores, atajos y comportamientos 5.2.
- **Blender 5.2 LTS Manual — Multiresolution Modifier / Decimate Modifier** — Blender Foundation — opciones exactas de los dos modificadores del pipeline sculpt→juego.
- **Release Notes oficiales 4.3, 4.4, 4.5, 5.0, 5.1, 5.2 — seccion Sculpt, Paint, Texture** (developer.blender.org/docs/release_notes) — Blender Foundation — cronologia verificada de brush assets, brush Plane, solver Manifold, size=diametro, Blur, Scene Project y numeros de performance.
- **"This Summer's Sculpt Mode Refactor"** (code.blender.org, nov 2024) — Hans Goudey, Blender Developers Blog — detalle tecnico y benchmarks del rewrite de 4.3 (16M/6M caras, Ryzen 7950X).
- **Blender Python API 5.2** (docs.blender.org/api/current): bpy.ops.sculpt, bpy.ops.object, bpy.ops.paint, bpy.types.Mesh — Blender Foundation — firmas exactas de operadores y propiedades remesh_* usadas en los snippets.
- **Stylized Character Workflow** (studio.blender.org/training) — Julien Kaspar, Blender Studio — flujo de produccion real sculpt→retopo: blockout con primitivas, objetos separados por resolucion, fases de esculpido y retopologia (curso grabado en 2.8: los conceptos valen, la UI no).
