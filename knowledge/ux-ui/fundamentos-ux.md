# Fundamentos de UX

> **Cuando cargar este archivo:** al arrancar el diseño o la evaluación de UX de una app o producto real (web/móvil, no juego) — antes de dibujar el primer flujo, definir para quién es, organizar la navegación, o hacer una auditoría de usabilidad. Es el archivo de proceso y método; el detalle visual vive en [ver: fundamentos-visuales], el de accesibilidad en [ver: accesibilidad], el móvil en [ver: mobile-ux]. Para el equivalente en juegos (HUD, tutoriales in-game, FTUE): [ver: gamedev/ux-ui-onboarding].

Este archivo es UX/UI **de producto/app**. Lo que ya vive en otro lado y NO se repite aquí:
- HUD, tutoriales in-game, FTUE, feedback de loading/save de juego → [ver: gamedev/ux-ui-onboarding]
- Game-feel, juice, feedback de input → [ver: gamedev/game-feel]
- Detalle de contraste, tipografía, espaciado, color → [ver: fundamentos-visuales]
- WCAG completo, lectores de pantalla, daltonismo → [ver: accesibilidad]
- Thumb zone, safe areas, gestos → [ver: mobile-ux]
- Componentes y patrones concretos (formularios, tablas, modales) → [ver: patrones-ui]
- Microinteracciones, estados, transiciones → [ver: interaccion-microux]

---

## 1. UX vs UI: no son lo mismo

| | **UX (User Experience)** | **UI (User Interface)** |
|---|---|---|
| Qué es | La experiencia completa: si el producto es útil, usable, encontrable, valioso | La capa visible/táctil: pantallas, controles, color, tipografía, layout |
| Pregunta que responde | ¿Resuelve el trabajo del usuario? ¿Con cuánto esfuerzo? | ¿Se ve claro y se opera bien? |
| Vive en | Flujos, arquitectura de información, investigación, jerarquía de tareas | Pantallas, componentes, design tokens |
| Analogía | El plano y la circulación de la casa | Los acabados, muebles y letreros |

**Usefulness = Utility + Usability** (NN/g). Un producto útil pero difícil de usar fracasa; uno usable pero sin las features que el usuario necesita también. UX = las dos. La UI puede ser bella y aun así ser mala UX si el flujo obliga a 6 pasos donde bastaban 2.

### El proceso (investigar → definir → diseñar → probar → iterar)

Doble diamante condensado. No es lineal: se cicla.

| Fase | Objetivo | Salida concreta |
|---|---|---|
| **1. Investigar** | Entender al usuario y el problema real, no el que asumes | Notas de entrevista/observación, hallazgos |
| **2. Definir** | Acotar para quién y qué trabajo se resuelve | Persona(s), job statement, problem statement |
| **3. Diseñar** | Mapear el camino y las pantallas | User flow, arquitectura de info, wireframes |
| **4. Probar** | Ponerlo frente a usuarios reales antes de invertir en pulido | Test de usabilidad, hallazgos priorizados |
| **5. Iterar** | Arreglar lo que rompió, volver a probar | Siguiente versión + evidencia |

Regla operativa para un dev solo: **el prototipo más barato que valide la hipótesis**. Un boceto en papel o un flujo en texto vale para test si aún no hay UI. Probar temprano y feo > probar tarde y bonito.

---

## 2. Investigación de usuario para un dev solo

No hace falta un laboratorio. Lo que sí hace falta: **hablar y observar antes de asumir**.

| Método | Cuándo | Cómo (versión mínima) |
|---|---|---|
| **Entrevista** | Al inicio, para entender contexto y motivación | 5-8 personas del público objetivo; preguntas abiertas sobre lo que hacen HOY, no sobre lo que "querrían". Preguntar por la última vez que hicieron la tarea |
| **Observación** | Para ver el comportamiento real (lo que dicen ≠ lo que hacen) | Ver a alguien hacer la tarea sin ayudarlo; anotar dónde duda, dónde se traba |
| **Test de usabilidad** | Sobre un prototipo o el producto | Dar una tarea, callarse, observar. "Piensa en voz alta". 5 usuarios detectan ~85% de los problemas de usabilidad (Nielsen) |
| **Encuesta** | Para cuantificar algo que ya viste cualitativamente | Complemento, no sustituto de hablar |
| **Analytics** | Producto ya vivo | Dónde caen los usuarios (funnel), qué no usan |

