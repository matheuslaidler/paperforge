"""Process-wide signal bus used to broadcast UI events (language switch, theme, etc.)."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal


class _Bus(QObject):
    lang_changed = Signal(str)            # new lang code, e.g. "pt_br"
    build_started = Signal(str)           # describes which build started
    build_finished = Signal(str)          # describes which build finished
    log_line = Signal(str)                # streaming log line


bus = _Bus()
