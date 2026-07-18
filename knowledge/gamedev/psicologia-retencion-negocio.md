# Psicología del jugador, retención y negocio

> **Cuando cargar este archivo:** al diseñar sistemas de retención/recompensa, elegir o revisar el modelo de negocio (premium, F2P, ads, battle pass), calibrar dificultad y frustración, interpretar métricas (D1/D7/D30, ARPDAU, LTV, CPI) o planear el lanzamiento en Steam/móvil.

## 1. Motivación: SDT aplicada a juegos

Marco canon: Self-Determination Theory (Deci & Ryan), llevada a juegos por Ryan, Rigby & Przybylski ("The Motivational Pull of Video Games", 2006; modelo PENS). Hallazgo central verificado en 4 estudios: **autonomía, competencia y relación predicen de forma independiente el disfrute y la intención de seguir jugando**.

| Necesidad | Qué es en un juego | Cómo satisfacerla (aplicable) | Cómo se rompe |
|---|---|---|---|
| **Competencia** | Sensación de maestría creciente | Reto calibrado + feedback claro e inmediato + progresión visible (skill real, no solo números) | Dificultad injusta, feedback ambiguo, progreso solo por grind |
| **Autonomía** | Actuar por voluntad propia | Elecciones significativas: builds, rutas, orden de objetivos, estilo de juego | Tutorial-riel largo, timers que dictan cuándo jugar, una sola build viable |
| **Relación** | Sentirse conectado/importante para otros | Co-op, clanes, NPCs que reaccionan al jugador, async social (ghosts, mensajes) | Social forzado para progresar, matchmaking tóxico sin herramientas |

**Intrínseco vs extrínseco:**
- Motivación intrínseca = jugar porque la actividad en sí satisface (dominar el combate, explorar). Extrínseca = jugar por la recompensa externa (login bonus, cofre diario).
- Riesgo clásico de SDT (efecto de sobrejustificación): **recompensas extrínsecas sobre una actividad ya intrínsecamente divertida pueden desplazar la motivación intrínseca** — el jugador pasa de "juego porque me gusta" a "juego por el premio", y cuando el premio deja de crecer, se va.
- Heurística: usa lo extrínseco para *iniciar* el hábito (primeros días) y lo intrínseco para *sostenerlo* (maestría, expresión, comunidad). Un juego cuyo único gancho a D30 son recompensas de login está muerto.
- Las recompensas extrínsecas que *informan* competencia (medalla por hazaña difícil) dañan menos que las que solo *pagan* tiempo (cofre por conectarte).

## 2. Calendarios de recompensa, dopamina y hábito

Fuente canon: John Hopson, "Behavioral Game Design" (Gamasutra/Game Developer, 2001). Aplica condicionamiento operante a juegos.

| Calendario | Regla | Patrón de conducta que produce | Ejemplo en juego |
|---|---|---|---|
| **Ratio fijo** | Premio cada N acciones | Ráfaga de actividad → pausa larga post-premio (riesgo de abandono en la pausa) | Level-up por XP fija |
| **Ratio variable** | Premio cada ~N acciones (aleatorio) | **La tasa de actividad más alta y constante de todas** — siempre "el próximo intento puede ser el premio" | Drops de loot raro, gacha |
| **Intervalo fijo** | Premio tras T tiempo | Pausa → actividad creciente al acercarse T | Cosecha/energía con timer |
| **Intervalo variable** | Premio tras ~T tiempo (aleatorio) | Chequeo continuo a ritmo moderado | Spawn aleatorio de evento/boss |

Advertencias del propio Hopson (no son opcionales):
- **Extinción**: si las recompensas cesan de golpe, el resultado es frustración e ira — no indiferencia. Endgame sin nuevas fuentes de recompensa = rage-churn.
- **Contraste conductual**: reducir recompensas respecto a lo que el jugador ya recibía (nerf de drop rates, temporada más tacaña) provoca abandono desproporcionado. Cambios graduales, y siempre varias actividades recompensables en paralelo.
- Evitar **contingencias negativas** (castigo por no jugar, tipo el deterioro de castillos de Ultima Online): generan sesiones por obligación, resentimiento y burnout.

**Modelo Hooked (Nir Eyal)** — el bucle de hábito en 4 fases: **trigger** (externo: push/icono → interno: aburrimiento, rutina) → **acción** (mínima fricción) → **recompensa variable** (la variabilidad es lo que dispara dopamina y el "estado de caza") → **inversión** (el jugador mete tiempo/datos/progreso que mejora la próxima vuelta y le crea coste de salida). Un juego con retención de hábito real logra que el trigger sea interno ("me aburro en la fila → abro el juego"). Eyal mismo advierte: el mismo mecanismo que crea hábitos útiles crea adicciones si se explota.

