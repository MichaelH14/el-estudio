# Animación facial y lip-sync

> **Cuando cargar este archivo:** al dar vida a la cara de un personaje — expresiones, diálogo con lip-sync, mirada y parpadeo, cejas y micro-expresión — y decidir CÓMO construirla (blendshapes vs huesos faciales vs híbrido), CUÁNTO invertir según el juego, y cómo llega y se controla en Unity 6. Asume el rig de cuerpo montado [ver: rigging/rig-a-unity] y la deformación resuelta [ver: rigging/deformacion]; aquí se cierra el hueco de la CARA, que rigging deja explícitamente fuera. Los 12 principios (anticipation, ease, exageración) están en [ver: gamedev/animacion] y no se repiten: esto es la capa de producción 3D específica de la cara.

Regla que gobierna todo el archivo: **la cara es el lugar donde el jugador mira primero.** Un cuerpo animado a la perfección con ojos muertos se lee como un cadáver; unos ojos vivos sobre un cuerpo mediocre se perdonan. Por eso el criterio de inversión (§2) va antes que la técnica: casi ningún juego necesita las 52 shapes de ARKit, pero casi todos ganan con ojos + parpadeo.

---

## 1. Los tres enfoques: blendshapes vs huesos faciales vs híbrido

La cara deforma distinto que el cuerpo. El linear blend skinning de huesos [ver: rigging/deformacion §7] resuelve bien la mandíbula (bisagra) y la rotación de los ojos (pivote), pero **no** puede esculpir la forma sutil de una sonrisa o un frunce. Ahí entran los blendshapes (morph targets): deltas de posición por-vértice esculpidos a mano.

| Enfoque | Qué mueve la cara | Fuerte en | Débil en | Coste |
|---|---|---|---|---|
| **Blendshapes / morph targets** | Deltas por-vértice desde el neutral (§3); pesos 0→1 combinados | Forma sutil y arbitraria: sonrisa, frunce, visemes, cejas | Rotación grande (ojos, mandíbula amplia) se deforma feo; no encadena físicas/IK | Memoria (deltas por shape) + 1 curva por shape/clip |
| **Huesos faciales** | Huesos reales que rotan/trasladan: `jaw`, `eye.L`, `eye.R`, a veces cejas/labios | Mandíbula (bisagra), ojos (pivote), cualquier cosa que rote o siga un target en runtime (look-at, físicas de mejilla) | Formas sutiles necesitan MUCHOS huesos y pesos finísimos; caro de animar a mano | Cuenta de huesos + pesos ≤4 influencias [ver: rigging/rig-a-unity §1] |
| **Híbrido (el estándar de producción)** | **Huesos** para jaw + ojos; **blendshapes** para expresión, visemes, párpados, cejas | Lo mejor de ambos; es como trabaja ARKit/MetaHuman | Más piezas que mantener | Medio |

**El default honesto: híbrido.** Mandíbula y ojos = 3 huesos (`jaw`, `eye.L`, `eye.R`); todo lo demás = blendshapes. Los ojos SIEMPRE son huesos (rotan un globo rígido, no lo deforman) y necesitan ser Transforms accesibles en runtime para el look-at (§6) — si usas Optimize Game Objects, expón los huesos de ojo/cabeza en **Extra Transforms to Expose** [ver: rigging/rig-a-unity §7].

Constraint técnico de blendshapes que condiciona todo lo demás: **un blendshape es un array de deltas de posición con el MISMO conteo y orden de vértices que la malla base.** No puedes añadir/quitar geometría entre neutral y shape. Toda la topología facial (loops concéntricos alrededor de ojos y boca) se decide ANTES [ver: modelado/topologia] [ver: modelado/organico-personajes] — un loop mal puesto en la boca arruina cada viseme por igual.

---

## 2. Cuánto invertir según el juego (el criterio para un dev solo)

La cara es un pozo sin fondo de trabajo. Este es el gate honesto — subir un peldaño solo si el juego lo cobra en pantalla:

