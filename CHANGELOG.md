# Changelog — El Estudio

Registro de versiones. El plugin se construyó fase por fase; cada fase se investigó, se auditó adversarialmente y se verificó (los operadores de Blender contra el binario real, los comandos de audio ejecutándolos).

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
