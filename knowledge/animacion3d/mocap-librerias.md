# Motion capture y librerías de animación

> **Cuando cargar este archivo:** al decidir de dónde sale la animación de un personaje humanoide — capturar mocap, comprar/bajar una librería (Mixamo, Asset Store), o keyframear a mano —, al retargetear clips de mocap a tu rig, al limpiar mocap (ruido, foot sliding), al mezclar mocap con keyframe, o al evaluar IA generativa de movimiento (text-to-motion) a 2026. Es la fase de **producción 3D general**: la ejecución concreta en Blender (mapeo de huesos, ARP Remap/Rokoko/Copy Rotation, bake) está en [ver: animacion-blender/retarget-mocap]; el consumo en Unity está en [ver: unity/animacion-unity]; el retargeting técnico Humanoid en [ver: rigging/rig-a-unity].

Este archivo NO repite los 12 principios ni el game-feel del ataque (wind-up/active/recovery, hitstop, telegraphing) — eso vive en [ver: gamedev/animacion] y [ver: gamedev/game-feel]. Aquí: **de dónde viene el movimiento y cómo convertirlo en algo shippeable**.

---

## 1. Qué es el mocap y la verdad central

**Mocap** = capturar el movimiento de un actor real y mapearlo a un esqueleto digital. No produce animación terminada: produce **datos de rotación por hueso por frame**, densos y crudos.

**La verdad que gobierna todo el archivo:** el mocap es un **punto de partida**, nunca el producto final. Da realismo, peso y matiz "gratis" que keyframear a mano cuesta horas — pero llega con ruido, con las proporciones y el timing del actor (no los del personaje ni los del gameplay), y sin la exageración/appeal que hace que un juego se sienta como ese juego. **El 60-70% lo da la captura; el 30-40% restante (limpieza + pulido + game-feel) lo pone el animador** — y ese tramo es no negociable.

### Tipos de captura (de más caro/preciso a más barato/ruidoso)

| Sistema | Cómo | Coste / acceso (2026) | Calidad | Para indie |
|---|---|---|---|---|
| **Óptico con marcadores** (Vicon, OptiTrack) | Cámaras IR + traje de marcadores en volumen calibrado | Estudio: alquiler por día, caro | Gold standard | Solo alquilando un estudio para una tanda |
| **Inercial / IMU** (Rokoko Smartsuit, Movella/Xsens) | Sensores en el traje, sin cámaras; funciona en cualquier sitio | Traje: inversión de hardware (Rokoko el más barato del grupo; Xsens mucho más) | Bueno; **sufre drift** posicional y magnético | Viable si vas a capturar mucho tú mismo |
| **Markerless por vídeo/IA** (Move.ai, Rokoko Vision, DeepMotion) | Red neuronal infiere la pose desde vídeo normal | Gratis–barato (ver §4) | Menor: jitter, foot sliding, sin dedos finos | **La opción real del solo dev** |
| **Librería pre-hecha** (Mixamo, Asset Store) | Clips ya capturados y limpiados por terceros | Gratis (Mixamo) a de pago | Genérica pero limpia | El punto de entrada por defecto |

Para un dev solo, "hacer mocap" casi nunca significa montar un volumen óptico: significa **bajar una librería o pasar un vídeo por una IA**. Capturar en estudio o comprar un traje IMU es una decisión de coste real, no un default.

---

## 2. ¿Mocap o keyframe a mano? Decisión para dev solo/indie

No es "mejor uno u otro": cada animación cae de un lado. Los principios de por qué keyframe gana en gameplay están en [ver: gamedev/animacion] (Timing, Anticipation, Follow-through); aquí la decisión de **origen del asset**.

