# Vehículos: el método

> **Cuando cargar este archivo:** al modelar cualquier vehículo de juego — coche, camión, tanque, moto, aeronave, kart estilizado — o al planificar su presupuesto, sus partes móviles y su interior. Complementa [ver: hard-surface] (técnicas generales) con el método específico de vehículo.

## 1. Por qué los vehículos son el examen final del hard-surface

Un vehículo combina en un solo asset TODO lo que hace difícil el hard-surface, y añade dos exigencias que un prop normal no tiene:

| Exigencia | Por qué es distinta a un prop |
|---|---|
| **Superficies curvas continuas GRANDES** | Un capó o un guardabarros es una sola superficie fluida de metros que el jugador ve reflejar el cielo. Cualquier bulto o pellizco en la topología se delata en el reflejo — en un prop pequeño el mismo error se esconde en el detalle [ver: topologia] |
| **Precisión mecánica** | Las piezas tienen que PODER funcionar: ruedas que giran sobre su eje real, puertas sobre bisagras reales, suspensión con recorrido. El ojo humano conoce los coches de memoria: una rueda 5% más grande o un eje desplazado "se ve mal" sin que el espectador sepa por qué |
| **Familiaridad del espectador** | Como las caras humanas: todo el mundo ha visto miles de coches. El margen de error en proporciones es mínimo comparado con un prop sci-fi inventado |
| **Es muchos assets en uno** | Carrocería + interior + ruedas + cristales + luces + mecánica visible. Krystian Gołębczyk (80.lv) lo trabaja por bloques; Gurmukh Bhasin (80.lv) lo llama partir el vehículo en "mini design projects" |

Regla de entrada: **entender cómo funciona antes de modelarlo**. Gołębczyk: *"If you don't know how something is working, it will be very hard to model it"*. Antes de la primera extrusión, el agente debe poder responder: ¿dónde pivota cada puerta? ¿qué recorre la suspensión? ¿por dónde entra el conductor?

## 2. El método: las 5 fases

Orden canónico consolidado de los breakdowns de artistas de vehículos (Woodvine — Back 4 Blood; Karpovs — Star Citizen/CoD; Washington — ex-Forza; Gołębczyk):

| Fase | Qué se hace | Criterio de salida |
|---|---|---|
| **1. Blueprint alineado** | Reunir blueprints del vehículo (o de uno similar) + fotos reales; montarlos en el viewport en vistas ortográficas alineadas a escala real. Woodvine usa "blueprints of the same or similar model" incluso para diseños propios; Washington collagea piezas de varios vehículos reales para inventar uno creíble | Blueprint a escala real (1 unidad = 1 m), vistas cruzadas coinciden entre sí. Todo el detalle en [ver: blueprints-referencias] |
| **2. Blockout de volúmenes** | Masas principales: carrocería como caja esculpida, cabina, ruedas como cilindros EN SU POSICIÓN Y DIÁMETRO FINAL, distancia entre ejes. Verificar stance (altura, reparto visual de masas) contra fotos en perspectiva, no solo contra el blueprint | Silueta correcta desde 360°, probada en el engine con la cámara real del juego [ver: gamedev/arte-direccion §9]. Las ruedas ya no se mueven de sitio |
| **3. Superficies principales con subdivisión** | Las superficies grandes y fluidas (capó, techo, laterales, guardabarros) como UNA malla continua de baja densidad + subdivisión. Cage mínimo: pocos loops, espaciado uniforme. Equivalente genérico del flujo de Woodvine (3ds Max: Editable Poly → Symmetry → Chamfer → Turbosmooth): malla poligonal base → modificador de simetría → bisel de aristas (chamfer/bevel) → subdivision surface | Reflejos limpios con zebra/matcap (§3) ANTES de cortar nada |
| **4. Cortes de paneles** | Separar puertas, capó, maletero, parachoques a partir de la superficie ya limpia (§4). Las líneas de panel (shutlines) heredan la curvatura de la superficie madre | Cada panel sigue reflejando en continuidad con sus vecinos; los gaps tienen grosor y profundidad reales |
| **5. Detalle** | Manijas, espejos, luces, rejillas, limpiaparabrisas, interior (§6), mecánica visible. Piezas pequeñas como objetos separados (no soldadas a la carrocería); librería reutilizable de tornillos/bisagras/válvulas en high y low (Gołębczyk) | Jerarquía de formas legible: primaria → secundaria → terciaria [ver: props-armas §4] |

