"""
Products page for the CRM application
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QLineEdit, QDialog, QFormLayout, QMessageBox,
    QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont
from utils.icons import get_icon, create_icon_button

from database.db import get_all_products, add_product, update_product, delete_product, get_product
from utils.helpers import (
    show_error_message, show_success_message, show_confirm_dialog,
    validate_number, validate_integer, export_to_csv, export_to_excel
)


class ProductDialog(QDialog):
    """Dialog for adding/editing products"""
    def __init__(self, parent=None, product_id=None):
        super().__init__(parent)
        self.product_id = product_id
        self.setWindowTitle("Edit Product" if product_id else "Add Product")
        self.setModal(True)
        self.setFixedWidth(400)
        
        layout = QFormLayout(self)
        
        self.name_input = QLineEdit()
        self.category_input = QLineEdit()
        self.quantity_input = QLineEdit()
        self.price_input = QLineEdit()
        
        layout.addRow("Name:", self.name_input)
        layout.addRow("Category:", self.category_input)
        layout.addRow("Quantity:", self.quantity_input)
        layout.addRow("Unit Price:", self.price_input)
        
        buttons = QHBoxLayout()
        btn_save = QPushButton("Save")
        btn_cancel = QPushButton("Cancel")
        
        btn_save.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        
        buttons.addWidget(btn_save)
        buttons.addWidget(btn_cancel)
        layout.addRow(buttons)
        
        # Load existing data if editing
        if product_id:
            self.load_product()
    
    def load_product(self):
        """Load product data into form"""
        product = get_product(self.product_id)
        if product:
            self.name_input.setText(product['name'])
            self.category_input.setText(product['category'] or '')
            self.quantity_input.setText(str(product['quantity']))
            self.price_input.setText(str(product['unit_price']))
    
    def get_data(self):
        """Get form data"""
        return {
            'name': self.name_input.text().strip(),
            'category': self.category_input.text().strip(),
            'quantity': self.quantity_input.text().strip(),
            'price': self.price_input.text().strip()
        }


class ProductsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.refresh()
    
    def init_ui(self):
        """Initialize the products UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header with title and buttons
        header = QHBoxLayout()
        
        title = QLabel("Products Management")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        header.addWidget(title)
        
        header.addStretch()
        
        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search products...")
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
        search_icon = get_icon('search')
        if not search_icon.isNull():
            # Note: QLineEdit doesn't directly support icons, but we can style it
            pass
        self.search_input.textChanged.connect(self.filter_table)
        header.addWidget(self.search_input)
        
        # Action buttons with icons
        btn_add = create_icon_button("Add Product", "add")
        btn_add.setFixedHeight(35)
        btn_add.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        btn_add.clicked.connect(self.add_product)
        
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
        
        # Table with professional styling
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Category", "Quantity", "Unit Price"])
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
        
        layout.addWidget(self.table)
    
    def refresh(self):
        """Refresh products table"""
        products = get_all_products()
        self.all_products = products
        self.populate_table(products)
    
    def populate_table(self, products):
        """Populate table with products"""
        self.table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            self.table.setItem(row, 0, QTableWidgetItem(str(product['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(product['name']))
            self.table.setItem(row, 2, QTableWidgetItem(product['category'] or ''))
            self.table.setItem(row, 3, QTableWidgetItem(str(product['quantity'])))
            self.table.setItem(row, 4, QTableWidgetItem(f"${product['unit_price']:.2f}"))
            
            # Center align ID and numbers
            for col in [0, 3, 4]:
                item = self.table.item(row, col)
                if item:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def filter_table(self):
        """Filter table based on search input"""
        search_text = self.search_input.text().lower()
        
        if not search_text:
            self.populate_table(self.all_products)
            return
        
        filtered = [
            p for p in self.all_products
            if search_text in p['name'].lower() or
               search_text in (p['category'] or '').lower()
        ]
        self.populate_table(filtered)
    
    def add_product(self):
        """Add a new product"""
        dialog = ProductDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            
            if not data['name']:
                show_error_message(self, "Validation Error", "Product name is required")
                return
            
            valid_qty, quantity = validate_integer(data['quantity'], "Quantity")
            valid_price, price = validate_number(data['price'], "Price")
            
            if not valid_qty:
                show_error_message(self, "Validation Error", "Invalid quantity")
                return
            
            if not valid_price:
                show_error_message(self, "Validation Error", "Invalid price")
                return
            
            try:
                add_product(data['name'], data['category'], quantity, price)
                show_success_message(self, "Success", "Product added successfully")
                self.refresh()
            except Exception as e:
                show_error_message(self, "Error", f"Failed to add product: {str(e)}")
    
    def edit_product(self):
        """Edit selected product"""
        selected = self.table.selectedItems()
        if not selected:
            show_error_message(self, "No Selection", "Please select a product to edit")
            return
        
        product_id = int(self.table.item(selected[0].row(), 0).text())
        dialog = ProductDialog(self, product_id)
        
        if dialog.exec():
            data = dialog.get_data()
            
            if not data['name']:
                show_error_message(self, "Validation Error", "Product name is required")
                return
            
            valid_qty, quantity = validate_integer(data['quantity'], "Quantity")
            valid_price, price = validate_number(data['price'], "Price")
            
            if not valid_qty:
                show_error_message(self, "Validation Error", "Invalid quantity")
                return
            
            if not valid_price:
                show_error_message(self, "Validation Error", "Invalid price")
                return
            
            try:
                update_product(product_id, data['name'], data['category'], quantity, price)
                show_success_message(self, "Success", "Product updated successfully")
                self.refresh()
            except Exception as e:
                show_error_message(self, "Error", f"Failed to update product: {str(e)}")
    
    def delete_product_action(self):
        """Delete selected product"""
        selected = self.table.selectedItems()
        if not selected:
            show_error_message(self, "No Selection", "Please select a product to delete")
            return
        
        product_id = int(self.table.item(selected[0].row(), 0).text())
        product_name = self.table.item(selected[0].row(), 1).text()
        
        if show_confirm_dialog(self, "Confirm Delete", 
                              f"Are you sure you want to delete '{product_name}'?"):
            try:
                delete_product(product_id)
                show_success_message(self, "Success", "Product deleted successfully")
                self.refresh()
            except Exception as e:
                show_error_message(self, "Error", f"Failed to delete product: {str(e)}")
    
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
            self.edit_product()
        elif action == delete_action:
            self.delete_product_action()
    
    def export_data(self, format_type: str):
        """Export products data"""
        products = get_all_products()
        
        # Convert to list of dicts for export
        export_data = [
            {
                'ID': p['id'],
                'Name': p['name'],
                'Category': p['category'] or '',
                'Quantity': p['quantity'],
                'Unit Price': p['unit_price']
            }
            for p in products
        ]
        
        headers = ['ID', 'Name', 'Category', 'Quantity', 'Unit Price']
        
        if format_type == 'csv':
            if export_to_csv(export_data, headers, self):
                show_success_message(self, "Success", "Data exported to CSV successfully")
        elif format_type == 'excel':
            if export_to_excel(export_data, headers, self):
                show_success_message(self, "Success", "Data exported to Excel successfully")

