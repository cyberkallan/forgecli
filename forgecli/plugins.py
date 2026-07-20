"""Plugin system for ForgeCLI-generated tools.

Plugins are capability toggles stored in the project's config.json and
reflected into the generated code as feature flags. Each plugin has a small
description so users understand what enabling it does.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from .core.logging_utils import get_logger

_LOG = get_logger("plugins")


@dataclass
class Plugin:
    """A toggleable capability."""

    key: str
    name: str
    description: str
    default: bool = False
    future: bool = False  # planned but not yet wired into generated code


PLUGINS: List[Plugin] = [
    Plugin("updater", "Updater", "Check PyPI for newer versions on startup.",
           default=True),
    Plugin("analytics", "Analytics", "Emit anonymous usage events to a local log.",
           default=False),
    Plugin("logging", "Logging", "Persist debug logs to ./logs/.",
           default=True),
    Plugin("theme_engine", "Theme Engine", "Load and switch themes at runtime.",
           default=True),
    Plugin("config_manager", "Configuration Manager",
           "Persist user settings across runs.", default=True),
    Plugin("auto_save", "Auto Save", "Persist in-progress state automatically.",
           default=True),
    Plugin("auto_backup", "Auto Backup", "Snapshot config before destructive ops.",
           default=True),
    Plugin("cloud_sync", "Cloud Sync", "Sync settings across devices.",
           default=False, future=True),
    Plugin("auto_update", "Auto Update", "Apply updates automatically when found.",
           default=False),
    Plugin("notifications", "Notifications",
           "Desktop notifications on completion.", default=False),
]


def plugin_map() -> Dict[str, Plugin]:
    return {p.key: p for p in PLUGINS}


def load_plugin_state(project_root: Path) -> Dict[str, bool]:
    """Read plugin toggles from a project's config.json."""
    cfg = Path(project_root) / "config.json"
    if not cfg.exists():
        return {p.key: p.default for p in PLUGINS}
    try:
        data = json.loads(cfg.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        _LOG.warning("config.json unreadable: %s", exc)
        return {p.key: p.default for p in PLUGINS}
    plugins = data.get("plugins") or {}
    return {p.key: bool(plugins.get(p.key, p.default)) for p in PLUGINS}


def save_plugin_state(project_root: Path, state: Dict[str, bool]) -> None:
    """Write plugin toggles back into the project's config.json."""
    cfg = Path(project_root) / "config.json"
    if cfg.exists():
        try:
            data = json.loads(cfg.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = {}
    else:
        data = {}
    data["plugins"] = state
    cfg.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


__all__ = ["Plugin", "PLUGINS", "plugin_map", "load_plugin_state", "save_plugin_state"]