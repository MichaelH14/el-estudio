# Animación 2D

> **Cuando cargar este archivo:** al producir o dirigir animación 2D de un juego real — decidir frame-by-frame vs esqueletal 2D (Spine / Unity 2D Animation / DragonBones), presupuestar frame counts de un pixel-art (walk/idle/attack/VFX), montar ciclos 2D loopables, usar onion skinning en Aseprite, timing/holds/snappiness del sprite, animar efectos (explosión, impacto, hit), o exportar el resultado (spritesheet+JSON o datos de hueso) hacia Unity. Es la fase de ANIMACIÓN dentro de la producción de ARTE 2D.

Este archivo NO repite lo que ya está resuelto en otras bases — lo referencia y añade el ángulo 2D de producción:

- **Los 12 principios en gameplay, anatomía de ataque (wind-up/active/recovery), telegraphing, hitstop, frame counts base de sprites** → [ver: gamedev/animacion]. Aquí solo lo que cambia al dibujar frame a frame en baja resolución.
- **La teoría de las poses de un ciclo (contact/down/passing/up), rebote de cadera, run con fase aérea, loop perfecto, foot sliding** → [ver: animacion3d/ciclos-locomocion]. Vale idéntico en 2D; aquí se aplica con menos frames y con el truco del espejo.
- **Responsiveness, input<100ms, coyote time** → [ver: gamedev/game-feel]. **Estilo/paleta/mood** → [ver: gamedev/arte-direccion] y [ver: pixel-art]. **La implementación en Unity (Animator, Sprite Renderer, 2D lights)** → [ver: unity/animacion-unity] y [ver: 2d-a-unity].

---

## 1. Frame-by-frame vs esqueletal 2D: el corte de producción

Dos familias, y la decisión es de presupuesto, no de gusto. La regla maestra sigue siendo la de [ver: gamedev/animacion §4]: **"if it doesn't bend, it doesn't need bones"**.

| Criterio | **Frame a frame** (dibujar cada cuadro) | **Esqueletal 2D** (Spine / Unity 2D Anim / DragonBones) |
|---|---|---|
| Qué es | Cada frame es un dibujo distinto en un spritesheet | Piezas recortadas + huesos + mesh que deforma; se interpola en runtime |
| Coste inicial | Bajo: dibujar y ya | Alto: trocear el personaje, rig, mesh, weights (~15–60 min de mesh por sprite, SPRITETOMESH — [ver: gamedev/animacion]) |
| Coste por animación NUEVA | **Alto**: cada frame se redibuja (walk = 6–12 dibujos) | **Bajo**: walk con 4–6 keyframes interpolados; reusa el rig |
| Iterar el diseño | Redibujar TODO el ciclo | Ajustar keys; cambiar la skin sin tocar animaciones |
| Peso en disco | Spritesheets crecen rápido (file bloat) | Datos de hueso muy ligeros; mejor para networking |
| Blending / mezclas | No hay: corte seco entre clips (o crossfade de sprites, feo) | Crossfade, capas, IK, mezcla en runtime |
| Estilo | Control total: smears, squash libre, deformación por frame | Riesgo de "marioneta de papel" si no se usan mesh + curvas |
| Pixel art nítido | Nativo | **Difícil**: la deformación de mesh rompe la grid de píxeles → NO es el camino para pixel art puro |

**Cuándo cada uno:**
- **Frame a frame** → pixel art de baja resolución (16×16, 32×32, 64×64), VFX (moneda, explosión, chispa), criaturas sin estructura articulada, animaciones únicas no reutilizables, y **siempre que el look sea "pixel perfect"** (el mesh deform pelea con la grid).
- **Esqueletal** → personajes articulados con **3–4+ animaciones**, varios personajes que comparten rig, customización de equipo (skins/attachments en runtime), arte "cutout" de alta resolución (estilo vectorial/pintado), necesidad de blending suave. Es el camino de los juegos con arte "recortado" (no-pixel) y mucho personaje.
- **Híbrido sano y común**: esqueletal para el personaje + frame a frame para VFX e impactos (los efectos "no doblan", se dibujan).

**Las tres herramientas esqueletales 2D:**