| Nivel | Juego típico | Qué construyes | Coste real |
|---|---|---|---|
| **0 — Sin cara** | Móvil/casual, top-down, cámara lejana, sin diálogo, estilizado duro | Nada. O cara pintada en textura fija | 0 |
| **1 — Cara barata** | Móvil estilizado, cartoon, NPCs de fondo | Textura de cara intercambiable (§9) o 2-4 blendshapes de emoción exagerada + parpadeo | Horas |
| **2 — El 80/20** | Third-person action, aventura, cámara media, poco diálogo | **Huesos de ojo + look-at + parpadeo + jaw abre/cierra + 1 sonrisa + 1 frunce**. Da el 80% de la "vida" percibida | Días |
| **3 — Diálogo real** | RPG/narrativo con conversaciones, cámara cercana en cutscenes | Nivel 2 + set de visemes (§5) + set de emociones FACS (§4) + cejas (§7) + saccades | Semanas de arte |
| **4 — Close-up cinematográfico** | Protagonista de AAA narrativo, primeros planos | Set ARKit 52 completo + audio-driven o mocap facial + correctivos de combinación (§3) | Pipeline dedicado |

**La regla del dev solo:** casi nunca pasas del nivel 2 salvo que el juego SEA diálogo. El error caro es construir nivel 4 para un juego que la cámara nunca acerca. Antes de esculpir 52 shapes, pregunta: *¿la cámara ve la cara a menos de 3 metros? ¿hay diálogo con la boca en pantalla?* Si ambas son no → nivel 1-2. El siguiente error caro es el inverso: un juego de diálogo con la boca abriendo/cerrando sin visemes se lee como marioneta rota — ahí el nivel 3 no es opcional.

---

## 3. Blendshapes de expresión: esculpir, combinar, el sistema de sliders

### Crear las shapes (en el DCC, antes de Unity)
1. **Neutral primero.** Es la base de todos los deltas. La cara en reposo, boca cerrada relajada, ojos abiertos naturales. Todo shape es la diferencia contra esta.
2. **Esculpir cada shape sobre el neutral** moviendo vértices, sin tocar el conteo/orden. En Blender = *shape keys*; en Maya = *blend shape targets*. Cada uno un solo "gesto" atómico (no "cara feliz" entera sino `mouthSmileLeft`, `cheekSquintLeft`, `browInnerUp`… que SUMADOS dan la cara feliz).
3. **Partir en izquierda/derecha** todo lo que puede ser asimétrico (`mouthSmileLeft`/`mouthSmileRight`, cejas, ojos). La asimetría es lo que separa "vivo" de "máscara" (§7). ARKit parte casi todo en L/R por esto.
4. **Rango 0→1 = neutral→shape completo.** El slider interpola linealmente. Nunca esculpas un shape que ya sea una combinación de otros dos — pierdes la capacidad de mezclarlos.

### Combinar: la suma y su problema
Los shapes se suman ponderados: `mouthSmileLeft·0.8 + browInnerUp·0.4 + …`. Pero la suma lineal de dos deltas puede dar geometría rota cuando ambos tocan los mismos vértices (clásico: `mouthSmile` + `jawOpen` → labios que se cruzan o se despegan). Solución = **corrective/combination shape** (in-between o combo): un shape extra que se activa SOLO cuando dos disparadores están altos a la vez, y corrige la geometría. Es el mismo mecanismo que los correctivos de codo/hombro del cuerpo [ver: rigging/deformacion §4], disparado por producto de pesos en vez de por ángulo de hueso. Presupuéstalos: solo héroes con close-up los pagan.

### El sistema de sliders
- **In-engine / DCC:** cada shape es un slider 0-1 (0-100 en Unity). El "rig facial" para un animador es este panel de sliders (a veces con controles on-screen mapeados a los sliders).
- **Exclusividad:** shapes opuestos (`mouthSmile` vs `mouthFrown`) no se activan juntos; el sistema que los conduce elige uno. Con L/R separados puedes sonreír de un lado y fruncir del otro (sonrisa torcida, desprecio).
- **Presupuesto de memoria:** cada shape guarda deltas de los vértices que mueve. Una cara de 52 shapes multiplica el coste de vértice de la malla facial — por eso la cara suele ser una malla/isla propia y densa, y el cuerpo no lleva shapes.

---

## 4. FACS: el vocabulario de las expresiones

**FACS (Facial Action Coding System)** — Ekman & Friesen, 1978 (base de Carl-Herman Hjortsjö) — taxonomiza el movimiento facial en **Action Units (AU)**, cada una la contracción de uno o más músculos, independiente de la emoción. Es el marco que usa la industria para decidir QUÉ shapes esculpir: en vez de inventar shapes, esculpes las AU y las combinas. En CG, "las expresiones se expresan como vectores de AU, y esos valores se usan como pesos de blendshapes" (definición canónica de la aplicación de FACS a animación).

