# Animación en Unity

> **Cuando cargar este archivo:** al implementar cualquier animación en Unity 6 + URP — Animator Controllers, blend trees, tweening/juice, Timeline/cutscenes, animación 2D (sprites o esqueletal), IK, o eventos de animación que disparan gameplay. También al decidir QUÉ sistema de animación usar.

## Mapa de decisión rápido

| Necesidad | Herramienta |
|---|---|
| Locomoción de personaje (idle/walk/run/jump) | Animator Controller + blend tree |
| Punch/shake/fade/escala de UI o props (juice) | Tweening (PrimeTween o LitMotion) — NO Animator [ver: gamedev/game-feel] |
| Cutscene/cinemática con varios actores | Timeline + Signals |
| Personaje 2D con pocas frames dibujadas a mano | Frame-by-frame (Animation window / Aseprite Importer) |
| Personaje 2D con muchas animaciones y partes reutilizables | Esqueletal: paquete 2D Animation + PSD Importer (o Spine si hay presupuesto) |
| Mirar/agarrar/apuntar procedural sobre animación existente | Animation Rigging (Two Bone IK, Multi-Aim) |
| Cientos de estados y el grafo se volvió spaghetti | Animancer o Playables API (ver sección Alternativas) |
| Abrir hitbox, sonar footstep en un frame exacto | Animation Event (+ StateMachineBehaviour como red de seguridad) |

---

## 1. Animator Controller

### Parámetros y hashes
- 4 tipos de parámetro: **Float, Int, Bool, Trigger**. Trigger se auto-resetea al consumirse por una transición.
- **Nunca** pasar strings a `SetFloat`/`SetBool`/`Play` en código caliente. `Animator.StringToHash(string)` genera un id CRC32 estable entre sesiones (sirve incluso para networking). Cachear como `static readonly int`:

```csharp
public class PlayerAnimation : MonoBehaviour
{
    static readonly int SpeedHash  = Animator.StringToHash("Speed");
    static readonly int AttackHash = Animator.StringToHash("Attack");
    // Para Play/CrossFade por nombre de estado, incluir la ruta si hay ambigüedad:
    static readonly int BounceState = Animator.StringToHash("Base Layer.Bounce");

    [SerializeField] Animator animator;

    public void Move(float speed) => animator.SetFloat(SpeedHash, speed);
    public void Attack() =>
        // Bypass del grafo: transición directa a un estado, blend 0.1s en segundos reales
        animator.CrossFadeInFixedTime(AttackHash, 0.1f, 0);
}
```

- `CrossFade` usa duración en tiempo normalizado del clip destino; `CrossFadeInFixedTime` en segundos. Para acciones de gameplay casi siempre quieres `CrossFadeInFixedTime`.
- Estado actual: `animator.GetCurrentAnimatorStateInfo(0)` (+ `IsInTransition(0)`). Comparar con `stateInfo.shortNameHash == AttackHash`, no con strings.

### Transiciones (propiedades exactas, Manual Unity 6)
| Propiedad | Comportamiento |
|---|---|
| **Has Exit Time** | La transición depende del tiempo normalizado del clip, no solo de parámetros. Para acciones respondientes a input: **desactivarlo** (si no, el input espera al exit time → sensación de lag) [ver: gamedev/game-feel] |
| **Exit Time** | Tiempo normalizado en que la condición de salida se vuelve true (0.75 = al 75% del clip). En clips con loop: valores <1 se evalúan **cada ciclo**; valores >1 disparan **una sola vez** tras N loops (ej. 3.5 = a mitad del cuarto loop) |
| **Fixed Duration** | Marcado: duración del blend en segundos. Sin marcar: fracción del tiempo normalizado del estado origen |
| **Transition Duration** | Longitud del blend entre estados |
| **Transition Offset** | Punto normalizado donde arranca el clip destino (0.5 = a la mitad) |
| **Conditions** | Múltiples condiciones = AND. Para OR: crear varias transiciones al mismo destino |

