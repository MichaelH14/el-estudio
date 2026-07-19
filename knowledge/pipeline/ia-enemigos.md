# IA de enemigos y pathfinding en Unity

> **Cuando cargar este archivo:** al implementar cualquier enemigo o NPC que percibe, decide, se mueve o ataca — pathfinding (NavMesh 3D o grid 2D), FSM/behavior trees, percepción, spawners/oleadas o pacing tipo AI Director. Unity 6.x/URP.

Archivo puente: el QUÉ/POR QUÉ de diseño está en `gamedev/` y los patrones C#/física en `unity/`; aquí está la unión concreta. Estado de paquetes verificado a julio 2026.

## 1. Decisión inicial: qué stack según el juego

| Juego | Pathfinding | Cerebro | Movimiento |
|---|---|---|---|
| 3D con suelo navegable (shooter, action, TD 3D) | NavMesh (paquete AI Navigation) | FSM de clases-estado | `NavMeshAgent` |
| 2D top-down / tilemap | A* Pathfinding Project (de facto) o NavMeshPlus o A* casero | FSM | `Rigidbody2D` + velocity [ver: unity/fisica-unity] |
| Plataformas 2D (side-view) | Normalmente NINGUNO: patrones fijos + steering | Enum+switch o FSM | `Rigidbody2D` |
| Enjambre masivo (100+ unidades) | Un path compartido o flow hacia el jugador + separación local | FSM mínima + ticks espaciados (§9) | velocity directa |
| Enemigo de arena sin obstáculos | Ninguno: seek/steering directo (§5) | Enum+switch | velocity directa |

Regla: el pathfinding es caro de montar y mantener — confírmalo necesario. Un enemigo que camina hacia el jugador en línea recta con separación cubre a la mitad de los juegos de acción 2D.

## 2. El cerebro: FSM → behavior tree → utility

**FSM con clases-estado es el default** — la escalera enum→clases→SO y el `StateMachine` base ya están en [ver: unity/csharp-patrones] §5; no lo dupliques, extiéndelo. Estados canónicos de un enemigo: `Patrol → Suspicious → Combat → Search → Return`. La FSM de gameplay manda y el Animator solo refleja (`SetBool` desde `Enter()`) — regla de csharp-patrones.

```csharp
// Estado de persecución sobre la base State de [ver: unity/csharp-patrones §5]
public class ChaseState : State
{
    readonly NavMeshAgent agent; readonly Enemy enemy;   // inyectados por constructor
    float repathTimer;
    public override void Enter() { agent.isStopped = false; repathTimer = 0f; }
    public override void Tick()
    {
        repathTimer -= Time.deltaTime;
        if (repathTimer <= 0f)                            // repath por intervalo, NUNCA cada frame
        {
            agent.SetDestination(enemy.Target.position);
            repathTimer = 0.25f;
        }
        if (!agent.pathPending && agent.remainingDistance <= agent.stoppingDistance)
            enemy.Fsm.ChangeState(enemy.Attack);
        else if (!enemy.Perception.CanSee(enemy.Target))
            enemy.Fsm.ChangeState(enemy.Search);          // a última posición conocida (§6)
    }
}
```

**Behavior trees — concepto y cuándo:** árbol de nodos compuestos (`Sequence` = AND en orden, `Selector` = primer hijo que funcione, decoradores = condiciones/repetición) evaluado desde la raíz cada tick; las hojas son acciones/condiciones. Ventaja sobre FSM: las transiciones no son N² (cada estado no necesita conocer a los demás); la prioridad la da la estructura del árbol. Referencia canónica: "The Behavior Tree Starter Kit" (Champandard & Dunstan, Game AI Pro, capítulo gratis en gameaipro.com). Cuándo saltar de FSM a BT: cuando pasas de ~6-8 estados y las transiciones cruzadas se vuelven spaghetti, o cuando un diseñador debe editar comportamiento sin código.

- **Unity Behavior (`com.unity.behavior`, gratis, 1.0.16 a mayo 2026):** el paquete oficial. Editor visual de "behavior graphs" (variante de BT donde las ramas pueden converger), Blackboard de variables compartidas, componente agente que ejecuta el grafo en el GameObject. Es la opción por defecto para BT en Unity 6 antes de comprar un asset. Versión mínima de Unity requerida: NO VERIFICADO en esta pasada — confirmar en Package Manager.
- Assets de pago veteranos (Behavior Designer, NodeCanvas) existen; evalúalos solo si Unity Behavior se queda corto. Estado actual de esos assets: NO VERIFICADO.

