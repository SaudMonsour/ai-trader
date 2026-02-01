from typing import List
from src.utils.config_loader import get_entities
from src.utils.logger import get_logger

logger = get_logger("EntityExtractor")

class EntityExtractor:
    def __init__(self):
        self.entity_map = get_entities()
        # map: "Apple" -> "AAPL"
        # We can also do reverse mapping or simple contains check
        # For efficiency, we iterate over keys (Apple) in text
    
    def extract(self, text: str) -> List[str]:
        """
        Returns list of Tickers found in text.
        """
        found_tickers = set()
        if not text:
            return []
        
        text_lower = text.lower()
        
        for name, ticker in self.entity_map.items():
            # Simple substring match
            # "Apple" in "Apple releases new iPhone" -> Match
            # "Gold" in "Golden Globes" -> Match (False positive risk)
            # Better: check word boundaries or ignore case carefully
            # For MVP: simple lower case substring
            if name.lower() in text_lower:
                found_tickers.add(ticker)
                
        return list(found_tickers)
