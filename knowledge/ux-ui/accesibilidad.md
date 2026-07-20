# Accesibilidad (a11y)

> **Cuando cargar este archivo:** al diseñar o evaluar cualquier interfaz de app o producto (web y móvil) y necesites que sea usable por personas con discapacidad visual, auditiva, motora o cognitiva — antes de elegir colores/contraste, marcar HTML semántico, definir foco de teclado, tamaños de touch target, animaciones, o al montar una auditoría de a11y. Numérico y operativo (ratios, px, dp, niveles WCAG). Para HUD/tutoriales/settings de accesibilidad EN JUEGOS → [ver: gamedev/ux-ui-onboarding] (remapeo, subtítulos, daltonismo in-game, focus con mando); esa base ya cubre el ángulo juego y aquí NO se repite.

Fuente normativa de referencia: **WCAG 2.2** (W3C, Recommendation oficial). Los números duros de este archivo salen verificados contra las páginas *Understanding* de w3.org, Apple HIG y web.dev de Google. Este archivo es UX/UI general de producto; el lado juegos vive en gamedev.

---

## 1. Por qué accesibilidad (alcance, legal, y que mejora la UX de todos)

**No es un nicho.** La OMS estima ~16% de la población mundial con alguna discapacidad significativa. Pero la a11y no se diseña solo para discapacidad *permanente*: se diseña para un espectro que incluye a todo el mundo en algún momento.

| Tipo de limitación | Permanente | Temporal | Situacional (le pasa a cualquiera) |
|---|---|---|---|
| **Visión** | Ceguera, baja visión | Ojo operado, conjuntivitis | Sol directo en la pantalla, brillo bajo, pantalla sucia |
| **Motora** | Amputación, temblor | Brazo enyesado | Un bebé en brazos, celular a una mano en el metro |
| **Auditiva** | Sordera | Infección de oído | Bar ruidoso, oficina en silencio sin audífonos |
| **Cognitiva** | Dislexia, TDAH, autismo | Migraña, medicación | Distracción, prisa, segundo idioma, cansancio |

(Marco *Persona/Temporal/Situacional* de Microsoft Inclusive Design; concepto alineado con WAI.)

- **Curb-cut effect** (efecto de la rampa de acera): las rampas se hicieron para sillas de ruedas y hoy las usan carritos, maletas y bicis. Igual en digital — features de a11y que ayudan a *todos*: subtítulos en un bar ruidoso, alto contraste bajo el sol, navegación por teclado para power-users, texto escalable para présbitas (W3C WAI).
- **Legal (varía por jurisdicción — verificar siempre):** EE. UU. → ADA + Section 508 (refieren WCAG 2.0/2.1 AA); UE → EN 301 549 y el **European Accessibility Act** (aplicación desde jun-2025 a muchos productos y servicios digitales de consumo); Ontario → AODA. El estándar legal más común es **WCAG 2.1/2.2 nivel AA**. Litigios ADA por sitios inaccesibles se cuentan por miles al año en EE. UU.
- **Realidad del mercado:** el informe *WebAIM Million* reporta año tras año que **~96% de las home pages** tienen fallos WCAG detectables automáticamente. La barra está baja: cumplir lo básico ya diferencia.
- **La a11y ES usabilidad.** Estructura clara, contraste alto, targets grandes, foco visible y lenguaje simple mejoran la conversión y reducen errores para el 100% de los usuarios, no solo para quien usa lector de pantalla (NN/g). [ver: fundamentos-ux]

---

## 2. WCAG a nivel operativo: niveles y principios POUR

### Niveles de conformidad

| Nivel | Qué es | Cuándo apuntar |
|---|---|---|
| **A** | Mínimo indispensable; sin esto la interfaz es inusable para algún grupo | Piso absoluto, nunca por debajo |
| **AA** | El **objetivo real de producto** y el estándar legal de facto | Meta por defecto de todo proyecto serio |
| **AAA** | Ideal; a menudo no aplicable a todo el contenido | Buscar donde sea barato (respeta-motion, foco fuerte); no se exige AAA global |

