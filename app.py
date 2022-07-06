import configparser
import json
import sys
import time
import logging

import uvicorn
from fastapi import (
    FastAPI,
    Request,
    HTTPException,
)
from fastapi.encoders import (
    jsonable_encoder,
)
from pydantic import BaseModel
from model.agent import GPT2Agent


config = configparser.ConfigParser()
config.read('env.ini')

logger = logging.getLogger('uvicorn')
logger.setLevel(logging.DEBUG)

app = FastAPI()


from model.agent import BaseAgent
from typing import Optional
class DialogManager():
    def __init__(self, agent: BaseAgent, max_utter_length: Optional[int] = 1):
        """
        max_utter_length (int): max number of utterance.
            1 is only use user input.
            2 is that use user input and system output.
            default 1.
        dialog (list[tuple[sys|usr, str]]): ["x1", "y1", ..., "xn", "yn"]
        """
        self.id: int = 0
        self.dialog: list[str] = []
        self.agent: BaseAgent = agent
        self.max_utter_length: Optional[int] = max_utter_length

    def __call__(self, input_: str) -> str:
        self.dialog.append(input_)
        if self.max_utter_length is not None:
            inputs = self.dialog[-self.max_utter_length:]
        else:
            inputs = self.dialog
        reply = self.agent.reply(inputs)
        self.dialog.append(reply)
        return reply


s = time.time()
agent = GPT2Agent(
    model_name="rinna/japanese-gpt2-medium",
    model_checkpoint="data/gpt-2/GPT2-pretrain-step-28000.pkl",
)
# from model.agent import EchoAgent
# agent = EchoAgent()
logger.debug(f"Load GPT2Agent: {time.time() - s:.2f} s")

manager = DialogManager(
    agent,
    max_utter_length=1,
)


class Mattermost(BaseModel):
    text: str
    response_type: str

@app.post("/mattermost", response_model=Mattermost)
async def mattermost(request: Request):
    req = json.loads(
        (await request.body()).decode("utf-8")
    )
    if req['token'] != config['Mattermost']['Token']:
        raise HTTPException(status_code=400, detail="Bad Request")

    text = req['text']
    if text.startswith(req['trigger_word']):
        text = text[len(req['trigger_word'])+1:]

    logger.info(f"{text=}")
    response = manager(text)
    return {
        "text": response,
        "response_type": "in_channel",
    }


if __name__ == "__main__":
    pass
