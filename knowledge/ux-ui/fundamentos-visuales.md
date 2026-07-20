# Fundamentos de diseño visual (UX/UI de apps y productos)

> **Cuando cargar este archivo:** al diseñar, maquetar o evaluar cualquier pantalla de una app o producto (web/móvil) — antes de elegir tipografía, paleta, espaciado, grid o jerarquía; cuando "algo se ve amateur" y hay que diagnosticar por qué; o al auditar contraste, legibilidad y foco visual. Es el "cómo se ve", complementa el "cómo funciona" de [ver: fundamentos-ux]. Para HUD/tutoriales/onboarding de **juegos** no repitas esto: [ver: gamedev/ux-ui-onboarding] y [ver: gamedev/game-feel]. Implementación de UI en motor: [ver: unity/ui-unity] y [ver: pipeline/ui-flujo-completo].

Este archivo cubre lo **visual**: jerarquía, tipografía, color, espaciado, grid, Gestalt, contraste/énfasis y consistencia. Los tokens y componentes reutilizables viven en [ver: sistemas-diseno]; los patrones de pantalla (formularios, listas, nav) en [ver: patrones-ui]; thumb zone y safe areas en [ver: mobile-ux]; el detalle completo de WCAG en [ver: accesibilidad]; motion y feedback en [ver: interaccion-microux].

---

## 1. Cómo lee el ojo una interfaz (jerarquía visual)

**Jerarquía visual** = organizar los elementos para que el ojo los consuma en el orden de importancia que tú decides, no al azar (NN/g). Si todo pesa lo mismo, el usuario no sabe dónde mirar y el diseño se lee como ruido.

### Patrones de escaneo reales (NN/g, eyetracking desde 2006)

| Patrón | Qué es | Implicación de diseño |
|---|---|---|
| **F-shaped** | Texto sin formato: barrido horizontal arriba, otro más corto abajo, y bajada vertical por la izquierda | Lo importante va en las primeras líneas y primeras palabras de cada línea; formatea (headings, bullets) para romperlo |
| **Layer-cake** | El ojo salta de heading a heading ignorando el cuerpo | Headings autoexplicativos que empiezan con la palabra clave |
| **Spotted** | Caza un elemento concreto (un precio, un botón, un enlace) | El elemento buscado debe destacar por color/forma |
| **Marking** | La vista fija mientras se hace scroll (más en móvil) | Contenido clave visible sin depender del punto exacto de scroll |
| **Commitment** | Lectura casi completa; solo con alta motivación | No asumas que ocurrirá: diséñalo para el escaneo |

El F-pattern es lo que pasa **cuando el diseño NO guía**: aparece con bloques de texto planos y baja motivación. Buen formato lo neutraliza. La conclusión de NN/g: el diseño debe **guiar la atención**, no rendirse al patrón por defecto.

### Las 5 herramientas para crear jerarquía

El ojo prioriza por diferencia relativa. Herramientas, de más a menos potentes en UI:

| Herramienta | Cómo se usa | Nota |
|---|---|---|
| **Tamaño (size)** | Más grande = más importante | Potente pero se abusa; NN/g: no más de 3 tamaños (small/medium/large), máx. 2 elementos "grandes" o dejan de destacar |
| **Peso (weight)** | Bold vs regular; a veces mejor que subir tamaño | Refactoring UI: da jerarquía con **peso y color antes que con tamaño** — el layout no crece |
| **Color/contraste** | Saturado y oscuro adelante; muted atrás | Nunca **solo** color (accesibilidad) [ver: accesibilidad] |
| **Espacio (whitespace)** | Aire alrededor = protagonismo; juntar = relación | Ver §4 |
| **Posición** | Arriba-izquierda y centro tienen prioridad natural de lectura (culturas LTR) | El CTA principal rara vez va escondido abajo-derecha |

### El squint test (prueba del entrecerrar / blur)

Entrecierra los ojos o aplica blur a la pantalla (NN/g lo llama *squint test*): si con la imagen borrosa **sigues sabiendo qué es lo primero que debes mirar**, la jerarquía funciona. Si todo se convierte en una masa gris uniforme, no hay jerarquía. Es la verificación más rápida y barata de una pantalla.

---

