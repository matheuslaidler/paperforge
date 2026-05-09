"""Helpers that bridge ``paperforge.i18n`` to Qt widgets (auto-retranslation)."""

from __future__ import annotations

from typing import Callable

from PySide6.QtWidgets import QLabel, QPushButton, QWidget

from paperforge import i18n


class Retranslator:
    """Holds (widget, key, setter) triples and re-applies translations on demand."""

    def __init__(self) -> None:
        self._items: list[tuple[QWidget, str, Callable[[str], None]]] = []

    def bind(
        self,
        widget: QWidget,
        key: str,
        setter: Callable[[str], None] | None = None,
    ) -> None:
        if setter is None:
            if isinstance(widget, QLabel):
                setter = widget.setText
            elif isinstance(widget, QPushButton):
                setter = widget.setText
            else:
                setter = lambda _t: None  # noqa: E731
        setter(i18n.t(key))
        self._items.append((widget, key, setter))

    def retranslate(self) -> None:
        for _w, key, setter in self._items:
            setter(i18n.t(key))
