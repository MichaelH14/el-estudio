# Addons y el ecosistema

> **Cuando cargar este archivo:** antes de instalar/activar/evaluar cualquier addon o extensión de Blender, cuando un addon falla tras actualizar Blender, o cuando haya que decidir si comprar una herramienta de pago para producir game assets.

Verificado contra Blender **5.2.0 LTS** (release 14-jul-2026, soporte hasta jul-2028) y el manual oficial 5.2. Mucho contenido web sobre addons es de la era 2.8–4.1 y **ya no aplica**: el sistema cambió por completo en 4.2.

---

## 1. El sistema de extensiones moderno (4.2+)

Desde **Blender 4.2 LTS** (16-jul-2024) los addons y themes se distribuyen como **extensiones**: un `.zip` con un manifiesto `blender_manifest.toml` + código, instalable y actualizable desde dentro de Blender. La plataforma oficial es **extensions.blender.org** — todo lo publicado ahí es **gratis y open source** (GPL), pasa por revisión de un equipo de moderación antes de publicarse.

| Concepto | Detalle |
|---|---|
| Plataforma oficial | `extensions.blender.org` — add-ons y themes, gratis, GPL, con moderación |
| UI | `Edit → Preferences → Get Extensions` (buscar/instalar/actualizar) y `Add-ons` (activar/desactivar) |
| Formatos | Extensión = `.zip` con `blender_manifest.toml` + `__init__.py` (add-on) o `.xml` (theme) |
| Repos | 1 remoto por defecto (Blender oficial, admite Access Token) + 2 locales (User/System). Se pueden añadir repos de terceros por URL |
| Namespace Python | Módulo = `bl_ext.{repo}.{id}` (ej. `bl_ext.blender_org.<id>`) — los legacy usaban solo el nombre del módulo |
| CLI | `blender --command extension build` / `validate` / instalar por línea de comandos |

**Instalar** (3 vías, nombres exactos de la UI):
1. Arrastrar la URL de instalación desde la web a Blender (drag & drop).
2. En `Get Extensions`: buscar el nombre → botón **Install**.
3. **Install from Disk** (menú desplegable arriba a la derecha, o arrastrar el `.zip`) — va a un repo Local y **no recibe updates**.

**Actualizar**: es **manual** — botón **Refresh Remote** para consultar los repos, luego **Install Available Updates** / **Update All**. El repo remoto tiene la opción **Check for Updates on Startup** (notifica en la barra de estado, no auto-instala). La versión publicada en el repo siempre se considera "la última": no hay rollback desde la UI.

**Desinstalar vs desactivar**: quitar una extensión es permanente; para pararla temporalmente, **Disable** en la pestaña Add-ons. Si un addon no activa, revisar la consola del sistema (los errores de Python salen ahí, no en la UI) — [ver: bpy-scripting].

### El manifiesto y la compatibilidad de versiones

Campos clave de `blender_manifest.toml` (manual 5.2):

- `blender_version_min` — mínima soportada (mínimo posible: `"4.2.0"`). **Obligatorio.**
- `blender_version_max` — primera versión **NO** soportada (semántica excluyente: `"5.1.0"` = funciona hasta 5.0.x). Opcional — y aquí está el dolor: si el autor no lo pone, Blender no puede saber que el addon romperá en la próxima major.
- `[permissions]` — `files`, `network`, `clipboard`, `camera`, `microphone`, cada uno con su justificación. **Son declarativos, no un sandbox**: un addon es Python arbitrario con acceso total al sistema. El acceso a red además respeta el toggle global `bpy.app.online_access` (Preferences → System → Allow Online Access).

### Legacy add-ons (los `.py` sueltos de siempre)

Siguen funcionando: `Add-ons → Install from Disk` acepta el `.py` o `.zip` clásico (con `bl_info` en vez de manifiesto). Para addons en carpeta con varios `.py` sueltos: crear `mi_carpeta/addons/`, meter el addon dentro, y registrar `mi_carpeta` en `Preferences → File Paths → Script Directories` (el subdirectorio DEBE llamarse `addons`). Muchos addons de pago (Gumroad/Superhive) aún se distribuyen así.

---

## 2. El dolor real: addons rotos por release

Blender saca 3 releases/año y las majors **rompen la API de Python**. Casos verificados:

| Release | Rotura relevante para addons |
|---|---|
| 5.0 (18-nov-2025) | `bpy.props` ya no se accede por sintaxis dict — `bpy.context.scene['cycles']` **deja de funcionar**; nuevos accessors `get_transform`/`set_transform`; themes custom de versiones viejas **no migran** (API de themes reescrita); soporte Intel Mac eliminado |
| 5.1 / 5.2 | API de Python para propiedades de modificadores de Geometry Nodes cambió; assets con GN tools deben re-guardarse; identificadores de sockets de nodos Compare/Random Value cambiaron |

Consecuencia práctica (medida el 19-jul-2026, cinco días después del release de 5.2 LTS):

- **Bool Tool** ya publicó "Adapted to Blender 5.2 LTS" (mantenimiento activo).
- **MESHmachine** y **MACHIN3tools** anuncian soporte "4.2 → 5.2".
- **DECALmachine** anunciaba "4.3 → 5.1" — aún sin puerto a 5.2.
- **Zen UV 3** fue declarado **legacy**: desarrollo y soporte concluidos, compatible "hasta 5.0"; el autor exige comprar la generación nueva (Zen UV 5) para seguir.

**Regla operativa**: tras cada release de Blender, asumir que TODO addon de pago está roto hasta que su changelog diga lo contrario. Las herramientas con más cirugía interna (raycasting, overlays con `gpu`, manejo de normals) son las que más tardan. Para producción: quedarse en la **LTS** (5.2 hasta jul-2028) y no saltar a la 5.3/6.0 el día uno — [ver: blender5-actualidad].

---

## 3. Addons integrados que activar (Blender 5.2)

Verificado sobre instalación real de 5.2.0: lo integrado (`scripts/addons_core/`) quedó reducido a: `bl_pkg` (el gestor de extensiones), `cycles`, `hydra_storm`, `io_anim_bvh`, `io_curve_svg`, `io_mesh_uv_layout`, `io_scene_fbx`, `io_scene_gltf2`, **`node_wrangler`**, `pose_library`, `rigify`, `ui_translate`, `viewport_vr_preview`.

⚠️ Cambio 4.2 clave que el contenido web viejo ignora: **LoopTools, F2, Bool Tool y Extra Objects YA NO vienen con Blender** — se movieron a extensions.blender.org. Hay que instalarlos (1 clic en Get Extensions), no solo activarlos.

### Node Wrangler (integrado — activarlo siempre)

Imprescindible para materiales y Geometry Nodes. Atajos exactos (manual 5.2):

| Atajo | Función |
|---|---|
| `Shift-W` | Menú rápido de Node Wrangler en el editor de nodos |
| `Ctrl-T` | **Add Texture Setup**: nodo de textura + Texture Coordinate + Mapping |
| `Shift-Ctrl-T` | **Add Principled Setup**: selecciona los archivos de textura (basecolor/roughness/normal…) y monta TODO el árbol PBR con Color Space correcto, detectando por nombre de archivo — clave para materiales de game assets [ver: materiales-preview] |
| `Shift-Ctrl-LMB` en un nodo | **Preview Node Output** (Shader): conecta al Material Output para previsualizar; clic repetido cicla outputs |
| `Shift-Alt-LMB` | Preview en Geometry Nodes (solo outputs Geometry) |
| `Alt-RMB` drag | **Lazy Connect**: conectar dos nodos sin apuntar a los sockets |
| `Alt-R` | Reload Images (recarga texturas re-bakeadas sin ir al Image Editor) |
| `Shift-C` | Copy Settings del nodo activo a los seleccionados |

### Los des-integrados (instalar desde extensions.blender.org)

Estado medido el 19-jul-2026:

| Extensión | Qué aporta | Estado |
|---|---|---|
| **LoopTools** (v4.7.7) | Operadores de edición sobre loops/selecciones: Bridge, Circle, Curve, Flatten, Gstretch, Loft, Relax, Space. `Edit Mode → Context Menu → LoopTools`. Circle y Relax son oro para limpiar topología [ver: modelado/topologia] | 2M descargas; **sin update en ~2 años**, "offered as is, with limited support"; compat 4.2+ declarada, funciona en 5.x |
| **F2** (v1.8.5) | Extiende la tecla `F` en Edit Mode: crear caras desde un solo vértice o edge según contexto (rellenar esquinas en cadena). Ubicación: `Editmode → F` | 384K descargas; update hace ~1 año; compat 4.2+; addon minúsculo (5 KB), poco que romper |
| **Bool Tool** (v2.1.0) | Gestión rápida de booleans: añade/gestiona/aplica modificadores Boolean y sus cutters (Brush/Auto), lista de cutters, carving interactivo. NO es un solver nuevo — usa los Boolean de Blender [ver: modificadores] | 1M descargas; **mantenimiento activo** (adaptado a 5.2 LTS el 14-jul-2026, mantenedor nickberckley) |
| **Extra Mesh Objects** (v0.4.1) | Más primitivas en `Add → Mesh` (Round Cube, Gears, Pipe Joints, etc.) | 1.1M descargas; update hace 3 meses; "limited support" |

