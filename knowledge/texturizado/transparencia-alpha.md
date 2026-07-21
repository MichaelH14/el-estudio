# Transparencia y alpha: follaje, cristal, pelo

> **Cuando cargar este archivo:** al texturizar o montar en Unity CUALQUIER asset que no sea 100% opaco — follaje/pasto/vallas/rejas (recorte por alpha), cristal/agua/humo/partículas (mezcla), o pelo/piel de cartas apiladas — y necesites decidir el **tipo de transparencia** (alpha clipping vs alpha blend vs alpha-to-coverage), arreglar **halos negros/blancos** en los bordes, resolver **transparencias que se dibujan mal** (sorting/render queue), o el **overdraw** que matan en móvil. NO repite la teoría PBR ([ver: pbr-teoria]) ni el import/material genérico ([ver: texturas-a-unity]); aquí va SOLO el eje de la transparencia. El viento del follaje y la refracción del cristal como shader viven en [ver: vfx-shaders/recetas-shaders]; el coste móvil profundo en [ver: movil/unity-movil-graficos]; la mecánica de sorting/overdraw 2D y Surface Type en [ver: unity/rendering-urp].

Versión de referencia: **Unity 6 / URP (manual 6000.2) · Blender 5.2 LTS · Substance Painter 2026**. Datos con dependencia de versión/pipeline van marcados.

## 1. Las tres técnicas y cuándo cada una (la decisión de arranque)

Transparencia no es UNA cosa. Hay tres mecanismos distintos, con costes y problemas distintos. Elegir mal es la causa raíz de casi todos los bugs de este archivo.

| Técnica | Qué hace el shader | Escribe depth (ZWrite) | ¿Sorting back-to-front? | Bordes | Para qué | Coste |
|---|---|---|---|---|---|---|
| **Alpha clipping** (cutout / alpha test) | `if (alpha < threshold) discard;` — el píxel se dibuja **entero o no se dibuja** | **Sí** (opaco a efectos de depth) | **No hace falta** | Duros/aliasing (sin AA extra) | Follaje, pasto, vallas, rejas, cadenas, hojas | Barato en CPU/sorting; `discard` **rompe early-Z en TBDR** móvil (§10) |
| **Alpha blend** (transparent) | Mezcla RGB con el fondo según alpha (`Blend SrcAlpha OneMinusSrcAlpha`) | **No** (ZWrite Off) | **Obligatorio** | Suaves, graduales | Cristal, agua, humo, fuego, partículas, UI, decals suaves | Caro: **overdraw** garantizado + sorting frágil |
| **Alpha-to-coverage** (A2C, `AlphaToMask`) | Convierte el alpha en una **máscara de cobertura MSAA** sub-píxel | **Sí** (como cutout) | **No hace falta** (order-independent) | Suaves **sin** sorting | Follaje y **pelo** de calidad, bordes de cutout antialiaseados | Requiere **MSAA activo**; niveles de opacidad limitados por samples (§4) |

Regla de decisión en una línea:

- **¿El material tiene borde definido y es "sí/no" opaco** (una hoja, una reja)? → **alpha clipping**. Nunca lo pongas Transparent.
- **¿Es genuinamente translúcido y gradual** (vidrio, humo, agua)? → **alpha blend** (Transparent), y asume el problema de sorting (§3).
- **¿Es cutout PERO el aliasing del borde molesta** (follaje AAA, pelo)? → **alpha-to-coverage** con MSAA (§4).

El error #1 de todo el tema: meter follaje/rejas como **Transparent** "porque tiene alpha". Es cutout → va **Opaque + Alpha Clipping**, y te ahorras todos los problemas de sorting y la mitad del overdraw.

## 2. Alpha clipping (cutout): follaje, vallas, rejas

El shader descarta el fragmento si el alpha no llega al umbral. El resultado se comporta como **geometría opaca con agujeros**: escribe profundidad, se ocluye bien, y **no necesita ordenarse** contra nada. Es el modo que quieres siempre que puedas.

**En URP Lit** (manual 6000.2, Surface Options):

- **Surface Type = Opaque** (¡no Transparent!) + activar el checkbox **Alpha Clipping**. La doc: *"Alpha Clipping — Discards pixels if their alpha value is lower than the Threshold value. The default value is 0.5."* Ese 0.5 es el punto de corte.
- El alpha vive en el **canal A del Base Map** (albedo con alpha). Import: `Alpha Source = Input Texture Alpha`, y **`alphaIsTransparency = ON`** para la dilatación de borde (§5) — aunque no sea "blend", la dilatación evita el fringe.
- Render queue: el shader entra en la cola **AlphaTest = 2450** (entre Geometry 2000 y el fin de lo opaco, GeometryLast 2500). O sea Unity lo dibuja **después** de lo opaco sólido pero **antes** de lo transparente, y lo ordena front-to-back como opaco (`Rendering.RenderQueue`, valores verificados §9).

