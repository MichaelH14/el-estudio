# Input System (el nuevo)

> **Cuando cargar este archivo:** al implementar cualquier input en Unity 6 — movimiento, botones, touch movil, gamepad, rebinding de controles, navegacion de UI con mando — o al migrar codigo que usa `UnityEngine.Input` (el Input Manager viejo).

## Version y contexto

- Paquete `com.unity.inputsystem`; version actual en docs.unity3d.com: **1.19.x** (verificado jul 2026). No es el default del core: si el paquete no esta instalado, Unity usa el Input Manager viejo. Las plantillas oficiales de Unity 6 suelen traerlo ya instalado con un asset `InputSystem_Actions.inputactions` creado. La version REAL instalada en un proyecto puede ser menor (revisar `Packages/manifest.json`) — el contenido de este archivo esta verificado contra la doc 1.19 pero las APIs cubiertas aqui son estables desde 1.8+.
- **Project-wide actions** (`InputSystem.actions`) existen desde Input System **1.8** (marzo 2024, requiere Editor 2022.3+). Se asignan en **Edit > Project Settings > Input System Package** y se habilitan solas al arrancar.
- El manual de Unity 6 recomienda el Input System package para proyectos nuevos; el Input Manager viejo queda como legado.
- El selector real es **Player Settings > Active Input Handling**: `Input System Package` / `Input Manager (Old)` / `Both`.

## Modelo mental: Actions, Maps, Bindings, Control Schemes

| Concepto | Clase | Que es |
|---|---|---|
| Action | `InputAction` | Intencion de gameplay ("Jump", "Move"). Devuelve valores o dispara callbacks. Nombre unico dentro de su map |
| Action Map | `InputActionMap` | Coleccion nombrada de actions ("Player", "UI", "Vehicle"). Se habilita/deshabilita en bloque — es el mecanismo para cambiar de contexto (gameplay ↔ menu) |
| Binding | `InputBinding` | Ruta de control concreta: `<Gamepad>/leftStick`, `<Keyboard>/space`. Una action puede tener N bindings |
| Composite | `InputBindingComposite` | Binding sintetico: 4 teclas → un `Vector2` (WASD), modificador+tecla, etc. |
| Control Scheme | grupo de bindings | Agrupa bindings por dispositivo ("Keyboard&Mouse", "Gamepad", "Touch"). Permite auto-asignar dispositivos por jugador y filtrar con `bindingMask` |
| Asset | `InputActionAsset` | El `.inputactions` completo (JSON). Editable en el Actions Editor |

Claves del modelo:
- La separacion proposito/dispositivo es lo que hace posible rebinding, multi-plataforma y multiplayer local sin tocar gameplay code.
- **Las actions arrancan deshabilitadas** salvo las project-wide. Hay que llamar `action.Enable()` o `map.Enable()`. Con una action habilitada no se pueden modificar sus bindings (deshabilitar → editar → habilitar).
- Si varias actions se ejecutan el mismo frame, **el orden entre ellas es indefinido** — no asumir orden.

### Action types y phases

| Tipo | Conducta | Uso |
|---|---|---|
| **Value** (default) | Conflict resolution entre controles (gana el mas actuado) + **initial state check** al habilitar (dispara con el estado actual) | Movimiento, look, cualquier valor continuo |
| **Button** | Como Value pero **sin** initial state check (un boton ya presionado al habilitar NO dispara) | Jump, fire, acciones discretas |
| **Pass-Through** | Sin conflict resolution: cualquier cambio de cualquier control bound dispara | Multi-touch, actions de UI tipo Point/Click, leer todos los dispositivos a la vez |

Phases: `Disabled → Waiting → Started → Performed → Canceled` (consultar con `InputAction.phase`). Callbacks: `started`, `performed`, `canceled`, todos reciben `InputAction.CallbackContext`. El contexto **solo es valido durante el callback** — no guardarlo. `ctx.time` y `ctx.startTime` van en la linea temporal de `Time.realtimeSinceStartup`; `ctx.duration = time - startTime` (util para "cuanto tiempo estuvo presionado").

