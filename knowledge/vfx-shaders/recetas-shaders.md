# Recetas de shaders (Shader Graph / URP, Unity 6)

> **Cuando cargar este archivo:** al construir un shader concreto en Unity 6 / URP para dar juice a un juego — disolver al morir, flash de daño, borde brillante, holograma, escudo, agua, texturas que fluyen, follaje que se mece, bandera, gelatina, o cel-shading. Trae las cadenas de nodos exactas y el parámetro que controla cada efecto, más cómo dispararlo desde código. El PORQUÉ del feel (por qué el flash vende el golpe) está en [ver: gamedev/game-feel]; la implementación base del feel (screenshake, hit-stop, tweening) en [ver: pipeline/feel-en-unity] — aquí va el shader/VFX puro. Para partículas GPU/CPU: [ver: particulas-vfx-graph], [ver: vfx-recetas]. Fundamentos de nodos: [ver: shader-graph-fundamentos]. Rendimiento: [ver: optimizacion-vfx].

Versión de referencia: **Shader Graph 17.x + URP 17.x = Unity 6 (6000.x)**. Los nombres de nodo, módulos y settings son de esa versión; datos dependientes de versión van marcados. Cualquier valor numérico es punto de partida — se calibra jugando [ver: gamedev/game-feel].

---

## 1. Anatomía mínima que hay que fijar antes de cualquier receta

| Concepto | Qué es | Dónde se toca |
|---|---|---|
| **Master Stack** | Los dos contextos de salida del graph: **Vertex** (Position, Normal, Tangent) y **Fragment** (Base Color, Emission, Metallic, Smoothness, Normal (TS), Alpha, Alpha Clip Threshold) | El graph raíz |
| **Graph Settings** | Material (Lit/Unlit/Sprite), **Surface Type** (Opaque/Transparent), **Alpha Clipping** (on/off), Render Face (Front/Back/Both) | Panel Graph Settings |
| **Blackboard / Properties** | Propiedades expuestas. Cada una tiene un **Reference** (ej. `_Amount`) — ESE string es el que usa el código, no el nombre visible | Blackboard |
| **Emission (HDR)** | El canal que "brilla". Solo se ve el glow real si hay **Bloom** en el volume de post-proceso; sin Bloom, Emission solo suma color | Fragment: Emission |
| **Alpha Clip Threshold** | Descartar píxeles cuyo Alpha < threshold. Requiere **Alpha Clipping = on** en Graph Settings | Fragment: Alpha Clip Threshold |

Nodos que se repiten en casi toda receta (nombres EXACTOS, verificados contra la doc):

