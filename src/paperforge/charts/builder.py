"""Dispatch chart builds based on user request (CLI flags, YAML or wizard output)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from paperforge import i18n
from paperforge.charts.base import ChartConfig
from paperforge.charts.data_loader import (
    ChartData,
    Series,
    load_csv,
    load_yaml_config,
    series_from_config,
)
from paperforge.charts.palette import get as get_palette
from paperforge.charts.templates import REGISTRY
from paperforge.utils.logging import info, warn


@dataclass
class ChartBuildRequest:
    template: Optional[str] = None
    config_file: Optional[Path] = None
    csv: Optional[Path] = None
    output: Optional[Path] = None
    title: Optional[str] = None
    xlabel: Optional[str] = None
    ylabel: Optional[str] = None
    source: Optional[str] = None
    log_y: bool = False
    log_x: bool = False
    dpi: int = 150
    width: float = 8.5
    height: float = 5.5
    formats: tuple[str, ...] = ("png",)
    palette: str = "default"
    x_col: Optional[str] = None
    y_col: Optional[str] = None
    series_col: Optional[str] = None


@dataclass
class ChartBuildResult:
    path: Path
    template: str


def build_chart(req: ChartBuildRequest) -> ChartBuildResult:
    template_name, raw_cfg, raw_data = _resolve_inputs(req)

    if template_name not in REGISTRY:
        raise ValueError(
            i18n.t("chart.error.template_unknown",
                   template=template_name,
                   available=", ".join(REGISTRY))
        )
    chart_cls, config_cls = REGISTRY[template_name]

    palette = get_palette(req.palette)
    base_cfg = ChartConfig(
        title=req.title or raw_cfg.get("title", ""),
        xlabel=req.xlabel or raw_cfg.get("xlabel", ""),
        ylabel=req.ylabel or raw_cfg.get("ylabel", ""),
        source=req.source or raw_cfg.get("source"),
        figsize=(req.width, req.height),
        dpi=req.dpi,
        palette=raw_cfg.get("palette", palette),
        log_x=req.log_x or bool(raw_cfg.get("log_x", False)),
        log_y=req.log_y or bool(raw_cfg.get("log_y", False)),
        legend_loc=raw_cfg.get("legend_loc", "best"),
    )

    cfg = _build_template_config(config_cls, base_cfg, raw_cfg, raw_data)
    chart = chart_cls(cfg, raw_data.extras if raw_data else {})

    output = _resolve_output_path(req.output, template_name)
    info(i18n.t("chart.status.rendering", template=template_name))
    written = chart.build(output, formats=req.formats)
    return ChartBuildResult(path=written, template=template_name)


# --------------------------------------------------------------------------- #
#  Internals                                                                  #
# --------------------------------------------------------------------------- #
def _resolve_inputs(req: ChartBuildRequest) -> tuple[str, dict, ChartData]:
    """Merge YAML/CSV/CLI inputs into (template_name, raw_cfg_dict, ChartData)."""
    raw_cfg: dict = {}
    raw_data = ChartData()

    if req.config_file:
        raw_cfg = load_yaml_config(req.config_file)

    template_name = req.template or raw_cfg.get("template")
    if not template_name:
        raise ValueError(i18n.t("chart.error.no_data"))

    if raw_cfg:
        # The 'bar' template stores series as plain {label, values} dicts; do
        # NOT push them through series_from_config (which would silently drop
        # the 'values' field because Series uses x/y).
        if "series" in raw_cfg and isinstance(raw_cfg["series"], list):
            if template_name == "bar":
                raw_data.extras["series"] = raw_cfg["series"]
            else:
                raw_data.series = series_from_config(raw_cfg["series"])
        for key in ("categories", "envelopes", "vlines", "bands",
                    "annotations", "reference_dose", "show_regression",
                    "show_markers", "show_values"):
            if key in raw_cfg:
                raw_data.extras[key] = raw_cfg[key]

    if req.csv:
        info(i18n.t("chart.status.loading_data", path=str(req.csv)))
        loaded = load_csv(req.csv, x_col=req.x_col, y_col=req.y_col,
                          series_col=req.series_col)
        if loaded.series:
            raw_data.series = loaded.series

    return template_name, raw_cfg, raw_data


def _build_template_config(config_cls, base: ChartConfig, raw: dict,
                           data: ChartData):
    """Combine BaseChart fields + template-specific extras into a single config."""
    extra: dict = dict(data.extras)
    if data.series:
        extra["series"] = data.series

    # Template-specific keys that already came from YAML.
    for key in ("categories", "envelopes", "vlines", "bands", "annotations",
                "reference_dose", "show_regression", "show_markers",
                "show_values", "bar_width", "smooth"):
        if key in raw:
            extra[key] = raw[key]
        elif key in data.extras:
            extra[key] = data.extras[key]

    # Special case: bar template stores series as plain dicts {label, values}.
    if config_cls.__name__ == "BarConfig" and "series" in extra:
        normalized: list[dict] = []
        for item in extra["series"]:
            if isinstance(item, Series):
                normalized.append({"label": item.label, "values": list(item.y),
                                   "color": item.color})
            elif isinstance(item, dict):
                normalized.append(item)
        extra["series"] = normalized

    common = {f: getattr(base, f) for f in (
        "title", "xlabel", "ylabel", "source", "figsize", "dpi",
        "palette", "grid_alpha", "log_x", "log_y", "legend_loc",
    )}
    return config_cls(**common, **{k: v for k, v in extra.items()
                                   if k in config_cls.__dataclass_fields__})


def _resolve_output_path(output: Optional[Path], template_name: str) -> Path:
    if output:
        return output
    from datetime import datetime
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return Path.cwd() / f"chart_{template_name}_{stamp}.png"


# --------------------------------------------------------------------------- #
#  Public helper used by the GUI (bypasses CSV/YAML resolution)               #
# --------------------------------------------------------------------------- #
def build_chart_from_state(
    template: str,
    base_cfg_kwargs: dict,
    series: list,
    extras: dict,
    output: Path,
    formats: tuple[str, ...] = ("png",),
) -> ChartBuildResult:
    """Build a chart directly from in-memory state — used by the GUI.

    Reuses the same ``REGISTRY`` and ``_build_template_config`` helpers as the
    YAML/CSV pipeline, but skips parsing. Callers are responsible for handing
    over already-typed series objects (``charts.data_loader.Series`` instances
    for line/log-scale/scatter/dose-response, or plain ``{label, values}``
    dicts for bar) and pre-validated extras (envelopes pre-compiled, etc.).
    """
    if template not in REGISTRY:
        raise ValueError(
            i18n.t("chart.error.template_unknown",
                   template=template, available=", ".join(REGISTRY))
        )
    chart_cls, config_cls = REGISTRY[template]
    base = ChartConfig(**base_cfg_kwargs)
    data = ChartData(series=series, extras=dict(extras))
    cfg = _build_template_config(config_cls, base, dict(extras), data)
    chart = chart_cls(cfg, dict(extras))
    written = chart.build(output, formats=formats)
    return ChartBuildResult(path=written, template=template)


def render_chart_on_axes(
    template: str,
    base_cfg_kwargs: dict,
    series: list,
    extras: dict,
    ax,
) -> None:
    """Render an in-memory chart onto a caller-provided matplotlib Axes.

    Used by the live preview canvas in the GUI — does not save to disk.
    """
    if template not in REGISTRY:
        return
    chart_cls, config_cls = REGISTRY[template]
    base = ChartConfig(**base_cfg_kwargs)
    data = ChartData(series=series, extras=dict(extras))
    cfg = _build_template_config(config_cls, base, dict(extras), data)
    chart = chart_cls(cfg, dict(extras))
    chart.render(ax)
    chart._apply_common(ax)
