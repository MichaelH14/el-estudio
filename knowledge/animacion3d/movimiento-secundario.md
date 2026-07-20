# Movimiento secundario y dinámico

> **Cuando cargar este archivo:** al decidir cómo se mueve TODO lo que cuelga de un personaje 3D de juego — pelo, cola, capa, orejas, faldón, colgantes, correas, pecho, antenas — y quién lo mueve: el animador a mano (overlap/follow-through keyframeado) o un solver en runtime (spring/jiggle bones, cloth). Cubre la técnica de animación de arrastre, el concepto de huesos dinámicos, el criterio simular-vs-hornear, y el presupuesto en móvil. La ejecución concreta en Blender (offset de keys en el graph editor, hornear la sim a clip) es la fase siguiente [ver: keyframes-curvas para el concepto de curva/offset]. El consumo del rig en Unity (Animator, avatar mask, root motion) está en [ver: unity/animacion-unity]. La altitud game-feel de esto (springs de lean/recoil, "vida gratis") ya está en [ver: gamedev/animacion §5,§7] y [ver: gamedev/game-feel §5]: aquí va la profundidad de PRODUCCIÓN 3D, no se repite.

## 1. Qué es y qué NO cubre este archivo

**Movimiento secundario** = el que NO comanda directamente el gameplay ni la pose principal, sino que *resulta* de ella: partes flojas que arrastran, oscilan y asientan por inercia. Es la capa que convierte una pose técnicamente correcta en un personaje que parece tener masa y estar vivo.

Dos formas de conseguirlo, y este archivo trata de elegir entre ellas:

| Vía | Quién lo produce | Coste de autor | Coste de runtime | Reactivo |
|---|---|---|---|---|
| **A mano** (overlap/follow-through keyframeado) | El animador, hueso por hueso | Alto (cada clip) | Cero | No — congelado en el clip |
| **Simulado en runtime** (jiggle/spring bones, cloth) | Un solver spring-damper cada frame | Cero por clip | CPU por cadena/vértice | Sí — reacciona al movimiento real |
| **Horneado** (sim → keyframes) | Solver una vez, luego es animación | Bajo | Cero (solo curvas extra) | No — congelado |

Ya cubierto en otros archivos (no se repite, se referencia):
- Los 12 principios a nivel game-feel, incl. follow-through/overlap/secondary action → [ver: gamedev/animacion §1,§5].
- Springs procedurales de lean/bob/recoil (la MISMA matemática spring-damper aplicada a la cámara y al cuerpo) → [ver: gamedev/animacion §7].
- Deform bones vs control bones, 4 influencias/vértice, export deform-only → [ver: rigging/esqueletos-armature §6,§10].
- Damped Transform, avatar mask y additive layers como herramientas Unity → [ver: unity/animacion-unity §3,§8].

## 2. Overlap, follow-through y drag: la técnica a mano

Los tres son principios de Disney (Thomas & Johnston, *The Illusion of Life*, 1981; sistematizados por Richard Williams como "successive breaking of joints"). Verificado (Wikipedia, *Twelve basic principles of animation*):

| Principio | Definición exacta | En el rig 3D |
|---|---|---|
| **Follow-through** | Las partes flojas **siguen moviéndose después** de que el cuerpo para, con amortiguación de oscilación, y son "tiradas de vuelta" hacia el centro de masa | El peso de un golpe/parada se vende AQUÍ, no alargando el wind-up [ver: gamedev/animacion §5] |
| **Overlapping action** | Distintas partes se mueven en **timings distintos**: el brazo va en otro tiempo que la cabeza | Desfasar las keys del hueso hijo respecto al padre |
| **Drag** | Las partes tardan **varios frames en arrancar** cuando el movimiento empieza (inercia de salida) | La punta llega tarde: la base lidera, la punta arrastra |

**Cómo se keyframea (production depth):** el arrastre a mano es un **offset temporal en cadena**. Sobre una cola/coleta de N huesos:
1. Anima primero el hueso **base** (el que cuelga del cuerpo) — o simplemente hereda del padre.
2. Copia esa curva a cada hueso hijo y **desplázala 2–4 frames más tarde** por eslabón (la cifra exacta se calibra: más masa/longitud = más retardo).
3. La punta acaba con el mayor desfase → efecto látigo. Al parar, cada eslabón sobrepasa la pose de reposo y vuelve con una oscilación que decae (2–3 rebotes decrecientes). El detalle de curva/offset en el editor es fase Blender [ver: keyframes-curvas].

