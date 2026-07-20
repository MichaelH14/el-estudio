# Diseño de interacción y microinteracciones

> **Cuando cargar este archivo:** al diseñar, implementar o evaluar el comportamiento de cualquier elemento interactivo de una app/producto (web o móvil) — botones, toggles, inputs, tarjetas, modales, gestos — y su feedback: estados (hover/focus/pressed/disabled/loading), microinteracciones, transiciones y motion, timing, y cómo el usuario sabe qué es tocable y qué pasará al tocarlo. No es para HUD ni tutoriales de juego (eso vive en gamedev).

Este archivo cubre el ángulo **producto/app**. Los fundamentos de proceso UX (research, IA, flujos, usabilidad) están en [ver: fundamentos-ux]; el layout/color/tipografía en [ver: fundamentos-visuales]; los tokens y estados a nivel de sistema en [ver: sistemas-diseno]; los patrones concretos (formularios, navegación, tablas) en [ver: patrones-ui]; thumb zone y gestos en [ver: mobile-ux]; contraste/foco/ARIA en [ver: accesibilidad]. El feel de juego en tiempo real (screenshake, hit-stop, cámaras) vive en [ver: gamedev/game-feel] y el HUD/tutorial in-game en [ver: gamedev/ux-ui-onboarding]. Aquí: **la capa de interacción de una interfaz de producto**, sin repetir esos.

---

## 1. Affordances y significantes: que se sepa qué es interactuable

Distinción de Don Norman (*The Design of Everyday Things*, ed. revisada 2013):

| Concepto | Qué es | En pantalla |
|---|---|---|
| **Affordance** | La relación entre objeto y usuario: qué acciones son *posibles* | Un botón *puede* tocarse; un campo *puede* recibir texto. Existe aunque no se vea |
| **Significante (signifier)** | La **señal perceptible** que comunica dónde y cómo actuar | El borde, sombra, subrayado, cursor, color que dicen "esto es un botón" |

Regla operativa: en una GUI **casi todo es "posible" por software** — lo que importa es el *significante*. Si el usuario no ve la señal, la affordance no existe para él. Errores clásicos: texto que parece link pero no lo es (falso significante) y elementos clicables sin ninguna señal (affordance oculta).

