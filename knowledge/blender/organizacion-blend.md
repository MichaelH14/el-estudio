# Organización de proyectos .blend

> **Cuando cargar este archivo:** al crear o estructurar cualquier .blend de asset de juego (colecciones, naming, variantes), al limpiar archivos que engordan (orphan data / purge), al decidir entre un .blend por asset o biblioteca linked, al marcar assets para el Asset Browser, o al versionar/recuperar .blend. Complementa [ver: blender-mcp-operativo] (cómo ejecutar) — aquí va el CÓMO ORGANIZAR.

Verificado contra el manual y la API de Blender en docs.blender.org (rama `latest`, stack objetivo **Blender 5.2 LTS**), release notes oficiales 4.2–5.2 en developer.blender.org, y las Naming Conventions de Blender Studio. Mucho contenido web de Blender 2.8–4.x ya no aplica: los cambios de versión van marcados explícitos.

---

## 1. Colecciones: la estructura del .blend de un asset

Las colecciones (desde 2.8; los "groups" y "layers" de tutoriales viejos NO existen) organizan sin crear relación de transformación (eso es parenting). Un objeto puede estar en varias colecciones a la vez.

Estructura recomendada para un asset de juego (convención de esta base, alineada con la práctica de prefijos de Blender Studio):

```text
Scene Collection
└── crate_wood                  ← colección raíz = nombre del asset (lo que se linkea/exporta)
    ├── crate_wood-final        ← SOLO lo que va al motor (low poly + LODs) [ver: import-export]
    ├── crate_wood-high         ← high poly para bake (excluida del view layer al terminar)
    ├── crate_wood-ref          ← referencias/blueprints (Disable in Renders + no seleccionable)
    └── crate_wood-wip          ← pruebas, versiones descartadas (excluida; purgar antes de cerrar)
```

Operadores exactos (Object Mode, menú `Object ‣ Collection`):

| Acción | Operador / atajo |
|---|---|
| Mover a colección | **Move to Collection** — `M` (en 5.0 ganó búsqueda por texto en el popup) |
| Añadir a otra colección sin sacar de la actual | **Link to Collection** — `Shift-M` |
| Crear colección con la selección | **Create New Collection** — `Ctrl-G` (⚠️ no queda linkeada a la escena) |
| Quitar de colección | **Remove from Collection** — `Ctrl-Alt-G` |
| En el Outliner: nueva colección hija | **New Collection** (botón/context menu) |

**Toggles de visibilidad** (Outliner, columna derecha; se muestran más con el popover del embudo → Restriction Toggles). Diferencias que importan:

| Toggle | Efecto | Clave para assets |
|---|---|---|
| **Exclude from View Layer** (checkbox) | Fuera del viewport, render Y evaluación | El correcto para `high`/`wip`: no gasta rendimiento. Python: `LayerCollection.exclude = True` |
| **Hide in Viewports** (ojo, `H`/`Alt-H`) | Oculta solo en viewport, view layer actual | Temporal. El objeto SIGUE evaluándose (afecta rendimiento). NO viaja al linkear el archivo |
| **Disable in Viewports** (monitor) | Oculta en viewport, todos los view layers | "Invisibilidad de largo plazo": sobrevive `Alt-H`, deja de evaluarse, SÍ viaja al linkear. Python: `Collection.hide_viewport` |
| **Disable in Renders** (cámara) | Solo afecta render | Para `ref` y helpers. Python: `Collection.hide_render` |
| **Disable Selection** (cursor) | No seleccionable en viewport | Para referencias que no quieres tocar por accidente. Python: `Collection.hide_select` |

