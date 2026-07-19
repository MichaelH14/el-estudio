# Topología

> **Cuando cargar este archivo:** al modelar o retopologizar CUALQUIER malla de juego (personaje, prop, arma, entorno), al revisar un wireframe antes de aprobarlo, o al diagnosticar shading raro / deformación fea / artefactos de subdivisión. Complementa [ver: fundamentos-3d] (conceptos base de malla) y alimenta a [ver: high-to-low] (bakes) y [ver: presupuestos-poligonos] (números por categoría).

## 1. Qué es la topología y qué debe lograr

Topología = el layout de la malla: cómo están colocados vértices y edges para crear la superficie (polycount wiki). No es "cuántos polígonos" sino **dónde y cómo fluyen**.

Según polycount, un modelo in-game se optimiza para 4 cosas a la vez — este es el criterio de aceptación de cualquier malla:

| Objetivo | Qué significa en la práctica |
|---|---|
| **Silueta** | Los polígonos definen la forma; los que no aportan a la silueta son candidatos a eliminarse (§6) |
| **Deformación** | Edge loops donde la malla dobla/estira, para skinning y morphs limpios (§5) |
| **Shading** | Minimizar cambios extremos entre vertex normals; la topología decide cómo se sombrea la superficie |
| **UV seams** | La topología debe permitir cortes de UV limpios y baratos (§9) |

Mala topología no es solo estética: causa framerates bajos (vértices desperdiciados), deformación fea y errores de render visibles. La topología correcta **depende del destino de la malla** (§2): base para sculpt, low-poly de juego, o modelo de subdivisión tienen reglas distintas.

## 2. Quads, tris y n-gons: la moneda de trabajo

### Quads: la moneda durante el modelado

Se trabaja en quads no por superstición sino por beneficios concretos (polycount, Polygon Count):

- **Edge-loop selection y transform**: seleccionar/mover anillos y loops completos solo funciona bien en mallas de quads — acelera todo el modelado.
- **Legibilidad del flow**: una malla de quads deja "leer" la dirección de la superficie de un vistazo, y facilita pesar (skin) el modelo a los huesos.
- **Sculpt**: si la malla va a ZBrush/sculpt, quads lo más posible para evitar pinching al esculpir (polycount, Topology).
- **Subdivisión**: Catmull-Clark quiere caras regulares (quads); todo lo demás genera artefactos (§7, Pixar OpenSubdiv).

Los artistas conservan los quads el mayor tiempo posible en el pipeline — pero son una herramienta de EDICIÓN, no el formato final.

### El engine triangula TODO al final

Datos duros de polycount (Polygon Count):

- La GPU solo ve **vértices y triángulos** — no existen polígonos de 4+ lados en render. "Poly count" en jerga de juego = **triangle count**.
- El contador de polígonos del DCC engaña: el número real es el de triángulos (configurar el contador en tris siempre).
- Al exportar, cada quad se parte en 2 triángulos automáticamente — y la diagonal puede caer en dos direcciones: el mismo quad no planar queda como "cresta" (ridge) o "valle" (valley) según cómo se triangule. **Revisar el modelo dentro del engine** y triangular a mano los quads donde la diagonal quedó mal.
- Si el modelo se triangula distinto en el bake y en el export, el shading de la normal map "zigzaguea" por el modelo. **Triangular antes del bake** lo resuelve (§9).
- Rango de coste citado por el wiki: desde 2 triángulos (un billboard) hasta 40,000+ (personaje complejo). Presupuestos concretos por categoría: [ver: presupuestos-poligonos].

### Cuándo los triángulos son aceptables

| Situación | Veredicto |
|---|---|
| Low-poly final de juego | Tris totalmente válidos — "triangles are fine, but you want every edge to be there for a reason" (polycount, Topology) |
| Zonas planas que no deforman | Tris inofensivos; nadie los verá en el shading |
| Cerrar/reducir loops (gather) | Válido: un tri o un pentágono estratégico recoge loops que divergen (§4) |
| Malla que va a subdividirse | Evitarlos: generan artefactos bajo Catmull-Clark (Pixar) |
| Zonas de deformación fuerte | Evitarlos: rompen el flow de loops que el skinning necesita |

### N-gons (5+ lados)

- **Jamás en una malla entregable**: el engine/exportador los triangula de forma impredecible.
- En modelado de subdivisión, un **pentágono estratégico** en un saddle point (ej. unión brazo-torso) es técnica legítima de Pixar para recoger 3+ loops divergentes manteniendo la superficie lisa (OpenSubdiv Modeling Tips) — se usa consciente y puntual, no por descuido.

