"""Annotations panel: vertical lines, bands and theoretical envelopes (log-scale)."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QColorDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from paperforge import i18n
from paperforge.gui.chart_tab.state import Band, EnvelopeSpec, VLine
from paperforge.gui.i18n_qt import Retranslator


class AnnotationsForm(QWidget):
    annotationsChanged = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._retr = Retranslator()
        self._build_ui()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self.unsupported_lbl = QLabel(i18n.t("gui.chart.annot.unsupported"))
        self.unsupported_lbl.setStyleSheet("color: #888; font-style: italic;")
        outer.addWidget(self.unsupported_lbl)
        self.unsupported_lbl.hide()

        # ----- vlines ----- #
        self.vline_table = self._make_table([
            i18n.t("gui.chart.annot.col_x"),
            i18n.t("gui.chart.annot.col_label"),
            i18n.t("gui.chart.annot.col_color"),
            i18n.t("gui.chart.annot.col_linestyle"),
            i18n.t("gui.chart.annot.col_alpha"),
        ])
        self._gb_vlines = self._make_group(
            "gui.chart.annot.vlines", self.vline_table)
        outer.addWidget(self._gb_vlines)

        # ----- bands ----- #
        self.band_table = self._make_table([
            i18n.t("gui.chart.annot.col_xstart"),
            i18n.t("gui.chart.annot.col_xend"),
            i18n.t("gui.chart.annot.col_label"),
            i18n.t("gui.chart.annot.col_color"),
            i18n.t("gui.chart.annot.col_alpha"),
        ])
        self._gb_bands = self._make_group(
            "gui.chart.annot.bands", self.band_table)
        outer.addWidget(self._gb_bands)

        # ----- envelopes ----- #
        self.env_table = self._make_table([
            i18n.t("gui.chart.annot.col_label"),
            i18n.t("gui.chart.annot.col_expr"),
            i18n.t("gui.chart.annot.col_color"),
            i18n.t("gui.chart.annot.col_alpha"),
        ])
        env_help = QLabel(i18n.t("gui.chart.annot.envelope_help"))
        env_help.setStyleSheet("color: #888; font-style: italic;")
        env_help.setWordWrap(True)
        env_wrapper = QWidget()
        env_layout = QVBoxLayout(env_wrapper)
        env_layout.setContentsMargins(0, 0, 0, 0)
        env_layout.addWidget(env_help)
        env_layout.addWidget(self.env_table)
        env_layout.addLayout(self._make_buttons(self.env_table, defaults_envelope=True))
        self._gb_env = QGroupBox(i18n.t("gui.chart.annot.envelopes"))
        gb_lay = QVBoxLayout(self._gb_env)
        gb_lay.addWidget(env_wrapper)
        outer.addWidget(self._gb_env)
        outer.addStretch(1)

        # connect signals once everything exists
        for tbl in (self.vline_table, self.band_table, self.env_table):
            tbl.itemChanged.connect(lambda *_: self.annotationsChanged.emit())

    # ------------------------------------------------------------------ #
    def _make_table(self, headers: list[str]) -> QTableWidget:
        t = QTableWidget(0, len(headers))
        t.setHorizontalHeaderLabels(headers)
        t.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        t.verticalHeader().setVisible(False)
        return t

    def _make_buttons(self, table: QTableWidget, *,
                      defaults_envelope: bool = False) -> QHBoxLayout:
        row = QHBoxLayout()
        add = QPushButton(i18n.t("gui.chart.annot.add"))
        rm = QPushButton(i18n.t("gui.chart.annot.remove"))
        row.addWidget(add); row.addWidget(rm); row.addStretch(1)

        def _add():
            n = table.rowCount()
            table.setRowCount(n + 1)
            if defaults_envelope:
                # label, expression, color, alpha
                defaults = ["envelope", "10 * (1 - x / 90) ** 1", "#666666", "0.6"]
                for c, v in enumerate(defaults):
                    table.setItem(n, c, QTableWidgetItem(v))
            self.annotationsChanged.emit()

        def _rm():
            r = table.currentRow()
            if r < 0:
                r = table.rowCount() - 1
            if r >= 0:
                table.removeRow(r)
                self.annotationsChanged.emit()

        add.clicked.connect(_add)
        rm.clicked.connect(_rm)
        return row

    def _make_group(self, key: str, table: QTableWidget) -> QGroupBox:
        gb = QGroupBox(i18n.t(key))
        lay = QVBoxLayout(gb)
        lay.addWidget(table)
        lay.addLayout(self._make_buttons(table))
        return gb

    # ------------------------------------------------------------------ #
    def retranslate(self) -> None:
        self.unsupported_lbl.setText(i18n.t("gui.chart.annot.unsupported"))
        self._gb_vlines.setTitle(i18n.t("gui.chart.annot.vlines"))
        self._gb_bands.setTitle(i18n.t("gui.chart.annot.bands"))
        self._gb_env.setTitle(i18n.t("gui.chart.annot.envelopes"))

    # ------------------------------------------------------------------ #
    def set_supported(self, supported: bool) -> None:
        self.unsupported_lbl.setVisible(not supported)
        for w in (self._gb_vlines, self._gb_bands, self._gb_env):
            w.setEnabled(supported)

    # ------------------------------------------------------------------ #
    def collect(self) -> tuple[list[VLine], list[Band], list[EnvelopeSpec]]:
        vlines: list[VLine] = []
        for r in range(self.vline_table.rowCount()):
            try:
                x = float(self._cell(self.vline_table, r, 0) or 0)
            except ValueError:
                continue
            label = self._cell(self.vline_table, r, 1) or ""
            color = self._cell(self.vline_table, r, 2) or "#666"
            ls = self._cell(self.vline_table, r, 3) or "--"
            try:
                alpha = float(self._cell(self.vline_table, r, 4) or 0.5)
            except ValueError:
                alpha = 0.5
            vlines.append(VLine(x=x, label=label, color=color,
                                linestyle=ls, alpha=alpha))

        bands: list[Band] = []
        for r in range(self.band_table.rowCount()):
            try:
                xs = float(self._cell(self.band_table, r, 0) or 0)
                xe = float(self._cell(self.band_table, r, 1) or 0)
            except ValueError:
                continue
            label = self._cell(self.band_table, r, 2) or ""
            color = self._cell(self.band_table, r, 3) or "#06A77D"
            try:
                alpha = float(self._cell(self.band_table, r, 4) or 0.10)
            except ValueError:
                alpha = 0.10
            bands.append(Band(x_start=xs, x_end=xe, label=label,
                              color=color, alpha=alpha))

        envs: list[EnvelopeSpec] = []
        for r in range(self.env_table.rowCount()):
            label = self._cell(self.env_table, r, 0) or "envelope"
            expr = self._cell(self.env_table, r, 1) or "x"
            color = self._cell(self.env_table, r, 2) or "#666"
            try:
                alpha = float(self._cell(self.env_table, r, 3) or 0.6)
            except ValueError:
                alpha = 0.6
            envs.append(EnvelopeSpec(label=label, expression=expr,
                                     color=color, alpha=alpha))
        return vlines, bands, envs

    @staticmethod
    def _cell(table: QTableWidget, row: int, col: int) -> str:
        item = table.item(row, col)
        return item.text().strip() if item else ""

    # ------------------------------------------------------------------ #
    #  Bulk load from example / state                                    #
    # ------------------------------------------------------------------ #
    def load(self, vlines: list[VLine], bands: list[Band],
             envelopes: list[EnvelopeSpec]) -> None:
        """Replace all annotations at once. Used when applying templates."""
        for tbl in (self.vline_table, self.band_table, self.env_table):
            tbl.blockSignals(True)
            tbl.setRowCount(0)
            tbl.blockSignals(False)

        self.vline_table.blockSignals(True)
        for v in vlines:
            r = self.vline_table.rowCount()
            self.vline_table.insertRow(r)
            for c, val in enumerate([str(v.x), v.label, v.color,
                                     v.linestyle, str(v.alpha)]):
                self.vline_table.setItem(r, c, QTableWidgetItem(val))
        self.vline_table.blockSignals(False)

        self.band_table.blockSignals(True)
        for b in bands:
            r = self.band_table.rowCount()
            self.band_table.insertRow(r)
            for c, val in enumerate([str(b.x_start), str(b.x_end),
                                     b.label, b.color, str(b.alpha)]):
                self.band_table.setItem(r, c, QTableWidgetItem(val))
        self.band_table.blockSignals(False)

        self.env_table.blockSignals(True)
        for e in envelopes:
            r = self.env_table.rowCount()
            self.env_table.insertRow(r)
            for c, val in enumerate([e.label, e.expression,
                                     e.color, str(e.alpha)]):
                self.env_table.setItem(r, c, QTableWidgetItem(val))
        self.env_table.blockSignals(False)

        self.annotationsChanged.emit()
