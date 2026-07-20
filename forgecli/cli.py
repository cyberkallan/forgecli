"""ForgeCLI entry point."""
from __future__ import annotations

import sys
from typing import Optional

from .core.config import UserSettings, load_state, save_state
from .core.dependencies import ensure_python_packages, scan_and_resolve
from .core.logging_utils import configure_logging, get_logger
from .core.platform import detect_platform
from .core.system_info import collect_system_info
from .dashboard import run_dashboard
from .ui.animations import run_startup_sequence
from .ui.banners import build_banner
from .ui.prompts import console
from .ui.theme import Theme, build_registry

_LOG = get_logger("cli")


def _ensure_runtime_libs(theme: Theme) -> None:
    """Make sure rich/pyfiglet/questionary are importable (pip if needed)."""
    missing = []
    for pkg, mod in [("rich", "rich"), ("pyfiglet", "pyfiglet"),
                     ("questionary", "questionary"), ("colorama", "colorama")]:
        try:
            __import__(mod)
        except ImportError:
            missing.append(pkg)
    if missing:
        console.print(f"[{theme.warning}]Installing: {', '.join(missing)} ...[/]")
        ensure_python_packages(missing)


def _resolve_theme(settings: UserSettings) -> Theme:
    registry = build_registry()
    return registry.get(settings.default_theme) or registry.get("Cyberpunk")  # type: ignore[return-value]


def main(argv: Optional[list] = None) -> int:
    """Run ForgeCLI. Returns a process exit code."""
    configure_logging()
    settings = load_state()
    theme = _resolve_theme(settings)

    # 1. Ensure our own runtime libraries exist.
    _ensure_runtime_libs(theme)

    # 2. Animated startup.
    run_startup_sequence(console, theme, per_step=0.35,
                        animation=settings.extras.get("startup_animation", "Cyber Loading"))

    # 3. Detect platform + auto-install missing system tools.
    platform_info = detect_platform()
    console.print(f"[{theme.info}]Platform: {platform_info.pretty_name} "
                  f"(pkg manager: {platform_info.package_manager.name if platform_info.package_manager else 'none'})[/]")
    try:
        report = scan_and_resolve(platform_info=platform_info,
                                  progress=lambda msg: console.print(f"  [{theme.muted}]{msg}[/]"))
        if report.failed:
            console.print(f"[{theme.warning}]Optional tools missing: {', '.join(report.failed)}[/]")
    except Exception as exc:  # never block the app on dep issues
        _LOG.warning("Dependency resolution failed: %s", exc)

    # 4. Banner + system info.
    info = collect_system_info()
    banner = build_banner(console, theme, text="FORGECLI", font="standard",
                           version="1.0.0",
                           socials={"GitHub": settings.default_github,
                                     "Instagram": settings.default_instagram},
                           status="Ready")
    console.print(banner)

    # 5. Dashboard loop.
    try:
        return run_dashboard(theme, settings)
    except KeyboardInterrupt:
        console.print(f"\n[{theme.muted}]Interrupted. Bye.[/]")
        return 0
    except Exception as exc:  # surface unexpected errors cleanly
        _LOG.exception("Dashboard crashed")
        console.print(f"[{theme.danger}]Unexpected error: {exc}[/]")
        return 1


if __name__ == "__main__":
    sys.exit(main())