**Utility AI — a nivel mención:** cada acción posible se puntúa con funciones sobre el contexto (distancia, HP, munición) y se ejecuta la de mayor score; elimina transiciones explícitas por completo. Brilla en NPCs con muchas acciones contextuales (Sims, RPG companions; Dragon Age Inquisition lo usó — "Behavior Decision System", Game AI Pro 3). Para el enemigo típico de acción es sobreingeniería: FSM o BT primero. Intro: "An Introduction to Utility Theory" (Graham) y "Dual-Utility Reasoning" (Dill), Game AI Pro.

## 3. NavMesh 3D: el paquete AI Navigation

En Unity 6 la navegación vive en el paquete **`com.unity.ai.navigation`** (docs consultadas: 2.0.14) con componentes; el flujo viejo de bake por escena quedó atrás (la doc trae guía de upgrade). Componentes:

| Componente | Qué hace |
|---|---|
| `NavMeshSurface` | Define y bakea el NavMesh para UN agent type. Varios surfaces por escena posibles |
| `NavMeshAgent` | El personaje que navega (path + steering + avoidance integrados) |
| `NavMeshObstacle` | Obstáculo móvil que los agentes evitan; puede recortar el mesh (carve) |
| `NavMeshLink` | Conecta surfaces desconectados (saltos, drops). `OffMeshLink` está DEPRECADO |
| `NavMeshModifier` | Ajusta cómo un GameObject participa en el bake (área, exclusión) |
| `NavMeshModifierVolume` | Marca un volumen con un área (agua = cara, peligro = evitar) |

**Bake (`NavMeshSurface`):**
- `Agent Type` define radio/altura/slope del "molde" con que se talla el mesh — un surface por tipo (humanoide vs rata gigante).
- `Collect Objects`: All GameObjects (default) | Volume | Current Object Hierarchy | NavMeshModifier Component Only.
- `Use Geometry`: **Physics Colliders** suele ser mejor que Render Meshes — la doc indica que con colliders los agentes pueden acercarse más al borde físico real, y es coherente con colliders simples sobre visuales complejos [ver: unity/fisica-unity].
- El bake excluye automáticamente los GameObjects que tengan `NavMeshAgent` o `NavMeshObstacle` (doc oficial).
- Runtime: `BuildNavMesh()` (síncrono, rebake completo), `UpdateNavMesh(NavMeshData)` (incremental, devuelve `AsyncOperation`), `AddData()`/`RemoveData()`. Para niveles procedurales: generar geometría → `BuildNavMesh()` en la carga, no por frame.
- Áreas con costo (`Default Area` + modifiers: Walkable/Not Walkable/Jump + custom): el path elige por costo total, no solo distancia — carretera barata, pantano caro.

**`NavMeshAgent` — tuning (nombres exactos):**

| Propiedad | Qué controla | Receta |
|---|---|---|
| `speed` | Velocidad máx siguiendo el path | Igualar al diseño del encounter: perseguidor ~1.1x la velocidad del jugador se siente amenazante sin ser injusto (calibrar en playtest) [ver: gamedev/game-feel] |
| `acceleration` | unidades/s² | Baja = arranque pesado (tanque); alta = respuesta inmediata (insecto) |
| `angularSpeed` | Giro máx en deg/s | Bajo + `speed` alto = curvas amplias, se siente vehículo |
| `stoppingDistance` | Se detiene a esta distancia del destino | Melee: alcance del ataque − margen; NUNCA 0 en perseguidores (empujan/vibran contra el objetivo) |
| `autoBraking` | Frena al acercarse al destino | ON para chase; OFF para waypoints de patrulla (no frena en cada punto) |
| `obstacleAvoidanceType` | Calidad del avoidance entre agentes | Bajarla en masas (§9); la separación entre agentes YA la hace esto — no dupliques con steering |
| `updatePosition` / `updateRotation` | Sincronizar transform con la simulación | Ambos false = el agente solo calcula y tú mueves (root motion, físicas custom) |

