# Receta: arma game-ready en Blender

> **Cuando cargar este archivo:** al modelar una pistola o rifle game-ready en Blender 5.2 (via MCP o headless) de principio a fin — referencia → blockout → hard-surface de las partes → despiece con pivots → sockets → export a Unity 6. Es el PUENTE que convierte la teoría de [ver: modelado/props-armas] + [ver: modelado/hard-surface] en operadores concretos de Blender; la teoría no se repite aquí, se cita.

Versión: **Blender 5.2 LTS** (14-jul-2026) + export a **Unity 6**. El QUÉ y el POR QUÉ están en [ver: modelado/props-armas §7] (armas FP/TP, pivots, attachment points) y [ver: modelado/hard-surface] (bevels, weighted normals, booleans). Las herramientas están en [ver: blender/edicion-malla], [ver: blender/modificadores] y [ver: blender/import-export]. Aquí está el ORDEN EJECUTABLE. Operando por MCP, cargar antes [ver: blender/blender-mcp-operativo].

## 0. Decisiones que gobiernan toda la receta (antes de tocar geometría)

Fijar esto ANTES del paso 1 — cambia el presupuesto entero [ver: modelado/props-armas §1, §7]:

| Decisión | Opciones | Consecuencia en la receta |
|---|---|---|
| **Uso** | First-person viewmodel / third-person world model / ambos | FP = el máximo presupuesto en la mitad que ve la cámara (§7); TP = fracción, manda la silueta |
| **Presupuesto low-poly** | Pistola 6k–10k tris · rifle hero 12k–18k · rango general 8k–20k (NastyRodent) | Fija la densidad por parte antes de subdividir nada [ver: modelado/presupuestos-poligonos] |
| **High-poly** | Sí (hero, bake) 60k–100k · No (mid-poly, sin bake) | Elige workflow por parte en §5 [ver: modelado/hard-surface §3] |
| **Textura** | 2K–4K por arma · texel density 512–1024 px/m | Decide UVs sin mirror en lo visible (§10) |
| **Modularidad** | Arma suelta / sistema con miras-silenciador-cargador intercambiables | Sistema = sockets estandarizados ENTRE armas (§8) |
| **Eje forward** | Convención del proyecto (recomendado: cañón por **+Y**, up **+Z**) | Modelar el arma RECTA sobre ese eje hace que corredera/cerrojo se muevan en UN solo eje y alinea la mira (§4, §6) |

**Regla de oro del arma FP:** modelar el arma alineada a un eje del mundo. No es estética — es lo que hace que (a) el recorrido de las partes lineales sea una traslación limpia en un eje, y (b) la línea de mira quede centrada y recta sin trucos (§6).

## 1. Referencia técnica (fase 1 — no se salta)

El QUÉ está en [ver: modelado/blueprints-referencias] y [ver: modelado/props-armas §2 fase 1]. En Blender:

1. **Tablero de referencia** aparte (PureRef externo) con fotos multi-ángulo + **video de disassembly** — hay que entender cómo la corredera, el cargador y el gatillo SE MUEVEN, no solo cómo se ven.
2. **Blueprint ortográfico en el viewport**: `Add ▸ Image ▸ Reference` (`bpy.ops.object.empty_image_add(background=False)` — verificado contra el operador `OBJECT_OT_empty_image_add`; "Reference" = `background=False`, "Background" = `background=True`) crea un Empty tipo Image. Uno por vista (lateral, superior). En N-panel ▸ Item: bloquear con **Show In ▸ Orthographic** y bajar **Opacity**; en Object ▸ Visibility desactivar **Selectable** para no moverlo sin querer.
3. **Escala del blueprint a medidas reales**: escalar el Empty imagen hasta que el largo del arma coincida con la dimensión real (una pistola ~19 cm, un rifle ~90 cm). El blueprint miente en perspectiva — [ver: modelado/blueprints-referencias]; corregir contra medidas, no contra la foto.

Gate para avanzar: entiendes las PIEZAS (qué es cuerpo fijo y qué se mueve) y sus ejes de movimiento.

## 2. Escena y escala en Blender