### Vertex count: el coste real

El rendimiento y la memoria los manda el **vertex count**, no el tri count (polycount). Y el vertex count real en engine es mayor que el del DCC: cada UV seam, cada hard edge (cambio de smoothing) y cada cambio de material **duplica los vértices** de esa arista para el render. Abusar de smoothing groups, sobre-cortar UVs o multiplicar materiales infla el coste aunque el tri count no cambie [ver: pipeline/arte-a-unity].

## 3. Edge flow: qué es y cómo planificarlo

**Edge flow** = la dirección en que corren los edge loops sobre la superficie. Importa porque: (1) la malla deforma a lo largo de sus loops — loops bien orientados doblan limpio, loops cruzados colapsan; (2) el skinning pesa por loops; (3) editar y extender la malla es barato solo donde el flow es coherente.

Cómo planificarlo según el objeto:

| Objeto | El flow sigue... | Fuente |
|---|---|---|
| Cuerpo orgánico | Las **líneas de anatomía/musculatura**: al animar, los vértices empujan en el mismo eje que los músculos | 80.lv (Pyrch, Metro Exodus); Topology Guides |
| Articulaciones | El **eje de flexión**: loops perpendiculares al hueso, alineados al eje de rotación, para que las caras no se distorsionen al doblar | Topology Guides (Modeling for Animation) |
| Cara | **Anillos concéntricos** alrededor de ojos y boca (las zonas de máxima deformación facial), con el resto del flow conectándolos | canon visible en los breakdowns de FaceTopology: Uncharted 2 (Naughty Dog), Mass Effect 3, Gears of War 3, AC IV |
| Ropa / equipo | Las **líneas de diseño de la prenda** (costuras, cortes, straps) | 80.lv (Pyrch) |
| Hard-surface | La curvatura de la superficie: loops que soportan los cortes y biseles [ver: hard-surface] | Pixar OpenSubdiv |

Regla de planificación: **primero las líneas maestras, después el relleno.** Trazar los loops críticos (contorno de ojo, boca, hombro, línea de mandíbula, costuras) y conectar el resto de la malla entre ellos. El relleno se acomoda; las líneas maestras no se improvisan.

Transiciones de densidad: para pasar de zona densa a zona ligera (dedos → palma), usar reducciones de loops planificadas — un pole de valencia 5 puede expandir 3 loops en 5 (Pixar). Técnicas de reducción detalladas en Topology Guides (Loop Reduction).

Tres preguntas antes de trazar el primer loop (destilado de las fuentes anteriores):

1. **¿Qué se dobla?** → ahí van loops perpendiculares al eje de flexión (§5).
2. **¿Qué define la silueta?** → ahí va la densidad (§6).
3. **¿Dónde van a caer los poles?** → decidirlo AHORA; moverlos después degrada la malla (§4).

## 4. Poles: dónde molestan y dónde no

**Pole** = vértice con valencia ≠ 4 (Topology Guides):

| Tipo | Valencia | Origen típico | Carácter |
|---|---|---|---|
| **N-pole** | 3 edges | Insets, esquinas convexas (vértice de cubo); necesario p.ej. en la base de la nariz | El menos problemático |
| **E-pole** | 5 edges | Extrusiones, giros de loops, esquinas cóncavas en hard-surface | El más común y el que más pincha |
| 6+ edges | 6 o más | Descuido (fan de tris, merge masivo) | Mala práctica casi siempre; solo tolerable en superficie plana |

Hechos verificados:

- Un pole **pincha alrededor de su perímetro** al subdividir o suavizar: superficie desigual, dimples o bumps (Topology Guides; polycount).
- Los vértices de alta valencia además producen superficies "onduladas" (wavy) bajo Catmull-Clark cuando los rodean triángulos, y tienen coste de performance en subdivisión (Pixar OpenSubdiv).
- Los poles **no se pueden eliminar** de un modelo complejo — se **colocan** donde no dañan.

Dónde ponerlos y dónde no:

| Zona | Veredicto |
|---|---|
| Superficie plana | Inofensivo — el lugar preferido (Topology Guides; polycount) |
| Curvatura suave y zona poco visible (ej. mejilla) | Aceptable; la distorsión es imperceptible |
| Curvatura fuerte / esquina que define forma | NO: el pole altera la superficie justo donde más se ve |
| Zona que deforma (articulación, boca) | NO: el pinch se anima y se vuelve evidente (polycount: "best kept away from areas that deform") |
| Cap de un cilindro/revolución | Resolver con layouts de quads valencia-4 en la tapa, no con un pole central de alta valencia (Pixar) |

