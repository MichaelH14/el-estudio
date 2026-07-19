# Modelado hard-surface

> **Cuando cargar este archivo:** al modelar cualquier objeto rígido/mecánico (armas, vehículos, naves, robots, props industriales, arquitectura sci-fi) — para elegir workflow (subdivision / mid-poly / boolean-kitbash), decidir bevels, normals, decals y nivel de limpieza del high-poly.

## 1. Qué es hard-surface y qué lo hace difícil

Hard-surface = superficies rígidas fabricadas: metal, plástico, maquinaria, arquitectura. Lo opuesto a orgánico (músculo, tela, criaturas) [ver: organico-personajes]. La dificultad NO está en la complejidad de la forma sino en el **shading**: una superficie plana o suavemente curvada con material reflectante delata CUALQUIER error de topología o de normals como una ondulación en el reflejo. En orgánico un vértice mal colocado se pierde en el ruido; en hard-surface se ve a metros.

Consecuencias operativas:

- El criterio de calidad es **el reflejo, no el wireframe**: se inspecciona con matcap de alto contraste o material glossy, girando el objeto (Topology Guides: los materiales por defecto esconden distorsiones que un matcap especializado revela).
- Los bordes concentran casi toda la información visual del objeto (§2). Un modelo con siluetas correctas y bordes bien tratados "lee" como caro; el mismo modelo con filos perfectos de 90° lee como CAD barato.
- Antes de modelar: referencias y blueprint del objeto real o concept aprobado [ver: blueprints-referencias]; las proporciones no se inventan sobre la marcha.
- El presupuesto (tris, materiales, texturas) se fija ANTES por categoría de asset [ver: presupuestos-poligonos] y la spec de entrega a engine ya existe [ver: pipeline/arte-a-unity].

## 2. Bevels/chamfers: ningún borde real es perfectamente afilado

Todo objeto fabricado tiene los filos matados: mecanizado, moldeo, desgaste, pintura acumulada. Un borde de 90° exacto:

| Problema del filo perfecto | Por qué |
|---|---|
| No atrapa luz | El highlight de borde vive EN el chaflán; sin chaflán, la transición de normal es de 1 píxel → sin highlight → el objeto se ve plano y falso |
| Aliasing | Transición brusca de shading en 1 píxel = escalera brillante en movimiento |
| Shading roto o "todo facetado" | Con smooth shading, dos caras a 90° compartiendo normal promediada generan gradientes sucios en ambas caras |
| Bake sucio | En el bake high→low el detalle del borde cae en 1-2 texels y se pixela [ver: high-to-low] |

Reglas de bevel:

- **Todo borde visible lleva bevel/chamfer** — por geometría (mid-poly), por subdivisión con support loops (high-poly) o bakeado en la normal map. La única pregunta es CUÁL de las tres vías, no si se hace.
- **El ancho del bevel se calibra al tamaño en pantalla**, no al tamaño real: un bevel que no llega a ~1-2 píxeles en la distancia típica de cámara no existe (alias o desaparece); uno exagerado lee como juguete. Práctica reportada por el equipo de Angelic (80.lv): bevels simples en zonas poco visibles, más detallados en geometría prominente, decidido por presencia en pantalla.
- Bevels ligeramente exagerados respecto al objeto real venden mejor a distancia de juego — el bake comprime; lo sutil se pierde.
- En curvas, la densidad de segmentos del cilindro/curva también se decide por tamaño en pantalla: la silueta poligonal se nota antes que el shading [ver: presupuestos-poligonos].

## 3. Los tres workflows: costes y cuándo

