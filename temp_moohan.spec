# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['temp_moohan.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\t2.jang\\Documents\\GitHub\\3rd_apps\\myenv\\Lib\\site-packages\\uiautomator2\\assets\\u2.jar', 'uiautomator2/assets')],
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
    a.binaries,
    a.datas,
    [],
    name='temp_moohan',
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
