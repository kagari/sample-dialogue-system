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

from model.agent import BaseAgent, EchoAgent
from controller import DialogManager, UserManager


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


class UserManagerForEval:
    def __init__(self, agent1: BaseAgent, agent2: BaseAgent, eval_turn: int, max_utter_length: int, save_dir: str, url: str) -> None:
        self.agent1 = agent1
        self.agent2 = agent2
        self.eval_turn = eval_turn
        self.max_utter_length = max_utter_length
        self.save_dir = save_dir
        self.url = url
        self.user_instances: dict[str, DialogManager] = dict()
        self.latest_id = 0
        if not os.path.isdir(self.save_dir):
            os.makedirs(self.save_dir)
        return

    def reply(self, user_id: str, input_: str) -> str:
        if user_id not in self.user_instances:
            self.latest_id += 1
            self.user_instances[user_id] = DialogManager(self.latest_id, self.agent1, self.save_dir, self.max_utter_length)
        instance = self.user_instances[user_id]
        reply = instance(input_)
        if len(instance.dialog)//2 ==  self.eval_turn:
            instance.dialog = []
            dialog_id = f"{instance.agent.name}-{instance.id}"
            url_message = (f"対話番号: {dialog_id}\n" +
                "以下のURLからアンケートの回答をお願いします。\n" +
                self.url)
            reply += "\n\n" + url_message
            if instance.agent.name == self.agent1.name:
                instance.agent = self.agent2
            else:
                instance.agent = self.agent1
        return reply


