# Monetización móvil avanzada

> **Cuando cargar este archivo:** al diseñar la economía F2P de un juego móvil (monedas blanda/dura, sinks), montar la tienda de IAP y sus packs/ofertas, colocar ads y elegir mediación (LevelPlay/AppLovin MAX), decidir battle pass o suscripción, modelar el gasto de whales, o calcular y optimizar ARPDAU/ARPPU/LTV en un juego móvil real con Unity 6. La TEORÍA de negocio/psicología (modelos, dark patterns, battle pass, whale ethics, rangos ARPDAU/LTV/CPI) está en [ver: gamedev/psicologia-retencion-negocio] y no se repite aquí. El CÓMO técnico en Unity (WalletService, Unity IAP 5.x, LevelPlay, analytics) está en [ver: pipeline/sistemas-meta]. Los requisitos de tienda/privacidad (ATT, odds, restore, Data Safety) en [ver: release-movil] y [ver: pipeline/publicacion-tiendas]. Este archivo es el ángulo **operativo móvil** de la monetización: cómo se construye, con qué números.

**Estado y honestidad de datos (2026-07-20):** los números de plataforma (fees, versiones de paquete) están verificados contra docs oficiales; caducan, re-verificar antes de decisiones de dinero. Los benchmarks de mercado (conversión, eCPM, retención de suscripción) llevan fuente y año inline; los que no se pudieron verificar con fuente primaria van marcados **"orientativo, verificar"**. Prohibido tratar un rango orientativo como dato duro.

---

## 1. Economía F2P: el motor de dos monedas

La teoría de sources/sinks, "una moneda por loop", pity y loot tables está en [ver: gamedev/mecanicas-sistemas]; su cableado en Unity (ScriptableObjects + WalletService con `reason`/`source` por transacción) en [ver: pipeline/sistemas-meta]. Aquí, la **estructura de economía dual** que hace vivible un F2P móvil:

| Moneda / recurso | Rol | Se gana con (source) | Se gasta en (sink) | ¿IAP? |
|---|---|---|---|---|
| **Blanda (soft)** | Motor del loop diario; abundante | Jugar (recompensas de nivel, dailies, idle) | Upgrades incrementales, consumibles, entradas | No (casi nunca) |
| **Dura (hard/premium)** | Moneda-puente al dinero real; escasa | Goteo mínimo gratis (logros, primera vez) + **compra** | Skips de timer, gacha/pulls, cosméticos premium, slots | **Sí** (es el producto IAP núcleo) |
| **Energía / vidas** | Regula el ritmo de sesión (appointment) | Regeneración por tiempo (1 cada N min) | Jugar niveles; el sink que vende el skip | Refill por hard currency |
| **Materiales / fichas de evento** | Sinks de progresión profunda y de live-ops | Drops, eventos, conversión de blanda | Craft, ascensión, canje de evento | Indirecto (packs) |

**Reglas de economía dual (lo que sostiene o hunde un F2P):**
- La **blanda** debe fluir; su escasez frustra sin monetizar. La **dura** debe ser escasa y deseada; su abundancia gratis mata el IAP. Nunca dejes comprar directamente ventaja de loop con blanda que también se gana jugando: se convierte en grind-para-pagar-skip (dark pattern FTC — [ver: gamedev/psicologia-retencion-negocio]).
- **El problema de toda economía F2P madura es la inflación**: a los meses, los veteranos y whales acumulan blanda/dura sin sink que la absorba, y el juego se vuelve trivial para ellos. Necesitas **sinks permanentes que escalen** (colección infinita, niveles de mejora sin techo, cosméticos rotativos, prestige) — no solo sinks de una vez.
- Taxonomía de sinks por lo que venden éticamente ([ver: gamedev/psicologia-retencion-negocio] para la línea): **expresión** (cosméticos), **profundidad** (mejoras, colección), **conveniencia** (slots, auto), **contenido** (packs de nivel). Evita el sink que vende **alivio de un dolor fabricado** (timer que tú inflaste) o **poder en PvP**.
- Instrumenta `currency_gained`/`currency_spent` con `source`/`reason` desde el día 1 ([ver: pipeline/sistemas-meta]); sin eso, no puedes ver qué source infla ni qué sink está muerto. Ratio faucet/sink por moneda es la métrica de salud económica.
- Gacha/cajas: pity (garantía a N pulls) + **odds publicadas** (requisito Apple/Google, no opcional — [ver: release-movil]).

