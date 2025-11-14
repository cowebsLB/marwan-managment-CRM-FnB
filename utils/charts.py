"""
Chart utilities for the CRM application
"""
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from typing import List, Tuple
import matplotlib.pyplot as plt


def create_waste_by_reason_chart(data: List[Tuple[str, int]]) -> FigureCanvasQTAgg:
    """Create a bar chart for waste by reason with percentages"""
    fig = Figure(figsize=(7, 5))
    ax = fig.add_subplot(111)
    
    if not data:
        ax.text(0.5, 0.5, 'No data available', 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
    else:
        # Filter out None values and ensure data is valid
        valid_data = [(str(item[0] or 'Unknown'), int(item[1] or 0)) for item in data if item[0] is not None]
        
        if not valid_data:
            ax.text(0.5, 0.5, 'No data available', 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
        else:
            reasons = [item[0] for item in valid_data]
            quantities = [item[1] for item in valid_data]
            
            # Calculate percentages
            total = sum(quantities) if quantities else 1
            percentages = [(q / total * 100) if total > 0 else 0 for q in quantities]
            
            # Truncate long reason names
            truncated_reasons = [reason[:15] + '...' if len(reason) > 15 else reason for reason in reasons]
            
            bars = ax.bar(truncated_reasons, quantities, color=['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6'], width=0.6)
            ax.set_xlabel('Reason', fontsize=10)
            ax.set_ylabel('Quantity', fontsize=10)
            ax.set_title('Waste by Reason', fontsize=12, fontweight='bold', pad=15)
            ax.tick_params(axis='x', rotation=45, labelsize=9)
            ax.tick_params(axis='y', labelsize=9)
            
            # Add value and percentage labels on bars
            for i, bar in enumerate(bars):
                height = bar.get_height()
                pct = percentages[i]
                ax.text(bar.get_x() + bar.get_width()/2., height + height*0.02,
                       f'{int(height)}\n({pct:.1f}%)',
                       ha='center', va='bottom', fontsize=8)
    
    fig.tight_layout(pad=2.5)
    canvas = FigureCanvasQTAgg(fig)
    return canvas


def create_pie_chart(data: List[Tuple[str, float]], title: str, colors: List[str] = None) -> FigureCanvasQTAgg:
    """Create a pie chart"""
    fig = Figure(figsize=(6, 5))
    ax = fig.add_subplot(111)
    
    if not data:
        ax.text(0.5, 0.5, 'No data available', 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
    else:
        # Filter out None values and ensure data is valid
        valid_data = [(str(item[0] or 'Unknown'), float(item[1] or 0)) for item in data if item[0] is not None]
        
        if not valid_data:
            ax.text(0.5, 0.5, 'No data available', 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
        else:
            labels = [item[0] for item in valid_data]
            values = [item[1] for item in valid_data]
            
            if colors is None:
                colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#34495e', '#e67e22']
            
            # Truncate long labels more aggressively
            truncated_labels = [label[:12] + '...' if len(label) > 12 else label for label in labels]
            
            # Use smaller font and adjust label distance
            ax.pie(values, labels=truncated_labels, autopct='%1.1f%%', startangle=90, 
                   colors=colors[:len(valid_data)], textprops={'fontsize': 8}, labeldistance=1.05)
            ax.set_title(title, fontsize=11, fontweight='bold', pad=10)
    
    fig.tight_layout(pad=1.5)
    canvas = FigureCanvasQTAgg(fig)
    canvas.setSizePolicy(canvas.sizePolicy().horizontalPolicy(), canvas.sizePolicy().verticalPolicy())
    return canvas


def create_bar_chart(data: List[Tuple[str, float]], title: str, xlabel: str, ylabel: str, 
                     color: str = '#3498db', horizontal: bool = False) -> FigureCanvasQTAgg:
    """Create a bar chart"""
    fig = Figure(figsize=(7, 5))
    ax = fig.add_subplot(111)
    
    if not data:
        ax.text(0.5, 0.5, 'No data available', 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
    else:
        # Filter out None values and ensure data is valid
        valid_data = [(str(item[0] or 'Unknown'), float(item[1] or 0)) for item in data if item[0] is not None]
        
        if not valid_data:
            ax.text(0.5, 0.5, 'No data available', 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
        else:
            labels = [item[0] for item in valid_data]
            values = [item[1] for item in valid_data]
        
            # Calculate percentages
            total = sum(values) if values else 1
            percentages = [(v / total * 100) if total > 0 else 0 for v in values]
            
            if horizontal:
                # Truncate long labels for horizontal bars
                truncated_labels = [label[:20] + '...' if len(label) > 20 else label for label in labels]
                bars = ax.barh(truncated_labels, values, color=color, height=0.6)
                ax.set_xlabel(xlabel, fontsize=10)
                ax.set_ylabel(ylabel, fontsize=10)
                ax.tick_params(axis='y', labelsize=9)
                # Add value and percentage labels
                for i, bar in enumerate(bars):
                    width = bar.get_width()
                    pct = percentages[i]
                    value_str = f'{width:.1f}' if isinstance(values[i], float) else f'{int(width)}'
                    ax.text(width + width*0.02, bar.get_y() + bar.get_height()/2.,
                           f'{value_str} ({pct:.1f}%)',
                           ha='left', va='center', fontsize=8)
            else:
                # Truncate long labels for vertical bars
                truncated_labels = [label[:12] + '...' if len(label) > 12 else label for label in labels]
                bars = ax.bar(truncated_labels, values, color=color, width=0.6)
                ax.set_xlabel(xlabel, fontsize=10)
                ax.set_ylabel(ylabel, fontsize=10)
                ax.tick_params(axis='x', rotation=45, labelsize=9)
                # Add value and percentage labels
                for i, bar in enumerate(bars):
                    height = bar.get_height()
                    pct = percentages[i]
                    value_str = f'{height:.1f}' if isinstance(height, float) else f'{int(height)}'
                    ax.text(bar.get_x() + bar.get_width()/2., height + height*0.02,
                           f'{value_str}\n({pct:.1f}%)',
                           ha='center', va='bottom', fontsize=8)
            
            ax.set_title(title, fontsize=12, fontweight='bold', pad=15)
    
    fig.tight_layout(pad=2.5)
    canvas = FigureCanvasQTAgg(fig)
    return canvas


def create_line_chart(data: List[Tuple[str, float]], title: str, xlabel: str, ylabel: str) -> FigureCanvasQTAgg:
    """Create a line chart"""
    fig = Figure(figsize=(7, 5))
    ax = fig.add_subplot(111)
    
    if not data:
        ax.text(0.5, 0.5, 'No data available', 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
    else:
        # Filter out None values and ensure data is valid
        valid_data = [(str(item[0] or ''), float(item[1] or 0)) for item in data if item[0] is not None]
        
        if not valid_data:
            ax.text(0.5, 0.5, 'No data available', 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
        else:
            labels = [item[0] for item in valid_data]
            values = [item[1] for item in valid_data]
        
            # Format date labels if they look like dates
            formatted_labels = []
            for label in labels:
                if len(label) == 10 and '-' in label:  # Date format YYYY-MM-DD
                    # Extract just the day part for cleaner display
                    formatted_labels.append(label.split('-')[2] + '/' + label.split('-')[1])
                else:
                    formatted_labels.append(label[:10] + '...' if len(label) > 10 else label)
            
            ax.plot(formatted_labels, values, marker='o', color='#3498db', linewidth=2, markersize=8)
            ax.set_xlabel(xlabel, fontsize=10)
            ax.set_ylabel(ylabel, fontsize=10)
            ax.set_title(title, fontsize=12, fontweight='bold', pad=15)
            ax.tick_params(axis='x', rotation=45, labelsize=9)
            ax.tick_params(axis='y', labelsize=9)
            ax.grid(True, alpha=0.3)
            
            # Add value labels with percentage change from previous point
            max_value = max(values) if values else 1
            offset = max_value * 0.05 if max_value > 0 else 1
            for i, (label, value) in enumerate(zip(formatted_labels, values)):
                value_label = f'{int(value)}'
                # Calculate percentage change from previous point
                if i > 0 and values[i-1] > 0:
                    pct_change = ((value - values[i-1]) / values[i-1]) * 100
                    if abs(pct_change) > 0.1:  # Only show if change is significant
                        value_label += f'\n({pct_change:+.1f}%)'
                elif i == 0 and len(values) > 1 and values[1] > 0:
                    # Show percentage of total for first point
                    total = sum(values)
                    pct = (value / total * 100) if total > 0 else 0
                    value_label += f'\n({pct:.1f}%)'
                ax.text(i, value + offset, value_label, ha='center', va='bottom', fontsize=8)
    
    fig.tight_layout(pad=2.5)
    canvas = FigureCanvasQTAgg(fig)
    return canvas