| La animación es… | Origen recomendado | Por qué |
|---|---|---|
| Locomoción humanoide realista (walk/run/idle/turn) | **Mocap/librería** + limpieza | El realismo del peso humano es caro de keyear; mocap lo da directo [ver: animacion3d/ciclos-locomocion] |
| Relleno / fondo / NPCs, ambientación, cinemática larga | **Mocap/librería** | El volumen mata; nadie mira el timing exacto de un NPC de fondo |
| Ataque/verbo **firma** del jugador (lo que hace 10.000 veces) | **Keyframe** (o mocap muy pulido) | Necesita snappiness, exageración y silueta propia — game-feel, no realismo [ver: animacion3d/animacion-combate] |
| Cualquier cosa estilizada / cartoon / exagerada | **Keyframe** | El mocap es literal; la exageración es una decisión de autor |
| Criatura no humana, cuadrúpedo, mecánico | **Keyframe / procedural** | El mocap humanoide no mapea; las librerías son bípedas [ver: rigging/rigs-mecanicos] |
| Timing atado a frames de gameplay (i-frames, hitboxes) | **Keyframe** | Necesitas control frame-a-frame que el mocap no te da [ver: unity/animacion-unity §9] |

**Regla operativa:** usa mocap/librería para el **tejido conectivo realista** (moverse por el mundo) y keyframe para la **identidad** (lo que define al personaje y al feel). En medio: mocap como base + pase de keyframe encima (§6).

---

## 3. Mixamo a fondo (Adobe, gratis)

Dos productos en uno, gratis con cuenta de Adobe (verificado: Adobe adquirió Mixamo en 2015; sigue operativo — Wikipedia). Es el punto de entrada estándar para personajes humanoides.

### 3a. Auto-Rigger
- Subes una **malla humanoide en T/A-pose** (FBX/OBJ/ZIP). Colocas unos pocos marcadores sobre articulaciones clave (barbilla, muñecas, codos, rodillas, ingle — **posición exacta y cantidad NO verificadas contra fuente primaria esta sesión**, descritas por uso general del producto). Una red neuronal infiere dónde están los miembros e **inserta esqueleto + skin weights** automáticamente ("The AutoRigger applies machine learning to understand where the limbs of a 3D model are and to insert a 'skeleton', or rig, into the 3D model as well as calculating the skinning weights" — Wikipedia, verificado 2026-07-20).
- Salida: personaje riggeado con esqueleto de prefijo `mixamorig:` (incluye dedos; **cantidad exacta de huesos NO verificada** contra fuente primaria — no la cites como dato duro), listo para animar con la librería.
- Nota 2026: la retención de mallas subidas en servidor de Adobe se discontinuó; puedes subir y riggear temporalmente, pero **guarda tu FBX local** (Wikipedia). El auto-rig NO hace facial ni corrige topología mala [ver: modelado/topologia] [ver: rigging/skinning-weights].

### 3b. Librería de animaciones
- Miles de clips humanoides (derivados de mocap + keyframe pulido) que **retargetean a cualquier humanoide compatible** por el naming estándar.
- Descarga: **FBX** (con skin, o "animación sola" para aplicar a otro rig) o **DAE**. Checkbox **"In Place"** = quita el desplazamiento raíz (para mover el personaje por código/root motion, no por la animación).
- En Unity: importas el FBX con **Animation Type = Humanoid** y sus clips corren sobre TU personaje vía Avatar compartido — flujo detallado y verificado en [ver: rigging/rig-a-unity §4] y [ver: unity/animacion-unity §1].

### Límites de Mixamo (por qué no es la respuesta a todo)

| Límite | Detalle |
|---|---|
| **Solo bípedo humanoide** | Nada de cuadrúpedos, criaturas ni props articulados |
| **Calidad genérica** | Es una librería compartida: tu walk es el walk de otros 10.000 juegos. Sin identidad |
| **Esqueleto fijo** | Skeleton `mixamorig:` cerrado; dedos incluidos pero genéricos, **sin facial** |
| **Foot sliding** | Al retargetear a proporciones distintas de las del actor, los pies patinan — cleanup obligatorio (§5) |
| **Timing no editable en Mixamo** | Ajustas velocidad global, no curvas; el pulido fino se hace en Blender/Unity |

### Licencia
Contenido de Mixamo (personajes + animaciones) es **royalty-free para usar en tus proyectos**, incluidos comerciales, según la FAQ oficial de Adobe. Restricción típica: **no revender/redistribuir los assets crudos** como producto standalone. ⚠️ La página de la FAQ de Adobe (`helpx.adobe.com/.../mixamo-faq.html`) no se pudo cargar en esta sesión (timeout repetido) — el hecho "royalty-free para uso en proyectos" es la política establecida y ampliamente documentada de Adobe; **confirma el texto exacto de la licencia en la FAQ antes de un lanzamiento comercial grande**.

