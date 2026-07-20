# PBR: teoría práctica para texturizado de juego

> **Cuando cargar este archivo:** al decidir QUÉ valores meter en cada mapa de un material PBR (base color, metallic, roughness, normal, height, AO, emission), al escribir la spec de textura para Unity, al empacar canales (mask map), o al diagnosticar un material que "se ve raro" en el engine (plateado/lavado, normal invertido, albedo con sombras cocidas). Es la capa de TEORÍA→VALORES. El bake de esos mapas vive en [ver: baking] y en [ver: modelado/high-to-low]; el preview dentro de Blender en [ver: blender/materiales-preview]; los slots exactos de import en [ver: pipeline/arte-a-unity].

Versión de referencia: **Blender 5.2 LTS · Unity 6 / URP (manual 6000.2) · Substance Painter 2026**. Datos con dependencia de versión o de fuente van marcados.

## 1. Qué es PBR y por qué es el estándar

PBR (Physically Based Rendering) es un shading model que aproxima cómo la luz interactúa **de verdad** con una superficie, en vez de "pintar" el resultado a ojo. Un modelo es físicamente basado cuando cumple tres cosas (LearnOpenGL, *PBR/Theory*):

1. **Microfacet model** — la superficie es un conjunto estadístico de micro-espejos; la `roughness` describe qué tan alineados están (liso = reflejo nítido, rugoso = reflejo disperso).
2. **Energy conservation** — la luz que sale nunca supera la que entra. Difusa + especular son mutuamente excluyentes: `kD = 1 − kS`. Esto es lo que impide que un material "brille de más".
3. **BRDF físico** — Cook-Torrance es el estándar de industria.

**Por qué ganó, en términos de producción:** un material autorizado con datos físicos (reflectividad real, roughness real) se ve **coherente bajo CUALQUIER luz** — mediodía, interior, atardecer, el nivel oscuro. El artista deja de re-pintar highlights para cada escena; el mismo set de texturas funciona en todo el juego. Eso es exactamente lo que un pipeline de assets necesita: el look se decide una vez y el engine lo resuelve con su luz [ver: pipeline/arte-a-unity §10]. El contraejemplo (materiales "hechos a ojo") se rompe apenas cambia la iluminación.

**Base física mínima que hay que tener en la cabeza** (LearnOpenGL; physicallybased.info):

| Concepto | Qué significa para el texturizado |
|---|---|
| **Dieléctrico** (no-metal: plástico, madera, piel, roca) | Refleja especular **~4%** (F0 ≈ 0.04) sin tinte; el resto de la luz entra, rebota y sale como **color difuso** → el albedo ES ese color |
| **Conductor** (metal) | **Absorbe toda la luz refractada → NO tiene difuso.** Su reflejo especular es fuerte (F0 ≈ 0.5–1.0) y **tiene color** (oro, cobre). En metalness, ese color de reflejo se guarda en el **base color** |
| **Fresnel** | Todo se vuelve más reflectivo en ángulos rasantes; el shader lo hace solo. No se pinta |
| **Roughness / microsurface** | Estadística de los micro-espejos. NO cambia cuánta luz refleja, cambia si el reflejo es **nítido o difuso** |

La consecuencia práctica de "los metales no tienen difuso" es toda la lógica del workflow metallic (§2).

## 2. Los dos workflows: Metallic/Roughness vs Specular/Glossiness

Dos formas de codificar lo mismo. Ambas son PBR válidas; se diferencian en **cómo** guardan la reflectividad.

| | **Metallic / Roughness** (el de juegos) | **Specular / Glossiness** |
|---|---|---|
| Mapa de color | **Base Color** = color difuso (dieléctricos) **o** color de reflejo (metales), en el mismo mapa | **Diffuse** (color difuso) + **Specular** (color de reflejo) en DOS mapas RGB |
| Mapa de metal | **Metallic** (1 canal, ~binario) decide si el base color es difuso o reflejo | No existe: el specular map ya lleva la reflectividad |
| Nitidez | **Roughness** (1 canal; 0 = espejo, 1 = mate) | **Glossiness** (1 canal; invertido: 1 = espejo) |
| F0 de dieléctricos | **Fijo ~4%** por el shader (no lo controla el artista) | Editable a mano en el specular map → fácil meter valores no-físicos |
| Peso en memoria | Menos canales (base + metallic + roughness) | Un mapa RGB extra (specular a color) |
| Riesgo típico | Bordes blancos/oscuros en el borde metal↔no-metal si el metallic no es limpio | "Energy conservation" violada a mano; valores de F0 inventados |

