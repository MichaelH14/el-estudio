# Retención y live-ops móvil

> **Cuando cargar este archivo:** al operar un juego móvil ya lanzado (o al diseñar para que se pueda operar) — leer la curva de churn D1/D7/D30, tapar el funnel install→FTUE→primer pago, montar remote config para tunear economía/dificultad sin update, correr A/B tests en cohortes, calendarizar eventos/temporadas, o decidir el timing y opt-in de las push. El QUÉ/POR QUÉ psicológico (hooks, dark patterns, modelos de negocio, benchmarks de mercado) vive en [ver: gamedev/psicologia-retencion-negocio]; el CÓMO técnico en Unity 6 (save, IAP, ads, notificaciones locales, analytics, tiempo) en [ver: pipeline/sistemas-meta]. **Este archivo no repite ninguno de los dos: aporta el ángulo operativo móvil** — la curva real, el funnel, y las palancas que se mueven en vivo. Estado: iOS/Android 2026.

## 1. Qué añade este archivo

Los dos base ya cubren la teoría (SDT, calendarios de recompensa, session hooks, dark patterns) y el cableado Unity (WalletService, Unity IAP 5.x, LevelPlay, notificaciones locales, analytics UGS/Firebase/GameAnalytics, reloj UTC/anti-cheat). Aquí va lo que **solo aparece cuando el juego ya tiene jugadores reales**: leer la curva de churn, operar contenido sin re-release, cambiar la economía remotamente, probar en cohortes, y hacerlo todo como un dev solo sin equipo de live-ops.

## 2. La curva de churn móvil: qué es "bueno" y por dónde se cae

Benchmark base (GameAnalytics, pool ~11.600 juegos, retención **clásica** = ¿volvió exactamente el día N?) — números completos y por plataforma/región en [ver: gamedev/psicologia-retencion-negocio §3]. La lectura operativa móvil:

| Corte | Mediana | Top 25% | Qué diagnostica | Palanca dominante |
|---|---|---|---|---|
| **D0→D1** | ~22% vuelven | 26-33% (iOS top) | Onboarding + primera impresión | FTUE, tiempo-a-diversión |
| **D1→D7** | 3.4-3.9% siguen | 7-8% | Core loop + primeros hooks | Daily loop, primeros hitos |
| **D7→D30** | <3% (75% de juegos abajo de 3%) | — | Metajuego + hábito | Live-ops, colección, social |

- **La aritmética brutal**: con D1 mediana de 22%, **~78% de los que instalan no vuelven ni una vez**. El churn no es una fuga lenta — es un acantilado en las primeras 24 h. Optimizar D30 con D1 roto es reordenar sillas en cubierta.
- **"40-20-10" (D1 40 / D7 20 / D30 10) ya es territorio top ~5%, no "bueno"** — la vara bajó vs 2023; el jugador ya no da la "oportunidad de cortesía". Trátalo como techo aspiracional, no como meta de partida.
- **Ranking por género** (GameAnalytics, dirección verificada; exactos por género → descargar el reporte completo, marcar el resto como orientativo): **arcade** lidera D1 (instalación impulsiva, loop inmediato); **mesa/cartas/puzzle/casino** lideran retención a medio-largo plazo (hábito diario, sesiones cortas repetibles); **multiplayer** lidera *duración de sesión* pero no número de sesiones ni playtime total. Elegir género fija tu curva antes que tu ejecución [ver: gamedev/generos].
- **Qué es "bueno" por tier de género** (heurística operativa, calibrar con tu propio soft launch — los exactos por género son orientativos hasta verificar el reporte):

  | Tier | Géneros | D1 "sano" | D7 "sano" | Naturaleza |
  |---|---|---|---|---|
  | Alto | puzzle, card/board, casino, merge | ≥35-40% | ≥12-15% | Hábito diario, sesión corta |
  | Medio | match-3, casual, midcore RPG, idle | ~30-35% | ~8-12% | Progresión + meta |
  | Bajo (por diseño) | hyper/hybrid-casual, arcade | ~30-35% D1 pero D7 se desploma | ~4-6% | Volumen alto, vida corta, monetiza rápido |

  Orientativo — verificar contra el reporte GameAnalytics del año y contra tu soft launch.