## Las tres formas de consumir input

### 1. Referencia a actions + polling o callbacks (recomendada por Unity)

```csharp
InputAction _move, _jump;

void Awake()
{
    // Con project-wide actions (Unity 6): sin referencias en el Inspector
    _move = InputSystem.actions.FindAction("Player/Move");
    _jump = InputSystem.actions.FindAction("Player/Jump");
}

void Update()
{
    Vector2 dir = _move.ReadValue<Vector2>();
    if (_jump.WasPressedThisFrame()) Jump();
}
```

Cachear la referencia en `Awake`/`Start` — no hacer `FindAction` por frame. Alternativa serializada: campo `public InputActionReference jumpRef;` y usar `jumpRef.action`.

### 2. Clase C# generada (type-safe)

En el Inspector del `.inputactions`: marcar **Generate C# Class** → Apply. Genera una clase (p.ej. `PlayerControls`) con una struct por map y una interfaz de callbacks por map (`IPlayerActions` con `OnMove`, `OnJump`...).

```csharp
PlayerControls _controls;

void Awake()
{
    _controls = new PlayerControls();
    _controls.Player.SetCallbacks(this); // this : PlayerControls.IPlayerActions
}
void OnEnable()  => _controls.Player.Enable();
void OnDisable() => _controls.Player.Disable();

public void OnJump(InputAction.CallbackContext ctx)
{
    if (ctx.performed) Jump();
}
```

Sin strings, autocompletado, errores en compile-time. Ideal para proyectos donde el codigo es la fuente de verdad.

### 3. PlayerInput component (multiplayer local y prototipos con Inspector)

Component que conecta un asset de actions a callbacks sin codigo de plumbing. Cuatro **Behaviors**: `Send Messages` (llama `OnJump()` via `SendMessage` en el mismo GO), `Broadcast Messages` (idem hacia hijos), `Invoke Unity Events` (eventos en Inspector con firma `void OnFire(InputAction.CallbackContext ctx)`), `Invoke C# Events` (`onActionTriggered`, `onDeviceLost`, `onDeviceRegained`).

- Con `PlayerInputManager` da multiplayer local: instancia prefabs por jugador, empareja dispositivos unicos por jugador y soporta split-screen (campo Camera).
- En single-player **auto-cambia de control scheme** al detectar uso de otro dispositivo (teclado ↔ gamepad).
- `SwitchCurrentActionMap("UI")` / `DeactivateInput()` / `ActivateInput()` para cambiar contexto.
- ⚠️ Cada `PlayerInput` crea una **copia privada** de las actions: acceder siempre via `playerInput.actions`, nunca `InputSystem.actions` directamente, o se rompe el filtrado por dispositivo.

### 4. (Prototipo) Polling directo de dispositivos

`Keyboard.current.spaceKey.wasPressedThisFrame`, `Mouse.current.position.ReadValue()`, `Gamepad.current.leftStick.ReadValue()`. Sin actions: sin rebinding, sin schemes, acoplado al hardware. Solo prototipos o herramientas de editor.

### Criterio de eleccion

| Escenario | Usar |
|---|---|
| Juego single-player tipico (Unity 6) | Project-wide actions + `InputSystem.actions.FindAction` cacheado, o clase generada |
| Codigo estricto, refactors frecuentes | Clase C# generada |
| Multiplayer local / split-screen | `PlayerInput` + `PlayerInputManager` (unica opcion sensata) |
| Prototipo de 1 tarde, un solo dispositivo | Polling directo de `Keyboard.current` etc. |

### Polling API por frame (sobre actions)

| Metodo | True cuando |
|---|---|
| `ReadValue<T>()` | Valor actual (aplica processors) |
| `IsPressed()` | Actuacion sobre el press point ahora |
| `WasPressedThisFrame()` | Cruzo el press point este frame |
| `WasReleasedThisFrame()` | Cayo bajo el release threshold este frame |
| `WasPerformedThisFrame()` | La phase paso a Performed este frame (respeta interactions) |
| `WasCompletedThisFrame()` | La phase salio de Performed este frame |

### Update Mode y FixedUpdate

