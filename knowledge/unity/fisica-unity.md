# Física en Unity (2D y 3D)

> **Cuando cargar este archivo:** al implementar movimiento, colisiones, triggers, raycasts, character controllers o cualquier Rigidbody/Collider; también al depurar jitter, objetos que atraviesan paredes o colisiones que no disparan mensajes.

## 1. Dos motores separados: PhysX (3D) y Box2D (2D)

- 3D: integración de **Nvidia PhysX** (docs oficiales: "Unity's default built-in 3D physics system is an integration of the Nvidia PhysX engine").
- 2D: motor propio basado en **Box2D** (los docs de Unity 6 ya no nombran el motor; la base Box2D está confirmada por fuentes externas e históricas).
- Son **simulaciones independientes**: un `Collider` (3D) jamás detecta un `Collider2D`, un `Rigidbody` no interactúa con un `Rigidbody2D`, y `Physics.Raycast` no ve colliders 2D (ni viceversa con `Physics2D`).

| Concepto | 3D (PhysX) | 2D (Box2D) |
|---|---|---|
| Cuerpo | `Rigidbody` | `Rigidbody2D` |
| Colliders | `BoxCollider`, `SphereCollider`, `CapsuleCollider`, `MeshCollider`, `WheelCollider`, `TerrainCollider` | `BoxCollider2D`, `CircleCollider2D`, `CapsuleCollider2D`, `PolygonCollider2D`, `EdgeCollider2D`, `CompositeCollider2D`, `TilemapCollider2D` |
| Queries | `Physics.Raycast/SphereCast/BoxCast/Overlap*` | `Physics2D.Raycast/CircleCast/BoxCast/Overlap*` |
| Mensajes | `OnCollisionEnter(Collision)`, `OnTriggerEnter(Collider)` | `OnCollisionEnter2D(Collision2D)`, `OnTriggerEnter2D(Collider2D)` |
| Material | `PhysicsMaterial` | `PhysicsMaterial2D` |
| Settings | Project Settings ▸ Physics | Project Settings ▸ Physics 2D |
| Gravedad | `Vector3` global (default estándar 0,-9.81,0) | `Vector2` global + `gravityScale` por cuerpo |

Regla: elige UN motor por mecánica. Un juego 2D con sprites usa SIEMPRE los componentes `*2D`. Mezclarlos = colisiones que "no funcionan" sin error alguno.

## 2. Rigidbody: tipos de cuerpo

Clasificación que usa el motor (idéntica en concepto para 2D y 3D):

| Tipo | Cómo se define | Le afectan fuerzas/gravedad | Cómo se mueve | Costo |
|---|---|---|---|---|
| **Static** | 3D: collider SIN Rigidbody. 2D: `bodyType = Static` (o collider sin Rigidbody2D) | No | No debe moverse en runtime | Mínimo |
| **Kinematic** | Rigidbody con `isKinematic = true` (3D) / `bodyType = Kinematic` (2D) | No | Por script: `MovePosition`/`MoveRotation`/velocity | Bajo |
| **Dynamic** | Rigidbody normal (3D) / `bodyType = Dynamic` (2D) | Sí | Fuerzas, impulsos, velocity; el motor resuelve colisiones | El más caro |

Propiedades clave (nombres Unity 6 — renombradas en 6.0):

