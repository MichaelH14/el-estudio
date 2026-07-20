# Receta: kit modular de entorno en Blender → Unity

> **Cuando cargar este archivo:** cuando toca EJECUTAR en Blender 5.2 un kit modular de arquitectura (muros, esquinas, pisos, techos, puertas, ventanas) y sacarlo a Unity 6 — desde configurar grid y snapping hasta el export por pieza y la verificación de encaje sin gaps. Es el PUENTE: la teoría de por qué/qué (kits como sistema, footprints, trim) vive en [ver: modelado/entornos-modulares]; la herramienta cruda (snapping, modificadores, FBX) en [ver: blender/interfaz-flujo], [ver: blender/modificadores], [ver: blender/import-export]. Aquí van los PASOS y operadores exactos, no la teoría.

Esta receta NO repite: la filosofía del kit ni las métricas de gameplay (congélalas antes — [ver: modelado/entornos-modulares §2/§6], [ver: gamedev/level-design]); ni el detalle de cada modificador ([ver: blender/modificadores]); ni la tabla completa de settings FBX ([ver: blender/import-export]). Asume que ya elegiste seguir un kit y que las métricas están fijas.

## 0. Precondiciones (antes del primer vértice)

Lo que esta receta da por hecho — resuelto en las bases, no aquí:

| Decisión congelada | Dónde se decide | Valor del ejemplo trabajado |
|---|---|---|
| Métricas de gameplay (jugador, puerta, pasillo, muro) | [ver: gamedev/level-design], [ver: modelado/entornos-modulares §6] | muro alto 3.0 m · puerta 1.25×2.5 m · pasillo ≥ 2.0 m |
| Módulo de grid (1/2/4 m) | [ver: modelado/entornos-modulares §2] | **2 m** (interior estándar) |
| Convención de pivot | esta receta, §2 | esquina min-XY, base Z=0 |
| Presupuesto de tris por pieza | [ver: modelado/presupuestos-poligonos] | muro plano ~12–50 tris |
| Escala 1 u = 1 m, métrica | [ver: blender/interfaz-flujo §10] | Metric, Unit Scale 1.0 |

**Elegir el módulo** (compresión de [ver: modelado/entornos-modulares §2]): 1 m interiores densos · **2 m** interior estándar FPS/3ª persona · 4 m exteriores/naves. Regla dura: tamaños de pieza múltiplos entre sí (potencias de 2); el módulo NO se cambia después de producir piezas.

## 1. Configurar escena, grid y snapping para el módulo

**bpy — setup game-ready + snapping modular** (compacta [ver: blender/interfaz-flujo §10/§9]; una intención por llamada si vas por MCP [ver: blender/blender-mcp-operativo]):

```python
import bpy
sc = bpy.context.scene
sc.unit_settings.system = 'METRIC'
sc.unit_settings.scale_length = 1.0
sc.unit_settings.length_unit = 'METERS'
ts = sc.tool_settings
ts.use_snap = True                         # Shift-Tab en UI
ts.snap_elements = {'INCREMENT'}           # Increment/Grid para colocar módulos
ts.use_snap_grid_absolute = True           # Absolute Grid Snap: ancla AL grid, no relativo
ts.use_snap_translate = True               # Affect: Move
ts.use_snap_rotate = False
ts.use_snap_scale = False
print(ts.snap_elements, ts.use_snap_grid_absolute)   # evidencia
```

- **Absolute Grid Snap** es la clave: sin él, `Increment` snapea en pasos RELATIVOS a la posición inicial y el kit se desalinea ([ver: blender/interfaz-flujo §9]). En UI: imán del header ▸ Snap To `Increment` + checkbox **Absolute Grid Snap**.
- `Ctrl` mantenido durante un `G`/`R`/`S` = snap temporal (lo más usado); `Shift`-`Tab` togglea el snap permanente.
- **El paso de Increment ≈ 1 m y se subdivide al hacer zoom** — no garantiza saltos de 2 m por sí solo. Para offsets EXACTOS del módulo, prefiere **valor tipeado** (`G` `X` `2` `Return`) o el **Array** del §4; el grid snap es ayuda visual, no el mecanismo de precisión. *NO VERIFICADO el mapeo exacto increment↔escala de grid en 5.2: confirmar en Blender vivo antes de fiarte solo del snap.*
- Visualizar el módulo: `N` ▸ View, y Overlays ▸ Guides ▸ Scale/Subdivisions para que el grid dibujado ayude a leer los 2 m. `Numpad7` (Top ortográfica) para trabajar el layout en planta.

