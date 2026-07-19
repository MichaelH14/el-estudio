# Presupuestos de polígonos y LODs

> **Cuando cargar este archivo:** al fijar el poly budget de un asset o de una escena completa, decidir cuántos LODs hacer y con qué ratios, evaluar si un modelo "pesa demasiado", o presupuestar geometría para móvil/PC/VR antes de modelar. Complementa los specs de entrega de [ver: pipeline/arte-a-unity] y el style guide de [ver: gamedev/arte-direccion].

## 1. El número que de verdad cuenta: triángulos y vértices del engine

- **"Polígono" = triángulo.** Cuando un artista de juegos dice poly count quiere decir triangle count: el hardware gráfico solo procesa triángulos; todo quad/n-gon se triangula al exportar (polycount wiki). El contador de la herramienta de modelado en modo "polys" siempre miente por lo bajo — contarlo SIEMPRE en triángulos [ver: fundamentos-3d].
- Los quads se conservan durante el modelado (edge loops, skinning limpio [ver: topologia]) y se triangulan al final. Ojo: cada quad puede triangularse en dos diagonales distintas ("ridge" o "valley"); revisar el modelo EN el engine y triangular a mano donde el shading lo exija, y **triangular antes del bake** de normal maps para que la iluminación no zigzaguee [ver: high-to-low].
- **El vertex count real importa más que el triangle count** para memoria y coste de transformación (polycount wiki). Y el vertex count del engine NO es el de la herramienta:

| Qué duplica vértices | Por qué |
|---|---|
| UV seams | Un vértice con 2 coordenadas UV se parte en 2 |
| Hard edges / smoothing splits | Cada normal distinta en el mismo punto = vértice extra |
| Cambio de material en la superficie | "Un vértice no puede compartirse entre materiales" (Provost) |

- Provost ("Beautiful, Yet Friendly"): en el pipeline real los vértices "se parten y se re-parten", quedando típicamente en **2-3× el conteo de la herramienta**. El antídoto: **alinear** los cortes — donde haya hard edge, poner el UV seam en el mismo edge; donde cambie el material, que coincida con seam y hard edge. Tres cortes alineados cuestan 1 split, desalineados cuestan 3.
- Ejemplo aritmético (consecuencia directa de las reglas de split): un cubo son 8 vértices en el DCC, pero con sus 6 caras en hard edge cada esquina necesita 3 normales distintas → **24 vértices para el engine** (3×). El mismo cubo todo suavizado con una isla UV continua se queda cerca de 8+costuras. Un cilindro facetado (hard edges en cada lado) duplica el perímetro completo; suavizado, no.
- Relación vértices↔triángulos para convertir presupuestos mentalmente: en una superficie cerrada y soldada hay ≈2 triángulos por vértice (1 tri = 3 verts, 2 tris = 4, 4 tris = 6… la proporción tiende a 2:1, polycount wiki); los splits del engine empujan la relación real hacia 1:1. Por eso "24k vértices" de una cabeza MetaHuman y "~30-50k tris" de un personaje AAA describen la misma escala.
- Consecuencia práctica: un low-poly "de 10k tris" con UVs de confeti y smoothing caótico puede costar más que uno de 15k limpio. El presupuesto se audita con el conteo de vértices/tris **del engine** (Unity: inspector del mesh importado / Frame Debugger), nunca con el del DCC.
- Límite duro heredado de índices de 16 bits: **65,535 vértices por mesh** es el máximo garantizado en GPUs móviles (Android dev guide). Pasarse fuerza índices de 32 bits (más memoria y ancho de banda) o partir el mesh.
- ¿Cuántos lados a un cilindro, cuántos cortes a una curva? No hay número mágico: la densidad se decide por el **tamaño en pantalla de la silueta** a la distancia real de juego — justo la suficiente para que la curva no se lea facetada, y ni un loop más (es la misma lógica del umbral de micro-triángulos del §2). Bevel/redondez solo donde la silueta o el specular lo muestran; el interior plano no paga detalle [ver: hard-surface] [ver: topologia].

## 2. Por qué el polycount importa menos que antes — y cuándo SÍ importa

