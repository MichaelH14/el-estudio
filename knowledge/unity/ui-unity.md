# UI en Unity: uGUI y UI Toolkit

> **Cuando cargar este archivo:** al construir cualquier interfaz de juego en Unity 6.x — HUD, menús, barras de vida, texto, UI móvil con notch — o al decidir entre uGUI y UI Toolkit, o al optimizar una UI que genera draw calls / rebuilds excesivos.

## 1. Decisión 2026: uGUI vs UI Toolkit

Estado real según la doc oficial de Unity 6.2: "UI Toolkit is intended to become the recommended UI system", pero uGUI sigue siendo "established and production-proven" mientras UI Toolkit está "in active development". Para UI de juego runtime, **uGUI sigue siendo el default seguro**; UI Toolkit ya es viable para proyectos con mucha UI tipo aplicación.

| Criterio | uGUI | UI Toolkit |
|---|---|---|
| Shaders/materiales custom en UI (glow, disolve, VFX) | ✅ Sí — razón oficial para elegirlo | ❌ No soportado |
| Animation Clips / Timeline sobre UI | ✅ | ❌ (solo transiciones USS) |
| UnityEvents serializados en Inspector / Visual Scripting | ✅ | ❌ |
| Mask con sprite arbitrario | ✅ (Mask / RectMask2D) | ❌ (solo clipping rectangular `overflow`) |
| Referenciar UI desde MonoBehaviours | ✅ Directo (drag & drop) | Vía `UIDocument.rootVisualElement.Q<T>()` |
| Estilos globales reutilizables | ❌ (a mano, prefabs) | ✅ USS/TSS (hojas de estilo) |
| Render sin texturas (vectorial), anti-aliasing de UI | ❌ | ✅ |
| UI muy densa (inventarios enormes, listas virtualizadas) | Costoso (pooling manual) | ✅ `ListView` virtualizado |
| World-space | ✅ Canvas World Space (siempre) | ✅ Solo desde Unity 6.2 (Panel Settings World Space) |
| Data binding runtime | ❌ (manual) | ✅ (bindea propiedades de cualquier `object` C#) |

**Criterio de decisión rápido:**
- HUD de juego con juice visual (shaders, partículas sobre UI, animación con Timeline) → **uGUI**.
- Menús/pantallas tipo aplicación, muchas vistas, listas largas, un equipo que piensa en CSS → **UI Toolkit**.
- Proyecto pequeño/mediano, un solo dev o agente: **uGUI para todo** es la opción con menos fricción y más documentación de terceros.
- No mezclar sistemas dentro de una misma pantalla; mezclarlos por pantallas (menú en UI Toolkit, HUD en uGUI) es válido pero cada uno trae su propio pipeline de input y ordenación.

[ver: unity6-actualidad] para el estado de la roadmap; [ver: gamedev/ux-ui-onboarding] para el diseño de la UI en sí.

## 2. uGUI: Canvas y render modes

Todo elemento uGUI vive bajo un `Canvas`. Orden de dibujo = orden en la Hierarchy (lo de abajo se dibuja encima). Reordenar por código: `SetAsFirstSibling()`, `SetAsLastSibling()`, `SetSiblingIndex(i)`.

| Render mode | Qué hace | Cuándo |
|---|---|---|
| **Screen Space - Overlay** | Se dibuja encima de todo, sin cámara; se ajusta solo a la resolución | HUD y menús estándar. Default correcto en el 90% de los casos |
| **Screen Space - Camera** | Canvas plano frente a una cámara concreta; FOV/perspectiva afectan la UI | UI que debe recibir post-proceso, efectos 3D sobre UI, o control de orden con otras cámaras. En URP también se puede poner la UI en una overlay camera del camera stack [ver: rendering-urp] |
| **World Space** | El Canvas es un objeto 3D más en la escena | UI diegética, barras de vida, paneles en el mundo (sección 8) |

Gotchas verificados:
- **Asigna siempre la cámara explícitamente** (`Canvas.worldCamera` / Event Camera). Un Canvas Screen Space - Camera sin cámara asignada busca la main camera con `GameObject.FindWithTag`, que es lento.
- Overlay usa solo posición/color/UV0 en vértices; Camera y World Space añaden normal y tangente. Shaders custom que necesiten más canales: activar "Additional Shader Channels" en el Canvas.
- El EventSystem es obligatorio para input. Con el Input System package, el módulo debe ser `InputSystemUIInputModule` (no `StandaloneInputModule`) [ver: input-system].

## 3. Canvas Scaler: multi-resolución

Componente `CanvasScaler` en el Canvas raíz. Modos:

- **Constant Pixel Size** — tamaño fijo en píxeles. Solo para editor tools o si gestionas escala a mano.
- **Scale With Screen Size** — **el modo correcto para juegos**. Compara la resolución actual con una Reference Resolution y escala todo el Canvas.
- **Constant Physical Size** — unidades físicas por DPI. Raro en juegos.

Con Scale With Screen Size, el **Screen Match Mode**:
- `Match Width Or Height` + slider Match: 0 = manda el ancho, 1 = manda el alto, valores intermedios interpolan.
- `Expand`: el canvas nunca es más pequeño que la referencia (nada se corta, aparecen márgenes).
- `Shrink`: el canvas nunca es más grande (puede cortar).

**Receta estándar (práctica común, no dogma oficial):** Reference Resolution 1920×1080 (landscape) o 1080×1920 (portrait); Match 0.5 como punto de partida. Si el layout es horizontal y lo crítico es que quepa a lo alto (HUD landscape), Match 1 (height); en portrait donde lo crítico es el ancho, Match 0. Probar siempre en al menos 16:9, 20:9 y 4:3 con el **Device Simulator** (Window > General > Device Simulator: simula forma de pantalla, resolución, orientación y safe area).

`Reference Pixels Per Unit` enlaza el pixels-per-unit de los sprites con la UI; déjalo consistente con tus sprites (default 100).

## 4. RectTransform: anchors y pivots

- **Anchors** (Anchor Min/Max, en fracciones 0–1 del padre): si min == max, el elemento tiene tamaño fijo relativo a ese punto; si min != max, el elemento **se estira** con el padre (cada esquina mantiene offset fijo a su anchor). El inspector cambia de Pos/Width/Height a Left/Right/Top/Bottom según el caso.
- **Pivot**: punto alrededor del cual ocurren rotación, escala y resize. Barra de vida que se vacía hacia la izquierda → pivot X = 0. Popup que crece desde el centro → pivot (0.5, 0.5).
- Regla: **resolver el layout responsive con anchors siempre que se pueda** — los anchors son gratis en runtime; los Layout Groups no (sección siguiente).
- Anchor presets (botón cuadrado arriba-izquierda del inspector): esquinas, centros y stretch. Alt+click también setea posición/tamaño.

Patrón típico de panel adaptativo: fondo con anchors stretch-stretch (min 0,0 / max 1,1, offsets 0) y contenido interno anclado a esquinas/centros concretos.

## 5. Auto layout: qué cuesta y cuándo usarlo

Componentes: `HorizontalLayoutGroup`, `VerticalLayoutGroup`, `GridLayoutGroup`, `ContentSizeFitter`, `LayoutElement` (min/preferred/flexible width y height; se asignan en ese orden según el espacio disponible).

Cómo calcula: 4 pasadas — anchos bottom-up, anchos top-down, altos bottom-up, altos top-down. Consecuencia documentada: los altos pueden depender de los anchos, **nunca al revés**. Los recálculos se agrupan al final del frame vía `LayoutRebuilder.MarkLayoutForRebuild`.

Coste real (guía oficial de optimización):
- Cada Layout Group que se marca dirty encola sorts y recálculos (`ICanvasElement`/`CanvasUpdateRegistry`); **layout groups anidados multiplican el coste** y se recalculan cuando cualquier hijo cambia.
- La recomendación oficial es **reemplazar layout groups por RectTransforms anclados** en todo lo que no cambie de estructura en runtime. Ejemplo de la guía: columna izquierda = anchors X(0, 0.5), Y(0, 1).
- Uso legítimo: contenido de cantidad variable en runtime (inventario, lista de jugadores). Uso ilegítimo: maquetar pantallas estáticas por comodidad de editor.
- `ContentSizeFitter` dentro de un Layout Group del padre = conflicto clásico (dos controladores peleando el mismo tamaño); Unity lo avisa en el inspector. Un solo controlador de tamaño por RectTransform.

## 6. TextMeshPro (TMP)

TMP es la solución de texto estándar; en Unity 6 viene integrado en el paquete `com.unity.ugui` 2.0 (su manual vive dentro de la doc de ese paquete; no se instala paquete aparte). El `Text` legacy existe pero no usarlo en trabajo nuevo: TMP usa atlas **SDF (signed distance field)** — nítido a cualquier escala/rotación.

**Font Asset** = textura atlas + material. Se crea con Window > TextMeshPro > Font Asset Creator, o Asset > Create > TextMeshPro > Font Asset. Valores verificados en doc oficial:
- Atlas 512×512 basta para la mayoría de fuentes **solo con ASCII**; padding 5 está bien para 512×512. Más caracteres (acentos completos, CJK) → subir resolución (1024/2048) o multi-atlas.
- Sampling Point Size: Auto Sizing (usa el mayor tamaño que quepa) para atlas estáticos.
- Render Mode: `SDFAA` es el más rápido y suficiente para casi todo; `SDF16`/`SDF32` para glifos complejos o texto muy pequeño.
- Character Set: para español incluir rango Unicode con áéíóúüñ¿¡ (custom range o custom characters), no el preset ASCII pelado.

**Atlas Population Mode:**
- `Static` — atlas horneado en editor con set fijo de caracteres. **Para el build final**: cero coste de rasterización en runtime.
- `Dynamic` — añade glifos al atlas en runtime según se necesiten. Cómodo en desarrollo y necesario para texto impredecible (nombres de usuario, chat); coste de CPU al añadir glifos y el atlas crece. La doc confirma que en Dynamic puedes cambiar el tamaño del atlas sin regenerarlo. "Clear Dynamic Data on Build" limpia los glifos acumulados al hacer build (y al cerrar el editor).
- Existe además una opción de poblar desde fuentes del sistema operativo (Dynamic OS, sin empaquetar el .ttf) — NO VERIFICADO en la doc de 6.2, confírmalo en el dropdown del editor antes de depender de ello.

**Fallbacks:** cadena de font assets para caracteres que faltan (emoji, CJK). Coste documentado: buscar en la lista consume CPU extra y **cada fuente adicional usada = draw calls adicionales**. Mantener la cadena corta y meter en el atlas principal todo lo previsible.

**Auto Size:** el equivalente TMP de Best Fit. La guía oficial de uGUI dice del Best Fit clásico: "should never be used" (spamea el atlas con tamaños). En TMP el patrón correcto: activar Auto Size en editor para encontrar el tamaño óptimo del peor caso, copiar ese valor como tamaño fijo, desactivar Auto Size en runtime.

## 7. Safe area móvil (notch / Dynamic Island)

`Screen.safeArea` devuelve un `Rect` **en píxeles, origen abajo-izquierda**, como máximo `Rect(0, 0, Screen.width, Screen.height)`. Patrón estándar uGUI: un panel "SafeArea" hijo directo del Canvas, stretch completo, y convertir el rect a anchors:

```csharp
public class SafeArea : MonoBehaviour
{
    RectTransform rt; Rect last;

    void Awake() { rt = (RectTransform)transform; Apply(); }
    void Update() { if (Screen.safeArea != last) Apply(); } // rotacion / cambio de pantalla

    void Apply()
    {
        last = Screen.safeArea;
        Vector2 min = last.position, max = last.position + last.size;
        min.x /= Screen.width; min.y /= Screen.height;
        max.x /= Screen.width; max.y /= Screen.height;
        rt.anchorMin = min; rt.anchorMax = max;
        rt.offsetMin = rt.offsetMax = Vector2.zero;
    }
}
```

- Todo el HUD interactivo va DENTRO del panel SafeArea; los fondos full-bleed (imágenes, video) van FUERA para que cubran hasta el borde físico.
- El chequeo en `Update` es barato (comparación de Rect) y cubre rotación de dispositivo; alternativa: reaccionar a cambios de orientación/resolución.
- Probar con Device Simulator (dibuja la línea de safe area de cada dispositivo simulado).
- En UI Toolkit el eje Y va arriba-izquierda: la doc oficial da la conversión `new Rect(safeArea.x, Screen.height - safeArea.y, safeArea.width, safeArea.height)`; aplicar como margins/padding del contenedor raíz.

## 8. World-space UI: barras de vida, nombres, indicadores

**Opción A — Canvas World Space (uGUI, siempre disponible):**
Receta oficial: Canvas → Render Mode World Space; darle un tamaño en píxeles razonable (la doc sugiere 800×600 de partida) y escalar con `escala = metros_deseados / ancho_px` (ej. 2 m de ancho con canvas de 800 px → escala 0.0025 uniforme en X/Y/Z). Asignar Event Camera si es interactivo.

Barra de vida sobre la cabeza (billboard):

```csharp
public class Billboard : MonoBehaviour
{
    Camera cam;
    void Start() => cam = Camera.main;
    void LateUpdate() =>
        transform.rotation = cam.transform.rotation; // mismo giro que la camara, sin roll raro
}
```

Coste: **cada Canvas World Space es un canvas más que batchear**. Para 50 enemigos con barra de vida, NO usar 50 canvases con Layout Groups: un solo canvas world-space por unidad con 2 Images (fondo + fill con `Image.type = Filled` o escala X con pivot 0), raycast target off en todo, y pooling de las barras [ver: rendimiento-unity].

**Opción B — Overlay + proyección (recomendada para indicadores):** un solo Canvas Screen Space - Overlay y posicionar los marcadores con `Camera.WorldToScreenPoint`:

```csharp
Vector3 sp = cam.WorldToScreenPoint(target.position + Vector3.up * 2f);
marker.gameObject.SetActive(sp.z > 0);          // detras de camara = ocultar
marker.position = sp;                            // marker es RectTransform en canvas Overlay
```

Ventajas: un solo canvas, tamaño constante en pantalla, fácil de clampear a los bordes para indicadores off-screen. Es el patrón correcto para waypoints, nombres y daño flotante.

**Opción C — UI Toolkit World Space (desde Unity 6.2):** Panel Settings con render mode World Space posiciona documentos UI Toolkit en la escena 3D, con configuración de input propia (Panel Input Configuration). Verificado: la página existe en el manual 6000.2 y no existe en 6000.0/6000.1 — no usar este camino si el proyecto está en Unity 6.0/6.1.

## 9. Optimización uGUI

Modelo mental verificado (guía oficial "Optimizing Unity UI"): **cuando cualquier elemento dibujable de un Canvas cambia, el Canvas entero rehace su batch** — analiza todos los elementos, no solo el que cambió. Markers de Profiler: `Canvas.BuildBatch` y `Canvas.SendWillRenderCanvases`.

**Separar por frecuencia de cambio (la optimización #1):**
- Mínimo 2-3 canvases (o sub-canvases anidados): estático (fondos, marcos, labels fijos) / dinámico poco frecuente (contadores, vida) / dinámico por frame (timer, minimapa).
- Un sub-canvas (Canvas anidado) aísla sus cambios: no ensucia al padre ni a hermanos.
- No fragmentar en docenas: la propia guía dice que desde Unity 5.2 no hace falta partir agresivamente. 3-6 canvases bien elegidos.

**Raycast targets (input):**
- `Raycast Target` OFF en TODO lo decorativo (imágenes de fondo, iconos, texto no clicable). El GraphicRaycaster itera la lista de targets e intersecta jerarquía: "the smaller the list... the faster each Raycast test".
- TMP y las Images lo traen ON por defecto — auditar siempre. Preset o script de editor que lo apague en masa vale la pena en proyectos grandes.

**Mostrar/ocultar UI:**
- Ocultar un panel que volverá a aparecer: **desactivar el componente `Canvas`** (`canvas.enabled = false`), no `SetActive(false)`. Deja los meshes en memoria, no dispara OnEnable/OnDisable, y al reactivar no hay rebuild ni re-batch.
- Nunca "ocultar" con alpha 0: se sigue rasterizando y pagando fill-rate.
- `CanvasGroup.alpha` para fades: se aplica a nivel de CanvasRenderer sin regenerar geometría (cambiar `Graphic.color` sí marca dirty el canvas).
- UI full-screen opaca abierta → desactivar las cámaras de mundo que quedan tapadas (se ahorra todo el render 3D).

**Batching y fill-rate:**
- El orden de hermanos determina el batching: elementos con el mismo material intercalados con otro material rompen el batch (A,B,C: si B se interpone, A y C no se batchean). Diagnóstico: Frame Debugger + Profiler UI → columna "Batch Breaking Reason".
- Atlas de sprites de UI (un atlas = un material = batches grandes) [ver: assets-pipeline-git].
- Overdraw: minimizar capas de imágenes full-screen apiladas; combinar decoración en un solo sprite cuando se pueda.
- `Mask` usa stencil y añade draw calls; para clipping rectangular usar `RectMask2D`, que además excluye del batching los elementos totalmente fuera del viewport.

**Listas y scroll:**
- ScrollRect con cientos de items = pooling obligatorio (reutilizar solo las celdas visibles + un margen corto, nunca instanciar todo el dataset). La guía sugiere incluso placeholders con `LayoutElement` para los huecos, y usar `RectMask2D` para acotar qué se recicla.
- `Canvas.pixelPerfect` fuerza el alineado a la rejilla de píxeles (solo aplica en Screen Space); no tiene coste de rebuild, pero en canvases con scroll/animación produce movimiento con "escalones" en vez de suave — desactivarlo ahí por fluidez, no por performance.
- Animator sobre elementos UI ensucia el canvas **cada frame aunque el valor no cambie**: para UI animada constante, separarla a su propio canvas; para tweens puntuales, usar código/tweening en vez de Animator.

[ver: rendimiento-unity] para Profiler y presupuestos de frame; [ver: gamedev/game-feel] para qué animar en la UI.

## 10. UI Toolkit runtime: lo mínimo operativo

Piezas: **UXML** (estructura, ~HTML), **USS** (estilo, sintaxis CSS con adaptaciones de Unity), **UIDocument** (MonoBehaviour que instancia el UXML en escena), **PanelSettings** (asset: cómo se renderiza el panel).

- Layout: motor **Yoga** (subset de Flexbox). Default: `flex-direction: column` (eje principal vertical, al revés que CSS web). La doc recomienda evitar `position: absolute` salvo overlays/popups.
- PanelSettings ≈ Canvas + CanvasScaler: Scale Mode (`Constant Pixel Size` / `Constant Physical Size` / `Scale With Screen Size` con Reference Resolution y Match Width Or Height), Sort Order entre paneles, Theme Style Sheet (TSS), Target Texture.
- Acceso desde C# y eventos:

```csharp
public class MenuController : MonoBehaviour
{
    Button playBtn;

    void OnEnable()
    {
        var root = GetComponent<UIDocument>().rootVisualElement;
        playBtn = root.Q<Button>("play-button");        // por name del UXML
        playBtn.RegisterCallback<ClickEvent>(OnPlay);
    }
    void OnDisable() => playBtn.UnregisterCallback<ClickEvent>(OnPlay); // evitar leaks

    void OnPlay(ClickEvent evt) { /* ... */ }
}
```

- **Runtime data binding** (Unity 6): bindea propiedades de cualquier `object` C# a controles (data source + binding path, modos y conversores) — elimina el boilerplate de "actualizar label cuando cambia el modelo".
- Listas grandes: `ListView` virtualiza items (solo crea los visibles) — la ventaja killer frente a uGUI para inventarios/leaderboards.
- Performance runtime documentada: `VisualElement.usageHints` (setear ANTES de añadir el elemento al panel; después lanza excepción) para elementos que se mueven/transforman mucho; el dynamic atlas agrupa texturas para no romper batches; evitar teselación de mesh excesiva en dispositivos modestos.
- Los estilos inline en C# (`element.style.x`) pisan al USS; preferir clases USS + `AddToClassList`/`RemoveFromClassList` para estados.

## Reglas practicas

1. Default de juego: uGUI. UI Toolkit solo si el proyecto es UI-céntrico (mucha pantalla tipo app, listas enormes) y no necesitas shaders custom ni Timeline sobre UI.
2. Canvas raíz: Screen Space - Overlay + CanvasScaler en Scale With Screen Size, Reference 1920×1080 (o 1080×1920 portrait), Match según qué eje manda en tu layout.
3. Separa la UI en 3-6 canvases por frecuencia de cambio: estático / ocasional / por-frame. Nada que cambie cada frame comparte canvas con nada estático.
4. Todo elemento decorativo: `Raycast Target = false`. Audítalo antes de cerrar cada pantalla.
5. Layout responsive con anchors; Layout Groups SOLO donde la cantidad de hijos varía en runtime. Cero layout groups anidados profundos.
6. Un solo controlador de tamaño por RectTransform (no ContentSizeFitter dentro de Layout Group que ya controla ese eje).
7. Texto siempre TMP. Atlas Static para el build (con áéíóúüñ¿¡ incluidos); Dynamic solo para texto impredecible, con Clear Dynamic Data on Build activo.
8. TMP Auto Size: úsalo en editor para hallar el tamaño, fíjalo, apágalo.
9. Panel SafeArea (anchors desde `Screen.safeArea`) como raíz de todo el HUD interactivo en móvil; fondos full-bleed fuera de él. Probar en Device Simulator con un dispositivo con notch.
10. Mostrar/ocultar paneles frecuentes: `canvas.enabled`, no `SetActive`; fades con `CanvasGroup.alpha`; jamás alpha 0 como "oculto".
11. Asigna `worldCamera`/Event Camera explícita en todo Canvas no-Overlay.
12. Indicadores sobre el mundo (nombres, waypoints, daño): un solo canvas Overlay + `WorldToScreenPoint`, no un canvas world-space por objeto. Barras de vida en masa: canvas world-space simple por unidad, sin layout groups, con pooling.
13. Scroll con muchos items: pooling de celdas (uGUI, solo las visibles + margen) o `ListView` (UI Toolkit). `pixelPerfect` off en canvases con scroll/animación para movimiento suave (no es una optimización de CPU, es rendering).
14. No animes UI con Animator si corre constantemente; ensucia el canvas cada frame. Tween por código o canvas aparte.
15. Sprites de UI en atlas; vigila "Batch Breaking Reason" en el Profiler UI y el Frame Debugger antes de dar una pantalla por terminada.
16. Clipping rectangular: `RectMask2D`. `Mask` (stencil) solo si necesitas forma arbitraria.
17. En UI Toolkit: clases USS para estados (no estilos inline), `UnregisterCallback` en `OnDisable`, `usageHints` antes de añadir al panel, `ListView` para listas.
18. UI Toolkit world-space: solo existe desde Unity 6.2 — verifica la versión del proyecto antes de planearlo.

## Errores comunes

| Error | Antídoto |
|---|---|
| Toda la UI en un solo Canvas; el timer que cambia cada frame fuerza re-batch de todo | Sub-canvases por frecuencia de cambio; profiler: `Canvas.BuildBatch` alto = canvas mal partido |
| Raycast targets por defecto en todo → GraphicRaycaster caro y clicks "fantasma" que bloquean botones | Apagar Raycast Target en decorativos; buscar qué bloquea con el Event System debug |
| Maquetar pantallas estáticas con Vertical/Horizontal Layout Groups anidados | Anchors + posiciones fijas; layout groups solo para contenido variable |
| Best Fit / Auto Size activo en runtime en decenas de textos | Tamaño fijo calculado una vez en editor |
| Atlas TMP con preset ASCII y el juego en español → tofu/□ en áéíóúñ | Character set custom con el rango completo del idioma; probar con textos reales |
| Fuente Dynamic en build final acumulando glifos y CPU | Static para ship; Clear Dynamic Data on Build |
| HUD pegado a los bordes físicos; el notch/isla tapa botones | Panel SafeArea con anchors de `Screen.safeArea`; probar en Device Simulator |
| Ocultar paneles con `SetActive(false)`/alpha 0 y reabrirlos con hitch | `canvas.enabled = false`; alpha vía CanvasGroup solo para fades reales |
| Canvas Screen Space - Camera sin cámara asignada → búsqueda lenta de main camera | Asignar `worldCamera` siempre, por código en el spawn si hace falta |
| 50 barras de vida = 50 canvases con layout groups y raycasts | Canvas mínimo por unidad (2 Images, raycast off) o proyección a un canvas Overlay único |
| UI se ve bien en 16:9 del editor y rota en 20:9 / tablet | Device Simulator multi-dispositivo + Match del CanvasScaler elegido a propósito; nunca dar por buena una pantalla probada en una sola relación de aspecto |
| Elementos UI Toolkit posicionados todo con `position: absolute` | Flexbox (Yoga) con `flex-grow`/`align-items`; absolute solo overlays |
| Callbacks de UI Toolkit registrados sin unregister → leaks al recargar UI | Par Register/Unregister en OnEnable/OnDisable |
| Asumir que UI Toolkit acepta el shader custom del HUD o máscaras con sprite | No los soporta: esa pantalla va en uGUI |
| Animator "idle" sobre la UI ensuciando el canvas cada frame | Quitar el Animator o aislar ese elemento en su canvas |

## Fuentes

- Comparison of UI systems in Unity — Unity Manual 6000.2 (docs.unity3d.com) — la posición oficial de Unity sobre uGUI vs UI Toolkit vs IMGUI y la tabla de capacidades que faltan en UI Toolkit.
- Canvas — paquete com.unity.ugui 2.0, Unity Manual — render modes, orden de dibujo, canales de vértice y Additional Shader Channels.
- Canvas Scaler — paquete com.unity.ugui 2.0, Unity Manual — modos de escala, reference resolution, screen match mode.
- Optimizing Unity UI (guía de Ian Dundore) — learn.unity.com — la fuente canónica de rendimiento uGUI: rebuild/batching, sub-canvases, raycast targets, layout groups, ocultar canvas, Best Fit, fill-rate, batch breaking.
- Basic Layout (RectTransform) — paquete com.unity.ugui 2.0, Unity Manual — anchors, pivots, campos de posición.
- Auto Layout — paquete com.unity.ugui 2.0, Unity Manual — min/preferred/flexible, orden de pasadas del layout, LayoutRebuilder.
- Screen.safeArea — Unity Script Reference 6000.2 — semántica exacta del Rect (píxeles, origen abajo-izquierda) y conversión para UI Toolkit.
- Device Simulator — Unity Manual 6000.2 — qué simula (pantalla, orientación, safe area) para verificar UI móvil.
- TextMeshPro Font Assets / Font Asset Creator / Font Asset properties — docs TMP dentro de com.unity.ugui 2.0 — SDF, valores de atlas/padding, render modes, population modes, Clear Dynamic Data on Build, coste de fallbacks.
- Get started with runtime UI — Unity Manual 6000.2 — flujo UIDocument + UXML + Q<T> + RegisterCallback con código oficial.
- Panel Settings asset — Unity Manual 6000.2 — scale modes, sort order, theme style sheet para runtime UI Toolkit.
- Layout engine (UI Toolkit) — Unity Manual 6000.2 — Yoga/Flexbox, default flex-direction column, aviso sobre position absolute.
- USS introduction — Unity Manual 6000.2 — relación USS/CSS.
- Performance consideration for runtime UI — Unity Manual 6000.2 — usageHints, dynamic atlas, teselación.
- Runtime data binding — Unity Manual 6000.2 — binding de objetos C# a controles en runtime.
- World space UI (UI Toolkit) — Unity Manual 6000.2 — confirmación de que existe solo desde 6.2 (la página da 404 en los manuales 6000.0 y 6000.1).
- Creating a World Space UI — paquete com.unity.ugui 2.0, Unity Manual — receta oficial de canvas world-space con números de escala.
- VisualElement.usageHints — Unity Script Reference 6000.2 — restricción de asignación antes de añadir al panel.