**Significantes estándar que el usuario ya lee** (aprovechar convención — Jakob's Law, §11):
- Texto subrayado o en color de marca = link.
- Rectángulo con relleno/sombra/borde = botón. Relleno sólido = acción primaria; contorno o texto solo = secundaria/terciaria.
- Cursor `pointer` en desktop sobre todo lo clicable (nunca `pointer` sobre texto no interactivo — es un falso significante).
- Campo con borde hundido/box = input. Placeholder ≠ label (el placeholder desaparece; no es un significante persistente).
- Chevron `>` / flecha = "hay más", navega o expande. Switch = on/off inmediato; checkbox = selección que se confirma con otro botón.

Principios de percepción que hacen legible lo interactivo: **Ley de Prägnanz / cierre**, **proximidad** y **similitud** (Gestalt) agrupan controles relacionados; la **jerarquía visual** dice cuál es la acción primaria. Detalle visual en [ver: fundamentos-visuales].

---

## 2. Feedback inmediato: toda acción confirma

Regla #1 de la interacción: **ninguna acción deja al usuario adivinando**. Todo tap/click/submit produce un cambio perceptible en el frame siguiente. La referencia dura son los tres límites de tiempo de respuesta (Jakob Nielsen, NN/g, "Response Times: The 3 Important Limits", 1993 — siguen vigentes, son límites de la cognición humana, no de hardware):

| Umbral | Qué percibe el usuario | Feedback requerido |
|---|---|---|
| **0.1 s (100 ms)** | El sistema reacciona **instantáneamente** | Basta mostrar el resultado; no hace falta feedback extra. Estados hover/pressed y respuesta directa a input caen aquí |
| **1 s** | Nota el retraso pero **su flujo de pensamiento no se rompe** | No hace falta indicador especial entre 0.1–1 s, aunque conviene una señal de "trabajando" (botón a estado loading) |
| **10 s** | Límite para **mantener la atención** en la tarea | Mostrar un indicador de progreso; para >10 s, **percent-done + estimación + forma de cancelar**. El usuario hará otra cosa y necesitará reorientarse al volver |

Traducción a patrones de carga:

| Duración esperada | Patrón correcto |
|---|---|
| < 100 ms | Nada; resultado directo. Cambio de estado del control basta |
| 0.1–1 s | Cambio de estado inmediato (botón `pressed`→`loading`). Opcional spinner pequeño |
| 1–10 s | Indicador indeterminado (spinner) o **skeleton screen** para contenido; deshabilitar re-submit |
| > 10 s | Barra determinada con **porcentaje** + estimación + botón cancelar (NN/g) |

- **Skeleton screens** para carga de contenido (listas, feeds, perfiles): comunican estructura y se perciben más rápidos que un spinner centrado; el spinner es mejor para acciones puntuales cortas. Percepción > cronómetro.
- **Optimistic UI** para acciones de alta probabilidad de éxito (like, marcar leído, enviar mensaje): actualizar la UI **al instante** asumiendo éxito y reconciliar solo si falla. Esconde toda la latencia de red. Requiere un camino de rollback visible ante error.
- **Estados de error** son feedback: mensaje específico, cerca del elemento, en lenguaje humano, con la salida ("reintentar"). Un fallo silencioso es la peor interacción posible. [ver: patrones-ui] para copy de error.

---

## 3. Los seis estados de un elemento interactivo (diseñarlos TODOS)

Un control no es "un diseño": son **seis**. Diseñar solo el `default` es el bug de diseño más común. Cada estado es un significante de qué está pasando.

| Estado | Cuándo | Qué debe comunicar | Cómo se hace |
|---|---|---|---|
| **Default (enabled)** | Reposo, disponible | "Esto se puede usar" | El diseño base con su significante claro |
| **Hover** | Puntero encima (solo desktop/mouse) | "Vas a interactuar con esto" | Cambio sutil: elevación, brillo, subrayado. **No existe en touch** — nunca depender de hover para info crítica |
| **Focus** | Seleccionado por teclado/AT | "El teclado está aquí" | **Anillo de foco visible**, contraste ≥ 3:1 (WCAG 1.4.11). Usar `:focus-visible` para mostrarlo a teclado y no a mouse |
| **Active / Pressed** | Durante el tap/click | "Registré tu toque" | Feedback inmediato (<100 ms): hundir, oscurecer, escalar 0.96–0.98. En móvil sustituye al hover |
| **Disabled** | No disponible ahora | "No se puede, y por qué" | Baja opacidad/gris + `cursor: not-allowed`. Ojo: exento de contraste 4.5:1 pero por eso mismo puede ser inaccesible — ver nota |
| **Loading** | Acción en curso | "Trabajando, no re-envíes" | Spinner en el propio botón + deshabilitar; conservar el ancho para que no salte el layout |

Datos concretos de **state layers** de Material Design 3 (opacidad del overlay de estado sobre el color del componente — verificado en los tokens `md-sys-state`):

| Estado | Opacidad del state layer (M3) |
|---|---|
| Hover | **0.08** |
| Focus | **0.12** |
| Pressed | **0.12** |
| Dragged | **0.16** |

Notas críticas:
- **Focus visible es obligatorio** (WCAG 2.4.7, AA). Nunca `outline: none` sin reemplazo. El indicador debe tener contraste 3:1 contra el fondo adyacente (1.4.11). WCAG 2.2 añade 2.4.11 *Focus Not Obscured* (AA): el elemento con foco no puede quedar tapado por barras/stickies.
- **Disabled con cuidado**: un botón deshabilitado no es focusable, no anuncia por qué, y su bajo contraste lo hace ilegible. Alternativa frecuente (NN/g): mantener el botón **habilitado** y mostrar el error inline al intentar, en vez de un botón muerto que el usuario no entiende por qué no responde.
- **Hover no viaja al móvil**: cualquier información que solo aparece en hover (tooltips, acciones ocultas) es invisible en touch. Dar equivalente permanente o por tap. [ver: mobile-ux]
- El **loading en el botón** evita el doble-submit y ancla el feedback donde el usuario miró. Bloquear el control mientras dura.

---

## 4. Touch targets y Ley de Fitts

**Ley de Fitts:** el tiempo para alcanzar un objetivo depende de su **distancia** y su **tamaño** — objetivos grandes y cercanos se aciertan más rápido y con menos error. Implicaciones: acciones frecuentes = grandes y a mano; destructivas = separadas de las frecuentes; los **bordes y esquinas** de la pantalla son "infinitamente grandes" (el puntero se topa), ideales para dianas.

Tamaños mínimos de target — cada número con su fuente primaria:

| Fuente | Mínimo | Nivel / contexto |
|---|---|---|
| **WCAG 2.2 SC 2.5.8** Target Size (Minimum) | **24 × 24 CSS px** | AA (con excepciones: spacing, inline, equivalente, control del user-agent, esencial) |
| **WCAG 2.1 SC 2.5.5** Target Size (Enhanced) | **44 × 44 CSS px** | AAA |
| **Apple HIG** | **44 × 44 pt** | Recomendación de plataforma iOS para todo control tocable |
| **Material Design (Android)** | **48 × 48 dp** | con **8 dp** de separación entre targets |

Práctica: diseñar a **44–48 px/pt/dp** como piso real (cumple AAA y ambas plataformas); 24 px es el mínimo legal AA, no una meta. El *área táctil* puede ser mayor que el pixel visible (padding/hitbox invisible) — un icono de 24 px con hitbox de 48 comparte lo mejor de ambos. Zona del pulgar y colocación en [ver: mobile-ux].

---

## 5. Anatomía de una microinteracción

Una **microinteracción** es un momento de uso contenido alrededor de una sola tarea: dar like, activar un switch, un pull-to-refresh, escribir la contraseña, silenciar. Modelo de Dan Saffer (*Microinteractions*, O'Reilly 2013) — cuatro partes:

| Parte | Qué es | Ejemplo (toggle de "modo silencio") |
|---|---|---|
| **1. Trigger** | Lo que la inicia: acción del usuario (tap) o del sistema (evento) | El usuario toca el switch |
| **2. Rules** | Qué puede pasar y en qué orden; el modelo de lo permitido | Cambia a on/off; guarda; no permite estado intermedio |
| **3. Feedback** | Lo que el usuario percibe de las reglas: lo hace *entendible* | El pomo se desliza con física, cambia el color, un tick, quizá un háptico |
| **4. Loops & Modes** | Qué pasa con el tiempo/repetición; cambios de estado a largo plazo | Recuerda la preferencia; el badge del icono refleja el modo |

Principios:
- **El feedback es donde vive el deleite** — pero el feedback existe para *comunicar la regla*, no para adornar. Un like que "salta" confirma que se registró; si además deleita, mejor, pero primero informa.
- **Menos, no más**: una microinteracción hace *una* cosa bien. No meter cinco animaciones en un toggle.
- La regla de dosificación se comparte con el juice de juegos (añadir de más y recortar), pero en producto el techo es mucho más bajo — ver §9 y [ver: gamedev/game-feel §2].

Ejemplos canónicos de microinteracción bien resuelta: el pull-to-refresh (Loren Brichter), el "typing…" de los chats, el switch con física de iOS, la barra de fuerza de contraseña, el corazón que late al dar like.

---

## 6. Transiciones y motion: para qué sirve el movimiento

El motion no es decoración: tiene **cuatro trabajos funcionales**. Si una animación no hace ninguno, sobra.

| Trabajo del motion | Qué logra | Ejemplo |
|---|---|---|
| **Guiar la atención** | Dirigir el ojo al cambio importante | Un ítem nuevo entra deslizándose; el error hace un shake corto |
| **Continuidad espacial** | Mantener el modelo mental de "dónde está" | Un panel que sale del botón que lo abrió; shared-element transition |
| **Relación causa-efecto** | Mostrar que A produjo B | Al borrar, la fila colapsa y las de abajo suben; el usuario ve el porqué |
| **Ocultar latencia** | Que la espera se sienta corta | Transición de 200–300 ms que cubre la carga; skeleton que "respira" |

### Duración y easing — tokens verificados de Material Design 3

Nada útil se mueve linealmente (salvo spinners y progreso). Curvas y tiempos de M3 (verificados en `md-sys-motion`):

**Easing (curvas):**

| Token M3 | cubic-bezier | Cuándo |
|---|---|---|
| **Emphasized** | `cubic-bezier(0.2, 0, 0, 1)` | Curva por defecto para transiciones que empiezan y acaban en pantalla; expresiva |
| **Emphasized decelerate** | `cubic-bezier(0.05, 0.7, 0.1, 1)` | Elementos que **entran** (aparecen): arrancan rápido y frenan suave (ease-out) |
| **Emphasized accelerate** | `cubic-bezier(0.3, 0, 0.8, 0.15)` | Elementos que **salen** (desaparecen): aceleran hacia afuera (ease-in) |
| **Standard** | `cubic-bezier(0.2, 0, 0, 1)` | Transiciones pequeñas/utilitarias |
| **Legacy (M2 "standard")** | `cubic-bezier(0.4, 0, 0.2, 1)` | La clásica ease-in-out de Material 2; sigue siendo un default seguro |

Regla de oro (compartida con animación de juego): **entrar = ease-out** (rápido→lento, se siente responsivo), **salir = ease-in** (acelera y se va), **movimientos autónomos = ease-in-out**. Lo que responde a input del usuario nunca lleva ease-in al arranque: se percibe como lag. [ver: gamedev/game-feel §5]

**Duración (tokens M3, ms):**

| Familia | Valores (ms) | Uso típico |
|---|---|---|
| **Short** | 50 / 100 / 150 / 200 | Micro-feedback: hover, selección, ripple, toggles |
| **Medium** | 250 / 300 / 350 / 400 | Transiciones de componente: expandir, entrar/salir de tarjeta, modales |
| **Long** | 450 / 500 / 550 / 600 | Cambios grandes de pantalla, elementos que recorren mucho |
| **Extra-long** | 700 / 800 / 900 / 1000 | Movimientos amplios/expresivos; usar con moderación |

### Timing: los rangos que la investigación respalda

| Situación | Duración objetivo | Fuente |
|---|---|---|
| Percepción de "instantáneo" | **≤ 100 ms** | NN/g, 3 límites |
| Feedback simple (checkbox, toggle) | **~100 ms** ("se siente inmediato") | NN/g, Animation Duration |
| Transición de componente (modal, panel) | **200–300 ms** | NN/g |
| Rango sano de casi toda animación UI | **100–400 ms** (400 ms ya se percibe "muy lento") | NN/g |
| Umbral de "arrastre/pesadez" | **desde 500 ms** se siente un lastre real | NN/g |
| Pace de interacción sin espera mutua | **< 400 ms** (Doherty Threshold) | Laws of UX |

Matices: **entrar dura un poco más que salir** (p. ej. modal 300 ms al aparecer, 200–250 ms al cerrar) — quitar algo debe sentirse rápido. Distancias mayores = duración un poco mayor, pero nunca proporcional lineal (una animación de pantalla completa no dura 2 s). Todo tween debe ser **interrumpible**: si el usuario re-acciona antes de terminar, encadenar desde el valor actual, no reiniciar desde el "ideal".

---

## 7. Motion que informa vs. motion que distrae

| Informa (mantener) | Distrae/cansa (recortar) |
|---|---|
| Confirma una acción del usuario | Anima algo que el usuario no disparó ni necesita mirar |
| Da continuidad entre dos estados | Rebota/gira "porque queda bonito" |
| Es corta (≤ 400 ms) e interrumpible | Bloquea la interacción hasta terminar |
| Ocurre una vez por acción | Se repite en bucle en el periférico de la vista |
| Respeta `prefers-reduced-motion` | Ignora la preferencia del sistema |

- **`prefers-reduced-motion`** (media query CSS) y WCAG 2.3.3 *Animation from Interactions* (AAA): dar una alternativa reducida (fundir en vez de deslizar, o cortar). Obligatorio para usuarios con trastorno vestibular; parpadeos > 3/s son riesgo de fotosensibilidad (WCAG 2.3.1, A). [ver: accesibilidad]
- **Costo de repetición**: una animación deliciosa la primera vez es fricción la número 50. Cuanto más frecuente la acción, **más corta y sobria** su animación. El motion expresivo se reserva para momentos de baja frecuencia (onboarding, éxito, primer uso).
- Los **12 principios de Disney** aplican a UI (anticipación, squash&stretch suave, ease, follow-through) pero atenuados: en producto se usa un subconjunto discreto, no la exageración de un cartoon. El repertorio completo y su versión de juego en [ver: gamedev/animacion] / [ver: gamedev/game-feel].

---

## 8. Las Laws of UX aplicadas a interacción

Fuente: Jon Yablonski, *Laws of UX* (lawsofux.com / libro O'Reilly). Las que más pesan en la capa de interacción:

| Ley | Enunciado | Aplicación a interacción |
|---|---|---|
| **Fitts's Law** | Tiempo de alcance = f(distancia, tamaño del target) | Targets grandes (§4); primario grande y a mano; destructivo lejos; usar bordes/esquinas |
| **Hick's Law** | El tiempo de decisión crece con el número y complejidad de opciones | Menos botones por pantalla; progressive disclosure; una acción primaria clara por vista |
| **Jakob's Law** | El usuario espera que tu app funcione como las demás que ya usa | Usar patrones e íconos convencionales; no reinventar el switch, el back, el submit |
| **Doherty Threshold** | La productividad se dispara cuando la respuesta es **< 400 ms** | Responder bajo 400 ms; si no se puede, feedback que llene el hueco (skeleton, optimistic) |
| **Peak-End Rule** | La experiencia se juzga por su **momento pico** y su **final** | Invertir el deleite en el clímax (éxito, envío completado) y en el cierre, no repartido plano |
| **Aesthetic-Usability Effect** | Lo estéticamente agradable se **percibe** como más usable (y perdona fallos menores) | El polish de estados/motion no es cosmético: sube la usabilidad percibida y la tolerancia |
| **Miller's Law** | ~7 ± 2 ítems en memoria de trabajo | Agrupar (chunking); no pedir recordar entre pasos; mostrar, no memorizar |
| **Zeigarnik Effect** | Se recuerdan mejor las tareas **incompletas** | Barras de progreso y checklists de onboarding motivan a completar |
| **Von Restorff (aislamiento)** | El elemento distinto se recuerda/nota más | Un solo CTA destacado por vista; no compitan dos "primarios" |
| **Tesler's Law** | Toda complejidad irreducible se **transfiere** a alguien | Absorber la complejidad en el sistema, no volcarla en el usuario (smart defaults) |

Peak-End + Aesthetic-Usability son el mandato de negocio de este archivo: **el detalle de interacción cambia cómo se recuerda y se valora todo el producto**, no solo ese botón.

---

## 9. Delight sin ruido: cuándo aporta y cuándo estorba

| Aporta (invertir aquí) | Estorba (evitar) |
|---|---|
| Momentos de **baja frecuencia y alto significado**: éxito, primer logro, envío completado, estado vacío | Acciones repetidas 50×/sesión (scroll, tabs, teclear) |
| Confirma algo que el usuario **necesitaba saber** | Animación que retrasa una tarea urgente |
| Refuerza la **marca/personalidad** en un punto que ya funciona | "Personalidad" que tapa un flujo roto — la fundación va primero |
| Es **opcional y no bloqueante** | Bloquea input hasta que la animación termina |
| Sorprende una vez, luego se vuelve sutil | Efecto que no cambia y se nota cada vez (fatiga) |

Heurística: **primero funcional, después deleite**. El deleite sobre una interacción rota es maquillaje. Y el deleite tiene rendimientos decrecientes con la frecuencia — por eso Peak-End: concentrarlo en el pico y el final.

---

## 10. El puente con game feel: qué comparte y qué difiere

Comparten raíz (respuesta < 100 ms, tweening no lineal, feedback multisensorial, "output por input") pero el techo y las metas divergen. Detalle del lado juego en [ver: gamedev/game-feel]; en Unity [ver: unity/ui-unity]; pipeline de UI de juego en [ver: pipeline/ui-flujo-completo].

| Dimensión | App / producto (este archivo) | Juego (game feel) |
|---|---|---|
| **Meta** | Eficiencia, claridad, confianza | Sensación, diversión, expresividad |
| **Respuesta a input** | < 100 ms percibido instantáneo | < 100 ms del correction cycle (idéntico piso) |
| **Cantidad de juice** | Sobrio; el motion informa | Abundante; el juice deleita y "vende" el impacto |
| **Screenshake / hit-stop** | Casi nunca (marea, no informa) | Núcleo del feel de acción |
| **Repetición** | Miles de veces → mínimo | Miles de veces → calibrado pero generoso |
| **Duración típica** | 100–400 ms | 100–300 ms de feedback, frames de hit-stop |
| **Accesibilidad** | `prefers-reduced-motion` obligatorio | Opciones de reduce-motion/flash igualmente exigidas |
| **Interrumpibilidad** | Sí (el usuario manda) | Sí (encadenar tweens) |

Regla de trasvase: **se puede robar del gamedev la técnica (easing, anticipación, follow-through, feedback inmediato) pero no la dosis**. Una app con juice de plataformero cansa; un juego con la sobriedad de un dashboard se siente muerto.

---

## Reglas prácticas

1. **Diseña los 6 estados** de cada control (default, hover, focus, active, disabled, loading) — no solo el default.
2. **Nada sin feedback**: todo tap/click/submit cambia algo perceptible en < 100 ms. Output vacío = bug.
3. **Focus visible siempre** (`:focus-visible`), contraste ≥ 3:1; nunca `outline:none` sin reemplazo.
4. **Targets ≥ 44–48 px/pt/dp** (24 px es el mínimo AA, no la meta); hitbox puede exceder el pixel visible.
5. **Motion con un trabajo**: guiar atención, dar continuidad, mostrar causa o cubrir latencia. Si no hace ninguno, quítalo.
6. **Timing**: micro-feedback ~100 ms, transiciones 200–300 ms, techo sano ~400 ms (500 ms ya se siente un lastre); entrar un poco más que salir.
7. **Entrar = ease-out, salir = ease-in**; respuesta a input jamás ease-in (se siente lag).
8. **Responde < 400 ms** (Doherty); si no puedes, llena el hueco con skeleton u optimistic UI.
9. **Carga**: < 1 s nada especial; 1–10 s indicador; > 10 s barra con % + estimación + cancelar.
10. **Optimistic UI** para acciones de éxito casi seguro; con camino de rollback visible ante error.
11. **Respeta `prefers-reduced-motion`**; nada parpadea > 3 veces/segundo.
12. **Deleite en el pico y el final** (Peak-End); sobrio en lo repetitivo (fatiga).
13. **Convención antes que invención** (Jakob): switch, back, submit e íconos estándar como los espera el usuario.
14. **Una acción primaria por vista** (Von Restorff + Hick); no dos "primarios" compitiendo.
15. **Nada crítico solo en hover** — no existe en touch; da equivalente permanente o por tap.
16. **Botones nunca muertos**: si un disabled confunde, mantén habilitado + error inline al intentar.
17. **Tweens interrumpibles**: re-acción antes de terminar encadena desde el valor actual, no reinicia.
18. **Conserva el layout** en loading (mismo ancho del botón) — que el motion no provoque saltos (CLS).

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Solo se diseñó el estado default | Especificar hover/focus/active/disabled/loading en el design system [ver: sistemas-diseno] |
| `outline: none` para "limpiar" el foco | Usar `:focus-visible` con anillo de contraste ≥ 3:1; el teclado lo necesita |
| Depender del hover para acciones o info | Equivalente permanente/por tap; en touch el hover no existe |
| Botón deshabilitado sin decir por qué | Error inline al intentar, o habilitado con validación visible |
| Acción sin feedback (el usuario re-clica) | Estado loading en el propio botón + bloquear re-submit |
| Spinner infinito para cargas > 10 s | Barra determinada con % + estimación + cancelar (NN/g) |
| Animación de 800 ms en algo que se hace 50×/sesión | Bajar a ≤ 150 ms o quitar; el deleite frecuente se vuelve fricción |
| Ease-in (o linear) en respuesta a input | Ease-out: rápido→lento, se percibe responsivo |
| Motion decorativo que bloquea la tarea | Motion no bloqueante; la interacción sigue disponible durante la animación |
| Ignorar `prefers-reduced-motion` | Alternativa reducida (fundido/corte); riesgo vestibular real |
| Targets de 24–30 px pegados entre sí | 44–48 px con 8 dp de separación (Fitts + WCAG) |
| Placeholder usado como label | Label persistente; el placeholder desaparece al escribir (no es significante) |
| Dos "acciones primarias" en la misma vista | Una destacada (Von Restorff); el resto secundario/terciario |
| Copiar el juice de un juego en una app | Robar la técnica, no la dosis; producto = sobrio |

## Fuentes

- **Response Times: The 3 Important Limits** — Jakob Nielsen, Nielsen Norman Group — los umbrales 0.1 s / 1 s / 10 s y qué feedback dar en cada uno; base de todo el timing de feedback. Verificado en nngroup.com.
- **Executing UX Animations: Duration and Motion Characteristics** — Nielsen Norman Group (Page Laubheimer, 2020) — rango sano 100–400 ms, ~100 ms para feedback simple, 200–300 ms para cambios de pantalla, 500 ms = "arrastre"; entrar > salir. Verificado en nngroup.com/articles/animation-duration.
- **Motion — Easing and duration tokens** — Material Design 3 (m3.material.io) — tokens de duración (short 50–200, medium 250–400, long 450–600, extra-long 700–1000 ms) y easing (emphasized `(0.2,0,0,1)`, decel `(0.05,0.7,0.1,1)`, accel `(0.3,0,0.8,0.15)`, legacy `(0.4,0,0.2,1)`) + state-layer opacities (hover 0.08, focus/pressed 0.12, dragged 0.16). Verificado en el source `md-sys-motion` / `md-sys-state` de material-web.
- **WCAG 2.2 — SC 2.5.8 Target Size (Minimum)** — W3C/WAI — mínimo **24 × 24 CSS px** (AA) con 5 excepciones; SC 2.5.5 Enhanced = 44 px (AAA). Verificado en w3.org/WAI.
- **WCAG 2.2 — SC 1.4.3 Contrast (Minimum) y 1.4.11 Non-Text Contrast** — W3C/WAI — texto normal **4.5:1**, texto grande (≥18 pt / 14 pt bold ≈ 24 px/18.5 px) **3:1**, componentes de UI y foco **3:1**. Verificado.
- **Apple Human Interface Guidelines** — Apple — target táctil mínimo **44 × 44 pt**; complementa a Material (**48 × 48 dp**, 8 dp de separación). Número canónico de plataforma.
- **Laws of UX** — Jon Yablonski (lawsofux.com / O'Reilly) — Fitts, Hick, Jakob, Doherty (**< 400 ms**), Peak-End, Aesthetic-Usability, Miller (7±2), Von Restorff, Zeigarnik, Tesler. Marco de las leyes aplicadas. Verificado.
- **Microinteractions: Designing with Details** — Dan Saffer (O'Reilly, 2013) — anatomía trigger → rules → feedback → loops & modes. Definición canónica de microinteracción.
- **The Design of Everyday Things** (ed. rev. 2013) — Don Norman — distinción affordance vs significante; base de "qué se ve como interactuable".
- **Refactoring UI** — Adam Wathan & Steve Schoger — diseño práctico de estados, profundidad/elevación y jerarquía de acciones (primario/secundario); complemento aplicado a los estados de §3.
