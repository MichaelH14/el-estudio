# Shader Graph: fundamentos

> **Cuando cargar este archivo:** al crear o modificar un shader con Shader Graph en Unity 6 / URP — armar el grafo, elegir target y Master Stack, exponer propiedades en el Blackboard, usar nodos (texturas, noise, Fresnel, math, tiempo), decidir espacios (object/world/tangent), reutilizar lógica con Sub Graphs, meter HLSL con Custom Function, o conectar el shader a material y a código. Para el pipeline gráfico base (URP Asset, shaders prebuilt, SRP Batcher, Bloom) [ver: unity/rendering-urp]. Para el PORQUÉ del feel visual [ver: gamedev/game-feel]; para las RECETAS concretas de efectos (dissolve, hit flash, outline, agua) [ver: recetas-shaders].

Este archivo cubre la mecánica de Shader Graph. Las recetas paso-a-paso viven en [ver: recetas-shaders] y [ver: vfx-2d]; VFX Graph y partículas en [ver: particulas-vfx-graph] y [ver: vfx-recetas]; optimización en [ver: optimizacion-vfx].

## Qué es Shader Graph

Herramienta visual de Unity para construir shaders conectando **nodos** en vez de escribir HLSL a mano. El grafo se compila a un shader real que se usa igual que cualquier otro (se asigna a un material). Es un **package** (`com.unity.shadergraph`); en Unity 6 la versión es **17.x** (6.0 → 17.0, 6.1 → 17.1, 6.2 → 17.2). Viene incluido con URP y HDRP; NO funciona con Built-in salvo instalando el package y usando el target Built-in (poco común).

- Ventaja: iteración visual con **preview en vivo** por nodo, sin recompilar a mano, sin sintaxis HLSL.
- Límite: cada nodo tiene coste; un grafo grande genera mucho código por pixel. No sustituye a HLSL para lo muy complejo (ver sección "Shader Graph vs HLSL").

## Anatomía del grafo: Master Stack y targets

El grafo produce su salida final en el **Master Stack**, dividido en dos **contextos** que son las dos etapas del shader:

| Contexto | Qué controla | Corre por |
|---|---|---|
| **Vertex** | Posición/normal/tangente de cada vértice (deformación, wind, wave) | Vértice |
| **Fragment** | Color y propiedades de superficie de cada pixel | Pixel |

Cada contexto contiene **Blocks** (bloques). Un Block es una pieza de la surface/vertex description. **Blocks built-in exactos** (nombre y tipo confirmados en la doc):

| Contexto | Block | Tipo |
|---|---|---|
| Vertex | **Position** | Vector 3 |
| Vertex | **Normal** | Vector 3 |
| Vertex | **Tangent** | Vector 3 |
| Vertex | **Color** | Vector 4 |
| Fragment | **Base Color** | Vector 3 |
| Fragment | **Normal (Tangent Space)** / **Normal (Object Space)** / **Normal (World Space)** | Vector 3 |
| Fragment | **Emission** | Vector 3 |
| Fragment | **Metallic** | Float |
| Fragment | **Specular** | Vector 3 |
| Fragment | **Smoothness** | Float |
| Fragment | **Ambient Occlusion** | Float |
| Fragment | **Alpha** | Float |
| Fragment | **Alpha Clip Threshold** | Float |

- **Qué blocks aparecen depende del target y de los Graph Settings.** Ej.: Metallic vs Specular según el Workflow Mode; `Alpha Clip Threshold` solo si activas **Alpha Clipping**; los targets Sprite exponen otro set. Cambiar un setting agrega/quita blocks del stack.
- **Emission > 1** (con HDR ON) es lo que alimenta el Bloom para glow selectivo [ver: unity/rendering-urp].

### Targets (a qué pipeline compila)

Shader Graph soporta **3 targets**: Universal Render Pipeline, High Definition Render Pipeline, Built-In Render Pipeline. Se elige en **Graph Settings** (rueda dentada del Blackboard/Graph Inspector). Un mismo grafo puede tener varios targets activos.