| Nodo | Puertos clave | Qué hace | Fórmula |
|---|---|---|---|
| **Step** | Edge, In → Out | Umbral duro (máscara binaria) | `In >= Edge ? 1 : 0` |
| **Smoothstep** | Edge1, Edge2, In → Out | Umbral suave (Hermite) | `smoothstep(Edge1,Edge2,In)` |
| **Lerp** | A, B, T → Out | Mezcla lineal | `A + T*(B-A)` |
| **Simple Noise** | UV, **Scale (default 500)** → Out [0..1] | Value noise pseudo-aleatorio | — |
| **Gradient Noise** | UV, Scale → Out [0..1] | Perlin/gradient noise (más suave) | — |
| **Voronoi** | UV, Angle Offset, Cell Density → Out, Cells | Worley/celdas (hexágonos, escudos) | — |
| **Tiling And Offset** | UV, Tiling, Offset → Out | Escala/desplaza UVs (scroll) | `UV*Tiling + Offset` |
| **Time** | → Time, Sine Time, Cosine Time, Delta Time, Smooth Delta | Reloj del shader | Sine/Cosine Time ∈ [-1,1] |
| **Fraction** | In → Out | Parte decimal (sierra repetida) | `In - floor(In)` |
| **Fresnel Effect** | Normal, View Dir, **Power** → Out [0..1] | Borde según ángulo de vista | `pow(1 - saturate(dot(N,V)), Power)` |
| **Position** | Space: Object/View/World/Tangent/Absolute World → Out(V3) | Posición de vértice o fragmento | — |
| **Scene Depth** | UV, modo Linear01/Raw/**Eye** → Out | Profundidad del depth buffer | Devuelve 0.5 si Depth Texture off |
| **Scene Color** | UV → Out(V3) | Copia del color buffer (`_CameraOpaqueTexture`) | Requiere Surface = Transparent |

---

## 2. Cómo se dispara desde código (la mitad de la magia)

El shader define el efecto; **el código anima el parámetro**. Patrón general:

```csharp
// 1. Material único de esta instancia (NO el sharedMaterial: eso afecta a todos)
Renderer r = GetComponent<Renderer>();
Material mat = r.material;              // clona en el primer acceso

// 2. Cachear el ID una vez (más rápido que pasar string cada frame)
static readonly int Amount = Shader.PropertyToID("_Amount");

// 3. Animar el parámetro
mat.SetFloat(Amount, t);               // t = progreso 0..1
mat.SetColor(FlashColor, Color.white);
```

Reglas:
- **`SetFloat`/`SetColor`/`SetVector`** usan el **Reference** de la propiedad (`_Amount`), no el nombre visible.
- **`material`** clona el material (una copia por objeto → rompe el batching, pero permite valores por-instancia). Para MUCHAS instancias sin clonar: **`MaterialPropertyBlock`** + `renderer.SetPropertyBlock(mpb)` (mantiene el batching por GPU instancing).
- **Animar el valor con una curva**, no de golpe: dissolve al morir = lerpear `_Amount` 0→1 en ~0.4 s; hit flash = subir `_FlashAmount` a 1 y bajarlo en 2–4 frames con ease-out [ver: gamedev/game-feel §"Flashes"].
- Un tween corto (coroutine, `Mathf.Lerp`, o DOTween) sobre `SetFloat` ES el efecto. La curva de ese tween decide el feel [ver: pipeline/feel-en-unity].

---

## 3. DISSOLVE — desintegrar al morir/spawnear

**Idea:** ruido comparado contra un umbral animado; por debajo del umbral el píxel se descarta; en la frontera, un borde emisivo.

| Paso | Nodo(s) | Detalle |
|---|---|---|
| 1 | **Simple Noise** o **Gradient Noise** (UV, Scale) | El patrón de disolución. Scale ↑ = grano más fino |
| 2 | Property `_Amount` (Float, Slider 0–1) | El control. Es el `Edge` del threshold |
| 3 | **Step** (Edge = `_Amount`, In = noise) → Alpha | 0 donde noise < Amount → se descarta |
| 4 | Graph Settings: **Alpha Clipping = on**; conectar Step→Alpha, **Alpha Clip Threshold = 0.5** | Descarta el hueco |
| 5 (borde) | Segundo **Step** con Edge = `_Amount + _EdgeWidth` (default ~0.05); **Subtract** los dos Steps | La franja delgada del borde |
| 6 | **Multiply** franja × `_EdgeColor` (HDR) → **Emission** | El glow del borde (necesita Bloom para brillar) |

Control: **`_Amount`** 0 (sólido) → 1 (desaparecido). Desde código: `mat.SetFloat("_Amount", Mathf.Lerp(0,1,t))` al morir.
Variantes: dissolve **direccional** (de abajo a arriba) = sumar la **Y** de un **Position** (World/Object) al ruido antes del Step, remapeado con **Inverse Lerp**. Fuente de la receta: Cyanilux, "Dissolve Shader Breakdown".

---

## 4. HIT FLASH — el destello de daño

**Idea:** mezclar el color base hacia un color de flash (blanco puro casi siempre) con un solo parámetro. Es juice de primer nivel: vende que el golpe conectó [ver: gamedev/game-feel §"Flashes" — sprite a blanco 1–3 frames].

| Paso | Nodo(s) | Detalle |
|---|---|---|
| 1 | Sample Texture 2D / Base Color | El color normal del personaje |
| 2 | Property `_FlashColor` (Color HDR, default blanco), `_FlashAmount` (Float 0–1) | Los controles |
| 3 | **Lerp** (A = colorBase, B = `_FlashColor`, T = `_FlashAmount`) → **Base Color** | T=0 normal, T=1 todo flash |
| 4 (opcional) | Mandar el mismo Lerp también a **Emission** | Para que el flash "reviente" con Bloom |

Control: **`_FlashAmount`**. Desde código, al recibir daño:
```csharp
mat.SetFloat("_FlashAmount", 1f);
// esperar 2–4 frames y bajarlo con ease-out (coroutine/tween)
```
- Sprites 2D: mismo Lerp en un **Sprite Lit/Unlit** graph, o el archiconocido "flash material" con `_FlashColor`/`_FlashAmount` [ver: vfx-2d].
- Es el complemento visual del **hit-stop** y el **screenshake** — los tres disparan en el mismo frame del impacto [ver: pipeline/feel-en-unity].

---

## 5. FRESNEL / RIM LIGHT — borde brillante

**Idea:** el borde de la silueta (donde la normal es casi perpendicular a la vista) brilla. Base de holograma, escudo, rim de personaje.

| Paso | Nodo(s) | Detalle |
|---|---|---|
| 1 | **Fresnel Effect** (Power = `_RimPower`) | `pow(1 - dot(N,V), Power)`. Power ↑ = borde más fino |
| 2 | **Multiply** Fresnel × `_RimColor` (HDR) | Color e intensidad del rim |
| 3 | → **Emission** (Unlit o Lit) | El rim que brilla |

Control: **`_RimPower`** (grosor del borde) y **`_RimColor`** (color/intensidad). En cel-shading el rim se **multiplica por NdotL** para que solo aparezca en la zona iluminada (Roystan). Fórmula verificada contra la doc del nodo Fresnel Effect.

---

## 6. OUTLINE — contorno

Dos técnicas, distintas familias. URP Shader Graph es **single-pass** por graph, así que el inverted hull NO sale de un solo graph: se logra con material/submalla extra o Renderer Feature.

### 6a. Inverted hull (extruir la silueta)
| Paso | Cómo | Detalle |
|---|---|---|
| 1 | Segundo material/objeto que renderiza SOLO las backfaces (**Render Face = Back**, o Cull Front) | El casco invertido |
| 2 | En **Vertex/Position**: `Position(Object) + Normal * _OutlineWidth` | Empuja los vértices hacia afuera a lo largo de la normal |
| 3 | Color plano `_OutlineColor` (Unlit) | El contorno |
En URP se cablea con un **Renderer Feature "Render Objects"** (LayerMask del objeto, Override material outline, front-face culling) o duplicando la malla escalada. Barato, per-objeto, se rompe en cantos duros con normales no suavizadas.

### 6b. Post-process edge detection (pantalla completa)
| Paso | Cómo | Detalle |
|---|---|---|
| 1 | **Full Screen Pass Renderer Feature** + un **Fullscreen Shader Graph** | Corre en toda la pantalla |
| 2 | Muestrear **Scene Depth** y `_CameraNormalsTexture` (requiere DepthNormals prepass) en patrón X | 4 muestras alrededor del píxel |
| 3 | Diferencias con operador **Roberts cross** (²+², luego √) sobre depth y normales; **max** de ambos | Detecta cantos |
| 4 | Threshold + componer sobre la escena | Grosor uniforme en pantalla |
Detecta bordes internos y silueta; coste fijo por pantalla; requiere depth + normales. Fuente: Roystan, "Outline Shader".

Tradeoff: inverted hull = por objeto, barato, sin bordes internos; edge-detect = todo el frame, uniforme, necesita prepass de depth/normals.

---

## 7. HOLOGRAM — proyección holográfica

**Idea:** Fresnel (borde) + scanlines (líneas que barren) + flicker (parpadeo) + transparencia. Composición estándar de nodos verificados.

| Capa | Nodo(s) | Control |
|---|---|---|
| Rim | **Fresnel Effect** × `_HoloColor` (HDR) → Emission | `_RimPower` |
| Scanlines | **Position(Screen o Object).Y** → **Multiply** por `_LineDensity` → **Fraction** (sierra) → **Step**/Smoothstep para hacer la banda | `_LineDensity` = nº de líneas |
| Scroll de líneas | Sumar `Time.y * _ScrollSpeed` a la Y antes del Fraction | `_ScrollSpeed` — las líneas suben |
| Flicker | **Simple Noise** con UV = `Time` (o Sine Time) → multiplica el Alpha/Emission | `_FlickerSpeed` |
| Transparencia | Surface = **Transparent**; Alpha = rim + scanlines base | `_Alpha` |

