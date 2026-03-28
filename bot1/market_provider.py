from src.services.binance_client import fetch_candles
from src.services.feature_engine import FeatureEngine
from config import SYMBOLS

class MarketProvider:
    def __init__(self):
        self.engine = FeatureEngine()
        self.default_symbol = SYMBOLS[0] if SYMBOLS else "BTCUSDT"

    def get_features(self, symbol=None):
        target_symbol = symbol or self.default_symbol
        feature_map = {"15m": "m15", "1h": "h1", "4h": "h4"}
        
        combined_features = {
            "symbol": target_symbol,
            "regime": "BULL_TREND",  # Mocked logic for fallback safety
            "volatility": "NORMAL"
        }
        
        price = 0
        
        for bn_interval, f_prefix in feature_map.items():
            candles = fetch_candles(target_symbol, bn_interval)
            indicators = self.engine.build_for_interval(candles)
            
            combined_features[f"rsi_{f_prefix}"] = indicators["rsi"]
            combined_features[f"macd_{f_prefix}"] = indicators["macd"]
            combined_features[f"ema_{f_prefix}"] = indicators["ema"]
            combined_features[f"bb_{f_prefix}"] = indicators["bb"]
            combined_features[f"atr_{f_prefix}"] = indicators["atr"]
            
            if bn_interval == "15m":
                price = indicators["price"]
                
        combined_features["price"] = price

        # Safe fallback estimation for strategy_selector naive logic
        if combined_features.get("ema_h4", 0) > 0 and price > combined_features["ema_h4"]:
            combined_features["regime"] = "BULL_TREND"
        else:
            combined_features["regime"] = "BEAR_TREND"
            
        return combined_features