- **Regla de diagnóstico móvil**: si el churn se concentra en un nivel/paso exacto, es muro de dificultad o de legibilidad; si es difuso y en D0-D1, es el FTUE o el loop; si cae en D7-D30, falta daily loop / live-ops [ver: gamedev/psicologia-retencion-negocio §4].
- **Instrumenta la curva ANTES del soft launch** — sin retención por cohorte no puedes diagnosticar nada de esta tabla [ver: pipeline/sistemas-meta §6].

## 3. El funnel: install → FTUE → D1 → D7 → primer pago

Cada flecha es una fuga medible. Instrumenta una por una; no se arregla lo que no se mide por etapa.

| Etapa | Métrica de la etapa | Fuga típica móvil | Cómo taparla |
|---|---|---|---|
| **Store → install** | CVR de la ficha (conversion rate) | Icono/screenshots no comunican el género en 2 s | ASO: claridad de género en la ficha [ver: release-movil], [ver: mercado-movil] |
| **Install → open** | % que abre tras instalar | Descarga pesada, se olvidó | APK/IPA ligero, primera apertura rápida [ver: unity-movil-rendimiento] |
| **Open → FTUE done** | funnel de pasos del tutorial | Tutorial largo, meta confusa, muro de texto | Valor jugable en <60 s, un concepto por vez, cero muros de texto [ver: ux-ui/mobile-ux] |
| **FTUE → D1** | retención D1 | Nada que hacer al volver / no hay razón de volver | Daily loop mínimo desde el día 1 (§4) |
| **D1 → D7** | retención D7 | Loop se agota, sin metas de sesión | Quests diarias, primer hito de progresión, evento de bienvenida |
| **D7 → primer pago** | conversión a pagador (1-5%, orden de magnitud) | Prompt de compra a destiempo, valor no percibido | Primera oferta cuando ya hay hábito y contexto de necesidad, no en la sesión 1 |
| **Primer pago → recompra** | ARPPU, frecuencia | Nada nuevo que comprar, tienda estática | Rotación de ofertas, contenido nuevo (live-ops §5) |

- **El primer pago no es el objetivo del día 1.** Cronología sana: primero hábito (D7), luego oferta. La conversión sube cuando el jugador ya invirtió tiempo (sunk cost sano = "ya llegué hasta aquí"), no cuando se le interrumpe la primera sesión con una tienda.
- Cada bache del funnel tiene su propio evento de analytics; el funnel del FTUE (step_id) es el más rentable de instrumentar porque D1 es la fuga más grande [ver: pipeline/sistemas-meta §6].
- Números de conversión, ARPU/ARPPU, CPI y la ecuación LTV>CPI que decide si escalar: [ver: gamedev/psicologia-retencion-negocio §6] y [ver: monetizacion-movil].

## 4. El daily loop: qué hace el jugador cada día y por qué vuelve

El "session hook" a nivel diseño está en [ver: gamedev/psicologia-retencion-negocio §3]; aquí el ángulo móvil — cómo se ensambla un **día** de juego y las razones concretas de volver mañana:

| Razón de volver | Mecánica móvil | Filo / ética |
|---|---|---|
| "Me toca el premio" | Daily reward / streak con escalado | Extrínseco puro: arranca hábito, no lo sostiene; protege el streak con 1 "perdón" o genera churn por despecho |
| "Se me llenó la energía" | Energía/vidas con regen por timer | *Appointment mechanic*: funciona pero **dicta cuándo jugar** (mata autonomía) y hoy lee como diseño anticuado; usar con moderación |
| "El evento termina hoy" | Evento por tiempo limitado con countdown | FOMO legítimo si el countdown es real; falso/permanente = dark pattern [ver: gamedev/psicologia-retencion-negocio §2] |
| "Me falta 1 para completar" | Colección incompleta (cartas, sets) | El tirón más limpio: es intrínseco (competencia), no un pago por asistir |
| "Mi clan me necesita" | Guerra de clan, turnos async, regalos | El más duradero — toca *relación*, no solo premio; el que mejor sostiene D30 |
| "Quiero mejorar mi marca" | Leaderboard, mejor tiempo, otra build | El hook definitivo, intrínseco puro; el único que sobrevive sin live-ops |

