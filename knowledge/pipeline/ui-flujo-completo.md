# UI y flujo de pantallas completo en Unity

> **Cuando cargar este archivo:** al montar el esqueleto de pantallas de un juego real en Unity 6 — boot → title → gameplay (HUD + pause) → results —, implementar settings persistidos, loading async, tutorial in-game, o cablear navegación touch/mando/teclado. El diseño (qué pantallas, qué settings, qué tutorial) está en [ver: gamedev/ux-ui-onboarding]; la técnica base de Canvas/uGUI en [ver: unity/ui-unity] y de input en [ver: unity/input-system]. Aquí está la unión: recetas completas.

## 1. Arquitectura: escenas vs canvases vs paneles

Decisión concreta para un juego chico (la que menos fricción da):

| Nivel | Usar para | Por qué |
|---|---|---|
| **Escena** | `Boot` (index 0), `Menu`, `Game` (una por "mundo" si hay varios) | Cargar/descargar en bloque, aislar memoria, punto natural de loading screen |
| **Canvas** (dentro de escena) | Capas por frecuencia de cambio: HUD estático / HUD dinámico / Pause overlay | Regla de sub-canvases de [ver: unity/ui-unity]; el pause en canvas propio no ensucia el HUD |
| **Panel** (GameObject + `CanvasGroup` bajo un Canvas) | Title ↔ Settings ↔ Créditos; popups; Results sobre gameplay | Cambio instantáneo, sin loading, sin perder estado |

**Receta estándar — 3 escenas:**

- **`Boot`** (Build index 0): managers persistentes (`DontDestroyOnLoad` o escena que nunca se descarga con carga aditiva [ver: unity/arquitectura-unity]) + un Canvas global con lo que debe sobrevivir a cambios de escena: **ScreenFader, loading UI y el panel de Settings**. Poner Settings aquí resuelve gratis el requisito "mismas opciones desde Title y desde Pause".
- **`Menu`**: Title, selección de save, créditos — todos paneles bajo un Canvas.
- **`Game`**: gameplay + HUD + pause overlay + results panel. Results como panel (no escena) permite "Retry" sin recargar y mostrar stats aún vivos en memoria.

Juego tamaño jam: 2 escenas (Boot+Menu fusionadas) funciona; no bajar de 2 — el Boot separado es lo que hace trivial "aplicar settings antes de cualquier pantalla".

**Stack de paneles** (una sola pieza de código gobierna toda la navegación, incluido el Back universal):

```csharp
public class ScreenStack : MonoBehaviour
{
    readonly Stack<UIScreen> _stack = new();
    public void Push(UIScreen s)
    {
        if (_stack.Count > 0) _stack.Peek().Hide();
        _stack.Push(s); s.Show();
    }
    public void Pop() // conectado a la action UI/Cancel (Esc, B, círculo)
    {
        if (_stack.Count <= 1) return;
        _stack.Pop().Hide(); _stack.Peek().Show();
    }
}
```

`UIScreen` = `CanvasGroup` (alpha + `interactable` + `blocksRaycasts`) + campo `firstSelected` (GameObject) + memoria del último seleccionado para restaurar focus al volver (sección 8). Mostrar/ocultar paneles frecuentes con `canvas.enabled` o CanvasGroup, no `SetActive` [ver: unity/ui-unity].

## 2. Bootstrap y arranque

Orden en `Boot`:

1. `Awake`: crear servicios, cargar PlayerPrefs a memoria.
2. `Start`: **aplicar** settings (mixer, calidad, locale). ⚠️ La doc oficial de `AudioMixer.SetFloat` prohíbe llamarlo en `Awake`, `OnEnable` o `RuntimeInitializeLoadType.AfterSceneLoad` — "puede resultar en comportamiento inesperado". Volúmenes SIEMPRE en `Start` o después.
3. Cargar `Menu` con la corrutina de loading (sección 5).

PlayerPrefs (doc oficial): solo `string`/`float`/`int`; vive en registry (Windows), plist (macOS), `NSUserDefaults` (iOS), XML en `shared_prefs` (Android), IndexedDB ≤1MB (WebGL). **Sin cifrar — nunca datos sensibles ni anti-cheat.** `PlayerPrefs.Save()` fuerza el flush (se llama solo en quit normal, no en crash). Para settings está perfecto; el save de progreso del juego va en JSON en `Application.persistentDataPath` [ver: sistemas-meta].