| Herramienta | Estado (jul-2026) | Notas |
|---|---|---|
| **Spine** (Esoteric Software) | Estándar de industria, **de pago** (licencia por tramos) | Editor dedicado; features abajo (§9); runtimes oficiales para Unity/Unreal/Godot/web y casi todo lenguaje |
| **Unity 2D Animation** (paquete `com.unity.2d.animation`) | Gratis, dentro de Unity 6 | Skinning Editor integrado; sin editor externo; ideal si ya vives en Unity (§9) |
| **DragonBones** | Gratis/open-source, **desarrollo estancado** (⚠️ verificar mantenimiento antes de casarte con él) | Alternativa histórica gratuita a Spine; formato propio + exporters |

---

## 2. Frame counts en pixel art: el look a pocos frames

En 2D dibujado se anima con MENOS frames que en 3D — y esa economía es parte de la estética, no una limitación. El 3D muestrea continuo (interpola a 30/60 fps); el 2D dibuja poses discretas y las **sostiene** (holds). Pocos frames bien elegidos leen como "snappy" y con carácter; muchos frames mal cronometrados leen "flotante".

**Base de frame counts** (piso, no techo — tabla completa en [ver: gamedev/animacion §3]):

| Acción | Frames típicos | Ángulo 2D específico |
|---|---|---|
| Idle | 2–4 | Un breathing de 2 frames ya bate a un frame fijo. Loop largo evita el "tic-tic" |
| Walk | 4–6 (8–12 si el estilo pide fluidez) | Con el truco del espejo, medio ciclo dibujado = ciclo completo (§5) |
| Run | 6–8 | Poses más extremas que el walk, no solo más rápidas |
| Attack | 3–6 | 1 anticipación + 1–2 de extensión/smear + 2–3 recovery |
| Jump | 3–5 | Squash despegue + stretch aire + squash aterrizaje |

- **El caso extremo** que fija el precio del frame-by-frame: **Cuphead**, ~50.000 frames a mano en el juego base (72.000 con el DLC, récord Guinness), ~25 min por frame — [ver: gamedev/animacion §4]. No elijas ese look por accidente: multiplica frames × acciones × personajes antes de decidir.
- **Resolución manda sobre frame count**: a 16×16 no CABE detalle de sub-poses; el movimiento se lee en la silueta y en 3–4 frames. A 64×64+ empieza a compensar más fluidez. Casa el detalle de animación con la resolución del sprite [ver: pixel-art].

---

## 3. Timing en 2D: duración por frame, holds y "on twos"

En pixel art el timing se controla con la **duración de cada frame en milisegundos** (en Aseprite cada frame lleva su propia duración; se edita en el timeline — [ver: aseprite-flujo]). No hay curvas: hay poses y cuánto tiempo se sostiene cada una.

- **El timing manda sobre el frame count**: 4 frames con holds bien puestos leen mejor que 12 uniformes. Patrón de golpe (pixel art): wind-up rápido ~80 ms/frame, **hold del frame de impacto ~300 ms**, hold de anticipación ~400 ms antes de soltar — [ver: gamedev/animacion §3].
- **"On ones / twos / threes"** = cuántos frames de pantalla se sostiene cada dibujo:
  - **On ones** (1 dibujo por frame de pantalla) = máxima fluidez, más caro. Reservado para acción rápida y VFX.
  - **On twos** (1 dibujo cada 2 frames de pantalla, ~12 dibujos/s a 24) = el default económico del 2D dibujado; suficiente para casi todo.
  - **On threes+** = estilizado, "stop-motion", staccato deliberado.
- **Desacople fps de animación ≠ fps del juego**: Cuphead se animó a **24 fps "on ones"** mientras el juego corre a **60 fps** — la simulación e input van al hardware, la animación va a su ritmo artístico ([ver: gamedev/animacion §3]). En sprites esto se implementa con la duración por frame; el juego actualiza a 60, el sprite cambia de dibujo cuando su timer lo dice.
- **Snappy vs suave**: gameplay quiere transición al frame activo casi instantánea (snappy); la suavidad se reserva para follow-through e idles. El "salto" brusco a los frames de impacto al pulsar botón es CORRECTO (Sakurai) — [ver: gamedev/animacion §3].
- **Holds desiguales** son la herramienta #1: no repartas el tiempo por igual entre frames. Anticipación larga, impacto sostenido, recovery variable.

---