Para el flujo hard-surface de game assets: Bool Tool + Node Wrangler + LoopTools cubren el 90% de lo que la gente compra addons para hacer — [ver: modelado/hard-surface].

---

## 4. Los famosos por categoría — precio y veredicto para GAME assets

Precios verificados en los listados **Gumroad de cada autor el 19-jul-2026** (Superhive bloquea acceso automatizado; sus precios pueden diferir). "Blender Market" ahora se llama **Superhive** (superhivemarket.com — blendermarket.com redirige).

| Addon | Categoría | Precio (Gumroad, jul-2026) | Compat declarada | Veredicto para game assets |
|---|---|---|---|---|
| **Hard Ops 26** | Hard-surface | US$19 (bundle con Boxcutter: US$37) | Listado no declara versión exacta — verificar antes de comprar | Acelera bevel/boolean workflow. ÚTIL pero no imprescindible: modificadores + Bool Tool cubren lo mismo más lento [ver: modelado/hard-surface] |
| **Boxcutter 26 "Stiletto"** | Hard-surface (corte interactivo) | US$19 | Ídem | Cortes boolean dibujando en pantalla. Cómodo para bloquear props; mismo resultado con Bool Tool + más pasos |
| **MESHmachine** | Hard-surface (fillets/normals) | US$44.99 | 4.2 → 5.2 | Fusiones y re-fillets sin subdivisión + transferencia de custom normals: MUY relevante para low-poly con shading limpio [ver: modelado/high-to-low] |
| **MACHIN3tools** | QoL general (pies, focus, align) | US$2 básico (ya NO está en GitHub — el repo desapareció); versión DeusEx: precio NO VERIFICADO | 4.2 → 5.2 | Por US$2, sí. Pero es QoL de humano (pie menus): para un agente operando por MCP/headless aporta poco |
| **DECALmachine** | Decals / trim sheets | US$54.99 | 4.3 → 5.1 (**5.2 aún no** a jul-2026) | Decals no destructivos + herramientas de atlas/export para engines. Potente PERO exige bake/atlas para llegar a Unity: flujo con fricción; para empezar, texturas normales [ver: pipeline/arte-a-unity] |
| **UVPackmaster PRO** | UV packing | US$44 | UVPM actual es v4 (docs oficiales) | El packer más eficiente (CPU/GPU). Vale la pena SOLO con atlases grandes/muchos objetos; el `Pack Islands` nativo mejoró mucho y cubre assets sueltos |
| **Zen UV** | UV workflow | v3 legacy EOL (compat hasta 5.0); Zen UV 5 actual: precio NO VERIFICADO | v3 muerta, v5 activa | Checker/unwrap/quadrify cómodos, pero es QoL de humano. El caso Zen UV 3 es el ejemplo perfecto del riesgo de comprar: EOL forzado + re-compra |
| **RetopoFlow** | Retopología | GPL: **gratis desde GitHub Releases** (v3.4.10, ene-2026; repo activo, push jul-2026); precio Superhive NO VERIFICADO | RF 3.4: "Blender 3.6 or later" (README); 5.x no declarado — probar antes | Retopo con strokes sobre high-poly. Para personajes orgánicos high→low sí; para props hard-surface la retopo manual basta [ver: modelado/organico-personajes]. OJO: no usar el zip del botón verde Code, solo Releases |
| **Auto-Rig Pro** | Rigging + export | US$50 (listado Gumroad marcado "LEGACY"; precio Superhive NO VERIFICADO) | — | EL addon de rigging para juegos: auto-rig + retarget + exportador FBX/glTF dedicado a Unity/Unreal. Si se hacen personajes animados, es de lo poco que se paga con razón; si no, Rigify (integrado) [ver: import-export] |
| **Geo-Scatter** | Scattering | US$99 | NO VERIFICADO en 5.x | Render/archviz/entornos para cinemática. Para juegos el scattering se hace EN el engine (terrain, instancing): NO comprarlo para game assets |
| Render/materiales (Physical Starlight, mats de archviz, etc.) | Render | — | — | Fuera de alcance: el look final de un juego lo da Unity/URP, no Cycles. Nada de esta categoría para el pipeline |

