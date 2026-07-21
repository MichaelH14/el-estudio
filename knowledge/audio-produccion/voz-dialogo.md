# Voz y diálogo (VO)

> **Cuando cargar este archivo:** cuando el juego va a tener VOZ — diálogo grabado, barks/esfuerzos, narrador, o voz estilizada tipo gibberish — y hay que decidir SI conviene (es lo más caro y pesado del audio), cómo grabarla casera, cómo procesarla para que se entienda en la mezcla, y sobre todo la LICENCIA/derechos (actores, voz por IA, clonación). Es el lado de PRODUCCIÓN DE AUDIO de la voz. Lo que va en OTRO lado y NO se repite aquí: la escritura del diálogo, la voz de personaje y el sistema de barks como base de reglas [ver: gamedev/narrativa-guion §3]; los visemes y el lip-sync facial [ver: animacion3d/animacion-facial §5]; la implementación en Unity (Yarn Line Provider, `LocalizedAudioClip`, canal de VO con ducking, subtítulos por Timeline) [ver: pipeline/narrativa-localizacion §9-11]; la estrategia de localización de producto [ver: ux-ui/i18n-l10n]; la cadena de mezcla y el ducking/sidechain [ver: direccion-audio-mezcla]; y el formato de entrega del clip (mono, Vorbis, nombrado por ID) [ver: audio-a-juego §1]. Aquí va: decidir la voz, grabarla, limpiarla, la IA de voz y su terreno legal, contratar actores, y el gibberish.

---

## 1. ¿Necesita voz tu juego? El espectro (la voz es CARA)

La voz no es "una capa más de audio": es la más cara de producir, la más pesada de shippear y la única que **multiplica por idioma** si doblas. Antes de grabar una línea, sitúate en el espectro y elige el nivel MÍNIMO que la experiencia pide.

| Nivel | Qué es | Coste real | Localización | Úsalo si |
|---|---|---|---|---|
| **Sin voz** | Texto + retratos + SFX. La voz "se lee" | Cero | Solo texto | Default indie. RPGs clásicos, estrategia, puzzle, la mayoría del móvil |
| **Voz estilizada / gibberish** | Fonemas sin idioma (Simlish, Animalese) | 1 sesión, sin guion doblable | **No se traduce** (ventaja clave) | Vida/social/cozy, mascotas, personajes no-humanos (§7) |
| **Esfuerzos / grunts** | Solo los sonidos de gameplay: salto, golpe, daño, muerte, esfuerzo | 1-2 sesiones, decenas de clips | Casi no localiza (un gruñido es neutro) | Casi TODO juego de acción/plataformas. El mejor ROI de voz (§2) |
| **Barks** | Líneas cortas contextuales no interactivas (combate, alerta, idle) | Cientos de líneas × variantes | Se localiza si doblas | Shooters, inmersivos, mundos con NPCs "vivos" (§2) |
| **Full VO** | Todo el diálogo hablado, cinemáticas incluidas | Decenas de miles de líneas × N idiomas | El multiplicador que hunde presupuestos | RPG/narrativo AAA/AA donde la voz ES el producto |

**La fórmula del coste** (interiorízala antes de prometer voz):

```
coste_VO ≈ (grabación + dirección + edición + implementación) × nº_líneas × nº_idiomas_doblados
```

- Cada término esconde trabajo: casting, dirección de sesión, edición línea por línea, retakes, sync, QA de subtítulos, y **cada idioma doblado repite grabación+dirección+edición completas**.
- Regla de escalado: **empieza por esfuerzos** (nivel más barato con más impacto de game-feel [ver: gamedev/game-feel]), sube a barks solo si el mundo lo pide, y reserva full VO para cuando el diálogo es la razón de ser del juego. La mayoría de indies que "querían full VO" terminan en esfuerzos + gibberish + subtítulos, y está bien.
- Estrategia estándar incluso en AA: **VO en un idioma + subtítulos localizados** para el resto (§10). Doblar es la decisión más cara de todo el proyecto de audio.

---

## 2. Barks y esfuerzos: la producción de audio

El SISTEMA de barks (concepto→criterios→reglas, fallback genérico primero, memoria/cooldowns) ya está en [ver: gamedev/narrativa-guion §3]. Aquí va lo que ese sistema **exige del audio**: variación suficiente para no cansar, y esfuerzos grabados aparte.

### Esfuerzos (efforts): el mejor ROI de voz

Son los sonidos no-lingüísticos del cuerpo: salto, aterrizaje, esfuerzo al empujar, golpe recibido, jadeo, muerte, respiración. Casi ningún juego de acción se siente vivo sin ellos, y son **baratos y neutros de idioma**.