Después siguen low-poly, UVs y bake — que en vehículos no cambian de método general [ver: high-to-low], con dos matices: exagerar levemente los chamfers respecto a la realidad para que el bake capture los bordes (Woodvine), y priorizar los tres workflows de [ver: hard-surface §3] así:

- **Subdivisión clásica + bake**: hero cars realistas, cámara cercana.
- **Mid-poly (chamfer + custom normals + normal map para detalle menor)**: el estándar actual para vehículos de juego — Karpovs lo señala como la técnica que se volvió norma en consolas actuales. Evita duplicar todo el vehículo en high-poly.
- **Low-poly directo sin bake**: estilizados (§7).

**Orden interno de modelado** (Gołębczyk): carrocería a escala correcta → puertas y elementos medianos (parachoques, luces, espejos) → interior de grande a pequeño → ruedas al final (§5) — las ruedas se modelan al final pero su posición y diámetro quedaron congelados en el blockout.

## 3. Superficies curvas limpias: el reflejo es el test

Una superficie de coche no se evalúa mirando la malla: se evalúa mirando **cómo refleja**. El estándar de la industria (heredado del diseño automotriz CAD) es la continuidad de curvatura, y el test práctico son las franjas zebra / matcap de alto contraste.

### Niveles de continuidad (léxico CAD, aplicado a sub-d)

Interpretación de las franjas zebra (documentación de Rhino, comando Zebra — vale igual mirando un matcap de franjas en cualquier viewport):

| Nivel | Qué coincide | Cómo se ven las franjas en la unión | En un vehículo |
|---|---|---|---|
| **G0** (posición) | Las superficies solo se tocan | Las franjas se quiebran o "saltan de lado" al cruzar la unión | Arista dura intencional (borde de panel). Correcto SOLO donde hay un corte real |
| **G1** (tangencia) | Posición + tangente | Las franjas conectan pero giran bruscamente en la unión | Se nota como "línea fantasma" en el reflejo. Casi nunca es lo que quieres en carrocería |
| **G2** (curvatura) | Posición + tangente + curvatura | Las franjas continúan suaves a través de la unión | El objetivo en toda superficie de carrocería que comparte flujo |

En modelado poligonal no hay G2 matemático — se **aproxima** con el cage de subdivisión. Reglas prácticas destiladas de Topology Guides (Johnson Martin) y el polycount wiki (*Subdivision Surface Modeling*):

- **Cage mínimo y espaciado uniforme el mayor tiempo posible.** Cada loop extra es un riesgo: *"even adding an extra edge loop that 'seems' to follow the surface can cause minute distortions to reflections if placed incorrectly"* (Topology Guides). La densidad se gana subdividiendo, no añadiendo loops a mano.
- **Poles fuera de las superficies vistosas.** Los poles (vértices de 3 o 5+ edges [ver: topologia §4]) son inevitables; se REUBICAN hacia zonas ocultas (bajos, interior de pasos de rueda), no se eliminan.
- **Creases vs holding edges**: los support loops junto a una arista deforman la curvatura vecina en superficies grandes; el edge creasing da topología más limpia — PERO los creases no sobreviven el export a otros programas/bakers (polycount wiki). Decisión: creases para explorar, holding edges o mid-poly para la versión que viaja por el pipeline.
- **Detalle DESPUÉS de la superficie**: manijas, tapas y tomas de aire se añaden tras aplicar 1-2 niveles de subdivisión sobre la superficie ya validada, para no contaminar el cage base (Topology Guides).
- **Test permanente, no final**: matcap de franjas de alto contraste activo DURANTE el modelado — el matcap gris por defecto esconde defectos (Topology Guides). BeamNG (docs oficiales) exige "good polyflow" explícitamente "to ensure that you get good looking reflections"; para mallas sin high-poly, auto-smooth de 45-60° como punto de partida.
- Mover la luz/entorno del viewport alrededor del modelo: un defecto solo aparece cuando una franja lo cruza.

### Protocolo de inspección de reflejos (runbook)

