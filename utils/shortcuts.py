"""
Cross-platform Shortcut Creation Module
Handles creating desktop, start menu, and startup shortcuts for Windows, Linux, and Mac
"""
import os
import sys
import platform
import logging
from pathlib import Path
from typing import Tuple

from utils.config import get_base_path, get_log_path, setup_logging

logger = setup_logging()

SYSTEM = platform.system()


def get_executable_path() -> Path:
    """Get the path to the application executable"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return Path(sys.executable)
    else:
        # Running as script - return path to main.py
        base_path = Path(get_base_path())
        return base_path / "main.py"


def get_desktop_path() -> Path:
    """Get the desktop directory path"""
    if SYSTEM == "Windows":
        return Path(os.path.join(os.environ.get("USERPROFILE", ""), "Desktop"))
    elif SYSTEM == "Darwin":  # macOS
        return Path(os.path.join(os.path.expanduser("~"), "Desktop"))
    else:  # Linux
        return Path(os.path.join(os.path.expanduser("~"), "Desktop"))


def get_start_menu_path() -> Path:
    """Get the Start Menu programs directory path"""
    if SYSTEM == "Windows":
        appdata = os.environ.get("APPDATA", "")
        return Path(os.path.join(appdata, "Microsoft", "Windows", "Start Menu", "Programs"))
    elif SYSTEM == "Darwin":  # macOS
        return Path(os.path.join(os.path.expanduser("~"), "Applications"))
    else:  # Linux
        return Path(os.path.join(os.path.expanduser("~"), ".local", "share", "applications"))


def get_startup_path() -> Path:
    """Get the startup directory path"""
    if SYSTEM == "Windows":
        appdata = os.environ.get("APPDATA", "")
        return Path(os.path.join(appdata, "Microsoft", "Windows", "Start Menu", "Programs", "Startup"))
    elif SYSTEM == "Darwin":  # macOS
        # macOS uses LaunchAgents
        return Path(os.path.join(os.path.expanduser("~"), "Library", "LaunchAgents"))
    else:  # Linux
        return Path(os.path.join(os.path.expanduser("~"), ".config", "autostart"))


def create_windows_shortcut(target: Path, shortcut_path: Path, name: str = "Marwan Management CRM") -> Tuple[bool, str]:
    """Create a Windows shortcut (.lnk file)"""
    try:
        import win32com.client
        
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(shortcut_path))
        shortcut.Targetpath = str(target)
        shortcut.WorkingDirectory = str(target.parent)
        shortcut.Description = name
        shortcut.save()
        
        logger.info(f"Windows shortcut created: {shortcut_path}")
        return True, ""
    except ImportError:
        error_msg = "win32com module not available. Install pywin32: pip install pywin32"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Failed to create Windows shortcut: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def create_linux_desktop_file(target: Path, shortcut_path: Path, name: str = "Marwan Management CRM") -> Tuple[bool, str]:
    """Create a Linux .desktop file"""
    try:
        shortcut_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Determine if target is executable or Python script
        if target.suffix == ".py":
            exec_line = f"python3 {target}"
        else:
            exec_line = str(target)
        
        desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={name}
Comment=Food & Beverage Restaurant Management System
Exec={exec_line}
Icon=application-x-executable
Terminal=false
Categories=Office;Management;
"""
        
        with open(shortcut_path, 'w', encoding='utf-8') as f:
            f.write(desktop_content)
        
        # Make executable
        os.chmod(shortcut_path, 0o755)
        
        logger.info(f"Linux desktop file created: {shortcut_path}")
        return True, ""
    except Exception as e:
        error_msg = f"Failed to create Linux desktop file: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def create_macos_app_bundle(target: Path, shortcut_path: Path, name: str = "Marwan Management CRM") -> Tuple[bool, str]:
    """Create a macOS .app bundle or alias"""
    try:
        # For simplicity, create a shell script that launches the app
        # In a full implementation, you'd create a proper .app bundle
        shortcut_path.parent.mkdir(parents=True, exist_ok=True)
        
        if target.suffix == ".py":
            exec_line = f"python3 {target}"
        else:
            exec_line = str(target)
        
        script_content = f"""#!/bin/bash
cd "{target.parent}"
{exec_line}
"""
        
        with open(shortcut_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        os.chmod(shortcut_path, 0o755)
        
        logger.info(f"macOS launcher script created: {shortcut_path}")
        return True, ""
    except Exception as e:
        error_msg = f"Failed to create macOS launcher: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def create_desktop_shortcut() -> Tuple[bool, str]:
    """
    Create a desktop shortcut
    
    Returns:
        Tuple of (success: bool, error_message: str)
    """
    try:
        target = get_executable_path()
        desktop_path = get_desktop_path()
        
        if SYSTEM == "Windows":
            shortcut_path = desktop_path / "Marwan Management CRM.lnk"
            return create_windows_shortcut(target, shortcut_path)
        elif SYSTEM == "Darwin":  # macOS
            shortcut_path = desktop_path / "Marwan Management CRM.command"
            return create_macos_app_bundle(target, shortcut_path)
        else:  # Linux
            shortcut_path = desktop_path / "Marwan Management CRM.desktop"
            return create_linux_desktop_file(target, shortcut_path)
    except Exception as e:
        error_msg = f"Failed to create desktop shortcut: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def create_start_menu_shortcut() -> Tuple[bool, str]:
    """
    Create a Start Menu shortcut
    
    Returns:
        Tuple of (success: bool, error_message: str)
    """
    try:
        target = get_executable_path()
        start_menu_path = get_start_menu_path()
        
        if SYSTEM == "Windows":
            shortcut_path = start_menu_path / "Marwan Management CRM.lnk"
            return create_windows_shortcut(target, shortcut_path)
        elif SYSTEM == "Darwin":  # macOS
            # On macOS, Applications folder is used
            shortcut_path = start_menu_path / "Marwan Management CRM.command"
            return create_macos_app_bundle(target, shortcut_path)
        else:  # Linux
            shortcut_path = start_menu_path / "marwan-management-crm.desktop"
            return create_linux_desktop_file(target, shortcut_path)
    except Exception as e:
        error_msg = f"Failed to create start menu shortcut: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def add_to_startup() -> Tuple[bool, str]:
    """
    Add application to system startup
    
    Returns:
        Tuple of (success: bool, error_message: str)
    """
    try:
        target = get_executable_path()
        startup_path = get_startup_path()
        
        if SYSTEM == "Windows":
            shortcut_path = startup_path / "Marwan Management CRM.lnk"
            return create_windows_shortcut(target, shortcut_path)
        elif SYSTEM == "Darwin":  # macOS
            # macOS uses LaunchAgents plist files - simplified implementation
            plist_path = startup_path / "com.marwan.crm.plist"
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.marwan.crm</string>
    <key>ProgramArguments</key>
    <array>
        <string>{target}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
"""
            startup_path.mkdir(parents=True, exist_ok=True)
            with open(plist_path, 'w', encoding='utf-8') as f:
                f.write(plist_content)
            logger.info(f"macOS LaunchAgent created: {plist_path}")
            return True, ""
        else:  # Linux
            shortcut_path = startup_path / "marwan-management-crm.desktop"
            success, error = create_linux_desktop_file(target, shortcut_path)
            if success:
                # Add X-GNOME-Autostart-enabled=true to desktop file
                with open(shortcut_path, 'a', encoding='utf-8') as f:
                    f.write("X-GNOME-Autostart-enabled=true\n")
            return success, error
    except Exception as e:
        error_msg = f"Failed to add to startup: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def remove_from_startup() -> Tuple[bool, str]:
    """
    Remove application from system startup
    
    Returns:
        Tuple of (success: bool, error_message: str)
    """
    try:
        startup_path = get_startup_path()
        
        if SYSTEM == "Windows":
            shortcut_path = startup_path / "Marwan Management CRM.lnk"
        elif SYSTEM == "Darwin":
            plist_path = startup_path / "com.marwan.crm.plist"
            shortcut_path = plist_path
        else:  # Linux
            shortcut_path = startup_path / "marwan-management-crm.desktop"
        
        if shortcut_path.exists():
            shortcut_path.unlink()
            logger.info(f"Removed from startup: {shortcut_path}")
            return True, ""
        else:
            return True, "Startup entry not found"
    except Exception as e:
        error_msg = f"Failed to remove from startup: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def is_shortcut_supported() -> bool:
    """
    Check if shortcut creation is supported on this platform
    
    Returns:
        True if shortcuts are supported, False otherwise
    """
    if SYSTEM == "Windows":
        try:
            import win32com.client
            return True
        except ImportError:
            return False
    else:
        # Linux and macOS support is always available (uses file-based methods)
        return True

