import os
import shutil
import unittest

from model.agent import EchoAgent
from controller import UserManager, DIALOG_SAVE_DIR


class TestUserManager(unittest.TestCase):
    def tearDown(self) -> None:
        self.tmp_dir = os.path.join(".", DIALOG_SAVE_DIR)
        shutil.rmtree(self.tmp_dir, ignore_errors=True)
        return

    def test_user_counting(self) -> None:
        user_manager = UserManager(EchoAgent(), 20)
        for id_, user_id in enumerate(['a', 'b', 'c', 'd', 'e'], start=1):
            _ = user_manager(user_id, 'hello!')
            instance = user_manager.user_instances[user_id]
            self.assertEqual(instance.id, id_)
            self.assertEqual(instance.dialog, ['hello!', 'hello!'])


class TestResponseAPIforMattermost(unittest.TestCase):
    pass