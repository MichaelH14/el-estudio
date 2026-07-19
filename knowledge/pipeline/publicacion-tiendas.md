# Publicacion en tiendas: legal, comercial y operativo

> **Cuando cargar este archivo:** al preparar el submit de un juego a Google Play, App Store, Steam o itch.io — cuentas developer, review, ratings de contenido, privacidad/consentimiento, fiscal básico, assets de tienda, origen legal de los assets del juego y live-ops. Cubre el tramo del build firmado al juego vendiéndose. La estrategia de wishlists/demo/timing está en [ver: pipeline-completo]; el CÓMO técnico de IAP/ads/analytics en [ver: sistemas-meta]; la firma técnica del build en [ver: unity/build-plataformas].

Datos duros con fecha: verificados contra docs oficiales el **2026-07-18**. Fees, umbrales y target API caducan — re-verificar antes de decisiones de dinero. Lo fiscal/legal de este archivo es **orientativo, NO asesoría fiscal ni legal**.

## 1. Mapa comparativo de las 4 tiendas

| | Google Play | App Store | Steam | itch.io |
|---|---|---|---|---|
| Cuenta | $25 una vez | $99/año ($299 Enterprise) | $100 por **producto** | Gratis |
| Fee recuperable | No | No | Sí: se devuelve al superar $1,000 Adjusted Gross Revenue del juego | — |
| Corte de la tienda | 15% primer $1M/año, 30% después (subs 15%) — fuera de EEA/UK/US; en EEA/UK/US estructura nueva desde 30-jun-2026 (ver §2) | 30%; 15% con Small Business Program (≤$1M proceeds/año) | 30% estándar (tiers 25%/20% sobre $10M/$50M: NO VERIFICADO en esta pasada, vive en el Distribution Agreement tras login) | Lo eliges tú ("open revenue sharing"); histórico default 10% (el % exacto: NO VERIFICADO) |
| Review | Automática + humana; días (variable, sin SLA público) | 90% en <24h | 1-5 días (página y build se revisan por separado) | **Sin review** |
| Payout | ~día 15 del mes siguiente; umbral $1 (moneda local) / $100 (wire USD) | ≤45 días tras fin del fiscal month; umbral mínimo por país | Net-30 tras fin de mes; umbral $100 | Directo (PayPal/Stripe) o acumulado por itch |
| Espera mínima al launch | Review de production access (≤7 días típico) si cuenta personal nueva | Solo el review | **30 días** desde pagar el fee + página "coming soon" pública ≥2 semanas | Ninguna |

itch.io es la única sin barrera: sube el build y véndelo hoy. Por eso es el canal de playtests y jams [ver: pipeline-completo], y también un launch "soft" real antes de Steam.

## 2. Google Play Console — del build firmado a producción

### Cuenta y el peaje de las cuentas personales
- $25 una vez, tarjeta real (no prepaid), ID gubernamental a tu nombre legal. Cuentas nuevas verifican acceso a device Android vía la app Play Console (desde 2024).
- ⚠️ **Cuenta personal creada después del 13-nov-2023**: obligatorio un **closed test con ≥12 testers opted-in 14 días CONTINUOS** antes de poder pedir acceso a producción. Continuos = si un tester entra y sale, no cuenta. Después: solicitud de "production access" (preguntas sobre el test, el juego y readiness), review ≤7 días típico. **Planifica 3-4 semanas de colchón** entre build listo y poder publicar. Cuenta de organización no tiene este requisito.

### Tracks (el camino del build)
| Track | Testers | Review de políticas | Notas |
|---|---|---|---|
| Interno | ≤100 | **No** (exento también del Data safety) | Subida disponible en minutos; el equivalente a TestFlight interno |
| Cerrado | ≤2,000 por lista (hasta 200 listas; 50 por track) | Sí | Por email o Google Group; aquí se cumple el requisito de los 12 testers |
| Abierto | Ilimitado (mín. configurable 1,000) | Sí | Visible públicamente en Play; cualquiera se une |
| Producción | — | Sí | Los usuarios reciben el version code más alto compatible |

Promoción normal: interno → cerrado → producción (abierto es opcional). El **version code** solo sube, nunca se repite [ver: unity/build-plataformas].

