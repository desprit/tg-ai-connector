import re
from typing import List
from typing import Tuple
from typing import Optional

import openai
import openai.error

from .. import model
from .. import config

settings = config.get_settings()
REMOVE_ANSWER_RE = re.compile(r"Answer\d+:")


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
