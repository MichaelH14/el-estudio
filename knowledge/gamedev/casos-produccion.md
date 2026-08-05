# Diez producciones reales: qué salió mal y qué robarles

> **Cuándo cargar este archivo:** al planificar un proyecto y necesitar precedentes reales en vez de teoría — estimar presupuesto o duración, decidir si financiar por crowdfunding, negociar un retraso, evaluar cambiar de motor o de herramientas a mitad, entender por qué un juego "no cuaja" tras años de trabajo, o buscar un mecanismo concreto de decisión (cómo desempatar entre dos directores, cómo priorizar en crunch, cómo medir si el combate es divertido). El proceso genérico está en [ver: produccion-proceso] y el ritmo del dev solo en [ver: pipeline/produccion-solo-dev]; aquí están los **casos con nombre, cifra y cita**.

Fuente única de este archivo: *Blood, Sweat, and Pixels* (Jason Schreier, 2017), leído completo. Schreier entrevistó a ~100 desarrolladores entre 2015 y 2017. Todas las citas son textuales del libro (traducidas); todos los números son los que el libro reporta.

## 1. La tesis, y por qué te concierne

Un desarrollador, tras shipear, le dijo a Schreier: *"Oh, Jason. Es un milagro que CUALQUIER juego se haga."* El libro entero defiende que **ningún juego se hace en circunstancias normales**, porque no existen: cada juego inventa su propio proceso.

Las cinco razones estructurales que da Schreier — útiles porque explican por qué tu estimación va a fallar, y no es culpa tuya:

1. **Son interactivos.** El juego reacciona; no se renderiza una vez y ya.
2. **La tecnología no para de cambiar.** Feargus Urquhart (Obsidian): hacer juegos es como rodar películas *"si tuvieras que construir una cámara nueva cada vez"*. Otras analogías del libro: construir un edificio durante un terremoto; conducir un tren mientras alguien va poniendo la vía delante de ti.
3. **Las herramientas siempre son distintas.**
4. **Planificar es imposible.** Chris Rippy (productor, Halo Wars): en software normal estimas por tareas pasadas, *"pero con los juegos hablas de: ¿dónde está la diversión? ¿cuánto tarda la diversión? ¿lo conseguiste? ¿conseguiste suficiente diversión? […] Es un viaje a oscuras hasta ese punto."* ⭐ Y el matiz que sí sirve: **una vez demostrada la diversión y el look, la cosa SÍ se vuelve predecible.** La incertidumbre vive en preproducción, no en producción.
5. **No sabes si es divertido hasta jugarlo.** Emilia Schatz (Naughty Dog): *"Todos tiramos muchísimo trabajo porque creamos un montón de cosas y se juegan fatal. Haces planes intrincados en tu cabeza sobre lo bien que va a funcionar todo, y cuando lo pruebas de verdad, es terrible."*

Bruce Straley (Uncharted 4) lo comprime: **"No puedes taskear la creatividad. No puedes taskear la diversión."**

Y los patrones que se repiten en los diez casos, sin excepción: **todo juego se retrasa al menos una vez**; todos hacen recortes dolorosos; todos organizan el calendario alrededor de ferias; todos hacen crunch.

## 2. Los números que puedes usar

| Dato | Valor | De dónde |
|---|---|---|
| **Burn rate estándar de estudio** | **$10.000 por persona y mes** (salario + seguro + oficina + equipo) | Se usa igual en Obsidian y en Yacht Club. Es LA cifra para traducir dinero a tiempo |
| Pillars of Eternity | $3.986.794 en Kickstarter (74.000 backers) → presupuesto final ~$5,3M | El retraso final se comió $1,5M extra del estudio |
| Shovel Knight | $311.502 en Kickstarter (~$250k tras impuestos y comisiones) para 5 personas | ≈ 6 meses de burn rate |
| Stardew Valley | 1 persona, 4 años y medio, $0 de presupuesto | 1,5M copias y ~$21M brutos en 6 meses |
| Destiny | Acuerdo de $500M a 10 años con Activision | Metacritic 77; perdieron un bonus de $2,5M por no llegar a 90 |
| Dragon Age: Inquisition | ~99.000 bugs registrados | Incluye bugs cualitativos ("me aburrí aquí" se registra como bug) |

