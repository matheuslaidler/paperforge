"""Color themes shared between PDF (CSS variable) and slides/charts (RGB tuples)."""

from __future__ import annotations

from dataclasses import dataclass, field

# Validated scientific palette (battle-tested across PDF, slides and charts).
PRIMARY = "#2E86AB"
SECONDARY = "#06A77D"
ACCENT = "#D62246"
WARNING = "#F4A261"
NEUTRAL = "#5C5C5C"

DEFAULT_PALETTE: list[str] = [PRIMARY, SECONDARY, ACCENT, WARNING, NEUTRAL,
                              "#9D4EDD", "#FFB703", "#3A86FF"]
COLORBLIND_PALETTE: list[str] = ["#0072B2", "#E69F00", "#009E73", "#CC79A7",
                                 "#56B4E9", "#D55E00", "#F0E442", "#000000"]


@dataclass
class ColorTheme:
    """Theme for slides and plot accents."""

    name: str = "default"
    primary: str = PRIMARY
    secondary: str = SECONDARY
    accent: str = ACCENT
    text: str = "#222222"
    muted: str = "#666666"
    background: str = "#FFFFFF"
    code_bg: str = "#F4F4F4"
    palette: list[str] = field(default_factory=lambda: list(DEFAULT_PALETTE))


THEMES: dict[str, ColorTheme] = {
    "default": ColorTheme(name="default"),
    "minimal": ColorTheme(
        name="minimal",
        primary="#222222", secondary="#666666", accent="#222222",
        text="#000000", muted="#888888", background="#FFFFFF",
        code_bg="#F8F8F8",
    ),
    "dark": ColorTheme(
        name="dark",
        primary="#5DADE2", secondary="#48C9B0", accent="#EC7063",
        text="#ECF0F1", muted="#95A5A6", background="#1B2631",
        code_bg="#283747",
    ),
    "nature": ColorTheme(
        name="nature",
        primary="#2D6A4F", secondary="#52B788", accent="#D62828",
        text="#1B4332", muted="#74817C", background="#FEFAE0",
        code_bg="#F2EFD5",
    ),
}


def get(name: str) -> ColorTheme:
    if name not in THEMES:
        raise KeyError(f"Unknown theme '{name}'. Available: {sorted(THEMES)}")
    return THEMES[name]
