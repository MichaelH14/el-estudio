# Sistemas de diseño
> **Cuando cargar este archivo:** al arrancar un producto/app nuevo y decidir su base visual reutilizable, al montar o auditar tokens (color/espaciado/tipografía/radios/sombras), al definir la biblioteca de componentes y TODOS sus estados, al conectar el diseño con CSS/Tailwind/framework, o al decidir si copiar/adaptar Material, HIG, Polaris o Carbon. Es la capa "sistema" que ordena lo que [ver: fundamentos-visuales] enseña suelto y lo que [ver: patrones-ui] y [ver: interaccion-microux] aplican pieza a pieza.

Este archivo es UX/UI de **producto/app** (web y móvil). Los fundamentos crudos (contraste, escala tipográfica, jerarquía, grid) viven en [ver: fundamentos-visuales] — aquí NO se repiten, se **sistematizan** en variables reutilizables. El lado juegos (HUD, tutoriales in-game, FTUE) está en [ver: gamedev/ux-ui-onboarding] y el game-feel en [ver: gamedev/game-feel]; la implementación de UI en motor en [ver: unity/ui-unity] y [ver: pipeline/ui-flujo-completo]. Referéncialos, no los dupliques.

## 1. Qué es un design system (y qué NO es)

Definición NN/g: **"un conjunto completo de estándares para gestionar el diseño a escala usando componentes y patrones reutilizables"**. No es una paleta de colores ni un archivo de Figma bonito: es la fuente única de verdad + su código + las reglas de uso.

| Capa | Qué contiene | No confundir con |
|---|---|---|
| **Design system** (el todo) | Tokens + componentes + patrones + principios + documentación viva, sincronizados diseño↔código | El resto son *partes* de esto |
| **Style guide** | Reglas de marca: color, tipografía, logo, tono de voz, principios de interacción | Es documentación, no componentes ejecutables |
| **Component library** | Piezas UI concretas y reutilizables: nombre, atributos, **estados**, snippet de código, framework | Un style guide no trae código; una lib sí |
| **Pattern library** | Cómo se combinan varios componentes en estructuras recurrentes (formularios, layouts, flujos) | Componente = pieza; patrón = receta de uso |

**Por qué existe (el ROI real, NN/g):**

| Beneficio | Mecanismo |
|---|---|
| **Consistencia** | Misma decisión (un color, un radio) sale de una variable, no de 40 copias divergentes |
| **Velocidad** | Ensamblar UI de piezas premade en vez de reinventar cada pantalla; el equipo pasa de retocar píxeles a resolver problemas |
| **Escala** | Un cambio en el token se propaga a todo el producto de una vez |
| **Lenguaje común** | "Botón primario", "card", "surface" significan lo mismo para diseño, front y back |
| **Onboarding** | El sistema documentado enseña el producto a quien entra nuevo |

**El costo honesto (NN/g):** un sistema exige mantenimiento continuo y su ROI aparece **a lo largo de años/muchas pantallas**, no en la primera. Para un proyecto de una sola pantalla, un design system formal es sobre-ingeniería. Regla de arranque para dev solo: **empieza por tokens + 5-8 componentes base**, no por un sistema de 200 piezas. La ley de Tesler recuerda que la complejidad es irreducible: un sistema no la elimina, la **centraliza donde se mantiene una vez** [ver: fundamentos-ux].

## 2. Design tokens: las decisiones como variables

**Definición (Design Tokens Community Group, W3C):** *"la fuente única de verdad para nombrar y almacenar una decisión de diseño, distribuida para que los equipos la usen entre herramientas de diseño y lenguajes de código."* Un token no es un valor suelto: es un **nombre semántico + un valor**, y puede ser un **alias** (referencia a otro token) o **composite** (varios valores hijo, ej. una sombra = offset + blur + color).

### Las 3 capas de tokens (tiers) — el patrón que usan Material, Polaris y Carbon

