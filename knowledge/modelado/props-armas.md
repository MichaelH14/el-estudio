# Props, cosas y armas: el método

> **Cuando cargar este archivo:** al modelar cualquier prop de juego — objeto de entorno, item, arma, prop interactivo — desde la referencia hasta la entrega game-ready; o al presupuestar detalle por distancia de cámara, planear trim sheets, preparar partes móviles/pivots o generar variantes de un asset base.

## 1. Qué es un prop y de qué tipo es (esto decide TODO el presupuesto)

Un prop game-ready no es "un modelo bonito": es un asset que entra al engine con escala, pivot, presupuesto, UVs y materiales correctos sin retoques [ver: pipeline/arte-a-unity]. Antes de tocar geometría, clasificar el asset — su **rol** y su **distancia mínima de cámara** determinan cuánto cuesta:

| Categoría | Distancia típica de cámara | Presupuesto relativo | Textura típica |
|---|---|---|---|
| Prop de fondo (background) | Lejos, nunca en foco | Mínimo; a menudo vive de un trim sheet (§6) | Comparte trim/atlas |
| Prop estándar de entorno | Media; el jugador pasa al lado | Medio | Trim + detalles únicos, o textura propia chica |
| Hero prop | Cerca; centro de una escena o interacción | Alto; textura propia | Set propio (1–2K, hasta 4K si llena pantalla) |
| Prop interactivo (puerta, palanca, cofre) | Cerca + se manipula | Medio-alto + partes móviles y pivots (§8) | Según tamaño |
| Arma first-person | Pegada a cámara, siempre en pantalla | El más alto del juego (§7) | 2K–4K por arma (NastyRodent) |
| Arma third-person / world model | Media (en manos de otros, en el suelo) | Fracción del FP | Comparte o reduce el set FP |

Regla: **la distancia mínima a la que la cámara verá el asset fija su texel density y su detalle geométrico**. Un barril que nunca se ve a menos de 5 m no merece tornillos modelados. Los números de texel density y polys por categoría se congelan en el style guide [ver: gamedev/arte-direccion §2] y se detallan en [ver: presupuestos-poligonos].

## 2. El método completo: referencia → game-ready

Pipeline de un prop con **gate de salida por fase** — no se avanza sin pasar el gate (mismo espíritu que el runbook de auditoría de [ver: pipeline/arte-a-unity §10]):

| Fase | Qué se hace | Gate para avanzar |
|---|---|---|
| 1. Referencia | Carpeta organizada de referencias reales: fotos desde varios ángulos, videos de disassembly si tiene mecanismo, medidas reales del objeto. Los breakdowns serios usan cientos de imágenes (Oriol Salom reunió ~1000 para un AK-74) [ver: blueprints-referencias] | Entiendes cómo el objeto está CONSTRUIDO (piezas, materiales, función), no solo cómo se ve |
| 2. Blockout a escala | Primitivas a medidas reales (1 unidad = 1 m), con figura humana al lado (§3). Exportar al engine YA y verlo con la cámara del juego | Silueta, proporciones y escala aprobadas EN engine [ver: gamedev/arte-direccion §9] |
| 3. Formas primarias → secundarias → terciarias | Refinar por jerarquía (§4): primero masas, luego piezas funcionales, al final superficie | Squint test: el objeto se lee por su masa; el detalle no tapa la forma |
| 4. High-poly | Detalle completo: subdivisión/booleans en hard-surface, sculpt para orgánico o desgaste [ver: hard-surface] | El high refleja la referencia al nivel de estilización del proyecto |
| 5. Low-poly | Retopo o rebuild desde el blockout: solo geometría que afecta silueta o deformación [ver: topologia]. En hard-surface medio, el mid-poly del blockout suele SER la base del low (Room 8, Salom) | Dentro del presupuesto de tris de su categoría; vertex count auditado (§5) |
| 6. UVs | Shells rectas donde se pueda ("always keeping things straight", Room 8), texel density uniforme entre partes (Salom mantiene la variación en ~±20%), splits en cada hard edge (§5) | Sin solapes no planificados; densidad dentro de spec |
| 7. Bake | Normal/AO/curvature del high al low, con cage; bakear el normal a 2× la resolución final de entrega (NastyRodent) [ver: high-to-low] | Bake limpio visto A LA DISTANCIA REAL de juego, no a 400% de zoom |
| 8. Texturas | Por pases: material base → tratamiento de superficie → daño/desgaste → micro-detalle (los 4 pases de Room 8) | Aprobada bajo la luz y post del juego [ver: gamedev/arte-direccion] |
| 9. Entrega | Export según spec: escala, ejes, pivots, naming, LODs, colliders (§10) | Checklist del §10 completa; auditoría de [ver: pipeline/arte-a-unity §10] en verde |

