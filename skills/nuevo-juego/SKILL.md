---
name: nuevo-juego
description: Use when starting a new game from an idea — turns a raw concept into a validated core loop, a one-page GDD, a genre recipe and a day-0 Unity project ready to prototype. Trigger on "quiero hacer un juego de X", "tengo una idea", "empecemos un juego nuevo".
---

# /nuevo-juego — de la idea al proyecto listo

Llevas una idea cruda hasta un proyecto Unity con el core loop en prototipo. NO saltes etapas: cada una tiene criterio de salida.

## Conocimiento a cargar (en este orden, solo lo que la etapa pida)

1. SIEMPRE: `${CLAUDE_PLUGIN_ROOT}/knowledge/gamedev/preproduccion.md` + `${CLAUDE_PLUGIN_ROOT}/knowledge/gamedev/fundamentos-diseno.md`
2. Al elegir género: `${CLAUDE_PLUGIN_ROOT}/knowledge/gamedev/generos.md` + `${CLAUDE_PLUGIN_ROOT}/knowledge/pipeline/recetas-generos.md`
3. Al montar el proyecto: `${CLAUDE_PLUGIN_ROOT}/knowledge/pipeline/pipeline-completo.md` (checklist día 0) + `${CLAUDE_PLUGIN_ROOT}/knowledge/pipeline/estructura-proyecto.md`

## Etapas

### 1. Filtrar la idea (no toques Unity todavía)
- Aplica los filtros de preproduccion.md: ¿cuál es el core loop (qué HACE el jugador cada 30s)? ¿por qué divierte al minuto 1 y al 10? ¿cuál es el "toy"?
- Si la idea no pasa los filtros, dilo claro y propón el recorte que la salvaría. No construyas sobre una idea sin loop.
- Salida: el loop descrito en 2-3 frases + la promesa del juego en 1 frase.

### 2. Concepto y GDD de 1 página
- Género y sus convenciones obligatorias (generos.md) + alcance realista para 1 dev.
- GDD ligero según preproduccion.md: loop, verbos, progresión, arte (dirección en 1 frase), plataforma target, lista de corte (qué se elimina primero si hay que recortar).
- Pregunta al usuario SOLO las decisiones de producto que no puedas derivar (plataforma, 2D/3D, tono). Batchea las preguntas.
- Salida: `GDD.md` en la raíz del proyecto + OK del usuario.

### 3. Proyecto Unity día 0
- Sigue el checklist de arranque de pipeline-completo.md paso a paso (versión LTS, plantilla URP, settings, git+LFS, estructura de carpetas de estructura-proyecto.md).
- Crea también `CHECKPOINT.md` (estado + decisiones + qué sigue) — se actualiza SIEMPRE al final de cada sesión de trabajo.
- Salida: proyecto compila, primer commit hecho.

### 4. Prototipo gris del core loop
- Solo el loop, en greybox, sin arte ni menús (receta del género como guía técnica).
- Criterio de salida: el toy se siente bien Y el loop completo es jugable. Si tras iterar no divierte en gris → recomienda kill/pivot con honestidad (preproduccion.md: kill criteria).

## Reglas
- Verifica en el editor/build real cada etapa antes de declararla lista (consola sin errores, play mode probado — ver `${CLAUDE_PLUGIN_ROOT}/knowledge/unity/unity-mcp-flujo.md` si hay MCP conectado).
- Scope brutal: ante la duda, la versión más chica.
- Nada de assets finales, marketing ni features "para después" en esta skill — eso viene en producción.
