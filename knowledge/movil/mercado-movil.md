# El mercado móvil

> **Cuando cargar este archivo:** al decidir si un juego va a móvil (y a qué plataforma primero), al estimar si un proyecto móvil tiene negocio viable antes de invertir, al planear descubrimiento/UA/ASO, o al calibrar expectativas de ingreso para un indie o equipo pequeño en iOS/Android. Profundiza el ángulo MÓVIL de [ver: gamedev/psicologia-retencion-negocio] (retención, LTV/CPI, modelos de negocio genéricos) y [ver: gamedev/generos] (qué géneros funcionan en móvil). Para la mecánica de tienda/requisitos técnicos de publicación ver [ver: release-movil] y [ver: pipeline/publicacion-tiendas].

## Principio rector

El móvil **no es una plataforma de distribución, es un negocio de adquisición**. En Steam el motor es el descubrimiento (wishlists, algoritmo, festivales); en móvil el descubrimiento orgánico para un juego nuevo es **estadísticamente cero** y el motor es la ecuación LTV > CPI [ver: gamedev/psicologia-retencion-negocio §6]. Un juego móvil excelente sin presupuesto de UA ni featuring es un árbol que cae en un bosque vacío. La primera pregunta de un proyecto móvil no es "¿es divertido?" sino "¿cómo llega alguien a instalarlo, y monetiza más de lo que cuesta traerlo?". Si no hay respuesta, el juego va a PC/Steam [ver: gamedev/generos].

## 1. Tamaño y forma del mercado (2024-2025)

| Dato | Cifra | Fuente |
|---|---|---|
| Ingreso mundial juegos móviles 2024 | **~$92B** (+3.0% YoY) | Newzoo (vía Udonis, 2025) |
| Descargas de juegos móviles 2024 | **49.6B** (−6% YoY, en declive desde 2021) | Sensor Tower (vía Udonis, 2025) |
| Ingreso por género 2024 (top) | Strategy **$17.5B** · RPG **$16.8B** · Puzzle **$12.2B** · Casino **$11.7B** · Simulation **$6.1B** | Sensor Tower (vía Udonis, 2025) |
| Descargas por género 2024 (top) | Simulation **9.8B** · Puzzle **9.7B** · Arcade **9.6B** | Sensor Tower (vía Udonis, 2025) |
| Juegos móviles nuevos que llegaron a $1B en 2025 | **0** (ninguno) | Deconstructor of Fun, State of Mobile 2026 |

**Lo que esa tabla grita:**
- **El ingreso sube, las descargas bajan.** Más dinero repartido entre MENOS instalaciones nuevas = el mercado es cada vez más caro de entrar y más concentrado en juegos ya vivos. La "torta" crece por gasto de jugadores existentes en juegos consolidados, no por hits nuevos.
- **Los géneros que facturan (Strategy, RPG, Casino) NO son los que descargan (Sim, Puzzle, Arcade).** El dinero grande está en géneros de LiveOps profundo y whales [ver: retencion-liveops], que un indie no puede sostener. Los géneros de volumen de descarga (arcade/casual) monetizan por ads a ARPDAU bajo.
- **Cero juegos nuevos a $1B en 2025** confirma la madurez: el top está ocupado por títulos con 5-10 años de vida (Candy Crush, Clash, Monopoly Go como excepción reciente). Entrar arriba es prácticamente imposible sin capital de estudio.

## 2. iOS vs Android como mercados: quién paga

El error del dev nuevo es tratarlos como "la misma app en dos tiendas". Como **mercados** son distintos: Android tiene el volumen de usuarios, iOS tiene el dinero.

| Eje | iOS (App Store) | Android (Google Play) |
|---|---|---|
| Cuota de usuarios global | Minoría (~28-30% de smartphones mundiales) | Mayoría (~70%) |
| **Gasto de consumidor / ingreso** | **~65% del gasto en apps** pese a ~30% de descargas | ~35% del gasto pese a ~65-70% de descargas |
| ARPU relativo | **~2x el de Android** (regla histórica) | Base |
| Público que paga | EE.UU., Japón, Europa occidental, Corea | India, Brasil, SE-Asia, LatAm, mercados emergentes |
| CPI | Más caro (menos inventario, ATT encarece targeting) | Más barato |
| Piratería / sideload | Cerrado (sideload UE por DMA desde 2024, marginal) | Abierto (APK, tiendas alternativas) |

> ⚠️ Los porcentajes exactos del split de gasto (65/35) y el "~2x ARPU" son la **pauta histórica consolidada** de los State of Mobile de data.ai/Sensor Tower a lo largo de varios años; **orientativo — verificar la cifra vigente en Sensor Tower / data.ai State of Mobile 2025/2026** antes de citarla como dato duro. La *dirección* (iOS monetiza mucho más por usuario, Android tiene el volumen) es sólida y consistente año tras año.

