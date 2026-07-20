"""System information gathering for the dashboard header."""
from __future__ import annotations

import os
import platform
import shutil
import socket
import subprocess
from dataclasses import asdict, dataclass, field
from typing import Optional


@dataclass
class SystemInfo:
    """A snapshot of host information relevant to the dashboard."""

    os_name: str = ""
    os_version: str = ""
    kernel: str = ""
    python_version: str = ""
    terminal_size: str = "unknown"
    cpu: str = ""
    ram_total: str = ""
    ram_used: str = ""
    current_dir: str = ""
    cwd_writable: bool = True
    network_status: str = "unknown"
    git_status: str = ""
    shell: str = ""
    user: str = ""
    extras: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return asdict(self)


def _humanize_bytes(num: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(num) < 1024.0:
            return f"{num:3.1f} {unit}"
        num /= 1024.0
    return f"{num:.1f} PB"


def _read_meminfo() -> dict:
    data = {}
    try:
        with open("/proc/meminfo", encoding="utf-8") as fh:
            for line in fh:
                if ":" in line:
                    k, v = line.split(":", 1)
                    data[k.strip()] = v.strip().split()[0]
    except OSError:
        pass
    return data


def _read_cpuinfo() -> dict:
    data = {}
    try:
        with open("/proc/cpuinfo", encoding="utf-8") as fh:
            for line in fh:
                if ":" in line:
                    k, v = line.split(":", 1)
                    data.setdefault(k.strip(), v.strip())
    except OSError:
        pass
    return data


def _check_network(timeout: float = 1.5) -> str:
    """Cheap connectivity check that never blocks long."""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("1.1.1.1", 53))
        return "online"
    except OSError:
        return "offline"


def _check_git_status(cwd: str) -> str:
    if not shutil.which("git"):
        return "git not installed"
    try:
        result = subprocess.run(  # noqa: S603
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            timeout=2,
        )
        if result.returncode != 0:
            return "not a git repo"
        branch = subprocess.run(  # noqa: S603
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            timeout=2,
        )
        status = subprocess.run(  # noqa: S603
            ["git", "status", "--short"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            timeout=2,
        )
        branch_name = (branch.stdout or "main").strip()
        dirty = bool((status.stdout or "").strip())
        return f"on {branch_name}{' (dirty)' if dirty else ''}"
    except (subprocess.TimeoutExpired, OSError) as exc:
        return f"git error: {exc.__class__.__name__}"


def _terminal_size() -> str:
    try:
        size = shutil.get_terminal_size((80, 24))
        return f"{size.columns}x{size.lines}"
    except (OSError, ValueError):
        return "unknown"


def collect_system_info(cwd: Optional[str] = None) -> SystemInfo:
    """Collect a SystemInfo snapshot for the current process."""
    cwd = cwd or os.getcwd()
    meminfo = _read_meminfo()
    cpuinfo = _read_cpuinfo()
    ram_total = _humanize_bytes(int(meminfo.get("MemTotal", 0)) * 1024) if meminfo else "unknown"
    ram_avail = int(meminfo.get("MemAvailable", 0)) * 1024 if meminfo else 0
    ram_total_bytes = int(meminfo.get("MemTotal", 0)) * 1024 if meminfo else 0
    ram_used = _humanize_bytes(ram_total_bytes - ram_avail) if ram_total_bytes else "unknown"

    size = shutil.get_terminal_size((80, 24))
    info = SystemInfo(
        os_name=platform.system(),
        os_version=platform.version(),
        kernel=platform.release(),
        python_version=platform.python_version(),
        terminal_size=f"{size.columns}x{size.lines}",
        cpu=cpuinfo.get("model name", platform.processor() or "unknown"),
        ram_total=ram_total,
        ram_used=ram_used,
        current_dir=cwd,
        cwd_writable=os.access(cwd, os.W_OK),
        network_status=_check_network(),
        git_status=_check_git_status(cwd),
        shell=os.environ.get("SHELL") or os.environ.get("COMSPEC") or "unknown",
        user=os.environ.get("USER") or os.environ.get("USERNAME") or "unknown",
    )
    return info


__all__ = ["SystemInfo", "collect_system_info"]