1. Aplicar matcap de franjas de alto contraste (o material espejo con HDRI de franjas).
2. Orbitar la cámara a ras de cada superficie grande (capó, techo, lateral) — los defectos aparecen en ángulos rasantes, no de frente.
3. Rotar el modelo (o el entorno) lentamente: las franjas deben DESLIZARSE por la superficie sin engancharse; un punto donde la franja "vibra" o se arremolina = pole o loop mal puesto.
4. Revisar cada unión entre paneles: quiebre de franja solo donde hay corte real (G0 intencional).
5. Repetir tras CADA cambio de topología en superficies principales — el test cuesta segundos; rehacer un capó contaminado cuesta horas.
6. Antes de dar por cerrada la fase 3: captura de las franjas en 4 vistas como evidencia del estado limpio (referencia para comparar si fases posteriores lo estropean).

## 4. Cortes de paneles

El error clásico es modelar cada panel por separado y rezar para que casen. El método correcto es el inverso:

1. **Modelar la superficie madre continua** (lateral completo, frontal completo) y limpiarla hasta que refleje bien (§3).
2. **Marcar las líneas de corte** sobre esa superficie siguiendo el blueprint (las shutlines reales de un coche siguen el flujo del diseño, no la topología cómoda).
3. **Separar los paneles** duplicando/cortando la superficie madre: cada panel hereda la curvatura exacta, así el reflejo fluye de puerta a guardabarros aunque sean mallas distintas.
4. **Dar realidad al corte**: grosor del borde del panel (un fold hacia dentro, no un plano de papel), gap consistente (en coches reales ~3-5 mm — a escala de juego suele exagerarse un poco para que lea), y sombra/AO del gap capturada en el bake [ver: high-to-low §6].
5. Paneles que deben moverse (puerta, capó) se separan como objetos con su pivot en la bisagra (§5); paneles decorativos pueden quedar en la misma malla con el corte solo marcado (geometría o normal map, según cámara y presupuesto [ver: hard-surface §7 y §9]).

## 5. Partes móviles y jerarquía: modelar para el rig del engine

Un vehículo jugable no es una malla: es una **jerarquía de mallas** que el engine va a animar por transformaciones. El modelador decide en el DCC qué puede moverse después — si la rueda está soldada a la carrocería, no hay rigging que la salve.

Principios (docs de Unity — WheelCollider tutorial — y docs de vehículos de BeamNG, coincidentes):

- **Cada parte móvil = objeto separado, con nombre propio y pivot en su eje mecánico real.** BeamNG: el origen de un prop móvil "should be aligned with the axis of rotation, and have one of the direction vectors point along the axis of rotation".
- **Jerarquía plana y predecible**: un root (pivot en el centro del vehículo a nivel del suelo, mirando a +Z [ver: pipeline/arte-a-unity §7]) con hijos body, wheel_FL/FR/RL/RR, puertas, torreta, etc. Unity monta el coche exactamente así: root → body + una malla por rueda, con los colliders de rueda como objetos aparte — el asset debe entregar las ruedas como mallas independientes o no hay setup posible.
- La transformación del vehículo completo la hace el root; NINGUNA parte hija lleva transformaciones cocidas (rotación/escala ≠ 0/1) [ver: fundamentos-3d §5].

| Parte | Pivot | Notas de modelado |
|---|---|---|
| **Rueda** | Centro exacto del eje de giro, alineado al eje lateral del vehículo | Malla separada por rueda (las 4 pueden instanciar la misma malla espejada). El engine necesita su radio exacto para el collider (Unity). El pivot descentrado = rueda que "cojea" al girar |
| **Puerta** | La línea de bisagra real (borde delantero, vertical) | Modelar el interior del marco y el canto de la puerta: al abrirse se ve. Probar la rotación EN el DCC antes de exportar |
| **Capó / maletero** | Su bisagra real (borde trasero del capó, superior del maletero) | Igual: el hueco que destapa debe existir (bandeja de motor simplificada o tapa plástica, §6) |
| **Suspensión básica** | La rueda cuelga del root con espacio de recorrido | El paso de rueda (wheel well) se modela con holgura REAL: la rueda comprimida no puede atravesar la carrocería. En Unity la suspensión extiende hacia abajo desde la posición del collider — el modelador solo garantiza el hueco y la rueda separada |
| **Volante / palancas / agujas** | Su eje de rotación | Solo si la cámara los ve (§6); son los "props" internos que el rig anima |
| **Hélice / rotor** | Centro del eje de giro | Práctica estándar de flight/combat games: dos variantes — palas modeladas (parada/lenta) y disco con textura alpha de blur (a velocidad); ambas comparten el pivot. Marca la variante en el naming |
| **Torreta de tanque** | Anillo de la torreta (vertical) + pivot separado del cañón (horizontal) | Dos niveles de jerarquía: torreta gira, cañón eleva. El mantelete debe cubrir el hueco en todo el rango de elevación |
| **Orugas** | — (no rotan como objeto) | Modelar UN eslabón/segmento modular y decidir con el equipo la técnica de animación (scroll de UV sobre malla continua, o cadena de segmentos instanciados); las ruedas de rodaje sí llevan pivots individuales como ruedas normales |