---

## 2. IAP: catálogo, tienda y el primer pago

Tipos y API (Unity IAP 5.4.x: `ProductType.Consumable`/`NonConsumable`/`Subscription`, precios localizados de `OnProductsFetched`, restore, grant idempotente): [ver: pipeline/sistemas-meta]. Aquí el **diseño de la oferta**.

**Adopción de IAP por género (Unity, vía Udonis — año no especificado en fuente, orientativo):** RPG 88% · Estrategia 79% · Aventura 77% · Casual 71%. **79% de los juegos móviles monetizan con IAP** (Business of Apps vía Udonis). El IAP es **~95% del gasto total del usuario** en móvil (TechCrunch, 2025) — los ads llegan a más gente pero el dinero grande es IAP.

### La escalera de precios (price ladder) y precios psicológicos
Tiers típicos observados en tiendas (Apple/Google usan price points fijos; el diseño elige cuáles ofrecer):

| Tramo | Precio típico | Rol en la tienda |
|---|---|---|
| Entrada | $0.99 – $2.99 | Primer pago, quita-fricción, starter pack |
| Medio | $4.99 – $9.99 | El caballo de batalla; suele llevar tag "Más popular" |
| Alto | $19.99 – $49.99 | Ancla de valor; "Mejor valor" con bonus % mayor |
| Whale | $99.99 (+) | Ancla superior: hace que $19.99 parezca razonable |

- **Anclaje**: el pack de $99.99 casi no se vende, pero su función es que el de $19.99 se lea como sensato. Nunca ofrezcas solo packs baratos: sin ancla alta, el techo de ARPPU se autolimita.
- **Escalado de bonus**: el mismo pack da más "gemas por dólar" cuanto más grande (ej. +0% a $0.99 → +100-150% a $99.99). Empuja al ticket alto sin subir el precio unitario percibido.
- **Framing de valor, no de moneda**: muestra "500 gemas +40% extra" con el precio en dinero real localizado visible; prohibido ofuscar el precio con ratios raros (dark pattern — [ver: gamedev/psicologia-retencion-negocio]).

### El primer pago: la conversión más cara
- **~1-5% de los jugadores paga alguna vez.** Concreto: conversión IAP diaria mediana **1.5% en RPG/Estrategia**, **>0.5% se considera bueno** en otros géneros (GameAnalytics vía Udonis); **97.7% de los jugadores de Candy Crush nunca paga** (Udonis) → ~2.3% pagadores.
- **Cuesta ~$35.42 convertir un primer pago** por medios pagados (Liftoff vía Udonis, año no especificado — orientativo). Traducción: el primer pago es carísimo de comprar, así que **diséñalo para que ocurra orgánico y temprano**.
- **Starter pack**: oferta de una sola vez, precio de entrada ($0.99-$4.99), valor percibido desproporcionado (el "mejor deal que verá"), aparece D0-D3 o tras el primer momento de fricción. Su objetivo NO es facturar, es **romper la barrera psicológica del primer pago** — quien paga una vez, repite.
- Tras el primer pago, la tienda debe tener el siguiente escalón listo (repeat-purchase); el LTV del pagador se construye en compras 2..N, no en la primera.

### Packs y ofertas
| Producto | Precio | Cuándo aparece | Propósito |
|---|---|---|---|
| **Starter pack** | $0.99-$4.99 | Una vez, D0-D3 | Primer pago |
| **Pack de moneda** | escalera $0.99-$99.99 | Siempre en tienda | Motor de ARPPU |
| **Bundle temático** | $4.99-$19.99 | Evento/temporada | Ticket medio, urgencia real |
| **Oferta segmentada** | variable | Por estado del jugador | Ofrecer lo que ESE jugador necesita |
| **"Quitar ads"** | $2.99-$5.99 (no consumible) | Tras ver N ads | Convierte al que odia ads (puente híbrido, §8) |

