# Arte y dirección visual

> **Cuando cargar este archivo:** al elegir o definir el estilo visual de un juego, escribir un style guide, diseñar personajes/entornos/UI, resolver problemas de legibilidad en pantalla, o montar el pipeline de assets 2D/3D de un equipo chico.

## 1. Dirección de arte: qué es y qué decide

La dirección de arte NO es "hacer arte bonito": es garantizar que **todo lo visible comunica la misma identidad y sirve al gameplay**. Un screenshot aleatorio del juego debe ser reconocible como TU juego (Portal = azul/naranja sobre blanco clínico; Mirror's Edge = rojo sobre blanco; Hotline Miami = neón rosa).

Decisiones que fija la dirección de arte (en orden):

1. **Experiencia emocional objetivo** — antes que género o referencias. Solarski: empezar cada proyecto preguntando "¿cuál es la emoción?" y derivar formas, color y movimiento de ahí.
2. **Paleta como identidad** — 2-4 colores dominantes que dominan la mayoría de las pantallas y el key art. La paleta ES la marca.
3. **Nivel de estilización** — escala 1-10 (1 = cartoon plano, 10 = fotorrealista). Fijarlo por escrito evita drift entre assets.
4. **Lenguaje de formas** — círculo = inocencia/energía (Mario, Kirby), cuadrado = estabilidad/madurez (Luigi, tanques aliados), triángulo = agresión/peligro (Wario, Bowser, pinchos). Aplica a personajes, arquitectura, iconos de UI y hasta a las trayectorias de movimiento (Journey: personaje triangular que se mueve en arcos suaves = tensión entre forma y movimiento).
5. **Reglas de qué NO se hace** — tan importante como lo que sí. Ej. TF2: nada de outlines negros, siluetas se separan con rim light.

**Coherencia > calidad individual de assets.** Un asset "mejor pintado" que rompe la paleta o el nivel de detalle daña el juego más que uno mediocre pero coherente. Esto es lo que un agente IA generando assets tiende a romper primero: cada asset nuevo debe compararse contra el visual target, no contra "¿se ve bien solo?".

### El visual target (práctica AAA aplicable a indie)

La técnica reportada del equipo de Overwatch (GDC 2017, Bill Petras): en vez de fijar el estilo solo con documentos, modelaron a fondo UN personaje como **art target** y lo probaron dentro de un nivel jugable real para calibrar el nivel de exageración de todo lo demás — el detalle de qué héroe y qué mapa exacto viene de resúmenes de la charla, NO VERIFICADO contra el video/transcript original. El principio en sí (vertical slice de un personaje + escena para calibrar el resto) es estándar en dirección de arte AAA y replicable en indie: producir 1 escena jugable con 1 personaje + 1 entorno + UI al nivel de calidad final, EN el engine, y medir todo asset futuro contra ella.

## 2. El style guide: contenido mínimo

Documento vivo (en AAA: 20-40 páginas; para un indie/agente basta 2-5 con lo mismo comprimido):

| Sección | Contenido concreto |
|---|---|
| Pilares visuales | 3 adjetivos/frases que filtran toda decisión ("cálido, gastado, artesanal") |
| Mood board | Referencias CON callouts: qué se toma de cada una y qué NO |
| Paleta | Hex exactos, con nombre y significado por color ("rojo #D13438 = solo daño") |
| Escala de estilización | 1-10 declarado + ejemplo de juego equivalente |
| Lenguaje de formas | Formas dominantes de aliados / enemigos / entorno / UI |
| Do's & Don'ts | Pares correcto/incorrecto lado a lado (lo más útil para outsourcing y para IA) |
| Specs técnicos | Resolución de sprite / texel density, tamaño de tile, poly budget, formato de export |
| Visual target | Screenshot(s) de la escena gold-standard en engine |

Regla de oro: si dos personas (o dos sesiones de un agente) producen assets con el guide y no se distinguen de los existentes, el guide funciona.

### Runbook: definir la dirección de arte desde cero

1. Escribir la experiencia emocional objetivo en 1 frase (Solarski: la emoción antes que el género).
2. Reunir 10-20 referencias y anotar en cada una QUÉ se toma (paleta, formas, luz, densidad de detalle) y qué se descarta.
3. Derivar: 3 pilares visuales + paleta (hex) + lenguaje de formas + escala de estilización 1-10.
4. Elegir estilo con la tabla del §3 contra el equipo y tiempo reales.
5. Producir el visual target: 1 escena jugable gold-standard en engine.
6. Congelar specs técnicos (resolución/texel density, tile/poly budget, formatos).
7. Escribir do's & don'ts a partir de los primeros errores reales de producción; actualizar el guide con cada excepción aprobada.

## 3. Elegir estilo: coste real para equipos chicos

Comparativa (consolidada de guías indie + postmortems):

| Estilo | Coste | Riesgo principal | Ejemplos | Cuándo elegirlo |
|---|---|---|---|---|
| **Pixel art** | Bajo-medio | La animación escala mal: cada frame es trabajo manual; "barato" es un mito a alta fidelidad (Celeste, Stardew, Dead Cells invirtieron fuerte) | Celeste, Stardew Valley, Hyper Light Drifter | Solo dev con base 2D; resolución BAJA y consistente; menos frames bien elegidos |
| **Low-poly 3D** | Bajo-medio | Sin buena luz y color se ve a "asset store"; la geometría simple no perdona mala paleta | Journey, Poly Bridge | Querer 3D sin presupuesto AAA; la iluminación hace el 50% del look |
| **Flat / vector** | Bajo | Monotonía visual; exige diseño gráfico fuerte para no verse genérico | Monument Valley, Thomas Was Alone, Linelight | Puzzle/móvil donde la claridad manda; equipos sin ilustrador |
| **Hand-painted / hand-drawn** | Alto | Cada frame de animación es una ilustración; el estilo más caro en 2D | Cuphead, Hollow Knight, Gris | Solo con artista dedicado y scope de animación acotado |
| **3D realista** | Muy alto | Envejece rápido, exige equipo especializado y hardware; uncanny valley | The Last of Us, RDR2 | Prácticamente nunca para un equipo chico. Evitar |

Heurísticas de decisión:

- **Elegir el estilo por el equipo que TIENES, no por el juego que admiras.** "Un artista part-time" descarta Cuphead automáticamente.
- **Prototipar el estilo en engine antes de comprometerse**: un mini vertical slice con 3-4 assets en 2 estilos candidatos, vistos con la cámara real del juego. El estilo se evalúa en movimiento y a resolución de juego, nunca en un canvas de Photoshop.
- Journey como norte de diseño: *"do the most with the least"* — cada elemento visual extra debe justificarse; quitar es más barato que pulir.
- Pipeline híbrido 3D→2D (ver §8, Dead Cells) cuando quieres look 2D pero mucha cantidad de animación.
- El coste real no es el primer asset, es el **asset número 200 + sus animaciones + sus variantes**. Estimar multiplicando, no por el prototipo.

## 4. Color aplicado a juegos

Tres funciones del color (Tulleken & Bailey), en orden de prioridad para gameplay:

1. **Función**: identificar qué es cada cosa y de quién es (equipos en RTS por color de jugador, portales azul/naranja = dos mecánicas distintas en Portal).
2. **Emoción / mood**: hue + saturación + color grading cambian el tono de una escena entera. Journey cambia la paleta por fase para expresar la progresión narrativa (dorado → rojo → azul oscuro → blanco).
3. **Marca**: el color icónico que identifica el juego en una thumbnail.

### Color como lenguaje (vocabulario funcional)

Definir un diccionario de color y NO violarlo nunca:

| Significado | Convención habitual | Regla |
|---|---|---|
| Peligro / daño | Rojo, naranja saturado | Nada decorativo puede usar el mismo rojo |
| Interactivo / camino | Un color reservado (Mirror's Edge: rojo = ruta del runner) | El color-guía debe ser raro en el resto de la escena |
| Loot / recompensa | Jerarquía por rareza (gris<verde<azul<morado<naranja, convención ARPG) | Consistente en drops, iconos y tooltips |
| Curación / buff | Verde / dorado suave | — |
| Aliado vs enemigo | Dos hues opuestos (TF2: rojo cálido vs azul frío) | Verificar con filtros de daltonismo |

Reglas de manejo:

- **Saturación = atención.** Elementos jugables saturados; fondo desaturado. Si todo satura, nada destaca.
- **El contraste de VALOR (claro/oscuro) manda sobre el de hue**: convierte el screenshot a escala de grises; si el personaje no se separa del fondo, el color no lo va a arreglar.
- **Daltonismo**: ~1 de cada 12 hombres, 1 de cada 200 mujeres (mayoría rojo-verde). Nunca comunicar información SOLO con color: doblar con forma, patrón, icono o texto (Call of Duty pasó indicadores rojo/verde a azul/naranja).
- Paletas limitadas (3-5 hues + rampas de valor) son más baratas de mantener y más identitarias que paletas abiertas. Palette-swap sigue siendo válido para variantes de enemigos.

### Luz, valor y post-proceso como mood

- La iluminación define cómo se percibe forma, profundidad, espacio y mood; es el multiplicador más barato del estilo (en low-poly hace la mitad del look, §3).
- Objetivo de la luz en gameplay: entregar las 2-3 piezas de información que el jugador necesita en ese momento y hundir el resto en el fondo. Luz y sombra atraen el ojo — son herramienta de composición, no solo de ambiente.
- **Color grading** cambia el mood de una escena entera sin tocar assets (Tulleken); The Witness usa grading especial para marcar áreas importantes. Definir el grading por zona/momento en el style guide, no improvisarlo al final.
- Presupuesto de valor por escena: decidir qué rango tonal ocupa el fondo, cuál el midground jugable y cuál los focos; si todo vive en el mismo rango, la escena es plana y nada guía.
- Journey pintaba sombras a mano por falta de sistema dinámico: la restricción técnica bien dirigida se convierte en identidad, no en carencia.

## 5. Readability: que el juego se lea en el caos

La legibilidad es LA restricción que separa arte de juego de ilustración. En Overwatch fue la necesidad que pesó sobre todas: identificar al personaje en medio del combate; toda silueta nueva se validaba contra las existentes y los VFX de habilidades se limitaban para no saturar.

### Siluetas

- **Test de silueta**: rellenar el sprite/modelo de negro sólido. Las 9 clases de TF2 son identificables SOLO por silueta (Valve, paper NPAR 2007). Cada personaje/enemigo con rol distinto necesita silueta distinta (proporción, postura, arma, un elemento único).
- La silueta se lee primero por **proporción y postura**, no por detalle. Exagerar: el Heavy es una masa, el Scout es líneas finas.
- TF2 separa siluetas del fondo con **rim lighting** en vez de outline negro; en 2D el equivalente es outline u halo de contraste con el fondo.

### Jerarquía de lectura (de TF2, generaliza a cualquier juego)

El jugador lee en este orden y el arte debe soportarlo: **1) ¿de qué equipo/bando es? (color global) → 2) ¿qué es / qué clase? (silueta) → 3) ¿qué arma/estado tiene? (detalle y saturación local)**.