- **Unidades**: Scene Properties ▸ Units ▸ Metric, Unit Scale 1.0, 1 unidad = 1 m [ver: blender/import-export]. Modelar a tamaño real desde el primer cubo.
- **Figura/manos de referencia**: importar un maniquí o cápsula del personaje del proyecto al lado — el arma correcta a escala real puede verse enana en un personaje heroico y se ajusta al personaje [ver: modelado/props-armas §3].
- **Cursor 3D en el origen del mundo** (`Shift-C`) antes de empezar; el root del arma vivirá ahí.

## 3. Blockout a escala (fase 2)

Masas primarias solamente — silueta y proporción, cero detalle [ver: modelado/props-armas §4; modelado/hard-surface §3 runbook]. En Blender:

1. Primitivas a medida real por masa grande: cuerpo/receiver, cañón (cylinder), empuñadura, cargador, guardamonte. `Shift-A ▸ Mesh`, y escalar con dimensiones reales en el N-panel (Item ▸ Dimensions).
2. **Nombrar desde ya** cada masa con la convención de partes (§9): `Rifle_Receiver`, `Rifle_Slide`, `Rifle_Barrel`… — el blockout ya define el despiece.
3. **Evaluar la silueta a 45°**, no de perfil: es el ángulo al que el viewmodel se sostiene en pantalla (NastyRodent). Usar matcap de alto contraste [ver: blender/materiales-preview].
4. **Gate en engine**: exportar el blockout a Unity YA y verlo con la cámara del juego (FOV del viewmodel si es FP) — la lente del viewport de Blender engaña [ver: modelado/props-armas §7.1; pipeline/arte-a-unity]. No se detalla nada hasta aprobar proporción EN engine.

## 4. Despiece: cada parte móvil su objeto, su origen en el eje real

**Esta es la decisión game-ready central.** El low-poly se entrega despiezado como se anima, no soldado [ver: modelado/props-armas §7.2]. Corregir pivots después contamina el rig y la animación en Unity.

Partes típicas y dónde va el origen (pivot):

| Parte (objeto) | Movimiento | Origen / pivot | En Blender |
|---|---|---|---|
| `Slide` / `Bolt` (corredera/cerrojo) | Lineal atrás-adelante | Sobre el eje de deslizamiento (= eje del cañón) | Cursor a 2 vértices del riel ▸ Origin to 3D Cursor |
| `Magazine` (cargador) | Sale/entra del pozo | Donde lo agarra la mano; recorrido sin intersectar el arma | Cursor al borde inferior del pozo |
| `Trigger` (gatillo) | Rotación corta | En su perno real | Cursor al perno del gatillo |
| `Hammer`/`Safety`/`Selector` | Rotación | En su perno/eje | Cursor al eje |
| `Cylinder` (tambor, revólver) | Rotación + basculación | Eje del tambor y bisagra del crane | Dos empties/orígenes (uno por eje) |
| `ChargingHandle`/`Pump` | Lineal o rotación | Su eje mecánico | Cursor al eje |

Procedimiento por parte (operadores verificados en la base):

1. **Separar** la geometría de la parte: en Edit Mode, seleccionar sus caras y `P ▸ Selection` → `bpy.ops.mesh.separate(type='SELECTED')` [ver: blender/edicion-malla]. Renombrar el objeto nuevo.
2. **Colocar el cursor 3D en el eje de movimiento**: seleccionar en Edit Mode los vértices que definen el eje (los 2 extremos del riel, el perno) y `Shift-S ▸ Cursor to Selected` (`bpy.ops.view3d.snap_cursor_to_selected`) — cae en la mediana de la selección.
3. **Mover el origen al cursor**: Object Mode ▸ `Object ▸ Set Origin ▸ Origin to 3D Cursor` → `bpy.ops.object.origin_set(type='ORIGIN_CURSOR')` (verificado contra el enum RNA de `OBJECT_OT_origin_set`: el identificador es `ORIGIN_CURSOR`, no `ORIGIN_TO_3D_CURSOR`).

```python
import bpy
# Con la corredera ya separada y activa, y sus 2 vertices de riel seleccionados en Edit Mode:
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.view3d.snap_cursor_to_selected()        # cursor 3D a la mediana del riel
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')  # pivot de la corredera en su eje
bpy.ops.view3d.snap_cursor_to_center()           # devolver el cursor al mundo (Shift-C)
```

