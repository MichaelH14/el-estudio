# Operar Blender via MCP (agente IA)

> **Cuando cargar este archivo:** siempre que vayas a operar un Blender vivo a través del servidor MCP "blender" (blender-mcp) — crear/editar assets, consultar la escena, tomar screenshots — o a decidir entre MCP interactivo y `blender --background` para batch. Es el manual operativo de LA HERRAMIENTA.

Verificado contra el repo oficial **ahujasid/blender-mcp** (README + `addon.py` + `src/blender_mcp/server.py`, julio 2026) y contra docs oficiales de **Blender 5.2 LTS** (manual y API `docs.blender.org`). Stack objetivo: Blender 5.x con el addon "Blender MCP" habilitado + servidor MCP registrado en el cliente (Claude Code) via `uvx blender-mcp`. La teoría de modelado es agnóstica y vive en su base [ver: modelado/fundamentos-3d]; aquí solo cómo operar.

---

## 1. Arquitectura: dos piezas y un socket

| Pieza | Dónde corre | Qué hace |
|---|---|---|
| **Addon `addon.py`** ("Blender MCP") | DENTRO de Blender | Abre un socket TCP en `localhost:9876` (configurable) y ejecuta los comandos recibidos |
| **Servidor MCP** (`uvx blender-mcp`, Python ≥3.10) | Proceso aparte, lo lanza el cliente MCP | Habla Model Context Protocol con el agente y traduce cada tool a un comando JSON hacia el socket |

Datos duros (leídos del código real):

- Protocolo: **JSON sobre TCP** — comando `{type, params}` → respuesta `{status, result|message}`.
- El socket hace `listen(1)`: **un cliente a la vez**. No conectar dos agentes al mismo Blender.
- Cada comando se ejecuta **en el main thread de Blender** via `bpy.app.timers.register(...)`. Consecuencia: mientras tu código corre, la UI de Blender está congelada; un `while True` o una operación eterna **cuelga Blender entero**.
- Timeout de socket: **180 s** en ambos lados. Operación más larga que eso = timeout aunque Blender la termine.
- **Sin Blender abierto con el socket activo NO hay conexión.** El servidor MCP solo es un puente; si el addon no está escuchando, toda tool devuelve error de conexión.
- El addon **se niega a arrancar en `blender --background`** (mensaje literal del código: "cannot start server in background mode (blender -b) - commands would never execute"; sugiere `xvfb-run -a blender` en Linux sin display). MCP = Blender con GUI, siempre.

## 2. Setup del stack (ya instalado — cómo se ve cuando está bien)

1. **Addon**: `addon.py` es un add-on *legacy* (no Extension). En Blender 4.2+/5.x se instala por `Edit ‣ Preferences ‣ Add-ons ‣` menú desplegable `‣ Install from Disk…` (el botón "Install…" de los tutoriales 2.8–4.1 ya no existe: en 4.2 los add-ons se separaron en Extensions y legacy). Habilitar el checkbox **"Blender MCP"**. Los add-ons legacy con `bl_info` siguen soportados en 5.2 (el manual 5.2 mantiene "Installing Legacy Add-ons").
2. **Cliente**: registro en Claude Code según el README oficial: `claude mcp add blender uvx blender-mcp`. En clientes con config JSON: `{"command": "uvx", "args": ["blender-mcp"]}`.
3. Gotchas de instalación documentados en el README:
   - `spawn uvx ENOENT`: clientes GUI no heredan el PATH de la terminal → usar la ruta completa de `uvx` (`which uvx`).
   - Conflictos de Python (conda/pyenv): pinear con `"args": ["--python", "3.11", "blender-mcp"]` + `UV_PYTHON_PREFERENCE=only-managed`.
   - **NO correr `uvx blender-mcp` a mano en una terminal**: lo lanza el cliente MCP. Correrlo aparte crea un segundo proceso que compite por el socket.
4. Credenciales de integraciones (si se usan): en `Edit ‣ Preferences ‣ Add-ons ‣ Blender MCP` (persisten entre reinicios) o por env vars `BLENDERMCP_SKETCHFAB_API_KEY`, `BLENDERMCP_HYPER3D_API_KEY`, `BLENDERMCP_HUNYUAN3D_SECRET_ID/SECRET_KEY/API_URL`. Telemetría anónima: se apaga en preferencias o con `DISABLE_TELEMETRY=true`.
5. Host/puerto no estándar: env vars `BLENDER_HOST` / `BLENDER_PORT` en el lado del servidor MCP.