### Cuándo basta con heurísticas (sin usuarios)

No siempre hay acceso a usuarios. Una **evaluación heurística** (revisar la interfaz contra las 10 heurísticas de Nielsen, sección 6) es la red de seguridad barata:
- Sirve para atrapar los problemas obvios ANTES de gastar un test con usuarios reales.
- No reemplaza el test: las heurísticas encuentran violaciones de principio, no descubren qué le importa al usuario ni qué trabajo intenta hacer.
- Regla: heurísticas para **evaluar** una solución; investigación con personas para **decidir qué construir**. Si el producto es convención pura (un login, un checkout estándar), las heurísticas + patrones establecidos [ver: patrones-ui] cubren casi todo. Si es algo nuevo o un dominio que no conoces, no te saltes hablar con usuarios.

Sesgo a vigilar: tú no eres el usuario. El "false-consensus" hace que asumas que los demás piensan como tú. Por eso se observa, no se adivina.

---

## 3. Personas y Jobs-to-be-done: para quién y qué trabajo

### Persona (NN/g)

Descripción ficticia pero realista de un usuario objetivo típico, destilada de investigación real. Responde **QUIÉN**.
- Contiene solo lo que **afecta decisiones de diseño**: contexto de uso, comportamiento, objetivos, nivel de experiencia, una cita representativa. Datos demográficos solo si cambian el diseño.
- Pocas, con profundidad > muchas superficiales. Una persona principal + 1-2 secundarias suele bastar para un producto pequeño.
- Debe salir de field studies / entrevistas / encuestas, **no inventada en una reunión**. Una persona inventada es peor que ninguna: da falsa confianza.

### Jobs-to-be-done (NN/g)

Cuando un usuario "contrata" (usa) un producto, lo hace para un **trabajo** (lograr un resultado). Responde **QUÉ resultado busca**, en qué contexto.
- Estructura del job statement: qué necesita lograr + contexto (cuándo/dónde/por qué) + criterio de éxito **funcional** + criterio de éxito **emocional/social**.
- Ejemplo (NN/g): *"viajar a otra ciudad para una conferencia"* — distinto de viajar de vacaciones, con requisitos distintos aunque el "producto" (avión, hotel) sea el mismo.
- **Personas y JTBD son compatibles, no rivales**: la persona da el quién y la empatía; el JTBD da el resultado buscado y evita diseñar features que a nadie le sirven. Una persona bien hecha ya incluye los jobs.

Uso práctico: antes de añadir una feature, escribe el job que resuelve. Si no puedes escribirlo, probablemente la feature sobra.

---

## 4. User flows y task flows: mapear el camino, reducir pasos

**User flow** (NN/g): el conjunto de interacciones típicas/ideales para completar una tarea con el producto. Escala micro (minutos-horas), dentro de un solo producto. Distinto del **user journey** (macro, días-semanas, multicanal, con emociones) — el journey es el mapa grande; el flow es el zoom a una tarea.

| Concepto | Qué mapea | Cuándo usarlo |
|---|---|---|
| **User journey map** | Toda la experiencia a través de canales y tiempo, con emociones | Estrategia, ver dónde duele el proceso completo |
| **User flow** | Los pasos + decisiones + respuestas del sistema para una tarea | Diseñar/optimizar una tarea concreta (registro, compra) |
| **Task flow** | La secuencia lineal ideal de una sola tarea, sin ramas de decisión | El camino feliz de una acción específica |
| **Wireflow** | Flow + wireframes de cada pantalla | Cuando ya vas a la UI |

Cómo mapear un flow (barato): caja por pantalla/estado, flecha por acción, rombo por decisión. Marca el **punto de entrada** (¿de dónde viene el usuario? notificación, link, home) y el **objetivo**.

**Reducir pasos** — el corazón del flow:
- Cuenta los pasos del camino feliz. Cada paso es una oportunidad de abandono.
- Elimina pasos que no aportan decisión (pantallas "de confirmación" vacías, campos que puedes inferir).
- Usa defaults inteligentes y datos precargados en vez de pedir input [ver: interaccion-microux].
- El paso más caro es el que fuerza a recordar algo de otra pantalla (viola "recognition over recall", heurística 6).

