"""
Dashboard page for the CRM application
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from database.db import get_products_count, get_total_waste_quantity, get_total_asset_value, get_waste_by_reason
from utils.charts import create_waste_by_reason_chart


class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.refresh()
    
    def init_ui(self):
        """Initialize the dashboard UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Dashboard Overview")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Metrics cards
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(20)
        
        self.products_card = self.create_metric_card("Total Products", "0", "#3498db")
        self.waste_card = self.create_metric_card("Total Waste", "0", "#e74c3c")
        self.assets_card = self.create_metric_card("Total Asset Value", "$0", "#2ecc71")
        
        metrics_layout.addWidget(self.products_card)
        metrics_layout.addWidget(self.waste_card)
        metrics_layout.addWidget(self.assets_card)
        
        layout.addLayout(metrics_layout)
        
        # Charts section
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(20)
        
        # Waste by reason chart
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
        
        chart_title = QLabel("Waste by Reason")
        chart_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        chart_title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        chart_layout.addWidget(chart_title)
        
        self.chart_container = QWidget()
        chart_layout.addWidget(self.chart_container)
        
        charts_layout.addWidget(chart_frame, stretch=1)
        layout.addLayout(charts_layout)
        
        layout.addStretch()
    
    def create_metric_card(self, title: str, value: str, color: str) -> QFrame:
        """Create a professional metric card widget"""
        card = QFrame()
        card.setObjectName("metricCard")
        card.setFixedHeight(160)
        card.setStyleSheet(f"""
            QFrame#metricCard {{
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e1e8ed;
            }}
            QFrame#metricCard:hover {{
                border: 1px solid {color};
                box-shadow: 0px 2px 8px rgba(0, 0, 0, 0.1);
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 11))
        title_label.setStyleSheet("color: #7f8c8d; font-weight: 500;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 36, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {color};")
        value_label.setObjectName("valueLabel")
        layout.addWidget(value_label)
        
        layout.addStretch()
        
        return card
    
    def refresh(self):
        """Refresh dashboard data"""
        # Update metrics
        products_count = get_products_count()
        total_waste = get_total_waste_quantity()
        total_assets = get_total_asset_value()
        
        # Update cards
        products_card = self.products_card.findChild(QLabel, "valueLabel")
        if products_card:
            products_card.setText(str(products_count))
        
        waste_card = self.waste_card.findChild(QLabel, "valueLabel")
        if waste_card:
            waste_card.setText(str(total_waste))
        
        assets_card = self.assets_card.findChild(QLabel, "valueLabel")
        if assets_card:
            assets_card.setText(f"${total_assets:,.2f}")
        
        # Update chart
        waste_data = get_waste_by_reason()
        self.update_chart(waste_data)
    
    def update_chart(self, data):
        """Update the waste by reason chart"""
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
        chart = create_waste_by_reason_chart(data)
        layout.addWidget(chart)