AUs de alto valor (el kit mínimo que cubre casi todo):

| AU | Nombre | Músculo | Análogo ARKit |
|---|---|---|---|
| **AU1** | Inner brow raiser | frontalis (medial) | `browInnerUp` |
| **AU2** | Outer brow raiser | frontalis (lateral) | `browOuterUp_L/R` |
| **AU4** | Brow lowerer | corrugator | `browDown_L/R` |
| **AU6** | Cheek raiser | orbicularis oculi | `cheekSquint_L/R` |
| **AU12** | Lip corner puller (sonrisa) | zygomaticus major | `mouthSmile_L/R` |
| **AU15** | Lip corner depressor | depressor anguli oris | `mouthFrown_L/R` |
| **AU26** | Jaw drop | masetero (relaja) | `jawOpen` |

Las emociones universales de Ekman se construyen COMBINANDO AUs (útil para armar tus shapes de emoción del nivel 3):

| Emoción | AUs (según FACS/EMFACS, canónico) |
|---|---|
| Alegría | AU6 + AU12 (la "Duchenne" real necesita el AU6 de los ojos; sin él, sonrisa falsa) |
| Tristeza | AU1 + AU4 + AU15 |
| Sorpresa | AU1 + AU2 + AU5 (párpado sube) + AU26 |
| Miedo | AU1 + AU2 + AU4 + AU5 + AU20 + AU26 |
| Ira | AU4 + AU5 + AU7 + AU23 |
| Asco | AU9 (nariz) + AU15 + AU16 |

Lección de producción: la **sonrisa Duchenne** (AU6 en los ojos, no solo AU12 en la boca) es por qué una sonrisa hecha solo con la boca se ve siniestra. Si esculpes una sola emoción bien, que sea la alegría con ojos.

---

## 5. Visemes y lip-sync

Un **viseme** es el análogo visual de un fonema: la forma de la boca para un sonido. No hay 1:1 fonema↔viseme — muchos fonemas comparten forma (p/b/m se ven iguales: labios cerrados). Por eso un set de visemes es MUCHO más chico que el inventario de fonemas.

### Los sets de visemes que importan

| Set | Nº | Para qué | Fuente |
|---|---|---|---|
| **Preston Blair / Hanna-Barbera** | **6 básicos (A–F) + 3 extra (G, H, X)** | Animación 2D/cartoon a mano; el canon histórico. A=labios cerrados (M,B,P), B=dientes (S,K,D), C=abierto (E), D=muy abierto (A), E=redondo (O), F=fruncido (U,W), G=dientes sobre labio (F,V), H=lengua arriba (L), X=reposo | Rhubarb Lip Sync (usa estas shapes) |
| **Oculus/Meta OVRLipSync** | **15** | Lip-sync en tiempo real desde audio (VR/juego): `sil, PP, FF, TH, DD, kk, CH, SS, nn, RR, aa, E, ih, oh, ou` | Meta OVRLipSync viseme reference |
| **ARKit (mouth subset)** | ~parte de las 52 | Captura facial y estándar de intercambio; se combinan varias mouth-shapes para formar cada viseme | Apple ARKit |

Para un juego con diálogo, **8-12 visemes bien elegidos bastan** (los 15 de Oculus son un techo cómodo). Menos de eso (jaw abre/cierra solo) = nivel 2, se lee como marioneta pero pasa en cámara media.

### ARKit 52: el estándar de facto para toda la cara
Las **52 blendShapeLocation de ARKit** (`ARFaceAnchor.BlendShapeLocation`, Apple) son el vocabulario que adoptó de facto la industria — Live Link Face, MetaHuman, Ready Player Me, casi todo pipeline de captura facial exporta y consume ARKit. Coeficientes **0.0–1.0** (en Unity: 0–100, multiplica ×100). Reparto por zona (52 total):

| Zona | Nº | Ejemplos |
|---|---|---|
| **Brow** (cejas) | 5 | `browInnerUp`, `browDown_L/R`, `browOuterUp_L/R` |
| **Eye** (ojos/párpados) | 14 | `eyeBlink_L/R`, `eyeWide_L/R`, `eyeSquint_L/R`, `eyeLookUp/Down/In/Out_L/R` |
| **Jaw** (mandíbula) | 4 | `jawOpen`, `jawForward`, `jawLeft`, `jawRight` |
| **Mouth** (boca) | 23 | `mouthClose`, `mouthFunnel`, `mouthPucker`, `mouthSmile_L/R`, `mouthFrown_L/R`, `mouthUpperUp_L/R`, `mouthLowerDown_L/R`, `mouthRoll/Shrug/Press/Stretch/Dimple…` |
| **Cheek** (mejillas) | 3 | `cheekPuff`, `cheekSquint_L/R` |
| **Nose** (nariz) | 2 | `noseSneer_L/R` |
| **Tongue** (lengua) | 1 | `tongueOut` |

