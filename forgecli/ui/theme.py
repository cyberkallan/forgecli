"""Theme engine and persistence.

A theme defines the palette used both by ForgeCLI itself and by the tools it
generates. Themes are stored in JSON under the user's ForgeCLI home directory.
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from ..core.config import get_state_dir
from ..core.logging_utils import get_logger

_LOG = get_logger("ui.theme")


# Valid color tokens we accept: named colors, #hex, rgb(...), bright_x.
_COLOR_RE = re.compile(r"^(?:#[0-9a-fA-F]{3,8}|[a-zA-Z][\w .]*|rgb\([^)]*\))$")


@dataclass
class Theme:
    """A palette that drives every visual element."""

    name: str
    description: str = ""
    style: str = "dark"
    bg: str = "black"
    fg: str = "white"
    primary: str = "cyan"
    secondary: str = "magenta"
    success: str = "green"
    warning: str = "yellow"
    danger: str = "red"
    info: str = "blue"
    muted: str = "bright_black"
    border: str = "cyan"
    gradient: List[str] = field(default_factory=lambda: ["cyan", "magenta"])
    custom: bool = False

    def validate(self) -> List[str]:
        """Return a list of validation errors (empty list if valid)."""
        errors: List[str] = []
        for attr in ("bg", "fg", "primary", "secondary", "success",
                     "warning", "danger", "info", "muted", "border"):
            value = getattr(self, attr)
            if not isinstance(value, str) or not _COLOR_RE.match(value):
                errors.append(f"Invalid color for {attr}: {value!r}")
        for color in self.gradient:
            if not _COLOR_RE.match(color):
                errors.append(f"Invalid gradient color: {color!r}")
        if self.style not in {"dark", "light"}:
            errors.append(f"style must be 'dark' or 'light', got {self.style!r}")
        return errors

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Theme":
        known = {f for f in cls.__dataclass_fields__}
        cleaned = {k: v for k, v in data.items() if k in known}
        return cls(**cleaned)


# ---- Registry ---------------------------------------------------------------

class ThemeRegistry:
    """In-memory registry backed by the filesystem for custom themes."""

    def __init__(self, themes: Optional[Iterable[Theme]] = None) -> None:
        self._themes: Dict[str, Theme] = {}
        if themes:
            for t in themes:
                self._themes[t.name.lower()] = t

    # ---- Built-in access ----------------------------------------------------

    @property
    def names(self) -> List[str]:
        return sorted(self._themes.keys(), key=str.lower)

    def __contains__(self, name: str) -> bool:
        return name.lower() in self._themes

    def get(self, name: str) -> Optional[Theme]:
        return self._themes.get(name.lower())

    def add(self, theme: Theme, *, overwrite: bool = False) -> None:
        key = theme.name.lower()
        if key in self._themes and not overwrite:
            raise ValueError(f"Theme already exists: {theme.name}")
        self._themes[key] = theme

    def remove(self, name: str) -> bool:
        return self._themes.pop(name.lower(), None) is not None

    def all(self) -> List[Theme]:
        return [self._themes[k] for k in self.names]

    # ---- Persistence --------------------------------------------------------

    def custom_dir(self) -> Path:
        path = get_state_dir() / "themes"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def load_custom_themes(self) -> int:
        """Load themes from disk. Returns the number loaded."""
        path = self.custom_dir()
        count = 0
        for fp in sorted(path.glob("*.json")):
            try:
                data = json.loads(fp.read_text(encoding="utf-8"))
                theme = Theme.from_dict(data)
                theme.custom = True
                errors = theme.validate()
                if errors:
                    _LOG.warning("Skipping invalid theme %s: %s", fp, errors)
                    continue
                self.add(theme, overwrite=True)
                count += 1
            except (OSError, json.JSONDecodeError) as exc:
                _LOG.warning("Failed to read theme %s: %s", fp, exc)
        return count

    def save_custom_theme(self, theme: Theme) -> Path:
        """Persist a custom theme to disk. Returns the file path."""
        theme.custom = True
        errors = theme.validate()
        if errors:
            raise ValueError("Invalid theme: " + "; ".join(errors))
        safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", theme.name).strip("_") or "theme"
        path = self.custom_dir() / f"{safe.lower()}.json"
        path.write_text(json.dumps(theme.to_dict(), indent=2, ensure_ascii=False),
                        encoding="utf-8")
        return path

    def delete_custom_theme(self, name: str) -> bool:
        theme = self.get(name)
        if not theme or not theme.custom:
            return False
        path = self.custom_dir()
        for fp in path.glob("*.json"):
            try:
                data = json.loads(fp.read_text(encoding="utf-8"))
                if data.get("name", "").lower() == name.lower():
                    fp.unlink()
                    self.remove(name)
                    return True
            except OSError:
                continue
        return False


# ---- Gradient helpers ------------------------------------------------------

def gradient_text(text: str, colors: Iterable[str]) -> str:
    """Return text where each character is colored in sequence from ``colors``.

    Used for banners when the caller doesn't want a Rich console call.
    """
    palette = list(colors)
    if not palette:
        return text
    palette = palette * max(1, len(text) // len(palette) + 1)
    out: List[str] = []
    for i, ch in enumerate(text):
        if ch == "\n":
            out.append(ch)
            continue
        out.append(f"[{palette[i % len(palette)]}]{ch}[/]")
    return "".join(out)


__all__ = ["Theme", "ThemeRegistry", "gradient_text", "build_registry"]


def build_registry() -> ThemeRegistry:
    """Construct a registry seeded with all built-in themes plus any custom ones."""
    from ..themes.builtin import BUILTIN_THEMES

    registry = ThemeRegistry()
    for theme in BUILTIN_THEMES.values():
        registry.add(theme, overwrite=True)
    registry.load_custom_themes()
    return registry
