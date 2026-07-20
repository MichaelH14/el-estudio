# Geometry Nodes — programación visual de geometría para assets de juego

> **Cuando cargar este archivo:** cada vez que haya que hacer scatter de props/vegetación, variaciones procedurales de un asset (rocas, árboles), kits modulares paramétricos, o geometría por curva (cables, tuberías, vallas) — y siempre antes de exportar a Unity un objeto que tenga un modificador Geometry Nodes.

## Qué son y estado en Blender 5.x

- Sistema de nodos que modifica la geometría de un objeto: se añade un **modificador Geometry Nodes** (`Add Modifier ‣ Geometry Nodes`) y se edita el árbol en el **Geometry Node Editor** (workspace "Geometry Nodes" en el template por defecto).
- El árbol conectado al modificador es un **Node Group**: la geometría previa del stack entra por **Group Input**, sale por **Group Output** y sigue al siguiente modificador. Es un modificador más — se apila, se reordena y se aplica como cualquier otro [ver: modificadores].
- Tipos de geometría que procesa (manual 5.2): **Meshes, Curves, Point Clouds, Volumes, Instances, Empties** (Empties con modificador GN es nuevo de 5.2).
- Madurez: es un sistema **core y estable** desde 3.x; en 5.x es la base de features oficiales. En 5.0 varios modificadores de fábrica pasaron a ser node groups internos: **Scatter on Surface**, **Curve to Tube**, y un **Array** nuevo (el viejo quedó como **Array (Legacy)**). En 5.2 LTS llegó un sistema de **física experimental** (hair/cloth) sobre GN.
- Historia mínima que hay que saber para filtrar tutoriales viejos:

| Versión | Cambio clave |
|---|---|
| 2.92 (2021) | Primer release: scatter e instancing con nodos "Attribute *" (obsoletos) |
| 3.0 | **Rediseño total: fields**. Los nodos Attribute Math/Mix/etc. desaparecen. Tutoriales pre-3.0 NO sirven |
| 3.6 LTS | **Simulation Zone** (simulaciones con estado) |
| 4.0 | **Node tools** (node groups como operadores), **Repeat Zone**, sockets de rotación, node group assets aparecen en el menú Add Modifier |
| 4.1 | **Menu Switch**, **Index Switch**, nodo **Bake** |
| 4.3 | Zona **For Each Element**, soporte Grease Pencil, **Gizmos**, packed bakes |
| 4.5 LTS | **Set Mesh Normal**, nodos Import (OBJ/PLY/STL/CSV/VDB), operador **Visual Geometry to Objects**, API Python `GeometrySet` |
| 5.0 | **Bundles** y **Closures**, volume grids con sockets propios, nodo **UV Tangent**, modificadores de fábrica basados en GN |
| 5.1 | Más nodos de grids, String to Curves con socket **Font**, cada node tool registra su propio operador |
| 5.2 LTS | **Lists**, **Geometry Bundles**, física experimental, nodo **Mesh Bevel**, GN en Empties, **Collection Children**, string fields, **API Python nueva para inputs del modificador** (ver bpy abajo) |

⚠️ La MAYORÍA del contenido web es de 2.9–4.x. Regla: si un tutorial usa nodos "Attribute Math/Attribute Mix" es pre-3.0 (inservible); si setea inputs del modificador con `mod["Socket_2"]` es pre-5.2 (API cambiada).

## Modelo mental (viniendo de modificadores)

Un modificador clásico es una caja cerrada con opciones fijas. Geometry Nodes es armar tu propio modificador. Tres conceptos nuevos:

### Fields (campos)

- Un **field** es una función que se evalúa **por elemento** (por vértice, cara, instancia…). No es un valor: es "la instrucción para calcular un valor en cada elemento".
- Visual: los links de field se dibujan con **línea discontinua**; los sockets de field son **rombos** (círculo = valor único; rombo con punto = acepta field pero ahora lleva un valor único). Link rojo sólido = error de conexión.
- Dos familias de nodos: **data-flow** (entra y sale geometría: Set Position, Instance on Points…) y **function/input** (rombos: Math, Position, Index, Normal…). Un field solo significa algo **en el contexto** del nodo data-flow que lo consume.
- Trampa clásica: el mismo sub-árbol de field conectado a dos nodos data-flow puede dar **resultados distintos** — se re-evalúa con la geometría que llega a cada nodo. Para congelar un valor antes de modificar la geometría: **Capture Attribute** (guarda el resultado como atributo anónimo y lo arrastra con la geometría).
- Para sacar UN valor de un field: **Sample Index** o **Attribute Statistic**.