**Implicaciones de diseño y estrategia:**
- **Premium tiene su casa en iOS.** El usuario de iPhone en tier-1 está acostumbrado a pagar; un premium de pago único de nicho de calidad tiene su mejor (y casi única) oportunidad ahí [ver: §6].
- **F2P+ads escala en Android por volumen**; el ARPU bajo se compensa con la base masiva y el CPI barato de mercados tier-2/3.
- **Priorización de plataforma:** si el modelo es premium o de alto ARPU → iOS primero. Si es ad-driven de volumen → Android primero (y probar en tier-3 barato). No es "ambas a la vez el día 1" salvo que el pipeline lo dé gratis [ver: unity/build-plataformas].
- iOS **retiene mejor** en el cuartil alto (D1 top 31-33% vs Android 25-27%, GameAnalytics 2025) [ver: gamedev/psicologia-retencion-negocio §3] — otra razón por la que el mismo juego "vale más" por usuario en iOS.

## 3. Descubrimiento y UA: por qué el orgánico casi no existe

**La diferencia estructural con Steam:** Steam te descubre por wishlists, tags, "más como esto", festivales, el discovery queue — hay superficies orgánicas donde un juego bueno *puede* aflotar. La App Store y Google Play tienen charts dominados por incumbentes y búsqueda dominada por marcas; para un título nuevo sin marca ni ads, la probabilidad de que alguien lo *encuentre* solo es cercana a cero. **El descubrimiento móvil se COMPRA.**

Las tres (y solo tres) vías reales a instalaciones:

| Vía | Qué es | Realidad para indie |
|---|---|---|
| **UA pagada** | Comprar instalaciones vía redes de ads (Apple Search Ads, Google App Campaigns, Meta, Unity/ironSource/AppLovin, TikTok) | El canal dominante. Requiere presupuesto + LTV medido. Sin esto, no hay volumen |
| **Featuring de tienda** | Que Apple/Google te destaquen editorialmente | No se compra, se gana: build pulido, uso de tech de plataforma, calidad de ficha. Impredecible; ayuda pero no es plan de negocio |
| **Orgánico / viral** | ASO + boca a boca + creadores + comunidad | El único gratis. Real solo si el juego tiene un hook viral genuino o un nicho con comunidad. La excepción, no la regla |

**CPI (cost per install) — la métrica que decide todo.** Rangos por género y plataforma (Admiral Media, Mobile Game Marketing Benchmarks 2025; cross-ref [ver: gamedev/psicologia-retencion-negocio §6]):

| Género | CPI Android | CPI iOS |
|---|---|---|
| Hyper-casual | $0.25–0.80 | $0.50–1.50 |
| Puzzle | $0.80–2 | $1.50–3.50 |
| Match-3 | $1–2.50 | $2–5 |
| Midcore RPG | $2.50–6 | $4–12 |
| Estrategia (4X) | $2–5 | $3.50–10 |
| Casino (iOS) | — | hasta ~$21 |

- **Regla:** el CPI es más alto en iOS que en Android, y más alto en tier-1 (EE.UU./UK/Japón) que en tier-2/3. Un install de EE.UU. iOS de un midcore puede costar $8-12; el mismo género en tier-3 Android puede costar centavos — pero ese usuario tier-3 también monetiza mucho menos. **No se compra el install barato, se compra el install rentable** (LTV de ESE usuario > CPI de ESE usuario).
- **El impacto de ATT (App Tracking Transparency):** desde iOS 14.5 (2021) el juego debe pedir permiso explícito para trackear entre apps; si el usuario lo niega, el IDFA se devuelve en cero (verificado en docs de Apple) [ver: unity-movil-input-servicios, release-movil]. Con la mayoría negando, el targeting y la atribución en iOS se degradaron → CPI de iOS subió y la medición se volvió probabilística (SKAdNetwork/AdAttributionKit). Consecuencia práctica: **el UA en iOS es más caro y más ciego que en 2020**; Android (Privacy Sandbox en transición) aún da más señal.

**Tiers de mercado (geografía del CPI):** el CPI y el LTV varían por región; la industria agrupa países en tiers. No es un número de negocio, es el vocabulario para leer los benchmarks:

| Tier | Países típicos | CPI | LTV | Uso |
|---|---|---|---|---|
| **Tier 1** | EE.UU., UK, Canadá, Australia, Japón, Alemania, Nórdicos | Alto | Alto | Donde está el dinero; UA caro |
| **Tier 2** | Sur/Este de Europa, Corea, parte de LatAm | Medio | Medio | Escalado intermedio |
| **Tier 3** | India, Brasil, SE-Asia, mercados emergentes | Bajo (centavos posibles) | Bajo | Volumen barato de test; monetiza por ads |

Regla: comprar tier-3 barato infla las descargas y el ego, no el ingreso. La rentabilidad se mide **por tier**: el LTV de un usuario tier-1 iOS y el de un tier-3 Android son mundos distintos, y su CPI también.

