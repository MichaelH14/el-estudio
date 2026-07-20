# De blueprint a blockout a escala en Blender

> **Cuando cargar este archivo:** cuando ya tienes el paquete de referencias de un asset y toca EJECUTAR en Blender — montar las vistas en el viewport, poner la figura humana de escala y bloquear los volúmenes primarios con primitivas a tamaño real, antes de cualquier modelado fino. Es el PUENTE entre la teoría de referencias/malla y la herramienta; asume [ver: modelado/blueprints-referencias], [ver: modelado/fundamentos-3d], [ver: blender/interfaz-flujo] y [ver: blender/blender-mcp-operativo] y no los repite.

Stack: **Blender 5.2 LTS** (operadores/props verificados contra manual y API 5.2, jul-2026), export a **Unity 6** con la convención **1 unidad = 1 metro** [ver: pipeline/arte-a-unity]. Lo que aquí es nuevo es la RECETA paso a paso; el porqué vive en las bases.

Qué NO es esto: no es armar el paquete de referencias (eso es [ver: modelado/blueprints-referencias]), no es topología ni detalle (eso es la fase siguiente [ver: pipeline-3d/flujo-modelado-blender]). El blockout es **masa de forma + proporción + escala validada**, y nada más [ver: modelado/fundamentos-3d §8].

---

## 1. Preflight: escena game-ready + regla humana (paso 0, siempre)

Antes de importar una sola imagen: escena en métrico y la figura de 1.8 m plantada. La escala se fija AHORA y es intocable [ver: modelado/fundamentos-3d §4].

```python
import bpy
from math import radians
sc = bpy.context.scene
sc.unit_settings.system = 'METRIC'
sc.unit_settings.scale_length = 1.0
sc.unit_settings.length_unit = 'METERS'          # 1 u = 1 m [ver: blender/interfaz-flujo §10]

def get_col(name):
    c = bpy.data.collections.get(name)
    if not c:
        c = bpy.data.collections.new(name); sc.collection.children.link(c)
    return c
ref_col, blk_col = get_col("REF"), get_col("BLOCKOUT")

# Regla humana de 1.8 m: cilindro cuerpo + esfera cabeza, bloqueada y no seleccionable
bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.17, depth=1.55, location=(0,0,0.775))
body = bpy.context.active_object; body.name = "SCALE_human_1m80"
bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.11, location=(0,0,1.69))
head = bpy.context.active_object
body.select_set(True); bpy.context.view_layer.objects.active = body
bpy.ops.object.join()                             # cabeza+cuerpo en un objeto
for c in body.users_collection: c.objects.unlink(body)
ref_col.objects.link(body)
body.lock_location = body.lock_rotation = body.lock_scale = (True,True,True)
body.hide_select = True                           # no se puede tocar sin querer
print("dims humano:", tuple(round(d,3) for d in body.dimensions))  # ~ (0.34, 0.34, 1.80)
```

- Verificado: `primitive_cylinder_add(vertices, radius, depth)`, `primitive_uv_sphere_add(segments, ring_count, radius)`, `lock_location/rotation/scale` (arrays de 3 bool), `hide_select`.
- La figura de 1.8 m es una **regla que nunca se apaga**: toda masa se juzga a su lado. Para un personaje, además, sirve de guía de proporción por cabezas (~7.5) [ver: modelado/organico-personajes] — no repetir esa tabla aquí.
- Sustituible por un maniquí real (mesh importado) en la misma colección REF, mismos locks.

## 2. PureRef al lado vs referencias EN el viewport

No son excluyentes; se usan a la vez para cosas distintas.

| Necesidad | Herramienta | Por qué |
|---|---|---|
| Mood, material, desgaste, contexto, callouts de "de aquí tomo X" | **PureRef** (o board/manifest) al lado, always-on-top | Es apariencia y decisión, no medida; no estorba el viewport [ver: modelado/blueprints-referencias §8] |
| Blueprint ortográfico contra el que se MIDE la silueta | **Image empty por vista** dentro de Blender | Se modela encima, a escala real, en el mismo espacio 3D |
| Fotos en perspectiva para validar curvatura | PureRef (mirar) + rotar el modelo en perspectiva | El blueprint aplana; la sección transversal la dan las fotos [ver: modelado/blueprints-referencias §6] |
| Foto única con perspectiva como fondo para modelar en cámara | fSpy → cámara reconstruida en Blender | Camera matching, no calcar a ojo [ver: modelado/blueprints-referencias §6] |