Nota de honestidad: la página de Apple es JS y no se pudo scrapear entera esta sesión; el conteo **52** y el reparto por zona son el estándar documentado y verificado por conteo (5+14+4+23+3+2+1=52). Si vas a mapear nombre-por-nombre, valida contra la lista viva de Apple. Ventaja de adoptar ARKit aunque no captures con iPhone: cualquier animación/captura facial de terceros cae sobre tu personaje sin re-mapear.

### Mapear audio → visemes (auto-lip-sync)

| Método | Cómo | Cuándo | Herramienta (2026) |
|---|---|---|---|
| **Por amplitud (jaw follow)** | El jaw/`jawOpen` sigue el volumen (RMS) del audio; sin fonemas | NPCs de fondo, estilizado, presupuesto cero. "Barato pero convincente a distancia" | SALSA LipSync (Unity, asset de pago — detalles NO verificados esta sesión) |
| **Por fonemas en tiempo real** | Analiza el audio en runtime → pesos de los 15 visemes interpolados | Diálogo procedural, voz del jugador, VR | Oculus/Meta OVRLipSync (los 15 visemes, interpolados "para simular movimiento natural") |
| **Offline / precomputado** | Reconoce el habla del clip y saca timing de mouth-shapes (TSV/XML/JSON) que horneas en una animación | Diálogo autorado fijo, muchos idiomas | Rhubarb Lip Sync (CLI, A–X shapes) |
| **Audio-driven por IA** | Red neuronal audio→animación facial completa (no solo boca), salida a menudo ARKit-compatible | Cine/AAA, calidad alta sin mocap | NVIDIA Audio2Face (referencia; especificaciones NO verificadas esta sesión) |

Regla: **el lip-sync NO es solo la boca.** Un viseme sin la mandíbula, sin el leve movimiento de cejas y sin parpadeos se ve muerto. La boca es el 40%; el resto es jaw + cara idle viva (§6-7). Y **coarticulación**: la boca anticipa el sonido siguiente y arrastra el anterior — por eso interpolar entre visemes (no hacer snap) es obligatorio, exactamente el problema que resuelve la interpolación de OVRLipSync.

---

## 6. Ojos y mirada: donde vive el personaje

Los ojos son **huesos** (`eye.L`, `eye.R`) que rotan un globo rígido — nunca blendshapes. Lo que les da vida:

| Elemento | Cómo se hace | Nota |
|---|---|---|
| **Look-at** | Los huesos de ojo apuntan a un target. En Unity: **Multi-Aim Constraint** (Animation Rigging) sobre cada eye bone, o `SetLookAtPosition`/`SetLookAtWeight` en `OnAnimatorIK` para Humanoid [ver: unity/animacion-unity §8] | Interpolar el weight, nunca 0→1 seco. Limitar el rango (Min/Max) para que el ojo no rote a lo imposible |
| **Convergencia** | Ambos ojos apuntan al MISMO punto → bizquean levemente en objetos cercanos | Sin convergencia, mirada de muñeco de escaparate |
| **Párpados siguen la mirada** | Al mirar abajo, el párpado superior baja un poco (blendshape `eyeLook*` o hueso) | Ojo que mira abajo con párpado fijo = mirada de zombi |
| **Parpadeo** | Blendshape `eyeBlink_L/R` procedural: cada ~2-8 s, duración ~100-150 ms, cierre más rápido que la apertura | Dispara un parpadeo en cada cambio grande de mirada (es fisiológico) |
| **Saccades (micro-darts)** | El ojo NUNCA está perfectamente quieto: micro-saltos de 1-2° cada fracción de segundo | Un target de look-at con jitter minúsculo. Es LA diferencia entre vivo y muñeco |

