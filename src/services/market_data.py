import requests


def get_all_prices():
    # -------------------------------
    # 1️⃣ COINGECKO
    # -------------------------------
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "bitcoin,ethereum,cardano",
            "vs_currencies": "usd"
        }

        r = requests.get(url, params=params, timeout=10)

        if r.status_code == 200:
            data = r.json()

            return {
                "BTCUSDT": float(data["bitcoin"]["usd"]),
                "ETHUSDT": float(data["ethereum"]["usd"]),
                "ADAUSDT": float(data["cardano"]["usd"])
            }

        print("⚠️ CoinGecko failed:", r.status_code)

    except Exception as e:
        print("⚠️ CoinGecko error:", e)

    # -------------------------------
    # 2️⃣ COINPAPRIKA (FALLBACK)
    # -------------------------------
    try:
        mapping = {
            "BTCUSDT": "btc-bitcoin",
            "ETHUSDT": "eth-ethereum",
            "ADAUSDT": "ada-cardano"
        }

        prices = {}

        for sym, coin_id in mapping.items():
            url = f"https://api.coinpaprika.com/v1/tickers/{coin_id}"
            r = requests.get(url, timeout=10)

            if r.status_code == 200:
                data = r.json()
                prices[sym] = float(data["quotes"]["USD"]["price"])

        if prices:
            return prices

    except Exception as e:
        print("⚠️ CoinPaprika error:", e)

    # -------------------------------
    # FAIL
    # -------------------------------
    print("❌ All price sources failed")
    return {}