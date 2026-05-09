"""Cross-platform Chromium-family browser detection for headless PDF rendering."""

from __future__ import annotations

import os
import platform
import shutil
from pathlib import Path
from typing import Iterable

from paperforge.config import load_config


def _windows_candidates() -> list[Path]:
    pf86 = os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)")
    pf = os.environ.get("PROGRAMFILES", r"C:\Program Files")
    local = os.environ.get("LOCALAPPDATA", "")
    paths = [
        Path(pf86) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
        Path(pf) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
        Path(pf) / "Google" / "Chrome" / "Application" / "chrome.exe",
        Path(pf86) / "Google" / "Chrome" / "Application" / "chrome.exe",
        Path(pf) / "BraveSoftware" / "Brave-Browser" / "Application" / "brave.exe",
    ]
    if local:
        paths.append(Path(local) / "Microsoft" / "Edge" / "Application" / "msedge.exe")
        paths.append(Path(local) / "Google" / "Chrome" / "Application" / "chrome.exe")
    return paths


def _mac_candidates() -> list[Path]:
    return [
        Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
        Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
        Path("/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"),
    ]


def _linux_executables() -> Iterable[str]:
    # Edge does not exist on Linux; Chromium-family only.
    return ("google-chrome", "chromium", "chromium-browser", "brave-browser")


def detect(override: str | Path | None = None) -> Path:
    """Find the first available browser executable.

    Resolution: explicit override -> config.browser -> env PAPERFORGE_BROWSER ->
    OS-specific candidates -> raise FileNotFoundError.
    """
    if override:
        p = Path(override)
        if p.is_file():
            return p
        raise FileNotFoundError(f"Browser path not found: {override}")

    cfg_browser = load_config().browser
    if cfg_browser:
        p = Path(cfg_browser)
        if p.is_file():
            return p

    env = os.environ.get("PAPERFORGE_BROWSER")
    if env:
        p = Path(env)
        if p.is_file():
            return p

    system = platform.system()
    if system == "Windows":
        for c in _windows_candidates():
            if c.is_file():
                return c
    elif system == "Darwin":
        for c in _mac_candidates():
            if c.is_file():
                return c
    else:  # Linux + others
        for name in _linux_executables():
            found = shutil.which(name)
            if found:
                return Path(found)

    raise FileNotFoundError(
        "No supported browser found. Install Microsoft Edge, Google Chrome, "
        "Chromium or Brave; or set --browser / PAPERFORGE_BROWSER."
    )
