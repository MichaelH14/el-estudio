# Narrativa y localización en Unity

> **Cuando cargar este archivo:** al implementar diálogo (Ink/Yarn Spinner), localización (Unity Localization: tablas, locales, fuentes por idioma), texto dinámico, subtítulos/cinemáticas con Timeline, o voice-over multi-idioma en un proyecto Unity 6.x. La teoría de guion/branching está en [ver: gamedev/narrativa-guion]; la técnica de UI/TMP en [ver: unity/ui-unity] — esto es la unión.

Verificado contra: Unity Localization **1.5.12**, ink-unity-integration **2.x** (Ink 2 requiere Unity 2022.3+), Yarn Spinner for Unity **3.2.7** (jul 2026, Unity 2022.3+), Timeline **1.8.12**. Todo corre en Unity 6.x/URP.

## 1. Mapa: qué sistema para cada texto del juego

Regla de oro del puente: **cada texto vive en UN solo sistema**. No dupliques diálogo en string tables ni UI en el guion.

| Tipo de texto | Sistema | Por qué |
|---|---|---|
| Diálogo ramificado, quests, barks con lógica | Ink o Yarn Spinner (§2-4) | Traen estado, branching y su propio pipeline i18n |
| UI: menús, HUD, tooltips, mensajes de sistema | Unity Localization — string tables (§6) | Componentes que se auto-actualizan al cambiar locale |
| Texto con variables (puntos, nombre, plurales) | String tables + Smart Strings (§7) | Plural/género/formato por locale sin código extra |
| Fuentes TMP, texturas con texto, VO | Unity Localization — asset tables (§8, §12) | Un asset distinto por locale, misma clave |
| Subtítulos de cinemáticas | String tables + Timeline (§11) | Timing en Timeline, texto en tablas |

- Elegir herramienta de diálogo por el workflow del escritor y el patrón de branching ANTES de escribir [ver: gamedev/narrativa-guion]. Aquí solo la capa Unity.
- El resto del pipeline de pantallas/menús donde estos textos aterrizan: [ver: ui-flujo-completo].

## 2. Ink en Unity: ink-unity-integration

**Instalación** (paquete `com.inkle.ink-unity-integration`): Package Manager → "Install package from git URL" → `https://github.com/inkle/ink-unity-integration.git#upm`. Alternativas: OpenUPM o el .unitypackage de releases. Ink 2.x requiere Unity 2022.3 LTS+.

**Compilación:** los `.ink` se compilan solos vía ScriptedImporter al crear/editar. El JSON compilado queda en el asset `InkFile` (`inkFile.storyJson`). Solo los archivos "master" (no incluidos por otros) compilan a historia jugable; un include se puede marcar "Compile As Master File" en import settings. El paquete trae un **Ink Player Window** para jugar/depurar la historia sin escena.

**Runtime — el loop completo** (API verificada en la doc oficial de ink):

```csharp
using Ink.Runtime;

public class InkDriver : MonoBehaviour
{
    [SerializeField] TextAsset inkJson;   // el JSON compilado
    Story story;

    void Awake()
    {
        story = new Story(inkJson.text);
        story.BindExternalFunction("dar_item", (string id) => Inventario.Dar(id));
        story.ObserveVariable("reputacion", (name, val) => hud.SetRep((int)val));
    }

    public void Avanzar()                 // llamar desde el botón "continuar"
    {
        if (story.canContinue) {
            string linea = story.Continue();          // UNA línea por llamada
            ui.MostrarLinea(linea, story.currentTags); // tags: ["speaker:Ana", ...]
        }
        else if (story.currentChoices.Count > 0)
            ui.MostrarOpciones(story.currentChoices);  // botón i → story.ChooseChoiceIndex(i)
        else
            ui.CerrarDialogo();
    }
}
```

