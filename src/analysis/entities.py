import yaml
import re
from pathlib import Path

class EntityExtractor:
    def __init__(self, path="config/entities.yaml"):
        self.path = Path(path)
        with self.path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        # Handle both list of dicts (old) and dict mapping (new)
        self.entities_map = data.get("entities", {})

    def extract(self, text: str):
        if not text:
            return []
        t = text.lower()
        found = set()
        
        if isinstance(self.entities_map, dict):
            for name, ticker in self.entities_map.items():
                # Simple word boundary check
                pattern = r"\b" + re.escape(name.lower()) + r"\b"
                if re.search(pattern, t):
                    if isinstance(ticker, list):
                        found.update(ticker)
                    else:
                        found.add(ticker)
        elif isinstance(self.entities_map, list):
            for ent in self.entities_map:
                for alias in ent.get("aliases", []):
                    pattern = r"\b" + re.escape(alias.lower()) + r"\b"
                    if re.search(pattern, t):
                        for tk in ent.get("tickers", []):
                            found.add(tk)
        return list(found)