## 3. Arrancar la conexión

- **Versión actual del addon: auto-start.** Al registrarse (Blender abre con el addon habilitado), levanta el socket solo — propiedad `blendermcp_auto_start_server`, default `True`. Abrir Blender normal ya deja todo listo.
- **Manual / versiones viejas**: en el 3D Viewport, sidebar (tecla `N`) → pestaña **BlenderMCP** → panel "Blender MCP": campo **Port** (default 9876), checkbox **"Use assets from Poly Haven"**, botón **"Connect to MCP server"** / **"Disconnect from MCP server"** (muestra "Running on port 9876" cuando corre).
- **Por código** (p. ej. en un script de arranque): `bpy.ops.blendermcp.start_server()` / `bpy.ops.blendermcp.stop_server()`.
- Automatizar el arranque completo = abrir Blender **con GUI** (app normal o `blender archivo.blend` desde terminal); el auto-start hace el resto. En un servidor Linux sin display: `xvfb-run -a blender`.
- Troubleshooting oficial: a veces el **primer** comando tras conectar falla y el segundo entra; si sigue fallando, reiniciar los dos lados (Blender y el cliente MCP).

## 4. Catálogo de herramientas del MCP

Núcleo (siempre disponibles):

| Tool | Qué hace | Límite clave |
|---|---|---|
| `get_scene_info` | Nombre de escena, `object_count`, `materials_count`, lista de objetos | **Solo los primeros 10 objetos** — en escenas grandes, consultar por código |
| `get_object_info(object_name)` | name, type, location, rotation, scale, visible, materiales, y en MESH: conteos de mesh + `world_bounding_box` (AABB en mundo) | Un objeto por llamada, por nombre exacto |
| `get_viewport_screenshot(max_size)` | Captura el viewport 3D activo (`bpy.ops.screen.screenshot_area` con `temp_override` del área VIEW_3D) y devuelve la imagen al agente | Requiere UI real con un área VIEW_3D; captura overlays/gizmos tal cual se ven; `max_size` default 1000 px — más grande = más tokens y latencia |
| `execute_blender_code(code)` | **LA herramienta.** `exec()` del código en namespace `{"bpy": bpy}` | El resultado es **solo el stdout capturado**: sin `print()` no vuelve nada. Excepción → error. 180 s máximo |

Integraciones de assets (cada familia tiene su `get_*_status` — **llamarlo antes de asumir que está activa**; por defecto vienen apagadas):

| Familia | Tools | Notas |
|---|---|---|
| **Poly Haven** (librería CC0) | `get_polyhaven_status`, `get_polyhaven_categories`, `search_polyhaven_assets`, `download_polyhaven_asset` (asset_type: `models` / `textures` / `hdris`), `set_texture` (aplica una textura ya bajada a un objeto) | Checkbox en el panel del addon; descarga a disco; bueno para genéricos + HDRIs de iluminación |
| **Sketchfab** | `get_sketchfab_status`, `search_sketchfab_models`, `get_sketchfab_model_preview`, `download_sketchfab_model` (por UID) | Requiere API key; **solo modelos marcados downloadable**; más variedad que Poly Haven para temas específicos |
| **Hyper3D Rodin** (gen. IA) | `get_hyper3d_status`, `generate_hyper3d_model_via_text`, `generate_hyper3d_model_via_images`, `poll_rodin_job_status`, `import_generated_asset` (GLB) | Key free-trial con límite diario de generaciones; keys propias en hyper3d.ai / fal.ai. Solo ítems sueltos: no escenas completas, no terrenos, no piezas para ensamblar |
| **Hunyuan3D** (gen. IA) | `get_hunyuan3d_status`, `generate_hunyuan3d_model`, `poll_hunyuan_job_status`, `import_generated_asset_hunyuan` (OBJ) | Modo `OFFICIAL_API` (SecretId/Key de Tencent) o `LOCAL_API`. Mismas restricciones que Rodin |

El servidor también expone el prompt MCP `asset_creation_strategy`: su orden oficial de prioridad de fuentes es — específico existente → Sketchfab, luego Poly Haven; genérico → Poly Haven, luego Sketchfab; único/custom → Rodin/Hunyuan; iluminación → HDRIs de Poly Haven; y **modelar por código solo cuando ninguna integración aplica o piden un primitivo simple**. Tras CUALQUIER import: leer `world_bounding_box` y ajustar location/scale/rotation — los assets llegan con escala y posición arbitrarias [ver: import-export].

