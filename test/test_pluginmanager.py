import unittest
import mock

from lala import util, pluginmanager
from re import compile

def f(user, channel, text):
    pass

class TestUtil(unittest.TestCase):
    def setUp(self):
        util._PM = pluginmanager.PluginManager("/dev/null")

    def test_on_join(self):
        self.assertEqual(len(util._PM._join_callbacks), 0)
        util.on_join(f)
        self.assertEqual(len(util._PM._join_callbacks), 1)
        self.assertTrue(f in util._PM._join_callbacks)

    def test_command(self):
        self.assertEqual(len(util._PM._callbacks), 0)

        util.command(f)

        self.assertEqual(len(util._PM._callbacks), 1)
        self.assertTrue("f" in util._PM._callbacks)

    def test_named_command(self):
        self.assertEqual(len(util._PM._callbacks), 0)

        c = util.command("command")
        c(f)

        self.assertEqual(len(util._PM._callbacks), 1)
        self.assertTrue("command" in util._PM._callbacks)

    def test_regex(self):
        self.assertEqual(len(util._PM._regexes), 0)

        r = util.regex(".*")
        r(f)

        self.assertEqual(len(util._PM._regexes), 1)
        self.assertTrue(".*" in util._PM._regexes)

    def test_message_called(self):
        mocked_f = mock.Mock(spec=f)
        util._PM.register_callback("test", mocked_f)
        util._PM._handle_message("user", "channel", "!test")
        mocked_f.assert_called_once_with("user", "channel", "!test")

    def test_regex_called(self):
        mocked_f = mock.Mock(spec=f)
        util._PM.register_regex(compile("test"), mocked_f)
        util._PM._handle_message("user", "channel", "regex")
        self.assertFalse(mocked_f.called)
        util._PM._handle_message("user", "channel", "test foobar")
        self.assertTrue(mocked_f.called)