Regla: **en el viewport solo entra lo ORTOGRÁFICO y dimensional** (front/side/top). Todo lo demás vive en PureRef. Un agente sin GUI usa el manifest de referencias como equivalente de PureRef y monta solo las vistas orto como image empties.

## 3. Montar las vistas: image empties por eje (front/side/top)

En Blender una referencia ortográfica es un **Empty de tipo Image**. Menú `Add ‣ Image ‣ Reference` (empty visible desde todos los ángulos) o `Add ‣ Image ‣ Background` (empty que se dibuja detrás y solo de frente). Ambos son el MISMO operador con el flag `background`:

```
bpy.ops.object.empty_image_add(filepath, relative_path=True, align='WORLD',
                               location=(0,0,0), rotation=(0,0,0), background=False)
```

`load_reference_image` / `load_background_image` de tutoriales viejos **ya no existen** en la API 5.2 — es `empty_image_add`.

### Props del image empty (Properties ‣ Object Data ‣ Empty) — verificadas 5.2

| UI | bpy | Valores / default | Para el blockout |
|---|---|---|---|
| Size | `empty_display_size` | float, def 1.0 | Escala de la imagen (§4 la calibra a metros) |
| Offset X, Y | `empty_image_offset` | array 2, def (-0.5,-0.5) | (-0.5,-0.5) centra el origen; para línea de suelo abajo usar (−0.5, 0.0) |
| Depth | `empty_image_depth` | `'DEFAULT'`/`'FRONT'`/`'BACK'`, def DEFAULT | **BACK** = detrás del modelo (modelado normal); **FRONT** + opacidad baja = overlay para chequeo de alineación fino (el manual sugiere Front+low opacity) |
| Side | `empty_image_side` | `'DOUBLE_SIDED'`/`'FRONT'`/`'BACK'`, def DOUBLE_SIDED | DOUBLE_SIDED para verla al orbitar; FRONT/BACK si tienes foto de frente y de espalda por separado |
| Show in Orthographic | `show_empty_image_orthographic` | bool, def True | True |
| Show in Perspective | `show_empty_image_perspective` | bool, def True | **False** — que no estorbe al rotar en perspectiva (hint del manual) |
| Only Axis Aligned | `show_empty_image_only_axis_aligned` | bool, def False | **True** — cada imagen solo aparece cuando estás cuadrado a su vista → front/side/top no se pisan |
| Opacity | `use_empty_image_alpha` + `color[3]` | bool def False; alpha 0–1 | `use_empty_image_alpha=True` y `color[3]≈0.4–0.6` |

### Orientación de cada vista

El image empty por defecto (rotation 0) queda tumbado en el plano XY (se ve desde arriba). Rotaciones convención (frente del asset mirando −Y):

| Vista | Numpad | `rotation_euler` | Plano |
|---|---|---|---|
| Top | 7 | (0, 0, 0) | XY |
| Front | 1 | (radians(90), 0, 0) | XZ, normal −Y |
| Right/Side | 3 | (radians(90), 0, radians(90)) | YZ, normal +X |

Verificar SIEMPRE con screenshot desde cada Numpad: la imagen debe leerse derecha y no espejada. Si sale al revés (un blueprint de perfil suele traer el objeto mirando a un lado concreto), sumar 180° sobre la normal del plano y re-chequear — no compensar modelando [ver: modelado/blueprints-referencias §5].

### Snippet: montar las 3 vistas (MCP/headless)