El detalle de pivots para props interactivos y attachment points es el mismo mecanismo de [ver: props-armas §7.2 y §8]; la verificación de escala/ejes/pivots al importar está en [ver: pipeline/arte-a-unity §7 y §10].

### Otros tipos de vehículo: qué parte móvil no puede faltar

El principio del §5 (parte móvil = malla separada + pivot en el eje mecánico) aplicado por tipo — inventario mínimo de separaciones antes de exportar:

| Tipo | Partes móviles mínimas | Trampa típica |
|---|---|---|
| Moto | Rueda trasera; **horquilla delantera completa (manillar + horquilla + rueda) como sub-jerarquía** que rota sobre el eje de dirección inclinado | Pivot de dirección vertical: la dirección real gira sobre el eje INCLINADO de la horquilla |
| Avión | Hélice/rotores; tren de aterrizaje (retráctil = jerarquía propia); superficies de control: alerones, flaps, elevadores, timón — cada una con pivot en su línea de bisagra | Superficies de control soldadas al ala: sin ellas el avión no puede "actuar" que vuela |
| Helicóptero | Rotor principal + rotor de cola (pivots en sus ejes); tren o patines | Olvidar la variante blur-disc del rotor |
| Camión articulado | Cabina y remolque como assets separados unidos por el pivot de la quinta rueda | Modelarlo como una sola pieza rígida |
| Barco | Timón, hélices; cañones/torretas si combate | El pivot del root: en barcos conviene en la línea de flotación, no en la quilla — documentar la convención en la spec |
| Maquinaria (grúa, excavadora) | Cada eslabón del brazo con su pivot de articulación, en cadena jerárquica (base → brazo → antebrazo → pala) | Pivots en el centro de cada pieza en vez de en el pasador real de la articulación |

### Cristales, luces y materiales: decisiones que se toman EN la malla

La asignación de materiales es parte del modelado del vehículo, porque obliga a separar geometría:

- **Cristales = malla separada con material propio** (transparencia). BeamNG lo exige explícitamente: luces y ventanas con materiales individuales. Un cristal fundido en la malla de carrocería no puede ser transparente ni romperse por separado.
- **Luces**: la óptica (faro) como pieza con material emisivo/propio para poder encenderse en el engine [ver: pipeline/arte-a-unity §7, Emission]. El interior del faro (reflector, bombilla simplificada) solo si la cámara acerca.
- **Presupuesto de materiales**: el objetivo de 1 material por prop [ver: pipeline/arte-a-unity] se relaja en vehículos jugables: lo típico es carrocería/opacos + cristal + (opcional) interior — cada material extra rompe batching, así que se agrupa TODO lo opaco en un solo material/atlas y se justifica cada adicional.
- **Carrocería pintada vs plásticos/goma**: si comparten material, la separación la hace la textura (masks/ID map del bake [ver: high-to-low §6]) — otra razón para planear los IDs de material desde el modelado, no al final.

## 6. Interiores: cuánto modelar según cámara

El interior es la mitad del coste de un vehículo — y muchas veces sobra. Decidir ANTES de modelar, por cámara y gameplay:

| Nivel | Cuándo | Qué se modela |
|---|---|---|
| **Nada (cristales opacos/tintados)** | Vehículo decorativo de fondo, tráfico lejano, RTS/top-down | Cero interior; cristales oscuros u opacos. El truco más barato y el más usado en fondos |
| **Cockpit básico ("shell interior")** | Tercera persona con cámara que puede acercarse; cristales transparentes | Cáscara interior: asientos, volante, salpicadero como volúmenes simples, todo en texturas modestas. Sin detalle bajo el nivel "se ve algo dentro" |
| **Interior completo** | Primera persona / cámara de cockpit / cinemáticas dentro | Salpicadero con instrumentos legibles, volante animable con su pivot, pedales, techo interior, pilares vistos desde dentro. Es un entorno pequeño: presupuesto propio |

