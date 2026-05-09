"""Modal dialog for picking CSV columns when importing data."""

from __future__ import annotations

import csv
from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from paperforge import i18n


class CsvImportDialog(QDialog):
    def __init__(self, path: Path, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(i18n.t("gui.chart.csv.title"))
        self.setMinimumWidth(550)

        with path.open(encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            self._fieldnames = list(reader.fieldnames or [])
            self._rows = list(reader)

        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.x_combo = QComboBox(); self.x_combo.addItems(self._fieldnames)
        self.y_combo = QComboBox(); self.y_combo.addItems(self._fieldnames)
        if len(self._fieldnames) >= 2:
            self.y_combo.setCurrentIndex(1)
        self.series_combo = QComboBox(); self.series_combo.addItem("")
        for fn in self._fieldnames:
            self.series_combo.addItem(fn)
        form.addRow(QLabel(i18n.t("gui.chart.csv.x_col")), self.x_combo)
        form.addRow(QLabel(i18n.t("gui.chart.csv.y_col")), self.y_combo)
        form.addRow(QLabel(i18n.t("gui.chart.csv.series_col")), self.series_combo)
        layout.addLayout(form)

        # Preview
        preview_lbl = QLabel(i18n.t("gui.chart.csv.preview"))
        layout.addWidget(preview_lbl)
        preview = QTableWidget(min(8, len(self._rows)), len(self._fieldnames))
        preview.setHorizontalHeaderLabels(self._fieldnames)
        for r, row in enumerate(self._rows[: preview.rowCount()]):
            for c, fn in enumerate(self._fieldnames):
                preview.setItem(r, c, QTableWidgetItem(str(row.get(fn, ""))))
        preview.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        preview.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(preview)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # ------------------------------------------------------------------ #
    def x_col(self) -> str | None:
        return self.x_combo.currentText() or None

    def y_col(self) -> str | None:
        return self.y_combo.currentText() or None

    def series_col(self) -> str | None:
        v = self.series_combo.currentText()
        return v or None
