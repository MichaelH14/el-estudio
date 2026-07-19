# Producción solo-dev con agente IA

> **Cuando cargar este archivo:** siempre que UN humano + UN agente IA estén desarrollando un juego Unity de punta a punta — para repartir el trabajo, estructurar cada sesión, mantener los documentos vivos (GDD/CHECKPOINT/lista de corte), controlar el scope y decidir cuándo parar. Es el manual de OPERACIÓN del dúo; el mapa de etapas está en [ver: pipeline-completo].

Este archivo asume: la teoría de proceso (milestones, playtest, scope, sostenibilidad) está en [ver: gamedev/produccion-proceso] y [ver: gamedev/preproduccion]; la operación técnica del editor está en [ver: unity/unity-mcp-flujo]. Aquí vive lo que ninguno cubre: **cómo el dúo humano+agente convierte esas dos bases en un ritmo de trabajo que shippea**.

## 1. División del trabajo: quién hace qué

Principio rector: el agente comprime la ESCRITURA (código, data, tooling, builds); no comprime el JUICIO (diversión, estética, scope) ni las esperas externas (playtests, reviews de tienda) [ver: pipeline-completo]. Dato de calibración duro — estudio METR (RCT, early-2025, 16 devs experimentados, 246 tareas reales): los devs esperaban ir 24% más rápido con IA, fueron **19% más lentos**, y al terminar aún CREÍAN haber ido 20% más rápido. Moral: la sensación de velocidad no es evidencia; los hitos shippeados sí (§6).

| Tarea | Quién | Regla operativa |
|---|---|---|
| Concepto, hooks, kill/continue | **Humano decide** | El agente prepara opciones y datos; jamás decide si algo "es divertido" — no puede sentirlo [ver: unity/unity-mcp-flujo §6] |
| ¿Es divertido? ¿Se siente bien? | **Humano jugando** (+ testers frescos) | El agente verifica que FUNCIONA; solo un humano verifica que GUSTA. Playtest con frescos: método Valve [ver: gamedev/produccion-proceso] |
| Scope: qué entra, qué se corta | **Humano decide, agente administra** | El agente mantiene la lista de corte y PROPONE cortes con costo estimado; el humano firma |
| Dirección de arte, estética | **Humano decide sobre opciones** | El agente genera variantes/aplica el style guide; el veredicto visual es humano [ver: arte-a-unity] |
| Código de sistemas, UI, tooling | **Agente ejecuta** | Con ciclo sagrado + verificación propia por cambio [ver: unity/unity-mcp-flujo §4-5] |
| Tests, builds, CI, automatización | **Agente ejecuta** | Es lo más delegable: mecánico y verificable por máquina [ver: testing-qa] |
| Contenido desde data (niveles, enemigos, balance inicial) | **Agente genera, humano prueba jugando** | Los números iniciales son hipótesis; el balance real sale de jugar y de telemetría |
| Refactors, deuda, consolidación | **Agente ejecuta, humano prioriza** | Sesiones de consolidación periódicas (§5, error 7) |
| Cuentas, compras, tiendas, legal, keystores | **Humano** | Credenciales e identidad de publicación no se delegan |
| Documentos vivos (CHECKPOINT, GDD) | **Agente escribe, ambos leen** | Se actualizan en la MISMA sesión del cambio (§3) |

Herramientas del agente en Unity: la vía principal es MCP (mcp-for-unity, opera el editor real con verificación) [ver: unity/unity-mcp-flujo]. Existe además **Assistant** oficial de Unity (paquete `com.unity.ai.assistant`, requiere Unity 6.2+/6000.2, cuenta Unity y sistema de puntos; modos `/ask`, `/run`, `/code` dentro del editor) — útil como consulta puntual del humano, pero no sustituye al agente con MCP: no mantiene contexto de proyecto ni cadencia.

## 2. La sesión de trabajo: objetivo único