### Target API (caduca cada año)
A 2026: apps nuevas y updates deben apuntar a **Android 16 (API 36)** desde el **31-ago-2026** (extensión pedible hasta 1-nov-2026). Apps que no actualizan dejan de ser instalables en devices nuevos. Regla operativa: al retomar cualquier juego dormido, lo primero es subir `targetSdkVersion`.

### Antes del primer release a producción (todo en Policy > App content)
Privacy policy URL · Data safety form (§6) · cuestionario IARC (§5) · declaración de ads · target audience/families si aplica · access credentials para el reviewer si hay login. Sin esto completo, el release no se puede enviar.

### Motivos comunes de retirada/rechazo (de las policies oficiales)
- **Data safety inexacto** → updates bloqueados o removal (declaración oficial de Google).
- **Misrepresentar contenido en el cuestionario IARC** → removal o suspensión (§5).
- Crash/broken functionality, metadata engañosa, permisos no justificados, y (juegos con dinero) loot boxes sin odds publicadas [ver: gamedev/psicologia-retencion-negocio].

### Service fee — cambio 2026
Desde el **30-jun-2026** en EEA/UK/US: subs auto-renovables 10% + 5% billing fee (primer $1M, sin tope claro publicado arriba de eso — verificar). Otras transacciones — **instalaciones nuevas**: 10% + 5% primer $1M → **25% + 5% sobre ese monto**. **Instalaciones existentes**: 20% + 5% primer $1M → 25% + 5% sobre ese monto (o 20% por external web links). Programas Play Games Level Up/Apps Experience: -5pp en la mayoría de categorías. Resto del mundo: 15% primer $1M/año, 30% después (subs 15% flat). Está en transición — **verificar la página oficial de service fees antes de proyectar ingresos**.

## 3. App Store Connect — cuenta, review y por qué rechazan juegos

### Cuenta
- $99/año. Individual: tu **nombre legal aparece como seller** (sin alias ni nombre de estudio). Organización: entidad legal real + **D-U-N-S** (gratis) + web propia con dominio + email del dominio.

### Review
- **90% de submissions revisadas en <24h**. Expedited review pedible para bug crítico o evento con fecha.
- **>40% de los rechazos = Guideline 2.1 (App Completeness)**: crashes, placeholder, links rotos, backend caído durante el review, IAP configurado pero invisible para el reviewer.
- Si hay login: **credenciales demo en App Review Information** — sin ellas es rechazo automático.

### Guidelines que muerden a los juegos (números exactos)
| Guideline | Regla | Trampa típica |
|---|---|---|
| 2.1 | Versión final, sin placeholder, probada en device | Submit del build "casi listo" |
| 2.2 | Ni demos ni betas en el App Store → TestFlight | Subir la "demo" como app aparte |
| 2.3.2/2.3.3 | Screenshots del juego EN USO (no key art ni splash); declarar qué requiere compra extra | Screenshots de cinemática/concept art |
| 2.3.8 | Metadata (icono, screenshots) apta para 4+ aunque el juego sea 17+ | Screenshot con sangre en un juego M |
| 3.1.1 | Todo desbloqueo digital por IAP de Apple; **loot boxes: odds publicadas ANTES de comprar**; monedas compradas no expiran; **botón restore obligatorio** [ver: sistemas-meta] | Vender monedas por web link dentro de la app |
| 3.1.2 | Subs ≥7 días y con valor continuo real | Sub que no entrega nada nuevo |
| 4.3 | Spam: no re-skins ni múltiples bundle IDs del mismo juego | "Un juego por tema/ciudad/equipo" |
| 5.1.1 | Privacy policy linkeada en ASC **y dentro de la app**; si hay cuentas, **borrado de cuenta in-app** obligatorio | Cuenta que solo se borra por email a soporte |
| 5.1.2 | Tracking solo con permiso ATT (§6) | SDK de ads trackeando sin prompt |
| 5.1.4 | Kids: sin analytics ni ads de terceros; COPPA/GDPR | Meter un juego infantil con AdMob |

TestFlight: beta interna hasta 100 testers sin review; externa con review ligero [ver: pipeline-completo]. Apple usa su **propio cuestionario de age rating** en App Store Connect (no IARC).

## 4. Steam Direct e itch.io

