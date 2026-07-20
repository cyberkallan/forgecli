"""Loading / startup animations for ForgeCLI.

Every animation is a small, self-contained generator of frames rendered with
``rich.live``. They are deliberately resilient: a frame that cannot render
falls back to a plain progress message so the UI never crashes.
"""
from __future__ import annotations

import random
import string
import time
from typing import Callable, Iterator, List, Optional, Sequence

from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.spinner import Spinner
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.text import Text

from ..core.logging_utils import get_logger
from .theme import Theme

_LOG = get_logger("ui.animations")


def _fps_to_interval(speed: float) -> float:
    """Convert an animation speed multiplier into a sleep interval (seconds)."""
    speed = max(0.1, float(speed) or 1.0)
    return max(0.01, 0.12 / speed)


def _run_frames(
    console: Console,
    frame_fn: Callable[[int], object],
    duration: float,
    speed: float,
) -> None:
    """Render frames produced by ``frame_fn(i)`` for ``duration`` seconds."""
    interval = _fps_to_interval(speed)
    end = time.monotonic() + duration
    i = 0
    try:
        with Live(frame_fn(i), console=console, refresh_per_second=int(1 / interval),
                   screen=False, transient=True) as live:
            while time.monotonic() < end:
                live.update(frame_fn(i))
                i += 1
                time.sleep(interval)
    except Exception as exc:  # pragma: no cover - defensive
        _LOG.debug("Animation interrupted: %s", exc)


# ---- Individual animations -------------------------------------------------

def spinner_animation(console: Console, theme: Theme, duration: float, message: str,
                     speed: float = 1.0) -> None:
    spinner_name = {"Cyberpunk": "dots12", "Matrix": "dots", "Green Hacker": "dots"}.get(
        theme.name, "dots")
    def frame(i: int) -> object:
        spinner = Spinner(spinner_name, text=f"[{theme.primary}]{message}[/]")
        return Group(spinner, Text(f"  frame {i}", style=theme.muted))
    _run_frames(console, frame, duration, speed)


def progress_bar_animation(console: Console, theme: Theme, duration: float, message: str,
                           speed: float = 1.0) -> None:
    progress = Progress(
        SpinnerColumn(),
        TextColumn(f"[{theme.primary}]{{task.description}}"),
        BarColumn(complete_style=theme.primary, finished_style=theme.success),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    )
    task_id = progress.add_task(message, total=100)
    end = time.monotonic() + duration
    interval = _fps_to_interval(speed)
    try:
        with Live(progress, console=console, refresh_per_second=int(1 / interval),
                  transient=True) as live:
            while time.monotonic() < end:
                elapsed = duration - (end - time.monotonic())
                pct = min(100.0, (elapsed / duration) * 100.0)
                progress.update(task_id, completed=pct)
                live.refresh()
                time.sleep(interval)
            progress.update(task_id, completed=100.0)
    except Exception as exc:  # pragma: no cover
        _LOG.debug("Progress animation interrupted: %s", exc)


def dots_animation(console: Console, theme: Theme, duration: float, message: str,
                   speed: float = 1.0) -> None:
    base = message.rstrip(". ")
    def frame(i: int) -> object:
        dots = "." * (i % 4)
        return Text(f"[{theme.primary}]{base}[/][{theme.secondary}]{dots}[/]",
                    style=theme.primary)
    _run_frames(console, frame, duration, speed)


def _rain_frame(width: int, height: int, columns: List[List[int]],
                chars: str, theme: Theme) -> Text:
    lines: List[str] = []
    for y in range(height):
        row = []
        for x in range(width):
            col = columns[x]
            head = col[0]
            trail = col[1]
            if y == head:
                row.append(f"[{theme.fg}] {chars[(x + y) % len(chars)]}[/]")
            elif 0 <= head - y < 6:
                intensity = 6 - (head - y)
                row.append(f"[{theme.primary}] {chars[(x * 3 + y) % len(chars)]}[/]")
            else:
                row.append("  ")
            col[:] = [head + (1 if y == height - 1 else 0), trail]
        lines.append("".join(row))
    # advance columns
    for col in columns:
        col[0] = (col[0] + 1) % (height + 6)
    return Text("\n".join(lines[:height]), style=theme.primary)


