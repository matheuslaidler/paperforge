"""Entry point: GUI by default, CLI when arguments are provided.

Behavior:

- ``paperforge`` (no args)     -> GUI
- ``paperforge --gui``         -> GUI
- ``paperforge SUBCOMMAND ...``-> CLI (Typer)
- ``paperforge --cli``         -> CLI even without a subcommand (prints help)
"""

import os
import sys

# Force UTF-8 stdio on Windows so the console doesn't mangle accents.
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

# Reconfigure stdout/stderr to UTF-8 — critical on Windows console (cp1252).
# When packaged with --windowed they may be None; guard with hasattr.
for _stream_name in ("stdout", "stderr"):
    _stream = getattr(sys, _stream_name, None)
    if _stream is not None and hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def _wants_gui() -> bool:
    return len(sys.argv) == 1 or sys.argv[1:] == ["--gui"]


def _wants_cli_help() -> bool:
    return sys.argv[1:] == ["--cli"]


def main() -> int:
    if _wants_gui():
        from paperforge.gui.app import launch
        return launch(sys.argv)

    if _wants_cli_help():
        sys.argv[1:] = ["--help"]

    # CLI mode — matplotlib stays on Agg
    os.environ.setdefault("MPLBACKEND", "Agg")
    from paperforge.cli import app
    return app() or 0


if __name__ == "__main__":
    sys.exit(main())