**El creativo de ads ES el producto (para casual):** en hyper/hybrid-casual, el juego se vende por su video de ad, no por su ficha — y el negocio vive de la métrica **IPM** (installs per mille, instalaciones por cada 1.000 impresiones) y del CTR del creativo, no del diseño del juego [ver: gamedev/generos]. Un publisher testea decenas de creativos y decenas de prototipos, mata casi todos, y escala el que da IPM/CTR rentable. Sin pipeline de creativos en rotación constante (fatiga de anuncio = el mismo video deja de convertir en semanas), no hay UA sostenible. Esto es un negocio de marketing de performance, no de game design — la razón por la que un indie sin publisher no puede competir en casual. Los rangos concretos de IPM/CTR por canal van con fuente en la base hermana [ver: gamedev/psicologia-retencion-negocio §6] (Admiral Media 2025).

**Por qué un indie NO puede jugar el juego de UA:** la ecuación LTV > CPI [ver: gamedev/psicologia-retencion-negocio §6] exige (a) LTV medido en soft launch, (b) capital para comprar a escala mientras se optimiza, (c) pipeline de creativos de ads en rotación constante. Sin las tres, comprar installs es quemar dinero. Para el indie sin capital, "UA" = orgánico + ASO + comunidad, y eso solo funciona con hook viral o nicho.

## 4. ASO: la ficha de tienda es tu wishlist de Steam

ASO (App Store Optimization) es el **equivalente móvil de la página de Steam** [ver: gamedev/psicologia-retencion-negocio §7]: la lógica es idéntica — comunicar el género y la promesa en 2 segundos — pero las palancas son otras. ASO hace dos trabajos: **descubribilidad** (aparecer en búsqueda/charts) y **conversión** (que quien ve la ficha instale). Para un indie sin UA, ASO ES el marketing.

**Las palancas, por orden de peso en conversión:**

| Elemento | Rol | Regla operativa |
|---|---|---|
| **Icono** | La primera y a veces única impresión; compite en una grilla diminúscula | Legible a 60px, alto contraste, UN concepto claro, distinto de los competidores del género. Es el activo #1 — págale a un artista antes que gastar en ads [analogía capsule de Steam] |
| **Primeros 1-3 screenshots** | Lo único que la mayoría ve sin hacer scroll | Deben mostrar GAMEPLAY real y la promesa del género en los primeros 2; texto overlay corto que venda el hook. Apple exige que muestren juego real, no solo splash art (guideline 2.3.3) |
| **Título + subtítulo (iOS) / título corto (Android)** | Peso alto en ranking de keywords Y en claridad | Nombre + descriptor de género/hook. iOS: subtítulo (30 car.) es prime real estate de keywords |
| **Keywords** | iOS: campo dedicado de 100 caracteres (no visible). Android: se indexa de título + descripción corta + larga | iOS: rellenar los 100 car. sin repetir ni poner el nombre de la app; Android: keywords naturales en la descripción (Google indexa el texto). Prohibido keyword-stuffing con marcas ajenas (rechazo Apple 2.3.7) |
| **Rating / reseñas** | Filtro de conversión brutal: <4.0★ hunde la instalación | Pedir review con prompt nativo (SKStoreReviewController / In-App Review de Google) DESPUÉS de un momento de éxito, nunca al abrir |
| **Vídeo (app preview / promo)** | 15-30s de gameplay; sube conversión en géneros visuales | Abre con gameplay en el primer segundo (misma regla que tráiler de Steam) |

- **A/B testing nativo (real, gratis, subutilizado):** Apple **Product Page Optimization** (hasta 3 variantes de icono/screenshots/vídeo) y Google Play **Store Listing Experiments**. Testear icono y primer screenshot es la optimización de mayor ROI que existe en móvil. *Las cifras de "uplift %" de un test de icono varían enormemente por juego; medir SIEMPRE en el A/B propio — no asumir un número prestado.*
- **Localización de la ficha** (título/screenshots/keywords) a los idiomas de tus mercados objetivo es de las palancas orgánicas más baratas y efectivas, sobre todo para descubribilidad en tiendas no-inglesas [ver: pipeline/narrativa-localizacion].
- No confundir ASO con SEO: la tienda re-indexa lento y castiga el stuffing; iterá título/keywords en ciclos, no a diario.

## 5. Premium vs F2P en móvil: por qué F2P domina

