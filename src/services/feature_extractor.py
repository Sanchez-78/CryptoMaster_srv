import statistics

def _ema(values: list[float], period: int) -> list[float | None]:
k = 2 / (period + 1)
result = [None] * (period - 1)
seed = sum(values[:period]) / period
result.append(seed)

```
for v in values[period:]:
    result.append(result[-1] * (1 - k) + v * k)

return result
```

def _rsi(closes: list[float], period: int = 14) -> list[float | None]:
result = [None] * period
gains, losses = [], []

```
for i in range(1, period + 1):
    delta = closes[i] - closes[i - 1]
    gains.append(max(delta, 0))
    losses.append(max(-delta, 0))

avg_gain = sum(gains) / period
avg_loss = sum(losses) / period

for i in range(period, len(closes) - 1):
    delta = closes[i + 1] - closes[i]
    avg_gain = (avg_gain * (period - 1) + max(delta, 0)) / period
    avg_loss = (avg_loss * (period - 1) + max(-delta, 0)) / period
    rs = avg_gain / avg_loss if avg_loss != 0 else float("inf")
    result.append(100 - (100 / (1 + rs)))

return result
```

def _macd(closes: list[float]) -> tuple[list, list]:
ema12 = _ema(closes, 12)
ema26 = _ema(closes, 26)

```
macd_line = [
    (a - b) if a is not None and b is not None else None
    for a, b in zip(ema12, ema26)
]

valid = [v for v in macd_line if v is not None]
signal_raw = _ema(valid, 9)
pad = len(macd_line) - len(valid)
signal_line = [None] * pad + signal_raw

return macd_line, signal_line
```

def _bollinger(closes: list[float], period: int = 20) -> tuple[list, list, list]:
upper, lower, mid = [], [], []

```
for i in range(len(closes)):
    if i < period - 1:
        upper.append(None)
        lower.append(None)
        mid.append(None)
        continue

    window = closes[i - period + 1:i + 1]
    mean = sum(window) / period
    std = statistics.stdev(window)

    mid.append(mean)
    upper.append(mean + 2 * std)
    lower.append(mean - 2 * std)

return upper, mid, lower
```

def _atr(candles: list[dict], period: int = 14) -> list[float | None]:
trs = [None]

```
for i in range(1, len(candles)):
    high = candles[i]["high"]
    low = candles[i]["low"]
    prev_close = candles[i - 1]["close"]

    trs.append(max(high - low, abs(high - prev_close), abs(low - prev_close)))

result = [None] * period
valid_trs = [v for v in trs if v is not None]

atr = sum(valid_trs[:period]) / period
result.append(atr)

for tr in valid_trs[period:]:
    atr = (atr * (period - 1) + tr) / period
    result.append(atr)

return result
```

def extract(candles: list[dict]) -> list[dict]:
closes = [c["close"] for c in candles]
volumes = [c["volume"] for c in candles]

```
rsi = _rsi(closes)
macd, signal = _macd(closes)
bb_upper, bb_mid, bb_lower = _bollinger(closes)
ema20 = _ema(closes, 20)
ema50 = _ema(closes, 50)
atr = _atr(candles)

features = []

for i, candle in enumerate(candles):
    close = candle["close"]

    if (
        rsi[i] is None or macd[i] is None or signal[i] is None or
        ema20[i] is None or ema50[i] is None or
        bb_upper[i] is None or bb_lower[i] is None or
        atr[i] is None
    ):
        continue

    # Momentum
    return_1 = (closes[i] - closes[i - 1]) / closes[i - 1] if i > 0 else 0
    return_3 = (closes[i] - closes[i - 3]) / closes[i - 3] if i > 2 else 0

    # MACD diff
    macd_diff = macd[i] - signal[i]

    # Trend strength
    trend_strength = (ema20[i] - ema50[i]) / close

    # Bollinger width
    bb_width = (bb_upper[i] - bb_lower[i]) / close

    features.append({
        "open_time": candle["open_time"],
        "close": close,

        # normalized core features
        "rsi": rsi[i] / 100,
        "macd": macd[i],
        "macd_signal": signal[i],
        "macd_diff": macd_diff,

        "ema20": ema20[i],
        "ema50": ema50[i],
        "trend_strength": trend_strength,

        "bb_upper": bb_upper[i],
        "bb_mid": bb_mid[i],
        "bb_lower": bb_lower[i],
        "bb_width": bb_width,

        "atr": atr[i],

        # volume normalized
        "volume": volumes[i] / 1_000_000,

        # momentum
        "return_1": return_1,
        "return_3": return_3,
    })

return features
```
