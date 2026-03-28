import time
from datetime import datetime
from shared.strategy_selector import StrategySelector
from shared.volatility_filter import VolatilityFilter
from shared.profit_optimizer import ProfitOptimizer
from shared.position_manager import compute_position_size

from src.services.firebase_client import load_config, save_trade
from src.services.ml_model import MLModel

class ExecutionBot:

    def __init__(self):
        self.selector = StrategySelector()
        self.vol_filter = VolatilityFilter()
        self.optimizer = ProfitOptimizer()
        self.ml_model = MLModel()

    def compute_signal(self, features, config, strategy):
        try:
            prediction = self.ml_model.predict(features["symbol"], features)
            base_conf = prediction["confidence"]
        except Exception as e:
            print(f"⚠️ ML Model fallback triggered: {e}")
            prediction = {"signal": "HOLD", "confidence": 0.5}
            base_conf = 0.5

        strat_weight = config.get("weights", {}).get(strategy, 1.0)
        
        conf = base_conf * strat_weight
        conf *= config.get("confidence_scale", 1)
        conf += config.get("confidence_bias", 0)

        return {
            "signal": prediction["signal"],
            "raw_prob": base_conf,
            "confidence": max(0, min(1, conf))
        }

    def run(self, market):
        print("🟢 Execution started")

        while True:
            try:
                config = load_config()
                if not config:
                    time.sleep(5)
                    continue

                features = market.get_features()
                price = features["price"]

                if not self.vol_filter.allow(features):
                    continue

                strategy = self.selector.select(features)
                
                prediction = self.compute_signal(features, config, strategy)
                signal = prediction["signal"]
                confidence = prediction["confidence"]

                if signal == "HOLD":
                    continue

                if self.optimizer.block(signal, confidence, features):
                    continue

                size = compute_position_size(
                    confidence,
                    trust=config.get("trust", 1)
                )

                trade = {
                    "symbol": features["symbol"],
                    "signal": signal,
                    "confidence": confidence,
                    "strategy": strategy,
                    "price": price,
                    "size": size,
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "OPEN",
                    "self_eval": {
                        "predicted": prediction["raw_prob"]
                    }
                }

                save_trade(trade)

                print(f"✅ {signal} {confidence:.2f} (strat: {strategy})")

                time.sleep(5)

            except Exception as e:
                print("❌ ERROR:", e)
                time.sleep(5)