Sub-targets del target **Universal (URP)** — se elige el correcto al crear (`Assets > Create > Shader Graph > URP > …`). **Lit/Unlit** confirmados contra la doc oficial (Graph Target); el resto (Sprite Lit/Unlit/Custom Lit, Canvas, Decal, Fullscreen) viene del menú de creación de Unity 6 — no se pudo re-confirmar contra una página que los liste todos juntos en esta sesión (los fetches a slugs candidatos dieron 404):

| Sub-target URP | Para qué |
|---|---|
| **Lit** | Superficie PBR con iluminación (default 3D realista) |
| **Unlit** | Sin iluminación (VFX, UI en mundo, estilo flat) |
| **Sprite Lit** | Sprite 2D que recibe Light 2D (necesita 2D Renderer) |
| **Sprite Unlit** | Sprite 2D sin luces |
| **Sprite Custom Lit** | Sprite 2D con modelo de luz custom |
| **Canvas** | Shaders para UI (uGUI Canvas) |
| **Decal** | Proyección de decals sobre superficies |
| **Fullscreen** | Efecto a pantalla completa (Fullscreen Pass Renderer Feature) |

⚠️ El sub-target importa: **Sprite Lit** para 2D con luces, **Sprite Unlit** si el juego 2D no usa Light 2D. Elegir mal = el sprite no reacciona (o no) a las luces. [ver: vfx-2d]

## Blackboard: exponer parámetros

El **Blackboard** define los inputs del shader. Tres cosas viven ahí: **Properties**, **Keywords** y **Categories** (grupos colapsables para organizar).

- **Property** = valor customizable que aparece en el **Material Inspector** para ajustarlo sin abrir el grafo.
- **Reference** = el nombre INTERNO que usa el shader (lo que pasas por código: `material.SetFloat("_MiProp", x)`). Auto-generado, editable; caracteres no soportados → underscore. ⚠️ Usar la **Reference**, no el display name, al setear por código.
- **Exposed** (toggle, punto verde): controla acceso de escritura por C# API. Si lo apagas, la propiedad vuelve a su default y pierde ajustes custom.

### Tipos de Property (confirmados)

| Tipo | Notas |
|---|---|
| **Float** | Modos: Default, **Slider** (min/max), **Integer** |
| **Vector 2 / Vector 3 / Vector 4** | En el inspector muestra un campo Vector4; en V2/V3 los componentes extra se ignoran |
| **Color** | Modos **Default (sRGB)** y **HDR**; puede marcarse **Main Color** (equivale a `_BaseColor`) |
| **Boolean** | Muestra un ToggleUI |
| **Texture 2D** | Puede marcarse **Main Texture** (`_BaseMap`); opciones de fallback (white/black/etc.) |
| **Texture 2D Array / Texture 3D / Cubemap** | Texturas multi-capa / volumétricas / de entorno |
| **Virtual Texture** | Aparece como campos Texture; manejo por capas |
| **Matrix 2 / 3 / 4** | ⚠️ NO se muestran en el Inspector del material (solo por código) |

Nota (verificado con fetch directo a *Property Types* 17.0 en esta sesión): **Gradient** y **Sampler State** NO están en la lista oficial de Property Types del Blackboard — la lista completa y cerrada es la de la tabla arriba (Float, Vector 2/3/4, Color, Boolean, Texture 2D + variantes, Virtual Texture, Matrix 2/3/4). `Sampler State` sí existe como **nodo** (input de `Sample Texture 2D`), no como property expuesta del Blackboard; `Gradient` existe como nodo/tipo de dato pero no confirmado como property. No los des por hecho como property expuesta.

### Keywords (variantes de shader)

Un **Keyword** genera variantes del shader (distintos code-paths). En el grafo se usan como nodos **branch** de keyword: la rama que sobra no se ejecuta. Tipos:

| Tipo | Qué hace |
|---|---|
| **Boolean** | On/off → elige entre 2 ramas |
| **Enum** | 2+ estados → elige entre N ramas |
| **Built-in** | Keywords que ya define Unity (ej. iluminación, instancing) |

**Definition** (crítico para tamaño de build):