Técnicas concretas (paper de TF2 + análisis TF2 vs Overwatch):

- Concentrar el contraste y el color claro en el **torso/pecho hacia arriba** y en el **arma**: es donde el jugador mira y apunta. Piernas y pies: oscuros, sin detalle.
- Gradiente de valor en el personaje: oscuro abajo → claro arriba, dirige el ojo a la cabeza/arma.
- **Áreas de descanso visual**: zonas planas sin detalle. El detalle solo tiene valor por contraste con zonas limpias. Ruido uniforme = ilegible.
- Entornos menos saturados y con menos contraste que los personajes, siempre. El entorno es escenario, no protagonista.
- Un personaje debe leerse contra TODOS los fondos del juego, en la peor condición de luz. Probar en la escena más oscura y la más ruidosa.

### Jerarquía en pantalla con caos

Presupuesto de atención: el jugador procesa 2-3 cosas por momento. Prioridad visual descendente: amenaza inmediata > jugador/cursor > objetivo > pickups > decoración. Todo VFX nuevo compite en este presupuesto — los efectos de "juice" no pueden tapar la información de gameplay [ver: game-feel]. Si un playtest muestra muertes "injustas", sospechar de legibilidad antes que de balance.

## 6. Composición de pantalla y guiado del ojo

Dos niveles (Level Design Book):