- `ContinueMaximally()` devuelve todo el bloque de golpe (útil para logs, no para typewriter).
- Estado de juego ↔ historia: `story.variablesState["oro"] = 50;` y lectura con cast.
- **Guardado:** `story.state.ToJson()` / `story.state.LoadJson(json)` — integra el diálogo en tu sistema de save desde el día 1.
- **Convención de tags** (patrón de oficio, no API): `# speaker: Ana`, `# portrait: ana_enfadada`, `# sfx: puerta` — el driver parsea `currentTags` y dispara UI/audio. Es tu "capa de dirección de escena".
- **Localización: ink NO trae sistema propio.** Opciones reales a 2026: (a) un `.ink` por idioma con estructura idéntica (riesgo de divergencia — exige diff disciplinado por release), (b) tags con ID por línea + tabla externa (tooling custom). Existen herramientas comunitarias de extracción — NO VERIFICADO cuál es estable; evaluar antes de apostar. Si el juego nace multi-idioma y el diálogo es grande, este punto favorece a Yarn (§4).

## 3. Yarn Spinner 3 en Unity

**Instalación:** Asset Store / itch.io (de pago; incluyen add-ons: Text Animator, integración con Unity Localization y soporte de voice-over) o gratis por git URL `https://github.com/YarnSpinnerTool/YarnSpinner-Unity.git#current` / OpenUPM (`dev.yarnspinner.unity`, scope `dev.yarnspinner`). Unity 2022.3+.

**Componentes runtime** (nombres exactos v3):

| Componente | Rol |
|---|---|
| `DialogueRunner` | El puente guion↔juego. Propiedades: Yarn Project, Dialogue Presenters, Variable Storage, Line Provider, Start Automatically/Start Node. Eventos: On Node Start/Complete, On Dialogue Start/Complete, On Unhandled Command. Método clave: `StartDialogue(nodo)` |
| Variable Storage | Estado de variables Yarn; si no asignas uno, crea In Memory Variable Storage (no persiste — para saves, implementa el tuyo contra tu sistema de guardado) |
| Line Provider | Recibe line IDs y devuelve la línea localizada + assets (audio VO); default: Builtin Localisation Line Provider |
| Dialogue Presenters | Las vistas que muestran líneas/opciones (antes "Dialogue Views" en v2); los prefabs de ejemplo traen presenter de línea y de opciones listos |

**Comandos y funciones** (el pegamento con gameplay, verificado en doc v3):

```csharp
[YarnCommand("leap")]
public void Leap() { /* en Yarn: <<leap MyCharacter>> — busca el GameObject por nombre */ }

[YarnFunction("add_numbers")]
public static int AddNumbers(int a, int b) => a + b;   // en Yarn: {add_numbers(1,1)}
```

- Alternativa manual: `dialogueRunner.AddCommandHandler<T>("nombre", Metodo)`.
- Comandos que devuelven `IEnumerator` o `YarnTask` **pausan el diálogo hasta terminar** — así se hacen momentos scripted dentro de una conversación (mover cámara, animar, esperar). [ver: unity/csharp-patrones] para corrutinas vs Awaitable.

**Localización en Yarn (su punto fuerte):**

1. Cada línea necesita un ID: `#line:1a64a5`. Botón **"Add Line Tags to Scripts"** en el Yarn Project los genera para todo lo no taggeado. Sin IDs completos no se puede generar el strings file.
2. Export CSV desde el inspector del Yarn Project → traducir → re-importar.
3. Dos backends: **Built-in Localisation** (setup fácil, suficiente para texto) o **Unity Localization** (más features, más configuración — úsalo si ya tienes el paquete para la UI, así TODO el juego cambia de idioma con un solo `SelectedLocale`).
4. VO: "Localised Line Assets" — audio por línea y por locale, servido por el Line Provider (§12).

## 4. Ink vs Yarn: la decisión en Unity

Complementa la tabla de workflow de escritor de [ver: gamedev/narrativa-guion] con los criterios que solo se ven desde Unity:

| Criterio Unity | Ink | Yarn Spinner 3 |
|---|---|---|
| UI de diálogo | La haces tú entera (§5) — control total, más trabajo | Presenters/prefabs listos + se reemplazan por custom |
| Localización | Nada first-party (§2) | Line IDs + CSV + integración Unity Localization |
| VO por línea | Convención de tags + tu código | Soportado (Localised Line Assets) |
| Gameplay desde el guion | `BindExternalFunction` (tú defines el contrato) | `[YarnCommand]`/`[YarnFunction]` + comandos que pausan |
| Prosa densa, lógica de estado compleja | Su terreno natural (weave, tracking automático de lo visto) | Correcto pero el formato es nodo-a-nodo |
| Depurar sin escena | Ink Player Window | Menos tooling equivalente en editor — NO VERIFICADO en esta pasada |

**Regla rápida:** juego con MUCHO texto ramificado y un solo idioma (o loc tardía) → Ink. Diálogo de personajes en un juego con gameplay propio, multi-idioma o con VO → Yarn Spinner 3. No mezcles ambos en un proyecto.

## 5. UI de diálogo: typewriter, choices, barks

Arquitectura mínima (uGUI, [ver: unity/ui-unity] para canvas/TMP/safe area): un canvas de diálogo propio (frecuencia de cambio alta — separado del HUD), con caja de texto TMP, retrato/nombre, contenedor de opciones y un input "avanzar/skip".

**Typewriter correcto — `maxVisibleCharacters`, nunca concatenar:**

```csharp
IEnumerator TypeLine(TMP_Text label, string linea, float cps = 40f)
{
    label.text = linea;                 // texto completo: rich text y wrap se calculan UNA vez
    label.ForceMeshUpdate();
    int total = label.textInfo.characterCount;
    label.maxVisibleCharacters = 0;
    for (int i = 1; i <= total; i++) {
        label.maxVisibleCharacters = i;
        if (skipRequested) { label.maxVisibleCharacters = total; yield break; }
        yield return new WaitForSeconds(1f / cps);
    }
}
```

Por qué: añadir chars a `.text` regenera la mesh en cada append y hace que las palabras salten de renglón a mitad de escritura; `maxVisibleCharacters` revela una mesh ya maquetada. Además los tags rich text no se "escriben" a medias.

- **Skip siempre**: primer input completa la línea, segundo avanza. Sin esto, el playtest muere en 10 minutos.
- **Choices:** botones de un pool (no Instantiate/Destroy por conversación), en un `VerticalLayoutGroup` (uso legítimo: cantidad variable en runtime). Cada botón captura su índice → `ChooseChoiceIndex(i)` / selección del presenter. Navegables con gamepad [ver: unity/input-system].
- **Barks:** el diseño (reglas/criterios/cooldowns) está en [ver: gamedev/narrativa-guion] §3. En Unity: texto flotante vía canvas Overlay + `WorldToScreenPoint` (patrón exacto en [ver: unity/ui-unity] §8), texto desde string table por clave, y prioridad única (un bark visible por NPC).
- Diálogo interrumpible por gameplay: diseña pausa/reanudación desde el día 1 (lección Firewatch, [ver: gamedev/narrativa-guion]).

## 6. Unity Localization: setup mínimo que funciona

Paquete `com.unity.localization` (verificado con 1.5.12). Usa **Addressables** por debajo para locales y tablas [ver: unity/assets-pipeline-git].

**Setup (una vez):**

1. **Edit > Project Settings > Localization** → Create (crea el asset Localization Settings).
2. Locale Generator (ahí mismo) → crear un asset Locale por idioma (es, en, ht…).
3. **Window > Asset Management > Localization Tables** → New Table Collection → **String Table Collection** (texto) y **Asset Table Collection** (fuentes, texturas, audio).
4. Para el build: los grupos Addressables de localización se gestionan en Window > Asset Management > Addressable Assets > Groups.

