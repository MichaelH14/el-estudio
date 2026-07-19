# Multijugador y netcode en Unity

> **Cuando cargar este archivo:** al decidir si un juego lleva multijugador y de qué tipo, al implementar netcode en Unity (NGO, Mirror, FishNet o server propio), al montar leaderboards/ghosts/turnos asíncronos, o al testear/depurar cualquier feature en red. La teoría de mercado y costo del género multijugador está en [ver: gamedev/generos] (sección "Multijugador competitivo") — este archivo es el CÓMO técnico.

## 0. La decisión previa (antes de una línea de netcode)

Multijugador online realtime cuesta 3-5x el equivalente single-player y añade el riesgo de población (huevo-gallina de jugadores) [ver: gamedev/generos]. Antes de elegir librería, elegir **capa de multijugador**:

| Capa | Qué da | Costo técnico | Cuándo |
|---|---|---|---|
| **Asíncrono** (leaderboards, ghosts, turnos) | El 80% del valor social: competir sin coincidir | Bajo: backend HTTP simple | Default para solo dev. Sección 5 |
| **Local** (pantalla compartida, varios gamepads) | Party/co-op sin red | Cero netcode (solo input multi-device [ver: unity/input-system]) | Party, versus de sofá |
| **Co-op por invitación** (host = un jugador, join code) | Jugar con amigos, sin matchmaking ni servers propios | Medio: NGO + Relay/Sessions | Co-op 2-8, sin dinero en juego |
| **Competitivo matchmade** | Partidas justas on-demand | Alto: server dedicado autoritativo + anti-cheat + población | Solo con presupuesto y plan de jugadores |

Regla de [ver: gamedev/generos]: si no puedes responder "¿de dónde salen mis primeros 1,000 concurrentes?", baja una fila en la tabla. Y el netcode se decide el **día 1 de arquitectura** — nunca se "añade después".

## 1. Fundamentos motor-agnósticos (Gambetta destilado)

La serie *Fast-Paced Multiplayer* de Gabriel Gambetta (4 partes) es el canon. Comprimida:

### 1.1 Servidor autoritativo (Parte I)

- Premisa: **no confíes en el cliente; asume que VA a hacer trampa**. En cuanto el cliente decide su propio estado (posición, vida, dinero), un cliente modificado decide lo que quiera.
- Arquitectura: el cliente envía solo **inputs** ("me muevo a la derecha"), el server simula y devuelve estado. El cliente es un "espectador privilegiado": renderiza lo que el server dicta.
- Consecuencia: **si hay dinero, ranking o economía persistente, servidor autoritativo SIEMPRE.** No es opcional ni optimizable.
- El problema que crea: con 50-200 ms de round-trip, el "dumb client" se siente injugable (input → esperar al server → ver el resultado). Las 3 técnicas siguientes existen para tapar esa latencia SIN devolver autoridad al cliente.

### 1.2 Client-side prediction + server reconciliation (Parte II)

- **Predicción**: el cliente aplica su propio input localmente de inmediato (el juego es mayormente determinista) mientras el mensaje viaja. Cero lag percibido en TU personaje.
- **Reconciliación**: cada input lleva **número de secuencia**. El server responde con el estado autoritativo + el último input procesado. El cliente: (1) resetea a ese estado, (2) **re-aplica los inputs pendientes** aún no confirmados. Sin esto, la predicción produce "rubber-banding" (saltos hacia atrás).

```csharp
// Esqueleto conceptual de predicción+reconciliación (lado cliente)
struct InputCmd { public uint seq; public Vector2 move; public float dt; }
List<InputCmd> pending = new();          // inputs enviados sin confirmar
void OnInput(Vector2 move, float dt) {
    var cmd = new InputCmd { seq = nextSeq++, move = move, dt = dt };
    pending.Add(cmd);
    SendToServer(cmd);                   // viaja
    ApplyMove(cmd);                      // y se aplica YA (predicción)
}
void OnServerState(Vector3 authoritativePos, uint lastProcessedSeq) {
    transform.position = authoritativePos;              // reset al estado del server
    pending.RemoveAll(c => c.seq <= lastProcessedSeq);  // descartar confirmados
    foreach (var c in pending) ApplyMove(c);            // re-aplicar pendientes
}
```

Requisito: `ApplyMove` debe ser **la misma lógica determinista en cliente y server** (compartir el método, no duplicarlo).