Matiz de dopamina que cambia decisiones de diseño: la dopamina responde a la **anticipación** de la recompensa más que a recibirla — las recompensas 100% predecibles dejan de generar deseo (por eso el login bonus fijo se siente trámite a la semana). Diseña el momento *antes* de abrir el cofre (revelado, escalada, casi-premio) con tanto cuidado como el contenido del cofre — y recuerda que ese mismo principio, apuntado a dinero real, es exactamente la mecánica de una slot machine.

### La línea ética: engagement vs explotación

Regulación real a 2026: la FTC multó a Epic (Fortnite) con **US$520M en 2022**, de los cuales $245M por **dark patterns** en el flujo de compra (botones confusos e inconsistentes, cargos sin autorización, especialmente a menores). La FTC clasificó el **grinding deliberado** ("hacer la versión gratis tan tediosa que induce a pagar") como dark pattern. Bélgica prohibió de facto las loot boxes pagadas con dinero real (2018) por considerarlas apuestas; varios países europeos mantienen escrutinio activo.

| Dark pattern (evitar) | Por qué es explotación |
|---|---|
| Loot boxes pagadas con odds ocultas | Apuesta sin regulación; ilegal en Bélgica y bajo escrutinio en más países |
| Moneda premium en ratios raros (1.100 gemas, packs de 980) | Ofusca el precio real en dinero |
| Grinding diseñado para doler y vender el skip | Dark pattern según la FTC (2022) |
| FOMO artificial agresivo (ofertas con countdown falso o permanente) | Compra por pánico, no por valor |
| Flujo de compra confuso / sin confirmación | Literalmente lo multado en Fortnite |
| Pay-to-win en PvP | Convierte el matchmaking en subasta |
| Castigo por no conectarse (pierdes lo ganado) | Contingencia negativa: juega por miedo |

Notas operativas adicionales:
- Apple y Google exigen publicar las probabilidades de cualquier loot box / mecánica aleatoria de pago en sus stores. Si tu juego las tiene, las odds van visibles — es requisito de plataforma, no opcional.
- Responsabilidad con big spenders: Grinding Gear Games (PoE) llegó a rechazar compras de jugadores que daban señales de gastar más de lo que podían permitirse. Un diseño sano no depende de extraer dinero de jugadores en pérdida de control; si tu curva de ingresos vive de 5 personas gastando miles, tienes un problema ético y de negocio (churn de un whale = cráter).
- Push notifications son triggers externos legítimos (evento empezó, tu turno llegó) hasta que se vuelven spam: la primera notificación irrelevante cuesta el permiso de notificaciones para siempre.

Test honesto de la línea: **¿el jugador, con información completa y en frío, volvería a hacer esa compra/sesión?** Si el diseño depende de que NO esté en frío (impulso, sunk cost, confusión), está del lado equivocado. Variable ratio para ritmo de juego = herramienta legítima; variable ratio ligado a dinero real = zona de apuestas.

## 3. Retención: números, hooks y churn real

Benchmarks GameAnalytics 2025 (pool ~11.600 juegos móviles, 16 géneros — los números reales, no los aspiracionales):

| Métrica | Bottom 25% | Mediana | Top 25% |
|---|---|---|---|
| **D1** | ≤10-11% | ~22% | 26-28% (iOS top: 31-33%) |
| **D7** | ~1.5% | 3.4-3.9% | 7-8% |
| **D28/D30** | — | <3% (el 75% de juegos está debajo de 3%) | — |
| Sesión | — | 5-6 min | 8-9 min |
| Sesiones/día | — | ~4 (midcore: 6-7) | — |
| Playtime diario | — | ~22 min | top 2%: hasta 4h |

- La regla clásica "40-20-10" (D1 40%, D7 20%, D30 10% = juego excelente) sigue circulando, pero con los datos 2025 eso es territorio top ~5%, no "bueno". La tendencia es a la baja vs 2023 (D1 mediana venía de 28-29%): los jugadores ya no "le dan una oportunidad" al juego — esperan valor inmediato.
- Por género (GameAnalytics): arcade lidera D1; mesa/cartas/puzzle/casino lideran retención a medio-largo plazo; multiplayer lidera duración de sesión (pero no playtime total ni número de sesiones).
- Por plataforma y región: iOS retiene mejor que Android en el top quartile (D1 31-33% vs 25-27%); la mejor región en retención es Medio Oriente (D1/D7/D28 de 22.6%/4.9%/1.5%), las peores África y Asia — relevante si vas a hacer soft launch: elige un mercado representativo de tu público real, no el más barato.
- Ojo con fuentes de marketing/UA que citan "D7 promedio 15-20%": miden pools sesgados (juegos con presupuesto de UA) o retención rolling. Los números de arriba (retención clásica, pool masivo) son la vara honesta para un dev independiente.
- **D1 mide onboarding y primera impresión; D7 mide el core loop; D30 mide metajuego/hábito.** Diagnostica en ese orden — no arregles metajuego si D1 está roto [ver: ux-ui-onboarding].

