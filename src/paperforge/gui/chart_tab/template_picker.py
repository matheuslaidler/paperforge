"""Combo + description for picking one of the five chart templates."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from paperforge import i18n
from paperforge.gui.i18n_qt import Retranslator

TEMPLATES = [
    ("line", "Time series, kinetic curves"),
    ("bar", "Grouped bars with value labels"),
    ("log-scale", "Survival/decay; log-Y; theoretical envelopes"),
    ("scatter", "Correlation analysis"),
    ("dose-response", "Viability vs dose / concentration"),
]


class TemplatePicker(QWidget):
    templateChanged = Signal(str)
    metaChanged = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._retr = Retranslator()

        self.combo = QComboBox()
        for code, _desc in TEMPLATES:
            self.combo.addItem(code, code)
        self.combo.currentIndexChanged.connect(self._emit_template)

        self.desc = QLabel("")
        self.desc.setWordWrap(True)
        self.desc.setStyleSheet("color: #52606D; font-style: italic;")
        self._update_desc()

        self.title = QLineEdit()
        self.xlabel = QLineEdit()
        self.ylabel = QLineEdit()
        self.source = QLineEdit()
        self.title.setPlaceholderText(i18n.t("gui.placeholder.title"))
        for w in (self.title, self.xlabel, self.ylabel, self.source):
            w.textChanged.connect(self.metaChanged)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        form_top = QFormLayout()
        self._lbl_template = self._make_label("gui.label.template")
        form_top.addRow(self._lbl_template, self.combo)
        form_top.addRow(QLabel(""), self.desc)
        layout.addLayout(form_top)

        form_meta = QFormLayout()
        self._lbl_title = self._make_label("gui.label.title")
        self._lbl_xlabel = self._make_label("gui.label.xlabel")
        self._lbl_ylabel = self._make_label("gui.label.ylabel")
        self._lbl_source = self._make_label("gui.label.source")
        form_meta.addRow(self._lbl_title, self.title)
        form_meta.addRow(self._lbl_xlabel, self.xlabel)
        form_meta.addRow(self._lbl_ylabel, self.ylabel)
        form_meta.addRow(self._lbl_source, self.source)
        layout.addLayout(form_meta)
        layout.addStretch(1)

    def _make_label(self, key: str) -> QLabel:
        lbl = QLabel(i18n.t(key))
        self._retr.bind(lbl, key)
        return lbl

    def retranslate(self) -> None:
        self._retr.retranslate()
        self.title.setPlaceholderText(i18n.t("gui.placeholder.title"))

    def _update_desc(self) -> None:
        idx = self.combo.currentIndex()
        if 0 <= idx < len(TEMPLATES):
            self.desc.setText(TEMPLATES[idx][1])

    def _emit_template(self, idx: int) -> None:
        self._update_desc()
        if 0 <= idx < len(TEMPLATES):
            self.templateChanged.emit(TEMPLATES[idx][0])

    # ------------------------------------------------------------------ #
    def current_template(self) -> str:
        return self.combo.currentData() or "line"

    def meta(self) -> tuple[str, str, str, str]:
        return (
            self.title.text(),
            self.xlabel.text(),
            self.ylabel.text(),
            self.source.text(),
        )

    def set_meta(self, title: str, xlabel: str, ylabel: str, source: str) -> None:
        for w, value in (
            (self.title, title),
            (self.xlabel, xlabel),
            (self.ylabel, ylabel),
            (self.source, source),
        ):
            w.blockSignals(True)
            w.setText(value)
            w.blockSignals(False)
        self.metaChanged.emit()
