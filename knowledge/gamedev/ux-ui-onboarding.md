# UX, UI y Onboarding

> **Cuando cargar este archivo:** al diseñar o implementar HUD, menús, flujo de pantallas, tutoriales/FTUE, settings, accesibilidad o feedback de estado (loading/save/errores) en cualquier juego — especialmente antes de escribir la primera pantalla de UI o el primer paso de tutorial.

## 1. HUD: taxonomía y jerarquía de información

### Los 4 tipos de UI (Fagerholt & Lorentzon, "Beyond the HUD", Chalmers 2009)

Dos ejes: **ficción** (¿el personaje del mundo lo percibe?) y **geometría** (¿vive en el espacio 3D del juego o en overlay 2D?).

| Tipo | Ficción | Geometría | Ejemplo real |
|---|---|---|---|
| **Diegético** | Sí | Mundo 3D | Dead Space (salud en la espina del traje), Metro 2033 (reloj del personaje para la máscara de gas), mapa físico de Far Cry 2 |
| **No diegético** | No | Overlay 2D | HUD clásico: barras, minimapa, contador de munición (World of Warcraft, TF2) |
| **Espacial** | No | Mundo 3D | Siluetas de aliados en Left 4 Dead, camino brillante de Fable 3 |
| **Meta** | Sí | Overlay 2D | Sangre en pantalla como indicador de daño (Call of Duty) |

**Lección de Marcus Andrews (EA DICE, "Game UI Discoveries")**: la preservación de la **función va antes que la estética/inmersión**. Dead Space logra UI 100% diegética pero sin ventaja funcional real; Team Fortress 2 mezcla todos los tipos sin pudor y prioriza claridad; los jugadores de WoW valoran información y rendimiento por encima de inmersión visual. Elegir diegético solo cuando NO cueste legibilidad.

### Qué mostrar siempre vs bajo demanda (heurística práctica)

| Nivel | Criterio | Ejemplos |
|---|---|---|
| **Permanente** | Afecta decisiones segundo a segundo | Salud, munición/recurso activo, objetivo actual, timer si aplica |
| **Contextual** | Solo cuando es relevante | Prompt de interacción al acercarse, daño recibido, pickup obtenido, aviso de recarga |
| **Bajo demanda** | El jugador lo pide (botón/menú) | Mapa completo, inventario, stats, quest log, controles |

