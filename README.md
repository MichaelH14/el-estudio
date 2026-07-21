# El Estudio 🎮

Plugin de Claude Code que convierte a un agente de IA en un **estudio de videojuegos completo** — diseño, programación en Unity, arte 3D y 2D, animación, audio y publicación — desde la idea hasta la tienda.

**Estado:** ✅ Completo · **v1.8.0** · 159 archivos de conocimiento (45.600 líneas) en 16 bases · 7 agentes · 7 skills.

---

## La idea

Los modelos de IA cambian; el conocimiento escrito se queda.

El Estudio destila en archivos markdown todo lo que un agente necesita para hacer videojuegos — game design, arte, animación, audio, Unity, y el pipeline completo de idea a juego terminado — para que **cualquier modelo** pueda operar como un estudio de videojuegos, sin depender de lo que el modelo "ya sepa".

**La inteligencia vive en los archivos, no en el modelo.** Cada archivo es un manual operativo denso, destilado de fuentes reales (libros canon, charlas GDC, postmortems, docs oficiales), escrito para que lo lea un agente mientras trabaja en un juego real: reglas prácticas, checklists, pitfalls con su antídoto, y fuentes citadas. Nada inventado — lo que no se pudo verificar se marca, no se adorna.

## Qué sabe hacer

El plugin cubre el ciclo completo de producción de un videojuego, organizado en 16 bases de conocimiento:

### Diseño y producción
| Base | Archivos | Qué cubre |
|---|---:|---|
| `gamedev/` | 14 | Game design: mecánicas, core loops, géneros, level design, game feel, arte, narrativa, historia del medio, UX, psicología y negocio |
| `pipeline/` | 13 | La unión juego↔Unity: de idea a juego terminado, recetas por género, IA de enemigos, netcode, save/economía, testing, y **publicación en tiendas** |

### El motor
| Base | Archivos | Qué cubre |
|---|---:|---|
| `unity/` | 14 | Unity 6 a fondo: arquitectura, C#, física, Input System, UI, rendering/URP, audio, rendimiento, builds, gotchas, y cómo operar Unity vía MCP |

### Arte 3D (con Blender)
| Base | Archivos | Qué cubre |
|---|---:|---|
| `modelado/` | 11 | Teoría de modelado 3D: topología, hard-surface, personajes, blueprints, props/armas/vehículos/entornos |
| `blender/` | 12 | Blender 5.2 a fondo: interfaz, modificadores, geometry nodes, sculpt, addons, API Python, y operar Blender vía MCP |
| `pipeline-3d/` | 9 | Recetas de modelar EN Blender, paso a paso, por categoría de asset |
| `texturizado/` | 9 | UV unwrapping, PBR, baking, painting, Substance, atlas, export a URP |
| `rigging/` | 8 | Esqueletos, skinning/weights, deformación, IK/FK, Rigify, rigs mecánicos, export a Unity |
| `animacion3d/` | 9 | Ciclos, combate, curvas, mocap, animación facial, capas, movimiento secundario, criaturas |
| `animacion-blender/` | 8 | Animar EN Blender: timeline, graph editor, actions, NLA, hornear, export de clips, retarget de mocap |
| `pipeline-assets/` | 4 | La unión: pipeline completo idea→prefab, puente técnico Blender↔Unity, aprender de assets, versionado |

### Arte 2D, VFX y audio
| Base | Archivos | Qué cubre |
|---|---:|---|
| `arte-2d/` | 8 | Pixel art, sprites, animación 2D, tilesets, Aseprite, 2D→Unity, arte de UI |
| `vfx-shaders/` | 6 | Shader Graph, recetas de shaders, partículas/VFX Graph, recetas de VFX, VFX 2D, optimización |
| `audio-produccion/` | 14 | Síntesis y diseño de sonido desde cero, foley, teoría musical, producción, música adaptativa, chiptune, dirección/mezcla, voz, middleware, y **hacer audio por código** |

### Transversal
| Base | Archivos | Qué cubre |
|---|---:|---|
| `ux-ui/` | 10 | Diseño UX/UI de producto: fundamentos, sistemas de diseño, patrones, móvil, accesibilidad, microinteracciones, UX writing, i18n |
| `movil/` | 9 | Especialización móvil: diseño, mercado, monetización, retención/live-ops, rendimiento, gráficos, servicios, arte y release iOS+Android |

