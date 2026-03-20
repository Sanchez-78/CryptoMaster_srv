from datetime import datetime, UTC

from src.services.binance_client import fetch_candles
from src.services.feature_extractor import extract_multi_tf_features

from src.services.meta_agent import MetaAgent
from src.services.self_evolving import SelfEvolvingSystem
from src.services.stabilizer import Stabilizer
from src.services.auto_strategy import AutoStrategy
from src.services.real_market import RealMarket

from src.services.firebase_client import (
    save_signal,
    load_open_signals,
    load_all_signals,
)

from src.services.evaluator import evaluate_signals
from src.services.portfolio_manager import PortfolioManager
from src.services.profit_optimizer import ProfitOptimizer


SYMBOLS = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]

agent = MetaAgent()
portfolio = PortfolioManager()
optimizer = ProfitOptimizer()
evolver = SelfEvolvingSystem()
stabilizer = Stabilizer()
auto_strat = AutoStrategy()
market = RealMarket()


def run_pipeline():
    print("\n=== START PIPELINE ===\n")

    for symbol in SYMBOLS:
        try:
            print(f"\n🔍 {symbol}")

            m15 = fetch_candles(symbol, "15m")
            h1 = fetch_candles(symbol, "1h")
            h4 = fetch_candles(symbol, "4h")

            if not m15 or not h1 or not h4:
                continue

            raw_price = m15[-1]["close"]

            features = extract_multi_tf_features(m15, h1, h4)
            if not features:
                continue

            print("DEBUG FEATURES:", features)

            # =========================
            # 🤖 META AI
            # =========================
            signal, confidence = agent.decide(features)

            # =========================
            # 🧪 AUTO STRATEGY
            # =========================
            auto_signal, auto_conf = auto_strat.decide(features)
            if auto_conf > confidence:
                print("🧪 AutoStrategy override")
                signal, confidence = auto_signal, auto_conf

            print(f"🤖 FINAL: {signal} ({confidence})")

            open_signals = load_open_signals()

            # =========================
            # 🛑 STABILIZER
            # =========================
            if stabilizer.block(signal, confidence):
                continue

            # =========================
            # 🚫 OPTIMIZER
            # =========================
            if optimizer.block(signal, confidence, features, open_signals):
                continue

            if not portfolio.can_open(signal, open_signals):
                print("🚫 Portfolio limit")
                continue

            # =========================
            # 💱 REAL PRICE
            # =========================
            price = market.apply(raw_price, signal)
            print(f"💱 Raw: {raw_price} → Real: {price}")

            # =========================
            # 🧬 EVOLVING SIZE
            # =========================
            params = evolver.params
            size = (10 * confidence * params["confidence_boost"]) * params["risk_multiplier"]

            # =========================
            # 🚀 EXECUTION
            # =========================
            print("\n🚀 EXECUTING TRADE")
            print(symbol, signal, round(size, 2))

            save_signal({
                "symbol": symbol,
                "signal": signal,
                "confidence": confidence,
                "price": price,
                "features": features,
                "timestamp": datetime.now(UTC).isoformat(),
                "evaluated": False
            })

            evaluate_signals(symbol)

        except Exception as e:
            print(f"❌ {symbol} error:", e)

    # =========================
    # 🧠 LEARNING
    # =========================
    try:
        all_signals = load_all_signals()

        agent.learn(all_signals)
        stabilizer.update(all_signals)
        auto_strat.evolve(all_signals)

    except Exception as e:
        print("❌ Learning error:", e)

    # =========================
    # 📊 PERFORMANCE
    # =========================
    try:
        all_signals = load_all_signals()

        wins = sum(1 for s in all_signals if s.get("result") == "WIN")
        losses = sum(1 for s in all_signals if s.get("result") == "LOSS")

        trades = wins + losses
        winrate = (wins / trades * 100) if trades > 0 else 0
        profit = sum(s.get("profit", 0) for s in all_signals)

        print("\n📊 PERFORMANCE")
        print({
            "trades": trades,
            "winrate": round(winrate, 2),
            "profit": round(profit, 4)
        })

        # =========================
        # 🧬 EVOLVE SYSTEM
        # =========================
        evolver.evolve({
            "winrate": winrate,
            "profit": profit
        })

        agent.dqn.epsilon = evolver.params["exploration"]

    except Exception as e:
        print("❌ Performance error:", e)

    print("\n=== END PIPELINE ===\n")


if __name__ == "__main__":
    run_pipeline()