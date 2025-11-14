"""
Marwan Management CRM - Main Application
Food & Beverage Restaurant Management System
"""
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QLabel, QFrame
)
from PyQt6.QtCore import Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor
from utils.icons import get_icon, create_icon_button

from database.db import init_database
from ui.dashboard import DashboardPage
from ui.products import ProductsPage
from ui.waste import WastePage
from ui.assets import AssetsPage
from ui.analytics import AnalyticsPage
from ui.splash import SplashScreen
from ui.setup_wizard import SetupWizard
from utils.updater_ui import show_update_dialog
from utils.config import is_setup_complete, should_rerun_wizard


class MainWindow(QMainWindow):
    def __init__(self, splash_screen=None):
        super().__init__()
        self.splash = splash_screen
        self.setWindowTitle("Marwan Management CRM - FnB")
        
        # Center window on screen, ensuring it's always visible
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        window_width = 1400
        window_height = 900
        
        # Calculate center position
        x = (screen.width() - window_width) // 2
        y = (screen.height() - window_height) // 2
        
        # Ensure window is always on-screen (no negative coordinates)
        x = max(0, x)
        y = max(0, y)
        
        # If window is larger than screen, adjust to fit
        if window_width > screen.width():
            x = 0
            window_width = screen.width()
        if window_height > screen.height():
            y = 0
            window_height = screen.height()
        
        self.setGeometry(x, y, window_width, window_height)
        
        # Initialize database
        if self.splash:
            self.splash.update_status("Initializing database...", 5)
        init_database()
        
        # Create central widget
        if self.splash:
            self.splash.update_status("Setting up interface...", 15)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        if self.splash:
            self.splash.update_status("Creating navigation sidebar...", 25)
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Content area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Top bar
        if self.splash:
            self.splash.update_status("Setting up top bar...", 35)
        top_bar = self.create_top_bar()
        content_layout.addWidget(top_bar)
        
        # Stacked widget for pages
        self.stacked_widget = QStackedWidget()
        content_layout.addWidget(self.stacked_widget)
        
        # Create pages with progress updates
        if self.splash:
            self.splash.update_status("Loading Dashboard page...", 45)
        self.dashboard_page = DashboardPage()
        self.stacked_widget.addWidget(self.dashboard_page)
        
        if self.splash:
            self.splash.update_status("Loading Products page...", 60)
        self.products_page = ProductsPage()
        self.stacked_widget.addWidget(self.products_page)
        
        if self.splash:
            self.splash.update_status("Loading Waste page...", 75)
        self.waste_page = WastePage()
        self.stacked_widget.addWidget(self.waste_page)
        
        if self.splash:
            self.splash.update_status("Loading Assets page...", 85)
        self.assets_page = AssetsPage()
        self.stacked_widget.addWidget(self.assets_page)
        
        if self.splash:
            self.splash.update_status("Loading Analytics page...", 90)
        self.analytics_page = AnalyticsPage()
        self.stacked_widget.addWidget(self.analytics_page)
        
        main_layout.addWidget(content_widget, stretch=1)
        
        # Set default page
        if self.splash:
            self.splash.update_status("Finalizing setup...", 95)
        self.navigate_to_page(0)
        
        # Apply styles
        self.apply_styles()
        
        # Complete loading
        if self.splash:
            self.splash.update_status("Ready!", 100)
        
        # Auto-check for updates on startup (after 2 seconds delay)
        QTimer.singleShot(2000, self.check_for_updates)
    
    def create_sidebar(self) -> QWidget:
        """Create the sidebar navigation"""
        sidebar = QFrame()
        sidebar.setFixedWidth(250)
        sidebar.setObjectName("sidebar")
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(20, 30, 20, 20)
        layout.setSpacing(10)
        
        # Logo/Title section
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(5)
        
        title = QLabel("Marwan CRM")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2c3e50; padding: 10px 0px;")
        title_layout.addWidget(title)
        
        subtitle = QLabel("Food & Beverage Management")
        subtitle.setFont(QFont("Segoe UI", 9))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #7f8c8d; padding-bottom: 15px;")
        title_layout.addWidget(subtitle)
        
        layout.addWidget(title_container)
        
        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("color: #e0e0e0; margin: 10px 0px;")
        layout.addWidget(separator)
        
        layout.addSpacing(10)
        
        # Navigation buttons with icons
        self.btn_dashboard = create_icon_button("Dashboard", "dashboard")
        self.btn_products = create_icon_button("Products", "products")
        self.btn_waste = create_icon_button("Waste", "waste")
        self.btn_assets = create_icon_button("Assets", "assets")
        self.btn_analytics = create_icon_button("Analytics", "analytics")
        
        buttons = [
            self.btn_dashboard,
            self.btn_products,
            self.btn_waste,
            self.btn_assets,
            self.btn_analytics
        ]
        
        for btn in buttons:
            btn.setFixedHeight(48)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setObjectName("navButton")
            btn.setIconSize(QSize(20, 20))
            layout.addWidget(btn)
        
        # Connect buttons
        self.btn_dashboard.clicked.connect(lambda: self.navigate_to_page(0))
        self.btn_products.clicked.connect(lambda: self.navigate_to_page(1))
        self.btn_waste.clicked.connect(lambda: self.navigate_to_page(2))
        self.btn_assets.clicked.connect(lambda: self.navigate_to_page(3))
        self.btn_analytics.clicked.connect(lambda: self.navigate_to_page(4))
        
        layout.addStretch()
        
        return sidebar
    
    def create_top_bar(self) -> QWidget:
        """Create the top bar"""
        top_bar = QFrame()
        top_bar.setFixedHeight(60)
        top_bar.setObjectName("topBar")
        
        layout = QHBoxLayout(top_bar)
        layout.setContentsMargins(30, 0, 30, 0)
        
        # Title (will be updated based on current page)
        self.page_title = QLabel("Dashboard")
        self.page_title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.page_title.setStyleSheet("color: #2c3e50; padding: 5px 0px;")
        layout.addWidget(self.page_title)
        
        layout.addStretch()
        
        return top_bar
    
    def navigate_to_page(self, index: int):
        """Navigate to a specific page"""
        self.stacked_widget.setCurrentIndex(index)
        
        # Update page title
        titles = ["Dashboard", "Products", "Waste", "Assets", "Analytics"]
        self.page_title.setText(titles[index])
        
        # Update button styles
        buttons = [
            self.btn_dashboard,
            self.btn_products,
            self.btn_waste,
            self.btn_assets,
            self.btn_analytics
        ]
        
        for i, btn in enumerate(buttons):
            if i == index:
                btn.setStyleSheet("""
                    QPushButton#navButton {
                        background-color: #3498db;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        text-align: left;
                        padding: 12px 15px;
                        font-size: 14px;
                        font-weight: 600;
                        font-family: 'Segoe UI';
                    }
                    QPushButton#navButton:hover {
                        background-color: #2980b9;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton#navButton {
                        background-color: transparent;
                        color: #34495e;
                        border: none;
                        border-radius: 6px;
                        text-align: left;
                        padding: 12px 15px;
                        font-size: 14px;
                        font-weight: 500;
                        font-family: 'Segoe UI';
                    }
                    QPushButton#navButton:hover {
                        background-color: #f8f9fa;
                        color: #2c3e50;
                    }
                """)
        
        # Refresh current page if it has a refresh method
        current_widget = self.stacked_widget.currentWidget()
        if hasattr(current_widget, 'refresh'):
            current_widget.refresh()
    
    def check_for_updates(self):
        """Check for updates silently in background"""
        # Check for updates without showing dialog unless update is available
        from utils.updater import check_for_updates, APP_VERSION, GITHUB_REPO
        from PyQt6.QtWidgets import QMessageBox
        
        try:
            update_available, latest_version, release_info = check_for_updates(GITHUB_REPO)
            
            if update_available and release_info:
                # Show update dialog only if update is available
                show_update_dialog(self, auto_check=True)
            # If no update or no releases, do nothing (silent check)
        except Exception as e:
            # Silently fail - don't interrupt user experience
            pass
    
    def apply_styles(self):
        """Apply application-wide styles"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f7fa;
            }
            QFrame#sidebar {
                background-color: #ffffff;
                border-right: 1px solid #e1e8ed;
            }
            QFrame#topBar {
                background-color: #ffffff;
                border-bottom: 2px solid #e1e8ed;
                padding: 0px;
            }
        """)


