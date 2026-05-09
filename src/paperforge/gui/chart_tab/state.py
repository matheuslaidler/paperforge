"""In-memory model for the chart tab. Mutated by every panel; read by preview."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from paperforge.charts.data_loader import Series
from paperforge.theme import DEFAULT_PALETTE


@dataclass
class VLine:
    x: float = 0.0
    label: str = ""
    color: str = "#666666"
    linestyle: str = "--"
    alpha: float = 0.5


@dataclass
class Band:
    x_start: float = 0.0
    x_end: float = 1.0
    label: str = ""
    color: str = "#06A77D"
    alpha: float = 0.10


@dataclass
class EnvelopeSpec:
    label: str = "envelope"
    expression: str = "x"
    color: str = "#666666"
    alpha: float = 0.6
    linewidth: float = 1.3


@dataclass
class ChartState:
    template: str = "line"
    title: str = ""
    xlabel: str = ""
    ylabel: str = ""
    source: str = ""
    series: list[Series] = field(default_factory=list)
    bar_categories: list[str] = field(default_factory=list)
    bar_series: list[dict] = field(default_factory=list)  # {label, values, color}
    vlines: list[VLine] = field(default_factory=list)
    bands: list[Band] = field(default_factory=list)
    envelopes: list[EnvelopeSpec] = field(default_factory=list)
    log_x: bool = False
    log_y: bool = False
    dpi: int = 150
    width: float = 8.5
    height: float = 5.5
    palette_name: str = "default"
    formats: tuple[str, ...] = ("png",)
    legend_loc: str = "best"

    def base_cfg_kwargs(self) -> dict[str, Any]:
        from paperforge.charts.palette import get as get_palette
        return {
            "title": self.title,
            "xlabel": self.xlabel,
            "ylabel": self.ylabel,
            "source": self.source or None,
            "figsize": (self.width, self.height),
            "dpi": self.dpi,
            "palette": get_palette(self.palette_name) or list(DEFAULT_PALETTE),
            "log_x": self.log_x,
            "log_y": self.log_y,
            "legend_loc": self.legend_loc,
        }

    def extras(self, compiled_envelopes: list | None = None) -> dict[str, Any]:
        out: dict[str, Any] = {}
        if self.template == "log-scale":
            out["vlines"] = [
                {"x": v.x, "label": v.label, "color": v.color,
                 "linestyle": v.linestyle, "alpha": v.alpha}
                for v in self.vlines if v.label or v.x
            ]
            out["bands"] = [
                {"x_start": b.x_start, "x_end": b.x_end, "label": b.label,
                 "color": b.color, "alpha": b.alpha}
                for b in self.bands
            ]
            if compiled_envelopes is not None:
                out["envelopes"] = compiled_envelopes
        if self.template == "bar":
            out["categories"] = list(self.bar_categories)
            out["series"] = list(self.bar_series)
        return out
