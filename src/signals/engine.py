from typing import List, Optional
from src.models import NewsItem, Signal
from src.utils.config_loader import get_config
from src.utils.logger import get_logger

logger = get_logger("SignalEngine")

class SignalEngine:
    def __init__(self):
        self.buy_threshold = get_config("trading.sentiment_buy_threshold", 0.5)
        self.sell_threshold = get_config("trading.sentiment_sell_threshold", -0.5)
        self.min_confidence = get_config("trading.min_confidence", 0.7)

    def generate_signal(self, news_item: NewsItem) -> List[Signal]:
        signals = []
        if not news_item.entities:
            return []

        score = news_item.sentiment_score
        # Basic Sentiment Strategy
        action = None
        confidence = abs(score) # Simple confidence proxy for MVP

        if score >= self.buy_threshold:
            action = "BUY"
        elif score <= self.sell_threshold:
            action = "SELL"
        
        if action and confidence >= self.min_confidence:
            import hashlib
            for ticker in news_item.entities:
                # Deterministic ID: news_id + ticker + action
                # We do NOT include timestamp because we want it to be idempotent for the SAME news item.
                raw_id = f"{news_item.id}|{ticker}|{action}"
                sig_id = hashlib.sha1(raw_id.encode('utf-8')).hexdigest()
                
                signal = Signal(
                    id=sig_id,
                    asset=ticker,
                    action=action,
                    confidence=confidence,
                    reasons=[f"Sentiment {score:.2f} based on news '{news_item.title}'"],
                    source_news_id=news_item.id
                )
                signals.append(signal)
                logger.info(f"Generated Signal: {action} {ticker} (Conf: {confidence:.2f})")
        
        return signals