| Modelo | En móvil | Cuándo tiene sentido |
|---|---|---|
| **F2P + ads** | Monetiza al 100% de usuarios; ARPDAU bajo ($0.05–0.15 casual, cross-ref base). Depende de VOLUMEN enorme | Hyper/hybrid-casual, puzzle, arcade. Solo con UA o viralidad que dé el volumen |
| **F2P + IAP** | Techo altísimo; <5% paga; exige LiveOps y economía dual perpetuos [ver: monetizacion-movil, retencion-liveops] | Estrategia/4X, gacha/collection-RPG, match-3. Negocio de estudio, no de solo-dev |
| **Híbrido (IAP+ads)** | El **estándar móvil de 2026** ("hybrid-casual"): rewarded + IAP de conveniencia | Casual/mid-core. Único segmento casual creciendo IAP (+20%, $4.2B — Deconstructor of Fun 2026) |
| **Premium (pago único)** | La rareza. El usuario móvil espera gratis; la fricción del precio antes de probar es letal en un mercado sin descubrimiento | **iOS, nichos de calidad**, ports de indies de PC/consola, público que ya conoce la marca |

**Por qué F2P domina (no es moda, es estructura):**
1. **La fricción del precio mata la instalación** en un canal donde ya cuesta muchísimo que alguien llegue a la ficha. Cobrar $3 antes de probar recorta el funnel donde más duele.
2. **F2P monetiza la cola larga:** un premium cobra una vez; un F2P bueno extrae LTV durante meses vía IAP/ads. En un mercado que premia LiveOps, el pago único deja dinero en la mesa.
3. **El techo de ingreso de F2P es órdenes de magnitud mayor** — todo el top-grossing es F2P.

**Cuándo premium SÍ en móvil:**
- **En iOS**, para un juego de calidad con identidad clara (puzzle premium, narrativa, port de indie reconocido). El público de iPhone tier-1 paga por curación.
- **Apple Arcade** es la vía premium sana: Apple te paga un deal fijo por entrar a su catálogo de suscripción, de-riskeando el desarrollo a cambio de techo limitado — la única puerta premium realista para un dev pequeño en móvil [ver: gamedev/psicologia-retencion-negocio §5].
- **Nichos** donde el jugador busca "un juego que respete su tiempo, sin ads ni IAP" — es un argumento de venta en sí mismo. Mercado chico pero real, y casi solo en iOS.
- Regla: si vas premium en móvil, **el juego tiene que verse premium en el icono y los screenshots** — compite contra "gratis", y solo gana lo que parece obviamente mejor.

## 6. Soft launch: medir antes de arriesgar el global

El **soft launch** es lanzar en uno o pocos mercados pequeños y representativos ANTES del lanzamiento mundial, para medir D1/D7/D30, ARPDAU, funnel de onboarding y estabilidad técnica con usuarios reales — y iterar hasta que las métricas aguanten la ecuación LTV>CPI. Es el equivalente móvil del Next Fest/demo de Steam, pero mide *negocio*, no solo interés [ver: release-movil].

**Cómo se hace bien:**

| Decisión | Guía |
|---|---|
| **Qué mercados** | Chicos, en inglés o tu idioma objetivo, con comportamiento REPRESENTATIVO de tu público final. Clásicos: **Canadá, Australia, Nueva Zelanda, Nórdicos** (proxy de EE.UU./tier-1). Para volumen barato de test de retención: **Filipinas**. Elegir por representatividad, NO por lo barato del CPI |
| **Plataforma** | Google Play permite releases por país graduales fácilmente (ideal para soft launch controlado); iOS es más rígido. Muchos hacen soft launch en Android primero |
| **Qué medir** | D1/D7 (¿el core loop y onboarding aguantan?), ARPDAU y conversión a pago (¿monetiza?), CPI real comprando un poco de tráfico, funnel de onboarding por cohorte, crashes/ANRs por dispositivo |
| **Umbral go/no-go** | La ecuación de [ver: gamedev/psicologia-retencion-negocio §6]: con el CPI real de tu género y el LTV MEDIDO (no proyectado optimista), ¿hay margen? Si no, iterar o matar — no escalar a global esperando que "mejore solo" |
| **Requisito previo** | **Analytics por cohorte instrumentado ANTES del soft launch** (retención, funnel, eventos de economía). Sin datos por cohorte, el soft launch no mide nada [ver: unity-movil-input-servicios] |

- Regla de representatividad (cross-ref benchmarks GameAnalytics 2025): la mejor región en retención es Medio Oriente, las peores África/Asia — si haces soft launch en un mercado de retención estructuralmente baja, tus números mentirán a la baja; si en uno alto, a la alza. Elegí un proxy honesto de tu público real, no el extremo barato.
- Soft launch NO es "lanzar en un país y ya": es un **ciclo** de medir → iterar → re-medir, a veces meses, hasta que la cohorte aguante. Presupuestá esa iteración.

## 7. Requisitos de plataforma que afectan el negocio (2026)

No son "papeleo": estos requisitos pueden bloquear el lanzamiento o el modelo de negocio. Detalle técnico en [ver: release-movil]; aquí el ángulo de negocio.

