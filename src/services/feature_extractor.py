import numpy as np


def extract_features(candles):
    # ❗ ochrana proti prázdným datům
    if not candles or len(candles) < 20:
        return None

    closes = np.array([c["close"] for c in candles])

    try:
        return {
            "rsi": float(np.mean(closes[-14:]) / closes[-1]),
            "macd": float((closes[-1] - np.mean(closes[-26:])) / closes[-1]),
            "ema": float((np.mean(closes[-10:]) - closes[-1]) / closes[-1]),
            "bb": float((np.max(closes[-20:]) - closes[-1]) / closes[-1]),
            "atr": float(np.mean(np.abs(np.diff(closes[-14:]))) / closes[-1])
        }
    except Exception as e:
        print("❌ Feature error:", e)
        return None


def extract_multi_tf_features(candles_m15, candles_h1, candles_h4):
    f15 = extract_features(candles_m15)
    f1 = extract_features(candles_h1)
    f4 = extract_features(candles_h4)

    # ❗ ochrana
    if not f15 or not f1 or not f4:
        return None

    return {
        "rsi_m15": f15["rsi"],
        "macd_m15": f15["macd"],
        "ema_m15": f15["ema"],
        "bb_m15": f15["bb"],
        "atr_m15": f15["atr"],

        "rsi_h1": f1["rsi"],
        "macd_h1": f1["macd"],
        "ema_h1": f1["ema"],
        "bb_h1": f1["bb"],
        "atr_h1": f1["atr"],

        "rsi_h4": f4["rsi"],
        "macd_h4": f4["macd"],
        "ema_h4": f4["ema"],
        "bb_h4": f4["bb"],
        "atr_h4": f4["atr"],

        "trend": "BULL" if f4["ema"] > 0 else "BEAR",
        "volatility": "HIGH" if f15["atr"] > 0.01 else "NORMAL",
        "regime": "BULL_TREND" if f4["ema"] > 0 else "RANGE",

        "price": candles_m15[-1]["close"]
    }