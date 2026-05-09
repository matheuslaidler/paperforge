#!/usr/bin/env bash
# Build a standalone PaperForge binary on Linux.
# Output: dist/paperforge
set -euo pipefail

cd "$(dirname "$0")/.."

python -m pip install --upgrade pip
pip install -e .[dev]

# .ico is Windows-only; on Linux the spec falls back to no icon and the
# QApplication uses paper.png at runtime via QApplication.setWindowIcon.
pyinstaller paperforge.spec --noconfirm

echo
echo "Done. Binary at: dist/paperforge"