**Session hooks** (razones para volver — combinar 2-3, no las 8):
- Daily rewards y streaks (extrínseco puro: arranca hábito, no lo sostiene; un streak roto sin protección genera churn por despecho).
- Appointment mechanics (cosecha/energía/timers): funcionan pero son doble filo — dictan cuándo jugar (mata autonomía) y hoy leen como diseño anticuado/manipulador.
- Quests diarias/semanales con expiración; eventos por tiempo limitado; battle pass (sección 5).
- Hooks sociales: guerra de clan, turnos async, regalos entre amigos — los más duraderos porque tocan relación, no solo premio.
- Cadencia de contenido en vivo (temporadas, rotaciones): sostiene D30+, pero solo si el equipo puede producirla indefinidamente — un evento tardío tras meses de silencio no resucita una cohorte muerta.
- El hook definitivo es intrínseco: "quiero probar otra build / mejorar mi tiempo / ver qué sigue".

**Por qué se van de verdad** (datos de estudios de drop-off, no suposición):
1. Onboarding malo: tutorial largo, metas confusas, tarda en llegar lo divertido. La primera sesión predice el churn. Caso documentado: menú con 12 iconos tras el tutorial → 61% tocó la tienda sin guía, vagó y desinstaló.
2. Sobrecarga cognitiva: demasiados sistemas/decisiones de golpe.
3. Fricción técnica: cargas lentas, trabas de >3 min en un paso del onboarding.
4. Monetización hostil: pay-to-win percibido, ads agresivas, prompts de compra a destiempo.
5. Y la causa que ningún dashboard muestra: **el core loop no es divertido**. La retención no se "añade" con features encima de un loop flojo [ver: fundamentos-diseno].

## 4. Dificultad y frustración: rage-quit vs reto justo

- **Flow** (Csikszentmihalyi, aplicado a juegos): el canal entre ansiedad (reto >> habilidad) y aburrimiento (reto << habilidad). Como la habilidad crece, la dificultad debe crecer — pero en sierra: pico de reto → valle de consolidación/poder, no rampa lineal.
- **Paradoja del fracaso** (Jesper Juul, *The Art of Failure*): buscamos voluntariamente juegos que nos garantizan fallar, porque escapar del fracaso mejorando es el disfrute central. El fracaso motiva **cuando el jugador se lo atribuye a su ejecución y ve el camino a mejorar**. Juul distingue metas completables (una vez), transitorias (partidas repetibles) y de mejora (superar tu marca) — cada una tolera una relación distinta con el fracaso.
- **Rage-quit = fracaso que el jugador percibe como culpa del juego**: controles imprecisos, muerte por información oculta, castigo desproporcionado (perder 20 min de progreso por un error), RNG que decide, dificultad a saltos. Reto justo: reglas legibles, muerte explicable ("fue mi culpa"), reintento inmediato, castigo proporcional.
- **Caso Celeste (Maddy Thorson)**: juego brutalmente difícil con Assist Mode (velocidad del juego reducible en pasos de ~20%, dash extra, invencibilidad). Nació del debate público sobre Cuphead; se llamaba "Cheat Mode" y lo renombraron por juicioso. Thorson: "Assist Mode rompe el juego… pero las opciones importantes son las intermedias" — granularidad para ajustar fino, no un botón de trivializar. Implementarlo tomó días; la identidad del juego (reto + empatía) quedó intacta. Lección: dificultad como opt-in granular > "easy/normal/hard" ciego.
- Curva de aprendizaje ≠ curva de dificultad: enseña un concepto por vez, en entorno seguro, y luego examina combinando [ver: level-design]. El pico de churn por dificultad suele estar en los primeros muros, no en el endgame.
- Muerte con dignidad: reintento en segundos (Celeste, Super Meat Boy) permite dificultad altísima con frustración baja. Tiempo-hasta-reintento alto exige dificultad más suave.
- Ajuste dinámico de dificultad (DDA): existe el espectro desde rubber-banding invisible hasta directores de intensidad (el AI Director de Left 4 Dead, que modula spawns según el estrés del grupo, es el caso de referencia). Regla: el DDA que el jugador detecta se siente como trampa en ambas direcciones — o insulta su competencia o invalida su victoria. Si lo usas, que module ritmo/recursos, no el resultado del duelo.
- Señal de diagnóstico: si el churn se concentra en un punto exacto del contenido, es un muro de dificultad o de legibilidad; si es difuso y temprano, es el onboarding o el loop [ver: ux-ui-onboarding].

