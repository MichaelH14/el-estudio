# UX writing y microcopy

> **Cuando cargar este archivo:** al escribir o auditar CUALQUIER texto de interfaz de una app, producto o juego — labels de botones, placeholders, tooltips, mensajes de ayuda, errores, confirmaciones, empty states, notificaciones/push, o al definir la voz y el tono del producto. Es el "diseño del texto": la disciplina de qué palabras exactas ve el usuario. El *qué patrón* (cuándo un toast vs modal, cuándo un empty state) vive en [ver: patrones-ui]; el *por qué* (heurísticas, carga cognitiva) en [ver: fundamentos-ux]; el copy de tutoriales/HUD de juego en [ver: gamedev/ux-ui-onboarding]; el modelo i18n/l10n general (RTL, plurales/género, formatos por locale, expansión de texto, culturalización) en [ver: i18n-l10n]; la mecánica técnica de traducir en Unity (string tables, Smart Strings, pseudo-locale) en [ver: pipeline/narrativa-localizacion].

Este archivo es **el texto de la interfaz** (UX writing / content design / microcopy). Lo que ya vive en otro lado y NO se repite aquí:
- **Cuándo** usar un toast, modal, undo, banner; los 3 tipos de empty state; validación inline vs on-submit → [ver: patrones-ui §3, §7, §9]
- Las heurísticas que rigen el copy (H2 lenguaje real, H4 consistencia, H9 recuperación de errores) y carga cognitiva → [ver: fundamentos-ux §6, §8]
- Estados de un control (loading, disabled), microinteracciones, timing del feedback → [ver: interaccion-microux]
- El modelo i18n/l10n completo — RTL, plurales/género (ICU MessageFormat), formatos de fecha/número/moneda por locale, tabla de expansión, keys, proceso de traducción (TMS, pseudo-locale, string freeze), culturalización de color/símbolo/imagen → [ver: i18n-l10n]
- Pipeline técnico de localización en Unity (string tables, Smart Strings, claves, pseudo-locale, CSV) → [ver: pipeline/narrativa-localizacion]
- Copy de tutoriales/FTUE, HUD, subtítulos, settings de juego → [ver: gamedev/ux-ui-onboarding]
- Estructura de diálogo, branching, barks, guion → [ver: gamedev/narrativa-guion]
- Que el error no dependa solo del color (rojo + icono + texto), contraste del texto → [ver: accesibilidad]

**Versión / estándares 2026:** UX writing es disciplina de lenguaje, casi independiente de versión. Los sistemas citados están vivos a 2026 (Material 3, Apple HIG, Shopify Polaris, Microsoft Writing Style Guide, GOV.UK). Las cifras dependientes de estudio se marcan con su fuente; lo no verificado esta sesión se marca **NO VERIFICADO**.

---

## 1. Qué es UX writing y por qué es disciplina propia

**UX writing** (a.k.a. *content design*, *microcopy*): diseñar el texto funcional que el usuario lee mientras usa el producto — no el marketing, no la documentación. Es parte de la UI tanto como el color o el espaciado, y casi siempre el elemento que más carga cognitiva mueve por pixel.

| No es | Es |
|---|---|
| Copywriting de marketing (persuadir para comprar) | El texto que guía la tarea *dentro* del producto |
| Documentación / manual (leído aparte, a demanda) | Texto embebido en el momento de la acción |
| "Rellenar los strings al final" | Diseño: se piensa junto al flujo, no después |
| Decorar con personalidad | Claridad primero; la personalidad se cuela sin estorbar |

- **Microcopy**: los textos chicos y funcionales — label de botón, placeholder, hint bajo un campo, texto de tooltip, mensaje de estado, línea de un empty state, título de una confirmación. Chicos en tamaño, enormes en impacto: deciden si el usuario entiende qué pasa y qué hacer.
- Regla madre (transversal a NN/g, Material, Apple, Microsoft, Polaris, GOV.UK): **claridad por encima de todo**. Mailchimp lo fija: *"siempre es más importante ser claro que entretenido"*. Ingenio que cuesta comprensión = fallo.
- Se escribe en el idioma **del usuario, no del sistema** (heurística 2, [ver: fundamentos-ux]): "Papelera", no "Objeto eliminado del árbol de nodos"; "Tarjeta rechazada", no "Error 402".