Settings del paquete → **Update Mode**: `Process Events In Dynamic Update` (default), `In Fixed Update`, `Manually` (`InputSystem.Update()`).

⚠️ Con el default (Dynamic), llamar `WasPressedThisFrame()` **dentro de `FixedUpdate` pierde o duplica presses** (puede haber 0 o N fixed steps por frame de render). Antidoto: leer/latchear en `Update` y consumir en `FixedUpdate`, o usar el patron de buffer con timestamp (abajo). No cambiar el Update Mode a Fixed salvo que TODO el gameplay lea en fixed. [ver: fisica-unity]

## Touch movil (Enhanced Touch)

La API de alto nivel para touch. **No** hacer polling del device `Touchscreen` (pierde cambios de estado entre frames); los docs lo prohiben explicitamente.

```csharp
using UnityEngine.InputSystem.EnhancedTouch;
using Touch = UnityEngine.InputSystem.EnhancedTouch.Touch;

void OnEnable()  => EnhancedTouchSupport.Enable();   // obligatorio, no viene activa
void OnDisable() => EnhancedTouchSupport.Disable();

void Update()
{
    foreach (var t in Touch.activeTouches)
        Debug.Log($"{t.touchId} {t.phase} {t.screenPosition} {t.delta}");
}
```

- `Touch.activeTouches`: touches activos del frame; `Touch.activeFingers`: dedos (el N-esimo contacto). Phases: `Began, Moved, Stationary, Ended, Canceled`. Todos los records con el mismo `touchId` son un mismo contacto continuo.
- La API **no genera GC garbage** (memoria no administrada + structs wrapper) — segura para llamar cada frame en movil.
- Simulacion en Editor: `TouchSimulation.Enable()` o Input Debugger > Options > *Simulate Touch Input From Mouse or Pen*.
- Touch via actions: para un solo punto, bindear `<Pointer>/press` y `<Pointer>/position` (cubre mouse y touch). Para **multi-touch** con actions: `<Touchscreen>/touch*/press` con action type **Pass-Through** (recibe callback por cada touch).

### Gestos basicos (DIY)

El paquete **no trae reconocedores de gestos** (tap/swipe/pinch) a fecha de 1.19 — se implementan sobre Enhanced Touch:

- **Tap**: `Ended` con poca distancia total y duracion corta (los defaults del sistema usan 0.2 s como tap time — buen umbral).
- **Swipe**: al `Ended`, si el desplazamiento total supera un umbral en px (escalar por DPI: `Screen.dpi`), direccion = componente dominante del vector.
- **Pinch** (2 dedos):

```csharp
if (Touch.activeTouches.Count == 2)
{
    var a = Touch.activeTouches[0]; var b = Touch.activeTouches[1];
    float now  = Vector2.Distance(a.screenPosition, b.screenPosition);
    float prev = Vector2.Distance(a.screenPosition - a.delta,
                                  b.screenPosition - b.delta);
    ApplyZoom((now - prev) * pinchSpeed); // >0 separando, <0 juntando
}
```

### Controles on-screen (joystick virtual)

`OnScreenStick` y `OnScreenButton` (uGUI): simulan controles de un device real via `controlPath` (p.ej. `<Gamepad>/leftStick`, `<Gamepad>/buttonSouth`), asi el MISMO action map de gamepad funciona en movil sin codigo extra. `OnScreenStick` con **Movement Range** en px; usar su modo *Isolated Input Actions* si el drag produce jitter por alternancia pointer/stick. Requieren EventSystem + `InputSystemUIInputModule`. [ver: ui-unity]

## Gamepad

Layout estandarizado de `Gamepad` (mismo codigo para Xbox/PS/Switch): `buttonSouth/North/East/West` (posicion fisica, no letra), `leftStick`/`rightStick` (`StickControl`, Vector2 normalizado con deadzone ya aplicada), `dpad`, `leftTrigger`/`rightTrigger` (float 0-1), `leftShoulder`/`rightShoulder`, `startButton`/`selectButton`, `leftStickButton`/`rightStickButton`. `Gamepad.current` = el ultimo usado; `Gamepad.all` para todos.