- **Composición espacial**: organización 3D de masas del nivel — funciona desde cualquier ángulo de cámara. Es la que importa en juegos con cámara libre.
- **Composición de plano** (encuadre tipo foto/cine): solo controlable en cámaras fijas, 2D de scroll, o vistas/cinemáticas puntuales.

Herramientas que SÍ funcionan:

- **Jerarquía por contraste local**: algo alto entre cosas bajas, denso entre vacío, rotado contra la grilla, redondo entre rectángulos. Un focal point solo existe por contraste con su contexto.
- **Landmarks**: forma única y memorable, visible desde lejos, que además es ÚTIL (meta, orientación). Journey: la montaña visible en casi toda pantalla = objetivo narrativo y brújula. Regla: si se puede viajar al landmark, tiene que haber payoff al llegar.
- **Vista / approach**: componer aperturas donde el jugador ve el área siguiente antes de entrar (preview + orientación).
- **Luz como imán**: los jugadores van hacia la luz; iluminar la salida/objetivo, oscurecer lo secundario [ver: level-design].
- Color discordante / saturación alta alrededor de los puntos jugables.

Advertencia (Level Design Book): las **leading lines** de manual de pintura están sobrevaloradas en juegos — el jugador nunca juega el screenshot que compusiste; en perspectiva, literalmente todo pasillo converge. No diseñar niveles como fotografías: la jerarquía espacial, los landmarks y el playtesting de navegación pesan más que el encuadre. En 2D de cámara fija o cinemáticas, la composición de plano sí aplica con toda su fuerza (regla de tercios, framing).

