# UX móvil

> **Cuando cargar este archivo:** al diseñar o evaluar la versión móvil (o mobile-first) de una app o producto — web, PWA o nativo — antes de decidir dónde van las acciones, qué tamaño tienen los targets, qué gestos usar, cómo se comporta ante teclado/notch/rotación, o cómo se ve en tablet vs teléfono vs desktop. Complementa [ver: fundamentos-ux] y [ver: patrones-ui]; para el móvil de un JUEGO (HUD, controles virtuales, auto-pausa in-game) el detalle está en [ver: gamedev/ux-ui-onboarding] — aquí va el ángulo producto/app, no se repite lo de juegos.

Este archivo es UX/UI **general de productos**. Los números duros están verificados contra fuente primaria (WCAG 2.2 en w3.org, Android/Material en developer.android.com, investigación de campo de Hoober). Donde la fuente es Apple HIG, se marca porque su página es un SPA que no se pudo leer directamente (el 44 pt está corroborado por WCAG AAA, que exige idéntico 44×44).

---

## 1. Mobile-first: empezar por lo chico

Diseñar primero la pantalla más pequeña y luego ampliar, no al revés. No es una moda: es una **restricción que fuerza prioridad**.

| Por qué mobile-first | Consecuencia de diseño |
|---|---|
| El móvil obliga a elegir qué es lo esencial (cabe poco) | Se destila el contenido a lo que de verdad importa; el desktop "hereda" esa jerarquía ya depurada |
| Escalar de chico→grande es aditivo (agregar); de grande→chico es amputar (esconder, romper) | Mobile-first evita el "responsive de recortes" donde el móvil queda mutilado |
| El grueso del tráfico web hoy es móvil | La versión móvil no es un caso secundario: suele ser **el** caso |
| El pulgar es menos preciso que un cursor de ratón | Targets más grandes, menos densidad, acciones al alcance — disciplina que también mejora el desktop |

**Dato NN/g (estudio de comprensión lectora, 1.629 casos):** la comprensión en móvil y desktop es casi idéntica (móvil ~3 puntos porcentuales por encima), pero en **contenido difícil el usuario móvil se ralentiza** (~30 ms/palabra extra) para mantener la comprensión. Conclusión operativa: en móvil, **brevedad y priorización** siguen siendo críticas para contenido complejo (financiero, médico, técnico) — no porque no se entienda, sino porque cuesta más esfuerzo. [ver: fundamentos-ux]

**Fitts's Law (Paul Fitts, 1954 · Laws of UX):** el tiempo para alcanzar un target es función de la **distancia** a él y su **tamaño** — targets más grandes y más cerca = más rápidos y con menos error. Es la ley física que justifica todo lo de abajo (targets grandes, acciones cerca del pulgar, bordes/esquinas como zonas "infinitas").

---

## 2. El pulgar como cursor · thumb zones

En móvil el cursor es el **pulgar**, y no llega cómodo a toda la pantalla. Investigación de campo de **Steven Hoober (UXmatters, 2013 · 1.333 observaciones reales en la calle)**:

| Cómo sostienen el teléfono | % | Quién toca la pantalla |
|---|---|---|
| **Una mano** | 49 % | El pulgar de esa mano (67 % derecho, 33 % izquierdo) |
| **Cradled** (una mano sostiene, la otra toca) | 36 % | Pulgar 72 % / dedo 28 % |
| **Dos manos** (ambos pulgares) | 15 % | Dos pulgares |

Regla derivada (confirmada por Josh Clark, citado en Smashing Magazine): **~49 % usa una mano** y **~75 % de las interacciones son con el pulgar**. Los usuarios **cambian de agarre constantemente** (a veces cada pocos segundos) según la tarea — no diseñar para un único agarre fijo.

### El mapa del pulgar (una mano, teléfono típico)

