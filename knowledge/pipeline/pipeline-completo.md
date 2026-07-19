# Pipeline completo: de idea a build en Unity

> **Cuando cargar este archivo:** al arrancar un juego nuevo de cero, al decidir "qué toca hacer ahora" en cualquier punto del desarrollo, o al planificar etapas/hitos de un proyecto Unity completo. Es el mapa maestro que une la teoría de proceso (`gamedev/`) con la técnica de motor (`unity/`).

Este archivo NO repite la teoría: la comprime y la aterriza en Unity 6.x/URP. El QUÉ y POR QUÉ de cada fase está en [ver: gamedev/preproduccion] y [ver: gamedev/produccion-proceso]; el CÓMO técnico profundo de cada área está en `unity/`. Aquí vive la unión: qué existe EN el proyecto Unity al final de cada etapa, con checklist de salida y kill criteria.

## El mapa maestro

| # | Etapa | Artefacto de salida | Qué existe en Unity al salir |
|---|---|---|---|
| 0 | Idea → concepto | One-pager + criterio de kill escrito | **Nada. Unity cerrado.** |
| 1 | Día 0 | Proyecto configurado + build "hola mundo" corriendo en la plataforma real | Proyecto URP en git, Build Profiles, escenas base |
| 2 | Prototipo gris | Core loop divertido en gris (decisión kill/continue) | 1 escena `Prototype`, primitives, input del verbo, juice mínimo |
| 3 | First playable / MVP | El juego entero de punta a punta, feo pero completo | Flujo Boot→Menú→Juego→Resultado, save mínimo, build IL2CPP probado en device |
| 4 | Producción de contenido | Todo el macro design dentro (content complete) | Prefabs como unidad, data en ScriptableObjects, cadencia semanal de builds de playtest |
| 5 | Polish | Pases en orden: estabilidad→fricción→juice→consistencia→onboarding→performance | Profiler en device, atlas, stripping probado |
| 6 | Build + publicación | Build firmado subido a tienda + página de tienda viva (desde MUCHO antes) | Build Profiles Release por plataforma, CI o receta CLI |
| 7 | Post-launch | Parches con cadencia; capacidad de rebuild rápido | Editor en último patch LTS, pipeline de build reproducible |

Regla estructural: **cada etapa tiene criterio de salida escrito ANTES de empezarla** [ver: gamedev/produccion-proceso]. El nombre del hito importa menos que su gate.

## Etapa 0 — Idea → concepto (Unity cerrado)

Todo fuera del motor: core loop en 3-5 pasos, hooks, one-pager, criterio de kill, plataforma target primaria. El detalle completo (filtros de Clark, triple intersección de Yu, plantilla de one-pager) está en [ver: gamedev/preproduccion]; el género y sus expectativas en [ver: gamedev/generos] y su receta Unity en [ver: recetas-generos].

**Checklist de salida:** core loop describible sin mencionar historia · ≥1 hook comunicable en una frase · plataforma primaria decidida (define input y presupuesto de performance) · riesgo #1 identificado · criterio de kill del prototipo escrito con timebox (1-7 días).

**Kill aquí:** si no puedes describir qué hace el jugador cada 30 segundos, o si tras el filtro de hooks la idea no sobrevive — esperar una idea mejor es más barato que ejecutar una débil (el 99% falla el filtro). No se abre Unity para "explorar": abrir el motor sin loop escrito es la forma más cara de no tener idea.

## Etapa 1 — Día 0: el arranque perfecto en 30 pasos

Referencias de detalle: versión y paquetes [ver: unity/unity6-actualidad] · git/estructura/imports [ver: unity/assets-pipeline-git] · settings de build [ver: unity/build-plataformas] · organización fina del proyecto [ver: estructura-proyecto].

**Papel (antes de abrir Unity):**
1. One-pager terminado (etapa 0). Sin one-pager no hay proyecto.
2. Criterio de kill del prototipo escrito, con timebox de 1-7 días, guardado en el repo (`DESIGN.md`).
3. Plataforma target PRIMARIA decidida — todo el día 0 se configura contra ella.

