# Recetas de VFX (Unity 6 / URP)

> **Cuando cargar este archivo:** al construir efectos concretos que dan juice — explosiones, impactos, muzzle flash, estelas, hechizos, humo, curación, pickups — con Particle System, VFX Graph, Trail/Line Renderer o shaders en Unity 6 / URP. El PORQUÉ del feel (por qué el flash vende el golpe, hit-stop, shake) está en [ver: gamedev/game-feel]; el timing respecto a la animación en [ver: gamedev/animacion]; la implementación base del feel en el motor en [ver: pipeline/feel-en-unity]. Aquí va el VFX/shader concreto: qué módulo, qué nodo, qué parámetro.

Versión de referencia: **Unity 6 (6000.0), URP 17.x** — Shader Graph 17, VFX Graph 17, Particle System (built-in), 2D Renderer. Datos dependientes de versión marcados. Nombres de módulos/nodos verificados contra docs de Unity (ver Fuentes); lo no verificado va marcado "⚠️confirmar".

---

## 1. Las cuatro herramientas de VFX: cuándo cada una

| Herramienta | Qué es | Úsala para | Coste/plataforma |
|---|---|---|---|
| **Sprite / flipbook** (Texture Sheet Animation, o Animator sobre sprite) | Secuencia de dibujos pre-renderizados en un grid | Explosión, muzzle flash, chispazo, humo pre-horneado, VFX 2D estilizado. Un solo quad. | Barato en runtime, caro en autoría/memoria (sheet grande). Mejor para efectos únicos que "no doblan" |
| **Particle System (built-in / Shuriken)** | Simulación de partículas en **CPU**, modular | El default para el 90% del juice 3D/2D: humo, chispas, polvo, fuego, magia. Colisión con física, sub-emitters, trails integrados | CPU-bound: miles de partículas OK, cientos de miles no. Colisión CPU precisa |
| **VFX Graph** | Simulación en **GPU** vía node graph (contextos/bloques) | Millones de partículas, efectos masivos (tormentas, nubes densas, fluidos), lectura de mapas/atributos. Requiere SRP (URP/HDRP) | GPU-bound: escala a millones. Colisión sólo aproximada (depth buffer / SDF), no física real |
| **Shader (Shader Graph)** | Material procedural sobre una malla/quad | Dissolve, glow/rim, escudos de energía, ondas de choque como quad, distorsión de calor, líquidos. El efecto ES el material, no partículas | Barato por draw call; el coste es fragmentos en pantalla (fillrate) |

**Regla de decisión:**
- ¿El efecto es un dibujo que se reproduce igual siempre? → **flipbook** (sprite sheet).
- ¿Necesitas comportamiento (dispersión, colisión, gravedad, variación)? → **Particle System**.
- ¿Cientos de miles / millones de partículas o lees texturas por partícula? → **VFX Graph**.
- ¿El efecto es una superficie continua (onda, escudo, disolución, brillo)? → **shader**.
- La mayoría de efectos "completos" **combinan** varias: partículas con material de shader + una luz + post-proceso Bloom (sección 9).
- **Móvil: cuidado con VFX Graph.** Requiere **compute shaders obligatorios** + soporte de SSBO, **no soporta OpenGL ES**, y en URP para móvil está **en preview y solo con partículas unlit** (incompatible con gamma color space) — verificado en la doc de requisitos de VFX Graph. Para móvil, **Particle System (Shuriken) es la opción segura por defecto**; VFX Graph en móvil solo si confirmaste el hardware target (GPUs modernas, Metal/Vulkan) y aceptas que es preview.

Detalle de módulos de partículas → [ver: particulas-vfx-graph]. Fundamentos de nodos → [ver: shader-graph-fundamentos]. Recetas de shader puro → [ver: recetas-shaders]. VFX 2D → [ver: vfx-2d]. Presupuesto/rendimiento → [ver: optimizacion-vfx].

---

## 2. Anatomía del frame de impacto (el "juice stack")

Un golpe que se siente NO es una cosa: son **5–6 capas disparadas en el MISMO frame de contacto**. El VFX es solo una de ellas — el porqué de que todas juntas vendan el golpe está en [ver: gamedev/game-feel]. Aquí, qué dispara cada capa y con qué:

| Capa | Herramienta | Disparo |
|---|---|---|
| **Flash** (sprite a blanco / flash de material) | Shader: propiedad `_FlashAmount` que hace lerp del albedo a blanco, o material emisivo pulsado 1–3 frames | En el frame de hit, vía anim event o al aplicar daño |
| **Partículas de impacto** (chispas + puff) | Particle System con **Burst** (Emission → Bursts) en `Play()` | Instanciar/`Play()` en el punto de contacto, orientadas por la normal del hit |
| **Hit-stop** (freeze de 2–15 frames) | `Time.timeScale` o freeze local | En el frame de contacto — NO congelar las propias partículas del impacto [ver: gamedev/game-feel §3] |
| **Screen shake** | Sistema de trauma (Cinemachine Impulse o propio) | `trauma += k`; shake = trauma² [ver: gamedev/game-feel §4] |
| **Sonido** | SFX one-shot con pitch ±5–15% | Mismo frame que el evento (latencia mínima) [ver: gamedev/game-feel §7] |
| **Número flotante / knockback** | UI pooled + impulso físico | En el punto de impacto |

