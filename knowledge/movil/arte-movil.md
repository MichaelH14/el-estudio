# Arte y modelado para móvil

> **Cuando cargar este archivo:** al fijar presupuestos de arte (tris, texturas, materiales, memoria) para un juego que corre en teléfonos reales, al decidir estilo visual pensando en gama baja, al modelar/texturizar/atlasar con el device como techo, o al montar UI/HUD para dedos y pantallas chicas. Es la capa de ESPECIALIZACIÓN móvil sobre las bases generales: [ver: modelado/presupuestos-poligonos] (poly budget, LODs, impostors), [ver: texturizado/atlas-trim-optimizacion] (atlas/trim/tileable, compresión, memoria) y [ver: arte-2d/fundamentos-2d] (PPU, resolución, paleta). Aquí va SOLO el ángulo móvil; lo genérico NO se repite. El runtime y shaders móviles: [ver: unity-movil-rendimiento], [ver: unity-movil-graficos]. UI de interacción: [ver: ux-ui/mobile-ux]. Negocio/estilo de mercado: [ver: mercado-movil].

## 1. La restricción que no existe en PC: el presupuesto de arte es TÉRMICO

En consola/PC presupuestas por **frame** (tris/frame, draw calls/frame, ms de GPU). En móvil ese presupuesto sigue vivo [ver: modelado/presupuestos-poligonos §7] pero hay un techo por encima: **el térmico y de batería**. El arte no se aprueba porque corra a 60 FPS los primeros 30 segundos — se aprueba porque los **sostiene** sin throttling.

| Realidad móvil | Número / fuente | Consecuencia para el arte |
|---|---|---|
| El SoC baja frecuencias por calor | El framerate suele **deteriorarse dentro de los primeros 45-50 min** de juego (Android perf guide) | Presupuestar para el estado THROTTLED, no el frío. Un margen ~20-30% bajo el pico |
| GPU tile-based (TBDR) en todo Android/iOS | La escena se procesa por **tiles**; el vertex/binning pass lee posición de cada vértice a memoria (Android, vertex-data-management) | El vertex count pega más fuerte que en desktop; overdraw es doblemente caro (bandwidth) |
| El objetivo real de UI es barato | Meta: **reducir el tiempo de UI a 2-3 ms** por frame (Android perf guide) | HUD sin overdraw ni transparencias apiladas (§9) |
| Unity reacciona al calor | Adaptive Performance da feedback de estado térmico/energético para "mantener framerates constantes por más tiempo y prevenir throttling" (Unity docs) | El arte debe degradar limpio: LOD bias, resolución, calidad — sin romperse (§6) [ver: unity-movil-rendimiento] |

**Regla mental móvil:** el peor caso no es la pantalla más cargada — es esa misma pantalla **a los 40 minutos, con el teléfono caliente y la batería al 15%**. Ese es el presupuesto real.

## 2. Presupuestos de arte por tier de dispositivo

El techo de tris/frame y draw calls no es único: depende de la gama. Los números por-asset genéricos ("columna Móvil") ya están en [ver: modelado/presupuestos-poligonos §3]; aquí se **estratifica por tier** y se ancla con lo que sí tiene fuente.

### Anclas con fuente (no inventar alrededor de esto)

| Ancla | Número | Fuente |
|---|---|---|
| Escena móvil real (cámara fija, muchos animados) | Demo Armies: **~210,000 tris/frame a ~30 FPS**; torretas ~3,000 tris; soldados de multitud **~360 tris** c/u | Android Game Dev — Geometry optimization |
| Límite duro de mesh | **65,535 vértices** por mesh (índices 16-bit); pasarse → 32-bit (más bandwidth) o partir | Android Geometry / [ver: modelado/presupuestos-poligonos §1] |
| Micro-triángulos | Mantener triángulos **> 10 px²** en la imagen final; los <1-10 px se pagan enteros sin aportar | Android Geometry |
| Personaje "premium" en móvil | MetaHuman "best LOD" = **LOD3 ≈ 2,500 verts cabeza + 1,507 cuerpo (~4k verts)**, texturas **máx. 2048** | Epic MetaHuman docs |
| Avatar de plataforma masiva multiplataforma | Roblox: **10,742 tris** por avatar completo (cabeza 4k, torso 1,750, extremidades 1,248 c/u) | Roblox Creator Docs |

