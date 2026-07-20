# Receta: personaje game-ready en Blender

> **Cuando cargar este archivo:** cuando vas a EJECUTAR un personaje/criatura de juego en Blender 5.2 (por MCP o headless) de principio a fin — elegir ruta, blockear, esculpir o modelar directo, retopologizar con loops de deformación, y dejar la malla lista para rigging y export a Unity 6. Es el PUENTE: la teoría de personaje vive en [ver: modelado/organico-personajes] y la de la herramienta en [ver: blender/sculpt], [ver: blender/edicion-malla] y [ver: blender/modificadores]. Aquí SOLO va la secuencia concreta de operadores.

Antes de tocar geometría: [ver: flujo-modelado-blender] (setup de escena/unidades/MCP) y [ver: blockout-desde-referencia] (montar el paquete de referencias). Esta receta asume esas dos hechas.

## 0. Decisión de ruta (fija coste y pipeline entero)

La ruta la dicta la escala de estilización del style guide [ver: gamedev/arte-direccion], no el gusto. Detalle del criterio: [ver: modelado/organico-personajes §1].

| | **RUTA A — sculpt → retopo** | **RUTA B — poly-modeling directo** |
|---|---|---|
| Cuándo | Realista o estilizado con detalle de superficie que se hornea a normal map (arrugas, folds, anatomía) | Low-poly/flat, indie, escala de estilización ≲4; el detalle horneado no se vería |
| Flujo Blender | Blockout (Skin/base mesh) → Sculpt (Voxel Remesh + Multires) → retopo (Poly Build/RetopoFlow + Shrinkwrap) → UV → bake | Box-modeling con Mirror directo a la malla final → UV triviales → color por material/vertex |
| Salida | Low-poly + set de mapas bakeados [ver: modelado/high-to-low] | Una sola malla, sin high-poly, sin bake |
| Sección | §2 | §3 |

Regla dura: **el sculpt NUNCA es el asset de juego** (siempre acaba en retopo+bake). Y si el estilo es flat, esculpir es coste puro — ir directo a §3.

## 1. Setup mínimo de la sesión

- Escena en **métrico, 1 unidad = 1 m** (Unity: 1 u = 1 m; probar contra un cubo de 1 m — Unity Manual). Personaje humano ≈ 1.7–1.9 m de alto real.
- Blueprints front/side montados como Image Empties, en su propia colección `refs`, bloqueados de selección [ver: modelado/blueprints-referencias].
- Origen del personaje en `(0,0,0)`, sobre el plano de suelo, **entre los pies** (Unity Manual: los pies al anchor/origin local). Mirando hacia el eje forward del proyecto — la conversión exacta de ejes y el bug de rotación −89.98 al exportar viven en [ver: blender/import-export].
- Estructura de colecciones y naming: [ver: blender/organizacion-blend].

---

## 2. RUTA A — sculpt → retopo → game-ready

### A1. Blockout: base mesh con el Skin modifier

El Skin modifier convierte un esqueleto de vértices/aristas en un volumen — la vía más rápida a un base mesh proporcionado para esculpir. (Estable 2.8→5.2; controles verificados contra la API; confirmar los menús en Blender vivo.)

1. `Add ▸ Mesh ▸ Plane`, Edit Mode, `M ▸ At Center` → un vértice único. (O `Add Mesh: Extra Objects` → Single Vert.)
2. Traza el esqueleto con `E` (Extrude): pelvis→columna→cuello→cabeza en el eje central (X=0); una pierna y un brazo hacia +X. Sigue las proporciones del blueprint (cabezas de altura, mitad del cuerpo en la entrepierna [ver: modelado/organico-personajes §3]).
3. Stack de modificadores en ORDEN: **Mirror** (Axis X, Clipping ON, Merge ON) → **Skin** → **Subdivision Surface** (viewport 1–2). El Mirror arriba te deja construir medio esqueleto [ver: blender/modificadores §2].
4. Dar grosor: en Edit Mode, seleccionar vértices y **`Ctrl`-`A` = Skin Resize** (arrastrar; `X`/`Y`/`Z` restringe eje). Afinar muñecas/tobillos/cuello con radios menores.
5. **Mark Root** en la pelvis (`bpy.ops.mesh.skin_root_mark`) — define desde dónde se calcula el volumen. `bpy.ops.mesh.skin_radii_equalize` iguala radios de una selección; `skin_loose_mark_clear` hace ramas "sueltas" (interpolan más suave).
6. Cuando la silueta lee en negro [ver: gamedev/arte-direccion §5]: aplicar el stack → base mesh. `Ctrl`-`A` sobre cada modificador de arriba a abajo, o `Object ▸ Convert ▸ Mesh`.

