"""Config module"""
import logging
import ConfigParser

from inspect import getframeinfo, stack
from os.path import basename

_CFG = None
_FILENAME = None


def get(key, default=None):
    """Returns the value of a config option.
    The section is the name of the calling file.

    If ``key`` does not exist and ``default`` is passed, the default value will
    be saved for later calls and returned.

    :param key: The key to lookup
    :param default: Default value to return in case ``key`` does not exist"""
    plugin = basename(getframeinfo(stack()[1][0]).filename.replace(".py", ""))
    logging.debug("%s wants to get the value of %s" % (plugin, key))
    try:
        return _CFG.get(plugin, key)
    except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
        logging.info("%s is missing in config section '%s'" % (key, plugin))
        if default is not None:
            logging.info("Using %s" % default)
            _set(plugin, key, str(default))
            return default
        else:
            raise


_get = lambda section, key: _CFG.get(section, key)


def set(key, value):
    """Sets the ``value`` of ``key``.
    The section is the name of the calling file."""
    plugin = basename(getframeinfo(stack()[1][0]).filename.replace(".py", ""))
    logging.debug("%s wants to set the value of %s to %s" % (plugin, key, value))
    _set(plugin, key, value)


def _set(section, key, value):
    if _CFG.has_section(section):
        _CFG.set(section, key, value)
    else:
        _CFG.add_section(section)
        _CFG.set(section, key, value)
    with open(_FILENAME, "wb") as fp:
        _CFG.write(fp)