## 2. Convención de pivot: esquina, no centro (el paso que hace que encaje en Unity)

La regla operativa de esta receta: **origen en la esquina min-X min-Y de la huella, a la altura de la base (Z=0)**. Así cada pieza se coloca en Unity sobre una coordenada entera del grid (0,0 / 2,0 / 2,2…) y snapea sin ajuste. Es UNA convención para TODO el kit — cuál no importa, que sea la misma sí ([ver: modelado/entornos-modulares §2]).

Patrón manual (3D Cursor, [ver: blender/interfaz-flujo §8]):
1. Edit Mode ▸ seleccionar el vértice de la esquina inferior → `Shift`-`S` ▸ **Cursor to Selected**.
2. Object Mode ▸ `Object ▸ Set Origin ▸ **Origin to 3D Cursor**`.
3. `Shift`-`C` o `Shift`-`S` ▸ Cursor to World Origin para devolver el cursor.

**bpy — origen a la esquina min del bounding box** (automatiza el patrón; sirve en batch para todo el kit):

```python
import bpy
from mathutils import Vector
sc = bpy.context.scene
def origen_esquina(obj):
    loc = [Vector(c) for c in obj.bound_box]            # 8 esquinas locales
    mn  = Vector((min(v.x for v in loc), min(v.y for v in loc), min(v.z for v in loc)))
    prev = tuple(sc.cursor.location)
    sc.cursor.location = obj.matrix_world @ mn          # esquina min en mundo
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    sc.cursor.location = prev
    print(obj.name, "origen ->", tuple(round(x, 4) for x in obj.location))
origen_esquina(bpy.context.object)
```

Verificación del pivot: la pieza recién puesta debe quedar con **rotación (0,0,0), scale (1,1,1) y su origen sobre una intersección del grid**; auditar con `N` ▸ Item. Antes de exportar: `Ctrl`-`A` ▸ All Transforms ([ver: blender/import-export]).

## 3. Modelar el kit mínimo a escala de gameplay

Kit mínimo antes de ampliar ([ver: modelado/entornos-modulares §3]): muro recto, esquina interior, esquina exterior, muro-puerta, muro-ventana, piso, techo, remate/trim, escalera, pilar. Cada pieza **más ancha/alta que la realidad** — se dimensiona por cámara y personaje, no por plano de arquitecto ([ver: modelado/entornos-modulares §6]).

Ejemplo trabajado, **módulo 2 m, muro 3.0 m, altura de planta (pitch) 3.2 m** (muro 3.0 + losa 0.2):

| Pieza | Huella X×Y (m) | Alto Z (m) | Origen (esquina) | Notas de modelado |
|---|---|---|---|---|
| Muro recto | 2.0 × 0.1 | 3.0 | (0,0,0) base | La que más se repite; plano con grosor por Solidify o box |
| Piso (losa) | 2.0 × 2.0 | 0.2 (Z 0→−0.2) | (0,0,0), cara sup. en Z=0 | El piso de arriba = techo del de abajo; una losa por nivel |
| Techo | 2.0 × 2.0 | 0.2 | (0,0,0), se coloca a Z=3.0 | Grosor real: se ve al apilar plantas |
| Esquina interior | 0.1 × 0.1 (+2 tramos) | 3.0 | vértice de esquina | 90° adentro; **NO es la exterior rotada** (cara visible distinta) |
| Esquina exterior | 0.1 × 0.1 (+2 tramos) | 3.0 | vértice de esquina | 90° afuera |
| Muro-puerta | 2.0 × 0.1 | 3.0 | (0,0,0) base | Hueco 1.25×2.5 centrado (jamba 0.375, dintel 0.5). **Marco estándar de TODO el juego** |
| Muro-ventana | 2.0 × 0.1 | 3.0 | (0,0,0) base | Hueco 1.0×1.2, alféizar a Z=1.0; decidir si el vidrio es pieza aparte |
| Pilar / poste | 0.2 × 0.2 | 3.0 | (0,0,0) base | Tapa esquinas, cruces y costuras verticales |
| Escalera / rampa | 2.0 × 2.0 | sube 3.2 | (0,0,0) base | Pendiente 30–35°; su huella también snapea |
| Trim / remate | tira, longitud múltiplo | según moldura | (0,0,0) | Zócalo/cornisa/marco; mapea a la trim sheet (§5) |