```python
import bpy
obj = bpy.context.object                       # el esqueleto de vértices ya trazado
mir = obj.modifiers.new("Mirror", 'MIRROR');  mir.use_clip = True
skin = obj.modifiers.new("Skin", 'SKIN')
sub = obj.modifiers.new("Subsurf", 'SUBSURF'); sub.levels = 2
# Skin Resize se hace en Edit Mode con transform.skin_resize (necesita contexto de viewport)
# Congelar: bpy.ops.object.convert(target='MESH')  -> aplica todo el stack en orden
```

Alternativa sin Skin: bloquear con primitivas separadas (cabeza, torso, extremidades) y fusionar con Join + Voxel Remesh [ver: blender/sculpt] — mejor cuando la forma es orgánica no-humanoide.

### A2. Esculpir: silueta → planos → detalle

No repetir aquí el detalle de Sculpt Mode — la ejecución completa (brushes, Dyntopo vs Multires vs Voxel, atajos) está en [ver: blender/sculpt]. La secuencia mínima para personaje:

| Fase | Densidad en Blender | Qué congelar antes de subir |
|---|---|---|
| Primaria (silueta/masas) | Voxel Remesh 10–50k (`R` size, `Ctrl`-`R` ejecuta); Grab/Snake Hook/Clay Strips | Proporciones y landmarks óseos [ver: modelado/organico-personajes §3] |
| Secundaria (planos/músculos) | Voxel Remesh más fino o primeros niveles de Multires; Clay Strips/Plane/Crease | Los planos anatómicos; sin ruido |
| Terciaria (arrugas/poros/folds) | **Multires niveles 3–5** (`Ctrl`-`1..5`); Draw Sharp/Crease/Layer | SOLO lo que el bake capture a la resolución objetivo |

- Simetría del sculpt: Mirror X activo; tras Dyntopo, **Symmetrize** (`bpy.ops.sculpt.symmetrize`) porque los lados se desincronizan a nivel de datos.
- La cabeza, manos y pies se esculpen aparte o con atajos honestos (ojos = esfera separada, zapatos en vez de pies, dedos fusionados) [ver: modelado/organico-personajes §6].
- El detalle terciario para juego vive en Multires SOBRE el retopo (A4) o sobre el sculpt a bake-ar — nunca inviertas horas de detalle en la malla del Voxel Remesh (es de trabajo).

### A3. Retopología sobre el sculpt

El sculpt aprobado se congela (cambiarlo después = repetir retopo+UV+bake). Dos caminos:

**A3a. Nativo (Poly Build + Shrinkwrap):**

1. `Add ▸ Mesh ▸ Plane`, borrar sus caras, renombrar `Char_LP`. Añadir **Shrinkwrap** (Target = el sculpt, Wrap Method `Project` o `Nearest Surface`, Snap Mode **Above Surface**, Offset ~0.002 m) — mantiene la retopo pegada sin z-fighting, no-destructivo [ver: blender/modificadores §3].
2. Activar el overlay **Retopology** (ver la malla nueva a través del sculpt sin X-Ray) y **Auto Merge** (Sidebar ▸ Tool ▸ Options).
3. Snapping ON (`Shift`-`Tab`): Snap To **Face**, con **Face Nearest** para pegar también donde hay oclusión, y **Backface Culling** en las opciones de snap.
4. **Poly Build** (Toolbar): `Ctrl`-`LMB` añade vértice/quad, `Shift`-`LMB` borra, arrastrar un edge lo extruye. Trazar PRIMERO las líneas maestras (contorno de ojo, boca, línea de mandíbula, hombro, costuras) y rellenar después [ver: modelado/topologia §3].
5. Cerrar la retopo → **aplicar Shrinkwrap** (recién ahora) → limpieza de malla [ver: blender/edicion-malla §6].

