from PyQt6.QtCore import pyqtSignal, QObject, Qt
from PyQt6.QtGui import QGuiApplication
from PyQt6 import QtCore

class ThemeManager(QObject):
    themeChanged = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._style_hints = QGuiApplication.styleHints()
        self._style_hints.colorSchemeChanged.connect(self.on_theme_changed) # type: ignore

    def on_theme_changed(self):
        self.themeChanged.emit()

    @QtCore.pyqtProperty(bool, notify=themeChanged) # type: ignore
    def is_dark_mode(self):
        return self._style_hints.colorScheme() == Qt.ColorScheme.Dark # type: ignore