Reglas de construcción (no negociar):
- **Alinear las caras a coordenadas de grid**: los bordes verticales del muro en X=0 y X=2.0 exactos → dos muros adyacentes cierran sin gap ni overlap.
- **Muro-puerta = marco único** estandarizado entre todos los kits: una sola referencia de métrica/animación ([ver: modelado/entornos-modulares §3]).
- Geometría DENTRO de la huella, nunca en su borde exterior; footprints múltiplos entre sí.
- Modela primero en **greybox** (cubos con dimensiones exactas), sin bevel ni detalle — el detalle va después del stress-test (§7).
- Hard-surface fino (bevels, weighted normals) solo cuando el sistema esté aprobado [ver: modelado/hard-surface], [ver: blender/modificadores §4].

## 4. Generar el kit: Array, Mirror e instancias

**Array** para tramos repetidos (muro largo, barandal, columnata). El Array clásico (`type='ARRAY'` en bpy = **Legacy**, [ver: blender/modificadores §3]) con offset constante = módulo:

```python
import bpy
obj = bpy.context.object                         # el muro base
arr = obj.modifiers.new("Array", 'ARRAY')        # Legacy
arr.count = 5
arr.use_relative_offset = False
arr.use_constant_offset = True
arr.constant_offset_displace = (2.0, 0.0, 0.0)   # módulo 2 m en X
```

- Para SOLDAR las copias en una malla continua (barandal, cornisa): Array con **Realize Instances** ON → **Weld** → luego Bevel/Weighted Normal ([ver: blender/modificadores §3/§4] receta "Kit modular"). Si las piezas van sueltas al motor (lo normal en un kit que Unity ensambla), NO sueldes: aplica el Array solo cuando quieras una pieza-compuesta.
- **Mirror** para esquinas y piezas simétricas: origen del objeto en el eje, Clipping ON, Merge ON; la esquina exterior se saca espejando/reorientando la interior SOLO si la cara visible coincide (a menudo no — modélala aparte).

**Instancias para no duplicar malla** ([ver: blender/organizacion-blend §3]):
- `Alt`-`D` (**Duplicate Linked**) comparte la malla: 20 muros iguales = casi 0 MB extra y editar uno edita todos. `Shift`-`D` copia la malla (úsalo solo si vas a modificar esa copia).
- Para montar el cuarto de prueba (§7): `Add ▸ Collection Instance` instancia la colección entera de una pieza como un empty transformable.
- ⚠️ Al exportar FBX las instancias se **des-instancian** (cada copia escribe su malla) — el ahorro de instancias es dentro del .blend; en Unity el instancing lo da el motor por malla+material compartidos ([ver: modelado/entornos-modulares §8], [ver: blender/import-export]).

## 5. Modelar para trim sheet y tileable (el modelado que la textura necesita)

La teoría del trim (biseles 45°, layout estandarizado, "Ultimate Trim") está en [ver: modelado/entornos-modulares §4] y [ver: modelado/high-to-low]. Aquí, lo que hay que HACER en la malla:

**Tileable (muro/piso que repite sin costura):**
- El muro cubre el módulo con **caras planas cuya UV llena el 0–1** (o un múltiplo) de la textura tileable; el borde derecho de la UV continúa en el izquierdo → sin seam al repetir.
- Unwrap: marcar seams en las esquinas de la cara, `U` ▸ Unwrap, y en el UV Editor escalar/encajar la isla al cuadrante 0–1. Para que 2 muros seguidos tilen, sus UVs deben coincidir en U.
- Texel density consistente con el resto del kit ([ver: pipeline/arte-a-unity]); no estires la UV en piezas de distinto tamaño.

**Trim sheet (molduras, marcos, zócalos):**
- La geometría **mapea sus caras a la tira horizontal** que le toca del atlas de trim; las UVs pueden salir de 0–1 a lo ANCHO (las tiras tilean en U), no en V.
- **Hard edges** donde el normal map del trim hace el bevel de 45°; `Edit ▸ Mark Sharp` + Shade Auto Smooth (Smooth By Angle, [ver: blender/modificadores §6]). Normales promediadas ahí arruinan el efecto.
- **Padding** real entre islas UV vecinas contra el sangrado de mips.
- Regla hard edge ↔ UV seam ([ver: modelado/high-to-low]): cada hard edge coincide con un seam.

Un kit entero comparte **1 trim + 2–3 tileables** → coherencia visual y batching barato ([ver: modelado/entornos-modulares §8]). No rompas el material por variar una pieza; varía por instancia (vertex color, decals).

## 6. Organizar el .blend del kit

Estructura por pieza para export limpio ([ver: blender/organizacion-blend §1], [ver: blender/import-export]):

```text
Scene Collection
└── kit_dungeon                    ← nombre del kit
    ├── EXP_wall_a                 ← colección EXPORTABLE (prefijo EXP_ para el batch)
    ├── EXP_wall_door
    ├── EXP_corner_in
    ├── EXP_floor
    ├── ...
    ├── kit_dungeon-ref            ← blueprints (Disable in Renders + no seleccionable)
    └── kit_dungeon-test           ← cuarto de prueba (§7), Exclude from View Layer al exportar
```

- **Naming = contrato con Unity** ([ver: blender/import-export]): objeto y malla con nombre limpio y estable, p. ej. `SM_KitDungeon_Wall_A`, `SM_KitDungeon_Corner_In`. Cero `Cube.001`. El sufijo describe el rol y ayuda al grid/snapping de ProBuilder en Unity (§9).
- Colección raíz = kit; una colección `EXP_<pieza>` por pieza exportable.
- `Ctrl`-`S` antes de operaciones destructivas (apply de stack, joins) y `Ctrl`-`A` ▸ All Transforms en cada pieza antes de exportar.

## 7. Probar el kit ARMANDO un espacio — antes de detallar

No negociable ([ver: modelado/entornos-modulares §3]): el kit se valida montando cuartos, pasillos y loops con las piezas EN GREYBOX; solo si sobrevive se invierte en high-poly y texturas. Dónde armar el test:

| Dónde | Cómo | Cuándo |
|---|---|---|
| **En Blender** | `Add ▸ Collection Instance` de cada pieza; colocar con snap (§1) o coords tipeadas; loop cerrado + apilado vertical | Iteración rápida de arte sin salir del DCC |
| **En Unity** (recomendado) | Exportar el greybox (§8) y armar con el grid del motor; se recorre con el controller real | Validación real: cámara y colisión del juego |

Checklist del stress-test:
- **Cerrar un loop**: el kit vuelve sobre sí mismo pasando por varias piezas sin desfase acumulado.
- **Apilar en vertical**: verifica que muro(3.0)+losa(0.2) = pitch(3.2) y las plantas encajan sin gap.
- **Adyacencias**: toda pieza junto a toda pieza, en las 4 rotaciones (0/90/180/270), sin overlap.
- Señal de alarma: si necesitas una **pieza-parche** para tapar un caso concreto, la huella está mal — arregla el sistema, no parchees.

## 8. Export del kit a Unity

