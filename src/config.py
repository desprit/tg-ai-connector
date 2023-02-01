import logging
from pathlib import Path
from typing import Optional
from functools import lru_cache

import toml
from pydantic import BaseModel

from . import model


class OpenAIIntegration(BaseModel):
    API_KEY: str
    DALLE_COMMAND: Optional[str]
    CHATGPT_COMMAND: Optional[str]


class ReplicateIntegration(BaseModel):
    API_KEY: str
    MIDJOURNEY_COMMAND: Optional[str]
    STABLE_DIFFUSION_COMMAND: Optional[str]


class Integrations(BaseModel):
    openai: Optional[OpenAIIntegration]
    replicate: Optional[ReplicateIntegration]

    @property
    def MIDJOURNEY_COMMAND(self) -> str:
        if self.replicate and self.replicate.MIDJOURNEY_COMMAND:
            return self.replicate.MIDJOURNEY_COMMAND
        return "m"

    @property
    def STABLE_DIFFUSION_COMMAND(self) -> str:
        if self.replicate and self.replicate.MIDJOURNEY_COMMAND:
            return self.replicate.MIDJOURNEY_COMMAND
        return "s"

    @property
    def DALLE_COMMAND(self) -> str:
        if self.openai and self.openai.DALLE_COMMAND:
            return self.openai.DALLE_COMMAND
        return "d"

    @property
    def CHATGPT_COMMAND(self) -> str:
        if self.openai and self.openai.CHATGPT_COMMAND:
            return self.openai.CHATGPT_COMMAND
        return "p"


class TelegramSettings(BaseModel):
    BOT_TOKEN: str
    ALLOWED_USERS: list[int] = []
    ALLOWED_CHATS: list[int] = []


class GeneralSettings(BaseModel):
    TEXT_HISTORY_SIZE: int = 10
    TEXT_HISTORY_TTL: int = 300
    IMAGE_HISTORY_TTL: int = 300


class Config(BaseModel):
    DEBUG: bool = False
    general: GeneralSettings
    telegram: TelegramSettings
    integrations: Integrations


@lru_cache()
def get_settings() -> Config:
    try:
        p = Path.cwd() / "config.toml"
        settings = toml.load(p)
    except FileNotFoundError:
        raise model.ConfigException("Config file not found")
    try:
        config = Config.parse_obj(settings)
    except Exception as e:
        raise model.ConfigException(f"Config file is not valid: {e}")
    if not config.telegram.BOT_TOKEN:
        raise model.ConfigException("Telegram bot token is required")
    return config


logging.basicConfig(
    filename="log.txt",
    filemode="a",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.DEBUG,
)
if not get_settings().DEBUG:
    logging.getLogger("tg-ai-connector").setLevel(logging.INFO)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("telebot").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)

logger = logging.getLogger("tg-ai-connector")