El dato que resume el cambio de era (fuente primaria: tweet del director de Horizon Zero Dawn, Mathijs de Jonge, 2015): **un solo Thunderjaw en PS4 son 550k polígonos; Killzone 3 en PS3 usaba 250k como máximo para TODO lo que había en pantalla**. El vertex processing se volvió barato; el cuello de botella se movió.

Dónde está el coste real hoy:

| Coste | Qué es | Fuente |
|---|---|---|
| **Draw calls / render state** | Por cada mesh+material la CPU prepara y envía estado (shaders, texturas, buffers) al GPU. Miles de draw calls ahogan la CPU aunque los meshes sean simples. Antídotos en Unity: SRP Batcher, GPU instancing, batching, GPU Resident Drawer | Unity Manual "Optimizing draw calls" |
| **Materiales por asset** | Cada material extra = draw call + estado extra + rompe batching. 1 material por prop, trim sheets para entorno | [ver: pipeline/arte-a-unity §7], [ver: entornos-modulares] |
| **Overdraw / fill rate** | Coste = píxeles cubiertos × complejidad del shader × densidad de texel; capas transparentes solapadas (vegetación, VFX) lo disparan | Provost pt. 2 |
| **Memoria y ancho de banda** | Más vértices = más datos al GPU cada frame; en móvil eso es batería y thermal throttling | Android dev guide |

Cuándo el polycount SÍ sigue importando:

1. **Micro-triángulos**: triángulos de 1-10 píxeles en pantalla. El GPU los procesa enteros aunque casi no aporten imagen; regla de Google: **mantener los triángulos por encima de ~10 px² en la imagen final**. Un modelo denso visto de lejos sin LOD es una fábrica de micro-triángulos.
2. **Aliasing geométrico (crítico en VR)**: mucha densidad de triángulos en pocos píxeles = bordes que hormiguean; los LODs reducen aliasing además de coste (Arm, Real-Time 3D Art Best Practices VR).
3. **Skinned meshes**: cada vértice de un personaje animado se deforma por CPU/GPU cada frame; el skinning no se abarata con batching, y el Mesh LOD de Unity no reduce el coste de deformación (§7).
4. **Multi-pass**: sombras (cada shadow map re-dibuja la geometría), reflejos, depth prepass — el mismo mesh se paga varias veces por frame.
5. **Plataformas tile-based (móvil/Quest)**: la geometría se procesa por tile; el vertex count pega más fuerte que en desktop.
6. **Triángulos largos y finos**: más caros de rasterizar que los cercanos a equiláteros (Android dev guide) — otra razón para topología pareja [ver: topologia].

Diagnóstico rápido — ¿es la geometría o es otra cosa? (aplicando Provost con el profiler):

| Síntoma | Cuello probable | Primera acción |
|---|---|---|
| FPS cae al mirar zonas con MUCHOS objetos, aunque sean simples | Draw calls (CPU) | Frame Debugger: contar draw calls; batching/instancing/atlas |
| FPS cae al acercarse a transparencias (vegetación, humo, vidrio) | Overdraw / fill rate | Ver overdraw; reducir capas alpha solapadas |
| FPS cae con muchos personajes animados en pantalla | Skinning + vértices | LODs con menos huesos/influencias; multitud con presupuesto propio |
| FPS cae solo cuando un mesh denso llena la pantalla o se ve de lejos | Geometría (micro-tris / vertex) | LODs con saltos reales; revisar splits de vértices |
| FPS estable pero memoria al límite | Texturas casi siempre, buffers de mesh después | Auditar texturas antes de tocar geometría |

Regla mental: **el polycount es UN renglón del presupuesto, junto a draw calls, materiales, overdraw y memoria.** Un asset entra en presupuesto cuando cumple los cinco, no cuando "tiene pocos polys".

## 3. Órdenes de magnitud reales (números con origen)

### Evolución histórica (todos triángulos, con fuente declarada)

Recopilación de Rick Stirling (artista de industria; trabajó en GTA San Andreas — números propios, de libros oficiales o de modelos extraídos):

