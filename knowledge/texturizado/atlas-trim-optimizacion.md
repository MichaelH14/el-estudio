# Atlas, trim sheets y optimización de texturas

> **Cuando cargar este archivo:** al decidir CÓMO se reparte la textura de un set de assets — atlas, trim sheet, tileable o bake único —, al fijar resolución y presupuesto de memoria de texturas, al elegir formato de compresión por tipo de mapa para Unity, o al hacer channel packing. Es la capa de *estrategia y presupuesto* de textura; el detalle de UV, bake y pintado vive en [ver: uv-unwrapping], [ver: baking], [ver: texturizado-blender], [ver: substance-y-alternativas]. La entrega final a Unity (canales URP Lit, import) en [ver: texturas-a-unity] y [ver: pipeline/arte-a-unity].

## 1. Las cuatro estrategias de textura (mapa mental)

Antes de texturizar un asset se decide de dónde sale su textura. Cada píxel de textura única cuesta memoria, bandwidth y trabajo de artista; la optimización es **maximizar reutilización sin que se note**.

| Estrategia | Qué es | Cuándo | Coste de memoria |
|---|---|---|---|
| **Bake único** | Una textura exclusiva del asset, horneada de su high-poly [ver: baking] | Hero assets que se ven de cerca y una sola vez (arma del jugador, jefe, prop narrativo) | Alto — 1 set de mapas por asset |
| **Trim sheet** | Una textura de franjas horizontales reutilizable; la geometría mapea cada cara a la franja que le toca (§3) | Todo el detalle lineal de arquitectura y props de calle: marcos, molduras, vigas, paneles | Muy bajo — 1 sheet cubre un set entero |
| **Tileable** | Textura que repite sin costura en X/Y (§4) | Superficies grandes y continuas: pisos, muros, terreno, telas | Muy bajo — 1 textura, área infinita |
| **Atlas** | Varios objetos/materiales empaquetados en UNA textura (§2) | Props sueltos, kits, follaje, UI — para colapsar materiales y draw calls | Medio — depende del empaque |

Regla de reparto (Insomniac, *Sunset Overdrive*, §9): la mayoría del mundo se cubre con **trim + tileable**; el bake único se reserva para lo que de verdad se inspecciona de cerca. Un juego bien optimizado comparte MUCHÍSIMA textura (§9).

## 2. Texture atlas: menos materiales → menos draw calls

Un atlas empaqueta las UVs de varios objetos/materiales en una sola textura, de modo que comparten **un solo material**. El beneficio es de CPU: menos materiales = menos cambios de estado = menos draw calls / SetPass [ver: unity/rendimiento-unity §2].

### El matiz del SRP Batcher (Unity 6 / URP)

Con el **SRP Batcher activo por defecto**, muchos materiales del mismo shader ya se dibujan barato (mantiene datos de material persistentes en GPU) — así que colapsar 20 materiales en 1 por atlas rinde **menos** de lo que rendía en la era pre-SRP-Batcher [ver: unity/rendimiento-unity §2]. Dónde el atlas SIGUE siendo decisivo:

| Caso | Por qué el atlas importa aún |
|---|---|
| **GPU instancing** | Instancing exige *misma malla + mismo material*; un atlas permite que variantes visuales compartan el material y entren al mismo batch [ver: unity/rendimiento-unity §2] |
| **UI / sprites 2D** | Sprite Atlas colapsa el batching de UGUI; sin él, cada sprite es su draw call [ver: pipeline/arte-a-unity §5] |
| **Follaje** | Un atlas por especie → un material para todas las cards [ver: modelado/entornos-modulares §7] |
| **Props de escenario** | Decenas de props chicos en 1-2 atlas = pocas mallas, pocos materiales, instancing viable |

Verificar SIEMPRE con Frame Debugger si el atlas realmente juntó los batches [ver: unity/rendimiento-unity §2] — el atlas mal hecho (padding insuficiente, sRGB mezclado) no ahorra nada.