**Selección de locale al arrancar:** la lista de **Locale Selectors** se consulta en orden (índice 0 primero); si uno devuelve null pasa al siguiente. Verificados: `SystemLocaleSelector` (detecta idioma del dispositivo: iOS prefs → Android → culture → system language) y Specific Locale Selector (fallback fijo). El paquete trae más selectores (línea de comandos, persistencia en PlayerPrefs) — confirmar nombres exactos en la doc antes de referenciarlos por código. Cambio en runtime (selector de idioma del menú de opciones — obligatorio [ver: gamedev/ux-ui-onboarding]):

```csharp
var locales = LocalizationSettings.AvailableLocales.Locales;
LocalizationSettings.SelectedLocale = locales.First(l => l.Identifier.Code == "es");
```

**Consumo:**

- UI estática: clic derecho en el componente Text/TMP → **Localize** → añade el componente Localize String Event ya cableado a la tabla. Cero código; se re-emite al cambiar locale.
- Desde código: `LocalizedString` con `TableReference` + `TableEntryReference`:

```csharp
var ls = new LocalizedString("UI", "puntos_ganados");
ls.Arguments = new object[] { puntos };            // args Smart String (no serializados)
ls.StringChanged += txt => label.text = txt;       // dispara al suscribir y al cambiar locale
```

- Síncrono: `GetLocalizedString()` usa `WaitForCompletion` — **no soportado en WebGL**; en WebGL todo async (`GetLocalizedStringAsync`).
- Preload en Localization Settings: No Preloading / Preload Selected Locale (/And Fallbacks) / Preload All Locales. "Initialize Synchronously" bloquea el main thread — solo para juegos chicos donde un hitch en el boot no importa.

## 7. Texto dinámico: Smart Strings (variables, plural, género)

Sintaxis general: `{selector:formatter(opciones):formato}`. Activar "Smart" por entrada de tabla. Verificado en la doc oficial:

| Necesidad | Sintaxis (en la traducción, no en código) |
|---|---|
| Variable posicional | `Tienes {0} monedas` + `Arguments = new object[]{ n }` |
| Plural | `Tienes {0:plural:una manzana\|{} manzanas}` — formas por locale; nombres del formatter: `plural`, `p`, o implícito |
| Género/elección | `{0:choose(m\|f):él\|ella} te espera` — mapea valores a salidas |
| Variable global sin código | `{nombreJugador}` vía Persistent Variables Source (se definen en settings, sin scripting) |
| Número/fecha con formato del locale | `{0:N}` → "1,234.5" en en / "1.234,5" en es — NUNCA formatear números a mano |
| Anidado | `{User.Address:{Street}, {City}}` |

- Variables locales serializadas por LocalizedString: `ls.Add("hp", new IntVariable { Value = 100 })` y en el string `{hp}`.
- **La regla que salva la localización:** el ORDEN de las palabras cambia por idioma. Jamás construir frases concatenando fragmentos traducidos; una sola entrada Smart String con placeholders, y cada traducción reordena como su gramática pida.
- Plural/género DENTRO del diálogo Ink/Yarn: cada herramienta tiene su mecanismo propio (en Yarn hay markup de formato; sintaxis exacta NO VERIFICADA en esta pasada — confirmar en docs.yarnspinner.dev antes de usar). No mezcles Smart Strings con texto que vive en el guion.

## 8. Fuentes por idioma: TMP + asset tables

Base TMP (atlas SDF, character sets, fallbacks y su coste): [ver: unity/ui-unity] §6. Lo que añade la localización:

- Latín (es/en/fr/pt/ht): una sola fuente estática con el rango completo (áéíóúüñ¿¡ + francés/portugués si aplica) cubre todo — no necesitas fuente por locale.
- CJK/cirílico/árabe: fuente/atlas por locale vía **asset table**: clase verificada `LocalizedTmpFont : LocalizedAsset<TMP_FontAsset>` — la misma clave devuelve el font asset del locale activo; un script cambia `TMP_Text.font` al cambiar locale (o componente localizador de la propiedad).
- Fallbacks TMP: cadena corta; cada fuente extra usada = draw calls extra. Lo previsible va al atlas principal del locale.
- Árabe/hebreo (RTL + shaping contextual): TMP solo no lo resuelve bien — requiere trabajo/plugins extra. NO VERIFICADO el estado 2026 del soporte RTL nativo; si el proyecto necesita RTL, investigar ANTES de comprometer el idioma.
- Tamaños: el mismo layout debe aguantar es (largo) y en (corto) — Auto Size solo en editor para hallar el peor caso, luego fijo ([ver: unity/ui-unity] regla 8).

## 9. Pseudo-localización: probar ANTES de traducir

Asset: **Assets > Create > Localization > Pseudo-Locale**. Genera "traducciones" falsas del idioma fuente que ocupan más espacio y usan caracteres acentuados. Métodos por defecto verificados: **Accenter** (áçèñtos → detecta fuentes/atlas incompletos), **Expander** (alarga el texto → detecta overflow/truncado), **Encapsulator** ([corchetes] → detecta strings cortados y concatenaciones); hay más métodos configurables en el asset.

Qué caza (por eso va ANTES de pagar traducción): texto que se sale o trunca, **strings hardcodeados** (todo lo que NO cambia al activar el pseudo-locale está fuera del sistema — el test más barato que existe), texto compuesto por concatenación, glifos faltantes, texto dentro de texturas. Se activa como cualquier locale (`SelectedLocale` o el menú de locale del Game view). Pásalo como gate de QA en cada milestone con UI nueva [ver: testing-qa].

Heurística de expansión: reserva ~30% de espacio extra sobre el inglés para lenguas romances/alemán (regla de oficio, no cifra oficial — el Expander te lo hace visible).

## 10. Pipeline de traducción: claves, CSV, qué no hardcodear

**Claves estables (la decisión que no se puede deshacer barato):**

- Formato jerárquico: `ui.menu.jugar`, `hud.vidas`, `dlg.ana.intro.010`, `sub.cine01.030`. Numerar diálogo/subtítulos de 10 en 10 (insertar sin renombrar).
- La clave NUNCA es el texto fuente ("Press Start" como clave = cambiar el copy rompe la clave y toda traducción asociada).
- La clave nace con la entrada y no se renombra tras enviar a traducir (Unity añade un Id numérico interno además del Key — el CSV lleva ambos).
- En Yarn los line IDs (`#line:xxx`) cumplen este rol y se generan solos — no los edites a mano.

**Flujo CSV (verificado):** en la ventana de tablas, menú ⋮ → **Export** (CSV o CSV With Comments — los comentarios son el contexto para el traductor: quién habla, dónde aparece, límite de caracteres). Traducir fuera (sheet compartido) → ⋮ → **Import**: **CSV(Merge)** actualiza solo lo presente en el archivo (el modo normal de recibir tandas); CSV pelado reemplaza TODO el contenido. El CSV debe traer columna Key o Id; Id vacío/0 = entrada nueva. El paquete también soporta XLIFF y extensión de Google Sheets (sync directo con un sheet — ideal para iterar con un traductor humano).

**Qué NO hardcodear jamás** (todo esto lo delata el pseudo-locale §9):

1. Strings visibles en código o serializados en prefabs → string table.
2. Frases concatenadas (`"Nivel " + n`) → Smart String con placeholder.
3. Números/fechas/moneda formateados a mano → formato del locale (`{0:N}`).
4. Fuente TMP fija donde hay locales no-latinos → `LocalizedTmpFont`.
5. Texto pintado en texturas/sprites → evitar; si es inevitable, asset table con una textura por locale.
6. Anchos/posiciones exactos para el texto inglés → anchors + espacio de expansión.
7. Orden de palabras asumido (sufijos, "s" de plural pegada por código) → plural/choose del §7.