```python
import bpy
from math import radians
ref_col = bpy.data.collections["REF"]
VIEWS = {  # nombre: (ruta_absoluta, rotation_euler)
    "REF_top":   ("/ruta/asset/top.png",   (0,0,0)),
    "REF_front": ("/ruta/asset/front.png", (radians(90),0,0)),
    "REF_side":  ("/ruta/asset/side.png",  (radians(90),0,radians(90))),
}
for name,(path,rot) in VIEWS.items():
    bpy.ops.object.empty_image_add(filepath=path, background=True,
                                   align='WORLD', location=(0,0,0), rotation=rot)
    e = bpy.context.active_object; e.name = name
    e.empty_image_depth = 'BACK'
    e.show_empty_image_perspective = False
    e.show_empty_image_only_axis_aligned = True
    e.use_empty_image_alpha = True; e.color[3] = 0.5
    e.empty_image_offset = (-0.5, 0.0)            # suelo en la base de la imagen
    e.lock_location = e.lock_rotation = e.lock_scale = (True,True,True)
    e.hide_select = True
    for c in e.users_collection: c.objects.unlink(e)
    ref_col.objects.link(e)
    print(name, "-> data:", e.data.name if e.data else None,
          "dims:", tuple(round(d,3) for d in e.dimensions))
```

Nota: `filepath` DEBE ser absoluto en MCP/headless (no hay file browser). El image datablock queda en `obj.data` del empty — chequearlo es la evidencia de que cargó. Bloquear + `hide_select` evita el error clásico de arrastrar la referencia sin darse cuenta.

## 4. Alinear y calibrar la escala real

El eje de simetría del objeto sobre el eje del mundo, suelo en Z=0. Runbook (generalizado en [ver: modelado/blueprints-referencias §5], aquí con las teclas):

1. **Suelo en 0:** con `empty_image_offset` = (−0.5, 0.0) la base de la imagen cae en el origen del empty; el empty en location Z=0 → suelo del objeto en Z=0.
2. **Escala común con una medida conocida:** añadir una caja de calibración de una dimensión REAL del objeto (ancho total, wheelbase, largo del arma) y escalar cada image empty (su `empty_display_size`) con **pivot en el origen del mundo** (`Period` → 3D Cursor, con el cursor en el origen vía `Shift`-`C`) hasta que el objeto en la imagen calce la caja. Interactivo: `S` y arrastrar; por código: ajustar `empty_display_size` y re-medir.
3. **Cruz de alineación:** 2–3 landmarks (eje de rueda, mira, ojo) deben caer en el MISMO punto 3D al cambiar entre Numpad 1/3/7. Truco: un plano temporal a la altura del landmark, visible en front y side; si no toca en ambas, una vista está corrida — corregir la imagen, no el modelo.
4. **Escala fijada = intocable.** Reescalar a mitad de proyecto descalibra todo [ver: modelado/fundamentos-3d §4].

## 5. El blockout: volúmenes primarios con primitivas a escala real

Ahora se bloquea. **Masas primero, detalle nunca antes de validar proporciones** [ver: modelado/fundamentos-3d §8] [ver: gamedev/arte-direccion]. Orden de bloqueo: **silueta en front → estirar en side → conciliar en top** [ver: modelado/blueprints-referencias §6].

### Primitivas para bloquear (add ops verificadas 5.2)

| Primitiva | Operador | Params clave | Uso en blockout |
|---|---|---|---|
| Cubo | `mesh.primitive_cube_add` | `size=2.0` (¡2 m por defecto!) | Torso, cajas, cuerpo de vehículo, módulo |
| Cilindro | `mesh.primitive_cylinder_add` | `vertices=32, radius, depth` | Miembros, cañones, ruedas, columnas |
| Esfera UV | `mesh.primitive_uv_sphere_add` | `segments, ring_count, radius` | Cabeza, cúpulas, juntas |
| Cono | `mesh.primitive_cone_add` | `vertices, radius1, radius2, depth` | Puntas, narices, conos de tobera |
| Plano | `mesh.primitive_plane_add` | `size=2.0` | Suelo, paneles, cartas/billboards |

