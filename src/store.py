import time
import pathlib

from . import model
from . import config

settings = config.get_settings()


class MessagesStore:
    """
    Stores whitelisted users, chats and usernames.
    Data is stored in memory.
    """

    __instance = None
    ttl = settings.general.text_history_ttl
    limit = settings.general.text_history_size
    items: dict[str, list[model.HistoryEntry]]

    def __init__(self):
        if MessagesStore.__instance is not None:
            raise Exception("This class is a singleton!")
        self.items = {}
        MessagesStore.__instance = self

    @staticmethod
    def get_instance():
        if MessagesStore.__instance is None:
            return MessagesStore()
        return MessagesStore.__instance

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


class WhitelistStore:
    """
    Stores whitelisted users, chats and usernames.
    Uses local file to store the data.
    """

    __instance = None
    entries: set[str]
    filepath = pathlib.Path(__name__).parent / "whitelist.txt"

    def __init__(self):
        if WhitelistStore.__instance is not None:
            raise Exception("This class is a singleton!")
        if not self.filepath.exists():
            self.filepath.touch()
        with open(self.filepath) as f:
            self.entries = set([l.strip() for l in f.readlines()])
        WhitelistStore.__instance = self

    @staticmethod
    def get_instance():
        if WhitelistStore.__instance is None:
            return WhitelistStore()
        return WhitelistStore.__instance

    def whitelist(self, entry: str | int) -> str | None:
        if isinstance(entry, int):
            entry = str(entry)
        entry = entry.lower()
        if entry in self.entries:
            return f"{entry} is already whitelisted"
        self.entries.add(entry)
        with open(self.filepath, "a") as f:
            f.write(f"{entry}\n")
        return None

    def blacklist(self, entry: str | int) -> str | None:
        if isinstance(entry, int):
            entry = str(entry)
        entry = entry.lower()
        if entry not in self.entries:
            return f"{entry} is not whitelisted"
        self.entries.remove(entry)
        with open(self.filepath, "w") as f:
            f.write("\n".join(self.entries))
        return None

    def is_whitelisted(self, entry: str | int) -> bool:
        if isinstance(entry, int):
            entry = str(entry)
        entry = entry.lower()
        return entry in self.entries
