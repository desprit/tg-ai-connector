import os
from typing import Tuple
from typing import Optional

import replicate
import replicate.exceptions

from .. import config

settings = config.get_settings()
if settings.integrations.midjourney:
    os.environ["REPLICATE_API_TOKEN"] = settings.integrations.midjourney.API_KEY
    model = replicate.models.get("tstramer/midjourney-diffusion")
    version = model.versions.get(
        "436b051ebd8f68d23e83d22de5e198e0995357afef113768c20f0b6fcef23c8b"
    )


def get_midjourney_response(text: str) -> Tuple[str, Optional[str]]:
    """
    Generate an image using Midjourney Diffusion model and return a link.
    """
    if not settings.integrations.midjourney:
        return "", "Midjourney integration is not configured"
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
        output = version.predict(**inputs)
    except (replicate.exceptions.ReplicateError, replicate.exceptions.ModelError) as e:
        return "", f"Error while getting image: {e}"
    if isinstance(output, list):
        return output[0] or "", None
    return output or "", None
