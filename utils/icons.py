"""
Icon utilities for the CRM application
Uses PyQt6's built-in icons and Material Design style
"""
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QStyle
from PyQt6.QtCore import Qt


def get_icon(icon_name: str) -> QIcon:
    """
    Get an icon by name using PyQt6's standard icons.
    
    Args:
        icon_name: Name of the icon (e.g., 'dashboard', 'products', 'add', 'export')
    
    Returns:
        QIcon object
    """
    # Map icon names to QStyle.StandardPixmap
    icon_map = {
        'dashboard': QStyle.StandardPixmap.SP_ComputerIcon,
        'products': QStyle.StandardPixmap.SP_DirIcon,
        'waste': QStyle.StandardPixmap.SP_TrashIcon,
        'assets': QStyle.StandardPixmap.SP_FileDialogDetailedView,
        'add': QStyle.StandardPixmap.SP_FileDialogNewFolder,
        'edit': QStyle.StandardPixmap.SP_FileDialogListView,
        'delete': QStyle.StandardPixmap.SP_TrashIcon,
        'export': QStyle.StandardPixmap.SP_DriveFDIcon,
        'search': QStyle.StandardPixmap.SP_FileDialogContentsView,
        'save': QStyle.StandardPixmap.SP_DialogSaveButton,
        'cancel': QStyle.StandardPixmap.SP_DialogCancelButton,
        'close': QStyle.StandardPixmap.SP_DialogCloseButton,
        'refresh': QStyle.StandardPixmap.SP_BrowserReload,
    }
    
    # Get the application style
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance()
    if app:
        style = app.style()
        if icon_name in icon_map:
            return style.standardIcon(icon_map[icon_name])
    
    # Return empty icon if not found
    return QIcon()


def create_icon_button(text: str, icon_name: str = None, parent=None):
    """
    Create a button with icon and text.
    
    Args:
        text: Button text
        icon_name: Optional icon name
        parent: Parent widget
    
    Returns:
        QPushButton with icon
    """
    from PyQt6.QtWidgets import QPushButton
    
    btn = QPushButton(text, parent)
    if icon_name:
        icon = get_icon(icon_name)
        if not icon.isNull():
            btn.setIcon(icon)
            btn.setIconSize(btn.iconSize())
    
    return btn

