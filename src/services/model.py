from src.services.strategy_selector import StrategySelector
from src.services.firebase_client import load_weights

selector = StrategySelector()


def predict_signal(features, weights=None):

    if weights is None:
        weights = load_weights()

    strategy = selector.select(features)

    rsi = features.get("rsi_m15", 0)
    macd = features.get("macd_m15", 0)
    ema = features.get("ema_m15", 0)
    bb = features.get("bb_m15", 0)

    # =========================
    # 🎯 BASE STRATEGY SCORE
    # =========================
    if strategy == "TREND_LONG":
        score = ema + macd + (rsi - 0.5)

    elif strategy == "TREND_SHORT":
        score = -(ema + macd + (rsi - 0.5))

    elif strategy == "BREAKOUT":
        score = abs(bb - 0.5) + abs(macd)

    else:  # MEAN REVERSION
        score = -(rsi - 0.5) - (bb - 0.5)

    # =========================
    # 🧠 STRATEGY WEIGHTS (SELF LEARNING)
    # =========================
    strat_weights = weights.get("strategy", {})
    strat_weight = strat_weights.get(strategy, 1.0)

    score *= strat_weight

    # =========================
    # 📊 SIGNAL
    # =========================
    if score > 0.1:
        signal = "BUY"
    elif score < -0.1:
        signal = "SELL"
    else:
        signal = "HOLD"

    confidence = min(abs(score), 1.0)

    print(f"🧠 Strategy: {strategy} (w={round(strat_weight,2)})")

    return signal, confidence