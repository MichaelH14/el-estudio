# Texturizado estilizado y hand-painted

> **Cuando cargar este archivo:** al texturizar un asset de juego con estética estilizada — hand-painted (luz pintada en la difusa), PBR estilizado, gradientes o low-poly barato — y decidir DÓNDE poner la luz, con qué herramienta pintar, cómo mantener consistencia entre assets y qué shader lo termina en Unity. Es el CÓMO de textura del estilo que [ver: modelado/estilizacion-lowpoly] y [ver: gamedev/arte-direccion] eligen. La teoría PBR base vive en [ver: pbr-teoria]; el bake de mapas en [ver: baking]; la entrega a Unity en [ver: texturas-a-unity].

## 1. El eje del estilizado: ¿dónde vive la luz?

La decisión que define TODO el pipeline de textura estilizado es una sola: **¿la luz la calcula el motor, o la pinta el artista en el albedo?** No es una preferencia estética, es una bifurcación de pipeline con costes y consecuencias opuestas.

| | PBR (realista o estilizado) | Hand-painted puro |
|---|---|---|
| **Luz y sombra** | Las calcula el shader en tiempo real; el albedo NO las contiene | Pintadas a mano DENTRO del albedo/difusa |
| **Albedo / base color** | "Lit-neutral": color plano de material, sin dirección de luz, sin AO horneado, sin highlights [ver: pbr-teoria] | Es una ilustración terminada: AO, sombra de forma, highlights y rim ya pintados |
| **Mapas** | Base + Metallic + Roughness/Smoothness + Normal (+AO, Emission) [ver: pbr-teoria] | Solo difusa a menudo; sin normal, sin roughness, sin metallic |
| **Shader en engine** | Lit / PBR completo [ver: unity/rendering-urp] | Unlit o Baked Lit — el motor NO debe re-iluminar lo ya pintado (§8) |
| **Envejece** | Depende del hardware/iluminación de la generación | Casi nada: el look no depende de la luz del motor (WoW se ve igual a 15 años) |
| **Skill que exige** | Autoría de materiales (capas, máscaras, escaneo) | Skill de PINTOR: valor, color, luz, bordes — el más escaso |

**Regla de no-contradicción:** meter luz pintada en un albedo que además recibe luz dinámica = doble sombra, doble AO, look sucio. Hand-painted ⇒ shader que no re-ilumine (§8). Es el error nº1 al importar assets hand-painted a un proyecto con Lit por defecto.

## 2. El espectro: full hand-painted ↔ PBR estilizado

No es binario. Es un eje continuo, y cada juego elige un punto según su skill 2D y su motor. Ubicar el asset en el espectro ANTES de texturizar (es un parámetro del encargo, no una decisión por asset):

| Punto del espectro | Qué se pinta / qué calcula el motor | Mapas | Referentes típicos | Cuándo elegirlo |
|---|---|---|---|---|
| **Full hand-painted** | TODO en la difusa: luz, sombra, AO, highlights, material | Difusa sola (a veces + normal suave para formas grandes) | World of Warcraft, Torchlight, mucho RPG móvil | Hay pintor real; se quiere look "timeless" e independiente de la luz |
| **Hand-painted + bakes** | Se pinta ENCIMA de AO/curvatura horneados como guía; el resto a mano | Difusa + AO/curvature de referencia (no siempre exportados) | Escuela clásica de props estilizados | Pintor + modelo con high-poly; acelera el sombreado de forma |
| **PBR estilizado** | Material real (metal/rough/normal) pero EXAGERADO, limpio y a mano; albedo lit-neutral pero saturado y simplificado | Base + Metallic + Roughness + Normal (todos "domados") | Overwatch, Fortnite, Fall Guys | Se quiere iluminación dinámica y PBR pero con lenguaje cartoon |
| **Flat + gradientes** | Colores planos + gradient map para tono/profundidad barata; casi cero luz pintada | 1 textura de paleta/gradiente diminuta (§5, §6) | Móvil hyper-casual, puzzle, Monument Valley-like | Sin artista de textura; look gráfico limpio |
| **Sin textura (vertex/atlas)** | El color viaja en la malla o en una paleta-atlas; la luz la hace el shader | Ninguno o 1 paleta 128–256px | Astroneer, Grow Home [ver: modelado/estilizacion-lowpoly] | Solo dev, cero skill 2D, máximo ahorro [ver: pipeline-3d/receta-lowpoly-estilizado] |

