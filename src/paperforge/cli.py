"""Top-level Typer application — wires every subcommand."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.table import Table

from paperforge import __version__
from paperforge import config as config_mod
from paperforge import i18n
from paperforge.utils.logging import console, error, ok

app = typer.Typer(
    name="paperforge",
    help=i18n.t("cli.app.help"),
    no_args_is_help=True,
    rich_markup_mode="rich",
    add_completion=False,
)


# --------------------------------------------------------------------------- #
#  Root callback (global flags)                                               #
# --------------------------------------------------------------------------- #
def _version_callback(value: bool) -> None:
    if value:
        console.print(f"[accent]paperforge[/] {__version__}")
        raise typer.Exit()


@app.callback()
def root(
    version: Optional[bool] = typer.Option(
        None, "--version", "-V", callback=_version_callback, is_eager=True,
        help="Print version and exit.",
    ),
    lang: Optional[str] = typer.Option(
        None, "--lang", help=i18n.t("cli.option.lang"),
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help=i18n.t("cli.option.verbose"),
    ),
) -> None:
    """Global options. Subcommands run after this returns."""
    if lang:
        i18n.reload(lang)
    if verbose:
        # Future hook: configure log level globally.
        console.print("[muted]verbose mode on[/]")


# --------------------------------------------------------------------------- #
#  paperforge pdf                                                             #
# --------------------------------------------------------------------------- #
@app.command(help=i18n.t("cli.help.pdf"))
def pdf(
    input: Path = typer.Argument(..., exists=True, readable=True,
                                 help="Markdown source file."),
    output: Optional[Path] = typer.Argument(None, help="Output PDF (default: <input>.pdf)."),
    style: str = typer.Option("default", "--style", "-s",
                              help="Built-in style: default | minimal | academic."),
    css: Optional[Path] = typer.Option(None, "--css",
                                       help="Custom CSS file (overrides --style)."),
    orientation: str = typer.Option("portrait", "--orientation",
                                    help="portrait | landscape"),
    margin_top: str = typer.Option("2cm", "--margin-top"),
    margin_bottom: str = typer.Option("2cm", "--margin-bottom"),
    margin_left: str = typer.Option("1.8cm", "--margin-left"),
    margin_right: str = typer.Option("1.8cm", "--margin-right"),
    mathjax: bool = typer.Option(True, "--mathjax/--no-mathjax",
                                 help="Render LaTeX formulas via MathJax."),
    mathjax_engine: str = typer.Option("cdn", "--mathjax-engine",
                                       help="cdn | katex-local"),
    mathjax_timeout: int = typer.Option(8, "--mathjax-timeout",
                                        help="Seconds to wait for MathJax to render."),
    browser: Optional[Path] = typer.Option(None, "--browser",
                                           help="Override browser auto-detection."),
    references_style: str = typer.Option("abnt", "--references-style",
                                         help="abnt | none"),
    keep_html: bool = typer.Option(False, "--keep-html",
                                   help="Keep intermediate HTML for debugging."),
    open_after: bool = typer.Option(False, "--open",
                                    help="Open the resulting PDF after build."),
    title: Optional[str] = typer.Option(None, "--title",
                                        help="HTML <title>; default = first H1 or filename."),
) -> None:
    """Build a PDF from Markdown."""
    from paperforge.pdf.builder import PDFBuilder, PDFBuildOptions

    out = output or input.with_suffix(".pdf")
    opts = PDFBuildOptions(
        style=style,
        css_path=css,
        orientation=orientation,
        margins=(margin_top, margin_right, margin_bottom, margin_left),
        mathjax=mathjax,
        mathjax_engine=mathjax_engine,
        mathjax_timeout=mathjax_timeout,
        browser=browser,
        references_style=references_style,
        keep_html=keep_html,
        title=title,
    )
    try:
        builder = PDFBuilder(opts)
        result = builder.build(input, out)
    except FileNotFoundError as exc:
        error(str(exc))
        raise typer.Exit(code=1) from exc
    ok(i18n.t("pdf.ok",
              path=str(result.path),
              size_kb=result.size_kb,
              pages=result.pages))
    if open_after:
        _open_path(result.path)


# --------------------------------------------------------------------------- #
#  paperforge slides                                                          #
# --------------------------------------------------------------------------- #
@app.command(help=i18n.t("cli.help.slides"))
def slides(
    input: Path = typer.Argument(..., exists=True, readable=True,
                                 help="Markdown source file with ## Slide N blocks."),
    output: Optional[Path] = typer.Argument(None, help="Output PPTX (default: <input>.pptx)."),
    theme: str = typer.Option("default", "--theme",
                              help="default | dark | minimal | nature"),
    theme_file: Optional[Path] = typer.Option(None, "--theme-file",
                                              help="Custom theme YAML."),
    aspect: str = typer.Option("16:9", "--aspect", help="16:9 | 4:3"),
    cover: bool = typer.Option(True, "--cover/--no-cover",
                               help="Synthesize cover slide."),
    footer_template: str = typer.Option("{n} / {total}", "--footer-template",
                                        help="Footer text; supports {n} and {total}."),
) -> None:
    """Build a PowerPoint deck from Markdown."""
    from paperforge.slides.builder import SlideBuildOptions, SlideBuilder

    out = output or input.with_suffix(".pptx")
    opts = SlideBuildOptions(
        theme=theme,
        theme_file=theme_file,
        aspect=aspect,
        cover=cover,
        footer_template=footer_template,
    )
    builder = SlideBuilder(opts)
    result = builder.build(input, out)
    ok(i18n.t("slides.ok", path=str(result.path), slides=result.slide_count))


# --------------------------------------------------------------------------- #
#  paperforge chart                                                           #
# --------------------------------------------------------------------------- #
@app.command(help=i18n.t("cli.help.chart"))
def chart(
    template: Optional[str] = typer.Option(None, "--template", "-t",
                                           help="line | bar | log-scale | scatter | dose-response"),
    config: Optional[Path] = typer.Option(None, "--config", "-c",
                                          help="YAML config file."),
    csv: Optional[Path] = typer.Option(None, "--csv", help="CSV data file."),
    output: Optional[Path] = typer.Option(None, "--output", "-o",
                                          help="Output path (without extension if multiple formats)."),
    title: Optional[str] = typer.Option(None, "--title"),
    xlabel: Optional[str] = typer.Option(None, "--xlabel"),
    ylabel: Optional[str] = typer.Option(None, "--ylabel"),
    source: Optional[str] = typer.Option(None, "--source", help="Citation / data source."),
    log_y: bool = typer.Option(False, "--log-y", help="Set Y axis to log scale."),
    log_x: bool = typer.Option(False, "--log-x", help="Set X axis to log scale."),
    dpi: int = typer.Option(150, "--dpi"),
    width: float = typer.Option(8.5, "--width", help="Figure width in inches."),
    height: float = typer.Option(5.5, "--height", help="Figure height in inches."),
    formats: str = typer.Option("png", "--format",
                                help="Comma-separated: png,svg,pdf"),
    palette: str = typer.Option("default", "--palette",
                                help="default | colorblind"),
    x_col: Optional[str] = typer.Option(None, "--x-col"),
    y_col: Optional[str] = typer.Option(None, "--y-col"),
    series_col: Optional[str] = typer.Option(None, "--series-col",
                                             help="Column to split into series."),
) -> None:
    """Create a scientific chart."""
    from paperforge.charts.builder import ChartBuildRequest, build_chart
    from paperforge.charts.wizard import run_wizard

    if not template and not config and not csv:
        # No inputs at all -> launch interactive wizard.
        run_wizard()
        return

    req = ChartBuildRequest(
        template=template,
        config_file=config,
        csv=csv,
        output=output,
        title=title,
        xlabel=xlabel,
        ylabel=ylabel,
        source=source,
        log_y=log_y,
        log_x=log_x,
        dpi=dpi,
        width=width,
        height=height,
        formats=tuple(s.strip() for s in formats.split(",")),
        palette=palette,
        x_col=x_col,
        y_col=y_col,
        series_col=series_col,
    )
    result = build_chart(req)
    ok(i18n.t("chart.ok", path=str(result.path)))


# --------------------------------------------------------------------------- #
#  paperforge config                                                          #
# --------------------------------------------------------------------------- #
@app.command(help=i18n.t("cli.help.config"))
def config(
    set_kv: Optional[str] = typer.Option(None, "--set",
                                         help="KEY=VALUE (e.g. lang=pt_br)."),
    reset: bool = typer.Option(False, "--reset",
                               help="Restore default configuration."),
    show_path: bool = typer.Option(False, "--path",
                                   help="Print the config file path and exit."),
) -> None:
    """Show or change persistent settings."""
    if show_path:
        console.print(str(config_mod.config_file_path()))
        return

    if reset:
        config_mod.reset_config()
        ok(i18n.t("config.reset.ok"))
        return

    if set_kv:
        if "=" not in set_kv:
            error(i18n.t("config.set.malformed", raw=set_kv))
            raise typer.Exit(code=2)
        key, _, value = set_kv.partition("=")
        try:
            config_mod.update_field(key.strip(), value.strip())
        except KeyError:
            from dataclasses import fields
            valid = ", ".join(f.name for f in fields(config_mod.PaperForgeConfig))
            error(i18n.t("config.set.invalid", key=key, keys=valid))
            raise typer.Exit(code=2)
        ok(i18n.t("config.set.ok", key=key.strip(), value=value.strip()))
        return

    _print_config()


def _print_config() -> None:
    cfg = config_mod.load_config()
    table = Table(title=i18n.t("config.printed.header"), show_lines=False)
    table.add_column("Key", style="accent")
    table.add_column("Value")
    from dataclasses import asdict
    for k, v in asdict(cfg).items():
        table.add_row(k, str(v) if v != "" else "[muted]<auto>[/]")
    console.print(table)
    console.print(
        i18n.t("config.printed.path", path=str(config_mod.config_file_path()))
    )


# --------------------------------------------------------------------------- #
#  Helpers                                                                    #
# --------------------------------------------------------------------------- #
def _open_path(path: Path) -> None:
    """Open a file with the OS default app (cross-platform)."""
    import platform
    import subprocess
    system = platform.system()
    try:
        if system == "Windows":
            import os
            os.startfile(path)  # type: ignore[attr-defined]
        elif system == "Darwin":
            subprocess.run(["open", str(path)], check=False)
        else:
            subprocess.run(["xdg-open", str(path)], check=False)
    except Exception:
        pass


if __name__ == "__main__":
    app()
