"""Embedded matplotlib canvas with debounced re-render."""

from __future__ import annotations

import numpy as np
from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg,
    NavigationToolbar2QT,
)
from matplotlib.figure import Figure
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QVBoxLayout, QWidget

from paperforge import i18n
from paperforge.charts.builder import render_chart_on_axes
from paperforge.charts.templates.log_scale import Envelope


class PreviewCanvas(QWidget):
    """Live matplotlib preview. Use ``request_render(state)`` from any panel."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.figure = Figure(figsize=(7, 5), tight_layout=True)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(150)
        self._timer.timeout.connect(self._do_render)
        self._pending_state = None

        self._render_placeholder()

    # ------------------------------------------------------------------ #
    def request_render(self, state) -> None:
        """Schedule a re-render with debounce. Called by panels on change."""
        self._pending_state = state
        self._timer.start()

    # ------------------------------------------------------------------ #
    def _has_data(self, state) -> bool:
        if state.template == "bar":
            return any(s.get("values") for s in state.bar_series)
        return any(s.x and s.y for s in state.series)

    def _compile_envelopes(self, state) -> list:
        compiled: list = []
        for env in state.envelopes:
            try:
                code = compile(env.expression, "<envelope>", "eval")
            except Exception:
                continue
            def _make(code_obj=code, alpha=env.alpha,
                      color=env.color, label=env.label, lw=env.linewidth):
                def _fn(x):
                    try:
                        return eval(code_obj, {"__builtins__": {}}, {"np": np, "x": x})
                    except Exception:
                        return np.full_like(x, np.nan, dtype=float)
                return Envelope(label=label, func=_fn, color=color, alpha=alpha,
                                linewidth=lw)
            compiled.append(_make())
        return compiled

    def _do_render(self) -> None:
        state = self._pending_state
        if state is None:
            return

        self.figure.clear()
        if not self._has_data(state):
            self._render_placeholder()
            return

        ax = self.figure.add_subplot(111)
        try:
            extras = state.extras(compiled_envelopes=self._compile_envelopes(state))
            series = (state.series if state.template != "bar" else [])
            render_chart_on_axes(
                state.template,
                state.base_cfg_kwargs(),
                series,
                extras,
                ax,
            )
        except Exception as exc:  # noqa: BLE001
            ax.text(0.5, 0.5, f"Preview error:\n{exc}",
                    ha="center", va="center", transform=ax.transAxes,
                    color="#D62246", fontsize=10)
            ax.axis("off")
        self.canvas.draw_idle()

    def _render_placeholder(self) -> None:
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.text(
            0.5, 0.5,
            i18n.t("gui.chart.preview.placeholder"),
            ha="center", va="center", transform=ax.transAxes,
            color="#888", fontsize=12, style="italic",
        )
        ax.axis("off")
        self.canvas.draw_idle()

    # ------------------------------------------------------------------ #
    def figure_for_export(self) -> Figure:
        """Return the current figure (already populated). Used by Save figure."""
        return self.figure