Control global: **`_HoloColor`**, `_LineDensity`, `_ScrollSpeed`. Cada nodo (Fresnel, Position, Fraction, Time, Simple Noise, Step) está verificado; la combinación es la receta clásica de holograma.

---

## 8. FORCE FIELD / SHIELD — escudo con impacto

**Idea:** Fresnel para el domo translúcido + patrón hexagonal + un "ping" de impacto que se expande desde el punto de golpe.

| Capa | Nodo(s) | Control |
|---|---|---|
| Domo | **Fresnel Effect** (Power alto) × `_ShieldColor` (HDR) → Emission; Surface Transparent | `_ShieldColor`, `_RimPower` |
| Hexágonos | **Voronoi** (Cell Density) → tomar bordes de celda (One Minus del patrón + Step) | `_HexDensity` |
| Intersección | **Scene Depth (Eye)** − depth del fragmento (**Screen Position**) → **One Minus** → borde donde el escudo cruza geometría | brilla donde toca el suelo |
| Impacto | Property `_HitPos` (Vector3) + `_HitTime`: **Distance**(Position, `_HitPos`), comparar con un radio que crece con el tiempo → anillo | onda desde el golpe |

Control: pintar el domo con `_ShieldColor`; al recibir impacto, código pasa `mat.SetVector("_HitPos", punto)` y anima `_HitTime`. La intersección con geometría usa depth (§11) — **requiere Depth Texture on** (Voronoi y Scene Depth verificados contra la doc).

