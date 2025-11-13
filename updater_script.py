"""
Standalone Updater Script
This script is launched by the main application to safely replace it with a new version.
It runs separately so the main app can close while the update is applied.
"""
import os
import sys
import time
import shutil
from pathlib import Path
import platform


def wait_for_process_exit(process_path: Path, max_wait: int = 30):
    """
    Wait for a process to exit before proceeding with update.
    
    Args:
        process_path: Path to the executable to wait for
        max_wait: Maximum seconds to wait
    """
    try:
        import psutil
        process_name = process_path.name
        
        for _ in range(max_wait):
            # Check if process is still running
            running = False
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
                        running = True
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if not running:
                return True
            
            time.sleep(1)
        
        return False
    except ImportError:
        # If psutil is not available, just wait a fixed time
        print("Warning: psutil not available, waiting fixed time...")
        time.sleep(5)
        return True


def replace_application(update_file: Path, app_path: Path) -> bool:
    """
    Replace the current application with the update file.
    
    Args:
        update_file: Path to the new version file
        app_path: Path to current application executable
    
    Returns:
        True if replacement successful
    """
    try:
        app_path = Path(app_path)
        update_file = Path(update_file)
        
        if not update_file.exists():
            print(f"Error: Update file not found: {update_file}")
            return False
        
        if not app_path.exists():
            print(f"Error: Application not found: {app_path}")
            return False
        
        # Wait for main application to close
        print("Waiting for application to close...")
        if not wait_for_process_exit(app_path):
            print("Warning: Application may still be running")
        
        # Create backup of current version
        backup_path = app_path.parent / f"{app_path.stem}_backup{app_path.suffix}"
        print(f"Creating backup: {backup_path}")
        
        try:
            if app_path.exists():
                shutil.copy2(app_path, backup_path)
        except Exception as e:
            print(f"Warning: Could not create backup: {e}")
        
        # Replace application
        print(f"Replacing application: {app_path}")
        
        if update_file.suffix == ".zip":
            # Extract zip file
            import zipfile
            with zipfile.ZipFile(update_file, 'r') as zip_ref:
                # Extract to app directory
                extract_dir = app_path.parent
                zip_ref.extractall(extract_dir)
            
            # Find the main executable in extracted files
            # This assumes the zip contains the executable with the same name
            extracted_exe = extract_dir / app_path.name
            if extracted_exe.exists() and extracted_exe != app_path:
                if app_path.exists():
                    app_path.unlink()
                extracted_exe.rename(app_path)
        else:
            # Direct file replacement
            if app_path.exists():
                app_path.unlink()
            shutil.copy2(update_file, app_path)
        
        # Make executable (Unix-like systems)
        if platform.system() != "Windows":
            os.chmod(app_path, 0o755)
        
        print("Update applied successfully!")
        
        # Clean up update file
        try:
            update_file.unlink()
        except Exception as e:
            print(f"Warning: Could not delete update file: {e}")
        
        # Restart application
        print("Restarting application...")
        if platform.system() == "Windows":
            import subprocess
            subprocess.Popen([str(app_path)], shell=True)
        else:
            os.execv(str(app_path), [str(app_path)])
        
        return True
        
    except Exception as e:
        print(f"Error during update: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point for updater script"""
    if len(sys.argv) < 3:
        print("Usage: updater_script.py <update_file> <app_path>")
        sys.exit(1)
    
    update_file = Path(sys.argv[1])
    app_path = Path(sys.argv[2])
    
    print("=" * 50)
    print("Application Updater")
    print("=" * 50)
    print(f"Update file: {update_file}")
    print(f"Application: {app_path}")
    print("=" * 50)
    
    if replace_application(update_file, app_path):
        print("Update completed successfully!")
        sys.exit(0)
    else:
        print("Update failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()

