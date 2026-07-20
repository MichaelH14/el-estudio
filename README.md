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
  modelado/   Fase 5 — modelado 3D para juegos (teoría agnóstica)
  blender/    Fase 6 — Blender 5.x a fondo (en construcción)
agents/
  director.md El agente principal: carga el conocimiento según la tarea
skills/       Flujos de trabajo (en construcción)
commands/     Comandos (en construcción)
```

Cada archivo de `knowledge/` es un manual operativo destilado de fuentes reales (libros canon, charlas GDC, postmortems, documentales, artículos técnicos), escrito para ser leído por un agente IA: denso, accionable, con fuentes citadas.

## Estado

**Bloque A — Juegos + Unity**
- ✅ Fase 0 — Esqueleto del plugin
- ✅ Fase 1 — Conocimiento de videojuegos en general (14 archivos + índice, fuentes citadas)
- ✅ Fase 2 — Conocimiento de Unity (14 archivos + índice, verificado contra docs de Unity 6)
- ✅ Fase 3 — El pipeline unido (13 archivos puente + índice, incl. publicación en tiendas)
- ✅ Fase 4 — Ensamblaje v1: director + 4 skills (/nuevo-juego, /receta-genero, /juice-pass, /ship-check)

**Bloque B — Arte 3D con Blender ✅ COMPLETO**
- 🔨 Fases 5–12 — ✅Modelado 3D (11) → ✅Blender (12) → ✅modelado en Blender (8) → ✅Texturizado (8) → ✅Rigging (8) → ✅Animación 3D (8) → ✅Animación en Blender (7) → ✅Pipeline de assets (4) + skills /asset-3d y /aprender-asset (incl. addons, bpy, blender-mcp) → modelado en Blender → texturizado → rigging → animación → animación en Blender → pipeline de assets Blender↔Unity

**Bloque C — Transversal ✅ COMPLETO**
- ✅ Fase 13 — Diseño UX/UI general (8) · ✅ Fase 14 — Equipo de 7 agentes · ♾️ Mejora continua

Detalle completo en [PLAN.md](PLAN.md).

## Instalación

```
/plugin marketplace add MichaelH14/el-estudio
/plugin install el-estudio@michael-games
```

## Licencia

MIT
