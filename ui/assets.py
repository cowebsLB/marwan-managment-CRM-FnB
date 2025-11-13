"""
Assets page for the CRM application
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QLineEdit, QDialog, QFormLayout, QMessageBox,
    QHeaderView, QAbstractItemView, QDateEdit, QComboBox, QFrame, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, QDate, QSize
from PyQt6.QtGui import QFont
from utils.icons import get_icon, create_icon_button

from database.db import (
    get_all_assets, add_asset, update_asset, delete_asset, get_asset,
    get_total_asset_value, get_average_asset_value, get_assets_by_type,
    get_assets_by_condition
)
from utils.helpers import (
    show_error_message, show_success_message, show_confirm_dialog,
    validate_number, export_to_csv, export_to_excel
)


class AssetDialog(QDialog):
    """Dialog for adding/editing assets"""
    def __init__(self, parent=None, asset_id=None):
        super().__init__(parent)
        self.asset_id = asset_id
        self.setWindowTitle("Edit Asset" if asset_id else "Add Asset")
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
            QLineEdit, QDateEdit, QComboBox {
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 13px;
                background-color: white;
            }
            QLineEdit:focus, QDateEdit:focus, QComboBox:focus {
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
        
        self.name_input = QLineEdit()
        self.type_input = QComboBox()
        self.type_input.setEditable(True)
        self.type_input.addItems(["Equipment", "Vehicle", "Technology", "Furniture", "Other"])
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        self.value_input = QLineEdit()
        self.condition_input = QComboBox()
        self.condition_input.addItems(["Excellent", "Good", "Fair", "Poor"])
        
        layout.addRow("Name:", self.name_input)
        layout.addRow("Type:", self.type_input)
        layout.addRow("Purchase Date:", self.date_input)
        layout.addRow("Value ($):", self.value_input)
        layout.addRow("Condition:", self.condition_input)
        
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
        if asset_id:
            self.load_asset()
    
    def load_asset(self):
        """Load asset data into form"""
        asset = get_asset(self.asset_id)
        if asset:
            self.name_input.setText(asset['name'])
            self.type_input.setCurrentText(asset['type'] or '')
            date = QDate.fromString(asset['purchase_date'], "yyyy-MM-dd")
            self.date_input.setDate(date)
            self.value_input.setText(str(asset['value']))
            self.condition_input.setCurrentText(asset['condition'] or 'Good')
    
    def get_data(self):
        """Get form data"""
        return {
            'name': self.name_input.text().strip(),
            'type': self.type_input.currentText().strip(),
            'date': self.date_input.date().toString("yyyy-MM-dd"),
            'value': self.value_input.text().strip(),
            'condition': self.condition_input.currentText()
        }


class AssetsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.refresh()
    
    def init_ui(self):
        """Initialize the assets UI"""
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
        
        title = QLabel("Assets Management")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        header.addWidget(title)
        
        header.addStretch()
        
        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search assets...")
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
        btn_add = create_icon_button("Add Asset", "add")
        btn_add.setFixedHeight(35)
        btn_add.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        btn_add.clicked.connect(self.add_asset)
        
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
        
        self.total_value_card = self.create_summary_card("Total Asset Value", "$0", "#2ecc71")
        self.avg_value_card = self.create_summary_card("Average Value", "$0", "#1abc9c")
        self.types_card = self.create_summary_card("Asset Types", "0", "#9b59b6")
        self.conditions_card = self.create_summary_card("Conditions", "0", "#34495e")
        
        summary_layout.addWidget(self.total_value_card, stretch=1)
        summary_layout.addWidget(self.avg_value_card, stretch=1)
        summary_layout.addWidget(self.types_card, stretch=1)
        summary_layout.addWidget(self.conditions_card, stretch=1)
        
        layout.addLayout(summary_layout)
        
        # Table with professional styling - set max height so it scrolls internally
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Type", "Purchase Date", "Value", "Condition"])
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
        """Refresh assets table"""
        assets = get_all_assets()
        self.all_assets = assets
        self.populate_table(assets)
        
        # Update summary cards
        total_value = get_total_asset_value()
        avg_value = get_average_asset_value()
        types_data = get_assets_by_type()
        conditions_data = get_assets_by_condition()
        
        self.update_card_value(self.total_value_card, f"${total_value:,.2f}")
        self.update_card_value(self.avg_value_card, f"${avg_value:,.2f}")
        self.update_card_value(self.types_card, str(len(types_data)))
        self.update_card_value(self.conditions_card, str(len(conditions_data)))
    
    def update_card_value(self, card: QFrame, value: str):
        """Update the value in a summary card"""
        value_label = card.findChild(QLabel, "valueLabel")
        if value_label:
            value_label.setText(value)
    
    def populate_table(self, assets):
        """Populate table with assets"""
        self.table.setRowCount(len(assets))
        
        for row, asset in enumerate(assets):
            self.table.setItem(row, 0, QTableWidgetItem(str(asset['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(asset['name']))
            self.table.setItem(row, 2, QTableWidgetItem(asset['type'] or ''))
            self.table.setItem(row, 3, QTableWidgetItem(asset['purchase_date'] or ''))
            self.table.setItem(row, 4, QTableWidgetItem(f"${asset['value']:,.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(asset['condition'] or ''))
            
            # Center align ID and value
            for col in [0, 4]:
                item = self.table.item(row, col)
                if item:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def filter_table(self):
        """Filter table based on search input"""
        search_text = self.search_input.text().lower()
        
        if not search_text:
            self.populate_table(self.all_assets)
            return
        
        filtered = [
            a for a in self.all_assets
            if search_text in a['name'].lower() or
               search_text in (a['type'] or '').lower() or
               search_text in (a['condition'] or '').lower()
        ]
        self.populate_table(filtered)
    
    def add_asset(self):
        """Add a new asset"""
        dialog = AssetDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            
            if not data['name']:
                show_error_message(self, "Validation Error", "Asset name is required")
                return
            
            valid_value, value = validate_number(data['value'], "Value")
            
            if not valid_value:
                show_error_message(self, "Validation Error", "Invalid value")
                return
            
            try:
                add_asset(data['name'], data['type'], data['date'], value, data['condition'])
                show_success_message(self, "Success", "Asset added successfully")
                self.refresh()
            except Exception as e:
                show_error_message(self, "Error", f"Failed to add asset: {str(e)}")
    
    def edit_asset(self):
        """Edit selected asset"""
        selected = self.table.selectedItems()
        if not selected:
            show_error_message(self, "No Selection", "Please select an asset to edit")
            return
        
        asset_id = int(self.table.item(selected[0].row(), 0).text())
        dialog = AssetDialog(self, asset_id)
        
        if dialog.exec():
            data = dialog.get_data()
            
            if not data['name']:
                show_error_message(self, "Validation Error", "Asset name is required")
                return
            
            valid_value, value = validate_number(data['value'], "Value")
            
            if not valid_value:
                show_error_message(self, "Validation Error", "Invalid value")
                return
            
            try:
                update_asset(asset_id, data['name'], data['type'], data['date'], value, data['condition'])
                show_success_message(self, "Success", "Asset updated successfully")
                self.refresh()
            except Exception as e:
                show_error_message(self, "Error", f"Failed to update asset: {str(e)}")
    
    def delete_asset_action(self):
        """Delete selected asset"""
        selected = self.table.selectedItems()
        if not selected:
            show_error_message(self, "No Selection", "Please select an asset to delete")
            return
        
        asset_id = int(self.table.item(selected[0].row(), 0).text())
        asset_name = self.table.item(selected[0].row(), 1).text()
        
        if show_confirm_dialog(self, "Confirm Delete", 
                              f"Are you sure you want to delete '{asset_name}'?"):
            try:
                delete_asset(asset_id)
                show_success_message(self, "Success", "Asset deleted successfully")
                self.refresh()
            except Exception as e:
                show_error_message(self, "Error", f"Failed to delete asset: {str(e)}")
    
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
            self.edit_asset()
        elif action == delete_action:
            self.delete_asset_action()
    
    def export_data(self, format_type: str):
        """Export assets data"""
        assets = get_all_assets()
        
        # Convert to list of dicts for export
        export_data = [
            {
                'ID': a['id'],
                'Name': a['name'],
                'Type': a['type'] or '',
                'Purchase Date': a['purchase_date'] or '',
                'Value': a['value'],
                'Condition': a['condition'] or ''
            }
            for a in assets
        ]
        
        headers = ['ID', 'Name', 'Type', 'Purchase Date', 'Value', 'Condition']
        
        if format_type == 'csv':
            if export_to_csv(export_data, headers, self):
                show_success_message(self, "Success", "Data exported to CSV successfully")
        elif format_type == 'excel':
            if export_to_excel(export_data, headers, self):
                show_success_message(self, "Success", "Data exported to Excel successfully")