---

## 5. Arquitectura de información (IA)

**IA** (NN/g): (1) identificar y definir el contenido/funciones, y (2) la organización, estructura y nomenclatura que definen las relaciones entre ellos. La IA es el **esqueleto invisible**; la navegación es la punta del iceberg visible que se apoya en ella. *IA informa la UI, pero no ES la UI* — vive en hojas de cálculo y diagramas, no en wireframes.

**Definir la IA ANTES de la navegación** — rediseñar la navegación por estética es barato; rediseñarla porque la estructura estaba mal es caro.

### Componentes

| Componente | Qué es | Ejemplo app |
|---|---|---|
| **Content inventory / audit** | Lista de todo lo que hay (y si sirve) | Todas las pantallas y funciones actuales |
| **Organization scheme** | Cómo se agrupa (por tema, tarea, audiencia, orden) | Menú por tarea vs por tipo de contenido |
| **Taxonomía / labeling** | Nombres estandarizados de categorías | "Ajustes" no "Config"/"Preferencias" mezclados [ver: patrones-ui] |
| **Navegación** | Global, local, utility, breadcrumbs, filtros, footer | El mecanismo visible para moverse |
| **Búsqueda** | Cuando el volumen supera lo navegable | Catálogos grandes |

### Métodos para construir y validar la IA

| Método | Para qué | Números (NN/g) |
|---|---|---|
| **Card sorting abierto** | Descubrir cómo agrupa la gente el contenido (crean sus propias categorías) | ~15 participantes para insight cualitativo; 30-50 para cuantitativo |
| **Card sorting cerrado** | Validar categorías que ya definiste (encajan cartas en tus grupos) | Ídem; a veces tree testing es mejor para validar |
| **Tree testing** | Probar si la gente ENCUENTRA cosas en tu estructura, sin pistas visuales | Valida la jerarquía real |

Regla: card sorting abierto para **generar** la estructura, tree testing para **validarla**. Las etiquetas deben usar el lenguaje del usuario (heurística 2: match con el mundo real), no jerga interna.

---

## 6. Las 10 heurísticas de usabilidad de Nielsen (NN/g)

El estándar de facto para evaluar cualquier interfaz. Una a una, con ejemplo de app:

| # | Heurística | Qué exige | Ejemplo de app (bien) |
|---|---|---|---|
| 1 | **Visibility of system status** | Mantener al usuario informado de qué pasa, con feedback en tiempo razonable | Spinner al enviar, "Guardado", barra de progreso de upload, badge de no-leídos |
| 2 | **Match between system and real world** | Hablar el lenguaje del usuario, convenciones reales, no jerga del sistema | "Carrito", "Papelera" en vez de "Objeto eliminado del árbol de nodos"; iconos reconocibles |
| 3 | **User control and freedom** | Salidas claras: deshacer, cancelar, volver — "salidas de emergencia" | Undo tras borrar, "Cancelar" en cada modal, back que no pierde datos |
| 4 | **Consistency and standards** | El mismo término/acción significa lo mismo en todo; seguir convenciones de plataforma | Un solo estilo de botón primario; "Guardar" siempre en el mismo sitio; respetar iOS/Android [ver: sistemas-diseno] |
| 5 | **Error prevention** | Prevenir el error antes que un buen mensaje: eliminar condiciones de error o confirmar acciones de peso | Validación en vivo del formulario, deshabilitar "Enviar" hasta que sea válido, confirmar "Eliminar cuenta" |
| 6 | **Recognition rather than recall** | Minimizar carga de memoria: mostrar opciones, no obligar a recordar | Autocompletar, mostrar el email en pantalla de confirmación, recientes/sugeridos [ver: sección 8, Miller] |
| 7 | **Flexibility and efficiency of use** | Atajos para expertos sin estorbar a novatos | Keyboard shortcuts, gestos, acciones en lote, "favoritos" — invisibles hasta que se buscan |
| 8 | **Aesthetic and minimalist design** | Nada irrelevante o rara vez necesario; cada elemento compite por atención | Una CTA primaria por pantalla, quitar texto de relleno, progressive disclosure (sección 8) |
| 9 | **Help users recognize, diagnose, recover from errors** | Mensajes en lenguaje claro: qué pasó + cómo salir. Nunca un código pelado | "Tarjeta rechazada, prueba otra" con botón, no "Error 402" |
| 10 | **Help and documentation** | Ayuda buscable, orientada a tarea, en contexto cuando se necesita | Tooltips, "?" contextual, docs con buscador — visible pero no invasivo |

