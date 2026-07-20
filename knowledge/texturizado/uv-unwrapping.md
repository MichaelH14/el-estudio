# UV unwrapping para assets de juego

> **Cuando cargar este archivo:** antes de texturizar, bakear o encargar CUALQUIER modelo 3D que reciba textura — para desplegar sus UVs (seams, unwrap, packing), fijar y verificar texel density, y preparar el canal de lightmap para Unity. Es el paso obligatorio entre un modelo game-ready y todo lo que sigue: bake [ver: baking], PBR [ver: pbr-teoria], pintado [ver: texturizado-blender] [ver: substance-y-alternativas] y export a Unity [ver: texturas-a-unity]. La malla debe llegar aquí ya limpia y con hard edges decididos [ver: modelado/fundamentos-3d] [ver: blender/edicion-malla].

**Versiones y verificación (jul-2026):** Blender 5.2 LTS · Unity 6/URP (6000.2) · Substance Painter 2026.
Los settings de Unity (lightmap UVs, tangentes) están verificados contra el manual oficial 6000.2 esta sesión (URLs en Fuentes). Los operadores `bpy.ops.uv.*` y sus parámetros están **re-verificados esta sesión contra `docs.blender.org/api/current/bpy.ops.uv.html`** (la página se identifica en su selector de versión como **5.2** — bajada por HTTP directo con `curl`; el fetcher de artefactos/navegador siguió devolviendo 403 al mismo dominio, pero el HTTP plano no): los 9 operadores citados en §9 existen tal cual, con dos correcciones sobre lo que se había asumido antes (default real de `unwrap` y disponibilidad de `MINIMUM_STRETCH` — ver §3). La malla de edición y los operadores de Edit Mode ya están verificados en [ver: blender/edicion-malla].

---

## 1. Qué son las UVs y por qué toda textura las necesita

Una textura es una imagen 2D; el modelo vive en 3D. Las **UVs** son las coordenadas que dicen qué punto de la imagen cae sobre cada vértice de la malla — el "molde de papel" desplegado del modelo. Sin UVs no hay forma de pegar una imagen a una superficie: **cualquier mapa que se muestree con coordenadas de textura (base color, normal, roughness, metallic, AO, emission, lightmap) las necesita.** Solo escapan los materiales 100% procedurales/por-vértice y los shaders unlit de color plano [ver: estilizado-texturas].

| Término | Definición |
|---|---|
| **U, V** | Los dos ejes del espacio de textura; se llaman U/V porque X/Y/Z ya nombran los ejes del modelo (Wikipedia, *UV mapping*) |
| **UV / vértice UV** | Coordenada (u,v) asignada a un vértice *dentro de una cara*. Un vértice de malla puede tener varias UVs (una por isla que toca) — por eso los seams duplican vértices de GPU [ver: modelado/fundamentos-3d §2] |
| **Isla (UV island / chart)** | Grupo conexo de caras en el plano UV, rodeado de seams |
| **Seam (costura)** | Borde por donde se "corta" la malla para poder aplanarla (§2) |
| **UV map / canal UV** | Un conjunto completo de UVs. Una malla puede tener varios: `UV0` para texturas, `UV2` para lightmap (§8) |

### El espacio 0–1 (el UV tile)

- Las UVs se normalizan al rango **[0,1] en U y en V**, independiente de la resolución de la imagen (Wikipedia, *UV mapping*). `(0,0)` = una esquina de la textura, `(1,1)` = la opuesta. Ese cuadrado es el **UV tile** o **UDIM 1001**.
- Trabajar en 0–1 hace la textura resolución-agnóstica: la misma UV sirve a 512, 1024 o 2048 px.
- **Regla para juego: todo el detalle único cabe dentro del 0–1, sin solapes** (salvo solape intencional §7). UVs fuera de 0–1 = la textura se repite (tiling) — deseable en trims/tileables, un bug en un asset de detalle único [ver: atlas-trim-optimizacion].

### UDIM (a nivel concepto)

- **UDIM** = una rejilla de tiles 0–1 numerados para repartir un asset en varias texturas de alta resolución. El primer tile es **1001** (el cuadrado 0–1); avanzar en U suma 1 (1002, 1003…); subir una fila en V suma 10 (1011 es el tile encima del 1001). Cada tile lleva su propia imagen.
- **Uso:** film/VFX y assets de héroe muy grandes donde un solo 0–1 no da resolución. Substance Painter soporta flujo UDIM (UV Tiles).
- **En juego casi no se usa en runtime:** los engines de tiempo real esperan una textura por material; UDIM se colapsa a atlas antes de shippear. Para 99% de props de juego: **un solo tile 0–1** [ver: atlas-trim-optimizacion]. Mencionado aquí para reconocerlo, no para usarlo por defecto.