**"Successive breaking of joints" (Williams):** en un brazo que se detiene, hombro lidera → codo sigue → muñeca después → dedos al final. En una capa: cuello/hombros lideran, dobladillo llega último. Nunca todo a la pose final en el mismo frame — eso es lo que hace que una animación se sienta "de robot".

**Dónde vale la pena animarlo a mano** (en vez de simular): momentos hero y cinemáticas donde el timing es dirección de arte y no puedes fiarte de un solver — el aleteo de capa de una ejecución, el latigazo de cola de un remate [ver: animacion-combate], una animación firma que se ve en primer plano. Para movimiento ambiental genérico (pelo meciéndose al caminar, colgante que tiembla), simular sale más barato y reacciona solo.

## 3. Spring/jiggle bones: el concepto

Un **jiggle bone / spring bone** es un hueso **extra** del esqueleto que:
- **SÍ deforma la malla** (tiene weights: el pelo/cola/capa está skinneado a él) — a diferencia de un hueso de control [ver: rigging/esqueletos-armature §6].
- **NO lo keyframea el animador** — no lleva animación autorizada; un solver lo mueve en runtime.
- **Cuelga de un hueso del cuerpo** como padre: raíz de pelo → `Head`; raíz de capa → `Chest`/`Spine`; raíz de cola/faldón → `Hips`. El solver lee el movimiento del padre cada frame y deja que la cadena arrastre y sobrepase.

En el rig, cada elemento cuelga de un hueso de cuerpo y define una cadena. Longitudes y colliders típicos (orden de magnitud, calibrar):

| Elemento | Hueso padre | Longitud de cadena | Colliders que evitan clipping |
|---|---|---|---|
| Coleta / flequillo | `Head` | 3–5 | Sphere en la cabeza/cuello |
| Pelo largo | `Head` | 5–8 | Sphere cabeza + capsule hombros/espalda |
| Cola de animal | `Hips` | 5–10 | Capsule en muslos/glúteos |
| Orejas / antenas | `Head` | 2–4 | — (rara vez clippean) |
| Capa (tira) | `Chest`/`Spine` | 4–6 por tira | Capsule espalda + muslos |
| Faldón / taparrabos | `Hips` | 3–5 por tira | Capsule en ambos muslos |
| Bufanda / correa suelta | `Neck`/`Chest` | 4–6 | Sphere/capsule torso |
| Colgante / pendiente | hueso más cercano | 1–3 | — o pecho |

- **Colliders**: son los que impiden que el pelo atraviese la cabeza o la falda los muslos. Menos es más — un sphere en cabeza y un capsule por muslo cubren el 90% de casos; cada collider extra multiplica el chequeo por cadena (§8).
- Van en su propia **bone collection** (nómbrala `DYN`/`JIGGLE`) para que sea obvio cuáles no se tocan a mano [ver: rigging/esqueletos-armature §6].
- Son **deform bones normales** al exportar: salen al FBX con Only Deform Bones ON, cuentan contra el presupuesto de huesos y contra el coste de skinning (4 influencias/vértice sigue siendo el objetivo) [ver: rigging/esqueletos-armature §10].
- Piezas **rígidas** (hebilla, placa de armadura, colgante duro) NO son jiggle: un hueso, weight 100%, y si acaso una cadena de 1–2 eslabones para que oscile como péndulo — no cloth [ver: rigging/rigs-mecanicos].

## 4. La matemática común: todo es un spring-damper

Todos los solvers (Dynamic Bone, VRM SpringBone, Damped Transform, Magica, el spring de lean de [ver: gamedev/animacion §7]) son **el mismo muelle amortiguado**. Cambia el nombre del parámetro, no la física:

| Concepto físico | Qué hace | Dynamic Bone¹ | VRM SpringBone² | Damped Transform³ | Cloth (Unity)⁴ |
|---|---|---|---|---|---|
| **Rigidez / stiffness** | Fuerza que devuelve a la pose de reposo (más = más tieso, menos swing) | `Stiffness` / `Elasticity` | `Stiffness Force` | *(implícito en el weight)* | `Stretching`/`Bending Stiffness` |
| **Amortiguación / damping** | Con qué rapidez muere la oscilación (más = menos rebotes) | `Damping` | `Drag Force` | `Damp Position` / `Damp Rotation` | `Damping` |
| **Gravedad** | Tira hacia abajo (peso del pelo/tela) | `Gravity` | `Gravity Power` + `Gravity Direction` | — | `Use Gravity` |
| **Fuerza externa / viento** | Empuje constante o de viento | `Force` | *(vía viento del entorno)* | — | `External`/`Random Acceleration` |
| **Inercia / ignorar al padre** | Cuánto del movimiento del padre se ignora (evita que el snap del cuerpo lo dispare) | `Inert` | *(bone `Center`)* | `Weight` | `World Velocity/Acceleration Scale` |
| **Grosor de colisión** | Radio para chocar con colliders | `Radius` | `Hit Radius` | — | radio de sphere/capsule |

