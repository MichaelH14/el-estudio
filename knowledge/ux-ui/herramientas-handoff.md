# Herramientas, prototipado y handoff

> **Cuando cargar este archivo:** al pasar de idea a pantalla — hacer wireframes, montar el archivo de Figma (auto-layout, componentes, variables), construir un prototipo clicable para testear, preparar la entrega a desarrollo (specs/tokens/assets/dev mode), definir breakpoints responsive, correr un design review antes de shippear, o decidir cómo validar un cambio de UI con datos. Manual del *proceso* y las *herramientas*, no de los principios visuales (esos viven en [ver: fundamentos-visuales]) ni del sistema (en [ver: sistemas-diseno]).

Este archivo cubre el **flujo de trabajo** UX/UI para apps y productos (web y móvil). Lo específico de juegos — HUD, tutoriales in-game, FTUE — vive en [ver: gamedev/ux-ui-onboarding]; el pulido en tiempo real (juice) en [ver: gamedev/game-feel]; la implementación de UI de juego en [ver: unity/ui-unity] y [ver: pipeline/ui-flujo-completo]. Aquí el ángulo es producto/app.

---

## 1. El proceso: escalera de fidelidad

La regla madre: **no pintar antes de validar la estructura, no prototipar antes de validar el layout, no entregar antes de resolver los estados.** Cada peldaño arriba cuesta más de rehacer, así que se resuelven los problemas baratos primero (estructura, flujo) y los caros después (visual, código).

| Peldaño | Fidelidad | Qué se valida | Con qué | No hacer |
|---|---|---|---|---|
| **Sketch** | Muy baja (papel/pizarra) | ¿La idea de layout tiene sentido? Cantidad de pantallas | Papel, whiteboard, Excalidraw | Perder tiempo alineando pixeles |
| **Wireframe** | Baja (gris) | Estructura, jerarquía de contenido, flujo entre pantallas | Figma en gris, Balsamiq | Elegir colores/tipografía |
| **Mockup** | Alta (visual) | Look final: color, tipografía, imágenes, marca | Figma con design system | Empezar sin tokens/estilos |
| **Prototipo** | Interactivo | Flujo real, ¿el usuario entiende y completa la tarea? | Figma prototyping, links clicables | Prototipar todo si solo pruebas un flujo |
| **Handoff** | Spec + assets | Que dev pueda implementar sin adivinar | Figma Dev Mode, tokens, assets | Entregar sin estados ni responsive |

- **Las tres dimensiones de la fidelidad** no suben juntas (NN/g): *interactividad* (¿los clics funcionan solos o los simula una persona?), *visuales* (jerarquía y estilo real vs boceto), *contenido* (texto real vs placeholder). Un prototipo puede ser visualmente alto pero de interactividad baja, y viceversa — se sube solo la dimensión que la pregunta de esta iteración necesita.
- Regla de decisión: **subí la fidelidad de la dimensión que estás probando, mantené baja las demás.** Probar copy → contenido real, visuales grises. Probar visual → mockup pulido, un solo flujo clicable.

---

## 2. Wireframing: rápido y en gris

Objetivo: **resolver estructura y flujo antes de que el color y la tipografía secuestren la conversación.** Un wireframe bonito hace que stakeholders discutan el azul del botón en vez de si el paso 3 sobra.

| Principio | Por qué |
|---|---|
| **Todo en escala de grises** | El color es la señal más fuerte; si lo quitás, la jerarquía tiene que salir del tamaño, peso y espacio — lo que de verdad estás validando |
| **Cajas y líneas, no arte** | La baja fidelidad *comunica que está inacabado* → la gente critica la estructura, no el pixel (NN/g). El realismo prematuro apaga el feedback honesto |
| **Contenido representativo, no lorem** | Usar rangos reales: el nombre más largo, el precio de 7 dígitos, la lista vacía. El lorem esconde los reventones de layout |
| **Un flujo por tablero** | Wireframe = mapa de decisión, no galería. Enlazar pantallas con flechas para ver el recorrido completo |