La receta VFX (flash + partículas) es lo que ESTE archivo cubre; las otras capas están en game-feel. La clave: **todas en el frame de contacto, no escalonadas**. Un flash 4 frames tarde se lee como bug, no como impacto.

---

## 3. El timing del VFX: anticipación → hit → fade

Todo VFX de acción tiene la misma estructura de 3 tiempos que un ataque (wind-up / active / recovery, [ver: gamedev/animacion §2]). Sincronizarlo con la animación se hace con **anim events anclados al clip**, no con timers paralelos — así el VFX sobrevive a cambios de timing de la animación [ver: gamedev/animacion §7].

| Tiempo del VFX | Qué es | Cómo se implementa |
|---|---|---|
| **Anticipación / carga** | Partículas que se ACUMULAN hacia el punto (energía cargándose), glow que sube | Emisión continua + Velocity/Force over Lifetime apuntando al centro; emisión desde una esfera que encoge. Telegrafía el ataque [ver: gamedev/animacion §2] |
| **El hit / release** | El burst instantáneo en el frame activo | Emission → **Bursts** (Count alto, 1 cycle) disparado por anim event en el frame active |
| **Fade / disipación** | La cola: humo que sube y desvanece, chispas que caen y mueren | Color over Lifetime (alpha→0) + Size over Lifetime + Force/gravedad. Los restos con permanencia valen más [ver: gamedev/game-feel §2] |

- **Duración**: el burst y el flash son cortos (1–5 frames); el fade puede durar 0.5–3 s. Feedback de golpe frecuente ≤ 300 ms en su parte "activa" [ver: gamedev/game-feel §5].
- **Anim events**: marca en el clip de ataque el frame exacto donde nace el VFX (`SpawnHitVFX`), el frame del flash, el frame del sonido. En el Particle System usa `Stop`/`Play` o `Emit(n)` desde ese evento.
- El VFX de anticipación del ENEMIGO es telegraphing y debe ser largo y legible; el del JUGADOR, mínimo (el jugador ya "pagó" su anticipación en el trigger) [ver: gamedev/animacion §2].

---

## 4. Particle System — los módulos que importan

Módulos (nombres exactos, doc de Unity). Se activan con el checkbox de su cabecera; casi todos aceptan **curvas** y **rangos aleatorios** (Random Between Two Constants/Curves) — ahí vive la variación orgánica.

| Módulo | Controla | Propiedades clave |
|---|---|---|
| **Main** | Estado inicial de cada partícula | Start Lifetime, Start Speed, Start Size, Start Color, Gravity Modifier, Simulation Space (Local/World), Max Particles |
| **Emission** | Ritmo y timing de emisión | **Rate over Time**, **Rate over Distance**, **Bursts** (Time, Count, Cycles, Interval, Probability) |
| **Shape** | Volumen/superficie de emisión + dirección inicial | Shape: Cone, Sphere, Hemisphere, Box, Circle, Edge, Mesh… + Radius, Angle |
| **Velocity over Lifetime** | Velocidad a lo largo de la vida | Linear XYZ, Orbital, Radial, Speed Modifier |
| **Limit Velocity over Lifetime** | Frena partículas (drag) | Speed, Dampen, Drag |
| **Inherit Velocity** | Hereda velocidad del emisor en movimiento | Mode (Current/Initial), Multiplier |
| **Force over Lifetime** | Fuerza continua (viento, empuje) | Force XYZ (constante/curva) |
| **Color over Lifetime** | Color y **alpha** en el tiempo (el fade) | Gradient (RGBA sobre la vida) |
| **Color by Speed** | Color según velocidad | Gradient + rango de speed |
| **Size over Lifetime** / **Size by Speed** | Crecer/encoger | Curva de size |
| **Rotation over Lifetime** / **Rotation by Speed** | Girar | Angular velocity |
| **Noise** | Turbulencia orgánica del movimiento | Strength, Frequency, Scroll Speed, Octaves |
| **Collision** | Colisión con el mundo (CPU) | World/Planes, Dampen, Bounce, Lifetime Loss |
| **Sub Emitters** | Spawnea otro sistema en un evento | Birth / **Collision** / **Death** / Trigger / Manual (sección 7: explosión, impacto) |
| **Texture Sheet Animation** | Flipbook sobre la partícula | Mode (Grid/Sprites), Tiles X/Y, Animation (Whole Sheet/Single Row), Frame over Time, Start Frame, Cycles |
| **Lights** | Luz real por partícula (caro) | Light prefab, Ratio, Range/Intensity multipliers |
| **Trails** | Estela por partícula | Mode (Particles/Ribbon), Ratio, Lifetime, Width over Trail |
| **Renderer** | Cómo se dibuja | Render Mode (Billboard, Stretched Billboard, Horizontal/Vertical Billboard, Mesh), Material, Trail Material, Sort Mode (None/By Distance/Oldest in Front/Youngest in Front/By Depth), Sorting Fudge |