### Atributos y dominios

- **Atributo** = dato por elemento guardado en la geometría (float, int, bool, vector, color, quaternion, matriz 4x4…). Los **named attributes** (con nombre) los ven también shaders, weight paint y UV; los **anónimos** viven solo entre nodos.
- **Dominios**: Point, Edge, Face, **Face Corner** (ahí viven los UV), Spline, **Instance** (solo existe en GN) y Layer (Grease Pencil). Blender interpola automáticamente entre dominios cuando conectas un atributo donde no toca.
- Nodos clave: **Named Attribute** (leer), **Store Named Attribute** (escribir), **Capture Attribute** (congelar), y en 5.2 **Rename Attribute**, **Get Attribute Names**, **Transfer Attributes**.
- **UVs en GN**: no hay socket de 2D Vector — hay que escribirlos con **Store Named Attribute** (tipo *2D Vector*, dominio *Face Corner*, nombre p. ej. `UVMap`). Igual los Byte Color.
- Inspección: **Spreadsheet Editor** (muestra dominio, tipo y valores reales) + nodo **Viewer** (conectar con `Ctrl-Shift-Click` sobre un nodo; desde 5.0 también muestra valores sueltos dentro del propio nodo).
- En el panel del modificador, cada input puede alternar entre valor fijo y atributo con el icono a la derecha del campo → así un artista pinta un vertex group y el node group lo usa como máscara de densidad.

### Instancias

- Una **instancia** es una referencia barata a una geometría + una transformación. 1000 rocas instanciadas = 1 mesh en memoria. Es EL mecanismo de rendimiento de GN.
- Nodos: **Instance on Points**, **Translate/Rotate/Scale Instances**, **Instance Rotation/Scale**, **Realize Instances**, **Instances to Points**, **Geometry to Instance**.
- Mientras algo es instancia NO se puede editar su malla por elemento (todas comparten data). **Realize Instances** las convierte en geometría real única — y el coste de memoria/CPU se multiplica (advertencia literal del manual: "performance can become much worse").
- Los atributos en dominio Instance (p. ej. un color aleatorio por instancia) se propagan a la geometría real al realizar.

## Recetas de juego

### 1. Scatter de props/vegetación sobre una superficie

Camino corto (5.x): modificador de fábrica **Scatter on Surface** — density/amount, **Poisson Disk** (distancia mínima entre puntos), máscara de distribución, seed, instancia un Object o una Collection. Para el 80% de los casos no hace falta armar nada.

Camino manual (control total), cadena canónica:

```
Group Input (superficie)
 → Distribute Points on Faces  [Poisson Disk; Density Factor ← vertex group pintado]
 → Instance on Points          [Instance ← Collection Info con "Separate Children" + "Pick Instance" para variar]
 → Rotate Instances            [Align Rotation to Vector con la Normal + Random Value en Z]
 → Scale Instances             [Random Value 0.8–1.3]
 → Join Geometry con la superficie original → Group Output
```

