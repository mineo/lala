#!/usr/bin/python2
# coding: utf-8
import lurklib
import glob
import sys
import exceptions as exc
import logging

from os.path import basename
from os import listdir

class Plugger(object):
    def __init__(self, bot, path):
        self.bot = bot
        if not path in sys.path:
            sys.path.append(path)
        self.path = path

    def load_plugins(self):
        for plugin in glob.glob("%s/*.py" % self.path):
            logging.debug("Loading %s" % plugin)
            self.load_plugin(basename(plugin), py=True)

    def load_plugin(self, name, py=False):
        # Is there ".py in name?
        if not py:
            name = name + ".py"

        if name in listdir(self.path):
            plug = __import__(name[:-3])
            plug.Plugin(self.bot)
        else:
            raise exc.NoSuchPlugin("No %s.py found in sys.path" % name)

class Bot(lurklib.Client):
    def __init__(self,
                server,
                admin,
                port=None,
                nick='Lurklib',
                user='Lurklib',
                real_name='The Lurk Internet Relay Chat Library',
                password=None,
                tls=False,
                tls_verify=False,
                encoding='UTF-8',
                hide_called_events=True,
                UTC=False,
                channel="#reisplanet",
                version="lala 0.1",
                logformat="%(filename)s: %(funcName)s:%(lineno)d %(message)s"
                ):

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

        logging.basicConfig(format=logformat, level=logging.DEBUG)
        self._admins = [admin]
        self._identified = []
        self._channel = channel
        self._callbacks = {}
        self._regexes = {}
        self._cbprefix = "!"
        self.__version__ = version
        self.plugger = Plugger(self, "plugins")
        self.plugger.load_plugins()

    def on_connect(self):
        self.join(self._channel)

    def on_privmsg(self, event):
        user = event[0][0]
        text = event[2]
        logging.info("%s: %s" % (user, text))
        command = text.split()[0].replace(self._cbprefix, "")
        try:
            if self._callbacks.has_key(command):
                self._callbacks[command](
                    self, #bot
                    user,
                    event[1], #channel
                    text)

            for regex in self._regexes:
                match = regex.search(text)
                if match is not None:
                    self._regexes[regex](
                            self,
                            user,
                            event[1], #channel
                            text,
                            match)
        except (lurklib.exceptions._Exceptions.NotInChannel,
                lurklib.exceptions._Exceptions.NotOnChannel):
            # Some plugin tried to send to a channel it's not in
            # This should not happen, but anyway:
            pass

    def on_ctcp(self, event):
        if event[2] == "VERSION":
            logging.debug("VERSION request from %s" % event[0][0])
            self.notice(event[0][0], 
                        self.ctcp_encode("VERSION %s" % self.__version__))


    def register_callback(self, trigger, func):
        """ Adds func to the callbacks for trigger """
        logging.debug("Registering callback for %s" % trigger)
        self._callbacks[trigger] = func

    def register_regex(self, regex, func):
        self._regexes[regex] = func

if __name__ == '__main__':
    bot = Bot()
    bot.mainloop()