---

## 9. WATER — agua estilizada

**Idea:** normales que fluyen (olas) + color por profundidad + espuma en las orillas + refracción. Todo depende de **depth** y **opaque texture** (§11).

| Capa | Nodo(s) | Control |
|---|---|---|
| Ripples | 2× **Sample Texture 2D** de un normal map, UVs vía **Tiling And Offset** con Offset = `Time.y * _FlowSpeed` (dos direcciones distintas) → blend | `_FlowSpeed`, `_Tiling` |
| Color por profundidad | **Scene Depth (Eye)** − depth del fragmento → **Lerp** entre `_ShallowColor` y `_DeepColor` | `_DepthFade` |
| Espuma en orillas | Depth difference (igual que §11) → **Step**/Smoothstep con `_FoamAmount` → blanco en la intersección | `_FoamAmount` |
| Refracción | **Scene Color** con UV = Screen Position + distorsión (normal map) — Surface Transparent | `_Distortion` |
| Espuma que fluye | Sumar scroll a la textura de espuma (Tiling And Offset + Time) | — |

Control: `_FlowSpeed`, `_DeepColor`/`_ShallowColor`, `_FoamAmount`. **Requiere en el URP Asset: Depth Texture ON (color por profundidad y espuma) + Opaque Texture ON (refracción con Scene Color)**. Fuentes: Cyanilux "Depth", nodos Scene Depth/Scene Color/Tiling And Offset.

---

## 10. UV SCROLL / PANNING, WIND SWAY, VERTEX ANIMATION

### 10a. UV Scroll / Panning — cintas, lava, nubes, cascadas
| Paso | Nodo(s) |
|---|---|
| 1 | **Tiling And Offset**: Offset = **Time** × `_ScrollSpeed` (Vector2) |
| 2 | Ese UV → **Sample Texture 2D** |
Control: **`_ScrollSpeed`** (dirección/velocidad). Es `UV*Tiling + Offset` con Offset animado. Dos capas a distinta velocidad = parallax barato (nubes, lava). El nodo Tiling And Offset está pensado exactamente para "scrolling textures over Time" (doc).

