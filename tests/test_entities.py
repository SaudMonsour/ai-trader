from src.analysis.entities import EntityExtractor

def test_entity_matching(tmp_path, monkeypatch):
    # use default config/entities.yaml
    extractor = EntityExtractor(path="config/entities.yaml")
    text = "Apple reports strong revenue in Q4"
    found = extractor.extract(text)
    assert "AAPL" in found