**El threshold es un dial de arte, no un fijo:**

| Threshold | Efecto |
|---|---|
| ~0.5 (default) | Corte estándar; balance entre "comerse" borde y dejar fleco semitransparente |
| Más bajo (0.2–0.3) | Deja más píxeles → hojas/pelo más "llenos", pero más fleco sucio en el borde |
| Más alto (0.7+) | Recorta agresivo → silueta más limpia pero adelgaza el asset |

**Dos problemas propios del cutout, con su fix Unity:**

1. **Aliasing del borde** (escalones duros). El cutout no tiene gradiente → el borde "baila". Fix: **alpha-to-coverage** (§4) o TAA. No lo arregla MSAA solo (MSAA no antialiasa dentro del triángulo salvo con A2C).
2. **Adelgazamiento a distancia (mip thinning).** Al bajar de mip, el alpha promedio baja y **cada vez pasan menos píxeles el test** → el follaje se ve ralo/transparente de lejos. Fix Unity: en el import de la textura, **`Mip Maps > Preserve Coverage = ON`** + fijar el **Alpha Cutoff Value** al mismo threshold del material. Doc (`TextureImporterSettings.mipMapsPreserveCoverage`): *"rescale the alpha values of computed mipmaps so coverage is preserved… a higher percentage of pixels passes the alpha test and lower mipmap levels do not become more transparent."* **Está OFF por default** — actívalo en TODA textura de cutout.

## 3. Alpha blend (transparent): cristal, humo, agua — y el infierno del sorting

El shader **mezcla** su color con lo que ya hay detrás. Para que la mezcla sea correcta, lo de atrás tiene que estar ya dibujado → **hay que pintar de atrás hacia adelante** (back-to-front). Y para no tapar a los de atrás, el transparente **no escribe profundidad** (`ZWrite Off`). Ese par de hechos es el origen de todos los artefactos.

**En URP Lit:** Surface Type = **Transparent**. Doc: *"Blends the surface with the background. URP renders transparent surfaces in a separate render pass after opaque surfaces."* Opciones que aparecen solo en Transparent:

| Opción URP Lit | Qué controla |
|---|---|
| **Blending Mode = Alpha** | Mezcla estándar por alpha (`SrcAlpha·(1−SrcAlpha)`). El default para cristal/agua |
| **Blending Mode = Premultiply** | RGB ya multiplicado por alpha; evita halos y mezcla bordes suaves + aditivos en un solo material (§5) |
| **Blending Mode = Additive** | Suma color al fondo (fuego, energía, glow); no oscurece |
| **Blending Mode = Multiply** | Multiplica con el fondo (tintes, sombras de humo) |
| **Preserve Specular Lighting** | *"Keeps specular highlights on transparent surfaces by not applying the alpha value."* Cristal que debe brillar aunque sea casi invisible. Solo con Alpha/Additive |
| **Sorting Priority** | *"Unity renders materials with lower values first."* Offset manual de la cola para forzar orden entre transparentes que se pelean |

**Por qué se dibuja mal (los 3 síntomas clásicos):**

1. **Unity ordena por OBJETO, no por píxel.** `TransparencySortMode`: en perspectiva *"sort objects based on distance from camera position to the object center"*. Dos transparentes que se **interpenetran** (una copa dentro de otra, humo cruzando cristal) tienen el mismo "centro" ambiguo → uno se dibuja entero delante o detrás del otro, mal. No hay fix perfecto sin OIT; se mitiga partiendo la malla o con Sorting Priority.
2. **Un objeto cóncavo se ve a sí mismo mal.** Como no escribe depth, las caras traseras del propio cristal se mezclan en orden arbitrario → el interior se ve "plano" o revuelto. Mitigación: **dos pasadas** (primero caras traseras, luego frontales) o aceptar el look.
3. **El transparente no se ocluye ni proyecta bien.** Al no escribir depth, algo detrás de un cristal puede dibujarse encima si su cola es mayor. Y las sombras de transparentes son un tema aparte.

Herramienta de diagnóstico: **Frame Debugger** para ver el orden real de draw calls [ver: unity/rendering-urp].

## 4. Alpha-to-coverage (A2C): cutout con borde suave y SIN sorting