## 2. Tipografía

El 90 %+ de una UI es texto. La tipografía **es** la interfaz.

### Escala tipográfica (modular scale)

No inventes tamaños sueltos: define una escala y elige solo de ella. Se construye con un **ratio** aplicado a un tamaño base (típ. 16px en web):

| Ratio | Nombre | Uso típico |
|---|---|---|
| 1.125 | Major second | Densa, mucho texto (dashboards) |
| 1.200 | Minor third | UI equilibrada |
| 1.250 | Major third | Marketing / landing |
| 1.333 | Perfect fourth | Editorial, contraste alto |
| 1.500 / 1.618 | Perfect fifth / golden | Titulares muy dramáticos |

Ejemplo con base 16 y ratio 1.25: 16 → 20 → 25 → 31 → 39 → 49px. (Convención popularizada por type-scale.com y Tim Brown, *A List Apart*.) **Material Design 3** codifica una escala por roles semánticos en vez de por tamaño suelto:

| Rol M3 | Baseline (Large) | Uso |
|---|---|---|
| **Display** | 57 / 45 / 36 sp | Números y titulares grandes, expresivos |
| **Headline** | 32 / 28 / 24 sp | Encabezados de sección |
| **Title** | 22 / 16 / 14 sp | Títulos de tarjeta/dialog, medium-emphasis |
| **Body** | 16 / 14 / 12 sp | Texto corrido, párrafos largos |
| **Label** | 14 / 12 / 11 sp | Botones, chips, captions |

(Valores baseline de M3; los pesos y line-heights van atados a cada rol. sp = scale-independent pixels, respeta el ajuste de tamaño del usuario.)

### Line-height (interlineado)

- **Cuerpo: ~1.5** (150 %). WCAG SC 1.4.8 (AAA) exige que exista un mecanismo para interlineado **≥1.5 dentro del párrafo** y **espacio entre párrafos ≥1.5× el interlineado**.
- **Inversamente proporcional al tamaño**: texto pequeño necesita MÁS line-height; titulares grandes, menos (bajar a ~1.1–1.25). Un H1 con line-height 1.5 se ve desparramado.
- Inversamente proporcional a la **medida** también: líneas largas piden más interlineado para no perder el renglón.
- Técnica fina (Smashing): calcular el leading contra la x-height, no el font-size (`line-height: calc(1ex / 0.32)` como punto de partida en pantalla).

### Medida (line length / measure)

| Fuente | Rango óptimo |
|---|---|
| **Baymard Institute** | **50–75 caracteres** por línea para cuerpo |
| **WCAG SC 1.4.8 (AAA)** | **≤80 caracteres** (40 si es CJK) |
| Smashing (práctica) | 60–70 caracteres (`max-width: 60ch`) |

Líneas de 100+ caracteres cansan (se pierde el salto de renglón); demasiado cortas fragmentan la lectura. Regla operativa: **limita el ancho del bloque de texto con `max-width` en `ch`**, no dejes que el párrafo ocupe todo el viewport de un monitor ancho.

### Pesos, pareja de fuentes y legibilidad

- **Pesos para jerarquía**: 400 (regular) cuerpo, 500–600 (medium/semibold) para labels y énfasis, 700 (bold) para titulares. Evita weights <400 en texto pequeño (se rompe en pantallas de baja densidad).
- **Emparejar fuentes**: máximo 2 familias (una display/heading + una de cuerpo), o una sola superfamilia con varios pesos. Contraste por rol, no dos fuentes que "compiten". Si dudas, **una sola familia bien usada** gana a dos mal combinadas.
- **Legibilidad**: fuentes de UI probadas (Inter, SF Pro, Roboto, system-ui) antes que decorativas. Tamaño mínimo de cuerpo cómodo en móvil ~16px (evita el zoom automático de iOS en inputs <16px). Evita ALL CAPS en bloques largos (más lento de leer); úsalo solo en labels cortos con letter-spacing ligero.

### Jerarquía tipográfica sin tamaño

Refactoring UI: la jerarquía tipográfica no es solo tamaño. Un mismo tamaño puede diferenciarse por **peso + color**: título en gris-900 semibold, metadato en gris-500 regular. Da jerarquía primero con color/peso; sube el tamaño solo cuando peso y color ya no alcanzan.