```
┌─────────────────────┐
│  🔴 DIFÍCIL          │  Esquinas superiores + borde superior:
│     (estirar,        │  estirar el pulgar o recolocar la mano.
│      recolocar)      │  → NADA crítico ni frecuente aquí.
│                      │
│  🟡 ESTIRAR          │  Mitad de pantalla: alcanzable con esfuerzo.
│     (alcanzable con  │  → Contenido secundario, listas scrolleables.
│      esfuerzo)       │
│                      │
│  🟢 NATURAL          │  Tercio inferior + centro-abajo:
│     (el pulgar       │  el pulgar descansa y se mueve aquí.
│      descansa aquí)  │  → Acciones primarias, nav principal, CTAs.
└─────────────────────┘
   Pantalla más grande = zona 🔴 crece (por eso los phablets
   empujaron los patrones de nav al fondo).
```

**Implicaciones de layout:**

- **Acciones primarias, navegación principal y CTAs → tercio inferior** (zona 🟢). Por eso las tab bars van abajo, no arriba.
- Acciones **destructivas** (borrar, cerrar sesión) fuera de la zona 🟢 o con confirmación — no donde el pulgar cae por inercia. [ver: patrones-ui]
- Nada esencial en las **esquinas superiores** ni pegado a los bordes (fundas, bezels y el propio agarre roban precisión).
- El botón "atrás"/menú arriba-izquierda es incómodo a una mano en pantallas grandes → soportar también **swipe-back** (iOS lo trae; en web, considerar gesto o botón inferior).
- Contenido largo se lee scrolleando con el pulgar en 🟢; las **acciones sobre ese contenido** (like, guardar, comprar) deben caer también en 🟢, no obligar a reposicionar la mano.

---

## 3. Touch targets: los números reales

Un target chico = "fat-finger errors". Las cifras de cada autoridad (todas apuntan a ~7-10 mm físicos):

| Guía | Mínimo | Notas |
|---|---|---|
| **Apple HIG (iOS)** | **44×44 pt** | Área tappable cómoda para *todos* los controles (fuente Apple HIG; corroborado por WCAG AAA) |
| **Material 3 / Android** | **48×48 dp** | ≈9 mm físicos, independiente de densidad de pantalla; **8 dp de separación mínima** entre targets |
| **WCAG 2.2 — 2.5.8 (AA)** | **24×24 CSS px** | Mínimo legal accesible. Excepción de *spacing*: un círculo de 24 px de diámetro centrado en cada target no debe intersecar otro |
| **WCAG 2.2 — 2.5.5 (AAA)** | **44×44 CSS px** | El estándar "cómodo" — mismo número que Apple |
| **NN/g / MIT Touch Lab** | **1×1 cm (≈10 mm)** | Yema del dedo mide 1,6–2 cm; pulgar ~2,5 cm de ancho. Menos de 1 cm = errores (investigación Parhi/Karlson/Bederson) |

**pt ≠ dp ≠ CSS px** como unidad exacta, pero los tres son "referencias independientes de densidad" de magnitud parecida; por eso los números difieren un poco. En la práctica: **apunta a ≥44 pt / 48 dp para cualquier control interactivo**, y trata 24 px como el piso legal, no como la meta.

**Separación (spacing) tan importante como el tamaño:**

- Material: ≥8 dp entre targets. WCAG 2.5.8: el "círculo de 24 px" cubre el caso de targets chicos bien separados.
- El **área tappable puede ser mayor que el área visible**: un icono de 24 dp puede tener un hit-slop invisible que lo lleva a 48 dp (patrón nativo estándar; en web, padding o pseudo-elemento). Esto reconcilia estética compacta con dedos reales.
- Filas de lista, chips, iconos de barra: revisar que el **hit target real** (no el glifo) cumpla el mínimo.