La restricción física del agente: **el contexto se llena y el rendimiento degrada al llenarse** (documentado por Anthropic para Claude Code). La sesión eterna multipropósito es al agente lo que el crunch al humano: produce cada vez peor. De ahí la unidad de trabajo:

**1 sesión = 1 objetivo escrito = 1 definition of done = evidencia antes de cerrar.**

### Protocolo de sesión

```text
ABRIR
 1. Leer CHECKPOINT.md + DESIGN.md (§3). Nunca asumir el estado: leerlo.
 2. Verificar línea base VERDE: compila sin errores + tests pasan
    (read_console / run_tests) ANTES de tocar nada. Si está rota,
    arreglarla ES el objetivo de la sesión.
 3. Escribir el objetivo único y su DoD (tabla abajo). Si no cabe en
    una frase, es más de una sesión: partirlo.
TRABAJAR
 4. Cambios chicos con ciclo sagrado entre medio [ver: unity/unity-mcp-flujo §4].
 5. Tras 2 intentos fallidos del mismo fix: parar de adivinar,
    instrumentar (Debug.Log, test que reproduce). Tras 2 correcciones
    del humano sobre lo mismo: reset de contexto con un prompt mejor —
    el contexto está envenenado de intentos fallidos.
CERRAR
 6. Verificar el DoD con EVIDENCIA (output de test, consola, build).
 7. Actualizar CHECKPOINT.md: hecho / siguiente / decisiones.
 8. Commit descriptivo. El proyecto queda VERDE — jamás cerrar sesión
    con el proyecto roto: la sesión siguiente arranca ciega.
```

### Definition of done por tipo de tarea

Scrum Guide: el DoD es "la descripción formal del estado del Increment cuando cumple las medidas de calidad requeridas"; lo que no lo cumple **no se presenta como hecho** — vuelve al backlog. Traducido a Unity solo-dev:

| Tarea | DONE significa (todo, no algo) |
|---|---|
| Mecánica nueva | Compila limpio · test PlayMode del comportamiento clave · verificada en play mode con `Debug.Log` de instrumentación leído · **alcanzable jugando** desde el flujo real del juego · CHECKPOINT actualizado |
| Contenido (nivel, enemigo, item) | Data en ScriptableObject, no hardcodeada [ver: unity/csharp-patrones] · aparece jugando una partida normal · consola limpia al usarlo |
| Pantalla de UI | Accesible desde el flujo de pantallas (no solo en su escena aislada) · navegable con los inputs del juego · verificada en ≥2 resoluciones [ver: ui-flujo-completo] |
| Bug fix | Causa raíz identificada (no síntoma tapado) · test de regresión en el mismo commit · el síntoma original re-verificado muerto |
| Build | Generado por CLI/Build Profile · **corre en la plataforma real**, no solo en Editor [ver: unity/build-plataformas] |
| Balance/tuning | Valores en SO · el humano jugó la build con los valores nuevos (el agente no siente dificultad) |

Regla de evidencia (Anthropic, best practices de agentes): dale al agente **un check que pueda correr** — test, exit code de build, consola — y muestra la evidencia en vez de afirmar éxito. "Looks done" no es señal; el output del check sí. En Unity el check siempre existe: `run_tests` + `read_console` + play mode instrumentado [ver: unity/unity-mcp-flujo §5].

## 3. Documentos vivos mínimos

Fundamento: la memoria del agente entre sesiones NO existe salvo lo que escriba a disco. Anthropic lo formaliza como *structured note-taking / agentic memory*: "el agente escribe regularmente notas persistidas fuera de la ventana de contexto" y las relee tras cada reset — es lo que permite coherencia en tareas de horas/semanas. Para un juego bastan TRES archivos en la raíz del repo, commiteados:

### DESIGN.md — el GDD de 1 página

Formato y teoría completos en [ver: gamedev/preproduccion] (one-pager de Librande + secciones del GDD moderno). Regla: solo se detalla lo DECIDIDO; cambia el mismo día que cambia el diseño; si dejó de cambiar, dejó de servir. Esqueleto:

```markdown
# DESIGN — <Juego>
LOGLINE: <1 frase: verbo + fantasía + giro>
CORE LOOP: 1. ... → 2. ... → 3. ... → (vuelve a 1 con más ...)
HOOKS (máx 3): ...
PRINCIPIOS (3-5, resuelven disputas futuras): "ante la duda, X gana a Y"
## Macro design (contenido completo, con estado)
| Elemento | Tamaño est. | Estado: idea/decidido/hecho/cortado |
## Lista de corte (orden = costo × poco aporte al core; se corta desde arriba)
1. ...
## v2 / siguiente juego (las ideas que NO entran)
## Kill criteria vigentes (etapa actual + post-launch cuando toque)
```

### CHECKPOINT.md — el estado para retomar sin perder contexto

```markdown
# CHECKPOINT — <Juego> · <fecha> · Etapa: <prototipo|MVP|producción|polish>
## Estado del proyecto
Verde/Roto · commit: <hash> · compila: sí · tests: 14/14 · última build device: <fecha>
## Hecho (últimas sesiones, lo relevante)
- Dash con i-frames funcionando, test PlayMode DashInvulnerability
## Siguiente (máx 3, en orden — lo primero es lo que abre la próxima sesión)
1. Conectar dash al tutorial (hoy es huérfano: solo accesible en escena Test)
## Decisiones tomadas (NO reabrir sin causa nueva)
- 2026-07-12: input buffering 0.1s en salto — testers fallaban el timing
- 2026-07-15: se corta el modo endless (lista de corte #1 ejecutada)
## Bloqueos / dudas para el humano
- ¿El boss 2 mantiene la 2ª fase? Estimo 3 sesiones; aporta poco al core
## Comandos
build: Unity -batchmode -activeBuildProfile ... · tests: run_tests PlayMode
```

Reglas: se actualiza al CERRAR cada sesión (paso 7 del protocolo), no "cuando haya tiempo" · máx 1-2 páginas — se poda: lo viejo se borra o se comprime en "Decisiones" · las decisiones registradas evitan el ciclo mortal del solo-dev con agente: re-discutir en cada sesión lo ya decidido · la sección "Bloqueos" es el buzón inverso: preguntas del agente al humano, batcheadas, no goteo.

### CLAUDE.md (o equivalente) — las reglas permanentes del proyecto

Lo que el agente debe saber en TODA sesión y no puede inferir del código: versión exacta del editor, comandos de build/test, convenciones (PPU, nombres, carpetas [ver: estructura-proyecto]), gotchas del proyecto. Regla de Anthropic: corto y podado — "por cada línea: ¿quitarla causaría errores? Si no, fuera"; un archivo inflado hace que el agente ignore las reglas importantes. El detalle que solo aplica a veces va en DESIGN/CHECKPOINT o en la base de conocimiento, no aquí.

## 4. Gestión de scope continua: la lista de corte

La teoría (trade X⇒Y, feature freeze, señales de scope creep, 71% de postmortems con problemas de scope) está en [ver: gamedev/produccion-proceso]. Lo operativo del dúo:

- La lista vive en DESIGN.md **desde el día 1**, ordenada por (costo de terminar × poco aporte al core). Cuando el calendario apriete, se corta desde arriba **sin renegociar la visión**.
- **El agente es el guardián mecánico del scope**: al recibir una petición de feature nueva, su primera respuesta incluye el costo real estimado (feature × UI × testing × balance × bugs) y la pregunta "¿qué sale a cambio?". El humano decide; el agente registra la decisión en CHECKPOINT.
- Peligro específico del agente: **el costo de AÑADIR se desplomó, el costo de MANTENER no.** Cada feature generada en minutos sigue costando testing, balance, UI, onboarding y bugs a precio completo. El scope creep asistido por IA es más rápido que el manual — la lista de corte y el trade X⇒Y son más necesarios, no menos.
- Idea nueva a mitad de proyecto → sección "v2 / siguiente juego" de DESIGN.md, nunca al sprint actual [ver: gamedev/produccion-proceso].
- Al cerrar el MVP/first playable el scope se congela: de ahí en adelante la lista solo se ejecuta, no crece [ver: pipeline-completo].

