# Foley y grabación

> **Cuando cargar este archivo:** cuando hay que GRABAR sonido real para el juego — foley (hacer que un objeto suene como otro), grabación casera con micro/teléfono, captura de ambientes de campo (lluvia, calle, bosque) o voz casera (gritos, esfuerzos, VO scratch) — y dejar el material limpio y procesado. Es la PROFUNDIZACIÓN de la Vía 2 (foley) de [ver: crear-sfx]: aquí no se repite la tabla básica de sustituciones ni el "cuarto silencioso" — se asume leído y se baja al detalle operativo (cadena de señal, patrones polares, niveles en dBFS, técnicas estéreo de campo, batch-processing por línea de comando). La edición en GUI (Audacity) está en [ver: crear-sfx]; el acabado final/entrega (loops, mono/estéreo, naming) en [ver: audio-a-juego]; el diseño/síntesis con el que se apila la grabación en [ver: sintesis-y-diseno-sonido]; la voz como PIPELINE (TTS, casting, dirección de VO) en [ver: voz-dialogo]. Aquí va el CRAFT de capturar sonido real y meterlo al juego.

---

## Grabar vs sintetizar vs biblioteca: el criterio del dev solo

Las 4 vías (síntesis / foley / editar samples / biblioteca) y su tabla comparativa están en [ver: crear-sfx]. Aquí el criterio afilado de **cuándo vale las horas de grabar** en vez de bajar un WAV o generar:

| Situación | Vía | Por qué |
|---|---|---|
| Sonido **orgánico con identidad** (pasos del prota, tela del abrigo, la puerta ESA) | **Grabar** | Nadie más tiene tu grabación; el foley da carácter que el stock no |
| Sonido **físico difícil de sintetizar** pero común (motor, lluvia, cristal) | **Biblioteca** editada | Ya existe en CC0/royalty-free a calidad pro; grabarlo tú sale peor y tarda más |
| **UI, retro, tonal, arma sci-fi, blip** | **Síntesis** [ver: sintesis-y-diseno-sonido] | Se controla parámetro a parámetro; grabarlo no tiene sentido |
| Sonido **imposible de conseguir real** (criatura, magia, nave) | **Layering**: foley + síntesis + biblioteca | Se construye; ninguna fuente sola basta [ver: sintesis-y-diseno-sonido] |
| **Prototipo / jam** (need it now) | Biblioteca o síntesis | Grabar es la última optimización, no la primera |

Regla del dev solo: **graba lo que te da identidad y no se compra** (pasos, foley del personaje, props únicos, voz). Todo lo demás, biblioteca CC0 o síntesis. Grabar 200 sonidos a mano es cómo se quema un proyecto solo — presupuesta las horas de grabación para los 10-20 sonidos que el jugador oye mil veces.

---

## El arte del foley: por qué un objeto suena como otro

El nombre viene de Jack Foley (Universal, años 30). La industria lo divide en **tres categorías** — misma división en cualquier foley stage (verificado, Wikipedia "Foley"):

| Categoría | Qué cubre | Herramienta típica |
|---|---|---|
| **Feet** (pasos) | Toda pisada del personaje sobre cada superficie | Zapatos reales + "foley pits": cajones con grava, tierra, madera, mármol. Al artista de pies se le dice *Foley walker / stepper* |
| **Moves** (tela) | El roce constante de ropa/cuero al moverse — la capa que "llena" el movimiento | Prendas cerca del micro; guantes de cuero, chaqueta, tela gruesa |
| **Specifics** (props) | Todo lo puntual: agarrar, soltar, golpear, romper, teclear, armas, llaves | El objeto real o su **sustituto** (ver abajo) |

### La regla de sustitución (el corazón del oficio)

La fuente real casi nunca suena "bien": suena débil, sucia o aburrida. Un objeto cotidiano suena **más real que lo real**. La tabla de sustituciones clásicas (celofán=fuego, coco=cascos, maicena=nieve, apio=huesos, guantes=alas…) está en [ver: crear-sfx] — **no se repite**. Lo que importa aquí es **cómo razonar una sustitución nueva** cuando no hay tabla:

| Eje a igualar | Pregunta | Ejemplo |
|---|---|---|
| **Transient (ataque)** | ¿El sonido empieza con un golpe seco, un click, una entrada suave? | Hueso roto = ataque seco + crujido → apio/zanahoria dan ese snap |
| **Contenido espectral** | ¿Es grave/pesado, medio/con cuerpo, o agudo/brillante? | Ala grande = whoosh grave → paraguas/guante pesado, no papel |
| **Textura/grano** | ¿Es liso, granular, crujiente, líquido? | Nieve = granular comprimido → maicena o bolsa de fécula |
| **Duración/decay** | ¿Se apaga rápido o resuena? | Metal = decay largo resonante → sartén/lámina, no cartón |

Si el sustituto iguala **transient + espectro + textura**, el cerebro lo acepta aunque la fuente sea absurda. El pitch y el espacio se ajustan después en edición [ver: audio-a-juego] — así que no busques el objeto que ya suena perfecto, busca el que tiene el **carácter** correcto y ajústalo.

### La despensa del foley (organizada por qué provee)

Complementa la tabla de [ver: crear-sfx]. Ten a mano una caja con:

| Provee | Objetos |
|---|---|
| **Crujidos / roturas** | Apio, zanahoria, lechuga, palitos, cáscara de nuez, tostada, plástico rígido |
| **Impactos / cuerpo** | Guías telefónicas / libros gruesos, repollo, sandía, filete, saco de arena, almohada |
| **Metal** | Sartén, llaves, cadena, lámina fina, cubiertos, herramienta, muelle |
| **Líquido** | Vaso + pajilla, esponja, trapo mojado, bandeja con agua, botella |
| **Fricción / roce (moves)** | Guantes de cuero, chaqueta, globo, tela vaquera, papel de lija |
| **Granular (superficies)** | Maicena, sal, arroz, café en grano, grava en bandeja, cereal |
| **Aire / whoosh** | Regla flexible, vara, toalla, paraguas, abanico, tubo corrugado |
| **Vidrio / cerámica** | Copa, bombillas viejas (romper con cuidado), platos, canicas |

Grábalos todos **una vez** en una sesión "de despensa": tendrás una mini-biblioteca propia y CC-limpia (la grabaste tú) para futuros proyectos.

---

## Micrófono y cadena de señal

[ver: crear-sfx] tiene la tabla equipo-de-menos-a-más. Aquí la profundización de qué micro y por qué.

### Condensador vs dinámico vs teléfono

| Tipo | Sensibilidad | Alimentación | Fuerte en | Débil en | Uso game-audio |
|---|---|---|---|---|---|
| **Condensador** (USB Yeti/Samson, o XLR + interfaz) | Alta, captura detalle y transientes | Phantom **+48V** (el USB lo lleva dentro) | Foley fino, detalle, ambiente | Chupa TODO el ruido del cuarto | El caballo de batalla del foley casero |
| **Dinámico** (SM58/SM7B-style) | Baja, robusto | Ninguna | Fuentes fuertes, voz, gritos; **rechaza el cuarto** | Le falta "aire"/detalle fino | Cuartos sin tratar y voz/esfuerzos |
| **Teléfono** (app de grabadora en WAV) | Fija, con **AGC** que bombea | — | Tenerlo siempre encima | AGC arruina dinámica; graves flojos | Boceto y foley cercano; desactivar AGC si la app deja |

Clave: el condensador USB es el mejor salto por el dinero para foley, PERO su sensibilidad exige un cuarto callado. En un cuarto ruidoso, un **dinámico** cercano gana porque rechaza el fondo. El teléfono sirve si te **acercas mucho** y desactivas el auto-gain.

### Patrón polar (de qué dirección capta)

