# Changelog — El Estudio

Registro de versiones. El plugin se construyó fase por fase; cada fase se investigó, se auditó adversarialmente y se verificó (los operadores de Blender contra el binario real, los comandos de audio ejecutándolos).

## v1.8.4 — 2026-08-05
Segunda tanda de fuentes traídas por Michael, verificadas antes de escribirlas:
- **`gamedev/casos-produccion.md`** (archivo nuevo, base gamedev de 15 a 16): destilado de *Blood, Sweat, and Pixels* (Jason Schreier, leído íntegro). Las diez producciones con cifras reales (burn rate de $10.000/persona/mes, presupuestos de Kickstarter, resultados), las cinco trampas recurrentes (fantasma del juego anterior, gravedad del equipo, stretch goals como deuda, cambio de motor a mitad, arte antes que gameplay), mecanismos copiables (peelable scope, el experimento de Kading que llevó el combate de 1,2 a 8,8 sobre 10, la escala 1-10 para desempatar codirección, la política de demos de Brennecke, el recorte como filtro de calidad), el caso del dev solo sin romantizar (Stardew Valley) y por qué las herramientas de desarrollo son el factor número uno.
- **`pipeline/ia-enemigos.md` §4b**: flow field pathfinding para hordas — invertir la búsqueda partiendo del objetivo, un solo cálculo para cientos de unidades, encarecer las celdas junto a los muros para curvas amplias y contar a los propios enemigos en el coste para que no se apilen.
- **`unity/ui-unity.md` §8b**: UI con feel — barra de vida por capas (trozo de daño retrasado, shake, flash, punch, números flotantes) y menú con overlay de foco interpolado.
- **`unity/csharp-patrones.md` §8b**: composición sobre duplicación con un único `Health` que notifica por eventos, a partir del bug real de los enemigos inmortales (`== 0` en vez de `<= 0` en una de las tres copias).
- **`pipeline/publicacion-tiendas.md`**: canal emergente Unity dentro de Fortnite (Unite Seoul 2026, acceso anticipado anunciado para 2027), marcado como anuncio y no como producto disponible.

## v1.8.3 — 2026-08-03
Conocimiento nuevo destilado de tres fuentes que trajo Michael, verificado contra fuentes primarias:
- **`gamedev/ia-percibida.md`** (archivo nuevo, base gamedev de 14 a 15): la ilusión de inteligencia como objetivo de diseño. Reglas de targeting exactas de los cuatro fantasmas de Pac-Man, F.E.A.R. contra el paper original de Orkin (es GOAP sobre una FSM de tres estados, no una FSM grande — corrige un mito muy repetido; el flanqueo y la pinza eran efectos colaterales, y los barks son la capa que hace visible la intención), Alien: Isolation (director que sabe / alien que busca, desbloqueo de ramas como ilusión de aprendizaje y la salvaguarda de no premiar la muerte del jugador), qué rompe la ilusión, y NPCs con LLM con sus límites reales. Enlazado desde `pipeline/ia-enemigos` y desde los agentes `director`, `disenador` e `ingeniero`.
- **`unity/audio-unity.md`**: eventos sonoros compuestos disparados por la simulación física — partir un suceso largo en fases (crack/fall/impact) con variantes, derivar volumen y variante de magnitudes físicas reales (`Collision.impulse`), y encadenar con `PlayScheduled` sin cortes. Resuelve el "peso falso" del clip largo que no reacciona.
- **`arte-2d/animacion-2d.md`**: dibujar con la animación reproduciéndose (live draw) para VFX de avance continuo (fuego, humo, viento) frente al onion skin, que sirve para animación pose a pose. Nativo en GameMaker Studio 2; en Aseprite 1.3+ vía la extensión Live Draw.

