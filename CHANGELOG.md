# Changelog

All notable changes to PaperForge will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-05-09
### Added
- **Native PySide6 GUI** as the default mode. Double-clicking the executable
  opens a Qt 6 window with three tabs (PDF / PowerPoint / Chart), a status
  bar with language switcher, and a custom application icon.
- **Live matplotlib preview** in the Chart tab — updates while you edit.
- **Editable data tables** with CSV import, color picker, marker/linestyle
  selectors per series.
- **Annotations panel** for the log-scale template: vertical lines, shaded
  bands, and theoretical envelopes (NumPy expressions in a sandbox).
- **Custom icon pipeline**: `scripts/build_icon.py` produces a multi-size
  Windows `.ico` from `src/paperforge/paper.png`. The PyInstaller spec uses
  it automatically. The `scripts/generate_placeholder_icon.py` script gives
  a starter icon if you don't have one yet.
- **PyInstaller spec file** (`paperforge.spec`) — surgical PySide6
  collection (~89 MB final binary, down from ~280 MB with naive collect_all).
- New dependencies: `PySide6>=6.6` and `Pillow>=10.0`.

### Changed
- `paperforge` (no args) now opens the GUI; pass any subcommand to use the
  CLI as before. `--gui` and `--cli` flags select mode explicitly.
- Console entry point renamed to `paperforge-cli`; `paperforge` is now a
  GUI-script that doesn't open a terminal on Windows.
- README rewritten around the desktop app; CLI reference moved further down.

### Removed
- `paperforge/interactive.py` (the Rich text-mode menu) — replaced by the
  GUI.

## [0.1.0] - 2026-05-08
### Added
- Initial release.
- `paperforge pdf` — Markdown to PDF via headless browser (Edge/Chrome/Chromium).
- `paperforge slides` — Markdown to PowerPoint via python-pptx.
- `paperforge chart` — five chart templates (line, bar, log-scale, scatter,
  dose-response) with interactive Rich wizard.
- `paperforge config` — persistent settings in `~/.paperforge/config.yaml`.
- English (default) and Brazilian Portuguese UI strings.
- GitHub Actions release pipeline for Windows/Linux binaries and PyPI publication.
