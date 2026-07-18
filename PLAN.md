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

### ⬜ Fase 4 — Ensamblaje v1
- `agents/director.md` completo: enruta por tarea, carga conocimiento por índice.
- Skills: `/nuevo-juego` (idea→GDD→scaffold), `/receta` (género→plan Unity), `/juice-pass`, `/ship-check`…
- Instalación local vía marketplace propio y prueba real: crear un mini-juego usando SOLO el plugin.

## Bloque B — Arte 3D con Blender (ampliación 2026-07-18)

Mismo patrón de tres pasos (general → herramienta → unión) aplicado al arte 3D. Orden:

### ⬜ Fase 5 — Modelado 3D general (`knowledge/modelado/`)
Teoría agnóstica de herramienta: topología (quads, edge flow, poles), hard-surface vs orgánico, high-poly→low-poly y normal baking, presupuestos de polígonos por plataforma, escala y proporción, y **las categorías de modelo con su método propio**: props/cosas, estructuras/entornos (modular kits), personajes, vehículos, armas. Incluye **blueprints**: referencias ortográficas (front/side/top) — conseguirlas, hacerlas y montarlas para modelar encima.

### ⬜ Fase 6 — Blender: la herramienta (`knowledge/blender/`)
Blender 5.x a fondo: interfaz/atajos/workflow, edit mode y herramientas de malla, modificadores (el stack canónico), geometry nodes, sculpting, **el ecosistema open source**: addons famosos y cuáles valen (gratis y de pago), la API Python (bpy), cómo escribir addons propios / modificar Blender, extensiones oficiales. Y **la conexión para agentes**: blender-mcp (operar Blender desde el plugin, igual que Unity MCP).

### ⬜ Fase 7 — Unión: modelado EN Blender
Recetas por categoría: modelar un prop, un kit modular de entorno, un personaje, un vehículo, un arma — game-ready (low-poly, topología limpia), de referencia/blueprint a malla terminada.

### ⬜ Fase 8 — Texturizado (`knowledge/texturizado/`)
UV unwrapping (seams, packing, texel density), PBR (albedo/metallic/roughness/normal), baking high→low, texturizado en Blender (painting, procedural con nodos), estilos (stylized vs realista), atlas y trim sheets, export correcto a Unity/URP.

### ⬜ Fase 9 — Rigging (`knowledge/rigging/`)
Esqueletos: jerarquía de huesos, weights/skinning limpio, IK/FK, Rigify y rigs game-ready, deformación correcta (hombros, caderas), rigs de props/vehículos/armas, export a Unity (Humanoid vs Generic, retargeting).

### ⬜ Fase 10 — Animación 3D general (`knowledge/animacion3d/`)
De los 12 principios (ya en gamedev/animacion) al nivel producción 3D: ciclos (walk/run/idle), animación de combate para juegos, keyframes/curvas/interpolación, mocap básico y librerías (Mixamo etc.), animación por capas.

### ⬜ Fase 11 — Unión: animación EN Blender
Action editor, NLA, graph editor en la práctica; animar el personaje riggeado; export de clips a Unity/Mecanim sin dolores (escala, rotaciones, root motion).

### ⬜ Fase 12 — Pipeline de assets completo + aprender de assets existentes
Blender↔Unity de punta a punta (FBX/glTF, escalas, ejes, materiales, colliders). Y la skill **/aprender-asset**: Michael le pasa un asset de Unity (FBX, prefab, atlas, material) y el agente lo analiza — polycount, topología, texel density, convenciones de nombres, rig — y destila sus convenciones para replicar el estilo.

## Bloque C — Transversal

### ⬜ Fase 13 — Diseño UX/UI (`knowledge/ux-ui/`)
Diseño de interfaces en general (no solo juegos): fundamentos (jerarquía, tipografía, color, espaciado, grids), sistemas de diseño, patrones de apps web/móvil, accesibilidad, herramientas y handoff. Complementa gamedev/ux-ui-onboarding (que es de juegos).

### ⬜ Fase 14 — Ensamblaje v2: el equipo de agentes
Roster previsto (cada agente = un rol que carga SU parte del conocimiento; sin override de modelo):
| Agente | Rol | Conocimiento que carga |
|---|---|---|
| `director` | Orquesta todo, decide, GDD, scope | índices + gamedev/preproduccion |
| `disenador` | Mecánicas, balance, niveles, feel | gamedev/* |
| `ingeniero` | Implementa en Unity/C#, opera Unity MCP | unity/* + pipeline/* |
| `artista-3d` | Modela y texturiza, opera blender-mcp | modelado/blender/texturizado |
| `animador` | Rigging + animación | rigging/animacion3d |
| `ux-ui` | Interfaces, HUD, onboarding, arte 2D de UI | ux-ui + gamedev/arte-direccion |
| `qa` | Audita: feel pass, rendimiento, checklist de ship; no se auto-aprueba | gotchas + reglas prácticas de todos |

### ♾️ Mejora continua
Cada juego real retroalimenta el conocimiento (pitfalls nuevos, recetas probadas). Los huecos que un agente reporte ("necesitaba X y no estaba") se convierten en investigación.

## Ideas propuestas (pendientes de OK de Michael)

- **Arte 2D / pixel art** (`knowledge/arte2d/`): sprites, pixel art, Aseprite, spritesheets/atlas, animación 2D frame a frame — la mayoría de los juegos chicos son 2D y el bloque B es 3D.
- **VFX y shaders**: Shader Graph con recetas (disolve, hit flash, outline, agua), partículas/VFX Graph, el "juice visual" a nivel implementación.
- **Creación de audio**: generar SFX (jsfxr/ChipTone), música con herramientas e IA, grabación casera — la fase 1 cubre teoría, no producción.
- **IA generativa para assets**: cuándo y cómo usar generación de imagen/3D/audio, con licencias claras, y sus límites de calidad.
- **Memoria por juego**: el plugin mantiene GDD + CHECKPOINT + decisiones de cada juego para retomar en cualquier sesión sin perder contexto.
- **QA automatizado de juegos**: Unity Test Framework + tests de gameplay + smoke tests de builds.

## Infra local (Mac de Michael)

- Blender: 4.3.0 viejo pendiente de borrar (es de la cuenta `jeanmichaelhiraldopimentel`, requiere sudo de Michael); Blender 5.2.0 ya descargado vía brew cask, listo para instalar. Config de usuario 4.2/4.3 se conserva.
- blender-mcp: instalar cuando arranque el bloque B.

## Decisiones tomadas

- **Nombre**: El Estudio (provisional, renombrable). Agente principal: `director`.
- **Repo**: público, `MichaelH14/el-estudio` (personal, NO MEK). Licencia MIT.
- **Idioma**: español con términos técnicos en inglés.
- **Modelo del agente**: sin override — hereda el modelo de la sesión (debe funcionar igual con Opus).
- **Fase 1 se escribe con el mejor modelo disponible hoy**: el manual que le quede a Opus lo redacta Fable mientras exista.
