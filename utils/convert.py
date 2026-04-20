import os
import sys

from PyQt6.QtCore import pyqtSignal, QThread

class ConvertWorker(QThread):
    finished = pyqtSignal(bool, str)

    def __init__(self, savePath, ls, index):
        super().__init__()
        self.savePath = savePath
        self.index = index
        self.list = ls

    def get_ffmpeg_path(self):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS # type: ignore
        else:
            current_file_path = os.path.abspath(__file__)
            utils_path = os.path.dirname(current_file_path)
            base_path = os.path.dirname(utils_path) # 这里才是根目录

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