Contraste de los propios controles: **WCAG 1.4.11 Non-text Contrast (AA) exige 3:1** entre un componente UI (o su borde/estado) y el color adyacente — un botón "fantasma" gris claro sobre blanco falla. Texto: **4.5:1** normal, **3:1** texto grande (≥18 pt, o ≥14 pt bold). [ver: accesibilidad] [ver: fundamentos-visuales]

---

## 4. Gestos: potencia con riesgo de descubribilidad

| Gesto | Uso convencional | Riesgo |
|---|---|---|
| **Tap** | Acción primaria; siempre visible y con feedback | Ninguno — es el default |
| **Swipe** (horizontal) | Navegar entre pantallas/tabs, carrusel, acciones en fila de lista (archivar/borrar) | Oculto: el usuario no sabe que existe si no hay pista |
| **Swipe** (vertical) | Scroll (esperado); pull-to-refresh arriba; sheets que suben | Colisiona con scroll si no se calibra el umbral |
| **Long-press** | Menú contextual, preview, selección múltiple, reordenar | El más invisible de todos; casi nadie lo descubre solo |
| **Pull-to-refresh** | Recargar una lista/feed desde arriba | Convención fuerte en feeds; fuera de un feed, confunde |
| **Pinch/spread** | Zoom en mapas, imágenes | Solo donde el zoom tiene sentido |
| **Edge-swipe** | Back (iOS izquierda), abrir drawer | Puede chocar con controles pegados al borde |

**Regla de oro (Norman & Nielsen, "Gestural Interfaces: A Step Backwards in Usability"):** los gestos **carecen de descubribilidad, de affordance visible y a menudo de feedback**. Son atajos para expertos, **nunca el único camino** a una acción.

- Todo lo alcanzable por gesto debe ser alcanzable también por un control **visible** (botón, menú). El gesto acelera; el botón enseña. [ver: interaccion-microux]
- Dar **pistas de descubribilidad**: un pelín de la siguiente card asomando (hay más al swipe), un handle en el sheet, animación de "rebote" en la primera carga.
- Feedback inmediato durante el gesto: el elemento sigue al dedo (direct manipulation), no salta al soltar.
- No reasignar gestos del sistema (edge-swipe back de iOS, swipe-down de notificaciones) a acciones propias.
- Respetar el "juego a una mano": los gestos primarios deben poder iniciarse desde la zona 🟢.

---

## 5. Responsive vs adaptive · breakpoints

| Enfoque | Qué es | Cuándo |
|---|---|---|
| **Responsive** | Un layout fluido que se estira/reacomoda continuamente (%, `fr`, `flex`, `clamp()`, media queries) | Default para web/PWA de contenido; un solo codebase se adapta a todo |
| **Adaptive** | Layouts discretos distintos por rango de tamaño (o incluso pantallas separadas) | Cuando móvil y desktop necesitan estructura/IA distinta, no solo reflow (ej. app compleja con master-detail) |

En la práctica moderna se mezclan: **fluid dentro de cada breakpoint, saltos estructurales en los breakpoints**.

### Breakpoints de referencia (Material 3 / Android window size classes — verificado en developer.android.com)

| Size class | Ancho | Representa |
|---|---|---|
| **Compact** | `< 600 dp` | 99,96 % de teléfonos en portrait |
| **Medium** | `600–839 dp` | Tablets en portrait, plegables abiertos en portrait |
| **Expanded** | `840–1199 dp` | Tablets en landscape, plegables en landscape |
| **Large** | `1200–1599 dp` | Tablets grandes |
| **Extra-large** | `≥ 1600 dp` | Desktop |

Alto (útil para teclado/landscape): **Compact** `<480 dp`, **Medium** `480–899 dp`, **Expanded** `≥900 dp`.

> No memorizar breakpoints mágicos por dispositivo (hay demasiados): partir de estos rangos semánticos y **poner el breakpoint donde el contenido se rompe**, no donde está un iPhone concreto.