- `Shift-LMB` en un toggle lo aplica al ítem y todos sus hijos; `Ctrl-LMB` lo aísla (solo esa colección).
- **Cambio 4.5**: el panel de Collection Properties reorganizó "Restrictions" como "Visibility" (release notes 4.5 UI).
- **Color tags**: context menu del Outliner sobre la colección ‣ **Set Color Tag** — 8 colores + None. Python: `collection.color_tag` con `'NONE'`, `'COLOR_01'`…`'COLOR_08'`. Convención sugerida: verde = exportable/final, rojo = high/no exportar, amarillo = WIP.
- **Collection Exporters (nuevo en 4.2)**: en `Properties ‣ Collection Properties ‣ Exporters` se adjunta un exportador (glTF 2.0, FBX legacy, OBJ, USD, Alembic, PLY) CON su configuración a la colección; botón **Export All** o `File ‣ Export All Collections` re-exporta todo con un clic. Es LA herramienta para iterar assets de juego sin re-configurar el export cada vez [ver: import-export]. API: `Collection.exporters`.

Patrón bpy para levantar la estructura (una intención por llamada si vas por MCP [ver: blender-mcp-operativo]):

```python
import bpy

def coll(name, parent, color='NONE'):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in {ch.name for ch in parent.children}:
        parent.children.link(c)
    c.color_tag = color
    return c

root = coll("crate_wood", bpy.context.scene.collection)
coll("crate_wood-final", root, 'COLOR_04')
coll("crate_wood-high",  root, 'COLOR_01')
coll("crate_wood-ref",   root, 'COLOR_03')

def find_lc(lc, name):                      # LayerCollection ≠ Collection
    if lc.collection.name == name: return lc
    for ch in lc.children:
        r = find_lc(ch, name)
        if r: return r

find_lc(bpy.context.view_layer.layer_collection, "crate_wood-high").exclude = True
print([c.name for c in root.children])      # evidencia
```

## 2. Naming consistente dentro del .blend

Reglas duras de los data-blocks (manual, sección Data-Blocks):

- Nombre único POR TIPO. Colisión → Blender añade sufijo numérico `.001`–`.999` automáticamente. Esos sufijos son la marca del naming sucio.
- **Cambio 5.0**: nombres hasta **255 bytes UTF-8** (antes 63). Al abrir en 4.5 LTS se truncan; linkear data-blocks de nombre largo desde 4.5 NO funciona (release notes 5.0 Core).
- **Nombres con prefijo punto (`.foo`) = data-block oculto**: no aparece en File Browsers ni en la mayoría de selectores; en **5.1** también se ocultan de los resultados de búsqueda. Útil para helpers internos; trampa si lo haces sin querer.
- Objeto y su object data (malla) tienen nombres INDEPENDIENTES: duplicar `Crate` crea `Crate.001` con malla `Crate.001`, pero renombrar el objeto no renombra la malla. Los motores muestran ambos (Unity: la malla; jerarquías: el objeto).

Convención recomendada (destilada de Blender Studio "Datablock names", adaptada a un dev de juegos solo):

| Regla | Ejemplo |
|---|---|
| `lower_underscore_case`, prefijos en MAYÚSCULAS, sin espacios ni caracteres especiales | `GEO-crate_wood-lid` |
| Prefijo por propósito: `GEO` (renderiza/exporta), `RIG` (armature), `LGT` (luces), `HLP` (empties/helpers), `TMP` (placeholder), `WGT` (bone shapes) | `HLP-crate_wood-socket_lid` |
| El nombre del asset presente en TODOS sus data-blocks (namespace único) | `crate_wood` en objeto, malla y material |
| Simetría: sufijos exactos `.L` / `.R` (los reconocen mirror/rig) — NO usarlos para cosas no simétricas | `GEO-door-handle.L` |
| Variantes con punto | `GEO-crate_wood.burned` |
| Sustituir `.001` por `_001` cuando la copia es intencional (Blender Studio lo exige para library overrides seguras) | `LI-tree_birch_001` |
| Malla nombrada igual que su objeto; materiales con prefijo `M_` (convención juego) o al menos el namespace | `M_crate_wood` |

