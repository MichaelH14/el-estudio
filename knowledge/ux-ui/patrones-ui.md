# Patrones de UI comunes

> **Cuando cargar este archivo:** al diseñar, elegir o auditar cualquier componente de interfaz de una app o producto (web o móvil) — navegación, formularios, listas/tablas, cards, modales/sheets, estados vacíos, loading, feedback, búsqueda/filtros — y para decidir *qué patrón usar y cuándo*. Complementa [ver: fundamentos-ux] (principios y heurísticas: el *por qué*); aquí está el *qué patrón y cuándo* con números. Lo específico de UI de JUEGOS (HUD, tutoriales in-game, FTUE) vive en [ver: gamedev/ux-ui-onboarding]; el game-feel en [ver: gamedev/game-feel]; la implementación de UI en Unity en [ver: unity/ui-unity] y [ver: pipeline/ui-flujo-completo].

Regla base para todo este archivo: **no inventes un patrón nuevo cuando existe uno que el usuario ya conoce** (Ley de Jakob — "los usuarios pasan la mayor parte del tiempo en OTROS sitios y esperan que el tuyo funcione igual", Laws of UX). El patrón convencional gana casi siempre; innova solo donde aporta valor medible.

---

## 1. Cómo elegir un patrón (framing rápido)

Antes de colocar cualquier componente, responder:

| Pregunta | Decide entre |
|---|---|
| ¿Cuántas opciones/destinos hay? | Tab bar (≤5) vs drawer/hamburger (>5) · Segmented control (2-5) vs dropdown (>5) |
| ¿El usuario tiene un objetivo concreto o explora? | Objetivo → búsqueda/filtros/paginación · Explora → feed/scroll infinito |
| ¿Cuánto cuesta interrumpir ahora? | Inline/toast (bajo) vs modal (alto, solo si es crítico) |
| ¿La info es permanente, contextual o bajo demanda? | Heurística del HUD aplica también a apps [ver: gamedev/ux-ui-onboarding §1] |
| ¿Es acción reversible? | Reversible → hacer + ofrecer Undo · Irreversible/destructiva → confirmación explícita |

Leyes que gobiernan estas decisiones (Laws of UX — Jon Yablonski, verificado en lawsofux.com):
- **Hick's Law**: el tiempo de decisión crece con el número y complejidad de opciones → menos opciones visibles a la vez, progressive disclosure.
- **Fitts's Law**: el tiempo para alcanzar un target depende de su **distancia** y **tamaño** → botones primarios grandes y cerca del pulgar; targets pequeños y lejanos son caros [ver: mobile-ux thumb zone].
- **Miller's Law**: ~7±2 ítems en memoria de trabajo → agrupar (chunking) menús y formularios.
- **Doherty Threshold**: la productividad se dispara cuando la respuesta es **< 400 ms**; por encima, el usuario percibe espera → feedback inmediato (ver §8).

---

## 2. Navegación

### 2.1 Patrones y cuándo usar cada uno

| Patrón | Plataforma | Cuándo | Límite / número |
|---|---|---|---|
| **Tab bar / bottom nav** | Móvil (iOS bottom tab, Android nav bar) | 3-5 destinos primarios de igual peso, acceso frecuente | **≤5 ítems**; con más, tabs se vuelve ineficiente (NN/g). Visible = alta discoverability |
| **Top nav bar** | Web/desktop | Sitio con pocas secciones, marca arriba | Combina con mega-menú si hay muchas categorías |
| **Drawer / hamburger** | Móvil y web | **>5** destinos, o navegación secundaria de sitios "browse-mostly" (noticias, contenido) | Ahorra espacio pero *"out of sight, out of mind"*: reduce discoverability y uso (NN/g) |
| **Segmented control / tabs internas** | Ambos | Alternar 2-5 vistas del MISMO objeto (no navegar entre secciones) | >5 opciones → usar dropdown |
| **Breadcrumbs** | Web jerárquica | Wayfinding en jerarquías de **≥3 niveles**, sobre todo si el usuario entra por búsqueda externa | Innecesario en estructuras planas (1-2 niveles) |

### 2.2 El debate hamburger vs tabs (evidencia NN/g)

