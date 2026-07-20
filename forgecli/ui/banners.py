"""ASCII banner generation with FIGlet fonts and custom styles."""
from __future__ import annotations

import shutil
import sys
from typing import Iterable, List, Optional

import pyfiglet
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from ..core.logging_utils import get_logger
from .theme import Theme, gradient_text

_LOG = get_logger("ui.banners")


# Curated set of fonts that render reliably across terminals and aren't huge.
FIGLET_FONTS: List[str] = [
    "standard",
    "slant",
    "big",
    "block",
    "digital",
    "doom",
    "isometric1",
    "isometric2",
    "isometric3",
    "isometric4",
    "banner",
    "banner3-D",
    "caligraphy",
    "colossal",
    "cybermedium",
    "cyberlarge",
    "epic",
    "fender",
    "georgia11",
    "ghost",
    "graffiti",
    "hieroglyphs",
    "invita",
    "italic",
    "larry3d",
    "merlin1",
    "mike",
    "mini",
    "modular",
    "moscow",
    "nipples",
    "ogre",
    "oldbanner",
    "pawp",
    "peaks",
    "pebbles",
    "poison",
    "puffy",
    "pyramid",
    "rectangles",
    "red_phoenix",
    "relief",
    "rev",
    "reverse",
    "roman",
    "rounded",
    "rowancap",
    "rozzo",
    "runic",
    "runyc",
    "sblood",
    "script",
    "serifcap",
    "shadow",
    "shimrod",
    "short",
    "slant_relief",
    "slide",
    "slscript",
    "small",
    "smkeyboard",
    "smslant",
    "smtengwar",
    "soft",
    "speed",
    "spliff",
    "stacey",
    "stampatello",
    "standard",
    "starwars",
    "stellar",
    "sub-zero",
    "subteran",
    "swampland",
    "swan",
    "sweet",
    "thick",
    "thin",
    "threepoint",
    "ticks",
    "ticksslant",
    "tinker-toy",
    "tombstone",
    "trek",
    "tsalagi",
    "tubular",
    "twisted",
    "two-point",
    "univers",
    "usaflag",
    "wavy",
    "weird",
]


STYLE_PRESETS = {
    "FIGlet": "standard",
    "Unicode": "georgia11",
    "Double": "colossal",
    "ANSI": "moscow",
    "Block": "block",
    "Slant": "slant",
    "Ghost": "ghost",
    "Roman": "roman",
    "Cyberpunk": "cybermedium",
    "Glitch": "weird",
    "Matrix": "digital",
    "Banner": "banner3-D",
}


def _safe_figlet(text: str, font: str) -> str:
    """Render via pyfiglet, falling back to the standard font on failure."""
    try:
        return pyfiglet.figlet_format(text, font=font)
    except Exception as exc:  # font not installed, etc.
        _LOG.debug("FIGlet font %s failed: %s", font, exc)
        try:
            return pyfiglet.figlet_format(text, font="standard")
        except Exception as inner:  # pragma: no cover
            _LOG.warning("FIGlet unavailable: %s", inner)
            return text


def render_text(text: str, font: str = "standard") -> str:
    """Return the ASCII rendition of ``text`` using ``font``."""
    return _safe_figlet(text, font)


def render_unicode(text: str) -> str:
    """Use a Unicode block font to render ``text`` in boxed characters."""
    # Fancy Unicode boxed style that works in any UTF-8 terminal.
    chars = {
        "A": "🅰", "B": "🅱", "C": "🅲", "D": "🅳", "E": "🅴", "F": "🅵",
        "G": "🅶", "H": "🅷", "I": "🅸", "J": "🅹", "K": "🅺", "L": "🅻",
        "M": "🅼", "N": "🅽", "O": "🅾", "P": "🅿", "Q": "🆀", "R": "🆁",
        "S": "🆂", "T": "🆃", "U": "🆄", "V": "🆅", "W": "🆆", "X": "🆇",
        "Y": "🆈", "Z": "🆉",
        "0": "⓪", "1": "①", "2": "②", "3": "③", "4": "④",
        "5": "⑤", "6": "⑥", "7": "⑦", "8": "⑧", "9": "⑨",
    }
    return "".join(chars.get(ch.upper(), ch) for ch in text)


def render_ansi_color_banner(text: str, colors: Iterable[str]) -> str:
    """Render a FIGlet banner with ANSI 24-bit color cycling through ``colors``."""
    banner = _safe_figlet(text, "standard")
    palette = list(colors) or ["cyan"]
    out = []
    for i, line in enumerate(banner.rstrip("\n").split("\n")):
        color = palette[i % len(palette)]
        out.append(f"\x1b[38;2;{_named_to_rgb(color)}m{line}\x1b[0m")
    return "\n".join(out)


