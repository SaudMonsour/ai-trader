from datetime import datetime, timezone

class PaperBroker:
    def __init__(self, state_manager, logger):
        self.state = state_manager
        self.log = logger

    def place_order(self, signal):
        # simple simulated execution: market price is mocked as last price = 1 for simplicity
        size_pct = 0.01  # placeholder sizing; integrate risk manager later
        cash = self.state.state["portfolio"]["cash"]
        amount = cash * size_pct
        # simulate buy or sell
        if signal.action == "BUY":
            qty = amount / 1.0
            positions = self.state.state["portfolio"]["positions"]
            positions.setdefault(signal.asset, {"qty": 0, "avg_price": 0})
            prev = positions[signal.asset]
            prev_qty = prev["qty"]
            prev_avg = prev["avg_price"]
            new_qty = prev_qty + qty
            if prev_qty == 0:
                new_avg = 1.0
            else:
                new_avg = (prev_avg*prev_qty + 1.0*qty) / new_qty
            prev["qty"] = new_qty
            prev["avg_price"] = new_avg
            self.state.state["portfolio"]["cash"] = cash - amount
            self.state.save()
            self.log.info({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "component": "execution.paper",
                "event": "order_filled",
                "signal_id": signal.id,
                "asset": signal.asset,
                "action": signal.action,
                "qty": qty
            })
            return True
        # SELL handling (simplified)
        if signal.action == "SELL":
            positions = self.state.state["portfolio"]["positions"]
            pos = positions.get(signal.asset)
            if not pos or pos["qty"] <= 0:
                return False
            qty = pos["qty"] * 0.5  # sell half
            pos["qty"] -= qty
            self.state.state["portfolio"]["cash"] = cash + qty * 1.0
            self.state.save()
            self.log.info({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "component": "execution.paper",
                "event": "order_filled",
                "signal_id": signal.id,
                "asset": signal.asset,
                "action": signal.action,
                "qty": qty
            })
            return True
        return False