## 4. Los 12 principios en 2D: cuáles pesan y qué cambia

El canon completo (los 12 traducidos a gameplay) está en [ver: gamedev/animacion §1]. Lo que el 2D dibujado hace DISTINTO al 3D:

| Principio | Qué cambia en 2D frame-a-frame |
|---|---|
| **Timing** ⭐⭐⭐ | Igual de rey, pero se ejecuta con duración por frame + holds, no con curvas. Ver §3 |
| **Squash & Stretch** ⭐⭐⭐ en 2D | **Aquí es GRATIS y radical**: en 3D muchos motores no escalan huesos ([ver: gamedev/animacion §1]); en un sprite redibujas la forma como quieras — aplasta al aterrizar, estira en el salto sin coste técnico. El 2D es donde S&S brilla más |
| **Anticipación** ⭐⭐⭐ | Mismo conflicto responsiveness↔peso. En el jugador: 1–3 frames. En enemigos: wind-up largo = telegraph. Igual que 3D |
| **Smears (exageración de velocidad)** | Un frame donde el arma/brazo se estira o se multiplica vendiendo velocidad. El látigo de Castlevania: ~3 px de smear. Barato y letal para strikes de 1–2 frames — [ver: gamedev/animacion §3]. Es el equivalente 2D del motion blur |
| **Exageración** ⭐⭐⭐ | En baja resolución la silueta ES la lectura: exagera hasta que la pose se distinga en 16×16. Menos píxeles = más exageración necesaria |
| **Pose a pose** | Gana en juegos: dibujas las poses clave (keys) primero, los in-betweens después. Permite iterar sin terminar |
| **Follow-through / overlap** | Sin huesos hijos: se dibuja a mano (1–2 frames de "asentamiento" de capa/pelo tras la pose principal). En esqueletal 2D sí puedes retrasar huesos hijos 2–4 frames |
| **Solid drawing** | "Solid drawing" literal: volumen, que la forma no se aplane sin querer entre frames; consistencia de silueta cuadro a cuadro |

**Síntesis 2D**: gobiernan **Timing, Squash & Stretch y Anticipación**; y el 2D añade dos herramientas propias baratísimas — **smears** y **holds desiguales** — que valen más que subir el frame count.

---

## 5. Ciclos 2D: walk / run / idle con pocas poses

La **teoría de las poses** (contact / down / passing / up, rebote de cadera, run = fase aérea, cierre de loop, foot sliding) está completa en [ver: animacion3d/ciclos-locomocion]. Vale idéntica en 2D. Lo específico del sprite:

- **Truco del espejo (mirror)**: un walk se construye con las 4 poses de MEDIO ciclo (un paso); el paso opuesto es el espejo horizontal. En pixel art frontal/lateral simétrico, dibujas ~4 poses y espejas → ciclo completo con la mitad del trabajo. (No sirve si el personaje es asimétrico: pelo de lado, arma en una mano, sombreado direccional.)
- **Pocas poses, más lectura**: el walk mínimo jugable es **contact + passing por lado** (2 poses × 2 = 4 frames) que ya lee. Súbelo a 6–8 si quieres el down/up marcado.
- **El rebote vertical** (cadera sube/baja dos veces por ciclo) se dibuja moviendo el cuerpo 1–2 px arriba/abajo entre poses. Sin ese bob, el sprite "flota" — mismo pecado que en 3D.
- **Idle nunca es 1 frame**: 2–4 frames de breathing (pecho/hombros ±1 px) + parpadeo ocasional. Un idle de 1 frame lee como "juego pausado" — [ver: animacion3d/ciclos-locomocion §4].
- **Loop perfecto en 2D**: regla del frame duplicado — el frame de inicio y "el que vendría DESPUÉS del último" deben ser la misma pose; **no dibujes el último frame igual al primero** o el motor reproduce la pose dos veces → tartamudeo. En Aseprite el tag define el rango que loopea (§6–7); Unity lo reproduce con el Animator [ver: unity/animacion-unity].
- **Ping-pong ≠ loop real**: un idle de respiración PUEDE usar dirección Ping-pong (sube y baja reusando frames); un walk NO (necesita ciclo completo, ping-pong lo haría "caminar hacia atrás").

---

## 6. Onion skinning: ver los frames vecinos para animar

