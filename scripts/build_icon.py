"""Convert ``src/paperforge/paper.png`` into a multi-size Windows ``.ico``.

Run this once before building the .exe; the .ico is committed-friendly so
it can also be checked in if desired.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "paperforge" / "paper.png"
DST = Path(__file__).resolve().parent / "paper.ico"


def main() -> int:
    if not SRC.is_file():
        print(f"ERROR: source PNG not found at {SRC}", file=sys.stderr)
        return 1
    img = Image.open(SRC)
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64),
             (128, 128), (256, 256)]
    img.save(DST, format="ICO", sizes=sizes)
    kb = DST.stat().st_size / 1024
    print(f"OK: {DST} ({kb:.1f} KB, {len(sizes)} sizes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
