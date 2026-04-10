import os
import sys
import threading

import requests
from PyQt6 import QtCore
from PyQt6.QtCore import QUrl, QObject, pyqtSlot, pyqtSignal, QThread, Qt
from PyQt6.QtGui import QIcon, QGuiApplication
from PyQt6.QtQml import QQmlApplicationEngine
from musicdl import musicdl
from PyQt6.QtWidgets import QFileDialog, QApplication, QMessageBox
from pathlib import Path

os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"

def get_qml_path(file_name):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS # type: ignore
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

class ConvertWorker(QThread):
    finished = pyqtSignal(bool, str)

    def __init__(self, savePath, ls, index):
        super().__init__()
        self.savePath = savePath
        self.index = index
        self.list = ls

    def get_ffmpeg_path(self):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS  # type: ignore
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))

        ffmpeg_bin="ffmpeg"

        if sys.platform == 'win32':
            ffmpeg_bin = os.path.join(base_path, "ffmpeg", "win", "ffmpeg.exe")
        elif sys.platform == 'darwin':
            ffmpeg_bin = os.path.join(base_path, "ffmpeg", "mac", "ffmpeg")

        return ffmpeg_bin

    def run(self):
        current_item = self.list[self.index]
        directory = os.path.dirname(self.savePath)

        new_name = f"{current_item['artist']}-{current_item['name']}.mp3"
        new_name = "".join([c for c in new_name if c not in r'\/:*?"<>|'])

        final_path = os.path.join(directory, new_name)
        temp_output = os.path.join(directory, "temp_processing.mp3")

        ffmpeg_exe = self.get_ffmpeg_path()

        cmd = [
            ffmpeg_exe, '-y',
            '-i', self.savePath,
            '-i', current_item['cover'],
            '-map', '0:a',
            '-map', '1:0',
            '-c:a', 'libmp3lame',
            '-b:a', '320k',
            '-metadata', f"title={current_item['name']}",
            '-metadata', f"artist={current_item['artist']}",
            '-metadata', f"album={current_item['album']}",
            '-id3v2_version', '3',
            '-metadata:s:v', 'title=Album cover',
            '-metadata:s:v', 'comment=Cover (front)',
            temp_output
        ]
        try:
            import subprocess
            startupinfo = None
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=startupinfo,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )

            if process.returncode == 0:
                if os.path.exists(final_path):
                    os.remove(final_path)
                os.rename(temp_output, final_path)
                self.finished.emit(True, f"转换成功: {final_path}")
            else:
                self.finished.emit(False, f"FFmpeg 错误: {process.stderr}")

        except Exception as e:
            if os.path.exists(temp_output):
                os.remove(temp_output)
            self.finished.emit(False, f"转换出错: {str(e)}")

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
                "cover": "http://127.0.0.1:8000/cover.png",
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
            if os.path.exists(self.savePath):
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Question)
                msg.setText("要删除原无损音频文件吗? ")
                msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
                msg.button(QMessageBox.StandardButton.Ok).setText("删除") # type: ignore
                msg.button(QMessageBox.StandardButton.Cancel).setText("保留") # type: ignore
                retval = msg.exec()
                if retval == QMessageBox.StandardButton.Ok:
                    os.remove(self.savePath)

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

    target_qml = get_qml_path("main.qml")
    engine.load(QUrl.fromLocalFile(target_qml))

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())