Herramienta central del frame-a-frame: mostrar los frames anterior(es) y siguiente(s) semitransparentes bajo el frame actual, para dibujar el in-between con referencia. Detalle de flujo en [ver: aseprite-flujo]; lo esencial verificado en la doc de Aseprite:

- **Activar**: tecla **F3**, o el icono de onion skin en el timeline.
- **Config** (icono "Configure Timeline" en el timeline): número de frames **previos y siguientes** a mostrar, y **tinte rojo/azul** para distinguir pasado (rojo) vs futuro (azul). *(La doc oficial de Aseprite no detalla rangos de opacidad exactos ni modos de merge en esa página — confirmar valores finos en la UI; no los inventes.)*
- **Uso**: dibujas las poses clave primero (pose a pose), activas onion, y rellenas los in-betweens viendo hacia dónde va cada extremidad. Es el "papel cebolla" del animador tradicional, en digital.

---

## 7. Flujo de animación en Aseprite: tags, duración, preview

Aseprite es el estándar de pixel art animado (2026). Mecánica verificada contra su doc oficial (UI completa en [ver: aseprite-flujo]):

- **Tags** (secuencias con nombre en UN archivo): cada tag = una animación (walk, idle, attack) dentro del mismo sprite. Crear: **Frame > Tags > New Tag**, o click-derecho en un rango > **New Tag**, o **F2** dos veces (la 1ª crea un tag "Loop" por defecto, la 2ª abre sus propiedades).
  - **Animation Direction** (la propiedad clave del tag): **Forward** (inicio→fin), **Reverse** (fin→inicio), **Ping-pong** (alterna ida y vuelta). *(Versiones recientes añaden un contador de repeticiones por tag — confirmar en la UI; la doc del excerpt no lo detalla.)*
  - Un solo archivo `.aseprite` con tags walk/idle/attack → un solo spritesheet + JSON con todos los rangos (§10). Es el patrón de handoff.
- **Duración por frame**: cada frame tiene su duración en ms (timeline). Aquí vive el timing de §3 — holds largos en impacto, cortos en wind-up.
- **Preview**: ventana de reproducción en loop del tag activo, a la velocidad real. **Verifica el loop AQUÍ** antes de exportar (que no tartamudee, que la respiración no salte).
- **Capas + celdas (cels)**: separar personaje/arma/efecto en capas para animarlos independientes y exportarlos juntos o por separado (`--split-layers`, §10).

---

## 8. Animación de efectos 2D (VFX de sprite): los frames de un hit

Los efectos "no doblan" → casi siempre **frame a frame**, incluso en juegos de personaje esqueletal (el híbrido de §1). Van rápido (on ones, ~40–80 ms/frame) y viven poco. Frame counts de práctica indie (⚠️ convención, no doc única — calibrar a ojo):

| Efecto | Frames típicos | Notas de animación |
|---|---|---|
| **Hit spark / chispa de impacto** | 2–4 | Nace grande y brillante, colapsa rápido. El frame 1 es el más grande (flash) |
| **Muzzle flash / fogonazo** | 2–3 | Instantáneo; 1 frame de flash + 1–2 de disipación |
| **Explosión** | 5–8 (+ humo residual) | Expansión (S&S: crece rápido) → pico → disipación/humo que se desvanece. El pico se sostiene 1 hold |
| **Slash / weapon trail** | 3–5 | Arco de smear que barre la zona de peligro; marca dónde golpea |
| **Polvo de aterrizaje / pasos** | 3–5 | Se expande hacia afuera y baja opacidad; refuerza el peso |
| **Recogida / pickup (moneda, ítem)** | 4–8 | Loop de brillo/rotación; on twos basta |

- **Anatomía de un efecto** = nace (flash grande) → pico (hold breve) → muere (disipa/encoge/desvanece). Es squash&stretch puro: crece rápido, muere rápido.
- **Additive/blend en el motor**: los VFX luminosos (chispa, explosión, fogonazo) suelen ir con blending aditivo y **2D lights** para que "quemen" — eso es implementación [ver: unity/animacion-unity] y [ver: 2d-a-unity], no dibujo.
- **Hitstop y screen shake** venden más que añadir frames al efecto — [ver: gamedev/animacion §2] y [ver: gamedev/game-feel]. Un hit de 3 frames + 4 frames de hitstop pega más que uno de 10 frames sin pausa.
- **Smear como VFX barato**: para un strike de 1–2 frames, el propio smear del arma ES el efecto (Castlevania) — no siempre necesitas una capa de VFX aparte.