**Motor y proyecto:**
4. Instalar **Unity 6.3 LTS, último patch** (`6000.3.Xf1`) vía Hub, con los módulos de la plataforma (Android SDK/NDK/OpenJDK, o soporte iOS). Nunca mainline para producción.
5. Crear proyecto con plantilla **Universal 2D** o **Universal 3D** (URP ya configurado por el template).
6. Nombre del proyecto = nombre corto y estable; anotar la versión exacta del editor (queda en `ProjectSettings/ProjectVersion.txt`).

**Git (antes de tocar nada más):**
7. `git init` + `.gitignore` de Unity + `.gitattributes` (LFS para binarios, `merge=unityyamlmerge` para .unity/.prefab/.asset) + `git lfs install`. En este orden: un binario commiteado sin LFS queda en la historia para siempre.
8. Verificar `Project Settings > Editor`: Asset Serialization **Force Text** y **Visible Meta Files** (defaults en Unity 6 — confirmar igual).
9. Commit 0: `Assets/` (con .meta), `Packages/manifest.json` + lock, `ProjectSettings/`. Jamás `Library/`.
10. `README.md`: versión del editor, cómo abrir, cómo buildear, convenciones (PPU, nombres).

**Identidad (inmutable después de publicar):**
11. Player Settings: Company Name + Product Name.
12. Bundle Identifier `com.estudio.juego` — no se puede cambiar una vez publicado.
13. Version `0.1.0`; Bundle Version Code / Build = 1.
14. Móvil: Default Orientation fija (Portrait o Landscape, no Auto si el juego no lo soporta).
15. Color Space **Linear** (default URP; verificar) y Active Input Handling = **Input System**.

**Paquetes y settings de trabajo:**
16. Verificar/instalar: Input System (project-wide Actions), Cinemachine 3.x (`Unity.Cinemachine`); 3D: **ProBuilder** (`com.unity.probuilder` 6.x) para greybox.
17. Crear el asset de Input Actions con el action map mínimo del verbo central (Move/Jump/Fire…) [ver: unity/input-system].
18. Si 2D: fijar el **PPU global** del proyecto (un solo valor, documentado en README).
19. Configurar **Preset por carpeta o AssetPostprocessor** para imports (sprites/audio/modelos) — una vez, y nunca más tocar import settings a mano.
20. Revisar el URP Asset del template contra la plataforma target (móvil: shadows, HDR, MSAA) [ver: unity/rendering-urp].

**Estructura:**
21. Carpetas: `_Game/` (Art, Audio, Code/Runtime, Code/Editor, Prefabs, Scenes, Data, UI) + `ThirdParty/` + `Settings/`.
22. Assembly Definitions propios para `Code/Runtime` y `Code/Editor` [ver: unity/arquitectura-unity].
23. Carpeta `Tests/` con asmdef de test + **1 test EditMode dummy que pasa** — valida el pipeline de tests el día 0, no el día que aparece el primer bug (Unity Test Framework es core desde 6.2) [ver: testing-qa].
24. Escenas: `Boot` (índice 0) + `Prototype`; crear un **scene template** (Unity 6.3: cualquier escena → template reutilizable) con Camera + Light + managers para que toda escena futura nazca consistente.

**Build desde el primer día:**
25. **Switch de plataforma a la target primaria HOY** — no la semana del release: el reimport es caro y los problemas de plataforma solo se ven ahí.
26. Crear Build Profiles `Dev` y `Release` (assets versionables, van a git) con la lista de escenas.
27. **Build "hola mundo" y correrlo EN el dispositivo/plataforma real.** Esto valida el toolchain completo (SDK, firma debug, driver gráfico) cuando arreglarlo cuesta una hora, no una semana.
28. Documentar el comando de build por CLI en el README (`-batchmode -activeBuildProfile ... -build ...`).
29. Si irá a tienda: crear la keystore Android ya + backup (archivo + contraseñas) fuera del repo; iOS: verificar cuenta del Developer Program.
30. Commit "día 0 completo" + tag `v0.1.0-day0`. A partir de aquí, prototipo.

