import json
import os
import sys
import threading

from PyQt6 import QtCore
from PyQt6.QtCore import QUrl, QObject, pyqtSlot, pyqtSignal
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtQml import QQmlApplicationEngine
from musicdl import musicdl
import webbrowser
from pathlib import Path

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
        self.data_ready.connect(self.on_search_ok)

    listChanged = pyqtSignal()
    searchError = pyqtSignal(str)
    data_ready = pyqtSignal(list)

    @QtCore.pyqtProperty(list, notify=listChanged)
    def searchResult(self):
        return self.list

    @pyqtSlot(str, str)
    def search(self, keyword, server):
        self.list=[]
        # 测试
        print(f"正在搜索: {keyword}\n使用服务: {server}")
        # 搜索
        thread = threading.Thread(target=self.do_search, args=(keyword, server))
        thread.start()

    # 测试代码
    def do_search_test(self, keyword, server):
        import time
        time.sleep(2)
        local_list = [
            {
                "name": "test1",
                "artist": "test2",
                "url": "https://music.163.com/song/media/outer/url?id=138654.mp3",
            },
            {
                "name": "test3",
                "artist": "test4",
                "url": "https://music.163.com/song/media/outer/url?id=138654.mp3",
            },
            {
                "name": "test5",
                "artist": "test6",
                "url": "https://music.163.com/song/media/outer/url?id=138654.mp3",
            },
        ]
        self.list = local_list
        self.listChanged.emit()

    def do_search(self, keyword, server):
        try:
            home_dir = Path.home()
            init_music_clients_cfg = dict()
            init_music_clients_cfg['NeteaseMusicClient'] = {'work_dir': f'{home_dir}/musicdl/Netease'}
            init_music_clients_cfg['QQMusicClient'] = {'work_dir': f'{home_dir}/musicdl/QQ'}
            init_music_clients_cfg['MiguMusicClient'] = {'work_dir': f'{home_dir}/musicdl/migu'}
            init_music_clients_cfg['KuwoMusicClient'] = {'work_dir': f'{home_dir}/musicdl/kuwo'}
            init_music_clients_cfg['QianqianMusicClient'] = {'work_dir': f'{home_dir}/musicdl/qianqian'}

            client = musicdl.MusicClient(
                music_sources=[server],
                init_music_clients_cfg=init_music_clients_cfg
            )
            search_results = client.search(keyword)
            local_list = []
            for item in search_results[server]:
                local_list.append({
                    "name": item['song_name'],
                    "artist": item['singers'],
                    "url": item['download_url'],
                })
            self.list = local_list
            self.listChanged.emit()
        except Exception as e:
            self.searchError.emit(str(e))

    @pyqtSlot(list)
    def on_search_ok(self, data):
        self.list = data
        self.listChanged.emit()

    @pyqtSlot(int)
    def download(self, index):
        webbrowser.open(self.list[index]['url'])


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