El orden importa: **cada fase es más cara que la anterior**, así que los errores se matan temprano. Un blockout malo detectado en fase 2 cuesta minutos; detectado en fase 8, cuesta el asset entero.

## 3. Escala y lectura: el prop debe "sentirse" correcto

- **Figura humana SIEMPRE en escena.** Un maniquí a escala del personaje del juego vive en el archivo de trabajo de todo prop, de la fase 2 a la 9. Skyrim calibró todos sus kits contra el personaje de ~128 unidades ≈ 6 pies (Burgess/Purkeypile, GDC 2013); el Level Design Book lo generaliza: "build to a human scale".
- **Medidas reales primero.** Sillas, puertas, botellas, armas: el jugador conoce estos objetos con el cuerpo. Un objeto familiar 15% fuera de escala se siente "raro" aunque nadie sepa decir por qué. Buscar las dimensiones reales del objeto en la fase de referencia y modelarlas (1 unidad = 1 m [ver: pipeline/arte-a-unity §7]).
- **La estilización cambia proporciones, no la escala funcional**: un cofre cartoon puede exagerar la tapa, pero su alto sigue relacionado con el personaje que lo abre [ver: estilizacion-lowpoly].
- **Verificar en engine, no en el viewport**: la lente/FOV del DCC miente. El gate de la fase 2 es verlo con la cámara real del juego junto al personaje real.
- Props que el personaje agarra: verificar el tamaño EN LA MANO del personaje (un rifle correcto a escala real puede verse enano en un personaje de proporciones heroicas — se ajusta el prop al personaje, y esa decisión se documenta en el style guide).

## 4. Jerarquía de formas: primaria → secundaria → terciaria

Canon de diseño de objetos (Neil Blevins, "Primary, Secondary and Tertiary Shapes"):

| Nivel | Qué es | En el pipeline | Test |
|---|---|---|---|
| **Primaria** | Las masas grandes: lo que queda al entrecerrar los ojos | El blockout (fase 2). Define silueta y lectura a distancia | Squint test / silueta en negro [ver: gamedev/arte-direccion §5] |
| **Secundaria** | Piezas medianas sobre las primarias: paneles, asas, cargador, bisagras | Refinado del blockout (fase 3) | El objeto "funciona": cada pieza secundaria tiene propósito |
| **Terciaria** | Detalle chico: tornillos, costuras, chaflanes, texto, desgaste | High-poly y texturas (fases 4 y 8) — mucho acaba en el normal map, no en geometría | Solo visible a la distancia real del asset (§5) |

Reglas de Blevins que aplican directo al modelado:

- **Proporción 70/30, no 50/50**: al subdividir una forma, los cortes desiguales crean interés; las divisiones a la mitad aburren.
- **Distribución desigual del detalle**: áreas densas contra áreas limpias — el detalle solo lee por contraste con zonas de descanso (coincide con el principio de readability de [ver: gamedev/arte-direccion §5]).
- **La jerarquía es de arriba hacia abajo**: nunca detallar terciario sobre un primario no aprobado. El detalle no arregla una masa mal proporcionada.