### Interruption Source (evita transiciones "que no responden")
Por defecto una transición en curso **no puede interrumpirse**. `Interruption Source` define qué colas de transiciones pueden cortarla:
- `None` | `Current State` | `Next State` | `Current State Then Next State` | `Next State Then Current State`.
- **Ordered Interruption**: activado, solo transiciones con mayor prioridad (más arriba en la lista) que la actual pueden interrumpir; desactivado, cualquiera válida.
- Al interrumpirse, el blend continúa desde una **pose congelada** del momento de la interrupción hacia el nuevo destino (documentado en el blog oficial de Unity "State Machine Transition interruptions", 2016; la página da 403 hoy — comportamiento NO re-verificado en Unity 6, pero es el diseño histórico del sistema).
- Receta práctica combate: transición attack→attack con `Next State` para permitir combos que corten la animación actual.

### Update mode y culling (Inspector del Animator)
- **Update Mode**: `Normal` (por frame), `Animate Physics` (con el paso de física — usarlo si el rig mueve Rigidbodies o el personaje empuja física [ver: fisica-unity]), `Unscaled Time` (ignora `Time.timeScale` — UI durante pausa).
- **Culling Mode**: `Cull Completely` + desactivar `Update When Offscreen` del SkinnedMeshRenderer = cero coste de animación fuera de cámara (recomendación oficial). Ojo: con cull completo, root motion no avanza offscreen.
- Un Animator **sin Controller asignado no procesa nada** — asignar el controller solo cuando haga falta es una optimización válida.
- Al desactivar el GameObject el Animator pierde su estado; el flag **Keep Animator Controller State On Disable** (`Animator.keepAnimatorControllerStateOnDisable`) lo preserva — relevante para pooling [ver: rendimiento-unity].

### Costes (página oficial de optimización de Mecanim)
- Curvas de **escala** son más caras que posición/rotación; curvas constantes se optimizan solas.
- Una layer con **weight 0 se salta** por completo.
- Humanoid: si no usas IK goals o dedos, quítalos con avatar mask. Generic: no asignar root bone si no usas root motion (root motion es lo caro).
- Humanoid vs Generic: Generic es más barato; usar Humanoid solo si necesitas retargeting o IK humanoide.

---

## 2. Blend Trees

Un blend tree mezcla clips **similares** simultáneamente según parámetros (vs transición, que cambia de estado en el tiempo). Requisito clave: los movimientos deben ocurrir en los **mismos puntos de tiempo normalizado** (ej. pie izquierdo apoya en 0.0, derecho en 0.5, en TODOS los clips de locomoción) — si no, el blend "patina".

| Tipo | Cuándo usarlo |
|---|---|
| **1D** | Un solo parámetro (Speed: idle→walk→run). Thresholds ordenados; `Automate Thresholds` los reparte, o computa desde velocidad root |
| **2D Simple Directional** | Un clip por dirección (walk N/S/E/O), máximo uno por dirección + opcional uno en (0,0) (idle) |
| **2D Freeform Directional** | Varias magnitudes por dirección (walk fwd + run fwd). **Obligatorio** un clip en (0,0) |
| **2D Freeform Cartesian** | X e Y son conceptos distintos, no direcciones (ej. velocidad angular vs velocidad lineal) |
| **Direct** | Peso de cada clip controlado directamente por un parámetro — facial/blendshapes, idles aleatorios |

- Posiciones 2D: arrastrar en el diagrama o `Compute Positions` (Velocity XZ, Speed And Angular Speed) que las deriva del root motion de cada clip.
- Patrón estándar third-person: blend tree 2D Freeform Directional con parámetros `VelX`/`VelZ` alimentados con `SetFloat(..., value, dampTime, Time.deltaTime)` para suavizar (la sobrecarga de `SetFloat` con damp time evita snaps).

---

## 3. Layers y Avatar Masks

- Uso típico: layer base = locomoción cuerpo completo; layer superior con **avatar mask** de torso/brazos = disparar/lanzar mientras camina.
- **Blending por layer**: `Override` (reemplaza layers anteriores) o `Additive` (suma encima — los clips deben tener propiedades compatibles; útil para "lean" o respiración).
- **Avatar mask**: en humanoid se marca por partes del cuerpo; en generic por jerarquía de transforms. La "M" en la lista de layers indica máscara activa.
- **Sync layers**: replican la estructura de otra layer con clips distintos (ej. layer "herido" con los mismos estados pero clips cojeando). "S" en la lista. Opción `Timing`: activada, pondera la duración entre layers según weight; desactivada, los clips se estiran a la duración de la layer original.
- Cambiar peso en runtime: `animator.SetLayerWeight(index, weight)` — animarlo con un tween pequeño para que no haga pop.