- Herramientas: **Figma** (frames en gris + auto-layout ya desde el wireframe ahorra rehacer), **Balsamiq** (estética deliberadamente "boceto"), **Excalidraw**/papel para sketch. La herramienta importa menos que la disciplina de no pintar.
- Salida esperada: cada pantalla con su jerarquía de contenido resuelta (qué es primario/secundario/terciario) y el flujo entre pantallas. Recién ahí se pinta. Fundamentos de jerarquía y whitespace: [ver: fundamentos-visuales].

---

## 3. Figma: el estándar de facto (2026)

Figma es la herramienta dominante de diseño de producto. No hay que dominarla toda; hay que dominar **el flujo que hace el diseño mantenible y entregable**. Cinco piezas:

### 3.1 Frames
- El frame es el contenedor con reglas (recorta, aplica layout, define tamaño de dispositivo). Un mockup de pantalla = un frame del tamaño del viewport target (p. ej. 390×844 para iPhone estándar, o un ancho de breakpoint web).
- Frames anidados = la jerarquía del árbol que después será el DOM / view hierarchy. Nombrarlos como se nombrarán en código ayuda al handoff.

### 3.2 Auto-layout (lo más importante)
- Auto-layout hace que un frame se comporte como **flexbox**: dirección (fila/columna), gap entre hijos, padding, alineación, y cómo cada hijo *hug* (se ajusta al contenido) o *fill* (llena el contenedor).
- Por qué es no-negociable: sin auto-layout, cambiar un texto rompe todo el layout a mano; con auto-layout, el diseño **reacciona al contenido** igual que lo hará el código. Es el puente conceptual diseño↔CSS.
- Usar el mismo *espaciado de una escala* (no números al azar) en gaps y paddings — ver escala de spacing en 6.2.

### 3.3 Componentes y variants
- **Componente** = fuente de verdad reutilizable (un botón, un card). Se edita una vez, se propaga a todas las instancias.
- **Variants** = las variaciones de un mismo componente agrupadas por propiedades: `type` (primary/secondary/ghost), `state` (default/hover/focus/disabled/loading), `size` (sm/md/lg). Un botón bien hecho tiene *todos* sus estados como variants — eso obliga a diseñar los estados (sección 8) y le da a dev el catálogo completo.
- Espejo directo de los componentes de código. Nombrar variants como las props del componente real acelera el handoff (y Code Connect, 5.3).

### 3.4 Estilos y variables (design tokens)
- **Estilos**: colores, tipografías, sombras, blur reutilizables con nombre semántico (`text/primary`, `surface/raised`).
- **Variables**: el mecanismo moderno de **design tokens** en Figma — valores con nombre (`color.bg.default`, `space.4`, `radius.md`) que soportan **modes** (light/dark, densidad, marca) intercambiables. Cambiás el mode y todo el archivo re-tematiza.
- Regla: **cero valores hardcodeados** en un mockup serio. Todo color/espacio/radio sale de una variable. Eso es lo que hace que el design system sea sistema y no colección de pantallas. Profundidad de tokens y theming: [ver: sistemas-diseno].

### 3.5 Prototyping
- Conectar frames con interacciones (on tap/hover/drag → navigate/open overlay/back) para producir un **flujo clicable** navegable en el navegador o el móvil.
- Smart animate interpola entre dos frames con capas del mismo nombre → transiciones sin animar a mano (útil para comunicar motion al dev; specs de duración/easing en [ver: interaccion-microux]).
- Alcance: prototipar **solo el camino que vas a testear**. Un prototipo de "checkout" no necesita que funcione el menú de ajustes.

---

## 4. Prototipado: fidelidad según el objetivo

La pregunta no es "¿alta o baja fidelidad?" sino **"¿qué estoy tratando de aprender?"** — y eso decide qué dimensión subir (NN/g).

