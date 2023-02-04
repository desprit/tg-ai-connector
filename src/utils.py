import re
from typing import Optional

import telebot

from . import model
from . import config

logger = config.logger
settings = config.get_settings()

COMMAND_RE = re.compile(r"^(\/\w+)\s?")
REMOVE_COMMAND_RE = re.compile(r"^\/\w+\s?")


class IsAllowed(telebot.custom_filters.SimpleCustomFilter):
    key = "is_allowed"

    @staticmethod
    def check(m: telebot.types.Message):
        is_allowed = allowed(m.from_user.id, m.chat.id)
        if not is_allowed:
            logger.warn(
                f">>> Message from user {m.from_user.id}, chat {m.chat.id} was blocked"
            )
        return is_allowed


def allowed(user_id: int, chat_id: int) -> bool:
    if settings.debug:
        logger.debug(f">>> Message received from user {user_id}, chat {chat_id}")
    allowed = (
        user_id in settings.telegram.allowed_users
        or chat_id in settings.telegram.allowed_chats
    )
    if not allowed:
        return False
    return True


def get_command(text: str) -> str:
    """
    Extract command from message, example:
    >>> get_command("/m Hello")
    "m"
    """
    if isinstance(text, str):
        return COMMAND_RE.findall(text)[0].strip().lstrip("/")
    return text


def clean_message_from_command(text: str) -> str:
    """
    Remove command from message, example:
    >>> clean_message_from_command("/m Hello")
    "Hello"
    """
    if isinstance(text, str):
        return REMOVE_COMMAND_RE.sub("", text).strip()
    return text


def find_config_by_command(cmd: str) -> Optional[model.Network]:
    """
    Search ReplicateNetworks and OpenAiNetworks for the one that matches the given command.
    """
    if settings.integrations.replicate:
        for network in settings.integrations.replicate.networks:
            if network.command == cmd:
                return network
    if settings.integrations.openai:
        for network in settings.integrations.openai.networks:
            if network.command == cmd:
                return network
    return None


def get_list_of_commands() -> str:
    """
    Return list of commands supported by the bot.
    """
    commands = [
        ["help", "Show help message"],
        ["ping", "Check if bot is alive"],
    ]
    if settings.integrations.replicate:
        for network in settings.integrations.replicate.networks:
            commands.append(
                [
                    network.command,
                    f"Send request to Replicate API network {network.name}",
                ]
            )
    if settings.integrations.openai:
        for network in settings.integrations.openai.networks:
            commands.append(
                [network.command, f"Send request to OpenAI API network {network.name}"]
            )
    return "".join(f"<code>/{cmd}</code> - {desc}\n" for cmd, desc in commands)