## 7. UI art integrada con el estilo

La UI es parte de la dirección de arte, no un overlay genérico [ver: ux-ui-onboarding].

- **Espectro de integración**: HUD clásico → UI estilizada no-diegética → UI diegética (dentro del mundo). Dead Space: salud y stasis en la espina del traje RIG, munición como holograma del arma — "diegetic by design and diegetic by implementation" (Dino Ignacio, su diseñador). Coste: la UI diegética es cara y arriesga legibilidad; solo si la inmersión es pilar del juego.
- **Vía barata y de alto impacto**: UI no-diegética pero con la personalidad del juego (Persona 5: menús, transiciones y tipografía comparten la identidad rebelde del juego; la UI ES parte del estilo). Para un indie: heredar paleta, formas y texturas del mundo en paneles, botones y fuentes; prohibido el look "default de engine".
- La UI usa el MISMO diccionario de color del §4 (el rojo de daño del mundo = el rojo de la barra de vida).
- Legibilidad primero: la estilización nunca baja el contraste texto/fondo ni encoge el cuerpo de fuente por estética. Probar la UI sobre el fondo más ruidoso del juego.
- Técnica de producción: paneles y marcos con **9-slice** para escalar sin deformar (estándar en pixel art y UI general; saint11 lo cubre en sus tutoriales).

## 8. Pipeline de assets 2D

Flujo: **concept/thumbnail → sprite base → animación → export → integración → revisión EN el juego**. La revisión final siempre con la cámara y zoom reales.

Herramientas actuales del indie (estado 2025-2026):

