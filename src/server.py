import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import datetime

from src.utils.state_manager import get_state_manager
from src.utils.config_loader import load_config, get_config
from src.models import Signal, TradeOrder

# Load Config
load_config()
state_manager = get_state_manager()

app = FastAPI(title="Trading Agent API")

# Allow CORS for dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---
class HealthResponse(BaseModel):
    status: str
    mode: str
    emergency_stop: bool
    last_run_utc: Optional[str]
    portfolio: Dict[str, Any]
    orders: Dict[str, Any]

class SetEmergencyStopRequest(BaseModel):
    enabled: bool

# --- Endpoints ---

@app.get("/api/health")
def get_health():
    state_manager.load_state() # Refresh state from disk
    
    positions = state_manager.state["portfolio"].get("positions", {})
    cash = state_manager.state["portfolio"].get("cash", 0)
    
    # Calculate simple stats
    today_orders = 0
    # Logic for today orders could be refined
    
    return {
        "status": "healthy",
        "mode": get_config("trading.mode", "paper"),
        "emergency_stop": state_manager.is_emergency_stop(),
        "last_run_utc": state_manager.state.get("last_run_utc"),
        "portfolio": {
            "cash": cash,
            "positions": [
                {
                    "symbol": k,
                    "qty": v, # v is quantity float
                    "avg_price": 0.0, # Not tracked in MVP
                    "current_price": 0.0,
                    "unrealized_pnl": 0.0
                } for k, v in positions.items()
            ],
            "positions_count": len(positions)
        },
        "orders": {
            "today_count": len(state_manager.state.get("order_history", [])), # Simplified
            "pending": len(state_manager.state.get("open_orders", []))
        }
    }

@app.post("/api/emergency-stop")
def set_emergency_stop(req: SetEmergencyStopRequest):
    state_manager.set_emergency_stop(req.enabled)
    # If enabling stop, we probably want to signal the main bot to stop/cancel too.
    # The main bot checks is_emergency_stop() loop, but maybe slow?
    # For now, state flag is enough.
    return {"success": True, "emergency_stop": req.enabled}

@app.get("/api/signals")
def get_signals(limit: int = 100):
    state_manager.load_state()
    return {"items": state_manager.get_signals(limit=limit)}

@app.get("/api/orders")
def get_orders(limit: int = 100):
    state_manager.load_state()
    history = state_manager.state.get("order_history", [])
    # Return reverse chronological
    return {"items": history[-limit:][::-1]}

@app.get("/api/portfolio")
def get_portfolio():
    state_manager.load_state()
    data = state_manager.get_portfolio()
    
    # Transform dict positions to list for UI
    positions_list = []
    for sym, qty in data.get("positions", {}).items():
        positions_list.append({
            "symbol": sym,
            "qty": qty,
            "avg_price": 0.0,
            "current_price": 0.0, # Ensure field
            "unrealized_pnl": 0.0
        })
        
    return {
        "cash": data.get("cash", 0),
        "positions": positions_list,
        "total_value": data.get("cash", 0) # + 0 since current_price is 0
    }

@app.get("/api/logs")
def get_logs(limit: int = 100, q: str = ""):
    # Read logs from logs/ directory
    # Find latest log file
    import glob
    import os
    
    log_files = glob.glob("logs/trading_bot_*.log")
    if not log_files:
        return {"items": []}
    
    latest_log = max(log_files, key=os.path.getctime)
    
    logs = []
    try:
        with open(latest_log, 'r') as f:
            lines = f.readlines()
            # Parse last N lines
            for line in lines[-limit:]:
                # Simple parsing, assuming standard log format
                # 2024-01-01 10:00:00 - Name - LEVEL - Message
                try:
                    parts = line.strip().split(" - ")
                    if len(parts) >= 4:
                        ts = parts[0]
                        comp = parts[1]
                        lvl = parts[2]
                        msg = " - ".join(parts[3:])
                        
                        if q.lower() in msg.lower() or q.lower() in comp.lower():
                             logs.append({
                                 "timestamp": ts,
                                 "component": comp,
                                 "level": lvl,
                                 "message": msg
                             })
                except:
                    continue
    except Exception as e:
        return {"items": [{"timestamp": "", "level": "ERROR", "message": f"Failed to read logs: {e}"}]}
        
    return {"items": logs[::-1]} # Newest first

if __name__ == "__main__":
    uvicorn.run("src.server:app", host="0.0.0.0", port=8000, reload=True)