### Steam Direct — proceso y tiempos reales
1. Onboarding Steamworks: identidad + banco + fiscal (W-9 US / **W-8BEN** resto, §7). Hasta verificar, no avanzas.
2. **$100 por producto** (no reembolsable; recuperable en el payout cuando el juego supera $1,000 AGR).
3. **Reloj obligatorio**: mínimo **30 días** entre pagar el fee y poder lanzar, y la página debe estar en "coming soon" público **≥2 semanas**. O sea: el launch más rápido posible desde cero es ~1 mes.
4. **Content survey**: declarar TODO el contenido adulto que exista en el build (aunque no sea accesible) + disclosure de IA (§9). Genera los ratings regionales que se muestran en la página.
5. Review doble, **1-5 días cada uno**: página de tienda (antes del coming soon) y build (corren el juego, revisan config). Son colas separadas — lanzar la página meses antes del build es lo normal y lo recomendado [ver: pipeline-completo].
6. Payout: net-30 tras fin de mes, umbral $100, ACH (US) o wire SWIFT en USD.

### itch.io
- Sin review, sin fee, sin espera. Revenue share lo fijas tú en settings.
- Dos modos de cobro: **direct to you** (cada compra va a tu PayPal/Stripe — tú gestionas el VAT) o **collected by itch, paid later** (itch cobra y liquida — **el VAT de la UE lo maneja itch automáticamente**). Para un indie: collected, siempre — menos superficie fiscal.
- Subidas por `butler` con canales y parches incrementales [ver: pipeline-completo].
- Rol en el pipeline: playtests pagados/gratis, demos, jams, y validar precio antes del launch de Steam.

## 5. Ratings de contenido: IARC, ESRB, PEGI

- **IARC** = un solo cuestionario (gratis, en Play Console: Policy > App content) que genera ratings de varias autoridades a la vez: **ESRB** (Américas), **PEGI** (Europa/Medio Oriente), **USK** (Alemania), **ClassInd** (Brasil), **ACB** (Australia), **GRAC** (Corea, juegos). También lo usan otras tiendas (no Apple ni Steam: cada una tiene su cuestionario propio; el de Steam sale del content survey).
- Cómo funciona: respondes sobre el contenido (violencia, sexo, drogas, apuestas, lenguaje, interacción entre usuarios, compras) y cada autoridad calcula su rating con sus propias reglas. Se rehace si un update cambia el contenido.
- Qué dispara qué (nivel concepto, síntesis de los criterios públicos — el cálculo exacto es de cada autoridad):

| Respuesta del cuestionario | Efecto típico |
|---|---|
| Violencia cartoon/fantasía sin sangre | E10 / PEGI 7 — el territorio de un juego casual |
| Violencia realista, sangre | T-M / PEGI 16-18 |
| Apuestas simuladas (slots, póker sin dinero real) | Sube el rating aunque no haya dinero — ESRB "Simulated Gambling" |
| IAP / items aleatorios de pago | No sube el rating pero añade descriptor ("In-Game Purchases (Includes Random Items)") |
| Chat/UGC entre usuarios | Aviso "Users Interact" — y dispara obligaciones de moderación |

- ⛔ **Mentir en el cuestionario = retirada**: Google lo dice literal ("Misrepresentation of your app's content may result in its removal or suspension") y las autoridades IARC pueden auditar y **override** tu rating después de publicado. Responder "sin violencia" para bajar el rating es la mentira más cara del submit.
- Un rating alto no es un problema; un rating **incorrecto** sí. El rating además filtra a qué audiencias/países llega el juego (Corea y Alemania son estrictos).

## 6. Privacidad y datos: policy, formularios, consentimiento

### Privacy policy — obligatoria SIEMPRE que hay ads/analytics/IAP
Un juego Unity con LevelPlay + analytics [ver: sistemas-meta] **recolecta datos** aunque tú no tengas backend: los SDKs transmiten identifiers y usage data. Ambas tiendas exigen policy pública que diga: qué datos se recogen y cómo · para qué se usan · con qué terceros se comparten (nombra los SDKs) · retención y borrado · cómo revocar consentimiento · contacto. Apple además la exige linkeada **dentro de la app** (5.1.1). Generadores tipo template + revisión propia bastan para un juego chico; lo que no puede pasar es que la policy contradiga los formularios de la tienda.