---

## 2. Voz y tono: la personalidad en palabras

**Voz = constante; tono = variable.** Mailchimp lo resume: *"tienes la misma voz todo el tiempo, pero tu tono cambia"*. La voz es la personalidad fija del producto; el tono la ajusta al contexto y al **estado emocional del lector**.

### 2.1 Definir la voz (el rasgo fijo)

Las cuatro dimensiones de tono de NN/g (estudio con 50 participantes; las variaciones producen diferencias medibles pero **pequeñas**, ~0.5–1 punto en escala de 5 → la voz importa, pero no salva un mal flujo):

| Dimensión (espectro) | Un extremo | El otro |
|---|---|---|
| **Formal ↔ casual** | "Introduzca sus credenciales" | "Entra con tu correo" |
| **Serio ↔ gracioso** | Sin bromas | Humor, juego de palabras |
| **Respetuoso ↔ irreverente** | Deferente | Descarado, atrevido |
| **Neutral ↔ entusiasta** | Seco, informativo | Emocionado ("¡Genial!") |

- **Regla NN/g:** decide primero la posición en cada dimensión (alto nivel), después las palabras. Y **no te vayas a los extremos** — casi ningún producto de negocio gana siendo 100% gracioso o 100% seco.
- Herramienta operativa (Podmajersky, *Strategic Writing for UX*): un **voice chart** que traduce cada principio de marca a decisiones concretas: conceptos, vocabulario, verbosidad, gramática, puntuación, mayúsculas. Es lo que hace la voz **reproducible** por cualquiera que escriba, no solo por el que la inventó.
- La voz sale de la marca/personas, no de la reunión. Escríbela como 3-5 adjetivos + un "somos X, no Y" (ej. Mailchimp: *"raros pero no inapropiados, listos pero no snobs"*).

### 2.2 Adaptar el tono al contexto (el rasgo variable)

Mailchimp: *"considera el estado mental del lector"*. El mismo producto habla distinto según lo que le pasa al usuario:

| Contexto | Estado del usuario | Tono correcto | Ejemplo |
|---|---|---|---|
| **Éxito / celebración** | Alivio, logro | Cálido, breve, celebra sin exceso | "¡Listo! Tu pedido va en camino" |
| **Error del usuario** | Frustrado, quizás avergonzado | Calmado, útil, **cero culpa**, cero broma | "Ese correo no existe. Revísalo y vuelve a intentar" |
| **Error del sistema** | Confundido, molesto | Honesto, se disculpa sobrio, da salida | "No pudimos guardar. Reintenta en un momento" |
| **Acción destructiva** | Tenso, a punto de perder algo | Directo, serio, nombra lo que se pierde | "Eliminar 12 archivos. Esto no se puede deshacer" |
| **Onboarding / vacío** | Curioso, sin contexto | Alentador, guía | "Aún no tienes proyectos. Crea el primero" |
| **Espera / carga** | Impaciente | Tranquilizador, honesto | "Procesando tu pago…" |

- **La broma tiene contexto:** el humor que encanta en un empty state es hostil en un error de pago. Regla de oro: **nunca hagas humor sobre el dolor del usuario** (dinero, datos perdidos, fallo). NN/g cita como mal ejemplo un buscador que pone chistes en vez de explicar por qué no hay resultados.
- El tono cambia; la voz no. Un producto "casual y cálido" sigue siendo casual y cálido en un error — solo baja el volumen del humor, no cambia de personalidad.

---

## 3. Claridad: los principios que aplican a todo texto

Destilado de Microsoft Writing Style Guide (top 10 tips), Polaris, GOV.UK, Apple HIG y NN/g. Cada regla con antes → después:

