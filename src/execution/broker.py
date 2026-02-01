from src.models import TradeOrder
from src.utils.config_loader import get_config
from src.utils.state_manager import get_state_manager
from src.utils.logger import get_logger

logger = get_logger("Broker")

class Broker:
    def __init__(self):
        self.mode = get_config("system.mode", "paper")
        self.dry_run = get_config("system.dry_run", True)
        self.state_manager = get_state_manager()

    def execute(self, order: TradeOrder) -> bool:
        """
        Executes order. Returns True if successful.
        """
        if self.state_manager.is_emergency_stop():
            logger.critical("EMERGENCY STOP ENABLED. Skipping execution.")
            return False

        # Idempotency Check
        if order.order_id and self.state_manager.order_exists(order.order_id):
            logger.warning(f"Skipping duplicate order {order.order_id}")
            return True # Treat as success

        if self.dry_run:
            logger.info(f"[DRY RUN] Would execute: {order.action} {order.quantity} {order.symbol}")
            return True

        if self.mode == "paper":
            return self._execute_paper(order)
        elif self.mode == "live":
            logger.critical("LIVE TRADING NOT IMPLEMENTED")
            return False
        
        return False

    def reconcile_orders(self):
        """
        Checks for PENDING/SUBMITTED orders on startup and queries broker for actual status.
        """
        logger.info("Reconciling orders...")
        history = self.state_manager.state.get("order_history", [])
        updated = False
        import datetime
        
        for i, order in enumerate(history):
            status = order.get("status", "UNKNOWN")
            if status in ["PENDING", "SUBMITTED"]:
                order_id = order.get('order_id')
                logger.info(f"Reconciling order {order_id} (Current Status: {status})")
                
                try:
                    # Query broker for actual status
                    broker_status = self.get_order_status(order_id)
                    
                    if broker_status == "FILLED":
                        logger.info(f"Order {order_id} was FILLED")
                        history[i]["status"] = "FILLED"
                        history[i]["reconciled_at"] = datetime.datetime.utcnow().isoformat()
                        
                        # Only apply to portfolio if not already applied
                        if not order.get("applied_to_portfolio"):
                            self._apply_fill_to_portfolio(order)
                            history[i]["applied_to_portfolio"] = True
                        updated = True
                        
                    elif broker_status == "FAILED":
                        logger.info(f"Order {order_id} FAILED")
                        history[i]["status"] = "FAILED"
                        history[i]["reconciled_at"] = datetime.datetime.utcnow().isoformat()
                        updated = True
                        
                    else:
                        # Still PENDING/SUBMITTED - update last check timestamp
                        history[i]["last_checked_utc"] = datetime.datetime.utcnow().isoformat()
                        logger.info(f"Order {order_id} still {broker_status}")
                        updated = True
                        
                except Exception as e:
                    logger.error(f"Failed to reconcile order {order_id}: {e}")
                    # Keep status as is, will retry next startup
                
        if updated:
            self.state_manager.save_state()
            logger.info("Reconciliation complete.")
        else:
            logger.info("No stale orders found.")

    def get_order_status(self, order_id: str) -> str:
        """
        Query broker/exchange for order status.
        For paper mode, simulate by checking if order exists in filled history.
        For live mode, query actual broker API.
        """
        if self.mode == "paper":
            # In paper mode, if we have a PENDING order it means execution didn't complete
            # Check if it's in history as FILLED - if not, it failed
            history = self.state_manager.state.get("order_history", [])
            for order in history:
                if order.get("order_id") == order_id and order.get("status") == "FILLED":
                    return "FILLED"
            # If PENDING and not found as FILLED, assume it failed during crash
            return "FAILED"
        elif self.mode == "live":
            # TODO: Implement live broker API query
            logger.warning("Live broker status query not implemented")
            return "UNKNOWN"
        
        return "UNKNOWN"

    def _apply_fill_to_portfolio(self, order):
        """Apply a filled order to the portfolio."""
        try:
            portfolio = self.state_manager.get_portfolio()
            cash = portfolio["cash"]
            positions = portfolio["positions"]
            
            symbol = order.get("symbol")
            action = order.get("action")
            quantity = order.get("quantity", 0)
            price = order.get("price", 0)
            
            cost = price * quantity
            
            if action == "BUY":
                portfolio["cash"] -= cost
                positions[symbol] = positions.get(symbol, 0.0) + quantity
            elif action == "SELL":
                portfolio["cash"] += cost
                positions[symbol] = positions.get(symbol, 0.0) - quantity
                if positions[symbol] <= 0:
                    del positions[symbol]
            
            self.state_manager.update_portfolio(portfolio["cash"], positions)
            logger.info(f"Applied {action} {quantity} {symbol} @ {price} to portfolio")
            
        except Exception as e:
            logger.error(f"Failed to apply fill to portfolio: {e}")

    def _execute_paper(self, order: TradeOrder) -> bool:
        portfolio = self.state_manager.get_portfolio()
        cash = portfolio["cash"]
        positions = portfolio["positions"]
        
        if not hasattr(self, 'market_data') or not self.market_data:
             logger.error("Broker needs MarketData")
             return False
        
        price = self.market_data.get_current_price(order.symbol)
        if not price:
            return False

        cost = price * order.quantity
        
        # Simulate PENDING -> FILLED
        now_iso = __import__('datetime').datetime.utcnow().isoformat()
        
        if order.action == "BUY":
            if cost > cash:
                 logger.error("Insufficient funds during execution")
                 # Record FAILED order
                 self.state_manager.add_order({
                     "order_id": order.order_id,
                     "signal_id": order.signal_id,
                     "status": "FAILED",
                     "reason": "Insufficient funds",
                     "timestamp": now_iso
                 })
                 return False
            portfolio["cash"] -= cost
            current_qty = positions.get(order.symbol, 0.0)
            positions[order.symbol] = current_qty + order.quantity
            
        elif order.action == "SELL":
            current_qty = positions.get(order.symbol, 0.0)
            if current_qty < order.quantity:
                logger.error("Insufficient position to sell")
                self.state_manager.add_order({
                     "order_id": order.order_id,
                     "signal_id": order.signal_id,
                     "status": "FAILED",
                     "reason": "Insufficient position",
                     "timestamp": now_iso
                 })
                return False
            portfolio["cash"] += cost
            positions[order.symbol] = current_qty - order.quantity
            if positions[order.symbol] <= 0:
                del positions[order.symbol]

        self.state_manager.update_portfolio(portfolio["cash"], positions)
        
        # Record Order FILLED
        order_record = {
            "order_id": order.order_id,
            "signal_id": order.signal_id,
            "symbol": order.symbol,
            "action": order.action,
            "quantity": order.quantity,
            "price": price,
            "status": "FILLED",
            "timestamp": now_iso
        }
        self.state_manager.add_order(order_record)
        
        logger.info(f"PAPER EXECUTION: {order.action} {order.quantity} {order.symbol} @ {price}")
        return True

    def set_market_data(self, md):
        self.market_data = md
