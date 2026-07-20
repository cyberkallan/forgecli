"""Branding and project data models used by the wizard and generator."""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional


_SLUG_RE = re.compile(r"[^a-z0-9_]+")


def slugify(value: str, fallback: str = "forgecli_tool") -> str:
    """Convert ``value`` into a snake_case identifier."""
    cleaned = _SLUG_RE.sub("_", (value or "").lower()).strip("_")
    return cleaned or fallback


@dataclass
class Branding:
    """All branding fields collected by the Branding Wizard."""

    project_name: str = "ForgeCLI Tool"
    command_name: str = "forgecli_tool"
    author: str = "Arjun TM"
    github: str = "https://github.com/cyberkallan"
    website: str = ""
    instagram: str = "https://instagram.com/imarjunarz"
    youtube: str = ""
    telegram: str = ""
    discord: str = ""
    twitter: str = ""
    email: str = ""
    license: str = "MIT"
    version: str = "1.0.0"
    description: str = "A terminal tool built with ForgeCLI."
    tagline: str = "Built with ForgeCLI"
    company: str = ""
    organization: str = ""
    support_url: str = ""
    documentation_url: str = ""
    donation_url: str = ""
    logo_text: str = "FORGECLI"
    banner_style: str = "Cyber"          # Style preset
    ascii_style: str = "Cyberpunk"       # FIGlet font preset
    footer_text: str = "Built with ForgeCLI"
    custom_colors: Dict[str, str] = field(default_factory=dict)
    theme: str = "Cyberpunk"
    icons: str = "Default"
    startup_animation: str = "Cyber Loading"
    loading_animation: str = "Cyber Loading"
    spinner_type: str = "dots"
    progress_bar_style: str = "Smooth"
    menu_style: str = "Cyber"
    border_style: str = "rounded"
    font: str = "standard"

    # Derived / wizard-collected
    category: str = "CLI Utility"
    subcategory: str = "Calculator"
    tags: list[str] = field(default_factory=lambda: ["cli", "terminal"])
    python_version: str = ">=3.9"

    # Project-level options
    install_deps_on_run: bool = True
    auto_update: bool = True
    enable_logger: bool = True
    enable_theme: bool = True
    enable_config: bool = True
    enable_plugins: bool = False
    include_examples: bool = True
    include_tests: bool = True
    include_docker: bool = False

    # Metadata
    extras: Dict[str, Any] = field(default_factory=dict)

    def command_slug(self) -> str:
        if self.command_name:
            return slugify(self.command_name, "forgecli_tool")
        return slugify(self.project_name, "forgecli_tool")

    def slug(self) -> str:
        return slugify(self.project_name, "forgecli_tool")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def save(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False),
                        encoding="utf-8")
        return path

    @classmethod
    def load(cls, path: Path) -> "Branding":
        data = json.loads(path.read_text(encoding="utf-8"))
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in data.items() if k in known})


@dataclass
class GeneratedProject:
    """A materialised tool project on disk."""

    branding: Branding
    root: Path

    def __post_init__(self) -> None:
        self.root = Path(self.root)

    def files(self) -> list[Path]:
        """Return every file path inside ``root``."""
        return sorted(p for p in self.root.rglob("*") if p.is_file())


__all__ = ["Branding", "GeneratedProject", "slugify"]