**Por qué importa tanto (a nivel principio, tradición de animación de personajes — Williams, Preston Blair):** el público lee intención en la mirada antes que en cualquier otra parte. Un personaje que mira al jugador, luego al objeto del que habla, y parpadea al cambiar, se percibe consciente. La "idle face" viva durante una pausa de diálogo (mirada que deriva + saccades + parpadeo + micro-respiración de cejas) es lo que evita el "mannequin muerto" entre líneas. Si solo puedes invertir en UNA cosa facial, invierte en los ojos (§2, nivel 2).

---

## 7. Cejas y micro-expresión

Las cejas cargan una porción enorme de la emoción con muy pocos shapes: `browInnerUp` (AU1, preocupación/sorpresa), `browDown_L/R` (AU4, enfado/concentración), `browOuterUp_L/R` (AU2, sorpresa/escepticismo). Con solo estas 5 + boca ya tienes un rango expresivo amplio.

Principios de micro-expresión (lo que separa "vivo" de "preset"):
- **Asimetría.** Una ceja sube más que la otra; una comisura tira más. La simetría perfecta es el sello de lo falso — por eso todo se parte en L/R (§3).
- **Micro-movimiento constante.** Aun "neutral", la cara nunca está congelada: respiración, tragar, micro-ajustes de cejas y boca. En idle de diálogo, una capa aditiva sutil [ver: unity/animacion-unity §3] mantiene la cara respirando.
- **Anticipación y arrastre** [ver: gamedev/animacion]: la ceja sube ANTES de la palabra sorprendida; la sonrisa se deshace más lento de lo que se formó.
- **Menos es más.** La micro-expresión es de baja amplitud. Subir todos los shapes al 100% da una careta de emoji. La emoción real vive entre 0.1 y 0.5.

---

## 8. Import y control de blendshapes en Unity 6

### Import (Model tab del importer) — settings verificados
Al importar el FBX con shape keys/morph targets [ver: rigging/rig-a-unity §2]:

| Setting (Model tab) | Qué hace | Valor recomendado |
|---|---|---|
| **Import BlendShapes** | Activa importar los shapes | **ON** (obvio; sin esto no llegan) |
| **Import Deform Percent** | Preserva los valores de deform percent de los shapes; OFF los pone todos a 0 | ON si tu DCC autoró valores |
| **Blend Shape Normals** | Cómo se calculan las normales del shape: **Import** (del archivo) / **Calculate** (recalcula) / **None** (el shape no afecta normales) | **Calculate** o **Import** — NUNCA None si hay luz sobre la cara |
| **Legacy Blend Shape Normals** | Método viejo, usa Smoothing Angle | OFF salvo compat con pipeline antiguo |

**Gotcha crítico de iluminación:** si Blend Shape Normals = None, las normales NO se deforman con el shape → al sonreír/abrir la boca la cara se ve plana o con sombras rotas bajo la luz, aunque la geometría esté bien. Ponlo en **Calculate** (o Import si tu DCC las exporta) y que **coincida con el setting de Normals de la malla base**. Es el bug facial #1 que "no se ve en el viewport sin luz".

**Tangents: NO hay setting por-blendshape — es de la malla base.** El importer tiene un dropdown **Tangents** propio (Import / Calculate Legacy / Calculate Legacy - Split Tangent / Calculate Mikktspace / None), pero solo aplica a la malla base y solo aparece si Normals = Import o Calculate; no existe un "Blend Shape Tangents" separado. Los blendshapes heredan los tangentes de la malla base — por eso el specular/normal-map de la cara no se recalcula al gesticular, solo el shading por normales (arriba). Si la piel se ve mal bajo normal map al hacer una mueca fuerte, es una limitación conocida, no un bug de tu import.

### Control por código
- **El driver NO exporta.** Igual que los correctivos del cuerpo [ver: rigging/deformacion §4], cualquier driver/lógica que movía tus shapes en el DCC **se queda en el DCC**: en Unity los blendshapes llegan inertes (weight 0). Los conduces tú, por script o por clip.
- **API:** `SkinnedMeshRenderer.SetBlendShapeWeight(index, weight)` / `GetBlendShapeWeight(index)`. El **rango es el definido en el modelo** (típicamente **0–100** al venir de Blender/Maya — por eso los 0–1 de ARKit se multiplican ×100). Enumerar por nombre (los índices no son estables entre re-exports):

