# Partículas: Particle System y VFX Graph

> **Cuando cargar este archivo:** al construir cualquier efecto de partículas en Unity 6 / URP — chispas de impacto, humo, fuego, magia, polvo, restos, trails — sea con el Particle System (Shuriken, CPU) o con VFX Graph (GPU); al decidir cuál de los dos usar; al disparar bursts por código sincronizados con gameplay/animación; o al hacer que una partícula dispare lógica de juego (colisión/trigger). El PORQUÉ del feel (por qué el flash vende el golpe, permanence, dosificación) está en [ver: gamedev/game-feel] y la integración base del feel en [ver: pipeline/feel-en-unity] — aquí va el módulo/nodo/parámetro concreto. Shaders de partícula: base en [ver: shader-graph-fundamentos], recetas en [ver: recetas-shaders].

## Los dos sistemas: tabla de decisión honesta

Unity tiene DOS sistemas de partículas, no intercambiables:

| | **Particle System (Shuriken)** | **VFX Graph** |
|---|---|---|
| Simulación | **CPU** | **GPU** (compute shaders) |
| Package | Integrado en el core | `com.unity.visualeffectgraph` (instalar) |
| Cantidad práctica | miles (decenas de miles ya duele en CPU/móvil) | **millones** |
| Autoría | Inspector con **módulos** (tabs) | **grafo** de nodos + contexts |
| Móvil | **Casi siempre este.** Corre en todo, incluido GLES | ⚠️ NO out-of-preview en móvil; **no soporta OpenGL ES**; en URP solo **unlit** y sin gamma color space |
| Requisito HW | ninguno especial | `SystemInfo.supportsComputeShaders` + SSBOs (`maxComputeBufferInputsVertex > 0`) |
| Colisión con la escena | **Sí** (World/Planes, `OnParticleCollision`) | limitada (depth-buffer / signed distance fields; no colisión con colliders arbitrarios) |
| Leer estado por partícula en CPU | **Sí** (`GetParticles`, callbacks) | No trivial (viven en GPU) |
| Control fino por gameplay | **Sí** — cada partícula accesible en C# | Menos directo; se maneja por propiedades expuestas |

**Regla de elección:**
- **Móvil o efecto que interactúa con gameplay/colisión → Shuriken.** Es el default para un juego indie/móvil. [ver: unity/rendimiento-unity]
- **VFX Graph solo cuando:** target es desktop/consola con GPU capaz, y necesitas volumen masivo (tormentas de nieve, campos de mil proyectiles, disoluciones, efectos data-driven complejos) que la CPU no aguanta. No lo elijas "porque es más nuevo".
- Detalle de optimización de ambos: [ver: optimizacion-vfx]. Recetas concretas de efectos: [ver: vfx-recetas]. Efectos 2D: [ver: vfx-2d].

---

# PARTICLE SYSTEM (Shuriken)

Se autoría por **módulos**: cada tab del componente `ParticleSystem` es un módulo activable. Los 24 módulos, agrupados por función:

| Grupo | Módulos |
|---|---|
| Estado inicial | **Main**, Emission, Shape |
| Movimiento | Velocity over Lifetime, Noise, Limit Velocity over Lifetime, Inherit Velocity, Lifetime by Emitter Speed, Force over Lifetime, External Forces |
| Apariencia | Color over Lifetime, Color by Speed, Size over Lifetime, Size by Speed, Rotation over Lifetime, Rotation by Speed |
| Física / eventos | Collision, Triggers, Sub Emitters |
| Render | Texture Sheet Animation, Lights, Trails, Custom Data, **Renderer** |

## Main module — el estado inicial de cada partícula

Controla el valor con el que NACE cada partícula. Propiedades clave:

