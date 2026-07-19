# Fundamentos de la malla 3D

> **Cuando cargar este archivo:** antes de modelar, encargar, revisar o depurar CUALQUIER modelo 3D de juego — define la anatomía de la malla, normales y shading, escala, pivots, qué hace "game-ready" a un modelo y el vocabulario del oficio. Es la base de toda la fase de modelado [ver: topologia] [ver: high-to-low].

## 1. Anatomía de la malla: vértice, edge, cara

Toda malla poligonal se compone de tres elementos (definiciones del manual de Blender, válidas en cualquier software):

| Elemento | Definición | Nota operativa |
|---|---|---|
| **Vértice** (vertex) | Punto en el espacio 3D; extremo de las aristas | Es la unidad de coste real en GPU (§2) |
| **Edge** (arista) | Segmento que conecta dos vértices; frontera entre caras | Las herramientas de selección/flujo operan sobre edges |
| **Cara** (face/polygon) | Superficie definida por 3+ edges; es lo que recibe shading | Solo las caras se renderizan; edges y vértices son estructura |

### Tris, quads y ngons

| Tipo | Definición | Al renderizar | Al deformar/subdividir |
|---|---|---|---|
| **Tri** (triángulo) | Cara de 3 vértices | Es lo ÚNICO que la GPU dibuja; todo se convierte a tris al cargar en el engine | Deforma de forma predecible pero no da edge loops; aceptable en low-poly final |
| **Quad** | Cara de exactamente 4 vértices | Se divide en 2 tris al exportar — la diagonal puede caer en dos direcciones ("ridge" o "valley") | El formato de trabajo: permite edge loops, buen flujo de deformación y sculpt/subdivisión sin pellizcos |
| **Ngon** | Cara de 5+ vértices | El engine/exportador la triangula como quiera — resultado impredecible | Rompe los loops (un face loop se detiene en tris y ngons), pellizca al subdividir; prohibido en mallas finales |

Hechos clave (Polycount wiki, *Polygon Count*):

- Cuando un artista de juegos dice "poly count" quiere decir **triangle count**. El contador de polígonos del software de modelado engaña: el número real es el de tris tras la conversión. Configurar el contador en tris siempre.
- **La triangulación no es determinista entre herramientas**: la misma malla en quads puede triangularse distinto en el DCC, el baker y el engine. Un quad triangulado distinto entre bake y render produce shading en zigzag (errores "en X"). Antídoto: **triangular explícitamente antes de bakear y exportar** esa triangulación (Marmoset, *Toolbag Baking Tutorial*: la variación de la diagonal cambia la tangent basis).
- Los quads no existen para la GPU: existen para el ARTISTA — selección por loops, lectura del flujo, skinning. Se preservan durante el modelado y se triangulan al final del pipeline.
- Rango real de un asset de juego: desde 2 tris (un billboard) hasta 40,000+ tris (personaje complejo) — la cifra por categoría se decide por proyecto [ver: presupuestos-poligonos].

### Trabajo por tipo de malla (Polycount wiki, *Topology*)

| Destino de la malla | Regla de topología |
|---|---|
| Base para sculpt (ZBrush/Mudbox y similares) | Quads casi exclusivos — los tris pellizcan al esculpir |
| Modelo sub-d (subdivisión, high-poly) | Edge loops correctos son críticos; la subdivisión amplifica cada defecto |
| Low-poly final de juego | Tris aceptables, pero **cada edge debe existir por una razón** (silueta, deformación, shading o UV) |

## 2. El vértice de GPU no es el vértice del modelador

El dato más importante que el software de modelado te oculta (Polycount wiki, *Polygon Count*):

