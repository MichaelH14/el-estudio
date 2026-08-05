---
name: medir-diversion
description: >-
  Use when a game "works but isn't fun" and nobody can say why — runs
  measured, recurring playtest rounds with a numeric score so the fun becomes
  a tracked number instead of an opinion. Trigger on "no es divertido", "algo
  falla pero no sé qué", "el combate se siente flojo", "¿esto divierte?",
  "medir si divierte", "playtest".
---

# /medir-diversion — convertir "no es divertido" en un número que sube

"No es divertido" es la única crítica que no se puede accionar, y es la que más se repite. Esta skill la convierte en una **serie numérica con pendiente**, usando el método que rescató el combate de Dragon Age: Inquisition (de 1,2 a 8,8 sobre 10 en cuatro semanas).

Compatibilidad: si `${CLAUDE_PLUGIN_ROOT}` no existe, usa la raíz del repo/plugin como `EL_ESTUDIO_ROOT` y resuelve las rutas desde ahí.

⛔ **Esta skill no arregla nada por sí sola.** Mide, aísla la causa y ordena qué tocar. Implementar es del `ingeniero`; si la conclusión es que el problema es el loop y no el feel, es del `disenador`.

## Conocimiento a cargar

1. `${CLAUDE_PLUGIN_ROOT}/knowledge/gamedev/casos-produccion.md` §6 — el método original y por qué funciona.
2. `${CLAUDE_PLUGIN_ROOT}/knowledge/gamedev/produccion-proceso.md` — protocolo de sesión de playtest (método Valve): qué preguntar, qué NO preguntar, cómo observar sin contaminar.
3. `${CLAUDE_PLUGIN_ROOT}/knowledge/gamedev/fundamentos-diseno.md` — tabla síntoma→sección, para traducir la queja a una causa de diseño.
4. Si el diagnóstico apunta a percepción y no a diseño: `${CLAUDE_PLUGIN_ROOT}/knowledge/gamedev/game-feel.md` (y de ahí a `/juice-pass`).

## El método

### 1. Aislar qué se mide

Una ronda mide **una cosa**: el combate, o el loop de una noche, o el primer minuto. No "el juego".

Construye **escenarios a propósito** para eso — no vale "juega la build". El original construyó encuentros de combate específicos para poder atribuir el resultado a una variable. Si mides combate: tres o cuatro encuentros cortos que aíslen situaciones distintas (uno contra uno, rodeado, con poca vida, con el recurso agotado).

Criterio de salida: sabes qué pregunta responde esta ronda y tienes el escenario que la responde.

### 2. La encuesta (siempre la misma)

Corta, numérica y constante entre rondas, o no hay pendiente que comparar:

```
1. Del 1 al 10, ¿cuánto te divirtió?            [1-10]
2. ¿Qué fue lo mejor?                            [texto libre, 1 frase]
3. ¿Qué te frustró?                              [texto libre, 1 frase]
4. ¿Qué creías que iba a pasar y no pasó?        [texto libre, 1 frase]
5. ¿Jugarías otra ronda ahora mismo?             [sí / no]
```

- La pregunta 1 es la métrica. Las otras cuatro explican el número.
- La 4 detecta expectativas rotas, que es de donde sale la mitad de la frustración.
- La 5 es el mejor predictor de retención que cabe en una pregunta.
- ⛔ Nunca preguntes "¿qué le añadirías?". El jugador diagnostica bien y receta mal.

### 3. La cadencia

**Corta, obligatoria y recurrente**: ~1 hora, una vez por semana, mínimo cuatro semanas seguidas. Entre rondas se cambia **poco y a propósito**, para que el número signifique algo.

Adaptación por tamaño de equipo (el original tenía un estudio entero):

| Situación | Cómo se hace |
|---|---|
| Equipo pequeño | Todos juegan y rellenan. Sin excepciones: el que no juega no opina |
| **Dev solo o dúo** | 3-5 personas externas fijas (amigos, Discord, familia) que repiten cada ronda. **La constancia del grupo importa más que su tamaño** |
| Nadie disponible | Te mides tú, pero solo la 3 y la 4 valen; tu propia nota está contaminada y lo sabes |

⚠️ Rota parcialmente a los testers a partir de la ronda 3: quien ya jugó cuatro veces ha aprendido tus controles y deja de detectar lo que rompe a alguien nuevo (es el error de la "regla de ocho" de Halo Wars — los diseñadores, de tanto testear, querían complicar unos controles que a un novato ya le costaban).

### 4. Leer el resultado

- **Lo que importa es la pendiente, no el valor.** Un 4 que la semana siguiente es 6 es una buena noticia; un 7 estancado tres rondas es una mala.
- Agrupa los textos libres y **busca tendencias, no frases**. Una persona aburrida puede tener un mal día; cinco personas frustradas en el mismo punto es un dato.
- **Un 1,2 inicial no es un fracaso, es una línea base.** El efecto documentado: la moral del equipo mejoró la misma semana que salió el 1,2, porque dejaron de esquivar el problema.
- Si tras dos rondas de cambios el número no se mueve, **estás tocando la variable equivocada** — vuelve al paso 1 y aísla otra cosa.

### 5. Actuar en orden

Con las tendencias en la mano, la prioridad es siempre la misma:

1. Lo que **frustra** (quita puntos rápido).
2. Lo que **se esperaba y no pasó** (expectativa rota = injusticia percibida).
3. Lo que ya está bien pero puede brillar (esto es lo último, y es donde todos quieren empezar).

Regla de priorización heredada de Naughty Dog: **atiende lo que está al 60% antes de pulir lo que ya está al 95%.**

Y el gate honesto: si la nota no sube tras varias rondas atacando bien las causas, la conclusión puede ser que **el loop no divierte**, no que le falte pulido. Eso es diseño ([ver: gamedev/fundamentos-diseno]) o kill criteria ([ver: gamedev/preproduccion]), y hay que decirlo en voz alta en vez de seguir puliendo.

## Salida

Un registro acumulativo (en `Docs/PLAYTEST.md` del proyecto, o donde viva la memoria viva):

```markdown
## Ronda N — fecha — qué se midió
Nota media: X,X  (ronda anterior: Y,Y)
Testers: N (M repiten)
Tendencias — frustración: ...
Tendencias — expectativa rota: ...
Cambios que entran para la próxima ronda: ... (pocos y a propósito)
```

Y una línea en el `CHECKPOINT.md`, porque es evidencia de estado del proyecto igual que un test que pasa.

## Reglas

- Una ronda mide una cosa. Si mides todo, no mides nada.
- Misma encuesta siempre; cambiarla borra la serie.
- Pocos cambios entre rondas, elegidos a propósito.
- Observa callado: no expliques cómo se juega, no defiendas el diseño, no ayudes. Lo que el tester no entiende solo, no está en el juego.
- Tendencias, no anécdotas.
- La nota es para navegar, no para presumir: no se enseña fuera del equipo.
- Si el número no se mueve en dos rondas, cambia de variable, no de intensidad.
