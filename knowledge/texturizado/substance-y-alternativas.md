# Substance 3D Painter y el ecosistema de texturizado

> **Cuando cargar este archivo:** al decidir CON QUÉ texturizar un asset de juego (Substance vs Blender-only vs alternativas), al montar el flujo Substance (importar low+high, bakear mesh maps dentro, smart materials, export a Unity URP), al elegir/entender el export preset de Unity, al valorar coste/licencia de las herramientas, o al buscar librerías de materiales con licencia limpia. Es el archivo de DECISIÓN y FLUJO; la teoría PBR, el bake y los import settings de Unity viven en sus propios slugs y se referencian, no se repiten.

Este archivo asume que ya tienes UVs [ver: uv-unwrapping], entiendes el modelo PBR metallic/roughness [ver: pbr-teoria], y sabes qué mapas quiere Unity [ver: texturas-a-unity] y con qué spec entregas [ver: pipeline/arte-a-unity]. Aquí: **con qué herramienta pintar y cómo sacar los mapas empaquetados como Unity los pide.**

---

## 1. Por qué Substance Painter es el estándar de la industria

No es "un Photoshop 3D". Los cuatro pilares que ninguna otra herramienta junta con la misma madurez:

| Pilar | Qué es | Por qué cambia el juego |
|---|---|---|
| **Smart materials** | Materiales completos (base + capas de desgaste + máscaras) que se re-aplican a cualquier malla y **se re-calculan solos** usando los mesh maps del asset nuevo | Un "metal pintado y descascarado" se aplica a 50 props distintos y en cada uno el desgaste cae donde toca (bordes, cavidades) sin repintar |
| **Máscaras generadas por los bakes** | Los generadores (Mask Editor, Metal Edge Wear, Dirt, Curvature…) leen **curvature, AO, position, thickness, world-space normal** para poner suciedad en huecos y desgaste en filos automáticamente | El realismo "gratis": el bake alimenta las máscaras. Sin buenos mesh maps, los smart materials no funcionan → el bake DENTRO de Substance es el corazón del flujo (§3) |
| **Capas no-destructivas** | Stack de capas + máscaras + efectos + filtros, todo paramétrico y re-editable; resolución independiente del canvas hasta el export | Cambiar el color base o subir a 4K al final sin rehacer nada; iterar con el director de arte sin coste |
| **Pintado en 3D** | Se pinta sobre el modelo en el viewport (y en el 2D del UV a la vez), con proyección triplanar, stencils y partículas que respetan la superficie | Cero costuras visibles; pintar a través de seams de UV; ver el resultado con la luz real en tiempo real (viewport PBR/IBL) |

**El insight operativo:** el valor de Substance no es "pintar bonito a mano", es que **el bake de mesh maps + los generadores procedurales hacen el 80% del trabajo de realismo automáticamente.** Por eso un flujo Substance sin bakes limpios rinde peor que Blender. Y por eso, para estilos SIN ese realismo (flat, hand-painted, low-poly), Substance aporta poco (§11).

---

## 2. El flujo Substance de punta a punta

```
Blender: modelar low + high, UVs del low, exportar par _low/_high
   │
   ▼
Substance: New project (cargar low) ──► Bake Mesh Maps (contra el high)  §3
   │
   ▼
Texturizar: smart materials + máscaras generadas + pintado a mano  §4
   │
   ▼
Export Textures: preset Unity URP → mapas empaquetados  §5
   │
   ▼
Unity: material URP Lit, canales ya en su sitio  [ver: texturas-a-unity]
```

- **New Project:** cargar el **low-poly** como *Mesh* (el que llevará textura y va al juego). Template: **PBR - Metallic Roughness** (el que casa con URP metallic). Document Resolution: 2048 típico, se sube al final; el canvas es independiente del export.
- **Normal map format del proyecto:** ponerlo en **OpenGL** (`Edit ‣ Project Configuration` / al crear). Unity usa convención **OpenGL (Y+, verde hacia arriba)**; DirectX (Y−) invierte los relieves. Esto se fija aquí y se respeta al exportar (§5).
- **Low + high match:** la baja necesita UVs limpias sin solapes en UV0 [ver: uv-unwrapping]; la alta NO necesita UVs. Ambas a la misma posición/escala en el mundo.
- Preparación de la malla, UDIMs vs UV única, texel density: [ver: uv-unwrapping] · [ver: atlas-trim-optimizacion].