Reglas de elección:
- **Elige el punto por el skill 2D real, no por el juego que admiras.** "Hand-painted porque WoW" sin pintor = el error de presupuesto clásico [ver: gamedev/arte-direccion §3]. Full hand-painted es el punto MÁS CARO de todos.
- **No mezcles puntos dentro de un juego** sin decisión explícita: un prop full hand-painted junto a uno flat+gradiente se leen como dos juegos (§7).
- El espectro NO es "más caro = mejor". Flat+gradientes y sin-textura ganan en coherencia, memoria y velocidad para un equipo mínimo (§10).

## 3. Anatomía de una difusa hand-painted (el orden de pintado)

Full hand-painted no es "pintar como se me ocurra": es una secuencia de capas que reconstruye a mano lo que el PBR calcularía. Orden estándar de la escuela (props/personajes estilizados):

1. **UVs limpias primero.** Hand-painted castiga las costuras: van escondidas y con buena densidad de texel [ver: uv-unwrapping]. Una seam en la cara de un personaje se ve pintada mal para siempre.
2. **Flat colors (bloqueo).** Rellenar cada zona de material con su color plano de la paleta maestra (§7). Es el equivalente al albedo lit-neutral, pero será el punto de partida, no el resultado.
3. **AO como capa base multiplicada.** Hornear AO [ver: baking] y ponerlo en modo Multiply sobre los flats: da el oclusion gratis (grietas, contactos) que arrancan el sombreado. NO es el look final, es el andamio.
4. **Sombra de forma (form shadow).** Elegir UNA dirección de luz global del style guide (típico: arriba-adelante) y pintar la ladera en sombra de cada volumen. Aquí es donde el asset empieza a tener volumen sin geometría.
5. **Highlights y bordes al filo (chiseled edges).** El sello del hand-painted: bordes definidos con un highlight fino en el canto que recibe luz y una línea oscura en el que no. Da la lectura "cincelada" de WoW. Silueta > detalle: el borde lee a distancia [ver: gamedev/arte-direccion §5].
6. **Rim / luz de rebote** en el lado opuesto a la luz principal, sutil, para despegar del fondo.
7. **Variación de color y "material feel".** Manchas de tono, óxido, vetas de madera, poros — pintados, no fotográficos. El detalle SOLO por contraste con áreas de descanso (Nielsen: sobre-detalle = muddiness) [ver: gamedev/arte-direccion §5].

Tres tipos de oscuro que el pintor separa (confundirlos es el error nº1 del hand-painted novato):
- **Oclusión (AO):** grietas y contactos donde no entra luz ambiente. Es el bake del paso 3; no cambia con la dirección de luz.
- **Form shadow:** la ladera del volumen que da la espalda a la luz principal. Transición SUAVE, define el volumen (paso 4).
- **Cast shadow:** la sombra que un elemento proyecta sobre otro (el ala sobre el cuerpo). Borde más DURO, se pinta sabiendo la dirección de luz global.

Principios que separan hand-painted bueno de "textura con AO y ya":
- **Contraste de valor > color.** El volumen lo hace el rango claro-oscuro, no el hue. Test: en escala de grises el asset debe leerse [ver: gamedev/arte-direccion §4].
- **Bordes definidos, transiciones controladas.** Ni todo duro (recortado) ni todo suave (fofo): duro en los cantos y cast shadows, suave en las form shadows.
- **Frecuencia de detalle escalonada.** Primero las masas grandes de luz/sombra (baja frecuencia), al final los detalles finos (alta frecuencia) SOLO en focal points; nunca detalle fino sobre una masa mal resuelta.
- **Nada de fotos.** Pegar una foto de madera rompe el estilo al instante; se pinta la sugerencia de madera con la paleta del juego.