**WCAG 2.2 — 1.4.10 Reflow (AA):** el contenido debe poder mostrarse **sin scroll en dos dimensiones** a **320 CSS px de ancho** (equivale a un viewport de 1280 px al 400 % de zoom) y a **256 CSS px de alto** para contenido de scroll horizontal. Traducción: tu layout tiene que sobrevivir a 320 px de ancho reflowado. Es el piso duro del responsive. [ver: accesibilidad]

**Qué cambia entre móvil / tablet / desktop:**

| | Móvil (compact) | Tablet (medium/expanded) | Desktop (expanded+) |
|---|---|---|---|
| Columnas | 1 | 1–2 | 2–3+ |
| Navegación | Bottom tab bar / drawer | Nav rail lateral | Nav lateral persistente + top bar |
| Densidad | Baja (dedos) | Media | Alta (cursor preciso) |
| Master-detail | Apiladas (lista → detalle) | Lado a lado | Lado a lado |
| Hover | No existe → nada crítico depende de hover | Parcial | Sí (pero seguir sin depender de él) |

---

## 6. Safe areas: notch, isla dinámica, home indicator, barras

La pantalla física ≠ el área usable. Zonas que el sistema se reserva y que la UI **no debe pisar** con contenido interactivo o esencial:

| Zona | Dónde | Riesgo si la invades |
|---|---|---|
| **Notch / Dynamic Island** | Franja superior central (iPhone) | Texto/iconos tapados por la cámara/isla |
| **Home indicator** | Barra inferior (~34 pt en iOS sin botón home) | Botones bajo la barra: taps robados por el gesto de home |
| **Status bar** | Franja superior (hora, batería, señal) | Contenido detrás del reloj/batería |
| **System/navigation bars** | Barras del sistema Android (o gesture area) | Controles pisados por back/home del sistema |
| **Esquinas redondeadas** | Radio de la pantalla | Contenido cortado en las esquinas |

**Cómo respetarlas:**

- **Web/PWA:** `<meta name="viewport" content="viewport-fit=cover">` + CSS `env(safe-area-inset-top/right/bottom/left)` para paddings; en fullscreen usar **`dvh`, no `vh`** (el `vh` de iOS no descuenta la barra dinámica del navegador → el contenido queda debajo). [ver: gamedev/ux-ui-onboarding]
- **Nativo:** `safeAreaInsets` (iOS) / `WindowInsets` (Android edge-to-edge). Diseñar edge-to-edge (fondo hasta el borde) pero **contenido dentro del safe area inset**.
- **Fondo** puede (y suele) extenderse bajo el notch/barras para verse inmersivo; **texto, botones y touch targets, nunca.**
- Probar en dispositivos con y sin notch, y en landscape (los insets izquierdo/derecho aparecen ahí).

---

## 7. Convenciones de plataforma: iOS (HIG) vs Android (Material)

Los usuarios traen expectativas del sistema. Romperlas sin razón = fricción. **Regla:** en cada plataforma, seguir su convención de navegación aunque compartas codebase; una app cross-platform idéntica suele sentirse "ajena" en ambas.

| Patrón | iOS (Human Interface Guidelines) | Android (Material Design) |
|---|---|---|
| **Volver atrás** | Botón "‹ Título" arriba-izquierda + **edge-swipe** desde el borde izquierdo. **No hay** back del sistema | **Back del sistema** (gesto de borde o botón) — universal. "Up" arriba-izquierda para jerarquía |
| **Navegación principal** | **Tab bar abajo** (hasta ~5 ítems) | **Bottom navigation bar** (3–5 ítems) o **nav drawer** |
| **Acción primaria** | Botón en la nav bar (arriba-derecha) o CTA en contenido | **FAB** (Floating Action Button) flotando abajo-derecha |
| **Título de pantalla** | Centrado en la top bar (o large title a la izquierda) | Alineado a la izquierda en la top app bar |
| **Menú de más opciones** | Action sheet / botón explícito | **Overflow menu** (⋮ tres puntos) |
| **Confirmaciones** | Alert / action sheet desde abajo | Dialog / bottom sheet |
| **Switches/controles** | Estilo iOS (toggle redondeado) | Estilo Material (switch, ripple al tocar) |
| **Tipografía sistema** | San Francisco (SF) | Roboto |