**A3b. RetopoFlow (addon):** v3.4.10 (ene-2026), GPL-3.0, Orange Turbine; su tabla oficial dice "Blender 3.6+", compatibilidad exacta con 5.2 NO VERIFICADA — probar en un .blend desechable antes de confiarle trabajo. Herramientas sketch-based sobre el high-poly: **Contours** (anillos para extremidades cilíndricas), **PolyStrips** (tiras que siguen el flow), **PolyPen** (vértice a vértice para detalle), **Strokes**, **Patches**. Para low/mid-poly de juego, A3a suele bastar sin addon.

**Auto-retopo (Quad Remesh/Voxel):** NO para lo que deforma — no sabe dónde está el codo [ver: modelado/topologia §8]. Sirve solo para mallas intermedias o props de fondo.

### A4. Loops de deformación EN LA PRÁCTICA

Es el corazón de la retopo de personaje. Dónde poner geometría en Blender (los principios en [ver: modelado/topologia §5] y [ver: modelado/organico-personajes §5]; aquí el how-to):

| Zona | Qué construir | Cómo en Blender |
|---|---|---|
| **Cara (si hay expresión)** | Anillos concéntricos alrededor de OJO y BOCA + loop nasolabial (ala nariz→comisura) | Trazar los dos "agujeros" primero con Poly Build; ojo = esfera separada, párpados envolviéndola |
| **Cara (sin expresión)** | Cero loops faciales: malla mínima que sostenga silueta y bake | No pagar geometría que no anima |
| **Hombro** | Loops que siguen el deltoides o anillos "bendy-straw"; el de mayor rango | `Ctrl`-`R` loop cuts extendidos hacia pecho/brazo; validar con brazo arriba |
| **Codo / rodilla** | VARIOS loops paralelos en el pliegue (uno solo = manguera afilada) | 3+ loops (`Ctrl`-`R`, `Wheel` sube cuenta), extendidos más allá del pliegue a la superficie plana vecina (topologyguides) |
| **Muñeca / tobillo** | Loops perpendiculares al hueso, densidad moderada (torsión) | Anillos limpios; sin poles aquí |
| **Cadera / entrepierna** | Loops que rodean la pierna donde nace del torso + loops del glúteo | Deforma en 3 ejes; probar SENTADO antes de aprobar |
| **Mano** | Loops en cada nudillo si hay dedos individuales; modelar semiflexionada | Elegir peldaño honesto (5 dedos→4→fusionados→mitten) según cámara |

Reglas transversales al retopologizar: **quads** en zonas de flexión; **poles** (valencia≠4) SOLO en zonas planas, JAMÁS en articulación ni comisura; densidad donde hay curvatura o deformación, nada de edges que no aporten a silueta/deformación/UV. Validar SIEMPRE posando al máximo del juego, no en T-pose (el fix va en la malla, no en el rig).

### A5. UV, triangulación y bake

Comprimido — el detalle vive en [ver: modelado/high-to-low] y [ver: pipeline/arte-a-unity]:

1. Seams escondidos (interior de brazos/piernas, bajo el pelo, tras las orejas); cada hard edge lleva su UV seam.
2. **Triangular ANTES de bakear** (modificador Triangulate al final con Pin to Last) y usar esa misma triangulación en el engine — si no, el shading zigzaguea.
3. Bake normal/AO/curvature/ID del sculpt (o Multires) al low, tangent space **MikkTSpace** (el de Unity), 16-bit→8-bit con dither, edge padding por resolución.
4. Aprobar el bake EN Unity con la luz del juego, no en el visor.

---

## 3. RUTA B — poly-modeling low-poly directo (indie estilizado)

