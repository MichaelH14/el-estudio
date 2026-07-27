---
name: validar-mercado
description: Use before producing a commercial, mobile or free-to-play game concept — audits market, competitors, acquisition channel, monetization fit and go/no-go evidence before Unity work starts. Trigger on "vale la pena", "mercado", "competencia", "móvil", "free-to-play", "DBD mobile", or "go/no-go".
---

# /validar-mercado — go/no-go antes de producir

Decides si una idea merece prototipo comercial. No reemplaza jugar el prototipo: bloquea ideas donde el canal, mercado o monetización hacen inviable el proyecto antes de gastar semanas.

Compatibilidad: si `${CLAUDE_PLUGIN_ROOT}` no existe, usa la raíz del repo/plugin como `EL_ESTUDIO_ROOT` y resuelve las rutas desde ahí.

## Conocimiento a cargar

1. `${CLAUDE_PLUGIN_ROOT}/knowledge/movil/mercado-movil.md` — si apunta a iOS/Android.
2. `${CLAUDE_PLUGIN_ROOT}/knowledge/movil/monetizacion-movil.md` — si hay F2P, ads, IAP o live-ops.
3. `${CLAUDE_PLUGIN_ROOT}/knowledge/gamedev/psicologia-retencion-negocio.md` — LTV/CPI, ética, retención y modelos.
4. `${CLAUDE_PLUGIN_ROOT}/knowledge/gamedev/generos.md` — encaje por género y expectativas de audiencia.
5. `templates/market-validation/VALIDACION_MERCADO.md` — formato de salida.

## Etapas

### 1. Tesis de mercado

- Define plataforma, audiencia, género, promesa jugable y por qué ahora.
- Identifica el hueco específico: no basta "dejaron mercado"; debe existir demanda alcanzable.
- Salida: hipótesis falsable en 3 frases.

### 2. Competencia y sustitutos

- Lista 5-10 competidores directos y sustitutos cercanos.
- Para cada uno: plataforma, monetización, señal de demanda, review pain, diferenciación posible.
- Si no hay competidores, no asumas oportunidad: puede significar que el mercado no existe.

### 3. Canal de adquisición

- Define cómo llega el jugador: orgánico, comunidad, creators, ASO, paid UA, publisher.
- Si depende de paid UA, exige hipótesis de LTV > CPI y presupuesto de test.
- Para indie sin capital, prioriza nicho, comunidad y hook viral medible.

### 4. Encaje de producto

- Valida si el loop cabe en la plataforma: sesión, controles, interrupciones, social, contenido.
- Verifica que monetización no destruya el diseño.
- Define el MVP mínimo que prueba demanda, no solo tecnología.

### 5. Go/no-go

- Usa tres estados: `GO`, `PIVOT`, `NO-GO`.
- `GO` requiere canal plausible, diferenciación clara y MVP medible.
- `PIVOT` requiere cambio concreto de plataforma, audiencia, scope o monetización.
- `NO-GO` se declara si la única esperanza es "que se vuelva viral" sin mecanismo.

## Reglas

- No cites números actuales sin fuente reciente. Si el dato puede cambiar, verifica antes.
- No confundas vacante con mercado: un juego retirado deja usuarios solo si todavía hay deseo, comunidad y canal.
- La salida siempre incluye riesgos mortales, kill criteria y el experimento más barato.