Mover un pole después es caro: cada movimiento exige quitar un loop en la dirección de destino y otro en el origen para no crear n-gons, degradando la malla (Topology Guides). **Planificar la posición de los poles antes de densificar** — en el blockout/primer pase de retopo, no al final.

## 5. Deformación vs estático: dos juegos de reglas

La topología cuesta tiempo; se invierte donde paga. Polycount: la topología importa MÁS donde el modelo MÁS deforma — y lista las zonas críticas: **entrepierna/cadera/glúteos, hombros/axilas, comisuras de boca/mejillas, rodillas, codos, manos/dedos**.

| Aspecto | Malla que DEFORMA (personaje, criatura) | Malla ESTÁTICA (prop, entorno, arma) |
|---|---|---|
| Quads | Dominantes, sobre todo en zonas de flexión | Irrelevante en el final; tris libres |
| Poles | Fuera de articulaciones y cara móvil | Donde sea, mientras el shading no sufra |
| Edge loops | Obligatorios en articulaciones, perpendiculares al hueso y alineados al eje de flexión | Solo los que definan silueta o soporten UV/shading |
| Densidad | Extra en zonas que doblan (aunque no aporte silueta en T-pose) | Solo silueta y curvatura (§6) |
| Flow | Anatomía/músculos/líneas de ropa (§3) | La forma manda; "every edge for a reason" |
| Criterio de éxito | Deforma limpio en las poses extremas del juego | Silueta correcta + shading limpio + vertex count mínimo |

Claves para deformación (Topology Guides, Modeling for Animation):

- **Loops de articulación que se extienden más allá de la zona de flexión** hacia la superficie plana vecina: permiten ángulos extremos sin artefactos.
- Densidad variable: concentrar polígonos en zonas que deforman (cara, articulaciones) y ahorrar en las estáticas del mismo personaje.
- En la T-pose todo se ve bien — la topología de deformación **solo se valida posando**: doblar codo/rodilla al máximo del juego y mirar el volumen. La articulación que colapsa o "desinfla" es falta de loops o loops mal alineados, y se corrige en la malla, no en el rig [ver: organico-personajes].
- Referencia canon de articulación film-grade: *The Art of Moving Points* de Brian Tindall (Character TD de Pixar, hippydrome.com) — la referencia que el propio polycount recomienda para deformación pre-rendered.

Los props no son "personajes fáciles": son otro régimen. Gastar loops de deformación en un barril es tan error como no ponerlos en un codo. [ver: props-armas]

## 6. Densidad: silueta primero

Reglas de polycount (Topology, Silhouette + Polygon Density):

1. **La silueta manda**: no gastar polys donde no aportan al contorno visible. El interior de una superficie lisa se resuelve con shading y normal map, no con geometría [ver: high-to-low].
2. **Más geometría donde hay curvatura, menos donde es recto.** Un plano es un plano con 2 tris o con 200.
3. Balancear contra las otras prioridades: una zona recta que DEFORMA sí necesita loops (§5); una curva que jamás se ve de perfil puede vivir con menos segmentos.

Guías numéricas verificadas:

- En subdivisión, **6 spans bastan para un círculo preciso; 4 para objetos de fondo** (Pixar OpenSubdiv — ojo: es para mallas que se subdividen, no para low-poly directo; el low-poly ajusta lados según tamaño en pantalla [ver: presupuestos-poligonos]).
- La densidad se juzga **a la distancia/cámara real del juego**, nunca en el viewport a fondo de zoom — mismo principio que aprobar assets en engine [ver: gamedev/arte-direccion].
- El coste real es vertex count (§2): antes de quitar tris "para optimizar", revisar UV seams, hard edges y materiales, que suelen pesar más.

## 7. Topología de soporte para subdivisión

Para high-poly de bake o assets sub-d [ver: hard-surface]:

- Malla bien construida según Pixar: **mayoría de quads, pocos extraordinary vertices (poles), describe la forma con el mínimo de puntos de control, y es manifold**.
- Cada nivel de subdivisión multiplica el vertex count ~4x (polycount) — el cage se mantiene tan ligero como la forma permita.
- **Holding edges** (loops de soporte): edges extra cerca de una arista que debe quedar dura tras subdividir; controlan la tensión. Coste: densifican la malla y arrastran loops por todo el modelo.
- **Creases**: tensión por arista sin geometría extra. Datos de Pixar: sharpness 0-10; usar creases es en general **más barato que añadir loops**; valores >5 rara vez necesarios; organizar en crease sets con nombre.
- ⚠️ Trampa de pipeline (polycount, Subdivision Surface Modeling): **los crease weights no suelen sobrevivir el export** entre DCCs/bakers — funcionan dentro de la herramienta de origen. Si el modelo viajará entre herramientas (típico en juegos), los holding edges son lo portable; probar el pipeline completo ANTES de comprometerse con creases.
- Espaciado de loops parejo: loops muy desiguales crean distorsiones sutiles en los reflejos (Topology Guides, Mesh Artifacts). En superficies pulidas (autos, armas) revisar con un material reflectivo/matcap.
- Manifold obligatorio (polycount): sin T-vertices, caras dobladas, gaps, caras volteadas, geometría interna invisible ni vértices flotantes — todo eso rompe subdivisión, bakes y booleans.

## 8. Retopología: cuándo y cómo

**Cuándo**: cuando la malla de trabajo no sirve como malla de juego — típicamente tras un sculpt (millones de polys sin orden) o tras booleans/kitbash sucio. **Cuándo NO**: polycount señala que a veces basta partir del 2º nivel de subdivisión del sculpt o del base mesh y colapsar/cortar loops — retopo desde cero es una opción, no un rito.

Flujo estándar de personaje verificado en producción (80.lv — Metro Exodus, TLOU2 fan-art pro):

1. Sculpt/high-poly terminado y aprobado (la retopo fija la forma: cambiar el sculpt después = repetir trabajo).
2. **Retopo** dibujando la malla nueva sobre la superficie del sculpt (quad-draw o equivalente): primero las líneas maestras del flow (§3), poles planificados (§4), loops de articulación (§5), densidad por silueta (§6).
3. UVs sobre la malla nueva.
4. Bake de normal/AO/ID del high al low [ver: high-to-low].

Datos de producción: la retopo de un personaje completo toma **16-80 horas de trabajo** según complejidad (attachments, ropa, straps) — cifra de Evgeny Pyrch (Metro Exodus, 80.lv). No es un paso "rápido"; se presupuesta.

Retopo automática (ZRemesher y similares): útil para mallas intermedias de sculpt o props de fondo; para personajes que deforman, el flow anatómico y los loops de articulación siguen requiriendo dirección manual — el auto-retopo no sabe dónde está el codo.

Señales de que una malla existente necesita re-plantearse (no parchearse): flow que pelea contra la anatomía en varias zonas, poles incrustados en articulaciones, densidad invertida (denso en lo plano, pobre en la curva), o tantos parches que la malla ya no se puede editar por loops.

## 9. Topología y LODs

Los LODs son retopología degradada de la misma malla — y la topología del LOD0 decide si salen baratos o caros:

- Un LOD0 con flow limpio de loops se reduce colapsando loops enteros (rápido, predecible, conserva la silueta); una malla parcheada obliga a decimación automática con resultados sucios.
- La prioridad se invierte respecto al LOD0: en LODs lejanos solo importa la **silueta** — los loops de deformación pueden desaparecer en personajes lejanos (la animación a esa distancia no se aprecia igual), los poles dejan de importar (nadie ve el pinch a 40 m), y los quads dan igual (se entrega triangulado).
- Lo que NO puede cambiar entre LODs sin que se note el "pop": la silueta general y la posición de los UV seams (cambiarlos regenera vértices y puede mover el shading).
- Entrega y naming (`_LOD0..n` en el FBX, umbrales por % de altura en pantalla): [ver: pipeline/arte-a-unity §7]. Cuántos niveles y cuánto reducir por categoría: [ver: presupuestos-poligonos].

## 10. Topología y el bake/shading (por qué el low importa)

Lo mínimo que la topología del low-poly debe respetar para que el bake funcione (detalle completo en [ver: high-to-low]):

- **Triangular el low antes del bake**: si el exportador voltea diagonales después, el shading de la normal map zigzaguea (polycount, Polygon Count).
- **Workflow synced**: baker y engine deben usar la misma tangent basis (MikkTSpace es la más común); FBX guarda tangentes para garantizarlo (polycount, Normal Map Technical Details) [ver: pipeline/arte-a-unity].
- **Cada hard edge necesita UV split**: un hard edge duplica vértices igual que un seam; hard edge sin corte de UV = artefacto visible en el bake (canon del thread "Making sense of hard edges, uvs, normal maps and vertex counts", referenciado por polycount).
- Sin workflow synced, la defensa es geométrica: **bevels y/o hard edges** en las aristas duras para que los errores de shading no sean extremos (Marmoset, Toolbag Baking Tutorial).
- Normal map tangent-space para todo lo que deforma (object-space no deforma sin shader especial) — polycount.