| Herramienta | Rol | Coste |
|---|---|---|
| Aseprite | Pixel art + animación frame a frame, tilesets, paletas | Pago único barato |
| Krita | Painting digital: concepts, fondos, sprites hand-painted | Gratis, open source |
| Spine / DragonBones | Animación esqueletal 2D (personajes por partes) | Spine pago / DragonBones gratis |
| Tiled | Tilemaps agnóstico de engine | Gratis |
| Inkscape / Affinity | Vector para UI y estilo flat | Gratis / pago único |

Notas de producción:

- Pixel art: fijar resolución base y tamaño de tile ANTES de producir; mezclar densidades de píxel (sprites 16px junto a 32px, o rotaciones/escalas no enteras) rompe el estilo al instante. Escalar solo a múltiplos enteros, sin filtrado.
- Los fundamentos entrenables del pixel art (tutoriales de saint11/Pedro Medeiros, artista de Celeste y TowerFall, +70 tutoriales gratis): shading, outlines, anti-aliasing manual, subpixel animation, iluminación, tiles, 9-slice UI.
- Animación esqueletal vs frame a frame: esqueletal amortiza (un rig, muchas animaciones, blending) pero se nota "de papel recortado" si el estilo pide deformación dibujada; frame a frame es más expresivo y más caro por segundo.
- **Pipeline híbrido 3D→2D (Dead Cells, Motion Twin)**: model sheet en pixel art → modelo y rig 3D → animación por keyframes (pocos frames clave, luego interpolados) → render por frame a resolución mínima sin anti-aliasing + normal map por frame + toon shader → sprites. Ventajas: una persona anima todo el bestiario, cualquier animación se re-timea fácil para el gameplay, y el reuso de rigs/assets ahorra "cientos de horas". Opción seria si necesitas volumen de animación con equipo mínimo (hoy replicable en Blender).

## 9. Pipeline de assets 3D

Flujo estándar (metalness/roughness PBR): **concept → blockout (silueta y escala en engine) → high-poly → low-poly/retopo → UV → bake (normal, AO, curvature, ID) → texturizado → export (glTF/FBX) → material en engine → revisión con la luz real del juego**.

- **Blockout primero, siempre**: forma, silueta y proporciones a nivel de masa, probadas EN el engine con la cámara real, antes de invertir en detalle. (Mismo principio que el test de silueta del §5.)
- Estilizado low-poly puede saltarse high-poly y bake: color plano por material, vertex colors o una paleta-textura de 1 gradiente; la iluminación y el post-proceso hacen el look.
- Herramientas: **Blender** cubre todo el pipeline gratis (modelado, UV, bake, hand-painting, render); **Substance Painter** para PBR por capas (fill layers + máscaras + smart materials) — plan indie de suscripción mensual, precio exacto NO VERIFICADO (fuente consultada da ~$20-25/mes pero no lo confirmé contra el pricing oficial de Adobe; revisar precio actual antes de presupuestar). Hand-painted estilizado: pintar en Blender/Krita directamente sobre el modelo.
- Presupuestos consistentes: fijar texel density y poly budget por categoría de asset en el style guide (§2); un asset fuera de presupuesto se nota como un asset fuera de estilo.
- Trucos de coherencia y ahorro: paleta de materiales compartida entre assets, trim sheets/atlas para entorno, modularidad (kit de piezas que encajan en grilla) — menos assets únicos, mundo más coherente y menos draw calls.
- La textura no se aprueba en el visor de Substance/Blender: se aprueba bajo la iluminación, el fog y el post-proceso del juego.

## Reglas prácticas

