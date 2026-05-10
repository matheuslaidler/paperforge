# PaperForge

> Desktop app that turns Markdown into publication-ready PDFs, PowerPoint decks and scientific charts.

[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)
[![Platforms](https://img.shields.io/badge/platforms-Windows%20%7C%20Linux-lightgrey.svg)](#install)

PaperForge is a single executable with three tabs:

- **PDF** — Markdown → A4 PDF (default / minimal / academic styles, MathJax, ABNT references).
- **PowerPoint** — Markdown → `.pptx` (cover from YAML frontmatter, four themes, auto-fit).
- **Chart** — five scientific templates (line, bar, log-scale, scatter, dose-response) with
  an editable data table and live matplotlib preview. Each template ships with example
  data ready to render — open the tab and you already see a chart.

No LaTeX. No Pandoc. No `wkhtmltopdf`. Just one binary plus any Chromium-family browser
(Edge / Chrome / Chromium / Brave) for the PDF backend.

---

## Install

| Platform | How |
|---|---|
| **Windows** | Download `paperforge.exe` from [Releases](https://github.com/matheuslaidler/paperforge/releases) and double-click. |
| **Linux** | Download `paperforge-linux-x64`, `chmod +x paperforge-linux-x64`, run it. |
| **Source** | `pip install -e .` then `paperforge`. |

The `.exe` is ~89 MB; the Linux binary ~116 MB. Both bundle Python and Qt 6.

## Use

Just open the app and pick a tab.

### PDF / PowerPoint
Drag a `.md` file into the source field, set output path, click **Build**. Logs stream live.

### Including charts in slides
Generate a chart in the **Chart** tab → click **Save figure…** to export it as
PNG → reference it in your slide source with
`![alt text](path/to/chart.png)`. The image automatically lands on the
right-hand column of that slide while bullets/text take the left column.

### Chart
1. Pick a template — example data appears immediately.
2. Edit series in the data table, or click **Import CSV…**.
3. *(log-scale only)* add vertical lines, shaded bands, theoretical envelopes (NumPy formulas evaluated in a sandbox, e.g. `10 * (1 - x / 90) ** 1`).
4. Tweak DPI / size / palette in *Style*.
5. Click **Save figure…** to export PNG/SVG/PDF.

Every template comes pre-loaded with a real example. The `log-scale` template ships with
a real fermentation study (biomass × ethanol on log-Y, 6 series + 3 Ghose-Tyagi envelopes + the
industrial VHG band) — switch to it and you have a full publication-ready chart in one
click.

## CLI mode (advanced)

The same binary works as a CLI:

```bash
paperforge pdf paper.md
paperforge slides talk.md
paperforge chart            # interactive Rich wizard
paperforge --help
```

Pass any subcommand and the GUI is bypassed. Useful for scripting / CI.

## Build from source

```bash
git clone https://github.com/matheuslaidler/paperforge.git
cd paperforge
pip install -e .[dev]
python -m paperforge        # opens the GUI
pytest -q                   # 25 tests
```

### Build the standalone binary

```bash
# Windows
.\scripts\build_windows.bat

# Linux
./scripts/build_linux.sh
```

Both call `python scripts/build_icon.py` (PNG → multi-size ICO) then `pyinstaller paperforge.spec`.
Replace `src/paperforge/paper.png` (must be 512×512 RGBA, transparent background recommended)
to brand the app — the build script picks it up automatically.

## Configuration

```yaml
# ~/.paperforge/config.yaml
lang: en                  # en | pt_br
default_pdf_style: default
default_slide_theme: default
browser: ""               # empty = auto-detect (Edge/Chrome/Chromium/Brave)
references_style: abnt    # abnt | none
mathjax_engine: cdn       # cdn | katex-local
mathjax_timeout: 8
```

Toggle the language at the bottom-right of the main window or via
`paperforge config --set lang=pt_br`.

## Project layout

```
paperforge/
├── src/paperforge/
│   ├── gui/             ← PySide6 desktop app (default mode)
│   ├── pdf/             ← Markdown → PDF builder
│   ├── slides/          ← Markdown → PPTX builder
│   ├── charts/          ← five chart templates + builder
│   ├── locales/         ← en.yaml, pt_br.yaml
│   ├── cli.py           ← Typer CLI (kept for scripting)
│   └── paper.png        ← app icon (512×512 RGBA)
├── examples/            ← sample inputs
├── tests/               ← pytest suite (25 tests)
├── scripts/             ← icon converter + build helpers
└── paperforge.spec      ← PyInstaller spec (used by both build scripts)
```

## Author & License

Built by **Matheus Laidler** ([@matheuslaidler](https://github.com/matheuslaidler)).
Released under the [MIT License](LICENSE).