### Armar un atlas en Blender

Dos rutas: **empacar UVs existentes** en 0-1 (si cada objeto ya está texturizado, se re-empacan sus islas y se hornea a una imagen común) o **texturizar directamente sobre el layout empacado**. Empaque de islas de una selección a una textura común:

```python
import bpy
# En Edit Mode con todas las islas seleccionadas (varios objetos: usar UV editing multi-objeto)
bpy.ops.uv.select_all(action='SELECT')
bpy.ops.uv.pack_islands(margin=0.01)   # margin = padding entre islas (0-1); sube en atlas chicos
```

Hornear los objetos a UNA imagen de atlas (cada material apunta a un nodo Image Texture con la MISMA imagen destino):

```python
img = bpy.data.images.new("Atlas_Albedo", 2048, 2048)   # potencia de 2
bpy.context.scene.render.engine = 'CYCLES'
# margin en PÍXELES: rellena más allá del borde de isla para no sangrar en los mips
bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'}, margin=8, save_mode='EXTERNAL')
```

> ⚠️ Operadores `bpy.ops.uv.pack_islands` / `bpy.ops.object.bake` son estables desde 2.8 y su firma incluye `margin`/`save_mode`; **NO reverificados contra las docs de Blender 5.2 en esta sesión** (docs.blender.org bloqueó el fetch). El detalle de parámetros de bake y de UV vive en [ver: baking] y [ver: uv-unwrapping] — no repetir aquí.

### Padding: el error clásico del atlas

Sin **padding** (margen entre islas), los mip levels bajos promedian píxeles de islas vecinas → sangrado de color en los bordes a distancia. Regla operativa: padding proporcional al tamaño y al número de mips que vas a usar; en atlas 2K/4K, 8-16 px entre islas. El Sprite Atlas de Unity añade su propio padding [ver: pipeline/arte-a-unity §5] — por eso los sprites 2D se entregan SUELTOS, sin padding cocido.

**Atlas vs Texture2DArray:** para muchas variantes del mismo tamaño (terreno multicapa, variantes de módulo) un `Texture2DArray` evita el problema de padding/bleed y el desperdicio de espacio del atlas — mismo material, índice de capa por vértice/instancia. El atlas plano gana para formas irregulares que aprovechan el hueco.

## 3. Trim sheets a fondo: el UV es todo

El concepto de trim sheet, el caso canónico (*Sunset Overdrive*, "The Ultimate Trim") y su papel en el kit modular ya están en [ver: modelado/entornos-modulares §4] — **no se repite aquí**. Este archivo cubre la mecánica de textura y de UV que hace funcionar el trim.

### Anatomía del sheet

Un trim sheet es una textura donde el eje **V (vertical)** se divide en **franjas horizontales** de distinta altura, cada una un motivo distinto (moldura ancha, zócalo, tira de tornillos, panel liso, bisel), y el eje **U (horizontal) es tileable** dentro de cada franja.

```
 V=1.0 ┌──────────────────────────┐
       │  cornisa / moldura grande │  ← franja alta
 V=0.7 ├──────────────────────────┤
       │  panel con biselado 45°   │
 V=0.5 ├──────────────────────────┤
       │  tira de tornillos/remaches│  ← franja fina
 V=0.4 ├──────────────────────────┤
       │  liso / tileable neutro   │
 V=0.0 └──────────────────────────┘
        U tilea →  (repite en horizontal)
```

### Cómo se hace el UV del trim (la parte que importa)