| Juego (año, plataforma) | Asset | Tris |
|---|---|---|
| Quake (1996, PC) | Personaje | 200 (+textura 320×200 8-bit) |
| Half-Life (1998, PC) | Zombie | 844 (HD pack: 1,700) |
| Unreal Tournament (1999, PC) | Personaje jugable | 800 |
| Halo (2001, Xbox) | Master Chief | 2,000 |
| Wind Waker (2002, GC) | Link | 2,800 |
| GTA San Andreas (2004, PS2) | Protagonistas / NPCs | 2,000 / 1,200 (texturas 256×256 / 256×128) |
| Half-Life 2 (2004, PC) | Alyx / soldado Combine / headcrab | 8,323 / 4,682 / 1,690 |
| Half-Life 2 (2004, PC) | SMG / pistola (1ª persona con brazos) | 2,854 / 2,268 |
| Resident Evil 4 (2005, GC) | Leon | 10,000 |
| Gears of War (2006, X360) | Marcus / Boomer | 15,000 / 11,000 (diffuse+spec+normal) |
| Twilight Princess (2006, GC/Wii) | Link | 6,900 |
| PGR2 (2003, Xbox) → PGR3 (2006, X360) | Vehículos | 10,000 → 80,000-100,000 |
| Uncharted 1 (2007, PS3) | Drake / piratas | ~30,000 / ~12,000-15,000 |
| UT3 (2007, PC) | Armas en 1ª persona | 4,500-12,000 |

### Era PS4/PS5 y actual (fuentes primarias)

| Dato | Números | Fuente |
|---|---|---|
| Thunderjaw, Horizon Zero Dawn (PS4) | 550,000 polys un solo robot (24×9 m); todas las máquinas del juego con detalle equivalente | Tweet del director M. de Jonge (Guerrilla), 2015 |
| Killzone 3 (PS3), referencia | 250,000 polys máximo para el frame completo | Mismo tweet |
| Evolución facial oficial PlayStation | Kratos: 1,200 (PS2) → 5,700 (PS3) → 32,000 (PS4, God of War 2018) polys solo la cara. Kazuya (Tekken): ~100 (PS1) → 6,000 la cabeza con pelo (PS4). Rathalos: 1,390 → 11,274 facial | PlayStation Blog oficial, 2019 |
| MetaHuman (Epic, actual) | Cabeza LOD0 = 24,000 **vértices** (669 blendshapes, 713 joints); cuerpo LOD0 = 30,500 vértices. Cadena de 8 LODs hasta 130 vértices | Docs oficiales MetaHuman |
| Nanite (UE5) | Meshes "calidad film" de millones de tris sin LODs de autor — pero no aplica a Unity (§7) | Docs Epic |

Lectura: un protagonista AAA actual anda en las decenas de miles de tris con la densidad concentrada en la cara (32k solo el rostro de Kratos), y las criaturas-jefe llegan a cientos de miles. La cara consume una fracción enorme del presupuesto del personaje porque es donde mira el jugador [ver: organico-personajes].

### Presupuestos por plataforma publicados (2025-2026)

| Plataforma | Presupuesto oficial | Fuente |
|---|---|---|
| **Quest 2 / Quest Pro** | 750k-1M tris/frame; 80-200 draw calls con simulación pesada, hasta 400-600 con simulación ligera; 72 FPS mínimo | Meta Horizon developer docs |
| **Quest 3 / 3S** | 1.3M-1.8M tris/frame; 200-300 draw calls con simulación pesada, hasta 700-1,000 con simulación ligera | Meta Horizon developer docs |
| **Móvil Android (referencia)** | Demo Armies (RTS con multitudes): ~210k tris/frame a 30 FPS; torretas ~3,000 tris; personajes de multitud ~360 tris | Android developers, guía de geometría |
| **Móvil (personaje "premium")** | MetaHuman en móvil: "best LOD" = LOD 3 ≈ 2,500 verts cabeza + 1,507 cuerpo (~4k verts total); texturas máx. 2048 | Docs MetaHuman |
| **Roblox (UGC, referencia de plataforma masiva)** | Avatar completo: 10,742 tris repartidos — cabeza 4,000, torso 1,750, cada extremidad 1,248 | Roblox Creator Docs |
| **PC/consola actual** | NO existe un número oficial único por asset; se deriva del frame budget (§8). Anclas reales: tabla anterior | — |