### Play Data Safety form
- Declaras: datos **collected** (salen del device), **shared** (van a terceros), prácticas de seguridad (cifrado en tránsito, mecanismo de borrado), y el propósito de cada dato.
- **Incluye lo que hacen tus SDKs** — "irrespective of whether data is transmitted to you or a third-party server". Los vendors publican guías de qué declarar por SDK: úsalas, no adivines.
- Track interno exento; el resto no. Declaración inexacta → updates bloqueados o removal.

### Apple App Privacy labels (+ manifests)
- En App Store Connect declaras cada tipo de dato (Identifiers, Usage Data, Diagnostics, Purchases…), si está **linked** a la identidad del usuario, y si se usa para **tracking**.
- Eres responsable de lo que recolectan **todos** tus SDKs; los SDKs "commonly used" traen **privacy manifests** y firma — el build los agrega [ver: unity/build-plataformas].
- Declaración típica de un juego con ads+analytics+IAP (síntesis — confirmar contra los manifests de TUS SDKs): Identifiers (device ID) + Usage Data (product interaction, advertising data) + Diagnostics (crash) + Purchases → casi todo "linked", y "tracking = yes" si hay ads personalizados.

### Consentimiento en runtime: UMP y ATT
- **GDPR (EEA/UK)**: consentimiento previo para ads personalizados. Mecanismo estándar de Google: **UMP SDK** — `Update()` del consent status en **cada arranque** + `LoadAndShowConsentFormIfRequired()`; el form solo aparece cuando la región lo exige. LevelPlay y demás SDKs tienen sus APIs para recibir ese mismo consentimiento — cablearlas todas, no solo AdMob.
- **ATT (iOS 14.5+)**: prompt del sistema ANTES de trackear o leer el IDFA. Denegado → IDFA en ceros (los ads siguen, sin personalizar, con eCPM menor). Prohibido: bloquear funcionalidad o incentivar el permiso, y el **fingerprinting como alternativa**. Trackear sin permiso = rechazo; respondes también por tus SDKs.
- **COPPA/niños** (concepto, no asesoría): dirigido a <13 en USA → consentimiento parental verificable y de facto **cero ads/analytics de terceros** (Apple 5.1.4 lo prohíbe directo en Kids; Play Families lo restringe). Para un indie: si el juego no es PARA niños, no lo marques "para niños" — el régimen es otro deporte. Con audiencia mixta, Play exige declarar target audience y tratar a los menores como tales.

## 7. Fiscal básico del indie (orientativo — NO asesoría fiscal)

- **W-8BEN** (individuo no-US): certifica ante el withholding agent (Valve/Apple/Google) que eres extranjero y reclama beneficios de tratado. Sin tratado con USA, la retención estándar sobre royalties de fuente US es 30% (tasa NRA default del IRS; el % aplicable a TU caso: confirmar con asesor). Steam lo pide en el onboarding (interview fiscal); sin él no hay payouts.
- **IVA/sales tax del comprador: lo gestiona la tienda.** Apple y Google actúan como merchant of record; Steam calcula y remite VAT/sales tax; itch solo en modo "collected by itch". Tú recibes proceeds netos — no facturas IVA a cada comprador de cada país.
- Lo que la tienda NO hace: tus impuestos locales sobre el ingreso recibido. Eso es contabilidad propia del país donde tributas.
- Umbrales/tiempos de payout: ver tabla §1. Práctico: los primeros meses puede no llegar nada por no alcanzar el umbral — es normal, se acumula.

## 8. Assets de marketing de tienda

### Steam (dimensiones verificadas 2026)
| Asset | Tamaño | Regla |
|---|---|---|
| Header capsule | 920×430 | La cara del juego en la tienda |
| Small capsule | 462×174 | El logo debe **casi llenarla** — se ve diminuta en listas |
| Main capsule | 1232×706 | Featured/portada |
| Vertical capsule | 748×896 | |
| Screenshots | ≥5, mínimo 1920×1080 (16:9) | **Solo gameplay** — ni concept art, ni cinemáticas, ni premios; ≥4 marcadas "suitable for all ages" |
| Page background | 1438×810 (opcional) | |