¹ Verificado del asset (2026-07-20): existe y usa `DynamicBoneCollider`; la lista exacta de campos NO la devolvió el fetch de esta sesión — los nombres son los campos públicos documentados del componente, tratar como referencia, no re-verificados este fetch.
² Verificado (vrm.dev): `Stiffness Force`, `Gravity Power`, `Gravity Direction`, `Drag Force`, `Hit Radius`, `VRMSpringBoneColliderGroup`, y un GameObject **Center** que reancla el cálculo para que el personaje no "vibre" al desplazarse.
³ Verificado (Unity Animation Rigging 1.3): `Weight` (0–1), `Constrained Object`, `Source`, `Damp Position` (0–1), `Damp Rotation` (0–1), `Maintain Aim` (bool).
⁴ Verificado (Unity Manual, `class-Cloth.html`) — ver §7.

Regla de tuning universal: **subir stiffness hasta que deje de parecer gelatina; subir damping hasta que no rebote como resorte de dibujo animado; bajar el peso/inercia sobre el padre hasta que el snap del cuerpo no dispare la cadena.** Los valores exactos se calibran mirando en movimiento, nunca a ojo en pose estática — misma filosofía que el juice [ver: gamedev/game-feel §Reglas].

**Loop de tuning (production):** reproducir la animación MÁS agresiva del set (carrera con giro brusco, esquiva, aterrizaje) y ajustar sobre ELLA, no sobre el idle — el idle no revela el over-swing. Orden: (1) stiffness para el rango de swing general, (2) damping para cuántos rebotes al parar, (3) gravedad para el reposo colgante, (4) colliders para clipping, (5) inercia/reanclado para el desplazamiento rápido. Muchos solvers arrancan la cadena desde la bind pose: dales **1–2 frames de settle** antes de capturar/grabar, o pre-warm, o el primer frame saldrá con la cadena estirada.

## 5. Opciones en Unity para movimiento secundario

| Opción | Qué es | Coste runtime | Colisión | Cuándo |
|---|---|---|---|---|
| **Overlap a mano** (keyframes) | Offset de keys en el clip | Cero | — | Hero, cinemática, timing de arte [ver: animacion-combate] |
| **Damped Transform** (Animation Rigging) | Constraint built-in, hueso a hueso, corre sobre C# Animation Jobs | Barato | No (solo retardo) | Pocos colgantes: antenas, coletas, una cola simple [ver: unity/animacion-unity §8] |
| **Dynamic Bone** (asset, Will Hong) | El clásico de spring bones; $20, v1.3.4 (may-2024), Built-in/URP/HDRP, min Unity 2019.4 (verificado 2026-07-20) | CPU por cadena | Sí (`DynamicBoneCollider`) | Estándar histórico; simple y probado |
| **Magica Cloth 2** (magicasoft.jp) | Sucesor moderno: modos **BoneCloth** (cadenas de huesos/spring) y **MeshCloth** (tela por malla), viento, self-collision, colliders Sphere/Capsule/Plane (verificado 2026-07-20) | Multihilo⁵ | Sí | Default moderno; escala mejor a móvil/multitudes |
| **VRM SpringBone** | Ecosistema VRM/avatares (VTuber) | CPU | Sí (`ColliderGroup`) | Avatares VRM, no juego genérico |
| **Cloth component** (Unity built-in) | Sim de tela real por vértice sobre SkinnedMeshRenderer | Caro (§7) | Solo sphere/capsule/conic | 1–2 capas/banderas hero |

⁵ Magica Cloth 2 se promociona como sucesor **multihilo** de Dynamic Bone; la implementación exacta (Job System/Burst/DOTS) NO se confirmó en el fetch de esta sesión — verificar en su doc antes de citarla como argumento de rendimiento. Su razón de existir es precisamente el salto de coste sobre Dynamic Bone.

