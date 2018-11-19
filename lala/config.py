"""
Config module

.. versionchanged:: 0.5
The function set_default_options was removed. To achieve the same behaviour,
set a module-level dict called "DEFAULT_OPTIONS" where the keys are the
option names and the values are the default values in your plugin.
"""
import logging


from appdirs import user_config_dir
from inspect import getframeinfo, stack
from os import getenv
from os.path import basename, expanduser, join
from six import iteritems, string_types
from six.moves import configparser

_CFG = None
_FILENAME = None

#: Used as a separator when storing lists of values in the config file
_LIST_SEPARATOR = ","

#: Default settings
_CONFIG_DEFAULTS = {
    "channels": "",
    "plugins": "",
    "nickserv_password": None,
    "log_folder": expanduser("~/.lala/logs"),
    "log_file": expanduser("~/.lala/lala.log"),
    "encoding": "utf-8",
    "fallback_encoding": "utf-8",
    "max_log_days": 2,
    "nickserv_admin_tracking": "false"
}


def _initialize(filename=None):
    global _CFG
    global _FILENAME
    cfg = configparser.RawConfigParser(_CONFIG_DEFAULTS)
    if filename is None:
        configfiles = [join(user_config_dir(appname="lala"),
                            "config"),
                       join(getenv("HOME"), ".lala", "config"),
                       "/etc/lala/config"]
    else:
        configfiles = [filename]
    files = cfg.read(configfiles)
    cfg.add_section("base")

    logging.info("Read config files %s", files)
    logging.info("Using %s to save setting", files[0])

    _CFG = cfg
    _FILENAME = files[0]


def _find_current_plugin_name():
    """Tries to find the filename of the current plugin. This is essentially
    the first filename different from the filename of this file ("config.py")
    on the stack
    """
    for elem in stack():
        frameinfo = getframeinfo(elem[0])
        filename = frameinfo.filename
        if not __file__.startswith(filename):
            return basename(filename.replace(".py", ""))


def _set(section, key, value):
    if _CFG.has_section(section):
        _CFG.set(section, key, value)
    else:
        _CFG.add_section(section)
        _CFG.set(section, key, value)
    if _FILENAME is not None:
        with open(_FILENAME, "w") as fp:
            _CFG.write(fp)


def get(key, converter=None):
    """Returns the value of a config option.
    The section is the name of the calling file.

    Default values for all keys can be set with :meth:`set_default_options`.

    :param key: The key to lookup
    """
    plugin = _find_current_plugin_name()
    logging.info("%s wants to get the value of %s" % (plugin, key))
    value = None
    value = _CFG.get(plugin, key)
    if converter is not None:
        value = converter(value)
    return value


def _get(section, key):
    return _CFG.get(section, key)


def get_int(*args):
    """Returns the value of a config option as an int.

    :param *args: See :meth:`lala.config.get`
    :rtype: int
    """
    return get(*args, converter=int)


def set(key, value, plugin=None):
    """Sets the ``value`` of ``key``.
    The section is the name of the calling file."""
    plugin = _find_current_plugin_name()
    if not isinstance(value, string_types):
        value = str(value)
    logging.info("%s wants to set the value of %s to %s" % (plugin, key, value))
    _set(plugin, key, value)


def _list_converter(value):
    """Converts a list of values into a string in which the values will be
    separated by :data:`_LIST_SEPARATOR`."""
    if not isinstance(value, string_types):
        value = map(str, value)
        value = _LIST_SEPARATOR.join(value)
    return value


def get_list(*args):
    """Gets a list option.

    :param *args: See :meth:`lala.config.get`
    :rtype: list of strings
    """
    value = get(*args, converter=_list_converter)
    return value.split(_LIST_SEPARATOR)


def set_list(key, value, *args):
    """Sets option ``key`` to ``value`` where ``value`` is a list of values.

    None of the values in ``value`` are allowed to contain
    :data:`lala.config._LIST_SEPARATOR`.

    This method does *not* preserve the type of the items in the list, they're
    all passed through :meth:`str`.

    :param key: See :meth:`lala.config.set`
    :param value: A list of values for ``key``.
    """
    value = _list_converter(value)
    set(key, value, *args)


def _set_default_options(plugin, opts):
    """Sets the default options for a plugin.

    The names of the arguments in ``kwargs`` will be used as the option names,
    the values as the values of the options.
    """
    for key, value in iteritems(opts):
        if not _CFG.has_option(plugin, key):
            if not isinstance(value, list):
                _set(plugin, key, value)
            else:
                set_list(key, value, plugin)
