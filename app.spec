# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    datas=[
        ("main.qml", ".")
    ],
    pathex=[],
    binaries=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='app',
)
app_bundle = BUNDLE(
    coll,
    name='MusicDL.app',
    bundle_identifier='zhouc.musicdl_gui',
    info_plist={
        'CFBundleShortVersionString': '0.0.1',
        'NSHighResolutionCapable': 'True',
        'LSBackgroundOnly': 'False',
        'NSHumanReadableCopyright': 'Copyright © 2026 zhouc. All rights reserved.'
    },
)