**Cuál usa Unity URP y por qué:** el shader **URP Lit** arranca en **Workflow Mode = Metallic** por defecto (manual 6000.2). Es el estándar de juegos porque: menos texturas (un canal de metallic + un canal de roughness en vez de un mapa specular RGB), más difícil equivocarse con la física (el F0 dieléctrico lo fija el shader), y es lo que exportan por defecto Substance, Blender y glTF. URP Lit **también** ofrece Workflow Mode = Specular (propiedad *Specular Map* = "Sets the color of reflections"), pero para assets nuevos: **metallic** salvo razón fuerte. Todo lo de aquí en adelante asume metallic/roughness.

## 3. Los mapas, uno a uno

El set de un material de juego, con qué guarda cada uno y el error que lo arruina. El **cómo se bakea** cada mapa está en [ver: baking] y [ver: modelado/high-to-low §6]; aquí va el **qué valor** debe llevar y **cómo lo lee Unity**.

| Mapa | Datos | Color space | Slot URP Lit | Regla de oro |
|---|---|---|---|---|
| **Base Color / Albedo** | Color difuso (dieléctrico) o color de reflejo (metal) | **sRGB** | Base Map (RGB) | CERO luz cocida (§4) |
| **Metallic** | ¿Es metal? | **Lineal** | Metallic Map | 0 o 1, casi binario (§3.2) |
| **Roughness → Smoothness** | Microsuperficie | **Lineal** | Smoothness (alpha) | ⚠️ Unity invierte: smoothness = 1 − roughness (§3.3) |
| **Normal** | Dirección de superficie por píxel | **Lineal** | Normal Map | ⚠️ OpenGL (Y+) para Unity (§5) |
| **Height** | Altura por píxel | **Lineal** | Height Map (parallax) | Solo si el material lo paga |
| **AO** | Oclusión de luz ambiente | **Lineal** | Occlusion Map | Separado del albedo, nunca dentro |
| **Emission** | Luz emitida | **sRGB / HDR** | Emission Map | Solo si el asset emite |

sRGB vs lineal es CRÍTICO en el import (§7): meter un roughness como sRGB corrompe los valores.

### 3.1 Base Color / Albedo — el que NO puede llevar luz

El albedo guarda **solo el color propio del material**, iluminado de forma perfectamente plana. Lo que jamás va cocido dentro (polycount; LearnOpenGL; base de high-to-low §6):

- **Sombras, AO, cavity** → van en el AO map, que ocluye solo luz ambiente. AO dentro del albedo = modelo sucio bajo toda luz.
- **Highlights / brillos especulares** → los calcula el shader con roughness + Fresnel.
- **Reflejos direccionales** → los pone el engine.

Regla mental: si tapas los ojos y giras el asset bajo una luz nueva, el albedo **no debería tener ninguna información que dependa de dónde estaba la luz**. Rangos válidos en §4.

Para metales, el base color deja de ser "difuso" y pasa a ser el **color de reflectancia** del metal (oro, cobre…). El shader lo usa como F0 tintado (`F0 = mix(0.04, baseColor, metalness)`, LearnOpenGL).

### 3.2 Metallic — casi binario

El canal metallic es el interruptor que le dice al shader si el base color es difuso (0) o reflejo (1). En la práctica es **0 o 1** — los grises intermedios son físicamente raros porque un material o es conductor o no lo es (physicallybased.info lista todos los metales con metallic = 1). Valores intermedios legítimos, solo para:

- **Antialiasing del borde** metal↔no-metal (un píxel a medias en la frontera).
- **Capas finas encima del metal**: óxido, pintura desconchada, polvo, huellas — y aun así suele salir mejor **mezclando dos materiales** que pintando un metallic gris.

Pitfall clásico: pintar el metallic a "0.5 porque el metal se ve algo sucio". El resultado es un material que no es ni metal ni dieléctrico y se ve mal bajo toda luz. Metal sucio = metallic 1 + roughness alta + suciedad en el albedo/roughness, no metallic gris.

### 3.3 Roughness / Smoothness — el que más vende el material

