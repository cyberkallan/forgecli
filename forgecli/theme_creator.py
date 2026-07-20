"""Custom theme creator view."""
from __future__ import annotations

import questionary
from rich.console import Console
from rich.panel import Panel

from .ui.banners import preview_banner
from .ui.theme import Theme, build_registry


SLOTS = ["bg", "fg", "primary", "secondary", "success", "warning",
         "danger", "info", "muted", "border"]


def run_theme_creator(console: Console, theme) -> Theme | None:
    """Interactive custom theme builder with live preview."""
    name = questionary.text("Theme name", "My Theme").ask()
    if not name:
        return None

    base_name = questionary.select(
        "Start from a built-in theme", build_registry().names,
        default=theme.name,
    ).ask() or theme.name
    base = build_registry().get(base_name) or theme

    new_theme = Theme(**{f: getattr(base, f) for f in Theme.__dataclass_fields__})
    new_theme.name = name
    new_theme.custom = True

    if questionary.confirm("Edit color slots?", default=True).ask():
        for slot in SLOTS:
            cur = getattr(new_theme, slot)
            val = questionary.text(f"{slot} (hex/name, blank keeps {cur})", "").ask()
            if val:
                setattr(new_theme, slot, val.strip())

    grad = questionary.text(
        "Gradient (comma-separated colors, blank keeps current)",
        ",".join(new_theme.gradient),
    ).ask()
    if grad:
        new_theme.gradient = [c.strip() for c in grad.split(",") if c.strip()]

    new_theme.style = questionary.select("Style", ["dark", "light"],
                                          default=new_theme.style).ask() or new_theme.style

    errors = new_theme.validate()
    if errors:
        console.print(Panel("\n".join(errors), border_style="red",
                            title="Validation errors"))
        return None

    console.print(f"[{theme.success}]Preview:[/]")
    preview_banner(console, "PREVIEW", "standard", new_theme)

    if questionary.confirm("Save theme?", default=True).ask():
        registry = build_registry()
        path = registry.save_custom_theme(new_theme)
        console.print(f"[{theme.success}]Saved {path}[/]")
        return new_theme
    return None


__all__ = ["run_theme_creator"]