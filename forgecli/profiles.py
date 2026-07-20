"""Branding profiles: save and load reusable branding presets."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List, Optional

from .core.config import get_state_dir
from .core.logging_utils import get_logger
from .models import Branding

_LOG = get_logger("profiles")


def profiles_dir() -> Path:
    path = get_state_dir() / "profiles"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _safe_name(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", (name or "").strip()).strip("_") or "profile"
    return cleaned.lower()


def save_profile(name: str, branding: Branding) -> Path:
    """Persist a branding preset. Returns the file path."""
    path = profiles_dir() / f"{_safe_name(name)}.json"
    path.write_text(json.dumps(branding.to_dict(), indent=2, ensure_ascii=False),
                    encoding="utf-8")
    return path


def load_profile(name: str) -> Optional[Branding]:
    """Load a preset by name. Returns None if it does not exist."""
    path = profiles_dir() / f"{_safe_name(name)}.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        _LOG.warning("Profile %s unreadable: %s", path, exc)
        return None
    known = {f for f in Branding.__dataclass_fields__}
    return Branding(**{k: v for k, v in data.items() if k in known})


def list_profiles() -> List[Path]:
    return sorted(profiles_dir().glob("*.json"))


def delete_profile(name: str) -> bool:
    path = profiles_dir() / f"{_safe_name(name)}.json"
    if path.exists():
        path.unlink()
        return True
    return False


__all__ = ["save_profile", "load_profile", "list_profiles", "delete_profile", "profiles_dir"]