**Capas típicas de un efecto = varios sistemas hijos**, cada uno un rol: uno para el core (flash/flash-quad), uno para chispas (Stretched Billboard), uno para humo (billboard grande, Color over Lifetime a alpha 0), uno para la onda. Se agrupan bajo un GameObject padre y se disparan juntos.

---

## 5. VFX Graph — contextos y bloques (GPU)

Cuando el Particle System se queda corto en cantidad. Simulación en **GPU**; arquitectura de **4 contextos** en orden de flujo (verificado, doc de Unity):

| Contexto | Qué hace |
|---|---|
| **Spawn** | Decide cuántas partículas y cuándo (rate, bursts, loops con delay). Emite `SpawnEvent` |
| **Initialize** | Corre UNA vez por partícula nueva: posición inicial, velocidad, lifetime, color, tamaño (el editor suele mostrarlo como "Initialize Particle" para sistemas de partículas, pero el nombre de contexto documentado es **Initialize**) |
| **Update** | Corre CADA frame sobre todas las vivas: fuerzas, colisión, turbulencia, envejecimiento |
| **Particle Output** | Renderiza (quad, mesh, strip…) leyendo los atributos calculados |

- Dentro de cada contexto se apilan **Blocks** (equivalentes a los módulos del Particle System). **Operators** son nodos de cálculo que alimentan puertos; **Properties** son parámetros expuestos (editables desde inspector/script/Timeline).
- Patrón de nombres de bloques: `Set <Atributo>`, `Add <Atributo>`, `Multiply <Atributo>` (ej. Set Velocity, Add Position, Set Lifetime), más bloques de fuerza/colisión (Gravity, Turbulence, Collide with Depth Buffer/SDF). ⚠️Confirmar el nombre EXACTO de cada bloque en el Node Library de VFX Graph de tu versión antes de escribir — no todos los bloques del Particle System tienen equivalente idéntico.
- **VFX Graph no hace física de colisión real**: colisiona contra el depth buffer o Signed Distance Fields, aproximado. Si necesitas colisión precisa por partícula (casquillos que ruedan, debris físico), usa Particle System.
- Requiere render pipeline (URP/HDRP); no funciona con el built-in pipeline. Detalle → [ver: particulas-vfx-graph].

---

## 6. Trail Renderer y Line Renderer — estelas y rayos

Dos componentes para líneas/estelas SIN partículas. Nombres de propiedad verificados (doc de Unity).

**Trail Renderer** — estela que sigue al transform (proyectil, espada, dash):

| Propiedad | Controla |
|---|---|
| **Time** | Segundos que vive cada punto de la estela = largo de la cola |
| **Min Vertex Distance** | Distancia mínima entre puntos (menor = más suave, más vértices) |
| **Width** | Ancho + **curva** a lo largo de la estela (afinar hacia el final = look de "cometa") |
| **Color** | **Gradient** a lo largo del largo (color→transparente al final) |
| **Emitting** | Activa/pausa la generación de puntos (apagar entre swings) |
| **AutoDestruct** | Destruye el GameObject tras Time sin moverse |
| **Alignment** | View (mira a cámara) / TransformZ (sigue el eje Z del transform) |
| **Texture Mode** | Stretch / Tile / DistributePerSegment / RepeatPerSegment |
| **Materials** / **Min Vertex Distance** / **Corner Vertices** / **End Cap Vertices** | Material (aditivo para brillo), redondeo de esquinas y punta |

**Line Renderer** — línea explícita entre puntos (rayo láser, cadena de electricidad, mira, cuerda):

| Propiedad | Controla |
|---|---|
| **Positions** | Array de puntos Vector3 a conectar (los mueves por script para un rayo que zigzaguea) |
| **Width** | Ancho + curva por vértice |
| **Color** | **Gradient** a lo largo |
| **Use World Space** | Puntos en coords de mundo (rayo entre dos objetos) vs locales |
| **Loop** | Conecta primer y último punto (círculos, AoE) |
| **Alignment** / **Texture Mode** / **Corner/End Cap Vertices** | Igual que Trail Renderer |

**Elegir**: la estela que un objeto en movimiento deja atrás → **Trail Renderer** (automático). Una línea que TÚ defines punto a punto (rayo, láser, cadena, telegraph de trayectoria) → **Line Renderer**. Estela con partículas (que se dispersan al desprenderse) → módulo **Trails** del Particle System. Rayo eléctrico animado → Line Renderer con Positions perturbadas por noise cada frame + material aditivo + Bloom.