**Kill criteria del día 0:** si el paso 27 (build en plataforma real) no sale en ≤1 día de trabajo, el proyecto tiene un riesgo técnico de plataforma mayor al presupuestado — resolverlo o cambiar de target ANTES de escribir gameplay.

## Etapa 2 — Prototipo gris del core loop

Teoría completa (toy first, fake it, juice mínimo, timebox EGP) en [ver: gamedev/preproduccion]. Aterrizaje en Unity:

| En Unity | Fuera de Unity |
|---|---|
| UNA escena `Prototype` — sin menús, sin flujo | Nada nuevo: el one-pager ya existe |
| Geometría: primitives (Cube/Plane/Capsule) con materiales de color plano; 3D con niveles: ProBuilder (build/edit de geometría en el editor, pensado para greyboxing) | Si el core es de decisiones/turnos: paper prototype ANTES de codear |
| Input: el action map del verbo central, nada más | Referencias de feel (clips de juegos que se sienten como quieres) |
| Juice mínimo: 1 SFX placeholder + 1 tween/flash por acción — sin esto no se puede evaluar el feel [ver: feel-en-unity] | |
| Física/character controller de la vía más simple que funcione [ver: unity/fisica-unity] | |

Qué **NO** se hace aquí: arquitectura fina, save, menús, atlas, Addressables, arte, optimización, asmdefs nuevos. "Nobody cares about your great engineering" — el código del prototipo es desechable por contrato.

**Checklist de salida:** el toy divierte al minuto 1 sin contexto · el loop con objetivo sostiene al minuto 10 · **al menos 1 tester externo fresco** lo jugó y pidió "una más" · decisión kill/continue tomada contra el criterio escrito en el día 0.

**Kill criteria:** "se pondrá divertido cuando agregue X" → kill o replantear · divertido min 1, aburrido min 10 tras 2-3 iteraciones → kill · solo el autor lo disfruta → playtest externo antes de decidir · el timebox (1-7 días por hipótesis) venció sin respuesta clara → es un proyecto disfrazado, kill. Matar en prototipo es victoria barata [ver: gamedev/preproduccion].

## Etapa 3 — First playable / MVP: el juego entero, feo

El gate de Cerny: si esta versión no emociona a jugadores frescos, se archiva. Para solo dev sin publisher, la ruta es **MVP del critical path + pasadas horizontales** (no vertical slice a calidad final) [ver: gamedev/preproduccion].

**En Unity:**
- Flujo de escenas completo: `Boot` (índice 0, servicios persistentes) → `MainMenu` → `Game` → `Results`. Wireframe de TODAS las pantallas antes de construirlas (título, HUD, pausa, settings, game over, victoria, confirmar salir, loading) [ver: ui-flujo-completo].

```csharp
// Boot.cs — escena índice 0: crea lo persistente y pasa al menú
using UnityEngine;
using UnityEngine.SceneManagement;

public class Boot : MonoBehaviour
{
    [SerializeField] string firstScene = "MainMenu";

    async void Start()
    {
        DontDestroyOnLoad(gameObject); // save, audio, settings viven aquí
        // await InitServicesAsync(); — lo que haga falta antes del menú
        var op = SceneManager.LoadSceneAsync(firstScene, LoadSceneMode.Single);
        while (!op.isDone) await Awaitable.NextFrameAsync(destroyCancellationToken);
    }
}
```

- Save mínimo que persiste una sesión (JSON a `Application.persistentDataPath` basta aquí) [ver: sistemas-meta].
- **Primer build IL2CPP en device real** si aún no se hizo: stripping, permisos y memoria solo se ven ahí [ver: unity/build-plataformas].
- Arte: placeholder marcado como tal. Un "beautiful corner" (área pequeña pulida) solo si necesitas validar la dirección visual [ver: arte-a-unity].

**Fuera de Unity:** el **macro design** — lista completa del contenido del juego (niveles, enemigos, items) con tamaños estimados y estado. Es el plan de producción. Y si el juego irá a Steam: **crear la página "Coming Soon" ya** — Valve recomienda subirla "as soon as you are ready to start talking publicly about your game" (mínimo 2 semanas antes del release); según Zukowski no existe "demasiado temprano" para exponer el juego (el riesgo real es que el juego sea aburrido, no la sobre-exposición).

