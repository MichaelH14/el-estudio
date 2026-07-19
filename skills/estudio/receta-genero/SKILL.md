---
name: receta-genero
description: Use when building the technical foundation of a game of a known genre in Unity (platformer, top-down, puzzle, endless, idle, roguelite) — applies the proven recipe instead of improvising architecture. Trigger on "monta la base de un plataformas", "cómo armo un idle", "estructura para un roguelite".
---

# /receta-genero — base técnica probada por género

Montas la fundación técnica de un género siguiendo su receta, no improvisando.

## Conocimiento a cargar

1. `${CLAUDE_PLUGIN_ROOT}/knowledge/pipeline/recetas-generos.md` — LA receta del género pedido (arquitectura, componentes, paquetes, riesgos)
2. `${CLAUDE_PLUGIN_ROOT}/knowledge/pipeline/estructura-proyecto.md` — estructura y convenciones
3. Según el género, los archivos unity/ que la receta señale (física, input, tilemaps en recetas, UI…)
4. Si el género no está en las recetas: `${CLAUDE_PLUGIN_ROOT}/knowledge/gamedev/generos.md` para derivar los pilares y construir la receta más cercana (dilo explícito: "receta derivada, no probada").

## Flujo

1. **Confirma el género y sub-género exacto** con el usuario si hay ambigüedad (top-down ≠ twin-stick ≠ isométrico). Lee las expectativas del jugador del género — eso define qué es obligatorio.
2. **Presenta el plan de la receta** en corto: sistemas a crear, orden, y los 3-5 riesgos técnicos del género con su mitigación. OK del usuario si el alcance es grande.
3. **Construye en el orden de la receta**, verificando cada sistema en play mode antes del siguiente. Riesgos del género primero (lo que puede matar el proyecto se prueba antes).
4. **Entrega**: lista de qué quedó montado, qué falta para "jugable", y los ajustes de feel recomendados (→ `/juice-pass` cuando haya gameplay).

## Reglas
- La receta manda; si te desvías de ella, justifica por qué en una línea.
- Cada sistema con su verificación real (play mode / test), nunca "debería funcionar".
- Deja los valores de tuning (velocidades, gravedad, cooldowns) en ScriptableObjects o campos serializados — el tuning fino viene después y debe ser editable sin tocar código.