- Heurística: cada elemento permanente del HUD compite por atención — si no cambia una decisión inmediata, degradarlo a contextual o bajo demanda. Muchos juegos hacen fade-out del HUD cuando la info no es relevante (patrón común; calibrar por género: un shooter competitivo tolera más densidad que una aventura narrativa).
- Framework de Hodent (The Gamer's Brain): toda pieza de UI es un **sign** con uno de 3 roles — informar estado (barra de vida), invitar a la acción (save point brillando) o dar feedback (puerta que indica "cerrada"). Si un elemento no cumple ninguno, sobra.
- Permitir mover/escalar elementos del HUD y ocultarlo es un plus de accesibilidad y de capturas (checklist de settings de Game Developer).

## 2. Flujo de pantallas y menús

### Flujo estándar

```
Boot/splash → Title → (selección de save/perfil) → Gameplay ⇄ Pause → Results/Game Over → Title
                 ↘ Settings (accesible desde Title Y desde Pause, con las mismas opciones)
```

| Pantalla | Debe tener |
|---|---|
| **Title** | Play/Continue prominente (Continue primero si hay save), Settings, salir. Empezar a jugar sin navegar múltiples niveles de menú (guideline cognitiva de GAG) |
| **Pause** | Resume, Settings, Restart (si aplica), salir con confirmación. Pausar de verdad: simulación + contexto de input (abrir menú = desactivar input de gameplay; cerrar = reactivarlo, sin inputs residuales) |
| **Settings** | Ver sección 7. Accesible ANTES de empezar a jugar y durante el gameplay |
| **Results** | Resultado claro, recompensas, y las dos salidas obvias: retry/next y volver. Tras derrota, resaltar progreso personal reduce frustración (patrón de Overwatch citado por Hodent) |

### Navegación con mando/teclado (Figma "Press Start" + Xbox Accessibility Guideline 112)

- **Siempre hay exactamente un elemento con focus visible.** Al abrir cualquier pantalla o popup, mover el focus explícitamente al primer elemento lógico — nunca dejar el focus "en nada".
- **Back universal**: B (Xbox) / círculo (PS) / Esc (PC) retrocede un nivel, en TODAS las pantallas. La convención es tan fuerte que muchos juegos ni muestran botón de "atrás" en pantalla.
- **Tabs con shoulder buttons** (LB/RB) para secciones principales; LT/RT para páginas. Mecánica de interacción consistente en todo el juego ("A selecciona, B vuelve") — cambiarla entre pantallas desorienta (XAG 112).
- **Focus order lógico**: sigue el layout visual; en menús lineales (solo vertical u horizontal), el focus hace **loop** del último al primer elemento; en grillas 2D navegables en 4 direcciones, NO hacer loop (XAG 112).
- **Posición inicial del focus**: cerca del centro/acción principal, no obligatoriamente la esquina superior izquierda (Figma) — reduce fricción para alcanzar todo.
- Elementos repetidos entre pantallas (título, prompts de botones) siempre en la misma posición y el mismo orden de lectura.
- UI 100% navegable con **input digital solo** (D-pad/teclado sin ratón) y con ratón si la plataforma lo tiene; detectar cambio dinámico teclado↔mando y actualizar los glifos de botones.
- Listas/colecciones grandes (inventario, bestiario): más de una vía de acceso — tabs de filtro + búsqueda (ejemplo: inventario de Minecraft, XAG 112).
- Menús multipágina: link persistente de vuelta al menú principal desde cualquier submenú.
- En PC, los menús se manejan con ratón aunque el gameplay no lo use (checklist de Game Developer): soportar hover + click además de teclado.
- **Touch**: no hay focus — targets grandes (sección 6), y todo lo alcanzable por gesto también alcanzable por tap simple.

## 3. Onboarding y tutoriales

### Tipos de tutorial

| Tipo | Qué es | Cuándo usarlo |
|---|---|---|
| **Contextual** | Tips en el momento exacto en que la mecánica es relevante | Default para casi todo; mínima interrupción |
| **Guiado (step-by-step)** | Secuencia dirigida con pasos obligados | Solo mecánicas complejas/no estándar; F2P con funnel instrumentado |
| **Sandbox / discovery** | Espacio seguro donde experimentar sin castigo | Juegos de sistemas; primeras zonas "fail-safe" |
| **Adaptativo** | Ayuda solo a quien se equivoca | El mejor de todos cuando se puede: quien lo hace bien nunca ve el tip y se siente listo (George Fan) |
| **Ambiental** | El level design enseña sin texto | Siempre que se pueda [ver: level-design] |

### Los 10 principios de George Fan (GDC 2012, "How I Got My Mom to Play Through Plants vs. Zombies")

1. Que no se sienta tutorial — nunca llamarlo "tutorial".
2. **Aprender haciendo**, no leyendo: el nivel 1 enseña "plantas disparan a la derecha, zombis vienen de la izquierda" jugándolo.
3. Dosificar mecánicas: PvZ no introduce ni el dinero hasta el nivel 10.
4. Basta con que el jugador haga la acción UNA vez y vea el resultado (la moneda con flecha gigante).
5. **Máximo ~8 palabras en pantalla** a la vez.
6. Mensajes no intrusivos: texto pasivo, sin pausar el juego.
7. Mensajes adaptativos: el tip solo aparece si el jugador se está equivocando.
8. Cero ruido: cada mensaje debe esclarecer o entretener, o es "el pastorcito mentiroso".
9. El diseño visual enseña: el Peashooter tiene boca gigante = dispara; el Screen-Door Zombie lleva su escudo visible.
10. Apoyarse en conocimiento previo: plantas = inmóviles, zombis = lentos, moneda = valor. No inventar convenciones si existe una universal.

### Qué odian los jugadores (FontsArena + Hacker News + Hodent)

- La paradoja: **~74% dice odiar los tutoriales, pero en A/B testing los juegos con buen tutorial retienen 3-5x más** (cifras reportadas por FontsArena). No odian aprender — odian **sentirse estúpidos** y que los traten como si no supieran aprender.
- Antipatrones concretos: tutoriales no salteables; forced learning (popups paso a paso, menús griseados, cutscenes obligatorias antes de poder jugar); asumir que todo jugador es novato (un veterano que reinicia en difícil no debe tragarse el walkthrough básico); bloquear el juego "de verdad" durante horas.
- **Un tutorial único al inicio no basta**: Hodent (datos de Paragon, Epic) encontró que la falta de competencia era el factor #1 de abandono, y que las mecánicas críticas necesitan refuerzo iterativo a lo largo de las primeras sesiones. "Ser competente en el juego impacta directo la retención."
- El tutorial ideal: salteable (u opcional), contextual, con zonas tempranas donde fallar no castiga, y que haga sentir al jugador inteligente por descubrir — no obediente por seguir instrucciones.

## 4. FTUE: los primeros 5 minutos deciden la retención

Números de la industria móvil (Mistplay, GameAnalytics, Udonis — 2024-2026):

- **~77% de los usuarios abandona una app el primer día.** D1 retention promedio ronda **24%** (rango típico 20-40%). D1 es el techo de todas las métricas posteriores.
- **Demostrar el valor del juego en 2-3 minutos** (GameAnalytics). Roblox lo formula igual: "get to the fun quickly" — el jugador decide en minutos.
- El FTUE es un **funnel instrumentado**: trackear cada paso del tutorial y medir dónde se cae la gente. Sin funnel no hay diagnóstico. [ver: psicologia-retencion-negocio]

Reglas operativas (GameAnalytics + Roblox + Udonis):

1. **Cero fricción al abrir**: nada de crear cuenta, popup de IAP o ad antes de jugar. Al gameplay lo antes posible.
2. **Early wins**: recompensas y refuerzo positivo en los primeros minutos; progresión rápida al inicio (umbrales de XP bajos, level-ups frecuentes).
3. **Open loops**: cerrar el primer objetivo-recompensa y abrir el siguiente inmediatamente, cada uno un poco más largo.
4. Enseñar el potencial: mostrar qué se puede desbloquear (personajes, poderes) aunque tome tiempo llegar.
5. **Personalización temprana** (avatar, base): crea apego emocional y sube retención.
6. Al terminar el onboarding, dejar un **objetivo claro a largo plazo** ya plantado — "leave players wanting more" (Roblox).
7. Pedir login/notificaciones/rating DESPUÉS de que el jugador ya recibió valor, nunca antes.

## 5. Accesibilidad: el checklist estándar

Fuente principal: **Game Accessibility Guidelines** (gameaccessibilityguidelines.com), nivel "Basic" = bajo costo, alto impacto. Las 4 quejas más comunes de jugadores: **remapeo, tamaño de texto, daltonismo y presentación de subtítulos** — resolver esas 4 ya cubre a la mayoría.

| Categoría | Guidelines básicas |
|---|---|
| **Motor** | Remapeo completo de controles; sensibilidad ajustable; controles simples o alternativa simple; targets grandes y espaciados en touch; toggle de vibración/haptics; la UI se maneja con el mismo input que el gameplay |
| **Visión** | Alto contraste texto/fondo; fuente legible por defecto y tamaño ajustable; **ninguna información esencial transmitida SOLO por color**; formateo de texto simple; FOV ajustable en 3D |
| **Audición** | Subtítulos de todo diálogo importante, claros y legibles (tamaño, color, opacidad de fondo ajustables); información esencial nunca solo por sonido; volúmenes separados (música/SFX/voz) |
| **Cognitivo** | Sin imágenes parpadeantes ni patrones repetitivos (fotosensibilidad); avanzar textos al propio ritmo (nunca texto auto-avanzado); lenguaje simple y claro; tutoriales interactivos; empezar a jugar sin laberinto de menús |
| **Habla** | Entrada de voz nunca obligatoria |
| **General** | Varios niveles de dificultad; guardar TODAS las configuraciones; documentar las features de accesibilidad |

Prácticas de referencia (XAG 112 / Microsoft + búsquedas 2026):

- **Accesibilidad accesible desde el primer arranque**: Minecraft Dungeons muestra el menú de accesibilidad como PRIMERA pantalla del juego (TTS, subtítulos, color de outline de enemigos). God of War Ragnarök hace un walkthrough guiado de settings en el primer boot. Alternativa: defaults ya accesibles (subtítulos ON por defecto).
- Modos de daltonismo: cubrir al menos las 3 variantes (protanopia, deuteranopia, tritanopia) o, mejor, permitir elegir los colores directamente. Nunca depender de rojo-vs-verde para info crítica.
- Escalar texto no debe obligar a scroll en dos direcciones (reflow correcto — ejemplo The Outer Worlds).
- Mapa con zoom → ofrecer también lista de texto de puntos de interés (ejemplo Halo Infinite Tacmap).

## 6. UX móvil

### Touch targets y thumb zone (UX Movement, Parachute, estudios de agarre)

- **Target mínimo: 44pt (iOS) / 48dp (Android)**; el dedo índice adulto mide 16-20 mm ≈ 45-57 px. Para acciones frecuentes de gameplay, más grande.
- **~49% de los usuarios usa el teléfono a una mano con el pulgar**; ~75% de las interacciones son con el pulgar. El **tercio inferior de la pantalla es la zona natural** del pulgar: acciones primarias abajo-centro/abajo-lados; nada crítico en las esquinas superiores ni pegado a los bordes (fundas y bezels roban precisión).
- Controles de juego (joystick virtual, botones): anclados a las esquinas inferiores, con opción de reposicionarlos y ajustar tamaño/opacidad (guideline motor de GAG: elementos grandes, espaciados y recolocables).

### Safe areas y layout

- Respetar los **safe area insets** del dispositivo (notch, isla dinámica, home indicator, esquinas redondeadas): HUD y botones nunca debajo de esas zonas. En web/PWA usar unidades `dvh`, no `vh`, para fullscreen.
- Decidir orientación temprano: portrait favorece juego a una mano y sesiones cortas; landscape favorece controles dobles. Si se soportan ambas, probar el HUD en las dos.
- Probar en dispositivos reales de varios tamaños, no solo simulador (los estudios de thumb zone insisten: medir dónde llega el pulgar de verdad).

### Interrupciones (convención de plataforma)

- El móvil vive interrumpido: llamadas, notificaciones, cambio de app, bloqueo de pantalla. Convención estándar: **auto-pausa inmediata** al perder foco + persistir estado al pasar a background, de modo que matar la app nunca pierda progreso significativo. En juegos por turnos/asincrónicos, reanudar exactamente donde quedó.
- Sesiones móviles son cortas: diseñar unidades de juego completables en pocos minutos y guardar entre unidades. [ver: generos]

## 7. Settings que todo juego debe tener

Checklist condensado (Game Developer, "Create better game settings options"):

| Categoría | Mínimo indispensable |
|---|---|
| **Video (PC)** | Resoluciones múltiples y aspect ratios; fullscreen/ventana/borderless; preset de calidad único (Low→Ultra) + ajuste individual (texturas, sombras, partículas, AA, V-Sync, límite de FPS, FOV, motion blur OFF-able); gamma |
| **Audio** | Volumen maestro + separados: música, SFX, voces, ambiente; mute rápido |
| **Controles** | Rebinding completo; invertir ejes (por dispositivo); sensibilidad X/Y separadas; reset a defaults; cambio dinámico teclado↔mando |
| **Idioma** | Selección de idioma; idioma de subtítulos independiente del de audio |
| **Accesibilidad** | Ver sección 5 — idealmente menú propio, con **preview en vivo** del efecto (ej. tamaño de subtítulo visible al ajustarlo) |
| **Gameplay** | Toggle de hints/tutorial; dificultad cambiable (donde el diseño lo permita); screen shake y flashes OFF-able |
| **UX del propio menú** | Ajustable ANTES de empezar a jugar y DESDE el pause; navegable con ratón, teclado y mando; confirmación antes de descartar cambios sin guardar; persistir todo |

Regla de oro: **cada setting se guarda y se restaura siempre** (GAG general). Un setting que se resetea al reiniciar es un bug de confianza.

## 8. Feedback de estado: nunca dejar al jugador ciego

Principio (Hodent): el jugador necesita saber en todo momento **qué pasó, qué está pasando y qué puede hacer**. Todo input merece feedback [ver: game-feel].

### Loading (Apple HIG + Pencil & Paper)

- < 1 segundo: no hace falta indicador. Más de eso: indicador obligatorio.
- Duración estimable → **barra determinada** (inicio y fin); desconocida → spinner/indeterminado, pero nunca uno que pueda congelarse sin que se note.
- Skeleton screens / arte / tips durante la carga reducen la espera percibida. Un loading largo con pantalla negra muda se percibe como cuelgue.

### Guardado (GitLab Pajamas + datacalculus + convención de consolas)

- Autosave con **indicador visible** ("Saving…" + spinner mientras ocurre; "Saved" al terminar). La confirmación visual inmediata construye confianza; sin ella el jugador no sabe si debe hacer algo más.
- Convención de consola: icono de autosave animado + aviso "no apagues la consola mientras se guarde" en el primer arranque.
- Autosave + save manual conviven: el autosave reduce ansiedad, el manual da control. Indicar SIEMPRE cuándo fue el último guardado en el slot (timestamp, ubicación, progreso).
- Nunca sobrescribir el único save sin confirmación; ante corrupción, conservar el backup anterior.

### Errores y estados vacíos

- Hodent: ayudar a **prevenir** el error primero (confirmaciones en acciones destructivas, greying-out con explicación); si ocurre, mensaje claro en lenguaje de jugador + **camino de recuperación** (retry, volver al menú) — nunca un código pelado ni un freeze.
- Desconexión en multiplayer: avisar al instante, intentar reconexión visible, y dejar claro qué pasó con la partida.
- Estados vacíos (sin partidas guardadas, sin items): mostrar qué hacer para llenarlos, no un panel en blanco.

## Reglas prácticas

1. Función antes que inmersión: UI diegética solo si no cuesta legibilidad (Andrews).
2. Cada elemento permanente del HUD debe justificar su atención; lo demás, contextual o bajo demanda.
3. Un elemento con focus visible SIEMPRE en menús de mando/teclado; al abrir popup, mover el focus explícitamente.
4. B/círculo/Esc = atrás, en todas las pantallas, sin excepción; A/X = confirmar, consistente todo el juego.
5. Menús lineales hacen loop; grillas 2D no (XAG 112).
6. Tutorial: máximo ~8 palabras en pantalla; enseñar haciendo, una acción con resultado visible vale más que un párrafo (Fan).
7. Tips adaptativos: mostrar ayuda solo a quien se equivoca; el que acierta nunca la ve.
8. Nunca tutorial no salteable ni forced learning con menús griseados; refuerzo iterativo en las primeras sesiones, no un dump inicial.
9. FTUE: valor demostrado en 2-3 minutos; cero cuentas/paywalls/ads antes del primer momento de diversión.
10. Instrumentar el funnel del tutorial paso a paso desde el día 1; D1 retention es el techo de todo lo demás.
11. Las 4 prioridades de accesibilidad: remapeo completo, texto escalable, subtítulos configurables, nada crítico solo por color.
12. Subtítulos ON por defecto; volúmenes música/SFX/voz separados; sin flashes ni patrones parpadeantes.
13. Settings accesibles antes de empezar a jugar Y desde el pause; todo setting persiste siempre.
14. Móvil: targets ≥44pt/48dp, acciones primarias en el tercio inferior, nada crítico en esquinas superiores ni bajo el notch/home indicator.
15. Móvil: auto-pausa al perder foco y persistir estado en background; matar la app no puede perder progreso.
16. Loading >1s = indicador; duración conocida = barra determinada; loading largo sin señal de vida = percepción de cuelgue.
17. Autosave con indicador visible y save manual conviviendo; nunca sobrescribir el único save sin confirmar.
18. Todo error da mensaje claro + camino de recuperación; toda acción destructiva pide confirmación.
19. Pausar = pausar de verdad: simulación + contexto de input, sin inputs residuales al cerrar el menú.
20. Probar la UI con mando solo, con teclado solo, y en touch con una mano en dispositivo real.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| UI diegética "porque es cool" que sacrifica legibilidad | Preservar función primero; TF2/WoW demuestran que los jugadores prefieren información clara (Andrews) |
| HUD saturado: todo permanente "por si acaso" | Tiers: permanente/contextual/bajo demanda; cada elemento debe pagar su renta de atención |
| Focus perdido al abrir un popup con mando (el jugador aprieta y no pasa nada) | Mover el focus explícitamente al primer elemento de cada pantalla/popup nuevo |
| Cambiar el mapeo de botones entre pantallas (A confirma aquí, B confirma allá) | Mecánica de interacción idéntica en todo el juego (XAG 112) |
| Tutorial-muro: 10 popups de texto antes de tocar el juego | Aprender haciendo, dosificar mecánicas (PvZ no muestra dinero hasta el nivel 10), contextual en el momento relevante |
| Tutorial no salteable que asume novato universal | Salteable/opcional siempre; detectar competencia (adaptativo) en vez de imponer el walkthrough |
| Un solo tutorial al inicio y nunca más reforzar | Refuerzo iterativo: la falta de competencia fue el driver #1 de churn en Paragon (Hodent) |
| Pedir cuenta/notificaciones/rating antes del primer momento de diversión | Todo pedido de permiso va DESPUÉS de entregar valor |
| Información crítica solo por color (rojo=enemigo, verde=aliado) | Color + forma/icono/outline; modos de daltonismo o colores elegibles |
| Texto de diálogo que avanza solo | El jugador avanza los textos a su propio ritmo (GAG cognitivo) |
| Botones de juego móvil pegados a bordes o bajo el notch | Safe area insets + targets en la thumb zone; opción de reposicionar controles |
| Autosave silencioso (el jugador no sabe si guardó y repite la misión) | Indicador "Saving…/Saved" + timestamp del último save visible en el slot |
| Pantalla negra durante cargas largas | Indicador de progreso + tips/arte; skeleton screens reducen la espera percibida |
| Settings que no persisten o solo accesibles in-game | Guardar todo siempre; menú de settings disponible desde el title screen (ideal: prompt de accesibilidad en el primer boot, como Minecraft Dungeons) |
| Escalar el texto rompe el layout (scroll en 2 direcciones) | Reflow del contenido al escalar (ejemplo: The Outer Worlds) |
| "Botones muertos": elementos visibles sin acción implementada | Todo lo visible funciona o no se muestra; ocultar features incompletas |

## Fuentes

- **"How I Got My Mom to Play Through Plants vs. Zombies" — George Fan, GDC 2012 (via Game Developer/Gamasutra)** — los 10 principios de tutorial más citados de la industria; la regla de las 8 palabras y los mensajes adaptativos salen de aquí.
- **"Beyond the HUD: User Interfaces for Increased Player Immersion in FPS Games" — Erik Fagerholt & Magnus Lorentzon, tesis Chalmers 2009** — origen de la taxonomía diegetic/non-diegetic/spatial/meta que usa toda la industria.
- **"Game UI Discoveries: What Players Want" — Marcus Andrews (EA DICE), Game Developer** — el argumento función-sobre-inmersión con análisis de Far Cry 2, Dead Space, TF2 y WoW.
- **"User Interface Design in Video Games" — Anthony Stonehouse, Game Developer** — la taxonomía aplicada con ejemplos (Metro 2033, Fable 3, CoD, WoW).
- **The Gamer's Brain / "The UX of Engagement and Immersion" — Celia Hodent, GDC 2017 + libro** — framework usability + engage-ability; signs & feedback; competencia→retención (datos de Paragon); manejo de frustración.
- **Game Accessibility Guidelines (gameaccessibilityguidelines.com), lista Basic** — el checklist de accesibilidad estándar de facto, organizado por costo/impacto; las 4 quejas principales.
- **Xbox Accessibility Guideline 112: UI Navigation — Microsoft Learn** — reglas concretas de focus order, consistencia, loop de menús, navegación digital-only, con ejemplos (Sea of Thieves, Forza Horizon 4, Minecraft Dungeons, Halo Infinite, The Outer Worlds).
- **"10 Tips for a Great First Time User Experience (FTUE) in F2P Games" — GameAnalytics** — valor en 2-3 min, funnel de tutorial, early wins, open loops, personalización.
- **"Onboarding" — Roblox Creator Hub, Game Design docs** — teach the essentials / get to the fun quickly / leave players wanting more; progresión rápida temprana; A/B testing del FTUE.
- **"Mobile game player retention" — Mistplay + FTUE guides de Udonis/Keewano** — ~77% churn día 1, D1 promedio ~24% (rango 20-40%).
- **"Press Start: How Controllers Shaped Video Game Design" — Figma Blog** — patrones de navegación con mando: focus, back universal, tabs en shoulder buttons, posición inicial del focus.
- **"Create Better Game Settings Options (Handy Checklist)" — Game Developer** — el checklist de settings por categoría de la sección 7.
- **"Why Players Hate Tutorials But Can't Play Without Them" — FontsArena** — la paradoja 74% odio / 3-5x retención (cifras reportadas por esta fuente); "no odian tutoriales, odian sentirse estúpidos"; antipatrones de forced learning.
- **UX de loading y saving — Apple HIG (Loading), Pencil & Paper (Loading Feedback patterns), GitLab Pajamas (Saving & Feedback), datacalculus (Save/Load Systems for Game UI/UX)** — umbral de 1s, determinado vs indeterminado, skeleton screens, patrón "Saving…/Saved" con confirmación visual.
- **Touch targets y thumb zone — UX Movement (Finger-Friendly Design), Parachute Design (Thumb Zone), estudios de agarre citados en ambos** — 44-48pt mínimo, dedo de 16-20mm, ~49% agarre a una mano, ~75% interacciones con pulgar, tercio inferior como zona natural.
