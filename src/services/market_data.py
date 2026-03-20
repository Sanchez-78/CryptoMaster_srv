import requests
import time

_cache = None
_last_fetch = 0
CACHE_TTL = 30


def get_all_prices():
    global _cache, _last_fetch

    # cache
    if _cache and time.time() - _last_fetch < CACHE_TTL:
        return _cache

    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "bitcoin,ethereum,cardano",
            "vs_currencies": "usd"
        }

        r = requests.get(url, params=params, timeout=5)

        if r.status_code == 200:
            data = r.json()

            _cache = {
                "BTCUSDT": float(data["bitcoin"]["usd"]),
                "ETHUSDT": float(data["ethereum"]["usd"]),
                "ADAUSDT": float(data["cardano"]["usd"])
            }

            _last_fetch = time.time()
            return _cache

        if r.status_code == 429:
            print("⚠️ Rate limit, backing off...")
            time.sleep(2)

    except Exception as e:
        print("⚠️ Market data error:", e)

    # 🔥 FALLBACK (KRITICKÝ)
    if _cache:
        print("⚠️ Using cached prices")
        return _cache

    # 🔥 LAST RESORT → fake price (aby AI běžela)
    print("⚠️ Using fallback prices")

    return {
        "BTCUSDT": 60000,
        "ETHUSDT": 3000,
        "ADAUSDT": 0.5
    }