## 5. Modelos de negocio: pros/contras y encaje por género

| Modelo | Cómo gana | Pros | Contras | Géneros que lo aguantan |
|---|---|---|---|---|
| **Premium** (pago único) | Venta + DLC | Diseño libre de metagame de monetización; audiencia Steam/consola lo prefiere | Todo el ingreso al lanzamiento; sin cola de ingresos; presión de wishlists | Narrativa, single-player, roguelikes, horror, indie PC en general |
| **F2P + IAP** | Compras in-app | Techo de ingresos altísimo; funnel de adquisición barato de entrada | Exige live-ops perpetuo; economía dual; riesgo ético constante; <5% paga | Multiplayer competitivo, collection-RPG/gacha, match-3, estrategia 4X móvil |
| **F2P + ads** | Impresiones | Monetiza al 100% de usuarios; sin diseñar economía IAP | ARPDAU bajo ($0.05-0.15); depende de volumen enorme; UX en riesgo | Hyper-casual, casual, puzzle |
| **Híbrido (IAP+ads)** | Ambos | Hoy el estándar móvil ("hybrid-casual"); rewarded + IAP de conveniencia | Complejidad de balanceo | Casual/mid-core móvil |
| **Battle pass** | Pase de temporada $5-15 | Conversión fuerte, gasto predecible, retención por metas | ARPPU limitado; puede canibalizar otras compras; FOMO como motor | Multiplayer por sesiones con engagement alto |
| **Suscripción** | Cuota mensual | Ingreso recurrente estable | Solo viable con catálogo (Game Pass/Apple Arcade) o como add-on de un F2P gigante (Fortnite Crew); un indie no sostiene una suscripción propia | Servicios/plataformas, no juegos sueltos |

Apuntes por modelo:
- **Premium**: heurística extendida en la comunidad Steam — no subvalorar el precio: un precio muy bajo señala baja calidad, deja sin margen para rebajas (el motor comercial de Steam durante años post-launch) y no lo compensa el volumen.
- **Suscripción en la práctica**: tres formas reales — catálogo de plataforma (Game Pass, Apple Arcade: cobras un deal fijo por entrar, útil para de-riskear desarrollo a cambio de techo limitado), add-on sobre un F2P masivo (Fortnite Crew: moneda mensual + pase + cosmético exclusivo) y suscripción propia (solo sostenible con MMO/servicio con contenido constante). Para un dev solo, la única puerta realista es la primera.
- **F2P**: asume live-ops perpetuo desde el diseño — temporadas, eventos, balance. Si no puedes sostener ese ritmo de producción [ver: produccion-proceso], el modelo te queda grande aunque el juego sea bueno.

**Ads: tipos y su impacto medido en UX** (datos de redes de ads — sesgo pro-rewarded posible, pero la dirección es consistente entre fuentes):

| Formato | UX | Datos |
|---|---|---|
| **Rewarded video** (opt-in: ver ad por premio) | La mejor tolerada: 75% de jugadores la ve como poco disruptiva | 1-2 rewarded/día correlaciona con MEJOR D7 (52%) que cero ads (45%); "retry ad" tras perder: +25pp de D1 en ese estudio |
| **Interstitial** (pantalla completa forzada) | La que más churn causa | Interstitial cada nivel → 15-25% abandona en la primera sesión; una sola exposición disruptiva sube churn 6-7%; en pantallas de recompensa, el quit rate se triplica |
| **Banner** | Ignorable; ingreso mínimo | Contamina UI por centavos |
| **Offerwall/playables** | Nicho | Solo con audiencia que lo espera |

Regla: rewarded integrada al loop (revivir, doblar premio, girar de nuevo) puede SUMAR retención; interstitial es un impuesto que se paga en churn — si se usa, nunca sobre pantallas de recompensa ni en los primeros minutos.

**Battle pass en detalle** (Deconstructor of Fun; GDC 2020 "Clash of Clans: Bigger, Better, Battle Pass" — Eino Joas):
- Motor psicológico: FOMO en tres capas — perder lo ya ganado, "desperdiciar" el tiempo jugado sin pase, y perder cosméticos irrecuperables.
- Estructura típica: track free + premium, temporada de ~1 mes (móvil) a 8-12 semanas, misiones que empujan exploración horizontal (probar modos/personajes = retención). Temporadas más cortas mantienen el atractivo alto cerca del inicio.
- Tres filosofías de pacing entre tracks: simétrico (mismo ritmo en free y premium), premium cargado (presión monetaria) o free cargado (apuesta por retención). Elegir una es una decisión de posicionamiento, no un detalle.
- El efecto retención es más fuerte en quienes YA compraron el pase (protegen su inversión — fase "investment" del modelo Hooked) que en los free; el pase retiene mejor de lo que convierte.
- Económicamente: convierte mucho, pero casi todo el ingreso es la compra inicial del pase (ARPPU limitado). Caso real de canibalización: la introducción del pase en **Clash Royale** coincidió con caída de ingresos totales. En **Clash of Clans** funcionó porque acompañó una expansión de la economía, no la sustituyó.
- Mitigaciones vistas en la industria: pases no expirables y compra de pases viejos (Halo Infinite), recompensas en bucle post-completado (MTG Arena), niveles extra (Wild Rift).