## 3. Settings persistidos: implementación completa

Qué settings ofrecer y por qué: checklist de [ver: gamedev/ux-ui-onboarding] §7. Aquí el cómo:

| Setting | API de aplicación | Persistencia |
|---|---|---|
| Volúmenes (master/música/SFX) | `AudioMixer.SetFloat("MusicVol", dB)` sobre exposed params [ver: unity/audio-unity] | `PlayerPrefs.SetFloat` (guardar el valor 0-1 del slider, no los dB) |
| Calidad gráfica | `QualitySettings.SetQualityLevel(i, applyExpensiveChanges)` | `PlayerPrefs.SetInt` |
| Resolución/fullscreen (PC) | `Screen.SetResolution(w, h, FullScreenMode)` | `PlayerPrefs` (w, h, mode) |
| V-Sync / FPS cap | `QualitySettings.vSyncCount`, `Application.targetFrameRate` | `PlayerPrefs.SetInt` |
| Idioma | `LocalizationSettings.SelectedLocale` (paquete Localization) | `PlayerPrefs.SetString("locale", code)` |
| Controles (rebinding) | `PerformInteractiveRebinding` → `SaveBindingOverridesAsJson()` | `PlayerPrefs` (JSON) [ver: unity/input-system] |
| Toggles (shake, hints, vibración) | flags propios consultados por gameplay | `PlayerPrefs.SetInt` 0/1 |

**Audio — el slider correcto** (John French; el fader del mixer es logarítmico, un slider lineal a mitad ≈ silencio):

```csharp
// Slider: min 0.0001 (¡no 0! log10(0) = -inf), max 1
public void SetVolume(string param, float slider01)
{
    mixer.SetFloat(param, Mathf.Log10(slider01) * 20f); // 1→0dB, 0.5→-6dB, 0.0001→-80dB
    PlayerPrefs.SetFloat(param, slider01);
}
```

Gotcha oficial: tras `SetFloat`, los snapshots del mixer **dejan de controlar ese parámetro**. Si usas snapshots para duck/pausa, no expongas esos mismos parámetros a sliders — separa grupos.

**Gráficos.** `SetQualityLevel(i, applyExpensiveChanges: false)` para cambios en runtime (la doc: cambiar AA es caro; con `false` lo difiere). Poblar el dropdown desde `QualitySettings.names` — la doc avisa que los levels no usados por la plataforma se strippean del build: nunca hardcodear índices. Resoluciones desde `Screen.resolutions` (solo PC); el cambio se aplica **al final del frame**, no inmediato. `FullScreenMode`: `ExclusiveFullScreen` (Windows only), `FullScreenWindow` (todas las plataformas, el default sensato), `MaximizedWindow` (Windows/macOS), `Windowed` (desktop). Móvil: ignora resolución/fullscreen; ofrece quality preset + `Application.targetFrameRate` explícito (30/60/120 — no confiar en el default de plataforma).

**Idioma** (paquete `com.unity.localization`, docs 1.5 a jul 2026). La inicialización es async; los "Startup Selectors" se evalúan en cascada (índice 0 en adelante) hasta que uno devuelve locale. Receta de persistencia robusta y explícita:

```csharp
IEnumerator SetLanguage(string code) // "es", "en"
{
    yield return LocalizationSettings.InitializationOperation; // esperar SIEMPRE antes de tocar
    LocalizationSettings.SelectedLocale =
        LocalizationSettings.AvailableLocales.GetLocale(code);
    PlayerPrefs.SetString("locale", code); // reaplicar en Boot con esta misma corrutina
}
```

Los componentes `LocalizeStringEvent`/tablas re-localizan solos al cambiar `SelectedLocale` — no hace falta refrescar la UI a mano. ⚠️ `WaitForCompletion` (modo síncrono) no está soportado en WebGL. Estructura de tablas y flujo completo de localización: [ver: narrativa-localizacion].

**Controles**: todo el flujo (rebind interactivo, exclusiones de mouse, `Dispose`, restore defaults) ya está resuelto en [ver: unity/input-system] — el panel de settings solo llama a ese código y muestra `GetBindingDisplayString()`.

Regla de oro de UX: cada cambio se aplica al instante (preview en vivo) y se persiste al salir del panel con `PlayerPrefs.Save()`. Un setting que se resetea al reiniciar es un bug de confianza [ver: gamedev/ux-ui-onboarding].