## 5. El flujo correcto del agente (el bucle sagrado)

```text
1. get_scene_info                    → SIEMPRE al empezar: qué hay, cómo se llama
2. get_viewport_screenshot           → estado ANTES, si el cambio es visual
3. execute_blender_code (chico)      → UNA intención por llamada, con print() de lo que importa
4. Evidencia DESPUÉS                 → print de datos (conteos, dimensiones, bounding box)
                                       y/o screenshot si el cambio es visual
5. ¿Coincide con la intención?       → sí: siguiente paso · no: investigar y corregir ANTES de seguir
```

- **Nunca declarar "hecho" sin evidencia** del paso 4. "El código corrió sin error" NO es evidencia: `exec` silencioso puede no haber hecho nada (nombre de objeto mal escrito, contexto incorrecto, colección equivocada).
- **Por qué chico**: timeout de 180 s, main thread bloqueado, y el propio README lo exige ("Complex operations might need to be broken down into smaller steps"). Un timeout NO garantiza que la operación falló — puede haber terminado después del corte: re-consultar estado antes de reintentar (reintentar a ciegas = objetos duplicados).
- `print()` es tu único canal de retorno en `execute_blender_code`. Patrón: terminar cada bloque con un `print` de verificación (`print(len(bpy.data.objects), obj.dimensions[:])`) o `print(json.dumps(datos))` para estructurar.
- Screenshot **antes/después** en cambios visuales: es la práctica que el propio prompt del servidor manda ("Use get_viewport_screenshot() BEFORE making changes… AFTER executing code… to verify the result").

## 6. `execute_blender_code` con seguridad

Riesgo real (advertencia literal del README): ejecuta Python arbitrario dentro de Blender — puede borrar toda la escena, tocar preferencias, escribir en disco o cerrar Blender. "ALWAYS save your work before using it."

```python
import bpy
# Preflight al iniciar una sesión de trabajo MCP:
if bpy.data.is_saved:
    bpy.ops.wm.save_mainfile()          # checkpoint en disco
bpy.ops.ed.undo_push(message="MCP: checkpoint")  # paso de undo explícito
col = bpy.data.collections.get("MCP_Trabajo")
if col is None:
    col = bpy.data.collections.new("MCP_Trabajo")
    bpy.context.scene.collection.children.link(col)
print("saved:", bpy.data.is_saved, "| col:", col.name)
```

Reglas de operación:

- **Guardar antes** de cualquier bloque destructivo; `bpy.ops.wm.save_as_mainfile(filepath=...)` si el .blend aún no tiene ruta.
- **Operar sobre colecciones propias** (`MCP_Trabajo` o por asset): nunca barrer `bpy.data.objects` completo con deletes; filtrar SIEMPRE por colección o prefijo de nombre [ver: organizacion-blend].
- `bpy.ops.ed.undo_push(message=...)` antes de bloques grandes crea un paso de undo limpio para el humano (la API lo marca "internal use only": funciona, pero no depender de él como rollback garantizado — el checkpoint real es el .blend guardado).
- **Prohibido**: `bpy.ops.wm.quit_blender()`, `bpy.ops.wm.open_mainfile()` sin guardar antes (descarta todo sin preguntar), deletes/purges globales (`bpy.ops.outliner.orphans_purge` solo con confirmación), loops sin cota.
- **No invocar operadores modales/interactivos** (los que esperan input de mouse: transform modal, knife, sculpt strokes): via timer no hay evento de usuario y fallan o dejan el estado colgado. Usar la vía de datos (`obj.location = ...`, `bmesh`) en vez del operador equivalente [ver: bpy-scripting].
- Muchos `bpy.ops` dependen de contexto (objeto activo, modo, área). Preparar contexto explícito (`bpy.context.view_layer.objects.active = obj`, `bpy.ops.object.mode_set(mode='OBJECT')`) o usar `bpy.context.temp_override(...)`, y preferir API de datos sobre operadores siempre que exista.

## 7. Kit de evidencia: verificar sin ojos humanos

**a) Medidas por código** (la evidencia más barata y exacta — geometría evaluada con modificadores):