- **Oferta por estado/segmento**: al no-pagador, el starter; al que falló 3 veces un nivel, un pack de ayuda; al whale, el bundle grande. La segmentación se sirve con Remote Config ([ver: pipeline/publicacion-tiendas]) sin pasar por review.
- **Urgencia honesta**: countdown real que expira de verdad. Countdown falso/perpetuo = dark pattern.

---

## 3. Ads: formatos, colocación y mediación

Datos de churn por formato y la regla "rewarded suma, interstitial es impuesto en churn" están en [ver: gamedev/psicologia-retencion-negocio]; la API de LevelPlay (`LevelPlayRewardedAd`, `LoadAd/ShowAd/IsAdReady`, estado no-fill) en [ver: pipeline/sistemas-meta]. Aquí: **eCPM real, catálogo de colocaciones y mediación**.

| Formato | eCPM (orientativo) | Dónde va | Costo UX |
|---|---|---|---|
| **Rewarded video** (opt-in) | **$10-50** (ironSource vía Udonis) | Integrado al loop (revivir, doblar, spin) | Bajo — 68% lo prefiere (TechCrunch); 82% de devs lo usa (DeltaDNA) |
| **Interstitial** (forzado) | **$4-6** (ironSource vía Udonis) | Entre sesiones/niveles, con cap | Alto — paga su eCPM en churn |
| **Banner** | Bajo (centavos) | Pantallas no-core | Contamina UI por poco |
| **Native / offerwall / playable** | Nicho, variable | Tienda/offerwall opt-in | Solo con audiencia que lo espera |

**eCPM por región (orientativo, verificar con red/mediación real):** tier-1 (US, UK, CA, AU, países nórdicos) paga múltiplos de tier-3 (India, Brasil, SEA, LATAM). El eCPM de US suele ser el más alto del pool; la misma impresión rewarded puede valer $30+ en US y <$3 en un tier-3. Esto **decide tu estrategia de UA**: comprar instalaciones en tier-1 caras contra LTV alto, o volumen barato en tier-3 con ads como monetización principal. Verifica con tu dashboard de mediación por país, no de memoria.

**Catálogo de colocaciones rewarded (el dinero sano):** revivir tras morir · doblar la recompensa de fin de nivel · spin/pull gratis diario · acelerar un timer una vez · abrir cofre extra · moneda blanda por ad (goteo pequeño). Cada una debe ofrecer valor **pequeño y opt-in** (si el ad da tanta hard currency como un IAP, canibaliza el IAP — §8).

**Reglas de colocación:**
- **Cero ads en la primera sesión** y en los primeros minutos: mata D1 antes de que exista hábito.
- Interstitial **nunca sobre pantallas de recompensa** (triplica el quit rate — [ver: gamedev/psicologia-retencion-negocio]) y con **frequency cap** (ej. 1 cada 2-3 min o cada N niveles) + **cooldown post-sesión-inicial**.
- Gate por profundidad de sesión: el jugador debe "ganarse" el juego antes de ver el primer interstitial.
- Botón rewarded con estado "no disponible" (gris + reintento) cuando `IsAdReady()` es false — nunca botón muerto ([ver: pipeline/sistemas-meta]).

**Mediación (LevelPlay vs AppLovin MAX):** ambas subastan cada impresión entre varias redes (Unity Ads, AppLovin, AdMob, Meta, ironSource…) y sirven la que más paga — **más eCPM que una red sola** a cambio de configurar adapters. LevelPlay (`com.unity.services.levelplay` 9.5.0, integrado en Unity — [ver: pipeline/sistemas-meta]) es el default nativo de Unity 6; AppLovin MAX es el competidor dominante. Prefiere **in-app bidding** sobre waterfall clásico: la subasta en tiempo real saca más eCPM que el orden manual de pisos. Redes líderes 2022 (AppsFlyer vía Udonis): AppLovin, Unity Ads, Meta, TikTok, Google, ironSource.

