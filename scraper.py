import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from typing import Dict, List, Optional

class PopulationScraper:
    def __init__(self):
        self.url = "https://www.worldometers.info/world-population/population-by-country/"
        self.data = None
        
    def scrape_data(self) -> pd.DataFrame:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            print("Fetching data from Worldometers...")
            response = requests.get(self.url, headers=headers)
            response.raise_for_status()
            
            print("Parsing HTML content...")
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple table selectors
            table = None
            table_selectors = [
                {'id': 'example2'},  # Original selector
                {'class': 'table'},  # Common table class
                {'class': 'table-striped'},  # Bootstrap table class
                {'class': 'table-bordered'}  # Another common table class
            ]
            
            for selector in table_selectors:
                table = soup.find('table', selector)
                if table:
                    print(f"Found table with selector: {selector}")
                    break
            
            if not table:
                # Fallback: look for any table with population data
                print("Trying to find table by content...")
                tables = soup.find_all('table')
                for t in tables:
                    if t.find('th', string=lambda text: text and ('Country' in text or 'Population' in text)):
                        table = t
                        print("Found table by content")
                        break
            
            if not table:
                raise ValueError("Could not find population table on the page")
            
            print("Extracting table data...")
            # Extract headers
            headers = []
            header_row = table.find('tr')
            for th in header_row.find_all(['th', 'td']):
                headers.append(th.get_text(strip=True))
            
            # Extract data rows
            rows = []
            for row in table.find_all('tr')[1:]:  # Skip header row
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 10:  # Ensure we have enough columns
                    row_data = [cell.get_text(strip=True) for cell in cells]
                    rows.append(row_data)
            
            if not rows:
                raise ValueError("No data rows found in the table")
            
            print("Creating DataFrame...")
            # Create DataFrame
            df = pd.DataFrame(rows, columns=headers[:len(rows[0]) if rows else 0])
            
            # Clean and process the data
            print("Cleaning and processing data...")
            df = self._clean_data(df)
            
            self.data = df
            print("Scraping completed successfully!")
            return df
            
        except Exception as e:
            print(f"Error scraping data: {e}")
            print("Using fallback data...")
            return self._get_fallback_data()
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and format the scraped data"""
        # Rename columns to standard names
        column_mapping = {
            'Country (or dependency)': 'Country',
            'Population (2025)': 'Population',
            'Yearly Change': 'Yearly_Change',
            'Net Change': 'Net_Change',
            'Density (P/Km²)': 'Density',
            'Land Area (Km²)': 'Land_Area',
            'Migrants (net)': 'Net_Migration',
            'Fert. Rate': 'Fertility_Rate',
            'Median Age': 'Median_Age',
            'Urban Pop %': 'Urban_Population_Percent',
            'World Share': 'World_Share'
        }
        
        # Apply column mapping
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        # Clean numeric columns
        numeric_columns = ['Population', 'Net_Change', 'Density', 'Land_Area', 
                          'Net_Migration', 'Fertility_Rate', 'Median_Age']
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '').str.replace('−', '-')
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Clean percentage columns
        percentage_columns = ['Yearly_Change', 'Urban_Population_Percent', 'World_Share']
        for col in percentage_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace('%', '').str.replace('−', '-')
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Add rank column
        df.insert(0, 'Rank', range(1, len(df) + 1))
        
        return df
    
    def _get_fallback_data(self) -> pd.DataFrame:
        """Fallback data in case scraping fails"""
        print("Using fallback data...")
        fallback_data = [
            ['India', 1463865525, 0.89, 12929734, 492, 2973190, -495753, 1.94, 28.8, 37.1, 17.78],
            ['China', 1416096094, -0.23, -3225184, 151, 9388211, -268126, 1.02, 40.1, 67.5, 17.20],
            ['United States', 347275807, 0.54, 1849236, 38, 9147420, 1230663, 1.62, 38.5, 82.8, 4.22],
            ['Indonesia', 285721236, 0.79, 2233305, 158, 1811570, -39509, 2.1, 30.4, 59.6, 3.47],
            ['Pakistan', 255219554, 1.57, 3950390, 331, 770880, -1235336, 3.5, 20.6, 34.4, 3.10]
        ]
        
        columns = ['Country', 'Population', 'Yearly_Change', 'Net_Change', 'Density', 
                  'Land_Area', 'Net_Migration', 'Fertility_Rate', 'Median_Age', 
                  'Urban_Population_Percent', 'World_Share']
        
        df = pd.DataFrame(fallback_data, columns=columns)
        df.insert(0, 'Rank', range(1, len(df) + 1))
        return df
    
    def get_data(self) -> pd.DataFrame:
        """Get the scraped data, scraping if necessary"""
        if self.data is None:
            self.scrape_data()
        return self.data
    
    def search_country(self, country_name: str) -> Optional[pd.Series]:
        """Search for a specific country"""
        if self.data is None:
            self.scrape_data()
        
        if self.data is None:
            print("No data available for search")
            return None
        
        # Try exact match first
        exact_match = self.data[self.data['Country'].str.lower() == country_name.lower()]
        if not exact_match.empty:
            return exact_match.iloc[0]
        
        # Try partial match
        partial_match = self.data[self.data['Country'].str.contains(country_name, case=False, na=False)]
        if not partial_match.empty:
            return partial_match.iloc[0]
        
        return None
    
    def get_top_countries(self, n: int = 10, by: str = 'Population') -> pd.DataFrame:
        """Get top N countries by specified metric"""
        if self.data is None:
            self.scrape_data()
        
        if self.data is None or self.data.empty:
            print("No data available for getting top countries")
            return pd.DataFrame(columns=['Rank', 'Country', 'Population', 'Yearly_Change', 'Net_Change', 
                                       'Density', 'Land_Area', 'Net_Migration', 'Fertility_Rate', 
                                       'Median_Age', 'Urban_Population_Percent', 'World_Share'])
        
        if by not in self.data.columns:
            print(f"Column '{by}' not found in data")
            return pd.DataFrame(columns=['Rank', 'Country', 'Population', 'Yearly_Change', 'Net_Change', 
                                       'Density', 'Land_Area', 'Net_Migration', 'Fertility_Rate', 
                                       'Median_Age', 'Urban_Population_Percent', 'World_Share'])
        
        return self.data.nlargest(n, by)
    
    def get_countries_by_range(self, column: str, min_val: float, max_val: float) -> pd.DataFrame:
        """Get countries within a specified range for a given metric"""
        if self.data is None:
            self.scrape_data()
        
        if self.data is None:
            print("No data available for range search")
            return pd.DataFrame()
        
        if column not in self.data.columns:
            print(f"Column '{column}' not found in data")
            return pd.DataFrame()
        
        return self.data[(self.data[column] >= min_val) & (self.data[column] <= max_val)]