Conversión útil: $4M ≈ 40 personas durante 10 meses, o 20 durante 20 meses. Pero el libro avisa: en la vida real el equipo crece y encoge cada mes, así que el calendario es **vivo**, no una hoja fija.

## 3. Los diez casos, comprimidos

**Pillars of Eternity (Obsidian).** Microsoft les canceló un juego de golpe; 26 despidos en un día. Se salvaron con Kickstarter. Lo transferible: sin publisher al que impresionar pudieron hacer el vertical slice *"de la manera correcta"* — con los métodos reales de producción en vez de, como dice el lead de niveles Bobby Null, *"humo y espejos, hackear cosas para impresionar al publisher"*.

**Uncharted 4 (Naughty Dog).** Cambio de dirección a mitad con dos años ya invertidos: tiraron cinemáticas, voces y animación por millones. Con 200 personas esperando trabajo, Druckmann: *"si aciertas el 80%, estás mejor que intentando acertar el 100%, porque mientras tanto el equipo está parado"*.

**Stardew Valley (Eric Barone, solo).** El caso más relevante para un dev solo — sección §5 entera.

**Diablo III (Blizzard).** Lanzamiento roto (Error 37) y un diseño que empujaba a comprar en vez de jugar. Dos años después, *Reaper of Souls* lo salvó. Josh Mosqueira: *"puedes construir un juego, testearlo y creer que lo conoces — hasta que lo lanzas. El primer día, más gente ha jugado más horas colectivamente que todo el desarrollo hasta ese punto."* ⭐ Y el dato que más importa: **el Diablo II que la gente recuerda no es el original, es el de después de la expansión**. Los clásicos suelen ser su versión post-feedback.

**Halo Wars (Ensemble).** Microsoft les obligó a convertir su IP propia en un juego de Halo (*"o lo hacéis Halo, o os despedimos a todos"*) y creyó que era un cambio de color. El estudio se partió en tres proyectos con menos de 100 personas y cerró al terminar el juego. Todos menos tres se quedaron hasta shipear.

**Dragon Age: Inquisition (BioWare).** Motor de shooters (Frostbite) para hacer un RPG: no tenía personaje visible, ni stats, ni guardado. Mark Darrah: *"tuvimos que construirlo todo encima"*. Sin herramientas nadie podía estimar nada; sin estimaciones no había calendario.

**Shovel Knight (Yacht Club).** Cinco personas, sin jefe, sin dinero, con la regla de que **si uno decía no, se paraba**. §6.

**Destiny (Bungie).** Reinicio de la historia a menos de un año del lanzamiento, hecho *sin los escritores*. §4 y §7.

**The Witcher 3 (CD Projekt Red).** El caso de "cómo un outsider gana": §8.

**Star Wars 1313 (LucasArts).** Cancelado no por malo sino porque Disney compró la empresa. Steve Chen: *"desde mi punto de vista el juego no fue cancelado. El estudio fue cancelado. Es algo muy distinto."* Lección amarga: **hay causas de muerte que no dependen de la calidad de tu juego** — y por eso importa de quién dependes.

## 4. Las cinco trampas que aparecen una y otra vez

**1. El fantasma del juego anterior.** Diablo III cargó con Diablo II: *"el espectro de Diablo II pesaba sobre el equipo"* y volvió conservadoras decisiones que no debían serlo. Dragon Age: Inquisition cargó con las críticas a DA2 y reaccionó metiendo TODO: *"tenía todo menos el fregadero"* (Cameron Lee). ⭐ Antídoto que funcionó en Blizzard: **el equipo de consola, que no cargaba con la tradición, experimentó libre** (*"era un poco el Salvaje Oeste"*) y de ahí salió el rediseño del loot que salvó el juego. Si estás atascado por lo que "debe ser", monta un equipo o una rama sin ese peso.

**2. La gravedad del equipo.** Destiny quería ser fantasía en tercera persona y acabó siendo sci-fi en primera. Jaime Griesemer: *"tenemos un montón de artistas de producción que hacen sci-fi y no han hecho un orco ni una espada jamás, así que a lo mejor tenemos que hacer sci-fi. Queremos tercera persona, pero tenemos gente especializada en animación de primera persona y todo el código asume que la mira está en el centro […] Antes de darte cuenta, básicamente estamos haciendo Halo."* ⭐ **La composición del equipo decide el juego que sale.** Para un dev solo: tus habilidades actuales son la gravedad; cuenta con ella al elegir proyecto.

