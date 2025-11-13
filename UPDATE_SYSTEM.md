# Automatic Update System Documentation

## Overview

The automatic update system allows your PyQt6 application to check for updates from GitHub releases and automatically download and install them.

## Files

- **`utils/updater.py`**: Core update logic (checking, downloading, version comparison)
- **`utils/updater_ui.py`**: PyQt6 UI dialog for update notifications
- **`updater_script.py`**: Standalone script that safely replaces the application

## Setup Instructions

### 1. Configure GitHub Repository

Edit `utils/updater.py` and set your GitHub repository:

```python
GITHUB_REPO = "your-username/your-repository"  # Replace with your actual repo
```

### 2. Set Application Version

Update the version in `utils/updater.py`:

```python
APP_VERSION = "1.0.0"  # Update this when releasing new versions
```

### 3. Create GitHub Releases

When releasing a new version:

1. Create a new release on GitHub with a tag (e.g., `v1.0.1`)
2. Upload your `.exe` or `.zip` file as a release asset
3. The asset should be named with `.exe` or `.zip` extension

## How It Works

### Update Check Flow

1. User clicks "Check for Updates" button (or auto-check on startup)
2. Application queries GitHub API for latest release
3. Compares latest version tag with current `APP_VERSION`
4. If update available, shows dialog with release notes
5. User can choose to update now or later

### Update Process

1. Downloads the update file to temporary directory
2. Launches `updater_script.py` as separate process
3. Main application closes
4. Updater script waits for main app to fully exit
5. Creates backup of current version
6. Replaces application with new version
7. Restarts application

## Integration

The update system is already integrated into `main.py`:

- **Update Button**: Added to top bar (🔄 Check for Updates)
- **Auto-check on Startup**: Optional (commented out by default)

To enable auto-check on startup, uncomment this line in `main.py`:

```python
QTimer.singleShot(2000, self.check_for_updates)  # Check after 2 seconds
```

## Usage

### Manual Update Check

Click the "🔄 Check for Updates" button in the top bar.

### Programmatic Update Check

```python
from utils.updater_ui import show_update_dialog

# Show update dialog with auto-check
show_update_dialog(parent_window, auto_check=True)

# Or just show dialog (user clicks "Check for Updates")
show_update_dialog(parent_window, auto_check=False)
```

### Direct Update Check (No UI)

```python
from utils.updater import check_for_updates

update_available, latest_version, release_info = check_for_updates()
if update_available:
    print(f"Update available: {latest_version}")
```

## Version Format

Versions should follow semantic versioning:
- Format: `MAJOR.MINOR.PATCH` (e.g., `1.0.0`, `1.0.1`, `2.0.0`)
- GitHub tags can have `v` prefix (e.g., `v1.0.1`) - it will be stripped automatically

## PyInstaller Integration

When building with PyInstaller, include the updater files:

```bash
pyinstaller --onefile --noconsole --name "Marwan_CRM" \
    --add-data "updater_script.py;." \
    --add-data "utils/updater.py;utils" \
    --add-data "utils/updater_ui.py;utils" \
    main.py
```

Or use a `.spec` file for better control.

## Troubleshooting

### "GitHub repository not configured"

- Edit `utils/updater.py` and set `GITHUB_REPO` to your repository

### "Could not fetch release information"

- Check internet connection
- Verify repository name is correct
- Ensure repository has at least one release

### "Could not find update file"

- Ensure release has an asset with `.exe` or `.zip` extension
- Asset should be attached to the release, not just source code

### Update fails to apply

- Check file permissions
- Ensure application has write access to its directory
- On Windows, may need to run as administrator

## Security Considerations

- Updates are downloaded from GitHub releases (HTTPS)
- Consider adding signature verification for production use
- Always test updates in a safe environment first

## Customization

### Change Update Check URL

Modify `GITHUB_API_BASE` in `utils/updater.py` if using GitHub Enterprise.

### Custom Asset Selection

Modify `get_asset_download_url()` to select specific assets by name pattern.

### Custom Update Logic

Override functions in `utils/updater.py` to customize update behavior.

## Dependencies

- `requests` (optional, falls back to `urllib`)
- `psutil` (optional, for better process detection)
- `PyQt6` (for UI)

All are included in `requirements.txt`.