## 4. Herramientas: dónde pintar

| Herramienta | Rol en estilizado | Fuerza | Coste (jul-2026) |
|---|---|---|---|
| **Blender Texture Paint** | Pintar en 3D directo sobre el modelo (projection paint) + Image Editor 2D; bake de AO/normal en el mismo archivo | Todo-en-uno gratis; ver la costura pintarse en 3D; sin round-trip | Gratis. Detalle de modo y slots en [ver: texturizado-blender] |
| **Substance 3D Painter** | Capas + máscaras + generadores por mesh maps; para PBR estilizado y hand-painted híbrido | Bakes de calidad, no-destructivo, export con presets Unity | Suscripción indie; precio exacto **NO VERIFICADO** (fuente da ~$20–25/mes; confirmar contra pricing oficial de Adobe antes de presupuestar) [ver: substance-y-alternativas] |
| **Photoshop / Krita / Procreate** | Pintar la difusa en 2D sobre las UVs exportadas; retoque final | Máximo control de pintor; Krita gratis; Procreate en iPad para pintores | Krita gratis; PS suscripción; Procreate pago único |
| **3D Coat** | Referencia del gremio para hand-painted 3D (no verificado a fondo aquí) | Herramientas de pintor sobre modelo | **NO VERIFICADO** — fuera si no se confirma |

**Flujo recomendado para full hand-painted con herramientas gratis:** Blender para UVs + bake AO/curvatura [ver: baking] → pintar en Blender Texture Paint (3D) o exportar a Krita/PS para la difusa → re-importar → verificar EN Unity con el shader final (§8).

**Esqueleto bpy — preparar el slot de pintura y hornear el AO base** (operadores estables de Cycles; parámetros completos y verificados en [ver: baking] y [ver: texturizado-blender]):

```python
import bpy
# 1) Imagen destino para la difusa hand-painted (potencia de 2)
img = bpy.data.images.new("DIFF_asset", width=2048, height=2048, alpha=True)

# 2) Nodo Image Texture en el material, seleccionado y activo = destino del bake
#    (Cycles hornea SIEMPRE al nodo Image Texture activo del material activo)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'              # el bake vive en Cycles, no en EEVEE
scene.render.bake.margin = 16               # sangrado del bake fuera de las islas UV
scene.render.bake.use_selected_to_active = False  # AO del propio objeto: no hace falta hi->lo

# 3) Hornear Ambient Occlusion como capa base (luego Multiply sobre los flats, §3)
bpy.ops.object.bake(type='AO')              # type acepta 'AO','NORMAL','COMBINED','DIFFUSE'...
img.save_render(filepath="//bake/AO_asset.png")
```

> Para bake high→low (AO/normal desde un high-poly): `use_selected_to_active=True`, seleccionar hi + lo con lo ACTIVO, y ajustar `bake.max_ray_distance` / `bake.cage_extrusion`. El procedimiento completo, con cage y verificación, está en [ver: baking] — no se reproduce aquí.

## 5. Gradient maps y paletas limitadas

Dos técnicas que dan tono y cohesión con casi cero pintura — la vía barata del estilizado:

- **Gradient map (mapa de gradiente):** re-mapea el VALOR de una imagen (o de un AO/curvatura) a una rampa de color. Sombras → un tono frío, medios → color base, luces → un tono cálido, en UN gradiente. Recolorea un asset entero cambiando la rampa. En Substance es un filtro/efecto; en Photoshop es "Gradient Map"; en Blender es un nodo ColorRamp sobre el valor. Da el "tinte" coherente que hace que 40 props se vean del mismo mundo.
- **Paleta limitada (3–5 hues + rampas de valor):** más barata de mantener y MÁS identitaria que una paleta abierta [ver: gamedev/arte-direccion §4]. Hex exactos del style guide, copiados, nunca re-pickeados a ojo.
- **Textura-atlas de gradientes (Palette Grid, 80.lv):** UNA textura diminuta de tiras de gradiente compartida por todos los assets; las UVs de cada grupo de caras se snapean a una tira. Da profundidad (oscuro→claro) sin pintar. Coste de memoria: "una textura 1K consume memoria comparable a ~40.000 vértices" (Bahri, 80.lv) → usar 128–256px, no 1K. Detalle del runbook en [ver: modelado/estilizacion-lowpoly §4] y [ver: atlas-trim-optimizacion].

