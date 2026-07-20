# El flujo de modelar un asset en Blender (de referencia a game-ready)

> **Cuando cargar este archivo:** al ARRANCAR el modelado de UN asset en Blender 5.2 (vía MCP o headless) y necesitar la secuencia maestra completa — es el MAPA que ordena las etapas, dice qué archivo de conocimiento cargar en cada una, define el estado de salida de cada etapa y enruta a la receta concreta del tipo de asset. No es teoría (vive en `modelado/`) ni detalle de herramienta (vive en `blender/`): es el hilo que los cose.

## 0. Cómo se usa este mapa

Este archivo NO se ejecuta de corrido: en cada etapa **carga el archivo indicado**, ejecútala hasta su estado de salida, corre su **checkpoint por código** (§10, sin ojos humanos) y solo entonces avanza. Un asset que no pasa el checkpoint de una etapa NO entra a la siguiente — se repara donde falló. La ejecución en un Blender vivo asume el MCP montado [ver: blender/blender-mcp-operativo]; en batch, `--background --python` [ver: blender/bpy-scripting].

La regla de oro de todo el flujo: **la escala métrica (1u = 1 m) y el pivote correctos se fijan en la Etapa 0. Arreglarlos al final es carísimo** — reescalar arrastra UVs, bakes (distancias de proyección en unidades de escena), rig, física e iluminación del engine [ver: modelado/fundamentos-3d §4] [ver: blender/import-export].

## 1. Vista de pájaro: las 7 etapas + handoff

| # | Etapa | Cargar | Estado de salida (qué queda listo) | Checkpoint (§10) |
|---|---|---|---|---|
| 0 | .blend a escala | `blender/organizacion-blend`, `blender/interfaz-flujo` §10 | Escena métrica, colecciones `ref/high/low/final`, cubo 1 m + figura 1.8 m | Units + colecciones existen |
| 1 | Montar referencias | `modelado/blueprints-referencias` | Vistas orto alineadas al origen, escala real calibrada, cruz verificada | Empties/planos de ref en `ref`, alineados |
| 2 | Blockout a escala | `blockout-desde-referencia`, `gamedev/arte-direccion` | Masas con proporción/escala validadas girando en perspectiva | `dimensions` ≈ spec; se ve bien rotando |
| 3 | Modelado 1º/2º/3º | **la receta del tipo** (§9) + su base `modelado/` | Malla en quads con silueta, detalle primario→terciario resuelto | Silueta ok; tris en rango grueso |
| 4 | Cleanup de malla | `blender/edicion-malla`, `modelado/fundamentos-3d §7` | Malla manifold, sin doubles/ngons/wire, normales fuera | 0 non-manifold, 0 loose, normales ok |
| 5 | **Gate game-ready** | este archivo §8 | Checklist §8 pasada al 100% | La checklist §8 entera |
| — | Handoff UV/bake/textura | (fase siguiente) `modelado/high-to-low`, `modelado/topologia` | Malla congelada + triangulación; entra a UV/bake | — (contrato §7) |
| 6 | Export a Unity | `blender/import-export`, `pipeline/arte-a-unity` | FBX con transforms aplicados, File Scale 1, nombres limpios | Auto-validación reimport (§10) |

Etapas 0-5 + export son MODELADO (este archivo). UV, bake y texturizado son la fase siguiente: aquí solo se define el **handoff** (§7), no se ejecutan.

## 2. Etapa 0 — El .blend a escala desde el minuto cero

Estructura de colecciones fija por asset (crear ANTES de añadir geometría) [ver: blender/organizacion-blend]:

| Colección | Contiene | Nota |
|---|---|---|
| `ref` | Image empties / planos de blueprint, cubo 1 m, figura 1.8 m | Nunca exporta; ocúltala al bakear |
| `high` | High-poly (sculpt / subd / booleans) para el bake | No va a Unity; fuente del detalle [ver: modelado/high-to-low] |
| `low` | Low-poly de trabajo | Se promueve a `final` al pasar el gate |
| `final` | La malla game-ready lista para export | Prefijo `EXP_` si usa Collection Exporter [ver: blender/import-export] |

