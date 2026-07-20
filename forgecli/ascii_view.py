"""ASCII generator view with live preview before saving."""
from __future__ import annotations

import os
from pathlib import Path

import questionary
from rich.console import Console
from rich.panel import Panel

from .core.config import get_state_dir
from .ui.banners import (
    STYLE_PRESETS, FIGLET_FONTS, available_fonts,
    render_text, render_unicode, render_ansi_color_banner, preview_banner,
)


def run_ascii_generator(console: Console, theme) -> str | None:
    """Interactive ASCII art generator. Returns saved path or None."""
    text = questionary.text("Text to render", "FORGECLI").ask()
    if not text:
        return None

    style = questionary.select("Style preset", list(STYLE_PRESETS.keys()),
                               default="Cyberpunk").ask() or "Cyberpunk"
    font = STYLE_PRESETS.get(style, "standard")

    if style == "Unicode":
        art = render_unicode(text)
        console.print(Panel(art, border_style=theme.border,
                            title=f"[{theme.secondary}]Unicode preview[/]"))
    else:
        preview_banner(console, text, font, theme)

    # Show font alternatives the user can switch to.
    if questionary.confirm("Try other FIGlet fonts?", default=False).ask():
        fonts = available_fonts() or FIGLET_FONTS[:20]
        chosen = questionary.select("Font", fonts, default=font).ask()
        if chosen:
            preview_banner(console, text, chosen, theme)
            font = chosen

    ansi = render_ansi_color_banner(text, theme.gradient or [theme.primary, theme.secondary])
    if questionary.confirm("Render ANSI-coloured version?", default=False).ask():
        console.print(ansi)

    if questionary.confirm("Save art to file?", default=False).ask():
        dest_dir = get_state_dir() / "ascii"
        dest_dir.mkdir(parents=True, exist_ok=True)
        filename = questionary.text("Filename", "banner.txt").ask() or "banner.txt"
        out = Path(dest_dir) / filename
        if style == "Unicode":
            out.write_text(art, encoding="utf-8")
        else:
            out.write_text(render_text(text, font), encoding="utf-8")
        console.print(f"[{theme.success}]Saved {out}[/]")
        return str(out)
    return None


__all__ = ["run_ascii_generator"]