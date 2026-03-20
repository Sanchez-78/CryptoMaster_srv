import requests

def get_usd_to_czk():
    try:
        url = "https://api.exchangerate.host/latest?base=USD&symbols=CZK"
        res = requests.get(url, timeout=5)
        data = res.json()

        rate = data["rates"]["CZK"]
        return float(rate)

    except Exception as e:
        print("⚠️ FX fallback:", e)
        return 23.0  # fallback