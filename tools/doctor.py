#!/usr/bin/env python3
"""Report local tooling readiness for El Estudio workflows."""

from __future__ import annotations

import argparse
import json
import shutil
import socket
import subprocess
from pathlib import Path
from typing import Any


COMMON_UNITY_ROOTS = [
    Path("/Applications/Unity/Hub/Editor"),
    Path.home() / "Applications" / "Unity" / "Hub" / "Editor",
]
COMMON_BLENDER_PATHS = [
    Path("/Applications/Blender.app/Contents/MacOS/Blender"),
    Path("/opt/homebrew/bin/blender"),
    Path("/usr/local/bin/blender"),
]
MCP_PORTS = {
    "unity_mcp_6400": 6400,
    "unity_mcp_6401": 6401,
    "blender_mcp_9876": 9876,
}


def command_version(command: str) -> dict[str, Any]:
    executable = shutil.which(command)
    if not executable:
        return {"ok": False, "path": None, "version": None}
    try:
        completed = subprocess.run(
            [executable, "--version"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=5,
            check=False,
        )
        version = completed.stdout.strip().splitlines()[0] if completed.stdout.strip() else "unknown"
    except Exception as exc:  # pragma: no cover - diagnostic best effort
        version = f"error: {exc}"
    return {"ok": True, "path": executable, "version": version}


def find_unity_editors() -> list[str]:
    editor_paths: list[str] = []
    for unity_root in COMMON_UNITY_ROOTS:
        if not unity_root.exists():
            continue
        for unity_binary in sorted(unity_root.glob("*/Unity.app/Contents/MacOS/Unity")):
            editor_paths.append(str(unity_binary))
    direct_binary = shutil.which("Unity")
    if direct_binary and direct_binary not in editor_paths:
        editor_paths.append(direct_binary)
    return editor_paths


def find_blender() -> dict[str, Any]:
    blender_from_path = shutil.which("blender")
    candidates = [Path(blender_from_path)] if blender_from_path else []
    candidates.extend(COMMON_BLENDER_PATHS)
    for candidate_path in candidates:
        if candidate_path.exists():
            return {"ok": True, "path": str(candidate_path)}
    return {"ok": False, "path": None}


def port_open(port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.3):
            return True
    except OSError:
        return False


def collect_report() -> dict[str, Any]:
    return {
        "commands": {
            "git": command_version("git"),
            "gh": command_version("gh"),
            "python3": command_version("python3"),
        },
        "unity": {
            "ok": bool(find_unity_editors()),
            "editors": find_unity_editors(),
        },
        "blender": find_blender(),
        "mcp_ports": {
            name: {"port": port, "open": port_open(port)}
            for name, port in MCP_PORTS.items()
        },
    }


def print_text_report(report: dict[str, Any]) -> None:
    print("El Estudio doctor")
    print("")
    for command_name, command_report in report["commands"].items():
        status = "ok" if command_report["ok"] else "missing"
        print(f"- {command_name}: {status} ({command_report['path'] or 'not found'})")
    print(f"- Unity editors: {len(report['unity']['editors'])}")
    for editor_path in report["unity"]["editors"]:
        print(f"  - {editor_path}")
    blender_status = "ok" if report["blender"]["ok"] else "missing"
    print(f"- Blender: {blender_status} ({report['blender']['path'] or 'not found'})")
    for port_name, port_report in report["mcp_ports"].items():
        status = "open" if port_report["open"] else "closed"
        print(f"- {port_name}: {status} ({port_report['port']})")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print JSON report.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = collect_report()
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_text_report(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