Setup por código (patrón MCP/headless — extiende el de `interfaz-flujo` §10 con las colecciones):

```python
import bpy
sc = bpy.context.scene
sc.unit_settings.system = 'METRIC'
sc.unit_settings.scale_length = 1.0
sc.unit_settings.length_unit = 'METERS'
sc.unit_settings.system_rotation = 'DEGREES'
for name in ("ref", "high", "low", "final"):          # colecciones base
    if name not in bpy.data.collections:
        sc.collection.children.link(bpy.data.collections.new(name))
# cubo de referencia de 1 m en la coleccion ref (regla del cubo)
bpy.ops.mesh.primitive_cube_add(size=1.0)             # 1 m de arista
ref = bpy.data.collections["ref"]
ob = bpy.context.object; ob.name = "REF_cubo_1m"
[c.objects.unlink(ob) for c in ob.users_collection]; ref.objects.link(ob)
```

**Pivote desde el inicio, no al final:** decide el origen del objeto por USO (base/bisagra/agarre/esquina de kit/centro de giro) [ver: modelado/fundamentos-3d §5] y colócalo con el patrón `Shift`-`S` Cursor to Selected → `Object ‣ Set Origin ‣ Origin to 3D Cursor` [ver: blender/interfaz-flujo §8]. El origen del objeto ES el pivot que ve Unity y en Unity no se edita [ver: blender/import-export].

**Estado de salida:** units métricas confirmadas, 4 colecciones, cubo 1 m + (opcional) figura 1.8 m visibles. **Checkpoint:** §10-A.

## 3. Etapa 1 — Montar las referencias

No se modela de memoria. Runbook completo (paquete dimensional + apariencia, corte por vistas, alineación al origen, calibración de escala con dimensión conocida, verificación de la cruz de 2-3 landmarks) en [ver: modelado/blueprints-referencias §5-§9]. Para un agente sin GUI: **manifest de referencias** (lista de imágenes + propósito por cada una) guardado junto al .blend, mismo contrato que un board PureRef.

Las image empties / planos van a `ref`, alineados al eje del mundo (eje de simetría sobre el eje global, suelo en Z=0), opacidad ~0.5, detrás de la geometría, no seleccionables. **Estado de salida:** vistas montadas y calibradas a escala real; la cruz cuadra al cambiar entre vistas orto. **Checkpoint:** §10-B.

## 4. Etapa 2 — Blockout a escala

Masas primero, cero detalle. Orden de bloqueo: **silueta en front → estirar en side → conciliar en top**, validando cada pocos minutos girando en perspectiva con la cámara del juego (el blueprint es andamio, el juez es la vista 3D) [ver: modelado/blueprints-referencias §6]. Receta genérica del blockout paso a paso en [ver: blockout-desde-referencia]; el criterio de proporción/escala y su aprobación en engine en [ver: gamedev/arte-direccion].

Operadores núcleo del blockout: `Shift`-`A` primitivas, `G/R/S` + eje + valor tipeado (nunca "a ojo"), `E` extrude, `Ctrl`-`R` loop cut, `Ctrl`-`B` bevel, Mirror modifier para simetría [ver: blender/interfaz-flujo §5] [ver: blender/modificadores]. Trabajar con `scale = 1` real: si un `S` dejó el objeto con escala ≠ 1, aplicar `Ctrl`-`A ‣ Scale` de una — no acumular deuda de transform.

**Estado de salida:** volúmenes con la proporción y la escala reales del asset, aprobados girando en perspectiva y contra las fotos; `dimensions` del objeto ≈ medidas de la spec. Nada de bevels finos ni detalle. **Aquí el flujo se RAMIFICA** según tipo de asset (§9) — el blockout aprobado es el punto de bifurcación. **Checkpoint:** §10-C.

## 5. Etapa 3 — Modelado primario → secundario → terciario

