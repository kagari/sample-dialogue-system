from typing import Optional

from model.agent import BaseAgent


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
