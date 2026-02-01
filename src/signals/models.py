from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
import uuid

@dataclass
class Signal:
    asset: str              # e.g. "AAPL"
    action: str             # BUY | SELL | HOLD
    confidence: float       # 0.0 - 1.0
    source_news_id: str
    timestamp_utc: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    id: str = field(default_factory=lambda: f"sig_{uuid.uuid4()}")
    size_pct: float = 0.0   # desired size as % of capital
    reasons: List[str] = field(default_factory=list)
    meta: Dict = field(default_factory=dict)