1. **Geometría low-poly con bordes duros** donde el bevel del normal map hace la transición — las normales promediadas arruinan el efecto [ver: modelado/entornos-modulares §4], [ver: baking].
2. **Cada cara (loop de la pieza) se asigna a una franja**: se selecciona la cara, se hace un unwrap simple (project/box) y se **escala y mueve la isla en V** para que ocupe exactamente el rango de su franja (p. ej. V 0.4–0.5 para la tira de tornillos).
3. **En U la isla puede salirse de 0-1**: la franja tilea en horizontal, así que una viga larga estira su U más allá de 1.0 y el motivo se repite. Cero necesidad de más textura.
4. **Alinear al píxel de la franja**: el borde de la isla en V debe caer exacto en el límite de la franja, o la cara agarra medio motivo vecino. Snappear V a las coordenadas del layout (útil una guía numérica del sheet).
5. **Padding entre franjas** en el sheet mismo: dejar unos píxeles muertos entre motivos para que los mips no sangren de una franja a la de al lado [ver: modelado/entornos-modulares §4].
6. **Una misma cara puede cortarse y saltar a otra zona** de su franja para variar el desgaste sin nueva geometría.

No hay operador "trim" de un clic en Blender: es unwrap + transform de islas en el UV editor [ver: uv-unwrapping]. El valor está en la disciplina de V, no en una herramienta.

### La regla de oro del trim

**Layout de franjas idéntico entre materiales.** Si el sheet de metal, el de madera y el de concreto tienen las franjas en los MISMOS rangos V, cambiar el material de un edificio entero = cambiar UNA textura, y cada cara sigue cayendo en su sitio [ver: modelado/entornos-modulares §4]. Esa es la palanca de reutilización más grande de arquitectura.

## 4. Tileables: sin costura, y cuándo mezclarlos

Un tileable repite en X e Y sin costura visible. El detalle de creación (offset, healing, síntesis) vive en [ver: texturizado-blender] / [ver: substance-y-alternativas]; aquí, la **decisión**.

### Tileable vs textura única

| Usa TILEABLE | Usa ÚNICA (bake) |
|---|---|
| Superficie grande y continua (piso, muro, terreno) | Silueta y detalle irrepetible (cara, arma hero) |
| Texel density constante importa más que el detalle específico | El asset se ve de cerca una vez |
| Se repite por todo el nivel | Aparece una vez |
| Presupuesto de memoria ajustado (móvil) | Presupuesto de hero asset |

### Romper la repetición (mezclar tileable + detalle único)

Un tileable perfecto se delata por repetición. En orden de coste (detalle de las capas en [ver: modelado/entornos-modulares §4]):

| Técnica | Coste extra | Notas |
|---|---|---|
| **Decals** | 1 draw/quad proyectado | Manchas, grietas, grafiti sobre el tileable base; el detalle único donde hace falta, sin subir la textura base [ver: unity/rendimiento-unity] |
| **Detail map** (URP Lit) | 1 sample + 1 textura chica | Segunda textura tileada a alta frecuencia que se multiplica sobre la base; da microdetalle de cerca sin subir la resolución base |
| **Vertex color / máscaras** | Casi gratis (por vértice) | Tinte y desgaste por instancia sobre el mismo material — sin nuevas texturas [ver: modelado/entornos-modulares §4] |
| **Blend de 2 tileables** | +1 sample | Mezclar dos tileables por máscara/vertex (musgo sobre piedra) |

El texel density del tileable se declara en la spec y se mantiene consistente con el resto del set [ver: pipeline/arte-a-unity §7] — un tileable a otra densidad canta al lado de sus vecinos.

## 5. Resolución: presupuesto, no "4K por defecto"

La resolución NO se elige por "que se vea bien"; se deriva de **texel density × tamaño del objeto en mundo × cuánto se acerca la cámara**, y se topa por presupuesto de plataforma.

### Potencias de 2 (obligatorio en la práctica)