### Snippet: exportar el par low/high desde Blender 5.2 para bakear en Substance

Nombrar con sufijos `_low`/`_high` es lo que permite el **match por nombre** (§3) y evita que la proyección sangre entre partes. Operadores verificados contra Blender 5.2 [ver: blender/import-export]:

```python
import bpy
# Selección: objetos low nombrados "*_low", high "*_high", misma posición.
def export_sel(objs, path):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.export_scene.fbx(
        filepath=path, use_selection=True,
        apply_scale_options='FBX_SCALE_UNITS',   # File Scale 1 en cualquier consumidor
        object_types={'MESH'}, use_mesh_modifiers=True,
        mesh_smooth_type='FACE', add_leaf_bones=False)

lows  = [o for o in bpy.data.objects if o.type=='MESH' and o.name.endswith('_low')]
highs = [o for o in bpy.data.objects if o.type=='MESH' and o.name.endswith('_high')]
export_sel(lows,  bpy.path.abspath("//asset_low.fbx"))
export_sel(highs, bpy.path.abspath("//asset_high.fbx"))
```

---

## 3. Bakear los mesh maps DENTRO de Substance

Se puede bakear en Blender [ver: baking] o en Marmoset Toolbag y luego importar los mapas, PERO bakear dentro de Substance es lo estándar porque los generadores/smart-materials consumen ESOS mapas directamente y los recalculan si cambias de malla. Panel: **Texture Set Settings ‣ Mesh Maps ‣ Bake Mesh Maps** (o `Bake Mode` en la barra superior).

**Mapas que bakea Substance** (los que alimentan generadores y export):

| Mesh map | Para qué lo usan los generadores / el shader |
|---|---|
| **Normal** (tangent) | Detalle de la alta sobre la baja; va al export como normal de Unity |
| **World Space Normal** | Máscaras direccionales (polvo "de arriba"), ambient |
| **ID** (Color ID) | Seleccionar zonas por color de material/malla para asignar materiales por zona |
| **Ambient Occlusion** | Sombra en cavidades; suciedad; se exporta como Occlusion de Unity |
| **Curvature** | Filos (convexo) y grietas (cóncavo) → desgaste en bordes, mugre en huecos |
| **Position** | Gradientes por altura/posición (óxido que sube desde abajo) |
| **Thickness** | Zonas finas (translucidez, SSS, oclusión interior) |
| **Bent Normals** (opcional) | AO más preciso en iluminación |

**Parámetros de bake que importan** (nombres de la UI de Painter — pueden variar levemente por versión; verificar en tu build):

| Parámetro | Valor recomendado | Nota |
|---|---|---|
| Output Size | 2048/4096 (≥ el del export) | Bakear a resolución mayor y bajar da mejor AA |
| Antialiasing | **Subsampling 2×2 o 4×4** | Quita el escalonado de bordes en normal/AO |
| High Definition Meshes | cargar el `_high` | Si no hay alta: *Use low poly mesh as high poly* (bakea AO/curvature de la propia baja) |
| **Match** | **By Mesh Name** | La clave del flujo `_low`/`_high`: cada parte baja proyecta SOLO contra su alta homónima → cero sangrado entre piezas cercanas |
| Max Frontal / Rear Distance (o Cage) | ajustar hasta que capture sin recortar ni capturar de más | Equivale al *cage/ray distance* de Blender/Marmoset [ver: baking] |
| Average Normals / Ignore Backface | según piezas | Controla proyección en superficies duras vs suaves |
| Self Occlusion (AO) | *Only Same Mesh Name* con match por nombre | Evita que una pieza oscurezca a otra que no toca |

