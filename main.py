import time
import random

from src.services.meta_agent import MetaAgent
from src.services.feature_engine import FeatureEngine
from src.services.portfolio_manager import PortfolioManager
from src.services.firebase_client import save_signal, save_meta_state

agent = MetaAgent()
fe = FeatureEngine()
pf = PortfolioManager()

loop = 0


def render_progress(p):
    score = int(p["winrate"] * 100)
    filled = score // 5
    bar = "█" * filled + "-" * (20 - filled)

    if score < 30:
        color = "\033[91m"
    elif score < 60:
        color = "\033[93m"
    else:
        color = "\033[92m"

    print(f"\n📊 {color}[{bar}] {score}%\033[0m")
    print(p)


def fake_prices():
    return {
        "BTCUSDT": 100 + random.uniform(-1, 1),
        "ETHUSDT": 50 + random.uniform(-1, 1),
    }


def run():
    global loop
    loop += 1

    print("\n=== LOOP", loop, "===")

    prices = fake_prices()

    # ─── UPDATE TRADES ─────────────────
    closed = pf.update_trades(prices)

    for trade, profit, result in closed:
        trade["signal"] = trade["action"]

        # 🔥 SAVE (write only)
        save_signal({
            "symbol": trade["symbol"],
            "signal": trade["signal"],
            "profit": profit,
            "result": result,
            "features": trade.get("features", {}),
        })

        # 🔥 EVENT LEARNING (NO READS)
        agent.learn_from_trade({
            "profit": profit,
            "result": result,
            "signal": trade["signal"],
            "features": trade.get("features", {}),
        })

    print("Closed:", len(closed))

    # ─── NEW TRADES ───────────────────
    for s, price in prices.items():
        fe.update(s, price)
        f = fe.build(s)

        action, conf = agent.decide(f)
        trade, _ = pf.open_trade(s, action, price, conf)

        if trade:
            trade["features"] = f

    # ─── PROGRESS ─────────────────────
    render_progress(agent.last_stats)

    # ─── SAVE META (LOW WRITE) ────────
    if loop % 10 == 0:
        save_meta_state({
            "progress": agent.last_stats,
            "bias": agent.bias,
            "patterns": len(agent.patterns),
        })

    pf.print_status()


if __name__ == "__main__":
    print("🔥 EVENT-DRIVEN BOT START")

    while True:
        run()
        time.sleep(5)