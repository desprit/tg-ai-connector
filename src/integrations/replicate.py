import io
import os
import time
from typing import Tuple
from typing import Optional

from replicate.exceptions import ReplicateError
from replicate import models as replicate_models

from .. import model
from .. import config

logger = config.logger
settings = config.get_settings()
if settings.integrations.replicate:
    os.environ["REPLICATE_API_TOKEN"] = settings.integrations.replicate.api_key


def get_replicate_image_response(
    text: str, cfg: model.Network
) -> Tuple[str, Optional[str]]:
    if not text:
        return "", "No text provided"
    try:
        model = replicate_models.get(cfg.name)
        version = model.versions.get(cfg.version)
    except Exception as e:
        return "", f"Error while initializing Replicate model: {e}"
    inputs = {
        "prompt": text,
        "width": 768,
        "height": 768,
        "prompt_strength": 0.8,
        "num_outputs": 1,
        "num_inference_steps": 50,
        "guidance_scale": 7.5,
        "scheduler": "DPMSolverMultistep",
    }
    output = None
    for _ in range(2):
        try:
            if settings.debug:
                logger.debug(f">>> Replicate image request for: {text}")
            output = version.predict(**inputs)
            logger.debug(f">>> Replicate image response: {output}")
        except ReplicateError as e:
            time.sleep(1)
        except Exception as e:
            return "", f"Error while getting image: {e}"
        break
    if not output:
        return "", "Error while getting image response"
    if isinstance(output, list):
        return output[0] or "", None
    return output or "", None


def get_replicate_audio_response(
    file_data: bytes, text: str, cfg: model.Network
) -> Tuple[str, Optional[str]]:
    try:
        model = replicate_models.get(cfg.name)
        version = model.versions.get(cfg.version)
    except Exception as e:
        return "", f"Error while initializing Replicate model: {e}"
    f = io.BytesIO(file_data)
    inputs = {"audio": f, "transcription": "plain text"}
    if len(text) == "2":
        inputs["language"] = text
    output = None
    for _ in range(2):
        try:
            if settings.debug:
                logger.debug(f">>> Replicate audio request")
            output = version.predict(**inputs)
            logger.debug(f">>> Replicate audio response: {output}")
        except ReplicateError as e:
            time.sleep(1)
        except Exception as e:
            return "", f"Error while getting audio: {e}"
        break
    if not output:
        return "", "Error while getting audio response"
    if not isinstance(output, dict) or "segments" not in output:
        return "", "Error while getting audio response"
    return output["segments"][0]["text"] or "", None