### 10b. Wind / Foliage sway — vertex displacement por noise
En el **Vertex** context:
| Paso | Nodo(s) | Detalle |
|---|---|---|
| 1 | **Position(Object)** + **Simple/Gradient Noise** con UV = worldXZ + `Time × _WindSpeed` | Onda que viaja |
| 2 | **Multiply** por **UV.y** o por vertex color (rojo = "rigidez") | Solo la punta se mueve, la base queda anclada |
| 3 | Multiplicar por `_WindStrength` y sumar al **Position** → block **Position (Vertex)** | Desplaza el vértice |
Control: **`_WindStrength`**, `_WindSpeed`. La máscara (UV.y / vertex color) es lo que evita que el tronco se despegue del suelo.

### 10c. Vertex animation — bandera, gelatina
| Efecto | Cómo |
|---|---|
| **Bandera** | En Vertex: sumar a Position.Z una **Sine** de `(Position.x * _Freq + Time * _Speed)`, enmascarada por Position.x (0 en el mástil, 1 en la punta) |
| **Gelatina / wobble** | Sine de `Time` sobre Position, amplitud decae con la distancia al pivote; al impactar, código sube `_WobbleAmount` y decae con tween elástico [ver: gamedev/game-feel §squash&stretch] |
| **Squash&stretch por shader** | Escalar Position en Vertex (Y×0.7, XZ×1.3 al aplastar) conservando volumen — controlado por `_Squash` desde código |
Todo esto vive en el **Vertex/Position** block usando **Time**, **Sine**, **Position**. Es deformación de malla, no de píxel — barato y no rompe el shading si las normales no importan.

---

## 11. Depth y screen-space (concepto) — por qué agua/borde/escudo lo necesitan

[ver: unity/rendering-urp] para el detalle de pipeline; aquí lo justo para las recetas.

| Textura | Qué es | Se activa en | La usan |
|---|---|---|---|
| **Depth Texture** (`_CameraDepthTexture`) | Distancia de cada píxel a la cámara | URP Asset → **Depth Texture** (o por-cámara) | Scene Depth, soft particles, espuma, intersección de escudo |
| **Opaque Texture** (`_CameraOpaqueTexture`) | Copia del color ANTES de renderizar transparentes | URP Asset → **Opaque Texture** (+ Opaque Downsampling) | Scene Color → refracción, distorsión, cristal, calor |

Claves verificadas:
- **Scene Depth** devuelve **0.5** (no error) si Depth Texture está apagado → efecto plano y "sin explicación". Primer sospechoso si el agua no tiñe o el escudo no marca la intersección.
- **Scene Color** solo funciona en material **Transparent** (o render queue 2999–3000) porque muestrea el opaque texture; en Opaque no hay copia que leer.
- **Intersección/foam/soft edge** = `SceneDepth(Eye) − depthDelFragmento`; cerca de 0 → están tocando → **One Minus**/Smoothstep para el borde.
- **Opaque Downsampling = 4x Box** da una copia suavemente borrosa (útil para cristal esmerilado). [ver: optimizacion-vfx] para el coste.

---

## 12. TOON / RAMP shading (cel-shade)

**Idea:** cuantizar la luz en bandas planas + rim + specular escalonado + outline (§6). Estilizado clásico.

| Capa | Nodo(s) | Control |
|---|---|---|
| Bandas de luz | **Dot Product**(Normal, LightDir) = NdotL → **Sample Texture 2D** de un **ramp** (gradiente horizontal 1D), o **Smoothstep(0, 0.01, NdotL)** para corte duro | textura ramp = nº y color de bandas |
| Rim | **Fresnel Effect** × NdotL (solo en zona iluminada) | `_RimPower` |
| Specular | `pow(NdotH, glossiness)` → **Smoothstep** → highlight plano | `_Glossiness` |
| Outline | Inverted hull o edge-detect (§6) | `_OutlineWidth` |

- El **ramp** (textura de gradiente muestreada por NdotL) es más flexible que el Smoothstep: cambias la rampa y cambias el look sin tocar el graph.
- En URP la dirección de la luz principal se obtiene con el nodo **Get Main Light Direction** (Shader Graph 17.x, categoría Input, devuelve un Vector3 world-space) — es la vía oficial, sin HLSL a mano. Para color/atenuación/sombra de esa luz (no cubierto por ese nodo) se sigue recurriendo a un **Custom Function** que llama `GetMainLight()` de la lighting library de URP; esa sintaxis exacta NO se verificó línea por línea. [ver: unity/rendering-urp]
- Fuente de la receta: Roystan, "Toon Shader".

