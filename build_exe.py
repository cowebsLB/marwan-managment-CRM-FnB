"""
Build script for creating executable
Run: python build_exe.py
"""
import PyInstaller.__main__
import os
import sys

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# PyInstaller arguments
args = [
    'main.py',
    '--name=MarwanManagementCRM',
    '--onefile',  # Create a single executable file
    '--windowed',  # No console window (GUI app)
    '--icon=NONE',  # You can add an icon file later if needed
    '--hidden-import=PyQt6.QtCore',
    '--hidden-import=PyQt6.QtGui',
    '--hidden-import=PyQt6.QtWidgets',
    '--hidden-import=matplotlib.backends.backend_qtagg',
    '--hidden-import=matplotlib.figure',
    '--hidden-import=matplotlib.backends.backend_agg',
    '--hidden-import=pandas',
    '--hidden-import=openpyxl',
    '--hidden-import=requests',
    '--hidden-import=psutil',
    '--collect-all=matplotlib',
    '--collect-all=PyQt6',
    '--add-data=LICENSE.txt;.',  # Include LICENSE.txt in the executable (Windows uses ; as separator)
    '--noconfirm',  # Overwrite output directory without asking
    '--clean',  # Clean PyInstaller cache before building
]

# Change to script directory
os.chdir(script_dir)

print("Building executable...")
print("This may take a few minutes...")
print()

try:
    PyInstaller.__main__.run(args)
    print()
    print("=" * 60)
    print("Build completed successfully!")
    print("=" * 60)
    print(f"Executable location: {os.path.join(script_dir, 'dist', 'MarwanManagementCRM.exe')}")
    print()
    print("Note: The first run may be slower as the database is initialized.")
except Exception as e:
    print(f"Error building executable: {e}")
    sys.exit(1)