### Monetización que arruina el diseño vs la que convive

| Caso real | Qué pasó | Lección |
|---|---|---|
| **Dungeon Keeper móvil (EA, 2014)** — arruina | Timers de horas en el corazón del juego (excavar) + pagar por saltarlos. Outcry público, regulador de publicidad UK obligó a corregir anuncios; EA admitió "misjudged the economy" | Si la monetización vende el alivio de un dolor que tú creaste, el juego ES la tienda. Mató la marca |
| **Star Wars Battlefront II (2017)** — arruina | Loot boxes con ventaja de progresión/poder en un AAA de $60. Backlash masivo, EA retiró las microtransacciones en el lanzamiento; el caso aceleró la regulación de loot boxes en Europa | Pagar por poder en PvP + precio premium = doble cobro; la comunidad lo castiga y los reguladores toman nota |
| **Path of Exile (GGG)** — convive | F2P con monetización "divorciada a propósito de las mecánicas" (Chris Wilson): cosméticos, supporter packs y conveniencia (stash tabs); cero puertas de pago al contenido o al poder | El jugador paga por respeto y apoyo, no por presión. Una década de sostenibilidad |
| **Fortnite** — convive (con asterisco) | Solo cosméticos y battle pass: cero poder vendido; el juego domina años | El asterisco: la multa FTC 2022 fue por el FLUJO de compra (dark patterns), no por QUÉ vende. Puedes vender lo correcto de forma incorrecta |
| **Clash Royale** — degradación gradual | Pase canibalizó ingresos; años de ajustes de economía percibidos como avaricia fueron erosionando la confianza | La confianza monetaria se pierde por acumulación, no por un solo evento |

Principio operativo: la monetización sana vende **expresión** (cosméticos), **contenido** (expansiones, DLC), **conveniencia no dolorosa** (slots de inventario) o **apoyo** (supporter packs). La tóxica vende **poder** (P2W), **alivio de dolor fabricado** (timers/grind diseñado) o **apuestas** (loot boxes pagadas). Diseña el juego completo primero y pregúntale a la monetización "¿qué puedes ofrecer sin tocar nada?" — no al revés.

## 6. Métricas del negocio: qué significan y rangos

| Métrica | Definición | Rangos típicos (móvil, 2025) |
|---|---|---|
| **DAU/MAU** | Usuarios activos diarios/mensuales; su ratio (stickiness) mide hábito | Stickiness >20% es fuerte |
| **ARPDAU** | Ingreso promedio por usuario activo y día | Ads casual: $0.05-0.15 · IAP midcore/RPG: $0.30-1.00+ · social casino: el más alto del mercado |
| **ARPU (lifetime)** | Ingreso por usuario en su vida | Hyper-casual ~$0.86 · match ~$3 · party ~$4.90 (Appodeal 2025) |
| **LTV** | Valor total de un usuario durante su vida en el juego ≈ ARPDAU × días de vida esperados | $5-50 según género/mercado |
| **CPI** | Costo de adquirir una instalación pagada | Hyper-casual: $0.25-0.80 Android / $0.50-1.50 iOS · puzzle: $0.80-2 / $1.50-3.50 · match-3: $1-2.50 / $2-5 · midcore RPG: $2.50-6 / $4-12 · estrategia: $2-5 / $3.50-10 · casino iOS: hasta ~$21 |
| **Conversión a pagador** | % de jugadores F2P que alguna vez paga | Un dígito bajo; la mayoría del ingreso IAP viene de una fracción pequeña de pagadores ("whales") — NO VERIFICADO un % exacto en esta investigación; asume 1-5% como orden de magnitud |
| **ROAS** | Retorno del gasto publicitario por cohorte (D7/D30) | Se mide contra la ventana de payback definida |

