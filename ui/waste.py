"""
Waste page for the CRM application
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QLineEdit, QDialog, QFormLayout, QMessageBox,
    QHeaderView, QAbstractItemView, QDateEdit, QSplitter
)
from PyQt6.QtCore import Qt, QDate, QSize
from PyQt6.QtGui import QFont
from utils.icons import get_icon, create_icon_button

from database.db import (
    get_all_waste, add_waste, update_waste, delete_waste, get_waste,
    get_waste_by_reason
)
from utils.helpers import (
    show_error_message, show_success_message, show_confirm_dialog,
    validate_integer, export_to_csv, export_to_excel
)
from utils.charts import create_waste_by_reason_chart


class WasteDialog(QDialog):
    """Dialog for adding/editing waste entries"""
    def __init__(self, parent=None, waste_id=None):
        super().__init__(parent)
        self.waste_id = waste_id
        self.setWindowTitle("Edit Waste Entry" if waste_id else "Add Waste Entry")
        self.setModal(True)
        self.setFixedWidth(400)
        
        layout = QFormLayout(self)
        
        self.item_input = QLineEdit()
        self.quantity_input = QLineEdit()
        self.reason_input = QLineEdit()
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        
        layout.addRow("Item:", self.item_input)
        layout.addRow("Quantity:", self.quantity_input)
        layout.addRow("Reason:", self.reason_input)
        layout.addRow("Date:", self.date_input)
        
        buttons = QHBoxLayout()
        btn_save = QPushButton("Save")
        btn_cancel = QPushButton("Cancel")
        
        btn_save.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        
        buttons.addWidget(btn_save)
        buttons.addWidget(btn_cancel)
        layout.addRow(buttons)
        
        # Load existing data if editing
        if waste_id:
            self.load_waste()
    
    def load_waste(self):
        """Load waste data into form"""
        waste = get_waste(self.waste_id)
        if waste:
            self.item_input.setText(waste['item'])
            self.quantity_input.setText(str(waste['quantity']))
            self.reason_input.setText(waste['reason'] or '')
            date = QDate.fromString(waste['date'], "yyyy-MM-dd")
            self.date_input.setDate(date)
    
    def get_data(self):
        """Get form data"""
        return {
            'item': self.item_input.text().strip(),
            'quantity': self.quantity_input.text().strip(),
            'reason': self.reason_input.text().strip(),
            'date': self.date_input.date().toString("yyyy-MM-dd")
        }


class WastePage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.refresh()
    
    def init_ui(self):
        """Initialize the waste UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header with title and buttons
        header = QHBoxLayout()
        
        title = QLabel("Waste Management")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        header.addWidget(title)
        
        header.addStretch()
        
        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search waste entries...")
        self.search_input.setFixedWidth(300)
        self.search_input.setFixedHeight(35)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 13px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        self.search_input.textChanged.connect(self.filter_table)
        header.addWidget(self.search_input)
        
        # Action buttons with icons
        btn_add = create_icon_button("Add Waste Entry", "add")
        btn_add.setFixedHeight(35)
        btn_add.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btn_add.clicked.connect(self.add_waste)
        
        btn_export_csv = create_icon_button("Export CSV", "export")
        btn_export_csv.setFixedHeight(35)
        btn_export_csv.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        btn_export_csv.clicked.connect(lambda: self.export_data('csv'))
        
        btn_export_excel = create_icon_button("Export Excel", "export")
        btn_export_excel.setFixedHeight(35)
        btn_export_excel.setStyleSheet("""
            QPushButton {
                background-color: #16a085;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #138d75;
            }
        """)
        btn_export_excel.clicked.connect(lambda: self.export_data('excel'))
        
        header.addWidget(btn_add)
        header.addWidget(btn_export_csv)
        header.addWidget(btn_export_excel)
        
        layout.addLayout(header)
        
        # Splitter for table and chart
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Table widget
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Item", "Quantity", "Reason", "Date"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e1e8ed;
                border-radius: 6px;
                gridline-color: #f0f0f0;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #e1e8ed;
                font-weight: 600;
                font-size: 12px;
                color: #2c3e50;
            }
        """)
        
        # Context menu for edit/delete
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        table_layout.addWidget(self.table)
        splitter.addWidget(table_widget)
        
        # Chart widget
        chart_widget = QWidget()
        chart_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #e1e8ed;
                border-radius: 8px;
            }
        """)
        chart_layout = QVBoxLayout(chart_widget)
        chart_layout.setContentsMargins(20, 20, 20, 20)
        
        chart_title = QLabel("Waste by Reason")
        chart_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        chart_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        chart_layout.addWidget(chart_title)
        
        self.chart_container = QWidget()
        chart_layout.addWidget(self.chart_container)
        
        splitter.addWidget(chart_widget)
        
        # Set splitter proportions (60% table, 40% chart)
        splitter.setSizes([600, 400])
        
        layout.addWidget(splitter)
    
    def refresh(self):
        """Refresh waste table and chart"""
        waste_entries = get_all_waste()
        self.all_waste = waste_entries
        self.populate_table(waste_entries)
        self.update_chart()
    
    def populate_table(self, waste_entries):
        """Populate table with waste entries"""
        self.table.setRowCount(len(waste_entries))
        
        for row, waste in enumerate(waste_entries):
            self.table.setItem(row, 0, QTableWidgetItem(str(waste['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(waste['item']))
            self.table.setItem(row, 2, QTableWidgetItem(str(waste['quantity'])))
            self.table.setItem(row, 3, QTableWidgetItem(waste['reason'] or ''))
            self.table.setItem(row, 4, QTableWidgetItem(waste['date']))
            
            # Center align ID and numbers
            for col in [0, 2]:
                item = self.table.item(row, col)
                if item:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def filter_table(self):
        """Filter table based on search input"""
        search_text = self.search_input.text().lower()
        
        if not search_text:
            self.populate_table(self.all_waste)
            return
        
        filtered = [
            w for w in self.all_waste
            if search_text in w['item'].lower() or
               search_text in (w['reason'] or '').lower()
        ]
        self.populate_table(filtered)
    
    def update_chart(self):
        """Update the waste by reason chart"""
        waste_data = get_waste_by_reason()
        
        # Clear existing chart
        layout = self.chart_container.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        else:
            layout = QVBoxLayout(self.chart_container)
            layout.setContentsMargins(0, 0, 0, 0)
        
        # Create new chart
        chart = create_waste_by_reason_chart(waste_data)
        layout.addWidget(chart)
    
    def add_waste(self):
        """Add a new waste entry"""
        dialog = WasteDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            
            if not data['item']:
                show_error_message(self, "Validation Error", "Item name is required")
                return
            
            valid_qty, quantity = validate_integer(data['quantity'], "Quantity")
            
            if not valid_qty:
                show_error_message(self, "Validation Error", "Invalid quantity")
                return
            
            try:
                add_waste(data['item'], quantity, data['reason'], data['date'])
                show_success_message(self, "Success", "Waste entry added successfully")
                self.refresh()
            except Exception as e:
                show_error_message(self, "Error", f"Failed to add waste entry: {str(e)}")
    
    def edit_waste(self):
        """Edit selected waste entry"""
        selected = self.table.selectedItems()
        if not selected:
            show_error_message(self, "No Selection", "Please select a waste entry to edit")
            return
        
        waste_id = int(self.table.item(selected[0].row(), 0).text())
        dialog = WasteDialog(self, waste_id)
        
        if dialog.exec():
            data = dialog.get_data()
            
            if not data['item']:
                show_error_message(self, "Validation Error", "Item name is required")
                return
            
            valid_qty, quantity = validate_integer(data['quantity'], "Quantity")
            
            if not valid_qty:
                show_error_message(self, "Validation Error", "Invalid quantity")
                return
            
            try:
                update_waste(waste_id, data['item'], quantity, data['reason'], data['date'])
                show_success_message(self, "Success", "Waste entry updated successfully")
                self.refresh()
            except Exception as e:
                show_error_message(self, "Error", f"Failed to update waste entry: {str(e)}")
    
    def delete_waste_action(self):
        """Delete selected waste entry"""
        selected = self.table.selectedItems()
        if not selected:
            show_error_message(self, "No Selection", "Please select a waste entry to delete")
            return
        
        waste_id = int(self.table.item(selected[0].row(), 0).text())
        item_name = self.table.item(selected[0].row(), 1).text()
        
        if show_confirm_dialog(self, "Confirm Delete", 
                              f"Are you sure you want to delete this waste entry for '{item_name}'?"):
            try:
                delete_waste(waste_id)
                show_success_message(self, "Success", "Waste entry deleted successfully")
                self.refresh()
            except Exception as e:
                show_error_message(self, "Error", f"Failed to delete waste entry: {str(e)}")
    
    def show_context_menu(self, position):
        """Show context menu for table"""
        if self.table.itemAt(position) is None:
            return
        
        from PyQt6.QtWidgets import QMenu
        
        menu = QMenu(self)
        edit_icon = get_icon('edit')
        delete_icon = get_icon('delete')
        edit_action = menu.addAction(edit_icon, "Edit")
        delete_action = menu.addAction(delete_icon, "Delete")
        
        action = menu.exec(self.table.mapToGlobal(position))
        
        if action == edit_action:
            self.edit_waste()
        elif action == delete_action:
            self.delete_waste_action()
    
    def export_data(self, format_type: str):
        """Export waste data"""
        waste_entries = get_all_waste()
        
        # Convert to list of dicts for export
        export_data = [
            {
                'ID': w['id'],
                'Item': w['item'],
                'Quantity': w['quantity'],
                'Reason': w['reason'] or '',
                'Date': w['date']
            }
            for w in waste_entries
        ]
        
        headers = ['ID', 'Item', 'Quantity', 'Reason', 'Date']
        
        if format_type == 'csv':
            if export_to_csv(export_data, headers, self):
                show_success_message(self, "Success", "Data exported to CSV successfully")
        elif format_type == 'excel':
            if export_to_excel(export_data, headers, self):
                show_success_message(self, "Success", "Data exported to Excel successfully")

