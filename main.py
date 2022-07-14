import configparser
import json
import sys
import time
import logging
from datetime import datetime

import uvicorn
from fastapi import (
    FastAPI,
    Request,
    BackgroundTasks,
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

line_logger = logging.getLogger('line')
fileHandler = logging.FileHandler(config['LINE']['LogFile'], mode='a')
line_logger.setLevel(logging.INFO)
line_logger.addHandler(fileHandler)


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
        reply = self.agent.reply(inputs, top_p=0.99, top_k=10)
        self.dialog.append(reply)
        return reply


s = time.time()
agent = GPT2Agent(
    model_name=config['GPT2Agent']['ModelName'],
    model_checkpoint=config['GPT2Agent']['ModelCheckpoint'],
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
        logger.error("status 400")
        raise HTTPException(status_code=400, detail="Bad Request")

    text = req['text']
    if text.startswith(req['trigger_word']):
        text = text[len(req['trigger_word'])+1:]

    logger.debug("request = %s", text)
    response = manager(text)
    return {
        "text": response,
        "response_type": "in_channel",
    }


from builtins import bytes
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage
)
from linebot.utils import PY3


channel_secret = config['LINE']['ChannelSecret']
channel_access_token = config['LINE']['AccessToken']
if channel_secret is None:
    print('Specify LINE ChannelSecret as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE ChannelAccessToken as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


def create_body(text):
    if PY3:
        return [bytes(text, 'utf-8')]
    else:
        return text


async def handle_events(events):
    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        response = manager(event.message.text)

        try:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=response)
            )
        except:
            line_logger.error("Couldn't reply message: reply_token = %s", event.reply_token)


@app.post("/line")
async def line(request: Request, background_tasks: BackgroundTasks):
    stime = datetime.now().isoformat(' ', timespec='seconds')

    signature = request.headers.get('X-Line-Signature') or \
        request.headers.get('x-line-signature')
    body = (await request.body()).decode("utf-8")

    if signature is None:
        line_logger.info('Webhook\t%s\t%s\t%s\t%s\t%d\t%s',
            stime, 'POST', '/line', signature, 400, body
        )
        raise HTTPException(status_code=400, detail="Bad Request")


    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        line_logger.info('Webhook\t%s\t%s\t%s\t%s\t%d\t%s',
            stime, 'POST', '/line', signature, 400, body
        )
        raise HTTPException(status_code=400, detail="Bad Request")

    background_tasks.add_task(handle_events, events=events)

    line_logger.info('Webhook\t%s\t%s\t%s\t%s\t%d\t%s',
        stime, 'POST', '/line', signature, 200, "ok"
    )
    return "ok"


if __name__ == "__main__":
    pass