**Checklist de salida:** jugable de inicio a fin sin huecos (placeholder sí, huecos no) · testers frescos terminan una run y quieren otra · macro design escrito · **scope congelado: de aquí en adelante solo se corta, no se añade**.

**Kill criteria:** el first playable no emociona a jugadores externos → se archiva la idea (regla Cerny — antes de quemar la producción, no después).

## Etapa 4 — Producción de contenido

Teoría (milestones, playtest método Valve, lista de corte, scope creep) en [ver: gamedev/produccion-proceso]. Aterrizaje:

| En Unity | Fuera de Unity |
|---|---|
| **Prefab como unidad de trabajo**: la escena solo contiene instancias; el contenido se edita en Prefab Mode (diffs limpios, merges posibles) | Playtest semanal con testers frescos (protocolo completo en la base gamedev) |
| Data de diseño en **ScriptableObjects** (`Data/`): enemigos, items, niveles como assets balanceables sin tocar código [ver: unity/csharp-patrones] | Lista de corte viva, ordenada por costo × poco aporte |
| Niveles: greybox con ProBuilder/Tilemap primero, arte después [ver: gamedev/level-design]; escenas nuevas desde el scene template | GDD vivo: solo se detalla lo decidido |
| Sprite Atlas por grupo de uso simultáneo; imports ya automatizados por preset (día 0, paso 19) | Assets externos (audio, arte) con su pipeline [ver: arte-a-unity] |
| Contenido dinámico por Addressables, cero `Resources.Load` | Página de tienda acumulando wishlists |
| Fix no trivial → test de regresión en `Tests/` [ver: testing-qa] | |

**La cadencia semanal es el corazón de la etapa** — build de playtest cada viernes, triage el lunes [ver: gamedev/produccion-proceso] y [ver: produccion-solo-dev]. En Unity eso es un comando, no un ritual manual:

```bash
# Viernes: build Dev + subida al canal de playtest de itch (butler)
Unity -batchmode -quit -projectPath . \
  -activeBuildProfile "Assets/Settings/BuildProfiles/Win-Dev.asset" \
  -build "Builds/Win/Juego.exe" -logFile build.log
butler push Builds/Win usuario/mi-juego:win-playtest --userversion 0.4.2
```

butler (CLI oficial de itch.io) sube por canales con parches incrementales — ideal para el loop semanal. Móvil: TestFlight interno (iOS, hasta 100 testers sin review) [ver: unity/build-plataformas].

**Checklist de salida (content complete):** todo el macro design está dentro · cero placeholders · jugable de inicio a fin con el contenido real · la lista de corte se ejecutó sin renegociar la visión.

**Kill/pivot criteria:** alpha movida más de una vez sin cortar nada a cambio → scope creep activo, cortar ya · N features al 80% y ninguna cerrada → cerrar antes de abrir · playtests semanales sin mejora de señal en 4+ semanas → volver al diseño del loop, el contenido no arregla un core débil.

## Etapa 5 — Polish

El orden canónico de pases y su porqué están en [ver: gamedev/produccion-proceso]: **estabilidad → fricción → juice → consistencia → onboarding → performance**. Lo específico de Unity por pase:

| Pase | En Unity concretamente |
|---|---|
| Estabilidad | Crashes y saves corruptos en **build IL2CPP en device**, no en Editor; consola limpia de errores/warnings propios |
| Fricción | Tiempos de carga (escenas aditivas/async), input deadzones, confirmaciones de más [ver: unity/input-system] |
| Juice | Tweens, partículas, hit-stop, screenshake [ver: feel-en-unity] |
| Consistencia | Texto/i18n [ver: narrativa-localizacion], volúmenes en AudioMixer, transiciones, estados vacíos |
| Onboarding | Lo último — con testers 100% frescos [ver: gamedev/ux-ui-onboarding] |
| Performance | Profiler EN device, presupuesto de frame, GC a cero en hot paths, atlas/draw calls, memoria [ver: unity/rendimiento-unity] |

**Checklist de salida:** cero bugs bloqueantes conocidos · frame time estable en el hardware mínimo · onboarding pasado por ≥5 testers frescos sin intervención · build report auditado (texturas, `Resources/`) [ver: unity/build-plataformas].

