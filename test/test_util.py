import unittest
import mock

from lala import util, pluginmanager

def f(user, channel, text):
    pass

class TestUtil(unittest.TestCase):
    def setUp(self):
        util._PM = mock.Mock(spec=pluginmanager.PluginManager)

    def test_on_join(self):
        util.on_join(f)
        util._PM.register_join_callback.assert_called_once_with(f)

    def test_command(self):
        util.command(f)
        util._PM.register_callback.assert_called_once_with("f", f)

    def test_named_command(self):
        c = util.command("command")
        c(f)
        util._PM.register_callback.assert_called_once_with("command", f)

    def test_regex(self):
        r = util.regex(".*")
        r(f)
        util._PM.register_regex.assert_called_once_with(".*", f)

    def test_argcheck(self):
        self.assertFalse(util._check_args(f, 2))
        self.assertTrue(util._check_args(f, 3))

    def test_message(self):
        util._BOT = mock.Mock()
        util.msg("user", "message")
        util._BOT.msg.assert_called_once_with("user", "message", True)

        util.msg("user", ["message1", "message2"])
        util._BOT.msg.assert_called_with("user", "message2", True)
        self.assertEqual(util._BOT.msg.call_args_list[1][0][1], "message1")

    def test_empty_message(self):
        util._BOT = mock.Mock()
        util.msg("user", "message")
        util._BOT.msg.assert_called_once_with("user", "message", True)

        util.msg("user", ["message1", "" "message2"])
        util._BOT.msg.assert_called_with("user", "message2", True)
        self.assertEqual(len(util._BOT.msg.call_args_list), 3)
        self.assertEqual(util._BOT.msg.call_args_list[1][0][1], "message1")