Regla operativa: **AA es la meta**. Los criterios AAA útiles y baratos (contraste 7:1, foco reforzado, `prefers-reduced-motion`) se adoptan como bonus, no como requisito global.

### Los 4 principios POUR (W3C WAI)

| Principio | Significa | Ejemplos de criterio |
|---|---|---|
| **P**erceptible | La info se puede percibir por algún sentido disponible | Alt text, contraste, subtítulos, texto escalable |
| **O**perable | Se puede navegar y operar con cualquier input | Teclado, foco visible, sin trampas, targets grandes, tiempo suficiente |
| **U**nderstandable | Info e interfaz claras y predecibles | Lenguaje simple, comportamiento consistente, errores explicados |
| **R**obust | Funciona en distintos navegadores y tecnologías asistivas | HTML válido, roles/labels correctos, ARIA bien puesto |

### Qué cambió en WCAG 2.2 (2023)

**9 criterios nuevos** y **1 eliminado** (verificado en w3.org/WAI new-in-22):

| SC nuevo | Nivel | De qué va |
|---|---|---|
| 2.4.11 Focus Not Obscured (Minimum) | AA | Sticky headers/footers no deben tapar el elemento con foco |
| 2.4.12 Focus Not Obscured (Enhanced) | AAA | Igual, sin ocultarlo *nada* |
| 2.4.13 Focus Appearance | AAA | Indicador de foco de tamaño y contraste mínimos (ver §6) |
| 2.5.7 Dragging Movements | AA | Toda acción de arrastre debe tener alternativa de tap simple |
| 2.5.8 Target Size (Minimum) | AA | Targets ≥ 24×24 CSS px (ver §9) |
| 3.2.6 Consistent Help | A | Mecanismo de ayuda en la misma posición entre páginas |
| 3.3.7 Redundant Entry | A | No re-pedir info ya ingresada en el mismo flujo |
| 3.3.8 Accessible Authentication (Min) | AA | No exigir pruebas cognitivas (recordar/transcribir) para loguearse |
| 3.3.9 Accessible Authentication (Enhanced) | AAA | Igual, sin excepciones de reconocimiento de objetos |

- **Eliminado: 4.1.1 Parsing** — quedó obsoleto (los navegadores modernos ya manejan HTML mal formado). No perseguir "validación HTML perfecta" como criterio de a11y.

---

## 3. Contraste de color: los ratios exactos

Todos verificados contra las páginas *Understanding* de WCAG 2.2. El ratio se calcula con la luminancia relativa de los dos colores; **no se redondea** (4.499:1 NO cumple 4.5:1).

| Qué | Nivel A/AA | Ratio mínimo | SC |
|---|---|---|---|
| **Texto normal** (< 18 pt / < 14 pt bold) | AA | **4.5:1** | 1.4.3 |
| **Texto grande** (≥ 18 pt ≈ 24 px, o ≥ 14 pt bold ≈ 18.5 px) | AA | **3:1** | 1.4.3 |
| **Componentes de UI y objetos gráficos** (bordes de input, iconos, estados, partes de un gráfico necesarias para entenderlo) | AA | **3:1** | 1.4.11 |
| Texto normal (nivel reforzado) | AAA | **7:1** | 1.4.6 |
| Texto grande (nivel reforzado) | AAA | **4.5:1** | 1.4.6 |

- **Definición exacta de "texto grande" (1.4.3):** al menos **18 pt** (≈ 24 px) normal, o **14 pt bold** (≈ 18.5 px). Conversión W3C: 1pt ≈ 1.333px.
- **Exenciones de 1.4.3:** texto que es parte de un **logo/marca**, texto **puramente decorativo**, y texto en **componentes inactivos (disabled)** — no tienen requisito de contraste.
- **1.4.11 (non-text)** es la que suele fallar en diseños "limpios": un input con borde gris clarito < 3:1 contra el fondo blanco NO cumple; un icono-botón sin label cuyo glifo no llega a 3:1, tampoco. El *estado* también cuenta (un checkbox marcado debe distinguirse a ≥ 3:1).