**El match por nombre (`_low` + `_high`) es el detalle que más falla y más se olvida.** Sin él, en un asset con muchas partes juntas (una pistola, una maleta con hebillas), la proyección de una pieza captura la geometría de la vecina → "sombras fantasma" y normales rotas. Es idéntico en Substance, Marmoset y el bake selected-to-active de Blender. Teoría y troubleshooting del bake (cage, ray distance, skew, waviness): [ver: baking].

---

## 4. Texturizar: smart materials, máscaras y capas

Flujo, no botones (los botones cambian por versión):

1. **Base con smart materials.** Arrastrar un smart material de la librería (Assets) → se aplica y usa los mesh maps del asset. Es el punto de partida, no el final.
2. **Máscaras generadas.** A una capa/carpeta, `Add mask ‣ Add generator` (Mask Editor, Metal Edge Wear, Dirt…). El generador lee curvature/AO/position → pone el efecto donde toca. Se afina con sliders (grunge amount, contrast), no pintando.
3. **Color ID.** Con el mesh map de ID, `Add mask ‣ Add color selection` → texturizar por zonas (mango de cuero vs cañón de metal) sin seleccionar a mano.
4. **Pintado a mano** solo donde el procedural no llega: logos, marcas de uso específicas, storytelling ("este arañazo cuenta algo"). Con proyección/stencils.
5. **Anchor points** para reusar una máscara/altura en otra capa (mugre que sigue el relieve pintado antes).

Estilizado y hand-painted en Substance (menos común, se suele hacer en Blender): [ver: estilizado-texturas].

---

## 5. Export: el preset de Unity URP y el empaquetado de canales

`File ‣ Export Textures` (`Ctrl+Shift+E`). El campo clave es **Output template** (Config): Substance trae presets por engine. Para Unity URP metallic, el preset es del tipo **"Unity Universal Render Pipeline (Metallic Standard)"** — *el nombre exacto varía por versión de Painter; verificar en el dropdown. No se pudo confirmar hoy contra la doc de Adobe (la página no cargó); el empaquetado de abajo SÍ está verificado contra la doc de URP Lit.*

**Qué saca el preset URP metallic y por qué así** (canales verificados contra la doc de URP Lit):

| Archivo (por texture set) | Contenido / empaquetado | Import en Unity |
|---|---|---|
| `..._BaseColor` | RGB albedo (+ A opacidad si el material es Transparent/Alpha Clip) | sRGB **On** |
| `..._MetallicSmoothness` | **R = Metallic**, **A = Smoothness** | sRGB **Off** (dato lineal) |
| `..._Occlusion` | AO en escala de grises | sRGB **Off** |
| `..._Normal` | Normal tangente **OpenGL (Y+)** | Texture Type = **Normal map** |
| `..._Emissive` (si emite) | RGB, HDR | sRGB **On**; alimenta Bloom [ver: unity/rendering-urp] |

Por qué ese empaquetado es correcto y no accidental (doc URP Lit):

- **URP Lit lee smoothness del ALPHA del Metallic Map** (propiedad *Smoothness Source = Metallic Alpha*, el default) y lo multiplica por el slider Smoothness. Por eso el metallic y el smoothness viajan en UN archivo RGBA.
- **URP usa smoothness = 1 − roughness.** Substance authorea en **roughness**; el preset de Unity **invierte** el canal al exportar y lo mete en el alpha. Si exportas roughness crudo (preset genérico) el material sale plástico/lavado al revés. Esto ya lo marca la spec de entrega [ver: pipeline/arte-a-unity §7].
- **Occlusion:** URP la lee del canal **G**. La doc de URP Lit permite **empaquetar metallic (R) + occlusion (G) + smoothness (A) en una sola textura RGBA**; el preset estándar de Adobe la saca aparte por compatibilidad, pero empaquetarla ahorra una textura si controlas el material.
- **Normal OpenGL, no DirectX.** Unity = OpenGL (Y+). Si el verde sale invertido (relieves hundidos donde deben sobresalir) es normal DirectX: cambiar el formato del proyecto/export a OpenGL, o invertir el canal verde en el import.