---

## 3. Color aplicado a UI

### Anatomía de una paleta de producto

| Rol | Cuántos | Para qué |
|---|---|---|
| **Neutrales (greys)** | 8–10 shades de un solo gris (a veces con tinte de marca) | Texto, fondos, bordes, superficies. Es el 70–80 % de la UI |
| **Primario (brand)** | 1 color, 5–10 shades | CTA, enlaces, estados activos, foco |
| **Acento/secundario** | 0–2 colores | Categorías, datos, destacar sin ser el CTA |
| **Semánticos** | success/warning/error/info | Feedback de estado (§ abajo) |

Refactoring UI: **necesitas más colores de los que crees** — no un hex por rol, sino una rampa de shades por color. Construye en **HSL** (no hex): fija el hue, varía saturation/lightness para generar la rampa; esto da control real sobre "más claro/oscuro" sin adivinar.

### La regla 60-30-10 (heurística de proporción)

Convención heredada del diseño de interiores, aplicada a UI: **60 %** color/superficie dominante (normalmente neutro), **30 %** secundario, **10 %** acento (el CTA, lo que debe saltar). No es un estándar medible, es un reparto que evita el error de "todo es color de marca". Si el 60 % ya grita, el 10 % de acento no tiene dónde destacar.

### Contraste — números WCAG 2.2 (verificados contra w3.org)

| Criterio | Nivel | Requisito |
|---|---|---|
| **1.4.3 Contrast (Minimum)** | AA | Texto normal **≥ 4.5:1**; texto grande **≥ 3:1** |
| **1.4.6 Contrast (Enhanced)** | AAA | Texto normal **≥ 7:1**; texto grande **≥ 4.5:1** |
| **1.4.11 Non-text Contrast** | AA | Componentes de UI y objetos gráficos (bordes de input, iconos con significado, estados) **≥ 3:1** contra el color adyacente |

**"Texto grande"** = ≥18pt (**24px**) regular **o** ≥14pt bold (**≈18.5px**) — WCAG usa 1pt = 1.333px. Excepciones: texto decorativo, logotipos y componentes inactivos/deshabilitados no requieren cumplir.

Consecuencias prácticas:
- Gris claro sobre blanco "elegante" suele **fallar 4.5:1** — verifícalo, no lo estimes a ojo (NN/g: *low-contrast text* es un antipatrón real).
- El **borde de un input vacío** y el **icono** que comunica algo también deben cumplir 3:1 (1.4.11), no solo el texto.
- El foco de teclado (focus ring) es no-text: ≥3:1 contra el fondo. [ver: accesibilidad]

### Color como significado (semántico)

| Color | Significado convencional | Regla |
|---|---|---|
| Verde | success / confirmado / disponible | Nunca el ÚNICO indicador |
| Rojo | error / destructivo / detenido | Acompaña con icono + texto |
| Amarillo/ámbar | warning / atención / pendiente | — |
| Azul | info / neutral / enlace | — |

**Prohibido codificar información crítica solo por color** (WCAG 1.4.1 Use of Color; ~1 de cada 12 hombres tiene alguna deficiencia de color). Añade icono, forma, texto o patrón. El rojo-vs-verde (éxito/error) es justo el par que más falla en daltonismo. [ver: accesibilidad]

### Modo claro / oscuro