# Global reference to keep window alive
_main_window = None
_window_shown = False


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Skip setup wizard when running as script (development mode)
    # Only show wizard when running as compiled executable
    is_compiled = getattr(sys, 'frozen', False)
    
    # Check if setup is needed (only for compiled executable)
    if is_compiled and (not is_setup_complete() or should_rerun_wizard()):
        # Show setup wizard
        wizard = SetupWizard()
        wizard.show()
        wizard.fade_in()
        
        def on_wizard_finished(launch_app: bool):
            """Handle wizard completion"""
            if launch_app:
                # Setup complete, launch main application
                splash = SplashScreen()
                splash.show()
                splash.fade_in()
                app.processEvents()
                QTimer.singleShot(300, lambda: load_application(app, splash))
            else:
                # User cancelled or chose not to launch
                app.quit()
        
        wizard.finished.connect(on_wizard_finished)
    else:
        # Development mode or setup already complete, show splash and load application
        splash = SplashScreen()
        splash.show()
        splash.fade_in()
        
        # Process events to ensure splash is visible
        app.processEvents()
        
        # Small delay to show splash
        QTimer.singleShot(300, lambda: load_application(app, splash))
    
    # Start the application event loop
    sys.exit(app.exec())


def load_application(app, splash):
    """Load the main application with progress updates"""
    global _main_window
    try:
        print("Loading application...")
        # Create main window (hidden, will show after loading)
        _main_window = MainWindow(splash_screen=splash)
        print("Main window created")
        _main_window.hide()  # Keep hidden until loading is complete
        
        # Small delay to ensure everything is ready
        QTimer.singleShot(500, lambda: finish_loading(app, splash))
    except Exception as e:
        # If loading fails, show error and close splash
        import traceback
        error_msg = f"Error: {str(e)}"
        print(f"ERROR: {error_msg}")
        print(traceback.format_exc())
        splash.update_status(error_msg, 0)
        QTimer.singleShot(2000, lambda: splash.close())


