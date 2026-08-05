#!/usr/bin/env python3
"""Create the El Estudio day-0 overlay for a Unity game project."""

from __future__ import annotations

import argparse
import datetime as datetime_module
import json
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TEST_FRAMEWORK_PACKAGE = "com.unity.test-framework"
EDITOR_GLOBS = [
    "/Applications/Unity/Hub/Editor/*/Unity.app/Contents/Resources/PackageManager/BuiltInPackages",
    "/Applications/Unity/Unity.app/Contents/Resources/PackageManager/BuiltInPackages",
]
UNITY_TEMPLATE_ROOT = REPO_ROOT / "templates" / "unity-day0"
MEMORY_TEMPLATE_ROOT = REPO_ROOT / "templates" / "game-memory"
EXTRA_TEMPLATE_FILES = [
    REPO_ROOT / "templates" / "asset-provenance" / "ASSET_PROVENANCE.md",
    REPO_ROOT / "templates" / "analytics" / "ANALYTICS_TAXONOMY.md",
    REPO_ROOT / "templates" / "scope-peelable" / "SCOPE.md",
]


def render_template(text: str, game_name: str) -> str:
    today = datetime_module.date.today().isoformat()
    return text.replace("{{GAME_NAME}}", game_name).replace("{{DATE}}", today)


def copy_template_file(source_path: Path, destination_path: Path, game_name: str, force: bool) -> bool:
    if destination_path.exists() and not force:
        return False

    destination_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        text = source_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        shutil.copy2(source_path, destination_path)
        return True

    destination_path.write_text(render_template(text, game_name), encoding="utf-8")
    return True


def copy_tree(source_root: Path, destination_root: Path, game_name: str, force: bool) -> tuple[int, int]:
    copied_count = 0
    skipped_count = 0
    for source_path in sorted(source_root.rglob("*")):
        if source_path.is_dir():
            continue
        destination_path = destination_root / source_path.relative_to(source_root)
        copied = copy_template_file(source_path, destination_path, game_name, force)
        if copied:
            copied_count += 1
        else:
            skipped_count += 1
    return copied_count, skipped_count


def scaffold(destination_root: Path, game_name: str, force: bool) -> tuple[int, int]:
    destination_root.mkdir(parents=True, exist_ok=True)
    copied_count, skipped_count = copy_tree(UNITY_TEMPLATE_ROOT, destination_root, game_name, force)
    memory_copied, memory_skipped = copy_tree(MEMORY_TEMPLATE_ROOT, destination_root, game_name, force)
    copied_count += memory_copied
    skipped_count += memory_skipped

    docs_root = destination_root / "Docs"
    for source_path in EXTRA_TEMPLATE_FILES:
        destination_path = docs_root / source_path.name
        copied = copy_template_file(source_path, destination_path, game_name, force)
        if copied:
            copied_count += 1
        else:
            skipped_count += 1

    return copied_count, skipped_count


def detect_test_framework_version() -> str | None:
    """Version del test framework que trae el editor instalado. None si no hay editor."""
    versions: list[str] = []
    for pattern in EDITOR_GLOBS:
        root = Path(pattern.split("*")[0])
        if not root.exists():
            continue
        for manifest_path in root.glob(pattern[len(str(root)) + 1:] + f"/{TEST_FRAMEWORK_PACKAGE}/package.json"):
            try:
                versions.append(json.loads(manifest_path.read_text(encoding="utf-8"))["version"])
            except (ValueError, KeyError, OSError):
                continue
    return sorted(versions)[-1] if versions else None


def ensure_test_framework(destination_root: Path) -> str:
    """El smoke test EditMode necesita com.unity.test-framework; sin el, los scripts no compilan."""
    manifest_path = destination_root / "Packages" / "manifest.json"
    if not manifest_path.exists():
        return "manifest.json ausente (carpeta vacia): anade com.unity.test-framework al crear el proyecto Unity."

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except ValueError:
        return "manifest.json ilegible: revisa com.unity.test-framework a mano."

    dependencies = manifest.setdefault("dependencies", {})
    if TEST_FRAMEWORK_PACKAGE in dependencies:
        return f"{TEST_FRAMEWORK_PACKAGE} ya presente ({dependencies[TEST_FRAMEWORK_PACKAGE]})."

    version = detect_test_framework_version()
    if version is None:
        return f"No se detecto ningun editor Unity: anade {TEST_FRAMEWORK_PACKAGE} a Packages/manifest.json a mano."

    dependencies[TEST_FRAMEWORK_PACKAGE] = version
    manifest["dependencies"] = dict(sorted(dependencies.items()))
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return f"{TEST_FRAMEWORK_PACKAGE} {version} anadido a Packages/manifest.json."


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path, help="Unity project folder or empty destination folder.")
    parser.add_argument("--game-name", required=True, help="Human-readable game name.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing scaffold files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    destination_root = args.destination.expanduser().resolve()
    copied_count, skipped_count = scaffold(destination_root, args.game_name, args.force)
    print(f"Scaffold: {destination_root}")
    print(f"Copied: {copied_count}")
    print(f"Skipped: {skipped_count}")
    print(f"Test framework: {ensure_test_framework(destination_root)}")
    print("Next: open in Unity, run Day0SmokeTest, then update CHECKPOINT.md with evidence.")
    print("Iteracion rapida: menu 'El Estudio' en el editor (arranque desde escena inicial, velocidad, reset de progreso).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