- `origin_set` solo mueve la LOCALIZACIÓN del origen, no rota los ejes locales. Por eso el paso 0 (arma alineada a +Y) importa: si el eje de deslizamiento es paralelo a +Y, la corredera se anima como traslación limpia en Y — sin ejes locales torcidos.
- **Modelar el interior que el movimiento revela**: puerto de eyección abierto, pozo del cargador vacío, recámara visible con la corredera atrás. Si al animar aparece un hueco, la ilusión se rompe [ver: modelado/props-armas §7.2].

## 5. Hard-surface de las partes (workflow por pieza)

Elegir workflow POR PARTE, no por arma [ver: modelado/hard-surface §3]. Para armas FP el default de producción es **mid-poly (bevels + weighted normals)**; subdivision+bake solo para piezas hero muy curvas.

**Stack mid-poly por parte** (receta de [ver: blender/modificadores §4], calibrada a arma):

| Orden | Modificador | Ajuste para arma |
|---|---|---|
| 1 | Mirror (si la parte es simétrica) | Solo en piezas simétricas; **cero mirror en UV de lo visible en FP** (§10) |
| 2 | Boolean(s) | Detalle mecánico: puerto de eyección, agujeros de pin, ranuras del riel Picatinny, aligeramientos. Solver **Manifold** si todo es manifold, si no **Exact** |
| 3 | Bevel | `width ~0.3–0.6 mm`, `segments 2`, Limit Method **Angle ~30°** (o **Weight** con `bevel_weight_edge`), Clamp Overlap ON |
| 4 | Weighted Normal | `Face Area`, Keep Sharp ON |
| 5 | Triangulate | Pin to Last |

```python
import bpy, math
part = bpy.context.object
bv = part.modifiers.new("Bevel", 'BEVEL')
bv.width = 0.0004                 # 0.4 mm — calibrar al tamaño en pantalla, no al real
bv.segments = 2
bv.limit_method = 'ANGLE'
bv.angle_limit = math.radians(30)
bv.use_clamp_overlap = True
wn = part.modifiers.new("WeightedNormal", 'WEIGHTED_NORMAL')
wn.mode = 'FACE_AREA'; wn.keep_sharp = True
part.modifiers.new("Triangulate", 'TRIANGULATE')
```

Reglas hard-surface que aplican directo (no repetir teoría — [ver: modelado/hard-surface]):
- **Todo borde visible lleva bevel**; calibrar el ancho al tamaño en PANTALLA a distancia de cámara FP, no al tamaño real (el bake/normal comprime lo sutil).
- **Booleans no-destructivos** hasta aprobar el diseño; el cortador atraviesa de verdad (nada de caras coplanares) [ver: blender/modificadores §3].
- Riel Picatinho / ranuras repetidas: **Array** (5.x: Shape Line, Realize Instances + Merge) → Boolean, o Boolean con el cortador ya arrayado [ver: blender/modificadores §3].
- **Detalle terciario que no da silueta** (tornillos, texto, panel lines finas) → decal/floater o normal map, no geometría [ver: modelado/hard-surface §7].
- Verificar shading con matcap girando la pieza cada sesión; el reflejo delata la topología, no el wireframe [ver: modelado/hard-surface §1].

## 6. Sights: la mira recta, centrada y al eje (crítico en FP)

El sight alignment es GEOMETRÍA, no animación [ver: modelado/props-armas §7.1]. Al apuntar (ADS) el engine alinea la línea alza→guion con el centro de cámara; una mira torcida o descentrada del blockout no se arregla animando.

1. **Alza y guion (front/rear sight) sobre el plano central del arma**: si el forward es +Y y el up +Z, el plano de simetría es X=0. Los dos elementos de mira deben tener su centro en X=0.
2. **Verificarlo**: añadir un Empty (Plain Axes) o una línea temporal en X=0 a lo largo de +Y; el punto de mira, el fondo del alza y el centro del cañón deben quedar sobre esa línea vista de frente (mirar por −Y, vista Front `Numpad 1`).
3. **Altura correcta**: alza y guion a la misma altura de línea de mira (sight height) — que al mirar por encima del alza, el guion quede centrado en la escotadura (sight picture limpio).
4. **Nada tapa la mira alineada**: ni riel, ni óptica montada por defecto, deben cortar el sight picture.
5. Si el arma lleva **óptica** montada en FP, esa óptica pasa a ser lo MÁS cercano a cámara → hereda presupuesto de hero, y su retícula/centro también van sobre X=0.

