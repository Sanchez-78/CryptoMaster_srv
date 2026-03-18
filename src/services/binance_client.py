import requests
from config import CANDLE_LIMIT

BASE_URL = "https://api.binance.com/api/v3/klines"

FIELDS = ["open_time", "open", "high", "low", "close", "volume",
          "close_time", "quote_volume", "trades",
          "taker_buy_base", "taker_buy_quote", "ignore"]


def fetch_candles(symbol: str, interval: str) -> list[dict]:
    params = {"symbol": symbol, "interval": interval, "limit": CANDLE_LIMIT}
    response = requests.get(BASE_URL, params=params, timeout=10)
    response.raise_for_status()
    raw = response.json()
    candles = []
    for row in raw:
        candle = dict(zip(FIELDS, row))
        candles.append({
            "open_time": int(candle["open_time"]),
            "open":      float(candle["open"]),
            "high":      float(candle["high"]),
            "low":       float(candle["low"]),
            "close":     float(candle["close"]),
            "volume":    float(candle["volume"]),
        })
    return candles

import time

def fetch_candles(symbol: str, interval: str) -> list[dict]:
    for attempt in range(3):
        try:
            response = requests.get(BASE_URL, params={
                "symbol": symbol,
                "interval": interval,
                "limit": CANDLE_LIMIT
            }, timeout=10)
            response.raise_for_status()
            raw = response.json()
            break
        except Exception:
            if attempt == 2:
                raise
            time.sleep(1)

"symbol": symbol,