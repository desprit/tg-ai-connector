import logging
from pathlib import Path
from functools import lru_cache

import toml
from pydantic import BaseModel

from . import model


class Config(BaseModel):
    debug: bool = False
    install_global_handlers: bool = False
    general: model.GeneralSettings
    telegram: model.TelegramSettings
    integrations: model.Integrations

    def validate(self):
        commands = []
        if self.integrations.openai:
            commands.extend([n.command for n in self.integrations.openai.networks])
        if self.integrations.replicate:
            commands.extend([n.command for n in self.integrations.replicate.networks])
        if len(commands) != len(set(commands)):
            raise model.ConfigException(
                f"Commands should only repeat once, but found: {commands}"
            )
        if self.telegram.bot_token == "TG_BOT_TOKEN":
            raise model.ConfigException("Please set your bot token in config.toml")


@lru_cache()
def get_settings() -> Config:
    try:
        p = Path.cwd() / "config.toml"
        settings = toml.load(p)
    except FileNotFoundError:
        raise model.ConfigException("Config file not found")
    try:
        config = Config.parse_obj(settings)
        config.validate()
    except Exception as e:
        raise model.ConfigException(f"Config file is not valid: {e}")
    return config


logging.basicConfig(
    filename="log.txt",
    filemode="a",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.DEBUG,
)
if not get_settings().debug:
    logging.getLogger("tg-ai-connector").setLevel(logging.INFO)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("telebot").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)

logger = logging.getLogger("tg-ai-connector")