- **Hidden navigation (hamburger)** sacrifica discoverability por espacio: los destinos ocultos se usan menos, incluso por usuarios que conocen el ícono. *"Out of sight is out of mind."*
- **Visible navigation (tab bar)** mantiene los destinos siempre a la vista → mayor engagement con la navegación, pero cuesta espacio de pantalla y escala mal (>5 ítems).
- **Regla operativa**: destinos primarios (los que el usuario usa a diario) → tab bar visible. Todo lo demás (settings, ayuda, secciones raras) → dentro del hamburger o en un tab "Más". Nunca metas la acción principal solo en el hamburger.
- Móvil con 3-5 secciones core → **bottom tab bar** casi siempre gana. Sitio de contenido con 8+ categorías → hamburger + búsqueda prominente.

### 2.3 Breadcrumbs (reglas NN/g)

- Reflejan la **jerarquía del sitio (IA)**, NO el historial de sesión.
- Ubicación: arriba, justo debajo de la navegación global; empiezan por Home.
- El ítem actual (último) **nunca es un link**.
- **Nunca reemplazan** la navegación global ni la local de la sección — la complementan.
- Móvil: no envolver en varias líneas; truncar a mostrar solo el padre inmediato si hace falta.

---

## 3. Formularios

El formulario es donde más se pierde y se frustra al usuario. Principio rector: **el formulario más corto posible** — cada campo es fricción; borra todo lo que no sea estrictamente necesario ahora.

### 3.1 Reglas de estructura

| Regla | Detalle |
|---|---|
| **Label siempre visible** | Label ARRIBA del campo (mejor para escaneo vertical y móvil). El **placeholder NO es label** — desaparece al escribir, mata la memoria y falla accesibilidad. |
| **Single column** | Una columna vertical; multi-columna rompe el flujo de lectura y la gente salta campos. |
| **Agrupar (chunking)** | Miller's Law: agrupa campos relacionados (datos personales / envío / pago) con espaciado o secciones. |
| **Input types correctos** | `type=email/tel/number/date/url`, `inputmode`, `autocomplete` → teclado adecuado en móvil y autofill. Enorme ganancia con cero costo. |
| **Marcar lo opcional, no lo requerido** | Si casi todo es requerido, marca solo `(opcional)`; menos ruido de asteriscos. |
| **Botón primario claro** | Un solo CTA primario visible; acciones secundarias con menos peso. Nunca dos botones igual de prominentes. |

### 3.2 Validación — cuándo y cómo mostrar errores (NN/g)

| Momento | Qué hacer |
|---|---|
| **Mientras escribe (premature)** | **NO** validar en campos vacíos aún sin tocar ni durante la exploración. Marcar error antes de que el usuario termine es hostil. |
| **Inline, selectiva** | Validación en tiempo real solo para campos **propensos a error** (contraseña con reglas, username disponible, confirmación de email). Idealmente valida al `blur` (salir del campo), no en cada tecla. |
| **On submit** | Si no llegaste a validar inline, valida al enviar: muestra un resumen arriba + marca cada campo. Lleva el foco al primer error. |
| **Recuperación** | Preserva SIEMPRE lo que el usuario escribió (nunca vaciar el form). Mensaje **junto al campo**, específico, y con la solución. |

Mensaje de error (NN/g error-message-guidelines):
- **Ubicación**: pegado a la fuente del error (proximidad reduce carga cognitiva).
- **Redacción**: lenguaje plano, específico ("Ingresa una fecha con formato DD/MM/AAAA"), NUNCA genérico ("Ocurrió un error") ni culpando ("entrada inválida/ilegal").
- **No solo color**: rojo + ícono + texto (deficiencia de visión de color afecta a una porción significativa de usuarios — cifra exacta NO VERIFICADA contra fuente primaria en este documento; ver §11 y [ver: accesibilidad]).
- Severidad: errores graves → modal; leves → inline/banner/toast.

---

## 4. Listas y tablas

### 4.1 Densidad

- **Comfortable** (más padding, 1 acción a la vista): apps de consumo, móvil, lectura casual.
- **Compact/dense** (más filas por pantalla): herramientas de poder, dashboards, tablas de datos donde comparar es el trabajo. Ofrecer toggle de densidad en apps pro.

