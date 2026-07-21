# Receta: vehículo game-ready en Blender

> **Cuando cargar este archivo:** al EJECUTAR en Blender 5.2 el modelado de un vehículo de juego (coche, camión, moto, tanque, kart) — la secuencia concreta de operadores, atajos y snippets `bpy` que convierte el método en malla entregable. El QUÉ/PORQUÉ vive en [ver: modelado/vehiculos]; la herramienta suelta en [ver: blender/modificadores], [ver: blender/edicion-malla], [ver: blender/materiales-preview]. Aquí solo el flujo puente, paso a paso.

Este archivo NO repite ni la teoría de vehículo ([ver: modelado/vehiculos] tiene las 5 fases, la continuidad G0/G1/G2, la tabla de pivots por tipo, presupuestos y LODs) ni el detalle de cada herramienta ([ver: blender/modificadores] tiene todas las opciones del Bevel/Array/Subsurf; [ver: blender/materiales-preview] tiene el nombre exacto de cada matcap). Da la **cadena de ejecución**: qué operador, en qué orden, con qué verificación, cross-refiriendo lo demás. Genérico para MCP o headless [ver: blender/blender-mcp-operativo] [ver: blender/bpy-scripting].

Las 5 fases de [ver: modelado/vehiculos §2] mapean 1:1 a las secciones §2–§6. El blockout desde referencia genérico está en [ver: pipeline-3d/blockout-desde-referencia]; el flujo base de modelado en Blender en [ver: pipeline-3d/flujo-modelado-blender]. Esto lo especializa a vehículo.

Versión: **Blender 5.2 LTS** → export a **Unity 6**. Datos dependientes de versión, explícitos donde aplica.

> ⚠️ **Nota de verificación honesta:** `docs.blender.org` devolvió 403 en esta sesión, así que las páginas del manual 5.2 NO se pudieron re-verificar en vivo aquí. Los detalles de herramienta (Bevel, Array Circle, Subsurf, matcaps, cleanup) vienen de los archivos base de `blender/`, que SÍ están verificados contra el manual 5.2. De los operadores específicos de vehículo de §1/§5/§6 (`origin_set`, `snap_cursor_to_selected`, `parent_set`, `mesh.spin`, `empty_image_add`, `transform_pivot_point`), 3 se re-verificaron el 20-jul-2026 contra el código fuente real de Blender en GitHub (rama `main`, `object_transform.cc` / `object_add.cc`):
> - `object.origin_set(type=...)` — enum RNA confirmado: `'ORIGIN_CURSOR'`, `'ORIGIN_GEOMETRY'`, `'GEOMETRY_ORIGIN'`, `'ORIGIN_CENTER_OF_MASS'`, `'ORIGIN_CENTER_OF_VOLUME'` (los dos primeros son operadores DISTINTOS: "Origin to Geometry" vs "Geometry to Origin"). **Correcto tal cual estaba.**
> - `object.parent_set(type='OBJECT', keep_transform=True)` — confirmado correcto (enum `"OBJECT"` + booleano `keep_transform`).
> - `object.load_reference_image` — **NO EXISTE** en el Blender actual (existió en versiones viejas, ~2.8x). El operador real de `Add ‣ Image ‣ Reference` es **`object.empty_image_add(filepath=..., background=False)`**; `background=True` da "Background Image". **Corregido en §1** (venía mal en una versión anterior de esta receta, mismo error que se encontró y corrigió en [ver: pipeline-3d/receta-arma]).
> - Resto (`snap_cursor_to_selected`, `mesh.spin`, `transform_pivot_point`) NO re-verificados en vivo esta sesión — API estable de largo recorrido, alta confianza; confirmar en Blender vivo antes de automatizar en producción.

## 0. Setup de escena y convención de ejes

Antes del primer vértice, congela la convención — o pagas re-orientar todo al exportar.

| Ítem | Valor | Cómo |
|---|---|---|
| Unidades | Métrico, 1 unidad = 1 m, Unit Scale 1.0 | Scene Properties ‣ Units [ver: blender/interfaz-flujo] |
| Frente del vehículo | Hacia **-Y** en Blender | El exportador FBX (Forward -Z, Up Y) lo mapea a **+Z/forward** de Unity — confirmar la convención exacta y el bug de rotación en [ver: blender/import-export] |
| Eje de giro de rueda | **X** (lateral) | Con frente -Y y up +Z, la rueda rueda sobre X |
| Eje de bisagra de puerta / dirección | **Z** (vertical) | Puerta abre sobre Z; volante/dirección gira sobre Z |
| Recorrido de suspensión | **Z** | La rueda baja por -Z; el paso de rueda deja holgura en Z [ver: modelado/vehiculos §5] |

