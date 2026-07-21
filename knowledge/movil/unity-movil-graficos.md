# Gráficos móviles en Unity

> **Cuando cargar este archivo:** al configurar el pipeline y los settings gráficos de un juego móvil real (Unity 6, iOS/Android 2026): qué apagar en el URP Asset para móvil, cómo iluminar (baked), qué shaders usar, cómo atacar el overdraw/fillrate, cómo comprimir texturas (ASTC), y por qué las GPU móviles TBDR cambian las reglas del render. PROFUNDIZA el ángulo móvil sobre bases ya sembradas: la mecánica genérica de URP en [ver: unity/rendering-urp], la de VFX/shaders en [ver: vfx-shaders/optimizacion-vfx], la de poly budget en [ver: modelado/presupuestos-poligonos], y el profiling/frame budget en [ver: unity/rendimiento-unity]. Aquí va SOLO lo que es distinto en móvil. El arte/estética en [ver: arte-movil]; el rendimiento CPU/memoria móvil en [ver: unity-movil-rendimiento]; build/firma/tamaño en [ver: release-movil].

## 0. La única regla que explica el resto: la GPU móvil es TBDR y vive del fillrate

Todo lo demás en este archivo es una consecuencia de dos hechos de hardware:

1. **La GPU móvil es tile-based (TBDR).** Mali (Arm), Adreno (Qualcomm), PowerVR/Apple GPU y las de Apple Silicon rasterizan la pantalla por **tiles pequeños** que caben en una memoria on-chip rapidísima; el framebuffer completo solo se escribe a RAM al final de cada tile. Esto hace que **depth-test, blending y MSAA ocurran en el tile on-chip** (muy baratos) pero castiga durísimo cualquier operación que obligue a leer el framebuffer ya resuelto de vuelta desde RAM (grabs de pantalla, ciertos efectos, cambios de render target a media escena).
2. **El cuello de botella típico en móvil es el fill rate**, no los vértices ni los draw calls. Doc oficial de Unity: si la app está limitada por fill rate, "la GPU intenta dibujar más píxeles por frame de los que puede" — y nombra el **overdraw de elementos transparentes solapados (UI, partículas, sprites)** como el contribuyente clásico [ver: vfx-shaders/optimizacion-vfx §1-2].

Corolarios que gobiernan el diseño gráfico móvil:

| Consecuencia del TBDR/fillrate | Qué implica en la práctica |
|---|---|
| Cada píxel repintado (overdraw) se paga entero | Overdraw es el enemigo #1: menos capas transparentes, menos partículas grandes, menos UI apilada |
| El bandwidth a RAM es el recurso caro (batería + calor) | Menos resolución de framebuffer (render scale), menos passes fullscreen, texturas comprimidas |
| MSAA sale casi gratis en el tile… si no rompes el flujo TBDR | 4x MSAA es viable en móvil; leer la Opaque Texture puede **anularlo** (§2) |
| Leer el framebuffer resuelto = tile flush a RAM | Evitar GrabPass, custom passes que blitean a media escena, Depth/Opaque Texture innecesarias |
| Throttling térmico recorta el fillrate sostenido | El presupuesto es el pico SOSTENIDO con el device caliente, no el pico de 30 s |

## 1. URP Asset para móvil: qué apagar (y el porqué TBDR)

La mecánica genérica del URP Asset y de cada setting está en [ver: unity/rendering-urp §2]. Aquí, la lista móvil con el matiz de hardware. Un **URP Asset por quality level**; el móvil usa el más recortado.

