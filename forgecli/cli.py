"""ForgeCLI entry point - supports both subcommands and the interactive dashboard."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Sequence

from . import __version__
from .core.config import load_state, save_state
from .core.dependencies import ensure_python_packages
from .core.logging_utils import configure_logging, get_logger
from .core.platform import detect_platform
from .core.system_info import collect_system_info
from .dashboard import run_dashboard
from .generators.project import generate_project
from .models import Branding
from .profiles import (
    delete_profile, list_profiles, load_profile, save_profile,
)
from .self_update import apply_update, check_update
from .themes.builtin import BUILTIN_THEMES
from .ui.animations import run_startup_sequence
from .ui.banners import build_banner
from .ui.prompts import console
from .ui.theme import build_registry
from .validate import validate_project

_LOG = get_logger("cli")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: Optional[Sequence[str]] = None) -> int:
    configure_logging()
    parser = build_parser()
    # If no args at all, run the interactive dashboard (preserve original UX).
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        return _run_dashboard()

    args = parser.parse_args(list(argv))
    if not getattr(args, "command", None):
        return _run_dashboard()
    handler = COMMANDS.get(args.command)
    if handler is None:
        parser.print_help()
        return 1
    return handler(args) or 0


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="forgecli",
        description="ForgeCLI - Premium Terminal Tool Builder. "
                    "Generates complete, production-quality CLI applications "
                    "from user input. Run with no subcommand to launch the dashboard.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    sub = parser.add_subparsers(dest="command", metavar="SUBCOMMAND")

    # ----- new: non-interactive generation from flags --------------------
    p_new = sub.add_parser(
        "new", aliases=["n"],
        help="Generate a new project non-interactively from flags.",
    )
    p_new.add_argument("--name", required=True, help="Project name (used as the folder slug).")
    p_new.add_argument("--command", help="CLI command (defaults to slugified name).")
    p_new.add_argument("--author", help="Author name.")
    p_new.add_argument("--github", help="GitHub profile URL.")
    p_new.add_argument("--category", help="Tool category (see `forgecli list-categories`).")
    p_new.add_argument("--subcategory", help="Tool subcategory.")
    p_new.add_argument("--theme", help="Theme name (see `forgecli themes`).")
    p_new.add_argument("--description", help="Project description.")
    p_new.add_argument("--tagline", help="Project tagline.")
    p_new.add_argument("--license", default="MIT", help="License (MIT, Apache-2.0, GPL-3.0).")
    p_new.add_argument("--version", dest="project_version", default="1.0.0",
                        help="Project version.")
    p_new.add_argument("--out", default=".", help="Output directory.")
    p_new.add_argument("--overwrite", action="store_true", help="Overwrite target dir if it exists.")
    p_new.add_argument("--no-docker", action="store_true", help="Don't include Docker files.")
    p_new.add_argument("--no-tests", action="store_true", help="Don't include tests.")
    p_new.add_argument("--save-profile", help="Also save the result as a branding profile.")

    # ----- init: interactive shortcut into the wizard ----------------------
    sub.add_parser("init", aliases=["i"], help="Launch the interactive branding wizard.")

    # ----- generate: from branding JSON -----------------------------------
    p_gen = sub.add_parser(
        "generate", aliases=["g"],
        help="Generate a project from a saved branding.json file.",
    )
    p_gen.add_argument("branding", type=Path, help="Path to branding.json.")
    p_gen.add_argument("--out", default=".", help="Output directory.")
    p_gen.add_argument("--overwrite", action="store_true", help="Overwrite target dir if it exists.")
    p_gen.add_argument("--save-profile", help="Also save the result as a branding profile.")

    # ----- list-categories -------------------------------------------------
    sub.add_parser("list-categories", aliases=["cats"],
                   help="List every tool category and its subcategories.")

    # ----- themes ----------------------------------------------------------
    sub.add_parser("themes", aliases=["t"],
                   help="List every available theme.")

    # ----- profiles --------------------------------------------------------
    p_prof = sub.add_parser("profiles", aliases=["pf"],
                             help="Manage branding profiles.")
    p_prof.add_argument("action", choices=["list", "save", "load", "delete"])
    p_prof.add_argument("name", nargs="?", help="Profile name (for save/load/delete).")
    p_prof.add_argument("--from", dest="from_path", type=Path,
                         help="Load branding from this file (for `save`).")

    # ----- validate --------------------------------------------------------
    p_val = sub.add_parser("validate", aliases=["v"],
                            help="Run a headless validation on a generated project.")
    p_val.add_argument("path", type=Path, help="Project directory.")

    # ----- export ----------------------------------------------------------
    p_exp = sub.add_parser("export", aliases=["e"],
                            help="Export a generated project in many formats.")
    p_exp.add_argument("path", type=Path, help="Project directory.")
    p_exp.add_argument("--format", "-f", required=True,
                        help="Format: zip, tar.gz, folder, github, termux, linux, docker, git, "
                              "pypi, homebrew, aur, systemd, makefile, install.sh.")
    p_exp.add_argument("--out", default="./exports", help="Export directory.")

    # ----- run -------------------------------------------------------------
    p_run = sub.add_parser("run", aliases=["r"],
                            help="Run a generated project (headless or interactive).")
    p_run.add_argument("path", type=Path, help="Project directory.")
    p_run.add_argument("--timeout", type=float, default=None,
                        help="Kill the process after N seconds.")
    p_run.add_argument("--args", nargs=argparse.REMAINDER, default=[],
                        help="Arguments to forward to the tool's main.py.")

    # ----- self-update -----------------------------------------------------
    sub.add_parser("self-update", aliases=["update"],
                   help="Check PyPI and upgrade ForgeCLI if a newer version is available.")

    return parser


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------

COMMANDS: dict = {}


def _register(name):
    def deco(fn):
        COMMANDS[name] = fn
        for a in getattr(fn, "_aliases", ()):
            COMMANDS[a] = fn
        return fn
    return deco


def _err(msg: str, code: int = 1) -> int:
    console.print(f"[red]Error:[/] {msg}")
    return code


@_register("new")
def _cmd_new(args: argparse.Namespace) -> int:
    settings = load_state()
    registry = build_registry()
    name = args.name.strip()
    if not name:
        return _err("Project name is required.")
    cmd = args.command or _slug(name)
    branding = Branding(
        project_name=name,
        command_name=cmd,
        author=(args.author or settings.default_author).strip(),
        github=(args.github or settings.default_github).strip(),
        description=(args.description or f"{name} - a CLI built with ForgeCLI.").strip(),
        tagline=(args.tagline or settings.default_export_dir or "Built with ForgeCLI").strip(),
        category=(args.category or "CLI Utility").strip(),
        subcategory=(args.subcategory or "Custom").strip(),
        theme=(args.theme or settings.default_theme).strip(),
        license=args.license,
        version=args.project_version,
        include_docker=not args.no_docker,
        include_tests=not args.no_tests,
    )
    target = Path(args.out).expanduser().resolve() / cmd
    target.mkdir(parents=True, exist_ok=True)
    try:
        project = generate_project(
            branding, root=target.parent,
            progress=lambda m: console.print(f"  [{('cyan' if registry.get(branding.theme) else 'red')}]* {m}[/]"),
            overwrite=args.overwrite,
        )
    except FileExistsError as exc:
        return _err(str(exc))
    except Exception as exc:
        return _err(f"Generation failed: {exc}")

    if args.save_profile:
        save_profile(args.save_profile, branding)
        console.print(f"[green]Profile saved: {args.save_profile}[/]")

    console.print(f"[green]Generated at {project.root}[/]")
    console.print(f"  Run: python {project.root / 'main.py'}")
    return 0


@_register("init")
def _cmd_init(args: argparse.Namespace) -> int:
    from .wizard.branding import run_branding_wizard
    settings = load_state()
    theme = build_registry().get(settings.default_theme)
    if not theme:
        theme = list(build_registry())[0]
        theme = build_registry().get(theme) or theme
    branding = run_branding_wizard(theme, settings)
    if not branding:
        return 0
    target = Path(settings.default_export_dir or "./exports").expanduser().resolve() / branding.command_name
    target.mkdir(parents=True, exist_ok=True)
    project = generate_project(branding, root=target.parent,
                               progress=lambda m: console.print(f"  [dim]* {m}[/]"))
    console.print(f"[green]Generated at {project.root}[/]")
    return 0


@_register("generate")
def _cmd_generate(args: argparse.Namespace) -> int:
    if not args.branding.exists():
        return _err(f"Branding file not found: {args.branding}")
    try:
        branding = Branding.load(args.branding)
    except Exception as exc:
        return _err(f"Could not load branding.json: {exc}")
    out_root = Path(args.out).expanduser().resolve()
    try:
        project = generate_project(branding, root=out_root, overwrite=args.overwrite,
                                   progress=lambda m: console.print(f"  [dim]* {m}[/]"))
    except FileExistsError as exc:
        return _err(str(exc))
    except Exception as exc:
        return _err(f"Generation failed: {exc}")

    if args.save_profile:
        save_profile(args.save_profile, branding)
        console.print(f"[green]Profile saved: {args.save_profile}[/]")
    console.print(f"[green]Generated at {project.root}[/]")
    return 0


@_register("list-categories")
@_register("cats")
def _cmd_list_categories(args: argparse.Namespace) -> int:
    from .categories import TOOL_CATEGORIES
    for category, subs in TOOL_CATEGORIES.items():
        console.print(f"[cyan bold]{category}[/]")
        for sub in subs:
            console.print(f"  - {sub}")
    return 0


@_register("themes")
@_register("t")
def _cmd_themes(args: argparse.Namespace) -> int:
    for name, theme in BUILTIN_THEMES.items():
        console.print(f"[{theme.primary}]•[/] [bold]{name}[/]  -  {theme.description}")
    return 0


@_register("profiles")
@_register("pf")
def _cmd_profiles(args: argparse.Namespace) -> int:
    if args.action == "list":
        files = list_profiles()
        if not files:
            console.print("[yellow]No profiles saved.[/]")
            return 0
        for fp in files:
            console.print(f"  {fp.stem}")
        return 0
    if not args.name:
        return _err("Profile name is required.")
    if args.action == "save":
        if not args.from_path:
            return _err("Use --from <branding.json> to save a profile.")
        if not args.from_path.exists():
            return _err(f"Not found: {args.from_path}")
        branding = Branding.load(args.from_path)
        path = save_profile(args.name, branding)
        console.print(f"[green]Saved {path}[/]")
        return 0
    if args.action == "load":
        b = load_profile(args.name)
        if not b:
            return _err(f"No profile named {args.name!r}.")
        console.print(b.to_dict())
        return 0
    if args.action == "delete":
        if delete_profile(args.name):
            console.print(f"[green]Deleted profile {args.name}[/]")
            return 0
        return _err(f"No profile named {args.name!r}.")
    return 0


@_register("validate")
@_register("v")
def _cmd_validate(args: argparse.Namespace) -> int:
    report = validate_project(args.path)
    console.print(f"[bold]Validating:[/] {report.path}")
    for c in report.checks:
        console.print(f"  [green]OK[/] {c}")
    for e in report.errors:
        console.print(f"  [red]FAIL[/] {e}")
    return 0 if report.ok else 1


@_register("export")
@_register("e")
def _cmd_export(args: argparse.Namespace) -> int:
    from .exporter import export_project
    proj_path = args.path.resolve()
    if not (proj_path / "branding.json").exists():
        return _err(f"Not a generated project (missing branding.json): {proj_path}")
    branding = Branding.load(proj_path / "branding.json")
    from .models import GeneratedProject
    project = GeneratedProject(branding=branding, root=proj_path)
    fmt_map = {
        "zip": "Zip (.zip)",
        "tar.gz": "Tarball (.tar.gz)",
        "folder": "Standalone Folder",
        "github": "GitHub Ready",
        "termux": "Termux Ready",
        "linux": "Linux Ready",
        "docker": "Docker Project",
        "git": "Git Repository",
        "pypi": "PyPI Package",
        "homebrew": "Homebrew Formula",
        "aur": "AUR PKGBUILD",
        "systemd": "Systemd Service",
        "makefile": "Makefile",
        "install.sh": "Install Script",
    }
    if args.format not in fmt_map:
        return _err(f"Unknown format: {args.format}. Valid: {', '.join(fmt_map)}")
    out = Path(args.out).expanduser().resolve()
    try:
        target = export_project(project, fmt_map[args.format], out)
    except Exception as exc:
        return _err(f"Export failed: {exc}")
    console.print(f"[green]Exported to {target}[/]")
    return 0


@_register("run")
@_register("r")
def _cmd_run(args: argparse.Namespace) -> int:
    from .preview import launch
    from .models import GeneratedProject
    from rich.console import Console as _C
    proj_path = args.path.resolve()
    if not (proj_path / "branding.json").exists():
        return _err(f"Not a generated project (missing branding.json): {proj_path}")
    branding = Branding.load(proj_path / "branding.json")
    project = GeneratedProject(branding=branding, root=proj_path)
    theme = build_registry().get(branding.theme)
    if not theme:
        theme = list(BUILTIN_THEMES.values())[0]
    return launch(project, _C(), theme, args=list(args.args), timeout=args.timeout)


@_register("self-update")
@_register("update")
def _cmd_self_update(args: argparse.Namespace) -> int:
    info = check_update()
    if not info.available:
        console.print(f"[green]Already on the latest version ({info.current}).[/]")
        return 0
    console.print(f"[yellow]Updating {info.current} -> {info.latest} ...[/]")
    ok, output = apply_update()
    console.print(output[-2000:])
    return 0 if ok else _err("Update failed.")


# Make aliases discoverable.
_cmd_list_categories._aliases = ("cats",)
_cmd_themes._aliases = ("t",)
_cmd_profiles._aliases = ("pf",)
_cmd_validate._aliases = ("v",)
_cmd_export._aliases = ("e",)
_cmd_run._aliases = ("r",)
_cmd_self_update._aliases = ("update",)
_cmd_new._aliases = ("n",)
_cmd_init._aliases = ("i",)
_cmd_generate._aliases = ("g",)


# ---------------------------------------------------------------------------
# Interactive dashboard (preserved UX when run with no subcommand)
# ---------------------------------------------------------------------------

def _slug(value: str) -> str:
    import re
    return re.sub(r"[^a-z0-9_]+", "_", (value or "").lower()).strip("_") or "forgecli_tool"


def _run_dashboard() -> int:
    """Launch the interactive dashboard."""
    settings = load_state()
    theme = build_registry().get(settings.default_theme)
    if not theme:
        from .themes.builtin import get_builtin_theme
        theme = get_builtin_theme("Cyberpunk")

    # Ensure dependencies are present.
    for pkg in ("rich", "pyfiglet", "questionary", "colorama"):
        try:
            __import__(pkg)
        except ImportError:
            ensure_python_packages([pkg])

    run_startup_sequence(console, theme, per_step=0.35,
                        animation=settings.extras.get("startup_animation", "Cyber Loading"))

    platform_info = detect_platform()
    console.print(f"[{theme.info}]Platform: {platform_info.pretty_name} "
                  f"(pkg manager: {platform_info.package_manager.name if platform_info.package_manager else 'none'})[/]")

    info = collect_system_info()
    banner = build_banner(console, theme, text="FORGECLI", font="standard",
                           version=__version__,
                           socials={"GitHub": settings.default_github,
                                     "Instagram": settings.default_instagram},
                           status="Ready")
    console.print(banner)
    try:
        return run_dashboard(theme, settings)
    except KeyboardInterrupt:
        console.print(f"\n[{theme.muted}]Interrupted. Bye.[/]")
        return 0
    except Exception as exc:
        _LOG.exception("Dashboard crashed")
        console.print(f"[{theme.danger}]Unexpected error: {exc}[/]")
        return 1


__all__ = ["main", "build_parser", "__version__"]


if __name__ == "__main__":
    sys.exit(main())