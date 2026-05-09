# `paperforge chart` — Scientific figures

Five built-in templates plus an interactive wizard.

## Templates

| Name | Best for |
|------|----------|
| `line` | Multiple time series, kinetic curves |
| `bar` | Grouped bar charts with value labels |
| `log-scale` | Survival/decay curves, exponential growth |
| `scatter` | Correlation analysis (optional regression line) |
| `dose-response` | Viability vs concentration / dose |

## Three input modes

### 1. Interactive wizard

```bash
paperforge chart
```

A Rich-powered prompt walks you through template selection, axis labels,
input data (CSV path or empty for inline), and output path. A sibling
`*.paperforge.yaml` file is saved next to the PNG so the result is
reproducible.

### 2. Template + CSV + flags

Quickest one-liner:

```bash
paperforge chart --template line --csv data.csv \
                 --x-col t --y-col viability \
                 --title "CLS" --xlabel "Days" --ylabel "% CFU" \
                 --log-y --source "Fabrizio 2003" --output cls.png
```

Useful flags:

- `--csv PATH` — load data from CSV.
- `--x-col`, `--y-col`, `--series-col` — column names.
- `--title`, `--xlabel`, `--ylabel`, `--source`.
- `--log-x`, `--log-y` — turn on log axes.
- `--dpi`, `--width`, `--height` — figure size.
- `--format png,svg,pdf` — multiple outputs at once.
- `--palette default|colorblind` — color cycle.

### 3. Template + YAML config (recommended for reproducibility)

```bash
paperforge chart --config my_chart.yaml --output figure.png
```

YAML schema example (log-scale):

```yaml
template: log-scale
title: "Survival vs time"
xlabel: "Days"
ylabel: "Viability (% CFU)"
log_y: true

series:
  - label: "WT"
    x: [1, 3, 5, 7, 9]
    y: [100, 80, 35, 10, 4]
    marker: o
  - label: "SOD-OE"
    x: [1, 3, 5, 7, 9]
    y: [100, 90, 70, 40, 18]
    marker: ^

vlines:
  - x: 7
    label: "Day 7"
    color: gray

bands:
  - x_start: 5
    x_end: 9
    color: "#06A77D"
    alpha: 0.10
```

Bar template uses `categories` + numeric `values` per series:

```yaml
template: bar
title: "Yield ± treatment"
ylabel: "Yield (g/L)"
categories: ["A 30°C", "A 40°C", "B 30°C", "B 40°C"]
series:
  - label: "Control"
    values: [60.3, 35.2, 66.1, 45.4]
  - label: "Treated"
    values: [69.3, 44.0, 73.6, 55.3]
```

## Source citation box

Every chart can carry a citation rendered in a rounded box at the bottom-right
corner. Either pass `--source "..."` or include a `source:` field in the YAML
config. The visual style is identical across all templates so figures look
consistent in a report or slide deck.
