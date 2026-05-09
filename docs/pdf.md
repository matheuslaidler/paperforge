# `paperforge pdf` — Markdown to PDF

Render any Markdown file into an A4 PDF using a Chromium-family browser
(Edge, Chrome, Chromium, or Brave) running headless.

## Usage

```bash
paperforge pdf <input.md> [output.pdf]
```

If you omit `output.pdf`, PaperForge writes alongside the input
(`paper.md → paper.pdf`).

## Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--style` | `default` | `default \| minimal \| academic` |
| `--css PATH` | — | Custom stylesheet (overrides `--style`) |
| `--orientation` | `portrait` | `portrait \| landscape` |
| `--margin-top/-bottom/-left/-right` | `2cm/2cm/1.8cm/1.8cm` | Page margins |
| `--mathjax / --no-mathjax` | on | LaTeX rendering via MathJax |
| `--mathjax-engine` | `cdn` | `cdn \| katex-local` |
| `--mathjax-timeout` | `8` | Seconds to wait for MathJax to render |
| `--browser PATH` | auto | Override browser detection |
| `--references-style` | `abnt` | `abnt \| none` |
| `--keep-html` | off | Keep the intermediate HTML file |
| `--open` | off | Open the PDF after build |
| `--title TEXT` | first H1 / filename | HTML `<title>` element |

## Built-in styles

- **default** — academic blue accent (#2E86AB), tables with zebra striping,
  ABNT-friendly references section.
- **minimal** — Georgia serif, no colors, clean for printing.
- **academic** — strict ABNT (Times New Roman 12pt, 1.5 line height, indented
  paragraphs).

## Custom CSS

Pass any CSS file via `--css path/to/brand.css`. The Markdown is rendered to a
plain HTML5 document; your CSS controls everything from `body` onward.

A minimal example:

```css
@page { size: A4 portrait; margin: 2cm; }
body { font-family: 'Inter', sans-serif; line-height: 1.6; }
h1, h2 { color: #1B4332; }
```

## ABNT references

When `--references-style abnt` (default), the first heading whose text matches
`References`, `Bibliography`, or `Referências bibliográficas` triggers a
hanging-indent block on every paragraph that follows. This produces the
classical ABNT layout where author surnames stand out at the left margin.

## Browser selection order

1. `--browser PATH` flag.
2. `browser` field in `~/.paperforge/config.yaml`.
3. `PAPERFORGE_BROWSER` environment variable.
4. Auto-detect (OS-specific candidates).

If no browser is found, the command exits with a clear error message asking
the user to install one of: Microsoft Edge, Google Chrome, Chromium, Brave.