---

## 9. Esqueletal 2D en profundidad: cuándo compensa y cómo

Compensa cuando el ahorro por animación nueva supera el coste de rig, es decir con **3–4+ animaciones**, varios personajes con el mismo rig, o customización en runtime (skins/attachments). El look debe tolerar deformación de mesh (NO pixel art puro).

**Spine** (features verificadas, sitio oficial Esoteric):
- **Bones** (esqueleto de huesos), **mesh skinning / weights** (doblar y deformar imágenes con malla ponderada = brazos que curvan, tela que ondula), **skins / attachment swapping** (customización: cambiar cabeza/arma/armadura sin re-animar), **IK constraints**, **path constraints**, **transform constraints** (copia rotación/traslación/escala/shear de un hueso a otros — no en el tier Essential), **dopesheet** (timing), **Ghosting** (el onion skin del esqueletal: ghosts por frame o solo-keyframe, vectores de movimiento, render imagen/silueta/x-ray), efectos **pseudo-3D**.
- **Runtimes** oficiales para Unity, Unreal, Godot, web y casi todo lenguaje: exportas datos (`.json`/`.skel` + `.atlas` + textura) y el runtime los reproduce e interpola en el juego.

**Unity 2D Animation** (paquete `com.unity.2d.animation`, Skinning Editor integrado — herramientas verificadas):
- Flujo: importar arte (el **PSD Importer** convierte un PSD por capas en un **Prefab de Sprites** listo para riggear) → abrir **Skinning Editor** → riggear → **Sprite Skin** (componente runtime) deforma la malla en juego.
- **Huesos**: **Create Bone** (Shift+E: click inicio, click fin), **Edit Bone** (Shift+W: mover/rotar la pose por defecto, autoguarda como bind pose), **Split Bone** (Shift+R: divide un hueso en segmentos) — verificados en la doc oficial de shortcuts del Skinning Editor. *("Reparent Bone" no aparece como herramienta separada en esa página — no confirmado, no lo des por hecho en la app.)*
- **Geometría/malla**: **Auto Geometry** ("Generate For Selected" genera la malla), **Edit Geometry**, **Create Vertex**, **Create Edge** (malla manual).
- **Weights**: **Auto Weights** (autogenera el peso si hay geometría + huesos que la cruzan), **Weight Slider** y **Weight Brush** (ajuste fino), **Bone Influence** (qué huesos afectan a un sprite), **Sprite Influence** (qué sprites afecta un hueso).
- **Verificación**: **Preview Pose** (mover huesos para comprobar que la malla deforma bien sin romperse).
- **IK y Sprite Swap** están en el mismo paquete (IK 2D via componentes; Sprite Library/Sprite Resolver para intercambiar sprites por categoría — customización). Detalle de consumo en runtime → [ver: unity/animacion-unity] y [ver: 2d-a-unity].

**Regla de decisión** (repite el §1 pero cerrada): un personaje con idle+walk+run+attack+hurt (5 animaciones) que además cambia de arma → esqueletal. Un slime con idle+squish (2 animaciones, deforma orgánico) → frame a frame. Un enemigo pixel-perfect a 24×24 → frame a frame SIEMPRE (el mesh rompe la grid).

---

## 10. Export y handoff a Unity

Dos caminos según la familia (§1). Detalle de importación y settings en [ver: 2d-a-unity]; aquí el lado del artista.

**A) Frame a frame → spritesheet + datos** (Aseprite CLI, flags verificados):
- `--sheet hoja.png` genera la hoja; `--data datos.json` los metadatos.
- `--sheet-type` = `horizontal` | `vertical` | `rows` | `columns` | `packed`. `--sheet-pack` empaqueta sin desperdicio.
- `--format` = `json-hash` (default) o `json-array`. `--list-tags` incluye los tags en el JSON bajo `frameTags` (así el motor sabe qué frames son walk vs attack).
- `--split-layers` exporta cada capa por separado; `--filename-format` con tokens `{layer}` `{frame}` `{tag}` `{title}`.
- Espaciado: `--inner-padding N` (borde por frame), `--shape-padding N` (separación entre frames — evita bleeding de píxeles vecinos al muestrear). `--trim` recorta bordes vacíos. `--scale N` reescala.
- **Handoff limpio**: un `.aseprite` con tags → CLI → `hoja.png` + `datos.json` con `frameTags`. En Unity: Sprite Mode **Multiple**, **Point (no filter)** filter, **None** compression, PPU consistente, slice por grid/packed [ver: 2d-a-unity].

