# Analytics Taxonomy

## Principios

- Instrumentar antes del soft launch.
- Medir comportamiento, no vanidad.
- No enviar datos personales innecesarios.
- Respetar consentimiento por región y tienda.

## Eventos Mínimos

| Evento | Cuándo | Parámetros |
|---|---|---|
| `session_start` | Inicio de sesión | version, platform, locale |
| `tutorial_step` | Paso de onboarding | step_id, result |
| `level_start` | Inicio de partida/nivel | level_id, mode |
| `level_complete` | Victoria | level_id, duration, retries |
| `level_fail` | Derrota | level_id, reason, duration |
| `currency_gain` | Gana moneda | currency, amount, source |
| `currency_spend` | Gasta moneda | currency, amount, sink |
| `ad_rewarded_offer` | Se muestra opción rewarded | placement |
| `ad_rewarded_complete` | Rewarded completado | placement, reward |
| `iap_start` | Intenta compra | product_id |
| `iap_complete` | Compra confirmada | product_id, price_localized |
| `crash_marker` | Marcador previo a zona riesgosa | system, scene |

## Métricas Go/No-Go

- D1/D7/D30 retention.
- Session length.
- Crash-free rate.
- Tutorial completion.
- First meaningful action.
- LTV estimado contra CPI real si hay paid UA.
