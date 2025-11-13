# -*- mode: python ; coding: utf-8 -*-
# Optimized PyInstaller spec for smaller executable size

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('updater_script.py', '.')],  # Embed updater_script.py as data file
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'matplotlib.backends.backend_qtagg',
        'pandas',
        'openpyxl',
        'requests',
        'psutil',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # GUI frameworks not used
        'tkinter',
        'tkinter.*',
        'PyQt5',
        'PyQt5.*',
        'PySide2',
        'PySide2.*',
        'PySide6',
        'PySide6.*',
        # Testing frameworks
        'unittest',
        'unittest.*',
        'test',
        'tests',
        'pytest',
        'doctest',
        'pydoc',
        # Development tools
        'setuptools',
        'distutils',
        'pip',
        'wheel',
        'pkg_resources',
        # Unused standard library modules
        'email',
        'email.*',
        'http',
        'http.*',
        'xmlrpc',
        'xmlrpc.*',
        'curses',
        'readline',
        # Optional dependencies that might be pulled in
        'IPython',
        'jupyter',
        'notebook',
        # Matplotlib backends we don't use
        'matplotlib.backends.backend_tkagg',
        'matplotlib.backends.backend_gtk3agg',
        'matplotlib.backends.backend_gtk4agg',
        'matplotlib.backends.backend_wxagg',
        'matplotlib.backends.backend_qt5agg',
        # Pandas optional dependencies
        'pandas.io.clipboard',
        'pandas.io.parsers.readers',
    ],
    noarchive=False,
    optimize=2,  # Python bytecode optimization
)
pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Marwan_CRM',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,  # Strip debug symbols to reduce size
    upx=True,  # Enable UPX compression (if available)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one
)
