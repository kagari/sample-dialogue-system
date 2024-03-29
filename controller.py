import csv
import os
from glob import glob
from time import time

from model.agent import BaseAgent


class UserManager():
    def __init__(self, agent: BaseAgent, save_dir: str, max_utter_length: int = 1):
        """
        """
        self.user_instances: dict[str, DialogManager] = dict()
        self.agent: BaseAgent = agent
        self.max_utter_length: int = max_utter_length
        self.save_dir: str = save_dir
        self.latest_id: int = 0
        if not os.path.isdir(self.save_dir):
            os.makedirs(self.save_dir)
        else:
            fnames = sorted(glob(os.path.join(self.save_dir, "*.csv")))
            if fnames:
                last_fname = fnames.pop()
                bname = os.path.basename(last_fname)
                title, _ = os.path.splitext(bname)
                self.latest_id = int(title.split("-").pop())

    def __call__(self, user_id: str, input_: str) -> str:
        if user_id in self.user_instances:
            instance = self.user_instances[user_id]
        else:
            self.latest_id += 1
            instance = DialogManager(self.latest_id, self.agent, self.save_dir, self.max_utter_length)
            self.user_instances[user_id] = instance

        reply = instance(input_)
        return reply


class DialogManager():
    def __init__(self, id_: int, agent: BaseAgent, save_dir: str, max_utter_length: int = 1):
        """
        max_utter_length (int): max number of utterance.
            1 is only use user input.
            2 is that use user input and system output.
            default 1.
        dialog (list[tuple[sys|usr, str]]): ["x1", "y1", ..., "xn", "yn"]
        """
        self.id: int = id_
        self.dialog: list[str] = []
        self.agent: BaseAgent = agent
        self.max_utter_length: int = max_utter_length
        self.save_dir: str = save_dir

    def __call__(self, input_: str) -> str:
        self.dialog.append(input_)
        intime = time()
        inputs = self.dialog[-self.max_utter_length:]
        reply = self.agent.reply(inputs)
        reptime = time()
        self.dialog.append(reply)

        fname = os.path.join(self.save_dir, f"{self.agent.name}-{self.id}.csv")
        columns = ["timestamp", "from", "text"]
        if not os.path.isfile(fname):
            f = open(fname, "w", newline="")
            writer = csv.DictWriter(f, columns, quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()
        else:
            f = open(fname, "a", newline="")
            writer = csv.DictWriter(f, columns, quoting=csv.QUOTE_NONNUMERIC)

        writer.writerow(dict(zip(columns, [intime, "user", input_])))
        writer.writerow(dict(zip(columns, [reptime, "system", reply])))
        f.close()

        return reply


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
            url_message = (
                "これでこの対話は終了です。\n" +
                f"対話番号: {dialog_id}\n" +
                "以下のURLからアンケートの回答をお願いします。\n" +
                self.url)
            reply += "\n\n" + url_message
            if instance.agent.name == self.agent1.name:
                instance.agent = self.agent2
            else:
                instance.agent = self.agent1
        return reply