| Patrón | Capta | Rechaza | Cuándo |
|---|---|---|---|
| **Cardioide** | Frente | Detrás | Default de foley/voz. Tiene **proximity effect**: graves suben al acercarse (útil o problema) |
| **Omnidireccional** | Todo, plano, sin proximity | Nada | Ambiente/room en cuarto tratado; **malo** en cuarto ruidoso |
| **Figura-8 (bidireccional)** | Frente + atrás | Los lados | Componente "side" en Mid-Side; dos fuentes enfrentadas |
| **Supercardioide / shotgun** | Cono estrecho al frente | Lo de alrededor | Aislar una fuente a distancia / campo |

El Yeti-style trae selector de patrón: **cardioide** para casi todo el foley. Para VO, cardioide y cantar/hablar **ligeramente fuera del eje** (off-axis) reduce plosivas.

### La cadena de señal (dónde se pierde/gana calidad)

`Fuente → distancia/patrón del micro → preamp/ganancia → conversor A/D (24-bit) → archivo`

- **Distancia manda más que la ganancia.** Acercar el micro sube la señal SIN subir el ruido del cuarto (la relación señal/ruido mejora); subir ganancia sube ambos. Foley cercano: **5–20 cm**.
- **XLR + interfaz** (Focusrite Scarlett-style) da mejor preamp y phantom real que el USB, a cambio de otra caja. Solo si el audio es central en el juego.
- **Monitorea con auriculares cerrados** mientras grabas: el oído ignora la nevera/aire, el micro no. Si lo oyes en los cascos, está en la toma.

---

## La habitación y la distancia (profundización)

El "cuarto silencioso" (clóset con ropa, room tone, nada de baños con eco) está en [ver: crear-sfx]. Detalle acústico que suma:

| Concepto | Regla operativa |
|---|---|
| **Reverb horneada** | La reverb del cuarto **no se quita** en post. Graba SECO (ropa/almohadas absorben reflexiones) y espacializa en el motor [ver: unity/audio-unity] |
| **Proximity effect** | Micro cardioide muy cerca (<10 cm) infla los graves → voz "gorda" o retumbe. Aléjate un poco o aplica high-pass ~80 Hz si no lo quieres |
| **Regla 3:1** (multi-micro) | Si usas 2 micros, el 2º debe estar a ≥3× la distancia que separa el 1º de la fuente → evita cancelación de fase al sumar |
| **Off-axis / reflexión** | No apuntes el micro a una pared dura cercana ni a la mesa; una reflexión temprana ensucia el ataque. Trapo/manta bajo el objeto en la mesa |
| **Distancia por tipo** | Foley detalle: 5–20 cm. Voz: 15–20 cm con pop filter. Ambiente/room: 1 m+ y patrón omni en cuarto tratado |

---

## Niveles de grabación: sin clipear, con headroom

Un clip (pico que toca 0 dBFS) viene **roto** y no se arregla — regrabar es la única salida. Pero grabar "al tope" tampoco es la meta: en **24-bit hay ~144 dB de rango**, así que grabar con margen NO añade ruido audible.

| Regla | Valor | Por qué |
|---|---|---|
| **Grabar en 24-bit** | 24-bit PCM | Enorme headroom; puedes grabar "bajo" y normalizar después sin ruido |
| **Picos objetivo** | **−18 a −12 dBFS** (voz/foley normal) | Deja ~12 dB de margen para el transiente sorpresa que no viste venir |
| **Techo absoluto** | Nunca por encima de **−6 dBFS** | Un golpe fuerte imprevisto no debe llegar a 0 |
| **Fuente muy dinámica** (gritos, impactos) | Baja la ganancia y **aléjate** | Mejor grabar bajo y subir en post que clipear una vez |
| **Sin normalizar al grabar** | Normaliza en edición | Normalizar a la fuente = re-cuantizar; hazlo una vez, al final [ver: audio-a-juego] |

Flujo: pon la ganancia, haz la toma **más fuerte que esperas** (el grito, el golpe seco), mira que el pico quede ≤ −6 dBFS, y recién ahí graba en serio. Si la app muestra rojo una sola vez, baja ganancia o aléjate y repite.

---

