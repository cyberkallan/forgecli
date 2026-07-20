#!/usr/bin/env python3
"""ForgeCLI — module entrypoint launcher.

Lets you run ``python forgecli.py`` (or ``./forgecli.py`` after ``chmod +x``)
from the project root without installing. Same effect as ``python -m forgecli``.
"""
from forgecli.cli import main

if __name__ == "__main__":
    raise SystemExit(main())