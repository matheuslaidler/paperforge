# GUI guide

PaperForge's GUI is the default experience. This page walks through every
panel.

## Launching

- **Standalone binary**: double-click `paperforge.exe` (or run
  `./paperforge` on Linux).
- **From Python**: `paperforge` (no arguments) or `python -m paperforge`.

The first launch creates `~/.paperforge/config.yaml` with default settings
and a `cache/` folder for downloaded images.

## Layout

```
┌────────────────────────────────────────────────────┐
│ File   Help                                       │   ← menu bar
├────────────────────────────────────────────────────┤
│ [ PDF ] [ PowerPoint ] [ Chart ]                  │   ← tabs
│                                                    │
│   ... currently selected tab ...                  │
│                                                    │
├────────────────────────────────────────────────────┤
│ Ready              [ English ▾ ]    v0.2.0        │   ← status bar
└────────────────────────────────────────────────────┘
```

The language combo on the right of the status bar persists your choice in
`~/.paperforge/config.yaml`. Switching the language re-translates every
label without restarting the app.

## PDF tab

Two file pickers (drag & drop supported), four collapsible groups
(Styling / Layout / Advanced), and a build button. Logs stream into the
viewer below as the PDF is generated.

| Field | Meaning |
|-------|---------|
| **Source Markdown** | The `.md` file to convert. |
| **Output file** | Defaults to `<source>.pdf`. |
| **Style** | Built-in stylesheet: `default`, `minimal`, `academic`. |
| **Custom CSS** | Path to a stylesheet that overrides the built-in. |
| **Orientation** | `portrait` (default) or `landscape`. |
| **Margins** | Top/Right/Bottom/Left, e.g. `2cm`. |
| **References style** | `abnt` (hanging-indent on the bibliography section) or `none`. |
| **MathJax** | Render LaTeX formulas (uses CDN by default). |
| **Keep intermediate HTML** | Useful for debugging. |
| **Open PDF when finished** | Launches the system viewer. |

## PowerPoint tab

| Field | Meaning |
|-------|---------|
| **Source Markdown** | A file with `## Slide N — Title` blocks. |
| **Output file** | Defaults to `<source>.pptx`. |
| **Theme** | `default`, `dark`, `minimal`, `nature`. |
| **Aspect ratio** | `16:9` or `4:3`. |
| **Generate cover slide** | Synthesize a cover from YAML frontmatter. |
| **Footer template** | Supports `{n}` (slide #) and `{total}`. |

The optional YAML frontmatter:

```markdown
---
title: My Talk
subtitle: A short subtitle
author: First Last
event: Conference 2026
---

## Slide 1 — Introduction
- Bullet point
```

## Chart tab

Layout: a section list on the left, content panel in the middle, live
matplotlib preview on the right.

### 1. Template & metadata

Pick one of five templates: `line`, `bar`, `log-scale`, `scatter`,
`dose-response`. Set title, axis labels, citation. The Annotations section
is only enabled when `log-scale` is selected.

### 2. Data

Two layouts depending on the template:

- **line / log-scale / scatter / dose-response**: list of series on the
  left (with colour swatches), editable XY table on the right. Use
  *Import CSV…* to load tabular data; you'll be prompted for the X / Y /
  Series columns.
- **bar**: editable categories column + one row of values per series.

Buttons:

- `+ Series` — add an empty series with the next palette color.
- `− Series` — remove the highlighted one.
- `Duplicate` — clone the current series for fast variants.
- `Import CSV…` — opens the CSV import dialog.
- `Clear` — drop everything.
- `+ / −` (small buttons) — add/remove a row in the XY table.

Click the colour swatch to open a colour picker.

### 3. Annotations (log-scale only)

Three editable tables:

- **Vertical lines**: `(x, label, color, linestyle, alpha)`.
- **Bands**: `(x_start, x_end, label, color, alpha)`.
- **Envelopes**: `(label, formula, color, alpha)` where the formula is a
  Python expression evaluated in a sandbox with `np` and `x` available.
  Examples:
  - `10 * (1 - x / 90) ** 1` (Levenspiel ethanol inhibition).
  - `np.exp(-x / 40)` (exponential decay).
  - `5 + 0.1 * x` (linear).

If the formula raises (zero-division, syntax error), the envelope is
silently skipped and the rest of the chart renders normally.

### 4. Style

DPI (72–600), figure size in inches, palette (`default`, `colorblind`),
legend location, log-X / log-Y, and output formats. Tick more than one
format box to write PNG, SVG and/or PDF in one click.

### Live preview

The right pane has a matplotlib `FigureCanvasQTAgg` plus the standard
toolbar (zoom, pan, save). Re-renders are debounced 150 ms after the last
change so typing in the data table feels snappy.

When data is missing, the preview shows a placeholder message instead of
crashing.

### Save figure

Click **Save figure…** to write the image. The button writes every format
checked in *Style* (e.g. `chart.png` and `chart.svg`) and shows the path
in a confirmation dialog.

## Reproducing the Brandão case (`biomassa × etanol log`)

A complete walkthrough that produces a chart equivalent to the original
hand-coded `biomassa_etanol_log.py`:

1. Template tab: pick `log-scale`. Set title, axis labels, source citation.
2. Style tab: enable *Log scale on Y*.
3. Data tab: add 6 series (TISTR 30 °C ±NAC, TISTR 40 °C ±NAC, BY4742 40 °C ±NAC),
   set markers (`s`, `^`, `v`) and colors. Fill the XY tables with the
   Burphan 2018 timepoints.
4. Annotations tab:
   - Vertical line at `x = 50`, label "inhibition limit".
   - Band from 60 to 75, color `#06A77D`, alpha `0.10` (industrial VHG zone).
   - Three envelopes: `10 * (1 - x / 75) ** 1`, `10 * (1 - x / 90) ** 1`,
     `10 * (1 - x / 105) ** 1` (Ghose-Tyagi).
5. Click **Save figure…** to export a publication-grade PNG.