**3. Los stretch goals son deuda, no ingresos.** Obsidian prometió una segunda ciudad sin haber construido la primera. Urquhart después: *"Todos dijimos: ojalá no lo hubiéramos hecho. Al final no era necesaria."* Y Sawyer, por ritmo: *"vas por todo Defiance Bay, luego zonas salvajes, y aquí otra ciudad. Es como: tío, esto es el acto tres, sácame de aquí."* La construyeron igual, porque la habían prometido. Yacht Club prometió tres campañas gratis: **les costó años y ~$2M**. D'Angelo: *"ese ha sido nuestro mayor error: prometimos mucho juego. Cuando prometemos algo, queremos reventarlo. Así que prometer cualquier cosa es malo."* En la segunda campaña, Obsidian recaudó parecido **sin prometer segunda ciudad**.

**4. Cambiar de herramienta o motor a mitad cuesta meses invisibles.** Obsidian cambió a Maya y el arte se frenó semanas. Rob Nesler: *"hacen falta meses o años para ser tan bueno en algo que, cuando alguien te pregunta cuánto tardas, puedas responder 'tanto'."* ⭐ **Sin capacidad de estimar tareas básicas no hay calendario, y sin calendario no hay presupuesto.** BioWare y Bungie construyeron motor y juego a la vez: los dos lo pagaron.

**5. Construir arte antes que gameplay.** En Inquisition el arte iba rapidísimo y el diseño no podía probar nada. Ben McGrath: *"durante mucho tiempo la broma era que habíamos hecho un generador de capturas fantástico, porque podías pasear por los niveles sin nada que hacer."*

## 5. Ser dev solo: el caso Stardew Valley, sin romantizar

Eric Barone dijo seis meses. Tardó **cuatro años y medio**. Su novia le pagó las facturas casi todo ese tiempo. Lo que el libro documenta, y que sirve de espejo:

- **Sin nadie que te frene, el scope crece solo.** *"No había productores detrás de su silla diciéndole que dejara de sobre-escopear y publicara el maldito juego."* Cada semana el juego crecía.
- **Trabajaba en lo que le apetecía cada día**, no por hitos. Un día música, otro retratos, otro pesca. Rehízo los retratos **unas 15 veces** y todos los sprites más de una vez.
- **El síntoma del 90%.** Barone: tendía a construir el 90% de una feature, aburrirse y saltar a otra. *"Eso me dio la falsa impresión de que estaba cerca, porque arrancas el juego y parece que puedes hacer todo. Pero si miras de verdad, todo necesita un poco más de trabajo."* ⭐ El 90% de diez features es cero features.
- **Se pierde la objetividad por completo.** *"No tenía ni idea de cuándo el juego era divertido. De hecho pensé que el juego era basura hasta unos días antes del lanzamiento."*
- **La soledad es un problema técnico, no solo emocional**: no hay con quien contrastar. Cogió un trabajo de acomodador en un teatro en parte para ver gente.
- **El descanso le hizo más productivo.** Paró un mes para hacer un jueguito móvil; volvió mejor. Después escribió que espaciaba las sesiones *"no solo para disfrutar la vida, sino para que mi tiempo de desarrollo fuera más productivo"*.
- **No sabes fingir lo que no sabes hacer — apréndelo a fingir.** No sabía iluminación: dibujó **círculos blancos semitransparentes** detrás de antorchas y velas. Se ve igual de bien.
- **Gestionó las expectativas por trozos.** *"Si desde el principio hubiera dicho que iban a ser cinco años, no creo que nadie lo hubiera aceptado."*
- **Lanzó sin el multijugador que había prometido**, porque estaba quemado. Fue la decisión correcta.
- Al terminar: burnout, culpa y el bucle de parches que generan más bugs. Su siguiente proyecto: *"esta vez intento ser más realista. Espero que tarde dos años."*

## 6. Mecanismos concretos que puedes copiar mañana