---

## 4. Otras fuentes: librerías, servicios y mocap por IA

### Librerías de pago (más curadas que Mixamo)
- **Unity Asset Store**: packs game-ready con **root motion** ya horneado y sets temáticos (espada, rifle, unarmed, RPG). Vendors de referencia: MoCap Online, Kubold (Sword&Shield, Rifle, Movement Animset Pro), Explosive. Ventaja sobre Mixamo: curación, cobertura de un moveset completo, root motion listo. Coste: de pago por pack.
- **Marketplaces**: Fab (ex-Unreal Marketplace), **ActorCore** (Reallusion) con mocap premium y retarget a iClone/Blender/Unity, y librerías por suscripción. Verifica siempre que la **licencia** permita uso en tu motor/juego.

### Servicios de mocap
- **Alquiler de estudio óptico** (Vicon/OptiTrack) para una tanda concentrada de captura — la vía de calidad si tienes presupuesto y muchas tomas.
- **Traje IMU propio** (Rokoko Smartsuit / Movella) si vas a capturar de forma continua.

### Mocap por vídeo/IA — estado y coste a 2026 (verificado hoy 2026-07-20)

| Herramienta | Cámaras | Formatos | Extras | Precio (jul-2026) |
|---|---|---|---|---|
| **Rokoko Vision 3.0** | **Mono** (single cam; la dual se retiró ~30 días tras el lanzamiento de v3, el solver monocular la superó) | FBX, BVH | Compatible UE5 Manny/HIK/Mixamo; **sin dedos al lanzamiento** | **Starter gratis: 30 s/mes**; Basic $10/mes (anual) o $12/mes: 600 s/mes |
| **DeepMotion Animate 3D** | Mono (vídeo desde cualquier dispositivo) | FBX, BVH, GLB, MP4 | **Face + hand tracking**, física, **foot locking**, motion smoothing, Rotoscope Pose Editor | Tier gratis existe; **tiers/creditos exactos no publicados en la landing** — confirmar en deepmotion.com |
| **Move.ai** | **Multi-cam** (pro) + app móvil **Move One** | (no listados en la home) | Calidad "comparable a óptico", sin trajes/marcadores | Orientado a enterprise/demo; **sin tier gratis público en la home** (jul-2026) — pricing "book a demo" |

Otras (Plask, Wonder Dynamics/Wonder Studio, Kinetix) existen; **no verifiqué precios/estado 2026** — no cito specs inventadas.

**Lectura práctica:** para un solo dev que quiere una animación puntual realista y no la encuentra en Mixamo, la ruta barata es **grabarte con el móvil y pasarlo por Rokoko Vision o DeepMotion**, luego retargetear (§5) y limpiar (§6). El resultado es "greybox++": suficiente para prototipar y para relleno, casi nunca shippeable como hero sin pulido.

---

## 5. Retargeting: llevar el mocap a TU rig

Un clip de mocap está atado al esqueleto de origen (el actor, o `mixamorig:`). Para que corra en tu personaje hay que **remapear hueso-a-hueso**. Dos caminos:

### Vía Unity Humanoid (el retargeter integrado)
El sistema Humanoid de Unity ES un retargeter: describe la pose en **muscle space** (valores normalizados por rango articular), no en rotaciones crudas, así que **la misma animación corre en cualquier humanoide** aunque las proporciones difieran (Unity Manual — Retargeting, verificado). Requisitos: origen y destino en **Animation Type = Humanoid** con Avatar válido. El flujo de swap de personaje y los settings del Avatar están en [ver: rigging/rig-a-unity §4] y [ver: unity/animacion-unity §1] — no los repito.

- **Root motion / desplazamiento**: el **Body Transform** (centro de masa) es la única curva en world-space; el **Root Transform** se deriva proyectándolo al plano Y y su cambio por frame mueve el GameObject (Unity Manual — Root Motion, verificado). Para mocap de locomoción hacia adelante, **Based Upon = Body Orientation** funciona; para strafe hay que ajustar offset a mano. **Bake Into Pose** Rotation + Y para clips de locomoción (evita rotación/altura no deseada); XZ para idles (evita drift). Detalle de estos toggles en [ver: rigging/rig-a-unity §5].

