# Optimización de VFX y shaders (Unity 6 / URP)

> **Cuando cargar este archivo:** antes de firmar un efecto de partículas o un shader; cuando el frame cae al disparar VFX (golpes, explosiones, auras, hechizos); al decidir VFX Graph vs Shuriken; al portar VFX a móvil; y en cualquier pase de optimización de transparencias/fillrate. La metodología general de profiling, batching y presupuesto de frame vive en [ver: unity/rendimiento-unity] — aquí va SOLO el ángulo VFX/shader. El *porqué* del feel (por qué un hit flash vende el golpe) está en [ver: gamedev/game-feel]; la implementación base del feel en [ver: pipeline/feel-en-unity].

## 0. La regla de oro para VFX

Un VFX casi nunca está limitado por vértices o draw calls: está limitado por **fillrate** — cuántos píxeles pinta la GPU por frame — y el multiplicador es el **overdraw** de las transparencias apiladas. El presupuesto de un efecto no es "cuántas partículas", es "cuántas veces se repinta cada píxel de pantalla y qué cuesta cada repintado". Todo lo demás en este archivo es una consecuencia de eso.

Orden mental antes de tocar nada: **medir → identificar si es fillrate/overdraw o shader por píxel → recortar → volver a medir en el device real** [ver: unity/rendimiento-unity §1].

## 1. Overdraw — el enemigo #1

**Qué es:** cada fragmento transparente que se dibuja se **mezcla** (blend) sobre lo que ya había. Las transparencias NO escriben profundidad ni se ocluyen entre sí, así que 20 partículas apiladas = ese píxel se procesa y mezcla 20 veces. Doc oficial nombra "overlapping transparent elements, such as UI, particles and sprites" como el contribuyente clásico de overdraw.

### Cómo medirlo (de más rápido a más preciso)

| Herramienta | Dónde | Qué muestra |
|---|---|---|
| **Scene view Draw Mode → Overdraw** | Dropdown arriba-izquierda del Scene view | Acumulación teñida: cuanto más brillante/saturado un área, más capas transparentes se pintan ahí. Es la primera lectura, gratis |
| **Rendering Debugger (URP)** → pestaña Rendering → sección Rendering Debug | `Window > Analysis > Rendering Debugger` | Toggle **Overdraw**: "indica si se renderiza la vista de depuración de overdraw... para ver dónde Unity dibuja píxeles uno sobre otro" (doc oficial URP, verificado — es un toggle, no varios modos con nombre) |
| **Frame Debugger** | `Window > Analysis > Frame Debugger` | Recorre draw a draw: ver cuántos draws de transparencia se acumulan sobre la misma zona y con qué shader/material [ver: unity/rendimiento-unity §1] |
| **Profiler → GPU** | Development Build en device | Confirma que el tiempo está en el pase transparente/GPU y no en CPU. GPU-bound = `Gfx.WaitForPresentOnGfxThread` domina [ver: unity/rendimiento-unity §1] |

### Cómo reducirlo (palancas concretas)

1. **Menos partículas, no más pequeñas y muchas.** Duplicar el count duplica el peor caso de overdraw. Bajar `Max Particles` (módulo Main) y `Rate over Time` / `Bursts` (módulo Emission).
2. **Partículas más chicas donde se solapan.** Un efecto grande de humo semitransparente es el peor overdraw posible; capas grandes = pantalla repintada N veces.
3. **Recortar el alfa transparente del sprite.** Con **Render Mode: Billboard** (el default de Renderer module) el quad SIEMPRE es rectangular — Unity no lo ciñe al pixel opaco automáticamente (no verificado ningún ajuste de "Tight/Polygon mesh" para billboards en la doc del Renderer module; eso es una función del Sprite Editor para `SpriteRenderer` 2D, no confirmada para partículas). Dos vías reales para partículas: (a) empacar el sprite ajustado al borde opaco dentro del atlas/textura (menos margen vacío en el UV rect) y (b) si el ahorro de fillrate justifica el coste extra de vértices, pasar **Render Mode: Mesh** con una malla low-poly recortada al silueta en vez de un quad — solo vale la pena si el efecto tiene pocas partículas simultáneas.
4. **Fade de alfa en los bordes**, no cortes duros: reduce el área con alfa alto que realmente mezcla peso.
5. **Fundir capas en textura**: en vez de 3 sistemas de humo superpuestos en runtime, hornear el look en una sola textura/flipbook (módulo **Texture Sheet Animation**) → 1 capa en vez de 3.
6. **Blend mode**: Additive y Alpha ambos generan overdraw. Additive suele poder ir sin ordenar por distancia (el resultado no depende del orden) — ahorra el CPU del sort, no el fillrate.

