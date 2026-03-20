def compute_reward(signal, features, result, profit):
    reward = 0.0

    # =========================
    # 💰 BASE PROFIT
    # =========================
    reward += profit * 100  # scale

    # =========================
    # 📉 LOSS PENALTY
    # =========================
    if result == "LOSS":
        reward *= 1.5  # větší trest

    # =========================
    # 📈 TREND BONUS
    # =========================
    trend = features.get("trend")

    if trend == "BULL" and signal == "BUY":
        reward += 0.5
    elif trend == "BEAR" and signal == "SELL":
        reward += 0.5
    else:
        reward -= 0.2

    # =========================
    # 🌪️ VOLATILITY BONUS
    # =========================
    vol = features.get("volatility")

    if vol == "HIGH":
        reward *= 1.2
    elif vol == "LOW":
        reward *= 0.8

    # =========================
    # 🧠 REGIME BONUS
    # =========================
    regime = features.get("regime")

    if regime == "BULL_TREND" and signal == "BUY":
        reward += 0.5
    elif regime == "BEAR_TREND" and signal == "SELL":
        reward += 0.5

    # =========================
    # 💤 HOLD PENALTY
    # =========================
    if signal == "HOLD":
        reward -= 0.1

    return round(reward, 4)