### Guía derivada por tipo de asset (síntesis de las fuentes de esta página — NO es un estándar publicado)

Rangos para arrancar un proyecto; el número final lo fija el frame budget (§8) y el estilo [ver: gamedev/arte-direccion]:

| Asset | Móvil | PC/consola estilizado-mid | PC/consola high-end | VR (Quest) |
|---|---|---|---|---|
| Protagonista | 4k-15k | 20k-50k | 50k-150k | 10k-30k |
| NPC / enemigo común | 1k-8k | 10k-30k | 20k-60k | 5k-15k |
| Personaje de multitud | 300-2k | 2k-10k | LODs/impostors (§6) | 1k-5k |
| Arma 1ª persona (con brazos) | 2k-6k | 10k-30k | 30k-80k | 5k-20k |
| Prop pequeño (taza, botella) | 50-300 | 200-1k | 500-3k | 100-500 |
| Prop hero (interactuable, se ve de cerca) | 500-3k | 2k-10k | 5k-30k | 1k-5k |
| Vehículo jugable | 5k-20k | 40k-100k | 100k-300k+ | 10k-40k |
| Módulo de entorno (muro, esquina) | 100-1k | 500-5k | 2k-20k | 200-2k |

Reglas de reparto que sí están publicadas: más triángulos a lo que está en primer plano, menos al fondo; si hay muchos objetos en pantalla, menos tris cada uno; si solo hay 2-3 objetos, pueden ser densos (Android dev guide). El presupuesto por categoría se congela en el style guide antes de producir [ver: gamedev/arte-direccion §2].

## 4. LODs: niveles, ratios, generación

### Cuántos niveles y qué ratio

- **Ratio estándar: ~50% de tris por nivel.** Lo recomienda Google para móvil y es exactamente lo que hace el generador de Mesh LOD de Unity ("cada LOD contiene aproximadamente la mitad de índices que el anterior"). La cadena MetaHuman lo ilustra: 24k → 12k → 6k → 2.5k → 1.3k → 560 → 270 → 130 vértices.
- **Cuántos**: props/entorno típicos, 2-3 niveles + Culled; héroes vistos a toda distancia, 3-4; sistemas extremos como MetaHuman llegan a 8. Cada nivel extra cuesta memoria y CPU de selección — "demasiado LOD cuesta CPU y memoria" (Android dev guide). Juego de cámara fija o objetos siempre a la misma distancia: **cero LODs** — no pagar lo que no se usa.
- **Los saltos deben ser notables**: LODs con poca diferencia de vértices no ahorran nada y siguen pagando selección + memoria (Arm VR guide).
- Los LODs también combaten el **aliasing geométrico**: menos densidad a distancia = menos shimmer, clave en VR (Arm).
- Distancias/umbrales: en Unity el LOD Group cambia por **% de altura del objeto en pantalla**, no por metros — detalles de configuración, naming `_LOD0..n` y crossfade en [ver: pipeline/arte-a-unity §7].
- En cada LOD bajan JUNTOS: tris, huesos activos e influencias de skin (MetaHuman: 713 joints en LOD0 → 26 en LOD7; 12 influencias → 4), y resolución de material/textura si el sistema lo permite.

### Automática vs manual

| Método | Cuándo | Limitaciones |
|---|---|---|
| **Generación automática** (Mesh LOD de Unity al importar, decimadores de DCC, herramientas tipo Simplygon) | Props, rocas, entorno, follaje — el 90% del contenido | Colapsa edges sin entender la silueta ni las UVs críticas; falla en formas muy curvas o piezas desconectadas (docs Unity) |
| **LOD manual / retopo dirigido** | Héroes, armas en 1ª persona, siluetas icónicas, hard-surface con bordes que no pueden colapsar [ver: hard-surface] | Caro; reservarlo para lo que el jugador mira fijo |
| **Híbrido** | Generar automático + retocar a mano LOD1 (el más visto después del 0) | El sweet spot habitual |

