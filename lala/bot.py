import logging

from twisted.words.protocols.irc import IRCClient
from lala import util, config, __version__


class Lala(IRCClient):
    versionName = "lala"
    versionNum = __version__
    lineRate = 1

    def _get_nick(self):
        return self.factory.nickname

    nickname = property(_get_nick)

    def signedOn(self):
        logging.debug("Joining %s" % self.factory.channel)
        self.join(self.factory.channel)
        if self.factory.nspassword is not None:
            logging.info("Identifying with Nickserv")
            self.msg("Nickserv", "identify %s" % self.factory.nspassword,
                    log=False)

    def joined(self, channel):
        logging.debug("Successfully joined %s" % channel)

    def userJoined(self, user, channel):
        logging.debug("%s joined %s" % (user, channel))
        util._PM.on_join(user, channel)

    def privmsg(self, user, channel, message):
        user = user.split("!")[0]
        if channel == self.nickname:
            channel = user
        try:
            message = message.decode("utf-8")
        except Exception:
            message = message.decode(config._get("base", "fallback_encoding"))
        self.factory.logger.info("%s: %s" % (user, message))
        util._PM._handle_message(user, channel, message)

    def msg(self, channel, message, log, length=None):
        if log:
            self.factory.logger.info("%s: %s" % (self.nickname, message))
        message = message.rstrip().encode("utf-8")
        IRCClient.msg(self, channel, message, length)
