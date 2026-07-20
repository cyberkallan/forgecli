"""Shared UI helpers built on Rich + questionary."""
from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .theme import Theme


# A single global console so animations, banners, and panels share state.
console = Console()


def styled_panel(content, theme: Theme, *, title: str = "", subtitle: str = "") -> Panel:
    """Wrap ``content`` in a themed panel."""
    return Panel(
        content,
        border_style=theme.border,
        title=f"[{theme.primary}]{title}[/]" if title else None,
        subtitle=f"[{theme.muted}]{subtitle}[/]" if subtitle else None,
        padding=(1, 2),
        expand=True,
    )


def info_line(theme: Theme, label: str, value: str) -> Text:
    return Text.from_markup(
        f"[{theme.secondary}] {label:<18}[/] [{theme.fg}]{value}[/]"
    )


def success(console_: Optional[Console], theme: Theme, msg: str) -> None:
    (console_ or console).print(f"[{theme.success}]✓[/] [{theme.fg}]{msg}[/]")


def warn(console_: Optional[Console], theme: Theme, msg: str) -> None:
    (console_ or console).print(f"[{theme.warning}]![/] [{theme.fg}]{msg}[/]")


def error(console_: Optional[Console], theme: Theme, msg: str) -> None:
    (console_ or console).print(f"[{theme.danger}]✗[/] [{theme.fg}]{msg}[/]")


def ask(message: str, default: str = "") -> str:
    """Ask for a free-text answer."""
    result = questionary.text(message, default=default).ask()
    return result if result is not None else default


def confirm(message: str, default: bool = True) -> bool:
    res = questionary.confirm(message, default=default).ask()
    return bool(res)


def choose(message: str, choices: Sequence[str], *, default: Optional[str] = None) -> Optional[str]:
    """Arrow-key navigable single select."""
    return questionary.select(message, choices=list(choices), default=default).ask()


def choose_multi(message: str, choices: Sequence[str]) -> List[str]:
    return list(questionary.checkbox(message, choices=list(choices)).ask() or [])


__all__ = [
    "console",
    "styled_panel",
    "info_line",
    "success",
    "warn",
    "error",
    "ask",
    "confirm",
    "choose",
    "choose_multi",
]