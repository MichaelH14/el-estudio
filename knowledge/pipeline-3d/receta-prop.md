# Receta: prop game-ready en Blender

> **Cuando cargar este archivo:** cuando hay que MODELAR un prop rígido concreto en Blender (caja, barril, cofre, farola, cajón, palanca) de la referencia al FBX en Unity, ejecutando paso a paso con las herramientas reales — a mano o por MCP/headless. El QUÉ y el porqué viven en [ver: modelado/props-armas]; la herramienta suelta en [ver: blender/edicion-malla] y [ver: blender/modificadores]. Aquí está el CÓMO encadenado.

Versión: **Blender 5.2 LTS** → **Unity 6**. Este archivo NO repite teoría de modelado ni el detalle de cada herramienta: los comprime y cruza. El valor es la secuencia ejecutable. Antes de arrancar por MCP, cargar [ver: blender/blender-mcp-operativo].

## 0. Antes de tocar geometría: 3 decisiones

Las tres deciden todo el trabajo; tomarlas mal cuesta el asset entero [ver: modelado/props-armas §1].

**A) Clasificar el prop** (rol + distancia mínima de cámara) → fija presupuesto de tris, texel density y si merece textura propia o trim. Fondo / estándar / hero / interactivo. Números por categoría: [ver: modelado/presupuestos-poligonos].

**B) Elegir el método de superficie** [ver: modelado/hard-surface]:

| Método | Cuándo | Salida | Coste |
|---|---|---|---|
| **Low-poly directo** | Prop de fondo/estándar, estilizado, o que vive de un trim sheet | Una malla, sin high, shading por Shade Auto Smooth + Sharp | El más barato |
| **Mid-poly + bevel + weighted normals** | Prop estándar/hero rígido con filos limpios, SIN normal map propio o con uno ligero | Biseles reales pequeños + normales ponderadas = shading duro-limpio | Medio — el caballo de batalla de props (§3) |
| **High→low con bake** | Hero prop, superficie con daño/relieve que la geometría no puede llevar | High-poly (subdiv/sculpt) → low retopo → bake normal/AO | El más caro [ver: modelado/high-to-low] |

Regla operativa: **la mayoría de props de entorno son mid-poly + WN.** El high→low se reserva para lo que la cámara ve muy de cerca o lleva relieve orgánico. El barril de fondo puede ser low-poly directo.

**C) ¿El prop se mueve o se agarra?** → decide pivotes y despiece (§5, §6). Un cofre es interactivo (tapa móvil); un barril estático se agarra/rueda; una farola solo se planta. Esto se decide AHORA, no al exportar — cambiar pivotes tarde contamina prefabs [ver: modelado/props-armas §8].

## 1. Setup de escena (una vez por .blend)

Prop = un objeto (o familia) por .blend [ver: blender/organizacion-blend]. Escena en metros, escala real desde el primer vértice [ver: blender/import-export].

```python
import bpy
s = bpy.context.scene
s.unit_settings.system = 'METRIC'
s.unit_settings.scale_length = 1.0        # 1 unidad = 1 m
# maniquí de escala: un cubo de 1.8 m como referencia humana viva en la escena
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.5, 0, 0.9))
bpy.context.object.scale = (0.5, 0.25, 1.8)   # persona ~1.8 m para calibrar (borrar antes de exportar)
```

Overlays útiles todo el rato: **Statistics** (tris en vivo) y **Face Orientation** (azul=fuera). Contador en **triángulos**, no en faces [ver: modelado/topologia §2].

## 2. La receta (referencia → FBX)

Pipeline con gate por fase [ver: modelado/props-armas §2]. Ejemplo espina: **cofre de madera** (interactivo, simétrico, con herraje = boolean, tapa móvil). Las ramas por tipo de prop se anotan en cada paso.

