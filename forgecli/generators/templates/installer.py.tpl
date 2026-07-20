"""Dependency installer for {{PROJECT_NAME}}."""
from __future__ import annotations

import subprocess
import sys
from typing import Iterable, List


def ensure_runtime_dependencies(packages: Iterable[str]) -> List[str]:
    """Install missing runtime dependencies. Returns the list installed now."""
    installed: List[str] = []
    for pkg in packages:
        module = pkg.split(">=")[0].split("==")[0].replace("-", "_")
        try:
            __import__(module)
            continue
        except ImportError:
            pass
        cmd = [sys.executable, "-m", "pip", "install", "--quiet", "--disable-pip-version-check",
               pkg, "--no-warn-script-location"]
        try:
            subprocess.run(cmd, check=True)
            installed.append(pkg)
        except subprocess.CalledProcessError:
            pass
    return installed


if __name__ == "__main__":
    raise SystemExit(0 if not ensure_runtime_dependencies(["rich", "pyfiglet", "questionary"]) else 0)