## 5. Presupuesto de detalle: dónde van los polígonos

- **La distancia mínima de cámara decide** (§1). Presupuesto geométrico en: 1) silueta, 2) lo que la cámara ve de cerca, 3) lo que se mueve. Lo demás vive en el normal map o el trim.
- **El vertex count real importa más que los tris**: la GPU procesa vértices, y cada UV split, hard edge / smoothing split y cambio de material DUPLICA vértices a lo largo de esa arista (Polycount wiki, "Polygon Count"). Un low de 10k tris con UVs fragmentadas puede costar más que uno de 15k limpio. Auditar vertex count final, no solo tris [ver: presupuestos-poligonos].
- **Hard edges y UVs van juntos**: cada hard edge (split de normales / smoothing group) debe tener split de UV en el mismo lugar — es la regla central del bake tangent-space (Polycount wiki, "Normal Map"); si no, seams visibles. Triangular antes de espejear para evitar errores de sombreado [ver: high-to-low].
- **Texel density por categoría, uniforme dentro del asset**: NastyRodent documenta 512–1024 px/m para armas FP; un asset con densidad dispareja entre piezas se ve roto aunque la textura sea buena. Mantener la variación acotada (Salom: ~±20% entre partes del arma).
- Chaflanes/bevels en las aristas que la cámara ve de cerca: una arista perfectamente afilada no existe en el mundo real y delata el 3D barato; a distancia, el bevel vive en el normal map [ver: hard-surface].
- En estilizado, el presupuesto terciario CAE a propósito: el detalle se traslada a formas secundarias exageradas y a la textura pintada; la jerarquía del §4 no cambia, cambia dónde se corta [ver: estilizacion-lowpoly].
- Vehículos y assets XXL siguen el mismo método con presupuestos propios y el interior como problema aparte [ver: vehiculos].

## 6. Trim sheets y tileables: modelar PARA el trim

Para props de ENTORNO en cantidad, la textura única por asset no escala. El trim sheet — una textura de franjas que tilean en U o en V — texturiza docenas de assets con un solo material (Beyond Extent: 12 assets = 36 texturas únicas vs 3 texturas con trims; menos memoria y draw calls).

**El orden es lo que casi todos hacen mal: el trim se diseña ANTES de modelar los assets, y los assets se modelan PARA el trim.**

| Paso | Regla |
|---|---|
| 1. Inventario | Listar los assets/superficies del set (bioma, edificio, kit) y qué franjas necesitan: molduras, zócalos, metales, bordes, paneles, remaches |
| 2. Layout de franjas | Alturas en potencias de 2 dentro de la textura (en una 1024: franjas de 512/256/128/64/32/16 px — Beyond Extent), dimensionadas por el elemento MÁS GRANDE que las usará y la texel density del proyecto |
| 3. Dirección | Decidir tiling en U o en V y ser consistente; franjas híbridas: parte tileable + secciones únicas bakeadas (asas, cerraduras) en la misma sheet |
| 4. Producir el trim | High-poly de las franjas sobre un plano → bake → texturizar. El trim es un asset en sí mismo, con su propio pipeline del §2 |
| 5. Modelar para el trim | Geometría con bordes/cortes donde las franjas cambian; UVs = mover shells RECTAS sobre las franjas. Shells enderezadas (con loops extra si la pieza curva distorsiona demasiado) |
| 6. Variación | Vertex color como máscara de tinte multiplicativo sobre textura limpia (Klafke); decales para romper repetición |

Reglas del set modular (Thiago Klafke, "Creating Modular Environments"; aplica a props de kit):

