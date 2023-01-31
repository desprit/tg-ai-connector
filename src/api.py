from fastapi import FastAPI

from . import utils
from . import model


app = FastAPI()


@app.post("/get_entities", response_model=model.EntitiesResponse)
def get_entities(gpt_request: model.EntitiesRequest):
    response = utils.get_gpt_response([], gpt_request.text)
    return {"text": response}


@app.post("/generate_image")
def generate_image():
    response = utils.get_midjourney_response("a human on a beach")
    print(response)
    print(type(response))
    return {"text": "success"}
