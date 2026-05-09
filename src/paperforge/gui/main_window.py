"""Main application window: 3 tabs (PDF / Slides / Chart) + status bar + menu."""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QTabWidget,
    QWidget,
)

from paperforge import __version__, i18n
from paperforge.gui.signals import bus
from paperforge.gui.widgets.status_bar import StatusBar
from paperforge.utils.paths import package_root


class MainWindow(QMainWindow):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("PaperForge")
        self.setMinimumSize(QSize(1000, 700))

        icon_path = package_root() / "paper.png"
        if icon_path.is_file():
            self.setWindowIcon(QIcon(str(icon_path)))

        # ----- tabs -----
        self.tabs = QTabWidget(self)
        self.tabs.setDocumentMode(True)
        self.tabs.setMovable(False)
        self.setCentralWidget(self.tabs)
        self._populate_tabs()

        # ----- menu -----
        self._build_menu()

        # ----- status bar -----
        self.status = StatusBar(self)
        self.setStatusBar(self.status)

        # global signals -> retranslate UI when language changes
        bus.lang_changed.connect(self._retranslate)

    # ------------------------------------------------------------------ #
    def _populate_tabs(self) -> None:
        from paperforge.gui.pdf_tab import PdfTab
        from paperforge.gui.slides_tab import SlidesTab
        from paperforge.gui.chart_tab.chart_tab import ChartTab

        self._pdf_tab = PdfTab()
        self._slides_tab = SlidesTab()
        self._chart_tab = ChartTab()

        self.tabs.addTab(self._pdf_tab, i18n.t("gui.tab.pdf"))
        self.tabs.addTab(self._slides_tab, i18n.t("gui.tab.slides"))
        self.tabs.addTab(self._chart_tab, i18n.t("gui.tab.chart"))

    # ------------------------------------------------------------------ #
    def _build_menu(self) -> None:
        bar = self.menuBar()

        file_menu = QMenu(i18n.t("gui.menu.file"), self)
        bar.addMenu(file_menu)
        quit_action = QAction(i18n.t("gui.menu.quit"), self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        help_menu = QMenu(i18n.t("gui.menu.help"), self)
        bar.addMenu(help_menu)
        about_action = QAction(i18n.t("gui.menu.about"), self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

        self._file_menu = file_menu
        self._help_menu = help_menu
        self._about_action = about_action
        self._quit_action = quit_action

    # ------------------------------------------------------------------ #
    def _show_about(self) -> None:
        QMessageBox.about(
            self,
            i18n.t("gui.about.title"),
            i18n.t("gui.about.body", version=__version__),
        )

    # ------------------------------------------------------------------ #
    def _retranslate(self, _lang: str) -> None:
        self.tabs.setTabText(0, i18n.t("gui.tab.pdf"))
        self.tabs.setTabText(1, i18n.t("gui.tab.slides"))
        self.tabs.setTabText(2, i18n.t("gui.tab.chart"))
        self._file_menu.setTitle(i18n.t("gui.menu.file"))
        self._help_menu.setTitle(i18n.t("gui.menu.help"))
        self._quit_action.setText(i18n.t("gui.menu.quit"))
        self._about_action.setText(i18n.t("gui.menu.about"))
        for tab in (self._pdf_tab, self._slides_tab, self._chart_tab):
            if hasattr(tab, "retranslate"):
                tab.retranslate()
        self.status.retranslate()