## Reglas prácticas

1. Antes de modelar, declara el destino de la malla: ¿base de sculpt, low-poly de juego, o sub-d? Cada uno tiene reglas distintas (§2).
2. Trabaja en quads; entrega sabiendo que TODO acaba en triángulos — configura el contador del DCC en tris desde el día 1.
3. En el low-poly final, cada edge existe por una razón: silueta, deformación, UV o shading. Si no responde a ninguna, se colapsa.
4. Traza primero las líneas maestras del flow (ojos, boca, articulaciones, costuras); rellena después.
5. Orgánico: el flow sigue músculos/anatomía; ropa: sigue las costuras del diseño; articulación: loops alineados al eje de flexión.
6. Planifica los poles en el primer pase: en zonas planas o de curvatura suave, JAMÁS en articulaciones ni curvatura que define forma.
7. E-poles y N-poles son inevitables; valencia 6+ es descuido — resolver caps de cilindro con quads, no con un fan al centro.
8. Personaje: densidad extra en entrepierna/cadera, hombros/axilas, boca/mejillas, rodillas, codos y manos — las 6 zonas críticas de polycount.
9. Extiende los loops de articulación más allá de la zona que dobla, hacia la superficie plana vecina.
10. Valida deformación POSANDO al máximo ángulo del juego, nunca solo en T-pose; el fix va en la malla, no en el rig.
11. Prop estático: silueta primero, tris libres, cero loops "de deformación" que nadie usará.
12. Más geometría donde hay curvatura, menos donde es recto; juzga la densidad a la cámara real del juego.
13. Vigila el vertex count real: UV seams, hard edges y materiales duplican vértices aunque el tri count no suba.
14. Sub-d: mayoría de quads, pocos poles, malla manifold; creases más baratos que holding edges DENTRO de una herramienta, holding edges si el asset viaja entre herramientas — prueba el pipeline completo antes.
15. Espaciado de loops parejo en superficies reflectivas; revisa con matcap/material espejo.
16. Retopo: sculpt aprobado primero; presupuesta en serio (16-80 h un personaje de producción).
17. Auto-retopo solo para mallas intermedias o props de fondo; articulaciones y cara siempre con flow dirigido a mano.
18. Triangula el low antes del bake y usa tangent basis synced (MikkTSpace/FBX) con el engine.
19. Cada hard edge lleva su UV split; sin workflow synced, añade bevels a las aristas duras.
20. Revisa el modelo triangulado DENTRO del engine con la luz real: diagonales de quads no planares pueden necesitar girarse a mano [ver: pipeline/arte-a-unity].

## Errores comunes