- Pocas categorías de textura lo aguantan casi todo: su escena usó 3 — muro tileable, trim, piso.
- **Todo múltiplo del módulo base**: si el módulo es 1×1, una pieza doble es 2×1 exacto — nunca 1.5×1 (su ejemplo: 256×128, jamás 192×128). El footprint de cada sub-kit debe ser múltiplo del de los demás (Burgess: si no, los layouts dejan de cerrar al dar la vuelta).
- Pivots en esquinas/extremos de la pieza para snapping y rotación en grid, consistentes entre piezas similares.
- Suelos y muros con ESPESOR real, no planos de papel — fallan el stack test al construir en niveles (Level Design Book).
- Kit de entorno completo: [ver: entornos-modulares]. Cuándo un prop merece textura única vs trim: si es hero o su forma es irrepetible → única; si es parte de una familia de superficie continua → trim.

## 7. Armas: el caso especial

El arma first-person es el asset con más presupuesto por cm² del juego: está SIEMPRE en pantalla, pegada a la cámara, y el jugador la mira durante decenas de horas.

### 7.1 First-person vs third-person

| Aspecto | First-person (viewmodel) | Third-person / world model |
|---|---|---|
| Qué ve la cámara | Solo la mitad trasera-superior del lado de cámara; nunca la cara exterior opuesta ni la culata completa | El arma entera a media distancia |
| Presupuesto | El máximo: NastyRodent (armas de Squad / Ready or Not): low-poly 8k–20k tris según plataforma; rifle hero 12k–18k; pistolas 6k–10k; high-poly 60k–100k | Fracción del FP: versión reducida o LOD del viewmodel |
| Densidad geométrica | Concentrada en lo que la cámara ve cerca: zona del gatillo, miras (sights), boca del cañón (NastyRodent) | Repartida; manda la silueta |
| UVs | **SIN mirroring en lo visible en FP** (receiver, sights, gatillo): la simetría espejada se nota a esa distancia (NastyRodent). Mirror OK en la cara oculta y la parte baja | Mirror agresivo permitido |
| Texturas | 2K–4K por arma; texel density 512–1024 px/m (NastyRodent) | Reducidas |
| Silueta | **Se evalúa a 45°** — el ángulo al que el viewmodel se sostiene en pantalla, no de perfil de catálogo (NastyRodent: la retopología se optimiza para el ángulo de cámara FP de 45°, con la densidad de poly más alta donde ese frame de cámara lo ve más) | De perfil y 3/4, como cualquier prop |

- Los engines renderizan el viewmodel con **FOV separado** del mundo (y trucos contra el clipping con paredes y el near plane); el arma FP necesita además representación en mundo para sombras/reflejos (docs de Unreal, "First Person Rendering"). Consecuencia para el modelador: el arma se revisa EN el engine con el FOV de viewmodel real — en el viewport del DCC las proporciones aparentes engañan.
- **Sight alignment**: la línea de mira (alza → guion/punto de mira) debe ser recta, centrada en el eje del arma y a la altura correcta — al apuntar (ADS), el juego alinea esa línea con el centro de cámara. Miras torcidas o descentradas del blockout no se arreglan animando. Modelar el arma recta sobre su eje, con el sight picture limpio (nada del arma tapa la mira alineada).
- Ergonomía de referencia: entender cómo se sostiene y opera el arma real (videos de disassembly y manipulación — fase 1 del §2) es lo que hace creíbles pose, animación y desgaste.

### 7.2 Partes móviles y pivots para animar

El low-poly se entrega **despiezado como se anima**, no soldado. Partes típicas separadas, cada una con pivot propio en su eje real de movimiento:

| Parte | Movimiento | Pivot |
|---|---|---|
| Corredera / cerrojo (slide/bolt) | Recorrido lineal atrás-adelante | En su eje de deslizamiento |
| Cargador (magazine) | Sale y entra del pozo | Donde agarra la mano; el recorrido de extracción no debe intersectar el arma ("pull-and-seat without intersection", NastyRodent) |
| Gatillo, martillo, seguro, selector | Rotación corta | En su perno real |
| Tambor (revólver) | Rotación + basculación | Eje del tambor y bisagra del crane |
| Palanca de carga, bombeo | Lineal o rotación | Su eje mecánico |

