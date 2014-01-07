import ConfigParser
import lala.config
import lala.pluginmanager
import lala.util
import mock
try:
    # Python < 2.7
    import unittest2 as unittest
except ImportError:
    import unittest

from . import _helpers


class PluginTestCase(unittest.TestCase):
    plugin = None

    @classmethod
    def setUpClass(cls):
        lala.config._CFG = ConfigParser.RawConfigParser()
        lala.config._set("quotes", "database_path", ":memory:")
        lala.pluginmanager._callsbacks = {}
        lala.pluginmanager._regexes = {}
        lala.pluginmanager._join_callbacks = []
        __import__("lala.plugins.%s" % cls.plugin)

    def setUp(self):
        msg_patcher = mock.patch('lala.util.msg')
        msg_patcher.start()
        self.addCleanup(msg_patcher.stop)


class TestFortune(PluginTestCase):
    plugin = "fortune"

    def setUp(self):
        super(TestFortune, self).setUp()
        lala.plugins.fortune.msg = lala.util.msg

    def test_fortune(self):
        lala.plugins.fortune.getProcessOutput = _helpers.DeferredHelper(
                                                data="fortune")
        lala.pluginmanager._handle_message("user", "#channel", "!fortune")
        lala.plugins.fortune.getProcessOutput._fire()
        lala.util.msg.assert_called_once_with("#channel", "user: fortune")

    def test_ofortune(self):
        lala.plugins.fortune.getProcessOutput = _helpers.DeferredHelper(
                                                data="ofortune")
        lala.pluginmanager._handle_message("user", "#channel", "!ofortune")
        lala.plugins.fortune.getProcessOutput._fire()
        lala.util.msg.assert_called_once_with("#channel", "user: ofortune")

    def test_fortune_with_default_files(self):
        # A space is in front of 'people' to make sure whitespace around
        # arguments is properly stripped.
        lala.config._set("fortune", "fortune_files", "riddles, people")
        lala.plugins.fortune.getProcessOutput = _helpers.DeferredHelper(
                                                data="fortune")
        lala.pluginmanager._handle_message("user", "#channel", "!fortune")
        lala.plugins.fortune.getProcessOutput._fire()
        lala.util.msg.assert_called_once_with("#channel", "user: fortune")
        # The first entry is the path to the fortune binary
        self.assertEqual(lala.plugins.fortune.getProcessOutput.args[1:][0],
                         ["riddles", "people"])

    def test_fortune_with_non_default_files(self):
        lala.plugins.fortune.getProcessOutput = _helpers.DeferredHelper(
                                                data="fortune")
        lala.pluginmanager._handle_message("user", "#channel", "!fortune people riddles")
        lala.plugins.fortune.getProcessOutput._fire()
        lala.util.msg.assert_called_once_with("#channel", "user: fortune")
        # The first entry is the path to the fortune binary
        self.assertEqual(lala.plugins.fortune.getProcessOutput.args[1:][0],
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
        lala.plugins.base.is_admin = mock.Mock(return_value=True)

    def test_addadmin(self):
        lala.pluginmanager._handle_message("user", "#channel", "!addadmin user3")
        lala.config._CFG.set.assert_called_once_with("base", "admins",
                                                    "user,user2,user3")

    def test_addadmin_already_admin(self):
        lala.pluginmanager._handle_message("user", "#channel", "!addadmin user")
        lala.util._BOT.msg.assert_called_once_with("#channel",
                "user already is an admin",
                True)

    def test_admins(self):
        lala.pluginmanager._handle_message("user", "#channel", "!admins")
        lala.util._BOT.msg.assert_called_once_with("#channel", "user,user2",
                                                   True)

    def test_deladmin(self):
        lala.pluginmanager._handle_message("user", "#channel", "!deladmin user2")
        lala.config._CFG.set.assert_called_once_with("base", "admins",
                                                          "user")

    def test_deladmin_is_no_admin(self):
        lala.pluginmanager._handle_message("user", "#channel", "!deladmin user3")
        lala.util._BOT.msg.assert_called_once_with(
                "#channel", "Sorry, user3 is not even an admin", True)

    def test_disable(self):
        lala.pluginmanager._handle_message("user", "#channel", "!disable command")
        lala.pluginmanager.disable.assert_called_once_with("command")

    def test_enable(self):
        lala.pluginmanager._handle_message("user", "#channel", "!enable command")
        lala.pluginmanager.enable.assert_called_once_with("command")

    def test_join(self):
        lala.pluginmanager._handle_message("user", "#channel", "!join #channel")
        lala.util._BOT.join.assert_called_once_with("#channel")

    def test_part(self):
        lala.pluginmanager._handle_message("user", "#channel", "!part #channel")
        lala.util._BOT.part.assert_called_once_with("#channel")

    def test_quit(self):
        lala.plugins.base.reactor = mock.Mock()
        lala.pluginmanager._handle_message("user", "#channel", "!quit")
        lala.util._BOT.quit.assert_called_once_with("leaving")

    def test_reconnect(self):
        lala.pluginmanager._handle_message("user", "#channel", "!reconnect")
        lala.util._BOT.quit.assert_called_once_with("leaving")

    def test_server(self):
        lala.util._BOT.server = "irc.nowhere.invalid"
        lala.pluginmanager._handle_message("user", "#channel", "!server")
        lala.util._BOT.msg.assert_called_once_with("user",
                                                   "irc.nowhere.invalid", True)

    def tearDown(self):
        super(TestBase, self).tearDown()
        lala.util._BOT.msg.reset_mock()
        lala.util._BOT.quit.reset_mock()
        lala.pluginmanager.disable.reset_mock()
        lala.pluginmanager.enable.reset_mock()
        lala.config._CFG.set.reset_mock()


class TestHTTPTitle(PluginTestCase):
    plugin = "httptitle"

    def setUp(self):
        super(TestHTTPTitle, self).setUp()
        lala.plugins.httptitle.msg = lala.util.msg

    def test_title(self):
        url = "http://example.com"
        lala.plugins.httptitle.getPage = _helpers.DeferredHelper(
                data="<html><head><title>title</title></head></html>")
        lala.pluginmanager._handle_message("user", "#channel", url)
        lala.plugins.httptitle.getPage._fire()
        self.assertTrue(url in lala.plugins.httptitle.getPage.args)
        lala.util.msg.assert_called_once_with("#channel", "Title: title")

    def test_notitle(self):
        lala.plugins.httptitle.getPage = _helpers.DeferredHelper(
                data="<html></html>")
        lala.pluginmanager._handle_message("user", "#channel", "http://example.com")
        lala.plugins.httptitle.getPage._fire()
        self.assertFalse(lala.util.msg.called)

    def test_errback(self):
        url = "http://example.com"
        lala.plugins.httptitle.getPage = _helpers.DeferredHelper(fire_callback=False,
                fire_errback=True, data=Exception())
        lala.pluginmanager._handle_message("user", "#channel", url)
        lala.plugins.httptitle.getPage._fire()
        lala.util.msg.assert_called_once_with("#channel",
                "Sorry, I couldn't get the title for %s" % url)


class TestRoulette(PluginTestCase):
    plugin = "roulette"

    def setUp(self):
        super(TestRoulette, self).setUp()
        lala.plugins.roulette.msg = lala.util.msg
        lala.plugins.roulette.gun.reload()
        lala.util.msg.reset_mock()

    def test_autorelaod(self):
        lala.plugins.roulette.gun.bullet = 6
        lala.plugins.roulette.gun.chamber = 5
        lala.pluginmanager._handle_message("user", "#channel", "!shoot")
        lala.util.msg.assert_called_with("#channel", "Reloading")

    def test_shoot(self):
        for chamber in range(1, 6):
            lala.plugins.roulette.gun.bullet = chamber
            for i in range(1, chamber + 1):
                lala.pluginmanager._handle_message("user", "#channel", "!shoot")
                if i == chamber:
                    #boom!
                    lala.util.msg.assert_any_call("#channel",
                                  "user: Chamber %s of 6: BOOM" % chamber)
                    lala.util.msg.assert_any_call("#channel", "Reloading")
                else:
                    lala.util.msg.assert_called_with("#channel",
                                  "user: Chamber %s of 6: *click*" % i)
            lala.util.msg.reset_mock()

    def test_reload(self):
        lala.plugins.roulette.gun.chamber = 6
        lala.pluginmanager._handle_message("user", "#channel", "!reload")
        self.assertEqual(lala.plugins.roulette.gun.chamber, 1)
        self.assertTrue(lala.plugins.roulette.gun.bullet in range(1, 7))


class TestQuotes(PluginTestCase):
    plugin = "quotes"

    def setUp(self):
        super(TestQuotes, self).setUp()
        lala.plugins.quotes.msg = lala.util.msg

    def test_on_join(self):
        lala.plugins.quotes.db_connection.runQuery = _helpers.DeferredHelper(
            data=[[1, "testquote"]])
        lala.pluginmanager.on_join("user", "#channel")
        lala.plugins.quotes.db_connection.runQuery._fire()
        lala.util.msg.assert_called_once_with("#channel", "[1] testquote")

    def test_on_join_no_quote(self):
        lala.plugins.quotes.db_connection.runQuery = _helpers.DeferredHelper(data=[])
        lala.pluginmanager.on_join("user", "#channel")
        self.assertFalse(lala.util.msg.called)

    @_helpers.mock_is_admin
    def test_delquote_no_quote(self):
        lala.plugins.quotes.db_connection.runInteraction =\
            _helpers.DeferredHelper(data=0)
        lala.pluginmanager._handle_message("user", "#channel", "!delquote 1")
        lala.plugins.quotes.db_connection.runInteraction._fire()
        lala.util.msg.assert_called_with("#channel",
            "It doesn't look like quote #1 exists.")

    @_helpers.mock_is_admin
    def test_delquote_with_quote(self):
        lala.plugins.quotes.db_connection.runInteraction =\
            _helpers.DeferredHelper(data=1)
        lala.pluginmanager._handle_message("user", "#channel", "!delquote 1")
        lala.plugins.quotes.db_connection.runInteraction._fire()
        lala.util.msg.assert_called_with("#channel",
            "Quote #1 has been deleted.")

    def test_getquote(self):
        data = [(1, "testquote")]
        lala.plugins.quotes.db_connection.runQuery = _helpers.DeferredHelper(data=data)
        lala.pluginmanager._handle_message("user", "#channel", "!getquote 1")
        lala.plugins.quotes.db_connection.runQuery._fire()
        lala.util.msg.assert_called_with("#channel",
                lala.plugins.quotes.MESSAGE_TEMPLATE % data[0])

    def test_getquote_no_quote(self):
        data = []
        lala.plugins.quotes.db_connection.runQuery = _helpers.DeferredHelper(data=data)
        lala.pluginmanager._handle_message("user", "#channel", "!getquote 1")
        lala.plugins.quotes.db_connection.runQuery._fire()
        lala.util.msg.assert_called_with("#channel", "%s: There's no quote #%s"
        %("user", 1))

    def test_searchquote(self):
        max_quotes = int(lala.config._get("quotes", "max_quotes"))
        data = []
        for i in xrange(max_quotes):
            data.append([i, "testquote %i" % i])
        lala.plugins.quotes.db_connection.runQuery = _helpers.DeferredHelper(data=data)
        lala.pluginmanager._handle_message("user", "#channel", "!searchquote test")
        lala.plugins.quotes.db_connection.runQuery._fire()
        for i in data:
            lala.util.msg.assert_any_call("#channel",
                    lala.plugins.quotes.MESSAGE_TEMPLATE % (i[0], i[1]))

    def test_searchquote_none_found(self):
        lala.plugins.quotes.db_connection.runQuery = _helpers.DeferredHelper(data=[])
        lala.pluginmanager._handle_message("user", "#channel", "!searchquote foo")
        lala.plugins.quotes.db_connection.runQuery._fire()
        lala.util.msg.assert_called_once_with("#channel", "No matching quotes found")

    def test_searchquote_too_many(self):
        max_quotes = int(lala.config._get("quotes", "max_quotes")) + 1
        data = []
        for i in xrange(max_quotes):
            data.append([i, "testquote %i" % i])
        lala.plugins.quotes.db_connection.runQuery = _helpers.DeferredHelper(data=data)
        lala.pluginmanager._handle_message("user", "#channel", "!searchquote test")
        lala.plugins.quotes.db_connection.runQuery._fire()
        lala.util.msg.assert_called_once_with("#channel",
                "Too many results, please refine your search")


class TestBirthday(PluginTestCase):
    plugin = "birthday"

    def setUp(self):
        super(TestBirthday, self).setUp()
        lala.plugins.birthday.msg = lala.util.msg
        lala.plugins.birthday.date = _helpers.NewDate

    def test_join_birthday(self):
        lala.pluginmanager._handle_message("user", "#channel", "!my_birthday_is 10.12.")
        lala.pluginmanager.on_join("user", "#channel")
        lala.plugins.birthday.msg.assert_called_once_with("#channel",
            "\o\ Happy birthday, user /o/")

    def test_join_not_birthday(self):
        lala.pluginmanager._handle_message("user", "#channel", "!my_birthday_is 09.12.")
        lala.pluginmanager.on_join("user", "#channel")
        self.assertFalse(lala.plugins.birthday.msg.called)

    def test_past_birthday(self):
        lala.config._set("birthday", "user", "09.12.2012")
        lala.pluginmanager.on_join("user", "#channel")
        self.assertEqual(lala.config._get("birthday", "user"), "09.12.2013")

    def test_set_birthday_not_yet(self):
        """Tests setting a birthday that has not already happened this year."""
        lala.pluginmanager._handle_message("user", "#channel", "!my_birthday_is 11.12.")
        self.assertEqual(lala.config._get("birthday", "user"), "11.12.2012")

    def test_set_birthday_already(self):
        """Tests setting a birthday that has already happened this year."""
        lala.pluginmanager._handle_message("user", "#channel", "!my_birthday_is 09.12.")
        self.assertEqual(lala.config._get("birthday", "user"), "09.12.2013")


class TestLast(PluginTestCase):
    plugin = "last"

    def setUp(self):
        super(TestLast, self).setUp()
        lala.plugins.last.msg = lala.util.msg
        lala.plugins.last.datetime = _helpers.NewDateTime

    def _fill_log(self, entries):
        for i in xrange(entries):
            lala.pluginmanager._handle_message("user", "#channel", "text %i" % i)

    def test_chatlog(self):
        max_entries = int(lala.config._get("last", "max_lines"))
        self._fill_log(max_entries)

        self.assertEqual(len(lala.plugins.last._chatlog), max_entries)
        lala.pluginmanager._handle_message("user", "#channel", "text")
        self.assertEqual(len(lala.plugins.last._chatlog), max_entries)

    def test_last(self):
        max_entries = int(lala.config._get("last", "max_lines"))
        self._fill_log(max_entries)
        lala.pluginmanager._handle_message("user", "#channel", "!last")

        messages = []
        date = _helpers.NewDateTime.now().strftime(lala.config._get("last",
                                                   "datetime_format"))
        for i in xrange(max_entries):
            messages.append('[%s] user: text %i' % (date, i))
        lala.util.msg.assert_called_with('user', messages, log=False)


class TestCalendar(PluginTestCase):
    plugin = "calendar"

    def setUp(self):
        super(TestCalendar, self).setUp()
        lala.plugins.calendar.msg = lala.util.msg

    def test_weeknum(self):
        lala.plugins.calendar.date = _helpers.NewDate
        lala.pluginmanager._handle_message("user", "#channel", "!weeknum")
        lala.plugins.calendar.msg.assert_called_once_with("#channel",
                "It's week #50 of the year 2012.")
