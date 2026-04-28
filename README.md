# MusicDL GUI

## 简介

<img src="assets/icon.png" width="100px">

![License](https://img.shields.io/badge/License-MIT-dark_green)

基于[musicdl](https://github.com/CharlesPikachu/musicdl)的GUI程序，使用PyQt6开发

这个仓库是基于PyQt的版本，另有基于Tauri的版本  
[Tauri ver.](https://github.com/Zhoucheng133/MusicDL-GUI) | ★ PyQt ver.

## 功能

✅ 自定义下载位置  
✅ 自动编码下载的歌曲 (包括封面图片和meta信息)*  
✅ 多个平台搜索  
✅ 深色模式

\* 自动编码时以`{艺人名}-{歌曲名}.mp3`命名，如果源文件是flac你可以选择保留源文件或只保留mp3，否则转码后则会替换原始文件

## 截图

<img src="demo/demo.png" width="500px">

## 打包

### Windows

```bash
pyinstaller --noconfirm --clean win.spec
```

### macOS

```bash
pyinstaller --noconfirm --clean mac.spec
```