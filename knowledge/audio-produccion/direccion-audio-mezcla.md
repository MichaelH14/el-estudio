# Dirección de audio, mezcla y coordinación del soundscape

> **Cuando cargar este archivo:** cuando ya tienes SFX, música, voz y ambiente producidos y hay que **coordinarlos como una sola mezcla en vivo** — repartir el espectro para que no se tapen, decidir qué manda en cada momento, poner ducking, armar el árbol de buses, fijar loudness (LUFS) y verificar la mezcla jugando en varios dispositivos. Es la capa de "director de audio + ingeniero de mezcla" del juego. NO repite la teoría de funciones/adaptividad/silencio ([ver: gamedev/audio]), la implementación en motor ([ver: unity/audio-unity]) ni la normalización por-asset ([ver: audio-a-juego]) — los cruza y aporta la coordinación global.

## 1. El juego es una mezcla en vivo, no una carpeta de sonidos

La diferencia entre un juego que "suena a juego" y uno que suena a demo es que el primero está **mezclado**: alguien decidió, para cada instante posible, qué se oye claro, qué queda de fondo y qué se calla. En un disco esa decisión se toma una vez sobre una línea de tiempo fija; en un juego la mezcla es **dinámica e impredecible** — el jugador dispara el orden y la densidad de los sonidos. Por eso el trabajo no es "mezclar 40 clips", es **diseñar el sistema que los mezcla en tiempo real**.

| Mentalidad de "sonidos sueltos" | Mentalidad de dirección/mezcla |
|---|---|
| Cada asset a volumen "que se oiga bien solo" | Cada asset a su nivel **relativo al resto en el peor caso de densidad** |
| Se prueba cada sonido en aislado | Se prueba **jugando**, con la escena más cargada de sonidos a la vez |
| Todo compite por el mismo espacio | Cada capa tiene **su banda de frecuencia y su momento** asignados |
| "Súbele el volumen" arregla todo | Se resuelve por **espectro, prioridad y ducking**, no solo por ganancia |

Regla base: **si tienes que subir un sonido para oírlo, primero pregúntate qué lo está tapando.** Casi siempre la respuesta es otra cosa ocupando su misma banda, no falta de volumen (§3, masking).

## 2. El soundscape: las cinco capas y su reparto

Todo el audio de un juego cae en cinco capas. Coordinar = darle a cada una un rol, una banda de frecuencia tendencial, un comportamiento dinámico y una prioridad, para que convivan sin embarrarse.

| Capa | Rol (información que da) | Banda dominante | Comportamiento | Prioridad de mezcla |
|---|---|---|---|---|
| **Voz / diálogo** | Narrativa e instrucción; SIEMPRE inteligible | 300 Hz–4 kHz (fundamental + consonantes) | Comprimida, estable; **duckea todo lo demás** | Máxima [ver: voz-dialogo] |
| **SFX de gameplay** | Feedback, amenaza, causa-efecto | Ancho; punch 80–250 Hz + ataque 2–5 kHz | Transitorio, corto; picos altos | Alta (lo crítico nunca se culla) |
| **Música** | Emoción, tono, ritmo del momento | Ocupa TODO el espectro (por eso hay que tallarle hueco) | Sostenida; cede ante voz y SFX crítico | Media (adaptable) [ver: musica-adaptativa] |
| **Ambiente** | Presencia del mundo, "esto está vivo" | Extremos: sub-rumble + aire agudo; **evita los medios de la voz** | Cama sostenida + one-shots | Baja (base culleable) |
| **UI** | Confirmación de interacción | Medios-agudos 1–6 kHz, sin sub | Corto, seco, el más suave del juego | Baja pero **nunca tapada** (es feedback) |

- La convivencia se resuelve en tres ejes que son las secciones siguientes: **espectro** (§3, quién ocupa qué frecuencia), **prioridad** (§4, quién manda cuando chocan en el tiempo) y **niveles/buses** (§7, la ganancia relativa base).
- Diegético vs no-diegético afecta el reparto: la voz de un NPC en el mundo es 3D y se atenúa; la voz del narrador es 2D y va por encima. [ver: gamedev/audio] cubre la distinción; aquí importa que **cada capa decide 2D/3D** (§9).

## 3. El presupuesto del espectro de frecuencias (la clave que casi nadie aplica)