| Propiedad | Qué hace | Nota |
|---|---|---|
| **Duration** | Cuánto dura un ciclo de emisión (seg) | No es la vida de la partícula |
| **Looping** | Repite el ciclo | OFF para efectos one-shot (explosión) |
| **Prewarm** | Arranca "ya en régimen" (como si llevara rato corriendo) | Solo con Looping ON; para humo/fuego de ambiente ya lleno |
| **Start Delay** | Retraso antes de emitir | |
| **Start Lifetime** | Vida de cada partícula (seg) | La palanca #1 de "cuánto se ve" |
| **Start Speed** | Velocidad inicial en la dirección de la Shape | |
| **Start Size / Start Rotation / Start Color** | Tamaño / giro / color+alpha iniciales | Cada uno acepta constante, curva o Random Between Two |
| **Gravity Modifier** | Multiplica la gravedad del proyecto (0 = ingrávido) | Humo: 0 o negativo (sube); restos: 1 |
| **Simulation Space** | **Local** (siguen al emisor), **World** (se quedan donde nacieron), **Custom** | ⚠️ El error más común: trail/humo en Local que "se arrastra" con el objeto → debe ser **World** |
| **Simulation Speed** | Multiplica el tiempo de la simulación | Para slow-mo/hit-stop [ver: gamedev/game-feel] |
| **Max Particles** | Cap duro de partículas vivas (default **1000**) | Presupuesto por sistema; al llegar deja de emitir |
| **Play On Awake** | Arranca solo al habilitarse | OFF para bursts disparados por código |
| **Stop Action** | Qué pasa al terminar: None / Disable / Destroy / **Callback** | Callback → `OnParticleSystemStopped()` (clave para pooling) |
| **Ring Buffer Mode** | Recicla las más viejas en vez de matarlas al morir | Trails/estelas persistentes con cap |

Cada propiedad "varying" tiene modos: **Constant**, **Curve**, **Random Between Two Constants**, **Random Between Two Curves**. La aleatoriedad barata (Random Between Two) es lo que da variedad orgánica.

## Emission — cuántas y cuándo

| Propiedad | Qué hace |
|---|---|
| **Rate over Time** | Partículas por segundo (flujo continuo: humo, fuego) |
| **Rate over Distance** | Partículas por unidad de distancia recorrida (trail de polvo al correr — 0 si el emisor está quieto) |
| **Bursts** | Ráfagas discretas programadas |

Cada Burst tiene: **Time** (seg desde que arranca), **Count** (cuántas emite), **Cycles** (cuántas veces se repite), **Interval** (seg entre ciclos), **Probability** (0–1, likelihood de que dispare; 1 = garantizado). Una explosión = un burst con Count alto, Cycles 1. [ver: gamedev/game-feel §2 dosificación]

## Shape — de dónde salen y hacia dónde

Define el volumen/superficie de emisión y la dirección inicial. **12 tipos**: Sphere, Hemisphere, Cone, Donut, Box, Mesh, Mesh Renderer, Skinned Mesh Renderer, Sprite, Sprite Renderer, Circle, Edge.

| Uso típico | Shape + settings |
|---|---|
| Explosión / burst radial | **Sphere** (Radius) |
| Fuego, chorro, muzzle, fuente | **Cone** — Angle (apertura), Radius, Length, **Emit from: Base / Volume** |
| Chispas de impacto direccionales | **Cone** estrecho orientado por la normal del hit |
| Polvo desde el suelo, área | **Box** — Emit from: Volume / Edge / Shell |
| Partículas sobre la silueta de un modelo (disolución, aura) | **Mesh / Skinned Mesh Renderer** — Type: Vertex / Edge / Triangle, Normal Offset |
| Anillo (portal, onda) | **Donut** o **Circle** con **Arc** |

Propiedades comunes: **Radius**, **Arc** (porción del círculo, para abanicos/conos parciales), **Randomize Direction** (mezcla la dirección hacia una random — desordena), **Spherize Direction** (empuja hacia afuera del centro), **Align to Direction** (orienta el sprite según su dirección de viaje — clave para chispas alargadas). Position/Rotation/Scale reposicionan la shape respecto al emisor.

## Movimiento over lifetime