- **Probar los recorridos antes de entregar**: la corredera debe poder ir atrás sin clipping ("slide geometry must allow rack movement without clipping", NastyRodent). Mover cada parte por su recorrido completo en el DCC es parte del QA del asset.
- **Modelar el interior mínimo que el movimiento revela**: puerto de eyección abierto, pozo del cargador vacío, recámara visible con la corredera atrás. Si al animar se ve el hueco, el arma se rompe como ilusión.
- Naming y jerarquía consistentes (root del arma → partes hijas) — el animador y el engine dependen de eso; la convención exacta va en la spec del proyecto [ver: pipeline/arte-a-unity §1].
- El bake AAA de un arma maneja decenas de material IDs para separar piezas en el high (Room 8 cita 30–50 en títulos tipo Call of Duty); en el low, el objetivo sigue siendo pocos materiales finales [ver: pipeline/arte-a-unity §7].

### 7.3 Attachment points

- Puntos de anclaje estandarizados para accesorios: óptica (riel superior), bocacha/silenciador (rosca del cañón), linterna/grip (rieles laterales/inferior), correa.
- **La estandarización es ENTRE armas**: un arma modular (mira/silenciador/grip/extensión de cañón intercambiables) es un SISTEMA de assets, no un asset suelto — comparten reglas de UV space, texel density y grupos de material PBR entre sí. Si el scope de un rifle no comparte slot de material con el de otro, el estudio paga en draw calls redundantes por partida, no solo en trabajo de outsourcing perdido (NastyRodent).
- Cada attachment es un prop del §2 con su propio presupuesto (y en FP, la óptica montada pasa a ser lo MÁS cercano a cámara: hereda presupuesto de hero).

## 8. Props interactivos: pivots y jerarquía para gameplay

Un prop interactivo se modela alrededor de su MECÁNICA, no de su estética. Las decisiones de pivot/jerarquía son de modelado — corregirlas después contamina prefabs, animaciones y código (Skyrim: cambiar pivots a mitad de proyecto = cientos de updates manuales; Burgess/Purkeypile).

| Prop | Pivot / jerarquía | Notas |
|---|---|---|
| Puerta | Pivot en el EJE de la bisagra, no en el centro | Marco y hoja separados; la hoja rota sola. Estado por defecto: cerrada |
| Palanca / interruptor | Pivot en el eje de rotación de la palanca | Base estática + brazo móvil como hijos |
| Cofre / caja con tapa | Tapa separada, pivot en la bisagra trasera | Modelar el INTERIOR (se ve al abrir); estado por defecto: cerrado |
| Cajón | Pivot donde corre; recorrido lineal sin clipping | Interior visible modelado |
| Válvula / rueda | Pivot en el centro del eje de giro | Simetría radial real para que el loop de giro no "salte" |
| Botón | Pivot en su eje de pulsado | Recorrido corto definido |

Reglas:

- **Estado por defecto documentado y modelado**: lo normal es entregar el prop CERRADO/en reposo, con las partes móviles en cero. El estado abierto lo produce la animación/engine, no otro mesh.
- Todo lo que el estado alternativo revela (interior del cofre, canto de la puerta, fondo del cajón) se modela y texturiza — presupuestarlo desde el blockout.
- Pivot general de props estáticos: en la base para lo que apoya en el suelo, en el punto de agarre para lo que se coge — la tabla completa y su auditoría en Unity está en [ver: pipeline/arte-a-unity §7].
- Congelar la convención de pivots y naming en la spec del día 1 y no tocarla (Skyrim: pivots a nivel de suelo y centrados como norma del kit, excepciones documentadas).

## 9. Series y variaciones: 5 variantes baratas de un prop base

Un mundo creíble necesita cantidad; la cantidad se fabrica con variantes, no con assets únicos. Orden de técnicas de MÁS barata a más cara — agotar cada nivel antes de bajar al siguiente:

| # | Técnica | Coste | Qué produce |
|---|---|---|---|
| 1 | Variante de textura/material sobre el mismo mesh | Casi cero (Level Design Book: las variantes texturales "no requieren revalidación geométrica") | Barril rojo/óxido/militar; madera clara/oscura |
| 2 | Tinte por vertex color o máscara de tint | Casi cero, infinitas variaciones de color (Klafke) | Familias de color por zona/facción |
| 3 | Decales y desgaste localizados | Bajo | Grafiti, números, manchas — rompe la repetición sin tocar el asset |
| 4 | Recombinación de piezas (kitbash del propio prop) | Bajo-medio | Cofre con/sin herrajes, estante con distintas baldas — exige modelar por PARTES desde el blockout |
| 5 | Deformación de proporción sobre las mismas UVs | Medio | Alto/bajo/ancho; en assets con trim, la geometría cambia y la textura no |
| 6 | Estados de daño/uso | Medio | Intacto/dañado/roto — el roto puede reusar piezas del intacto |
| 7 | Remodelar variante única | Alto — solo si 1–6 no alcanzan | Un asset nuevo |

- Diseñar el prop base PENSANDO en sus variantes: separado en piezas lógicas, UVs sobre trim donde se pueda, máscaras de tinte previstas. La variante barata se decide en la fase 2, no al final.
- Las variantes comparten pivot, escala y naming con el base (sufijo de variante) — así el engine las intercambia sin tocar nada [ver: pipeline/arte-a-unity §1].
- La economía del reuso es brutal cuando se hace bien: Skyrim construyó 300+ dungeons con 2 artistas de kit a tiempo completo y 8 level designers en 2.5 años (Burgess/Purkeypile, GDC 2013).

## 10. Checklist de entrega de un prop game-ready

La spec completa de integración (Unity/URP: escala, ejes, formatos, materiales, colliders, LODs) es [ver: pipeline/arte-a-unity §7 y §10]; esto es el lado del MODELADOR antes de exportar:

1. **Escala real** verificada contra la figura humana del proyecto y medidas del objeto real.
2. **Pivot** según categoría (base / agarre / eje de bisagra / esquina de grid) y transform limpio: rotación (0,0,0), escala (1,1,1), mirando al eje forward de la spec.
3. **Estado por defecto**: partes móviles en reposo/cerrado; recorridos de cada parte probados sin clipping.
4. **Jerarquía y naming**: root + partes hijas nombradas por convención; LODs como `_LOD0..n`; malla de colisión `_COL` si la spec la pide.
5. **Presupuesto**: tris dentro de la categoría Y vertex count auditado (splits de UV/hard edges/materiales).
6. **Topología**: sin n-gons en el export, triangulación consistente (triangular antes de espejear), hard edges solo donde hay UV split.
7. **UVs**: sin solapes no planificados, mirror solo en zonas no visibles (crítico en armas FP), texel density del proyecto ±20%, shells rectas sobre trims.
8. **Bake**: normal/AO limpios revisados a distancia real de juego; bakeado a 2× la resolución de entrega; padding correcto.
9. **Materiales**: número dentro de spec (objetivo 1 por prop), canales según el shader target (smoothness vs roughness acordado) [ver: pipeline/arte-a-unity §7].
10. **LODs**: presentes si la spec los pide y LOD1 conserva la silueta (perder la silueta en LOD1 es el error de LOD más citado — NastyRodent).
11. **Variantes**: entregadas con el mismo pivot/escala/naming + sufijo.
12. **Aprobación final EN engine**: escena visual-target, cámara real (FOV de viewmodel si es arma FP), luz y post reales [ver: gamedev/arte-direccion].

## Reglas prácticas

