import os
import sys
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtQml import QQmlApplicationEngine

os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"

app = QGuiApplication(sys.argv)
engine = QQmlApplicationEngine()
engine.load("main.qml")

if not engine.rootObjects():
    sys.exit(-1)
sys.exit(app.exec())