| Principio | Regla | Antes ✗ → Después ✓ |
|---|---|---|
| **Menos palabras** | Poda cada palabra que no aporte (Microsoft: "ideas grandes, menos palabras") | "Si estás listo para comprar…" → "¿Listo? Contáctanos" |
| **Escribe como hablas** | Léelo en voz alta; sin jerga (Microsoft) | "ID inválido" → "Necesitas un correo así: alguien@ejemplo.com" |
| **Lenguaje del usuario** | Su vocabulario, no términos internos | "Autenticación fallida" → "Correo o contraseña incorrectos" |
| **Al grano, front-load** | La palabra clave primero (se escanea el inicio) | "Más información sobre facturas" → "Facturas: cómo descargarlas" |
| **Voz activa, empieza con verbo** | Microsoft: "casi siempre empieza con un verbo"; corta "puedes" | "Puedes guardar los archivos" → "Guarda los archivos" |
| **Sé específico** | Di exactamente qué, no genérico | "Algo salió mal" → "No se pudo enviar el mensaje" |
| **Sentence case** | Solo mayúscula inicial + nombres propios (Microsoft, GOV.UK, Material) | "Guardar Todos Los Cambios" → "Guardar cambios" |
| **Sin punto en títulos/labels** | UI titles y botones sin punto final (Microsoft) | "Guardar." → "Guardar" |

- **Nivel de lectura:** apunta bajo. Polaris: ~**7º grado**. GOV.UK exige inglés llano y apunta aún más abajo para contenido público. Regla práctica: si una frase necesita releerse, reescríbela.
- **Contracciones — matiz por contexto:** Microsoft, Mailchimp y Polaris las **recomiendan** ("no" → "don't"/"no lo") porque calientan el tono. Pero GOV.UK **desaconseja las contracciones negativas** ("can't", "don't") porque parte de los usuarios las malinterpreta. Resolución: contracciones para el tono general; en copy crítico, de seguridad o negativo, escribe el "no" completo para que no se lea al revés.
- **Consistencia > variedad:** un término, una cosa (§9). No alternes "Ajustes"/"Config"/"Preferencias" ni "Eliminar"/"Borrar"/"Quitar" para la misma acción.

---

## 4. Copy de botones y acciones

El botón es el microcopy más caro: es donde el usuario decide actuar. **Un botón dice qué PASA al pulsarlo**, no un genérico.

### 4.1 Verbo de acción, no "OK/Enviar/Aceptar"

| Genérico ✗ | Específico ✓ (qué pasa) |
|---|---|
| OK / Aceptar | Guardar cambios · Eliminar · Publicar |
| Enviar / Submit | Enviar solicitud · Crear cuenta · Pagar $340 |
| Sí / No (en "¿Seguro?") | Eliminar 12 archivos · Cancelar |
| Continuar (ambiguo) | Ir al pago · Siguiente: envío |
| + Agregar (redundante) | + Proyecto (Polaris: quita la palabra que sobra) |

- Regla (Apple HIG, Polaris, Material): **verbo + objeto**. El label debe poder leerse como "quiero **[label]**". "Quiero OK" no significa nada; "Quiero Guardar cambios" sí.
- **Empareja el botón con su título.** Si el modal pregunta "¿Descartar borrador?", el botón de acción es "Descartar", no "OK". El usuario que no lee el cuerpo debe entender solo con el par título+botón.
- **Los dos botones nunca pesan igual.** Una acción primaria (color/relleno), la secundaria discreta (texto/borde). Y la destructiva se ve destructiva (rojo + label explícito). [ver: patrones-ui §9] para el mecanismo; aquí manda el *texto*.

### 4.2 Primera vs segunda persona

| Persona | Ejemplo | Cuándo |
|---|---|---|
| **Segunda ("tu")** — el sistema le habla al usuario | "Inicia **tu** prueba gratis" | Default seguro; el producto se dirige al usuario |
| **Primera ("mi")** — el botón habla *por* el usuario | "Iniciar **mi** prueba gratis" | El botón como declaración del propio usuario |

- Un A/B test muy citado (ContentVerve / Michael Aagaard) reportó que cambiar "tu" por "mi" en un botón subió el CTR ~90% — **NO VERIFICADO** en fuente primaria esta sesión y es **un solo test**, no ley. La lección firme: la persona gramatical del botón importa, no es cosmética; **elige una convención y sé consistente**, y si es una conversión clave, testéala en tu producto.
- No mezcles en el mismo flujo: o todo "tu" o todo "mi".

---

## 5. Microcopy: labels, placeholders, tooltips, ayuda