Cómo usarlas: recorre cada pantalla y marca qué heurística viola cada problema. Prioriza por severidad (frecuencia × impacto × persistencia). Una evaluación heurística la puede hacer una persona; con 3-5 evaluadores se cubre más.

---

## 7. Usabilidad y cómo se mide (NN/g)

**Usabilidad**: atributo de calidad que mide qué tan fácil es usar una interfaz. Cinco componentes (Nielsen):

| Componente | Pregunta | Cómo se mide |
|---|---|---|
| **Learnability** | ¿Cuán fácil es lograr tareas básicas la PRIMERA vez? | Task success de usuarios nuevos, time-on-task inicial |
| **Efficiency** | Una vez aprendido, ¿cuán rápido se hacen las tareas? | Time-on-task de usuarios expertos, nº de clics/pasos |
| **Memorability** | Al volver tras un tiempo, ¿se recupera la destreza fácil? | Task success tras periodo de no-uso |
| **Errors** | ¿Cuántos errores, cuán graves, cuán fácil recuperarse? | Error rate, tasa de recuperación |
| **Satisfaction** | ¿Cuán agradable es de usar? | Encuesta (ej. SUS) |

### Métricas concretas

| Métrica | Qué captura | Nota |
|---|---|---|
| **Task success rate** | % de usuarios que completan la tarea | La métrica más directa de usabilidad |
| **Time-on-task** | Cuánto tardan | Baja con la eficiencia; sube con confusión |
| **Error rate** | Errores por tarea | + severidad y recuperabilidad |
| **SUS (System Usability Scale)** | Satisfacción, 10 ítems, escala 0-100 | Promedio de la industria ≈ **68** = "OK"; por encima es bueno (literatura SUS, Sauro/MeasuringU) |

Regla del test barato (Nielsen): **5 usuarios encuentran ~85% de los problemas** de usabilidad. Más vale 3 tests de 5 usuarios iterando que 1 test de 15. Utilidad ≠ usabilidad: mide también si el producto sirve para el trabajo (sección 3), no solo si es fácil.

---

## 8. Carga cognitiva: bajar el esfuerzo mental

**Carga cognitiva** (NN/g): la cantidad de recursos mentales que exige operar el sistema.
- **Intrínseca**: el esfuerzo inevitable de la tarea y de absorber info nueva. No se puede eliminar, solo dosificar.
- **Extraña (extraneous)**: procesamiento que NO ayuda a entender — clutter, estilos sin significado, inconsistencias. **Este se minimiza.**

Tres palancas (NN/g):
1. **Eliminar clutter visual**: quitar links redundantes, imágenes irrelevantes, tipografía decorativa sin función.
2. **Apoyarse en modelos mentales existentes**: etiquetas y layouts familiares (heurística 2 y 4) bajan la curva.
3. **Descargar (offload) al sistema**: reemplazar leer/recordar/decidir con defaults, datos precargados, ayudas visuales. Ejemplo: mostrar la opción recomendada preseleccionada.

### Leyes que aplican (Laws of UX)

| Ley | Enunciado | Aplicación en app |
|---|---|---|
| **Ley de Hick** | El tiempo de decisión crece con el número y complejidad de opciones (Hick & Hyman, 1952) | Menos opciones cuando importa la velocidad; partir procesos complejos en pasos; destacar la opción recomendada; onboarding gradual |
| **Ley de Miller** | La persona promedio retiene ~7 (±2) ítems en memoria de trabajo | **Caveat oficial**: no usarla para imponer límites rígidos ("máximo 7 ítems de menú"). Su valor real es **chunking**: agrupar la info para procesarla mejor |
| **Progressive disclosure** (NN/g) | Diferir features avanzadas/raras a una pantalla secundaria | Mejora learnability, efficiency y reduce errores. Mostrar arriba TODO lo frecuente; lo raro, a un paso claro y etiquetado |