---

## 2. Seams: dónde cortar

Un seam es un corte necesario: aplanar una superficie 3D sin cortarla obliga a estirarla (imposible sin distorsión, como una cáscara de naranja). El arte está en **cortar donde no se note y donde menos se estire.**

### Dónde poner seams

| Regla | Por qué |
|---|---|
| En bordes **escondidos** (interior de un codo, bajo el brazo, costuras de ropa reales, contacto con el suelo) | El seam produce un corte visible en la textura y un salto de shading; que caiga donde la cámara no llega |
| En **hard edges / cambios de ángulo fuertes** de hard-surface | El quiebre ya rompe la superficie ópticamente; el seam ahí es gratis y reduce el estiramiento |
| Siguiendo la **silueta natural** de las piezas (cilindro → corte a lo largo + tapas aparte) | Menos distorsión, islas más rectangulares (mejor packing §5) |
| Suficientes para que **cada isla se aplane casi plana** | Pocas islas grandes = más estiramiento; el balance es "las mínimas islas que dejen la distorsión aceptable (§4)" |

### La regla hard-edge ↔ seam (canon)

Establecida en [ver: modelado/fundamentos-3d §3] y [ver: modelado/high-to-low] — no se repite la derivación, solo el uso operativo aquí:

- **Todo hard edge DEBE coincidir con un UV seam.** Hard edge sin seam = artefacto de seam en el bake del normal map (las vertex normals partidas no tienen a dónde ir en la textura).
- Lo inverso NO: puede (y suele) haber más seams que hard edges — seams extra reducen el warping de textura y no cuestan (el vértice ya se parte en el seam).
- Como el seam ya duplica el vértice de GPU, poner el hard edge ahí es casi gratis [ver: modelado/fundamentos-3d §2].
- **Flujo Blender:** marcar sharp y seam juntos. `Select ‣ Select All by Trait` o seleccionar por sharpness y `UV ‣ Mark Seam`; o `UV ‣ Seams From Islands` (deriva seams de las islas ya hechas). Marcar seam por rutas largas: shortest path + Edge Tag ‣ Tag Seam [ver: blender/edicion-malla §3].

Blender: `Edge ‣ Mark Seam` (`U` en Edit Mode → UV menu, o `Ctrl+E ‣ Mark Seam`). Los seams se guardan en el atributo `seam` de la malla y son lo que `Unwrap` respeta al cortar.

---

## 3. Unwrap en Blender

El UV Editor (workspace **UV Editing**) muestra la malla desplegada sobre el cuadrado 0–1. Selección sincronizada con la 3D. Flujo base: **marcar seams → seleccionar todo (`A`) → desplegar → revisar distorsión (§4) → empacar (§5) → fijar texel density (§6).**

### Los tres métodos que importan

| Método | Menú (`U` en 3D Edit Mode) | Qué hace | Cuándo |
|---|---|---|---|
| **Unwrap** | UV ‣ Unwrap | Aplana **respetando los seams marcados** minimizando distorsión de ángulo | El caballo de batalla: todo lo que lleva seams pensados (personajes, props, hard-surface con seams) |
| **Smart UV Project** | UV ‣ Smart UV Project | Corta automático por **ángulo entre caras** y empaca; ignora seams manuales | Primer pase rápido, props mecánicos, bake de AO/lightmap provisional, o cuando marcar seams a mano no compensa |
| **Follow Active Quads** | UV ‣ Follow Active Quads | Propaga la UV de la cara activa a un tramo de quads manteniendo proporción de edges | Tuberías, cintas, escaleras, carreteras, telas en cuadrícula — todo lo que es una tira regular de quads |

Otros del mismo menú: **Cube/Cylinder/Sphere Projection** (proyección primitiva, útil para formas que calzan), **Project From View** (proyecta lo que ves — decals, caras planas frontales), **Lightmap Pack** (islas sin solape para un canal de lightmap propio, §8), **Reset** (cada cara al cuadrado 0–1 completo).

### Parámetros clave