| Definition | Comportamiento | Coste |
|---|---|---|
| **Shader Feature** (default) | Solo compila las variantes que USAS en el build; strippea las demás | Build chico/rápido. ⚠️ Riesgo de shader rosado si activas por código una variante que fue strippeada |
| **Multi Compile** | Compila TODAS las variantes pase lo que pase | Flexible en runtime, pero **aumenta mucho build time y tamaño** |

- **Scope**: **Global** (compartida entre shaders, se setea con `Shader.EnableKeyword`) o **Local** (solo este shader, se setea con `material.EnableKeyword`). Regla: si la variante se elige por material en el inspector → Shader Feature; si la alternas por código en runtime → Multi Compile (o asegurar que la variante no se strippee).

## Nodos esenciales

Puertos exactos confirmados en la doc. Categorías en el menú (click derecho → Create Node, o barra espaciadora).

### Input / coordenadas

| Nodo | Puertos | Qué da |
|---|---|---|
| **UV** | Channel (dropdown UV0–UV7) → **Out** (Vector 4) | Coordenadas UV de la malla; u,v en .xy + 2 canales extra |
| **Position** | Space (dropdown) → **Out** (Vector 3) | Posición del vértice/fragmento en el espacio elegido (ver "Espacios") |
| **Normal Vector** | Space → Out (Vector 3) | Normal de la superficie |
| **Time** | Outputs: **Time**, **Sine Time**, **Cosine Time**, **Delta Time**, **Smooth Delta** | Sine/Cosine Time oscilan −1..1 (animación cíclica); Delta para efectos frame-independent |
| **Sample Texture 2D** | In: **Texture** (Texture 2D), **UV** (Vector 2), **Sampler** (Sampler State); +**LOD**/**Bias**/**DDX**/**DDY** (Float, solo visibles según **Mip Sampling Mode**) → Out: **RGBA** (V4), **R/G/B/A** (Float) | Muestrea una textura. Dropdown **Type**: Default o **Normal**; con Normal, **Space** = Tangent (mallas deformables) u Object (estáticas, usa canal blue, UNorm en Linear) |

### Math / mezcla

| Nodo | Puertos | Qué hace |
|---|---|---|
| **Multiply** | A, B → Out | Producto (tint, atenuar, escalar UVs) |
| **Add** | A, B → Out | Suma (offset, sumar máscaras) |
| **Lerp** | **A**, **B**, **T** → Out | Interpolación lineal `A + T*(B−A)`. T=0→A, T=1→B. Base del hit flash (Lerp a blanco por propiedad) |
| **Step** | **Edge**, **In** → Out | Umbral duro: `Out = In >= Edge ? 1 : 0`. Bordes nítidos |
| **Smoothstep** | **Edge1**, **Edge2**, **In** → Out | Interpolación Hermite suave 0..1 entre Edge1 y Edge2. Bordes con anti-alias / gradiente controlado |
| **Fresnel Effect** | **Normal** (default World Space Normal), **View Dir** (default World Space View Dir), **Power** → **Out** (Float 0..1) | Rim light: 0 de frente, 1 en ángulos rasantes. Sube **Power** = borde más fino. Base de escudos/hologramas/rim |

### Noise / procedural

| Nodo | Puertos | Patrón |
|---|---|---|
| **Simple Noise** | **UV** (V2), **Scale** (Float, default **500**) → **Out** (Float 0..1) | Value noise pseudo-aleatorio. Hash: Deterministic (default) / Legacy Sine |
| **Gradient Noise** | **UV**, **Scale** → **Out** (0..1) | Perlin/gradient noise, más orgánico que Simple. Nota doc: algo más caro que muestrear una textura |
| **Voronoi** | **UV**, **Angle Offset**, **Cell Density** → **Out** (Float), **Cells** (Float) | Worley/celular — piedra, grietas, escamas, agua. Cell Density = cantidad de celdas |

> **Costo:** el noise procedural (sobre todo Gradient/Voronoi) es más caro que samplear una textura de ruido. Para móvil o muchos pixeles, hornear el patrón a textura suele ganar [ver: optimizacion-vfx].

## Espacios de coordenadas

El dropdown **Space** de nodos como Position / Normal Vector / View Direction decide el marco de referencia. Elegir mal = el efecto se rompe al mover/rotar el objeto o la cámara.

| Espacio | Qué devuelve | Cuándo usarlo |
|---|---|---|
| **Object** | Relativo al origen del objeto | Efectos que deben "pegarse" al modelo aunque se mueva (dissolve por altura local, gradientes ligados a la malla) |
| **World** | Posición en el mundo, en metros | Efectos ligados al entorno (agua por altura global, tri-planar, patrones que no siguen al objeto). En HDRP es relativo a la cámara |
| **Absolute World** | Mundo sin ajuste de cámara | Igual que World pero coordenada de mundo sin modificar (útil en HDRP camera-relative) |
| **View** | Relativo a la cámara, en metros | Efectos que dependen de la vista |
| **Tangent** | Relativo a la tangente de la superficie | Normal maps, detalle sobre la superficie |

- **Normal maps** viven en **Tangent Space** (por eso `Sample Texture 2D` Type=Normal usa Space Tangent para mallas deformables). Object Space se usa para normal maps de objetos estáticos.
- Regla práctica: si el efecto debe seguir al objeto → Object; si debe quedarse fijo en el mundo mientras el objeto pasa → World.

## Sub Graphs: reutilizar lógica de nodos

Un **Sub Graph** es un grafo que incluyes dentro de otros — como una función reutilizable en programación. Asset con extensión **`.shadersubgraph`**.

- **Inputs** = las properties del Blackboard del Sub Graph.
- **Outputs** = salen de un **Output Node** (el Sub Graph NO tiene Master Stack).
- Al usarlo en otro grafo, Unity crea un **Sub Graph Node** que muestra esos inputs/outputs como un solo nodo.
- Uso típico: encapsular un cálculo repetido (ej. un patrón de scroll de UV, una función de dissolve, un remap) y llamarlo en varios shaders. Cambiar el Sub Graph actualiza todos los que lo usan.
- Buena práctica: armar una librería de Sub Graphs propios (`Assets/Shaders/SubGraphs/`) para no re-cablear lo mismo. [ver: recetas-shaders]

## Custom Function node: meter HLSL

Cuando el nodo no existe o necesitas control fino, el **Custom Function node** inyecta HLSL en el grafo. Dos modos:

| Modo | Cómo | Cuándo |
|---|---|---|
| **String** | Escribes el cuerpo HLSL en el nodo; Unity genera firma/llaves/indentado. Token `$precision` se sustituye por half/float según precisión del nodo | Snippets cortos |
| **File** | Referencias un `.hlsl` externo; NO genera la función, solo inyecta un `#include` y llama a la función | Código reutilizable, funciones largas, versionado |

Reglas exactas (confirmadas):
- **Puertos** se definen en el **Custom Port Menu**; los nombres de puerto = nombres de las variables/argumentos en el código.
- **Sufijos de precisión en el nombre de la función**: `_float` (precisión completa) o `_half` (ahorro). Los argumentos deben cuadrar con los inputs definidos.
- Archivo `.hlsl`: debe llevar **`#ifndef` / `#define`** (include guards) para evitar carga duplicada.
- **Texturas** (v10.3+): usar los structs `UnityTexture2D` y `UnitySamplerState` en vez de tipos crudos (consistencia cross-plataforma).
- ⚠️ **Preview**: el preview del nodo NO accede a las librerías del render pipeline → usar fallback con `#ifdef SHADERGRAPH_PREVIEW`.
- ⚠️ Uniforms declaradas dentro se vuelven **globales** (se setean con `Shader.SetGlobalMatrix()` etc., no por material).

## Shader Graph vs HLSL a mano

| Dimensión | Shader Graph | HLSL escrito a mano |
|---|---|---|
| Iteración / preview | ✅ Visual, en vivo, por nodo | ❌ Editar-guardar-recompilar |
| Compatibilidad SRP Batcher | ✅ Genera el CBUFFER `UnityPerMaterial` solo [ver: unity/rendering-urp] | Hay que escribirlo correcto a mano |
| Portabilidad entre pipelines | ✅ Cambiar target re-genera | Reescribir includes/macros por pipeline |
| Control de bajo nivel | ❌ Limitado a lo que exponen los nodos | ✅ Total (branching complejo, loops, compute, tessellation avanzada) |
| Legibilidad de lógica compleja | ❌ "Spaghetti de nodos" a cierta escala | ✅ Texto diffeable, comentable |
| Coste por pixel | ⚠️ Cada nodo suma; fácil inflar sin darse cuenta | Control fino de cada instrucción |

- **Regla:** Shader Graph para el 90% de shaders de juego (superficie, VFX, estilizado). HLSL a mano (o Custom Function dentro del grafo) para algoritmos que los nodos no cubren o donde el coste importa mucho.
- **Híbrido recomendado:** mantener el grafo y meter el HLSL puntual con Custom Function (File mode) — te quedas con SRP Batcher y preview, y bajas a HLSL solo donde hace falta.
- Ver el código generado: botón **View Generated Shader** (menú del grafo) para auditar coste real.

## Conectar shader → material → código

1. El grafo se guarda como `.shadergraph` → se crea un **Material** que lo usa como shader.
2. Las **properties expuestas** aparecen en el Material Inspector.
3. Por código se setean por **Reference** (no display name):

```csharp
// Ej.: hit flash — subir _FlashAmount y bajarlo con el tiempo
material.SetFloat("_FlashAmount", 1f);   // Reference del Blackboard
material.SetColor("_BaseColor", Color.red);
material.SetTexture("_BaseMap", tex);
```

### Variar por instancia sin instanciar material

Cambiar `renderer.material` **clona** el material (nueva instancia en memoria, rompe batching por material). Para variar por instancia:

- **MaterialPropertyBlock**: setea overrides por-renderer SIN clonar el material. ⚠️ Pero **rompe la compatibilidad con SRP Batcher** para ese renderer (lo dice la doc de URP) [ver: unity/rendering-urp].
- **Alternativas compatibles con SRP Batcher:** materiales distintos del **mismo shader** (baratos con SRP Batcher — "pocos shaders, muchos materiales"), o **GPU instancing** con propiedades per-instance.
- Trade-off real: MaterialPropertyBlock evita clonar y es ideal para GPU instancing manual, pero sacrifica SRP Batcher. Elegir según qué domina el frame. El detalle de batching/instancing y cómo medirlo está en [ver: unity/rendimiento-unity].

```csharp
// MaterialPropertyBlock: color por-instancia sin clonar material
var mpb = new MaterialPropertyBlock();
renderer.GetPropertyBlock(mpb);
mpb.SetColor("_BaseColor", nuevoColor);
renderer.SetPropertyBlock(mpb);
```

## URP vs Built-in y estado en Unity 6

- Shader Graph es **la forma estándar** de escribir shaders en URP/HDRP en Unity 6. Built-in usa ShaderLab/HLSL a mano (Shader Graph existe para Built-in pero es residual).
- Un grafo con target URP **no** sirve en Built-in y viceversa sin re-targetear; los shaders no son compatibles entre pipelines [ver: unity/rendering-urp].
- Unity 6 (Shader Graph 17.x): Render Graph compila el frame; para **custom render passes** en HLSL cambió la API (`RecordRenderGraph`), pero eso es del pipeline, no del grafo de superficie [ver: unity/rendering-urp].
- **VFX Graph** puede consumir Shader Graphs como shaders de sus partículas (output) — la lógica de nodos se comparte [ver: particulas-vfx-graph].

## Reglas practicas

1. Crear el grafo con el **sub-target correcto** desde el inicio: URP Lit (3D con luz), Unlit (VFX/flat), Sprite Lit (2D con Light 2D), Sprite Unlit (2D sin luz). Re-targetear después es fricción.
2. Setear propiedades por código SIEMPRE con la **Reference** del Blackboard, nunca el display name.
3. Marcar **Main Color** / **Main Texture** en las properties base para que se llamen `_BaseColor` / `_BaseMap` (compatibilidad con APIs de URP).
4. Mantener el grafo **chico**: cada nodo suma coste por pixel. Auditar con **View Generated Shader** si dudas del costo.
5. Encapsular lógica repetida en **Sub Graphs** (`.shadersubgraph`) y reutilizar — no re-cablear lo mismo en 5 shaders.
6. Elegir el **espacio** consciente: Object si el efecto sigue al objeto, World si se queda fijo en el mundo. Normal maps = Tangent Space.
7. Noise procedural solo cuando compense; para móvil/muchos pixeles, hornear a textura de ruido [ver: optimizacion-vfx].
8. **Emission > 1** con HDR ON para que el Bloom haga glow selectivo (proyectiles, neones) [ver: unity/rendering-urp].
9. Alpha Clipping en vez de Alpha blend cuando puedas (evita overdraw y orden de transparencias) [ver: optimizacion-vfx].
10. Keywords que se eligen por material en el inspector → **Shader Feature**; que se alternan por código en runtime → **Multi Compile** (o garantizar que la variante no se strippee).
11. HLSL puntual: **Custom Function** en **File mode** con include guards y sufijos `_float`/`_half`; fallback `#ifdef SHADERGRAPH_PREVIEW`.
12. Variar por instancia: materiales distintos del mismo shader (barato con SRP Batcher) o GPU instancing; usar **MaterialPropertyBlock** solo sabiendo que rompe SRP Batcher [ver: unity/rendimiento-unity].
13. Nunca `renderer.material = x` en loop caliente (clona material cada vez); cachear o usar MaterialPropertyBlock.
14. Deformación de vértices (wind, wave) va en el contexto **Vertex** (Position block), no en Fragment.
15. Verificar el shader en el **device real más débil** del target: el preview del editor no representa el coste en GPU móvil.
16. Un grafo por look; muchos **materiales** del mismo grafo para variantes (colores, intensidades) — pocos shaders, muchos materiales [ver: unity/rendering-urp].

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Setear por código con el display name y "no pasa nada" | Usar la **Reference** exacta del Blackboard (`material.SetFloat("_MiProp", …)`) |
| Sprite 2D no reacciona a Light 2D | Sub-target equivocado: usar **Sprite Lit**, no Unlit; y 2D Renderer asignado [ver: unity/rendering-urp] |
| Bloom no glow-ea aunque hay emisión | Emission ≤ 1 o HDR OFF: subir Emission > 1 y HDR ON [ver: unity/rendering-urp] |
| Efecto se rompe al mover/rotar el objeto | Espacio mal elegido: World cuando debía ser Object (o al revés) |
| Normal map se ve plano/roto | `Sample Texture 2D` Type debe ser **Normal**, Space Tangent (deformable) u Object (estático); textura importada como Normal Map |
| Shader rosado en runtime al activar una variante | Keyword en **Shader Feature** cuya variante fue strippeada; pasar a **Multi Compile** o forzar la variante |
| Build enorme / tarda mucho | Demasiados keywords en **Multi Compile**: revisar cuáles pueden ser Shader Feature |
| FPS cae con noise procedural | Gradient/Voronoi caros por pixel; hornear a textura o usar Simple Noise / menos pixeles [ver: optimizacion-vfx] |
| Custom Function funciona en preview pero rompe en build (o viceversa) | Falta fallback `#ifdef SHADERGRAPH_PREVIEW`; el preview no accede a las libs del pipeline |
| Custom Function `.hlsl` da "redefinición" | Faltan include guards `#ifndef`/`#define`; y nombre de función sin sufijo `_float`/`_half` |
| Objeto pierde SRP Batcher sin saber por qué | Un **MaterialPropertyBlock** en ese renderer lo desactiva; usar materiales/instancing si quieres batchear [ver: unity/rendimiento-unity] |
| `renderer.material.SetColor(...)` clona material y crece la memoria | Usar `sharedMaterial` (afecta a todos) o **MaterialPropertyBlock** (por instancia) según intención |
| Grafo lento sin razón aparente | Nodos de más / noise / muchas texturas: abrir **View Generated Shader** y contar instrucciones |
| Grafo URP no compila al abrir proyecto Built-in (o al revés) | Shaders no son cross-pipeline; re-targetear en Graph Settings [ver: unity/rendering-urp] |
| Deformación de vértices puesta en Fragment | Va en el contexto **Vertex** (Position/Normal/Tangent blocks) |

## Fuentes

- Master Stack — Shader Graph 17.0 manual (docs.unity3d.com/Packages/com.unity.shadergraph@17.0) — contextos Vertex/Fragment, qué es un Block, dependencia de Graph Settings.
- Built-In Blocks — Shader Graph 17.0 manual — nombres y tipos exactos de blocks Vertex (Position/Normal/Tangent/Color) y Fragment (Base Color, Normal Tangent/Object/World, Emission, Metallic, Specular, Smoothness, Ambient Occlusion, Alpha, Alpha Clip Threshold).
- Graph Target — Shader Graph 17.0 manual — los 3 targets (URP/HDRP/Built-in) y que un grafo puede tener varios.
- Blackboard — Shader Graph 17.0 manual — properties/keywords/categories, campo Reference, toggle Exposed, aparición en Material Inspector.
- Property Types — Shader Graph 17.0 manual (re-verificado con fetch directo en esta sesión: la lista es cerrada, Gradient y Sampler State confirmados AUSENTES de Property Types) — lista exacta de tipos (Float con Slider/Integer, Vector 2/3/4, Color sRGB/HDR + Main Color, Boolean ToggleUI, Texture 2D + Main Texture, Texture 2D Array/3D/Cubemap, Virtual Texture, Matrix 2/3/4 no visibles en inspector).
- Keywords / Keywords concepts — Shader Graph 17.0 manual — Boolean/Enum/Built-in; Definition **Shader Feature** (strippea, default) vs **Multi Compile** (compila todas, build más grande).
- Sub Graph — Shader Graph 17.0 manual — `.shadersubgraph`, inputs = properties del Blackboard, Output Node (sin Master Stack), Sub Graph Node.
- Custom Function Node — Shader Graph 17.0 manual — modos String/File, `$precision`, sufijos `_float`/`_half`, include guards, `UnityTexture2D`/`UnitySamplerState`, fallback `SHADERGRAPH_PREVIEW`, uniforms globales.
- Sample Texture 2D Node — Shader Graph 17.0 manual (re-verificado con fetch directo en esta sesión) — puertos Texture/UV/Sampler (+LOD/Bias/DDX/DDY según Mip Sampling Mode) → RGBA/R/G/B/A, Type Default/Normal, Space Tangent/Object (detalle canal blue/UNorm Linear para Object).
- Step Node — Shader Graph 17.0 manual (verificado con fetch directo en esta sesión, no estaba confirmado en la investigación original) — puertos Edge/In → Out, comparación por-componente.
- Time Node — Shader Graph 17.0 manual — outputs Time, Sine Time, Cosine Time, Delta Time, Smooth Delta.
- UV Node — Shader Graph 17.0 manual — Channel UV0–UV7, Out Vector 4.
- Lerp Node — Shader Graph 17.0 manual — A/B/T → Out, `A + T*(B−A)`.
- Smoothstep Node — Shader Graph 17.0 manual — Edge1/Edge2/In → Out, interpolación Hermite 0..1.
- Fresnel Effect Node — Shader Graph 17.0 manual — Normal (World default), View Dir (World default), Power → Out 0..1.
- Simple Noise Node — Shader Graph 17.0 manual — UV/Scale (default 500) → Out 0..1, value noise, hash Deterministic/Legacy Sine.
- Gradient Noise Node — Shader Graph 17.0 manual — UV/Scale → Out 0..1, Perlin; nota de coste vs textura.
- Voronoi Node — Shader Graph 17.0 manual — UV/Angle Offset/Cell Density → Out/Cells, Worley noise, Deterministic desde 2021.2.
- Position Node — Shader Graph 17.0 manual — Space Object/View/World/Tangent/Absolute World y qué devuelve cada uno.
