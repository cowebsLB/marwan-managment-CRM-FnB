"""
Marwan Management CRM - Main Application
Food & Beverage Restaurant Management System
"""
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QLabel, QFrame
)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QFont, QIcon

from database.db import init_database
from ui.dashboard import DashboardPage
from ui.products import ProductsPage
from ui.waste import WastePage
from ui.assets import AssetsPage
from utils.updater_ui import show_update_dialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Marwan Management CRM - FnB")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize database
        init_database()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Content area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Top bar
        top_bar = self.create_top_bar()
        content_layout.addWidget(top_bar)
        
        # Stacked widget for pages
        self.stacked_widget = QStackedWidget()
        content_layout.addWidget(self.stacked_widget)
        
        # Create pages
        self.dashboard_page = DashboardPage()
        self.products_page = ProductsPage()
        self.waste_page = WastePage()
        self.assets_page = AssetsPage()
        
        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.products_page)
        self.stacked_widget.addWidget(self.waste_page)
        self.stacked_widget.addWidget(self.assets_page)
        
        main_layout.addWidget(content_widget, stretch=1)
        
        # Set default page
        self.navigate_to_page(0)
        
        # Apply styles
        self.apply_styles()
        
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
        
        # Logo/Title
        title = QLabel("Marwan CRM")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Food & Beverage")
        subtitle.setFont(QFont("Arial", 10))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #7f8c8d; margin-bottom: 20px;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        # Navigation buttons
        self.btn_dashboard = QPushButton("📊 Dashboard")
        self.btn_products = QPushButton("📦 Products")
        self.btn_waste = QPushButton("🗑️ Waste")
        self.btn_assets = QPushButton("💼 Assets")
        
        buttons = [
            self.btn_dashboard,
            self.btn_products,
            self.btn_waste,
            self.btn_assets
        ]
        
        for btn in buttons:
            btn.setFixedHeight(50)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setObjectName("navButton")
            layout.addWidget(btn)
        
        # Connect buttons
        self.btn_dashboard.clicked.connect(lambda: self.navigate_to_page(0))
        self.btn_products.clicked.connect(lambda: self.navigate_to_page(1))
        self.btn_waste.clicked.connect(lambda: self.navigate_to_page(2))
        self.btn_assets.clicked.connect(lambda: self.navigate_to_page(3))
        
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
        self.page_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(self.page_title)
        
        layout.addStretch()
        
        return top_bar
    
    def navigate_to_page(self, index: int):
        """Navigate to a specific page"""
        self.stacked_widget.setCurrentIndex(index)
        
        # Update page title
        titles = ["Dashboard", "Products", "Waste", "Assets"]
        self.page_title.setText(titles[index])
        
        # Update button styles
        buttons = [
            self.btn_dashboard,
            self.btn_products,
            self.btn_waste,
            self.btn_assets
        ]
        
        for i, btn in enumerate(buttons):
            if i == index:
                btn.setStyleSheet("""
                    QPushButton#navButton {
                        background-color: #3498db;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        text-align: left;
                        padding-left: 15px;
                        font-size: 14px;
                        font-weight: bold;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton#navButton {
                        background-color: transparent;
                        color: #2c3e50;
                        border: none;
                        border-radius: 8px;
                        text-align: left;
                        padding-left: 15px;
                        font-size: 14px;
                    }
                    QPushButton#navButton:hover {
                        background-color: #ecf0f1;
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
                background-color: #f5f6fa;
            }
            QFrame#sidebar {
                background-color: #ffffff;
                border-right: 1px solid #e0e0e0;
            }
            QFrame#topBar {
                background-color: #ffffff;
                border-bottom: 1px solid #e0e0e0;
            }
            QPushButton#navButton {
                background-color: transparent;
                color: #2c3e50;
                border: none;
                border-radius: 8px;
                text-align: left;
                padding-left: 15px;
                font-size: 14px;
            }
            QPushButton#navButton:hover {
                background-color: #ecf0f1;
            }
        """)


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