El punto medio ideal para follaje y pelo de calidad. Se activa con la orden ShaderLab **`AlphaToMask On`** (doc: *"Enables or disables alpha-to-coverage mode on the GPU"*, soportado en URP/HDRP/Built-in/Custom SRP). Mecánica (Wikipedia, *Alpha to coverage*; cita MSDN):

- Convierte el **alpha del fragmento en una máscara de cobertura MSAA** sub-píxel: alpha alto → más samples cubiertos, alpha bajo → menos. El AA de MSAA promedia esos samples → **borde suave**.
- **Order-independent**: como sigue siendo alpha-test (escribe depth), **no necesita back-to-front**. Es lo que lo hace perfecto para *"dense foliage where there are several overlapping polygons that use alpha transparency"* — y para **pelo** (§7).
- **Requiere MSAA activo** en el URP Asset (Anti Aliasing 2x/4x). Sin MSAA, A2C no hace nada.
- **Limitación**: los niveles de opacidad los limita el número de samples — *4x MSAA da solo 5 niveles* → puede haber quantization/banding en gradientes largos. Va perfecto para bordes, no para un cristal graduando de 0 a 100%.

En Shader Graph URP no hay un checkbox "AlphaToMask" directo; se logra con Alpha Clipping en un shader que además declare `AlphaToMask On` (shader a mano o variante). En móvil, ojo: MSAA es barato en TBDR pero A2C + `discard` sigue rompiendo early-Z (§10) — úsalo con criterio.

## 5. Dilatación de color / edge padding: por qué salen halos negros o blancos

**El problema.** Bajo los píxeles con alpha = 0, el RGB **sigue existiendo** (normalmente negro, a veces blanco, basura del exportador). El hardware, al **mipmapear** o filtrar **bilinealmente** el borde, promedia el color visible con ese RGB invisible de al lado → aparece un **halo/fringe** oscuro (o claro) alrededor de toda la silueta. Se ve peor a distancia (mips bajos) y en bordes de hoja/pelo.

**El fix: dilatar (bleed/padding).** Empujar el color de los píxeles visibles **hacia afuera**, dentro de las zonas transparentes, para que el vecino que se promedia tenga el color correcto en vez de negro. La doc de Unity lo dice literal (`TextureImporter.alphaIsTransparency`): *"dilate the color channels of visible texels into fully transparent areas. This effectively adds padding around transparent areas that prevents filtering artifacts from forming on their edges."*

**Dónde generar la dilatación (elige, en orden de preferencia):**

| Vía | Cómo | Nota |
|---|---|---|
| **En el DCC / Substance** | Export con **Dilation** (Substance Painter: "Dilation + transparent" / "Dilation infinite") — el PNG ya nace con el borde relleno | Preferido: la textura queda bien en disco para cualquier engine [ver: substance-y-alternativas] |
| **En Unity al import** | Marcar **`Alpha Is Transparency = ON`** → Unity dilata al importar | Cómodo, pero ⚠️ **no aplica a texturas HDR** y deja el color de los invisibles "undefined". Bien para color LDR |
| **Premultiplied alpha** | RGB ya multiplicado por alpha + Blending Mode **Premultiply** (§3) | Evita el halo por matemática de mezcla; otro camino, no combinar con dilatación a ciegas |

**Straight vs premultiplied alpha (el porqué del halo).** En **straight** (el default) el RGB y el alpha son independientes: la mezcla `RGB·alpha + fondo·(1−alpha)` samplea el RGB por separado, así que el negro invisible del borde **sí** contamina → necesitas dilatar. En **premultiplied** el RGB ya viene multiplicado por su alpha (los invisibles son 0,0,0,0 de forma coherente), y la mezcla es `RGB + fondo·(1−alpha)`: el borde promedia hacia 0 sin fringe, y de yapa mezcla suave + aditivo en un mismo material. URP Lit lo soporta con **Blending Mode = Premultiply**. Elige UNA vía; premultiply + dilatación a ciegas puede sobreoscurecer.

Regla: **toda textura con alpha** (cutout o blend) necesita dilatación **o** premultiply. Si ves un contorno oscuro fantasma en el borde de las hojas/pelo, es esto — no es la iluminación.

## 6. Follaje: alpha cards, doble cara, viento y LOD a billboard

El follaje es el caso de estudio del cutout. Anatomía de producción:

- **Alpha cards.** Planos ("cards") con una textura de rama/racimo de hojas: **Base Color + Alpha** (recorte), y a menudo **Normal**, **AO/Translucency** y a veces un mapa de **subsurface** para la luz que atraviesa la hoja. El árbol se arma solapando cards. Textura → **alpha clipping** (§2), nunca blend.
- **Doble cara (2-sided).** Una card es un plano infinitamente fino; desde atrás desaparecería. En URP Lit: **Render Face = Both** — *"renders both faces"*. El Lit **invierte la normal en la cara trasera** para que la luz responda bien por los dos lados. Coste: duplica los fragmentos de esa card (overdraw). Alternativa barata: geometría de dos planos cruzados (cross-cards) con Render Face = Front.
- **Viento.** No se anima con huesos: se desplazan los vértices en el shader por noise, anclando la base (máscara UV.y o vertex color) para que el tronco no flote. La cadena de nodos exacta (Wind / Foliage sway) está en [ver: vfx-shaders/recetas-shaders §10b] — no la repito aquí.
- **Preserve Coverage obligatorio** en la textura (§2) o el árbol se ve calvo/ralo a distancia.
- **LOD a billboard.** El último LOD de un árbol es un **billboard/impostor**: un solo quad con alpha que siempre mira a cámara (imagen pre-renderizada del árbol). Baja tris **y** capas de overdraw de golpe — clave en bosques móviles [ver: modelado/presupuestos-poligonos §5]. Sigue siendo cutout.

## 7. Hair / fur cards: capas de tarjetas con alpha, y el orden de dibujado

El pelo realtime se hace con **cards** (mechones = planos con textura de pelo: Base Color + **Alpha** + Normal/Flow + Root-Tip + ID/AO). Se apilan decenas de cards solapándose. El problema central es el **orden**: las cards son transparentes y se **interpenetran** → el sorting por objeto/triángulo de §3 **no las puede ordenar bien**. Los tres enfoques reales:

| Enfoque | Cómo | Trade-off |
|---|---|---|
| **Alpha clip para el grueso + blend para las puntas** | El cuerpo del pelo va **cutout** (escribe depth, no sorting); una pasada extra alpha-blend solo para el fleco suave de las puntas | Silueta sólida sin bugs de sorting; las puntas siguen siendo frágiles |
| **Alpha-to-coverage + MSAA** (§4) | `AlphaToMask On`; bordes suaves **order-independent** | El más limpio para pelo; exige MSAA (desktop/consola cómodo, móvil con cuidado) |
| **Dithered / hashed alpha + TAA** | Descarte con patrón de ruido (screen-door) que TAA promedia en el tiempo | Order-independent y barato; **exige TAA** o se ve el punteado; puede "hervir" en movimiento |

En todos: un **depth pre-pass** (o el propio alpha-clip que escribe depth) es lo que estabiliza el orden; el pelo 100% alpha-blend sin depth es lo que se ve revuelto al girar la cabeza. Fur (pelaje corto) suele resolverse con **shells** (capas concéntricas) o el mismo esquema de cards; misma lógica de alpha. La construcción de la malla de cards es de modelado; aquí importa que el **tipo de transparencia** sea cutout/A2C, no blend puro.

## 8. Cristal / vidrio: transparencia + (opcional) refracción

El cristal es el caso canónico de **alpha blend** real. Dos niveles de fidelidad:

- **Cristal simple (barato).** Surface Type = Transparent, Blending Mode = **Alpha**, alpha bajo (0.1–0.3), **Preserve Specular Lighting = ON** para que el highlight y el reflejo sigan vivos aunque el cristal sea casi invisible. Smoothness alta. Un toque de **Fresnel** (más opaco/reflectivo en ángulos rasantes, como el vidrio real) se logra con el nodo Fresnel Effect [ver: vfx-shaders/recetas-shaders §5]. Para la mayoría de props (ventanas, botellas, vitrinas) esto basta.
- **Cristal con refracción (screen-space).** La imagen detrás se **distorsiona** al pasar por el vidrio. Se hace muestreando la **Opaque Texture** (`_CameraOpaqueTexture`, "copia del color ANTES de los transparentes") con el UV desplazado por el normal map → el nodo **Scene Color** en Shader Graph. Requiere **Opaque Texture = ON** en el URP Asset. La receta de refracción/distorsión (agua, frosted glass, calor) está en [ver: vfx-shaders/recetas-shaders §9 y §11] — no la duplico. ⚠️ En móvil TBDR leer la Opaque Texture **anula el MSAA** y quema bandwidth [ver: movil/unity-movil-graficos §2]; usa refracción real solo si el juego la paga.

Reglas de cristal: siempre `ZWrite Off` (viene con Transparent); si el cristal es grueso/cerrado (una botella) vas a pelear el sorting de caras internas (§3) — parte la malla o acepta el look. Nada de refracción **verdadera** (índice IOR físico) en runtime; todo es fake screen-space.