Evidencia de que esto es una decisión de producción real: en Gran Turismo 5 solo los coches "premium" (~25% del catálogo) tenían vista de interior detallada; los "standard" no tenían cockpit y solo tras la actualización Spec 2.0 recibieron una vista interior simplificada (documentado en la recepción del juego). Polyphony eligió nivel de interior POR COCHE según su rol — exactamente la tabla de arriba aplicada a escala AAA.

La misma lógica aplica a toda la mecánica oculta. Karpovs (Star Citizen, CoD): *"Instead of modeling full undercarriage with transmission or a complete engine fuel system, you can use plastic covers or simplify it"* — los bajos y el vano motor se resuelven con tapas y volúmenes simples, y el presupuesto liberado se invierte donde el jugador mira (ruedas, cabina, zona de daño). Preguntar SIEMPRE: ¿qué cámaras del juego real ven esta pieza? [ver: gamedev/arte-direccion].

## 7. Ruedas y neumáticos: el sub-método

La rueda es el prop dentro del vehículo — y donde más se nota la calidad. Karpovs les da prioridad de texel density y detalle: *"labels and marking on the wheels give the vehicle a specific look and feel"*.

Método radial (estándar del oficio; Washington lo describe para ruedas y hélices: "segments then arrayed around a central axis"):

1. **Neumático — el segmento**: modelar UNA porción del neumático (un módulo del patrón de huella, con su perfil de flanco). Toda la limpieza se hace aquí: es la única pieza que se repite.
2. **Array radial**: repetir el segmento alrededor del eje hasta cerrar el círculo. El número de segmentos fija la redondez: el conteo de lados se decide por el tamaño en pantalla ([ver: topologia §6]; la discusión canon "# of sides on a barrel" del foro de polycount, citada por el wiki: la silueta manda).
3. **Huella (tread)**: según cámara y presupuesto — geometría real del dibujo (hero car, primeros planos), o huella bakeada a normal map sobre un toro liso (la mayoría de juegos), o solo textura (fondo/estilizado). El flanco (lettering, marca) casi siempre va en normal map + albedo [ver: high-to-low].
4. **Rin (rim)**: objeto separado del neumático. Mismo truco radial: un radio (spoke) modelado limpio → array. La profundidad del rin y la tuerca central venden la rueda de cerca.
5. **Ensamblar y congelar el pivot** en el centro del eje (§5). Duplicar/instanciar a las demás posiciones — jamás modelar 4 ruedas.

Detalles que delatan una rueda amateur: neumático que es un cilindro sin perfil (el flanco real es curvo y sobresale del rin), huella que no envuelve el hombro del neumático, rueda flotando sin contacto aplastado contra el suelo (en juego lo resuelve la suspensión; en renders/thumbnails, un leve flatten en la zona de contacto), y radios del rin con normales rotas por el array mal soldado.

## 8. Vehículos estilizados y low-poly: la regla del juguete

Cuando el juego es estilizado [ver: estilizacion-lowpoly], el vehículo no se "simplifica": se **re-proporciona**. El patrón consolidado de la práctica del oficio (formulación propia — no hay UNA fuente canónica que lo bautice así):

- **Regla del juguete**: proporciones de juguete de cuerda — ruedas MÁS grandes respecto al cuerpo, carrocería más corta y ancha (chibi), cabina más alta, voladizos (overhangs) casi nulos. El vehículo entero tiende a formas más redondas o más cuadradas según el lenguaje de formas del juego [ver: gamedev/arte-direccion §1].
- **Exagerar la función**: lo que define al vehículo se agranda (la pala de la excavadora, el cañón del tanque, el alerón del deportivo); lo que no, se funde en la masa. Mismo principio de silueta que personajes [ver: estilizacion-lowpoly §3].
- **Menos cortes, más masa**: reducir drásticamente las líneas de panel y el greeble; un coche estilizado puede ser 1 volumen + ruedas + 2-3 acentos. El detalle vive en el color y el shading, no en la geometría.

Cuándo saltarse el realismo mecánico — y cuándo no:

| Se puede saltar | NUNCA saltarse |
|---|---|
| Suspensión real (la rueda puede colgar "del aire") | Pivots correctos: la rueda estilizada TAMBIÉN gira sobre su centro |
| Interior (cristales opacos o cabina de 6 polys con un conductor-cápsula) | Que las ruedas toquen el suelo y estén dentro de la silueta al girar |
| Mecánica visible (motor, ejes, transmisión) | La jerarquía de partes móviles del §5 — el rig del engine es el mismo |
| Grosor real de paneles, gaps, tornillería | La lectura de dirección: dónde es el frente debe ser obvio en silueta |
| Precisión del blueprint (se parte de proporciones inventadas) | El blockout probado en engine con la cámara real — MÁS importante aún, porque las proporciones exageradas se calibran a ojo |

Workflow: low-poly directo sin high-poly ni bake, color por paleta-atlas o vertex color [ver: estilizacion-lowpoly §4] — el vehículo estilizado es de los assets más baratos de producir bien.

## 9. Presupuestos y LODs

Números con origen publicado (compilación de Rick Stirling — games artist, ex-Rockstar North — "Yes, but how many polygons?", la referencia que el propio polycount wiki enlaza; polys ≈ tris en esta tabla):

| Juego / asset | Plataforma, año | Conteo |
|---|---|---|
| Project Gotham Racing 2 — coches | Xbox, 2003 | ~10,000 |
| Project Gotham Racing 3 — coches | Xbox 360, 2006 | 80,000–100,000 |
| Half-Life 2 — buggy (sin arma montada) | PC, 2004 | 5,824 |

Lecturas operativas de esa tabla y del resto de fuentes:

- **El salto PGR2→PGR3 (10x en una generación)** muestra que el presupuesto de un vehículo protagonista escala con el hardware más rápido que el de personajes. Los racing games modernos usan cientos de miles de tris en sus hero cars con LODs agresivos; las cifras exactas por juego actual deben confirmarse contra un breakdown publicado del juego objetivo antes de usarlas como spec (los números que circulan en foros sin origen: prohibidos) [ver: presupuestos-poligonos].
- **El buggy de HL2 (~6k)** es el punto de referencia del otro extremo: vehículo jugable de shooter donde el coche NO es el protagonista — dos órdenes de magnitud menos que un racing del mismo periodo.
- **Jugable vs decorativo**: el vehículo decorativo (tráfico, atrezzo de calle) es un prop [ver: props-armas §1]: sin interior (§6), sin partes móviles salvo quizá ruedas, mid-poly o low directo, y comparte trim sheets/atlas con el entorno donde sea posible. Presupuestarlo como prop grande, no como "coche barato".
- **Dónde invertir el presupuesto dentro del vehículo** (consolidado de Karpovs): ruedas y cabina primero, silueta de carrocería después, mecánica oculta al mínimo con tapas. La superficie grande y lisa es barata en polys — lo caro son los bordes, cortes y piezas pequeñas.
- **LODs**: los vehículos jugables y de tráfico son candidatos obligados a LODs (se ven de cerca Y a distancia). Regla de producción: LOD1 elimina interior, mecánica y piezas pequeñas (limpiaparabrisas, manijas); LOD2 funde paneles en una cáscara; el último nivel es una silueta de pocos cientos de tris o impostor. Reducción ~50% de tris por nivel como punto de partida y nombrado `_LOD0..n` dentro del FBX para que Unity monte el LOD Group solo — mecánica y criterios en [ver: pipeline/arte-a-unity §7]. Las ruedas suelen aguantar un nivel más de detalle que la carrocería porque su silueta circular delata el low-poly antes.

## Reglas prácticas

