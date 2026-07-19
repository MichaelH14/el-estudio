---
name: juice-pass
description: Use when a game works but feels dead, flat or unresponsive — audits and implements game feel (hit-stop, screenshake, tweens, particles, audio feedback) in priority order. Trigger on "se siente muerto", "le falta juice", "no se siente bien", "dale vida".
---

# /juice-pass — del juego apagado al juego vivo

Auditas el feel del juego y lo implementas en orden de impacto. El juice amplifica un loop que ya divierte — no arregla un loop aburrido (si el problema es el loop, dilo y para: eso es diseño, no juice).

## Conocimiento a cargar

1. `${CLAUDE_PLUGIN_ROOT}/knowledge/gamedev/game-feel.md` — la teoría y el repertorio completo
2. `${CLAUDE_PLUGIN_ROOT}/knowledge/pipeline/feel-en-unity.md` — cada técnica con SU implementación Unity (tweens, Impulse, partículas, pooling)
3. Si hay animaciones flojas: `${CLAUDE_PLUGIN_ROOT}/knowledge/gamedev/animacion.md`
4. Si el audio no acompaña: `${CLAUDE_PLUGIN_ROOT}/knowledge/gamedev/audio.md` + `${CLAUDE_PLUGIN_ROOT}/knowledge/unity/audio-unity.md`

## Flujo

### 1. Auditoría (antes de tocar nada)
Juega/observa el juego real y pasa el diagnóstico de game-feel.md en orden: (1) latencia input→respuesta, (2) curvas de movimiento/física, (3) capa de polish. Lista qué falta por acción del jugador: cada verbo (saltar, golpear, recoger, morir) debe tener feedback visual + sonoro + de cámara proporcional a su importancia.

### 2. Plan en orden de impacto
El checklist ejecutable de feel-en-unity.md: primero lo que más se siente (input feel, hit feedback del verbo principal, SFX por evento), después cámaras, después partículas/flashes/números, al final los detalles. Presenta el plan en corto.

### 3. Implementación
- Técnica por técnica según feel-en-unity.md, con sus valores iniciales recomendados y TODO parametrizado (curvas, duraciones, intensidades editables).
- Regla de dosificación: añade de más y recorta después — pero con toggles/sliders para calibrar.
- Accesibilidad SIEMPRE: screenshake y flashes con opción de reducir/apagar.

### 4. Verificación
El feel solo se evalúa JUGANDO: build/play real, no lectura de código. Compara antes/después con el usuario. Los números de tuning finales quedan documentados en el CHECKPOINT.

## Reglas
- Nunca cambies reglas de gameplay en un juice pass (daño, velocidades de diseño) — solo percepción. Si detectas un problema de diseño, repórtalo aparte.
- Pooling obligatorio para todo lo que spawnea en caliente (partículas, números, audio sources).
- Sonido = 50% del feel: ningún pase está completo si los eventos clave no suenan.