| Workflow | Cómo funciona | Coste | Cuándo elegirlo | Riesgo principal |
|---|---|---|---|---|
| **Subdivision (high-poly clásico)** | Modelo subdividible con support loops/creases → high-poly denso → retopo low-poly → bake de normal map [ver: high-to-low] | Alto: dos mallas + UV único + bake por asset | Hero assets con textura única (arma en primera persona, prop protagonista) [ver: props-armas]; formas curvas complejas donde el bake paga | El más lento; cada iteración de forma obliga a rehacer low+bake |
| **Mid-poly (bevels + weighted normals)** | UNA malla con bevels reales de geometría + vertex normals ponderadas (§5); texturas tileables/trims/decals, sin bake high→low | Medio: una sola malla, sin retopo ni bake; más vértices que un low-poly puro | Entornos, vehículos y naves grandes donde una textura única no da texel density; producción con mucha iteración | Vertex count mayor; LODs deben eliminar los bevels finos; shading depende de normals custom que hay que preservar en el export |
| **Boolean / kitbash** | Formas por operaciones booleanas no destructivas + piezas de kit reutilizadas (§6, §9) → se remesh/bakea, o se limpia a mid-poly | Bajo para explorar, medio para cerrar: la exploración es rapidísima, el cierre (limpieza o bake) es el coste real | Concepting 3D, blockout de diseño, greebles y detalle mecánico masivo; naves/mechs/entornos sci-fi | Geometría sucia que alguien tiene que resolver después; drift de estilo si el kit no comparte lenguaje de formas |

- No son excluyentes: el pipeline moderno típico es **boolean/kitbash para diseñar → subdivision O mid-poly para cerrar el asset** según su categoría.
- La decisión por asset se toma con: distancia de cámara, ¿textura única o tileable?, cuántas iteraciones de diseño se esperan, presupuesto de vértices [ver: presupuestos-poligonos].
- Para estilos low-poly estilizados nada de esto aplica igual: el facetado ES el look [ver: estilizacion-lowpoly].

### Runbook: un asset hard-surface de principio a fin

