"""Banner builder view: compose animated banners with social icons."""
from __future__ import annotations

import json
from pathlib import Path

import questionary
from rich.console import Console

from .core.config import get_state_dir
from .ui.banners import build_banner, STYLE_PRESETS, available_fonts


def run_banner_builder(console: Console, theme) -> dict | None:
    """Compose a banner with logo text, font, version, status, and socials."""
    text = questionary.text("Banner text", "FORGECLI").ask()
    if not text:
        return None

    style = questionary.select("Banner style", list(STYLE_PRESETS.keys()),
                               default="Cyberpunk").ask() or "Cyberpunk"
    font = STYLE_PRESETS.get(style, "standard")
    fonts = available_fonts()
    if fonts and questionary.confirm("Pick a specific font?", default=False).ask():
        font = questionary.select("Font", fonts, default=font).ask() or font

    version = questionary.text("Version", "1.0.0").ask() or "1.0.0"
    status = questionary.text("Status", "stable").ask() or "stable"

    socials = {}
    for label in ["GitHub", "Website", "Instagram", "Telegram", "Discord"]:
        val = questionary.text(f"{label} (blank to skip)", "").ask()
        if val:
            socials[label] = val

    panel = build_banner(console, theme, text=text, font=font,
                         version=version, socials=socials, status=status)
    console.print(panel)

    if questionary.confirm("Save banner config?", default=False).ask():
        dest_dir = get_state_dir() / "banners"
        dest_dir.mkdir(parents=True, exist_ok=True)
        out = dest_dir / f"{text.lower()}_banner.json"
        config = {"text": text, "font": font, "version": version,
                  "status": status, "socials": socials}
        out.write_text(json.dumps(config, indent=2), encoding="utf-8")
        console.print(f"[{theme.success}]Saved {out}[/]")
        return config
    return None


__all__ = ["run_banner_builder"]