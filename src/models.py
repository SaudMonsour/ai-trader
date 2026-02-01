from dataclasses import dataclass, field
from typing import List, Optional, Dict
import datetime

@dataclass
class NewsItem:
    id: str
    source: str
    title: str
    url: str
    published_at: str  # ISO format UTC
    content: str
    summary: Optional[str] = None
    
    # Enriched Data
    sentiment_score: float = 0.0
    entities: List[str] = field(default_factory=list)
    topic: Optional[str] = None

@dataclass
class Asset:
    symbol: str
    type: str  # stock, crypto, commodity

@dataclass
class MarketData:
    symbol: str
    price: float
    timestamp: str

@dataclass
class Signal:
    asset: str
    action: str  # BUY, SELL, HOLD
    confidence: float
    reasons: List[str]
    id: str = "" # Deterministic ID
    source_news_id: Optional[str] = None
    generated_at: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())

@dataclass
class TradeOrder:
    symbol: str
    action: str
    quantity: float
    order_id: str = ""
    signal_id: str = ""
    order_type: str = "MARKET"
    price_limit: Optional[float] = None