El espectro audible (~20 Hz–20 kHz) es un **recurso finito y compartido**. Dos sonidos que viven en la misma banda pelean: el más fuerte **enmascara** al otro y lo vuelve inaudible aunque técnicamente esté sonando. Mezclar bien es **repartir el espectro** para que lo importante siempre tenga su banda despejada.

### Masking (por qué subir volumen no arregla nada)

- **Masking simultáneo (de frecuencia):** un sonido fuerte hace inaudible a otro más flojo en una frecuencia **cercana** — caen en el mismo "critical band" del oído y se perciben como uno (Wikipedia, *Auditory masking*: un pico de 1 kHz tapa un tono de 1.1 kHz por debajo). **Las frecuencias graves enmascaran una banda más ancha que las agudas** → el sub de la música y de una explosión pelean con TODO lo que tenga cuerpo.
- **Masking temporal:** un sonido fuerte tapa lo que ocurre ~20–100 ms antes y después de él. Un impacto grande sepulta los sonidos flojos que caen pegados en el tiempo.
- **Implicación de mezcla:** si un SFX crítico no se oye en combate, casi nunca es falta de volumen; es que la música o el ambiente ocupan su banda. La solución es **tallar** (carve), no subir.

### El mapa de bandas (referencia de reparto)

Rangos y carácter perceptual estándar (teachmeaudio, *Audio Spectrum*). Úsalo como plano de reparto:

| Banda | Hz | Carácter | Dueño típico en un juego | Peligro |
|---|---|---|---|---|
| **Sub-bass** | 20–60 | Se siente más que se oye; poder | **UN solo dueño** por momento (kick/drone de música **o** explosión, no los dos) | Suma de subs = clip y "barro" que no se oye pero come headroom |
| **Bass** | 60–250 | Cuerpo, fundamento rítmico | Cuerpo de música + punch de impactos | Boomy si se acumula |
| **Low-mid** | 250–500 | La **"zona de barro"** | Casi nadie la necesita entera | Acumulación aquí = mezcla turbia; recortar en capas que no la usan |
| **Mid** | 500 Hz–2 kHz | Cuerpo de voz e instrumentos | Voz, leads, motores | Saturarla = sonido "de lata", fatiga |
| **Upper-mid** | 2–4 kHz | **Presencia e inteligibilidad**; el oído es hipersensible | **Voz + ataque de SFX crítico** — la banda más peleada | Exceso a 3 kHz = fatiga auditiva rápida |
| **Presence** | 4–6 kHz | Definición, "clic", claridad | Transientes de UI, detalle de SFX | Chillón/irritante si se abusa |
| **Brilliance** | 6–20 kHz | Aire, brillo, sparkle | Aire del ambiente, shimmer | Hiss y fatiga si se sube de más |

### Reglas de reparto espectral (accionables)

- **High-pass todo lo que no necesite graves.** UI, la mayoría de SFX medios, capas de música que no son el bajo → HPF para liberar el sub. Punto de partida (heurística, ajustar de oído): UI y SFX agudos HPF ~200–300 Hz; SFX medios ~80–120 Hz; capas de música no-bajo ~30–40 Hz. El bajo/kick y las explosiones son los únicos con derecho al sub.
- **Un dueño del sub por momento.** Si la música tiene un drone grave sostenido y encima entra una explosión con sub, la explosión pierde impacto. O bajas el sub de la música cuando hay explosiones (ducking espectral / sidechain, §5), o la música no vive en el sub.
- **Protege 2–4 kHz para la voz y el feedback crítico.** Es donde se entiende el diálogo y donde el oído localiza el ataque de un sonido. Si la música brilla mucho ahí, **tállale un pocket** (un dip de EQ estático o dinámico en la música en esa banda) para que la voz encaje sin subir su volumen. Esto es *complementary/carve EQ*: no subes A, bajas B en la banda de A.
- **Limpia la zona de barro (250–500 Hz).** Un recorte suave ahí en música y ambiente aclara toda la mezcla sin que se note qué cambió.
- **Suma los subs mentalmente.** Diez sonidos con energía en 20–60 Hz = un lodo grave que come headroom (§8) y no aporta nada audible. Mono-summea los graves (todo lo <120 Hz al centro) para que no haya cancelaciones de fase en mono.

## 4. Jerarquía y prioridad: quién manda cuando chocan en el tiempo