**Decisión: una FBX por pieza** (lo estándar para un kit que Unity ensambla como prefabs snapeables) — cada pieza su asset, su prefab, su entrada en la paleta de ProBuilder/grid. Alternativa: un solo FBX con las piezas como objetos separados (root limpio, cada pieza su origen) si el equipo prefiere una sola importación; Unity crea sub-meshes por objeto.

Settings FBX para Unity (tabla completa y por qué en [ver: blender/import-export]; aquí los que importan al kit):

| Opción | Valor | Motivo |
|---|---|---|
| Apply Scalings | **FBX Units Scale** (`FBX_SCALE_UNITS`) | File Scale 1 en Unity, transforms (1,1,1) — sin el bug del 100× |
| Scale | 1.0 | escena en metros |
| Forward / Up | −Z / Y (defaults) | Blender Z-up → Unity Y-up |
| Smoothing | **Face** | evita warning de smoothing groups |
| Apply Modifiers | ON (salvo shape keys, aquí no aplica) | exporta el Array/Bevel evaluados |
| Add Leaf Bones | OFF | irrelevante sin rig, déjalo OFF |
| Object Types | MESH (+ EMPTY para sockets) | fuera cámaras/luces |

**bpy — export por colección `EXP_`** (patrón de [ver: blender/import-export]; con `Ctrl`-`A` ▸ All Transforms ya hecho en cada pieza):

```python
import bpy, os
OUT = bpy.path.abspath("//export"); os.makedirs(OUT, exist_ok=True)
for col in bpy.data.collections:
    if not col.name.startswith("EXP_"):
        continue
    bpy.ops.export_scene.fbx(
        filepath=os.path.join(OUT, col.name[4:] + ".fbx"),
        collection=col.name,
        apply_scale_options='FBX_SCALE_UNITS',
        mesh_smooth_type='FACE',
        add_leaf_bones=False,
        object_types={'EMPTY', 'MESH'},
    )
    print("exportado:", col.name)
```

Mejor aún para iterar: un **Collection Exporter** por colección (`Properties ▸ Collection ▸ Exporters`, desde 4.2) → **Export All** re-exporta el kit entero de un clic sin reconfigurar ([ver: blender/import-export], [ver: blender/organizacion-blend §1]).

- **Naming para el grid de Unity/ProBuilder**: nombre de pieza estable y descriptivo (`Wall_A`, `Corner_In`, `Floor_2x2`) → la paleta de la escena y el snapping los distinguen. En Unity 6 el snapping modular lo da el **Grid and Snap overlay integrado** (ProGrids es legacy/absorbido); ProBuilder recomienda usar el grid snapping del motor para pegarse a ángulos rectos y evitar T-junctions al combinar piezas (§9).
- **Pivot** = origen del objeto (§2): en Unity el pivot no se edita; si quedó al centro, todo el kit se coloca mal.
- Roundtrip: sobrescribe SIEMPRE el mismo FBX (conserva el GUID/prefabs); no renombres piezas tras el primer import ([ver: blender/import-export]).

## 9. Verificar en Unity que las piezas encajan sin gaps ni z-fighting

La validación es EN el motor, con la cámara y luz del juego — no en el viewport de Blender ([ver: modelado/entornos-modulares §8], [ver: pipeline/arte-a-unity]):

1. **Model tab de cada FBX**: File Scale = 1 (si sale 0.01, faltó FBX Units Scale); root con rotación 0 (o el −89.98 conocido/aceptado) y escala (1,1,1).
2. **Grid and Snap overlay** (Scene view): fija el tamaño de grid = módulo (2 m) y usa **Push to Grid** / increment snapping (`Ctrl` en Windows, `Cmd` en macOS mientras arrastras) para colocar en pasos de módulo.
3. **Vertex snapping** para pegar dos piezas exactas: mantener **`V`**, arrastrar el vértice de una al vértice de la otra (`Shift`-`V` togglea el modo). Comprobar que la costura queda a 0.
4. **Gaps**: colocar dos muros contiguos y una esquina; a luz rasante no debe verse una línea de fondo entre piezas.
5. **Z-fighting**: dos caras coplanares superpuestas parpadean; suele venir de piezas que se solapan en vez de tocarse — el pivot en esquina + colocación por grid lo evita. Si aparece, revisa que las huellas no se pisen.
6. Recorrer el espacio con el **controller real**: pasillos ≥ 2× el jugador, puertas transitables, escaleras cómodas ([ver: gamedev/level-design]).
7. Prototipado extra en Unity: **ProBuilder** puede bloquear formas (Shape tool: escaleras, arcos, puertas) sobre el mismo grid para probar layouts antes de traer arte final; exporta a FBX si una pieza probada merece volverse asset.

