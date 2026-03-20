import requests

USER_KEY = "ucu8uw37ow88ew4s348tsxrhc9c9g6"
API_TOKEN = "and589k3e6zj4a2tihuao9e3bqzadf"


def send_notification(message: str):
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": API_TOKEN,
            "user": USER_KEY,
            "message": message
        }
    )