| Elemento | Qué es | Reglas de copy |
|---|---|---|
| **Label de campo** | Nombra qué se pide | Persistente, arriba del campo, sustantivo claro ("Correo", no "Ingrese su correo"). Nunca lo sustituye el placeholder [ver: patrones-ui §3.1] |
| **Placeholder** | Ejemplo del **formato**, no instrucción | Muestra un ejemplo real ("nombre@correo.com", "DD/MM/AAAA"). Desaparece al escribir → jamás pongas info crítica ahí |
| **Hint / help text** | Aclara requisito o razón | Debajo del campo, permanente, breve: "Mínimo 8 caracteres" · "Solo la vemos para enviarte el recibo" |
| **Tooltip** | Ayuda contextual a demanda | Una frase; explica lo que el icono/label no alcanza a decir. No metas ahí nada indispensable (no todos lo abren) |
| **Empty/placeholder de valor** | Donde iría un dato aún ausente | Resuélvelo con default o mensaje útil, **nunca un "—" gigante** [ver: patrones-ui §7.2] |
| **Character/estado counter** | Progreso de un límite | "120/280" — informa antes de que falle, no después |

- **Placeholder ≠ label** es el error de microcopy más común. El placeholder como única etiqueta rompe memoria (desaparece), accesibilidad y edición. Label visible siempre; placeholder solo para el ejemplo de formato.
- **Marca lo opcional, no lo requerido** cuando casi todo es obligatorio: "(opcional)" tras el label, en vez de sembrar asteriscos [ver: patrones-ui §3.1].
- El hint que explica **por qué** pides un dato baja fricción: "Teléfono (para avisarte de tu entrega)" convierte mejor que "Teléfono *".

---

## 6. Mensajes de error: humanos, claros, accionables

Un buen error tiene **tres partes**: qué pasó + por qué (si ayuda) + **cómo arreglarlo**. NN/g agrupa las reglas en visibilidad, comunicación y eficiencia:

| Regla (NN/g) | En el texto |
|---|---|
| **Lenguaje llano, cero jerga** | "No se pudo conectar", no "ERR_CONNECTION_TIMED_OUT" |
| **Específico, no genérico** | "El código expiró", no "Ocurrió un error" |
| **Da la solución** | "Revisa tu conexión y reintenta" — un camino de salida, idealmente un botón |
| **Tono positivo, sin culpar** | NN/g: "no uses frases que culpen al usuario o impliquen que hace algo mal" |
| **Junto a la causa** | Pegado al campo/acción que falló (proximidad baja carga) [ver: patrones-ui §3.2] |
| **Preserva lo escrito** | Nunca vacíes el formulario; el usuario corrige, no reescribe |

- **Sin culpa:** "Entrada inválida" / "Contraseña ilegal" → "La contraseña necesita 8+ caracteres". Culpa al requisito, no a la persona.
- **Sin códigos pelados:** un "Error 402" o un stack trace es texto del sistema, no del usuario. Traduce siempre. (Si necesitas un código para soporte, ponlo pequeño y secundario: "Si persiste, menciona el código E-402".)
- **No solo color:** el rojo no basta; añade icono + texto (≈8% de hombres tiene deficiencia de visión de color) [ver: accesibilidad].
- **Empareja el mensaje con la severidad:** error de campo → inline; fallo de flujo → banner/toast; pérdida de datos → modal [ver: patrones-ui §9]. El *texto* cambia poco; el *contenedor* sí.

**Plantilla operativa:** `[Qué pasó, en su idioma]. [Cómo arreglarlo / qué hacer ahora].`
Ejemplo: "No pudimos cobrar tu tarjeta. Revisa los datos o prueba con otra." + botón "Reintentar".

---

## 7. Empty states, confirmaciones y estados

El *cuándo/cuál* de estos patrones vive en [ver: patrones-ui §7-§9]; aquí, **las palabras**.

### 7.1 Empty states — el vacío como guía

| Tipo | Qué dice el texto |
|---|---|
| **Primer uso** (nunca hubo datos) | Explica qué irá aquí + **acción directa**: "Aún no tienes clientes. Agrega el primero" (no un panel mudo) |
| **Vaciado por el usuario** (inbox a cero) | Refuerzo positivo, celebra: "Todo al día 🎉" — no alarmes |
| **Sin resultados** (búsqueda/filtro) | Confirma el estado + salida: "Nada para 'xyz'. Prueba otro término o quita filtros" |

El empty state suele ser la primera impresión de la pantalla: es onboarding contextual, no un error. Convierte el vacío en el siguiente paso.

### 7.2 Confirmaciones y destructivo — el "¿estás seguro?" bien escrito