**El experimento de Daniel Kading (Dragon Age: Inquisition)** — el más accionable del libro. El combate no era divertido y nadie sabía por qué. Kading pidió autoridad para convocar **al equipo entero, una hora, una vez por semana, cuatro semanas seguidas**, con encuentros construidos a propósito para aislar variables, y **una encuesta después de cada sesión**.
- Semana 1: nota media **1,2 sobre 10**.
- Semana 4: **8,8 sobre 10**.
- Y el efecto lateral que importa tanto como el número — Kading: *"la moral dio un giro asombroso a mejor esa misma semana. No es que pudiéramos reconocer los problemas. Es que no los estábamos esquivando."*
⭐ Receta: playtest **obligatorio, corto, recurrente, con escenarios construidos y encuesta numérica**. La nota no sirve para presumir, sirve para ver la pendiente.

**"Peelable scope" (Mark Darrah, BioWare)** para negociar un retraso: llegar con propuestas por capas — *esto podemos entregar con un mes más; esto con seis; esto con un año; y esto es exactamente lo que hay que cortar si no hay retraso*. Consiguieron el año.

**La escala 1-10 para desempatar (Druckmann y Straley, codirectores).** Cuando discrepan, cada uno puntúa del 1 al 10 cuánto le importa. Si uno está en 8 y el otro en 3, gana el 8, sin discusión. Si ambos están en 9-10, se encierran en un despacho: *"a veces son conversaciones de horas, hasta que los dos estamos de acuerdo. Y donde acabamos puede que no sea ninguna de las dos opciones de partida."*

**La política de demo de Adam Brennecke (Obsidian).** *"Mi política para E3 y para el vertical slice es que tiene que ser algo que va a estar en el juego final, para que el trabajo no se desperdicie."* Eligieron la primera media hora — que además es lo que más pulido necesita. El contraejemplo: la demo de Halo Wars en E3 2007 estaba scripteada a mano con código que no servía para el juego; la de Inquisition en PAX 2013 era **casi entera falsa** y nada de aquello llegó al juego final.

**El filtro por corte (Mateusz Tomaszkiewicz, The Witcher 3).** Cortó **el 50% de las quests** esbozadas: *"primero porque no teníamos tiempo de hacerlas todas, y segundo porque lo usé como oportunidad para filtrar las más débiles"*. ⭐ La falta de tiempo, bien usada, es un filtro de calidad.

**"Perfect is the enemy of good" como regla de priorización en crunch** (Josh Scherr, Naughty Dog): *"estás puliendo algo que está al 95% mientras esto de aquí, al 60%, necesita mucho amor"*.

**Ratio prototipo→producción** (Evan Wells, sobre un set piece cortado): *"puede llevarte unos días montar el prototipo, pero va a llevarte unos meses completarlo de verdad"* — porque toca efectos, sonido, animación y todos los departamentos.

## 7. Las herramientas de desarrollo son el factor número uno

La cita más importante del libro para un equipo pequeño, de alguien que trabajó en Destiny:

> *"El mayor diferenciador entre un estudio que hace un juego de altísima calidad y uno que no, no es la calidad del equipo. Son sus herramientas de desarrollo. Si tú puedes tirar cincuenta veces a puerta y eres un jugador de hockey malísimo, y yo solo puedo tirar tres veces y soy Wayne Gretzky, probablemente tú lo harás mejor. Eso son las herramientas."*

Y: *"Es la parte menos sexy del desarrollo y, aun así, es el factor más importante que existe. Buenas herramientas = mejor juego, siempre."*

El dato concreto: en Halo, ver un cambio de diseño en el juego tardaba **10-15 segundos**; en Destiny podía tardar **hasta media hora**. Multiplícalo por cada iteración de cada persona durante años.

⭐ **Traducción para un proyecto pequeño:** el tiempo que tardas desde "cambio un número" hasta "lo veo en el juego" es tu métrica de productividad real. Si es alto, arreglarlo rinde más que cualquier feature. Hot reload, escenas de prueba, valores expuestos en el inspector, un botón que salte al nivel que estás tocando.

## 8. Cómo gana un outsider: The Witcher 3

