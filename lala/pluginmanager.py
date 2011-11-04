import sys
import logging
import os

class PluginManager(object):
    def __init__(self, path):
        if not path in sys.path:
            sys.path.append(os.path.join(os.path.dirname(__file__),path))
        self.path = path
        self._callbacks = {}
        self._join_callbacks = list()
        self._regexes = {}
        self._cbprefix = "!"

    def load_plugin(self, name):
        logging.debug("Trying to load %s" % name)
        __import__(os.path.splitext(name)[0])

    def register_callback(self, trigger, func):
        """ Adds func to the callbacks for trigger """
        logging.debug("Registering callback for %s" % trigger)
        self._callbacks[trigger] = func

    def register_join_callback(self, func):
        self._join_callbacks.append(func)

    def register_regex(self, regex, func):
        self._regexes[regex] = func

    def _handle_message(self, user, channel, message):
        if message.startswith(self._cbprefix):
            command = message.split()[0].replace(self._cbprefix, "")
            if command in self._callbacks:
                self._callbacks[command](
                    user,
                    channel,
                    message)

        for regex in self._regexes:
            match = regex.search(message)
            if match is not None:
                self._regexes[regex](
                        user,
                        channel,
                        message,
                        match)

    def on_join(self, user, channel):
        for cb in self._join_callbacks:
            cb(user, channel)
