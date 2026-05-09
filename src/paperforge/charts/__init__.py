"""Scientific chart pipeline: templates + interactive wizard + matplotlib backend."""

from paperforge.charts.builder import ChartBuildRequest, ChartBuildResult, build_chart
from paperforge.charts.palette import DEFAULT_PALETTE, COLORBLIND_PALETTE

__all__ = [
    "ChartBuildRequest",
    "ChartBuildResult",
    "build_chart",
    "DEFAULT_PALETTE",
    "COLORBLIND_PALETTE",
]