- Bindear siempre por rol (`buttonSouth`), nunca por letra: en Switch la posicion fisica se mantiene coherente.
- Deadzone: processor `stickDeadzone(min=0.125,max=0.925)` — esos son los defaults de `InputSettings.defaultDeadzoneMin/Max`. Aplicada por defecto en los sticks.
- Iconos por dispositivo: `action.GetBindingDisplayString(bindingIndex)` para mostrar "A" vs "Cruz" segun el device activo.
- En Windows (XInput), UWP y Switch el polling es explicito: `InputSystem.pollingFrequency` (default 60 Hz).
- ⚠️ Switch Pro Controller por USB cableado **no** esta soportado en desktop — solo Bluetooth.

### Rumble

`Gamepad` implementa `IDualMotorRumble`:

```csharp
Gamepad.current?.SetMotorSpeeds(0.25f, 0.75f); // low-freq izq, high-freq der [0..1]
// NO hay parametro de duracion: apagar a mano
IEnumerator Pulse(float lo, float hi, float secs)
{
    Gamepad.current?.SetMotorSpeeds(lo, hi);
    yield return new WaitForSeconds(secs);
    Gamepad.current?.ResetHaptics();
}
```

- `InputSystem.PauseHaptics()` / `ResumeHaptics()` en pausa del juego o perdida de foco; `ResetHaptics()` apaga y resetea.
- Soporte por plataforma (docs oficiales): mandos PS4/Xbox/Switch en sus consolas (con el package de consola), PS4 en Mac/Windows, Xbox en Windows. Fuera de eso (p.ej. mandos genericos, movil) no esta garantizado.
- DualShock: `DualShockGamepad.SetLightBarColor(Color)`; si se combina con rumble en llamadas rapidas se pierden comandos (limite de driver USB) — usar `SetMotorSpeedsAndLightBarColor()`.

### Navegacion de UI con mando

- uGUI necesita `InputSystemUIInputModule` en el EventSystem (boton de reemplazo automatico aparece en el Inspector del viejo `StandaloneInputModule`). UI Toolkit runtime en Unity 6 puede consumir las actions directo, sin modulo.
- Action map "UI" del asset default: `Navigate` (Pass-Through Vector2), `Submit`, `Cancel`, `Point`, `Click`, `ScrollWheel`, etc. ⚠️ Para compatibilidad con UI Toolkit **no renombrar** ni el map "UI" ni sus actions ni cambiar sus action types.
- La navegacion con stick/dpad requiere que haya un elemento seleccionado: setear `EventSystem.current.SetSelectedGameObject(firstButton)` al abrir cada menu, o no hay foco que mover. [ver: ui-unity]
- Cursor virtual con stick: component `VirtualMouseInput` (solo uGUI). No configurar virtual mouse Y navegacion para el mismo gamepad (input doble).
- Multiplayer: `MultiplayerEventSystem` + un `InputSystemUIInputModule` por jugador (via `PlayerInput.uiInputModule`).
- ⚠️ **No hay consumo automatico UI vs juego**: un click que usa la UI TAMBIEN llega al gameplay. Pointer: chequear `EventSystem.current.IsPointerOverGameObject()` antes de disparar. Navegacion/botones: cambiar de action map (Player ↔ UI) al abrir menus — es el antidoto estructural.

## Rebinding en runtime y persistencia

```csharp
void StartRebind(InputAction action, int bindingIndex)
{
    action.Disable(); // obligatorio antes de tocar bindings
    var op = action.PerformInteractiveRebinding(bindingIndex)
        .WithControlsExcluding("<Mouse>/position")
        .WithControlsExcluding("<Mouse>/delta")
        .WithCancelingThrough("<Keyboard>/escape")
        .OnMatchWaitForAnother(0.1f)
        .OnComplete(o => { action.Enable(); RefreshUI(); o.Dispose(); })
        .OnCancel(o => { action.Enable(); o.Dispose(); })
        .Start();
}
```