- **Nativo vs custom:** usar componentes nativos por defecto (accesibilidad, familiaridad y mantenimiento gratis). Custom solo cuando aporta valor claro de marca/producto — y entonces replicar el *comportamiento* esperado (back, focus, gestos), no solo el aspecto. [ver: sistemas-diseno]
- **Un solo modelo de "atrás":** si tu app vive en ambas, no mezcles — respeta el back del sistema en Android y el swipe-back en iOS; no inventes un tercer botón que compita.
- Iconografía y glifos según plataforma (compartir: cuadrado-con-flecha en iOS vs los tres puntos conectados en Android).

---

## 8. Interrupciones: el móvil vive interrumpido

Una sesión móvil se corta todo el tiempo. La app **nunca puede perder trabajo** por eso.

| Interrupción | Comportamiento correcto |
|---|---|
| **Llamada / notificación / cambio de app** | Persistir estado al pasar a background; al volver, restaurar exactamente (scroll, formulario a medio llenar, paso del flujo). Matar la app no puede perder datos ingresados |
| **Rotación de pantalla** | Preservar estado a través del cambio de configuración (Android recrea la Activity: guardar en `onSaveInstanceState`/ViewModel; en web, no depender de `resize` para reconstruir estado). Si la app es solo-portrait, **bloquearlo explícitamente**, no dejarlo al azar |
| **Teclado que tapa el input** | El campo enfocado debe **scrollear a la vista sobre el teclado** (nunca quedar oculto). En web: `scrollIntoView`, cuidar `100vh`→usar `dvh`; probar el botón de submit (que no quede bajo el teclado). Nativo: `adjustResize`/keyboard avoidance |
| **Conexión intermitente** | Estados offline claros; reintentos; encolar acciones y sincronizar al volver. Nunca un spinner infinito sin salida. [ver: interaccion-microux] |
| **Bloqueo / batería baja / interrupción del sistema** | Autosave frecuente entre pasos; el flujo largo (checkout, formulario) sobrevive a que la pantalla se apague |

Principio: **guardar estado es responsabilidad de la app, no del usuario.** Cada interrupción es un test de "¿pierdo trabajo?". El equivalente en juegos (auto-pausa al perder foco, persistir en background) está en [ver: gamedev/ux-ui-onboarding].

---

## 9. Rendimiento percibido: en móvil la inmediatez pesa más

En móvil hay menos CPU, red peor y más impaciencia (contexto de uso: en movimiento, distraído). La **respuesta percibida** manda tanto como la real.

**Umbrales canónicos (Jakob Nielsen / NN/g, "Response Times: The 3 Important Limits"):**

| Tiempo | Percepción | Qué hacer |
|---|---|---|
| **≤ 0,1 s** | Instantáneo — sensación de manipulación directa | Feedback de tap/press debe caer aquí (estado :active, ripple) |
| **≤ 1 s** | El flujo de pensamiento no se corta (aunque note el delay) | Transiciones, cargas ligeras; no hace falta spinner |
| **≥ 10 s** | Se pierde la atención | Barra determinada + permitir seguir en otra cosa; evitar a toda costa |

**Doherty Threshold (Laws of UX): por debajo de ~400 ms de respuesta la productividad se dispara** y el usuario se "engancha". Objetivo de latencia percibida en interacciones: **< 400 ms**.

Técnicas de percepción (el "cómo se siente rápido"):