1. Clasifica el asset (fondo / estándar / hero / interactivo / arma) ANTES de modelar: su distancia mínima de cámara fija todo el presupuesto.
2. Referencia hasta entender cómo el objeto está construido y cómo funciona — no solo cómo se ve; mecanismos exigen video de desassembly.
3. Blockout a medidas reales con maniquí humano al lado, aprobado EN el engine con la cámara del juego antes de detallar.
4. Jerarquía de formas siempre: primaria (silueta) → secundaria (piezas funcionales) → terciaria (superficie); nunca detalle sobre masa no aprobada.
5. Divide formas en 70/30, no 50/50; concentra detalle en áreas y deja zonas de descanso.
6. El detalle geométrico va a: silueta, lo que la cámara ve cerca, lo que se mueve. El resto es normal map o trim.
7. Audita vertex count, no solo tris: cada UV split / hard edge / material extra duplica vértices.
8. Cada hard edge lleva su UV split en el mismo lugar; triangula antes de espejear.
9. Texel density del proyecto, uniforme dentro del asset (variación ≤ ~20% entre piezas).
10. Entorno en cantidad = trim sheet diseñado ANTES; modela PARA el trim con UVs rectas sobre franjas en potencias de 2.
11. Piezas de kit en múltiplos exactos del módulo base, con espesor real y pivots de esquina para snapping.
12. Arma FP: presupuesto en la mitad que la cámara ve (gatillo, sights, boca del cañón); cero mirror en lo visible; silueta evaluada a 45° y en el engine con el FOV del viewmodel.
13. Línea de mira recta y centrada desde el blockout; el sight alignment no se arregla animando.
14. Partes móviles separadas con pivot en su eje mecánico real, recorridos probados sin clipping, interior visible modelado.
15. Attachment points estandarizados en toda la familia de armas (escala, orientación, UVs).
16. Props interactivos: pivot en el eje físico (bisagra, riel, perno), estado por defecto cerrado/en reposo, y la convención de pivots congelada — no se cambia a mitad de proyecto.
17. Variantes por orden de coste: textura → tinte → decal → kitbash → proporción → daño → remodelar; el prop base se diseña por piezas para permitirlas.
18. LOD1 conserva la silueta; mata detalle interno primero.
19. Nada se aprueba en el viewport del DCC: la aprobación es en engine, escena visual-target, luz y distancia reales.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Detallar antes de validar blockout en engine | Gate de fase 2: silueta/escala/proporción aprobadas con la cámara real primero |
| Prop modelado "a ojo" sin referencia de escala | Maniquí humano en el archivo + medidas reales del objeto; test en engine |
| Detalle uniforme por todas partes "para que se vea rico" | 70/30, distancia de cámara como presupuesto, zonas de descanso (Blevins) |
| Presupuestar solo tris e ignorar los splits | Vertex count final auditado; UVs y smoothing consolidados donde se pueda |
| Seams de shading tras el bake | Hard edge sin UV split (o viceversa); regla: van juntos, siempre |
| Bake evaluado a 400% de zoom | Revisar a la distancia real del asset en juego; ahí se decide qué artefacto importa |
| Trim sheet improvisado después de modelar los assets | El trim se planifica primero (inventario de franjas) y se modela PARA él |
| Pieza modular de 1.5 módulos "porque quedaba mejor" | Múltiplos exactos del footprint o el kit deja de cerrar (Burgess) |
| Arma FP con UVs espejadas en el lado de cámara | Mirror solo en caras ocultas; el receiver/sights/gatillo llevan UV único (NastyRodent) |
| Arma aprobada de perfil, rota en el viewmodel | Evaluarla a 45° y con el FOV real del viewmodel en engine |
| Corredera/cargador soldados al mesh, o sin interior detrás | Partes separadas con pivot propio desde el low; modelar puerto de eyección/pozo visibles; probar recorridos |
| Sights torcidos o descentrados | Arma modelada recta sobre su eje desde el blockout; la línea de mira es geometría, no animación |
| Scopes que no encajan entre rifles de la misma familia | Attachment points estandarizados (escala/orientación/UVs) en la spec de la familia |
| Puerta/cofre con pivot en el centro | Pivot en la bisagra; estado por defecto cerrado; interior modelado |
| Cambiar la convención de pivots a mitad de proyecto | Congelarla el día 1; en Skyrim el cambio costaba cientos de updates manuales |
| Cada variante como asset nuevo remodelado | Escalera de coste del §9: textura y tinte primero; remodelar es el último recurso |
| LOD1 que destruye la silueta | Reducir detalle interno primero; la silueta es lo último que se toca |
| Suelos/muros de kit sin espesor (papel) | Stack test: el kit debe construir en niveles con cantos reales |
| Prop aprobado en el visor del DCC que desentona en el juego | Aprobación solo en escena visual-target con luz/post/cámara reales [ver: gamedev/arte-direccion] |

