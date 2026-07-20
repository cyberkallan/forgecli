"""Automatic dependency detection and installation."""
from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Sequence

from .logging_utils import get_logger
from .platform import PlatformInfo, PackageManager, is_root

_LOG = get_logger("core.dependencies")


@dataclass
class Dependency:
    """An external tool ForgeCLI depends on."""

    name: str
    binary: str
    apt: Optional[str] = None
    pkg: Optional[str] = None
    pacman: Optional[str] = None
    dnf: Optional[str] = None
    brew: Optional[str] = None
    pip: Optional[str] = None  # python package providing this binary
    optional: bool = False
    description: str = ""

    def installable(self, manager_name: str) -> Optional[str]:
        """Return the package name to install on the given manager, if any."""
        attr = manager_name.lower()
        return getattr(self, attr, None)


@dataclass
class DependencyReport:
    """Result of a dependency scan."""

    present: List[str] = field(default_factory=list)
    installed_now: List[str] = field(default_factory=list)
    missing_optional: List[str] = field(default_factory=list)
    failed: List[str] = field(default_factory=list)


# Canonical dependency list for ForgeCLI itself.
FORGECLI_DEPS: List[Dependency] = [
    Dependency(
        "Python interpreter",
        binary=sys.executable,
        description="Python 3.9+ runtime.",
    ),
    Dependency("git", "git", apt="git", pkg="git", pacman="git", dnf="git", brew="git",
               description="Version control system."),
    Dependency("curl", "curl", apt="curl", pkg="curl", pacman="curl", dnf="curl", brew="curl",
               description="Command line HTTP client."),
    Dependency("wget", "wget", apt="wget", pkg="wget", pacman="wget", dnf="wget", brew="wget",
               optional=True, description="Alternative downloader."),
    Dependency("figlet", "figlet", apt="figlet", pkg="figlet", pacman="figlet", dnf="figlet", brew="figlet",
               optional=True, description="FIGlet banner generator."),
    Dependency("lolcat", "lolcat", apt="lolcat", pkg="lolcat", pacman="lolcat-llc", brew="lolcat",
               pip="lolcat", optional=True, description="Rainbow text tool."),
    Dependency("toilet", "toilet", apt="toilet", pkg="toilet", pacman="toilet", dnf="toilet", brew="toilet",
               optional=True, description="TOIlet banner generator."),
]


def check_binary(binary: str) -> bool:
    """Return True if ``binary`` is on PATH or is a valid absolute path."""
    if not binary:
        return False
    if binary == sys.executable:
        return True
    return shutil.which(binary) is not None


def ensure_python_packages(packages: Sequence[str], quiet: bool = True) -> List[str]:
    """Install missing pip packages. Returns the list of newly installed packages."""
    installed: List[str] = []
    for pkg in packages:
        try:
            __import__(pkg.replace("-", "_").split("[")[0])
            continue
        except ImportError:
            pass
        cmd = [sys.executable, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", pkg]
        if quiet:
            cmd.append("--no-warn-script-location")
        _LOG.info("Installing pip package: %s", pkg)
        try:
            subprocess.run(cmd, check=True)  # noqa: S603
            installed.append(pkg)
        except subprocess.CalledProcessError as exc:
            _LOG.warning("Failed to install %s: %s", pkg, exc)
    return installed


def _run_with_privilege(cmd: Sequence[str], manager: PackageManager) -> bool:
    """Run a package install command, trying to gain root if needed."""
    if cmd[0] == "sudo" and is_root():
        cmd = list(cmd)[1:]
    try:
        subprocess.run(list(cmd), check=True)  # noqa: S603
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, OSError) as exc:
        _LOG.warning("Install command %s failed: %s", cmd, exc)
        # Fallback: try without sudo if it failed.
        if cmd and cmd[0] == "sudo":
            try:
                subprocess.run(list(cmd)[1:], check=True)  # noqa: S603
                return True
            except (subprocess.CalledProcessError, FileNotFoundError, OSError) as exc2:
                _LOG.error("Fallback install failed: %s", exc2)
        return False


def install_system_package(package_name: str, platform_info: PlatformInfo) -> bool:
    """Install a single system package using the detected manager."""
    manager = platform_info.package_manager
    if manager is None:
        return False
    cmd = manager.install_cmd + [package_name]
    return _run_with_privilege(cmd, manager)


def scan_and_resolve(
    deps: Optional[Sequence[Dependency]] = None,
    platform_info: Optional[PlatformInfo] = None,
    *,
    install_missing: bool = True,
    progress: Optional[Callable[[str], None]] = None,
) -> DependencyReport:
    """Check each dependency and (optionally) install anything missing."""
    from .platform import detect_platform

    deps = deps or FORGECLI_DEPS
    pi = platform_info or detect_platform()
    manager = pi.package_manager

    report = DependencyReport()

    for dep in deps:
        if check_binary(dep.binary):
            report.present.append(dep.name)
            if progress:
                progress(f"OK   {dep.name}")
            continue

        if dep.optional:
            report.missing_optional.append(dep.name)
            if progress:
                progress(f"SKIP {dep.name} (optional)")
            continue

        if not install_missing:
            report.failed.append(dep.name)
            if progress:
                progress(f"MISS {dep.name}")
            continue

        installed_ok = False
        if manager is not None:
            pkg = dep.installable(manager.name)
            if pkg:
                if progress:
                    progress(f"INSTALL {pkg} via {manager.name} ...")
                installed_ok = install_system_package(pkg, pi)
        if installed_ok:
            report.installed_now.append(dep.name)
            if progress:
                progress(f"DONE {dep.name}")
            continue

        if dep.pip:
            if progress:
                progress(f"PIP   {dep.pip}")
            if ensure_python_packages([dep.pip]):
                report.installed_now.append(dep.name)
                continue

        report.failed.append(dep.name)
        if progress:
            progress(f"FAIL {dep.name}")
    return report


__all__ = [
    "Dependency",
    "DependencyReport",
    "FORGECLI_DEPS",
    "check_binary",
    "ensure_python_packages",
    "install_system_package",
    "scan_and_resolve",
]