- Baja los `vertices`/`segments` al bloquear (8–12): el blockout es lectura de masa, no densidad. Ajusta el conteo en el panel **Adjust Last Operation** (`F9`) — no re-crees la primitiva.
- Para hitear una medida EXACTA en metros: crear y luego `obj.dimensions = (x,y,z)` (asigna escala; la escala queda ≠1 y se **aplica al congelar el blockout**, `Ctrl`-`A` ‣ Scale). Aviso de la API: asignar `dimensions` cambia el scale del objeto, y **asignaciones consecutivas sobre el MISMO objeto sin depsgraph actualizado no son fiables** (la referencia de `bpy.types.Object.dimensions` lo advierte explícitamente). Si un agente corrige una masa ya dimensionada dentro del mismo bloque de código, llamar `bpy.context.view_layer.update()` entre asignaciones — o partir la corrección en una llamada MCP separada.
- Cada masa primaria = un objeto en la colección BLOCKOUT (así se mueven, cuentan y aprueban por separado). Para personaje/vehículo simétrico, media mitad + modificador **Mirror** [ver: blender/modificadores].

### Snippet: bloquear una masa y verificar dimensiones (MCP/headless)

```python
import bpy
blk = bpy.data.collections["BLOCKOUT"]
def masa(name, prim, dims_m, loc, **kw):
    getattr(bpy.ops.mesh, prim)(location=loc, **kw)
    o = bpy.context.active_object; o.name = name
    o.dimensions = dims_m                       # fija tamaño real en metros
    for c in o.users_collection: c.objects.unlink(o)
    blk.objects.link(o)
    return o

torso = masa("BLK_torso", "primitive_cube_add", (0.45,0.24,0.62), (0,0,1.20), size=1.0)
# verificación numérica (depsgraph evaluado) [ver: blender/blender-mcp-operativo §7]
dg = bpy.context.evaluated_depsgraph_get()
for o in blk.objects:
    print(o.name, "dim:", tuple(round(d,3) for d in o.dimensions),
          "scale:", tuple(round(s,3) for s in o.scale))
```

Regla del agente: **cada masa lleva su chequeo de `dimensions` en metros** contra la spec y contra la figura de 1.8 m. "El código corrió" no es evidencia [ver: blender/blender-mcp-operativo §5].

## 6. Proporciones antes que detalle: el bucle de corrección

El blueprint es andamio, no verdad [ver: modelado/blueprints-referencias §6]. Bucle hasta que cierre:

1. **Leer la silueta** desde front (Numpad 1, orto): ¿las masas calzan el contorno de la referencia? Corregir en X/Z.
2. **Estirar en side** (Numpad 3): profundidad y perfil. Corregir en Y.
3. **Conciliar en top** (Numpad 7): planta; aquí se descubren los conflictos entre front y side.
4. **Rotar en perspectiva** (Numpad 5 → orbitar): el juez real. Un blockout que calza las 3 vistas pero se ve mal girando ESTÁ MAL — el blueprint no trae la sección transversal [ver: modelado/blueprints-referencias §6].
5. **Contra la figura de 1.8 m:** ¿el tamaño relativo es creíble? Un error de escala se ve aquí antes que en ninguna medida.
6. **Vista master por feature:** si front y side se contradicen (fotos distintas), declarar cuál manda para esa forma y tratar la otra como aproximación.

Error de perspectiva de las fotos: no calcar proporciones de una foto wide cercana; solo tele-perpendicular da proporción, el resto pasa por fSpy o se usa solo para apariencia [ver: modelado/blueprints-referencias §6]. Para un agente: renderizar el WIP desde cámaras orto fijas y compararlo contra la imagen de referencia — no fiarse de "se ve bien".

## 7. Blockout por tipo de asset: qué cambia

La receta es la misma; cambia el ancla de escala, la cámara que decide densidad, cómo se parten las masas y el pivot.