**Unwrap** (panel *Adjust Last Operation*):
- **Method:** el default real del operador en Blender 5.2 es `Conformal` (rápido, preserva ángulos, puede estirar áreas) — **no** `Angle Based` como asume la mayoría de tutoriales viejos; verificado en la firma de `bpy.ops.uv.unwrap()` en docs.blender.org (servida como 5.2). `Angle Based` sigue siendo la recomendación textual de Blender ("usually gives better results than Conformal, while being somewhat slower") — cámbialo a mano si el resultado por defecto no convence. `Minimum Stretch` (SLIM, relaja iterativamente para minimizar estiramiento) **confirmado presente en 5.2**; usa el parámetro `iterations` (0–10000), que solo aplica a este método.
- **Fill Holes**, **Correct Aspect** (respeta el aspect no cuadrado de la textura), **Margin** / **Margin Method**, **Use Subdivision Surface**. También existen (menos usados): `use_original_bounds`, `no_flip`, `use_weights`/`weight_group`/`weight_factor` (parametrización ponderada por vertex group).

**Smart UV Project** (dialog):
- **Angle Limit** (default **66°**): ángulo entre caras a partir del cual corta una isla. Más bajo = más islas.
- **Island Margin**: separación entre islas al empacar (0 por defecto — subirlo para dejar padding).
- **Area Weight**, **Correct Aspect**, **Scale to Bounds** (estira el resultado a llenar el 0–1).

**Follow Active Quads** — **Edge Length Mode:** `Even` (todos los quads igual, look de cuadrícula) · `Length` (respeta longitud real de cada edge) · `Length Average`. Requiere una cara activa ya bien desplegada como semilla; **no empaca ni escala a 0–1** por sí solo — normalizar después.

### Snippet: unwrap desde seams (headless / MCP)

```python
import bpy, math
obj = bpy.context.active_object
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
# respeta los seams ya marcados en la malla:
bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001, correct_aspect=True)
# alternativa automática sin seams:
# bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.0,
#                          correct_aspect=True, scale_to_bounds=False)
bpy.ops.object.mode_set(mode='OBJECT')
```

`angle_limit` en la API está en **radianes**; el default real es `1.15192` rad (≈66°) — confirmado en la firma de `bpy.ops.uv.smart_project()` (docs.blender.org, 5.2). Si necesitas otro ángulo en grados, conviértelo con `math.radians(x)` como en el snippet comentado arriba; no hardcodees el radián a mano.

---

## 4. Distorsión: leerla y minimizarla

El objetivo no es "cero distorsión" (imposible), sino **distorsión uniforme y por debajo de lo perceptible**, y sobre todo texel density consistente (§6).

### Checker map: el diagnóstico visual

- Aplicar una textura de **cuadrícula (checker)** con números/colores por celda. La lectura:
  - **Cuadros cuadrados y del mismo tamaño en toda la malla** → sin estiramiento y texel density uniforme. Meta.
  - **Cuadros rectangulares/estirados** → *stretch*: la isla está comprimida en un eje. Marcar más seams o relajar.
  - **Cuadros más grandes en una pieza que en otra** → texel density inconsistente: esa pieza recibe menos píxeles (§6, `Average Islands Scale`).
- En Blender: material con checker (o **Image Editor ‣ New ‣ UV Grid / Color Grid**) mostrado en el viewport; el addon Texel Density Checker pinta un checker por TD (§6). Flujo de checker en engine/standalone: [ver: texturas-a-unity].

### Stretch overlay (Blender)

En el UV Editor, **Overlays ‣ Display Stretching**: colorea las caras en el plano UV por **Area** o **Angle**. Azul = sano, rojo = estirado. Es el diagnóstico numérico que complementa el checker visual.

### Minimizar

| Herramienta | Efecto |
|---|---|
| Más **seams** en las zonas rojas | La causa raíz del stretch suele ser "islas muy grandes / muy curvas" |
| **UV ‣ Minimize Stretch** (`Ctrl+V` en UV Editor) | Relaja iterativamente los vértices UV para bajar el estiramiento (respeta pins). Interactivo: `blend`/iteraciones |
| **Pin** (`P`) + Unwrap | Clavar vértices clave y re-desplegar para forzar forma |
| Herramientas **Relax / Pinch** (UV toolbar) | Suavizar islas a mano [ver: texturizado-blender] |

`bpy.ops.uv.minimize_stretch(fill_holes=True, blend=0.0, iterations=...)`.

---

## 5. Packing: empacar el 0–1

Packing = colocar todas las islas dentro del 0–1 aprovechando el máximo de espacio (cada píxel vacío es resolución tirada), con **padding suficiente** para que no se filtren unas islas en otras al bajar de mip.

### Pack Islands (Blender, `UV ‣ Pack Islands`)

Reescrito en 3.6+ (empaque tipo UVPackmaster). Parámetros (API `bpy.ops.uv.pack_islands`):

