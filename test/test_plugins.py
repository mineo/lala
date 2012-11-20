import ConfigParser
import lala.config
import lala.pluginmanager
import lala.util
import mock
import subprocess
import unittest

from . import _helpers


class PluginTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._old_pm = lala.util._PM
        lala.util._PM = lala.pluginmanager.PluginManager()
        lala.config._CFG = ConfigParser.SafeConfigParser()

    def setUp(self):
        self.old_msg = lala.util.msg
        lala.util.msg = mock.Mock()

    def tearDown(self):
        lala.util.msg = self.old_msg


class TestFortune(PluginTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestFortune, cls).setUpClass()
        import lala.plugins.fortune

    def setUp(self):
        super(TestFortune, self).setUp()
        subprocess.Popen = mock.Mock(spec=subprocess.Popen)
        popenreturnMock = mock.Mock()
        communicateMock = mock.Mock(return_value=["fortune"])

        popenreturnMock.returncode = 0
        subprocess.Popen.return_value = popenreturnMock
        popenreturnMock.communicate = communicateMock

        lala.plugins.fortune.msg = lala.util.msg

    def test_fortune(self):
        lala.util._PM._handle_message("user", "#channel", "!fortune")
        subprocess.Popen.assert_called_once_with(["fortune", "fortunes"],
                                                 stdout=subprocess.PIPE)
        lala.util.msg.assert_called_once_with("#channel", "user: fortune")

    def test_ofortune(self):
        lala.util._PM._handle_message("user", "#channel", "!ofortune")
        subprocess.Popen.assert_called_once_with(["fortune", "-o"],
                                                 stdout=subprocess.PIPE)
        lala.util.msg.assert_called_once_with("#channel", "user: fortune")

    def tearDown(self):
        super(TestFortune, self).tearDown()


class TestBase(PluginTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestBase, cls).setUpClass()
        import lala.plugins.base
        lala.util._BOT = mock.Mock()
        lala.config._CFG = mock.Mock()
        lala.config._CFG.get.return_value = "user,user2"
        lala.util._PM.enable = mock.Mock()
        lala.util._PM.disable = mock.Mock()

    def setUp(self):
        super(TestBase, self).setUp()
        lala.plugins.base.is_admin = mock.Mock(return_value=True)

    def test_addadmin(self):
        lala.util._PM._handle_message("user", "#channel", "!addadmin user3")
        lala.config._CFG.set.assert_called_once_with("base", "admins",
                                                          "user,user2,user3")

    def test_addadmin_already_admin(self):
        lala.util._PM._handle_message("user", "#channel", "!addadmin user")
        lala.util._BOT.msg.assert_called_once_with("#channel",
                "user already is an admin",
                True)

    def test_admins(self):
        lala.util._PM._handle_message("user", "#channel", "!admins")
        lala.util._BOT.msg.assert_called_once_with("#channel", "user,user2",
                                                   True)

    def test_deladmin(self):
        lala.util._PM._handle_message("user", "#channel", "!deladmin user2")
        lala.config._CFG.set.assert_called_once_with("base", "admins",
                                                          "user")

    def test_deladmin_is_no_admin(self):
        lala.util._PM._handle_message("user", "#channel", "!deladmin user3")
        lala.util._BOT.msg.assert_called_once_with(
                "#channel", "Sorry, user3 is not even an admin", True)

    def test_disable(self):
        lala.util._PM._handle_message("user", "#channel", "!disable command")
        lala.util._PM.disable.assert_called_once_with("command")

    def test_enable(self):
        lala.util._PM._handle_message("user", "#channel", "!enable command")
        lala.util._PM.enable.assert_called_once_with("command")

    def test_join(self):
        lala.util._PM._handle_message("user", "#channel", "!join #channel")
        lala.util._BOT.join_.assert_called_once_with("#channel")

    def test_part(self):
        lala.util._PM._handle_message("user", "#channel", "!part #channel")
        lala.util._BOT.part.assert_called_once_with("#channel")

    def test_quit(self):
        lala.plugins.base.reactor = mock.Mock()
        lala.util._PM._handle_message("user", "#channel", "!quit")
        lala.util._BOT.quit.assert_called_once_with("leaving")

    def test_reconnect(self):
        lala.util._PM._handle_message("user", "#channel", "!reconnect")
        lala.util._BOT.quit.assert_called_once_with("leaving")

    def test_server(self):
        lala.util._BOT.server = "irc.nowhere.invalid"
        lala.util._PM._handle_message("user", "#channel", "!server")
        lala.util._BOT.msg.assert_called_once_with("user",
                                                   "irc.nowhere.invalid", True)

    def tearDown(self):
        super(TestBase, self).tearDown()
        lala.util._BOT.msg.reset_mock()
        lala.util._BOT.quit.reset_mock()
        lala.util._PM.disable.reset_mock()
        lala.util._PM.enable.reset_mock()
        lala.config._CFG.set.reset_mock()