| Módulo | Propiedades exactas | Para qué |
|---|---|---|
| **Velocity over Lifetime** | Linear X/Y/Z, **Space** (Local/World), Orbital X/Y/Z, Offset X/Y/Z, Radial, **Speed Modifier** | Deriva controlada; Orbital = giro alrededor de un eje (chispas que orbitan); Radial = hacia/desde el centro |
| **Force over Lifetime** | Force X/Y/Z, Space (Local/World), **Randomize** | Aceleración constante: viento, corrientes, atracción. Randomize = dirección nueva por frame (turbulencia) |
| **Limit Velocity over Lifetime** | Speed (limit), Dampen, Drag | Frenar partículas (humo que se estanca, restos que se detienen) |
| **Noise** | **Strength**, **Frequency** (bajo=suave, alto=abrupto), **Scroll Speed**, Damping, **Octaves** (capas), Octave Multiplier, Octave Scale, **Quality**, Remap, **Position/Rotation/Size Amount** | La palanca de vida orgánica: humo que serpentea, magia que ondula, chispas que no van rectas. Móvil: pocas Octaves, Quality baja |
| **Inherit Velocity** | Multiplier, curva | Sub-partículas que heredan la velocidad del padre (estela que sigue al proyectil) |
| **External Forces** | Multiplier, Influence | Reacciona a componentes **Wind Zone** / Particle System Force Field |

## Apariencia over lifetime

| Módulo | Propiedades | Uso |
|---|---|---|
| **Color over Lifetime** | **Color** (Gradient: borde izq = nacimiento, der = muerte; RGBA) | El fade-out canónico: chispa naranja → transparente. El alpha del gradient controla la desaparición |
| **Size over Lifetime** | **Size** (curva), **Separate Axes** (X/Y/Z independientes) | Humo que crece; chispa que se encoge al morir; onda que se expande |
| **Rotation over Lifetime** | **Angular Velocity** (grados/seg), Separate Axes | Restos que giran, humo que rota lento |
| **Color by Speed** | Gradient + rango de Speed | Color según velocidad (rápido=brillante). Diferente de "over Lifetime" (tiempo) |
| **Size by Speed / Rotation by Speed** | curva + rango de Speed | Stretch/giro proporcional a la velocidad |

Regla de feel: casi todo efecto lleva **Color over Lifetime** (fade con alpha) + **Size over Lifetime** (curva de nacimiento→muerte). Sin esos dos, las partículas "aparecen y desaparecen" de golpe y se ven baratas.

## Texture Sheet Animation — sprites animados (explosiones, humo frame-a-frame)

Trata la textura como una grilla de sub-imágenes y las reproduce como flipbook.

| Propiedad | Qué hace |
|---|---|
| **Mode** | **Grid** (grilla regular) o **Sprites** (lista de sprites) |
| **Tiles** | X / Y — divisiones de la grilla |
| **Animation** | **Whole Sheet** (toda la hoja como una secuencia) / **Single Row** (cada fila una animación) |
| **Time Mode** | **Lifetime** (curva sobre la vida) / **Speed** / **FPS** |
| **Row Mode** (Single Row) | Custom / **Random** (fila al azar por partícula → variedad) / Mesh Index |
| **Frame over Time** | Curva que controla qué frame se muestra |
| **Start Frame** | Frame inicial (desfasar para que no todas empiecen igual) |
| **Cycles** | Repeticiones de la animación sobre la vida |

Uso: una hoja de 8×8 de una explosión de humo real reproducida sobre la vida de la partícula = explosión volumétrica barata sin miles de partículas.

## Renderer — cómo se dibuja

| Propiedad | Opciones / valores | Nota |
|---|---|---|
| **Render Mode** | **Billboard** (siempre encara según Render Alignment), **Stretched Billboard**, Horizontal Billboard, Vertical Billboard, **Mesh** (3D), **None** | Billboard = default; Mesh = restos/escombros 3D; Stretched = balas/chispas rápidas |
| **Render Alignment** | View, World, Local, **Facing**, **Velocity** | Velocity/Facing para orientar según movimiento |
| **Length Scale / Velocity Scale** | (solo Stretched) estira según tamaño / según velocidad | Chispa/rayo que se alarga con la velocidad |
| **Material** | material de partícula (ver shaders abajo) | |
| **Trail Material** | material del módulo Trails | |
| **Sort Mode** | None, By Distance, Oldest in Front, Youngest in Front, By Depth | Orden de dibujo dentro del sistema |
| **Sorting Fudge** | sesga la prioridad vs otros transparentes | Para meter/sacar el efecto respecto a otros objetos transparentes |

