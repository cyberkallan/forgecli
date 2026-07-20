"""Example plugin for {{PROJECT_NAME}}.

A plugin is any ``.py`` file under ``./plugins/`` that exposes a
``register(ctx)`` function returning ``[(label, callable), ...]``.

To enable this example, rename ``_example.py`` to ``example_plugin.py``.
"""
from __future__ import annotations


def hello(ctx):
    """Sample command that prints a greeting using the active theme."""
    ctx["console"].print(f"[{ctx['theme'].primary}]Hello from a {{PROJECT_NAME}} plugin![/]")


def register(ctx):
    """Called by main.py to merge this plugin's commands into the menu."""
    return [("Plugin: Hello", hello)]


__all__ = ["register"]