Regla de oro de toda la receta (de [ver: modelado/fundamentos-3d §5]): **ninguna pieza hija llega al export con rotación ≠ 0 o escala ≠ 1 cocidas**. Se aplica escala/rotación en la MALLA (`Ctrl-A ‣ Rotation & Scale`) *antes* de fijar el origen (§5), no después.

## 1. Blueprint alineado (fase 1)

Monta las vistas ortográficas como Empties de imagen, a escala real, bloqueadas. La teoría de "el blueprint miente / las fotos engañan" está en [ver: modelado/blueprints-referencias] y [ver: pipeline-3d/blockout-desde-referencia] — aquí la ejecución:

1. `Add ‣ Image ‣ Reference` por cada vista (front, side, top). Crea un Empty tipo `IMAGE`. En bpy: `bpy.ops.object.empty_image_add(filepath=..., background=False)` (⚠️ NO es `load_reference_image` — ese operador no existe en Blender actual; `background=True` da "Background Image" en vez de "Reference").
2. Alinea cada Empty a su plano: front en el plano XZ mirando -Y, side en YZ, top en XY. Propiedades del Empty (Object Data): `empty_image_side`, `use_empty_image_alpha` (bajar opacidad ~0.5), `show_empty_image_perspective` OFF para que solo aparezcan en vistas ortográficas. *(Nombres de propiedad NO re-verificados en vivo esta sesión; confirmar en el Blender de trabajo.)*
3. **Escala a real** por una cota conocida (batalla/wheelbase, o diámetro de rueda): overlay `Measurement ‣ Edge Length` sobre un edge de medición y escala los Empties hasta que la cota coincida con la ficha real [ver: blender/materiales-preview §4] [ver: blender/edicion-malla].
4. Colección `refs` aparte; desactívala como seleccionable (filtro del Outliner) y bloquea transform, para no moverla sin querer.

```python
import bpy
# Cargar las 3 vistas y bloquearlas en una colección 'refs'
col = bpy.data.collections.get("refs") or bpy.data.collections.new("refs")
if col.name not in bpy.context.scene.collection.children:
    bpy.context.scene.collection.children.link(col)
for view, ruta in [("front", "/refs/front.png"), ("side", "/refs/side.png"), ("top", "/refs/top.png")]:
    bpy.ops.object.empty_image_add(filepath=ruta, background=False)   # ajusta la ruta real
    e = bpy.context.object
    e.name = f"REF_{view}"; e.hide_select = True
    e.lock_location = e.lock_rotation = e.lock_scale = (True, True, True)
    for c in e.users_collection: c.objects.unlink(e)     # mover el Empty a 'refs'
    col.objects.link(e)
```

## 2. Blockout de volúmenes (fase 2)

Masas primarias + ruedas en posición y diámetro FINALES. Nada de detalle. Criterio de salida: silueta correcta 360° y **stance probado en engine** [ver: modelado/vehiculos §2].

1. **Cuerpo**: `Add ‣ Mesh ‣ Cube`, escálalo al bounding box de la carrocería contra el blueprint.
2. **Mirror temprano** en el eje longitudinal (X si el largo va en Y): añade Mirror con el origen del objeto en el plano de simetría, `Clipping` ON, `Merge` ON — todo lo posterior actúa sobre la malla ya simétrica [ver: blender/modificadores §2]. Modelas media carrocería.
3. **Ruedas**: `Add ‣ Mesh ‣ Cylinder`; rota 90° sobre Y (`R Y 90`) para tumbar el eje sobre X. Verts del cilindro por tamaño en pantalla [ver: modelado/topologia §6]. Colócalas en su posición y diámetro definitivos — **aquí se congelan** (después no se mueven).
4. **Marca los centros de eje ahora**: por cada rueda, mueve el 3D cursor a su centro y anota (o deja un Empty `hub_FL` ahí). Esos puntos serán los orígenes de §5.
5. **Verifica stance**: silueta en Flat negro orbitando 360° [ver: blender/materiales-preview §5], y export del blockout a Unity con la cámara real del juego [ver: pipeline/arte-a-unity]. En estilizado (§7) esto pesa MÁS: las proporciones exageradas se calibran a ojo en engine [ver: modelado/vehiculos §8].