### 4.2 Paginación vs scroll infinito vs "Load more" (NN/g)

| Patrón | Úsalo cuando | Evítalo cuando |
|---|---|---|
| **Paginación numerada** | El usuario busca algo específico, compara, o necesita volver al mismo punto; hay footer con info clave | Feed de descubrimiento continuo |
| **Scroll infinito** | Exploración homogénea sin objetivo (redes, noticias, feed) — minimiza interacción, sube engagement | Búsqueda de algo concreto, comparar listas largas, o si el footer importa (lo bloquea) |
| **"Load more" (botón)** | Punto medio: da control, no rompe el footer, controla ancho de banda | Cuando el volumen es tan alto que el botón cansa |

Problema clásico del scroll infinito: **el botón Atrás** devuelve al tope y obliga a re-scrollear todo lo ya visto → mortal para tareas orientadas a objetivo. Paginación mantiene al usuario en una página manejable. Híbrido emergente: scroll infinito con números de página como landmarks (data de usabilidad aún limitada, según NN/g).

### 4.3 Orden, filtro y acciones

- **Orden (sort)**: sobre la columna en tablas; en listas móviles, un control de "Ordenar por" arriba. Indica la columna/criterio activo y la dirección.
- **Filtro**: para catálogos grandes, filtros a la izquierda (desktop) o en un bottom sheet (móvil). Muestra **cuántos resultados** quedan y **filtros activos como chips removibles**. Distingue filtrar (reduce el set) de buscar (query).
- **Acciones por fila**: la acción primaria clara; las secundarias en un overflow menu (⋮) para no saturar. En móvil, swipe actions (con ícono + label, no solo color). Acción destructiva por fila → siempre con confirmación o undo (§9).
- **Bulk actions**: checkbox por fila + barra de acciones contextual que aparece al seleccionar.

### 4.4 Tablas responsive

Una tabla ancha NO cabe en móvil. Estrategias, de mejor a peor según caso:

| Estrategia | Cuándo |
|---|---|
| **Priorizar columnas** | Ocultar columnas menos importantes en móvil, mostrar la clave + expandir por fila |
| **Card por fila (stacking)** | Cada fila se convierte en una tarjeta vertical con label:valor. Ideal para pocas columnas, mucho detalle |
| **Scroll horizontal contenido** | Congelar la primera columna (identificador) y hacer scroll-x del resto. El scroll debe estar DENTRO de un contenedor, nunca hacer scroll horizontal la página entera |
| **Vista resumen + detalle** | Tabla mínima → tap abre pantalla/sheet con todo |

Nunca reduzcas la fuente a ilegible para que "quepa". Ni targets < mínimo (§11).

---

## 5. Cards

### 5.1 Cuándo una card (y cuándo no)

- **Sí card**: cuando cada ítem es una **entidad autónoma** que agrupa contenido heterogéneo (imagen + título + meta + acciones) y compite en un grid escaneable — productos, posts, proyectos, contactos.
- **No card**: listas simples de texto uniforme (una lista con divisores es más densa y rápida de escanear); datos tabulares comparables (usa tabla); UI donde la card solo añade bordes y sombras sin agrupar nada real. Refactoring UI: **demasiados bordes ensucian** — usa espaciado o fondo para separar antes que enmarcar todo.

### 5.2 Anatomía y grid

- Anatomía típica: media (opcional) → título → texto de apoyo → metadata → acciones. Una **acción primaria** por card como mucho; el resto en overflow.
- **Toda la card clickable** llevando al detalle es lo esperado; si hay acciones internas, cuida que no se solapen los hit targets (Fitts/§11).
- Grid: columnas responsive (`auto-fill`/`minmax`), gutter consistente de la escala de espaciado (§11). Mantén altura coherente o usa masonry a propósito, no por accidente.
- Jerarquía DENTRO de la card por **peso y color de fuente**, no solo tamaño (Refactoring UI: "size isn't everything").

---

## 6. Modales, sheets y popovers

Interrumpir tiene un costo alto. NN/g: *"a nadie le gusta ser interrumpido; si debes hacerlo, que valga la pena"*.

### 6.1 Cuándo interrumpir con un modal (NN/g modal-nonmodal)