**Runbook — gradient map como grading barato sobre un asset ya pintado (o sobre su AO):**
1. Partir de una imagen en valor: la difusa en grises, o directamente el AO/curvatura horneado [ver: baking].
2. Definir una rampa de 3–5 paradas con hex del style guide: sombra (tono frío o complementario), medio (color base), luz (tono cálido). El "empuje" de temperatura sombra-fría/luz-cálida es lo que da el look pintado sin pintar.
3. Aplicar el gradient map: Photoshop `Gradient Map` (Image ▸ Adjustments), Substance filtro/efecto de gradiente, Blender nodo `ColorRamp` sobre el Factor de valor.
4. La MISMA rampa sobre todos los assets del bioma = 40 props que se leen del mismo mundo con cero repintado.
5. Recolorear el juego entero = editar la rampa, no los assets. Es el gradient map lo que hace timeless y coherente el flat+gradiente del espectro (§2).

**Cuándo cada uno:** gradient map = tono/mood coherente sobre difusas ya pintadas. Paleta-atlas de gradientes = reemplaza el pintado por completo en low-poly (§6). Se combinan: atlas para el color base + gradient map global para el grading.

## 6. Texturizado low-poly barato (el pipeline más económico que existe)

Para un solo dev sin skill 2D, el estilizado más racional se salta el hand-painted entero. Tres técnicas, de más barata a más flexible (mecánica completa en [ver: modelado/estilizacion-lowpoly §4] y [ver: pipeline-3d/receta-lowpoly-estilizado]):

| Técnica | Cómo | Textura | Consistencia | Trampa |
|---|---|---|---|---|
| **Color por material** | Un material plano por zona | Ninguna | Trivial | Cada material extra = draw call; rompe batching con pocos assets [ver: texturas-a-unity] |
| **Vertex colors** | Color pintado en los vértices, viaja en el FBX/glTF; el rasterizador interpola → gradientes gratis | Ninguna; 1 material para todo | Alta si la paleta es fija | Necesita shader que LEA vertex color (Lit estándar lo ignora → se importa "gris") |
| **Paleta-atlas** | UNA textura 128–256px de bloques/gradientes; UVs colapsadas a un punto/tira | 1 textura + 1 material para el juego | Máxima: recolorear la paleta = re-skin global | 1K es overkill (§5); UVs sin unwrap real |

Este es el punto "sin textura" del espectro (§2). El color y la cohesión son gratis; TODO el look lo termina el shader y la luz (§8). Objetivo: **1 material para todo el mundo estático**; un material nuevo exige justificación por escrito [ver: texturas-a-unity].

## 7. Consistencia de estilo entre assets (el style guide de textura)

Un asset "bien pintado" que rompe la paleta o la densidad de detalle daña el juego más que uno mediocre coherente [ver: gamedev/arte-direccion §1]. Lo que un agente que texturiza en serie rompe primero. Se congela por escrito y todo asset se audita contra el visual target [ver: gamedev/arte-direccion §2]:

| Parámetro de textura | Qué se congela | Síntoma si se rompe |
|---|---|---|
| **Paleta maestra** | Hex exactos, idealmente 1 paleta-atlas compartida (§5) | Un asset con "su" verde desentona en todas las escenas |
| **Dirección de luz pintada** | Un vector global (p.ej. arriba-adelante) para el form shadow de TODO hand-painted (§3) | Un prop iluminado desde la izquierda junto a otro desde arriba = luz imposible |
| **Densidad de detalle** | Nivel de "trabajo" por cm² relativo al tamaño; dónde va el detalle y dónde el descanso | Un barril hiperdetallado junto a una casa lisa: "de otro juego" |
| **Texel density** | px/m consistente por categoría (p.ej. 512 props, 1024 hero) | Un asset con textura más nítida se lee como más importante sin serlo |
| **Tratamiento de bordes** | Grosor y contraste del chiseled edge / rim; duro vs suave | Bordes recortados junto a bordes fofos rompen el "sello" del estilo |
| **Rango de valor** | Qué tan oscura la sombra y qué tan clara la luz pintadas | Un asset de bajo contraste se ve "lavado" al lado de uno contrastado |