## 5. Los errores del solo-dev asistido por IA

Los clásicos del solo-dev (restart syndrome, motor propio, comparar con AAA) están en [ver: gamedev/produccion-proceso]. Estos son los NUEVOS, específicos del dúo:

| # | Error | Mecánica del daño | Antídoto |
|---|---|---|---|
| 1 | **La fábrica corre más que la aduana** | El agente genera sistemas más rápido de lo que se integran, prueban y juegan; se acumula inventario de código no verificado | **WIP = 1**: nada nuevo hasta que lo anterior cumple su DoD completo (§2), incluido "alcanzable jugando" |
| 2 | **Features huérfanas** | Código que compila y "existe" pero ningún camino del juego lo alcanza (solo corre en su escena de test) | El DoD exige conexión al flujo real. Auditoría periódica: ¿qué % del código se ejecuta en una partida normal? Lo huérfano se conecta o se corta |
| 3 | **Polish prematuro** | El polish es barato de pedir ("agrégale juice") y esconde malas decisiones de diseño (Fullerton) [ver: gamedev/preproduccion] | Pasadas horizontales: todo el juego sube de calidad junto; el polish es una FASE con orden propio [ver: gamedev/produccion-proceso], no un condimento por sesión |
| 4 | **"Compila" = "funciona"** | La compilación verifica sintaxis, no comportamiento; en Unity además las excepciones de runtime NO detienen el play mode | Willison: "no commiteo código que no pueda explicar exactamente a otra persona". Cada cambio: test + play mode instrumentado + consola leída [ver: unity/unity-mcp-flujo §5] |
| 5 | **Sensación de velocidad sin medida** | METR: los devs se sintieron 20% más rápidos siendo 19% más lentos. El agente produce ACTIVIDAD visible que se confunde con PROGRESO | Medir por hitos shippeables jugados (§6), nunca por líneas/commits/sesiones. Si el build jugable no mejoró esta semana, no hubo progreso |
| 6 | **Vibe coding en producción** | "Olvidar que el código existe" (Karpathy) es legítimo SOLO en el prototipo desechable; en producción produce un codebase que nadie entiende cuando llega el bug raro | El prototipo se tira por contrato [ver: pipeline-completo]; del MVP en adelante, todo código es revisado, testeado y explicable |
| 7 | **Duplicación acumulada** | GitClear (211M líneas analizadas, 2020-2024): con asistentes IA las líneas clonadas subieron de 8.3% (2021) a 12.3% (2024) y el copy/paste superó al código movido/refactorizado por primera vez; el refactor cayó de ~25% a <10% de las líneas cambiadas | Sesión de consolidación periódica (cada 5-10 sesiones de feature, heurística de síntesis): el agente busca duplicados y los unifica; un fix que se aplica en un solo lugar |
| 8 | **Contexto envenenado** | Sesiones largas multipropósito degradan al agente; corregir 5 veces lo mismo lo empeora | 1 sesión = 1 objetivo; tras 2 correcciones fallidas, reset con prompt mejor que incorpore lo aprendido (Anthropic) |
| 9 | **El agente juzga diversión** | El agente puede reportar "la mecánica funciona y se siente bien" — lo segundo es alucinación: no juega, no siente | Todo juicio de diversión/feel/dificultad pasa por el humano jugando la build (§6) y por testers frescos [ver: gamedev/produccion-proceso] |
| 10 | **Documentos muertos** | CHECKPOINT/GDD desactualizados envenenan TODAS las sesiones futuras: el agente retoma sobre un estado falso | Actualización en la misma sesión del cambio (protocolo §2); doc que contradice al código = bug de máxima prioridad |

### Receta: el smoke test anti-huérfanos