Overdraw: las partículas son transparentes (alpha blend) → dibujan siempre, tapen lo que tapen. Muchas partículas grandes superpuestas = fillrate quemado, el asesino en móvil. Menos partículas + más grandes con buen arte > nube de mil sprites. [ver: unity/rendering-urp §overdraw] [ver: optimizacion-vfx]

## Collision — partículas que chocan con la escena

| Propiedad | Qué hace |
|---|---|
| **Type** | **World** (colisiona con GameObjects de la escena) / **Planes** (planos definidos por Transforms — barato) |
| **Collision Mode** | 3D / 2D (solo World) |
| **Dampen** | fracción de velocidad que pierde al chocar |
| **Bounce** | fracción que rebota |
| **Lifetime Loss** | fracción de vida que pierde al chocar (0 = sobrevive; 1 = muere al primer golpe) |
| **Radius Scale** | ajusta la esfera de colisión al tamaño visual |
| **Collides With** | máscara de layers |
| **Collision Quality** | **High** (siempre consulta la física directo — preciso, caro) / **Medium** y **Low** (ambos usan voxel grid cache — **solo colliders estáticos que no se mueven**; Low consulta la física con menos frecuencia que Medium → más barato) |
| **Send Collision Messages** | ON → dispara `OnParticleCollision(GameObject other)` en scripts | La partícula avisa a gameplay |

**Planes** es mucho más barato que World: para un suelo plano (restos que caen y se acumulan), un plano basta. World High solo si de verdad necesitas colisión precisa contra geometría compleja.

## Triggers — partícula que dispara lógica de juego

Distinto de Collision: no altera la física, solo **reporta** la relación partícula↔collider. Lista de colliders + cuatro eventos, cada uno con acción **Ignore / Kill / Callback**:

| Evento | Cuándo |
|---|---|
| **Inside** | cada frame que la partícula está DENTRO del collider |
| **Outside** | cada frame que está FUERA |
| **Enter** | el frame que ENTRA |
| **Exit** | el frame que SALE |

**Collider Query Mode**: Disabled / One / All. Con acción **Callback** → `OnParticleTrigger()`, dentro se llama `ps.GetTriggerParticles(ParticleSystemTriggerEventType.Enter, particles)` para leer/modificar las partículas afectadas.

**Patrón "partícula que dispara gameplay":** partícula de fuego entra en un trigger volume → Enter=Callback → en `OnParticleTrigger` aplicas daño / enciendes algo. O al revés: `OnParticleCollision` en el objeto golpeado por las chispas para reaccionar.

## Sub Emitters — partículas que emiten partículas

Un sub-sistema se dispara según el estado del padre:

| Condición | Cuándo emite |
|---|---|
| **Birth** | durante toda la vida del padre (soporta varios bursts) |
| **Collision** | cuando el padre colisiona (requiere módulo Collision) |
| **Death** | cuando el padre muere |
| **Trigger** | al interactuar con un trigger volume |
| **Manual** | solo vía `ParticleSystem.TriggerSubEmitter()` |

Con **Emit Probability** e **Inherit** (qué hereda del padre: color, size, rotation, lifetime, etc.). Casos: cohete con **Birth**=humo de estela + **Death**=explosión; gota que al chocar (**Collision**) salpica; chispa que deja mini-trail.

## Emisión por evento: disparar desde código

Sincronizar el burst con el gameplay o con un frame de animación (no con `Play On Awake`):

```csharp
public ParticleSystem impacto;   // Play On Awake = OFF, Looping = OFF

// Burst simple con las props del inspector:
impacto.Emit(30);

// Burst con overrides por código (posición, color, velocidad):
var ep = new ParticleSystem.EmitParams {
    position    = hit.point,
    applyShapeToPosition = true,
    startColor  = Color.yellow,
    velocity    = hit.normal * 4f
};
impacto.Emit(ep, 20);

// Control de reproducción de un sistema completo:
impacto.Play();     // arranca emisión
impacto.Stop();     // deja de emitir (las vivas terminan su vida)
impacto.Pause();
impacto.Clear();    // borra las vivas ya
impacto.TriggerSubEmitter(0);   // dispara un sub-emitter Manual
```

