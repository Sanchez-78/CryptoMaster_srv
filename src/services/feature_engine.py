import pandas as pd
import numpy as np

def compute_indicators(candles):
    if not candles:
        return {"rsi": 0, "macd": 0, "ema": 0, "bb": 0, "atr": 0, "price": 0}

    df = pd.DataFrame(candles)
    if df.empty:
        return {"rsi": 0, "macd": 0, "ema": 0, "bb": 0, "atr": 0, "price": 0}
        
    df["close"] = df["close"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    
    # Need sufficient data for stable indicators
    if len(df) < 26:
        return {"rsi": 0, "macd": 0, "ema": 0, "bb": 0, "atr": 0, "price": df["close"].iloc[-1]}

    # RSI (14)
    delta = df["close"].diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=13, adjust=False).mean()
    ema_down = down.ewm(com=13, adjust=False).mean()
    rs = ema_up / ema_down
    df["rsi"] = 100 - (100 / (1 + rs))

    # MACD (12, 26, 9)
    exp1 = df["close"].ewm(span=12, adjust=False).mean()
    exp2 = df["close"].ewm(span=26, adjust=False).mean()
    df["macd"] = exp1 - exp2

    # EMA (14)
    df["ema"] = df["close"].ewm(span=14, adjust=False).mean()

    # Bollinger Bands (distance from price as %)
    sma = df["close"].rolling(20).mean()
    std = df["close"].rolling(20).std()
    upper = sma + (std * 2)
    lower = sma - (std * 2)
    
    # Safely calculate BB position indicator (0 to 1 scaling normally)
    bb_range = upper - lower
    df["bb"] = np.where(bb_range == 0, 0, (df["close"] - lower) / bb_range)

    # ATR (14)
    tr1 = df["high"] - df["low"]
    tr2 = (df["high"] - df["close"].shift()).abs()
    tr3 = (df["low"] - df["close"].shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df["atr"] = tr.rolling(14).mean()

    # Get latest values replacing NaNs
    latest = df.iloc[-1].fillna(0).to_dict()
    
    return {
        "rsi": float(latest.get("rsi", 0)),
        "macd": float(latest.get("macd", 0)),
        "ema": float(latest.get("ema", 0)),
        "bb": float(latest.get("bb", 0)),
        "atr": float(latest.get("atr", 0)),
        "price": float(latest.get("close", 0))
    }

class FeatureEngine:
    def __init__(self):
        pass

    def build_for_interval(self, candles):
        return compute_indicators(candles)