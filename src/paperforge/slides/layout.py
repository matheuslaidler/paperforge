"""Vertical-stack layout helpers + shrink-to-fit font sizing."""

from __future__ import annotations

from pptx.util import Inches, Pt

from paperforge.slides.parser import Block, parse_table


def estimate_para_height_emu(text: str, font_pt: int, width_emu: int) -> int:
    """Estimate the EMU height of a paragraph given font size and target width."""
    chars_per_inch = 12 * (15.0 / font_pt)
    width_inches = width_emu / int(Inches(1))
    chars_per_line = max(20, int(chars_per_inch * width_inches))
    n_lines = max(1, (len(text) + chars_per_line - 1) // chars_per_line)
    line_h = int(Pt(font_pt * 1.25))
    return n_lines * line_h + int(Pt(6))


def estimate_block_height_emu(block: Block, font_pt: int, width_emu: int) -> int:
    """Estimate EMU height for any block kind."""
    if block.kind in ("para", "quote"):
        assert isinstance(block.payload, str)
        return estimate_para_height_emu(block.payload, font_pt, width_emu)
    if block.kind == "list":
        assert isinstance(block.payload, list)
        return sum(
            estimate_para_height_emu(item, font_pt, width_emu)
            for item in block.payload
        )
    if block.kind == "table":
        assert isinstance(block.payload, list)
        rows = parse_table(block.payload)
        if not rows:
            return 0
        return int(Inches(0.4 + 0.42 * len(rows)))
    if block.kind == "code":
        assert isinstance(block.payload, list)
        line_h = int(Pt((font_pt - 2) * 1.20))
        return len(block.payload) * line_h + int(Pt(10))
    return 0  # image — vertical impact handled by side-column placement


def fit_font_size(
    text_blocks: list[Block],
    width_emu: int,
    available_h_emu: int,
    *,
    start_pt: int = 15,
    min_pt: int = 9,
) -> int:
    """Find the largest font size for which all blocks fit vertically."""
    pt = start_pt
    while pt >= min_pt:
        total = sum(
            estimate_block_height_emu(b, pt, width_emu)
            for b in text_blocks
        )
        if total <= available_h_emu:
            return pt
        pt -= 1
    return min_pt
