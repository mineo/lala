import sys
import logging
import os


class PluginManager(object):
    def __init__(self):
        self._callbacks = {}
        self._join_callbacks = list()
        self._regexes = {}
        self._cbprefix = "!"


    def load_plugin(self, name):
        logging.debug("Trying to load %s" % name)
        name = "lala.plugins.%s" % name
        __import__(name)

    def register_callback(self, trigger, func):
        """ Adds ``func`` to the callbacks for ``trigger``."""
        logging.debug("Registering callback for %s" % trigger)
        self._callbacks[trigger] = func

    def register_join_callback(self, func):
        """ Registers ``func`` as a callback for join events."""
        self._join_callbacks.append(func)

    def register_regex(self, regex, func):
        """ Registers ``func`` as a callback for every message that matches
        ``regex``."""
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
        """ Calls all callbacks for on_join events that were previously
        registered with :meth:`lala.util.on_join`.
        """
        for cb in self._join_callbacks:
            cb(user, channel)
