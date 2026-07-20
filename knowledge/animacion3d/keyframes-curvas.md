# Keyframes, curvas e interpolación

> **Cuando cargar este archivo:** al animar personajes 3D con keyframes y trabajar en el graph/curve editor — poner keys en canales, elegir interpolación (stepped/linear/bezier), leer y editar tangentes/handles, meter timing con ease in/out y spacing, bloquear poses con stepped keys (blocking), pulir a spline, limpiar curvas (jitter, keys redundantes), ciclar con modificadores de curva, y entender qué de esas curvas suaves sobrevive al exportar a Unity (sampleado por frame). Es la CRAFT técnica de las curvas, agnóstica de herramienta. Los principios de POSING/APPEAL están en [ver: principios-produccion]; el consumo en motor (Animator/blend trees/root motion) en [ver: unity/animacion-unity]; el game-feel del timing en [ver: gamedev/animacion] y [ver: gamedev/game-feel]. La ejecución concreta en un DCC (Action editor, NLA, export de clips) es la fase siguiente, aún no cubierta.

## 1. El modelo mental: keyframe → canal → curva

Animar keyframeando es un contrato con la herramienta: **tú fijas valores en momentos concretos; el software rellena el resto interpolando.** Lo que ves como "una animación" es en realidad un haz de curvas 1D independientes.

| Término | Qué es | Nota operativa |
|---|---|---|
| **Keyframe / key** | Un valor fijado en un `(tiempo, valor)` sobre UN canal | En el dopesheet, un "keyframe" es un frame donde ≥1 canal tiene key (Unity: *keyframe = frame en que una o más curvas tienen key*) |
| **Channel / F-curve** | Una curva 1D por propiedad-eje: `locX`, `locY`, `locZ`, `rotX/Y/Z(/W)`, `scaleX…`, blendshape, custom | Un hueso = ~9–10 canales; un personaje = cientos. El graph editor es el mapa de TODOS ellos |
| **Interpolación** | Cómo la herramienta conecta dos keys consecutivas de un canal | Es donde vive el 90% del "feel" — dos animadores con las MISMAS poses producen movimientos distintos según las curvas |
| **Breakdown** | Key intermedia que define el CAMINO entre dos poses clave (el "cómo") | No es relleno automático: es una decisión de arco/overlap. Concepto de Williams |
| **Inbetween** | Los frames que la máquina calcula entre keys | En 3D los hace el interpolador; en 2D tradicional los dibujaba un asistente |

