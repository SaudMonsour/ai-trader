import time
import sys
import signal
from src.utils.logger import setup_logger, get_logger
from src.utils.config_loader import load_config, get_config
from src.utils.state_manager import get_state_manager

from src.ingestion.news_fetcher import NewsFetcher
from src.ingestion.market_data import MarketDataFetcher
from src.analysis.sentiment import SentimentAnalyzer
from src.analysis.extractor import EntityExtractor
from src.signals.engine import SignalEngine
from src.execution.risk_manager import RiskManager
from src.execution.broker import Broker

# Setup Logger
setup_logger()
logger = get_logger("Main")

class TradingBot:
    def __init__(self):
        self.running = True
        logger.info("Initializing TradingBot...")
        
        # Load Config
        self.config = load_config()
        self.tick_interval = get_config("system.tick_interval_sec", 60)
        
        # Init Components
        self.state_manager = get_state_manager()
        self.news_fetcher = NewsFetcher()
        self.market_data = MarketDataFetcher()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.entity_extractor = EntityExtractor()
        self.signal_engine = SignalEngine()
        
        self.risk_manager = RiskManager()
        self.risk_manager.set_market_data(self.market_data)
        
        self.broker = Broker()
        self.broker.set_market_data(self.market_data)
        
        # Handle Signals
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def shutdown(self, signum, frame):
        logger.info("Shutdown signal received. Saving state...")
        self.running = False
        self.state_manager.save_state()
        sys.exit(0)

    def run(self):
        logger.info("Bot started in loop.")
        while self.running:
            try:
                self.tick()
            except Exception as e:
                logger.error(f"Error in tick: {e}", exc_info=True)
            
            logger.debug(f"Sleeping for {self.tick_interval}s...")
            time.sleep(self.tick_interval)

    def tick(self):
        logger.info("Tick: Fetching news...")
        
        # 1. Fetch News
        news_items = self.news_fetcher.fetch_all()
        if not news_items:
            logger.info("No new news.")
            return

        for item in news_items:
            try:
                self.process_item(item)
            except Exception as e:
                logger.error(f"Failed to process item {item.id}: {e}")
            
            # Mark processed regardless of outcome to avoid infinite error loop on bad item?
            # Or only on success?
            # If error is transient (network), we want to retry.
            # If error is logic (bug), we want to skip.
            # For MVP, we mark as processed to be safe from stuck loops.
            self.state_manager.mark_news_processed(item.id)

    def process_item(self, item):
        # 2. Analysis
        # Combine title and content/summary for analysis
        full_text = f"{item.title} . {item.content or ''}"
        
        item.sentiment_score = self.sentiment_analyzer.analyze(full_text)
        item.entities = self.entity_extractor.extract(full_text)
        
        logger.info(f"Analyzed '{item.title}': Sentiment={item.sentiment_score:.2f}, Entities={item.entities}")
        
        if not item.entities:
            return # Skip if no entities found

        # 3. Generate Signals
        signals = self.signal_engine.generate_signal(item)
        
        for sig in signals:
            logger.info(f"Signal: {sig.action} {sig.asset} ({sig.confidence})")
            
            # Persist Signal
            self.state_manager.add_signal(sig)
            
            # 4. Risk Check
            order = self.risk_manager.check_risk(sig)
            if order:
                # 5. Execute
                if self.broker.execute(order):
                    logger.info(f"Order Executed: {order.symbol}")
                else:
                    logger.error(f"Order Execution Failed: {order.symbol}")
            else:
                logger.info("Signal rejected by Risk Manager")

if __name__ == "__main__":
    bot = TradingBot()
    bot.run()
