# El Graph Editor en la práctica (Blender 5.2)

> **Cuando cargar este archivo:** siempre que ejecutes animación de keyframes DENTRO de Blender 5.2 — leer/editar F-Curves en el Graph Editor, elegir interpolación (Constant/Linear/Bézier) y tipo de handle (Automatic/Auto Clamped/Vector/Aligned/Free), moldear ease/overshoot/settle con tangentes, bloquear en stepped y pasar a spline, ciclar con el modificador Cycles, meter vida con Noise, limpiar curvas (Clean/Decimate/Smooth/Euler filter), y **exportar clips limpios a Unity 6** entendiendo qué de esas curvas sobrevive al sampling del FBX. Es el CÓMO operativo: qué operador `bpy.ops.graph.*`, qué setting, qué atajo. La **teoría** (qué es un buen timing/spacing, un ciclo, un ataque) NO se repite aquí: vive en [ver: animacion3d/keyframes-curvas] (la base directa de este archivo) y sus vecinos. Pensado para un agente operando Blender por MCP o `blender -b` headless.

Stack de referencia: **Blender 5.2 LTS** + **Unity 6 (Mecanim)**. Operadores, enums y propiedades **verificados contra `docs.blender.org/manual/en/latest` y `/api/current`** (páginas *Last updated 2026-07-20*), no contra un binario local. La funcionalidad descrita es estable en 5.x; los datos dependientes de versión van marcados. ⚠️ **El sistema de animación cambió en 4.4** (Slotted/Layered Actions, "Baklava"): desde 4.4 toda Action es *layered* y `action.fcurves` **ya no existe** — abajo, §1 y §10, la API correcta. Ignorar tutoriales pre-4.4 que usan `action.fcurves`: se rompen en 5.2.

Cómo encaja en la base: la CRAFT de curvas (leer pendientes, ease asimétrico, moving holds, spacing por valor) está en [ver: animacion3d/keyframes-curvas]; los principios de posing en [ver: animacion3d/principios-produccion]; ciclos en [ver: animacion3d/ciclos-locomocion]; combate en [ver: animacion3d/animacion-combate]; overlap/settle en [ver: animacion3d/movimiento-secundario]; mocap denso en [ver: animacion3d/mocap-librerias]. El consumo en motor en [ver: unity/animacion-unity]. Vecinos en esta carpeta: [ver: sistema-animacion] · [ver: actions-organizacion] · [ver: nla-editor] · [ver: bake-animacion] · [ver: export-clips-unity] · [ver: animacion-blender-operativo]. Ejecutar bpy/MCP: [ver: blender/bpy-scripting] · [ver: blender/blender-mcp-operativo].

---

## 1. Dónde vive la curva en 5.2 (Slotted Actions, lo justo)

El Graph Editor no anima nada por sí mismo: edita las **F-Curves de una Action**. En 5.2 la Action es el contenedor de animación de un data-block, y su estructura cambió:

| Nivel | Qué es | Estado en 5.2 |
|---|---|---|
| **Action** | Data-block contenedor. Desde 4.4 toda Action es *layered* (`is_action_legacy` solo True en actions vacías) | Se puede *append/link* entre .blend |
| **Slot** | Sub-conjunto de la Action con su propio set de F-Curves; un data-block usa `action` + `action_slot`. Una Action puede tener N slots (objeto + material + luz en la misma Action) | **Expuesto en UI** (Action Editor: icono de tipo junto al nombre del slot) |
| **Layer / Strip** | Capas y strips internos donde viven los channelbags | **Solo Python API** — no expuesto en UI todavía (preparación para animación por capas futura) |
| **Channelbag** | El set de F-Curves de un `(strip, slot)`. Se obtiene con `strip.channelbag(slot)` | La ruta correcta a `.fcurves` en 5.2 |

- Para el trabajo diario en el Graph Editor esto es transparente: seleccionas el objeto/hueso y ves sus curvas. Importa cuando **scriptas**: `action.fcurves` desapareció; ruta correcta en §10.
- Organización de Actions/slots (una Action por clip, naming, Fake User para que no se borren) → detalle en [ver: actions-organizacion] y [ver: sistema-animacion]. El NLA (montar/mezclar strips) → [ver: nla-editor].

---

## 2. Anatomía del Graph Editor y overlays

Dos regiones: **channel region** (izquierda, lista de canales/F-Curves) y **main region** (curvas en plano tiempo×valor). El **Dopesheet** es el mismo dato para *timing* (solo CUÁNDO hay key); el Graph Editor es para *cómo se mueve* (la forma). Modelo mental y lectura de pendientes = velocidad: [ver: animacion3d/keyframes-curvas §3].

