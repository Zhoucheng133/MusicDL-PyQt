import os
import sys
import threading

import requests
from PyQt6 import QtCore
from PyQt6.QtCore import QUrl, QObject, pyqtSlot, pyqtSignal, QThread
from PyQt6.QtGui import QIcon
from PyQt6.QtQml import QQmlApplicationEngine
from musicdl import musicdl
from PyQt6.QtWidgets import QFileDialog, QApplication
# import webbrowser
from pathlib import Path

os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"

def get_qml_path(file_name):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        # 开发环境路径
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, file_name)


class DownloadWorker(QThread):
    progressChanged = pyqtSignal(float)
    finished = pyqtSignal(bool, str)

    def __init__(self, url, dest):
        super().__init__()
        self.url = url
        self.dest = dest
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        try:
            response = requests.get(self.url, stream=True, timeout=15)
            total_size = int(response.headers.get('content-length', 0))

            downloaded_size = 0
            with open(self.dest, 'wb') as f:
                for data in response.iter_content(chunk_size=8192):
                    if self._is_cancelled:
                        self.finished.emit(False, "下载已取消")
                        return
                    f.write(data)
                    downloaded_size += len(data)
                    if total_size > 0:
                        self.progressChanged.emit(downloaded_size / total_size)

            self.finished.emit(True, "下载成功")
        except Exception as e:
            self.finished.emit(False, f"下载出错: {str(e)}")

class Core(QObject):
    listChanged = pyqtSignal()
    searchError = pyqtSignal(str)
    data_ready = pyqtSignal(list)

    showProgressDialog = pyqtSignal()
    updateProgress = pyqtSignal(float)
    hideProgressDialog = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.list=[]
        self.data_ready.connect(self.on_search_ok)

        self.worker = None

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
                    "cover": item['cover_url'],
                    "album": item['album'],
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
        item = self.list[index]
        url = item['url']

        ext = os.path.splitext(url.split('?')[0])[-1]
        if not ext: ext = ".mp3"  # 默认兜底

        default_name = f"{item['artist']}-{item['name']}{ext}"

        file_path, _ = QFileDialog.getSaveFileName(
            None,
            "选择保存位置",
            default_name,
            f"Files (*{ext});;All Files (*)"
        )

        # 如果用户点击了取消，则不进行后续操作
        if not file_path:
            return

        # 4. 显示进度条对话框
        self.showProgressDialog.emit()

        # 5. 启动线程下载
        self.worker = DownloadWorker(url, file_path)
        self.worker.progressChanged.connect(self.updateProgress.emit)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    @pyqtSlot()
    def cancel_download(self):
        if self.worker:
            self.worker.cancel()

    def on_finished(self, success, message):
        self.hideProgressDialog.emit(message)
        if self.worker:
            self.worker.quit()
            self.worker.wait()
            self.worker = None

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    if sys.platform == 'win32':
        app.setWindowIcon(QIcon(resource_path("assets/icon.ico")))

    core = Core()
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("core", core)

    target_qml = get_qml_path("main.qml")
    engine.load(QUrl.fromLocalFile(target_qml))

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())