- `linearVelocity` (antes `velocity`), `linearDamping` (antes `drag`), `angularDamping` (antes `angularDrag`). Aplica a `Rigidbody` y `Rigidbody2D`; los nombres viejos siguen compilando como obsoletos.
- **Mass**: en kg (default 1). La masa NO cambia la velocidad de caída (docs explícitos); afecta cómo responde a fuerzas y a choques entre cuerpos. Mantén ratios de masa entre cuerpos que interactúan por debajo de ~10:1 para estabilidad del solver (práctica estándar; ratios extremos = solver inestable).
- **Linear/Angular Damping**: resistencia al movimiento/rotación. Default Angular Damping 3D: 0.05.
- **Use Gravity** (3D) / **Gravity Scale** (2D, multiplicador por cuerpo — para plataformas 2D es normal subirlo a 2–5 para saltos "de juego", no realistas [ver: gamedev/game-feel]).
- **Constraints**: Freeze Position/Rotation por eje. Personaje dinámico → congela SIEMPRE la rotación (X,Y,Z en 3D; Z en 2D solo si quieres que ruede… normalmente congelada).
- **Collision Detection**: `Discrete` (default) | `Continuous` | `ContinuousDynamic` | `ContinuousSpeculative` (3D); `Discrete`/`Continuous` (2D). Balas/objetos rápidos → algún modo Continuous, o se "teletransportan" a través de paredes (tunneling).
- **Interpolate**: `None` (default) | `Interpolate` | `Extrapolate` — ver §6.
- **Sleeping**: los cuerpos quietos se duermen y dejan de simular. 2D expone `Sleeping Mode` (Never Sleep / Start Awake / Start Asleep). Never Sleep = caro, evitar salvo necesidad.
- 2D extra: `Simulated` (apaga TODO el cuerpo en el motor, más barato que desactivar el GameObject), `Use Auto Mass` (masa desde el área del collider), `Layer Overrides` (Include/Exclude Layers por cuerpo).

Kinematic en detalle:

- Se mueve con `rb.MovePosition(pos)` / `rb.MoveRotation(rot)` **desde FixedUpdate**: el motor interpola el barrido y (con Interpolate activo) el render queda suave. Para teleport usa `rb.position = pos` (docs: MovePosition es para movimiento, no teleport).
- Empuja cuerpos Dynamic pero nada lo empuja a él.
- **2D**: un Kinematic solo genera contactos contra Dynamic; contra Static u otros Kinematic NO — salvo `useFullKinematicContacts = true`, que habilita los callbacks (sin respuesta física: los colliders se solapan; útil para character controllers 2D custom).
- `linearVelocity` en un kinematic 2D funciona (mueve el cuerpo); en 3D no se puede setear velocity a un kinematic.

## 3. Colliders y triggers: qué dispara qué

- Colliders primitivos (Box/Sphere/Capsule) = baratos y estables. **Compound collider**: varios primitivos en hijos bajo UN Rigidbody en el padre — la opción correcta para formas complejas que se mueven.
- `MeshCollider`: no-convexo solo sirve para geometría estática; dos MeshColliders no-convexos NO colisionan entre sí. `Convex = true` lo limita a **255 triángulos** y entonces sí puede usarse en cuerpos dinámicos y chocar con otros mesh colliders. Docs: para objetos que se mueven, primitivos > mesh.
- **Is Trigger**: el collider deja de bloquear físicamente y pasa a reportar entradas/salidas.

Mensajes (3D; en 2D son los mismos con sufijo `2D`):

- `OnCollisionEnter/Stay/Exit(Collision col)` — con puntos de contacto (`col.contacts`, `col.impulse`).
- `OnTriggerEnter/Stay/Exit(Collider other)` — sin contactos.
- Llegan al script en el GameObject del collider Y al del Rigidbody padre (compound). Se ejecutan dentro del paso de física (ver §6).

**Matriz de colisión (docs oficiales, Unity 6):**

| Par | ¿OnCollision? | ¿OnTrigger? |
|---|---|---|
| Dynamic + Static | Sí | — |
| Dynamic + Dynamic | Sí | — |
| Dynamic + Kinematic | Sí* | — |
| Kinematic + Kinematic | No (3D)** | — |
| Static + Static | No | No |
| Trigger (Dynamic o Kinematic) + cualquier collider | No | Sí |
| Trigger Static + Dynamic o Kinematic | No | Sí |
| Trigger Static + Static (no-trigger o trigger) | No | No |

\* Colisión detectada y mensaje enviado; la respuesta física solo mueve al Dynamic.
\** En 2D, Kinematic+Kinematic y Kinematic+Static requieren `useFullKinematicContacts`.

Reglas derivadas (memorizar):
1. Sin al menos un Rigidbody en el par, NO hay mensajes de nada (dos colliders estáticos son invisibles entre sí).
2. Un trigger necesita que al menos uno del par tenga Rigidbody. Pickup estático + jugador con Rigidbody = OK. Pickup estático + jugador solo-CharacterController = OK también (el CharacterController cuenta para triggers).
3. Un collider trigger jamás genera `OnCollision*`.