Overlays y filtros que evitan el "plato de espagueti" (menú **View** y controles del header — verificado):

| Overlay / control | Efecto | Cuándo |
|---|---|---|
| **Normalize** (View ‣ Normalize) | Escala cada curva a un rango común para que canales de magnitudes distintas (rotación en rad vs loc en m) se lean juntos | Comparar timing entre canales de escalas dispares |
| **Auto Normalization** | Recalcula la normalización en cada edición | Dejar ON al usar Normalize mientras editas |
| **Show Only Selected** (control de header) | Solo muestra curvas de los objetos/huesos seleccionados | Aislar el canal culpable — el reflejo #1 al diagnosticar |
| **Only Selected Keyframes Handles** (View) | Solo dibuja los handles de las keys seleccionadas | Reduce ruido visual en curvas densas |
| **Show Handles** `Ctrl-H` | Toggle de todos los handles | Ver la forma limpia sin puntos |
| **Show Sliders** / **Show Cursor** | Sliders de valor en la lista / línea horizontal del 2D Cursor (pivote de rotar/escalar keys) | Editar valores numéricos exactos |
| Filtros de canal (Only Show Errors, Filter by Collection/Type) | Filtra qué canales lista | Rigs con cientos de canales |

- **2D Cursor**: intersección Playhead × línea azul horizontal; sirve de pivote para rotar/escalar bloques de keys. Se mueve con `Shift-RMB`.
- **Selección de columnas** `K` (Columns on Selected Keys): selecciona todas las keys en los frames de las ya seleccionadas — clave para retimear una pose completa a la vez.

---

## 3. Interpolación entre keys (Constant / Linear / Bézier + easings)

Se fija por segmento (de la key activa a la siguiente). Menú **Key ‣ Interpolation Mode**, atajo **`T`**; operador `bpy.ops.graph.interpolation_type(type=...)`. Traducción a feel en [ver: animacion3d/keyframes-curvas §2].

| Modo | Enum | Forma | Uso |
|---|---|---|---|
| **Constant** | `CONSTANT` | Escalón: mantiene el valor hasta la siguiente key | **Blocking** (§6), snaps, visibilidad, holds duros |
| **Linear** | `LINEAR` | Recta; sin cambio brusco de valor pero sí de velocidad | Mecánica, LEDs, tramos que no quieres que el auto redondee |
| **Bézier** | `BEZIER` | Suave en valor Y en velocidad (default) | Todo lo orgánico: cuerpos, cámara, follow-through |

- **Easing (by strength)** y **Dynamic Effects** son sub-tipos que aceleran/desaceleran con ecuaciones (Sine, Quad, Cubic…, y Back/Bounce/Elastic). Menú **Key ‣ Easing Type**, atajo **`Ctrl-E`**; `bpy.ops.graph.easing_type`. Dirección: **Ease In / Out / In-Out** (`Automatic Easing` elige la común: In para easings, Out para dynamic effects).
  - **Back**: la key se aleja del objetivo antes de dispararse (In) o lo sobrepasa y vuelve (Out) — overshoot con una sola key. Parámetro *Back* = tamaño/dirección.
  - **Bounce**: rebota con decaimiento exponencial (pelota que cae). **Elastic**: sobrepasa, rebota bajo, vuelve a sobrepasar con intensidad decreciente. Params *Amplitude* / *Period*.
- Para **personaje** casi siempre se moldea a mano con handles (§4/5), no con estas ecuaciones; los easings son útiles para UI/props/cámara.
- Nota: propiedades de valor **discreto** (enteros, enums) siempre dibujan escalón, elijas lo que elijas.

**Extrapolación** (qué hace la curva ANTES de la 1ª key / DESPUÉS de la última): `bpy.ops.graph.extrapolation_type(type=...)` → `CONSTANT` (aplana), `LINEAR` (continúa la pendiente), `MAKE_CYCLIC` (añade un modificador Cycles, §7), `CLEAR_CYCLIC`.

---

## 4. Handles: los cinco tipos y el suavizado

Con interpolación Bézier, cada key tiene handle izquierdo y derecho. Menú **Key ‣ Handle Type**, atajo **`V`**; `bpy.ops.graph.handle_type(type=...)`. No hace falta cambiar el tipo antes de arrastrar un auto-handle: arrastrarlo ya lo convierte. Equivalencias Unity/Maya en [ver: animacion3d/keyframes-curvas §3].

