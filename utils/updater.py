"""
Automatic Update System for PyQt6 Desktop Applications
Checks GitHub releases and handles updates
"""
import os
import sys
import json
import shutil
import subprocess
import platform
from pathlib import Path
from typing import Optional, Tuple, Dict
from urllib.request import urlopen, urlretrieve
from urllib.error import URLError

# Try to import requests, fallback to urllib
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


# Application version - Update this when releasing new versions
APP_VERSION = "1.0.0"

# GitHub repository configuration
# Format: "username/repository" (e.g., "username/marwan-crm")
GITHUB_REPO = "cowebsLB/marwan-managment-CRM-FnB"

# GitHub API base URL
GITHUB_API_BASE = "https://api.github.com/repos"


def get_latest_release_info(repo: str) -> Optional[Dict]:
    """
    Fetch the latest release information from GitHub API.
    
    Args:
        repo: GitHub repository in format "username/repository"
    
    Returns:
        Dictionary with release info or None if error
    """
    api_url = f"{GITHUB_API_BASE}/{repo}/releases/latest"
    
    try:
        if HAS_REQUESTS:
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            return response.json()
        else:
            with urlopen(api_url, timeout=10) as response:
                data = json.loads(response.read().decode())
                return data
    except Exception as e:
        print(f"Error fetching release info: {e}")
        return None


def compare_versions(current: str, latest: str) -> bool:
    """
    Compare version strings to determine if update is available.
    
    Args:
        current: Current application version (e.g., "1.0.0")
        latest: Latest release version (e.g., "1.0.1")
    
    Returns:
        True if latest version is newer than current
    """
    def version_tuple(version_str: str) -> Tuple[int, ...]:
        # Remove 'v' prefix if present and split by dots
        version_str = version_str.lstrip('v')
        parts = version_str.split('.')
        return tuple(int(part) for part in parts if part.isdigit())
    
    try:
        current_tuple = version_tuple(current)
        latest_tuple = version_tuple(latest)
        return latest_tuple > current_tuple
    except (ValueError, AttributeError):
        # If version comparison fails, assume update is available
        return latest != current


def get_asset_download_url(release_info: Dict, asset_extension: str = ".exe") -> Optional[str]:
    """
    Get the download URL for a specific asset from release.
    
    Args:
        release_info: Release information dictionary from GitHub API
        asset_extension: File extension to look for (default: ".exe")
    
    Returns:
        Download URL string or None if not found
    """
    assets = release_info.get("assets", [])
    
    # Look for asset with matching extension
    for asset in assets:
        if asset.get("name", "").endswith(asset_extension):
            return asset.get("browser_download_url")
    
    # If no .exe found, try .zip
    if asset_extension == ".exe":
        for asset in assets:
            if asset.get("name", "").endswith(".zip"):
                return asset.get("browser_download_url")
    
    return None


def download_file(url: str, destination: str, progress_callback=None) -> bool:
    """
    Download a file from URL to destination.
    
    Args:
        url: URL to download from
        destination: Local file path to save to
        progress_callback: Optional callback function for progress updates
    
    Returns:
        True if download successful, False otherwise
    """
    try:
        if HAS_REQUESTS:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(destination, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            progress_callback(progress)
            
            return True
        else:
            # Fallback to urllib
            urlretrieve(url, destination)
            return True
    except Exception as e:
        print(f"Error downloading file: {e}")
        return False


def get_app_directory() -> Path:
    """
    Get the directory where the application is located.
    Works with both development and PyInstaller builds.
    
    Returns:
        Path object pointing to application directory
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable (PyInstaller)
        return Path(sys.executable).parent
    else:
        # Running as script
        return Path(__file__).parent.parent


def get_app_executable() -> Path:
    """
    Get the path to the main application executable.
    
    Returns:
        Path object pointing to executable
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return Path(sys.executable)
    else:
        # Running as script - return main.py path
        return Path(__file__).parent.parent / "main.py"


def check_for_updates(repo: str = None) -> Tuple[bool, Optional[str], Optional[Dict]]:
    """
    Check if a new version is available on GitHub.
    
    Args:
        repo: GitHub repository (uses GITHUB_REPO if not provided)
    
    Returns:
        Tuple of (update_available, latest_version, release_info)
    """
    if repo is None:
        repo = GITHUB_REPO
    
    if repo == "username/repository":
        print("Warning: GitHub repository not configured. Please set GITHUB_REPO in updater.py")
        return False, None, None
    
    release_info = get_latest_release_info(repo)
    
    if not release_info:
        return False, None, None
    
    latest_version = release_info.get("tag_name", "").lstrip('v')
    update_available = compare_versions(APP_VERSION, latest_version)
    
    return update_available, latest_version, release_info


def prepare_update_files(download_url: str, temp_dir: Path) -> Optional[Path]:
    """
    Download update file to temporary directory.
    
    Args:
        download_url: URL to download update from
        temp_dir: Temporary directory to save file
    
    Returns:
        Path to downloaded file or None if failed
    """
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine file extension from URL
    file_extension = ".exe" if download_url.endswith(".exe") else ".zip"
    download_path = temp_dir / f"update{file_extension}"
    
    print(f"Downloading update to: {download_path}")
    
    if download_file(download_url, str(download_path)):
        return download_path
    
    return None


def restart_application():
    """
    Restart the current application.
    This function will be called after update is complete.
    """
    app_path = get_app_executable()
    
    if platform.system() == "Windows":
        # On Windows, use subprocess to start new instance
        subprocess.Popen([str(app_path)], shell=True)
    else:
        # On Unix-like systems
        os.execv(str(app_path), sys.argv)
    
    sys.exit(0)


def run_updater_script(update_file: Path, app_path: Path):
    """
    Launch the standalone updater script to handle the update process.
    This allows the main app to close while updater replaces it.
    
    Args:
        update_file: Path to downloaded update file
        app_path: Path to current application executable
    """
    updater_script = get_app_directory() / "updater_script.py"
    
    if not updater_script.exists():
        print("Warning: updater_script.py not found. Update cannot proceed automatically.")
        return False
    
    # Launch updater script with arguments
    if platform.system() == "Windows":
        subprocess.Popen([
            sys.executable,
            str(updater_script),
            str(update_file),
            str(app_path)
        ], creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        subprocess.Popen([
            sys.executable,
            str(updater_script),
            str(update_file),
            str(app_path)
        ])
    
    return True