El espectro reparte "quién ocupa qué frecuencia"; la prioridad reparte "quién gana cuando dos cosas importantes suenan a la vez y no caben". La regla NO es física ("el más fuerte gana") sino **importancia de gameplay** — el estándar Overwatch (sistema de importancia 0–120, 4 buckets, solo 1 sonido en High) está en [ver: gamedev/audio]; la implementación (`AudioSource.priority` 0–256, 0 = máxima prioridad, Max Real Voices, virtualización) en [ver: unity/audio-unity §4].

Orden de mando por defecto (de arriba abajo gana el de arriba):

| Rango | Qué es | Qué le hace a lo de abajo |
|---|---|---|
| 1. **Voz / diálogo** | Instrucción, narrativa, callouts | Duckea música y ambiente (§5); nunca se culla |
| 2. **SFX crítico de gameplay** | Amenaza, daño recibido, evento que exige reacción | Puede duckear música brevemente; prioridad de voz alta |
| 3. **SFX de feedback** | Confirmación de acción propia (golpe, pickup) | Compite por voces; variación evita fatiga [ver: crear-sfx] |
| 4. **Música** | Emoción/tono | Cede banda y nivel ante 1–2; se adapta [ver: musica-adaptativa] |
| 5. **Ambiente + UI cosmético** | Cama del mundo, adornos | Primero en cullearse cuando hay caos |

- **Límite de voces por evento + cooldown:** que 30 monedas no disparen 30 voces (patrón Goose Game). Se decide aquí (diseño) y se implementa en el motor/middleware. [ver: gamedev/audio], [ver: unity/audio-unity §4].
- **Voice limiting del diálogo:** solo una línea de voz "principal" a la vez; si entra otra, corta o encola la anterior. Dos NPCs hablando encima = ninguno se entiende.
- **La regla de oro:** define 3–4 niveles de prioridad, **garantiza que lo crítico SIEMPRE se oiga** y acepta silenciar lo cosmético en el caos. En un juego chico esto es un enum de prioridad + límites de instancia, no el sistema de Overwatch.

## 5. Ducking / sidechain: hacer sitio automáticamente

Ducking = bajar automáticamente un bus cuando otro necesita el espacio. Mecánicamente es **sidechain compression**: la señal de control (key) de un canal reduce la ganancia de otro (Wikipedia, *Dynamic range compression*: el micro del DJ va al sidechain del compresor de la música → cuando habla, la música baja). Parámetros: **threshold** (nivel del key que dispara), **ratio** (cuánto baja por dB sobre threshold), **attack/release** (velocidad de bajada y de retorno), **makeup gain**.

Implementación concreta en Unity (efecto **Duck Volume** en el bus Music + **Send** desde el bus Voice) está en [ver: unity/audio-unity §3]; en FMOD/Wwise es nativo [ver: middleware-fmod-wwise]. Aquí lo que decides es **el qué, el cuánto y el cuándo**:

| Quién duckea | A quién | Cantidad (punto de partida) | Attack / Release | Nota |
|---|---|---|---|---|
| Voz / diálogo | Música + ambiente | −6 a −12 dB | rápido (~50–100 ms) / lento (~400–600 ms) | La voz manda; retorno lento = natural |
| Voz tutorial / narrador | Música | −8 a −10 dB | ~100 ms / ~500 ms | Que se entienda SIEMPRE, no negociable |
| SFX crítico (golpe clave, boss) | Música | −3 a −6 dB, breve | rápido / ~300 ms | Duck corto para dar impacto, no para bajar la música un rato |
| Stinger | Ambiente | −4 a −8 dB | ~50 ms / ~400 ms | El stinger entra por encima [ver: musica-adaptativa] |

- Cantidades y tiempos son **heurística de partida** (coherente con [ver: gamedev/audio]); ajustar de oído. Lo no negociable: **el diálogo se entiende siempre**.
- **Release lento** (400–600 ms) para que la música "respire" de vuelta sin salto; **attack rápido** para que la voz no arranque tapada.
- **Sidechain como estilo, no solo como utilidad:** duckear rítmicamente la música con el kick (el "pumping" de la electrónica) o con cada paso del jugador es una firma sonora válida — decisión de dirección, no accidente.
- **Ducking espectral (avanzado):** en vez de bajar todo el bus, bajar solo la banda que estorba (dynamic EQ / multiband sidechain): la música pierde solo 2–4 kHz cuando hay voz y conserva su cuerpo. Middleware o EQ dinámico; en Unity nativo no viene de fábrica.