- **Grábalos en una pasada dedicada**, separados del diálogo: el actor hace 10 "hits", 10 "jumps", 10 "deaths" seguidos. Cansan la voz — déjalos para el final de la sesión o una sesión propia.
- **Baja el gain para los gritos/muertes** o haz una pasada aparte: un scream a nivel de diálogo normal **clipea** y no se recupera (§3). Nunca grabes esfuerzos fuertes con la misma ganancia que el habla.
- **No localizan** (o casi): un gruñido, un jadeo, un "¡agh!" sirven en cualquier idioma. Reutilízalos entre versiones y ahórrate doblarlos. Sepáralos del pool de diálogo por esa razón.

### Variación: el número que evita la fatiga

La regla de variación de SFX aplica igual a la voz de gameplay: **3-10 variantes** para cualquier bark/esfuerzo que suene >5 veces por sesión (el jugador nota la repetición en la primera hora) [ver: crear-sfx; audio-a-juego §7].

| Frecuencia del bark/esfuerzo | Variantes mínimas | Ejemplo |
|---|---|---|
| Cada pocos segundos (hit, jump, footstep-voz) | **8-10+** | Gruñido de golpe recibido |
| Varias veces por combate (spot enemy, reload) | **5-8** | "¡Enemigo!" |
| Ocasional (idle, saludo) | **3-5** | Comentario ambiental |
| Trama / único | 1 | Línea de guion |

- **Nombra y numera** para que el motor rote las tomas: `vo_guard_alert_01..08.wav`, mismo base + `_NN` correlativo → Audio Random Container / pool round-robin [ver: audio-a-juego §7; unity/audio-unity §4].
- La aleatoriedad ponderada + cooldown/no-repeat vive en el sistema de barks [ver: gamedev/narrativa-guion §3], pero **si no grabaste variantes, no hay qué rotar**: el audio es el cuello de botella, presupuéstalo al escribir.

---

## 3. Grabar voz casera: micro, sala, dirección, tomas

Se puede grabar VO publicable en casa. El enemigo no es el micro barato — es **la sala** (reflexiones) y **el ruido** (nevera, aire, tráfico). Los fundamentos de micro y captura están en [ver: foley-grabacion]; aquí va lo específico de la voz.

### Micro y sala

| Decisión | Recomendación para voz | Por qué |
|---|---|---|
| Tipo de micro | **Dinámico** (estilo SM58/SM7B) en sala sin tratar; condensador solo con sala tratada | El dinámico rechaza la sala y el ruido de fondo; el condensador capta TODA la habitación (reverb "de baño") |
| USB vs interfaz | USB (tipo Yeti) sirve para prototipo/placeholder; interfaz + XLR para final | El USB condensador capta demasiada sala |
| Tratamiento barato | Clóset lleno de ropa, fort de mantas, o mantas de mudanza colgadas alrededor | Superficies blandas = señal SECA (el motor pone la reverb, no la sala) |
| Distancia | ~15-20 cm, con **pop filter** | Cerca = más voz / menos sala; el pop filter mata plosivas en origen |
| Eje | Hablar **ligeramente off-axis** (de refilón, no de frente) | Reduce plosivas (P/B/T) y sibilancia sin procesar |

### Niveles de grabación

- **Picos a -12 … -6 dBFS**, nunca tocar 0. No puedes des-clipear un grito: si el actor va a gritar, **baja la ganancia** o haz una pasada aparte para los esfuerzos fuertes (§2).
- Graba en **24-bit** (más headroom para procesar; se entrega en 16-bit con dither [ver: audio-a-juego §2]).
- **Room tone obligatorio:** graba **20-30 s de silencio de la sala** al inicio de cada sesión. Es el perfil de ruido para limpiar después (§4) y el relleno para pegar líneas sin "huecos muertos".

### Dirección del actor (incluido si el actor eres tú)

- **Da contexto, no lectura:** quién habla, a quién, qué acaba de pasar, estado emocional. Dictar la entonación ("dilo más enojado en la tercera palabra") mata la naturalidad; describir la situación la genera. (Principio de dirección de VO estándar; alineado con la ficha de voz de personaje [ver: gamedev/narrativa-guion §3].)
- **Varias tomas por línea (3+):** una neutra, una "de más", una "de menos". Es más barato elegir en edición que volver a convocar sesión.
- **Slate/anuncia la toma** ("línea 042, toma 2") para encontrarla luego. Si tienes guion en spreadsheet con IDs [ver: gamedev/narrativa-guion §7], nombra por ID.
- **Consistencia de distancia:** el actor NO puede acercarse/alejarse entre líneas de la misma escena — el *proximity effect* (más graves al acercarse) cambia el timbre y no pega en el juego. Marca la posición.
- **Esfuerzos al final** (cansan la voz) y en pasada propia (§2).

---

## 4. Procesar la voz: la cadena de limpieza

