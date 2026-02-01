from typing import Optional
from src.models import Signal, TradeOrder
from src.utils.config_loader import get_config
from src.utils.state_manager import get_state_manager
from src.utils.logger import get_logger

logger = get_logger("RiskManager")

class RiskManager:
    def __init__(self):
        self.risk_per_trade_pct = get_config("risk.risk_per_trade_pct", 0.5)
        self.max_pos_size_pct = get_config("risk.max_position_size_pct", 10.0)
        self.state_manager = get_state_manager()
        self.market_data = None # Dependency Injection later

    def set_market_data(self, market_data_fetcher):
        self.market_data = market_data_fetcher

    def evaluate(self, signal: Signal, portfolio: dict) -> dict:
        """
        Returns {allow: bool, size_pct: float, reason: str, quantity: float, price: float}
        """
        result = {"allow": False, "reason": "Unknown", "quantity": 0.0, "price": 0.0}
        
        cash = portfolio["cash"]
        equity = cash # Approx
        
        # 1. Price Check
        if not self.market_data:
            result["reason"] = "Market Data disconnected"
            return result
            
        price = self.market_data.get_current_price(signal.asset)
        if not price or price <= 0:
            result["reason"] = f"Invalid price for {signal.asset}"
            return result
        result["price"] = price

        # 2. Risk Calculations
        max_allocation = equity * (self.max_pos_size_pct / 100.0)
        default_stop_loss_pct = 0.05
        risk_amount = equity * (self.risk_per_trade_pct / 100.0)
        position_value = risk_amount / default_stop_loss_pct
        
        # Cap at Max Position Size
        if position_value > max_allocation:
             position_value = max_allocation
             # logger.debug(f"Capped at max allocation {max_allocation}")

        # Check available cash with Buffer (1% for fees/slippage)
        fee_buffer_pct = 0.01
        required_cash = position_value * (1.0 + fee_buffer_pct)
        
        if required_cash > cash:
            result["reason"] = f"Insufficient cash with buffer (Required: {required_cash:.2f}, Avail: {cash:.2f})"
            return result
            
        quantity = position_value / price
        if quantity <= 0:
            result["reason"] = "Quantity zero"
            return result

        result["allow"] = True
        result["quantity"] = quantity
        result["reason"] = "Risk checks passed"
        return result

    def check_risk(self, signal: Signal) -> Optional[TradeOrder]:
        """
        Legacy wrapper for backward compat if needed, or main entry.
        """
        portfolio = self.state_manager.get_portfolio()
        evaluation = self.evaluate(signal, portfolio)
        
        if not evaluation["allow"]:
            logger.warning(f"Risk Rejected {signal.asset}: {evaluation['reason']}")
            return None
            
        import uuid
        # Generate Order ID (Deterministic based on signal ID + attempt? or just unique?)
        # For idempotency, we want order_id to be tied to signal_id.
        # But we might retry? 
        # Let's simple SHA1(signal.id) for now.
        import hashlib
        order_id = hashlib.sha1(f"{signal.id}|order".encode()).hexdigest()

        order = TradeOrder(
            order_id=order_id,
            signal_id=signal.id,
            symbol=signal.asset,
            action=signal.action,
            quantity=evaluation["quantity"],
            order_type="MARKET"
        )
        
        logger.info(f"Risk Approved: {signal.action} {order.quantity:.4f} {signal.asset}")
        return order