---

## 7. Recetario (capas + timing de cada una)

Timings en ms/frames = **punto de partida** de craft (no cifras de doc); calíbralos jugando [ver: gamedev/game-feel]. Frames @60fps salvo nota.

### EXPLOSIÓN (el efecto multicapa canónico)
Orden de capas, del centro hacia afuera y del frame 0 hacia el fade:

| # | Capa | Herramienta / módulo | Timing |
|---|---|---|---|
| 1 | **Flash** blanco/amarillo | Quad aditivo grande o `Lights` module (1 luz brillante) | frame 0, dura 1–2 frames, escala rápido y muere |
| 2 | **Core** (bola de fuego) | Particle System, Burst pequeño (3–8), Texture Sheet Animation de fuego, Size over Lifetime creciente | 0–200 ms |
| 3 | **Humo** | Sistema aparte, billboard grande, Color over Lifetime → alpha 0, Force over Lifetime hacia arriba, Noise | 100 ms → 1.5–3 s (el que más dura) |
| 4 | **Chispas** | Sistema, Render Mode **Stretched Billboard**, Burst (20–50), gravedad, Collision con bounce | 0–600 ms |
| 5 | **Onda de choque** | Shader en quad: anillo que escala (Time → radio) con soft edge, o distorsión de calor (refracción) | frame 0 → 300 ms |
| 6 | **Escombros / debris** | Sistema con Render Mode **Mesh**, Collision (permanencia: quedan en el suelo) | 0 → varios s |

Todo se dispara junto en frame 0; lo escalonado es cuánto DURA cada capa, no cuándo empieza. Añadir Bloom (sección 9) al flash/core/chispas para el glow. Sub Emitter con condición **Death** sirve para spawnear el humo/chispas al morir la bola de fuego.

### IMPACTO / HIT (bala en pared, golpe conectando)
1. **Flash direccional** en el punto de contacto (quad aditivo pequeño, 1–2 frames).
2. **Chispa direccional**: Particle System, Burst (5–15), **Shape = Cone** orientado por la **normal del hit** (reflejar la dirección de la bala), Render Mode Stretched Billboard, gravedad ligera. Rota el emisor con `Quaternion.LookRotation(hit.normal)`.
3. **Puff de polvo/material**: partículas del color de la superficie (piedra gris, madera marrón) — VFX distinto por material vende el mundo físico [ver: gamedev/game-feel §2].
4. **Decal** de permanencia (agujero de bala) si aplica.
5. Capa de impacto en el enemigo: flash de material a blanco 1–3 frames + hit-stop + shake [ver: gamedev/game-feel]. Sub Emitter con condición **Collision** genera el chispazo cuando la partícula-bala golpea.

### MUZZLE FLASH (destello de disparo, 1–2 frames)
- **Un solo quad** con material aditivo + sprite de flash, mostrado **1–2 frames** y ocultado (o Texture Sheet Animation de 1 ciclo muy rápido). "1–2 frames de flash en la boca del arma venden el disparo más que la bala" [ver: gamedev/game-feel §2].
- Añade una **Light** (point) de 1–2 frames para que ilumine el entorno (parpadeo).
- Opcional: humo tenue tras el disparo + casquillo (Stretched Billboard con física y permanencia).
- No lo hagas persistente ni animado largo — la brevedad ES el efecto.

### TRAIL (estela de proyectil o espada)
- **Proyectil (flecha, bala, misil)**: **Trail Renderer** hijo del proyectil, Time corto (0.1–0.3 s), Width con curva que afina hacia atrás, Color gradient a transparente, material aditivo. Para misil: sumar humo con Particle System (módulo Trails o sistema con Rate over Distance).
- **Espada / arma cuerpo a cuerpo (weapon trail)**: **Trail Renderer** en la punta del arma, con **Emitting** activado SOLO durante los frames active del swing (anim event on/off), Time muy corto (0.1–0.2 s) para que la estela sea un arco limpio y no una mancha. Marca la zona de peligro del ataque [ver: gamedev/animacion §2]. Alternativa de más control: mesh de trail generado por script sobre el arco del swing.
- **Rate over Distance** (Emission) es clave para trails de partículas: emite por distancia recorrida, así la densidad es constante sin importar la velocidad.

### MAGIA / HECHIZO (carga → release → impacto)
Estructura de 3 fases sincronizada con la animación de casteo [ver: gamedev/animacion §2]:
1. **Carga (wind-up)**: partículas que CONVERGEN hacia la mano/bastón — emitir desde una esfera (Shape = Sphere) con **Velocity/Force over Lifetime radial NEGATIVO** (hacia el centro), glow subiendo (Color/emisión creciente). Telegrafía potencia.
2. **Release**: **Burst** en el frame de soltar + proyectil (con Trail Renderer) o rayo (Line Renderer con noise). Flash en la mano.
3. **Impacto**: receta de IMPACTO arriba + efecto elemental (AoE de shader en el suelo, partículas ascendentes). 
- El look de energía se hace con **shader** (Fresnel para glow de borde, Gradient Noise/Voronoi scrolleado para plasma) + partículas + Bloom (sección 8/9), no solo partículas.