---

## 5. Gratis vs pago: la respuesta honesta

**Para empezar (y bastante más allá): casi todo lo cubre Blender vanilla + integrados + extensiones gratis.**

| Necesidad | Lo cubre gratis |
|---|---|
| Modelado hard-surface | Modificadores (Bevel/Boolean/Mirror) + Bool Tool + LoopTools |
| UV unwrap + packing | `UV → Unwrap`, Smart UV Project, `Pack Islands` nativo (con rotación/escala) |
| Materiales PBR rápidos | Node Wrangler (`Shift-Ctrl-T`) |
| Retopología | Snap to Face + Shrinkwrap; RetopoFlow gratis desde GitHub si hace falta |
| Rigging | Rigify (integrado) |
| Export a Unity | `io_scene_fbx` / `io_scene_gltf2` integrados [ver: import-export] |
| Primitivas extra | Extra Mesh Objects |

Comprar addons tiene sentido cuando el cuello de botella es **volumen** (decenas de assets del mismo tipo): MESHmachine para normals/fillets en serie, UVPackmaster para atlases densos, Auto-Rig Pro para varios personajes. Comprar "por si acaso" = US$50+ parados y un riesgo de compatibilidad más en cada release.

## 6. Criterios para evaluar un addon (checklist de compra)

1. **Mantenimiento**: ¿changelog con entradas en los últimos 6 meses? ¿Respondió a la última release de Blender? (Bool Tool: 5 días; DECALmachine: meses).
2. **Compatibilidad 5.x declarada por escrito** en el listado — "supports 2.8+" en la descripción es marketing viejo, no compatibilidad.
3. **No-lock-in**: ¿qué queda en el `.blend` si desinstalas? Meshes/armatures normales (Hard Ops, MESHmachine, ARP: el rig sigue funcionando, solo pierdes regeneración) = seguro. Datos propietarios u objetos que dependen del addon para evaluarse (decals sin bakear, scatters) = lock-in real: bakear/aplicar ANTES de archivar.
4. **Fuente**: extensions.blender.org (GPL, moderado, updates in-app) > Superhive/Gumroad del autor oficial (updates manuales) > cualquier otra cosa (ver riesgos).
5. **¿Es QoL de humano?** Pie menus, overlays, gizmos: irrelevantes si el que opera es un agente por `bpy`/MCP [ver: blender-mcp-operativo]. Priorizar addons que aportan **operadores/algoritmos**, no UI.
6. **¿Expone API Python?** Un addon sin operadores invocables por `bpy.ops` es casi inutilizable headless.
7. **Modelo de versiones**: ¿updates incluidos o re-compra por generación? (Zen UV 3→5: re-compra).

## 7. Riesgos

- **Addon abandonado**: sin `blender_version_max`, sigue "instalable" y falla en runtime. Los ex-integrados con "limited support" (LoopTools, F2) sobreviven porque son simples, pero nadie lo garantiza.
- **Malware**: un addon es Python con acceso total (filesystem, red); los `[permissions]` del manifiesto son informativos, NO un sandbox. Los "gratis" pirateados de addons de pago en webs de terceros son el vector clásico. Regla: solo extensions.blender.org, el canal oficial del autor, o repos GitHub del autor real (verificar cuenta: MACHIN3tools YA NO está en GitHub — un "repo oficial" que aparezca hoy sería falso).
- **Dependencia excesiva**: cada addon de pago es una pieza más que puede romper el pipeline en cada release. Si un `.blend` necesita 6 addons para abrirse limpio, el bus factor es el changelog de 6 desarrolladores.
- **Archivos entregados**: antes de archivar o pasar un `.blend` a otra máquina: aplicar modificadores dependientes de addons, bakear decals, y anotar en el archivo qué addons requiere [ver: organizacion-blend].

## 8. Dónde vive la config y cómo migra

Carpeta de usuario **por versión** (major.minor — 5.2 NO lee la de 5.1 automáticamente):