- **Combina 2-3, no los seis.** El caso móvil clásico: daily reward + quests diarias + un evento rotativo. Apilar los ocho convierte el juego en una lista de tareas y quema al jugador.
- **El daily loop debe tener un final claro** ("ya hice lo de hoy"): sin cierre, el appointment mechanic se vuelve trabajo sin fin y produce burnout, no hábito.
- **Trigger interno > externo**: el objetivo real es que el jugador abra el juego por aburrimiento en la fila del supermercado, no porque una push lo empujó. La push arranca el hábito; el loop lo sostiene [ver: gamedev/psicologia-retencion-negocio §2].
- Timers, streaks y resets diarios se calculan con **hora de servidor**, no el reloj del device (que el jugador adelanta) — cap de offline rewards y clamp de retroceso en [ver: pipeline/sistemas-meta §7].

## 5. Live-ops: operar el juego sin re-release

Live-ops = mantener el juego vivo con contenido y eventos **sin publicar una versión nueva en la tienda**. Es la diferencia entre un juego que muere a las 6 semanas y uno que dura años. Sensor Tower (State of Mobile Gaming, datos 2024): con la UA más cara por privacidad, los estudios priorizaron **operar el catálogo existente sobre lanzar títulos nuevos** — session duration +7,9% y frecuencia de sesión +12% interanual, empujadas por live-ops y contenido.

| Palanca live-ops | Cadencia típica | Qué mueve | Requiere update de app? |
|---|---|---|---|
| **Daily/weekly quests** | Reset diario/semanal | D1-D7, sesiones/día | No (data-driven / remote config) |
| **Evento por tiempo limitado** | Cada 1-2 semanas | Picos de DAU y de gasto | No, si el contenido ya está en el build o se sirve remoto |
| **Tienda rotativa** | Diaria/semanal | ARPDAU, recompra | No (remote config §6) |
| **Temporada / battle pass** | ~4 semanas (móvil) | Retención + conversión predecible | No para la config; sí si trae assets nuevos |
| **Balance / economía** | Reactivo | Salud de la economía, dificultad | No (remote config §6) |
| **Contenido nuevo (niveles, cartas)** | Mensual+ | D30, reactivación | Normalmente sí (assets) — o addressables/descarga remota |

- **La regla de oro del contenido rotativo**: el motor de un evento debe ser **datos, no código**. Si cada evento exige recompilar y pasar review, no es live-ops — es un parche. Diseña eventos como configuraciones (fechas, multiplicadores, tabla de premios, tema) que se activan remoto sobre sistemas ya en el build.
- **Calendario, no improvisación**: un evento tardío tras meses de silencio **no resucita una cohorte muerta**. La cadencia constante es el producto; sostenerla indefinidamente es el compromiso real del F2P [ver: gamedev/psicologia-retencion-negocio §5].
- **Contraste conductual en vivo**: nunca recortes recompensas/drop rates de golpe entre temporadas — compensa por otro lado y comunícalo, o el nerf silencioso dispara review bombing [ver: gamedev/psicologia-retencion-negocio §2].
- **Assets sin update**: contenido nuevo que no cabe en "solo config" se sirve con **Addressables + descarga remota** (Cloud Content Delivery o tu CDN) para no forzar una release por cada evento con arte nuevo [ver: unity-movil-graficos], [ver: release-movil]. Ojo con el peso de descarga en datos móviles.
- **Surfacear el evento en la tienda**: Apple ofrece **In-App Events** (guideline 2.3.13) — eventos con fecha/hora reales, configurados en App Store Connect, que aparecen en la ficha y en búsqueda como canal de descubrimiento y reactivación; deben ser precisos y del evento (no del juego en general), y si se monetizan cumplen las reglas de IAP de Sección 3. Google Play tiene un surface equivalente de contenido promocional/LiveOps. Es UA orgánica gratis para tu calendario de eventos [ver: release-movil], [ver: mercado-movil].

## 6. Remote config: cambiar economía/dificultad/eventos sin update

El CÓMO de cablearlo (fetch, caché, offline) pertenece a servicios [ver: pipeline/sistemas-meta]; aquí la **elección y la estrategia**. Dos opciones reales en Unity 6 (2026):

