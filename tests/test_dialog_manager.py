import os
import shutil
import unittest

from model.agent import EchoAgent
from controller import UserManager
from routers.line import LINEResponderForEvaluation


class TestUserManager(unittest.TestCase):
    def setUp(self) -> None:
        self.test_save_dir = os.path.join("tests", "dialog")
        return

    def tearDown(self) -> None:
        shutil.rmtree(self.test_save_dir, ignore_errors=True)
        return

    def test_user_counting(self) -> None:
        user_manager = UserManager(EchoAgent(), self.test_save_dir, 20)
        for id_, user_id in enumerate(['a', 'b', 'c', 'd', 'e'], start=1):
            _ = user_manager(user_id, 'hello!')
            instance = user_manager.user_instances[user_id]
            self.assertEqual(instance.id, id_)
            self.assertEqual(instance.dialog, ['hello!', 'hello!'])
        return


class TestLINEResponderForEvaluation(unittest.TestCase):
    """対話システムの評価用の変更内容をテストする。
    具体的には以下の3つ。
    n回の応答後に、
    1. 対話履歴をリセットする
    1. POST API（のモック）を叩いて Google Form の URL と 対話番号（{モデル名}-{ユーザid}）を送る
    1. 対話モデルを入れ替える（BaseModel <-> GenderedModelなど）
    """
    def setUp(self) -> None:
        self.eval_turn = 10
        self.test_save_dir = os.path.join("tests", "dialog")
        return

    def tearDown(self) -> None:
        return

    def test_reset_dialog(self) -> None:
        user_id = "aaa"
        agent1 = EchoAgent()
        agent1.name = "agent1"
        agent2 = EchoAgent()
        agent2.name = "agent2"
        responder = LINEResponderForEvaluation(
            agent1=agent1,
            agent2=agent2,
            eval_turn=self.eval_turn,
            save_dir=self.test_save_dir,
            max_utter_length=1,
        )

        for len_, input_ in enumerate(map(str, range(self.eval_turn-1)), start=1):
            _ = responder.reply(user_id=user_id, input_=input_)
            self.assertEqual(len(responder.user_instances[user_id].dialog), len_*2)
            self.assertEqual(responder.user_instances[user_id].dialog[-1], input_)
        _ = responder.reply(user_id=user_id, input_=str(self.eval_turn))
        self.assertEqual(len(responder.user_instances[user_id].dialog), 0)
        return

    def test_post_form_url_and_dialog_id(self) -> None:
        pass
        return

    def test_switch_dialog_model(self) -> None:
        pass
        return


class TestResponseAPIforMattermost(unittest.TestCase):
    pass