"""ForgeCLI dashboard - the main navigation hub."""
from __future__ import annotations

from pathlib import Path

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .ascii_view import run_ascii_generator
from .banner_builder import run_banner_builder
from .core.config import UserSettings, get_state_dir, load_state, save_state
from .core.dependencies import FORGECLI_DEPS, scan_and_resolve
from .core.logging_utils import get_logger
from .core.system_info import collect_system_info
from .core.platform import detect_platform
from .exporter import EXPORT_FORMATS, export_project
from .filemanager import manage as manage_files
from .generators.commands_runtime import commands_for
from .generators.project import (
    WORKSPACE_DIR, generate_project, list_generated_projects, load_project,
)
from .models import Branding
from .preview import launch as launch_preview
from .settings_view import manage_settings
from .theme_creator import run_theme_creator
from .ui.banners import build_banner
from .ui.menu import MENU_STYLES, render_menu_table
from .ui.prompts import console as default_console, confirm
from .ui.theme import Theme, build_registry

_LOG = get_logger("dashboard")


DASHBOARD_OPTIONS = [
    "Create New Tool",
    "Open Existing Project",
    "Edit Project",
    "Generate Files",
    "Export Project",
    "Preview Tool",
    "Themes",
    "Plugins",
    "Templates",
    "Settings",
    "About",
    "Exit",
]


def _banner(theme: Theme, *, settings: UserSettings) -> Panel:
    info = collect_system_info()
    socials = {
        "GitHub": settings.default_github,
        "Instagram": settings.default_instagram,
    }
    return build_banner(default_console, theme, text="FORGECLI",
                        font="standard", version="1.0.0", socials=socials,
                        status="Ready")


def _system_panel(theme: Theme) -> Panel:
    info = collect_system_info()
    table = Table.grid(padding=(0, 1))
    table.add_column(style=theme.muted)
    table.add_column(style=theme.fg)
    rows = [
        ("OS", info.os_name),
        ("Version", info.os_version),
        ("Kernel", info.kernel),
        ("Python", info.python_version),
        ("Terminal", info.terminal_size),
        ("CPU", info.cpu[:50] or "unknown"),
        ("RAM", f"{info.ram_used} / {info.ram_total}"),
        ("Network", info.network_status),
        ("Git", info.git_status),
        ("CWD", info.current_dir),
    ]
    for label, value in rows:
        table.add_row(f" {label} ", str(value))
    return Panel(table, border_style=theme.border,
                 title=f"[{theme.primary}]System[/]")


def _print_dashboard(theme: Theme, settings: UserSettings) -> None:
    default_console.print(_banner(theme, settings=settings))
    default_console.print(_system_panel(theme))
    default_console.print(Panel(
        render_menu_table(theme.menu_style if hasattr(theme, "menu_style") else "Cyber",
                          "Dashboard", DASHBOARD_OPTIONS, theme),
        border_style=theme.border,
        title=f"[{theme.primary}]◆[/] [{theme.secondary}]Dashboard[/]",
        padding=(1, 2),
    ))


def _pick_project(console: Console) -> "GeneratedProject | None":
    projects = list_generated_projects()
    if not projects:
        return None
    labels = [f"{p.root.name}  ·  {p.branding.subcategory}" for p in projects]
    choice = questionary.select("Open project", choices=labels).ask()
    if not choice:
        return None
    idx = labels.index(choice)
    return projects[idx]


def _create_new_tool(console: Console, theme: Theme, settings: UserSettings) -> None:
    if questionary.confirm("Use quick branding (essentials only)?",
                            default=False).ask():
        from .wizard.branding import run_quick_branding
        branding = run_quick_branding(theme, settings)
    else:
        from .wizard.branding import run_branding_wizard
        branding = run_branding_wizard(theme, settings)

    if not branding:
        return

    console.print(Panel(_branding_summary(branding, theme),
                        border_style=theme.border,
                        title=f"[{theme.primary}]Branding summary[/]"))

    if not questionary.confirm("Generate this project?", default=True).ask():
        return

    target_dir = questionary.text("Output directory",
                                   settings.default_export_dir or "./exports").ask()
    target = Path(target_dir) if target_dir else None
    with console.status("[bold]Generating project...", spinner=theme.spinner_type if hasattr(theme, "spinner_type") else "dots"):
        project = generate_project(branding, root=target, progress=lambda msg: console.print(f"  • {msg}"))
    console.print(f"[{theme.success}]Project generated at {project.root}[/]")