Por qué el naming sucio explota en el export: los exportadores usan los nombres de los data-blocks tal cual — `Cube.001`, `Material.003` acaban en el motor como nombres de mesh/material; los sufijos `.001` generan colisiones y rompen el re-import/remapeo de materiales al iterar (detalle por formato en [ver: import-export]). Regla: si en el Outliner hay un `.001` que no pediste, o es basura o es un nombre sin resolver.

Herramientas: `F2` renombra el ítem activo; **Batch Rename** `Ctrl-F2` (menú `Edit ‣ Batch Rename…`) para renombrar en masa con buscar/reemplazar. Sincronizar mallas con sus objetos:

```python
import bpy
for obj in bpy.context.scene.objects:
    if obj.data and obj.data.users == 1 and obj.data.name != obj.name:
        obj.data.name = obj.name
print("mallas renombradas")
```

## 3. Object data compartida e instancias: variantes baratas

| | `Shift-D` **Duplicate Objects** | `Alt-D` **Duplicate Linked** |
|---|---|---|
| Objeto nuevo | Sí | Sí |
| Malla (object data) | **Copiada** (independiente) | **Compartida** (editar una edita todas) |
| Transform | Propio | Propio (mover/rotar/escalar libre) |
| Materiales | Compartidos por defecto (¡también en Shift-D!) | Compartidos |
| Coste en archivo | Malla duplicada = MB duplicados | Solo un objeto más: casi gratis |
| Uso típico | Vas a modificar la copia | Repetición: 4 patas de mesa, ruedas, props repetidos |

- Qué se copia y qué se linkea en `Shift-D` es configurable en `Preferences ‣ Editing ‣ Duplicate Data`.
- El contador de usuarios de un data-block se ve junto a su nombre (número). Romper el vínculo después: clic en ese número = **Make Single User** (copia propia).
- **Variante de material sin duplicar malla**: en `Properties ‣ Material`, el selector **Link** del slot tiene `Data` (default: el material vive en la malla, compartido por todos los linked duplicates) u `Object` (el material vive en el objeto). Con `Link = Object`, dos `Alt-D` de la misma malla pueden tener materiales distintos — skins/variantes de color gratis. Python: `obj.material_slots[0].link = 'OBJECT'`.
- **Collection Instance**: `Add ‣ Collection Instance` crea UN objeto (empty) que instancia la colección completa — para kits y escenas de prueba. Se revierte con Make Instances Real. El offset de origen se controla con `Instance Offset` en Collection Properties.
- ⚠️ Para EXPORTAR a motor, las instancias y data compartida se resuelven según el formato (glTF conserva instancing, FBX según opciones) — verificar en [ver: import-export]. Dentro del .blend siempre son ganancia.

## 4. Datos huérfanos y purge: por qué engordan los .blend

Ciclo de vida (manual, Data-Blocks ‣ Life Time):

- Cada data-block cuenta usuarios (`ID.users`). **Con 0 usuarios NO se escribe al guardar** — se pierde en el siguiente save+reload, no antes. Por eso un .blend recién trabajado engorda: mallas viejas, materiales sueltos e imágenes empaquetadas siguen dentro hasta purgar o re-abrir.
- **Fake User** (icono escudo, `ID.use_fake_user`): fuerza a conservar un data-block sin usuarios. Imprescindible para materiales/node groups de biblioteca; veneno si se acumula sin querer.
- Fuentes típicas de engorde: texturas empaquetadas (`File ‣ External Data`), duplicados `Shift-D` descartados, materiales de imports FBX/glTF, colecciones `wip`.

Limpieza:

- **`File ‣ Clean Up ‣ Purge Unused Data`** — abre el diálogo de purge (no se puede deshacer).
- Outliner en Display Mode **Unused Data** (**cambio 4.2**: antes se llamaba "Orphan Data" — así aparece en tutoriales viejos) → botón **Purge** en el header. **Desde 4.2** el purge abre diálogo con opciones: **Local Data-Blocks**, **Linked Data-Blocks**, **Recursive Delete** (borra lo que solo usaban los borrados — sin esto hay que purgar varias veces).
- En ese modo el icono de escudo añade/quita fake users por ítem.
- Reasignar antes de borrar: context menu ‣ `ID Data ‣ Remap Users` reemplaza TODOS los usos de un data-block por otro (`ID.user_remap(new_id)`) — p. ej. consolidar 5 materiales `.00x` en uno.