**ATT/privacidad:** en iOS, denegar el prompt ATT deja el IDFA en ceros → ads siguen pero **sin personalizar, con eCPM menor**; prohibido bloquear el juego o incentivar el permiso ([ver: release-movil], [ver: pipeline/publicacion-tiendas]). El eCPM iOS post-ATT es materialmente más bajo que pre-2021 para tráfico no consentido.

---

## 4. Battle pass y suscripciones móviles

### Battle pass (móvil)
La psicología (FOMO en 3 capas), la estructura free/premium track, las tres filosofías de pacing y la canibalización (caso Clash Royale vs Clash of Clans) están en [ver: gamedev/psicologia-retencion-negocio]. Especificidad móvil:

- **Temporadas cortas (~1 mes)** mantienen el atractivo alto cerca del inicio; el móvil rota más rápido que consola (8-12 semanas).
- **Precio $5-10** (tier medio de IAP); free track visible que muestra lo que el jugador se "pierde".
- **Pase que se paga solo** (currency-back): el premium track devuelve suficiente hard currency para comprar el siguiente pase → el jugador se auto-suscribe sin cobro recurrente. Es el truco de retención de pase más potente en móvil.
- Misiones diarias/semanales que empujan **exploración horizontal** (probar modos/personajes = retención — [ver: retencion-liveops]).
- El pase **retiene mejor de lo que convierte**, y casi todo su ingreso es la compra inicial (ARPPU limitado). Modela la canibalización de otras compras ANTES de introducirlo; que **acompañe** una expansión de economía, no que la sustituya.

### Suscripciones móviles
| Tipo | Qué ofrece | Modelo de referencia |
|---|---|---|
| **Quitar ads** | No consumible o sub barata | Puente híbrido (§8) para el que odia ads |
| **VIP / club** | Goteo diario de hard currency + perks (más energía, drops, cosmético exclusivo) | Fortnite Crew (moneda mensual + pase + skin) |
| **Battle pass como sub** | Auto-renueva el pase cada temporada | Menos fricción, más churn si el valor baja |

**Benchmarks de suscripción (RevenueCat, State of Subscription Apps 2025):**
- **Gaming usa 78% planes semanales** (vs. anual dominante en otras categorías) — el jugador compra impulso corto, no compromiso anual.
- **96.3% de los trials de gaming duran ≤4 días.**
- Install→paid mediana **1.9% a día 35** (all-apps); **hard paywall 12.11% vs freemium 2.18%**.
- **82% de los trials arrancan el mismo día de instalar** (day 0); trial→paid mediana **45.7%** (trials de 17-32 días).
- Churn del **~30% en el primer mes** para anuales; **retención año 1: anual 44.1%, mensual 17.0%, semanal 3.4%.**
- **ARPU D14 de gaming: $0.08** (el más bajo de todas las categorías) — la suscripción de juego pura casi no factura sin el resto de la economía.
- Refund rate mayor en hard paywall (5.8%) que freemium (3.4%).

**Cuándo usar suscripción:** solo si entregas **valor recurrente constante** (contenido/moneda/perks cada día); si el valor baja, el churn semanal de gaming (semanal año-1 3.4%) te vacía. Para un dev pequeño, la sub viable es **VIP/quitar-ads como add-on** de un F2P que ya funciona, no una sub propia de plataforma ([ver: gamedev/psicologia-retencion-negocio]). Trial + periodo de gracia (grace period recupera pagos fallidos) son obligados; sin grace, pierdes suscriptores por tarjeta caducada, no por decisión.

---

## 5. Whales y la distribución de gasto

**El modelo real:** minnows / dolphins / whales. La mayoría del ingreso IAP viene de una fracción pequeña de pagadores. Datos: **97.7% de Candy Crush nunca paga** (Udonis) → el negocio vive del ~2%; **whales gastan ~$20 de media por compra** (DeltaDNA vía Udonis, orientativo). La cifra ampliamente citada de "~5% de pagadores = 65-70% del ingreso" (Tapjoy) está marcada **NO VERIFICADO** en [ver: gamedev/psicologia-retencion-negocio]; trátala como orden de magnitud, no dato duro.

