"""Persistent user configuration stored in ``~/.paperforge/config.yaml``.

Layered resolution (lowest to highest precedence):

1. Built-in defaults below.
2. ``~/.paperforge/config.yaml``
3. ``./paperforge.yaml`` in the current working directory (auto-loaded if present).
4. Environment variables ``PAPERFORGE_LANG``, ``PAPERFORGE_BROWSER``.
5. CLI flags (``--lang``, ``--browser``) — handled in ``cli.py``.
"""

from __future__ import annotations

import os
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Any

import yaml

from paperforge.utils.paths import config_dir

_DEFAULT_CONFIG_PATH = config_dir() / "config.yaml"
_PROJECT_CONFIG_NAME = "paperforge.yaml"


@dataclass
class PaperForgeConfig:
    """Schema for the persistent config. New fields ALWAYS get a default value."""

    lang: str = "en"
    default_pdf_style: str = "default"
    default_slide_theme: str = "default"
    browser: str = ""               # empty = auto-detect
    references_style: str = "abnt"  # "abnt" | "none"
    mathjax_engine: str = "cdn"     # "cdn" | "katex-local"
    mathjax_timeout: int = 8


# --------------------------------------------------------------------------- #
#  Loading / saving                                                            #
# --------------------------------------------------------------------------- #
def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        with path.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
            return data if isinstance(data, dict) else {}
    except (yaml.YAMLError, OSError):
        return {}


def _apply_env_overrides(data: dict[str, Any]) -> dict[str, Any]:
    if env_lang := os.environ.get("PAPERFORGE_LANG"):
        data["lang"] = env_lang
    if env_browser := os.environ.get("PAPERFORGE_BROWSER"):
        data["browser"] = env_browser
    return data


def _coerce(data: dict[str, Any]) -> PaperForgeConfig:
    """Build a PaperForgeConfig dropping unknown keys (forward compat)."""
    valid = {f.name for f in fields(PaperForgeConfig)}
    cleaned = {k: v for k, v in data.items() if k in valid}
    return PaperForgeConfig(**cleaned)


def load_config() -> PaperForgeConfig:
    """Resolve config from disk + project + env, in that precedence order."""
    data: dict[str, Any] = asdict(PaperForgeConfig())          # defaults
    data.update(_read_yaml(_DEFAULT_CONFIG_PATH))               # user
    project_local = Path.cwd() / _PROJECT_CONFIG_NAME
    if project_local.is_file():
        data.update(_read_yaml(project_local))                  # per-project
    data = _apply_env_overrides(data)                           # env vars
    return _coerce(data)


def save_config(cfg: PaperForgeConfig) -> Path:
    """Persist user config to ``~/.paperforge/config.yaml`` and return the path."""
    _DEFAULT_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _DEFAULT_CONFIG_PATH.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(asdict(cfg), fh, sort_keys=True, allow_unicode=True)
    return _DEFAULT_CONFIG_PATH


def reset_config() -> Path:
    return save_config(PaperForgeConfig())


def config_file_path() -> Path:
    return _DEFAULT_CONFIG_PATH


def update_field(name: str, value: Any) -> PaperForgeConfig:
    """Update one field on the persisted config and return the new state."""
    cfg = load_config()
    if name not in {f.name for f in fields(PaperForgeConfig)}:
        raise KeyError(f"Unknown config field: {name}")
    # Cast to the field's annotated type when it's int.
    annotation = next(f.type for f in fields(PaperForgeConfig) if f.name == name)
    if annotation is int or annotation == "int":
        value = int(value)
    setattr(cfg, name, value)
    save_config(cfg)
    return cfg
