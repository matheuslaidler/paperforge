"""Simple scatter plot with optional regression line."""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import cycle

import numpy as np

from paperforge.charts.base import BaseChart, ChartConfig
from paperforge.charts.data_loader import Series


@dataclass
class ScatterConfig(ChartConfig):
    series: list[Series] = field(default_factory=list)
    show_regression: bool = False
    marker_size: float = 36.0
    alpha: float = 0.85


class ScatterChart(BaseChart):
    config_class = ScatterConfig
    cfg: ScatterConfig

    def render(self, ax) -> None:
        cfg = self.cfg
        colors = cycle(cfg.palette)
        for s in cfg.series:
            color = s.color or next(colors)
            ax.scatter(
                s.x, s.y,
                s=cfg.marker_size, color=color, alpha=cfg.alpha,
                marker=s.marker or "o", label=s.label,
                edgecolors="black", linewidths=0.5,
            )
            if cfg.show_regression and len(s.x) >= 2:
                xs = np.array(s.x, dtype=float)
                ys = np.array(s.y, dtype=float)
                m, b = np.polyfit(xs, ys, 1)
                xx = np.linspace(xs.min(), xs.max(), 50)
                ax.plot(xx, m * xx + b, "--", color=color, alpha=0.6, linewidth=1.4)
        if any(s.label for s in cfg.series):
            ax.legend(loc=cfg.legend_loc, framealpha=0.95, fontsize=9.5)
