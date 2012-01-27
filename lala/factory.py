from twisted.internet import protocol
from lala.bot import Lala
from lala import pluginmanager, util, config


class LalaFactory(protocol.ReconnectingClientFactory):
    protocol = Lala

    def __init__(self, channel, nickname, plugins, logger):
        self.channel = channel
        self.nickname = nickname
        self.logger = logger
        util._PM = pluginmanager.PluginManager("plugins")
        try:
            self.nspassword = config._get("base", "nickserv_password")
        except Exception:
            self.nspassword = None
        for plugin in plugins:
            util._PM.load_plugin(plugin)
        util._PM.load_plugin("base")

    def buildProtocol(self, addr):
        prot = protocol.ReconnectingClientFactory.buildProtocol(self, addr)
        util._BOT = prot
        return prot