Más `recursos-libres.md` (recursos externos verificados) y un `INDEX.md` por base que enruta la carga.

## El equipo de agentes

El plugin es un estudio con roles. El `director` orquesta y enruta; los especialistas ejecutan cargando **solo su parte** del conocimiento; el `qa` verifica con evidencia y no se auto-aprueba.

| Agente | Rol |
|---|---|
| `director` | Orquesta, decide scope, escribe el GDD, enruta al equipo |
| `disenador` | Mecánicas, core loop, balance, niveles, economía |
| `ingeniero` | Implementa en Unity/C#, feel, sistemas; opera Unity vía MCP |
| `artista-3d` | Modela y texturiza (3D y 2D); opera Blender vía MCP |
| `animador` | Rig y animación; export de clips a Unity |
| `ux-ui` | HUD, menús, onboarding, interfaces |
| `qa` | Audita todo entregable con evidencia; obligatorio, no se salta |

## Skills (slash commands)

| Skill | Qué hace |
|---|---|
| `/nuevo-juego` | Idea cruda → GDD → proyecto Unity día 0 → prototipo del loop |
| `/receta-genero` | Monta la base técnica de un género conocido |
| `/juice-pass` | El juego funciona pero se siente muerto — pase de game feel |
| `/ship-check` | Guantelete completo antes de publicar |
| `/asset-3d` | Producir un asset 3D de referencia a prefab game-ready |
| `/aprender-asset` | Analizar un asset de Unity y extraer sus convenciones |
| `/memoria-juego` | Mantener el GDD + CHECKPOINT de un juego para retomarlo en cualquier sesión |

## Capacidades verificadas contra herramientas reales

El plugin no solo sabe, también **hace**, y su conocimiento está verificado ejecutándolo:

- **Blender** (vía MCP + headless): los operadores `bpy` de las bases 3D están verificados contra Blender 5.2 real, no supuestos — incluidos round-trips de export FBX.
- **Audio por código** (headless, gratis): con `SoX` (SFX sintéticos), `FluidSynth` + soundfont GM (música MIDI→audio), `mido` (escribir MIDI) y `ffmpeg`, el agente fabrica el audio de un juego sin GUI. Verificado generando música y SFX reales.
- **Unity** (vía MCP): opera el editor con el flujo editar→compilar→verificar.

## Instalación

```
/plugin marketplace add MichaelH14/el-estudio
/plugin install el-estudio@michael-games
```

Los plugins cargan al arrancar la sesión.

## Uso

En una sesión con el plugin cargado, pídele al equipo lo que quieras construir:

```
"Quiero hacer un juego de plataformas 2D. Usa /nuevo-juego."
"Modélame un cofre game-ready para Unity."   → /asset-3d
"El combate funciona pero se siente flojo."   → /juice-pass
"Vamos a publicar en Play Store."             → /ship-check
```

El `director` carga el conocimiento relevante, delega en los especialistas y pasa todo por el `qa` antes de darlo por terminado.

## Cómo se construyó

Cada base se produjo con un proceso multi-agente adversarial:

1. **Investigar** — un agente por tema busca fuentes reales (libros canon, GDC, postmortems, docs oficiales) y destila el archivo.
2. **Criticar** — un crítico adversarial audita, verifica las afirmaciones dudosas contra la fuente (y contra los binarios reales de Blender/SoX cuando aplica), y repara.
3. **Coherencia** — un editor arma el índice, detecta solapes y refs colgantes.

Regla de hierro: **nada inventado**. Lo verificado se cita; lo no verificado se marca "NO VERIFICADO"; lo que resultó falso se corrige. La auditoría final: 3.667+ cross-references sin ninguna rota, cero datos privados en un repo público.

## Estructura del repo

```
.claude-plugin/     plugin.json + marketplace.json
agents/             los 7 agentes del estudio
skills/             las 7 skills (cada una en su carpeta con SKILL.md)
knowledge/          las 16 bases de conocimiento + recursos-libres.md
                    cada base tiene su INDEX.md que enruta la carga
PLAN.md             el plan de construcción (histórico) y huecos/ideas futuras
```

## Mejora continua

El plugin es un proyecto vivo. Cada juego real que se haga con él retroalimenta el conocimiento: pitfalls nuevos, recetas probadas, y los huecos que un agente reporte se convierten en investigación. Los huecos e ideas pendientes están en `PLAN.md`.

## Licencia

MIT