| Parámetro | Opciones / default | Nota |
|---|---|---|
| **Shape Method** | `Concave` (default, ajusta al contorno real, mejor densidad) · `Convex` · `Aabb` (cajas, más rápido/predecible) | Concave empaca más apretado; Aabb deja huecos pero es estable |
| **Rotation** (`rotate`) | on/off + **Rotation Method** `Any` · `Cardinal` · `Axis-aligned` | Rotar mejora la densidad; **apagarla** si quieres orientación consistente (§ abajo) |
| **Scale** | on (default) | Escala las islas para caber |
| **Margin** | default `0.001`, **Margin Method** `Scaled` · `Add` · `Fraction` | El padding entre islas (§ padding) |
| **Merge Overlapping**, **Lock Pinned Islands**, **Pin** | — | Pins para congelar islas ya colocadas |

`bpy.ops.uv.pack_islands(shape_method='CONCAVE', rotate=True, margin=0.01, margin_method='SCALED')`.

### Padding / edge padding según resolución

El margen debe sobrevivir a los **mipmaps**: cada nivel de mip promedia píxeles vecinos, y sin padding el color de una isla "sangra" a la de al lado (seams brillantes a distancia). Regla del oficio (Marmoset/handplane; no un único número oficial — **calibrar al target**):

| Resolución de textura | Padding entre islas (borde a borde) | Regla |
|---|---|---|
| 256 | ~4 px | El padding **escala con la resolución** |
| 512 | ~8 px | Baseline común: ~8 px @1024 y proporcional |
| 1024 | ~8–16 px | Unity usa **4 px @1024** como default de *Pack Margin* de lightmap (ancla oficial, §8) |
| 2048 | ~16–32 px | Para lightmaps y assets que se ven de cerca, subir |
| 4096 | ~32 px | — |

- El **borde exterior del 0–1** también necesita padding (no pegar islas al borde 0/1).
- Padding se expresa en px pero se setea como fracción del 0–1 (`margin`): `px_padding / resolución`. Ej: 16 px @2048 → margin ≈ 0.0078.
- **Edge padding / dilation** (rellenar los píxeles fuera de la isla con el color del borde) lo hace el baker/pintor, no el packer: Substance dilata automáticamente al exportar; el baker de Blender/Marmoset tiene "Padding/Extend" [ver: baking].

### Orientación consistente

- **Endereza las islas** (UV ‣ Align, o herramienta "Straighten") y oriéntalas igual (p. ej. la trama de la madera siempre vertical). Beneficios: se pintan/tilean mejor, se comprimen mejor, y detalles direccionales (anisotropía, brushstrokes) quedan coherentes.
- Si la orientación importa, **apagar Rotation** en Pack Islands o usar `Rotation Method: Axis-aligned` para que solo rote en 90°.

---

## 6. Texel density (px/m): consistencia entre assets

**Texel density (TD)** = cuántos píxeles de textura cubren un metro de superficie del modelo (Beyond Extent, *Texel Density Explained*). Es la métrica que hace que dos props uno al lado del otro se vean del mismo "nivel de detalle". TD inconsistente = un asset se ve nítido y el de al lado borroso, aunque ambos sean 2048.

### Cálculo

- Depende de **resolución de textura** y **tamaño real del modelo**: más resolución o menos tamaño → más TD.
- Fórmula base: una cara que ocupa **todo** el 0–1 de una textura de `R` px sobre un tramo real de `L` metros tiene `TD = R / L` px/m.
- Unidades: se usa **px/m** o **px/cm** (1 px/cm = 100 px/m).
- **Medir en la práctica:** aplicar un checker de resolución conocida (o el addon) y ver si los cuadros miden lo mismo en todos los assets; el addon lo da numérico.

### Herramientas

| Herramienta | Qué hace |
|---|---|
| **Blender — Texel Density Checker** (addon mrven, GitHub; presets en 2026.1) | Calcula TD de mesh/caras para cualquier tamaño de textura, **reescala UVs a un TD objetivo**, copia TD entre objetos, selecciona caras por TD, y visualiza con checker/vertex color |
| **Blender — `UV ‣ Average Islands Scale`** | Iguala la escala **relativa** de todas las islas (todas al mismo TD entre sí); no fija un valor absoluto — hacerlo primero, luego escalar el conjunto al TD objetivo. `bpy.ops.uv.average_islands_scale(scale_uv=False, shear=False)` |
| **Maya/3ds Max** | Calculadora de TD en el UV toolkit nativo |

### Valores de referencia (rangos del oficio — NO un estándar único; calibrar por proyecto)

TD se decide con el poly budget y la cámara del juego [ver: modelado/presupuestos-poligonos]. Referencias:

| Contexto | TD orientativo | Fuente / nota |
|---|---|---|
| Móvil / assets lejanos | ~256–512 px/m | Rango común del oficio (no verificado a un doc único) |
| PC/consola, props estándar | ~512–1024 px/m (5.12–10.24 px/cm) | Rango común; "5.12 px/cm" es baseline muy citado |
| Héroe / first-person / se ve de cerca | ~1024–2048 px/m (10.24–20.48 px/cm) | Beyond Extent recomienda **20.48 px/cm** (=2048 px/m) para proyectos personales; FPS = TD más alto, TPS medio, top-down el más bajo |

- **Regla operativa:** fijar UN TD por proyecto (o por tier: entorno / props / héroe), declararlo en el style guide junto al poly budget [ver: pipeline/arte-a-unity §7], y verificar cada asset con checker/addon antes de texturizar. La spec de entrega a Unity ya pide texel density consistente [ver: texturas-a-unity].
- Assets grandes (edificios, terreno) reparten TD con **trims y tileables**, no con un 0–1 gigante [ver: atlas-trim-optimizacion].

---

## 7. Overlapping UVs: cuándo sí, cuándo no

Solapar islas = varias caras comparten el mismo espacio de textura → ahorro de resolución (esas caras reciben más px por el mismo tamaño de mapa).

### Cuándo SÍ

| Caso | Cómo |
|---|---|
| **Simetría** (personaje, vehículo, prop simétrico) | Desplegar una mitad, **espejar** la otra encima (voltear la isla). Media textura = doble TD. En Blender: copiar isla y `mirror` en el eje UV |
| **Repetición** (tornillos, tablones, ladrillos idénticos, ruedas) | Apilar todas las instancias en la misma isla; se pintan una vez |
| **Tileables/trims** | Muchas caras muestrean el mismo material repetido [ver: atlas-trim-optimizacion] |

- Truco estándar: mover el juego espejado/repetido **a un UDIM tile vecino** (fuera del 0–1) mientras se bakea para que el baker no confunda el solape, y traerlo de vuelta después. O usar el flujo "bake por UV set" del baker.

### Cuándo NO (obligatorio islas únicas)

| Caso | Por qué |
|---|---|
| **Lightmap UVs (UV2)** | El lightmap guarda iluminación *por punto del mundo*: dos caras solapadas recibirían la misma luz → sombras erróneas. **Sin solapes y sin salir de 0–1** es requisito duro (§8) |
| **Detalle único** (asimetría real: cicatriz en una mejilla, desgaste específico, texto/logo, sucio direccional) | Islas solapadas no pueden llevar detalle distinto; el espejo delata la simetría (patrón repetido "de plástico") |
| **Bake de AO/curvature del asset final** | El AO es posicional; caras solapadas se pisan. Si hay solape para textura, el AO se hace en el UV set único o desplazando el solape a otro tile |
| **Costura visible del espejo** | Línea central de simetría muy notoria → romper con un decal o desplazar el seam |

Práctica común: **UV0 con solapes para el color/normal** (ahorra) + **UV2 sin solapes para el lightmap** (§8). El mejor de ambos.

---

## 8. UVs para lightmaps en Unity (segundo canal)

Verificado contra el manual Unity 6000.2 (URLs en Fuentes).

### Cuándo hace falta

- **Solo si el objeto es estático y recibe iluminación *baked* (lightmapping).** Objetos dinámicos o iluminados solo en tiempo real no usan lightmap UVs. Un juego con GI totalmente real-time no necesita UV2.
- El lightmap es una textura extra que guarda la luz pre-calculada; necesita **su propio set de UVs sin solapes y dentro de 0–1** (§7) — el UV0 con solapes de simetría no sirve.

### Cómo se genera

Dos caminos:

1. **Autor propio:** colocar las lightmap UVs en el canal **`Mesh.uv2`** (Unity lo llama "UV1" en la UI; el segundo set) — desplegado sin solapes, islas rectas, con padding. Se exporta como segundo UV map del FBX [ver: blender/import-export]. En Blender, `Lightmap Pack` o un unwrap limpio en un segundo UV layer.
2. **Automático (lo habitual):** en el **Model Import Settings ‣ Model ‣ Geometry**, activar **Generate Lightmap UVs** → Unity crea el set en `Mesh.uv2` a partir del UV0 al importar. "Creates a second UV channel for the lightmap."

### Settings de Generate Lightmap UVs (Unity 6000.2, verificados)