### Paso 1 — Referencia y medidas
- Carpeta de refs reales + medidas del objeto físico [ver: modelado/blueprints-referencias]. Montaje del blockout desde blueprints: [ver: blockout-desde-referencia].
- Anotar las **piezas** (base, tapa, bisagras, cerradura, flejes) y **qué se mueve** — eso predetermina el despiece del §5.
- **Gate:** entiendes cómo está construido y cómo funciona, no solo cómo se ve.

### Paso 2 — Blockout a escala (formas primarias)
Primitivas a medidas reales, silueta primero. Herramientas: `Shift+A ▸ Mesh` para primitivas; `Tab` a Edit Mode; `E` extrude, `I` inset, `Ctrl+R` loop cut, `S/G/R` transform [ver: blender/edicion-malla §2].

```python
import bpy
# base del cofre: 0.80 x 0.45 x 0.40 m
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.20))
b = bpy.context.object; b.name = "Chest_Base"
b.dimensions = (0.80, 0.45, 0.40)
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)  # Ctrl+A: escala a 1
```

- **Barril:** `primitive_cylinder_add(vertices=24, radius=0.28, depth=0.85)`. 24 lados es buen punto medio para un prop estándar; fondo puede bajar a 12–16 [ver: modelado/presupuestos-poligonos]. **Arreglar las tapas ngon** (Grid Fill o poke) antes de seguir [ver: blender/edicion-malla].
- **Farola / poste:** cilindro fino vertical + brazo; el boolean de huecos (respiraderos, tornillos) va en el §3.
- **Caja:** cubo escalado; los flejes/refuerzos son extrusiones o piezas aparte.
- **Gate:** silueta y proporciones aprobadas EN engine con la cámara del juego y el maniquí al lado — nunca en el viewport [ver: modelado/props-armas §3]. Exportar el blockout YA es válido [ver: gamedev/arte-direccion].

### Paso 3 — Formas secundarias y terciarias (el stack de modificadores)
Aquí se refina la masa aprobada en piezas funcionales y luego superficie. En mid-poly esto ES el stack de modificadores; el orden es ley [ver: blender/modificadores §2]. Orden canónico para un prop:

```
Mirror  →  Boolean(es)  →  Bevel  →  Weighted Normal  →  Triangulate (Pin to Last)
```

| Modificador | Ajuste concreto para el prop | Por qué en esa posición |
|---|---|---|
| **Mirror** | Solo si es simétrico (cofre: eje X). Origen del objeto EN el eje; **Clipping** ON al editar, **Merge** ON | Arriba: todo lo que sigue actúa sobre la malla completa; sin costura en el eje [ver: blender/modificadores §3] |
| **Boolean** | Huecos/cortes: cerradura embutida, respiraderos de la farola, hueco de bisagra. Solver **Manifold** si TODO es manifold, **Exact** si hay solapes | Tras Mirror, antes del Bevel: el bevel debe ver los cortes ya hechos para biselarlos también |
| **Bevel** | `width≈0.003–0.005 m`, `segments=2`, **Limit Method: Angle** ~30° (o **Weight** con `bevel_weight_edge` si el ángulo no discrimina), **Clamp Overlap** ON | Tarde: rompe TODO filo afilado; una arista perfecta no existe en el mundo real y delata el 3D barato [ver: modelado/props-armas §5] |
| **Weighted Normal** | `mode='FACE_AREA'`, **Keep Sharp** ON. Activar **Face Influence** solo si el Bevel marcó Face Strength | Al final del shading: opera sobre las caras finales, aplana las caras grandes → shading limpio SIN normal map |
| **Triangulate** | Quad Method **Beauty**, con **Pin to Last** | Último: congela la triangulación que verán bake, export y engine [ver: modelado/topologia §2] |

```python
import bpy, math
obj = bpy.data.objects["Chest_Base"]

# (Mirror y Boolean se añaden antes; aquí el par mid-poly + triangulate)
bv = obj.modifiers.new("Bevel", 'BEVEL')
bv.width = 0.004
bv.segments = 2
bv.limit_method = 'ANGLE'
bv.angle_limit = math.radians(30)
bv.harden_normals = True            # bisela limpio; crea custom_normal
bv.use_clamp_overlap = True

wn = obj.modifiers.new("WeightedNormal", 'WEIGHTED_NORMAL')
wn.mode = 'FACE_AREA'
wn.keep_sharp = True

tri = obj.modifiers.new("Triangulate", 'TRIANGULATE')
tri.quad_method = 'BEAUTY'
# Pin to Last se marca en UI; por script, añadir Triangulate de último basta
```

