#!/usr/bin/python2
# coding: utf-8
import lurklib
import glob
import sys
import logging
import logging.handlers
import os

from os.path import basename
from lala import util


class Plugger(object):
    def __init__(self, bot, path):
        self.bot = bot
        if not path in sys.path:
            sys.path.append(os.path.join(os.path.dirname(__file__),path))
        self.path = path

    def load_plugins(self):
        for plugin in glob.glob("%s/*.py" % self.path):
            logging.debug("Loading %s" % plugin)
            self.load_plugin(basename(plugin), py=True)

    def load_plugin(self, name, py=False):
        # Is there ".py in name?
        if not py:
            name = name + ".py"

        logging.debug("Trying to load %s" % name)
        plug = __import__(name[:-3])


class Bot(lurklib.Client):
    def __init__(self,
                server,
                port=None,
                nick='lalal',
                user='lalala',
                real_name='lalilu',
                password=None,
                tls=False,
                tls_verify=False,
                encoding='utf-8',
                fallback_encoding='utf-8',
                hide_called_events=True,
                UTC=False,
                channels=[],
                version="lala 0.1.4",
                debug=True,
                plugins=[],
                nickserv=None
                ):
        """ Create a new :py:class:`lala.Bot` instance

        :param server: Server to connect to
        :param port: Server port
        :param nick: The Bots nick
        :param user: User to specify in the *USER* message
        :param real_name: Real name
        :param password: Server password
        :param tls: Whether or not to use TLS
        :param tls_verify: Whether or not to verify the TLS certificate
        :param encoding: Encoding to use
        :param channels: List of channels to join after connecting
        :param version: Version of the bot. Will be used in *CTCP VERSION*
        replies
        :param plugins: List of plugins to load
        """

        self._logger = logging.getLogger("MessageLog")

        debugformat=\
            "%(levelname)s %(filename)s: %(funcName)s:%(lineno)d %(message)s"
        if debug:
            logging.basicConfig(format=debugformat, level=logging.DEBUG)

        self._channels = channels
        self._callbacks = {}
        self._join_callbacks = list()
        self._regexes = {}
        self._cbprefix = "!"
        self.__version__ = version
        self._nickserv_password = nickserv
        self.plugger = Plugger(self, "plugins")

        lurklib.Client.__init__(self,
                server = server,
                port = port,
                nick = nick,
                real_name = real_name,
                password = password,
                tls = tls,
                tls_verify = tls_verify,
                encoding = encoding,
                hide_called_events = hide_called_events,
                UTC = UTC
                )
        self.fallback_encoding = fallback_encoding
        util._BOT = self
        for plugin in plugins:
            self.plugger.load_plugin(plugin)
        self.plugger.load_plugin("base")

    def on_connect(self):
        for channel in self._channels:
            self.join_(channel)

        if self._nickserv_password:
            logging.debug("Identifying with %s" % self._nickserv_password)
            self.privmsg("NickServ", "identify %s" % self._nickserv_password,
                    log=False)

    def on_privmsg(self, event):
        user = event[0][0]
        text = event[2]
        if event[1] == self.current_nick:
            channel = user
        else:
            channel = event[1]
        self._logger.info("%s: %s" % (user, text))
        try:
            if text.startswith(self._cbprefix):
                command = text.split()[0].replace(self._cbprefix, "")
                if command in self._callbacks:
                    self._callbacks[command](
                        user,
                        channel,  # channel
                        text)

            for regex in self._regexes:
                match = regex.search(text)
                if match is not None:
                    self._regexes[regex](
                            user,
                            channel,
                            text,
                            match)
        except (lurklib.exceptions._Exceptions.NotInChannel,
                lurklib.exceptions._Exceptions.NotOnChannel):
            # Some plugin tried to send to a channel it's not in
            # This should not happen, but anyway:
            pass
        # Catch TypeError: some command parameter was not correct
        # TODO Find a way to tell people about wrong parameters
        except TypeError, e:
            pass

    def on_notice(self, event):
        user = event[0][0]
        text = event[2]
        self._logger.info("NOTICE from %s: %s" % (user, text))

    def on_join(self, event):
        self._logger.info("%s joined" % event[0][0])
        for cb in self._join_callbacks:
            cb(event)

    def on_ctcp(self, event):
        if event[2] == "VERSION":
            logging.debug("VERSION request from %s" % event[0][0])
            self.notice(event[0][0],
                        self.ctcp_encode("VERSION %s" % self.__version__))

    def on_part(self, event):
        user = event[0][0]
        channel = event[1]
        reason = event[2]
        self._logger.info("%s parted: %s" % (user, reason))

    def on_quit(self, event):
        user = event[0][0]
        reason = event[1]
        self._logger.info("%s left: %s" % (user, reason))

    def register_callback(self, trigger, func):
        """ Adds func to the callbacks for trigger """
        logging.debug("Registering callback for %s" % trigger)
        self._callbacks[trigger] = func

    def register_join_callback(self, func):
        self._join_callbacks.append(func)

    def register_regex(self, regex, func):
        self._regexes[regex] = func

    def privmsg(self, target, message, log=True):
        if log:
            self._logger.info("%s: %s" % (self.current_nick, message))
        lurklib.Client.privmsg(self, target, message)

    def _handle_quit(self, sig, frame):
        self.quit("Somebody pushed the big red button!")

    def mainloop(self):
        try:
            lurklib.Client.mainloop(self)
        except lurklib.exceptions._Exceptions.IRCError, e:
            logging.warning(e)
            self.on_connect = None
            self.mainloop()

if __name__ == '__main__':
    bot = Bot()
    bot.mainloop()
