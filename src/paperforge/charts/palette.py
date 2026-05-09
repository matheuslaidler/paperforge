"""Validated chart palettes."""

from paperforge.theme import COLORBLIND_PALETTE, DEFAULT_PALETTE  # re-export

PALETTES: dict[str, list[str]] = {
    "default": DEFAULT_PALETTE,
    "colorblind": COLORBLIND_PALETTE,
}


def get(name: str) -> list[str]:
    if name not in PALETTES:
        raise KeyError(
            f"Unknown palette '{name}'. Available: {sorted(PALETTES)}"
        )
    return PALETTES[name]
