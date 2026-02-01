import yfinance as yf
from src.utils.logger import get_logger

logger = get_logger("MarketData")

class MarketDataFetcher:
    def __init__(self):
        pass

    def get_current_price(self, symbol: str) -> float:
        try:
            ticker = yf.Ticker(symbol)
            # fast_info is faster than history
            price = ticker.fast_info.last_price
            if price is None:
                 # Fallback
                 hist = ticker.history(period="1d")
                 if not hist.empty:
                     price = hist['Close'].iloc[-1]
            return price
        except Exception as e:
            logger.error(f"Failed to fetch price for {symbol}: {e}")
            return None

    def get_prices(self, symbols: list) -> dict:
        prices = {}
        # yfinance can download multiple
        if not symbols:
            return {}
        try:
            # downloading multiple might be faster
            data = yf.download(symbols, period="1d", progress=False)['Close']
            if len(symbols) == 1:
                # data is series
                 val = data.iloc[-1]
                 prices[symbols[0]] = float(val)
            else:
                # data is dataframe
                last_row = data.iloc[-1]
                for sym in symbols:
                    if sym in last_row:
                        prices[sym] = float(last_row[sym])
        except Exception as e:
            logger.error(f"Batch fetch failed: {e}")
            # Fallback to individual
            for sym in symbols:
                p = self.get_current_price(sym)
                if p:
                    prices[sym] = p
        return prices