## 7. Presupuesto de detalle por cámara (FP vs TP)

Dónde van los polígonos [ver: modelado/props-armas §5, §7.1]:

| Zona | First-person viewmodel | Third-person / world model |
|---|---|---|
| Mitad que ve la cámara (trasera-superior del lado de cámara: **gatillo, sights, boca del cañón, lado de expulsión**) | Máxima densidad; loops y bevels aquí | Normal |
| Cara exterior opuesta / culata completa / parte baja | Mínimo; nunca se ve en FP → mirror y baja densidad OK | Se ve → densidad media |
| Silueta | Se evalúa **a 45°** (ángulo del viewmodel) | De perfil y 3/4 |

- Los engines renderizan el viewmodel con **FOV separado**; revisar SIEMPRE en engine con ese FOV, no en el viewport [ver: modelado/props-armas §7.1; pipeline/arte-a-unity].
- Si el proyecto usa **una sola malla para FP y TP**, presupuestar para el peor caso (FP) y bajar detalle con LODs; si son mallas distintas, el world model es una reducción del viewmodel.

## 8. Attachment points / sockets (empties nombrados)

Puntos de anclaje para accesorios como **Empties** hijos del arma → llegan a Unity como GameObjects vacíos con su transform, listos como attach points [ver: blender/import-export]. Estandarizados ENTRE armas de la familia (misma escala/orientación) si el arma es modular [ver: modelado/props-armas §7.3].

Sockets típicos: `SOCKET_Optic` (riel superior), `SOCKET_Muzzle` (rosca del cañón, para silenciador/bocacha), `SOCKET_Mag` (pozo del cargador), `SOCKET_Grip`/`SOCKET_Light` (rieles laterales/inferior), `SOCKET_Sling` (correa), `SOCKET_Muzzle_Flash`/`SOCKET_Shell_Eject` (VFX/casquillos).

- **Add**: `Add ▸ Empty ▸ Plain Axes` (`bpy.ops.object.empty_add(type='PLAIN_AXES')`). El `radius` es solo display, no viaja a Unity (el socket es transform puro).
- **Orientación importa**: rotar el Empty para que un eje conocido apunte en la dirección de montaje (p.ej. +Y hacia la boca en `SOCKET_Muzzle`) — Unity hereda esa rotación; el accesorio se alinea a ella. Fijar la convención en la spec del proyecto.
- **Parentar** al root: seleccionar socket, luego el root, `Ctrl-P ▸ Object (Keep Transform)` → `bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)`.
- Prefijo consistente (`SOCKET_`) — Unity no lo exige, es convención de equipo [ver: blender/import-export].

```python
import bpy
def socket(name, loc, parent, rot=(0,0,0)):
    bpy.ops.object.empty_add(type='PLAIN_AXES', radius=0.02, location=loc, rotation=rot)
    e = bpy.context.object; e.name = name
    e.parent = parent
    e.matrix_parent_inverse = parent.matrix_world.inverted()   # conserva la posicion visual
    return e
root = bpy.data.objects['WPN_Rifle']
socket('SOCKET_Optic',  (0.0, 0.05, 0.09),  root)              # coords = placeholders,
socket('SOCKET_Muzzle', (0.0, 0.42, 0.02),  root, (0,0,0))     # medir en el modelo real
socket('SOCKET_Mag',    (0.0, 0.10, -0.06), root)
```

## 9. Jerarquía pensada para el rig/animación en Unity

Un root limpio con las partes como hijas — el animador y el engine dependen de esto [ver: blender/import-export; modelado/props-armas §7.2]:

```
WPN_Rifle            (Empty o el receiver; origen en el mundo, transform limpio)
├── Rifle_Receiver   (cuerpo fijo)
├── Rifle_Barrel
├── Rifle_Slide      (pivot en el eje de deslizamiento)
├── Rifle_Trigger    (pivot en el perno)
├── Rifle_Magazine   (pivot en el agarre)
├── Rifle_Sight_F / Rifle_Sight_R
├── SOCKET_Optic / SOCKET_Muzzle / SOCKET_Mag ...   (empties)
└── Rifle_COL        (colisión low-poly, si la spec la pide)
```

