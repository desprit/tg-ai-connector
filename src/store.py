import time
import pathlib

from . import model
from . import config

settings = config.get_settings()


class DialogsStore:
    """
    Stores whitelisted users, dialogs and usernames.
    Data is stored in memory.
    """

    __instance = None
    ttl = settings.general.text_history_ttl
    limit = settings.general.text_history_size
    chats: dict[str, list[model.ChatHistoryEntry]]
    completions: dict[str, list[model.CompletionHistoryEntry]]

    def __init__(self):
        if DialogsStore.__instance is not None:
            raise Exception("This class is a singleton!")
        self.chats = {}
        self.completions = {}
        DialogsStore.__instance = self

    @staticmethod
    def get_instance():
        if DialogsStore.__instance is None:
            return DialogsStore()
        return DialogsStore.__instance

    def add_to_chats(self, chat_id: str, value: model.ChatHistoryEntry):
        if chat_id not in self.chats:
            self.chats[chat_id] = []
        self.chats[chat_id].append(value)

    def add_to_completions(self, chat_id: str, value: model.CompletionHistoryEntry):
        if chat_id not in self.completions:
            self.completions[chat_id] = []
        self.completions[chat_id].append(value)

    def get_from_chats(self, chat_id: str) -> list[model.ChatHistoryEntry]:
        return self.chats.get(chat_id, [])

    def get_from_completions(self, chat_id: str) -> list[model.CompletionHistoryEntry]:
        return self.completions.get(chat_id, [])

    def clean_old_completions(self, key: str):
        if key not in self.completions:
            return
        filtered = []
        for item in self.completions[key]:
            if item.timestamp > (time.time() - self.ttl):
                filtered.append(item)
        self.completions[key] = filtered[-self.limit :]

    def clean_old_chats(self, key: str):
        if key not in self.chats:
            return
        filtered = []
        for item in self.chats[key]:
            if item.timestamp > (time.time() - self.ttl):
                filtered.append(item)
        self.chats[key] = filtered[-self.limit :]

    def clear_chats(self, chat_id: str):
        self.chats[chat_id] = []

    def clear_completions(self, chat_id: str):
        self.completions[chat_id] = []


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
