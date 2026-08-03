# Nightfall Protocol MVP — Caso de Referencia

Este ejemplo documenta el tipo de evidencia que El Estudio debe exigir cuando construye un juego real con Unity.

## Contexto

- Juego: survival horror asimétrico offline con bots, inspirado por el hueco móvil dejado por juegos tipo `Dead by Daylight Mobile`, sin copiar IP.
- Objetivo MVP: loop jugable con corredor, bots, perseguidor, objetivos y salida.
- Motor: Unity 6.
- Arte: primitivas/modelos simples generados para validar loop antes de producción visual.

## Loop Validado

1. Runner explora arena.
2. Activa relays.
3. Stalker patrulla/persigue.
4. Bots simulan presión sistémica.
5. Gate se abre al completar objetivos.

## Evidencia Esperada

- Escena abre sin errores.
- Play mode ejecuta el loop.
- Smoke test confirma objetos críticos.
- `CHECKPOINT.md` registra qué está verificado y qué no.

## Evidencia Real De Este Caso

- Proyecto: `~/UnityProjects/NightfallProtocolMVP` (fuera del plugin, sin git).
- Editor: Unity `6000.3.18f1`, 2026-07-24.
- `NightfallSmokeTest.cs` en este directorio es **copia literal** del que corrió en el proyecto
  (`Assets/NightfallProtocol/Editor/NightfallSmokeTest.cs`), no una reescritura.
- Ejecución real, headless:

  ```bash
  /Applications/Unity/Hub/Editor/6000.3.18f1/Unity.app/Contents/MacOS/Unity \
    -quit -batchmode -nographics \
    -projectPath ~/UnityProjects/NightfallProtocolMVP \
    -executeMethod NightfallProtocol.Editor.NightfallSmokeTest.Run
  ```

- Salida registrada en `Logs/nightfall-smoke.log`:
  `Nightfall smoke test passed: scene builds, agents spawn, objectives exist, and paths resolve.`
- `Logs/nightfall-playtest.log` (play mode, 2026-07-24 19:10): 0 excepciones y 0 NullReference.

## Huecos Detectados Para El Plugin

- Necesita plantilla Unity día 0 con smoke test.
- Necesita `CHECKPOINT.md` obligatorio desde la primera sesión.
- Necesita doctor de MCP antes de operar Unity/Blender.
- Necesita caso de mercado antes de invertir en arte final.

Este caso no sustituye un juego completo publicado. Es una barra mínima: cada proyecto real debe dejar evidencia igual o mejor.