| Tipo | Ancla de escala (se fija 1º) | Masas primarias | Pivot del blockout | Simetría/kit | Deep-dive |
|---|---|---|---|---|---|
| **Prop / item** | Dimensión funcional (asiento 0.45 m, altura de puerta) + distancia de cámara → presupuesto | Caja madre + sub-cajas | Base centrada (Y=0) | — | [ver: pipeline-3d/receta-prop] · [ver: modelado/props-armas] |
| **Arma** | Largo total + posición en manos (FP vs 3ª persona) | Cuerpo / cañón / culata / cargador como **piezas separadas** desde ya (partes móviles) | Punto de agarre | Piezas móviles con su pivot | [ver: pipeline-3d/receta-arma] · [ver: modelado/props-armas] |
| **Personaje** | Altura 1.8 m + conteo de cabezas; A/T-pose | Torso, pelvis, miembros, cabeza como primitivas | Entre los pies | **Mirror** (media mitad) | [ver: pipeline-3d/receta-personaje] · [ver: modelado/organico-personajes] |
| **Vehículo** | Wheelbase + track + altura; blueprint front/side/top obligatorio | Carrocería + ruedas (a su radio real) + cabina | Centro entre ejes, en el suelo | Mirror longitudinal; ruedas como piezas | [ver: pipeline-3d/receta-vehiculo] · [ver: modelado/vehiculos] |
| **Entorno / kit modular** | El **GRID** (módulo base 2/4 m) decide todo; medidas a escala de personaje | Módulos a medida de grid (paredes, pisos, techos) | Esquina/centro CONSISTENTE en todo el kit | Snapping **absoluto** al grid | [ver: pipeline-3d/receta-kit-modular] · [ver: modelado/entornos-modulares] |

- Vehículo/entorno EXIGEN top view; un prop simétrico a veces se bloquea solo con front+side.
- Kit modular: el blockout prueba el GRID antes de detallar una pieza — activar Absolute Grid Snap [ver: blender/interfaz-flujo §9].

## 8. Criterio de salida: cuándo el blockout está listo

Pasa a modelado real [ver: pipeline-3d/flujo-modelado-blender] SOLO cuando TODO esto es cierto:

- [ ] Silueta legible desde las 3 vistas orto **y** girando en perspectiva con la cámara del juego.
- [ ] Proporciones validadas contra la referencia (vista master por feature) y contra la figura de 1.8 m.
- [ ] Escala real: `dimensions` en metros plausibles; el asset junto al humano se ve del tamaño correcto.
- [ ] Todas las masas **primarias** presentes; ninguna secundaria/terciaria todavía.
- [ ] Frente convencional correcto y apoya en Y=0 (pivot provisional por uso [ver: modelado/fundamentos-3d §5]).
- [ ] Legible a la distancia de cámara real del juego (nada de detalle que no se verá).
- [ ] Aprobado contra el visual target / dirección de arte — idealmente EN el engine [ver: gamedev/arte-direccion].
- [ ] **NO** hay aún: topología limpia, detalle, bevels, UVs, materiales. Eso es la fase siguiente.

Si algo de arriba falla, el blockout no sale: se corrige en masa, que cuesta minutos, no en detalle, que cuesta horas.

## 9. Trabajar el blockout por MCP / headless

El bucle sagrado de [ver: blender/blender-mcp-operativo §5], aplicado al blockout:

1. `get_scene_info` → estado inicial (¿está la escena de §1?).
2. `get_viewport_screenshot` ANTES si el cambio es visual.
3. `execute_blender_code` — UNA masa por llamada, bloque de 5–30 líneas, termina en `print()` de verificación.
4. **Evidencia doble:** numérica (`dimensions` con depsgraph evaluado, `scale`, conteo de objetos) + visual (render/screenshot desde front/side/top).
5. ¿Coincide con la intención? Sí → siguiente masa; no → corregir ANTES de seguir.

Verificación visual sin ojos humanos: render Workbench de las 3 vistas orto a archivo y **mirar la imagen** contra la referencia — se puede dejar el image empty visible en el render para superponer. Motor `BLENDER_WORKBENCH` (rápido, sin luces) [ver: blender/blender-mcp-operativo §7].

