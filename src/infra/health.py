"""
FastAPI Health & Metrics Endpoint
Provides readiness and liveness checks for orchestration.
"""
from fastapi import FastAPI
import os
import json
from pathlib import Path
from datetime import datetime

app = FastAPI(title="Trading Agent Health API")
STATE_FILE = Path("data/state.json")

def read_state():
    """Read current state from state.json."""
    try:
        with STATE_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
def health():
    """
    Health check endpoint.
    Returns current system status and key metrics.
    """
    state = read_state()
    mode = os.getenv("SYSTEM_MODE", state.get("mode", "unknown"))
    emergency = state.get("emergency_stop", False)
    cash = state.get("portfolio", {}).get("cash", None)
    last_run = state.get("last_run_utc", None)
    
    # Count orders by status
    order_history = state.get("order_history", [])
    filled_count = sum(1 for o in order_history if o.get("status") == "FILLED")
    failed_count = sum(1 for o in order_history if o.get("status") == "FAILED")
    pending_count = sum(1 for o in order_history if o.get("status") in ["PENDING", "SUBMITTED"])
    
    return {
        "status": "healthy" if not emergency else "emergency_stop_active",
        "mode": mode,
        "emergency_stop": emergency,
        "portfolio": {
            "cash": cash,
            "positions_count": len(state.get("portfolio", {}).get("positions", {}))
        },
        "orders": {
            "filled": filled_count,
            "failed": failed_count,
            "pending": pending_count,
            "total": len(order_history)
        },
        "last_run_utc": last_run,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/ready")
def ready():
    """
    Readiness check endpoint.
    Returns whether the system is ready to accept traffic.
    """
    try:
        state = read_state()
        # Check if state has required keys
        required_keys = ["portfolio", "processed_news_ids"]
        if all(k in state for k in required_keys):
            return {"ready": True, "timestamp": datetime.utcnow().isoformat()}
        else:
            return {"ready": False, "reason": "State missing required keys"}
    except Exception as e:
        return {"ready": False, "reason": str(e)}

@app.get("/metrics")
def metrics():
    """
    Prometheus-compatible metrics endpoint.
    Returns basic counters for monitoring.
    """
    state = read_state()
    order_history = state.get("order_history", [])
    
    # Count by status
    filled = sum(1 for o in order_history if o.get("status") == "FILLED")
    failed = sum(1 for o in order_history if o.get("status") == "FAILED")
    pending = sum(1 for o in order_history if o.get("status") in ["PENDING", "SUBMITTED"])
    
    # Simple Prometheus text format
    metrics_text = f"""# HELP orders_total Total number of orders
# TYPE orders_total counter
orders_total{{status="filled"}} {filled}
orders_total{{status="failed"}} {failed}
orders_total{{status="pending"}} {pending}

# HELP portfolio_cash Current cash balance
# TYPE portfolio_cash gauge
portfolio_cash {state.get("portfolio", {}).get("cash", 0)}

# HELP emergency_stop Emergency stop flag
# TYPE emergency_stop gauge
emergency_stop {1 if state.get("emergency_stop", False) else 0}

# HELP processed_news_total Total processed news items
# TYPE processed_news_total counter
processed_news_total {len(state.get("processed_news_ids", []))}
"""
    
    return metrics_text

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