| Handle | Enum | Comportamiento | Uso |
|---|---|---|---|
| **Automatic** | `AUTO` | Auto, curva suave; puede sobrepasar/oscilar | Punto de partida, pero propenso a overshoot no deseado |
| **Auto Clamped** | `AUTO_CLAMPED` | Auto **clampeado**: evita overshoots y S-shapes entre keys | **Default sano** para curvas orgánicas |
| **Vector** | `VECTOR` | Auto apuntando a la key vecina → segmento recto (como linear) | Mezclar tramos rectos dentro de una curva bézier |
| **Aligned** | `ALIGNED` | Manual, in/out **colineales** (siempre opuestos) → suave en el punto | Moldear ease a mano manteniendo continuidad |
| **Free** | `FREE` | Manual, in/out **independientes** → cambio de dirección brusco | Cambios de dirección con velocidad distinta a cada lado |

- **Handle Smoothing** (propiedad de la F-Curve, aplica a Automatic/Auto Clamped): **None** (solo mira keys adyacentes; simple y predecible pero mete kinks) vs **Continuous Acceleration** (resuelve un sistema para minimizar saltos de aceleración; curvas mucho más suaves, pero un cambio de valor **propaga** su efecto a lo largo de la curva; la propagación la cortan keys con handle Free/Aligned/Vector o extremos Auto Clamped). Recomendación oficial: **Auto Clamped por defecto**, Automatic solo donde quieras ese comportamiento. Continuous Acceleration conviene a *limited animation* (pocas keys, poco pulido); en animación de alto key-rate muy pulida, la propagación estorba más de lo que suma.
- Regla: **empieza en Auto Clamped, rompe a Aligned/Free solo donde el movimiento lo pida** (mismo criterio que la base). Romper todo por defecto = curvas imposibles de mantener.

**Ops de handle rápidas** (Key ‣ Snap): **Flatten Handles** (handles horizontales — para holds/extremos, pico limpio sin overshoot), **Equalize Handles** (misma longitud, lado L/R/both).

---

## 5. Meter timing/spacing/ease/overshoot EN Blender

Traducción operativa de [ver: animacion3d/keyframes-curvas §4–5]. **Primero timing (mover en X, mejor en Dopesheet), luego forma (mover en Y / girar handles, en Graph Editor).**

| Quieres… | En el Graph Editor haces… |
|---|---|
| **Ease in** (asienta en la pose) | Handle de ENTRADA plano/horizontal en la key destino (Flatten Handles o bajar el handle out del vecino) |
| **Ease out** (arranca lento) | Handle de SALIDA plano en la key origen |
| **Pasar a máx velocidad** (breakdown en mitad de arco) | Handles empinados a ambos lados (Aligned, no planos) |
| **Ease asimétrico** (carácter, peso) | Handle in ≠ handle out: rompe a **Free** y da longitudes distintas. Golpe que pega = salida casi vertical hacia el frame de impacto |
| **Overshoot + settle** | Key en la pose destino + key un pelín MÁS ALLÁ del valor + key de vuelta; tangentes: entrada rápida al overshoot, salida suave al settle. ⚠️ **Auto Clamped mata el overshoot a propósito** → hay que romper a Free/Aligned y empujar el handle |
| **Overlap** (padre→hijo) | Desfasar 2–4 frames las keys de los canales hijos respecto al padre (mover keys en X en Dopesheet) |
| **Moving hold** (no congelar) | En vez de dos keys idénticas, la 2ª deriva mínimamente: pendiente casi imperceptible, no un tramo plano largo |

- **Spacing = cambio de VALOR por frame (pendiente)**, no densidad de keys. Da contraste; evita el spacing parejo robótico. La pendiente ES la velocidad.
- **Snap a frames enteros**: mantén keys en enteros salvo intención (Key ‣ Snap ‣ ... a Nearest Frame). Keys en `12.4` ensucian el export y complican el retime.

---

## 6. Blocking → spline (stepped primero)

Método pose-a-pose llevado a Blender. Se bloquea el TIMING en stepped antes de tocar interpolación ([ver: animacion3d/keyframes-curvas §6], [ver: animacion3d/principios-produccion]).

| Fase | Interpolación | Cómo en Blender |
|---|---|---|
| **1. Blocking** | `CONSTANT` en TODO | Keyea completo (Key All) en cada pose; pon toda la Action en Constant (`interpolation_type(type='CONSTANT')` sobre todas las keys). Ves SOLO tus poses y su timing |
| **2. Breakdowns** | Aún `CONSTANT` | Poses intermedias que definen el arco/camino |
| **3. Spline** | `BEZIER` | Convierte todo a Bézier — el software interpola; aparece el movimiento continuo |
| **4. Polish** | Bézier + handles a mano | Arreglar el caos del auto-spline: arcos, ease, overshoot, overlap, foot slide |