| Objetivo de la iteración | Fidelidad que necesitás | Fidelidad que dejás baja |
|---|---|---|
| ¿El flujo tiene sentido? ¿Falta/sobra un paso? | Interactividad (clicable, aunque sea gris) | Visual, contenido |
| ¿El usuario entiende el copy/los labels? | Contenido real | Visual, interactividad |
| ¿La pantalla se ve confiable/pulida? (salud, fintech) | Visual (mockup) | Interactividad |
| ¿Los usuarios completan la tarea sin ayuda? | Interactividad + contenido real | Visual puede ser medio |

- **Ventajas lo-fi** (NN/g): más rápido de crear y modificar entre sesiones, quita presión al usuario ("está inacabado, critique libre"), evita que el diseñador se enamore de una solución a medias, y comunica a stakeholders que falta trabajo.
- **Ventajas hi-fi** (NN/g): el sistema responde realista y rápido en la prueba, permite testear componentes/workflow/gráficos concretos, el usuario se comporta como en producto real, y el diseñador **observa** en vez de operar el prototipo (menos error humano de facilitación). Coste: mucho más tiempo de preparación.
- **Prototipo clicable para testear** > describir con palabras. Se aprende más viendo a 1 persona intentar la tarea que en una hora de debate interno. Cómo correr esa prueba: sección 9.

---

## 5. Handoff design-to-dev

El handoff falla cuando el dev tiene que **adivinar**. Un mockup no es un spec; el spec es todo lo que hace falta para implementar sin volver a preguntar.

### 5.1 Qué necesita quien implementa (checklist de entrega)

| Categoría | Qué debe estar explícito |
|---|---|
| **Medidas** | Espaciado (padding/gap/margin), dimensiones, alineación — todo desde la escala de spacing, no valores sueltos |
| **Color** | Referencia al **token** (`color.bg.default`), no solo el hex. El hex se copia; el token dice *por qué* |
| **Tipografía** | Familia, tamaño, peso, line-height, letter-spacing — idealmente un token de estilo de texto |
| **Forma** | Border-radius, borde, sombra/elevación (como token) |
| **Estados** | Los 8: default, hover, focus, active/pressed, disabled, loading, error, empty (sección 8). Sin esto, dev inventa |
| **Responsive** | Cómo se comporta cada bloque en cada breakpoint (sección 7): qué apila, qué se oculta, qué reflowa |
| **Motion** | Trigger, duración (ms), easing — no "que anime bonito" ([ver: interaccion-microux]) |
| **Edge cases** | Texto largo/vacío, lista vacía, error de red, i18n (el alemán expande ~30%), RTL |
| **Assets** | Exportados en las densidades correctas (5.2) |

### 5.2 Exportar assets
- **iOS**: @1x/@2x/@3x (PNG) para raster; SF Symbols o vectores para iconos.
- **Android**: mdpi/hdpi/xhdpi/xxhdpi/xxxhdpi, o vector drawable para iconos.
- **Web**: **SVG para iconos y logos** (escalan sin peso extra), PNG/WebP para fotos, `srcset` para densidades. Optimizar SVG (quitar metadata) antes de entregar.
- Regla: iconos = vector siempre que se pueda; fotos = raster con variantes de densidad.

### 5.3 Dev Mode de Figma (help.figma.com)
Interfaz para desarrolladores que reduce el "adivinar". Lo que aporta:

| Función | Uso |
|---|---|
| **Inspect** | Ver specs (medidas, colores, tipografía) y snippets de código en varios lenguajes, con valores copiables |
| **Code Connect** | Muestra el **código real del componente** del design system en vez del snippet auto-generado → dev usa el componente que ya existe |
| **Assets** | Descarga automática de iconos/imágenes/videos detectados en el diseño |
| **Compare changes** | Diff contra versiones previas + cuándo se editó cada frame |
| **Ready for dev** | Marcar frames/componentes/secciones como listos; notifica a dev, evita implementar borradores |
| **Annotations & measurements** | Marcar detalles críticos que el inspect no captura solo |
| **VS Code extension** | Inspeccionar el diseño sin salir del editor |