| Requisito | Estado 2026 | Impacto de negocio |
|---|---|---|
| **Apple — IAP obligatorio** para bienes digitales (guideline 3.1.1) | Vigente | Contenido, monedas, cosméticos: por IAP de Apple (comisión 15-30%). No podés cobrar por fuera dentro de la app |
| **Odds de loot box visibles** (Apple 3.1.1 / Google) | Vigente en ambas | Si tu monetización usa cajas aleatorias, las probabilidades van publicadas. Requisito, no opción [ver: gamedev/psicologia-retencion-negocio §2] |
| **Apple ATT** (permiso de tracking; IDFA en cero si se niega) | Vigente desde iOS 14.5 | Encarece y enceguece el UA de iOS (§3). Diseñá la medición asumiendo mayoría de opt-out |
| **Google Play target API level** | Apps nuevas y updates deben apuntar a **Android 16 (API 36)** desde **31-ago-2026**; apps existentes ≥ **Android 15 (API 35)** para alcanzar usuarios nuevos en devices nuevos (extensión hasta 1-nov-2026) | Un juego con target API viejo **desaparece para usuarios nuevos** en teléfonos recientes. Mantené el target SDK al día o el catálogo se te muere solo (verificado en docs de Google) |
| **Data Safety (Google) / Privacy Nutrition Labels (Apple)** | Vigente | Declaración obligatoria de qué datos recolecta el SDK de ads/analytics. Declarar mal = rechazo o retirada |
| **Kids Category** (Apple 1.3/5.1.4; Google Families) | Vigente | Sin ads/analytics de terceros con IDFA; COPPA/GDPR-K. Si tu juego apunta a niños, el modelo ad-driven estándar NO aplica |
| **Real-money gaming** (Apple 5.3.4) | Vigente | Licencia por jurisdicción + geo-restricción + la app gratis. No para un indie casual |

**La comisión de tienda (lo que Apple/Google se quedan de cada peso):** afecta directo tu ingreso NETO y hay que modelarla en el LTV. Cifras verificadas por fetch esta sesión:

| Plataforma | Comisión estándar | Reducida | Umbral / condición |
|---|---|---|---|
| **Apple App Store** | 30% (paid apps + IAP) | **15%** (Small Business Program) | ≤$1M USD de proceeds/año; si superás $1M, vuelve a 30% las ventas futuras. Suscripciones: tier estándar (30%) baja a 15% recién tras 1 año de servicio pagado por suscriptor; **en Small Business Program es 15% desde el día 1** (no hay que esperar el año) |
| **Google Play (resto del mundo, vigente)** | 30% (sobre >$1M/año) | **15%** (primer $1M/año) | 15% al primer $1M de revenue/año, 30% al excedente; suscripciones **15% siempre** |
| **Google Play (UE/UK/EE.UU., desde 30-jun-2026)** | Estructura nueva por DMA/antitrust: 10%+5% fee de billing al primer $1M; 20-25%+5% por encima (menos con external links) | — | Reestructuración regulatoria en curso; **verificar la vigente para tu mercado** |

- **Consecuencia de diseño:** para un indie/estudio pequeño, la comisión real es **15%** (ambas tiendas, bajo $1M/año) — mejor de lo que dice el "30% de siempre". Pero se descuenta ANTES de tu ingreso: un IAP de $9.99 te deja ~$8.49 neto (menos el fee de billing donde aplique). Modelá el LTV en NETO, no en bruto.
- El panorama de comisiones está en flujo regulatorio (DMA en la UE, casos antitrust en EE.UU.): **re-verificá la tasa vigente para tu mercado y fecha** antes de fijar proyecciones de ingreso [ver: release-movil].

**Rechazos de review más comunes que cuestan semanas** (Apple, guidelines 2.x): app crashea en el device del reviewer; backend caído durante review; sin cuenta demo para features tras login (2.1); screenshots que no muestran gameplay real (2.3.3); metadata con marcas ajenas o keyword-stuffing (2.3.7); IAP mal configurados o no funcionales (2.1b). Antídoto: checklist de submission y build de review con backend vivo + cuenta demo [ver: release-movil].

## 8. La expectativa honesta: el coste real de competir

**La verdad brutal que ningún tutorial de "haz tu primer juego móvil" dice:** la mayoría de los juegos móviles **no recuperan la inversión**. El mercado está saturado, dominado por un puñado de estudios gigantes con presupuestos de UA de millones/mes y equipos de LiveOps permanentes, y el descubrimiento orgánico —el único recurso gratis de un indie— es casi inexistente para un título sin marca.

| Realidad | Consecuencia para el plan |
|---|---|
| Ingreso sube, descargas bajan (§1) | Entrar es más caro y más concentrado cada año |
| Cero juegos nuevos a $1B en 2025 (§1) | El top está cerrado a títulos de 5-10 años; no aspires a la cima, aspirá a un nicho rentable |
| Orgánico ≈ 0 sin hook viral (§3) | Sin capital de UA, necesitás viralidad genuina o un nicho con comunidad — o el juego no llega a nadie |
| Hybrid-casual único casual creciendo (§5) | El único segmento casual con negocio nuevo, pero es negocio de UA + LiveOps, no de diseño puro |
| iOS monetiza ~2x, Android da volumen (§2) | Elegí plataforma y modelo según de dónde saldrá el dinero, no "las dos porque sí" |