- **Contra la piratería, valor, no candados.** CD Projekt nació vendiendo en los mercados de software pirata de Varsovia. Cuando publicaron *Baldur's Gate* en Polonia, metieron en la caja mapa, guía y banda sonora: **18.000 copias el día uno**, en un país donde comprar juegos legalmente era nuevo. Iwiński: creen en *"la zanahoria, no el palo"*.
- **La regla anti-FedEx.** Mateusz Tomaszkiewicz: *"cada quest, por pequeña que sea, debe tener algo memorable, algún pequeño giro, algo por lo que la recuerdes. Algo inesperado."* Es la razón de que un juego de 200 horas no se sienta relleno — y BioWare le dijo a Schreier que querían copiar esa norma.
- **Densidad medida, no intuida.** El equipo de nivel colocaba puntos de interés y luego *"cogíamos el caballo, que apenas funcionaba, y cabalgábamos entre ellos midiendo el tiempo"*, comparándose con Red Dead Redemption y Skyrim. Se puede medir el ritmo de un mundo abierto con un cronómetro.
- **Reescribir es el trabajo, no un fracaso.** Jakub Szamałek: *"no creo que haya una sola quest en The Witcher 3 que se escribiera una vez, se aceptara y se grabara. Todo se reescribió docenas de veces."*
- **Evaluar sin juego es casi imposible** — y hay que asumirlo. Szamałek enseñaba escenas con dos pescadores grises sin animación ni voz: *"y diez personas mirando la pantalla te dicen: no lo pillo"*. Su solución no fue explicarlo mejor: fue iterar hasta que se pudiera ver.
- **Renunciaron a la generación anterior de consolas** cuando todos los demás hacían cross-gen. Acertaron. BioWare no lo hizo y Aaryn Flynn admitió: *"probablemente debería haberme esforzado más en matar la versión last-gen"* — acabó siendo el 10% de las ventas y limitó el juego entero.

## 9. Crunch: lo que dicen los que lo hacen

El libro no lo justifica ni lo esconde. Los datos, para decidir con la información puesta:

- Evan Wells (Naughty Dog): nunca es obligatorio... pero *"cuando un diseñador se queda hasta tarde, los demás se sienten presionados a quedarse también"*.
- **El hallazgo incómodo** (Druckmann): en Uncharted 4 planificaron antes que nunca para reducir crunch, y *"lo que descubrimos es que, en vez de reducir el crunch, hacemos un juego más ambicioso, y la gente trabaja igual de duro"*. ⭐ **El tiempo ahorrado se reinvierte en ambición, no en descanso** — salvo que alguien decida activamente lo contrario.
- Su conclusión medio en broma, medio en serio: *"para resolver el crunch, lo mejor que puedes hacer es: no intentes hacer el Juego del Año."*
- Erick Pangilinan: noches largas sí, **fines de semana nunca**. *"Soy muy estricto con eso."* Es la única regla del libro que alguien sostiene en el tiempo.
- El coste real, Justin Bell (Obsidian): *"sales del crunch y — tengo hijos. Los miro y pienso: han pasado seis meses y ahora eres una persona distinta. Y yo no estaba."*

Para un dev solo esto se traduce en algo distinto y peor: no hay nadie que te mande parar. Ver §5.

## Reglas prácticas

- [ ] Traduce dinero a tiempo con **$10.000 por persona y mes** antes de prometer nada.
- [ ] Asume el retraso: **los diez juegos del libro se retrasaron**. Planifica con la fecha, negocia con "peelable scope".
- [ ] No prometas lo que no puedes estimar. Un stretch goal es deuda con intereses, y la moneda de pago es tu tiempo.
- [ ] Toda demo pública debe ser **material que va a estar en el juego final**; si no, es trabajo tirado y expectativas que no puedes cumplir.
- [ ] Mide tu ciclo de iteración (cambio→verlo). Si es lento, arréglalo antes de seguir: es el factor número uno.
- [ ] Prueba la diversión con playtests **cortos, recurrentes, obligatorios y con nota numérica**; mira la pendiente entre semanas, no el valor absoluto.
- [ ] Antes de subir de complejidad, comprueba si el problema es el nivel, la legibilidad o las herramientas.
- [ ] Cuando falte tiempo, usa el recorte como **filtro de calidad**: corta primero lo más flojo, no lo más caro.
- [ ] Prioriza lo del 60% antes que pulir lo del 95%.
- [ ] Prototipo ≠ terminado: presupuesta **días para el prototipo, meses para completarlo**.
- [ ] Si eres dos, ten un mecanismo explícito de desempate (la escala 1-10) antes de necesitarlo.
- [ ] Si estás solo: hitos externos, alguien que juegue, y descansos programados. Perderás la objetividad — cuenta con ello.
- [ ] Sospecha del 90%: una feature al 90% es una feature sin terminar. Cierra antes de abrir.
- [ ] Nunca prometas contenido en función de horas ("100 horas de juego"): te obligas a rellenar.
- [ ] Lanzar es la mitad del trabajo, no el final. Diablo III y Destiny se arreglaron después. **Todo juego se puede arreglar.**

