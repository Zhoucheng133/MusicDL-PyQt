import os
import sys

from PyQt6.QtCore import QUrl, QObject, pyqtSlot
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
    @pyqtSlot(str, str)
    def search(self, keyword, server):
        print(f"正在搜索: {keyword}\n使用服务: {server}")


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