- Retención **clásica** (¿volvió exactamente el día N?) vs **rolling** (¿volvió el día N o después?): la rolling siempre da números más altos. Los benchmarks de este archivo son clásicos. Al comparar contra cualquier cifra externa, verifica primero cuál de las dos usa — es la fuente número 1 de comparaciones inválidas.
- Concentración de gasto: cifras ampliamente citadas en la industria (Tapjoy/Adweek y similares) dicen que **~5% de los pagadores genera 65-70% del ingreso IAP** ("whales"). NO VERIFICADO con fuente primaria en esta sesión — trátalo como orden de magnitud, no dato duro. La implicación de diseño sí es sólida (ver aviso ético de PoE en sección 2): un negocio que depende de extraer casi todo su ingreso de un puñado de jugadores es frágil (un whale que se va = cráter) y éticamente riesgoso.
- **La ecuación que decide si un F2P vive: LTV > CPI con margen.** Heurística de la industria: CPI objetivo entre 30-70% del LTV según ventana de payback y tolerancia al riesgo. Si tu LTV proyectado no supera el CPI de tu género, no tienes negocio — tienes un hobby caro.
- ARPDAU sin retención es vanidad: LTV = monetización × permanencia. Subir D7 suele mover más el LTV que exprimir ARPDAU.
- Para un dev solo sin presupuesto de UA: el "CPI" real es contenido viral/orgánico, y la métrica honesta es retención + conversión — no intentes competir comprando instalaciones en géneros de CPI alto.

## 7. Lanzamiento y wishlists: lo mínimo que un dev solo debe saber

**Steam** (datos de Chris Zukowski / howtomarketagame y GameDiscoverCo):
- Publica la página de Steam **lo antes posible** — en cuanto tengas algo mostrable. Las wishlists no caducan ("wishlists aren't milk"); solo se dañan si el juego cambia de género/estilo drásticamente.
- La página necesita: **capsule profesional** (paga un artista antes que pagar ads), género visual consistente, ≥3 entornos distintos en screenshots (señal de "no es asset flip"), tráiler que abra con **gameplay real** en los primeros segundos.
- Umbrales de **Popular Upcoming** (Zukowski, dato actualizado jun-2026 — Valve subió la vara respecto al viejo "con 7.000 ya estás dentro"): Bronze <6.000 wishlists (aparición rara y breve) · Silver 7.000-10.000 (aparición breve) · Gold 10.000-20.000 (todo el mes previo al lanzamiento) · Diamond 300.000+ (2+ meses de exposición). Capsule floja + pocas reviews te suprime igual con cualquier cifra. Trata "7.000" como piso histórico, no como meta segura — verifica el número vigente antes de fijar tu objetivo, el algoritmo se mueve.
- Esa escala de *visibilidad* es distinta de la escala de *resultados de ingreso* (no confundirlas): Bronze (<$10K, el algoritmo te ignora) · Silver ($10K-249K, viable solo si el scope fue contenido; ~20-30K wishlists) · Gold ($250K+, Valve te promueve; 30-50K wishlists) · Diamond ($1M+; ~100K+).
- Conversión wishlist→venta primera semana (GameDiscoverCo): ~15% con <5K wishlists, ~20% con 5-40K, ~23-25% por encima. **~1.000 reviews ≈ $150K+ bruto** — el proxy público más fiable del éxito ajeno.
- El género decide tu techo antes que tu talento: % de juegos que llegan a 1.000 reviews — open world survival craft 20.8%, horror 3.2%, RPG 2.4%, **plataformas 2D 0.18%**. Elegir género es una decisión de negocio [ver: generos].
- Demo + Next Fest: participa UNA vez, con el juego listo para impresionar (Next Fest es one-shot por juego). Retrasa el lanzamiento si tienes un Next Fest pendiente, la página débil o campañas de creadores confirmadas; lanza ya si las wishlists se estancaron sin tácticas nuevas, llevas >3 años de desarrollo o el presupuesto se agota.
- Cálculo inverso para fijar tu meta de wishlists (presskit.gg): (1) define cuánto dinero necesitas, (2) asume que el primer mes trae ~25-40% del ingreso del primer año, (3) aplica la conversión wishlist→venta de tu rango, (4) divide por tu precio. Eso da la meta ANTES de fijar fecha, no después.
- Timing de lanzamiento: evita las semanas de mega-lanzamientos y rebajas de Steam; el resto importa menos de lo que se cree.

**Móvil:**
- Sin presupuesto de UA no hay "lanzamiento" móvil clásico: hay soft launch (mercado pequeño, ej. Filipinas/Canadá... para medir D1/D7 y ARPDAU reales), iterar hasta que las métricas aguanten, y solo entonces escalar — o apostarlo todo a featuring/orgánico/viral.
- La decisión go/no-go es la ecuación de la sección 6: si con CPI real del género y tu LTV medido no hay margen, escalar es quemar dinero.
- ASO básico (icono, screenshots, keywords) es el equivalente móvil de la página de Steam: misma lógica de claridad de género en 2 segundos.
- En ambos ecosistemas, el marketing mínimo viable de un dev solo es: página/ficha clara del género + demo o gameplay honesto + presencia donde ya vive su nicho (subreddits, Discords, un devlog) — antes que cualquier gasto en ads.

