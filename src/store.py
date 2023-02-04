import time

from . import model
from . import config

settings = config.get_settings()


class Store:
    ttl: int
    limit: int = 1
    items: dict[str, list[model.HistoryEntry]]

    def __init__(self):
        self.items = {}

    def add(self, key: str, value: model.HistoryEntry):
        if key not in self.items:
            self.items[key] = []
        self.items[key].append(value)

    def get(self, key: str) -> list[model.HistoryEntry]:
        return self.items.get(key, [])

    def clean_old_items(self, key: str):
        filtered = []
        for item in self.get(key):
            if item.timestamp > (time.time() - self.ttl):
                filtered.append(item)
        return filtered[-self.limit :]

    def clear(self, key: str):
        self.items[key] = []


class MessagesStore(Store):
    ttl = settings.general.text_history_ttl
    limit = settings.general.text_history_size