Objetivo: que la voz **se entienda por encima de música y SFX** sin sonar procesada. Orden de la cadena (cada paso sobre el anterior). Las herramientas base (Audacity, SoX) y sus licencias están en [ver: herramientas-recursos-audio]; el balance final en la mezcla (bus de VO, ducking) en [ver: direccion-audio-mezcla].

### La cadena, en orden

| Paso | Qué arregla | Cómo |
|---|---|---|
| **1. Reducción de ruido** | Aire de sala, hiss, zumbido de fondo | Perfil del room tone → restar. Suave: de más = voz "underwater" |
| **2. De-plosive / plosivas** | Golpes de P/B ("pop") | High-pass 80-100 Hz + fade manual sobre el pop residual (mejor: pop filter en origen, §3) |
| **3. De-esser** | Sibilancia (S/SH) chillona | Comprimir/atenuar la banda 5-8 kHz SOLO cuando hay "ess" |
| **4. EQ** | Rumble, boxiness, presencia | High-pass; bajar 200-500 Hz si "cajón"; subir 2-5 kHz para inteligibilidad |
| **5. Compresión** | Rango dinámico (susurro vs grito) | Ratio suave; pega la voz a un nivel parejo para que no desaparezca ni sature |
| **6. Nivel** | Consistencia entre líneas | Normalizar pico con headroom; el balance fino va en el mixer, no re-exportando |

### SoX: comandos verificados (man page)

SoX hace la cadena por lotes desde terminal — ideal para cientos de líneas [ver: hacer-audio-por-codigo]. Instalar por brew (`brew install sox`), no npm [ver: audio-a-juego]. Sintaxis verificada contra el man de SoX:

```bash
# 1. Perfil de ruido desde los primeros 0.5 s de room tone (solo aire de sala)
sox voz_cruda.wav -n trim 0 0.5 noiseprof sala.prof
# 2. Restar ese ruido — amount 0.2-0.3; más alto = más artefactos/"underwater"
sox voz_cruda.wav voz_nr.wav noisered sala.prof 0.25
# 3. High-pass: quita rumble y buena parte de la energía de plosivas
sox voz_nr.wav voz_hp.wav highpass 90
# 4. Compand (compresor): attack,decay | knee:puntos de transferencia | ganancia
#    Ejemplo canónico del man de SoX:
sox voz_hp.wav voz_comp.wav compand 0.3,1 6:-70,-60,-20 -5 -90 0.2
# 5. Normalizar pico dejando headroom (-3 dBFS)
sox voz_comp.wav voz_final.wav norm -3
```

- `noiseprof [perfil]` genera el perfil desde un tramo de solo-ruido; `noisered [perfil] [amount]` lo resta (amount 0-1, default 0.5 — **empieza bajo, 0.2-0.3**).
- `highpass [-1|-2] frecuencia[k] [ancho]`; `lowpass` es su espejo. Voz masculina HP ~80 Hz, femenina ~100 Hz.
- `compand attack,decay [knee-dB:]in,out[,in,out…] [gain [vol-inicial [delay]]]`: comprime el rango dinámico; el ejemplo de arriba es el del propio man.
- `norm [nivel]` normaliza el pico al nivel dado; `gain dB` sube/baja lineal.
- **SoX NO trae de-esser dedicado:** para la sibilancia usa Audacity (EQ de banda estrecha o plugin) o el de-esser de una DAW. No lo inventes con SoX.
- Audacity tiene **Noise Reduction** integrado y, opcional, **supresión de ruido por IA (OpenVINO)** [ver: audio-a-juego §Licencias].

### Encajarla en la mezcla

- La voz es el **canal prioritario**: va a su propio grupo del AudioMixer con **ducking/sidechain** — música y SFX BAJAN mientras alguien habla, y suben al terminar [ver: direccion-audio-mezcla; pipeline/narrativa-localizacion §"canal propio"; gamedev/audio (adaptativa)].
- **Cuerpo de la voz en medios (200 Hz-4 kHz)** para que sobreviva al altavoz de móvil (lección DOOM, [ver: audio-a-juego §6]).
- No masterices cada línea a tope: consistencia entre líneas > volumen absoluto. El nivel integrado del mix se mide in-engine [ver: audio-a-juego §4].

---

## 5. TTS y voz por IA (2026): herramientas y LICENCIA ⚠️ legal serio

La voz por IA a 2026 ya es utilísima para **prototipo/placeholder/temp track** (grabas la sesión real después). Como **asset final publicado** es una decisión de **riesgo asumido** que HAY que documentar — el terreno legal es resbaloso y hay pleitos activos. Regla que engloba todo: **verifica el tier y la licencia EXACTOS antes de shippear; el free casi nunca sirve para un juego que se vende.**

### Herramientas y su estado (verificado 2026-07-21)