| Pitfall | Síntoma visible | Antídoto |
|---|---|---|
| Pole (E-pole/valencia alta) en zona curva o articulación | Pinch/dimple en el shading; al subdividir, bulto u hoyuelo; al animar, arruga que "respira" | Mover el pole a zona plana — y como moverlo degrada la malla, planificarlo desde el primer pase (§4) |
| Codo/rodilla sin loops suficientes o mal alineados | La articulación colapsa o pierde volumen al doblar; textura estirada en el pliegue | Loops perpendiculares al hueso, alineados al eje de flexión, extendidos más allá de la zona; validar posando |
| Quad no planar triangulado "al azar" en export | Sombreado en cresta o valle que cambia entre DCC y engine; facetas que aparecen solo in-game | Triangular a mano los quads conflictivos ANTES de exportar y de bakear |
| N-gon olvidado en la malla final | Triangulación impredecible: shading sucio, bake con artefactos justo ahí | Auditar: seleccionar caras de 5+ lados antes de export; resolver a quads/tris conscientes |
| Malla no-manifold (caras dobles, internas, T-vertices, verts flotantes) | Bakes con manchas, booleans que fallan, sombras rotas, subdivisión que explota | Chequeo manifold antes de UV/bake; limpiar geometría invisible |
| Alta valencia rodeada de tris en sub-d | Superficie "ondulada" (wavy) tras subdividir | Reconstruir el cap/zona con quads valencia-4 (Pixar §4) |
| Loops de soporte con espaciado desigual | Reflejos con ondulaciones sutiles en superficies pulidas | Espaciado parejo; revisar con matcap reflectivo |
| Creases que se pierden al exportar | El high-poly llega "derretido" al baker: aristas duras desaparecidas | Holding edges para assets que viajan; probar el pipeline completo antes de producir en masa |
| Hard edge sin UV split | Seam de shading o gradiente extremo en la normal map bakeada | Regla mecánica: hard edge ⇒ corte de UV en esa arista |
| Bake con un tangent space y render con otro | Shading que zigzaguea o luce invertido según el ángulo de luz | Workflow synced (MikkTSpace + FBX con tangentes); verificar en el engine, no en el baker |
| Densidad invertida (detalle donde no hay curvatura ni deformación) | Tri count alto sin que la silueta mejore; performance regalada | Pasada de silueta: ¿qué edges no cambian el contorno ni la deformación? Colapsarlos |
| "Optimizar" cortando UVs y smoothing groups por todos lados | Vertex count in-game dispara aunque los tris bajen | Contar vértices in-game, no en el DCC; menos seams, menos hard edges, menos materiales |
| Retopo empezada con el sculpt aún cambiando | Retrabajo completo de malla+UVs+bake con cada iteración del sculpt | Congelar la forma antes de retopo; la retopo es un compromiso de 16-80 h en personajes |
| Confiar el codo al auto-retopo | Flow genérico que ignora ejes de flexión; deformación fea imposible de pesar bien | Auto-retopo solo intermedio/props; zonas de deformación siempre dirigidas a mano |

## Fuentes

- **Topology** — polycount wiki (canon del game art) — la definición y los principios: 4 objetivos del modelo in-game, tipos de topología según destino, zonas críticas de deformación, poles lejos de deformación, manifold, densidad/silueta.
- **Polygon Count** — polycount wiki — GPUs solo ven tris/vértices, triangulación en export (ridge/valley), triangular antes del bake, quads como herramienta de workflow, vertex count vs tri count, splits por UV/smoothing/material, rango 2 tris (billboard) a 40k+ (personaje).
- **Subdivision Surface Modeling** — polycount wiki — creases no exportables entre herramientas, 4x vértices por nivel de subdivisión, ecosistema canon de sub-d (The Pole, GuerrillaCG).
- **FaceTopology** — polycount wiki — breakdowns de topología facial de juegos publicados: Uncharted 2 (Naughty Dog), Mass Effect 3 (BioWare), Gears of War 3, AC IV (Digic).
- **Normal Map Technical Details** — polycount wiki — tangent basis, workflow synced, MikkTSpace como estándar de facto, FBX con tangentes, tangent-space vs object-space para mallas que deforman.
- **Modeling Tips (OpenSubdiv)** — Pixar (documentación técnica oficial) — quads + pocos extraordinary vertices + manifold, 6/4 spans para círculos en sub-d, alta valencia = wavy + coste, caps de cilindro en quads, pentágono en saddle points, creases 0-10 (>5 raro, más barato que loops).
- **Moving and Manipulating Edge Poles** — Johnson Martin, Topology Guides — definiciones N-pole/E-pole/valencia, pinching perimetral, colocación por curvatura, coste de mover poles, planificación previa.
- **Modeling with Animation in Mind** — Johnson Martin, Topology Guides — loops alineados al eje de animación, flow por musculatura, loops extendidos más allá de la articulación, densidad variable, reubicar poles fuera de zonas de movimiento.
- **Dealing with Mesh Artifacts in Subdivision Modeling / Optimal Edge Loop Reduction Flows** — Johnson Martin, Topology Guides — espaciado parejo de loops vs distorsión de reflejos; reducciones de densidad planificadas.
- **Topology for Game and Game-Based Characters** — 80.lv (Evgeny Pyrch — Metro Exodus; Massimiliano Bianchini — TLOU2) — flow por líneas de anatomía y de diseño de ropa, flujo sculpt→retopo→UV→bake, 16-80 h de retopo por personaje.
- **Toolbag Baking Tutorial** — Marmoset (documentación técnica del baker) — cage, tangent spaces y handedness en bake/render, bevels+hard edges como defensa sin workflow synced.
- **The Art of Moving Points / hippydrome.com** — Brian Tindall, Character TD de Pixar — referencia canon de topología de articulación film-grade, recomendada por el propio polycount wiki para deformación (consultado el sitio; el detalle técnico vive en el libro).
