import json
from pathlib import Path
from datetime import datetime, timezone

STATE_PATH = Path("data/state.json")
DEFAULT_STATE = {
    "last_run_utc": None,
    "processed_news_ids": [],
    "portfolio": {"cash": 100000.0, "positions": {}},
    "open_orders": []
}

class StateManager:
    def __init__(self, path=STATE_PATH):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write(DEFAULT_STATE)
        self.state = self._read()

    def _read(self):
        with self.path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, state):
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

    def save(self):
        self.state["last_run_utc"] = datetime.now(timezone.utc).isoformat()
        self._write(self.state)

    def mark_processed(self, news_id):
        if news_id not in self.state["processed_news_ids"]:
            self.state["processed_news_ids"].append(news_id)
            self.save()