## Etapa 6 — Build y publicación

El checklist técnico por plataforma (firma, stores, stripping, WebGL, Steam Deck, CI) está completo en [ver: unity/build-plataformas] — no se repite aquí. Lo que este mapa añade: **la publicación no es una etapa final, empieza en el first playable**.

| Momento | Acción de tienda |
|---|---|
| First playable | Página Steam "Coming Soon" arriba (Valve: "as soon as you are ready to start talking publicly about your game"; los wishlists reciben notificación automática al lanzar y con descuentos ≥20% de 8+ horas) |
| Producción | Screenshots/GIF reales en cada milestone; devlog si hay energía |
| Pre-launch | Demo si el juego lo aguanta: la mayoría de quienes la juegan NO la wishlistean y eso está bien — sigue siendo la herramienta de marketing más potente (Zukowski, jun-2026). Next Fest una sola vez, con la demo ya probada |
| Launch | No planificar alrededor de "Popular Upcoming": Valve subió el umbral efectivo de ~7.000 a ~100.000 wishlists (cambio reportado jun-2026); la visibilidad indie ahora pasa por el Personal Calendar y las notificaciones a wishlist |
| Post-launch | Parches con cadencia; editor SIEMPRE en el último patch de la LTS para poder rebuildear ante un CVE (lección 2025) [ver: unity/unity6-actualidad] |

**Checklist de salida:** build Release (IL2CPP, Development Build OFF) probado en la plataforma real · versión/build number incrementados · página de tienda completa · plan post-launch presupuestado ANTES del launch [ver: gamedev/produccion-proceso].

## Tiempos relativos y presupuesto de riesgo (dev solo + agente IA)

Calibre de scope total: Zukowski ("The Missing Middle") recomienda para indies juegos de **1-9 meses** de desarrollo con expectativa de $10-40k — la mediana real de Steam es ~$4.000 por juego (~$17.000 filtrando juegos de <$10, datos Gamalytic). Ejemplos reales: Luck be a Landlord, 2 meses de concepto a demo; Islanders, 7 meses. El primer juego no es el dream game.

Presupuesto relativo por etapa — **heurística de síntesis** (de las fuentes de [ver: gamedev/preproduccion] y [ver: gamedev/produccion-proceso], no cifras de un estudio; calibrar por proyecto):

| Etapa | % del calendario | Riesgo que ataca | Con agente IA se comprime… |
|---|---|---|---|
| Concepto | 2-5% | Mercado/diseño: ¿merece existir? | Poco — es decisión humana |
| Día 0 | ~1% (1 día) | Técnico de plataforma | Mucho (es mecánico) |
| Prototipo | 10-15% | **Diseño: ¿divierte?** — el riesgo #1 casi siempre | El código sí; el juicio de diversión NO (necesita humanos jugando) |
| First playable | 15-20% | Estructura: ¿el juego entero funciona? | Bastante (flujo, save, menús son código estándar) |
| Producción | 30-40% | Contenido/arte: ¿puedo producirlo a este nivel? | Sistemas sí; el arte y el balance requieren iteración humana |
| Polish | 20-25% | Calidad percibida — "el último 10% es el 90%" | Parcialmente: bugs/perf sí, feel y onboarding necesitan testers |
| Build/release | 5-10% | Certificación/tienda | Poco — los reviews de Apple/Google/Valve van a su ritmo |

Regla de riesgo: un proyecto de una persona soporta **UN riesgo grande**; la etapa temprana correspondiente lo ataca primero con el artefacto más barato (prototipo para diseño, build día-0 para técnica, beautiful corner para arte) [ver: gamedev/preproduccion]. Con agente IA el cuello de botella del calendario deja de ser "escribir código" y pasa a ser **decisiones + playtests con humanos frescos + esperas externas** — planificar el calendario alrededor de la cadencia de playtest, no de la velocidad de implementación.

## Kill criteria — resumen transversal