def _branding_summary(b: Branding, theme) -> str:
    lines = [
        f"Name:        {b.project_name}",
        f"Command:     {b.command_name}",
        f"Author:      {b.author}",
        f"Version:     {b.version}",
        f"Category:    {b.category} / {b.subcategory}",
        f"License:     {b.license}",
        f"Theme:       {b.theme}",
        f"Animation:   {b.startup_animation}",
        f"Menu style:  {b.menu_style}",
        f"ASCII font:  {b.ascii_style}",
        f"Auto update: {b.auto_update}",
    ]
    return "\n".join(f"[{theme.secondary}]{ln}[/]" for ln in lines)


def _export_project(console: Console, theme: Theme, settings: UserSettings) -> None:
    project = _pick_project(console)
    if not project:
        console.print(f"[{theme.warning}]No projects available. Create one first.[/]")
        return
    fmt = questionary.select("Export format", EXPORT_FORMATS).ask() or "Zip (.zip)"
    out_dir = questionary.text("Export directory",
                                settings.default_export_dir or "./exports").ask()
    try:
        target = export_project(project, fmt, Path(out_dir) if out_dir else None)
        console.print(f"[{theme.success}]Exported to {target}[/]")
    except (OSError, ValueError) as exc:
        console.print(f"[{theme.danger}]Export failed: {exc}[/]")


def _preview_project(console: Console, theme: Theme) -> None:
    project = _pick_project(console)
    if not project:
        console.print(f"[{theme.warning}]No projects available.[/]")
        return
    mode = questionary.select("Preview mode",
                              ["Run interactive", "Show file tree", "Show main.py",
                               "Run headless smoke test"]).ask() or "Run interactive"
    if mode == "Run interactive":
        console.print(f"[{theme.info}]Launching {project.root.name} ...[/]")
        launch_preview(project, console, theme, timeout=20)
    elif mode == "Show file tree":
        from .ui.prompts import console as _c
        for fp in project.root.rglob("*"):
            if fp.is_file():
                _c.print(fp.relative_to(project.root))
    elif mode == "Show main.py":
        text = (project.root / "main.py").read_text(encoding="utf-8", errors="replace")
        console.print(text)
    else:
        code = launch_preview(project, console, theme, interactive=False, timeout=15)
        console.print(f"[{theme.success}]Headless exit: {code}[/]")


def _themes_view(console: Console, theme: Theme, settings: UserSettings) -> None:
    registry = build_registry()
    while True:
        action = questionary.select("Themes", [
            "Switch active theme", "List themes", "Create custom theme",
            "Delete custom theme", "Back",
        ]).ask()
        if not action or action == "Back":
            return
        if action == "List themes":
            for name in registry.names:
                t = registry.get(name)
                console.print(f"[{theme.primary}]{name}[/] - {t.description}")
        elif action == "Switch active theme":
            new_name = questionary.select("Active theme", registry.names,
                                          default=theme.name).ask()
            if new_name:
                new_theme = registry.get(new_name) or theme
                settings.default_theme = new_name
                save_state(settings)
                console.print(f"[{theme.success}]Active theme: {new_name}[/]")
        elif action == "Create custom theme":
            new_theme = run_theme_creator(console, theme)
            if new_theme:
                console.print(f"[{theme.success}]Created {new_theme.name}[/]")
        elif action == "Delete custom theme":
            targets = [n for n in registry.names if (registry.get(n) and registry.get(n).custom)]
            if not targets:
                console.print(f"[{theme.warning}]No custom themes.[/]")
                continue
            victim = questionary.select("Delete which?", targets).ask()
            if victim and registry.delete_custom_theme(victim):
                console.print(f"[{theme.success}]Deleted {victim}[/]")