```python
import bpy
antes = len(bpy.data.meshes) + len(bpy.data.materials) + len(bpy.data.images)
bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
despues = len(bpy.data.meshes) + len(bpy.data.materials) + len(bpy.data.images)
print(f"purge: {antes} -> {despues}")
bpy.ops.wm.save_mainfile()          # el purge solo se materializa al guardar
```

- Opción **Compress** al guardar (`File ‣ Save As…`, checkbox Compress; default configurable en Preferences ‣ Save & Load): comprime con **Zstandard** (desde 3.0; antes Gzip — un .blend 3.0+ comprimido NO abre en 2.9x). Ojo: linkear desde un .blend comprimido carga el archivo ENTERO en memoria.

## 5. Un .blend por asset vs biblioteca: linked libraries

| | Un .blend por asset | Un .blend biblioteca (muchos assets) |
|---|---|---|
| Export por asset | Directo (Collection Exporter en la raíz) | Requiere disciplina de colecciones por asset |
| Versionado (LFS) | Diffs pequeños, historial por asset | Cada cambio versiona TODO el archivo |
| Riesgo de corrupción | Aislado | Un archivo corrupto = toda la biblioteca |
| Navegar/reusar | Más archivos que abrir | Todo a mano; ideal + Asset Browser |
| Recomendación | **Assets hero / en producción activa** | Props chicos, materiales, node groups compartidos |

Para un dev solo: **carpeta `assets/` con un .blend por asset hero + un `library_props.blend` / `library_materials.blend` para lo menudo, registrada como Asset Library** (sección 6). Escenas de nivel/escena linkean, no copian.

Mecánica de Link/Append (`File ‣ Link…` / `File ‣ Append…`, o drag & drop del .blend):

- **Link**: referencia viva; el data llega **de solo lectura** (ni mover el objeto se puede). Soluciones: linkear la COLECCIÓN con `Instance Collections` activado (llega como un objeto instancia transformable, creado en el 3D Cursor), o crear **Library Overrides**.
- **Append**: copia local editable; pierde conexión con el origen.
- **Library Overrides** (concepto): capa de edición local sobre data linkeada que se mantiene sincronizada — las propiedades NO tocadas siguen al archivo fuente. Se soporta añadir modificadores/constraints y overrides múltiples del mismo asset. Requisito de estructura: todas las colecciones del asset como hijas de una raíz clara (por eso la colección raíz = asset de la sección 1). El sistema de proxies viejo fue eliminado en 3.2 — cualquier tutorial que diga "Make Proxy" es obsoleto.
- Rutas: por defecto **relativas** (`//`) — mover el proyecto completo funciona; mover solo el .blend rompe. `Save As…` con **Remap Relative** re-mapea. Biblioteca rota → placeholders vacíos, se arregla con context menu ‣ **Relocate** en el Outliner (modo Blender File) o `bpy.ops.wm.lib_relocate()`.
- Convertir linked → local: `Object ‣ Relations ‣ Make Local…`.
- **Cambio 5.0**: existe **Packed linked data** — IDs linkeados empaquetados DENTRO del archivo (siguen siendo de solo lectura pero sobreviven si la biblioteca desaparece). Abierto en 4.5 LTS se convierte en data local normal (release notes 5.0 Core).
- No se puede linkear desde archivos de versión mucho más nueva; 4.5 LTS lee el formato 5.0, versiones anteriores NO (cambio de formato "Large Buffers", 5.0 Core).

## 6. El Asset Browser: reusar entre proyectos

Setup una vez: `Edit ‣ Preferences ‣ File Paths ‣ Asset Libraries` → añadir nombre + carpeta (p. ej. `~/game-assets/`). Todo .blend dentro (a cualquier profundidad) se escanea; Blender indexa y cachea.