Reglas duras de Valve: en las capsules **solo el título del juego** (sin quotes de prensa, sin "¡90% en Steam!"), logotipo legible contra el fondo. Qué funciona (síntesis de práctica): la capsule es un **thumbnail**, no un póster — personaje/objeto reconocible + título legible al 25% del tamaño; probarla encogida antes de subirla. Encargarla a un artista es de las mejores inversiones de marketing del juego (§9).

### Ficha móvil (ASO básico)
- Play: icono 512×512 (PNG 32-bit, ≤1MB), **feature graphic 1024×500** (obligatoria para el video), screenshots ≥2 (recom. 1080p+, 9:16/16:9), video = YouTube público/unlisted, embeddable y **sin ads**.
- App Store: screenshots por tamaño de device, app previews = capturas reales del juego (2.3.4).
- ASO en una línea: title + subtitle/short description llevan las keywords que la gente busca (género + fantasía: "idle miner", "solitario clásico"); el icono se A/B-testea (Play tiene experimentos nativos de ficha); las 2 primeras screenshots deciden — gameplay con un beneficio claro por screenshot, texto grande, portrait si el juego es portrait.

### Trailer (30-60s) — síntesis de práctica (referencia: Derek Lieu, trailer editor de Hades/Subnautica)
- **Gameplay en el primer segundo.** Sin logos de estudio al inicio, sin fade-in lento, sin texto de lore. El viewer decide en ~5s.
- Estructura: hook (lo más espectacular/diferente) → el core loop legible → variedad/escalada → título + fecha + CTA ("Wishlist on Steam").
- Errores típicos: trailer-película sin gameplay · enseñar el tutorial en vez del mid-game · música que no corta con la acción · >90s.
- El trailer se corta DEL juego real: capturas limpias sin HUD de debug, 60fps si el juego los tiene.

### Press kit y devlogs
- **presskit()** (Rami Ismail, gratis): descripción corta + historia del estudio, facts (precio, fecha, plataformas, links), screenshots/key art descargables en zip, trailer embebido, logos, contacto. Una tarde de trabajo; los medios no cubren juegos sin assets descargables.
- Devlogs (itch/YouTube/X): marketing acumulativo durante producción [ver: pipeline-completo] — cada milestone visual es un post con GIF. El GIF corto y loopeable es la moneda del gamedev en redes.

## 9. Origen de los assets del juego: encargo, compra, IA

### Encargar a artistas
- Brief mínimo: referencias visuales (3-5 imágenes "quiero esto"), lista exacta de entregables con tamaños/formato (sprites con PPU y padding, source files .psd/.ase incluidos [ver: arte-a-unity]), rondas de revisión acordadas (2 es sano), precio y plazo por escrito.
- **Derechos — lo único innegociable**: contrato escrito (email claro basta como rastro) con cesión de derechos de explotación comercial o licencia **exclusiva, perpetua, mundial** para el juego y su marketing. "Work for hire" es la figura US; en otros países la cesión debe ser explícita. Sin ese papel, técnicamente no puedes vender el juego. (Orientativo — no asesoría legal.)
- El artista retiene portfolio rights normalmente — está bien, se pacta.

### Comprar stock / Asset Store
- Unity Asset Store (concepto; EULA exacto: NO VERIFICADO en esta pasada — leerlo antes de depender de él): licencia por seat/entidad, permite **embeber** los assets en juegos comerciales, prohíbe redistribuirlos como assets (tu juego no puede ser "el asset pack jugable").
- Licencias abiertas: **CC0** (Kenney, parte de OpenGameArt) = uso libre sin atribución · **CC-BY** = atribución OBLIGATORIA donde la licencia diga · **GPL en assets** = riesgo de contaminar, evitar · fuentes tipográficas: **OFL** es segura para embeber.
- Regla operativa: `CREDITS.md` en el repo desde el día que entra el primer asset externo (asset → origen → licencia → si exige atribución). Al final del proyecto es imposible reconstruirlo. La pantalla de créditos del juego cumple las atribuciones acumuladas.

