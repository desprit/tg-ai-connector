from typing import Optional
from dataclasses import dataclass

from pydantic import BaseModel


@dataclass
class HistoryEntry:
    message: str
    timestamp: int


@dataclass
class ChatHistoryEntry(HistoryEntry):
    response: str


@dataclass
class EntitiesRequest:
    text: str


@dataclass
class EntitiesResponse:
    text: str


class Network(BaseModel):
    name: str
    command: str


class OpenAiNetwork(Network):
    ...


class OpenAIIntegration(BaseModel):
    api_key: str
    networks: list[OpenAiNetwork]


class ReplicateNetwork(Network):
    version: str


class ReplicateIntegration(BaseModel):
    api_key: str
    networks: list[ReplicateNetwork]


class Integrations(BaseModel):
    openai: Optional[OpenAIIntegration]
    replicate: Optional[ReplicateIntegration]


class TelegramSettings(BaseModel):
    bot_token: str
    admin_id: Optional[int]
    allowed_users: list[int] = []
    allowed_chats: list[int] = []


class GeneralSettings(BaseModel):
    text_history_size: int = 10
    text_history_ttl: int = 300


class ConfigException(Exception):
    pass


class IntegrationException(Exception):
    pass