---

## Reglas prácticas

1. El **Reference** de la propiedad (`_Amount`) es lo que usa `SetFloat`, no el nombre visible — confírmalo en el Blackboard.
2. Animar el parámetro con **curva/tween** desde código; el shader es estático, el feel lo pone la curva [ver: pipeline/feel-en-unity].
3. **Un objeto que cambia por-instancia** → `renderer.material` (clona) o **MaterialPropertyBlock** (mantiene batching). Nunca `sharedMaterial` para un solo enemigo.
4. **Cachear `Shader.PropertyToID`** una vez; no pasar strings cada frame.
5. Emission solo brilla con **Bloom** en el volume; sin Bloom, súbelo a HDR pero no esperes glow.
6. Alpha Clip (dissolve) requiere **Alpha Clipping = on** en Graph Settings, no basta conectar Alpha.
7. **Depth Texture ON** para agua, espuma, escudo-intersección, soft particles; si Scene Depth da 0.5 constante, está apagado.
8. **Opaque Texture ON + Surface Transparent** para refracción/distorsión con Scene Color.
9. **Step = corte duro; Smoothstep = corte suave.** Bordes de dissolve/escudo casi siempre Smoothstep (antialias barato).
10. Scroll de texturas = **Tiling And Offset** con Offset = Time × velocidad — no muevas UVs a mano.
11. Vertex sway/bandera: enmascarar el desplazamiento (UV.y o vertex color) para anclar la base; nunca mover el vértice entero.
12. Inverted hull es **pass/objeto extra** en URP (Renderer Feature o malla duplicada), no sale de un graph single-pass.
13. Hit flash, dissolve, screenshake y hit-stop disparan **en el mismo frame** del impacto [ver: gamedev/game-feel].
14. Simple/Gradient Noise **Scale default = 500**: si el ruido se ve "liso", el Scale está mal calibrado, no roto.
15. Fresnel Power alto = borde fino; Power bajo = casi todo el objeto brilla. Empezar en ~2–5.
16. Todo valor numérico aquí es **punto de partida**: calibrar con el juego corriendo, no en el editor pausado.
17. Toon: preferir **ramp texture** sobre Smoothstep hard-coded — cambiar el look sin recompilar el graph.
18. Simplificar antes de shippear: nodos redundantes cuestan; medir con Frame Debugger [ver: optimizacion-vfx].
19. Para NdotL en toon shading, usar el nodo **Get Main Light Direction** (oficial, sin HLSL) en vez de un Custom Function a mano si solo hace falta la dirección.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| `SetFloat("Amount", ...)` no hace nada | El Reference es `_Amount` con guión bajo; verificar en Blackboard, no usar el display name |
| El flash/dissolve afecta a TODOS los enemigos a la vez | Estás tocando `sharedMaterial`; usar `.material` o MaterialPropertyBlock por instancia |
| Emission subida pero nada brilla | Falta **Bloom** en el Volume de post-proceso; Emission sin Bloom solo suma color |
| Dissolve no descarta píxeles | **Alpha Clipping** apagado en Graph Settings, o Alpha Clip Threshold mal (poner 0.5) |
| Agua plana, no tiñe por profundidad; espuma no aparece | **Depth Texture** apagado en el URP Asset → Scene Depth devuelve 0.5 |
| Scene Color sale negro/vacío | Material en **Opaque**; Scene Color exige Surface **Transparent** (queue 2999–3000) y Opaque Texture ON |
| Outline "inverted hull" no aparece desde un solo graph | URP es single-pass; hace falta Renderer Feature "Render Objects" (Cull Front) o malla duplicada |
| Borde de dissolve/escudo con aliasing feo | Cambiar el **Step** del borde por **Smoothstep** |
| El follaje se despega del suelo al mecerse | Falta la máscara (UV.y / vertex color) que ancla la base del desplazamiento |
| Scanlines del holograma no se mueven | El **Offset/scroll** debe usar **Time**, no un valor fijo; sumar `Time.y * speed` |
| Ruido de dissolve se ve como gradiente liso | **Scale** del Simple/Gradient Noise demasiado bajo (o alto); default 500, ajustar |
| Vertex animation rompe la iluminación | Recalcular normales tras desplazar, o usar Unlit si el shading no importa |
| Refracción/agua mata el rendimiento en móvil | Opaque Downsampling a 2x/4x y limitar el uso de Scene Color [ver: optimizacion-vfx] |
| Flash instantáneo se ve como parpadeo brusco | Bajar `_FlashAmount` con **ease-out** en 2–4 frames, no de golpe [ver: gamedev/game-feel] |

