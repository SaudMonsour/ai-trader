from dataclasses import dataclass, field
from typing import List, Optional, Dict

@dataclass
class Signal:
    id: str
    timestamp_utc: str
    asset: str
    action: str
    confidence: float
    size_pct_suggested: float
    reasons: List[str]
    source_news_id: str
    metadata: Optional[Dict] = field(default_factory=dict)