### Generación con IA — estado práctico 2026
- **Copyright** (orientativo; posición pública del US Copyright Office, informe ene-2025 — NO VERIFICADO contra el doc original en esta pasada): el output puramente generado por IA **sin autoría humana no es copyrightable en USA** → cualquiera puede copiarlo legalmente. Con selección, edición y composición humana sustancial, la obra resultante sí protege la parte humana. Traducción práctica: IA como base + retrabajo humano documentado (guardar los archivos de trabajo) es defendible; "prompt → PNG → al juego" te deja sin protección sobre ese asset.
- **Steam (verificado)**: el content survey obliga a declarar IA en dos categorías. **Pre-generated** (assets creados con IA durante el dev): se revisan como cualquier contenido y la declaración **aparece en la página de la tienda**. **Live-generated** (el juego genera contenido en runtime): además debes describir los **guardrails** contra contenido ilegal, y está **prohibido** el contenido sexual adulto live-generated. El review compara tus respuestas contra el build: declarar mal = no pasar.
- Apple/Google: sin casilla específica de IA a esta fecha (NO VERIFICADO exhaustivamente), pero las reglas de contenido, spam (4.3) y propiedad intelectual aplican igual al contenido generado.
- Riesgo de marca: parte del público de Steam penaliza el AI-art visible en reviews. Decisión de producto, no solo legal.

## 10. Remote config y live-ops (concepto)

- **Qué es**: parámetros clave-valor servidos desde la nube que el juego lee al arrancar → tunear economía, dificultad, eventos y feature flags **sin re-release ni pasar review**. El ciclo de review (24h Apple, días Play) deja de estar entre tú y un número mal balanceado.
- **Unity Remote Config** (UGS): key-value con **Game Overrides** (reglas de quién recibe qué: segmentos, %, A/B test) y environments dev/prod. Casos oficiales: curva de dificultad, feature flags, contenido de temporada on/off, A/B de precios. Alternativas: **Firebase Remote Config** (gratis, móvil) o un JSON versionado en tu CDN (suficiente para un juego chico sin A/B).
- **Cuándo compensa**: idle/F2P con economía viva, eventos calendarizados o soft launch en tuning constante → cablearlo ANTES del launch [ver: gamedev/psicologia-retencion-negocio]. Premium single-player sin eventos: casi nunca — un update normal basta.
- Reglas de implementación: **defaults locales SIEMPRE** (sin red → el juego funciona igual) · cachear el último config recibido · los valores remotos entran por la misma capa de datos que los ScriptableObjects [ver: sistemas-meta] · cada cambio remoto es un release de facto: probarlo en un environment dev antes de tocar prod.
- Límite: remote config cambia NÚMEROS y flags, no código ni assets — contenido nuevo sigue necesitando build (o Addressables + descarga, otro deporte).

## Reglas prácticas

