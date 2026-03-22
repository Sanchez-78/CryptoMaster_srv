import time

class DataCache:
    def __init__(self):
        self.cache = {}
        self.ttl = 60  # sekund

    def get(self, key, loader):
        now = time.time()

        if key in self.cache:
            data, ts = self.cache[key]
            if now - ts < self.ttl:
                return data

        data = loader()
        self.cache[key] = (data, now)
        return data