### 1.3 Entity interpolation (Parte III)

- El server emite snapshots a baja frecuencia (ejemplo de Gambetta: 10/s → *time step* de 100 ms). Teletransportar a los otros jugadores snapshot a snapshot se ve a saltos.
- Solución contraintuitiva: **renderiza a los DEMÁS en el pasado** — con los dos últimos snapshots recibidos, interpola (lerp) entre ellos. Ves movimiento real ocurrido, no una extrapolación adivinada, con ~1 time step de retraso (100 ms en el ejemplo), que en juego normal no se nota.
- Resultado del sistema completo: tú te ves en el presente (predicción); los demás van con retraso (interpolación); el server manda (autoridad).

### 1.4 Lag compensation (Parte IV)

- Problema: apuntas a donde el enemigo estaba hace ~100 ms (interpolación). Con hit-scan, fallarías tiros perfectos.
- Solución: el cliente manda el disparo con timestamp y vector de puntería; el server **reconstruye el mundo en ese instante pasado** (guarda historial de posiciones por tick), evalúa el hit contra lo que el tirador VEÍA, y aplica el resultado.
- Trade-off asumido: la víctima puede recibir un tiro una fracción de segundo DESPUÉS de ponerse a cubierto (era vulnerable en el pasado del tirador). Se acepta porque favorecer al que apuntó bien se siente más justo que fallar tiros limpios.

### 1.5 Tick rate

- El server no simula por frame de render: simula a **tick rate** fijo (la malla temporal de todo lo anterior: secuencias, snapshots, historial de lag comp).
- Más ticks/s = menos latencia añadida y más CPU/ancho de banda. Acción rápida pide más; turnos/casual, menos. En NGO el `TickRate` se configura en el `NetworkManager` (default 30 ticks/s); los cambios de `NetworkVariable` se acumulan y se envían **por tick**, no por frame.
- Para profundizar más allá de Gambetta (rollback GGPO, física en red de Rocket League, netcode de Overwatch, determinismo): el repo curado **0xFA11/MultiplayerNetworkingResources** indexa los canónicos (Fiedler/Gaffer on Games, Valve Source Networking, "1500 Archers", GDC de Overwatch y Mortal Kombat).

## 2. Tabla de decisión: NGO vs server propio vs alternativas (estado 2026)

Verificado a julio 2026: **NGO 2.13** (requiere Unity 6.0+), **Mirror** (MIT, soporta hasta Unity 6000.1), **FishNet** (gratis sin límite de CCU, Unity 6+ soportado por completo).

| Criterio | NGO 2.x (oficial) | Mirror | FishNet | Server propio (Node/WS + cliente Unity) |
|---|---|---|---|---|
| Licencia/costo | Gratis, paquete oficial | MIT, gratis | Gratis sin CCU caps; extras Pro | Gratis + hosting |
| Madurez | Oficial, integrado al ecosistema Unity 6 | 1000+ juegos Steam, 200M+ jugadores (Population: ONE, Zooba) | Activo, "no-break promise" entre majors, LTS propio | Tú eres la madurez |
| Client-side prediction | ❌ No integrada — manual (sección 1.2) u owner-authority | ❌ En fase "researching" | ✅ Integrada gratis, tick-based (patrón replicate/reconcile) | Manual |
| Lag compensation | ❌ Manual | ⚠️ Beta | ✅ Pero solo en Pro (collider rollback) | Manual |
| Integración Relay/Lobby/MPPM/Tools oficiales | ✅ Nativa | Parcial (transports de terceros) | Parcial (transports) | N/A |
| Ideal para | Co-op/casual con simulación en Unity; quien quiere el camino soportado por Unity | Proyectos que valoran API estable estilo UNET ([SyncVar]/[Command]/[ClientRpc]) y años de battle-testing | Acción rápida server-authoritative sin escribir CSP a mano | Lógica de datos/reglas (cartas, turnos, economía), clientes web, control total |

**Por tipo de juego:**

