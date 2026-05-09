---
title: Sample Talk
subtitle: A demonstration of paperforge slides
author: Matheus Laidler
event: Internal seminar
---

## Slide 1 — Why PaperForge?

- Single command: Markdown → PowerPoint
- Auto-fit fonts when content overflows
- Tables, code blocks, blockquotes
- Image columns when a slide includes a figure

## Slide 2 — Quick numbers

| Metric | Before | After  | Δ |
|--------|--------|--------|---|
| Yield  | 60.3   | **69.3** | +14.9% |
| ROS    | 6.4×   | **2.8×** | −56%   |

## Slide 3 — Pipeline

```
Markdown  →  parser  →  layout  →  python-pptx  →  .pptx
```

> Designed to feel like writing a document, not configuring a tool.

## Slide 4 — Closing

- Run `paperforge slides talk.md` and open the result.
- Customize the cover via YAML frontmatter.
- Pick a theme: `--theme dark`, `--theme minimal`, `--theme nature`.