| Justificado | NO justificado |
|---|---|
| Error crítico / prevenir pérdida de datos irreversible | Newsletter / promo no solicitada |
| Info requerida para continuar un flujo que el usuario inició (login para guardar favorito) | Interrumpir un checkout u otro proceso de alto valor |
| Wizard: partir una tarea multi-paso en trozos digeribles (con indicador de progreso) | Decisiones complejas que requieren info externa que el modal tapa |

Costos del modal: rompe el flujo, sube carga cognitiva (olvidas la tarea previa), añade pasos, y **tapa el contexto** que quizá necesitas para responder.

### 6.2 Elegir el contenedor correcto

| Contenedor | Móvil/Desktop | Uso |
|---|---|---|
| **Modal / dialog centrado** | Ambos | Decisión bloqueante corta, confirmación crítica, formulario breve. Focus trap, cierre por Esc/botón/backdrop (salvo destructivo), foco al abrir, devolver foco al cerrar [ver: accesibilidad] |
| **Bottom sheet** | Móvil ★ | Acciones contextuales, selección, filtros, detalles — nace desde abajo (thumb zone), arrastrable, se descarta deslizando. Preferible al modal centrado en móvil |
| **Side sheet / drawer** | Desktop | Panel de detalle/edición sin perder la lista de fondo |
| **Popover / dropdown** | Ambos | Menú de opciones anclado a un control; NO para contenido crítico. Se cierra al hacer click fuera |
| **Inline expand** | Ambos | Detalle progresivo sin sacar al usuario de contexto — la opción menos intrusiva; prefiérela si cabe |

Regla anti-abuso: si la interrupción no sirve al objetivo del USUARIO (solo al negocio), no uses modal. Wizard multi-paso → **muestra progreso** para evitar abandono (NN/g).

---

## 7. Estados vacíos (empty states)

El empty state suele ser la **primera impresión** de una pantalla. Un espacio en blanco confunde; conviértelo en onboarding contextual (NN/g empty-state-interface-design; para juegos, ver la sección "Errores y estados vacíos" en [ver: gamedev/ux-ui-onboarding]).

### 7.1 Los tres tipos y qué debe llevar cada uno

| Tipo | Situación | Qué mostrar |
|---|---|---|
| **First use (nunca hubo datos)** | Bandeja/dashboard/lista recién creada | Explicar qué irá aquí + **acción directa** para poblarlo ("Añade tu primera fuente") + opción "explorar con datos demo" |
| **User-cleared (el usuario lo vació)** | Inbox a cero, tareas completadas | Refuerzo positivo ("Todo al día") — celebrar, no alarmar |
| **No results (búsqueda/filtro sin match)** | Query o filtros sin resultados | Confirmar el estado ("No hay registros para ese rango"), sugerir ampliar/limpiar filtros, ofrecer corrección de query |

### 7.2 Convertir el vacío en onboarding

- Tres funciones del empty state bien diseñado (NN/g): (1) **comunicar estado del sistema** (sube confianza), (2) **enseñar** qué puede poblar el área y cómo, (3) **dar un camino de acción** (link directo a la tarea).
- Las "pull revelations" (ayuda contextual disparada cuando el usuario ya empezó la tarea) se recuerdan mejor que un tutorial forzado aparte — coincide con FTUE contextual de juegos [ver: gamedev/ux-ui-onboarding].
- NUNCA dejes el área totalmente en blanco ni con un "—" gigante donde iba un valor: resuelve el estado sin dato con default/placeholder o un mensaje útil.

---

## 8. Loading, skeleton screens y optimistic UI

Objetivo: **percepción de velocidad**, no solo velocidad real. Se apoya en los tres límites de respuesta de Jakob Nielsen (nngroup.com, "Response Times: The 3 Important Limits"):

| Límite | Percepción | Feedback |
|---|---|---|
| **0.1 s (100 ms)** | Instantáneo, manipulación directa | Ninguno especial; solo mostrar el resultado |
| **1.0 s** | Se nota, pero el hilo de pensamiento sigue intacto | Sin feedback especial; ideal mantenerse aquí (concuerda con Doherty < 400 ms de Laws of UX) |
| **10 s** | Límite para mantener la atención | Progreso con % y estimación; permitir cancelar; más de 10 s → el usuario se va a otra cosa |