**Orden de ejecución (gotcha de raíz):** los solvers de spring bones leen la pose YA animada, así que corren **después** del Animator, en `LateUpdate` (Dynamic Bone, Magica, VRM) o en el pase de Animation Rigging (Damped Transform, vía Animation Jobs tras el Animator). Si un script tuyo mueve esos huesos en `Update`, el solver lo pisa. No keyframees un hueso que también controla un solver — mismo conflicto que tween-vs-clip [ver: unity/animacion-unity §4].

## 6. Cloth simulation: cuándo tela real vs cadenas de huesos

El **Cloth component** de Unity es una sim de tela por vértice. Verificado (Unity Manual, `class-Cloth.html`):
- **Solo funciona sobre `SkinnedMeshRenderer`** (si lo pones en un Mesh Renderer normal, Unity lo reemplaza por uno skinned).
- Parámetros: `Stretching Stiffness`, `Bending Stiffness`, `Damping`, `External Acceleration`, `Random Acceleration`, `World Velocity Scale`, `World Acceleration Scale`, `Friction`, `Use Gravity`, `Use Tethers`.
- **Colisión limitada**: solo sphere, capsule y conic-capsule colliders — **no** reacciona a los colliders arbitrarios de la escena, hay que asignarlos a mano. Es **unidireccional**: "la tela reacciona a esos cuerpos pero no les devuelve fuerza".
- **Self-collision e inter-collision** (params `Inter-Collision Distance` / `Inter-Collision Stiffness`) evitan que la tela se atraviese, pero "pueden llevarse una parte significativa del tiempo total de simulación" (cita del Manual) — es el gasto más caro.
- Constraints pintables (Select / Paint / Gradient) para fijar qué vértices están **anclados** al cuerpo (max coefficient) y cuáles cuelgan **libres** (0) — el trabajo real de configurar una capa: hombros/cuello anclados, dobladillo libre, gradiente entre medias. `Use Tethers` limita el estiramiento uniendo vértices libres a los anclados con constraints tipo cuerda (evita que la tela se descuelgue infinitamente).

**El criterio simular-tela vs huesos:**

| Pregunta | Respuesta → técnica |
|---|---|
| ¿La tela debe **plegarse, drapear, arrugarse** y leerse como tela real? (capa hero en primer plano, bandera al viento, vestido largo) | **Cloth sim** — es lo único que da pliegues reales |
| ¿La tela solo necesita **oscilar/arrastrar** como un plano rígido? (faldón, taparrabos, bufanda, tira de capa, correa) | **Cadenas de huesos** (BoneCloth / Dynamic Bone / spring) — cientos de veces más barato |
| ¿Es pelo, cola, orejas, colgante, antena, pecho? | **Siempre huesos**, nunca cloth |
| ¿Personaje de fondo o multitud en móvil? | Huesos con LOD, o hornear, o nada (§8–§9) |

Números de orden de magnitud: una cadena de huesos son **5–20 huesos** integrados por un spring; una malla de cloth son **cientos de vértices** con constraints y self-collision. Por eso la regla es: *hueso salvo que necesites pliegues de verdad.*

**El híbrido moderno (respuesta móvil):** riguear la capa/falda con una **rejilla de huesos** (bone lattice) y moverlos con **BoneCloth** (Magica) — se obtiene movimiento tipo tela (varias cadenas que colisionan entre sí) a coste de huesos, sin la sim por vértice del Cloth component. Es el punto dulce para tela que se ve pero no exige pliegues fotorrealistas.

## 7. Baked vs runtime: el criterio

Se puede **hornear** una simulación a keyframes: correr el solver una vez (en el DCC o en Unity), grabar las transformaciones de los huesos a un clip, y a partir de ahí es animación normal sin solver en runtime.

| | Horneado a keyframes | Simulado en runtime |
|---|---|---|
| **Coste runtime** | Cero solver (solo curvas extra; ojo: curvas de **escala** son las más caras) [ver: unity/animacion-unity §1 costes] | CPU por cadena/vértice cada frame |
| **Reactivo** | **NO** — igual en cada reproducción; ignora la fuerza/velocidad real, viento y colisiones del momento | **SÍ** — reacciona al movimiento real, al viento, a los colliders |
| **Determinismo** | Determinista, idéntico siempre | Puede variar entre ejecuciones |
| **Peso en build** | Curvas ocupan memoria de clip [ver: unity/rendimiento-unity] | Solo el código del solver |
| **Ideal para** | Loop ambiental (pelo meciéndose en un idle, bandera en un clip fijo), cinemática, móvil, multitudes | Colgantes gameplay que DEBEN reaccionar al movimiento impredecible |