1. Define la emoción objetivo y 3 pilares visuales por escrito ANTES de producir ningún asset.
2. Construye un visual target: 1 escena gold-standard en engine; todo asset nuevo se compara contra ella, no contra sí mismo.
3. Elige estilo por el equipo y tiempo REALES; prototipa 2 estilos candidatos en engine antes de comprometerte.
4. Estima el coste de arte multiplicando por el catálogo completo (assets × animaciones × variantes), no por el primer asset.
5. Paleta limitada con hex exactos y significado por color; el diccionario de color (peligro/interactivo/loot) no se viola jamás.
6. Nunca comuniques gameplay SOLO con color: dobla con forma, patrón o icono (daltonismo: ~1/12 hombres).
7. Test de silueta en negro para todo personaje/enemigo nuevo; si dos roles distintos comparten silueta, rediseña.
8. Test de escala de grises al screenshot: figura debe separarse del fondo por valor, no por hue.
9. Contraste y saturación concentrados en lo jugable (torso/arma/pickup); entorno siempre más apagado que los personajes.
10. Deja áreas de descanso visual: el detalle solo lee por contraste con zonas limpias.
11. Personaje probado contra el fondo más oscuro Y el más ruidoso del juego antes de aprobarlo.
12. Jerarquía en pantalla: amenaza > jugador > objetivo > loot > decoración; cada VFX nuevo debe justificar su lugar en ese presupuesto.
13. Guía con jerarquía espacial, landmarks útiles y luz — no con leading lines de screenshot.
14. UI hereda paleta, formas y tipografía del juego; cero look "default de engine"; contraste de texto intocable.
15. Pixel art: una sola densidad de píxel, escalado entero sin filtrado, resolución y tile size fijados antes de producir.
16. 3D: blockout en engine con cámara real antes de detallar; texturas aprobadas solo bajo la luz del juego.
17. Fija texel density y poly budget por categoría en el style guide; modularidad y trim sheets antes que assets únicos.
18. Todo el arte se evalúa en movimiento, a resolución de juego, con la cámara del juego — nunca como imagen estática ampliada.
19. Si el volumen de animación 2D te ahoga, evalúa el pipeline 3D→sprites tipo Dead Cells antes de recortar contenido.
20. Aliados y enemigos usan lenguajes de forma opuestos (redondo/estable vs anguloso) para leerse sin pensar [ver: animacion].
21. La luz entrega las 2-3 piezas de información del momento; ilumina el objetivo, hunde lo secundario.
22. El style guide es documento vivo: cada excepción aprobada se documenta o se convierte en drift.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| "Pixel art porque es barato" y luego ahogarse en frames de animación | El coste del pixel art está en la animación y la fidelidad: bajar resolución, limitar frames, o pipeline 3D→2D |
| Elegir estilo imitando a Cuphead/Hollow Knight sin su equipo | Matriz estilo×equipo del §3; el estilo se elige por capacidad, no por admiración |
| Assets individualmente buenos, juego incoherente (drift de estilo) | Visual target + do's/don'ts; revisar cada asset contra la escena gold-standard |
| Todo saturado y detallado "para que se vea rico" → nada destaca | Saturación = atención: presupuestarla; entorno desaturado, descanso visual |
| Personaje invisible sobre ciertos fondos | Test de grises + test contra peor fondo; rim light/outline; recolorear el fondo, no parchar con flechas |
| Información crítica solo por color (rojo/verde) | Forma + patrón + icono siempre; pasar filtros de daltonismo |
| VFX espectaculares que tapan el combate | Los VFX compiten en el presupuesto de atención; legibilidad va primero [ver: game-feel] |
| Diseñar niveles como screenshots (leading lines, encuadres) | Jerarquía espacial + landmarks + playtest de navegación; el jugador no juega tu foto |
| UI genérica de engine pegada sobre un juego con identidad | La UI es un asset de arte más: misma paleta, formas y tipografía (Persona 5 como norte) |
| UI diegética por moda, ilegible en la práctica | Diegética solo si la inmersión es pilar Y sobrevive el test de legibilidad; si no, UI estilizada no-diegética |
| Mezclar densidades de píxel o escalados no enteros | Specs fijos en el style guide; auditar assets importados de packs |
| Aprobar texturas/materiales en el visor de la herramienta | Solo se aprueba bajo luz, fog y post-proceso del juego real |
| Detallar modelos antes de validar silueta y escala | Blockout en engine primero; el detalle no arregla una masa mal proporcionada |
| Style guide de 40 páginas que nadie actualiza | Guide corto + visual target vivo; cada cambio aprobado se refleja el mismo día |
| Aprobar arte estático que falla en movimiento (flicker, ruido al scrollear, animación que rompe la silueta) | Evaluar todo en movimiento con la cámara del juego; la pose clave de cada animación debe conservar la silueta [ver: animacion] |

