import os
from state.state_manager import StateManager
from ingestion.news_fetcher import NewsFetcher
from signals.engine import RuleEngine
from analysis.sentiment import analyze_sentiment
from analysis.entities import EntityExtractor
from execution.order_manager import OrderManager
from execution.paper_broker import PaperBroker
from utils.logger import get_logger

def test_main_cycle(tmp_path, monkeypatch):
    # prepare temp state file
    os.environ["PYTEST_TMPDIR"] = str(tmp_path)
    state = StateManager(path=tmp_path / "state.json")
    logger = get_logger("test", path=str(tmp_path / "test.log"))
    # fake news fetcher
    class FakeFetcher:
        def fetch(self):
            return [{
                "news_id": "test_1",
                "title": "Fed signals rate cut",
                "link": "http://example.com/1",
                "summary": "rate cut expected"
            }]
    fetcher = FakeFetcher()
    extractor = EntityExtractor(path="config/entities.yaml")
    engine = RuleEngine(path="config/rules.yaml")
    broker = PaperBroker(state, logger)
    order_mgr = OrderManager(broker, logger)
    items = fetcher.fetch()
    for it in items:
        sentiment = analyze_sentiment(it["title"] + " " + it["summary"])
        entities = extractor.extract(it["title"] + " " + it["summary"])
        sig = engine.evaluate(it, sentiment, entities)
        res = order_mgr.handle(sig, mode="dry_run")
        assert res["executed"] == False
        state.mark_processed(it["news_id"])
    assert "test_1" in state.state["processed_news_ids"]