## 6. Mezcla automática por rango dinámico (HDR): la alternativa al ducking manual

En vez de encadenar duckings a mano, algunos motores mezclan por **rango dinámico**, imitando el HDR visual: autoras cada sonido con su **loudness real** (un disparo a nivel altísimo, unos pasos a nivel bajísimo) y el sistema aplica una **ventana** que sigue al sonido más fuerte del momento; lo que cae por debajo del piso de la ventana se atenúa o se culla solo. Resultado: **los sonidos fuertes duckean a los flojos automáticamente**, sin cablear cada relación. Es el **sistema HDR de Wwise** (popularizado por DICE en *Battlefield 3*).

- Ventaja: escala a cientos de sonidos sin un grafo de ducking manual; el contraste dinámico (silencio→explosión) es enorme.
- Costo: exige autorar loudness **absoluto y consistente** por sonido; un asset mal nivelado rompe la ventana (un paso demasiado alto tapa todo).
- ⚠️ **Defaults exactos de la ventana (ancho en dB, threshold, release) NO VERIFICADOS en esta pasada** — la doc de Audiokinetic bloquea el fetch; describir el concepto es seguro, pero confirmar valores en la doc oficial antes de configurarlo. Detalle de middleware en [ver: middleware-fmod-wwise].
- Para un juego chico: **no lo necesitas**. El árbol de buses + ducking manual de §5 y §7 cubre todo. HDR paga cuando hay un sound designer dedicado y cientos de fuentes.

## 7. Arquitectura de buses y gain staging (el mezclador del juego)

La mezcla vive en un **árbol de buses/grupos**: cada sonido sale por su grupo, los grupos suben hasta el Master, y en cada grupo cuelgas efectos, ducking y el control de volumen del jugador. Estructura mínima:

```
Master
├─ Music      (HPF suave, compresión ligera, Duck Volume ← Voice)
├─ SFX        (sub-buses: SFX_Player / SFX_World / SFX_UI)
├─ Voice      (compresión + de-ess, Send → Duck de Music)
├─ Ambient    (HPF, nivel bajo, cama del mundo)
└─ UI         (2D, el más suave, nunca duckeado)
```

- **Buses vs VCA:** un **bus** procesa la señal (suma, efectos, medición); un **VCA** solo controla ganancia de un grupo sin re-rutear el audio (útil para "baja todo el SFX del juego" sin meter un punto de procesado). FMOD y Wwise distinguen los dos [ver: middleware-fmod-wwise]; el AudioMixer de Unity trabaja con grupos-bus [ver: unity/audio-unity §3].
- **Return / send buses:** la reverb no se pone por sonido, se pone **una vez** en un return bus y cada fuente le manda una cantidad (send). Un solo reverb "cueva" alimentado por sends = coherencia + CPU baja (§9).
- **Niveles relativos de partida** (heurística, no estándar; el 0 dB del bus = ganancia unidad, se mezcla desde ahí a la baja):

| Bus | Nivel relativo de arranque | Razón |
|---|---|---|
| Voice | referencia (el más alto que debe entenderse) | Ancla de la mezcla |
| SFX crítico | ~igual o −1 a −2 dB bajo Voice | Feedback debe leerse |
| SFX feedback | −3 a −6 dB | Presente sin cansar |
| Music | −6 a −12 dB bajo la voz | Acompaña, no tapa |
| Ambient | −12 a −20 dB | Cama, se siente sin notarse |
| UI | −6 a −10 dB, seco | Confirma sin molestar |

- **Gain staging:** autora los assets con **headroom** (picos ~9–12 dB bajo el máximo, [ver: audio-a-juego]) y mezcla **hacia abajo** desde ahí, no subiendo todo hasta clip. Si el Master está clippeando, el problema es que subiste todo; baja, no limites a ciegas.
- **Sliders del jugador:** Master / Música / SFX / (Voz) como mínimo — es mezcla Y accesibilidad. El fader trabaja en dB logarítmicos: `Log10(slider)*20`, slider 0.0001–1, persistir el valor lineal [ver: unity/audio-unity §3]. Nunca un lerp lineal −80→0 dB (a mitad de slider ya estás mudo).
- **Snapshots / estados de mezcla:** menú, exploración, combate, "bajo el agua", pausa — cada uno es un snapshot del mezclador (volúmenes + filtros) al que transicionas [ver: unity/audio-unity §3]. Un exposed param lo controla `SetFloat` **o** los snapshots, nunca ambos.

