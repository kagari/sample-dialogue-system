import configparser
import logging
from datetime import datetime
from builtins import bytes
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

from model.agent import EchoAgent
from controller import UserManager


router = APIRouter()

config = configparser.ConfigParser()
config.read('env.ini')

line_logger = logging.getLogger('line')
fileHandler = logging.FileHandler(config['LINE']['LogFile'], mode='a')
line_logger.setLevel(logging.INFO)
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

manager = UserManager(
    EchoAgent(),
    config['Mattermost']['DialogSaveDirectory'],
    max_utter_length=20,
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

        response = manager(event.message.text)

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