## 2. Fillrate y transparencias en móvil

Las GPU móviles son **tile-based (TBDR)**: rasterizan por tiles pequeños y son muy sensibles al ancho de banda y al fillrate. El pase transparente no puede aprovechar el early-Z ni el hidden-surface removal → cada capa transparente **se paga entera**. Por eso un VFX que va sobrado en PC tanquea un teléfono.

Reglas de fillrate en móvil:

- **Fill rate es el cuello típico en móvil** (doc oficial): overdraw de partículas/UI/sprites superpuestos y fragment shaders caros [ver: unity/rendimiento-unity §6].
- **Clampear el tamaño en pantalla**: `Max Particle Size` (módulo Renderer) es *la fracción máxima del viewport* que una partícula puede ocupar. Un valor bajo (p.ej. 0.5) evita que una partícula cercana a cámara llene media pantalla de fragmentos transparentes.
- **Efectos fullscreen (flashes, humo que cubre cámara)**: son overdraw de pantalla completa ×capas. Usar el mínimo de capas; considerar un solo quad con shader en vez de nube de partículas.
- **Shaders de partícula simples**: en URP, `Particles Unlit` antes que `Particles Lit` (ver §3). Cada fragmento transparente ejecuta el fragment shader completo, y se ejecuta N veces por overdraw.
- **Render Scale** baja el número absoluto de fragmentos de TODO el frame, VFX incluido — palanca global en el URP Asset [ver: unity/rendimiento-unity §6].

## 3. Complejidad de shader — el presupuesto por píxel

El coste de un shader de VFX es **coste-por-fragmento × número-de-fragmentos**. El overdraw multiplica; el shader es el factor. Un shader transparente caro se paga una vez por cada capa apilada.

### Palancas de coste (doc oficial de shader performance)

| Palanca | Regla |
|---|---|
| **Per-pixel vs per-vertex** | Mover cálculo del fragment al vertex shader: el ALU corre 1× por vértice en vez de 1× por fragmento. En Shader Graph, meter lógica en el **Vertex** stage cuando el resultado interpola bien |
| **Texture samples** | Cada `Sample Texture 2D` es un acceso a memoria. Menos samples; empaquetar datos en canales (mask R/G/B/A de una sola textura); activar mipmaps para reducir cache misses |
| **Precisión** | `half` (16-bit) en vez de `float` (32-bit) reduce ALU y ancho de banda. NO usar `half` para posiciones world-space ni valores que exijan precisión (artefactos). Ver Shader Graph precision abajo |
| **Funciones caras** | Evitar `sqrt`, `log`, `exp`; evitar `sin`/`cos` — usar `dot`/`cross` donde se pueda. Estas corren por fragmento |
| **`discard` / `clip`** | Rompen el early depth test → el hardware ya no puede descartar fragmentos ocultos antes del fragment shader. Evitar `clip`/`discard` salvo en alpha-cutout necesario (follaje, alpha test); en partículas transparentes normalmente no hace falta |
| **Escribir a render target** | Menor bit-depth (16 vs 32), menos MSAA, evitar multi-render-target innecesario |

### Precisión en Shader Graph (Unity 6)

Dos niveles distintos — no confundir (verificado contra doc de Shader Graph 17.x):

**Graph Settings → Precision** (default de todo el grafo): solo dos opciones — **Single** (32-bit) o **Half** (16-bit). Para un shader de VFX móvil, setear el grafo entero en **Half**.

**Precision por nodo** (dropdown en cada nodo, override puntual del default del grafo):

| Modo | Qué es | Uso |
|---|---|---|
| **Use Graph Precision** | Sigue la precisión configurada en Graph Settings | Default recomendado para casi todos los nodos — deja que el ajuste global mande |
| **Single** | Fuerza este nodo a float 32-bit aunque el grafo esté en Half | Posiciones world-space, UVs, trigonometría, cálculos que necesitan rango/precisión |
| **Half** | Fuerza este nodo a float 16-bit aunque el grafo esté en Single | Vectores cortos, direcciones, posiciones object-space, colores HDR. No para el sol / luces muy brillantes |
| **Inherit** | Toma la precisión del wire de entrada conectado; sin conexión, cae a la precisión del grafo | Nodos intermedios que combinan varias entradas |
| **Switchable** | Solo en nodos de Sub Graph: el nodo que usa el Sub Graph decide la precisión al conectarlo | Sub Graphs reutilizables entre shaders con distinto presupuesto |

