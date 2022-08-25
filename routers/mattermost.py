import configparser
import json
import logging
from fastapi import (
    APIRouter,
    Request,
    HTTPException,
)
from fastapi.encoders import (
    jsonable_encoder,
)

from model.agent import GPT2Agent
from controller import UserManager


router = APIRouter()

logger = logging.getLogger('uvicorn')
logger.setLevel(logging.DEBUG)

config = configparser.ConfigParser()
config.read('env.ini')


agent = GPT2Agent(
    model_name=config['GPT2Agent']['ModelName'],
    model_checkpoint=config['GPT2Agent']['ModelCheckpoint'],
)
manager = UserManager(
    agent,
    max_utter_length=20,
)


@router.post("/mattermost")
async def mattermost(request: Request):
    req = json.loads(
        (await request.body()).decode("utf-8")
    )
    if req['token'] != config['Mattermost']['Token']:
        logger.error("status 400")
        raise HTTPException(status_code=400, detail="Bad Request")

    text = req['text']
    if text.startswith(req['trigger_word']):
        text = text[len(req['trigger_word'])+1:]
    user_id = req['user_id']

    logger.debug("request = %s", text)
    response = manager(user_id, text)
    return {
        "text": response,
        "response_type": "in_channel",
    }
