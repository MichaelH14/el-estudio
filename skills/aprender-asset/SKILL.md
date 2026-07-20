---
name: aprender-asset
description: Use when the user hands you an existing Unity 3D asset (FBX, prefab, mesh, material, texture atlas, AnimatorController) and wants the agent to analyze it and extract its conventions — polycount, texel density, naming, material setup, rig type — to produce future assets consistent with it. Trigger on "aprende de este asset", "analiza este FBX/prefab", "saca las convenciones de este modelo", "quiero que mis assets se parezcan a este".
---

# /aprender-asset — extraer las convenciones de un asset de Unity

Analizas un asset 3D existente y produces una FICHA de convenciones que sirve de spec para hacer assets consistentes con él. NO copias el asset — extraes su ESTÁNDAR técnico.

## Conocimiento a cargar

1. `${CLAUDE_PLUGIN_ROOT}/knowledge/pipeline-assets/aprender-de-assets.md` — LA metodología (qué inspeccionar y cómo)
2. `${CLAUDE_PLUGIN_ROOT}/knowledge/modelado/presupuestos-poligonos.md` — para juzgar el polycount
3. `${CLAUDE_PLUGIN_ROOT}/knowledge/texturizado/texturas-a-unity.md` — para leer el setup de material/mapas
4. Si el asset tiene rig/clips: `${CLAUDE_PLUGIN_ROOT}/knowledge/rigging/rig-a-unity.md`

## Flujo

### 1. Identifica qué te dieron
Pregunta o detecta el tipo: ¿FBX/modelo? ¿prefab? ¿material? ¿atlas 2D? ¿AnimatorController? Cada uno se inspecciona distinto. Pide la ruta exacta del asset si no la tienes.

### 2. Inspecciona (los archivos de Unity son texto o medibles)
- **El `.meta`** (texto YAML, siempre): import settings — scaleFactor, normal map settings, rig type (`animationType`), material remap, compresión. Léelo directo.
- **La malla (FBX)**: impórtalo a Blender por MCP/headless y MIDE por código — tris/verts, escala real, número de UV maps, bones, materiales, pivote. (Receta en aprender-de-assets.md.)
- **El prefab** (`.prefab`, texto YAML): componentes, LODGroup, colliders, referencias a materiales/meshes.
- **El material** (`.mat`, texto): shader usado, mapas asignados, cómo empaqueta canales (metallic/smoothness), tiling.
- **Texel density**: si hay UVs + textura, calcúlala (px/m).

### 3. Verifica con datos reales, no supongas
Toda medida sale de inspeccionar el archivo real (Blender midiendo el FBX, o leyendo el .meta/.prefab), NUNCA de estimar a ojo. Si algo no se puede leer (p.ej. el asset está comprimido/binario y no hay MCP de Unity), dilo explícito en la ficha en vez de inventarlo.

### 4. Entrega la FICHA de convenciones
Tabla compacta: polycount (tris/verts), texel density, escala/unidades, pivote, naming (objetos/materiales), shader + mapas + packing, rig (tipo/huesos/naming) y clips si aplica, import settings clave. Cierra con **"para replicar este estilo, un asset nuevo debe: ..."** (la spec accionable).

## Reglas
- Aprende las CONVENCIONES técnicas, no copies el asset. Si es comprado/licenciado, respeta la licencia — nunca redistribuir el asset, solo extraer su estándar.
- Cada número con su fuente (qué archivo/medición lo dio). Lo no medible se marca, no se inventa.
- Si hay varios assets, saca el patrón COMÚN (y señala las excepciones) — eso es el style guide real.
