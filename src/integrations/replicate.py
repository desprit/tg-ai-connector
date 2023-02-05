import os
from typing import Tuple
from typing import Optional

import replicate
import replicate.version
import replicate.exceptions

from .. import model
from .. import config

logger = config.logger
settings = config.get_settings()
if settings.integrations.replicate:
    os.environ["REPLICATE_API_TOKEN"] = settings.integrations.replicate.api_key


def get_replicate_response(
    text: str, cfg: model.ReplicateNetwork
) -> Tuple[str, Optional[str]]:
    if not text:
        return "", "No text provided"
    try:
        model = replicate.models.get(cfg.name)
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
    try:
        if settings.debug:
            logger.debug(f">>> Replicate request: {text}")
        output = version.predict(**inputs)
        logger.debug(f">>> Replicate response: {output}")
    except Exception as e:
        return "", f"Error while getting image: {e}"
    if isinstance(output, list):
        return output[0] or "", None
    return output or "", None