- **Boolean bien hecho:** el cutter debe ser **manifold** y quedar en una colección `CUT_` con visibilidad de viewport off; tras el corte, **limpiar la topología** que deja (loops sueltos, ngons) — un boolean sucio es el error clásico [ver: modelado/hard-surface]. Cerradura del cofre, agujero de tornillo de la farola: cutter cilíndrico/cúbico → Difference.
- **Detalle terciario** (cabezas de tornillo, remaches, texto): en mid-poly va casi todo a normal map o decal, no a geometría [ver: modelado/props-armas §4]. Si no hay bake, se insinúa con biseles y se resuelve en textura (fuera del alcance de esta receta).
- **Squint test:** el prop se lee por su masa; el detalle no tapa la forma. 70/30 en las subdivisiones, no 50/50.
- **Gate:** shading limpio bajo un matcap [ver: blender/materiales-preview]; sin pinch en los biseles.

### Paso 4 — Shading de filos (estado 5.x)
Auto Smooth **ya no es un checkbox** (muerto en 4.1) [ver: blender/edicion-malla §5]. En 5.2:

```python
import bpy
bpy.ops.object.shade_auto_smooth(angle=math.radians(35))   # añade el modificador Smooth by Angle
```

- Umbral 30–45°. Ajustar filos concretos con `Edge ▸ Mark Sharp` / `Clear Sharp`. Sharp marcado = smoothing groups en el FBX: viaja al engine, no es cosmético.
- Si usaste Bevel con Harden Normals + Weighted Normal, el shading duro-limpio ya está resuelto; Smooth by Angle es el respaldo para las piezas sin bevel.

### Paso 5 — Separar las partes móviles (props interactivos)
El prop interactivo se despieza **como se anima**, no soldado [ver: modelado/props-armas §8]. La tapa del cofre es un objeto propio.

En Edit Mode: seleccionar las caras de la tapa → `P` → **Separate ▸ By Selection** (o **By Material** si la tapa tiene su slot). `Mesh ▸ Separate`.

```python
import bpy
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
# ...seleccionar las caras de la tapa (por material, vertex group o box-select)...
bpy.ops.mesh.separate(type='SELECTED')       # o type='MATERIAL'
bpy.ops.object.mode_set(mode='OBJECT')
# Blender nombra la pieza nueva "Chest_Base.001"; renombrar:
bpy.data.objects["Chest_Base.001"].name = "Chest_Lid"
```

| Parte móvil típica | Se separa | Su pivote va en |
|---|---|---|
| Tapa de cofre/caja | Sí | La **bisagra trasera** (§6) |
| Puerta (hoja) | Sí, marco aparte | El **eje de la bisagra** |
| Cajón | Sí | Donde corre (recorrido lineal) |
| Palanca / brazo | Sí, base estática aparte | Su **perno de giro** |
| Válvula / rueda | Sí | El **centro del eje** |

- **Modelar el interior que el movimiento revela:** al abrir el cofre se ve el fondo interno → modelarlo y darle su material. Un cofre hueco por dentro se rompe como ilusión.
- **Estado por defecto = cerrado/en reposo**, partes en cero. El estado abierto lo produce la animación en Unity, no otro mesh.
- **Probar el recorrido** en Blender antes de entregar: rotar la tapa por su arco completo y confirmar que no hace clipping con la base.

### Paso 6 — Pivote y origen correctos (esto es Unity)
El **origen del objeto en Blender = pivot en Unity** (allí ya no se edita) [ver: blender/import-export]. La regla la fija el USO del prop:

| Uso del prop | Origen va en | Por qué |
|---|---|---|
| Apoya en el suelo (barril, caja, cofre, farola) | **Base, centro, contacto con el suelo** (z mínima) | Se coloca a ras de suelo con solo poner Y=0 en Unity |
| Se agarra / empuña | El **punto de agarre** | El engine lo sujeta desde ahí |
| Rota sobre un eje (tapa, puerta, palanca, válvula) | El **eje físico** (bisagra, perno, centro de giro) | La rotación en engine gira alrededor del origen |
| Pieza de kit modular | **Esquina/extremo en el grid** | Snapping y rotación en grilla [ver: receta-kit-modular] |

**Origen a la base (barril, cofre-base, farola)** — poner el cursor 3D en la z mínima y hacer origin ahí:

```python
import bpy
obj = bpy.data.objects["Chest_Base"]
co = [obj.matrix_world @ v.co for v in obj.data.vertices]      # coords de mundo
cx = (min(v.x for v in co) + max(v.x for v in co)) / 2
cy = (min(v.y for v in co) + max(v.y for v in co)) / 2
bpy.context.scene.cursor.location = (cx, cy, min(v.z for v in co))
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.context.scene.cursor.location = (0, 0, 0)                  # Shift+C limpia el cursor
```

**Origen de la TAPA a la bisagra** (arista trasera-superior). Poner el cursor en el punto medio de esa arista (seleccionarla en Edit Mode → `Shift+S ▸ Cursor to Selected`) y:

```python
import bpy
lid = bpy.data.objects["Chest_Lid"]
bpy.context.view_layer.objects.active = lid
# ...en Edit Mode, seleccionar la arista de la bisagra y Cursor to Selected...
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')   # origen = eje de giro real de la tapa
```

Manual alternativo (sin script): `Object ▸ Set Origin ▸ Origin to 3D Cursor`. Las variantes son *Geometry to Origin*, *Origin to Geometry*, *Origin to 3D Cursor*, *Origin to Center of Mass* (`bpy.ops.object.origin_set` enums: `ORIGIN_GEOMETRY`, `ORIGIN_CURSOR`, `ORIGIN_CENTER_OF_MASS`, `ORIGIN_CENTER_OF_VOLUME`, `GEOMETRY_ORIGIN` — verificar enum exacto en vivo si automatizas).

**Jerarquía para animar en Unity:** la tapa se parenta a la base (root del prop). `Ctrl+P ▸ Object (Keep Transform)`:

```python
import bpy
base = bpy.data.objects["Chest_Base"]; lid = bpy.data.objects["Chest_Lid"]
bpy.ops.object.select_all(action='DESELECT')
lid.select_set(True); base.select_set(True)
bpy.context.view_layer.objects.active = base          # el activo es el PADRE
bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
```

En Unity llegan como base (root) + tapa (hijo con su transform); animar la rotación de la tapa gira sobre su bisagra. **Alternativa válida:** dejarlas separadas sin parentar y armar la jerarquía en el prefab de Unity — pero los pivotes SIEMPRE se fijan en Blender.

### Paso 7 — Cleanup game-ready
Secuencia de limpieza antes de UVs/export [ver: blender/edicion-malla §6]. Por script, sobre cada objeto del prop:

```python
import bpy
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_mode(type='EDGE')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.remove_doubles(threshold=0.0001)        # Merge by Distance
bpy.ops.mesh.delete_loose(use_verts=True, use_edges=True, use_faces=False)
bpy.ops.mesh.dissolve_degenerate()
bpy.ops.mesh.normals_make_consistent(inside=False)   # Shift+N
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.mesh.select_non_manifold(use_wire=True, use_boundary=True,
                                 use_multi_face=True, use_non_contiguous=True)
bpy.ops.object.mode_set(mode='OBJECT')
```

Contar los no-manifold seleccionados: si en una malla que debe ser cerrada no da 0, investigar antes de seguir. Auditar ngons: `Select ▸ Select All by Trait ▸ Faces by Sides > 4` — cero en el export.

