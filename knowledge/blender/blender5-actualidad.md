# Blender 5.x y el proyecto open source: estado, versiones y ecosistema

> **Cuando cargar este archivo:** al decidir qué versión de Blender usar o si conviene actualizar, al toparte con contenido/tutoriales que no cuadran con la UI actual (mucho material web es 2.8–4.x), al reportar un bug de Blender, al evaluar addons/marketplaces/alternativas comerciales, o al recomendar recursos de aprendizaje. Versión de referencia: **Blender 5.2 LTS** (estado verificado a julio 2026 contra fuentes oficiales).

## 1. El mapa de versiones a julio 2026

Verificado contra el índice oficial de release notes (developer.blender.org) el 19-jul-2026:

| Versión | Fecha | Estado |
|---|---|---|
| 4.2 LTS | 16-jul-2024 | LTS, soporte hasta jul-2026 (recién expirado) |
| 4.5 LTS | 15-jul-2025 | **Última LTS de la serie 4.x**, soporte hasta jul-2027 |
| 5.0 "Hi Five" | 18-nov-2025 | Primera 5.x — el salto de compatibilidad |
| 5.1 "Built for Speed" | 17-mar-2026 | Release de rendimiento |
| **5.2 LTS "The Long Roar Ahead"** | **14-jul-2026** | **LTS actual, soporte hasta jul-2028 — la versión de este stack** |
| 5.3 | en desarrollo (alpha) | Mainline, no usar para producción |

- Los archivos `.blend` guardados en 5.x pueden no abrir igual (o nada) en 4.x — la compatibilidad hacia adelante no está garantizada. Congelar la versión POR PROYECTO [ver: organizacion-blend].
- Las corrective releases (5.2.1, 5.2.2…) son solo bugfixes: instalarlas sin miedo dentro de la misma serie.

## 2. Qué cambió de 4.x a 5.x (lo relevante para game assets)

Todo verificado contra las release notes oficiales de 5.0/5.1/5.2. Cuando un tutorial contradiga esto, el tutorial es viejo.

### Compatibilidad y sistema (5.0 — los breaking changes)

- **Macs Intel: soporte ELIMINADO** en 5.0. Mac = Apple Silicon (backend Metal).
- Requisitos mínimos de GPU subieron; en Cycles, NVIDIA mínimo compute capability sm_50 (~GeForce 900).
- **Collada (.dae) eliminado por completo** (import y export). Pedir siempre FBX o glTF.
- Compresión de `.blend` al guardar ahora ON por defecto; point caches LZO/LZMA fuera (ZSTD).
- Nombres de data-blocks ahora hasta 255 bytes (antes 63) — afecta convenciones de naming largas.
- **La Theme API se reescribió**: temas custom de 4.5 se rompen en 5.0 (300+ settings eliminados).

### UI (5.0–5.2)

- "Full Screen Area" ahora se llama **Focus Mode**; los editores de animación y el Sequencer ganaron footer con controles de playback; menús y popups quedan abiertos hasta click (hay preference para el comportamiento viejo).
- **MatCaps renovados con capa specular** (mejor lectura de superficies oscuras al modelar) [ver: materiales-preview]; el overlay "HDRI Preview" ahora se llama "Reference Spheres".
- El flujo general de la interfaz vive en [ver: interfaz-flujo]; aquí solo el delta.

### Viewport y backend gráfico (el estado real de Vulkan)

- 4.5 LTS declaró Vulkan "on par" con OpenGL, pero **OpenGL sigue siendo el default en Windows/Linux; Vulkan es opt-in** en `Edit ‣ Preferences ‣ System ‣ Display Graphics ‣ Backend` (requiere reiniciar). En las notas 5.0–5.2 NO aparece ningún cambio de default. macOS usa Metal siempre.
- 5.1 mejoró mucho Vulkan: arranque en frío de EEVEE ~2× más rápido y menos memoria de texturas. El display HDR/wide-gamut en Windows/Linux requiere el backend Vulkan.
- EEVEE 5.0: materiales compilan hasta 4× más rápido; instancias en viewport hasta 3× fps. Ojo scripts: **el identificador del engine cambió de `BLENDER_EEVEE_NEXT` a `BLENDER_EEVEE`** en 5.0.