**El criterio en una frase:** ¿el secundario debe reaccionar a movimiento **impredecible** de gameplay (paradas bruscas, cambios de dirección, viento dinámico, chocar con el entorno)? → **runtime**. ¿Es un movimiento **predecible/en loop/de fondo**? → **hornear**. Un peinado horneado se ve genial en el idle pero NO reaccionará cuando el personaje frene en seco — ahí se nota lo congelado.

Regla mixta común: **hornear el idle/locomoción** (donde el secundario es predecible y repetitivo) y **simular en runtime solo las acciones reactivas** o los personajes hero en primer plano.

## 8. Presupuesto de físicas de accesorios en móvil

Jerarquía de coste, de barato a caro (calibrar con Profiler en dispositivo caliente, no en editor [ver: unity/rendimiento-unity §6]):

| Técnica | Coste relativo | Escala a multitudes |
|---|---|---|
| Overlap horneado a keyframes | Casi cero | Sí (es solo animación) |
| Damped Transform / spring bones (pocas cadenas cortas) | Bajo | Sí con LOD |
| Dynamic Bone / BoneCloth (varias cadenas + colliders) | Medio | Con cuidado (cap de cadenas, disable a distancia) |
| Cloth component (sim por vértice + self-collision) | **Alto** | **No** — reservar a 1–2 personajes hero |

Tácticas móvil (verificado a nivel de existencia de la feature; valores a calibrar):
- **LOD de físicas**: desactivar spring bones más allá de N metros / fuera de cámara. Dynamic Bone trae *distant disable*; Magica Cloth 2 tiene un **Disable Mode**; alinearlo con el culling del Animator [ver: unity/animacion-unity §1 culling].
- **Cap de longitud de cadena**: menos eslabones por elemento en gama baja; una cadena de 3 vs 8 es ~3× menos integraciones.
- **Menos colliders**: cada collider extra por cadena multiplica el chequeo. Solo los que evitan clipping visible (pecho, muslos, cabeza).
- **Hornear en fondo**: NPCs de fondo y multitudes → secundario horneado o ninguno; el jiggle solo en el personaje jugable y jefes.
- **Fill rate manda en móvil** [ver: unity/rendimiento-unity §6]: el jiggle es coste CPU/animación, no de pintado — pero un SkinnedMeshRenderer con más huesos también sube el coste de skinning; medir ambos.

El principio duro: **jiggle bones son baratos, cloth es caro.** En móvil, la elección por defecto es cadenas de huesos (horneadas donde se pueda), y el Cloth component es un lujo de 1–2 personajes destacados.

## 9. La vida gratis: dónde ponerla y dónde no

El secundario dinámico es "vida gratis" porque cuesta cero animación por clip — el solver la aplica sobre CUALQUIER animación. Pero no todo lo merece:

| Ponlo | No lo pongas |
|---|---|
| Pelo, coleta, flequillo | Ropa ceñida (sigue al cuerpo por skinning normal) |
| Cola, orejas de animal, antenas | Placas de armadura, hebillas (rígido: un hueso) [ver: rigging/rigs-mecanicos] |
| Capa, faldón, taparrabos, bufanda, tiras/correas sueltas | Elementos que la cámara casi no ve |
| Colgantes, pendientes, amuletos que cuelgan | NPCs de fondo/multitud en móvil (hornear o nada) |
| Pecho/panza en personajes cartoon (con mesura) | Nada que rompa la **silueta legible** de gameplay [ver: gamedev/animacion §3] |

**Rendimientos decrecientes:** 2–3 cadenas bien tuneadas (pelo + un accesorio) ya leen como "vivo"; 20 cadenas cuestan 10× y apenas se ven mejor. La vida más barata del catálogo es **una cadena de pelo + un colgante**. Añade la tercera solo si el personaje se ve en primer plano.

**El over-jiggle es un olor:** físicas de pecho/pelo sobre-tuneadas (todo temblando como gelatina) delatan al aficionado y distraen del gameplay. Si la punta oscila más que una vez o dos al parar, sube el damping. La readability del combate manda sobre el detalle: un arma o accesorio gigante que tiembla arruina la lectura de la pose [ver: gamedev/game-feel §silueta].