### Tiers (ORIENTATIVO — derivado, verificar en el device real con profiler)

No existe un estándar publicado "gama baja = X tris". Esta tabla es un punto de arranque; el número final sale del profiler sobre el teléfono objetivo [ver: unity-movil-rendimiento].

| Tier | Perfil aprox. | FPS objetivo | Tris/frame (orientativo) | Texturas base | Materiales/personaje | Sombras |
|---|---|---|---|---|---|---|
| **Baja** | Android 2-3 GB RAM, GLES3, Mali/Adreno viejo | 30 | ~100-200k | ≤1024 | 1 | Ninguna realtime (baked/blob) |
| **Media** | El grueso del mercado; Vulkan | 30-60 | ~200-400k (ancla: Armies 210k @30) | ≤2048 | 1-2 | 1 direccional baked; blob de contacto |
| **Alta** | Flagship, Vulkan/Metal 3 | 60 | mayor, aún lejos de PC | 2048 (4096 solo hero) | 2-3 | 1 realtime acotada posible |

Reglas de reparto móvil (heredadas y afiladas): **más objetos en pantalla → menos tris cada uno; 2-3 objetos → pueden ser densos** (Android). En primer plano el detalle, al fondo horneado en textura. El presupuesto por categoría se **congela en el style guide** antes de producir [ver: gamedev/arte-direccion] — el drift en móvil se paga en calor y en reviews de gama baja, no en un dip de FPS en tu flagship de dev.

### Memoria de texturas: lo primero que revienta en gama baja

Las texturas son el mayor consumidor de RAM [ver: texturizado/atlas-trim-optimizacion §7]. En móvil el presupuesto de RAM es duro y compartido con el SO. Números de la tabla de memoria (aritmética `W×H×bpp/8`, +33% con mips) [ver: texturizado/atlas-trim-optimizacion §6]:

| Tamaño | Sin comprimir (RGBA32) | ASTC 6x6 (3.56 bpp) | ASTC 8x8 (2.0 bpp) |
|---|---|---|---|
| 1024² | 4.00 MB | 0.45 MB | 0.25 MB |
| 2048² | 16.00 MB | 1.78 MB | 1.00 MB |

Un hero prop con 4 mapas a 2048 sin comprimir = **256 MB** (imposible en gama baja); los mismos en ASTC 6x6 con mips ≈ **9.5 MB**. **Nunca "None"; ASTC siempre en móvil** [ver: texturizado/atlas-trim-optimizacion §6].

## 3. Draw calls y materiales: LA restricción móvil (atlasing extremo)

En PC con SRP Batcher el conteo de materiales pesa menos [ver: texturizado/atlas-trim-optimizacion §2]. En móvil, con CPU débil y GPU tile-based, **cada draw call cuesta más caro en proporción**: la CPU prepara estado y el driver móvil es más lento. Colapsar materiales y mallas sigue siendo la palanca #1.

| Palanca móvil | Qué hace | Detalle |
|---|---|---|
| **Un atlas para MUCHOS objetos** | Decenas de props chicos comparten 1 material → 1 draw call posible con instancing/batch | Atlas por bioma/kit, no por prop [ver: texturizado/atlas-trim-optimizacion §2] |
| **Trim sheet para arquitectura** | Un edificio entero con 1 textura; swap de material = 1 textura | Layout de franjas idéntico entre materiales [ver: texturizado/atlas-trim-optimizacion §3] |
| **1 material por personaje** | Skin + ropa + accesorios en un atlas → un solo SetPass por char | La cara concentra el texel [ver: §4] |
| **Static/GPU batching** | Junta mallas estáticas/instanciadas | Verificar con Frame Debugger que SÍ juntó [ver: unity-movil-rendimiento] |
| **Sprite Atlas (2D/UI)** | Sin él cada sprite es su draw call | §8 |