| Etapa | Señal de kill/pivot | Acción |
|---|---|---|
| Concepto | Sin loop describible o sin hooks | No abrir Unity; esperar idea mejor |
| Día 0 | Build en plataforma real no sale en ≤1 día | Resolver toolchain o cambiar target antes de escribir gameplay |
| Prototipo | Toy no divierte en gris tras 2-3 iteraciones honestas | Kill — celebrarlo: fue barato |
| First playable | No emociona a testers frescos | Archivar (Cerny) — el contenido no lo salvará |
| Producción | 4+ semanas de playtests sin mejora; scope solo crece | Cortar desde la lista de corte; si el core es el problema, volver a prototipo |
| Pre-release | Demo/página con señal muy débil | No suele ser kill: ajustar expectativas, precio y fecha; lanzar igual — terminar es una skill que se entrena |
| Siempre | "Mejor lo reescribo/reinicio de cero" | Prohibido: refactor local, nunca restart [ver: gamedev/produccion-proceso] |

## Reglas prácticas

- [ ] Unity no se abre hasta tener one-pager + criterio de kill escritos.
- [ ] Día 0 completo en un día: Unity 6.3 LTS + plantilla Universal (URP) + git/LFS ANTES de los primeros assets + identidad de Player Settings.
- [ ] Switch a la plataforma target y build "hola mundo" en el dispositivo real el día 0-1 — el toolchain se valida cuando es barato.
- [ ] Test dummy que pasa el día 0: el pipeline de tests existe antes del primer bug.
- [ ] Un prototipo = una hipótesis = una escena = 1-7 días. Código desechable por contrato.
- [ ] Nada de arte, menús, save ni arquitectura en el prototipo; sí juice mínimo (1 SFX + 1 tween) para poder evaluar feel.
- [ ] Decisión kill/continue contra el criterio ESCRITO, con al menos 1 tester externo fresco.
- [ ] First playable = flujo completo Boot→Menú→Juego→Resultado sin huecos + save mínimo + build IL2CPP en device.
- [ ] Al cerrar first playable: macro design escrito y scope congelado — solo se corta.
- [ ] Página Steam "Coming Soon" arriba desde el first playable; "demasiado temprano" no existe.
- [ ] Producción = prefab como unidad + data en ScriptableObjects + escenas desde scene template + imports por preset.
- [ ] Cadencia semanal automatizada: build por CLI (`-activeBuildProfile`) + `butler push` (o TestFlight) cada viernes; triage lunes.
- [ ] Fix no trivial durante producción → test de regresión en el mismo commit.
- [ ] Polish en orden (estabilidad→fricción→juice→consistencia→onboarding→performance); onboarding lo último, con testers frescos.
- [ ] Todo pase de estabilidad/performance se mide en build de device, jamás solo en Editor.
- [ ] Scope total tipo "missing middle": 1-9 meses; el calendario se planifica alrededor de los playtests, no de la velocidad del agente.
- [ ] Release: Development Build OFF, versión incrementada, build report auditado, plan post-launch presupuestado antes del launch.
- [ ] Editor siempre en el último patch de la LTS mientras el juego esté vivo (capacidad de rebuild ante CVE).

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Abrir Unity "para explorar la idea" sin one-pager | El motor no es una herramienta de ideación: papel primero, el loop se escribe en 5 líneas |
| Montar el proyecto a medias (sin git/LFS, sin bundle ID, plataforma default) y pagar después | Los 30 pasos del día 0 en orden; los binarios sin LFS y el bundle ID mal quedan para siempre |
| Primer build a device la semana del lanzamiento | Build hola-mundo día 0-1 y build IL2CPP en first playable; stripping/permisos/memoria solo existen ahí |
| Prototipo con arquitectura "para reusar después" | El prototipo se tira; asmdefs, managers y patrones llegan en first playable |
| Prototipo sin ningún juice → "no divierte" falso negativo | 1 SFX + 1 tween mínimos antes de juzgar el feel |
| Saltarse el gate de first playable y entrar a producción "porque ya hay momentum" | Es el gate de Cerny: sin emoción de testers frescos, producción = quemar meses en un muerto |
| Pulir contenido a nivel final antes del content complete | Pasadas horizontales: todo el juego sube junto; lo pulido temprano suele cortarse |
| Escena monolítica que crece toda la producción | Prefab como unidad + subescenas aditivas; los merges y el trabajo paralelo dependen de esto |
| Balancear hardcodeado en scripts | ScriptableObjects como data de diseño: balance sin recompilar y diffs legibles |
| "El marketing se hace al final" | La página de tienda acumula wishlists durante TODA la producción; al final ya es tarde |
| Planificar el launch contando con Popular Upcoming | Umbral efectivo ~100k wishlists (2026): visibilidad = wishlists propios + Personal Calendar + demo |
| Medir el éxito de la demo por wishlists directos de quien la juega | La mayoría no wishlistea la demo y aun así es la mejor herramienta de marketing (señal indirecta) |
| Calendario que asume que el agente IA acelera TODO por igual | El agente comprime código; playtests, arte, balance y reviews de tienda van a ritmo humano/externo |
| Shippear y congelar el editor para siempre | Último patch LTS + build reproducible: hay que poder re-publicar rápido (caso CVE-2025-59489) |