## 3. Superficies principales con subdivisión (fase 3)

Las superficies grandes (capó, techo, laterales, guardabarros) como **una malla continua de cage mínimo + Subdivision**. El objetivo es reflejo limpio ANTES de cortar nada.

1. Sobre el volumen del cuerpo, construye el cage: pocos loops, espaciado uniforme. Loops con `Ctrl-R` (loop cut; `RMB` para caer al centro exacto), extrude/inset donde haga falta [ver: blender/edicion-malla §2]. La densidad se gana subdividiendo, **no** metiendo loops a mano [ver: modelado/vehiculos §3].
2. **Subdivision Surface**: `Ctrl-1` / `Ctrl-2` (viewport). En el stack: Mirror ARRIBA, Subsurf DEBAJO — con Mirror después salen dos superficies separadas (ejemplo canónico del manual) [ver: blender/modificadores §2].
3. **Control edges / continuidad**: para endurecer un borde bajo subdivisión, elige una vía de [ver: blender/modificadores §6]:
   - Holding edges (loop de soporte con `Ctrl-R`) — sobrevive cualquier export.
   - Crease (`Shift-E`) — malla base limpia, pero **el crease no viaja al pipeline**; úsalo para EXPLORAR, no para el asset que exporta.
4. **Test del reflejo (no negociable)**: corre el protocolo zebra de [ver: blender/materiales-preview §3] — matcap `check_reflection_horizontal` + **orbitar**. Franja que fluye suave = ~G2 (objetivo en carrocería); franja que salta = G0 (solo válido en corte real); franja que gira brusco = G1 (arreglar). El *porqué* de cada nivel está en [ver: modelado/vehiculos §3]; aquí solo se ejecuta y se repite tras CADA cambio de topología.
5. Poles fuera de las superficies vistosas: reubícalos a bajos e interior de pasos de rueda [ver: modelado/topologia §4].
6. Detalle (manijas, tomas de aire) DESPUÉS de validar la superficie — no contaminar el cage base.

```python
# Añadir subsurf y dejar el viewport en matcap zebra para inspección
import bpy
obj = bpy.context.object
ss = obj.modifiers.get("Subdivision") or obj.modifiers.new("Subdivision", 'SUBSURF')
ss.levels = 2; ss.render_levels = 2
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        sh = area.spaces.active.shading
        sh.type = 'SOLID'; sh.light = 'MATCAP'
        sh.studio_light = 'check_reflection_horizontal.exr'  # set 5.x [ver: blender/materiales-preview §2]
```

## 4. Cortes de paneles (fase 4)

De la superficie madre limpia se SEPARAN los paneles — nunca se modelan sueltos [ver: modelado/vehiculos §4].

1. **Marca las shutlines** sobre la superficie siguiendo el blueprint: `K` (Knife) para cortes libres, o `J` (Connect Vertex Path) cuando deben pasar por vértices existentes [ver: blender/edicion-malla §2].
2. **Panel móvil (puerta, capó, maletero)** → objeto propio: en Edit Mode selecciona las caras del panel y `P ‣ Selection` (`bpy.ops.mesh.separate(type='SELECTED')`). Ese objeto llevará su pivot en §5.
3. **Panel decorativo** (no se abre): se queda en la misma malla, corte solo marcado (geometría o normal map según cámara/presupuesto [ver: modelado/hard-surface §7]).
4. **Dale realidad al corte**: grosor de borde (un fold hacia dentro con `I` inset + `E` extrude, o Solidify [ver: blender/modificadores §3]), gap consistente. La sombra/AO del gap se captura luego en el bake [ver: modelado/high-to-low].
5. Cada panel debe **seguir reflejando en continuidad** con sus vecinos: re-corre el zebra (§3.4) tras cortar — el corte no debe ensuciar la curvatura heredada.

## 5. Partes móviles y jerarquía: el núcleo del puente (fase 5)

Aquí está el mayor valor concreto: **cómo poner cada pivot en su eje mecánico real y armar la jerarquía que el rig de vehículo de Unity espera**. El principio ("parte móvil = objeto separado + origen en el eje de rotación") es de [ver: modelado/vehiculos §5]; esta es su ejecución en Blender.

### 5.1 Fijar el origen en el eje mecánico (el gesto que se repite)

Patrón universal — **snap del cursor al eje, luego origen al cursor**:

1. Entra a Edit Mode del objeto móvil y selecciona la geometría que define el eje:
   - **Rueda**: el loop del hub / centro del eje → `Shift-S ‣ Cursor to Selected` (`bpy.ops.view3d.snap_cursor_to_selected()`) deja el cursor en el centro exacto de ese anillo.
   - **Puerta**: el edge vertical de la bisagra (o sus dos vértices) → mismo `Cursor to Selected` = punto medio de la bisagra.
2. Object Mode, con la pieza seleccionada: `Object ‣ Set Origin ‣ Origin to 3D Cursor` (`bpy.ops.object.origin_set(type='ORIGIN_CURSOR')`).
3. El origen del objeto queda EN el eje. Enums de `origin_set` (estables): `'ORIGIN_CURSOR'`, `'ORIGIN_GEOMETRY'`, `'GEOMETRY_ORIGIN'`, `'ORIGIN_CENTER_OF_MASS'`, `'ORIGIN_CENTER_OF_VOLUME'`.

```python
# Fijar el origen de una rueda en el centro de su eje (hub loop ya seleccionado en Edit Mode)
import bpy
bpy.ops.view3d.snap_cursor_to_selected()          # cursor al centro del anillo del hub
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')   # origen del objeto = eje de giro
# Devolver el cursor al mundo para no dejarlo perdido:
bpy.ops.view3d.snap_cursor_to_center()            # Cursor to World Origin
```

### 5.2 Aplicar transforms ANTES de fijar el origen

Si la pieza tiene rotación/escala cocida (típico tras rotar cilindros, o en la rueda espejada con escala -1), **aplica primero** `Ctrl-A ‣ Rotation & Scale` sobre la malla; luego fija el origen (§5.1). Orden inverso = origen mal calculado y ejes torcidos al exportar [ver: blender/import-export]. En espejado con escala negativa, 5.1 voltea normales solo (Corrective Flip Normals) — verifica con Face Orientation [ver: blender/edicion-malla §5].

### 5.3 Nombrar y jerarquizar

1. **Naming** por convención de rig (lo que Unity monta): `body`, `wheel_FL`/`FR`/`RL`/`RR`, `door_L`/`R`, `hood`, `turret`, `steering`… [ver: modelado/vehiculos §5] [ver: pipeline/arte-a-unity §7].
2. **Root**: un Empty en el centro del vehículo a nivel del suelo (`Add ‣ Empty ‣ Plain Axes`, origen en Y=0), nómbralo `<vehiculo>_root`.
3. **Parent**: selecciona todas las piezas, por último el root (activo), `Ctrl-P ‣ Object (Keep Transform)` (`bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)`). Jerarquía PLANA: root → body + una malla por rueda + puertas.
4. **Torreta / maquinaria**: dos niveles — `turret` hija de root, `cañon` hija de turret; base→brazo→antebrazo→pala en cadena, cada pivot en su pasador [ver: modelado/vehiculos §5].

```python
# Emparentar todo al root con Keep Transform
import bpy
root = bpy.data.objects["car_root"]
piezas = [o for o in bpy.data.objects if o.name.startswith(("body","wheel_","door_","hood"))]
bpy.ops.object.select_all(action='DESELECT')
for o in piezas: o.select_set(True)
root.select_set(True)
bpy.context.view_layer.objects.active = root   # el activo es el padre
bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
```

### 5.4 Probar la rotación EN Blender antes de exportar

La verificación que separa un vehículo riggeable de una malla muerta:

1. Cambia el pivot de transform a **Individual Origins**: pie menu `.` (punto) o `bpy.context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'`.
2. Selecciona las 4 ruedas → `R X` (rotar sobre su eje) → deben **girar limpias sobre el eje**, sin cojear ni describir un óvalo. Si una "cojea", su origen está descentrado → repite §5.1.
3. Selecciona una puerta → `R Z` → debe abrir sobre la bisagra, no flotar. El hueco que destapa debe existir (marco y canto modelados [ver: modelado/vehiculos §5]).
4. `Ctrl-Z` para deshacer las rotaciones de prueba (o hazlo en una copia) — el asset se exporta en rest, con las hijas en rotación (0,0,0).

### 5.5 Suspensión: qué se modela y qué NO

En Unity, `WheelCollider` simula el recorrido de suspensión en runtime (extiende hacia abajo desde el collider) — **no hace falta modelar el resorte/amortiguador para que la rueda "suspenda"** [ver: modelado/vehiculos §5]. El modelador solo garantiza dos cosas en Blender:

1. **Hueco real en el paso de rueda** (wheel well): con la rueda en su posición más comprimida (sube ~la mitad del recorrido esperado sobre +Z), verifica que NO atraviesa la carrocería — mueve la rueda a mano en Blender y orbita; si toca, agranda el wheel well en la carrocería, no la suspensión.
2. **Rueda como objeto separado con pivot en el eje** (§5.1) — ya cubierto; es lo único que el rig necesita de la rueda.

Solo modela brazos/amortiguadores visibles como piezas propias (buggy, monster truck, vehículo con bajos expuestos): cada brazo es un objeto separado, pivot en el punto de anclaje al chasis (`Cursor to Selected` sobre el perno/bulón → `Origin to 3D Cursor`, §5.1), jerarquía chasis→brazo→rueda si el brazo es visible en cámara. Si la suspensión no se ve (auto de calle, cámara exterior estándar), no se modela — es trabajo perdido.

## 6. La receta de la rueda (sub-método radial)

Un segmento limpio → array radial → ensamblar → un solo pivot. Nunca modelar 4 ruedas [ver: modelado/vehiculos §7].

1. **Neumático — el segmento**: modela UN módulo de la huella con su perfil de flanco (curvo, sobresale del rin). Toda la limpieza se hace aquí.
2. **Array radial**. Dos vías:
   - **UI (no-destructivo)**: Array (5.0+) en `Shape: Circle`, `Central Axis` = eje del hub, `Align Rotation` ON, `Count` por tamaño en pantalla; luego `Realize Instances` + `Merge` para soldar copias adyacentes [ver: blender/modificadores §3]. ⚠️ El Array clásico legacy NO tiene modo Circle — es el nuevo basado en nodos.
   - **Script (destructivo, simple)**: `bpy.ops.mesh.spin` con el segmento seleccionado (ver snippet).
3. **Huella (tread)**: geometría real solo en hero car / primer plano; el resto, normal map sobre un toro liso [ver: modelado/high-to-low] [ver: modelado/vehiculos §7].
4. **Rin**: objeto SEPARADO del neumático. Mismo truco radial: un radio (spoke) limpio → array circular → realize/weld. Profundidad + tuerca central venden la rueda de cerca.
5. **Ensamblar y fijar el pivot** en el centro del eje (§5.1). Duplica/instancia (`Alt-D` = duplicado enlazado) a las 4 posiciones; el lado opuesto se espeja (escala -1 en X → **aplica escala** y verifica normales, §5.2).

```python
# Neumático radial por Spin: segmento seleccionado en Edit Mode, eje del hub = X
import bpy, math
bpy.ops.mesh.spin(
    steps=48,                     # nº de segmentos = redondez (por tamaño en pantalla)
    angle=math.radians(360),
    center=bpy.context.scene.cursor.location,   # cursor en el centro del eje
    axis=(1, 0, 0))               # eje X (frente -Y, up +Z)
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.remove_doubles(threshold=0.0001)   # soldar la costura del cierre
```

Detalles que delatan una rueda amateur (de [ver: modelado/vehiculos §7]): neumático = cilindro sin perfil, huella que no envuelve el hombro, radios con normales rotas por array mal soldado (revisa con `M ‣ By Distance` y Face Orientation).

## 7. Interiores según cámara

La DECISIÓN (nada / cockpit básico / completo) es de [ver: modelado/vehiculos §6] — depende de qué cámaras del juego ven la pieza. Ejecución en Blender:

| Nivel | Qué construyes | Operadores |
|---|---|---|
| **Nada** | Cristal opaco/tintado, cero interior | Cristal = malla separada (`P ‣ Selection`) con material propio; sin geometría dentro |
| **Cockpit básico** | Cáscara: asientos, volante, salpicadero como volúmenes simples, objeto `interior` | Blockout con cubos/cilindros; texturas modestas |
| **Completo** | Salpicadero con instrumentos, volante animable, pedales | Presupuesto propio (es un entorno pequeño); volante = objeto separado con pivot en el eje de dirección (Z), §5.1 |