El error 2 tiene antídoto automatizable: un PlayMode test que arranca el juego por su puerta REAL (la escena `Boot`) y verifica que el flujo llega a gameplay. Si una feature solo funciona instanciada a mano en una escena de test, este test no la ve — exactamente el punto: lo que el smoke test no alcanza, el jugador tampoco.

```csharp
using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

public class SmokeTests
{
    [UnityTest]
    public IEnumerator Boot_LlegaAGameplay_SinErrores()
    {
        // Nota: Unity Test Framework ya falla el test ante cualquier LogError inesperado
        yield return SceneManager.LoadSceneAsync("Boot", LoadSceneMode.Single);
        float timeout = Time.realtimeSinceStartup + 20f;
        while (SceneManager.GetActiveScene().name != "Game")
        {
            Assert.Less(Time.realtimeSinceStartup, timeout, "Boot nunca llegó a Game");
            yield return null;                     // aquí el juego navega solo o por
        }                                          // auto-avance de menú en modo test
        Assert.IsNotNull(Object.FindAnyObjectByType<PlayerController>(),
            "Game cargó sin Player: el flujo real está roto");
        LogAssert.NoUnexpectedReceived();          // ningún log inesperado en todo el flujo
    }
}
```

Requisitos: escenas en el Build Profile, asmdef de tests referenciando el asmdef del juego [ver: unity/unity-mcp-flujo §5], y un mecanismo de auto-avance del menú activable en test (flag/env). Corre en cada sesión como parte de la línea base verde. Ampliaciones naturales: un test por pantalla del flujo, un test que ejecuta cada verbo del jugador [ver: testing-qa].

## 6. Ritmo sostenible y momentum

La teoría de sostenibilidad (caso Barone como advertencia, tácticas Birkett, chequeo de sostenibilidad) está en [ver: gamedev/produccion-proceso]. El aterrizaje del dúo:

- **Hito chico shippeable cada 1-2 semanas**: algo que otra persona puede JUGAR (build itch por butler, TestFlight) — la receta CLI está en [ver: pipeline-completo]. El hito shippeable es la única métrica de progreso inmune al error 5.
- **El humano juega su propio build cada semana, en la plataforma target.** Innegociable y NO delegable: es el único circuito donde se detectan el aburrimiento, la fricción y el feel. El agente prepara la build el viernes (automatizado); el humano la juega el fin de semana; el triage del lunes alimenta el CHECKPOINT — la misma cadencia semanal del método Valve [ver: gamedev/produccion-proceso].
- **La cadencia del calendario la marcan los humanos, no el agente**: playtests con frescos, decisiones de scope, reviews de tienda. Planificar alrededor de eso; el agente rellena los huecos con trabajo delegable (tests, deuda, tooling) [ver: pipeline-completo].
- **El agente no se cansa; el humano sí.** El riesgo nuevo: el agente puede sostener un ritmo de generación que quema al humano que debe jugarlo, juzgarlo y decidirlo. El límite de WIP y el chequeo de sostenibilidad (≤40-45 h/semana del HUMANO) siguen aplicando aunque "el código se escriba solo".
- Momentum psicológico: sesiones que SIEMPRE cierran en verde con un avance registrado en CHECKPOINT. La sesión que deja el proyecto roto o el objetivo a medias es la que mata la moral y el retomar. Atascado en una pared → cambiar de sección y avanzar por otra (Yu #9), registrando el bloqueo.

### La semana tipo del dúo

Plantilla operativa (síntesis del ciclo Valve/Slay the Spire de [ver: gamedev/produccion-proceso] adaptada al dúo — calibrar por proyecto):

| Día | Humano | Agente |
|---|---|---|
| Lunes | Triage del playtest/build del finde; decide hipótesis y prioridades de la semana; firma cortes | Registra triage y decisiones en CHECKPOINT; actualiza lista de corte |
| Mar-Jue | Revisa lo integrado JUGANDO en Editor; responde el buzón de bloqueos | 1-2 sesiones de feature/día con DoD completo (WIP=1) |
| Viernes | Aprueba la build | Sesión de consolidación (deuda, duplicados, huérfanos) + build por CLI + subida (butler/TestFlight) [ver: pipeline-completo] |
| Finde | **Juega la build en la plataforma target** (y testers frescos si toca playtest) | Nada — o tareas delegables sin decisión: tests, tooling, docs |

La fila del finde es la que no se negocia: sin humano jugando, el lunes no hay triage y la semana entera del agente vuela a ciegas.

## 7. Cuándo parar un proyecto

Los kill criteria por etapa (concepto → prototipo → first playable → producción) están tabulados en [ver: pipeline-completo] y su teoría en [ver: gamedev/preproduccion] (kill early estilo Supercell: matar en prototipo es victoria barata). Reglas transversales del dúo:

- **El criterio de kill se escribe ANTES de empezar cada etapa** y vive en DESIGN.md. El agente lo cita textual cuando llega el momento de evaluar — su función es impedir que el costo hundido renegocie el criterio.
- El agente puede presentar la evidencia (playtests, métricas, semanas sin mejora de señal); **la decisión de matar es siempre humana**.
- Matar el proyecto ≠ fracaso del proceso: el archivo DESIGN.md con sus decisiones y su "v2" es el activo que queda. El siguiente proyecto se escala HACIA ABAJO [ver: gamedev/produccion-proceso].

### Kill criteria post-lanzamiento

El post-launch se presupuesta antes del launch [ver: gamedev/produccion-proceso]. Lo que casi nadie escribe: **cuándo termina**. Antes de lanzar, dejar en DESIGN.md:

| Elemento | Contenido (decidido EN FRÍO, pre-launch) |
|---|---|
| Ventana de estabilización | Periodo fijo post-launch solo para crashes/bloqueantes (heurística de síntesis: 2-4 semanas; lo importante es que sea FINITA y escrita) |
| Piso de señal | El umbral propio (ventas, jugadores activos, tendencia de wishlists/reviews) bajo el cual NO se producen updates de contenido. Sin piso escrito, todo resultado "casi justifica" seguir |
| Punto de decisión | Fecha concreta (p. ej. fin de la estabilización) donde se elige una de tres rutas: (a) señal fuerte → roadmap de contenido con su propio scope y lista de corte; (b) señal débil → modo mantenimiento: solo fixes críticos, el juego queda a la venta; (c) sin señal → cerrar desarrollo activo y arrancar el siguiente juego más chico |
| Regla de cadencia | Parches agrupados con cadencia, jamás en ráfaga de pánico: los all-nighters post-launch de Barone producían parches que "creaban tantos problemas como resolvían" [ver: gamedev/produccion-proceso] |

Por qué la ruta (c) es legítima y frecuente: estrategia Birkett — la supervivencia del solo-dev viene del PORTAFOLIO de juegos pequeños, no de resucitar uno con updates infinitos; las ideas restantes van a la v2/secuela (Yu) donde parten con lo aprendido. NO VERIFICADO en fuente independiente: la afirmación popular "los updates no reviven un launch muerto" no se pudo confirmar con datos en esta investigación — por eso el mecanismo aquí es el piso de señal propio escrito pre-launch, no una regla universal.

Cerrar desarrollo activo ≠ delistar: el juego sigue a la venta, el repo queda reproducible (editor en el último patch LTS, build por CLI documentada) para poder re-publicar ante un CVE o un port [ver: pipeline-completo].

## Reglas prácticas

- [ ] División fija: el agente ejecuta y verifica lo verificable por máquina; el humano decide diversión, estética, scope y kill. Ninguna decisión de esas tres se delega.
- [ ] 1 sesión = 1 objetivo escrito en una frase + DoD explícito. No cabe en una frase → se parte.
- [ ] Abrir sesión: leer CHECKPOINT.md + DESIGN.md, verificar línea base verde (compila + tests) ANTES de tocar nada.
- [ ] Cerrar sesión: DoD con evidencia + CHECKPOINT actualizado + commit + proyecto verde. Jamás cerrar roto.
- [ ] Todo "done" lleva evidencia leída: output de test, consola filtrada, build corriendo. "Compila" no es evidencia de nada más que sintaxis.
- [ ] DoD de toda feature incluye "alcanzable jugando desde el flujo real" — es el antídoto estructural de las features huérfanas.
- [ ] WIP = 1: nada nuevo entra hasta que lo anterior cumplió su DoD completo.
- [ ] Fix no trivial → causa raíz + test de regresión en el mismo commit [ver: testing-qa].
- [ ] Tras 2 intentos fallidos: instrumentar, no adivinar. Tras 2 correcciones humanas de lo mismo: reset de contexto con prompt mejor.
- [ ] Tres documentos vivos y solo tres: DESIGN.md (GDD 1 página + lista de corte + kill criteria), CHECKPOINT.md (estado/siguiente/decisiones), CLAUDE.md (reglas permanentes, podado).
- [ ] Los documentos se actualizan en la MISMA sesión del cambio; doc desactualizado = bug de máxima prioridad.
- [ ] Decisión tomada y registrada NO se reabre sin causa nueva — el registro existe para no re-discutir en cada sesión.
- [ ] Lista de corte desde el día 1, ordenada por costo × poco aporte; se corta desde arriba sin drama.
- [ ] Feature nueva → el agente responde con costo real + "¿qué sale a cambio?"; el humano firma; se registra.
- [ ] Medir progreso SOLO por hitos shippeables jugados; nunca por líneas, commits ni sensación de velocidad (METR).
- [ ] Build shippeable cada 1-2 semanas; el humano la juega en la plataforma target cada semana, sin excepción.
- [ ] Sesión de consolidación cada 5-10 sesiones de feature: duplicados, deuda, huérfanos.
- [ ] Kill criteria escritos antes de cada etapa Y antes del launch (ventana de estabilización + piso de señal + punto de decisión); el agente los cita, el humano decide.
- [ ] El ritmo lo limita el humano (≤40-45 h/semana suyas), no la capacidad de generación del agente.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Generar 3 sistemas en una sesión "aprovechando el envión" | WIP = 1; con 3 sistemas sin verificar no sabes cuál rompió qué [ver: unity/unity-mcp-flujo] |
| Feature que "existe" pero solo corre en su escena de test | DoD con "alcanzable jugando"; auditoría periódica de huérfanos: conectar o cortar |
| Declarar "funciona" porque compiló y la tool no dio error | Test + play mode instrumentado + consola leída; en Unity las excepciones de runtime no detienen el play mode |
| Confundir actividad del agente con progreso del juego | La única métrica es el build jugable mejorando semana a semana (METR: la sensación engaña incluso post-hoc) |
| Sesión multipropósito de horas que degenera | 1 objetivo por sesión; contexto lleno = agente peor; partir y resetear |
| Re-discutir cada sesión lo ya decidido | Sección "Decisiones" del CHECKPOINT; se cita, no se reabre sin causa nueva |
| CHECKPOINT que se actualiza "cuando haya tiempo" | Es el paso 7 del protocolo de cierre; sin él, la próxima sesión arranca sobre un estado falso |
| Pedir juice/polish por sesión porque es barato de pedir | El polish es fase con orden propio; antes del content complete solo el juice mínimo del prototipo [ver: gamedev/produccion-proceso] |
| Vibe coding del MVP en adelante | Código de producción: revisado, testeado, explicable (Willison); solo el prototipo es desechable por contrato |
| Aceptar el scope creep porque "el agente lo hace en 10 minutos" | Añadir es barato, MANTENER no: trade X⇒Y siempre; el costo real es testing × balance × UI × bugs |
| El agente opina que el juego "se siente bien" | No juega: feel, diversión y dificultad los juzga el humano en build real + testers frescos |
| Duplicar código porque el agente regenera en vez de reusar | Sesiones de consolidación; pedir explícitamente "busca si ya existe antes de crear" (GitClear: la duplicación es EL patrón de deuda de la era IA) |
| Cerrar la sesión con el proyecto roto "mañana lo arreglo" | La sesión siguiente hereda un estado rojo sin contexto; verde al cierre es innegociable |
| Post-launch sin criterio de fin: updates infinitos a un juego sin señal | Piso de señal + punto de decisión escritos PRE-launch; ruta (c): siguiente juego chico (portafolio Birkett) |
| Parches post-launch en ráfaga de pánico | Cadencia agrupada; los parches de madrugada crean tantos problemas como resuelven (caso Barone) |
| Delegar al agente la decisión de matar el proyecto | El agente presenta evidencia y cita el criterio escrito; la decisión es humana, siempre |

## Fuentes

**Web (consultadas en esta investigación):**
- Best practices — Claude Code docs oficiales (code.claude.com/docs/en/best-practices, Anthropic) — la base del protocolo de sesión: contexto que degrada al llenarse, "give Claude a check it can run", evidencia sobre afirmación, reset tras 2 correcciones fallidas, explore→plan→implement→commit, CLAUDE.md podado, review adversarial en contexto fresco.
- Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity — METR (metr.org, jul-2025) — RCT con 16 devs experimentados y 246 tareas reales: esperaban +24%, resultaron **−19%**, y post-hoc creían +20%. La fuente del "medir por hitos, no por sensación". Caveat propio del estudio: foto de early-2025, devs expertos en repos grandes que dominaban.
- AI Copilot Code Quality (2025 research) — GitClear (gitclear.com) — 211M líneas cambiadas 2020-2024: líneas clonadas 8.3%→12.3%, copy/paste supera a código movido por primera vez, refactor de ~25% a <10% de líneas cambiadas. La evidencia del error 7 (duplicación acumulada).
- Not all AI-assisted programming is vibe coding — Simon Willison (simonwillison.net, mar-2025) — definición de Karpathy ("olvidar que el código existe", válido para "throwaway weekend projects"), y la regla de producción: "no commiteo código que no pueda explicar exactamente a otra persona".
- The Scrum Guide — Schwaber & Sutherland (scrumguides.org) — definición canónica del Definition of Done y la regla de que lo que no lo cumple no se presenta como incremento: base de la tabla de DoD por tipo de tarea.
- Assistant package manual — docs.unity3d.com/Packages/com.unity.ai.assistant@1.0 — el asistente IA oficial de Unity: requiere Unity 6.2 (6000.2)+, cuenta Unity + puntos, modos /ask, /run y /code. Contexto de herramientas, no sustituto del flujo MCP.
- Effective context engineering for AI agents — Anthropic (anthropic.com/engineering) — *structured note-taking / agentic memory*: "notas persistidas fuera de la ventana de contexto" releídas tras cada reset como mecanismo de coherencia en tareas largas. El fundamento del CHECKPOINT.md.
- howtomarketagame.com — Chris Zukowski (blog + búsqueda interna) — consultado para kill criteria post-launch; no se encontró un artículo que respalde con datos "los updates no reviven un launch muerto", por eso esa afirmación queda NO VERIFICADA y el mecanismo propuesto es el piso de señal propio.

**Base sintetizada (esta base de conocimiento):**
- [ver: gamedev/produccion-proceso] — milestones y gates, método Valve, lista de corte, scope creep (71% de postmortems), polish en orden, sostenibilidad (Barone, Birkett, Yu): toda la teoría de proceso que este archivo operacionaliza.
- [ver: gamedev/preproduccion] — one-pager/GDD ligero (Librande), kill early (Supercell), criterios de kill por prototipo, scoping para equipo de 1: la fuente de DESIGN.md.
- [ver: unity/unity-mcp-flujo] — el ciclo sagrado de compilación, verificar sin ojos, límites del agente en el editor: el nivel técnico bajo el protocolo de sesión.
- [ver: pipeline-completo] — el mapa de etapas con checklists de salida y kill criteria por etapa, la cadencia de build semanal (butler/TestFlight) y el reparto humano/agente por etapa.