- **La conversión a spline SIEMPRE ensucia** (overshoots, arcos rotos, pies deslizando). La fase 4 es el trabajo real; presupuéstala.
- Preferencia útil al bloquear: **Preferences ‣ Animation ‣ Default interpolation = Constant** para que las keys nuevas nazcan en stepped (evita convertir después). Encaja con las 3 fases del ataque wind-up/active/recovery: bloquea en stepped, valida el gameplay, y recién pule [ver: animacion3d/animacion-combate].

---

## 7. F-Curve Modifiers: efecto no destructivo sobre la curva

Panel *Sidebar ‣ Modifiers* o menú **Channel ‣ Add F-Curve Modifier** (`bpy.ops.graph.fmodifier_add`). Se evalúan **de arriba abajo**; `Influence` mezcla curva original↔modificada; `Restrict Frame Range` + `Blend In/Out` acotan el efecto. En vivo y editables.

| Modificador | Qué hace | Settings clave | Cuándo |
|---|---|---|---|
| **Cycles** | Repite la curva fuera del rango de keys | `mode_before`/`mode_after` (`NONE`/`REPEAT`/`REPEAT_OFFSET`/`MIRROR`), `cycles_before`/`cycles_after` (0 = infinito) | **Loops**: idle, walk. `REPEAT_OFFSET` para locomoción que avanza (loc sube en escalera); `MIRROR` para vaivenes |
| **Noise** | Ruido procedural sobre la curva | `Blend Type` (Replace [-0.5,0.5] / Add / Subtract / Multiply), `Scale` (densidad), `Strength` (amplitud), `Offset`, `Phase` (seed), `Depth`+`Lacunarity`+`Roughness` (detalle fractal) | Vida sin keyear: **camera shake**, respiración, handheld, temblor de idle |
| **Limits** | Recorta tiempo y valor | Min/Max **X** (recorta antes/después con extrapolación Constant), Min/Max **Y** (clampa valores) | Impedir que un canal pase de un tope (una tapa que no cruza su marco) |
| **Stepped Interpolation** | Muestrea cada N frames y sostiene | `Step Size`, `Offset`, `Start/End Frame` | Look **stop-motion / 12fps** sobre una animación suave, sin borrar keys |
| **Generator** | Función polinómica (recta, parábola…) | `Mode` (Expanded/Factorized), `Order`, constantes; `Additive` | Movimiento matemático (rampa infinita) |
| **Built-in Function** | Sine/Cosine/Tangent/Sqrt/Ln/Normalized Sine | `Amplitude`, `Phase Multiplier/Offset`, `Value Offset`, `Additive` | Oscilación pura (péndulo, flotar) |
| **Envelope** | Reforma la curva entre dos bordes con control points | Reference, Min/Max, puntos por frame | Escalar amplitud a lo largo del tiempo |
| **Smooth (Gaussian)** | Suaviza (mismo algoritmo que el operador Smooth) | `Sigma`, `Filter Width` | Bajar detalle/ruido de forma no destructiva |

- ⚠️ **Cycles y Smooth (Gaussian) deben ser el PRIMER modificador** y son **mutuamente incompatibles** (necesitan saber dónde están las keys exactas; otro modificador antes lo impide).
- **Trivially Cyclic**: si ambos extremos son `REPEAT` o `REPEAT_OFFSET` sin otros cambios, Blender lo reconoce como ciclo infinito y ajusta los **handles bézier automáticos** para transición suave entre repeticiones. Activa **Cycle-Aware Keying** (header del Dopesheet/Graph) para que las keys nuevas respeten el ciclo. Detalle de ciclos en [ver: animacion3d/ciclos-locomocion].
- ⚠️ **Los modificadores NO se exportan como tales** (Unity no los importa). Qué sobrevive al FBX → §9.

---

## 8. Limpieza de curvas

Curvas sucias = animación sucia + clips más pesados. Origen típico: sobre-keyado a mano y **mocap** (key por frame en cada canal). Todo bajo el menú **Key ‣ Density / Smooth / Snap** o su operador. Criterio ("menos keys mejor puestas", jitter, gimbal) en [ver: animacion3d/keyframes-curvas §7].

