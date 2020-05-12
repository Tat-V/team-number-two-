import unittest
import datetime
from Shushushu import LOG_ACTIONS, log_action, decorator_error
from unittest import mock


@log_action
def useless_function(update):
    return None


class TestLogging(unittest.TestCase):
    def setUp(self) -> None:
        self.update = mock.MagicMock()

    def tearDown(self) -> None:
        # global LOG_ACTIONS
        LOG_ACTIONS = []

    # def test_log_action(self):
    #     self.update.message.text = 'something important'
    #     self.update.effective_user.first_name = 'meaningless name'
    #     self.update.message.chat.id = 'some long integer'
    #     useless_function(self.update)
    #     self.assertEqual(LOG_ACTIONS, [{'user': 'meaningless name', 'user id': 'some long integer',
    #     'function': 'useless_function',
    #     'message': 'something important',
    #     'time': datetime.datetime.now().strftime("%Y-%m-%d %H.%M")}])

    def test_if_none(self):
        self.update = None
        useless_function(self.update)
        self.assertEqual(LOG_ACTIONS, [])

    def test_if_no_message(self):
        self.update = mock.MagicMock(spec=['effective_user'])
        useless_function(self.update)
        self.assertEqual(LOG_ACTIONS, [])

    def test_if_no_user(self):
        self.update = mock.MagicMock(spec=['message'])
        useless_function(self.update)
        self.assertEqual(LOG_ACTIONS, [])

    def test_no_update(self):
        with self.assertRaises(IndexError):
            useless_function()


if __name__ == '__main__':
    unittest.main()