- Chequeo de llegada correcto: `!agent.pathPending && agent.remainingDistance <= agent.stoppingDistance` (con `pathPending`, `remainingDistance` aún no es válido).
- Teleport: `agent.Warp(pos)`, jamás `transform.position` con el agente activo.
- Física: el agente mueve el transform con su propia simulación — NO lo combines con `Rigidbody` dinámico (dos sistemas moviendo lo mismo). Patrón estándar: Rigidbody **kinematic** en el enemigo para que triggers/hits funcionen (la matriz de mensajes exige Rigidbody [ver: unity/fisica-unity §3]) y el daño se detecta con queries/overlaps.
- `isStopped = true` para congelar sin perder el path (hit-stun, cutscene).

**`NavMeshObstacle`:** dos modos. Sin carve = los agentes lo esquivan con steering local (para obstáculos en movimiento). Con `Carve` = recorta un agujero real en el NavMesh y el pathfinding lo rodea (para bloqueos que duran: puerta cerrada, coche aparcado, muro invocado). `Carve Only Stationary` + `Time To Stationary` + `Move Threshold` controlan cuándo recalcular. Regla de la doc: objeto que se mueve constantemente → sin carve; objeto que bloquea rutas → carve (si no, los agentes se estrellan contra él intentando atravesarlo porque el path lo ignora).

**`NavMeshLink` (saltos, drops, ventanas):** `Width` (franja o punto), `Bidirectional`, costo por `Cost Override` o por área ("Jump" es el área de links autogenerados). Travesía manual para animar el salto:
1. `agent.autoTraverseOffMeshLink = false;`
2. En `Update`: si `agent.isOnOffMeshLink` → disparar animación/tween del salto [ver: unity/animacion-unity].
3. Al terminar: `agent.CompleteOffMeshLink()` y sigue el path. (APIs verificadas en ScriptReference 6000.0; conservan el nombre "OffMeshLink" aunque el componente nuevo sea NavMeshLink.)

**Validar posiciones contra el mesh:** `NavMesh.SamplePosition(pos, out NavMeshHit hit, maxDistance, NavMesh.AllAreas)` — punto navegable más cercano. La doc recomienda `maxDistance` ≈ 2x la altura del agente (grande = caro). Úsalo para spawns (§8), destinos de wander y clicks de move-to.

## 4. Pathfinding 2D

**Por qué NavMesh nativo NO es el default en 2D:** `NavMeshSurface` solo consume Render Meshes o Physics Colliders 3D — no lee sprites, tilemaps ni colliders 2D. Opciones reales:

| Opción | Qué es | Cuándo |
|---|---|---|
| **A* Pathfinding Project** (arongranberg.com) | El asset estándar de facto. Free + Pro (Pro añade generación automática de navmesh/recast y penalties por textura). Grafos: grid, navmesh/recast, point | Default para 2D top-down serio, y alternativa a NavMesh también en 3D |
| **NavMeshPlus** (github.com/h8man/NavMeshPlus) | Fork comunitario MIT (~2.3k stars) que extiende `NavMeshSurface` para colectar tiles, sprites y colliders 2D | Si quieres el workflow NavMesh oficial (agentes, obstacles) en 2D sin comprar nada |
| **A* casero en grid** | ~100 líneas sobre tu Tilemap | Grids chicos/turn-based, control total de costos, cero dependencias |

**A* Pathfinding Project en 2D (verificado en su doc oficial):**
- Grid Graph con el toggle **"2D"** (alinea el grafo al plano XY) + **"Use 2D Physics"** para detectar obstáculos con colliders 2D.
- Soporte integrado de **tilemaps** en grid y recast graphs.
- Scripts de movimiento: `AIPath` (desactivar su gravity en 2D o el agente "cae"), `AILerp` (interpola exacto por el path, estilo grid puro), `FollowerEntity`. Destino: se asigna por script o con el componente de destino del paquete.
- Avoidance local: `RVOSimulator` con `movementPlane = XY`.
- Gotcha documentado: los colliders 2D tienen volumen cero en Z — al hacer graph updates con bounds, expandir los bounds en Z.