class TestHTTPTitle(PluginTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestHTTPTitle, cls).setUpClass()
        import lala.plugins.httptitle

    def setUp(self):
        super(TestHTTPTitle, self).setUp()
        lala.plugins.httptitle.msg = lala.util.msg

    def test_title(self):
        url = "http://example.com"
        lala.plugins.httptitle.getPage = _helpers.DeferredHelper(
                data="<html><head><title>title</title></head></html>")
        lala.util._PM._handle_message("user", "#channel", url)
        self.assertTrue(url in lala.plugins.httptitle.getPage.args)
        lala.util.msg.assert_called_once_with("#channel", "Title: title")

    def test_notitle(self):
        lala.plugins.httptitle.getPage = _helpers.DeferredHelper(
                data="<html></html>")
        lala.util._PM._handle_message("user", "#channel", "http://example.com")
        self.assertFalse(lala.util.msg.called)

    def test_errback(self):
        url = "http://example.com"
        lala.plugins.httptitle.getPage = _helpers.DeferredHelper(fire_callback=False,
                fire_errback=True)
        lala.util._PM._handle_message("user", "#channel", url)
        lala.util.msg.assert_called_once_with("#channel",
                "Sorry, I couldn't get the title for %s" % url)


class TestRoulette(PluginTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestRoulette, cls).setUpClass()
        import lala.plugins.roulette

    def setUp(self):
        super(TestRoulette, self).setUp()
        lala.plugins.roulette.msg = lala.util.msg
        lala.plugins.roulette.gun.reload()
        lala.util.msg.reset_mock()

    def test_autorelaod(self):
        lala.plugins.roulette.gun.bullet = 6
        lala.plugins.roulette.gun.chamber = 5
        lala.util._PM._handle_message("user", "#channel", "!shoot")
        lala.util.msg.assert_called_with("#channel", "Reloading")

    def test_shoot(self):
        for chamber in range(1, 6):
            lala.plugins.roulette.gun.bullet = chamber
            for i in range(1, chamber + 1):
                lala.util._PM._handle_message("user", "#channel", "!shoot")
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
        lala.util._PM._handle_message("user", "#channel", "!reload")
        self.assertEqual(lala.plugins.roulette.gun.chamber, 1)
        self.assertTrue(lala.plugins.roulette.gun.bullet in range(1, 7))


class TestQuotes(PluginTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestQuotes, cls).setUpClass()
        import lala.plugins.quotes

    def setUp(self):
        super(TestQuotes, self).setUp()
        lala.plugins.quotes.msg = lala.util.msg

    def test_on_join(self):
        lala.plugins.quotes.db_connection.runQuery = _helpers.DeferredHelper(
            data=[[1, "testquote"]])
        lala.util._PM.on_join("user", "#channel")
        lala.util.msg.assert_called_once_with("#channel", "[1] testquote")

    def test_on_join_no_quote(self):
        lala.plugins.quotes.db_connection.runQuery = _helpers.DeferredHelper(data=[])
        lala.util._PM.on_join("user", "#channel")
        self.assertFalse(lala.util.msg.called)

    def test_searchquote(self):
        max_quotes = int(lala.config._get("quotes", "max_quotes"))
        data = []
        for i in xrange(max_quotes):
            data.append([i, "testquote %i" % i])
        lala.plugins.quotes.db_connection.runQuery = _helpers.DeferredHelper(data=data)
        lala.util._PM._handle_message("user", "#channel", "!searchquote test")
        for i in data:
            lala.util.msg.assert_any_call("#channel",
                    lala.plugins.quotes.MESSAGE_TEMPLATE % (i[0], i[1]))

    def test_searchquote_too_many(self):
        max_quotes = int(lala.config._get("quotes", "max_quotes")) + 1
        data = []
        for i in xrange(max_quotes):
            data.append([i, "testquote %i" % i])
        lala.plugins.quotes.db_connection.runQuery = _helpers.DeferredHelper(data=data)
        lala.util._PM._handle_message("user", "#channel", "!searchquote test")
        lala.util.msg.assert_called_once_with("#channel",
                "Too many results, please refine your search")


class TestBirthday(PluginTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestBirthday, cls).setUpClass()
        import lala.plugins.birthday

    def setUp(self):
        super(TestBirthday, self).setUp()
        lala.plugins.birthday.msg = lala.util.msg
        lala.plugins.birthday.date = _helpers.NewDate

    def test_join_birthday(self):
        lala.util._PM._handle_message("user", "#channel", "!my_birthday_is 10.12.")
        lala.util._PM.on_join("user", "#channel")
        lala.plugins.birthday.msg.assert_called_once_with("#channel",
            "\o\ Happy birthday, user /o/")

    def test_join_not_birthday(self):
        lala.util._PM._handle_message("user", "#channel", "!my_birthday_is 09.12.")
        lala.util._PM.on_join("user", "#channel")
        self.assertFalse(lala.plugins.birthday.msg.called)

    def test_past_birthday(self):
        lala.config._set("birthday", "user", "09.12.2012")
        lala.util._PM.on_join("user", "#channel")
        self.assertEqual(lala.config._get("birthday", "user"), "09.12.2013")

    def test_set_birthday_not_yet(self):
        """Tests setting a birthday that has not already happened this year."""
        lala.util._PM._handle_message("user", "#channel", "!my_birthday_is 11.12.")
        self.assertEqual(lala.config._get("birthday", "user"), "11.12.2012")

    def test_set_birthday_already(self):
        """Tests setting a birthday that has already happened this year."""
        lala.util._PM._handle_message("user", "#channel", "!my_birthday_is 09.12.")
        self.assertEqual(lala.config._get("birthday", "user"), "09.12.2013")

