"""Slides tab: Markdown → PowerPoint GUI."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QThread
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from paperforge import i18n
from paperforge.gui.i18n_qt import Retranslator
from paperforge.gui.signals import bus
from paperforge.gui.widgets.busy_button import BusyButton
from paperforge.gui.widgets.file_picker import FilePicker
from paperforge.gui.widgets.log_viewer import LogViewer
from paperforge.gui.worker import run_in_thread
from paperforge.slides.builder import (
    SlideBuildOptions,
    SlideBuildResult,
    SlideBuilder,
)


class SlidesTab(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._retr = Retranslator()
        self._thread: Optional[QThread] = None
        self._build_ui()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 14, 14, 14)

        splitter = QSplitter(Qt.Vertical, self)

        top = QWidget()
        top_layout = QVBoxLayout(top)
        top_layout.setContentsMargins(0, 0, 0, 0)

        self.input_picker = FilePicker(filter="Markdown (*.md *.markdown)")
        self.input_picker.setPlaceholder(i18n.t("gui.placeholder.md"))
        self.input_picker.pathChanged.connect(self._auto_output)
        self.output_picker = FilePicker(save_mode=True, filter="PowerPoint (*.pptx)")
        self.output_picker.setPlaceholder(i18n.t("gui.placeholder.pptx"))

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["default", "dark", "minimal", "nature"])
        self.aspect_combo = QComboBox()
        self.aspect_combo.addItems(["16:9", "4:3"])
        self.cover_chk = QCheckBox()
        self.cover_chk.setChecked(True)
        self.footer_edit = QLineEdit("{n} / {total}")
        self.footer_edit.setPlaceholderText(i18n.t("gui.slides.placeholder.footer"))

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        self._lbl_in = self._make_label("gui.label.input")
        self._lbl_out = self._make_label("gui.label.output")
        self._lbl_theme = self._make_label("gui.label.theme")
        self._lbl_aspect = self._make_label("gui.slides.label.aspect")
        self._lbl_cover = self._make_label("gui.slides.label.cover")
        self._lbl_footer = self._make_label("gui.slides.label.footer")
        form.addRow(self._lbl_in, self.input_picker)
        form.addRow(self._lbl_out, self.output_picker)
        form.addRow(self._lbl_theme, self.theme_combo)
        form.addRow(self._lbl_aspect, self.aspect_combo)
        form.addRow(self._lbl_cover, self.cover_chk)
        form.addRow(self._lbl_footer, self.footer_edit)
        top_layout.addLayout(form)

        self.build_btn = BusyButton(
            i18n.t("gui.slides.button.build"),
            busy_text=i18n.t("gui.slides.button.busy"),
        )
        self.build_btn.clicked.connect(self._on_build)
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        btn_row.addWidget(self.build_btn)
        top_layout.addLayout(btn_row)
        top_layout.addStretch(1)

        self.log = LogViewer()
        self.log.attach_to_logger("paperforge")

        splitter.addWidget(top)
        splitter.addWidget(self.log)
        splitter.setSizes([450, 200])
        outer.addWidget(splitter)

        self._retr.bind(self.build_btn, "gui.slides.button.build",
                        self.build_btn.update_idle_text)
        self._retr.bind(self.build_btn, "gui.slides.button.busy",
                        self.build_btn.update_busy_text)

    def _make_label(self, key: str) -> QLabel:
        lbl = QLabel(i18n.t(key))
        self._retr.bind(lbl, key)
        return lbl

    def retranslate(self) -> None:
        self._retr.retranslate()
        self.input_picker.setPlaceholder(i18n.t("gui.placeholder.md"))
        self.output_picker.setPlaceholder(i18n.t("gui.placeholder.pptx"))
        self.footer_edit.setPlaceholderText(i18n.t("gui.slides.placeholder.footer"))

    def _auto_output(self, text: str) -> None:
        if text.strip() and not self.output_picker.path():
            self.output_picker.setPath(str(Path(text).with_suffix(".pptx")))

    def _on_build(self) -> None:
        input_path = Path(self.input_picker.path()).expanduser()
        if not input_path.is_file():
            QMessageBox.warning(
                self, "PaperForge",
                i18n.t("slides.error.input_missing", path=str(input_path)),
            )
            return
        out_text = self.output_picker.path() or str(input_path.with_suffix(".pptx"))
        output_path = Path(out_text).expanduser()

        opts = SlideBuildOptions(
            theme=self.theme_combo.currentText(),
            aspect=self.aspect_combo.currentText(),
            cover=self.cover_chk.isChecked(),
            footer_template=self.footer_edit.text() or "{n} / {total}",
        )
        builder = SlideBuilder(opts)
        self.build_btn.set_busy(True)
        bus.build_started.emit("PowerPoint")

        self._thread, _ = run_in_thread(
            self,
            builder.build,
            input_path,
            output_path,
            on_finished=self._on_finished,
            on_failed=self._on_failed,
        )

    def _on_finished(self, result: SlideBuildResult) -> None:
        self.build_btn.set_busy(False)
        bus.build_finished.emit("PowerPoint")
        self.log.append_line(
            i18n.t("slides.ok", path=str(result.path), slides=result.slide_count)
        )

    def _on_failed(self, message: str) -> None:
        self.build_btn.set_busy(False)
        bus.build_finished.emit("PowerPoint")
        self.log.append_line(f"ERROR: {message}")
        QMessageBox.critical(self, "PaperForge", message)
