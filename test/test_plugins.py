import lala.config
import lala.pluginmanager
import lala.util
import random
try:
    # Python < 2.7
    import unittest2 as unittest
except ImportError:
    import unittest

from . import _helpers
from ._helpers import mock
from hypothesis import given
from hypothesis.strategies import integers
from importlib import import_module
from six.moves import configparser, range
from twisted.python.failure import Failure


class PluginTestCase(unittest.TestCase):
    plugin = None
    user = "user"
    channel = "#channel"

    @classmethod
    def setUpClass(cls):
        lala.config._CFG = configparser.RawConfigParser()
        lala.config._set("quotes", "database_path", ":memory:")
        lala.pluginmanager._callsbacks = {}
        lala.pluginmanager._regexes = {}
        lala.pluginmanager._join_callbacks = []
        cls.mod = import_module("lala.plugins.%s" % cls.plugin)
        default_opts = getattr(cls.mod, lala.pluginmanager.DEFAULT_OPTIONS_VARIABLE,
                               None)
        if default_opts is not None:
            lala.config._set_default_options(cls.plugin, default_opts)
        initf = getattr(cls.mod, lala.pluginmanager.MODULE_INIT_FUNC, None)
        if initf is not None:
            initf()

    def setUp(self):
        msg_patcher = mock.patch('lala.plugins.%s.msg' % self.plugin)
        msg_patcher.start()
        self.addCleanup(msg_patcher.stop)

    def handle_message(self, msg):
        """Instruct the plugin manager to handle ``msg``
        :param str msg:
        """
        lala.pluginmanager._handle_message(self.user, self.channel, msg)


class TestFortune(PluginTestCase):
    plugin = "fortune"

    def test_fortune(self):
        self.mod.getProcessOutput = _helpers.DeferredHelper(
            data="fortune")
        self.handle_message("!fortune")
        self.mod.getProcessOutput.callback()
        self.mod.msg.assert_called_once_with(self.channel, "user: fortune")

    def test_ofortune(self):
        self.mod.getProcessOutput = _helpers.DeferredHelper(
            data="ofortune")
        self.handle_message("!ofortune")
        self.mod.getProcessOutput.callback()
        self.mod.msg.assert_called_once_with(self.channel, "user: ofortune")

    def test_fortune_with_default_files(self):
        # A space is in front of 'people' to make sure whitespace around
        # arguments is properly stripped.
        lala.config._set("fortune", "fortune_files", "riddles, people")
        self.mod.getProcessOutput = _helpers.DeferredHelper(
            data="fortune")
        self.handle_message("!fortune")
        self.mod.getProcessOutput.callback()
        self.mod.msg.assert_called_once_with(self.channel, "user: fortune")
        # The first entry is the path to the fortune binary
        self.assertEqual(self.mod.getProcessOutput.args[1:][0],
                         ["riddles", "people"])

    def test_fortune_with_non_default_files(self):
        self.mod.getProcessOutput = _helpers.DeferredHelper(
            data="fortune")
        self.handle_message("!fortune people riddles")
        self.mod.getProcessOutput.callback()
        self.mod.msg.assert_called_once_with(self.channel, "user: fortune")
        # The first entry is the path to the fortune binary
        self.assertEqual(self.mod.getProcessOutput.args[1:][0],
                         ["people", "riddles"])