**Ojo con no conflar métricas:** "**42% de la población de gamers son pagadores**" (Newzoo 2025, vía Udonis) mide *share global de gamers que gastan algo en cualquier plataforma/vida* — NO es la conversión F2P diaria (1-5%). Son cosas distintas; usar la de Newzoo para proyectar un F2P móvil es un error de comparación.

**Diseño que respeta al whale sin volverse predatorio:**
- Vende al whale **profundidad, colección, prestigio, expresión y conveniencia** — nunca **poder en PvP** (convierte el matchmaking en subasta) ni **alivio de dolor fabricado**.
- Dale techo de gasto significativo (colección infinita, cosméticos rotativos, leaderboards de vanidad) para que su dinero tenga dónde ir sin romper el balance de los free.
- **La fragilidad es de negocio y ética a la vez**: si tu curva vive de 5 personas gastando miles, el churn de un whale es un cráter, y estás extrayendo de gente que puede estar en pérdida de control. GGG (Path of Exile) llegó a **rechazar compras** de jugadores con señales de gasto insostenible ([ver: gamedev/psicologia-retencion-negocio]). Un F2P sano tiene base ancha de pagadores + whales, no solo whales.

---

## 6. La línea ética móvil y la regulación (2026)

La tabla general de dark patterns, la multa FTC a Epic ($520M, $245M por dark patterns de compra) y el test honesto ("¿lo haría el jugador informado y en frío?") están en [ver: gamedev/psicologia-retencion-negocio]. Aquí, lo **específico de móvil**:

| Dark pattern móvil (evitar) | Por qué |
|---|---|
| Timer de horas en el corazón del loop + vender el skip | Caso Dungeon Keeper (EA): el juego se vuelve la tienda; regulador UK intervino |
| Countdown falso/perpetuo en ofertas | Compra por pánico, no por valor |
| Bundle con moneda en ratios que ofuscan el precio real | Ofusca el dinero; escrutinio regulatorio |
| Ad mal colocado que se toca por error (misclick) | Ingreso por engaño; daña reputación y viola políticas de red |
| Sub difícil de cancelar / trial-a-pago oculto | "Subscription trap"; FTC y app stores endurecen |
| Loot box de pago con odds ocultas | Ilegal/prohibido en varios países; **odds obligatorias en Apple y Google** |
| Presión de gasto sobre menores | Foco regulatorio duro (FTC, China, EU) |

**Regulación móvil vigente (verificar antes de decisiones — cambia rápido):**
- **Apple y Google exigen publicar las odds** de cualquier mecánica aleatoria de pago (loot box) ANTES de comprar; sin eso = rechazo/removal ([ver: release-movil], [ver: pipeline/publicacion-tiendas]).
- **Bélgica** prohíbe de facto loot boxes pagadas con dinero real (2018, tratadas como apuesta).
- **China**: licencia de publicación (ISBN) obligatoria + odds publicadas + límites de gasto/tiempo para menores (verificar el marco vigente si publicas allí).
- **UE (DSA / derecho de consumo)** y **UK (ASA)** vigilan FOMO agresivo, precios engañosos y ofertas a menores.
- La FTC clasificó el **grinding deliberado** (hacer la versión gratis tan tediosa que induce a pagar) como dark pattern.

---

## 7. Métricas de monetización móvil y cómo optimizarlas

Definiciones y rangos base (ARPDAU por género, LTV, la ecuación **LTV > CPI con margen**, retención clásica vs rolling) en [ver: gamedev/psicologia-retencion-negocio §6] y el mercado/CPI móvil en [ver: mercado-movil]. Aquí, **cómo se mueven sin romper el juego**.