## 8. Loudness y rango dinámico: que nada reviente ni se pierda

Dos problemas distintos: **loudness** (qué tan alto se percibe el juego en promedio, para que no sea ni más flojo ni más fuerte que lo demás que el jugador oye) y **rango dinámico** (cuánta distancia hay entre lo más flojo y lo más fuerte — el arma del impacto).

### Loudness: medir en LUFS, no en picos

- **LUFS/LKFS** (Loudness Units Full Scale) = medición de loudness **percibido**, K-weighted, según **ITU-R BS.1770**. 1 LU = 1 dB. Es lo que hay que medir; el pico (dBFS) no dice qué tan alto se **oye** algo.
- **Anclas de broadcast:** **−23 LUFS** integrado (EBU R128, ±0.5 LU, verificado) y **−24 LKFS** (ATSC A/85, US — ampliamente citado, no fetcheado esta pasada). Son la referencia de "nivel neutro" de la que parten cine y TV.
- **True peak máximo −1 dBTP** (EBU R128): deja margen para que el limitador y la conversión D/A no clippeen por picos inter-sample. **Nunca dejes el pico en 0 dBFS.**
- **Gating** (EBU R128): la medida integrada ignora silencios (gate absoluto −70 LUFS, relativo −10 LU) — por eso medir un juego con mucho silencio da un número engañoso; medir sobre gameplay real representativo.
- **Juegos vs broadcast:** no hay un mandato universal como en TV (existe una recomendación específica de la AES para juegos, **ASWG-R001**, anclada cerca de los niveles de broadcast — **valor exacto NO VERIFICADO esta pasada**; usar −23/−24 como referencia y **la doc de certificación de la plataforma como autoridad final**). Los juegos **quieren más rango dinámico** que la TV (el silencio da peso al estruendo), así que suelen mezclarse con un integrado similar pero **picos más vivos**.
- **Móvil apunta más alto** (convención, ~−16 a −18 LUFS): compite en altavoces diminutos y contra otras apps; menos rango dinámico, más nivel medio. Marcar como heurística, no estándar. [ver: movil/unity-movil-graficos] para la diversidad de hardware.
- **Soundtrack en streaming:** si publicas el OST, las plataformas normalizan (referencias ampliamente citadas: Spotify/YouTube ~−14 LUFS, Apple Music ~−16 LUFS) — masterizar el álbum aparte del in-game, que tiene otra meta.

### Rango dinámico: el arma del impacto

- El error del "loudness war" (aplastar todo a máximo volumen) mata los juegos: si todo está fuerte, nada golpea. **El rango dinámico es lo que hace que una explosión se sienta.** Necesitas los momentos flojos (§11, silencio) para tener los fuertes.
- **Compresión con intención:** comprime la voz (inteligibilidad constante) y el Master ligeramente (pegamento), NO el juego entero. Un limitador en el Master como **red de seguridad** contra clips imprevistos (varios sonidos coincidiendo), no como herramienta de subir volumen.
- **Herramienta de medición:** un medidor LUFS (p. ej. **Youlean Loudness Meter**, versión gratis) capturando la salida del juego durante gameplay real. Sin medir, "suena bien" es a qué volumen tengas el monitor ese día.

## 9. Audio espacial dentro de la mezcla

La posición es parte de la mezcla, no un adorno. Lo posicional bien hecho **descongestiona**: dos sonidos en lados opuestos ya no pelean aunque compartan banda.