| | **Unity Remote Config** (UGS) | **Firebase Remote Config** |
|---|---|---|
| Qué es | Servicio UGS de key-value namespaced con override values, sin deploy de app (doc oficial) | Servicio de Google, key-value con condiciones, sin update (doc oficial) |
| Se cambia sin update | Dificultad, calidad gráfica por device, settings por región/segmento, feature flags, rollout gradual, eventos on/off, **precios/recompensas/battle pass**, campañas A/B | Comportamiento/apariencia, segmentación por versión/idioma/audiencia GA, personalización ML, rollouts, A/B |
| Targeting | **Game Overrides**: qué jugadores reciben qué config, cuándo se entrega, experiencias por segmento (doc oficial) | Condiciones por audiencia GA, país, versión, custom signals; **personalización** por ML |
| A/B / experimentos | Campaigns & A/B tests integrados (samples oficiales) | A/B testing nativo con Google Analytics; **hasta 24 experimentos+rollouts concurrentes** (doc, límite 2026) |
| Interfaces | Package, Dashboard, REST API, CLI, Admin API, deployments por archivo (versionable) | SDK cliente, consola, Admin SDK, real-time updates (push sin polling) |
| Límites (2026) | En desarrollo activo, sin límites publicados en la doc | **3.000 parámetros/template, 300 versiones de template, 24 experimentos+rollouts concurrentes** (doc oficial) |
| Encaje | Ya estás en el ecosistema UGS (IAP, Analytics, Cloud Save) | Ya usas Firebase (Analytics, Crashlytics, FCM push) |

- **Regla de arquitectura**: cualquier número que puedas querer tocar en vivo (precios de tienda, drop rates, energía máxima, HP de un boss, fechas de evento, on/off de una feature) **NO se hardcodea** — se lee de remote config con un **default local seguro** en el build. Si el fetch falla o no hay red, el juego usa el default y sigue jugable; nunca bloquees el core loop esperando config.
- **Feature flags = red de seguridad**: envuelve toda feature nueva o riesgosa en un flag remoto. Si algo revienta en producción, lo apagas sin pasar por review de tienda (horas/días de espera que no tienes en una crisis).
- **La economía data-driven de [ver: pipeline/sistemas-meta §3]** (ShopOfferDef, CurrencyDef) es lo que hace esto posible: si la tienda es una lista de ofertas serializadas, remote config solo cambia los valores. Si está cableada en código, no.
- **Servidor manda para lo que toca dinero**: remote config del cliente es tuneable por el jugador con un proxy; para daily reset, tienda rotativa con valor real o anti-cheat, valida contra tu backend [ver: pipeline/sistemas-meta §7].
- **⛔ Límite de plataforma (Apple 2.5.2, verificado)**: remote config puede cambiar **valores/datos y flags** (precios, drop rates, dificultad, qué evento está activo), pero **NO puede descargar ni ejecutar código que introduzca o cambie features/funcionalidad** de la app — eso viola la guideline 2.5.2. Traducción operativa: la *lógica* de todo evento/feature debe estar en el build que ya pasó review; remote config solo decide qué se enciende y con qué números. Un "evento nuevo" es una config sobre sistemas ya presentes, nunca comportamiento nuevo bajado por red. Además (2.3.1a) toda feature debe estar declarada en las notas de review — feature flags que revelan funcionalidad oculta no divulgada son riesgo de rechazo.

## 7. A/B testing en producción

Probar un cambio en una cohorte (variante B) contra el statu quo (control A) y medir el efecto real, en vez de adivinar.

| Elemento | Guía operativa |
|---|---|
| **Qué probar** | Una variable por experimento: precio de un pack, dificultad del nivel 3, copy de la oferta, timing de la primera push, largo del FTUE |
| **Métrica objetivo** | UNA primaria decidida ANTES (D7, conversión, ARPDAU); las demás son guardarraíles (que B no rompa retención por subir ARPDAU) |
| **Asignación** | Aleatoria y estable por usuario (mismo user → misma variante siempre); Unity Game Overrides / Firebase A/B lo hacen |
| **Tamaño y duración** | Suficientes usuarios por brazo y ≥1 ciclo semanal completo (el comportamiento fin de semana ≠ entre semana); no leer el resultado a las 3 h |
| **Nuevos vs todos** | Cambios de FTUE/onboarding → solo cohortes **nuevas** (los viejos ya pasaron el tutorial y contaminan); cambios de economía → segmento controlado |
| **Decisión** | Ganó B solo si la primaria mejora sin que un guardarraíl se degrade; si no, se descarta — no se "casa" con la hipótesis |

