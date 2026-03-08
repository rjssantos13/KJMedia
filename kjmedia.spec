# -*- mode: python ; coding: utf-8 -*-
import os

SPEC_DIR = os.path.dirname(os.path.abspath(SPEC))
from kivy.tools.packaging.pyinstaller_hooks import get_deps_all

block_cipher = None

deps = get_deps_all()

a = Analysis(
    ['main.py'],
    pathex=[SPEC_DIR],
    binaries=deps.get('binaries', []),
    datas=[
        (os.path.join(SPEC_DIR, 'assets'), 'assets'),
    ],
    hiddenimports=[
        'yt_dlp',
        'yt_dlp.downloader',
        'yt_dlp.extractor',
        'yt_dlp.postprocessor',
        'youtube_search',
        'certifi',
        'urllib3',
        'requests',
    ],
    hookspath=deps.get('hookspath', []),
    hooksconfig=deps.get('hooksconfig', {}),
    runtime_hooks=deps.get('runtime_hooks', []),
    excludes=deps.get('excludes', []),
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
    name='KJMedia',
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
)
