"""Rich console singleton + helpers used everywhere."""

from __future__ import annotations

from rich.console import Console
from rich.theme import Theme

_THEME = Theme(
    {
        "info": "cyan",
        "warn": "yellow",
        "error": "bold red",
        "ok": "bold green",
        "muted": "grey50",
        "accent": "bold #2E86AB",
    }
)

console = Console(theme=_THEME, legacy_windows=False, force_terminal=None)


def info(msg: str) -> None:
    console.print(f"[info]i[/] {msg}")


def ok(msg: str) -> None:
    console.print(f"[ok]✓[/] {msg}")


def warn(msg: str) -> None:
    console.print(f"[warn]![/] {msg}")


def error(msg: str) -> None:
    console.print(f"[error]x[/] {msg}")