**B) Esqueletal → datos de hueso**:
- **Spine**: exporta `.json` o `.skel` binario + `.atlas` + PNG del atlas → runtime de Spine para Unity/Unreal/Godot.
- **Unity 2D Animation**: el rig vive en el propio proyecto; los clips son `.anim` reproducidos por el **Animator** [ver: unity/animacion-unity]. No hay "export": se anima y consume dentro de Unity.

**Sprite Atlas (Unity)**: empaquetar los sprites en un atlas reduce draw calls y evita el bleeding en runtime — es paso de pipeline, [ver: 2d-a-unity].

**Pixel Perfect Camera (Unity, `com.unity.2d.pixel-perfect`)** — para que la animación pixel art no "tiemble" (subpixel jitter) ni se deforme al escalar (propiedades verificadas):
- **Asset Pixels Per Unit**: debe coincidir con el PPU de TODOS los sprites.
- **Reference Resolution X/Y**: resolución nativa de diseño; se escala desde ahí en múltiplos enteros.
- **Upscale Render Texture**: renderiza cerca de la Reference Resolution y sube — píxeles sin aliasing.
- **Pixel Snapping**: engancha los sprites a la grid al renderizar (evita jitter subpixel); **se desactiva si Upscale está ON**.
- **Crop Frame** (X/Y, barras negras) y **Stretch Fill**.
- Setup recomendado: filtro **Point**, compresión **None**, pivotes en **Custom / Pixels**, Snap Settings Move X/Y/Z = **1 ÷ PPU**. Cinemachine → extensión Pixel Perfect en la vcam. Detalle en [ver: 2d-a-unity].

**Paletas** (contexto de arte, no de animación pero toca al export): **lospec.com/palette-list** es la base de datos de paletas pixel art (hardware + de autor). Canon conocido: **PICO-8 = 16 colores**, **Game Boy DMG = 4 tonos**. Elegir/limitar paleta es fase de [ver: pixel-art]; animar dentro de una paleta fija evita colores "sucios" entre frames.

---

## Reglas prácticas

