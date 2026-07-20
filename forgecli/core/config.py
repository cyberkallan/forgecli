"""Persistent user configuration for ForgeCLI."""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

from .logging_utils import get_logger

_LOG = get_logger("core.config")


@dataclass
class UserSettings:
    """User-tunable default settings."""

    default_author: str = "Arjun TM"
    default_github: str = "https://github.com/cyberkallan"
    default_instagram: str = "https://instagram.com/imarjunarz"
    default_license: str = "MIT"
    default_theme: str = "Cyberpunk"
    default_export_dir: str = "./exports"
    animation_speed: float = 1.0
    auto_save: bool = True
    auto_backup: bool = True
    update_channel: str = "stable"
    extras: Dict[str, Any] = field(default_factory=dict)


def get_state_dir() -> Path:
    """Return the directory where ForgeCLI stores persistent state."""
    base = os.environ.get("FORGECLI_HOME") or str(Path.home() / ".forgecli")
    path = Path(base)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_state_file() -> Path:
    """Return the path to the persistent state file."""
    return get_state_dir() / "state.json"


def load_state() -> UserSettings:
    """Load persistent settings, returning defaults on any failure."""
    path = get_state_file()
    if not path.exists():
        return UserSettings()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        _LOG.warning("State file unreadable, ignoring: %s", exc)
        return UserSettings()
    defaults = UserSettings()
    merged: Dict[str, Any] = {**asdict(defaults), **data}
    extras = merged.pop("extras", {}) or {}
    merged["extras"] = extras
    settings = UserSettings(**merged)
    return settings


def save_state(settings: UserSettings) -> Path:
    """Persist settings to disk and return the file path."""
    path = get_state_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = asdict(settings)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def state_file_exists() -> bool:
    return get_state_file().exists()


def reset_state() -> None:
    """Remove the state file so defaults take effect on next launch."""
    path = get_state_file()
    if path.exists():
        path.unlink()


__all__ = [
    "UserSettings",
    "get_state_dir",
    "get_state_file",
    "load_state",
    "save_state",
    "state_file_exists",
    "reset_state",
]