def finish_loading(app, splash):
    """Finish loading sequence - fade out splash and show main window"""
    global _main_window
    print("Finishing loading...")
    if _main_window is None:
        error_msg = "Error: Window not created"
        print(error_msg)
        splash.update_status(error_msg, 0)
        QTimer.singleShot(2000, lambda: splash.close())
        return
    
    print("Preparing to show main window...")
    # Show window immediately, then fade out splash
    show_main_window(splash)
    
    # Fade out splash after a short delay
    QTimer.singleShot(300, lambda: close_splash(splash))


def close_splash(splash):
    """Close the splash screen"""
    if splash:
        print("Closing splash screen...")
        splash.fade_out()
        QTimer.singleShot(600, lambda: splash.close())


def show_main_window(splash):
    """Show main window (splash will be closed separately)"""
    global _main_window, _window_shown
    print("Showing main window...")
    
    if _main_window is None:
        print("ERROR: _main_window is None!")
        return
    
    # Prevent showing multiple times
    if _window_shown:
        print("Window already shown, skipping...")
        return
    
    _window_shown = True
    
    # Process events first
    from PyQt6.QtWidgets import QApplication
    QApplication.processEvents()
    
    # Ensure window is on-screen before showing
    screen = QApplication.primaryScreen().geometry()
    current_geom = _main_window.geometry()
    
    # Fix negative coordinates - ensure window is visible
    x = current_geom.x()
    y = current_geom.y()
    if x < 0 or y < 0:
        x = max(0, x)
        y = max(0, y)
        _main_window.move(x, y)
        print(f"Fixed window position from ({current_geom.x()}, {current_geom.y()}) to ({x}, {y})")
    
    # Make sure window flags are correct - remove any splash-like flags
    flags = _main_window.windowFlags()
    flags = flags & ~Qt.WindowType.WindowStaysOnTopHint
    flags = flags & ~Qt.WindowType.SplashScreen
    flags = flags | Qt.WindowType.Window
    _main_window.setWindowFlags(flags)
    
    # Set window to be visible and on top
    _main_window.setWindowOpacity(1.0)
    _main_window.showMaximized()  # Maximize window on startup
    _main_window.raise_()
    _main_window.activateWindow()
    
    # Process events again
    QApplication.processEvents()
    
    print(f"Window shown - Visible: {_main_window.isVisible()}, Opacity: {_main_window.windowOpacity()}")
    print(f"Window geometry: {_main_window.geometry()}")
    print(f"Window flags: {_main_window.windowFlags()}")
    
    # Verify window is actually visible
    if not _main_window.isVisible():
        print("WARNING: Window is not visible after show() call!")
        _main_window.setVisible(True)
        _main_window.show()
        QApplication.processEvents()


def fade_in_window():
    """Fade in the main window"""
    global _main_window
    if _main_window is None:
        return
    
    print("Starting fade in animation...")
    _main_window.setWindowOpacity(0.0)
    fade_in = QPropertyAnimation(_main_window, b"windowOpacity")
    fade_in.setDuration(300)
    fade_in.setStartValue(0.0)
    fade_in.setEndValue(1.0)
    fade_in.finished.connect(lambda: print("Fade in complete"))
    fade_in.start()


if __name__ == "__main__":
    main()

