# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('/home/tejas/auto_typer/venv/lib/python3.12/site-packages/customtkinter', 'customtkinter'), ('config.py', '.'), ('engine', 'engine'), ('features', 'features'), ('ui', 'ui')],
    hiddenimports=['customtkinter', 'pynput', 'pynput.keyboard', 'pynput.keyboard._xorg', 'pynput.keyboard._win32', 'pynput.keyboard._darwin', 'pynput._util', 'pynput._util.xorg', 'pynput._util.win32', 'pynput._util.darwin', 'pyautogui', 'pyperclip', 'PIL', 'Pygments', 'pystray', 'config', 'engine', 'engine.typing_engine', 'features', 'features.profiles', 'features.snippets', 'features.history', 'features.scheduler', 'features.analytics', 'ui', 'ui.app', 'ui.overlay', 'ui.widgets', 'ui.dialogs', 'pynput.keyboard._xorg'],
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
    name='AutoTyperPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
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
    name='AutoTyperPro',
)