- El "¿Estás seguro?" genérico **no informa**. Sustitúyelo por: **título = la consecuencia**, **botón = la acción exacta**.
  - ✗ "¿Estás seguro?" / [OK] [Cancelar]
  - ✓ "¿Eliminar el proyecto 'Ventas Q3'?" · "Se borran 8 tableros y no se puede deshacer." / [Eliminar proyecto] [Cancelar]
- **Nombra exactamente qué se afecta** (cantidad, nombre) y si es reversible. "Eliminar 12 archivos" > "Eliminar elementos".
- **Reversible → prefiere "hacer + Deshacer"** (snackbar "Archivado — Deshacer") en vez de un diálogo previo; reserva la confirmación modal para lo **irreversible** [ver: patrones-ui §9].
- El botón destructivo lleva el verbo real, nunca "OK". El de escape es "Cancelar" (claro y neutral), no "No".

### 7.3 Éxito y carga

- **Éxito:** confírmalo y, si aporta, di qué sigue: "Guardado" · "Pago recibido — te enviamos el recibo". Efímero (toast) para lo de bajo impacto [ver: patrones-ui §9].
- **Carga:** honesto y específico. "Cargando…" seco < "Preparando tu reporte…". En esperas largas, di el estado/progreso, no un spinner mudo [ver: interaccion-microux; patrones-ui §8].

---

## 8. Notificaciones y push: enganchar sin molestar

El push mal escrito quema permiso y desinstala. Reglas:

| Regla | Detalle |
|---|---|
| **Aporta valor real, no ruido** | Cada push responde "¿por qué le importa AHORA al usuario?". Si es para el negocio y no para él, no lo mandes |
| **Específico y accionable** | "Tu pedido #3021 sale mañana 9-11am" > "Novedades de tu pedido" |
| **Front-load** | La info clave en las primeras palabras (el push se trunca): "Pago recibido: $340…" |
| **Personal y oportuno** | Nombre/dato + momento correcto; no a las 3am, no 5 veces al día |
| **Pide el permiso en contexto** | Explica el beneficio antes del prompt del SO; nunca todos los permisos al abrir [ver: patrones-ui §10.3] |
| **Respeta el "no"** | Pedir una vez; insistir (nagging) es dark pattern [ver: patrones-ui §12] |
| **Da control** | Tipos de notificación granulares y fáciles de apagar |

- El copy que **crea urgencia falsa** ("¡Solo hoy!", contadores inventados) es dark pattern y hay regulación creciente (GDPR/DSA/FTC, 2026) [ver: patrones-ui §12]. Urgencia solo si es real.
- Título corto + cuerpo que amplía; nunca repitas el título en el cuerpo.

---

## 9. Consistencia: un término, una cosa (el glosario)

La heurística 4 (consistencia, [ver: fundamentos-ux §6]) aplicada al lenguaje: **el mismo concepto se llama siempre igual en todo el producto.**

- Mantén un **glosario de producto** (una tabla): término aprobado + qué es + variantes prohibidas. Ej.: usar "Proyecto" (no "espacio"/"tablero"/"workspace" para lo mismo); "Eliminar" (no "borrar"/"quitar"/"remover" mezclados).
- Cubre también acciones (Guardar vs Aplicar vs Confirmar — que cada una signifique algo distinto y estable), estados (Activo/Pausado/Archivado) y roles (Admin/Miembro).
- Un mismo botón ("Guardar") en el mismo sitio, con el mismo texto, en todas las pantallas. La inconsistencia hace dudar al usuario de si "Borrar" y "Eliminar" hacen lo mismo.
- El glosario es también la base de la traducción: un término inconsistente en el idioma fuente se multiplica por cada idioma (§10).

---

## 10. Localización del copy: escribir pensando en la traducción

El **modelo i18n/l10n completo** — RTL/bidi, plurales y género con ICU MessageFormat, formatos de fecha/número/moneda por locale (CLDR/`Intl`), la tabla de expansión de texto (IBM/W3C), keys estables, el proceso de traducción (TMS, pseudo-localización, string freeze) y la culturalización de color/símbolo/imagen — vive en [ver: i18n-l10n] y no se repite aquí. El **cómo técnico en Unity** (string/asset tables, Smart Strings, pseudo-locale, CSV) está en [ver: pipeline/narrativa-localizacion]. Aquí, solo el **ángulo de redacción**: qué hace que el copy fuente sea fácil o imposible de traducir bien.