- [ ] Cuentas developer creadas MESES antes del launch: verificación de identidad, D-U-N-S (org Apple) y el closed test de Play (12 testers × 14 días continuos) tienen semanas de latencia.
- [ ] Presupuesto de cuentas primer juego: $25 Play + $99/año Apple + $100/juego Steam + $0 itch (datos jul-2026).
- [ ] Steam: fee pagado ≥30 días antes del launch previsto y página "coming soon" ≥2 semanas antes — el reloj legal de Valve, aparte de la estrategia de wishlists [ver: pipeline-completo].
- [ ] Play cuenta personal nueva: el closed test de 14 días arranca en cuanto exista el primer build instalable — es el critical path del calendario.
- [ ] Target API de Android verificado al retomar CUALQUIER proyecto (31-ago-2026: API 36).
- [ ] Review de Apple: build final sin placeholder, links vivos, backend arriba, credenciales demo en App Review Information, IAP visibles para el reviewer.
- [ ] Restore de compras visible + odds de loot boxes publicadas antes del submit — rechazo seguro si faltan [ver: sistemas-meta].
- [ ] Cuestionario IARC respondido con el contenido REAL: mentir para bajar rating = removal; las autoridades auditan post-publicación.
- [ ] Privacy policy pública ANTES del primer formulario de tienda; nombra los SDKs reales (LevelPlay, analytics, IAP).
- [ ] Data safety (Play) y Privacy labels (Apple) rellenados con las guías oficiales de cada SDK instalado, no de memoria.
- [ ] UMP inicializado en cada arranque + prompt ATT antes de tocar IDFA; jamás bloquear el juego por denegar.
- [ ] Juego no dirigido a niños → no marcarlo "para niños"; dirigido a niños → cero ads/analytics de terceros (Apple lo prohíbe, Play lo restringe).
- [ ] W-8BEN entregado en el onboarding de cada tienda; el IVA del comprador lo maneja la tienda, tus impuestos locales no (orientativo — asesor para tu caso).
- [ ] Steam: 5+ screenshots de gameplay puro (≥4 all-ages), capsules solo con el título, small capsule legible como thumbnail encogido.
- [ ] Trailer: gameplay en el segundo 1, ≤60s, título+fecha+CTA al final; sin logos ni lore al inicio.
- [ ] presskit() montado antes del primer contacto con prensa/creators; GIF loopeable por milestone como material de devlog.
- [ ] `CREDITS.md` con origen y licencia de CADA asset externo desde el primer asset; atribuciones CC-BY en la pantalla de créditos.
- [ ] Contrato escrito con cesión/licencia exclusiva comercial por cada asset encargado; source files incluidos en el entregable.
- [ ] Assets con IA: declarados en el content survey de Steam (pre vs live-generated, guardrails si live); asumir que el output puro de IA no tiene copyright (orientativo 2026).
- [ ] Juego con economía viva/eventos → remote config cableado antes del launch, con defaults locales que aguantan sin red.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Crear la cuenta de Play la semana del launch | El closed test obligatorio (14 días continuos) + production review convierten eso en un mes de retraso seco |
| Pagar el fee de Steam con el build listo "para lanzar ya" | 30 días de espera obligatoria + 2 semanas de coming soon: el fee se paga al abrir la página, no al final |
| Submit a Apple con backend apagado o sin credenciales demo | Guideline 2.1 = 40%+ de los rechazos; el reviewer juega TU build hoy |
| "Demo" subida como app separada al App Store | 2.2: demos/betas van por TestFlight; la app aparte es rechazo y huele a 4.3 spam |
| Bajarle el rating al juego respondiendo suave el IARC | Removal/suspensión + override de la autoridad; el rating alto no mata, el falso sí |
| Data safety "sin recolección" con LevelPlay+analytics dentro | Los SDKs transmiten identifiers: es declaración falsa → updates bloqueados o removal |
| Prompt ATT saltado "porque los ads igual salen" | Trackear sin permiso = rechazo; fingerprinting como workaround = rechazo también |
| Screenshot de concept art / cinemática en Steam | Valve exige gameplay; además vende una expectativa que las reviews cobran |
| Capsule con quotes de prensa o "¡Oferta!" | Prohibido: solo el título del juego; el texto extra es motivo de rechazo de la página |
| Asset "gratis de internet" sin licencia rastreada | Sin CREDITS.md no puedes probar qué puedes usar; un DMCA post-launch tumba el juego de la tienda |
| Encargo de arte pagado por chat sin papel de derechos | Sin cesión escrita no hay derecho claro de venta; se arregla con un email-contrato de una página |
| Asset IA sin declarar en Steam | El review compara survey vs build; declararlo después de pillado es peor que el checkbox |
| Precio/economía hardcodeados en un F2P | Cada ajuste de balance paga review completo; remote config con defaults locales lo vuelve un cambio de dashboard |
| Proyectar ingresos con "70% para mí" en móvil | Play/Apple ~85% bajo $1M (programas small business) pero con matices 2026 (billing fees EEA/UK/US); verificar la página oficial del mes |
| Esperar el payout del mes 1 | Umbrales ($100 Steam/wire Play, mínimos por país Apple) + net-30/45: el primer dinero tarda 2-3 meses |

## Fuentes