def _named_to_rgb(color: str) -> str:
    """Tiny named-color to RGB helper for ANSI conversion."""
    table = {
        "red": "255;85;85",
        "green": "80;250;123",
        "blue": "139;233;253",
        "yellow": "241;250;140",
        "cyan": "139;233;253",
        "magenta": "255;121;198",
        "white": "248;248;242",
        "black": "40;42;54",
        "orange": "255;184;108",
        "pink": "255;121;198",
        "purple": "189;147;249",
    }
    if color in table:
        return table[color]
    if color.startswith("#") and len(color) == 7:
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        return f"{r};{g};{b}"
    return "139;233;253"


def render_rich(text: str, font: str, theme: Theme, gradient: Optional[bool] = True) -> Text:
    """Return a Rich ``Text`` for ``text`` using the theme palette."""
    banner = _safe_figlet(text, font)
    if gradient and theme.gradient:
        palette = theme.gradient
    else:
        palette = [theme.primary]
    lines = []
    for i, line in enumerate(banner.rstrip("\n").split("\n")):
        color = palette[i % len(palette)]
        lines.append(Text(line, style=color))
    return Text("\n").join(lines)


def render_social_row(socials: dict, theme: Theme) -> Text:
    """Render a small row of social handles with optional inline icons."""
    text = Text()
    text.append("  ", style=theme.muted)
    for label, url in socials.items():
        if not url:
            continue
        text.append("▸ ", style=theme.secondary)
        text.append(f"{label}: ", style=theme.fg)
        text.append(url, style=theme.primary)
        text.append("    ", style=theme.muted)
    return text


def preview_banner(console: Console, text: str, font: str, theme: Theme,
                  *, with_panel: bool = True) -> None:
    """Print a banner preview to ``console``."""
    art = render_rich(text, font, theme, gradient=True)
    if with_panel:
        panel = Panel(art, border_style=theme.border,
                      title=f"[{theme.secondary}]Preview · {font}[/]",
                      subtitle=f"[{theme.muted}]{text}[/]")
        console.print(panel)
    else:
        console.print(art)


def available_fonts() -> List[str]:
    """Return the curated FIGlet font list, filtered to ones that load."""
    loaded: List[str] = []
    for font in FIGLET_FONTS:
        try:
            pyfiglet.Figlet(font=font)
            loaded.append(font)
        except pyfiglet.FontNotFound:
            continue
    return loaded


def detect_figlet_binary() -> bool:
    """Return True if the system ``figlet`` binary is available."""
    return shutil.which("figlet") is not None


def system_figlet(text: str, font: str) -> Optional[str]:
    """Use the system ``figlet`` binary if present. Returns None otherwise."""
    if not detect_figlet_binary():
        return None
    import subprocess

    try:
        result = subprocess.run(  # noqa: S603
            ["figlet", "-f", font, text],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        return result.stdout
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as exc:
        _LOG.debug("system figlet failed: %s", exc)
        return None


def build_banner(console: Console, theme: Theme, *, text: str, font: str,
                 version: str = "", socials: Optional[dict] = None,
                 status: str = "") -> Panel:
    """Compose the full banner with social row, version, and status."""
    art = render_rich(text, font, theme)
    body = Text()
    body.append_text(art)
    if version:
        body.append("\n")
        body.append("  ", style=theme.muted)
        body.append(f"v{version}", style=theme.secondary)
        if status:
            body.append("  •  ", style=theme.muted)
            body.append(status, style=theme.success)
    if socials:
        body.append("\n")
        body.append_text(render_social_row(socials, theme))
    return Panel(body, border_style=theme.border,
                 title=f"[{theme.primary}]◆[/] [{theme.secondary}]{text}[/]",
                 subtitle=f"[{theme.muted}]ForgeCLI generated[/]")


__all__ = [
    "FIGLET_FONTS",
    "STYLE_PRESETS",
    "render_text",
    "render_unicode",
    "render_rich",
    "render_ansi_color_banner",
    "render_social_row",
    "preview_banner",
    "available_fonts",
    "detect_figlet_binary",
    "system_figlet",
    "build_banner",
]


# Suppress noisy warning printed when pyfiglet probes for missing fonts.
_orig_showwarning = None
def _silence_font_warnings() -> None:
    global _orig_showwarning
    import warnings
    _orig_showwarning = warnings.showwarning
    def _quiet(*args, **kwargs):  # pragma: no cover - cosmetic
        return None
    warnings.showwarning = _quiet


_silence_font_warnings()
sys.modules.setdefault("pyfiglet", pyfiglet)