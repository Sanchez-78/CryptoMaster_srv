import requests

BASE_URL = "https://api.binance.com/api/v3/klines"


def get_candles(symbol="BTCUSDT", interval="15m", limit=100):
    try:
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }

        response = requests.get(BASE_URL, params=params)
        data = response.json()

        candles = []

        for c in data:
            candles.append({
                "time": c[0],
                "open": float(c[1]),
                "high": float(c[2]),
                "low": float(c[3]),
                "close": float(c[4]),
                "volume": float(c[5])
            })

        return candles

    except Exception as e:
        print("❌ Market data error:", e)
        return []