## Técnica de captura

Las bases (muchas tomas, silencio antes/después, exagerar) están en [ver: crear-sfx]. Añadidos que separan una sesión usable de una que se tira:

- **Room tone SIEMPRE.** 10–30 s de "silencio" del cuarto por sesión. Sirve para (1) el perfil de reducción de ruido (abajo) y (2) rellenar huecos de ambiente sin que se note el corte. Grábalo con el MISMO setup que las tomas.
- **Graba de más.** Cuesta lo mismo grabar 12 pisadas que 3. En la sesión no sabes cuál servirá; en edición eliges. El material que no capturaste es un regreso al setup.
- **Slate verbal.** Antes de cada grupo di el nombre en voz ("pasos madera, toma 1"). Encontrar la toma en 40 archivos sin slate es una tarde perdida.
- **Varía la performance, no solo repitas.** Pisada suave / normal / fuerte; agarre lento / brusco. Esa variación es la que alimenta el pool de variantes en runtime [ver: unity/audio-unity], no solo el pitch aleatorio.
- **Aísla el gesto.** Un movimiento por toma, con manos/ropa quietas alrededor. Si la silla cruje o la manga roza, esa toma está contaminada.
- **Deja correr.** No cortes entre repeticiones; graba una pista larga con las 12 tomas y córtalas en edición — más rápido y no pierdes la primera por darle a stop tarde.

---

## Field recording: capturar ambientes reales

Ni [ver: crear-sfx] ni los demás cubren campo. Aquí lo esencial para atmósferas (lluvia, calle, bosque, mar, multitud) que se usan como cama de ambiente en loop [ver: gamedev/audio, ambiente].

### Equipo mínimo

| Ítem | Para qué |
|---|---|
| **Grabadora portátil** (Zoom H-series, Tascam DR-series) con micros estéreo integrados | Autónoma, 24-bit, X/Y integrado; el estándar del field recordist solo |
| **Windscreen de espuma + "dead cat" (windjammer peludo)** | ⛔ El viento arruina cualquier toma exterior. La espuma es el mínimo; el peludo es obligatorio con brisa. El low-cut del recorder ayuda pero **no basta solo** |
| **Trípode o soporte** | La grabadora en mano capta ruido de manipulación (handling). Apóyala o usa shock mount |
| **Auriculares cerrados** | Oír lo que realmente entra (avión, obra, perro) antes de grabar 5 min inútiles |

Teléfono en modo campo: sirve para bocetos, pero el micro se satura con viento/graves y el AGC bombea. Para ambiente de verdad, grabadora dedicada.

### Técnicas estéreo (elige por mono-compatibilidad)

Un ambiente de juego a menudo se colapsa a mono o se re-espacializa en el motor, así que la **compatibilidad mono** manda:

| Técnica | Setup | Carácter | Mono-safe | Uso |
|---|---|---|---|---|
| **X/Y** | 2 cardioides coincidentes ~90° | Imagen sólida, foco central | ✅ Sí (coincidente, sin fase) | Default del recorder portátil; lo más seguro |
| **Mid-Side (M/S)** | Cardioide (mid) + figura-8 (side); se decodifica M±S | **Ancho ajustable en post**, mono perfecto | ✅✅ El mejor | Ambiente para juego: ajustas ancho después y colapsa a mono sin fase |
| **ORTF** | 2 cardioides, 17 cm, 110° | Ancho natural, tipo "oído humano" | ⚠️ Aceptable | Ambientes ricos si el cuarto/lugar lo permite |
| **A-B (par espaciado)** | 2 omnis separados | Muy ancho, envolvente | ❌ Fase en mono | Solo si NO va a colapsar a mono |
| **Blumlein** | 2 figura-8 a 90° | Preciso, realista | ✅ Sí | Requiere lugar tratado/limpio; avanzado |

Para el dev solo con un Zoom: **X/Y integrado** para casi todo, **M/S** si el modelo lo trae y quieres ajustar el ancho en post.

### Técnica de ambiente

