"""
Dashboard page for the CRM application
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from database.db import (
    get_products_count, get_total_waste_quantity, get_total_asset_value, get_waste_by_reason,
    get_total_inventory_value, get_average_product_price, get_low_stock_products,
    get_products_by_category, get_inventory_value_by_category, get_waste_by_item,
    get_waste_trend, get_assets_by_type, get_assets_value_by_type, get_average_asset_value
)
from utils.charts import (
    create_waste_by_reason_chart, create_pie_chart, create_bar_chart, create_line_chart
)


class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.refresh()
    
    def init_ui(self):
        """Initialize the dashboard UI"""
        # Create scroll area for better navigation
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Dashboard Overview")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Primary Metrics cards (Row 1)
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(15)
        
        self.products_card = self.create_metric_card("Total Products", "0", "#3498db", "📦")
        self.inventory_value_card = self.create_metric_card("Inventory Value", "$0", "#16a085", "💰")
        self.waste_card = self.create_metric_card("Total Waste", "0", "#e74c3c", "🗑️")
        self.assets_card = self.create_metric_card("Total Asset Value", "$0", "#2ecc71", "🏢")
        
        metrics_layout.addWidget(self.products_card, stretch=1)
        metrics_layout.addWidget(self.inventory_value_card, stretch=1)
        metrics_layout.addWidget(self.waste_card, stretch=1)
        metrics_layout.addWidget(self.assets_card, stretch=1)
        
        layout.addLayout(metrics_layout)
        
        # Secondary Metrics cards (Row 2)
        metrics_layout2 = QHBoxLayout()
        metrics_layout2.setSpacing(15)
        
        self.avg_price_card = self.create_metric_card("Avg Product Price", "$0", "#9b59b6", "💵")
        self.low_stock_card = self.create_metric_card("Low Stock Items", "0", "#f39c12", "⚠️")
        self.avg_asset_card = self.create_metric_card("Avg Asset Value", "$0", "#1abc9c", "📊")
        self.categories_card = self.create_metric_card("Categories", "0", "#34495e", "📁")
        
        metrics_layout2.addWidget(self.avg_price_card, stretch=1)
        metrics_layout2.addWidget(self.low_stock_card, stretch=1)
        metrics_layout2.addWidget(self.avg_asset_card, stretch=1)
        metrics_layout2.addWidget(self.categories_card, stretch=1)
        
        layout.addLayout(metrics_layout2)
        
        # Charts section - Row 1
        charts_layout1 = QHBoxLayout()
        charts_layout1.setSpacing(20)
        
        # Products by Category (Pie Chart)
        chart_frame1 = QFrame()
        chart_frame1.setObjectName("chartFrame")
        chart_frame1.setStyleSheet("""
            QFrame#chartFrame {
                background-color: white;
                border: 1px solid #e1e8ed;
                border-radius: 8px;
            }
        """)
        chart_layout1 = QVBoxLayout(chart_frame1)
        chart_layout1.setContentsMargins(20, 20, 20, 20)
        
        chart_title1 = QLabel("Products by Category")
        chart_title1.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        chart_title1.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        chart_layout1.addWidget(chart_title1)
        
        self.category_chart_container = QWidget()
        self.category_chart_container.setMinimumHeight(350)
        chart_layout1.addWidget(self.category_chart_container)
        
        # Inventory Value by Category
        chart_frame2 = QFrame()
        chart_frame2.setObjectName("chartFrame")
        chart_frame2.setStyleSheet("""
            QFrame#chartFrame {
                background-color: white;
                border: 1px solid #e1e8ed;
                border-radius: 8px;
            }
        """)
        chart_layout2 = QVBoxLayout(chart_frame2)
        chart_layout2.setContentsMargins(20, 20, 20, 20)
        
        chart_title2 = QLabel("Inventory Value by Category")
        chart_title2.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        chart_title2.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        chart_layout2.addWidget(chart_title2)
        
        self.inventory_value_chart_container = QWidget()
        self.inventory_value_chart_container.setMinimumHeight(350)
        chart_layout2.addWidget(self.inventory_value_chart_container)
        
        charts_layout1.addWidget(chart_frame1, stretch=1)
        charts_layout1.addWidget(chart_frame2, stretch=1)
        layout.addLayout(charts_layout1)
        
        # Charts section - Row 2
        charts_layout2 = QHBoxLayout()
        charts_layout2.setSpacing(20)
        
        # Waste by Reason
        chart_frame3 = QFrame()
        chart_frame3.setObjectName("chartFrame")
        chart_frame3.setStyleSheet("""
            QFrame#chartFrame {
                background-color: white;
                border: 1px solid #e1e8ed;
                border-radius: 8px;
            }
        """)
        chart_layout3 = QVBoxLayout(chart_frame3)
        chart_layout3.setContentsMargins(20, 20, 20, 20)
        
        chart_title3 = QLabel("Waste by Reason")
        chart_title3.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        chart_title3.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        chart_layout3.addWidget(chart_title3)
        
        self.waste_reason_chart_container = QWidget()
        self.waste_reason_chart_container.setMinimumHeight(350)
        chart_layout3.addWidget(self.waste_reason_chart_container)
        
        # Waste Trend (Line Chart)
        chart_frame4 = QFrame()
        chart_frame4.setObjectName("chartFrame")
        chart_frame4.setStyleSheet("""
            QFrame#chartFrame {
                background-color: white;
                border: 1px solid #e1e8ed;
                border-radius: 8px;
            }
        """)
        chart_layout4 = QVBoxLayout(chart_frame4)
        chart_layout4.setContentsMargins(20, 20, 20, 20)
        
        chart_title4 = QLabel("Waste Trend (Last 7 Days)")
        chart_title4.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        chart_title4.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        chart_layout4.addWidget(chart_title4)
        
        self.waste_trend_chart_container = QWidget()
        self.waste_trend_chart_container.setMinimumHeight(350)
        chart_layout4.addWidget(self.waste_trend_chart_container)
        
        charts_layout2.addWidget(chart_frame3, stretch=1)
        charts_layout2.addWidget(chart_frame4, stretch=1)
        layout.addLayout(charts_layout2)
        
        # Charts section - Row 3
        charts_layout3 = QHBoxLayout()
        charts_layout3.setSpacing(20)
        
        # Assets by Type
        chart_frame5 = QFrame()
        chart_frame5.setObjectName("chartFrame")
        chart_frame5.setStyleSheet("""
            QFrame#chartFrame {
                background-color: white;
                border: 1px solid #e1e8ed;
                border-radius: 8px;
            }
        """)
        chart_layout5 = QVBoxLayout(chart_frame5)
        chart_layout5.setContentsMargins(20, 20, 20, 20)
        
        chart_title5 = QLabel("Assets by Type")
        chart_title5.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        chart_title5.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        chart_layout5.addWidget(chart_title5)
        
        self.assets_type_chart_container = QWidget()
        self.assets_type_chart_container.setMinimumHeight(350)
        chart_layout5.addWidget(self.assets_type_chart_container)
        
        # Asset Value by Type
        chart_frame6 = QFrame()
        chart_frame6.setObjectName("chartFrame")
        chart_frame6.setStyleSheet("""
            QFrame#chartFrame {
                background-color: white;
                border: 1px solid #e1e8ed;
                border-radius: 8px;
            }
        """)
        chart_layout6 = QVBoxLayout(chart_frame6)
        chart_layout6.setContentsMargins(20, 20, 20, 20)
        
        chart_title6 = QLabel("Asset Value by Type")
        chart_title6.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        chart_title6.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        chart_layout6.addWidget(chart_title6)
        
        self.assets_value_chart_container = QWidget()
        self.assets_value_chart_container.setMinimumHeight(350)
        chart_layout6.addWidget(self.assets_value_chart_container)
        
        charts_layout3.addWidget(chart_frame5, stretch=1)
        charts_layout3.addWidget(chart_frame6, stretch=1)
        layout.addLayout(charts_layout3)
        
        layout.addStretch()
        
        scroll.setWidget(content_widget)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def create_metric_card(self, title: str, value: str, color: str, icon: str = "") -> QFrame:
        """Create a professional metric card widget"""
        card = QFrame()
        card.setObjectName("metricCard")
        card.setFixedHeight(140)
        card.setStyleSheet(f"""
            QFrame#metricCard {{
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e1e8ed;
            }}
            QFrame#metricCard:hover {{
                border: 2px solid {color};
                box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.15);
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(8)
        
        # Header with icon and title
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        if icon:
            icon_label = QLabel(icon)
            icon_label.setFont(QFont("Segoe UI", 16))
            icon_label.setStyleSheet(f"color: {color};")
            header_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 10))
        title_label.setStyleSheet("color: #7f8c8d; font-weight: 500;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {color};")
        value_label.setObjectName("valueLabel")
        layout.addWidget(value_label)
        
        layout.addStretch()
        
        return card
    
    def refresh(self):
        """Refresh dashboard data"""
        # Update primary metrics
        products_count = get_products_count()
        total_inventory_value = get_total_inventory_value()
        total_waste = get_total_waste_quantity()
        total_assets = get_total_asset_value()
        
        # Update secondary metrics
        avg_price = get_average_product_price()
        low_stock_count = len(get_low_stock_products())
        avg_asset_value = get_average_asset_value()
        categories_data = get_products_by_category()
        categories_count = len(categories_data)
        
        # Update primary cards
        self.update_card_value(self.products_card, str(products_count))
        self.update_card_value(self.inventory_value_card, f"${total_inventory_value:,.2f}")
        self.update_card_value(self.waste_card, str(total_waste))
        self.update_card_value(self.assets_card, f"${total_assets:,.2f}")
        
        # Update secondary cards
        self.update_card_value(self.avg_price_card, f"${avg_price:.2f}")
        self.update_card_value(self.low_stock_card, str(low_stock_count))
        self.update_card_value(self.avg_asset_card, f"${avg_asset_value:,.2f}")
        self.update_card_value(self.categories_card, str(categories_count))
        
        # Update charts
        self.update_category_chart()
        self.update_inventory_value_chart()
        self.update_waste_reason_chart()
        self.update_waste_trend_chart()
        self.update_assets_type_chart()
        self.update_assets_value_chart()
    
    def update_card_value(self, card: QFrame, value: str):
        """Update the value in a metric card"""
        value_label = card.findChild(QLabel, "valueLabel")
        if value_label:
            value_label.setText(value)
    
    def update_category_chart(self):
        """Update products by category chart"""
        data = get_products_by_category()
        self.update_chart_container(self.category_chart_container, 
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
            layout.addWidget(chart)
        except Exception as e:
            # If chart creation fails, show error message
            error_label = QLabel(f"Unable to load chart")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setStyleSheet("color: #7f8c8d; padding: 20px;")
            layout.addWidget(error_label)