Otros settings del export: **File format** PNG (8-bit color/AO, 16-bit solo si hay banding en normal/height), **Size** potencia de 2 (1024/2048), **Padding/Dilation** = *Infinite* o *Dilation + transparent* (rellena fuera de las islas UV → sin costuras negras al mipmapear) [ver: uv-unwrapping] — *nombres de la opción de padding dados por conocimiento del producto: la página de Adobe "Exporting textures" volvió a dar timeout hoy (redirige a la home de helpx sin contenido), verificar el nombre exacto en el dropdown de tu build antes de automatizarlo.* Los import settings completos en Unity (ASTC móvil, Read/Write Off, sRGB por mapa, MikkTSpace) NO se repiten aquí: [ver: texturas-a-unity] · [ver: unity/assets-pipeline-git].

> Substance también trae presets **HDRP (Metallic Standard)** (mask map ORM-style: AO/Metallic/Detail/Smoothness empaquetado distinto) y **Unity 5 (Standard Metallic)** para Built-in. Para un proyecto URP, el preset URP; no mezclar con el de HDRP (empaqueta los canales en otro orden).

---

## 6. Licencia y coste a 2026

> ⚠️ **Precios: estructura verificada por conocimiento del producto; las cifras EXACTAS no se pudieron confirmar hoy contra la página de Adobe/Steam (no cargaron).** Tratar los números como orden de magnitud y confirmar en `adobe.com/products/substance3d` y `store.steampowered.com` antes de comprar. Lo que SÍ es estable es el MODELO de licencia.

| Vía de compra | Modelo | Qué incluye | Para quién |
|---|---|---|---|
| **Adobe — plan Substance 3D** (suscripción) | Recurrente mensual/anual | Painter + Designer + Sampler + Stager + librería **Substance 3D Assets** con *points* mensuales; updates continuos | Estudio o quien use varias apps y quiera lo último |
| **Adobe — plan Texturing** (suscripción, más barato) | Recurrente | Subset centrado en texturizado | Quien solo textura |
| **Steam — "Substance 3D Painter 20XX"** | **Perpetua** (compra única) | SOLO Painter, versión de ESE año; **sin** updates a la versión siguiente, **sin** los *points*/assets de Adobe | **Dev solo / freelance**: pagas una vez y es tuyo |
| **Educación** | Descuento fuerte / gratis | Según programa Adobe edu (requiere verificación de estudiante) | Estudiantes y profesores |

Claves de decisión de coste (verificadas como modelo, no como cifra):

- **La versión de Steam es perpetua pero se "congela" en su año.** Comprar "Painter 2026" te da 2026 para siempre; para tener 2027 vuelves a comprar. Para un dev solo esto suele salir MUCHO más barato que la suscripción a la larga.
- **La suscripción de Adobe da los *Substance 3D Assets* con points** (antes "Substance Source"): librería enorme de materiales/smart materials descargables. La versión Steam no.
- **Substance Designer** (crear materiales procedurales/tileables desde cero, nodos) es app aparte; para solo texturizar assets no hace falta — con Painter + librerías gratis (§8) alcanza.

---

## 7. Alternativas a Substance Painter