- **Tomas LARGAS.** 30 s a varios minutos por ambiente → material para hacer loops sin repetición obvia y para elegir el tramo más "limpio" (sin el carro que pasó) [ver: audio-a-juego, loops].
- **Graba el mismo sitio a distintas horas/intensidades.** Lluvia suave vs tormenta, calle diurna vs nocturna → capas para ambiente adaptativo [ver: gamedev/audio].
- **Separa capas.** Graba la **cama** (el continuo: lluvia, viento, murmullo) aparte de los **one-shots** (el trueno, el pájaro, la bocina). En el motor la cama va en loop y los one-shots se disparan aleatorios [ver: unity/audio-unity].
- **Watch the low end.** Tráfico, aire acondicionado y viento meten rumble sub-80 Hz que come headroom y ensucia. High-pass ~80 Hz en edición para ambientes que no dependen de graves.
- **Distancia = perspectiva.** Cerca de la fuente = detalle e intimidad; lejos = espacio y reverberación natural. Para una cama envolvente, un poco de distancia y omni/M/S.

---

## Edición del material grabado (batch por línea de comando)

La edición en GUI (Audacity: trim, normalize, noise reduction, fade, EQ, pitch) está detallada en [ver: crear-sfx]. Aquí el complemento que un agente/dev solo agradece: **procesar decenas de tomas por lote con SoX** (instalar `sox` por brew; CLI de audio de facto). Sintaxis verificada contra el man page de SoX:

| Objetivo | Comando |
|---|---|
| **Perfil de ruido** (desde room tone) | `sox in.wav -n trim 0 0.5 noiseprof room.prof` |
| **Reducir ruido** con ese perfil | `sox in.wav out.wav noisered room.prof 0.21` (amount 0–1; 0.21 suave, default 0.5) |
| **Recortar silencio** de inicio y fin (top-and-tail) | `sox in.wav out.wav silence 1 0.05 0.1% reverse silence 1 0.05 0.1% reverse` |
| **Normalizar** a −1 dBFS | `sox in.wav out.wav norm -1` (norm = alias de `gain -n`) |
| **Micro-fades** anti-click en los extremos | `sox in.wav out.wav fade t 0.005 0 0.005` (`0` = hasta el final; `t` = lineal) |
| **A mono + resamplear** 44.1 kHz (fuente **estéreo**) | `sox in.wav out.wav remix 1,2 rate 44100` (o `channels 1 rate 44100` — funciona con cualquier nº de canales, `remix 1,2` exige que la fuente tenga ≥2 canales o falla con `too few input channels`) |
| **Cadena completa** de acabado (⚠️ DOS pasos, ver nota) | `sox raw.wav _trim.wav silence 1 0.05 0.1% reverse silence 1 0.05 0.1% reverse` **&&** `sox _trim.wav ready.wav norm -1 fade t 0.005 0 0.005` |
| **Lote** sobre una carpeta | `mkdir -p ready && for f in *.wav; do sox "$f" "ready/$f" norm -1 fade t 0.005 0 0.005; done` |

⚠️ **`silence` y `fade` (stop-position 0=fin) NO se pueden encadenar en una sola invocación de SoX**: al recortar con `silence` la duración de salida deja de ser conocida de antemano, y `fade` con stop-position 0 necesita conocer esa duración → falla con `fade: cannot fade out: audio length is neither known nor given` (verificado ejecutando la cadena real). Solución: **dos invocaciones de `sox`** (primero recorta, después normaliza+fade sobre el archivo ya recortado) — ambas cadenas de arriba están probadas end-to-end. La carpeta destino del lote (`ready/`) debe existir antes (`mkdir -p`) o SoX falla con `can't open output file` (también verificado).

Regla honesta: SoX es imbatible para **lotes repetitivos** (normalizar 80 pisadas, top-and-tail una carpeta). Para escuchar/decidir/limpiar un ruido puntual, la GUI de Audacity es mejor [ver: crear-sfx]. `noisered` con `amount` alto (>0.3) da el "sonido submarino/robótico" — quédate bajo.