Sin sculpt, sin bake: la silueta y el color hacen el look [ver: modelado/estilizacion-lowpoly]. La receta específica de estilo está en [ver: receta-lowpoly-estilizado]; aquí lo específico de personaje.

1. **Mirror desde el vértice 1**: empezar con medio cuerpo. `Add ▸ Mesh ▸ Cube` (o cilindro por extremidad), añadir **Mirror** (Axis X, Clipping ON, Merge ON) ANTES del primer extrude — construyes la mitad, ves el todo.
2. **Box-modeling / extrusión**: `E` para sacar torso→cuello→cabeza y las extremidades; `Ctrl`-`R` para meter los pocos loops que la silueta y la deformación exigen; `I`+`E` para detalles hundidos. Proporciones estilizadas decididas ANTES (chibi 2–3 cabezas, cartoon 4–6) [ver: modelado/organico-personajes §4].
3. **Topología deformable desde el inicio**: aunque sean 800–2000 tris, las zonas del A4 (hombro, codo, rodilla, cadera) necesitan sus loops igual. Un low-poly que no deforma es un low-poly fallido.
4. **La silueta ES el asset**: evaluar en negro y desde la cámara real del juego; cada vértice se gasta en contorno/landmarks, cero en superficie interior.
5. Shading decidido por style guide: **flat** (facetado como estética: `Face ▸ Shade Flat`) o **smooth + Mark Sharp** puntual (`Shade Auto Smooth` 30–45° + Mark Sharp donde la silueta lo pida). Tris permitidos desde el minuto uno.
6. Color: por material/vertex color/paleta-atlas, UVs triviales (islas al color de la paleta) — sin normal map [ver: modelado/high-to-low §7].

Esta ruta produce un personaje jugable en horas; el coste real se muda a paleta, luz y animación.

---

## 4. Simetría: Mirror durante el modelado y cuándo aplicarla

| Momento | Estado del Mirror |
|---|---|
| Blockout, sculpt, retopo, box-modeling | **Mirror activo** (Axis X, Clipping ON, Merge ON) todo el proceso; construyes una mitad |
| Sculpt con Dyntopo | Mirror del sculpt + **Symmetrize** al final (los lados se desincronizan) |
| Asimetrías del diseño (accesorios, cicatriz, bolsillo en un lado, pose) | **APLICAR el Mirror** (`Ctrl`-`A`) y AHÍ agregar la asimetría, como último paso sobre la malla ya aprobada |
| Antes de UV/bake/export | Mirror aplicado; UVs espejados con **Data ▸ UV Offset +1.0 en U** para que el overlap no ensucie el bake [ver: blender/modificadores §3] |

Nunca dejes el Mirror sin aplicar si vas a UV-unwrappear con islas únicas por lado o a poner detalle asimétrico. Regla: **espejar lo más tiempo posible, romper la simetría lo más tarde posible.**

---

## 5. Ropa y accesorios: capas y borrar lo oculto

- **Ropa SOBRE el cuerpo terminado**: construir cada prenda como malla nueva sobre el cuerpo mid-res, conformarla con **Shrinkwrap** (o el brush **Scene Project** 5.2 en sculpt), y esculpir/modelar folds encima [ver: modelado/organico-personajes §7].
- **Borrar el cuerpo bajo ropa opaca** en el low-poly final — es coste de skinning/render Y la causa #1 de clipping (dos superficies deformando pegadas se atraviesan). Procedimiento en Blender:
  1. Aislar el cuerpo (`/` numpad o `Shift`-`H`).
  2. Con **X-Ray ON** (`Alt`-`Z`), box-select (`B`) las caras cubiertas por la prenda cerrada.
  3. `X ▸ Faces` para borrarlas; sellar el borde con margen de solape OCULTO bajo el borde de la tela (`E`/Bridge).
  4. Conservar solo la piel que asoma (cuello, manos, tobillos).