## 4. Pause bien hecho

`Time.timeScale = 0` es el mecanismo, pero hay que saber exactamente qué congela (doc oficial + análisis de GameDevBeginner):

| Se detiene con timeScale = 0 | Sigue corriendo |
|---|---|
| `FixedUpdate` (no se llama) → toda la física | `Update` y `LateUpdate` (¡el input se sigue leyendo!) |
| Corrutinas suspendidas en `WaitForSeconds` | Corrutinas con `yield return null` o `WaitForSecondsRealtime` |
| Todo lo multiplicado por `Time.deltaTime`; `Time.time` | `Time.unscaledTime` / `unscaledDeltaTime` |
| Animators en modo Normal; partículas (por defecto) | Animators en `UnscaledTime`; partículas con `main.useUnscaledTime` |
| — | **Audio** (no depende de timeScale) |

PauseManager completo:

```csharp
public static class Pause
{
    public static bool IsPaused { get; private set; }
    public static event System.Action<bool> Changed;

    public static void Set(bool paused)
    {
        if (IsPaused == paused) return;
        IsPaused = paused;
        Time.timeScale = paused ? 0f : 1f;
        AudioListener.pause = paused;                    // congela TODO el audio...
        if (paused) InputSystem.PauseHaptics(); else InputSystem.ResumeHaptics();
        var player = InputSystem.actions.FindActionMap("Player");
        if (paused) player.Disable(); else player.Enable(); // UI map queda activo
        Changed?.Invoke(paused);
    }
}
```

- **Música y SFX de menú durante la pausa**: `AudioSource.ignoreListenerPause = true` en esas sources (uso exacto que documenta Unity: "menu item sounds or background music for the menu").
- **UI animada durante pausa**: `Animator.updateMode = AnimatorUpdateMode.UnscaledTime` (doc: "ideal for UI elements... when the game is paused"); tweens con su flag unscaled (DOTween: `.SetUpdate(true)`; en otra lib, buscar el equivalente antes de asumir que existe).
- **Input**: cambiar de action map (Player ↔ UI) es el antídoto estructural a "el personaje dispara mientras navego el menú" [ver: unity/input-system]. El `Update` sigue corriendo: cualquier lógica de gameplay que lea input fuera de actions debe chequear `Pause.IsPaused`.
- **Móvil**: auto-pausa al perder foco (convención de plataforma, [ver: gamedev/ux-ui-onboarding] §6): en `OnApplicationPause(true)` / `OnApplicationFocus(false)` llamar `Pause.Set(true)` y persistir estado.
- Cuidado con `timeScale = 0` y lerps de cámara/física en pantalla de pause con fondo vivo: si algo debe seguir moviéndose (fondo del menú), muévelo con `unscaledDeltaTime`.

## 5. Loading async sin congelones

Comportamiento oficial de `LoadSceneAsync` + `allowSceneActivation = false`: **`progress` se detiene en 0.9** y `isDone` queda `false` hasta activar. ⚠️ Mientras tanto **la cola entera de AsyncOperations se congela** — no encolar otro `LoadSceneAsync`/`UnloadSceneAsync` detrás, se quedará esperando.

```csharp
public IEnumerator LoadScene(string scene, Image bar)
{
    yield return fader.FadeOut(0.25f);                    // cubre el cambio (sección 9)
    Application.backgroundLoadingPriority = ThreadPriority.High; // pantalla de carga pura: carga a tope
    var op = SceneManager.LoadSceneAsync(scene);
    op.allowSceneActivation = false;
    while (op.progress < 0.9f)
    {
        bar.fillAmount = op.progress / 0.9f;              // barra determinada real 0→1
        yield return null;
    }
    bar.fillAmount = 1f;
    op.allowSceneActivation = true;                       // AQUÍ viene el hitch de activación
    Application.backgroundLoadingPriority = ThreadPriority.BelowNormal; // default
    yield return fader.FadeIn(0.25f);
}
```

