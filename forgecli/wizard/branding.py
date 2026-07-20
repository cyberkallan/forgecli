"""The interactive Branding Wizard."""
from __future__ import annotations

from typing import Optional

import questionary
from rich.panel import Panel

from ..categories import list_categories, subcategories_for, suggest_entrypoint
from ..core.config import UserSettings
from ..models import Branding, slugify
from ..ui.banners import STYLE_PRESETS
from ..ui.menu import MENU_STYLES
from ..ui.animations import ANIMATION_NAMES
from ..ui.theme import Theme, build_registry
from ..ui.prompts import console, ask, confirm, choose


def _hr(theme: Theme, title: str) -> None:
    console.print(Panel(f"[{theme.primary}]{title}[/]", border_style=theme.border,
                        title=f"[{theme.secondary}]ForgeCLI · Branding Wizard[/]",
                        padding=(0, 2)))


def run_branding_wizard(theme: Theme, settings: UserSettings,
                        existing: Optional[Branding] = None) -> Optional[Branding]:
    """Run the full interactive branding wizard. Returns None if cancelled."""
    b = existing or Branding(
        author=settings.default_author,
        github=settings.default_github,
        instagram=settings.default_instagram,
        license=settings.default_license,
        theme=settings.default_theme,
    )

    _hr(theme, "1. Identity")

    b.project_name = ask("Project name", b.project_name or "ForgeCLI Tool")
    if not b.project_name:
        console.print("[red]A project name is required.[/]")
        return None
    b.command_name = ask("Command name (CLI entrypoint)",
                         b.command_name or suggest_entrypoint(b.project_name))
    b.tagline = ask("Tagline", b.tagline)
    b.description = ask("Description", b.description)
    b.version = ask("Version", b.version)
    b.license = choose("License", ["MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause", "ISC"],
                       default=b.license) or "MIT"

    _hr(theme, "2. Author & Links")
    b.author = ask("Author", b.author)
    b.github = ask("GitHub URL", b.github)
    b.website = ask("Website URL", b.website)
    b.instagram = ask("Instagram URL", b.instagram)
    b.youtube = ask("YouTube URL", b.youtube)
    b.telegram = ask("Telegram URL", b.telegram)
    b.discord = ask("Discord invite / URL", b.discord)
    b.twitter = ask("Twitter/X URL", b.twitter)
    b.email = ask("Email", b.email)
    b.company = ask("Company", b.company)
    b.organization = ask("Organization", b.organization)
    b.support_url = ask("Support URL", b.support_url)
    b.documentation_url = ask("Documentation URL", b.documentation_url)
    b.donation_url = ask("Donation URL", b.donation_url)

    _hr(theme, "3. Category")
    b.category = choose("Tool category", list_categories(), default=b.category) or "CLI Utility"
    subs = subcategories_for(b.category)
    b.subcategory = choose(f"Subcategory ({b.category})", subs, default=subs[0]) or subs[0]

    _hr(theme, "4. Banner & ASCII")
    b.logo_text = ask("Logo / banner text", b.logo_text or b.project_name.upper())
    b.banner_style = choose("Banner style", list(STYLE_PRESETS.keys()),
                            default=b.banner_style) or "Cyber"
    b.ascii_style = choose("ASCII style", list(STYLE_PRESETS.keys()),
                            default=b.ascii_style) or "Cyberpunk"
    b.footer_text = ask("Footer text", b.footer_text)
    b.menu_style = choose("Menu style", MENU_STYLES, default=b.menu_style) or "Cyber"
    b.border_style = choose("Border style",
                            ["rounded", "square", "heavy", "double", "ascii"],
                            default=b.border_style) or "rounded"

    _hr(theme, "5. Theme & Animations")
    registry = build_registry()
    b.theme = choose("Theme", registry.names, default=b.theme) or "Cyberpunk"
    b.icons = choose("Icon set", ["Default", "Minimal", "Nerd", "Emoji"],
                     default=b.icons) or "Default"
    b.startup_animation = choose("Startup animation", ANIMATION_NAMES,
                                  default=b.startup_animation) or "Cyber Loading"
    b.loading_animation = choose("Loading animation", ANIMATION_NAMES,
                                  default=b.loading_animation) or "Cyber Loading"
    b.spinner_type = choose("Spinner type",
                              ["dots", "dots2", "dots12", "arc", "bouncingBar",
                               "clock", "moon", "material", "star"],
                              default=b.spinner_type) or "dots"
    b.progress_bar_style = choose("Progress bar style",
                                    ["Smooth", "Blocky", "Minimal", "Neon"],
                                    default=b.progress_bar_style) or "Smooth"

    _hr(theme, "6. Features")
    b.install_deps_on_run = confirm("Auto-install dependencies on run?", b.install_deps_on_run)
    b.auto_update = confirm("Enable update checker?", b.auto_update)
    b.enable_logger = confirm("Enable logging?", b.enable_logger)
    b.enable_theme = confirm("Enable theme engine?", b.enable_theme)
    b.enable_config = confirm("Enable config manager?", b.enable_config)
    b.enable_plugins = confirm("Enable plugin system?", b.enable_plugins)
    b.include_examples = confirm("Include examples?", b.include_examples)
    b.include_tests = confirm("Include tests?", b.include_tests)
    b.include_docker = confirm("Include Docker project files?", b.include_docker)

    _hr(theme, "7. Custom Colors (optional)")
    if confirm("Override any theme colors?", False):
        for slot in ["primary", "secondary", "success", "warning", "danger", "border"]:
            val = ask(f"Color for '{slot}' (hex or name, blank to skip)", "")
            if val:
                b.custom_colors[slot] = val

    _hr(theme, "8. Done")
    console.print(f"[{theme.success}]Branding collected for "
                  f"[{theme.primary}]{b.project_name}[/][/]")
    return b


def run_quick_branding(theme: Theme, settings: UserSettings) -> Optional[Branding]:
    """A fast path that only asks the essentials, using defaults for the rest."""
    b = Branding(
        author=settings.default_author,
        github=settings.default_github,
        instagram=settings.default_instagram,
        license=settings.default_license,
        theme=settings.default_theme,
    )
    _hr(theme, "Quick Branding")
    b.project_name = ask("Project name", "ForgeCLI Tool")
    if not b.project_name:
        return None
    b.command_name = ask("Command name",
                         suggest_entrypoint(b.project_name))
    b.tagline = ask("Tagline", b.tagline)
    b.description = ask("Short description", b.description)
    b.category = choose("Tool category", list_categories(), default="CLI Utility") or "CLI Utility"
    subs = subcategories_for(b.category)
    b.subcategory = choose(f"Subcategory ({b.category})", subs, default=subs[0]) or subs[0]
    b.theme = choose("Theme", build_registry().names, default=settings.default_theme) or "Cyberpunk"
    return b


__all__ = ["run_branding_wizard", "run_quick_branding"]