## 4. Layers y collision matrix

Configuración: **Edit ▸ Project Settings ▸ Physics (y Physics 2D) ▸ Layer Collision Matrix** — checkbox por par de layers; desmarcado = ese par ni colisiona ni se reporta. Es LA herramienta para recortar trabajo del motor y evitar lógica de filtrado en código.

Organización típica que funciona para la mayoría de juegos:

| Layer | Contenido | Desactivar contra |
|---|---|---|
| `Ground` | Suelo, paredes, geometría estática | — (colisiona con todo) |
| `Player` | Cuerpo del jugador | `PlayerProjectile` |
| `Enemy` | Enemigos | `Enemy` (si no deben empujarse), `EnemyProjectile` |
| `PlayerProjectile` | Balas del jugador | `Player`, `PlayerProjectile` |
| `EnemyProjectile` | Balas enemigas | `Enemy`, `EnemyProjectile` |
| `Pickup` | Triggers de items | Todo menos `Player` |
| `Debris` | Ragdolls, escombros, FX físicos | `Player`, `Enemy`, `Debris`, proyectiles |
| `Sensor` | Triggers de detección IA/zonas | Todo menos lo que detectan |

- En código: `Physics.IgnoreLayerCollision(l1, l2)`, `Physics.IgnoreCollision(colA, colB)` para pares puntuales.
- Unity 6 además trae **Layer Overrides** por Rigidbody/Collider (Include/Exclude Layers) para excepciones sin gastar layers.
- LayerMask en queries: `LayerMask.GetMask("Ground", "Enemy")` o campo serializado `public LayerMask groundMask;` (preferido: editable en Inspector). Un raycast sin máscara golpea TODO, incluido el propio collider del que dispara.

## 5. Queries: Raycast, Overlap, Cast

Cheat sheet 3D (`Physics.*`):

| Necesitas | API |
|---|---|
| Primer impacto en una línea | `Physics.Raycast(origin, dir, out RaycastHit hit, dist, mask)` |
| Todos los impactos, sin GC | `Physics.RaycastNonAlloc(ray, buffer, dist, mask)` → devuelve count; **resultados SIN ordenar** (docs) |
| ¿Qué hay en una esfera? | `Physics.OverlapSphereNonAlloc(center, radius, buffer, mask)` |
| Volumen que avanza (ataque ancho, ground check) | `Physics.SphereCast` / `Physics.BoxCast` (+ variantes NonAlloc) |
| ¿El collider X toca algo? | `Physics.ComputePenetration`, `Collider.ClosestPoint` |

- Variantes `NonAlloc`: escriben en un buffer pre-alocado, devuelven `int` count, cero garbage. Si el buffer se llena, se trunca sin aviso y sin garantía de que estén los más cercanos — dimensiona el buffer al peor caso razonable (8–32 típico). Siguen soportadas en Unity 6 (docs 6000.x las listan como Supported).
- **2D**: en Unity 6 las variantes `NonAlloc` de `Physics2D` ya no aparecen en los docs (obsoletas); el patrón actual es sobrecargas con `ContactFilter2D` + `RaycastHit2D[]`/`List<RaycastHit2D>`: `Physics2D.Raycast(origin, dir, filter, results, dist)`. A diferencia de 3D, los resultados 2D **SÍ vienen ordenados** por distancia ascendente (docs).
- Todo query acepta `layerMask` y (3D) `QueryTriggerInteraction`. Ojo: **Queries Hit Triggers está activado por default** en Project Settings — tus raycasts golpean triggers salvo que pases `QueryTriggerInteraction.Ignore`.
- **Auto Sync Transforms está desactivado por default**: si mueves un Transform y lanzas un raycast en el mismo frame antes del paso de física, el query ve la posición VIEJA del collider. Fix puntual: `Physics.SyncTransforms()` antes del query (no reactivar autoSync global: es caro).

