"""Editable series panel: list of series + editable XY table + CSV import."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QColorDialog,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from paperforge import i18n
from paperforge.charts.data_loader import Series, load_csv
from paperforge.gui.i18n_qt import Retranslator
from paperforge.theme import DEFAULT_PALETTE


MARKERS = ["o", "s", "^", "v", "D", "P", "*", "x", "+", ".", "none"]
LINESTYLES = ["-", "--", "-.", ":", "none"]


class SeriesPanel(QWidget):
    seriesChanged = Signal()

    def __init__(self, parent: QWidget | None = None, *, mode: str = "series") -> None:
        """``mode='series'`` (line/log/scatter/dose) or ``mode='bar'``."""
        super().__init__(parent)
        self._retr = Retranslator()
        self._mode = mode

        self._build_ui()
        # Start with one empty series for usability.
        self._add_default_series()

    # ------------------------------------------------------------------ #
    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        toolbar = QHBoxLayout()
        self.btn_add = QPushButton(i18n.t("gui.chart.data.add_series"))
        self.btn_remove = QPushButton(i18n.t("gui.chart.data.remove_series"))
        self.btn_dup = QPushButton(i18n.t("gui.chart.data.duplicate_series"))
        self.btn_csv = QPushButton(i18n.t("gui.chart.data.import_csv"))
        self.btn_clear = QPushButton(i18n.t("gui.chart.data.clear"))
        for b in (self.btn_add, self.btn_remove, self.btn_dup, self.btn_csv, self.btn_clear):
            toolbar.addWidget(b)
        toolbar.addStretch(1)
        outer.addLayout(toolbar)

        self.btn_add.clicked.connect(self._add_default_series)
        self.btn_remove.clicked.connect(self._remove_current_series)
        self.btn_dup.clicked.connect(self._duplicate_current_series)
        self.btn_csv.clicked.connect(self._import_csv)
        self.btn_clear.clicked.connect(self._clear_all)

        splitter = QSplitter(Qt.Horizontal, self)

        # Left: list of series.
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        self.series_list = QListWidget()
        self.series_list.currentRowChanged.connect(self._on_series_selected)
        left_layout.addWidget(self.series_list)
        splitter.addWidget(left)

        # Right: editor for current series.
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)

        meta_box = QGroupBox()
        meta_layout = QHBoxLayout(meta_box)
        self.label_edit = QLineEdit()
        self.label_edit.textChanged.connect(self._on_label_changed)
        self.marker_combo = QComboBox(); self.marker_combo.addItems(MARKERS)
        self.linestyle_combo = QComboBox(); self.linestyle_combo.addItems(LINESTYLES)
        self.color_btn = QPushButton("●")
        self.color_btn.clicked.connect(self._pick_color)
        self.color_btn.setFixedWidth(40)

        meta_layout.addWidget(QLabel(i18n.t("gui.chart.data.col_label") + ":"))
        meta_layout.addWidget(self.label_edit, 1)
        if self._mode == "series":
            meta_layout.addWidget(QLabel(i18n.t("gui.chart.data.col_marker") + ":"))
            meta_layout.addWidget(self.marker_combo)
            meta_layout.addWidget(QLabel(i18n.t("gui.chart.data.col_linestyle") + ":"))
            meta_layout.addWidget(self.linestyle_combo)
        meta_layout.addWidget(QLabel(i18n.t("gui.chart.data.col_color") + ":"))
        meta_layout.addWidget(self.color_btn)
        right_layout.addWidget(meta_box)

        # XY table
        if self._mode == "series":
            self.table = QTableWidget(0, 2)
            self.table.setHorizontalHeaderLabels([
                i18n.t("gui.chart.data.col_x"),
                i18n.t("gui.chart.data.col_y"),
            ])
        else:
            # bar mode: one column "value", row per category
            self.table = QTableWidget(0, 2)
            self.table.setHorizontalHeaderLabels(["Category", "Value"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.itemChanged.connect(self._on_cell_edited)
        right_layout.addWidget(self.table)

        # row buttons
        row_buttons = QHBoxLayout()
        self.btn_add_row = QPushButton("+")
        self.btn_del_row = QPushButton("−")
        self.btn_add_row.setFixedWidth(36)
        self.btn_del_row.setFixedWidth(36)
        self.btn_add_row.clicked.connect(self._add_row)
        self.btn_del_row.clicked.connect(self._del_row)
        row_buttons.addWidget(self.btn_add_row)
        row_buttons.addWidget(self.btn_del_row)
        row_buttons.addStretch(1)
        right_layout.addLayout(row_buttons)

        self.marker_combo.currentTextChanged.connect(self._on_meta_changed)
        self.linestyle_combo.currentTextChanged.connect(self._on_meta_changed)

        splitter.addWidget(right)
        splitter.setSizes([180, 460])
        outer.addWidget(splitter)

        # storage
        self._series_data: list[Series] = []
        self._bar_categories: list[str] = []
        self._bar_series: list[dict] = []  # {label, values, color}

    # ------------------------------------------------------------------ #
    def retranslate(self) -> None:
        self._retr.retranslate()
        self.btn_add.setText(i18n.t("gui.chart.data.add_series"))
        self.btn_remove.setText(i18n.t("gui.chart.data.remove_series"))
        self.btn_dup.setText(i18n.t("gui.chart.data.duplicate_series"))
        self.btn_csv.setText(i18n.t("gui.chart.data.import_csv"))
        self.btn_clear.setText(i18n.t("gui.chart.data.clear"))
        if self._mode == "series":
            self.table.setHorizontalHeaderLabels([
                i18n.t("gui.chart.data.col_x"),
                i18n.t("gui.chart.data.col_y"),
            ])

    # ------------------------------------------------------------------ #
    def set_bar_categories(self, categories: list[str]) -> None:
        """In bar mode, sync row count + labels."""
        self._bar_categories = list(categories)
        if self._mode == "bar":
            self.table.blockSignals(True)
            self.table.setRowCount(len(categories))
            for i, cat in enumerate(categories):
                self.table.setItem(i, 0, QTableWidgetItem(cat))
            self.table.blockSignals(False)
            self._sync_current_bar_series_from_table()
            self.seriesChanged.emit()

    # ------------------------------------------------------------------ #
    def series(self) -> list[Series]:
        return list(self._series_data)

    def bar_payload(self) -> tuple[list[str], list[dict]]:
        return list(self._bar_categories), list(self._bar_series)

    # ------------------------------------------------------------------ #
    #  Series CRUD                                                       #
    # ------------------------------------------------------------------ #
    def _add_default_series(self) -> None:
        idx = self._next_default_count()
        color = list(DEFAULT_PALETTE)[idx % len(DEFAULT_PALETTE)]
        markers = ["o", "s", "^", "v", "D", "P"]
        if self._mode == "series":
            # Pre-populate three blank rows so the user has somewhere to type
            # straight away and the live preview hides the placeholder once
            # the first values are entered.
            s = Series(
                label=f"Series {idx + 1}",
                x=[], y=[],
                marker=markers[idx % len(markers)],
                linestyle="-", color=color,
            )
            self._series_data.append(s)
        else:
            entry = {"label": f"Series {idx + 1}",
                     "values": [0.0] * max(1, len(self._bar_categories)),
                     "color": color}
            self._bar_series.append(entry)
        self._refresh_list()
        self.series_list.setCurrentRow(len(self._items()) - 1)
        # Add a few empty rows in series mode so the table is editable on
        # first sight (instead of a single stub row).
        if self._mode == "series" and self.table.rowCount() < 4:
            self.table.blockSignals(True)
            for _ in range(4 - self.table.rowCount()):
                r = self.table.rowCount()
                self.table.insertRow(r)
                self.table.setItem(r, 0, QTableWidgetItem(""))
                self.table.setItem(r, 1, QTableWidgetItem(""))
            self.table.blockSignals(False)
        self.seriesChanged.emit()

    # ------------------------------------------------------------------ #
    #  Bulk loading from examples / external state                        #
    # ------------------------------------------------------------------ #
    def load_series(self, series: list[Series]) -> None:
        """Replace all series at once (used by examples + state restore)."""
        if self._mode != "series":
            return
        self._series_data = [
            Series(label=s.label, x=list(s.x), y=list(s.y),
                   marker=s.marker, linestyle=s.linestyle, color=s.color)
            for s in series
        ]
        self._refresh_list()
        if self._series_data:
            self.series_list.setCurrentRow(0)
        else:
            self.table.setRowCount(0)
        self.seriesChanged.emit()

    def load_bar_payload(self, categories: list[str],
                         bar_series: list[dict]) -> None:
        if self._mode != "bar":
            return
        self._bar_categories = list(categories)
        self._bar_series = [dict(s) for s in bar_series]
        self._refresh_list()
        if self._bar_series:
            self.series_list.setCurrentRow(0)
        else:
            self.table.setRowCount(0)
        self.seriesChanged.emit()

    def _next_default_count(self) -> int:
        return len(self._items())

    def _items(self) -> list:
        return self._series_data if self._mode == "series" else self._bar_series

    def _remove_current_series(self) -> None:
        row = self.series_list.currentRow()
        items = self._items()
        if 0 <= row < len(items):
            items.pop(row)
            self._refresh_list()
            self.series_list.setCurrentRow(min(row, len(items) - 1))
            self.seriesChanged.emit()

    def _duplicate_current_series(self) -> None:
        row = self.series_list.currentRow()
        items = self._items()
        if 0 <= row < len(items):
            import copy
            clone = copy.deepcopy(items[row])
            if isinstance(clone, Series):
                clone.label += " (copy)"
            else:
                clone["label"] = clone.get("label", "") + " (copy)"
            items.insert(row + 1, clone)
            self._refresh_list()
            self.series_list.setCurrentRow(row + 1)
            self.seriesChanged.emit()

    def _clear_all(self) -> None:
        if self._mode == "series":
            self._series_data.clear()
        else:
            self._bar_series.clear()
        self.series_list.clear()
        self.table.setRowCount(0)
        self.seriesChanged.emit()

    # ------------------------------------------------------------------ #
    def _refresh_list(self) -> None:
        self.series_list.clear()
        for item in self._items():
            label = item.label if isinstance(item, Series) else item.get("label", "")
            color = item.color if isinstance(item, Series) else item.get("color", "#888")
            li = QListWidgetItem(f"  {label}")
            li.setForeground(QColor(color or "#222"))
            self.series_list.addItem(li)

    def _on_series_selected(self, row: int) -> None:
        items = self._items()
        if not (0 <= row < len(items)):
            self.label_edit.blockSignals(True); self.label_edit.setText(""); self.label_edit.blockSignals(False)
            self.table.setRowCount(0)
            return
        cur = items[row]
        self.label_edit.blockSignals(True)
        if isinstance(cur, Series):
            self.label_edit.setText(cur.label)
            self.marker_combo.setCurrentText(cur.marker or "o")
            self.linestyle_combo.setCurrentText(cur.linestyle or "-")
            self._set_color_btn(cur.color or "#2E86AB")
            # populate table with x/y
            self.table.blockSignals(True)
            self.table.setRowCount(max(len(cur.x), 1))
            for i in range(self.table.rowCount()):
                xv = str(cur.x[i]) if i < len(cur.x) else ""
                yv = str(cur.y[i]) if i < len(cur.y) else ""
                self.table.setItem(i, 0, QTableWidgetItem(xv))
                self.table.setItem(i, 1, QTableWidgetItem(yv))
            self.table.blockSignals(False)
        else:
            self.label_edit.setText(cur.get("label", ""))
            self._set_color_btn(cur.get("color", "#888"))
            self.table.blockSignals(True)
            self.table.setRowCount(len(self._bar_categories))
            for i, cat in enumerate(self._bar_categories):
                self.table.setItem(i, 0, QTableWidgetItem(cat))
                vals = cur.get("values", [])
                v = vals[i] if i < len(vals) else 0.0
                self.table.setItem(i, 1, QTableWidgetItem(str(v)))
            self.table.blockSignals(False)
        self.label_edit.blockSignals(False)

    # ------------------------------------------------------------------ #
    def _on_label_changed(self, text: str) -> None:
        row = self.series_list.currentRow()
        items = self._items()
        if not (0 <= row < len(items)):
            return
        if isinstance(items[row], Series):
            items[row].label = text
        else:
            items[row]["label"] = text
        li = self.series_list.item(row)
        if li:
            li.setText(f"  {text}")
        self.seriesChanged.emit()

    def _on_meta_changed(self) -> None:
        row = self.series_list.currentRow()
        if not (0 <= row < len(self._series_data)):
            return
        s = self._series_data[row]
        s.marker = self.marker_combo.currentText()
        s.linestyle = self.linestyle_combo.currentText()
        self.seriesChanged.emit()

    def _on_cell_edited(self, _item: QTableWidgetItem) -> None:
        if self._mode == "series":
            self._sync_current_series_from_table()
        else:
            self._sync_current_bar_series_from_table()
        self.seriesChanged.emit()

    def _sync_current_series_from_table(self) -> None:
        row = self.series_list.currentRow()
        if not (0 <= row < len(self._series_data)):
            return
        xs: list[float] = []
        ys: list[float] = []
        for r in range(self.table.rowCount()):
            x_item = self.table.item(r, 0); y_item = self.table.item(r, 1)
            try:
                x = float((x_item.text() if x_item else "").strip())
                y = float((y_item.text() if y_item else "").strip())
            except (TypeError, ValueError):
                continue
            xs.append(x); ys.append(y)
        self._series_data[row].x = xs
        self._series_data[row].y = ys

    def _sync_current_bar_series_from_table(self) -> None:
        row = self.series_list.currentRow()
        if not (0 <= row < len(self._bar_series)):
            return
        # Update categories from column 0
        new_cats: list[str] = []
        new_vals: list[float] = []
        for r in range(self.table.rowCount()):
            cat_item = self.table.item(r, 0)
            val_item = self.table.item(r, 1)
            new_cats.append((cat_item.text() if cat_item else "").strip())
            try:
                new_vals.append(float((val_item.text() if val_item else "").strip()))
            except (TypeError, ValueError):
                new_vals.append(0.0)
        self._bar_categories = new_cats
        self._bar_series[row]["values"] = new_vals
        # propagate categories to other bar series
        for other in self._bar_series:
            cur_vals = other.get("values", [])
            if len(cur_vals) < len(new_cats):
                cur_vals = list(cur_vals) + [0.0] * (len(new_cats) - len(cur_vals))
            elif len(cur_vals) > len(new_cats):
                cur_vals = cur_vals[: len(new_cats)]
            other["values"] = cur_vals

    # ------------------------------------------------------------------ #
    def _add_row(self) -> None:
        n = self.table.rowCount()
        self.table.setRowCount(n + 1)
        self.table.setItem(n, 0, QTableWidgetItem(""))
        self.table.setItem(n, 1, QTableWidgetItem(""))

    def _del_row(self) -> None:
        n = self.table.currentRow()
        if n < 0:
            n = self.table.rowCount() - 1
        if n >= 0:
            self.table.removeRow(n)
        if self._mode == "series":
            self._sync_current_series_from_table()
        else:
            self._sync_current_bar_series_from_table()
        self.seriesChanged.emit()

    # ------------------------------------------------------------------ #
    def _set_color_btn(self, color: str) -> None:
        self.color_btn.setStyleSheet(
            f"background:{color}; color:white; border-radius:3px;"
        )
        self._current_color = color

    def _pick_color(self) -> None:
        row = self.series_list.currentRow()
        items = self._items()
        if not (0 <= row < len(items)):
            return
        current = (items[row].color if isinstance(items[row], Series)
                   else items[row].get("color", "#2E86AB"))
        color = QColorDialog.getColor(QColor(current or "#2E86AB"), self)
        if not color.isValid():
            return
        chex = color.name()
        if isinstance(items[row], Series):
            items[row].color = chex
        else:
            items[row]["color"] = chex
        self._set_color_btn(chex)
        li = self.series_list.item(row)
        if li:
            li.setForeground(QColor(chex))
        self.seriesChanged.emit()

    # ------------------------------------------------------------------ #
    def _import_csv(self) -> None:
        if self._mode != "series":
            QMessageBox.information(self, "PaperForge",
                                    "CSV import is for non-bar templates.")
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "Import CSV", "", "CSV (*.csv);;All files (*.*)",
        )
        if not path:
            return
        # Use a quick dialog to pick columns.
        from paperforge.gui.chart_tab.csv_import_dialog import CsvImportDialog
        dlg = CsvImportDialog(Path(path), self)
        if dlg.exec() != dlg.Accepted:
            return
        try:
            data = load_csv(Path(path), x_col=dlg.x_col(),
                            y_col=dlg.y_col(), series_col=dlg.series_col())
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "PaperForge", f"CSV error: {exc}")
            return
        if not data.series:
            QMessageBox.warning(self, "PaperForge", "No data points loaded.")
            return
        # Replace current series.
        for i, new in enumerate(data.series):
            new.color = list(DEFAULT_PALETTE)[i % len(DEFAULT_PALETTE)]
            new.marker = list(("o", "s", "^", "v", "D", "P"))[i % 6]
        self._series_data = list(data.series)
        self._refresh_list()
        self.series_list.setCurrentRow(0)
        self.seriesChanged.emit()