- **Pitfall #1 — leer temprano**: los resultados oscilan al principio (poca muestra). Fija duración de antemano y no pares en el primer pico favorable (peeking = falsos positivos).
- **Pitfall #2 — métrica de vanidad**: subir ARPDAU canibalizando retención baja el LTV. La primaria debe ser la que mueve el negocio (normalmente LTV/retención), no la más fácil de mover.
- **Pitfall #3 — muchas variantes a la vez**: cada brazo divide la muestra; con tráfico de dev solo, prueba A vs B, no A/B/C/D.
- Un dev solo rara vez tiene volumen para significancia estadística fina — úsalo para cambios de **efecto grande** (¿FTUE de 3 pasos o de 8?), no para afinar un botón azul vs celeste.

## 8. Push notifications: re-engagement sin quemar el permiso

El API local (canales Android, permiso iOS, scheduling, reprogramar en background) está en [ver: pipeline/sistemas-meta §6]; **push remoto real** (segmentado desde tu backend) necesita FCM u otro servicio. Aquí la **estrategia**:

| Regla | Detalle |
|---|---|
| **Opt-in en contexto** | Pide el permiso cuando el jugador activa algo que lo usa (avísame cuando esté la energía, cuando sea mi turno) — **no en el primer arranque**. Android 13+ exige POST_NOTIFICATIONS; iOS pide autorización explícita |
| **Timing** | Cuando el jugador *puede* jugar (su ventana horaria habitual, aprendida de sus sesiones), no cuando a ti te conviene. Zona horaria del jugador, no la tuya |
| **Relevancia > frecuencia** | La **primera notificación irrelevante cuesta el permiso para siempre** [ver: gamedev/psicologia-retencion-negocio §2]. Cada push debe corresponder a un estado real (evento empezó, energía llena, tu turno) |
| **Reprograma el set** | Al ir a background, cancela TODO y reprograma según el estado actual; nunca notifiques algo ya resuelto [ver: pipeline/sistemas-meta §6] |
| **Segmenta (push remoto)** | No mandes lo mismo a todos: churned de 3 días ≠ jugador activo; el mensaje de reactivación es distinto del de engagement |
| **iOS vs Android** | iOS parte con menos opt-in (prompt obligatorio explícito); Android 13+ también lo exige ahora. Diseña asumiendo que buena parte NUNCA opta — las push son un bonus, no la base de la retención |

- **La push no arregla un juego sin razón de volver**: es un recordatorio del hook, no el hook. Empujar a un jugador a un loop aburrido solo acelera la desinstalación.
- **Deep link obligatorio**: la push abre directo a lo que anuncia (el evento, el turno), no al menú principal. Fricción tras el tap = tap desperdiciado.
- **ATT y ads**: si el re-engagement se apoya en campañas de UA con tracking, entra App Tracking Transparency (§9).

## 9. Analytics para retención: cohortes, embudos, North Star

Los eventos mínimos y las opciones de SDK (Unity Analytics / Firebase / GameAnalytics) están en [ver: pipeline/sistemas-meta §6]. El ángulo de *retención* — cómo se lee:

- **Cohortes, no agregados**: "retención D7 = 4%" no dice nada; "la cohorte que instaló tras el evento X retiene 6% vs 4% de la anterior" sí. Toda métrica de retención se segmenta por **cohorte de instalación**, canal, versión del juego y device.
- **Retención clásica vs rolling**: la clásica (¿volvió exactamente el día N?) da números más bajos que la rolling (¿el día N o después?). Los benchmarks de §2 son clásicos — al comparar contra cualquier cifra externa, verifica cuál usa o la comparación es inválida [ver: gamedev/psicologia-retencion-negocio §6].
- **Embudos por etapa** (§3): el del FTUE es el primero a instrumentar; cada paso un evento con step_id, y se lee dónde cae el % entre pasos.
- **North Star móvil**: elige UNA métrica que capture valor entregado (p. ej. sesiones con partida completada, no solo "abrió la app") y correla con LTV. Persíguela; las demás son diagnóstico.
- **Encuesta de churn**: los dashboards miden *qué* pasó, no *por qué*. Una micro-encuesta al desinstalar (o a jugadores dormidos que vuelven) captura el sentimiento que ninguna cohorte muestra — engagement resentido por FOMO/timers no se ve hasta que explota [ver: gamedev/psicologia-retencion-negocio §3].
- **Crash-free ≥ 99,5% antes de escalar UA**: un juego que crashea no tiene retención que medir; los crashes contaminan toda cohorte [ver: pipeline/sistemas-meta §6].