- Regla de producción: los LODs se entregan CON el asset (nombrados en el FBX); "los agrego después" = nunca existen [ver: pipeline/arte-a-unity §7].
- El LOD0 no es el high-poly: es el low-poly de juego ya optimizado [ver: high-to-low]. Los LODs se generan desde el LOD0, no desde el sculpt.
- Transiciones: crossfade/dithering para matar el "pop"; probar la distancia de cambio con la cámara real del juego — un pop visible a distancia de gameplay significa umbral mal puesto o salto de silueta demasiado brusco.

## 5. Impostors y billboards: vegetación, multitudes, fondo

- **Billboard**: "un objeto 2D texturizado que rota para mirar siempre a la cámara" (Unity Manual). 2 triángulos. Es el último LOD antes de Culled para árboles, arbustos y objetos lejanos: bosque cercano en 3D, bosque lejano en billboards. En Unity: Billboard Renderer + Billboard Asset dentro del LOD Group (URP y Built-in; en HDRP solo vía VFX Graph) [ver: pipeline/arte-a-unity].
- **Impostor**: evolución del billboard — en vez de una sola vista, un atlas con el objeto renderizado desde muchos ángulos (variante estándar: distribución octaédrica de vistas, popularizada por Ryan Brucks/Epic); el shader elige y mezcla las vistas según el ángulo de cámara, a menudo con normales/depth para recibir luz. Paralaje y luz creíbles a coste de 2 tris + 1 material. Herramientas listas para Unity existen (p.ej. Amplify Impostors) — el detalle de implementación es de la fase Unity, aquí basta saber CUÁNDO usarlos: cientos de instancias del mismo objeto a media/larga distancia.
- **Multitudes**: número real — los personajes de multitud del demo Armies son **~360 tris** cada uno (Android dev guide). El patrón profesional: pocos LODs de mesh cerca, impostor/billboard lejos, y para masas enormes vertex animation textures o sistemas dedicados (MetaHuman Crowds hace exactamente eso: generación de assets optimizados + gestión de LOD + animación a escala).
- La vegetación es el caso extremo de overdraw: capas de alpha solapadas. El billboard/impostor no solo baja tris — baja capas transparentes apiladas, que era el coste real (Provost, §2).

## 6. Nanite, virtualized geometry y el Mesh LOD de Unity 6

### Qué cambia Nanite (UE5) — y por qué te importa aunque uses Unity

Nanite trocea el mesh en clusters jerárquicos y decide el detalle **por cluster en runtime**: el frame deja de estar "limitado por polycounts, draw calls y memoria de mesh" (docs Epic) y los LODs de autor desaparecen para geometría estática. Sus límites documentados: sin blend mode Translucent, sin forward rendering, **sin VR estéreo ni MSAA**, requiere DX12 + Shader Model 6, tope de 16M de instancias, y World Position Offset limitado. Conclusión honesta: Nanite redefine el presupuesto de geometría OPACA de entorno en PC/consola potente, pero no en VR, no en móvil, y no en Unity.

### Lo que tienes en Unity 6 (el stack objetivo)

| Tecnología | Qué hace | Qué NO hace |
|---|---|---|
| **Mesh LOD** (Unity 6.2+) | Genera LODs automáticos al importar ("Generate Mesh LODs" en el importer): cada nivel ≈ mitad de índices, guardados en el index buffer del mesh original (memoria máx. +100%, menos que meshes separados). Selección automática por tamaño en pantalla. Requiere ≥256 tris para arrancar; para al llegar a ~64 | No ajusta materiales por nivel (eso es del LOD Group); el crossfade exige GPU Resident Drawer; **ignora skin weights al simplificar y NO reduce el coste de deformación** de skinned meshes; incompatible con static batching/GPU instancing clásicos |
| **GPU Resident Drawer + GPU occlusion culling** | Baja drásticamente el coste CPU de draw calls de muchos objetos instanciados y descarta lo ocluido en GPU | No es Nanite: el mesh sigue siendo el que autoraste, con sus LODs |
| **SRP Batcher / instancing** | Reduce coste de estado entre draw calls de materiales que comparten shader | No junta materiales distintos: el presupuesto de materiales sigue vivo |

### Lo que estas tecnologías NO cambian (2026)

