class OrderManager:
    def __init__(self, broker, logger):
        self.broker = broker
        self.log = logger

    def handle(self, signal, mode="dry_run"):
        record = {
            "timestamp": signal.timestamp_utc,
            "signal_id": signal.id,
            "asset": signal.asset,
            "action": signal.action,
            "confidence": signal.confidence,
            "mode": mode
        }
        self.log.info(record)
        if mode == "dry_run":
            return {"executed": False}
        if mode == "paper":
            ok = self.broker.place_order(signal)
            record["executed"] = ok
            self.log.info(record)
            return {"executed": ok}
        return {"executed": False}