## 9. Sorting y render queue en Unity: cómo ordena y qué se rompe

Unity dibuja por **render queue** (número). Valores exactos (`Rendering.RenderQueue`, verificados):

| Cola | Valor | Qué va aquí | Orden interno |
|---|---|---|---|
| **Background** | 1000 | Skybox, fondos | — |
| **Geometry** | 2000 | Opaco sólido (default) | **Front-to-back** (aprovecha early-Z) |
| **AlphaTest** | 2450 | **Cutout / alpha clipping** (follaje, rejas) | Como opaco |
| **GeometryLast** | 2500 | Fin de lo tratado como opaco | — |
| **Transparent** | 3000 | **Alpha blend** (cristal, humo, agua, partículas) | **Back-to-front** por distancia a cámara |
| **Overlay** | 4000 | Efectos finales, lens flare | — |

Claves operativas:

- **AlphaTest (2450) va DESPUÉS de Geometry.** El cutout se pone tras lo opaco a propósito, para no pagar su `discard` sobre píxeles que igual se taparían.
- **Transparent (3000) se ordena back-to-front** (doc: *"rendered after Geometry and AlphaTest, in back-to-front order"*) — pero **por objeto, no por píxel** (§3), y ahí está el bug.
- **Sorting Priority** del material URP Lit = offset a la cola (*"lower values first"*): la palanca para forzar que un decal transparente vaya sobre otro, o que el cristal del casco vaya después del HUD-glass.
- El truco del "agua transparente": ponerla en `Transparent-100` (offset) para que se dibuje **después de lo opaco pero antes** del resto de transparentes (patrón que la propia doc de SubShader Tags menciona).

En **2D** el mecanismo es otro (Sorting Layer → Order in Layer → distancia): cubierto en [ver: unity/rendering-urp "Sorting en 2D"].

## 10. Móvil: overdraw, y por qué el alpha clipping es caro en TBDR

En GPU móvil (tile-based, TBDR) el cuello es el **fillrate/overdraw**, no los tris. La transparencia es su peor enemigo:

- **Cada capa de alpha blend se paga entera.** No escribe depth → no se ocluye → el fragment shader corre por cada capa apilada. Cielo + niebla + humo + cristal = 4-5× overdraw sobre esa zona. Mídelo con **Scene view → Overdraw** ANTES de optimizar nada [ver: movil/unity-movil-graficos §4].
- **El `discard` del cutout rompe el early-Z.** El hardware TBDR ya no puede descartar fragmentos ocultos antes del fragment shader porque no sabe si se van a recortar. Doc/base móvil: *"clip/discard rompe el early-Z del TBDR"* → reservar alpha clipping para **cutout real (follaje)**, nunca "por si acaso" [ver: movil/unity-movil-graficos §3]. Un material que podría ser Opaque puro **no** debe tener Alpha Clipping activo.
- **A2C + MSAA** es viable en TBDR (MSAA se resuelve en el tile), pero sigue arrastrando el coste del `discard`. Follaje móvil masivo: preferir **billboard/impostor** en el LOD lejano para bajar capas (§6).
- **Refracción/Opaque Texture**: cara y anula MSAA en TBDR (§8). Evítala en móvil salvo hero prop.

Jerarquía de ataque en móvil si tanquea: recortar **capas/overdraw** → render scale → resolución de textura → shader a Unlit → geometría. El fillrate manda [ver: movil/unity-movil-graficos §10].

## 11. Lado DCC (Blender / Substance): autoría del alpha

El look final se aprueba en Unity (mantra de la base), pero el alpha se **autora** antes:

- **Blender:** la transparencia entra por el input **Alpha** del Principled BSDF (o un nodo de máscara). Para **previsualizar** cutout vs blend en EEVEE se elige el método de transparencia del material (en EEVEE Next 4.2+ es **Render Method: Dithered / Blended** — nombre de UI **NO VERIFICADO hoy**, el manual de docs.blender.org devolvió 403 al fetch; confirmar en tu build antes de documentarlo como definitivo) y, para follaje/cards, **desactivar Backface Culling** para ver las dos caras (el overlay de viewport homónimo está confirmado en [ver: blender/materiales-preview]; la propiedad de material equivalente en EEVEE Next puede llamarse distinto — verificar). ⚠️ Es **preview**: EEVEE ≠ URP; el veredicto es Unity.
- **Substance Painter:** pinta el alpha en un canal de opacidad; el export mete el alpha en el canal correcto del Base Color y, crítico, aplica **Dilation** (§5). Confirma el preset y que salga la dilatación [ver: substance-y-alternativas].
- El bake de máscaras (opacity, translucency de hoja) es tema de [ver: baking].

