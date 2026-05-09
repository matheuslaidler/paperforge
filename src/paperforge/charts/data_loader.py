"""Load chart data from CSV or YAML/JSON files into typed series structures."""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class Series:
    label: str
    x: list[float]
    y: list[float]
    marker: str = "o"
    linestyle: str = "-"
    color: str | None = None  # None -> palette cycle


@dataclass
class ChartData:
    series: list[Series] = field(default_factory=list)
    extras: dict[str, Any] = field(default_factory=dict)  # e.g. envelopes


def load_csv(path: Path, *, x_col: str | None, y_col: str | None,
             series_col: str | None = None) -> ChartData:
    """Load a CSV. If ``series_col`` is given, split rows into one series per value.

    If x_col/y_col are not provided, defaults to the first two numeric columns.
    """
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    if not rows:
        return ChartData()

    fieldnames = list(rows[0].keys())
    if x_col is None:
        x_col = fieldnames[0]
    if y_col is None:
        y_col = next((c for c in fieldnames if c != x_col), fieldnames[-1])

    if series_col and series_col in fieldnames:
        groups: dict[str, list[tuple[float, float]]] = {}
        for r in rows:
            key = r.get(series_col, "")
            try:
                x = float(r[x_col])
                y = float(r[y_col])
            except (TypeError, ValueError):
                continue
            groups.setdefault(key, []).append((x, y))
        series = [
            Series(label=k, x=[p[0] for p in v], y=[p[1] for p in v])
            for k, v in groups.items()
        ]
    else:
        xs: list[float] = []
        ys: list[float] = []
        for r in rows:
            try:
                xs.append(float(r[x_col]))
                ys.append(float(r[y_col]))
            except (TypeError, ValueError):
                continue
        series = [Series(label=y_col, x=xs, y=ys)]
    return ChartData(series=series)


def load_yaml_config(path: Path) -> dict:
    """Generic YAML config loader. Returns a plain dict — caller normalizes."""
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def series_from_config(items: list[dict]) -> list[Series]:
    """Convert a list of dicts to Series objects. Used by YAML configs."""
    out: list[Series] = []
    for it in items:
        out.append(
            Series(
                label=str(it.get("label", "")),
                x=list(it.get("x", [])),
                y=list(it.get("y", [])),
                marker=str(it.get("marker", "o")),
                linestyle=str(it.get("linestyle", "-")),
                color=it.get("color"),
            )
        )
    return out