- **Feedback inmediato al tap** (< 0,1 s): cambio de estado visible antes de que llegue la respuesta del servidor. Un botón que no reacciona al instante se siente roto.
- **Optimistic UI:** mostrar el resultado esperado ya (like marcado, mensaje enviado) y revertir si falla. El usuario no espera al round-trip.
- **Skeleton screens** > spinners para cargas de contenido: la página "aparece" progresivamente y la espera se siente más corta. [ver: gamedev/ux-ui-onboarding]
- **Cargar primero lo visible** (above-the-fold), diferir el resto; imágenes con placeholder/blur-up y `loading="lazy"`.
- **Prefetch** de la siguiente pantalla probable; transiciones que ocultan la latencia real.
- Nunca bloquear toda la UI por una operación parcial: aislar el spinner al componente que carga.

---

## 10. Formularios y entrada de texto en móvil

Tipear en móvil es lento y molesto. La mejor entrada de texto es **la que no hay que teclear**. Best practices verificadas (Smashing Magazine, Google research):

### Teclado correcto por campo

| Campo | Atributo | Efecto |
|---|---|---|
| Email | `type="email"` / `inputmode="email"` | Teclado con `@` y `.com` |
| Teléfono | `type="tel"` | Teclado numérico de marcado |
| Número | `type="number"` / `inputmode="numeric"` | Dígitos (usar `inputmode` para PIN/códigos sin flechas de spinner) |
| URL | `type="url"` | Teclado con `/` y `.com` |
| Fecha | `type="date"` | Selector de fecha nativo |
| Búsqueda | `type="search"` + `enterkeyhint="search"` | Botón "Buscar" en el teclado |

- **`enterkeyhint`** ajusta la tecla de acción (Go / Next / Search / Send) al contexto del campo.

### Minimizar tipeo

- **Autofill / `autocomplete`** con tokens correctos (`name`, `email`, `tel`, `street-address`, `postal-code`, `cc-number`, `one-time-code` para OTP). Google: el autofill hace llenar formularios **~30 % más rápido**. Es de lo más alto ROI en un form móvil.
- `autocapitalize` para nombres/direcciones; `autocorrect` OFF en campos únicos (email, usuario, password) para que no "corrija" datos válidos.
- Defaults inteligentes, geolocalización para dirección, escaneo de tarjeta/documento, OTP autocompletado desde SMS.
- Preferir **selección sobre escritura**: pickers, chips, segmented controls, steppers.
- Formato mientras se escribe (máscaras de teléfono/tarjeta) sin bloquear el pegado.

### Layout del formulario

- **Una sola columna, siempre.** Google (eye-tracking): usuarios completan forms de una columna **~15,4 s más rápido** que multi-columna; múltiples columnas rompen el escaneo vertical.
- **Labels arriba del campo** (top-aligned): menos fixations, más rápido que labels a la izquierda. Placeholder **nunca** como único label (desaparece al escribir).
- Campos e inputs con el **mismo mínimo de touch target** (≥44 pt/48 dp de alto tappable).
- Validación **inline** y en el momento correcto (al salir del campo, no a cada tecla; errores claros con cómo arreglarlo). [ver: interaccion-microux]
- Pedir **solo lo imprescindible**; cada campo extra sube el abandono. Dividir forms largos en pasos con progreso visible.
- Botón de submit **visible sobre el teclado**, no escondido debajo.

---

## Reglas prácticas