| Problema | Operador | Settings | Nota |
|---|---|---|---|
| **Keys redundantes** (curva ya suave con 3–4) | **Clean Keyframes** `graph.clean(threshold=0.001, channels=False)` | `channels=True` borra además canales vacíos | Quita keys cuyo borrado no cambia la forma bajo el umbral |
| **Demasiadas keys** (mocap/sobre-key) | **Decimate** `graph.decimate(mode, factor)` | `mode='RATIO'` (fracción a conservar, def 0.333) o `mode='ERROR'` (Allowed Change: cuánto puede desviarse) | La forma editable con el mínimo de keys |
| **Jitter / ruido** | **Smooth (Gaussian)** `graph.gaussian_smooth` | `Sigma` (forma de la campana), `Filter Width` (cuántas keys mira) | Preserva mejor que el legacy. **Butterworth Smooth** `graph.butterworth_smooth` preserva picos (ideal para mocap: `Cutoff Frequency`, `Filter order`, `Samples per Frame`). **Smooth (Legacy)** `graph.smooth` es muy agresivo |
| **Flip Euler** (359°→0°) | **Euler Filter** `graph.euler_filter` (Channel ‣ Clean Channels ‣ Discontinuity/Euler Filter) | — | Arregla saltos/volteos en curvas de Euler Rotation por clipping. Preferir cuaternión donde se pueda |
| **Necesitas keys reales por frame** | **Bake Keyframes** `graph.bake_keys` (Key ‣ Density) | Rango | Añade key en cada frame entre las seleccionadas — hornea la forma (incl. modificadores) a keys editables |
| **Densidad ↔ muestras** | `graph.keys_to_samples` / `graph.samples_to_keys` | — | Convierte F-Curve de keys bézier a *samples* baked y viceversa |

- **Smooth suaviza pero NO borra keys**; para reducir cantidad usa Clean o Decimate. Bake Keyframes es lo contrario: densifica a per-frame (útil antes de aplanar un modificador a keys).

---

## 9. La trampa del export: Unity NO importa tus curvas bézier

La distinción de producción más importante ([ver: animacion3d/keyframes-curvas §9]): **tú editas curvas bézier continuas; el FBX viaja como muestras por frame, y Unity encima aplica su propia reducción.** Nada de tu bézier fino llega intacto por defecto.

**Qué pasa al exportar (Blender, `bake_anim`):** el exporter FBX **samplea el valor EVALUADO** de cada propiedad animada a intervalo `bake_anim_step` (default `1.0` = cada frame). Consecuencias:
- Tus handles/tangentes se convierten en **una muestra por frame** — la curva bézier deja de existir como tal.
- Como samplea el valor *evaluado*, el efecto de **Noise/Cycles DENTRO del rango horneado sí queda capturado** como muestras… PERO el rango exportado es el rango de keyframes de la Action (con **All Actions**: el start/end de cada Action). Un **Cycles que repite MÁS ALLÁ de la última key NO se captura** pasado ese punto. Para un loop limpio: hornea el ciclo a keys reales (Bake Keyframes / `nla.bake`) cubriendo el rango completo, **o** exporta exactamente UN ciclo y activa **Loop Time** en Unity.

**Qué pasa al importar (Unity, verificado en [ver: unity/animacion-unity] y [ver: animacion3d/keyframes-curvas §9]):**
- **Anim. Compression**: `Off` (todo) / **Keyframe Reduction** (default sano, borra keys redundantes por umbral) / **Optimal**.
- **Rotation Error** (grados) / **Position/Scale Error** (%): baja el umbral si aparece patinaje/pérdida de detalle; súbelo si el clip pesa.
- **Resample Curves** (ON): convierte Euler→cuaternión con una key por frame.
- Los clips importados son **read-only**: editar = volver a Blender o copiar keys a un clip nuevo.

**Implicación operativa:** un ease sutil moldeado con handles puede **desaparecer** bajo el Keyframe Reduction de Unity. **Verifica el clip YA importado en el motor**, no solo en el Graph Editor. Setup del FBX y del importer, model@anim, avatar y naming → [ver: export-clips-unity]; horneado profundo (IK/constraints/NLA a keys) → [ver: bake-animacion]; pipeline arte→Unity → [ver: pipeline/arte-a-unity], [ver: blender/import-export].

### Ajustes de export relevantes (FBX)

En 5.2 el **import** usa el nuevo add-on FBX (C++); el **export** sigue por el add-on **legacy** (`bpy.ops.export_scene.fbx`). Sección **Bake Animation** (labels UI → parámetro):