**A* casero (cuando aplica):** la referencia canónica es Red Blob Games ("Introduction to A*"): frontier con priority queue, `f = g + h` (costo real desde el origen + heurística al objetivo), heurística Manhattan para 4 direcciones (nunca sobreestimar), reconstrucción por `came_from`. Con `h = 0` es Dijkstra (multi-objetivo); greedy (solo `h`) es rápido pero no óptimo. Lección de Red Blob que importa más que el algoritmo: **el diseño del grafo pesa más que el algoritmo** — menos nodos (grid grueso, waypoints) rinde más que micro-optimizar el loop. Implementación Unity: grid desde `Tilemap.HasTile`/costos por tile, correr A* fuera del hot path (§9), cachear paths entre celdas repetidas, cero allocs por request (buffers reusados [ver: unity/csharp-patrones §8]).

## 5. Steering: debajo o en lugar del pathfinding

Vocabulario de Craig Reynolds ("Steering Behaviors for Autonomous Characters", 1999; red3d.com/cwr/steer):

| Behavior | Fórmula esencial | Uso típico |
|---|---|---|
| Seek / Flee | Velocidad deseada hacia/desde el objetivo − velocidad actual | Enemigo de arena, huir del jugador |
| Pursue / Evade | Seek/Flee hacia la posición FUTURA (posición + velocidad × t) | Proyectil guiado, interceptar |
| Wander | Objetivo aleatorio suavizado que deriva | Patrulla sin waypoints, idle vivo |
| Separation | Suma de repulsiones inversas a la distancia de vecinos | Enjambres: que no se apilen |
| Alignment + Cohesion | Igualar velocidad media / ir al centroide de vecinos | Flocking completo (boids) |
| Obstacle avoidance | Desvío lateral ante obstáculo proyectado | Esquivar props sin repath |

```csharp
// Separación para enjambre 2D (sin pathfinding): sumar a la velocity del Rigidbody2D
static readonly Collider2D[] _near = new Collider2D[16];
Vector2 Separation(ContactFilter2D enemyFilter, float radius)
{
    int n = Physics2D.OverlapCircle(transform.position, radius, enemyFilter, _near);
    Vector2 push = Vector2.zero;
    for (int i = 0; i < n; i++)
    {
        if (_near[i].attachedRigidbody == rb) continue;
        Vector2 away = (Vector2)transform.position - (Vector2)_near[i].transform.position;
        push += away / Mathf.Max(away.sqrMagnitude, 0.01f);   // más cerca = empuja más
    }
    return push;   // rb.linearVelocity = (seekDir * speed + push * peso) en FixedUpdate
}
```

- Con `NavMeshAgent` en 3D NO sumes separación manual: `obstacleAvoidanceType` ya separa agentes. El steering manual es para movimiento custom (2D, enjambres, voladores).
- El patrón de Left 4 Dead (deck de Booth, verificado): **reactive path following** — en vez de seguir el path nodo a nodo, avanzar hacia un punto "look ahead" más adelante del path + avoidance local para props/otros agentes. Barato de recomputar, movimiento fluido, y "se superpone bien con el flocking del mob". Riesgo documentado: el avoidance te puede sacar del path → repath. Es exactamente lo que A*PP/`NavMeshAgent` hacen por dentro; si escribes seguimiento de path a mano, copia este esquema.

## 6. Percepción: vista, oído y estados de alerta

**Cono de visión = 3 filtros baratos en orden** (distancia → ángulo → línea de vista):

```csharp
public bool CanSee(Transform target)
{
    Vector3 to = target.position - eye.position;
    if (to.sqrMagnitude > viewDistance * viewDistance) return false;      // 1. rango
    if (Vector3.Angle(eye.forward, to) > viewAngle * 0.5f) return false;  // 2. cono
    // 3. línea de vista: layers de occlusores + objetivo, sin triggers [ver: unity/fisica-unity §5]
    if (Physics.Raycast(eye.position, to.normalized, out var hit, viewDistance,
                        occluderMask | targetMask, QueryTriggerInteraction.Ignore))
        return ((1 << hit.collider.gameObject.layer) & targetMask) != 0;
    return false;
}
```