**Nota mocap:** el mocap captura el cuerpo, **no** el pelo ni la tela [ver: mocap-librerias]. El secundario dinámico es justo la capa que se añade DESPUÉS del mocap para que un clip capturado no se sienta "de maniquí". Igual que el secondary action se resuelve con additive layers en vez de reanimar cada clip [ver: unity/animacion-unity §3] [ver: capas-estados].

## 10. Viento, red y el flujo de horneado

**Viento (add barato de vida global):** una fuerza de viento sobre las cadenas ya simuladas hace ondear pelo/capa/faldón sin animación extra. Dynamic Bone lo toma como `Force`; Cloth como `External`/`Random Acceleration`; Magica trae viento propio (verificado 2026-07-20). Un viento suave con algo de ruido/turbulencia lee "escena viva" a coste casi nulo — pero cuida que no compita con la readability ni haga temblar props de gameplay.

**Red / multiplayer:** el movimiento secundario es **puramente cosmético** — nunca autoritativo, nunca en la sim de gameplay. No lo sincronices por red: cada cliente simula el suyo localmente sobre la pose replicada del personaje. Como es no determinista entre máquinas, dos jugadores verán el pelo distinto y da igual. Nunca dejes que una hitbox, un collider de gameplay o la lógica dependan de un hueso dinámico [ver: gamedev/game-feel].

**Flujo de horneado (sim → clip):**
1. Simular en el DCC (o en Unity en Play mode) sobre el clip base, con la cadena ya settleada (1–2 frames de warm-up).
2. **Grabar** las transformaciones de los huesos dinámicos a keyframes (rotación/posición; evitar escala) — en Unity, el Recorder o Bidirectional Motion Transfer de Animation Rigging; en DCC, el bake de la acción. El paso a paso en Blender es fase siguiente.
3. El clip resultante YA lleva el secundario horneado: quitar el solver del prefab. Ahora es animación pura, cero coste de runtime, apta para móvil/fondo — pero congelada (§8).
4. Verificar que el loop cierra (el último frame casa con el primero) o el pelo dará un salto al reiniciar el ciclo [ver: ciclos-locomocion].

## Reglas prácticas

