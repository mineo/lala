import lala.pluginmanager

from twisted.internet import protocol
from lala.bot import Lala
from lala import util, config


class LalaFactory(protocol.ReconnectingClientFactory):
    protocol = Lala

    def __init__(self, channel, nickname):
        self.channel = channel
        self.nickname = nickname
        try:
            self.nspassword = config._get("base", "nickserv_password")
        except Exception:
            self.nspassword = None
        lala.pluginmanager.setup()

    def buildProtocol(self, addr):
        prot = protocol.ReconnectingClientFactory.buildProtocol(self, addr)
        util._BOT = prot
        return prot