Regla operativa para un agente en serie: estos 6 son **parámetros fijos del encargo**, no espacio creativo. La creatividad vive dentro de ellos. Coherencia > calidad individual [ver: gamedev/arte-direccion §1]. Documentar cada excepción aprobada el mismo día o es drift garantizado.

## 8. El shader del engine termina el look (la textura es solo la mitad)

Una difusa estilizada NO es el look final: el shader y la luz de Unity cierran la otra mitad. La regla que amarra textura↔shader:

| Punto del espectro (§2) | Shader URP correcto | Por qué |
|---|---|---|
| **Full hand-painted** (luz ya pintada) | **Unlit** o **Baked Lit** | El motor NO debe re-iluminar: si aplica Lit, dobla sombras y AO. Verificado: URP ofrece Unlit y la jerarquía Lit/Complex Lit (docs URP 6000.0) |
| **PBR estilizado** | **Lit** con toon/ramp o **Simple Lit** | Se quiere iluminación dinámica; toon shading pone la luz en bandas duras en vez de gradiente |
| **Flat / gradientes / vertex** | **Simple Lit** o **Unlit** (custom que lea vertex color) | PBR completo que nadie verá es desperdicio; Simple Lit es no-PBR, más barato (docs URP 6000.0) |

Piezas que "dibujan" el estilo en el motor (detalle en [ver: unity/rendering-urp] y [ver: modelado/estilizacion-lowpoly §8]):
- **Toon / cel shading:** luz en bandas (step/smoothstep sobre el modelo de iluminación); specular thresholded; rim solo en el lado iluminado (receta Roystan, referente Breath of the Wild: 2 bandas + rim). Shader Graph o custom.
- **Outline:** separa siluetas (inverted hull o post-proceso por bordes). Alternativa sin outline: rim light (vía TF2) [ver: gamedev/arte-direccion §5].
- **Ramp map:** una textura-rampa 1D controla cómo la luz mapea a color — el mismo truco del gradient map (§5) pero en el shader, en tiempo real.

**Shader más barato que logre el look:** `Unlit > Baked Lit > Simple Lit > Lit` [ver: unity/rendering-urp]. Full hand-painted casi siempre cae en Unlit/Baked Lit — y ahí es donde el look "envejece poco": no depende de la iluminación del motor.

**Regla dura:** ningún asset estilizado se aprueba en el visor de Blender/Substance. Se aprueba en la escena visual-target de Unity, con el shader (toon/unlit), outline, fog y luz reales [ver: pipeline/arte-a-unity §10]. El "bonito en el viewport del DCC" no existe como dato.

## 9. Entrega e import a Unity (los settings que rompen el estilizado)

La spec exacta de canales URP y la auditoría de import viven en [ver: texturas-a-unity] y [ver: pipeline/arte-a-unity §7]. Lo específico del estilizado:

| Mapa / caso | Setting Unity | Trampa estilizada |
|---|---|---|
| **Difusa hand-painted** (albedo) | Texture Type `Default`, **sRGB (Color Texture) = On** | Es color, no dato: sRGB On. Y va a **Base Map** de un shader que no re-ilumine (§8) |
| **Paleta-atlas / gradiente** | sRGB On; **Filter Mode `Point`** si son bloques duros, `Bilinear` si son gradientes suaves; **Compression `None`** en texturas diminutas | Comprimir una paleta 128px mete banding en los gradientes; Point en un gradiente lo escalona |
| **AO / roughness / máscara** (si el PBR estilizado los usa) | **sRGB Off** (son datos, no color) | AO con sRGB On = oclusión mal graduada. Verificado contra Texture Importer 6000.0 |
| **Normal** (si lo hay) | Texture Type `Normal map` | Hand-painted a menudo NO lleva normal — no lo inventes |
| **Smoothness** | Canal A del Metallic o del Base Map; URP usa **smoothness = 1 − roughness** | Substance/glTF exportan roughness: pedir preset "Unity URP (Metallic Smoothness)" o invertir el canal [ver: texturas-a-unity] |

