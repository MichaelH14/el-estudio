# Tooling

## Validación del plugin

```bash
python3 tools/validate_repo.py
```

Valida:

- Conteos de knowledge, agentes y skills contra README/manifests.
- `INDEX.md` por cada base de conocimiento.
- Contrato mínimo de cada archivo de conocimiento.
- Frontmatter de cada skill.
- Links Markdown locales.
- Referencias `[ver: ...]` resolubles cuando tienen formato estructurado.

## Doctor local

```bash
python3 tools/doctor.py
python3 tools/doctor.py --json
```

Detecta GitHub CLI, Blender, Unity y puertos MCP comunes. No instala nada: reporta el estado real para no prometer capacidades inexistentes.

## Scaffold Unity día 0

```bash
python3 tools/scaffold_unity_day0.py ../MiJuego --game-name "Mi Juego"
```

Crea memoria viva, archivos Git/LFS y smoke test base. Es un overlay seguro: puede aplicarse sobre una carpeta vacía o sobre un proyecto Unity ya creado.
