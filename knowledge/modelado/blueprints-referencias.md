# Blueprints y referencias

> **Cuando cargar este archivo:** antes de arrancar CUALQUIER asset 3D — para armar el paquete de referencias (blueprints, fotos, moodboard técnico), montarlo en el viewport y validar el blockout contra él. También al encargar o generar turnarounds/model sheets de un diseño propio.

## 1. La regla profesional: nunca modelar de memoria

Todo asset serio arranca con referencias reunidas ANTES de la primera extrusión. La memoria humana (y el prior de un modelo generativo) guarda **símbolos** de los objetos, no sus medidas: quien modela "de memoria" produce el arquetipo genérico del objeto, con proporciones inventadas y detalle plausible pero falso.

Evidencia de cómo trabajan los profesionales:

- Mido Lai (Gnomon, ex creature modeler en X-Legend): *"Finding reference is important for both 2D concepts and 3D modeling"* — y compara el sculpt contra el concept con overlay durante TODO el proceso, no solo al inicio (80.lv).
- Irfan Haider (senior vehicle artist: Forza, DiRT, F1): incluso teniendo blueprints, **cross-verifica contra el vehículo real** porque los blueprints pueden estar incompletos o mal; con CAD real se salta el blueprint y surfacea directo (80.lv).

Para un agente IA la regla es idéntica y más crítica: generar geometría "que se ve bien" sin referencia produce assets genéricos que un director de arte rechaza al primer vistazo. Protocolo: **paquete de referencias primero → blockout → validar blockout contra referencia, no contra la sensación** [ver: fundamentos-3d].

Dos tipos de referencia, y un asset necesita AMBOS:

| Tipo | Qué da | Ejemplos |
|---|---|---|
| **Dimensional** | Proporciones, medidas, silueta exacta | Blueprints, specs oficiales, CAD, patentes, medidas con cinta |
| **De apariencia** | Forma 3D real, material, color, desgaste, contexto | Fotos en perspectiva, close-ups de superficie, video, scans |

El blueprint sin fotos produce un modelo "plano" (las vistas ortográficas no contienen la sección transversal de las superficies curvas); las fotos sin blueprint producen proporciones adivinadas.

## 2. Qué es un blueprint (referencia ortográfica)

**Blueprints** = dibujos precisos de las proporciones y tamaños de un objeto desde varias vistas ortográficas (Polynook). En proyección ortográfica no hay perspectiva: una unidad mide lo mismo en cualquier punto de la imagen — por eso se puede modelar midiendo directamente sobre ella.

| Vista | Qué fija | Nota |
|---|---|---|
| **Front** | Ancho y alto; silueta frontal | La vista que se alinea primero |
| **Side** | Largo y alto; silueta de perfil | La más informativa en vehículos y armas |
| **Top** | Largo y ancho; planta | Concilia front y side; crítica en vehículos (curvatura del capó/techo) |
| **Back** | Detalle trasero | A menudo omitida en blueprints de fan-site; pedirla o derivarla |
| Bottom / secciones | Bajos, cortes transversales | Solo en manuales técnicos/CAD; oro para hard-surface |

Qué assets lo exigen: vehículos [ver: vehiculos], armas y props mecánicos [ver: props-armas], hard-surface en general [ver: hard-surface], arquitectura/kits modulares [ver: entornos-modulares], y personajes vía turnaround (§7) [ver: organico-personajes].

**Jerarquía de fidelidad dimensional** (de mejor a peor — usar la mejor disponible):

1. CAD / scan real del objeto
2. Blueprint técnico de fábrica / manual de taller / patente
3. Blueprint de sitio de fans (dibujado a partir de fotos: hereda errores)
4. Foto telephoto perpendicular (§6)
5. Foto cualquiera con perspectiva (solo apariencia, nunca dimensión)

## 3. Dónde conseguir blueprints