- **Marcar**: context menu sobre el data-block (Outliner, 3D Viewport `Object` menu, o selector de data-block) → **Mark as Asset**. Genera preview automático. Soporta como asset "primitivo": **Object, Collection, Material, World, Node Group, Scene** (+ presets: poses, brushes). Para assets de juego lo útil: **colecciones** (el asset entero), **materiales** y **node groups** de Geometry Nodes [ver: geometry-nodes].
- **Quitar**: **Clear Asset** (o **Clear Asset (Set Fake User)** para no perder el data-block al guardar).
- **Catálogos**: jerarquía propia independiente de archivos/carpetas (`Props/Crates`, `Materials/Wood`). Se crean en el Asset Browser (`Catalog ‣ New Asset Catalog` o el `+` del árbol) y se asigna arrastrando el asset al catálogo. Se guardan en **`blender_assets.cats.txt`** junto al .blend — al compartir/copiar la biblioteca, ese archivo VIAJA con ella o los assets quedan sin catálogo.
- Un asset pertenece a UN catálogo. Los node groups en catálogos `Geometry Nodes/...` aparecen directamente en el menú **Add Modifier** / Add del editor de nodos.
- **Import Method** (header del Asset Browser): `Follow Preferences` / `Link` / `Append` / **`Pack`** (**nuevo en 5.0**: linkea y empaqueta en el archivo — autocontenido sin duplicar edición). Assets de bibliotecas online solo Append/Pack.
- La biblioteca **Current File** muestra los assets del archivo abierto; **Essentials** trae los bundled de Blender (brushes, Smooth By Angle, hair).
- Editar un asset = abrir SU .blend (Blender no escribe en otros archivos); el Asset Browser da "Open Blend File" en el context menu.
- Guardar el .blend dentro de la carpeta registrada ES lo que lo mete en la biblioteca — Blender no copia nada por ti.

```python
import bpy
mat = bpy.data.materials["M_crate_wood"]
mat.asset_mark()
mat.asset_generate_preview()        # puede correr en background thread
# opcional: asignar catálogo por UUID (el de blender_assets.cats.txt)
# mat.asset_data.catalog_id = "d1f81597-d27d-42fd-8386-3a3def6c9200"
print(mat.asset_data is not None)   # evidencia: True = marcado
```

## 7. Versionado de .blend

Los .blend son **binarios** (formato propio, opcionalmente Zstandard): git no diffea ni mergea — dos personas tocando el mismo .blend = conflicto irresoluble, gana uno. Para un dev solo con repo del juego:

- **Git LFS sí**: guarda punteros de texto en el repo y el binario en el storage LFS (git-lfs.com; instalable con `brew install git-lfs`). Sin LFS, cada save de un .blend de 100 MB engorda el repo para siempre. `.gitattributes`:

```text
*.blend filter=lfs diff=lfs merge=lfs -text
*.blend1 export-ignore
```

  (mejor aún: `*.blend1` y `*_autosave.blend` al `.gitignore` — son backups locales, no fuente).
- **Versiones incrementales como práctica de arte**: `File ‣ Save Incremental` (`Ctrl-Alt-S`) guarda con número incremental sin pisar nada (`crate_v001.blend` → `crate_v002.blend`); en `Save As` los botones +/− (o `NumpadPlus`/`NumpadMinus`) suben/bajan el número del nombre. Python: `bpy.ops.wm.save_mainfile(incremental=True)`. Guardar un incremental ANTES de operaciones destructivas grandes (apply de modificadores en cadena, joins, decimate final) [ver: modificadores]. Blender Studio reserva `v001` para exports/renders y deja los working files sin versión (la historia la lleva el VCS) — con LFS puedes hacer lo mismo.
- **Backups automáticos de Blender**: `Preferences ‣ Save & Load ‣ Save Versions` (default 2) — al guardar, el archivo anterior pasa a `.blend1`, el anterior a ese a `.blend2`, EN LA MISMA carpeta. Restaurar = renombrar `.blend1` → `.blend`.
- Convención de nombres de archivo (Blender Studio): "no caps, no gaps" — minúsculas, sin espacios, `_` como espacio, `-` como separador jerárquico: `char-goblin-modeling.blend`, `prop-crate_wood.blend`.

