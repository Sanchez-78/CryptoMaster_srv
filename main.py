import time
import random

from src.services.meta_agent import MetaAgent
from src.services.feature_engine import FeatureEngine
from src.services.portfolio_manager import PortfolioManager
from src.services.firebase_client import (
    load_recent_trades,
    load_compressed_trades,
    load_meta,
    save_meta_state,
)
from src.services.auto_cleaner import run_cleanup
from src.services.data_cache import DataCache

agent = MetaAgent()
fe = FeatureEngine()
pf = PortfolioManager()
cache = DataCache()

loop = 0


# 🔥 PROGRESS BAR
def render_progress(p):
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
    print(p)


# 🔥 DB USAGE (bez reads navíc)
def render_db_usage():
    meta = cache.get("meta", load_meta)

    counts = meta.get("counts", {"signals": 0, "compressed": 0})
    raw = counts.get("signals", 0)
    comp = counts.get("compressed", 0)

    total = raw + comp
    MAX = 10000

    pct = min(int((total / MAX) * 100), 100)
    filled = pct // 5
    bar = "█" * filled + "-" * (20 - filled)

    if pct < 50:
        color = "\033[92m"
        emoji = "🟢"
    elif pct < 80:
        color = "\033[93m"
        emoji = "🟡"
    else:
        color = "\033[91m"
        emoji = "🔴"

    print(f"\n💾 DB USAGE:")
    print(f"RAW={raw} COMP={comp}")
    print(f"{emoji} {color}[{bar}] {pct}%\033[0m")


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

    for t, profit, result in closed:
        t["signal"] = t["action"]

    print("Closed:", len(closed))

    # ─── NEW TRADES ───────────────────
    for s, price in prices.items():
        fe.update(s, price)
        f = fe.build(s)

        print(
            f"{s} regime={f['market_regime']} "
            f"trend={round(f['trend_strength'],5)} "
            f"vol={round(f['vol_10'],5)}"
        )

        action, conf = agent.decide(f)
        trade, _ = pf.open_trade(s, action, price, conf)

        if trade:
            trade["features"] = f

    # ─── LEARNING (🔥 CACHE) ──────────
    raw_trades = cache.get("raw", lambda: load_recent_trades(100))
    comp_trades = cache.get("comp", lambda: load_compressed_trades(100))

    print(f"RAW={len(raw_trades)} COMP={len(comp_trades)}")

    # 🔥 optional sampling (ještě méně CPU)
    raw_sample = random.sample(raw_trades, min(len(raw_trades), 50))
    comp_sample = random.sample(comp_trades, min(len(comp_trades), 50))

    agent.learn_from_history(raw_sample)
    agent.learn_from_compressed(comp_sample)

    # ─── PROGRESS ─────────────────────
    progress = agent.get_progress()
    render_progress(progress)

    # ─── SAVE META (počítadla) ────────
    meta = cache.get("meta", load_meta)

    counts = meta.get("counts", {"signals": 0, "compressed": 0})

    counts["signals"] += len(closed)

    save_meta_state({
        "counts": counts,
        "progress": progress,
    })

    # ─── DB USAGE ─────────────────────
    render_db_usage()

    pf.print_status()

    # 🔥 CLEANUP MÉNĚ ČASTO
    if loop % 200 == 0:
        run_cleanup()

    print("==========================")


if __name__ == "__main__":
    print("🔥 BOT START (LOW READ MODE)")

    while True:
        run()
        time.sleep(5)