"""PDF tab: Markdown → PDF GUI."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QThread
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QSpinBox,
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
from paperforge.pdf.builder import PDFBuilder, PDFBuildOptions, PDFBuildResult


class PdfTab(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._retr = Retranslator()
        self._thread: Optional[QThread] = None
        self._build_ui()

    # ------------------------------------------------------------------ #
    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 14, 14, 14)

        splitter = QSplitter(Qt.Vertical, self)

        # ---------- top: form ---------- #
        top = QWidget()
        top_layout = QVBoxLayout(top)
        top_layout.setContentsMargins(0, 0, 0, 0)

        # Required inputs
        self.input_picker = FilePicker(filter="Markdown (*.md *.markdown)")
        self.input_picker.setPlaceholder(i18n.t("gui.placeholder.md"))
        self.input_picker.pathChanged.connect(self._auto_output)
        self.output_picker = FilePicker(save_mode=True, filter="PDF (*.pdf)")
        self.output_picker.setPlaceholder(i18n.t("gui.placeholder.pdf"))

        primary = QFormLayout()
        primary.setLabelAlignment(Qt.AlignRight)
        self._lbl_input = self._make_label("gui.label.input")
        self._lbl_output = self._make_label("gui.label.output")
        primary.addRow(self._lbl_input, self.input_picker)
        primary.addRow(self._lbl_output, self.output_picker)
        top_layout.addLayout(primary)

        # Styling group
        self.style_combo = QComboBox()
        self.style_combo.addItems(["default", "minimal", "academic"])
        self.css_picker = FilePicker(filter="CSS (*.css)")
        self.css_picker.setPlaceholder(i18n.t("gui.placeholder.css"))
        self.refs_combo = QComboBox()
        self.refs_combo.addItems(["abnt", "none"])

        styling = QGroupBox()
        self._gb_style = styling
        f1 = QFormLayout(styling)
        self._lbl_style = self._make_label("gui.label.style")
        self._lbl_css = self._make_label("gui.pdf.label.css")
        self._lbl_refs = self._make_label("gui.pdf.label.references")
        f1.addRow(self._lbl_style, self.style_combo)
        f1.addRow(self._lbl_css, self.css_picker)
        f1.addRow(self._lbl_refs, self.refs_combo)
        top_layout.addWidget(styling)

        # Layout group
        self.orient_combo = QComboBox()
        self.orient_combo.addItems(["portrait", "landscape"])
        self.margin_t = QLineEdit("2cm")
        self.margin_r = QLineEdit("1.8cm")
        self.margin_b = QLineEdit("2cm")
        self.margin_l = QLineEdit("1.8cm")

        layout_group = QGroupBox()
        self._gb_layout = layout_group
        f2 = QFormLayout(layout_group)
        self._lbl_orient = self._make_label("gui.pdf.label.orientation")
        self._lbl_mt = self._make_label("gui.pdf.label.margin_top")
        self._lbl_mr = self._make_label("gui.pdf.label.margin_right")
        self._lbl_mb = self._make_label("gui.pdf.label.margin_bottom")
        self._lbl_ml = self._make_label("gui.pdf.label.margin_left")
        f2.addRow(self._lbl_orient, self.orient_combo)
        margins_row = QHBoxLayout()
        margins_row.addWidget(self.margin_t)
        margins_row.addWidget(self.margin_r)
        margins_row.addWidget(self.margin_b)
        margins_row.addWidget(self.margin_l)
        margins_w = QWidget()
        margins_w.setLayout(margins_row)
        f2.addRow(self._lbl_mt, margins_w)
        top_layout.addWidget(layout_group)

        # Advanced group
        adv = QGroupBox()
        self._gb_adv = adv
        f3 = QFormLayout(adv)
        self.mathjax_chk = QCheckBox()
        self.mathjax_chk.setChecked(True)
        self.mathjax_engine = QComboBox()
        self.mathjax_engine.addItems(["cdn", "katex-local"])
        self.mathjax_timeout = QSpinBox()
        self.mathjax_timeout.setRange(0, 60)
        self.mathjax_timeout.setValue(8)
        self.keep_html_chk = QCheckBox()
        self.open_after_chk = QCheckBox()
        self.open_after_chk.setChecked(True)
        self._lbl_mj = self._make_label("gui.pdf.label.mathjax")
        self._lbl_mj_engine = self._make_label("gui.pdf.label.mathjax_engine")
        self._lbl_mj_timeout = self._make_label("gui.pdf.label.mathjax_timeout")
        self._lbl_keep = self._make_label("gui.pdf.label.keep_html")
        self._lbl_open = self._make_label("gui.pdf.label.open_after")
        f3.addRow(self._lbl_mj, self.mathjax_chk)
        f3.addRow(self._lbl_mj_engine, self.mathjax_engine)
        f3.addRow(self._lbl_mj_timeout, self.mathjax_timeout)
        f3.addRow(self._lbl_keep, self.keep_html_chk)
        f3.addRow(self._lbl_open, self.open_after_chk)
        top_layout.addWidget(adv)

        # Build button
        self.build_btn = BusyButton(
            i18n.t("gui.pdf.button.build"),
            busy_text=i18n.t("gui.pdf.button.busy"),
        )
        self.build_btn.clicked.connect(self._on_build)
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        btn_row.addWidget(self.build_btn)
        top_layout.addLayout(btn_row)
        top_layout.addStretch(1)

        # ---------- bottom: log ---------- #
        self.log = LogViewer()
        self.log.attach_to_logger("paperforge")

        splitter.addWidget(top)
        splitter.addWidget(self.log)
        splitter.setSizes([550, 200])

        outer.addWidget(splitter)

        # Group titles + retranslate
        styling.setTitle(i18n.t("gui.pdf.group.styling"))
        layout_group.setTitle(i18n.t("gui.pdf.group.layout"))
        adv.setTitle(i18n.t("gui.pdf.group.advanced"))
        self._retr.bind(styling, "gui.pdf.group.styling", styling.setTitle)
        self._retr.bind(layout_group, "gui.pdf.group.layout", layout_group.setTitle)
        self._retr.bind(adv, "gui.pdf.group.advanced", adv.setTitle)
        self._retr.bind(self.build_btn, "gui.pdf.button.build", self.build_btn.update_idle_text)
        self._retr.bind(self.build_btn, "gui.pdf.button.busy", self.build_btn.update_busy_text)

    # ------------------------------------------------------------------ #
    def _make_label(self, key: str):
        from PySide6.QtWidgets import QLabel
        lbl = QLabel(i18n.t(key))
        self._retr.bind(lbl, key)
        return lbl

    # ------------------------------------------------------------------ #
    def retranslate(self) -> None:
        self._retr.retranslate()
        self.input_picker.setPlaceholder(i18n.t("gui.placeholder.md"))
        self.output_picker.setPlaceholder(i18n.t("gui.placeholder.pdf"))
        self.css_picker.setPlaceholder(i18n.t("gui.placeholder.css"))

    # ------------------------------------------------------------------ #
    def _auto_output(self, text: str) -> None:
        if not text.strip():
            return
        if not self.output_picker.path():
            self.output_picker.setPath(str(Path(text).with_suffix(".pdf")))

    # ------------------------------------------------------------------ #
    def _collect_options(self) -> tuple[Path, Path, PDFBuildOptions]:
        input_path = Path(self.input_picker.path()).expanduser()
        if not input_path.is_file():
            raise FileNotFoundError(
                i18n.t("pdf.error.input_missing", path=str(input_path))
            )
        out_text = self.output_picker.path() or str(input_path.with_suffix(".pdf"))
        output_path = Path(out_text).expanduser()
        css_text = self.css_picker.path()
        opts = PDFBuildOptions(
            style=self.style_combo.currentText(),
            css_path=Path(css_text).expanduser() if css_text else None,
            orientation=self.orient_combo.currentText(),
            margins=(
                self.margin_t.text() or "2cm",
                self.margin_r.text() or "1.8cm",
                self.margin_b.text() or "2cm",
                self.margin_l.text() or "1.8cm",
            ),
            mathjax=self.mathjax_chk.isChecked(),
            mathjax_engine=self.mathjax_engine.currentText(),
            mathjax_timeout=self.mathjax_timeout.value(),
            references_style=self.refs_combo.currentText(),
            keep_html=self.keep_html_chk.isChecked(),
        )
        return input_path, output_path, opts

    # ------------------------------------------------------------------ #
    def _on_build(self) -> None:
        try:
            input_path, output_path, opts = self._collect_options()
        except FileNotFoundError as exc:
            QMessageBox.warning(self, "PaperForge", str(exc))
            return

        builder = PDFBuilder(opts)
        self.build_btn.set_busy(True)
        bus.build_started.emit("PDF")

        self._thread, _ = run_in_thread(
            self,
            builder.build,
            input_path,
            output_path,
            on_finished=self._on_finished,
            on_failed=self._on_failed,
        )

    def _on_finished(self, result: PDFBuildResult) -> None:
        self.build_btn.set_busy(False)
        bus.build_finished.emit("PDF")
        self.log.append_line(
            i18n.t("pdf.ok",
                   path=str(result.path),
                   size_kb=result.size_kb,
                   pages=result.pages)
        )
        if self.open_after_chk.isChecked():
            _open_path(result.path)

    def _on_failed(self, message: str) -> None:
        self.build_btn.set_busy(False)
        bus.build_finished.emit("PDF")
        self.log.append_line(f"ERROR: {message}")
        QMessageBox.critical(self, "PaperForge", message)


# --------------------------------------------------------------------------- #
def _open_path(path: Path) -> None:
    import platform
    import subprocess
    system = platform.system()
    try:
        if system == "Windows":
            import os
            os.startfile(str(path))  # type: ignore[attr-defined]
        elif system == "Darwin":
            subprocess.run(["open", str(path)], check=False)
        else:
            subprocess.run(["xdg-open", str(path)], check=False)
    except Exception:
        pass
