"""
Products page for the CRM application
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QLineEdit, QDialog, QFormLayout, QMessageBox,
    QHeaderView, QAbstractItemView, QFrame, QScrollArea, QSizePolicy, QComboBox, QCompleter
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor
from utils.icons import get_icon, create_icon_button

from database.db import (
    get_all_products, add_product, update_product, delete_product, get_product,
    get_total_inventory_value, get_average_product_price, get_low_stock_products,
    get_products_by_category, get_all_categories
)
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
            QLineEdit, QComboBox {
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 13px;
                background-color: white;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #3498db;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #7f8c8d;
                margin-right: 5px;
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
        
        # Category input with autocomplete
        self.category_input = QComboBox()
        self.category_input.setEditable(True)  # Allow typing new categories
        self.category_input.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)  # Don't auto-insert
        
        # Setup autocomplete
        completer = self.category_input.completer()
        if completer:
            completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)  # Match anywhere in the string
        
        # Load existing categories
        self.refresh_categories()
        
        self.quantity_input = QLineEdit()
        self.price_input = QLineEdit()
        
        layout.addRow("Name:", self.name_input)
        layout.addRow("Category:", self.category_input)
        layout.addRow("Quantity:", self.quantity_input)
        layout.addRow("Unit Price:", self.price_input)
        
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
        if product_id:
            self.load_product()
    
    def refresh_categories(self):
        """Refresh the category list from database"""
        self.category_input.clear()
        categories = get_all_categories()
        self.category_input.addItems(categories)
    
    def load_product(self):
        """Load product data into form"""
        product = get_product(self.product_id)
        if product:
            self.name_input.setText(product['name'])
            # Set category - if it exists in the list, select it; otherwise set as current text
            category = product['category'] or ''
            index = self.category_input.findText(category)
            if index >= 0:
                self.category_input.setCurrentIndex(index)
            else:
                self.category_input.setCurrentText(category)
            self.quantity_input.setText(str(product['quantity']))
            self.price_input.setText(str(product['unit_price']))
    
    def get_data(self):
        """Get form data"""
        return {
            'name': self.name_input.text().strip(),
            'category': self.category_input.currentText().strip(),  # Use currentText() for QComboBox
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
        
        title = QLabel("Products Management")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        header.addWidget(title)
        
        header.addStretch()
        
        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search products...")
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
        search_icon = get_icon('search')
        if not search_icon.isNull():
            # Note: QLineEdit doesn't directly support icons, but we can style it
            pass
        self.search_input.textChanged.connect(self.filter_table)
        header.addWidget(self.search_input)
        
        # Action buttons with icons
        btn_add = create_icon_button("Add Product", "add")
        btn_add.setFixedHeight(35)
        btn_add.setSizePolicy(btn_add.sizePolicy().horizontalPolicy(), btn_add.sizePolicy().verticalPolicy())
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
        btn_export_csv.setSizePolicy(btn_export_csv.sizePolicy().horizontalPolicy(), btn_export_csv.sizePolicy().verticalPolicy())
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
        btn_export_excel.setSizePolicy(btn_export_excel.sizePolicy().horizontalPolicy(), btn_export_excel.sizePolicy().verticalPolicy())
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
        
        self.total_value_card = self.create_summary_card("Total Inventory Value", "$0", "#16a085")
        self.avg_price_card = self.create_summary_card("Average Price", "$0", "#9b59b6")
        self.low_stock_card = self.create_summary_card("Low Stock Items", "0", "#f39c12")
        self.categories_card = self.create_summary_card("Categories", "0", "#34495e")
        
        summary_layout.addWidget(self.total_value_card, stretch=1)
        summary_layout.addWidget(self.avg_price_card, stretch=1)
        summary_layout.addWidget(self.low_stock_card, stretch=1)
        summary_layout.addWidget(self.categories_card, stretch=1)
        
        layout.addLayout(summary_layout)
        
        # Table with professional styling - set max height so it scrolls internally
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Category", "Quantity", "Unit Price", "Total Value"])
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
        """Refresh products table"""
        products = get_all_products()
        self.all_products = products
        self.populate_table(products)
        
        # Update summary cards
        total_value = get_total_inventory_value()
        avg_price = get_average_product_price()
        low_stock_count = len(get_low_stock_products())
        categories_data = get_products_by_category()
        categories_count = len(categories_data)
        
        self.update_card_value(self.total_value_card, f"${total_value:,.2f}")
        self.update_card_value(self.avg_price_card, f"${avg_price:.2f}")
        self.update_card_value(self.low_stock_card, str(low_stock_count))
        self.update_card_value(self.categories_card, str(categories_count))
    
    def update_card_value(self, card: QFrame, value: str):
        """Update the value in a summary card"""
        value_label = card.findChild(QLabel, "valueLabel")
        if value_label:
            value_label.setText(value)
    
    def populate_table(self, products):
        """Populate table with products"""
        self.table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            total_value = product['quantity'] * product['unit_price']
            self.table.setItem(row, 0, QTableWidgetItem(str(product['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(product['name']))
            self.table.setItem(row, 2, QTableWidgetItem(product['category'] or ''))
            self.table.setItem(row, 3, QTableWidgetItem(str(product['quantity'])))
            self.table.setItem(row, 4, QTableWidgetItem(f"${product['unit_price']:.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(f"${total_value:.2f}"))
            
            # Center align ID and numbers
            for col in [0, 3, 4, 5]:
                item = self.table.item(row, col)
                if item:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Highlight low stock items
            if product['quantity'] < 20:
                for col in range(6):
                    item = self.table.item(row, col)
                    if item:
                        item.setBackground(QColor("#fff3cd"))
    
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
                'Unit Price': p['unit_price'],
                'Total Value': p['quantity'] * p['unit_price']
            }
            for p in products
        ]
        
        headers = ['ID', 'Name', 'Category', 'Quantity', 'Unit Price', 'Total Value']
        
        if format_type == 'csv':
            if export_to_csv(export_data, headers, self):
                show_success_message(self, "Success", "Data exported to CSV successfully")
        elif format_type == 'excel':
            if export_to_excel(export_data, headers, self):
                show_success_message(self, "Success", "Data exported to Excel successfully")

