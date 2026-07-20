"""UI helpers - prompts, panels, and the startup animation bridge.

All interactive prompts go through ``ask``/``confirm``/``choose`` so they share
a bold, theme-aware prompt_toolkit style and a big Rich header line above each
prompt (keeps menus readable on Termux and other compact terminals).
"""
from __future__ import annotations

import time
from typing import Optional

import questionary
from questionary import Style
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


# A single shared console for the generated tool.
_console = Console()


# ---------------------------------------------------------------------------
# prompt_toolkit color/style helpers
# ---------------------------------------------------------------------------

_PT_BASIC = {
    "black": "ansiwhite", "red": "ansired", "green": "ansigreen",
    "yellow": "ansiyellow", "blue": "ansiblue", "magenta": "ansimagenta",
    "cyan": "ansicyan", "white": "ansiwhite", "grey": "ansibrightblack",
    "gray": "ansibrightblack", "default": "default",
}
_PT_BRIGHT = {
    "bright_red": "ansibrightred", "bright_green": "ansibrightgreen",
    "bright_yellow": "ansibrightyellow", "bright_blue": "ansibrightblue",
    "bright_magenta": "ansibrightmagenta", "bright_cyan": "ansibrightcyan",
    "bright_white": "ansiwhite", "bright_black": "ansibrightblack",
}


def _pt_color(color, *, default="ansicyan"):
    """Convert a Rich theme color to a prompt_toolkit color spec."""
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
    bare = "".join(ch for ch in key if ch.isalpha())
    if bare in _PT_BRIGHT:
        return _PT_BRIGHT[bare]
    if bare in _PT_BASIC:
        return _PT_BASIC[bare]
    return default


def _style_for(theme):
    """Build a prompt_toolkit Style themed with ``theme``."""
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


def _print_header(message, theme):
    """Render a big themed header above the prompt."""
    primary = getattr(theme, "primary", "cyan") or "cyan"
    secondary = getattr(theme, "secondary", "white") or "white"
    _console.print(f"\n[bold {primary}]❯[/] [bold {secondary}]{message}[/]")


# ---------------------------------------------------------------------------
# Prompt helpers
# ---------------------------------------------------------------------------

def ask(message: str, default: str = "", theme=None) -> str:
    _print_header(message, theme)
    res = questionary.text(message, default=default or "",
                           style=_style_for(theme)).ask()
    return res if res is not None else (default or "")


def confirm(message: str, default: bool = True, theme=None) -> bool:
    _print_header(message, theme)
    return bool(questionary.confirm(message, default=default,
                                    style=_style_for(theme)).ask())


def choose(message: str, choices, default: Optional[str] = None,
           theme=None) -> Optional[str]:
    """Arrow-key single select. ``default`` is guarded against ``choices``."""
    if not choices:
        return None
    safe_default = default if default in choices else None
    _print_header(message, theme)
    return questionary.select(message, choices=list(choices),
                              default=safe_default,
                              style=_style_for(theme)).ask()


def select_menu(title: str, options, *, theme, default: Optional[str] = None):
    """Big themed menu for the main command loop.

    Renders a decorative Rich header panel (via ``render_menu``) and then an
    arrow-key navigable, styled ``questionary.select``. Returns the chosen
    label or ``None`` on cancel.
    """
    render_menu(theme)
    return choose(title, options, default=default, theme=theme)


def panel(content, theme, *, title: str = "", subtitle: str = "") -> Panel:
    return Panel(
        content if isinstance(content, str) else content,
        border_style=getattr(theme, "border", "cyan") or "cyan",
        title=f"[{getattr(theme, 'primary', 'cyan')}]{title}[/]" if title else None,
        subtitle=f"[{getattr(theme, 'muted', 'bright_black')}]{subtitle}[/]"
                 if subtitle else None,
        padding=(1, 2),
    )


def make_ctx(console: Console, theme, **extra) -> dict:
    """Build the command context. ``ask``/``confirm``/``choose`` are bound to
    ``theme`` so every command prompt is styled, while keeping the simple
    ``ctx['ask']('Host', '127.0.0.1')`` call signature commands already use."""
    return {
        "console": console,
        "theme": theme,
        "ask": lambda message, default="": ask(message, default, theme=theme),
        "confirm": lambda message, default=True: confirm(message, default, theme=theme),
        "choose": lambda message, choices, default=None: choose(message, choices,
                                                                  default=default,
                                                                  theme=theme),
        "panel": lambda c, **kw: panel(c, theme, **kw),
        **extra,
    }