1. **Referencias**: blueprint/concept + fotos del objeto real o análogos; categoría del asset y presupuesto asignado [ver: blueprints-referencias] [ver: presupuestos-poligonos].
2. **Blockout de formas primarias**: solo masas y silueta, probado EN el engine con la cámara real del juego [ver: gamedev/arte-direccion §9]. Aquí se aprueba la proporción; nada de detalle todavía.
3. **Elegir workflow** con la tabla de arriba — y anotar la decisión (el asset #2 de la misma familia debe usar el mismo).
4. **Formas secundarias**: paneles, cortes grandes, mecánica visible. Booleans no-destructivos (§6); cada corte con lógica de fabricación (§9).
5. **Cierre según workflow**: subdivision → support loops + high denso + retopo + bake [ver: high-to-low]; mid-poly → bevels + weighted normals (§5); kitbash → limpieza según destino (§6).
6. **Terciario**: greebles, tornillería, texto — como decals/floaters/stamps siempre que no den silueta (§7).
7. **UVs y texturizado** según la vía elegida (única bakeada vs tileables/trims).
8. **Export y verificación en engine**: spec de escala/ejes/normals [ver: pipeline/arte-a-unity]; inspección final con material reflectante bajo la luz REAL del juego, girando el asset — el visor del DCC no aprueba nada.

## 4. Workflow subdivision (high-poly clásico)

La base técnica de topología (quads, poles, edge flow) está en [ver: topologia]; aquí lo específico de hard-surface.

Tres vías para endurecer un borde bajo subdivisión:

| Vía | Cómo | Pro | Contra |
|---|---|---|---|
| **Support loops** (holding edges) | Encerrar el borde entre dos loops cercanos; distancia loop-borde = radio del chaflán resultante | Universal, sobrevive a cualquier export | Densifica toda la malla por donde pasa el loop; puede distorsionar a lo largo de su recorrido (Topology Guides) |
| **Edge crease** | Peso de crease por arista que la subdivisión respeta | Malla base limpia, iteración rápida | No todos los formatos/pipelines de intercambio preservan creases — verificar antes de adoptarlo como estándar |
| **Bevel previo + subdivisión** | Chaflán real de 1-2 segmentos antes de subdividir | El radio queda explícito y editable | Más geometría base; los chaflanes que se cruzan exigen resolver esquinas |

Reglas de subdivisión hard-surface:
- **Poles (vértices de 3 o 5+ aristas)**: generan artefactos de reflexión. No siempre se pueden eliminar — se REUBICAN a zonas planas o poco visibles (Topology Guides). Prohibido un pole en mitad de una superficie curva reflectante.
- **Orden de trabajo**: curvatura primaria primero con malla MÍNIMA; los detalles de alta densidad (tornillos, ranuras, paneles) se añaden AL FINAL, cuando la curvatura base ya está congelada — detalles tempranos contradicen la curvatura y la abollan (Topology Guides: "keep the mesh simple", "add details last").
- **Verificación continua**: matcap de contraste alto o checker reflectante + girar el modelo; cada sesión de detalle termina con esta pasada.
- Los ngons son aceptables en caras totalmente planas que la subdivisión no toca; jamás en superficie curva.
- Cortes y agujeros en superficies curvas son EL problema clásico: al cortar se redistribuyen los loops alrededor del agujero manteniendo la curvatura original (si los loops se desvían, la curva se abolla). Si el agujero puede ser un decal (§7), suele ser mejor decal.

## 5. Workflow mid-poly: bevels + weighted normals

El workflow que domina en entornos y vehículos actuales. Definición del canon de polycount (wiki): face weighted normals = "añadir bevels y alterar las vertex normals para que queden perpendiculares en los polígonos planos grandes".

**Qué resuelven las weighted normals:** con normals promediadas por defecto, un bevel pequeño entre dos caras grandes reparte el gradiente de shading POR TODA la cara → superficie "inflada" y sucia. Ponderando la normal de cada vértice por el ÁREA de las caras adyacentes, las caras grandes quedan ópticamente planas y todo el gradiente se concentra en el bevel → shading limpio sin normal map. Es lo que un modificador tipo Weighted Normals o el promedio por área de la herramienta calcula automáticamente.

**El paquete mid-poly completo** (reportado en producción por Angelic/Metaverse Game Studios en 80.lv, y en la guía MIDPOLY de blacksteinn):

1. Una sola malla optimizada con bevels reales en todos los bordes visibles.
2. Weighted normals para shading limpio (a mano o por modificador).
3. Texturizado con tileables + trim sheets + decals (§7), no textura única bakeada — así un asset enorme mantiene texel density [ver: pipeline/arte-a-unity].
4. Bake opcional SOLO de detalle de superficie (tornillos, ranuras) desde floaters o en Substance, sin high-poly completo.

**Costes y límites (del hilo de polycount "Face weighted normals question and methods"):**

- Vértices: los bevels añaden geometría, PERO si la malla se unwrapea sin cortes en los bevels, se evita el doble-vértice de los hard edges — el coste real queda comparable a un low-poly con smoothing groups.
- **LODs**: los bevels finos a distancia producen sparkle/ruido; en algún LOD se eliminan y se vuelve a hard edges. Planificarlo desde el principio.
- Advertencia citada del hilo: "editar normals a mano es destructivo y no se reproduce con fiabilidad" — preferir el cálculo automático (modificador/área) sobre la edición manual vértice a vértice, y verificar que el export/import a engine preserva las custom normals (un reimport que recalcule normals destruye el asset silenciosamente).
- No es bala de plata: consenso del hilo — "ninguno es mejor en todo; funcionan en escenarios distintos". Hero props con textura única siguen queriendo bake clásico.

**Cuándo gana mid-poly**: assets grandes o modulares (naves, edificios, maquinaria, kits de entorno [ver: entornos-modulares]), equipos que iteran diseño con frecuencia (sin re-retopo ni re-bake por cada cambio — la razón #1 citada por Angelic), y pipelines con pocos artistas.

## 6. Booleans bien usados

**El workflow no-destructivo es la regla**: las operaciones booleanas se mantienen "vivas" (stack de modificadores, Live Booleans en ZBrush, historial CAD) con los objetos cortantes editables hasta el final. Beneficio: iterar el diseño moviendo/escalando cortadores sin remodelar. Solo se aplica/colapsa cuando el diseño está aprobado — y sobre una COPIA.

**¿Limpiar o no limpiar? Depende de a dónde va la malla:**

| Destino de la malla booleana | ¿Limpiar? |
|---|---|
| High-poly que SOLO se bakea | NO hace falta fusionar ni topologizar: el bake es un ray cast que solo ve la superficie (§10). Basta que el shading se vea bien: bevel/polish en los cortes (vía remesh denso + polish tipo Dynamesh, o bevel en las aristas del corte) |
| Render/cinemática | Igual que arriba: si el shading aguanta, la topología interna da igual |
| Mid-poly que va al juego | SÍ: eliminar caras internas, resolver slivers y n-gons problemáticos, bevel en las aristas del corte + weighted normals. Los ngons planos pueden quedarse si el engine triangula estable |
| Malla que se va a subdividir | SÍ, y a fondo: la subdivisión amplifica cualquier triángulo/pole del corte; reconstruir con loops [ver: topologia] |
| Malla que se va a deformar/animar | Limpieza total a quads con edge flow — o no usar booleans ahí |

**Pitfalls de boolean:**

- Caras coplanares entre operandos = resultado impredecible (z-fighting del algoritmo): desplazar el cortador una fracción para que atraviese de verdad.
- Corte sobre superficie curva: el agujero "pellizca" la curvatura; hace falta redistribuir loops alrededor (§4) o aceptar el artefacto si no se ve.
- Slivers (triángulos aguja) en las costuras: causan sombras/AO sucios en el bake; se detectan girando con matcap.
- Booleans encadenados vivos son pesados: agrupar cortadores y colapsar por etapas con copias de seguridad de los operandos.

## 7. Decals y detalle proyectado: geometría que no es geometría

Alternativa a modelar: proyectar el detalle. Tres familias, todas en producción real:

| Técnica | Qué es | Ejemplo shippeado (documentado) |
|---|---|---|
| **Normal/surface decals** | Planos flotantes o proyecciones diferidas (DBuffer en Unreal, URP Decal Projector en Unity) que mezclan normal/detalle sobre la superficie base | Workflow de Sergey Tyapkin (80.lv): FWN + tileables + decal sheets — "una nave de 100 metros con texel density alta sin bakear normal maps"; canon del pipeline de Star Citizen para naves (mezcla por canal en GBuffer, discutido en polycount) |
| **Geometry decals de borde** | Tiras de geometría con alpha-test pegadas sobre aristas para venderlas como rotas/desgastadas; se eliminan en LODs bajos | Fallout 3 (análisis de Simon Schreibt): piedra lisa + plano de "borde roto" con normal map; Cyberpunk 2077 usa POM decals para bordes rotos |
| **Trim sheets** | Una textura de tiras horizontales de detalle (molduras, rejillas, bordes CON su bevel bakeado) que toda la geometría del entorno mapea por UV | "The Ultimate Trim" — Morten Olsen, GDC 2015: técnica con la que el equipo pequeño de entorno de Insomniac texturizó el open world de Sunset Overdrive; los bevels de borde vienen "falsos" en la normal del trim |

Reglas de uso:

- **Decal antes que geometría** para: paneles, tornillos, rejillas, texto/señalética, costuras, daños localizados — todo lo que no afecta la silueta.
- Para que el decal se funda con la base (técnica discutida del pipeline de Star Citizen en polycount): el material del decal se mezcla por canal con el de la superficie (solo normal, o normal+roughness), y el tileable de base puede muestrearse triplanar para que el parche coincida con lo de abajo. El caso de uso declarado: "cualquier hard-surface tan grande que el texturizado único es imposible".
- La geometría solo es obligatoria donde hay SILUETA o el jugador se acerca lo bastante para ver el paralaje del plano flotante.
- Decals de normal exigen consistencia: mismo espacio tangente y convención de canal verde que el resto del proyecto [ver: high-to-low] [ver: pipeline/arte-a-unity].
- Coste render: los decals diferidos tienen coste por píxel cubierto; cientos de decals grandes solapados son un problema de fill rate — presupuestarlos como se presupuestan tris.
- Los geometry decals se planifican con los LODs: son lo primero que se apaga con la distancia (así lo hacía Fallout 3).

## 8. Kitbashing: usar y crear kits

Ensamblar modelos nuevos a partir de piezas prefabricadas (combinar, escalar, recomponer). Heredero directo del model-making de cine: los greebles de ILM en Star Wars se hacían pegando piezas de maquetas comerciales sobre formas base (§9). Hoy es industria: KitBash3D (fundada 2017) vende kits usados por estudios de cine y juegos.

**Usar kits (comprados o internos):**

- Ideal para: concepting 3D rápido, blockouts creíbles, fondos/mid-ground, greebles mecánicos.
- ⚠️ Un kit comercial NO es game-ready por defecto: auditar polycount, materiales (¿cuántos por pieza?), escala y pivots contra la spec del proyecto [ver: pipeline/arte-a-unity] antes de dejarlo entrar al repo.
- ⚠️ Drift de estilo: piezas de kits distintos mezclan lenguajes de formas y densidades de detalle; el resultado "Frankenstein" viola la dirección de arte [ver: gamedev/arte-direccion]. Regla: máximo 1-2 kits por familia visual, y repintar/retexturizar a la paleta del proyecto.
- Piezas de kit en primer plano se delatan: reservar kitbash para lo que no se inspecciona de cerca, o retrabajar la pieza.

**Crear kits propios (la inversión que amortiza):**

1. Definir el lenguaje de formas del kit (ángulos característicos, radios de bevel, densidad de greeble) ANTES de la primera pieza — el kit entero debe parecer diseñado por la misma "fábrica".
2. Escala y grid consistentes: todas las piezas snapean a la misma grilla y comparten texel density [ver: entornos-modulares].
3. Prioriza variedad de categoría sobre cantidad total de piezas: conectores, paneles, cilindros mecánicos, bordes/marcos, vents, cables — un kit chico con esas categorías cubiertas se reutiliza más que uno enorme y desordenado (NO hay cifra de pieza óptima con fuente publicada verificada; calibrar por prueba con el equipo).
4. Cada pieza con bevels y normals ya resueltos (mid-poly, §5) para que lo ensamblado sea usable directo.
5. El kit se documenta con una lámina de contacto (render de todas las piezas) o nadie lo reutiliza.

## 9. Precisión e intención: panel lines, greebles y storytelling

El detalle hard-surface NO es ruido decorativo — es diseño. Los tres niveles de lectura estándar: **forma primaria** (silueta, se lee a cualquier distancia), **secundaria** (paneles, cortes grandes, se lee a media distancia), **terciaria** (tornillos, texto, arañazos, se lee de cerca). Detallar terciario sobre una primaria débil es maquillar un cadáver: la silueta se aprueba primero [ver: gamedev/arte-direccion §5].

- **Panel lines con lógica de fabricación**: cada línea de panel implica que ALGO se ensambla, se abre o se atornilla ahí. Paneles de acceso donde habría mantenimiento, costuras donde piezas grandes se unirían, tornillería en los bordes de los paneles, no al azar. Un corte sin razón fabricable lee como falso aunque esté limpio.
- **Greebles**: detalle mecánico pequeño que "sugiere función mecánica sin necesariamente tener un propósito real" y crea ilusión de escala (definición del canon: "greeblies" acuñado por George Lucas en los 70 para los detalles de las maquetas de naves de Star Wars, muchas construidas pegando piezas de kits de modelismo comerciales sobre formas base — precedente directo del kitbashing de hoy; el término "nurnies" es de una producción distinta, Babylon 5, acuñado por Ron Thornton en Foundation Imaging para el mismo tipo de detalle CGI). Reglas: densidad de greeble VARIABLE (zonas densas contra zonas de descanso — mismo principio de readability del arte 2D [ver: gamedev/arte-direccion §5]); los greebles siguen la dirección estructural del objeto; a mayor densidad de greeble percibida, más grande parece el objeto — es la herramienta #1 de escala en naves.
- **Storytelling del objeto** (breakdown de Akshat Rastogi en 80.lv): "un prop debe contar una historia — eso es lo que lo hace único". Método: escribir 1-2 frases de historia del objeto (quién lo usó, cuánto tiempo, cómo lo trató) ANTES de detallar; el desgaste se concentra donde hay CONTACTO y USO reales (asas, esquinas golpeadas, zonas de roce), estudiado de referencias de objetos reales envejecidos — nunca desgaste uniforme "por todos lados".
- La función dicta la forma: pistones que podrían moverse, cables que van de un punto a otro real, bisagras del lado que abre. El espectador no sabe por qué un mech "se ve mal", pero su cerebro detecta mecánica imposible.

## 10. El high-poly que solo existe para bakear: qué tan limpio

Verdad liberadora del canon de baking: **el bake es una proyección de rayos que solo ve la SUPERFICIE del high-poly** [ver: high-to-low]. De ahí:

| No importa (si solo se bakea) | Sí importa |
|---|---|
| Topología interna: ngons, triángulos, poles en zonas planas | Que el SHADING de la superficie sea limpio (el bake captura el shading, incluidos sus errores) |
| Mallas intersectadas sin fusionar (booleans sin limpiar, piezas encajadas) | Que no haya huecos/gaps visibles a la escala del ray cast |
| **Floaters**: detalles (tornillos, paneles) flotando SOBRE la superficie sin tocarla — se proyectan al bake como si estuvieran unidos; técnica estándar | Silueta del low-poly suficientemente cercana: la "waviness" del bake en superficies curvas es resultado natural de la diferencia low/high (hilo canon de EarthQuake en polycount) — se reduce con más segmentos en el low, no limpiando el high |
| Que sea "watertight" o un solo objeto | Densidad suficiente: la malla high debe ser lisa donde debe ser lisa (facetado del high = facetado bakeado) |
| UVs del high-poly (no necesita) | Hard edges del LOW en las costuras UV — regla del canon: "hard edge donde hay seam es gratis" en vértices (hilo de EarthQuake) |

- Corolario: perseguir quads perfectos en un high-poly de bake es tiempo tirado. La limpieza se invierte donde se VE: shading de superficie y bordes.
- Recordatorio del mismo canon: la normal map tangente es específica de la geometría low sobre la que se bakeó — tocar el low (o sus normals, o sus UVs) después del bake invalida el mapa [ver: high-to-low].
- El detalle fino (tornillería, ranuras) puede ni siquiera ser malla: alphas/stamps en el sculpt o directamente en el texturizado.

Checklist pre-bake del high-poly (el proceso completo de bake — cage, match por nombre, padding — vive en [ver: high-to-low]):

- [ ] Superficie lisa donde debe serlo: pasada de matcap sin facetado ni abolladuras.
- [ ] Todos los bordes con chaflán/redondeo lo bastante ancho para caer en varios texels a la resolución del bake.
- [ ] Floaters pegados a distancia mínima de la superficie (que la proyección los capture sin halos).
- [ ] Sin huecos visibles entre piezas intersectadas a la distancia de inspección del asset.
- [ ] El LOW congelado: segmentos suficientes en curvas (anti-waviness), hard edges en seams UV, custom normals finales.
- [ ] Piezas emparejadas high↔low (por nombre o explosión) para evitar proyecciones cruzadas entre partes vecinas.

## Reglas prácticas

1. Elige workflow POR ASSET con la tabla del §3: textura única + hero → subdivision/bake; grande/modular/iterativo → mid-poly; explorar diseño → boolean/kitbash.
2. Todo borde visible lleva bevel — por geometría, subdivisión o normal map. Cero filos de 90° puros en el juego.
3. Calibra el ancho de bevel al tamaño en pantalla a distancia real de cámara; lo que no llega a 1-2 px no existe, exagera ligeramente.
4. Verifica shading con matcap de alto contraste girando el modelo — cada sesión, no al final.
5. En subdivision: curvatura primaria con malla mínima primero, detalles al final; poles reubicados a zonas planas/ocultas.
6. Mid-poly: weighted normals calculadas por área (modificador), no editadas a mano; confirma que el export a engine preserva custom normals.
7. Mid-poly: planifica desde el día 1 el LOD que elimina los bevels finos y vuelve a hard edges.
8. Booleans siempre no-destructivos hasta aprobación del diseño; colapsar sobre copia, con operandos guardados.
9. Limpia booleans según destino (tabla §6): bake = no fusionar; juego = caras internas fuera + bevels en cortes; subdivisión = reconstrucción completa.
10. Nunca caras coplanares entre operandos de un boolean; el cortador atraviesa de verdad.
11. Decal antes que geometría para todo detalle sin silueta (paneles, tornillos, rejillas, daños); geometría solo donde hay silueta o primer plano.
12. Geometry decals de borde se apagan en LODs — planificado, no descubierto.
13. Kit comercial: auditoría de polycount/materiales/escala/pivots contra la spec ANTES de entrar al proyecto; máximo 1-2 kits por familia visual, retexturizados a la paleta propia.
14. Kit propio: lenguaje de formas + grid + texel density definidos antes de la pieza 1; lámina de contacto o no se reutiliza.
15. Jerarquía primaria→secundaria→terciaria: la silueta se aprueba antes de detallar; densidad de detalle variable con zonas de descanso.
16. Cada panel line con lógica de fabricación (acceso, ensamble, tornillo); cada greeble siguiendo la estructura; desgaste solo donde hay contacto y uso — escribe la historia del objeto en 1-2 frases antes de detallar.
17. High-poly de bake: floaters e intersecciones bienvenidos; invierte la limpieza en el shading de superficie, no en la topología interna.
18. Waviness en el bake de curvas = añadir segmentos al LOW, no limpiar el high; hard edges del low en las costuras UV.
19. Después del bake, el low-poly (geometría, normals, UVs) queda CONGELADO; cualquier cambio = re-bake.
20. Presupuestos numéricos de tris/texturas por categoría: [ver: presupuestos-poligonos]; specs de entrega a engine: [ver: pipeline/arte-a-unity].

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Filos de 90° "porque el concept los tiene" — look CAD/juguete barato | Regla #2: bevel en todo borde visible; el concept es dibujo, el modelo vive con luz real |
| Bevels tan finos que desaparecen o hacen sparkle a distancia de juego | Ancho por tamaño en pantalla; LOD que los elimina (regla #7) |
| Superficie "inflada" o gradientes sucios en caras grandes con smooth shading | Weighted normals por área; el gradiente se concentra en el bevel (§5) |
| Custom normals destruidas silenciosamente al importar al engine (recálculo automático) | Verificar el asset EN el engine con material reflectante tras el primer import; fijar la opción de import de normals en la spec |
| Elegir high-to-low para un asset de 20 metros y quedarse sin texel density | Assets grandes = mid-poly + tileables/trims/decals (§5, §7) |
| Perseguir quads perfectos en un high-poly que solo se bakea | Solo la superficie importa: floaters e intersecciones OK (§10) |
| Waviness en el bake y "arreglarla" retocando el high-poly | Es la diferencia de curvatura low/high: más segmentos en el low (canon EarthQuake) |
| Boolean aplicado destructivamente al primer día y el diseño cambia | No-destructivo hasta aprobación; operandos guardados |
| Boolean con caras coplanares → caras fantasma/z-fighting | Desplazar el cortador para que atraviese |
| Agujero booleano en superficie curva que abolla el reflejo | Redistribuir loops alrededor del corte manteniendo curvatura, o convertirlo en decal |
| Modelar tornillos/rejillas/paneles en geometría en todo el entorno | Decals/trims para lo que no da silueta; la geometría es el recurso caro (§7) |
| Kitbash "Frankenstein": piezas de 4 kits con lenguajes de forma distintos | 1-2 kits por familia + retexturizado a la paleta; auditar contra el visual target [ver: gamedev/arte-direccion] |
| Kit comercial de cine metido directo al juego (100k tris, 8 materiales por pieza) | Auditoría de game-readiness antes de entrar (regla #13) |
| Greebles uniformes por toda la superficie "para que se vea complejo" | Densidad variable con zonas de descanso; los greebles sugieren función y escala, no rellenan |
| Panel lines aleatorias sin lógica de ensamblaje | Cada corte responde a fabricación/acceso; si no tiene razón, fuera |
| Desgaste espolvoreado uniforme (edge wear generator al 100%) | Historia del objeto primero; desgaste solo en zonas de contacto/uso real (Rastogi, 80.lv) |
| Detallar terciario sobre una silueta no aprobada | Primaria → secundaria → terciaria; blockout aprobado en engine primero [ver: gamedev/arte-direccion] |
| Tocar el low-poly después del bake "solo un poquito" | Normal map tangente = específica de esa geometría; cualquier cambio invalida el bake |

## Fuentes

- **Understanding averaged normals and ray projection / Who put waviness in my normal map** — usuario "EarthQuake", hilo canon en polycount.com (discussion 81154) — por qué la waviness es resultado natural del delta low/high, cages y dirección de rayos, "hard edge en seam UV es gratis", normal map tangente atada a su geometría. Consultado directo. ⚠️ El nombre real y la afiliación a Marmoset atribuidos a "EarthQuake" en investigaciones previas NO se pudieron confirmar (wiki.polycount.com y marmoset.co bloqueados) — se cita solo por su alias de foro.
- **Face weighted normals question and methods** — polycount.com (discussion 213802) — FWN vs bake, coste en vértices según UV splits, problema de bevels finos en LODs, advertencia sobre edición manual de normals. Consultado directo.
- **Face weighted normals** — polycount wiki (wiki.polycount.com/wiki/Face_weighted_normals) — definición canónica ("añadir bevels y alterar las vertex normals perpendiculares en los polígonos planos grandes"). ⚠️ El wiki estaba caído al momento de consulta (ECONNREFUSED); definición recuperada vía extracto de buscador — reverificar cuando vuelva.
- **Creating Assets Within the Mid Poly Workflow in UE5** — Malte Resenberger-Loosmann (Hard-surface & Material Lead, Angelic / Metaverse Game Studios), 80.lv — mid-poly en producción real: una malla, FWN, bevels por presencia en pantalla, iteración sin re-retopo/re-bake, UVs conectadas con menos padding. Consultado directo.
- **Decal Technique for Hard Surface Scenes** — Sergey Tyapkin, 80.lv — FWN + tileables + decal sheets + DBuffer decals en UE: nave de 100 m con texel density alta sin bake ni textura única. Consultado directo.
- **The Ultimate Trim: Texturing Techniques of Sunset Overdrive** — Morten Olsen (Insomniac Games), GDC 2015 (GDC Vault play/1022323; slides en SlideShare) — trim sheets estandarizados con bevels "falsos" en la normal para que un equipo chico de entorno texturizara un open world. Metadatos y tesis verificados vía múltiples fuentes; el detalle fino del layout de trims no se verificó contra el video.
- **Game Art Tricks #1: Fallout 3 – Edges** (+ #85 Cyberpunk: Broken Edges) — Simon Schreibt (simonschreibt.de) — geometry decals con alpha-test para bordes rotos sobre geometría low, eliminados en LODs; POM decals en Cyberpunk 2077. Consultado directo.
- **Topology Guides** — Johnson Martin (topologyguides.com): índice + "Dealing with Mesh Artifacts in Subdivision Modeling" — poles reubicables, holding edges vs creases, malla mínima primero y detalles al final, matcaps de contraste para detectar distorsión; catálogo de guías hard-surface (panel lines, chamfered cuts, holes en curvas). Consultado directo.
- **Greeble** — Wikipedia — "greeblies" acuñado por George Lucas en la producción de Star Wars (naves construidas pegando piezas de kits de modelismo comerciales); "nurnies" es término aparte de Ron Thornton/Foundation Imaging para Babylon 5; definición "sugiere función mecánica sin propósito real", ilusión de escala. Consultado directo, reverificado.
- **Step by Step Guide on Creating a Photorealistic Used Wooden Box** — Akshat Rastogi, 80.lv — método de storytelling: historia del objeto antes de detallar, desgaste en zonas de contacto/uso, referencias de objetos reales envejecidos. Consultado directo.
- **KitBash3D (about/blog) + resultados de búsqueda sobre kitbashing** — kitbash3d.com — definición, origen en el model-making físico, fundada 2017, clientes cine/juegos. Nivel extracto de buscador, no artículo completo.
- **MIDPOLY: The Ultimate Guide with All Working Nuances** — blacksteinn / Mikhail Kalabin, blog de ArtStation — tesis del midpoly: "forma suave y chaflanes mayores por geometría sin bakear normal desde otra malla". Solo extracto (ArtStation bloquea el fetch); usado únicamente para corroborar la definición.
