try:
    # Python < 2.7
    import unittest2 as unittest
except ImportError:
    import unittest
import lala.factory
import lala.util
import lala.pluginmanager
import lala.config
import mock

from twisted.test import proto_helpers


class TestBot(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch("lala.pluginmanager")
        patcher.start()
        self.addCleanup(patcher.stop)

        self.factory = lala.factory.LalaFactory("#test", "nick")
        self.proto = self.factory.buildProtocol(("127.0.0.1", ))
        self.tr = proto_helpers.StringTransport()
        self.proto.makeConnection(self.tr)

    def test_bot_calls_pm_on_join(self):
        self.proto.userJoined("user", "channel")
        lala.pluginmanager.on_join.assert_called_once_with("user", "channel")

    def test_bot_calls_pm_on_privmsg(self):
        self.proto.privmsg("user", "channel", "message")
        lala.pluginmanager._handle_message.assert_called_once_with("user",
                "channel", "message")

    @mock.patch('lala.config._CFG')
    def test_bot_joins_channel_on_signon(self, mock):
        self.proto.join = mock.Mock()
        self.proto.signedOn()
        self.proto.join.assert_called_once_with("#test")

    def test_factory(self):
        lala.factory.LalaFactory("#test", "nick")

    def test_nick(self):
        self.assertEqual(self.proto.nickname, "nick")

    @mock.patch('lala.config._CFG')
    def test_nickserv(self, mock):
        self.factory.nspassword = "test"
        self.proto.msg = mock.Mock()
        self.proto.signedOn()
        self.proto.msg.assert_called_once_with("Nickserv", "identify test",
                log=False)