### Cómo medirlo y con qué

- **Fórmula:** `(L1 + 0.05) / (L2 + 0.05)`, con L = luminancia relativa (la clara arriba). No hace falta calcularla a mano.
- **Herramientas:** WebAIM Contrast Checker (web), TPGi **Colour Contrast Analyser** (app de escritorio con cuentagotas — mide sobre pantalla, ideal para móvil/imágenes), Stark y el propio contrast picker de **Chrome DevTools** (muestra el ratio y las líneas de 3:1 / 4.5:1 en el selector de color).
- **Truco de sistema de diseño:** define contraste con **lightness/luminancia**, no con saturación. Grises "de marca" sobre color suelen fallar; para texto secundario baja la lightness, no solo la opacidad. Un gris a 60% de opacidad sobre fondos variables tiene contraste impredecible. [ver: fundamentos-visuales] · [ver: sistemas-diseno]
- **Dark mode no es gratis:** el contraste se recalcula por tema. El blanco puro (#FFF) sobre negro puro (#000) a 21:1 genera *halation* (halo) para muchos usuarios; usar off-white (#E8E8E8-ish) sobre gris muy oscuro, verificando que siga ≥ 4.5:1. [ver: mobile-ux]

---

## 4. No depender solo del color (daltonismo)

**SC 1.4.1 Use of Color — nivel A** (verbatim): *"Color is not used as the only visual means of conveying information, indicating an action, prompting a response, or distinguishing a visual element."*

~8% de los hombres y ~0.5% de las mujeres tienen algún tipo de daltonismo (deuteranopia/protanopia = rojo-verde, el más común; tritanopia = azul-amarillo). El clásico rojo-vs-verde para error/éxito es exactamente lo que no se ve.

| Antipatrón (solo color) | Antídoto (color + segunda señal) |
|---|---|
| Campo inválido = borde rojo | Borde rojo **+ icono + texto** de error debajo |
| Éxito verde / error rojo (toast) | Icono distinto (✓ / ✕) + palabra |
| Links solo por color dentro de párrafo | Subrayado (o negrita + otra señal); no basta el azul |
| Serie de gráfico solo por color de línea | Etiquetas directas, patrones/dashes, marcadores de forma |
| Estado "activo/seleccionado" solo por tinte | Tinte + borde/underline/peso/checkmark |
| Mapa de calor rojo↔verde | Paleta segura para daltónicos (ej. viridis) + valores |

- Probar en **escala de grises**: si en B/N no distingues estados/series, dependes del color.
- No fiarse solo de simuladores de daltonismo; la regla es estructural: **toda info por color lleva una redundancia** (texto, icono, forma, posición o patrón).

---

## 5. Lectores de pantalla: semántica, alt, labels, orden

Un lector de pantalla (VoiceOver iOS/macOS, TalkBack Android, NVDA/JAWS en Windows) **linealiza** la interfaz: la lee y navega elemento por elemento. Lo que da sentido no es lo visual, es el **árbol de accesibilidad** que construye el HTML/roles. Diseño bonito con `<div>` para todo = interfaz muda o caótica.

### Semántica primero (WebAIM)

- **Encabezados h1–h6 como esquema real** del contenido, sin saltar niveles por estética. Los usuarios de lector saltan de heading en heading para escanear (equivalente auditivo del escaneo visual). Una sola `<h1>` por vista.
- **Landmarks / sectioning:** `<header> <nav> <main> <aside> <footer>` (o roles ARIA equivalentes). Permiten saltar directo a "contenido principal" o "navegación".
- **HTML nativo antes que ARIA.** Un `<button>` real ya es focusable, anunciado como botón y operable con Enter/Espacio; un `<div onclick>` no es nada de eso. **Primera regla de ARIA (WAI-ARIA APG): si existe un elemento HTML nativo con la semántica que necesitas, úsalo — no lo reconstruyas con ARIA.** ARIA mal puesto es peor que sin ARIA.
- **Listas, tablas y forms con su marcado real** (`<ul>`, `<th scope>`, `<label>`), no simulados con estilos.

### Texto alternativo (SC 1.1.1, nivel A)

| Caso | alt correcto |
|---|---|
| Imagen informativa (foto de producto) | Describe lo relevante: `alt="Zapato rojo de correr, vista lateral"` |
| Icono con función, sin texto visible (lupa = buscar) | `alt`/`aria-label="Buscar"` — describe la **acción**, no el dibujo |
| Imagen puramente decorativa | `alt=""` (vacío) para que el lector la **ignore** — nunca omitir el atributo |
| Imagen compleja (gráfico) | alt corto + descripción larga adyacente o en tabla de datos |

Sin `alt`, muchos lectores leen el **nombre de archivo** (`IMG_2287.png`) — ruido puro.

### Formularios

- **Todo input con `<label>` asociado** (`for`/`id`) o `aria-label`. Un placeholder **NO es label** (desaparece al escribir y suele fallar contraste). [ver: patrones-ui]
- Errores: asociados al campo (`aria-describedby`) y anunciados; no solo un borde rojo. Instrucciones y formato esperado, antes del campo.
- Agrupar radios/checkboxes en `<fieldset>` + `<legend>`.

### Orden de lectura/foco

- El **orden del DOM = orden de lectura**. Si el CSS (flex/grid/`order`) reordena visualmente pero el DOM queda desordenado, el lector y el teclado leen en el orden "viejo" → confusión (SC 1.3.2 Meaningful Sequence, A). Mantener DOM y visual alineados. [ver: interaccion-microux]

---

## 6. Navegación por teclado

Base de la operabilidad: si algo funciona con mouse/touch, **debe funcionar solo con teclado** (SC 2.1.1 Keyboard, A). Cubre a quien usa teclado, switch, control por voz o lector de pantalla.

| Requisito | Regla concreta | SC |
|---|---|---|
| **Foco visible** | Nunca `outline: none` sin reemplazo. Todo elemento enfocable muestra un indicador claro | 2.4.7 (AA) |
| **Orden lógico** | El tab sigue el flujo visual (arriba→abajo, izq→der). No usar `tabindex` > 0 | 2.4.3 (A) |
| **Skip link** | "Saltar al contenido" como primer foco, para brincar navegación repetida | 2.4.1 (A) |
| **Sin trampas** | Si el foco entra a un componente, debe poder salir solo con teclado (Esc/Tab). Modales: atrapar foco *dentro del modal a propósito*, y devolverlo al cerrar | 2.1.2 (A) |
| **Foco no tapado** | Headers/footers sticky no deben ocultar el elemento enfocado | 2.4.11 (AA, nuevo 2.2) |
| **Foco fuerte** (bonus) | Indicador ≥ área de un perímetro de **2 px** y **cambio de contraste 3:1** entre estado normal y enfocado | 2.4.13 (AAA) |

### `tabindex` (WebAIM)

- `tabindex="0"` → hace enfocable un elemento no nativo (solo para widgets custom).
- `tabindex="-1"` → fuera del orden de tab, pero enfocable por JS (`.focus()`) — para mover foco a un modal/panel al abrirlo.
- `tabindex="1+"` → **nunca**; rompe el orden natural.

- **Elementos nativos ya son enfocables** (links, buttons, inputs). Si te ves poniendo `tabindex` y handlers de teclado en un `<div>`, casi siempre la respuesta es usar un `<button>`.
- **Al abrir un overlay/modal**, mover el foco al modal; al cerrarlo, devolverlo al disparador. (Mismo principio que el "focus explícito al abrir popup" del lado juegos con mando → [ver: gamedev/ux-ui-onboarding].)
- **SC 2.5.7 Dragging Movements (AA, nuevo 2.2):** toda acción que hoy exige arrastrar (reordenar lista, slider, mapa) necesita una alternativa que NO sea arrastre (botones +/−, tap-para-mover, inputs) — cubre a quien no puede hacer gestos precisos.

---

## 7. Tamaño de texto y zoom

El usuario debe poder agrandar el texto sin que el layout se rompa. Verificado contra WCAG 2.2.

| Requisito | Número exacto | SC |
|---|---|---|
| **Redimensionar texto** hasta 200% sin perder contenido ni función | **200%** | 1.4.4 (AA) |
| **Reflow**: contenido usable sin scroll en 2 direcciones a un ancho equivalente a **320 CSS px** (= 1280 px al **400% de zoom**), o **256 CSS px** de alto para contenido horizontal | 320 px / 256 px / 400% | 1.4.10 (AA) |
| **Text Spacing**: sin pérdida de contenido cuando el usuario fuerza line-height **1.5×**, espacio tras párrafo **2×**, letter-spacing **0.12×**, word-spacing **0.16×** (× = tamaño de fuente) | 1.5 / 2 / 0.12 / 0.16 | 1.4.12 (AA) |

Implicaciones de diseño/implementación:

- **Nunca fijar el font-size en `px` absolutos que ignoren la preferencia del usuario.** En web usar unidades relativas (`rem`) y respetar el font-size base del navegador; en iOS soportar **Dynamic Type**, en Android el **font scale** del sistema. Un móvil con texto al 200% no debe recortar botones ni forzar scroll horizontal.
- **No `maximum-scale=1` ni `user-scalable=no`** en el viewport meta — bloquea el pinch-zoom y es un fallo directo. [ver: mobile-ux]
- **Contenedores que crecen con el contenido**, no alturas fijas en `px` para texto. Probar el reflow a 320 px de ancho (móvil chico) y con el texto escalado: nada se debe solapar ni cortar. [ver: fundamentos-visuales]
- El escalado que rompe layout (scroll en dos ejes) es el mismo problema que en juegos → [ver: gamedev/ux-ui-onboarding].

---

## 8. Sensibilidad al movimiento

Animación innecesaria causa **mareo, náusea y dolor de cabeza** a personas con trastornos vestibulares (W3C, SC 2.3.3). Además, el flash puede provocar **convulsiones**.

- **SC 2.3.3 Animation from Interactions (AAA):** la animación de movimiento disparada por interacción (parallax, transiciones grandes, zoom, auto-scroll) debe poder **desactivarse**, salvo que sea esencial. El mecanismo estándar: respetar **`prefers-reduced-motion`** del SO/navegador.

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

- Alternativa a la animación: **cross-fade suave** (opacidad) en vez de movimiento/desplazamiento grande; el fade rara vez marea. Reemplazar "slide/zoom" por "fade" cuando reduce-motion está activo, no eliminar todo feedback.
- **SC 2.3.1 Three Flashes (A):** nada debe parpadear **más de 3 veces por segundo** (o mantenerse bajo el umbral de flash general y de rojo). Aplica a loaders, transiciones, video, notificaciones. Regla simple: cero destellos rápidos de área grande.
- **Autoplay:** carruseles y video que se mueven solos deben poder pausarse/parar/ocultar (SC 2.2.2 Pause, Stop, Hide, A).
- iOS/macOS/Android exponen "Reduce Motion" a nivel sistema; en nativo, leer esa preferencia y bajar transiciones. (En juegos, esto es el toggle de screen-shake/flashes → [ver: gamedev/game-feel] · [ver: gamedev/ux-ui-onboarding].)

---

## 9. Objetivos táctiles y tiempo

### Touch / pointer targets

| Estándar | Tamaño mínimo | Espaciado | Fuente |
|---|---|---|---|
| **WCAG 2.5.8 (AA, nuevo 2.2)** | **24 × 24 CSS px** | O que un círculo de 24 px centrado en cada target no se solape con el vecino | w3.org (verificado) |
| **WCAG 2.5.5 (AAA)** | **44 × 44 CSS px** | — | w3.org (verificado) |
| **Apple HIG** | **44 × 44 pt** | — | Apple Design Tips (verbatim: *"at least 44 points x 44 points so they can be accurately tapped with a finger"*) |
| **Material / Google** | **48 × 48 dp** (≈ 9 mm ≈ tamaño de la yema del dedo) | **8 px** entre targets | web.dev (Google, verificado) |

- **24 px es el piso legal (AA); 44 pt / 48 dp es lo que de verdad se toca cómodo.** Diseñar a 44/48 y dejar 24 como mínimo absoluto para casos apretados (celdas de tabla densa).
- El **área táctil puede ser mayor que el visual**: un icono de 24 px puede tener un hit area de 44-48 con padding invisible. Preferir eso a agrandar el glifo.
- Excepciones de 2.5.8 (verificadas): *spacing* (círculo de 24 px sin solape), *equivalent* (misma acción disponible en otro control que sí cumple), *inline* (link dentro de una frase), *user agent control*, *essential*.
- Nada crítico en las esquinas superiores ni pegado a bordes en móvil (thumb zone) → [ver: mobile-ux] tiene el detalle de thumb zone, safe areas y densidad.

### Tiempo (SC 2.2.1 Timing Adjustable, A)

- **No imponer límites de tiempo cortos.** Si hay timeout (sesión, carrito, código), permitir **extender/desactivar/ajustar** (al menos ×10), salvo que el límite sea esencial (subasta en vivo).
- **Sesiones:** avisar antes de expirar y ofrecer continuar sin perder datos ingresados (se enlaza con SC 3.3.7 Redundant Entry).
- No exigir **gestos de precisión ni multitáctil** obligatorio (doble-pinch, trazos exactos): dar alternativa de tap simple (se cruza con 2.5.7 Dragging).

---

## 10. Auditoría: herramientas y método para un dev solo

**Ninguna herramienta automática es suficiente.** Detectan solo una fracción de los problemas — cifra comúnmente citada **~30–50%** (Deque reclama hasta ~57% con axe); el resto (foco lógico, alt significativo, orden de lectura, sentido) **exige prueba manual**. Automatizar lo automatizable y hacer a mano el resto.

| Herramienta | Qué detecta | Uso |
|---|---|---|
| **axe DevTools** (Deque) | Motor estándar de la industria; contraste, roles, labels, ARIA mal puesto | Extensión de navegador; `axe-core` integrable en CI/tests |
| **Lighthouse** (Chrome DevTools) | Auditoría "Accessibility" (usa axe por debajo) + performance/SEO | Un click en DevTools; score orientativo, no exhaustivo |
| **WAVE** (WebAIM) | Errores, alertas, estructura de headings y contraste, visual sobre la página | Extensión; muy bueno para ver el esqueleto semántico |
| **Contrast checkers** | Ratios exactos | WebAIM Contrast Checker (web), TPGi Colour Contrast Analyser (escritorio, cuentagotas), Chrome color picker |
| **Lectores de pantalla** | La prueba real de la semántica | VoiceOver (Cmd+F5 macOS / iOS), NVDA (Windows, gratis), TalkBack (Android) |

### Checklist de auditoría manual (el mínimo que no automatiza nada)

1. **Solo teclado:** desconecta el mouse. ¿Llegas a todo con Tab? ¿Se ve siempre el foco? ¿Puedes salir de modales? ¿El orden tiene sentido?
2. **Lector de pantalla** por la vista principal: ¿los botones se anuncian con su función? ¿los inputs con su label? ¿los headings dan un esquema? ¿las imágenes tienen alt útil?
3. **Zoom 200% / 400%:** ¿se rompe el layout? ¿scroll en dos direcciones?
4. **Escala de grises:** ¿distingues estados y errores sin color?
5. **Reduce-motion ON:** ¿desaparecen las animaciones grandes?
6. **Contraste** de texto y de bordes/iconos contra su fondo real (incluye dark mode).

- En apps móviles nativas: **Accessibility Inspector** (Xcode) y **Accessibility Scanner** (Android) hacen el equivalente a axe/WAVE.
- Integrar `axe-core` o `jest-axe`/Playwright-axe en el pipeline atrapa regresiones de contraste/labels antes del deploy. [ver: herramientas-handoff]
- Testear con usuarios reales de tecnología asistiva > cualquier checklist; los checkers no miden si algo *tiene sentido*, solo si técnicamente cumple.

---

## Reglas prácticas

1. **AA es la meta**, no A; adopta los AAA baratos (contraste 7:1, foco fuerte, `prefers-reduced-motion`) como bonus.
2. Texto normal **≥ 4.5:1**, texto grande (≥ 18 pt / 14 pt bold) **≥ 3:1**, bordes/iconos/estados de UI **≥ 3:1** (1.4.3 y 1.4.11). No redondear.
3. Contraste con **lightness**, no con opacidad ni saturación; recalcularlo por tema (light/dark).
4. **Ninguna info solo por color**: siempre color + icono/texto/forma/patrón (1.4.1). Verifícalo en escala de grises.
5. **HTML nativo antes que ARIA**: `<button>`/`<a>`/`<input>` reales; primera regla de ARIA — si existe el elemento nativo, úsalo.
6. Un solo **`<h1>`** por vista y **headings sin saltar niveles**; landmarks (`main/nav/header/footer`) siempre.
7. Todo input con **`<label>`** asociado; el placeholder no es label. Errores anunciados y ligados al campo.
8. `alt` describe **función** en iconos-acción, contenido en imágenes informativas, y **`alt=""`** en decorativas — nunca omitir el atributo.
9. **Todo lo operable con mouse, operable con teclado**; foco visible siempre (jamás `outline:none` a secas); sin trampas; skip link primero.
10. Nunca `tabindex` > 0. `tabindex="0"` solo para widgets custom; `-1` para foco programático.
11. **Targets: diseña a 44 pt / 48 dp**, mínimo legal 24×24 CSS px (AA); el hit area puede ser mayor que el glifo; ≥ 8 px entre targets.
12. Toda acción de **arrastre** tiene alternativa de tap simple (2.5.7); nada de gestos de precisión obligatorios.
13. Texto escalable a **200%** y **reflow a 320 px** sin scroll en dos ejes; unidades relativas (`rem`/Dynamic Type); **nunca** `user-scalable=no`.
14. Respeta **`prefers-reduced-motion`** (fade en vez de slide/zoom); **nada parpadea > 3 veces/segundo**; autoplay pausable.
15. Sin **timeouts cortos** sin opción de extender/desactivar; avisar antes de expirar sesión sin perder datos.
16. DOM = orden de lectura; no dejes que flex/grid `order` desincronice lo visual de lo semántico.
17. Login **sin pruebas cognitivas** (recordar/transcribir): permitir pegar contraseña, gestor de contraseñas, passkeys (3.3.8).
18. Audita con **axe/Lighthouse/WAVE** + **contrast checker**, pero valida a mano: **teclado solo + lector de pantalla + zoom + grises**.
19. Integra `axe-core` en CI para atrapar regresiones; lo automático es ~30–50%, el resto es manual.
20. La a11y se diseña desde el principio (color, jerarquía, semántica), no se "parcha" al final — reparar tarde cuesta mucho más.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Texto gris claro "elegante" a 3:1 sobre blanco | ≥ 4.5:1 para texto normal (1.4.3); baja lightness, no subas opacidad |
| Placeholder como único label del input | `<label>` real asociado; placeholder es ayuda, no etiqueta |
| Error solo con borde rojo | Borde + icono + texto de error ligado al campo (1.4.1 + 3.3.1) |
| `<div onclick>` como botón | `<button>` nativo: enfocable, anunciado y operable con teclado |
| ARIA por todos lados "para ser accesible" | Primera regla de ARIA: HTML nativo primero; ARIA malo > sin ARIA |
| `outline: none` para que "se vea limpio" | Reemplázalo por un foco visible con ≥ 3:1; nunca lo quites a secas |
| Bordes de input/iconos por debajo de 3:1 | 1.4.11 aplica a componentes de UI, no solo al texto |
| `alt` omitido → el lector lee `IMG_2287.png` | Alt descriptivo; `alt=""` explícito en decorativas |
| Info crítica solo por color (rojo/verde) | Segunda señal siempre; probar en escala de grises |
| `user-scalable=no` / `maximum-scale=1` en viewport | Quitarlo; permitir pinch-zoom y respetar font scale del sistema |
| Layout que se rompe (scroll en 2 ejes) al zoom 200% | Unidades relativas + contenedores fluidos; probar reflow a 320 px |
| Parallax/animaciones grandes sin escape | `@media (prefers-reduced-motion: reduce)`; fade como fallback |
| Modal sin foco atrapado ni retorno | Al abrir → foco al modal; atrapar dentro; al cerrar → devolver al disparador |
| Targets de 20 px pegados entre sí | 44 pt/48 dp de área + 8 px de separación (hit area > glifo) |
| Timeout de sesión que borra el formulario | Aviso previo + extender/desactivar (2.2.1) + no re-pedir datos (3.3.7) |
| "Pasa Lighthouse 100 → es accesible" | El score es orientativo; validar teclado + lector de pantalla a mano |
| A11y como tarea final "si da tiempo" | Diseñar accesible desde color/jerarquía/semántica; parchar tarde cuesta 10× |

## Fuentes

- **WCAG 2.2 — Understanding docs, W3C/WAI (w3.org/WAI/WCAG22/Understanding/)** — fuente normativa primaria; de aquí salen verificados verbatim: 1.4.1 Use of Color (A), 1.4.3 Contrast Minimum (4.5:1 / 3:1; def. texto grande 18pt≈24px / 14pt bold≈18.5px; exenciones logo/decorativo/inactivo; sin redondeo), 1.4.10 Reflow (320/256 px, 400%), 1.4.11 Non-text Contrast (3:1), 1.4.12 Text Spacing (1.5/2/0.12/0.16), 2.3.1 Three Flashes (3/s), 2.3.3 Animation from Interactions, 2.4.13 Focus Appearance (2px, 3:1), 2.5.5 Target Size Enhanced (44px), 2.5.8 Target Size Minimum (24px + 5 exenciones).
- **"What's New in WCAG 2.2" — W3C/WAI** — los 9 criterios nuevos con su nivel y la eliminación de 4.1.1 Parsing.
- **"Introduction to Understanding WCAG / Accessibility Principles" — W3C/WAI** — los 4 principios POUR, los tipos de discapacidad cubiertos y el argumento de beneficio universal (curb-cut).
- **Apple Human Interface Guidelines — Design Tips (developer.apple.com/design/tips)** — mínimo de hit target verificado verbatim: 44 × 44 points.
- **"Accessible tap targets" — web.dev (Google)** — 48 device-independent px (≈ 9 mm, tamaño de la yema) y ~8 px de separación entre targets; base de la guía de Material.
- **WebAIM — "Designing for Screen Reader Compatibility"** — cómo linealiza el lector; headings como esquema, landmarks, HTML semántico, alt, labels de formulario, orden de lectura, skip links.
- **WebAIM — "Keyboard Accessibility"** — orden de tab, foco visible (evitar `outline:0`), skip links, sin trampas de teclado, uso correcto de `tabindex` (0 / -1, nunca > 0), elementos nativamente enfocables.
- **WebAIM Million (informe anual)** — ~96% de home pages con fallos WCAG detectables automáticamente; magnitud del problema.
- **Nielsen Norman Group — accesibilidad vs. usabilidad vs. diseño inclusivo** — la a11y como parte de la usabilidad y por qué mejora la experiencia de todos (referencia de encuadre, no de números).
- **Deque / axe-core** — motor de auditoría estándar; base de la cifra de cobertura automática (~30–57%, varía por fuente) que justifica la prueba manual.