La jerarquía de formas (Polycount/Feng Zhu, canon del oficio): **primario** = las masas grandes que dan la silueta; **secundario** = los planos y cortes que rompen esas masas (paneles, biseles grandes); **terciario** = el detalle fino (remaches, tornillos, arañazos) que casi siempre **se BAKEA desde el high-poly, no se modela en el low** [ver: modelado/fundamentos-3d §6] [ver: modelado/props-armas].

| Nivel | Qué es | Dónde vive normalmente |
|---|---|---|
| Primario | Silueta / grandes volúmenes | En el low-poly (geometría real) |
| Secundario | Planos, cortes de panel, bevels grandes | Low-poly + refuerzo en high-poly |
| Terciario | Remaches, costuras, desgaste, poros | **High-poly → normal map** (no toca el low) [ver: modelado/high-to-low] |

**El método concreto (subd vs mid-poly+weighted normals vs booleans/kitbash; sculpt→retopo para orgánico; box-on-grid para modular) lo dicta la RECETA del tipo de asset — salta a §9.** Regla transversal: modelar en quads, cada edge justificado por silueta/deformación/shading/UV [ver: modelado/topologia]. **Estado de salida:** malla con las tres jerarquías resueltas (terciario planificado para bake), en quads, silueta que aguanta la cámara del juego. **Checkpoint:** §10-C + revisión de wireframe.

## 6. Etapa 4 — Cleanup de malla (antes de tocar UV/export)

Pasada de higiene obligatoria con herramientas automáticas, nunca "a ojo" [ver: blender/edicion-malla] [ver: modelado/fundamentos-3d §7]:

| Defecto | Operador Blender | bpy |
|---|---|---|
| Doubles (vértices superpuestos) | Edit `M ‣ By Distance` (Merge by Distance) | `bpy.ops.mesh.remove_doubles(threshold=1e-4)` |
| Non-manifold (wire, caras internas, bordes) | `Select ‣ All by Trait ‣ Non Manifold` | ver §10-D |
| Elementos sueltos (wire/loose) | `Select ‣ All by Trait ‣ Loose Geometry` → `X` | §10-D |
| Normales invertidas | `Shift`-`N` (Recalculate Outside) | `bpy.ops.mesh.normals_make_consistent(inside=False)` |
| Ngons residuales (post-boolean) | `Select ‣ Faces by Sides ‣ >4` → re-topar | — |
| Caras internas ocultas | Seleccionar y borrar lo que la cámara nunca ve | — |

Verificación visual de normales: overlay **Face Orientation** todo azul (rojo = invertida) — para un agente, render por MCP y leer el color, o §10-D por código [ver: blender/blender-mcp-operativo]. **Estado de salida:** malla manifold (bordes por diseño OK), sin doubles/ngons/wire/caras internas, normales hacia fuera. **Checkpoint:** §10-D.

## 7. Handoff a UV / bake / textura (solo el CONTRATO — fase siguiente)

El modelado NO hace UV/bake/textura; aquí se entrega el estado exacto que esas fases esperan [ver: modelado/high-to-low] [ver: modelado/topologia]:

- **`high` y `low` separados**, ambos limpios (§6); el `high` con el detalle terciario que se bakeará.
- **Triangulación decidida y aplicada** ANTES del bake y export (`Ctrl`-`T` Triangulate Faces — atajo estándar histórico de Blender, pero **NO VERIFICADO** contra el manual 5.2 en esta sesión: WebSearch agotado y docs.blender.org devolvió 403; confirmar en Blender vivo o usar `F3` ‣ "Triangulate Faces" como red de seguridad [ver: blender/interfaz-flujo §5]): la triangulación no es determinista entre baker/engine — congelarla evita shading en zigzag [ver: modelado/fundamentos-3d §1].
- **Regla hard edge = UV seam** ya planificada (no ejecutada aquí): todo hard edge debe caer sobre una costura de UV [ver: modelado/high-to-low].
- Escala/pivote/normales ya correctos (Etapas 0/4) — la fase de UV no los arregla.