def info_table(console: Console, theme, info) -> None:
    table = Table.grid(padding=(0, 1))
    table.add_column(style=theme.muted)
    table.add_column(style=theme.fg)
    rows = [
        ("Project", "{{PROJECT_NAME}}"),
        ("Version", "{{VERSION}}"),
        ("Category", "{{CATEGORY}} / {{SUBCATEGORY}}"),
        ("Author", "{{AUTHOR}}"),
        ("GitHub", "{{GITHUB}}"),
        ("Python", info.python_version),
        ("Terminal", info.terminal_size),
        ("CWD", info.current_dir),
        ("Network", info.network_status),
        ("Git", info.git_status),
    ]
    for label, value in rows:
        table.add_row(f" {label} ", str(value))
    console.print(panel(table, theme, title="System"))


MENU_STYLES = ["Cyber", "Classic", "Minimal", "Professional", "Arrow",
               "Icons", "Grid", "Cards", "Animated", "Scrollable"]
STARTUP_ANIMATIONS = ["Spinner", "Cyber Loading", "Progress Bar", "Dots",
                      "Matrix Rain", "Hex Animation", "Binary Animation",
                      "Circuit Animation", "Neon Pulse", "Terminal Boot",
                      "Boot Loader", "Retro BIOS"]
LOADING_ANIMATIONS = STARTUP_ANIMATIONS


def render_menu(theme):
    _console.print(Panel(
        f"[{theme.secondary}]{{PROJECT_NAME}}[/] · [{theme.muted}]v{{VERSION}}[/]\n"
        f"[{theme.info}]{{SUBCATEGORY}} · {{CATEGORY}}[/]",
        border_style=theme.border,
        title=f"[{theme.primary}]◆[/] [{theme.secondary}]Dashboard[/]",
        padding=(0, 2),
    ))
    return None


def _frame(console: Console, theme, message: str, style: str, spinner_name: str) -> None:
    from rich.spinner import Spinner
    from rich.live import Live

    if style == "Matrix Rain":
        chars = "abcdef0123456789$#@!"
        import random
        height = max(6, min(12, console.size.height - 4))
        width = max(10, min(40, console.size.width // 2))
        cols = [random.randint(-height, 0) for _ in range(width)]
        end = time.time() + 0.6
        with Live(console=console, refresh_per_second=20, transient=True) as live:
            while time.time() < end:
                lines = []
                for y in range(height):
                    row = []
                    for x in range(width):
                        if y == cols[x]:
                            row.append(f"[{theme.fg}]{random.choice(chars)}[/]")
                        elif 0 < cols[x] - y < 5:
                            row.append(f"[{theme.primary}]{random.choice(chars)}[/]")
                        else:
                            row.append(" ")
                    lines.append("".join(row))
                live.update(Text("\n".join(lines)))
                for i in range(width):
                    cols[i] += 1
                    if cols[i] > height + 5:
                        cols[i] = random.randint(-height, 0)
                time.sleep(0.05)
        return
    if style == "Progress Bar":
        from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, SpinnerColumn
        progress = Progress(SpinnerColumn(), TextColumn(f"[{theme.primary}]{{task.description}}"),
                            BarColumn(complete_style=theme.primary, finished_style=theme.success),
                            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                            TimeElapsedColumn(), console=console, transient=True)
        task = progress.add_task(message, total=100)
        with progress:
            for i in range(101):
                progress.update(task, completed=i)
                time.sleep(0.006)
        return
    if style == "Cyber Loading":
        from rich.live import Live
        n = 24
        end = time.time() + 0.6
        with Live(console=console, refresh_per_second=20, transient=True) as live:
            while time.time() < end:
                filled = int((time.time() % 0.6) / 0.6 * n)
                bar = "".join(f"[{theme.primary}]█[/]" if i < filled else f"[{theme.muted}]▁[/]" for i in range(n))
                live.update(Text.from_markup(f"[{theme.secondary}]{message}[/]\n{bar}"))
                time.sleep(0.05)
        return
    spinner = Spinner(spinner_name, text=f"[{theme.primary}]{message}[/]")
    with Live(spinner, console=console, refresh_per_second=15, transient=True):
        time.sleep(0.6)


_SPINNER_NAMES = {
    "dots": "dots", "dots2": "dots2", "dots12": "dots12",
    "arc": "arc", "clock": "clock", "moon": "moon",
    "bouncingBar": "bouncingBar",
}


def run_startup_animation(console: Console, theme, *, animation: str = "Cyber Loading") -> None:
    steps = ["Loading modules", "Checking environment",
             "Detecting operating system", "Loading UI", "Ready"]
    spinner = _SPINNER_NAMES.get("{{SPINNER_TYPE}}", "dots")
    for step in steps:
        _frame(console, theme, step, animation, spinner)
        console.print()


def run_loading_animation(console: Console, theme, message: str, animation: str = "Cyber Loading") -> None:
    spinner = _SPINNER_NAMES.get("{{SPINNER_TYPE}}", "dots")
    _frame(console, theme, message, animation, spinner)