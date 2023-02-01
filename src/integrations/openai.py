import io
import re
from typing import List
from typing import Tuple
from typing import Optional

import openai
import openai.error
from PIL import Image

from .. import model
from .. import config

settings = config.get_settings()
REMOVE_ANSWER_RE = re.compile(r"Answer\d+:")
if settings.integrations.openai:
    openai.api_key = settings.integrations.openai.API_KEY


def get_gpt_response(
    history: List[model.ChatHistoryEntry], text: str
) -> Tuple[str, Optional[str]]:
    """
    Request an answer from Chat GPT-3 model.
    """
    text = format_with_context(history, text)
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=text,
            max_tokens=500,
            temperature=0.9,
            timeout=10,
            n=1,
        )
    except openai.error.OpenAIError as e:
        return "", f"Error while getting response, {e}"
    if len(response["choices"]) == 0:
        return "", "Error while getting response, no choices"
    text = response["choices"][0]["text"]
    # Answer comes in format
    # "AnswerN: Hello...""
    # We need to remove the "AnswerN:" part
    text = REMOVE_ANSWER_RE.sub("", text).strip()
    return text, None


def format_with_context(history: List[model.ChatHistoryEntry], text: str) -> str:
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



def get_dalle_response(
    text: str, image: Optional[io.BytesIO] = None
) -> Tuple[str, Optional[str]]:
    if not settings.integrations.openai:
        return "", "OpenAI integration is not configured"
    try:
        if image:
            response = edit_image(text, image)
        else:
            response = create_image(text)
    except openai.error.OpenAIError as e:
        return "", f"Error while getting image: {e}"
    if not response or not "data" in response:
        return "", "Error while getting image: no data"
    if len(response["data"]) == 0:
        return "", "Error while getting image: no data"
    return response["data"][0]["b64_json"], None


def create_image(text: str) -> dict:
    """
    Generate an image and return a link.
    """
    return openai.Image.create(
        prompt=text,
        n=1,
        size="1024x1024",
        response_format="b64_json",
    )


def edit_image(text: str, image_data: bytes) -> dict:
    """
    Edit existing image and return a link.
    """
    arr = io.BytesIO()
    img = Image.open(io.BytesIO(image_data))
    img = img.convert("RGBA")
    img.save(arr, format="PNG")
    return openai.Image.create_edit(
        image=arr.getvalue(),
        prompt=text,
        n=1,
        size="1024x1024",
        response_format="b64_json",
    )