import re
from typing import Optional

import telebot

from . import model
from . import store
from . import config

logger = config.logger
settings = config.get_settings()

COMMAND_RE = re.compile(r"^(\/\w+)\s?")
REMOVE_COMMAND_RE = re.compile(r"^\/\w+\s?")


class IsAllowed(telebot.custom_filters.SimpleCustomFilter):
    key = "is_allowed"

    @staticmethod
    def check(m: telebot.types.Message):
        chat_id = m.chat.id
        user_id = m.from_user.id
        username = m.from_user.username  # can be None
        if settings.debug:
            logger.debug(f">>> Message received from user {user_id}, chat {chat_id}")
        is_allowed_config = allowed_config(m.from_user.id, m.chat.id)
        is_allowed_whitelist = allowed_whitelist(m.from_user.id, m.chat.id, username)
        if not is_allowed_config and not is_allowed_whitelist:
            logger.warn(
                f">>> Message from user {m.from_user.id}, chat {m.chat.id} was blocked"
            )
        return is_allowed_config or is_allowed_whitelist


class IsAdmin(telebot.custom_filters.SimpleCustomFilter):
    key = "is_admin"

    @staticmethod
    def check(m: telebot.types.Message):
        is_admin = m.from_user.id == settings.telegram.admin_id
        if not is_admin:
            logger.warn(
                f">>> Non-admin user {m.from_user.id} tried to use whitelist command, blocked"
            )
        return is_admin


def allowed_config(user_id: int, chat_id: int) -> bool:
    allowed = (
        user_id in settings.telegram.allowed_users
        or chat_id in settings.telegram.allowed_chats
        or user_id == settings.telegram.admin_id
    )
    if allowed:
        return True
    return False


def allowed_whitelist(user_id: int, chat_id: int, username: Optional[str]) -> bool:
    whitelist_store = store.WhitelistStore.get_instance()
    if whitelist_store.is_whitelisted(user_id):
        return True
    if whitelist_store.is_whitelisted(chat_id):
        return True
    if username and whitelist_store.is_whitelisted(username.lower()):
        return True
    return False


def get_command(text: str) -> str:
    """
    Extract command from message, example:
    >>> get_command("/m Hello")
    "m"
    """
    if isinstance(text, str):
        commands = COMMAND_RE.findall(text)
        return commands[0].strip().lstrip("/") if commands else ""
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


def find_config_by_type(cmd_type: str) -> Optional[model.Network]:
    """
    Search ReplicateNetworks and OpenAiNetworks for the one that matches the given type.
    """
    if settings.integrations.replicate:
        for network in settings.integrations.replicate.networks:
            if network.type == cmd_type:
                return network
    return None


def get_list_of_commands(user_id: int) -> str:
    """
    Return list of commands supported by the bot.
    """
    commands = [
        ["help", "Show help message"],
        ["ping", "Check if bot is alive"],
    ]
    admin_commands = [
        ["whitelist [user_id|username|chat_id]", "Add user or chat to whitelist"],
        ["blacklist [user_id|username|chat_id]", "Remove user or chat from whitelist"],
    ]
    if user_id == settings.telegram.admin_id:
        commands.extend(admin_commands)
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