## Errores comunes

| Error | Cómo se ve en el libro | Antídoto |
|---|---|---|
| Estimar como si fuera software normal | *"No puedes taskear la diversión"* | Incertidumbre en preproducción; solo estima en producción, tras probar el core |
| Prometer features en el crowdfunding para recaudar más | Segunda ciudad de Pillars; tres campañas de Shovel Knight (~$2M y años) | Promete el juego, no la lista; deja los extras sin comprometer |
| Cambiar de motor/herramientas con el proyecto en marcha | Frostbite en Dragon Age; motor nuevo en Destiny y Halo Wars | Si es inevitable, asume meses de parón y no estimes hasta dominarlo |
| Producir arte antes de que el gameplay exista | *"Un generador de capturas fantástico"* | Greybox jugable primero; el arte va detrás del loop probado |
| Hacer una demo espectacular que no es el juego | Halo Wars E3 2007, Inquisition PAX 2013 | Regla de Brennecke: solo se enseña lo que se va a shipear |
| Reaccionar al juego anterior en vez de diseñar el nuevo | DA2 → Inquisition metió "todo menos el fregadero" | Separa qué falló por tiempo y qué falló por decisión |
| Rediseñar por aburrimiento tras años en el mismo juego | La "regla de ocho" de Halo Wars, cuestionada por gente que ya dominaba los controles | Rippy: *"cuando testeas el juego demasiado tiempo, inventas problemas y añades capas que no hacen falta"* |
| Un juego, dos jefes de diseño | Halo Wars: *"cuando los lead designers se pelean, no es bueno"* | Una sola persona decide, o un mecanismo explícito de desempate |
| Rehacer la historia al final del proyecto | El reboot de Destiny, hecho sin los escritores → "Franken-story", Metacritic 77 | Si hay que romper, rompe pronto y con quien sabe escribir |
| Confundir "casi terminado" con terminado | Dustin Browder (Blizzard): *"estamos al 99%, pero ese último 1% es una perra"* — tardaron casi un año | Deja hueco vacío al final del calendario explícitamente para iterar |
| Creer que un buen juego no puede morir | Star Wars 1313, cancelado por una compra corporativa | Controla de quién dependes; para un indie, esa es la ventaja real |

## Fuentes

- **Blood, Sweat, and Pixels: The Triumphant, Turbulent Stories Behind How Video Games Are Made** — Jason Schreier, Harper Paperbacks, 2017 (leído íntegro). Basado en entrevistas con ~100 desarrolladores entre 2015 y 2017; el libro declara que no contiene diálogo recreado y que las anécdotas se corroboraron con al menos dos fuentes cuando fue posible. Capítulos: Pillars of Eternity, Uncharted 4, Stardew Valley, Diablo III, Halo Wars, Dragon Age: Inquisition, Shovel Knight, Destiny, The Witcher 3, Star Wars 1313.
- ⚠️ **Frescura:** los casos son de 2005-2017 y los números (presupuestos, ventas, burn rate) son **de esa época**. Lo estable son los mecanismos y las trampas; lo volátil son las cifras y el estado de los estudios (ver `docs/source-freshness.md` en la raíz del repo). El burn rate de $10.000/persona/mes es el dato más citado del libro y sigue siendo la regla de bolsillo habitual, pero conviene ajustarlo al país y al año antes de usarlo en un presupuesto real.
- **Base sintetizada:** [ver: produccion-proceso] (milestones, playtesting método Valve, scope creep, polish, postmortems), [ver: preproduccion] (filtros de idea, pitch, vertical slice, kill criteria), [ver: pipeline/produccion-solo-dev] (ritmo y documentos del dev solo), [ver: historia-lecciones] (historia del medio y precedentes de diseño), [ver: psicologia-retencion-negocio] (modelos de negocio y lanzamiento).
