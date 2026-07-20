"""Project generator: materialises a complete CLI tool from a Branding."""
from __future__ import annotations

import datetime as _dt
import json
import re
import shutil
from importlib import resources
from pathlib import Path
from typing import Callable, Iterable, Optional

from ..core.config import get_state_dir
from ..core.logging_utils import get_logger
from ..models import Branding, GeneratedProject
from ..themes.builtin import get_builtin_theme

_LOG = get_logger("generators.project")

_TEMPLATES_DIR = "templates"


def _read_template(name: str) -> str:
    """Read a generator template from the package resources."""
    candidate = resources.files("forgecli.generators").joinpath(_TEMPLATES_DIR, name)
    return candidate.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Token helpers
# ---------------------------------------------------------------------------

def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "_", (value or "").lower()).strip("_") or "forgecli_tool"


def _license_body(license_name: str, author: str, year: str) -> str:
    if license_name.upper() == "MIT":
        return (
            f"MIT License\n\nCopyright (c) {year} {author}\n\n"
            "Permission is hereby granted, free of charge, to any person obtaining a copy\n"
            "of this software and associated documentation files (the \"Software\"), to deal\n"
            "in the Software without restriction, including without limitation the rights\n"
            "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell\n"
            "copies of the Software, and to permit persons to whom the Software is\n"
            "furnished to do so, subject to the following conditions:\n\n"
            "The above copyright notice and this permission notice shall be included in all\n"
            "copies or substantial portions of the Software.\n\n"
            "THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n"
            "IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n"
            "FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n"
            "AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n"
            "LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n"
            "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\n"
            "SOFTWARE.\n"
        )
    if license_name.upper() in {"APACHE-2.0", "APACHE 2.0"}:
        return (
            f"Apache License 2.0\n\nCopyright (c) {year} {author}.\n\n"
            "Licensed under the Apache License, Version 2.0 (the \"License\");\n"
            "you may not use this file except in compliance with the License.\n"
            "You may obtain a copy of the License at\n\n    http://www.apache.org/licenses/LICENSE-2.0\n\n"
            "Unless required by applicable law or agreed to in writing, software\n"
            "distributed under the License is distributed on an \"AS IS\" BASIS,\n"
            "WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\n"
        )
    if license_name.upper().startswith("GPL"):
        return (
            f"{license_name} License\n\nCopyright (c) {year} {author}.\n\n"
            "This program is free software: you can redistribute it and/or modify\n"
            "it under the terms of the GNU General Public License as published by\n"
            "the Free Software Foundation, either version 3 of the License, or\n"
            "(at your option) any later version.\n"
        )
    return (
        f"All rights reserved.\n\nCopyright (c) {year} {author}.\n"
        f"Released under the {license_name} license.\n"
    )


def _safe(value: str) -> str:
    return (value or "").replace("\r", "").strip()


def _safe_url(value: str, fallback: str = "") -> str:
    value = (value or "").strip()
    if not value:
        return fallback
    return value


# ---------------------------------------------------------------------------
# Token substitution
# ---------------------------------------------------------------------------

