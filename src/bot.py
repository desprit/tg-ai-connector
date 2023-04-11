import telebot
import requests

from . import model
from . import utils
from . import store
from . import config
from .integrations.openai import get_chat_response
from .integrations.openai import get_dalle_response
from .integrations.openai import get_completion_response
from .integrations.openai import CHAT_API_NAME, IMAGE_API_NAME, COMPLETION_API_NAME
from .integrations.replicate import get_replicate_audio_response
from .integrations.replicate import get_replicate_image_response


logger = config.logger
settings = config.get_settings()
dialogs_store = store.DialogsStore.get_instance()
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


def get_audio_file(file_id: str) -> requests.Response:
    """
    Download audio file from the message.
    """
    file_info = bot.get_file(file_id)
    file = requests.get(
        "https://api.telegram.org/file/bot{0}/{1}".format(
            settings.telegram.bot_token, file_info.file_path
        )
    )
    return file


def handle_replicate_request(m: telebot.types.Message):
    """
    Image generation and voice-to-text decode using Replicate API.
    Example:
    >>> /m A sunset on the beach
    """
    cfg = utils.find_config_by_command(m.command)
    if not cfg:
        return bot.reply_to(m, "Unknown command")
    if cfg.type == "audio":
        if m.reply_to_message and m.reply_to_message.voice:
            file = get_audio_file(m.reply_to_message.voice.file_id)
            response, error = get_replicate_audio_response(file.content, m.cleaned, cfg)
            if error:
                return bot.reply_to(m, error)
            bot.reply_to(m, response)
            return
        bot.reply_to(m, "No voice attachment found")
        return
    if cfg.type == "image":
        response, error = get_replicate_image_response(m.cleaned, cfg)
        if error:
            return bot.reply_to(m, error)
        bot.send_photo(m.chat.id, response, reply_to_message_id=m.message_id)
        return
    bot.reply_to(m, "Unknown command type")


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


def handle_completion_request(m: telebot.types.Message):
    """
    Conversation handler using OpenAI text completion models.
    Example:
    >>> /d What is the meaning of life?
    To clean the history:
    >>> /d clear
    """
    unique_id = f"{m.chat.id}:{m.from_user.id}"
    dialogs_store.clean_old_completions(unique_id)
    if m.cleaned.startswith("clear"):
        dialogs_store.clear_completions(unique_id)
        return bot.reply_to(m, "History cleared")

    cfg = utils.find_config_by_command(m.command)
    if not cfg:
        return bot.reply_to(m, "Unknown command")
    history = dialogs_store.get_from_completions(unique_id)
    response, error = get_completion_response(history, m.cleaned, cfg)
    if error:
        return bot.reply_to(m, error)
    history_entry = model.CompletionHistoryEntry.from_message(
        m.cleaned, m.date, response
    )
    dialogs_store.add_to_completions(unique_id, history_entry)
    bot.reply_to(m, response)


def handle_chat_request(m: telebot.types.Message):
    """
    Chat handler using OpenAI chat models.
    Example:
    >>> /c You are a helpful Twitch moderator
    To clean the history:
    >>> /c clear
    """
    unique_id = f"{m.chat.id}:{m.from_user.id}"
    dialogs_store.clean_old_chats(unique_id)
    if m.cleaned.startswith("clear"):
        dialogs_store.clear_chats(unique_id)
        return bot.reply_to(m, "History cleared")

    cfg = utils.find_config_by_command(m.command)
    if not cfg:
        return bot.reply_to(m, "Unknown command")
    history = dialogs_store.get_from_chats(unique_id)
    response, error = get_chat_response(history, m.cleaned, cfg)
    if error:
        return bot.reply_to(m, error)
    history_entry = model.ChatHistoryEntry.from_message(m.cleaned, m.date, response)
    dialogs_store.add_to_chats(unique_id, history_entry)
    bot.reply_to(m, response)


def handle_voice_message(m: telebot.types.Message):
    """
    Handler to automatically convert voice messages to text.
    Should not get triggered if message starts with a command.
    """
    if m.text and m.text.startswith("/"):
        return
    cfg = utils.find_config_by_type("audio")
    if not cfg:
        return bot.reply_to(m, "Network to process audio not found")
    msg = bot.reply_to(m, "Generating text...")
    file = get_audio_file(m.voice.file_id)
    response, error = get_replicate_audio_response(file.content, "", cfg)
    if error:
        bot.edit_message_text(
            "Couldn't generate text", chat_id=m.chat.id, message_id=msg.id
        )
        return bot.reply_to(m, error)
    bot.edit_message_text(response, chat_id=m.chat.id, message_id=msg.id)


"""
Initialize handlers for integrations listed in configuration file.
"""

if settings.integrations.replicate:
    networks = settings.integrations.replicate.networks
    for n in networks:
        bot.register_message_handler(
            handle_replicate_request, commands=[n.command], is_allowed=True
        )


if settings.integrations.openai:
    networks = settings.integrations.openai.networks
    image_cmd = next((n.command for n in networks if n.name == IMAGE_API_NAME), None)
    if image_cmd:
        bot.register_message_handler(
            handle_dalle_request, commands=[image_cmd], is_allowed=True
        )
    chat_cmd = next((n.command for n in networks if n.name == CHAT_API_NAME), None)
    if chat_cmd:
        bot.register_message_handler(
            handle_chat_request, commands=[chat_cmd], is_allowed=True
        )
    completion_cmd = next(
        (n.command for n in networks if n.name == COMPLETION_API_NAME), None
    )
    if completion_cmd:
        bot.register_message_handler(
            handle_completion_request, commands=[completion_cmd], is_allowed=True
        )


"""
Register global handlers.
"""

if settings.install_global_handlers:
    bot.register_message_handler(handle_voice_message, content_types=["voice"])


logger.info(">>> Started polling")
bot.infinity_polling()