1. El **coste de autor**: esculpir/texturizar un asset de 2M tris sigue costando lo mismo en horas humanas; el bake high→low sigue siendo el pipeline [ver: high-to-low].
2. **Personajes animados**: el skinning se paga por vértice deformado; los presupuestos de personaje del §3 siguen vigentes en todos los engines.
3. **Memoria de texturas** — que suele reventar antes que la geometría.
4. **Móvil y VR**: los presupuestos de Meta y de la guía Android aplican tal cual; ahí se modela low-poly clásico con LODs.
5. La disciplina de **materiales y draw calls**: 1 material por prop y trim sheets siguen siendo la optimización más rentable [ver: entornos-modulares].

## 7. Presupuestar una escena completa: del frame budget al asset

Método (la aritmética es derivada; los techos, de las fuentes citadas):

1. **Fijar plataforma + FPS objetivo** → techo de tris/frame y draw calls. Quest 2: 750k-1M tris y 80-600 draw calls según cuánta CPU coma la simulación (Meta). Móvil mid: usar la referencia Armies (~210k a 30 FPS) como suelo conservador y perfilar en el device real. PC/consola: definir techo propio con la escena de peor caso y el profiler — no hay número oficial.
2. **Presupuestar la peor pantalla, no la media.** Lo que manda es el "visibility spectrum" (Provost): cuánto puede verse A LA VEZ desde el peor punto de vista. Level design que limita vistas largas compra más presupuesto que cualquier optimización de mesh.
3. **Repartir por categorías** y escribirlo en el style guide. Ejemplo de reparto sobre Quest 2 (aritmética de ejemplo sobre el techo oficial, no estándar publicado): protagonista+manos 30k · 6 NPCs × 15k = 90k · entorno visible 400k · props 150k · vegetación/VFX 80k ≈ 750k, dejando margen. Cada categoría recibe también presupuesto de **draw calls y materiales**, no solo de tris.
4. **Contar lo que está EN PANTALLA, no lo que existe**: con LODs bien hechos, un asset de 50k aporta 50k de cerca y 3k de lejos; el presupuesto de frame se calcula con los LODs a sus distancias reales de juego.
5. **Recordar los multiplicadores**: sombras/reflejos re-dibujan geometría; overdraw de transparencias; vertex count real 2-3× el del DCC (§1). El número de la hoja de cálculo es optimista por diseño.
6. **Verificar con instrumentos, no con fe**: profiler y Frame Debugger sobre el device objetivo; tris/frame, draw calls/frame y ms de CPU/GPU de render. La auditoría por asset (tris ≤ budget de su categoría, nº materiales, LODs presentes) está en [ver: pipeline/arte-a-unity §10].
7. Presupuesto que no se cumple → primero draw calls y materiales (lo más rentable), luego LODs/distancias de culling, y solo al final re-modelar assets.

### Runbook: fijar el presupuesto de un asset nuevo

1. Clasificar el asset (protagonista / NPC / prop / arma / vehículo / módulo de entorno) y leer su renglón en el style guide; si no existe, derivarlo de la tabla del §3 y congelarlo.
2. Determinar su caso de uso extremo: ¿a qué distancia mínima se ve y cuánto ocupa en pantalla? Eso fija el LOD0 (silueta y curvas sin facetar a ESA distancia, ni un loop más).
3. Repartir el presupuesto interno: cara/manos o zona focal reciben la mayor densidad; zonas ocultas o siempre lejanas, lo mínimo (gradiente de detalle, mismo principio que la jerarquía de lectura de [ver: gamedev/arte-direccion §5]).
4. Decidir la cadena de LODs ANTES de modelar: cuántos niveles, ratio ~50%, cuál será billboard/impostor. Modelar el LOD0 con topología que colapse bien [ver: topologia].
5. Fijar el resto del contrato: nº de materiales (ideal 1), texel density, y si lleva UV2/lightmap — todo en la spec de entrega [ver: pipeline/arte-a-unity §1].
6. Al entregar: verificar tris y vértices EN el engine contra el renglón del style guide; fuera de presupuesto = se devuelve, no "se acepta por esta vez" (el drift de presupuesto es acumulativo e invisible hasta que el frame se cae).

