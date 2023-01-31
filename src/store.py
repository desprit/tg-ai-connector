import time
from typing import Dict
from typing import List
from typing import Optional

from . import model
from . import config

settings = config.get_settings()


class Store:
    ttl: int
    limit: int = 1
    items: Dict[str, List[model.HistoryEntry]]

    def __init__(self):
        self.items = {}

    def add(self, key: str, value: model.HistoryEntry):
        if key not in self.items:
            self.items[key] = []
        self.items[key].append(value)

    def get(self, key: str) -> List[model.HistoryEntry]:
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
    ttl = settings.general.TEXT_HISTORY_TTL
    limit = settings.general.TEXT_HISTORY_SIZE


class ImagesStore(Store):
    ttl = settings.general.IMAGE_HISTORY_TTL

    def get_previous(self, key: str) -> Optional[model.ImageHistoryEntry]:
        if len(self.get(key)) == 0:
            return None
        return self.get(key)[-1]
