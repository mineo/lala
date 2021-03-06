import lala.pluginmanager
from ._helpers import mock

from ._helpers import bot_command, bot_command_list, LalaTestCase
from hypothesis import given
from lala import util
from re import compile


def f(user, channel, text):
    pass


def f2(arg1, arg2):
    pass


def regex_f(arg1, arg2, arg3, arg4):
    pass


class TestUtil(LalaTestCase):
    def setUp(self):
        super(TestUtil, self).setUp()
        pm_patcher = mock.patch('lala.pluginmanager')
        pm_patcher.start()
        self.addCleanup(pm_patcher.stop)

    def test_on_join(self):
        util.on_join(f2)
        lala.pluginmanager.register_join_callback.assert_called_once_with(f2)

    def test_command(self):
        util.command(f)
        lala.pluginmanager.register_callback.assert_called_once_with("f", f, False, None)

    @given(bot_command())
    def test_named_command(self, command):
        lala.pluginmanager.register_callback.reset_mock()
        c = util.command(command)
        c(f)
        lala.pluginmanager.register_callback.assert_called_once_with(command, f, False, None)

    @given(bot_command_list())
    def test_command_aliases(self, aliases):
        lala.pluginmanager.register_callback.reset_mock()
        c = util.command(aliases=aliases)
        c(f)
        lala.pluginmanager.register_callback.assert_called_once_with("f", f, False, aliases)

    def test_command_str(self):
        self.assertRaises(TypeError, util.command, object())

    def test_regex(self):
        regex = compile(".*")
        r = util.regex(regex)
        r(regex_f)
        lala.pluginmanager.register_regex.assert_called_once_with(regex, regex_f)

    def test_argcheck(self):
        self.assertFalse(util._check_args(f, 2))
        self.assertTrue(util._check_args(f, 3))

        self.assertRaises(TypeError, util.command, f2)
        self.assertRaises(TypeError, util.on_join, f)

        r = util.regex("foobar")
        self.assertRaises(TypeError, r, f2)

    def test_message(self):
        util.msg("user", "message")
        util._BOT.msg.assert_called_once_with("user", "message", True)

        util.msg("user", ["message1", "message2"])
        util._BOT.msg.assert_called_with("user", "message2", True)
        self.assertEqual(len(util._BOT.msg.call_args_list), 3)
        self.assertEqual(util._BOT.msg.call_args_list[1][0][1], "message1")

    def test_empty_message(self):
        util.msg("user", "")
        self.assertFalse(util._BOT.msg.called)
        util.msg("user", ["", ""])
        self.assertFalse(util._BOT.msg.called)