- **Sincronizar con animación:** un **Animation Event** en el frame del golpe llama a un método que hace `Emit()` / `Play()`. Así el polvo del pisotón sale en el frame exacto del contacto. [ver: pipeline/feel-en-unity]
- `EmitParams` overridea solo lo que setees; lo demás sale del inspector.
- Métricas útiles: `ps.particleCount`, `ps.isStopped`, `ps.isEmitting`, `ps.GetParticles(array)` para leer/modificar partículas vivas en CPU (Shuriken only).

## Pooling de sistemas de partículas

Instanciar/destruir un prefab de partículas por cada impacto genera GC spikes y stutter. Poolear:

1. Prefab del efecto con **Stop Action = Callback**.
2. Al terminar, Unity llama `OnParticleSystemStopped()` en un script del prefab → devuelve el objeto al pool (SetActive(false)) en vez de destruirlo.
3. Al necesitar el efecto: sacar del pool, reposicionar, `Clear()` + `Play()`.
4. Alternativa de reciclaje in-place: **Ring Buffer Mode** para estelas/restos con cap sin crear objetos.

Unity 6 trae `UnityEngine.Pool.ObjectPool<T>` para esto. Permanence (casquillos/cráteres que quedan) SIEMPRE con pool + cap de instancias, nunca acumulación infinita. [ver: gamedev/game-feel §permanence] [ver: pipeline/feel-en-unity]

## Materiales / shaders de partícula

URP trae tres shaders de partícula: **Particles Unlit**, **Particles Simple Lit**, **Particles Lit** (elegir el más barato que dé el look — Unlit para la mayoría de VFX). Surface Type **Opaque / Transparent**; en Transparent, **Blending Mode**:

| Blending | Qué hace | Úsalo para |
|---|---|---|
| **Additive** | suma el color al fondo (nunca oscurece; se acumula brillo) | **Fuego, magia, energía, glow, chispas, láser** — lo que emite luz |
| **Alpha** | mezcla por el alpha del material | **Humo, polvo, niebla, nubes** — lo que bloquea/tinta |
| **Premultiply** | como Alpha pero RGB ya multiplicado por alpha | bordes limpios mezclando additive+alpha en la misma textura (humo con núcleo brillante) |
| **Multiply** | multiplica con el fondo (oscurece) | sombras, manchas oscuras, humo negro denso |

- **Additive + emission/HDR** es lo que alimenta el **Bloom** → el glow de fuego/magia sale de ahí, no de la partícula sola. HDR ON en el URP Asset. [ver: unity/rendering-urp §post-processing]
- Additive no necesita ordenamiento perfecto (la suma es conmutativa) → más barato en overdraw que alpha ordenado. Pero se satura a blanco: no abuses en pantalla llena.
- Shaders de partícula custom (dissolve, distorsión, flipbook con soft particles) en Shader Graph con target **Unlit** o el nodo apropiado: [ver: shader-graph-fundamentos], recetas en [ver: recetas-shaders].

---

# VFX GRAPH (GPU)

Grafo de **contexts** conectados verticalmente (el flujo de datos de la partícula):

| Context | Rol |
|---|---|
| **Spawn** | Decide CUÁNTAS y cuándo (loop duration/count, delay; estados Running/Idle/Waiting). Recibe flujo Start/Stop |
| **Initialize** | Corre una vez por partícula nueva: setea capacidad del sistema (**Capacity**), bounds, y atributos iniciales |
| **Update** | Corre cada frame sobre TODAS las vivas: integra velocidad/rotación, envejece y mata las expiradas |
| **Output** | Renderiza. Contexts de salida confirmados en la doc de VFX Graph 17.0: **Output Particle Mesh** / **Output Mesh** (mesh), **Output Point**, **Output Primitive** (quad/triángulo/octágono, el equivalente billboard), **Output Line** (líneas/estelas), y sus variantes con Shader Graph propio (**Output ShaderGraph Quad**, **Output ShaderGraph Mesh**, **Output ShaderGraph Strip**). El set exacto disponible varía según si el proyecto usa el flujo "Shader Graph output" (Unity 6 / VFX Graph 17) o los outputs clásicos — confirmar el nombre en el menú "Create Node" del Editor real antes de asumirlo |