```csharp
// Patrón NonAlloc reutilizable (3D)
static readonly Collider[] _hits = new Collider[16];

int count = Physics.OverlapSphereNonAlloc(transform.position, 3f, _hits, enemyMask,
                                          QueryTriggerInteraction.Ignore);
for (int i = 0; i < count; i++)
{
    if (_hits[i].TryGetComponent(out Enemy e)) e.Alert();
}
// No usar _hits.Length; solo los primeros `count` son válidos este frame.
```

## 6. FixedUpdate vs Update, interpolación y jitter

Modelo mental (docs de execution order):

- La física corre a **timestep fijo**: `Time.fixedDeltaTime`, default **0.02 s = 50 Hz** (Project Settings ▸ Time). El render corre a FPS variable.
- Por cada frame de render, Unity ejecuta **0, 1 o N** ciclos `FixedUpdate → simulación física → OnTrigger*/OnCollision* → WaitForFixedUpdate` hasta ponerse al día; a 144 fps hay frames SIN paso de física, a 30 fps hay frames con 2.
- **Maximum Allowed Timestep** capa cuánto intenta recuperarse en frames lentos (evita la espiral de la muerte: física lenta → más pasos → más lento). Default en proyectos nuevos: 0.3333 s (NO VERIFICADO en docs actuales — confírmalo en Project Settings ▸ Time).
- Dentro de `FixedUpdate`, usa `Time.deltaTime` con normalidad: Unity devuelve ahí el fixedDeltaTime.
- Unity 6, Project Settings ▸ Physics ▸ **Simulation Mode**: `FixedUpdate` (default) | `Update` | `Script` (tú llamas `Physics.Simulate()` — para replays/rollback/determinismo por pasos).

**Por qué el jitter** (análisis clásico de KinematicSoup, vigente): mover unas cosas en `Update` y otras en `FixedUpdate` = frecuencias distintas = tartamudeo relativo, típicamente "el mundo tiembla cuando la cámara sigue al player físico". Antídotos:

1. Fuerzas/velocidad SIEMPRE en `FixedUpdate`; lectura de input en `Update` (cachear en un campo; para botones usar acumulación: `jumpPressed |= jump.WasPressedThisFrame()` y limpiar tras consumirlo en FixedUpdate) [ver: input-system].
2. **Interpolate** en el Rigidbody que la cámara sigue (player, vehículo). `Interpolate` = suaviza entre los DOS últimos pasos de física (un pelín de retraso, exacto); `Extrapolate` = predice (sin retraso, puede penetrar visualmente). Regla: Interpolate para el player; None para el resto (tiene costo por cuerpo).
3. Cámara que sigue al player físico → en `LateUpdate` (o Cinemachine), leyendo la posición ya interpolada del Transform.
4. No cambies `Time.timeScale` sin saber que la física escala con él (slow-motion físico "gratis"; con `timeScale = 0` no hay pasos de física).

## 7. Character controllers: las 3 vías

| Vía | Qué es | Pros | Contras | Úsala cuando |
|---|---|---|---|---|
| **`CharacterController`** | Componente cápsula con motor de movimiento propio (sin Rigidbody dinámico) | Cero setup, `Move()` con colisión y slide, `isGrounded`, slope/step integrados, control "Doom-style" instantáneo | Solo cápsula, NO recibe fuerzas ni empujones, no usa gravedad solo (la aplicas tú), no rota el collider | FPS/tercera persona estándar, prototipos, NPCs simples |
| **Rigidbody dinámico custom** | `Rigidbody` + colliders, control por `linearVelocity`/`AddForce` en FixedUpdate | Interactúa de verdad con la física (empuja, lo empujan, plataformas móviles, explosiones) | Ground check, slopes, steps y "no resbalar" los implementas tú; tuning fino | Juegos physics-driven, plataformas con knockback, 2D con `Rigidbody2D` |
| **Rigidbody kinematic custom** | Kinematic + casts manuales (SphereCast/`useFullKinematicContacts` en 2D) para mover y resolver | Control total y determinista, sin sorpresas del solver | La vía más cara en código: colisión, depenetración y slopes 100% a mano | Plataformas de precisión, réplicas de feel clásico, netcode con rollback |

