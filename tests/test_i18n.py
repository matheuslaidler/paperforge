"""i18n contract: pt_br must not have orphan keys missing in en."""

import yaml

from paperforge.utils.paths import asset


def _load(lang: str) -> dict:
    path = asset("locales", f"{lang}.yaml")
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def test_pt_br_has_no_orphan_keys() -> None:
    en = set(_load("en"))
    pt = set(_load("pt_br"))
    orphans = pt - en
    assert not orphans, f"pt_br has keys missing in en: {sorted(orphans)}"


def test_translator_falls_back_to_english() -> None:
    from paperforge.i18n import Translator
    t = Translator(lang="pt_br")
    # A key that exists in both
    assert t("cli.help.pdf") != "cli.help.pdf"
    # An unknown key falls back to the literal key
    assert t("does.not.exist") == "does.not.exist"