1. Antes de modelar: entender el funcionamiento mecánico (bisagras, ejes, recorridos). Si no puedes explicar cómo se abre la puerta, no puedes modelarla.
2. Blueprint alineado a escala real (1 unidad = 1 m) montado en ortográficas ANTES de la primera extrusión; cross-verificar contra fotos porque los blueprints mienten [ver: blueprints-referencias §6].
3. Blockout con las ruedas en posición y diámetro FINALES; stance validado en el engine con la cámara real. Después del blockout, las ruedas no se mueven.
4. Superficies grandes como malla continua de cage mínimo: pocos loops, espaciado uniforme; densidad por subdivisión, nunca loops "de refuerzo" a ojo.
5. Matcap/zebra de alto contraste activo TODO el tiempo; el objetivo en carrocería es franjas que cruzan las uniones sin quebrarse ni girar (aprox. G2). Franja que salta = G0 (solo válido en cortes reales); franja que gira brusco = G1 (arreglar).
6. Poles reubicados a zonas ocultas (bajos, pasos de rueda, interior); jamás en mitad de un capó.
7. Los paneles se CORTAN de la superficie madre ya limpia, nunca se modelan sueltos; cada corte con grosor de borde y gap consistente.
8. Cada parte móvil = objeto separado + pivot en su eje mecánico real + naming claro (wheel_FL, door_L, turret, hood). Probar la rotación en el DCC antes de exportar.
9. Jerarquía: root en el centro-suelo mirando +Z; ninguna pieza hija con transformaciones cocidas; las 4 ruedas instancias de una malla.
10. El paso de rueda con holgura para el recorrido de suspensión: rueda comprimida no atraviesa carrocería.
11. Interior según cámara y NADA más: opaco (fondo) / cáscara (tercera persona) / completo (primera persona). Mecánica oculta = tapas simples (Karpovs).
12. Ruedas por método radial: un segmento limpio → array; rin separado; pivot en el eje; huella por normal map salvo hero car. Prioridad de texel density a la rueda.
13. Chamfers levemente exagerados sobre la realidad para que el bake los capture; mid-poly (chamfer + custom normals) como default de producción, high-poly completo solo para hero cars.
14. Estilizado: re-proporcionar (ruedas grandes, cuerpo corto, cero voladizos), menos cortes de panel — pero pivots, contacto con el suelo y jerarquía de §5 intactos.
15. Presupuesto: invertir en ruedas, cabina y bordes; las superficies lisas son baratas. Vehículo decorativo se presupuesta como prop, sin interior ni partes móviles.
16. LODs nombrados en el FBX desde la entrega: LOD1 sin interior ni piezas chicas, LOD2 cáscara, último nivel silueta; ruedas un nivel más detalladas que el resto.
17. Cristales y luces como mallas separadas con material propio desde el modelado; todo lo opaco agrupado en un material/atlas, cada material extra justificado.
18. En motos el pivot de dirección va en el eje inclinado de la horquilla; en aviones cada superficie de control lleva su bisagra; en maquinaria, cadena jerárquica de articulaciones con pivots en los pasadores reales.
19. Números de polycount solo de breakdowns/fuentes publicadas del juego objetivo; cifra de foro sin origen = no existe.
20. Guardar capturas del test de zebra al cerrar la fase de superficies: son la referencia para detectar si los cortes de panel o el detalle posterior ensuciaron la carrocería.
21. Todo lo anterior se audita al importar con el runbook de [ver: pipeline/arte-a-unity §10]: escala contra cubo de 1 m, rotación (0,0,0), pivots apoyando en Y=0.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Modelar el coche "de memoria" → arquetipo genérico con proporciones falsas | Blueprint + fotos SIEMPRE, incluso para diseños inventados (se parte de un vehículo real similar) [ver: blueprints-referencias] |
| Reflejos con bultos y pellizcos en el capó | Cage mínimo y uniforme, poles reubicados, detalle añadido después de subdividir; zebra/matcap permanente (§3) |
| Añadir loops "que siguen la superficie" para arreglar un defecto | Cada loop extra distorsiona (Topology Guides): quitar loops, no añadir; rehacer la zona con menos geometría |
| Paneles modelados por separado que no casan en el reflejo | Cortar de la superficie madre limpia (§4) |
| Cortes de panel de papel: sin grosor ni profundidad | Fold interior en cada borde + gap consistente; AO del gap al bake |
| Rueda soldada a la carrocería o con pivot descentrado | Malla separada por rueda, pivot en el centro del eje; girar en el DCC para verificar (§5) |
| Puerta que al abrirse revela vacío (sin marco ni canto) | Modelar canto de puerta y marco interior antes de dar por cerrada la fase de cortes |
| Interior completo en un coche que solo se ve en tercera persona lejana | Decidir nivel de interior por cámara ANTES (§6); GT5 lo hizo por catálogo entero |
| Motor y bajos modelados a detalle "por completitud" | Tapas y volúmenes simples (Karpovs); presupuesto a donde mira el jugador |
| Creases de subdivisión que se pierden al exportar al baker | Creases solo para explorar; la versión que viaja usa holding edges o mid-poly (polycount wiki) |
| Neumático = cilindro liso con textura estirada | Sub-método radial con perfil de flanco real (§7) |
| Vehículo estilizado con proporciones reales "pero menos polys" | El estilizado se RE-proporciona (regla del juguete), no se decima (§8) |
| Estilizado sin frente legible o con ruedas que no tocan el suelo | La exageración no exime la lectura ni el contacto; blockout en engine igual que el realista |
| Spec de polys copiada de un foro ("los coches AAA tienen X") | Solo números con origen publicado; si no hay, presupuestar por comparable verificado (PGR3 ~100k en X360 como orden de magnitud histórico) y confirmar en profiling propio |
| Vehículo entregado como una sola malla al engine | Jerarquía de §5 en el FBX: el rigging del vehículo en engine es imposible sin partes separadas (Unity WheelCollider exige ruedas independientes) |