```csharp
SkinnedMeshRenderer face; // el SMR de la cara
Mesh m = face.sharedMesh;
// index estable-por-nombre: cachea en Awake, NO uses índices crudos
int iJawOpen   = m.GetBlendShapeIndex("jawOpen");     // Mesh.GetBlendShapeIndex
int count      = m.blendShapeCount;                    // enumerar todos:
for (int i = 0; i < count; i++) Debug.Log(m.GetBlendShapeName(i));
// conducir un viseme/emoción (0..100):
face.SetBlendShapeWeight(iJawOpen, arkitCoef01 * 100f);
```

### Conducir muchos shapes a la vez
- **Direct Blend Tree** (Animator): un blend tree tipo *Direct* mapea un parámetro Float por shape → cada uno pondera un clip que pone ese shape [ver: unity/animacion-unity §2]. Bueno para sets de emoción/viseme autorados.
- **Script directo** para audio-driven/procedural (lip-sync runtime, look-at, saccades): setea los weights cada frame. Es lo que hacen OVRLipSync/SALSA por debajo.
- **Timeline** para cutscenes con diálogo autorado en el tiempo [ver: unity/animacion-unity §6]; **Animation Events** para disparar un gesto en un frame exacto [ver: unity/animacion-unity §9].
- **Presupuesto:** la cara es un `SkinnedMeshRenderer` propio; recuerda que el skinning no se abarata con batching [ver: rigging/deformacion §7] y que las curvas de blendshape cuestan por clip — por eso los NPCs de fondo van a nivel 1-2, no a 52 shapes.

---

## 9. Estilizado: el truco barato que se ve bien

Para cartoon/móvil/estilizado, la cara realista es contraproducente (uncanny) y cara. Opciones baratas que se ven MEJOR en ese estilo:

| Truco | Cómo | Ejemplo de estilo |
|---|---|---|
| **Pocas shapes exageradas** | 3-6 blendshapes al extremo: `happy`, `angry`, `sad`, `surprised`, `blink`. Amplitud alta, formas caricaturescas | Overwatch-ish, indie cartoon |
| **Texturas de cara intercambiables** | Ojos y boca son una zona de UV cuyo texture/atlas se cambia por expresión (o por frame de flipbook). Cero deformación de malla | Anime/toon, muchos móviles, Zelda-BOTW-style |
| **Flipbook de ojos/boca por UV offset** | Un atlas de expresiones; un script mueve el UV o cambia el material según estado/audio | Estilizado 3D barato |
| **Jaw-only lip-sync por amplitud** | Un solo hueso `jaw` abre/cierra siguiendo el volumen del audio; sin visemes | NPCs, móvil, fondo |

La textura intercambiable es EL truco barato: dibujas las expresiones (rápido y expresivo, como 2D [ver: unity/animacion-unity §7]) en vez de esculpirlas, y evitas por completo el coste de blendshapes y el uncanny valley. En estilo toon suele verse mejor que un rig facial completo. Compaginable con huesos de ojo para look-at si quieres mirada dirigida sobre ojos dibujados (mover el UV del ojo en vez de rotar un globo).

---

## Reglas prácticas

1. Decide el NIVEL (§2) antes de tocar un shape. ¿La cámara ve la cara de cerca? ¿hay diálogo con la boca en pantalla? Si ambas no → nivel 1-2, jamás 52 shapes.
2. Si solo inviertes en una cosa facial, que sean los **ojos**: hueso + look-at + parpadeo + saccades. Dan más "vida" por hora que cualquier otra cosa.
3. Híbrido por defecto: **huesos** para `jaw`/`eye.L`/`eye.R`, **blendshapes** para expresión/visemes/párpados/cejas.
4. Ojos son huesos, nunca blendshapes; expón `eye`/`head` en Extra Transforms to Expose si usas Optimize Game Objects [ver: rigging/rig-a-unity §7].
5. Esculpe shapes ATÓMICos desde el neutral (AU FACS), no emociones enteras; parte todo en L/R para permitir asimetría.
6. Adopta el naming/estructura **ARKit 52** aunque no captures con iPhone: cualquier captura o animación de terceros cae sobre tu personaje sin re-mapear.
7. 8-12 visemes bastan para diálogo (15 de Oculus como techo). Siempre **interpola** entre visemes (coarticulación); nunca hagas snap.
8. Lip-sync ≠ solo boca: sin jaw + cejas + parpadeo se ve muerto. La boca es ~40% de la lectura.
9. Sonrisa con AU6 (ojos), no solo AU12 (boca): sin los ojos, la sonrisa es siniestra.
10. Micro-expresión de baja amplitud (0.1-0.5): subir shapes al 100% da careta de emoji.
11. Blend Shape Normals = **Calculate** (o Import), coincidiendo con las Normals de la base; jamás None si hay luz sobre la cara.
12. El driver del shape NO exporta: en Unity llegan inertes; condúcelos por `SetBlendShapeWeight` (script/Direct blend tree/clip).
13. `GetBlendShapeIndex(name)` cacheado en Awake; nunca índices crudos (cambian entre re-exports). Weight 0-100 (ARKit 0-1 → ×100).
14. Correctivos de combinación solo donde dos shapes chocan (smile+jawOpen) y solo en héroes de close-up [ver: rigging/deformacion §4].
15. Cara = `SkinnedMeshRenderer` propio y denso; el resto del cuerpo sin shapes. NPCs de fondo a nivel 1-2, no 52.
16. Estilizado: dibuja expresiones (texturas intercambiables) en vez de esculpirlas — más barato, evita el uncanny, se ve mejor en toon.
17. Amplitude lip-sync (jaw sigue el volumen) para NPCs de fondo; fonemas (OVRLipSync) para diálogo cercano; offline (Rhubarb) para diálogo autorado.
18. Parpadeo en cada cambio grande de mirada (es fisiológico); saccades siempre (el ojo nunca está quieto).

