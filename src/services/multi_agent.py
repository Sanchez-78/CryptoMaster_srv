from collections import Counter

from src.services.dqn_agent import DQNAgent
from src.services.model import predict_signal
from src.services.reward_system import compute_reward


class MultiAgent:

    def __init__(self):
        self.dqn = DQNAgent()

    # =========================
    # 🤖 DECISION (VOTING)
    # =========================
    def decide(self, features):
        votes = []

        # =========================
        # 🤖 DQN
        # =========================
        dqn_signal, dqn_conf = self.dqn.act(features)
        votes.append((dqn_signal, dqn_conf))

        # =========================
        # 📊 STRATEGY MODEL
        # =========================
        try:
            strat_signal, strat_conf = predict_signal(features)
        except:
            strat_signal, strat_conf = "HOLD", 0.3

        votes.append((strat_signal, strat_conf))

        # =========================
        # ⚡ MOMENTUM AGENT
        # =========================
        momentum_signal = "HOLD"

        macd = features.get("macd_m15", 0)

        if macd > 0:
            momentum_signal = "BUY"
        elif macd < 0:
            momentum_signal = "SELL"

        votes.append((momentum_signal, 0.4))

        # =========================
        # 🗳️ VOTING
        # =========================
        counts = Counter([v[0] for v in votes])
        final_signal = counts.most_common(1)[0][0]

        # =========================
        # 📊 CONFIDENCE
        # =========================
        confs = [v[1] for v in votes if v[0] == final_signal]

        if confs:
            confidence = sum(confs) / len(confs)
        else:
            confidence = 0.3

        print("🗳️ Votes:", votes)

        return final_signal, float(min(confidence, 1.0))

    # =========================
    # 🧠 LEARNING
    # =========================
    def learn(self, signals):
        if not signals:
            return

        for s in signals[-50:]:  # víc dat = lepší learning
            try:
                if s.get("result") not in ["WIN", "LOSS"]:
                    continue

                features = s.get("features")

                if not features:
                    continue

                # 🔥 STATE
                state = self.dqn._to_vector(features)

                # 🔥 SMART REWARD
                reward = compute_reward(
                    s.get("signal"),
                    features,
                    s.get("result"),
                    s.get("profit", 0)
                )

                print(f"🎯 Reward: {reward}")

                # 🔥 STORE
                self.dqn.remember(state, s.get("signal"), reward)

            except Exception as e:
                print("❌ Learn error:", e)

        # 🔥 TRAIN
        self.dqn.replay()

        # 🔥 SAVE
        self.dqn.save()

        print("🧠 Multi-agent learning done")