| Herramienta | Estado a 2026 | Licencia / coste | Veredicto para juego |
|---|---|---|---|
| **Blender Texture Paint + bake** | Nativo, activo | Gratis (GPL) | Suficiente para estilizado/hand-painted y PBR simple; sin smart-materials ni generadores por mesh-map. El "plan A" del dev solo (§11) [ver: texturizado-blender] |
| **ArmorPaint** | Activo (repo con desarrollo continuo) | **Código abierto en GitHub**; los binarios precompilados son de pago (financian el proyecto) | Pintado 3D PBR estilo Substance, más ligero y sin ecosistema de smart-materials/librería. Opción libre real si compilas o pagas el binario |
| **Quixel Mixer** | **Efectivamente descontinuado / sin desarrollo activo**; Quixel se absorbió en **Fab** (Epic, lanzado 22-oct-2024) | Era gratis | Ya NO es una apuesta de futuro. Sigue descargable pero sin soporte; no montar pipeline nuevo encima. *Estado de Mixer/Bridge: verificar en Epic/Fab; la absorción en Fab sí está confirmada* |
| **Materialize** (Bounding Box Software) | Estable | **Open source GPL v3**, gratis | NO pinta assets; **genera mapas PBR desde una sola imagen/difuso** (height→normal, difuso→metallic/smoothness/AO). Usado en Uncharted Collection. Perfecto para convertir una foto/textura plana en material tileable |
| **Substance 3D Sampler** | Activo (Adobe) | Suscripción/Steam (aparte de Painter) | Foto/scan → material tileable, *delighting*, y generación por IA (§10). Complemento, no reemplazo de Painter |

Materiales tileables procedurales desde nodos (no pintar assets): **Substance Designer** (pago) o **Material Maker** (open source, gratis) — pertenecen al mundo "crear la textura", no "texturizar el modelo".

---

## 8. Librerías de materiales: dónde sacar texturas con licencia limpia

No todo se pinta desde cero. Materiales base y tileables de librería aceleran muchísimo — pero **la licencia manda** (repo público, hay que poder redistribuir el juego):

| Fuente | Contenido | Licencia (verificada) | Uso |
|---|---|---|---|
| **Poly Haven** | Texturas PBR, HDRIs, modelos | **CC0** — uso comercial, sin atribución, redistribuible | Base de materiales tileables y HDRIs para iluminar el viewport/lookdev. La más limpia |
| **ambientCG** | Materiales PBR, HDRIs, modelos | **CC0** — comercial, sin atribución | Enorme catálogo de superficies tileables (metal, roca, tela, suelo) |
| **Substance 3D Assets** (ex-Substance Source) | Smart materials + materiales `.sbsar` paramétricos | Incluida en suscripción Adobe (con points); licencia Adobe | Solo si estás en la suscripción; se consumen dentro de Painter |
| **Otras (itch.io, cc0textures mirrors, texturas.com)** | Variado | **Leer CADA licencia** — muchas NO son CC0 ni permiten redistribución en juego | Verificar antes de meter al repo; si dice "no redistribution", fuera |

Regla dura para repo público/comercial: **CC0 o licencia comercial con redistribución explícita, y guardar el archivo de licencia junto al asset.** "Free" no es una licencia. Ante duda → Poly Haven / ambientCG (ambas CC0) y listo.

---

## 9. Tileable / trim sheets vs unique bake: cuándo cada uno

El error caro es texturizar TODO como asset único (bake individual por objeto). El entorno de un juego se construye en su mayoría con **materiales tileables y trim sheets**, no con bakes únicos. Decisión:

| Situación | Enfoque de textura | Por qué |
|---|---|---|
| Superficies grandes y repetidas (suelos, muros, terreno, paneles de nave, tela) | **Material tileable** (Poly Haven/ambientCG o Substance Designer) | Un material de 1–2K cubre kilómetros; el detalle no depende del tamaño del objeto |
| Kits modulares / arquitectura / props duros con detalle repetido (tubos, tornillos, molduras, bordes) | **Trim sheet** (una tira de detalles mapeada a muchas mallas) | Decenas de mallas comparten UNA textura; se re-usa el mismo strip; ahorro brutal de memoria y draw calls [ver: atlas-trim-optimizacion] |
| Props "hero", personajes, armas, cualquier cosa donde cada texel se authorea | **Unique bake** (low+high → mesh maps → Substance) | El detalle es específico e irrepetible; aquí SÍ el flujo Substance completo (§2–5) |
| Objeto con partes hero + partes genéricas | **Mixto**: hero en unique bake, resto en trim/tileable | Presupuesto de texel density donde importa [ver: uv-unwrapping] |