Progressive disclosure bien hecho: el usuario solo baja al nivel secundario en ocasiones raras, y la vía para hacerlo es obvia. Mal hecho: esconder algo frecuente detrás de un "Ver más" ambiguo. Decidir qué va en cada capa requiere datos de uso reales, no intuición.

---

## 9. Números duros de referencia

Para diseñar/auditar sin adivinar. Detalle y casos en [ver: accesibilidad] y [ver: fundamentos-visuales]; aquí el resumen accionable con fuente.

### Contraste (WCAG 2.2)

| Qué | Ratio | Nivel | Fuente |
|---|---|---|---|
| Texto normal | **4.5:1** | AA (1.4.3) | WCAG 2.2 |
| Texto grande (≥18pt / ≥14pt bold, ≈24px / ≈18.5px) | **3:1** | AA (1.4.3) | WCAG 2.2 |
| Texto normal (enhanced) | **7:1** | AAA (1.4.6) | WCAG 2.2 |
| Texto grande (enhanced) | **4.5:1** | AAA (1.4.6) | WCAG 2.2 |
| Componentes UI y gráficos (bordes, iconos, foco, estados) | **3:1** | AA (1.4.11) | WCAG 2.2 |

Nota WCAG: los valores no se redondean — 4.499:1 **no** pasa 4.5:1.

### Touch targets (móvil)

| Estándar | Tamaño mínimo | Origen | Fuente |
|---|---|---|---|
| WCAG 2.2 mínimo | **24×24 CSS px** | AA (2.5.8), con excepciones (spacing, inline, etc.) | WCAG 2.2 |
| WCAG 2.2 enhanced | **44×44 CSS px** | AAA (2.5.5) | WCAG 2.2 |
| Apple HIG | **44×44 pt** | Convención iOS de larga data | Apple HIG |
| Android / Material | **48×48 dp**, ≥8dp de separación | Material Design Accessibility | Google Accessibility / Material |
| NN/g (físico) | **≥ 1 cm × 1 cm** (0.4in); yema del dedo ≈ 1.6-2 cm, pulgar ≈ 2.5 cm (MIT Touch Lab) | Recomienda medir en mm físicos, no px | NN/g |

Operativo: en web/móvil, target ≥44-48px con ≥8px de aire entre targets cubre WCAG AAA, Apple y Material a la vez. Zona del pulgar y safe areas → [ver: mobile-ux].

---

## 10. El puente con juegos: qué comparte y qué es distinto

Comparte el fondo (todo lo de [ver: gamedev/ux-ui-onboarding]); cambia el contexto de uso.

| Dimensión | App / producto | Juego |
|---|---|---|
| **Objetivo del usuario** | Completar una tarea externa (comprar, reservar, gestionar) con **mínimo esfuerzo** | Divertirse; el "esfuerzo" (reto) ES el valor |
| **Fricción** | Enemiga: cada paso extra = abandono | A veces deseada: la dificultad es el juego |
| **Onboarding** | Rápido, opcional, autoexplicativo; el usuario ya sabe qué quiere | FTUE crítico: enseñar mecánicas nuevas, "aprender haciendo" [ver: gamedev/ux-ui-onboarding] |
| **UI** | Estándar, invisible, convención (heurística 4) | Puede ser diegética/temática, parte de la fantasía |
| **Éxito** | Task success, time-on-task, conversión | Retención, engagement, diversión (D1) |
| **Feedback** | Claro y funcional (estados, errores) | Además "juice"/game-feel [ver: gamedev/game-feel] |
| **Navegación** | Puntero/teclado/touch, patrones web | A menudo mando: focus visible, back universal [ver: gamedev/ux-ui-onboarding §2] |

Comunes a ambos: visibilidad de estado, prevención de error, no dejar al usuario ciego, targets grandes en touch, accesibilidad (contraste, texto escalable, nada crítico solo por color), y **probar con usuarios reales**. Implementación de UI en juego: [ver: unity/ui-unity] y [ver: pipeline/ui-flujo-completo].

