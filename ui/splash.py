"""
Splash Screen for the CRM Application
Shows loading progress with detailed status messages
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PyQt6.QtGui import QFont, QColor, QPainter, QLinearGradient, QBrush


class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.SplashScreen
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(500, 400)
        
        # Center on screen
        self.center_on_screen()
        
        self.init_ui()
        self.setup_animations()
    
    def center_on_screen(self):
        """Center the splash screen on the screen"""
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def init_ui(self):
        """Initialize the splash screen UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 40, 30, 40)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Marwan Management CRM")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Food & Beverage Management System")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #7f8c8d; margin-bottom: 10px;")
        layout.addWidget(subtitle)
        
        layout.addStretch()
        
        # Status label
        self.status_label = QLabel("Initializing...")
        self.status_label.setFont(QFont("Segoe UI", 11))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #34495e; min-height: 30px;")
        layout.addWidget(self.status_label)
        
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
                height: 25px;
                font-size: 11px;
                font-weight: 600;
                color: #2c3e50;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Version label
        try:
            from utils.updater import APP_VERSION
            version_text = f"Version {APP_VERSION}"
        except ImportError:
            version_text = "Version 1.0.0"
        
        version_label = QLabel(version_text)
        version_label.setFont(QFont("Segoe UI", 9))
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #95a5a6; margin-top: 10px;")
        layout.addWidget(version_label)
        
        layout.addStretch()
        
        # Set background style
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 12px;
            }
        """)
    
    def setup_animations(self):
        """Setup fade animations"""
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(500)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
    
    def update_status(self, message: str, progress: int):
        """
        Update status message and progress
        
        Args:
            message: Status message to display
            progress: Progress percentage (0-100)
        """
        self.status_label.setText(message)
        self.progress_bar.setValue(progress)
        # Process events to update UI immediately
        from PyQt6.QtWidgets import QApplication
        QApplication.processEvents()
    
    def fade_out(self, callback=None):
        """
        Fade out the splash screen
        
        Args:
            callback: Optional callback function to call after fade completes
        """
        # Disconnect any previous connections
        try:
            self.fade_animation.finished.disconnect()
        except:
            pass
        
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        
        if callback:
            self.fade_animation.finished.connect(callback)
        
        self.fade_animation.start()
    
    def fade_in(self):
        """Fade in the splash screen"""
        self.setWindowOpacity(0.0)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()
    
    def paintEvent(self, event):
        """Custom paint event for rounded corners and shadow"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw shadow
        shadow_rect = self.rect().adjusted(0, 0, -1, -1)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0, 30))
        painter.drawRoundedRect(shadow_rect.translated(3, 3), 12, 12)
        
        # Draw main background
        painter.setBrush(QColor(255, 255, 255))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect().adjusted(0, 0, -1, -1), 12, 12)
        
        super().paintEvent(event)