| Setting (URP Asset) | Móvil | Porqué específico móvil |
|---|---|---|
| **Rendering Path** | **Forward** (o Forward+ si de verdad hay muchas luces) | Deferred no es compatible con MSAA y en TBDR el G-buffer quema bandwidth. Forward es el default móvil sano [ver: unity/rendering-urp §3] |
| **HDR** | Default ON; **OFF en low-end si no usas Bloom/tonemapping** | Doc oficial: desactivarlo "salta cálculos HDR y da mejor rendimiento" en hardware bajo. HDR sube el bit-depth del render target = más bandwidth |
| **Anti Aliasing (MSAA)** | **2x–4x** (barato en TBDR); default del asset es Disabled | Se resuelve en el tile on-chip. ⚠️ Gotcha: en plataformas sin la store action *StoreAndResolve*, si **Opaque Texture** está activa Unity **ignora el MSAA** (doc URP Asset) — leer la opaque texture fuerza un resolve que rompe el MSAA del tile |
| **Render Scale** | **La palanca #1**: 0.7–0.9 en pantallas densas | Baja el nº absoluto de fragmentos de TODO el frame. Doc: valores <1.0 "reducen significativamente la carga GPU". Muchos teléfonos tienen DPI altísimo; nadie nota render scale 0.85 y recuperas 20-30% de fillrate |
| **Upscaling Filter** | FSR 1.0 o STP si bajas render scale y se ve blando | Recupera nitidez sin pagar la resolución nativa |
| **Additional Lights** | **Per Vertex** (default móvil) o Disabled; per-pixel solo la Main | Doc: Per Vertex es "lo más mobile-friendly". Límite por cámara: **32** en móvil, **16** en OpenGL ES 3.0 o anterior [ver: unity/rendering-urp §3] |
| **Cast Shadows / Soft Shadows** | Soft Shadows **OFF** (default); Hard shadows y Max Distance corta | Doc: soft shadows tienen "alto impacto en render tile-based". La palanca de calidad de sombra más barata es acortar **Shadow Max Distance** |
| **Shadow Cascades** | 1 (móvil) | Cada cascade re-dibuja geometría al shadow map (multi-pass) |
| **Depth Texture / Opaque Texture** | **OFF** salvo que un shader los use | Cada uno cuesta un pass extra y bandwidth; la Opaque Texture además anula el MSAA (arriba). Si necesitas depth, "After Transparents" ahorra bandwidth |
| **LOD Cross Fade** | OFF si no lo usas | Doc: quita variantes de shader y reduce build time |
| **SRP Batcher** | **ON siempre** | Reduce cambios de render-state; pocos shaders, muchos materiales [ver: unity/rendering-urp §2] |

```csharp
// Render scale y target frame rate en runtime (opción de calidad in-game).
// El framerate objetivo NO se fija con vSync en móvil: Application.targetFrameRate.
using UnityEngine.Rendering.Universal;
var urp = (UniversalRenderPipelineAsset)UnityEngine.Rendering.GraphicsSettings.currentRenderPipeline;
urp.renderScale = 0.85f;                 // suele ser invisible y compra fillrate
Application.targetFrameRate = 60;        // 30 en low-end para estabilidad térmica/batería
```

## 2. Iluminación móvil: baked casi siempre

La regla móvil es más dura que la genérica de [ver: unity/rendering-urp §5]: **las luces realtime con sombra son un lujo que casi nunca cabe en el presupuesto móvil.** Cada luz realtime per-pixel corre el fragment shader otra vez por los objetos que afecta, y cada sombra realtime es un shadow map extra (re-dibuja geometría). En TBDR eso es fillrate + bandwidth que rara vez sobran.

| Estrategia | Cuándo en móvil | Coste runtime |
|---|---|---|
| **Baked (lightmaps + probes)** | El **default móvil**: toda la escenografía estática | Casi cero — la luz está en la textura |
| **Mixed + Lighting Mode Subtractive** | Low/mid-end: sombras estáticas baked, solo la Directional principal proyecta realtime | Lo más barato con algo de dinamismo [ver: unity/rendering-urp §5] |
| **Mixed + Shadowmask** | Mid/high-end: mejor calidad, escenas grandes | Medio |
| **Realtime puro** | SOLO lo que de verdad se mueve/cambia (una antorcha del jugador, un jefe) — pocas y controladas | Alto |

