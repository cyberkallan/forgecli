"""Self-update for ForgeCLI via pip."""
from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass

import urllib.error
import urllib.request
import json

from . import __version__


@dataclass
class UpdateInfo:
    current: str
    latest: str
    available: bool


def _latest_pypi_version(package: str = "forgecli") -> str | None:
    try:
        with urllib.request.urlopen(f"https://pypi.org/pypi/{package}/json", timeout=5) as r:
            return json.loads(r.read())["info"]["version"]
    except (urllib.error.URLError, json.JSONDecodeError, OSError):
        return None


def _parse(v: str) -> tuple:
    return tuple(int(p) if p.isdigit() else 0 for p in v.replace("-", ".").split("."))


def check_update() -> UpdateInfo:
    latest = _latest_pypi_version()
    return UpdateInfo(current=__version__, latest=latest or "unknown",
                      available=bool(latest and _parse(latest) > _parse(__version__)))


def apply_update() -> tuple[bool, str]:
    """Run ``pip install -U forgecli`` and capture the result."""
    proc = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "forgecli",
         "--disable-pip-version-check", "--no-warn-script-location"],
        capture_output=True, text=True, check=False,
    )
    return proc.returncode == 0, (proc.stdout + "\n" + proc.stderr).strip()


__all__ = ["check_update", "apply_update", "UpdateInfo"]