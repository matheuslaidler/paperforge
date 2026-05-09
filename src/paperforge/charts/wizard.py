"""Rich-based interactive chart wizard. Saves a sibling YAML for reproducibility."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from pathlib import Path

import yaml
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from paperforge import i18n
from paperforge.charts.builder import ChartBuildRequest, build_chart
from paperforge.charts.templates import REGISTRY
from paperforge.utils.logging import console, ok


def run_wizard() -> None:
    console.print(Panel.fit(
        f"[accent]{i18n.t('chart.wizard.welcome')}[/]",
        border_style="accent",
    ))

    template = Prompt.ask(
        i18n.t("chart.wizard.prompt.template"),
        choices=list(REGISTRY),
        default="line",
    )
    title = Prompt.ask(i18n.t("chart.wizard.prompt.title"), default="")
    xlabel = Prompt.ask(i18n.t("chart.wizard.prompt.xlabel"), default="")
    ylabel = Prompt.ask(i18n.t("chart.wizard.prompt.ylabel"), default="")
    source = Prompt.ask(i18n.t("chart.wizard.prompt.source"), default="") or None

    csv_input = Prompt.ask(i18n.t("chart.wizard.prompt.csv"), default="")
    csv_path: Path | None = Path(csv_input).expanduser() if csv_input.strip() else None

    x_col = y_col = series_col = None
    if csv_path:
        x_col = Prompt.ask("X column name", default="") or None
        y_col = Prompt.ask("Y column name", default="") or None
        series_col = Prompt.ask("Series column (optional)", default="") or None

    log_y = Confirm.ask("Log scale on Y?", default=False)
    log_x = Confirm.ask("Log scale on X?", default=False)

    output_input = Prompt.ask(
        i18n.t("chart.wizard.prompt.output"),
        default=f"chart_{template}_{datetime.now().strftime('%Y%m%d-%H%M%S')}.png",
    )
    output = Path(output_input).expanduser()

    formats = Prompt.ask(
        i18n.t("chart.wizard.prompt.format"),
        default="png",
    )

    req = ChartBuildRequest(
        template=template,
        csv=csv_path,
        output=output,
        title=title or None,
        xlabel=xlabel or None,
        ylabel=ylabel or None,
        source=source,
        log_x=log_x,
        log_y=log_y,
        formats=tuple(s.strip() for s in formats.split(",")),
        x_col=x_col,
        y_col=y_col,
        series_col=series_col,
    )

    if not req.csv and template != "bar":
        console.print(
            "[warn]No CSV provided — the chart will be empty.[/] "
            "Pass a CSV or build a YAML config to add data."
        )

    result = build_chart(req)
    ok(i18n.t("chart.ok", path=str(result.path)))

    # Sibling YAML for reproducibility.
    yaml_path = result.path.with_suffix(".paperforge.yaml")
    payload = {k: (str(v) if isinstance(v, Path) else v)
               for k, v in asdict(req).items() if v is not None and v != ""}
    payload.pop("formats", None)
    yaml_path.write_text(
        yaml.safe_dump(payload, sort_keys=True, allow_unicode=True),
        encoding="utf-8",
    )
    console.print(i18n.t("chart.wizard.saved_yaml", path=str(yaml_path)))
