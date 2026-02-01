from signals.engine import RuleEngine

def test_rule_weighting():
    engine = RuleEngine(path="config/rules.yaml")
    news_item = {"news_id":"n1", "title":"Company missed earnings", "summary": "earnings miss announced"}
    sentiment = -0.5
    entities = ["AAPL"]
    sig = engine.evaluate(news_item, sentiment, entities)
    assert sig.confidence > 0
    assert sig.action in ["BUY","SELL","HOLD"]
