try:
    # Python < 2.7
    import unittest2 as unittest
except ImportError:
    import unittest
import mock

from ._helpers import (command_func_generator, irc_nickname, irc_nickname_list,
                       bot_command, bot_command_list)
from hypothesis import assume, given
from lala import util, pluginmanager
from re import compile
from twisted.internet.defer import Deferred
from twisted.python.failure import Failure


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

    @given(aliases=bot_command_list(min_size=1), gen=command_func_generator)
    def test_command_aliases(self, aliases, gen):
        pluginmanager._callbacks = {}

        f = gen()

        util.command(command="f", aliases=aliases)(f)

        all_triggers = aliases
        all_triggers.insert(0, "f")

        self.assertIn("Aliases: %s" % (", ".join(aliases)),
                      pluginmanager._callbacks["f"].func.__doc__)

        for alias in aliases:
            self.assertEqual(pluginmanager._callbacks["f"],
                             pluginmanager._callbacks[alias])

    @given(bot_command())
    def test_named_command(self, command):
        pluginmanager._callbacks = {}

        c = util.command(command)
        c(f)

        self.assertEqual(len(pluginmanager._callbacks), 1)
        self.assertTrue(command in pluginmanager._callbacks)

    @given(command=bot_command(), aliases=bot_command_list())
    def test_disabled_command(self, command, aliases):
        c = util.command(command, aliases=aliases)
        c(f3)

        pluginmanager.disable(command)
        self.assertFalse(pluginmanager._callbacks[command].enabled)
        for alias in aliases:
            self.assertFalse(pluginmanager._callbacks[alias].enabled)
        pluginmanager._handle_message("user", "channel", "!%s" % command)

    @given(command=bot_command(), aliases=bot_command_list())
    def test_reenabled_command(self, command, aliases):
        c = util.command(command, aliases=aliases)
        c(f3)

        pluginmanager.disable(command)
        pluginmanager.enable(command)
        self.assertTrue(pluginmanager._callbacks[command].enabled)
        self.assertRaises(ValueError, pluginmanager._handle_message, "user",
                          "channel", "!%s" % command)
        for alias in aliases:
            self.assertTrue(pluginmanager._callbacks[alias].enabled)
            self.assertRaises(ValueError, pluginmanager._handle_message, "user",
                              "channel", "!%s" % alias)

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

    @given(bot_command())
    def test_message_called(self, command):
        mocked_f = mock.Mock(spec=f)
        pluginmanager.register_callback(command, mocked_f)
        pluginmanager._handle_message("user", "channel", "!%s" % command)
        mocked_f.assert_called_once_with("user", "channel", "")

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
    @given(username=irc_nickname(),
           admins=irc_nickname_list())
    def test_is_admin_no_nickserv_positive(self, mock, username, admins):
        admins.append(username)
        util._BOT.factory.nspassword = None
        mock.return_value = ",".join(admins)
        self.assertTrue(pluginmanager.is_admin(username))


    @mock.patch("lala.config._get")
    @given(username=irc_nickname(),
           admins=irc_nickname_list())
    def test_is_admin_no_nickserv_negative(self, mock, username, admins):
        assume(username not in admins)
        util._BOT.factory.nspassword = None
        mock.return_value = ",".join(admins)
        self.assertFalse(pluginmanager.is_admin(username))

    @mock.patch.multiple("lala.config", _get=mock.DEFAULT, _CFG=mock.DEFAULT)
    @given(username=irc_nickname(),
           admins=irc_nickname_list())
    def test_is_admin_with_nickserv_positive(self, _get, _CFG, username, admins):
        admins.append(username)
        util._BOT.factory.nspassword = "foobar"
        util._BOT.identified_admins = admins
        _get.return_value = ",".join(admins)
        _CFG.getboolean.return_value = True
        self.assertTrue(pluginmanager.is_admin(username))

    @mock.patch.multiple("lala.config", _get=mock.DEFAULT, _CFG=mock.DEFAULT)
    @given(username=irc_nickname(),
           admins=irc_nickname_list())
    def test_is_admin_with_nickserv_negative(self, _get, _CFG, username, admins):
        util._BOT.factory.nspassword = "foobar"
        util._BOT.identified_admins = admins

        assume(username not in util._BOT.identified_admins)

        _get.return_value = ",".join(admins)
        _CFG.getboolean.return_value = True
        self.assertFalse(pluginmanager.is_admin(username))

    @mock.patch.multiple("lala.config", _get=mock.DEFAULT, _CFG=mock.DEFAULT)
    @given(username=irc_nickname(),
           admins=irc_nickname_list())
    def test_is_admin_with_explicitly_disabled_nickserv_positive(self, _get, _CFG, username, admins):
        admins.append(username)
        util._BOT.factory.nspassword = "testpassword"
        _get.return_value = ",".join(admins)
        _CFG.getboolean.return_value = False
        self.assertTrue(pluginmanager.is_admin(username))

    @mock.patch.multiple("lala.config", _get=mock.DEFAULT, _CFG=mock.DEFAULT)
    @given(username=irc_nickname(),
           admins=irc_nickname_list())
    def test_is_admin_with_explicitly_disabled_nickserv_negative(self, _get, _CFG, username, admins):
        assume(username not in admins)
        util._BOT.factory.nspassword = "testpassword"
        _get.return_value = ",".join(admins)
        _CFG.getboolean.return_value = False
        self.assertFalse(pluginmanager.is_admin(username))

    @mock.patch("lala.config._get")
    @given(username=irc_nickname(min_size=2))
    def test_is_admin_partial_match(self, mock, username):
        mock.return_value = username
        self.assertFalse(pluginmanager.is_admin(username[1:]))
        self.assertFalse(pluginmanager.is_admin(username[:-1]))

    @mock.patch("lala.config._get")
    @given(username=irc_nickname(), admins=irc_nickname_list())
    def test_admin_only_command_as_non_admin(self, mock, username, admins):
        assume(username not in admins)
        util._BOT.factory.nspassword = None
        mock.return_value = ",".join(admins)

        util.command(command="mock", admin_only=True)(f3)
        pluginmanager._handle_message(username, "#channel", "!mock")

    @mock.patch("lala.pluginmanager._generic_errback")
    def test_automatically_adds_errbacks_deferred(self, mock):
        d = Deferred()

        def return_deferred(u, c, t):
            return d

        util.command(command="mock")(return_deferred)
        f = Failure(ValueError(""))
        pluginmanager._handle_message("gandalf", "#channel", "!mock")
        d.errback(f)
        mock.assert_called_once_with("gandalf", "#channel", f)

    @mock.patch("lala.pluginmanager._generic_errback")
    def test_automatically_adds_errbacks_multiple_deferreds(self, errb):
        ds = [Deferred(), Deferred()]

        def return_deferred(u, c, t):
            for d in ds:
                yield d

        util.command(command="errb")(return_deferred)
        f = Failure(ValueError(""))
        pluginmanager._handle_message("gandalf", "#channel", "!errb")
        for d in ds:
            d.errback(f)
        self.assertEqual(errb.call_count, 2)
        c = [mock.call("gandalf", "#channel", f)] * 2
        self.assertEqual(c, errb.call_args_list)
