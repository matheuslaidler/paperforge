"""Right-rail style panel: dpi/width/height/palette/log-axes/legend/formats."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QWidget,
)

from paperforge import i18n
from paperforge.gui.i18n_qt import Retranslator

LEGEND_LOCS = ["best", "upper right", "upper left", "lower left", "lower right",
               "right", "center left", "center right", "lower center",
               "upper center", "center"]


class StylePanel(QWidget):
    styleChanged = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._retr = Retranslator()

        self.dpi = QSpinBox(); self.dpi.setRange(72, 600); self.dpi.setValue(150)
        self.width = QDoubleSpinBox(); self.width.setRange(2.0, 30.0); self.width.setSingleStep(0.5); self.width.setValue(8.5)
        self.height = QDoubleSpinBox(); self.height.setRange(2.0, 30.0); self.height.setSingleStep(0.5); self.height.setValue(5.5)
        self.palette = QComboBox(); self.palette.addItems(["default", "colorblind"])
        self.legend = QComboBox(); self.legend.addItems(LEGEND_LOCS)
        self.log_x = QCheckBox()
        self.log_y = QCheckBox()
        self.fmt_png = QCheckBox("PNG"); self.fmt_png.setChecked(True)
        self.fmt_svg = QCheckBox("SVG")
        self.fmt_pdf = QCheckBox("PDF")

        for w in (self.dpi, self.width, self.height):
            w.valueChanged.connect(self.styleChanged)
        for w in (self.palette, self.legend):
            w.currentIndexChanged.connect(self.styleChanged)
        for w in (self.log_x, self.log_y, self.fmt_png, self.fmt_svg, self.fmt_pdf):
            w.toggled.connect(self.styleChanged)

        form = QFormLayout(self)
        self._lbl_dpi = self._make_label("gui.label.dpi")
        self._lbl_w = self._make_label("gui.label.width")
        self._lbl_h = self._make_label("gui.label.height")
        self._lbl_pal = self._make_label("gui.label.palette")
        self._lbl_legend = self._make_label("gui.label.legend_loc")
        self._lbl_lx = self._make_label("gui.label.log_x")
        self._lbl_ly = self._make_label("gui.label.log_y")
        self._lbl_fmt = self._make_label("gui.label.format")
        form.addRow(self._lbl_dpi, self.dpi)
        form.addRow(self._lbl_w, self.width)
        form.addRow(self._lbl_h, self.height)
        form.addRow(self._lbl_pal, self.palette)
        form.addRow(self._lbl_legend, self.legend)
        form.addRow(self._lbl_lx, self.log_x)
        form.addRow(self._lbl_ly, self.log_y)

        formats_row = QHBoxLayout()
        formats_row.addWidget(self.fmt_png)
        formats_row.addWidget(self.fmt_svg)
        formats_row.addWidget(self.fmt_pdf)
        formats_row.addStretch(1)
        formats_widget = QWidget()
        formats_widget.setLayout(formats_row)
        form.addRow(self._lbl_fmt, formats_widget)

    def _make_label(self, key: str) -> QLabel:
        lbl = QLabel(i18n.t(key))
        self._retr.bind(lbl, key)
        return lbl

    def retranslate(self) -> None:
        self._retr.retranslate()

    # ------------------------------------------------------------------ #
    def chosen_formats(self) -> tuple[str, ...]:
        out: list[str] = []
        if self.fmt_png.isChecked(): out.append("png")
        if self.fmt_svg.isChecked(): out.append("svg")
        if self.fmt_pdf.isChecked(): out.append("pdf")
        return tuple(out) or ("png",)