- Paquetes: **Kinematic Character Controller** (Asset Store, gratuito, estándar de facto para la vía kinemática 3D) y el paquete **Character Controller de Unity para ECS/DOTS** existen; evalúa antes de escribir uno desde cero. (Estado/versionado actual de ambos: NO VERIFICADO en esta pasada.)
- `CharacterController` — valores de docs: **Skin Width ≈ 10% del Radius** (nunca 0; personaje atascado → sube Skin Width), **Step Offset 0.1–0.4** para humanoide de 2 m, **Min Move Distance 0**. `Move()` NO aplica gravedad (docs explícitos) y devuelve `CollisionFlags`; `SimpleMove()` sí aplica gravedad e ignora el eje Y (variante limitada, casi nunca la que quieres). Interacción con física: solo vía `OnControllerColliderHit` empujando tú a los Rigidbodies.

```csharp
// CharacterController: gravedad + salto (patrón de los docs)
CharacterController cc; Vector3 vel; float speed = 6f, jumpH = 1.2f, g = -19.6f;

void Update()
{
    if (cc.isGrounded && vel.y < 0) vel.y = -2f;          // pegado al suelo
    Vector3 move = new Vector3(input.x, 0, input.y);
    if (jumpPressed && cc.isGrounded) vel.y = Mathf.Sqrt(jumpH * -2f * g);
    vel.y += g * Time.deltaTime;
    cc.Move((transform.TransformDirection(move) * speed + vel) * Time.deltaTime);
}
```

```csharp
// Rigidbody dinámico: control por velocidad (patrón Catlike Coding)
Rigidbody rb; Vector2 input; float maxSpeed = 8f, maxAccel = 40f;

void Update() => input = moveAction.ReadValue<Vector2>();   // input en Update

void FixedUpdate()                                          // física en FixedUpdate
{
    Vector3 v = rb.linearVelocity;
    Vector3 target = new Vector3(input.x, 0, input.y) * maxSpeed;
    float dv = maxAccel * Time.deltaTime;                   // aceleración limitada
    v.x = Mathf.MoveTowards(v.x, target.x, dv);
    v.z = Mathf.MoveTowards(v.z, target.z, dv);
    rb.linearVelocity = v;                                  // y NO tocar v.y: la lleva la gravedad
}
```

- Ground check para la vía Rigidbody: `OnCollisionStay` + normales de contacto (`normal.y >= Mathf.Cos(maxGroundAngle)`) — más robusto que un raycast único; en slopes proyecta la velocidad sobre el plano de contacto (`Vector3.ProjectOnPlane`) para no despegar (Catlike Coding). Congela la rotación del Rigidbody y usa fricción 0 en el material del personaje (la fricción del solver contra paredes causa "pegarse").

## 8. AddForce vs velocity (criterio)

`ForceMode` (docs Unity 6): `Force` (continua, respeta masa) · `Acceleration` (continua, ignora masa) · `Impulse` (instantánea, respeta masa) · `VelocityChange` (instantánea, ignora masa).

- **Setear `linearVelocity`**: control directo y predecible → movimiento de personaje, dashes, feel arcade. Los docs avisan: no re-setees la velocidad completa cada paso "porque sí" en objetos que deben simular de forma realista — pisas al solver (gravedad, choques).
- **`AddForce(f, ForceMode.Force)`** cada FixedUpdate: aceleración física real → vehículos, objetos empujados, viento.
- **`AddForce(f, ForceMode.Impulse)`** una vez: salto físico, knockback, explosión (`AddExplosionForce`).
- Híbrido común y legítimo: velocity horizontal seteada + eje Y intacto para gravedad/salto por Impulse.
- 2D: `Rigidbody2D.AddForce` con `ForceMode2D.Force/Impulse` (no hay Acceleration/VelocityChange en 2D).

## 9. Reglas prácticas