- **El vertex count real manda sobre el triangle count** para rendimiento y memoria, pero por costumbre se habla en tris.
- La GPU exige duplicar un vértice cada vez que sus atributos difieren entre caras adyacentes. Se duplica en: **costuras de UV (seams), cambios de smoothing (hard edges), cambios de material**. Cada uno de esos es "una rotura física" de la superficie para el renderer.
- Consecuencia: abusar de hard edges, sobre-fragmentar UVs o asignar materiales de más multiplica el vertex count real aunque el triangle count no cambie. Eso estresa la etapa de transformación y la memoria (y provoca fallos de vertex cache — Polycount wiki, *GameRenderingTerminology*).
- Truco de estimación: el contador de **vértices UV** aproxima mejor el coste real que el de vértices de malla. No obsesionarse con el número exacto: sentido común y no derrochar.
- La optimización rinde donde hay volumen: personajes principales, objetos muy instanciados y escenas de estrés — no en el prop que aparece una vez (Provost, *Beautiful, Yet Friendly*: el cuello de botella alterna entre transform-bound y fill-bound; controlar qué se VE pesa más que pulir un mesh).

**Regla de oro derivada**: alinear las tres roturas. Donde ya hay una costura de UV, un hard edge es casi gratis (el vértice ya está partido); un hard edge en medio de una isla UV sí añade coste Y artefactos de bake (§3).

## 3. Normales y shading

### Normal de cara y normal de vértice

| Concepto | Qué es | Para qué |
|---|---|---|
| **Face normal** | Vector perpendicular al plano de la cara; una por cara | Orientación de la cara (dentro/fuera), flat shading, backface culling |
| **Vertex normal** | Vector por vértice, normalmente el promedio de las caras que lo comparten | El engine compara luz vs vertex normal para iluminar: TODO el shading suave sale de aquí (Polycount wiki, *VertexNormal*) |

- **Flat shading**: cada cara usa su face normal → facetado, aristas duras en todo. **Smooth shading**: normales promediadas por vértice → superficie continua aunque la geometría sea angulosa (Topology Guides, *Encyclopedia*).
- Un **hard edge** es un vértice con normales partidas: cada lado del edge usa su propia normal. **Smoothing groups** (término de 3ds Max) y **Harden/Soften Edge** (Maya) son la misma operación con otra interfaz: partir o unificar vertex normals (Polycount wiki, *Smoothing Groups*).
- Las caras tienen UNA sola dirección visible por defecto: los engines descartan la cara trasera (**backface culling**). Cara invertida = cara invisible o negra en el juego (§7).

### La regla hard edge ↔ UV seam

Canon del game art (Polycount wiki *Smoothing Groups* + foro Polycount, thread de EarthQuake + Marmoset):

1. **Todo hard edge DEBE coincidir con una costura de UV.** Hard edge sin split de UV = artefacto de seam en el bake (cada cara intenta bakear sobre la línea del edge).
2. Lo inverso NO aplica: puede (y suele) haber más costuras de UV que hard edges — las costuras extra reducen el warping de textura.
3. Poner hard edges EN las costuras de UV de un asset hard-surface suaviza los gradientes del normal map → el bake aguanta mejor mipmaps, LODs y compresión [ver: hard-surface].
4. Como el UV seam ya duplica el vértice, el hard edge ahí no añade coste (§2).

### Cuándo hard edge y cuándo geometría

- Superficie orgánica que deforma: todo smooth, sin hard edges; la topología resuelve el shading [ver: organico-personajes].
- Hard-surface: hard edges en ángulos ≥ ~fuertes con su UV split, O bevels/chamfers con smooth shading. Los engines necesitan algo de geometría cerca de esquinas muy duras o las vertex normals "pelean" con el normal map (Polycount wiki, *VertexNormal*).
- **Face weighted normals (FWN)**: técnica para hard-surface sin bake — bevel en las aristas + normales forzadas perpendiculares en las caras grandes, de modo que toda la transición de shading vive en el bevel pequeño. Coste: los bevels crean triángulos finos y largos, que rinden mal (fill rate) — dosificar (Polycount wiki, *Face weighted normals*).

