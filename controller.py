import csv
import os
from glob import glob
from time import time
from typing import Optional

from model.agent import BaseAgent


DIALOG_SAVE_DIR = "data/dialog"


class UserManager():
    def __init__(self, agent: BaseAgent, max_utter_length: int = 1):
        """
        """
        self.user_instances: dict[str, DialogManager] = dict()
        self.agent: BaseAgent = agent
        self.max_utter_length: int = max_utter_length
        self.latest_id = 0
        if not os.path.isdir(DIALOG_SAVE_DIR):
            os.makedirs(DIALOG_SAVE_DIR)
        else:
            fnames = sorted(glob(os.path.join(DIALOG_SAVE_DIR, "*.csv")))
            if fnames:
                last_fname = fnames.pop()
                bname = os.path.basename(last_fname)
                title, _ = os.path.splitext(last_fname)
                self.latest_id = int(title.split("-").pop())

    def __call__(self, user_id: str, input_: str) -> str:
        print(user_id)
        if user_id in self.user_instances:
            instance = self.user_instances[user_id]
        else:
            self.latest_id += 1
            instance = DialogManager(self.latest_id, self.agent, self.max_utter_length)
            self.user_instances[user_id] = instance

        reply = instance(input_)
        return reply


class DialogManager():
    def __init__(self, id_: int, agent: BaseAgent, max_utter_length: int = 1):
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

    def __call__(self, input_: str) -> str:
        intime = time()
        inputs = self.dialog[-self.max_utter_length:]
        reply = self.agent.reply(inputs, top_p=0.99, top_k=10)
        reptime = time()

        self.dialog.append(input_)
        self.dialog.append(reply)

        fname = os.path.join(DIALOG_SAVE_DIR, f"{self.agent.name}-{self.id}.csv")
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
