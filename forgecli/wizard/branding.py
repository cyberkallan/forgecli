"""The interactive Branding Wizard."""
from __future__ import annotations

from typing import Optional

import questionary
from rich.panel import Panel

from ..categories import list_categories, subcategories_for, suggest_entrypoint
from ..core.config import UserSettings
from ..models import Branding, slugify
from ..profiles import list_profiles, load_profile, save_profile
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

    b.project_name = ask("Project name", b.project_name or "ForgeCLI Tool",
                         theme=theme)
    if not b.project_name:
        console.print("[red]A project name is required.[/]")
        return None
    b.command_name = ask("Command name (CLI entrypoint)",
                         b.command_name or suggest_entrypoint(b.project_name),
                         theme=theme)
    b.tagline = ask("Tagline", b.tagline, theme=theme)
    b.description = ask("Description", b.description, theme=theme)
    b.version = ask("Version", b.version, theme=theme)
    b.license = choose("License", ["MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause", "ISC"],
                       default=b.license, theme=theme) or "MIT"

    _hr(theme, "2. Author & Links")
    b.author = ask("Author", b.author, theme=theme)
    b.github = ask("GitHub URL", b.github, theme=theme)
    b.website = ask("Website URL", b.website, theme=theme)
    b.instagram = ask("Instagram URL", b.instagram, theme=theme)
    b.youtube = ask("YouTube URL", b.youtube, theme=theme)
    b.telegram = ask("Telegram URL", b.telegram, theme=theme)
    b.discord = ask("Discord invite / URL", b.discord, theme=theme)
    b.twitter = ask("Twitter/X URL", b.twitter, theme=theme)
    b.email = ask("Email", b.email, theme=theme)
    b.company = ask("Company", b.company, theme=theme)
    b.organization = ask("Organization", b.organization, theme=theme)
    b.support_url = ask("Support URL", b.support_url, theme=theme)
    b.documentation_url = ask("Documentation URL", b.documentation_url, theme=theme)
    b.donation_url = ask("Donation URL", b.donation_url, theme=theme)

    _hr(theme, "3. Category")
    b.category = choose("Tool category", list_categories(), default=b.category,
                        theme=theme) or "CLI Utility"
    subs = subcategories_for(b.category)
    b.subcategory = choose(f"Subcategory ({b.category})", subs,
                           default=subs[0], theme=theme) or subs[0]

    _hr(theme, "4. Banner & ASCII")
    b.logo_text = ask("Logo / banner text", b.logo_text or b.project_name.upper(),
                      theme=theme)
    b.banner_style = choose("Banner style", list(STYLE_PRESETS.keys()),
                            default=b.banner_style, theme=theme) or "Cyber"
    b.ascii_style = choose("ASCII style", list(STYLE_PRESETS.keys()),
                            default=b.ascii_style, theme=theme) or "Cyberpunk"
    b.footer_text = ask("Footer text", b.footer_text, theme=theme)
    b.menu_style = choose("Menu style", MENU_STYLES, default=b.menu_style,
                          theme=theme) or "Cyber"
    b.border_style = choose("Border style",
                            ["rounded", "square", "heavy", "double", "ascii"],
                            default=b.border_style, theme=theme) or "rounded"

    _hr(theme, "5. Theme & Animations")
    registry = build_registry()
    b.theme = choose("Theme", registry.names, default=b.theme,
                     theme=theme) or "Cyberpunk"
    b.icons = choose("Icon set", ["Default", "Minimal", "Nerd", "Emoji"],
                     default=b.icons, theme=theme) or "Default"
    b.startup_animation = choose("Startup animation", ANIMATION_NAMES,
                                  default=b.startup_animation,
                                  theme=theme) or "Cyber Loading"
    b.loading_animation = choose("Loading animation", ANIMATION_NAMES,
                                  default=b.loading_animation,
                                  theme=theme) or "Cyber Loading"
    b.spinner_type = choose("Spinner type",
                              ["dots", "dots2", "dots12", "arc", "bouncingBar",
                               "clock", "moon", "material", "star"],
                              default=b.spinner_type, theme=theme) or "dots"
    b.progress_bar_style = choose("Progress bar style",
                                    ["Smooth", "Blocky", "Minimal", "Neon"],
                                    default=b.progress_bar_style,
                                    theme=theme) or "Smooth"

    _hr(theme, "6. Features")
    b.install_deps_on_run = confirm("Auto-install dependencies on run?",
                                     b.install_deps_on_run, theme=theme)
    b.auto_update = confirm("Enable update checker?", b.auto_update, theme=theme)
    b.enable_logger = confirm("Enable logging?", b.enable_logger, theme=theme)
    b.enable_theme = confirm("Enable theme engine?", b.enable_theme, theme=theme)
    b.enable_config = confirm("Enable config manager?", b.enable_config,
                               theme=theme)
    b.enable_plugins = confirm("Enable plugin system?", b.enable_plugins,
                                theme=theme)
    b.include_examples = confirm("Include examples?", b.include_examples,
                                  theme=theme)
    b.include_tests = confirm("Include tests?", b.include_tests, theme=theme)
    b.include_docker = confirm("Include Docker project files?", b.include_docker,
                                theme=theme)

    _hr(theme, "7. Custom Colors (optional)")
    if confirm("Override any theme colors?", False, theme=theme):
        for slot in ["primary", "secondary", "success", "warning", "danger", "border"]:
            val = ask(f"Color for '{slot}' (hex or name, blank to skip)", "",
                      theme=theme)
            if val:
                b.custom_colors[slot] = val

    _hr(theme, "8. Done")
    console.print(f"[{theme.success}]Branding collected for "
                  f"[{theme.primary}]{b.project_name}[/][/]")
    return b