- **Un asset = un root** con nombre limpio y estable (`WPN_Rifle`, no `Cube.003`); el nombre es el contrato con Unity, no se renombra tras el primer import [ver: blender/import-export].
- Root con transform limpio (loc 0, rot 0, scale 1); cada parte conserva SU origen (el pivot del paso 4).
- Aplanar empties "organizativos" que no aporten transform útil — ensucian el prefab.
- Naming/jerarquía exactos → spec del proyecto [ver: pipeline/arte-a-unity].

## 10. Cierre game-ready y export (fases 5–9 comprimidas)

El detalle de cada punto vive en las bases; aquí el ORDEN. Checklist completo en [ver: modelado/props-armas §10].

1. **Low-poly**: dentro del presupuesto del §0; en mid-poly, el propio blockout refinado suele SER la base del low. Audita **vertex count**, no solo tris (cada UV split / hard edge / material duplica vértices) [ver: modelado/props-armas §5].
2. **UVs**: shells rectas, texel density uniforme (~±20%), split en cada hard edge. **Sin mirror en lo visible en FP** (receiver, sights, gatillo); mirror OK en cara oculta y parte baja [ver: modelado/props-armas §7.1]. Para partes espejadas, offset de UV +1 en U para no ensuciar el bake [ver: blender/modificadores §3].
3. **Bake** (solo si hay high-poly / hero): normal/AO/curvature high→low con cage, bakeado a 2× la resolución de entrega; revisar a la distancia REAL de juego, no a 400% [ver: modelado/high-to-low; modelado/props-armas §7].
4. **Shading**: `Shade Auto Smooth` (~30–45°) + Mark Sharp puntual; **hard edge = UV seam** en el mismo sitio [ver: blender/edicion-malla §5].
5. **Limpieza**: Merge by Distance, Delete Loose, Recalculate Outside, sin n-gons en export, triangular antes de espejear [ver: blender/edicion-malla §6].
6. **Transforms**: `Ctrl-A ▸ All Transforms` en cada objeto (root y partes) — salvo el contra-giro deliberado para matar el -89.98 [ver: blender/import-export]. Cuidado: aplicar escala mantiene cada pivot donde lo pusiste.
7. **Export FBX** con los settings de Unity 6 [ver: blender/import-export]: `apply_scale_options='FBX_SCALE_UNITS'` (File Scale 1), Forward −Z / Up Y, Smoothing **Face**, Add Leaf Bones OFF, Object Types `{EMPTY, MESH, ARMATURE}` (los sockets son EMPTY → tienen que ir incluidos). Un asset/familia por colección con Collection Exporter.
8. **QA de recorridos ANTES de dar por listo** (§11).

## 11. QA de recorridos (prueba de movimiento antes de entregar)

Mover cada parte por su recorrido completo y verificar sin clipping [ver: modelado/props-armas §7.2]:

- **Corredera/cerrojo atrás**: recorrido lineal completo sin clipping; con la corredera atrás, el puerto de eyección y la recámara quedan visibles y modelados.
- **Cargador**: extracción completa sin intersectar el arma ("pull-and-seat without intersection").
- **Gatillo/martillo/selector**: rotación en su perno sin atravesar el guardamonte.
- **Óptica/silenciador**: instanciar un accesorio en su socket y comprobar orientación/posición.
- Verificación por código sin ojos: mover la parte y medir bounding boxes / intersecciones, o render desde la cámara FP [ver: blender/blender-mcp-operativo]. La aprobación final es EN engine con el FOV del viewmodel [ver: pipeline/arte-a-unity].

## Reglas prácticas