---

## Procesar la grabación para que encaje en el juego

La grabación cruda casi nunca entra tal cual: se **pitchea, se estira y se apila con síntesis**. El diseño de esa capa sintética y el layering (ataque + cuerpo + cola) están en [ver: sintesis-y-diseno-sonido] y [ver: crear-sfx]. Recetas SoX (verificadas) para la parte de procesar la toma real:

| Transformación | Comando | Efecto |
|---|---|---|
| **Bajar pitch, mantener duración** (más grande/pesado) | `sox in.wav out.wav pitch -300` | −300 cents = −3 semitonos. Criatura, impacto pesado |
| **Subir pitch, mantener duración** (más pequeño/rápido) | `sox in.wav out.wav pitch 500` | +5 semitonos. Bicho pequeño, UI ágil |
| **El truco viejo: velocidad** (pitch + tempo juntos) | `sox in.wav out.wav speed 0.8` | Más lento Y más grave = monstruo; `speed 1.5` = pequeño/rápido |
| **Estirar/acortar SIN cambiar pitch** | `sox in.wav out.wav tempo 1.2` | Ajustar duración a la animación sin agudizar |
| **Reverb ligera** (dar espacio; con moderación) | `sox in.wav out.wav reverb 20` | 20% reverberancia; mejor espacializar en el motor [ver: unity/audio-unity] |

- **`pitch` vs `speed`**: `pitch` cambia solo el tono (algoritmo de time-stretch, puede meter artefactos si te pasas); `speed` cambia tono y duración a la vez (limpio, es "el disco a otra RPM"). Para monstruos y pesos, `speed` abajo suena más orgánico; para afinar un SFX tonal a la tonalidad de la música, `pitch` [ver: sintesis-y-diseno-sonido].
- **Apilar con síntesis**: la grabación aporta textura/realismo; la síntesis aporta el sub-boom, el brillo o la cola que la toma no tiene. Un impacto pro = foley (cuerpo) + click sintético (transient) + sub grave (peso) [ver: sintesis-y-diseno-sonido].
- **Variación**: prefiere pitch ±5–10 % en runtime a hornear muchos WAV, salvo que la variación deba ser deliberada (superficies distintas) [ver: unity/audio-unity].

---

## Voz grabada casera (VO scratch, gritos, esfuerzos)

El PIPELINE de voz (TTS, casting de actores, dirección, procesado de diálogo) vive en [ver: voz-dialogo]. Aquí solo el **craft de grabarla en casa** — sobre todo los *efforts* de combate (golpear, saltar, recibir daño, morir), que un dev graba a sí mismo y son puro game-feel [ver: gamedev/game-feel].

| Aspecto | Regla |
|---|---|
| **Micro** | **Dinámico** (SM58-style) gana en cuarto sin tratar — rechaza el fondo; condensador solo en cuarto callado |
| **Pop filter** | Obligatorio: las plosivas (P/B) mandan un golpe de aire que satura. Un aro con media de nylon sirve |
| **Distancia** | 15–20 cm, ligeramente **off-axis** (no soplar recto al micro) |
| **High-pass** | ~80–100 Hz en post: quita rumble/proximity sin tocar la voz |
| **De-ess** | Domar la sibilancia (S/SH agudas) si el condensador las exagera |
| **Esfuerzos de combate** | Graba tandas: golpe leve / medio / fuerte, salto, esfuerzo, dolor, muerte. **Muchas variantes** por tipo → pool en runtime, evita el efecto "repetido" [ver: unity/audio-unity] |
| **Gritos fuertes** | **Aléjate y baja ganancia** — un grito clipea fácil; mejor grabar bajo en 24-bit y subir en post |
| **Boca seca** | Hidrátate: los "clicks" de boca son la plaga de la VO casera; se editan uno a uno, mejor evitarlos |
| **Room tone de voz** | Graba 10 s de tu silencio también aquí, para reducción de ruido y relleno |