| SO | Ruta |
|---|---|
| macOS | `~/Library/Application Support/Blender/5.2/` |
| Linux | `~/.config/blender/5.2/` (o `$XDG_CONFIG_HOME/blender/5.2/`) |
| Windows | `%APPDATA%\Blender Foundation\Blender\5.2\` |

Dentro (layout oficial 5.2):

- `./config/userpref.blend` — preferencias (incluye QUÉ addons están activados y sus settings).
- `./extensions/` — repos de extensiones instaladas (`blender_org/`, locales…).
- `./scripts/addons/` — legacy add-ons instalados a mano.
- `./scripts/addons_core/` — **solo en la instalación del sistema**: los integrados.
- Env vars útiles: `BLENDER_USER_RESOURCES` (redirigir TODO el perfil — útil para tests reproducibles), `BLENDER_SYSTEM_EXTENSIONS` (extensiones a nivel sistema). Instalación portable: carpeta `portable/` junto al ejecutable (macOS: dentro de `Blender.app/Contents/Resources`).

**Migración entre versiones**: al primer arranque de una versión nueva, Blender ofrece importar la configuración de la anterior (copia preferencias y addons instalados a la carpeta nueva). Los legacy addons copiados pueden no funcionar en la versión nueva; las extensiones se re-validan contra su `blender_version_min/max`. Los themes NO sobrevivieron el salto 4.x→5.0 (API reescrita). Tras migrar: `Get Extensions → Refresh Remote → Install Available Updates`.

### Patrones bpy (headless / MCP)

```python
import addon_utils, bpy

# Inventario real: qué módulos existen y cuáles están activados
for mod in addon_utils.modules():
    enabled, loaded = addon_utils.check(mod.__name__)
    print(mod.__name__, enabled)

# Activar un integrado (persistir con save_userpref si se quiere permanente)
bpy.ops.preferences.addon_enable(module="node_wrangler")

