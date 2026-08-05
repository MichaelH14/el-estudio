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

## Qué cuenta como "terminado"

Heredado de producciones reales [ver: gamedev/casos-produccion]:

- Una feature **al 90% no está terminada**. Diez features al 90% son cero features entregadas.
- "Funciona en prototipo" es un estado distinto de "terminado": faltan efectos, sonido, animación, UI y casos borde. Presupuesta **días para el prototipo, meses para completarlo**.
- Antes de abrir una capa nueva de alcance, la anterior tiene que estar cerrada y probada (`Docs/SCOPE.md`).
- La diversión también se cierra con evidencia: una serie de `/medir-diversion` que sube, no la opinión del que lo hizo.

## Reglas de bloqueo

- Sin core loop no hay Unity.
- Sin canal plausible no hay producción comercial; solo prototipo exploratorio.
- Sin evidencia no hay ✅.
- Sin `CORTE.md` el scope no está controlado.
- Sin QA, el director no usa la palabra terminado.
- Sin material real, no hay demo pública: solo se enseña lo que va a shipear.
- Si el bucle cambio→verlo se mide en minutos, se arregla antes de seguir produciendo.