VO scratch (voz temporal para probar timing/tono antes de contratar actor) grábala tú mismo sin culpa: es placeholder [ver: voz-dialogo]. Los efforts, en cambio, a menudo se quedan finales — trátalos con el mismo cuidado que un SFX core.

---

## Reglas prácticas

- [ ] Graba solo lo que da **identidad y no se compra** (foley del personaje, props únicos, voz/efforts); el resto, biblioteca CC0 o síntesis.
- [ ] Presupuesta horas de grabación para los **10–20 sonidos** que el jugador oye mil veces, no para los 200.
- [ ] Piensa el foley por sus 3 categorías: **feet / moves (tela) / specifics (props)** — la capa de "moves" es la que casi todos olvidan.
- [ ] Sustitución nueva: iguala **transient + espectro + textura**; el pitch y el espacio se ajustan después.
- [ ] Micro **cerca (5–20 cm)** antes que subir ganancia; monitorea con auriculares cerrados para oír el fondo.
- [ ] Condensador USB en cuarto callado; **dinámico** en cuarto ruidoso o para voz/gritos.
- [ ] Cardioide para casi todo; graba SECO (ropa/almohadas) y espacializa en el motor, nunca hornees reverb del cuarto.
- [ ] Graba en **24-bit**, picos **−18 a −12 dBFS**, techo absoluto −6; nunca clipear (el clip no se arregla).
- [ ] **Room tone SIEMPRE** (10–30 s por sesión, mismo setup) para perfil de ruido y relleno.
- [ ] **Graba de más** y varía la performance (suave/normal/fuerte); slate verbal antes de cada grupo.
- [ ] Field recording: **windjammer peludo** obligatorio con brisa; trípode contra handling; tomas **largas** (30 s+).
- [ ] Ambiente estéreo: **X/Y** (default seguro) o **M/S** (ancho ajustable + mono perfecto); evita A-B si va a colapsar a mono.
- [ ] Separa la **cama** (loop) de los **one-shots** (disparo aleatorio) al grabar el ambiente.
- [ ] Batch con **SoX** para lotes (normalizar, top-and-tail, fades); GUI para lo puntual [ver: crear-sfx].
- [ ] `noisered` con amount **bajo** (~0.2); pasarse = sonido submarino.
- [ ] Procesar: `speed` para monstruos/pesos (orgánico), `pitch` para afinar tonal; apilar con síntesis [ver: sintesis-y-diseno-sonido].
- [ ] Voz casera: **pop filter**, off-axis, high-pass ~80 Hz; gritos con menos ganancia y más distancia.
- [ ] Efforts de combate: **muchas variantes** por acción → pool en runtime [ver: unity/audio-unity].
- [ ] Toda grabación propia es **CC-limpia** (la hiciste tú), pero regístrala igual en `CREDITS.md` [ver: audio-a-juego].

## Errores comunes

| Error | Antídoto |
|---|---|
| Grabar 200 sonidos a mano y quemar el proyecto | Grabar solo lo de identidad (10–20 core); resto biblioteca/síntesis |
| Buscar el objeto que ya suena "perfecto" | Busca el que tiene el **carácter** (transient/espectro/textura) y ajusta pitch/espacio después |
| Olvidar la capa "moves" (tela) | El roce de ropa llena el movimiento; sin ella el personaje suena "flotando" |
| Subir ganancia en vez de acercar el micro | Ganancia sube señal Y ruido; distancia corta sube solo la señal |
| Condensador sensible en cuarto ruidoso | Dinámico cercano (rechaza fondo) o tratar el cuarto (clóset/ropa) |
| Grabar "al tope" y clipear un transiente | 24-bit, picos −18 a −12 dBFS, techo −6; el clip no se arregla, se regraba |
| No grabar room tone | 10–30 s por sesión: sin él no hay perfil de reducción de ruido ni relleno |
| Reverb del cuarto horneada en la toma | Grabar seco y espacializar en el motor [ver: unity/audio-unity] |
| Ambiente exterior arruinado por viento | Windjammer peludo obligatorio; el low-cut solo no basta |
| Ambiente A-B que colapsa a mono con fase rara | X/Y o M/S (coincidentes, mono-safe) para audio de juego |
| Cama y one-shots grabados juntos en una toma | Sepáralos: la cama va en loop, los one-shots se disparan aleatorios |
| `noisered` con amount alto → voz submarina | Amount ~0.2; si hace falta más, regraba más limpio |
| Grito clipeado en la voz | Alejarse + bajar ganancia; grabar bajo en 24-bit y subir en post |
| Clicks de boca por sequedad en la VO | Hidratarse; editar uno a uno es más lento que evitarlos |
| Un solo effort de golpe repetido (metralleta) | Muchas variantes por acción + pool/pitch en runtime [ver: unity/audio-unity] |

