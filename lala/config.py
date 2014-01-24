"""Config module"""
import logging


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
        if not __file__.startswith(filename):
            return basename(filename.replace(".py", ""))


def _set(section, key, value):
    if _CFG.has_section(section):
        _CFG.set(section, key, value)
    else:
        _CFG.add_section(section)
        _CFG.set(section, key, value)
    if _FILENAME is not None:
        with open(_FILENAME, "wb") as fp:
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
    if not isinstance(value, basestring):
        value = str(value)
    logging.info("%s wants to set the value of %s to %s" % (plugin, key, value))
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


def set_default_options(**kwargs):
    """Sets the default options for a plugin.

    The names of the arguments in ``kwargs`` will be used as the option names,
    the values as the values of the options.
    """
    plugin = _find_current_plugin_name()
    for key, value in kwargs.iteritems():
        if not _CFG.has_option(plugin, key):
            if not isinstance(value, list):
                _set(plugin, key, value)
            else:
                set_list(key, value, plugin)