| Juego | Recomendación |
|---|---|
| Puzzle diario, ranking, ghosts de carreras | Sin netcode: backend asíncrono (sección 5) |
| Party de sofá | Input local multi-gamepad, cero red |
| Co-op 2-8 con amigos, sin dinero | NGO + Sessions/Relay, host = un jugador |
| Turnos online (cartas, tablero) | Server propio HTTP/WebSocket: la "simulación" son reglas de datos, no física — correr Unity headless para eso es desperdicio |
| Acción competitiva, apuestas/ranking real | Server dedicado autoritativo: NGO en modo `StartServer()` headless, o FishNet, o server propio. Validación total server-side (sección 6) |
| Fighting 1v1 | Rollback netcode (familia GGPO, determinismo + resimulación): NINGUNA de las 3 librerías lo trae de fábrica; es otra arquitectura (ver repo 0xFA11) |
| MMO/persistente masivo | Fuera del alcance de estas librerías high-level; tech de servidor especializada |

**Cuándo server propio en vez de NGO:** cuando la verdad del juego NO necesita el motor de Unity (nada de física/colisiones server-side). Un server Node/WebSocket que valida reglas y persiste estado es más barato de hostear, más fácil de escalar y trivial de testear que un build headless de Unity. Unity queda como cliente de render puro. Para WebGL: NGO soporta WebGL vía Unity Transport 2.0+ (WebSockets), pero un server propio WS es el camino natural de los juegos web ligeros.

## 3. Netcode for GameObjects (NGO 2.x) — el mapa mínimo

Paquete `com.unity.netcode.gameobjects` (2.13 a jul-2026, Unity 6.0+, Mono e IL2CPP). Modelo default: **client-server con server autoritativo** (existe además "distributed authority" vía servicio cloud de Unity, donde el owner de cada objeto es su autoridad — útil casual, inaceptable si hay dinero: la autoridad vive en clientes).

### 3.1 NetworkManager y arranque

- Un `NetworkManager` en escena (singleton: `NetworkManager.Singleton`) + transporte `UnityTransport` en el mismo GameObject.
- `StartHost()` (server + cliente local, el modo co-op típico), `StartServer()` (dedicado, sin cliente local), `StartClient()`.
- `UnityTransport.SetConnectionData(ip, port)` para conexión directa; `SetHostRelayData()`/`SetClientRelayData()` para Relay.
- **Connection Approval**: activar en el inspector + `NetworkManager.ConnectionApprovalCallback` — tu primer guardián anti-cheat (validar versión, token de sesión, cupo) antes de aceptar al cliente.
- Callbacks: `OnClientConnectedCallback` / `OnClientDisconnectCallback`.
- "Enable Scene Management" → `NetworkManager.SceneManager` carga/sincroniza escenas a todos los clientes (incluye late-joiners) [ver: unity/arquitectura-unity].

### 3.2 NetworkObject, spawning y ownership

- Todo lo replicado lleva `NetworkObject` en la raíz del prefab + scripts que heredan de `NetworkBehaviour` (no `MonoBehaviour`). El prefab se registra en la lista de Network Prefabs del `NetworkManager`.
- **Solo el server spawnea** (en client-server):

```csharp
var instance = Instantiate(enemyPrefab);
instance.GetComponent<NetworkObject>().Spawn();   // Spawn(destroyWithScene: true) por defecto
// Con dueño: NetworkManager.SpawnManager.InstantiateAndSpawn(prefabNetObj, ownerClientId);
m_Spawned.Despawn();                              // solo la autoridad; destruye por defecto
```

- `Instantiate` solo crea la copia local — sin `Spawn()` no existe en red. `OnNetworkSpawn()` es el "Start de red" de un `NetworkBehaviour` (ahí se suscriben callbacks, sección 3.3).
- **Ownership**: por defecto el server es dueño de todo. `IsOwner`, `OwnerClientId`, `ChangeOwnership()`. El dueño puede recibir autoridad limitada (transform, NetworkVariables owner-write) — el server retiene spawn/despawn y la verdad del juego.
- Player objects: el prefab de jugador asignado en `NetworkManager` se spawnea por cliente conectado con ese cliente como owner.
- Proyectiles y spawns en ráfaga: pooling con `INetworkPrefabInstanceHandler` (la versión de red de [ver: unity/csharp-patrones] sección ObjectPool).

### 3.3 NetworkVariables vs RPCs — el criterio

**Test oficial: ¿un jugador que entra a mitad de partida necesita este dato? Sí → `NetworkVariable`. No → RPC.**

