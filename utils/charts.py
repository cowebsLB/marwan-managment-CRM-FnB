"""
Chart utilities for the CRM application
"""
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from typing import List, Tuple


def create_waste_by_reason_chart(data: List[Tuple[str, int]]) -> FigureCanvasQTAgg:
    """Create a bar chart for waste by reason"""
    fig = Figure(figsize=(8, 5))
    ax = fig.add_subplot(111)
    
    if not data:
        ax.text(0.5, 0.5, 'No data available', 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
    else:
        reasons = [item[0] for item in data]
        quantities = [item[1] for item in data]
        
        bars = ax.bar(reasons, quantities, color=['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6'])
        ax.set_xlabel('Reason', fontsize=10)
        ax.set_ylabel('Quantity', fontsize=10)
        ax.set_title('Waste by Reason', fontsize=12, fontweight='bold')
        ax.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontsize=9)
    
    fig.tight_layout()
    canvas = FigureCanvasQTAgg(fig)
    return canvas