Handoff limpio = la fase de textura no devuelve el asset. Si UV/bake exigen tocar la malla, se vuelve a la Etapa 4, no se parchea sobre la marcha.

## 8. Etapa 5 — GATE game-ready (criterio unificado)

La checklist que **TODO asset debe pasar** antes de salir a export, sin importar su tipo. Consolida `fundamentos-3d §6-§7`, `import-export` y `arte-a-unity §7`. Falla uno → no exporta.

1. **Escala:** 1u = 1 m; el asset mide lo que la spec (verificar contra el cubo 1 m). §10-C.
2. **Transforms:** rotation (0,0,0) y scale (1,1,1) aplicados (`Ctrl`-`A ‣ All Transforms`). §10-E.
3. **Pivote:** origen por uso (base/bisagra/agarre/esquina); apoya en Z=0 y rota sobre su punto lógico.
4. **Presupuesto:** tris del engine dentro del budget de su categoría [ver: modelado/presupuestos-poligonos]. §10-C.
5. **Topología:** quads de trabajo, cada edge justificado, poles fuera de zonas de deformación [ver: modelado/topologia].
6. **Malla sana:** 0 non-manifold (salvo bordes por diseño), 0 doubles, 0 ngons finales, 0 wire, 0 caras internas. §10-D.
7. **Normales:** hacia fuera (Face Orientation azul); estrategia de shading decidida (smooth total orgánico / hard edges+seam o bevels en hard-surface) [ver: modelado/fundamentos-3d §3].
8. **Materiales:** ≤ los de la spec (ideal 1 por prop), nombres limpios y estables (`Crate_Wood`, no `Material.001`) — el shader real se hace en Unity [ver: pipeline/arte-a-unity §7].
9. **Nombres:** objeto y malla limpios y estables (son el contrato con Unity; no se renombran tras el primer import).
10. **Naming de sistema** si aplica: `_LOD0..n`, sockets Empties, `UCX_` colliders [ver: blender/import-export].
11. **Aprobación:** se ve bien EN el engine con la luz y cámara reales, no en el viewport de Blender [ver: gamedev/arte-direccion].

**Estado de salida:** malla promovida a `final`, apta para UV/bake y para export. **Checkpoint:** §10 completo.

## 9. Ramificación por tipo de asset → a qué receta saltar

El blockout aprobado (Etapa 2) bifurca. Cada rama tiene su método de modelado y su receta concreta:

| Tipo de asset | Señal que lo identifica | Método dominante (Etapa 3) | Receta | Base de teoría |
|---|---|---|---|---|
| **Prop rígido** | Estático, no deforma, sin partes móviles | Box/poly mid-poly; bevels + weighted normals | [ver: receta-prop] | [ver: modelado/props-armas] |
| **Arma** | Partes móviles (corredera, gatillo), 1ª/3ª persona, pivots | Hard-surface: subd / booleans + kitbash | [ver: receta-arma] | [ver: modelado/props-armas] + [ver: modelado/hard-surface] |
| **Vehículo** | Superficies curvas grandes y continuas, ruedas | Subd surfacing, continuidad de superficie | [ver: receta-vehiculo] | [ver: modelado/vehiculos] |
| **Personaje / criatura** | Orgánico que deforma con rig | Sculpt → retopo → bake [ver: blender/sculpt] | [ver: receta-personaje] | [ver: modelado/organico-personajes] |
| **Kit modular** | Encaja en grid, se repite, snapping | Box-on-grid, pivots consistentes, Absolute Grid Snap | [ver: receta-kit-modular] | [ver: modelado/entornos-modulares] |
| **Low-poly estilizado** | Flat shading, vertex color, sin PBR | Poly directo, sin high-poly ni bake | [ver: receta-lowpoly-estilizado] | [ver: modelado/estilizacion-lowpoly] |