## Reglas prácticas

1. Cuenta SIEMPRE en triángulos, y audita el vertex count en el engine — el DCC miente en ambos.
2. Alinea UV seams, hard edges y cambios de material sobre los mismos edges: cada corte desalineado duplica vértices gratis.
3. Presupuesto por asset = tris + nº materiales + memoria de texturas + coste de skinning. Un solo renglón no aprueba el asset.
4. Congela el poly budget por categoría en el style guide ANTES del primer asset de producción [ver: gamedev/arte-direccion].
5. Máximo 65,535 vértices por mesh (índices de 16 bits); si lo pasas, parte el mesh o asume índices de 32 bits a conciencia.
6. Ningún triángulo por debajo de ~10 px² en pantalla a su distancia real de juego: si pasa, falta un LOD.
7. LODs: ~50% de tris por nivel, 2-3 niveles + Culled para props, con saltos notables; cámara fija = cero LODs.
8. En cada LOD bajan juntos tris, huesos e influencias de skin — no solo la malla.
9. LODs automáticos para el 90% del contenido; manuales solo para héroes, armas FP y siluetas icónicas; retoca a mano el LOD1.
10. Los LODs se entregan con el asset, nombrados `_LOD0..n` en el FBX [ver: pipeline/arte-a-unity §7].
11. Último LOD de vegetación y objetos repetidos lejanos: billboard o impostor (2 tris), nunca mesh.
12. Personajes de multitud: cientos de tris (no miles) + impostors a distancia; la referencia real es ~360 tris por unidad.
13. Concentra la densidad del personaje en cara y manos — es donde mira el jugador; la cara de un héroe AAA puede valer 32k ella sola.
14. En VR: techo oficial de Meta por headset (750k-1M Quest 2; 1.3-1.8M Quest 3), 72 FPS, y draw calls contados con la mano; los micro-triángulos además hacen shimmer.
15. Presupuesta la peor pantalla del juego, no la media; limitar líneas de visión largas compra más que optimizar meshes.
16. Cuenta los multiplicadores ocultos: sombras y reflejos re-dibujan la geometría; transparencias apiladas revientan el fill rate.
17. Nanite no existe en tu stack: en Unity 6 usa Mesh LOD + GPU Resident Drawer, y sigue modelando con presupuesto.
18. Mesh LOD de Unity no reduce el coste de deformación de skinned meshes: los personajes necesitan su presupuesto de verdad, no confianza en el auto-LOD.
19. Todo "cumple presupuesto" se verifica con profiler/Frame Debugger en el device objetivo — jamás a ojo ni solo en el editor.
20. Antes de re-modelar por performance, ataca draw calls y materiales: suele ser el 80% del problema con el 20% del esfuerzo.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Presupuestar con el conteo de "polys" del DCC | Contar triángulos y vértices en el engine; el real es 2-3× por splits |
| Obsesión con quitar 500 tris a un prop mientras la escena tiene 3,000 draw calls | El coste real está en draw calls/materiales/overdraw; perfilar antes de optimizar meshes (§2) |
| "El polycount ya no importa" como licencia para todo | Sigue importando en móvil, VR, skinned meshes, micro-triángulos y multi-pass (§2) |
| UVs fragmentadas y hard edges por todos lados "porque el bake sale mejor" | Cada seam/hard edge duplica vértices: alinearlos entre sí y solo donde hagan falta [ver: high-to-low] |
| Copiar el polycount de un juego AAA sin su plataforma ni su pipeline | Usar los techos de TU plataforma (§3) y derivar del frame budget (§8) |
| Números de foro sin origen como presupuesto | Solo cifras con fuente real (breakdowns oficiales, docs de plataforma); lo demás es mito |
| LODs "para después" | Se entregan con el asset en el FBX; después = nunca |
| 5 LODs casi idénticos en un prop de 800 tris | LODs solo con saltos notables; objetos ya baratos o a distancia fija no llevan |
| Pop visible al cambiar de LOD | Crossfade + revisar que el nivel siguiente conserve la silueta; umbral por % de pantalla bien puesto |
| Bosque completo en meshes 3D "porque los árboles son bonitos" | Billboard/impostor como último LOD; la vegetación mata por overdraw, no solo por tris |
| Multitud de NPCs con el mesh del protagonista | Presupuesto de multitud propio (cientos de tris) + impostors + animación barata |
| Confiar en el auto-LOD para el personaje principal | El generador ignora silueta y skin weights; héroes llevan LODs dirigidos a mano |
| "Con Nanite ya no hay presupuestos" (en un proyecto Unity) | Nanite es de UE5 y ni ahí cubre VR/translucencia; en Unity 6: Mesh LOD + GPU Resident Drawer + presupuesto clásico |
| Presupuestar la escena promedio | La peor pantalla define el frame budget; el jugador siempre encuentra el peor ángulo |
| Aprobar el presupuesto en el editor de PC | Profiler y Frame Debugger en el device objetivo; 60 FPS en el editor no prueba nada |

