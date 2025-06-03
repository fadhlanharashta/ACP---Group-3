# Imports
#Files
# import worldometre 

# Libraries
import tkinter as tk
from tkinter import ttk

class WorldometerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Worldometer Statistics Viewer")
        self.root.geometry("800x600")
        
        # Country selection frame (top)
        self.country_frame = ttk.LabelFrame(root, text="Select Country", padding=10)
        self.country_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Country dropdown
        self.country_var = tk.StringVar()
        self.country_combo = ttk.Combobox(
            self.country_frame, 
            textvariable=self.country_var,
            state="readonly"
        )
        self.country_combo.pack(fill=tk.X, expand=True)
        
        # Add some sample countries (you'll need to implement real country list)
        self.country_combo['values'] = [
            "Select a country",
            "United States",
            "China",
            "India",
            "Brazil",
            "Germany"
        ]
        self.country_combo.current(0)
        
        # Bind selection event
        self.country_combo.bind("<<ComboboxSelected>>", self.on_country_select)
        
        # Statistics display frame (bottom)
        self.stats_frame = ttk.LabelFrame(root, text="Population Statistics", padding=10)
        self.stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Statistics labels
        self.labels = {
            "Population": tk.StringVar(),
            "Birth Rate": tk.StringVar(),
            "Death Rate": tk.StringVar(),
            "Growth Rate": tk.StringVar()
        }
        
        # Initialize all labels with "N/A"
        for stat, var in self.labels.items():
            var.set("N/A")
            label = ttk.Label(self.stats_frame, text=f"{stat}:")
            value = ttk.Label(self.stats_frame, textvariable=var)
            label.grid(sticky=tk.W, pady=2)
            value.grid(row=label.grid_info()["row"], column=1, sticky=tk.W, pady=2)
    
    def on_country_select(self, event):
        """Called when a country is selected from dropdown"""
        selected_country = self.country_var.get()
        
        if selected_country == "Select a country":
            return
            
        # Here you would call your worldometre functions with the selected country
        # For now, we'll just demonstrate with dummy data
        self.labels["Population"].set("Fetching...")
        
        # Simulate fetching data (replace with actual worldometre calls)
        self.root.after(1000, lambda: self.update_stats(
            population="1,402,000,000",
            birth_rate="12.3 per 1,000",
            death_rate="7.8 per 1,000",
            growth_rate="0.45%"
        ))
    
    def update_stats(self, population, birth_rate, death_rate, growth_rate):
        """Update the statistics display"""
        self.labels["Population"].set(population)
        self.labels["Birth Rate"].set(birth_rate)
        self.labels["Death Rate"].set(death_rate)
        self.labels["Growth Rate"].set(growth_rate)

if __name__ == "__main__":
    root = tk.Tk()
    app = WorldometerApp(root)
    root.mainloop()
