"""Config module"""
import logging
import ConfigParser

from inspect import getframeinfo, stack
from os.path import basename

_CFG = None
_FILENAME = None

#: Used as a separator when storing lists of values in the config file
_LIST_SEPARATOR = ","

def _find_current_plugin_name():
    """Tries to find the filename of the current plugin. This is essentially
    the first filename different from the filename of this file ("config.py")
    on the stack
    """
    for elem in stack():
        frameinfo = getframeinfo(elem[0])
        filename = frameinfo.filename
        if filename != __file__:
            return basename(filename.replace(".py", ""))


def _set(section, key, value):
    if _CFG.has_section(section):
        _CFG.set(section, key, value)
    else:
        _CFG.add_section(section)
        _CFG.set(section, key, value)
    with open(_FILENAME, "wb") as fp:
        _CFG.write(fp)


def get(key, default=None, converter=None, setter=_set):
    """Returns the value of a config option.
    The section is the name of the calling file.

    If ``key`` does not exist and ``default`` is passed, the default value will
    be saved for later calls and returned.

    :param key: The key to lookup
    :param default: Default value to return in case ``key`` does not exist"""
    plugin = _find_current_plugin_name()
    logging.debug("%s wants to get the value of %s" % (plugin, key))
    value = None
    try:
        value = _CFG.get(plugin, key)
    except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
        logging.info("%s is missing in config section '%s'" % (key, plugin))
        if default is not None:
            logging.info("Using %s" % default)
            setter(plugin, key, str(default))
            value = default
        else:
            raise

    if converter is not None:
        value = converter(value)
    return value


_get = lambda section, key: _CFG.get(section, key)


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
    logging.debug("%s wants to set the value of %s to %s" % (plugin, key, value))
    _set(plugin, key, value)


def _list_converter(value):
    """Converts a list of values into a string in which the values will be
    separated by :data:`_LIST_SEPARATOR`."""
    if not isinstance(value, basestring):
        value = map(str, value)
        value = _LIST_SEPARATOR.join(value)
    return value


def get_list(*args):
    """Gets a list option.

    :param *args: See :meth:`lala.config.get`
    :rtype: list of strings
    """
    value = get(*args, converter=_list_converter, setter=set_list)
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