| Regla de redacción | Por qué / qué hacer |
|---|---|
| **Cero modismos, refranes, puns** | No traducen literal. "Pan comido", "matar dos pájaros", juegos de palabras → di lo literal |
| **Frases completas, no fragmentos concatenados** | El orden de palabras cambia por idioma (p.ej. alemán manda el verbo al final); nunca construyas concatenando en código ("Nivel " + n). Una frase con placeholder: "Nivel {0}" — el motor de plural/género (ICU MessageFormat) que resuelve esto vive en [ver: i18n-l10n §6] |
| **Deja aire de expansión al escribir** | Un label corto en inglés puede llegar a 2-3x en otro idioma (tabla IBM/W3C completa: [ver: i18n-l10n §3]); no calibres el texto al ancho justo del inglés |
| **Cuida el humor y lo cultural** | Referencias locales, sarcasmo y celebraciones se leen distinto entre culturas; el detalle de color/símbolo/imagen por cultura está en [ver: i18n-l10n §9] |

- Formatos de fecha/número/moneda, plural/género con ICU, RTL, keys estables y el proceso de traducción (TMS, pseudo-locale, string freeze) son terreno de [ver: i18n-l10n] — esa es la referencia operativa completa; este archivo solo cubre el estilo de redacción del copy fuente.
- El copy fuente **también** entra por el sistema de strings desde el día 1 (nunca "ya lo migraré") [ver: i18n-l10n §1-§2; pipeline/narrativa-localizacion §10 para el caso Unity].
- Escribir claro y corto (§3) es *ya* escribir traducible: frases simples, un sujeto, un verbo, sin subordinadas anidadas.

---

## 11. El copy en juegos

El texto de juego comparte todo lo anterior pero cambia el contexto; el detalle de HUD/tutoriales/settings está en [ver: gamedev/ux-ui-onboarding] y la estructura de diálogo en [ver: gamedev/narrativa-guion]. Puntos de *copy* propios:

| Situación | Regla de copy |
|---|---|
| **Tutorial / FTUE** | Máx. **~8 palabras** en pantalla a la vez (George Fan); enseñar haciendo, no leyendo. Nunca lo llames "tutorial" |
| **Feedback de acción** | Verbo claro, inmediato, en lenguaje del jugador: "¡Recargado!", no un código; "Fallaste — reintenta" con salida |
| **Narrativa de UI / flavor** | El copy puede llevar la voz del mundo (diegético), pero **función antes que fantasía**: si un label temático cuesta legibilidad, gana la claridad [ver: gamedev/ux-ui-onboarding §1] |
| **Pantalla de derrota** | Enmarca el progreso en positivo (patrón Overwatch): resalta lo logrado, no solo el fracaso |
| **Empty state (sin partidas/items)** | Igual que en app: di qué hacer para llenarlo, no un panel en blanco |
| **Botones de menú** | "Jugar"/"Continuar" prominentes y con verbo; "Continuar" primero si hay partida guardada |
| **Subtítulos** | Toda línea hablada subtitulada, incluidos barks; legibles, on por defecto [ver: pipeline/narrativa-localizacion §11] |

- El tono del juego es parte del *game feel*: un shooter frenético y un cozy game escriben el mismo "Guardado" con energía distinta — pero ambos claros primero.
- Copy de tutorial en el tono pedagógico aprobado: la mecánica de *cómo se habla* al jugador es su propia disciplina; aquí solo la regla de las 8 palabras y "enseñar haciendo".

---

## Reglas prácticas

