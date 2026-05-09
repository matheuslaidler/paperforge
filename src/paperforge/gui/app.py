"""QApplication bootstrap + ``launch()`` entrypoint."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Force matplotlib to use the Qt backend BEFORE pyplot is imported anywhere.
# This must run before any ``import matplotlib.pyplot``.
os.environ.setdefault("MPLBACKEND", "QtAgg")
import matplotlib  # noqa: E402
matplotlib.use("QtAgg", force=True)

from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtGui import QGuiApplication, QIcon  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from paperforge import __version__
from paperforge.gui import theme as gui_theme  # noqa: E402
from paperforge.gui.main_window import MainWindow  # noqa: E402
from paperforge.utils.paths import package_root  # noqa: E402


def _setup_qt_platform_plugin_path() -> None:
    """When running as a PyInstaller bundle, point Qt at the bundled platforms dir."""
    if getattr(sys, "frozen", False):
        meipass = Path(getattr(sys, "_MEIPASS", "."))
        plugins = meipass / "PySide6" / "plugins" / "platforms"
        if plugins.is_dir():
            os.environ.setdefault(
                "QT_QPA_PLATFORM_PLUGIN_PATH", str(plugins)
            )


def _set_windows_app_id() -> None:
    """Set an AppUserModelID so the taskbar uses our icon instead of python.exe.

    Without this Windows groups the window under the host interpreter, which
    means the taskbar shows the generic Python icon instead of paper.ico.
    Must run BEFORE any QApplication or window is created.
    """
    if sys.platform != "win32":
        return
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "matheuslaidler.paperforge.app"
        )
    except Exception:
        pass


def _icon_path() -> Path:
    return package_root() / "paper.png"


def launch(argv: list[str] | None = None) -> int:
    """Initialize Qt and show the main window. Returns the process exit code."""
    _set_windows_app_id()
    _setup_qt_platform_plugin_path()

    if hasattr(Qt, "AA_EnableHighDpiScaling"):
        QGuiApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, "AA_UseHighDpiPixmaps"):
        QGuiApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication.instance() or QApplication(argv if argv is not None else sys.argv)
    app.setApplicationName("PaperForge")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("Matheus Laidler")
    icon_p = _icon_path()
    if icon_p.is_file():
        app.setWindowIcon(QIcon(str(icon_p)))
    gui_theme.apply(app)

    window = MainWindow()
    window.show()
    return app.exec()