## 8. Recuperación de desastres

| Mecanismo | Dónde | Detalle |
|---|---|---|
| **Auto Save** | Temporary Directory del sistema (configurable en `Preferences ‣ File Paths ‣ Temporary Files`) | Default ON, **cada 2 min** (`Preferences ‣ Save & Load ‣ Auto Save ‣ Timer`). Archivos `<archivo>_autosave.blend`, con timestamp. **Solo se conserva UNO por proyecto**. Contenido viejo (2.8–3.x) habla de autosaves con nombre numérico — ya no aplica en 5.x |
| **Recover Auto Save** | `File ‣ Recover ‣ Auto Save` | Abre el file browser en el temp dir; activar la vista de lista detallada para ver fechas. Tras recuperar: **Save As inmediato** |
| **quit.blend** | Temp dir, al cerrar Blender normalmente | `File ‣ Recover ‣ Last Session` lo reabre. El temp dir puede vaciarse al reiniciar la máquina — no es backup de largo plazo |
| **`.blend1`** | Junto al archivo | Último save anterior (sección 7) |

Límites verificados (manual, Recovering Data + código fuente del autosave):

- ⚠️ **Auto Save se APLAZA mientras hay un operador modal activo** — `wm_autosave_timer` (`wm_files.cc`, código fuente actual de Blender) detecta un modal handler en curso y reintenta cada 10 ms en vez de guardar, en lugar de saltarse el ciclo entero. Un brush stroke de Sculpt/Texture Paint o un transform (`G`/`R`/`S`) en Edit Mode SON operadores modales: si Blender crashea a mitad de uno, ese cambio puntual no llegó a ningún autosave; entre strokes/transforms el autosave sí corre normal. NO VERIFICADO en el manual (5.x no lo documenta explícito), sí en el código fuente [ver: sculpt].
- Solo hay UN autosave por proyecto (lo documentaba explícito el manual de 2.93; el mecanismo — sobrescribir el mismo archivo — no cambió en 5.x): lo posterior al último ciclo se pierde.
- **Cambio 5.2**: existe `bpy.ops.wm.save_auto_save()` para disparar un autosave por código — ideal como checkpoint barato antes de una operación pesada vía MCP sin tocar el archivo real (release notes 5.2 Core). En 5.2 los autosaves además guardan info de imágenes editadas dentro de Blender.
- Hábito del agente: `bpy.ops.wm.save_mainfile()` antes de operaciones pesadas o arriesgadas (boolean masivo, apply de todo el stack, purge, scripts que borran). Un save explícito vale más que toda la cadena de recovery.

## Reglas prácticas

