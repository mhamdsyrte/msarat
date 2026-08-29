# -*- mode: python ; coding: utf-8 -*-
# سبك PyInstaller لبناء تطبيق سطح المكتب (وندوز/لينكس)
# طريقة البناء:
#   pip install -r requirements.txt --break-system-packages
#   pyinstaller masarat.spec
# الناتج يطلع بمجلد dist/

import sys
import os

block_cipher = None

APP_ROOT = os.path.dirname(os.path.abspath(SPEC))
PROJECT_ROOT = os.path.dirname(APP_ROOT)

a = Analysis(
    ['main.py'],
    pathex=[APP_ROOT, os.path.join(PROJECT_ROOT, 'app')],
    binaries=[],
    datas=[
        (os.path.join(PROJECT_ROOT, 'app', 'templates'), 'app/templates'),
        (os.path.join(PROJECT_ROOT, 'app', 'static'), 'app/static'),
    ],
    hiddenimports=['engineio.async_drivers.threading', 'app'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Masarat',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(APP_ROOT, 'icon.ico') if sys.platform == 'win32' else os.path.join(APP_ROOT, 'icon.png'),
)