### Tangent basis: por qué el normal map depende de la malla

Resumen mínimo aquí; el pipeline completo de bake vive en [ver: high-to-low]:

- Un normal map tangent-space se interpreta usando la **tangent basis** de cada vértice: normal + tangente (derivada de las UVs) + bitangente. Cambias las vertex normals o las UVs → cambias cómo se lee el mapa (Polycount wiki, *Normal Map Technical Details*).
- Hay múltiples formas de calcular la base; **MikkTSpace es la más común** y es la que usan Unity y Unreal — bakear y renderizar con la MISMA tangent basis ("synced workflow") o habrá seams y shading sucio (Marmoset, *Toolbag Baking Tutorial*).
- **Handedness**: el canal verde (Y) del normal map puede ir en + (OpenGL/Maya/Blender/Unity/Toolbag) o − (DirectX/3ds Max/Unreal/Source). Mapa que se ve "hundido donde debería salir" = canal verde invertido (tabla completa en Polycount wiki, *Normal Map Technical Details*).
- Exportar en un formato que guarde tangentes (FBX) asegura que las del bake sean las del render.

## 4. Escala real y unidades

**Regla: 1 unidad = 1 metro, siempre, desde el primer blockout.** Referencias verificadas:

- Unity asume "1 m en el mundo del juego = 1 unidad del archivo importado" y su física lo da por hecho (manual del FBX Importer; spec de entrega y verificación contra un cubo de 1 m en [ver: pipeline/arte-a-unity]).
- glTF 2.0 (spec Khronos): "las unidades de todas las distancias lineales son metros"; sistema right-handed, +Y arriba, el frente del asset mira a +Z.
- Cada DCC tiene su convención de unidades y ejes internos — lo que importa es que el par DCC↔engine esté verificado UNA vez (export de prueba contra un cubo de 1 m) y congelado en la spec.

Por qué la escala incorrecta rompe todo lo demás:

| Sistema | Qué rompe una escala errónea |
|---|---|
| **Física** | La gravedad y las fuerzas están en unidades del mundo real (m/s²). Un personaje al doble de escala cae "en cámara lenta" relativo a su tamaño; uno a la mitad parece de plomo. Masas, colisiones e inercias quedan absurdas |
| **Iluminación** | La atenuación de las luces y los sistemas físicos de exposición calculan con distancias reales; una escena a 10x recibe luz que "no llega" o quema. GI y lightmaps calculan texel density y rebotes contra el tamaño real |
| **Rigging/animación** | Retargeting y sistemas humanoides esperan proporciones humanas (~1.8 m de alto); un rig fuera de escala rompe reutilización de animaciones y root motion |
| **Bakes** | Las distancias de proyección, offsets de cage y rangos de height map se expresan en unidades de escena (Marmoset: height inner/outer "in scene units") — con escala rara, los valores por defecto de cualquier baker fallan |
| **Ensamblado** | Assets de distintos autores/orígenes no encajan; los kits modulares dejan de snapear [ver: entornos-modulares] |

Antídoto único: escena plantilla con un cubo de 1 m y una figura humana de 1.8 m como referencia permanente; todo asset se modela junto a ellas. **La escala se corrige en el modelo o en el importer del engine, jamás con el scale del Transform en escena** [ver: pipeline/arte-a-unity].

## 5. Pivots y orígenes

El pivot (origen del objeto) define cómo el asset se coloca, rota y snapea. Se decide POR USO, no por defecto del software:

| Tipo de asset | Pivot | Por qué |
|---|---|---|
| Personaje, edificio, árbol, prop de suelo | En la BASE, centrado (entre los pies) | Colocar en Y=0 y apoya solo; drag-and-drop a terreno |
| Prop agarrable (arma, herramienta) | Punto de agarre | El attach a la mano es identidad, sin offsets mágicos [ver: props-armas] |
| Puerta, palanca, tapa | El eje de giro (bisagra) | Rotar el transform ES abrir la puerta |
| Módulo de kit (pared, piso) | Esquina o centro CONSISTENTE en todo el kit | Snapping en grilla; un módulo con pivot distinto rompe el kit [ver: entornos-modulares] |
| Rueda, hélice, ventilador | Centro exacto de rotación | Girar sin bambolear [ver: vehiculos] |
| Proyectil / VFX mesh | Centro, +Z hacia adelante | La dirección de vuelo es el forward del transform |

Reglas transversales:

- El pivot se define en el DCC ANTES de exportar; el modelo vive en el origen (0,0,0) del archivo, orientado al frente convencional del proyecto.
- Transformaciones congeladas/aplicadas al exportar (posición/rotación/escala "limpias"): el criterio de aceptación en engine es instancia con rotación (0,0,0), escala (1,1,1), apoyada en Y=0 [ver: pipeline/arte-a-unity].
- Los bakers también lo agradecen: transforms sin resetear producen proyecciones y normales sesgadas (Polycount wiki, *Texture Baking*: Reset Transforms).

## 6. Game-ready vs render offline

Lo que separa un modelo de juego de uno de cine/archviz — el error nº1 de quien viene de render (o de un generador 3D genérico) es entregar un modelo "de render" como si fuera de juego:

| Dimensión | Game-ready (tiempo real) | Offline (cine/archviz/stills) |
|---|---|---|
| Presupuesto | Tris contados por categoría; cada edge justificado por silueta/deformación/shading | Densidad casi libre; se subdivide en render (sub-d/displacement) |
| Detalle fino | BAKEADO: high-poly → normal/AO/curvature sobre un low-poly (Marmoset: capturar superficies "demasiado densas para usarse directamente") | En la geometría misma o displacement al render |
| Topología | Low-poly triangulable, silueta primero, vertex splits controlados (§2) | Quads sub-d limpios; el flujo para deformación manda (escuela Pixar/Hippydrome) |
| Silueta | Los polígonos se gastan donde definen silueta; el normal map NO cambia la silueta (Marmoset) | La subdivisión da curvatura "gratis" |
| Materiales | Pocos por modelo (ideal 1 en props — cada uno rompe batching), texturas en atlas/trim sheets | Decenas de materiales/AOVs sin problema |
| UVs | Obligatorias, sin solapes en el rango 0-1 (+UV2 para lightmaps), padding para mips | Opcionales (procedurales, Ptex, UDIMs múltiples) |
| Escala/pivot | 1u = 1 m + pivot por uso (§4, §5) — el asset se instancia en un mundo | La escena se compone a mano una vez |
| LODs | `_LOD0..n` como parte de la entrega | No existen |
| Tangent space | Sincronizado con el engine (MikkTSpace) (§3) | Irrelevante si no hay normal maps de bake |
| Criterio de "listo" | Se ve bien EN el engine, con la luz y cámara del juego [ver: gamedev/arte-direccion] | Se ve bien en el frame final |

Un modelo de sculpt/render se convierte en game-ready por el pipeline high→low: retopo/optimización + UV + bake + texturas PBR [ver: high-to-low]. Nunca "importando y ya".

## 7. Geometría rota: qué es y por qué revienta engines y bakes

La lista de "evitar siempre" del canon (Polycount wiki *Topology*: "Avoid T-vertices, doubled faces, gaps, flipped faces, internal unseen faces, floating vertices") + tipos non-manifold del manual de Blender.

### Non-manifold

Geometría **manifold** ("water-tight"): define un volumen cerrado sin auto-intersecciones donde las normales apuntan coherentes hacia fuera (o dentro). **Non-manifold** = geometría que no puede existir en el mundo real; rompe toda operación que necesite saber qué es dentro y qué es fuera: booleans, fluidos/refracción, impresión 3D, y en juegos: bakes de AO/thickness, generación de colisión y navmesh, sombras. Tipos exactos (manual de Blender):