| Tier | Nombre típico | Ejemplo | Regla |
|---|---|---|---|
| **1. Primitivos / core / reference** | `blue-500`, `space-4`, `radius-2` | `#3B82F6`, `16px`, `8px` | Valores crudos, sin significado de uso. **Nunca se usan directo en componentes.** |
| **2. Semánticos / alias / system** | `color-action-primary`, `color-surface`, `space-inset-md` | → `blue-500`, → `gray-50` | Describen **intención**, no apariencia. Aquí vive el light/dark. Es la capa que consume la UI. |
| **3. De componente** | `button-primary-bg`, `card-radius` | → `color-action-primary` | Opcional; solo cuando un componente necesita desviarse del semántico. |

La disciplina clave: **los componentes consumen tokens semánticos, no primitivos**. Así, cambiar la marca = reasignar la capa 2, sin tocar componentes.

### Categorías de tokens (el mínimo de un sistema de producto)

| Categoría | Qué modela | Ejemplo de escala |
|---|---|---|
| **Color** | Fondos, texto, bordes, acciones, estados (éxito/aviso/error/info) | Ver §3 |
| **Spacing** | Padding, margin, gap — un solo eje de espaciado | 4·8·12·16·24·32·48·64… |
| **Typography** | Familia, tamaño, peso, line-height, letter-spacing (composite por estilo) | Ver §3 |
| **Radius** | Esquinas: none/sm/md/lg/full | 0·4·8·12·9999px |
| **Shadow / elevation** | Profundidad, capas (composite) | sm/md/lg/xl |
| **Motion** | Duración + curva de easing | 150/200/300ms |
| **Z-index** | Orden de apilado: base/dropdown/sticky/modal/toast | 0·10·20·1000·1100 |
| **Breakpoints** | Puntos de corte responsive | sm 640 / md 768 / lg 1024 / xl 1280 |

### Light/dark por tokens (no por CSS duplicado)

Se hace **en la capa semántica**, no en cada componente: `color-surface` → `gray-50` en claro, `gray-900` en oscuro. El componente solo referencia `color-surface` y funciona en ambos temas sin código extra. Nunca hardcodear `#fff` en un componente: eso rompe el dark mode y no se puede retematizar. Verificar que **cada par texto/fondo en AMBOS temas** pase el contraste de §7.

### Del token al código

| Destino | Cómo aterriza el token |
|---|---|
| **CSS puro** | Custom properties: `:root { --color-action-primary: #3B82F6 }`; dark mode con `:root[data-theme="dark"]` o `@media (prefers-color-scheme: dark)` |
| **Tailwind** | En `theme.extend` (colors, spacing, borderRadius, fontSize…); Tailwind ya trae escala base de 4px (`spacing-1`=4px, `-4`=16px, `-8`=32px) y type scale (12/14/16/18/20/24/30/36…) — extenderla, no pelearla |
| **React/componentes** | Tokens como objeto JS/TS o CSS vars consumidas por el componente; nunca literales de color dentro del JSX |
| **Multiplataforma** | Herramienta tipo Style Dictionary transforma UN JSON de tokens a CSS, iOS, Android, etc. — evita mantener el valor en 3 sitios [ver: herramientas-handoff] |

Regla: el token se define **una vez** y se transforma; si el mismo `#3B82F6` aparece tecleado en Figma, en CSS y en Swift, no hay sistema — hay tres copias que van a divergir.

Ejemplo mínimo de los 3 tiers en CSS custom properties (el mismo componente sirve claro y oscuro sin código extra):

```css
:root {
  /* 1. primitivos: valores crudos, sin uso */
  --blue-500: #3B82F6;  --gray-50: #F9FAFB;  --gray-900: #111827;  --space-4: 16px;
  /* 2. semánticos: intención; aquí vive el tema */
  --color-action-primary: var(--blue-500);
  --color-surface: var(--gray-50);
  --color-text: var(--gray-900);
}
:root[data-theme="dark"] {
  --color-surface: var(--gray-900);
  --color-text: var(--gray-50);   /* solo se reasigna la capa 2 */
}
/* 3. el componente consume SOLO semánticos + escala */
.btn-primary { background: var(--color-action-primary); padding: var(--space-4); }
.card        { background: var(--color-surface); color: var(--color-text); }
```