- `eye` = transform a altura de ojos, no el pivot en los pies (raycast desde el suelo choca con todo). En 2D: `Vector2.Angle` + `Physics2D.Raycast` con `ContactFilter2D`.
- **Oído:** no simules audio — un "ruido" es un evento con posición y radio. Emisor (disparo, pasos en sprint) publica en un canal de eventos ScriptableObject [ver: unity/csharp-patrones §1]; cada enemigo suscrito compara distancia vs su `hearingRange` y reacciona (girar, investigar). Barato y debuggeable.
- **Estados de alerta (receta estándar, la escalera de sigilo):** `Patrol` → ver al jugador NO dispara combate instantáneo: sube un medidor de sospecha (más rápido cuanto más cerca/centrado) → `Suspicious` (mirar, acercarse al punto) → medidor lleno = `Combat` → al perder visión, guardar **última posición conocida** y pasar a `Search` (ir allí + wander local unos segundos) → timeout sin re-contacto = `Return` a patrulla. El medidor visible para el jugador es fairness (§7). Para profundizar en sistemas de percepción shippeados: "Modeling Perception and Awareness in Tom Clancy's Splinter Cell Blacklist" (Walsh) y "Crytek's Target Tracks Perception System" (Welsh), Game AI Pro.
- La percepción es de lo más caro del enemigo (raycasts) → tick espaciado, no por frame (§9).

## 7. Telegraphing y fairness

La teoría vive en [ver: gamedev/animacion] (anatomía wind-up/strike/recovery) y [ver: gamedev/game-feel]; el balance dificultad-frustración en [ver: gamedev/fundamentos-diseno]. Lo operativo al implementar el enemigo:

- **Todo ataque tiene wind-up legible**: pose + flash/SFX ANTES de la ventana de daño. La ventana de daño se abre con animation event, no "cuando empieza la animación" [ver: unity/animacion-unity].
- **Proyectil esquivable por construcción**: tiempo de reacción = distancia de spawn / velocidad del proyectil. Si eso da < ~0.4 s en el rango típico de combate, el jugador no puede reaccionar — baja velocidad, sube distancia o añade aviso previo. Verifícalo con números, no a ojo.
- **Cooldowns visibles**: si el enemigo tiene un ataque fuerte con cooldown, muéstralo (postura de cansancio, brillo que recarga). Un patrón invisible se lee como random injusto — el jugador debe poder aprender el ritmo [ver: gamedev/mecanicas-sistemas §5 sobre percepción de azar].
- **Sin daño desde fuera de pantalla sin aviso**: ataque que origina off-screen → audio cue direccional o indicador de borde primero.
- **Presupuesto de agresión simultánea**: con N enemigos rodeando, limita cuántos atacan a la vez (los demás orbitan/posicionan). Sin esto, 5 melee = daño simultáneo ilegible. Implementación simple: contador global de "permisos de ataque" que los estados Attack piden en `Enter()` y devuelven en `Exit()`.
- El hit-feedback del lado del jugador (hit-stop, shake, sonido) es lo que hace justo el intercambio [ver: feel-en-unity].

## 8. Spawning, oleadas y el patrón AI Director

**Spawner base:**
- Pool SIEMPRE (`ObjectPool<T>`, reset en `actionOnGet`) — enemigos son el caso canónico [ver: unity/csharp-patrones §4]. Registro de vivos en un runtime set (mismo archivo, §1): el spawner, la UI y la condición de victoria leen la misma lista sin `Find*`.
- Posición de spawn: fuera de la vista de la cámara + `NavMesh.SamplePosition` (§3) para garantizar que el punto es navegable (en 2D: nodo walkable del grid). Spawn dentro de cámara = teleport visible = ilusión rota.
- **Composición por presupuesto de amenaza**: cada tipo de enemigo tiene un costo de amenaza; la oleada "compra" enemigos hasta agotar el presupuesto de la ronda (presupuesto crece por ronda). Para elegir QUÉ comprar, tabla de pesos — misma maquinaria que las loot tables [ver: gamedev/mecanicas-sistemas §5]: pesos, no porcentajes; sub-tablas por ronda; entradas condicionales ("desde ronda 5").
- Encounter design (dónde y con qué cobertura pelear) es problema de nivel: [ver: gamedev/level-design].