### Import/Export (crítico para pipeline de juego) [ver: import-export]

| Formato | Cambio | Versión |
|---|---|---|
| FBX | **Importador C++ nuevo es el default** (llegó experimental en 4.5). Operador nuevo: `bpy.ops.wm.fbx_import`; el addon Python (`bpy.ops.import_scene.fbx`) queda como legacy | 5.0 |
| FBX | Export de normals de shape keys (arregla imports en motores de juego) | 5.1 |
| glTF | Export/import de **compresión meshopt** (`EXT_meshopt_compression`/`KHR_meshopt_compression`), point clouds, iridescence y dispersion | 5.2 |
| OBJ | Opciones nuevas: Material Name Collision ("Reference Existing" reusa materiales existentes por nombre) y Apply Transforms | 5.0 |
| USD | UVs indexadas en export (reconstrucción de islas en otras apps, 5.1); color space ligado al working space del archivo (5.2) | 5.1–5.2 |
| Collada | Eliminado | 5.0 |

### Geometry Nodes [ver: geometry-nodes]

- 5.0: **Bundles** (agrupar varios valores en un solo link, como structs) y **Closures** (inyectar comportamiento en node groups) — también disponibles en shader nodes.
- 5.0: **seis modificadores nuevos basados en GN**: Array, Scatter on Surface, Instance on Elements, Randomize Instances, Curve to Tube (genera UVs), Geometry Input. El Array legacy sigue disponible [ver: modificadores].
- 5.2: **nodo Mesh Bevel** (bevel procedural por fin), física por nodos con **solver XPBD** (Cloth Dynamics y Hair Dynamics como modificadores node-based, colliders, forces, effectors custom con tags), socket **Sound** + nodo Sample Sound Frequencies (animación audio-reactiva).

### Sculpt y paint [ver: sculpt]

- 4.3 movió los brushes al sistema de assets (Brush Assets) — los tutoriales pre-4.3 sobre gestión de brushes ya no aplican.
- 5.0: curvas de pen pressure configurables por propiedad (size/strength/jitter); los unified brush settings ahora son por modo, no por escena.
- 5.2: herramientas **Add Primitive** (Add Cube/Cone/Cylinder/UV Sphere…) directo en Sculpt Mode; brush **Scene Project** (proyecta vértices contra otras superficies, estilo Shrinkwrap); el **voxel remesher ahora interpola atributos de color** (ya no destroza el vertex paint al remeshear); Dyntopo sin diálogo de confirmación repetido.
- Baking de Multiresolution muy mejorado en 5.0: vector displacement, n-gons, bake solo a imágenes seleccionadas [ver: modelado/high-to-low].

### Modelado y UV [ver: edicion-malla]

- 5.2: operadores del addon Loop Tools ahora built-in con nombres nuevos: **"To Circle"**, **"Space Edge Loops Evenly"**, **"Flatten"**.
- 5.2 UV: operador Select by Winding, mejor Select Linked (delimit por seam/sharp/material), snapping base.
- 5.0: Boolean solver "Fast" renombrado a **"Float"** (operador, modificador y API, consistente).

### Python API (afecta scripts y MCP) [ver: bpy-scripting]

- 5.0 breaking: las propiedades definidas con `bpy.props` ya NO se almacenan junto a las custom properties — **`bpy.context.scene['cycles']` ya no funciona**. Nuevo flag `READ_ONLY` y accessors `get_transform`/`set_transform`.
- 5.2: la API de propiedades del modificador de Geometry Nodes cambió; assets con GN tools deben re-guardarse en 5.1+.
- Patrón de guard para scripts que deban correr en 4.x y 5.x:

```python
import bpy

if bpy.app.version >= (5, 0, 0):
    bpy.ops.wm.fbx_import(filepath="asset.fbx")      # importador C++ (default en 5.0+)
else:
    bpy.ops.import_scene.fbx(filepath="asset.fbx")   # addon Python legacy (4.x)
```

