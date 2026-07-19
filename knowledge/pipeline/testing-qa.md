# Testing y QA de juegos en Unity

> **Cuando cargar este archivo:** al montar tests en un proyecto Unity (Unity Test Framework, asmdefs de test, mocks de tiempo/input), al decidir qué merece test y qué no, antes de cada release (smoke tests + pase de QA manual), o al instrumentar un playtest con analytics.

Archivo puente: une el proceso de QA/playtesting de [ver: gamedev/produccion-proceso] con la técnica de [ver: unity/unity-mcp-flujo] y [ver: unity/gotchas-unity]. Aquí está el CÓMO concreto en Unity: qué testear, cómo estructurarlo, y los pases de verificación por release. Verificado contra Unity Manual 6000.2 y package `com.unity.test-framework` 1.8.x (julio 2026); para Unity 6.2+ la guía del Test Framework vive dentro del Manual, no en docs del package. El número exacto de versión que trae un proyecto nuevo depende del Package Manager en el momento — confirmar ahí, no asumir un patch fijo.

---

## 1. Qué testear en un juego chico (y qué no)

El presupuesto de testing de un equipo de 1 es finito. Regla de oro: **test automatizado para lo que es lógica; playtest humano para lo que es experiencia**. El playtesting (protocolo, cadencia, preguntas) está en [ver: gamedev/produccion-proceso] — esto de aquí es lo que corre solo.

| Sí testear (ROI alto) | Por qué |
|---|---|
| Lógica de gameplay pura: daño, cooldowns, reglas de combate, estados de partida (win/lose), scoring | Determinista, se rompe en silencio con cada refactor, y es el corazón del juego |
| Economía interna: precios, drops, curvas de XP, income/sinks | Un `[Test]` puede simular 10.000 iteraciones del loop y detectar inflación o balances negativos que un humano tardaría horas en ver [ver: gamedev/mecanicas-sistemas] |
| Save/load: round-trip completo, migración de versiones de save, archivo corrupto | El bug de save es el que borra el progreso del jugador — el peor bug shippeable |
| Generación procedural: mismo seed → mismo output; invariantes (siempre hay salida, N enemigos en rango) | Sin tests, un cambio en el generador rompe niveles que nunca verás a mano |
| Parsers/datos: tablas de loot, configs, diálogos, localización cargando sin claves rotas | Datos rotos fallan en runtime frente al jugador, no en compilación |
| Regresiones: 1 test por cada bug no trivial arreglado | El bug que volvió dos veces es el que merece test perpetuo |

| No compensa automatizar | Qué usar en su lugar |
|---|---|
| Game feel, juice, "se siente bien" | Playtest humano + criterio [ver: gamedev/game-feel] [ver: feel-en-unity] |
| Visuales, layouts, animaciones "se ven bien" | Ojos (screenshot + humano); el test solo puede verificar que el objeto existe |
| Balance subjetivo (¿es divertido?, ¿muy difícil?) | Playtest con testers frescos + telemetría (§8) |
| Flujos de UI completos click a click | Smoke test manual de 10 min (§7); automatizar UI en Unity es caro y frágil para un dev solo |

## 2. Separar lógica de motor: el patrón humble object

El obstáculo #1 para testear en Unity: la lógica vive dentro de `MonoBehaviour`, que necesita un GameObject, una escena y el lifecycle del motor. La solución es el patrón **humble object** (origen: *xUnit Test Patterns*, Gerard Meszaros, 2007 — atribución estándar; la fuente web no estuvo accesible en esta sesión): extraer la lógica a una **clase C# pura** y dejar el MonoBehaviour como cáscara delgada que solo traduce entre el motor y la lógica.

```csharp
// Clase PURA — testeable sin escena, sin GameObject, sin Unity corriendo
public class HealthModel
{
    public int Current { get; private set; }
    public int Max { get; }
    public bool IsDead => Current <= 0;
    public event System.Action<int> Damaged;

    public HealthModel(int max) { Max = max; Current = max; }

    public void TakeDamage(int amount)
    {
        if (IsDead || amount <= 0) return;
        Current = System.Math.Max(0, Current - amount);
        Damaged?.Invoke(amount);
    }
}

// Humble object — solo cablea el motor con el modelo; casi no hay nada que testear aquí
public class PlayerHealth : MonoBehaviour
{
    [SerializeField] int maxHealth = 100;
    public HealthModel Model { get; private set; }

    void Awake() => Model = new HealthModel(maxHealth);
    void OnTriggerEnter(Collider other)
    {
        if (other.TryGetComponent<DamageSource>(out var dmg))
            Model.TakeDamage(dmg.Amount);
    }
}
```