| Tipo non-manifold | Descripción |
|---|---|
| Bordes y agujeros | Edges con UNA sola cara conectada (la superficie tiene "borde de papel") |
| Wire | Edges o vértices que no pertenecen a ninguna cara |
| Caras interiores | Edges conectados a TRES o más caras (una pared interna colgando de una superficie) |
| Vértice compartido | Un vértice que une caras no adyacentes (dos conos tocándose por la punta) |

Nota: no todo borde abierto es un bug — un plano de suelo o un cartel tienen bordes por diseño. Lo que es SIEMPRE bug: wire, caras interiores y vértices compartidos.

### Catálogo de defectos, síntoma y antídoto

| Defecto | Qué es | Síntoma en el juego/bake | Antídoto |
|---|---|---|---|
| **Caras invertidas** (flipped normals) | Face normals apuntando hacia dentro | Caras invisibles o negras por backface culling; AO y thickness bakeados al revés | Visualizar orientación de caras SIEMPRE antes de exportar; recalcular normales hacia fuera |
| **Doubles** | Vértices/caras duplicados superpuestos | Z-fighting (parpadeo), shading roto, edges que "no sueldan", bakes con manchas | Merge por distancia tras cada operación de espejo/unión; auditar contador de vértices |
| **T-vertex** | Vértice apoyado en medio del edge de otra cara sin conectarlo | Huecos y seams de un píxel al renderizar (Polycount wiki, *GameRenderingTerminology*) | Conectar el vértice a la cara vecina o rehacer la unión |
| **Caras internas ocultas** | Geometría encerrada dentro del modelo | Coste invisible; sombras/AO sucios; rompe bakes | Borrar todo lo que la cámara jamás verá |
| **Vértices flotantes** | Vértices sin cara (wire) | Bounding box inflada, exportadores que fallan, selección fantasma | Limpieza de elementos sueltos antes de exportar |
| **Gaps** | Huecos entre caras que deberían estar soldadas | Rayitas de luz atravesando el modelo; seams de smooth shading | Weld de vértices coincidentes; revisar con luz detrás del modelo |
| **Ngons residuales** | Restos de booleans/caps | Triangulación impredecible, shading sucio, loops rotos (§1) | Re-toparlos a quads/tris intencionales, sobre todo tras booleans [ver: hard-surface] |
| **Escala/rotación sin aplicar** | Transform del objeto ≠ identidad | Modelo gigante/miniatura/girado en engine; normales y bakes sesgados | Aplicar transformaciones antes de exportar (§5) |
| **Auto-intersecciones** | Caras que se atraviesan | Sombras y AO imposibles, física errática | Modelar limpio o separar en piezas con intención |

Los defectos de esta tabla son el checklist de auditoría previa a TODO export y a todo bake. La mayoría del software de modelado incluye selección de non-manifold y limpieza por distancia — correrlas es gratis; depurar un bake sucio no.

## 8. Glosario operativo del oficio

Vocabulario estándar (fuentes: manual de Blender, Topology Guides *Encyclopedia*, Polycount wiki). En inglés porque así se habla el oficio:

| Término | Definición operativa |
|---|---|
| **Edge loop** | Cadena de edges a través de quads consecutivos; termina en un pole o borde, si no es cíclica. Herramienta central de topología [ver: topologia] |
| **Edge ring** | Los edges "paralelos" a lo largo de un face loop (los travesaños de la escalera, si el loop son los rieles) |
| **Face loop** | Cadena de quads consecutivos; se detiene en tris y ngons |
| **Edge flow** | La dirección/contorno que siguen los loops sobre la forma (p. ej. alrededor del ojo) |
| **Pole** | Vértice donde convergen 3, 5 o más edges (4 es lo regular). Desvía los loops y abolla superficies subdivididas: colocarlos en zonas planas y lejos de deformación (Polycount wiki, *Topology*) |
| **Bevel** | Redondear una arista sustituyéndola por segmentos; controla el highlight del borde |
| **Chamfer** | Bevel plano de un solo corte (bisel a ~45°) |
| **Extrude** | Extender caras/edges hacia afuera creando geometría nueva |
| **Inset / Outset** | Extruir una cara hacia dentro/fuera de sí misma creando un anillo de caras |
| **Boolean** | Combinar/sustraer/intersectar mallas; deja ngons y non-manifold si no se limpia después |
| **Weld / Merge** | Fusionar vértices en uno |
| **Crease** | Peso por edge que resiste la subdivisión (mantiene el filo bajo sub-d) |
| **Subdivision surface (sub-d)** | Algoritmo de suavizado (Catmull-Clark) que multiplica la malla; base del modelado high-poly |
| **Box modeling** | Partir de un cubo/primitiva y extruir hasta la forma |
| **Poly/edge modeling** | Construir edge a edge siguiendo los flujos principales |
| **NURBS / CAD** | Modelado matemático de superficies (producto/ingeniería); casi no se usa en juegos, pero llega como origen de assets a convertir |
| **Base mesh** | Malla genérica de partida para sculpt |
| **Blockout** | Masa de forma/proporción/escala validada en engine antes de detallar [ver: gamedev/arte-direccion] |
| **High poly** | Modelo denso sin optimizar: fuente del bake o asset de render |
| **Low poly** | Modelo optimizado para el juego; también el estilo visual que imita ese look [ver: estilizacion-lowpoly] |
| **Retopology** | Reconstruir topología limpia sobre un sculpt/scan [ver: topologia] |
| **Bake** | Transferir detalle high→low a texturas (normal, AO, curvature…) [ver: high-to-low] |
| **Cage** | Copia inflada del low-poly que limita la proyección del bake (Marmoset) |
| **Floater** | Detalle high-poly flotando sobre la superficie solo para bakearse |
| **Decimation** | Reducción automática de tris (para manejar sculpts, no para hacer el low final) |
| **LOD** | Versiones de menos detalle según distancia (`_LOD0..n`) [ver: pipeline/arte-a-unity] |
| **Silhouette** | El contorno del modelo: donde se gastan los polígonos (Polycount wiki, *Topology*) |
| **Smoothing groups / hard edge** | Partición de vertex normals para aristas duras (§3) |
| **FWN** | Face weighted normals: shading limpio de hard-surface vía bevels + normales editadas (§3) |
| **Tangent basis / MikkTSpace** | Sistema de coordenadas por vértice que interpreta el normal map; MikkTSpace = estándar de facto (§3) |
| **Handedness (Y+/Y−)** | Convención del canal verde del normal map: OpenGL (Y+) vs DirectX (Y−) |
| **Watertight / manifold** | Volumen cerrado y coherente (§7) |
| **T-vertex, doubles, wire** | Defectos de geometría rota (§7) |
| **Texel density** | Resolución de textura por metro de superficie, consistente entre assets [ver: pipeline/arte-a-unity] |
| **Trim sheet / atlas** | Textura compartida por muchos assets para ahorrar materiales y draw calls [ver: entornos-modulares] |
| **Draw call** | Orden de dibujo a la GPU; cada material extra en el modelo añade coste (Polycount wiki, *GameRenderingTerminology*) |

## Reglas prácticas

