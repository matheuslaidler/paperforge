"""Primary push-button that reflects busy state (label change + disabled)."""

from __future__ import annotations

from PySide6.QtWidgets import QPushButton, QWidget


class BusyButton(QPushButton):
    """A QPushButton with explicit busy/idle states. Apply the ``PrimaryButton`` style."""

    def __init__(
        self,
        text: str = "",
        parent: QWidget | None = None,
        *,
        busy_text: str = "Working…",
    ) -> None:
        super().__init__(text, parent)
        self.setObjectName("PrimaryButton")
        self._idle_text = text
        self._busy_text = busy_text

    def set_busy(self, busy: bool) -> None:
        if busy:
            self.setEnabled(False)
            self.setText(self._busy_text)
        else:
            self.setEnabled(True)
            self.setText(self._idle_text)

    def update_idle_text(self, text: str) -> None:
        self._idle_text = text
        if self.isEnabled():
            self.setText(text)

    def update_busy_text(self, text: str) -> None:
        self._busy_text = text
        if not self.isEnabled():
            self.setText(text)
