# VFX y shaders 2D

> **Cuando cargar este archivo:** al construir efectos y shaders para un juego 2D real en Unity 6 / URP — hit flash de sprite, dissolve, outline, agua/wobble con Shader Graph target Sprite; explosión/impacto como spritesheet o como Particle System 2D; trails y afterimages; luces 2D como efecto; y el juice barato de pixel art (flash, pocas partículas, shake) sin romper el estilo. Es el "cómo se hace el efecto 2D concreto": los NODOS, módulos y settings. El PORQUÉ del feel vive en otro lado (abajo).

Este archivo NO repite lo resuelto en otras bases — lo referencia y añade el ángulo 2D:

- **Por qué un hit flash vende el golpe, hitstop, screenshake=trauma², repertorio de juice, S&S** → [ver: gamedev/game-feel]. Aquí va el shader/VFX que lo implementa, no la teoría.
- **La implementación base del feel en Unity (Cinemachine Impulse para shake, punch/flash por tween, Particle System Shuriken módulo a módulo, pooling de VFX)** → [ver: pipeline/feel-en-unity]. Aquí solo lo que cambia en 2D y las recetas de shader.
- **Luces 2D (Light 2D) y sorting en 2D** → [ver: unity/rendering-urp]. Aquí se usan como EFECTO, no se re-explica el sistema.
- **La explosión/impacto DIBUJADO frame a frame (frame counts, anatomía nace→pico→muere)** → [ver: arte-2d/animacion-2d §8]. Aquí ese spritesheet se reproduce en el motor.
- **Import de sprites, Sprite Atlas, Pixel Perfect, overdraw** → [ver: arte-2d/2d-a-unity] y [ver: unity/rendering-urp].
- **Fundamentos de Shader Graph / VFX Graph / partículas GPU en profundidad** → [ver: shader-graph-fundamentos], [ver: particulas-vfx-graph], [ver: optimizacion-vfx] dentro de esta misma base.

**Versión:** Unity 6 (6000.x) · URP con **2D Renderer** · Shader Graph 17.x · nodos/módulos verificados contra doc oficial (jul-2026). Datos version-dependientes marcados.

---

## 1. El mapa: qué herramienta para cada efecto 2D

| Efecto | Herramienta | Por qué |
|---|---|---|
| Explosión / impacto / muzzle **dibujado** | **Spritesheet animado** (Sprite Renderer + Animator, o Particle System modo Sprites) | El arte ya lo dibujó frame a frame [ver: arte-2d/animacion-2d §8]; máximo control estético, cero física |
| Chispas, humo, debris, polvo | **Particle System (Shuriken)** con sprites | Física CPU, colisión, `OnParticleCollision`, pooling — el caballo de batalla del juice [ver: pipeline/feel-en-unity §6] |
| Hit flash, dissolve, outline, agua/wobble, tint | **Shader Graph, target Sprite** | Efecto por-pixel sobre el sprite, driven por una propiedad que un script anima |
| Lluvia/nieve/enjambre/magia de pantalla masiva | **VFX Graph** (GPU) | Miles→millones de partículas; NO para hits que interactúan con física (§8) |
| Estela de proyectil / dash | **Trail Renderer** o Trails module del Particle System | Barato, geométrico (§7) |
| Afterimage / motion ghost | **Ghosts de sprite** (pool de copias que fade) | Vende velocidad sin shader (§7) |
| Atmósfera, "quemar" un neón, foco | **Light 2D** (Spot/Sprite/Global) + **Bloom** | El efecto es la luz, no un sprite [ver: unity/rendering-urp §Luces 2D] |
| Impacto de cámara | **Cinemachine Impulse** (shake) + kick | Cross-ref, no se reimplementa [ver: pipeline/feel-en-unity §3] |

Regla de oro 2D: **si el efecto "no dobla" y es puramente visual, spritesheet o partículas; si necesita reaccionar por-pixel al sprite (flash, disolver, contorno), shader; si necesita física, Shuriken.** El shader NO reemplaza a la animación dibujada — la complementa.

---

## 2. Shader Graph con target Sprite: el setup

En **Graph Settings** (pestaña del Graph Inspector), con URP activo, el dropdown **Material** ofrece los targets 2D:

| Material target | Qué es | Cuándo |
|---|---|---|
| **Sprite Unlit** | Sprite sin iluminación; ignora las Light 2D | Efectos que "brillan solos" (impactos additive, UI, pixel art plano sin luces) |
| **Sprite Lit** | Sprite que reacciona a las **Light 2D** (usa normal map, mask) | Juego con luces 2D; el sprite recibe sombreado direccional |
| **Sprite Custom Lit** | Sprite Lit con tu propio modelo de iluminación por Blend Style | Estilizado avanzado; raro en indie |

**Bloques del Master Stack relevantes** (verificados en Built-In Blocks; los del vertex: Position, Normal, Tangent):
- **Base Color** (Vector3) — el color del pixel.
- **Alpha** (Float) — transparencia.
- **Alpha Clip Threshold** (Float) — **aparece solo si activas Alpha Clipping** en Graph Settings; los fragmentos con alpha por debajo se descartan (clave del dissolve, §4).
- **Normal (Tangent Space)** (Vector3) — solo en Sprite Lit; alimenta el normal map (§9).
- **Emission** (Vector3) — solo en targets Lit; empuja color a HDR para que Bloom lo agarre. En Sprite Unlit no hay bloque Emission: se multiplica el Base Color >1 (con Bloom + HDR) para el mismo efecto.

