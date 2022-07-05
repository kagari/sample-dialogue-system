from cgitb import handler
import json
import sys
import time
import logging

import uvicorn
from fastapi import (
    FastAPI,
    Request,
)
from fastapi.encoders import (
    jsonable_encoder,
)
from model.agent import GPT2Agent


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
    model_checkpoint="data/gpt-2/GPT2-pretrain-step-80000.pkl",
)
# from model.agent import EchoAgent
# agent = EchoAgent()
logger.debug(f"Load GPT2Agent: {time.time() - s:.2f} s")

manager = DialogManager(
    agent,
    max_utter_length=None,
)

@app.post("/handle_request")
async def handle_request(request: Request):
    req = json.loads(
        (await request.body()).decode("utf-8")
    )
    body = req['body']
    response = manager(body)
    return {"response": response}


if __name__ == "__main__":
    pass