## Fuentes

- **Polygon Count** — Polycount Wiki — canon del game art: el vertex count pesa más que los tris para rendimiento/memoria; UV splits, smoothing groups y materiales duplican vértices; rangos generales de presupuesto.
- **Normal Map (tangent space)** — Polycount Wiki — la regla hard edge = UV split, cages para el bake, triangular antes de espejear, artefactos por piezas interpenetradas.
- **3D Weapon Art for Games** — Nasty Rodent (estudio de weapon art; trabajó en Squad y Ready or Not) — números de armas FP con origen de producción: low 8k–20k tris (rifle hero 12k–18k, pistolas 6k–10k), high 60k–100k, texturas 2K–4K, texel density 512–1024 px/m, bake a 2×, silueta a 45°, densidad en gatillo/sights/boca, sin mirror en lo visible, restricciones de animación (rack sin clipping, pull-and-seat), errores de outsourcing.
- **FPS Weapon Creation: How to Match AAA Standards** — Room 8 Studio — pipeline en 8 fases, referencias como fase crítica, UVs rectas, custom normals, texturizado en 4 pases, decenas de material IDs en bakes AAA.
- **How to Model and Texture a Realistic AK-74** — Oriol Salom, 80.lv — breakdown real: ~1000 referencias organizadas, workflow mid-poly→high (ZBrush)→low, texel density uniforme entre partes (~±20%), texturizado por capas de material.
- **Trimsheets (deep dive)** — Scot Daniel Burns (Flix Interactive), Beyond Extent — layout de franjas en potencias de 2 (512/256/128/64/32/16 en 1024), tiling U/V, trims híbridos, economía (12 assets: 36 texturas vs 3), enderezar shells.
- **Creating Modular Environments** — Thiago Klafke (environment artist, Blizzard) — 3 categorías de textura para una escena completa, piezas en múltiplos exactos del módulo, pivots en extremos, vertex color como tinte.
- **Skyrim's Modular Level Design** — Joel Burgess & Nate Purkeypile, GDC 2013 (transcript en el blog de Burgess) — personaje ≈128 unidades (6 pies) como base de toda métrica, footprints múltiplos entre sub-kits, pivots a suelo/centro y congelados, proceso concept→proof→graybox→build-out→polish, 300+ dungeons con 2 artistas de kit.
- **Modular kit design** — The Level Design Book (Robert Yang et al.) — "build to a human scale", loopback/stack/gap tests, espesor real en pisos, variantes texturales baratas.
- **Composition: Primary, Secondary and Tertiary Shapes** — Neil Blevins (Soulburn Studios; artista de Pixar/Blizzard) — definición de los 3 niveles de forma, squint test, regla 70/30, distribución desigual del detalle.
- **First Person Rendering** — Epic Games, documentación de Unreal Engine — por qué el viewmodel se renderiza con FOV propio, clipping con near plane, representación en mundo para sombras/reflejos (el principio generaliza a cualquier engine).
- Base sintetizada: [ver: gamedev/arte-direccion] (visual target, readability, pipeline 3D general), [ver: pipeline/arte-a-unity] (spec de entrega, pivots por categoría, auditoría en engine).