def _plugins_view(console: Console, theme: Theme) -> None:
    from .plugins import PLUGINS, plugin_map, load_plugin_state, save_plugin_state
    project = _pick_project(console)
    if not project:
        console.print(f"[{theme.warning}]Open a project first.[/]")
        return
    state = load_plugin_state(project.root)
    while True:
        labels = [f"{'✓' if state[p.key] else '✗'} {p.name}" for p in PLUGINS]
        labels.append("Back")
        action = questionary.select("Plugins", labels).ask()
        if not action or action == "Back":
            save_plugin_state(project.root, state)
            return
        chosen = action.split(" ", 1)[1]
        p = next((pl for pl in PLUGINS if pl.name == chosen), None)
        if p:
            state[p.key] = not state[p.key]
            console.print(f"[{theme.success}]{p.name} is now {'on' if state[p.key] else 'off'}[/]")


def _templates_view(console: Console, theme: Theme) -> None:
    from .categories import TOOL_CATEGORIES
    console.print(Panel(
        "\n".join(f"[{theme.primary}]{cat}[/] - {len(subs)} subcategories"
                  for cat, subs in TOOL_CATEGORIES.items()),
        border_style=theme.border, title=f"[{theme.primary}]Templates[/]",
    ))


def _about_view(console: Console, theme: Theme) -> None:
    from . import __author__, __github__, __instagram__, __version__
    console.print(Panel(
        f"[{theme.primary}]ForgeCLI[/] v{__version__}\n"
        f"[{theme.secondary}]Premium Terminal Tool Builder[/]\n\n"
        f"Author: {__author__}\n"
        f"GitHub: {__github__}\n"
        f"Instagram: {__instagram__}\n\n"
        f"Workspace: {WORKSPACE_DIR}\n"
        f"State dir: {get_state_dir()}",
        border_style=theme.border, title="About ForgeCLI",
    ))


def _edit_project(console: Console, theme: Theme) -> None:
    project = _pick_project(console)
    if not project:
        console.print(f"[{theme.warning}]No projects to edit.[/]")
        return
    from .wizard.branding import run_branding_wizard
    new = run_branding_wizard(theme, load_state(), existing=project.branding)
    if new:
        new.save(project.root / "branding.json")
        console.print(f"[{theme.success}]Branding updated for {project.root.name}[/]")


def run_dashboard(theme: Theme, settings: UserSettings) -> int:
    """Main interactive loop."""
    while True:
        _print_dashboard(theme, settings)
        try:
            choice = questionary.select("Choose an action",
                                          DASHBOARD_OPTIONS).ask()
        except (KeyboardInterrupt, EOFError):
            default_console.print(f"[{theme.muted}]Goodbye.[/]")
            return 0
        if not choice or choice == "Exit":
            default_console.print(f"[{theme.primary}]Bye.[/]")
            return 0
        if choice == "Create New Tool":
            _create_new_tool(default_console, theme, settings)
        elif choice == "Open Existing Project":
            project = _pick_project(default_console)
            if project:
                default_console.print(f"[{theme.success}]Opened {project.root}[/]")
                manage_files(project.root, default_console, theme)
        elif choice == "Edit Project":
            _edit_project(default_console, theme)
        elif choice == "Generate Files":
            _create_new_tool(default_console, theme, settings)
        elif choice == "Export Project":
            _export_project(default_console, theme, settings)
        elif choice == "Preview Tool":
            _preview_project(default_console, theme)
        elif choice == "Themes":
            _themes_view(default_console, theme, settings)
        elif choice == "Plugins":
            _plugins_view(default_console, theme)
        elif choice == "Templates":
            _templates_view(default_console, theme)
        elif choice == "Settings":
            new_settings = manage_settings(default_console, theme)
            settings.default_theme = new_settings.default_theme
        elif choice == "About":
            _about_view(default_console, theme)


__all__ = ["run_dashboard", "DASHBOARD_OPTIONS"]