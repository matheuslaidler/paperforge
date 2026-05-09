"""QLineEdit + Browse button + drag&drop, used everywhere a file path is needed."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QWidget,
)


class FilePicker(QWidget):
    """Compound widget: ``[QLineEdit       ][Browse...]`` with drag&drop."""

    pathChanged = Signal(str)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        filter: str = "All files (*.*)",
        save_mode: bool = False,
        placeholder: str = "",
    ) -> None:
        super().__init__(parent)
        self._filter = filter
        self._save_mode = save_mode

        self.line = QLineEdit(self)
        self.line.setPlaceholderText(placeholder)
        self.line.textChanged.connect(self.pathChanged)

        self.btn = QPushButton("Browse…", self)
        self.btn.clicked.connect(self._open_dialog)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(self.line, 1)
        layout.addWidget(self.btn, 0)

        self.setAcceptDrops(True)

    # ------------------------------------------------------------------ #
    #  Public API                                                        #
    # ------------------------------------------------------------------ #
    def path(self) -> str:
        return self.line.text().strip()

    def setPath(self, value: str | Path) -> None:
        self.line.setText(str(value))

    def setPlaceholder(self, text: str) -> None:
        self.line.setPlaceholderText(text)

    def setBrowseLabel(self, text: str) -> None:
        self.btn.setText(text)

    # ------------------------------------------------------------------ #
    #  Internals                                                         #
    # ------------------------------------------------------------------ #
    def _open_dialog(self) -> None:
        if self._save_mode:
            path, _ = QFileDialog.getSaveFileName(
                self, "Save as…", self.path() or "", self._filter
            )
        else:
            path, _ = QFileDialog.getOpenFileName(
                self, "Choose file…", self.path() or "", self._filter
            )
        if path:
            self.setPath(path)

    # Drag&drop --------------------------------------------------------- #
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:  # noqa: N802
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:  # noqa: N802
        urls = event.mimeData().urls()
        if not urls:
            return
        local = urls[0].toLocalFile()
        if local:
            self.setPath(local)
            event.acceptProposedAction()
