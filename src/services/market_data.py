import requests

BASE_URL = "https://api.coingecko.com/api/v3/simple/price"


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
            "ids": coin_id,
            "vs_currencies": "usd"
        }

        r = requests.get(BASE_URL, params=params, timeout=10)

        if r.status_code != 200:
            print("❌ HTTP error:", r.status_code)
            return None

        data = r.json()

        if coin_id not in data:
            print("❌ Invalid data:", data)
            return None

        price = data[coin_id]["usd"]

        if not price or price == 0:
            return None

        return float(price)

    except Exception as e:
        print("❌ Price error:", e)
        return None