| Métrica | Definición | Palanca para subirla (sin romper) |
|---|---|---|
| **ARPDAU** | (ingreso IAP + ingreso ads) / DAU | El unificador del híbrido (§8); sube con mejor placement de rewarded y ofertas segmentadas, NO metiendo interstitials |
| **ARPPU** | Ingreso por usuario **pagador** | Ancla alta de precio, packs escalados, repeat-purchase, VIP/whale bundles |
| **Conversión a pagador** | % que paga alguna vez | Starter pack temprano + first-purchase funnel; onboarding que llega al valor antes de pedir dinero |
| **LTV** | ≈ ARPDAU × días de vida esperados | **Retención mueve LTV más que exprimir ARPDAU**; subir D7 vale más que un interstitial extra |
| **ARPPU de whale** | Gasto medio del top de pagadores | Profundidad/colección/prestigio; techo de gasto sano |

**Cómo optimizar sin romper:**
- **ARPDAU es vanidad sin retención: LTV = monetización × permanencia.** Un interstitial extra sube ARPDAU hoy y hunde D7 mañana → LTV neto baja. Optimiza la ecuación completa, no el número del día.
- **Segmenta**: no-pagador → starter + ads; pagador → bundles + menos ads; whale → VIP + productos de profundidad. Servido por Remote Config, cambiable sin review ([ver: pipeline/publicacion-tiendas]).
- **A/B por Remote Config**: precio, contenido de pack, frecuencia de ads, momento de la oferta. Mide contra **retención + LTV por cohorte**, no contra ARPDAU aislado.
- **Instrumenta ANTES del soft launch** (funnel FTUE, level start/complete/fail, currency gained/spent con source, IAP, rewarded visto por placement — [ver: pipeline/sistemas-meta]); sin datos por cohorte no puedes optimizar nada de esta tabla.

---

## 8. El modelo híbrido (dominante en 2026)

El estándar móvil actual es **hybrid-casual / híbrido**: IAP **y** ads en el mismo juego, cada uno monetizando a una audiencia distinta.

- **Los ads monetizan al ~95-98% que no paga** (llegan al 100% de usuarios); **el IAP monetiza al 1-5% que paga** y es **~95% del gasto total** (TechCrunch 2025). ARPDAU máximo = sumar ambos, no elegir uno.
- **Preferencia del jugador:** 82% prefiere juego gratis con ads sobre juego de pago sin ads (eMarketer vía Udonis); 74% vería video ad por recompensa (eMarketer).
- **La tensión IAP↔ads (canibalización):** quien mira un ad rewarded por gemas no compra ese pack de gemas. Solución de diseño:
  - **Rewarded da poco, IAP da mucho** (el ad nunca sustituye al pack).
  - **"Quitar ads" como producto de pagador** (§2): el que paga deja de ver ads → no le canibalizas el IAP, y monetizas al que los odia.
  - **Los whales ven menos/ningún ad** (VIP incluye quitar ads): su LTV vive del IAP, no lo diluyas con centavos de ad.
- **Diseña las dos audiencias explícitamente:** el pagador con una economía de IAP profunda (escalera de packs, battle pass, VIP); el no-pagador con inventario de ads sano (rewarded integrado) + un starter pack barato que ocasionalmente lo convierte.
- **Net revenue = gross × (1 − fee de tienda).** Fees verificados (2026-07-20, re-verificar — Google cambia su modelo el 30-jun-2026): **Apple** 30% estándar, **15%** en Small Business Program (<$1M proceeds/año) y en suscripciones tras el año 1; **Google Play** 15% sobre el primer $1M/año y 30% por encima (mercados aún en modelo viejo), **15% en suscripciones**; nuevo modelo Google en EEA/UK/US desde 30-jun-2026 = 10% + 5% billing fee para new installs. Modela el **~15-30%** que te quita la tienda al fijar precios y proyectar LTV.

---

## Reglas prácticas