- El trim sheet **se authorea una vez** (puede pintarse/bakearse en Substance como material único) y luego en Blender se mapean muchas mallas a esa tira [ver: modelado/props-armas] · [ver: atlas-trim-optimizacion].
- Substance también texturiza tileables (modo con *tiling* activado), pero para tileables procedurales puros Designer/Material Maker/librerías CC0 suelen ser mejor herramienta.

---

## 10. Photogrammetry / scans e IA generativa (concepto y licencias)

Nivel concepto — cuándo mirar por aquí y qué mirar de las licencias:

**Photogrammetry / scans:**
- Flujo: fotos → nube de puntos + malla alta + albedo (**RealityCapture** — gratis vía Epic/Fab; **Metashape**; **Meshroom** — open source AGPL). Da un high-poly con color que luego se **retopologiza + bakea a game-res** por el mismo flujo del §2–5.
- **Delighting obligatorio:** el albedo escaneado trae la luz del día horneada; hay que quitarla (Substance Sampler tiene *delighting*) o el asset se ve mal bajo la luz del juego.
- **Licencias:** el scan que TÚ capturas es tuyo, pero cuidado con sujetos **con marca/logo, obras de arte con copyright, o propiedad/localización privada**. Librerías de scans (Megascans en Fab, Poly Haven scans CC0) traen su licencia — usar esa.

**IA generativa de texturas:**
- Herramientas: **Substance 3D Sampler** (text-to-texture / image-to-material, basado en Adobe **Firefly**), plus varias basadas en Stable Diffusion (p.ej. *Dream Textures* en Blender).
- **Licencia = el punto crítico, no la calidad.** Adobe Firefly se entrena con Adobe Stock + contenido licenciado/dominio público y Adobe declara uso comercial seguro (con indemnización para planes elegibles) — *verificar los términos vigentes de tu plan*. Las basadas en Stable Diffusion tienen estatus legal/comercial **más turbio** (datos de entrenamiento) → verificar la licencia de CADA herramienta antes de meter el resultado en un juego que vendes.
- **Nivel de uso realista a 2026:** buena para **material base / variación tileable / lookdev rápido**, todavía floja para hero assets sin limpieza manual. Trátala como generador de punto de partida, no como entregable final.

---

## 11. La decisión honesta para un dev solo: Blender-only vs Blender+Substance

No hay respuesta única; depende de **estilo y presupuesto**, no de "cuál es mejor":

| Tu juego es… | Herramienta | Razón |
|---|---|---|
| Estilizado / low-poly / flat / cel / hand-painted / gradient-atlas | **Blender-only** (vertex colors, palette atlas, Texture Paint) | Substance aporta casi nada: no hay desgaste PBR que los generadores automaticen. Ahorras dinero y una herramienta [ver: estilizado-texturas] · [ver: texturizado-blender] |
| Realista PBR con desgaste, suciedad, muchos props/personajes hero | **Blender + Substance** | Aquí Substance se paga solo: smart materials + máscaras por mesh-map hacen el 80% del realismo. Blender puede bakear PBR pero sin ese ecosistema es mucho más lento |
| Realista pero pocos assets y presupuesto CERO | **Blender bake + hand-paint roughness/metallic + librerías CC0** | Viable con esfuerzo; añade Substance (Steam perpetua, pago único) cuando el volumen o el realismo lo justifiquen |
| Mixto / no lo tienes claro aún | Empieza **Blender-only**, mete Substance cuando DUELA | No compres herramienta antes de tener el cuello de botella. El estilo decide, y el estilo se congela en el style guide [ver: gamedev/arte-direccion] |

**Regla de coste:** Blender es gratis; Substance **Steam perpetua** (pago único por año-versión) es la vía sensata del dev solo si va a texturizar realista de forma continua; la **suscripción** solo si necesitas Designer/Sampler/assets o updates al día. Nunca compres la suscripción "por si acaso".

---

## Reglas prácticas