## 10. Live-ops para un dev solo: qué es realista

El F2P asume live-ops perpetuo; un dev solo no sostiene el ritmo de un estudio. Calibra el modelo a tu escala **antes** de comprometerte:

| Realista para 1 persona | Grande para 1 persona (evitar o automatizar) |
|---|---|
| Daily/weekly quests **generadas por config** (rotan solas) | Eventos artesanales semanales con arte nuevo cada vez |
| Tienda rotativa por **algoritmo/tabla**, no curada a mano | Temporadas narrativas con contenido original mensual |
| Balance por remote config (reactivo, cuando los datos lo piden) | Balance competitivo PvP con meta que exige tuneo constante |
| Battle pass **solo si** ya hay engagement por sesiones y el pase se puede rellenar con recompensas existentes | Gacha con pity, banners rotativos y economía dual |
| Feature flags para apagar problemas sin release | Soporte 24/7, community management en vivo |

- **Automatiza el calendario**: eventos que se activan por fecha desde remote config, quests que rotan por semilla determinista, tienda que se rellena de una tabla de pesos. El trabajo se hace **una vez** (el sistema), no cada semana (el contenido).
- **Elige un modelo que no exija live-ops perpetuo si no puedes sostenerlo**: premium o híbrido casual simple encaja mejor en equipos de 1-5 que un F2P de temporadas [ver: gamedev/psicologia-retencion-negocio §5], [ver: monetizacion-movil].
- **La honestidad de scope es supervivencia**: prometer una cadencia de eventos que no puedes mantener produce el peor resultado — un juego que arranca vivo y muere en público cuando el contenido se detiene.
- El contenido rotativo evergreen (variaciones proceduales, retos diarios generados, leaderboards semanales que se resetean solos) es el amigo del dev solo: **live-ops sin operación manual**.

## 11. Reactivación y winback: recuperar al 78% que se fue

La curva de §2 dice que la mayoría se va temprano; parte de esa masa es recuperable. La reactivación es una **motion de live-ops distinta** del engagement diario (§8) — otro público, otro mensaje, otra métrica.

| Segmento | Definición típica | Palanca de vuelta | Métrica |
|---|---|---|---|
| **Dormido** | Sin sesión 3-7 días, aún con la app instalada | Push segmentada (evento nuevo, "tu clan avanzó", energía llena) + deep link | Resurrection rate (% de dormidos que vuelven) |
| **Churned con app** | Sin sesión 7-30 días, app instalada | Evento de regreso / regalo de bienvenida-de-vuelta al abrir | Reactivación → re-retención D1 del que volvió |
| **Desinstalado** | Ya no está la app | Solo UA pagada (retargeting) o featuring/orgánico; la push no llega | CPI de reinstalación vs LTV [ver: monetizacion-movil] |

- **La reactivación honesta engancha al hook, no al miedo**: "salió contenido nuevo que te interesa" retiene; "vas a perder lo que ganaste" es contingencia negativa y quema la marca [ver: gamedev/psicologia-retencion-negocio §2].
- **El que vuelve tiene su propia curva**: mide la **re-retención** del reactivado como una cohorte aparte — traer de vuelta a alguien que se re-va en 1 día es gasto perdido. Un buen evento de regreso da al reactivado una razón de quedarse, no solo de abrir.
- **Trigger interno también aquí**: el mejor winback es que el propio contenido/comunidad genere el impulso de volver (un amigo que te reta, una temporada que empieza), no una ráfaga de push.
- **Prioriza por coste**: recuperar dormidos con app instalada es casi gratis (push + evento); reinstalar desinstalados cuesta CPI — solo tiene sentido si el LTV lo aguanta. Para un dev solo, la reactivación de dormidos vía calendario de eventos es el mejor retorno.

## Reglas prácticas