1. Fija uso (FP/TP), presupuesto, high-poly sí/no, textura y modularidad ANTES de la primera primitiva (§0).
2. Modela el arma RECTA sobre un eje del mundo (cañón +Y, up +Z): alinea la mira y hace lineal el recorrido de la corredera en un solo eje.
3. Referencia hasta entender qué se mueve y sobre qué eje; blueprint escalado a medidas reales, no a la foto.
4. Escena en metros, 1 u = 1 m, modelar a tamaño real; maniquí del personaje al lado.
5. Blockout aprobado EN engine con el FOV del viewmodel antes de detallar; silueta evaluada a 45°.
6. Cada parte móvil = objeto separado (`P ▸ Selection`), origen en su eje mecánico real (Cursor to Selected → Origin to 3D Cursor).
7. Modela el interior que el movimiento revela: puerto de eyección, pozo del cargador, recámara.
8. Mid-poly por defecto en armas FP: Bevel (Angle ~30°, 2 seg, Clamp Overlap) → Weighted Normal (Face Area, Keep Sharp) → Triangulate (Pin to Last).
9. Booleans para detalle mecánico (puerto, pines, ranuras del riel); no-destructivos hasta aprobar; solver Manifold/Exact.
10. Ancho de bevel por tamaño EN PANTALLA a distancia FP, no por tamaño real.
11. Sights sobre el plano central (X=0), a la misma altura, sight picture limpio; verificarlo con una línea/empty en X=0.
12. Presupuesto de detalle en la mitad que ve la cámara FP (gatillo, sights, boca, lado de expulsión); cero mirror en UV de lo visible.
13. Sockets = Empties Plain Axes nombrados (`SOCKET_*`), orientados a la dirección de montaje, parentados al root con Keep Transform.
14. Jerarquía: un root limpio (`WPN_Rifle`) → partes hijas con su pivot + sockets; nombres estables (contrato con Unity).
15. `Ctrl-A ▸ All Transforms` antes de exportar; FBX con FBX_SCALE_UNITS, Smoothing Face, Add Leaf Bones OFF, Object Types incluye EMPTY.
16. QA de recorridos (mover cada parte a tope sin clipping) ANTES de declarar listo; aprobación final en engine.
17. Nada se aprueba en el viewport de Blender: escala, silueta y sight picture se validan en Unity con la cámara real.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Modelar el arma torcida respecto al eje del mundo | Alinear cañón a +Y desde el blockout: la mira se centra sola y la corredera se anima en un eje limpio (§2, §6) |
| Detallar antes de aprobar el blockout en engine | Gate de fase 2: proporción/silueta a 45° con el FOV del viewmodel en Unity primero |
| Corredera/cargador soldados al mesh, o sin interior detrás | Separar con `P`, pivot en el eje, modelar puerto de eyección/pozo visibles (§4, §11) |
| Pivot de la corredera en el centro del objeto | Cursor to Selected sobre el riel → Origin to 3D Cursor (§4) |
| Sights torcidos o descentrados que "se arreglan animando" | La mira es geometría: alza y guion sobre X=0, misma altura, desde el blockout (§6) |
| UVs espejadas en el lado de cámara del arma FP | Mirror solo en caras ocultas/parte baja; receiver/sights/gatillo con UV único, offset +1 en U para lo espejado (§10) |
| Aprobar el arma de perfil y verla rota en el viewmodel | Evaluarla a 45° y con el FOV del viewmodel en engine (§3, §7) |
| Bevels finos que hacen sparkle o desaparecen a distancia FP | Ancho por tamaño en pantalla; LOD que los elimina y vuelve a hard edges [ver: modelado/hard-surface] |
| Sockets olvidados en el export (Object Types sin EMPTY) | Incluir `'EMPTY'` en Object Types del FBX; verificar que llegan como GameObjects a Unity (§8, §10) |
| Renombrar partes/materiales tras el primer import a Unity | El nombre es el contrato: se congela; renombrar rompe MeshFilters y materiales del prefab [ver: blender/import-export] |
| Escala sin aplicar → bevels desiguales, pivots que saltan, escala 100 en Unity | `Ctrl-A ▸ All Transforms` por objeto antes de exportar; FBX_SCALE_UNITS (§10) |
| Boolean con cutter no manifold o caras coplanares | Cutter manifold, atravesar de verdad; solver Manifold si todo es manifold, si no Exact [ver: blender/modificadores §3] |
| Scopes/silenciadores que no encajan entre armas de la familia | Sockets estandarizados (escala/orientación/naming) en la spec de la familia (§8) |
| Dar por "listo" sin mover las partes | QA de recorridos: cada parte a tope sin clipping antes de entregar (§11) |
| Detalle terciario (tornillos, texto) modelado en geometría por todo el arma | Decal/floater/normal map para lo que no da silueta [ver: modelado/hard-surface §7] |