1. **Claridad por encima de todo.** Ingenio que cuesta comprensión = fallo (Mailchimp: "más importante ser claro que entretenido").
2. Escribe en el **idioma del usuario, no del sistema** (heurística 2): "Papelera", no "nodo eliminado"; "Tarjeta rechazada", no "Error 402".
3. **Voz constante, tono variable.** Define la voz en 3-5 adjetivos + "somos X, no Y"; ajusta el tono al estado emocional (éxito ≠ error ≠ destructivo).
4. **Nunca hagas humor sobre el dolor del usuario** (pago fallido, datos perdidos). El chiste tiene contexto.
5. **Botón = qué pasa al pulsarlo:** verbo + objeto ("Guardar cambios"), jamás "OK/Enviar" genérico. Léelo como "quiero [label]".
6. **Empareja título y botón:** el par debe entenderse sin leer el cuerpo. "¿Descartar borrador?" → botón "Descartar".
7. **Menos palabras, empieza con verbo, corta "puedes"** (Microsoft): "Guarda los archivos", no "Puedes guardar los archivos".
8. **Front-load:** la palabra clave primero; se escanea el inicio de cada label, link y push.
9. **Sentence case, sin punto en títulos/labels/botones** (Microsoft, Material, GOV.UK).
10. **Placeholder ≠ label.** Label persistente arriba; placeholder solo como ejemplo de formato; hint permanente bajo el campo.
11. **Error = qué pasó + cómo arreglarlo, sin culpar, sin jerga, sin código pelado,** junto a la causa y preservando lo escrito (NN/g).
12. **Empty state como guía:** explica qué irá + acción directa; celebra el vaciado, no lo alarmes; en "sin resultados" ofrece salida.
13. **"¿Estás seguro?" no informa:** título = consecuencia, botón = acción exacta que nombra lo afectado ("Eliminar 12 archivos").
14. **Reversible → "hacer + Deshacer"** (snackbar); confirmación modal solo para lo irreversible.
15. **Push:** valor real para el usuario + específico + oportuno; pide permiso en contexto; respeta el "no"; cero urgencia falsa.
16. **Un término, una cosa:** mantén un glosario de producto; no alternes sinónimos para el mismo concepto/acción (heurística 4).
17. **Escribe traducible:** cero modismos/puns, frases completas con placeholders (nunca concatenar), plural/número al motor, ~30-40% de aire de expansión.
18. **Nivel de lectura bajo** (~7º grado, Polaris); si una frase se relee, reescríbela.
19. **Contracciones sí para calentar el tono**, pero escribe el "no" completo en copy crítico/negativo (GOV.UK: se malinterpretan).
20. **Juego:** ~8 palabras en tutorial, enseñar haciendo, función antes que fantasía; el copy diegético nunca a costa de la legibilidad.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Botón "OK"/"Enviar"/"Aceptar" genérico | Verbo + objeto que dice qué pasa: "Guardar cambios", "Crear cuenta", "Pagar $340" |
| "¿Estás seguro? [OK] [Cancelar]" para todo | Título = consecuencia, botón = acción que nombra lo afectado; Deshacer para lo reversible |
| Error con código pelado / stack trace ("Error 402") | Traduce a lenguaje del usuario + solución + botón; el código, pequeño y secundario para soporte |
| Mensaje que culpa: "Entrada inválida", "Contraseña ilegal" | Culpa al requisito, no a la persona: "La contraseña necesita 8+ caracteres" |
| Broma en un error de pago o pérdida de datos | Humor solo donde no duele; en el dolor, calma y solución |
| Placeholder usado como única etiqueta (desaparece al escribir) | Label persistente arriba; placeholder solo para el ejemplo de formato |
| "Algo salió mal" / "Ocurrió un error" (genérico) | Específico: "No se pudo enviar el mensaje. Revisa tu conexión y reintenta" |
| Jerga del sistema: "Autenticación fallida", "token expirado" | Idioma del usuario: "Correo o contraseña incorrectos", "Tu sesión expiró, entra de nuevo" |
| Empty state en blanco o con "—" gigante | Mensaje + acción directa: "Aún no tienes X. Crea el primero" |
| Sinónimos mezclados (Ajustes/Config/Preferencias; Borrar/Eliminar/Quitar) | Glosario: un término aprobado por concepto, consistente en todo |
| Concatenar frases traducidas ("Nivel " + n) → intraducible | Frase completa con placeholder ("Nivel {0}") + plural/género del motor de loc |
| Modismos/puns en el copy fuente | Di lo literal; el ingenio no sobrevive la traducción |
| Push que solo sirve al negocio / urgencia falsa / nagging | Valor real para el usuario, en contexto, una vez; urgencia solo si es real |
| Título largo, verbo enterrado al final | Front-load: palabra clave primero; corta "puedes" y "hay que" |
| Copy escrito al final, "rellenar strings" | Escribe el texto junto al flujo, desde el día 1, dentro del sistema de strings |
| Tutorial de juego con párrafos y "presiona X para continuar" x10 | ~8 palabras, enseñar haciendo, no llamarlo tutorial (Fan) |