1. Economía dual: blanda fluye (motor del loop), dura escasea (puente al dinero). Nunca dejes comprar ventaja de loop con blanda ganable jugando.
2. Diseña sinks permanentes que escalen (colección, prestige, cosméticos rotativos): toda economía F2P madura se infla si no.
3. Instrumenta `currency_gained`/`currency_spent` con `source`/`reason` antes del soft launch; audita el ratio faucet/sink por moneda.
4. Escalera de precios con ancla alta ($99.99) aunque casi no se venda: sin ancla, el ARPPU se autolimita; bonus % mayor en packs grandes.
5. Precio en dinero real localizado y visible; jamás ofuscarlo con ratios raros de moneda premium.
6. Starter pack de una vez, barato, valor desproporcionado, D0-D3: su meta es romper el primer pago (cuesta ~$35 comprarlo por UA), no facturar.
7. Ten listo el escalón de compra 2..N: el LTV del pagador se construye en las compras repetidas, no en la primera.
8. Rewarded opt-in integrada al loop, valor pequeño; interstitial nunca en primera sesión ni sobre recompensas, con frequency cap; banner casi nunca.
9. Rewarded da poco, IAP da mucho: si el ad iguala al pack, cierras tu propio IAP.
10. Mediación con in-app bidding (LevelPlay 9.5 o AppLovin MAX); mide eCPM por país (tier-1 ≫ tier-3) para decidir UX y UA.
11. Botón rewarded con estado "no disponible", nunca botón muerto.
12. Battle pass solo con engagement por sesiones + live-ops sostenible; temporada corta (~1 mes), $5-10, currency-back para auto-suscripción; que acompañe la economía, no que la sustituya.
13. Suscripción solo si entregas valor recurrente constante; en gaming domina el plan semanal y el trial ≤4 días; sin grace period pierdes suscriptores por tarjeta, no por decisión.
14. Vende a whales profundidad/expresión/prestigio, nunca poder PvP; dales techo de gasto sano; no construyas el negocio sobre 5 personas.
15. Loot boxes de pago → odds publicadas antes de comprar (requisito Apple/Google); countdown honesto; nada de subs difíciles de cancelar.
16. Optimiza LTV = ARPDAU × retención, no ARPDAU del día; un interstitial extra que hunde D7 baja el LTV neto.
17. Segmenta ofertas (no-pagador/pagador/whale) y "quitar ads" como producto de pagador; sírvelas con Remote Config sin pasar por review.
18. Modela el fee de tienda (~15-30%) al fijar precios; re-verifica los tramos (Apple SBP, Google cambia su modelo 30-jun-2026).
19. No confundas "% de gamers que pagan" (Newzoo ~42%, cross-plataforma) con la conversión F2P móvil (1-5%).
20. Verifica LTV > CPI con margen (CPI ≤ 30-70% del LTV) en soft launch antes de escalar UA ([ver: mercado-movil]).

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Dar hard currency gratis con generosidad "para que enganche" | Mata el IAP núcleo: goteo mínimo gratis, el grueso se compra o se gana con esfuerzo real |
| Tienda solo de packs baratos, sin ancla alta | ARPPU con techo bajo; añade ancla $99.99 y bonus escalado aunque casi no se venda |
| Perseguir el primer pago con presión en vez de valor | Starter pack barato de valor desproporcionado, temprano y opt-in; el pago llega por deal, no por pánico |
| Rewarded que regala tanta moneda como un pack de IAP | Canibaliza tu propio IAP; rewarded da poco, IAP da mucho |
| Interstitials desde el minuto 1 "para monetizar ya" | Cero ads en la primera sesión; el churn medido se come el eCPM ([ver: gamedev/psicologia-retencion-negocio]) |
| Subir ARPDAU metiendo ads y celebrar el número | LTV = ARPDAU × retención; si D7 cae, el LTV neto baja — mide por cohorte |
| Suscripción propia esperando ingreso estable en un juego pequeño | En gaming la sub semanal churnea rápido (año-1 ~3.4%); usa VIP/quitar-ads como add-on de un F2P que ya funciona |
| Battle pass como "ingreso extra gratis" | Casi todo su ingreso es la compra inicial y canibaliza otras compras; modela la canibalización (Clash Royale) antes |
| Economía sin sinks permanentes | A los meses los veteranos/whales inflan y trivializan el juego; sinks que escalan (colección, prestige) |
| Negocio dependiente de un puñado de whales | Cráter al primer churn + riesgo ético; base ancha de pagadores + whales, y techo de gasto sano |
| Loot box de pago sin odds publicadas | Rechazo/removal en Apple y Google; publica odds + pity antes del submit ([ver: release-movil]) |
| Confundir "% de gamers que pagan" con conversión F2P | Newzoo mide cross-plataforma/vida (~42%); la conversión F2P diaria es 1-5% |
| Proyectar LTV sin restar el fee de tienda | Net = gross × (1 − 15..30%); modela el fee real de tu tramo antes de fijar precio y UA |
| A/B de precio/ads midiendo solo ARPDAU | Mide contra retención + LTV por cohorte; el ARPDAU aislado engaña |

