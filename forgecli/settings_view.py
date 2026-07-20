"""Settings view: edit UserSettings interactively."""
from __future__ import annotations

from pathlib import Path

import questionary
from rich.console import Console
from rich.panel import Panel

from .core.config import UserSettings, load_state, save_state
from .ui.theme import build_registry

_TOGGLES = ["auto_save", "auto_backup"]


def manage_settings(console: Console, theme) -> UserSettings:
    settings = load_state()
    while True:
        console.print(Panel(_settings_block(settings, theme),
                            border_style=theme.border,
                            title=f"[{theme.primary}]Settings[/]"))
        action = questionary.select(
            "Action",
            choices=[
                "Set author", "Set GitHub", "Set Instagram",
                "Set default theme", "Set default license",
                "Set default export folder", "Set animation speed",
                "Set update channel", "Toggle auto save",
                "Toggle auto backup", "Save & Exit", "Discard & Exit",
            ],
        ).ask()
        if not action:
            return settings
        if action == "Save & Exit":
            save_state(settings)
            console.print(f"[{theme.success}]Settings saved.[/]")
            return settings
        if action == "Discard & Exit":
            return load_state()
        _handle(action, settings, console, theme)


def _handle(action: str, settings: UserSettings, console: Console, theme) -> None:
    if action == "Set author":
        settings.default_author = questionary.text("Author", settings.default_author).ask() or settings.default_author
    elif action == "Set GitHub":
        settings.default_github = questionary.text("GitHub URL", settings.default_github).ask() or settings.default_github
    elif action == "Set Instagram":
        settings.default_instagram = questionary.text("Instagram URL", settings.default_instagram).ask() or settings.default_instagram
    elif action == "Set default theme":
        names = build_registry().names
        settings.default_theme = questionary.select("Theme", names, default=settings.default_theme).ask() or settings.default_theme
    elif action == "Set default license":
        settings.default_license = questionary.select(
            "License", ["MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause", "ISC"],
            default=settings.default_license,
        ).ask() or settings.default_license
    elif action == "Set default export folder":
        path = questionary.text("Export folder", settings.default_export_dir).ask()
        if path:
            Path(path).mkdir(parents=True, exist_ok=True)
            settings.default_export_dir = path
    elif action == "Set animation speed":
        speed = questionary.text("Animation speed (0.5 - 2.0)", str(settings.animation_speed)).ask()
        try:
            settings.animation_speed = float(speed)
        except (TypeError, ValueError):
            console.print(f"[{theme.warning}]Invalid number, kept {settings.animation_speed}.[/]")
    elif action == "Set update channel":
        settings.update_channel = questionary.select(
            "Update channel", ["stable", "beta", "nightly"],
            default=settings.update_channel,
        ).ask() or settings.update_channel
    elif action == "Toggle auto save":
        settings.auto_save = not settings.auto_save
    elif action == "Toggle auto backup":
        settings.auto_backup = not settings.auto_backup


def _settings_block(s: UserSettings, theme) -> str:
    rows = [
        ("Author", s.default_author),
        ("GitHub", s.default_github),
        ("Instagram", s.default_instagram),
        ("License", s.default_license),
        ("Theme", s.default_theme),
        ("Export folder", s.default_export_dir),
        ("Animation speed", f"{s.animation_speed:.2f}x"),
        ("Update channel", s.update_channel),
        ("Auto save", "on" if s.auto_save else "off"),
        ("Auto backup", "on" if s.auto_backup else "off"),
    ]
    return "\n".join(f"[{theme.secondary}]{label:<18}[/][{theme.fg}] {value}[/]"
                     for label, value in rows)


__all__ = ["manage_settings"]