**AI Director (patrón, a nivel concepto — fuente: deck GDC de Michael Booth, "The AI Systems of Left 4 Dead", leído del PDF de Valve):**
- Mide una **intensidad emocional** por jugador (proxy numérico crudo): sube al recibir daño (proporcional), al quedar incapacitado, al ser empujado de una cornisa, y cuando un enemigo muere cerca (inverso a la distancia). Decae hacia cero con el tiempo, pero NO decae mientras hay enemigos atacándolo activamente.
- Ciclo de 4 estados sobre la intensidad máxima del equipo: **Build Up** (población completa de amenazas hasta cruzar el umbral de pico) → **Sustain Peak** (mantener 3–5 s) → **Peak Fade** (población mínima hasta que la intensidad sale del rango de pico — deja que el combate en curso termine solo) → **Relax** (población mínima 30–45 s o hasta que avancen lo suficiente, luego vuelta a Build Up).
- Claves de Booth: el director ajusta **frecuencia (pacing), no amplitud (dificultad)**; los bosses quedan FUERA del sistema (rompen el pacing a propósito); una estimación cruda de intensidad basta — el resultado se siente dramático igual ("simple algorithms can generate compelling pacing schedules"). También decide qué caches de items existen entre spots pre-colocados por el diseñador: procedural sobre opciones autorales, no libre.
- Mínimo viable en Unity: un manager con `float intensity` por jugador + enum de fase + el spawner de arriba leyendo "población completa/mínima" según fase. Dos tardes de trabajo, cambia el juego entero de sentir. El porqué del pacing en olas: [ver: gamedev/fundamentos-diseno] (flow y curvas).

## 9. Rendimiento: ticks e IA con LOD

El presupuesto de frame y la metodología de medición están en [ver: unity/rendimiento-unity]; lo específico de IA:

- **La decisión NO corre a framerate.** Percepción + FSM/BT tick a 5–10 Hz sobran para humanos; el movimiento (agente ya con destino, animación, steering) sí corre cada frame. Desfasar instancias para no pensar todas el mismo frame:

```csharp
float nextThink;
void Awake()  => nextThink = Time.time + Random.value * thinkInterval;  // desfase inicial
void Update()
{
    if (Time.time < nextThink) return;
    nextThink = Time.time + thinkInterval;    // 0.1–0.3 s típico
    perception.Scan();                        // raycasts aquí, no por frame
    fsm.Tick();
}
```

- **LOD de comportamiento** (concepto asentado — "Phenomenal AI Level-of-Detail Control with the LOD Trader", Sunshine-Hill, y "1000 NPCs at 60 FPS", Zubek, ambos en Game AI Pro): calidad de simulación según relevancia para el jugador. Receta de 3 niveles: **cerca/visible** = todo (percepción, avoidance, animación); **medio** = tick más lento, sin avoidance fino, animación simplificada; **lejos/no visible** = dormido o simulación estadística (posición extrapolada, "sigue patrullando" sin mover el transform). El criterio barato: distancia al jugador + `Renderer.isVisible`.
- Repath con presupuesto: `SetDestination` recalcula path — por intervalo y solo si el objetivo se movió más de X metros, jamás por frame (snippet §2).
- Con decenas de agentes NavMesh: `obstacleAvoidanceType` en calidad baja (o `None` para la masa y calidad solo en los cercanos).
- Cero allocs en el tick de IA: buffers NonAlloc para queries, sin LINQ, sin closures [ver: unity/csharp-patrones §8]. Un spike de GC con 50 enemigos pensando = stutter [ver: unity/gotchas-unity].
- Enjambres 2D masivos: separación con `OverlapCircle` + filtro por layer, radio corto, y tick de separación también espaciado (no todos los boids cada frame).

## Reglas prácticas

