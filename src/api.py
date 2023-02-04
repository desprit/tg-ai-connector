from fastapi import FastAPI

from . import model
from .integrations.openai import get_gpt_response


app = FastAPI()


@app.post("/get_entities", response_model=model.EntitiesResponse)
def get_entities(gpt_request: model.EntitiesRequest):
    """
    TODO
    """
    response = get_gpt_response([], gpt_request.text)
    return {"text": response}
