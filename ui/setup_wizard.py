"""
Setup Wizard for Marwan Management CRM
First-run setup wizard with multiple pages for configuration
"""
import os
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget,
    QTextEdit, QCheckBox, QLineEdit, QFileDialog, QProgressBar, QRadioButton,
    QButtonGroup, QMessageBox, QFrame, QScrollArea, QComboBox
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QKeyEvent

from utils.config import (
    get_base_path, get_config, save_setup_config, CONFIG_VERSION,
    get_default_config
)
from utils.shortcuts import (
    create_desktop_shortcut, create_start_menu_shortcut, add_to_startup,
    is_shortcut_supported, get_desktop_path, get_start_menu_path
)
# Database initialization is done via db_module in initialize_database method


class SetupWizard(QWidget):
    """Setup wizard dialog for first-run configuration"""
    
    finished = pyqtSignal(bool)  # Emitted when wizard completes (True) or is cancelled (False)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Marwan Management CRM - Setup Wizard")
        self.setFixedSize(700, 600)
        self.center_on_screen()
        
        # Load existing config or use defaults
        self.config = get_config()
        self.default_config = get_default_config()
        
        # Setup mode: 'quick' or 'custom'
        self.setup_mode = 'quick'
        
        # Wizard data
        self.wizard_data = {
            'installation_dir': self.config.get('installation_dir', get_base_path()),
            'database_path': self.config.get('database_path', os.path.join(get_base_path(), "restaurant_crm.db")),
            'use_default_db': True,
            'shortcuts': {
                'desktop': self.config.get('shortcuts', {}).get('desktop', True),
                'start_menu': self.config.get('shortcuts', {}).get('start_menu', True),
                'startup': self.config.get('shortcuts', {}).get('startup', False)
            },
            'restaurant_name': self.config.get('restaurant_name', ''),
            'currency': self.config.get('currency', 'USD'),
            'date_format': self.config.get('date_format', 'MM/DD/YYYY'),
            'license_accepted': False
        }
        
        self.current_page = 0
        self.init_ui()
        self.setup_animations()
    
    def center_on_screen(self):
        """Center the wizard on the screen"""
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def init_ui(self):
        """Initialize the wizard UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Content area with pages
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget, stretch=1)
        
        # Footer with navigation buttons (create before pages so buttons exist)
        footer = self.create_footer()
        layout.addWidget(footer)
        
        # Create pages (this calls update_navigation which needs the buttons)
        self.create_pages()
        
        # Apply styles
        self.apply_styles()
    
    def create_header(self):
        """Create the wizard header"""
        header = QFrame()
        header.setFixedHeight(80)
        header.setObjectName("wizardHeader")
        
        layout = QVBoxLayout(header)
        layout.setContentsMargins(30, 15, 30, 15)
        
        title = QLabel("Marwan Management CRM Setup")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        subtitle = QLabel("Welcome to the setup wizard")
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(subtitle)
        
        return header
    
    def create_footer(self):
        """Create the wizard footer with navigation buttons"""
        footer = QFrame()
        footer.setFixedHeight(60)
        footer.setObjectName("wizardFooter")
        
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(10)
        
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.cancel_wizard)
        layout.addWidget(self.btn_cancel)
        
        layout.addStretch()
        
        self.btn_back = QPushButton("← Back")
        self.btn_back.clicked.connect(self.go_back)
        layout.addWidget(self.btn_back)
        
        self.btn_skip = QPushButton("Skip")
        self.btn_skip.clicked.connect(self.skip_page)
        self.btn_skip.setVisible(False)
        layout.addWidget(self.btn_skip)
        
        self.btn_next = QPushButton("Next →")
        self.btn_next.clicked.connect(self.go_next)
        self.btn_next.setDefault(True)
        layout.addWidget(self.btn_next)
        
        return footer
    
    def create_pages(self):
        """Create all wizard pages"""
        self.page_welcome = self.create_welcome_page()
        self.page_license = self.create_license_page()
        self.page_installation = self.create_installation_page()
        self.page_database = self.create_database_page()
        self.page_shortcuts = self.create_shortcuts_page()
        self.page_config = self.create_config_page()
        self.page_progress = self.create_progress_page()
        self.page_completion = self.create_completion_page()
        
        self.stacked_widget.addWidget(self.page_welcome)
        self.stacked_widget.addWidget(self.page_license)
        self.stacked_widget.addWidget(self.page_installation)
        self.stacked_widget.addWidget(self.page_database)
        self.stacked_widget.addWidget(self.page_shortcuts)
        self.stacked_widget.addWidget(self.page_config)
        self.stacked_widget.addWidget(self.page_progress)
        self.stacked_widget.addWidget(self.page_completion)
        
        self.update_navigation()
    
    def create_welcome_page(self):
        """Create welcome page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Welcome message
        welcome_label = QLabel("Welcome to Marwan Management CRM")
        welcome_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(welcome_label)
        
        desc_label = QLabel(
            "This wizard will help you configure the application for first use.\n\n"
            "You can choose between Quick Setup (recommended) or Custom Setup."
        )
        desc_label.setFont(QFont("Segoe UI", 11))
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #34495e; margin: 20px 0;")
        layout.addWidget(desc_label)
        
        layout.addStretch()
        
        # Setup mode selection
        mode_group = QButtonGroup()
        
        self.radio_quick = QRadioButton("Quick Setup (Recommended)")
        self.radio_quick.setChecked(True)
        self.radio_quick.setFont(QFont("Segoe UI", 11))
        self.radio_quick.toggled.connect(lambda: self.set_setup_mode('quick'))
        mode_group.addButton(self.radio_quick)
        layout.addWidget(self.radio_quick)
        
        quick_desc = QLabel("Uses default settings. Fast and easy.")
        quick_desc.setFont(QFont("Segoe UI", 9))
        quick_desc.setStyleSheet("color: #7f8c8d; margin-left: 25px; margin-bottom: 15px;")
        layout.addWidget(quick_desc)
        
        self.radio_custom = QRadioButton("Custom Setup")
        self.radio_custom.setFont(QFont("Segoe UI", 11))
        self.radio_custom.toggled.connect(lambda: self.set_setup_mode('custom'))
        mode_group.addButton(self.radio_custom)
        layout.addWidget(self.radio_custom)
        
        custom_desc = QLabel("Choose installation directory, database location, and more.")
        custom_desc.setFont(QFont("Segoe UI", 9))
        custom_desc.setStyleSheet("color: #7f8c8d; margin-left: 25px;")
        layout.addWidget(custom_desc)
        
        layout.addStretch()
        
        # Version info
        version_label = QLabel(f"Version {CONFIG_VERSION}")
        version_label.setFont(QFont("Segoe UI", 9))
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #95a5a6;")
        layout.addWidget(version_label)
        
        return page
    
    def create_license_page(self):
        """Create license agreement page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        title = QLabel("License Agreement")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        # License text
        license_text = QTextEdit()
        license_text.setReadOnly(True)
        
        # Try multiple paths to find LICENSE.txt
        license_path = None
        possible_paths = []
        
        # When running as executable, check PyInstaller temp directory
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller onefile mode - check temp directory
                possible_paths.append(Path(sys._MEIPASS) / "LICENSE.txt")
            # Also check executable directory
            possible_paths.append(Path(sys.executable).parent / "LICENSE.txt")
            possible_paths.append(Path(get_base_path()) / "LICENSE.txt")
        else:
            # Running as script
            possible_paths.append(Path(__file__).parent.parent / "LICENSE.txt")
            possible_paths.append(Path(get_base_path()) / "LICENSE.txt")
        
        for path in possible_paths:
            if path and path.exists():
                license_path = path
                break
        
        if license_path and license_path.exists():
            try:
                with open(license_path, 'r', encoding='utf-8') as f:
                    license_text.setPlainText(f.read())
            except Exception as e:
                license_text.setPlainText(f"Error reading license file: {str(e)}")
        else:
            # Fallback: Show basic license info
            license_text.setPlainText(
                "MARWAN MANAGEMENT CRM - FOOD & BEVERAGE MANAGEMENT SYSTEM\n"
                "END USER LICENSE AGREEMENT\n\n"
                "Copyright (c) 2025 Marwan Management CRM made by cowebs.lb\n\n"
                "This software is provided for use in managing restaurant and food & beverage operations.\n\n"
                "By installing or using this Software, you acknowledge that you have read this Agreement, "
                "understand it, and agree to be bound by its terms and conditions.\n\n"
                "For the full license text, please refer to the LICENSE.txt file in the application directory."
            )
        license_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e1e8ed;
                border-radius: 4px;
                padding: 10px;
                background-color: #ffffff;
            }
        """)
        layout.addWidget(license_text, stretch=1)
        
        # Agreement checkbox
        self.checkbox_license = QCheckBox("I agree to the terms and conditions")
        self.checkbox_license.setFont(QFont("Segoe UI", 10))
        self.checkbox_license.stateChanged.connect(self.update_navigation)
        layout.addWidget(self.checkbox_license)
        
        return page
    
    def create_installation_page(self):
        """Create installation directory selection page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        title = QLabel("Installation Directory")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        desc = QLabel("Choose where to install the application files:")
        desc.setFont(QFont("Segoe UI", 10))
        desc.setStyleSheet("color: #34495e; margin-bottom: 10px;")
        layout.addWidget(desc)
        
        # Advanced options checkbox
        self.checkbox_advanced_install = QCheckBox("Show advanced options")
        self.checkbox_advanced_install.setFont(QFont("Segoe UI", 10))
        self.checkbox_advanced_install.toggled.connect(self.toggle_advanced_install)
        layout.addWidget(self.checkbox_advanced_install)
        
        # Directory selection (hidden by default in quick mode)
        self.install_dir_widget = QWidget()
        install_layout = QVBoxLayout(self.install_dir_widget)
        install_layout.setContentsMargins(0, 10, 0, 0)
        
        dir_layout = QHBoxLayout()
        self.install_dir_input = QLineEdit()
        self.install_dir_input.setText(self.wizard_data['installation_dir'])
        self.install_dir_input.setReadOnly(True)
        self.install_dir_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #e1e8ed;
                border-radius: 4px;
                padding: 8px;
                background-color: #f8f9fa;
            }
        """)
        dir_layout.addWidget(self.install_dir_input)
        
        btn_browse = QPushButton("Browse...")
        btn_browse.clicked.connect(self.browse_installation_dir)
        dir_layout.addWidget(btn_browse)
        
        btn_default = QPushButton("Use Default")
        btn_default.clicked.connect(self.use_default_install_dir)
        dir_layout.addWidget(btn_default)
        
        install_layout.addLayout(dir_layout)
        self.install_dir_widget.setVisible(False)
        layout.addWidget(self.install_dir_widget)
        
        layout.addStretch()
        
        return page
    
    def create_database_page(self):
        """Create database location selection page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        title = QLabel("Database Location")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        desc = QLabel("Choose where to store the database file:")
        desc.setFont(QFont("Segoe UI", 10))
        desc.setStyleSheet("color: #34495e; margin-bottom: 10px;")
        layout.addWidget(desc)
        
        # Database location options
        self.db_radio_default = QRadioButton("Use default location (recommended)")
        self.db_radio_default.setChecked(True)
        self.db_radio_default.setFont(QFont("Segoe UI", 10))
        self.db_radio_default.toggled.connect(self.update_db_selection)
        layout.addWidget(self.db_radio_default)
        
        default_path_label = QLabel(f"Default: {os.path.join(get_base_path(), 'restaurant_crm.db')}")
        default_path_label.setFont(QFont("Segoe UI", 9))
        default_path_label.setStyleSheet("color: #7f8c8d; margin-left: 25px; margin-bottom: 15px;")
        layout.addWidget(default_path_label)
        
        self.db_radio_custom = QRadioButton("Choose custom location")
        self.db_radio_custom.setFont(QFont("Segoe UI", 10))
        self.db_radio_custom.toggled.connect(self.update_db_selection)
        layout.addWidget(self.db_radio_custom)
        
        # Custom path selection (hidden by default)
        self.db_custom_widget = QWidget()
        db_layout = QHBoxLayout(self.db_custom_widget)
        db_layout.setContentsMargins(25, 0, 0, 0)
        
        self.db_path_input = QLineEdit()
        self.db_path_input.setText(self.wizard_data['database_path'])
        self.db_path_input.setReadOnly(True)
        self.db_path_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #e1e8ed;
                border-radius: 4px;
                padding: 8px;
                background-color: #f8f9fa;
            }
        """)
        db_layout.addWidget(self.db_path_input)
        
        btn_browse_db = QPushButton("Browse...")
        btn_browse_db.clicked.connect(self.browse_database_path)
        db_layout.addWidget(btn_browse_db)
        
        self.db_custom_widget.setVisible(False)
        layout.addWidget(self.db_custom_widget)
        
        layout.addStretch()
        
        return page
    
    def create_shortcuts_page(self):
        """Create shortcuts selection page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        title = QLabel("Shortcuts")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        if not is_shortcut_supported():
            not_supported = QLabel("Shortcut creation is not supported on this platform.")
            not_supported.setStyleSheet("color: #e74c3c;")
            layout.addWidget(not_supported)
            layout.addStretch()
            return page
        
        desc = QLabel("Choose which shortcuts to create:")
        desc.setFont(QFont("Segoe UI", 10))
        desc.setStyleSheet("color: #34495e; margin-bottom: 10px;")
        layout.addWidget(desc)
        
        # Shortcut checkboxes
        self.checkbox_desktop = QCheckBox("Create desktop shortcut")
        self.checkbox_desktop.setChecked(self.wizard_data['shortcuts']['desktop'])
        self.checkbox_desktop.setFont(QFont("Segoe UI", 10))
        layout.addWidget(self.checkbox_desktop)
        
        self.checkbox_start_menu = QCheckBox("Create Start Menu shortcut")
        self.checkbox_start_menu.setChecked(self.wizard_data['shortcuts']['start_menu'])
        self.checkbox_start_menu.setFont(QFont("Segoe UI", 10))
        layout.addWidget(self.checkbox_start_menu)
        
        # Advanced options
        self.checkbox_advanced_shortcuts = QCheckBox("Show advanced options")
        self.checkbox_advanced_shortcuts.setFont(QFont("Segoe UI", 10))
        self.checkbox_advanced_shortcuts.toggled.connect(self.toggle_advanced_shortcuts)
        layout.addWidget(self.checkbox_advanced_shortcuts)
        
        self.checkbox_startup = QCheckBox("Add to system startup (launch on login)")
        self.checkbox_startup.setChecked(self.wizard_data['shortcuts']['startup'])
        self.checkbox_startup.setFont(QFont("Segoe UI", 10))
        self.checkbox_startup.setVisible(False)
        layout.addWidget(self.checkbox_startup)
        
        layout.addStretch()
        
        return page
    
    def create_config_page(self):
        """Create initial configuration page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        title = QLabel("Initial Configuration")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        # Restaurant name
        name_label = QLabel("Restaurant/Business Name *")
        name_label.setFont(QFont("Segoe UI", 10))
        layout.addWidget(name_label)
        
        self.restaurant_name_input = QLineEdit()
        self.restaurant_name_input.setText(self.wizard_data['restaurant_name'])
        self.restaurant_name_input.setPlaceholderText("Enter your restaurant or business name")
        self.restaurant_name_input.textChanged.connect(self.update_navigation)
        self.restaurant_name_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #e1e8ed;
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.restaurant_name_input)
        
        layout.addSpacing(15)
        
        # Currency
        currency_label = QLabel("Currency")
        currency_label.setFont(QFont("Segoe UI", 10))
        layout.addWidget(currency_label)
        
        self.currency_combo = QComboBox()
        self.currency_combo.addItems(["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "INR", "BRL"])
        self.currency_combo.setCurrentText(self.wizard_data['currency'])
        layout.addWidget(self.currency_combo)
        
        layout.addSpacing(15)
        
        # Date format
        date_label = QLabel("Date Format")
        date_label.setFont(QFont("Segoe UI", 10))
        layout.addWidget(date_label)
        
        self.date_format_combo = QComboBox()
        self.date_format_combo.addItems(["MM/DD/YYYY", "DD/MM/YYYY", "YYYY-MM-DD"])
        self.date_format_combo.setCurrentText(self.wizard_data['date_format'])
        layout.addWidget(self.date_format_combo)
        
        layout.addStretch()
        
        return page
    
    def create_progress_page(self):
        """Create progress/installation page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        title = QLabel("Installing...")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #e1e8ed;
                border-radius: 8px;
                text-align: center;
                background-color: #f8f9fa;
                height: 30px;
                font-size: 12px;
                font-weight: 600;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.progress_status = QLabel("Preparing installation...")
        self.progress_status.setFont(QFont("Segoe UI", 10))
        self.progress_status.setStyleSheet("color: #34495e; min-height: 30px;")
        layout.addWidget(self.progress_status)
        
        # Error message area (hidden by default)
        self.error_widget = QWidget()
        error_layout = QVBoxLayout(self.error_widget)
        error_layout.setContentsMargins(0, 20, 0, 0)
        
        self.error_label = QLabel()
        self.error_label.setWordWrap(True)
        self.error_label.setStyleSheet("color: #e74c3c; padding: 10px; background-color: #fee; border: 1px solid #e74c3c; border-radius: 4px;")
        self.error_label.setVisible(False)
        error_layout.addWidget(self.error_label)
        
        self.btn_retry = QPushButton("Retry")
        self.btn_retry.clicked.connect(self.retry_installation)
        self.btn_retry.setVisible(False)
        error_layout.addWidget(self.btn_retry)
        
        self.error_widget.setVisible(False)
        layout.addWidget(self.error_widget)
        
        layout.addStretch()
        
        return page
    
    def create_completion_page(self):
        """Create completion page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Success icon/message
        success_label = QLabel("✓ Setup Complete!")
        success_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        success_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        success_label.setStyleSheet("color: #27ae60; margin: 20px 0;")
        layout.addWidget(success_label)
        
        desc = QLabel("Marwan Management CRM has been successfully configured and is ready to use.")
        desc.setFont(QFont("Segoe UI", 11))
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #34495e; margin-bottom: 30px;")
        layout.addWidget(desc)
        
        # Configuration summary
        summary_frame = QFrame()
        summary_frame.setFrameShape(QFrame.Shape.Box)
        summary_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #e1e8ed;
                border-radius: 4px;
                background-color: #f8f9fa;
                padding: 15px;
            }
        """)
        summary_layout = QVBoxLayout(summary_frame)
        
        summary_title = QLabel("Configuration Summary:")
        summary_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        summary_layout.addWidget(summary_title)
        
        self.summary_label = QLabel()
        self.summary_label.setFont(QFont("Segoe UI", 9))
        self.summary_label.setStyleSheet("color: #34495e;")
        summary_layout.addWidget(self.summary_label)
        
        layout.addWidget(summary_frame)
        
        layout.addStretch()
        
        # Launch checkbox
        self.checkbox_launch = QCheckBox("Launch Marwan Management CRM now")
        self.checkbox_launch.setChecked(True)
        self.checkbox_launch.setFont(QFont("Segoe UI", 10))
        layout.addWidget(self.checkbox_launch)
        
        return page
    
    def set_setup_mode(self, mode: str):
        """Set setup mode (quick or custom)"""
        self.setup_mode = mode
        self.update_navigation()
    
    def toggle_advanced_install(self, checked: bool):
        """Toggle advanced installation options"""
        self.install_dir_widget.setVisible(checked)
    
    def toggle_advanced_shortcuts(self, checked: bool):
        """Toggle advanced shortcut options"""
        self.checkbox_startup.setVisible(checked)
    
    def browse_installation_dir(self):
        """Browse for installation directory"""
        current_dir = self.install_dir_input.text()
        directory = QFileDialog.getExistingDirectory(self, "Select Installation Directory", current_dir)
        if directory:
            self.install_dir_input.setText(directory)
            self.wizard_data['installation_dir'] = directory
    
    def use_default_install_dir(self):
        """Use default installation directory"""
        default_dir = get_base_path()
        self.install_dir_input.setText(default_dir)
        self.wizard_data['installation_dir'] = default_dir
    
    def update_db_selection(self):
        """Update database selection based on radio buttons"""
        if self.db_radio_default.isChecked():
            self.wizard_data['use_default_db'] = True
            self.wizard_data['database_path'] = os.path.join(get_base_path(), "restaurant_crm.db")
            self.db_custom_widget.setVisible(False)
        else:
            self.wizard_data['use_default_db'] = False
            self.db_custom_widget.setVisible(True)
    
    def browse_database_path(self):
        """Browse for database file location"""
        current_path = self.db_path_input.text()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Select Database Location", current_path, "Database Files (*.db);;All Files (*)"
        )
        if file_path:
            if not file_path.endswith('.db'):
                file_path += '.db'
            self.db_path_input.setText(file_path)
            self.wizard_data['database_path'] = file_path
    
    def update_navigation(self):
        """Update navigation buttons based on current page"""
        total_pages = self.stacked_widget.count()
        is_completion_page = self.current_page == total_pages - 1
        is_progress_page = self.current_page == total_pages - 2
        
        # Back button - hide on completion page
        if is_completion_page:
            self.btn_back.setVisible(False)
        else:
            self.btn_back.setVisible(True)
            self.btn_back.setEnabled(self.current_page > 0)
        
        # Skip button (only on optional pages in quick mode)
        skip_pages = [2, 3, 4]  # Installation, Database, Shortcuts
        self.btn_skip.setVisible(
            not is_completion_page and
            not is_progress_page and
            self.setup_mode == 'quick' and 
            self.current_page in skip_pages
        )
        
        # Next button
        can_advance = True
        if self.current_page == 1:  # License page
            can_advance = self.checkbox_license.isChecked()
        elif self.current_page == 5:  # Config page
            can_advance = bool(self.restaurant_name_input.text().strip())
        
        # Button visibility and text
        if is_completion_page:
            # Completion page: Show Finish button, hide Back
            self.btn_next.setVisible(True)
            self.btn_next.setText("Finish")
            self.btn_next.setEnabled(True)
        elif is_progress_page:
            # Progress page: Hide Next button (installation in progress)
            self.btn_next.setVisible(False)
        else:
            # Other pages: Show Next button
            self.btn_next.setVisible(True)
            self.btn_next.setText("Next →")
            self.btn_next.setEnabled(can_advance)
    
    def go_back(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.stacked_widget.setCurrentIndex(self.current_page)
            self.update_navigation()
    
    def skip_page(self):
        """Skip current page (use defaults)"""
        if self.current_page < self.stacked_widget.count() - 2:
            self.current_page += 1
            self.stacked_widget.setCurrentIndex(self.current_page)
            self.update_navigation()
    
    def go_next(self):
        """Go to next page or finish"""
        if self.current_page == self.stacked_widget.count() - 1:  # Completion page
            self.finish_wizard()
        elif self.current_page == self.stacked_widget.count() - 3:  # Config page, next is progress
            self.collect_wizard_data()
            self.current_page += 1
            self.stacked_widget.setCurrentIndex(self.current_page)
            self.update_navigation()
            self.run_installation()
        else:
            self.current_page += 1
            self.stacked_widget.setCurrentIndex(self.current_page)
            self.update_navigation()
    
    def collect_wizard_data(self):
        """Collect data from wizard pages"""
        # Installation directory
        if self.setup_mode == 'custom' and self.checkbox_advanced_install.isChecked():
            self.wizard_data['installation_dir'] = self.install_dir_input.text()
        
        # Database path
        if not self.wizard_data['use_default_db']:
            self.wizard_data['database_path'] = self.db_path_input.text()
        
        # Shortcuts
        if is_shortcut_supported():
            self.wizard_data['shortcuts']['desktop'] = self.checkbox_desktop.isChecked()
            self.wizard_data['shortcuts']['start_menu'] = self.checkbox_start_menu.isChecked()
            self.wizard_data['shortcuts']['startup'] = self.checkbox_startup.isChecked()
        
        # Configuration
        self.wizard_data['restaurant_name'] = self.restaurant_name_input.text().strip()
        self.wizard_data['currency'] = self.currency_combo.currentText()
        self.wizard_data['date_format'] = self.date_format_combo.currentText()
        self.wizard_data['license_accepted'] = self.checkbox_license.isChecked()
    
    def run_installation(self):
        """Run the installation process"""
        self.error_widget.setVisible(False)
        self.btn_retry.setVisible(False)
        self.progress_bar.setValue(0)
        
        # Step 1: Create directories
        self.update_progress(10, "Creating directories...")
        QTimer.singleShot(100, lambda: self.create_directories())
    
    def create_directories(self):
        """Create necessary directories"""
        try:
            install_dir = Path(self.wizard_data['installation_dir'])
            install_dir.mkdir(parents=True, exist_ok=True)
            
            db_path = Path(self.wizard_data['database_path'])
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.update_progress(20, "Directories created successfully")
            QTimer.singleShot(100, lambda: self.initialize_database())
        except Exception as e:
            self.show_error(f"Failed to create directories: {str(e)}")
    
    def initialize_database(self):
        """Initialize database"""
        try:
            # Save config first so database module can read the path
            from utils.config import set_config
            set_config("database_path", self.wizard_data['database_path'])
            
            # Update database path in the module
            import database.db as db_module
            db_module.DB_PATH = self.wizard_data['database_path']
            
            # Now initialize with the correct path
            db_module.init_database()
            
            self.update_progress(40, "Database initialized successfully")
            QTimer.singleShot(100, lambda: self.create_shortcuts())
        except Exception as e:
            import traceback
            error_msg = f"Failed to initialize database: {str(e)}"
            print(f"Database init error: {error_msg}")
            print(traceback.format_exc())
            self.show_error(error_msg)
    
    def create_shortcuts(self):
        """Create shortcuts"""
        if not is_shortcut_supported():
            self.update_progress(80, "Skipping shortcuts (not supported)")
            QTimer.singleShot(100, lambda: self.save_configuration())
            return
        
        errors = []
        progress = 40
        step = 40 // 3  # Divide remaining progress among 3 shortcuts
        
        # Desktop shortcut
        if self.wizard_data['shortcuts']['desktop']:
            self.update_progress(progress, "Creating desktop shortcut...")
            success, error = create_desktop_shortcut()
            if not success:
                errors.append(f"Desktop shortcut: {error}")
            progress += step
        
        # Start menu shortcut
        if self.wizard_data['shortcuts']['start_menu']:
            self.update_progress(progress, "Creating Start Menu shortcut...")
            success, error = create_start_menu_shortcut()
            if not success:
                errors.append(f"Start Menu shortcut: {error}")
            progress += step
        
        # Startup shortcut
        if self.wizard_data['shortcuts']['startup']:
            self.update_progress(progress, "Adding to startup...")
            success, error = add_to_startup()
            if not success:
                errors.append(f"Startup: {error}")
            progress += step
        
        if errors:
            self.show_error("Some shortcuts could not be created:\n" + "\n".join(errors))
        else:
            self.update_progress(80, "Shortcuts created successfully")
        
        QTimer.singleShot(100, lambda: self.save_configuration())
    
    def save_configuration(self):
        """Save configuration"""
        try:
            success = save_setup_config(
                installation_dir=self.wizard_data['installation_dir'],
                database_path=self.wizard_data['database_path'],
                shortcuts=self.wizard_data['shortcuts'],
                restaurant_name=self.wizard_data['restaurant_name'],
                currency=self.wizard_data['currency'],
                date_format=self.wizard_data['date_format']
            )
            
            if success:
                self.update_progress(100, "Configuration saved successfully")
                QTimer.singleShot(500, lambda: self.show_completion())
            else:
                self.show_error("Failed to save configuration")
        except Exception as e:
            self.show_error(f"Failed to save configuration: {str(e)}")
    
    def show_completion(self):
        """Show completion page"""
        # Update summary
        summary_text = f"""
        <b>Installation Directory:</b> {self.wizard_data['installation_dir']}<br>
        <b>Database Location:</b> {self.wizard_data['database_path']}<br>
        <b>Restaurant Name:</b> {self.wizard_data['restaurant_name']}<br>
        <b>Currency:</b> {self.wizard_data['currency']}<br>
        <b>Date Format:</b> {self.wizard_data['date_format']}
        """
        self.summary_label.setText(summary_text)
        
        # Go to completion page
        self.current_page = self.stacked_widget.count() - 1
        self.stacked_widget.setCurrentIndex(self.current_page)
        self.update_navigation()
    
    def update_progress(self, value: int, message: str):
        """Update progress bar and status"""
        self.progress_bar.setValue(value)
        self.progress_status.setText(message)
        from PyQt6.QtWidgets import QApplication
        QApplication.processEvents()
    
    def show_error(self, message: str):
        """Show error message with retry option"""
        self.error_label.setText(message)
        self.error_widget.setVisible(True)
        self.btn_retry.setVisible(True)
        self.btn_next.setEnabled(False)
    
    def retry_installation(self):
        """Retry installation from current step"""
        self.error_widget.setVisible(False)
        self.btn_retry.setVisible(False)
        self.btn_next.setEnabled(True)
        self.run_installation()
    
    def finish_wizard(self):
        """Finish wizard and emit signal"""
        launch = self.checkbox_launch.isChecked()
        self.finished.emit(launch)
        self.close()
    
    def cancel_wizard(self):
        """Cancel wizard"""
        reply = QMessageBox.question(
            self, "Cancel Setup",
            "Are you sure you want to cancel the setup? The application will not be configured.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.finished.emit(False)
            self.close()
    
    def setup_animations(self):
        """Setup fade animations"""
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
    
    def fade_in(self):
        """Fade in the wizard"""
        self.setWindowOpacity(0.0)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()
    
    def apply_styles(self):
        """Apply wizard styles"""
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
            }
            QFrame#wizardHeader {
                background-color: #f8f9fa;
                border-bottom: 2px solid #e1e8ed;
            }
            QFrame#wizardFooter {
                background-color: #f8f9fa;
                border-top: 2px solid #e1e8ed;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-size: 11px;
                font-weight: 600;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
            QPushButton#btnCancel {
                background-color: #95a5a6;
            }
            QPushButton#btnCancel:hover {
                background-color: #7f8c8d;
            }
            QRadioButton {
                font-size: 11px;
                spacing: 8px;
            }
            QCheckBox {
                font-size: 11px;
                spacing: 8px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #3498db;
            }
        """)
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle keyboard navigation"""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if self.btn_next.isEnabled():
                self.go_next()
        elif event.key() == Qt.Key.Key_Escape:
            self.cancel_wizard()
        super().keyPressEvent(event)