En Tailwind es el mismo modelo en `theme.extend.colors`: define `action.primary` apuntando a la escala y usa `dark:` para reasignar la capa semántica — nunca literales de color en el JSX.

## 3. Escalas concretas (los números)

No inventar valores por pantalla — **elegir una escala fija y solo usar sus peldaños** (Refactoring UI). Los fundamentos de por qué (armonía, ritmo) están en [ver: fundamentos-visuales]; aquí, los valores operativos:

**Espaciado — base 4px / grid de 8pt** (convención dominante, base de Tailwind y Material):
`4 · 8 · 12 · 16 · 24 · 32 · 40 · 48 · 64 · 80 · 96 · 128`. Todo padding/margin/gap sale de aquí. Prohibido un `margin: 13px` suelto.

**Color — 9 tonos por color es lo ideal** (Refactoring UI: 5-10, 9 balancea bien):
- **Grises**: 8-10 tonos (el 90% de la UI es texto y superficies grises).
- **Primario**: 5-10 tonos (acciones, navegación, marca).
- **Acentos/semánticos**: éxito, aviso, error, info — cada uno con sus tonos para fondo/borde/texto.
- **No** generar tonos al vuelo con `lighten()/darken()` del preprocesador: da resultados inconsistentes. Definir la escala completa a mano/con herramienta.

**Tipografía — escala modular**: p. ej. `12 · 14 · 16 · 18 · 20 · 24 · 30 · 36 · 48 · 60` (Tailwind default). Body ≥16px en móvil (evita zoom en iOS). Line-height y peso también tokenizados por estilo (display/heading/body/caption).

**Radios**: `0 · 4 · 8 · 12 · 16 · full`. **Elevación/sombra**: 4-5 niveles (sm→xl), consistentes con la jerarquía de z-index.

## 4. Componentes y sus estados: la máquina de estados es el componente

Un componente sin todos sus estados **no está terminado** — está a medias y va a fallar en producción. Definir cada estado ANTES de dar el componente por listo:

| Estado | Cuándo | Qué debe pasar (producto/app) |
|---|---|---|
| **Default / enabled** | Reposo | Apariencia base, claramente accionable (affordance) |
| **Hover** | Puntero encima (solo mouse) | Feedback sutil; **no** es la única señal de que algo es clicable (móvil no tiene hover) |
| **Focus** | Foco de teclado/lector | Anillo de foco **visible y con contraste ≥3:1** (WCAG 1.4.11); nunca `outline:none` sin reemplazo |
| **Active / pressed** | Durante el click/tap | Feedback inmediato (<100ms); confirma que el input llegó |
| **Disabled** | No accionable ahora | Atenuado + `cursor:not-allowed`; **explicar por qué** si no es obvio; no baja del 3:1 si transmite info |
| **Loading** | Acción en curso | Spinner/estado en el propio botón; **deshabilitar para evitar doble submit**; >1s = indicador obligatorio [ver: interaccion-microux] |
| **Error** | Validación/acción falló | Mensaje claro en lenguaje humano + cómo recuperarse; el error nunca **solo** por color rojo (WCAG 1.4.1) |
| **Empty** | Sin datos aún | No un panel en blanco: decir qué es y cómo llenarlo; resolver valores dinámicos con default, nunca un "—" gigante |
| **Selected / checked / expanded** | Toggles, tabs, acordeones | El cambio de estado con contraste ≥3:1, no solo un cambio de hue |

**Biblioteca base para un producto (el mínimo):** Button (primary/secondary/ghost/destructive), Input/TextField, Select, Checkbox/Radio, Toggle, Card, Modal/Dialog, Toast/Snackbar, Tabs, Tooltip, Badge/Tag, Avatar, Table/List, Nav (top/side), Skeleton/Spinner, Empty state. Cada uno con la tabla de estados de arriba.

