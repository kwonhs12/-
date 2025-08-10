# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=['C:\\Users\\user\\Desktop\\1.2\\BOSS_announcer_downloads\\1.2'],
    binaries=[],
    datas=[
        ('images', 'images'),
        ('pa.ui', '.'),
        ('boss-tts-key.json', '.'),
        ('virtual.ui', '.'),
        ('main.ui', '.'),
        ('setting.ui', '.'),
        ('setting.json', '.'),
        ('speakmodule.py', '.'),
        ('getsheet.py', '.'),
        ('classify.py', '.')
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