- **Cristales = malla separada + material propio** (transparencia): un cristal fundido en la carrocería no puede ser transparente ni romperse aparte [ver: modelado/vehiculos §5].
- **Luces**: la óptica del faro como pieza con material emisivo para encenderse en el engine [ver: pipeline/arte-a-unity §7].
- **Mecánica oculta** (motor, bajos): tapas y volúmenes simples, no modelado real [ver: modelado/vehiculos §6].
- Materiales de trabajo: un slot por zona que Unity verá (`M_Body`, `M_Glass`, `M_Interior`), Principled BSDF plano [ver: blender/materiales-preview §6]. Todo lo opaco agrupado en un material/atlas; cada material extra rompe batching y se justifica.

## 8. Vehículo estilizado low-poly

El estilizado se **re-proporciona** (regla del juguete: ruedas grandes, cuerpo corto y ancho, cero voladizos), no se decima [ver: modelado/vehiculos §8] [ver: pipeline-3d/receta-lowpoly-estilizado].

- **Workflow Blender**: low-poly directo, SIN Subsurf ni Bevel del mid-poly. Shade Flat o Shade Smooth selectivo con Mark Sharp puntual [ver: blender/edicion-malla §5]. Color por paleta-atlas o vertex color [ver: modelado/estilizacion-lowpoly §4].
- **Lo que NO cambia**: los pivots y la jerarquía de §5 son idénticos — la rueda estilizada TAMBIÉN gira sobre su centro; el frente debe leerse en silueta; las ruedas tocan el suelo y caben en la silueta al girar [ver: modelado/vehiculos §8].
- **Blockout en engine igual de obligatorio** (más, porque las proporciones son inventadas): §2.5.
- Es de los assets más baratos de producir bien: sin high-poly ni bake.

## 9. Game-ready: cierre, LODs y export

1. **Cierre según workflow** [ver: modelado/hard-surface §3]:
   - **Mid-poly (default de vehículo de juego)**: stack `Mirror → (Booleans) → Bevel (2 seg, Limit Angle ~30°) → Weighted Normal (Keep Sharp) → Triangulate (Pin to Last)` — la receta anti-bake de [ver: blender/modificadores §4]. Chamfers levemente exagerados para que el bake los capture [ver: modelado/vehiculos §2].
   - **Hero car**: high→low + bake de normal map [ver: modelado/high-to-low] (fase de texturizado, fuera de esta receta).
2. **Limpieza de malla** antes de UVs/export: Merge by Distance, Delete Loose, Degenerate Dissolve, Recalculate Outside, non-manifold check — secuencia completa en [ver: blender/edicion-malla §6].
3. **LODs** nombrados en el objeto `_LOD0.._LODn` para que Unity monte el LOD Group solo: LOD1 elimina interior + piezas chicas (limpiaparabrisas, manijas); LOD2 funde paneles en cáscara; último nivel = silueta. Reducción ~50% tris/nivel con Decimate Collapse [ver: blender/modificadores §3]; las ruedas aguantan un nivel más de detalle (su silueta circular delata el low antes) [ver: modelado/vehiculos §9].
4. **Export FBX**: Apply Modifiers ON, escala 100×, Y-up/-Z-forward, jerarquía preservada — settings exactos y el bug de rotación en [ver: blender/import-export]. Los pivots que fijaste en §5 llegan como los orígenes de cada objeto.
5. **Verifica en Unity** con el runbook de [ver: pipeline/arte-a-unity §10]: escala contra cubo de 1 m, rotación (0,0,0) en las hijas, orígenes de rueda apoyando bien, WheelCollider recibe el radio correcto, materiales con nombre. API 200 ≠ nada — se prueba con la cámara y la luz real del juego [ver: blender/materiales-preview §10].

## Reglas prácticas

