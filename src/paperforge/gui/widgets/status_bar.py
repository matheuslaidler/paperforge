"""Status bar with language switcher and version label."""

from __future__ import annotations

from PySide6.QtWidgets import QComboBox, QLabel, QStatusBar, QWidget

from paperforge import __version__, i18n
from paperforge import config as config_mod
from paperforge.gui.signals import bus

LANGS = [("English", "en"), ("Português (BR)", "pt_br")]


class StatusBar(QStatusBar):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._task_label = QLabel(i18n.t("gui.status.ready"))
        self.addWidget(self._task_label, 1)

        self._lang_combo = QComboBox()
        for label, code in LANGS:
            self._lang_combo.addItem(label, code)
        current = config_mod.load_config().lang
        idx = next((i for i, (_, c) in enumerate(LANGS) if c == current), 0)
        self._lang_combo.setCurrentIndex(idx)
        self._lang_combo.currentIndexChanged.connect(self._on_lang_changed)
        self.addPermanentWidget(self._lang_combo)

        self._version_label = QLabel(f"v{__version__}")
        self.addPermanentWidget(self._version_label)

        bus.build_started.connect(lambda what: self._task_label.setText(
            i18n.t("gui.status.building", what=what)
        ))
        bus.build_finished.connect(lambda _: self._task_label.setText(
            i18n.t("gui.status.ready")
        ))

    # ------------------------------------------------------------------ #
    def retranslate(self) -> None:
        self._task_label.setText(i18n.t("gui.status.ready"))

    # ------------------------------------------------------------------ #
    def _on_lang_changed(self, idx: int) -> None:
        code = self._lang_combo.itemData(idx)
        if not code:
            return
        config_mod.update_field("lang", code)
        i18n.reload(code)
        bus.lang_changed.emit(code)