| Fuente | Qué tiene | Coste / licencia |
|---|---|---|
| **the-blueprints.com** | La base más grande: carros, motos, aviones, barcos, tanques, armas; vector y raster | Low-res gratis SOLO uso personal no comercial; comercial = comprar. EULA (ver abajo) |
| **carblueprints.info** | Blueprints de carros | Gratis, sin registro (según el propio sitio) |
| **drawingdatabase.com** | Vehículos, armas, naves, hi-res | Descarga gratis; revisar términos por imagen |
| **getoutlines.com** | Vectores de carros (nació para vehicle wraps) | Revisar términos |
| **Manuales técnicos** | Manuales de taller de vehículos, manuales militares de armas: vistas, cortes, despieces | Varía; los manuales gubernamentales suelen ser de acceso público — verificar estatus por documento |
| **Patentes** | Dibujos técnicos con vistas múltiples de mecanismos y productos, búsqueda pública (Google Patents) | Documentos públicos; excelente referencia de mecanismos internos |
| **3d.sk** | Fotos humanas por miles (turnarounds, anatomía, ropa) + body scans | Suscripción; se anuncia royalty-free comercial — confirmar licencia vigente en el sitio antes de usar en producción |
| **characterdesignreferences.com** | Colección curada de model sheets y concept art de producciones reales | Solo ESTUDIO: son material con copyright de los estudios (§7) |
| **Fotos propias** | Cualquier objeto accesible | Tuyas; técnica telephoto en §6 |

### Derechos de uso: las DOS capas

Usar un blueprint implica dos cuestiones legales separadas — confundirlas es el error clásico:

1. **La licencia de la imagen del blueprint.** EULA de the-blueprints.com (consultado): se permite *"incorporate the Product/Content into a separate work or product such as advertisements, film, television, or the creation of derivatives"* — es decir, **modelar en 3D a partir del blueprint está permitido** — pero el blueprint mismo *"cannot be part of the newly created content or be republished in any shape or form; as a whole or preview/thumbnail"*: prohibido redistribuir la imagen, incluirla en el paquete del asset o venderla. Contenido gratis = *"only for personal non-commercial applications"*.
2. **Los derechos del DISEÑO representado.** Un blueprint con licencia limpia de un Ferrari no te da derecho al trade dress ni a las marcas de Ferrari. El propio EULA lo delega: cierto contenido *"may require additional licensing, rights, permissions, releases, or clearance"* y es responsabilidad del comprador resolverlo. Regla operativa para un juego comercial: **diseño propio inspirado > réplica exacta**; vehículos/armas reconocibles sin licencia del fabricante = riesgo legal que decide el humano, no el agente. Sin logos, sin nombres de modelo, silueta alterada.

## 4. Hacer blueprints propios (diseño original)

El caso normal en producción: el asset es un diseño del juego, no existe blueprint. Se deriva del concept aprobado [ver: gamedev/arte-direccion].

**Flujo:** concept en perspectiva (el "bonito") → vistas ortográficas (el blueprint de trabajo). Son dos entregables distintos; el concept en perspectiva NO sirve como blueprint.

### A mano (humano o tableta)

1. Dibujar la vista **front** primero, sobre una grilla.
2. Trazar **líneas de registro horizontales** en cada landmark (línea de ojos, hombros, cintura, eje de ruedas, boca del cañón…) y extenderlas a lo ancho del canvas.
3. Dibujar **side** y **back** SOBRE esas mismas líneas: cada feature a la misma altura exacta en todas las vistas.
4. **Top** proyectando anchos desde front y largos desde side.
5. Todas las vistas a la MISMA escala, en el mismo canvas, con línea de suelo común.

La consistencia entre vistas es el requisito #1: un blueprint cuyas vistas no cuadran entre sí es peor que no tener blueprint, porque da autoridad a datos contradictorios.

### Con IA de imagen

Los generadores actuales producen turnarounds/model sheets aceptables como BORRADOR (prompt tipo: "character turnaround sheet, front side back views, neutral A-pose, flat orthographic, same scale, white background"; existen herramientas dedicadas a turnarounds). Fallos sistemáticos a auditar SIEMPRE antes de montar:

| Fallo típico de la IA | Cómo detectarlo | Corrección |
|---|---|---|
| Perspectiva sutil colada en una "vista ortográfica" | Bordes verticales que convergen; simetría rota | Regenerar pidiendo "flat orthographic"; o enderezar en editor 2D |
| Inconsistencia entre vistas (detalles que cambian, elementos que aparecen/desaparecen) | Superponer líneas de registro horizontales | Elegir UNA vista como canon y repintar las otras |
| Alturas que no cuadran entre vistas | Línea por ojos/hombros/cintura cruzando las vistas | Reencuadrar/escalar cada vista hasta alinear |
| Escalas distintas por vista | Medir el alto total de la figura en px por vista | Escalar a alto común |

**Specs de la imagen final** (propia o de IA): misma escala en todas las vistas · resolución suficiente para que el detalle más fino (remaches, costuras, gatillo) siga siendo legible al zoom máximo de modelado sin pixelar — criterio operativo, no una cifra fija: probar el zoom real contra la imagen antes de darla por buena · fondo neutro sin sombras proyectadas · línea de suelo marcada · cruz o líneas de registro visibles · sin compresión agresiva (PNG, no JPG re-guardado).

## 5. Montar las referencias en el software

Mecanismo genérico en cualquier DCC: **una imagen por vista ortográfica** (image plane / background image / image empty según la herramienta), visible idealmente solo en SU vista orto. Runbook (generalizado del setup de Polynook):

1. **Cortar** el blueprint compuesto en una imagen por vista (front, side, top, back).
2. **Alinear al origen:** el eje de simetría del objeto sobre el eje del mundo; la línea de suelo en altura 0. Así el mirror modifier/simetría funciona de gratis [ver: fundamentos-3d].
3. **Escala real común:** crear una caja con UNA dimensión conocida del objeto (ancho total, wheelbase, largo del arma; 1 unidad = 1 m [ver: pipeline/arte-a-unity]) y escalar la imagen hasta que el objeto calce esa medida. La escala se fija ANTES de modelar — reescalar a mitad de proyecto descalibra todo lo demás.
4. **Escalar todas las vistas con el pivot en el origen del mundo** (no en el centro de cada imagen): si no, las vistas se desalinean entre sí al escalar.
5. **Display:** opacidad ~0.5, imagen renderizada DETRÁS de la geometría, no seleccionable, sin recibir sombras.
6. **Verificar la cruz de alineación:** elegir 2-3 landmarks (eje de rueda delantera, mira del arma, centro del ojo) y comprobar que al cambiar de vista orto el mismo landmark cae en el mismo punto del espacio 3D. Truco: un plano o edge temporal a la altura del landmark, visible en front Y side — si no toca el landmark en ambas, una vista está corrida.

Higiene del setup: las imágenes de referencia viven en la carpeta del asset (no rutas sueltas del desktop) y el archivo de escena las referencia relativas — el que abra la escena mañana debe ver lo mismo.

## 6. Modelar encima: cuando el blueprint miente

**Orden de bloqueo:** silueta en front → estirar en side → conciliar en top; masas primero, detalle nunca antes de validar proporciones [ver: fundamentos-3d] [ver: gamedev/arte-direccion §9].

El blueprint NO es la verdad absoluta:

- Polynook lo dice sin rodeos: *"blueprints may be imperfect"* — no obsesionarse con calzar cada línea.
- Haider (Forza/F1): los blueprints *"can be incomplete"*; usa blueprint para las formas base y **cross-verifica contra fotos del vehículo real**.
- Las vistas de un blueprint de fan-site suelen contradecirse entre sí (se dibujaron desde fotos distintas). Protocolo: por cada feature, declarar una **vista master** (la que mejor muestra esa forma) y tratar las otras como aproximación.

