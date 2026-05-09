"""Generate a placeholder paper.png if the user has not provided one.

Produces a 512x512 PNG with **transparent background** so the icon looks
clean on the taskbar, dock, and any window-manager backdrop. Replace with
your own logo by simply overwriting ``src/paperforge/paper.png`` (must
also be 512x512 with alpha).
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
DST = ROOT / "src" / "paperforge" / "paper.png"


def main() -> int:
    SIZE = 512
    PRIMARY = (46, 134, 171, 255)         # #2E86AB
    PRIMARY_SHADOW = (38, 110, 142, 255)
    SECONDARY = (6, 167, 125, 255)         # #06A77D
    PAPER_BG = (255, 255, 255, 255)
    PAPER_BORDER = (200, 210, 220, 255)
    INK = (31, 41, 51, 255)                # #1F2933
    FOLD = (210, 220, 230, 255)

    canvas = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))  # fully transparent
    draw = ImageDraw.Draw(canvas)

    # Rounded blue badge that frames the page
    pad = 56
    badge_box = (pad, pad, SIZE - pad, SIZE - pad)
    draw.rounded_rectangle(badge_box, radius=64, fill=PRIMARY)

    # Inner subtle highlight
    inner_top = (badge_box[0] + 4, badge_box[1] + 4,
                 badge_box[2] - 4, badge_box[1] + 14)

    # White paper rectangle, slightly offset down-right
    paper_box = (pad + 36, pad + 28, SIZE - pad + 14, SIZE - pad + 14)
    draw.rounded_rectangle(
        paper_box, radius=20, fill=PAPER_BG,
        outline=PAPER_BORDER, width=3,
    )

    # Folded corner triangle (top-right of the paper)
    fx0, fy0 = paper_box[2] - 90, paper_box[1]
    draw.polygon(
        [(fx0, fy0), (paper_box[2], fy0), (paper_box[2], fy0 + 90)],
        fill=FOLD,
    )
    # subtle shadow line on the fold
    draw.line(
        [(fx0, fy0), (paper_box[2], fy0 + 90)],
        fill=PAPER_BORDER, width=2,
    )

    # Lines on the paper (text body)
    line_x0 = paper_box[0] + 38
    line_x1 = paper_box[2] - 74
    line_y = paper_box[1] + 78
    line_h = 18
    line_gap = 34
    line_widths = [1.0, 0.86, 0.94, 0.78, 0.92]
    colors = [PRIMARY, INK, INK, INK, INK]
    for w_factor, color in zip(line_widths, colors):
        x1 = int(line_x0 + (line_x1 - line_x0) * w_factor)
        draw.rounded_rectangle(
            (line_x0, line_y, x1, line_y + line_h),
            radius=8, fill=color,
        )
        line_y += line_gap

    # Tiny green chart bars at the bottom right of the paper
    bx = paper_box[2] - 138
    by = paper_box[3] - 32
    heights = [44, 64, 28, 80]
    for i, h in enumerate(heights):
        draw.rounded_rectangle(
            (bx + i * 22, by - h, bx + i * 22 + 16, by),
            radius=4, fill=SECONDARY,
        )

    DST.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(DST, format="PNG")
    print(
        f"OK: transparent icon written to {DST} "
        f"({DST.stat().st_size / 1024:.1f} KB)"
    )
    print(
        "Replace this file with your own 512x512 RGBA PNG (with transparency) "
        "to customise the app icon."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