El roughness es el mapa que hace que un material se **lea** como lo que es: el mismo base color gris con roughness baja es cromo pulido y con roughness alta es plomo mate. Variación en el roughness (rayones brillantes sobre metal opaco, huellas, gotas, desgaste) es lo que separa un material plano de uno creíble. Es, de lejos, donde más rinde el tiempo de texturizado.

⚠️ **Unity trabaja en SMOOTHNESS, no en roughness.** `smoothness = 1 − roughness`. URP Lit tiene la propiedad **Smoothness** con **Smoothness Source = Metallic Alpha** (default) o **Albedo Alpha** (manual 6000.2). Es decir: Unity **no tiene slot propio de roughness** — lo lee del **canal alpha** del Metallic Map (o del Base Map), ya invertido a smoothness. Substance/Blender/glTF exportan **roughness**; hay que invertirlo. Esto se cubre en §6 (empaque) y §7 (import). Es la causa #1 de "el metal se ve plateado/lavado" [ver: pipeline/arte-a-unity §7] [ver: blender/materiales-preview §10].

### 3.4 Normal — tangent space, y el verde crítico para Unity

El normal map guarda la **dirección** de la superficie por píxel (no profundidad, no silueta). Tangent space, MikkTSpace, handedness y todo el detalle técnico están en [ver: modelado/high-to-low §2]. Lo que importa para Unity está en §5: **Unity espera OpenGL (Y+)**, y ahí está el bug más común del pipeline.

Import: Texture Type = **Normal map**, color space **lineal** (el tipo Normal map lo maneja solo). Nunca importar un normal como textura de color sRGB.

### 3.5 Height / Displacement, AO, Emission — breves (detalle en high-to-low)

- **Height** (grises, lineal) → URP Lit lo usa como **Height Map** (parallax): "Adds the appearance of large bumps and protrusions". Solo donde el material lo pague (piedra, rejilla). Displacement real (mueve geometría) casi nunca en runtime. Comparativa normal vs height vs displacement en [ver: modelado/high-to-low §8].
- **AO** (grises, lineal) → URP Lit **Occlusion Map**, "simulates shadows in corners and crevices". En PBR va SEPARADO del albedo y ocluye **solo luz ambiente** (base de high-to-low §6). ⚠️ Unity samplea la oclusión del **canal verde (G)** de la textura de occlusion.
- **Emission** (RGB, admite **HDR**) → URP Lit **Emission Map**; valores >1 alimentan el Bloom [ver: pipeline/arte-a-unity §7] [ver: unity/rendering-urp]. Solo si el asset emite luz.

## 4. Valores de referencia reales

Todos en **sRGB 0–255** (como los ves en el color picker). El engine los convierte a lineal internamente [§7].

### Dieléctricos (metallic = 0) — base color medido (physicallybased.info)

| Material | Base color sRGB | IOR |
|---|---|---|
| Carbón / charcoal | 5, 5, 5 | 1.50 |
| Pasto (grass) | 27, 34, 10 | 1.50 |
| Arena (sand) | 112, 98, 59 | 1.50 |
| Concreto | 130, 130, 130 | 1.50 |
| Piel clara (tipo I) | 216, 163, 141 | 1.40 |
| Piel oscura (tipo VI) | 23, 13, 5 | 1.40 |
| Nieve fresca | 217, 217, 217 | 1.31 |
| Agua | 247, 254, 254 | 1.33 |

### Metales (metallic = 1) — el base color ES el color de reflectancia (physicallybased.info)

| Metal | Base color sRGB |
|---|---|
| Oro | 270, 197, 78 * |
| Plata | 252, 251, 248 |
| Aluminio | 234, 235, 236 |
| Cobre | 238, 159, 133 |
| Cromo | 167, 175, 179 |
| Hierro | 135, 131, 126 |
| Titanio | 112, 102, 92 |

\* Valores medidos de reflectancia espectral; los metales más brillantes pueden pasar de 255 en un canal (oro rojo = 270). Al autorizar en 8-bit se **clampa a 255** — por eso el oro de juego suele quedar ~(255, 226, 155). El dato crudo se conserva para pipelines HDR.

### Qué NO poner en el albedo, y el rango seguro

