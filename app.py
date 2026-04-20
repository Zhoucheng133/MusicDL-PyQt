import os
import sys

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QIcon
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtWidgets import QApplication

from utils.core import Core
from utils.theme import ThemeManager

os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"

def get_qml_path(directory, file_name):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS # type: ignore
    else:
        # 开发环境路径
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, directory, file_name)

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    if sys.platform == 'win32':
        app.setWindowIcon(QIcon(resource_path("assets/icon.ico")))

    core = Core()
    theme_manager = ThemeManager()
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("core", core) # type: ignore
    engine.rootContext().setContextProperty("themeManager", theme_manager) # type: ignore

    target_qml = get_qml_path("views", "main.qml")
    engine.load(QUrl.fromLocalFile(target_qml))

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())