- Nota práctica: Dev Mode requiere asiento Dev o Full en plan de pago (dato de Figma; puede cambiar — **verificar plan vigente**).
- El handoff ideal no es "te paso el link" sino: **archivo con auto-layout limpio + variables/tokens + todos los estados como variants + Ready for dev + notas de responsive y edge cases.** Ahí el dev implementa y no vuelve.

---

## 6. Responsive en el diseño (antes de codear)

Definir cómo se adapta cada pantalla **en el diseño**, no descubrirlo en el navegador. Mobile-first: diseñar el layout angosto primero (obliga a priorizar) y expandir. Detalles de móvil (thumb zone, targets) en [ver: mobile-ux].

### 6.1 Breakpoints
Los **window size classes de Material 3** son la referencia con números concretos (developer.android.com):

| Clase | Ancho (dp) | Representa |
|---|---|---|
| **Compact** | < 600 | ~teléfonos en vertical |
| **Medium** | 600 – 839 | tablets en vertical, plegables abiertos |
| **Expanded** | 840 – 1199 | tablets en horizontal |
| **Large** | 1200 – 1599 | tablets grandes |
| **Extra-large** | ≥ 1600 | desktop |

- En **web**, no hay una norma única; los frameworks fijan convenciones. Tailwind (de facto): `sm 640 / md 768 / lg 1024 / xl 1280 / 2xl 1536` px — **convención de framework, no estándar W3C**. Regla real: poné breakpoints donde *el contenido se rompe*, no en anchos de dispositivos concretos (los dispositivos cambian; el contenido manda).
- Definir por breakpoint: qué columnas apilan, qué se oculta/colapsa (menú → hamburguesa), qué reflowa, cómo cambian márgenes y tamaño de tipografía.

### 6.2 Escala de spacing (base del layout consistente)
- Usar una **escala**, no números arbitrarios. Base común **8pt** (alinea con los 8dp de Material), con 4pt para ajustes finos: `4, 8, 12, 16, 24, 32, 48, 64, 96, 128`.
- Refactoring UI: **empezá con demasiado whitespace y quitá**, no al revés — es más fácil apretar que airear un diseño apretado. La escala no lineal (saltos crecientes) evita tamaños casi-iguales indistinguibles.
- El mismo número en Figma (gap de auto-layout) y en CSS (gap/padding) = handoff sin traducción.

---

## 7. Design review y crítica (antes de shippear)

Evaluar un diseño con criterios, no con "me gusta". Correr esta pasada **antes** de marcar Ready for dev. (En El Estudio existe `/design-review` y `/polish` para esto.)

### 7.1 Los seis ejes de una crítica

