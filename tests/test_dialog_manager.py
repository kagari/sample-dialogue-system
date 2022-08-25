import os
import shutil
import unittest

from model.agent import EchoAgent
from controller import UserManager


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


class TestResponseAPIforMattermost(unittest.TestCase):
    pass