| Setting UI | Parámetro | Para Unity |
|---|---|---|
| Bake Animation | `bake_anim=True` | ON |
| Key All Bones | `bake_anim_use_all_bones=True` | ON (evita huesos sin key) |
| NLA Strips | `bake_anim_use_nla_strips` | Cada strip NLA → un take |
| **All Actions** | `bake_anim_use_all_actions` | **True** = cada Action → un take (rango = sus keyframes); **False** = solo la Action asignada (patrón *un FBX por clip*) |
| Force Start/End Keying | `bake_anim_force_startend_keying=True` | ON (key en los extremos del rango) |
| Sampling Rate | `bake_anim_step=1.0` | 1 muestra/frame |
| Simplify | `bake_anim_simplify_factor=1.0` | **0.0** para no simplificar y dejar que Unity reduzca (o >0 para adelgazar en Blender) |
| Only Deform Bones | `use_armature_deform_only=True` | Exporta solo huesos de deform |
| Add Leaf Bones | `add_leaf_bones=True` | **False** para Unity (evita huesos `_end` basura) |

---

## 10. Snippets bpy (headless / MCP)

⚠️ **API 5.2**: `action.fcurves` NO existe. Ruta correcta a las F-Curves de un data-block:

```python
import bpy

def get_fcurves(obj):
    """F-Curves de la slot activa del data-block en 5.2 (layered actions)."""
    adt = obj.animation_data
    slot = adt.action_slot                      # slot asignado a este objeto
    strip = adt.action.layers[0].strips[0]      # capa/strip base
    return strip.channelbag(slot).fcurves       # ActionChannelbag.fcurves
```

**Insertar keys** (crea Action+slot layered automáticamente) y fijarles interpolación stepped para blocking:

```python
ob = bpy.context.object
ob.keyframe_insert(data_path="location", frame=1)     # o pose_bone.keyframe_insert(...)
ob.keyframe_insert(data_path="location", frame=12)
for fc in get_fcurves(ob):
    for kp in fc.keyframe_points:
        kp.interpolation = 'CONSTANT'                 # blocking; 'BEZIER' al pasar a spline
    fc.update()
```

**Ciclar una animación** (modificador Cycles, debe ser el 1º):

```python
for fc in get_fcurves(ob):
    m = fc.modifiers.new(type='CYCLES')
    m.mode_before = 'REPEAT'
    m.mode_after  = 'REPEAT_OFFSET'   # locomoción que avanza
```

**Hornear constraints/IK a keys FK planas** antes de exportar (`bpy.ops.nla.bake`, en Pose Mode):

```python
bpy.ops.nla.bake(
    frame_start=1, frame_end=48, step=1,
    only_selected=True,        # solo huesos seleccionados
    visual_keying=True,        # captura el resultado de constraints/IK
    clear_constraints=False,   # True si quieres soltar los constraints tras hornear
    use_current_action=True,   # Overwrite Current Action
    clean_curves=False,
    bake_types={'POSE'},       # o {'OBJECT'}
)
```

**Exportar un clip a Unity** (un FBX = un clip; naming model@anim y avatar en [ver: export-clips-unity]):

```python
bpy.ops.export_scene.fbx(
    filepath="/out/Hero@Run.fbx",
    use_selection=True, object_types={'ARMATURE', 'MESH'},
    add_leaf_bones=False, use_armature_deform_only=True,
    primary_bone_axis='Y', secondary_bone_axis='X',
    bake_anim=True, bake_anim_use_all_actions=False,
    bake_anim_use_nla_strips=False, bake_anim_use_all_bones=True,
    bake_anim_force_startend_keying=True,
    bake_anim_step=1.0, bake_anim_simplify_factor=0.0,
)
```

Descubrir operadores/enums exactos desde dentro de Blender: `bpy.ops.graph.*` (ver §2–8), tooltips e Info editor [ver: blender/bpy-scripting §descubrir API].

---

## Reglas prácticas