## Fuentes

**Web (consultadas en esta investigación):**
- ProBuilder 6.0.9 — docs oficiales del paquete (docs.unity3d.com/Packages/com.unity.probuilder@6.0) — herramienta oficial de greybox: "build, edit, and texture custom geometry", level design y prototipado, export a DCC.
- Scene templates — Unity Manual 6000.3 (docs.unity3d.com) — plantillas de escena reutilizables (assets clonados vs referenciados) para el día 0 y las escenas de producción.
- Unity Test Framework 2.0 — docs oficiales del paquete — EditMode/PlayMode, test assemblies vía asmdef, NUnit adaptado; base del paso 23 del día 0.
- Templates — Unity Hub docs (docs.unity.com/en-us/hub) — un template es "a packaged version of a project" como punto de partida; el detalle por template se ve en el propio Hub (la página oficial no lista nombres — los nombres Universal 2D/3D vienen de la base unity/).
- butler — itch.io docs (itch.io/docs/butler) — CLI oficial: `butler push carpeta usuario/juego:canal`, parches incrementales, `--userversion`; el mecanismo del build semanal de playtest.
- Wishlists — Steamworks Documentation (partner.steamgames.com) — Coming Soon: "as soon as you are ready to start talking publicly about your game" (mínimo 2 semanas antes del release); notificaciones automáticas al launch; descuentos ≥20% disparan email de notificación a wishlisters (duración mínima de horas no confirmada en esta auditoría, verificar en `doc/marketing/discounts` antes de planificar el launch).
- The Missing Middle in Game Development — Chris Zukowski, howtomarketagame.com (2023) — juegos de 1-9 meses / $10-40k; mediana Steam ~$4k (~$17k en juegos >$10, datos Gamalytic); casos Luck be a Landlord e Islanders.
- You cannot over-expose your game — Chris Zukowski, howtomarketagame.com (jul-2026) — no existe "página demasiado temprano"; el riesgo real es un juego aburrido.
- How the Steam Personal Calendar affects your launch — Chris Zukowski, howtomarketagame.com (jun-2026) — Popular Upcoming pasó de ~7.000 a ~100.000 wishlists; Personal Calendar como vía de visibilidad nueva.

**Base sintetizada (esta base de conocimiento):**
- [ver: gamedev/preproduccion] — filtros de idea, one-pager, prototipo EGP, first playable vs MVP, scoping y kill criteria: toda la teoría de las etapas 0-3.
- [ver: gamedev/produccion-proceso] — milestones con gates, método Valve de playtest, lista de corte, orden del polish, sostenibilidad: la teoría de las etapas 4-5.
- [ver: unity/unity6-actualidad] — Unity 6.3 LTS, plantillas Universal, paquetes esenciales con versiones, licencias.
- [ver: unity/assets-pipeline-git] — git/LFS/.meta, estructura de carpetas, presets de import, Addressables: los pasos 7-9, 18-21 del día 0.
- [ver: unity/build-plataformas] — Build Profiles, firma, stripping, CLI/CI, checklist por plataforma: las etapas 1, 3 y 6 en su detalle técnico.
