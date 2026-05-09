"""Filesystem locations PaperForge uses for config, cache and bundled assets."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def config_dir() -> Path:
    """Return ``~/.paperforge`` (created on demand)."""
    base = Path(os.path.expanduser("~")) / ".paperforge"
    base.mkdir(parents=True, exist_ok=True)
    return base


def cache_dir() -> Path:
    """Return ``~/.paperforge/cache`` (created on demand)."""
    cache = config_dir() / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    return cache


def image_cache_dir() -> Path:
    """Cache for fetched HTTP images embedded in user Markdown."""
    img = cache_dir() / "imgs"
    img.mkdir(parents=True, exist_ok=True)
    return img


def package_root() -> Path:
    """Directory of the installed ``paperforge`` package (works under PyInstaller)."""
    if getattr(sys, "frozen", False):
        # PyInstaller stores bundled data under sys._MEIPASS
        return Path(sys._MEIPASS) / "paperforge"  # type: ignore[attr-defined]
    return Path(__file__).resolve().parent.parent


def asset(*parts: str) -> Path:
    """Build an absolute path to a bundled asset (CSS, locale, etc.)."""
    return package_root().joinpath(*parts)
