"""Simple line chart with one or more series."""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import cycle

from paperforge.charts.base import BaseChart, ChartConfig
from paperforge.charts.data_loader import Series


@dataclass
class LineConfig(ChartConfig):
    series: list[Series] = field(default_factory=list)
    show_markers: bool = True
    linewidth: float = 2.0


class LineChart(BaseChart):
    config_class = LineConfig
    cfg: LineConfig

    def render(self, ax) -> None:
        cfg = self.cfg
        colors = cycle(cfg.palette)
        for s in cfg.series:
            color = s.color or next(colors)
            marker = s.marker if cfg.show_markers else ""
            ax.plot(
                s.x, s.y,
                marker=marker,
                linestyle=s.linestyle or "-",
                color=color,
                linewidth=cfg.linewidth,
                markersize=6,
                label=s.label,
            )
        if any(s.label for s in cfg.series):
            ax.legend(loc=cfg.legend_loc, framealpha=0.95, fontsize=9.5)