Reglas móviles concretas:
- **Objetos dinámicos no reciben lightmaps** → los ilumina el sistema de probes. En Unity 6 usar **Adaptive Probe Volumes (APV)** para que los personajes no se vean planos/negros en escena baked [ver: unity/rendering-urp §6].
- **Una Directional realtime** (el "sol") es lo máximo que se da por sentado; el resto, baked o probes.
- **Reflection Probes baked**, nunca realtime en móvil (carísimos). Box projection para interiores.
- El bake es de authoring, no cuesta en runtime: subir Lightmap Resolution encarece el *tamaño del atlas de lightmap en memoria*, no los FPS — pero ese atlas también consume el presupuesto de textura (§5).
- Ambient Occlusion: hornearla en el lightmap/textura (Android doc lo recomienda como técnica de ahorro), no SSAO en tiempo real en low-end.

## 3. Shaders baratos que se ven caros

El tier de coste es `Unlit < Baked Lit < Simple Lit < Lit < Complex Lit` [ver: unity/rendering-urp §4]. En móvil, doc oficial: elegir shaders de las categorías **Mobile** o **Unlit**. El ángulo móvil sobre lo genérico de [ver: vfx-shaders/optimizacion-vfx §3]:

| Palanca de shader | Regla móvil |
|---|---|
| **Elegir el más barato que dé el look** | Estilizado plano → **Unlit** o **Simple Lit** (Blinn-Phong, no PBR). El PBR completo (Lit) rara vez se justifica en un móvil low-end |
| **Cálculo por píxel → por vértice** | Cada operación en el fragment corre una vez por fragmento × overdraw. Mover al vertex stage lo que interpole bien (Shader Graph: Vertex stage) |
| **Precisión `half` (16-bit)** | Default en móvil para VFX y la mayoría de cálculos; Single (32-bit) solo para posiciones world-space/UVs finas. En Shader Graph: Graph Settings → Precision = Half [ver: vfx-shaders/optimizacion-vfx §3] |
| **Texture samples** | Cada `Sample Texture` es acceso a memoria (= bandwidth = batería). Empacar máscaras en canales RGBA de UNA textura; mipmaps ON reducen cache misses |
| **Evitar transcendentes por píxel** | `sin/cos/pow/exp/log/sqrt` son caras por fragmento; usar `dot/cross`, precalcular en textura, o subir al vertex |
| **`clip`/`discard`** | Rompe el early-Z del TBDR → el hardware ya no descarta fragmentos ocultos antes del fragment shader. Reservar para alpha-cutout real (follaje); nunca "por si acaso" |
| **Transparencias** | Cada capa transparente ejecuta el fragment completo y no se ocluye. El coste de una transparencia = coste-por-fragmento × capas apiladas (§4) |

## 4. Overdraw: el enemigo #1 en móvil

Ya cubierto a fondo en [ver: vfx-shaders/optimizacion-vfx §1]; el matiz móvil es que la penalización es **mayor** porque el pase transparente no aprovecha el hidden-surface removal del TBDR: cada capa se paga entera contra el bandwidth limitado.

Fuentes de overdraw en un juego móvil, de peor a menor:

| Fuente | Antídoto móvil |
|---|---|
| **UI transparente apilada** (paneles semitransparentes, blur de fondo, iconos con halo) | Menos capas fullscreen; fondos opacos donde se pueda; no dejar quads fullscreen con alpha casi-0. El overdraw de UI se mide igual: Scene view → Overdraw |
| **Partículas grandes/semitransparentes** (humo, flashes que cubren cámara) | `Max Particle Size` bajo, menos partículas más grandes, hornear a flipbook en vez de apilar sistemas, Additive sin sort [ver: vfx-shaders/optimizacion-vfx §1-2] |
| **Fondos/capas fullscreen superpuestas** (parallax con niebla encima) | Reducir capas; Mesh Type Tight en sprites con mucha zona transparente |
| **Vegetación alpha** (follaje solapado) | El caso extremo: billboards/impostors como último LOD bajan capas transparentes además de tris [ver: modelado/presupuestos-poligonos §5] |