### HUMO / POLVO (pasos, aterrizaje, derrape)
- **Paso/footstep**: Burst pequeño (2–5) de polvo, Shape plano, Size over Lifetime creciente, Color over Lifetime → alpha 0, vida corta (0.4–0.8 s), disparado por **anim event** en el frame de contacto del pie.
- **Aterrizaje**: Burst mayor + anillo de polvo que se expande (Shape = Circle con Velocity radial), escala con la altura de la caída (más juice a más impacto).
- **Humo continuo (chimenea, fuego)**: Rate over Time bajo, Force over Lifetime hacia arriba, Noise para deriva orgánica, billboard grande, Color over Lifetime a transparente. Simulation Space = World para que no siga al emisor.
- Textura de humo suave + **soft particles** (sección 8) para que no corte feo contra el suelo.

### CURACIÓN / BUFF (partículas ascendentes + glow)
- Partículas que SUBEN: Shape = Circle/Cylinder alrededor del personaje, **Velocity over Lifetime +Y**, Color verde/dorado, forma de sprite (cruz, chispa, hoja).
- **Glow envolvente**: shader con **Fresnel Effect** (Power alto) emisivo sobre el personaje o un mesh cápsula, animado con Time (pulso), + Bloom.
- Anillo en el suelo: shader de textura scrolleada/rotada (Twirl / Polar Coordinates) sobre un quad horizontal.
- Ascenso + brillo cálido + pulso = lectura clara de "algo bueno". Contrario a impacto (rápido, agresivo): la curación es suave y sostenida.

### PICKUP / COLECCIÓN (moneda, ítem, power-up)
- **Idle atractivo**: rotación constante (Rotation over Lifetime o transform), bob senoidal, glow (Fresnel + Bloom), destello ocasional (sparkle sprite flipbook).
- **Al recoger**: Burst radial corto (chispas hacia afuera) + flash + partículas que **convergen hacia el HUD** (feedback de "fue a tu inventario") + SFX ascendente. Escala rápida con overshoot (ease Back) antes de desaparecer [ver: gamedev/game-feel §5].
- Coleccionables baratísimos de juicear y de altísimo impacto percibido — invertir aquí rinde.

---

## 8. VFX dirigido por shader (Shader Graph)

Efectos que son un **material**, no partículas. Nodos verificados marcados ✓; nodos estándar de uso común sin verificación puntual marcados (std). Fundamentos → [ver: shader-graph-fundamentos], recetas completas → [ver: recetas-shaders].

| Efecto | Nodos clave | Cómo |
|---|---|---|
| **Dissolve** (desintegración, teletransporte) | **Gradient Noise** ✓ (o **Voronoi** ✓) → **Step** (std) → **Alpha Clip Threshold**; borde brillante con un 2º Step a `threshold+width` → emission | Una propiedad `_Dissolve` (0→1) animada barre el clip; el anillo entre los dos steps es el borde incandescente |
| **Glow / rim** (escudo, buff, resaltado) | **Fresnel Effect** ✓ (Normal, View Dir, **Power**) → multiplicar por color HDR → Emission | Power alto = borde fino; Power bajo = glow ancho. Emission > 1 → Bloom (sección 9) |
| **Onda de choque / anillo** | **Time** (std) → radio; **Step**/**Smoothstep** (std) para el anillo; sobre quad | Anillo que escala desde el centro; sumar distorsión de pantalla para refracción |
| **Scroll de energía / plasma / humo** | **Time** (std) → **Tiling And Offset** (std) → **Sample Texture 2D** o **Gradient Noise** ✓ | Panear UVs anima flujo continuo (lava, energía, humo). Dos capas a distinta velocidad = profundidad |
| **Soft particles** (partículas que no cortan contra geometría) | **Scene Depth** ✓ (modo **Eye**) − profundidad del fragmento → **Smoothstep**/Saturate → multiplica alpha | Requiere **Depth Texture activada en el URP Asset**. La partícula desvanece al acercarse a una superficie en vez de cortar con un borde duro |
| **Intersección / borde de agua/escudo** | **Scene Depth** ✓ comparada con profundidad del fragmento → línea brillante donde se cruzan | Mismo depth trick; resalta el contacto con geometría |
| **Distorsión de calor / refracción** | Scroll de noise sobre las UVs de un **Scene Color** (std) node | Sobre quad transparente tras la explosión/motor |

**Nodos de ruido procedural** (para todo lo orgánico): **Gradient Noise** ✓ (Perlin: UV, Scale), **Voronoi** ✓ (celular: UV, Angle Offset, Cell Density → Out, Cells), y **Simple Noise** (value noise, std — ⚠️confirmar nombre exacto en tu versión). Anima cualquiera de ellos con **Time** en las UVs para movimiento.