### 8.1 Qué indicador según la duración (NN/g skeleton-screens)

| Espera | Indicador |
|---|---|
| < 1 s | Nada (o transición sutil). Un skeleton que parpadea < 1 s marea |
| 1-10 s, página/layout completo | **Skeleton screen**: wireframe que revela la estructura → "ilusión de espera más corta"; reduce carga cognitiva mostrando cómo se organizará el contenido |
| 2-10 s, un módulo aislado (card, video) | **Spinner** localizado en ese módulo |
| > 10 s | **Progress bar** con estimación de duración/estado |

### 8.2 Optimistic UI

- Asume éxito y **actualiza la UI de inmediato** (like, enviar mensaje, mover tarjeta), luego confirma con el servidor en segundo plano. Elimina la espera percibida en acciones de alta frecuencia y baja probabilidad de fallo.
- Requisito: **rollback claro** si el servidor falla (revertir el cambio + toast de error explicando). Sin manejo de error, el optimistic UI miente al usuario.
- No lo uses en acciones críticas/irreversibles (pagos, borrados definitivos): ahí el usuario necesita confirmación real del sistema.

---

## 9. Feedback: toasts, confirmaciones, éxito/error, undo

Todo cambio de estado necesita feedback (mismo principio que "feedback" en HUD de juego [ver: gamedev/ux-ui-onboarding §1]).

| Mecanismo | Cuándo | Reglas |
|---|---|---|
| **Toast / snackbar** | Confirmar acción de bajo impacto que YA ocurrió ("Guardado", "Mensaje enviado") | Efímero (auto-dismiss ~4-6 s), no bloquea, esquina/borde. NO para errores que exigen acción, ni para info que el usuario debe conservar |
| **Snackbar con Undo** | Acción reversible con riesgo de error (borrar, archivar, enviar) | Ejecuta la acción + ofrece **Undo** durante unos segundos. Mejor UX que un modal "¿seguro?" para lo reversible |
| **Confirmación (modal)** | Acción **destructiva o irreversible** (borrado permanente, pago, acción masiva) | Nombrar exactamente qué se afecta; botón destructivo con color/label claro ("Eliminar 12 archivos"), no un "OK" genérico |
| **Inline success/error** | Resultado de un form o de un campo | Junto al elemento; error específico y con solución (§3.2) |
| **Banner** | Estado global persistente (sin conexión, mantenimiento, cuota) | Permanece hasta que se resuelve; no efímero |

Heurística Undo-first: **preferir "hacer + Undo" a "preguntar antes"** siempre que la acción sea reversible — menos fricción y menos diálogos de confirmación que la gente clickea sin leer. Reservar la confirmación modal para lo verdaderamente irreversible.

---

## 10. Búsqueda, filtros y onboarding de app

### 10.1 Búsqueda

- Campo visible (no escondido tras un ícono) cuando la búsqueda es un camino primario; ícono-que-expande solo si es secundaria.
- **Search-as-you-type / autosuggest**: muestra sugerencias mientras escribe (respuesta idealmente < 400 ms, Doherty). Distingue **autocomplete** (completa la query) de **instant results** (muestra resultados en vivo). Debounce del input para no golpear el servidor en cada tecla.
- Estado sin resultados = empty state de tipo "no results" (§7): sugerir corregir/ampliar, no dejar en blanco.
- Recordar búsquedas recientes y ofrecer filtros/scopes cuando el corpus es grande.

### 10.2 Filtros

- Chips de filtros activos siempre visibles y removibles; contador de resultados en vivo.
- Móvil: filtros en bottom sheet con "Aplicar" (evita re-render en cada toque si es costoso) o aplicación instantánea si es barato. Botón "Limpiar todo".
- No confundir filtrar (reduce el set actual) con buscar (query nueva) ni con ordenar.

### 10.3 Onboarding de app (producto, no juego)

