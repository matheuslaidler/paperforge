"""Grouped bar chart with optional value labels (Burphan-style)."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from paperforge.charts.base import BaseChart, ChartConfig


@dataclass
class BarConfig(ChartConfig):
    categories: list[str] = field(default_factory=list)
    series: list[dict] = field(default_factory=list)  # {label, values}
    show_values: bool = True
    bar_width: float = 0.36


class BarChart(BaseChart):
    config_class = BarConfig
    cfg: BarConfig

    def render(self, ax) -> None:
        cfg = self.cfg
        n_groups = len(cfg.categories)
        n_series = len(cfg.series)
        if n_groups == 0 or n_series == 0:
            return
        x = np.arange(n_groups)
        total_width = cfg.bar_width * n_series
        offset = -total_width / 2 + cfg.bar_width / 2
        palette = cfg.palette

        for i, s in enumerate(cfg.series):
            label = s.get("label", f"Series {i+1}")
            values = list(s.get("values", []))
            color = s.get("color") or palette[i % len(palette)]
            bars = ax.bar(
                x + offset + i * cfg.bar_width,
                values,
                cfg.bar_width,
                label=label,
                color=color,
                edgecolor="black",
                linewidth=0.5,
            )
            if cfg.show_values:
                top = max(values) if values else 1
                for b in bars:
                    ax.text(
                        b.get_x() + b.get_width() / 2,
                        b.get_height() + top * 0.015,
                        f"{b.get_height():.1f}",
                        ha="center", fontsize=9,
                    )

        ax.set_xticks(x)
        ax.set_xticklabels(cfg.categories, fontsize=10)
        ax.set_ylim(0, ax.get_ylim()[1] * 1.1)
        if any(s.get("label") for s in cfg.series):
            ax.legend(loc=cfg.legend_loc, framealpha=0.95, fontsize=9.5)
        ax.grid(True, axis="y", alpha=cfg.grid_alpha, linestyle=":")
