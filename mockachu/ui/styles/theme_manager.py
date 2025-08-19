import qdarkstyle
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QPalette, QColor


class ThemeManager:
    DARK_THEME = "dark"

    def __init__(self, app=None):
        self.app = app or QApplication.instance()
        self.settings = QSettings("Mockachu", "Theme")
        self.current_theme = self.DARK_THEME

    def apply_theme(self, theme=None):
        try:
            stylesheet = qdarkstyle.load_stylesheet_pyqt6()

            # Remove cursor properties that cause "Unknown property cursor" warnings
            filtered_stylesheet = self._filter_cursor_properties(stylesheet)

            self.app.setStyleSheet(filtered_stylesheet)
            self.current_theme = self.DARK_THEME
            self.settings.setValue("theme", self.DARK_THEME)

        except Exception as e:
            print(f"Error applying theme: {e}")
            self._apply_fallback_theme()

    def _filter_cursor_properties(self, stylesheet):
        import re
        filtered = re.sub(r'cursor\s*:\s*[^;]*;', '', stylesheet)
        return filtered

    def _apply_fallback_theme(self):
        if not self.app:
            return

        palette = QPalette()

        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText,
                         QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase,
                         QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.ToolTipText,
                         QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText,
                         QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight,
                         QColor(42, 130, 218))
        palette.setColor(
            QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))

        self.app.setPalette(palette)

    def get_current_theme(self):
        return self.DARK_THEME

    def is_dark_theme(self):
        return True


_theme_manager = None


def get_theme_manager(app=None):
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager(app)
    return _theme_manager


def apply_theme(app=None):
    manager = get_theme_manager(app)
    manager.apply_theme()
