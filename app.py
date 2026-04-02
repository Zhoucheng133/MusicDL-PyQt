import os
import sys

from PyQt6 import QtCore
from PyQt6.QtCore import QUrl, QObject, pyqtSlot, pyqtSignal
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

class Core(QObject):
    def __init__(self):
        super().__init__()
        self.list=[]

    listChanged = pyqtSignal()

    @QtCore.pyqtProperty(list, notify=listChanged)
    def searchResult(self):
        return self.list

    @pyqtSlot(str, str)
    def search(self, keyword, server):
        print(f"正在搜索: {keyword}\n使用服务: {server}")
        self.list=["1", "2", "3"]
        self.listChanged.emit()


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)

    core = Core()
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("core", core)

    target_qml = get_qml_path("main.qml")
    engine.load(QUrl.fromLocalFile(target_qml))

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())