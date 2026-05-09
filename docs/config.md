# Configuration

PaperForge stores persistent settings in `~/.paperforge/config.yaml`. The file
is created lazily on first write.

## Resolution order

From lowest to highest precedence:

1. Built-in defaults baked into the package.
2. `~/.paperforge/config.yaml` (global).
3. `paperforge.yaml` in the current working directory (per-project).
4. Environment variables: `PAPERFORGE_LANG`, `PAPERFORGE_BROWSER`.
5. CLI flags (`--lang`, `--browser`).

## Schema

```yaml
lang: en                  # en | pt_br
default_pdf_style: default
default_slide_theme: default
browser: ""               # empty = auto-detect
references_style: abnt    # abnt | none
mathjax_engine: cdn       # cdn | katex-local
mathjax_timeout: 8        # seconds
```

## Common operations

```bash
# Show current state (Rich-rendered table)
paperforge config

# Persist a single field
paperforge config --set lang=pt_br
paperforge config --set browser="C:\Program Files\Google\Chrome\Application\chrome.exe"
paperforge config --set default_pdf_style=academic

# Restore everything to defaults
paperforge config --reset

# Print the absolute path of the config file (useful for editors / scripts)
paperforge config --path
```

## Environment variables

| Variable | Effect |
|----------|--------|
| `PAPERFORGE_LANG` | Overrides `lang` for the current shell |
| `PAPERFORGE_BROWSER` | Overrides browser auto-detection |
| `MPLBACKEND` | Forced to `Agg` automatically; does not require user action |
| `PYTHONIOENCODING` | Forced to `utf-8` automatically (Windows-friendly) |
