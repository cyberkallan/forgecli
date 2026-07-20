"""Example: invoke commands programmatically without the menu."""
from __future__ import annotations

from rich.console import Console
from theme import get_builtin_theme
from ui import make_ctx
from commands import commands_for


def main() -> int:
    console = Console()
    theme = get_builtin_theme("{{THEME_NAME}}")
    ctx = make_ctx(console, theme)
    commands = commands_for("{{CATEGORY}}", "{{SUBCATEGORY}}")
    console.print(f"[{theme.primary}]Available commands:[/]")
    for name, _ in commands:
        console.print(f"  - {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())