# `paperforge slides` — Markdown to PowerPoint

Convert a Markdown file with `## Slide N` blocks into a `.pptx` deck.

## Source format

Each slide is delimited by an H2 heading that matches one of:

- `## Slide 1 — Title here`
- `## Slide 1: Title here`
- `## 1 - Title here`

Inside a slide block PaperForge accepts:

- Paragraphs (with `**bold**` runs preserved).
- Bullet lists (`- item` or `* item`).
- Tables (GitHub-flavored Markdown).
- Fenced code blocks (`` ```code ``` ``).
- Blockquotes (`> quoted text`).
- One image per slide (`![alt](path/to/file.png)`); rendered in a right
  column when present.

## Cover slide

Two ways to drive the cover:

### YAML frontmatter

```markdown
---
title: My talk
subtitle: Deeper dive
author: First Last
event: Conference 2026
extra: Sponsored by ACME
---

## Slide 1 — Introduction
…
```

### First slide

If no frontmatter is found, the first `## Slide 1 …` block is mirrored as the
cover with its title and first paragraph.

Disable the cover entirely with `--no-cover`.

## Themes

Available built-in themes (pick one with `--theme NAME`):

- `default` — academic blue (#2E86AB) on white.
- `dark` — dark slate background, high-contrast accents.
- `minimal` — black on white, no decoration.
- `nature` — earthy green on cream.

Or write your own theme YAML and pass it via `--theme-file path/to/theme.yaml`:

```yaml
name: my-theme
primary: "#1B4332"
secondary: "#52B788"
accent: "#D62828"
text: "#000000"
muted: "#666666"
background: "#FFFFFF"
code_bg: "#F5F5F5"
```

## Aspect ratio

`--aspect 16:9` (default) or `--aspect 4:3`.

## Footer

Footer text supports `{n}` (current slide) and `{total}` placeholders:

```bash
paperforge slides talk.md --footer-template "{n} of {total}"
```

Set it to an empty string to suppress the footer.

## Auto-fit fonts (shrink-to-fit)

If the content of a slide overflows the available height, PaperForge reduces
the body font size step by step (15pt → 9pt) until everything fits. A warning
prints which slide was shrunk and to what size.