## Fuentes

- **SoX (Sound eXchange)** — man page oficial (`sox.1`, fuente en github.com/chirlu/sox) — sintaxis **verificada línea por línea** contra `sox --help-effect` en esta pasada: `noiseprof [profile]` / `noisered [profile [amount]]` (amount 0–1, default 0.5); `pitch [-q] shift` (shift en **cents**, 100 = 1 semitono); `tempo [-q] factor` (WSOLA, cambia velocidad no pitch); `speed factor[c]` (pitch + tempo); `gain [-n] [gain-dB]` y `norm [dB-level]` (alias de `gain -n`); `trim {position}`; `silence [-l] above-periods duration threshold`; `fade [type] in-length [stop-pos(0=fin) [out-length]]`; `reverb [reverberance ...]`; `remix` / `channels` / `rate`. Además **ejecutado end-to-end con SoX real** (brew, macOS) sobre un WAV sintético: se detectó y corrigió que `silence` + `fade` (stop 0) encadenados en una sola invocación fallan (`audio length is neither known nor given`) — corregido a dos invocaciones en la tabla de arriba; y que `mkdir -p` debe preceder al lote o falla `can't open output file`. Verificado 2026-07-21.
- **Foley (sound design)** — Wikipedia (en.wikipedia.org/wiki/Foley_(filmmaking)) — nombrado por Jack Foley; **tres categorías estándar Feet / Moves / Specifics** (verificado en el índice y cuerpo del artículo); "foley pits" para pasos, artistas "Foley walkers/steppers"; tricks clásicos (coco = cascos, corn starch = nieve, cellophane = fuego). Verificado 2026-07-21.
- **Cadena de señal, patrones polares (cardioide/omni/figura-8/supercardioide), condensador vs dinámico, phantom +48V, proximity effect, regla 3:1, gain staging −18/−12 dBFS y headroom en 24-bit** — práctica estándar de ingeniería de grabación (audio engineering consolidado). NO re-verificado contra una fuente única en esta pasada por agotamiento del presupuesto de WebSearch y caída temporal de WebFetch — son hechos de dominio establecidos; tratar los valores concretos de nivel como convención (no norma legal).
- **Técnicas estéreo de campo (X/Y coincidente, ORTF 17 cm/110°, Mid-Side decodificado M±S, A-B espaciado, Blumlein) y su compatibilidad mono** — práctica estándar de microfonía estéreo. Mismos límites de verificación que el punto anterior; los ángulos/distancias de ORTF son la convención documentada del método.
- **Grabadoras portátiles (Zoom H-series, Tascam DR-series) y protección de viento (foam windscreen / windjammer "dead cat")** — categorías de equipo de field recording de conocimiento general; NO se citan modelos/precios concretos (no verificados en esta pasada) — verificar specs/precio vigente antes de recomendar una compra.
- **Reparto con el resto del bloque**: base de foley/edición GUI/licencias en [ver: crear-sfx]; acabado/loops/entrega en [ver: audio-a-juego]; síntesis y layering en [ver: sintesis-y-diseno-sonido]; pipeline de voz en [ver: voz-dialogo]; teoría de ambiente/adaptividad en [ver: gamedev/audio]; implementación (pool, variación, mixer) en [ver: unity/audio-unity].
