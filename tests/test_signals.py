from src.signals.engine import SignalEngine
from src.models import NewsItem

def test_rule_weighting():
    engine = SignalEngine()
    news_item = NewsItem(
        id="n1",
        source="Test",
        title="Company missed earnings",
        url="http://example.com",
        published_at="2026-02-09T00:00:00Z",
        content="earnings miss announced"
    )
    news_item.sentiment_score = -0.8
    news_item.entities = ["AAPL"]
    
    signals = engine.generate_signal(news_item)
    assert len(signals) > 0
    sig = signals[0]
    assert sig.confidence > 0
    assert sig.action in ["BUY", "SELL", "HOLD"]
