import imp
import logging
import lala.config
import lala.util


__all__ = ["disable", "enable", "is_admin", "PluginFunc", "load_plugin"]


_callbacks = {}
_join_callbacks = list()
_regexes = {}
_cbprefix = "!"


class PluginFunc(object):
    def __init__(self, func, enabled=True, admin_only=False, aliases=None):
        self.enabled = enabled
        self.func = func
        self.admin_only = admin_only
        self.aliases = aliases or []


def _make_pluginfunc(func, admin_only=False, aliases=None):
    if aliases is not None:
        extradoc = "Aliases: %s" % (", ".join(aliases))
        doc = func.__doc__
        if doc is None:
            func.__doc__ = extradoc
        else:
            func.__doc__ += "\n"
            func.__doc__ += extradoc
    return PluginFunc(func,admin_only=admin_only, aliases=aliases)


def is_admin(user):
    """Check whether ``user`` is an admin.

    If a nickserv password is set, this will work by checking an internal
    list of identified admins.

    If no nickserv password is set, this simply checks if ``user`` is in
    the "admins" option of the "base" section."""
    if lala.util._BOT.factory.nspassword is not None and\
       lala.config._CFG.getboolean("base", "nickserv_admin_tracking"):
        return user in lala.util._BOT.identified_admins
    else:
        return user in lala.config._get("base",
                                        "admins").split(lala.config._LIST_SEPARATOR)


def load_plugin(name):
    logging.debug("Trying to load %s" % name)
    if not lala.config._CFG.has_section(name):
        lala.config._CFG.add_section(name)
    name = "lala/plugins/%s" % name
    (f, p, d) = imp.find_module(name)
    imp.load_module(name, f, p, d)


def register_callback(trigger, func, admin_only=False, aliases=None):
    """ Adds ``func`` to the callbacks for ``trigger``."""
    logging.debug("Registering callback for %s" % trigger)
    f = _make_pluginfunc(func, admin_only, aliases)
    if aliases is not None:
        for alias in aliases:
            _callbacks[alias] = f
    _callbacks[trigger] = f


def register_join_callback(func):
    """ Registers ``func`` as a callback for join events."""
    _join_callbacks.append(func)


def register_regex(regex, func):
    """ Registers ``func`` as a callback for every message that matches
    ``regex``."""
    _regexes[regex] = _make_pluginfunc(func)


def _handle_message(user, channel, message):
    if message.startswith(_cbprefix):
        command = message.split()[0].replace(_cbprefix, "")
        func = _callbacks.get(command)
        if func is not None:
            logging.debug(func)
            if func.enabled:
                if ((func.admin_only and is_admin(user))
                        or not func.admin_only):
                    _callbacks[command].func(
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

    for regex in _regexes:
        match = regex.search(message)
        if match is not None:
            func = _regexes[regex]
            if func.enabled:
                logging.info("%s matched %s" % (message, regex))
                _regexes[regex].func(
                        user,
                        channel,
                        message,
                        match)
            else:
                logging.info("%s is not enabled" % regex.pattern)


def on_join(user, channel):
    """ Calls all callbacks for on_join events that were previously
    registered with :meth:`lala.util.on_join`.
    """
    for cb in _join_callbacks:
        cb(user, channel)


def disable(trigger):
    """Disables `trigger`.

    :param str trigger: The trigger to disable. Can be a key for a callback or a
    regular expression
    """
    if trigger in _callbacks:
        _callbacks[trigger].enabled = False

    for regex in _regexes:
        if regex.pattern == trigger:
            _regexes[regex].enabled = False
            break


def enable(trigger):
    """Enables `trigger`.

    :param str trigger: The trigger to enable. Can be a key for a callback or a
    regular expression

    """
    if trigger in _callbacks:
        _callbacks[trigger].enabled = True

    for regex in _regexes:
        if regex.pattern == trigger:
            _regexes[regex].enabled = True


def _get_enabled_plugins():
    """Returns a list of all the enabled plugins.
    """
    return lala.config._get("base",
                            "plugins").split(lala.config._LIST_SEPARATOR)


def _reload():
    """Reloads all enabled plugins.
    """
    logging.debug("Reloading plugins")
    global _join_callbacks
    _join_callbacks = []
    _regexes.clear()
    _callbacks.clear()
    # Call setup to load the modules again.
    # Important: this works because when using imp.load_module to load an
    # already imported module, the second import is equivalent to a reload() of
    # that module.
    setup()


def setup():
    """Loads all enabled plugins
    """
    for plugin in _get_enabled_plugins():
        load_plugin(plugin)
    load_plugin("base")