| | `NetworkVariable<T>` | RPC (`[Rpc]`) |
|---|---|---|
| Naturaleza | ESTADO persistente (vida, puerta abierta, score) | EVENTO transitorio (explosión, animación one-shot) |
| Late-joiners | Reciben el valor actual automático | Se lo pierden |
| Bandwidth | Solo envía deltas al cambiar, por tick | Cada llamada viaja entera |
| Garantías | Solo el último valor; **dos variables no llegan atómicamente juntas** | Reliable por defecto y en orden; los N parámetros llegan juntos |
| Trampa típica | Usarla como evento (te pierdes cambios intermedios) | Usarlo como estado (late-joiner ve el mundo vacío) |

```csharp
public class Health : NetworkBehaviour
{
    // Default: todos leen (ReadPermission.Everyone), SOLO el server escribe (WritePermission.Server)
    private NetworkVariable<int> hp = new(100);

    public override void OnNetworkSpawn() => hp.OnValueChanged += OnHpChanged;
    public override void OnNetworkDespawn() => hp.OnValueChanged -= OnHpChanged;
    private void OnHpChanged(int prev, int curr) { /* actualizar UI/VFX en todos */ }

    [Rpc(SendTo.Server)]                       // el cliente PIDE, el server DECIDE
    public void RequestAttackRpc(ulong targetId, RpcParams p = default)
    {
        ulong attacker = p.Receive.SenderClientId;         // identidad real del emisor
        if (!ServerValidateAttack(attacker, targetId)) return;  // rango, cooldown, línea de visión
        hp.Value -= 10;                        // solo el server puede escribir
    }
}
```

- Tipos soportados: primitivos C#, structs Unity (`Vector3`, `Quaternion`...), enums, `INetworkSerializable`, structs unmanaged con `INetworkSerializeByMemcpy`, `FixedString32Bytes`…`4096Bytes`. **`string` NO está soportado** (usar FixedString). Colecciones: `NetworkList<T>` (crear en `Awake`, evento `OnListChanged`).
- RPCs 2.x: nombre del método DEBE terminar en `Rpc`. `[Rpc(SendTo.X)]` con `SendTo.Server / Owner / NotOwner / Everyone / ClientsAndHost / Me / NotMe / NotServer / SpecifiedInParams`. Runtime targeting: `AllowTargetOverride = true` + `RpcTarget.Single/Group/Not(...)`. Entrega: `RpcDelivery.Reliable` (default, orden garantizado) o `Unreliable` (para spam tolerante a pérdida). `InvokePermission` (`RpcInvokePermission.Server/.Owner/.Everyone`) restringe quién puede invocarlo.
- Tiempo: `NetworkManager.LocalTime` (adelantado; para lo que controla el owner) vs `ServerTime` (retrasado; para comparar contra estado server-auth como `NetworkTransform`). Código por tick: evento `NetworkTickSystem.Tick`.

### 3.4 NetworkTransform

- Componente helper que sincroniza transform con la **interpolación de entidades (sección 1.3) ya implementada** — solo interpola, no extrapola (extrapolación: FishNet Pro o manual).
- **Server-authoritative por defecto** (AI, NPCs, mundo). Modo **owner-authoritative** para el personaje del jugador: respuesta inmediata a su input a cambio de confiarle su posición al cliente — aceptable en co-op casual, NO con dinero/ranking (ahí: server-auth + predicción manual, o FishNet).
- Tuning de bandwidth: sincronizar solo los ejes usados; thresholds mínimos de cambio; `UseHalfFloatPrecision` (float 4B → 2B); `UseQuaternionSynchronization` para jerarquías complejas + `UseQuaternionCompression` (16B → 4B, "smallest three"). Interpolación: tipos Lerp / Smooth Dampening + `PositionMaxInterpolationTime` etc.
- `InLocalSpace` para objetos parentados; `SwitchTransformSpaceWhenParented` transiciona world↔local sin saltos.
- Física en red: el server simula, los clientes reciben — Rigidbodies no-kinematic en clientes pelearán con el NetworkTransform (usar `NetworkRigidbody` del paquete si aplica y FixedUpdate discipline [ver: unity/fisica-unity]).

### 3.5 Transporte, Relay y Sessions