**State layers (Material 3):** M3 modela hover/focus/pressed/dragged como una **capa semitransparente del color de estado** superpuesta al componente, en vez de definir un color nuevo por estado. Patrón útil para no multiplicar tokens; los porcentajes exactos de opacidad se consultan en la doc de M3 (NO VERIFICADO aquí, no citar de memoria).

El feedback de estado en juegos (game-feel, juiciness) es más agresivo y vive en [ver: gamedev/game-feel]; en producto se prioriza claridad y calma.

## 5. Atomic Design (Brad Frost) — a nivel práctico

Metodología para pensar la jerarquía del sistema, tomada de la química. **No es lineal**: es un modelo mental para moverse entre lo abstracto y lo concreto.

| Nivel | Definición (Frost) | En un producto real | Mapea a |
|---|---|---|---|
| **Átomos** | Bloques básicos irreducibles (label, input, button) | Un botón, un input, un ícono, un token | Tokens + elementos HTML |
| **Moléculas** | Grupos simples de átomos que funcionan como unidad | Un campo de búsqueda (label + input + botón) | Componentes pequeños |
| **Organismos** | Secciones UI complejas de moléculas/átomos | Un header (logo + nav + búsqueda) | Componentes compuestos |
| **Plantillas** | Layout a nivel página, estructura de contenido con placeholders | El esqueleto de "página de producto" | Patrones de layout |
| **Páginas** | Instancia con contenido real; testea el sistema | La página con datos reales | Pantalla final |

Uso operativo para dev solo: **no montes los 5 niveles como carpetas ceremoniosas**. Sirve para dos decisiones: (1) ¿esto es un átomo reutilizable o un one-off de esta página? (2) ¿lo que repito es un componente (pieza) o un patrón (composición)? Ver §6.

## 6. Patrones vs componentes: cuándo documentar un patrón

- **Componente** = una pieza reutilizable con su API y estados (Button, Modal).
- **Patrón** = una **forma recomendada de combinar** componentes para un problema recurrente (validación de formularios, confirmación de acción destructiva, paginación, búsqueda con filtros, empty→loading→error→success de una lista).

Documentar un patrón cuando: el mismo problema se resuelve en ≥3 lugares y hay una forma correcta y varias incorrectas. El patrón captura la **decisión de UX** (dónde va el mensaje de error, cuándo se deshabilita el submit, qué pasa en el estado vacío) que ningún componente suelto impone. Jakob's Law lo respalda: **la gente espera que los patrones se comporten como en las apps que ya usa** — documentar el patrón estándar evita que cada pantalla lo reinvente distinto [ver: patrones-ui].

## 7. Accesibilidad: horneada en el sistema, no parcheada al final

Si los tokens y componentes nacen accesibles, todo el producto lo hereda. Números **verificados contra WCAG 2.2** (fuente primaria w3.org):

| Regla | Valor exacto | SC | Nivel |
|---|---|---|---|
| Contraste texto normal | **≥ 4.5:1** | 1.4.3 | AA |
| Contraste texto grande (≥18pt/≈24px, o ≥14pt/≈18.66px bold) | **≥ 3:1** | 1.4.3 | AA |
| Contraste texto (mejorado) | 7:1 normal / 4.5:1 grande | 1.4.6 | AAA |
| Contraste **no-textual** (bordes de controles, íconos, estado, **anillo de foco**) | **≥ 3:1** contra el color adyacente | 1.4.11 | AA |
| **Target táctil mínimo** | **≥ 24×24 CSS px** (o <24 con separación: un círculo de 24px de diámetro centrado no toca otro target) | 2.5.8 | AA |
| Target táctil (mejorado) | **≥ 44×44 CSS px** | 2.5.5 | AAA |
| No usar **solo color** para transmitir información | forma/ícono/texto además del color | 1.4.1 | A |