- **Guardar el cuerpo completo** en una colección oculta del .blend fuente — los rediseños de vestuario lo necesitan [ver: blender/organizacion-blend].
- **Capas**: la capa inferior solo existe donde se ve (abrigo sobre camisa = modelar el abrigo + los trozos visibles de la camisa).
- **Accesorios rígidos** (hebillas, armadura, correas): hard-surface adosado [ver: receta-prop]; se skinnean 100% a UN hueso para que no se doblen como goma (fase de rigging).
- **Materiales**: personaje entero en 1–2 materiales, idealmente una sola malla skinneada — Unity documenta que 2 skinned meshes ≈ 2× el render del personaje. Fusionar mallas y atlasear.

---

## 6. Handoff a rigging: dejar la malla lista

La fase de rigging aún no está cubierta en esta base; esto es lo que la malla DEBE cumplir antes de entregarla (requisitos de Unity Manual — Modeling/Humanoid + práctica):

- [ ] **Bind pose acordada**: T-pose (brazos rectos formando "T" — lo que pide Unity Humanoid) o A-pose (~45°, reparte el error de deformación del hombro). Decidirla ANTES de retopo, no después.
- [ ] **Escala y rotación aplicadas** (`Ctrl`-`A ▸ Rotation & Scale` en Object Mode) — sin esto, bevels/merge/thickness salen mal y el rig hereda escala sucia.
- [ ] **Origen entre los pies, en el suelo** `(0,0,0)`; personaje mirando al forward del proyecto.
- [ ] **Malla limpia**: sin doubles, sin non-manifold en lo que debe ser cerrado, normales hacia fuera (`Shift`-`N`), sin caras interiores, sin n-gons (checklist completo [ver: blender/edicion-malla §6]).
- [ ] **Naming consistente**: objetos `Char_Body`, `Char_Hair`, `Char_Eyes`, `Char_Clothing`; materiales con nombre; una malla skinneada o el mínimo de piezas.
- [ ] **Manos semiflexionadas**, no en tabla (reduce el trabajo del rig en toda pose).
- [ ] **Max 4 influencias de hueso por vértice** (default de Unity) — se respeta al pesar, pero la topología debe permitirlo.

```python
import bpy, math
# Prep de export/rigging: aplicar transforms, recalcular normales, verificar
for o in bpy.context.selected_objects:
    if o.type != 'MESH': continue
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)   # Recalculate Outside
    bpy.ops.object.mode_set(mode='OBJECT')
    tris = sum(len(p.vertices) - 2 for p in o.data.polygons)  # conteo aprox de tris
    print(o.name, "tris≈", tris, "loc", tuple(round(v,3) for v in o.location))
```

Export FBX a Unity 6 (escala 100×, ejes, Apply Transform, qué sobrevive de blend shapes/armature): [ver: blender/import-export] y [ver: pipeline/arte-a-unity]. Un personaje con blend shapes exige verificar el export real — el manual del exportador FBX (sección Legacy) es contradictorio sobre shape keys [ver: blender/modificadores §5].

---

## 7. Presupuesto y checklist game-ready

Los números FINALES salen de [ver: modelado/presupuestos-poligonos] y la spec del proyecto — nunca de la costumbre. Órdenes de magnitud como ancla (contar TRIángulos y VÉRTICES del engine, no quads del DCC):

| Rol | Tris (orden de magnitud) | Notas |
|---|---|---|
| Protagonista 3ra persona (cámara cercana) | decenas de miles — ancla publicada: **~50k tris** estilizado UE4 (+ pelo aparte) | Loops de deformación completos, cara con expresión |
| NPC secundario | pocos miles–~8k | Menos loops faciales, manos simplificadas |
| NPC de fondo / multitud | ~500–2k + LODs / impostor | Silueta manda; sin deformación fina |
| Móvil / VR | fracción de lo anterior | El budget de plataforma manda [ver: modelado/presupuestos-poligonos] |

**Checklist game-ready (gate de aprobación):**

