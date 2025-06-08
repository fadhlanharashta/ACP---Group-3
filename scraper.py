import pandas as pd
import re
from typing import Dict, List, Optional
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options

class PopulationScraper:
    def __init__(self, max_retries: int = 1, retry_delay: int = 5):
        self.url = "https://www.worldometers.info/world-population/population-by-country/"
        self.data = None
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.driver = None
        
    def _setup_driver(self):
        """Set up and configure the Chrome WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-software-rasterizer')  # Disable software rasterizer
        chrome_options.add_argument('--disable-webgl')  # Disable WebGL
        chrome_options.add_argument('--disable-webgl2')  # Disable WebGL 2.0
        
        self.driver = webdriver.Chrome(options=chrome_options)
        
    def _close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
        
    def scrape_data(self) -> pd.DataFrame:
        retry_count = 0
        last_error = None
        
        while retry_count < self.max_retries:
            try:
                print(f"Fetching data from Worldometers... (Attempt {retry_count + 1}/{self.max_retries})")
                
                if not self.driver:
                    self._setup_driver()
                
                self.driver.get(self.url)
                
                print("\nPage Title:", self.driver.title)
                
                print("\nPage Source Length:", len(self.driver.page_source))
                
                print("\nAll tables found on page:")
                tables = self.driver.find_elements(By.TAG_NAME, "table")
                print(f"Number of tables found: {len(tables)}")
                
                print("\nWaiting for table to load...")
                wait = WebDriverWait(self.driver, 10)
                table = wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "datatable"))
                )
                
                print("\nFound target table:")
                
                print("\nExtracting table data...")
                headers = []
                header_cells = table.find_elements(By.CSS_SELECTOR, "thead th")
                print(f"\nNumber of header cells found: {len(header_cells)}")
                for cell in header_cells:
                    header_text = cell.text.strip()
                    headers.append(header_text)
                
                rows = []
                data_rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
                print(f"\nNumber of data rows found: {len(data_rows)}")
                
                for i, row in enumerate(data_rows[:len(data_rows)]):
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 10:
                        row_data = [cell.text.strip() for cell in cells]
                        rows.append(row_data)
                
                if not rows:
                    raise ValueError("No data rows found in the table")
                
                print("\nCreating DataFrame...")
                
                df = pd.DataFrame(rows, columns=headers[:len(rows[0]) if rows else 0])
                
                print("\nCleaning and processing data...")
                df = self._clean_data(df)
                
                self.data = df
                print("\nScraping completed successfully!")
                return df
                
            except Exception as e:
                last_error = e
                retry_count += 1
                if retry_count < self.max_retries:
                    print(f"\nError occurred: {str(e)}")
                    print(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    print(f"\nFailed after {self.max_retries} attempts. Last error: {str(last_error)}")
                    raise last_error
            finally:
                self._close_driver()
    
    def __del__(self):
        """Cleanup when the object is destroyed"""
        self._close_driver()
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and format the scraped data"""
        
        column_mapping = {
            'Country (or\ndependency)': 'Country',
            'Country (or dependency)': 'Country',
            'Population\n(2025)': 'Population',
            'Population (2025)': 'Population',
            'Yearly\nChange': 'Yearly_Change',
            'Yearly Change': 'Yearly_Change',
            'Net\nChange': 'Net_Change',
            'Net Change': 'Net_Change',
            'Density\n(P/Km²)': 'Density',
            'Density (P/Km²)': 'Density',
            'Land Area\n(Km²)': 'Land_Area',
            'Land Area (Km²)': 'Land_Area',
            'Migrants\n(net)': 'Net_Migration',
            'Migrants (net)': 'Net_Migration',
            'Fert.\nRate': 'Fertility_Rate',
            'Fert. Rate': 'Fertility_Rate',
            'Median\nAge': 'Median_Age',
            'Median Age': 'Median_Age',
            'Urban\nPop %': 'Urban_Population_Percent',
            'Urban Pop %': 'Urban_Population_Percent',
            'World\nShare': 'World_Share',
            'World Share': 'World_Share'
        }
        
        print("\nOriginal column names:")
        print(df.columns.tolist())
        
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        print("\nColumn names after mapping:")
        print(df.columns.tolist())
        
        numeric_columns = ['Population', 'Net_Change', 'Density', 'Land_Area', 
                          'Net_Migration', 'Fertility_Rate', 'Median_Age']
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '').str.replace('−', '-')
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        percentage_columns = ['Yearly_Change', 'Urban_Population_Percent', 'World_Share']
        for col in percentage_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace('%', '').str.replace('−', '-')
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
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
        
        print("\nAvailable columns in DataFrame:")
        print(self.data.columns.tolist())
        
        possible_columns = ['Country (or\ndependency)', 'Country (or dependency)', 'Country']
        country_column = None
        
        for col in possible_columns:
            if col in self.data.columns:
                country_column = col
                break
        
        if country_column is None:
            raise ValueError("Could not find country column in the data")
        
        exact_match = self.data[self.data[country_column].str.lower() == country_name.lower()]
        if not exact_match.empty:
            return exact_match.iloc[0]

        partial_match = self.data[self.data[country_column].str.contains(country_name, case=False, na=False)]
        if not partial_match.empty:
            return partial_match.iloc[0]
        
        return None
    
    def get_top_countries(self, n: int = 10, by: str = 'Population') -> pd.DataFrame:
        """Get top N countries by specified metric"""
        if self.data is None:
            self.scrape_data()
        
        if by not in self.data.columns:
            raise ValueError(f"Column '{by}' not found in data")
        
        return self.data.nlargest(n, by)