1. Juego 2D → componentes `*2D` en TODO; jamás mezclar los dos motores en una misma mecánica.
2. Todo lo que se mueve y colisiona lleva Rigidbody (aunque sea Kinematic). Mover un collider sin Rigidbody = re-inserción de collider estático, caro y sin barrido.
3. Fuerzas, velocity, `MovePosition` → solo en `FixedUpdate`. Input → `Update`, cacheado (botones acumulados hasta consumirse).
4. Nunca mover con `transform.position` un objeto con Rigidbody dinámico (los docs 2D lo prohíben explícito). Teleport puntual: `rb.position = x` (+ resetear `linearVelocity`).
5. Personaje dinámico: Freeze Rotation siempre; fricción 0 en su material físico; masa ~1–10.
6. Escala (1,1,1) en todo lo que tenga física; nada de escala no uniforme ni negativa en jerarquías con colliders.
7. Objetos rápidos (balas físicas, proyectiles): Collision Detection Continuous/ContinuousDynamic, o mejor: raycast por frame en vez de collider (hitscan).
8. Colliders de formas complejas móviles = compound de primitivos bajo un solo Rigidbody, no MeshCollider.
9. Layer Collision Matrix configurada ANTES de escribir filtros en código; proyectiles nunca en la layer de su dueño.
10. Raycasts siempre con `LayerMask` explícita; decidir triggers con `QueryTriggerInteraction` (por default los golpea).
11. Queries repetidos por frame → variantes NonAlloc (3D) / `ContactFilter2D` + buffer (2D); buffer estático dimensionado al peor caso; iterar solo `count` [ver: rendimiento-unity].
12. `Interpolate` en el Rigidbody que sigue la cámara; cámara en `LateUpdate`/Cinemachine.
13. `isGrounded`/ground-check: en CharacterController úsalo justo tras `Move()`; en Rigidbody usa normales de contacto, no un solo raycast al centro.
14. Trigger que no dispara → checklist: ¿alguno del par tiene Rigidbody? ¿layers se ven en la matrix? ¿Is Trigger marcado? ¿el script está en el GameObject del collider o del Rigidbody?
15. No subas Solver Iterations / bajes Fixed Timestep globalmente para arreglar UN objeto: arregla masas, tamaños y CCD de ese objeto.
16. `OnCollisionStay` deja de llegar cuando el cuerpo se duerme — no cuelgues lógica persistente de él sin contemplar sleep.
17. Cambios masivos de Transform + queries en el mismo frame → `Physics.SyncTransforms()` antes del query.
18. Depurar colisiones: Physics Debugger (Window ▸ Analysis ▸ Physics Debugger) y `Debug.DrawRay`; en 2D, gizmos de colliders en Scene view.

## 10. Errores comunes

| Error | Síntoma | Antídoto |
|---|---|---|
| Mover `transform` de un cuerpo dinámico | Colisiones que se saltan, jitter, física "borracha" | `linearVelocity`/`AddForce`; kinematic → `MovePosition` en FixedUpdate |
| Física en `Update` | Movimiento depende del framerate; saltos de altura variable | Migrar a `FixedUpdate`; input cacheado en `Update` |
| Cámara en `Update` siguiendo Rigidbody sin Interpolate | Player o mundo tiemblan | Interpolate en el Rigidbody + cámara en `LateUpdate` |
| Escala no uniforme / negativa con colliders | Collider no coincide con el visual, contactos raros, costo de re-cooking | Escala (1,1,1); ajustar tamaño en el import o en el collider (`size`/`radius`), no en el Transform |
| Dos colliders estáticos esperando `OnCollision`/`OnTrigger` | No llega ningún mensaje | Al menos un Rigidbody en el par (kinematic vale) |
| Kinematic 2D que "no choca" con paredes estáticas | Atraviesa todo menos cuerpos dinámicos | `useFullKinematicContacts = true` + resolver tú, o vía Dynamic con rotación congelada |
| Bala dinámica a 60 m/s con Discrete | Atraviesa paredes (tunneling) | CCD Continuous(Dynamic) o hitscan por raycast |
| `AddForce(..., Impulse)` cada FixedUpdate | Aceleración explosiva incontrolable | Impulse = una vez; continua = `Force` |
| Setear velocity completa cada paso en objetos "realistas" | Gravedad y choques no afectan; empujones imposibles | Setear solo los ejes controlados; dejar Y al solver |
| Raycast golpea al propio jugador o a triggers | Ground check siempre true; disparos que chocan "con nada" | LayerMask correcta + `QueryTriggerInteraction.Ignore` |
| Buffer NonAlloc pequeño o iterado entero | Enemigos que "no detecta"; referencias viejas del frame anterior | Dimensionar al peor caso; usar solo índices `< count` |
| MeshCollider no-convexo en objeto dinámico | No colisiona entre mallas / comportamiento inválido | Convex (≤255 tris) o compound de primitivos |
| `CharacterController` esperando gravedad/empujones | Flota; las explosiones no le hacen nada | Gravedad manual en `Move()`; knockback manual; o cambiar a vía Rigidbody |
| Subir Fixed Timestep a 0.01 "para suavidad" | CPU de física x2 en todo el juego | Interpolate + cámara bien puesta; el timestep se toca con perfiler en mano |
| Trigger de pickup en la layer equivocada | El pickup dispara con balas y enemigos | Layer `Pickup` que solo ve `Player` en la matrix |
| Lógica en `OnCollisionStay` con cuerpos que se duermen | La lógica "se apaga" a los segundos | Guardar estado en Enter/Exit o Sleeping Mode adecuado |