class TestBase(PluginTestCase):
    plugin = "base"

    @classmethod
    def setUpClass(cls):
        super(TestBase, cls).setUpClass()
        lala.util._BOT = mock.Mock()
        lala.util._BOT.factory.nspassword = None
        lala.config._CFG = mock.Mock()
        lala.config._CFG.get.return_value = "user,user2"
        lala.pluginmanager.enable = mock.Mock()
        lala.pluginmanager.disable = mock.Mock()

    def setUp(self):
        super(TestBase, self).setUp()
        self.mod.is_admin = mock.Mock(return_value=True)

    def test_addadmin(self):
        self.handle_message("!addadmin user3")
        lala.config._CFG.set.assert_called_once_with("base", "admins",
                                                     "user,user2,user3")

    def test_addadmin_already_admin(self):
        self.handle_message("!addadmin user")
        self.mod.msg.assert_called_once_with(self.channel,
                                             "user already is an admin")

    def test_admins(self):
        self.handle_message("!admins")
        self.mod.msg.assert_called_once_with(self.channel, "user,user2")

    def test_deladmin(self):
        self.handle_message("!deladmin user2")
        lala.config._CFG.set.assert_called_once_with("base", "admins",
                                                     "user")

    def test_deladmin_is_no_admin(self):
        self.handle_message("!deladmin user3")
        self.mod.msg.assert_called_once_with(
            self.channel, "Sorry, user3 is not even an admin")

    def test_disable(self):
        self.handle_message("!disable command")
        lala.pluginmanager.disable.assert_called_once_with("command")

    def test_enable(self):
        self.handle_message("!enable command")
        lala.pluginmanager.enable.assert_called_once_with("command")

    def test_join(self):
        self.handle_message(u"!join #channel")
        lala.util._BOT.join.assert_called_once_with(b"#channel")

    def test_part(self):
        self.handle_message(u"!part #channel")
        lala.util._BOT.part.assert_called_once_with(b"#channel")

    def test_quit(self):
        self.mod.reactor = mock.Mock()
        self.handle_message("!quit")
        lala.util._BOT.quit.assert_called_once_with("leaving")

    def test_reconnect(self):
        self.handle_message("!reconnect")
        lala.util._BOT.quit.assert_called_once_with("leaving")

    def test_server(self):
        lala.util._BOT.server = "irc.nowhere.invalid"
        self.handle_message("!server")
        self.mod.msg.assert_called_once_with(self.user, "irc.nowhere.invalid")

    def tearDown(self):
        super(TestBase, self).tearDown()
        self.mod.msg.reset_mock()
        lala.util._BOT.quit.reset_mock()
        lala.pluginmanager.disable.reset_mock()
        lala.pluginmanager.enable.reset_mock()
        lala.config._CFG.set.reset_mock()


class TestHTTPTitle(PluginTestCase):
    plugin = "httptitle"

    def test_title(self):
        url = "http://example.com"
        self.mod.getPage = _helpers.DeferredHelper(
            data="<html><head><title>title</title></head></html>")
        self.handle_message(url)
        self.mod.getPage.callback()
        self.assertTrue(url in self.mod.getPage.args)
        self.mod.msg.assert_called_once_with(self.channel, "Title: title")

    def test_notitle(self):
        self.mod.getPage = _helpers.DeferredHelper(
            data="<html></html>")
        self.handle_message("http://example.com")
        self.mod.getPage.callback()
        self.assertFalse(self.mod.msg.called)

    def test_errback(self):
        url = "http://example.com"
        f = Failure(Exception())
        self.mod.getPage = _helpers.DeferredHelper(data=f)
        self.handle_message(url)

        def check_error_got_passed_through(error):
            self.assertEqual(error, f)

        self.mod.getPage.addErrback(
            check_error_got_passed_through)
        self.mod.getPage.errback()
        self.mod.msg.assert_called_once_with(self.channel,
                                             "Sorry, I couldn't get the title for %s" % url)


class TestRoulette(PluginTestCase):
    plugin = "roulette"

    def setUp(self):
        super(TestRoulette, self).setUp()
        self.mod.gun.reload()

    def test_autoreload(self):
        self.mod.gun.bullet = 6
        self.mod.gun.chamber = 5
        self.handle_message("!shoot")
        self.mod.msg.assert_called_with(self.channel, "Reloading")

    def test_shoot(self):
        for chamber in range(1, 6):
            self.mod.gun.bullet = chamber
            for i in range(1, chamber + 1):
                self.handle_message("!shoot")
                if i == chamber:
                    # boom!
                    self.mod.msg.assert_any_call(self.channel,
                                                 "user: Chamber %s of 6: BOOM" % chamber)
                    self.mod.msg.assert_any_call(self.channel, "Reloading")
                else:
                    self.mod.msg.assert_called_with(self.channel,
                                                    "user: Chamber %s of 6: *click*" % i)
            self.mod.msg.reset_mock()

    def test_reload(self):
        self.mod.gun.chamber = 6
        self.handle_message("!reload")
        self.assertEqual(self.mod.gun.chamber, 1)
        self.assertTrue(self.mod.gun.bullet in range(1, 7))