Reglas de la bifurcación:
- **Hard-surface** (prop/arma/vehículo): decide UNA estrategia de bevel/normales por asset (subd clásico, mid-poly+FWN, o booleans+decals) [ver: modelado/hard-surface]; el reflejo delata todo, se inspecciona con matcap [ver: blender/materiales-preview].
- **Orgánico:** smooth shading total, topología con anillos concéntricos en las zonas que deforman; la ruta sculpt→retopo casi siempre gana al poly directo salvo estilizado [ver: modelado/organico-personajes].
- **Modular:** el grid y los pivots se deciden ANTES de la primera pieza; un módulo con pivot distinto rompe el kit [ver: modelado/entornos-modulares].
- **Estilizado low-poly:** salta el high-poly y el bake enteros — el look cierra en flat shading + vertex color/paleta-atlas y la luz del engine [ver: modelado/estilizacion-lowpoly].

## 10. Checkpoints por código/MCP (los ojos del agente)

Verificaciones que corren SIN ojos humanos. Un agente las ejecuta por MCP en el Blender vivo [ver: blender/blender-mcp-operativo] o en headless. `assert` que falla = etapa no superada. **Nota de honestidad:** los snippets `bpy`/`bmesh` de esta sección usan APIs reales de Blender pero no se ejecutaron en un Blender vivo durante la sesión que escribió este archivo — córrelos una vez por MCP/headless y confirma que no hay `AttributeError`/API renombrada antes de fiarte de ellos en producción.

**A — Escena (Etapa 0):**
```python
import bpy
u = bpy.context.scene.unit_settings
assert u.system == 'METRIC' and abs(u.scale_length - 1.0) < 1e-6, "escala no metrica 1.0"
for n in ("ref", "high", "low", "final"):
    assert n in bpy.data.collections, f"falta coleccion {n}"
```

**B — Referencias (Etapa 1):** confirmar que hay geometría/empties en `ref` y (si aplica) image empties cargados; la alineación de la cruz es visual → render por MCP y comparar landmarks entre vista front y side.

**C — Dimensiones + tris (Etapas 2/3, budget del gate):** requiere transforms aplicados para que `dimensions` sea real en metros.
```python
import bpy, bmesh
ob = bpy.context.object
deps = bpy.context.evaluated_depsgraph_get()
me = ob.evaluated_get(deps).to_mesh()          # malla CON modificadores
bm = bmesh.new(); bm.from_mesh(me)
tris = len(bm.calc_loop_triangles())           # tris reales del engine
bm.free(); ob.evaluated_get(deps).to_mesh_clear()
print("dims(m):", tuple(round(d, 3) for d in ob.dimensions), "| tris:", tris)
assert tris <= BUDGET_TRIS, f"{tris} tris > budget {BUDGET_TRIS}"
```

**D — Malla sana (Etapa 4):** cuenta non-manifold y loose por bmesh (0 = limpio, salvo bordes por diseño).
```python
import bpy, bmesh
ob = bpy.context.object
bm = bmesh.new(); bm.from_mesh(ob.data)
non_manifold = [e for e in bm.edges if not e.is_manifold]
loose_v = [v for v in bm.verts if not v.link_faces]
ngons = [f for f in bm.faces if len(f.verts) > 4]
bm.free()
print("non-manifold edges:", len(non_manifold), "| loose verts:", len(loose_v), "| ngons:", len(ngons))
# non-manifold puede incluir bordes abiertos POR DISEÑO (plano/cartel): revisar, no asumir bug
```
Normales invertidas por código es frágil (winding); lo fiable es el overlay **Face Orientation** + render por MCP, o `bpy.ops.mesh.normals_make_consistent(inside=False)` como corrección segura. NO VERIFICADO un test puro-código de "cara invertida" sin render — validar visualmente.

**E — Transforms aplicados (gate/export):**
```python
import bpy
ob = bpy.context.object
assert all(abs(s - 1.0) < 1e-4 for s in ob.scale), f"scale {tuple(ob.scale)} != 1"
assert all(abs(r) < 1e-4 for r in ob.rotation_euler), f"rotacion {tuple(ob.rotation_euler)} != 0"
```

