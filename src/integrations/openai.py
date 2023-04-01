import re
import time
from typing import Tuple
from typing import Optional

import openai
import openai.error

from .. import model
from .. import config

settings = config.get_settings()
if settings.integrations.openai:
    openai.api_key = settings.integrations.openai.api_key

CHAT_API_NAME = "chat"
IMAGE_API_NAME = "image"
COMPLETION_API_NAME = "completion"
REMOVE_ANSWER_RE = re.compile(r"Answer\d+:")


def send_completion_request(version: str, prompt: str):
    if not settings.integrations.openai:
        raise Exception("OpenAI integration is not configured")
    response = openai.Completion.create(
        model=version,
        prompt=prompt,
        max_tokens=settings.integrations.openai.max_tokens,
        temperature=0.2,
        timeout=10,
        n=1,
    )
    return response


def get_completion_response(
    history: list[model.CompletionHistoryEntry], text: str, cfg: model.Network
) -> Tuple[str, Optional[str]]:
    """
    Request an answer from one of the Text Completion models.
    """
    if not text:
        return "", "No text provided"
    text = _format_text_completion_request_with_context(history, text)
    response = None
    for _ in range(2):
        try:
            response = send_completion_request(cfg.version, text)
        except openai.error.APIConnectionError:
            time.sleep(1)
            continue
        except Exception as e:
            return "", f"Error while getting response, {e}"
        break
    if not response:
        return "", "Error while getting response"
    if not isinstance(response, dict) or not "choices" in response:
        return "", "Error while getting response, no choices"
    choices = response["choices"]
    if len(response["choices"]) == 0:
        return "", "Error while getting response, no choices"
    choice = choices[0]
    if not isinstance(choice, dict) or not "text" in choice:
        return "", "Error while getting response, no text"
    text = choice["text"]
    # Answer comes in format
    # "AnswerN: Hello...""
    # We need to remove the "AnswerN:" part
    text = REMOVE_ANSWER_RE.sub("", text).strip()
    return text, None


def send_chat_request(version: str, messages: list[dict]):
    if not settings.integrations.openai:
        raise Exception("OpenAI integration is not configured")
    response = openai.ChatCompletion.create(
        model=version,
        messages=messages,
        max_tokens=settings.integrations.openai.max_tokens,
        temperature=0.2,
        timeout=10,
        n=1,
    )
    return response


def get_chat_response(
    history: list[model.ChatHistoryEntry], text: str, cfg: model.Network
) -> Tuple[str, Optional[str]]:
    """
    Request an answer from a Chat model.
    """
    if not text:
        return "", "No text provided"
    messages = _format_chat_request(history, text)
    response = None
    for _ in range(2):
        try:
            response = send_chat_request(cfg.version, messages)
        except openai.error.APIConnectionError:
            time.sleep(1)
            continue
        except Exception as e:
            return "", f"Error while getting response, {e}"
        break
    if not response:
        return "", "Error while getting response"
    if not isinstance(response, dict) or not "choices" in response:
        return "", "Error while getting response, no choices"
    choices = response["choices"]
    if len(choices) == 0:
        return "", "Error while getting response, no choices"
    choice = choices[0]
    if not isinstance(choice, dict) or not "message" in choice:
        return "", "Error while getting response, no message"
    message = choice["message"]
    if not isinstance(message, dict) or not "content" in message:
        return "", "Error while getting response, no content"
    return message["content"], None


def get_dalle_response(text: str) -> Tuple[str, Optional[str]]:
    if not text:
        return "", "No text provided"
    response = None
    for _ in range(2):
        try:
            response = openai.Image.create(prompt=text, n=1, size="1024x1024")
        except openai.error.APIConnectionError:
            time.sleep(1)
            continue
        except Exception as e:
            return "", f"Error while getting image: {e}"
        break
    if not response:
        return "", "Error while getting image: no response"
    if not isinstance(response, dict) or not "data" in response:
        return "", "Error while getting image: no data"
    data = response["data"]
    if not isinstance(data, list) or len(data) == 0:
        return "", "Error while getting image: data is empty"
    value = data[0]
    if not isinstance(value, dict) or not "url" in value:
        return "", "Error while getting image: no url"
    return value["url"], None


def _format_text_completion_request_with_context(
    history: list[model.CompletionHistoryEntry], text: str
) -> str:
    """
    Combine history with new message.
    Example output:
        Prompt1: Hello
        Answer1: Hi
        Prompt2: How are you?
        Answer2: I'm fine
        ...
    """
    if len(history) == 0:
        return text
    result = ""
    for i, entry in enumerate(history, start=1):
        result += f"Prompt{i}: {entry.message}\n"
        result += f"Answer{i}: {entry.response}\n"
    result += f"Prompt{len(history) + 1}: {text}\n"
    return result


def _format_chat_request(history: list[model.ChatHistoryEntry], text: str):
    """
    Format old messages in the following structure:
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Who won the world series in 2020?"},
        {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
        {"role": "user", "content": "Where was it played?"}
    """
    role = "user"
    if text.lower().startswith("you are"):
        role = "system"
    if len(history) == 0:
        return [{"role": role, "content": text}]
    result = []
    for entry in history:
        result.append({"role": entry.message_role, "content": entry.message})
        result.append({"role": "assistant", "content": entry.response})
    result.append({"role": role, "content": text})
    return result