- `Application.backgroundLoadingPriority` (doc oficial, ms máximos de integración en main thread por frame): `Low` 2ms, `BelowNormal` 4ms (default), `Normal` 10ms, `High` 50ms. Con loading screen: `High`. Streaming DURANTE gameplay: `Low`.
- El 0.9→1 (activación) ejecuta `Awake`/`OnEnable` de todos los objetos de la escena entrante en un solo golpe — `allowSceneActivation` no lo asyncea. Antídoto: escenas entrantes ligeras (spawn diferido de lo pesado) y el fade tapando ese frame.
- Spinner/animación del loading: canvas propio y animado con `unscaledDeltaTime` (sobrevive a cualquier timeScale).
- Loading >1s → indicador obligatorio; barra determinada > spinner; tips/arte reducen espera percibida [ver: gamedev/ux-ui-onboarding] §8.
- La doc prohíbe usar `allowSceneActivation` en `Awake` (no es corrutina) — siempre desde corrutina o async method.
- Escenas grandes por Addressables y carga aditiva: [ver: unity/assets-pipeline-git] y [ver: unity/arquitectura-unity].

## 6. HUD data-driven: enlazar UI a gameplay sin acoplar

Regla: **el HUD nunca referencia al player; el gameplay publica, la UI suscribe.** Las tres vías y cuándo (detalle de cada patrón en [ver: unity/csharp-patrones]):

| Vía | Cuándo |
|---|---|
| **Evento C# en el sistema de gameplay** (`Health.OnChanged`) | Default si HUD y gameplay viven en la misma escena |
| **ScriptableObject event channel** (patrón Hipple) | Cuando publican/escuchan objetos de escenas distintas o quieres testear pantallas sueltas |
| **UnityEvent en Inspector** | Cableado puntual de diseñador; no para datos por frame |

Canal SO mínimo + vista:

```csharp
[CreateAssetMenu(menuName = "Events/Float Channel")]
public class FloatChannel : ScriptableObject
{
    public event System.Action<float> Raised;
    public void Raise(float v) => Raised?.Invoke(v);
}

public class HealthBarView : MonoBehaviour
{
    [SerializeField] FloatChannel healthNormalized;
    [SerializeField] Image fill;
    void OnEnable()  => healthNormalized.Raised += OnHealth;
    void OnDisable() => healthNormalized.Raised -= OnHealth; // siempre en par
    void OnHealth(float v) => fill.fillAmount = v;
}
```

- Actualizar SOLO on-change, nunca en `Update`; textos numéricos: cachear el último valor y no regenerar strings por frame (GC) [ver: unity/rendimiento-unity].
- **Results reutiliza el mismo mecanismo**: un objeto `RunStats` (SO runtime o clase plana) que el gameplay va llenando (kills, tiempo, score) y el panel de Results lee al abrirse. Cero queries al mundo al morir.
- Daño flotante/waypoints sobre el mundo: proyección a un canvas Overlay único, no canvases world-space por objeto [ver: unity/ui-unity] §8.

## 7. Tutorial/onboarding: sistema de pasos implementado

El diseño (contextual > guiado, ≤8 palabras, salteable, adaptativo) está en [ver: gamedev/ux-ui-onboarding] §3-4. Implementación:

**Datos**: un `TutorialStep` (ScriptableObject o entrada de lista) = `id` estable (string), texto, target UI opcional (referencia o tag), **condición de completado** (evento de gameplay: "movió", "disparó", "abrió inventario") y trigger de aparición. Los pasos escuchan los MISMOS canales de eventos del HUD (sección 6) — el tutorial es un consumidor más, cero hooks especiales en gameplay.

**Manager**: secuencia (o set de tips independientes para tutorial contextual), muestra el paso activo, espera su condición, marca completado, siguiente. Skippeable siempre (botón visible que completa todos los flags).

**Resaltado (highlight) — patrón overlay con hueco:**

- Canvas "Tutorial" propio con `sortingOrder` por encima de todo; dentro, un dim oscuro semitransparente con `Raycast Target = ON` (bloquea todo el resto de la UI).
- El hueco: 4 Images opacas-translúcidas alrededor del rect del target (calculado con `RectTransform.GetWorldCorners` + conversión a coords del canvas) — el click pasa por el hueco al botón real de abajo. Simple y sin re-parenting.
- Alternativa: `Canvas.overrideSorting = true` + `sortingOrder` alto en el elemento destacado (lo eleva sobre el dim); requiere que el elemento tolere un Canvas anidado.
- Con cualquiera de las dos: probar que el botón "Atrás"/skip del propio tutorial no quede debajo del dim, y dar fallback si el target no existe (elemento oculto por resolución/estado) — un target nulo no puede colgar la secuencia.
- Flecha/manita apuntando al target: misma capa del dim, animada con unscaled time.

