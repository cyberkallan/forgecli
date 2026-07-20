"""Theme loading for {{PROJECT_NAME}}."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Theme:
    name: str = "Cyberpunk"
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

    @classmethod
    def from_dict(cls, data: dict) -> "Theme":
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in data.items() if k in known})


_THEMES = {
    "Dark": Theme(name="Dark", fg="white", primary="cyan", secondary="bright_cyan",
                  success="green", warning="yellow", danger="red",
                  info="blue", muted="bright_black", border="cyan", gradient=["cyan", "white"]),
    "Green Hacker": Theme(name="Green Hacker", fg="green", primary="green", secondary="bright_green",
                          success="bright_green", warning="yellow", danger="red",
                          info="cyan", muted="green", border="green", gradient=["green", "bright_green", "green"]),
    "Blue Neon": Theme(name="Blue Neon", fg="white", primary="dodger_blue1", secondary="deep_pink1",
                       success="green", warning="yellow", danger="red", info="cyan",
                       muted="bright_black", border="dodger_blue1", gradient=["dodger_blue1", "deep_pink1"]),
    "Purple": Theme(name="Purple", primary="purple", secondary="violet", border="purple",
                    gradient=["purple", "violet"]),
    "Red": Theme(name="Red", primary="red", secondary="bright_red", border="red",
                 gradient=["red", "bright_red"]),
    "Amber": Theme(name="Amber", primary="dark_orange", secondary="yellow", border="dark_orange",
                   gradient=["dark_orange", "yellow"]),
    "Catppuccin": Theme(name="Catppuccin", fg="#cdd6f4", primary="#89b4fa", secondary="#cba6f7",
                        success="#a6e3a1", warning="#f9e2af", danger="#f38ba8",
                        info="#94e2d5", muted="#6c7086", border="#89b4fa",
                        gradient=["#89b4fa", "#cba6f7"]),
    "Tokyo Night": Theme(name="Tokyo Night", fg="#c0caf5", primary="#7aa2f7", secondary="#bb9af7",
                         success="#9ece6a", warning="#e0af68", danger="#f7768e",
                         info="#7dcfff", muted="#565f89", border="#7aa2f7",
                         gradient=["#7aa2f7", "#bb9af7"]),
    "Nord": Theme(name="Nord", fg="#d8dee9", primary="#88c0d0", secondary="#81a1c1",
                  success="#a3be8c", warning="#ebcb8b", danger="#bf616a",
                  info="#5e81ac", muted="#4c566a", border="#88c0d0", gradient=["#88c0d0", "#81a1c1"]),
    "Dracula": Theme(name="Dracula", fg="#f8f8f2", primary="#bd93f9", secondary="#ff79c6",
                     success="#50fa7b", warning="#f1fa8c", danger="#ff5555",
                     info="#8be9fd", muted="#6272a4", border="#bd93f9",
                     gradient=["#bd93f9", "#ff79c6"]),
    "Gruvbox": Theme(name="Gruvbox", fg="#ebdbb2", primary="#fabd2f", secondary="#fe8019",
                     success="#b8bb26", warning="#fabd2f", danger="#fb4934",
                     info="#83a598", muted="#928374", border="#fabd2f",
                     gradient=["#fabd2f", "#fe8019"]),
    "Matrix": Theme(name="Matrix", fg="green", primary="green", secondary="bright_green",
                    success="bright_green", warning="yellow", danger="bright_red",
                    info="green", muted="green", border="green", gradient=["green", "white", "green"]),
    "Cyberpunk": Theme(name="Cyberpunk", fg="white", primary="#00fff5", secondary="#ff00aa",
                       success="#00ff88", warning="#ffd000", danger="#ff3366",
                       info="#00aaff", muted="bright_black", border="#00fff5",
                       gradient=["#00fff5", "#ff00aa", "#00fff5"]),
}


def get_builtin_theme(name: str) -> Theme:
    key = (name or "Cyberpunk").lower()
    for t in _THEMES.values():
        if t.name.lower() == key:
            return t
    return _THEMES["Cyberpunk"]


def load_theme(path: str = "theme.json") -> Optional[Theme]:
    if not os.path.isfile(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.loads(fh.read())
    except (OSError, json.JSONDecodeError):
        return None
    return Theme.from_dict(data)