## 12. Transparencia fuera de URP Lit: Shader Graph y partículas

Los mismos tres tipos, con otros nombres, cuando no usas el Lit del inspector:

- **Shader Graph (URP).** En **Graph Settings**: **Surface Type = Opaque/Transparent** y el checkbox **Alpha Clipping = on/off** (equivalen a lo del Lit). El Master Stack expone en Fragment el bloque **Alpha** y, si Alpha Clipping está on, **Alpha Clip Threshold** — conectar la máscara al Alpha **no basta**, hay que activar Alpha Clipping en Graph Settings o no descarta [ver: vfx-shaders/recetas-shaders §1]. Para A2C hay que declarar `AlphaToMask On` (shader a mano o variante). Cutout barato hecho a mano: Alpha Clipping on + Threshold 0.5.
- **Partículas (Shuriken / VFX Graph).** Casi siempre **transparentes** → overdraw puro (una partícula cubre muchos píxeles y no se ocluye). Los dos blends que importan: **Alpha** (humo, salpicaduras — respeta el color de fondo) y **Additive** (fuego, chispas, magia — suma luz, ideal para HDR/Bloom, y **no necesita sorting** porque la suma es conmutativa). Aditivo = order-independent y barato de ordenar; alpha blend de partículas = sorting por sistema. El detalle de coste/flipbook/soft particles está en [ver: vfx-shaders/recetas-shaders] y [ver: unity/rendering-urp "overdraw"] — aquí basta: **partícula = transparente = vigila el overdraw** (§10).
- **Soft particles** (fade contra la geometría al intersecar) usan la **Depth Texture** del URP Asset; mismo aviso móvil que la refracción (pass extra) [ver: movil/unity-movil-graficos].

## Checklist de un asset con transparencia

Antes de marcar "listo" un asset no-opaco:

- [ ] **Tipo correcto elegido** (§1): cutout (follaje/rejas) = URP Lit **Opaque + Alpha Clipping**; translúcido gradual (cristal/humo) = **Transparent**; cutout con borde fino (pelo/follaje AAA) = **A2C + MSAA**. NUNCA follaje en Transparent.
- [ ] **Threshold** ajustado (~0.5 default) si es cutout; probado a distancia.
- [ ] **Dilatación / edge padding** hecha: `Alpha Is Transparency = ON` al import **o** Dilation en el DCC **o** premultiply (§5). Sin halo negro/blanco en el borde.
- [ ] **Preserve Coverage = ON** + Alpha Cutoff = threshold, en toda textura de cutout (§2) — no se ralea a distancia.
- [ ] **Doble cara** resuelta si aplica (Render Face = Both, o cross-cards) — las cards no desaparecen desde atrás (§6).
- [ ] **Sorting** revisado si es Transparent: interpenetraciones vistas desde varios ángulos; Sorting Priority si dos transparentes se pelean (§3, §9).
- [ ] **Compresión que preserva alpha** (BC7/DXT5/ASTC, **nunca BC1/DXT1** que descarta alpha) [ver: atlas-trim-optimizacion].
- [ ] **Overdraw medido** en el device más débil (Scene → Overdraw); cutout no activo en materiales que podrían ser opacos (§10).
- [ ] **Aprobado en Unity** con luz y post reales, en movimiento — no en el render del DCC [ver: texturas-a-unity §8].

## Reglas prácticas