Medir SIEMPRE con **Scene view Draw Mode → Overdraw** y el toggle **Overdraw** del Rendering Debugger (URP) ANTES de optimizar otra cosa; el área brillante es el problema [ver: vfx-shaders/optimizacion-vfx §8].

## 5. Texturas móviles: ASTC, mipmaps, atlas, presupuesto

Las texturas suelen reventar la memoria (y el bandwidth) antes que la geometría [ver: modelado/presupuestos-poligonos §2]. Palancas móviles:

### Compresión: ASTC es el default móvil 2026

Google (Android best practices) confirma **ASTC como formato primario recomendado** (soportado por 75%+ de dispositivos Android activos) con **ETC2 como fallback** (90%+). En iOS todos los GPU soportan ASTC. PVRTC es legacy (solo PowerVR, potencia de dos obligatoria) — evitarlo salvo compatibilidad muy vieja.

ASTC usa **bloques de 128 bits**; el block size elige el trade-off calidad/tamaño. Bits-por-píxel = 128 / (ancho×alto del bloque):

| Formato ASTC | bpp (derivado del bloque de 128 bits) | Uso típico móvil |
|---|---|---|
| **ASTC 4×4** | 8.00 | Máxima calidad: normal maps, texturas hero de cerca |
| **ASTC 5×5** | 5.12 | Alta calidad general |
| **ASTC 6×6** | 3.56 | **Sweet spot** para albedo/diffuse de la mayoría de assets |
| **ASTC 8×8** | 2.00 | Fondos, texturas lejanas, donde se puede apretar |
| **ASTC 10×10 / 12×12** | 1.28 / 0.89 | Muy agresivo; solo donde no se note |
| ETC2 RGBA8 / RGB8 (fallback) | 8 / 4 | Fallback Android sin ASTC |
| Sin comprimir RGBA32 | 32 | ⛔ solo si la compresión rompe el asset (gradientes UI puntuales) |

> Los bpp de ASTC son aritmética directa sobre la definición del formato (bloque de 128 bits); ASTC-como-recomendado y el soporte 75%/90% son de la guía de Android. Elegir por asset, no un block size global: normal maps a 4×4/5×5, albedo a 6×6, fondos a 8×8.

### Resolución, mipmaps y atlas (reglas móviles)

- **Mipmaps OBLIGATORIOS** en todo lo que se vea a distancia variable: sin mips, una textura vista de lejos hace shimmer y **quema cache/bandwidth** (muestrea texels que no aporta). Coste: **+33% de memoria por textura** (Android doc) — se paga con gusto. Excepción: UI a distancia fija y sprites siempre al mismo tamaño (mips OFF ahí ahorran ese 33%).
- **Resolución agresiva**: bajar la resolución de las texturas no críticas de un material (roughness/metallic de 1024→512) sin tocar el albedo. Tope práctico de textura en móvil: **2048** para lo hero; 1024/512 para el grueso (referencia: incluso MetaHuman en móvil topa texturas a 2048 [ver: modelado/presupuestos-poligonos §3]).
- **Filtering**: **Bilinear** es la recomendación general; Trilinear cuesta bandwidth. Anisotropic: combinar **bilinear + 2× aniso** en vez de trilinear (Android doc). Dato duro: el texture filtering puede ser hasta **50% del consumo de energía GPU** — no subir aniso por gusto.
- **Atlasing / channel packing**: empacar texturas en un atlas reduce draw calls (sprites/props que comparten material batchean) y empacar 3 máscaras de un canal (AO/rough/metal) en una RGBA reduce samples. Packed textures en **linear**, no sRGB [ver: unity/rendering-urp §12 sobre Sprite Atlas].
- **Presupuesto de textura**: la memoria de textura de la escena es un presupuesto tan real como el de tris. Auditar con el Memory Profiler en el device, no a ojo [ver: unity-movil-rendimiento].

## 6. Post-processing en móvil: caro por definición

Un stack de post es un **pass fullscreen** = releer y reescribir todo el framebuffer = el peor caso de bandwidth en TBDR. Regla: menos es más, y solo los efectos que doc oficial marca eficientes en móvil.