Flujo: **Spawn → Initialize → Update → Output** (Update es opcional; un efecto estático puede ir Initialize → Output).

## Disparar VFX Graph desde código

El componente en escena es **Visual Effect** (referencia a un VFX asset). Se controla por eventos y **propiedades expuestas** (Blackboard):

```csharp
using UnityEngine.VFX;

public VisualEffect vfx;

vfx.Play();                       // manda evento OnPlay (habilita el Spawn)
vfx.Stop();                       // manda OnStop
vfx.SendEvent("Explosion");       // dispara un Event context custom llamado "Explosion"

// Propiedades expuestas (equivalen a los "parámetros" del gameplay):
vfx.SetFloat("Intensity", 2f);
vfx.SetVector3("Direction", dir);
vfx.SetInt("BurstCount", 50);
vfx.SetTexture("FlipbookTex", tex);
vfx.SetBool("Trail", true);
```

- Eventos default: **OnPlay** / **OnStop** (implícitos). Para bursts nombrados, crear un **Event (Context)** con nombre y dispararlo con `SendEvent("nombre")`.
- **GPU Events** (experimental): partículas que spawnean partículas en GPU vía **Trigger Event Blocks → GPUEvent context** (equivalente a Sub Emitters, pero todo en GPU, sin ida-y-vuelta a CPU).
- El límite de partículas se fija en **Capacity** (Initialize context), no en un "Max Particles".

## Requisitos y límites de VFX Graph (móvil)

- Requiere **compute shaders** (`SystemInfo.supportsComputeShaders == true`) y **SSBOs**.
- **NO out-of-preview en móvil**; **no soporta OpenGL ES**. En URP: solo **partículas unlit** y **sin gamma color space**, y soporta solo un subconjunto de plataformas (HDRP soporta más).
- Traducción práctica: en un juego móvil, **VFX Graph no es la opción por defecto** — verifica `supportsComputeShaders` en el device real más débil del target antes de comprometerte. Para móvil masivo, muchas veces sale mejor Shuriken bien optimizado. [ver: unity/rendimiento-unity]

---

## Partículas y el feel (qué efecto para qué sensación)

El PORQUÉ está en [ver: gamedev/game-feel §2 repertorio de juice]; aquí el mapeo a módulos:

| Sensación | Receta de partículas |
|---|---|
| **Impacto conectó** (chispas) | Burst por código (`Emit`) en el frame del hit; Shape Cone estrecho orientado por `hit.normal`; Stretched Billboard con Velocity Scale; Additive; Color over Lifetime naranja→transparente; Size over Lifetime decreciente; vida corta (0.2–0.5 s) |
| **Peso / destrucción** (humo) | Rate over Time o burst; Alpha blend; Simulation Space **World**; Gravity Modifier ≤0 (sube); Size over Lifetime creciente; Noise suave; Start Rotation aleatoria |
| **Permanence** (restos que quedan) | Sub Emitter Death o burst de escombros con Render Mode **Mesh**; Collision Type Planes (caen al suelo y paran) o Ring Buffer; **con pool + cap** |
| **Estela de proyectil** | módulo **Trails** o Rate over Distance; Inherit Velocity; Additive |
| **Muzzle flash** | burst de 1 partícula grande, vida ~0.05 s, Additive, sincronizado al disparo |

Estos efectos amplifican; no sustituyen un buen core loop ni el hit-stop/shake. Ver la advertencia de Vlambeer en [ver: gamedev/game-feel §9].

## Presupuesto de partículas por plataforma (heurística práctica, no cifra oficial de Unity)

El costo real es **overdraw × recuento**, no solo el número. Puntos de partida a validar en el device real:

| Target | Orientación |
|---|---|
| **Móvil low-end / GLES** | Shuriken siempre. Pocos sistemas simultáneos; partículas grandes y pocas (decenas por efecto), no nubes. Noise/Collision baratos (Quality Low, Planes). Max Particles ajustado al pico real, no 1000 por defecto |
| **Móvil high-end** | Shuriken; cientos por efecto tolerable si el overdraw es bajo (partículas chicas, additive sin ordenar) |
| **Desktop / consola** | Shuriken hasta miles cómodo; **VFX Graph** cuando de verdad necesitas 10⁴–10⁶ |