- `RebindingOperation` es `IDisposable` — **siempre `Dispose()`** en complete y cancel (memory leak si no).
- Filtrar por scheme activo con `.WithBindingGroup("Gamepad")` / `WithBindingMask` para no pisar bindings del otro dispositivo.
- El rebind escribe `overridePath` (no toca el asset). Persistencia:

```csharp
PlayerPrefs.SetString("rebinds", actions.SaveBindingOverridesAsJson()); // guardar
actions.LoadBindingOverridesFromJson(PlayerPrefs.GetString("rebinds")); // al arrancar
actions.RemoveAllBindingOverrides(); // boton "restaurar defaults"
```

- Override puntual sin UI: `action.ApplyBindingOverride(index, "<Keyboard>/enter")`.
- Mostrar la tecla actual en la UI: `action.GetBindingDisplayString(index)`.
- El paquete trae el sample **Rebinding UI** (Package Manager > Input System > Samples) con un component reusable.

## Interacciones y processors

**Interactions** (modifican cuando una action llega a Performed). Defaults de `InputSettings` verificados: press point 0.5, tap 0.2 s, slow-tap 0.5 s, hold 0.4 s, multi-tap delay 0.75 s.

| Interaction | Performed cuando | Parametros (default) |
|---|---|---|
| `Press` | Al presionar (o soltar, o ambos, segun `behavior`) | `pressPoint=0.5` |
| `Hold` | Mantenido >= `duration` (started al presionar, canceled si suelta antes) | `duration=0.4` |
| `Tap` | Presionar y soltar dentro de `duration` (canceled si se pasa) | `duration=0.2` |
| `SlowTap` | Soltar DESPUES de >= `duration` (performed al soltar) | `duration=0.5` |
| `MultiTap` | `tapCount` taps con separacion <= `tapDelay` | `tapCount=2, tapTime=0.2, tapDelay=0.75` |

- Sin interaction explicita, un Button hace Performed al cruzar el press point (default `Press`).
- Con `Hold`, para distinguir "tap corto vs hold" en la misma tecla: usar `started`/`performed`/`canceled` o `ctx.duration`; o dos actions separadas (Tap en una, Hold en otra).
- Custom: implementar `IInputInteraction` (`Process(ref InputInteractionContext)`, `Reset()`) + `InputSystem.RegisterInteraction<T>()`. Desde 1.11 las extensiones custom se cargan automaticamente.

**Processors** (transforman el valor). Sintaxis por binding o por action: `"stickDeadzone(min=0.125,max=0.925)"`, `"invertVector2(invertX=false,invertY=true)"`, `"scaleVector2(x=2,y=2)"`, `"normalizeVector2"`, `"axisDeadzone"`, `"clamp(min=0,max=1)"`, `"scale(factor=2)"`, `"invert"`. Los de action se aplican DESPUES de los de binding. Custom: `InputProcessor<T>` + `InputSystem.RegisterProcessor<T>("nombre")`.

- ⚠️ Encadenar processors en el MISMO campo separados por coma (`"scale(factor=10),invertVector2"`); agregarlos como entradas separadas puede aplicar solo uno (bug reportado por la comunidad).
- Invertir eje Y de camara ("look invertido") = processor `invertVector2(invertY=true)` sobre el binding de look — no logica en codigo, asi el rebinding lo respeta.

## Coexistencia con el Input Manager viejo y migracion

- **Active Input Handling = Both** permite ambos a la vez (util para migrar por partes o para assets de terceros que usan `UnityEngine.Input`; IMGUI/`OnGUI` en runtime REQUIERE Both porque el Input System no lo soporta). Coste extra de procesamiento — dejar solo `Input System Package` al terminar.
- Con solo el nuevo activo, `UnityEngine.Input` lanza `InvalidOperationException` — los assets de la Store viejos revientan; chequear antes de cambiar el setting.
- Defines para codigo dual: `#if ENABLE_INPUT_SYSTEM` (nuevo activo) / `#if ENABLE_LEGACY_INPUT_MANAGER` (viejo activo). Con Both, ambos definidos.