| Efecto | Móvil | Ajuste móvil |
|---|---|---|
| **Bloom** | Sí, con cuidado | High Quality Filtering **OFF**, Downscale **Quarter**, bajar Max Iterations (default 6). Requiere HDR + emission > threshold [ver: unity/rendering-urp §8] |
| **Vignette / Color Adjustments / Tonemapping** | Sí | Baratos; el "grading" básico. Un tonemapper (Neutral/ACES) y todo el arte se calibra con él |
| **Chromatic Aberration / Lens Distortion** | Sí (doc los lista eficientes) | Puntuales |
| **Depth of Field** | Evitar; si acaso **Gaussian**, nunca Bokeh | Caro; requiere depth |
| **Motion Blur** | ⛔ Evitar en móvil | Caro y suele marear |
| **SSAO / screen-space effects** | ⛔ Solo mid/high-end | Requieren depth/normals = passes + bandwidth; hornear AO en el lightmap |

Eficientes en móvil según docs Unity: **Bloom (HQ off), Chromatic Aberration, Color Grading, Lens Distortion, Vignette** [ver: unity/rendering-urp §8]. Un juego entero pasa con 3-4 overrides. Si el juego apunta a low-end, evaluar **sin post-processing** y meter el "look" en el arte baked (§8).

## 7. Batching e instancing en móvil

La mecánica está en [ver: unity/rendimiento-unity] y [ver: unity/rendering-urp §2]; matices móviles:

| Técnica | Nota móvil |
|---|---|
| **SRP Batcher** | ON siempre. Diseñar con pocos shaders y muchos materiales; no romperlo con `MaterialPropertyBlock` por instancia |
| **GPU Instancing** | Para muchos objetos idénticos (props, follaje, balas). Requiere shader instancing-compatible. La forma barata de dibujar 500 rocas iguales |
| **Static Batching** | Combina meshes estáticos → menos draw calls, pero **infla memoria** (copia la geometría combinada) y **compite con GPU Resident Drawer**. En móvil con RAM ajustada, medir memoria antes de abusar |
| **GPU Resident Drawer / GPU Occlusion Culling (Unity 6)** | Aportan en 3D con miles de objetos repetidos; requieren Forward+ y solo cubren MeshRenderer. Para un juego 2D o 3D chico móvil, no activarlos "porque están" [ver: unity/rendering-urp §14] |
| **Dynamic Batching** | Legacy; casi siempre lo supera SRP Batcher/instancing. No confiar en él |

Verificar el batching REAL con el **Frame Debugger** sobre el device, nunca asumirlo [ver: unity/rendimiento-unity].

## 8. El look que rinde en móvil: estilizado, flat, baked

No es solo estética: es **la consecuencia directa del hardware** de las §0-§6. El estilizado/flat/baked domina el móvil porque cada decisión de ese look **elimina un coste caro en TBDR**:

| El look estilizado/flat/baked… | …porque el hardware móvil… |
|---|---|
| Iluminación **baked** en lightmaps | evita luces realtime per-pixel y shadow maps (fillrate + bandwidth) — §2 |
| Shaders **Unlit/Simple Lit**, colores planos | evita PBR por píxel × overdraw — §3 |
| Sombras horneadas / gradientes pintados en textura | evita sombras realtime y post-processing fullscreen — §2, §6 |
| Paletas limpias, pocas transparencias | reduce overdraw, el enemigo #1 — §4 |
| Siluetas fuertes low-poly | menos vértices en GPU tile-based, menos micro-triángulos — [ver: modelado/presupuestos-poligonos §2] |
| Menos batería y menos calor | menos bandwidth = sesiones más largas, menos throttling |

El detalle de dirección de arte, referencias y por qué además **envejece mejor y es más barato de producir** está en [ver: arte-movil]. Aquí basta la causa técnica: el realismo PBR con muchas luces realtime es exactamente lo que el TBDR y el fillrate castigan.

## 9. Presupuesto gráfico móvil (referencia con fuente)