Para un shader de VFX móvil: Graph Settings en **Half**, y subir a **Single** solo los nodos puntuales que lo necesiten (posición world-space, UVs finas).

### Tiers de shader en URP (de barato a caro)

`Unlit` < `Simple Lit` < `Lit` < `Complex Lit`. Para partículas, URP trae variantes dedicadas — nombres del menú de shader: **Universal Render Pipeline/Particles/Unlit**, **/Particles/Simple Lit**, **/Particles/Lit** (verificar la ruta exacta en tu versión del menú de materiales). Casi todo VFX quiere **Particles/Unlit** o un Shader Graph Unlit: el humo, chispas y flashes rara vez necesitan iluminación PBR. Para móvil, elegir shaders de las categorías **Mobile** o **Unlit** — son versiones simplificadas (doc oficial).

### Presupuesto de un fragment shader de VFX móvil (guía práctica)

Objetivo mental para un shader transparente que se va a apilar (recordar: cada capa de overdraw ejecuta el fragment completo). Cifras **orientativas**, no doc oficial — el techo real se mide en el device:

- **Texture samples:** 1–2 idealmente (albedo + una mask empacada en RGBA). Cada sample extra × overdraw.
- **Precisión:** Half por defecto; Single solo donde haga falta.
- **Funciones trascendentes por fragmento** (`sin`, `cos`, `pow`, `exp`, `log`, `sqrt`): apuntar a 0; si hace falta oscilación, precalcular en textura o hacerlo en el vertex stage.
- **Iluminación:** ninguna (Unlit) para chispas/humo/flashes; PBR solo si el efecto lo exige de verdad.
- **`clip`/`discard`:** 0 en transparentes (rompe early-Z).
- **Dependencias de profundidad (Soft Particles):** solo si el efecto roza geometría (§10).

Si el shader necesita más que esto, sospechar que el efecto se resuelve mejor con una **textura/flipbook horneado** (mueve el coste de runtime a authoring) que con matemática por píxel.

> Mito a desmontar: "menos nodos = shader más rápido". El contador de nodos no es la métrica; lo que cuesta es el trabajo **por fragmento** (samples, ALU, funciones caras) × overdraw. Un grafo con 40 nodos todo en el vertex stage puede ser más barato que uno de 10 nodos con tres `Sample Texture` y un `pow` en el fragment. Detalle de construcción de shaders en [ver: shader-graph-fundamentos] y [ver: recetas-shaders].

## 4. Presupuesto de partículas por plataforma

⚠️ Cifras **orientativas** — NO son doc oficial verificada; el límite real se descubre midiendo fillrate/overdraw en el device target [ver: unity/rendimiento-unity §6]. Punto de partida, no ley:

| Aspecto | Móvil (gama media) | Móvil (flagship) | PC/consola |
|---|---|---|---|
| Partículas vivas simultáneas (Shuriken) | cientos–~1–2 k | pocos miles | decenas de miles |
| Capas transparentes solapadas (overdraw pico) | 2–3× pantalla | 3–4× | 5×+ |
| Tamaño en pantalla | `Max Particle Size` bajo, evitar fullscreen | moderado | libre |
| Shader | Unlit/Mobile, Half | Unlit, Half | Lit permitido |
| Simulación GPU (VFX Graph) | solo si el device califica (§5) | sí, cientos de miles–millones | millones |

La disciplina que sí es doc oficial: **medir el pico sostenido con el device caliente** (thermal throttling), no el pico de 30 s [ver: unity/rendimiento-unity §6].

## 5. VFX Graph (GPU) vs Shuriken (CPU)

Dos sistemas distintos, no versiones del mismo:

| | **Shuriken** (Built-in Particle System) | **VFX Graph** (Visual Effect Graph) |
|---|---|---|
| Simulación | **CPU** (main thread; algo de jobs) | **GPU** (compute shaders) |
| Escala | cientos–miles (CPU-bound) | cientos de miles–millones |
| Autoría | Inspector con módulos (Main, Emission, Shape, Renderer, …) | Grafo por nodos/contextos (Spawn, Initialize, Update, Output) |
| Requisito HW | Ninguno especial — corre en todas las plataformas | **Compute shaders** (`SystemInfo.supportsComputeShaders`) + **SSBO** |
| **OpenGL ES** | Soportado | **NO soportado** |
| **URP** | Completo | Limitado: **solo partículas Unlit**, **no soporta gamma color space**; según la doc de requisitos de VFX Graph (17.x, Unity 6) su soporte en URP **sigue en preview** y móvil en preview |
| Interacción con lógica de juego | Fácil (colisiones CPU, callbacks, sub-emitters, eventos) | GPU-side; leer de vuelta a CPU es caro (usa GPU Events) |
| 2D / sprites | Encaja bien | Menos idóneo para 2D [ver: vfx-2d] |
| Módulos caros a vigilar | Collision, Lights, Trails, Noise (CPU) | Coste GPU: outputs y overdraw, igual que Shuriken |

**Decisión práctica:**
- **Móvil / máxima compatibilidad / VFX que interactúa con gameplay** → **Shuriken**. Es el default seguro. Detalle de módulos en [ver: particulas-vfx-graph].
- **Masas enormes (millones), PC/consola/HDRP, simulación pesada (fluidos, ribbons GPU)** → **VFX Graph**, tras confirmar `supportsComputeShaders` y no-OpenGL-ES en el target. En móvil, tratarlo como preview: probar en el device real antes de comprometerlo [ver: particulas-vfx-graph].
- **La cantidad de partículas NO es la razón para elegir GPU en móvil**: el cuello ahí es fillrate/overdraw, y eso lo sufren ambos por igual. VFX Graph resuelve *simulación*, no *overdraw*.

## 6. Batching de partículas y shaders

El detalle de SRP Batcher / GPU instancing / atlasing está en [ver: unity/rendimiento-unity §2]; aquí lo específico de VFX:

- **Un solo material por sistema**, compartido entre instancias del mismo efecto → menos SetPass. El **SRP Batcher** (default en URP) reduce cambios de estado entre draws del mismo shader; mantener las propiedades en `UnityPerMaterial` y no romperlo con `MaterialPropertyBlock` por partícula.
- **GPU Instancing de mesh particles**: checkbox **Enable Mesh GPU Instancing** en el módulo Renderer (solo en **Render Mode: Mesh**). Convierte N mesh-particles en pocos draws. Requiere shader compatible con instancing.
- **Atlas / Texture Sheet Animation**: varios efectos que comparten una atlas comparten material → batchean juntos. Un flipbook en una atlas evita cambiar textura por efecto.
- **Billboards ya son eficientes en draws** (un solo mesh dinámico por sistema); su coste es fillrate, no draw calls. No perseguir "menos draw calls" en billboards — perseguir menos overdraw.
- Verificar SIEMPRE con **Frame Debugger** que los sistemas de partículas batchean como esperas y por qué se corta un batch [ver: unity/rendimiento-unity §2].

## 7. LOD de VFX — menos efecto a distancia y fuera de cámara

| Técnica | Cómo | Setting exacto |
|---|---|---|
| **Culling fuera de cámara** | Que el sistema pare de simular offscreen | Módulo Main → **Culling Mode**: `Automatic` (loops pausan offscreen; no-loops siempre simulan), `Pause` (para offscreen), `Pause and Catch-up` (para y da un salto grande al reaparecer — puede causar spike), `Always Simulate` (nunca para) |
| **Presupuesto por distancia** | Menos `Rate over Time` / `Max Particles` cuando el emisor está lejos | Escalar por script según distancia a cámara, o LODs del prefab |
| **LOD Group** | Renderers distintos por % de altura en pantalla (ratio screen-space height/total, verificado); el tramo final de la barra del inspector se muestra como **Culled** (etiqueta de la UI del inspector, no localizada textualmente en el manual — no renderiza nada) | Componente `LOD Group` sobre el prefab del efecto; el nivel Culled apaga los renderers a distancia |
| **Apagar a distancia** | Desactivar el GameObject/emisión cuando el efecto no aporta | Gate por distancia en un manager, o Culling Mode = `Pause` |