| Herramienta | Comercial en juego | Licencia / trampas (verificadas) |
|---|---|---|
| **ElevenLabs** (TTS + clonación) | Solo **plan de pago** = uso comercial. **Free = solo no comercial** | Retienes derechos sobre tu Output, pero concedes a ElevenLabs licencia amplia para operar/mejorar/derivar el servicio. Clonación: declaras estar "autorizado a compartir" la voz; no hay verificación de consentimiento de terceros más allá de tu declaración; ElevenLabs no comercializa tu voz "standalone" sin permiso. **Indemnización (Sección 9): tú defiendes y cubres costes** ante reclamos. Confirmar términos vigentes antes de publicar |
| **ElevenLabs Sound Effects** (SFX) | Pago = royalty-free comercial; free = no comercial | Ya cubierto en [ver: audio-a-juego §Licencias] |
| **Piper** (TTS local) | ⚠️ **Depende del repo que uses — verifica CUÁL** | El repo original `rhasspy/piper` es MIT pero está **archivado** (solo lectura). El desarrollo activo se movió a `OHF-Voice/piper1-gpl`, que es **GPL-3.0** (verificado vía GitHub API, no MIT: el nombre ya lo avisa). GPL-3.0 es copyleft — para CLI/proceso externo que solo genera el WAV (no linkeas la librería dentro del binario del juego) el riesgo práctico es bajo, pero si integras el código de Piper directamente en tu build, GPL-3.0 puede obligarte a liberar ese código. Además, la licencia del PROGRAMA ≠ la de cada **voz preentrenada**: cada voz tiene su propia licencia — revísala por voz |
| **Coqui XTTS** y modelos open similares | ⚠️ **Riesgo alto** | Patrón frecuente: el CÓDIGO es open pero los **pesos del modelo** salen bajo licencia **no comercial / solo investigación** (el caso conocido de XTTS es la "Coqui Public Model License", no comercial — **NO VERIFICADO esta sesión**, confirmar). Separa siempre licencia-de-código de licencia-de-pesos |
| **Suno** (música, no voz de diálogo) | Ya cubierto en [ver: audio-a-juego §Licencias] | — |

### El gran tema: clonación de voz y la ley (⚠️)

Clonar una voz (real o de un actor) sin permiso **no es solo poco ético: puede ser ilegal**.

- **ELVIS Act** (Tennessee, firmada 21-mar-2024, vigente 1-jul-2024): **prohíbe usar IA para clonar la voz de un artista sin consentimiento**, ejecutable penalmente como Class A misdemeanor. Es la primera ley estatal de EE.UU. específica para voz + IA. (Existen además propuestas federales tipo NO FAKES Act — **no verificadas en detalle esta sesión**; el panorama legal se está moviendo rápido.)
- **SAG-AFTRA / Interactive Media Agreement** (huelga de videojuegos jul-2024 → jul-2025, ratificado 9-jul-2025): el acuerdo exige **consentimiento** para crear réplicas digitales, **divulgación** de su uso, **compensación comparable** al trabajo directo del actor, y **el actor puede suspender el consentimiento**. Traducción para ti: si contratas actor de union, la IA sobre su voz tiene reglas contractuales; y usar fuentes no-union para esquivarlas está expresamente restringido.
- Reglas de oro:
  1. **Nunca clones una voz identificable** (celebridad, actor, persona real) sin consentimiento escrito y explícito. Riesgo legal directo.
  2. Para voz por IA "genérica" del proveedor: usa **plan de pago**, guarda **prueba del plan y fecha** de generación, y asume que **el output no es exclusivo** (otro puede generar algo casi igual → malo para identidad de marca).
  3. **Documenta cada asset de voz IA** en el `LICENSES.md` (herramienta, plan, fecha, prompt/voz usada) [ver: audio-a-juego §8].
  4. IA para **temp/placeholder** = seguro. IA como **voz final publicada** = riesgo asumido y documentado; para un juego serio, la voz humana grabada sigue siendo lo defendible.

---

## 6. Contratar actores de voz: dónde, qué pedir, coste

Si la voz importa, un actor real gana a la IA en dirección, matiz y **defensa legal** (derechos claros por contrato). Cómo hacerlo bien:

### Dónde

- Marketplaces / castings: sitios de casting de VO, agencias, o comunidades de game audio. Escucha demos, pide una **audición pagada corta** con TUS líneas antes de cerrar (una demo pulida no garantiza que encaje con tu personaje).

### Qué pedir SIEMPRE en el contrato

| Ítem | Qué exigir | Por qué |
|---|---|---|
| **Buyout / derechos** | Compra de derechos para uso perpetuo, mundial, en todas las plataformas del juego (y ports) | Sin buyout claro no puedes shippear tranquilo; un uso mal licenciado bloquea la publicación [ver: audio-a-juego §8] |
| **Cláusula de IA** | Prohibir/limitar entrenar o clonar su voz con las grabaciones (o pactarlo explícito) | Alineado con lo que exige SAG-AFTRA (§5); protege a ambos |
| **Entrega** | WAVs crudos (stems), una **toma por archivo**, nombrados por tu ID de guion, room tone incluido | Necesitas el crudo para editar/procesar a tu cadena (§4), no un master ya "producido" |
| **Retakes** | Nº de retakes incluido (pickups) por cambios de guion | El guion cambia; presupuesta pickups o pagas sesión nueva |
| **Formato** | Sample rate y bit depth que fijaste (44.1/48 kHz, 24-bit) | Consistencia con el resto del set [ver: audio-a-juego §2] |

