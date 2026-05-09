"""Log-axis chart with optional theoretical envelopes (Levenspiel-style guides)."""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import cycle
from typing import Callable

import numpy as np

from paperforge.charts.base import BaseChart, ChartConfig
from paperforge.charts.data_loader import Series


@dataclass
class Envelope:
    """Theoretical guide curve evaluated as ``y = func(x)``."""

    label: str
    func: Callable[[np.ndarray], np.ndarray]
    color: str = "#666666"
    alpha: float = 0.6
    linewidth: float = 1.3


@dataclass
class LogScaleConfig(ChartConfig):
    series: list[Series] = field(default_factory=list)
    log_y: bool = True            # default for this template
    envelopes: list[Envelope] = field(default_factory=list)
    x_envelope: tuple[float, float] = (0.5, 110.0)
    annotations: list[dict] = field(default_factory=list)
    # vlines: [{'x': 50, 'label': 'critical', 'color': 'gray'}]
    vlines: list[dict] = field(default_factory=list)
    # bands: [{'x_start': 60, 'x_end': 75, 'label': 'industrial', 'color': '#06A77D'}]
    bands: list[dict] = field(default_factory=list)


class LogScaleChart(BaseChart):
    config_class = LogScaleConfig
    cfg: LogScaleConfig

    def render(self, ax) -> None:
        cfg = self.cfg

        # Bands first (lowest z-order).
        for b in cfg.bands:
            ax.axvspan(
                b["x_start"], b["x_end"],
                alpha=b.get("alpha", 0.10),
                color=b.get("color", "#06A77D"),
                zorder=0,
            )

        # Vertical lines.
        for v in cfg.vlines:
            ax.axvline(
                v["x"],
                color=v.get("color", "gray"),
                linestyle=v.get("linestyle", "--"),
                alpha=v.get("alpha", 0.5),
                linewidth=v.get("linewidth", 1),
                zorder=0,
            )
            if v.get("label"):
                ax.text(
                    v["x"] + v.get("label_offset", 0.5),
                    v.get("label_y", 1),
                    v["label"],
                    fontsize=8.5,
                    color="#555555",
                    style="italic",
                )

        # Theoretical envelopes (dashed).
        x_env = np.linspace(*cfg.x_envelope, 300)
        for env in cfg.envelopes:
            ax.plot(
                x_env, env.func(x_env),
                ":", color=env.color, alpha=env.alpha,
                linewidth=env.linewidth, label=env.label,
            )

        # Experimental data series.
        colors = cycle(cfg.palette)
        for s in cfg.series:
            color = s.color or next(colors)
            ax.plot(
                s.x, s.y,
                marker=s.marker, linestyle=s.linestyle, color=color,
                linewidth=2, markersize=7, label=s.label,
            )

        # Custom text annotations.
        for ann in cfg.annotations:
            ax.annotate(
                ann.get("text", ""),
                xy=tuple(ann.get("xy", (0, 0))),
                xytext=tuple(ann.get("xytext", ann.get("xy", (0, 0)))),
                fontsize=ann.get("fontsize", 9),
                ha=ann.get("ha", "center"),
                arrowprops=ann.get("arrowprops"),
            )

        if cfg.series or cfg.envelopes:
            ax.legend(loc=cfg.legend_loc, framealpha=0.95, fontsize=9)