**Regla de prioridad de fuentes al modelar:** dimensiones globales ← specs oficiales/blueprint · formas y curvatura 3D ← fotos en perspectiva · detalle de superficie ← close-ups. El blueprint aplana: la sección transversal de un capó o un antebrazo NO está en las 4 vistas — la dan las fotos y el conocimiento del objeto.

### Fotos como referencia: la perspectiva engaña

Una foto normal tiene distorsión de perspectiva; calcar proporciones de ella es heredar el error. Técnica documentada (Small Art Works) para fotos "tipo blueprint":

- *"Use your camera at full telephoto and then back away from the subject until it fills your screen"* — cuanto más lejos, menos error de paralaje.
- Cámara **perpendicular** al plano del objeto, en trípode, zoom óptico (nunca digital).
- El efecto es medible: en la comparación del artículo, la línea de techo del vehículo sale recta con tele desde lejos y curvada con wide de cerca.
- Un metro/regla apoyado en el objeto, perpendicular a la línea de visión, regala la escala.

**Camera matching** cuando solo hay fotos con perspectiva: **fSpy** (open source, gratis) extrae los parámetros de cámara desde UNA foto; con la cámara reconstruida en el DCC se monta la foto de fondo y se modela contra ella en perspectiva real (add-on oficial de importación para Blender; datos manuales — FoV, posición, orientación — para cualquier otro software).

**Checkpoint permanente:** rotar el modelo en perspectiva cada pocos minutos. Un modelo que calza las 4 vistas pero se ve mal girando **está mal** — el blueprint era el andamio, el juez es la vista en perspectiva con la cámara del juego [ver: pipeline/arte-a-unity §10].

## 7. Referencias para orgánico: turnarounds, model sheets, anatomía

### Model sheet (herencia de animación, canon del personaje)

Un **model sheet** estandariza la apariencia de un personaje entre muchos artistas: cabeza y cuerpo en varios ángulos (**model rotation**), expresiones faciales, manos, notas de construcción y proporciones. Personaje que se aparta del sheet = **off-model** (Wikipedia). Ojo con la fuente de estudio: los model sheets de producciones reales *"are copyrighted material owned by the animation studio"* — sirven para aprender el formato, no para redistribuir ni calcar.

### Turnaround para modelado 3D

Lo que el modelador necesita del concept artist (o de la IA, con la auditoría del §4):

| Requisito | Por qué |
|---|---|
| Front / side / back a la misma escala | Es el blueprint del personaje |
| Pose neutral: A-pose o T-pose, extremidades despegadas del cuerpo | Se modela/rigea en neutral; una pose dinámica no se puede calcar [ver: organico-personajes] |
| Sin perspectiva "artística", sin escorzo | La vista con actitud es OTRO entregable (el concept de presentación) |
| Boca/ojos neutros + hoja de expresiones aparte | Los blendshapes parten del neutro |
| Callouts de detalle (hebillas, costuras, props) | El zoom del turnaround no los resuelve |

En sculpting, la comparación contra el concept es continua y con overlay: Mido Lai superpone el concept sobre el sculpt (SpotLight en ZBrush o equivalente) y exige que *"the facial apexes of your model should match those of the concept one to one"*; guarda ángulos de cámara fijos para re-comparar igual en cada sesión — técnica directamente aplicable por un agente: renderizar el WIP desde cámaras fijas y comparar contra el turnaround.

### Anatomía: lo que el turnaround no contiene

El turnaround da silueta y proporción; el **volumen interno** lo da la anatomía:

- **Fotos/scans del natural:** 3d.sk (miles de fotos humanas organizadas: turnarounds, cabezas, manos, ropa; body scans) — el estándar de la industria para referencia humana.
- **Libros de forma:** la serie **Anatomy For Sculptors** (*Understanding the Human Figure*, *Form of the Head and Neck*, *Anatomy of Facial Expression*) — anatomía simplificada a FORMAS 3D pensada para escultores, no para médicos; el desglose de cómo los músculos se interconectan es lo que evita el "personaje inflado sin estructura".
- **Esculturas/écorché:** referencia clásica de planos de la cabeza y musculatura (bustos de planos tipo Asaro, écorchés) — útil sobre todo para estilizado, donde los planos importan más que el detalle [ver: estilizacion-lowpoly].

