
import pandas as pd
import yaml
import sys
import requests
from io import open, StringIO

def fetch_and_generate():
    try:
        print("Fetching S&P 500 list from Wikipedia...")
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Use StringIO to wrap the string content for read_html
        tables = pd.read_html(StringIO(response.text))
        df = tables[0]
        
        # Prepare entities dictionary: Name -> Ticker
        entities = {}
        tickers = []
        
        print(f"Found {len(df)} companies.")
        
        for index, row in df.iterrows():
            ticker = row['Symbol'].replace('.', '-') # BRK.B -> BRK-B
            name = row['Security']
            
            # Add mapping
            entities[name] = ticker
            tickers.append(ticker)
            
            # Simple heuristic for common names (e.g. "Apple Inc." -> "Apple")
            # Remove Inc, Corp, Ltd, plc
            simple_name = name
            for suffix in [' Inc.', ' Corp.', ' Ltd.', ' plc', ' N.V.', ' Company', ' Co.']:
                simple_name = simple_name.split(suffix)[0]
            
            simple_name = simple_name.strip()
            
            if simple_name != name:
                entities[simple_name] = ticker

        # Generate entities.yaml content
        entities_data = {
            "entities": entities
        }
        
        with open('config/entities.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(entities_data, f, sort_keys=False, allow_unicode=True)
            
        print("Updated config/entities.yaml")
        
        # Read existing config to preserve other settings
        with open('config/config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        # Update assets
        config['assets']['stocks'] = tickers
        
        # Save config.yaml
        with open('config/config.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(config, f, sort_keys=False, allow_unicode=True)
            
        print("Updated config/config.yaml")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fetch_and_generate()