- [ ] Decide familia ANTES de dibujar: pixel-perfect o VFX o "no dobla" → frame a frame; 3–4+ animaciones / customización / arte cutout → esqueletal. "If it doesn't bend, it doesn't need bones".
- [ ] Presupuesta el frame-a-frame en dibujos totales (frames × acciones × personajes) antes de comprometerte al look — Cuphead costó 50.000 frames y ~25 min/frame.
- [ ] Pixel art frame counts como PISO: idle 2–4, walk 4–6, run 6–8, attack 3–6, jump 3–5. Sube solo si el estilo lo pide.
- [ ] Timing sobre frame count: holds desiguales (impacto ~300 ms, wind-up ~80 ms/frame) antes que añadir dibujos.
- [ ] Anima "on twos" por defecto; reserva "on ones" para acción rápida y VFX. Desacopla el fps de la animación del fps del juego (Cuphead: 24 anim / 60 juego).
- [ ] Squash & stretch a fondo: en 2D es gratis y es lo que más vende peso (aplasta al caer, estira al saltar).
- [ ] Smear frame para cualquier strike de 1–2 frames (arma estirada/multiplicada); es el "motion blur" barato del 2D.
- [ ] Walk con el truco del espejo: dibuja medio ciclo y espeja — salvo personaje asimétrico (arma, pelo de lado, sombreado direccional).
- [ ] Idle NUNCA de 1 frame: breathing de 2–4 frames + parpadeo; loop largo para que no haga "tic-tic".
- [ ] Cierra el loop con la regla del frame duplicado: no repitas el frame de inicio como último; el motor loopea 0→N→0.
- [ ] Ping-pong solo para ciclos simétricos (respiración); NUNCA para un walk (lo haría caminar hacia atrás).
- [ ] Onion skinning (F3) SIEMPRE para in-betweens; tinte rojo=pasado, azul=futuro; dibuja las keys primero (pose a pose).
- [ ] Un `.aseprite` por personaje con tags (walk/idle/attack); verifica cada loop en el Preview de Aseprite antes de exportar.
- [ ] VFX frame a frame aunque el personaje sea esqueletal: hit 2–4f, explosión 5–8f, van rápido y mueren rápido. Hitstop + shake pegan más que más frames.
- [ ] Export pixel art: Aseprite CLI `--sheet --data --list-tags --format json-hash` con `--shape-padding` ≥1 (evita bleeding); en Unity Point filter, None compression, PPU consistente.
- [ ] Pixel Perfect Camera con Asset PPU = PPU de sprites, Reference Resolution nativa, Point/None, Snap = 1/PPU — o el sprite tiembla al moverse.
- [ ] Esqueletal en Unity: PSD Importer → Skinning Editor (Create Bone → Auto Geometry → Auto Weights → Weight Brush a mano) → Preview Pose → Sprite Skin en runtime.
- [ ] No metas mesh deform en pixel art puro: rompe la grid de píxeles.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Elegir frame a frame "porque se ve mejor" sin presupuestar | Calcula dibujos totales (frames×acciones×personajes) — Cuphead = 50.000 frames a mano |
| Esqueletal en pixel art puro → la malla deforma y rompe la grid | Frame a frame para todo lo pixel-perfect; esqueletal solo para arte cutout/alta res |
| Repartir el tiempo por igual entre frames → animación flotante | Holds desiguales: wind-up corto, impacto sostenido; el timing lee el peso |
| Subir el frame count buscando fluidez cuando falta lectura | Menos frames + poses más exageradas + smears; a baja resolución la silueta es la lectura |
| Idle de 1 frame ("juego pausado / roto") | Breathing 2–4f additive + parpadeo; loop largo |
| Último frame del loop == primer frame → tartamudeo cada vuelta | Regla del frame duplicado: el motor loopea 0→N→0; no dupliques la pose de inicio |
| Ping-pong en un walk → "camina hacia atrás" | Ping-pong solo para ciclos simétricos (respiración); walk = ciclo completo |
| Sprite que "tiembla" al moverse en Unity | Pixel Perfect Camera + Point filter + Snap 1/PPU + PPU consistente; nada de subpixel |
| Bleeding: píxeles del sprite vecino aparecen en el borde | `--shape-padding` ≥1 al exportar y/o extrude en el Sprite Atlas |
| Strike de 1–2 frames que no se lee | Smear frame del arma; el propio smear marca la zona de peligro |
| VFX animado lento y largo buscando impacto | Efecto corto (nace grande→pico→muere) + hitstop + screen shake |
| Squash & stretch tímido en 2D "por realismo" | En 2D es gratis y estilístico: exagéralo, es donde S&S más brilla |
| Rig esqueletal sin mesh/weights → "marioneta de papel" recortada | Mesh con weights + curvas; frames de smear dibujados para strikes |
| Personaje que "flota" al caminar | Bob vertical de cadera (1–2 px arriba/abajo por paso); sin rebote no hay peso |
| Exportar cada animación a un archivo suelto | Un `.aseprite` con tags → un spritesheet + JSON con `frameTags`; handoff único |

## Fuentes

**Bases de El Estudio sintetizadas (referenciadas, no repetidas):**
- [ver: gamedev/animacion] — 12 principios en gameplay, anatomía de ataque (wind-up/active/recovery), telegraphing, hitstop, smears, frame counts base de sprites, Cuphead (50.000 frames / 24fps on-ones / 60fps juego), tabla sprite vs esqueletal, SPRITETOMESH (15–60 min mesh/sprite).
- [ver: animacion3d/ciclos-locomocion] — teoría de las poses del ciclo (contact/down/passing/up), rebote de cadera, run = fase aérea, loop perfecto (regla del frame duplicado), foot sliding. Vale idéntico en 2D con menos frames.
- [ver: gamedev/game-feel] — responsiveness, input<100ms, coyote time, screen shake. [ver: pixel-art], [ver: aseprite-flujo], [ver: 2d-a-unity], [ver: unity/animacion-unity] — fases hermanas.