Cuidados propios del blockout por código:
- **API de datos > operadores modales**: `obj.location`, `obj.dimensions`, `obj.scale` en vez de `transform.translate/resize` (los modales no operan por MCP) [ver: blender/blender-mcp-operativo §6].
- `primitive_*_add` y `empty_image_add` NO son modales: van bien por MCP con params dados.
- Trabajar SIEMPRE en las colecciones REF/BLOCKOUT propias; nunca borrar por `bpy.data.objects` global.
- Guardar (`bpy.ops.wm.save_mainfile()`) tras montar refs y en cada hito de masas.
- Escala masiva (N assets) → headless `blender -b --python ... --python-exit-code 1`, no MCP [ver: blender/blender-mcp-operativo §8].

## Reglas practicas

1. Escena en Metric, 1 u = 1 m, y figura de 1.8 m plantada ANTES de importar la primera imagen; la figura no se apaga nunca.
2. Escala real fijada en el paso 2 con una medida conocida; después, intocable — reescalar a mitad descalibra todo.
3. Referencias orto (front/side/top) como image empties; mood/material/contexto en PureRef o manifest, fuera del viewport.
4. En 5.2 el operador es `bpy.ops.object.empty_image_add(...)`; `load_reference_image`/`load_background_image` ya no existen.
5. Cada image empty: `only_axis_aligned=True`, `show_empty_image_perspective=False`, opacidad 0.4–0.6 (`use_empty_image_alpha`+`color[3]`), Depth BACK (o FRONT+low para chequeo fino).
6. Bloquear las referencias: `lock_location/rotation/scale=(True,True,True)` + `hide_select=True`, en la colección REF.
7. Orientación de vistas: Top (0,0,0), Front (90°,0,0), Side (90°,0,90°); verificar con screenshot por Numpad y voltear 180° si sale espejada.
8. Cruz de alineación: 2–3 landmarks caen en el mismo punto 3D al cambiar entre Numpad 1/3/7; si no, corregir la imagen, no el modelo.
9. Masas primero: silueta en front → estirar en side → conciliar en top; detalle NUNCA antes de validar proporciones.
10. Primitivas de bloqueo con `vertices`/`segments` bajos (8–12); afinar en Adjust Last Operation (`F9`), no re-crear.
11. Ojo con `primitive_cube_add(size=2.0)`: el cubo default mide 2 m. Fijar tamaño real con `obj.dimensions=(x,y,z)`.
12. Una masa = un objeto en BLOCKOUT; simétrico → media mitad + Mirror.
13. Rotar en perspectiva constantemente: calzar las 3 vistas es el andamio, el juez es la vista 3D con la cámara del juego.
14. Por tipo: fijar el ancla de escala correcta (funcional/agarre/altura-cabezas/wheelbase/grid) antes de la primera primitiva.
15. Salida del blockout solo con la checklist de §8 completa; si falla, corregir en masa, no en detalle.
16. MCP: una intención por llamada, evidencia numérica (`dimensions`+`scale`) Y visual en cada paso; "corrió sin error" no es evidencia.
17. Al congelar el blockout: aplicar escala (`Ctrl`-`A` ‣ Scale) antes de pasar a modelado — `obj.dimensions` dejó scale ≠ 1.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Modelar detalle antes de cerrar proporciones | Blockout = solo masa/proporción/escala; checklist de salida (§8) antes de tocar un bevel |
| Arrastrar sin querer una referencia y descalibrar | `lock_*` + `hide_select` en las image empties desde que se montan (§3) |
| `load_reference_image` de un tutorial viejo tira error | En 5.2 es `empty_image_add`; capturar el comando real con hover+`Ctrl`-`C` si dudas [ver: blender/interfaz-flujo §5] |
| Las 3 imágenes se pisan en el viewport | `show_empty_image_only_axis_aligned=True`: cada una solo aparece cuadrada a su vista |
| Referencia estorba al orbitar en perspectiva | `show_empty_image_perspective=False` (hint del propio manual) |
| Cubo "de 1 m" que en verdad mide 2 m | `primitive_cube_add` default `size=2.0`; fijar con `obj.dimensions` y verificar |
| Blockout que calza las 3 vistas pero se ve raro girando | El blueprint aplana; rotar en perspectiva es el juez; cross-check con fotos [ver: modelado/blueprints-referencias §6] |
| Escala rara: físicas/luz/kits rotos aguas abajo | Figura de 1.8 m como regla permanente + `dimensions` en metros en cada masa; nunca "arreglar" con Unit Scale |
| Imagen de perfil montada espejada | Verificar por Numpad; sumar 180° sobre la normal; no compensar modelando |
| Calibrar cada image empty con su propio pivot y desalinear | Pivot de escala en el origen del mundo (`Shift`-`C` + 3D Cursor) |
| Reescalar la referencia a mitad de proyecto | Escala fijada en el paso 2 y congelada; todo lo demás cuelga de ella |
| `obj.dimensions` asignado y export gigante/girado | Deja scale ≠ 1: aplicar `Ctrl`-`A` ‣ Scale al congelar el blockout [ver: blender/import-export] |
| Corregir `obj.dimensions` dos veces seguidas en el mismo objeto y el tamaño final no cuadra | La API avisa: asignaciones consecutivas sin depsgraph actualizado no son fiables; `bpy.context.view_layer.update()` entre asignaciones o separar en otra llamada |
| MCP: asumir que la masa se creó porque no hubo error | `print(dimensions, scale)` + screenshot orto; evidencia doble siempre |