1. Overlap/follow-through **a mano** solo en hero y cinemáticas donde el timing es dirección de arte; el resto, **simular** (más barato y reactivo).
2. Arrastre a mano = **offset de 2–4 frames por eslabón** desde la base hacia la punta, proporcional a masa/longitud (no 10 huesos en una oreja ni 3 en una capa larga); al parar, 2–3 rebotes decrecientes, nunca todo a la pose final en el mismo frame.
3. Jiggle/spring bones son **deform bones extra sin keyframes**: skinnea el elemento a ellos, cuélgalos del hueso de cuerpo más cercano, y déjalos en una bone collection `DYN`/`JIGGLE`.
4. Todo solver es un **spring-damper**: tunea rigidez (que no sea gelatina), sube damping hasta matar el over-jiggle (que no rebote como resorte de cartoon), e inercia sobre el padre (que el snap del cuerpo no lo dispare). La readability de la pose de gameplay manda sobre el detalle.
5. Elige el solver por escala: **Damped Transform** (built-in, sin asset de pago) para pocos colgantes sin colisión, **Dynamic Bone/Magica** para varias cadenas con colisión, **Cloth** solo para tela hero.
6. **Hueso salvo que necesites pliegues reales**: pelo/cola/faldón/bufanda → cadenas de huesos; capa hero/bandera que drapea → cloth sim.
7. Híbrido móvil: rejilla de huesos + BoneCloth para tela que se ve pero no exige pliegues fotorrealistas.
8. **Hornear** el secundario predecible (idle, locomoción en loop, fondo); **simular en runtime** solo lo que debe reaccionar a movimiento impredecible — un peinado/capa horneado NO reacciona a paradas bruscas, no lo uses en acciones reactivas de primer plano.
9. Los solvers corren en `LateUpdate` / pase de Animation Rigging (tras el Animator): no keyframees ni muevas en `Update` un hueso que controla un solver.
10. Piezas rígidas (armadura, hebillas) = un hueso weight 100%, jamás cloth ni jiggle.
11. Móvil: LOD de físicas (disable a distancia/offscreen), cap de longitud de cadena, mínimo de colliders, NPCs de fondo horneados o sin secundario; cada jiggle bone cuenta además contra el presupuesto de huesos y de skinning (4 influencias/vértice sigue siendo el objetivo) [ver: rigging/esqueletos-armature §10].
12. Reancla el solver al desplazarse (VRM `Center`, `Inert` de Dynamic Bone, `World Velocity Scale`) para que el personaje no "vibre" al moverse rápido.
13. Ante un teleport/respawn/corte de cámara, **resetea** la cadena (o desactiva el solver ese frame) — un padre que salta hace explotar el muelle.
14. 2–3 cadenas bien tuneadas > 20 cadenas mediocres: empieza por pelo + un colgante y añade solo si se ve en primer plano.
15. El secundario es la capa que se añade DESPUÉS del mocap (que no captura pelo ni tela) — no lo esperes del clip capturado.
16. El movimiento secundario es **cosmético**: no lo sincronices por red (cada cliente lo simula local) y nunca cuelgues gameplay, hitboxes ni colliders de un hueso dinámico.
17. Un viento suave con turbulencia sobre las cadenas es vida de escena casi gratis; que no compita con la readability.
18. Al hornear un ciclo, verificar que el último frame casa con el primero o el pelo salta al reiniciar el loop.
19. Da 1–2 frames de settle/pre-warm al solver antes de capturar o grabar — el primer frame desde la bind pose sale con la cadena estirada.
20. Tunea sobre la animación MÁS agresiva del set (giro brusco, aterrizaje), no sobre el idle — el idle esconde el over-swing.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Animar overlap a mano en cada clip de gameplay (horas por personaje) | Simular con spring bones: cero coste por clip, aplica a todo; a mano solo hero/cine |
| Todo el pelo/cola llega a la pose final en el mismo frame → se siente de robot | Offset de 2–4 frames por eslabón (drag); punta llega última |
| Usar el Cloth component para pelo, cola o un faldón simple | Cadenas de huesos (BoneCloth/Dynamic Bone); cloth solo si necesita pliegues reales |
| Cloth con self-collision en todo → "una parte significativa del tiempo de sim" (Manual) en un solo personaje | Self-collision solo donde hay clipping real; distancias pequeñas; menos partículas |
| Esperar que el Cloth choque con los colliders de la escena | Solo sphere/capsule/conic asignados a mano; es unidireccional (no devuelve fuerza) |
| Horneado de hair sway usado en una acción reactiva → no reacciona al frenazo | Runtime para lo reactivo; hornear solo idle/loop/fondo |
| Curvas de escala en el clip horneado → las más caras de todas | Hornear posición/rotación; evitar animar escala [ver: unity/animacion-unity §1] |
| Script moviendo en `Update` un hueso que también lleva Dynamic Bone/Magica | El solver (LateUpdate) lo pisa: elige uno; no mezcles keyframe y solver en el mismo hueso |
| El personaje corre y el pelo "vibra"/estalla por el snap del root | Subir inercia (`Inert`/`World Velocity Scale`) o reanclar (`Center` de VRM) |
| Teleport/respawn/corte → la cadena explota o tarda en asentar | Reset del solver ese frame, o desactivarlo durante el teleport |
| Físicas de pecho/pelo sobre-tuneadas temblando como gelatina | Subir stiffness y damping; el over-jiggle delata y distrae |
| 15 cadenas de spring bones en cada NPC de una multitud móvil | 2–3 cadenas en hero, LOD de físicas, fondo horneado o sin secundario |
| Jiggle bones con >4 influencias/vértice o marcados no-deform → no deforman en Unity | Deform ON, limitar a 4 influencias y normalizar antes de exportar [ver: rigging/esqueletos-armature §10] |
| Cloth/jiggle en un accesorio gigante que rompe la silueta de combate | La readability manda: recortar el secundario que tape la pose [ver: gamedev/game-feel] |
| Sincronizar huesos dinámicos por red o colgar una hitbox de ellos | Es cosmético y no determinista: simular local en cada cliente, gameplay jamás depende de él |
| Ciclo horneado que da un salto de pelo al reiniciar | El último frame del loop debe casar con el primero antes de hornear [ver: ciclos-locomocion] |
| Primer frame con la cadena estirada desde la bind pose | Dar 1–2 frames de settle/pre-warm antes de capturar o grabar |
| Tunear las físicas mirando solo el idle y verlas estallar en carrera | Calibrar sobre la animación más agresiva del set; el idle no revela el over-swing |
| Pagar Dynamic Bone/Magica para dos antenas que solo necesitan retardo | Damped Transform (Animation Rigging, sin coste de asset) cubre pocos colgantes sin colisión |

## Fuentes