Reglas transversales: bajar **Max Particles** al mínimo que se vea bien; **Culling Mode** para pausar sistemas fuera de cámara; medir overdraw con el modo Overdraw / Frame Debugger; pooling siempre. Detalle en [ver: optimizacion-vfx] y [ver: unity/rendimiento-unity].

## Reglas prácticas

1. **Móvil o interacción con gameplay/colisión → Shuriken.** VFX Graph solo en desktop/consola con GPU capaz y volumen que la CPU no aguanta.
2. Antes de comprometer VFX Graph en móvil, verificar `SystemInfo.supportsComputeShaders` en el device real más débil; recordar que no corre en OpenGL ES.
3. Humo/estelas/restos que no deben "arrastrarse" con el objeto → **Simulation Space = World**. Es el bug #1.
4. Casi todo efecto lleva **Color over Lifetime** (fade por alpha) + **Size over Lifetime** — sin eso las partículas se ven baratas (aparecen/desaparecen de golpe).
5. Efecto one-shot (explosión, hit) → Looping OFF, Play On Awake OFF, disparado por `Emit()`/`Play()` desde código o Animation Event, no en loop.
6. Chispas de impacto: burst por `Emit`, Shape Cone estrecho orientado por `hit.normal`, Stretched Billboard, Additive, vida corta.
7. **Additive** para lo que emite luz (fuego/magia/chispas); **Alpha** para lo que bloquea (humo/polvo). Additive + HDR alimenta el Bloom [ver: unity/rendering-urp].
8. Elegir el shader de partícula más barato: **Particles Unlit** salvo que de verdad necesite luz.
9. Colisión barata: **Planes** para un suelo plano; **World High** solo si necesitas geometría precisa; Collision Quality **Medium/Low** (ambos usan voxel cache) solo sirven con colliders estáticos que no se mueven.
10. Partícula que dispara gameplay: Triggers con acción **Callback** + `OnParticleTrigger`/`GetTriggerParticles`, o `OnParticleCollision` (necesita Send Collision Messages ON).
11. **Poolear** todo efecto frecuente: Stop Action = Callback → `OnParticleSystemStopped` → devolver al pool. Nunca Instantiate/Destroy por hit.
12. Permanence (restos, casquillos, cráteres) con pool + **cap** de instancias; considerar Ring Buffer Mode. [ver: gamedev/game-feel]
13. Variedad orgánica barata: Random Between Two Constants en Start Size/Rotation/Lifetime + Start Frame aleatorio en Texture Sheet Animation.
14. Noise para vida orgánica (humo/magia), pero en móvil pocas Octaves y Quality baja.
15. Bajar **Max Particles** al pico real medido; activar **Culling Mode** para sistemas fuera de cámara; vigilar **overdraw** (partículas grandes superpuestas = fillrate). [ver: optimizacion-vfx]
16. Sincronizar el burst con el frame exacto del golpe vía **Animation Event**, no a ojo.
17. VFX Graph: el límite es **Capacity** en el Initialize context; disparar por `SendEvent("nombre")` y parametrizar por `SetFloat/SetVector3/...` de propiedades expuestas.
18. Sub Emitters para efectos compuestos (cohete: Birth=estela + Death=explosión) en vez de tres sistemas manejados a mano.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| El humo/trail se "arrastra" pegado al objeto que se mueve | Simulation Space **World** (estaba en Local) |
| VFX Graph puesto en un juego móvil y "no se ve nada" en algunos devices | No corre en OpenGL ES ni está out-of-preview en móvil; verificar `supportsComputeShaders`; usar Shuriken |
| Partículas aparecen y desaparecen de golpe, se ven baratas | Falta **Color over Lifetime** (alpha fade) y **Size over Lifetime** |
| El fuego/magia additive no "brilla" (no hace bloom) | Bloom necesita HDR ON + emission/valores >1; additive solo no basta [ver: unity/rendering-urp] |
| Stutter/GC al spawnear efectos por impacto | No Instantiate/Destroy: pooling (Stop Action Callback + `OnParticleSystemStopped`) |
| `OnParticleCollision` nunca se llama | Falta **Send Collision Messages** ON en el módulo Collision |
| `OnParticleTrigger` no reporta partículas | Falta la acción **Callback** en el evento (Enter/Inside/...) y/o los colliders en la lista |
| FPS se hunde con "pocas" partículas en móvil | Overdraw: partículas grandes transparentes superpuestas; menos y más chicas, o additive; medir con modo Overdraw |
| El burst sale desincronizado del golpe | Dispararlo con Animation Event en el frame de contacto, no con Rate/loop |
| Restos infinitos acumulándose (memoria/FPS a pique) | Cap de instancias + pool, o Ring Buffer Mode |
| Explosión que se repite en loop | Main: Looping OFF; disparar con `Play()`/`Emit()` |
| Additive saturando toda la pantalla a blanco | Additive se acumula; bajar cantidad/alpha o usar Premultiply/Alpha en zonas densas |
| Sub-emitter Collision no emite | Requiere el módulo **Collision** activo en el sistema padre |
| Max Particles default 1000 comiendo memoria en 20 sistemas | Ajustar Max Particles al pico real de cada efecto |

