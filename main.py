import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scraper import PopulationScraper
from visualizer import PopulationVisualizer

class PopulationExplorerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Population Data Explorer")
        self.root.geometry("1000x700")
        
        self.scraper = PopulationScraper()
        self.visualizer = PopulationVisualizer()
        self.data = None
        self.selected_countries = []
        
        # Configure styles
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TButton', font=('Arial', 10), padding=5)
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        
        self.create_widgets()
        self.load_data()
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.header_frame, text="🌍 Population Data Explorer", style='Header.TLabel').pack(side=tk.LEFT)
        
        # Status label
        self.status_label = ttk.Label(self.header_frame, text="Loading data...")
        self.status_label.pack(side=tk.RIGHT)
        
        # Left panel - controls
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Search section
        search_frame = ttk.LabelFrame(self.control_frame, text="Search Country", padding=10)
        search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_frame, text="Country Name:").grid(row=0, column=0, sticky=tk.W)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.grid(row=0, column=1, sticky=tk.EW, padx=5)
        self.search_entry.bind('<Return>', lambda e: self.search_country())
        
        ttk.Button(search_frame, text="Search", command=self.search_country).grid(row=0, column=2)
        ttk.Button(search_frame, text="Add to Compare", command=self.add_from_search).grid(row=1, column=0, columnspan=3, pady=(5,0), sticky=tk.EW)
        
        # Compare section
        compare_frame = ttk.LabelFrame(self.control_frame, text="Compare Countries", padding=10)
        compare_frame.pack(fill=tk.X, pady=5)
        
        self.compare_listbox = tk.Listbox(compare_frame, height=8, selectmode=tk.MULTIPLE)
        self.compare_listbox.pack(fill=tk.BOTH, expand=True)
        
        button_frame = ttk.Frame(compare_frame)
        button_frame.pack(fill=tk.X, pady=(5,0))
        
        ttk.Button(button_frame, text="Visualize", command=self.visualize_comparison).pack(side=tk.LEFT, expand=True)
        ttk.Button(button_frame, text="Remove", command=self.remove_from_comparison).pack(side=tk.LEFT, expand=True, padx=5)
        ttk.Button(button_frame, text="Clear All", command=self.clear_comparison_list).pack(side=tk.LEFT, expand=True)
        
        # Top countries section
        top_frame = ttk.LabelFrame(self.control_frame, text="Top Countries", padding=10)
        top_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(top_frame, text="Metric:").grid(row=0, column=0, sticky=tk.W)
        self.top_metric_var = tk.StringVar()
        self.top_metric_combo = ttk.Combobox(top_frame, textvariable=self.top_metric_var, 
                                           values=['Population', 'Yearly_Change', 'Density', 'Land_Area', 
                                                  'Fertility_Rate', 'Median_Age', 'Urban_Population_Percent'])
        self.top_metric_combo.grid(row=0, column=1, sticky=tk.EW, padx=5)
        self.top_metric_combo.current(0)
        
        ttk.Label(top_frame, text="Count:").grid(row=1, column=0, sticky=tk.W)
        self.top_count_var = tk.StringVar(value="10")
        ttk.Entry(top_frame, textvariable=self.top_count_var, width=5).grid(row=1, column=1, sticky=tk.W, padx=5)
        
        ttk.Button(top_frame, text="Show Top", command=self.show_top_countries).grid(row=2, column=0, columnspan=2, pady=(5,0), sticky=tk.EW)
        
        # Export section
        export_frame = ttk.Frame(self.control_frame)
        export_frame.pack(fill=tk.X, pady=(10,0))
        
        ttk.Button(export_frame, text="Export Data", command=self.export_data).pack(side=tk.LEFT, expand=True)
        ttk.Button(export_frame, text="Exit", command=self.root.quit).pack(side=tk.LEFT, expand=True, padx=5)
        
        # Right panel - display area
        self.display_frame = ttk.Frame(self.main_frame)
        self.display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Country info display
        self.info_text = tk.Text(self.display_frame, wrap=tk.WORD, state=tk.DISABLED, 
                                font=('Arial', 10), padx=10, pady=10)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # Matplotlib canvas (initially hidden)
        self.figure = None
        self.canvas = None
    
    def load_data(self):
        """Load data from scraper"""
        try:
            self.data = self.scraper.scrape_data()
            if self.data is not None and not self.data.empty:
                self.status_label.config(text=f"Loaded {len(self.data)} countries")
            else:
                self.status_label.config(text="Using fallback data")
                messagebox.showwarning("Warning", "Failed to load live data. Using fallback dataset.")
        except Exception as e:
            self.status_label.config(text="Error loading data")
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
    
    def search_country(self):
        """Search for a country and display its information"""
        country_name = self.search_entry.get().strip()
        if not country_name:
            messagebox.showwarning("Warning", "Please enter a country name")
            return
        
        result = self.scraper.search_country(country_name)
        
        if result is not None:
            self.display_country_info(result)
        else:
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, f"Country '{country_name}' not found.\n\n")
            
            # Show suggestions
            suggestions = self.data[self.data['Country'].str.contains(country_name, case=False, na=False)]
            if not suggestions.empty:
                self.info_text.insert(tk.END, "Did you mean:\n")
                for country in suggestions['Country'].head(5):
                    self.info_text.insert(tk.END, f"• {country}\n")
            
            self.info_text.config(state=tk.DISABLED)
    
    def display_country_info(self, country_data):
        """Display country information in the text widget"""
        self.clear_plot()  # Clear any existing plot
        
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        
        # Format the country information
        info = f"🏳️  {country_data['Country']}\n"
        info += "=" * 40 + "\n\n"
        
        metrics = [
            ('Rank', f"#{int(country_data['Rank'])}"),
            ('Population', f"{int(country_data['Population']):,}"),
            ('Yearly Change', f"{country_data['Yearly_Change']:.2f}%"),
            ('Net Change', f"{int(country_data['Net_Change']):,}"),
            ('Density', f"{int(country_data['Density']):,} people/km²"),
            ('Land Area', f"{int(country_data['Land_Area']):,} km²"),
            ('Net Migration', f"{int(country_data['Net_Migration']):,}"),
            ('Fertility Rate', f"{country_data['Fertility_Rate']:.2f}"),
            ('Median Age', f"{country_data['Median_Age']:.1f} years"),
            ('Urban Population', f"{country_data['Urban_Population_Percent']:.1f}%"),
            ('World Share', f"{country_data['World_Share']:.2f}%")
        ]
        
        for name, value in metrics:
            info += f"{name:<15}: {value}\n"
        
        self.info_text.insert(tk.END, info)
        self.info_text.config(state=tk.DISABLED)
    
    def add_from_search(self):
        """Add the currently searched country to comparison"""
        country_name = self.search_entry.get().strip()
        if not country_name:
            messagebox.showwarning("Warning", "Please search for a country first")
            return
        
        result = self.scraper.search_country(country_name)
        if result is not None:
            self.add_to_comparison(result['Country'])
        else:
            messagebox.showwarning("Warning", f"Country '{country_name}' not found")
    
    def add_to_comparison(self, country_name):
        """Add a country to the comparison list"""
        if country_name not in self.selected_countries:
            self.selected_countries.append(country_name)
            self.update_comparison_list()
            messagebox.showinfo("Info", f"Added '{country_name}' to comparison list")
        else:
            messagebox.showinfo("Info", f"'{country_name}' is already in comparison list")
    
    def remove_from_comparison(self):
        """Remove selected countries from comparison list"""
        selected = self.compare_listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "Please select countries to remove")
            return
        
        for idx in reversed(selected):
            self.selected_countries.pop(idx)
        
        self.update_comparison_list()
    
    def clear_comparison_list(self):
        """Clear the comparison list"""
        self.selected_countries = []
        self.update_comparison_list()
    
    def update_comparison_list(self):
        """Update the listbox with current comparison countries"""
        self.compare_listbox.delete(0, tk.END)
        for country in self.selected_countries:
            self.compare_listbox.insert(tk.END, country)
    
    def show_top_countries(self):
        """Show top countries by selected metric"""
        metric = self.top_metric_var.get()
        try:
            n = int(self.top_count_var.get())
        except ValueError:
            messagebox.showwarning("Warning", "Please enter a valid number")
            return
        
        top_countries = self.scraper.get_top_countries(n, metric)
        if top_countries.empty:
            messagebox.showwarning("Warning", "No data available for this metric")
            return
        
        # Display in a new window
        top_window = tk.Toplevel(self.root)
        top_window.title(f"Top {n} Countries by {metric}")
        top_window.geometry("600x400")
        
        # Create treeview
        tree = ttk.Treeview(top_window, columns=('Rank', 'Country', metric), show='headings')
        tree.heading('Rank', text='Rank')
        tree.heading('Country', text='Country')
        tree.heading(metric, text=metric)
        
        # Add data
        for _, row in top_countries.iterrows():
            tree.insert('', tk.END, values=(int(row['Rank']), row['Country'], self.format_metric_value(row[metric], metric)))
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add visualization button
        ttk.Button(top_window, text="Visualize", 
                  command=lambda: self.visualizer.create_top_countries_chart(top_countries, n, metric)).pack(pady=5)
    
    def visualize_comparison(self):
        """Create visualizations for the comparison list"""
        if len(self.selected_countries) < 2:
            messagebox.showwarning("Warning", "Need at least 2 countries for comparison")
            return
        
        # Get data for selected countries
        comparison_data = []
        for country in self.selected_countries:
            country_info = self.scraper.search_country(country)
            if country_info is not None:
                comparison_data.append(country_info)
        
        if not comparison_data:
            messagebox.showwarning("Warning", "No valid countries found for comparison")
            return
        
        df_comparison = pd.DataFrame(comparison_data)
        
        # Show visualization options in a dialog
        self.show_visualization_options(df_comparison)
    
    def show_visualization_options(self, df_comparison):
        """Show dialog with visualization options"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Visualization Options")
        dialog.geometry("300x200")
        
        ttk.Label(dialog, text="Select Visualization Type:").pack(pady=10)
        
        ttk.Button(dialog, text="Single Metric Comparison", 
                  command=lambda: self.show_single_metric_options(dialog, df_comparison)).pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Button(dialog, text="Multi-Metric Comparison", 
                  command=lambda: self.create_multi_metric_chart(df_comparison)).pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Button(dialog, text="Scatter Plot", 
                  command=lambda: self.show_scatter_plot_options(dialog, df_comparison)).pack(fill=tk.X, padx=20, pady=5)
    
    def show_single_metric_options(self, parent, df_comparison):
        """Show options for single metric visualization"""
        parent.destroy()  # Close the previous dialog
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Single Metric Visualization")
        dialog.geometry("300x300")
        
        ttk.Label(dialog, text="Select Metric:").pack(pady=10)
        
        metrics = ['Population', 'Yearly_Change', 'Density', 'Land_Area', 
                  'Fertility_Rate', 'Median_Age', 'Urban_Population_Percent']
        
        for metric in metrics:
            ttk.Button(dialog, text=metric, 
                      command=lambda m=metric: self.create_single_metric_chart(dialog, df_comparison, m)).pack(fill=tk.X, padx=20, pady=2)
    
    def create_single_metric_chart(self, dialog, df_comparison, metric):
        """Create single metric chart and display in main window"""
        dialog.destroy()
        self.clear_plot()
        
        # Create figure
        self.figure = plt.Figure(figsize=(8, 5), dpi=100)
        ax = self.figure.add_subplot(111)
        
        # Create visualization
        countries = df_comparison['Country'].tolist()
        values = df_comparison[metric].tolist()
        
        colors = plt.cm.Set3(range(len(countries)))
        bars = ax.bar(countries, values, color=colors, alpha=0.8, edgecolor='black', linewidth=1)
        
        # Customize the chart
        ax.set_title(f'{metric} Comparison', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Countries', fontsize=12, fontweight='bold')
        ax.set_ylabel(self.visualizer._get_ylabel(metric), fontsize=12, fontweight='bold')
        
        # Rotate x-axis labels
        plt.xticks(rotation=45, ha='right')
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    self.visualizer._format_number(value, metric),
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        # Display in tkinter window
        self.display_plot()
    
    def create_multi_metric_chart(self, df_comparison):
        """Create multi-metric chart and display in main window"""
        self.clear_plot()
        
        metrics = ['Population', 'Density', 'Fertility_Rate', 'Median_Age']
        
        # Create figure with subplots
        self.figure = plt.Figure(figsize=(10, 8), dpi=100)
        
        for i, metric in enumerate(metrics[:4]):  # Limit to 4 metrics
            ax = self.figure.add_subplot(2, 2, i+1)
            
            countries = df_comparison['Country'].tolist()
            values = df_comparison[metric].tolist()
            
            colors = plt.cm.Set2(range(len(countries)))
            bars = ax.bar(countries, values, color=colors, alpha=0.8, edgecolor='black')
            
            ax.set_title(f'{metric}', fontsize=14, fontweight='bold')
            ax.set_xlabel('Countries', fontsize=10)
            ax.set_ylabel(self.visualizer._get_ylabel(metric), fontsize=10)
            
            ax.tick_params(axis='x', rotation=45, labelsize=9)
            
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       self.visualizer._format_number(value, metric),
                       ha='center', va='bottom', fontsize=8)
            
            ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        self.figure.suptitle('Multi-Metric Country Comparison', fontsize=16, fontweight='bold')
        self.figure.tight_layout()
        
        # Display in tkinter window
        self.display_plot()
    
    def show_scatter_plot_options(self, parent, df_comparison):
        """Show options for scatter plot visualization"""
        parent.destroy()  # Close the previous dialog
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Scatter Plot Options")
        dialog.geometry("400x300")
        
        metrics = ['Population', 'Yearly_Change', 'Density', 'Land_Area', 
                  'Fertility_Rate', 'Median_Age', 'Urban_Population_Percent']
        
        ttk.Label(dialog, text="X-axis Metric:").pack(pady=(10,0))
        x_var = tk.StringVar()
        x_combo = ttk.Combobox(dialog, textvariable=x_var, values=metrics)
        x_combo.current(0)
        x_combo.pack(padx=20, pady=5)
        
        ttk.Label(dialog, text="Y-axis Metric:").pack(pady=(10,0))
        y_var = tk.StringVar()
        y_combo = ttk.Combobox(dialog, textvariable=y_var, values=metrics)
        y_combo.current(1)
        y_combo.pack(padx=20, pady=5)
        
        ttk.Button(dialog, text="Create Scatter Plot", 
                  command=lambda: self.create_scatter_plot(dialog, df_comparison, x_var.get(), y_var.get())).pack(pady=20)
    
    def create_scatter_plot(self, dialog, df_comparison, x_metric, y_metric):
        """Create scatter plot and display in main window"""
        dialog.destroy()
        self.clear_plot()
        
        # Create figure
        self.figure = plt.Figure(figsize=(8, 6), dpi=100)
        ax = self.figure.add_subplot(111)
        
        x_values = df_comparison[x_metric]
        y_values = df_comparison[y_metric]
        
        scatter = ax.scatter(x_values, y_values, c=range(len(df_comparison)), 
                           cmap='viridis', alpha=0.7, s=100, edgecolor='black')
        
        # Add country labels
        for i, row in df_comparison.iterrows():
            ax.annotate(row['Country'], (row[x_metric], row[y_metric]), 
                       xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        ax.set_title(f'{y_metric} vs {x_metric}', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel(self.visualizer._get_ylabel(x_metric), fontsize=12, fontweight='bold')
        ax.set_ylabel(self.visualizer._get_ylabel(y_metric), fontsize=12, fontweight='bold')
        
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Display in tkinter window
        self.display_plot()
    
    def display_plot(self):
        """Display the current matplotlib figure in the GUI"""
        if self.figure is None:
            return
        
        # Clear previous canvas if it exists
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        
        # Hide the info text
        self.info_text.pack_forget()
        
        # Create new canvas
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.display_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add close button
        if hasattr(self, 'close_plot_btn'):
            self.close_plot_btn.destroy()
        
        self.close_plot_btn = ttk.Button(self.display_frame, text="Close Plot", command=self.clear_plot)
        self.close_plot_btn.pack(pady=5)
    
    def clear_plot(self):
        """Clear the current plot and show info text"""
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        
        if self.figure:
            plt.close(self.figure)
            self.figure = None
        
        if hasattr(self, 'close_plot_btn'):
            self.close_plot_btn.destroy()
        
        # Show the info text again
        self.info_text.pack(fill=tk.BOTH, expand=True)
    
    def export_data(self):
        """Export data to CSV or Excel"""
        if self.data is None:
            messagebox.showwarning("Warning", "No data available to export")
            return
        
        # Ask what to export
        export_choice = messagebox.askquestion("Export", "Export all data or just comparison list?", 
                                             icon='question', default='yes', 
                                             detail="Click 'Yes' for all data, 'No' for comparison list")
        
        if export_choice == 'yes':
            data_to_export = self.data
        else:
            if not self.selected_countries:
                messagebox.showwarning("Warning", "Comparison list is empty")
                return
            data_to_export = self.data[self.data['Country'].isin(self.selected_countries)]
        
        # Ask for format
        format_choice = messagebox.askquestion("Format", "Export as CSV or Excel?", 
                                             icon='question', default='yes', 
                                             detail="Click 'Yes' for CSV, 'No' for Excel")
        
        # Get save path
        file_ext = ".csv" if format_choice == 'yes' else ".xlsx"
        file_path = filedialog.asksaveasfilename(
            defaultextension=file_ext,
            filetypes=[("CSV Files", "*.csv"), ("Excel Files", "*.xlsx")] if format_choice == 'yes' 
            else [("Excel Files", "*.xlsx"), ("CSV Files", "*.csv")],
            title="Save As"
        )
        
        if not file_path:
            return  # User cancelled
        
        try:
            if format_choice == 'yes':
                data_to_export.to_csv(file_path, index=False)
            else:
                data_to_export.to_excel(file_path, index=False)
            
            messagebox.showinfo("Success", f"Data successfully exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")
    
    def format_metric_value(self, value, metric):
        """Format a metric value for display"""
        if pd.isna(value):
            return 'N/A'
        
        if metric in ['Population', 'Net_Change', 'Land_Area', 'Net_Migration']:
            return f"{int(value):,}"
        elif metric in ['Yearly_Change', 'Urban_Population_Percent', 'World_Share']:
            return f"{value:.2f}%"
        elif metric in ['Fertility_Rate', 'Median_Age']:
            return f"{value:.1f}"
        elif metric == 'Density':
            return f"{int(value)}"
        else:
            return str(value)

if __name__ == "__main__":
    root = tk.Tk()
    app = PopulationExplorerApp(root)
    root.mainloop()