Los formatos de bloque operan sobre bloques fijos de texels — **4×4 en BC*/ETC2**, y **de 4×4 hasta 12×12 en ASTC** (bloque elegible por el artista, ver tabla §6) — y los mipmaps se generan dividiendo entre 2 en cada nivel. Texturas potencia de 2 (256, 512, 1024, 2048, 4096) garantizan que la textura completa (y cada mip) se divida en bloques exactos, sin relleno parcial en el borde. Unity acepta NPOT pero la compresión y el mipmapping se degradan → **siempre POT** para todo lo que se comprime y mipmapea [ver: unity/rendimiento-unity §8], [ver: pipeline/arte-a-unity §7]. Rectangulares POT (2048×1024) están OK; los trim sheets suelen ser 2:1 o 4:1.

### Cuándo cada resolución (criterio, no reflejo)

| Resolución | Uso típico | Cuándo NO subir de ahí |
|---|---|---|
| **256** | Props chicos lejanos, LODs, iconos de mundo | Nunca se acerca la cámara |
| **512** | Props estándar, mobiliario, tileables móvil | Se ve a media distancia; móvil |
| **1024** | Props protagonistas, trim sheets, tileables PC, personajes móvil | El grueso del contenido: default sano para muchos assets |
| **2048** | Hero props, personajes principales, tileables de alta calidad PC | Se inspecciona de cerca |
| **4096** | Solo hero assets cinemáticos / superficies enormes en PC/consola | Casi nunca en móvil — cuesta 16 MB (BC7) por mapa (§7) |

Regla: **empezar bajo y subir solo si la cámara real lo justifica**, comparando en pantalla del device, no en el inspector [ver: unity/rendimiento-unity]. La densidad debe ser consistente entre assets del mismo plano — no un prop a 512 px/m junto a otro a 2048 px/m [ver: pipeline/arte-a-unity §7]. Presupuestos de textura por gama de móvil: [ver: unity/rendimiento-unity §6] (orientativos: baja ≤1024, media ≤2048, alta 2048-4096).

## 6. Compresión en Unity: formato correcto por tipo de mapa

Una textura sin comprimir (RGBA32 = 32 bpp) cuesta 4-8× más memoria y bandwidth que comprimida — **nunca "None" en un build** [ver: unity/rendimiento-unity §8]. El formato se elige por **plataforma × tipo de mapa**, con **override por plataforma** en el importer [ver: pipeline/arte-a-unity §7].

### Formato por tipo de mapa (Unity 6 / URP)

| Mapa | Desktop/PC | Móvil (Android/iOS) | sRGB | Por qué |
|---|---|---|---|---|
| **Albedo / Base color** | BC7 (calidad) o DXT1/BC1 (sin alpha, rápido) | ASTC 4x4–6x6 | **On** | Color: necesita el gamma correcto |
| **Albedo + alpha** | BC7 o DXT5/BC3 | ASTC 4x4–6x6 | **On** | El alpha va en el mismo bloque |
| **Normal map** | **BC5** (2 canales, reconstruye Z) | ASTC 5x5–6x6 | **Off** | Datos direccionales, no color; BC5 evita el artefacto de banda de DXT |
| **Mask / ORM / metallic-smoothness** | **BC7** (linear) | ASTC 5x5–6x6 | **Off** | Datos, no color; BC7 preserva los 3-4 canales |
| **Un solo canal** (height, AO suelto, roughness suelto) | **BC4** (1 canal, 4 bpp) | ASTC / EAC_R | **Off** | La mitad de memoria que un RGB |
| **HDR** (emission fuerte, lightmap) | **BC6H** | ASTC HDR (requiere soporte) | **Off** | Rango >1 sin clamp |

`bpp` verificados (Unity, GPU texture formats reference): DXT1/BC1 = 4, DXT5/BC3 = 8, BC4 = 4 (1 canal), BC5 = 8 (2 canales), BC6H = 8 (HDR), BC7 = 8, ETC2 = 4-8, ASTC = 8 (4×4) → 0.89 (12×12). El punto medio móvil habitual para albedo es ASTC **6x6 (3.56 bpp)**; normales exigen algo más de calidad (5x5 ≈ 5.12 bpp) [ver: unity/rendimiento-unity §8].