Regla que NO cruza: en app, si puedes quitar un paso, quítalo. En juego, un paso puede ser el reto — no "optimices" la diversión hasta matarla.

---

## Reglas prácticas

1. Separa UX (¿resuelve el trabajo, con qué esfuerzo?) de UI (¿se ve y opera claro?). Una UI bella con mal flujo es mala UX.
2. Investiga antes de asumir: habla con 5-8 usuarios y **observa** (lo que hacen ≠ lo que dicen). Tú no eres el usuario.
3. Escribe el **job statement** de cada feature. Si no puedes escribir qué trabajo resuelve, la feature sobra.
4. Persona destilada de investigación real, con solo lo que afecta el diseño. Persona inventada = falsa confianza, peor que ninguna.
5. Mapea el user flow y **cuenta los pasos del camino feliz**; elimina los que no aportan una decisión. Cada paso es abandono potencial.
6. Define la arquitectura de información ANTES de la navegación. Card sorting abierto para generar, tree testing para validar.
7. Etiquetas en el lenguaje del usuario, no jerga interna (heurística 2). Términos consistentes en todo el producto (heurística 4).
8. Audita cada pantalla contra las 10 heurísticas de Nielsen; prioriza por severidad (frecuencia × impacto × persistencia).
9. Visibilidad de estado siempre: todo input tiene feedback (spinner, "Guardado", progreso). Nunca dejar al usuario ciego.
10. Previene el error antes de explicarlo: validación en vivo, deshabilitar CTA inválida, confirmar acciones destructivas.
11. Errores en lenguaje claro con camino de salida, nunca un código pelado (heurística 9).
12. Recognition over recall: muestra opciones, autocompleta, precarga. No obligues a recordar datos de otra pantalla.
13. Una CTA primaria por pantalla; quita lo irrelevante (heurística 8). Cada elemento compite por atención.
14. Baja la carga extraña: menos clutter, modelos mentales familiares, defaults inteligentes. La intrínseca se dosifica, no se elimina.
15. Ley de Hick: menos opciones cuando importa la velocidad; destaca la recomendada; onboarding gradual.
16. Miller (7±2): úsala para **chunking**, NO como límite rígido de ítems de menú.
17. Progressive disclosure: todo lo frecuente arriba; lo raro a un paso obvio y etiquetado.
18. Contraste mínimo AA: 4.5:1 texto normal, 3:1 texto grande y componentes UI. Touch target ≥44-48px con ≥8px de aire.
19. Prueba con 5 usuarios e itera (encuentran ~85% de los problemas). 3 tests de 5 > 1 test de 15.
20. Mide: task success, time-on-task, error rate, SUS (promedio ≈68). Sin métrica, "mejoró" es opinión.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Diseñar desde tus propias suposiciones ("yo lo usaría así") | Investiga y observa a usuarios reales; tú no eres el usuario (false-consensus) |
| Confundir UI bonita con buena UX | Cuenta los pasos y mide task success; un flujo de 6 pasos donde bastaban 2 es mala UX aunque brille |
| Persona inventada en una reunión | Destílala de entrevistas/field studies reales, con solo lo que afecta el diseño |
| Añadir features sin saber qué job resuelven | Job statement obligatorio por feature; sin él, no se construye |
| Diseñar la navegación antes que la IA | Content inventory + card sorting primero; rediseñar por mala estructura es caro |
| Etiquetas con jerga interna ("Config", "Módulo 3") | Lenguaje del usuario, consistente en todo (heurísticas 2 y 4) |
| Menú con 20 opciones planas | Chunking (Miller) + progressive disclosure; agrupa, no listes todo |
| Esconder algo frecuente tras "Ver más" ambiguo | Progressive disclosure correcto: lo frecuente arriba, la vía a lo secundario obvia y etiquetada |
| Acción sin feedback (¿guardó? ¿envió?) | Visibilidad de estado: spinner/"Guardado"/progreso en todo input (heurística 1) |
| Mensaje de error "Error 402" | Lenguaje claro + qué hacer + botón de recuperación (heurística 9) |
| Obligar a recordar datos entre pantallas | Recognition over recall: precarga, autocompleta, muéstralo en pantalla (heurística 6) |
| Pantalla saturada, varias CTAs compitiendo | Una CTA primaria; quita lo irrelevante (heurística 8) |
| Touch targets chicos y pegados | ≥44-48px con ≥8px de aire; medir en el dispositivo real [ver: mobile-ux] |
| Texto gris claro sobre blanco | ≥4.5:1 (AA); verificar el ratio, no "se ve bien" [ver: fundamentos-visuales] |
| Saltarse el test "porque no hay tiempo" | 5 usuarios, prototipo feo, 1 hora: encuentra ~85% de los problemas |
| Declarar "mejoró la UX" sin medir | Task success / time-on-task / SUS antes y después |
| Copiar patrones de juego a una app (o al revés) | En app la fricción es enemiga; en juego el reto es el valor. No cruzar la regla |