class TestQuotes(PluginTestCase):
    plugin = "quotes"

    def execute_example(self, f):
        self.setUp()
        try:
            return f()
        finally:
            self.tearDown()

    def test_on_join(self):
        self.mod.db_connection.runQuery = _helpers.DeferredHelper(
            data=[[1, "testquote"]])
        lala.pluginmanager.on_join(self.user, self.channel)
        self.mod.db_connection.runQuery.callback()
        self.mod.msg.assert_called_once_with(self.channel, "[1] testquote")

    def test_on_join_no_quote(self):
        self.mod.db_connection.runQuery = _helpers.DeferredHelper(data=[])
        lala.pluginmanager.on_join(self.user, self.channel)
        self.assertFalse(self.mod.msg.called)

    @_helpers.mock_is_admin
    @given(integers())
    def test_delquote_no_quote(self, qnum):
        self.mod.db_connection.runInteraction = _helpers.DeferredHelper(data=0)
        self.handle_message("!delquote %d" % qnum)
        self.mod.db_connection.runInteraction.callback()
        self.mod.msg.assert_called_with(self.channel,
                                        "It doesn't look like quote #%d exists." % qnum)

    @_helpers.mock_is_admin
    def test_delquote_with_quote(self):
        self.mod.db_connection.runInteraction =\
            _helpers.DeferredHelper(data=1)
        self.handle_message("!delquote 1")
        self.mod.db_connection.runInteraction.callback()
        self.mod.msg.assert_called_with(self.channel,
                                        "Quote #1 has been deleted.")

    @given(integers(min_value=0))
    def test_getquote(self, qnum):
        data = [(qnum, "testquote", None, 0)]
        self.mod.db_connection.runQuery = _helpers.DeferredHelper(data=data)
        self.handle_message("!getquote %d" % qnum)
        self.mod.db_connection.runQuery.callback()
        self.mod.msg.assert_called_with(self.channel,
                                        self.mod.MESSAGE_TEMPLATE_WITH_RATING % data[0])

    @given(integers(min_value=0))
    def test_getquote_no_quote(self, qnum):
        data = []
        self.mod.db_connection.runQuery = _helpers.DeferredHelper(data=data)
        self.handle_message("!getquote %d" % qnum)
        self.mod.db_connection.runQuery.callback()
        self.mod.msg.assert_called_with(self.channel, "%s: There's no quote #%s"
                                        % (self.user, qnum))

    @given(integers(min_value=0))
    def test_getquote_none_quote(self, qnum):
        data = [(None,  # quote id
                 None,  # quote text
                 None,  # rating
                 0)]
        self.mod.db_connection.runQuery = _helpers.DeferredHelper(data=data)
        self.handle_message("!getquote %d" % qnum)
        self.mod.db_connection.runQuery.callback()
        self.mod.msg.assert_called_with(self.channel, "%s: There's no quote #%s"
                                        % (self.user, qnum))

    def test_qflop(self):
        data = [("1", "quote", "1", "4"), ("2", "quote", "2", "3")]
        calls = [mock.call(self.channel, self.mod.MESSAGE_TEMPLATE_WITH_RATING % d) for d in data]
        self.mod.db_connection.runQuery = _helpers.DeferredHelper(data=data)
        self.handle_message("!qflop")
        self.mod.db_connection.runQuery.callback()
        self.mod.msg.assert_has_calls(calls)

    def test_qtop(self):
        data = [("2", "quote", "2", "3"), ("1", "quote", "1", "4")]
        calls = [mock.call(self.channel, self.mod.MESSAGE_TEMPLATE_WITH_RATING % d) for d in data]
        self.mod.db_connection.runQuery = _helpers.DeferredHelper(data=data)
        self.handle_message("!qtop")
        self.mod.db_connection.runQuery.callback()
        self.mod.msg.assert_has_calls(calls)

    def test_searchquote(self):
        max_quotes = int(lala.config._get("quotes", "max_quotes"))
        data = []
        for i in range(max_quotes):
            data.append([i, "testquote %i" % i])
        self.mod.db_connection.runQuery = _helpers.DeferredHelper(data=data)
        self.handle_message("!searchquote test")
        self.mod.db_connection.runQuery.callback()
        for i in data:
            self.mod.msg.assert_any_call(self.channel,
                                         self.mod.MESSAGE_TEMPLATE % (i[0], i[1]))

    def test_searchquote_none_found(self):
        self.mod.db_connection.runQuery = _helpers.DeferredHelper(data=[])
        self.handle_message("!searchquote foo")
        self.mod.db_connection.runQuery.callback()
        self.mod.msg.assert_called_once_with(self.channel, "No matching quotes found")

    def test_searchquote_too_many(self):
        max_quotes = int(lala.config._get("quotes", "max_quotes")) + 1
        data = []
        for i in range(max_quotes):
            data.append([i, "testquote %i" % i])
        self.mod.db_connection.runQuery = _helpers.DeferredHelper(data=data)
        self.handle_message("!searchquote test")
        self.mod.db_connection.runQuery.callback()
        self.mod.msg.assert_called_once_with(self.channel,
                                             "Too many results, please refine your search")