# Activar una extensión: el módulo lleva namespace bl_ext.{repo}.{id}
# (el id exacto sale del inventario de arriba, NO adivinarlo)
# bpy.ops.preferences.addon_enable(module="bl_ext.blender_org.<id>")
bpy.ops.wm.save_userpref()
```

Validar/empaquetar una extensión propia desde terminal: `blender --command extension validate` y `blender --command extension build` (en el directorio del manifiesto).

---

## Reglas practicas

- [ ] Trabajar en la **LTS** (5.2 hasta jul-2028); no saltar de major el día del release: los addons tardan semanas/meses en portarse.
- [ ] Activar `node_wrangler` siempre; instalar desde extensions.blender.org: **Bool Tool, LoopTools, F2, Extra Mesh Objects** (ya NO vienen integrados desde 4.2).
- [ ] Antes de comprar nada: comprobar que el flujo no se cubre con vanilla + integrados (casi siempre se cubre).
- [ ] Antes de comprar algo: exigir compat 5.x **por escrito** en el listado + changelog activo + qué pasa con los archivos sin el addon.
- [ ] Instalar SOLO desde: extensions.blender.org, canal oficial del autor (Superhive/Gumroad), o GitHub verificado del autor. Nunca "versiones gratis" de addons de pago.
- [ ] Tras instalar/activar: verificar en consola que no hubo traceback, y con `addon_utils.check()` que quedó enabled.
- [ ] `Install from Disk` no recibe updates: anotar versión instalada y revisar el canal del autor tras cada release de Blender.
- [ ] Updates de extensiones son manuales: `Refresh Remote → Install Available Updates` como rutina tras cada upgrade de Blender.
- [ ] Al migrar de versión de Blender: importar settings en el primer arranque, actualizar extensiones, y probar los addons de pago UNO a uno antes de trabajar en serio.
- [ ] Los `[permissions]` del manifiesto no son sandbox: tratar cada addon como código con acceso total.
- [ ] Antes de archivar/entregar un `.blend`: aplicar/bakear todo lo que dependa de un addon (decals, fillets paramétricos, scatters).
- [ ] Para operar por MCP/headless: preferir addons con operadores `bpy.ops` documentados; los de pie menus/gizmos no aportan [ver: blender-mcp-operativo].
- [ ] El id de módulo de una extensión es `bl_ext.{repo}.{id}` — obtenerlo enumerando `addon_utils.modules()`, no adivinarlo.
- [ ] Precios y compatibilidad caducan: re-verificar en el listado del autor antes de recomendar compra (los de este archivo son de jul-2026).
- [ ] Scattering, render fancy y archviz: resolver en Unity, no comprar addons de Blender para eso [ver: pipeline/arte-a-unity].

## Errores comunes

| Error | Antídoto |
|---|---|
| "Activo LoopTools en Preferences" y no aparece | Desde 4.2 no viene con Blender: hay que **instalarlo** desde Get Extensions primero |
| Buscar tutoriales/addons con instrucciones "User Preferences → Add-ons → Install Add-on from File" (2.8–4.1) | El flujo actual es `Get Extensions` + `Install from Disk`; la terminología vieja no existe en 5.2 |
| Instalar el zip del botón verde "Code" de GitHub (RetopoFlow y similares) | Usar SOLO los zips de GitHub **Releases** o del marketplace: el auto-zip de GitHub tiene estructura que Blender no acepta |
| Asumir que "compatible 4.2+" implica que funciona en 5.x | `blender_version_min` solo fija el mínimo; sin `blender_version_max` la rotura aparece en runtime. Ver changelog del addon para 5.x |
| `bpy.context.scene['cycles']` u otros accesos dict a `bpy.props` en scripts/addons viejos | Roto desde 5.0: usar las propiedades tipadas (`scene.cycles...`) o `bl_system_properties_get()` |
| Importar un addon de pago por su nombre de módulo legacy tras instalarlo como extensión | El módulo ahora es `bl_ext.{repo}.{id}`; enumerar con `addon_utils.modules()` |
| Migrar de versión y dar por hecho que los themes custom siguen | En 5.0 la API de themes se reescribió: los themes viejos no se migran — reinstalar desde extensions.blender.org |
| Comprar Geo-Scatter/addons de render para un pipeline de juego | Son para render/archviz; el equivalente de juego vive en el engine |
| Confiar en que el addon "auto-actualiza" | No existe auto-update: solo notificación opcional al arranque; actualizar es acción manual |
| Entregar un `.blend` con decals/fillets sin bakear "porque en mi máquina se ve bien" | Sin el addon instalado, la otra máquina no evalúa esos datos: bakear/aplicar antes de entregar |

## Fuentes

- **Get Extensions / Add-ons — Blender 5.2 Manual** — docs.blender.org (Preferences) — flujo exacto de instalación, updates, repos y legacy add-ons en 5.2.
- **Extensions / Getting Started — Blender 5.2 Manual** — docs.blender.org (Advanced) — `blender_manifest.toml`, `blender_version_min/max`, permissions, CLI build/validate, moderación de la plataforma.
- **Blender's Directory Layout — Blender 5.2 Manual** — docs.blender.org — rutas por SO, `extensions/`, `scripts/addons`, `addons_core`, env vars, portable.
- **Node Wrangler — Blender 5.2 Manual** — docs.blender.org — atajos exactos verificados (Shift-W, Ctrl-T, Shift-Ctrl-T, previews).
- **Release notes 4.2 (Extensions), 5.0 (+Python API), 5.2** — developer.blender.org — fechas de release, plataforma de extensiones, breaking changes de Python/themes en 5.0, cambios de compat en 5.2.
- **extensions.blender.org** — Blender Foundation — páginas de Bool Tool, LoopTools, F2, Extra Mesh Objects: versiones, fechas de update, descargas, compatibilidad ("part of Blender 4.1 bundled add-ons").
- **Instalación local Blender 5.2.0 LTS** — verificación de primera mano — listado real de `scripts/addons_core/` y `addon_utils.modules()` en 5.2.
- **Listados Gumroad oficiales (19-jul-2026)** — machin3 (MESHmachine $44.99, DECALmachine $54.99, MACHIN3tools $2), masterxeon1001 (Hard Ops $19, Boxcutter $19, bundle $37), glukoz (UVPackmaster PRO $44), artell (Auto-Rig Pro $50 "LEGACY"), bd3d (Geo-Scatter $99) — precios y rangos de compatibilidad declarados.
- **machin3.io / uvpackmaster.com / zen-masters.github.io (Zen UV)** — webs oficiales de autores — canales de venta, UVPM v4, aviso de EOL de Zen UV 3.
- **github.com/CGCookie/retopoflow** — Orange Turbine / CG Cookie — README (tabla de compat, aviso sobre zips de GitHub), release v3.4.10 (ene-2026), actividad del repo (jul-2026).
