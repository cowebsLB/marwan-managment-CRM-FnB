# Building the Executable

## Prerequisites

1. Make sure you have Python 3.8+ installed
2. Install all dependencies including PyInstaller

## Installation Steps

### 1. Install Build Dependencies

```bash
pip install -r build_requirements.txt
```

Or install PyInstaller separately:
```bash
pip install pyinstaller
```

### 2. Build the Executable

**Option A: Using the build script (Recommended)**
```bash
python build_exe.py
```

**Option B: Using PyInstaller directly**
```bash
pyinstaller --name=MarwanManagementCRM --onefile --windowed --add-data="database;database" main.py
```

### 3. Find Your Executable

After building, the executable will be located in:
```
dist/MarwanManagementCRM.exe
```

## Build Options Explained

- `--onefile`: Creates a single executable file (easier to distribute)
- `--windowed`: Hides the console window (GUI application)
- `--add-data=database;database`: Includes the database directory in the executable
- `--name=MarwanManagementCRM`: Sets the name of the executable

## Troubleshooting

### If the executable doesn't run:

1. **Check for missing dependencies**: Run the executable from command line to see error messages:
   ```bash
   dist/MarwanManagementCRM.exe
   ```

2. **Database location**: The database will be created in the same directory as the executable on first run.

3. **Antivirus false positives**: Some antivirus software may flag PyInstaller executables. This is a known false positive.

### If you want to add an icon:

1. Create or obtain a `.ico` file
2. Add `--icon=path/to/icon.ico` to the build arguments
3. Or modify `build_exe.py` and change `'--icon=NONE'` to `'--icon=path/to/icon.ico'`

## File Size

The executable will be approximately 50-100 MB due to included Python interpreter and all dependencies. This is normal for PyInstaller builds.

## Distribution

You can distribute just the `.exe` file. Users don't need Python installed to run it.