---

## 9. Combinar shader + partículas + luz (el efecto "completo")

Un efecto pro rara vez es una sola herramienta. La combinación estándar:

1. **Partículas** con **material de shader** (aditivo/emisivo, con soft particles y flipbook) — el cuerpo del efecto.
2. **Emisión HDR > 1.0** en el color/material → activa **Bloom** para el glow. Bloom (URP, Volume) verificado: **Threshold** (default 0.9), **Intensity** (0–1, default 0 = apagado), **Scatter** (radio, default 0.7), **Tint**, **Clamp** (default 65472). Subir la intensidad del color emisivo por encima de Threshold hace que brille; ese es el mecanismo real del "glow" en URP — no hay glow per-material, sale del post-proceso.
3. **Luz real** en el pico del efecto: módulo **Lights** del Particle System, o una `Light` instanciada 1–3 frames (explosión, muzzle flash), para que el efecto ILUMINE el entorno. Es caro — pocas, breves, con cap.
4. **Post**: además de Bloom, opcional Chromatic Aberration / Lens Distortion en un Volume pulsado para impactos grandes (con moderación — accesibilidad, [ver: gamedev/game-feel §4]).

Sin Bloom, los VFX emisivos se ven planos; con Bloom sin Threshold calibrado, TODO brilla y se lava. Ajusta Threshold para que solo lo intencionalmente brillante (VFX, no el mundo) pase el corte.

---

## 10. VFX en 2D (Sprite / URP 2D Renderer)

Con el **2D Renderer** de URP asignado en el pipeline asset. Detalle → [ver: vfx-2d], estilo → [ver: arte-2d/pixel-art].

| Técnica | Herramienta | Nota |
|---|---|---|
| **Efecto flipbook 2D** (explosión, chispazo dibujados) | Sprite sheet + Animator, o Particle System con **Texture Sheet Animation** sobre billboard | El look 2D estilizado casi siempre es flipbook dibujado, no simulación |
| **Partículas 2D** | Particle System (funciona en 2D), Simulation Space World, Renderer billboard | Polvo, chispas, humo estilizado |
| **Glow 2D** | **Light 2D** (component) + material **Sprite-Lit-Default** | Ver abajo |
| **Sorting** | Sorting Layer + Order in Layer del Renderer; Sort Mode del Particle System | El VFX debe quedar delante/detrás del sprite correcto |
| **Shader 2D** | Shader Graph con target Sprite (Lit/Unlit) | Dissolve, flash, outline sobre sprites |

**Light 2D** — tipos verificados (URP 2D): **2D Freeform** (polígono editable), **2D Sprite** (forma de un sprite), **2D Spot** (cono direccional), **2D Global** (ilumina todo por igual, una por blend style/sorting layer). No es iluminación física. Para glow: una Sprite/Point Light sobre el objeto emisivo + Bloom. Los sprites deben usar material **Sprite-Lit-Default** para responder a las luces 2D.

Flash de sprite (hit) en 2D: shader con `_FlashAmount` que hace lerp del color de textura a blanco, pulsado 1–3 frames [ver: gamedev/game-feel §2] — más barato que intercambiar sprites.

---

## 11. Dosificación aplicada a VFX

La regla de Jonasson/Purho — **añadir MÁS de lo razonable y luego recortar** — aplica directo al VFX [ver: gamedev/game-feel §2, §9]:

- Monta el efecto con **todas** las capas de la receta (flash + core + humo + chispas + onda + luz + Bloom), pásate.
- Míralo en movimiento, en contexto de juego (no aislado en una escena vacía) y a la escala real de pantalla.
- **Recorta**: quita capas hasta que quitar una MÁS se note que falta. Es más fácil calibrar bajando que subiendo desde cero.
- Cuidado especial en VFX con el **fillrate** y el **cap de partículas**: pasarse en autoría está bien, pasarse en runtime (miles de partículas grandes transparentes solapadas) mata el framerate [ver: optimizacion-vfx]. Recortar aquí es también rendimiento.
- Un efecto se ve "barato" casi siempre por FALTAR capas (solo partículas, sin flash/luz/Bloom/shake/sonido), no por sobrar.

---

## 12. Assets de VFX: crear vs comprar

| Opción | Cuándo | Nota |
|---|---|---|
| **Comprar** (Asset Store: packs de VFX Graph/Particle, sheets de fuego/humo/chispa) | Prototipo, efectos genéricos (fuego, humo, explosión estándar), equipo sin artista de VFX | Rápido; riesgo de look "de Asset Store" reconocible. Revisar licencia y que sea URP-compatible |
| **Crear texturas propias** | Identidad visual propia, estilo estilizado, control total | Ver abajo |

