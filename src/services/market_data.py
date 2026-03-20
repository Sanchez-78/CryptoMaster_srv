import requests

BASE_URL = "https://api.coingecko.com/api/v3/coins/markets"


def get_price(symbol="BTCUSDT"):
    try:
        mapping = {
            "BTCUSDT": "bitcoin",
            "ETHUSDT": "ethereum",
            "ADAUSDT": "cardano"
        }

        coin_id = mapping.get(symbol)
        if not coin_id:
            return None

        params = {
            "vs_currency": "usd",
            "ids": coin_id
        }

        r = requests.get(BASE_URL, params=params, timeout=10)
        data = r.json()

        if not data:
            return None

        return float(data[0]["current_price"])

    except Exception as e:
        print("❌ Price error:", e)
        return None