import os
import threading

from PyQt6 import QtCore
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal
from musicdl import musicdl
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from pathlib import Path

from utils.convert import ConvertWorker
from utils.downloader import DownloadWorker

class Core(QObject):
    listChanged = pyqtSignal()
    searchError = pyqtSignal(str)
    data_ready = pyqtSignal(list)

    showProgressDialog = pyqtSignal()
    updateProgress = pyqtSignal(float)
    hideProgressDialog = pyqtSignal(str)

    index=0
    savePath=""

    def __init__(self):
        super().__init__()
        self.list=[]
        self.data_ready.connect(self.on_search_ok)

        self.downloadWorker = None
        self.convertWorker = None

    @QtCore.pyqtProperty(list, notify=listChanged) # type: ignore
    def searchResult(self):
        return self.list

    @pyqtSlot(str, str)
    def search(self, keyword, server):
        self.list=[]
        # 搜索
        thread = threading.Thread(target=self.do_search, args=(keyword, server))
        thread.start()

    # 测试代码
    def do_search_test(self, keyword, server):
        import time
        # time.sleep(2)
        local_list = [
            {
                "name": "test1",
                "artist": "test2",
                "url": "http://127.0.0.1:8000/saji-星のオーケストラ.flac",
                "cover": "http://127.0.0.1:8000/cover.jpg",
                "album": "test3"
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
        self.index = index

        ext = os.path.splitext(url.split('?')[0])[-1]
        if not ext: ext = ".mp3"

        default_name = f"{item['artist']}-{item['name']}{ext}"

        file_path, _ = QFileDialog.getSaveFileName(
            None,
            "选择保存位置",
            default_name,
            f"Files (*{ext});;All Files (*)"
        )

        # 取消=>不进行后续操作
        if not file_path:
            return

        self.savePath = file_path

        self.showProgressDialog.emit()

        self.downloadWorker = DownloadWorker(url, file_path)
        self.downloadWorker.progressChanged.connect(self.updateProgress.emit)
        self.downloadWorker.finished.connect(self.on_finished)
        self.downloadWorker.start()

    @pyqtSlot()
    def cancel_download(self):
        if self.downloadWorker:
            self.downloadWorker.cancel()

    def on_finished(self, success, message):
        if self.downloadWorker:
            self.downloadWorker.quit()
            self.downloadWorker.wait()
            self.downloadWorker = None

        if not success:
            self.hideProgressDialog.emit(message)
            return

        self.convertWorker = ConvertWorker(savePath=self.savePath, ls=self.list, index=self.index)
        self.convertWorker.finished.connect(self.on_convert_finished)
        self.convertWorker.start()

    def on_convert_finished(self, success, message):
        self.hideProgressDialog.emit(message)
        if success:
            if os.path.isfile(self.savePath) and not self.savePath.lower().endswith(".mp3"):
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Question)
                msg.setText("要删除原无损音频文件吗? ")
                msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
                msg.button(QMessageBox.StandardButton.Ok).setText("删除") # type: ignore
                msg.button(QMessageBox.StandardButton.Cancel).setText("保留") # type: ignore
                retval = msg.exec()
                if retval == QMessageBox.StandardButton.Ok:
                    os.remove(self.savePath)