**Board mínimo para un personaje:** turnaround + concept en perspectiva + anatomía de las zonas visibles + referencias de material (piel/tela/pelo/metal) + 2-3 referencias del nivel de estilización objetivo del juego [ver: gamedev/arte-direccion].

## 8. Tableros de referencia (PureRef y equivalentes)

**PureRef** (Idyllic Pixel) es el estándar de facto: canvas libre de imágenes, drag & drop desde el navegador, always-on-top sobre el DCC, notas, desaturación de un toque, alinear/ordenar. Windows/Mac/Linux. Licencia: personal = gratis/pay-what-you-want; comercial = Small Business $49 pago único (hasta 3 usuarios, versión 2.x) o Business por asiento ($10/mes, $8/mes anual) — precios consultados en el sitio oficial (2026-07). Equivalente aceptable: cualquier canvas de imágenes, incluso un archivo de board en la herramienta 2D del proyecto — la práctica importa más que la app.

**Estructura del board por asset** (un board POR asset, no un board global del juego):

| Sección | Contenido | Fuente típica |
|---|---|---|
| 1. Identidad / mood | 3-6 imágenes del estilo objetivo CON callouts de qué se toma de cada una | Style guide del juego [ver: gamedev/arte-direccion §2] |
| 2. Técnica / dimensional | Blueprints, medidas, cortes, mecanismos, patente | §3 |
| 3. Material / color | Close-ups de superficie, desgaste (edge wear, óxido, tela), paleta hex del juego | Fotos macro, texturas de referencia |
| 4. Contexto en juego | Escala vs personaje, distancia de cámara real, asset vecino ya aprobado | Screenshot del engine |

Reglas del board:

- Cada imagen entra con un PROPÓSITO anotado ("de aquí: el desgaste de los bordes"; "de aquí: NADA de la paleta"). Imagen sin propósito = ruido.
- Desaturar el board completo para chequear valores contra el asset (función nativa de PureRef).
- El board **se guarda con el asset** (archivo .pur o carpeta de imágenes junto al modelo): es parte del entregable — quien retoque el asset en 6 meses necesita las mismas referencias.
- Para un agente IA sin GUI, el equivalente funcional es un **manifest de referencias**: lista de archivos de imagen + una línea de propósito por cada uno, escrito ANTES de modelar y guardado junto al asset. Mismo contrato, otro formato.

## 9. Runbook: paquete de referencias de un asset (resumen operativo)

Secuencia completa antes de modelar cualquier asset — cada paso remite a su sección:

1. Clasificar el asset: hard-surface con blueprint disponible (§3), hard-surface de diseño propio (§4), orgánico/personaje (§7), entorno/modular [ver: entornos-modulares].
2. Reunir la referencia **dimensional**: blueprint/CAD/specs con al menos UNA medida real confirmada (§2-§3). Si no existe → derivarla del concept (§4) o fotografiarla en tele (§6).
3. Reunir la referencia de **apariencia**: fotos en perspectiva, close-ups de material, desgaste (§1, §8).
4. Chequear derechos en las dos capas: licencia de las imágenes + diseño representado; anotar el veredicto en el manifest (§3).
5. Armar el board/manifest con las 4 secciones y propósito por imagen (§8); guardarlo en la carpeta del asset.
6. Montar las vistas en viewport: alinear, calibrar escala real, verificar la cruz (§5).
7. Bloquear masas contra las vistas; validar el blockout girando en perspectiva y contra las fotos (§6).
8. Solo entonces: detalle, topología y el resto del pipeline [ver: topologia] [ver: high-to-low] — con el board abierto hasta el final.

Si el paso 2 o 3 queda vacío, el asset NO arranca: se consigue la referencia o se escala el problema al director de arte — nunca se rellena de memoria (§1).

## Reglas practicas