## Fuentes

- **Polygon Count — polycount wiki** (wiki.polycount.com) — canon del game art: polys vs triángulos, vertex count real vs triangle count, splits por UV/smoothing/materiales, e índice de recopilaciones históricas de counts.
- **Beautiful, Yet Friendly, partes 1 y 2 — Guillaume Provost** (Game Developer Magazine; hosteado en ericchadwick.com) — el texto fundacional sobre coste real del arte: transform-bound vs fill-bound, visibility spectrum, vértices que se parten 2-3×, fórmula del fill cost, alineación de seams.
- **Yes, but how many polygons? — Rick Stirling, rsart.co.uk 2007** (vía Wayback Machine) — artista de industria (GTA San Andreas); triangle counts 1996-2007 con origen declarado por entrada: modelos extraídos, libro D'Artiste (Gears), entrevistas de desarrolladores.
- **Tweet de Mathijs de Jonge (game director, Guerrilla), sept. 2015** (reportado por Wccftech) — fuente primaria: Thunderjaw 550k polys / 24×9 m; Killzone 3 250k máximo por frame completo en PS3.
- **The Polygonal Evolution of 5 Iconic PlayStation Characters — PlayStation Blog oficial, dic. 2019** — counts faciales first-party: Kratos 1,200→5,700→32,000; Kazuya, Rathalos, Palico, Sir Daniel.
- **Performance targets — Meta Horizon developer docs (Unity)** — presupuestos oficiales VR vigentes: tris/frame y draw calls por headset (Quest 2/Pro/3/3S), 72 FPS mínimo.
- **Geometry optimization — Android Game Development guide (Google)** — límite 65,535 vértices/16-bit, micro-triángulos <10 px, 50% por LOD, triángulos equiláteros, y números del demo Armies (210k/frame, 360 tris por unidad de multitud).
- **Real-Time 3D Art Best Practices: Advanced VR graphics techniques — Arm (doc 102073, PDF)** — aliasing geométrico por densidad de triángulos, LODs como mitigación de aliasing + coste, 4x MSAA barato en GPUs Mali.
- **Platform support and LOD specifications for MetaHumans — docs oficiales Epic** — cadena real de 8 LODs de un personaje cinematográfico: vértices, joints, influencias y texturas por nivel y por plataforma.
- **Nanite Virtualized Geometry — Unreal Engine docs (Epic)** — qué virtualiza y sus límites duros: sin translucencia, sin VR/MSAA/forward, DX12+SM6, 16M instancias.
- **Mesh LOD (introducción, generación al importar, funcionamiento del generador) — Unity Manual 6000.3** — auto-LOD nativo de Unity 6: mitad de índices por nivel, ≥256 tris para arrancar, +100% index buffer máximo, crossfade con GPU Resident Drawer, caveats de skinned meshes.
- **2D images for low LOD / Billboard Renderer + Optimizing draw calls — Unity Manual 6000.3** — billboards como último LOD (definición y soporte por pipeline) y por qué cuestan los draw calls (estado CPU→GPU; SRP Batcher, instancing, batching).
- **Avatar specifications — Roblox Creator Docs** — presupuesto oficial de una plataforma masiva multiplaforma: 10,742 tris por avatar con desglose por parte.
