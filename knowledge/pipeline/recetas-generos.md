# Recetas por género en Unity

> **Cuando cargar este archivo:** al arrancar la implementación en Unity de un juego de un género concreto (plataformas 2D, top-down/twin-stick, puzzle en grid, endless runner, idle, roguelite de acción) — da la arquitectura, componentes y riesgos de cada receta. Las convenciones de DISEÑO de cada género están en [ver: gamedev/generos]; aquí está el CÓMO en Unity 6.x/URP.

Cada receta asume: proyecto Unity 6.x con URP, Input System nuevo [ver: unity/input-system], y las decisiones de diseño ya tomadas con [ver: gamedev/generos] y [ver: gamedev/mecanicas-sistemas]. La estructura general de carpetas/escenas del proyecto vive en [ver: estructura-proyecto]; el pulido de feel en [ver: feel-en-unity].

## Mapa de recetas

| Género | Motor de movimiento | Paquetes clave además del stack base | Procgen |
|---|---|---|---|
| Plataformas 2D | `Rigidbody2D` dynamic o kinematic custom | 2D Tilemap Extras, Cinemachine 3.x | Rara vez (niveles a mano) |
| Top-down / twin-stick | `Rigidbody2D` dynamic, `gravityScale = 0` | 2D Tilemap Extras, Cinemachine 3.x | Opcional |
| Puzzle por turnos / grid | Ninguno (modelo C# puro, sin física) | Tweening (PrimeTween/DOTween) | No (diseño a mano) |
| Endless runner / hyper-casual | `Rigidbody`/`Rigidbody2D` kinematic o transform | `ObjectPool<T>`, Cinemachine | Sí (segmentos barajados) |
| Idle / incremental | Ninguno | BreakInfinity.cs (BigDouble) | No |
| Roguelite de acción | Según el sub-género (top-down típico) | Tilemap por script, ScriptableObjects | Sí (core del género) |

---

## Base común: Tilemaps a fondo

Aplica a plataformas 2D, top-down y roguelite. Verificado contra Unity 6000.2 y 2D Tilemap Extras 4.3.

### Componentes y flujo

- Jerarquía: **Grid** (GameObject raíz, define `cellSize` y layout Rectangle/Hexagonal/Isometric) → hijos **Tilemap** + **TilemapRenderer**. Crear con GameObject ▸ 2D Object ▸ Tilemap.
- Se pinta desde la ventana **Tile Palette** (Window ▸ 2D ▸ Tile Palette): una palette es un tilemap-asset de tiles arrastrados desde sprites.
- Sprites de tiles: **Pixels Per Unit = tamaño del tile en px** (tile de 16px con PPU 16 → 1 tile = 1 unidad de mundo). Si no cuadra, todo lo demás (colliders, física, cámara) queda desalineado.
- Capas típicas por escena: `Ground` (con collider), `Walls` (con collider), `Decor` (sin collider, sorting layer propia), `Hazards` (trigger). Un Tilemap por capa lógica, todos bajo el mismo Grid.
- Conversión mundo↔celda: `grid.WorldToCell(worldPos)` → `Vector3Int`; `tilemap.GetCellCenterWorld(cell)` para el centro. Es la API puente para gameplay en grid.

### Rule Tiles y brushes (paquete 2D Tilemap Extras)

- **Paquete separado**: `com.unity.2d.tilemap.extras` (v4.3.0 verificada jul 2026) — instalarlo; no viene con el Tilemap base.
- **Rule Tile**: define reglas en una caja 3×3 de vecinos (This / Not This / Don't Care); si la regla matchea, pinta su output. Outputs: **Fixed** (un sprite), **Random** (varios, con ruido Perlin y rotación opcional), **Animation** (secuencia con velocidad). Transform rules: Fixed, **Rotated** (prueba rotaciones de 90°), **Mirror X/Y/XY** — con Rotated+Mirror, ~5 reglas cubren lo que a mano serían decenas.
- Variantes: Hexagonal Rule Tile, Isometric Rule Tile, **Rule Override Tile** (re-skin de un Rule Tile existente sin duplicar reglas — ideal para biomas), Advanced Rule Override Tile, **Animated Tile**, **Auto Tile** (genera reglas desde máscara de textura).
- **Brushes** incluidos: GameObject Brush (pinta prefabs, no tiles — enemigos, pickups), Group Brush, Line Brush, Random Brush. Todos extensibles: Scriptable Brushes/Scriptable Tiles son clases heredables para herramientas propias.
- Regla de trabajo: el Rule Tile se configura UNA vez por tileset; después el nivel se pinta (o se genera por script) sin pensar en qué sprite va en cada borde.

### Colisión: TilemapCollider2D + CompositeCollider2D

- **TilemapCollider2D** genera un shape por tile (según el Collider Type del tile: None/Sprite/Grid). Solo, produce cientos de colliders con aristas internas → el clásico "el personaje se traba entre dos tiles planos" (ghost collisions).
- Fix canónico: añadir **CompositeCollider2D** al mismo GameObject (trae Rigidbody2D — ponerlo **Static**) y en el TilemapCollider2D elegir **Composite Operation: Merge** (Unity 6 reemplazó el checkbox "Used By Composite" por operaciones Merge/Intersect/Difference/Flip). El composite fusiona todo en una geometría continua sin aristas internas.
- CompositeCollider2D — propiedades que importan:
  - **Geometry Type**: `Outlines` (contorno hueco, tipo EdgeCollider2D — para muros/suelo) | `Polygons` (sólido — necesario p.ej. como bounding shape de cámara).
  - **Generation Type**: `Synchronous` (regenera al cambiar — default) | `Manual` (solo al llamar `compositeCollider.GenerateGeometry()` — usar durante generación procedural masiva).
  - **Vertex Distance** (elimina vértices demasiado cercanos), **Offset Distance** (tolerancia para fusionar vértices entre shapes), **Use Delaunay Mesh** (triangulación extra, mejora mallas Polygons problemáticas).
- **Extrusion Factor** (aparece en TilemapCollider2D al activar composite): extruye cada shape para cerrar micro-huecos entre tiles vecinos antes de fusionar.
- **Max Tile Change Count** (TilemapCollider2D): tope de cambios acumulados antes de un rebuild completo; si se edita el tilemap en runtime con frecuencia, bajarlo mejora los rebuilds incrementales.

### Rendimiento y chunks

- **TilemapRenderer ▸ Mode** (verificado Unity 6000.2):
  - `Chunk` (default): agrupa tiles por ubicación+textura y batchea por chunk — el mejor rendimiento, PERO incompatible con el SRP Batcher.
  - `SRP Batch`: para URP; batchea por chunk pero solo grupos secuenciales en sort order.
  - `Individual`: cada tile se ordena por separado — obligatorio cuando los tiles deben intercalarse en sorting con otros sprites (top-down con Y-sort, isométrico con Custom Sorting Axis). Más caro.
- **Detect Chunk Culling Bounds**: `Auto` inspecciona los sprites para expandir el culling (evita que tiles más grandes que la celda desaparezcan en el borde de cámara); `Manual` para fijarlo.
- Mapas grandes: dividir en varios Tilemaps por zona (y activar/desactivar por distancia) en vez de un tilemap monolítico; los tiles comparten sprite atlas para no romper batching [ver: unity/rendimiento-unity].

### Tilemaps por script (base de la procgen)

- `tilemap.SetTile(cell, tile)` para cambios puntuales; para generación masiva usar **`tilemap.SetTiles(Vector3Int[], TileBase[])`** en una sola llamada (firma verificada; hay sobrecarga con `TileChangeData[]`).
- Durante la generación: CompositeCollider2D en `Manual` → escribir todos los tiles → `GenerateGeometry()` una vez al final.
- `tilemap.GetTile<T>(cell)` / `tilemap.HasTile(cell)` para queries de gameplay; el Rule Tile se re-evalúa solo al escribir vecinos.

---

## Receta: Plataformas 2D

**Diseño previo obligatorio:** convenciones de forgiveness (coyote, buffer, corner correction) en [ver: gamedev/generos]; implementación del buffer con timestamps en [ver: unity/input-system].

**Arquitectura de escenas/sistemas:** Boot (managers persistentes) → Menu → una escena por nivel o escena Game + niveles como prefabs/tilemaps cargados aditivamente [ver: unity/arquitectura-unity]. Sistemas: PlayerController, CameraRig (Cinemachine), LevelManager (spawn/checkpoint/muerte), colecciones/HUD [ver: ui-flujo-completo].

**La decisión #1 — motor de movimiento:**

| Vía | Cuándo | Costo |
|---|---|---|
| `Rigidbody2D` Dynamic + `linearVelocity` en FixedUpdate | Default para el 90% de los plataformas: interactúa con física real (empujones, plataformas móviles, knockback) | Bajo; tuning de slopes/fricción a mano [ver: unity/fisica-unity] |
| Kinematic custom estilo Thorson (TowerFall/Celeste) | Precision platformer: feel pixel-perfect, determinismo total, replays | Alto: colisión AABB, movimiento y resolución 100% propios |

El modelo Thorson (fuente primaria, Medium): dos clases — **Solids** (geometría) y **Actors** (jugador/enemigos) — con AABB de enteros que jamás se solapan; `MoveX/MoveY(float amount, Action onCollide)` acumulan el resto subpíxel en un `remainder` y mueven píxel a píxel chequeando colisión; los Solids al moverse **empujan** (con `Squish()` si no hay espacio) y **cargan** a los Actors montados (push tiene prioridad sobre carry). En Unity se implementa sin Rigidbody dinámico: Kinematic + queries propias, o incluso sin física usando el tilemap como grid de colisión.

**Componentes concretos:** Tilemaps con Rule Tiles + TilemapCollider2D + CompositeCollider2D (Merge, Outlines) — sección anterior. Salto de altura variable y gravedad asimétrica (más gravedad cayendo que subiendo, vía `gravityScale` dinámico o multiplicador propio). One-way platforms: **`PlatformEffector2D`** con Used By Effector en el collider (Surface Arc ~180°). Plataformas móviles: Rigidbody2D **Kinematic** + `MovePosition` en FixedUpdate; arrastrar al jugador sumándole el delta de la plataforma (no parenting de Rigidbodies). Ground check: `Physics2D.BoxCast` bajo los pies con LayerMask de suelo, no un raycast único. Cámara: `CinemachineCamera` + **`CinemachineConfiner2D`** con un CompositeCollider2D (Geometry Type: Polygons) como bounding shape por zona — acepta cualquier Collider2D pero los docs recomiendan composite de polígonos; llamar `InvalidateBoundingShapeCache()` si el polígono cambia [ver: unity/rendering-urp].

**Riesgos típicos → solución:**

| Riesgo | Solución |
|---|---|
| Personaje se traba en uniones de tiles planos | CompositeCollider2D Merge + Extrusion Factor (ver base común) |
| Se pega a las paredes al saltar contra ellas | `PhysicsMaterial2D` con friction 0 en el jugador; fricción del suelo simulada por código |
| Salto floaty / feel muerto | Gravedad de juego (gravityScale 2–5), asimétrica, corte al soltar; tuning en [ver: feel-en-unity] y [ver: gamedev/generos] |
| Inputs de salto perdidos entre Update/FixedUpdate | Buffer por timestamp + coyote time (patrón completo en [ver: unity/input-system]) |
| Resbala por slopes o "vuela" al bajarlas | Proyectar velocidad sobre la normal de contacto [ver: unity/fisica-unity] |

**Alcance 1 dev:** las mecánicas son la parte barata; el costo real es la CANTIDAD de niveles buenos y su iteración (playtest por nivel). Presupuestar el contenido, no el controller [ver: gamedev/generos], [ver: produccion-solo-dev].

---

## Receta: Top-down / twin-stick

**Arquitectura:** igual que plataformas (Boot → Menu → Game); sistemas: PlayerController, AimSystem, WeaponSystem, spawner de enemigos + IA [ver: ia-enemigos], HUD.

**Movimiento:** `Rigidbody2D` Dynamic, **`gravityScale = 0`**, rotación Z congelada; `linearVelocity = input.normalized * speed` en FixedUpdate (normalizar SIEMPRE: diagonal sin normalizar = 41% más rápido). Colliders de muros: tilemap con Composite (base común).

**Sorting por profundidad (el problema #1 del top-down):** Project Settings ▸ Graphics ▸ Camera Settings (en URP 2D: en el asset del 2D Renderer) → **Transparency Sort Mode: Custom Axis**, **Transparency Sort Axis (0, 1, 0)** → los sprites con menor Y se dibujan delante. En cada SpriteRenderer, **Sprite Sort Point: Pivot** (default es Center) con pivot en los pies. Personajes multi-sprite: **SortingGroup** en la raíz. Tilemaps de decoración que deban intercalarse con personajes → TilemapRenderer Mode `Individual`.

**Colliders "de pies":** el BoxCollider2D/CapsuleCollider2D del personaje cubre solo los pies (tercio inferior del sprite), no el cuerpo — así puede pasar "por detrás" de props y el Y-sort hace la ilusión de profundidad.

**Aim twin-stick (mouse + stick con Input System):** dos actions separadas — `Aim` (Value/Vector2, `<Gamepad>/rightStick`) y el mouse por posición:

```csharp
Vector2 aimDir;
Vector2 stick = _aim.ReadValue<Vector2>();               // <Gamepad>/rightStick
if (stick.sqrMagnitude > 0.01f) aimDir = stick.normalized;
else {
    Vector2 mouse = _cam.ScreenToWorldPoint(Mouse.current.position.ReadValue());
    aimDir = (mouse - (Vector2)transform.position).normalized;
}
```

**Componentes:** Cinemachine con dead zone suave (o Position Composer) siguiendo al player; proyectiles con pooling `ObjectPool<T>` [ver: unity/csharp-patrones] y layers `PlayerProjectile`/`EnemyProjectile` en la collision matrix [ver: unity/fisica-unity].

**Riesgos → solución:**

| Riesgo | Solución |
|---|---|
| Personajes que se dibujan encima/debajo mal | Custom Axis (0,1,0) + Sort Point Pivot + SortingGroup (arriba) |
| Balas atraviesan enemigos rápidos | Collision Detection Continuous o hitscan por raycast |
| GC spikes por Instantiate/Destroy de balas | `ObjectPool<T>` desde el día 1 |
| El jugador choca "con el aire" sobre props | Collider solo en los pies; el resto del sprite es visual |
| Enemigos que se empujan entre sí en masa | Layer `Enemy` sin auto-colisión en la matrix, o steering con separación |

**Alcance 1 dev:** muy viable; el costo se va en variedad de enemigos e IA, no en el motor de movimiento. Roguelite top-down = esta receta + la de roguelite (abajo).

---

## Receta: Puzzle por turnos / grid

**Principio rector:** el estado del juego vive en un **modelo C# puro** (`Vector2Int` + arrays/diccionarios), sin física ninguna. Unity solo renderiza. Esto hace triviales el undo, el save, los tests unitarios [ver: testing-qa] y la validación de niveles.

**Arquitectura:** GameModel (grid lógico, reglas, win check — cero UnityEngine), GameView (sprites/tweens que reflejan el modelo), InputRouter (traduce input a comandos), UndoStack. Niveles como ScriptableObjects o pintados en Tilemap y parseados a modelo al cargar (`tilemap.HasTile` / `GetTile` sobre el bounding box).

**Movimiento en grid** — el Grid de Unity solo convierte coordenadas:

```csharp
public bool TryMove(Vector2Int dir)
{
    var target = _gridPos + dir;
    if (!_model.IsWalkable(target)) return false;
    _undoStack.Push(new MoveCmd(_gridPos, target));     // command pattern → undo gratis
    _gridPos = target;
    _targetWorld = _tilemap.GetCellCenterWorld((Vector3Int)target);
    return true;   // la vista tween-ea hacia _targetWorld; input en cola mientras tanto
}
```

**Undo/reset instantáneo es convención innegociable del género** [ver: gamedev/generos]: command pattern (cada acción sabe deshacerse) o snapshots del estado completo si el grid es chico. Tween de la vista con PrimeTween/DOTween [ver: unity/animacion-unity] — nunca mover con física.

**Riesgos → solución:**

| Riesgo | Solución |
|---|---|
| Modelo y vista desincronizados ("el sprite quedó en otra celda") | Única fuente de verdad = modelo; la vista NUNCA decide posiciones, solo interpola hacia lo que dice el modelo |
| Input durante animaciones rompe el estado | Lock de input hasta terminar el tween, o cola de comandos (mejor feel) |
| Undo que olvida efectos secundarios (botón presionado, caja caída) | Cada comando registra TODO su delta; test unitario: aplicar+deshacer = estado idéntico |
| Floats para lógica de celdas | `Vector2Int` en el modelo siempre; floats solo en la vista |

**Alcance 1 dev:** producción mínima; el 90% del trabajo es DISEÑO de puzzles y playtest ciego [ver: gamedev/generos]. La arquitectura modelo/vista se monta una vez y aguanta todo el juego.

---

## Receta: Endless runner / hyper-casual

**Arquitectura:** una sola escena Game + Menu overlay (el género exige retry instantáneo — recargar escena es demasiado lento para el loop de 30 s [ver: gamedev/generos]). Sistemas: RunnerController (auto-avance + input de un dedo), TrackManager (segmentos), DifficultyDirector (curva por distancia/tiempo), Score/Economy.

**El patrón de pista — reciclar, jamás instanciar:**
- Pista = cola de N segmentos-prefab (3–5 activos, 20–50 unidades cada uno) tomados de un `ObjectPool<T>`; cuando el jugador rebasa un segmento + margen, se re-posiciona al frente con contenido re-barajado (obstáculos como children activables, no instanciados).
- **Precisión float:** correr "hacia adelante" indefinidamente degrada la precisión de float lejos del origen (jitter visual y de física) [ver: unity/gotchas-unity]. Antídoto: **origin shift** — cada ~1000–2000 unidades, restar el offset a TODO (player, segmentos, partículas, targets de cámara) en un solo frame. Alternativa: el player quieto y el mundo moviéndose hacia él (evita el problema de raíz, complica físicas de salto).
- Movimiento del player: kinematic/transform con carriles (lerp entre X fijos) es lo estándar; física dinámica completa solo si el hook es físico.

**Móvil:** `Application.targetFrameRate = 60`; input de un toque/swipe con Enhanced Touch [ver: unity/input-system]; presupuesto de overdraw y batching agresivo [ver: unity/rendimiento-unity]. El negocio del género es UA, no diseño — validar CPI antes de pulir [ver: gamedev/generos].

**Riesgos → solución:**

| Riesgo | Solución |
|---|---|
| Stutter por Instantiate/Destroy de obstáculos | Pool total: segmentos y obstáculos pre-instanciados y reciclados |
| Jitter a los 2–3 minutos de run | Origin shift periódico (arriba) |
| Tunneling a alta velocidad | CCD Continuous en el player o colisión por raycast/overlap propio |
| Dificultad plana o imposible | DifficultyDirector con curva explícita (velocidad, densidad, tipos) tuneada por distancia, no hardcodeada por segmento |
| Retry lento mata la retención | Reset por re-posicionamiento de objetos, no `SceneManager.LoadScene` |

**Alcance 1 dev:** el juego es chico por definición; el costo está en el tuning del feel (3 s para entender, [ver: gamedev/generos]) y en la variedad de segmentos. Prototipo desechable primero.

---

## Receta: Idle / incremental

**Toda la matemática del género** (curva ~1.15x, prestige +50–200%, fórmulas de Cookie Clicker/AdVenture Capitalist) está en [ver: gamedev/mecanicas-sistemas] y [ver: gamedev/generos] — la spreadsheet va ANTES que el código. Aquí lo específico de Unity/C#:

**Arquitectura:** escena única + paneles UI [ver: ui-flujo-completo]. Sistemas: EconomyModel (C# puro, testeable), TickSystem, SaveSystem, OfflineCalculator, UIBinder. El juego ES la UI: la mayor parte del trabajo Unity es uGUI/UI Toolkit [ver: unity/ui-unity].

**Big numbers:** `double` aguanta hasta ~1.8e308 — suficiente para idles cortos. Pasado eso (o si el diseño contempla prestige profundo), usar **BreakInfinity.cs** (GitHub Razenpok, MIT): tipo `BigDouble` drop-in que llega hasta ~1e(9e15), port del break_infinity.js canónico del género, pensado para juegos (velocidad > precisión exacta). NO usar `System.Numerics.BigInteger`: memoria y costo crecen con el número, y el género no necesita precisión entera.
- Notación en UI (K, M, B, T…): formatear con tabla de sufijos propia; cachear el string y actualizar la UI a 2–4 Hz, no cada frame (formateo de strings = GC).

**Ticks:** lógica de economía en un tick fijo (5–10 Hz vía acumulador en `Update`), no por frame; la UI interpola si hace falta. Jamás `InvokeRepeating` por generador — un solo tick global recorre el modelo.

**Offline progress (LA promesa del género):**

```csharp
// Guardar en cada save: save.lastUtc = DateTime.UtcNow.ToString("o");
var last = DateTime.Parse(save.lastUtc, null, DateTimeStyles.RoundtripKind);
double secs = Math.Max(0, (DateTime.UtcNow - last).TotalSeconds); // reloj atrasado → 0
secs = Math.Min(secs, capHours * 3600);                           // cap de diseño (típico 2h–24h)
BigDouble earned = model.ProductionPerSecond() * secs;            // forma CERRADA
model.currency += earned;
ui.ShowWelcomeBack(earned, secs);
```

- **Forma cerrada, jamás simular** los segundos ausentes uno a uno. Si la producción cambia sola en el tiempo (generadores que compran generadores), integrar por pasos gruesos (p.ej. 60 pasos máximo para cualquier ausencia).
- Reloj del dispositivo es trampeable (adelantar la hora): clamp a 0 los deltas negativos, cap superior de diseño, y si hay economía real/ads recompensadas, validar contra hora de servidor.
- Save: JSON a `Application.persistentDataPath`, guardar en `OnApplicationPause(true)` (móvil) y por timer; mantener un backup rotado — un save corrupto en un idle mata al jugador entero.

**Riesgos → solución:**

| Riesgo | Solución |
|---|---|
| Overflow/Infinity de double a mitad del juego | BigDouble desde el día 1 si la curva lo va a pedir; migrar saves después es doloroso |
| GC por actualizar textos de números cada frame | UI a 2–4 Hz, strings cacheados, TextMeshPro `SetText` |
| Offline calc que congela el arranque | Forma cerrada / pasos gruesos con tope fijo |
| Trampa de reloj | Clamp + cap + (si hay dinero real) hora de servidor |
| Curva rota descubierta tarde | La spreadsheet manda; el código solo la ejecuta [ver: gamedev/mecanicas-sistemas] |

**Alcance 1 dev:** ideal — arte y escenas mínimos; el trabajo es matemática, UI y tuning contra sesiones reales. Meta-sistemas (prestige, misiones) en [ver: sistemas-meta].

---

## Receta: Roguelite de acción

**Diseño previo:** test de Josh Ge ("¿la mecánica core sola es divertida?"), meta-progresión obligatoria, scope por tiers — todo en [ver: gamedev/generos]. Combate y enemigos: [ver: ia-enemigos]; recompensas/desbloqueos: [ver: sistemas-meta].

**Arquitectura de escenas:** Boot → Hub/Menu (meta-progresión, tienda entre runs) → Run (escena de gameplay que se regenera por piso). Separación ESTRICTA de estado: `RunState` (HP, oro de run, items — muere con la run) vs `MetaState` (desbloqueos, moneda meta — persiste, es el save). Mezclarlos es el bug estructural #1 del género.

**Determinismo y seeds:** un `int seed` por run (mostrable/compartible); cada sistema con su propio `System.Random(seed + offset)` — JAMÁS `UnityEngine.Random` para generación (es estado global: cualquier VFX/shuffle ajeno que lo llame rompe la reproducibilidad).

**Items/upgrades como datos:** cada item/mejora = ScriptableObject (stats, sprite, efectos como lista de modificadores) + pools de drop con pesos [ver: gamedev/mecanicas-sistemas para loot tables; ver: unity/csharp-patrones para la arquitectura SO].

**Generación de niveles** (ver sección siguiente para técnicas): el output de la procgen es una estructura de datos (grid de celdas / grafo de salas) que después se PINTA al Tilemap con `SetTiles` + Rule Tiles (los bordes/esquinas se resuelven solos) + `GenerateGeometry()` del composite al final. GameObject Brush o spawn por script para poblar (enemigos, cofres, salida).

**Riesgos → solución:**

| Riesgo | Solución |
|---|---|
| Mapa generado injugable (salas inalcanzables) | Validación post-gen: flood fill desde el spawn; si no alcanza salida/llaves → regenerar (con presupuesto de intentos) |
| Runs irreproducibles al depurar | Seed por run + `System.Random` por sistema; log del seed en cada run |
| Estado de run que contamina la meta (o al revés) | Dos objetos de estado separados con ciclos de vida distintos; la run jamás escribe el save directamente |
| Explosión de contenido (100 items × interacciones) | Items = SO de datos + efectos componibles; métricas de pick/win rate desde el prototipo [ver: gamedev/mecanicas-sistemas] |
| Procgen antes que gameplay | Regla de Ge: primero el loop de combate divertido en UNA sala hecha a mano; la procgen después |

**Alcance 1 dev:** el género más amigable para 1 dev (contenido = sistemas × procgen) [ver: gamedev/generos]. El riesgo no es producción sino balance: presupuestar tuning con métricas.

---

## Generación procedural: cuándo y cómo

**Cuándo NO:** plataformas de precisión y puzzle — su valor es el diseño a mano de cada pantalla [ver: gamedev/generos]. **Cuándo sí:** roguelike/lite (core), runner (barajado de segmentos), top-down de exploración (opcional). Regla: la procgen multiplica contenido EXISTENTE que ya es divertido; no genera diversión.

Técnicas de menor a mayor complejidad, todas pintables a Tilemap con `SetTiles`:

| Técnica | Produce | Costo | Úsala para |
|---|---|---|---|
| Barajado de piezas hechas a mano (salas-prefab, segmentos) | Variedad controlada, calidad de autor | Mínimo | Runner, roguelite estilo Isaac/Spelunky-lite, primer roguelite |
| Drunkard's walk (random walk que talla suelo) | Cuevas orgánicas conectadas por construcción | Bajo | Mapas de exploración, minas |
| Rooms + corridors (grid o BSP) | Mazmorras clásicas sala-pasillo | Medio | Roguelike clásico |
| TinyKeep (Adonaac/Game Developer): salas random en un círculo → separación física → salas principales (>1.25× media) → Delaunay + MST + re-añadir ~8–10% de aristas → pasillos en L | Mazmorras orgánicas con loops | Alto | Roguelite ambicioso, segunda iteración |
| Wave Function Collapse (Gumin) — solo mención | Output que imita patrones de un ejemplo (overlapping o simple tiled model); usado en Bad North, Caves of Qud, Townscaper | Alto (contradicciones, debugging duro) | Decoración/biomas con implementación existente, NO como primer generador |

```csharp
// Drunkard's walk → Tilemap (patrón mínimo completo)
var rng = new System.Random(seed);
var floor = new HashSet<Vector2Int>();
var pos = Vector2Int.zero;
Vector2Int[] dirs = { Vector2Int.up, Vector2Int.down, Vector2Int.left, Vector2Int.right };
for (int i = 0; i < steps; i++) { floor.Add(pos); pos += dirs[rng.Next(4)]; }

var cells = floor.Select(p => (Vector3Int)p).ToArray();
groundMap.SetTiles(cells, Enumerable.Repeat((TileBase)groundRuleTile, cells.Length).ToArray());
wallComposite.GenerateGeometry();   // composite en Manual durante la generación
```

Patrón universal: **generar en datos → validar (flood fill, conteos) → pintar → colisionar**. Cada fase separada y testeable; la validación con presupuesto de reintentos y fallback (mapa mínimo garantizado).

## Reglas prácticas

1. Antes de la receta: checklist de convenciones del género [ver: gamedev/generos] — la receta implementa, no decide.
2. Tiles con PPU = px del tile; verificar que 1 tile = 1 unidad antes de pintar nada.
3. Instalar `com.unity.2d.tilemap.extras` y montar Rule Tiles ANTES de pintar el segundo nivel (el primero puede ser tiles sueltos de prototipo).
4. Todo tilemap con colisión: TilemapCollider2D + CompositeCollider2D (Composite Operation Merge, Rigidbody2D Static) desde el día 1 — nunca shipear colliders por-tile.
5. Un Tilemap por capa lógica (suelo/muros/decoración/hazards) bajo un mismo Grid; sorting layers explícitas.
6. Plataformas 2D: Rigidbody2D dynamic por default; kinematic custom (Thorson) solo si el juego ES el feel pixel-perfect.
7. Top-down: `gravityScale = 0`, input normalizado, Custom Sort Axis (0,1,0) + Sort Point Pivot + collider de pies — los cuatro juntos o la profundidad miente.
8. Puzzle/grid: modelo C# puro sin física; `Vector2Int` para lógica; la vista solo interpola. Undo por command pattern desde el primer commit.
9. Runner: pool total (segmentos + obstáculos) y origin shift periódico; retry sin recargar escena.
10. Idle: economía en spreadsheet → modelo C# testeable → UI. `BigDouble` (BreakInfinity.cs) si la curva pasará de double; offline por forma cerrada con cap.
11. Roguelite: `System.Random` con seed por sistema, jamás `UnityEngine.Random` en generación; log del seed de cada run.
12. Roguelite: RunState y MetaState separados con ciclos de vida distintos; solo MetaState toca el save.
13. Procgen: generar en datos → validar con flood fill → pintar con `SetTiles` (batch) → `GenerateGeometry()` una vez.
14. Procgen: empezar por barajado de piezas a mano; subir de técnica solo cuando la simple se quede corta.
15. Cámara 2D: Cinemachine + CinemachineConfiner2D con CompositeCollider2D (Polygons); nunca clamps a mano por nivel.
16. Proyectiles y spawns frecuentes: `ObjectPool<T>` antes del primer playtest largo, no después del primer GC spike.
17. Todo valor de feel (gravedad, coyote, velocidad de scroll, tick rate) en un ScriptableObject de tuning, no hardcodeado — el tuning es el 50% del trabajo de estas recetas.
18. Móvil (runner/idle/hyper-casual): `targetFrameRate = 60`, Enhanced Touch, y presupuesto de overdraw desde el primer build en dispositivo [ver: unity/rendimiento-unity].

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Personaje que se traba entre tiles "planos" | CompositeCollider2D Merge + Extrusion Factor; jamás colliders por-tile en producción |
| Pintar niveles con tiles sueltos y "luego ya pondré Rule Tiles" | Los Rule Tiles se configuran una vez y ahorran cada minuto siguiente; retrofitearlos re-pintando es carísimo |
| TilemapRenderer en Individual "porque sí" | Individual solo cuando el sorting lo exige (Y-sort/isométrico); Chunk/SRP Batch para el resto |
| Editar tilemap en runtime con Composite Synchronous y SetTile en loop | `SetTiles` batch + Generation Type Manual + `GenerateGeometry()` al final |
| Top-down con sorting por Order in Layer a mano, objeto por objeto | Custom Sort Axis (0,1,0) global + Sort Point Pivot: el sistema ordena solo |
| Twin-stick que solo apunta bien con mouse (o solo con stick) | Dos rutas de aim explícitas (posición vs dirección) desde el día 1; probar ambos esquemas cada build |
| Puzzle con el estado repartido entre MonoBehaviours de las piezas | Modelo central C# puro; las piezas son vistas tontas |
| Runner que instancia obstáculos sobre la marcha | Pool + segmentos reciclados; Instantiate en runtime es el GC spike más evitable que existe |
| Idle con `float`/`int` para la moneda | `double` mínimo, `BigDouble` si la curva crece; float pierde precisión ridículamente pronto |
| Offline progress simulando cada tick ausente | Forma cerrada o pasos gruesos acotados; el arranque no puede costar minutos |
| Roguelite con `UnityEngine.Random` en la generación | Estado global irreproducible; `System.Random(seed)` por sistema |
| Procgen sin validación ("casi siempre sale bien") | Flood fill de conectividad + presupuesto de reintentos + fallback garantizado |
| WFC como primer generador | Contradicciones y debugging NP-duro para un beneficio que el barajado de piezas ya da; WFC solo con implementación existente y necesidad real |
| Física custom estilo Celeste "porque Celeste lo hizo" | Thorson lo justifica para precision platformers con años de tuning; Rigidbody2D dynamic cubre el 90% de los casos con 10% del código |

## Fuentes

- **gamedev/generos.md** — base propia — convenciones, mercado y alcance solo-dev por género; esta receta implementa lo que ese archivo decide.
- **gamedev/mecanicas-sistemas.md** — base propia — loot tables con pesos, matemática idle/prestige, verbos y economías que estas recetas ejecutan.
- **unity/fisica-unity.md** — base propia — Rigidbody2D, las 3 vías de character controller, FixedUpdate/interpolación; toda la física citada aquí.
- **unity/input-system.md** — base propia — buffer con timestamps, coyote, Enhanced Touch, patrón de aim; el input de todas las recetas.
- **Tilemap Collider 2D reference — Unity Manual 6000.2 (docs.unity3d.com)** — Composite Operation (Merge/Intersect/Difference/Flip), Extrusion Factor, Max Tile Change Count; la colisión de tilemaps sale de aquí.
- **Composite Collider 2D reference — Unity Manual 6000.2** — Geometry Type Outlines/Polygons, Generation Type Synchronous/Manual, Vertex/Offset Distance, Use Delaunay Mesh.
- **Tilemap Renderer reference — Unity Manual 6000.2** — modos Chunk/SRP Batch/Individual con sus trade-offs exactos y Detect Chunk Culling Bounds.
- **Rule Tile — 2D Tilemap Extras 4.3 (docs.unity3d.com/Packages)** — reglas 3×3, outputs Fixed/Random/Animation, transforms Rotated/Mirror, variantes hex/iso.
- **2D Tilemap Extras 4.3 — índice del paquete** — inventario verificado de tiles (Rule/Override/Animated/Auto) y brushes (GameObject/Group/Line/Random); confirma que es paquete separado.
- **2D Sorting — Unity Manual 6000.2** — Transparency Sort Mode/Custom Axis (0,1,0), Sort Point Center vs Pivot, dónde se configura en URP 2D; el Y-sort del top-down.
- **Tilemap.SetTiles — Unity Scripting API 6000.2** — firmas exactas del batch de tiles usado en toda la procgen.
- **CinemachineConfiner2D — Cinemachine 3.1 docs** — confinamiento de cámara 2D, composite de Polygons recomendado, InvalidateBoundingShapeCache.
- **Celeste and TowerFall Physics — Maddy Thorson (Medium)** — fuente primaria del modelo Actor/Solid: MoveX/MoveY con remainder subpíxel, AABB enteros, push/carry/squish; la vía "física custom" de plataformas.
- **BreakInfinity.cs — Razenpok (GitHub, MIT)** — BigDouble hasta ~1e(9e15), port de break_infinity.js, drop-in de double; los big numbers del idle.
- **Procedural Dungeon Generation Algorithm — A. Adonaac (Game Developer)** — algoritmo TinyKeep completo con números (salas >1.25× media, ~8–10% de aristas re-añadidas tras el MST).
- **WaveFunctionCollapse — Maxim Gumin (GitHub)** — overlapping/simple tiled model, juegos que lo usan, contradicciones; la base de la mención de WFC.