- **Reparto 2D/3D:** UI, música, stingers y narrador en **2D** (sin posición); todo lo que pasa en el mundo en **3D** con atenuación por distancia y paneo. En Unity es `spatialBlend`; curvas de atenuación por tipo de sonido [ver: unity/audio-unity §1].
- **Pan law:** un sonido centrado llega a los dos altavoces y suena ~3–6 dB más fuerte que uno paneado a un lado si no se compensa. Los motores aplican **constant-power panning** (Wikipedia, *Panning*): ley de **−3 dB** en el centro si la salida queda estéreo, **−6 dB** si se va a colapsar a mono, **−4.5 dB** de compromiso. Implicación: **no llenes el centro** — la voz y el kick van al centro; espárcelos, deja SFX del mundo a los lados.
- **Distancia como mezcla:** la atenuación por distancia + un low-pass con la lejanía es un **fader automático gratis** — las cosas lejanas se quitan solas del camino de las cercanas. Curvas por tipo: un disparo se oye a 100 m, un paso a 10 m [ver: gamedev/audio], [ver: unity/audio-unity §1].
- **Reverb por zona (send-return):** una reverb por tipo de espacio (cueva, sala, exterior) en un return bus; cada fuente manda su send. Cambiar de zona = cambiar el snapshot de reverb con crossfade, nunca de golpe. La reverb **une** las capas (todas suenan "en el mismo cuarto") — es pegamento de cohesión (§10).
- **Test de mono:** colapsa la mezcla a mono y escucha. Lo que desaparece tenía cancelación de fase (típico en estéreo mal manejado o graves fuera de fase). Muchos altavoces de móvil y de TV son casi-mono — si se cae en mono, se cae en el hardware del jugador.

## 10. Identidad sonora: que todo suene "del mismo mundo"

La dirección de audio es a la mezcla lo que la dirección de arte es a los píxeles [ver: gamedev/arte-direccion]: una decisión de **coherencia**. SFX, música, voz y UI tienen que sonar como si vinieran del mismo universo, no como una carpeta de descargas.

- **La "biblia sonora":** un doc corto que fija la paleta — ¿realista o estilizado? ¿orgánico o sintético? ¿limpio o sucio/lo-fi? ¿qué era emocional (retro chiptune, orquestal oscuro, synth-metal como DOOM)? Todos los assets se juzgan contra ese doc.
- **Cadena de procesado compartida:** pasar todo el SFX por un mismo carácter (una pizca de la misma saturación, la misma reverb de mundo, el mismo rango de brillo) hace que sonidos de fuentes distintas (síntesis, foley, biblioteca) suenen hermanos. Bibliotecas stock reconocibles matan la identidad; procesarlas encima las integra [ver: crear-sfx].
- **Tonalidad compartida:** los SFX tonales (pickups, UI, alertas) afinados a la tonalidad de la música evitan disonancia accidental y hacen que el juego "cante junto" [ver: teoria-musica-juegos], [ver: crear-sfx].
- **Tracks de referencia:** elige 2–3 juegos cuyo audio quieres emular y A/B contra ellos durante toda la mezcla. "¿Sueno tan claro/impactante/cohesivo como esto?"
- **Test del mundo:** reproduce un SFX cualquiera, un fragmento de música y una línea de voz seguidos. ¿Parecen del mismo juego? Si uno canta fuera de tono, sobra procesado o falta.

## 11. El silencio como decisión de mezcla

El silencio es una herramienta de la mezcla, no la ausencia de trabajo. La teoría (cuándo callar, el procedimiento de 5 pasos, ambiente≠silencio) está en [ver: gamedev/audio]; aquí el ángulo de mezcla:

- **El rango dinámico necesita el suelo para tener techo.** Sin momentos flojos, no hay momentos fuertes. Bajar la música y el ambiente antes de un clímax **fabrica headroom** para que el golpe siguiente se sienta enorme sin subir su volumen.
- **Dropout como telégrafo:** cortar el audio un instante (o filtrarlo a un tinnitus tras una explosión) es una decisión de mezcla que señala una ventana de gameplay o un cambio de estado.
- **"Silencio" casi siempre = ambiente sin música.** La cama del mundo sostiene el hueco; la música entra como **evento**. La música que nunca calla no comunica nada (lección Goose Game, [ver: gamedev/audio]).

## 12. Mezclar en contexto y el checklist final

La mezcla no se hace en aislado ni una sola vez: se hace **jugando**, en el peor caso, y en el hardware real del jugador.

- **Mezcla jugando, no soleando.** Un sonido perfecto en solo puede desaparecer o reventar en la escena densa real. Mezcla la escena más cargada de sonidos simultáneos que el juego permita.
- **Nivel de monitoreo consistente.** La percepción de graves y agudos cambia con el volumen (curvas de igual sonoridad / Fletcher-Munson): a volumen alto todo suena más "lleno". Mezcla siempre a un nivel moderado y **fijo** (la misma posición del knob cada sesión) y verifica también bajito y fuerte. Mezclar fuerte engaña: subes de más los graves.
- **Traducción a dispositivos** — probar en ≥3 salidas, la mezcla debe funcionar en todas:

| Salida | Qué revela | Riesgo típico |
|---|---|---|
| Auriculares | Detalle, paneo, cola de reverb, ruido de fondo | Todo suena "bien" y te engañas |
| Altavoces de TV / monitor | Balance medio real | Graves inflados que ahí no están |
| **Altavoz de móvil** | Casi-mono, **sin graves**, banda estrecha | El sub desaparece; si el impacto vivía solo en el sub, **no existe** en móvil |
| Bluetooth / carro | Latencia, compresión del codec | Sync de ritmo, transientes blandos |

  El altavoz de móvil es el juez más duro: **el punch tiene que vivir también en los medios** (80–250 Hz + ataque en 2–5 kHz), no solo en el sub — lección DOOM, mezclar para el hardware real [ver: gamedev/audio], [ver: movil/unity-movil-graficos].

### Checklist de la mezcla final

- [ ] Reproducir la escena más densa del juego y confirmar que **la voz y el SFX crítico se entienden** ahí.
- [ ] Medir LUFS integrado sobre gameplay real; true peak ≤ **−1 dBTP**; sin clips en el Master.
- [ ] Pasar por auriculares + TV + **altavoz de móvil** + Bluetooth.
- [ ] Colapsar a **mono** y confirmar que nada crítico desaparece.
- [ ] Recorrer los estados/snapshots (menú↔juego↔combate↔pausa↔bajo agua) y sus transiciones.
- [ ] Mover cada slider del jugador (Master/Música/SFX/Voz) a 0, medio y máximo; verificar que ninguno rompe la mezcla.
- [ ] A/B contra los tracks de referencia: ¿tan claro e impactante como ellos?

## Reglas prácticas

- [ ] Trata el juego como una **mezcla en vivo**: cada asset a su nivel relativo en el peor caso de densidad, no "que se oiga bien solo".
- [ ] Antes de subir un sonido, pregunta **qué lo tapa** — casi siempre es masking de banda, no falta de volumen.
- [ ] Reparte el espectro: **HPF todo lo que no necesite graves**, un solo dueño del sub por momento, protege 2–4 kHz para voz y feedback crítico.
- [ ] Talla huecos (carve EQ): baja B en la banda de A en vez de subir A. Limpia la zona de barro 250–500 Hz.
- [ ] Mono-summea los graves (<~120 Hz al centro) para evitar cancelación de fase en mono.
- [ ] Prioridad por **importancia de gameplay**, no por volumen: voz > SFX crítico > feedback > música > ambiente/UI. Lo crítico nunca se culla.
- [ ] Ducking sobre la música cuando entra voz (−6 a −12 dB, release ~400–600 ms); **el diálogo se entiende siempre**.
- [ ] Árbol de buses Master → Music/SFX/Voice/Ambient/UI; reverb en **return bus** por sends, no por sonido.
- [ ] Gain staging: autora con headroom (~9–12 dB), mezcla **hacia abajo**; limitador en Master solo como red de seguridad.
- [ ] Sliders del jugador en dB logarítmicos (`Log10(slider)*20`), persistir valor lineal; mínimo Master/Música/SFX.
- [ ] Estados de mezcla por **snapshots** con transición, no cortes; un param lo controla snapshot **o** SetFloat, no ambos.
- [ ] Mide **LUFS** sobre gameplay real (ancla −23/−24); true peak ≤ **−1 dBTP**; nunca picos a 0 dBFS.
- [ ] Preserva **rango dinámico** (no aplastes todo a máximo): el silencio y lo flojo son lo que da impacto a lo fuerte.
- [ ] Cohesión: biblia sonora + cadena de procesado compartida + reverb de mundo común; SFX tonales afinados a la música.
- [ ] Mezcla **jugando**, a nivel de monitoreo fijo y moderado; verifica bajito y fuerte.
- [ ] Prueba en ≥3 salidas incluyendo **altavoz de móvil**; el punch debe vivir también en los medios, no solo en el sub.
- [ ] Corre el **checklist final** (§12) antes de ship.

## Errores comunes