### Paso 8 — Presupuesto y validación de tris (con modificadores)
El contador de Edit Mode NO ve lo que multiplican Bevel/Boolean; contar la malla **evaluada**:

```python
import bpy
obj = bpy.data.objects["Chest_Base"]
dg = bpy.context.evaluated_depsgraph_get()
me = obj.evaluated_get(dg).to_mesh()
me.calc_loop_triangles()
print(obj.name, len(me.loop_triangles), "tris")
obj.evaluated_get(dg).to_mesh_clear()
```

Chequear contra el presupuesto de su categoría [ver: modelado/presupuestos-poligonos]. Recordar: el coste real es **vertex count** — cada UV split, hard edge y material extra duplica vértices [ver: modelado/topologia §2].

### Paso 9 — Export a Unity (FBX)
Aplicar transforms y exportar con los settings exactos [ver: blender/import-export]. Objetivo: **1 material slot** por prop (nombre limpio y estable), escala 1, pivotes ya puestos.

```python
import bpy
bpy.ops.object.select_all(action='DESELECT')
for n in ("Chest_Base", "Chest_Lid"):
    bpy.data.objects[n].select_set(True)
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)  # NO location: respeta pivotes
bpy.ops.export_scene.fbx(
    filepath=bpy.path.abspath("//export/Chest.fbx"),
    use_selection=True,
    apply_scale_options='FBX_SCALE_UNITS',   # File Scale 1 en Unity (evita el x100)
    mesh_smooth_type='FACE',                 # smoothing groups; evita el warning de Unity
    add_leaf_bones=False,
    use_mesh_modifiers=True,                  # aplica Bevel/WN/Boolean/Triangulate en el export
    object_types={'EMPTY', 'MESH'})
```

- **Sockets** (attach points, p. ej. dónde cuelga una linterna en la farola): Empties (Plain Axes) como hijos, prefijo `SOCKET_`.
- **Colliders:** malla convexa low-poly `UCX_Chest_Base` junto al render mesh (convención Unreal; en Unity requiere AssetPostprocessor o Generate Colliders) [ver: blender/import-export].
- **NO location apply** si el pivote debe conservarse: aplicar solo rotación y escala. La rotación -89.98 en Unity es cosmética y aceptable en el prop; o Bake Axis Conversion en Unity.
- **Gate final:** abrir el FBX en Unity — File Scale 1, tamaño real contra una cápsula de 2 m, sin caras negras, 1 material con el nombre correcto, la tapa gira sobre su bisagra. "Listo" = esto verificado, no "el export no dio error" [ver: pipeline/arte-a-unity §10].

## 3. Variantes baratas: 5 versiones de un prop base
Cantidad se fabrica con variantes, no con assets únicos. Orden de más barato a más caro [ver: modelado/props-armas §9]. En Blender, las dos primeras técnicas usan **duplicados enlazados** (linked duplicates, `Alt+D`): comparten la misma malla → 5 barriles pesan casi lo de uno en el .blend [ver: blender/organizacion-blend].

```python
import bpy
base = bpy.data.objects["Barrel"]
for i, dx in enumerate([1, 2, 3, 4], start=1):
    dup = base.copy()                 # linked: comparte la MISMA mesh data (= Alt+D)
    bpy.context.collection.objects.link(dup)
    dup.location.x = dx * 0.8
    dup.name = f"Barrel_v{i}"
    # variante de material sobre la misma malla: asignar otro material al slot 0
    # dup.data.materials  -> compartido; para material propio: dup.data = base.data.copy()
```

| # | Técnica | En Blender |
|---|---|---|
| 1 | Variante de material/textura sobre la misma malla | Linked dup (`base.copy()`); cambiar el material del slot. Casi cero coste |
| 2 | Tinte por vertex color | Pintar vertex colors; una máscara, infinitos colores |
| 3 | Decal / desgaste localizado | Plano con textura sobre la malla; rompe repetición sin tocarla |
| 4 | Recombinación de piezas | Full copy (`base.data = base.data.copy()`) y quitar/añadir herrajes — exige haber modelado por PIEZAS |
| 5 | Deformación de proporción | Escalar la copia sobre las mismas UVs (alto/ancho) |