- [ ] Ruta correcta para la escala de estilización (no esculpir un flat).
- [ ] Silueta lee en negro a la cámara real del juego.
- [ ] Loops de deformación validados POSANDO (brazo arriba, sentadilla, giro de cabeza, sonrisa extrema) — no solo en T-pose.
- [ ] Quads en zonas de flexión; poles fuera de articulaciones y cara; tris justificados en el resto.
- [ ] Cuerpo bajo ropa opaca borrado; cuerpo completo guardado en el fuente.
- [ ] 1–2 materiales, malla skinneada única (o mínimo de piezas); texturas atlaseadas.
- [ ] Triangulado antes del bake; misma triangulación en engine; tangent space MikkTSpace.
- [ ] Escala/rotación aplicadas, origen entre los pies, pose de bind acordada.
- [ ] Tri/vertex count dentro del budget del rol (medido en engine).
- [ ] LODs planificados si el rol lo pide (`_LOD0..n`) [ver: pipeline/arte-a-unity].

## Reglas prácticas

1. Elige la RUTA por la escala de estilización antes de abrir Blender; bajo ~4, no esculpas — ve directo a §3.
2. Escena en métrico (1u=1m), personaje ~1.7–1.9 m, origen entre los pies en `(0,0,0)`.
3. Blockout con Skin modifier (Mirror→Skin→Subsurf) o primitivas separadas; congela proporciones ANTES de esculpir.
4. Skin Resize = `Ctrl`-`A`; Mark Root en la pelvis; aplica el stack solo cuando la silueta lea en negro.
5. Sculpt por fases: Voxel Remesh (silueta) → Multires niveles 3–5 (detalle); Symmetrize tras Dyntopo. No detalles sobre proporciones sin aprobar.
6. Congela el sculpt antes de retopo (cambiarlo = repetir retopo+UV+bake).
7. Retopo: overlay Retopology + Shrinkwrap (Above Surface, offset chico) + snap Face Nearest + Auto Merge + Poly Build; líneas maestras primero, relleno después.
8. Loops de deformación: anillos en ojo/boca+nasolabial (si hay expresión), 3+ loops paralelos en codo/rodilla extendidos a la zona plana, loops que rodean la cadera; poles solo en zonas planas.
9. Valida deformación POSANDO al máximo del juego; el fix va en la malla, no en el rig.
10. Mirror activo todo el proceso; aplícalo solo para meter asimetrías o UVs/detalle por lado; UV offset +1 en U para el lado espejado.
11. Ropa sobre el cuerpo terminado; borra el cuerpo bajo tela opaca (X-Ray + box-select + `X ▸ Faces`) con margen de solape oculto; guarda el cuerpo completo en el fuente.
12. Piezas rígidas (hebillas, armadura) a un hueso; personaje en 1–2 materiales, una malla skinneada.
13. Triangula antes de bakear (Triangulate + Pin to Last); tangent space MikkTSpace; aprueba el bake en Unity, no en el visor.
14. Manos semiflexionadas; ojos como esfera separada; zapatos en vez de pies salvo que el diseño lo exija.
15. Antes de entregar a rigging: escala/rotación aplicadas, normales recalculadas, malla limpia (checklist [ver: blender/edicion-malla §6]), naming, max 4 influencias por vértice, pose de bind acordada.
16. Los números de budget salen de [ver: modelado/presupuestos-poligonos] y la spec; cuenta tris/vértices en el engine, no quads del DCC.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Esculpir un personaje low-poly flat "para que quede mejor" | Si el estilo no hornea detalle, el sculpt es coste puro: ruta directa §3 |
| Base mesh del Skin con radios sin afinar (muñeca tan gruesa como el brazo) | `Ctrl`-`A` (Skin Resize) por zona; Equalize Radii en anillos; Mark Root en pelvis |
| Empezar la retopo con el sculpt aún cambiando | Congelar la forma primero — la retopo es un compromiso de 16–80 h en producción |
| Confiar el codo/hombro al auto-retopo | Auto-retopo solo para intermedios/props; articulaciones y cara siempre a mano |
| Un solo loop en codo/rodilla → se afila como manguera | 3+ loops paralelos extendidos más allá del pliegue; validar doblando al máximo |
| Cara con loops en espiral que "se ve bien" quieta | Anillos concéntricos en ojo/boca + nasolabial; se aprueba con la sonrisa extrema |
| Retopo aprobada en T-pose que explota al animar | Gate de poses extremas (brazo arriba, sentadilla, giro de cabeza) antes de aprobar |
| Aplicar el Shrinkwrap antes de cerrar la retopo | Shrinkwrap SIEMPRE último y aplicado al final; hasta entonces es no-destructivo |
| Dejar el cuerpo completo bajo la ropa en el modelo de juego | Se borra lo cubierto (clipping + coste); el "por si acaso" vive en el .blend fuente |
| Ropa que atraviesa el cuerpo al animar | Capa inferior solo donde se ve + margen de solape oculto; probar animaciones extremas |
| Escala sin aplicar antes de rigging/export | `Ctrl`-`A ▸ Rotation & Scale`; sin esto el rig y el engine heredan escala sucia |
| Origen del personaje en el pecho o fuera de los pies | Origen entre los pies en `(0,0,0)`, sobre el suelo (Unity espera el anchor ahí) |
| Personaje en 6 mallas y 8 materiales "para organizar" | 1 malla skinneada, 1–2 materiales (Unity: 2 mallas ≈ 2× render); atlasear |
| Dejar el Mirror sin aplicar y unwrappear con islas por lado | Aplicar Mirror antes de UV asimétrico; UV offset +1 en U para el espejo |
| Contar quads del DCC y creerse dentro de budget | Contar TRIángulos y vértices en el engine; los quads reportados mienten |
| Bind pose decidida DESPUÉS de retopologizar | Acordar T vs A-pose con el rig ANTES de la retopo |