- **Poses (extremes) vs breakdowns vs inbetweens** es la jerarquía de Richard Williams (*The Animator's Survival Kit*): el animador es dueño de extremes y breakdowns; los inbetweens son consecuencia de las curvas. Controlar la animación = controlar esos dos niveles + la forma de la curva, no tocar cada frame.
- Regla de oro del canal: **cada eje es independiente.** Un salto "flota" casi siempre porque `locY` tiene mala curva aunque `locX` esté perfecto. Diagnostica por canal, no por "la animación".

### Estrategia de keying: qué canales fijar
| Modo | Qué keyea | Cuándo |
|---|---|---|
| **Key All / whole-character** | TODOS los canales del rig en cada pose clave | Blocking pose-a-pose: garantiza poses completas y limpias, sin canales "colgados" a medias |
| **Selective / por grupo** | Solo los canales que cambian (una mano, la cadera) | Polish y overlap: mover un canal sin tocar el resto para desfasar timings |
| **Keying sets / grupos** | Un set nombrado de canales (ej. "IK piernas", "cara") | Rigs grandes: keyear coherente por dominio y no dejar un eje sin fijar |

- ⚠️ **Peligro del selective en blocking**: si keyeas solo algunos canales por pose, los que dejaste sin key mantienen su valor anterior y "se arrastran" — animación con partes zombis. En blocking, keyea completo; el selective es para el pulido.

## 2. Modos de interpolación: constant, linear, bezier

Tres familias, presentes con distinto nombre en todo DCC (Blender, Maya, MotionBuilder) y en Unity. Elegir mal es la causa raíz de la mayoría de curvas que "se sienten mal".

| Modo | Forma entre keys | Se siente | Cuándo usarlo |
|---|---|---|---|
| **Constant / Stepped** | Escalón: mantiene el valor de la key izquierda hasta la siguiente, salto seco | Corte, sin interpolación | **Blocking** (sección 6), snaps intencionales, cambios de textura/visibilidad, prop que aparece, "hold" duro |
| **Linear** | Recta entre keys | Mecánico, velocidad constante, sin ease | Maquinaria, LEDs, rebotes ya con su ease en el spacing, ciclos técnicos, cuando NO quieres que la herramienta redondee las esquinas |
| **Bezier / Spline** | Curva suave con handles/tangentes editables | Orgánico, con aceleración y desaceleración | **Todo lo orgánico**: cuerpos, cámaras, follow-through. Es el default de trabajo del animador de personajes |

- **Bezier es el caballo de batalla**; constant y linear son herramientas puntuales. Pero un bezier con tangentes por defecto (auto-suavizado) produce el look "flotante/gomoso" clásico del principiante — la suavidad hay que ganársela editando handles, no aceptando el default (sección 3).
- **Easing como sub-modo del bezier**: los editores ofrecen ecuaciones de ease predefinidas (Sinusoidal, Cuadrática, Cúbica… hasta efectos dinámicos Back/Bounce/Elastic) con dirección Ease In / Ease Out / In-Out. Útiles para UI/props; para personaje casi siempre se moldea a mano con tangentes en vez de aplicar una ecuación.
- Detalle Unity verificado: un segmento sin pesos se interpola con **Hermite**; al activar tangentes ponderadas pasa a **Bézier** usando `outWeight`/`inWeight` (peso por defecto = **1/3** cuando no se fija). Es la misma matemática, distinto grado de control del handle.

## 3. El graph/curve editor: leer y editar

### Dos vistas del mismo dato
- **Dopesheet**: solo CUÁNDO hay keys (diamantes en una rejilla de tiempo). Sirve para **timing** — mover keys en el tiempo, ver el spacing horizontal, retimear bloques enteros.
- **Graph / Curve editor**: el VALOR de cada canal como línea en un plano tiempo×valor. Sirve para **cómo se mueve** — pendiente, arcos, ease, overshoot. El animador de personajes vive aquí.

### Leer una curva (traducción directa a movimiento)

| Lo que ves en la curva | Lo que significa en pantalla |
|---|---|
| Pendiente plana (horizontal) | El objeto está QUIETO en ese eje (hold) |
| Pendiente suave | Movimiento lento en ese eje |
| Pendiente empinada | Movimiento rápido |
| Curva que sube-baja suave | Acelera y desacelera (ease natural) |
| Pico/valle | Un extremo: cambio de dirección |
| Zigzag de dientes finos | **Jitter** — ruido no intencional (sección 7) |
| Curva que pasa el objetivo y vuelve | **Overshoot + settle** (sección 5) |

- **La pendiente ES la velocidad.** Leer curvas = leer velocidades. Un arco que "se rompe" suele ser una curva de un eje con una pendiente que no acompaña a las otras.
- **Test rápido de hold**: si algo debe quedarse quieto y "tiembla", el canal no está plano — aplana la tangente o borra keys sobrantes.

### Tangentes / handles

El handle en cada key define la pendiente de entrada (in) y salida (out). Terminología verificada de Unity (equivalentes directos en Blender/Maya):

| Tipo de tangente | Comportamiento | Uso |
|---|---|---|
| **Clamped Auto** (default) | Suaviza automáticamente y **evita overshoot** al mover la key; se reajusta al editar | El punto de partida sano para curvas orgánicas |
| **Auto** (legacy) | Suaviza pero NO se reajusta al mover la key ni previene overshoot | Evitar; usar Clamped Auto |
| **Free Smooth** | Handles arrastrables a mano, in/out **colineales** (garantiza suavidad) | Moldear ease a mano manteniendo continuidad |
| **Flat** | Handles horizontales (caso especial de Free Smooth) | Extremos/holds: pico limpio sin overshoot |
| **Broken – Free** | In y out **independientes**, se rompe la colinealidad | Cambios de dirección con distinta velocidad a cada lado |
| **Broken – Linear** | La tangente apunta a la key vecina (segmento recto) | Mezclar tramos rectos y curvos en una misma curva |
| **Broken – Constant** | El tramo mantiene el valor de la key izquierda (escalón local) | Stepped puntual sin cambiar toda la curva |

- **Weighted tangents** (Unity `weightedMode`: None/In/Out/Both): además del ángulo, el handle tiene LONGITUD, que controla cuánta influencia tiene sobre el tramo. Handle largo = el ease se estira más lejos de la key. Da control fino del "peso" de la aceleración; también los DCC lo ofrecen.
- **Handle types de moldeo** (nomenclatura DCC, Blender/Maya): Free (libre), Aligned (colineal), Vector (apunta a la vecina = recto), Automatic y Auto Clamped (auto sin overshoot). Son el mismo concepto que la tabla de arriba con otros nombres.
- Regla: **empieza en Clamped/Auto-Clamped, rompe a Free/Broken solo donde el movimiento lo pida.** No rompas todo por defecto — genera curvas imposibles de mantener.

### Operaciones que se repiten en el editor
- **Retimear** = mover keys en el eje tiempo (mejor en dopesheet); **remodelar** = mover en el eje valor o girar handles (graph editor). Sepáralas mentalmente: primero timing, luego forma.
- **Box-select** de un bloque de keys para escalar el timing entero (estirar/comprimir la acción sin re-keyear).
- **Snap a frame entero**: mantén las keys en frames enteros salvo intención explícita; keys a `12.4` frames ensucian el export y complican el retime.
- **Aislar un canal** (solo la curva que investigas) para no leer el editor como un plato de espagueti; casi todo DCC tiene "solo canales seleccionados".

## 4. Ease in / ease out = timing del movimiento

Slow-in/slow-out (principio Disney, [ver: gamedev/animacion]) **es la forma de la curva cerca de las keys**. No es un efecto que se añade: es cómo entra y sale la tangente.

| Forma de la tangente en la key | Resultado |
|---|---|
| Tangente plana entrando (ease in) | El objeto DESACELERA al llegar a la pose (asienta) |
| Tangente plana saliendo (ease out) | El objeto ARRANCA lento desde la pose |
| Tangente empinada a ambos lados | Pasa por la pose a máxima velocidad (sin hold) — típico de un breakdown en mitad de un arco |
| Ambas tangentes planas (Flat) | Hold: llega, se queda, sale suave |

- **Ease agresivo = peso e impacto.** Un golpe que "pega" tiene ease-out casi vertical hacia el frame de impacto y un settle detrás; un ease simétrico y suave se siente ligero/flotante. El reparto asimétrico del ease es lo que da carácter (rápido-a-lento vs lento-a-rápido).
- En gameplay el ease se concentra en el **follow-through**, no en el arranque del jugador — el startup quiere ser casi lineal/snappy [ver: gamedev/animacion §5]. Reservar las curvas ricas para recovery, idles y cinemáticas.

## 5. Spacing, overshoot y settle

### Spacing: la distancia entre lo que pasa, no entre keys
- **Spacing** = cuánto se mueve el objeto ENTRE frames consecutivos. En la curva se lee como densidad: **tramos con la curva casi plana (poco cambio de valor por frame) = lento; tramos empinados (mucho cambio) = rápido.** Es el concepto de Williams (spacing/timing charts) traducido al graph editor.
- Ojo con la confusión clásica: **keys juntas en el TIEMPO ≠ lento.** Lo que decide la velocidad es el cambio de VALOR por frame (la pendiente), no cuántos frames hay entre keys. Dos keys muy separadas en el tiempo con gran salto de valor = movimiento rápido. Piensa en spacing de valor, no en densidad de keys.
- Regla práctica: si algo se siente uniforme/robótico, el spacing es demasiado parejo — necesita más contraste (frames rápidos muy rápidos, lentos muy lentos). Timing manda sobre cantidad de frames [ver: gamedev/animacion §3].

### Overshoot y settle: vida al final del movimiento
- **Overshoot**: la curva pasa DE LARGO el valor objetivo y vuelve. Un brazo que se detiene no frena en seco: sobrepasa un poco y asienta. Es follow-through/overlap ([ver: movimiento-secundario]) expresado en curva.
- **Settle**: el pequeño rebote amortiguado de vuelta al objetivo tras el overshoot (1–2 oscilaciones decrecientes).
- Cómo se construye en el graph editor:
  1. Key en la pose destino, key un pelín MÁS ALLÁ del valor (el overshoot), key de vuelta al destino (el settle).
  2. Tangentes: entrada rápida al overshoot, salida suave al settle.
  3. Escalonar overshoot por jerarquía: la mano sobrepasa DESPUÉS y MÁS que el antebrazo (overlap = desfasar las keys de los canales hijos 2–4 frames respecto a los padres).
- **Cuidado**: `Clamped Auto` / `Auto Clamped` **matan el overshoot a propósito** (evitan que la curva se pase). Para overshoot hay que romper a Free/Broken y empujar el handle, o meter la key extra. Si un movimiento se ve "muerto", muchas veces es la tangente auto-clamp comiéndose el rebote.

### Moving holds: por qué un "quieto" no debe estar congelado
- **Dead hold** (dos keys idénticas con curva plana): el personaje se **congela** — lee como pausa de video, sin vida. Es el error clásico que delata la animación amateur (Williams).
- **Moving hold / living hold**: en vez de dos keys iguales, la segunda **deriva un pelín** (traslación/rotación mínima) y suele venir de un ligero settle. El personaje "descansa" pero sigue vivo. En la curva: no es un tramo plano, es una pendiente casi imperceptible que sigue moviéndose hacia la pose.
- Regla: **evita curvas planas largas en canales de personaje.** Un hold de personaje es un moving hold; el flat puro se reserva para props/mecánica.

## 6. El flujo blocking → spline (stepped keys)

Método pose-a-pose ([ver: gamedev/animacion §1], [ver: principios-produccion]) llevado a la práctica de curvas. Se bloquea el TIMING antes de tocar la interpolación.

| Fase | Interpolación | Qué se decide | Qué NO se toca aún |
|---|---|---|---|
| **1. Blocking** | **Stepped / Constant** en TODO | Poses clave + timing (en qué frame ocurre cada pose). Sin interpolación: saltos secos entre poses | Arcos, ease, overlap |
| **2. Breakdowns** | Aún stepped | Poses intermedias que definen el camino/arco entre extremes | Suavidad |
| **3. Spline (conversión)** | Pasar todo a **Bezier/Spline** | La herramienta interpola; aparece el movimiento continuo | — |
| **4. Polish** | Bezier + tangentes a mano | Arreglar el caos que genera el auto-spline: arcos, ease, overshoot, overlap, cleanup | — |

- **Por qué stepped primero**: en stepped ves SOLO tus poses y su timing, sin que la interpolación te engañe. Si el timing lee bien en stepped (se entiende la acción saltando de pose a pose), la base es sólida. Es más fácil iterar timing aquí que sobre curvas ya suavizadas.
- **La conversión a spline SIEMPRE ensucia**: al pasar de stepped a bezier el software mete su propia interpolación y aparecen overshoots, arcos rotos y pies deslizando. La fase 4 (polish) es donde está el trabajo real; no la subestimes en el presupuesto.
- Pose-a-pose gana en juegos porque permite **iterar sin terminar** — poses aprobadas primero, pulido después, y todo puede cambiar en producción [ver: gamedev/animacion §1].
- Encaja con las 3 fases de un ataque (wind-up/active/recovery [ver: animacion-combate], [ver: gamedev/animacion §2]): bloquea las poses de cada fase en stepped, valida el timing de gameplay, y recién entonces pule.

## 7. Limpiar curvas: jitter, keys redundantes, simplificación

Curvas sucias = animación sucia + clips más pesados. Dos orígenes: sobre-keyar a mano y (sobre todo) **mocap**, que trae una key por frame en cada canal [ver: mocap-librerias].

| Problema | Síntoma en la curva | Antídoto |
|---|---|---|
| **Jitter / ruido** | Zigzag de dientes finos donde debería haber una línea limpia | Borrar keys intermedias y re-suavizar; smooth/sample; en mocap, capa de filtrado antes de retimear |
| **Keys redundantes** | Muchas keys sobre una curva que ya sería suave con 3–4 | Simplificar/decimar (quitar keys cuyo borrado no cambia la forma dentro de un umbral) |
| **Sobre-keyado a mano** | Cada frame con key "por si acaso"; imposible editar la forma | Menos keys, mejor puestas: pocas keys bien situadas dan más control que muchas |
| **Gimbal / flip de rotación** | Salto brusco de 359°→0° o volteo en curvas Euler | Trabajar en cuaternión donde se pueda; o filtrar Euler; ver nota de rotaciones abajo |

- **Regla del mínimo de keys**: la curva más editable es la de menos keys que consigue la forma. Cada key extra es un punto más que mantener cuando cambie el timing. "Menos keys, mejor colocadas" antes que "más control por más keys".
- **Rotaciones — cuaternión vs Euler** (Unity, verificado): la interpolación en cuaternión va por el **camino más corto** entre dos rotaciones (evita gimbal) pero **no puede representar giros > 180°** (dos keys a 270° interpolan los 90° cortos); Euler admite giros arbitrariamente grandes con curvas X/Y/Z independientes pero sufre gimbal al combinar ejes. Elige según necesites giros grandes (Euler) o robustez (cuaternión), y sé consciente de que el motor puede **resamplear Euler a cuaternión** al importar (sección 8).
- El cleanup NO es opcional en pipeline de mocap: los datos crudos son densos y ruidosos por definición; limpiar es la mitad del trabajo de un editor de mocap.

## 8. Ciclos y modificadores de curva

Para loops (walk/run/idle [ver: ciclos-locomocion]) no se copian keys a mano hasta el infinito: se usa un **modificador de ciclo** sobre la curva, que repite la forma fuera del rango de keys.

| Modo de ciclo (Blender: *Cycles* modifier; equivalentes en Maya *infinity/post-infinity*) | Qué hace | Uso |
|---|---|---|
| **Repeat Motion** (repetir) | Repite la curva idéntica, una y otra vez | Idle, giro de rueda, parpadeo, oscilación en sitio |
| **Repeat with Offset** (repetir con offset) | Repite sumando el desplazamiento acumulado de cada ciclo | **Locomoción que avanza**: el `locX/Z` sube en escalera para que el personaje camine hacia adelante ciclo tras ciclo, no en el sitio |
| **Repeat Mirrored** (repetir espejado) | Repite alternando la forma espejada | Péndulos, vaivenes simétricos |

- **Extrapolación** (qué hace la curva antes de la primera key / después de la última): **Constant** (mantiene el valor extremo, plano) o **Linear** (continúa con la pendiente de la última tangente). El ciclo es una extrapolación "inteligente" que repite en vez de aplanar/continuar.
- Otros modificadores de curva útiles: **Noise** (añade ruido procedural controlado — vida a un idle sin keyear temblor a mano; ideal para cámaras handheld o respiración) y **Stepped Interpolation** (fuerza a la curva a saltar en escalones de N frames sin borrar keys — útil para look "stop-motion"/12fps sobre una animación suave).
- ⚠️ Los modificadores son NO destructivos y en vivo — muchos motores **no los importan**: al exportar a Unity el ciclo hay que estar **horneado en keys reales** o resuelto por el `Loop Time`/`Loop Pose` del import [ver: unity/animacion-unity §import]. Verifica qué sobrevive antes de confiar en el modificador (sección 9).

## 9. Lo que ve el animador (curvas suaves) vs lo que exporta a Unity (sampleado por frame)

La distinción más importante de producción: **el animador trabaja con curvas continuas y analíticas; el motor consume, casi siempre, una versión discretizada — un valor por frame.** No asumir que la curva llega intacta.

| En el DCC (autoría) | Tras importar en Unity (runtime) |
|---|---|
| F-curves bezier continuas, evaluables a cualquier tiempo | Curvas **resampleadas/reducidas**; el importer decide qué keys guarda |
| Tangentes/handles editables | Puede quedar una key por frame (dense) o keys reducidas re-ajustadas |
| Modificadores en vivo (Cycles, Noise) | NO se importan: hay que hornearlos a keys o usar Loop Time |
| Rotaciones Euler o cuaternión a elección | **Resample Curves** (ON por defecto para Euler) genera **un keyframe cuaternión por CADA frame** |

Opciones de import de Unity que gobiernan esa traducción (verificado, Manual `class-AnimationClip`):

| Ajuste | Efecto | Cuándo |
|---|---|---|
| **Anim. Compression = Off** | Guarda todas las keys, máxima fidelidad, más memoria/tamaño | Casi nunca (solo debug de un artefacto de compresión) |
| **Keyframe Reduction** | Quita keys redundantes en import según umbrales de error | Default sano para la mayoría de clips (Legacy/Generic/Humanoid) |
| **Optimal** | Unity elige entre reducir o formato denso | Solo Generic/Humanoid; buen default general |
| **Rotation / Position / Scale Error** | Umbral de descarte: rotación en **grados**, posición/escala en **%**. Quita una key si `delta < valor_original × tolerancia` | Subir si el clip pesa mucho; bajar si aparece "patinaje"/pérdida de detalle |
| **Resample Curves** | Convierte Euler→cuaternión, una key por frame | ON por defecto; apagar solo si necesitas conservar curvas Euler crudas |

- **Implicación práctica #1 — no confíes en la interpolación fina que el motor no ve.** Un ease sutil moldeado con handles puede desaparecer si la reducción de keyframes lo aplana bajo el umbral de error. Verifica el clip YA importado en el motor, no solo en el DCC [ver: unity/animacion-unity].
- **Implicación práctica #2 — sincronía de blend trees.** Para que un blend de locomoción no patine, los clips deben pisar en el MISMO tiempo normalizado; eso se decide en las curvas de origen y debe sobrevivir al sampling [ver: unity/animacion-unity §2].
- **Implicación práctica #3 — mocap = denso por definición.** Datos de mocap/Mixamo llegan con key-por-frame; la reducción de Unity o un cleanup previo en el DCC es lo que los hace manejables [ver: mocap-librerias].
- **Los clips importados son de solo lectura** en Unity: para tocar una curva hay que copiar los keyframes a un clip nuevo, o volver al DCC (verificado, Manual `AnimationsImport`). El editing real de curvas vive en el DCC, no en el motor.
- **Sample rate**: el clip tiene un frame-rate de muestreo; el runtime interpola entre esas muestras. Un clip a 30fps muestreado y reproducido a 60fps se interpola linealmente entre muestras — otra razón para no depender de micro-detalle sub-frame de la curva original.

## Reglas prácticas

- [ ] Piensa y diagnostica **por canal** (`locY`, `rotZ`…), no por "la animación": el defecto casi siempre es una curva de un eje.
- [ ] Default de trabajo: **bezier con tangentes Clamped/Auto-Clamped**; rompe a Free/Broken solo donde el movimiento lo pida.
- [ ] Usa **stepped/constant para blocking**, linear para lo mecánico, bezier para lo orgánico — decide el modo a conciencia, no dejes el default.
- [ ] Bloquea el **timing en stepped** y valida que la acción se lee saltando de pose a pose ANTES de convertir a spline.
- [ ] Presupuesta la fase de **polish post-spline**: la conversión a bezier siempre ensucia (overshoot, arcos rotos, foot slide).
- [ ] **La pendiente es la velocidad**: lee las curvas como velocidades; tramo plano = quieto, empinado = rápido.
- [ ] Ease = forma de la tangente: **plana entrando = asienta; plana saliendo = arranca lento**. Reparte el ease de forma asimétrica para dar carácter.
- [ ] Spacing = cambio de valor por frame, **no** densidad de keys. Da contraste (rápidos muy rápidos, lentos muy lentos); evita el spacing uniforme robótico.
- [ ] Para **overshoot/settle**: key un pelín más allá + key de vuelta, y rompe la tangente auto-clamp (que lo mata por diseño).
- [ ] **Overlap** = desfasar 2–4 frames las keys de los canales hijos respecto a los padres.
- [ ] Holds de personaje = **moving holds** (deriva mínima), nunca dos keys idénticas con curva plana (dead hold = congelado).
- [ ] En **blocking keyea completo** (Key All); el keying selectivo por canal es solo para el pulido/overlap.
- [ ] **Menos keys, mejor colocadas**: la curva más editable es la de menos keys que logra la forma; borra las redundantes.
- [ ] Limpia el **jitter** (zigzag fino) siempre; en mocap el cleanup es la mitad del trabajo, no un extra.
- [ ] Elige **cuaternión** para robustez (camino corto, sin gimbal) o **Euler** si necesitas giros > 180°; sé consciente del resample del motor.
- [ ] Ciclos con **modificador de curva**: Repeat con **Offset** para locomoción que avanza; Mirrored para vaivenes.
- [ ] Los **modificadores no se exportan**: hornéalos a keys o resuélvelos con Loop Time/Loop Pose del import.
- [ ] **Verifica la curva YA importada en Unity**, no solo en el DCC: la reducción de keyframes puede aplanar tu ease sutil.
- [ ] En Unity los clips importados son **read-only**: edita en el DCC o copia keyframes a un clip nuevo.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Aceptar tangentes bezier por defecto en todo → look flotante/gomoso | La suavidad se gana editando handles; asigna ease asimétrico a mano, no dejes el auto-smooth |
| Convertir de stepped a spline y dar por terminado | La conversión siempre ensucia: polish es la fase real (arcos, overshoot, foot slide) |
| Sobre-keyar (una key por frame "por si acaso") | Menos keys mejor puestas; cada key extra es deuda de mantenimiento cuando cambie el timing |
| Confundir "keys juntas en el tiempo" con "movimiento lento" | La velocidad es el cambio de VALOR por frame (pendiente), no la densidad de keys |
| `Clamped Auto` comiéndose el overshoot → movimiento muerto | Romper a Free/Broken y empujar el handle, o meter key extra de overshoot+settle |
| Diagnosticar "la animación flota" en bloque | Aislar el canal culpable (casi siempre `locY` en saltos, o un eje de rotación) |
| Hold con dos keys idénticas → personaje congelado (dead hold) | Moving hold: deriva mínima en la segunda key; evita tramos planos largos en canales de personaje |
| Keyar selectivo en blocking → canales que se arrastran (partes zombis) | Key All en blocking; selective solo para overlap/pulido |
| Jitter de mocap sin limpiar → temblor en pantalla | Filtrar/simplificar antes de retimear; el cleanup es parte del pipeline, no opcional |
| Rotación que da un flip brusco (359°→0°) | Gimbal/Euler: trabajar en cuaternión o filtrar las curvas Euler |
| Confiar en un modificador de ciclo/Noise que el motor no importa | Hornear a keys reales o usar Loop Time/Loop Pose; verificar qué sobrevive al export |
| Pulir un ease sutil que la compresión de Unity aplana | Verificar el clip importado; subir precisión bajando el Rotation/Position Error si hace falta |
| Editar la curva sobre el clip importado en Unity (read-only) | Volver al DCC, o copiar keyframes a un clip nuevo editable |
| Clips de locomoción que patinan en el blend tree | Sincronizar los contactos en el mismo tiempo normalizado en el DCC; que sobreviva al sampling [ver: unity/animacion-unity] |

## Fuentes

**Bases sintetizadas (repo El Estudio):**
- [ver: gamedev/animacion] — 12 principios en gameplay, anatomía de ataque (wind-up/active/recovery), timing y snappiness, blend trees a nivel concepto, procedural. Este archivo aporta la CRAFT de curvas que ese asume.
- [ver: unity/animacion-unity] — consumo en motor: Animator, blend trees, avatar masks, compresión de import, root motion, eventos. Este archivo cubre el lado autoría de las mismas curvas.

**Fuentes web verificadas (fetch OK esta sesión, jul-2026):**
- **Unity Manual — Editing Animation Curves / Animation window** (`animeditor-AnimationCurves.html`) — keys vs keyframes, vista Curves vs Dopesheet, interpolación de rotación cuaternión (camino corto, límite 180°) vs Euler (giros grandes, gimbal).
- **Unity Manual — Editing Curves** (`EditingCurves.html`) — tipos de tangente verificados: Clamped Auto (default, anti-overshoot), Auto (legacy), Free Smooth, Flat, y Broken Free/Linear/Constant.
- **Unity Manual — Animation Clip import & compression** (`class-AnimationClip.html`) — Anim. Compression Off/Keyframe Reduction/Optimal; Rotation Error (grados) y Position/Scale Error (%); regla `delta < original × tolerancia`; Resample Curves (Euler→cuaternión, una key por frame, ON por defecto).
- **Unity Scripting API — `Keyframe`** (`ScriptReference/Keyframe.html`) — inTangent/outTangent, inWeight/outWeight, `weightedMode` (None→Hermite, con peso→Bézier), peso por defecto 1/3.
- **Unity Manual — Importing Animation from external sources** (`AnimationsImport.html`) — import de FBX/.blend/.ma/.max, takes desde MotionBuilder, clips importados **read-only** (editar copiando keyframes a un clip nuevo).

**Fuentes reales NO verificadas en esta sesión (marcadas por honestidad):**
- **Blender Manual — Graph Editor / F-Curves & Modifiers** (`editors/graph_editor/fcurves/introduction.html` y `modifiers.html`) — modos de interpolación Constant/Linear/Bezier, tipos de easing, handle types (Free/Aligned/Vector/Automatic/Auto Clamped), extrapolación Constant/Linear, y el modificador **Cycles** (Repeat Motion / Repeat with Offset / Repeat Mirrored) + Noise + Stepped. ⚠️ El fetch devolvió **HTTP 403** las dos veces esta sesión; la terminología descrita es funcionalidad estándar y estable de Blender, pero NO se re-verificó contra la página hoy — confirmar nombres exactos en la versión concreta de Blender antes de citar valores literales.
- **Richard Williams — *The Animator's Survival Kit*** (libro canónico, no URL) — jerarquía extremes/breakdowns/inbetweens, spacing/timing charts, ease in/out como reparto de spacing. Citado a nivel de CONCEPTO (idea central), no de página.
- **Mixamo (Adobe) / mocap** — datos mocap densos (key por frame) que motivan el cleanup y la reducción de keyframes. ⚠️ El fetch a `helpx.adobe.com/.../mixamo-faq.html` hizo **timeout** esta sesión; el punto "mocap = denso por frame" queda sostenido de forma independiente por la opción **Resample Curves** de Unity (verificada). Detalle propio de mocap en [ver: mocap-librerias].