def _tokens(branding: Branding) -> dict:
    """Build the token map used to substitute ``{{...}}`` placeholders."""
    year = _dt.datetime.utcnow().strftime("%Y")
    theme = get_builtin_theme(branding.theme)
    custom_overrides = branding.custom_colors or {}

    def _col(name: str, default: str) -> str:
        return custom_overrides.get(name, getattr(theme, name, default))

    theme_dict = {
        "name": theme.name,
        "description": theme.description,
        "style": theme.style,
        "bg": _col("bg", theme.bg),
        "fg": _col("fg", theme.fg),
        "primary": _col("primary", theme.primary),
        "secondary": _col("secondary", theme.secondary),
        "success": _col("success", theme.success),
        "warning": _col("warning", theme.warning),
        "danger": _col("danger", theme.danger),
        "info": _col("info", theme.info),
        "muted": _col("muted", theme.muted),
        "border": _col("border", theme.border),
        "gradient": list(theme.gradient or [theme.primary, theme.secondary]),
    }

    github_repo = branding.github or "https://github.com/cyberkallan"
    if github_repo.startswith("http"):
        github_repo = github_repo.rstrip("/")

    commands_md = _build_commands_md(branding)

    python_version_slug = branding.python_version.replace(">=", "").strip() or "3.11"

    return {
        "PROJECT_NAME": branding.project_name,
        "COMMAND_NAME": branding.command_name or _slug(branding.project_name),
        "VERSION": branding.version,
        "AUTHOR": branding.author,
        "EMAIL": branding.email or "",
        "GITHUB": branding.github,
        "GITHUB_REPO": github_repo,
        "INSTAGRAM": branding.instagram or "",
        "WEBSITE": branding.website or "",
        "YOUTUBE": branding.youtube or "",
        "TELEGRAM": branding.telegram or "",
        "DISCORD": branding.discord or "",
        "TWITTER": branding.twitter or "",
        "COMPANY": branding.company or "",
        "ORGANIZATION": branding.organization or "",
        "SUPPORT_URL": branding.support_url or "",
        "DOCS_URL": branding.documentation_url or "",
        "DONATION_URL": branding.donation_url or "",
        "LICENSE": branding.license,
        "LICENSE_BADGE": branding.license.replace(" ", "%20"),
        "LICENSE_BODY": _license_body(branding.license, branding.author, year),
        "DESCRIPTION": branding.description,
        "TAGLINE": branding.tagline,
        "FOOTER_TEXT": branding.footer_text,
        "LOGO_TEXT": branding.logo_text or branding.project_name.upper(),
        "CATEGORY": branding.category,
        "SUBCATEGORY": branding.subcategory,
        "THEME_NAME": branding.theme,
        "ASCII_FONT": branding.ascii_style,
        "ASCII_STYLE": branding.ascii_style,
        "BANNER_STYLE": branding.banner_style,
        "MENU_STYLE": branding.menu_style,
        "BORDER_STYLE": branding.border_style,
        "STARTUP_ANIMATION": branding.startup_animation,
        "LOADING_ANIMATION": branding.loading_animation,
        "SPINNER_TYPE": branding.spinner_type,
        "PROGRESS_BAR_STYLE": branding.progress_bar_style,
        "AUTO_UPDATE": "True" if branding.auto_update else "False",
        "INSTALL_DEPS_ON_RUN": "True" if branding.install_deps_on_run else "False",
        "ENABLE_LOGGER": "True" if branding.enable_logger else "False",
        "ENABLE_THEME": "True" if branding.enable_theme else "False",
        "ENABLE_CONFIG": "True" if branding.enable_config else "False",
        "ENABLE_PLUGINS": "True" if branding.enable_plugins else "False",
        "INCLUDE_DOCKER": "True" if branding.include_docker else "False",
        "PYTHON_VERSION": branding.python_version,
        "PYTHON_VERSION_SLUG": python_version_slug,
        "PYTHON_BADGE": python_version_slug.replace(".", "").replace(" ", "") or "3.11",
        "YEAR": year,
        "DATE": _dt.date.today().isoformat(),
        "TAGS_JSON": json.dumps(branding.tags or [branding.category.lower(), branding.subcategory.lower()]),
        "TAGS_PY_LIST": str(branding.tags or [branding.category.lower(), branding.subcategory.lower()]),
        "THEME_JSON": json.dumps(theme_dict, indent=2),
        "ICONS": branding.icons,
        "FONT": branding.font,
        "COMMANDS_MD": commands_md,
        "SLUG": _slug(branding.project_name),
        "STATUS": "stable",
        "BADGE_COLOR": _badge_color(branding.theme),
    }


def _badge_color(theme_name: str) -> str:
    mapping = {
        "Green Hacker": "green", "Matrix": "green", "Blue Neon": "blue",
        "Purple": "purple", "Red": "red", "Amber": "orange",
        "Catppuccin": "ff79c6", "Tokyo Night": "7aa2f7", "Nord": "88c0d0",
        "Dracula": "bd93f9", "Gruvbox": "fabd2f", "Cyberpunk": "00fff5",
        "Dark": "555555", "Light": "cccccc",
    }
    return mapping.get(theme_name, "00fff5")


def _build_commands_md(branding: Branding) -> str:
    """Produce a markdown list of commands, computed from commands.py source."""
    try:
        from .commands_runtime import commands_for

        rows = commands_for(branding.category, branding.subcategory)
    except Exception:  # pragma: no cover - safety net
        rows = []
    if not rows:
        return "- System info, help, and version commands are always available."
    lines = []
    for name, _fn in rows:
        lines.append(f"- **{name}**")
    return "\n".join(lines)


def _render(template: str, tokens: dict) -> str:
    """Replace ``{{TOKEN}}`` placeholders. Tokens missing remain literal."""
    out = template
    for key, value in tokens.items():
        out = out.replace("{{" + key + "}}", str(value))
    return out


# ---------------------------------------------------------------------------
# File writers
# ---------------------------------------------------------------------------

def _writelines(root: Path, rel: str, content: str) -> Path:
    target = root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return target


def _copy_template(root: Path, rel: str, template_name: str, tokens: dict) -> Path:
    text = _render(_read_template(template_name), tokens)
    return _writelines(root, rel, text)