### Coste (estructura verificada; cifras a confirmar)

- **Estructura estándar de videojuegos: pago por HORA de sesión** ("time in session"), no por palabra (verificado, GVAA Rate Guide). El actor cobra por el tiempo en cabina; los esfuerzos/gritos suelen sumar recargo (desgastan la voz).
- **Union vs no-union:** el trabajo union (SAG-AFTRA, Interactive Media Agreement) tiene **scale** mínimo por sesión + protecciones (§5); el no-union es negociable y suele salir más barato pero sin ese marco.
- **Referencias de tarifa** para números concretos y vigentes: **GVAA Rate Guide** (globalvoiceacademy.com) y las tarifas de la **SAG-AFTRA Interactive Media Agreement**. Las cifras exactas cambian por año/mercado — **consúltalas ahí, no las inventes** (esta sesión verificó la estructura por-hora + buyout, no montos concretos actuales).
- Regla de presupuesto: el coste escala con **nº de líneas × tarifa/hora + buyout**, y **se multiplica por idioma** si doblas (§10). Un reparto de varios personajes multiplica sesiones.

---

## 7. Gibberish / voz sintética estilizada (el truco barato)

Fonemas sin idioma real: da "voz" a los personajes **sin escribir diálogo doblable y sin localizar la voz**. Es el atajo de mayor ROI para juegos cozy/vida/mascotas.

### Simlish (el método "actor improvisa gibberish")

- Creado por Will Wright para *The Sims*. Tras descartar instrumentos (efecto "wah-wah" tipo Peanuts) y probar idiomas reales (ucraniano, navajo, tagalo, estonio), el actor Stephen Kearin propuso simplemente **hablar gibberish** y funcionó (verificado, Wikipedia).
- **Por qué gibberish y no idioma real:** que el jugador **conecte con la EMOCIÓN, no con las palabras**, y que **no canse** al repetirse entre partidas. *The Sims 2* llegó a 11 actores y 50.000+ líneas de Simlish.
- Cómo replicarlo: dirige al actor a improvisar sílabas con **intención emocional real** (contento, molesto, sorprendido). Grábalo como cualquier VO (§3) y trátalo como diálogo, pero **no necesita traducción** — un solo set sirve para todos los idiomas.

### Animalese (el método "un sonido por letra, generado del texto")

- Estilo *Animal Crossing*: la voz se **genera a partir del texto escrito**, mapeando **una muestra vocal corta por carácter** y concatenándolas rápido, con pitch/velocidad por personaje (método confirmado por los generadores open-source: carpeta de `sounds` con un clip por letra + pydub/ffmpeg concatenando; las internas exactas de Nintendo no son oficiales).
- Cómo montarlo tú:
  1. Graba (o sintetiza) **~26-40 muestras cortas** — una por letra/fonema base — con una voz.
  2. En runtime, para cada línea de texto: por cada carácter, reproduce su muestra, ajusta **pitch** (más agudo = personaje "pequeño") y **velocidad**, salta espacios/puntuación.
  3. Sube el pitch/tempo un poco para el efecto "parloteo". Sin actor por línea, sin localización de voz: el subtítulo lleva el significado.
- Encaja con lip-sync barato por amplitud (jaw sigue el volumen) [ver: animacion3d/animacion-facial §5].

**Ventaja transversal del gibberish:** el subtítulo (localizado) hace el trabajo de significado; la voz solo aporta emoción y carácter. Cero coste de doblaje (§10).

---

## 8. Lip-sync: la relación audio ↔ animación facial

El lip-sync es **problema de animación facial**, no de audio — los visemes, los sets (Preston Blair A-F, OVRLipSync 15, ARKit), la coarticulación y las tres estrategias (jaw-por-amplitud / fonemas en runtime / offline precomputado) están en [ver: animacion3d/animacion-facial §5] y NO se repiten aquí. Lo que aporta el AUDIO:

- **La claridad de la grabación decide la calidad del auto-lip-sync.** Un clip con ruido, reverb de sala o plosivas confunde al reconocedor de fonemas → visemes erróneos. La cadena de limpieza (§4) es también trabajo de lip-sync.
- **Da el texto al reconocedor:** las herramientas de lip-sync offline aceptan un **archivo de diálogo de texto opcional** que mejora muchísimo la precisión — pásaselo siempre. Tu ID de guion ya lo tiene.
- **Rhubarb Lip Sync** (offline, precomputado): CLI que toma **WAV/OGG + texto de diálogo opcional** y saca las mouth-shapes con timing en **TSV/XML/JSON/DAT**, usando el set Hanna-Barbera **A-F + G/H/X**. Uso básico `rhubarb -o salida.txt grabacion.wav`. Ese timing se hornea en la animación en el DCC/motor (verificado, repo de Rhubarb) [ver: animacion3d/animacion-facial §5].
- **Timing de audio = timing de boca:** si recortas silencios de la línea (§4) DESPUÉS de generar el lip-sync, lo desincronizas. Congela el clip de audio antes de calcular visemes.
- Regla de inversión (de animacion-facial): si la cámara no ve la boca a <3 m y no hay diálogo en pantalla, **jaw-por-amplitud basta**; no inviertas en fonemas para NPCs de fondo.

---

## 9. Implementación de diálogo: subtítulos SIEMPRE

La implementación técnica (Yarn `DialogueRunner`/Line Provider, `LocalizedAudioClip`, subtítulos por Timeline con track custom, canal de VO con ducking) está en [ver: pipeline/narrativa-localizacion §9-11] y la teoría de sistema de diálogo en [ver: gamedev/narrativa-guion]. Las reglas de PRODUCCIÓN de audio que gobiernan esa implementación:

- **SUBTÍTULOS SIEMPRE, para TODA línea hablada — incluidos los barks.** Es accesibilidad, no un extra [ver: ux-ui/accesibilidad; gamedev/ux-ui-onboarding]. Sin subtítulos, un jugador sordo o en un entorno ruidoso pierde información de juego.
  - Máx ~2 renglones, fondo semi-opaco u outline (legible sobre cualquier fondo), dentro del safe area, **on por defecto o preguntado en el primer arranque** [ver: pipeline/narrativa-localizacion §11].
- **Un ID estable por línea desde el día 1**, aunque grabes VO "después": el archivo de audio se nombra por ese ID (`dlg_ana_intro_010_es.wav`) y se enchufa sin tocar guion ni código. Retrofitear IDs cuesta 10× [ver: gamedev/narrativa-guion §7].
- **El subtítulo y el clip comparten el ID**, no el string: el texto vive en la tabla de localización (traducible), el audio en la tabla de VO por locale [ver: pipeline/narrativa-localizacion §9]. Nunca dupliques el diálogo en dos sistemas.
- **VO a su propio bus** con ducking de música/SFX mientras habla (§4).
- **Interrupción:** si el gameplay interrumpe una línea larga (radio, monólogo), diseña interrupción + reanudación como caso de primera clase — lección Firewatch [ver: gamedev/narrativa-guion §3]. En audio: no cortar en seco, hacer un fade corto.
- **String freeze antes del QA final:** cambiar copy después re-abre traducción Y regrabación de VO [ver: pipeline/narrativa-localizacion].

---

## 10. Localización de la voz: doblar es carísimo

La estrategia de localización de producto (a qué idiomas, expansión de texto, RTL, priorizar por mercado) está en [ver: ux-ui/i18n-l10n] y la técnica en Unity en [ver: pipeline/narrativa-localizacion]. Lo específico de la VOZ:

| Estrategia | Coste | Cuándo |
|---|---|---|
| **VO en 1 idioma + subtítulos localizados** | 1× voz + N× texto (barato) | **El estándar indie/AA.** Recomendado por defecto |
| **Gibberish + subtítulos localizados** | 1× voz (no se traduce) + N× texto | Cozy/vida/mascotas (§7). El más barato con "voz" |
| **Solo esfuerzos + texto** | Casi 0 de voz | Acción/plataformas sin diálogo hablado |
| **Doblaje completo (N idiomas)** | grabación+dirección+edición **× cada idioma** | Solo AAA/AA con presupuesto o mercado que lo exige |

- **Doblar repite TODO el pipeline de §3-4 por idioma**: casting, dirección, edición, sync, QA de subtítulos, y **re-lip-sync** si la boca sigue fonemas (los visemes cambian por idioma). Es la línea presupuestaria más cara del audio.
- **Los esfuerzos y el gibberish NO se doblan** (§2, §7): un gruñido y una sílaba sin idioma sirven en todas las versiones. Sepáralos del pool de diálogo desde el naming para reutilizarlos.
- **Prepara la localización aunque solo shippees un idioma:** IDs estables, texto en tablas, VO por locale ya cableado. Retrofitear localización a un proyecto "monolingüe" es rehacer la arquitectura [ver: pipeline/narrativa-localizacion].

---

## Reglas prácticas