1. Colección raíz por asset con el nombre EXACTO del asset; dentro: `-final`, `-high`, `-ref`, `-wip`.
2. `-final` contiene SOLO lo que exporta al motor; verifica su contenido antes de cada export [ver: import-export].
3. `high`/`wip`: **Exclude from View Layer** (checkbox), no `H` — así no se evalúan ni se cuelan en renders.
4. Referencias: **Disable in Renders** + **Disable Selection**.
5. Color tags siempre: verde = exportable, rojo = no exportar, amarillo = WIP.
6. Cero nombres `Cube`, `Material.001`, `Suzanne` en un archivo que se entrega: `F2` / `Ctrl-F2` (Batch Rename) antes de guardar.
7. Prefijos de propósito (`GEO/RIG/LGT/HLP/TMP`) + namespace del asset en TODOS los data-blocks.
8. Malla nombrada igual que su objeto; copias intencionales con `_001`, nunca `.001`.
9. Repetición dentro del asset = `Alt-D` (linked), no `Shift-D`; variantes de color = material slot con `Link = Object`.
10. Un .blend por asset importante; biblioteca .blend registrada en Asset Libraries para props/materiales/node groups menudos.
11. Escenas de nivel LINKEAN colecciones de asset (con Instance Collections); nunca append de 20 copias.
12. Rutas relativas siempre; mover proyecto completo, no archivos sueltos; si algo rompe: Outliner ‣ Blender File ‣ Relocate.
13. `File ‣ Clean Up ‣ Purge Unused Data` (con Recursive Delete) + save antes de commitear o entregar un .blend.
14. Fake user SOLO a lo que debe sobrevivir sin usuarios (materiales de biblioteca, node groups); auditar escudos de vez en cuando en Unused Data.
15. Repo con `.gitattributes` LFS para `*.blend`; `.blend1`/`*_autosave.blend` al `.gitignore`.
16. `Ctrl-S` antes de: booleans grandes, apply de stack, join masivo, purge, cualquier script destructivo. `Ctrl-Alt-S` (Save Incremental) antes de cirugía mayor.
17. Sculpt/paint largo: guardar manual cada rato — el autosave se aplaza mientras el stroke/transform está en curso (operador modal) y solo guarda entre strokes.
18. Marcar como asset las colecciones/materiales/node groups que reusarás; asignar catálogo y conservar `blender_assets.cats.txt` junto a la biblioteca.
19. Tras cualquier purge/renombrado por script: imprimir conteos antes/después como evidencia (patrón MCP) [ver: blender-mcp-operativo].
20. Nombres de archivo: minúsculas, sin espacios (`prop-crate_wood.blend`); nombres de data-block ASCII y sin punto inicial salvo que QUIERAS ocultarlos.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| "Guardé y el material desapareció" — data-block con 0 usuarios se descarta al save+reload | Fake user (escudo) o marcarlo como asset; revisar Unused Data antes de guardar |
| Purge borra de más (un material "de reserva" sin usuarios) | Los "de reserva" llevan fake user ANTES del purge; el purge no avisa por ítem |
| Purge aparente pero el archivo sigue gordo | El purge se materializa al GUARDAR; y con Recursive Delete apagado quedan cadenas huérfanas — activarlo |
| `.001` por todos lados tras duplicar/importar | Batch Rename `Ctrl-F2`; consolidar duplicados con `ID Data ‣ Remap Users` y purgar |
| Ocultar high poly con `H` y la escena sigue lenta | `H` no saca del view layer: usar **Exclude from View Layer** o **Disable in Viewports** (el monitor, no el ojo) |
| Editas una malla y "se rompen" otros objetos | Era object data compartida (`Alt-D`). Ver el contador de usuarios; **Make Single User** si quieres independencia |
| Objeto linkeado que no se puede ni mover | Comportamiento normal de Link: instanciar la colección o crear Library Override; tutoriales con "Make Proxy" = pre-3.2, obsoleto |
| Moviste el .blend y se rompieron texturas/bibliotecas | Rutas relativas: mover la carpeta completa o `Save As` + Remap Relative; reparar con Relocate |
| El .blend 5.x no abre en Blender viejo | Formato 5.0: solo 4.5 LTS lo lee; nombres >63 bytes se truncan en 4.5. Para compartir atrás: exportar o guardar desde 4.5 |
| Autosave no tenía tu último stroke de sculpt | Auto Save se aplaza mientras el operador modal (stroke/transform) sigue activo; además solo guarda UN autosave por proyecto. `Ctrl-S` frecuente entre strokes |
| Recuperaste un autosave y lo pisaste al seguir trabajando | Tras `File ‣ Recover ‣ Auto Save`: **Save As** inmediato a ruta definitiva |
| Repo de git gigante e inservible | `.blend` binario sin LFS: activar `git lfs track "*.blend"` desde el PRIMER commit (LFS no des-engorda historial ya commiteado) |
| Assets marcados que no aparecen en otra máquina/proyecto | La biblioteca es la CARPETA registrada en Preferences; el .blend debe estar dentro y `blender_assets.cats.txt` presente para los catálogos |
| Data-block "fantasma" que no aparece en búsquedas | Nombre con punto inicial = oculto (5.1 lo oculta también en search); renombrar o activar Show Hidden en Preferences ‣ Save & Load |