1. Decide el **tipo** primero (§1): cutout / blend / A2C. La mayoría de los bugs son un tipo mal elegido.
2. Follaje, pasto, vallas, rejas, cadenas → **Opaque + Alpha Clipping**, jamás Transparent. Escribe depth, no necesita sorting, la mitad de overdraw.
3. Cristal, agua, humo, fuego, partículas, UI → **Transparent**; asume el sorting frágil (§3) y el overdraw (§10).
4. Borde de cutout con aliasing molesto → **alpha-to-coverage** (`AlphaToMask On`) con **MSAA activo**; no lo arregla MSAA solo.
5. **Toda** textura con alpha lleva **dilatación** (Alpha Is Transparency / Dilation en Substance) o premultiply — o sale halo en el borde (§5).
6. Cutout → **Preserve Coverage ON** + Alpha Cutoff = threshold del material, o se ralea a distancia (§2). Está OFF por default.
7. Cards de follaje/pelo → **Render Face = Both** (o cross-cards); si no, desaparecen desde atrás.
8. Alpha blend = **ZWrite Off** por diseño → **no se ocluye ni se ordena por píxel**. Objetos cóncavos transparentes se ven mal; parte la malla o acéptalo.
9. Transparentes que se pelean el orden → **Sorting Priority** (menor = antes) antes de tocar shaders.
10. Compresión con alpha = **BC7/DXT5/ASTC**, nunca BC1/DXT1 (descarta el alpha); si el alpha sale bandeado, es la compresión.
11. Cristal creíble barato = Transparent + **Preserve Specular Lighting ON** + Fresnel [ver: vfx-shaders/recetas-shaders §5]; refracción real (Opaque Texture) solo si el juego la paga.
12. Viento de follaje = vertex displacement en shader, no huesos; ancla la base [ver: vfx-shaders/recetas-shaders §10b].
13. Último LOD de árbol = **billboard/impostor** para matar tris y capas de overdraw [ver: modelado/presupuestos-poligonos §5].
14. Móvil: `discard`/alpha clipping **rompe early-Z en TBDR** → solo para cutout real, nunca "por si acaso" en algo que podría ser Opaque [ver: movil/unity-movil-graficos §3].
15. Móvil: mide **overdraw** (Scene → Overdraw) antes de optimizar otra cosa; la transparencia apilada es el enemigo #1 [ver: movil/unity-movil-graficos §4].
16. El alpha del cutout va en el **canal A del Base Map**; el alpha del Metallic Map es **smoothness (dato)**, no transparencia — no los confundas (`alphaIsTransparency` OFF en el metallic) [ver: texturas-a-unity §2].
17. Aprueba la transparencia **en Unity**, moviendo cámara y luz, contra fondos claros y oscuros (el halo solo aparece contra ciertos fondos).
18. Partículas: **Additive** siempre que el look lo permita — suma conmutativa = sin sorting y feed directo al Bloom; **Alpha** solo cuando de verdad debe respetar el color de fondo (§12).
19. En Shader Graph, **Alpha Clipping** se activa en Graph Settings (no basta cablear el Alpha); Surface Type = Transparent para blend real. Equivale al inspector del Lit (§12).
20. Un asset que falla cualquier punto del checklist se **devuelve al paso que falló**; no se "arregla un poco" en Unity — eso crea drift permanente [ver: texturas-a-unity].

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Follaje/reja puesto como **Transparent** → sorting revuelto + overdraw doble | Es cutout: URP Lit **Opaque + Alpha Clipping** (§1, §2) |
| **Halo negro/blanco** alrededor de las hojas/pelo, peor de lejos | Falta dilatación: `Alpha Is Transparency = ON` o Dilation en Substance, o premultiply (§5) |
| El follaje se ve **ralo/calvo a distancia** | Falta **Preserve Coverage** + Alpha Cutoff = threshold en la textura (§2) |
| Card de hoja **desaparece desde atrás** | Render Face = Front en un plano fino; poner **Both** o usar cross-cards (§6) |
| Dos cristales/humos se dibujan **uno delante del otro mal** al moverse | Sorting por objeto (centro), no por píxel; interpenetración → parte la malla o usa Sorting Priority (§3) |
| Interior de una botella/casco transparente **revuelto** | Sin ZWrite las caras internas no se ordenan; dos pasadas (back luego front) o aceptar (§3, §8) |
| Borde de cutout con **escalones/aliasing** | Alpha-to-coverage (`AlphaToMask On`) + MSAA; MSAA solo no antialiasa el interior (§4) |
| Alpha-to-coverage **no hace nada** | MSAA apagado en el URP Asset; A2C exige multisampling (§4) |
| Smoothness bandeado / alpha sucio en un mapa de datos | Compresión BC1/DXT1 (descarta alpha) o `alphaIsTransparency` ON en un mapa que no es color; usar BC7/DXT5 (§checklist) |
| Cristal casi invisible pierde su **brillo/reflejo** | Falta **Preserve Specular Lighting** en el material Transparent (§3, §8) |
| FPS al piso en móvil "solo con humo/cristal" | Overdraw de capas transparentes; medir Scene → Overdraw, reducir capas/tamaño (§10) |
| Material **Opaque** con Alpha Clipping activo "por si acaso" mata perf móvil | El `discard` rompe early-Z; apagar Alpha Clipping si no hay recorte real (§10) |
| Refracción de cristal mata el móvil | Opaque Texture anula MSAA y quema bandwidth en TBDR; fake con Fresnel o quitarla en móvil (§8) |
| Cutout se ve **comido/adelgazado** incluso de cerca | Threshold demasiado alto; bajar hacia ~0.5 (o menos para hoja/pelo) (§2) |
| Algo detrás de un cristal se **dibuja encima** de él | Cola mal: el opaco de atrás debe ir en Geometry (2000) y el cristal en Transparent (3000); revisar Sorting Priority (§9) |
| Partículas alpha-blend que **parpadean/reordenan** al mover cámara | Sorting por sistema, no por partícula; pasar a **Additive** (order-independent) donde el look lo permita (§12) |
| Conecté el Alpha en Shader Graph y **no recorta** | Falta activar **Alpha Clipping** en Graph Settings; conectar el bloque Alpha no basta (§12) |
| Aprobar la transparencia en el render de Blender/Painter | EEVEE ≠ URP; validar en Unity con luz real y varios fondos (§11) |