## Fuentes

- **Illustrative Rendering in Team Fortress 2** — Jason Mitchell, Moby Francke, Dhabih Eng (Valve), NPAR/SIGGRAPH 2007 — canon de readability: siluetas identificables por clase, jerarquía equipo→clase→arma, rim light, gradientes de valor, influencia de ilustradores comerciales (Leyendecker, Cornwell, Rockwell).
- **Color in games: An in-depth look at one of game design's most useful tools** — Herman Tulleken & Jonathan Bailey, Game Developer/Gamasutra (2015) — funciones del color (función/emoción/marca), ejemplos por juego, daltonismo y accesibilidad.
- **Character Readability in Team Fortress 2 and Overwatch** — Xavier Coelho-Kostolny (character artist), Medium — comparación aplicada: dónde concentrar contraste/saturación, áreas de descanso visual, contraste figura-fondo.
- **The Art of Journey** — Matt Nava, GDC 2013 + breakdown en Game Developer — "do the most with the least", montaña como landmark-meta, paleta por fase narrativa, simplificación de personaje.
- **The Aesthetics of Game Art and Game Design** — Chris Solarski, Gamasutra (2012; base de su libro *Drawing Basics and Video Game Art*) — lenguaje de formas círculo/cuadrado/triángulo, composición dinámica, empezar por la emoción.
- **The Level Design Book — capítulo Composition** — Robert Yang et al. — composición espacial vs de plano, jerarquía por contraste local, landmarks, vista/approach, crítica fundamentada a las leading lines.
- **Designing Overwatch** — Bill Petras, GDC 2017 — readability como pilar número 1 de la dirección de arte, técnica de art target (un personaje llevado a nivel final y probado en un mapa jugable para calibrar el resto); detalle de qué héroe/mapa exacto NO VERIFICADO contra el video original, solo resúmenes de la charla.
- **Art Design Deep Dive: Using a 3D pipeline for 2D animation in Dead Cells** — Motion Twin, Game Developer — pipeline 3D→sprites completo: rig 3D, keyframes mínimos, render sin AA + normal maps, reuso de rigs.
- **The Indie Developer's Guide to Game Art Styles** — MLC Studio — comparativa de coste/riesgo por estilo (pixel, low-poly, flat, hand-drawn, realista) con ejemplos.
- **Crafting the Perfect Game Art Brief / How to write a UI art bible** — Game Developer + Caitlin (Thrifted Design Leadership) — contenido del style guide: mood boards con callouts, paleta con significados, escala 1-10 de estilización, do's/don'ts, 20-40 páginas, documento vivo.
- **Pixel Art Tutorials** — Pedro Medeiros / saint11 (artista de Celeste, TowerFall), saint11.art — +70 tutoriales gratis: shading, outlines, anti-aliasing, subpixel, iluminación, tiles, 9-slice.
- **Diegetic UI de Dead Space** — análisis en iabdi.com / Medium (citas de Dino Ignacio) + Game UI Database — "diegetic by design and by implementation", RIG como HUD; Persona 5 como contraejemplo de UI estilizada no-diegética.
- **Substance 3D Painter updates / PBR workflow guides** — Adobe blog (2025), generalistprogrammer.com — pipeline PBR actual (bake de mesh maps, fill layers, smart materials), precio bundle indie (~$25/mes).
- **Toolkits 2D indie 2025** — Toxigon / Game Genius Lab / hyperPad — roles vigentes de Aseprite, Krita, Spine/DragonBones, Tiled.
