"""Preview mode: run the generated tool with hot-reload support."""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

from rich.console import Console

from .core.logging_utils import get_logger
from .models import GeneratedProject

_LOG = get_logger("preview")


def launch(project: GeneratedProject, console: Console, theme,
           *, args: Optional[list] = None, interactive: bool = True,
           timeout: Optional[float] = None) -> int:
    """Launch the generated tool inside its own folder."""
    cmd = [sys.executable, "main.py"] + (args or [])
    cwd = str(project.root)
    env = os.environ.copy()
    env["PYTHONPATH"] = cwd
    try:
        if interactive:
            result = subprocess.run(cmd, cwd=cwd, env=env, check=False, timeout=timeout)
            return result.returncode
        result = subprocess.run(cmd, cwd=cwd, env=env, check=False,
                                timeout=timeout, capture_output=True, text=True)
        console.print(result.stdout)
        if result.stderr:
            console.print(f"[{theme.warning}]stderr:[/] {result.stderr}")
        return result.returncode
    except subprocess.TimeoutExpired:
        console.print(f"[{theme.warning}]Preview timed out after {timeout}s.[/]")
        return -1
    except FileNotFoundError as exc:
        console.print(f"[{theme.danger}]Launch failed: {exc}[/]")
        return -1


def watch(project: GeneratedProject, console: Console, theme,
          *, interval: float = 1.0) -> None:
    """Hot-reload loop: re-launch whenever files change."""
    cwd = Path(project.root)
    last_signature = _signature(cwd)
    try:
        while True:
            time.sleep(interval)
            new_signature = _signature(cwd)
            if new_signature != last_signature:
                console.print(f"[{theme.info}]Change detected. Re-launching preview ...[/]")
                launch(project, console, theme, interactive=False, timeout=10)
                last_signature = new_signature
    except KeyboardInterrupt:
        console.print(f"[{theme.muted}]Stopped watching.[/]")


def _signature(cwd: Path) -> dict:
    sig = {}
    for path in cwd.rglob("*.py"):
        try:
            sig[str(path)] = path.stat().st_mtime
        except OSError:
            continue
    return sig


__all__ = ["launch", "watch"]