1. Convención primero: métrico 1u=1m, frente a -Y, rueda gira sobre X, bisagra/dirección sobre Z. Confirmar el mapeo a Unity en [ver: blender/import-export].
2. Blueprint como Empties de imagen a escala real, en colección `refs`, bloqueada y no seleccionable; escala verificada contra una cota real con Measurement.
3. Mirror temprano (Clipping + Merge ON) sobre el eje longitudinal; modelas media carrocería.
4. Ruedas en el blockout con posición y diámetro FINALES; marca sus centros de eje (cursor/Empty) ahí mismo. Después no se mueven.
5. Superficie grande = cage mínimo + Subsurf (Mirror arriba, Subsurf debajo en el stack); densidad por subdivisión, jamás loops de refuerzo a ojo.
6. Zebra (`check_reflection_horizontal`) + orbitar tras CADA cambio de topología en carrocería; objetivo ~G2, franja que gira/salta = arreglar (salvo corte real).
7. Crease solo para explorar; la versión que exporta usa holding edges o mid-poly (el crease no viaja).
8. Paneles se CORTAN de la superficie madre (`K`/`J`), nunca sueltos; móvil → `P ‣ Selection`, decorativo → corte marcado; cada corte con grosor de borde y gap consistente.
9. Pivot de parte móvil: `Shift-S ‣ Cursor to Selected` sobre el eje → `Object ‣ Set Origin ‣ Origin to 3D Cursor`. Devuelve el cursor al mundo después.
10. Aplica `Ctrl-A ‣ Rotation & Scale` en la malla ANTES de fijar el origen; ninguna hija exporta con transform cocida.
11. Jerarquía plana: root Empty en centro-suelo → body + una malla por rueda + puertas, con `Ctrl-P ‣ Object (Keep Transform)`; naming de rig (`wheel_FL`, `door_L`, `turret`).
12. Prueba la rotación en Blender con pivot `Individual Origins`: ruedas `R X` giran limpias, puerta `R Z` abre sobre bisagra; si cojea, el origen está descentrado.
13. Rueda por método radial: un segmento → Array Circle (o `mesh.spin`) → realize/weld; rin separado con el mismo truco; pivot en el eje; las 4 son instancias/espejos, no mallas nuevas.
14. Suspensión: NO se modela el resorte/amortiguador (`WheelCollider` de Unity lo simula) salvo que se vea en cámara — el modelador solo garantiza wheel well con holgura real y rueda separada con pivot correcto (§5.5).
15. Espejo de rueda: escala -1 → aplicar escala + verificar normales (Face Orientation) antes de fijar origen.
16. Cristales y luces = mallas separadas con material propio desde el modelado; interior según cámara (nada/cáscara/completo), mecánica oculta con tapas.
17. Estilizado: re-proporcionar, SIN Subsurf/Bevel, color por paleta/vertex color — pero pivots, jerarquía, contacto con el suelo y frente legible intactos.
18. Cierre mid-poly con el stack `Mirror→Bevel→Weighted Normal→Triangulate (Pin to Last)`; limpieza de malla completa antes de exportar.
19. LODs `_LOD0..n` en el nombre: LOD1 sin interior ni piezas chicas, LOD2 cáscara, último silueta; ruedas un nivel más detalladas.
20. Export FBX: Apply Modifiers, escala 100×, Y-up, jerarquía; auditar en Unity (escala, rotación 0, radio de rueda, materiales) con la luz real del juego.
21. Números de polycount solo de breakdowns publicados del juego objetivo; decorativo se presupuesta como prop, sin interior ni partes móviles [ver: modelado/vehiculos §9].

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Origen de rueda descentrado → la rueda "cojea" / describe un óvalo al girar | `Shift-S ‣ Cursor to Selected` sobre el loop del hub → `Origin to 3D Cursor`; probar `R X` con Individual Origins (§5.1, §5.4) |
| Fijar el origen ANTES de aplicar rotación/escala → ejes torcidos en Unity | `Ctrl-A ‣ Rotation & Scale` en la malla primero, luego el origen (§5.2) |
| Rueda espejada con normales invertidas (caras negras en Unity) | Escala -1 → aplicar escala + `Shift-N` / Face Orientation antes de exportar (§5.2) [ver: blender/edicion-malla §5] |
| Vehículo exportado como una sola malla → imposible riggear en Unity | Cada parte móvil su objeto + jerarquía root→body→ruedas/puertas (§5.3); Unity WheelCollider exige ruedas independientes [ver: modelado/vehiculos §5] |
| Modelar amortiguador/resorte "para que se vea bien riggeado" cuando no se ve en cámara | Trabajo perdido: `WheelCollider` de Unity simula el recorrido; solo garantizar wheel well con holgura + rueda separada (§5.5) |
| Wheel well sin holgura → la rueda comprimida atraviesa la carrocería en juego | Probar la rueda subida a mano en Blender antes de exportar; agrandar el paso de rueda, no la suspensión (§5.5) [ver: modelado/vehiculos §5] |
| Subsurf antes de Mirror → dos mitades separadas en el eje | Mirror arriba del Subsurf en el stack, Merge ON [ver: blender/modificadores §2] |
| Reflejo con bultos en el capó | Cage mínimo + poles reubicados + detalle tras subdividir; zebra permanente (§3) [ver: modelado/vehiculos §3] |
| Añadir loops "que siguen la superficie" para tapar un defecto | Cada loop extra distorsiona: quitar, no añadir; rehacer con menos geometría [ver: modelado/topologia] |
| Paneles modelados sueltos que no casan en el reflejo | Cortarlos de la superficie madre limpia con `K`/`J` (§4) |
| Corte de panel de papel (sin grosor) | Inset+extrude interior o Solidify + gap consistente; AO del gap al bake (§4) |
| Crease usado en el asset final y se pierde al exportar al baker | Crease solo para explorar; holding edges / mid-poly en lo que viaja (§3) |
| Neumático = cilindro liso con textura estirada | Sub-método radial con perfil de flanco (§6) |
| Modelar las 4 ruedas a mano | Una rueda → instanciar (`Alt-D`) / espejar a las 4 posiciones (§6) |
| Array clásico "no tiene modo Circle" | Es el Array Legacy; el radial es el Array nuevo (5.0, nodos) o `mesh.spin` [ver: blender/modificadores §3] |
| Cursor abandonado fuera del origen → siguientes adds aparecen descolocados | `Shift-S ‣ Cursor to World Origin` tras cada uso del cursor (§5.1) |
| Interior completo en un coche que solo se ve en tercera persona lejana | Decidir nivel por cámara ANTES (§7) [ver: modelado/vehiculos §6] |
| Aprobar el vehículo por un render bonito de Blender | El veredicto es en Unity con shader y luz reales [ver: blender/materiales-preview §10] [ver: pipeline/arte-a-unity §10] |