| Setting | Definición | Default |
|---|---|---|
| **Hard Angle** | Ángulo entre triángulos vecinos a partir del cual Unity lo trata como hard edge y crea un seam en el lightmap | **88°** (rango 0–180) |
| **Angle Error** | Desviación máx. de los ángulos UV respecto a la geometría (%) | **8%** (0–100) |
| **Area Error** | Desviación máx. de las áreas UV respecto a la geometría (%) | **15%** (0–100) |
| **Margin Method** | `Manual` (fijas Pack Margin) o `Calculate` (Unity lo deriva de la resolución de lightmap) | — |
| **Pack Margin** | Margen entre charts en px, **asumiendo que la mesh ocupa un lightmap 1024×1024** | **4 px** (1–64; solo con Margin Method = Manual) |
| **Min Lightmap Resolution** | Resolución mínima de lightmap (texels/unidad) en todas las escenas donde aparece la mesh | — (solo con Calculate) |
| **Min Object Scale** | Escala mínima de transform de los GameObjects que usan la mesh | — (solo con Calculate) |

- Con **Margin Method: Calculate**, Unity calcula el Pack Margin usando Min Lightmap Resolution + Min Object Scale — más robusto cuando el mismo mesh aparece a distintas escalas.
- **Solape en el lightmap = warning "UV overlap"** al bakear: sombras/luz filtrándose entre caras. Subir Pack Margin o mejorar el unwrap. Detalle de lightmapping y sorting: [ver: unity/rendering-urp].
- La spec de entrega (cuándo pedir UV2 vs. dejar que Unity lo genere) vive en [ver: pipeline/arte-a-unity §7]. Tangentes del normal map (MikkTSpace, sincronizado bake↔engine): [ver: modelado/fundamentos-3d §3], import en [ver: texturas-a-unity].

---

## 9. Operadores `bpy.ops.uv.*` (referencia rápida)

Nombres y defaults **verificados esta sesión contra `docs.blender.org/api/current/bpy.ops.uv.html`** (la página se identifica como versión **5.2**) — bajada por HTTP directo, no por el fetcher de artefactos, que sigue devolviendo 403 a ese dominio. Los 9 operadores de la tabla existen tal cual en 5.2; los defaults quedan anotados donde difieren de lo asumido antes (`unwrap` → nota en §3). La malla y limpieza previas, en [ver: blender/edicion-malla]; scripting general en [ver: blender/bpy-scripting].

| Operador | Uso | Parámetros clave |
|---|---|---|
| `uv.mark_seam(clear=False)` | Marcar/quitar seams | `clear` |
| `uv.seams_from_islands()` | Derivar seams de las islas existentes | — |
| `uv.unwrap(...)` | Desplegar respetando seams | `method` (`ANGLE_BASED`/`CONFORMAL` **default**/`MINIMUM_STRETCH` con `iterations`), `margin`, `margin_method`, `correct_aspect`, `fill_holes` |
| `uv.smart_project(...)` | Auto-corte por ángulo + pack | `angle_limit` (rad, def ≈66°), `island_margin`, `area_weight`, `correct_aspect`, `scale_to_bounds` |
| `uv.follow_active_quads(mode=...)` | Propagar desde cara activa | `mode`: `EVEN`/`LENGTH`/`LENGTH_AVERAGE` |
| `uv.cube_project` / `cylinder_project` / `sphere_project` | Proyección primitiva | `..._size`, `correct_aspect`, `scale_to_bounds` |
| `uv.minimize_stretch(...)` | Relajar estiramiento | `fill_holes`, `blend`, `iterations` |
| `uv.average_islands_scale(...)` | Igualar TD relativo entre islas | `scale_uv`, `shear` |
| `uv.pack_islands(...)` | Empacar en 0–1 | `shape_method`, `rotate`+`rotate_method`, `margin`+`margin_method`, `scale`, `pin` |
| `uv.lightmap_pack(...)` | UVs de lightmap sin solape | opciones de selección + `margin` |

### Snippet: unwrap → TD uniforme → pack (pipeline completo)

```python
import bpy, math
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001, correct_aspect=True)
bpy.ops.uv.average_islands_scale()          # todas las islas al mismo TD relativo
bpy.ops.uv.pack_islands(shape_method='CONCAVE', rotate=True,
                        margin=0.0078)       # ≈16 px @2048
bpy.ops.object.mode_set(mode='OBJECT')
```

Verificar SIEMPRE tras el script: contar islas / abrir el UV Editor / aplicar checker — un operador que "no hizo nada" también es un bug [ver: blender/edicion-malla]. TD absoluto se fija con el addon Texel Density Checker (§6), no con estos operadores.

---

## Reglas prácticas

