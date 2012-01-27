import unittest
import lala.factory, lala.util, lala.pluginmanager
import mock

from twisted.test import proto_helpers

class TestBot(unittest.TestCase):
    def setUp(self):
        self._old_pm = lala.pluginmanager.PluginManager
        lala.pluginmanager.PluginManager = mock.Mock(spec=lala.pluginmanager.PluginManager)

        factory = lala.factory.LalaFactory("#test", "nick", [], mock.Mock())
        self.proto = factory.buildProtocol(("127.0.0.1", ))
        self.tr = proto_helpers.StringTransport()
        self.proto.makeConnection(self.tr)

    def test_pm_is_called(self):
        self.proto.privmsg("user", "channel", "message")
        lala.util._PM._handle_message.assert_called_once_with("user",
                "channel", "message")

    def test_factory(self):
        lala.factory.LalaFactory("#test", "nick", ["testplugin"], mock.Mock())
        self.assertTrue(("base", ) in lala.util._PM.load_plugin.call_args)
        self.assertTrue((("testplugin", ), {}) in
                lala.util._PM.load_plugin.call_args_list)

    def test_nick(self):
        self.assertEqual(self.proto.nickname, "nick")

    def tearDown(self):
        lala.pluginmanager.PluginManager = self._old_pm