| Error | Antídoto |
|---|---|
| "No se oye" → subir el volumen | Casi siempre es masking: talla la banda del que estorba (§3), no subas ganancia |
| Todos los graves compitiendo (mezcla turbia, come headroom) | HPF por capa; un solo dueño del sub por momento; mono-summear <120 Hz |
| Música que pelea con la voz en 2–4 kHz | Ducking + **carve EQ** en la música en esa banda; no subir la voz |
| Mezclar cada sonido en solo | Mezclar **jugando** la escena más densa; el solo miente |
| Aplastar todo a máximo volumen ("loudness war") | Preservar rango dinámico; medir LUFS, no picos; el impacto necesita momentos flojos |
| Dejar picos en 0 dBFS | True peak ≤ −1 dBTP; limitador de red de seguridad en Master |
| Reverb puesta por sonido | Un return bus por tipo de espacio + sends; une y ahorra CPU |
| Todo al centro del estéreo | Voz/kick al centro, mundo a los lados; respetar el pan law (−3/−6 dB) |
| Mezclar solo con auriculares a volumen alto | Nivel de monitoreo fijo y moderado; probar TV, **móvil**, Bluetooth, y mono |
| Punch que solo vive en el sub | Que el impacto tenga cuerpo en 80–250 Hz + ataque en 2–5 kHz (lección DOOM) |
| SFX de bibliotecas que no pegan entre sí | Cadena de procesado compartida + reverb de mundo común = suenan hermanos |
| Dos NPCs hablando encima | Voice limiting: una línea principal a la vez; corta o encola |
| Configurar HDR de Wwise con valores inventados | Verificar defaults en doc oficial (no fetcheable esta pasada); para juego chico, buses + ducking manual bastan |

## Fuentes

- **EBU R 128 / EBU Tech 3341** (Wikipedia; European Broadcasting Union) — target −23 LUFS ±0.5, LU vs LUFS, LRA, true peak máx −1 dBTP, gating −70/−10 LU, base ITU-R BS.1770. Verificado (fetch).
- **Audio Spectrum** — Teach Me Audio — las siete bandas de frecuencia con rangos en Hz (sub-bass 20–60 … brilliance 6–20 kHz), su carácter perceptual y la zona de barro 250–500 Hz. Verificado (fetch).
- **Auditory masking** (Wikipedia) — masking simultáneo (de frecuencia) vs temporal, critical bands, por qué el grave enmascara banda más ancha; base psicoacústica del reparto espectral. Verificado (fetch).
- **Dynamic range compression / sidechain** (Wikipedia) — mecánica del ducking: key signal al sidechain, threshold/ratio/attack/release/makeup, caso música-bajo-voz. Verificado (fetch).
- **Panning (audio)** (Wikipedia) — constant-power panning y pan law (−3 / −4.5 / −6 dB en el centro), phantom center; base del uso del estéreo en la mezcla. Verificado (fetch).
- **ITU-R BS.1770** — recomendación de medición de loudness (K-weighting) que sustenta LUFS/LKFS; referida vía EBU R128 (no fetcheada directa esta pasada).
- **ATSC A/85** (broadcast US, −24 LKFS) y **AES ASWG-R001** (recomendación de loudness para juegos) — citados como anclas de referencia; **valores exactos de ASWG-R001 NO VERIFICADOS esta pasada** — confirmar en la fuente antes de fijar un target.
- **Wwise HDR System** (Audiokinetic; origen DICE/*Battlefield 3*, GDC) — concepto de mezcla por ventana de rango dinámico; **defaults exactos NO VERIFICADOS** (doc de Audiokinetic bloquea el fetch, HTTP 403).
- **FMOD Studio — Mixing** (fmod.com/docs) — buses/VCA/return buses/snapshots/sidechain; página no extraíble por WebFetch (render JS). Detalle de middleware cruzado a [ver: middleware-fmod-wwise].
- **Cross-refs internas** — [ver: gamedev/audio] (Overwatch: importancia 0–120 y 4 buckets; silencio; ambiente; ducking heurístico), [ver: unity/audio-unity] (AudioMixer, Duck Volume+Send, snapshots, slider log, spatialBlend/rolloff, priority/voces), [ver: audio-a-juego] (headroom por-asset, true peak, mono/estéreo, loops), [ver: gamedev/arte-direccion] (dirección como coherencia). Youlean Loudness Meter mencionado como medidor LUFS gratuito de referencia (no fetcheado esta pasada).