## Reglas prácticas

1. Diseña primero para motivación intrínseca (competencia/autonomía/relación); usa recompensas extrínsecas solo como arranque del hábito, no como el hábito.
2. Variable ratio para ritmo y emoción del loop: SÍ ligado a tiempo de juego, NUNCA ligado a dinero real sin odds transparentes.
3. Nunca reduzcas recompensas ya establecidas de golpe (contraste conductual); cambia gradual y mantén varias fuentes de premio activas.
4. Cero contingencias negativas: no castigues no conectarse.
5. Test ético de cada compra: ¿la haría el jugador informado y en frío? Si depende de confusión, impulso o dolor fabricado, elimínala.
6. Precio en dinero real visible o calculable trivialmente; nada de ratios raros de moneda premium.
7. Diagnostica retención en orden: D1 = onboarding, D7 = core loop, D30 = metajuego. No parchees D30 con D1 roto.
8. Primera sesión: valor jugable en <60 segundos, un concepto nuevo por vez, cero muros de texto [ver: ux-ui-onboarding].
9. Elige 2-3 session hooks (daily+quests+evento o social), no los ocho a la vez; protege los streaks con un "perdón" ocasional.
10. Toda muerte/derrota debe ser explicable por el jugador como "fue mi culpa" y el reintento debe llegar en segundos.
11. Ofrece dificultad granular opt-in (estilo Assist Mode de Celeste: velocidad, ayudas puntuales) en vez de solo easy/normal/hard.
12. Ads: rewarded opt-in integrada al loop; interstitial jamás en pantallas de recompensa ni en la primera sesión; banner casi nunca.
13. Monetiza expresión, contenido, conveniencia o apoyo; nunca poder en PvP ni alivio de un grind que tú mismo inflaste.
14. Battle pass solo si tienes engagement por sesiones y live-ops sostenible; que complemente la economía, no que la sustituya (lección Clash Royale vs Clash of Clans).
15. Verifica LTV > CPI (CPI ≤ 30-70% del LTV) antes de gastar $1 en adquisición.
16. Steam: página arriba YA, capsule profesional, tráiler que abre con gameplay; 7K wishlists es el piso histórico de Popular Upcoming, no la meta segura — verifica el umbral vigente (sección 7).
17. Elige género conociendo su tasa de éxito y su CPI: es una decisión de negocio, no solo creativa.
18. Guarda tu Next Fest para cuando la demo esté pulida; solo hay una bala.
19. Instrumenta analytics (retención por cohorte, funnel de onboarding, eventos de economía) ANTES del soft launch — sin datos por cohorte no puedes diagnosticar nada de este archivo.
20. Compensa toda reducción de recompensas con una adición equivalente y comunícala; el silencio + nerf es la receta del review bombing.

## Errores comunes

| Error | Antídoto |
|---|---|
| Confundir engagement con diversión: retención alta por FOMO/timers con jugadores que odian el juego | Mide sentimiento (reviews, encuesta churn) además de métricas; el engagement resentido explota tarde o temprano |
| Añadir "sistemas de retención" sobre un core loop aburrido | Arregla el loop primero [ver: fundamentos-diseno]; la retención se construye, no se atornilla |
| Copiar la monetización de un juego gigante (gacha, pase, tienda rotativa) sin su volumen ni live-ops | Calibra el modelo a tu escala: premium o híbrido simple para equipos de 1-5 |
| Recompensar tanto el login que jugar se vuelve trabajo | Menos capas extrínsecas; que el premio gordo sea jugar mejor, no asistir |
| Nerfear drop rates o economía en vivo "porque los números lo piden" | Contraste conductual: compensa por otro lado y comunica; la confianza monetaria no se recupera |
| Dificultad como rampa lineal sin valles | Sierra: pico → consolidación → pico; picos de churn = revisar ese muro, no todo el juego |
| Culpar al jugador del rage-quit ("git gud") | Audita legibilidad: ¿la muerte fue explicable? ¿el castigo proporcional? ¿el retry inmediato? |
| Interstitials desde el minuto 1 para "monetizar temprano" | Primera sesión limpia; las ads llegan cuando ya hay hábito, y opt-in primero |
| Lanzar la página de Steam 1 mes antes del launch "cuando esté perfecta" | La página va arriba meses/años antes; las wishlists se acumulan y no caducan |
| Medir el éxito del launch en ventas del día 1 | Primera semana ≈ 15-25% de las wishlists; el resto es cola larga + rebajas + reviews |
| Proyectar LTV optimista para justificar UA | Usa ARPDAU y retención MEDIDOS en soft launch; sin margen LTV/CPI real, no se escala |
| Tratar el battle pass como ingreso extra gratis | Modela canibalización antes de introducirlo |
| Elegir F2P para un juego single-player narrativo "porque F2P factura más" | El modelo sigue al género y al engagement, no al revés: sin sesiones recurrentes no hay nada que monetizar en continuo |
| Compararte contra benchmarks sin verificar la definición (rolling vs clásica, pool con UA vs orgánico) | Confirma metodología antes de concluir que vas bien o mal |
| Precio premium de risa "para vender más copias" | El volumen no compensa; sin margen de rebaja pierdes el motor de la cola larga de Steam |

