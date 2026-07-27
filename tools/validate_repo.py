#!/usr/bin/env python3
"""Validate El Estudio repository structure and plugin contracts."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_ROOT = REPO_ROOT / "knowledge"
SKILLS_ROOT = REPO_ROOT / "skills"
AGENTS_ROOT = REPO_ROOT / "agents"
README_PATH = REPO_ROOT / "README.md"
CLAUDE_PLUGIN_PATH = REPO_ROOT / ".claude-plugin" / "plugin.json"
CLAUDE_MARKETPLACE_PATH = REPO_ROOT / ".claude-plugin" / "marketplace.json"
CODEX_PLUGIN_PATH = REPO_ROOT / ".codex-plugin" / "plugin.json"


@dataclass
class ValidationResult:
    errors: list[str]
    warnings: list[str]

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warning(self, message: str) -> None:
        self.warnings.append(message)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def skill_dirs() -> list[Path]:
    return sorted(path.parent for path in SKILLS_ROOT.glob("*/SKILL.md"))


def agent_files() -> list[Path]:
    return sorted(AGENTS_ROOT.glob("*.md"))


def knowledge_dirs() -> list[Path]:
    return sorted(path for path in KNOWLEDGE_ROOT.iterdir() if path.is_dir())


def knowledge_content_files() -> list[Path]:
    return sorted(path for path in KNOWLEDGE_ROOT.rglob("*.md") if path.name != "INDEX.md")


def load_json(path: Path, result: ValidationResult) -> dict:
    try:
        return json.loads(read_text(path))
    except Exception as exc:
        result.error(f"{relative(path)} is not valid JSON: {exc}")
        return {}


def check_counts(result: ValidationResult) -> None:
    skill_count = len(skill_dirs())
    agent_count = len(agent_files())
    content_count = len(knowledge_content_files())
    base_count = len(knowledge_dirs())
    readme = read_text(README_PATH)

    expected_fragments = [
        (README_PATH, f"{content_count} archivos de conocimiento"),
        (README_PATH, f"{base_count} bases"),
        (README_PATH, f"{agent_count} agentes"),
        (README_PATH, f"{skill_count} skills"),
    ]

    for manifest_path in [CLAUDE_PLUGIN_PATH, CLAUDE_MARKETPLACE_PATH]:
        expected_fragments.extend(
            [
                (manifest_path, f"{agent_count} agentes"),
                (manifest_path, f"{skill_count} skills"),
            ]
        )

    codex_text = read_text(CODEX_PLUGIN_PATH)
    if "Codex" not in codex_text:
        result.error(f"{relative(CODEX_PLUGIN_PATH)} should explicitly mention Codex")

    for path, fragment in expected_fragments:
        target_text = readme if path == README_PATH else read_text(path)
        if fragment not in target_text:
            result.error(f"{relative(path)} missing expected fragment: {fragment}")


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end_index = text.find("\n---", 4)
    if end_index == -1:
        return {}

    frontmatter = text[4:end_index]
    data: dict[str, str] = {}
    current_key: str | None = None
    for raw_line in frontmatter.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue
        if line.startswith(" ") and current_key:
            data[current_key] = f"{data[current_key]}\n{line.strip()}"
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            current_key = key.strip()
            data[current_key] = value.strip().strip('"')
    return data


def check_skills(result: ValidationResult) -> None:
    director_text = read_text(AGENTS_ROOT / "director.md")
    for skill_dir in skill_dirs():
        skill_path = skill_dir / "SKILL.md"
        text = read_text(skill_path)
        frontmatter = parse_frontmatter(text)
        skill_name = skill_dir.name
        if frontmatter.get("name") != skill_name:
            result.error(f"{relative(skill_path)} frontmatter name must be {skill_name}")
        if not frontmatter.get("description"):
            result.error(f"{relative(skill_path)} missing description")
        if f"/{skill_name}" not in director_text:
            result.error(f"agents/director.md does not route /{skill_name}")


def check_knowledge_contract(result: ValidationResult) -> None:
    for base_dir in knowledge_dirs():
        index_path = base_dir / "INDEX.md"
        if not index_path.exists():
            result.error(f"{relative(base_dir)} missing INDEX.md")

    for knowledge_path in knowledge_content_files():
        if knowledge_path.name == "recursos-libres.md":
            continue
        text = read_text(knowledge_path)
        required_fragments = [
            ("Cuando cargar este archivo", "Cuándo cargar este archivo"),
            ("Reglas prácticas", "Reglas practicas"),
            ("Errores comunes",),
            ("Fuentes",),
        ]
        for alternatives in required_fragments:
            if not any(fragment in text for fragment in alternatives):
                result.error(f"{relative(knowledge_path)} missing section: {' / '.join(alternatives)}")


def check_markdown_links(result: ValidationResult) -> None:
    markdown_link_pattern = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
    for markdown_path in sorted(REPO_ROOT.rglob("*.md")):
        if ".git" in markdown_path.parts:
            continue
        for match in markdown_link_pattern.finditer(read_text(markdown_path)):
            href = match.group(1).strip()
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", href) or href.startswith("#"):
                continue
            target = href.split("#", 1)[0]
            if not target:
                continue
            relative_target = (markdown_path.parent / target).resolve()
            root_target = (REPO_ROOT / target).resolve()
            if not relative_target.exists() and not root_target.exists():
                result.error(f"{relative(markdown_path)} has broken link: {href}")


def known_knowledge_slugs() -> set[str]:
    slugs: set[str] = set()
    for knowledge_path in KNOWLEDGE_ROOT.rglob("*.md"):
        slug = knowledge_path.relative_to(KNOWLEDGE_ROOT).with_suffix("").as_posix()
        slugs.add(slug)
    return slugs


def clean_ver_reference(reference: str) -> str | None:
    cleaned = reference.strip().replace(".md", "")
    cleaned = cleaned.split(" §", 1)[0].strip()
    if not cleaned or cleaned.startswith("§") or cleaned in {"...", "slug"}:
        return None
    if cleaned == "base/slug" or cleaned.endswith("/slug"):
        return None
    if " " in cleaned:
        return None
    if not re.match(r"^[a-z0-9_/.-]+$", cleaned):
        return None
    return cleaned


def check_ver_references(result: ValidationResult) -> None:
    slugs = known_knowledge_slugs()
    reference_pattern = re.compile(r"\[ver: ([^\]]+)\]")
    unresolved: list[str] = []
    ambiguous_count = 0

    for markdown_path in sorted(REPO_ROOT.rglob("*.md")):
        if ".git" in markdown_path.parts:
            continue
        text = read_text(markdown_path)
        same_base = None
        if KNOWLEDGE_ROOT in markdown_path.parents:
            same_base = markdown_path.parent.relative_to(KNOWLEDGE_ROOT).as_posix()
        for match in reference_pattern.finditer(text):
            raw_reference = match.group(1)
            parts = re.split(r"[,;·]", raw_reference)
            for raw_part in parts:
                cleaned = clean_ver_reference(raw_part)
                if cleaned is None:
                    ambiguous_count += 1
                    continue
                candidates = [cleaned]
                if same_base and "/" not in cleaned:
                    candidates.append(f"{same_base}/{cleaned}")
                if not any(candidate in slugs for candidate in candidates):
                    unresolved.append(f"{relative(markdown_path)} -> [ver: {raw_part.strip()}]")

    if unresolved:
        for item in unresolved[:25]:
            result.warning(f"unresolved structured reference: {item}")
        if len(unresolved) > 25:
            result.warning(f"{len(unresolved) - 25} more unresolved structured references")
    if ambiguous_count:
        result.warning(f"{ambiguous_count} [ver:] fragments are prose/section references and were skipped")


def check_plugin_manifests(result: ValidationResult) -> None:
    manifests: list[tuple[Path, dict]] = []
    for manifest_path in [CLAUDE_PLUGIN_PATH, CLAUDE_MARKETPLACE_PATH, CODEX_PLUGIN_PATH]:
        if not manifest_path.exists():
            result.error(f"missing {relative(manifest_path)}")
            continue
        manifests.append((manifest_path, load_json(manifest_path, result)))

    codex_manifest = load_json(CODEX_PLUGIN_PATH, result)
    if codex_manifest:
        for required_key in ["name", "version", "description", "author", "interface"]:
            if required_key not in codex_manifest:
                result.error(f"{relative(CODEX_PLUGIN_PATH)} missing {required_key}")
        interface = codex_manifest.get("interface", {})
        required_interface_keys = [
            "displayName",
            "shortDescription",
            "longDescription",
            "developerName",
            "category",
            "capabilities",
        ]
        for required_key in required_interface_keys:
            if required_key not in interface:
                result.error(f"{relative(CODEX_PLUGIN_PATH)} missing interface.{required_key}")

    versions: set[str] = set()
    for manifest_path, manifest in manifests:
        if manifest_path == CLAUDE_MARKETPLACE_PATH:
            plugins = manifest.get("plugins", [])
            if plugins:
                versions.add(str(plugins[0].get("version", "")))
            continue
        versions.add(str(manifest.get("version", "")))
    if len(versions) != 1:
        result.error(f"plugin versions differ: {sorted(versions)}")
    else:
        version = next(iter(versions))
        if f"v{version}" not in read_text(README_PATH):
            result.error(f"README.md missing current version v{version}")


def run_validation() -> ValidationResult:
    result = ValidationResult(errors=[], warnings=[])
    check_plugin_manifests(result)
    check_counts(result)
    check_skills(result)
    check_knowledge_contract(result)
    check_markdown_links(result)
    check_ver_references(result)
    return result


def main() -> int:
    result = run_validation()
    for warning in result.warnings:
        print(f"warning: {warning}")
    for error in result.errors:
        print(f"error: {error}")

    if result.errors:
        print(f"FAILED: {len(result.errors)} error(s), {len(result.warnings)} warning(s)")
        return 1

    print(f"OK: 0 errors, {len(result.warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