**Texturas de VFX que necesitas** (casi todo efecto sale de un puñado):
- **Chispa / spark** (punto blanco con glow suave, radial).
- **Humo / smoke** (mancha suave con alpha, a veces sheet de varios frames).
- **Flare / flash** (destello radial con rayos).
- **Noise / distortion** (para dissolve, disturbio, mask).
- **Gradient / ramp** (para Color over Lifetime o remaps).
- **Flipbook sheets** (fuego, explosión, impacto — grids 4×4/8×8).

Cómo producirlas:
- **Procedural en shader** (Gradient Noise/Voronoi ✓) evita texturas para muchos casos — más ligero, resolución infinita.
- Sheets de humo/fuego: simulación en software externo (EmberGen, Houdini, Blender) horneada a flipbook, o dibujadas.
- Chispa/flare/soft mask simples: generables con IA de imágenes (PNG con alpha) y limpiadas con una herramienta de remoción de fondo. Verificar siempre el alpha y que tile si debe tilear.

---

## Reglas prácticas

1. Un impacto NO es una capa: dispara flash + partículas + hit-stop + shake + sonido en el MISMO frame de contacto [ver: gamedev/game-feel].
2. Spawnea el VFX con **anim events anclados al clip**, nunca con timers paralelos — sobrevive a cambios de timing [ver: gamedev/animacion §7].
3. Decisión de herramienta: dibujo fijo→flipbook; comportamiento→Particle System; millones→VFX Graph; superficie continua→shader. La mayoría COMBINA.
4. Explosión = 6 capas (flash → core → humo → chispas → onda → debris), todas en frame 0, cada una con su duración; humo el que más dura.
5. Chispas y salpicaduras de impacto orientadas por la **normal del hit** (Shape = Cone rotado con `LookRotation(normal)`), no genéricas.
6. VFX distinto por material/superficie (piedra ≠ madera ≠ metal) — vende el mundo físico [ver: gamedev/game-feel §2].
7. Muzzle flash: 1–2 frames + Light breve; la brevedad es el efecto, no lo alargues.
8. Weapon trail: Trail Renderer con **Emitting** on/off por anim event solo en los frames active; Time corto para un arco limpio.
9. Estelas de partículas: **Rate over Distance** (Emission), no Rate over Time — densidad constante a cualquier velocidad.
10. Hechizo/magia en 3 fases: carga (partículas convergentes + glow subiendo, telegrafía) → release (burst) → impacto.
11. Restos con permanencia (casquillos, cráteres, debris con Collision) — presupuestados con cap y pooling [ver: gamedev/game-feel §2].
12. Fade = Color over Lifetime a alpha 0 + Size over Lifetime; nunca desaparición seca.
13. Glow = emisión HDR > 1.0 + **Bloom** (URP Volume), Threshold calibrado para que solo el VFX pase el corte. No hay glow per-material.
14. Soft particles: **Scene Depth** (Eye) − depth del fragmento → fade; activar Depth Texture en el URP Asset.
15. Dissolve: Gradient Noise/Voronoi → Step → Alpha Clip Threshold; borde incandescente con 2º Step + emission.
16. Luz real (Lights module / Light instanciada) SOLO en picos (explosión, muzzle), breve y con cap — es cara.
17. Ruido procedural en shader (Gradient Noise/Voronoi) antes que texturas cuando se pueda — más ligero.
18. 2D: Light 2D + material Sprite-Lit-Default para glow; flash de sprite con `_FlashAmount` en shader, no swap de sprites.
19. Dosifica: monta con TODAS las capas, míralo en juego a escala real, recorta hasta que falte algo [ver: gamedev/game-feel §9].
20. Cap de partículas (Main → Max Particles) y ojo al fillrate: pasarse en autoría OK, pasarse en runtime mata FPS [ver: optimizacion-vfx]. En móvil, Particle System (Shuriken) es la opción segura por defecto — VFX Graph exige compute shaders + SSBO, no soporta OpenGL ES y en URP móvil está en preview (solo unlit); no lo asumas disponible sin confirmar el hardware target.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| VFX de impacto sin flash/shake/sonido — solo partículas, se ve "barato" | Faltan capas: monta el juice stack completo (sección 2) [ver: gamedev/game-feel] |
| VFX disparado por timer paralelo, se desincroniza al cambiar la animación | Anim event anclado al clip [ver: gamedev/animacion §7] |
| Flash/burst que llega 3–4 frames tarde respecto al golpe | En el frame EXACTO de contacto; probar grabando a 60fps |
| Chispas de impacto genéricas en todas direcciones | Orientar por la normal del hit (Cone + LookRotation) |
| Emisivos que no brillan / se ven planos | Emisión HDR > 1.0 + Bloom con Threshold calibrado (no hay glow per-material en URP) |
| Bloom con Threshold bajo → TODO se lava y brilla | Subir Threshold hasta que solo el VFX intencional pase el corte |
| Partículas que cortan con borde duro contra el suelo | Soft particles (Scene Depth − fragment depth); activar Depth Texture en URP Asset |
| Weapon trail = mancha sucia todo el swing | Emitting solo en frames active + Time corto = arco limpio |
| Estela de partículas que se ralea al acelerar el objeto | Rate over Distance en vez de Rate over Time |
| Muzzle flash animado largo y persistente | 1–2 frames y fuera; la brevedad ES el efecto |
| Usar VFX Graph esperando colisión física precisa (debris que rueda) | VFX Graph colisiona aprox. (depth/SDF); para física real, Particle System con módulo Collision |
| Meter VFX Graph en el build móvil sin chequear el hardware | Requiere compute shaders + SSBO, sin Open GL ES, URP móvil en preview (solo unlit); default en móvil = Particle System |
| Miles de partículas grandes transparentes solapadas → FPS al piso | Cap de Max Particles + reducir tamaño/overdraw; medir fillrate [ver: optimizacion-vfx] |
| Humo que sigue al emisor de forma antinatural | Simulation Space = World (Main) |
| Copiar nombres de bloques de VFX Graph de memoria | Confirmar en el Node Library de tu versión; no todo módulo de Particle System tiene equivalente idéntico |
| Fade seco (partícula desaparece de golpe) | Color over Lifetime → alpha 0 + Size over Lifetime |
| Sprites 2D que no responden a Light 2D | Material Sprite-Lit-Default + 2D Renderer asignado en el pipeline asset |
| Efecto calibrado en escena vacía, se ve mal en juego | Calibrar SIEMPRE en contexto de gameplay, a escala de pantalla real |

