"""Abstract base for all chart templates + shared helpers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import matplotlib

matplotlib.use("Agg")  # headless-safe by default
import matplotlib.pyplot as plt  # noqa: E402

from paperforge.charts.palette import DEFAULT_PALETTE  # noqa: E402

DEFAULT_DPI = 150
DEFAULT_FIGSIZE = (8.5, 5.5)


@dataclass
class ChartConfig:
    """Common configuration shared by every chart template."""

    title: str = ""
    xlabel: str = ""
    ylabel: str = ""
    source: str | None = None
    figsize: tuple[float, float] = DEFAULT_FIGSIZE
    dpi: int = DEFAULT_DPI
    palette: list[str] = field(default_factory=lambda: list(DEFAULT_PALETTE))
    grid_alpha: float = 0.30
    log_x: bool = False
    log_y: bool = False
    legend_loc: str = "best"


def add_source_box(ax, citation: str) -> None:
    """Bottom-right citation box used consistently across every chart template."""
    ax.text(
        0.985, 0.025,
        citation,
        transform=ax.transAxes,
        fontsize=8,
        va="bottom",
        ha="right",
        bbox=dict(boxstyle="round,pad=0.4",
                  facecolor="#FAFAFA",
                  edgecolor="#CCCCCC"),
    )


def save_figure(fig, output_base: Path, formats: Iterable[str], dpi: int) -> Path:
    """Save the figure in one or more formats; return the first written path."""
    formats = [f.lower().lstrip(".") for f in formats]
    if not formats:
        formats = ["png"]

    output_base = Path(output_base)
    if output_base.suffix.lstrip(".").lower() in {"png", "svg", "pdf", "jpg", "jpeg"}:
        # User passed a full filename; honor its extension as the first format.
        primary_fmt = output_base.suffix.lstrip(".").lower()
        stem = output_base.with_suffix("")
        ordered = [primary_fmt] + [f for f in formats if f != primary_fmt]
    else:
        stem = output_base
        ordered = formats

    written: list[Path] = []
    for fmt in ordered:
        path = stem.with_suffix(f".{fmt}")
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        written.append(path)
    plt.close(fig)
    return written[0]


class BaseChart(ABC):
    """All templates inherit from this class."""

    config_class: type[ChartConfig] = ChartConfig

    def __init__(self, cfg: ChartConfig, data: dict | None = None) -> None:
        self.cfg = cfg
        self.data = data or {}

    @abstractmethod
    def render(self, ax) -> None:
        """Draw the chart on the supplied Axes."""

    def build(self, output: Path, formats: Iterable[str] = ("png",)) -> Path:
        fig, ax = plt.subplots(figsize=self.cfg.figsize)
        self.render(ax)
        self._apply_common(ax)
        return save_figure(fig, output, formats, self.cfg.dpi)

    def _apply_common(self, ax) -> None:
        if self.cfg.title:
            ax.set_title(self.cfg.title, pad=12)
        if self.cfg.xlabel:
            ax.set_xlabel(self.cfg.xlabel)
        if self.cfg.ylabel:
            ax.set_ylabel(self.cfg.ylabel)
        ax.grid(True, which="major", alpha=self.cfg.grid_alpha, linestyle=":")
        if self.cfg.log_x or self.cfg.log_y:
            ax.grid(True, which="minor", alpha=self.cfg.grid_alpha * 0.5,
                    linestyle=":")
        if self.cfg.log_x:
            ax.set_xscale("log")
        if self.cfg.log_y:
            ax.set_yscale("log")
        if self.cfg.source:
            add_source_box(ax, self.cfg.source)
