# Compatibilidad con Codex

El Estudio nació como plugin de Claude Code, pero el conocimiento y las skills son portables. Para operar en Codex:

## Contrato de rutas

- `EL_ESTUDIO_ROOT` = raíz del repo/plugin.
- Cualquier `${CLAUDE_PLUGIN_ROOT}` en una skill se resuelve como `EL_ESTUDIO_ROOT`.
- Los archivos de `knowledge/` siempre se cargan por índice primero: `knowledge/<base>/INDEX.md`.

## Componentes soportados

- `.codex-plugin/plugin.json` declara metadata, skills y presentación.
- `AGENTS.md` da instrucciones nativas a Codex cuando se trabaja dentro del repo.
- `skills/*/SKILL.md` mantiene formato portable de skill con frontmatter.
- `tools/validate_repo.py` evita que Claude/Codex diverjan en conteos y contratos.

## Limitaciones actuales

- Los agentes de `agents/*.md` son documentos operativos; Codex puede leerlos, pero no los convierte automáticamente en subagentes instalados.
- Unity MCP y Blender MCP dependen del entorno local. Usa `tools/doctor.py` antes de prometer operación directa del editor.
- Los comandos slash de Claude no son equivalentes 1:1 a la UX de Codex; en Codex se invocan por intención o por nombre de skill.

## Regla práctica

Si una instrucción depende de una capacidad específica de Claude Code, no la borres: añade una alternativa Codex al lado. El objetivo es portabilidad sin romper el flujo original.