def _empty_readme(root: Path, rel: str, *, message: str) -> Path:
    content = f"# {rel.rstrip('/').split('/')[-1]}\n\n{message}\n"
    return _writelines(root, rel + "/README.md", content)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_project(branding: Branding, *, root: Optional[Path] = None,
                     progress: Optional[Callable[[str], None]] = None,
                     overwrite: bool = False) -> GeneratedProject:
    """Materialise a complete CLI tool project on disk."""
    slug = branding.command_name or _slug(branding.project_name)
    target = Path(root or Path.cwd()) / slug
    if target.exists():
        if not overwrite and any(target.iterdir()):
            raise FileExistsError(f"Target {target} already exists. Pass overwrite=True.")
        if overwrite:
            shutil.rmtree(target)
    target.mkdir(parents=True)

    tokens = _tokens(branding)

    if progress:
        progress("Scaffolding folders")

    folder_specs = {
        "assets/": "Drop screenshots and icons here.",
        "plugins/": "Drop-in Python packages that add commands. Rename `_example.py` to enable the bundled demo.",
        "modules/": "Helper modules shared across plugins.",
        "commands/": "Stand-alone command implementations.",
        "themes/": "Custom theme JSON files.",
        "icons/": "ASCII / Unicode icon packs.",
        "docs/": "Extended documentation lives here.",
        "examples/": "Usage examples for the generated tool.",
        "tests/": "Pytest suite mirroring the source layout.",
    }
    for folder, msg in folder_specs.items():
        _empty_readme(target, folder, message=msg)

    # Ship the example plugin (disabled by default — starts with underscore).
    _copy_template(target, "plugins/_example.py", "plugins/_example.py.tpl", tokens)

    if progress:
        progress("Writing generated Python sources")
    code_files = {
        "main.py": "main.py.tpl",
        "banner.py": "banner.py.tpl",
        "ui.py": "ui.py.tpl",
        "utils.py": "utils.py.tpl",
        "theme.py": "theme.py.tpl",
        "installer.py": "installer.py.tpl",
        "updater.py": "updater.py.tpl",
        "commands.py": "commands.py.tpl",
    }
    for rel, tpl in code_files.items():
        _copy_template(target, rel, tpl, tokens)

    if progress:
        progress("Writing project metadata")
    _copy_template(target, "README.md", "README.md.tpl", tokens)
    _copy_template(target, "requirements.txt", "requirements.txt.tpl", tokens)
    _copy_template(target, "LICENSE", "LICENSE.tpl", tokens)
    _copy_template(target, "CHANGELOG.md", "CHANGELOG.md.tpl", tokens)
    _copy_template(target, "SECURITY.md", "SECURITY.md.tpl", tokens)
    _copy_template(target, "CONTRIBUTING.md", "CONTRIBUTING.md.tpl", tokens)
    _copy_template(target, "CODE_OF_CONDUCT.md", "CODE_OF_CONDUCT.md.tpl", tokens)
    _copy_template(target, ".gitignore", "gitignore.tpl", tokens)
    _copy_template(target, "pyproject.toml", "pyproject.toml.tpl", tokens)
    _copy_template(target, "config.json", "config.json.tpl", tokens)
    _copy_template(target, "settings.json", "settings.json.tpl", tokens)
    _copy_template(target, "theme.json", "theme.json.tpl", tokens)

    if branding.include_tests:
        if progress:
            progress("Adding tests")
        _copy_template(target, "tests/test_basic.py", "test_basic.py.tpl", tokens)
        _writelines(target, "tests/__init__.py", "")

    if branding.include_examples:
        if progress:
            progress("Adding examples")
        _copy_template(target, "examples/example_usage.py", "example_usage.py.tpl", tokens)
        _writelines(target, "examples/__init__.py", "")

    if branding.include_docker:
        if progress:
            progress("Adding Docker project")
        _copy_template(target, "Dockerfile", "Dockerfile.tpl", tokens)
        _writelines(target, ".dockerignore", "__pycache__/\n*.pyc\n.venv/\n")

    if progress:
        progress("Saving branding snapshot")
    branding.save(target / "branding.json")

    if progress:
        progress("Done")

    return GeneratedProject(branding=branding, root=target)


def load_project(path: Path) -> Optional[GeneratedProject]:
    """Load a previously generated project from disk."""
    branding_path = Path(path) / "branding.json"
    if not branding_path.exists():
        return None
    branding = Branding.load(branding_path)
    return GeneratedProject(branding=branding, root=Path(path))


def list_generated_projects(parent: Optional[Path] = None) -> list[GeneratedProject]:
    """List every generated project under ``parent`` (default: workspace dir)."""
    parent = Path(parent or _workspace_dir())
    if not parent.exists():
        return []
    results: list[GeneratedProject] = []
    for child in sorted(parent.iterdir()):
        if (child / "branding.json").is_file():
            loaded = load_project(child)
            if loaded is not None:
                results.append(loaded)
    return results


def _workspace_dir() -> Path:
    """Default location for generated projects."""
    base = get_state_dir() / "workspace"
    base.mkdir(parents=True, exist_ok=True)
    return base


__all__ = [
    "generate_project",
    "load_project",
    "list_generated_projects",
    "WORKSPACE_DIR",
]


WORKSPACE_DIR = _workspace_dir()