- Densidad artística: pintar un vertex group en Weight Paint y conectarlo como field al Density Factor (o exponerlo como input del grupo y elegir el atributo en el modificador).
- Excluir zonas (caminos, edificios): otro weight/máscara restando densidad, o **Raycast**/**Geometry Proximity** contra los colliders de la zona.
- Seed SIEMPRE expuesto como input del grupo → regenerar variantes es cambiar un número.

### 2. Variaciones procedurales de un asset (rocas, árboles)

Patrón "una roca base, N rocas distintas":

```
Cube / mesh base → Subdivide Mesh (2-3) → Set Position
  [Offset = Noise Texture (4D, W ← seed) * Normal * intensidad]
 → opcional Dual Mesh (look facetado low poly) → Set Shade Smooth / Mesh Bevel (5.2)
```

- Exponer como inputs: `Seed`, `Deformación`, `Subdivisiones`, `Escala`. Cada valor de seed = una roca distinta con el mismo material y presupuesto de polígonos [ver: modelado/presupuestos-poligonos].
- Para exportar N variantes: duplicar el objeto, cambiar el seed y aplicar el modificador en cada copia (o hacerlo por bpy en loop). No exportar "el generador": Unity recibe mallas, no árboles de nodos.
- Árboles: el tronco por curva (receta 4) + ramas con Instance on Points sobre puntos de la curva + hojas instanciadas. Para vegetación seria evaluar addons (abajo) antes de reinventar.

### 3. Kits modulares paramétricos

- Un node group con inputs = una pieza de kit configurable: `Largo`, `Altura`, `Nº de postes`, `Estilo` (**Menu Switch** para variantes A/B/C, **Index Switch** por índice). El artista lo usa desde el panel del modificador sin abrir nodos [ver: modelado/entornos-modulares].
- Desde 4.0, un node group marcado como asset con **Is Modifier** activado aparece directo en el menú **Add Modifier** (su catálogo del Asset Browser define el submenú). Así el kit entero se consume como "modificadores de la casa".
- Muros/valla modular: curva o Curve Line → **Resample Curve** (Length = tamaño del módulo) → Instance on Points instanciando el módulo → Align Rotation to Vector con la **Curve Tangent**.
- Regla de oro del kit: las piezas siguen la retícula/snap del proyecto — GN genera variantes, no rompe la métrica del kit.

### 4. Cables, tuberías, vallas por curva

```
Curva (dibujada o Curve Line) → Resample Curve
 → Curve to Mesh [Profile ← Curve Circle (resolución baja: 6-8 lados para juego)]
 → Set Material → Store Named Attribute (UVMap) si hace falta UV procedural
```

- 5.x trae el modificador de fábrica **Curve to Tube** que ya hace exactamente esto (radio, resolución) sin armar nada.
- Grosor variable: el input Scale de **Curve to Mesh** (5.x) o el atributo radius de la curva; caída de cable: **Fillet Curve** + editar la curva en Edit Mode — el modificador sigue vivo.
- Vallas: combinar receta 3 (postes instanciados por Resample) + receta 4 (larguero por Curve to Mesh) en el mismo grupo.
- Trim/longitud dinámica: **Trim Curve** con factor expuesto como input.

## Instancias vs realized: qué exporta a Unity (FBX) — CRÍTICO

El estado del árbol de nodos NO viaja a Unity. Lo que viaja es geometría evaluada, y las instancias son el punto donde se pierde todo si no se hace bien [ver: import-export] [ver: pipeline/arte-a-unity].

| Estado al exportar | Qué sale en el FBX |
|---|---|
| Instancias sin realizar | NO van dentro de la mesh evaluada. El exporter FBX (add-on, `File ‣ Export ‣ FBX (.fbx)`) solo escribe objetos instanciados en escenas estáticas, cada uno con su copia de data (el FBX de Blender no comparte data entre objetos). **No confiarse: realizar o convertir antes** |
| **Realize Instances** antes del Group Output | Todo se funde en UNA mesh del objeto → sale bien con *Apply Modifiers*, pero es un solo mesh gigante: sin culling por prop, sin colliders individuales, malo para lightmaps |
| `Object ‣ Apply ‣ Visual Geometry to Objects` (4.5+) | Convierte el resultado en objetos/colecciones REALES **compartiendo mallas** (instancias → objetos que reusan la misma mesh) y sin tocar el original. ⚠️ Los atributos por instancia NO se conservan |
| `Object ‣ Apply ‣ Make Instances Real` | Cada instancia → objeto real independiente. Con decenas de miles de instancias tumba la escena |
| `Object ‣ Apply ‣ Visual Geometry to Mesh` | Congela TODO el estado visual del objeto a una mesh estática |

Decisión práctica:
- **Props sueltos / kit modular** → exportar los módulos limpios (aplicando el GN de cada uno) y **poblar en Unity con prefabs**. Las instancias de GN no son prefabs: al realizar se vuelven vértices tontos.
- **Un asset compuesto** (roca con musgo, valla completa) → Realize Instances o aplicar el modificador, verificar escala/UVs, exportar como un asset normal.
- **Escena de layout** (para bloquear un nivel) → Visual Geometry to Objects y exportar la colección; en Unity llegará como muchos objetos con mallas compartidas.
- Atributos: por FBX solo sobreviven los canales estándar (UVs, vertex colors, materiales, pesos de skin, normales). Un atributo custom (p. ej. "edad" de cada planta) hay que **hornearlo a vertex color o UV extra** con Store Named Attribute antes de exportar.
- Los materiales asignados con **Set Material** sí viajan en la mesh evaluada.

## Node groups reutilizables y assets de nodos

- Agrupar: seleccionar nodos → `Ctrl-G` (Make Group), `Tab` entra/sale, `Ctrl-Alt-G` desagrupa. La interfaz (inputs/outputs, defaults, subpaneles, tooltips) se edita en el Sidebar `N` ‣ pestaña Group.
- Nombrar sockets como los verá el artista en el modificador; defaults sensatos; en 4.0+ un input puede forzarse a "single value" para esconder el toggle de atributo.
- **Asset**: click derecho sobre el nombre del node group (en el header del editor o en el Outliner/Blender File) → **Mark as Asset**. Aparece en el **Asset Browser**; los **catalogs** organizan (y para tools/modifiers definen el menú donde salen).
- Biblioteca propia: guardar el .blend en una carpeta registrada en `Preferences ‣ File Paths ‣ Asset Libraries` → los grupos quedan disponibles en cualquier proyecto, arrastrando desde el Asset Browser al editor de nodos [ver: organizacion-blend].
- **Essentials**: biblioteca de assets oficial incluida con Blender — node groups mantenidos por el equipo (5.0/5.2 añadieron varios, p. ej. transformaciones de espacio 3D↔pantalla). Buscar ahí antes de armar utilidades genéricas.
- **Node tools** (4.0+): un node group puede ser un **operador de menú** en vez de un modificador. En el header del Geometry Node Editor cambiar *Node Tree Sub-Type* a **Tool**, definir modos/tipos de objeto soportados; como asset, su catálogo lo coloca en el menú elegido. Los inputs salen en el panel *Adjust Last Operation*. Desde 5.1 cada tool registra su propio operador (idname configurable) y desde 5.2 sus inputs se pueden setear por Python — ideal para operarlos vía MCP [ver: blender-mcp-operativo]. ⚠️ Un node tool sobre una mesh **elimina los shape keys**; Simulation Zone y Viewer no funcionan en contexto Tool.

## Cuándo NO usar Geometry Nodes

- **Menos de ~4 variantes de un prop** → duplicar y editar a mano es más rápido que parametrizar. El generador se paga solo cuando amortiza: decenas de instancias, iteración de layout, o un kit que crecerá.
- **Un héroe único** (el asset protagonista) → modelado directo/sculpt; GN como mucho para detalles repetidos (remaches, cadenas).
- **UVs de calidad** → los nodos de UV (UV Unwrap, Pack UV Islands) existen pero un unwrap manual sigue dando mejor resultado para texturizado serio [ver: edicion-malla].
- **Cuando el árbol supera lo que entiendes de un vistazo** → un node group de 200 nodos sin documentar es deuda técnica igual que código espagueti. Frames con nombre, subgrupos, y si aún así crece: quizá era un script bpy [ver: bpy-scripting].
- **Presión de tiempo + resultado único** → GN brilla en lo REPETIBLE. Para una sola pieza, el camino corto es el camino.

## Dónde va la línea con el engine

GN **no sustituye** las herramientas de población del engine. La línea:

| Se hace en Blender (GN) | Se hace en Unity |
|---|---|
| Generar el asset y sus variantes (rocas 1-N, módulos de valla, cables) | Poblar el nivel con esos prefabs (terrain details, prefab brushes, herramientas de scatter del engine) |
| Scatter "horneado" que forma parte de UN asset (musgo sobre la roca) | Scatter masivo de nivel: vegetación de terreno con instancing GPU, culling y LODs del engine |
| Variación offline (seed → FBX) | Variación runtime (aleatorizar rotación/tinte al instanciar) |
| Geometría paramétrica de autor | Colliders, lightmaps, streaming, LOD groups |

Motivo técnico: el instancing de GN muere en el FBX (tabla anterior); el instancing del engine vive en runtime con culling y batching. Hornear 10.000 hierbas en una mesh es la receta del frame drop [ver: pipeline/arte-a-unity].

## bpy: patrones para operar headless

Crear el modificador y setear inputs (⚠️ API cambiada en 5.2):

```python
import bpy
obj = bpy.context.object
mod = obj.modifiers.new(name="GN", type='NODES')
mod.node_group = bpy.data.node_groups["GN_Rocas"]

# Los inputs se referencian por IDENTIFIER del socket, no por nombre visible:
for item in mod.node_group.interface.items_tree:
    print(item.name, getattr(item, "identifier", ""))

# Blender 5.2+ (release notes 5.2, API RNA nueva) — ⚠️ NO RE-VERIFICADO de forma independiente
# (docs.blender.org bloqueó el fetch en esta auditoría): antes de confiar en esta sintaxis exacta,
# comprobar en la sesión real con `print([a for a in dir(mod) if "input" in a.lower()])` o
# `print([a for a in dir(mod.properties) if not a.startswith("_")])` y ajustar si el nombre difiere.
mod.properties.inputs["Socket_2"].value = 350
mod.properties.inputs["Socket_3"].type = "ATTRIBUTE"
mod.properties.inputs["Socket_3"].attribute_name = "densidad"
# Blender <= 5.1 (API vieja, la que sale en casi todos los foros — esta sí confirmada):
#   mod["Socket_2"] = 350
```

Loop de variantes → FBX (una variante por seed):

```python
import bpy
for seed in range(1, 6):
    mod.properties.inputs["Socket_5"].value = seed   # input "Seed"
    dup = obj.copy(); dup.data = obj.data.copy()
    bpy.context.collection.objects.link(dup)
    with bpy.context.temp_override(object=dup, active_object=dup, selected_objects=[dup]):
        bpy.ops.object.modifier_apply(modifier="GN")  # colapsa a mesh real
    bpy.ops.export_scene.fbx(filepath=f"/tmp/roca_{seed:02d}.fbx",
                             use_selection=True, use_mesh_modifiers=True)
```

- Para leer la geometría evaluada sin aplicar nada: API `GeometrySet` (4.5+) sobre el objeto evaluado del depsgraph.
- Verificar SIEMPRE el resultado tras aplicar/exportar (conteo de vértices en el Spreadsheet o `len(dup.data.vertices)`), no asumir que el árbol hizo lo esperado.

## Recursos canon y ecosistema

| Recurso | Qué es | Por qué importa |
|---|---|---|
| Manual oficial (docs.blender.org, sección Geometry Nodes) | Referencia nodo a nodo, fields, atributos | La única fuente siempre al día con 5.2 LTS |
| Release notes (developer.blender.org/docs/release_notes/) | Cambios por versión | Filtro obligatorio contra tutoriales viejos |
| **Geometry Nodes from Scratch** — Blender Studio (Simon Thommes) | Curso oficial de fundamentos | Su autor es artista del Studio y miembro del módulo Geometry Nodes |
| **Erindale** (YouTube/Patreon, erindale.xyz) | Canal/formador de referencia en GN | Senior Generator Artist en Unity Technologies; nivel avanzado real |
| **Geo-Scatter** (geoscatter.com; venta en Superhive/Gumroad, de pago) | EL addon de scattering/biomas | Estándar de facto para entornos; Biome-Reader gratis para consumir biomas. Compatibilidad con 5.x: verificar antes de comprar |
| **BagaPie** (extensions.blender.org, gratis) | 50+ herramientas GN: scatter, ivy, arrays, arquitectura, pie menu `J`; GeoPack para empaquetar tus propios tools | Atajo enorme para props/entorno sin armar árboles; verificar versión soportada |
| **Higgsas Geometry Nodes Toolset Pack** (Gumroad) | Pack de node groups utilitarios (deformadores, arrays, curvas) | Pay-what-you-want desde €12 (consultado 2026-07); cubre Blender 3.3–5.0 según su página — en 5.2 verificar |
| Biblioteca **Essentials** (incluida en Blender) | Node groups oficiales | Gratis, mantenida por el equipo, cero riesgo de compatibilidad |

## Reglas prácticas

1. Antes de seguir un tutorial: ¿qué versión usa? Nodos "Attribute Math/Mix" = pre-3.0, basura. `mod["Socket_X"]` en Python = pre-5.2.
2. Todo generador expone `Seed` como input del grupo. Variar = cambiar un número, nunca reconstruir.
3. Instancias hasta el final del árbol; **Realize Instances** solo si el paso siguiente lo exige (deformar por elemento, exportar como mesh única).
4. Antes de exportar FBX: decidir consciente — realize (un asset), `Object ‣ Apply ‣ Visual Geometry to Objects` (muchos objetos, mallas compartidas), o poblar en Unity con prefabs.
5. UVs procedurales: **Store Named Attribute** tipo *2D Vector*, dominio *Face Corner*, nombre `UVMap` — y comprobar en Unity que llegó.
6. Atributos custom que Unity necesite → hornear a vertex color o UV extra; el FBX no lleva atributos genéricos.
7. Densidades y máscaras pintables: input de field en el grupo + vertex group en el objeto. El artista pinta, el árbol obedece.
8. Verificar SIEMPRE en el **Spreadsheet Editor** (dominio, tipo, conteos) y con el nodo **Viewer** (`Ctrl-Shift-Click`) — no adivinar qué hay en la geometría.
9. `Capture Attribute` cuando un valor deba sobrevivir a un cambio de geometría posterior (p. ej. posición original antes de deformar).
10. Node groups con interfaz limpia: nombres de socket para humanos, defaults útiles, subpaneles; el modificador es la UI del artista.
11. Reutilizable = asset: **Mark as Asset** + catálogo + .blend en la biblioteca de `Preferences ‣ File Paths ‣ Asset Libraries`.
12. Kit modular: las piezas generadas respetan la métrica del kit (snap/retícula); GN varía el vestido, no el esqueleto [ver: modelado/entornos-modulares].
13. Perfiles de tubo/cable a 6-8 lados para juego; la resolución de curva con **Resample Curve**, no a ojo.
14. Scatter de NIVEL (hierba masiva, bosques) → herramientas del engine; scatter de ASSET (musgo en la roca) → GN. No cruzar la línea.
15. Antes de armar un scatter propio: probar el modificador de fábrica **Scatter on Surface** (5.0+) — cubre density, Poisson Disk, máscara y seed.
16. ≤3 variantes de un prop → duplicar y editar a mano. El generador solo cuando amortiza.
17. En bpy, inputs del modificador por `identifier` del socket (`interface.items_tree`), nunca por nombre visible.
18. Tras cualquier apply/export por script: verificar conteo de vértices/objetos resultante, no dar por hecho.

## Errores comunes

| Error | Síntoma | Antídoto |
|---|---|---|
| Exportar FBX con instancias sin realizar | El prop llega vacío o incompleto a Unity | Realize Instances o `Visual Geometry to Objects` ANTES de exportar; revisar el FBX reimportándolo |
| Realizar 10k+ instancias "para que exporte" | Blender se arrastra, FBX de cientos de MB, un solo mesh imposible de cullear | Exportar módulos sueltos y poblar en Unity; realize solo para assets compuestos pequeños |
| Seguir tutorial 2.9x con nodos Attribute | Los nodos no existen en 5.x | Filtrar por versión; el rediseño de fields (3.0) invalidó todo lo anterior |
| Mismo field conectado a dos nodos esperando el mismo valor | Resultados distintos "sin explicación" | El field se re-evalúa por consumidor; congelar con **Capture Attribute** |
| Escribir UVs como Vector 3D o en dominio Point | UV rotos/inexistentes en Unity | *2D Vector* + *Face Corner* + Store Named Attribute, nombre `UVMap` |
| Atributo custom por instancia que "desaparece" | El dato no está en Unity ni tras convertir | `Visual Geometry to Objects` no conserva atributos de instancia; hornear antes a vertex color/UV |
| `mod["Socket_2"] = x` no setea el input (API cambiada en 5.2) | Script viejo no setea inputs | Probar `mod.properties.inputs["Socket_2"].value = x` (release notes 5.2); ⚠️ sintaxis no re-verificada en esta auditoría — confirmar con `dir(mod)`/`dir(mod.properties)` en la sesión real antes de asumir cuál forma funciona |
| Correr un node tool sobre mesh con shape keys | Shape keys eliminados sin aviso | Documentado en el manual: los node tools borran shape keys en meshes — aplicar antes o no usar tool ahí |
| Poner el modificador GN en orden equivocado del stack | Scatter flotando tras un Mirror/deform posterior | El GN es un modificador más: el orden del stack manda [ver: modificadores] |
| Armar en GN el scatter de vegetación del nivel entero | FPS muertos en Unity, memoria disparada | La población masiva es del engine (terrain/instancing GPU); GN entrega los prefabs |
| Node group gigante sin frames ni subgrupos | Nadie (ni tú en 2 semanas) entiende el árbol | Frames con nombre, subgrupos por responsabilidad, inputs documentados — o migrar a bpy |
| Confiar en que "Apply Modifiers" del FBX exporta todo | Instancias y datos no-mesh se pierden en silencio | Apply Modifiers exporta la mesh EVALUADA del objeto, no sus instancias; convertir primero |

## Fuentes

- **Manual de Blender 5.2 LTS — Geometry Nodes: Introduction, Fields, Attributes Reference, Realize Instances Node, Node-Based Tools** — docs.blender.org (consultado 2026-07) — definición del sistema, modelo de fields/atributos/dominios, semántica exacta de Realize Instances y de los node tools.
- **Manual de Blender 5.2 LTS — Scatter on Surface Modifier** — docs.blender.org — el scatter de fábrica basado en GN (density, Poisson Disk, máscaras, seed).
- **Manual de Blender 5.2 LTS — Object ‣ Apply (Visual Geometry to Mesh / Visual Geometry to Objects / Make Instances Real)** — docs.blender.org — rutas exactas de conversión de instancias a objetos reales y sus limitaciones (atributos de instancia no conservados).
- **Manual de Blender 5.2 LTS — FBX y FBX (Legacy)** — docs.blender.org — importador FBX nativo nuevo; export vía add-on: Apply Modifiers = mesh evaluada, objetos instanciados solo en escenas estáticas y sin data compartida.
- **Manual de Blender 5.2 LTS — Asset Libraries** — docs.blender.org — node groups como assets primitivos arrastrables a editores de nodos; bibliotecas locales y online.
- **Release notes oficiales 2.92, 3.0, 3.6, 4.0, 4.1, 4.3, 4.5, 5.0, 5.1 y 5.2 (secciones Geometry Nodes / Nodes & Physics / Python API)** — developer.blender.org/docs/release_notes/ — historia de versiones completa, Bundles/Closures/Lists, y el cambio de API Python de inputs del modificador en 5.2.
- **Geometry Nodes from Scratch — Blender Studio, Simon Thommes** — studio.blender.org/training/geometry-nodes-from-scratch/ — curso canónico de fundamentos por un miembro del módulo Geometry Nodes.
- **Erindale (erindale.xyz)** — Senior Generator Artist en Unity Technologies y formador de GN — canal de referencia para nivel avanzado.
- **Geo-Scatter — geoscatter.com** (consultado 2026-07) — addon líder de scattering/biomas; Biome-Reader gratuito; venta en Superhive/Gumroad.
- **BagaPie — extensions.blender.org/add-ons/bagapie/** (consultado 2026-07) — gratis, 50+ herramientas GN (scatter, ivy, arrays, arquitectura), pie menu `J`, GeoPack.
- **Higgsas Geometry Nodes Groups Toolset Pack — higgsas.gumroad.com** (consultado 2026-07) — pack pay-what-you-want desde €12, declarado para Blender 3.3–5.0.