Cifras ancla para arrancar; el número final se mide en el device target caliente [ver: modelado/presupuestos-poligonos §3, §7].

| Recurso | Móvil gama media | Fuente / nota |
|---|---|---|
| Tris en pantalla / frame | ~200k orientativo (suelo conservador) | Demo Armies RTS de Android: ~210k tris/frame a 30 FPS |
| Verts por mesh | **65,535** máx garantizado (índices 16-bit) | Android dev guide; pasarse fuerza 32-bit (más memoria) |
| Triángulo mínimo en pantalla | > ~10 px² a su distancia real | Android dev guide (micro-triángulos) |
| Protagonista | 4k–15k tris | [ver: modelado/presupuestos-poligonos §3] |
| NPC / enemigo | 1k–8k tris | idem |
| Personaje de multitud | 300–2k tris (~360 real en Armies) | Android dev guide |
| Textura hero (tope) | 2048; grueso 1024/512 | ref. MetaHuman móvil topa a 2048 |
| Additional lights por cámara | **32** móvil / **16** GLES3.0- | Unity "Light limits in URP" |
| Partículas vivas (Shuriken) | cientos–~1-2k (orientativo) | fillrate manda, no el count [ver: vfx-shaders/optimizacion-vfx §4] |
| Overdraw pico | 2-3× pantalla (orientativo) | medir en device |
| Draw calls | perfilar; atacar antes que re-modelar | [ver: unity/rendimiento-unity] |

⚠️ Los rangos marcados "orientativo" NO son doc oficial verificada — punto de partida, se validan con Profiler/Frame Debugger en el device. Solo los números con fuente citada (65,535; 10 px²; 210k Armies; 32/16 luces; 2048) son duros.

## 10. Verificar en el device real (no en el editor)

El editor sobre tu PC **esconde** el coste de fillrate y de bandwidth — un frame que va sobrado en el editor tanquea el teléfono [ver: vfx-shaders/optimizacion-vfx §9]. Protocolo móvil:

1. **Development Build en el device target más débil**, Profiler conectado (GPU + Memory).
2. **Device caliente**: probar tras 10+ min; el throttling térmico recorta el fillrate sostenible. El presupuesto es el pico sostenido caliente, no el pico frío.
3. **Peor caso de gameplay**, no la escena media: la pantalla con más enemigos + VFX + UI a la vez.
4. **GPU-bound vs CPU-bound**: si domina `Gfx.WaitForPresentOnGfxThread` es fillrate/overdraw (esta base); si es CPU/GC/físicas, ir a [ver: unity-movil-rendimiento].
5. Si tanquea el GPU, en ESTE orden: recortar **overdraw/capas** → **render scale** → **resolución de textura/post** → **shader a Unlit/Half** → geometría. El fillrate manda.

## Reglas prácticas

