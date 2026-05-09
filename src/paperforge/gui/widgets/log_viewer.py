"""Read-only log viewer that captures Python stdlib logging records."""

from __future__ import annotations

import logging

from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QPlainTextEdit, QWidget


class _LogBridge(QObject):
    """Bridges ``logging.Handler.emit`` (any thread) to a Qt signal (main thread)."""

    line = Signal(str)


class QtLogHandler(logging.Handler):
    """Logging handler that re-emits records as Qt signals (thread-safe)."""

    def __init__(self) -> None:
        super().__init__(level=logging.INFO)
        self.bridge = _LogBridge()
        self.setFormatter(logging.Formatter("%(message)s"))

    def emit(self, record: logging.LogRecord) -> None:  # noqa: D401
        try:
            msg = self.format(record)
        except Exception:
            msg = record.getMessage()
        self.bridge.line.emit(msg)


class LogViewer(QPlainTextEdit):
    """A read-only QPlainTextEdit hooked to a QtLogHandler installed on demand."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setReadOnly(True)
        self.setMaximumBlockCount(2000)
        self.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        self.setPlaceholderText("Build logs will appear here.")

        self._handler: QtLogHandler | None = None

    # ------------------------------------------------------------------ #
    def append_line(self, text: str) -> None:
        self.appendPlainText(text)
        self.moveCursor(QTextCursor.End)

    def attach_to_logger(self, name: str = "paperforge") -> None:
        """Install a handler on the named logger; emits go straight here."""
        if self._handler is not None:
            return
        h = QtLogHandler()
        h.bridge.line.connect(self.append_line, Qt.QueuedConnection)
        logging.getLogger(name).addHandler(h)
        logging.getLogger(name).setLevel(logging.INFO)
        self._handler = h

    def detach(self) -> None:
        if self._handler is None:
            return
        for log_name in ("paperforge",):
            logging.getLogger(log_name).removeHandler(self._handler)
        self._handler = None
