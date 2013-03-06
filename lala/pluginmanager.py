import logging
import lala.util

from lala.config import _get, _LIST_SEPARATOR

from lala.config import _get, _list_converter
from lala.util import msg

def _make_pluginfunc(func, admin_only=False):
    return {'enabled': True, 'func': func, 'admin_only': admin_only}


class PluginManager(object):
    def __init__(self):
        self._callbacks = {}
        self._join_callbacks = list()
        self._regexes = {}
        self._cbprefix = "!"

    @staticmethod
    def is_admin(user):
        """Check whether ``user`` is an admin.

        If a nickserv password is set, this will work by checking an internal
        list of identified admins.

        If not nickserv password is set, this simply checks if ``user`` is in
        the "admins" option of the "base" section."""
        if lala.util._BOT.factory.nspassword is not None:
            return user in lala.util._BOT.identified_admins
        else:
            return user in _get("base", "admins").split(_LIST_SEPARATOR)

    def load_plugin(self, name):
        logging.info("Trying to load %s" % name)
        name = "lala.plugins.%s" % name
        __import__(name)

    def register_callback(self, trigger, func, admin_only=False):
        """ Adds ``func`` to the callbacks for ``trigger``."""
        logging.debug("Registering callback for %s" % trigger)
        self._callbacks[trigger] = _make_pluginfunc(func, admin_only)

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
                logging.info("'%s: %s' in %s is a command" % (user, channel, message))
                logging.debug(funcdict)
                if funcdict["enabled"]:
                    if ((funcdict["admin_only"] and self.is_admin(user))
                            or not funcdict["admin_only"]):
                        self._callbacks[command]["func"](
                            user,
                            channel,
                            message)
                    else:
                        lala.util.msg(channel,
                                      "Sorry %s, you're not allowed to do that" % user)
                else:
                    lala.util.msg(channel, "%s is not enabled" % command)
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
