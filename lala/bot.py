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
        """ Called after a connection to the server has been established.

        Joins all configured channels and identifies with Nickserv."""
        logging.debug("Joining %s" % self.factory.channel)
        self.join(self.factory.channel)
        if self.factory.nspassword is not None:
            logging.info("Identifying with Nickserv")
            self.msg("Nickserv", "identify %s" % self.factory.nspassword,
                    log=False)

    def joined(self, channel):
        """ Called after joining a channel."""
        logging.debug("Successfully joined %s" % channel)

    def userJoined(self, user, channel):
        """ Handles join events."""
        logging.debug("%s joined %s" % (user, channel))
        util._PM.on_join(user, channel)

    def privmsg(self, user, channel, message):
        """ Handles received messages."""
        user = user.split("!")[0]
        if channel == self.nickname:
            # This is true if the bot was queried
            channel = user
        try:
            message = message.decode("utf-8")
        except Exception:
            message = message.decode(config._get("base", "fallback_encoding"))
        logging.debug("%s: %s" % (user, message))
        util._PM._handle_message(user, channel, message)

    def msg(self, channel, message, log, length=None):
        """ Sends ``message`` to ``channel``.

        Depending on ``log``, the message will be logged or not.

        Do not use this method from plugins, use :meth:`lala.util.msg` instead."""
        if log:
            logging.info("%s: %s" % (self.nickname, message))
        message = message.rstrip().encode("utf-8")
        IRCClient.msg(self, channel, message, length)

    def action(self, user, channel, data):
        """ Called when a user performs an ACTION on a channel."""
        user = user.split("!")[0]
        logging.info("ACTION: %s %s" % (user, data))

    def noticed(self, user, channel, message):
        """ Same as :py:meth:`lala.bot.Lala.privmsg` for NOTICEs."""
        user = user.split("!")[0]
        try:
            message = message.decode("utf-8")
        except Exception:
            message = message.decode(config._get("base", "fallback_encoding"))
        logging.info("NOTICE: %s: %s" % (user, message))
