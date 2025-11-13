"""
Waste page for the CRM application
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QLineEdit, QDialog, QFormLayout, QMessageBox,
    QHeaderView, QAbstractItemView, QDateEdit, QFrame, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, QDate, QSize
from PyQt6.QtGui import QFont
from utils.icons import get_icon, create_icon_button

from database.db import (
    get_all_waste, add_waste, update_waste, delete_waste, get_waste,
    get_waste_by_reason, get_total_waste_quantity
)
from utils.helpers import (
    show_error_message, show_success_message, show_confirm_dialog,
    validate_integer, export_to_csv, export_to_excel
)


class WasteDialog(QDialog):
    """Dialog for adding/editing waste entries"""
    def __init__(self, parent=None, waste_id=None):
        super().__init__(parent)
        self.waste_id = waste_id
        self.setWindowTitle("Edit Waste Entry" if waste_id else "Add Waste Entry")
        self.setModal(True)
        self.setFixedWidth(420)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #2c3e50;
                font-size: 13px;
                font-weight: 500;
            }
            QLineEdit, QDateEdit {
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 13px;
                background-color: white;
            }
            QLineEdit:focus, QDateEdit:focus {
                border: 2px solid #3498db;
            }
            QPushButton {
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: 600;
                font-size: 13px;
            }
        """)
        
        layout = QFormLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
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
        buttons.setSpacing(10)
        
        btn_save = create_icon_button("Save", "save")
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        btn_save.clicked.connect(self.accept)
        
        btn_cancel = create_icon_button("Cancel", "cancel")
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        
        buttons.addStretch()
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
        # Create scroll area for better navigation
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        content_widget = QWidget()
        content_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        layout = QVBoxLayout(content_widget)
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
        self.search_input.setMaximumWidth(300)
        self.search_input.setMinimumWidth(200)
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
        
        # Summary cards - use stretch to ensure they fit
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(15)
        
        self.total_waste_card = self.create_summary_card("Total Waste", "0", "#e74c3c")
        self.avg_waste_card = self.create_summary_card("Avg per Entry", "0", "#f39c12")
        self.reasons_card = self.create_summary_card("Unique Reasons", "0", "#9b59b6")
        self.items_card = self.create_summary_card("Unique Items", "0", "#34495e")
        
        summary_layout.addWidget(self.total_waste_card, stretch=1)
        summary_layout.addWidget(self.avg_waste_card, stretch=1)
        summary_layout.addWidget(self.reasons_card, stretch=1)
        summary_layout.addWidget(self.items_card, stretch=1)
        
        layout.addLayout(summary_layout)
        
        # Table with professional styling - set max height so it scrolls internally
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Item", "Quantity", "Reason", "Date"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setMaximumHeight(400)  # Set max height so table scrolls internally
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
        
        layout.addWidget(self.table)
        
        scroll.setWidget(content_widget)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def create_summary_card(self, title: str, value: str, color: str) -> QFrame:
        """Create a summary card widget"""
        card = QFrame()
        card.setObjectName("summaryCard")
        card.setFixedHeight(100)
        card.setMinimumWidth(150)
        card.setStyleSheet(f"""
            QFrame#summaryCard {{
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e1e8ed;
            }}
            QFrame#summaryCard:hover {{
                border: 2px solid {color};
                box-shadow: 0px 2px 8px rgba(0, 0, 0, 0.1);
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 9))
        title_label.setStyleSheet("color: #7f8c8d; font-weight: 500;")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {color};")
        value_label.setObjectName("valueLabel")
        value_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        layout.addWidget(value_label)
        
        return card
    
    def refresh(self):
        """Refresh waste table"""
        waste_entries = get_all_waste()
        self.all_waste = waste_entries
        self.populate_table(waste_entries)
        
        # Update summary cards
        total_waste = get_total_waste_quantity()
        avg_waste = total_waste / len(waste_entries) if waste_entries else 0
        reasons_data = get_waste_by_reason()
        # Count unique items
        unique_items = len(set(w['item'] for w in waste_entries))
        
        self.update_card_value(self.total_waste_card, str(total_waste))
        self.update_card_value(self.avg_waste_card, f"{avg_waste:.1f}")
        self.update_card_value(self.reasons_card, str(len(reasons_data)))
        self.update_card_value(self.items_card, str(unique_items))
    
    def update_card_value(self, card: QFrame, value: str):
        """Update the value in a summary card"""
        value_label = card.findChild(QLabel, "valueLabel")
        if value_label:
            value_label.setText(value)
    
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

