# El Estudio 🎮

Plugin de Claude Code para crear videojuegos con Unity desde cero.

## La idea

Los modelos de IA cambian; el conocimiento escrito se queda. El Estudio destila en archivos markdown todo lo que un agente necesita saber para hacer videojuegos — game design, arte, narrativa, historia del medio, Unity, y el pipeline completo de idea a juego terminado — para que **cualquier modelo** (está diseñado pensando en Opus) pueda operar como un estudio de videojuegos completo.

La inteligencia vive en los archivos, no en el modelo.

## Estructura

```
knowledge/
  gamedev/    Fase 1 — cómo se hacen los videojuegos (diseño, arte, narrativa, historia…)
  unity/      Fase 2 — el motor: Unity a fondo
  pipeline/   Fase 3 — la unión: de idea a juego terminado EN Unity
agents/
  director.md El agente principal: carga el conocimiento según la tarea
skills/       Flujos de trabajo (en construcción)
commands/     Comandos (en construcción)
```

Cada archivo de `knowledge/` es un manual operativo destilado de fuentes reales (libros canon, charlas GDC, postmortems, documentales, artículos técnicos), escrito para ser leído por un agente IA: denso, accionable, con fuentes citadas.

## Estado

- ✅ Fase 0 — Esqueleto del plugin
- ✅ Fase 1 — Conocimiento de videojuegos en general (14 archivos + índice, fuentes citadas)
- 🔨 Fase 2 — Conocimiento de Unity
- ⬜ Fase 3 — El pipeline unido (juegos + Unity)
- ⬜ Fase 4 — Ensamblaje: agente director + skills + commands
- ♾️ Fase 5 — Mejora continua

## Instalación

```
/plugin marketplace add MichaelH14/el-estudio
/plugin install el-estudio@michael-games
```

## Licencia

MIT
