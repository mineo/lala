import unittest
import lala.factory, lala.util, lala.pluginmanager, lala.config
import mock

from twisted.test import proto_helpers

class TestBot(unittest.TestCase):
    def setUp(self):
        self._old_pm = lala.pluginmanager.PluginManager
        lala.pluginmanager.PluginManager = mock.Mock(spec=lala.pluginmanager.PluginManager)

        self.factory = lala.factory.LalaFactory("#test", "nick", [], mock.Mock())
        self.proto = self.factory.buildProtocol(("127.0.0.1", ))
        self.tr = proto_helpers.StringTransport()
        self.proto.makeConnection(self.tr)

    def test_bot_calls_pm_on_join(self):
        self.proto.userJoined("user", "channel")
        lala.util._PM.on_join.assert_called_once_with("user", "channel")

    def test_bot_calls_pm_on_privmsg(self):
        self.proto.privmsg("user", "channel", "message")
        lala.util._PM._handle_message.assert_called_once_with("user",
                "channel", "message")

    def test_bot_joins_channel_on_signon(self):
        self.proto.join = mock.Mock()
        self.proto.signedOn()
        self.proto.join.assert_called_once_with("#test")

    def test_factory(self):
        lala.factory.LalaFactory("#test", "nick", ["testplugin"], mock.Mock())
        self.assertTrue(("base", ) in lala.util._PM.load_plugin.call_args)
        self.assertTrue((("testplugin", ), {}) in
                lala.util._PM.load_plugin.call_args_list)

    def test_nick(self):
        self.assertEqual(self.proto.nickname, "nick")

    def tearDown(self):
        lala.pluginmanager.PluginManager = self._old_pm
