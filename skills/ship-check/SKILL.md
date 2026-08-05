---
name: ship-check
description: >-
  Use before releasing a build to players or stores — runs the full pre-ship
  gauntlet: QA checklist, performance on target device, build settings, store
  requirements, ratings and privacy. Trigger on "vamos a publicar", "está listo
  para salir?", "prepara el release", "súbelo a la tienda".
---

# /ship-check — el guantelete antes de publicar

Corres el checklist completo pre-lanzamiento y reportas veredicto honesto: SHIP / NO SHIP con la lista exacta de bloqueantes. No maquilles: un "casi listo" es NO SHIP con lista corta.

Compatibilidad: si `${CLAUDE_PLUGIN_ROOT}` no existe, usa la raíz del repo/plugin como `EL_ESTUDIO_ROOT` y resuelve las rutas desde ahí.

## Conocimiento a cargar

1. `${CLAUDE_PLUGIN_ROOT}/knowledge/pipeline/testing-qa.md` — QA checklist y smoke tests
2. `${CLAUDE_PLUGIN_ROOT}/knowledge/unity/build-plataformas.md` — settings y requisitos por plataforma
3. `${CLAUDE_PLUGIN_ROOT}/knowledge/unity/rendimiento-unity.md` — targets de performance
4. Si va a tienda: `${CLAUDE_PLUGIN_ROOT}/knowledge/pipeline/publicacion-tiendas.md` — ratings, privacy, requisitos de consola de tienda, assets de ficha
5. Si tiene IAP/ads/analytics: `${CLAUDE_PLUGIN_ROOT}/knowledge/pipeline/sistemas-meta.md` (validación) — y cruza con las declaraciones de privacidad

## Flujo

### 1. Alcance del release
Pregunta (batcheado): ¿plataformas exactas? ¿tienda o distribución directa (itch/TestFlight/APK)? ¿primera publicación o update? Eso define qué secciones corren.

### 2. QA técnico
- Smoke test del build REAL por plataforma (no del editor): arranca, loop completo, save/load, pausa/resume, interrupciones móvil.
- Suite de tests si existe (via MCP `run_tests` o CLI) — en verde.
- Performance EN el dispositivo más débil del target: frame rate estable, memoria, thermal, batería (targets de rendimiento-unity.md).
- Device matrix mínima de testing-qa.md: aspect ratios, safe areas, idiomas activos.

### 3. Build y settings
Checklist de build-plataformas.md para cada plataforma: versión/build number incrementados, firma correcta, arquitecturas, stripping sin roturas, tamaño auditado, splash/íconos, orientaciones.

### 4. Tienda y legal (si aplica)
Checklist de publicacion-tiendas.md: rating de contenido veraz, privacy policy publicada y coherente con los SDKs reales del build, formularios de datos (Play Data Safety / App Privacy) correctos, ficha completa (screenshots, descripción, assets), track de testing antes de producción.

### 5. Veredicto
Tabla: ítem → estado (✅/❌/N/A) → evidencia (qué comando/prueba lo confirmó). Veredicto final SHIP / NO SHIP + bloqueantes ordenados por esfuerzo. Lo no verificable por el agente (p.ej. probar en un device físico que no está conectado) se lista como "requiere verificación humana" — nunca se marca ✅ sin evidencia.

## Reglas
- Evidencia o no cuenta: cada ✅ lleva el cómo se comprobó.
- El build que se prueba es el build que se publica (mismo artefacto, no "uno igual").
- Si algo falla en el guantelete, se arregla y SE REPITE el guantelete completo de esa sección — un fix puede romper otra cosa.

## Material de marketing: la regla innegociable

Todo lo que salga en tráilers, capturas o demos debe ser **material que está en el juego que vas a publicar**. No "representativo": el mismo. Enseñar algo que no existe todavía es cómo se ganan las peores reseñas de lanzamiento, y las producciones que lo hicieron (Halo Wars en E3, Dragon Age en PAX) tiraron meses de trabajo en demos que nadie volvió a usar [ver: gamedev/casos-produccion §6].

- [ ] Cada plano del tráiler existe en la build que se sube.
- [ ] Ninguna captura es de una versión con features que se cortaron.
- [ ] Si algo se ve mejor en la demo que en el juego, se arregla el juego o se cambia la demo.
