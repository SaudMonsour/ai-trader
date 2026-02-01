import json
import os
import datetime
import portalocker
from contextlib import contextmanager
from src.utils.logger import get_logger

logger = get_logger("StateManager")

class StateManager:
    def __init__(self, state_file="data/state.json"):
        self.state_file = state_file
        self.lock_file = state_file + ".lock"
        self.state = {
            "last_run_utc": None,
            "processed_news_ids": [],
            "signals": [],  # Store recent signals
            "portfolio": {
                "cash": 100000.0,
                "positions": {}
            }
        }
        self.load_state()

    @contextmanager
    def _lock(self):
        """Acquire exclusive lock for state file operations."""
        os.makedirs(os.path.dirname(self.lock_file) or ".", exist_ok=True)
        lock_fh = open(self.lock_file, 'w')
        try:
            portalocker.lock(lock_fh, portalocker.LOCK_EX)
            yield
        finally:
            portalocker.unlock(lock_fh)
            lock_fh.close()

    def load_state(self):
        if os.path.exists(self.state_file):
            try:
                with self._lock():
                    with open(self.state_file, 'r') as f:
                        self.state = json.load(f)
                # Ensure all keys exist
                if "processed_news_ids" not in self.state:
                    self.state["processed_news_ids"] = []
                if "portfolio" not in self.state:
                    self.state["portfolio"] = {"cash": 100000.0, "positions": {}}
                if "order_history" not in self.state:
                    self.state["order_history"] = []
                if "open_orders" not in self.state:
                    self.state["open_orders"] = []
                if "signals" not in self.state:
                    self.state["signals"] = []
            except Exception as e:
                logger.error(f"Failed to load state: {e}")
        else:
            logger.warning("State file not found, using default state.")
            self.save_state()

    def save_state(self):
        self.state["last_run_utc"] = datetime.datetime.utcnow().isoformat()
        
        with self._lock():
            # Atomic Write: Write to temp then rename
            import tempfile
            dir_name = os.path.dirname(self.state_file)
            os.makedirs(dir_name, exist_ok=True)
            
            fd, tmp_path = tempfile.mkstemp(dir=dir_name, text=True)
            try:
                with os.fdopen(fd, 'w') as f:
                    json.dump(self.state, f, indent=2)
                    f.flush()
                    os.fsync(f.fileno()) # Ensure file content durability
                
                # Atomic replace
                os.replace(tmp_path, self.state_file)
                
                # Attempt to fsync directory (best effort for durability)
                if hasattr(os, 'O_DIRECTORY'):
                    try:
                        dir_fd = os.open(dir_name, os.O_DIRECTORY)
                        os.fsync(dir_fd)
                        os.close(dir_fd)
                    except Exception:
                        pass
            except Exception as e:
                # Cleanup temp on failure
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                logger.error(f"Failed to save state: {e}")
                raise e

    def is_emergency_stop(self):
        return self.state.get("emergency_stop", False)

    def set_emergency_stop(self, enabled: bool):
        self.state["emergency_stop"] = enabled
        self.save_state()

    def add_order(self, order_dict):
        """Adds an executed order to history."""
        if "order_history" not in self.state:
            self.state["order_history"] = []
        self.state["order_history"].append(order_dict)
        # Keep healthy size
        if len(self.state["order_history"]) > 1000:
             self.state["order_history"] = self.state["order_history"][-1000:]
        self.save_state()

    def order_exists(self, order_id):
        # Check history
        history = self.state.get("order_history", [])
        for o in history:
            if o.get("order_id") == order_id:
                return True
        return False

    def is_news_processed(self, news_id):
        return news_id in self.state["processed_news_ids"]

    def mark_news_processed(self, news_id):
        if news_id not in self.state["processed_news_ids"]:
            self.state["processed_news_ids"].append(news_id)
            # Limit size of processed IDs to avoid infinite growth? Maybe keep last 1000.
            if len(self.state["processed_news_ids"]) > 5000:
                self.state["processed_news_ids"] = self.state["processed_news_ids"][-4000:]
            self.save_state()

    def update_portfolio(self, cash, positions):
        self.state["portfolio"]["cash"] = cash
        self.state["portfolio"]["positions"] = positions
        self.save_state()

    def get_portfolio(self):
        return self.state["portfolio"]

    def add_signal(self, signal_obj):
        """Adds a generated signal to history."""
        if "signals" not in self.state:
            self.state["signals"] = []
        
        # Avoid duplicate IDs
        if any(s["id"] == signal_obj.id for s in self.state["signals"]):
            return

        # Convert dataclass to dict if needed
        import dataclasses
        if dataclasses.is_dataclass(signal_obj):
            sig_dict = dataclasses.asdict(signal_obj)
        else:
            sig_dict = signal_obj

        self.state["signals"].append(sig_dict)
        # Keep last 1000
        if len(self.state["signals"]) > 1000:
            self.state["signals"] = self.state["signals"][-1000:]
        self.save_state()

    def get_signals(self, limit=100):
        return self.state.get("signals", [])[-limit:][::-1] # Newest first

# Global Instance
_state_manager = StateManager()

def get_state_manager():
    return _state_manager