- **Nada de 0,0,0 puro ni 255,255,255 puro.** No existe un dieléctrico que absorba el 100% ni que refleje el 100%. Aun el carbón está en ~5 y la nieve en ~217. Regla de autoría de juego (derivada de estos extremos): mantener el albedo dieléctrico **aprox. entre 30 y 240 sRGB**, y solo salirse para materiales genuinamente extremos (carbón, nieve). Un albedo demasiado oscuro se "traga" toda la luz y se ve muerto; demasiado claro rebota de más y rompe el look.
- **Cero luz horneada** (sombras, AO, highlights, reflejos) — §3.1.
- **Metales: el difuso va a negro conceptualmente** — no hay color difuso; todo el color del metal vive en el reflejo (base color con metallic = 1).

## 5. Normal map en Unity: OpenGL (Y+) vs DirectX (Y−) — el verde invertido

**El bug de textura más frecuente que llega al engine.** Un tangent-space normal map codifica la dirección Y (arriba/abajo del relieve) en el **canal verde**; hay dos convenciones opuestas de signo (base de high-to-low §2, tabla de handedness — fuente polycount):

| Convención | Verde | Software que la usa |
|---|---|---|
| **OpenGL** (Y+) | Y hacia arriba | **Blender, Maya, Toolbag, Unity** |
| **DirectX** (Y−) | Y hacia abajo | 3ds Max, Source, CryEngine, **Unreal** |

**Unity espera OpenGL (Y+).** Consecuencias operativas:

- **Normal bakeado en Blender → Unity: directo, sin flip.** Blender es OpenGL, Unity es OpenGL. Coinciden.
- **Normal de Substance Painter (default histórico = DirectX / Y−) → Unity: INVERTIDO.** Síntoma: el relieve se ve "hundido" donde debería sobresalir, la luz responde al revés en el eje vertical, los biseles se ven cóncavos. Se nota al mover la luz.

**Cómo se arregla (dos vías, elegir UNA):**

1. **En la herramienta de texturizado:** exportar el normal en formato **OpenGL** (en Substance Painter, seleccionar el output/preset con normal OpenGL). Es lo preferible: la textura queda correcta en disco.
2. **En Unity, al import:** Texture Type = Normal map → activar **"Flip Green Channel"**. La doc de Unity (manual 6000.2) lo describe así: *"Indicates whether to invert the green (Y) channel values of a normal map. This can be useful if the normal map uses a different convention to what Unity expects."* — no nombra DirectX/OpenGL explícitamente, pero esa "diferente convención" es exactamente esta: el verde invertido de DirectX. Útil cuando la textura ya vino en DirectX y no puedes re-exportar.

⚠️ No hacer las dos a la vez (doble flip = vuelve a estar mal). Y decidir la convención **una vez para todo el proyecto** — mezclar normales OpenGL y DirectX en el mismo juego garantiza que la mitad se vea invertida. Verificar SIEMPRE en el engine con luz real, moviendo la luz sobre un bisel conocido [ver: pipeline/arte-a-unity §10].

## 6. Canales empaquetados (mask maps): cómo lo espera Unity

Empacar varios mapas de 1 canal en los RGBA de una sola textura ahorra memoria, samples y draw state. Pero **URP y HDRP empacan distinto** — este es el punto donde más gente entrega la textura mal.

### URP Lit — Metallic Smoothness (el empaque de URP)

URP Lit **no** usa un mask map de 4 canales. Usa (manual 6000.2):

| Textura | Canales | Contenido |
|---|---|---|
| **Metallic Map** | RGB | Metallic (grises) |
| ↳ mismo archivo | **Alpha** | **Smoothness** (= 1 − roughness) ← Smoothness Source: *Metallic Alpha* |
| **Occlusion Map** | textura aparte (Unity lee canal **G**) | AO |
| **Base Map** | RGB + (A opcional) | Albedo (+ smoothness si Source = *Albedo Alpha*) |

O sea, para URP el artista entrega un **"MetallicSmoothness"**: RGB = metallic, **A = smoothness ya invertido**. La AO va como textura separada. Este es exactamente el preset **"Unity URP (Metallic Smoothness)"** que se le pide a Substance para que la conversión roughness→smoothness y el empaque en alpha salgan hechos [ver: pipeline/arte-a-unity §7] [ver: substance-y-alternativas].

### HDRP Lit — Mask Map de 4 canales

HDRP sí usa un único **Mask Map** RGBA (manual HDRP): default esperado de cada canal = 0.5.