Verificar SIEMPRE con Frame Debugger en el device: un atlas mal hecho (sRGB mezclado, padding insuficiente) no ahorra nada [ver: texturizado/atlas-trim-optimizacion §2]. El detalle de batching/SRP Batcher es de runtime [ver: unity-movil-rendimiento]; aquí la disciplina de ARTE: **producir para que quepan pocos materiales**, no arreglarlo en Unity después.

## 4. Texel density para pantallas chicas: el ojo no ve el detalle en 6"

La resolución no se elige "para que se vea bien" — se deriva de **texel density × tamaño en mundo × cuánto se acerca la cámara** [ver: texturizado/atlas-trim-optimizacion §5]. En móvil hay un factor extra: la **pantalla física es pequeña** (≈5-6.7") y la cámara de gameplay rara vez pega la nariz al asset. Menos resolución sirve, y el jugador no lo nota.

- **Baja la texel density base un escalón** respecto a PC para el mismo asset: lo que en PC va a 1024, en móvil suele ir a **512** sin pérdida perceptible a distancia de juego. 4096 **casi nunca** en móvil (16 MB/mapa en BC7; peor aún el bandwidth) [ver: texturizado/atlas-trim-optimizacion §5].
- **DPI alto NO significa subir texturas**: un panel de 460 ppi renderiza fino un sprite de UI, pero el asset 3D visto a distancia de gameplay no gana nada con más texels — gana con **texel density CONSISTENTE** entre vecinos (un prop a 512 px/m junto a otro a 2048 canta) [ver: pipeline/arte-a-unity].
- **Empieza bajo y sube solo si el DEVICE lo justifica**, comparando en la pantalla del teléfono, no en el inspector de tu Mac. El detalle de UV que hace posible bajar densidad sin sacrificar silueta vive en [ver: texturizado/uv-unwrapping].
- **Mip Streaming** con Memory Budget para escenas grandes; carga solo los mips que la cámara necesita [ver: texturizado/atlas-trim-optimizacion §7]. Mips **OFF en UI/2D pixel-perfect** (el +33% es puro desperdicio a resolución nativa).

Orientación de resolución por rol (ORIENTATIVO — el número real sale de la texel density del set y de la cámara; verificar en device):

| Rol del asset en móvil | Resolución típica | Notas |
|---|---|---|
| Prop chico / lejano / LOD | 128-256 | La cámara nunca se acerca |
| Prop estándar, mobiliario, tileable | 512 | El grueso del contenido; default sano móvil |
| Personaje jugable, hero prop, trim sheet | 1024 | Se ve a media distancia |
| Hero cinemático / superficie enorme | 2048 (4096 solo alta gama, hero único) | Se inspecciona de cerca; raro en móvil |

## 5. Shaders baratos que se ven caros

El principio móvil: **mover el coste de runtime a tiempo de autor**. Todo lo que se pueda hornear en la textura no se paga por píxel cada frame. El detalle de implementación de shaders está en [ver: unity-movil-graficos]; aquí la decisión de ARTE.

| Técnica | Qué es | Por qué rinde en móvil |
|---|---|---|
| **Baked lighting en la textura** | Luz, AO y sombra suave pintados/horneados en el albedo; lightmaps para estático | Cero coste de iluminación realtime; Unity lo recomienda ("bake lighting and shadows", limitar luces per-pixel realtime) |
| **Unlit / Mobile shaders** | Sin cálculo de luz por píxel; el color ya trae la luz | Unity: elegir categorías de shader **"Mobile" o "Unlit"** de fábrica |
| **Matcap (material capture)** | Una esfera pre-iluminada muestreada por la normal de vista; da metal/plástico "caro" con 1 textura y sin luces | 1 sample, 0 luces — look pulido en gama baja |
| **Gradientes / vertex color** | Ramp por altura/normal, tinte por vértice | Casi gratis (por vértice); variación sin texturas nuevas [ver: texturizado/atlas-trim-optimizacion §4] |
| **Vertex lighting** | Iluminación por vértice, no por píxel | Barato en TBDR; suficiente para low-poly |
| **Precisión half/mediump** | `float16`/mediump en el fragment donde no se note | Menos ALU y bandwidth; Android usa float16/SNORM en datos de vértice (vertex-data-management) |

Reglas de arte para shader barato:
- **Sombras realtime = lujo**. En gama baja, cero; usa un **blob shadow** (quad con textura suave) o sombra horneada.
- **Transparencias apiladas son el enemigo #1 del fill rate** (overdraw): vegetación, humo, UI translúcida. En TBDR el overdraw quema bandwidth = batería y calor. Menos capas alpha, alpha-test antes que alpha-blend donde se pueda [ver: modelado/presupuestos-poligonos §2].
- **Emisión y color en vez de post-proceso**: bloom/DOF caros; muchas veces un gradiente y emisión en la textura dan el mismo golpe visual sin el pase de pantalla completa.

## 6. LODs móviles y culling agresivo

Los LODs, ratios ~50% e impostors son genéricos [ver: modelado/presupuestos-poligonos §4-5]. El ángulo móvil:

- **LODs más tempranos y más agresivos**: en pantalla chica un LOD1 entra sin que el ojo lo pille; sube el LOD Bias por tier (gama baja = LODs antes) [ver: unity-movil-rendimiento].
- **Culling sin piedad**: occlusion culling + distancias de cámara cortas. Level design que **limita líneas de visión largas** compra más presupuesto que cualquier optimización de mesh [ver: modelado/presupuestos-poligonos §7]. En móvil esto es doblemente cierto por el binning pass.
- **Billboard/impostor como último LOD** para vegetación y objetos repetidos: 2 tris + 1 material, y sobre todo **corta las capas de overdraw** de la vegetación, que es el coste real [ver: modelado/presupuestos-poligonos §5].
- **Multitud a cientos de tris, no miles**: la referencia real es **~360 tris** por unidad (Armies) + impostor a distancia + animación barata (vertex animation textures).
- **Degradar limpio con Adaptive Performance**: el arte debe soportar que en caliente se baje resolución, LOD bias y densidad de partículas sin romperse. Diseña los assets para que se vean bien también en su versión degradada [ver: unity-movil-rendimiento].
- **Mesh LOD de Unity 6**: auto-LOD al importar (mitad de índices por nivel) pero **NO reduce el coste de deformación** de skinned meshes; personajes siguen necesitando su presupuesto real [ver: modelado/presupuestos-poligonos §6].

## 7. Estilos que rinden en móvil: por qué domina lo estilizado

El **qué** estético (emoción, pilares, estilo×equipo) lo decide [ver: gamedev/arte-direccion]; aquí el **por qué técnico** de que low-poly / flat / cartoon / cel dominen el móvil:

| Razón | Detalle |
|---|---|
| **Coste de producción** | El realista exige normal maps de alta densidad, PBR de 4-5 mapas, retopo fino; el estilizado resuelve con color plano + baked light + pocos materiales. Un dev solo o equipo chico no sostiene un bestiario realista [ver: gamedev/arte-direccion §3] |
| **Coste de runtime** | Flat/unlit/matcap = shaders baratos (§5); menos texturas = menos memoria y bandwidth; siluetas limpias = menos tris para leerse |
| **Pantalla chica** | A 6" el detalle de poro/microsuperficie **no se percibe**; el contraste de silueta y color sí. El estilizado lee mejor en móvil que el realista, que se vuelve papilla gris |
| **Uncanny valley evitado** | El realista a medio presupuesto se ve peor que un estilizado bien hecho; el estilizado envejece mejor y perdona la gama baja |
| **Batching** | Paletas cerradas + pocos materiales = atlasing y batching triviales (§3) |

**Antipatrón:** intentar "realista AAA en el bolsillo". Salvo estudio con presupuesto de flagship y escalado por tier, el realista en móvil consume el doble de arte para verse peor en gama baja. La decisión de estilo es también una decisión de **presupuesto y de mercado** [ver: gamedev/generos], [ver: mercado-movil].

## 8. Arte 2D para móvil

Los fundamentos 2D (PPU, resolución interna, paleta, ramps) son genéricos [ver: arte-2d/fundamentos-2d]; el import a Unity (Pixel Perfect Camera, Sprite Atlas, Tilemap) en [ver: arte-2d/2d-a-unity]. El ángulo móvil:

- **Sprites a la resolución de pantalla móvil, no de PC**: autoría a 1× para el tamaño físico real en el teléfono. Un sprite que se ve fino en un monitor 27" puede estar sobre-resuelto (memoria desperdiciada) para 6". Escala solo por **múltiplos enteros** con Filter Mode = Point en pixel art [ver: arte-2d/fundamentos-2d §3].
- **Sprite Atlas obligatorio**: sin él, cada sprite de UI/personaje es un draw call — letal en el HUD móvil. Junta el HUD entero en 1-2 atlas [ver: texturizado/atlas-trim-optimizacion §2], [ver: arte-2d/2d-a-unity].
- **UI escalable multi-densidad**: los teléfonos van de ~320 dp a tablets; el arte de UI debe escalar sin pixelarse ni romper layout. Entrega iconos en **potencias de 2** y deja que el Canvas Scaler maneje la densidad; para elementos con esquinas, **9-slice** en vez de sprites por tamaño [ver: arte-2d/ui-2d-arte], [ver: ux-ui/mobile-ux].
- **Mips OFF en sprites de UI** a resolución nativa; ON solo si el sprite se ve a escalas variables en mundo [ver: texturizado/atlas-trim-optimizacion §7].
- **Cutout/esqueletal (Spine/2D Animation)** para amortizar volumen de animación con equipo mínimo, o el pipeline **3D→sprites** (Dead Cells) [ver: arte-2d/fundamentos-2d §2].

## 9. UI/HUD para dedos y pantallas chicas

La UX de interacción (feedback, gestos, jerarquía de HUD) es [ver: ux-ui/mobile-ux]; aquí las **restricciones físicas** que gobiernan el ARTE de UI móvil.

| Restricción | Número / fuente | Consecuencia de arte |
|---|---|---|
| **Touch target mínimo Android** | **48×48 dp** (Material / Android Accessibility) ≈ 9 mm físicos | Botones e iconos tocables nunca por debajo; el arte se diseña a ese tamaño mínimo |
| **Touch target mínimo iOS** | **44×44 pt** (Apple HIG, cifra canónica de larga data) | Igual: el hit target manda sobre el tamaño visual del icono |
| **Espacio entre targets** | Separación suficiente para no tocar el vecino | No apiñar el HUD; márgenes generosos |
| **Safe areas / notch / Dynamic Island / home indicator** | `Screen.safeArea` en Unity; cutout de Android | HUD crítico DENTRO del safe area; fondo puede sangrar detrás del notch, botones no [ver: unity-movil-input-servicios], [ver: ux-ui/mobile-ux] |

Zonas de la pantalla (teléfono en vertical, una mano) — dónde vive cada elemento de arte:

| Zona | Alcance del pulgar | Qué poner ahí |
|---|---|---|
| Borde inferior (izq/der) | Cómodo | Botones de acción frecuentes, joystick virtual, disparo |
| Centro-inferior | Fácil | Acción principal, confirmar |
| Centro | Estirando | Contenido de juego; evitar botones críticos |
| Franja superior | Difícil (dos manos) | Info pasiva: vida, score, timer, moneda |
| Esquinas superiores | Muy difícil | Pausa/menú (poco frecuentes), dentro del safe area |

Reglas de arte para HUD móvil:
- **No saturar**: el pulgar tapa parte de la pantalla; el dato crítico va donde no lo cubra la mano. Menos elementos, más grandes.
- **Contraste intocable**: el HUD compite con luz solar directa y pantallas sucias. Valor y contraste altos, no colores lavados.
- **Zona del pulgar**: acciones frecuentes en los bordes inferiores alcanzables; info pasiva arriba [ver: ux-ui/mobile-ux].
- **Cero overdraw de UI**: paneles translúcidos apilados queman fill rate (§5); apunta a los **2-3 ms de UI** (Android). Atlas + 9-slice + sin capas alpha innecesarias.
- **Autodescriptiva y en el idioma del usuario**, sin siglas [ver: ux-ui/mobile-ux].

## 10. El pipeline con presupuesto móvil desde el modelado

El presupuesto móvil no se "arregla" al final: se **modela con él desde el vértice**. El mapa maestro del pipeline de un asset 3D es [ver: pipeline-assets/pipeline-completo-3d] y el detalle de importación a Unity es [ver: pipeline/arte-a-unity]; aquí lo específico de móvil, con números de la guía de vértices de Android (tile-based GPU).

| Decisión desde el modelado | Ganancia móvil (fuente: Android vertex-data-management) |
|---|---|
| **Comprimir posiciones** a `float16`/SNORM16 (vec3, 6 B) en vez de float32 (16 B) | Menos bandwidth de vértice; precisión degrada >±1024 → **partir mallas grandes en chunks** |
| **Normales octaédricas** (vec2 SNORM8, 2 B) vs vec3 float32 (12 B) | **-83%** en normales; tangent space como quaternion QTangent (8 B) |
| **UVs a UNORM16** (4 B) si están en [0,1] | -50%; ojo con UVs que hacen wrapping |
| **Vertex stream splitting** (posición contigua aparte del resto) | El binning pass del TBDR solo lee posición: hasta ~5 posiciones por línea de caché de 32 B comprimidas |
| **16-bit index buffers siempre** | Trocear meshes bajo **65,535 verts** [ver: modelado/presupuestos-poligonos §1] |
| **Evitar SSCALED**; usar SNORM | No bien soportado en móvil; SNORM cuesta ALU despreciable |
| Combinado (compresión + stream split) | De 48 B/vértice a **~8-19 B**; hasta **-50% de bandwidth** de memoria de vértice |

Traducción para el artista: **alinear UV seams / hard edges / cambios de material** sobre los mismos edges (cada corte desalineado duplica vértices [ver: modelado/presupuestos-poligonos §1]) pesa el doble en móvil, porque cada vértice extra es bandwidth en el binning pass. Y **1 material por asset + atlas** no es una optimización opcional: es la condición de entrada. La spec de entrega (tris por tier, texturas ≤ tope, nº materiales, texel density, canales del pack) se **congela el día 1** y se verifica EN el device con el profiler [ver: pipeline/arte-a-unity], [ver: texturizado/atlas-trim-optimizacion §8].

### Runbook: aprobar un asset para móvil

1. **Clasificar y leer el renglón del style guide** (tier objetivo + categoría). Si no existe, derivarlo de las tablas del §2 y congelarlo antes de producir.
2. **Modelar el LOD0 al caso de uso extremo**: la distancia mínima real de cámara en el teléfono, ni un loop más. Concentrar densidad en cara/manos/zona focal; hornear el resto.
3. **Comprimir el vértice desde el DCC**: posiciones float16/SNORM, normales octaédricas, UVs UNORM16, index 16-bit (trocear <65,535), stream splitting si el exportador lo permite (§10).
4. **1 material, atlas asignado**: el asset entra a un atlas de su set; nada de textura única salvo hero contado.
5. **Texturas por tier**: resolución del §4, ASTC (6x6 albedo, 5x5 normal), sRGB Off en datos, mips ON en 3D / OFF en UI, Read/Write Off [ver: texturizado/atlas-trim-optimizacion §6].
6. **LODs entregados en el FBX** (`_LOD0..n`), billboard/impostor como último nivel donde aplique (§6).
7. **Verificar EN el teléfono objetivo** (no en el editor): tris/verts contra el renglón, nº de draw calls con Frame Debugger, memoria de textura con Memory Profiler, y estabilidad tras 20-40 min en caliente. Fuera de presupuesto = se devuelve, no "se acepta por esta vez".

## Reglas prácticas

1. Presupuesta para el estado THROTTLED (teléfono caliente a los 40 min), no para el frío: deja ~20-30% de margen bajo el pico [Android: deterioro a 45-50 min].
2. Estratifica el presupuesto por tier (baja/media/alta); congela tris, texturas y materiales por categoría en el style guide ANTES de producir.
3. Ancla los números en lo verificado: Armies 210k tris/frame @30 FPS, multitud 360 tris, MetaHuman móvil ~4k verts, 65,535 verts/mesh; lo demás es orientativo, verificar en device.
4. Gama baja: texturas ≤1024, 1 material por personaje, cero sombras realtime (blob o baked). ASTC siempre; nunca "None".
5. Baja la texel density un escalón vs PC: lo que en PC va a 1024, en móvil suele ir a 512 sin pérdida perceptible a 6". 4096 casi nunca.
6. DPI alto no es licencia para subir texturas 3D; lo que importa es texel density CONSISTENTE entre vecinos.
7. Draw calls y materiales son LA restricción: un atlas para muchos objetos, trim para arquitectura, 1 material por personaje. Verifica el batch con Frame Debugger en el device.
8. Mueve el coste de luz a la textura: baked lighting, lightmaps, unlit/Mobile shaders, matcaps, gradientes, vertex color. Sombras realtime = lujo.
9. Transparencias apiladas = overdraw = calor: menos capas alpha; alpha-test > alpha-blend; billboard/impostor corta el overdraw de vegetación.
10. LODs más tempranos y culling agresivo; sube LOD Bias por tier; limita líneas de visión largas en level design.
11. Diseña assets que se vean bien también DEGRADADOS (Adaptive Performance baja resolución/LOD/partículas en caliente).
12. Elige estilo estilizado/flat/low-poly por coste (producción + runtime) y porque lee mejor en pantalla chica; huye del realista AAA en el bolsillo salvo escalado por tier.
13. 2D: autoría a la resolución física del teléfono, Sprite Atlas obligatorio, UI multi-densidad con Canvas Scaler + 9-slice, mips OFF en UI nativa.
14. Touch targets: **48 dp** (Android) / **44 pt** (iOS) mínimo; el hit target manda sobre el tamaño visual del icono; no apiñar.
15. HUD dentro del safe area (`Screen.safeArea`), fuera de notch/Dynamic Island/home indicator; contraste alto para sol directo; zona del pulgar para acciones frecuentes.
16. Cero overdraw de UI; apunta a 2-3 ms de UI (Android): atlas + 9-slice + sin paneles translúcidos apilados.
17. Modela con presupuesto móvil desde el vértice: comprime posiciones (float16/SNORM), normales octaédricas, UVs UNORM16, stream splitting, 16-bit index (trocear <65,535).
18. Alinea seams/hard edges/cambios de material sobre los mismos edges: cada vértice extra es bandwidth en el binning pass del TBDR.
19. Memoria de texturas es lo primero que revienta en gama baja: audita con el Memory Profiler en el device, no en el editor.
20. Verifica TODO presupuesto en el teléfono objetivo con profiler; 60 FPS en tu Mac/flagship de dev no prueba nada para gama baja.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Aprobar el arte porque corre a 60 FPS los primeros 30 s en tu flagship | Presupuestar para el estado throttled y validar en gama baja tras 20-40 min (§1) |
| Copiar el poly budget de un juego de consola | Usar tiers móviles y las anclas con fuente (Armies 210k, 360 tris multitud, ~4k verts personaje) (§2) |
| Texturas 4096/2048 "para que se vea nítido" en móvil | Un escalón menos: 512 default sano; el ojo no ve el detalle a 6", y la RAM/bandwidth sí lo cobra (§4) |
| Un material por prop "porque SRP Batcher lo aguanta" | En móvil el draw call cuesta más caro; atlas + 1 material por asset es condición de entrada (§3) |
| Sombras realtime y transparencias apiladas en gama baja | Blob/baked shadows; menos capas alpha; alpha-test; billboard para vegetación (§5) |
| Iluminación PBR realtime en todo | Baked lighting en textura + unlit/matcap; luz per-pixel realtime al mínimo (§5) |
| Realista AAA con presupuesto de equipo chico | Estilizado/flat/low-poly: más barato, envejece mejor, lee mejor en pantalla chica (§7) |
| Iconos de HUD "bonitos" de 30 px que nadie puede tocar | 48 dp / 44 pt mínimo de hit target; el arte se diseña a ese tamaño (§9) |
| HUD debajo del notch o pegado al home indicator | Respetar `Screen.safeArea`; solo el fondo sangra detrás del notch (§9) |
| Cada sprite de UI como su propio draw call | Sprite Atlas obligatorio; junta el HUD en 1-2 atlas (§8) |
| Confiar en el auto-LOD para el personaje principal | Mesh LOD no reduce deformación de skinned; héroe con LODs a mano y presupuesto real (§6) |
| Modelar sin pensar el vértice y "optimizar en Unity" | Comprimir posiciones/normales/UVs, stream splitting y trocear <65,535 desde el DCC (§10) |
| Meshes densas de un solo bloque | 16-bit index + chunks; float16 degrada precisión >±1024 → partir (§10) |
| Verificar el presupuesto en el editor de PC | Profiler + Memory Profiler + Frame Debugger en el teléfono objetivo (§2, §10) |

## Fuentes

Verificadas por fetch directo esta sesión (2026-07-20) salvo indicación:

- **Geometry optimization — Android Game Development guide (Google)** — límite 65,535 verts/16-bit, micro-triángulos <10 px², reducción LOD 50%, reparto por nº de objetos, y la demo Armies: ~210,000 tris/frame @ ~30 FPS, torretas ~3,000 tris, soldados de multitud ~360 tris.
- **Vertex data management — Android Game Development guide (Google)** — compresión de vértices en GPU tile-based: posiciones float16/SNORM16 (16→6 B), normales octaédricas SNORM8 (12→2 B, -83%), QTangent (8 B), UVs UNORM16, vertex stream splitting (binning solo lee posición), SSCALED no soportado, combinado 48→~8-19 B (hasta -50% bandwidth), datos de un Pixel 4 sobre escena de ~19M verts.
- **Performance overview / profiling — Android Game Development guide (Google)** — deterioro de framerate a los 45-50 min por thermal throttling; meta de UI 2-3 ms por frame; tamaño de buffer de trace 10-15 MB por core.
- **Reduce the size of touch targets — Android Accessibility Help (Google)** — mínimo recomendado 48×48 dp (≈9 mm), remitido a las guías de Material Design.
- **Optimizing graphics performance — Unity Manual (6000.2)** — bake de lighting/shadows (lightmapping), limitar luces per-pixel realtime, elegir shaders de categoría "Mobile"/"Unlit", overdraw draw mode, mipmaps por distancia, compresión de textura, LOD, "don't use more triangles than necessary", OnDemandRendering, profilar antes de optimizar.
- **Adaptive Performance — Unity package docs** — feedback de estado térmico/energético del dispositivo para mantener framerates constantes por más tiempo y prevenir thermal throttling (base para degradar calidad/LOD/resolución en caliente).
- **Human Interface Guidelines — Apple (Layout / Accessibility)** — mínimo de touch target 44×44 pt. Cifra canónica y de larga data de Apple; la página HIG es JS-rendered y no se extrajo su cuerpo por WebFetch esta sesión — el número no es un dato nuevo de esta sesión sino el estándar establecido de Apple.

Cruzadas desde bases hermanas (sus fuentes primarias están citadas allí, no reproducidas aquí):
- [ver: modelado/presupuestos-poligonos] — poly budgets, LODs ratio 50%, impostors/billboards, 65,535 verts, MetaHuman móvil (LOD3 ~4k verts, tex 2048, Epic docs), Roblox 10,742 tris (Roblox Creator Docs), Meta VR budgets, splits de vértice.
- [ver: texturizado/atlas-trim-optimizacion] — ASTC bpp y tablas de memoria (Unity GPU texture formats reference), atlas/trim/tileable, channel packing, mip streaming, POT.
- [ver: arte-2d/fundamentos-2d] — PPU, resolución interna, paleta, Sprite Atlas, Pixel Perfect Camera (Unity/Aseprite/Lospec verificados allí).

**Gaps honestos:** no hay estándar publicado único de "tris/frame por gama de móvil" — los tiers del §2 son derivados/orientativos, a verificar con profiler en el device real. Arm Mali GPU Best Practices (mediump/lowp, overdraw, MSAA en TBDR) no se pudo extraer esta sesión (página JS-rendered / doc bloqueada); su contenido de precisión de shader se apoya en la guía de vértices de Android y se profundiza en [ver: unity-movil-graficos]. Benchmarks de mercado (CPI, retención, ARPDAU, cuota por gama de device) NO van en este archivo de arte: viven en [ver: mercado-movil] y [ver: monetizacion-movil] con su fuente.