⚠️ **Al exportar, los linked duplicates se des-instancian**: cada copia escribe su malla en el FBX ("exported objects do not share data") [ver: blender/import-export]. El ahorro es de autoría/memoria en Blender; en Unity el reuso se hace con prefabs. Las variantes comparten pivote, escala y naming con el base + sufijo (`_v1`, `_v2`).

## Reglas prácticas
1. Clasifica el prop (fondo/estándar/hero/interactivo) y elige método (low-poly directo vs mid-poly+WN vs high→low) ANTES de la primera primitiva.
2. Escena en metros, `scale_length=1.0`, maniquí humano en escena; modela a medida real.
3. Aplica escala (`Ctrl+A`) tras el blockout y otra vez antes de exportar — bevel/solidify/merge fallan con escala ≠ 1.
4. Aprueba silueta y proporciones EN engine con la cámara del juego; nunca en el viewport del DCC.
5. Orden del stack fijo: **Mirror → Boolean → Bevel → Weighted Normal → Triangulate (último)**.
6. Mirror solo si es simétrico, con origen en el eje, Clipping+Merge ON; Bevel siempre DESPUÉS de los booleans.
7. Bevel mid-poly: 2 segmentos, ~0.004 m, Limit Angle ~30°, Clamp Overlap ON; Weighted Normal detrás con Keep Sharp.
8. Cutters de boolean manifold, en colección `CUT_`, y limpia la topología que deja el corte.
9. Ningún filo perfectamente afilado sale a producción: biselado real (mid-poly) o en el normal map (high→low).
10. Shade Auto Smooth 30–45° + Mark Sharp puntual; "Auto Smooth" como checkbox no existe en 5.x.
11. Partes móviles = objetos separados (`P ▸ By Selection`), estado por defecto cerrado, interior visible modelado, recorrido probado sin clipping.
12. Origen según USO: base al suelo / agarre / eje de bisagra / esquina de grid. Se fija en Blender; en Unity no se edita.
13. Pivote de la tapa en la bisagra vía cursor 3D + `Origin to 3D Cursor`; parenta la tapa a la base (`Keep Transform`) o arma la jerarquía en el prefab.
14. Cleanup completo (merge by distance, delete loose, recalc normals, non-manifold, ngons=0) antes de UVs y export, en ese orden.
15. Cuenta tris de la malla EVALUADA (depsgraph), no la de Edit Mode; audita vertex count, no solo tris.
16. Export: `FBX_SCALE_UNITS`, Smoothing=Face, Add Leaf Bones OFF, apply rotación+escala pero NO location; objetivo 1 material slot con nombre limpio.
17. Variantes por coste: material → vertex color → decal → recombinar → proporción; linked dup (`Alt+D`/`base.copy()`) para las baratas, sabiendo que se des-instancian al exportar.
18. "Listo" = FBX abierto en Unity con la checklist pasada (escala 1, sin caras negras, 1 material, tapa gira en su bisagra), no "el export no dio error".