## Fuentes

- **Subdivision Surface Modeling** — polycount wiki — canon del método sub-d: cage + subdivisión, creases y su no-exportabilidad, referencia central del oficio hard-surface.
- **Polygon Count** — polycount wiki — tris vs polys vs verts, por qué el vertex count real manda, e índice de las compilaciones de conteos con origen.
- **Yes, but how many polygons?** — Rick Stirling (games artist, ex-Rockstar North), rsart.co.uk, 2007 (enlazado por el polycount wiki; consultado vía Wayback) — conteos por juego con plataforma y año: PGR2 ~10k, PGR3 80-100k, buggy de HL2 5,824.
- **Zebra analysis (comando Zebra)** — documentación oficial de Rhinoceros (McNeel) — interpretación exacta de franjas para G0/G1/G2: quiebre / giro brusco / continuidad suave.
- **Dealing with Mesh Artifacts in Subdivision Modeling** — Johnson Martin, Topology Guides — causa raíz de reflejos sucios: loops mal puestos, poles, espaciado; matcaps de alto contraste; creases vs holding edges; detalle tras subdividir.
- **Create a functioning vehicle (WheelCollider tutorial)** — Unity Manual — jerarquía exigida por el engine: root + body + malla separada por rueda, colliders aparte, radio de rueda exacto.
- **Vehicle Modeling Guidelines** — documentación oficial de BeamNG.drive — separación de partes móviles/desmontables, orígenes alineados al eje de rotación, polyflow para reflejos, auto-smooth 45-60°.
- **Creation of Vehicles for Games** — Krystian Gołębczyk (hard-surface freelancer), 80.lv — orden de modelado carrocería→medianos→interior→ruedas, entender la función antes de modelar, librería reutilizable high/low.
- **Creating Realistic Vehicles in 3ds Max & Substance 3D Painter** — Miguel Sanchez Woodvine (Back 4 Blood), 80.lv — blueprint→blockout→high (Symmetry/Chamfer/Turbosmooth)→low→UV con texel density; chamfers exagerados para el bake.
- **Polaris MRZR D4: Military Vehicle Production** — Sergejs Karpovs (Star Citizen, Squadron 42, Call of Duty), 80.lv — optimización de zonas ocultas con tapas, mid-poly chamfer+custom normals como estándar, prioridad de texel/branding en ruedas.
- **Complex Vehicle Production in 3D** — Marvin Washington (ex-Forza), 80.lv — blueprints collageados para diseños propios, ruedas y hélices por segmento + array radial, splines para blindaje.
- **Futuristic Vehicle Production Breakdown (HEMTT-2182)** — Gurmukh Bhasin (concept designer), 80.lv — partir el vehículo en "mini design projects", blockout desde modelo base para stance/proporciones/escala.
- **Gran Turismo 5** — Wikipedia (sección Vehicles/Reception, con citas a prensa) — premium (~25% del catálogo) con interior detallado vs standard sin cockpit (vista simplificada solo tras Spec 2.0): el tiering de interiores como decisión de producción real.
- Base sintetizada: [ver: hard-surface], [ver: topologia], [ver: high-to-low], [ver: blueprints-referencias], [ver: props-armas], [ver: estilizacion-lowpoly], [ver: gamedev/arte-direccion], [ver: pipeline/arte-a-unity].
