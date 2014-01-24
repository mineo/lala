try:
    # Python < 2.7
    import unittest2 as unittest
except ImportError:
    import unittest
import mock

from lala import util, pluginmanager, config
from re import compile


def f(user, channel, text):
    pass


def f2(arg1, arg2):
    pass


def f3(user, channel, text):
    raise ValueError("I have been called, something is wrong")


def regex_f(user, channel, text, regex):
    raise ValueError("I have been called, something is wrong")


class TestPluginmanager(unittest.TestCase):
    def setUp(self):
        pluginmanager._callbacks = {}
        pluginmanager._regexes = {}
        pluginmanager._join_callbacks = []

    def test_on_join(self):
        self.assertEqual(len(pluginmanager._join_callbacks), 0)
        util.on_join(f2)
        self.assertEqual(len(pluginmanager._join_callbacks), 1)
        self.assertTrue(f2 in pluginmanager._join_callbacks)

    def test_command(self):
        self.assertEqual(len(pluginmanager._callbacks), 0)

        util.command(f)

        self.assertEqual(len(pluginmanager._callbacks), 1)
        self.assertTrue("f" in pluginmanager._callbacks)

    def test_named_command(self):
        self.assertEqual(len(pluginmanager._callbacks), 0)

        c = util.command("command")
        c(f)

        self.assertEqual(len(pluginmanager._callbacks), 1)
        self.assertTrue("command" in pluginmanager._callbacks)

    def test_disabled_command(self):
        c = util.command("command")
        c(f3)

        pluginmanager.disable("command")
        self.assertFalse(pluginmanager._callbacks["command"].enabled)
        pluginmanager._handle_message("user", "channel", "!command")

    def test_reenabled_command(self):
        c = util.command("command")
        c(f3)

        pluginmanager.disable("command")
        pluginmanager.enable("command")
        self.assertTrue(pluginmanager._callbacks["command"].enabled)
        self.assertRaises(ValueError, pluginmanager._handle_message, "user",
        "channel", "!command")

    def test_regex(self):
        self.assertEqual(len(pluginmanager._regexes), 0)

        regex = compile(".*")
        r = util.regex(regex)
        r(regex_f)

        self.assertEqual(len(pluginmanager._regexes), 1)
        self.assertTrue(regex in pluginmanager._regexes)

    def test_disabled_regex(self):
        regex = compile("command")
        c = util.regex(regex)
        c(regex_f)

        pluginmanager.disable(regex.pattern)
        self.assertFalse(pluginmanager._regexes[regex].enabled)
        pluginmanager._handle_message("user", "channel", "command")

    def test_reenabled_regex(self):
        regex = compile("command")
        c = util.regex(regex)
        c(regex_f)

        pluginmanager.disable(regex.pattern)
        pluginmanager.enable(regex.pattern)
        self.assertTrue(pluginmanager._regexes[regex].enabled)
        self.assertRaises(ValueError, pluginmanager._handle_message, "user",
        "channel", "command")

    def test_message_called(self):
        mocked_f = mock.Mock(spec=f)
        pluginmanager.register_callback("test", mocked_f)
        pluginmanager._handle_message("user", "channel", "!test")
        mocked_f.assert_called_once_with("user", "channel", "!test")

    def test_on_join_called(self):
        mocked_f = mock.Mock(spec=f2)
        pluginmanager.register_join_callback(mocked_f)
        pluginmanager.on_join("user", "channel")
        mocked_f.assert_called_once_with("user", "channel")

    def test_regex_called(self):
        mocked_f = mock.Mock(spec=f)
        pluginmanager.register_regex(compile("test"), mocked_f)
        pluginmanager._handle_message("user", "channel", "regex")
        self.assertFalse(mocked_f.called)
        pluginmanager._handle_message("user", "channel", "test foobar")
        self.assertTrue(mocked_f.called)

    @mock.patch("lala.config._get")
    def test_is_admin_no_nickserv(self, mock):
        util._BOT.factory.nspassword= None
        mock.return_value = "superman,gandalf"
        self.assertTrue(pluginmanager.is_admin("superman"))
        self.assertFalse(pluginmanager.is_admin("i'm-no-superman"))

    @mock.patch("lala.config._get")
    def test_is_admin_with_nickserv(self, mock):
        util._BOT.factory.nspassword = "foobar"
        util._BOT.identified_admins = ["superman"]
        mock.return_value = "superman,gandalf"
        self.assertTrue(pluginmanager.is_admin("superman"))
        self.assertFalse(pluginmanager.is_admin("i'm-no-superman"))

    @mock.patch("lala.config._get")
    def test_is_admin_partial_match(self, mock):
        mock.return_value = "superman,gandalf"
        self.assertFalse(pluginmanager.is_admin("gandal"))

    @mock.patch("lala.config._get")
    def test_admin_only_command_as_non_admin(self, mock):
        util._BOT.factory.nspassword= None
        mock.return_value = "superman"
        func_mock = mock.Mock()
        util.command(command="mock", admin_only=True)(func_mock)
        pluginmanager._handle_message("gandalf", "#channel", "!mock")
        self.assertFalse(func_mock.called)