## Fuentes

- Particle System modules (reference) — Unity Manual 6000.2 (docs.unity3d.com/Manual/ParticleSystemModules.html) — inventario exacto de los 24 módulos y su función.
- Main / Emission / Shape module — Unity Manual 6000.2 — propiedades exactas: Simulation Space, Max Particles, Stop Action, Ring Buffer; Rate over Time/Distance y Bursts (Time/Count/Cycles/Interval/Probability); los 12 shape types y Emit from Base/Volume/Edge/Shell.
- Velocity / Force / Noise / Color over Lifetime / Size over Lifetime / Rotation over Lifetime module — Unity Manual 6000.2 — nombres exactos (Linear/Orbital/Radial/Speed Modifier; Octaves/Frequency/Strength; Angular Velocity; Separate Axes).
- Collision module + Triggers module — Unity Manual 6000.2 — Type World/Planes, Dampen/Bounce/Lifetime Loss, Collision Quality, Send Collision Messages/`OnParticleCollision`; eventos Inside/Outside/Enter/Exit → Ignore/Kill/Callback, `OnParticleTrigger`/`GetTriggerParticles`.
- Sub Emitters module — Unity Manual 6000.2 — condiciones Birth/Collision/Death/Trigger/Manual, Emit Probability, Inherit, `TriggerSubEmitter`.
- Texture Sheet Animation module — Unity Manual 6000.2 — Grid/Sprites, Tiles, Whole Sheet/Single Row, Time Mode Lifetime/Speed/FPS, Row Mode, Frame over Time, Start Frame, Cycles.
- Renderer module — Unity Manual 6000.2 — Render Mode (Billboard/Stretched/Horizontal/Vertical/Mesh/None), Render Alignment, Length/Velocity Scale, Sort Mode, Sorting Fudge.
- ParticleSystem.Emit / ScriptReference — Unity ScriptReference — overloads `Emit(int)` y `Emit(EmitParams, int)`; control Play/Stop/Pause.
- Particles shaders in URP (Particles Simple Lit / Lit / Unlit) — Unity Manual 6000.2 (URP) — Surface Type Opaque/Transparent y Blending Mode Alpha/Premultiply/Additive/Multiply.
- Visual Effect Graph — overview, Contexts, Events, System Requirements — Unity Packages docs (com.unity.visualeffectgraph@17.0) — GPU sim, contexts Spawn/Initialize/Update/Output, OnPlay/OnStop, GPU Events (experimental), requisito compute shaders/SSBOs, sin OpenGL ES, móvil no out-of-preview, URP solo unlit.
- VFX.VisualEffect (component) — Unity ScriptReference — `Play`/`Stop`/`SendEvent` y setters `SetFloat/SetVector3/SetInt/SetTexture/SetBool` para propiedades expuestas.
- Introduction to Particle Systems — Unity Learn (Unity Technologies) — concepto de sistema de partículas, arquitectura de módulos y optimización por culling/ring buffer (nivel introductorio).