## Fuentes

- **Bases sintetizadas (no repetidas, referenciadas):** [ver: modelado/organico-personajes] (rutas, anatomía para juegos, topología de zonas que deforman, ropa, atajos honestos), [ver: modelado/topologia] (edge flow, poles, loops de deformación, retopo), [ver: modelado/high-to-low] (bake, tangent space, hard edge=UV seam), [ver: blender/sculpt] (Voxel/Dyntopo/Multires, brushes, Symmetrize), [ver: blender/edicion-malla] (Poly Build, snapping, retopo nativa, limpieza, normales), [ver: blender/modificadores] (Mirror, Skin, Shrinkwrap, Subsurf, Triangulate, orden del stack, apply/export).
- **Blender 5.2 LTS Manual** — docs.blender.org (páginas Skin Modifier, Retopology, Shrinkwrap, Poly Build, Sculpting) — Blender Foundation. Fuente primaria de operadores/atajos; las páginas del manual devuelven 403 a fetch automatizado — los operadores citados están verificados vía las bases blender/ y la API `bpy`; confirmar menús puntuales (Mark Root/Loose/Equalize del Skin) en Blender vivo.
- **Topology for Game and Game-Based Characters** — 80.lv (Evgeny Pyrch — Metro Exodus) — verificado por fetch 2026-07: edge flow a lo largo de las líneas de anatomía/diseño de ropa, atención extra a las articulaciones para rig/animación, retopo de 16–80 h por personaje.
- **Topology Guides** — topologyguides.com (Johnson Martin) — verificado por fetch 2026-07: alinear loops al eje de rotación para que las caras no distorsionen en poses extremas, extender loops de articulación a la superficie plana vecina, poles a zonas de mínima deformación, densidad extra en rodillas/tobillos.
- **Modeling optimal / Using Humanoid Characters** — Unity Manual, docs.unity3d.com — verificado por fetch 2026-07: T-pose para import humanoide, 1 unidad = 1 m (probar contra cubo de 1 m), pies en el origen/anchor local, capar agujeros + soldar vértices + quitar caras ocultas, máximo 4 influencias de hueso por vértice.
- **RetopoFlow** — github.com/CGCookie/retopoflow — verificado por fetch 2026-07: v3.4.10 (ene-2026), GPL-3.0, Orange Turbine, suite sketch-based; tabla oficial "Blender 3.6+", compatibilidad con 5.2 NO VERIFICADA (probar en .blend desechable).
