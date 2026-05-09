"""Top-level Chart tab: stitches together picker, data, annotations, style + live preview."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from paperforge import i18n
from paperforge.charts.builder import build_chart_from_state
from paperforge.gui.chart_tab.annotations_form import AnnotationsForm
from paperforge.gui.chart_tab.examples_data import get_example
from paperforge.gui.chart_tab.preview_canvas import PreviewCanvas
from paperforge.gui.chart_tab.series_table import SeriesPanel
from paperforge.gui.chart_tab.state import ChartState
from paperforge.gui.chart_tab.style_panel import StylePanel
from paperforge.gui.chart_tab.template_picker import TemplatePicker
from paperforge.gui.signals import bus
from paperforge.gui.widgets.busy_button import BusyButton


SECTIONS = [
    ("template", "gui.chart.section.template"),
    ("data", "gui.chart.section.data"),
    ("annot", "gui.chart.section.annotations"),
    ("style", "gui.chart.section.style"),
]


class ChartTab(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._state = ChartState()
        # Track which templates have been seeded with example data so we
        # don't clobber the user's edits when they switch back and forth.
        self._seeded: set[str] = set()
        self._build_ui()
        self._wire_signals()
        # Seed the default ("line") template with example data on first open.
        self._apply_example("line")
        self._refresh_state()

    # ------------------------------------------------------------------ #
    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)

        splitter = QSplitter(Qt.Horizontal, self)

        # Left: stacked panels with section list.
        left = QWidget()
        left_layout = QHBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.section_list = QListWidget()
        self.section_list.setMaximumWidth(140)
        for code, key in SECTIONS:
            self.section_list.addItem(QListWidgetItem(i18n.t(key)))
        self.section_list.setCurrentRow(0)
        left_layout.addWidget(self.section_list)

        self.stack = QStackedWidget()
        self.template_picker = TemplatePicker()
        self.series_panel = SeriesPanel(mode="series")
        self.bar_panel = SeriesPanel(mode="bar")
        self.bar_panel.set_bar_categories(["A", "B", "C"])
        self.annotations = AnnotationsForm()
        self.style_panel = StylePanel()

        # Section 1: Template
        self.stack.addWidget(self.template_picker)
        # Section 2: Data — switched between series and bar panels
        data_holder = QWidget()
        dh = QVBoxLayout(data_holder); dh.setContentsMargins(0, 0, 0, 0)
        dh.addWidget(self.series_panel)
        dh.addWidget(self.bar_panel)
        self.bar_panel.hide()
        self.stack.addWidget(data_holder)
        # Section 3: Annotations
        self.stack.addWidget(self.annotations)
        # Section 4: Style
        self.stack.addWidget(self.style_panel)

        left_layout.addWidget(self.stack, 1)
        splitter.addWidget(left)

        # Right: live preview + save button.
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        self.preview = PreviewCanvas()
        rl.addWidget(self.preview, 1)

        self.example_btn = QPushButton("Load example")
        self.example_btn.clicked.connect(self._on_load_example_clicked)
        self.save_btn = BusyButton(
            i18n.t("gui.chart.button.save"),
            busy_text=i18n.t("gui.chart.button.busy"),
        )
        self.save_btn.clicked.connect(self._save)
        save_row = QHBoxLayout()
        save_row.addWidget(self.example_btn)
        save_row.addStretch(1)
        save_row.addWidget(self.save_btn)
        rl.addLayout(save_row)
        splitter.addWidget(right)
        splitter.setSizes([520, 580])

        outer.addWidget(splitter)

    # ------------------------------------------------------------------ #
    def _wire_signals(self) -> None:
        self.section_list.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.template_picker.templateChanged.connect(self._on_template_changed)
        self.template_picker.metaChanged.connect(self._refresh_state)
        self.series_panel.seriesChanged.connect(self._refresh_state)
        self.bar_panel.seriesChanged.connect(self._refresh_state)
        self.annotations.annotationsChanged.connect(self._refresh_state)
        self.style_panel.styleChanged.connect(self._refresh_state)

    # ------------------------------------------------------------------ #
    def retranslate(self) -> None:
        for i, (_code, key) in enumerate(SECTIONS):
            self.section_list.item(i).setText(i18n.t(key))
        self.template_picker.retranslate()
        self.series_panel.retranslate()
        self.bar_panel.retranslate()
        self.annotations.retranslate()
        self.style_panel.retranslate()
        self.save_btn.update_idle_text(i18n.t("gui.chart.button.save"))
        self.save_btn.update_busy_text(i18n.t("gui.chart.button.busy"))

    # ------------------------------------------------------------------ #
    def _on_template_changed(self, code: str) -> None:
        # swap series/bar panels
        is_bar = code == "bar"
        self.bar_panel.setVisible(is_bar)
        self.series_panel.setVisible(not is_bar)
        self.annotations.set_supported(code == "log-scale")
        # Seed example data on the first time each template is selected.
        if code not in self._seeded:
            self._apply_example(code)
        self._refresh_state()

    def _on_load_example_clicked(self) -> None:
        """Reload the canonical example for the current template (overwrites)."""
        code = self.template_picker.current_template()
        self._apply_example(code, force=True)
        self._refresh_state()

    def _apply_example(self, template: str, *, force: bool = False) -> None:
        """Populate every panel with the canonical example for ``template``."""
        ex = get_example(template)
        # Meta
        self.template_picker.set_meta(ex.title, ex.xlabel, ex.ylabel, ex.source)
        # Style
        self.style_panel.log_x.setChecked(ex.log_x)
        self.style_panel.log_y.setChecked(ex.log_y)
        if ex.legend_loc:
            idx = self.style_panel.legend.findText(ex.legend_loc)
            if idx >= 0:
                self.style_panel.legend.setCurrentIndex(idx)
        # Data
        if template == "bar":
            self.bar_panel.load_bar_payload(ex.bar_categories, ex.bar_series)
        else:
            self.series_panel.load_series(ex.series)
        # Annotations
        self.annotations.load(ex.vlines, ex.bands, ex.envelopes)
        self._seeded.add(template)

    # ------------------------------------------------------------------ #
    def _refresh_state(self) -> None:
        s = self._state
        s.template = self.template_picker.current_template()
        s.title, s.xlabel, s.ylabel, s.source = self.template_picker.meta()

        if s.template == "bar":
            cats, bar_series = self.bar_panel.bar_payload()
            s.bar_categories = cats
            s.bar_series = bar_series
            s.series = []
        else:
            s.series = self.series_panel.series()
            s.bar_categories = []
            s.bar_series = []

        vlines, bands, envelopes = self.annotations.collect()
        s.vlines = vlines
        s.bands = bands
        s.envelopes = envelopes

        s.dpi = self.style_panel.dpi.value()
        s.width = self.style_panel.width.value()
        s.height = self.style_panel.height.value()
        s.palette_name = self.style_panel.palette.currentText()
        s.legend_loc = self.style_panel.legend.currentText()
        s.log_x = self.style_panel.log_x.isChecked()
        s.log_y = self.style_panel.log_y.isChecked()
        s.formats = self.style_panel.chosen_formats()

        self.preview.request_render(s)

    # ------------------------------------------------------------------ #
    def _save(self) -> None:
        s = self._state
        if s.template == "bar":
            if not any(item.get("values") for item in s.bar_series):
                QMessageBox.warning(self, "PaperForge",
                                    i18n.t("gui.chart.error.missing_data"))
                return
        elif not any(ss.x and ss.y for ss in s.series):
            QMessageBox.warning(self, "PaperForge",
                                i18n.t("gui.chart.error.missing_data"))
            return

        suggested = f"chart_{s.template}.{s.formats[0]}"
        path, _ = QFileDialog.getSaveFileName(
            self, i18n.t("gui.chart.button.save"), suggested,
            "Image (*.png *.svg *.pdf);;All files (*.*)",
        )
        if not path:
            return

        compiled = self.preview._compile_envelopes(s)
        extras = s.extras(compiled_envelopes=compiled)
        series = s.series if s.template != "bar" else []

        self.save_btn.set_busy(True)
        bus.build_started.emit("Chart")
        try:
            result = build_chart_from_state(
                s.template,
                s.base_cfg_kwargs(),
                series,
                extras,
                Path(path),
                formats=s.formats,
            )
        except Exception as exc:  # noqa: BLE001
            self.save_btn.set_busy(False)
            bus.build_finished.emit("Chart")
            QMessageBox.critical(self, "PaperForge", str(exc))
            return
        self.save_btn.set_busy(False)
        bus.build_finished.emit("Chart")
        QMessageBox.information(
            self, "PaperForge",
            i18n.t("chart.ok", path=str(result.path)),
        )
