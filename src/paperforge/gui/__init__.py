"""PaperForge graphical user interface (PySide6).

The GUI is the default mode: running ``paperforge.exe`` without arguments
opens the main window. CLI subcommands keep working — they are dispatched
when ``sys.argv`` carries any positional argument.
"""

from paperforge.gui.app import launch

__all__ = ["launch"]
