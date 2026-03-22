class PatternCluster:

    def trend_bucket(self, t):
        if t < -0.003:
            return "T0"
        elif t < -0.001:
            return "T1"
        elif t < 0.001:
            return "T2"
        elif t < 0.003:
            return "T3"
        else:
            return "T4"

    def vol_bucket(self, v):
        if v < 0.001:
            return "V0"
        elif v < 0.002:
            return "V1"
        else:
            return "V2"

    def build(self, features, action):
        regime = features.get("market_regime", "R")
        t = features.get("trend_strength", 0)
        v = features.get("vol_10", 0)

        tb = self.trend_bucket(t)
        vb = self.vol_bucket(v)

        return f"{regime}_{tb}_{vb}_{action}"