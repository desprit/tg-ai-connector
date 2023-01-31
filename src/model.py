from dataclasses import dataclass


@dataclass
class HistoryEntry:
    message: str
    timestamp: int


@dataclass
class ChatHistoryEntry(HistoryEntry):
    response: str


@dataclass
class ImageHistoryEntry(HistoryEntry):
    image_data: bytes  # base64


@dataclass
class EntitiesRequest:
    text: str


@dataclass
class EntitiesResponse:
    text: str


class ConfigException(Exception):
    pass


class IntegrationException(Exception):
    pass
