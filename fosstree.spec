# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for FossTree.

Build:
    pyinstaller fosstree.spec

Output:
    dist/FossTree/          (--onedir, default)
    dist/FossTree.exe       (--onefile, if toggled below)
"""

import sys
from pathlib import Path

# ── Toggle: set True for single-file exe (slower startup) ──
ONE_FILE = False

block_cipher = None

a = Analysis(
    ["fosstree/__main__.py"],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        # matplotlib Qt5 backend (imported dynamically in gui.py)
        "matplotlib.backends.backend_qt5agg",
        # Ensure matplotlib data is found
        "matplotlib",
        "matplotlib.pyplot",
        # PyQt5 plugins needed at runtime
        "PyQt5.sip",
    ],
    hookspath=[],
    hooksconfig={
        "matplotlib": {
            "backends": ["Qt5Agg"],
        },
    },
    runtime_hooks=[],
    excludes=[
        # Exclude unused heavy modules to reduce size
        "tkinter",
        "test",
        "xmlrpc",
        "pydoc",
        # Jupyter/IPython (dev-only)
        "IPython",
        "ipykernel",
        "jupyter",
        "notebook",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

if ONE_FILE:
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name="FossTree",
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=True if sys.platform == "linux" else False,
        disable_windowed_traceback=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
    )
else:
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name="FossTree",
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        # Linux: console=True so it works from terminal
        # Windows/macOS: console=False for double-click GUI launch
        console=True if sys.platform == "linux" else False,
        disable_windowed_traceback=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
    )
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name="FossTree",
    )

# macOS: create .app bundle
if sys.platform == "darwin" and not ONE_FILE:
    app = BUNDLE(
        coll,
        name="FossTree.app",
        icon=None,
        bundle_identifier="com.fosstree.app",
        info_plist={
            "CFBundleShortVersionString": "0.1.0",
            "CFBundleName": "FossTree",
            "NSHighResolutionCapable": True,
        },
    )
