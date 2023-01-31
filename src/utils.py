import re

import telebot

from . import config

logger = config.logger
settings = config.get_settings()

REMOVE_COMMAND_RE = re.compile(r"^\/\w+\s")


class IsAllowed(telebot.custom_filters.SimpleCustomFilter):
    key = "is_allowed"

    @staticmethod
    def check(m: telebot.types.Message):
        is_allowed = allowed(m.from_user.id, m.chat.id)
        if not is_allowed:
            logger.warn(
                f"Message from user {m.from_user.id}, chat {m.chat.id} was blocked"
            )
        return is_allowed


def allowed(user_id: int, chat_id: int) -> bool:
    if settings.DEBUG:
        logger.debug(f"Message received from user {user_id}, chat {chat_id}")
    allowed = (
        user_id in settings.telegram.ALLOWED_USERS
        or chat_id in settings.telegram.ALLOWED_CHATS
    )
    if not allowed:
        return False
    return True


def clean_message_from_command(text: str) -> str:
    """
    Remove command from message, example:
    >>> clean_message_from_command("/petuh Hello")
    "Hello"
    """
    return REMOVE_COMMAND_RE.sub("", text).strip()
