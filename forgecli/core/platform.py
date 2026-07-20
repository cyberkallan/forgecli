"""Platform detection for ForgeCLI.

Identifies the runtime operating system and the appropriate package manager.
"""
from __future__ import annotations

import os
import shutil
import sys
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from .logging_utils import get_logger

_LOG = get_logger("core.platform")


class OSFamily(str, Enum):
    """Supported operating system families."""

    TERMUX = "Termux"
    UBUNTU = "Ubuntu"
    DEBIAN = "Debian"
    KALI = "Kali"
    ARCH = "Arch"
    FEDORA = "Fedora"
    MACOS = "macOS"
    WINDOWS = "Windows"
    UNKNOWN = "Unknown"


@dataclass(frozen=True)
class PackageManager:
    """A package manager definition."""

    name: str
    install_cmd: List[str]  # used to install system packages
    update_cmd: List[str]
    check_cmd: List[str]  # command used to verify a package is present


@dataclass(frozen=True)
class PlatformInfo:
    """Everything ForgeCLI knows about the current runtime."""

    os_family: OSFamily
    pretty_name: str
    kernel: str
    arch: str
    package_manager: Optional[PackageManager]


def _read_os_release() -> dict:
    """Parse ``/etc/os-release`` if available."""
    candidates = ("/etc/os-release", "/usr/lib/os-release")
    data: dict = {}
    for path in candidates:
        if os.path.isfile(path):
            try:
                with open(path, encoding="utf-8") as fh:
                    for line in fh:
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        k, v = line.split("=", 1)
                        data[k.strip().upper()] = v.strip().strip('"').strip("'")
                break
            except OSError as exc:
                _LOG.debug("Failed to read %s: %s", path, exc)
    return data


def _detect_termux() -> bool:
    """Termux exposes itself through a few env vars and paths."""
    if os.environ.get("TERMUX_VERSION"):
        return True
    if os.path.isdir("/data/data/com.termux/files/usr"):
        return True
    if "com.termux" in (os.environ.get("PREFIX") or ""):
        return True
    return False


def _detect_os_family() -> OSFamily:
    if _detect_termux():
        return OSFamily.TERMUX
    if sys.platform.startswith("win"):
        return OSFamily.WINDOWS
    if sys.platform == "darwin":
        return OSFamily.MACOS
    info = _read_os_release()
    ident = (info.get("ID") or "").lower()
    like = (info.get("ID_LIKE") or "").lower()
    if ident == "kali" or "kali" in ident:
        return OSFamily.KALI
    if ident == "ubuntu":
        return OSFamily.UBUNTU
    if ident == "debian":
        return OSFamily.DEBIAN
    if ident == "arch" or "arch" in like:
        return OSFamily.ARCH
    if ident in {"fedora", "nobara", "rhel", "centos"}:
        return OSFamily.FEDORA
    if "ubuntu" in like:
        return OSFamily.UBUNTU
    if "debian" in like:
        return OSFamily.DEBIAN
    if "arch" in like:
        return OSFamily.ARCH
    if "fedora" in like or "rhel" in like:
        return OSFamily.FEDORA
    return OSFamily.UNKNOWN


def _detect_package_manager(family: OSFamily) -> Optional[PackageManager]:
    """Map an OS family to its package manager."""
    if family in {OSFamily.UBUNTU, OSFamily.DEBIAN, OSFamily.KALI}:
        return PackageManager(
            name="apt",
            install_cmd=["sudo", "apt-get", "install", "-y"],
            update_cmd=["sudo", "apt-get", "update"],
            check_cmd=["dpkg", "-s"],
        )
    if family == OSFamily.TERMUX:
        return PackageManager(
            name="pkg",
            install_cmd=["pkg", "install", "-y"],
            update_cmd=["pkg", "update", "-y"],
            check_cmd=["dpkg", "-s"],
        )
    if family == OSFamily.ARCH:
        return PackageManager(
            name="pacman",
            install_cmd=["sudo", "pacman", "-S", "--noconfirm"],
            update_cmd=["sudo", "pacman", "-Sy"],
            check_cmd=["pacman", "-Qi"],
        )
    if family == OSFamily.FEDORA:
        return PackageManager(
            name="dnf",
            install_cmd=["sudo", "dnf", "install", "-y"],
            update_cmd=["sudo", "dnf", "check-update", "-y"],
            check_cmd=["rpm", "-q"],
        )
    if family == OSFamily.MACOS:
        if shutil.which("brew"):
            return PackageManager(
                name="brew",
                install_cmd=["brew", "install"],
                update_cmd=["brew", "update"],
                check_cmd=["brew", "list"],
            )
        return None
    return None


def detect_platform() -> PlatformInfo:
    """Identify the current runtime environment."""
    family = _detect_os_family()
    pretty = {
        OSFamily.TERMUX: "Termux (Android)",
        OSFamily.UBUNTU: "Ubuntu",
        OSFamily.DEBIAN: "Debian",
        OSFamily.KALI: "Kali Linux",
        OSFamily.ARCH: "Arch Linux",
        OSFamily.FEDORA: "Fedora",
        OSFamily.MACOS: "macOS",
        OSFamily.WINDOWS: "Windows",
        OSFamily.UNKNOWN: "Unknown Linux",
    }.get(family, "Unknown")
    pretty_name = pretty
    if family not in {OSFamily.MACOS, OSFamily.WINDOWS, OSFamily.TERMUX}:
        info = _read_os_release()
        if info.get("PRETTY_NAME"):
            pretty_name = info["PRETTY_NAME"]
    return PlatformInfo(
        os_family=family,
        pretty_name=pretty_name,
        kernel=os.uname().sysname if hasattr(os, "uname") else sys.platform,
        arch=os.uname().machine if hasattr(os, "uname") else "unknown",
        package_manager=_detect_package_manager(family),
    )


def is_root() -> bool:
    """Return True if the process runs with root privileges."""
    try:
        return os.geteuid() == 0  # type: ignore[attr-defined]
    except AttributeError:
        return False  # Windows


__all__ = [
    "OSFamily",
    "PackageManager",
    "PlatformInfo",
    "detect_platform",
    "is_root",
]