1. Substance se justifica por el **bake + generadores**, no por "pintar a mano": estilo sin desgaste PBR → Blender-only, no gastes en Substance.
2. Proyecto Substance en **Normal = OpenGL (Y+)** desde el inicio: Unity es OpenGL; DirectX invierte los relieves.
3. Modela low + high, exporta con sufijos **`_low` / `_high`** y bakea con **Match = By Mesh Name**: sin eso, sangrado de proyección entre piezas.
4. Bakea a resolución ≥ export con **Antialiasing (subsampling)**; ajusta cage/max distance hasta capturar sin recortar [ver: baking].
5. Texturiza en orden: smart material base → máscaras **generadas** (curvature/AO) → color ID por zonas → pintado a mano solo lo específico.
6. Exporta con el **preset Unity URP metallic**, no un preset genérico: empaqueta Metallic(R)+Smoothness(A) e **invierte roughness→smoothness**.
7. Verifica el nombre exacto del preset URP en tu versión de Painter (varía); no asumas — míralo en el dropdown de Output template.
8. **Normal OpenGL** al export; si el verde sale invertido en Unity, era DirectX → corregir en export o invertir el canal verde en el import.
9. Padding/Dilation **Infinite** al exportar → sin costuras negras al mipmapear (nombre de la opción sin verificar hoy contra la doc de Adobe; confirma en el dropdown de tu build).
10. Import settings de Unity (sRGB por mapa, ASTC móvil, Normal type, Read/Write Off) NO se tocan aquí: pásalo por el AssetPostprocessor del proyecto [ver: texturas-a-unity].
11. No textures TODO como unique bake: superficies grandes y kits → **tileable / trim sheet**; unique bake solo para hero [ver: atlas-trim-optimizacion] · [ver: modelado/props-armas].
12. Librerías: **Poly Haven y ambientCG son CC0** (comercial, sin atribución) → default seguro; cualquier otra, leer y archivar la licencia antes de meterla al repo.
13. Scans: retopo + bake a game-res y **delighting** obligatorio; ojo con marcas/copyright del sujeto.
14. IA de texturas: verifica la **licencia comercial** de la herramienta (Firefly ≠ Stable Diffusion en estatus legal); úsala como base, no como entregable.
15. Coste dev solo: Blender gratis; Substance **Steam perpetua** > suscripción salvo que necesites Designer/Sampler/assets. Confirma precios en la web oficial (no los inventes).
16. El asset se aprueba en Unity con la luz real, no en el viewport de Painter [ver: pipeline/arte-a-unity §10].

## Errores comunes

| Pitfall | Síntoma | Antídoto |
|---|---|---|
| Bakear sin match por nombre en asset multi-parte | Sombras fantasma, normales rotas donde dos piezas se acercan | `_low`/`_high` + **Match = By Mesh Name** + Self Occlusion "Only Same Mesh Name" |
| Exportar con preset genérico (PBR Metallic Roughness) a Unity | Material lavado/plástico; rugosidad al revés | Preset **Unity URP metallic**: invierte roughness→smoothness en el alpha del MetallicSmoothness |
| Normal DirectX en Unity | Relieves hundidos donde deben sobresalir (verde invertido) | Proyecto/export en **OpenGL (Y+)**; o invertir canal verde en el import |
| Confiar en smart materials sin buenos mesh maps | El desgaste no cae en bordes/cavidades; se ve plano | Los generadores leen curvature/AO/position: **primero bakear bien**, luego texturizar |
| Sin padding/dilation al exportar | Costuras negras en las UV al alejarse (mipmaps) | Dilation **Infinite** en el export |
| Texturizar todo como unique bake | Memoria y draw calls disparados en el entorno | Tileables/trim sheets para lo repetido; unique solo hero [ver: atlas-trim-optimizacion] |
| Meter texturas "gratis" de cualquier sitio al repo | Riesgo legal en juego comercial | Solo CC0/comercial-redistribuible; Poly Haven/ambientCG por defecto; archivar licencia |
| Albedo de scan sin delighting | Luz del día horneada; se ve mal bajo la luz del juego | Delighting (Substance Sampler) antes de usar el color |
| IA generativa como entregable final | Calidad hero insuficiente + licencia dudosa | Base/lookdev sí; limpiar a mano; verificar licencia comercial de la herramienta |
| Comprar la suscripción Adobe "por si acaso" | Gasto recurrente que no usas | Dev solo realista → Steam perpetua; estilizado → Blender-only |
| Asumir el nombre/canales del preset URP de memoria | Canales en el slot equivocado | Verificar el preset en el dropdown de tu versión; contrastar canales contra URP Lit |