**Objetivos táctiles por plataforma (guidelines de origen):** Apple HIG recomienda **44×44 pt**; Material Design 3 / Android recomiendan **48×48 dp** (confirmado en Android Accessibility: "al menos 48dp"). Regla operativa: WCAG 2.2 exige 24px como piso legal, pero para dedos apunta a **44-48** y sepáralos. La thumb zone y el detalle móvil viven en [ver: mobile-ux]. La accesibilidad completa (lectores de pantalla, ARIA, teclado, reduced-motion) en [ver: accesibilidad].

Consecuencia para el sistema: un token de "texto secundario gris claro sobre blanco" que dé 3.8:1 es un **bug del sistema**, no una decisión estética — falla en todas las pantallas a la vez. Validar los pares de tokens al definirlos.

## 8. Sistemas de referencia: qué robar de cada uno (sin clonarlos)

No copiar un sistema entero: son enormes y opinan sobre marcas que no son la tuya. Aprender el **principio**, adaptar el valor.

| Sistema | Origen / plataforma | Qué aprender | Qué NO hacer |
|---|---|---|---|
| **Material Design 3** | Google, web + Android | Tokens en 3 tiers (ref/sys/component), color roles semánticos, dynamic color, state layers, elevación tokenizada | Copiar su look "Google" en un producto que no es Android; heredar su densidad |
| **Apple HIG** | Apple, iOS/macOS | Respeto por convenciones de plataforma, claridad > decoración, Dynamic Type, targets 44pt, jerarquía por tipografía | Usar componentes iOS en web y romper la expectativa de plataforma |
| **Shopify Polaris** | Shopify, apps de negocio web | Tokens semánticos bien nombrados, patrones de producto (tablas, formularios densos, empty states), tono de contenido | Su estética admin específica |
| **IBM Carbon** | IBM, enterprise/data | Grid 2x, escala de espaciado token-izada, rigor de accesibilidad, densidad para data-heavy | Su seriedad enterprise en un producto consumer/casual |
| **Atlassian / GitHub Primer** | web SaaS | Documentación de componentes con estados y do/don't, tokens públicos | — |

Lección transversal: **todos** separan primitivos de semánticos, documentan estados, y tratan la accesibilidad como requisito, no adorno. Eso es lo que se copia; los hex, no.

## 9. Nomenclatura y documentación: el mínimo viable para un dev solo

**Naming (semántico > descriptivo):** `color-action-primary`, no `color-blue`. `space-inset-md`, no `space-16`. El nombre dice **para qué**, no **qué es** — así cambiar el valor no obliga a renombrar. Convención consistente: `categoría-rol-variante-estado` (`button-primary-bg-hover`).

**Documentación mínima (no un sitio de 100 páginas):**

| Artefacto | Contenido | Herramienta ligera |
|---|---|---|
| **tokens.json / theme.ts** | La fuente única de tokens | Un archivo en el repo |
| **Página/archivo de componentes** | Cada componente con sus estados y cuándo usarlo | Storybook, o un `/kitchen-sink` propio que renderice todo |
| **Reglas de uso** | Do/don't por componente crítico + los patrones (§6) | README o comentarios |
| **Changelog** | Qué cambió y por qué (los tokens son API: rómpelos con cuidado) | El propio git |

Para dev solo la clave es **que exista y esté versionado con el código**, no que sea bonito. Un `theme.ts` + un Storybook (o página kitchen-sink) que muestre todos los estados ya es un design system funcional.

## 10. Consistencia vs flexibilidad: cuándo (y cómo) romper el sistema

Un sistema demasiado rígido mata productos; uno sin reglas no es sistema. Criterio:

- **Consistencia por defecto**: si el sistema resuelve el caso, úsalo tal cual. Cada desviación es deuda.
- **Romper el sistema** solo cuando: (a) el patrón estándar mide peor en un test real, (b) es un momento de marca deliberado (landing, onboarding hero), o (c) el sistema aún no cubre ese caso. Nunca "porque me aburrí del botón".
- **Cómo romperlo bien**: si la excepción se repite, **promuévela a token/componente** (deja de ser excepción). Si es única, aíslala y documenta por qué. La regla de oro de Refactoring UI aplica: elegir de una escala fija reduce decisiones (Hick's Law) y evita el drift; salirse de la escala debe ser un acto consciente y raro.
- **Densidad y contexto**: un producto de datos (dashboard, admin) tolera más densidad que una app consumer — el sistema puede tener modos (comfortable/compact), pero siguen siendo tokens, no valores sueltos.

## Reglas prácticas

1. Empieza por **tokens + 5-8 componentes base**, no por un sistema de 200 piezas; el ROI llega a escala, no en la pantalla 1.
2. Tres tiers de tokens: primitivos → **semánticos** → (opcional) componente. Los componentes consumen SOLO semánticos.
3. Nombra por intención (`color-action-primary`), nunca por apariencia (`color-blue`).
4. Un valor se define **una vez** y se transforma a cada plataforma; el mismo hex tecleado en 3 sitios no es sistema.
5. Elige escalas fijas y usa solo sus peldaños: espaciado base 4px (`4·8·12·16·24·32·48·64`), 9 tonos por color (Refactoring UI), type scale modular. Cero valores sueltos.
6. Light/dark en la capa semántica; jamás hardcodear `#fff` dentro de un componente.
7. Un componente no está listo hasta tener default/hover/focus/active/disabled/loading/error/empty definidos.
8. Anillo de foco **visible siempre**, contraste ≥3:1; nunca `outline:none` sin reemplazo (WCAG 1.4.11).
9. Contraste: texto normal ≥4.5:1, texto grande ≥3:1, no-texto/íconos/bordes ≥3:1 (WCAG 2.2 AA). Valida cada par de tokens en ambos temas.
10. Target táctil: piso legal 24×24 CSS px (WCAG 2.5.8); para dedos apunta a 44pt (Apple) / 48dp (Material) y sepáralos.
11. Nunca transmitir estado/error solo por color: color + ícono/forma/texto (WCAG 1.4.1).
12. Estado de carga en el propio botón + deshabilitar para evitar doble submit; loading >1s = indicador.
13. Empty states con contenido y acción, no paneles en blanco ni "—" gigantes.
14. Documenta un **patrón** cuando el mismo problema se resuelve en ≥3 sitios con una forma correcta y varias malas.
15. Trata los tokens como API: cámbialos con changelog; renombrar/borrar un token es un breaking change.
16. Roba principios de Material/HIG/Polaris/Carbon (separación de tiers, estados, a11y), nunca sus hex ni su estética.
17. Respeta la convención de plataforma (Jakob's Law): la app debe comportarse como las que el usuario ya usa.
18. Documentación mínima real: `theme.ts` + Storybook/kitchen-sink que renderice TODOS los estados, versionado en el repo.
19. Consistencia por defecto; romper el sistema solo con evidencia o marca deliberada, y si la excepción se repite, promuévela a token.
20. Menos opciones = decisión más rápida (Hick's Law): limitar variantes de cada componente evita el menú infinito.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Confundir "una paleta en Figma" con un design system | Sistema = tokens + componentes + patrones + código sincronizado + docs (def. NN/g); lo demás es una parte |
| Componentes que consumen tokens primitivos (`blue-500`) directo | Consumir la capa semántica; retematizar cambiando solo los alias, sin tocar componentes |
| El mismo `#3B82F6` tecleado en Figma, CSS y Swift | Token único transformado por plataforma (Style Dictionary); una fuente de verdad |
| `margin: 13px` y colores al vuelo con `lighten()` | Escala fija de espaciado (base 4px) y de color (9 tonos definidos a mano) — Refactoring UI |
| Componente "listo" con solo el estado default | Máquina de estados completa antes de dar por hecho: hover/focus/active/disabled/loading/error/empty |
| `outline:none` en focus por estética | Anillo de foco visible con contraste ≥3:1 (WCAG 1.4.11); reemplazar, nunca eliminar |
| Depender de hover para señalar clicabilidad | Móvil no tiene hover; la affordance debe existir en default |
| Texto gris claro que da 3.8:1 "porque se ve fino" | Es un bug del sistema: ≥4.5:1 texto normal (WCAG 1.4.3); valida el par de tokens |
| Error/estado solo en rojo | Color + ícono + texto (WCAG 1.4.1); no todos ven el hue |
| `#fff` hardcodeado en componentes | Token semántico (`color-surface`) resuelto por tema; sin eso no hay dark mode |
| Targets de 20px pegados unos a otros | ≥24px o separación de 24px-círculo (WCAG 2.5.8); apuntar a 44-48 para dedos |
| Clonar Material entero en un producto que no es Android | Robar el principio (tiers, estados, a11y), adaptar los valores a la marca propia |
| Sistema tan rígido que el equipo lo evita | Modos (comfortable/compact) por token; permitir excepción documentada y promoverla si se repite |
| Design system sin documentación viva | `theme.ts` + Storybook/kitchen-sink versionado; si nadie ve los estados, divergen |
| Renombrar/borrar tokens sin avisar | Los tokens son API: changelog y deprecación, no borrado silencioso |

## Fuentes

- **"Design Systems 101" — Nielsen Norman Group (nngroup.com)** — definición canónica ("estándares para gestionar el diseño a escala con componentes y patrones reutilizables") y las distinciones design system / style guide / component library / pattern library; beneficios y costos reales del §1.
- **Design Tokens Community Group — designtokens.org (glosario W3C)** — definición oficial de design token ("fuente única de verdad para nombrar y almacenar una decisión de diseño"), conceptos de alias y composite token que fundamentan los tiers del §2.
- **"Atomic Design" — Brad Frost (atomicdesign.bradfrost.com, cap. 2)** — los 5 niveles (átomos→moléculas→organismos→plantillas→páginas) con definición y ejemplo de cada uno; "no es un proceso lineal" (§5).
- **WCAG 2.2 — W3C Web Accessibility Initiative (w3.org/WAI)** — números verificados contra la fuente primaria: SC 1.4.3 (4.5:1 / 3:1, def. de texto grande 18pt·24px / 14pt·18.66px bold), 1.4.6 (7:1 AAA), 1.4.11 non-text 3:1, 2.5.8 target 24×24 CSS px + excepción de separación, 2.5.5 target 44×44 CSS px, 1.4.1 no solo color (§4, §7).
- **Refactoring UI — Adam Wathan & Steve Schoger (refactoringui.com)** — construir la paleta con 5-10 tonos (9 ideal), grises 8-10, primario 5-10; escala fija en vez de `lighten()/darken()` al vuelo (§3); jerarquía y disciplina de escalas.
- **Laws of UX — Jon Yablonski (lawsofux.com)** — Hick's (menos opciones = decisión más rápida), Jakob's (esperan las convenciones de otras apps), Tesler's (complejidad irreducible), Fitts's, Miller's, Doherty — principios que justifican consistencia, límite de variantes y patrones estándar (§1, §6, §10).
- **Material Design 3 — Google (m3.material.io)** — modelo de tokens en 3 tiers (reference/system/component), color roles, state layers, elevación tokenizada; touch target 48dp (§2, §4, §8). Nota: la doc es SPA; el 48dp está confirmado vía Android Accessibility Help (support.google.com — "al menos 48dp").
- **Apple Human Interface Guidelines — Apple (developer.apple.com/design)** — target táctil 44×44 pt, claridad sobre decoración, Dynamic Type, respeto de convención de plataforma (§7, §8). Cifra 44pt consistente con la base de conocimiento del estudio [ver: gamedev/ux-ui-onboarding].
- **Shopify Polaris & IBM Carbon (polaris.shopify.com, carbondesignsystem.com)** — ejemplos de sistemas maduros: tokens semánticos nombrados por intención, patrones de producto, escala de espaciado token-izada, rigor de accesibilidad y densidad para data-heavy (§8).