1. Sitúa el juego en el espectro (§1) y elige el nivel MÍNIMO de voz que la experiencia pide. Default indie = sin voz o gibberish + esfuerzos.
2. `coste_VO ≈ (grabación+dirección+edición+impl) × nº_líneas × nº_idiomas`. Si no cabe en presupuesto, baja de nivel — no recortes calidad de las líneas que sí grabas.
3. Empieza por **esfuerzos** (mejor ROI de game-feel): grábalos en pasada aparte, con gain bajo para gritos/muertes, y no los localices.
4. Variación: **3-10 variantes** por bark/esfuerzo frecuente; si no las grabaste, el motor no tiene qué rotar. Nombra `_NN` correlativo.
5. Graba con **micro dinámico** en sala sin tratar (clóset/mantas), ~15-20 cm, pop filter, ligeramente off-axis.
6. Picos a **-12…-6 dBFS**, 24-bit, y **20-30 s de room tone** por sesión (perfil de ruido + relleno).
7. Dirige con **contexto, no con lecturas**; captura **3+ tomas** por línea; slate por ID de guion.
8. Cadena de limpieza en orden: ruido → plosivas → de-ess → EQ → compresión → nivel. SoX por lotes (`noiseprof`→`noisered 0.25`→`highpass 90`→`compand`→`norm -3`); de-esser en Audacity/DAW (SoX no tiene).
9. Voz = **canal prioritario**: bus propio + **ducking/sidechain** sobre música y SFX; cuerpo en medios (200 Hz-4 kHz) para el altavoz de móvil.
10. IA de voz: **temp/placeholder = OK**; asset final = riesgo asumido y documentado. **Nunca el tier free** en un juego comercial; guarda plan+fecha; asume output no exclusivo.
11. **Nunca clones una voz identificable** sin consentimiento escrito (ELVIS Act la penaliza; SAG-AFTRA la contractualiza). Separa licencia-de-código de licencia-de-pesos en modelos open (XTTS y similares suelen ser no-comercial).
12. Actor: exige **buyout perpetuo/mundial, cláusula de IA, WAVs crudos (una toma por archivo), room tone, y retakes incluidos**. Pago por hora de sesión (estructura GVAA); cifras vigentes en GVAA Rate Guide / SAG-AFTRA IMA.
13. Documenta la licencia/derechos de **cada** voz (actor, IA, biblioteca) en `LICENSES.md` — sin derechos claros no se publica.
14. Gibberish (§7) para no localizar la voz: Simlish (actor improvisa con emoción) o Animalese (un sample por carácter, generado del texto). El subtítulo lleva el significado.
15. **Subtítulos SIEMPRE, para toda línea hablada incluidos barks.** Máx 2 renglones, fondo/outline, on por defecto o preguntado al arrancar.
16. **ID estable por línea desde el día 1**; audio nombrado por ID; texto en tablas, audio en tabla de VO por locale. Nunca dupliques diálogo en dos sistemas.
17. Congela el timing del clip **antes** de calcular lip-sync; pásale el texto de diálogo al reconocedor (Rhubarb) para más precisión.
18. **VO en 1 idioma + subtítulos localizados** por defecto; doblar solo con presupuesto que lo aguante (repite todo el pipeline por idioma).
19. Esfuerzos y gibberish **no se doblan**: sepáralos del pool de diálogo desde el naming para reutilizarlos entre versiones.
20. String freeze antes del QA final: cambiar copy después re-abre traducción Y regrabación de VO.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Prometer full VO sin cuentas → el presupuesto revienta a mitad | Espectro de §1 + fórmula de coste ANTES de escribir; bajar de nivel, no recortar calidad |
| Grabar esfuerzos y diálogo al mismo gain → el grito clipea y no se recupera | Pasada aparte para esfuerzos fuertes con ganancia baja; picos ≤ -6 dBFS |
| 1-2 variantes de un bark que suena cada 5 s → fatiga en la primera hora | 3-10 variantes grabadas + rotación/cooldown en el sistema de barks |
| Condensador USB en sala sin tratar → voz con "reverb de baño" | Micro dinámico + superficies blandas; señal SECA, el motor pone la reverb |
| Sin room tone → no hay perfil de ruido y las pausas suenan a "hueco muerto" | 20-30 s de silencio de sala por sesión, siempre |
| Dictar la entonación al actor → lectura robótica | Dar contexto y estado emocional, no lecturas; 3+ tomas y elegir en edición |
| `noisered` agresivo → voz "underwater" con artefactos | Empezar en amount 0.2-0.3 y subir con cuidado; escuchar, no confiar en el número |
| VO al mismo nivel que música/SFX → no se entiende | Bus propio + ducking; cuerpo en medios para el móvil |
| IA de voz del tier free como asset final → licencia/propiedad turbia | Plan de pago + documentar plan/fecha; asumir no-exclusividad; para juego serio, voz humana |
| Clonar la voz de un actor/celebridad sin permiso | ⛔ Ilegal (ELVIS Act) / contractual (SAG-AFTRA): consentimiento escrito o no se hace |
| Confundir licencia de código con licencia de pesos en TTS open | Revisar por separado; muchos pesos (XTTS y afines) son no-comercial/research |
| Sin subtítulos o subtítulos solo para cinemáticas | Subtítulos para TODA línea hablada, barks incluidos; on por defecto |
| Diálogo hardcodeado / audio nombrado a mano sin ID | ID estable desde el día 1; audio y subtítulo comparten ID; texto y VO en tablas |
| Recortar silencios del clip después de generar el lip-sync → boca desincronizada | Congelar el timing del audio antes de calcular visemes |
| Asumir que "tendrá doblaje" y no preparar localización | IDs + tablas + VO por locale desde el inicio; retrofitear = rehacer arquitectura |