**Docs oficiales de tiendas (consultadas 2026-07-18):**
- Steam Direct — partner.steamgames.com/steamdirect — fee $100/producto, recuperable a $1,000 AGR, 30 días de espera, coming soon ≥2 semanas, review 1-5 días, W-9/W-8BEN.
- Steamworks: Store Graphical Assets — partner.steamgames.com/doc/store/assets/standard — dimensiones de capsules, ≥5 screenshots 1920×1080 solo-gameplay, reglas de texto.
- Steamworks: Content Survey — partner.steamgames.com/doc/gettingstarted/contentsurvey — disclosure de contenido adulto y de IA (pre/live-generated, guardrails, prohibición adult live AI), ratings regionales en la página.
- Steamworks: Payments & Sales Reporting — partner.steamgames.com/doc/finance/payments_salesreporting — net-30, umbral $100, ACH/SWIFT.
- Steamworks: Getting Started — partner.steamgames.com/doc/gettingstarted — onboarding (identidad/banco/fiscal), review de página+precio+build.
- Play Console: registro de cuenta — support.google.com/googleplay/android-developer/answer/6112435 — $25 una vez, verificación de identidad, requisitos cuentas personales post-13-nov-2023.
- Play Console: requisitos de testing cuentas personales — answer/14151465 — 12 testers × 14 días continuos, production access review ≤7 días.
- Play Console: testing tracks — answer/9845334 — interno 100 sin review, cerrado 2,000/lista, abierto ilimitado.
- Play Console: target API — answer/11926878 — API 36 desde 31-ago-2026, extensión 1-nov-2026.
- Play Console: service fees — answer/112622 — 15%/30% y estructura EEA/UK/US desde 30-jun-2026.
- Play Console: payouts — answer/137997 — ~día 15, umbrales $1 local / $100 wire.
- Play Console: Data safety — answer/10787469 — collected/shared/security, SDKs incluidos, interno exento, enforcement.
- Play Console: content ratings (IARC) — answer/9859655 — autoridades, gratis, "misrepresentation may result in removal or suspension", override.
- Play Console: store listing assets — answer/9866151 — icono 512×512, feature graphic 1024×500, screenshots, video YouTube.
- Apple Developer: enrollment — developer.apple.com/support/enrollment — $99/año, individual vs org, D-U-N-S.
- App Review — developer.apple.com/distribute/app-review — 90% <24h, expedited, 40%+ rechazos = 2.1.
- App Review Guidelines — developer.apple.com/app-store/review/guidelines — 2.1, 2.2, 2.3.x, 3.1.1 (IAP, odds, restore), 3.1.2, 4.3, 5.1.1, 5.1.2, 5.1.4.
- App Privacy Details — developer.apple.com/app-store/app-privacy-details — labels, linked/tracking, responsabilidad por SDKs, privacy manifests.
- User Privacy and Data Use (ATT) — developer.apple.com/app-store/user-privacy-and-data-use — prompt iOS 14.5+, IDFA en ceros, prohibido fingerprinting/incentivos.
- App Store Connect Help: Getting Paid — developer.apple.com/help/app-store-connect/getting-paid — ≤45 días tras fiscal month, umbral por país, Paid Apps Agreement.
- Small Business Program — developer.apple.com/app-store/small-business-program — 15% si ≤$1M proceeds, associated accounts.
- itch.io Creator FAQ — itch.io/docs/creators/faq — open revenue sharing, direct vs collected, VAT automático en collected.
- IRS: About Form W-8BEN — irs.gov/forms-pubs/about-form-w-8-ben — certifica foreign status y treaty benefits ante el withholding agent.

**Otras:**
- Unity Remote Config — docs.unity.com/ugs (WhatsRemoteConfig) — key-value, Game Overrides, environments, casos de uso.
- AdMob UMP SDK (Unity) — developers.google.com/admob/unity/privacy — Update() por arranque, LoadAndShowConsentFormIfRequired().
- presskit() — dopresskit.com — Rami Ismail, gratis.
- Derek Lieu (trailer editor) — derek-lieu.com/blog — referencia de práctica de trailers; los consejos de estructura de §8 son síntesis de práctica, no cita literal.
- NO VERIFICADO en esta pasada (marcado en el texto): tiers 25%/20% de Steam (Distribution Agreement tras login) · % default de itch · EULA exacto del Unity Asset Store · informe del US Copyright Office ene-2025 · política IA de Apple/Google.

**Base sintetizada:**
- [ver: pipeline-completo] — timing de página/wishlists/demo y la etapa 6 del mapa maestro que este archivo detalla.
- [ver: sistemas-meta] — IAP/ads/analytics técnico cuyos requisitos de tienda (restore, odds, consent) aquí se explican.
- [ver: unity/build-plataformas] — firma, stripping, privacy manifests: el build que este archivo lleva a la tienda.
- [ver: arte-a-unity] — el pipeline de assets cuyo origen legal cubre §9.
- [ver: gamedev/psicologia-retencion-negocio] — el porqué de monetización/retención detrás de ratings, loot boxes y live-ops.