## Fuentes

- **Unity Manual 6000.2 — Lit Shader (URP)** (`urp/lit-shader.html`) — Surface Type (*"Opaque… URP renders opaque surfaces first"* / *"Transparent… Blends the surface with the background… separate render pass after opaque surfaces"*), **Blending Mode** (Alpha/Premultiply/Additive/Multiply, con descripciones exactas), **Render Face** (Front/Back/Both), **Alpha Clipping** (*"Discards pixels if their alpha value is lower than the Threshold value. The default value is 0.5"*), **Preserve Specular Lighting**, **Sorting Priority** (*"Unity renders materials with lower values first"*). Base de §1–§4, §8, §9.
- **Unity Scripting API — `Rendering.RenderQueue`** (`ScriptReference/Rendering.RenderQueue.html`) — valores exactos: Background 1000, Geometry 2000, **AlphaTest 2450**, GeometryLast 2500, **Transparent 3000** (*"rendered after Geometry and AlphaTest, in back-to-front order"*), Overlay 4000. Base de §2, §9.
- **Unity Manual — ShaderLab SubShader Tags** (`SL-SubShaderTags.html`) — el tag **Queue** (Background/Geometry/AlphaTest/Transparent/Overlay) y el offset (*"transparent water… draw after opaque objects but before transparent objects"*). Base de §9.
- **Unity Scripting API — `TextureImporter.alphaIsTransparency`** — dilatación de color / edge padding: *"dilate the color channels of visible texels into fully transparent areas. This effectively adds padding around transparent areas that prevents filtering artifacts from forming on their edges"*; no soportado en HDR; texels invisibles quedan "undefined". Base de §5.
- **Unity Scripting API — `TextureImporterSettings.mipMapsPreserveCoverage`** — *"rescale the alpha values of computed mipmaps so coverage is preserved… lower mipmap levels do not become more transparent"*; disabled by default. Base de §2, §6 (thinning de follaje).
- **Unity Manual — ShaderLab command `AlphaToMask`** (`SL-AlphaToMask.html`) — *"Enables or disables alpha-to-coverage mode on the GPU"*; `On`/`Off`; soportado en URP/HDRP/Custom SRP/Built-in; enlace a alpha-to-coverage y "Reduce aliasing with AlphaToMask mode". Base de §4, §7.
- **Unity Scripting API — `TransparencySortMode`** (Default/Perspective/Orthographic/CustomAxis) — perspectiva *"sort objects based on distance from camera position to the object center"*; ortho por distancia a lo largo de la vista → el sorting por objeto (no por píxel) que rompe interpenetraciones. Base de §3.
- **Wikipedia — Alpha to coverage** (en.wikipedia.org/wiki/Alpha_to_coverage; cita MSDN) — máscara de cobertura MSAA en función del alpha, order-independent, máscara monotónica, *"most useful for situations such as dense foliage where there are several overlapping polygons"*, 4x MSAA → ~5 niveles de opacidad (quantization). Base de §4, §7.
- Cruces internos de la base: [ver: pbr-teoria] (canales, mask maps, el alpha del Metallic = smoothness), [ver: texturas-a-unity] (import, `alphaIsTransparency`, compresión con alpha, verificación en Unity), [ver: atlas-trim-optimizacion] (compresión BC7/DXT5/ASTC), [ver: baking] (bake de máscaras opacity/translucency), [ver: texturizado-blender] / [ver: substance-y-alternativas] (autoría del alpha + Dilation), [ver: unity/rendering-urp] (Surface Type, sorting 2D, overdraw, Frame Debugger), [ver: movil/unity-movil-graficos] (TBDR, early-Z y `discard`, overdraw §3–§4), [ver: vfx-shaders/recetas-shaders] (viento §10b, refracción/Scene Color §9/§11, Fresnel §5), [ver: modelado/presupuestos-poligonos] (billboards/impostors), [ver: modelado/high-to-low] (normal de cards).
