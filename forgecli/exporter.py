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
    "PyPI Package",
    "Homebrew Formula",
    "AUR PKGBUILD",
    "Systemd Service",
    "Makefile",
    "Install Script",
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

    if fmt == "PyPI Package":
        target = out_dir / f"{name}-pypi"
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True)
        # Copy the project files (excluding the workspace README etc.) into a
        # `src/` layout that pip can build.
        src = target / "src" / project.branding.command_name
        shutil.copytree(root, src, ignore=_ignore_pycache, dirs_exist_ok=False)
        (target / "pyproject.toml").write_text(
            _pypi_pyproject(project), encoding="utf-8")
        (target / "README.md").write_text((root / "README.md").read_text(encoding="utf-8"),
                                           encoding="utf-8")
        (target / "LICENSE").write_text((root / "LICENSE").read_text(encoding="utf-8"),
                                          encoding="utf-8")
        return target

    if fmt == "Homebrew Formula":
        target = out_dir / f"{name}.rb"
        target.write_text(_homebrew_formula(project), encoding="utf-8")
        return target

    if fmt == "AUR PKGBUILD":
        target = out_dir / "PKGBUILD"
        target.write_text(_aur_pkgbuild(project), encoding="utf-8")
        return target

    if fmt == "Systemd Service":
        target = out_dir / f"{name}.service"
        target.write_text(_systemd_unit(project), encoding="utf-8")
        (out_dir / f"{name}-systemd-install.sh").write_text(
            f"#!/usr/bin/env bash\nset -e\n"
            f"install -Dm644 \"{name}.service\" /etc/systemd/system/{name}.service\n"
            "systemctl daemon-reload\n"
            f"systemctl enable --now {name}.service\n",
            encoding="utf-8",
        )
        try:
            os.chmod(out_dir / f"{name}-systemd-install.sh", 0o755)
        except OSError:
            pass
        return target

    if fmt == "Makefile":
        target = out_dir / "Makefile"
        target.write_text(_makefile(project), encoding="utf-8")
        return target

    if fmt == "Install Script":
        target = out_dir / "install.sh"
        target.write_text(_install_script(project), encoding="utf-8")
        try:
            os.chmod(target, 0o755)
        except OSError:
            pass
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


def _pypi_pyproject(project: GeneratedProject) -> str:
    b = project.branding
    py_min = b.python_version.replace(">=", "").strip() or "3.9"
    keywords = b.tags or ["cli", "cybersecurity", "terminal"]
    kw_str = "[" + ", ".join(f'"{t}"' for t in keywords) + "]"
    return (
        "[build-system]\nrequires = [\"setuptools>=68\", \"wheel\"]\n"
        "build-backend = \"setuptools.build_meta\"\n\n"
        "[project]\n"
        f'name = "{b.command_name}"\n'
        f'version = "{b.version}"\n'
        f'description = "{b.description}"\n'
        'readme = "README.md"\n'
        f'requires-python = ">={py_min}"\n'
        f'license = {{text = "{b.license}"}}\n'
        f'authors = [{{name = "{b.author}"}}]\n'
        f'keywords = {kw_str}\n'
        'dependencies = [\n'
        '    "rich>=13.7.0",\n'
        '    "pyfiglet>=1.0.2",\n'
        '    "questionary>=2.0.1",\n'
        ']\n\n'
        "[project.scripts]\n"
        f'{b.command_name} = "{b.command_name}.main:main"\n\n'
        "[tool.setuptools.packages.find]\n"
        "where = [\"src\"]\n"
    )


def _homebrew_formula(project: GeneratedProject) -> str:
    b = project.branding
    repo = (b.github or "https://github.com/cyberkallan/forgecli").rstrip("/")
    class_name = "".join(w.capitalize() for w in b.command_name.split("-"))
    return (
        f"class {class_name} < Formula\n"
        f'  desc "{b.description}"\n'
        f'  homepage "{repo}"\n'
        f'  url "{repo}/archive/refs/tags/v{b.version}.tar.gz"\n'
        f'  sha256 "REPLACE_WITH_REAL_SHA256"\n'
        f'  license "{b.license}"\n'
        '  depends_on "python@3.11"\n\n'
        '  def install\n'
        '    venv = virtualenv_create(libexec, "python3.11")\n'
        '    venv.pip_install resources\n'
        "    venv.pip_install_and_link buildpath\n"
        f'    bin.install_symlink libexec/"bin/{b.command_name}"\n'
        "  end\n"
        "end\n"
    )