- **Vertex colors:** no son un archivo de textura; viajan en el FBX/glTF. Al importar, asignar un shader que los lea (Unlit/custom/Shader Graph) o el modelo se ve gris [ver: modelado/estilizacion-lowpoly §4].
- **Tamaños potencia de 2** (512/1024/2048); texel density consistente (§7).
- Verificar el color EN Unity, no en el DCC: gamma y espacio de color difieren [ver: pipeline/arte-a-unity §10].

## 10. Trampas del estilizado y cuándo gana al realista

**Por qué el estilizado engaña ("se ve fácil"):**
- El low-poly/flat parece trivial porque hay poca geometría y poca textura — pero **cada decisión pesa más**: sin normal map ni PBR que tape, una proporción fea o una paleta floja quedan desnudas.
- **Full hand-painted es el punto MÁS CARO** (§2): cada textura es una ilustración con luz pintada. Elegirlo "porque es estilizado = barato" es el error de presupuesto clásico. Exige skill de pintor real (valor, color, bordes), el más escaso de conseguir.
- **Consistencia > virtuosismo:** 40 assets coherentes valen más que 5 obras maestras que no pegan (§7). Lo difícil no es un asset bonito, es que el asset nº200 se vea del mismo juego.

**Cuándo el estilizado gana al realista para un dev solo:**

| Ventaja | Detalle |
|---|---|
| **Coste** | Flat/gradiente/vertex se saltan high-poly, bake, PBR y texturas; asset game-ready en horas [ver: modelado/estilizacion-lowpoly §1] |
| **Timeless** | El look no depende de la luz/hardware del año; hand-painted y flat no "envejecen" como el realismo (§1) |
| **Esconde limitaciones** | La geometría simple y el shader barato ocultan la falta de equipo/hardware; el realismo las delata (uncanny valley) |
| **Memoria y build** | 1 paleta-atlas + 1 material pesan casi nada vs sets PBR de 2K por asset |
| **Onboarding** | Cualquier skill produce on-style con paleta-atlas/vertex; un agente IA texturiza en serie sin romper el look si los 6 parámetros (§7) están congelados |

Regla final: el realismo es "prácticamente nunca" para un equipo chico [ver: gamedev/arte-direccion §3]. La pregunta no es "estilizado o realista", es **qué punto del espectro** (§2) contra el skill 2D real y el motor.

## Reglas prácticas

