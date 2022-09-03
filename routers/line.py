import configparser
import logging
from datetime import datetime
from builtins import bytes
import os
import sys

from fastapi import (
    APIRouter,
    Request,
    BackgroundTasks,
    HTTPException,
)
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

from model.agent import GPT2Agent
from controller import UserManagerForEval


router = APIRouter()

config = configparser.ConfigParser()
config.read('env.ini')

line_logger = logging.getLogger('line')
fileHandler = logging.FileHandler(config['LINE']['LogFile'], mode='a')
line_logger.setLevel(logging.DEBUG)
line_logger.addHandler(fileHandler)

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

agent1 = GPT2Agent(
    model_name=config['GPT2Agent']['ModelName'],
    model_checkpoint=config['GPT2Agent']['ModelCheckpoint'],
)
agent1.name = "bmodel"

agent2 = GPT2Agent(
    model_name=config['FemaleGPT2Agent']['ModelName'],
    model_checkpoint=config['FemaleGPT2Agent']['ModelCheckpoint'],
)
agent2.name = "fmodel"

manager = UserManagerForEval(
    agent1=agent1,
    agent2=agent2,
    eval_turn=10,
    max_utter_length=2,
    save_dir=config['LINE']['DialogSaveDirectory'],
    url=config['EvalDialogModel']['URL'],
)


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

        response = manager.reply(event.source.user_id, event.message.text)

        try:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=response)
            )
        except:
            line_logger.error("Couldn't reply message: reply_token = %s", event.reply_token)


@router.post("/line")
async def line_endpoint(request: Request, background_tasks: BackgroundTasks):
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