Reglas del patrón:
- La lógica pura recibe sus dependencias **por parámetro o constructor**, nunca las busca (`GameObject.Find`, `Time.deltaTime` directo). El tiempo entra como argumento: `Tick(float dt)` — eso hace la clase 100% determinista (§5).
- En la clase pura: `?.`/`??` permitidos (es C# puro). En el MonoBehaviour: prohibidos sobre tipos Unity [ver: unity/gotchas-unity] §1.
- Ubicación: la lógica pura vive en `Code/Runtime` (asmdef `Game.Core` idealmente sin depender de `UnityEngine`) según la plantilla de [ver: estructura-proyecto]; eso permite tests EditMode instantáneos.
- No conviertas TODO en humble object por dogma: extrae donde hay reglas (combate, economía, progresión); el script que solo mueve un transform no necesita modelo.
- ScriptableObjects como contenedores de datos/config también se benefician: la lógica que los consume recibe los DATOS, no el asset [ver: unity/csharp-patrones].

## 3. Unity Test Framework: setup y estructura

**Versiones:** el package `com.unity.test-framework` (UTF) corre sobre NUnit; a julio 2026 la versión vigente en el registro es 1.8.x (confirmar la que trae tu Package Manager — el patch exacto cambia con actualizaciones del package, no de Unity). En Unity 6.2+ su guía de usuario está integrada en el Manual (`docs.unity3d.com/6000.2/Documentation/Manual/test-framework/`).

### EditMode vs PlayMode

| | EditMode | PlayMode |
|---|---|---|
| Dónde corre | Solo en el editor, en el loop `EditorApplication.update` | En play mode del editor **o en un player** (device real) |
| Acceso | `UnityEditor` + `UnityEngine` | Solo runtime (sin `UnityEditor`) |
| `[UnityTest]` | Solo puede `yield return null` (no corre coroutines de runtime) | Corre como coroutine real: `yield return null`, `WaitForSeconds`, `WaitForFixedUpdate` |
| Úsalo para | Lógica pura (humble objects), tooling de editor, validación de assets | Gameplay real: física, lifecycle, coroutines, input simulado |
| Velocidad | Instantáneo | Entra a play mode (domain reload) — más lento |

Regla de decisión (docs oficiales): **preferir `[Test]` (NUnit síncrono) salvo que necesites saltar frames o control de timing** — entonces `[UnityTest]`. La mayoría de los tests de un juego bien separado (§2) son `[Test]` EditMode sobre clases puras.

### Asmdefs de test

Estructura (encaja con la plantilla de [ver: estructura-proyecto]):

```
Assets/_Game/Code/
  Runtime/   Game.Core.asmdef, Game.Gameplay.asmdef
  Tests/
    EditMode/   Game.Tests.EditMode.asmdef   (platform: Editor only)
    PlayMode/   Game.Tests.PlayMode.asmdef   (platform: Any/las que toque)
```

- Crear con el Test Runner (**Window > General > Test Runner > Create a new Test Assembly Folder**) o `Assets > Create > Testing > Test Assembly Folder` — genera el asmdef con las referencias correctas: `nunit.framework.dll`, `UnityEngine.TestRunner`, y `UnityEditor.TestRunner` (esta última **solo** para EditMode).
- Añadir a mano la referencia al asmdef del código de juego (`Game.Core`, `Game.Gameplay`). **Los tests no pueden referenciar `Assembly-CSharp`** (el assembly implícito): si el código de juego no tiene asmdef propio, no es testeable desde un player — otra razón para la estructura de [ver: estructura-proyecto].
- Plataformas del asmdef de test: default "Editor only"; para correr PlayMode tests en device, marcar las plataformas objetivo.

### Testear MonoBehaviours y escenas

- **Primera opción: no lo hagas** — testea el modelo puro (§2) en EditMode.
- Cuando el comportamiento del motor ES lo que pruebas (física, triggers, lifecycle): PlayMode test que construye su mini-mundo — `new GameObject(...)` + `AddComponent`, o instanciar un prefab — y lo destruye al final. Snippet completo en [ver: unity/unity-mcp-flujo] §5.
- `yield return null` tras crear objetos para que corran `Awake`/`Start`; `yield return new WaitForFixedUpdate()` para que la física simule un paso (ejemplo oficial del atributo `[UnityTest]`).
- Cargar escenas completas en tests es frágil (dependencias implícitas, tiempos de carga): resérvalo para 1–2 smoke tests de boot; el resto construye contexto mínimo.
- **`LogAssert`** (`UnityEngine.TestTools`): un test falla si el código loguea un error/excepción/assert inesperado. `LogAssert.Expect(LogType.Error, "mensaje")` ANTES de ejecutar el código que lo produce; `LogAssert.NoUnexpectedReceived()` para afirmar silencio; `LogAssert.ignoreFailingMessages = true` solo como último recurso.
- Cobertura: package `com.unity.testtools.codecoverage` (1.3.x a julio 2026, mínimo Unity 2021.3) genera reporte HTML de qué líneas ejecutan los tests. Úsalo para encontrar lógica crítica sin cubrir, no para perseguir un %.

## 4. Mocks de input

Con el Input System nuevo [ver: unity/input-system] el input se simula de verdad con **`InputTestFixture`**:

- Setup: añadir `"com.unity.inputsystem"` al array `testables` de `Packages/manifest.json`; el asmdef de test referencia `Unity.InputSystem` y `Unity.InputSystem.TestFramework` (además de las de §3).
- La fixture "monta una versión limpia y default del Input System para cada test y restaura el estado original al terminar". Ojo: NO ejecuta `[InitializeOnLoad]` ni `[RuntimeInitializeOnLoadMethod]` — layouts custom se registran a mano en el setup.
- Heredar de `InputTestFixture`; si necesitas setup propio, override de `Setup()`/`TearDown()` llamando a `base`.

```csharp
public class JumpInputTests : InputTestFixture
{
    [Test]
    public void SpacePresses_TriggerJumpAction()
    {
        var keyboard = InputSystem.AddDevice<Keyboard>();
        var jump = new InputAction(binding: "<Keyboard>/space");
        jump.Enable();
        bool fired = false;
        jump.performed += _ => fired = true;

        Press(keyboard.spaceKey);      // también: Release, PressAndRelease,
        Assert.IsTrue(fired);          // Set(gamepad.leftStick, new Vector2(1,0)), Trigger(action)
    }
}
```

Para el input del legacy Input Manager no hay fixture oficial — otra razón para el Input System nuevo, o para que la lógica reciba "intents" (`JumpPressed`) en vez de leer input directo (§2).

## 5. Mocks de tiempo y aleatoriedad

Unity no trae un reloj inyectable oficial. Patrones en orden de preferencia:

1. **El tiempo entra por parámetro** (el mejor): la lógica pura expone `Tick(float deltaTime)` y el MonoBehaviour la llama con `Time.deltaTime`. En el test llamas `Tick(0.016f)` mil veces y simulas 16 segundos en microsegundos, determinista.
2. **Interfaz de reloj** para lógica que necesita "ahora" absoluto (cooldowns por timestamp, energía idle): `interface IClock { double Now { get; } }` — producción la implementa con `Time.timeAsDouble` o `DateTime.UtcNow` (para tiempo real fuera de sesión); el test usa un `FakeClock` que avanzas a mano.
3. **`Time.timeScale`** en PlayMode tests para acelerar esperas reales (`WaitForSeconds` escala con timeScale). Último recurso: acopla el test al reloj real y lo hace lento/flaky.

Aleatoriedad determinista (clave para procgen y para reproducir bugs):
- Inyectar `System.Random` con seed en la lógica pura — nunca `UnityEngine.Random` estático global dentro del modelo (estado compartido invisible entre sistemas). Si algo ya usa el global: `UnityEngine.Random.InitState(seed)` al inicio del test.
- Test de procgen: `Generate(seed: 42)` dos veces → outputs idénticos; y un loop de ~100 seeds asertando invariantes (hay salida, el nivel es transitable, conteos en rango) — property-based casero, barato y caza más bugs que un caso fijo.

Mocks de dependencias (servicios, backends): **NSubstitute** — `Substitute.For<ISaveService>()`, `.Returns(...)`, `.Received()`. Funciona sobre interfaces, que la separación de §2 ya te dio. Integración en Unity: la DLL de NuGet en `Assets/Plugins` es la vía clásica (forma exacta de instalación NO VERIFICADA en esta sesión contra una guía oficial Unity). Para un juego chico, un fake escrito a mano (`class FakeSaveService : ISaveService`) suele bastar y compila sin dependencias.

## 6. Tests corridos por el agente (MCP): el guardián de regresiones

El flujo operativo completo está en [ver: unity/unity-mcp-flujo] (§5: `run_tests` es async — guardar `job_id`, polling con `get_test_job`; el grupo `testing` de tools hay que activarlo). Lo que este archivo añade: **cuándo** los corre el agente.

| Momento | Qué correr |
|---|---|
| Tras cada feature/fix que toca lógica | Suite EditMode (rápida) — es el typecheck del gameplay |
| Antes de declarar "listo" un sistema | EditMode + PlayMode del sistema tocado |
| Antes de CUALQUIER build/release | Suite completa EditMode + PlayMode, cero fallos |
| Tras arreglar un bug no trivial | Escribir el test de regresión PRIMERO (que falle), arreglar, verlo pasar |

Reglas de agente:
- Test rojo = STOP. No se comenta el test, no se baja el assert, no se avanza "porque parece no relacionado". Se arregla el código o —si el test quedó obsoleto por un cambio de diseño real— se actualiza el test declarándolo explícitamente.
- Suite EditMode lenta = suite que no se corre. Presupuesto: segundos, no minutos. PlayMode se reserva para lo que de verdad necesita motor.
- Sin editor MCP conectado, la suite corre por CLI (§7) — mismo veredicto, misma regla.

## 7. Smoke tests de build: la pasada mínima por release

Un build puede romper lo que el editor corre perfecto: IL2CPP + stripping elimina código, el execution order cambia, los defaults móviles difieren [ver: unity/build-plataformas] [ver: unity/gotchas-unity] §12. Por eso **cada build candidato pasa este smoke ANTES de distribuirse** (~10 min por plataforma):

1. El build compila sin errores nuevos (y sin warnings nuevos de stripping).
2. Arranca hasta el menú principal — sin crash, sin pantalla negra, sin errores en el log del player (desktop: `Player.log`; Android: `adb logcat -s Unity`; iOS: consola de Xcode).
3. Nueva partida → jugar el core loop 2–3 minutos reales.
4. Save → cerrar la app del todo → reabrir → load: el progreso está.
5. Settings básicos: volumen, resolución/calidad, rebinding si existe.
6. Pausa/resume; en móvil: background (Home) → volver; llamada/notificación por encima; lock/unlock [gotchas §12: el estado se guarda en `OnApplicationPause(true)`].
7. Aspect ratio del device en mano: nada cortado por notch/safe area [ver: unity/ui-unity].
8. Performance de ojo: sin hitches obvios en el device más débil soportado; si hay duda, profiler [ver: unity/rendimiento-unity].
9. Quit limpio (y en móvil, batería/térmica tras 10 min si el juego es de sesiones largas).

Automatizable: los PlayMode tests corren **en device real** por CLI — `-runTests -testPlatform Android` (cualquier valor de `BuildTarget`) construye un player de test y lo ejecuta. Flags verificados (Manual 6000.2): `-runTests -batchmode -projectPath <ruta> -testPlatform EditMode|PlayMode|<BuildTarget> -testResults results.xml` (formato NUnit XML), `-testFilter`/`-testCategory` para filtrar, `-forgetProjectPath` para no ensuciar el historial del Hub. **`-quit` no se usa con `-runTests`** (no soportado). Los builds en sí: `manage_build` via MCP o CLI [ver: unity/build-plataformas].

## 8. QA manual sistemático: checklist pre-ship y triage para 1 dev

El smoke (§7) es por build; esto es el pase profundo **una vez por release** (beta/RC — [ver: gamedev/produccion-proceso] para dónde caen esos gates).

**Device matrix mínima (equipo de 1):**

| Slot | Qué | Por qué |
|---|---|---|
| El más débil soportado | El device REAL más viejo/barato que declaras soportar | Si va bien aquí, va bien en todos; el perf target se mide aquí [ver: unity/rendimiento-unity] |
| El mainstream | Un device de gama media actual del público objetivo | Es lo que tendrá la mayoría |
| El del dev | Tu device diario | Ya lo tienes; no cuenta como cobertura, solo como conveniencia |

iOS + Android si shippeas ambos (los gotchas difieren: pause/focus, teclado, safe areas). El Device Simulator del editor (Window > General > Device Simulator) cubre aspect ratios y safe areas en desarrollo, pero **no** sustituye device real para performance, touch, interrupciones ni térmica.

**Matriz de interrupciones móvil** (basada en los checks de Android Core App Quality — aplican igual en iOS):

| Check (ID Android) | Qué verificar |
|---|---|
| `Sleep_Resume` / `Lock_Resume` | El juego pausa al dormir/bloquear el device y resume sin corromper estado |
| `State_Preservation` | Progreso de partida preservado al salir del foreground — incluso si el OS mata el proceso |
| `App_Switcher` | Ir a Recents, cambiar de app, volver: el juego sigue donde estaba |
| `Consistent_UX` (interrupciones) | Llamada entrante, notificación, pérdida de red, batería baja — durante gameplay, sin crash ni estado roto |
| `Audio_Focus_Change` | Otra app pide audio (música, navegación): el juego cede/reduce volumen y lo recupera |

Más: timers al volver del background se recalculan con timestamps reales, no deltaTime acumulado; RenderTextures se regeneran (`IsCreated()`) [ver: unity/gotchas-unity] §12.

**Aspect ratios a cubrir:** 16:9 (desktop/tablet apaisado), 19.5:9–20:9 (móvil moderno con notch), 4:3 (iPad). En cada uno: HUD completo visible, nada bajo el notch, botones alcanzables [ver: unity/ui-unity].

**Bug triage para 1 dev** — una sola lista (archivo `BUGS.md` o issues del repo), cada entrada con pasos de reproducción + device/build, clasificada al capturarla:

| Prioridad | Definición | Política |
|---|---|---|
| P0 | Crash, bloqueo de progresión, save perdido/corrupto | Se arregla YA; bloquea cualquier release |
| P1 | Feature rota o visiblemente mal para la mayoría | Se arregla antes del release en curso |
| P2 | Molestia real pero esquivable | A la lista de corte; entra si sobra presupuesto [ver: gamedev/produccion-proceso] |
| P3 | Cosmético, edge case raro | Probablemente nunca — y está bien |

Regla anti-autoengaño: un bug sin pasos de reproducción no es un bug, es un rumor — se instrumenta (logs, §8) hasta reproducirlo antes de intentar arreglarlo. Y cada fix de P0/P1 no trivial deja un test de regresión (§6).

## 9. Playtesting instrumentado: analytics en builds de prueba

El protocolo humano del playtest (hipótesis, silencio, preguntas) está en [ver: gamedev/produccion-proceso]; la telemetría de producción y el diseño de embudos en [ver: sistemas-meta] y [ver: gamedev/psicologia-retencion-negocio]. Lo mínimo para que un build de playtest genere DATOS además de opiniones:

**Eventos mínimos del embudo** (instrumentar ANTES del primer playtest — la conducta pesa más que lo que el tester dice):

| Evento | Payload | Qué revela |
|---|---|---|
| `session_start` / `session_end` | duración, versión del build | Cuánto aguantan de verdad |
| `tutorial_step` | paso, tiempo en el paso | DÓNDE abandona la gente el onboarding |
| `level_start` / `level_complete` / `level_fail` | nivel, tiempo, causa de muerte | Picos de dificultad reales, no percibidos |
| `quit_point` | escena/estado al cerrar | El último lugar que vieron antes de irse |

**Implementación, dos vías:**
- **UGS Analytics** (Unity Gaming Services): custom events + funnels + dashboards ya hechos. Requiere vincular el proyecto a UGS, cumplir consent/privacidad (obligatorio), y puede tener costo — revisar pricing antes.
- **Log propio** (suficiente para playtests presenciales o de <20 testers): una clase `Telemetry.Log(evento, datos)` que escribe JSON-lines a `Application.persistentDataPath` y/o lo manda por POST a un endpoint propio. Cero dependencias, el archivo se recoge al final de la sesión.

Reglas: la telemetría nunca crashea el juego (try/catch + fail silent); versión del build en cada evento (comparar builds entre semanas); en playtest presencial, el log local + mirar por encima del hombro rinde más que un dashboard.

## Reglas prácticas

- [ ] Toda regla de gameplay/economía/progresión vive en clases C# puras (humble object) — el MonoBehaviour solo cablea motor ↔ modelo.
- [ ] El tiempo entra por parámetro (`Tick(dt)`) y la aleatoriedad por `System.Random` inyectado con seed; nada de `Time.*` ni `Random` global dentro del modelo.
- [ ] `[Test]` EditMode por defecto; `[UnityTest]` PlayMode solo cuando necesitas frames, física o lifecycle real.
- [ ] Asmdefs desde el día 0: código de juego con asmdef propio (los tests no pueden referenciar `Assembly-CSharp`), tests en `Tests/EditMode` + `Tests/PlayMode`.
- [ ] Save/load con test de round-trip + test de save corrupto (archivo truncado → el juego no crashea, hace fallback).
- [ ] Procgen: mismo seed → mismo output, más loop de ~100 seeds asertando invariantes.
- [ ] Economía: simulación headless de miles de iteraciones con asserts de invariantes (sin balances negativos, sin inflación descontrolada).
- [ ] Cada bug no trivial arreglado deja un test de regresión que primero falló.
- [ ] Test rojo = STOP: se arregla el código o se actualiza el test explícitamente; jamás se comenta.
- [ ] Suite EditMode en segundos; si tarda minutos, dejará de correrse — mover lo lento a PlayMode o adelgazarlo.
- [ ] Input simulado con `InputTestFixture` (`testables` en manifest.json + refs `Unity.InputSystem.TestFramework`).
- [ ] Errores esperados en tests se declaran con `LogAssert.Expect` ANTES del código que los loguea.
- [ ] Agente con MCP: suite tras cada feature, suite completa antes de cada build; `run_tests` → polling de `get_test_job`, nunca asumir el resultado [ver: unity/unity-mcp-flujo].
- [ ] Smoke test de §7 en cada build candidato, por plataforma, en device real — el editor no cuenta como plataforma.
- [ ] Device matrix mínima: el device más débil soportado + uno mainstream; el perf target se mide en el débil.
- [ ] Matriz de interrupciones móvil completa (lock, background, llamada, audio focus, matar proceso) antes de shippear móvil.
- [ ] Bugs: una sola lista, pasos de reproducción obligatorios, triage P0–P3; P2/P3 a la lista de corte sin culpa.
- [ ] Telemetría de embudo instrumentada ANTES del primer playtest externo; versión de build en cada evento.
- [ ] Cobertura (`com.unity.testtools.codecoverage`) para encontrar lógica crítica sin test — no para perseguir un porcentaje.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| "No se puede testear porque todo está en MonoBehaviours" | Es una decisión, no un destino: extraer la lógica a clases puras (§2); empezar por el sistema que más bugs da |
| Testear el feel ("el salto dura 0.42s") y romper el test con cada tuning | El feel se tunea con humanos [ver: feel-en-unity]; el test cubre reglas, no valores de sensación |
| `[UnityTest]` con `WaitForSeconds(5)` real por todos lados | Suite lenta que nadie corre: tiempo por parámetro (§5) o `Time.timeScale`; PlayMode solo para lo que necesita motor |
| `WaitForSeconds` en un `[UnityTest]` EditMode | Solo PlayMode los soporta; EditMode únicamente `yield return null` (docs 6000.2) |
| Tests que dependen del orden o comparten estado (statics, escena sucia) | Cada test construye y destruye su mundo; ojo con domain reload y statics [ver: unity/gotchas-unity] |
| El test pasa en editor, el juego falla en build | El editor no es la plataforma: smoke §7 por build + PlayMode tests en device por CLI (`-testPlatform <BuildTarget>`) |
| Referenciar `Assembly-CSharp` desde el asmdef de test | No se puede: el código de juego necesita asmdef propio [ver: estructura-proyecto] |
| Un error logueado a mitad de test que "no venía al caso" lo hace fallar | Es a propósito (LogAssert): o el error es un bug real, o se declara con `Expect`; no silenciar con `ignoreFailingMessages` global |
| Asserts de floats con `==` | `Assert.AreEqual(expected, actual, 0.001f)` (overload con tolerancia) — misma trampa de [ver: unity/gotchas-unity] §10 |
| Mockear medio motor para un test "unitario" de un MonoBehaviour | Señal de que la lógica está mal ubicada: extraer el modelo (§2) y testear eso; el cableado se cubre con 1 PlayMode test |
| Arreglar un bug reportado sin reproducirlo | Sin repro no hay fix verificable: instrumentar y reproducir primero [ver: gamedev/produccion-proceso] |
| "QA al final, cuando el juego esté terminado" | El pase §7 es por build desde el primer build; los bugs de plataforma encontrados en beta cuestan 10× |
| Playtest sin telemetría y decidir por las opiniones | Lo que HIZO > lo que DICE: embudo mínimo (§9) antes del primer playtest externo |
| Perseguir 100% de cobertura en un juego chico | Cobertura como linterna (qué crítico quedó a oscuras), no como KPI; el feel y los visuales jamás llegarán a cubrirse y no importa |
| El agente reporta "tests verdes" sin esperar el job de MCP | `run_tests` es async: polling de `get_test_job` hasta estado final [ver: unity/unity-mcp-flujo] |

## Fuentes

- **Edit Mode vs Play Mode tests — Unity Manual 6000.2 (test-framework)** — dónde corre cada modo, acceso a APIs, `[UnityTest]` como coroutine solo en PlayMode, recomendación de preferir `[Test]`, tests PlayMode en player, prohibición de referenciar `Assembly-CSharp`.
- **Workflow: create a test assembly — Unity Manual 6000.2** — flujo del Test Runner, referencias exactas del asmdef de test (`nunit.framework.dll`, `UnityEngine.TestRunner`, `UnityEditor.TestRunner` solo EditMode), plataformas default Editor-only.
- **UnityTest attribute — docs package com.unity.test-framework 1.4** — `IEnumerator`, yields permitidos por modo (`WaitForSeconds`/`WaitForFixedUpdate` solo PlayMode), ejemplos oficiales EditMode y PlayMode.
- **Unity Test Framework — landing del package (docs.unity3d.com)** — versión vigente 1.8.x a julio 2026 (el registro sigue publicando releases tras el lanzamiento de Unity 6.2; confirmar el patch en el Package Manager del proyecto); para Unity 6.2+ la guía vive en el Unity Manual (los links del package redirigen allí).
- **Running tests from the command line — Unity Manual 6000.2** — flags verificados: `-runTests`, `-testPlatform` (EditMode/PlayMode/BuildTarget), `-testResults` (NUnit XML), `-testFilter`, `-testCategory`, `-forgetProjectPath`, `-runSynchronously`; `-quit` no soportado con tests; sin convención de exit codes.
- **LogAssert — API docs com.unity.test-framework** — `Expect` (4 overloads), `NoUnexpectedReceived`, `ignoreFailingMessages`; un log de error/excepción inesperado falla el test; `Expect` va antes del código.
- **Input testing (InputTestFixture) — docs package com.unity.inputsystem 1.14** — `testables` en manifest.json, referencias `Unity.InputSystem` + `Unity.InputSystem.TestFramework`, entorno limpio por test, no corre `[InitializeOnLoad]`, API `Press`/`Release`/`PressAndRelease`/`Set`/`Trigger`.
- **Code Coverage — docs package com.unity.testtools.codecoverage 1.3.x** — reportes HTML/Cobertura/LCOV desde el Test Runner, coverage recording para testing manual, badges; mínimo Unity 2021.3.
- **NSubstitute — Getting started (nsubstitute.github.io)** — `Substitute.For<T>()`, `.Returns()`, `.Received()`; funciona sobre interfaces/miembros overridables.
- **Core app quality — Android Developers (developer.android.com)** — checklist oficial de interrupciones y estado: `Sleep_Resume`, `Lock_Resume`, `State_Preservation` (cita explícitamente "game progress"), `App_Switcher`, `Consistent_UX`, `Audio_Focus_Change`.
- **Unity Analytics overview — docs.unity.com (UGS)** — custom events, funnels/dashboards, requisito de vincular proyecto UGS, consent/privacidad obligatorios, posible costo.
- **xUnit Test Patterns — Gerard Meszaros (2007)** — origen del patrón Humble Object (atribución estándar del libro; la web del autor no estuvo accesible en esta sesión — el patrón en sí se describe aquí desde esa atribución + práctica establecida).
- **Base propia:** [ver: gamedev/produccion-proceso] (playtesting método Valve, triage, milestones/gates), [ver: unity/unity-mcp-flujo] (run_tests async, ciclo de compilación, verificación sin ojos), [ver: unity/gotchas-unity] (fake null, móvil §12, floats, statics/domain reload), [ver: estructura-proyecto] (asmdefs y carpetas de test del día 0).

Relacionados: [ver: produccion-solo-dev] (cuándo caen los gates de QA en el calendario), [ver: sistemas-meta] (telemetría de producción y embudos completos), [ver: unity/build-plataformas] (generar los builds que este archivo smokea).