| Canal | Contenido |
|---|---|
| **R** | Metallic |
| **G** | Ambient Occlusion |
| **B** | Detail Mask |
| **A** | Smoothness |

⚠️ **No es intercambiable con el de URP.** El orden RGBA de HDRP (metallic-AO-detail-smoothness) es distinto al MetallicSmoothness de URP (metallic en RGB, smoothness en A, AO aparte). Empacar para el pipeline equivocado = todo desplazado. Confirmar SIEMPRE qué render pipeline usa el proyecto antes de empacar.

Regla común a ambos: los canales empacados son **datos lineales** — sRGB OFF en el import (§7). Y el smoothness va **ya invertido** desde roughness antes de empacar.

## 7. Cómo Unity URP interpreta cada mapa (slots + import)

Resumen operativo; los import settings completos y su automatización (Presets / AssetPostprocessor) están en [ver: pipeline/arte-a-unity §7] y [ver: unity/assets-pipeline-git] [ver: texturas-a-unity].

| Mapa | Slot URP Lit | Texture Type | **sRGB (Color Texture)** |
|---|---|---|---|
| Albedo | Base Map | Default | **ON** |
| Metallic (+smoothness en A) | Metallic Map | Default | **OFF** |
| Normal | Normal Map | **Normal map** | (lo maneja el tipo) |
| Height | Height Map | Default | **OFF** |
| AO | Occlusion Map | Default | **OFF** |
| Emission | Emission Map | Default | **ON** (HDR) |

**El check sRGB es load-bearing** (Unity manual, Default texture type): *"Enable for non-HDR color textures such as albedo… Disable if the texture stores information that you need the exact value for"* — o sea **ON solo en color** (albedo, emission), **OFF en todo mapa de datos** (metallic, roughness/smoothness, occlusion, height, mask maps). Un roughness importado con sRGB ON queda con valores corridos por la curva gamma → material mate donde debía ser brillante. El normal usa Texture Type = Normal map (no toca el check sRGB a mano).

Otros checks: potencia de 2 (512/1024/2048), texel density consistente entre assets [ver: pipeline/arte-a-unity §7], compresión ASTC en móvil, Read/Write OFF. 1 material por prop como objetivo.

## 8. Automatización (bpy) — lo específico de PBR

El bake y el export FBX/textura viven en [ver: baking] y [ver: pipeline/arte-a-unity]; aquí solo lo propio de armar/validar el **material PBR** en Blender. El acceso al Principled BSDF (modelo OpenPBR en 5.x) está verificado en [ver: blender/materiales-preview §6].

**Cablear un material PBR completo desde texturas** (para previsualizar en EEVEE antes de exportar; el color space por mapa es lo crítico):

```python
import bpy

def pbr_material(nombre, base, metal, rough, normal):
    m = bpy.data.materials.get(nombre) or bpy.data.materials.new(nombre)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]

    def tex(path, colorspace):
        n = nt.nodes.new("ShaderNodeTexImage")
        n.image = bpy.data.images.load(path, check_existing=True)
        n.image.colorspace_settings.name = colorspace  # datos = lineal
        return n

    nt.links.new(tex(base,  'sRGB').outputs["Color"],      bsdf.inputs["Base Color"])
    nt.links.new(tex(metal, 'Non-Color').outputs["Color"], bsdf.inputs["Metallic"])
    nt.links.new(tex(rough, 'Non-Color').outputs["Color"], bsdf.inputs["Roughness"])
    nmap = nt.nodes.new("ShaderNodeNormalMap")               # tangent space
    nt.links.new(tex(normal, 'Non-Color').outputs["Color"], nmap.inputs["Color"])
    nt.links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
    return m
```

Notas: `colorspace_settings.name = 'Non-Color'` es lo que evita que Blender aplique gamma a metallic/roughness/normal (equivalente al sRGB OFF de Unity). El nodo **Normal Map** es tangent space por defecto — es el que consume un normal OpenGL como el que Unity espera. Esto es **preview**, no el look final: el veredicto es Unity [ver: blender/materiales-preview §10].

**Empacar un MetallicSmoothness para URP** (RGB = metallic, A = smoothness = 1 − roughness) con numpy sobre los píxeles de las imágenes:

```python
import bpy, numpy as np

def pack_metallic_smoothness(metal_img, rough_img, out_name):
    w, h = metal_img.size
    m = np.asarray(metal_img.pixels[:]).reshape(-1, 4)   # RGBA lineal
    r = np.asarray(rough_img.pixels[:]).reshape(-1, 4)
    out = bpy.data.images.new(out_name, w, h, alpha=True)
    out.colorspace_settings.name = 'Non-Color'
    p = np.zeros_like(m)
    p[:, 0:3] = m[:, 0:3]          # metallic en RGB
    p[:, 3]   = 1.0 - r[:, 0]      # smoothness en alpha (invierte roughness)
    out.pixels = p.ravel()
    return out
```

(Verifica que ambas imágenes sean del mismo tamaño y estén cargadas como `Non-Color`. El acceso `image.pixels` con numpy es la vía estándar; el bake de esos mapas de origen es [ver: baking].)

## Reglas prácticas

1. Autoriza en **metallic/roughness** salvo razón fuerte: es lo que URP Lit espera por defecto y lo más difícil de romper.
2. Albedo = solo color propio, iluminado plano. **Cero** sombras, AO, highlights o reflejos cocidos.
3. Albedo dieléctrico dentro de **~30–240 sRGB**; nunca 0,0,0 ni 255,255,255 puros (salvo carbón/nieve reales).
4. Metallic **binario**: 0 (dieléctrico) o 1 (metal). Gris solo para AA del borde o capas finas — y suele salir mejor mezclando materiales.
5. Metal = base color con el **color de reflectancia** del metal (oro 255,226,155…) + metallic 1; su difuso conceptual es negro.
6. Roughness es donde más rinde el tiempo: rayones, huellas, desgaste, gotas — varíalo, no lo dejes plano.
7. **Unity trabaja en smoothness = 1 − roughness.** Invierte el roughness antes de entregar; URP lo lee del **alpha** del Metallic Map.
8. Normal para Unity = **OpenGL (Y+)**. Blender→Unity es directo; Substance (DirectX) → exporta OpenGL **o** activa *Flip Green Channel* en el import. Nunca las dos.
9. Decide la convención de normal (OpenGL) **una vez** para todo el proyecto; no mezcles.
10. Import sRGB: **ON** solo en albedo y emission; **OFF** en metallic, roughness/smoothness, AO, height, mask maps.
11. Normal se importa con Texture Type = **Normal map** (no como color).
12. **Confirma el render pipeline antes de empacar:** URP = MetallicSmoothness (RGB metal + A smoothness, AO aparte); HDRP = Mask Map RGBA (R metal, G AO, B detail, A smoothness). No son intercambiables.
13. AO siempre **separado del albedo**, ocluyendo solo luz ambiente; en URP, Unity lo lee del canal **G** del Occlusion Map.
14. Height/parallax solo si el material lo paga; displacement runtime casi nunca (default: normal solo) [ver: modelado/high-to-low §8].
15. Emission solo si el asset emite; HDR (>1) para alimentar Bloom.
16. En Blender, todo mapa de datos (metallic/roughness/normal) = `colorspace 'Non-Color'`; solo albedo/emission en `'sRGB'`.
17. Texturas potencia de 2 y texel density consistente entre assets [ver: pipeline/arte-a-unity §7].
18. **Aprueba el material EN Unity**, con el shader y la luz reales, moviendo la luz — nunca en el visor de la herramienta ni en Material Preview de Blender [ver: blender/materiales-preview §10].

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| El metal se ve **plateado/lavado** en Unity | Entregaron **roughness** donde URP espera **smoothness**; invertir (1−roughness) y ponerlo en el **alpha** del Metallic Map, o usar el preset Unity URP de Substance (§3.3, §6) |
| El relieve se ve **hundido/invertido** al mover la luz | Normal **DirectX** en un engine que espera **OpenGL**; exportar OpenGL o activar *Flip Green Channel* (§5) |
| Normal flippeado **dos veces** (export OpenGL + Flip Green Channel ON) | Elegir UNA sola vía; doble flip vuelve a estar mal |
| Material **muerto/sucio bajo toda luz** | AO o sombras cocidas en el albedo; sacarlas al Occlusion Map (§3.1) |
| Metal "sucio" con **metallic gris (0.5)** | Metal es metallic **1**; la suciedad va en roughness/albedo o como material aparte (§3.2) |
| Roughness importado se ve **mate donde debía brillar** | sRGB quedó **ON** en un mapa de datos; apagarlo (§7) |
| Mask map "correcto" pero **todo desplazado** en el engine | Se empacó para el pipeline equivocado (URP MetallicSmoothness ≠ HDRP RGBA); confirmar pipeline (§6) |
| Albedo **negro puro o blanco puro** | Ningún dieléctrico real llega a 0 ni 255; rango ~30–240 (§4) |
| Metales que se ven de **plástico** | Falta metallic = 1 y/o base color demasiado oscuro; el color del metal vive en el reflejo (§4) |
| Values de F0 "inventados" para dieléctricos | En metallic/roughness el F0 dieléctrico lo fija el shader (~4%); no se toca (§2) |
| Preview lindo en **Material Preview de Blender**, roto en Unity | EEVEE ≠ URP; validar en el engine con luz real [ver: blender/materiales-preview §10] |
| Normal aprobado mirando la **textura 2D** | Se aprueba sobre el modelo, en el engine, moviendo la luz sobre un bisel |

