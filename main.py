import time

from src.services.meta_agent import MetaAgent
from src.services.feature_engine import FeatureEngine
from src.services.portfolio_manager import PortfolioManager
from src.services.firebase_client import save_signal, save_meta_state
from src.services.market_stream import MarketStream

agent = MetaAgent()
fe = FeatureEngine()
pf = PortfolioManager()

# 🔥 REAL MARKET STREAM
stream = MarketStream(["btcusdt", "ethusdt"])
stream.start()

loop = 0


# ─────────────────────────────
# 📊 PROGRESS BAR
# ─────────────────────────────
def render_progress(p):
    if "status" in p:
        print(f"\n🧠 {p['status']} | trades={p['trades']}")
        return

    score = p["score"]
    filled = score // 5
    bar = "█" * filled + "-" * (20 - filled)

    if score < 30:
        color = "\033[91m"
        emoji = "🔴"
    elif score < 60:
        color = "\033[93m"
        emoji = "🟡"
    else:
        color = "\033[92m"
        emoji = "🟢"

    print(f"\n📊 {emoji} {color}[{bar}] {score}%\033[0m")
    print(
        f"winrate={p['winrate']} profit={p['avg_profit']} "
        f"bias={p['bias']} trades={p['trades']}"
    )


# ─────────────────────────────
# 🔥 MAIN LOOP
# ─────────────────────────────
def run():
    global loop
    loop += 1

    print(f"\n=== LOOP {loop} ===")

    # 🔥 REAL DATA
    prices = stream.get_prices()

    if not prices:
        print("⏳ čekám na data z Binance...")
        return

    # ─── UPDATE TRADES ─────────────────
    closed = pf.update_trades(prices)

    for trade, profit, result in closed:
        trade["signal"] = trade["action"]

        # 🔥 SAVE TRADE
        save_signal({
            "symbol": trade["symbol"],
            "signal": trade["signal"],
            "profit": profit,
            "result": result,
            "features": trade.get("features", {}),
        })

        # 🔥 EVENT LEARNING (0 READS)
        agent.learn_from_trade({
            "profit": profit,
            "result": result,
            "signal": trade["signal"],
            "features": trade.get("features", {}),
        })

    print(f"Closed trades: {len(closed)}")

    # ─── NEW TRADES ───────────────────
    for symbol, price in prices.items():
        fe.update(symbol, price)
        f = fe.build(symbol)

        print(
            f"{symbol} | regime={f['market_regime']} "
            f"trend={round(f['trend_strength'],5)} "
            f"vol={round(f['vol_10'],5)}"
        )

        action, conf = agent.decide(f)

        trade, status = pf.open_trade(symbol, action, price, conf)

        if trade:
            trade["features"] = f

    # ─── PROGRESS ─────────────────────
    progress = agent.get_progress()
    render_progress(progress)

    # 🔥 DEBUG CLUSTERS (každých 20 loopů)
    if loop % 20 == 0:
        agent.print_top_clusters()

    # ─── SAVE META ────────────────────
    if loop % 10 == 0:
        save_meta_state({
            "progress": progress,
            "bias": agent.bias,
            "patterns": len(agent.patterns),
            "trades": agent.total_trades,
        })

    pf.print_status()

    print("==========================")


# ─────────────────────────────
# 🚀 START
# ─────────────────────────────
if __name__ == "__main__":
    print("🔥 REAL MARKET BOT START")

    while True:
        try:
            run()
            time.sleep(3)

        except Exception as e:
            print("❌ ERROR:", e)
            time.sleep(5)