| Viejo (`UnityEngine.Input`) | Nuevo |
|---|---|
| `Input.GetAxis("Horizontal")` | `moveAction.ReadValue<Vector2>().x` |
| `Input.GetAxisRaw(...)` | `action.ReadUnprocessedValue()` (o quitar processors) |
| `Input.GetButtonDown("Jump")` | `jumpAction.WasPressedThisFrame()` |
| `Input.GetButton("Jump")` | `jumpAction.IsPressed()` |
| `Input.GetKey(KeyCode.Space)` | `Keyboard.current.spaceKey.isPressed` |
| `Input.mousePosition` | `Mouse.current.position.ReadValue()` |
| `Input.GetTouch(0)` | `Touch.activeTouches[0]` (Enhanced Touch) |
| `Input.acceleration` | `Accelerometer.current.acceleration.ReadValue()` + `InputSystem.EnableDevice(...)` |

Orden de migracion practico: instalar paquete → Active Input Handling = Both → crear asset de actions y migrar sistema por sistema → quitar Both.

## Input buffering y feel de input

El Input System no trae buffering integrado; el patron con timestamps de eventos es robusto frente al desfase Update/FixedUpdate:

```csharp
float _jumpPressedAt = float.NegativeInfinity;
const float BufferWindow = 0.15f; // 0.1-0.2 s tipico

void OnEnable() => _jump.performed += OnJump;
void OnJump(InputAction.CallbackContext ctx) => _jumpPressedAt = (float)ctx.time;

void FixedUpdate()
{
    bool buffered = Time.realtimeSinceStartup - _jumpPressedAt <= BufferWindow;
    if (buffered && _grounded)
    {
        DoJump();
        _jumpPressedAt = float.NegativeInfinity; // consumir: un press = un salto
    }
}
```

- `ctx.time` esta en la linea de `Time.realtimeSinceStartup` (timestamp del EVENTO, no del callback) — comparar contra esa misma linea, no contra `Time.time`.
- **Consumir** el buffer al usarlo (resetear el timestamp), o un press dispara dos saltos.
- Coyote time: complemento del buffer — permitir saltar hasta ~0.1 s despues de dejar el borde (Celeste usa 0.1 s de "jump grace"). Valores tipicos de la practica comunitaria: buffer 0.1-0.2 s, coyote 0.05-0.15 s. Detalle de diseño en [ver: gamedev/game-feel].
- Salto de altura variable: al `canceled` (soltar) con velocidad Y > 0, recortar velocidad o aplicar fuerza hacia abajo (`rb.AddForce(Vector2.down * cancelRate)`).
- Mantener pressed-state entre frames de fisica: latchear con `performed`/`canceled` en vez de `IsPressed()` dentro de `FixedUpdate` cuando el timing importe.
- Para combos/fighting: guardar cola de (`accion`, `ctx.time`) y evaluar ventanas contra esa cola; `ctx.duration` distingue tap de hold sin timers propios.

## Reglas practicas