1. Instrumenta la curva de churn por cohorte (D1/D7/D30) y el funnel del FTUE **antes** del soft launch — sin eso no diagnosticas nada [ver: pipeline/sistemas-meta §6].
2. Diagnostica en orden: D1 roto = FTUE/loop; D7 roto = daily loop/hooks; D30 roto = metajuego/live-ops. No parchees D30 con D1 roto.
3. Trata "~78% no vuelven tras D1" como el problema #1: valor jugable en <60 s, un concepto por vez, cero muros de texto [ver: ux-ui/mobile-ux].
4. No pidas el primer pago en la sesión 1: primero hábito (D7), luego oferta en contexto.
5. Combina 2-3 session hooks (daily + quests + evento, o social), nunca los seis; el daily loop debe tener un "ya terminé lo de hoy" claro.
6. Protege streaks con un perdón ocasional; nunca castigues no conectarse (contingencia negativa).
7. Todo número tuneable (precios, drop rates, energía, dificultad, fechas de evento, on/off de feature) va en **remote config con default local seguro**, jamás hardcodeado.
8. Envuelve toda feature nueva/riesgosa en un **feature flag** remoto para apagarla sin pasar por review de tienda.
9. El motor de eventos es **datos, no código**: si un evento exige recompilar y pasar review, no es live-ops. Remote config cambia valores/flags, **nunca código nuevo** (Apple 2.5.2) — la lógica de cada evento ya está en el build; surfacea el calendario con Apple In-App Events (2.3.13) para UA orgánica gratis.
10. Mantén cadencia de contenido constante; un evento tardío no resucita una cohorte muerta. No te comprometas a un ritmo que no sostienes.
11. Nunca recortes recompensas de golpe entre temporadas (contraste conductual): compensa por otro lado y comunícalo.
12. A/B test: una variable, una métrica primaria fijada de antemano, ≥1 semana, sin peeking; cambios de FTUE solo sobre cohortes nuevas.
13. Con tráfico de dev solo, prueba solo cambios de efecto grande (A vs B), no matices; no dividas la muestra en 4 brazos.
14. Push: opt-in en contexto (no al arranque), timing en la ventana horaria del jugador, cada push = estado real, deep link directo; reprograma el set en cada background.
15. Segmenta la reactivación: el mensaje al churned de 3 días ≠ al jugador activo.
16. Toda métrica de retención se lee por cohorte (instalación, canal, versión, device); verifica clásica vs rolling antes de comparar.
17. Elige remote config por ecosistema: UGS si ya usas IAP/Analytics UGS; Firebase si ya usas FCM/Crashlytics/GA (límite 2026: 3.000 params, 24 experimentos concurrentes).
18. Hora de servidor para daily reset / tienda / eventos con valor real; cap de offline rewards [ver: pipeline/sistemas-meta §7].
19. Crash-free ≥ 99,5% antes de gastar en UA; un juego que crashea no tiene retención medible.
20. Como dev solo, automatiza el calendario (quests/tienda/eventos por config y semilla) — el trabajo se hace una vez en el sistema, no cada semana.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Optimizar D30/metajuego con D1 en el suelo | El acantilado es D0→D1; arregla FTUE y loop primero, el resto no importa si nadie llega |
| Pedir el primer pago en la sesión 1 "para monetizar temprano" | Hábito antes que oferta; la conversión sube tras la inversión de tiempo, no interrumpiendo la primera sesión |
| Economía y precios hardcodeados en código | Todo tuneable en remote config con default local; sin esto no hay live-ops ni A/B |
| "Eventos" que exigen recompilar y pasar review cada vez | Motor de eventos data-driven; el contenido es config sobre sistemas ya en el build |
| Intentar bajar comportamiento/features nuevos por remote config | Viola Apple 2.5.2: config = valores/flags, nunca código; la lógica va en el build revisado |
| Silencio de contenido y luego un evento "de rescate" | Cadencia constante o nada; una cohorte muerta no revive con un evento tardío |
| Nerf silencioso de drop rates entre temporadas | Contraste conductual = review bombing; compensa y comunica |
| Leer un A/B a las horas y "casarse" con la variante favorita | Duración fijada de antemano, primaria decidida antes, sin peeking; guardarraíles que B no puede romper |
| Probar cambios de FTUE sobre todos los usuarios | Los viejos ya pasaron el tutorial y contaminan; solo cohortes nuevas |
| Pedir permiso de push en el primer arranque | Opt-in en contexto; la primera push irrelevante quema el permiso para siempre |
| Push que abre al menú principal | Deep link directo a lo que anuncia; fricción tras el tap lo desperdicia |
| Retención agregada sin cohortes | Segmenta por cohorte/canal/versión; el agregado esconde qué campaña o build funciona |
| Comparar tu D7 contra una cifra externa sin verificar metodología | Clásica vs rolling, pool con UA vs orgánico — confirma antes de concluir |
| Bloquear el core loop esperando el fetch de remote config | Default local seguro; juega offline, aplica config cuando llegue |
| Prometer una cadencia de live-ops de estudio siendo dev solo | Calibra el modelo a tu escala; automatiza el calendario o elige premium/híbrido simple |
| Confiar en push para tapar un loop aburrido | La push recuerda el hook, no lo crea; arregla el loop [ver: gamedev/psicologia-retencion-negocio] |