### Impacto en memoria (calculado: W×H×bpp/8; +33% con mipmaps)

| Tamaño | RGBA32 (crudo) | BC7 / ASTC4x4 / BC5 (8bpp) | DXT1 / BC4 (4bpp) | ASTC 6x6 (3.56bpp) |
|---|---|---|---|---|
| 1024² | 4.00 MB | 1.00 MB | 0.50 MB | 0.45 MB |
| 2048² | 16.00 MB | 4.00 MB | 2.00 MB | 1.78 MB |
| 4096² | 64.00 MB | 16.00 MB | 8.00 MB | 7.12 MB |

Con la cadena completa de mipmaps, multiplicar por ~1.33 (§7). Lectura clave: **un solo hero prop con 4 mapas a 4096 sin comprimir = 256 MB** — imposible en móvil; los mismos 4 mapas en ASTC 6x6 a 2048 con mips ≈ 9.5 MB. La compresión no es opcional.

- **sRGB Off es crítico** en normal/mask/roughness/metallic/AO: tratarlos como color rompe los valores lineales [ver: pipeline/arte-a-unity §7].
- **Read/Write Off** salvo que un script lea píxeles — activarlo DUPLICA la memoria (copia en CPU) [ver: pipeline/arte-a-unity §9].

## 7. Mipmaps, streaming y presupuesto de memoria

**Las texturas son el mayor consumidor de RAM en móvil** — el orden de ataque (compresión → tamaño máximo → mipmaps/streaming → carga/descarga) está en [ver: unity/rendimiento-unity §8]. Aquí, mipmaps y streaming al detalle.

### Mipmaps

- Cuestan **+33% de memoria y disco** (la suma de la serie 1 + ¼ + 1⁄16 + … ≈ 1.333×), pero bajan cache misses/bandwidth y evitan el shimmer a distancia.
- **Activar en 3D**; **desactivar en UI/2D pixel-perfect** que se renderiza a resolución nativa — ahí el 33% es puro desperdicio [ver: unity/rendimiento-unity §8], [ver: pipeline/arte-a-unity §9].

### Mipmap Streaming (Unity)

Carga solo los mip levels que la cámara necesita según distancia, recortando VRAM en escenas grandes. Configuración (verificada, Unity Manual):

| Ajuste | Dónde | Qué hace |
|---|---|---|
| **Memory Budget** | Project Settings > Quality > Textures | Presupuesto en MB para el streaming Y todos los mips de texturas que no lo usan; Unity descarta mips para no pasarse |
| **Add All Cameras** | mismo panel | Todas las cámaras participan del streaming por defecto |
| **Streaming Controller** (componente) | Por cámara | Desactivar streaming o aplicar **Mipmap Bias** (offset a los niveles elegidos) en esa cámara |
| **Max Level Reduction** | Config | Impide que Unity baje de cierto mip; fija la resolución inicial al arrancar |

APIs: `QualitySettings.streamingMipmapsActive`, `StreamingController.streamingMipmapBias`, `Texture.desiredTextureMemory`. La textura debe importarse con **Stream Mipmap Levels** activo para participar. Diagnóstico de memoria de texturas y leaks con Memory Profiler [ver: unity/rendimiento-unity §8].

## 8. Channel packing: menos texturas, menos samples

Los mapas de datos (roughness, metallic, AO, height, máscaras) son **grayscale** → desperdician 2-3 canales si van sueltos. Empacar 3-4 en los canales RGBA de UNA textura ahorra: **memoria, un texture bind y un texture sample** en el shader (samples son un coste de GPU real en móvil) [ver: unity/rendimiento-unity §6].

### Los tres esquemas que importan (¡son distintos!)

