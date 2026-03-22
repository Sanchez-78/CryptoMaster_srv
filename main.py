import time
from datetime import datetime, UTC

from src.services.meta_agent import MetaAgent
from src.services.feature_engine import FeatureEngine
from src.services.portfolio_manager import PortfolioManager

# 🔥 DEBUG MODE
DEBUG_FORCE_CLOSE = False

SYMBOLS = ["BTCUSDT", "ETHUSDT"]

agent = MetaAgent()
fe = FeatureEngine()
portfolio = PortfolioManager()


def render_progress(p):
    score = p["score"]
    bar = "█" * (score // 5) + "-" * (20 - score // 5)

    color = "\033[91m" if score < 30 else "\033[93m" if score < 60 else "\033[92m"

    print(f"\n📊 {color}[{bar}] {score}%\033[0m")
    print(p)


def fake_prices():
    import random
    return {
        s: 100 + random.uniform(-1, 1)
        for s in SYMBOLS
    }


def run():
    prices = fake_prices()

    # UPDATE
    closed = portfolio.update_trades(prices)
    print("Closed trades:", len(closed))

    # NEW
    for s in SYMBOLS:
        price = prices[s]

        fe.update(s, price)
        f = fe.build(s)

        print(f"{s} regime={f['market_regime']} trend={round(f['trend_strength'],5)}")

        action, conf = agent.decide(f)

        trade, _ = portfolio.open_trade(s, action, price, conf)
        trade["features"] = f

        # 🔥 DEBUG BONUS
        if DEBUG_FORCE_CLOSE:
            portfolio.close_trade(trade, price * 1.002)

    # LEARNING
    trades = portfolio.trade_history
    print("Trades for learning:", len(trades))

    agent.learn_from_history(trades)

    # PROGRESS
    p = agent.get_progress()
    render_progress(p)

    portfolio.print_status()


if __name__ == "__main__":
    print("🔥 DEBUG ENGINE START")

    while True:
        run()
        time.sleep(2)