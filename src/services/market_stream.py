import websocket
import json
import threading

class MarketStream:
    def __init__(self, symbols):
        self.symbols = symbols
        self.prices = {}
        self.ws = None

    def _on_message(self, ws, message):
        data = json.loads(message)

        if "s" in data and "c" in data:
            symbol = data["s"]
            price = float(data["c"])
            self.prices[symbol] = price

    def _on_error(self, ws, error):
        print("WS ERROR:", error)

    def _on_close(self, ws, close_status_code, close_msg):
        print("WS CLOSED")

    def _on_open(self, ws):
        print("🔥 WS CONNECTED")

    def start(self):
        streams = "/".join([f"{s.lower()}@ticker" for s in self.symbols])
        url = f"wss://stream.binance.com:9443/stream?streams={streams}"

        self.ws = websocket.WebSocketApp(
            url,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_open=self._on_open,
        )

        thread = threading.Thread(target=self.ws.run_forever)
        thread.daemon = True
        thread.start()

    def get_prices(self):
        return self.prices