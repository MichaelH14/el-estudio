# El Estudio — Instrucciones para Codex

Este repo es un plugin/manual operativo para crear videojuegos con IA. Cuando trabajes aquí:

- Trata la raíz del repo como `EL_ESTUDIO_ROOT`.
- Si una skill menciona `${CLAUDE_PLUGIN_ROOT}`, resuélvelo como `EL_ESTUDIO_ROOT` cuando estés en Codex.
- Antes de diseñar o implementar juegos, carga primero el índice de la base relevante en `knowledge/*/INDEX.md`.
- No declares terminado nada de Unity/Blender sin evidencia: consola, test, build, medición o captura.
- Actualiza `GDD.md`, `CHECKPOINT.md` y `CORTE.md` cuando una sesión cambie el estado de un juego.
- Ejecuta `python3 tools/validate_repo.py` antes de publicar cambios del plugin.