1. Cero assets "de memoria": paquete de referencias (dimensional + apariencia) reunido y guardado ANTES de la primera extrusión.
2. Usa la mejor fuente dimensional disponible: CAD > blueprint de fábrica/manual > blueprint de fan-site > foto tele > foto normal.
3. Blueprint siempre acompañado de fotos en perspectiva: las vistas ortográficas no contienen la curvatura real.
4. Licencia en dos capas: (a) la imagen del blueprint y (b) el diseño representado (marcas, trade dress). Réplicas reconocibles de productos reales en juego comercial = decisión legal del humano, no del agente.
5. Jamás redistribuir la imagen del blueprint con el asset (el EULA típico lo prohíbe incluso como thumbnail); el modelo derivado sí es tuyo.
6. Diseño propio: derivar el turnaround/blueprint del concept con líneas de registro horizontales; cada landmark a la MISMA altura en todas las vistas.
7. Salida de IA de imagen = borrador: auditar perspectiva colada, inconsistencias entre vistas y escalas distintas antes de montarla en viewport.
8. Montaje: una imagen por vista orto, eje de simetría en el eje del mundo, suelo en 0, opacidad ~0.5, detrás de la geometría, no seleccionable.
9. Escala real fijada ANTES de modelar con una dimensión conocida y una caja de calibración (1 unidad = 1 m [ver: pipeline/arte-a-unity]); escalar las vistas con pivot en el origen del mundo.
10. Verificar la cruz: 2-3 landmarks deben caer en el mismo punto 3D al cambiar entre vistas orto; si no, una vista está corrida.
11. Por cada feature, una vista master; las demás vistas del blueprint son aproximación — los blueprints se contradicen y "may be imperfect".
12. Fotos propias tipo blueprint: full telephoto + alejarse + perpendicular + trípode; nunca calcar proporciones de una foto wide cercana.
13. Foto única con perspectiva → camera matching (fSpy) y modelar contra la cámara reconstruida, no "a ojo".
14. Rotar en perspectiva constantemente: calzar las 4 vistas no es el objetivo, es el andamio; el juez es la vista 3D con la cámara del juego.
15. Personajes: turnaround front/side/back en pose neutral a escala común; comparar el sculpt contra el concept con overlay y cámaras fijas guardadas (apexes faciales 1:1).
16. Anatomía en el board de todo orgánico: fotos/scans del natural + formas simplificadas (Anatomy For Sculptors); el turnaround no trae el volumen interno.
17. Un board de referencias POR asset con 4 secciones (mood/técnica/material/contexto) y propósito anotado por imagen; se archiva junto al asset.
18. Referencias con rutas relativas dentro de la carpeta del asset; una escena que abre sin sus referencias está incompleta.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Modelar "de memoria" porque el objeto "es simple" | Los objetos simples son los que todos conocen y donde el error genérico más se nota; board mínimo aunque sean 6 imágenes |
| Tratar el blueprint como verdad absoluta y calcar cada línea | Blueprint = andamio con errores; vista master por feature + cross-check con fotos (práctica de artistas AAA de vehículos) |
| Modelo perfecto en las 4 vistas, raro en perspectiva | El blueprint no contiene secciones transversales; validar girando y con fotos; aprobar solo en perspectiva |
| Calcar proporciones de una foto con perspectiva | Solo fotos tele perpendiculares dan proporción; el resto pasa por fSpy o se usa solo para apariencia |
| Montar las vistas sin verificar alineación entre ellas | Cruz de alineación con 2-3 landmarks antes de modelar; corregir la imagen, no compensar modelando |
| Escalar la referencia (o el modelo) a mitad del proyecto | Escala real calibrada en el paso 1 con dimensión conocida; después es intocable [ver: pipeline/arte-a-unity] |
| Escalar cada vista con su propio pivot y desalinear el conjunto | Pivot de escala siempre en el origen del mundo |
| Usar el concept en perspectiva como si fuera turnaround | Son dos entregables; exigir/derivar las vistas neutrales antes de modelar el personaje |
| Turnaround de IA montado sin auditar | Chequeo de líneas de registro + escala común + perspectiva colada; una vista canon y las otras corregidas |
| Blueprint gratis de internet dentro de un juego comercial | Gratis suele ser "personal use only"; comprar licencia o hacer blueprint propio; nunca empaquetar la imagen con el asset |
| Réplica exacta de un carro/arma real con logos "porque el blueprint era libre" | La licencia de la imagen no licencia el diseño: des-brandear, alterar silueta, o licencia del fabricante (decide el humano) |
| Board de 200 imágenes sin criterio (o cero board) | 4 secciones, propósito anotado por imagen; el board/manifest es parte del entregable |
| Personaje orgánico solo con el turnaround como referencia | Anatomía (fotos del natural + libros de forma) para el volumen; el turnaround solo da silueta |
| Referencias en rutas absolutas del desktop que se pierden | Carpeta del asset + rutas relativas; el board se versiona con el modelo |