### Vía Blender (antes de exportar)
Cuando el clip va a un rig **Generic** (criatura, o control fino), o quieres editar antes de Unity, retargeteas en Blender: addons como **Auto-Rig Pro (Remap)**, el **plugin de Rokoko para Blender**, o los retargeters nativos. Mapeas huesos origen→destino, **horneas (bake)** el resultado sobre tu armature, y exportas FBX. La ejecución paso a paso (Build Bones List, rest pose, constraints, bake) está en [ver: animacion-blender/retarget-mocap]; el contrato FBX/escala está en [ver: blender/import-export] y el puente rig↔Unity en [ver: rigging/rig-a-unity].

**Gotcha universal del retargeting:** proporciones distintas entre origen y destino = **foot sliding y penetración** casi garantizados. El retarget resuelve la orientación de los huesos, no los contactos con el suelo. Eso lo arregla la limpieza (§6), no el retargeter.

### Herramientas de retarget en Blender (panorama)

| Herramienta | Fuente típica | Nota |
|---|---|---|
| **Auto-Rig Pro — Remap** | BVH, Mixamo, Rokoko → rig ARP o custom | De pago; el más completo, mapea + hornea + maneja root [ver: rigging/rig-a-unity §7] |
| **Plugin Rokoko para Blender** | Rokoko Studio/Vision, Mixamo, BVH | Gratis; retarget bone-a-bone + import directo de sus capturas |
| **Retargeters nativos / addons libres** | BVH genérico, Mixamo | Cubren lo básico; más trabajo manual de mapeo |

En los tres el patrón es el mismo: **definir esqueleto origen → mapear a huesos destino → bake sobre tu armature → exportar FBX**. La ejecución exacta de cada vía (Build Bones List, rest pose, constraints, bake) está en [ver: animacion-blender/retarget-mocap].

---

## 6. Limpiar mocap: el pulido que SIEMPRE hace falta

Ningún mocap sale usable de la captura. Lista de lo que hay que arreglar, por frecuencia:

| Problema | Qué es | Antídoto |
|---|---|---|
| **Foot sliding** (el #1) | Los pies patinan sobre el suelo en vez de plantarse | **Foot IK / foot lock** + keys de plantado; en Unity foot IK en la capa; en DeepMotion "foot locking"; en Blender plantar y hornear. Casi siempre por retarget a otra escala |
| **Jitter / ruido** | Temblor de alta frecuencia del solver/marcadores | Filtro de suavizado (Butterworth/Gaussian) o **reducción de keys**; en markerless por IA es lo más notorio |
| **Densidad de keys** | Mocap = 1 key por hueso por frame → ilegible e ineditable | **Keyframe reduction/decimation** a curvas editables (curvas limpias en [ver: animacion3d/keyframes-curvas]); o un pase de blocking encima |
| **Penetración / pops** | Manos que atraviesan el cuerpo, saltos de gimbal, contactos sucios | Corregir a mano en los frames de contacto; revisar ejes de rotación |
| **Drift** (IMU) | La posición se va con el tiempo (sensores inerciales) | Re-anclar contactos, recortar la toma, capturar tomas cortas |
| **Falta de holds/appeal** | El mocap rara vez tiene holds limpios ni exageración | Añadir anticipación/holds/exageración a mano — es donde entra el game-feel [ver: gamedev/animacion] |
| **Loop sucio** | Inicio y fin no casan para ciclar | Loop Match / Loop Pose (Unity) o casar poses en Blender [ver: animacion3d/ciclos-locomocion] |

El error mental a evitar: **tratar el mocap como "terminado"**. Es material en bruto. La regla de Cooper (*Game Anim*, base de [ver: gamedev/animacion]) y el oficio del *Animator's Survival Kit* (Richard Williams, canon del craft) aplican igual sobre mocap que sobre keyframe: el peso, el timing y el appeal se **deciden**, no se capturan.

### Pipeline de una animación de mocap, de principio a fin

Orden que evita rehacer trabajo (limpiar antes de retargetear es tirar horas):

1. **Origen** — capturar (móvil→IA / estudio / IMU) o bajar de librería.
2. **Retarget** al esqueleto destino (Unity Humanoid o Blender) → aquí APARECE el foot sliding.
3. **Foot lock / IK** para clavar los pies (lo primero del cleanup, define todo lo demás).
4. **Reducción de keys** a curvas editables [ver: animacion3d/keyframes-curvas].
5. **Filtro de ruido/jitter** en las curvas sucias.
6. **Pase de game-feel**: holds, anticipación, exageración a mano [ver: gamedev/animacion].
7. **Loop** si cicla (casar inicio↔fin) [ver: animacion3d/ciclos-locomocion].
8. **Capas** encima (additive/partial-body, §7).
9. **Export + validación en Unity** (root motion, eventos) [ver: unity/animacion-unity].

---

## 7. Mezclar mocap + keyframe (layering encima del mocap)

Lo más productivo casi nunca es "mocap puro" ni "keyframe puro", sino **capas**:

| Técnica | Qué haces | Referencia |
|---|---|---|
| **Additive encima del mocap** | Respiración, sway, aim offset, lean como capa aditiva sobre la base capturada | [ver: animacion3d/movimiento-secundario] · [ver: unity/animacion-unity §3] |
| **Partial-body por máscara** | Mocap de piernas (locomoción) + upper body keyframeado (combate) vía avatar mask | [ver: animacion3d/capas-estados] · [ver: unity/animacion-unity §3] |
| **Mocap como referencia** | Keyframeas ENCIMA usando el mocap como "vídeo de referencia en 3D", no como final | [ver: animacion3d/keyframes-curvas] |
| **Base mocap + hero frames keyed** | Mocap el tejido realista; keyframeas a mano los frames de impacto/pose firma | [ver: animacion3d/animacion-combate] |

Regla de oro: el mocap te ahorra el 70% aburrido; **inviertes el tiempo ganado en keyframear el 30% que el jugador siente**. No al revés.

---

## 8. IA generativa de animación (text-to-motion) a 2026

Estado real, sin hype. Modelos de investigación que generan movimiento humano desde texto ("a person walks forward and picks something up"):

| Modelo | Qué es | Señal de calidad (verificado) |
|---|---|---|
| **MDM** (Motion Diffusion Model) | Difusión para movimiento; SOTA en su momento en HumanML3D/KIT | Evaluadores prefirieron su salida sobre mocap real el **42%** de las veces; genera variantes diversas del mismo prompt; hace in-betweening/editing (project page, verificado) |
| **MoMask** | Tokenización jerárquica (RVQ) | **FID 0.045** en HumanML3D (vs 0.141 de T2M-GPT); capta acciones sutiles mejor que difusión/autoregresivos previos (project page, verificado) |
| Comerciales/servicios | DeepMotion (text-to-motion además de vídeo), y varios en beta | Specs 2026 no todas verificadas — no invento |

**Para qué SÍ sirve a 2026:**
- Ideación/greybox rápido, relleno, prototipar un moveset antes de invertir en animación real.
- **In-betweening y edición** de movimiento existente (rellenar huecos, variar).

**Límites duros (por qué NO es hero animation):**
- Clips **cortos**, **un solo humanoide**, sin control fino de timing/contactos.
- Foot sliding y jitter igual que cualquier mocap → **necesita limpieza + retarget** de todas formas (§5-6).
- Cero exageración/game-feel: da movimiento "plausible-realista", no "snappy con identidad".
- No es frame-accurate para hitboxes/i-frames.
- Procedencia del dataset y **licencia** a menudo turbias — cuidado en comercial.

Veredicto 2026: **igual de útil que un mocap barato para greybox y fondo; no reemplaza la animación firma.** Trátalo como una fuente más de material en bruto, sujeto al mismo 30-40% de pulido.

---

## 9. Cuándo la librería genérica basta y cuándo el juego necesita animación propia

El eje es **identidad**. Una librería genérica (Mixamo, Asset Store, IA) es correcta hasta que la animación **es el personaje**.

| Genérico basta | Necesitas animación propia |
|---|---|
| Prototipo / greybox / game jam | Producto que debe sentirse pulido |
| NPCs y personajes de fondo | Personaje jugable / protagonista |
| Movimientos realistas no firmados (caminar, sentarse) | Verbos que el jugador hace miles de veces (deben sentirse únicos y responsivos) [ver: gamedev/game-feel] |
| Cobertura amplia rápida y barata | Silueta/personalidad reconocibles [ver: gamedev/animacion, Appeal] |
| Humano estándar realista | Estilo propio, exageración, cartoon, criatura |

**El test:** si dos juegos distintos se verían **idénticos** haciendo esta animación, y es un momento **core o hero**, necesitas animación propia. El mocap y la librería dan **realismo**; no dan **appeal ni identidad** — eso es trabajo de keyframe/pulido (principio de Appeal, [ver: gamedev/animacion]).

**Estrategia de ship realista para un solo dev:** greybox y rellena TODO con Mixamo/IA para tener el juego jugable de una; luego **reemplaza los verbos hero con animación propia** a medida que el proyecto madura. Nunca al revés (no pulas la animación de un NPC de fondo mientras el ataque del jugador sigue siendo un Mixamo genérico).

---

## Reglas prácticas

- [ ] Trata TODO mocap (capturado, de librería o de IA) como **material en bruto**: presupuesta el 30-40% de limpieza + pulido antes de considerarlo hecho.
- [ ] Mocap/librería para tejido conectivo realista (locomoción, idles, fondo); keyframe para identidad y game-feel (verbos hero, ataques).
- [ ] Mixamo primero para humanoides: gratis, auto-rig + librería. Baja el FBX y **guárdalo local** (Adobe ya no retiene mallas).
- [ ] Mixamo → Unity: `Animation Type = Humanoid`, Avatar compartido; usa "In Place" si mueves por root motion/código [ver: unity/animacion-unity §1].
- [ ] Confirma la licencia exacta en la FAQ de Adobe antes de un lanzamiento comercial grande (royalty-free para uso, no revender crudos).
- [ ] Para una animación realista que Mixamo no tiene: grábate con el móvil → Rokoko Vision o DeepMotion → retarget → limpieza. Es greybox++, no hero.
- [ ] Retargeting: Unity Humanoid (muscle space) para humanoides; Blender (Auto-Rig Pro Remap / plugin Rokoko) para Generic o edición previa [ver: rigging/rig-a-unity].
- [ ] Espera foot sliding SIEMPRE que retargetees a proporciones distintas; resuélvelo con foot IK/lock + keys de plantado, no con el retargeter.
- [ ] Root motion de mocap: Based Upon = Body Orientation, Bake Into Pose Rotation+Y en locomoción, XZ en idles [ver: rigging/rig-a-unity §5].
- [ ] Reduce keys (decimation) del mocap a curvas editables antes de tocarlo a mano [ver: animacion3d/keyframes-curvas].
- [ ] Añade holds, anticipación y exageración a mano sobre el mocap — es donde entra el game-feel [ver: gamedev/animacion].
- [ ] Mezcla por capas: additive (respiración/lean/aim) y partial-body por máscara (piernas mocap + torso keyed) [ver: unity/animacion-unity §3].
- [ ] IA text-to-motion: úsala para greybox, relleno e in-betweening; nunca para el verbo hero sin pulido; revisa la procedencia/licencia del modelo.
- [ ] Verifica que la licencia de cualquier pack de Asset Store/marketplace cubra tu motor y distribución comercial.
- [ ] Test de identidad: si dos juegos se verían idénticos haciendo esta animación y es core/hero → animación propia.
- [ ] Estrategia de ship: greybox con librería primero, reemplaza los verbos hero por animación propia después. Nunca pulir lo de fondo antes que lo core.

## Errores comunes

| Error | Antídoto |
|---|---|
| Tratar el mocap como "terminado" al salir de la captura | Es bruto: cleanup (§6) + game-feel a mano SIEMPRE |
| Esperar que Mixamo dé identidad al personaje | Mixamo es genérico compartido; los verbos hero se keyframean [ver: gamedev/animacion] |
| Ignorar el foot sliding tras retargetear | Foot IK/lock + keys de plantado; nace de proporciones distintas actor↔personaje |
| Usar mocap para un ataque que necesita snappiness | Keyframe: el mocap trae el timing del actor, no el del gameplay [ver: animacion3d/animacion-combate] |
| Aplicar mocap humanoide a un cuadrúpedo/criatura | Las librerías son bípedas; criatura = keyframe/procedural [ver: rigging/rigs-mecanicos] |
| Editar mocap directamente sobre 1 key/frame por hueso | Reducir keys a curvas antes de tocar [ver: animacion3d/keyframes-curvas] |
| Root motion de un strafe con Based Upon = Body Orientation | Body Orientation solo sirve para locomoción frontal; strafe pide offset manual (Unity Root Motion) |
| Subir la malla a Mixamo y no guardar el FBX riggeado | Adobe ya no retiene mallas; descarga y versiona local |
| Comprar/usar un pack sin leer su licencia comercial | Verificar licencia por motor + distribución antes de integrar |
| Creer que la IA text-to-motion reemplaza al animador | Da clips cortos plausibles con jitter/foot sliding; mismo 30-40% de pulido, sin game-feel |
| Pulir la animación de un NPC de fondo antes que el verbo del jugador | Prioriza siempre lo core/hero; el fondo se queda genérico más tiempo |
| Presentar precios de mocap por IA sin fecha | Los tiers cambian rápido; date-stampea (verificado jul-2026) y reconfirma |

## Fuentes

- **Retargeting Humanoid Animations** — Unity Manual 6000.2 (`Retargeting.html`) — el Avatar/muscle system como retargeter: misma animación en cualquier humanoide con Avatar válido; requisitos y flujo de swap de personaje. Verificado 2026-07-20.
- **Root Motion / Body Transform** — Unity Manual 6000.2 (`RootMotion.html`) — Body Transform (centro de masa, única curva world-space), Root Transform proyectado a Y, Bake Into Pose (Rotation+Y/XZ), Based Upon Body Orientation para mocap frontal y su fallo en strafe. Verificado 2026-07-20.
- **Rokoko Vision 3.0** — rokoko.com/products/video — markerless mono (dual retirada), export FBX/BVH, compat UE5 Manny/HIK/Mixamo, sin dedos al lanzamiento; Starter gratis 30 s/mes, Basic $10-12/mes 600 s/mes. Verificado 2026-07-20.
- **DeepMotion Animate 3D** — deepmotion.com/animate-3d — vídeo→animación, face+hand tracking, física, foot locking, motion smoothing, Rotoscope Pose Editor; FBX/BVH/GLB/MP4; tier gratis (tiers exactos no publicados en la landing). Verificado 2026-07-20.
- **Move.ai** — move.ai — markerless multi-cam (calidad "comparable a óptico") + app móvil Move One; sin tier gratis público en la home, pricing por demo (jul-2026). Verificado 2026-07-20.
- **Motion Diffusion Model (MDM)** — Tevet et al., project page (guytevet.github.io/mdm-page) — text-to-motion por difusión; humanos prefirieron su salida a mocap real el 42%; SOTA HumanML3D/KIT; edición/in-betweening. Verificado 2026-07-20.
- **MoMask** — Guo et al., project page (ericguo5513.github.io/momask) — RVQ jerárquico; FID 0.045 en HumanML3D vs 0.141 de T2M-GPT; capta acciones sutiles. Verificado 2026-07-20.
- **Mixamo** — Wikipedia — Auto-Rigger (ML inserta esqueleto), animation store (mocap + keyframe), propiedad de Adobe desde 2015, Fuse/Face Plus discontinuados, retención de mallas discontinuada; formatos FBX/DAE. Verificado 2026-07-20. ⚠️ La FAQ de Adobe (`helpx.adobe.com/.../mixamo-faq.html`) no cargó esta sesión (timeout); la licencia royalty-free-para-uso es política establecida de Adobe — reconfirmar el texto exacto antes de comercial.
- **Bases sintetizadas de El Estudio** (no repetir, referenciar):
  - [ver: gamedev/animacion] — *Game Anim* (Jonathan Cooper) y los 12 principios en gameplay; Timing/Anticipation/Follow-through, telegraphing, hitstop. El "porqué" de keyframe vs mocap en game-feel.
  - [ver: unity/animacion-unity] — consumo del mocap en Unity: Animator, blend trees, layers/avatar mask, IK, eventos, culling.
  - [ver: rigging/rig-a-unity] — Humanoid vs Generic, Avatar/muscle space, retargeting/Mixamo, root motion, Avatar Mask. El puente técnico rig↔Unity.
- **The Animator's Survival Kit** — Richard Williams — canon del craft de animación (a nivel concepto): timing, spacing, holds y appeal se deciden, no se capturan. Aplica igual sobre mocap.
