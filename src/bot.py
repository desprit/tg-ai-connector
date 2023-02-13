import telebot

from . import model
from . import utils
from . import store
from . import config
from .integrations.openai import get_gpt_response
from .integrations.openai import get_dalle_response
from .integrations.openai import DALLE_NAME, CHATGPT_NAME
from .integrations.replicate import get_replicate_response


logger = config.logger
settings = config.get_settings()
messages_store = store.MessagesStore.get_instance()
whitelist_store = store.WhitelistStore.get_instance()

telebot.apihelper.ENABLE_MIDDLEWARE = True
bot = telebot.TeleBot(settings.telegram.bot_token)
bot.add_custom_filter(utils.IsAdmin())
bot.add_custom_filter(utils.IsAllowed())


@bot.middleware_handler()
def clean_message(_, update: telebot.types.Update):
    """
    Clean message from command.
    """
    if update.message:
        update.message.command = utils.get_command(update.message.text)
        update.message.cleaned = utils.clean_message_from_command(update.message.text)


@bot.message_handler(commands=["start"], is_allowed=True)
def handle_start(m: telebot.types.Message):
    bot.reply_to(m, "Shaka, bruh! Ask me something. /help for more info")


@bot.message_handler(commands=["ping"], is_allowed=True)
def handle_ping(m: telebot.types.Message):
    bot.reply_to(m, "Pong, bruh!")


@bot.message_handler(commands=["help"], is_allowed=True)
def handle_help(m: telebot.types.Message):
    message = utils.get_list_of_commands(m.from_user.id)
    bot.reply_to(m, message, parse_mode="HTML")


@bot.message_handler(commands=["whitelist"], is_admin=True)
def handle_whitelist(m: telebot.types.Message):
    """
    Add user or chat to whitelist. Requires admin privileges.
    """
    if not m.cleaned:
        return bot.reply_to(m, "Please specify user id, username or chat id ")
    entry = m.cleaned.split(" ")[0]
    error = whitelist_store.whitelist(entry)
    if error:
        return bot.reply_to(m, error)
    bot.reply_to(m, f"Added {entry} to whitelist")


@bot.message_handler(commands=["blacklist"], is_admin=True)
def handle_blacklist(m: telebot.types.Message):
    """
    Block user or chat. Requires admin privileges.
    """
    if not m.cleaned:
        return bot.reply_to(m, "Please specify user id, username or chat id ")
    entry = m.cleaned.split(" ")[0]
    error = whitelist_store.blacklist(entry)
    if error:
        return bot.reply_to(m, error)
    bot.reply_to(m, f"Removed {entry} from whitelist")


def handle_replicate_request(m: telebot.types.Message):
    """
    Image generation using Replicate API.
    Example:
    >>> /m A sunset on the beach
    """
    cfg = utils.find_config_by_command(m.command)
    response, error = get_replicate_response(m.cleaned, cfg)
    if error:
        return bot.reply_to(m, error)
    bot.send_photo(m.chat.id, response, reply_to_message_id=m.message_id)


def handle_dalle_request(m: telebot.types.Message):
    """
    Image generation using OpenAI Dall-E API.
    Example:
    >>> /d A sunset on the beach
    """
    response, error = get_dalle_response(m.cleaned)
    if error:
        return bot.reply_to(m, error)
    bot.send_photo(m.chat.id, response, reply_to_message_id=m.message_id)


def handle_chatgpt_request(m: telebot.types.Message):
    """
    Conversation handler using OpenAI ChatGPT.
    Example:
    >>> /p What is the meaning of life?
    To clean the history:
    >>> /p clear
    """
    unique_id = f"{m.chat.id}:{m.chat.id}"
    messages_store.clean_old_items(unique_id)
    if "clear" in m.cleaned:
        messages_store.clear(unique_id)
        return bot.reply_to(m, "History cleared")

    history = messages_store.get(unique_id)
    response, error = get_gpt_response(history, m.cleaned)
    if error:
        return bot.reply_to(m, error)
    history_entry = model.ChatHistoryEntry(m.cleaned, m.date, response)
    messages_store.add(unique_id, history_entry)
    bot.reply_to(m, response)


if settings.integrations.replicate:
    networks = settings.integrations.replicate.networks
    for n in networks:
        bot.register_message_handler(
            handle_replicate_request, commands=[n.command], is_allowed=True
        )


if settings.integrations.openai:
    networks = settings.integrations.openai.networks
    dalle_cmd = next((n.command for n in networks if n.name == DALLE_NAME), None)
    if dalle_cmd:
        bot.register_message_handler(
            handle_dalle_request, commands=[dalle_cmd], is_allowed=True
        )
    chatgpt_cmd = next((n.command for n in networks if n.name == CHATGPT_NAME), None)
    if chatgpt_cmd:
        bot.register_message_handler(
            handle_chatgpt_request, commands=[chatgpt_cmd], is_allowed=True
        )


logger.info(">>> Started polling")
bot.infinity_polling()