- **Unity Transport (UTP)** es el transporte default (UDP; WebSockets para WebGL — NGO soporta WebGL con UTP 2.0+).
- **Relay** (Unity Gaming Services): proxy universal entre jugadores — el host es un jugador SIN IP pública ni port-forwarding; los demás entran con **join code**. Resuelve NAT traversal sin server dedicado. Costo: un salto extra de latencia (proxy).
- **Sessions (Multiplayer Services SDK)**: a 2026 es la vía recomendada por Unity — unifica Lobby + Matchmaker + Relay bajo una sola API de "sesiones" (crear sesión, join por código, listar). Los SDKs sueltos de Lobby/Relay siguen funcionando pero son la vía legacy; proyectos nuevos van por Sessions.
- Receta co-op solo-dev: `StartHost()` + Sessions con join code + `NetworkTransform` owner-auth + NetworkVariables server-write = co-op por invitación funcionando sin infra propia.

## 4. Mirror y FishNet en 30 segundos

- **Mirror**: heredero espiritual de UNET — `[SyncVar]`, `[Command]` (cliente→server), `[ClientRpc]` (server→clientes). MIT, gratis, muchísimo battle-testing (1000+ juegos Steam). Interest management (5 variantes), decenas de transports (UDP/TCP/WebSockets/Steam). Estado 2026: lag compensation en Beta, client-side prediction en "researching" — para CSP seria, no es el camino corto. Docs generales aún citan como recomendadas versiones LTS viejas, pero el README soporta explícitamente 6000.1: verificar la versión concreta al adoptar.
- **FishNet**: server-authoritative by design, gratis sin CCU caps, con la **predicción client-side integrada** (tick-based, replicate/reconcile) — su gran ventaja sobre NGO/Mirror para acción rápida. Lag compensation (rollback de colliders), extrapolación de NetworkTransform y code-stripping automático son **Pro** (de pago). "No-break promise": sin breaking changes entre majors (máx. 1 cada 6 meses).
- Criterio honesto: si tu juego necesita CSP + lag comp y no quieres escribirlas, FishNet (asumiendo Pro para lag comp) te ahorra el trabajo más difícil del netcode. Si tu juego es co-op/casual y quieres ecosistema oficial (Relay, MPPM, Tools, soporte de Unity), NGO. Mirror si valoras estabilidad de API y ejemplos maduros sobre features de vanguardia.

## 5. Multijugador asíncrono barato — el 80% del valor sin netcode realtime

Nada de esto necesita tick rate, predicción ni WebSockets: es un backend HTTP con auth. Da competencia y presencia social a costo de solo dev [ver: gamedev/generos, alternativas para 1 dev; ver: sistemas-meta].

| Feature | Cómo | Claves |
|---|---|---|
| **Leaderboards** | Backend propio (endpoint submit + top-N paginado) o servicio managed (UGS Leaderboards, Steam Leaderboards en su plataforma) | Validar server-side el score (sección 6): un leaderboard sin validación se llena de 999999999 la primera semana. Mostrar "tu posición ± vecinos", no solo el top global inalcanzable |
| **Ghosts** (carreras, speedrun) | Grabar input o transform del jugador por tick fijo → comprimir → subir como blob al backend → descargar y reproducir como entidad no-colisionable | Grabar a tick fijo e interpolar en reproducción (mismo principio de la sección 1.3). Versionar el formato del ghost: un cambio de física invalida ghosts viejos |
| **Turnos** (palabras, tablero, "tu movimiento") | Estado de partida en DB; endpoint "jugar movimiento" que valida reglas server-side; el rival consulta al abrir (polling) o recibe push notification | El server ES el árbitro: el cliente jamás manda "gané", manda el movimiento y el server aplica las reglas. Idempotencia: reintento del mismo movimiento no lo aplica dos veces |
| **Retos diarios / seeds compartidas** | Misma seed de RNG para todos los jugadores del día + leaderboard del reto | Gratis en netcode; enorme en retención [ver: gamedev/psicologia-retencion-negocio] |

En Unity: `UnityWebRequest` o `HttpClient` con `async`/`Awaitable` + `destroyCancellationToken` [ver: unity/csharp-patrones]. Nunca bloquear el main thread esperando red; siempre estado de UI para "cargando/sin conexión" [ver: ui-flujo-completo].

## 6. Anti-cheat pragmático

No existe cliente inhackeable (memoria editable, tráfico interceptable, builds decompilables). El anti-cheat rentable para un equipo chico es **diseño de servidor**, no software de kernel:

1. **El cliente pide, el server decide.** Todo RPC que muta estado se valida server-side: ¿puede este cliente hacer esto, ahora, desde donde está? (rango, cooldown, recursos, línea de visión, turno).
2. **Permisos como primera muralla**: NetworkVariables con `WritePermission.Server` (default — no lo relajes sin razón), RPCs con `InvokePermission`, `ConnectionApproval` al conectar.
3. **Identidad del emisor**: usar `RpcParams.Receive.SenderClientId`, jamás un "playerId" que venga como parámetro del cliente (suplantable).
4. **Rate limits server-side**: cadencia de disparo, acciones por segundo, mensajes de chat. Contador por cliente en el server; exceso = descartar y loggear (desconectar a reincidentes).
5. **Sanity checks de movimiento** aunque uses owner-authority: velocidad máxima entre updates, teleports imposibles, fuera de bounds. Corregir (snap-back) o expulsar.
6. **Economía y progresión: 100% server** ("gané 500 monedas" no existe como mensaje; existe "completé X", el server calcula la recompensa) — todo lo que toque dinero real, además, con las garantías de idempotencia de la sección 5.
7. **Nunca enviar al cliente lo que no debe saber** (wallhacks son datos que TÚ le mandaste): interest management / `ReadPermission.Owner` para info privada (mano de cartas).
8. Registrar anomalías (logs con clientId + acción + motivo del rechazo): sin telemetría no sabrás ni que te están robando [ver: testing-qa].

## 7. Testing multijugador

- **Multiplayer Play Mode (MPPM)**, paquete oficial `com.unity.multiplayer.playmode`: hasta 4 players de Editor (el principal + 3 virtuales) + hasta 4 instancias de build local, sin salir del Editor ni hacer builds por iteración. v3.0 requiere Unity 6.3 LTS (Windows/macOS); en 6.0-6.2 usar la versión de paquete correspondiente. Límites: los virtuales no editan escena ni tienen Editor completo; es para testing local chico, no carga masiva.
- **Simulación de latencia — obligatoria**: el netcode "funciona" en localhost (ping ~0) y se rompe a 150 ms. El paquete **Multiplayer Tools** (`com.unity.multiplayer.tools`, 2.2 a jul-2026, Unity 6000.0+) trae **Network Simulator**: componente `NetworkSimulator` con presets reales (broadband/DSL/satélite, 2G-5G), latencia/jitter/packet loss configurables y "scenarios" que degradan la conexión dinámicamente (lag spikes, desconexiones). Probar SIEMPRE el juego con el preset móvil peor que soportes.
- Multiplayer Tools también incluye: **Network Profiler** (qué objeto/variable consume bandwidth), **Runtime Net Stats Monitor** (stats en pantalla en builds) y **Network Scene Visualization**.
- **Bots**: para probar N jugadores sin N humanos — clientes headless (build por CLI con args de conexión; NGO documenta un command-line helper) corriendo input scriptado o la IA del juego [ver: ia-enemigos]. Un bot que se conecta, se mueve al azar y dispara encuentra el 80% de los crashes de red.
- Matriz mínima antes de "funciona": host solo · host+1 cliente · cliente que entra a MITAD de partida (late-join: aquí mueren los que usaron RPCs como estado) · cliente que se desconecta y reconecta · 150+ ms con 2-5% packet loss · host cierra la app sin avisar.
- Test de trampa: intenta TÚ hacer trampa (invocar tus RPCs con valores absurdos, spamear, mandar posición teleportada). Cada exploit que encuentres = una validación de la sección 6 que faltaba.

## Reglas practicas