## Fuentes

- **The Motivational Pull of Video Games: A Self-Determination Theory Approach** — Ryan, Rigby & Przybylski (Motivation & Emotion, 2006) — el estudio canon que valida SDT/PENS en juegos: autonomía, competencia y relación predicen disfrute y retención.
- **Behavioral Game Design** — John Hopson (Gamasutra/Game Developer, 2001) — el texto canon de calendarios de recompensa aplicados a juegos, incluidas sus advertencias (extinción, contraste conductual).
- **Hooked / "How to Manufacture Desire"** — Nir Eyal (nirandfar.com) — el modelo trigger→acción→recompensa variable→inversión del diseño de hábito, con su advertencia ética.
- **2025 Mobile Gaming Benchmarks** — GameAnalytics (vía Game Dev Reports) — benchmarks reales de D1/D7/D28, sesiones y playtime sobre ~11.600 juegos; la fuente de los rangos de retención citados.
- **Mobile Game Marketing Benchmarks 2025** — Admiral Media — CPI por género/plataforma, CTR e IPM por canal, ROAS por cohorte.
- **ARPDAU/CPI por género (2025-2026)** — Juego Studio, The Game Marketer, FoxData, Appodeal Casual Benchmarks — rangos de ARPDAU, ARPU lifetime y CPI usados en la tabla de métricas.
- **Battle Passes — Everything You Ought to Know and Then Some** — Deconstructor of Fun (2022) — anatomía completa del battle pass: psicología FOMO, estructura, canibalización (caso Clash Royale), variantes (Halo Infinite, MTGA).
- **Clash of Clans: Bigger, Better, Battle Pass** — Eino Joas, GDC 2020 — cómo Supercell integró el Gold Pass expandiendo la economía en vez de canibalizarla.
- **The Mechanics and Ethics of Free-to-Play in Path of Exile** — Game Developer — la filosofía de GGG: monetización "divorciada a propósito" de las mecánicas; citas de Chris Wilson.
- **FTC v. Epic Games (2022) + literatura legal sobre dark patterns** — FTC; Colorado Law Review "Techlash, Loot Boxes, and Regulating Dark Patterns"; policyreview.info — la multa de $520M, grinding como dark pattern, estado regulatorio de loot boxes (Bélgica).
- **Dungeon Keeper (2014)** — Wikipedia/registro de prensa — el postmortem público del desastre de monetización de EA móvil, con las admisiones de Wilson y Gibeau.
- **The Art of Failure** — Jesper Juul (MIT Press, 2013) — la paradoja del fracaso y los tres tipos de metas; base teórica de la sección de dificultad.
- **Celeste: Assist Mode** — declaraciones de Maddy Thorson (Wikipedia, Vice) — el caso de referencia de dificultad granular opt-in sin traicionar la identidad del juego.
- **Datos de ads y churn** — PocketGamer.biz (ad quality y churn), MAF, AppLixir, Adjust, estudio Deloitte/Google AdMob — rewarded vs interstitial: los números de retención y abandono citados (ojo: varias de estas fuentes son redes de ads; la dirección del efecto es consistente entre ellas).
- **Churn y onboarding** — 80.lv "How to Solve Player Drop-Off", Mistplay, análisis de İsmet Şükrü Ataman — razones medidas de abandono en primeras sesiones (sobrecarga cognitiva, caso del menú de 12 iconos).
- **How Many Wishlists Do You Need to Launch / guías de Chris Zukowski** — presskit.gg (sintetizando datos de Zukowski y Simon Carless/GameDiscoverCo) y Game World Observer — umbrales de wishlists, conversión wishlist→venta, tiers de revenue, reglas de la página de Steam.
- **howtomarketagame.com — "How Many Wishlists Should I Have When I Launch My Game?"** — Chris Zukowski (verificado en vivo, artículo con actualización jun-2026) — los umbrales de Popular Upcoming vigentes citados en este archivo; el dato clave es que el algoritmo de Valve se mueve, así que re-verifica el número antes de fijar una meta.
- **Estadísticas de concentración de gasto ("whales")** — Tapjoy vía Adweek y fuentes secundarias equivalentes — la cifra de "~5% de pagadores = 65-70% del ingreso" citada en sección 6; NO VERIFICADO con fuente primaria, tratado como orden de magnitud.
