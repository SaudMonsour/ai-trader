import yaml
import re
from pathlib import Path

class EntityExtractor:
    def __init__(self, path="config/entities.yaml"):
        self.path = Path(path)
        with self.path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        self.entities = data.get("entities", [])

    def extract(self, text: str):
        t = text.lower()
        found = set()
        for ent in self.entities:
            for alias in ent.get("aliases", []):
                pattern = r"\b" + re.escape(alias.lower()) + r"\b"
                if re.search(pattern, t):
                    for tk in ent.get("tickers", []):
                        found.add(tk)
        return list(found)
