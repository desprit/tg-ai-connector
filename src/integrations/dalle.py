import io
from typing import Tuple
from typing import Optional

import openai
import openai.error
from PIL import Image

from .. import config


settings = config.get_settings()
if settings.integrations.openai:
    openai.api_key = settings.integrations.openai.API_KEY


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