Notas:
- **`Automatic` es el default sano**: efectos en loop (antorchas, auras) pausan solos offscreen; one-shots (explosión) siempre simulan para no perder el disparo.
- **Cuidado con `Pause and Catch-up`**: al reaparecer hace un paso grande de simulación → posible spike de un frame. No usarlo en sistemas pesados que entran/salen de cámara seguido.
- **`Always Simulate`** solo para one-shots cortos donde pausar se notaría; nunca para loops pesados.
- **LOD Group puede reducir/apagar los renderers de VFX por distancia**; su uso para deshabilitar sistemas de partículas concretos a distancia NO está confirmado explícitamente en la doc del componente — verificar en tu proyecto (asignar el Particle System Renderer a los LODs y probar el nivel Culled).

## 8. Medir antes de optimizar (herramientas para VFX)

Reutiliza el kit general [ver: unity/rendimiento-unity §1], con foco VFX:

| Herramienta | Qué respondes con ella |
|---|---|
| **Scene Draw Mode → Overdraw** | ¿Dónde se apilan las transparencias? Lectura visual instantánea |
| **Profiler → GPU + CPU** | ¿Es GPU-bound (fillrate/overdraw) o CPU (Shuriken con Collision/Noise/Trails)? `Gfx.WaitForPresentOnGfxThread` = GPU |
| **Frame Debugger** | ¿Cuántos draws transparentes sobre la misma zona? ¿Batchean? ¿Qué shader? |
| **Rendering Statistics** (botón **Stats**, esquina superior derecha del Game view — NO hay entrada en `Window > Analysis` para esto, verificado) | Batches, Saved by batching, SetPass Calls, Tris, Verts. El set exacto varía según build target. NO reporta overdraw (para eso, el Scene Draw Mode) |
| **Rendering Debugger (URP)** | Toggle **Overdraw** (pestaña Rendering → Rendering Debug) |

CPU-bound en Shuriken suele venir de: **Collision** module, **Trails**, **Noise**, **Lights** (una luz por partícula = muerte), **Sub Emitters**, y **Sort Mode: By Distance** (ordena por distancia cada frame). Perfilar el módulo culpable, no adivinar [ver: unity/rendimiento-unity §1].

## 9. La trampa del VFX bonito que tanquea el móvil

El VFX que se ve espectacular en el editor de tu PC es exactamente el que revienta el frame en un teléfono, porque el editor esconde el coste de fillrate. Protocolo obligatorio:

1. **Nunca firmar un VFX solo por el editor.** El editor miente en GPU igual que en CPU [ver: unity/rendimiento-unity §1].
2. **Development Build en el device target real**, Profiler conectado, y el efecto disparado en el peor caso plausible (varios a la vez, cerca de cámara).
3. **Device caliente**: probar tras 10+ min de juego; el throttling térmico recorta el fillrate sostenible [ver: unity/rendimiento-unity §6].
4. **Peor caso de gameplay**, no el efecto aislado: 5 enemigos muriendo juntos con sus explosiones + partículas de ambiente + UI encima = el overdraw que de verdad importa.
5. Si tanquea: primero recortar **capas/overdraw**, luego **tamaño** (`Max Particle Size`), luego **shader** (a Unlit/Half), luego **count**. En ese orden — el fillrate manda.

## 10. Blend modes, soft particles y otros costes ocultos

**Blend modes** (en el material del shader de partícula):

| Blend | Coste | Cuándo |
|---|---|---|
| **Additive** | Overdraw sí; **sin sort** (el resultado no depende del orden) | Fuego, chispas, luz, magia, flashes. El favorito para VFX porque ahorra el sort de CPU |
| **Alpha (transparente)** | Overdraw + normalmente requiere ordenar por distancia | Humo, polvo, decals suaves. `Sort Mode: By Distance` cuesta CPU cada frame |
| **Premultiplied Alpha** | Como Alpha | Permite mezclar borde additive + cuerpo alpha en una sola textura |

**Soft Particles** (fade suave donde la partícula intersecta geometría): elimina el corte duro feo, pero **requiere la textura de profundidad de cámara** (Depth Texture en el URP Asset) y **añade un sample de profundidad por fragmento** → coste extra × overdraw. En móvil, usar con criterio: activarlo solo en los efectos que de verdad rozan geometría, no en todos. El parámetro que controla la suavidad es el factor de soft particles del shader (nombre exacto según shader/versión — verificar en el material).

**Otros costes ocultos del Particle System (Shuriken):**

