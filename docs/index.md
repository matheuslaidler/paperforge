# PaperForge documentation

Welcome. This folder contains long-form guides for each part of the app.
The README covers the basics; these pages are for users who want the full
picture.

- **[GUI guide](gui.md)** — tour of the desktop app (PDF, PowerPoint, Chart tabs).
- [PDF builder](pdf.md) — every flag in `paperforge pdf`, with concrete examples.
- [Slides builder](slides.md) — the `## Slide N` format, frontmatter, themes.
- [Charts](charts.md) — the five templates and YAML schemas (CLI usage).
- [Configuration](config.md) — `~/.paperforge/config.yaml` reference.

## Project layout

```
paperforge/
├── src/paperforge/
│   ├── gui/                # Qt 6 desktop app (default mode)
│   │   ├── app.py
│   │   ├── main_window.py
│   │   ├── pdf_tab.py
│   │   ├── slides_tab.py
│   │   ├── chart_tab/
│   │   └── widgets/
│   ├── pdf/                # md -> pdf builder
│   ├── slides/             # md -> pptx builder
│   ├── charts/             # data -> figure (with five templates)
│   ├── locales/            # en.yaml, pt_br.yaml
│   ├── cli.py              # Typer CLI (kept for scripting)
│   └── paper.png           # custom application icon
├── examples/               # sample inputs
├── tests/                  # pytest suite
├── scripts/                # PyInstaller helpers + icon converter
└── paperforge.spec         # PyInstaller spec used by both build scripts
```

## Author

Matheus Laidler. Released under MIT.