- [ ] Elige el stack con la tabla §1 ANTES de escribir el primer script: pathfinding solo si el nivel tiene obstáculos que rodear.
- [ ] FSM de clases-estado como default; BT (Unity Behavior) al pasar de ~6-8 estados con transiciones cruzadas; utility solo con justificación.
- [ ] La FSM manda, el Animator refleja; la ventana de daño la abre un animation event, no el tiempo.
- [ ] 3D: paquete AI Navigation — `NavMeshSurface` por agent type, `Use Geometry = Physics Colliders`, links con `NavMeshLink` (no el deprecado OffMeshLink).
- [ ] `stoppingDistance` > 0 en todo perseguidor; `autoBraking` OFF en patrullas por waypoints.
- [ ] Llegada = `!pathPending && remainingDistance <= stoppingDistance`; teleport = `Warp()`.
- [ ] NavMeshAgent + Rigidbody dinámico jamás juntos; Rigidbody kinematic para triggers/hits.
- [ ] Obstáculo que bloquea rutas de forma sostenida → `NavMeshObstacle` con Carve; en movimiento constante → sin carve.
- [ ] 2D: A* Pathfinding Project (grid 2D + Use 2D Physics) o NavMeshPlus; A* casero solo en grids chicos con la receta Red Blob (f = g + h, Manhattan en 4-dir).
- [ ] Steering manual (seek/separación) para movimiento custom y enjambres; con NavMeshAgent la separación ya la hace el avoidance.
- [ ] Percepción = distancia → ángulo → raycast, en ese orden, desde altura de ojos, con LayerMask y sin triggers.
- [ ] Sigilo/alerta: medidor de sospecha visible + última posición conocida + estado Search antes de rendirse.
- [ ] Todo ataque con wind-up legible; calcula el tiempo de reacción de cada proyectil (distancia/velocidad) y verifica que sea esquivable.
- [ ] Limita atacantes simultáneos con permisos de ataque cuando haya 3+ melee.
- [ ] Spawns: pool + runtime set + fuera de cámara + `NavMesh.SamplePosition` (maxDistance ≈ 2x altura del agente).
- [ ] Oleadas por presupuesto de amenaza con tablas de pesos, no listas hardcodeadas.
- [ ] Director de pacing: intensidad por jugador + ciclo Build Up/Sustain/Fade/Relax; ajusta frecuencia, no dificultad.
- [ ] IA piensa a 5–10 Hz con desfase aleatorio entre instancias; solo el movimiento corre por frame.
- [ ] LOD de comportamiento en cuanto haya 20+ enemigos: lejos/no visible = tick lento o dormido.
- [ ] Cero allocs en ticks de IA; perfila con la columna GC Alloc antes de dar por bueno el sistema.

## Errores comunes

| Error | Síntoma | Antídoto |
|---|---|---|
| `SetDestination` cada frame en N enemigos | Spikes de CPU al crecer la horda | Repath por intervalo (0.2–0.5 s) y solo si el objetivo se movió |
| `stoppingDistance = 0` en melee | Enemigos vibrando/empujando pegados al jugador | stoppingDistance = alcance del ataque − margen |
| Comprobar llegada solo con `remainingDistance` | "Llega" al instante de pedir el path | Guardar con `!pathPending` primero |
| Mover con `transform.position` un GameObject con NavMeshAgent | Agente "peleando" contra tu código, tirones | `Warp()` para teleport; destino para moverse; o `updatePosition = false` y mueves tú |
| NavMeshAgent + Rigidbody dinámico | Física borracha, doble movimiento | Rigidbody kinematic; daño por queries [ver: unity/fisica-unity] |
| Puerta/bloqueo como collider sin NavMeshObstacle | Agentes corriendo contra la puerta eternamente | NavMeshObstacle con Carve (el path la rodea) |
| Esperar NavMesh nativo en un juego 2D | Bake vacío o mesh inservible: no lee sprites/tilemaps/colliders 2D | A* Pathfinding Project, NavMeshPlus o A* casero (§4) |
| Raycast de visión desde el pivot (pies) | Enemigos "ciegos" tras cualquier borde bajo | Transform `eye` a altura de ojos + LayerMask correcta |
| Raycast de visión golpeando triggers propios | Detección fantasma intermitente | `QueryTriggerInteraction.Ignore` (Queries Hit Triggers está ON por default) |
| Percepción por frame en todos los enemigos | Coste de raycasts lineal con la horda, frame time serrucho | Tick de percepción a 5–10 Hz con desfase |
| Combate instantáneo al primer píxel de visión | Sigilo imposible, se siente injusto | Medidor de sospecha con rampa + estados Suspicious/Search |
| Ataques sin wind-up o con daño desde frame 0 | "Me pegó de la nada"; playtests frustrados | Wind-up + animation event para la ventana de daño [ver: gamedev/animacion] |
| Todos los enemigos atacan a la vez | Daño simultáneo ilegible e inevitable | Permisos de ataque limitados; el resto reposiciona |
| Director que sube DIFICULTAD cuando el jugador va mal | Espiral de muerte, frustración | Booth: modula frecuencia/pausas (pacing), no amplitud (daño/HP) |
| Instantiate/Destroy por oleada | GC spikes justo en los picos de acción | Pool + reset en `actionOnGet`; pre-calentar en carga |
| Enemigo pooled que revive con el estado viejo | Aparece atacando o con HP a medias | Reset completo de FSM/percepción/agent (`Warp` + estado inicial) al salir del pool |
| Balancear IA "a ojo" en el editor potente | En el móvil/build real la horda ahoga el frame | Perfilar en device real [ver: unity/rendimiento-unity]; LOD de comportamiento |

