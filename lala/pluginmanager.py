import logging

from lala.util import msg


def _make_pluginfunc(func):
    return {'enabled': True, 'func': func}


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
        logging.info("Registering callback for %s" % trigger)
        self._callbacks[trigger] = _make_pluginfunc(func)

    def register_join_callback(self, func):
        """ Registers ``func`` as a callback for join events."""
        self._join_callbacks.append(func)

    def register_regex(self, regex, func):
        """ Registers ``func`` as a callback for every message that matches
        ``regex``."""
        self._regexes[regex] = _make_pluginfunc(func)

    def _handle_message(self, user, channel, message):
        if message.startswith(self._cbprefix):
            command = message.split()[0].replace(self._cbprefix, "")
            funcdict = self._callbacks.get(command)
            if funcdict is not None:
                logging.debug(funcdict)
                if funcdict["enabled"]:
                    logging.info("Calling %s with '%s'" % (command, message))
                    self._callbacks[command]["func"](
                        user,
                        channel,
                        message)
                else:
                    msg(channel, "%s is not enabled" % command)
                    logging.info("%s is not enabled" % command)
            return

        for regex in self._regexes:
            match = regex.search(message)
            if match is not None:
                funcdict = self._regexes[regex]
                if funcdict["enabled"]:
                    logging.info("%s matched %s" % (message, regex))
                    self._regexes[regex]["func"](
                            user,
                            channel,
                            message,
                            match)
                else:
                    logging.info("%s is not enabled" % regex.pattern)

    def on_join(self, user, channel):
        """ Calls all callbacks for on_join events that were previously
        registered with :meth:`lala.util.on_join`.
        """
        for cb in self._join_callbacks:
            cb(user, channel)

    def disable(self, trigger):
        """Disables `trigger`.

        :trigger: The trigger to disable. Can be a key for a callback or a
        regular expression
        """
        if trigger in self._callbacks:
            self._callbacks[trigger]["enabled"] = False

        for regex in self._regexes:
            if regex.pattern == trigger:
                self._regexes[regex]["enabled"] = False
                break

    def enable(self, trigger):
        """Enables `trigger`.

        :trigger: The trigger to enable. Can be a key for a callback or a
        regular expression

        """
        if trigger in self._callbacks:
            self._callbacks[trigger]["enabled"] = True

        for regex in self._regexes:
            if regex.pattern == trigger:
                self._regexes[regex]["enabled"] = True