### Assets online (5.2 — nuevo mecanismo)

- La librería **Essentials** ahora tiene assets hospedados online (materiales paramétricos, HDRIs, setups de GN, brushes de Grease Pencil): se descargan on-demand, Blender no engorda.
- Se pueden agregar **librerías de assets remotas de terceros** en la nueva pestaña `Preferences ‣ Asset Libraries` (indexado inteligente, update con un click). Base del ecosistema de assets que viene [ver: addons-ecosistema].

## 3. Cadencia de releases y LTS: qué versión usar y cuándo actualizar

Política oficial (Developer Handbook): **3 releases estables al año** (una cada ~4 meses: nov/mar/jul) y **una LTS al año** con 2 años de bugfixes. Fases: Alpha (features nuevas, main) → Beta (solo bugfix, branch propio) → RC → release.

Lo que la política de backporting de LTS **garantiza** dentro de una serie LTS (2 años):

- El output (render) no cambia; la Python API no cambia (los scripts siguen funcionando); la compatibilidad de `.blend` no cambia; sin regresiones de rendimiento; librerías solo se actualizan por CVEs.

Decisión práctica para un estudio de juegos:

| Situación | Versión |
|---|---|
| Proyecto de assets en curso | **La LTS del proyecto (5.2 LTS)** — congelada hasta terminar |
| Proyecto nuevo | La LTS vigente (5.2 LTS, soporte hasta jul-2028) |
| Probar un feature nuevo (ej. física XPBD futura) | Mainline en paralelo, NUNCA migrando el proyecto |
| Addon crítico aún no portado a 5.x | 4.5 LTS (soportada hasta jul-2027) como puente |

**El riesgo real de actualizar es SIEMPRE los addons**: cada .0 rompe una parte del ecosistema (en 5.0 cayeron todos los temas custom y los addons que tocaban `bpy.props` internals; en 4.2 cambió el sistema entero a Extensions). Protocolo: copia del proyecto → abrir en la versión nueva → probar cada addon crítico → solo entonces migrar. Los addons legacy (`bl_info`) siguen soportados en 5.2 vía `Preferences ‣ Add-ons ‣ Install from Disk…`; los nuevos se instalan desde extensions.blender.org (`Get Extensions`) [ver: addons-ecosistema].

## 4. La Blender Foundation y por qué Blender seguirá gratis

Datos de blender.org/about y fund.blender.org (consultados 19-jul-2026):

- La **Blender Foundation** es una organización holandesa independiente sin ánimo de lucro (public benefit organization). El **Blender Institute** es su compañía operativa (desarrollo, docs, infraestructura, eventos como SIGGRAPH/GDC). Publica reportes anuales de finanzas y actividades desde 2020.
- El **Development Fund es su fuente principal de ingresos**. Números en vivo a 19-jul-2026: **~$325,955/mes**, 7,248 miembros individuales, 47 miembros corporativos. Patrocinadores corporativos actuales visibles en la página: AMD, Adobe, Google, Intel, Meta, Microsoft, NVIDIA, Qualcomm, Valve (Steam Workshop), Wacom, Netflix Animation Studios, BMW, Dell, y estudios de juegos como Arrowhead, Behaviour Interactive, Coffee Stain, Egosoft, GIANTS Software y Fireproof Games.
- **Lo que garantiza que siga gratis es la licencia, no la Foundation**: Blender es GPL v3-or-later. Nadie (ni la propia Foundation) puede cerrarlo; si el proyecto muriera, cualquiera puede hacer fork del código completo. La marca "Blender" sí es de la Foundation (trademark).
- Lo que importa a un estudio (página oficial de licencia):
  - **Todo lo que creas con Blender es 100% tuyo** — modelos, texturas, renders, los `.blend` mismos. Uso comercial sin restricción ninguna. La GPL aplica al software, no a tu output.
  - Los **addons publicados** (Python que usa la API) deben ser GPL-compliant. Se pueden VENDER (la venta restringe el acceso a la descarga, no la licencia): así funcionan los marketplaces.
  - Blender no requiere registro ni internet para funcionar.