## Fuentes

- **URP Lit Shader** — Unity Manual 6000.0 (`urp/lit-shader.html`) — verificado: Smoothness Source = *Metallic Alpha* (default) vs *Albedo Alpha*; metallic+smoothness+occlusion empaquetables en una sola RGBA; Unity multiplica los valores de textura por el slider Smoothness. (La equivalencia smoothness = 1 − roughness la fija la base de entrega.)
- **Poly Haven — Asset License** (`polyhaven.com/license`) — verificado: **CC0**, uso comercial, sin atribución, redistribuible.
- **ambientCG** (`ambientcg.com`) — verificado: todos los assets bajo **CC0**, sin atribución, uso comercial.
- **Materialize — Bounding Box Software** (`boundingboxsoftware.com/materialize`) — verificado: **open source GPL v3**, genera mapas PBR (height/normal/metallic/smoothness/AO) desde una imagen; usado en Uncharted Collection.
- **ArmorPaint — GitHub** (`github.com/armory3d/armorpaint`) — verificado: pintado 3D PBR; **código abierto**, binarios de pago para financiar; desarrollo activo.
- **Quixel — Wikipedia** — verificado: Epic adquirió Quixel (nov-2019); **Fab** lanzado 22-oct-2024 unifica los assets de Quixel. (Estado detallado de Mixer/Bridge: no confirmado hoy — marcar como "verificar".)
- **NO cargaron hoy (marcadas para re-verificar):** Adobe Substance 3D Painter — *Baking* y *Exporting textures* (`helpx.adobe.com/substance-3d-painter` y `substance3d.adobe.com/documentation/spdoc/...`, ambas redirigen a la home de helpx sin contenido; re-intentado en esta revisión con el mismo resultado), Adobe pricing, Marmoset Toolbag baking, Blender Cycles baking (docs.blender.org 403). Los nombres de preset de Painter, los nombres exactos de las opciones de Padding/Dilation, y las cifras de precio de §6 se dan por conocimiento del producto, explícitamente sin verificación de fuente hoy.
- **Verificado en esta revisión (2026-07-20) vía WebFetch:** Unity Manual 6000.0 `urp/lit-shader.html` — Smoothness Source = *Metallic Alpha* (default) confirmado; Unity Manual `urp/shaders-in-universalrp-channel-packed-texture.html` — confirma textualmente el empaquetado **Red = Metallic, Green = Occlusion, Blue = Not used, Alpha = Smoothness**; Unity Manual `StandardShaderMaterialParameterNormalMap.html` — confirma convención **OpenGL Y+** para normal maps; GitHub `armory3d/armorpaint` — confirma código abierto + binarios de pago; GitHub `BoundingBoxSoftware/Materialize` — confirma licencia **GPL-3.0**.
- **Bases sintetizadas:** [ver: blender/import-export] (export FBX, `export_scene.fbx` verificado en 5.2, escala/normales) y [ver: pipeline/arte-a-unity] (canales exactos URP Lit, smoothness = 1 − roughness, spec de texturas, texel density, aprobación en el juego).
- **Cross-refs internos (no re-explicados aquí):** [ver: uv-unwrapping] · [ver: pbr-teoria] · [ver: baking] · [ver: texturizado-blender] · [ver: estilizado-texturas] · [ver: atlas-trim-optimizacion] · [ver: texturas-a-unity] · [ver: modelado/props-armas] · [ver: unity/assets-pipeline-git] · [ver: unity/rendering-urp] · [ver: gamedev/arte-direccion].
