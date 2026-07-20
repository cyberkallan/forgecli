"""Utility helpers for {{PROJECT_NAME}}."""
from __future__ import annotations

import os
import platform
import shutil
import socket
import subprocess
from dataclasses import asdict, dataclass
from typing import Dict


@dataclass
class SystemInfo:
    python_version: str = ""
    terminal_size: str = ""
    current_dir: str = ""
    network_status: str = "unknown"
    git_status: str = ""

    def as_dict(self) -> Dict[str, str]:
        return asdict(self)


def _check_network(timeout: float = 1.5) -> str:
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("1.1.1.1", 53))
        return "online"
    except OSError:
        return "offline"


def _terminal_size() -> str:
    try:
        size = shutil.get_terminal_size((80, 24))
        return f"{size.columns}x{size.lines}"
    except (OSError, ValueError):
        return "unknown"


def _check_git_status(cwd: str) -> str:
    if not shutil.which("git"):
        return "git not installed"
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=cwd, capture_output=True, text=True, check=False, timeout=2,
        )
        if result.returncode != 0:
            return "not a git repo"
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd, capture_output=True, text=True, check=False, timeout=2,
        )
        status = subprocess.run(
            ["git", "status", "--short"],
            cwd=cwd, capture_output=True, text=True, check=False, timeout=2,
        )
        return f"on {(branch.stdout or 'main').strip()}{' (dirty)' if (status.stdout or '').strip() else ''}"
    except (subprocess.TimeoutExpired, OSError) as exc:
        return f"git error: {exc.__class__.__name__}"


def collect_system_info() -> SystemInfo:
    cwd = os.getcwd()
    size = shutil.get_terminal_size((80, 24))
    return SystemInfo(
        python_version=platform.python_version(),
        terminal_size=f"{size.columns}x{size.lines}",
        current_dir=cwd,
        network_status=_check_network(),
        git_status=_check_git_status(cwd),
    )


def slugify(value: str, fallback: str = "tool") -> str:
    import re
    cleaned = re.sub(r"[^a-z0-9_]+", "_", (value or "").lower()).strip("_")
    return cleaned or fallback