## Fuentes

- **End User License Agreement — the-blueprints.com** (the-blueprints.com/information/licenseagreement/, consultado 2026-07) — términos reales del mayor sitio de blueprints: derivados 3D permitidos, redistribución de la imagen prohibida, gratis = solo uso personal, clearance adicional a cargo del usuario.
- **Modeling Vehicles for AAA Games — Irfan Haider (Playground Games/Turn 10/Codemasters), 80.lv** — flujo profesional según la fuente disponible: CAD → surfacear directo; blueprint → formas base + cross-verificación con el vehículo real; "every edge must have a purpose".
- **Character Production Workflow Overview — Mido Lai, 80.lv** — referencia continua en personajes: overlay del concept sobre el sculpt (SpotLight), apexes faciales 1:1, cámaras guardadas para comparación consistente, anatomía bajo la ropa.
- **How to Set Up Blueprints for Modeling in Blender — Polynook** — el runbook de montaje (generalizado aquí): corte por vistas, alineación a ejes, caja de calibración con dimensión real, pivot en el origen, opacidad/depth, y la advertencia "blueprints may be imperfect".
- **Taking Orthogonal Reference Photos — Small Art Works (smallartworks.ca)** — técnica de foto casi-ortográfica: full telephoto + distancia, perpendicularidad, trípode, error de paralaje demostrado (roof line recta vs curvada), regla en escena para escala.
- **fSpy — fspy.io** — camera matching open source y gratuito desde una sola foto; add-on oficial de importación para Blender, parámetros manuales para cualquier DCC.
- **Model sheet — Wikipedia** — definición y contenido del model sheet de animación (model rotation, expresiones, notas de construcción), concepto "off-model", y su estatus de copyright (propiedad del estudio).
- **PureRef — pureref.com (features + download/pricing, consultado 2026-07)** — features (canvas, always-on-top, notas, desaturar) y modelo de licencia real: personal pay-what-you-want; comercial $49 único (≤3 usuarios) o por asiento.
- **Anatomy For Sculptors — anatomy4sculptors.com** — serie canon de libros de anatomía como FORMA 3D para escultores (*Understanding the Human Figure*, *Form of the Head and Neck*, *Anatomy of Facial Expression*).
- **3d.sk** — mayor banco de fotos humanas y scans para artistas 3D (turnarounds, anatomía, ropa); el sitio bloqueó el acceso directo en esta consulta — la condición "royalty-free comercial" viene de descripciones de terceros: confirmar licencia vigente antes de producción.
- **Índices de sitios de blueprints** (búsqueda verificada 2026-07): the-blueprints.com/blueprints/cars/, carblueprints.info, drawingdatabase.com, getoutlines.com — catálogos activos de blueprints de vehículos.
- Base sintetizada: [ver: gamedev/arte-direccion] (style guide, visual target, moodboard con callouts) y [ver: pipeline/arte-a-unity] (escala 1 m = 1 unidad, auditoría de assets en engine).
