"""
Analytics page for the CRM application
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from database.db import (
    get_products_by_category, get_inventory_value_by_category,
    get_waste_by_reason, get_waste_by_item, get_waste_trend,
    get_assets_by_type, get_assets_by_condition, get_assets_value_by_type
)
from utils.charts import (
    create_pie_chart, create_bar_chart, create_line_chart, create_waste_by_reason_chart
)


class AnalyticsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.refresh()
    
    def init_ui(self):
        """Initialize the analytics UI"""
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
        
        # Title
        title = QLabel("Analytics & Reports")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Products Analytics Section
        products_section = self.create_section_header("Products Analytics")
        layout.addWidget(products_section)
        
        # Products charts - Row 1
        products_charts1 = QHBoxLayout()
        products_charts1.setSpacing(20)
        
        # Products by Category
        chart_frame1, chart_layout1 = self.create_chart_frame("Products by Category")
        self.products_category_chart_container = QWidget()
        self.products_category_chart_container.setMinimumHeight(350)
        chart_layout1.addWidget(self.products_category_chart_container)
        products_charts1.addWidget(chart_frame1, stretch=1)
        
        # Inventory Value by Category
        chart_frame2, chart_layout2 = self.create_chart_frame("Inventory Value by Category")
        self.inventory_value_chart_container = QWidget()
        self.inventory_value_chart_container.setMinimumHeight(350)
        chart_layout2.addWidget(self.inventory_value_chart_container)
        products_charts1.addWidget(chart_frame2, stretch=1)
        
        layout.addLayout(products_charts1)
        
        # Waste Analytics Section
        waste_section = self.create_section_header("Waste Analytics")
        layout.addWidget(waste_section)
        
        # Waste charts - Row 1
        waste_charts1 = QHBoxLayout()
        waste_charts1.setSpacing(20)
        
        # Waste by Reason
        chart_frame3, chart_layout3 = self.create_chart_frame("Waste by Reason")
        self.waste_reason_chart_container = QWidget()
        self.waste_reason_chart_container.setMinimumHeight(350)
        chart_layout3.addWidget(self.waste_reason_chart_container)
        waste_charts1.addWidget(chart_frame3, stretch=1)
        
        # Top Wasted Items
        chart_frame4, chart_layout4 = self.create_chart_frame("Top Wasted Items")
        self.waste_item_chart_container = QWidget()
        self.waste_item_chart_container.setMinimumHeight(350)
        chart_layout4.addWidget(self.waste_item_chart_container)
        waste_charts1.addWidget(chart_frame4, stretch=1)
        
        layout.addLayout(waste_charts1)
        
        # Waste Trend Chart
        waste_charts2 = QHBoxLayout()
        waste_charts2.setSpacing(20)
        
        chart_frame5, chart_layout5 = self.create_chart_frame("Waste Trend (Last 7 Days)")
        self.waste_trend_chart_container = QWidget()
        self.waste_trend_chart_container.setMinimumHeight(350)
        chart_layout5.addWidget(self.waste_trend_chart_container)
        waste_charts2.addWidget(chart_frame5, stretch=1)
        waste_charts2.addStretch()  # Add empty space on the right
        
        layout.addLayout(waste_charts2)
        
        # Assets Analytics Section
        assets_section = self.create_section_header("Assets Analytics")
        layout.addWidget(assets_section)
        
        # Assets charts - Row 1
        assets_charts1 = QHBoxLayout()
        assets_charts1.setSpacing(20)
        
        # Assets by Type
        chart_frame6, chart_layout6 = self.create_chart_frame("Assets by Type")
        self.assets_type_chart_container = QWidget()
        self.assets_type_chart_container.setMinimumHeight(350)
        chart_layout6.addWidget(self.assets_type_chart_container)
        assets_charts1.addWidget(chart_frame6, stretch=1)
        
        # Assets by Condition
        chart_frame7, chart_layout7 = self.create_chart_frame("Assets by Condition")
        self.assets_condition_chart_container = QWidget()
        self.assets_condition_chart_container.setMinimumHeight(350)
        chart_layout7.addWidget(self.assets_condition_chart_container)
        assets_charts1.addWidget(chart_frame7, stretch=1)
        
        layout.addLayout(assets_charts1)
        
        # Asset Value by Type
        assets_charts2 = QHBoxLayout()
        assets_charts2.setSpacing(20)
        
        chart_frame8, chart_layout8 = self.create_chart_frame("Asset Value by Type")
        self.assets_value_chart_container = QWidget()
        self.assets_value_chart_container.setMinimumHeight(350)
        chart_layout8.addWidget(self.assets_value_chart_container)
        assets_charts2.addWidget(chart_frame8, stretch=1)
        assets_charts2.addStretch()  # Add empty space on the right
        
        layout.addLayout(assets_charts2)
        
        layout.addStretch()
        
        scroll.setWidget(content_widget)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def create_section_header(self, title: str) -> QLabel:
        """Create a section header label"""
        header = QLabel(title)
        header.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header.setStyleSheet("color: #34495e; margin-top: 20px; margin-bottom: 10px; padding-top: 10px; border-top: 2px solid #e1e8ed;")
        return header
    
    def create_chart_frame(self, title: str):
        """Create a chart frame with title"""
        chart_frame = QFrame()
        chart_frame.setObjectName("chartFrame")
        chart_frame.setStyleSheet("""
            QFrame#chartFrame {
                background-color: white;
                border: 1px solid #e1e8ed;
                border-radius: 8px;
            }
        """)
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(20, 20, 20, 20)
        
        chart_title = QLabel(title)
        chart_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        chart_title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        chart_layout.addWidget(chart_title)
        
        return chart_frame, chart_layout
    
    def refresh(self):
        """Refresh all analytics charts"""
        # Products charts
        self.update_products_category_chart()
        self.update_inventory_value_chart()
        
        # Waste charts
        self.update_waste_reason_chart()
        self.update_waste_item_chart()
        self.update_waste_trend_chart()
        
        # Assets charts
        self.update_assets_type_chart()
        self.update_assets_condition_chart()
        self.update_assets_value_chart()
    
    def update_products_category_chart(self):
        """Update products by category chart"""
        data = get_products_by_category()
        self.update_chart_container(self.products_category_chart_container,
                                   lambda: create_pie_chart(data, "Products by Category"))
    
    def update_inventory_value_chart(self):
        """Update inventory value by category chart"""
        data = get_inventory_value_by_category()
        self.update_chart_container(self.inventory_value_chart_container,
                                   lambda: create_bar_chart(data, "Inventory Value by Category",
                                                           "Category", "Value ($)", "#16a085", horizontal=True))
    
    def update_waste_reason_chart(self):
        """Update waste by reason chart"""
        data = get_waste_by_reason()
        self.update_chart_container(self.waste_reason_chart_container,
                                   lambda: create_waste_by_reason_chart(data))
    
    def update_waste_item_chart(self):
        """Update waste by item chart"""
        data = get_waste_by_item()
        self.update_chart_container(self.waste_item_chart_container,
                                   lambda: create_bar_chart(data, "Top Wasted Items",
                                                           "Item", "Quantity", "#e74c3c", horizontal=True))
    
    def update_waste_trend_chart(self):
        """Update waste trend chart"""
        data = get_waste_trend()
        # Reverse to show chronological order
        data = list(reversed(data))
        self.update_chart_container(self.waste_trend_chart_container,
                                   lambda: create_line_chart(data, "Waste Trend", "Date", "Quantity"))
    
    def update_assets_type_chart(self):
        """Update assets by type chart"""
        data = get_assets_by_type()
        self.update_chart_container(self.assets_type_chart_container,
                                   lambda: create_pie_chart(data, "Assets by Type"))
    
    def update_assets_condition_chart(self):
        """Update assets by condition chart"""
        data = get_assets_by_condition()
        self.update_chart_container(self.assets_condition_chart_container,
                                   lambda: create_pie_chart(data, "Assets by Condition"))
    
    def update_assets_value_chart(self):
        """Update asset value by type chart"""
        data = get_assets_value_by_type()
        self.update_chart_container(self.assets_value_chart_container,
                                   lambda: create_bar_chart(data, "Asset Value by Type",
                                                           "Type", "Value ($)", "#2ecc71", horizontal=True))
    
    def update_chart_container(self, container: QWidget, chart_creator):
        """Update a chart container with a new chart"""
        layout = container.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        else:
            layout = QVBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
        
        try:
            chart = chart_creator()
            if chart:
                layout.addWidget(chart)
            else:
                raise ValueError("Chart creator returned None")
        except Exception as e:
            # If chart creation fails, show error message with details
            import traceback
            error_msg = f"Unable to load chart\n{str(e)}"
            print(f"Chart error: {error_msg}")
            print(traceback.format_exc())
            error_label = QLabel(error_msg)
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setWordWrap(True)
            error_label.setStyleSheet("color: #e74c3c; padding: 20px; font-size: 11px;")
            layout.addWidget(error_label)