**Persistencia**: `PlayerPrefs.SetInt("tut_<id>_v1", 1)` por paso — clave **versionada** (cambiar el tutorial → subir sufijo → se re-muestra limpio). "Reset tutorial" en settings = borrar esos flags. Tips adaptativos: contador de fallos por mecánica en PlayerPrefs; el tip solo aparece al superar el umbral (quien lo hace bien nunca lo ve).

**Funnel**: log de analytics por paso (`tutorial_step_completed`, id) desde el día 1 — sin funnel no hay diagnóstico de FTUE [ver: gamedev/ux-ui-onboarding] §4.

## 8. Navegación multi-input: touch + mando + teclado

Reglas de diseño (focus visible, Back universal, loop en listas) en [ver: gamedev/ux-ui-onboarding] §2; APIs y gotchas de EventSystem en [ver: unity/input-system]. La unión operativa:

1. EventSystem con `InputSystemUIInputModule` (nunca `StandaloneInputModule` con el Input System).
2. **Cada `UIScreen.Show()` termina en `EventSystem.current.SetSelectedGameObject(firstSelected)`** — sin esto la navegación con mando/teclado está muerta. Al hacer `Pop`, restaurar el último seleccionado que la pantalla guardó al ocultarse (memoria de focus = navegación que se siente profesional).
3. **Back universal**: una sola suscripción global a la action `UI/Cancel` (`performed`) → `screenStack.Pop()`. Cubre Esc, B y círculo sin código por pantalla. No renombrar el map "UI" ni sus actions.
4. `Selectable.navigation`: `Automatic` sirve para menús simples; en grillas, tabs o layouts con elementos deshabilitados, pasar a `Explicit` y cablear los 4 vecinos — el automático salta raro. Listas verticales: loop último→primero (explícito); grillas: sin loop.
5. **Touch**: no hay focus — `SetSelectedGameObject` no aplica; targets ≥44pt/48dp y thumb zone [ver: gamedev/ux-ui-onboarding] §6; el HUD interactivo dentro del panel SafeArea [ver: unity/ui-unity] §7.
6. **Glifos por dispositivo**: detectar el device del último input (callback: `ctx.control.device`, o `PlayerInput.onControlsChanged` si usas PlayerInput) → actualizar prompts con `action.GetBindingDisplayString()` y ocultar el cursor con mando.
7. Clicks de UI que atraviesan al gameplay: switch de action map (ya resuelto por el PauseManager) + `IsPointerOverGameObject()` para el caso pointer-sobre-HUD en gameplay.
8. QA mínimo por pantalla: recorrerla completa con SOLO mando, SOLO teclado y SOLO touch. Si un elemento no se alcanza con D-pad, es un bug.

## 9. Transiciones y polish de UI

- **Fader global** (en el Canvas de Boot, `sortingOrder` máximo): un Image negro fullscreen + `CanvasGroup`; `FadeOut/FadeIn` como corrutinas con `unscaledDeltaTime` (funciona pausado y durante cargas). Es la pieza que hace TODAS las transiciones de escena limpias; su Image con `Raycast Target ON` mientras alpha > 0 bloquea clicks a mitad de transición.
- Fades de paneles: `CanvasGroup.alpha` (no `Graphic.color`, que ensucia el canvas) [ver: unity/ui-unity] §9.
- Slides/scale de menús: tween de `anchoredPosition`/`localScale` con lib de tweening (DOTween/PrimeTween/LitMotion [ver: unity/animacion-unity]) SIEMPRE en modo unscaled para UI. Nunca Animator en UI que anima constantemente [ver: unity/ui-unity].
- Duraciones (práctica común, no dogma): 0.15-0.3s para paneles y popups; más lento se siente pesado, más rápido no se lee. Easing: ease-out para entrar, ease-in para salir [ver: gamedev/game-feel].
- Popup: scale 0.9→1 + fade in, con overshoot sutil si el tono del juego lo permite.
- SFX de UI (hover, click, back, abrir/cerrar) en un AudioSource con `ignoreListenerPause = true` y ruteado al grupo de SFX del mixer [ver: unity/audio-unity].
- Botones: los 4 estados del `Selectable` (Normal/Highlighted/Pressed/Disabled) configurados; un botón sin feedback de press se siente muerto. Cero botones visibles sin acción implementada.
- Juice de UI (contadores que ruedan, barras con daño diferido, punch en pickups): [ver: feel-en-unity].