## Fuentes

- **AI Navigation package manual (com.unity.ai.navigation 2.0.14)** — docs.unity3d.com — componentes (NavMeshSurface/Link/Modifier/Obstacle), Collect Objects, Use Geometry, carve modes, deprecación de OffMeshLink; la autoridad del workflow Unity 6.
- **NavMeshSurface API (Unity.AI.Navigation)** — docs.unity3d.com Packages — `BuildNavMesh()`, `UpdateNavMesh()` async, `AddData`/`RemoveData` para bake en runtime.
- **NavMeshAgent + NavMesh.SamplePosition + autoTraverseOffMeshLink** — Unity ScriptReference 6000.0 — nombres y semántica exactos de speed/acceleration/stoppingDistance/autoBraking/obstacleAvoidanceType, Warp, travesía manual de links, SamplePosition con maxDistance ≈ 2x altura.
- **Unity Behavior manual + changelog (com.unity.behavior 1.0.16, 2026-05)** — docs.unity3d.com Packages — behavior graphs oficiales, Blackboard, gratuito.
- **A* Pathfinding Project** — arongranberg.com (sitio + doc "Pathfinding in 2D") — grafos grid/recast/point, free vs pro, toggle 2D + Use 2D Physics, tilemaps, AIPath/AILerp/FollowerEntity, RVOSimulator en XY.
- **NavMeshPlus** — github.com/h8man/NavMeshPlus — extensión comunitaria MIT del workflow NavMesh para 2D (tiles/sprites/colliders 2D).
- **"The AI Systems of Left 4 Dead"** — Michael Booth, Valve (deck GDC 2009, PDF oficial leído) — reactive path following con look-ahead, Survivor Intensity y sus triggers exactos, ciclo Build Up/Sustain Peak/Peak Fade/Relax con tiempos (3–5 s, 30–45 s), pacing ≠ dificultad, bosses fuera del director.
- **Steering Behaviors for Autonomous Characters** — Craig Reynolds (red3d.com/cwr/steer, paper 1999 + OpenSteer) — vocabulario canónico: seek/flee, pursue/evade, wander, separation/alignment/cohesion, obstacle avoidance.
- **Game AI Pro (gameaipro.com, capítulos gratuitos)** — Champandard & Dunstan (Behavior Tree Starter Kit), Graham (Utility Theory), Dill (Dual-Utility), Hanlon & Watts (Dragon Age Inquisition), Walsh (Splinter Cell Blacklist perception), Welsh (Crytek Target Tracks), Sunshine-Hill (LOD Trader), Zubek (1000 NPCs at 60 FPS) — el canon de BT, utility, percepción y AI LOD.
- **Introduction to A*** — Red Blob Games (Amit Patel) — BFS/Dijkstra/greedy/A*, f = g + h, heurísticas de grid, "el diseño del grafo importa más que el algoritmo".
- **Base sintetizada:** [ver: unity/csharp-patrones] (FSM base, pooling, runtime sets, event channels, cero allocs), [ver: unity/fisica-unity] (queries/LayerMask/triggers, Rigidbody kinematic, NonAlloc), [ver: gamedev/mecanicas-sistemas] (tablas de pesos, percepción del azar), [ver: gamedev/animacion] + [ver: gamedev/game-feel] (telegraphing, anatomía de ataque), [ver: gamedev/fundamentos-diseno] (flow/pacing), [ver: gamedev/level-design] (encounter design).
