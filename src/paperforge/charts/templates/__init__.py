"""Built-in chart templates."""

from paperforge.charts.templates.bar import BarChart, BarConfig
from paperforge.charts.templates.dose_response import DoseResponseChart, DoseResponseConfig
from paperforge.charts.templates.line import LineChart, LineConfig
from paperforge.charts.templates.log_scale import LogScaleChart, LogScaleConfig
from paperforge.charts.templates.scatter import ScatterChart, ScatterConfig

REGISTRY = {
    "line": (LineChart, LineConfig),
    "bar": (BarChart, BarConfig),
    "log-scale": (LogScaleChart, LogScaleConfig),
    "scatter": (ScatterChart, ScatterConfig),
    "dose-response": (DoseResponseChart, DoseResponseConfig),
}

__all__ = [
    "REGISTRY",
    "BarChart", "BarConfig",
    "DoseResponseChart", "DoseResponseConfig",
    "LineChart", "LineConfig",
    "LogScaleChart", "LogScaleConfig",
    "ScatterChart", "ScatterConfig",
]
