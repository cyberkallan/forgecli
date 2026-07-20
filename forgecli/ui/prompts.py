"""Shared UI helpers built on Rich + questionary.

All interactive prompts in ForgeCLI go through this module so we can:
  * style questionary with a bold, theme-aware prompt_toolkit ``Style``
  * print a big Rich header line above every prompt (keeps the menu readable
    on Termux and other terminals where the prompt_toolkit widget renders small)
  * guard ``default=`` against the choice list so a stale default never crashes
"""
from __future__ import annotations

from typing import List, Optional, Sequence

import questionary
from questionary import Style
from rich.console import Console
from rich.panel import Panel

from .theme import Theme


# A single global console so animations, banners, and panels share state.
console = Console()


# ---------------------------------------------------------------------------
# prompt_toolkit color helpers
# ---------------------------------------------------------------------------

# Map the common Rich color names we use across themes to prompt_toolkit's
# ``ansi*`` spec. prompt_toolkit accepts ``fg:#rrggbb`` for hex, ``fg:cyan``
# for base ANSI, and ``fg:ansibrightcyan`` for bright variants.
_PT_BASIC = {
    "black": "ansiwhite",      # readable on dark consoles
    "red": "ansired",
    "green": "ansigreen",
    "yellow": "ansiyellow",
    "blue": "ansiblue",
    "magenta": "ansimagenta",
    "cyan": "ansicyan",
    "white": "ansiwhite",
    "grey": "ansibrightblack",
    "gray": "ansibrightblack",
    "default": "default",
}
_PT_BRIGHT = {
    "bright_red": "ansibrightred",
    "bright_green": "ansibrightgreen",
    "bright_yellow": "ansibrightyellow",
    "bright_blue": "ansibrightblue",
    "bright_magenta": "ansibrightmagenta",
    "bright_cyan": "ansibrightcyan",
    "bright_white": "ansiwhite",
    "bright_black": "ansibrightblack",
}


def _pt_color(color: Optional[str], *, default: str = "ansicyan") -> str:
    """Convert a Rich theme color to a prompt_toolkit color spec.

    Hex like ``#00fff5`` passes through unchanged. Named Rich colors are
    mapped to ANSI equivalents; anything unknown falls back to ``default``.
    """
    if not color:
        return default
    color = str(color).strip()
    if not color:
        return default
    if color.startswith("#") and len(color) in (4, 7, 9):
        return color
    key = color.lower().replace(" ", "")
    if key in _PT_BRIGHT:
        return _PT_BRIGHT[key]
    if key in _PT_BASIC:
        return _PT_BASIC[key]
    # Best-effort: strip non-alphanumeric and try again
    bare = "".join(ch for ch in key if ch.isalpha())
    if bare in _PT_BRIGHT:
        return _PT_BRIGHT[bare]
    if bare in _PT_BASIC:
        return _PT_BASIC[bare]
    return default


_DEFAULT_STYLE = Style([
    ("qmark", "fg:ansicyan bold"),
    ("question", "fg:ansicyan bold"),
    ("pointer", "fg:ansicyan bold"),
    ("highlighted", "fg:ansicyan bold"),
    ("selected", "fg:ansicyan bold"),
    ("answer", "fg:ansigreen bold"),
    ("instruction", "fg:ansibrightblack"),
    ("text", ""),
    ("separator", "fg:ansibrightblack"),
])


def _style_for(theme: Optional[Theme]) -> Style:
    """Build a prompt_toolkit Style themed with ``theme`` (or the default)."""
    if theme is None:
        return _DEFAULT_STYLE
    primary = _pt_color(getattr(theme, "primary", None), default="ansicyan")
    secondary = _pt_color(getattr(theme, "secondary", None), default="ansimagenta")
    success = _pt_color(getattr(theme, "success", None), default="ansigreen")
    muted = _pt_color(getattr(theme, "muted", None), default="ansibrightblack")
    fg = _pt_color(getattr(theme, "fg", None), default="default")
    return Style([
        ("qmark", f"fg:{primary} bold"),
        ("question", f"fg:{secondary} bold"),
        ("pointer", f"fg:{primary} bold"),
        ("highlighted", f"fg:{primary} bold"),
        ("selected", f"fg:{success} bold"),
        ("answer", f"fg:{success} bold"),
        ("instruction", f"fg:{muted}"),
        ("text", f"fg:{fg}"),
        ("separator", f"fg:{muted}"),
    ])


def _print_header(message: str, theme: Optional[Theme]) -> None:
    """Render a big themed header above the prompt so it's visible even when
    the prompt_toolkit widget itself is compact."""
    if theme is None:
        console.print(f"\n[bold ansicyan]❯ {message}[/]")
        return
    primary = getattr(theme, "primary", "cyan") or "cyan"
    secondary = getattr(theme, "secondary", "white") or "white"
    console.print(f"\n[bold {primary}]❯[/] [bold {secondary}]{message}[/]")


# ---------------------------------------------------------------------------
# Prompt helpers
# ---------------------------------------------------------------------------

def ask(message: str, default: str = "", *, theme: Optional[Theme] = None) -> str:
    """Ask for a free-text answer, with a themed header and styled prompt."""
    _print_header(message, theme)
    result = questionary.text(message, default=default or "",
                              style=_style_for(theme)).ask()
    return result if result is not None else (default or "")


def confirm(message: str, default: bool = True, *,
            theme: Optional[Theme] = None) -> bool:
    _print_header(message, theme)
    res = questionary.confirm(message, default=default,
                              style=_style_for(theme)).ask()
    return bool(res)


def choose(message: str, choices: Sequence[str], *, default: Optional[str] = None,
           theme: Optional[Theme] = None) -> Optional[str]:
    """Arrow-key navigable single select.

    ``default`` is guarded against ``choices`` so a stale default never crashes
    the prompt (this is what used to blow up the dashboard when switching
    categories in the wizard).
    """
    if not choices:
        return None
    safe_default = default if default in choices else None
    _print_header(message, theme)
    return questionary.select(message, choices=list(choices),
                              default=safe_default,
                              style=_style_for(theme)).ask()


def choose_multi(message: str, choices: Sequence[str], *,
                 theme: Optional[Theme] = None) -> List[str]:
    _print_header(message, theme)
    return list(questionary.checkbox(message, choices=list(choices),
                                     style=_style_for(theme)).ask() or [])


# ---------------------------------------------------------------------------
# Styled panel helper (re-exported for convenience)
# ---------------------------------------------------------------------------

def styled_panel(content, theme: Optional[Theme] = None, *,
                 title: str = "", subtitle: str = "") -> Panel:
    """Wrap ``content`` in a themed panel."""
    border = _pt_color(getattr(theme, "border", None), default="ansibrightblack")
    return Panel(
        content,
        border_style=border if theme else "ansibrightblack",
        title=f"[{getattr(theme, 'primary', 'cyan')}]{title}[/]" if title else None,
        subtitle=f"[{getattr(theme, 'muted', 'bright_black')}]{subtitle}[/]"
                 if subtitle else None,
        padding=(1, 2),
        expand=True,
    )


__all__ = [
    "console",
    "styled_panel",
    "ask",
    "confirm",
    "choose",
    "choose_multi",
]
