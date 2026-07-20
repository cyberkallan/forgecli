"""Menu style rendering for the dashboard and generated tools.

The chosen "menu style" affects how a list of options is *displayed*. Selection
itself is always keyboard navigable via ``questionary`` so behaviour stays
consistent across styles.
"""
from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

from rich.table import Table
from rich.text import Text

from .theme import Theme


MENU_STYLES = [
    "Classic",
    "Cyber",
    "Minimal",
    "Professional",
    "Arrow",
    "Icons",
    "Grid",
    "Cards",
    "Animated",
    "Scrollable",
]

_ICON_MAP = {
    "create": "✚", "open": "📂", "edit": "✎", "generate": "⚡", "export": "📦",
    "preview": "▶", "themes": "🎨", "plugins": "🧩", "templates": "📑",
    "settings": "⚙", "about": "ℹ", "exit": "⏻", "default": "•",
}


def _icon_for(label: str) -> str:
    key = label.strip().lower().split()[0]
    return _ICON_MAP.get(key, _ICON_MAP["default"])


def render_menu(style: str, title: str, options: Sequence[str], theme: Theme) -> List[Text]:
    """Return a list of ``rich.Text`` lines representing the menu body."""
    style = style if style in MENU_STYLES else "Cyber"
    lines: List[Text] = []

    if style == "Classic":
        for i, opt in enumerate(options, 1):
            lines.append(Text.from_markup(
                f"[{theme.primary}]{i:>2}.[/] [{theme.fg}]{opt}[/]"))

    elif style == "Cyber":
        for i, opt in enumerate(options, 1):
            lines.append(Text.from_markup(
                f"[{theme.secondary}]╭─[/][{theme.primary}]{i:02d}[/][{theme.secondary}]─╮[/] "
                f"[{theme.fg}]{opt}[/]"))

    elif style == "Minimal":
        for opt in options:
            lines.append(Text.from_markup(f"[{theme.muted}]–[/] [{theme.fg}]{opt}[/]"))

    elif style == "Professional":
        for i, opt in enumerate(options, 1):
            lines.append(Text.from_markup(
                f"[{theme.primary}][{i:>2}][/]  [{theme.fg}]{opt}[/]"))

    elif style == "Arrow":
        for i, opt in enumerate(options, 1):
            lines.append(Text.from_markup(
                f"[{theme.secondary}]▸[/] [{theme.primary}]{i:>2}[/] [{theme.fg}]{opt}[/]"))

    elif style == "Icons":
        for i, opt in enumerate(options, 1):
            icon = _icon_for(opt)
            lines.append(Text.from_markup(
                f"[{theme.primary}]{icon}[/] [{theme.secondary}]{i:>2}[/] [{theme.fg}]{opt}[/]"))

    elif style == "Grid":
        # Two-column grid view.
        half = (len(options) + 1) // 2
        left, right = list(options[:half]), list(options[half:])
        for i in range(half):
            l = Text.from_markup(
                f"[{theme.primary}]{i+1:>2}.[/] [{theme.fg}]{left[i]:<20}[/]")
            if i < len(right):
                r_idx = half + i + 1
                l.append_text(Text.from_markup(
                    f"   [{theme.primary}]{r_idx:>2}.[/] [{theme.fg}]{right[i]}[/]"))
            lines.append(l)

    elif style == "Cards":
        for i, opt in enumerate(options, 1):
            lines.append(Text.from_markup(
                f"[{theme.border}]┌──────┐[/] [{theme.primary}]{i:>2}[/] "
                f"[{theme.fg}]{opt}[/]"))

    elif style == "Animated":
        for i, opt in enumerate(options, 1):
            bar = "▏" * ((i % 3) + 1)
            lines.append(Text.from_markup(
                f"[{theme.secondary}]{bar}[/] [{theme.primary}]{i:>2}[/] [{theme.fg}]{opt}[/]"))

    elif style == "Scrollable":
        for i, opt in enumerate(options, 1):
            marker = "▼" if i == 1 else " "
            lines.append(Text.from_markup(
                f"[{theme.primary}]{marker}[/] [{theme.secondary}]{i:>2}[/] [{theme.fg}]{opt}[/]"))

    return lines


def render_menu_table(style: str, title: str, options: Sequence[str], theme: Theme) -> Table:
    """Render the menu as a rich Table (used by the dashboard header)."""
    table = Table.grid(padding=(0, 2))
    table.add_column(style=theme.primary)
    table.add_column(style=theme.fg)
    for line in render_menu(style, title, options, theme):
        table.add_row(Text(" "), line)
    return table


__all__ = ["MENU_STYLES", "render_menu", "render_menu_table"]