**Pipeline bilingüe mínimo (es/en) para un solo dev:** 1) todo texto nuevo entra por tabla desde el día 1 (el idioma fuente también — nunca "ya lo migraré"); 2) pseudo-locale pasa limpio antes de traducir; 3) export CSV With Comments → traducir → CSV(Merge); 4) pase visual con el segundo idioma activo en las pantallas con menos espacio; 5) congelar strings antes del pase final de QA (todo cambio de copy post-freeze re-abre traducción). Añadir un tercer idioma = repetir 3-4, coste marginal si 1-2 se respetaron.

## 11. Cinemáticas y momentos scripted: Timeline + Signals + subtítulos

Timeline general (tracks, binding, Cinemachine) en [ver: unity/animacion-unity]; cuándo una cinemática merece existir en [ver: gamedev/narrativa-guion] §7.

**Señales (verificado, Timeline 1.8.12):** trío `SignalAsset` (el evento como asset) + `SignalEmitter` (marker en un track; propiedades: `asset`, `emitOnce` para loops, `retroactive` si el playhead arranca después del marker) + `SignalReceiver` (componente en el GameObject bound: mapea cada SignalAsset → UnityEvent). Úsalas para: disparar un nodo de diálogo Yarn/Ink en un punto exacto, activar cámaras/VFX, dar control al jugador al terminar. Límite práctico: el receiver mapea por SignalAsset, no por instancia — para docenas de subtítulos no escalan; usa un track custom:

```csharp
public class SubtitleClip : PlayableAsset
{
    public LocalizedString texto;   // clave de la string table "Subtitulos"
    public override Playable CreatePlayable(PlayableGraph graph, GameObject owner)
    {
        var p = ScriptPlayable<SubtitleBehaviour>.Create(graph);
        p.GetBehaviour().texto = texto;
        return p;
    }
}
public class SubtitleBehaviour : PlayableBehaviour
{
    public LocalizedString texto;
    public override void OnBehaviourPlay(Playable playable, FrameData info) => SubtitleUI.Show(texto);
    public override void OnBehaviourPause(Playable playable, FrameData info) => SubtitleUI.Hide();
}
[TrackClipType(typeof(SubtitleClip))] public class SubtitleTrack : TrackAsset { }
```

La duración del clip EN el timeline = duración del subtítulo en pantalla: el timing se ajusta arrastrando, no en código, y el texto sigue viviendo en la tabla (traducible sin tocar la cinemática). Patrón estándar de la comunidad sobre la API pública de Playables; `OnBehaviourPause` también dispara al parar el graph — un `if (info.effectivePlayState == PlayState.Paused)` extra distingue fin-de-clip de stop si hace falta (comportamiento clásico de Playables — verificar en tu versión al depurar).

**Reglas de subtítulos** (síntesis de práctica de accesibilidad [ver: gamedev/ux-ui-onboarding]): máx ~2 renglones, fondo semi-opaco o outline (legible sobre cualquier fondo), dentro del safe area, on por defecto o preguntado en el primer arranque, y TODA línea hablada tiene subtítulo — también los barks.

## 12. Voice-over y audio localizado (estructura)

Implementación de audio (mixer, grupos, ducking) en [ver: unity/audio-unity]; diseño de VO y presupuesto en [ver: gamedev/audio].