def _aur_pkgbuild(project: GeneratedProject) -> str:
    b = project.branding
    repo = (b.github or "https://github.com/cyberkallan/forgecli").rstrip("/")
    return (
        f"pkgname={b.command_name}\n"
        f"pkgver={b.version}\n"
        "pkgrel=1\n"
        f'pkgdesc="{b.description}"\n'
        f'url="{repo}"\n'
        f'license=("{b.license}")\n'
        "depends=(python python-rich python-pyfiglet python-questionary)\n"
        f'source=("$pkgname-$pkgver.tar.gz::{repo}/archive/refs/tags/v$pkgver.tar.gz")\n'
        'md5sums=("SKIP")\n\n'
        "package() {\n"
        f'  install -Dm644 "$srcdir/$pkgname-$pkgver/main.py" "$pkgdir/usr/lib/$pkgname/main.py"\n'
        "  install -d \"$pkgdir/usr/lib/$pkgname\"\n"
        "  cp -r \"$srcdir/$pkgname-$pkgver/\"* \"$pkgdir/usr/lib/$pkgname/\"\n"
        f'  install -Dm755 /dev/stdin "$pkgdir/usr/bin/{b.command_name}" <<EOF\n'
        "#!/usr/bin/env bash\n"
        f'exec python3 /usr/lib/{b.command_name}/main.py "$@"\n'
        "EOF\n"
        "}\n"
    )


def _systemd_unit(project: GeneratedProject) -> str:
    b = project.branding
    return (
        "[Unit]\n"
        f"Description={b.project_name}\n"
        "After=network.target\n\n"
        "[Service]\n"
        f"Type=simple\n"
        f"ExecStart=/usr/bin/python3 /opt/{b.command_name}/main.py\n"
        f"WorkingDirectory=/opt/{b.command_name}\n"
        "Restart=on-failure\n"
        "RestartSec=5\n\n"
        "[Install]\n"
        "WantedBy=multi-user.target\n"
    )


def _makefile(project: GeneratedProject) -> str:
    b = project.branding
    return (
        f"PY ?= python3\n"
        f"NAME = {b.command_name}\n\n"
        ".PHONY: install run test clean build\n\n"
        "install:\n"
        "\t$(PY) -m pip install -r requirements.txt\n"
        "\t$(PY) -m pip install .\n\n"
        "run:\n"
        "\t$(PY) main.py\n\n"
        "test:\n"
        "\t$(PY) -m pytest tests/ -q\n\n"
        "build:\n"
        "\t$(PY) -m build\n\n"
        "clean:\n"
        "\trm -rf build dist *.egg-info __pycache__ .pytest_cache\n"
    )


def _install_script(project: GeneratedProject) -> str:
    b = project.branding
    repo = (b.github or "https://github.com/cyberkallan/forgecli").rstrip("/")
    return (
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n\n"
        'echo "Installing ' + b.project_name + ' ..."\n'
        "if ! command -v python3 >/dev/null 2>&1; then\n"
        '  echo "python3 is required but not installed." >&2\n'
        "  exit 1\n"
        "fi\n\n"
        f'INSTALL_DIR="${HOME}/.{b.command_name}"\n'
        'rm -rf "$INSTALL_DIR"\n'
        f'git clone --depth 1 "{repo}" "$INSTALL_DIR" || \\\n'
        f'  curl -fsSL "{repo}/archive/refs/heads/main.tar.gz" | tar -xz -C "$INSTALL_DIR" --strip-components=1\n\n'
        'cd "$INSTALL_DIR"\n'
        'python3 -m pip install --user -r requirements.txt\n\n'
        f'BIN_DIR="${HOME}/.local/bin"\nmkdir -p "$BIN_DIR"\n'
        f'cat > "$BIN_DIR/{b.command_name}" <<EOF\n'
        "#!/usr/bin/env bash\n"
        f'exec python3 "$INSTALL_DIR/main.py" "$@"\n'
        "EOF\n"
        f'chmod +x "$BIN_DIR/{b.command_name}"\n\n'
        f'echo "Done. Run with: {b.command_name}"\n'
    )


__all__ = ["EXPORT_FORMATS", "export_project"]