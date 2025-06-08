from scraper import PopulationScraper
import pandas as pd

def test_scraper():
    # Initialize the scraper
    scraper = PopulationScraper()
    
    # Test scraping data
    print("Testing data scraping...")
    df = scraper.scrape_data()
    
    # Check if data was scraped successfully
    if df is not None and not df.empty:
        print("\nScraping successful!")
        print(f"Number of countries scraped: {len(df)}")
        print("\nFirst 5 rows of data:")
        print(df.head())
        
        # Test search functionality
        print("\nTesting country search...")
        test_countries = ['Indonesia', 'China', 'India']
        for country in test_countries:
            result = scraper.search_country(country)
            if result is not None:
                print(f"\nFound data for {country}:")
                print(result)
            else:
                print(f"\nNo data found for {country}")
        
        # Test top countries
        print("\nTesting top countries by population:")
        top_countries = scraper.get_top_countries(n=5, by='Population')
        print(top_countries[['Country', 'Population']])
    else:
        print("Scraping failed or returned empty data")

if __name__ == "__main__":
    test_scraper() 