- **No inviertas** literalmente. En dark mode los blancos puros sobre negro puro vibran: usa fondo casi-negro (p. ej. gris-900 ~#121212, convención de M3) y texto casi-blanco, no #000/#FFF.
- **Baja la saturación** de los colores de marca en dark mode; los saturados vibran sobre oscuro.
- La **elevación** en dark mode se comunica con superficies más claras (no con sombras, que casi no se ven). Cada nivel de elevación = un gris un poco más claro.
- Define la paleta como **tokens semánticos** (`surface`, `on-surface`, `primary`) y mapea cada tema, en vez de hardcodear hex por pantalla. [ver: sistemas-diseno]

---

## 4. Espaciado y whitespace

El espaciado es la herramienta que más separa lo "pro" de lo "amateur", y la más ignorada.

### Sistema de espaciado (escala 4/8)

- Base **8px** (8-point grid): componentes y layout se alinean a múltiplos de 8; elementos finos (iconos, texto, ajustes pequeños) a **4px**. Material lo formaliza así (grid de 8dp, 4dp para lo fino).
- Escala **no lineal** típica (Refactoring UI / Tailwind): `4, 8, 12, 16, 24, 32, 48, 64, 96, 128…` px. Los saltos crecen porque la diferencia relativa importa: 4→8 se nota, 200→204 no.
- **Elige solo de la escala.** Un `margin: 13px` suelto es la firma del diseño improvisado. Todo padding/margin/gap sale del set.

### Whitespace = respiración y agrupación

- **"Empieza con demasiado whitespace y quita"** (Refactoring UI). El instinto de principiante es apretar; casi siempre falta aire, no sobra.
- **Proximidad crea grupos** (Gestalt, §6): más aire ENTRE grupos que DENTRO. El error clásico: un label pegado por igual a su campo y al campo de arriba — el ojo no sabe qué label va con qué input.
- Regla del label: la distancia label→su-input debe ser **menor** que input-anterior→label. La proximidad hace el trabajo que la gente intenta arreglar con líneas y cajas.
- **Whitespace = énfasis**: rodear un elemento de aire lo hace importante sin agrandarlo (NN/g). Las landing premium respiran; las baratas apiñan.
- **Macro** (entre secciones) vs **micro** (interlineado, padding de botón) whitespace: ambos importan; el macro da estructura, el micro da legibilidad.

---

## 5. Grid y layout

### Columnas, gutters, márgenes

- **Grid de columnas** para alinear todo a una rejilla común. Web desktop: 12 columnas es el estándar de facto (divisible por 2/3/4/6). 
- **Material layout grid** (responsive por breakpoint): teléfono **4 columnas**, tablet **8**, desktop **12**, con márgenes/gutters típicos de 16–24dp.
- **Gutter** = espacio entre columnas; **margin** = aire a los lados del contenedor. Ambos salen de la escala de espaciado (§4).
- No confundir grid de columnas (layout) con el grid de 8px (espaciado): coexisten.

### El poder de alinear

- **Alinea a la rejilla y a un eje.** El desorden percibido casi siempre es falta de alineación: bordes izquierdos que no coinciden, textos centrados junto a textos a la izquierda.
- **Elige un tipo de alineación y sé consistente**: cuerpo de texto a la izquierda (nunca justificado en UI — WCAG 1.4.8 lo prohíbe en AAA: crea "ríos" y espaciado irregular). Centrado solo para bloques cortos (títulos, empty states).
- **Alinea números por la derecha / decimal** en tablas y precios; alinea el texto por la izquierda. Mezclar rompe el escaneo vertical de una columna.
- **Optical alignment**: a veces el alineado matemático se ve mal (un icono circular, comillas colgantes) — corrige a ojo. La percepción manda sobre el píxel exacto.

---

## 6. Principios de Gestalt en UI

Cómo el cerebro agrupa lo que ve, antes de "leerlo" (NN/g cubre estos como base de la percepción visual). En UI son las reglas que hacen que un layout se entienda sin instrucciones.

| Principio | Qué dice | Aplicación en UI |
|---|---|---|
| **Proximidad** | Lo cercano se percibe como grupo | Agrupar campos relacionados; separar secciones con más aire (la herramienta #1) |
| **Similitud** | Lo que se ve igual se percibe relacionado | Todos los botones primarios iguales; todos los enlaces del mismo color |
| **Región común (common region)** | Lo dentro de un borde/fondo compartido se agrupa | Cards, secciones con fondo; más fuerte que la proximidad — un borde puede agrupar aunque haya distancia |
| **Cierre (closure)** | El ojo completa formas incompletas | Iconos minimalistas, un carrusel que "corta" un item para insinuar que hay más |
| **Continuidad** | El ojo sigue líneas/curvas suaves | Alinear en un eje guía la mirada; una fila alineada se lee como secuencia |
| **Figura/fondo** | Separamos objeto de fondo | Modales con overlay oscuro; elevación; una CTA "figura" sobre fondo neutro |
| **Conexión uniforme** | Lo conectado (línea, mismo contenedor) se relaciona más que lo solo cercano | Steppers, breadcrumbs unidos por líneas |

Regla operativa: **antes de dibujar una caja o una línea divisoria, prueba si la proximidad y la similitud ya agrupan.** La mayoría de bordes sobran (Refactoring UI: "usa menos bordes" — separa con espacio, fondo distinto o sombra).

---

## 7. Contraste y énfasis: crear foco

Jerarquía (§1) es el orden global; énfasis es hacer que **una** cosa gane. El error opuesto y frecuente: **todo grita** (todos los botones con color de marca, todo en bold, tres CTAs compitiendo) → nada destaca.

- **Un CTA primario por pantalla/vista.** Lo demás son acciones secundarias (botón outline/ghost) o terciarias (solo texto/enlace). La jerarquía de botones comunica qué es la acción "correcta".
- **Emphasize by de-emphasizing** (Refactoring UI): cuando no puedes hacer que lo importante resalte más, **apaga la competencia** — baja el peso/color de lo secundario en vez de subir el del protagonista.
- **Von Restorff / Isolation Effect** (Laws of UX): entre elementos similares, el que **difiere** se recuerda y se ve primero. Por eso el CTA rompe el patrón de color del resto.
- **Contraste ≠ solo color**: tamaño, peso, saturación, aire y posición. Un botón puede ganar por ser el único con relleno sólido aunque sea del mismo tamaño.
- No abuses del acento: si medio 10 % de la 60-30-10 se convierte en 40 %, el foco se diluye.

---

## 8. Consistencia visual = calidad percibida

La repetición se lee como intención y cuidado; la variación aleatoria se lee como descuido. **Aesthetic-Usability Effect** (Laws of UX): lo que se ve cuidado se **percibe** como más usable (y perdona más fallos menores).

Repite deliberadamente (candidatos a **design tokens** [ver: sistemas-diseno]):

| Propiedad | Regla de consistencia |
|---|---|
| **Border-radius** | 1–3 valores en toda la app (p. ej. 4/8/16), no un radio distinto por card |
| **Sombras / elevación** | Un set de 2–5 niveles con **una sola fuente de luz** (misma dirección/blur), no sombras inventadas por componente. Sombra = elevación; más difusa = más alto |
| **Espaciado** | Toda medida sale de la escala 4/8 (§4) |
| **Color** | Solo de la paleta de shades (§3) |
| **Tipografía** | Solo de la escala/roles (§2) |
| **Iconografía** | Un solo set, mismo grosor de línea y tamaño de grid |
| **Duración/easing de motion** | Tokens consistentes [ver: interaccion-microux] |

**Jakob's Law** (Laws of UX): los usuarios pasan la mayor parte del tiempo en OTRAS apps; esperan que la tuya funcione parecido. Consistencia **externa** (con las convenciones de la plataforma — iOS HIG, Android/Material) tanto como interna. No reinventes el toggle, el date-picker ni el gesto de volver.

---

## 9. Workflow accionable (método Refactoring UI)

Orden de trabajo que evita los errores más comunes:

1. **Empieza por una feature, no por el layout.** Diseña "el flujo de crear factura", no "el shell de la app en abstracto". El detalle define el contenedor.
2. **Diseña en escala de grises primero.** Sin color, la jerarquía tiene que resolverse con **tamaño, peso, contraste y espacio**. Si funciona en gris, el color solo lo mejora; si no, el color estaba tapando una jerarquía rota.
3. **Jerarquía con peso y color antes que con tamaño** (§2). Sube tamaño solo cuando peso+color no alcanzan.
4. **Empieza con demasiado whitespace** y ve quitando (§4).
5. **Define los sistemas antes de dibujar en detalle**: escala tipográfica, escala de espaciado, paleta de shades. Elegir de un set finito, nunca valores sueltos.
6. **Menos bordes**: separa con espacio, fondo o sombra antes de dibujar líneas (§6).
7. **No uses gris puro sobre fondos de color** (Refactoring UI): para "texto tenue" sobre un fondo coloreado, usa un color con el **mismo hue** que el fondo, más claro/saturado — no gris, que se ve sucio/apagado.
8. **Diseña los estados desde el principio**: empty state, loading, error, un item, muchos items, texto larguísimo. El happy-path bonito con datos perfectos miente. [ver: patrones-ui]
9. **Verifica con el squint test** (§1) y con contraste real medido (§3), no a ojo.
10. **Prueba en el dispositivo real y multi-viewport** — API 200 ≠ UI correcta.

---

## Reglas prácticas

1. Toda pantalla pasa el **squint test**: borrosa, aún se sabe qué mirar primero.
2. Máximo ~3 tamaños de texto por pantalla (NN/g); jerarquía con **peso+color antes que tamaño** (Refactoring UI).
3. Escala tipográfica con ratio fijo (1.2–1.33 típico); elige solo de ella, nunca px sueltos.
4. Cuerpo line-height ~1.5; **inversamente** proporcional al tamaño (titulares 1.1–1.25).
5. Medida de texto **50–75 caracteres** (Baymard), ≤80 (WCAG 1.4.8); limita con `max-width` en `ch`.
6. Cuerpo ≥16px en móvil (evita zoom de iOS en inputs); nunca justificar texto en UI.
7. Contraste texto **≥4.5:1** normal, **≥3:1** grande (WCAG 1.4.3 AA); no-texto (bordes, iconos con significado, foco) **≥3:1** (1.4.11). Mídelo, no lo estimes.
8. Nunca información crítica **solo por color** (1.4.1): añade icono/forma/texto.
9. Paleta = 8–10 grises + 1 primario en rampa + semánticos; construye en **HSL**, no hex suelto.
10. Reparto **60-30-10**; un solo CTA primario por vista; **emphasize by de-emphasizing**.
11. Espaciado en escala **4/8**; más aire ENTRE grupos que DENTRO (proximidad).
12. Empieza con demasiado whitespace y quita; el error casi siempre es apretar, no espaciar.
13. Alinea todo a la rejilla y a un eje; números por la derecha, texto por la izquierda.
14. Antes de dibujar un borde/línea, prueba si proximidad+similitud ya agrupan (usa menos bordes).
15. Radios, sombras (una sola fuente de luz), espaciados, colores y tipos: **repetidos**, vía design tokens [ver: sistemas-diseno].
16. Touch targets — móvil: **44pt iOS / 48dp Android**; web WCAG **≥24×24px** (AA), ideal 44×44 (AAA); NN/g ~1cm físico [ver: mobile-ux].
17. Dark mode: casi-negro/casi-blanco (no #000/#FFF), baja saturación de marca, elevación por superficie más clara.
18. Diseña en **gris primero**; si la jerarquía funciona sin color, está bien resuelta.
19. Diseña **todos los estados** (empty/loading/error/uno/muchos/texto largo), no solo el happy path.
20. Consistente con la **plataforma** (Jakob's Law): no reinventes controles nativos; verifica en dispositivo real multi-viewport.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Todo pesa lo mismo: el ojo no sabe dónde ir | Jerarquía deliberada (§1); squint test; máx. 3 tamaños, 1 protagonista |
| Todo grita (3 CTAs, todo bold, todo con color de marca) | Un CTA primario; secundarios en outline/ghost; emphasize by de-emphasizing |
| Tamaños/espaciados sueltos (13px, 27px…) | Escala tipográfica + escala 4/8; elegir solo del set |
| Texto gris claro "elegante" que falla contraste | Medir contra 4.5:1 (1.4.3); no estimar a ojo (NN/g: low-contrast es antipatrón) |
| Información solo por color (rojo=error, verde=ok) | Color + icono + texto (WCAG 1.4.1); rojo/verde es justo lo que falla en daltonismo |
| Todo apretado, sin aire | Empezar con demasiado whitespace y quitar; macro + micro spacing |
| Label a igual distancia de dos inputs | Proximidad: label→su-input < separación entre grupos |
| Cajas y líneas por todos lados | Menos bordes: separar con espacio, fondo o sombra (Gestalt) |
| Bordes izquierdos que no alinean; centrar y alinear-izquierda mezclados | Una rejilla, un eje; texto a la izquierda, números a la derecha |
| Texto justificado "para que se vea limpio" | Nunca justificar en UI (ríos, spacing irregular; WCAG 1.4.8 lo prohíbe) |
| Sombras y radios distintos por componente | Set de 2–5 sombras con una sola fuente de luz; 1–3 radios; tokens |
| Dark mode por inversión literal (#000/#FFF) | Casi-negro/casi-blanco, marca desaturada, elevación por superficie |
| Diseñar el happy path con datos perfectos | Diseñar empty/loading/error/overflow desde el inicio |
| Dos+ fuentes que compiten | Máx. 2 familias (o 1 superfamilia); contraste por rol, no por familia |
| Párrafo que ocupa todo un monitor ancho | `max-width` ~60–75ch; la medida importa más que el ancho disponible |
| Reinventar controles nativos (date-picker, toggle, back) | Jakob's Law: usar convenciones de plataforma; consistencia externa |
| "Se ve bien en mi pantalla" | Multi-viewport en dispositivo real; API 200 ≠ UI correcta |

## Fuentes

- **WCAG 2.2 — W3C/WAI (w3.org/WAI/WCAG22)** — norma primaria de accesibilidad. Verificado directo: **1.4.3 Contrast (Minimum)** 4.5:1 / 3:1 grande, "texto grande" = 18pt(24px) o 14pt bold(≈18.5px); **1.4.6 (Enhanced)** 7:1 / 4.5:1; **1.4.11 Non-text Contrast** 3:1; **1.4.8 Visual Presentation** ≤80 chars, line-spacing ≥1.5, no justificar; **2.5.8 Target Size (Minimum)** 24×24 CSS px (AA) + 5 excepciones. Toda cifra de contraste/target sale de aquí.
- **Nielsen Norman Group — "Visual Hierarchy in UX" (nngroup.com)** — jerarquía por tamaño/color/espacio; máx. 3 tamaños; el squint test como verificación.
- **Nielsen Norman Group — "F-Shaped Pattern of Reading" (2006, actualizado)** — patrones de escaneo (F, layer-cake, spotted, marking, commitment) y por qué el buen formato guía la atención.
- **Nielsen Norman Group — Gestalt (proximidad y serie relacionada)** — proximidad, similitud, región común, cierre, continuidad, figura/fondo aplicados a UI; base del agrupamiento visual.
- **Nielsen Norman Group — "Touch Target Size"** — mínimo físico **1cm × 1cm** para targets táctiles; el porqué de medir en tamaño físico y no solo px.
- **Material Design 3 — m3.material.io** — grid de espaciado **8dp (4dp fino)**; **layout grid** 4/8/12 columnas por breakpoint; escala tipográfica por roles (Display/Headline/Title/Body/Label); target táctil **48×48dp**; convenciones de dark mode/elevación. (Nota: páginas JS-rendered; cifras de valores tipográficos por baseline publicado de M3, no fetch en vivo.)
- **Apple Human Interface Guidelines — developer.apple.com/design** — target táctil mínimo **44×44pt**; convenciones de plataforma iOS. (Nota: HIG es JS-rendered; el 44pt es valor publicado establecido, no verificado por fetch en vivo esta sesión.)
- **Refactoring UI — Adam Wathan & Steve Schoger (refactoringui.com, libro)** — método accionable: diseñar en gris primero; jerarquía con peso+color antes que tamaño; empezar con demasiado whitespace; escala de espaciado no lineal (4,8,12,16,24,32,48,64,96,128…); paleta con muchos shades en HSL; menos bordes; emphasize by de-emphasizing; no gris puro sobre color. (Del libro; sus resúmenes web dieron 404 esta sesión — citado por conocimiento establecido de la obra.)
- **Laws of UX — Jon Yablonski (lawsofux.com)** — verificado el listado: Aesthetic-Usability Effect, Von Restorff/Isolation, Jakob's Law, Hick's, Miller's (7±2), Fitts's, Doherty (<400ms), Serial Position, Common Region, Proximity, Similarity, Prägnanz, etc. Base psicológica del énfasis y la consistencia.
- **Baymard Institute — "Line Length & Readability"** — óptimo **50–75 caracteres** por línea para cuerpo; cita WCAG 1.4.8 (≤80).
- **Smashing Magazine — CSS legibility/typography** — line-height contra x-height (`calc(1ex/0.32)`), medida 60–70ch, unidades relativas para tipografía responsive.