- [ ] **API 5.2**: nunca `action.fcurves` (no existe). Usa `strip.channelbag(slot).fcurves`; para insertar, `obj.keyframe_insert(...)`.
- [ ] Diagnostica **por canal**: activa **Show Only Selected** y aísla la curva culpable antes de tocar nada.
- [ ] Default de handles: **Auto Clamped**; rompe a Aligned/Free solo donde el movimiento lo pida. Handle Smoothing en Auto Clamped por defecto.
- [ ] Elige interpolación a conciencia con `T`: **Constant** para blocking, **Linear** para mecánica, **Bézier** para lo orgánico. No aceptes el default a ciegas.
- [ ] **Bloquea en `CONSTANT`** y valida que la acción se lee saltando de pose a pose; recién entonces pasa a `BEZIER`. Presupuesta el polish post-spline.
- [ ] **La pendiente es la velocidad**; **spacing = cambio de valor por frame**, no densidad de keys. Da contraste, evita lo parejo.
- [ ] Ease = handle plano entrando (asienta) / saliendo (arranca lento); reparte asimétrico (Free) para carácter.
- [ ] **Overshoot/settle**: key extra más allá + vuelta, y rompe el Auto Clamped (que lo mata). Holds de personaje = **moving hold**, nunca dos keys idénticas planas.
- [ ] **Overlap**: desfasa 2–4 frames las keys de los canales hijos.
- [ ] Mantén keys en **frames enteros** (Snap ‣ a Nearest Frame) salvo intención.
- [ ] Ciclos con **Cycles** (1er modificador): `REPEAT_OFFSET` para avanzar, `MIRROR` para vaivén; activa Cycle-Aware Keying.
- [ ] **Cycles y Smooth (Gaussian) no conviven** y deben ir primeros.
- [ ] Limpia mocap: **Decimate** (Ratio/Error) para reducir, **Butterworth/Gaussian Smooth** para jitter, **Euler Filter** para flips. "Menos keys, mejor puestas".
- [ ] **Los modificadores no viajan como tales**: para un loop, hornéalo a keys (`nla.bake`/Bake Keyframes) cubriendo el rango completo, o exporta un ciclo y usa Loop Time en Unity.
- [ ] Antes de exportar animación con IK/constraints: **`bpy.ops.nla.bake` con `visual_keying=True`**.
- [ ] FBX a Unity: `add_leaf_bones=False`, `use_armature_deform_only=True`, `bake_anim_step=1.0`, `simplify_factor=0.0` (deja reducir a Unity); *All Actions* True para todos los clips o False para un FBX por clip.
- [ ] **Verifica el clip YA importado en Unity**: el Keyframe Reduction puede aplanar tu ease sutil. Un clip importado es read-only.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Script con `action.fcurves` → `AttributeError` en 5.2 | Layered actions: `strip.channelbag(slot).fcurves`; insertar con `keyframe_insert` |
| Seguir un tutorial pre-4.4 del sistema de Actions viejo | Desde 4.4 toda Action es *layered*; slots en UI, layers/strips solo en Python |
| Aceptar handles Automatic → overshoot/oscilación no deseada | Usar **Auto Clamped** por defecto; Automatic solo donde se busque ese efecto |
| Auto Clamped comiéndose el overshoot → movimiento muerto | Romper a Free/Aligned y empujar el handle, o meter key extra de overshoot+settle |
| Leer el Graph Editor como espagueti | **Show Only Selected** + Normalize + Only Selected Keyframes Handles |
| Convertir de stepped a spline y dar por terminado | La conversión siempre ensucia; el polish (arcos, overshoot, foot slide) es la fase real |
| Poner un Noise/Cycles y confiar que llega a Unity | El FBX samplea el rango de la Action; un Cycles más allá de la última key se pierde — hornear a keys o Loop Time |
| Loop que "salta" en Unity | Trivially-cyclic + Cycle-Aware Keying en Blender; en Unity Loop Time/Loop Pose; contactos en el mismo tiempo normalizado |
| Smooth no reduce el número de keys | Smooth suaviza; para adelgazar usa **Clean** (redundantes) o **Decimate** (Ratio/Error) |
| Rotación con flip 359°→0° en el clip | **Euler Filter**; o trabajar en cuaternión (Resample Curves de Unity lo pasa a quat igual) |
| Exportar con IK/constraints sin hornear → el clip no mueve nada en Unity | `bpy.ops.nla.bake(visual_keying=True)` antes del FBX |
| Huesos `_end`/basura en el avatar de Unity | `add_leaf_bones=False` y `use_armature_deform_only=True` al exportar |
| Ease sutil que desaparece en el motor | Verificar el clip importado; bajar Rotation/Position Error o subir precisión de compresión |
| Keys en frames fraccionarios tras un retime | Snap ‣ a Nearest Frame; mantener keys en enteros |

## Fuentes

**Bases sintetizadas (repo El Estudio) — la TÉCNICA que este archivo ejecuta:**
- [ver: animacion3d/keyframes-curvas] — CRAFT de curvas agnóstica de herramienta (interpolación, handles, ease, spacing, overshoot, blocking→spline, cleanup, ciclos, y el sampling a Unity). Base directa.
- [ver: unity/animacion-unity] — consumo en motor: Animator, blend trees, compresión de import, avatar, eventos. Lado Unity del export.

