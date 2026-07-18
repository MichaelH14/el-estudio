# El Estudio — Plan maestro

> Plugin de Claude Code que convierte a un agente IA en un estudio de videojuegos completo (diseño + Unity), diseñado para funcionar con Opus cuando Fable ya no esté. La inteligencia vive en los archivos, no en el modelo.

## Principio rector

Un modelo menos capaz + un manual perfecto ≥ un modelo más capaz sin manual. Todo el conocimiento se destila en markdown: reglas, checklists, recetas, pitfalls, con fuentes reales citadas. Nada depende de que el modelo "ya lo sepa".

## Reglas del conocimiento (estilo obligatorio de cada archivo)

1. **Lector = agente IA** trabajando en un juego real. No es un tutorial para humanos.
2. Español, términos técnicos en inglés donde son estándar (core loop, game feel, draw call).
3. Denso: tablas y listas > párrafos. Cero relleno, cero frases motivacionales.
4. Cada archivo abre con "**Cuándo cargar este archivo**" (progressive disclosure: el director carga solo lo relevante).
5. Cierra con **Reglas prácticas** (checklist), **Errores comunes** y **Fuentes** (título — origen).
6. Nada inventado: cada afirmación importante sale de una fuente real. Lo no verificado se marca o se omite.
7. Repo público: conocimiento genérico, nunca datos de clientes ni proyectos privados.

## Fases

### ✅ Fase 0 — Esqueleto
Estructura del plugin (formato calcado de El Coro), repo público en MichaelH14, plan.

### ✅ Fase 1 — Videojuegos en general (`knowledge/gamedev/`)
Completada 2026-07-18: 14 archivos + INDEX.md, ~3.650 líneas. Proceso: 29 agentes (14 investigadores + 14 críticos adversariales + 1 editor de coherencia), 0 caídos. Veredictos: 13 reparados, 1 ok, 0 débiles. Huecos globales detectados (programación/arquitectura, netcode, QA técnico, git/CI, i18n) son scope de las fases 2 y 3 — ver abajo. Investigación con fuentes reales: libros canon, charlas GDC, postmortems, documentales, artículos, noticias. Los 14 archivos:

| Archivo | Tema |
|---|---|
| fundamentos-diseno | Qué hace divertido un juego: MDA, core loops, flow, balance, motivación |
| mecanicas-sistemas | Catálogo de mecánicas, economías internas, progresión, RNG |
| generos | Convenciones y pilares por género + estado del mercado |
| level-design | Enseñar jugando, pacing, composición espacial, encounter design |
| game-feel | Juice: screenshake, hit-stop, tweening, cámaras, feedback |
| arte-direccion | Dirección de arte, estilos y sus costes, color, readability, style guides |
| animacion | 12 principios aplicados, sprites vs esquelética, telegraphing |
| narrativa-guion | Estructura, worldbuilding, diálogo, branching, ludonarrativa, storyboards |
| preproduccion | Pitch, GDD moderno, paper prototype, vertical slice, scoping para 1 dev |
| produccion-proceso | Milestones, playtesting, iteración, polish, lecciones de postmortems |
| historia-lecciones | Historia del medio destilada en lecciones de diseño extraíbles |
| audio | SFX, música adaptativa, silencio, implementación práctica |
| ux-ui-onboarding | HUD, menús, tutoriales, accesibilidad, UX móvil |
| psicologia-retencion-negocio | Motivación, retención, modelos de negocio y su ética |

Proceso por archivo: investigador (busca fuentes reales y escribe) → crítico adversarial (repara) → pase de coherencia global (INDEX.md, solapes).

### ⬜ Fase 2 — Unity a fondo (`knowledge/unity/`)
Mismo proceso. Temas previstos (~14): arquitectura (GameObjects/prefabs/lifecycle), patrones C#, física, Input System, UI (uGUI/UI Toolkit), animación, rendering/URP, audio, rendimiento/móvil, builds por plataforma, pipeline de assets + git, Unity 6.x actualidad, gotchas, flujo con Unity MCP.

### ⬜ Fase 3 — La unión (`knowledge/pipeline/`)
De idea a juego terminado EN Unity (~11): pipeline completo por milestones, recetas por género, estructura de proyecto, arte→Unity, juice en Unity (recetas de código), UI/flujo completo, narrativa en Unity + localización, sistemas meta (save, economía, IAP/ads), multijugador/netcode, testing/QA, producción solo-dev. (Cubre los huecos globales que la fase 1 detectó: netcode, QA técnico, i18n; programación/arquitectura y git/CI van en fase 2.)

### ⬜ Fase 4 — Ensamblaje
- `agents/director.md` completo: enruta por tarea, carga conocimiento por índice.
- Skills: `/nuevo-juego` (idea→GDD→scaffold), `/receta` (género→plan Unity), `/juice-pass`, `/ship-check`…
- Instalación local vía marketplace propio y prueba real: crear un mini-juego usando SOLO el plugin.

### ♾️ Fase 5 — Mejora continua
Cada juego real que se haga con el plugin retroalimenta el conocimiento (nuevos pitfalls, recetas probadas).

## Decisiones tomadas

- **Nombre**: El Estudio (provisional, renombrable). Agente principal: `director`.
- **Repo**: público, `MichaelH14/el-estudio` (personal, NO MEK). Licencia MIT.
- **Idioma**: español con términos técnicos en inglés.
- **Modelo del agente**: sin override — hereda el modelo de la sesión (debe funcionar igual con Opus).
- **Fase 1 se escribe con el mejor modelo disponible hoy**: el manual que le quede a Opus lo redacta Fable mientras exista.