1. Decide la capa de multijugador (asíncrono/local/co-op invitación/competitivo) ANTES de elegir librería; cada salto de fila multiplica el costo [ver: gamedev/generos].
2. ¿Dinero, ranking o economía persistente? → servidor autoritativo, sin debate. El cliente solo envía inputs/peticiones.
3. Netcode es arquitectura del día 1: la lógica de gameplay se escribe desde el inicio como "el server simula, el cliente presenta", aunque el server aún sea el host local.
4. Estado → `NetworkVariable`; evento → RPC. Test: ¿el que entra a mitad de partida lo necesita? Sí = variable.
5. No relajes los defaults de NGO (`WritePermission.Server`, `RpcDelivery.Reliable`) sin poder explicar el porqué en una frase.
6. Todo RPC que muta estado valida server-side: emisor real (`SenderClientId`), permisos, rango/cooldown/recursos, rate limit.
7. La lógica de movimiento compartida cliente/server vive en UN método determinista; predicción sin reconciliación (números de secuencia + re-aplicar pendientes) es rubber-banding garantizado.
8. Personaje propio: predicción u owner-authority. Los demás: interpolación (llegan ~1 tick tarde — es correcto, no lo "arregles" extrapolando a ciegas).
9. Hit-scan competitivo necesita lag compensation (historial por tick + rewind en el server); asume el trade-off del tiro tras cobertura.
10. Bandwidth de `NetworkTransform`: solo ejes usados + thresholds + half-float + quaternion compression; el Network Profiler dice qué objeto se come el ancho de banda.
11. `string` no existe en NetworkVariables: `FixedString32Bytes`+ y structs `INetworkSerializable`.
12. Spawns en ráfaga (balas, VFX) → pooling de red (`INetworkPrefabInstanceHandler`), nunca Instantiate/Destroy pelado [ver: unity/csharp-patrones].
13. Co-op solo-dev: `StartHost()` + Sessions/Relay con join code — cero infra propia; proyectos nuevos usan el Multiplayer Services SDK (Sessions), no los SDKs sueltos de Lobby/Relay.
14. Lógica de datos sin física (cartas, turnos, economía) → server propio HTTP/WS antes que Unity headless.
15. Leaderboard/ghost/turno: el server valida y calcula TODO resultado; el cliente jamás reporta "gané X".
16. Testea cada feature de red con Network Simulator a 150+ ms y packet loss, y con un late-joiner, ANTES de marcarla hecha; localhost miente.
17. MPPM para iterar multi-cliente en Editor; bots headless para probar más de 4 jugadores y dejar el server corriendo horas.
18. Suscripciones de red (`OnValueChanged`, `OnListChanged`, callbacks del NetworkManager) se pares en `OnNetworkSpawn`/`OnNetworkDespawn` — misma disciplina de eventos de [ver: unity/csharp-patrones].
19. Intenta hacer trampa en tu propio juego una tarde entera; cada exploit encontrado es una validación que faltaba.
20. Presupuesta el multijugador como servicio (hosting, soporte, parches de seguridad, población), no como feature que se termina [ver: produccion-solo-dev].

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| "Lo hago single-player y luego le meto online" | El netcode reescribe la arquitectura de gameplay; decidir capa el día 1 [ver: gamedev/generos] |
| Confiar en el cliente "porque es co-op entre amigos"… y luego escalar a ranked | La autoridad no se migra fácil: si hay CUALQUIER chance de competitivo/dinero, server-auth desde el inicio |
| RPC como estado (el late-joiner entra a un mundo vacío) | Test del late-joiner: todo lo que debe ver al entrar vive en NetworkVariables / estado spawneado |
| NetworkVariable como evento (cambios intermedios perdidos, "a" y "b" llegan en ticks distintos) | Eventos → RPC (params atómicos, reliable en orden) |
| Predicción sin reconciliación → el jugador "rebota" hacia atrás con lag | Números de secuencia + reset al estado del server + re-aplicar inputs pendientes (Gambetta II) |
| Extrapolar la posición de otros jugadores para "eliminar" el retraso | Interpolar entre los 2 últimos snapshots (movimiento real); el retraso de 1 tick es el diseño correcto |
| Desarrollar y probar solo en localhost | Network Simulator con presets móviles + packet loss en cada sesión de prueba; el bug de red no reproducible en LAN es lo normal, no la excepción |
| `Instantiate` sin `Spawn()` ("en mi pantalla sí está") | Todo objeto de red: Instantiate + `NetworkObject.Spawn()` en el server; verificar en una segunda instancia (MPPM) |
| Validar identidad con un playerId que manda el propio cliente | `rpcParams.Receive.SenderClientId` — la identidad la da el transporte, no el payload |
| Owner-authority en TODO por comodidad (posición, vida, score) | Owner-authority solo en presentación/movimiento casual; vida, economía y resultados siempre server-write |
| Leaderboard que acepta el score que reporta el cliente | El server recalcula o al menos sanity-checkea (tiempo mínimo posible, deltas imposibles); replay/inputs como evidencia en juegos serios |
| Mandar al cliente datos que no debe ver ("igual la UI no los muestra") | Wallhack = datos tuyos: interest management, visibilidad por objeto, `ReadPermission.Owner` |
| Elegir librería por hype y descubrir a mitad que falta CSP/lag comp | Tabla sección 2: NGO no trae CSP; Mirror la tiene en research; FishNet la trae (lag comp = Pro). Casarla con el tipo de juego ANTES |
| Probar solo el happy path de conexión | Matriz: late-join, reconexión, host que muere sin avisar, 150 ms + loss. Cada celda un test real |
| Cliente modificado que spamea RPCs válidos (rate abuse) | Rate limit por cliente en server + log + kick; `RpcDelivery.Unreliable` para lo tolerante a pérdida |
| Física local peleando con NetworkTransform (jitter en clientes) | En clientes no-autoridad el rigidbody no simula esa entidad: kinematic/sync desde red [ver: unity/fisica-unity] |