| Módulo / setting | Coste | Nota |
|---|---|---|
| **Trails** | CPU (genera geometría de estela) + más overdraw transparente | Caro; limitar ratio y ancho |
| **Noise** | CPU por partícula | Bonito pero se paga; bajar Quality (Low/Medium/High) |
| **Collision (World/Planes)** | CPU (queries) | El más caro; usar Planes en vez de World, o quitarlo |
| **Lights** | Altísimo — cada partícula puede instanciar una luz real | Casi nunca vale la pena; emular con Additive + Bloom |
| **Sub Emitters** | Multiplica sistemas | Cada uno con su presupuesto |
| **Sort Mode: By Distance** | CPU cada frame | Usar Additive sin sort donde el orden no importe |

Regla: **el look "premium" de fuego/magia se logra con Additive + una buena textura/flipbook + Bloom del post-process**, no apilando módulos caros. El coste del feel visual va en el post (Bloom) una vez, no por partícula.

## 11. VFX 2D (nota)

En 2D el overdraw es igual de crítico: sprites additive/transparentes apilados (partículas, glows, flashes de golpe) repintan el mismo píxel. Mismas palancas — menos capas, recortar alfa vacío del sprite, shaders Unlit, medir con Scene Overdraw. Con el **2D Renderer** de URP, ojo con las luces 2D interactuando con partículas. Detalle específico de 2D en [ver: vfx-2d]; el juice del golpe (hit flash, screen shake que acompaña) en [ver: gamedev/game-feel] y [ver: pipeline/feel-en-unity].

## Reglas prácticas

- [ ] Medir overdraw con **Scene Draw Mode → Overdraw** ANTES de tocar un VFX; el área brillante es el problema.
- [ ] Decidir GPU-bound vs CPU-bound con el Profiler antes de optimizar (fillrate ≠ Collision/Noise en CPU).
- [ ] Bajar `Max Particles` y `Rate over Time` antes que cualquier otra cosa; menos capas transparentes > partículas más chicas y más numerosas.
- [ ] Clampear `Max Particle Size` (Renderer) para que ninguna partícula llene media pantalla de fragmentos.
- [ ] Recortar el alfa vacío del sprite EN EL ATLAS (menos margen vacío en el UV rect); el Billboard sigue siendo un quad rectangular igual, no hay recorte automático de mesh.
- [ ] Shader de VFX = **Particles/Unlit** (o Shader Graph Unlit) por defecto; PBR solo si el efecto de verdad lo necesita.
- [ ] Grafo de shader en precisión **Half**, subir a Single solo los nodos que lo exijan.
- [ ] Mover cálculo del **Fragment** al **Vertex** stage siempre que interpole bien; minimizar `Sample Texture 2D`, evitar `sqrt/exp/log/sin/cos`.
- [ ] Evitar `clip`/`discard` en partículas (rompe early-Z); reservarlo para alpha-cutout real.
- [ ] Móvil: shaders de categoría Mobile/Unlit; verificar fillrate con Render Scale como palanca global.
- [ ] VFX Graph solo si el target tiene compute shaders + SSBO y NO es OpenGL ES; en móvil tratarlo como preview y probar en device.
- [ ] Shuriken como default en móvil y cuando el VFX interactúa con gameplay.
- [ ] Un material compartido por efecto; no romper el SRP Batcher; `Enable Mesh GPU Instancing` para mesh particles.
- [ ] `Culling Mode: Automatic` por defecto; nunca `Always Simulate` en loops pesados; cuidado con el spike de `Pause and Catch-up`.
- [ ] Escalar emisión / apagar VFX por distancia (LOD Group o gate por distancia); no simular lo que no se ve.
- [ ] Vigilar módulos caros de Shuriken: Collision, Trails, Noise, Lights, `Sort Mode: By Distance`.
- [ ] Probar SIEMPRE en el **device real, caliente, en el peor caso de gameplay** antes de firmar.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| "Se ve genial en mi PC" y se firma | El editor esconde el fillrate; Development Build en device real, caliente, peor caso |
| Perseguir "menos draw calls" en billboards | Los billboards ya batchean; el problema es overdraw, no draws — medir con Scene Overdraw |
| Humo grande con muchas capas semitransparentes | Overdraw fullscreen ×N; hornear a flipbook, menos capas, alfa con fade |
| Contar nodos del Shader Graph como métrica de coste | Lo que cuesta es el trabajo por fragmento (samples/ALU/funciones) × overdraw, no el nº de nodos |
| `Sample Texture` de sobra y `pow`/`sin` en el fragment | Empaquetar en canales, mover al vertex, evitar funciones trascendentes por píxel |
| `clip`/`discard` "por si acaso" en partículas | Rompe el early depth test; quitarlo salvo alpha-cutout necesario |
| Partícula cercana que llena la pantalla | `Max Particle Size` bajo para clampear la fracción de viewport |
| Meter VFX Graph en un juego móvil "porque es más moderno" | Requiere compute+SSBO, no OpenGL ES, URP en preview; Shuriken es el default móvil |
| Elegir VFX Graph por "más partículas" en móvil | En móvil el cuello es fillrate/overdraw, no simulación; GPU no arregla overdraw |
| `Always Simulate` en efectos de ambiente en loop | Simulan fuera de cámara gastando frame; `Automatic` o `Pause` |
| `Pause and Catch-up` en un sistema pesado que entra/sale de cámara | Salto grande de simulación al reaparecer = spike; usar `Pause` |
| Una luz por partícula (módulo Lights) para "que brille" | Cada luz es un coste enorme; emular con additive/bloom, no con luces reales |
| `Sort Mode: By Distance` en todo | Ordena cada frame en CPU; usar Additive sin sort donde el orden no importe |
| Shader `Lit` en chispas/humo | `Particles/Unlit`; el PBR no aporta y multiplica coste por cada capa de overdraw |
| Materiales distintos por instancia del mismo efecto | Rompe batching; material compartido + variación por instancia compatible con SRP Batcher |