## Errores comunes

| Pitfall | Síntoma | Antídoto |
|---|---|---|
| Esculpir 52 shapes para un juego que nunca acerca la cámara | Semanas gastadas, invisible en pantalla | Decidir nivel (§2) primero; nivel 2 (ojos+jaw+2 emociones) para la mayoría |
| Ojos muertos / fijos | El personaje se ve como cadáver o maniquí pese a buen cuerpo | Look-at + convergencia + parpadeo + saccades (§6) |
| Blend Shape Normals = None | La cara se ve plana/con sombras rotas al gesticular, solo bajo luz | Calculate o Import, coincidiendo con Normals de la base |
| Blendshape inerte en Unity (weight siempre 0) | El shape existe pero no se mueve | El driver no exportó: conducir por `SetBlendShapeWeight`/clip/Direct blend tree |
| Lip-sync solo mueve la boca | Habla como marioneta, se ve muerto | Añadir jaw + micro-cejas + parpadeos; interpolar visemes |
| Visemes con snap (sin interpolar) | Boca "tartamudea", salta entre formas | Interpolar entre visemes (coarticulación) — es lo que hace OVRLipSync |
| Sonrisa solo con la boca (sin AU6) | Sonrisa siniestra / uncanny | Sumar `cheekSquint`/AU6 (sonrisa Duchenne) |
| Todo simétrico | Cara de máscara, sin vida | Partir shapes en L/R; asimetría deliberada (§7) |
| Shapes al 100% para "más emoción" | Careta de emoji, expresión plástica | Baja amplitud (0.1-0.5); la micro-expresión es sutil |
| Ojos como blendshapes | Rotación fea, no se puede hacer look-at en runtime | Ojos = huesos que rotan; blendshapes solo para párpados |
| Añadir/quitar vértices entre neutral y shape | El blendshape no importa o revienta | Mismo conteo/orden de vértices en TODOS los shapes; topología decidida antes |
| Cara sin malla propia (shapes sobre el cuerpo entero) | Coste de vértice y de curvas disparado | Cara = SkinnedMeshRenderer denso aparte; cuerpo sin shapes |
| Índices de blendshape cacheados crudos | Tras re-export, la boca conduce el shape equivocado | `GetBlendShapeIndex(name)`, cachear por nombre en Awake |
| smile + jawOpen sin corrective | Labios cruzados/despegados al hablar sonriendo | Combination/corrective shape disparado por producto de pesos |
| Optimize Game Objects sin exponer el ojo/cabeza | El look-at no encuentra el hueso | Extra Transforms to Expose para `eye`/`head` [ver: rigging/rig-a-unity §7] |

## Fuentes