---

## 4. ¿Animator o animación por código/tweening?

| Señal | Veredicto |
|---|---|
| Movimiento de personaje con clips de artista, blending, retargeting | Animator |
| Escala de botón al hover, shake de cámara, fade, knockback visual, coleccionable flotando | Tween por código — crear un AnimatorController para esto es overkill (asset extra, sin control fino, coste de Animator por objeto) |
| Valores procedurales puros (puerta que abre 90°, plataforma que va y viene) | Tween o `Mathf`/corrutina; Animator solo si el artista necesita editar la curva |
| Necesitas curvas editadas a mano por artista sobre múltiples propiedades | Animation clip (aunque lo dispares con Playables o Animancer) |

Regla: **Animator para personajes y todo lo autorizado por artistas; tweening para feedback y props**. No mezclar los dos sobre la MISMA propiedad del mismo objeto: el Animator escribe cada frame y pisa al tween (si un clip anima `localScale`, un tween de escala sobre ese hueso pierde siempre).

---

## 5. Tweening a 2026: DOTween vs PrimeTween vs LitMotion

| | DOTween (+Pro) | PrimeTween | LitMotion |
|---|---|---|---|
| Estado (jul-2026) | Veterano, soporta Unity 6; core gratis, Pro de pago (editor visual, paths) | v1.4.11, activo, gratis | v2.0.2 (mayo 2026), activo, MIT |
| Allocations | Aloca (734 B por animación, 2.846 B por secuencia en el benchmark de PrimeTween) | **0 B siempre** (salvo async/await, que aloca por C#, no por la lib) | **0 B** al crear motions (structs) |
| Rendimiento | Base de comparación | 2.6–5.2× más rápido que DOTween en tests sintéticos (100k tweens, IL2CPP, M1) — benchmark del propio autor, con sesgo posible | Claim del autor: "2–20× más rápido que otras libs"; usa **Burst + Jobs** (requiere Burst 1.6+, Collections, Mathematics) |
| API | `transform.DOMoveY(10, 1)` (extension methods) | `Tween.PositionY(transform, 10, 1)` (estático, muy descubrible) | `LMotion.Create(a, b, dur).WithEase(...).Bind(...)` (builder, más verboso) |
| Secuencias | Sí | Sí (Chain/Group, 0 alloc) | Sí (añadidas en v2) |
| Extras | Ecosistema enorme, mucho tutorial | Adapter de migración desde DOTween + cheatsheet; `TweenSettings` serializables en Inspector | Integración UniTask/R3, anim de texto, punch/shake |
| Unity mínimo | 2020.3+ vía descarga directa (2022.3+ si es desde Asset Store) | sin mínimo estricto publicado; el README solo aclara que `TweenSettings` genérico serializable en Inspector requiere 2020.1+ (versiones más viejas: usar el `TweenSettings` no genérico) | 2021.3+ (requiere Burst 1.6+, Collections 1.5.1+, Mathematics) |

**Criterio de elección:**
- Proyecto nuevo, prioridad juice + simplicidad → **PrimeTween** (API descubrible, cero alloc, sin dependencias).
- Miles de tweens simultáneos o proyecto ya usa Burst/DOTS/UniTask → **LitMotion**.
- Equipo ya domina DOTween o necesita su editor visual (Pro) → quedarse, pero cachear tweens y usar `SetAutoKill(false)` + `Restart()` para no alocar por uso.
- Los tres conviven mal entre sí sobre la misma propiedad — elegir **una** lib por proyecto.

```csharp
// PrimeTween — juice de daño, cero allocs [ver: gamedev/game-feel]
Tween.PunchScale(transform, strength: Vector3.one * 0.3f, duration: 0.25f);
Tween.ShakeCamera(mainCamera, strengthFactor: 0.4f);
Sequence.Create()
    .Chain(Tween.PositionY(transform, transform.position.y + 1f, 0.3f, Ease.OutQuad))
    .Chain(Tween.Scale(transform, 0f, 0.15f, Ease.InBack));
```

Siempre matar/completar tweens al destruir o poolear el objeto (`Tween.StopAll(onTarget: transform)` en PrimeTween; `DOTween.Kill(transform)` en DOTween) — tweens huérfanos sobre objetos destruidos son la fuente #1 de excepciones con tweening.

---

## 6. Timeline: cinemáticas, cutscenes, signals

Paquete `com.unity.timeline` (docs verificadas: 1.8.12). Un **Timeline asset** (tracks + clips) se reproduce vía **PlayableDirector** en escena; los bindings de cada track (qué Animator, qué AudioSource) viven en el director, no en el asset — el mismo asset sirve para varios actores.

- Tracks principales: **Animation** (anima directamente o sobre un Animator; permite grabar keyframes en el propio Timeline), **Activation** (activa/desactiva GameObjects durante un rango), **Audio**, **Control** (reproduce otro PlayableDirector o partículas anidadas). Cinemachine 3.x añade su track para cortes de cámara.
- El PlayableDirector con `Play On Awake` + `Wrap Mode` (Hold/Loop/None) cubre la mayoría de cutscenes; para gameplay: `director.Play()`, `director.stopped +=` para saber cuándo terminó.

### Signals (Timeline → gameplay)
Tres piezas:
1. **Signal Asset** (`.signal`): identidad reutilizable de la señal.
2. **Signal Emitter**: marker en un track, en el frame exacto donde dispara (con warning icon hasta asignarle asset).
3. **Signal Receiver** (componente en el GameObject bindeado al track): tabla signal → reaction (UnityEvent — ej. `AudioSource.Play()`). Se crea solo al añadir la primera señal.

Opciones del emitter (ambas off por defecto): **Retroactive** (dispara si el playhead ya pasó el marker al empezar a reproducir — actívalo para señales de estado tipo "puerta ya abierta" al saltar la cutscene) y **Emit Once** (no repite en loops).

Criterio Timeline vs Animator: Timeline = secuencias **autoradas en el tiempo** con múltiples objetos; Animator = comportamiento **reactivo a estado/input**. No construir lógica de gameplay en Timeline.

---

## 7. Animación 2D: frame-by-frame vs esqueletal vs Spine

| | Frame-by-frame (sprites) | 2D Animation (Unity, esqueletal) | Spine (Esoteric) |
|---|---|---|---|
| Coste de producción | Alto por frame dibujado; cada animación nueva = dibujar todo | Rig una vez, animar huesos; reusar animaciones entre skins | Como esqueletal + editor dedicado muy superior (mesh deform, curvas) |
| Coste de runtime | Casi nulo (swap de sprite); memoria/atlas crece con nº de frames [ver: rendimiento-unity] | Deformación por vértices: **CPU deformation** (dynamic batching, para muchos objetos low-poly) o **GPU deformation** (solo URP, SRP Batcher — para pocos objetos high-poly) [ver: rendering-urp] | Runtime spine-unity, deformación CPU; muy optimizado pero dependencia externa |
| Coste de licencia | 0 | 0 (paquetes oficiales) | Por persona: Essential $69 / Professional $379 (precios vistos jul-2026, rebajados de $99/$449); Enterprise $2.499 + $379/usuario/año OBLIGATORIO si la empresa factura ≥ $500k/año. Integrar el runtime en productos nuevos exige licencia de editor vigente |
| Estilo resultante | Cualquier estilo, el más expresivo | "Marioneta": se nota en giros de perspectiva; mitigable con sprite swap | Ídem + mesh deformation lo disimula mejor |

**Stack oficial Unity (verificado):**
- **2D Animation** (10.x, requiere 2023.1+): Skinning Editor (huesos, weights, geometría) dentro del Sprite Editor; componente **Sprite Skin** deforma el sprite con Transforms como huesos; IK 2D incluido; **Sprite Library + Sprite Resolver** para sprite swap (skins, cambiar la mano según el ángulo).
- **PSD Importer**: importa `.psb` de Photoshop, genera un prefab de sprites por capa ("actor") listo para riggear — el artista mantiene el PSD, Unity re-importa.
- **Aseprite Importer** (oficial; 1.1.x para Unity 6.0, 1.2.x para 6.1; preinstalado en proyectos 2D nuevos desde 2023.2): importa `.ase/.aseprite` y genera clips + Animator Controller en modo Animated Sprite. La vía más barata para frame-by-frame.
- Frame-by-frame manual: keyframes de `SpriteRenderer.sprite` en la Animation window. Para elegir dirección de sprite en top-down, muchas veces es más simple un script que setea el sprite según el vector de movimiento que un blend tree.

**Elección:** pixel art / pocas frames → frame-by-frame (Aseprite). Personaje de alta resolución con muchas animaciones y skins → 2D Animation + PSD Importer. Solo pagar Spine si el equipo de arte ya lo domina o necesita mesh deformation seria — y presupuestar las licencias por persona.

---

## 8. Animation Rigging e IK

### IK humanoide built-in (sin paquetes)
Solo rigs **Humanoid**, activar `IK Pass` en la layer del Animator:

```csharp
void OnAnimatorIK(int layerIndex)
{
    animator.SetIKPositionWeight(AvatarIKGoal.LeftHand, grabWeight);
    animator.SetIKPosition(AvatarIKGoal.LeftHand, handle.position);
    animator.SetLookAtWeight(0.7f);
    animator.SetLookAtPosition(target.position);
}
```
Suficiente para: manos a un volante/arma, pies en escalones, mirar al jugador. Interpolar los weights (no 0→1 seco).

### Paquete Animation Rigging (1.3.1, Unity 2023.2+; corre sobre C# Animation Jobs)
Setup: `RigBuilder` en la raíz del Animator → hijo con componente `Rig` → hijos con constraints. Cada constraint y cada Rig tiene `weight` 0–1 animable/tweeneable en runtime (así se enciende/apaga el efecto suavemente).

Constraints incluidos: **Two Bone IK** (brazos/piernas — el caballo de batalla), **Multi-Aim** (cabeza/torso/arma apuntando), **Chain IK** (colas, tentáculos), **Damped Transform** (movimiento secundario con retardo: antenas, pelo), **Multi-Parent**, Multi-Position, Multi-Rotation, Multi-Referential, Override Transform, Twist Correction, Twist Chain, Blend Constraint.

Receta apuntado de arma: layer de disparo con avatar mask + Multi-Aim en columna/cabeza hacia el target + Two Bone IK de la mano de apoyo al guardamanos del arma. Incluye **Bidirectional Motion Transfer** para hornear el resultado del rig a keyframes y viceversa.

---

## 9. Eventos de animación: frames que disparan gameplay

En la Animation window (o en el importer del FBX, pestaña Animation → Events): botón Event en el playhead o click derecho en la línea de eventos.

- Firma: método **público con 0 o 1 parámetro** de tipo `float`, `int`, `string`, referencia a Object o `AnimationEvent` (este último transporta float+int+string+object a la vez).
- El método debe existir en un **MonoBehaviour del MISMO GameObject que el Animator** (dispatch estilo SendMessage). Si no existe → error "has no receiver" en runtime.

```csharp
// Componente junto al Animator. Los nombres se referencian desde el clip.
public void AE_Footstep() => footsteps.PlayRandom();      // [ver: gamedev/audio]
public void AE_HitboxOpen() => attackHitbox.enabled = true;
public void AE_HitboxClose() => attackHitbox.enabled = false;
```

Gotchas críticos (y su antídoto en Errores comunes):
- Un evento en los **últimos frames** puede no dispararse si una transición sale del estado antes de llegar a él.
- Durante un crossfade, los clips de **ambos** estados tienen peso y sus eventos disparan.
- Por eso: los eventos que ABREN algo (hitbox, invulnerabilidad) deben tener su CIERRE garantizado por un `StateMachineBehaviour`, no por otro evento:

```csharp
public class AttackStateCleanup : StateMachineBehaviour
{
    public override void OnStateExit(Animator animator, AnimatorStateInfo info, int layerIndex)
        => animator.GetComponent<PlayerCombat>().CloseHitbox(); // corre SIEMPRE, aun interrumpido
}
```

`OnStateEnter/Exit/Update` de `StateMachineBehaviour` son el hook fiable por-estado; los Animation Events son el hook fiable por-frame. Usar ambos según la garantía que necesites.

---

## 10. Alternativas al Animator (nivel mención)

El grafo del Animator escala mal: con decenas de estados, las transiciones se vuelven inauditables y cada cambio es riesgo de romper otra ruta. Opciones cuando eso pasa:

- **Animancer** (kybernetik.com.au, v8.4): reproduce clips directamente desde código (`animancer.Play(clip, fadeDuration)`) sin AnimatorController; blending, layers, mixers (equivalente a blend trees) y eventos propios definidos en C#, donde el flujo de estados vive en TU state machine [ver: csharp-patrones]. Lite gratis (evaluación en editor), Pro de pago con código fuente. Modo híbrido: convive con un AnimatorController existente para migrar gradual.
- **Playables API** (nativo): construir el `PlayableGraph` a mano — blending dinámico de clips en runtime, reproducir un clip sin controller, control de pesos por frame. Es lo que Animancer y Timeline usan por debajo. Potente pero de bajo nivel (gestión manual de graphs y su destrucción); úsalo para sistemas propios (ej. montador de combos data-driven), no para el caso general.

Para el 90% de los juegos: Animator con grafos PEQUEÑOS (por miembro/por capa, sub-state machines) + `CrossFadeInFixedTime` desde código para acciones puntuales evita el spaghetti sin dependencias.

---

## Reglas practicas

1. Cachear TODOS los parámetros del Animator como `static readonly int` con `Animator.StringToHash`; cero strings en Update.
2. Acciones que responden a input: transiciones con **Has Exit Time OFF** y Transition Duration corta (0.05–0.15s); exit time solo para encadenados naturales (attack→idle).
3. Combos/cancels: configurar **Interruption Source** (típicamente `Next State`) — el default no interrumpible es la causa #1 de "el personaje no responde".
4. `SetTrigger` que puede no consumirse (estado equivocado, transición no disponible): acompañar de `ResetTrigger` al salir del contexto, o usar Bool.
5. Un tween y un clip de animación NUNCA sobre la misma propiedad del mismo transform.
6. Elegir UNA lib de tweening por proyecto; para proyecto nuevo en 2026: PrimeTween (simplicidad) o LitMotion (escala/Burst).
7. Matar los tweens del objeto en `OnDestroy`/al devolverlo al pool.
8. Blend trees de locomoción: verificar que todos los clips pisan en el mismo tiempo normalizado; si no, reeditar los clips, no "compensar" con thresholds.
9. Blend 2D: Freeform Directional para locomoción con walk+run; Cartesian cuando X/Y no son direcciones; SIEMPRE clip en (0,0) en los Freeform.
10. Layers: peso 0 = gratis; apagar layers no usadas bajando weight, y animar el weight al activarlas.
11. Animators fuera de cámara: Culling Mode `Cull Completely` + `Update When Offscreen` off en el SkinnedMeshRenderer.
12. No animar escala si se puede evitar (curvas de escala son las más caras).
13. Todo evento que ABRE (hitbox, i-frames) tiene cierre garantizado en `OnStateExit` de un StateMachineBehaviour.
14. No colocar Animation Events en el último 10% del clip si el estado tiene transiciones de salida antes del final.
15. Cutscenes: Timeline + Signals; signals de estado con `Retroactive` ON para que saltarse la cutscene deje el mundo consistente.
16. 2D: Aseprite Importer para frame-by-frame; 2D Animation + PSD Importer para esqueletal; Spine solo con presupuesto de licencias por persona.
17. Sprite Skin en URP: probar GPU deformation con pocos personajes high-poly, CPU deformation con multitudes low-poly — y decidir con el Profiler, no por intuición.
18. IK simple en Humanoid: `OnAnimatorIK` con IK Pass; IK sobre Generic o procedural serio: Animation Rigging (Two Bone IK + Multi-Aim), pesos siempre interpolados.
19. Pooling de personajes animados: activar Keep Animator Controller State On Disable o resetear el estado explícitamente al sacar del pool.
20. Si el grafo pasa de ~20 estados por layer: sub-state machines primero; si aun así duele, evaluar Animancer/Playables antes de seguir pariendo transiciones.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Input "se come" porque la transición espera al final del clip | Has Exit Time OFF en transiciones disparadas por parámetros |
| Trigger queda armado y dispara la animación mucho después | `ResetTrigger` al cambiar de contexto, o Bool en vez de Trigger |
| Transición no interrumpible → el ataque no se puede cancelar | Interruption Source = Next State (u ordenada) en esa transición |
| `Animator.Play("Attack")` con string en cada llamada | Hash cacheado; y `CrossFadeInFixedTime` para que no haga snap |
| Blend de locomoción "patina" (foot sliding) | Clips sincronizados en tiempo normalizado + thresholds computados desde velocidad real, no a ojo |
| Tween de UI sigue corriendo tras destruir el panel → excepción | Kill/Stop de los tweens del target en OnDestroy; en PrimeTween `Tween.StopAll(onTarget:)` |
| Animator pisa el tween cada frame (el objeto "no se mueve") | La propiedad la anima un clip: quitar la curva del clip o tweenear otro transform padre/hijo |
| Evento de animación no dispara (salió del estado antes) | Evento más temprano en el clip + cierre garantizado en OnStateExit |
| "has no receiver" al reproducir un clip con eventos | El método debe ser público, 0–1 parámetro, en un componente del MISMO GameObject del Animator |
| Eventos duplicados durante crossfade (dos footsteps a la vez) | Eventos idempotentes o gate por estado (chequear `shortNameHash` antes de actuar) |
| Cutscene salteada deja puertas/estado del mundo a medias | Signals con Retroactive ON para todo lo que cambia estado persistente |
| Timeline no afecta al personaje (binding perdido) | Los bindings viven en el PlayableDirector de la escena, no en el asset — verificar el binding tras duplicar/instanciar |
| Additive layer deforma el modelo de forma rara | Los clips additive deben crearse respecto a una pose de referencia y tener propiedades compatibles; si no, usar Override + mask |
| Comprar Spine Essential para un estudio que factura ≥ $500k | La licencia obliga a Enterprise ($2.499 + $379/usuario/año); presupuestarlo ANTES de adoptar el runtime |
| Pooled enemy reaparece con la animación del que murió | Keep Animator Controller State On Disable + `Play(idleHash, 0, 0f)` al respawnear |
| Root motion no avanza cuando el personaje sale de cámara | Es el culling `Cull Completely`: usar `Cull Update Transforms` (o Always Animate) en agentes que deben seguir moviéndose |

## Fuentes

- Animation transitions — Unity Manual 6000.2 (`class-Transition.html`) — propiedades exactas de transiciones, exit time e interruption sources.
- Blend Trees / 2D Blending — Unity Manual 6000.2 (`class-BlendTree.html`, `BlendTree-2DBlending.html`) — tipos de blend 2D y cuándo usar cada uno, Compute Positions.
- Animation Layers — Unity Manual 6000.2 (`AnimationLayers.html`) — override/additive, masks, sync layers y Timing.
- Animator.StringToHash — Unity Scripting API 6000.2 — CRC32, estabilidad entre sesiones, ejemplo oficial.
- Animation Events — Unity Manual 6000.2 (`script-AnimationWindowEvent.html`) — firmas soportadas y flujo en la Animation window.
- Performance and optimization (Mecanim) — Unity Manual 6000.2 — culling, coste de curvas de escala, layers weight 0, humanoid vs generic.
- Playables API — Unity Manual 6000.2 (`Playables.html`) — PlayableGraph y ventajas sobre el state machine.
- Timeline 1.8.12 — docs del paquete (`index`, `toc`, `wf-signals.html`) — Signal Asset/Emitter/Receiver, Retroactive, Emit Once, tipos de track.
- 2D Animation 10.x — docs del paquete (índice y `SpriteSkin.html`) — rigging 2D, Sprite Skin, CPU vs GPU deformation (URP), integración PSD Importer (.psb → prefab "actor").
- Aseprite Importer 1.1/1.2 — docs del paquete — importación .ase/.aseprite, generación de clips/controller, matriz de compatibilidad con Unity 6.0/6.1.
- Animation Rigging 1.3.1 — docs del paquete (índice y `ConstraintComponents.html`) — los 12 constraints, C# Animation Jobs, Bidirectional Motion Transfer, compatibilidad 2023.2+.
- PrimeTween — GitHub KyryloKuzyk/PrimeTween (README v1.4.11 + discussion #10) — zero-alloc, API, benchmarks con números (0 B vs 734 B/2.846 B de DOTween; test sintético del autor).
- LitMotion — GitHub annulusgames/LitMotion (README, v2.0.2 mayo 2026) — claim 2–20× vs otras libs, Burst/Jobs, secuencias en v2, requisitos.
- DOTween — dotween.demigiant.com — soporte declarado "Unity 6 y anteriores hasta 2020.3", core gratis vs Pro.
- Spine purchase — esotericsoftware.com/spine-purchase — precios por persona vistos jul-2026 y umbral Enterprise de $500k de facturación.
- Animancer — kybernetik.com.au/animancer (v8.4) — reproducción directa de clips sin controller, Lite vs Pro, modo híbrido.