| Esquema | R | G | B | A | Dónde |
|---|---|---|---|---|---|
| **URP Lit metallic** (default) | Metallic | — | — | **Smoothness** | El Metallic Map de URP ya es un pack: metallic en grayscale + smoothness en su alpha [ver: pipeline/arte-a-unity §7] |
| **HDRP Mask Map** | **Metallic** | **Occlusion (AO)** | **Detail mask** | **Smoothness** | Verificado (HDRP Manual); valor por defecto de cada canal = 0.5 |
| **glTF ORM** (Metallic-Roughness) | Occlusion | **Roughness** | **Metallic** | — | El que importa `Unity glTFast` [ver: pipeline/arte-a-unity §7]; ⚠️ **roughness, no smoothness** |

Dos trampas que se pagan caro:

1. **URP usa smoothness = 1 − roughness.** Substance/glTF exportan **roughness**; hay que **invertir el canal** o exportar con el preset "Unity URP (Metallic Smoothness)" [ver: pipeline/arte-a-unity §7], [ver: substance-y-alternativas]. Meter roughness donde URP espera smoothness = material lavado/plateado.
2. **No se packea el normal map con datos escalares.** El normal quiere **BC5** (2 canales, alta calidad) y sRGB Off; el mask quiere BC7. Formatos distintos → texturas separadas. El pack es para los grayscale (metallic/rough/AO/height), no para el normal.

- Todo mapa packeado va con **sRGB Off** (son datos lineales, no color).
- En URP, la **Occlusion** es un mapa aparte del Metallic-Smoothness [ver: pipeline/arte-a-unity §7]; si quieres un ORM de 3 canales de estilo UE, lo montas tú y lo muestreas desde un shader custom / Shader Graph [ver: pbr-teoria].

### Empaque práctico

Substance Painter exporta el pack directo con su editor de output templates [ver: substance-y-alternativas]. En Blender/manual: componer con nodos o un script que meta cada grayscale en su canal antes de exportar. La spec de qué mapa va en qué canal se **congela el día 1** [ver: pipeline/arte-a-unity §1] — cambiarla a mitad de producción re-hornea todo.

## 9. Reutilización: cuánta textura comparte un juego optimizado

La respuesta corta: **muchísima, por diseño**. Métricas y casos canónicos en [ver: modelado/entornos-modulares §4]:

- **Insomniac / Sunset Overdrive**: una ciudad de ~1400×2400 m texturizada con 8-12 artistas usando, **por material, un par trim + tileable liso** — "con esos dos podemos cubrir cualquier superficie del juego" [ver: modelado/entornos-modulares §4].
- **Kit modular**: un kit entero comparte 1 trim + 2-3 tileables → cientos de piezas, un puñado de texturas, y batching/instancing barato [ver: modelado/entornos-modulares §1, §8].
- **Props**: agrupados en 1-2 atlas por bioma; instancing donde se repiten.
- **Bake único**: presupuestado SOLO para hero assets, al final, no al inicio [ver: modelado/entornos-modulares §1].

Presupuesto mental sano: el 80-90% del mundo cubierto con texturas compartidas (trim + tileable + atlas); el bake único es el lujo que se gasta con cuentagotas. Si cada asset trae su propia textura 2K, el proyecto no cabe en memoria y el batching muere [ver: unity/rendimiento-unity §8].

## Reglas prácticas