```python
import bpy
dg = bpy.context.evaluated_depsgraph_get()
for obj in bpy.data.collections["MCP_Trabajo"].objects:
    if obj.type != 'MESH':
        continue
    ev = obj.evaluated_get(dg)
    me = ev.to_mesh()
    me.calc_loop_triangles()
    print(f"{obj.name}: tris={len(me.loop_triangles)} verts={len(me.vertices)} "
          f"dim={tuple(round(d, 3) for d in obj.dimensions)} scale={tuple(obj.scale)}")
    ev.to_mesh_clear()
```

Checks numéricos estándar de un asset de juego: tris dentro de presupuesto [ver: modelado/presupuestos-poligonos], `scale == (1,1,1)` (transform aplicado antes de exportar [ver: pipeline/arte-a-unity]), dimensiones en metros plausibles, conteo de materiales y UV layers (`len(me.uv_layers)`). También existe `bpy.context.scene.statistics(view_layer)` (el string de la status bar).

**b) Screenshot vs render de evidencia:**

| Método | Cuándo | Notas |
|---|---|---|
| `get_viewport_screenshot` | Chequeo rápido de composición/estado | Es la pantalla literal: incluye overlays y gizmos; depende de qué muestre el viewport en ese momento |
| Render real a archivo + leer la imagen | Evidencia limpia de silueta/material/iluminación | Motor `BLENDER_WORKBENCH` (rápido, sin luces, tipo matcap) o `BLENDER_EEVEE` (materiales reales) [ver: materiales-preview] |
| `bpy.ops.render.opengl()` | Snapshot del viewport por código (= menú `View ‣ Render Viewport Preview`) | Solo Workbench y EEVEE — **no soportado con Cycles** (manual 5.2); usa cámara virtual de la vista actual salvo vista de cámara |

```python
import bpy
sc = bpy.context.scene
sc.render.engine = 'BLENDER_WORKBENCH'            # o 'BLENDER_EEVEE'
sc.render.image_settings.media_type = 'IMAGE'     # 5.0+: setear ANTES de file_format
sc.render.image_settings.file_format = 'PNG'
sc.render.resolution_x, sc.render.resolution_y = 960, 540
sc.render.filepath = '/ruta/evidencia/asset_frente.png'
bpy.ops.render.render(write_still=True)
print("render:", sc.render.filepath)
```

Después: leer el archivo de imagen con la tool de lectura del agente y **mirarlo de verdad** (silueta correcta, sin caras volteadas evidentes, material aplicado). Para cobertura completa: renders desde 2–4 ángulos moviendo la cámara por código.

## 8. Headless batch sin MCP: `blender --background --python`

El addon MCP **no corre** en background (§1) — el batch headless es `bpy` puro [ver: bpy-scripting]. Flags verificados en el manual 5.2:

| Flag | Uso |
|---|---|
| `-b`, `--background` | Sin UI; para render/export/validación por lotes |
| `--python <archivo.py>` | Ejecuta el script |
| `--python-expr "<código>"` | Expresión/script inline (multilínea permitido) |
| `--python-exit-code <n>` | Exit code 1–255 si el script lanza excepción — **imprescindible en CI** (default: excepción ≠ exit code ≠ 0) |
| `--factory-startup` | Ignora startup.blend y prefs del usuario → corridas reproducibles |
| `--addons <a,b>` | Habilita add-ons extra en esa corrida (lista separada por comas, sin espacios) |
| `-o <path>` / `-f <frame>` / `-a` | Render: salida, frame único, animación. `--render-format PNG` etc. |
| `--log "*"` | Categorías de logging para diagnosticar |

Patrón: `blender -b assets.blend --factory-startup --python export_glb.py --python-exit-code 1` (el orden importa: los argumentos se ejecutan en secuencia; `-b` primero, `--python` después del .blend).

**MCP interactivo vs headless batch:**

| Situación | Vía |
|---|---|
| Crear/iterar un asset con feedback visual, tocar la escena viva del artista | MCP |
| Export masivo (N .blend → N .glb/.fbx), validaciones de presupuesto en CI, render farm de thumbnails | Headless |
| Sesión larga sobre el mismo estado (el .blend abierto conserva todo entre llamadas) | MCP |
| Corridas reproducibles desde cero, paralelizables, sin Blender abierto | Headless |

## 9. Límites conocidos