1. Diseña asumiendo TBDR: el fillrate es el rey, el bandwidth es la batería. Menos píxeles repintados, menos passes fullscreen.
2. **Render scale 0.7–0.9** es la palanca de rendimiento móvil más directa: casi invisible, recupera 20-30% de GPU. Súbela con FSR/STP si se ve blanda.
3. Un URP Asset por quality level; el móvil va con Forward, HDR off en low-end, additional lights Per Vertex, soft shadows off, shadow max distance corta.
4. MSAA 2x-4x sí (barato en tile), PERO ojo: activar Opaque Texture puede **anular** el MSAA en plataformas sin StoreAndResolve.
5. Depth/Opaque Texture OFF salvo que un shader los pida; nada que obligue a releer el framebuffer resuelto (GrabPass, blits a media escena).
6. Ilumina baked: lightmaps + APV para dinámicos. Realtime solo lo que de verdad se mueve; una Directional como máximo dado por sentado. Reflection probes baked.
7. Lighting Mode: **Subtractive** low-end, **Shadowmask** mid; sombras realtime son un lujo, no un default.
8. Shader más barato que dé el look: Unlit/Simple Lit antes que Lit. Half precision por defecto, per-vertex sobre per-pixel, evita transcendentes y `clip` en transparentes.
9. Overdraw primero: mídelo con Scene → Overdraw ANTES de tocar nada; ataca UI transparente apilada y partículas grandes.
10. **ASTC** como formato base (6×6 albedo, 4×4/5×5 normal maps, 8×8 fondos); ETC2 fallback Android. Nunca sin comprimir salvo excepción puntual.
11. **Mipmaps ON** en todo lo de distancia variable (cuesta +33% memoria, lo vale); OFF solo en UI/sprites a tamaño fijo.
12. Texturas: tope 2048 hero, 1024/512 el grueso; baja resolución de máscaras no críticas; bilinear + 2× aniso, no trilinear.
13. Atlas + channel packing para bajar draw calls y samples; packed textures en linear.
14. Post-processing al mínimo: Bloom (HQ off, downscale quarter) + Vignette + Color/Tonemapping. ⛔ Motion Blur, DoF Bokeh, SSAO en low-end. Evalúa sin post en low-end.
15. SRP Batcher ON siempre; GPU instancing para lo repetido; cuidado con static batching (memoria) y con activar GPU Resident Drawer en juegos chicos.
16. El look estilizado/flat/baked no es "menos ambicioso": es el que el hardware móvil premia (menos overdraw, menos luces, menos calor) [ver: arte-movil].
17. Presupuesto gráfico con las cifras ancla (65,535 verts, >10px² por tri, 210k tris/frame de referencia, 32/16 luces) y ajústalo midiendo.
18. Verifica SIEMPRE en el device más débil, **caliente**, en el peor caso de gameplay — el editor miente en GPU.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Firmar el look en el editor de PC ("va a 120 FPS") | El editor esconde fillrate y bandwidth; Development Build en device débil, caliente, peor caso |
| Luces realtime con sombra "porque se ve mejor" | Cada una es fillrate + un shadow map; baked + APV, realtime solo lo que se mueve |
| Poner shader Lit (PBR) a todo | Simple Lit/Unlit para estilizado; el PBR por píxel × overdraw revienta el low-end |
| Activar Opaque Texture y perder el MSAA sin saber por qué | En plataformas sin StoreAndResolve, Opaque Texture ignora el MSAA; quita una de las dos |
| Depth/Opaque Texture "por si acaso" | Cada una = pass + bandwidth; OFF hasta que un shader las use de verdad |
| Texturas sin comprimir o en un solo block size global | ASTC por asset (4×4 normals, 6×6 albedo, 8×8 fondos); ETC2 fallback |
| Mipmaps desactivados "para ahorrar memoria" | Sin mips hay shimmer y se quema bandwidth muestreando texels de más; el +33% se paga con gusto |
| Subir aniso/trilinear por calidad | Filtering es hasta 50% de la energía GPU; bilinear + 2× aniso es el balance |
| Stack de post-processing completo en móvil | Cada pass fullscreen releé todo el framebuffer (peor caso TBDR); 3-4 overrides máx, Bloom HQ off |
| Motion Blur / DoF Bokeh / SSAO en low-end | Caros y/o marean; hornear AO en lightmap, evitar screen-space en low-end |
| Optimizar geometría mientras la escena tiene overdraw brutal | Mide overdraw primero (Scene → Overdraw); el fillrate manda sobre los tris |
| Resolución nativa a toda costa en pantalla densa | Render scale 0.85 + upscaler: invisible y recupera GPU |
| GrabPass / blit a media escena para efectos | Fuerza flush del tile a RAM (mata el TBDR); resolver con shaders sin releer framebuffer |
| Static batching a lo loco en un juego con RAM ajustada | Infla memoria (copia geometría) y compite con GPU Resident Drawer; medir |
| Confiar en presupuestos AAA copiados de un foro | Usar los techos de móvil con fuente (§9) y validar en el device |
| Ignorar el throttling térmico | Presupuestar el pico SOSTENIDO caliente, no el frío de 30 s |

## Fuentes

