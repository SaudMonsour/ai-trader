import os
from src.utils.state_manager import StateManager
from src.ingestion.news_fetcher import NewsFetcher
from src.signals.engine import SignalEngine
from src.analysis.sentiment import SentimentAnalyzer
from src.analysis.entities import EntityExtractor
from src.execution.order_manager import OrderManager
from src.execution.paper_broker import PaperBroker
from src.utils.logger import get_logger
from src.models import NewsItem

def test_main_cycle(tmp_path, monkeypatch):
    # prepare temp state file
    state_file = tmp_path / "state.json"
    state = StateManager(state_file=str(state_file))
    logger = get_logger("test")
    
    # fake news fetcher
    class FakeFetcher:
        def fetch_all(self):
            return [NewsItem(
                id="test_1",
                source="Test",
                title="Fed signals rate cut",
                content="rate cut expected",
                url="http://example.com/1",
                published_at="2026-02-09T00:00:00Z"
            )]
            
    fetcher = FakeFetcher()
    extractor = EntityExtractor(path="config/entities.yaml")
    engine = SignalEngine()
    analyzer = SentimentAnalyzer()
    broker = PaperBroker(state, logger)
    order_mgr = OrderManager(broker, logger)
    
    items = fetcher.fetch_all()
    for it in items:
        it.sentiment_score = analyzer.analyze(it.title + " " + it.content)
        it.entities = extractor.extract(it.title + " " + it.content)
        signals = engine.generate_signal(it)
        for sig in signals:
            res = order_mgr.handle(sig, mode="dry_run")
            assert res["executed"] == False
        state.mark_news_processed(it.id)
    assert "test_1" in state.state["processed_news_ids"]