def run_quick_branding(theme: Theme, settings: UserSettings) -> Optional[Branding]:
    """A fast path that only asks the essentials, using defaults for the rest."""
    _hr(theme, "Quick Branding")
    # Offer profile loading.
    profiles = list_profiles()
    loaded: Optional[Branding] = None
    if profiles and confirm(f"Load a saved profile? ({len(profiles)} available)",
                            False, theme=theme):
        names = [p.stem for p in profiles]
        choice = choose("Profile", names, theme=theme)
        if choice:
            loaded = load_profile(choice)
    b = loaded or Branding(
        author=settings.default_author,
        github=settings.default_github,
        instagram=settings.default_instagram,
        license=settings.default_license,
        theme=settings.default_theme,
    )
    b.project_name = ask("Project name", b.project_name or "ForgeCLI Tool",
                         theme=theme)
    if not b.project_name:
        return None
    b.command_name = ask("Command name",
                         b.command_name or suggest_entrypoint(b.project_name),
                         theme=theme)
    b.tagline = ask("Tagline", b.tagline or "Built with ForgeCLI", theme=theme)
    b.description = ask("Short description",
                        b.description or "A terminal tool built with ForgeCLI.",
                        theme=theme)
    b.category = choose("Tool category", list_categories(),
                        default=b.category or "CLI Utility",
                        theme=theme) or "CLI Utility"
    subs = subcategories_for(b.category)
    # Reset subcategory so a stale default from a different category never
    # reaches questionary.select (which would crash — see the Password Tools
    # repro). The choose() guard covers this too, but resetting is clearer.
    b.subcategory = ""
    b.subcategory = choose(f"Subcategory ({b.category})", subs,
                           default=b.subcategory or subs[0], theme=theme) or subs[0]
    b.theme = choose("Theme", build_registry().names, default=b.theme,
                     theme=theme) or "Cyberpunk"
    if confirm("Save this branding as a reusable profile?", False, theme=theme):
        name = ask("Profile name", slugify(b.project_name), theme=theme)
        if name:
            save_profile(name, b)
            console.print(f"[{theme.success}]Saved profile '{name}'.[/]")
    return b


__all__ = ["run_branding_wizard", "run_quick_branding"]