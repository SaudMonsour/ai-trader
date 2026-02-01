import yaml
import os

class ConfigLoader:
    def __init__(self, config_path="config/config.yaml", entities_path="config/entities.yaml"):
        self.config_path = config_path
        self.entities_path = entities_path
        self.config = {}
        self.entities = {}

    def load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Load entities if exists, else empty
        if os.path.exists(self.entities_path):
            with open(self.entities_path, 'r') as f:
                self.entities = yaml.safe_load(f).get('entities', {})
        
        return self.config

    def get_entities(self):
        return self.entities

    def get(self, key, default=None):
        keys = key.split('.')
        val = self.config
        for k in keys:
            if isinstance(val, dict):
                val = val.get(k)
            else:
                return default
        return val if val is not None else default

# Global instance
_loader = ConfigLoader()
def load_config():
    return _loader.load_config()

def get_config(key, default=None):
    return _loader.get(key, default)

def get_entities():
    return _loader.get_entities()
