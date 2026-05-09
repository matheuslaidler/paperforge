"""Tiny i18n layer — flat-key YAML dictionaries with English fallback."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

import yaml

from paperforge.config import load_config
from paperforge.utils.paths import asset

SUPPORTED_LANGS = ("en", "pt_br")
_DEFAULT_LANG = "en"


@lru_cache(maxsize=4)
def _load_locale(lang: str) -> dict[str, str]:
    path = asset("locales", f"{lang}.yaml")
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return {k: str(v) for k, v in data.items()} if isinstance(data, dict) else {}


def active_lang() -> str:
    """Resolve current language from env > config > default."""
    env = os.environ.get("PAPERFORGE_LANG")
    if env in SUPPORTED_LANGS:
        return env
    cfg_lang = load_config().lang
    return cfg_lang if cfg_lang in SUPPORTED_LANGS else _DEFAULT_LANG


class Translator:
    """Lookup with fallback chain: requested lang -> English -> raw key."""

    def __init__(self, lang: str | None = None):
        self.lang = lang or active_lang()
        self._strings = _load_locale(self.lang)
        self._fallback = _load_locale(_DEFAULT_LANG) if self.lang != _DEFAULT_LANG else {}

    def t(self, _key: str, /, **kwargs: Any) -> str:
        s = self._strings.get(_key) or self._fallback.get(_key) or _key
        return s.format(**kwargs) if kwargs else s

    # Allow ``translator("key.path")`` directly for ergonomic call sites.
    __call__ = t


# Module-level convenience: a translator bound to the active language at import.
_translator = Translator()


def t(_key: str, /, **kwargs: Any) -> str:
    """Translate ``_key`` using the active translator.

    The first parameter is positional-only (``/``) so callers can safely use
    ``key`` as a format kwarg (e.g. ``t("config.set.ok", key="lang", value="en")``).
    """
    return _translator.t(_key, **kwargs)


def reload(lang: str | None = None) -> None:
    """Force-reload the singleton, e.g. after a ``--lang`` CLI flag."""
    global _translator
    _translator = Translator(lang)