1. Unity 6, proyecto nuevo: usar el asset project-wide (`InputSystem_Actions`) y leer via `InputSystem.actions.FindAction(...)` cacheado en `Awake`, o generar la clase C#.
2. Un action map por contexto de juego (`Player`, `UI`, `Vehicle`, `Dialogue`); cambiar de contexto = `Disable()` un map y `Enable()` otro, nunca flags booleanos por action.
3. Acciones discretas (jump/fire) → type **Button**; valores continuos (move/look) → **Value**; multi-touch y Point/Click de UI → **Pass-Through**.
4. Con project-wide actions, en `Start` deshabilitar los maps que no tocan (arrancan TODOS habilitados).
5. Nunca `WasPressedThisFrame()` dentro de `FixedUpdate` con Update Mode default: latchear en `Update` o usar buffer con `ctx.time`.
6. Desuscribir callbacks y `Disable()` en `OnDisable` — callbacks colgados sobreviven al objeto y explotan con referencias muertas.
7. Movil: `EnhancedTouchSupport.Enable()` antes de leer `Touch.activeTouches`; jamas polling del device `Touchscreen`.
8. Joystick virtual movil: `OnScreenStick`/`OnScreenButton` apuntando a `<Gamepad>/...` para reusar el action map de gamepad tal cual.
9. Gamepad: bindear `buttonSouth` (rol/posicion), no "A"; UI de ayuda con `GetBindingDisplayString()` para que muestre el glifo del device activo.
10. Rumble: siempre apagarlo (timer/coroutine + `ResetHaptics()`), y `PauseHaptics()` en pausa y al perder foco.
11. Menus con mando: `SetSelectedGameObject` al abrir cada pantalla; sin seleccion inicial la navegacion no hace nada.
12. Clicks de UI que atraviesan al juego: `IsPointerOverGameObject()` para pointer; para lo demas, switch de action map Player↔UI.
13. Rebinding: `Disable()` antes, `Dispose()` del operation siempre, excluir `<Mouse>/position` y `<Mouse>/delta`, y persistir con `SaveBindingOverridesAsJson()` → PlayerPrefs (o save file).
14. Ofrecer siempre "restaurar controles" (`RemoveAllBindingOverrides()`).
15. Deadzones e inversion de ejes como processors en bindings, no como logica en codigo.
16. Multiplayer local: `PlayerInput` + `PlayerInputManager`; acceder actions SOLO via `playerInput.actions`.
17. No renombrar el action map "UI" ni sus actions si se usa UI Toolkit.
18. Assets de terceros que usan `UnityEngine.Input` → Active Input Handling = Both hasta reemplazarlos; medir y volver a solo-nuevo.

## Errores comunes

| Pitfall | Antidoto |
|---|---|
| "El input no responde" — actions nunca habilitadas | `map.Enable()` en `OnEnable` (las project-wide son la excepcion: vienen habilitadas) |
| Callback `performed` dispara al habilitar la action con un stick/tecla ya actuados | Es el initial state check de type Value; para botones usar type Button |
| Callback de move dispara una vez y "se queda pegado" el ultimo valor | Los callbacks solo disparan al CAMBIAR el valor: para movimiento continuo, poll con `ReadValue` en `Update`, o cachear el Vector2 en `performed` Y limpiarlo en `canceled` |
| Salto "fantasma" o perdido leyendo en `FixedUpdate` | Desfase update/fixed: latch en `Update` o buffer por timestamp (`ctx.time`) |
| `CallbackContext`/`InputValue` guardado para despues devuelve basura | Solo validos durante el callback: extraer el valor (`ReadValue<T>()`) ya |
| Doble disparo de jump con teclado y gamepad conectados | Es conflict resolution normal (gana el mas actuado, no duplica); si duplica, hay DOS actions o dos suscripciones al mismo callback |
| `MultiTap` no dispara | Bug conocido: no convive con otros bindings/interactions en la misma action — action dedicada solo para el multi-tap |
| Hold en la action de movimiento da errores/valores raros | Hold es para acciones discretas; movimiento va sin interaction, type Value |
| Dos processors agregados por separado y solo aplica uno | Encadenarlos en un solo string separados por coma |
| Rebinding captura `<Mouse>/position` al mover el raton | `WithControlsExcluding("<Mouse>/position")` y `.../delta` antes de `Start()` |
| Rebinds se pierden al reiniciar | Los overrides no se guardan en el asset: `SaveBindingOverridesAsJson()` + load al boot |
| Leak de `RebindingOperation` | `Dispose()` en `OnComplete` Y `OnCancel` |
| `UnityEngine.Input` lanza `InvalidOperationException` tras activar el paquete | Un asset/script legado sigue usando el API viejo: Active Input Handling = Both o migrar ese codigo |
| UI no responde tras migrar | El EventSystem sigue con `StandaloneInputModule`: reemplazar por `InputSystemUIInputModule` (boton en el Inspector) |
| Boton de UI clickeado Y el personaje dispara | No hay consumo automatico: `IsPointerOverGameObject()` / switch de action map |
| Navegacion con mando muerta en menus | Falta `SetSelectedGameObject` inicial; o Virtual Mouse y Navigate configurados a la vez (input doble) |
| Rumble que nunca para | `SetMotorSpeeds` no tiene duracion: apagar por timer y `PauseHaptics()` al perder foco |
| Multiplayer: todos los jugadores responden al mismo mando | Se leyo `InputSystem.actions`/`Gamepad.current` en vez de `playerInput.actions` (copia privada filtrada por device) |
| Switch Pro por USB no detectado en PC | Limitacion documentada: usar Bluetooth |
| El personaje se mueve con la ventana sin foco (o al reves, input muerto en background) | Ajustar Run In Background + Background Behavior en settings del paquete (default: resetea y deshabilita devices no-background al perder foco) |

