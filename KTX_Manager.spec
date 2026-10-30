# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('D:/Ứng dụng trí tuệ nhân tạo/Hệ thống quản lý KTX có tích hợp AI/code/KTX/css', 'css'), ('D:/Ứng dụng trí tuệ nhân tạo/Hệ thống quản lý KTX có tích hợp AI/code/KTX/js', 'js'), ('D:/Ứng dụng trí tuệ nhân tạo/Hệ thống quản lý KTX có tích hợp AI/code/KTX/sinhvien', 'sinhvien'), ('D:/Ứng dụng trí tuệ nhân tạo/Hệ thống quản lý KTX có tích hợp AI/code/KTX/quanly', 'quanly'), ('D:/Ứng dụng trí tuệ nhân tạo/Hệ thống quản lý KTX có tích hợp AI/code/KTX/ketoan', 'ketoan'), ('D:/Ứng dụng trí tuệ nhân tạo/Hệ thống quản lý KTX có tích hợp AI/code/KTX/index.html', '.'), ('D:/Ứng dụng trí tuệ nhân tạo/Hệ thống quản lý KTX có tích hợp AI/code/KTX/backend', 'backend')]
binaries = []
hiddenimports = ['sqlalchemy.sql.default_comparator']
tmp_ret = collect_all('fastapi')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('starlette')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('uvicorn')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pydantic')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pwdlib')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('jose')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['desktop_app.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5', 'PyQt6', 'PySide2', 'PySide6', 'matplotlib', 'scipy', 'pandas', 'IPython', 'notebook', 'jupyter', 'spyder', 'tkinter', '_tkinter', 'tornado', 'bokeh', 'statsmodels', 'sphinx', 'black', 'yapf', 'pytest'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='KTX_Manager',
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
    name='KTX_Manager',
)