- **Unity Manual 6 — Cloth** (`docs.unity3d.com/Manual/class-Cloth.html`) — VERIFICADO vía fetch (2026-07-20): solo sobre SkinnedMeshRenderer; parámetros `Stretching/Bending Stiffness`, `Damping`, `External/Random Acceleration`, `World Velocity/Acceleration Scale`, `Friction`, `Use Gravity`, `Use Tethers`; colliders solo sphere/capsule/conic asignados a mano y unidireccionales; self/inter-collision (`Inter-Collision Distance/Stiffness`) "can take a significant amount of the overall simulation time"; constraints pintables Select/Paint/Gradient.
- **Unity Animation Rigging 1.3 — Damped Transform** (`docs.unity3d.com/Packages/com.unity.animation.rigging@1.3/manual/constraints/DampedTransform.html`) — VERIFICADO vía fetch (2026-07-20): movimiento retardado/suavizado siguiendo un Source; `Weight`, `Constrained Object`, `Source`, `Damp Position` (0–1), `Damp Rotation` (0–1), `Maintain Aim`; casos antenas/colas/pelo. Corre sobre C# Animation Jobs [ver: unity/animacion-unity §8].
- **VRM SpringBone — vrm.dev** (`vrm.dev/en/univrm/springbone/`) — VERIFICADO vía fetch (2026-07-20): oscilación secundaria de pelo/falda/accesorios; `Stiffness Force`, `Gravity Power`, `Gravity Direction`, `Drag Force`, `Hit Radius`; `VRMSpringBoneColliderGroup` (spheres con offset/radius); GameObject **Center** para reanclar y evitar vibración al desplazarse.
- **Dynamic Bone — Unity Asset Store** (`assetstore.unity.com/packages/tools/animation/dynamic-bone-16743`, Will Hong) — VERIFICADO vía fetch (2026-07-20): físicas sobre huesos de personaje (pelo, tela, accesorios, cola); **$20** Extension Asset, **v1.3.4 (6-may-2024)**, min Unity 2019.4.1f1, Built-in/URP/HDRP, soporta `DynamicBoneCollider`. La lista exacta de campos (`Damping/Elasticity/Stiffness/Inert/Radius/Gravity/Force/...`) NO la devolvió el fetch — son los campos públicos documentados del componente, referenciar como tal.
- **Magica Cloth 2 — magicasoft.jp** (`magicasoft.jp/en/magica-cloth-2-2/`) — VERIFICADO vía fetch (2026-07-20): sucesor de Magica Cloth; modos **BoneCloth** (cadenas de huesos/spring) y **MeshCloth** (tela por malla); colliders Sphere/Capsule/Plane; viento, self-collision, construcción/escala en runtime, params `Update Mode`/`Disable Mode`/`Animation Pose Ratio`. Implementación multihilo (DOTS/Burst/Jobs) NO confirmada por el fetch — verificar antes de citarla como argumento de rendimiento; precio no devuelto.
- **Twelve basic principles of animation — Wikipedia** (`en.wikipedia.org/wiki/Twelve_basic_principles_of_animation`, sobre Thomas & Johnston, *The Illusion of Life: Disney Animation*, 1981) — VERIFICADO vía fetch (2026-07-20): follow-through (partes flojas siguen tras la parada, amortiguación de oscilación hacia el centro de masa), overlapping action (partes en timings distintos), drag (partes tardan frames en arrancar), secondary action (apoya sin distraer de la principal). "Successive breaking of joints" atribuido a Richard Williams (*The Animator's Survival Kit*), a nivel concepto.
- **Bases sintetizadas del propio repo:** [ver: gamedev/animacion §1,§3,§5,§7] (12 principios a nivel game-feel, follow-through/overlap como "vida gratis", springs de lean/recoil, additive layers para secondary action), [ver: gamedev/game-feel §5] (squash&stretch, tweening elástico, silueta), [ver: rigging/esqueletos-armature §6,§7,§10] (deform vs control bones, bone collections, 4 influencias/vértice, export deform-only), [ver: unity/animacion-unity §1,§3,§4,§8] (coste de curvas de escala y culling, avatar mask/additive layers, tween-vs-clip, Damped Transform/Animation Rigging), [ver: unity/rendimiento-unity §6] (presupuesto móvil, fill rate, profilear en caliente). Cross-refs internos animacion3d: [ver: keyframes-curvas], [ver: animacion-combate], [ver: ciclos-locomocion], [ver: mocap-librerias], [ver: capas-estados], [ver: principios-produccion].