- **Menos es más**: el mejor onboarding suele ser NINGUNo — que la app se explique sola. Si hace falta, prefiere **onboarding contextual** (coach marks/tooltips en el momento en que la feature es relevante) sobre un carrusel de intro que la gente salta.
- Pide permisos (notificaciones, ubicación, cámara) **en contexto**, cuando se necesitan y explicando el porqué — no todos de golpe al abrir.
- "Empty state como onboarding" (§7) suele batir a un tour separado: se aplica de inmediato y se recuerda mejor.
- Progressive disclosure: revela complejidad a medida que el usuario avanza (Hick's Law). Para tours de juego con manita/pasos, ver [ver: gamedev/ux-ui-onboarding].

---

## 11. Números de referencia (verificados contra fuente primaria)

| Dato | Valor | Fuente (criterio) |
|---|---|---|
| **Target táctil mínimo (web)** | **24 × 24 CSS px** | WCAG 2.2 SC 2.5.8 Target Size (Minimum), **nivel AA**. Excepciones: spacing (círculo de 24px sin solaparse), equivalent, inline, user-agent, essential |
| **Target táctil "enhanced"** | **44 × 44 CSS px** | WCAG 2.2 SC 2.5.5 Target Size (Enhanced), **nivel AAA** |
| **Target táctil iOS** | **44 × 44 pt** | Apple Human Interface Guidelines (recomendación estándar de hit area) |
| **Target táctil Android/Material** | **48 × 48 dp**, con **≥ 8 dp** de separación entre targets | Material Design (accessibility) |
| **Contraste texto normal** | **≥ 4.5 : 1** | WCAG 2.2 SC 1.4.3 Contrast (Minimum), **AA** |
| **Contraste texto grande** | **≥ 3 : 1**; "grande" = **≥ 18 pt** o **≥ 14 pt bold** (≈ 24 px / ≈ 18.5 px, con 1 pt = 1.333 px) | WCAG 2.2 SC 1.4.3, **AA** |
| **Contraste no-textual** (bordes de inputs, íconos, componentes UI, datos de gráficos) | **≥ 3 : 1** | WCAG 2.2 SC 1.4.11 Non-text Contrast, **AA** |
| **Contraste enhanced** | **7 : 1** normal / **4.5 : 1** grande | WCAG 2.2 SC 1.4.6 Contrast (Enhanced), **AAA** |
| **Respuesta instantánea** | **≤ 0.1 s (100 ms)** — sin feedback | Nielsen, "Response Times: 3 Limits" |
| **Hilo de pensamiento intacto** | **≤ 1 s** | Nielsen |
| **Límite de atención** | **10 s** — mostrar % y permitir cancelar | Nielsen |
| **Umbral de fluidez** | respuesta **< 400 ms** | Doherty Threshold (Laws of UX) |
| **Tab bar máx.** | **≤ 5** ítems; con más, pasar a hamburger | NN/g mobile navigation |

Escala de espaciado (design tokens): usa una escala definida (p. ej. base 4/8: 4, 8, 12, 16, 24, 32, 48, 64…), **no incrementos arbitrarios de 1 px** (Refactoring UI: "establish a spacing and sizing system"). Detalle de tokens y grid en [ver: sistemas-diseno] y [ver: fundamentos-visuales].

---

## 12. Anti-patrones y dark patterns a evitar

Un **dark pattern** (Harry Brignull, deceptive.design) es UI diseñada para engañar o coaccionar al usuario a favor del negocio. Además de ser hostil, hay regulación creciente (GDPR, FTC, DSA) que los sanciona. Los principales:

| Dark pattern | Qué es | Antídoto |
|---|---|---|
| **Confirmshaming** | Botón de rechazo redactado para avergonzar ("No, prefiero pagar de más") | Opciones neutrales y de igual peso visual |
| **Roach motel / obstruction** | Fácil entrar (suscribirse), dificilísimo salir (cancelar) | Cancelar tan fácil como suscribirse |
| **Sneaking / hidden costs** | Cargos o ítems que aparecen recién al final del checkout | Precio total transparente desde el inicio |
| **Forced continuity** | Trial que cobra sin avisar al terminar | Recordatorio antes del cobro + cancelación simple |
| **Nagging** | Pedir lo mismo (permiso, rating, upgrade) una y otra vez | Pedir una vez, en contexto, y respetar el "no" |
| **Misdirection / false hierarchy** | Resaltar la opción cara/beneficiosa para el negocio y esconder la gratuita | Jerarquía honesta según el objetivo del USUARIO |
| **Urgencia/escasez falsa** | Contadores y "quedan 2" inventados | Urgencia solo si es real y verificable |
| **Trick questions / preseleccionados** | Checkboxes de opt-in premarcados, doble negación | Opt-in explícito, lenguaje claro |
| **Disguised ads** | Anuncios que parecen contenido o controles del sistema | Etiquetar publicidad; separar de la UI real |
| **Privacy Zuckering** | Empujar a compartir más datos de los que el usuario quiere | Defaults de privacidad mínimos; granularidad de consentimiento |

Anti-patrones de UI (no necesariamente maliciosos, pero rompen usabilidad): **botones muertos** (sin acción en producción — cero en release), **modal-spam** al abrir la app, **placeholder-as-label**, scroll infinito que tapa el footer con info legal, tablas ilegibles por encoger fuente, y "mystery meat navigation" (íconos sin label que nadie entiende — usa label + ícono).

---

## Reglas prácticas

1. **Convención antes que invención** (Ley de Jakob): usa el patrón que el usuario ya conoce; innova solo con evidencia de que aporta.
2. Navegación primaria: **≤5 destinos → tab bar visible**; más → hamburger, pero nunca escondas la acción principal ahí.
3. Formulario más corto posible: borra campos, agrupa el resto, label arriba (nunca placeholder-as-label), `type`/`autocomplete`/`inputmode` correctos.
4. **No valides prematuro**: inline solo en campos error-prone (al `blur`); si no, on-submit con foco al primer error y preservando lo escrito.
5. Errores: junto al campo, específicos, con solución, y **nunca solo por color** (rojo + ícono + texto).
6. Listas con objetivo → **paginación numerada**; feed de exploración → scroll infinito; punto medio → "Load more".
7. Tablas en móvil: prioriza columnas o stack en cards; scroll horizontal **dentro** de un contenedor, jamás la página entera.
8. Interrumpe con modal **solo** si es crítico/irreversible o requerido para continuar; en móvil prefiere **bottom sheet**; si cabe inline, hazlo inline.
9. Empty state = onboarding: comunica estado + enseña + da acción directa. Cero pantallas en blanco y cero "—" gigantes.
10. Elige indicador por duración: **<1 s nada, 1-10 s skeleton (o spinner por módulo), >10 s progress bar** con estimación.
11. Objetivo de latencia percibida: **< 400 ms** (Doherty); usa **optimistic UI** en acciones frecuentes reversibles, con rollback + toast si falla.
12. Reversible → **hacer + Undo** (snackbar). Irreversible/destructivo → confirmación que **nombra lo afectado**, no un "OK" genérico.
13. Toast = confirmación efímera de lo ya hecho; **nunca** para errores accionables ni info que deba conservarse.
14. Respeta los mínimos: **24×24 CSS px** (AA) / 44 pt iOS / 48 dp Android; contraste **4.5:1** texto, **3:1** grande y no-textual [ver: accesibilidad].
15. Espaciado por **escala de tokens** (base 4/8), no valores arbitrarios; jerarquía por peso/color, no solo tamaño.
16. Búsqueda importante → campo visible + search-as-you-type con debounce; filtros activos como chips removibles con contador.
17. Onboarding: preferir contextual (coach marks en el momento) sobre carruseles; permisos en contexto, no de golpe.
18. Cero **dark patterns** y cero **botones muertos**: diseña a favor del objetivo del usuario, no del negocio a costa suya.

---

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Placeholder usado como label (desaparece al escribir) | Label persistente arriba del campo; placeholder solo para ejemplo de formato |
| Validar en rojo un campo que el usuario aún no terminó de llenar | Validar al `blur`/on-submit; nunca marcar error en campo vacío no tocado |
| Meter la acción principal solo dentro del hamburger | Acción primaria siempre visible (tab bar / botón); hamburger solo para lo secundario |
| Scroll infinito en un catálogo donde la gente compara y usa Atrás | Paginación numerada; reserva el scroll infinito para feeds de exploración |
| Modal para newsletter/promo apenas abre la app | Interrumpir solo si sirve al usuario; usar banner/inline y pedir en contexto |
| Empty state en blanco o con un "—" gigante | Mensaje + acción directa; resuelve el valor sin dato con default/placeholder |
| Spinner infinito sin estimación en esperas largas | Skeleton (1-10 s) o progress bar con % y cancelar (>10 s) |
| Confirmación "¿Estás seguro? OK/Cancelar" para todo | Undo para lo reversible; confirmación que nombra lo afectado solo para lo irreversible |
| Toast para un error que requiere que el usuario haga algo | Error inline/banner persistente junto a la causa, con la solución |
| Tabla ancha con fuente encogida a ilegible en móvil | Priorizar columnas o stack en cards; nunca sacrificar legibilidad ni el target mínimo |
| Color como único indicador de error/estado | Añadir ícono + texto (deficiencia de visión de color afecta a muchos usuarios — no depender solo del canal de color) |
| Targets < 24 px pegados unos a otros | Respetar 24×24 CSS px (AA) / 44-48 y separación; aplicar Fitts (grandes y cerca del pulgar) |
| Copiar el layout Y el demo data de un mockup | El mockup da el layout; los datos van reales o placeholders honestos, nunca inventados |

---

## Fuentes

- **WCAG 2.2 — Understanding SC 2.5.8 Target Size (Minimum)** — W3C/WAI (w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) — número primario del target mínimo web: 24×24 CSS px, nivel AA, y sus 5 excepciones. Verificado.
- **WCAG 2.2 — Understanding SC 1.4.3 Contrast (Minimum)** — W3C/WAI (w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) — ratios 4.5:1 / 3:1 y definición de "texto grande" (18pt / 14pt bold). Verificado. Complementa SC 1.4.11 (3:1 no-textual) y 1.4.6 (7:1 AAA).
- **Nielsen Norman Group — Response Times: The 3 Important Limits** — Jakob Nielsen (nngroup.com) — los umbrales 0.1 s / 1 s / 10 s que rigen feedback y loading. Verificado.
- **Nielsen Norman Group — Error-Message Guidelines** — NN/g (nngroup.com) — cuándo y cómo mostrar errores: proximidad, redacción, no-solo-color, validación inline selectiva. Verificado.
- **Nielsen Norman Group — Infinite Scrolling** — NN/g (nngroup.com) — cuándo scroll infinito vs paginación vs load-more; problema del botón Atrás y del footer. Verificado.
- **Nielsen Norman Group — Modal & Nonmodal Dialogs** — NN/g (nngroup.com) — cuándo interrumpir con modal, costos y buenas prácticas. Verificado.
- **Nielsen Norman Group — Empty States** — NN/g (nngroup.com) — tipos de empty state y cómo convertirlos en onboarding contextual. Verificado.
- **Nielsen Norman Group — Mobile Navigation: Hidden vs. Visible** — NN/g (nngroup.com) — evidencia del debate hamburger vs tabs y el límite de ≤5 ítems. Verificado.
- **Nielsen Norman Group — Skeleton Screens** — NN/g (nngroup.com) — indicador por duración y percepción de espera más corta. Verificado.
- **Nielsen Norman Group — Breadcrumbs** — NN/g (nngroup.com) — reglas de uso, jerarquía vs historial, ítem actual no-link. Verificado.
- **Laws of UX** — Jon Yablonski (lawsofux.com) — Hick, Fitts, Jakob, Miller, Doherty (<400ms), Peak-End, Aesthetic-Usability, etc. Verificado.
- **Refactoring UI** — Adam Wathan & Steve Schoger (refactoringui.com) — tácticas: escala de espaciado, jerarquía por peso/color, "start with too much white space", limitar bordes. Verificado.
- **Material Design — Accessibility (touch targets)** — Google (m3.material.io / m2.material.io) — mínimo 48×48 dp con ≥8 dp de separación. Estándar documentado (la página live es SPA; número foundational conocido, no citado de fetch en vivo).
- **Human Interface Guidelines** — Apple (developer.apple.com/design/human-interface-guidelines) — hit area mínima 44×44 pt en iOS. Estándar documentado (página live es SPA; número foundational conocido).
- **Deceptive Design (dark patterns)** — Harry Brignull (deceptive.design) — taxonomía de dark patterns (confirmshaming, roach motel, sneaking, forced continuity, etc.). Referencia de la sección 12.