**Contra quién competís (la concentración):** el top-grossing móvil lo ocupan estudios que gastan en UA lo que un indie factura en su vida — Supercell, King, Playrix, Scopely, Moon Active y similares corren campañas de UA de escala industrial, equipos de LiveOps de decenas de personas y años de datos de retención afinados. En un chart que se ordena por revenue y descargas, un juego nuevo sin ese motor no aparece. La saturación no es solo "hay muchos juegos"; es que **los que ocupan las superficies visibles tienen una ventaja de capital y operación que no se cierra con talento**. El indie no le gana al incumbente en su terreno (charts, keywords de marca, UA de tier-1) — lo evita eligiendo un terreno donde el incumbente no juega (nicho premium, comunidad propia, Apple Arcade).

**El número honesto:** no existe una cifra pública fiable de "% de juegos móviles que recuperan la inversión" para citar como dato duro (el dato de whales — ~5% de pagadores ≈ 65-70% del ingreso IAP — está en la base hermana marcado como orden de magnitud, no verificado con primario) [ver: gamedev/psicologia-retencion-negocio §6]. Pero la estructura del mercado (§1: ingreso concentrado, descargas en declive, cero hits nuevos a $1B) hace la conclusión sólida sin necesidad de un porcentaje inventado: **la mayoría no recupera, y planear un proyecto móvil asumiendo que el tuyo será la excepción es el error de expectativa más caro del medio.**

**Dónde SÍ hay oportunidad para un dev pequeño en móvil:**
1. **Premium/curado en iOS** (o Apple Arcade): un juego de calidad para un público que paga, sin la carrera de UA. Techo modesto, riesgo acotado.
2. **Un nicho con comunidad propia** (idle, deckbuilder, puzzle sistémico, roguelite móvil premium) donde el boca a boca y ASO alcancen — el juego lo generan los sistemas, no la producción [ver: gamedev/generos].
3. **Hybrid-casual CON publisher**: si el juego es hyper/hybrid-casual, la vía realista es un publisher que ponga el capital de UA y el pipeline de creativos; el dev aporta el prototipo con CPI/retención validados. Sin publisher ni capital, hyper-casual no es negocio [ver: gamedev/generos].
4. **Port de un indie ya validado en Steam/consola**: si el juego ya probó su público y su calidad en PC, el port a iOS (premium o Apple Arcade) llega con marca, reseñas y boca a boca preexistentes — el descubrimiento ya ocurrió en otra plataforma. Es la forma más segura de que un indie toque móvil.

**Encuadre de decisión (síntesis):** móvil-first tiene sentido cuando el juego ES intrínsecamente móvil (sesión corta, un dedo, hook viral) Y tenés capital de UA o un publisher, O cuando apuntás a un nicho premium de iOS/Apple Arcade. En todos los demás casos, el orden sano es **validar en Steam primero y portar a móvil después** — el mercado móvil castiga al que llega sin marca ni presupuesto, y premia al que llega ya validado.

**La regla honesta:** si el proyecto móvil depende de comprar installs a escala y no tenés ese capital, o de que "se haga viral" sin un hook diseñado para serlo, o de LiveOps perpetuo que un solo-dev no sostiene — **el juego probablemente va a PC/Steam, no a móvil**. El móvil premia capital y operación continua; el indie sin ninguno de los dos compite mejor donde el descubrimiento aún es gratis [ver: gamedev/psicologia-retencion-negocio §7].

## Reglas prácticas

