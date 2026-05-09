"""Shared pytest fixtures."""

from __future__ import annotations

import os
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolate_paperforge_home(tmp_path, monkeypatch):
    """Redirect ~/.paperforge to a tmp dir so tests do not touch the user home."""
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setenv("HOME", str(fake_home))
    monkeypatch.setenv("USERPROFILE", str(fake_home))  # Windows
    # Force reload of i18n singleton against fresh config.
    import paperforge.i18n as i18n_mod
    i18n_mod._load_locale.cache_clear()
    i18n_mod.reload()
    yield
    # nothing to clean: tmp_path is auto-removed.


@pytest.fixture
def sample_md(tmp_path: Path) -> Path:
    p = tmp_path / "sample.md"
    p.write_text(
        "# Title\n\n"
        "## Sumário\n\n"
        "1. [Introdução](#1-introdução)\n\n"
        "## 1. Introdução\n\n"
        "Some text with **bold** and *italic*.\n\n"
        "| A | B |\n|---|---|\n| 1 | 2 |\n\n"
        "## 2. Referências bibliográficas (ABNT)\n\n"
        "AUTHOR, A. Sample reference. **Journal**, v. 1, p. 1, 2026.\n",
        encoding="utf-8",
    )
    return p
