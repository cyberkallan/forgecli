"""Export generated projects in multiple formats."""
from __future__ import annotations

import os
import shutil
import subprocess
import tarfile
import zipfile
from pathlib import Path
from typing import Optional

from .core.logging_utils import get_logger
from .models import GeneratedProject

_LOG = get_logger("exporter")

EXPORT_FORMATS = [
    "Zip (.zip)",
    "Tarball (.tar.gz)",
    "Standalone Folder",
    "GitHub Ready",
    "Termux Ready",
    "Linux Ready",
    "Docker Project",
    "Git Repository",
]


def _ensure_export_dir(base: Optional[Path]) -> Path:
    target = Path(base or Path.cwd()) / "exports"
    target.mkdir(parents=True, exist_ok=True)
    return target


def _ignore_pycache(path: str, names) -> list[str]:
    return [n for n in names if n == "__pycache__"]


def export_project(project: GeneratedProject, fmt: str,
                   export_dir: Optional[Path] = None) -> Path:
    """Export ``project`` in the requested ``fmt``. Returns the resulting path."""
    root = Path(project.root)
    name = root.name
    out_dir = _ensure_export_dir(export_dir)
    fmt = fmt

    if fmt == "Zip (.zip)":
        target = out_dir / f"{name}.zip"
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
            for fp in root.rglob("*"):
                if fp.is_file() and "__pycache__" not in fp.parts:
                    zf.write(fp, fp.relative_to(root.parent))
        return target

    if fmt == "Tarball (.tar.gz)":
        target = out_dir / f"{name}.tar.gz"
        with tarfile.open(target, "w:gz") as tf:
            tf.add(root, arcname=name,
                   filter=lambda info: None if "__pycache__" in info.name else info)
        return target

    if fmt == "Standalone Folder":
        target = out_dir / name
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(root, target, ignore=_ignore_pycache, dirs_exist_ok=False)
        return target

    if fmt == "GitHub Ready":
        target = out_dir / name
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(root, target, ignore=_ignore_pycache, dirs_exist_ok=False)
        _git_init(target)
        return target

    if fmt == "Git Repository":
        target = out_dir / f"{name}.git"
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(root, target, ignore=_ignore_pycache, dirs_exist_ok=False)
        _git_init(target, bare=False)
        return target

    if fmt == "Termux Ready":
        target = out_dir / f"{name}-termux"
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(root, target, ignore=_ignore_pycache, dirs_exist_ok=False)
        _write_termux_launcher(target, name)
        return target

    if fmt == "Linux Ready":
        target = out_dir / f"{name}-linux"
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(root, target, ignore=_ignore_pycache, dirs_exist_ok=False)
        _write_desktop_entry(target, name, project)
        _write_bash_launcher(target, name)
        return target

    if fmt == "Docker Project":
        target = out_dir / f"{name}-docker"
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(root, target, ignore=_ignore_pycache, dirs_exist_ok=False)
        if not (target / "Dockerfile").exists():
            (target / "Dockerfile").write_text(
                "FROM python:3.11-slim\n"
                "WORKDIR /app\n"
                "COPY requirements.txt .\n"
                "RUN pip install --no-cache-dir -r requirements.txt\n"
                "COPY . .\n"
                "ENTRYPOINT [\"python\", \"main.py\"]\n",
                encoding="utf-8",
            )
        (target / "docker-compose.yml").write_text(
            f'services:\n  {name.replace("-", "_")}:\n    build: .\n    stdin_open: true\n    tty: true\n',
            encoding="utf-8",
        )
        return target

    raise ValueError(f"Unknown export format: {fmt}")


def _git_init(path: Path, bare: bool = False) -> None:
    if not shutil.which("git"):
        _LOG.warning("git not available; skipping git init for %s", path)
        return
    subprocess.run(["git", "init", "-q"] + (["--bare"] if bare else []),
                   cwd=str(path), check=False)
    subprocess.run(["git", "add", "-A"], cwd=str(path), check=False)
    subprocess.run(["git", "commit", "-q", "-m", "Initial commit (ForgeCLI)"],
                   cwd=str(path),
                   env={**os.environ, "GIT_AUTHOR_NAME": "ForgeCLI",
                        "GIT_AUTHOR_EMAIL": "forgecli@local",
                        "GIT_COMMITTER_NAME": "ForgeCLI",
                        "GIT_COMMITTER_EMAIL": "forgecli@local"},
                   check=False)


def _write_termux_launcher(target: Path, name: str) -> None:
    launcher = target / "install-termux.sh"
    launcher.write_text(
        "#!/data/data/com.termux/files/usr/bin/sh\n"
        "set -e\n"
        "pkg update -y\n"
        "pkg install -y python git\n"
        "pip install -r requirements.txt\n"
        "echo 'Run with: python main.py'\n",
        encoding="utf-8",
    )
    try:
        os.chmod(launcher, 0o755)
    except OSError:
        pass


def _write_bash_launcher(target: Path, name: str) -> None:
    launcher = target / f"{name}.sh"
    launcher.write_text(
        "#!/usr/bin/env bash\n"
        "set -e\n"
        'cd "$(dirname "$0")"\n'
        "python3 main.py \"$@\"\n",
        encoding="utf-8",
    )
    try:
        os.chmod(launcher, 0o755)
    except OSError:
        pass


def _write_desktop_entry(target: Path, name: str, project: GeneratedProject) -> None:
    entry = target / f"{name}.desktop"
    entry.write_text(
        "[Desktop Entry]\n"
        f"Name={project.branding.project_name}\n"
        f"Comment={project.branding.tagline}\n"
        "Exec=python3 main.py\n"
        f"Path={target}\n"
        "Terminal=true\n"
        "Type=Application\n"
        "Categories=Utility;\n",
        encoding="utf-8",
    )


__all__ = ["EXPORT_FORMATS", "export_project"]