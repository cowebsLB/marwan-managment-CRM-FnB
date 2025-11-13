"""
Helper utilities for the CRM application
"""
from PyQt6.QtWidgets import QMessageBox, QFileDialog
from PyQt6.QtCore import Qt
import pandas as pd
from typing import List, Dict, Tuple


def show_error_message(parent, title: str, message: str):
    """Show an error message dialog"""
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.exec()


def show_success_message(parent, title: str, message: str):
    """Show a success message dialog"""
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.exec()


def show_confirm_dialog(parent, title: str, message: str) -> bool:
    """Show a confirmation dialog, returns True if user confirms"""
    reply = QMessageBox.question(
        parent,
        title,
        message,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No
    )
    return reply == QMessageBox.StandardButton.Yes


def validate_number(value: str, field_name: str = "Value") -> Tuple[bool, float]:
    """Validate and convert string to float"""
    try:
        num = float(value)
        if num < 0:
            return False, 0.0
        return True, num
    except ValueError:
        return False, 0.0


def validate_integer(value: str, field_name: str = "Value") -> Tuple[bool, int]:
    """Validate and convert string to integer"""
    try:
        num = int(value)
        if num < 0:
            return False, 0
        return True, num
    except ValueError:
        return False, 0


def export_to_csv(data: List[Dict], headers: List[str], parent=None) -> bool:
    """Export data to CSV file"""
    try:
        file_path, _ = QFileDialog.getSaveFileName(
            parent,
            "Export to CSV",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_path:
            return False
        
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)
        return True
    except Exception as e:
        show_error_message(parent, "Export Error", f"Failed to export CSV: {str(e)}")
        return False


def export_to_excel(data: List[Dict], headers: List[str], parent=None) -> bool:
    """Export data to Excel file"""
    try:
        file_path, _ = QFileDialog.getSaveFileName(
            parent,
            "Export to Excel",
            "",
            "Excel Files (*.xlsx);;All Files (*)"
        )
        
        if not file_path:
            return False
        
        df = pd.DataFrame(data)
        df.to_excel(file_path, index=False, engine='openpyxl')
        return True
    except Exception as e:
        show_error_message(parent, "Export Error", f"Failed to export Excel: {str(e)}")
        return False