## Fuentes

- **Unity Remote Config — Overview / What's Remote Config** (docs.unity.com/ugs) — verificado: qué se puede cambiar sin update (dificultad, calidad gráfica, economía, precios, battle pass, eventos on/off, feature flags), Game Overrides (targeting por segmento/tiempo), campaigns & A/B, interfaces (package/dashboard/REST/CLI/Admin API), deployments versionables; en desarrollo activo, sin límites publicados.
- **Firebase Remote Config — documentation** (firebase.google.com/docs/remote-config) — verificado: fetch/activate + real-time, segmentación (versión/idioma/audiencias GA/custom signals), personalización por ML, rollouts con control, A/B con Google Analytics; **límites 2026: 3.000 parámetros por template, 300 versiones de template, 24 experimentos+rollouts concurrentes**.
- **App Tracking Transparency — Apple Developer** (developer.apple.com/documentation/apptrackingtransparency) — verificado: permiso obligatorio antes de acceder al IDFA / tracking cross-app, `requestTrackingAuthorization`, estados authorized/denied/notDetermined/restricted, IDFA en ceros sin autorización; relevancia para SDKs de ads y UA de re-engagement.
- **Sensor Tower — State of Mobile Gaming (datos 2024, pub. 2025)** (sensortower.com) — verificado: mercado móvil vuelve a crecer (+4% IAP rev vs 2023, +7,9% duración de sesión, +12% frecuencia de sesión), auge de hybrid-casual (IAP+ads), y el giro de la industria a **priorizar live-ops del catálogo existente sobre lanzar títulos nuevos** por el encarecimiento de la UA en entorno de privacidad.
- **Google Play — Target API level requirements** (developer.android.com) — verificado: apps nuevas y updates deben apuntar a **API 36 (Android 16) desde el 31-ago-2026** (excepciones Wear/Auto/TV/XR); existentes API 35 para seguir visibles a usuarios nuevos; extensión posible hasta 1-nov-2026. Relevante porque un update de app (para assets/live-ops que no caben en config) obliga a cumplir el target vigente [ver: release-movil].
- **Apple — App Review Guidelines** (developer.apple.com/app-store/review/guidelines) — verificado: **2.5.2** (la app es self-contained; no descargar/instalar/ejecutar código que introduzca o cambie features/funcionalidad) — el límite duro de qué puede y no puede hacer remote config; **2.3.13 In-App Events** (eventos con fecha en App Store Connect como canal de descubrimiento, monetizables bajo Sección 3); **2.3.1(a)** (declarar toda feature en notas de review). Reglas de IAP/suscripción (3.1.1, 3.1.2) para eventos monetizados.
- **GameAnalytics — 2026 Mobile & PC Gaming Benchmarks** (gameanalytics.com/reports) — verificado que el reporte cubre retención D1/D7/D30, playtime y comportamiento de sesión, e insights global/regional; los **exactos por género están tras el signup del reporte** — los números de cuartil pool de §2 vienen del pool GameAnalytics vía [ver: gamedev/psicologia-retencion-negocio §3]; los splits por género de este archivo son orientativos hasta descargar el reporte del año.
- **gamedev/psicologia-retencion-negocio.md** (base propia) — el QUÉ/POR QUÉ: benchmarks de retención pool y por plataforma/región, session hooks, calendarios de recompensa, dark patterns, modelos de negocio, ARPDAU/CPI/LTV, contraste conductual; este archivo es su ejecución operativa móvil.
- **pipeline/sistemas-meta.md** (base propia) — el CÓMO en Unity 6: save robusto, IAP 5.x, LevelPlay, notificaciones locales (API Android/iOS), analytics (eventos mínimos, SDKs), reloj UTC/anti-cheat/hora de servidor; este archivo referencia esas piezas sin repetirlas.