1. Decide DÓNDE vive la luz (motor vs albedo) antes de tocar una textura: es la bifurcación de pipeline, no un gusto (§1).
2. Ubica el asset en el espectro (full hand-painted → sin-textura) según el skill 2D REAL; es parámetro del encargo, no decisión por asset (§2).
3. Hand-painted ⇒ shader que NO re-ilumine (Unlit/Baked Lit); nunca metas luz pintada bajo un Lit que la vuelve a sombrear (§1, §8).
4. UVs limpias y costuras escondidas ANTES de pintar; hand-painted castiga cada seam para siempre [ver: uv-unwrapping].
5. Pinta en orden: flats → AO multiplicado → form shadow (una dirección global) → highlights y bordes cincelados → rim → variación (§3).
6. Contraste de VALOR antes que de color; el asset debe leerse en escala de grises [ver: gamedev/arte-direccion §4].
7. Bordes definidos: highlight fino en el canto iluminado, línea oscura en el opuesto — el sello del hand-painted (§3).
8. Nada de fotos pegadas: se pinta la sugerencia del material con la paleta del juego (§3).
9. Paleta maestra con hex exactos, copiados nunca re-pickeados a ojo; idealmente 1 paleta-atlas compartida (§5, §7).
10. Sin skill de pintor → salta el hand-painted: vertex colors o paleta-atlas de gradientes, el pipeline más barato (§6) [ver: pipeline-3d/receta-lowpoly-estilizado].
11. Gradient map para dar tono/mood coherente a difusas ya pintadas; paleta-atlas de gradientes para reemplazar el pintado en low-poly (§5).
12. Textura de paleta/gradiente: 128–256px, no 1K (1K ≈ 40k vértices en memoria, 80.lv); Compression None para no meter banding (§5, §9).
13. Vertex colors solo con un shader que los lea; verifícalos EN Unity, no en el viewport del DCC (§9).
14. Congela los 6 parámetros de textura (paleta, dirección de luz, densidad, texel density, bordes, rango de valor) en el style guide antes del primer asset de producción (§7).
15. Difusa/albedo = sRGB On; AO/roughness/máscara = sRGB Off; si entregas roughness, invierte a smoothness (URP: 1−roughness) (§9).
16. Objetivo 1 material para el mundo estático; material nuevo = justificación por escrito [ver: texturas-a-unity].
17. Shader más barato que logre el look: `Unlit > Baked Lit > Simple Lit > Lit` (§8) [ver: unity/rendering-urp].
18. Ningún asset se aprueba en el visor de Blender/Substance: solo en la escena visual-target de Unity con toon/outline/luz reales (§8) [ver: pipeline/arte-a-unity §10].
19. Estima el coste por el catálogo completo (assets × variantes), no por el primer asset; full hand-painted multiplica el más caro.
20. Documenta cada excepción de estilo el mismo día; excepción sin documentar = drift (§7).

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Difusa hand-painted bajo un shader Lit → doble sombra, doble AO, look sucio | Unlit/Baked Lit para hand-painted: la luz ya está pintada, el motor no debe re-iluminar (§1, §8) |
| "Estilizado = barato" y elegir full hand-painted sin pintor | Es el punto MÁS caro del espectro; sin skill 2D → flat/gradiente/vertex (§2, §10) |
| AO horneado usado como look final ("textura con AO y ya") | El AO es andamio: encima van form shadow, highlights, bordes y variación a mano (§3) |
| Pegar fotos de material sobre el modelo | Se pinta la sugerencia con la paleta del juego; una foto rompe el estilo al instante (§3) |
| Cada asset con su propia paleta "porque quedaba mejor" | Paleta maestra / atlas compartido con hex exactos; recolorear = re-skin global (§5, §7) |
| Direcciones de luz pintadas incoherentes entre props | Un vector de luz global congelado en el style guide para todo hand-painted (§7) |
| Vertex colors que importan "gris" | El Lit estándar no los lee: shader Unlit/custom que sí; verificar en Unity (§9) |
| Paleta/gradiente 1K comprimida → banding y peso | 128–256px + Compression None; 1K ≈ 40k vértices en memoria (§5, §9) |
| AO/roughness importados con sRGB On | Son datos, no color: sRGB Off; AO con sRGB On grada mal (§9) |
| Entregar roughness donde URP espera smoothness → material lavado | Invertir canal (1−roughness) o preset "Unity URP (Metallic Smoothness)" (§9) |
| Sobre-detallar "para que se vea trabajado" → muddiness | Silueta y valor > detalle; áreas de descanso; el detalle solo lee por contraste (§3) [ver: gamedev/arte-direccion §5] |
| Aprobar la textura en el visor de Substance/Blender | Solo se aprueba en la escena de Unity con el shader, outline y luz reales (§8) |
| Mezclar puntos del espectro en un mismo juego sin querer | Un punto por juego (o mezcla como código semántico documentado); auditar contra el visual target (§2) |
| Contraste construido con hue en vez de valor → asset plano | Test de escala de grises; el volumen lo hace el rango claro-oscuro (§3, §6) |
| Confundir oclusión, form shadow y cast shadow → sombras "planas" o dobles | Separar los tres oscuros: AO horneado (contactos), form shadow suave (volumen), cast shadow más dura (proyección) (§3) |
| Detalle fino pintado sobre masas de luz/sombra mal resueltas | Escalonar frecuencia: masas grandes primero, detalle fino solo en focal points al final (§3) |
| Gradient map con rampa distinta por asset → biomas incoherentes | La misma rampa para todo el bioma; recolorear = editar la rampa, no los assets (§5) |

