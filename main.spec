# -*- mode: python ; coding: utf-8 -*-

import os
import sys

def set_working_directory():
    # Set the working directory to the parent of the executable location
    os.chdir(os.path.dirname(sys.executable))

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('lib', 'lib'),
        ('tools', 'tools'),
        ('configs','configs'),
        ('tools', 'tools'),
        ('input', 'input'),
        ('output', 'output')
    ],
    hiddenimports=[
        'pkg_resources.py2_warn',
        'jaraco.text',
        'jaraco.context'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='main',
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
    name='main',
)

# Add this line to change the working directory
exe.run_before = set_working_directory