| Límite | Detalle |
|---|---|
| Requiere Blender con GUI | Addon rechaza `-b`; sin socket no hay tools (solo `xvfb` como escape en Linux) |
| Un cliente | `listen(1)`: no compartir un Blender entre dos agentes |
| 180 s por comando | Trocear; timeout ≠ operación fallida — re-consultar estado |
| Main thread | Código largo congela la UI; loops sin cota cuelgan Blender |
| `get_scene_info` truncado | Primeros 10 objetos; escenas grandes → queries por código |
| Operadores modales | Transform interactivo, knife, strokes de sculpt/paint: no operables via MCP — usar API de datos o dejárselo al humano [ver: sculpt] |
| Screenshots grandes | `max_size` alto = más tokens y latencia; 800–1000 px alcanza para verificar |
| Sin sandbox | `execute_blender_code` es Python total: la seguridad es disciplina del agente (§6) |
| Sin undo automático | Cada llamada muta el .blend vivo; el rollback real es el archivo guardado |

## 10. Cambios 4.x → 5.x que rompen scripts de la web

Mucho snippet circulante es de 2.8–4.x. Verificado contra release notes oficiales 5.0 y API 5.2:

| Cambio | Antes (4.x) | En 5.x |
|---|---|---|
| Identificador de EEVEE | `BLENDER_EEVEE_NEXT` (4.2–4.5) | **`BLENDER_EEVEE`** (renombrado en 5.0; el default de `RenderSettings.engine` en la API 5.2) |
| Formato de salida | `image_settings.file_format = ...` directo | 5.0+: setear `image_settings.media_type` (`'IMAGE'`/`'VIDEO'`/`'MULTI_LAYER_IMAGE'`) **antes** de `file_format` |
| Brushes | `brush.sculpt_tool` | `brush.sculpt_brush_type` (sufijo `_tool` → `_brush_type` en 5.0) |
| Instalar add-on .py | Botón "Install…" | 4.2+: dropdown **"Install from Disk…"** (Add-ons ≠ Extensions) |
| Render passes | Abreviaturas (`DiffCol`, `IndexMA`) | Renombrados a nombres completos en 5.0 |
| Settings de Cycles por ID-property | `scene['cycles']` | 5.0: acceso runtime-defined por subscript ya no soportado — usar `scene.cycles` |

Más contexto de la versión en [ver: blender5-actualidad]; ecosistema de add-ons en [ver: addons-ecosistema]; la UI que el humano ve en [ver: interfaz-flujo].

## Reglas practicas

1. Antes de nada: ¿responde el MCP? `get_scene_info` como ping; si falla, Blender no está abierto o el socket no corre (§3).
2. `get_scene_info` SIEMPRE al inicio de sesión y después de cada tarea completada.
3. Screenshot ANTES y DESPUÉS de todo cambio visual; medidas por código para todo cambio de geometría.
4. Una intención por `execute_blender_code`; bloques de 5–30 líneas, nunca mega-scripts de 200.
5. Todo bloque termina en `print()` de verificación — sin print no hay retorno.
6. Guardar el .blend (`bpy.ops.wm.save_mainfile()`) antes del primer cambio y en cada hito.
7. Trabajar dentro de colecciones propias; deletes SIEMPRE filtrados por colección/prefijo, jamás globales.
8. `bpy.ops.ed.undo_push()` antes de bloques grandes; el rollback confiable es el archivo guardado.
9. Preferir API de datos (`obj.location`, `bmesh`) sobre `bpy.ops`; si usas ops, prepara el contexto explícito primero.
10. Integraciones de assets: `get_*_status` antes de usarlas; nunca asumir que están activas.
11. Tras importar CUALQUIER asset (Poly Haven, Sketchfab, Rodin, Hunyuan): `world_bounding_box` + normalizar transform y escala.
12. Timeout ≠ fallo: re-consultar estado antes de reintentar; reintento a ciegas duplica objetos.
13. Nunca lanzar operadores modales ni `quit_blender`/`open_mainfile` sin checkpoint.
14. Verificación de asset de juego: tris contados con depsgraph evaluado, `scale=(1,1,1)`, dimensiones en metros, UVs presentes.
15. Evidencia visual limpia = render Workbench/EEVEE a archivo + leer la imagen; el screenshot del viewport es para chequeos rápidos.
16. Batch masivo o CI → headless `-b --python --python-exit-code 1 --factory-startup`, no MCP.
17. Nunca declarar "listo" un asset sin al menos UNA evidencia visual y UNA numérica de esta misma sesión.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| "El MCP no conecta" con Blender abierto | El socket no corre: panel BlenderMCP → "Connect to MCP server"; verificar que el addon está habilitado y el auto-start no falló (mirar la consola del sistema de Blender) |
| Correr `uvx blender-mcp` en una terminal aparte | No: lo lanza el cliente MCP; el proceso manual compite y confunde (troubleshooting oficial del README) |
| Ejecutar código y asumir éxito porque no hubo error | `exec` silencioso ≠ cambio hecho: exigir print de estado o screenshot posterior |
| Script de la web con `BLENDER_EEVEE_NEXT` o `file_format` sin `media_type` | Falla en 5.x — aplicar la tabla §10 |
| Mega-script de una vez → timeout a 180 s | Trocear; tras un timeout, consultar estado antes de reintentar |
| `bpy.ops.transform.translate()` u ops modales via MCP | Usar datos: `obj.location.x += 2`; los modales necesitan eventos de UI que no existen |
| Borrar "los cubos" con un loop sobre `bpy.data.objects` completo | Filtrar por colección propia o prefijo; un match genérico se lleva assets del humano |
| Confiar en `get_scene_info` en una escena de 200 objetos | Solo lista 10: contar y filtrar por código (`len(bpy.data.objects)`, comprehensions) |
| Import de Sketchfab/Rodin gigante o enterrado en el piso | Siempre `world_bounding_box` + reubicar/escalar tras importar |
| Intentar MCP contra `blender --background` en un pipeline | El addon no arranca en `-b` por diseño; headless = script `bpy` puro (§8) |
| Screenshot 4K "para ver mejor" | 800–1000 px basta y cuesta una fracción de tokens |
| Verificar material/iluminación con render Workbench | Workbench ignora luces y materiales node-based: para eso, EEVEE (§7) |