- **Estructura aunque grabes VO "después":** lo barato es la estructura, lo caro es retrofitearla. Cada línea con ID estable desde el día 1 (§10); archivo de audio nombrado por ID: `dlg_ana_intro_010_es.wav`. Cuando el VO llegue, se enchufa sin tocar guion ni código.
- **Unity Localization:** asset table "VO" con una entrada por línea; clase verificada `LocalizedAudioClip : LocalizedAsset<AudioClip>` (evento `AssetChanged`, carga async) → el driver de diálogo pide el clip de la clave y lo reproduce en el AudioSource de voz.
- **Yarn Spinner:** las Localised Line Assets asocian audio por línea y por locale; el Line Provider entrega línea + clip juntos — el camino con menos fricción si el diálogo ya está en Yarn.
- Canal propio: el VO va a su propio grupo del AudioMixer con ducking de música/SFX mientras habla.
- Duración por idioma: el mismo texto dura distinto grabado en cada idioma — el avance de línea lo marca el FIN DEL CLIP (o el input del jugador), nunca un timer fijo calibrado con un solo idioma.
- Estrategia realista para equipo chico: VO solo en cinemáticas clave + texto para el resto; o VO en un idioma + subtítulos localizados (estándar de la industria incluso en AA).

## Reglas prácticas

1. Cada texto vive en UN sistema: diálogo en Ink/Yarn, UI en string tables, assets en asset tables (§1). Nada duplicado.
2. Elige Ink vs Yarn con la tabla del §4 + el workflow del escritor de [ver: gamedev/narrativa-guion]; multi-idioma o VO por línea inclinan a Yarn 3.
3. Texto nuevo entra por tabla/guion DESDE EL DÍA 1, incluido el idioma fuente. "Ya lo migraré" cuesta 10x.
4. Claves jerárquicas estables (`ui.menu.jugar`, `dlg.ana.intro.010`, de 10 en 10); jamás el texto fuente como clave; jamás renombrar tras enviar a traducir.
5. Ink: guarda `story.state.ToJson()` en tu save; parsea `currentTags` para speaker/retrato/SFX; `BindExternalFunction` para tocar gameplay.
6. Yarn: "Add Line Tags to Scripts" antes del primer export; comandos que pausan (`IEnumerator`/`YarnTask`) para momentos scripted dentro del diálogo.
7. Typewriter con `maxVisibleCharacters` sobre el texto completo, nunca concatenando; skip en dos toques (completar → avanzar) siempre.
8. Choices con pool de botones + navegación de gamepad; barks por clave de tabla vía canvas Overlay + `WorldToScreenPoint`.
9. Un solo punto de verdad para el idioma: `LocalizationSettings.SelectedLocale`; selector de idioma en opciones + persistir la elección.
10. Nunca concatenar fragmentos traducidos ni formatear números a mano: Smart Strings con placeholders, `plural`/`choose`, y `{0:N}` para números.
11. WebGL: cero `GetLocalizedString()` síncrono (usa `WaitForCompletion`, no soportado); todo async.
12. Pseudo-locale como gate de QA por milestone: lo que no cambia al activarlo está hardcodeado; lo que se desborda con Expander necesita layout.
13. Reserva ~30% de expansión sobre el inglés en todo layout con texto (regla de oficio).
14. CSV With Comments para traductores (contexto: quién habla, dónde, límite de chars); re-importar con CSV(Merge), nunca con el reemplazo total salvo intención explícita.
15. String freeze antes del QA final: cambio de copy post-freeze re-abre traducción y VO.
16. Fuentes: latín completo en un atlas estático; locales no-latinos vía `LocalizedTmpFont` en asset table; cadena de fallbacks TMP corta.
17. Subtítulos por track custom de Timeline con `LocalizedString` (duración del clip = duración en pantalla); señales solo para eventos puntuales (disparar diálogo, cámaras, devolver control).
18. VO nombrado por line ID + asset table por locale; el avance de línea lo marca el fin del clip o el input, nunca un timer fijo.

## Errores comunes