## Fuentes

Esta receta es un archivo PUENTE: sintetiza la teoría de vehículo y las herramientas de Blender ya documentadas en la base, y añade la cadena de ejecución concreta. Las fuentes web primarias del método (breakdowns de 80.lv de Gołębczyk, Woodvine, Karpovs, Washington, Bhasin; Unity WheelCollider tutorial; BeamNG Vehicle Modeling Guidelines; polycount wiki; Topology Guides; Rhino zebra; Gran Turismo 5) están citadas en [ver: modelado/vehiculos] y [ver: modelado/hard-surface] — no se re-listan aquí.

- **Blender 5.2 LTS Manual** — docs.blender.org/manual — páginas de *Object Origin / Set Origin*, *3D Cursor & Snap*, *Parenting*, *Mesh ‣ Spin*, *Empties (reference/background images)*, *Transform Pivot Point*. ⚠️ **docs.blender.org sigue en 403 a WebFetch y WebSearch sigue agotado (200/200) esta sesión de auditoría** — pero SÍ se verificaron 3 operadores dudosos contra el código fuente real de Blender en GitHub (`object_transform.cc`, `object_add.cc`, rama `main`) el 20-jul-2026: `origin_set` (enum confirmado correcto), `parent_set` (confirmado correcto), y `load_reference_image` (**no existe** — corregido a `empty_image_add`, ver nota al inicio del archivo). Resto (`snap_cursor_to_selected`, `mesh.spin`, `transform_pivot_point`, nombres de propiedad de Empty-imagen como `empty_image_side`) NO re-verificados en vivo esta sesión; confirmar en el Blender de trabajo antes de depender de ellos por script.
- **Blender Python API (current)** — docs.blender.org/api/current — firmas y enums de los operadores de los snippets (`origin_set` type enum, `parent_set` type/keep_transform, `mesh.spin` steps/angle/axis/center, `snap_cursor_to_*`). Misma nota de 403 que arriba.
- **Base sintetizada (verificada contra Blender 5.2 en sus propios archivos):** [ver: modelado/vehiculos] (método, pivots por tipo, ruedas, interiores, LODs), [ver: modelado/hard-surface] (workflows, bevels, decals), [ver: blender/modificadores] (Mirror/Subsurf/Bevel/Array/Weighted Normal/Triangulate, stacks), [ver: blender/edicion-malla] (extrude/knife/separate/normals/cleanup), [ver: blender/materiales-preview] (matcaps, zebra, silueta, la trampa del render). Referencias de apoyo: [ver: modelado/topologia], [ver: modelado/high-to-low], [ver: modelado/blueprints-referencias], [ver: modelado/estilizacion-lowpoly], [ver: blender/import-export], [ver: pipeline/arte-a-unity], [ver: pipeline-3d/blockout-desde-referencia], [ver: pipeline-3d/flujo-modelado-blender].
