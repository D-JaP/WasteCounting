# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['window_app.py'],
    pathex=[],
    binaries=[],
    datas=[('.\\config.json', '.\\')],
    hiddenimports=[],
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
    name='WasteCounter',
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
    Tree('.\\final', prefix='.\\final\\'),
    Tree('.\\static',prefix= '.\\static\\'),
    Tree('.\\templates',prefix= '.\\templates\\'),
    strip=False,
    upx=True,
    upx_exclude=[],
    name='window_app',
)