Consultadas en esta investigación (2026-07-20), Unity 6 (docs 6000.2) salvo indicación. Nota: el WebSearch estaba agotado esta sesión; las verificaciones se hicieron por WebFetch directo a las páginas primarias y por cruce con las bases hermanas ya verificadas del repo.

- **Optimizing graphics performance / mobile rendering and shaders — Unity Manual 6000.2** (fetch directo) — fill rate como cuello móvil ("la GPU intenta dibujar más píxeles de los que puede"), overdraw de UI/partículas/sprites, elegir shaders de categorías **Mobile/Unlit**, reducir luces realtime per-pixel y usar **lightmapping**, mipmaps y compresión de texturas, LOD.
- **Universal Render Pipeline Asset — Unity Manual 6000.2** (fetch directo, versión versionada) — settings móviles verificados: HDR default ON (desactivar en low-end), **MSAA default disabled y ignorado si Opaque Texture está activa en plataformas sin StoreAndResolve**, Render Scale <1.0 reduce carga GPU, Additional Lights **Per Vertex** mobile-friendly, **Soft Shadows off (alto impacto en render tile-based)**, Depth/Opaque Texture off por bandwidth, LOD Cross Fade off quita variantes.
- **Best practices for textures — Android Game Development guide (Google)** (fetch directo) — **ASTC formato primario recomendado (75%+ de dispositivos), ETC2 fallback (90%+)**, ETC1 legacy; mipmaps **+33% memoria**; texture filtering **hasta 50% de la energía GPU**, recomendación **bilinear + 2× aniso**; atlasing para draw calls; channel packing (AO/rough/metal en RGBA linear); reducir resolución de máscaras no críticas.
- **Vertex data management — Android Game Development guide (Google)** (fetch directo) — bandwidth de vértices/binning en GPU tile-based, UNORM16, coste de fetch de datos por vértice; refuerza que el vertex count pega más en tile-based.
- **[ver: unity/rendering-urp]** (base hermana, ya verificada contra Unity Manual 6000.2) — Forward vs Forward+/Deferred, **límites de additional lights por cámara: 32 móvil / 16 GLES3.0-**, Lighting Modes Subtractive/Shadowmask, APV, Bloom móvil (HQ off, Downscale Quarter), efectos de post eficientes en móvil, Depth Texture "After Transparents".
- **[ver: vfx-shaders/optimizacion-vfx]** (base hermana, ya verificada contra Unity Manual) — overdraw como enemigo #1, fillrate en TBDR, `half` vs `float`, per-pixel vs per-vertex, `clip`/`discard` rompe early-Z, Particles/Unlit, medir overdraw con Scene Draw Mode / Rendering Debugger.
- **[ver: modelado/presupuestos-poligonos]** (base hermana, ya verificada) — **65,535 verts/mesh (16-bit) máx en móvil**, **micro-triángulos <10 px²**, demo **Armies ~210k tris/frame a 30 FPS** y ~360 tris por unidad de multitud, MetaHuman móvil (best LOD ~4k verts, texturas máx 2048), Arm Real-Time 3D Art Best Practices (4× MSAA barato en GPUs Mali, aliasing geométrico), tile-based procesa geometría por tile.
- **ASTC bits-por-píxel** — aritmética sobre la definición del formato (bloque de 128 bits): 4×4=8.0, 5×5=5.12, 6×6=3.56, 8×8=2.0, 10×10=1.28, 12×12=0.89 bpp. El "ASTC recomendado" y los % de soporte son de la guía de Android; los bpp son derivación directa del tamaño de bloque, no un dato de foro.
- **NO verificado en vivo esta sesión** (Arm/Apple son SPAs que WebFetch no pudo leer): el mecanismo detallado de tile memory on-chip de **Apple GPU (TBDR)** y las cifras finas de coste de MSAA/framebuffer-fetch de **Arm Mali** se afirman a nivel general (bien documentado y coherente con las bases verificadas), pero sus números exactos NO se releyeron de la fuente primaria en esta pasada — validar contra Apple "Tailor Your Apps for Apple GPUs and TBDR" y Arm GPU Best Practices Developer Guide antes de citar cifras específicas.