1. La malla llega a UV **ya limpia y con hard edges decididos**: limpieza (merge, non-manifold, normales) y escala aplicada ANTES de desplegar [ver: blender/edicion-malla §6].
2. Todo mapa que se muestrea con coordenadas (color, normal, roughness, metallic, AO, lightmap) exige UVs — solo escapa lo procedural/unlit plano.
3. Detalle único: dentro del 0–1, **sin solapes**. Fuera de 0–1 solo a propósito (tileables/trims) [ver: atlas-trim-optimizacion].
4. Seams en bordes escondidos, en la silueta natural y en los hard edges. **Todo hard edge = un seam** (la inversa no aplica).
5. Las islas mínimas que dejen la distorsión aceptable — no una isla gigante estirada ni cien islitas.
6. Elegir método: **Unwrap** (seams pensados) · **Smart UV Project** (auto/rápido, `angle_limit` 66°) · **Follow Active Quads** (tiras de quads regulares).
7. Verificar distorsión con **checker map** + **stretch overlay** antes de empacar: cuadros cuadrados e iguales en toda la malla.
8. Endereza y orienta las islas de forma consistente; apaga Rotation en Pack si la orientación importa.
9. **Average Islands Scale** primero (TD relativo uniforme), luego escalar al TD objetivo del proyecto.
10. Fija UN texel density por proyecto/tier (px/m), decláralo en el style guide junto al poly budget, y verifícalo por asset con checker/addon.
11. Padding proporcional a la resolución (~8–16 px @1024–2048); expresado como fracción `px/resolución` en `margin`. No pegar islas al borde 0/1.
12. Solape SÍ para simetría/repetición en UV0 (ahorra resolución); NO para lightmaps, detalle único, texto/logos y AO posicional.
13. Lightmap (UV2 / `Mesh.uv2`) solo si el objeto es estático y recibe luz baked: sin solapes, dentro de 0–1.
14. En Unity, o autoras el UV2 o activas **Generate Lightmap UVs** (defaults: Hard Angle 88°, Angle Error 8%, Area Error 15%, Pack Margin 4 px @1024); si el mesh aparece a varias escalas, usa Margin Method = Calculate.
15. Exporta el UV0 (y UV2 si aplica) en el FBX; tangentes MikkTSpace sincronizadas bake↔engine [ver: modelado/fundamentos-3d §3] [ver: texturas-a-unity].
16. Vía script/MCP: verifica cada operador con el tooltip Python (docs 5.2), y tras correr, comprueba el resultado en el UV Editor — no confíes en el "OK" del operador.
17. UDIM: reconócelo, pero para juego en runtime colapsa a un solo tile / atlas; no lo uses por defecto.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Textura estirada/comprimida en una zona | Stretch por isla muy grande/curva: más seams ahí + Minimize Stretch; leer con checker + Display Stretching |
| Un prop se ve nítido y el de al lado borroso | Texel density inconsistente: Average Islands Scale + fijar el mismo TD (px/m) con el addon |
| Seam brillante/oscuro visible a distancia | Falta padding: el color sangra entre islas al bajar de mip. Subir `margin` (~8–16 px según resolución) y confiar la dilation al baker/pintor |
| Artefacto de seam justo en un hard edge al bakear el normal | Hard edge sin UV seam: marcar seam en TODO hard edge [ver: modelado/fundamentos-3d §3] |
| Warning "UV overlap" al bakear lightmap en Unity | UV2 con solapes o fuera de 0–1: usar islas únicas; subir Pack Margin o Generate Lightmap UVs con Calculate |
| El normal map espejado se ve "de plástico"/simétrico | Solape de simetría en UV0 arrastrado a detalle que debía ser único: romper con decals o dar isla propia a la zona asimétrica |
| AO bakeado con manchas donde hay islas repetidas | AO es posicional y se pisa en solapes: bakear con las islas repetidas desplazadas a otro UDIM tile o en un UV set único |
| Textura se repite/tilea donde no debía | UVs fuera del 0–1 sin querer: normalizar al 0–1 (Pack Islands o escalar dentro del tile) |
| Follow Active Quads sale a escala rara | No empaca ni normaliza solo: Average Islands Scale + Pack Islands después |
| `angle_limit` de smart_project "no corta como en la UI" | La API está en radianes: `math.radians(66)`, no `66` |
| Lightmap generado con seams por todas partes | Hard Angle muy bajo: subirlo (default 88°) o autora el UV2 a mano |
| Islas pegadas al borde del 0–1 → sangrado en el borde de la textura | Dejar padding también contra 0 y 1, no solo entre islas |
| Modelo con escala sin aplicar desplegado | El unwrap/TD sale sesgado: aplicar escala en Object Mode ANTES [ver: blender/edicion-malla] |

## Fuentes