- [ ] Decide la estrategia de textura por asset ANTES de pintar: bake único solo para hero; el resto trim/tileable/atlas (§1).
- [ ] Trim + tileable compartidos cubren la arquitectura; el bake único no escala a un entorno [ver: modelado/entornos-modulares §4].
- [ ] Trim: cada cara escalada a su franja en V, U puede salir de 0-1 (tilea), borde de isla exacto en el límite de franja, padding entre franjas.
- [ ] Layout de franjas IDÉNTICO entre materiales del trim → cambiar el look de un edificio = cambiar una textura.
- [ ] Tileable para superficies grandes; rompe la repetición con decals + detail map + vertex color, no con más texturas base (§4).
- [ ] Atlas para props/UI/follaje y para habilitar GPU instancing; con SRP Batcher el beneficio de material-count es menor, verifica con Frame Debugger [ver: unity/rendimiento-unity §2].
- [ ] Padding en TODO atlas y trim sheet (8-16 px en 2K/4K) contra sangrado de mips.
- [ ] Todas las texturas potencia de 2 (rectangulares POT OK); NPOT rompe compresión y mips.
- [ ] Resolución por texel density × tamaño × cercanía de cámara; empieza bajo, sube solo si el device lo justifica. 1024 es un default sano, no 4096.
- [ ] Nunca "None": comprime siempre en builds. Normal → BC5/ASTC, albedo → BC7/DXT1/ASTC, mask → BC7/ASTC linear, single-channel → BC4 (§6).
- [ ] sRGB **Off** en normal/mask/roughness/metallic/AO/height; **On** solo en color/albedo/emission.
- [ ] Override de compresión por plataforma (ASTC móvil, BC desktop) en el importer [ver: pipeline/arte-a-unity §7].
- [ ] Channel packing: metallic+smoothness en una RGBA (URP ya lo hace); no packear el normal con datos escalares (formatos distintos).
- [ ] URP espera smoothness = 1 − roughness: invierte o usa el preset "Unity URP (Metallic Smoothness)" [ver: substance-y-alternativas].
- [ ] Mipmaps ON en 3D (+33%), OFF en UI/2D pixel-perfect; Mipmap Streaming con Memory Budget en escenas grandes (§7).
- [ ] Read/Write Off salvo lectura real por script (duplica memoria).
- [ ] Presupuesta el bake único con cuentagotas: 80-90% del mundo con textura compartida.
- [ ] Congela el esquema de canales del pack el día 1 (spec) — cambiarlo después re-hornea todo [ver: pipeline/arte-a-unity §1].

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Textura única 2K para cada prop "para que se vea bien" | Trim/tileable/atlas compartido; el bake único es para hero. El proyecto no cabe en RAM si no (§9) |
| Atlas sin padding → bordes que sangran color a distancia | 8-16 px entre islas; el sangrado aparece en los mips bajos, no a 1:1 |
| Contar con que el atlas baja draw calls y no verificar | Con SRP Batcher el beneficio cambia; Frame Debugger dice si los batches se juntaron [ver: unity/rendimiento-unity §2] |
| Trim con las islas mal alineadas en V → caras que agarran medio motivo vecino | Borde de isla exacto en el límite de franja; snap numérico en V |
| Layout de franjas distinto entre materiales del trim | Estandarizar el layout: es lo que permite swap de material de un edificio con una textura |
| Tileable impecable que canta a repetición a 10 m | Capas de ruptura: decals, detail map, vertex color, blend — no subir la resolución base [ver: modelado/entornos-modulares §4] |
| 4096 "por defecto porque hay presupuesto" | Resolución por texel density y cámara real; 4096 casi nunca en móvil (16 MB/mapa en BC7) |
| Textura NPOT (1000×1000, 1500×...) | Potencia de 2; NPOT degrada compresión y mipmapping |
| Compresión "None" para conservar calidad | Comprime siempre; RGBA32 cuesta 4-8× y peta el bandwidth [ver: unity/rendimiento-unity §8] |
| Normal map en DXT5/BC7 con banding, o con sRGB On | BC5 (2 canales, sRGB Off); DXT y sRGB destrozan el normal |
| Mask/roughness/metallic importados con sRGB On | sRGB Off: son datos lineales, no color; con On los valores salen mal |
| Meter roughness donde URP espera smoothness → material plateado | Invertir (1 − roughness) o preset "Unity URP (Metallic Smoothness)" [ver: pipeline/arte-a-unity §7] |
| Packear el normal en el mask map "para ahorrar una textura" | Normal quiere BC5; mask quiere BC7 — formatos distintos, texturas separadas |
| Mipmaps activados en atlas de UI | Desactivar: +33% de memoria sin beneficio a resolución nativa [ver: unity/rendimiento-unity §8] |
| Read/Write Write On "por si acaso" en todas las texturas | Duplica la memoria; solo cuando un script lea píxeles de verdad |
| Cambiar el esquema de canales del pack a media producción | Congelar el día 1; el cambio re-hornea todos los assets |