1. Modela en quads; triangula explícitamente al final y bakea/exporta ESA triangulación — nunca dejes que cada herramienta triangule a su manera.
2. Ngons: cero en la malla final. Tras cada boolean, limpia a quads/tris intencionales.
3. Cada edge del low-poly debe justificarse por una de cuatro razones: silueta, deformación, shading o UV. Si no, se colapsa.
4. Piensa en vertex count real: UV seams + hard edges + materiales duplican vértices — alinéalos entre sí (hard edge sobre seam existente = casi gratis).
5. Todo hard edge lleva su split de UV; no toda costura de UV necesita hard edge.
6. Orgánico que deforma: smooth shading total. Hard-surface: hard edges con split, o bevels/FWN — decide UNA estrategia por asset.
7. Bakea y renderiza con la misma tangent basis (MikkTSpace salvo que el engine diga otra cosa) y verifica la handedness del canal verde.
8. 1 unidad = 1 metro desde el blockout; escena plantilla con cubo de 1 m + figura de 1.8 m siempre visible.
9. Escala y rotación aplicadas (identidad) antes de exportar; la escala jamás se "arregla" en el Transform de la escena.
10. Pivot por USO (base/bisagra/agarre/esquina de kit/centro de giro) definido en el DCC; criterio: apoya en Y=0 y rota sobre su punto lógico.
11. El modelo vive en el origen del archivo, mirando al frente convencional del proyecto (+Z para glTF/Unity).
12. Polígonos donde hay curvatura y silueta; superficies planas con el mínimo. El normal map no arregla una silueta pobre.
13. Poles fuera de zonas que deforman y de superficies muy curvas; escóndelos en lo plano.
14. Antes de todo export: pasada de limpieza — non-manifold, doubles, caras invertidas, T-vertices, caras internas, elementos wire. Con la herramienta automática, no a ojo.
15. Visualiza la orientación de caras antes de entregar; una cara invertida es invisible en el juego.
16. Un material por prop como objetivo; el detalle vive en la textura/trim, no en materiales extra.
17. Borra lo que la cámara nunca verá (caras internas, traseras permanentes contra muros) — es presupuesto muerto.
18. Optimiza donde multiplica: héroes, assets instanciados en masa y escenas de estrés; no pulas el prop de fondo.
19. Un modelo "de render" (sculpt denso, sin UVs, sin escala) NO se importa al juego: pasa por high→low completo [ver: high-to-low].
20. Todo modelo se aprueba EN el engine con la luz y cámara reales del juego, nunca en el viewport del DCC [ver: gamedev/arte-direccion].

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Contar "polys" en el DCC y descubrir el doble de tris en el engine | Contador en modo triángulos; presupuesto SIEMPRE en tris [ver: presupuestos-poligonos] |
| Shading en zigzag / errores "en X" tras el bake | Triangulación distinta entre baker y engine: triangular antes de bakear y exportar triangulado |
| Hard edges por todos lados "para que se vea definido" | Cada hard edge duplica vértices y exige UV split; usar bevels/FWN o hard edges solo donde tocan |
| Hard edge en medio de una isla UV | Seam visible en el bake; partir la UV ahí o quitar el hard edge |
| Normal map con detalles hundidos que deberían sobresalir | Handedness equivocada: invertir canal verde o bakear con la convención del engine |
| Modelo gigante o miniatura al importar | Unidades del DCC sin verificar: test del cubo de 1 m; corregir en el archivo/importer, no en el Transform |
| Físicas "de luna" o luces que no iluminan | Escena fuera de escala real: re-escalar el ARTE, no compensar tocando gravedad/intensidades |
| Edificio que flota, puerta que gira por el centro | Pivot por defecto del software: definir pivot por uso (§5) antes de exportar |
| Kit modular que no snapea | Pivots inconsistentes entre módulos: esquina/centro idéntico en todo el kit [ver: entornos-modulares] |
| Booleans "rápidos" que dejan la malla rota | Tras cada boolean: limpiar ngons, doubles y non-manifold — el boolean es el inicio, no el final [ver: hard-surface] |
| Z-fighting parpadeante en una superficie | Caras duplicadas (doubles) o dos mallas coplanares: merge por distancia / separar superficies |
| Caras que desaparecen según el ángulo | Normales invertidas + backface culling: recalcular orientación hacia fuera |
| Rayitas de luz atravesando esquinas | Gaps/T-vertices en uniones: weld real, no caras "apoyadas" |
| Sculpt de millones de polys exportado "a ver si corre" | Nunca corre: high→low con retopo, UVs y bake es el único camino [ver: high-to-low] |
| Subdividir para "suavizar" un modelo de juego | La suavidad de un asset de juego sale de vertex normals y normal map, no de multiplicar tris |
| Detalle bakeado que no aparece | Detalle menor a 1 píxel a la resolución de textura o caras paralelas sin cambio de dirección: exagerar bevels/profundidad (Marmoset) |
| Aprobar el modelo en el viewport del DCC | El viewport miente (shading, luz, tangent basis): aprobar en engine con luz real [ver: pipeline/arte-a-unity] |

