# Frescura de Fuentes

El conocimiento de videojuegos mezcla principios estables con datos que caducan. Esta política evita que el agente use números viejos como si fueran actuales.

## Clasificación

| Tipo | Ejemplos | Revisión |
|---|---|---|
| Estable | MDA, 12 principios, topología, core loop | 24 meses |
| Semi-estable | Unity APIs, Blender APIs, paquetes, pipelines | 6 meses |
| Volátil | stores, IAP, ads, privacidad, target SDK, mercado móvil | 90 días |
| Crítico | leyes, políticas de tienda, precios, requisitos de publicación | verificar en la sesión |

## Metadata recomendada por archivo

```yaml
freshness:
  last_verified: 2026-07-27
  review_after: 2026-10-27
  volatility: volatile
  primary_sources:
    - https://example.com/source
```

## Regla operativa

- Si el archivo habla de reglas de Apple/Google, paquetes Unity, monetización, benchmarks o mercado actual, el agente debe verificar antes de decidir.
- Si una fuente no pudo verificarse, el archivo debe marcarlo en `Fuentes`, no ocultarlo.
- `tools/validate_repo.py` no falla todavía por metadata ausente, pero debe usarse para detectar estructura rota mientras esta política se adopta gradualmente.