## Reglas prácticas

1. 3 escenas (`Boot`/`Menu`/`Game`) + paneles con CanvasGroup dentro de cada una; Settings, fader y loading UI viven en `Boot` (persistente) para estar disponibles desde Title Y desde Pause.
2. Un `ScreenStack` único gobierna paneles; la action `UI/Cancel` → `Pop()` es el Back universal de todo el juego.
3. Aplicar settings guardados en `Start` de Boot — jamás `AudioMixer.SetFloat` en `Awake`/`OnEnable` (restricción oficial).
4. Sliders de volumen: rango 0.0001–1, `Mathf.Log10(v) * 20` a dB; persistir el valor 0-1, no los dB.
5. No mezclar snapshots del mixer con exposed params en los mismos parámetros: `SetFloat` les quita el control a los snapshots.
6. `SetQualityLevel(i, false)` en runtime; dropdown desde `QualitySettings.names`, nunca índices hardcodeados (los levels se strippean por plataforma).
7. Idioma: esperar `LocalizationSettings.InitializationOperation` antes de tocar `SelectedLocale`; persistir el código en PlayerPrefs y reaplicar en Boot.
8. Pause = `timeScale 0` + `AudioListener.pause` + `PauseHaptics` + switch de action map Player→UI, en UNA función estática que todo el juego usa.
9. Todo lo que deba moverse en pausa (UI animada, spinner, fondo del menú): unscaled time — Animator en `UnscaledTime`, tween con flag unscaled, corrutinas con `WaitForSecondsRealtime`.
10. Móvil: `OnApplicationPause/Focus` → auto-pausa + persistir estado; matar la app no puede perder progreso.
11. Loading: `allowSceneActivation = false`, barra = `progress / 0.9f`, activar bajo el fade; `backgroundLoadingPriority = High` solo con loading screen puro.
12. No encolar otra AsyncOperation mientras haya una carga desactivada pendiente (la cola entera se congela).
13. HUD suscribe, gameplay publica (evento C# o canal SO); UI se actualiza on-change, nunca en `Update`, y Results lee un `RunStats` acumulado.
14. Tutorial: pasos con id estable + condición por evento de gameplay, flags versionados en PlayerPrefs (`tut_<id>_v1`), skip siempre visible, fallback si el target no existe, funnel instrumentado día 1.
15. `SetSelectedGameObject` en cada `Show()` de pantalla; restaurar el focus anterior en cada `Pop()`.
16. Grillas y layouts irregulares: `Selectable.navigation` Explicit; probar cada pantalla con solo mando, solo teclado y solo touch antes de darla por cerrada.
17. Fader global con unscaled time y raycast bloqueante mientras es visible: ninguna transición de escena "pela" sin él.
18. `PlayerPrefs.Save()` al cerrar el panel de settings; PlayerPrefs jamás para datos sensibles o progreso serio.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Volúmenes aplicados en `Awake` → mixer ignora o se comporta raro | `Start` o después (restricción documentada de `AudioMixer.SetFloat`) |
| Slider de volumen lineal → a mitad de slider casi silencio | `Mathf.Log10(v)*20`, slider min 0.0001 |
| Snapshot de pausa "deja de funcionar" tras mover un slider | `SetFloat` roba el parámetro a los snapshots — separar parámetros de slider y de snapshot |
| Pause con `timeScale = 0` pero la música y el input de gameplay siguen | `AudioListener.pause` + switch de action map; timeScale no toca audio ni `Update` |
| Menú de pausa congelado (animaciones muertas) | Animator `UnscaledTime`, tweens unscaled, `WaitForSecondsRealtime` |
| Al reanudar, el personaje salta/dispara por el click del botón "Resume" | Action map Player deshabilitado durante la pausa; reactivar DESPUÉS de cerrar el menú |
| Barra de loading que se clava en 90% "colgada" | Es el diseño de `allowSceneActivation`: normalizar `progress/0.9` y activar; el 10% restante no es asyncable |
| Segundo `LoadSceneAsync` encolado tras una carga desactivada → deadlock aparente | Una sola operación pendiente; activar antes de encolar la siguiente |
| Hitch al activar la escena aunque la carga fue async | `Awake/OnEnable` de la escena entrante corren en un frame: escena entrante ligera + fade cubriendo |
| HUD con referencia directa al Player → se rompe al testear la UI sola o cambiar de escena | Eventos/canales SO; el HUD compila y corre sin gameplay presente |
| Score/texto regenerando strings cada frame → GC spikes | Actualizar on-change con valor cacheado |
| Tutorial que se cuelga porque el target del highlight no existe en esa resolución/estado | Fallback por paso (mostrar sin highlight o saltar) + timeout; nunca bloquear la secuencia |
| Rehacer el tutorial tras cada update porque cambiaron los pasos | Claves de PlayerPrefs versionadas por paso |
| Menú navegable con ratón pero muerto con mando | `SetSelectedGameObject` al abrir cada pantalla; verificar `InputSystemUIInputModule` |
| Focus perdido al cerrar un popup (el mando "no hace nada") | El stack restaura el último seleccionado de la pantalla anterior |
| Settings distintos en Title vs Pause (o solo accesibles in-game) | Un solo panel de Settings en la escena Boot, invocado desde ambos |
| Settings que no persisten al matar la app | `PlayerPrefs.Save()` explícito al salir del panel (el flush automático solo ocurre en quit limpio) |
| Transición de escena que muestra un frame del mundo a medio cargar | Fader global: FadeOut → load → activar → FadeIn, siempre |

## Fuentes

- **AsyncOperation.allowSceneActivation — Unity Script Reference 6000.2** — comportamiento exacto: progress se detiene en 0.9, isDone false, la cola de AsyncOperations se paraliza, no usable en Awake.
- **Time.timeScale — Unity Script Reference 6000.2** — confirmación oficial de que FixedUpdate y corrutinas en WaitForSeconds no corren con timeScale 0.
- **AudioMixer.SetFloat — Unity Script Reference 6000.2** — prohibición de Awake/OnEnable/AfterSceneLoad y pérdida de control de snapshots sobre parámetros seteados.
- **AudioListener.pause — Unity Script Reference 6000.2** — pausa global de AudioSources + `ignoreListenerPause` para sonidos de menú (caso de uso citado por la propia doc).
- **AnimatorUpdateMode — Unity Script Reference 6000.2** — Normal/Fixed/UnscaledTime; UnscaledTime documentado como el modo para UI durante pausa.
- **QualitySettings.SetQualityLevel — Unity Script Reference 6000.2** — firma con `applyExpensiveChanges`, coste de cambiar AA, stripping de levels por plataforma.
- **Screen.SetResolution / FullScreenMode — Unity Script Reference 6000.2** — las 3 sobrecargas, aplicación al final del frame, los 4 valores del enum (`ExclusiveFullScreen` solo Windows, `FullScreenWindow` todas las plataformas, `MaximizedWindow` Windows/macOS, `Windowed` desktop).
- **PlayerPrefs — Unity Script Reference 6000.2** — tipos soportados, ubicación por plataforma, límite WebGL 1MB, advertencia de no-cifrado.
- **Application.backgroundLoadingPriority — Unity Script Reference 6000.2** — presupuestos de ms por frame de cada ThreadPriority (2/4/10/50).
- **Localization Settings — manual del paquete com.unity.localization 1.5** — cascada de startup selectors, inicialización async, WaitForCompletion no soportado en WebGL.
- **LocalizationSettings — API del paquete com.unity.localization 1.5** — `SelectedLocale`, `AvailableLocales`, `InitializationOperation` (yieldable), `SelectedLocaleAsync`.
- **"The Right Way to Pause the Game in Unity" — John French, GameDevBeginner** — inventario práctico de qué congela timeScale 0 y qué no; patrón de flag estático de pausa.
- **"The Right Way to Make a Volume Slider in Unity" — John French** — fórmula `Log10(v)*20`, rango 0.0001–1 y por qué la conversión lineal falla.
- **Base sintetizada**: [ver: gamedev/ux-ui-onboarding] (flujo de pantallas, settings obligatorios, tutoriales, FTUE, accesibilidad), [ver: unity/ui-unity] (Canvas, CanvasGroup, optimización, safe area), [ver: unity/input-system] (action maps, EventSystem, rebinding, glifos), [ver: unity/csharp-patrones] (canales SO, eventos), [ver: unity/arquitectura-unity] (escenas y carga aditiva), [ver: unity/audio-unity] (mixer y grupos).
