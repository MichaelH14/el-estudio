---
name: asset-3d
description: Use when producing a complete 3D game asset from scratch — from reference to a game-ready prefab in Unity — orchestrating the full Blender pipeline (model → UV → texture → rig → animate → export → import). Trigger on "modélame un/una <prop/arma/vehículo/personaje>", "haz este asset 3D", "necesito un modelo de X para el juego".
---

# /asset-3d — de la referencia al prefab game-ready en Unity

Produces un asset 3D completo orquestando todo el pipeline del bloque de arte 3D. Operas Blender por MCP/headless y cierras en Unity.

## Conocimiento a cargar

1. `${CLAUDE_PLUGIN_ROOT}/knowledge/pipeline-assets/pipeline-completo-3d.md` — el MAPA MAESTRO (todas las etapas y sus gates)
2. `${CLAUDE_PLUGIN_ROOT}/knowledge/blender/blender-mcp-operativo.md` — SIEMPRE antes de operar Blender por MCP
3. Por etapa, la base que toque: `pipeline-3d/` (modelar), `texturizado/`, `rigging/`, `animacion-blender/`, y `pipeline-assets/blender-unity-bridge.md` (el export/import)

## Flujo (cada etapa con su gate verificable — no avances sin pasarlo)

### 1. Definir el asset
Tipo (prop/arma/vehículo/entorno/personaje), estilo (realista/estilizado/low-poly), presupuesto (tris/texturas/plataforma), si es estático o animado. Reúne o genera las referencias (blueprints/turnaround) [ver: modelado/blueprints-referencias]. OK del usuario en scope antes de modelar.

### 2. Modelar en Blender
Sigue la receta del tipo en `pipeline-3d/` (blockout a escala → game-ready). **Gate:** escala métrica, tris dentro de presupuesto, topología sana, pivote correcto — verificados por código contra el binario real, no a ojo.

### 3. UV + Texturizar
UV unwrap, mapas PBR (o vertex color si es low-poly), export de texturas. **Gate:** texel density consistente, sin distorsión grave, mapas con el color space correcto.

### 4. (Si animado) Rig + Animar
Esqueleto, weights, deformación probada posando; clips necesarios; hornear lo procedural. **Gate:** deforma sin pinch, ≤4 influencias por defecto, clips loopean.

### 5. Export + Import a Unity
Export FBX con los settings exactos de `blender-unity-bridge.md`; import en Unity; material URP; LODGroup/colliders/sockets; ensamblar el prefab. **Gate:** escala 1, rotación 0, normales bien, un material por slot, (Humanoid mapea si aplica).

### 6. Verificación final en el engine
El asset en Unity bajo el shader real y luz real, en el prefab, jugado/mirado — NO el "render bonito de Blender". Pasa el checklist game-ready unificado. Reporta con evidencia (medidas, capturas) qué pasó cada gate.

## Reglas
- Un dev + un agente: scope brutal, la versión más simple que cumpla. Recorta el detalle a la distancia de cámara real del asset.
- Cada gate se verifica con datos reales (medición por código, captura del viewport/engine), nunca "debería estar bien".
- Lo expresivo de la animación (acting fino) puede necesitar mano humana — dilo, no finjas que un agente ciego lo clava.
- El source (.blend) se conserva y queda trazable al prefab [ver: pipeline-assets/organizacion-versionado-3d].
