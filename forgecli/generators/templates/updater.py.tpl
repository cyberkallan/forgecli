"""Update checker for {{PROJECT_NAME}}.

Queries PyPI for the latest version and compares against the local version.
Designed to never crash the calling tool: every network/parse error is
swallowed and logged to stderr only.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Optional

from rich.console import Console


def _pypi_latest(package: str) -> Optional[str]:
    """Return the latest version string from PyPI, or None on any failure."""
    url = f"https://pypi.org/pypi/{package}/json"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read())
        return data.get("info", {}).get("version")
    except (urllib.error.URLError, json.JSONDecodeError, OSError):
        return None


def check_for_update(project_name: str, current_version: str,
                     console: Console, theme, *, force: bool = False) -> Optional[str]:
    """Check PyPI for an update. Returns the latest version if newer."""
    latest = _pypi_latest(project_name.lower().replace(" ", "").replace("-", "_"))
    if latest is None:
        if force:
            console.print(f"[{theme.warning}]Could not reach PyPI to check updates.[/]")
        return None
    def _parse(v: str) -> tuple:
        return tuple(int(p) if p.isdigit() else 0 for p in v.replace("-", ".").split("."))
    if _parse(latest) > _parse(current_version):
        console.print(f"[{theme.warning}]Update available:[/] {current_version} -> {latest}")
        console.print(f"[{theme.info}]Run: pip install --upgrade {project_name.lower().replace(' ', '')}[/]")
    elif force:
        console.print(f"[{theme.success}]You are on the latest version ({current_version}).[/]")
    return latest