## 5. Cómo se desarrolla y cómo participar

- Todo el desarrollo es público en **projects.blender.org** (Gitea self-hosted): repos `blender`, `blender-manual`, `extensions`, etc. Roadmap y milestones públicos.
- El código se organiza en **módulos** (Modeling, Sculpt, Animation & Rigging, Nodes & Physics, Pipeline & I/O…) con owners (deciden diseño y aprueban PRs) y members (cualquiera que contribuya activamente; sin proceso formal para unirse).
- **Reportar un bug bien** (Developer Handbook, "Making good bug reports"):
  1. Camino recomendado: `Help ‣ Report a Bug` DESDE Blender — autocompleta versión y system info. Requiere cuenta en projects.blender.org.
  2. Obligatorio: **pasos reproducibles + un `.blend` mínimo** que demuestre el problema. Elegir el repo correcto (los issues no se pueden mover entre repos): `blender` para el core, `extensions` para addons de la plataforma, `blender-manual` para docs.
  3. NO son bugs: comportamiento intencional mejorable (eso es feature request, va por otros canales), crashes por quedarse sin memoria, crashes por `.blend` corruptos.
- Contribuir sin ser programador C++: manual (canal #docs), traducciones (hay guía de traductor y equipos por idioma, español incluido), testeo de builds diarias, docs de la API. Código: pull requests en Gitea siguiendo la guía de contributing. Foros de desarrollo: devtalk.blender.org y el chat oficial (chat.blender.org).

## 6. El ecosistema alrededor

### Blender Studio (studio.blender.org)

El estudio propio de la Foundation: hace **open movies** que fuerzan a Blender a nivel producción y libera el conocimiento. Suscripción **€11.50/mes** (consultado 19-jul-2026) da acceso a todo: training, assets, archivos de producción completos de las películas.

- Películas: Singularity (2026), Wing It! (2023), Spring (2019), Hero (2018)… Nueva película larga **OVERGROWN** anunciada jul-2026.
- **DOGWALK** (jul-2025): juego corto open source del Studio, hecho con **pipeline Blender → Godot**, gratis en Steam. Referencia de primera para un estudio que produce assets de juego con Blender: los archivos de producción están publicados.
- El training cubre Geometry Nodes, rigging, shading, animación — hecho por los artistas de producción, no por youtubers.
- Herramientas del ecosistema oficial: Flamenco (render farm propia), addons del Studio publicados.

### Marketplaces y librerías de assets (precios consultados 19-jul-2026)

| Servicio | Qué es | Precio |
|---|---|---|
| **Blendkit** (antes "BlenderKit" — se renombró) | Librería de assets integrada en Blender vía addon; también integración Godot | Free: 22,565 modelos / 36,434 materiales / 4,767 HDRIs. Full $8.90/mes (78,032 modelos). El 75% va a creadores y desarrollo open source |
| **Superhive** (antes "Blender Market" — blendermarket.com redirige a superhivemarket.com) | EL marketplace de addons/assets de pago del ecosistema (aquí viven Hard Ops/Boxcutter y similares) | Por producto |
| extensions.blender.org | Plataforma OFICIAL de addons/temas gratuitos (desde 4.2) | Gratis |

### Comunidades

- **Blender Artists** (blenderartists.org): el foro histórico — WIPs, crits, soporte técnico profundo.
- **r/blender**: volumen enorme, nivel mixto; bueno para pulso del ecosistema.
- **BlenderNation** (blendernation.com): noticias diarias, addons nuevos, tutoriales curados.
- **devtalk.blender.org**: discusión de desarrollo (aquí se anuncian los breaking changes antes de que duelan).
- Blender Conference anual (Ámsterdam); presencia oficial en SIGGRAPH y GDC.

## 7. Blender vs alternativas para game art (2026, tabla honesta)

Precios verificados en la web oficial de cada uno el 19-jul-2026 salvo donde se indica.

| Herramienta | Su fuerza real | Frente a Blender | Licencia/precio |
|---|---|---|---|
| **Blender 5.2 LTS** | Generalista completo: modelado, sculpt, UV, rig, anim, bake, render, GN procedural. 100% scriptable (bpy → MCP/headless). Export glTF de referencia | — | $0, GPL, sin registro |
| **Maya** | Estándar AAA en rigging/animación; pipelines de estudio grandes lo asumen | Para un estudio chico no aporta nada que justifique el costo; su ventaja es interoperar con OTROS estudios Maya | Suscripción Autodesk (precio no verificable estático — confirmar en autodesk.com; existe licencia Indie por ingresos bajos) |
| **3ds Max** | Legado enorme en entornos/arch-viz para juegos; solo Windows | Ecosistema en declive relativo para game art nuevo; mismo modelo de suscripción | Suscripción Autodesk (ídem, confirmar en autodesk.com) |
| **Houdini** | Procedural sin rival: destrucción, VFX, scattering masivo, herramientas que se empaquetan como HDAs | Curva durísima; overkill para assets uno-a-uno. Su punto dulce: contenido procedural a escala | Indie **$299/año** (ingresos <$100K); **Houdini Engine para Unity/Unreal $0**; Apprentice gratis para aprender; Core $1,995 perpetuo workstation (sidefx.com) |
| **ZBrush** | Techo absoluto en sculpt orgánico de alto detalle (personajes AAA, decenas de millones de polys) | El Sculpt Mode de Blender cubre estilizado y mid-detail; ZBrush gana en broche fino orgánico y volumen de brushes | Suscripción Maxon (precio no verificable estático — confirmar en maxon.net) |
| **Plasticity** | Modelado CAD/NURBS para hard-surface: booleans y fillets perfectos sin pelear topología | No es DCC: sin UV/rig/anim serios — modela el sólido y el resto del pipeline se hace en Blender (trae Blender bridge) | **Indie $175 perpetuo** (12 meses de updates, uso comercial), Studio $299 (plasticity.xyz) |

**Por qué este stack elige Blender:** costo $0 con licencia que garantiza permanencia, una sola herramienta cubre TODO el pipeline de assets indie/estilizado [ver: modelado/fundamentos-3d], automatizable de punta a punta por un agente (bpy + MCP [ver: blender-mcp-operativo]), LTS con 2 años de estabilidad garantizada de API, y la comunidad/documentación más grande del 3D.

**Qué herramienta sumar después y para qué (en orden de probabilidad):**

1. **Plasticity** ($175 una vez): si el juego pide hard-surface mecánico denso (vehículos, armas, mechas) — modelar sólidos ahí, retopo/UV/bake en Blender [ver: modelado/hard-surface].
2. **Houdini Indie** ($299/año): cuando haga falta contenido procedural a escala (ciudades, destrucción, rocas por biomas) — y Houdini Engine mete los HDAs gratis en Unity [ver: pipeline/arte-a-unity].
3. **ZBrush**: solo si el estilo pivota a personajes orgánicos de alto detalle con bakes high-to-low intensivos [ver: modelado/organico-personajes].
4. Texturizado PBR dedicado (Substance Painter y equivalentes) es la adición más común en la práctica — se cubre en la base de pipeline [ver: pipeline/arte-a-unity].

## 8. Recursos canon para profundizar (por nivel)

| Nivel | Recurso | Por qué es canon |
|---|---|---|
| Referencia siempre | **Manual oficial** docs.blender.org/manual (versión 5.2) | La única fuente que siempre está al día; cada operador con su nombre exacto |
| Referencia scripting | **API docs** docs.blender.org/api/current | La verdad de bpy [ver: bpy-scripting] |
| Qué hay de nuevo | **Release notes oficiales** developer.blender.org/docs/release_notes + página de features de blender.org | El changelog canónico; leer ANTES de actualizar |
| Fundamentos guiados | **Blender Studio training** (studio.blender.org) | Cursos de los artistas de producción del Studio; parte del contenido libre |
| Fundamentos YouTube | **CG Cookie / Jonathan Lampel** (hace los recap oficiales de cada release que embebe blender.org) · **Blender Guru** (el "donut", el onboarding más famoso) | Reconocidos por la propia Foundation / la comunidad entera |
| Game assets específico | **Grant Abbitt** (low poly y game assets paso a paso) · **CG Boost** y **Polygon Runway** (estilizado; ambos miembros corporativos del Dev Fund) | Enfoque directo a assets de juego estilizados [ver: modelado/estilizacion-lowpoly] |
| Animación | **Wayne Dixon** (CG Cookie; co-hace los recaps oficiales) | Animación en Blender con criterio de producción |
| Estar al día | BlenderNation (diario) · devtalk.blender.org (cambios que vienen) | Radar del ecosistema sin ruido |

Regla de oro con tutoriales: **mirar la fecha y la versión**. UI 2.8x ≠ 4.x ≠ 5.x (temas, brushes, addons→extensions, FBX y Collada cambiaron). Si el video es pre-2024, verificar cada paso contra el manual 5.2 antes de replicarlo.

## 9. Reglas prácticas

- [ ] Producción de assets SIEMPRE en la LTS del proyecto (hoy: 5.2 LTS, soporte hasta jul-2028); mainline (5.3+) solo para probar en paralelo.
- [ ] No actualizar de versión mayor a mitad de proyecto; si hay que hacerlo: copia del proyecto → probar addons críticos → migrar.
- [ ] Corrective releases (5.2.x) se instalan siempre — solo traen fixes, la API y los `.blend` no cambian dentro de la LTS.
- [ ] Scripts multi-versión: guard con `bpy.app.version >= (5, 0, 0)`; recordar `wm.fbx_import` (5.0+) vs `import_scene.fbx` (legacy) y `BLENDER_EEVEE` (ya no `BLENDER_EEVEE_NEXT`).
- [ ] Nunca aceptar/entregar `.dae` (Collada murió en 5.0): el intercambio es FBX o glTF [ver: import-export].
- [ ] Para runtime web/móvil, evaluar glTF con meshopt compression (5.2+).
- [ ] Backend gráfico: OpenGL es el default; probar Vulkan en `Preferences ‣ System ‣ Display Graphics ‣ Backend` si el driver es moderno (mejor arranque y memoria desde 5.1); si hay glitches, volver a OpenGL y seguir trabajando.
- [ ] Habilitar la librería Essentials online (5.2) antes de fabricar materiales base a mano: puede que ya exista el material paramétrico.
- [ ] Addons: primero extensions.blender.org (oficial, gratis), después Superhive/Blendkit; legacy se instala con `Install from Disk…` [ver: addons-ecosistema].
- [ ] Reportar bugs desde `Help ‣ Report a Bug` con pasos + `.blend` mínimo; feature requests NO van al bug tracker.
- [ ] Tutorial pre-2024: verificar cada operador contra el manual 5.2 antes de seguirlo; los nombres exactos de esta base ya están verificados.
- [ ] Los assets producidos con Blender son propiedad completa del estudio (GPL solo aplica al software) — cero riesgo legal en uso comercial.
- [ ] Si se publica un addon propio del estudio, debe ser GPL-compliant (se puede vender igualmente).
- [ ] Al leer "Blender Market" o "BlenderKit" en docs/foros viejos: hoy son Superhive y Blendkit respectivamente — mismos servicios.
- [ ] Voxel remesh de mallas con vertex color: seguro desde 5.2 (interpola atributos); en 4.x destruía el paint — cuidado con instrucciones viejas.
- [ ] Si un addon crítico no está portado a 5.x, el puente es 4.5 LTS (soportada hasta jul-2027), no quedarse en versiones sin soporte.

## 10. Errores comunes

| Error | Antídoto |
|---|---|
| Buscar el botón "Install…" para addons (tutoriales 2.8–4.1) | Desde 4.2: `Get Extensions` (plataforma online) o menú desplegable `‣ Install from Disk…` para .zip legacy |
| Asumir que Vulkan ya es el default y depurar rendimiento sobre esa base | OpenGL sigue de default en Win/Linux a 5.2; verificar en `Preferences ‣ System` qué backend corre de verdad |
| `bpy.context.scene['cycles']` u otros accesos dict a props de addons | Eliminado en 5.0 — usar las propiedades tipadas (`scene.cycles.samples`) |
| Script de import FBX viejo lento o con paths de addon | En 5.0+ el importador default es C++: `bpy.ops.wm.fbx_import(filepath=...)` |
| Pedir a un cliente/artista un `.dae` "porque Blender lo abre" | Ya no: Collada se eliminó en 5.0; pedir FBX/glTF |
| Instalar un tema custom de 4.x en 5.x y creer que Blender está roto | La Theme API se reescribió en 5.0; buscar la versión 5.x del tema o migrar |
| Actualizar Blender el día que sale la .0 con el proyecto abierto | Las .0 rompen addons SIEMPRE; esperar mínimo a la .1 corrective o probar en copia |
| Creer que "gratis" implica assets con licencias raras | El output es 100% del creador (blender.org/about/license); lo GPL es el software y los addons publicados |
| Confiar en un tutorial de sculpt pre-4.3 para gestionar brushes | 4.3 movió los brushes a assets; el flujo viejo no existe |
| Reportar "me gustaría que X funcionara distinto" como bug | El tracker lo cierra: works-as-intended no es bug; proponer features va por los canales de feedback de la comunidad |
| Hair/fur de 4.5 explota memoria al abrir en 5.x | 5.0 respeta el atributo `resolution` de curves antes ignorado (~15× más geometría); bajar `resolution` o simplificar las curvas base |
| Presupuestar Maya/ZBrush "porque es lo profesional" | Para game art indie/estilizado no aportan sobre Blender 5.2; si un cuello real aparece, sumar la herramienta especializada puntual (tabla §7) |

## Fuentes

- **Release Notes index + 5.0/5.1/5.2 (Compatibility, UI, Pipeline & I/O, EEVEE & Viewport, Modeling & UV, Sculpt, Geometry Nodes, Python API, Core)** — developer.blender.org/docs/release_notes — el registro oficial de cada cambio 4.x→5.x citado aquí; consultado 19-jul-2026.
- **Páginas de features 5.0 / 5.1 / 5.2 LTS** — blender.org/download/releases/{5-0,5-1,5-2} — los headline features (color management HDR/ACES, física XPBD, Essentials online, fechas de release).
- **Blender LTS** — blender.org/download/lts — programa LTS, ventanas de soporte de 4.2/4.5.
- **Developer Handbook: Release Cycle y LTS (backporting)** — developer.blender.org/docs/handbook/release_process — cadencia 3/año, fases alpha/beta, garantías de la LTS.
- **Developer Handbook: Making good bug reports / Modules** — developer.blender.org/docs/handbook — cómo reportar bien y cómo se organiza el desarrollo.
- **Blender Foundation / Get Involved / License** — blender.org/about — naturaleza de la Foundation, GPL, propiedad del output, addons GPL, vías de contribución.
- **Blender Development Fund** — fund.blender.org — números en vivo (~$326K/mes, 7,248 individuos, 47 corporativos) y patrocinadores; consultado 19-jul-2026.
- **Blender Studio + proyecto DOGWALK** — studio.blender.org — precio de suscripción, películas, OVERGROWN, pipeline Blender→Godot de DOGWALK.
- **Manual oficial (Preferences ‣ System)** — docs.blender.org/manual — estado real del selector de Backend OpenGL/Vulkan.
- **Blendkit (ex-BlenderKit) pricing** — blenderkit.com/plans/pricing — tiers y números de assets; consultado 19-jul-2026.
- **Superhive (ex-Blender Market)** — redirect verificado blendermarket.com → superhivemarket.com; consultado 19-jul-2026.
- **SideFX — Buy Houdini** — sidefx.com/buy — precios Indie/Core/FX y Houdini Engine gratis para Unity/Unreal; consultado 19-jul-2026.
- **Plasticity** — plasticity.xyz — precios Indie/Studio y alcance del Blender bridge; consultado 19-jul-2026.
- **Blender 4.5 Release Notes (EEVEE & Viewport)** — developer.blender.org/docs/release_notes/4.5/eevee — la cita explícita "OpenGL is still the default", base del estado de Vulkan.