## Reglas prácticas

1. Congela métricas y módulo ANTES del primer vértice; el módulo no se cambia tras producir piezas.
2. Escena en metros, Unit Scale 1.0; verifícalo al abrir cualquier .blend.
3. Snapping: `Increment` + **Absolute Grid Snap** ON; pero para offsets exactos del módulo, tipea el valor (`G` `X` `2`) o usa Array — no confíes solo en el grid snap.
4. Pivot en la MISMA esquina (min-XY, base Z=0) en TODAS las piezas; audita con `N` ▸ Item y `Ctrl`-`A` ▸ All Transforms antes de exportar.
5. Caras del muro en coordenadas de grid exactas (X=0 y X=2.0); dos piezas cierran sin gap ni overlap.
6. Kit mínimo en greybox antes de detallar: muro, esquina interior, esquina exterior, muro-puerta, muro-ventana, piso, techo, pilar, escalera, trim.
7. Marco de puerta único estandarizado para todo el juego.
8. Muro(3.0)+losa(0.2)=pitch(3.2): verifícalo apilando dos plantas.
9. Repetición dentro del .blend = `Alt`-`D` (instancia); `Shift`-`D` solo si vas a editar la copia.
10. Array con offset constante = módulo; Realize+Weld solo si quieres una pieza-compuesta, no para piezas sueltas.
11. Esquina exterior NO es la interior rotada: modélala aparte si la cara visible difiere.
12. Trim sheet: hard edges donde el bevel del normal map, padding entre islas, UVs que salen de 0–1 solo a lo ancho.
13. Un kit = 1 trim + 2–3 tileables compartidos; no rompas el material por pieza.
14. Naming limpio y estable (`SM_Kit_Wall_A`), objeto y malla; cero `Cube.001` — es el contrato con Unity.
15. Una colección `EXP_<pieza>` por pieza + Collection Exporter (o el loop bpy) = re-export de un clic.
16. FBX: Apply Scalings = FBX Units Scale, Smoothing = Face, Apply Modifiers ON.
17. STRESS-TEST el kit (loop cerrado, apilado, 4 rotaciones) antes de high-poly; quien lo prueba arma niveles con él.
18. Pieza-parche = huella mal diseñada: arregla el sistema.
19. Verificación final EN Unity: grid snap del motor, vertex snap (`V`), sin gaps a luz rasante ni z-fighting, recorrido con el controller.
20. Sobrescribe el mismo FBX en el roundtrip; no renombres piezas tras el primer import.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Snap `Increment` sin Absolute Grid → el kit se desalinea | Activar **Absolute Grid Snap**; para exactitud, tipear el offset o usar Array |
| Pivot al centro de la pieza | Origen en la esquina min-XY, base Z=0, en TODO el kit (§2); auditar apoyando en grid |
| Pieza con scale ≠ 1 exportada | `N` ▸ Item para detectar; `Ctrl`-`A` ▸ All Transforms antes del FBX |
| Escala (100,100,100) en Unity | Faltó `apply_scale_options='FBX_SCALE_UNITS'` |
| Gaps entre piezas contiguas | Bordes del muro en coords de grid exactas; verificar adyacencia en las 4 rotaciones |
| Z-fighting en costuras | Piezas que se solapan en vez de tocarse; pivot en esquina + colocación por grid; pilares/trim tapan costuras legítimas |
| Esquina exterior = interior rotada y se ve mal | La cara visible difiere: modelar la exterior aparte |
| Detallar/texturizar antes de probar el sistema | Greybox + stress-test (§7); el detalle fosiliza errores de huella |
| Puertas de cada kit con su tamaño | Marco de puerta estandarizado a nivel de juego |
| Instancias GN o `Alt`-`D` que llegan vacías/dobladas a Unity | FBX des-instancia; realizar/aplicar antes; el instancing real lo da Unity por malla+material ([ver: blender/import-export]) |
| Trim con seams y bordes sucios | Hard edges + padding + UVs fuera de 0–1 solo en U |
| Muro tileable que se delata a repetición | Capas de ruptura (decals, props, variantes, vertex color), presupuestadas desde el diseño ([ver: modelado/entornos-modulares §4]) |
| `Cube.001` / `Material.003` en el FBX | Batch Rename (`Ctrl`-`F2`) antes de exportar; naming es contrato con Unity |
| Buscar ProGrids en Unity 6 | Es legacy: usar el Grid and Snap overlay integrado; ProBuilder ya apunta al grid del motor |
| "Listo" = el export no dio error | No: listo = FBX abierto en Unity, piezas snapeadas sin gaps/z-fighting y recorrido con el controller |