## Fuentes

- Input System 1.19 Manual — Workflows — Unity (docs.unity3d.com) — criterio oficial de que forma de consumo usar.
- Input System 1.19 Manual — Actions — Unity — modelo mental, enable/disable, restricciones de edicion, orden indefinido.
- Input System 1.19 Manual — Responding to Actions — Unity — action types, phases, polling API (`WasPressedThisFrame` etc.), conflict resolution, initial state check, CallbackContext.
- Input System 1.19 Manual — Interactions — Unity — Press/Hold/Tap/SlowTap/MultiTap, parametros y fases, custom interactions.
- Input System 1.19 Manual — Using Processors — Unity — processors built-in, niveles de aplicacion, orden binding→action.
- Input System 1.19 Manual — PlayerInput — Unity — behaviors de notificacion, copia privada de actions, multiplayer, gotcha de maps project-wide todos habilitados.
- Input System 1.19 Manual — Touch (Enhanced Touch) — Unity — `EnhancedTouchSupport`, `Touch.activeTouches`, no-GC, TouchSimulation, prohibicion de polling a `Touchscreen`, multi-touch via Pass-Through.
- Input System 1.19 Manual — Gamepad — Unity — layout, deadzone defaults, rumble y soporte por plataforma, DualShock light bar, polling 60 Hz, Switch Pro solo BT.
- Input System 1.19 Manual — UI Support — Unity — `InputSystemUIInputModule`, action map UI y compatibilidad UI Toolkit, conflicto UI/juego, `VirtualMouseInput`, `MultiplayerEventSystem`.
- Input System 1.19 Manual — Action Bindings — Unity — `PerformInteractiveRebinding` y todo el flujo de rebinding/persistencia, composites 2DVector, control schemes y binding masks.
- Input System 1.19 Manual — Migration — Unity — Active Input Handling, defines `ENABLE_INPUT_SYSTEM`/`ENABLE_LEGACY_INPUT_MANAGER`, tabla de equivalencias API viejo→nuevo.
- Input System 1.19 Manual — Settings — Unity — Update Modes y el gotcha de FixedUpdate, Background Behavior.
- Input System 1.19 Manual — Project-Wide Actions — Unity — `InputSystem.actions`, asset `InputSystem_Actions`, habilitacion automatica.
- Input System 1.19 Manual — On-Screen Controls — Unity — `OnScreenStick`/`OnScreenButton`, controlPath, Isolated Input Actions.
- Input System 1.19 Manual — Action Assets — Unity — flujo "Generate C# Class", interfaces `I<Map>Actions`, `SetCallbacks`.
- API Reference — `InputSettings` y `InputAction.CallbackContext` — Unity — valores default verificados (deadzone 0.125/0.925, press point 0.5, tap 0.2, slow-tap 0.5, hold 0.4, multi-tap delay 0.75) y semantica de `ctx.time`/`startTime`/`duration`.
- Input System — CHANGELOG oficial — Unity — project-wide actions en 1.8 (2024), autoload de extensiones custom en 1.11, historial hasta 1.19 (re-verificado jul 2026).
- Unity 6 Manual — Input — Unity — recomendacion oficial del paquete para proyectos nuevos; Input Manager como legado.
- "Input in Unity made easy (complete guide to the new system)" — John French, GameDevBeginner (actualizado 2025) — criterio practico entre los 3 metodos y gotchas confirmados (MultiTap, processors que no stackean, Hold en movimiento).
- "How to jump in Unity" — John French, GameDevBeginner — salto de altura variable (recorte de velocidad al soltar) y ventanas de perdon de input.