## Fuentes

Consultadas directamente en esta investigación (2026-07-20), Unity 6 (docs 6000.0) salvo indicación:

- **Graphics performance fundamentals** — Unity Manual — fill rate, memory bandwidth, vertex processing, CPU rendering; overdraw de transparencias (UI/partículas/sprites), "Overdraw Draw mode" del editor, shaders Mobile/Unlit para móvil.
- **Shader performance / Optimizing shader runtime performance** — Unity Manual (`SL-ShaderPerformance`) — per-pixel vs per-vertex, reducir texture samples, `half` vs `float`, evitar `sqrt/log/exp/sin/cos` (usar `dot`/`cross`), `discard`/`clip` rompe early depth test.
- **Precision Modes** — docs de Shader Graph (`com.unity.shadergraph@17.0`) — verificado en esta revisión (2026-07-20) y corregido: Graph Settings → Precision solo tiene Single/Half; el dropdown por-nodo es distinto y añade Use Graph Precision/Inherit/Switchable. Half recomendado para móvil.
- **Particle System Renderer module** — Unity Manual — Render Mode (Billboard/Mesh), Sort Mode, `Max Particle Size` (fracción del viewport), Render Alignment, Enable Mesh GPU Instancing.
- **Particle System Main module** — Unity Manual — `Max Particles`, Simulation Space, Culling Mode (Automatic / Pause and Catch-up / Pause / Always Simulate).
- **Visual Effect Graph — System Requirements / compatibility** — docs de VFX Graph (`com.unity.visualeffectgraph@17.0`) — requiere compute shaders (`SystemInfo.supportsComputeShaders`) y SSBO, NO soporta OpenGL ES; en URP solo partículas Unlit, sin gamma color space, soporte URP/móvil marcado como preview.
- **LOD Group** — Unity Manual (`class-LODGroup`) — niveles por % de altura en pantalla (ratio screen-space height/total, verificado); "Culled" es la etiqueta de la UI del inspector para el tramo final, no aparece como término textual en el manual.
- **Rendering Statistics window** — Unity Manual (`RenderingStatistics`) — se abre con el botón **Stats** del Game view (verificado: NO existe como entrada de `Window > Analysis`); reporta Batches/Saved by batching/SetPass/Tris/Verts, el set varía por build target; SRP Batcher y Standard Instanced NO se confirmaron como líneas de este panel en esta revisión.
- **Rendering Debugger (URP)** — Unity Manual (`urp/features/rendering-debugger-reference`) — pestaña Rendering → sección Rendering Debug → toggle **Overdraw** (verificado en esta revisión, 2026-07-20; resuelve el hueco que había quedado NO VERIFICADO).
- Metodología general de profiling, batching, GC, presupuesto de frame y móvil: [ver: unity/rendimiento-unity] (fuentes propias de ese archivo).
- Presupuestos de partículas por plataforma: **sin fuente verificable**; marcados como orientativos, a validar con Profiler en el device target.