## Fuentes

- **Unity Shader Graph 17.x — Node Library** (docs.unity3d.com, `com.unity.shadergraph@17.0`): páginas verificadas una por una — Fresnel Effect (`Out = pow(1 - saturate(dot(N,V)), Power)`), Simple Noise (Scale default 500), Gradient Noise, Voronoi, Step, Smoothstep, Lerp, Tiling And Offset (`UV*Tiling+Offset`), Time (Time/Sine/Cosine/Delta/Smooth Delta), Fraction (`In-floor(In)`), Position (Object/View/World/Tangent/Absolute World), Scene Depth (Linear01/Raw/Eye; 0.5 si depth off), Scene Color (opaque texture, requiere Transparent).
- **Unity Manual — Particle System modules** (docs.unity3d.com): nombres exactos de módulos (Emission, Shape, Velocity/Color/Size over Lifetime, Noise, Collision, Sub Emitters, Texture Sheet Animation, Trails, Renderer, etc.) — [ver: particulas-vfx-graph].
- **Unity VFX Graph 17.x — Contexts** (docs.unity3d.com, `com.unity.visualeffectgraph@17.0`): contextos Event, Spawn, GPU Event, Initialize, Update, Output — [ver: particulas-vfx-graph].
- **Unity URP 17.x — Universal Render Pipeline Asset** (docs.unity3d.com, `com.unity.render-pipelines.universal`): Depth Texture (`_CameraDepthTexture`), Opaque Texture (`_CameraOpaqueTexture`, "snapshot before transparents", casos frosted glass/water refraction/heat waves), Opaque Downsampling (None/2x Bilinear/4x Box/4x Bilinear).
- **Cyanilux — "Dissolve Shader Breakdown"** (cyanilux.com): receta dissolve con noise + doble Step (Amount y Amount+EdgeWidth 0.05) + edge color, Alpha Clip Threshold 0.5.
- **Cyanilux — "Depth" tutorial** (cyanilux.com): intersección/foam vía `SceneDepth(Eye) − fragmentDepth` + One Minus + Saturate; requisito Depth Texture en el URP Asset.
- **Roystan — "Outline Shader"** (roystan.net): edge detection post-proceso con depth + normales, muestreo en X, operador Roberts cross, max de ambos.
- **Roystan — "Toon Shader"** (roystan.net): bandas por NdotL (ramp o Smoothstep(0,0.01,NdotL)), rim = `1 - dot(V,N)` × NdotL, specular con `pow(NdotH, gloss)` + Smoothstep.
- **Unity Shader Graph 17.x — Get Main Light Direction Node** (docs.unity3d.com, `com.unity.shadergraph@17.0`): nodo oficial que devuelve la dirección world-space de la luz principal (Vector3) sin Custom Function — verificado en esta auditoría (2026-07-20).
- **Unity URP 17.x — Universal Render Pipeline Asset**: Opaque Downsampling verificado con sus 4 opciones exactas (None, 2x Bilinear, 4x Box, 4x Bilinear); Depth Texture → `_CameraDepthTexture`, Opaque Texture → `_CameraOpaqueTexture` — verificado en esta auditoría (2026-07-20).
- **Unity URP 17.x — Full Screen Pass Renderer Feature** y **Render Objects Renderer Feature** (docs.unity3d.com, redirige a `docs.unity3d.com/6000.0/.../urp/renderer-features/`): nombres exactos y propósito (full-screen effects / renderizar un subconjunto de objetos con Layer Mask y Material override) verificados en esta auditoría (2026-07-20).
</content>
</invoke>