1. Antes de comprometerte a móvil, respondé por escrito: "¿cómo llega el primer jugador a instalarlo y monetiza más de lo que cuesta traerlo?". Sin respuesta, va a Steam.
2. Elegí plataforma primaria por el dinero: modelo premium/alto-ARPU → iOS primero; ad-driven de volumen → Android primero. No "ambas el día 1" salvo que el pipeline lo dé gratis [ver: unity/build-plataformas].
3. Verificá LTV medido > CPI del género con margen ANTES de gastar en UA — la única cifra go/no-go [ver: gamedev/psicologia-retencion-negocio §6].
4. Instrumentá analytics por cohorte (retención, funnel de onboarding, eventos de economía) ANTES del soft launch; sin cohortes no medís nada [ver: unity-movil-input-servicios].
5. Soft launch en un mercado REPRESENTATIVO (Canadá/ANZ/Nórdicos para tier-1), no en el más barato; iterá hasta que la cohorte aguante.
6. Tratá el icono como el activo #1: legible a 60px, un concepto, distinto del género. Págale a un artista antes que a los ads.
7. Los primeros 2 screenshots muestran gameplay real + hook, no splash art (y Apple lo exige, 2.3.3).
8. Usá A/B testing nativo GRATIS (Apple Product Page Optimization / Google Store Listing Experiments) para icono y primer screenshot; medí el uplift en TU test, nunca asumas un número prestado.
9. Pedí rating con el prompt nativo después de un momento de éxito, nunca al abrir; <4.0★ hunde la conversión.
10. Localizá título/keywords/screenshots a tus mercados objetivo — palanca orgánica barata y de alto retorno [ver: pipeline/narrativa-localizacion].
11. Si vas premium en móvil, andá a iOS y/o Apple Arcade; el juego debe VERSE obviamente premium para ganarle a "gratis".
12. Si es hyper/hybrid-casual sin capital de UA, buscá publisher o cambiá de plataforma/género — no es negocio de diseño puro [ver: gamedev/generos].
13. Diseñá la medición de UA de iOS asumiendo mayoría de opt-out de ATT (IDFA en cero); usá SKAdNetwork/AdAttributionKit [ver: unity-movil-input-servicios].
14. Mantené el target API de Android al día (API 35/36 en 2026) o el juego desaparece para usuarios nuevos en devices recientes.
15. Declará bien Data Safety / Privacy Labels según lo que tu SDK de ads recolecta; una declaración falsa = retirada.
16. Build de review con backend vivo + cuenta demo + notas para el reviewer; evita el rechazo que cuesta semanas [ver: release-movil].
17. Si tu monetización usa loot boxes, publicá las odds (requisito Apple y Google) [ver: gamedev/psicologia-retencion-negocio §2].
18. Modelá el LTV en ingreso NETO: restá la comisión de tienda (15% bajo $1M/año en ambas, +fee de billing donde aplique), no el bruto del IAP.
19. Números de mercado (CPI, ARPU, split iOS/Android, comisiones) SIEMPRE con fuente y fecha; el mercado y las tasas se mueven (DMA/antitrust), re-verificá antes de decidir presupuesto.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| "Lo lanzo en las stores y el descubrimiento orgánico traerá jugadores" | El orgánico móvil ≈ 0 sin hook viral; el descubrimiento se compra (UA) o se gana (featuring/ASO+nicho). Planea de dónde sale el primer install |
| Tratar iOS y Android como la misma app en dos tiendas | Son mercados distintos: iOS = dinero (~2x ARPU), Android = volumen. Priorizá plataforma según tu modelo (§2) |
| Comprar installs sin LTV medido "para ver si pega" | Sin LTV>CPI verificado en soft launch, es quemar dinero. Mide primero, escala después |
| Elegir el mercado de soft launch por CPI barato | Elegí por representatividad de tu público; un mercado de retención estructuralmente baja/alta te miente. Canadá/ANZ como proxy tier-1 |
| Icono/screenshots como último detalle antes de subir | Son tu conversión entera; el icono es el activo #1. Diseñalos y A/B-testealos como decisión de negocio |
| Screenshots con splash art / logo en vez de gameplay | Apple rechaza (2.3.3) y la conversión cae; mostrá el juego real en los primeros 2 |
| Premium en Android esperando volumen de ventas | El usuario Android no paga upfront a esa escala; premium vive en iOS/Apple Arcade y en nichos |
| Copiar la monetización F2P de un juego gigante (gacha, tienda rotativa) sin su UA ni LiveOps | Calibrá el modelo a tu escala: premium o híbrido simple para equipos de 1-5 [ver: monetizacion-movil] |
| Ignorar ATT y diseñar el UA de iOS como en 2020 | Asumí opt-out mayoritario; el targeting/atribución de iOS es probabilístico ahora (§3) |
| Dejar el target API de Android sin actualizar | El juego se vuelve invisible para usuarios nuevos en devices recientes (deadline 31-ago-2026) |
| Proyectar LTV optimista para justificar el gasto de UA | Usá ARPDAU y retención MEDIDOS en soft launch, no aspiracionales; sin margen real, no escales |
| Meter interstitials agresivos desde el minuto 1 para "monetizar temprano" | Rewarded opt-in integrada al loop; interstitial nunca en la primera sesión ni en pantallas de recompensa [ver: gamedev/psicologia-retencion-negocio §5] |
| Asumir que un juego móvil bueno "encontrará su público" como en Steam | Móvil premia capital + operación continua; sin ninguno, el indie compite mejor en PC/Steam |
| Modelar el LTV sobre el bruto del IAP (olvidar la comisión) | Restá 15% (bajo $1M/año) + fee de billing donde aplique; un $9.99 te deja ~$8.49 neto (§7) |
| Contar con el featuring editorial de Apple/Google como plan de adquisición | No se compra ni se garantiza; es un bonus impredecible. El plan es UA o ASO+nicho, el featuring es suerte |
| Comprar tier-3 barato y celebrar el pico de descargas | Descargas ≠ ingreso; medí rentabilidad por tier (LTV tier-3 ≪ tier-1). El install barato rara vez es el rentable |
| Dejar la ficha en un solo idioma "el inglés basta" | Localizá título/keywords/screenshots a tus mercados; es descubribilidad orgánica barata que la mayoría ignora |

