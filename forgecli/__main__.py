"""Allow ``python -m forgecli`` to launch the app."""
from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