| Pitfall | Antídoto |
|---|---|
| Strings hardcodeados "temporales" por todo el proyecto | Regla 3 + pseudo-locale en cada milestone: lo que no cambia, está fuera del sistema |
| Clave = frase en inglés; cambia el copy y se rompe todo | Claves semánticas jerárquicas desde la primera entrada |
| `"Tienes " + n + " monedas"` concatenado — intraducible a idiomas con otro orden | Una entrada Smart String con `{0}`; el traductor reordena |
| Plural a mano (`n + " item(s)"`) | Formatter `plural` del §7 — cada locale define sus formas |
| Typewriter concatenando a `.text` → palabras que saltan de renglón y tags rotos | `maxVisibleCharacters` sobre mesh completa (§5) |
| Diálogo sin skip / cinemática sin skip | Primer input completa, segundo avanza; cinemáticas con skip tras N segundos |
| Elegir Ink por amor a la prosa y descubrir en beta que no localiza | La decisión de idiomas se toma ANTES que la de herramienta (§2, §4) |
| Yarn sin line IDs hasta el final; el export no sale o los IDs bailan | Taggear desde el primer script; los IDs son parte del contrato con traducción y VO |
| Tofu (□) al activar es/fr: atlas TMP con preset ASCII pelado | Character set completo del idioma en el atlas estático [ver: unity/ui-unity] |
| El save no guarda el estado del diálogo; al cargar, la conversación "olvida" | `story.state.ToJson()` (Ink) / Variable Storage propio (Yarn) dentro del save |
| Subtítulos con timing en código, retraducidos → desincronizados | Track custom: timing en el clip, texto en la tabla — independientes |
| VO con timer fijo calibrado en inglés; en español corta la frase | Avance por fin de clip o input (§12) |
| Probar la loc solo cambiando el idioma del Editor al final | Pseudo-locale + pase visual real con cada idioma en las pantallas más densas |
| Cambiar copy después del string freeze "porque es una palabrita" | El freeze es freeze: cada cambio re-abre CSV, review y VO de esa línea |

## Fuentes

- **Unity Localization package manual (1.5.12)** — docs.unity3d.com/Packages/com.unity.localization@1.5 (index, Quick Start Guide, Localization Settings, Pseudo-Localization, CSV) — la fuente primaria de string/asset tables, selectors, preload, pseudo-loc y flujo CSV/XLIFF/Google Sheets.
- **Smart Strings** — Unity Localization manual — sintaxis exacta de placeholders, formatters `plural`/`choose`, Persistent Variables, formato por locale.
- **Scripting API: LocalizedString, LocalizedTmpFont, LocalizedAudioClip, SystemLocaleSelector** — Unity Localization 1.5 API docs — nombres/base classes verificados, `StringChanged`, `Arguments`, restricción WebGL de `WaitForCompletion`.
- **ink-unity-integration README** — inkle, github.com/inkle/ink-unity-integration — instalación, ScriptedImporter, InkFile, Ink Player Window, compatibilidad (Ink 2 = Unity 2022.3+).
- **Running Your Ink (RunningYourInk.md)** — inkle, repo github.com/inkle/ink — API C# completa: Continue/canContinue, currentChoices, tags, variablesState, ObserveVariable, BindExternalFunction, state.ToJson.
- **Yarn Spinner docs (v3)** — docs.yarnspinner.dev (overview, installation-and-setup, assets-and-localization, dialogue-runner, creating-commands-functions) — componentes v3, line IDs y flujo de localización, built-in vs Unity Localization, comandos/funciones.
- **YarnSpinner-Unity README** — Secret Lab, github.com/YarnSpinnerTool/YarnSpinner-Unity — versión actual (3.2.7, jul 2026), vías de instalación, `dev.yarnspinner.unity`.
- **Timeline Scripting API: SignalEmitter** — com.unity.timeline 1.8.12 — trío SignalAsset/SignalEmitter/SignalReceiver, `emitOnce`, `retroactive`.
- **Base sintetizada:** `gamedev/narrativa-guion.md` (estructuras, branching, barks, elección de herramienta por escritor, pipeline de guion) y `unity/ui-unity.md` (TMP/atlas/fallbacks, canvas, safe area, world-space UI) — este archivo asume ambos y no los repite.
