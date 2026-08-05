# {{GAME_NAME}} — Unity Day 0

Este overlay prepara un proyecto Unity para trabajar con El Estudio.

## Uso

1. Crea un proyecto Unity vacío o abre una carpeta nueva.
2. Ejecuta `python3 tools/scaffold_unity_day0.py <ruta> --game-name "{{GAME_NAME}}"` desde el repo de El Estudio.
3. Abre el proyecto en Unity.
4. Ejecuta el test `Day0SmokeTest`.
5. Actualiza `CHECKPOINT.md` con evidencia real.

## Contrato

- `GDD.md` define el loop y alcance.
- `CHECKPOINT.md` dice qué está verificado y qué no.
- `CORTE.md` mantiene el scope bajo control.
- `ASSET_PROVENANCE.md` se copia por cada asset externo o generado.

## Herramientas de iteración (menú `El Estudio` en el editor)

`Assets/ElEstudio/Editor/DevTools.cs` añade lo que más acelera el bucle cambio→verlo,
que es la métrica de productividad que más pesa en un proyecto de juego:

- **Arrancar siempre desde la escena inicial** — al dar Play carga la escena 0 de Build
  Settings aunque estés editando otra. Se acabó el "peta porque no se inicializó nada".
- **Velocidad x0.25 / x1 / x4** (Alt+1/2/3 en Play mode) — para no esperar animaciones ni timers.
- **Borrar progreso guardado** — probar la primera partida sin buscar dónde vive el save.
- **Abrir CHECKPOINT.md** sin salir del editor.

Es código de editor: no entra en el build.