## Fuentes

- **Polycount wiki — Polygon Count** — comunidad Polycount (canon del game art) — tris vs polys, vertex count real (splits por UV/smoothing/material), triangulación no determinista, rango 2 tris–40k+ tris.
- **Polycount wiki — Topology** — Polycount — principios: tipos de malla por destino, zonas de deformación, lista de geometría rota, poles, densidad por curvatura, silueta.
- **Polycount wiki — VertexNormal** — Polycount — qué es la vertex normal, seams de modelos cortados, normales editadas (bent normals), interacción con normal maps.
- **Polycount wiki — Normal Map Technical Details** — Polycount — tangent basis (normal/tangente/bitangente), MikkTSpace como estándar, synced workflow, tabla de handedness por software, FBX guarda tangentes.
- **Polycount wiki — Smoothing Groups** — Polycount — hard/soft edges = partir vertex normals (Max/Maya), regla de UV splits en hard edges.
- **Polycount wiki — Face weighted normals** — Polycount — técnica FWN y su coste (triángulos finos).
- **Polycount wiki — Texture Baking** — Polycount — workflow completo de bake: triangular antes, explode, cage, padding, reset transforms.
- **Polycount wiki — GameRenderingTerminology** — Polycount — T-vertex, vertex splits y vertex cache, draw calls, fill rate.
- **"You're making me hard. Making sense of hard edges, uvs, normal maps and vertex counts"** — Joe "EarthQuake" Wilson, foro Polycount — la relación hard edge ↔ UV split ↔ vertex count, canon citado por el propio wiki.
- **The Toolbag Baking Tutorial** — Joe Wilson, Marmoset — cage smoothed/unsmoothed, tangent space sync (Mikk = Unity/Unreal), handedness, errores en X por triangulación, bevels y detalle ≥1 px, unidades de escena en el height bake.
- **Beautiful, Yet Friendly (partes 1-2)** — Guillaume Provost, Game Developer Magazine 2003 — qué cuesta de verdad: transform vs fill bound, densidad de vértices, dónde rinde optimizar.
- **Blender Manual — Glossary** — Blender Foundation — definiciones formales: vertex/edge/face, edge loop/ring, face loop, pole (3/5+ edges), ngon, quad, manifold y los 4 tipos de non-manifold, bevel/chamfer (conceptos agnósticos; se cita como diccionario, no como receta de herramienta).
- **Topology Guides — 3D Modeling Encyclopedia** — Johnson Martin — vocabulario del oficio: flat/smooth shading, bevel/chamfer/inset, boolean, sub-d Catmull-Clark, box/poly modeling, NURBS/CAD, high/low poly, real world scale.
- **glTF 2.0 Specification** — Khronos Group — unidades en metros, sistema Y-up right-handed, frente +Z.
- Bases ya sintetizadas: [ver: pipeline/arte-a-unity] (spec de entrega FBX/glTF, escala 1 m en Unity, pivots auditables, LODs, canales URP) y [ver: gamedev/arte-direccion] (blockout en engine, poly budget en el style guide, aprobación bajo luz real).