## Fuentes

Verificadas por fetch directo en esta investigación (2026-07-20), Unity contra 6000.x salvo indicación:

- **GPU texture formats reference** — Unity Manual (`texture-formats-reference.html`) — bpp y canales exactos: BC1/DXT1=4, BC3/DXT5=8, BC4=4 (1 canal), BC5=8 (2 canales, normales), BC6H=8 (HDR), BC7=8, ETC2=4-8, ASTC 4×4→12×12.
- **Choose a GPU texture format by platform** — Unity Manual (`texture-choose-format-by-platform.html`) — recomendaciones por plataforma: desktop DXT1/BC7/DXT5/BC6H; iOS ASTC (8→0.89 bpp) / ETC2 / PVRTC legacy; Android ASTC (ES 3.1+/Vulkan) / ETC2 / fallback a RGBA32.
- **Texture compression formats** — Unity Manual (`texture-compression-formats.html`) — página índice de compresión de texturas.
- **Mipmaps introduction** — Unity Manual (`texture-mipmaps-introduction.html`) — coste +33%, cuándo activar (3D) vs desactivar (UI a resolución nativa), enlace a Mipmap Streaming.
- **Configure Mipmap Streaming** — Unity Manual (`TextureStreaming-configure.html`) — Memory Budget (Quality > Textures), Add All Cameras, componente Streaming Controller, Mipmap Bias, Max Level Reduction; APIs `streamingMipmapsActive`, `streamingMipmapBias`, `desiredTextureMemory`.
- **Normal map texture type** — Unity Manual (`texture-type-normal-map.html`) — opciones de import (Create From Grayscale, Bumpiness, Flip Green Channel, Generate/Stream Mipmap, Read/Write, Non Power of 2).
- **Mask Map and Detail Map** — Unity HDRP Manual (`com.unity.render-pipelines.high-definition`, `Mask-Map-and-Detail-Map.html`) — channel packing del mask map: **R=Metallic, G=Occlusion, B=Detail mask, A=Smoothness**, default 0.5 por canal; detail map R=albedo desat, G=normalY, B=smoothness, A=normalX.
- **Adaptive scalable texture compression (ASTC)** — Wikipedia — tabla de bloques 4×4 (8.00 bpp) → 12×12 (0.89 bpp), bloque fijo 128-bit, LDR/HDR, soporte por GPU.

No accesibles por bloqueo del fetcher en esta sesión (403/timeout host-level) — cubiertos vía las bases ya sintetizadas: docs.blender.org (bake/UV), Marmoset, 80.lv, Adobe Substance helpx. La mecánica de trim, el caso "Ultimate Trim" (GDC 2015) y el hilo de Polycount ya están sintetizados y citados en [ver: modelado/entornos-modulares §4].

Cálculo de memoria de textura (tabla §6): aritmética directa `W×H×bpp/8` (+1.33× con mips), computada en esta sesión, no citada de terceros.

Bases sintetizadas y cruzadas: [ver: unity/rendimiento-unity] (draw calls/batching §2, compresión y memoria §8, presupuestos móvil §6), [ver: modelado/entornos-modulares] (trim sheets/tileables/kit §1,§4,§8), [ver: pipeline/arte-a-unity] (canales URP Lit, smoothness=1−roughness, POT, import §1,§7,§9). Detalle no repetido aquí en [ver: uv-unwrapping], [ver: baking], [ver: texturizado-blender], [ver: substance-y-alternativas], [ver: pbr-teoria], [ver: texturas-a-unity].
