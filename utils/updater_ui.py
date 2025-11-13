"""
Update Dialog UI for PyQt6
Provides user interface for checking and applying updates
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont
from pathlib import Path
import sys

from utils.updater import (
    check_for_updates, get_asset_download_url, prepare_update_files,
    run_updater_script, get_app_executable, get_app_directory,
    APP_VERSION, GITHUB_REPO
)


class UpdateCheckThread(QThread):
    """Background thread for checking updates"""
    update_available = pyqtSignal(bool, str, dict)  # update_available, version, release_info
    error_occurred = pyqtSignal(str)
    
    def __init__(self, repo: str = None):
        super().__init__()
        self.repo = repo or GITHUB_REPO
    
    def run(self):
        """Run update check in background"""
        try:
            update_available, latest_version, release_info = check_for_updates(self.repo)
            if release_info:
                self.update_available.emit(update_available, latest_version, release_info)
            else:
                self.error_occurred.emit("Could not fetch release information")
        except Exception as e:
            self.error_occurred.emit(f"Error checking for updates: {str(e)}")


class DownloadThread(QThread):
    """Background thread for downloading updates"""
    progress_updated = pyqtSignal(float)  # Progress percentage
    download_complete = pyqtSignal(Path)  # Path to downloaded file
    error_occurred = pyqtSignal(str)
    
    def __init__(self, download_url: str, temp_dir: Path):
        super().__init__()
        self.download_url = download_url
        self.temp_dir = temp_dir
    
    def run(self):
        """Download update file in background"""
        try:
            from utils.updater import download_file
            
            temp_dir = Path(self.temp_dir)
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            file_extension = ".exe" if self.download_url.endswith(".exe") else ".zip"
            download_path = temp_dir / f"update{file_extension}"
            
            def progress_callback(progress):
                self.progress_updated.emit(progress)
            
            if download_file(self.download_url, str(download_path), progress_callback):
                self.download_complete.emit(download_path)
            else:
                self.error_occurred.emit("Download failed")
        except Exception as e:
            self.error_occurred.emit(f"Error downloading update: {str(e)}")


class UpdateDialog(QDialog):
    """Dialog for checking and applying updates"""
    
    def __init__(self, parent=None, auto_check: bool = False):
        super().__init__(parent)
        self.setWindowTitle("Check for Updates")
        self.setModal(True)
        self.setFixedSize(500, 400)
        
        self.latest_version = None
        self.release_info = None
        self.downloaded_file = None
        
        self.init_ui()
        
        if auto_check:
            self.check_for_updates()
    
    def init_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Application Updates")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Current version label
        self.current_version_label = QLabel(f"Current Version: {APP_VERSION}")
        self.current_version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.current_version_label)
        
        # Status label
        self.status_label = QLabel("Click 'Check for Updates' to check for new versions.")
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Release notes (hidden initially)
        self.release_notes = QTextEdit()
        self.release_notes.setReadOnly(True)
        self.release_notes.setMaximumHeight(150)
        self.release_notes.hide()
        layout.addWidget(self.release_notes)
        
        # Progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.check_button = QPushButton("Check for Updates")
        self.check_button.clicked.connect(self.check_for_updates)
        button_layout.addWidget(self.check_button)
        
        self.update_button = QPushButton("Update Now")
        self.update_button.clicked.connect(self.start_update)
        self.update_button.setEnabled(False)
        self.update_button.hide()
        button_layout.addWidget(self.update_button)
        
        self.later_button = QPushButton("Update Later")
        self.later_button.clicked.connect(self.accept)
        self.later_button.hide()
        button_layout.addWidget(self.later_button)
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.reject)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
    def check_for_updates(self):
        """Start checking for updates in background thread"""
        self.check_button.setEnabled(False)
        self.status_label.setText("Checking for updates...")
        
        # Check if repo is configured
        if GITHUB_REPO == "username/repository":
            self.status_label.setText(
                "⚠️ GitHub repository not configured.\n"
                "Please set GITHUB_REPO in utils/updater.py"
            )
            self.check_button.setEnabled(True)
            return
        
        # Start background thread
        self.check_thread = UpdateCheckThread()
        self.check_thread.update_available.connect(self.on_update_check_complete)
        self.check_thread.error_occurred.connect(self.on_update_check_error)
        self.check_thread.start()
    
    def on_update_check_complete(self, update_available: bool, latest_version: str, release_info: dict):
        """Handle update check completion"""
        self.check_button.setEnabled(True)
        self.latest_version = latest_version
        self.release_info = release_info
        
        if update_available:
            self.status_label.setText(
                f"✅ New version available!\n"
                f"Latest version: {latest_version}\n"
                f"Current version: {APP_VERSION}"
            )
            
            # Show release notes if available
            body = release_info.get("body", "")
            if body:
                self.release_notes.setPlainText(body)
                self.release_notes.show()
            
            # Show update buttons
            self.update_button.show()
            self.update_button.setEnabled(True)
            self.later_button.show()
        else:
            self.status_label.setText(
                f"✅ You are using the latest version!\n"
                f"Version: {APP_VERSION}"
            )
    
    def on_update_check_error(self, error_message: str):
        """Handle update check error"""
        self.check_button.setEnabled(True)
        self.status_label.setText(f"❌ Error: {error_message}")
    
    def start_update(self):
        """Start downloading and applying update"""
        if not self.release_info:
            return
        
        # Get download URL
        download_url = get_asset_download_url(self.release_info)
        
        if not download_url:
            QMessageBox.warning(
                self,
                "Update Error",
                "Could not find update file in release assets.\n"
                "Please download manually from GitHub."
            )
            return
        
        # Confirm update
        reply = QMessageBox.question(
            self,
            "Confirm Update",
            f"Update to version {self.latest_version}?\n\n"
            "The application will restart after the update.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Disable buttons
        self.update_button.setEnabled(False)
        self.check_button.setEnabled(False)
        self.later_button.setEnabled(False)
        
        # Show progress bar
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        self.status_label.setText("Downloading update...")
        
        # Start download in background thread
        temp_dir = get_app_directory() / "temp_updates"
        self.download_thread = DownloadThread(download_url, temp_dir)
        self.download_thread.progress_updated.connect(self.on_download_progress)
        self.download_thread.download_complete.connect(self.on_download_complete)
        self.download_thread.error_occurred.connect(self.on_download_error)
        self.download_thread.start()
    
    def on_download_progress(self, progress: float):
        """Update progress bar"""
        self.progress_bar.setValue(int(progress))
    
    def on_download_complete(self, file_path: Path):
        """Handle download completion"""
        self.downloaded_file = file_path
        self.status_label.setText("Update downloaded. Applying update...")
        
        # Apply update
        app_path = get_app_executable()
        
        if run_updater_script(file_path, app_path):
            QMessageBox.information(
                self,
                "Update Complete",
                "Update will be applied when you restart the application.\n"
                "The application will now close."
            )
            self.accept()
            # Close main application
            if self.parent():
                self.parent().close()
        else:
            QMessageBox.warning(
                self,
                "Update Error",
                "Could not apply update automatically.\n"
                f"Please manually replace the application with:\n{file_path}"
            )
            self.update_button.setEnabled(True)
            self.check_button.setEnabled(True)
            self.later_button.setEnabled(True)
            self.progress_bar.hide()
    
    def on_download_error(self, error_message: str):
        """Handle download error"""
        self.status_label.setText(f"❌ Download error: {error_message}")
        self.update_button.setEnabled(True)
        self.check_button.setEnabled(True)
        self.later_button.setEnabled(True)
        self.progress_bar.hide()


def show_update_dialog(parent=None, auto_check: bool = False):
    """
    Show the update dialog.
    
    Args:
        parent: Parent widget
        auto_check: If True, automatically check for updates when dialog opens
    """
    dialog = UpdateDialog(parent, auto_check)
    dialog.exec()