## Fuentes

- **SoX — man page** (linux.die.net/man/1/sox) — sintaxis verificada de `noiseprof`, `noisered [perfil] [amount 0-1]`, `highpass`/`lowpass [-1|-2] frec [ancho]`, `compand attack,decay [knee:]in,out… [gain [vol [delay]]]`, `norm [nivel]`, `gain dB`. Verificado 2026-07-21.
- **Piper — repositorio** (github.com/rhasspy/piper, **archivado** 2025-10-06) — TTS neural local/offline; ese repo es **MIT**, pero el desarrollo activo se movió a `github.com/OHF-Voice/piper1-gpl`, verificado **GPL-3.0** (vía API de GitHub, no MIT — cambio de licencia real, no repetición del original); las voces preentrenadas tienen licencia propia por voz. Verificado 2026-07-21.
- **ElevenLabs — Terms of Service** (elevenlabs.io/terms) — free = solo no comercial, pago = comercial; el usuario retiene derechos sobre el Output pero concede licencia amplia a ElevenLabs; clonación requiere declarar autorización (sin verificación de terceros); ElevenLabs no comercializa tu voz standalone sin permiso; **indemnización a cargo del usuario (Sección 9)**. Verificado 2026-07-21.
- **ELVIS Act (Ensuring Likeness Voice and Image Security Act)** — Wikipedia — Tennessee; firmada 21-mar-2024, vigente 1-jul-2024; prohíbe clonar por IA la voz de un artista sin consentimiento, Class A misdemeanor; primera ley estatal EE.UU. de voz+IA. Verificado 2026-07-21.
- **2024-2025 SAG-AFTRA video game strike / Interactive Media Agreement** — Wikipedia — huelga jul-2024→jul-2025 (ratificada 9-jul-2025) centrada en IA; consentimiento para réplicas digitales, divulgación, compensación comparable, el actor puede suspender consentimiento, restricción de esquivar con fuentes no-union. Verificado 2026-07-21.
- **GVAA Rate Guide** (globalvoiceacademy.com) — estructura verificada: videojuegos se pagan **por hora en sesión** ("time in session"); guía de referencia estándar para tarifas de VO. Montos concretos vigentes NO renderizados esta sesión — consultar el guide y la SAG-AFTRA IMA para cifras actuales. Verificado (estructura) 2026-07-21.
- **Simlish** — Wikipedia — Will Wright/*The Sims*; gibberish improvisado (Stephen Kearin) tras descartar idiomas reales; objetivo: conexión emocional y evitar fatiga; *Sims 2* = 11 actores, 50.000+ líneas. Verificado 2026-07-21.
- **Animalese generator** (github.com/equalo-official/animalese-generator) — técnica estilo *Animal Crossing*: muestras vocales cortas por carácter (carpeta `sounds`) concatenadas con pydub/ffmpeg + ajuste de pitch/velocidad; las internas oficiales de Nintendo no son públicas. Verificado 2026-07-21.
- **Rhubarb Lip Sync** (github.com/DanielSWolf/rhubarb-lip-sync) — CLI lip-sync offline; input WAV/OGG + archivo de diálogo de texto opcional; output TSV/XML/JSON/DAT; mouth-shapes Hanna-Barbera A-F + G/H/X; `rhubarb -o salida.txt grabacion.wav`. Verificado 2026-07-21.
- **Coqui XTTS — licencia de pesos** — patrón conocido: código open pero pesos bajo licencia no comercial (Coqui Public Model License). **NO VERIFICADO esta sesión** — confirmar la licencia de pesos vigente antes de cualquier uso comercial.
- Archivos hermanos referenciados (no fuentes web): [ver: audio-a-juego], [ver: crear-sfx], [ver: herramientas-recursos-audio], [ver: direccion-audio-mezcla], [ver: foley-grabacion], [ver: hacer-audio-por-codigo], [ver: gamedev/narrativa-guion], [ver: animacion3d/animacion-facial], [ver: pipeline/narrativa-localizacion], [ver: ux-ui/i18n-l10n], [ver: ux-ui/accesibilidad].