1. **Mobile-first:** diseña la pantalla chica primero y amplía; nunca "recortes" desde el desktop.
2. **Acciones primarias en el tercio inferior** (zona 🟢 del pulgar); nada crítico en esquinas superiores ni pegado a bordes.
3. **Touch target ≥ 44 pt / 48 dp** para todo control; 24 px es el piso legal WCAG (AA), no la meta. Separación ≥ 8 dp.
4. El **área tappable puede exceder la visible**: hit-slop invisible para llevar iconos chicos a 48 dp.
5. **Contraste:** texto 4.5:1 (3:1 si grande); componentes UI y sus bordes/estados 3:1 (WCAG 1.4.11).
6. **Ningún gesto como único camino:** todo lo alcanzable por swipe/long-press también por un control visible; da pistas de descubribilidad y feedback en vivo.
7. No secuestres gestos del sistema (edge-swipe back, pull-down de notificaciones).
8. **Responsive fluido dentro del breakpoint, saltos estructurales en él;** pon el breakpoint donde se rompe el contenido, no en un dispositivo concreto.
9. Sobrevive a **320 CSS px de ancho reflowado** sin scroll en dos dimensiones (WCAG 1.4.10).
10. **Respeta safe areas:** `viewport-fit=cover` + `env(safe-area-inset-*)`; usa `dvh`, no `vh`; fondo hasta el borde, contenido dentro del inset.
11. **Sigue la convención de cada plataforma:** back del sistema en Android, swipe-back en iOS; tab bar abajo; no inventes un tercer modelo de "atrás".
12. **Nunca pierdas trabajo por una interrupción:** persistir estado en background, en rotación y con pantalla bloqueada; restaurar exactamente al volver.
13. **El teclado nunca tapa el campo enfocado** ni el botón de submit; scroll a la vista sobre el teclado.
14. **Feedback al tap en < 0,1 s;** apunta a < 400 ms de latencia percibida (Doherty); optimistic UI + skeletons antes que spinners.
15. **La mejor entrada de texto es no teclear:** `inputmode`/`type` correcto por campo, `autocomplete`/autofill, pickers sobre escritura.
16. **Formulario de una sola columna, labels arriba,** placeholder nunca como label, validación inline con solución.
17. Pide **solo lo imprescindible**; pasos con progreso para forms largos.
18. **Prueba en dispositivo real**, una mano, con y sin notch, portrait y landscape — el simulador no mide dónde llega el pulgar.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Diseñar en desktop y "responsivizar" recortando → móvil mutilado | Mobile-first: destila lo esencial en chico, amplía hacia arriba |
| CTA o navegación arriba, lejos del pulgar | Acciones primarias en el tercio inferior (zona 🟢); tab bar abajo |
| Iconos de 24 px sin hit-slop → fat-finger errors | Área tappable ≥ 44 pt/48 dp aunque el glifo sea chico; separación ≥ 8 dp |
| Botón "fantasma" gris claro sobre blanco | Componentes UI a 3:1 (WCAG 1.4.11); no fiar el estado solo al color |
| Función clave escondida en un long-press que nadie descubre | Todo gesto tiene un control visible equivalente + pista de descubribilidad |
| Carrusel/acción de swipe sin indicio de que existe | Asomar la siguiente card, handles, animación de rebote inicial |
| Breakpoints atados a modelos concretos de iPhone | Rangos semánticos (compact/medium/expanded); breakpoint donde se rompe el contenido |
| Contenido bajo el notch / botones bajo el home indicator | `env(safe-area-inset-*)` + `viewport-fit=cover`; contenido dentro del inset |
| `100vh` que deja el submit debajo de la barra del navegador iOS | Usar `dvh`; probar el botón real sobre el teclado |
| App idéntica en iOS y Android que ignora el back del sistema | Respetar la convención de cada plataforma; un solo modelo de "atrás" por OS |
| Rotar o recibir una llamada borra el formulario a medio llenar | Persistir estado en config-change y background; restaurar exacto |
| Teclado tapa el campo que se está escribiendo | Scroll del campo enfocado a la vista sobre el teclado |
| Spinner infinito mientras carga toda la pantalla | Skeletons, optimistic UI, aislar el loading al componente; feedback < 0,1 s |
| Form de dos columnas y labels dentro del input (placeholder) | Una columna, labels arriba; placeholder nunca como único label |
| Teclado alfabético para un PIN o un teléfono | `inputmode`/`type` correcto por campo; `autocomplete` para autofill |
| Pedir 12 campos "por si acaso" | Solo lo imprescindible; cada campo extra sube el abandono |