[ver: arquitectura-unity] para dónde vive esta lógica (componentes, ciclo de vida), [ver: input-system] para el cacheo de input, [ver: rendimiento-unity] para perfilar física, [ver: gotchas-unity] para trampas generales del editor, [ver: gamedev/game-feel] para tuning de gravedad/salto/knockback.

## Fuentes

- Rigidbody component reference — Unity Manual (docs.unity3d.com, Unity 6) — nombres actuales (Linear/Angular Damping), Interpolate, modos CCD, masa en kg.
- Rigidbody.linearVelocity / Rigidbody2D.linearVelocity / ForceMode — Unity Scripting API (Unity 6000.x) — renames de Unity 6 y semántica exacta de los ForceMode.
- Introduction to colliders + Interaction between collider types — Unity Manual — definición static/kinematic/dynamic y la matriz completa de OnCollision/OnTrigger.
- Rigidbody 2D body types (Dynamic/Kinematic/Static, fundamentals y reference) — Unity Manual (Unity 6) — propiedades exactas 2D, prohibición de mover Transform, colisiones de kinematic.
- Rigidbody2D.useFullKinematicContacts — Unity Scripting API — contactos kinematic-kinematic/static sin respuesta física.
- Layer-based collision detection — Unity Manual — Layer Collision Matrix y ruta de configuración.
- Physics.RaycastNonAlloc / Physics.OverlapSphereNonAlloc / Physics2D.Raycast — Unity Scripting API (Unity 6000.x) — semántica de buffers, orden de resultados (3D sin ordenar, 2D ordenado), estado NonAlloc en 2D.
- Physics project settings — Unity Manual — defaults: Queries Hit Triggers ON, Auto Sync Transforms OFF, Default Contact Offset 0.01, Simulation Mode.
- Physics.autoSyncTransforms — Unity Scripting API — queries ven posiciones viejas hasta el sync; `Physics.SyncTransforms`.
- Event execution order + Fixed updates — Unity Manual — ciclo FixedUpdate→simulación→callbacks→WaitForFixedUpdate, 0..N pasos por frame, timestep 0.02.
- Character Controller component + CharacterController.Move — Unity Manual/API — valores recomendados (Skin Width 10%, Step Offset 0.1–0.4), Move sin gravedad, CollisionFlags, limitaciones.
- Mesh colliders — Unity Manual — convex ≤255 triángulos, no-convexo no colisiona entre sí, cooking.
- Catlike Coding — "Movement: Physics" (catlikecoding.com, Jasper Flick) — patrón velocity+MoveTowards en FixedUpdate, ground por normales de contacto, ProjectOnPlane.
- KinematicSoup — "Timesteps and Achieving Smooth Motion in Unity" — diagnóstico canónico del jitter Update/FixedUpdate y arquitectura input-en-Update/física-en-FixedUpdate.
- Box2D — Wikipedia — confirmación de que el motor 2D de Unity está construido sobre Box2D (los docs actuales de Unity ya no lo nombran).
