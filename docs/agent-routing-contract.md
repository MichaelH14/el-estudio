# Contrato de Orquestación

Este contrato convierte el “estudio” en un flujo verificable. El director no declara trabajo terminado sin evidencia del especialista y pase de QA.

## Estados

| Estado | Dueño | Entrada | Salida obligatoria |
|---|---|---|---|
| `idea` | director | Idea cruda | Promesa + core loop en 2-3 frases |
| `validacion` | director/disenador | Concepto comercial | `VALIDACION_MERCADO.md` o decisión explícita de omitirlo |
| `gdd` | disenador | Loop aprobado | `GDD.md` + `CORTE.md` |
| `day0` | ingeniero | GDD aprobado | Proyecto/overlay Unity + `CHECKPOINT.md` |
| `prototype` | ingeniero | Proyecto compila | Loop gris jugable |
| `assets` | artista-3d/animador | Necesidad visual | Asset medido + provenance + prefab/clips |
| `ux` | ux-ui | Flujo jugable | HUD/menú/onboarding probado |
| `qa` | qa | Entregable candidato | Evidencia o bloqueo |
| `ship` | director | QA verde | Resumen, riesgos restantes y siguiente paso |

## Evidencia mínima

- Unity: consola sin errores, test o play mode ejecutado, y ruta de escena/proyecto.
- Blender: archivo exportado, métricas de malla, escala, materiales y formato.
- Diseño: hipótesis, decisión, criterio de salida y criterio de corte.
- Mercado: competidores, canal, monetización, riesgos y experimento barato.
- Memoria: `CHECKPOINT.md` actualizado con ✅, ⚠️ y ⬜.

## Reglas de bloqueo

- Sin core loop no hay Unity.
- Sin canal plausible no hay producción comercial; solo prototipo exploratorio.
- Sin evidencia no hay ✅.
- Sin `CORTE.md` el scope no está controlado.
- Sin QA, el director no usa la palabra terminado.