## Fuentes

- **LearnOpenGL — PBR/Theory** (learnopengl.com/PBR/Theory) — microfacet model, energy conservation (`kD = 1−kS`), dieléctrico F0 ≈ 0.04, conductores sin difuso con F0 0.5–1.0 tintado por albedo (`F0 = mix(F0, surfaceColor, metalness)`), roughness/NDF. Base de §1–2.
- **Unity Manual 6000.2 — Lit Shader (URP)** (`urp/lit-shader.html`) — Workflow Mode Metallic/Specular, Base/Metallic/Specular Map, **Smoothness** y **Smoothness Source = Metallic Alpha / Albedo Alpha**, Normal/Height/Occlusion/Emission. Base de §2, §3, §6, §7.
- **Unity Manual 6000.2 — Normal map texture type** (`texture-type-normal-map.html`) — Create From Grayscale, Bumpiness, Filtering, y **Flip Green Channel** ("invert the green (Y) channel values… if the normal map uses a different convention to what Unity expects" — no nombra DirectX/OpenGL literal, esa lectura es del autor). Base de §5.
- **Unity Manual 6000.2 — Default texture type** (`texture-type-default.html`) — **sRGB (Color Texture)**: ON en albedo/specular color, OFF cuando "you need the exact value" (metallic, roughness, occlusion, mask). Alpha Source, Read/Write, mipmaps. Base de §7.
- **Unity Manual — HDRP Mask Map and Detail Map** (`com.unity.render-pipelines.high-definition/manual/mask-map-and-detail-map.html`) — empaque RGBA del Mask Map: **R** Metallic, **G** Ambient Occlusion, **B** Detail Mask, **A** Smoothness; default 0.5 por canal. Base de §6.
- **physicallybased.info** (base de datos de valores medidos, actualizada 2026) — base color sRGB de metales (oro, plata, aluminio, cobre, cromo, hierro, titanio; metallic = 1) y de dieléctricos (carbón, concreto, nieve, agua, arena, pasto, piel) + IOR. Base de §4.
- **Base sintetizada — [ver: modelado/high-to-low]** — normal maps (tangent space, MikkTSpace, tabla de handedness OpenGL/DirectX por software, incl. Unity = Y+), AO separado del albedo, height vs normal vs displacement, floaters. (Fuentes primarias: polycount wiki, Marmoset.)
- **Base sintetizada — [ver: blender/materiales-preview]** — Principled BSDF (OpenPBR) en Blender 5.2, `colorspace_settings` Non-Color, smoothness = 1−roughness como trampa EEVEE→URP, "el veredicto es Unity". (Fuente primaria: Blender 5.2 Manual/API.)
- **Base sintetizada — [ver: pipeline/arte-a-unity]** — canales exactos de URP Lit, preset "Unity URP (Metallic Smoothness)", sRGB por mapa, texel density, 1 material por prop, runbook de auditoría de modelo. (Fuente primaria: Unity Manual 6000.2.)
- Cruces internos de texturizado: [ver: baking] (cómo se bakea cada mapa), [ver: uv-unwrapping], [ver: texturizado-blender], [ver: substance-y-alternativas] (export presets Substance Painter 2026), [ver: texturas-a-unity] (automatización de import), [ver: estilizado-texturas] (cuándo PBR no aplica).