**Vecinos en `animacion-blender/` (a redactar):** [ver: sistema-animacion] · [ver: actions-organizacion] · [ver: nla-editor] · [ver: bake-animacion] · [ver: export-clips-unity] · [ver: animacion-blender-operativo].

**Fuentes web verificadas (fetch OK esta sesión, 2026-07-20; `docs.blender.org`, páginas *Last updated 2026-07-20*):**
- **Blender Manual — F-Curve Properties** (`editors/graph_editor/fcurves/properties.html`) — interpolación Constant/Linear/Bézier + Easing/Dynamic Effects (Back/Bounce/Elastic, Ease In/Out/InOut); handle types Automatic/Auto Clamped/Vector/Aligned/Free; Handle Smoothing None/Continuous Acceleration; atajo `V` para handle.
- **Blender Manual — F-Curve Modifiers** (`.../fcurves/modifiers.html`) — Generator, Built-in Function, Envelope, **Cycles** (No Cycles/Repeat/Repeat with Offset/Repeat Mirrored, Count), Noise (Blend/Scale/Strength/Phase/Depth/Lacunarity/Roughness), Limits (X/Y), Stepped, Smooth (Gaussian); regla "Cycles y Smooth deben ir primeros e incompatibles"; Trivially Cyclic + Cycle-Aware Keying.
- **Blender Manual — Editing F-Curves** (`.../fcurves/editing.html`) — Interpolation Mode `T`, Easing Type `Ctrl-E`, Handle Type `V`; Snap (Flatten/Equalize Handles); Density ‣ Decimate/Bake Keyframes/Clean Keyframes; Smooth (Gaussian/Legacy/Butterworth); Blend/Ease tools.
- **Blender Manual — Graph Editor Introduction** (`editors/graph_editor/introduction.html`) — regiones, overlays View (Normalize/Auto Normalization, Show Handles `Ctrl-H`, Only Selected Keyframes Handles, Show Sliders/Cursor), Show Only Selected, 2D Cursor, Columns on Selected `K`.
- **Blender Manual — Actions** (`animation/actions.html`) — **Slotted/Layered Actions**: Action→Slots (expuestos en UI, tipo asociado), layers/strips solo en Python API, heurística de asignación auto.
- **Blender Manual — FBX** (`files/import_export/fbx.html`) y **FBX (Legacy)** (`.../fbx_legacy.html`) — en 5.2 el import usa el add-on nuevo, el **export va por el legacy** `export_scene.fbx`; sección Bake Animation (Key All Bones, NLA Strips, All Actions, Force Start/End Keying, Sampling Rate, Simplify) y Armatures (Only Deform Bones, Add Leaf Bones, bone axis).
- **Blender Python API** (`docs.blender.org/api/current`, *Last updated 2026-07-20*): `bpy.ops.graph.*` (interpolation_type/handle_type/extrapolation_type + enums, clean `threshold`/`channels`, decimate `mode`RATIO/ERROR, gaussian_smooth, euler_filter, bake_keys, keys/samples); `bpy.ops.nla.bake` (frame_start/end, step, only_selected, visual_keying, clear_constraints/parents, use_current_action, clean_curves, bake_types, channel_types); `bpy.ops.export_scene.fbx` (firma completa `bake_anim_*`, add_leaf_bones, use_armature_deform_only); `bpy.types.Action` (layers/slots, sin `fcurves`; `is_action_legacy`/`is_action_layered`); `bpy.types.ActionKeyframeStrip.channelbag(slot)` y `.key_insert`; `bpy.types.AnimData.action`/`action_slot`; `bpy.types.FModifierCycles` (`mode_before`/`mode_after` NONE/REPEAT/REPEAT_OFFSET/MIRROR, `cycles_before`/`cycles_after`).

**No verificado / nota de honestidad:** las páginas se sirvieron desde el canal `latest`/`current` de la documentación (que rastrea la versión actual, *Last updated 2026-07-20*), **no** contra un binario local de Blender 5.2 — los nombres de operador/enum/propiedad son estables en 5.x, pero un valor por defecto puntual podría diferir; confirmar en el binario 5.2 antes de citar un número literal crítico. El lado Unity (Resample Curves, Keyframe Reduction, Rotation/Position Error, read-only) se cross-referencia a las bases ya verificadas, no se re-fetcheó de `docs.unity3d.com` esta sesión.