**Fuentes web (verificadas por fetch, jul-2026):**
- **Onion Skinning** — Aseprite Docs oficial (`aseprite.org/docs/onion-skinning`) — F3 / icono timeline; nº de frames prev/next; tinte rojo/azul; config vía "Configure Timeline". (Rangos de opacidad/modos NO detallados en la página — confirmar en UI.)
- **Tags** — Aseprite Docs oficial (`aseprite.org/docs/tags`) — Frame > Tags > New Tag / F2×2; Animation Direction: Forward / Reverse / Ping-pong; un archivo con múltiples animaciones.
- **Exporting a Sprite Sheet / CLI** — Aseprite Docs oficial (`aseprite.org/docs/sprite-sheet` + `aseprite.org/docs/cli`) — `--sheet`, `--data`, `--sheet-type` (horizontal/vertical/rows/columns/packed), `--sheet-pack`, `--format` json-hash/json-array, `--list-tags` (frameTags), `--split-layers`, `--inner-padding`, `--shape-padding`, `--trim`, `--filename-format` ({layer}{frame}{tag}{title}), `--scale`.
- **2D Animation package** — Unity Docs `com.unity.2d.animation@10.0` (index + CharacterRig + `SkinEdToolsShortcuts.html`) — rig/animar 2D; PSD Importer → Prefab de sprites; Skinning Editor: Create Bone (Shift+E), Split Bone (Shift+R), Edit Bone (Shift+W), Auto Geometry (Shift+A), Edit Geometry (Shift+S), Create Vertex (Shift+D), Create Edge (Shift+G), Split Edge (Shift+H), Auto Weights (Shift+Z), Weight Slider (Shift+X), Weight Brush (Shift+N), Bone Influence (Shift+V), Sprite Influence (Shift+M), Preview Pose (Shift+Q), Reset Pose (Shift+1) — nombres y shortcuts verificados en la doc oficial.
- **Pixel Perfect Camera** — Unity Docs `com.unity.2d.pixel-perfect@5.0` — Asset Pixels Per Unit, Reference Resolution, Upscale Render Texture, Pixel Snapping (off si Upscale), Crop Frame, Stretch Fill; setup Point/None, Snap 1÷PPU, pivot Custom/Pixels, Cinemachine Pixel Perfect.
- **Spine (features)** — Esoteric Software (sitio oficial, `spine-in-depth` + `spine-transform-constraints` + `spine-ghosting`) — bones, mesh skinning/weights, skins (attachment swap), IK / path / transform constraints, dopesheet, y **Ghosting** (nombre oficial: onion skin del esqueletal — ghosts por frame o solo-keyframe, vectores de movimiento, render como imagen/silueta/x-ray, offset configurable); pseudo-3D; runtimes Unity/Unreal/Godot/web. Todas confirmadas por fetch directo esta pasada.
- **Lospec Palette List** — lospec.com/palette-list — base de datos de paletas pixel art (hardware + de autor). PICO-8 = 16 colores y Game Boy DMG = 4 tonos son canon de hardware conocido; contar/confirmar palettes específicas en el sitio.

**Canon de pixel art (nivel concepto, ampliamente documentado):**
- **Pedro Medeiros / Saint11** (`saint11.art`, ex `saint11.org`) — tutoriales canónicos de pixel art (smears, on twos, animación low-res). ⚠️ La página redirige; contenido tratado como conocimiento previo consistente con la práctica indie, no re-verificado línea a línea esta sesión.
- **Pixel Logic** — Michael Azzi — manual de referencia de pixel art (dithering, anti-aliasing, animación); citado a nivel de concepto.

*Gaps / a verificar en la siguiente pasada: (1) rangos exactos de opacidad y modos de onion skin en la UI de Aseprite; (2) contador de repeticiones por tag en Aseprite 2026 (feature reciente — confirmar en la app); (3) frame counts de VFX (§8) son convención indie, no doc única — calibrar por proyecto; (4) estado de mantenimiento real de DragonBones en 2026; (5) "Reparent Bone" en el Skinning Editor de Unity no aparece en `SkinEdToolsShortcuts.html` (Create Bone/Split Bone/Edit Bone sí confirmados con shortcuts) — no asumir que existe como herramienta separada; (6) componente Sprite Skin runtime referenciado por conocimiento previo, no confirmado en el fetch de esta sesión.*
