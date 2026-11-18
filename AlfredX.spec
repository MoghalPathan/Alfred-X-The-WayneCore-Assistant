# -*- mode: python ; coding: utf-8 -*-
# AlfredX PyInstaller build spec (v2.2)
# Build with:  pyinstaller AlfredX.spec
# Output: dist/AlfredX/  -> zip this folder for distribution.

import os

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('data/mobile_ui.html', 'data'),
        ('data/naved_poetry.json', 'data'),
        ('data/knowledge', 'data/knowledge'),
        ('assets', 'assets'),
    ],
    hiddenimports=[
        'setup_wizard',
        'core.tts_engine',
        'core.speech_engine',
        'core.commands',
        'core.ai_engine',
        'core.memory',
        'core.chat_history',
        'core.embedded_server',
        'core.wake_word',
        'core.language_switcher',
        'core.global_hotkey',
        'core.music_service',
        'spotipy', 'spotipy.oauth2',
        'requests', 'wikipedia', 'psutil',
        'speech_recognition',
        'edge_tts',
        'pygame',
        'pywhatkit',
        'screen_brightness_control',
        'qrcode',
        'cv2',
        'PIL', 'PIL.Image', 'PIL.ImageGrab',
        'dotenv',
        'uvicorn.logging',
        'uvicorn.loops.auto',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan.on',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'scipy', 'pandas',
        'PyQt5.QtBluetooth', 'PyQt5.QtNetwork',
        'PyQt5.QtSql', 'PyQt5.QtTest', 'PyQt5.QtXml',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AlfredX',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,   # GUI app: no black terminal window
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='AlfredX',
)