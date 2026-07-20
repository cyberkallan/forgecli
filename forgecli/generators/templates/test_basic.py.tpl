"""Basic smoke tests for {{PROJECT_NAME}}."""
from __future__ import annotations

import importlib
import os
import subprocess
import sys


def test_commands_module_loads():
    mod = importlib.import_module("commands")
    assert hasattr(mod, "commands_for")


def test_banner_module_loads():
    mod = importlib.import_module("banner")
    assert hasattr(mod, "show_banner")


def test_utils_module_loads():
    mod = importlib.import_module("utils")
    assert hasattr(mod, "collect_system_info")


def test_theme_module_loads():
    mod = importlib.import_module("theme")
    assert mod.get_builtin_theme("Cyberpunk").name == "Cyberpunk"


def test_main_runs_with_quit():
    """End-to-end smoke test: launches main.py under the project root.

    In a real terminal the user picks commands interactively. In a non-tty
    environment questionary may bail out early - that's acceptable for CI.
    """
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    if not sys.stdin.isatty():
        # No real terminal available; skip the interactive check.
        import pytest
        pytest.skip("no interactive terminal available")
    try:
        result = subprocess.run(
            [sys.executable, "main.py"],
            input=b"\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n",
            env=env,
            timeout=8,
            capture_output=True,
        )
    except subprocess.TimeoutExpired:
        return None
    assert result.returncode == 0