## Fuentes

- **Manual Blender 5.x — Collections** (`docs.blender.org/manual` · scene_layout/collections) — Blender Foundation — operadores M/Shift-M/Ctrl-G, View Layer (Include/Holdout/Indirect Only), panel Exporters.
- **Manual — Duplicate / Duplicate Linked** (scene_layout/object/editing) — Blender Foundation — semántica exacta de Shift-D vs Alt-D y qué se comparte.
- **Manual — Opening & Saving + Preferences Save & Load / File Paths** (files/blend, editors/preferences) — Blender Foundation — Save Incremental, Compress (Zstd desde 3.0), Save Versions/.blend1, rutas relativas, Temporary Files.
- **Manual — Recovering Data** (troubleshooting/recover) — Blender Foundation — autosave 2 min, `<archivo>_autosave.blend`, quit.blend; "un autosave por proyecto" además confirmado en manual 2.93 (web.archive.org).
- **Blender source — `wm_files.cc`, `wm_autosave_timer`** (projects.blender.org/blender/blender, rama `main`) — Blender Foundation — confirma que el autosave se aplaza (reintento cada 10 ms) mientras hay un operador modal activo; no documentado así en el manual 5.x.
- **Manual — Outliner Interface & Editing** (editors/outliner) — Blender Foundation — modo Unused Data, diálogo Purge (local/linked/recursive), restriction toggles, Set Color Tag, Remap Users.
- **Manual — Data-Blocks** (files/data_blocks) — Blender Foundation — usuarios/fake user, colisiones `.001`, nombres 255 bytes, dot-prefix = oculto.
- **Manual — Link & Append + Library Overrides** (files/linked_libraries) — Blender Foundation — Link de solo lectura, Instance Collections, Relocate, overrides y su jerarquía, proxies eliminados en 3.2.
- **Manual — Asset Libraries / Catalogs / Asset Browser** (files/asset_libraries, editors/asset_browser) — Blender Foundation — Mark as Asset, tipos soportados, `blender_assets.cats.txt`, Import Method (Link/Append/Pack), Essentials.
- **Manual — Material Assignment** (render/materials/assignment) — Blender Foundation — material slot Link: Data vs Object.
- **Release Notes Blender 5.0 Core** (developer.blender.org) — nombres 255 bytes, Packed linked data, formato Large Buffers (solo 4.5+ lo lee).
- **Release Notes 4.2 (UI, I/O), 4.5 (UI), 5.1 (UI), 5.2 (Core)** (developer.blender.org) — Orphan→Unused Data + diálogo de purge (4.2), Collection Exporters (4.2), Restrictions→Visibility (4.5), dot-prefix en búsquedas (5.1), `wm.save_auto_save` (5.2).
- **API bpy actual** (`docs.blender.org/api/current`) — Blender Foundation — firmas verificadas: `outliner.orphans_purge`, `ID.asset_mark/asset_generate_preview/user_remap/use_fake_user`, `wm.save_mainfile(incremental=)`, `Collection.color_tag/exporters`, `LayerCollection.exclude`, `AssetMetaData.catalog_id`.
- **Blender Studio — Naming Conventions** (studio.blender.org/tools/naming-conventions) — Blender Studio — "no caps no gaps", prefijos GEO/RIG/LGT/HLP/TMP, `.L/.R`, `_00x` en vez de `.00x`, namespace por asset.
- **Git LFS** (git-lfs.com) — proyecto oficial Git LFS — qué resuelve para binarios grandes en git.

*NO VERIFICADO: la versión exacta en que el autosave pasó de nombre numérico a `<archivo>_autosave.blend` (el comportamiento actual sí está verificado en el manual 5.x).*