**Cómo llega el sprite al graph** (el gotcha #1 de shaders 2D): el Sprite Renderer bindea automáticamente la textura del sprite a la propiedad con reference **`_MainTex`**. Para muestrear el propio sprite (outline, dissolve), añade una propiedad **Texture2D** con Reference `_MainTex` y sampléala con **Sample Texture 2D**; su UV es el UV0 del sprite. Sin esa propiedad, el graph no "ve" la textura del sprite. *(El auto-bind `_MainTex` es comportamiento estándar del Sprite Renderer; confirmar en tu versión — algunos flujos usan un Texture2D expuesto asignado a mano.)*

**Asignar el shader:** crea un **Material** desde el graph → arrástralo al campo Material del **Sprite Renderer**. El sprite ahora se dibuja con tu shader.

---

## 3. Receta: Hit flash (tint a blanco)

El efecto #1 del juice 2D — sprite a blanco 1–3 frames al recibir daño (por qué funciona: [ver: gamedev/game-feel §2]). Se hace con **Lerp**, no reemplazando el color.

**Nodos** (target Sprite Unlit o Lit):
1. **Sample Texture 2D** (`_MainTex`, UV = UV0) → RGBA.
2. Propiedad **Float** `_FlashAmount` (0→1, expuesta, default 0).
3. Color blanco: nodo **Color** (o Vector3 1,1,1). Para "quemar" con Bloom, usa (2,2,2) HDR.
4. **Lerp**: A = RGBA.RGB del sample, B = blanco, **T** = `_FlashAmount` → **Base Color**.
5. **Alpha** = RGBA.A del sample (respeta la silueta — flashea la forma, no un cuadro).

**El script** (setea la propiedad; el flash es un pulso, no un estado):
```csharp
static readonly int Flash = Shader.PropertyToID("_FlashAmount");
[SerializeField] float flashTime = 0.06f;   // ~3 frames a 50 fps
MaterialPropertyBlock mpb;                   // ⚠️ NO material.SetFloat: instancia el material y rompe batching

public void HitFlash() { StopAllCoroutines(); StartCoroutine(FlashCo()); }
IEnumerator FlashCo() {
    var sr = GetComponent<SpriteRenderer>();
    mpb ??= new MaterialPropertyBlock();
    sr.GetPropertyBlock(mpb); mpb.SetFloat(Flash, 1f); sr.SetPropertyBlock(mpb);
    yield return new WaitForSeconds(flashTime);
    sr.GetPropertyBlock(mpb); mpb.SetFloat(Flash, 0f); sr.SetPropertyBlock(mpb);
}
```
- **MaterialPropertyBlock** (no `renderer.material`) para no instanciar el material por objeto (rompería el SRP Batcher / atlas batching).
- Dispara el flash en el **mismo frame** del hit, junto al hitstop y el SFX [ver: pipeline/feel-en-unity §2].
- Pixel art: `_FlashAmount` binario (0 o 1) se ve más "duro/correcto" que un lerp suave; no interpoles la rampa.

---

## 4. Receta: Dissolve 2D

Desintegrar un sprite (muerte de enemigo, teleport, spawn inverso). Técnica: ruido + umbral animado + **Alpha Clip**.

**Setup:** Graph Settings → **Alpha Clipping = ON** (habilita el bloque **Alpha Clip Threshold**).

**Nodos:**
1. **Simple Noise** (UV = UV0, Scale ~20–60) → Out (0..1). *(O **Gradient Noise** para grano más orgánico; o **Voronoi** para disolver "en celdas".)* Para pixel art, samplea en su lugar una textura de ruido con **Point filter** (o **Posterize** el ruido) para que el borde disuelva en bloques, no en gradiente suave.
2. Propiedad **Float** `_Dissolve` (0→1, expuesta).
3. **Step** (Edge = `_Dissolve`, In = noise) → Out: 1 donde el ruido supera el umbral, 0 donde no. Conéctalo (o `noise` directo) al **Alpha** y sube `_Dissolve` de 0→1 para ir borrando.
   - Vía canónica: manda `noise` a **Alpha** y `_Dissolve` a **Alpha Clip Threshold**: al subir el threshold se van descartando los fragmentos de menor ruido → el sprite se "come" a sí mismo.
4. **Borde incandescente** (el detalle que lo vende): con **Step**, aísla la franja `noise ∈ [_Dissolve, _Dissolve+ancho]` (dos Steps restados, o Smoothstep para franja suave — *Smoothstep no re-verificado esta pasada*), multiplícala por un **Color** HDR brillante y súmala al **Base Color** (con **Emission** en target Lit para Bloom).

**Script:** animar `_Dissolve` 0→1 con un tween/coroutine (~0.3–0.6 s), ease-in [ver: gamedev/game-feel §5]. Reverse (1→0) = materializar.

---

## 5. Receta: Outline de sprite

Contorno para selección/hover/telegraph. Técnica: muestrear el alpha del sprite **desplazado** en 4 (u 8) direcciones y comparar con el propio.

**Nodos:**
1. Propiedad **Float** `_OutlineWidth` (en UV; ~1–3 px ÷ ancho de textura).
2. Cuatro **Tiling And Offset**: Tiling = (1,1), Offset = (±width, 0) y (0, ±width) → 4 UVs vecinos.
3. Cuatro **Sample Texture 2D** (`_MainTex`) en esos UVs → tomar el canal **A**. Combínalos con **Maximum** (o Add + Saturate) → `vecino_alpha`.
4. **Subtract**: `vecino_alpha − alpha_propio` → máscara del borde (1 justo fuera de la silueta, 0 dentro).
5. **Lerp**: A = color del sprite, B = **Color** del outline, T = máscara → **Base Color**.
6. **Alpha** = `max(alpha_propio, máscara)` para que el contorno se dibuje fuera de la silueta original.

**Gotchas:**
- El outline se **recorta en el borde del quad**: el sprite necesita **padding transparente** alrededor (≥ `_OutlineWidth` px) o el contorno se corta. Con Sprite Atlas, cuida el `extrude/padding` [ver: arte-2d/2d-a-unity §5].
- Mesh Type del sprite en **Full Rect**, no Tight — Tight recorta el quad a la silueta y no deja sitio para el borde.
- Alternativa sin shader: Sprite Renderer duplicado detrás, escalado o con material sólido (más barato para pocos objetos; peor para siluetas cóncavas).

---

## 6. Receta: Water / wobble 2D (distorsión UV)

Ondulación de agua, calor, "jelly", bandera. Técnica: desplazar el **UV** con una función del tiempo antes de muestrear.

**Wobble simple (auto-distorsión del propio sprite):**
1. Nodo **Time** → salida Time.
2. **Sine** de `(UV.y * frecuencia + Time * velocidad)` → desplazamiento horizontal ondulante (multiplícalo por una amplitud pequeña, ~0.01–0.05 UV).
3. Suma ese desplazamiento al UV (o usa **Tiling And Offset** con Offset animado) → UV distorsionado.
4. **Sample Texture 2D** (`_MainTex`) con el UV distorsionado → Base Color.
- **Twirl** (UV, Center, Strength, Offset → Out) para remolinos/portales en vez de onda senoidal.

**Agua con refracción (distorsionar lo que está DETRÁS):**
- Target Sprite con **Surface = Transparent**. Usa **Scene Color** (samplea el opaque/color buffer antes de transparentes; solo URP/HDRP, solo fragment): añade un pequeño offset animado (Simple Noise o Sine) al UV de pantalla y muestrea Scene Color → agua/heat-haze que refracta el fondo.
- ⚠️ En el **2D Renderer** la refracción de sprites (que también son transparentes) NO va por el opaque texture normal: se usa la **Camera Sorting Layer Texture** del 2D Renderer Data (captura las capas por debajo de un punto para muestrearlas en shader) [ver: unity/rendering-urp §Luces 2D]. Actívala en el 2D Renderer Data y muestréala; sin eso, Scene Color solo ve objetos opacos.

---

## 7. Partículas, trails y afterimages en 2D

### Particle System (Shuriken) en 2D
El detalle módulo a módulo (Main, Emission/Bursts, Shape, Color/Size over Lifetime, Collision, Sub Emitters, Ring Buffer, pooling) ya está en [ver: pipeline/feel-en-unity §6]. Lo específico de 2D:

- **Renderer module:** Render Mode = **Billboard** (default; siempre de cara a cámara ortográfica); **Sorting Layer ID** + **Order in Layer** iguales a los sprites (ponlas en la capa "FX"); **Sorting Fudge** para desempatar contra otros transparentes. Sin esto, las partículas aparecen detrás/delante mal [ver: unity/rendering-urp §Sorting en 2D].
- **Simulation Space = World** para impactos: las partículas no siguen al emisor si el objeto muere o se mueve.
- **Texture Sheet Animation** module (verificado): **Mode = Sprites** para reproducir un spritesheet de explosión del atlas del juego (o **Grid** con **Tiles** X/Y). **Time Mode** (Lifetime / Speed / FPS), **Frame over Time** (curva), **Start Frame**, **Cycles**. Así una explosión DIBUJADA [ver: arte-2d/animacion-2d §8] se emite como partícula que además se mueve/escala.
- **Material:** para additive luminoso (chispa, fuego) usa un material con blending aditivo; para humo/polvo, alpha blend.

### Trail Renderer (estelas)
Componente **Trail Renderer** (verificado). Propiedades clave: **Time** (vida de cada punto, s), **Min Vertex Distance** (distancia mínima entre puntos), **Width** (valor + curva a lo largo), **Color** (gradiente a lo largo; fija Alpha→0 al final), **Materials**, **Alignment** (View = de cara a cámara, TransformZ), **Texture Mode** (Stretch/Tile/DistributePerSegment/RepeatPerSegment). Para 2D: material transparente/additive, Sorting Layer en FX. Úsalo para dash, proyectil, cometa. (El **Trails** module del Particle System hace lo mismo por-partícula.)

### Afterimages / motion ghost
Sin shader: al hacer dash, **instancia N copias** del sprite actual (mismo `sprite`, `flipX`), cada una con un material/tint que hace fade de alpha→0 en ~0.2 s, en la capa por detrás del jugador. Poolea las copias (nunca Instantiate/Destroy por frame [ver: unity/csharp-patrones]). Vende velocidad extrema barato; combina con Trail para lo mejor de ambos.

### Squash & stretch en 2D
En 2D es gratis y estilístico [ver: arte-2d/animacion-2d §4]. Impl por **transform.localScale** con conservación de volumen (x×1.3 → y×0.77) y retorno elástico por tween/punch — patrón exacto en [ver: pipeline/feel-en-unity §4]. Por shader (vertex) solo si necesitas que el pivote/eje sea complejo; para sprites, el transform basta.

---

## 8. VFX Graph en 2D: cuándo sí

VFX Graph corre en **GPU** (compute shaders; URP/HDRP), escala a millones de partículas — vs Shuriken (miles, CPU). Contexts: **Spawn → Initialize → Update → Output**. El Output relevante para 2D es un **Output Particle** con primitiva **Quad** mapeada a un sprite/textura (los nombres exactos de cada variante Output no se enumeran en la doc de índice — verificar en el editor).

**Cuándo en un juego 2D:**
- SÍ: espectáculo ambiental masivo — lluvia/nieve de pantalla, enjambres, tormenta de partículas de un jefe, magia de fondo. Cientos de miles de quads que NO necesitan lógica CPU.
- NO: hits, debris que rebota, pickups, cualquier VFX que deba interactuar con física CPU o notificar colisión — VFX Graph no da `OnParticleCollision` ni lee partículas individuales desde C# (solo propiedades/eventos expuestos). Eso es Shuriken [ver: pipeline/feel-en-unity §6].

**Gotcha 2D:** VFX Graph no se integra con el **sorting layer** 2D como el Sprite Renderer; ordenar sus quads respecto a los sprites (que estén detrás del fondo o delante del jugador) es manual (posición Z / cámara / orden de render). Por eso el 99% del juice 2D indie es Shuriken, no VFX Graph. Detalle GPU en [ver: particulas-vfx-graph].

---

## 9. 2D Lights como efecto

El sistema (tipos de Light 2D, Blend Styles, 2D Renderer Data, setup mínimo) está en [ver: unity/rendering-urp §Luces 2D]. Usarlo como EFECTO/juice:

| Efecto | Cómo |
|---|---|
| **Sprite con volumen** (reacciona a la luz) | Sprite con **Secondary Texture** normal map (suffix `_NormalMap` en el import) + target **Sprite Lit** → la luz da dirección/relieve. Normal Map Quality en la Light 2D: Fast/Accurate |
| **Muzzle / explosión que "quema"** | Un **Light 2D Spot** de vida corta (script: intensity alto → 0 en ~0.1 s) en el punto de disparo — ilumina el entorno un frame, no solo el sprite |
| **Flicker de antorcha/neón** | Script que oscila `Light2D.intensity` con Perlin noise (mismo principio que el shake [ver: gamedev/game-feel §4]) |
| **Cookie / forma de luz** | Light 2D tipo **Sprite**: un sprite como máscara de luz (rayos, ventana, foco de linterna) |
| **Glow real** | Emission/HDR en el material + **Bloom** en el Volume [ver: unity/rendering-urp §Post-processing] — el bloom hace el trabajo, la Light 2D ilumina alrededor |
| **Atmósfera** | 1 Global Light ambiente (~0.2–0.5) + Spots/Freeform de color para mood; sombras con **ShadowCaster2D** |

Barato y potente: un impacto = flash de sprite (§3) + burst de partículas (§7) + un Light 2D Spot de 0.1 s. Tres capas, cero arte nuevo.

---

## 10. Screen shake y juice en 2D: qué comparte, qué es propio

El shake bien hecho (trauma², Perlin, Cinemachine Impulse) y todo el repertorio de juice están en [ver: gamedev/game-feel §4] y [ver: pipeline/feel-en-unity §3] — **no se reimplementan aquí**. Lo específico de 2D:

- **Shake 2D = traslación + rotación** (Eiserloh: 2D solo-rotación "kinda lame"; 2D trasl.+rot. "awesome"). En 3D sería solo rotación; en 2D la cámara ortográfica puede trasladarse sin atravesar geometría, así que traslada Y rota [ver: gamedev/game-feel §4].
- **Camera kick direccional** además del shake, en la dirección del golpe/disparo (Vlambeer) — el shake es ruido, el kick es dirección.
- **Cuidado con Pixel Perfect**: el shake de traslación sub-pixel pelea con la **Pixel Perfect Camera** (que engancha a la grid). O desactivas Pixel Snapping durante el shake, o haces el shake en múltiplos enteros de pixel, o aceptas el jitter [ver: arte-2d/2d-a-unity §6]. Es un conflicto real y propio del 2D pixel art.
- **Hitstop** = `Time.timeScale` a ~0 unos frames (con `unscaledDeltaTime` para lo que debe seguir vivo) — igual que 3D [ver: pipeline/feel-en-unity §2].

Comparte con 3D: hitstop, tweening/easing, flashes, sonido por evento, números flotantes, permanencia (casquillos/cráteres que quedan). Propio del 2D: shake traslacional permitido, S&S gratis por sprite, flash por-sprite trivial, y todo el conflicto con la grid de pixel art.

---

## 11. VFX barato y efectivo para pixel art (sin romper el estilo)

El pixel art se rompe con efectos "suaves" de alta resolución (gradientes finos, blur, partículas smooth). El juice debe respetar la grid:

| Técnica | Cómo NO romper el pixel art |
|---|---|
| **Hit flash** | Binario (0/1), no rampa suave; flashea la silueta (Alpha del sprite). El más barato y el que más pega |
| **Partículas** | Pocas y **grandes en pixel** (cada partícula = varios px, textura Point/None), sin fade de alpha suave — o fade escalonado. Nada de humo gaussiano de 500 partículas |
| **Dissolve** | **Posterize** el ruido o usa textura de ruido Point → disuelve en bloques de pixel, no en gradiente |
| **Shake** | En múltiplos enteros de pixel (o desactiva Pixel Snapping durante el shake); si no, tiembla feo |
| **Chispas dibujadas** | Un spritesheet de 2–4 frames de chispa (arte, no partículas) da el look más consistente [ver: arte-2d/animacion-2d §8] |
| **Bloom** | Con MUCHA moderación — un pelín en emisores; demasiado bloom "lava" el pixel art. Threshold alto |
| **Outline** | 1 px de ancho, color de la paleta; el contorno más grueso se ve no-pixel |
| **Additive** | Un flash additive de 1–2 frames sí; capas additive permanentes bajan el contraste del pixel art |

Setup base pixel art para que NADA del pipeline suavice el efecto: sprites/atlas en **Point (no filter)** + Compression **None**, PPU consistente, **Pixel Perfect Camera** [ver: arte-2d/2d-a-unity §3, §6]. Un efecto smooth sobre pixel art se nota más que la ausencia del efecto.

---

## 12. Optimización (lo justo)

El detalle (overdraw, Sprite Atlas, draw calls, Frame Debugger) está en [ver: unity/rendering-urp §Sprite Atlas / overdraw] y [ver: optimizacion-vfx]. Lo crítico de VFX 2D:

- **Overdraw es el asesino** en 2D/móvil: cada partícula/quad transparente redibuja pixels. Partículas **pocas, chicas**, sin quads casi-transparentes gigantes "por si acaso" [ver: unity/rendering-urp §overdraw].
- **Pooling siempre**: nunca `Instantiate/Destroy` de sistemas de partículas por impacto — pool con Stop Action = Callback [ver: pipeline/feel-en-unity §6].
- **MaterialPropertyBlock** para animar propiedades de shader por-instancia (flash, dissolve) sin instanciar el material (§3) — o el SRP Batcher / atlas batching se rompe.
- **Un solo atlas por escena de gameplay** para las texturas de VFX + sprites que salen juntos [ver: arte-2d/2d-a-unity §5].

---

## Reglas prácticas

- [ ] Elige herramienta por naturaleza del efecto: dibujado→spritesheet, física→Shuriken, por-pixel→shader, masivo ambiental→VFX Graph. El shader complementa la animación dibujada, no la reemplaza.
- [ ] Shader Graph 2D: Graph Settings → Material = **Sprite Unlit** (brilla solo) o **Sprite Lit** (reacciona a Light 2D). Para muestrear el sprite, propiedad Texture2D con Reference **`_MainTex`**.
- [ ] Hit flash con **Lerp**(color, blanco, `_FlashAmount`) + Alpha del sprite; binario en pixel art; disparado en el mismo frame del hit + hitstop + SFX.
- [ ] Anima propiedades de shader con **MaterialPropertyBlock**, nunca `renderer.material` (instancia el material y rompe batching).
- [ ] Dissolve: Alpha Clipping ON → **Simple/Gradient/Voronoi Noise** + **Step**/**Alpha Clip Threshold**, `_Dissolve` 0→1; borde incandescente con una franja aislada + Emission/HDR.
- [ ] Outline: **Tiling And Offset** ×4 → **Sample Texture 2D** (alpha) → Maximum − alpha propio; el sprite necesita **padding transparente** y Mesh Type **Full Rect** o el borde se recorta.
- [ ] Wobble/agua: desplaza el UV con **Time**+**Sine** (o **Twirl**) antes del Sample; refracción con **Scene Color** (Surface Transparent) o la **Camera Sorting Layer Texture** en 2D Renderer.
- [ ] Partículas 2D: Renderer → **Sorting Layer + Order in Layer** en la capa FX, **Simulation Space World** para impactos, **Texture Sheet Animation** modo Sprites para reproducir explosiones dibujadas.
- [ ] Emite juice con **burst**, no rate; **Color over Lifetime** siempre a alpha 0 (nunca desaparecer en seco) [ver: pipeline/feel-en-unity §6].
- [ ] Trails con **Trail Renderer** (Time, Min Vertex Distance, Width curve, Color gradient→0) o el Trails module; afterimages con pool de sprites que fade.
- [ ] VFX Graph SOLO para ambiental masivo (GPU); jamás para hits que necesitan `OnParticleCollision` o lógica CPU. Su sorting vs sprites es manual.
- [ ] Luces 2D como efecto: normal map (Secondary Texture `_NormalMap`) + Sprite Lit para volumen; Spot de 0.1 s para muzzle/explosión; flicker con Perlin.
- [ ] Shake 2D = **traslación + rotación** + camera kick direccional; cuidado con Pixel Perfect (shake en px enteros o desactiva Pixel Snapping).
- [ ] Pixel art: flash binario, partículas grandes en px con Point filter, dissolve posterizado, bloom mínimo, outline de 1 px. Point/None + PPU consistente + Pixel Perfect Camera.
- [ ] Overdraw: partículas pocas y chicas; pooling con Stop Action = Callback; un atlas por escena; nada de quads casi-transparentes gigantes.
- [ ] Un impacto = flash de sprite + burst de partículas + Light 2D Spot corto + hitstop + shake + SFX. Capas baratas > un efecto caro.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Hit flash reemplazando el color (pierde la forma, "cuadro blanco") | **Lerp** hacia blanco + **Alpha del sprite**; flashea la silueta |
| `renderer.material.SetFloat(...)` para el flash | Instancia el material y rompe el batching → **MaterialPropertyBlock** |
| Outline que se corta en el borde del sprite | Padding transparente ≥ ancho + Mesh Type **Full Rect** (no Tight) + extrude en el atlas |
| Dissolve con gradiente suave sobre pixel art | **Posterize** el ruido o textura de ruido **Point**: disuelve en bloques |
| Partículas 2D detrás/delante mal | Renderer module: **Sorting Layer + Order in Layer** en la capa FX; Sorting Fudge |
| Partículas que siguen al emisor cuando el objeto muere | **Simulation Space = World** |
| Partículas que desaparecen en seco | **Color over Lifetime** → alpha 0 (fade siempre) |
| VFX Graph para hits/debris → sin colisión CPU, sin `OnParticleCollision` | Ese juice es **Shuriken**; VFX Graph solo para ambiental masivo |
| Instantiate/Destroy de partículas por impacto (GC spikes) | Pooling con Stop Action = **Callback** [ver: pipeline/feel-en-unity §6] |
| Shake que hace temblar el pixel art (subpixel) | Shake en px enteros o desactivar Pixel Snapping durante el shake |
| Bloom exagerado que "lava" el pixel art | Threshold alto, intensidad baja; solo en emisores puntuales |
| Refracción de agua que no ve otros sprites (solo opacos) | **Camera Sorting Layer Texture** del 2D Renderer, no Scene Color a secas |
| Sprite Lit que se ve negro | Falta Global Light 2D ambiente (~0.2–0.5) [ver: unity/rendering-urp] |
| Efecto smooth (blur/gradiente) sobre pixel art | Rompe el estilo más que no tener efecto; todo en Point/None y a la grid |
| Emission sin efecto visible | Bloom activo + HDR + Threshold; en Sprite Unlit no hay bloque Emission (multiplica Base Color >1) |

## Fuentes

**Bases de El Estudio (referenciadas, no repetidas):**
- [ver: gamedev/game-feel] — el PORQUÉ: hit flash/shake/hitstop/juice, trauma², S&S, Eiserloh (2D trasl.+rot.), Vlambeer (kick, permanencia).
- [ver: pipeline/feel-en-unity] — impl base en Unity: Cinemachine Impulse (shake), punch/flash por tween, **Particle System Shuriken módulo a módulo**, pooling con Stop Action Callback, MaterialPropertyBlock, VFX Graph vs Shuriken.
- [ver: unity/rendering-urp] — **Light 2D** (tipos, Blend Styles, 2D Renderer Data, Camera Sorting Layer Texture), **sorting en 2D**, Sprite Atlas, overdraw, Bloom/Volumes.
- [ver: arte-2d/animacion-2d §8] — la explosión/impacto DIBUJADO frame a frame (nace→pico→muere). [ver: arte-2d/2d-a-unity] — import, Point/None, Pixel Perfect Camera.

**Fuentes web (verificadas por fetch, jul-2026):**
- **Shader Graph — Simple Noise / Gradient Noise / Voronoi** — Unity Docs `com.unity.shadergraph@17.0` (`Simple-Noise-Node.html`, `Gradient-Noise-Node.html`, `Voronoi-Node.html`) — Simple/Gradient Noise: inputs UV+Scale, Out 0..1; Voronoi: UV+Angle Offset+Cell Density → Out, Cells.
- **Shader Graph — Step / Lerp / Tiling And Offset / Twirl** — Unity Docs `com.unity.shadergraph@17.0` — Step (Edge, In → Out; 1 si In≥Edge); Lerp (A, B, T → Out = A+T(B−A)); Tiling And Offset (UV, Tiling, Offset → Out = UV·Tiling+Offset); Twirl (UV, Center, Strength, Offset → Out, distorsión UV).
- **Shader Graph — Sample Texture 2D** — Unity Docs `com.unity.shadergraph@17.0/Sample-Texture-2D-Node.html` — inputs Texture, UV, Sampler → RGBA, R, G, B, A.
- **Shader Graph — Scene Color** — Unity Docs `com.unity.shadergraph@17.0/Scene-Color-Node.html` — samplea el opaque texture (color buffer antes de transparentes); UV screen-space → Out RGB; requiere Surface Transparent (o render queue 2999/3000); solo URP/HDRP; solo fragment.
- **Shader Graph — Built-In Blocks + Master Stack** — Unity Docs `com.unity.shadergraph@17.0` (`Built-In-Blocks.html`, `Master-Stack.html`) — bloques Fragment: Base Color, Normal (Tangent Space), Emission, Metallic, Smoothness, Alpha, **Alpha Clip Threshold** (aparece al activar Alpha Clipping); contexts Vertex/Fragment.
- **Shader Graph — Node Library** — Unity Docs `com.unity.shadergraph@17.0/Node-Library.html` — categorías Artistic, Channel, Input, Math, Procedural, UV, Utility, Block.
- **Particle System — Texture Sheet Animation module** — Unity Manual 6000.0 (`PartSysTexSheetAnimModule.html`) — Mode (Grid/Sprites), Tiles, Animation (Whole Sheet/Single Row), Time Mode, Frame over Time, Start Frame, Cycles, Row Mode.
- **Trail Renderer** — Unity Manual 6000.0 (`class-TrailRenderer.html`) — Time, Min Vertex Distance, Width (valor+curva), Color (gradiente), Materials, Alignment (View/TransformZ), Texture Mode (Stretch/Tile/DistributePerSegment/RepeatPerSegment).
- **VFX Graph — overview + Contexts** — Unity Docs `com.unity.visualeffectgraph@17.0` (`index.html`, `Contexts.html`) — node-based; contexts Event/Spawn/Initialize/Update/Particle Output/Static Mesh Output; el detalle GPU/millones y compute-shaders/URP-HDRP ya sintetizado en [ver: pipeline/feel-en-unity §6].

**Convención de práctica (nivel concepto, ampliamente documentado — no doc única):**
- Técnicas de dissolve/outline/hit-flash por Shader Graph — patrón canónico de tutoriales de VFX 2D (Brackeys, Unity Learn, Daniel Ilett/Cyanilux a nivel concepto); aquí reconstruidas SOLO con nodos verificados en la doc oficial.

*Gaps / a verificar en la próxima pasada: (1) la página de doc del **target 2D Shader Graph** (`urp/2d/2DShaderGraph.html`) devolvió 404 en @17.0/@14.0/6000.0 esta sesión — los nombres de Material "Sprite Lit / Sprite Unlit / Sprite Custom Lit" y el bloque "Sprite Mask" del target Lit son conocimiento Unity establecido + cross-ref a rendering-urp (Sprite-Lit-Default, 2D Renderer Data), no re-verificados contra la página viva; confirmar el listado exacto de bloques del target Sprite Lit en el editor; (2) **Smoothstep Node** existe pero su página no se fetcheó esta pasada — el borde suave del dissolve se puede hacer con dos Steps (verificado); (3) auto-bind `_MainTex` del Sprite Renderer al graph: comportamiento estándar, confirmar en la versión exacta; (4) nombres exactos de las variantes de **Output Particle** en VFX Graph (Quad/Sprite/Unlit/Lit) no enumerados en la doc de índice — verificar en el editor; (5) WebSearch agotado esta sesión (presupuesto compartido) — todo se verificó por WebFetch directo a doc oficial.*
