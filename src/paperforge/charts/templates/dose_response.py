"""Dose-response curves (sigmoid-style viability vs dose)."""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import cycle

import numpy as np

from paperforge.charts.base import BaseChart, ChartConfig
from paperforge.charts.data_loader import Series


@dataclass
class DoseResponseConfig(ChartConfig):
    series: list[Series] = field(default_factory=list)
    reference_dose: float | None = None      # vertical reference line, e.g. 10 (% v/v)
    smooth: bool = True


class DoseResponseChart(BaseChart):
    config_class = DoseResponseConfig
    cfg: DoseResponseConfig

    def render(self, ax) -> None:
        cfg = self.cfg
        colors = cycle(cfg.palette)
        markers = cycle(("o", "s", "^", "v", "D", "P"))

        for s in cfg.series:
            color = s.color or next(colors)
            marker = s.marker or next(markers)
            x = np.asarray(s.x, dtype=float)
            y = np.asarray(s.y, dtype=float)
            ax.plot(
                x, y,
                marker=marker, linestyle=s.linestyle or "-",
                color=color, linewidth=2, markersize=7,
                label=s.label,
            )

        if cfg.reference_dose is not None:
            ax.axvline(cfg.reference_dose, color="gray", linestyle="--",
                       alpha=0.5, linewidth=1)
            ax.text(
                cfg.reference_dose + 0.05,
                ax.get_ylim()[0] + 5,
                f"{cfg.reference_dose}\n(reference)",
                fontsize=8.5,
                color="gray",
            )
        ax.set_ylim(0, 105)
        if any(s.label for s in cfg.series):
            ax.legend(loc=cfg.legend_loc or "lower left",
                      framealpha=0.95, fontsize=9.5)