## Fuentes

Web (canónicas de weapon art y de la herramienta; ⚠️ ver nota de verificación abajo):

- **3D Weapon Art for Games** — Nasty Rodent (weapon art de Squad / Ready or Not) — presupuestos FP (low 8k–20k tris, pistola 6k–10k, rifle hero 12k–18k; high 60k–100k), texturas 2K–4K, texel density 512–1024 px/m, bake a 2×, silueta a 45°, densidad en gatillo/sights/boca, sin mirror en lo visible, recorridos sin clipping (rack, pull-and-seat), modularidad como sistema de assets.
- **FPS Weapon Creation: How to Match AAA Standards** — Room 8 Studio — pipeline en fases, referencias como fase crítica, UVs rectas, custom normals, decenas de material IDs en bakes AAA.
- **How to Model and Texture a Realistic AK-74** — Oriol Salom (80.lv) — breakdown real: ~1000 referencias, workflow mid-poly→high→low, texel density uniforme (~±20%) entre partes.
- **First Person Rendering** — Epic Games (docs Unreal) — el viewmodel se renderiza con FOV propio; clipping con near plane; representación en mundo para sombras (el principio generaliza a Unity).
- **Blender 5.2 LTS Manual** — docs.blender.org — operadores citados: `object.empty_add`, `object.origin_set`, `view3d.snap_cursor_to_selected`, `mesh.separate`, `object.parent_set` (keep_transform), Bevel/Weighted Normal/Boolean/Array/Triangulate, Shade Auto Smooth, export FBX. **⚠️ docs.blender.org sigue en 403 a WebFetch y WebSearch sigue agotado (200/200) esta sesión de auditoría** — pero SÍ se verificaron 3 operadores dudosos contra el código fuente real de Blender en GitHub (`object_transform.cc`, `object_add.cc`, `object_relations.cc`, rama `main`) el 20-jul-2026:
  - `object.origin_set(type=...)` — el enum RNA real es **`ORIGIN_CURSOR`**, NO `ORIGIN_TO_3D_CURSOR` como decía una versión anterior de esta receta. **Corregido** (§2, §4).
  - El operador de `Add ▸ Image ▸ Reference` NO es `object.load_reference_image` (no existe) — es **`object.empty_image_add(background=False)`**; `background=True` da el modo "Background Image". **Corregido** (§1).
  - `object.parent_set(type='OBJECT', keep_transform=True)` — confirmado correcto tal cual (RNA real: enum `"OBJECT"` + booleano `keep_transform`).
  - Resto de operadores del stack (Bevel/Weighted Normal/Triangulate, `mesh.separate`, `view3d.snap_cursor_to_selected`, `empty_add(type='PLAIN_AXES')`, export FBX `FBX_SCALE_UNITS`) **no re-verificados en vivo esta sesión** — alta confianza por ser API estable y muy usada, pero confirmar en Blender vivo antes de automatizar en producción. Las coords de socket del snippet §8 siguen siendo placeholders inventados a propósito.

Bases sintetizadas (el QUÉ/POR QUÉ que esta receta no repite):

- [ver: modelado/props-armas] — armas FP/TP, partes móviles y pivots, attachment points, checklist game-ready, presupuesto por distancia de cámara.
- [ver: modelado/hard-surface] — bevels, weighted normals, booleans, decals, high-poly de bake.
- [ver: blender/modificadores] — stack mid-poly (Bevel+WN+Triangulate), Boolean (solvers 5.x), Array (Legacy vs nuevo 5.0), orden del stack.
- [ver: blender/edicion-malla] — separate, cursor/snap, normales/Shade Auto Smooth (4.1+), limpieza de malla, Set Origin.
- [ver: blender/import-export] — FBX a Unity 6 (escala FBX_SCALE_UNITS, ejes, -89.98), sockets como Empties, naming/jerarquía, colliders, LODs.
- Asumidas: [ver: modelado/blueprints-referencias], [ver: modelado/presupuestos-poligonos], [ver: modelado/high-to-low], [ver: blender/materiales-preview], [ver: blender/blender-mcp-operativo], [ver: pipeline/arte-a-unity].