## Fuentes

**Verificadas por WebFetch esta sesión (jul-2026):**
- **URP Lit Shader** — Unity Manual 6000.0 (`urp/lit-shader.html`) — inputs exactos: Base Map, Metallic (grayscale), Smoothness con Source `Metallic Alpha`/`Albedo Alpha`, Normal, Occlusion, Emission; jerarquía Lit/Complex Lit.
- **URP Simple Lit Shader** — Unity Manual 6000.0 (`urp/simple-lit-shader.html`) — shader ligero no-PBR para estilizado/móvil: Base, Specular, Smoothness, Normal, Emission; posición en la jerarquía de coste.
- **Texture Import Settings** — Unity Manual 6000.0/6000.2 (`class-TextureImporter.html`) — índice del importer confirmado (Texture Type, sRGB Color Texture, Filter/Compression/Max Size); detalle de canales por mapa en [ver: texturas-a-unity].
- **Elevating Gradient Texturing to a Standard Workflow in Blender** — Rayen Bahri (Saved Pixel Studio), 80 Level, abr-2026 — addon Palette Grid: tiras de gradiente, snapping de UVs, ajuste no-destructivo de hue/sat/gamma; "1K ≈ ~40.000 vértices" en memoria.

**Fuentes conocidas / sintetizadas de las bases (NO re-fetched esta sesión; docs.blender.org, polycount, Adobe y Marmoset bloquearon WebFetch aquí):**
- **Blender Manual — Texture Paint + Cycles Baking** (`sculpt_paint/texture_paint/`, `render/cycles/baking.html`) — modo de pintura 3D/2D, paint slots, bake types (AO/Normal/Combined/Diffuse), margin, Selected to Active, cage/extrusión. Operadores del esqueleto bpy (§4) son la API estable de Cycles; parámetros verificados en [ver: baking] y [ver: texturizado-blender].
- **Adobe Substance 3D Painter — docs** — bake de mesh maps (Normal, AO, Curvature, ID, Position, Thickness), fill/paint layers, máscaras, smart materials, generadores por mesh map, export con presets Unity. Precio indie **NO VERIFICADO** (~$20–25/mes, confirmar). Detalle en [ver: substance-y-alternativas].
- **Marmoset Toolbag — Baking Tutorial** — bake groups por sufijo `_high`/`_low`, cage, curvatura/AO como base de texturizado estilizado. Detalle en [ver: baking].
- **polycount wiki — Texturing / Hand Painted Textures** — referencia del gremio sobre pintar luz/sombra en la difusa.
- **Talking About Stylized Character Art** — Natacha Nielsen (Blizzard), 80.lv — luz pintada sobre AO/bent normals, silueta a distancia, sobre-detalle = muddiness (vía [ver: gamedev/arte-direccion] y [ver: modelado/estilizacion-lowpoly]).
- **Toon Shader tutorial** — Roystan (roystan.net) — cel shading: bandas por step/smoothstep, rim, specular thresholded (§8).

**Bases del propio repo sintetizadas:** [ver: modelado/estilizacion-lowpoly] (escuelas low-poly, vertex/paleta-atlas, el look se cierra en el shader), [ver: gamedev/arte-direccion] (elección de estilo, paleta, silueta, luz/valor, style guide, visual target), [ver: pipeline/arte-a-unity] (canales URP Lit, smoothness=1−roughness, aprobación en engine). Cross-refs internos de texturizado: [ver: pbr-teoria], [ver: uv-unwrapping], [ver: baking], [ver: texturizado-blender], [ver: substance-y-alternativas], [ver: atlas-trim-optimizacion], [ver: texturas-a-unity]; y [ver: pipeline-3d/receta-lowpoly-estilizado], [ver: unity/rendering-urp].
