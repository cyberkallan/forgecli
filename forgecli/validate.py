"""Headless validation of a generated project."""
from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from .core.logging_utils import get_logger

_LOG = get_logger("validate")


@dataclass
class ValidationReport:
    path: Path
    ok: bool = True
    checks: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def add(self, msg: str) -> None:
        self.checks.append(msg)

    def fail(self, msg: str) -> None:
        self.ok = False
        self.errors.append(msg)


REQUIRED_FILES = [
    "main.py", "banner.py", "ui.py", "utils.py", "theme.py",
    "installer.py", "updater.py", "commands.py", "config.json",
    "theme.json", "requirements.txt", "README.md", "LICENSE",
    "pyproject.toml", ".gitignore",
]


def validate_project(path: Path) -> ValidationReport:
    """Run a headless import + smoke check on a generated project."""
    report = ValidationReport(path=Path(path))

    if not report.path.is_dir():
        report.fail(f"Not a directory: {report.path}")
        return report

    for rel in REQUIRED_FILES:
        if (report.path / rel).exists():
            report.add(f"present: {rel}")
        else:
            report.fail(f"missing required file: {rel}")

    # Validate JSON config files parse.
    for rel in ("config.json", "theme.json", "settings.json"):
        fp = report.path / rel
        if fp.exists():
            try:
                json.loads(fp.read_text(encoding="utf-8"))
                report.add(f"valid JSON: {rel}")
            except json.JSONDecodeError as exc:
                report.fail(f"invalid JSON {rel}: {exc}")
        elif rel != "settings.json":
            # settings.json is optional
            pass

    # Byte-compile every Python source.
    proc = subprocess.run(
        [sys.executable, "-m", "compileall", "-q", str(report.path)],
        capture_output=True, text=True, check=False,
    )
    if proc.returncode != 0:
        report.fail("compileall reported errors")
        for line in proc.stderr.splitlines()[:5]:
            report.fail(line)
    else:
        report.add("all .py sources compile")

    # Headless import of the generated tool's modules.
    proc = subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.path.insert(0, '.'); "
         "import main, banner, ui, utils, theme, installer, updater, commands; "
         "print('import-ok')"],
        cwd=str(report.path), capture_output=True, text=True, check=False,
    )
    if proc.returncode == 0 and "import-ok" in proc.stdout:
        report.add("headless module import OK")
    else:
        report.fail("headless import failed")
        for line in (proc.stderr or proc.stdout).splitlines()[:5]:
            report.fail(line)

    return report


__all__ = ["validate_project", "ValidationReport"]