## Fuentes

- **"10 Usability Heuristics for User Interface Design" — Jakob Nielsen, Nielsen Norman Group (nngroup.com)** — las 10 heurísticas verbatim; el estándar de facto para evaluar cualquier interfaz. Verificado contra la fuente primaria.
- **"Usability 101: Introduction to Usability" — NN/g** — definición de usabilidad, los 5 componentes (learnability, efficiency, memorability, errors, satisfaction) y la distinción utility/usability/usefulness.
- **"Card Sorting: Uncover Users' Mental Models" — NN/g** — abierto vs cerrado, y los números de participantes (~15 cualitativo, 30-50 cuantitativo).
- **"Progressive Disclosure" — Jakob Nielsen, NN/g** — la definición y la regla de partir features frecuentes vs raras; beneficios en learnability/efficiency/errores.
- **"Minimize Cognitive Load to Maximize Usability" — NN/g** — carga intrínseca vs extraña y las tres palancas (clutter, modelos mentales, offloading).
- **"Personas: Study Guide" / artículos de persona — NN/g** — qué es una persona, qué contiene, que debe salir de investigación real.
- **"Jobs-to-Be-Done" y "Personas vs. JTBD" — NN/g** — definición de JTBD, estructura del job statement (funcional + emocional), ejemplo, y que persona y JTBD son compatibles.
- **"User Journeys vs. User Flows" — NN/g** — definición de user flow (micro, una tarea) vs journey (macro, multicanal).
- **"IA vs. Navigation" — NN/g** — IA como esqueleto invisible, navegación como la punta del iceberg; componentes (inventory, taxonomía, labeling) y que la IA se define antes que la navegación.
- **"Touch Targets on Touchscreens" — NN/g** — recomendación física ≥1cm×1cm; MIT Touch Lab (yema 1.6-2cm, pulgar 2.5cm); por qué medir en mm y no px.
- **WCAG 2.2 — W3C/WAI (w3.org/WAI)** — verificado en la fuente: contraste 4.5:1 texto normal / 3:1 grande (AA, 1.4.3), 7:1 (AAA, 1.4.6), texto grande = 18pt / 14pt bold; target size 24×24 CSS px (AA, 2.5.8) y 44×44 CSS px (AAA, 2.5.5) con sus excepciones.
- **Human Interface Guidelines — Apple (developer.apple.com)** — mínimo tappable 44×44 pt (convención iOS de larga data; la página viva es JS-rendered, cifra canónica ampliamente documentada y consistente con WCAG AAA 44 CSS px).
- **Material Design Accessibility / Android Accessibility Help — Google (support.google.com/accessibility, m3.material.io)** — verificado vía Google Accessibility: touch target mínimo 48×48 dp, referenciando las guías de Material Design.
- **Laws of UX — Jon Yablonski (lawsofux.com)** — Ley de Hick (tiempo de decisión ∝ nº y complejidad de opciones; Hick & Hyman 1952) y Ley de Miller (7±2 en memoria de trabajo, con el caveat de no usarla como límite rígido sino para chunking).
- **System Usability Scale (SUS) — literatura de Brooke / Sauro (MeasuringU)** — escala de 10 ítems 0-100, promedio de industria ≈68; usada como métrica de satisfacción (no re-verificada en fuente esta sesión, cifra ampliamente reportada).
- **Complementa:** [ver: gamedev/ux-ui-onboarding] (UX de juegos), [ver: fundamentos-visuales], [ver: accesibilidad], [ver: mobile-ux], [ver: patrones-ui].