## Fuentes

- **"The Four Dimensions of Tone of Voice" — Nielsen Norman Group (nngroup.com)** — verificado: las 4 dimensiones (formal↔casual, serio↔gracioso, respetuoso↔irreverente, neutral↔entusiasta), estudio con 50 participantes, diferencias medibles pero pequeñas (~0.5-1 pt/5), regla de no ir a los extremos y variar el tono por estado emocional manteniendo la voz.
- **"Error-Message Guidelines" — Nielsen Norman Group (nngroup.com)** — verificado: visibilidad/comunicación/eficiencia; lenguaje llano, específico, con solución, tono positivo ("no culpes al usuario"), junto a la causa, preservar el input.
- **"Better Link Labels: 4 Ss" / writing-links — Nielsen Norman Group (nngroup.com)** — verificado: especificidad, front-load (la gente mira las 2 primeras palabras), evitar "click here"/"read more", labels únicos.
- **Mailchimp Content Style Guide — Voice and Tone (styleguide.mailchimp.com)** — verificado: "misma voz siempre, el tono cambia"; considerar el estado mental del lector; pilares plainspoken/genuine/translators/dry humor; "más importante ser claro que entretenido".
- **Microsoft Writing Style Guide — Top 10 tips for style and voice (learn.microsoft.com)** — verificado con ejemplos: ideas grandes/menos palabras, escribe como hablas, contracciones para amabilidad, al grano/front-load, sé breve, sentence case, sin punto en títulos, empieza con verbo y corta "you can".
- **Shopify Polaris — Voice and tone + Actionable language (polaris-react.shopify.com)** — verificado: lenguaje llano, contracciones, ~7º grado de lectura, "lean", verbo-primero ("add apps", no "you can add apps"), quitar palabras redundantes ("+" en vez de "+ Add").
- **GOV.UK Style Guide — A to Z (guidance.publishing.service.gov.uk)** — verificado: inglés llano obligatorio, lista de "words to avoid" (leverage, utilise, deliver, robust, key, drive, facilitate, streamline, transform…), sentence case, dirigirse como "you", voz activa, y el matiz de desaconsejar contracciones negativas (can't/don't) porque se malinterpretan.
- **Apple Human Interface Guidelines — Writing (developer.apple.com/design/human-interface-guidelines/writing)** — estándar documentado (página live es SPA; no citada verbatim esta sesión): botones con verbos, evitar "OK"/"Submit" vagos, alertas específicas ("Safari cannot open the page", no "Error occurred"), voz activa, lenguaje inclusivo sin modismos.
- **Material Design 3 — Content design / UX writing best practices (m3.material.io/foundations/content-design)** — estándar documentado (SPA; no citada verbatim esta sesión): conciso, claro, consistente (terminología), sentence case, vocabulario del usuario, acciones con verbos.
- **"Strategic Writing for UX" — Torrey Podmajersky (O'Reilly)** — referencia del *voice chart* (principios de marca → conceptos, vocabulario, verbosidad, gramática, puntuación, mayúsculas) que hace la voz reproducible.
- **"Microcopy: The Complete Guide" — Kinneret Yifrah** — referencia canónica de microcopy conversacional (voz/tono, formularios, errores, empty states, botones).
- **Caso A/B "my vs your" — ContentVerve / Michael Aagaard** — reportado (~+90% CTR al cambiar "your" por "my" en un botón); **NO VERIFICADO** en fuente primaria esta sesión y un solo test — se usa solo como ilustración de que la persona gramatical importa y debe testearse.
- **Complementa:** [ver: patrones-ui] (qué patrón y cuándo), [ver: fundamentos-ux] (heurísticas y carga cognitiva), [ver: interaccion-microux] (feedback y estados), [ver: accesibilidad] (no solo color, contraste del texto), [ver: i18n-l10n] (modelo i18n/l10n completo: RTL, plurales/género, formatos, expansión, culturalización), [ver: pipeline/narrativa-localizacion] (pipeline técnico de traducción en Unity), [ver: gamedev/ux-ui-onboarding] y [ver: gamedev/narrativa-guion] (copy de juego).