## Fuentes

- **Bases sintetizadas** (verificadas contra manual y release notes de Blender 5.2 LTS): [ver: modelado/entornos-modulares] (kit como sistema, grid/módulo, pivots, footprints, kit mínimo, stress-test, trim, escala de gameplay, optimización); [ver: blender/interfaz-flujo] (snapping §9, 3D cursor §8, pivots §7, unidades §10, atajos); [ver: blender/modificadores] (Array Legacy/nuevo, Mirror, Weld, Bevel+Weighted Normal, receta "Kit modular"); [ver: blender/organizacion-blend] (colecciones EXP_, naming, `Alt`-`D` instancias, Collection Instance, Collection Exporters); [ver: blender/import-export] (settings FBX, escala 100×, pivots/naming, batch por colección, checklist Unity). Cross-refs de teoría: [ver: gamedev/level-design], [ver: pipeline/arte-a-unity], [ver: modelado/high-to-low], [ver: modelado/hard-surface].
- **Unity Manual — Grid and Snap** (docs.unity3d.com/Manual/GridSnapping.html) — Unity Technologies — Grid and Snap overlay, snap automático al grid, increment snapping (Move/Rotate/Scale) y personalización de tamaño/eje del grid; base del snapping modular en Unity 6.
- **Unity Manual — Positioning GameObjects** (docs.unity3d.com/Manual/PositioningGameObjects.html) — Unity Technologies — vertex snapping (mantener **`V`**, arrastrar vértice a vértice; `Shift`-`V` togglea), surface snapping (`Shift`-`Ctrl` / `Shift`-`Cmd`), incremento con `Ctrl`/`Cmd` — verificación de encaje pieza a pieza.
- **ProBuilder for Unity — Manual (index)** (docs.unity3d.com/Packages/com.unity.probuilder@6.0/manual/) — Unity Technologies — qué es ProBuilder: build/edit/texture de geometría, level design y prototipado, export a FBX/OBJ para refinar en DCC.
- **ProBuilder — Editing tips / building geometry** (com.unity.probuilder@6.0/manual, workflow-edit-tips) — Unity Technologies — usar el grid snapping de Unity para ángulos rectos, solo 90°/45°, evitar mover vértices más allá de un adyacente y los T-junctions al combinar mallas modulares.
- **ProBuilder — Creating meshes / Shape tool** (com.unity.probuilder@6.0/manual, workflow-create) — Unity Technologies — Shape tool con formas de edificio (escaleras, arcos, puertas) y Poly Shape para bloquear layouts sobre el grid antes del arte final.
- *NO VERIFICADO en esta sesión (WebSearch agotado, manual de Blender bloqueó WebFetch): el paso exacto de Increment snap vs escala de grid en 5.2 — confirmar en Blender vivo. Los operadores/atajos de Blender citados provienen de las bases, ya verificadas contra el manual 5.2.*