## Errores comunes
| Pitfall | Síntoma | Antídoto |
|---|---|---|
| Detallar antes de aprobar el blockout en engine | Se retrabaja el asset entero en fase tardía | Gate fase 2: silueta/escala aprobadas con la cámara real primero |
| Bevel antes del Boolean/Mirror | Cortes sin biselar; biseles fantasma en el eje de simetría | Bevel después de todo lo constructivo (§3) |
| Cutter de boolean no manifold | Caras basura, agujeros, resultado impredecible | Cerrar el cutter (manifold); solver Manifold si todo es manifold, si no Exact |
| Boolean deja topología sucia sin limpiar | Ngons y loops sueltos que rompen el bevel/bake | Limpiar el corte (dissolve/knife) tras el Difference |
| Filos perfectamente afilados en el low | Se ve "3D barato", el reflejo delata la arista | Bevel real (mid-poly) o bevel en el high para el normal (high→low) |
| Weighted Normal sin efecto | El shading no cambia | Debe ir DESPUÉS del último generate y la malla necesita caras smooth; revisar Keep Sharp |
| Buscar "Auto Smooth" (tutorial ≤4.0) | El checkbox no existe | `shade_auto_smooth(angle)` o Mark Sharp manual (§4) |
| Tapa del cofre soldada a la base | No se puede animar; se ve el hueco al "abrir" imaginado | Separar con `P`; modelar el interior; estado por defecto cerrado |
| Pivote de la tapa en el centro | Al rotar en Unity, la tapa flota y atraviesa la base | Origen en la arista de la bisagra (cursor 3D + Origin to 3D Cursor) |
| Origen en el centro de un prop que apoya | Flota o se hunde en el suelo; hay que ajustar Y a mano en cada instancia | Origen a la base (z mínima) — se coloca con Y=0 |
| Aplicar location antes de exportar | El pivote se va al world origin, se pierde el trabajo del §6 | Apply rotación+escala, **NO** location |
| Escala x100 en Unity | Prefab con escala (100,100,100), File Scale 0.01 | `apply_scale_options='FBX_SCALE_UNITS'` |
| Contar tris en Edit Mode | El presupuesto se pasa sin darse cuenta (Bevel/Boolean multiplican) | Contar la malla evaluada por depsgraph (§8) |
| Múltiples materiales por descuido | Draw calls de más; falla el "1 material esperado" | Consolidar slots; objetivo 1 material por prop |
| Linked dup exportado esperando instancias | El FBX pesa por 5 mallas, no 1 | Es esperado: se des-instancia; el reuso real es por prefab en Unity |
| Ngon olvidado en una tapa de cilindro | Shading sucio / bake con artefactos ahí | Grid Fill o poke en las tapas; auditar Faces by Sides > 4 antes del export |

## Fuentes
Bases sintetizadas (no repetir; el detalle vive ahí): **[ver: modelado/props-armas]** (método por fases, clasificación, jerarquía de formas, pivotes de props interactivos, variantes), **[ver: modelado/topologia]** (quads/tris, vertex count, hard edge=UV split), **[ver: modelado/hard-surface]** (elección de workflow, booleans, bevels), **[ver: blender/modificadores]** (stack Mirror→Boolean→Bevel→WN→Triangulate, solvers, propiedades bpy verificadas contra el manual 5.2), **[ver: blender/edicion-malla]** (Separate `P`, cleanup, Shade Auto Smooth, normales), **[ver: blender/import-export]** (settings FBX, escala 100×, pivote=origen, sockets/colliders, des-instanciado al exportar).

Fuentes web consultadas en vivo esta sesión:
- **Polycount forums — hilos de hard-surface subdivision / hard edges & normal maps** (polycount.com) — soporte de loops y bevels paramétricos, face-weighted normals como "game changer" para curvas sin geometría, regla hard edge ⇒ UV split, tangent space sincronizado (MikkTSpace) para Unity/Unreal.
- **The Art of Optimizing 3D Assets for Games** (gamedeveloper.com) — pivotes en centros lógicos de rotación/anclaje, LODs por distancia, normal maps para detalle sin geometría, atlasing/reuso de materiales, export con escala y jerarquía coherentes.

Operadores/atajos de Blender usados en la receta (Set Origin, Separate `P`, Parent `Ctrl+P Keep Transform`, cursor 3D `Shift+S`, primitivas, cleanup, export FBX): verificados contra el **Manual de Blender 5.2 LTS** a través de las bases hermanas de `blender/` (que los citan página por página); las propiedades bpy de Bevel/Weighted Normal/Triangulate y el export FBX están verificadas empíricamente allí. Los enums de `bpy.ops.object.origin_set` y `mesh.separate` son estables entre versiones pero conviene confirmarlos en un Blender vivo antes de automatizar por MCP [ver: blender/bpy-scripting].