## Fuentes

- **Blender 5.2 Manual — Empties** (docs.blender.org/manual/en/latest/modeling/empties.html, verificado por fetch jul-2026) — display de image empty: Offset X/Y, Depth (Default/Front/Back, con el tip "Front + low Opacity" para reference), Side (Both/Front/Back), Show in Orthographic/Perspective (hint de desactivar Perspective), Only Axis Aligned, Opacity; panel en Properties ‣ Object Data ‣ Empty.
- **Blender 5.2 Python API — `bpy.types.Object`** (docs.blender.org/api/current/bpy.types.Object.html, verificado por fetch) — identificadores y defaults: `empty_image_depth` Literal['DEFAULT','FRONT','BACK'], `empty_image_side` Literal['DOUBLE_SIDED','FRONT','BACK'], `empty_image_offset` (def −0.5,−0.5), `empty_display_size`, `show_empty_image_orthographic/perspective/only_axis_aligned`, `use_empty_image_alpha`, `color` (RGBA), `lock_location/rotation/scale`, `hide_select`, `dimensions` (aviso: asignar cambia scale).
- **Blender 5.2 Python API — `bpy.ops.object`** (docs.blender.org/api/current/bpy.ops.object.html, verificado por fetch) — firma completa de `empty_image_add(*, filepath, relative_path, align, location, rotation, background=False)`; confirmación de que `load_reference_image`/`load_background_image` no están en la API 5.2.
- **Blender 5.2 Python API — `bpy.ops.mesh`** (docs.blender.org/api/current/bpy.ops.mesh.html, verificado por fetch) — firmas de `primitive_cube_add(size=2.0, ...)`, `primitive_cylinder_add(vertices=32, radius, depth)`, `primitive_uv_sphere_add(segments, ring_count, radius)`, `primitive_cone_add(vertices, radius1, radius2, depth)`, `primitive_plane_add(size=2.0)`.
- **Blender 5.2 Manual — Mesh Primitives** (docs.blender.org/manual/en/latest/modeling/meshes/primitives.html, verificado por fetch) — menú Add, Adjust Last Operation, Generate UVs, Align, Cap Fill Type del cilindro.
- Bases sintetizadas (con sus propias fuentes: the-blueprints EULA, 80.lv Haider/Mido Lai, Polynook, Small Art Works, fSpy, Polycount wiki, Marmoset, glTF/Khronos): [ver: modelado/blueprints-referencias] (montaje de referencias, blueprint miente, perspectiva, cruz de alineación, turnarounds), [ver: modelado/fundamentos-3d] (escala 1 m, pivots, game-ready, definición de blockout), [ver: blender/interfaz-flujo] (units, Numpad, snapping, 3D cursor, F3/hover-Ctrl-C), [ver: blender/edicion-malla] (primitivas y edición), [ver: blender/blender-mcp-operativo] (bucle del agente, evidencia numérica+visual, headless).
