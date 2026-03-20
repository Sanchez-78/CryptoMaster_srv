import numpy as np


def ema(prices, period=14):
    return np.mean(prices[-period:])


def rsi(prices, period=14):
    deltas = np.diff(prices)

    gains = [d for d in deltas[-period:] if d > 0]
    losses = [-d for d in deltas[-period:] if d < 0]

    avg_gain = np.mean(gains) if gains else 0
    avg_loss = np.mean(losses) if losses else 0

    if avg_loss == 0:
        return 1

    rs = avg_gain / avg_loss
    return rs / (1 + rs)


def macd(prices):
    return ema(prices, 12) - ema(prices, 26)


def bollinger(prices, period=20):
    ma = np.mean(prices[-period:])
    std = np.std(prices[-period:])

    if std == 0:
        return 0.5

    lower = ma - 2 * std
    upper = ma + 2 * std

    return (prices[-1] - lower) / (upper - lower)


def atr(candles, period=14):
    trs = []

    for i in range(1, len(candles)):
        high = candles[i]["high"]
        low = candles[i]["low"]
        prev_close = candles[i - 1]["close"]

        tr = max(
            high - low,
            abs(high - prev_close),
            abs(low - prev_close)
        )

        trs.append(tr)

    if len(trs) < period:
        return 0

    return sum(trs[-period:]) / period


def extract_features(candles):
    closes = np.array([c["close"] for c in candles])

    return {
        "rsi": float(rsi(closes)),
        "macd": float(macd(closes) / closes[-1]),
        "ema": float((ema(closes) - closes[-1]) / closes[-1]),
        "bb": float(bollinger(closes)),
        "atr": float(atr(candles) / closes[-1])
    }


def extract_multi_tf_features(candles_m15, candles_h1, candles_h4):
    f15 = extract_features(candles_m15)
    f1h = extract_features(candles_h1)
    f4h = extract_features(candles_h4)

    features = {}

    # merge
    for k, v in f15.items():
        features[f"{k}_m15"] = v

    for k, v in f1h.items():
        features[f"{k}_h1"] = v

    for k, v in f4h.items():
        features[f"{k}_h4"] = v

    # =========================
    # TREND
    # =========================
    trend_score = (
        f15.get("ema", 0) +
        f1h.get("ema", 0) * 2 +
        f4h.get("ema", 0) * 3
    )

    if trend_score > 0.001:
        trend = "BULL"
    elif trend_score < -0.001:
        trend = "BEAR"
    else:
        trend = "NEUTRAL"

    features["trend"] = trend

    # =========================
    # VOLATILITY
    # =========================
    atr_val = f15.get("atr", 0)

    if atr_val < 0.002:
        volatility = "LOW"
    elif atr_val > 0.02:
        volatility = "HIGH"
    else:
        volatility = "NORMAL"

    features["volatility"] = volatility

    # =========================
    # REGIME
    # =========================
    ema_m15 = f15.get("ema", 0)
    ema_h1 = f1h.get("ema", 0)
    ema_h4 = f4h.get("ema", 0)

    bb = f15.get("bb", 0)

    trend_strength = abs(ema_m15) + abs(ema_h1) * 2 + abs(ema_h4) * 3

    is_sideways = trend_strength < 0.002 and 0.4 < bb < 0.6
    is_volatile = atr_val > 0.02

    if is_sideways:
        regime = "SIDEWAYS"
    elif is_volatile:
        regime = "VOLATILE"
    elif ema_h4 > 0 and ema_h1 > 0:
        regime = "BULL_TREND"
    elif ema_h4 < 0 and ema_h1 < 0:
        regime = "BEAR_TREND"
    else:
        regime = "UNCERTAIN"

    features["regime"] = regime

    return features