- **Apple Developer — `ARFaceAnchor.BlendShapeLocation`** (developer.apple.com/documentation/arkit/arfaceanchor/blendshapelocation) — Apple — las **52 blendshapes** faciales, coeficientes 0.0–1.0, estándar de facto (Live Link Face, MetaHuman). Página JS no scrapeable entera esta sesión: conteo 52 y reparto por zona (brow 5 / eye 14 / jaw 4 / mouth 23 / cheek 3 / nose 2 / tongue 1 = 52) verificados por conteo; validar nombre-por-nombre contra la lista viva de Apple. Consultado 2026-07-20.
- **Meta/Oculus — OVRLipSync Viseme Reference** (developers.meta.com/horizon/documentation/unity/audio-ovrlipsync-viseme-reference) — Meta — **15 visemes** (`sil, PP, FF, TH, DD, kk, CH, SS, nn, RR, aa, E, ih, oh, ou`), "visemes = análogo visual de fonemas", interpolación para movimiento natural. Consultado 2026-07-20.
- **Rhubarb Lip Sync** (github.com/DanielSWolf/rhubarb-lip-sync) — Daniel Wolf — auto lip-sync offline desde audio; **6 mouth shapes básicos A–F (Hanna-Barbera/Preston Blair) + G, H, X extra**; salida TSV/XML/JSON; integra con After Effects, Moho, Spine. Consultado 2026-07-20.
- **Facial Action Coding System (FACS)** (en.wikipedia.org/wiki/Facial_Action_Coding_System) — Ekman & Friesen 1978 (base Hjortsjö) — Action Units (AU1/2/4/6/12/15/26 y músculos), uso en CG: AUs como vectores → pesos de blendshapes. Consultado 2026-07-20.
- **Unity Manual 6000.2 — Model tab (FBX importer)** (`FBXImporter-Model.html`) — Unity Technologies — Import BlendShapes, Import Deform Percent, Blend Shape Normals (Import/Calculate/None), Legacy Blend Shape Normals; las normales del shape deben coincidir con las de la base. Consultado 2026-07-20.
- **Unity Scripting API 6000.2 — `SkinnedMeshRenderer.SetBlendShapeWeight` / `GetBlendShapeWeight`** — Unity Technologies — set/get de peso; rango = min/max definidos en el modelo (típ. 0-100). Consultado 2026-07-20.
- **Unity Scripting API 6000.2 — `Mesh.GetBlendShapeName` / `GetBlendShapeIndex` / `blendShapeCount`** — Unity Technologies — enumerar shapes por nombre, índice estable por nombre. Consultado 2026-07-20.
- **Unity Animation Rigging 1.3 — Multi-Aim Constraint** (`constraints/MultiAimConstraint.html`) — Unity Technologies — look-at por hueso: Source Objects, Aim/Up Axis, World Up, Offset, Min/Max Limits, Maintain Rotation Offset; uso para ojos/cabeza. Consultado 2026-07-20.
- **NVIDIA Audio2Face** — NVIDIA (ACE/Omniverse) — audio-driven facial animation con salida ARKit-compatible. Página no accesible esta sesión (404 en el path probado): citado a nivel de existencia/categoría, **especificaciones NO verificadas**.
- **SALSA LipSync** (Crazy Minnow Studio, Unity Asset Store) — lip-sync por aproximación de amplitud (sin fonemas) + EmoteR para ojos/parpadeos. Página no accesible esta sesión (404): citado a nivel de categoría, **detalles NO verificados**.
- **Mixamo** (Adobe) — auto-rigger de CUERPO + librería de animaciones humanoides; **no** hace rig/captura facial (Face Plus discontinuado). Detalle del pipeline body→Unity en [ver: rigging/rig-a-unity §4]. FAQ de Adobe no accesible esta sesión (timeout): scope facial marcado como conocimiento de la base, no re-verificado aquí.
- Referencia de concepto (tradición de animación de personajes, a nivel idea, no citada literal): **The Animator's Survival Kit** (Richard Williams) y **Preston Blair** — timing del parpadeo, la mirada como foco de intención, las mouth-shapes clásicas del habla. Los 12 principios están sintetizados en [ver: gamedev/animacion]; el game-feel en [ver: gamedev/game-feel].
- Bases sintetizadas (no se repite su teoría): **[ver: rigging/deformacion]** (blendshapes = deltas por-vértice, correctivos por driver que NO exporta, `SetBlendShapeWeight`, cara como SMR propio, skinning no batchea), **[ver: rigging/rig-a-unity]** (Model importer, Avatar, Optimize Game Objects + Extra Transforms to Expose, Mixamo body), **[ver: unity/animacion-unity]** (Direct blend tree para blendshapes, `OnAnimatorIK`/SetLookAt, Animation Rigging Multi-Aim, Timeline, Animation Events, 2D/texturas), **[ver: modelado/topologia]** y **[ver: modelado/organico-personajes]** (loops de ojos/boca, la topología facial se decide antes de los shapes).