**Web verificadas esta sesión:**
- **Unity Manual 6000.2 — Generate lightmap UVs** (`LightingGiUvs-GeneratingLightmappingUVs.html`) — Unity Technologies — lightmap UVs van a `Mesh.uv2` ("UV1"), cuándo se necesitan, cómo activar Generate Lightmap UVs.
- **Unity Manual 6000.2 — Automatic lightmap UV generation settings** (`LightingGiUvs-Reference.html`) — Unity — valores exactos: Hard Angle 88°, Angle Error 8%, Area Error 15%, Margin Method Manual/Calculate, Pack Margin 4 px @1024 (1–64), Min Lightmap Resolution, Min Object Scale.
- **Unity Manual 6000.2 — Model Import Settings / FBX Importer (Model tab)** (`FBXImporter-Model.html`) — Unity — Generate Lightmap UVs crea el segundo canal; Tangents ‣ **Calculate Mikktspace** es el default solo *cuando Normals = Calculate* (el default de Normals es "Import"; la doc no fija un default incondicional de Tangents — matizado esta sesión, re-verificado por fetch directo).
- **Blender Python API — `bpy.ops.uv` (UV Operators)** (`docs.blender.org/api/current/bpy.ops.uv.html`; la página se identifica en su selector de versión como **5.2**) — bajada esta sesión con `curl` directo (el fetcher de artefactos/navegador siguió devolviendo 403 al mismo dominio): confirma existencia y firma completa de los 9 operadores citados en §9; **corrige** el default de `uv.unwrap` a `method='CONFORMAL'` (no `ANGLE_BASED` como se había asumido) y **confirma `MINIMUM_STRETCH` presente en 5.2** con su parámetro `iterations`; confirma `smart_project` con `angle_limit` default `1.15192` rad (≈66°); confirma `pack_islands` con `shape_method` (`CONCAVE` default/`CONVEX`/`AABB`), `rotate_method` (`ANY`/`CARDINAL`/`AXIS_ALIGNED`/`AXIS_ALIGNED_X`/`AXIS_ALIGNED_Y`) y `margin` default `0.001`; confirma `average_islands_scale(scale_uv=False, shear=False)` y `mark_seam(clear=False)` exactos como en el archivo.
- **Texel Density Explained** — Beyond Extent (deep dive) — definición de texel density, px/cm ↔ px/m, cálculo (resolución ÷ tamaño), recomendación 20.48 px/cm para proyectos personales, TD por perspectiva (FPS alto / TPS medio / top-down bajo), tooling (Blender addon, Maya/Max).
- **Blender Texel Density Checker** — repo `mrven/Blender-Texel-Density-Checker` (GitHub README) — cálculo/reescalado de TD a un objetivo, copia de TD entre objetos, selección por TD, visualización con checker/vertex color, presets (2026.1).
- **UV mapping** — Wikipedia — U/V como ejes 2D (X/Y/Z ocupados por el modelo), rango normalizado [0,1] resolución-agnóstico, unwrap como molde, minimizar seams/overlaps, solape de triángulos opuestos para simetría.

**No accesibles esta sesión (403/404 incluso al `curl` directo, a diferencia de `docs.blender.org` — ver arriba):** `blender.org/download/releases/4-3/` (para fechar con precisión cuándo llegó Minimum Stretch/SLIM — queda sin fecha exacta; solo confirmado que está disponible en 5.2) y el repo `blender/blender-manual` en GitHub raw (404 en las rutas probadas). Substance Painter 2026 (`substance3d.adobe.com`/helpx) redirigió a home o dio timeout/404 — el detalle de UDIM/dilation/texture set en Substance queda por cross-ref a substance-y-alternativas (aún por escribir), no verificado directamente. La API de Edit Mode y el estado 5.2 ya están verificados en [ver: blender/edicion-malla].

**Bases sintetizadas (no repetir, cross-referenciar):**
- [ver: modelado/fundamentos-3d] — regla hard-edge↔seam, vertex splits por seam, tangent basis/MikkTSpace, texel density en el glosario.
- [ver: blender/edicion-malla] — limpieza de malla, Mark Seam, shortest path + Tag Seam, escala aplicada, verificación de operadores vía script.
- [ver: pipeline/arte-a-unity] — spec de entrega 3D: UV0 sin solapes, UV2/Generate Lightmap UVs, texel density declarada, canales URP Lit, smoothness = 1−roughness.

**Cross-refs internas de texturizado (aún por escribir):** [ver: pbr-teoria] · [ver: baking] · [ver: texturizado-blender] · [ver: substance-y-alternativas] · [ver: estilizado-texturas] · [ver: atlas-trim-optimizacion] · [ver: texturas-a-unity].