## v1.8.2 — 2026-08-03
Arreglado el scaffold día 0: el smoke test de plantilla rompía la compilación de un proyecto Unity 6 nuevo (`error CS0246: NUnit`) porque faltaban el `.asmdef` de tests y el paquete `com.unity.test-framework`. Ahora `templates/unity-day0` incluye `ElEstudio.Tests.EditMode.asmdef` y `scaffold_unity_day0.py` añade el paquete al `manifest.json` con la versión del editor instalado. Verificado en proyecto limpio (Unity 6000.3.18f1): 0 errores de compilación, `Day0SmokeTest` descubierto y pasando. Además, el smoke test de `examples/nightfall-protocol-mvp-review/` ahora es copia literal del que realmente corrió, con el comando y los logs de evidencia.

## v1.8.1 — 2026-07-27
Tooling de producción: compatibilidad Codex con `.codex-plugin/plugin.json` y `AGENTS.md`; conteos corregidos; skill `/validar-mercado`; validadores, doctor local, scaffold Unity día 0, CI, plantillas de memoria/provenance/analytics/mercado y caso de referencia Nightfall Protocol.

## v1.8.0 — 2026-07-21
Audio a fondo: `audio-produccion/` de 4 a 14 archivos (síntesis y diseño de sonido desde cero, foley, teoría musical, producción, música adaptativa, chiptune, dirección/mezcla, voz, middleware FMOD/Wwise, y hacer-audio-por-código). Stack de audio por código montado y verificado (SoX + FluidSynth + soundfont GM + mido + ffmpeg): el agente compuso música y sintetizó SFX reales, headless.

## v1.7.0 — 2026-07-21
Cierre de huecos: transparencia/alpha, terreno, criaturas no-bípedos, retarget de mocap en Blender, UX writing e i18n. Skill `/memoria-juego`. Auditoría final: 3.667 cross-refs, 0 rotas; 0 fugas de datos privados.

## v1.6.0 — 2026-07-20
Bloque D completo — especialización móvil (`movil/`, 9 archivos): diseño, mercado, monetización, retención/live-ops, rendimiento, gráficos, servicios, arte y release iOS+Android.

## v1.5.0 — 2026-07-20
Creación de audio (`audio-produccion/`, 4 archivos iniciales): crear SFX, crear/conseguir música, herramientas/recursos con licencias, preparar el audio para el juego.

## v1.4.0 — 2026-07-20
VFX y shaders (`vfx-shaders/`, 6 archivos): Shader Graph, recetas de shaders, partículas/VFX Graph, recetas de VFX, VFX 2D, optimización.

## v1.3.0 — 2026-07-20
Arte 2D (`arte-2d/`, 8 archivos): pixel art, sprites, animación 2D, tilesets, Aseprite, 2D→Unity, arte de UI. El `artista-3d` pasa a cubrir también 2D.

## v1.2.0 — 2026-07-20
Bloque C completo — equipo de agentes (fase 14): los 6 especialistas (disenador, ingeniero, artista-3d, animador, ux-ui, qa) además del director.

## v1.1.0 — 2026-07-20
Diseño UX/UI general (`ux-ui/`, 8 archivos): fundamentos UX, visuales, sistemas de diseño, patrones, móvil, accesibilidad, interacción, handoff.

## v1.0.0 — 2026-07-20
Bloque B completo — `pipeline-assets/` (4 archivos: pipeline idea→prefab, puente Blender↔Unity, aprender de assets, versionado). Skills `/asset-3d` y `/aprender-asset`. Fin del arte 3D.

## v0.6.0–v0.11.0 — 2026-07-19/20
Bloque B — arte 3D con Blender, fase por fase: modelado 3D, Blender, modelado en Blender, texturizado, rigging, animación 3D, animación en Blender. Operadores bpy verificados contra Blender 5.2 real en cada fase.

## v0.4.0–v0.5.0 — 2026-07-18/19
Bloque A completo — ensamblaje (director + 4 skills: /nuevo-juego, /receta-genero, /juice-pass, /ship-check) e instalación del plugin. Inicio del arte 3D (modelado).

## v0.1.0 — 2026-07-18
Esqueleto del plugin + Bloque A de conocimiento: game design (`gamedev/`, 14), Unity (`unity/`, 14), pipeline (`pipeline/`, 13).