class TestBirthday(PluginTestCase):
    plugin = "birthday"

    def setUp(self):
        super(TestBirthday, self).setUp()
        self.mod.date = _helpers.NewDate

    def test_join_birthday(self):
        self.handle_message("!my_birthday_is 10.12.")
        lala.pluginmanager.on_join(self.user, self.channel)
        self.mod.msg.assert_called_once_with(self.channel,
                                             "\o\ Happy birthday, user /o/")

    def test_join_not_birthday(self):
        self.handle_message("!my_birthday_is 09.12.")
        lala.pluginmanager.on_join(self.user, self.channel)
        self.assertFalse(self.mod.msg.called)

    def test_past_birthday(self):
        lala.config._set("birthday", self.user, "09.12.2012")
        lala.pluginmanager.on_join(self.user, self.channel)
        self.assertEqual(lala.config._get("birthday", self.user), "09.12.2013")

    def test_set_birthday_not_yet(self):
        """Tests setting a birthday that has not already happened this year."""
        self.handle_message("!my_birthday_is 11.12.")
        self.assertEqual(lala.config._get("birthday", self.user), "11.12.2012")

    def test_set_birthday_already(self):
        """Tests setting a birthday that has already happened this year."""
        self.handle_message("!my_birthday_is 09.12.")
        self.assertEqual(lala.config._get("birthday", self.user), "09.12.2013")


class TestLast(PluginTestCase):
    plugin = "last"

    def setUp(self):
        super(TestLast, self).setUp()
        self.mod.datetime = _helpers.NewDateTime

    def _fill_log(self, entries):
        for i in range(entries):
            self.handle_message("text %i" % i)

    def test_chatlog(self):
        max_entries = int(lala.config._get("last", "max_lines"))
        self._fill_log(max_entries)

        self.assertEqual(len(self.mod._chatlog), max_entries)
        self.handle_message("text")
        self.assertEqual(len(self.mod._chatlog), max_entries)

    def test_last(self):
        max_entries = int(lala.config._get("last", "max_lines"))
        self._fill_log(max_entries)
        self.handle_message("!last")

        messages = []
        date = _helpers.NewDateTime.now().strftime(lala.config._get("last",
                                                   "datetime_format"))
        for i in range(max_entries):
            messages.append('[%s] user: text %i' % (date, i))
        self.mod.msg.assert_called_with('user', messages, log=False)


class TestCalendar(PluginTestCase):
    plugin = "calendar"

    def test_weeknum(self):
        self.mod.date = _helpers.NewDate
        self.handle_message("!weeknum")
        self.mod.msg.assert_called_once_with(self.channel,
                                             "It's week #50 of the year 2012.")


class TestDecide(PluginTestCase):
    plugin = "decide"

    def setUp(self):
        super(TestDecide, self).setUp()
        self.tries_half = int(self.mod.TRIES / 2)
        random.seed(123)

    def test_basic(self):
        self.handle_message("!decide 1/2/3")
        self.mod.msg.assert_called_once_with(self.channel,
                                             "user: 1")

    @mock.patch('lala.plugins.decide.Counter.most_common')
    def test_real_hard(self, counter_mock):
        # We could use the seed here, but even with a seeded RNG the results
        # differ across Python versions.
        counter_mock.side_effect = [[('1', self.tries_half), ('2', self.tries_half - 1)]]
        self.handle_message("!decide_real_hard 1/2/3")
        self.mod.msg.assert_called_once_with(self.channel,
                                             self.mod._REAL_HARD_TEMPLATE.format(user=self.user, choice="1", count=self.tries_half, tries=self.mod.TRIES))

    def test_real_hard_single_choice(self):
        self.handle_message("!decide_real_hard 1")
        self.mod.msg.assert_called_once_with(self.channel,
                                             self.mod._NO_CHOICE_NECESSARY_TEMPLATE.format(user=self.user, choice="1"))

    @mock.patch('lala.plugins.decide.Counter.most_common')
    def test_real_hard_exactly_half(self, counter_mock):
        counter_mock.side_effect = [[('1', self.tries_half), ('2', self.tries_half)],
                                    [('1', self.tries_half + 1), ('2', self.tries_half - 1)],
                                    ]
        self.handle_message("!decide_real_hard 1/2")
        self.mod.msg.assert_called_once_with(self.channel,
                                             self.mod._REAL_HARD_TEMPLATE.format(user=self.user, choice="1", count=self.tries_half + 1, tries = lala.plugins.decide.TRIES))
