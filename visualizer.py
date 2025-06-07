import matplotlib.pyplot as plt
import pandas as pd
from typing import List, Dict
import numpy as np

class PopulationVisualizer:
    def __init__(self):
        plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
        
    def create_comparison_chart(self, countries_data: pd.DataFrame, metric: str = 'Population'):
        """Create a comparison chart for selected countries"""
        if countries_data.empty or metric not in countries_data.columns:
            print("No data available for visualization")
            return
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        countries = countries_data['Country'].tolist()
        values = countries_data[metric].tolist()
        
        # Create color palette
        colors = plt.cm.Set3(np.linspace(0, 1, len(countries)))
        
        bars = ax.bar(countries, values, color=colors, alpha=0.8, edgecolor='black', linewidth=1)
        
        # Customize the chart
        ax.set_title(f'{metric} Comparison', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Countries', fontsize=12, fontweight='bold')
        ax.set_ylabel(self._get_ylabel(metric), fontsize=12, fontweight='bold')
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45, ha='right')
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   self._format_number(value, metric),
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # Add grid for better readability
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        plt.tight_layout()
        plt.show()
    
    def create_multi_metric_comparison(self, countries_data: pd.DataFrame, metrics: List[str]):
        """Create a multi-metric comparison chart"""
        if countries_data.empty:
            print("No data available for visualization")
            return
        
        # Filter metrics that exist in the data
        available_metrics = [m for m in metrics if m in countries_data.columns]
        if not available_metrics:
            print("No valid metrics found for comparison")
            return
        
        countries = countries_data['Country'].tolist()
        
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        axes = axes.flatten()
        
        colors = plt.cm.Set2(np.linspace(0, 1, len(countries)))
        
        for i, metric in enumerate(available_metrics[:4]):  # Limit to 4 metrics
            if i >= len(axes):
                break
                
            ax = axes[i]
            values = countries_data[metric].tolist()
            
            bars = ax.bar(countries, values, color=colors, alpha=0.8, edgecolor='black')
            ax.set_title(f'{metric}', fontsize=14, fontweight='bold')
            ax.set_xlabel('Countries', fontsize=10)
            ax.set_ylabel(self._get_ylabel(metric), fontsize=10)
            
            # Rotate labels
            ax.tick_params(axis='x', rotation=45, labelsize=9)
            
            # Add value labels
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       self._format_number(value, metric),
                       ha='center', va='bottom', fontsize=8)
            
            ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Hide unused subplots
        for i in range(len(available_metrics), len(axes)):
            axes[i].set_visible(False)
        
        plt.suptitle('Multi-Metric Country Comparison', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.show()
    
    def create_top_countries_chart(self, data: pd.DataFrame, n: int = 10, metric: str = 'Population'):
        """Create a chart showing top N countries by metric"""
        if data.empty or metric not in data.columns:
            print("No data available for visualization")
            return
        
        top_data = data.nlargest(n, metric)
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        countries = top_data['Country'].tolist()
        values = top_data[metric].tolist()
        
        # Create horizontal bar chart for better country name visibility
        colors = plt.cm.viridis(np.linspace(0, 1, len(countries)))
        bars = ax.barh(countries, values, color=colors, alpha=0.8, edgecolor='black')
        
        ax.set_title(f'Top {n} Countries by {metric}', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel(self._get_ylabel(metric), fontsize=12, fontweight='bold')
        ax.set_ylabel('Countries', fontsize=12, fontweight='bold')
        
        # Add value labels
        for bar, value in zip(bars, values):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                   self._format_number(value, metric),
                   ha='left', va='center', fontsize=10, fontweight='bold')
        
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        plt.tight_layout()
        plt.show()
    
    def create_scatter_plot(self, data: pd.DataFrame, x_metric: str, y_metric: str, countries: List[str] = None):
        """Create a scatter plot comparing two metrics"""
        if data.empty or x_metric not in data.columns or y_metric not in data.columns:
            print("No data available for scatter plot")
            return
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Filter data if specific countries are provided
        if countries:
            plot_data = data[data['Country'].isin(countries)]
        else:
            plot_data = data.head(20)  # Show top 20 countries
        
        x_values = plot_data[x_metric]
        y_values = plot_data[y_metric]
        
        scatter = ax.scatter(x_values, y_values, c=range(len(plot_data)), 
                           cmap='viridis', alpha=0.7, s=100, edgecolor='black')
        
        # Add country labels
        for i, country in enumerate(plot_data['Country']):
            ax.annotate(country, (x_values.iloc[i], y_values.iloc[i]), 
                       xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        ax.set_title(f'{y_metric} vs {x_metric}', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel(self._get_ylabel(x_metric), fontsize=12, fontweight='bold')
        ax.set_ylabel(self._get_ylabel(y_metric), fontsize=12, fontweight='bold')
        
        ax.grid(True, alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        plt.show()
    
    def _get_ylabel(self, metric: str) -> str:
        """Get appropriate y-axis label for metric"""
        labels = {
            'Population': 'Population',
            'Yearly_Change': 'Yearly Change (%)',
            'Net_Change': 'Net Change',
            'Density': 'Density (People/km²)',
            'Land_Area': 'Land Area (km²)',
            'Net_Migration': 'Net Migration',
            'Fertility_Rate': 'Fertility Rate',
            'Median_Age': 'Median Age (years)',
            'Urban_Population_Percent': 'Urban Population (%)',
            'World_Share': 'World Share (%)'
        }
        return labels.get(metric, metric)
    
    def _format_number(self, value, metric: str) -> str:
        """Format numbers for display"""
        if pd.isna(value):
            return 'N/A'
        
        if metric in ['Population', 'Net_Change', 'Land_Area', 'Net_Migration']:
            if abs(value) >= 1e9:
                return f'{value/1e9:.1f}B'
            elif abs(value) >= 1e6:
                return f'{value/1e6:.1f}M'
            elif abs(value) >= 1e3:
                return f'{value/1e3:.1f}K'
            else:
                return f'{int(value)}'
        elif metric in ['Yearly_Change', 'Urban_Population_Percent', 'World_Share']:
            return f'{value:.1f}%'
        elif metric in ['Fertility_Rate', 'Median_Age']:
            return f'{value:.1f}'
        elif metric == 'Density':
            return f'{int(value)}'
        else:
            return str(value)