| Eje | Preguntas | Referencia |
|---|---|---|
| **Jerarquía** | ¿Qué mira el ojo primero? ¿Lo primario domina por tamaño/peso/espacio/color? ¿Hay 1 sola acción primaria por pantalla? | [ver: fundamentos-visuales] |
| **Consistencia** | ¿Espaciados de la escala? ¿Colores/tipos del token? ¿Este botón se ve/comporta como los demás? (Jakob's Law: la gente espera que funcione como lo que ya conoce) | [ver: sistemas-diseno] |
| **Estados** | ¿Están los 8 estados? ¿Qué ve el usuario mientras carga, si falla, si no hay datos? | 8 |
| **Accesibilidad** | Contraste, target size, focus visible, navegable por teclado, no depender solo del color | 8 + [ver: accesibilidad] |
| **Contenido** | ¿Texto real, incluidos los casos extremos (largo/vacío/error)? ¿Copy claro, sin jerga? | [ver: fundamentos-ux] |
| **Responsive** | ¿Cómo se ve en compact/expanded? ¿Thumb zone en móvil? | 6, [ver: mobile-ux] |

### 7.2 Cómo dar/recibir crítica
- Criticar **contra el objetivo del diseño**, no contra el gusto: "el objetivo es que completen el pago rápido; este paso extra lo frena" > "no me gusta".
- Separar problema de solución: reportar el problema observado; dejar que el diseñador resuelva. "Aquí no sé cuál es la acción principal" > "hacé el botón azul".
- El **Aesthetic-Usability Effect** (Laws of UX): un diseño bonito se *percibe* más usable y puede **esconder problemas reales de usabilidad** en las pruebas. Un mockup pulido no es evidencia de que funciona — por eso se testea el flujo, no la belleza.

---

## 8. Los estados de una pantalla (obligatorios)

Un diseño no está terminado con el estado "todo perfecto y lleno de datos". Diseñar **explícitamente**:

| Estado | Qué diseñar |
|---|---|
| **Default / ideal** | El caso feliz con datos reales |
| **Empty** | Lista/pantalla sin datos: nunca un "—" gigante; texto que orienta + acción para llenarla ([ver: patrones-ui]) |
| **Loading** | Skeleton/spinner; percepción de velocidad importa (Doherty Threshold: bajo ~400ms de respuesta la productividad se dispara — Laws of UX) |
| **Error** | Qué salió mal en lenguaje humano + cómo recuperarse. Nunca solo color rojo (no todos lo perciben) |
| **Partial** | Pocos datos, texto larguísimo, imagen faltante |
| **Hover / Focus / Active / Disabled** | Los estados de cada control interactivo (van como variants en Figma) |

Los estados de interacción (hover/focus/pressed) son también la materia de las microinteracciones: [ver: interaccion-microux].

---

## 9. Iterar con datos: validar un cambio de UI

Un cambio de UI no se valida con opiniones internas. Dos métodos, distintas preguntas:

### 9.1 Usability testing (el *por qué*)
- **5 usuarios encuentran ~85% de los problemas de usabilidad** (NN/g, Nielsen–Landauer). Fórmula: `N(1-(1-L)^n)`, con `L ≈ 31%` de problemas hallados por usuario. Un usuario solo ya revela ~1/3.
- Mejor **3 rondas de 5** que 1 ronda de 15: arreglás entre rondas, y cada rediseño destapa problemas nuevos. Rendimiento decreciente después de 5.
- Con varios grupos de usuarios muy distintos: 3–4 por grupo.
- Cualitativo → explica *por qué* la gente falla. Es lo que hacés con un prototipo clicable (sección 4).

### 9.2 A/B testing (el *cuánto*)
- Método cuantitativo: dos+ variantes con audiencia real en vivo, se mide cuál convierte mejor (NN/g).
- Requisitos: **miles de usuarios** para significancia, umbral estándar **95% (p=0.05)**, correr **1–2 semanas** (absorbe variación por día de semana), y **cambiar una sola variable** para poder aislar la causa.
- Bueno para: productos de alto tráfico, mejoras incrementales, métricas (conversión, CTR, revenue/usuario).
- Límite: dice *qué* cambió en el comportamiento, **no por qué**. Por eso se **triangula**: A/B para el cuánto + usability testing para el porqué. Un A/B sin la parte cualitativa te dice que B ganó pero no qué aprender para la próxima.
- Regla honesta: la mayoría de productos chicos **no tienen tráfico** para un A/B con significancia — ahí manda el usability testing con 5, no fabricar un "A/B" con 40 sesiones (no significa nada).

---

## 10. IA en el flujo de diseño (2026)

La IA acelera partes del flujo, no lo reemplaza. Dónde ayuda de verdad y dónde miente:

| Fase | IA ayuda | Límite / a vigilar |
|---|---|---|
| **Ideación / wireframe** | Generar variaciones de layout rápido, romper la página en blanco | Salidas genéricas; el criterio de cuál sirve es humano |
| **Contenido de relleno** | Copy realista (no lorem), datos de ejemplo plausibles | Revisar tono/marca; puede inventar |
| **Primer borrador de UI** | Del prompt/screenshot a un mockup base | Suele ignorar el design system real, accesibilidad y edge cases |
| **Diseño → código** | El **MCP server de Figma** deja que herramientas de IA (Claude Code, Cursor, VS Code) lean variables, componentes y layout de un frame y generen código usando el design system como referencia (help.figma.com) | La escritura al canvas por agente está **en beta**; el código generado necesita revisión (estados, responsive, a11y no salen gratis) |

- **Lo que la IA NO resuelve sola** (y hay que aportar humano): jerarquía intencional contra un objetivo, accesibilidad real (contraste/targets/foco), consistencia con el sistema existente, los 8 estados, y los edge cases. La IA produce el caso feliz; el trabajo de producto son los otros siete.
- Uso sensato 2026: IA para **arrancar y acelerar** (borrador, variaciones, boilerplate de código desde Figma), humano para **decidir, pulir y validar**. Un mockup generado sigue necesitando el design review de la sección 7 antes de shippear.
- (El estado exacto de features de IA de Figma cambia rápido — **verificar la versión vigente**; lo estable es el patrón: generar barato, validar caro.)

---

## Reglas prácticas

1. No pintes antes de validar estructura: wireframe en **gris** primero, siempre.
2. Subí la fidelidad **solo de la dimensión que estás probando** (interactividad / visual / contenido); mantené las otras bajas.
3. En Figma: **auto-layout desde el wireframe**. Nada de posiciones absolutas a mano.
4. **Cero valores hardcodeados** en un mockup serio: color, espacio, radio y tipografía salen de variables/estilos (tokens).
5. Diseñá **todos los estados de cada control como variants**: default, hover, focus, active, disabled, loading, error, empty.
6. Espaciado desde una **escala** (base 8pt: 4/8/12/16/24/32/48/64/96/128), nunca números al azar. Empezá con demasiado whitespace y quitá.
7. Contraste texto normal **≥ 4.5:1**, texto grande **≥ 3:1** (WCAG 2.2 SC 1.4.3, AA); componentes de UI/objetos gráficos **≥ 3:1** (SC 1.4.11, un criterio *distinto* — no es el mismo número reciclado).
8. Touch target: piso WCAG **24×24 CSS px** (AA), pero seguí la plataforma — **44×44 pt** (Apple) / **48×48 dp + 8dp de separación** (Material/Android). Diseñá a la plataforma, no al piso.
9. Definí el comportamiento **responsive por breakpoint** en el diseño (Material: compact <600 / medium 600–839 / expanded 840–1199 dp). Poné breakpoints donde el contenido se rompe.
10. Prototipá **solo el flujo que vas a testear**, con contenido real en los campos que importan.
11. Testeá con **5 usuarios** por ronda y hacé **varias rondas** arreglando entre medio, antes de gastar en A/B.
12. A/B testing solo con tráfico real (miles), 95% de confianza, 1–2 semanas, **una variable**; si no hay tráfico, usá usability testing.
13. Handoff = archivo con auto-layout + tokens + estados + **Ready for dev** + notas de responsive y edge cases. No "te paso el link".
14. Exportá iconos como **SVG/vector**; fotos raster con variantes de densidad (@2x/@3x, xxhdpi…).
15. Corré el **design review de 6 ejes** (jerarquía, consistencia, estados, accesibilidad, contenido, responsive) antes de marcar listo.
16. Contenido de los casos extremos **en el diseño**: nombre más largo, lista vacía, error, i18n (alemán ~+30%), RTL.
17. IA para arrancar/acelerar (borrador, variaciones, código desde Figma); humano decide, pulE y valida. El mockup generado igual pasa por review.

---

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Pintar (color/tipo) antes de resolver estructura | Wireframe en gris; el color entra recién en el mockup |
| Mockup a color pero interactividad cero, presentado como "prototipo" | Nombrar la fidelidad honestamente; para testear flujo hacé el clicable aunque sea gris |
| Enamorarse de un hi-fi pulido y no querer cambiarlo | Trabajar lo-fi mientras la solución esté en duda (NN/g); el realismo apaga la crítica |
| Lorem ipsum y datos perfectos que esconden reventones | Contenido representativo desde el wireframe: el más largo, el vacío, el error |
| Diseñar solo el "estado feliz" | Los 8 estados son parte del diseño, no un extra; van como variants |
| Valores sueltos (padding 13px, otro 15px) | Escala de spacing; en Figma, gaps/padding de auto-layout desde la escala |
| Handoff = "te mando el link de Figma" | Ready for dev + tokens + estados + notas de responsive/edge cases + assets exportados |
| Pasar el hex y ya | Pasar el **token** (`color.bg.default`); el hex no dice el porqué ni sobrevive al theming |
| Breakpoints copiados de anchos de dispositivos de moda | Breakpoints donde el contenido se rompe; usar window size classes como guía, no dogma |
| Confiar en que "se ve bien" = funciona (Aesthetic-Usability Effect) | Testear la tarea con usuarios reales; la belleza esconde problemas de usabilidad |
| Montar un "A/B" con 40 sesiones | Sin miles de usuarios no hay significancia; con poco tráfico, usability testing con 5 |
| Target de 24px porque "WCAG lo permite" en una app móvil | 24px es el piso; en móvil seguí 44pt/48dp — el pulgar no es un cursor |
| Aceptar el código que la IA generó del Figma tal cual | Revisar estados, responsive y accesibilidad — la IA entrega el caso feliz |
| Iconos exportados como PNG | SVG/vector: escalan sin peso ni blur en cualquier densidad |

---

## Fuentes

- **WCAG 2.2 — SC 1.4.3 Contrast (Minimum)** — W3C/WAI (w3.org) — Aplica solo a **texto**: 4.5:1 normal, 3:1 texto grande (AA); AAA (SC 1.4.6) sube a 7:1 / 4.5:1. Texto grande = 18pt / 14pt bold.
- **WCAG 2.2 — SC 1.4.11 Non-text Contrast** — W3C/WAI (w3.org) — Criterio **distinto** al 1.4.3: 3:1 para componentes de UI (bordes de input, ícono de estado) y objetos gráficos necesarios para entender el contenido (AA). No confundir los dos números con la misma fuente — son dos SC separados.
- **WCAG 2.2 — SC 2.5.8 Target Size (Minimum)** — W3C/WAI (w3.org) — Piso de target: 24×24 CSS px (AA) con 5 excepciones; SC 2.5.5 Enhanced = 44×44 (AAA).
- **NN/g — "The Difference Between Prototype Fidelities"** — Nielsen Norman Group (nngroup.com) — Las 3 dimensiones de fidelidad (interactividad/visual/contenido) y cuándo lo-fi vs hi-fi.
- **NN/g — "Why You Only Need to Test with 5 Users"** — Nielsen Norman Group (nngroup.com) — 5 usuarios ≈ 85% de problemas; fórmula N(1-(1-L)^n), L≈31%; 3 rondas de 5.
- **NN/g — "A/B Testing 101"** — Nielsen Norman Group (nngroup.com) — Requisitos de un A/B (miles de usuarios, 95%, 1–2 semanas, 1 variable) y triangulación con cualitativo.
- **Apple Human Interface Guidelines — Layout / Accessibility** — Apple (developer.apple.com) — Hit target mínimo 44×44 pt, safe areas, márgenes 16pt.
- **Material Design accessibility / Android touch targets** — Google (support.google.com/accessibility, developer.android.com) — Touch target 48×48 dp + 8dp de separación (~9mm; rango 7–10mm).
- **Material 3 Window Size Classes** — Google (developer.android.com) — Breakpoints compact/medium/expanded/large/extra-large en dp.
- **Laws of UX** — Jon Yablonski (lawsofux.com) — Fitts, Hick, Jakob, Doherty (<400ms), Aesthetic-Usability, Miller (7±2) y demás heurísticas citadas.
- **Guide to Dev Mode + Dev Mode MCP Server** — Figma (help.figma.com) — Funciones de handoff (inspect, Code Connect, assets, Ready for dev) y el MCP que expone diseño a herramientas de IA (write-to-canvas en beta).
- **Refactoring UI** — Adam Wathan & Steve Schoger (refactoringui.com) — Escala de spacing no lineal, empezar con demasiado whitespace, jerarquía por de-énfasis.
- **Material Design 3** — Google (m3.material.io) — Sistema de referencia para tokens/variables, componentes y layout adaptativo.
