from textblob import TextBlob
from src.utils.logger import get_logger

logger = get_logger("SentimentAnalyzer")

class SentimentAnalyzer:
    def __init__(self):
        pass

    def analyze(self, text: str) -> float:
        """
        Returns sentiment score between -1.0 (Negative) and 1.0 (Positive).
        """
        try:
            if not text:
                return 0.0
            blob = TextBlob(text)
            return blob.sentiment.polarity
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return 0.0