## Fuentes

- **Fast-Paced Multiplayer, partes I-IV — Gabriel Gambetta** (gabrielgambetta.com/client-server-game-architecture.html y siguientes) — el canon motor-agnóstico completo: server autoritativo, predicción+reconciliación con números de secuencia, entity interpolation (render en el pasado), lag compensation con rewind. Las 4 partes leídas y destiladas en la sección 1.
- **MultiplayerNetworkingResources — 0xFA11 (GitHub)** — repo curado de referencia para profundizar: Gaffer on Games (Fiedler), Valve Source Multiplayer Networking, GGPO/rollback (Cannon, Pusch), Overwatch GDC (Ford), Rocket League GDC (Cone), "1500 Archers" (Age of Empires), determinismo (LoL).
- **Netcode for GameObjects 2.13 — docs oficiales Unity** (docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13) — páginas leídas: about (versión/requisitos Unity 6.0+), rpcvnetvar (criterio estado vs evento y test del late-joiner), rpc ([Rpc], SendTo, RpcParams, delivery, InvokePermission), networkvariable (permisos, OnValueChanged, tipos, NetworkList), networktransform (autoridad, interpolación, half-float, quaternion compression), object-spawning (Spawn/Despawn/InstantiateAndSpawn), ownership (client-server vs distributed authority), networkmanager (Start*, ConnectionApproval, SetConnectionData/SetHostRelayData), networktime-ticks (LocalTime/ServerTime, NetworkTickSystem, batching por tick). El default de `TickRate` (30) no aparece en esas páginas de manual; verificado directo en el código fuente (`NetworkConfig.cs`, repo `Unity-Technologies/com.unity.netcode.gameobjects`, rama `develop`): `public uint TickRate = 30`.
- **Unity Relay — docs UGS** (docs.unity.com/ugs/manual/relay) — join codes, relay como proxy universal, sin dedicated server ni NAT punchthrough propio.
- **Multiplayer Services SDK / Sessions — docs UGS** (docs.unity.com/ugs/en-us/manual/mps-sdk/manual) — Sessions unifica Lobby+Matchmaker+Relay; vía recomendada 2026 para proyectos nuevos, con ruta de migración desde los SDKs sueltos.
- **Multiplayer Play Mode 3.0 — docs oficiales Unity** (docs.unity3d.com/Packages/com.unity.multiplayer.playmode@3.0) — 4 players de Editor + 4 builds locales, requisito Unity 6.3 LTS, límites de los players virtuales.
- **Multiplayer Tools 2.2 — docs oficiales Unity** (docs.unity3d.com/Packages/com.unity.multiplayer.tools@2.2) — Network Simulator (presets 2G-5G/broadband, jitter/loss/scenarios), Network Profiler, Runtime Net Stats Monitor, Scene Visualization; Unity 6000.0+.
- **Mirror Networking — README oficial (GitHub MirrorNetworking/Mirror)** — MIT, soporte hasta Unity 6000.1, 1000+ juegos Steam, lag compensation Beta, client-side prediction en "researching".
- **FishNet — docs oficiales (fish-networking.gitbook.io)** — gratis sin CCU caps, server-authoritative by design, Unity 6+ full support, "no-break promise"; página Pro: lag compensation (collider rollback), extrapolación y code stripping son Pro; predicción client-side en la doc gratuita.
- **Base propia:** [ver: gamedev/generos] — economía del género multijugador (costo 3-5x, huevo-gallina de población, alternativas solo-dev que este archivo implementa) · [ver: unity/csharp-patrones] — eventos/suscripciones, pooling, async/Awaitable con cancelación que el código de red reutiliza.