## Fuentes

- **WCAG 2.2 — Understanding Success Criteria (w3.org/WAI)** — *fuente primaria, verificada directamente.* 2.5.8 Target Size Minimum (24×24 CSS px, AA, con excepción de spacing del círculo de 24 px); 2.5.5 Target Size Enhanced (44×44 CSS px, AAA); 1.4.3 Contrast Minimum (4.5:1 texto / 3:1 texto grande ≥18 pt o ≥14 pt bold); 1.4.11 Non-text Contrast (3:1 componentes UI y gráficos); 1.4.10 Reflow (320 CSS px ancho / 256 CSS px alto, equivalente a 400 % de zoom). El piso legal de accesibilidad móvil.
- **Android Accessibility Help + Material Design (developer.android.com, support.google.com/accessibility)** — *primaria, verificada.* Touch target mínimo 48×48 dp (≈9 mm físicos, rango recomendado 7–10 mm); 8 dp de separación. Window size classes: compact <600 dp, medium 600–839, expanded 840–1199, large 1200–1599, extra-large ≥1600 dp (ancho). Los breakpoints y el target de facto en Android.
- **Apple Human Interface Guidelines — Layout / Accessibility (developer.apple.com)** — 44×44 pt como área tappable mínima cómoda. *Nota de honestidad: la página es un SPA que no se pudo leer por WebFetch; el 44×44 es la cifra de facto de Apple, corroborada por el idéntico 44×44 CSS px de WCAG 2.5.5 AAA.* Convenciones iOS (tab bar, swipe-back, sin back de sistema).
- **"How Do Users Really Hold Mobile Devices?" — Steven Hoober, UXmatters (2013)** — *primaria, investigación de campo, 1.333 observaciones.* 49 % una mano / 36 % cradled / 15 % dos manos; dominancia del pulgar; los usuarios cambian de agarre constantemente. Base empírica de las thumb zones.
- **"Designing for Thumbs / The Thumb Zone" — Smashing Magazine (citando a Josh Clark)** — el mapa de zonas 🟢/🟡/🔴, ~49 % una mano y ~75 % de interacciones con el pulgar, y dónde colocar nav y acciones.
- **"Touch Targets on Touchscreens" / "Design for Fingers" — Nielsen Norman Group** — mínimo 1×1 cm (≈10 mm); yema 1,6–2 cm, pulgar ~2,5 cm; investigación Parhi/Karlson/Bederson y MIT Touch Lab sobre error rates. Por qué el tamaño físico (no el pixel) manda.
- **"Reading Content on Mobile Devices" — Nielsen Norman Group (estudio de comprensión, 1.629 casos)** — comprensión móvil≈desktop pero el contenido difícil cuesta más esfuerzo en móvil; brevedad y priorización siguen siendo críticas. Fundamento del mobile-first como disciplina de prioridad.
- **"Response Times: The 3 Important Limits" — Jakob Nielsen / NN/g** — 0,1 s (instantáneo), 1 s (flujo intacto), 10 s (límite de atención). El marco del rendimiento percibido.
- **Laws of UX (lawsofux.com) — Fitts's Law y Doherty Threshold** — tiempo de alcance = f(distancia, tamaño) → targets grandes y cerca; y el umbral de ~400 ms bajo el cual la productividad se dispara.
- **"Best Practices for Mobile Form Design" — Smashing Magazine (+ Google research)** — `input type`/`inputmode` por campo, `autocomplete`/autofill (~30 % más rápido, Google), una columna (~15,4 s más rápido), labels arriba, targets 48 dp con 8 dp de separación. Base de la sección de formularios.
- **"Gestural Interfaces: A Step Backwards in Usability" — Don Norman & Jakob Nielsen** — los gestos carecen de descubribilidad, affordance y feedback; nunca deben ser el único camino a una acción.
