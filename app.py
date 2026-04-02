import os
import sys

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtQml import QQmlApplicationEngine

os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"

def get_qml_path(file_name):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        # 开发环境路径
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, file_name)

app = QGuiApplication(sys.argv)
engine = QQmlApplicationEngine()

target_qml = get_qml_path("main.qml")
engine.load(QUrl.fromLocalFile(target_qml))

if not engine.rootObjects():
    sys.exit(-1)
sys.exit(app.exec())