## Fuentes

- **Particle System modules** — Unity Manual (docs.unity3d.com, Unity 6) — nombres exactos de los ~24 módulos (Main, Emission, Shape, Velocity/Color/Size over Lifetime, Noise, Sub Emitters, Texture Sheet Animation, Trails, Renderer…).
- **Emission module** — Unity Manual — Rate over Time, Rate over Distance, Bursts (Time, Count, Cycles, Interval, Probability).
- **Sub Emitters module** — Unity Manual — condiciones Birth / Collision / Death / Trigger / Manual y su uso para explosión (Death) e impacto (Collision).
- **Texture Sheet Animation module** — Unity Manual (Unity 6) — Mode Grid/Sprites, Tiles X/Y, Animation Whole Sheet/Single Row, Frame over Time, Start Frame, Cycles.
- **Particle System Renderer module** — Unity Manual (Unity 6) — Render Mode (Billboard, Stretched/Horizontal/Vertical Billboard, Mesh), Sort Mode, Sorting Fudge, Material.
- **Trail Renderer component** — Unity Manual — Time, Min Vertex Distance, Width, Color, Emitting, AutoDestruct, Alignment (View/TransformZ), Texture Mode.
- **Line Renderer properties** — Unity Manual — Positions, Width, Color, Use World Space, Loop, Corner/End Cap Vertices, Alignment, Texture Mode.
- **VFX Graph — Contexts** — Unity VFX Graph docs (com.unity.visualeffectgraph@17) — arquitectura Spawn / Initialize / Update / Particle Output y Blocks; simulación GPU. (Verificado por fetch directo 2026-07-20: la doc nombra los contextos "Initialize", "Update" y "Particle Output" — no "Initialize/Update/Output Particle" como se listaba antes.)
- **VFX Graph — System Requirements** — Unity VFX Graph docs (com.unity.visualeffectgraph@17) — verificado 2026-07-20: compute shaders + SSBO obligatorios, sin soporte Open GL ES, URP en móvil en preview (solo partículas unlit, incompatible con gamma color space).
- **Shader Graph — Fresnel Effect node** — Unity Shader Graph docs (@17) — Normal, View Dir, Power → Out; uso para rim/glow.
- **Shader Graph — Voronoi node** — Unity Shader Graph docs (@17) — UV, Angle Offset, Cell Density → Out, Cells; ruido celular procedural.
- **Shader Graph — Gradient Noise node** — Unity Shader Graph docs (@17) — UV, Scale → Out (Perlin); ruido procedural.
- **Shader Graph — Scene Depth node** — Unity Shader Graph docs (@17) — modos Linear01/Raw/Eye; base de soft particles e intersección (requiere Depth Texture en URP Asset).
- **Bloom (post-processing)** — Unity URP docs (Unity 6) — Threshold (0.9), Intensity, Scatter (0.7), Tint, Clamp; el glow de VFX sale de emisión HDR > Threshold vía post-proceso.
- **2D Lights introduction** — Unity URP docs (Unity 6) — tipos 2D Freeform / Sprite / Spot / Global; no físico; Sprite-Lit-Default + 2D Renderer.
- **Game feel y juice** ([ver: gamedev/game-feel], este repo) — el porqué del feel: el juice stack, hit-stop, shake, dosificación (Jonasson/Purho, Vlambeer).
- **Animación para juegos** ([ver: gamedev/animacion], este repo) — timing wind-up/active/recovery, anim events, telegraphing — la sincronización del VFX con la animación.