def matrix_rain_animation(console: Console, theme: Theme, duration: float, message: str,
                          speed: float = 1.0) -> None:
    size = console.size
    width = max(10, min(40, size.width // 2))
    height = max(6, min(14, size.height - 4))
    chars = string.ascii_letters + string.digits + "@#$%&"
    columns = [[random.randint(-height, 0), 0] for _ in range(width)]

    def frame(i: int) -> object:
        text = _rain_frame(width, height, columns, chars, theme)
        return Panel(text, border_style=theme.border,
                     title=f"[{theme.secondary}]{message}[/]")

    _run_frames(console, frame, duration, speed)


def hex_animation(console: Console, theme: Theme, duration: float, message: str,
                  speed: float = 1.0) -> None:
    def frame(i: int) -> object:
        rows = []
        for r in range(4):
            line = " ".join(f"{random.randint(0, 0xFF):02x}" for _ in range(16))
            rows.append(f"[{theme.primary}]{line}[/]")
        body = "\n".join(rows)
        return Panel(Text.from_markup(body), border_style=theme.border,
                     title=f"[{theme.secondary}]{message}[/]")
    _run_frames(console, frame, duration, speed)


def binary_animation(console: Console, theme: Theme, duration: float, message: str,
                     speed: float = 1.0) -> None:
    def frame(i: int) -> object:
        rows = []
        for _ in range(6):
            line = " ".join(random.choice("01") for _ in range(32))
            rows.append(f"[{theme.primary}]{line}[/]")
        return Panel(Text.from_markup("\n".join(rows)), border_style=theme.border,
                     title=f"[{theme.secondary}]{message}[/]")
    _run_frames(console, frame, duration, speed)


def circuit_animation(console: Console, theme: Theme, duration: float, message: str,
                      speed: float = 1.0) -> None:
    glyphs = "╭─╮│╰─╯┤├┬┴┼"
    width = max(20, min(48, console.size.width - 4))
    def frame(i: int) -> object:
        rows = []
        for _ in range(5):
            line = "".join(random.choice(glyphs) for _ in range(width))
            rows.append(f"[{theme.primary}]{line}[/]")
        return Panel(Text.from_markup("\n".join(rows)), border_style=theme.border,
                     title=f"[{theme.secondary}]{message}[/]")
    _run_frames(console, frame, duration, speed)


def neon_pulse_animation(console: Console, theme: Theme, duration: float, message: str,
                         speed: float = 1.0) -> None:
    palette = theme.gradient or [theme.primary, theme.secondary]
    def frame(i: int) -> object:
        color = palette[i % len(palette)]
        glow = f"[{color} on {theme.bg}]  ✦  {message}  ✦  [/]"
        return Text.from_markup(glow, justify="center")
    _run_frames(console, frame, duration, speed)


def cyber_loading_animation(console: Console, theme: Theme, duration: float, message: str,
                            speed: float = 1.0) -> None:
    blocks = "▁▂▃▄▅▆▇█"
    def frame(i: int) -> object:
        n = 12
        filled = (i // 2) % (n + 1)
        bar = "".join(f"[{theme.primary}]█[/]" if j < filled else f"[{theme.muted}]▁[/]"
                      for j in range(n))
        pct = int((filled / n) * 100)
        return Text.from_markup(
            f"[{theme.secondary}]{message}[/]\n[{theme.primary}]{bar}[/] [{theme.info}]{pct:>3}%[/]"
        )
    _run_frames(console, frame, duration, speed)


def terminal_boot_animation(console: Console, theme: Theme, duration: float, message: str,
                            speed: float = 1.0) -> None:
    lines_pool = [
        "BIOS v2.4.1 ForgeCLI (c) 2026",
        "CPU: {cpu} OK",
        "Memory test: 65536K OK",
        "Detecting IDE devices...",
        "Loading kernel modules...",
        "Mounting filesystems...",
        "Starting network services...",
        message,
    ]
    def frame(i: int) -> object:
        visible = lines_pool[: min(len(lines_pool), i // 3 + 1)]
        body = "\n".join(f"[{theme.success}]>[/] [{theme.fg}]{ln}[/]" for ln in visible)
        return Panel(Text.from_markup(body), border_style=theme.border,
                     title=f"[{theme.primary}]ForgeCLI Boot[/]")
    _run_frames(console, frame, duration, speed)


def boot_loader_animation(console: Console, theme: Theme, duration: float, message: str,
                           speed: float = 1.0) -> None:
    def frame(i: int) -> object:
        stages = ["GRUB", "kernel", "initramfs", "userspace", message]
        active = min(len(stages) - 1, i // 4)
        rows = []
        for idx, stage in enumerate(stages):
            if idx < active:
                mark = f"[{theme.success}]✓[/]"
            elif idx == active:
                mark = f"[{theme.primary}]●[/]"
            else:
                mark = f"[{theme.muted}]○[/]"
            rows.append(f"{mark} [{theme.fg}]{stage}[/]")
        return Panel(Text.from_markup("\n".join(rows)), border_style=theme.border)
    _run_frames(console, frame, duration, speed)


def retro_bios_animation(console: Console, theme: Theme, duration: float, message: str,
                         speed: float = 1.0) -> None:
    def frame(i: int) -> object:
        pct = min(100, (i * 5) % 105)
        bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
        body = (f"[{theme.success}]Phoenix BIOS 4.0[/]\n"
                f"[{theme.fg}]POST memory check:[/]\n"
                f"[{theme.primary}]{bar}[/] [{theme.info}]{pct}%[/]\n"
                f"[{theme.warning}]Press DEL to enter SETUP[/]")
        return Panel(Text.from_markup(body), border_style=theme.border,
                     title=f"[{theme.secondary}]RETRO BIOS[/]")
    _run_frames(console, frame, duration, speed)


def custom_animation(console: Console, theme: Theme, duration: float, message: str,
                     speed: float = 1.0) -> None:
    """A configurable animation driven by the user's chosen glyphs and palette."""
    glyphs = theme.extras.get("custom_glyphs", "◆◇◈◉●○") if hasattr(theme, "extras") else "◆◇◈◉●○"
    palette = theme.gradient or [theme.primary, theme.secondary]
    def frame(i: int) -> object:
        color = palette[i % len(palette)]
        glyph = glyphs[i % len(glyphs)]
        return Text.from_markup(f"[{color}]{glyph * (1 + i % 5)}[/]  [{theme.fg}]{message}[/]")
    _run_frames(console, frame, duration, speed)


def typewriter_animation(console: Console, theme: Theme, duration: float, message: str,
                          speed: float = 1.0) -> None:
    """Reveal ``message`` one character at a time, then hold."""
    interval = max(0.02, _fps_to_interval(speed) / 3)
    full = message + "  ▍"
    def frame(i: int) -> object:
        n = min(len(full), i + 1)
        shown = full[:n] + ("▍" if n < len(full) else "")
        return Text.from_markup(f"[{theme.primary}]{shown}[/]")
    end = time.monotonic() + duration
    i = 0
    try:
        with Live(frame_fn_result(frame, i), console=console, refresh_per_second=int(1 / interval),
                   transient=True) as live:
            while time.monotonic() < end:
                live.update(frame(i))
                i += 1
                time.sleep(interval)
    except Exception as exc:  # pragma: no cover
        _LOG.debug("Typewriter interrupted: %s", exc)


def frame_fn_result(frame, i):
    return frame(i)


def glitch_text_animation(console: Console, theme: Theme, duration: float, message: str,
                            speed: float = 1.0) -> None:
    """Flicker ``message`` with glitchy replacement characters."""
    glitch = "▓▒░§¶∞∆◊≈≠"
    def frame(i: int) -> object:
        out = []
        for ch in message:
            if ch != " " and i % 5 == 0 and random.random() < 0.3:
                out.append(random.choice(glitch))
            else:
                out.append(ch)
        return Text.from_markup(f"[{theme.primary}]{''.join(out)}[/]",
                                 justify="center")
    _run_frames(console, frame, duration, speed)


def scanlines_animation(console: Console, theme: Theme, duration: float, message: str,
                         speed: float = 1.0) -> None:
    """CRT scanlines sweeping over a message."""
    h = max(6, min(12, console.size.height - 4))
    def frame(i: int) -> object:
        sweep = i % h
        rows = []
        for y in range(h):
            line = ("█" * 30) if y == sweep else ("▒" * 30 if (y + i) % 3 == 0 else " " * 30)
            rows.append(f"[{theme.primary}]{line}[/]")
        rows[h // 2] = f"[{theme.secondary}]{message.center(30)}[/]"
        return Panel(Text.from_markup("\n".join(rows)), border_style=theme.border)
    _run_frames(console, frame, duration, speed)


def crt_flicker_animation(console: Console, theme: Theme, duration: float, message: str,
                           speed: float = 1.0) -> None:
    """Flicker the message like a fading CRT."""
    palette = [theme.primary, theme.secondary, theme.muted]
    def frame(i: int) -> object:
        color = palette[(i + (1 if random.random() < 0.2 else 0)) % len(palette)]
        return Text.from_markup(f"[{color}]{message}[/]", justify="center")
    _run_frames(console, frame, duration, speed)


def fireworks_animation(console: Console, theme: Theme, duration: float, message: str,
                         speed: float = 1.0) -> None:
    """Burst fireworks made of theme glyphs."""
    sparks = "*+•.✦✧"
    palette = theme.gradient or [theme.primary, theme.secondary, theme.success]
    def frame(i: int) -> object:
        rows = []
        for _ in range(6):
            line = "".join(random.choice(sparks) if random.random() < 0.4 else " "
                           for _ in range(36))
            color = palette[random.randrange(len(palette))]
            rows.append(f"[{color}]{line}[/]")
        rows[5] = f"[{theme.secondary}]{message.center(36)}[/]"
        return Panel(Text.from_markup("\n".join(rows)), border_style=theme.border)
    _run_frames(console, frame, duration, speed)


def snow_animation(console: Console, theme: Theme, duration: float, message: str,
                    speed: float = 1.0) -> None:
    """Gentle snowfall over a message."""
    flakes = "❄❅❆✻"
    def frame(i: int) -> object:
        rows = []
        for _ in range(6):
            line = "".join(random.choice(flakes) if random.random() < 0.25 else " "
                           for _ in range(36))
            rows.append(f"[{theme.fg}]{line}[/]")
        rows[3] = f"[{theme.primary}]{message.center(36)}[/]"
        return Panel(Text.from_markup("\n".join(rows)), border_style=theme.border)
    _run_frames(console, frame, duration, speed)


def ascii_wave_animation(console: Console, theme: Theme, duration: float, message: str,
                          speed: float = 1.0) -> None:
    """A sine-wave of glyphs scrolling across."""
    import math
    width = max(30, min(60, console.size.width - 4))
    def frame(i: int) -> object:
        rows = []
        for y in range(5):
            line = []
            for x in range(width):
                v = math.sin((x + i) * 0.3 + y * 0.6)
                if v > 0.6:
                    line.append(f"[{theme.primary}]█[/]")
                elif v > 0:
                    line.append(f"[{theme.secondary}]▄[/]")
                else:
                    line.append(" ")
            rows.append("".join(line))
        rows.append(f"[{theme.info}]{message}[/]")
        return Text.from_markup("\n".join(rows))
    _run_frames(console, frame, duration, speed)


# ---- Registry --------------------------------------------------------------

ANIMATIONS = {
    "Spinner": spinner_animation,
    "Progress Bar": progress_bar_animation,
    "Dots": dots_animation,
    "Cyber Loading": cyber_loading_animation,
    "Matrix Rain": matrix_rain_animation,
    "Hex Animation": hex_animation,
    "Binary Animation": binary_animation,
    "Circuit Animation": circuit_animation,
    "Neon Pulse": neon_pulse_animation,
    "Terminal Boot": terminal_boot_animation,
    "Boot Loader": boot_loader_animation,
    "Retro BIOS": retro_bios_animation,
    "Typewriter": typewriter_animation,
    "Glitch Text": glitch_text_animation,
    "Scanlines": scanlines_animation,
    "CRT Flicker": crt_flicker_animation,
    "Fireworks": fireworks_animation,
    "Snow": snow_animation,
    "ASCII Wave": ascii_wave_animation,
    "Custom Animation": custom_animation,
}

ANIMATION_NAMES = list(ANIMATIONS.keys())


def play_animation(name: str, console: Console, theme: Theme, duration: float,
                  message: str, speed: float = 1.0) -> None:
    """Dispatch to the named animation, falling back to spinner if unknown."""
    fn = ANIMATIONS.get(name, spinner_animation)
    fn(console, theme, max(0.4, duration), message, speed)


# ---- Startup sequence -------------------------------------------------------

STARTUP_STEPS = [
    "Loading modules",
    "Checking environment",
    "Detecting operating system",
    "Installing dependencies",
    "Loading UI",
    "Ready",
]


def run_startup_sequence(console: Console, theme: Theme, *,
                        per_step: float = 0.5,
                        animation: str = "Cyber Loading",
                        speed: float = 1.0) -> None:
    """Play the animated 'Loading modules ... Ready' startup banner."""
    for step in STARTUP_STEPS:
        play_animation(animation, console, theme, per_step, step, speed)
        console.print()


__all__ = [
    "ANIMATIONS",
    "ANIMATION_NAMES",
    "play_animation",
    "run_startup_sequence",
    "STARTUP_STEPS",
]