## Fuentes

- **BlenderMCP README** — ahujasid/blender-mcp (GitHub, consultado jul-2026) — setup oficial (uvx, Claude Code `claude mcp add`, ENOENT/Python 3.11), integraciones, troubleshooting, advertencia de seguridad de `execute_blender_code`.
- **`addon.py`** — ahujasid/blender-mcp (código fuente) — puerto 9876, `listen(1)`, ejecución en main thread via `bpy.app.timers`, rechazo de background mode, auto-start, límite de 10 objetos en `get_scene_info`, implementación de screenshot y `execute_code` (stdout capturado).
- **`src/blender_mcp/server.py`** — ahujasid/blender-mcp (código fuente) — lista exacta de las 22 tools MCP, timeouts de 180 s, prompt `asset_creation_strategy` con la estrategia oficial de assets y verificación visual.
- **Command Line Arguments** — Manual Blender 5.2 LTS (docs.blender.org) — flags exactos: `--background`, `--python`, `--python-expr`, `--python-exit-code`, `--factory-startup`, `--addons`, render flags, `--log`.
- **Viewport Render** — Manual Blender 5.2 LTS (docs.blender.org) — solo Workbench/EEVEE (no Cycles), menú `View ‣ Render Viewport Preview`, cámara virtual de la vista.
- **Add-ons (Preferences)** — Manual Blender 5.2 LTS (docs.blender.org) — "Install from Disk" para add-ons legacy; legacy add-ons siguen soportados.
- **Blender 5.0 Release Notes: Python API** — developer.blender.org — renombre `BLENDER_EEVEE_NEXT` → `BLENDER_EEVEE`, `media_type` antes de `file_format`, `_tool` → `_brush_type`, render passes renombrados, fin del acceso subscript a settings runtime.
- **Release Notes index** — developer.blender.org — confirmación de la línea de versiones: 4.5 LTS → 5.0 → 5.1 → **5.2 LTS** (actual) → 5.3 alpha.
- **Python API: `bpy.ops.render` / `bpy.ops.ed` / `bpy.ops.screen`** — docs.blender.org/api (current, 5.2) — firmas reales de `render.opengl`, `render.render`, `ed.undo_push`, `screen.screenshot_area`.
- **Python API: `bpy.types.RenderSettings` / `ImageFormatSettings` / `Scene`** — docs.blender.org/api (current, 5.2) — `engine` default `'BLENDER_EEVEE'`, enum de `media_type`, `Scene.statistics()`.