**Export (Etapa 6):** la auto-validación por reimport del FBX (malla no vacía, dims < 100 = no hay x100, scale 1) está en [ver: blender/import-export] — correrla siempre. La validación definitiva es en Unity (MCP de Unity si está: leer transform/normales/materiales del prefab).

## 11. Etapa 6 — Export a Unity

Detalle exacto (settings, el 100× de `FBX Units Scale`, la rotación -89.98, qué exporta y qué no, Collection Exporters, naming/sockets/colliders/LODs) en [ver: blender/import-export]; la spec de recepción en Unity en [ver: pipeline/arte-a-unity]. Los 6 imprescindibles:

1. `Ctrl`-`A ‣ All Transforms` sobre la selección (salvo el contra-giro deliberado de props estáticos).
2. FBX: Scale 1.0 + **Apply Scalings = FBX Units Scale** → File Scale 1 en Unity (no 0.01/×100).
3. Forward -Z, Up Y (defaults); Smoothing = Face; Tangent Space OFF (Unity calcula MikkTSpace).
4. Object Types = EMPTY + ARMATURE + MESH (fuera cámaras/luces).
5. Nombres de objeto/malla/material limpios y estables (contrato con Unity, no renombrar tras el 1er import).
6. "Listo" = FBX abierto en Unity y checklist de import pasada, no "el export no dio error".

## Reglas prácticas

1. Cada etapa: cargar su archivo → ejecutar → correr su checkpoint por código (§10) → solo entonces avanzar. Falla el checkpoint = se repara ahí, no se avanza.
2. Escala métrica 1u = 1 m y pivote por uso se fijan en la Etapa 0; arreglarlos al final arrastra UV/bake/rig/física — carísimo.
3. Colecciones `ref/high/low/final` creadas ANTES de la primera geometría; `ref` nunca exporta.
4. Cero assets de memoria: paquete de referencias montado y calibrado (Etapa 1) antes de la primera extrusión.
5. Blockout = masas y escala, cero detalle; validar girando en perspectiva con la cámara del juego, no calzando las 4 vistas.
6. El blockout aprobado es el punto de bifurcación: identifica el tipo de asset y salta a su receta (§9) — no modeles "genérico".
7. Primario→secundario→terciario; el terciario casi siempre se BAKEA desde el high-poly, no se modela en el low.
8. Modela en quads; cada edge justificado por silueta/deformación/shading/UV; poles fuera de zonas que deforman.
9. Cleanup (Etapa 4) con herramientas automáticas, nunca a ojo: doubles, non-manifold, loose, ngons, normales, caras internas.
10. Triangula explícitamente (`Ctrl`-`T`, atajo no reverificado esta sesión — ver nota §7) antes de bake y export, y bakea/exporta ESA triangulación.
11. Todo hard edge cae sobre una costura de UV; decide UNA estrategia de shading por asset.
12. Nunca trabajar con scale ≠ 1 acumulada: aplica `Ctrl`-`A ‣ Scale` en cuanto aparezca.
13. Pivote = origen del objeto vía `Shift`-`S` Cursor to Selected → Set Origin to 3D Cursor; en Unity ya no se toca.
14. El gate game-ready (§8) se pasa entero antes de UV/bake; el handoff (§7) es un contrato, no un "más o menos".
15. Materiales: ≤ spec (ideal 1 por prop), nombres limpios y estables; el shader real vive en Unity.
16. Verifica geometría por Statistics overlay / Spreadsheet / bmesh (§10), no por impresión visual.
17. Normales: overlay Face Orientation todo azul + render por MCP; el test puro-código de cara invertida no es fiable.
18. Aprobación final SIEMPRE en el engine con luz y cámara reales; el viewport de Blender miente.
19. Export: transforms aplicados + FBX Units Scale + nombres congelados; "listo" = abierto y validado en Unity.
20. Ante un tutorial 2.8-4.x: verifica el operador contra el manual 5.2 antes de replicar (FBX import, Collection Exporters, Shade Auto Smooth cambiaron) [ver: blender/blender5-actualidad].

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Modelar detalle antes de aprobar el blockout | Etapa 2 es solo masas/escala; se aprueba girando en perspectiva antes de tocar bevels |
| Dejar la escala/pivote "para arreglar al exportar" | Se fijan en Etapa 0; al final arrastran UV/bake/rig/física — coste multiplicado |
| Modelar con scale ≠ 1 acumulada y "verse bien" | `N ‣ Item` para auditar; `Ctrl`-`A ‣ Scale` en cuanto aparezca; §10-E antes del gate |
| Modelar terciario (remaches, tornillos) en el low-poly | Terciario se bakea desde el high-poly a normal map; el low gasta tris solo en silueta [ver: modelado/high-to-low] |
| Elegir método de modelado sin clasificar el asset | El blockout bifurca (§9): tipo → receta → método; nada de "modelar genérico" |
| Saltar el cleanup y llegar a UV con ngons/doubles | Etapa 4 obligatoria con §10-D; la fase de UV NO arregla malla rota, la rebota |
| Dejar que baker y engine triangulen distinto | `Ctrl`-`T` explícito antes de bake/export; exportar ESA triangulación |
| Confiar en "se ve bien" en el viewport de Blender | Statistics/Spreadsheet/bmesh para números; render MCP para normales; aprobación en engine |
| Hard edge en medio de una isla UV | Seam visible en el bake: hard edge SIEMPRE sobre costura de UV [ver: modelado/high-to-low] |
| Renombrar objeto/malla/material tras el 1er import a Unity | Congelar nombres; renombrar = MeshFilters vacíos y materiales sueltos en prefabs |
| Export "sin error" tomado como listo | "Listo" = FBX abierto en Unity y checklist de import pasada (§11) |
| Test puro-código de cara invertida dado por bueno | Winding no es fiable por código: Face Orientation + render MCP, o `normals_make_consistent` |
| Bordes abiertos del blockout marcados como bug non-manifold | Un plano/cartel tiene bordes por diseño; §10-D lista, el humano/agente decide cuál es bug |

