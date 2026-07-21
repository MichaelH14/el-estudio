---
name: memoria-juego
description: Use to create or update the persistent memory of a game project so any future session can resume without losing context — the living GDD, the CHECKPOINT (what's done, what's next, decisions taken), and the cut list. Trigger on "guarda el estado del juego", "actualiza el checkpoint", "retomemos el juego" (to load), or automatically at the end of a work session on a game.
---

# /memoria-juego — la memoria viva de un juego

Mantienes, dentro del propio proyecto del juego, los documentos que dejan retomarlo en cualquier sesión sin perder contexto. Es la memoria del juego, separada de la memoria personal del usuario.

## Dónde vive

En la RAÍZ del proyecto del juego (no en el plugin, no en la memoria global), tres archivos versionados con el juego:

- `GDD.md` — el diseño vivo de 1 página: core loop, verbos, progresión, arte en 1 frase, plataforma, alcance. Se actualiza cuando el diseño cambia. Formato: [ver: gamedev/preproduccion].
- `CHECKPOINT.md` — el estado: qué está hecho ✅, qué sigue ⬜, decisiones tomadas y su porqué, y lo que está a medias ⚠️ (con dónde quedó). Se actualiza al FINAL de cada sesión de trabajo.
- `CORTE.md` — la lista de corte: qué se elimina primero si hay que recortar scope, mantenida desde el día 1 [ver: gamedev/preproduccion].

## Al GUARDAR (fin de sesión, o "guarda el estado")

1. Actualiza `CHECKPOINT.md`: mueve a ✅ lo terminado y verificado (con la evidencia de que se verificó), deja en ⚠️ lo a medias con el punto exacto donde quedó, y en ⬜ lo siguiente en orden.
2. Registra las decisiones nuevas y su porqué (para no re-litigarlas la próxima sesión).
3. Si el diseño cambió, actualiza `GDD.md`; si el scope cambió, `CORTE.md`.
4. Sé honesto: lo no verificado NO va como ✅ — va como ⚠️ "hecho, sin comprobar".

## Al RETOMAR ("retomemos el juego")

1. Lee `CHECKPOINT.md` primero, luego `GDD.md`. Ahí está el estado y el porqué de las decisiones.
2. Retoma por lo que esté en ⚠️ (a medias) o el siguiente ⬜, sin re-hacer lo ✅ ni re-decidir lo ya decidido.
3. Si algo en el checkpoint contradice lo que ves en el proyecto real, gana la realidad — verifica y corrige el checkpoint.

## Reglas

- La memoria del juego vive CON el juego (en su repo), no en el plugin ni en la memoria personal — así viaja con el proyecto y sobrevive cualquier sesión o modelo.
- Un CHECKPOINT es inútil si miente: el estado tiene que reflejar la realidad verificada, no la intención. Un ✅ sin evidencia es un ⚠️.
- Cortito y vivo: nada de GDD de 100 páginas. El valor es retomar rápido, no documentar por documentar [ver: gamedev/preproduccion].