## Fuentes

- **Mobile Gaming Statistics (2025)** — Udonis (blog.udonis.co), agregando **Newzoo** (ingreso juegos móviles 2024 ~$92B, +3% YoY), **Sensor Tower** (49.6B descargas 2024, −6% YoY; ingreso por género: Strategy $17.5B, RPG $16.8B, Puzzle $12.2B, Casino $11.7B, Sim $6.1B) y **Statista** (ARPU US $60.58 2025). Fetch verificado esta sesión. — https://www.blog.udonis.co/mobile-marketing/mobile-games/mobile-gaming-statistics
- **App Store Review Guidelines** — Apple Developer. Secciones verificadas por fetch: 3.1.1 (IAP obligatorio para bienes digitales, odds de loot box visibles, créditos no expiran), 3.1.2 (suscripciones), 1.3 y 5.1.4 (Kids Category: sin ads/analytics de terceros, COPPA/GDPR), 4.2 (minimum functionality), 5.3.4 (real-money gaming), 2.1/2.3.3/2.3.7 (rechazos: crash, backend caído, screenshots sin gameplay, keyword-stuffing). — https://developer.apple.com/app-store/review/guidelines/
- **App Tracking Transparency** — Apple Developer. Verificado por fetch: requestTrackingAuthorization, IDFA devuelto en cero si el usuario niega, prompt obligatorio antes de trackear entre apps. Base del impacto de ATT en el UA de iOS. — https://developer.apple.com/documentation/apptrackingtransparency
- **Target API level requirements for Google Play** — Google (Android Developers). Verificado por fetch: apps nuevas/updates → Android 16 (API 36) desde 31-ago-2026; existentes ≥ Android 15 (API 35) para alcanzar usuarios nuevos; extensión hasta 1-nov-2026. — https://developer.android.com/google/play/requirements/target-sdk
- **State of Mobile 2026** — Deconstructor of Fun. Móvil 2026: hybrid-casual único segmento casual creciendo IAP (+20%, $4.2B); ningún juego nuevo llegó a $1B en 2025; 4X móvil en boom. Cross-ref desde [ver: gamedev/generos] y [ver: gamedev/psicologia-retencion-negocio]. (Fuente heredada de las bases hermanas, no re-fetch esta sesión.)
- **2025 Mobile Gaming Benchmarks** — GameAnalytics (pool ~11,600 juegos, 16 géneros). D1/D7/D28 por plataforma y región; iOS top D1 31-33% vs Android 25-27%; mejor región MENA. Cross-ref [ver: gamedev/psicologia-retencion-negocio §3]. (Fuente heredada; los rangos ya viven documentados en la base hermana.)
- **Mobile Game Marketing Benchmarks 2025** — Admiral Media. CPI por género y plataforma (tabla §3), IPM/CTR por canal (§3). Cross-ref [ver: gamedev/psicologia-retencion-negocio §6]. (Fuente heredada de la base hermana.)
- **App Store Small Business Program** — Apple Developer. Verificado por fetch: 15% de comisión para desarrolladores con ≤$1M USD de proceeds/año; 30% estándar por encima. Suscripciones (verificado adicionalmente en developer.apple.com/app-store/subscriptions/): tier estándar 30%→15% recién tras 1 año de servicio pagado por suscriptor; en Small Business Program, 15% desde el día 1. — https://developer.apple.com/app-store/small-business-program/
- **Google Play service fees** — Google (Play Console Help). Verificado por fetch: 15% al primer $1M/año, 30% al excedente (resto del mundo); suscripciones 15%; estructura nueva UE/UK/EE.UU. (10%+5% billing fee) desde 30-jun-2026 por DMA/antitrust. — https://support.google.com/googleplay/android-developer/answer/112622
- **State of Mobile / consumer spend split iOS vs Android** — data.ai / Sensor Tower (histórico). La pauta ~65/35 de gasto y ~2x ARPU de iOS: **orientativo, verificar la cifra vigente** en el State of Mobile más reciente antes de usarla como dato duro (businessofapps y varios agregadores devolvieron 403/404 en esta sesión; no se pudo re-fetch un primario). La dirección (iOS monetiza más por usuario, Android tiene volumen) es consistente y sólida.
- **NO VERIFICADO esta sesión:** cifras exactas de uplift de conversión por A/B de icono/screenshot (varían por juego — medir en el test propio); split porcentual exacto iOS/Android de gasto 2025/2026 (verificar en Sensor Tower/data.ai). Marcados en el texto donde aplican.
