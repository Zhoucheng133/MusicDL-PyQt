from PyQt6.QtCore import pyqtSignal, QThread
import requests

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