## Fuentes

Bases sintetizadas (el grueso de la verificación de operadores/settings vive en ellas, contrastadas contra el manual Blender 5.2 y las release notes 5.x):
- [ver: modelado/fundamentos-3d] — anatomía de malla, escala/pivote, game-ready vs offline, catálogo de geometría rota, jerarquía primario/secundario/terciario.
- [ver: modelado/blueprints-referencias] — paquete de referencias, montaje en viewport, blockout contra referencia, manifest para agente.
- [ver: blender/interfaz-flujo] — atajos verificados, transformaciones, 3D cursor/pivot, units métricas, colecciones.
- [ver: blender/import-export] — export FBX exacto, escala 100×, rotación -89.98, qué exporta y qué no, auto-validación por reimport.
- [ver: pipeline/arte-a-unity] — spec de entrega 3D, escala 1 m, materiales URP Lit, LODs, checklist de import.
- [ver: blender/organizacion-blend], [ver: blender/edicion-malla], [ver: blender/blender-mcp-operativo], [ver: blender/bpy-scripting] — organización del .blend, herramientas de cleanup, operación por MCP, headless.

Web (canon del oficio; verificadas dentro de las bases hermanas — NO re-fetcheadas en esta sesión, ver gaps):
- **Blender 5.2 Manual — 3D Viewport / Overlays (Statistics), Meshes: Triangulate Faces, Merge by Distance, Recalculate Normals, Select All by Trait** — Blender Foundation, docs.blender.org — operadores y overlays citados.
- **Polycount Wiki — Topology / Texture Baking** — comunidad Polycount — jerarquía de formas, triangular antes de bakear, geometría rota.
- **The Toolbag Baking Tutorial** — Joe Wilson, Marmoset (marmoset.co) — synced tangent workflow, triangular antes de bake, unidades de escena.
- **Modeling Vehicles for AAA Games — Irfan Haider** y **Character Production Workflow Overview — Mido Lai** — 80.lv — flujo profesional referencia→blockout→high→low y comparación continua contra referencia.