## Fuentes

- **In App Purchasing 5.4 / LevelPlay 9.5 — docs oficiales Unity** (docs.unity3d.com, docs.unity.com/grow) — vía [ver: pipeline/sistemas-meta]: tipos de IAP, precios localizados, restore/grant idempotente, clases y eventos de LevelPlay, in-app bidding. La base técnica que este archivo diseña por encima.
- **State of Subscription Apps 2025 — RevenueCat** (revenuecat.com) — benchmarks de suscripción verificados: install→paid día 35 (1.9%; hard paywall 12.11% vs freemium 2.18%), trial→paid 45.7%, gaming 78% semanal y 96.3% trials ≤4 días, churn mes-1 ~30%, retención año-1 anual 44.1%/mensual 17%/semanal 3.4%, ARPU D14 gaming $0.08, refund rates.
- **App Store Small Business Program — Apple** (developer.apple.com/app-store/small-business-program) — 15% vs 30% estándar, umbral $1M USD proceeds/año, 15% suscripciones tras año 1, 10% alternative terms UE.
- **Google Play service fees — Play Console Help** (support.google.com/googleplay/android-developer/answer/112622) — 15% primer $1M/año y 30% por encima, 15% suscripciones, nuevo modelo EEA/UK/US 10%+5% billing desde 30-jun-2026, alternative billing −4%.
- **Mobile Game Monetization / In-App Purchases / eCPM — Udonis blog** (blog.udonis.co) — agregador que cita fuentes primarias: eCPM rewarded $10-50 e interstitial $4-6 (ironSource), 79% de juegos con IAP (Business of Apps), first-purchase $35.42 (Liftoff), conversión IAP 1.5% RPG y >0.5% bueno (GameAnalytics), adopción IAP por género (Unity), 97.7% Candy Crush no paga, whale ~$20/compra (DeltaDNA), 68% prefiere rewarded (TechCrunch), 82% devs rewarded (DeltaDNA). Fuente secundaria: verificar contra las primarias antes de decisiones de dinero.
- **Mobile Gaming Statistics 2026 — Udonis blog** (blog.udonis.co) — cita: 42% de gamers son pagadores y 52% Gen Alpha/Z (Newzoo 2025), IAP = 95% del gasto (TechCrunch 2025), IAP+sub +13% YoY a $150B (Sensor Tower 2024), 82% prefiere free-con-ads y 74% vería ad por recompensa (eMarketer).
- **Mobile Gaming Benchmarks 2025 / 2026 — GameAnalytics** (gameanalytics.com/reports) — reportes de retención/engagement por género/región/plataforma que alimentan los rangos base ([ver: gamedev/psicologia-retencion-negocio]); confirmar cifras exactas en el PDF del reporte vigente.
- **gamedev/psicologia-retencion-negocio.md** (base propia) — teoría de modelos de negocio, dark patterns + FTC Epic, battle pass (FOMO/canibalización), whale ethics (PoE/GGG), rangos ARPDAU/LTV/CPI, ads churn por formato: el POR QUÉ que este archivo operacionaliza para móvil.
- **pipeline/sistemas-meta.md** (base propia) — WalletService, Unity IAP 5.x, LevelPlay, notificaciones, analytics, tiempo/anti-cheat: el CÓMO técnico en Unity 6 de todo lo que aquí se diseña.
- **pipeline/publicacion-tiendas.md** (base propia) — ATT/IDFA, Data Safety, App Store Review 3.1.1 (odds/restore), Remote Config para A/B de precio/economía: los requisitos de tienda y la herramienta de segmentación referenciados.
