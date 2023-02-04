import base64

import telebot

from . import model
from . import utils
from . import store
from . import config
from .integrations.openai import get_gpt_response
from .integrations.openai import get_dalle_response
from .integrations.replicate import get_midjourney_response
from .integrations.replicate import get_stable_diffusion_response


logger = config.logger
settings = config.get_settings()
telebot.apihelper.ENABLE_MIDDLEWARE = True
bot = telebot.TeleBot(settings.telegram.BOT_TOKEN, parse_mode=None)
bot.add_custom_filter(utils.IsAllowed())

images_store = store.ImagesStore()
messages_store = store.MessagesStore()


@bot.middleware_handler()
def clean_message(_, update: telebot.types.Update):
    if update.message:
        update.message.cleaned = utils.clean_message_from_command(update.message.text)


@bot.message_handler(commands=["start"], is_allowed=True)
def handle_start(m: telebot.types.Message):
    bot.reply_to(m, "Shaka, bruh! Ask me something.")


@bot.message_handler(commands=["ping"], is_allowed=True)
def handle_ping(m: telebot.types.Message):
    bot.reply_to(m, "Pong, bruh!")


@bot.message_handler(
    commands=[settings.integrations.MIDJOURNEY_COMMAND], is_allowed=True
)
def handle_midjourney_request(m: telebot.types.Message):
    """
    Midjourney image generation requests handler.
    Example:
    >>> /m A sunset on the beach
    """
    response, error = get_midjourney_response(m.cleaned)
    if error:
        return bot.reply_to(m, error)
    bot.send_photo(m.chat.id, response, reply_to_message_id=m.message_id)


@bot.message_handler(
    commands=[settings.integrations.STABLE_DIFFUSION_COMMAND], is_allowed=True
)
def handle_stable_diffusion_request(m: telebot.types.Message):
    """
    Stable Diffusion image generation requests handler.
    Example:
    >>> /s A sunset on the beach
    """
    response, error = get_stable_diffusion_response(m.cleaned)
    if error:
        return bot.reply_to(m, error)
    bot.send_photo(m.chat.id, response, reply_to_message_id=m.message_id)


@bot.message_handler(commands=[settings.integrations.DALLE_COMMAND], is_allowed=True)
def handle_dalle_request(m: telebot.types.Message):
    """
    OpenAI Dall-E image generation requests handler.
    Example:
    >>> /d A sunset on the beach
    To clean the history:
    >>> /d clear
    To adjust the previous image:
    >>> /d adjust Green sky
    """
    unique_id = f"{m.chat.id}:{m.chat.id}"
    images_store.clean_old_items(unique_id)

    if "adjust" in m.cleaned:
        text = m.cleaned.replace("adjust", "").strip()
        previous_image = images_store.get_previous(unique_id)
        if not previous_image:
            return bot.reply_to(m, "No previous image to adjust")
        response, error = get_dalle_response(text, previous_image.image_data)
    else:
        response, error = get_dalle_response(m.cleaned)
    if error:
        return bot.reply_to(m, error)

    image_data = base64.b64decode(response)
    history_entry = model.ImageHistoryEntry(m.cleaned, m.date, image_data)
    images_store.add(unique_id, history_entry)
    bot.send_photo(m.chat.id, image_data, reply_to_message_id=m.message_id)


@bot.message_handler(commands=[settings.integrations.CHATGPT_COMMAND], is_allowed=True)
def handle_chatgpt_request(m: telebot.types.Message):
    """
    OpenAI ChatGPT requests handler.
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


logger.info("Started polling")
bot.infinity_polling()
