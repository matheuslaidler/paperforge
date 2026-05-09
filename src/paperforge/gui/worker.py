"""Generic ``QObject`` worker pattern for running blocking builds in a QThread."""

from __future__ import annotations

from typing import Any, Callable

from PySide6.QtCore import QObject, QThread, Signal, Slot


class BuilderWorker(QObject):
    """Runs ``fn(*args, **kwargs)`` on a worker thread and emits signals."""

    finished = Signal(object)        # the function's return value
    failed = Signal(str)             # human-readable error message

    def __init__(
        self,
        fn: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__()
        self._fn, self._args, self._kw = fn, args, kwargs

    @Slot()
    def run(self) -> None:
        try:
            result = self._fn(*self._args, **self._kw)
        except Exception as exc:  # noqa: BLE001
            self.failed.emit(f"{type(exc).__name__}: {exc}")
            return
        self.finished.emit(result)


def run_in_thread(
    parent: QObject,
    fn: Callable[..., Any],
    *args: Any,
    on_finished: Callable[[Any], None],
    on_failed: Callable[[str], None],
    **kwargs: Any,
) -> tuple[QThread, BuilderWorker]:
    """Convenience wrapper: creates worker + thread, wires signals, starts the run.

    Returns the (thread, worker) pair so the caller can keep references alive.
    """
    thread = QThread(parent)
    worker = BuilderWorker(fn, *args, **kwargs)
    worker.moveToThread(thread)

    thread.started.connect(worker.run)
    worker.finished.connect(on_finished)
    worker.failed.connect(on_failed)
    worker.finished.connect(thread.quit)
    worker.failed.connect(thread.quit)
    thread.finished.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)

    thread.start()
    return thread, worker
