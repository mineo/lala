"""Helpers to be used with plugins"""
import lala.config as config

from types import FunctionType
from inspect import getargspec

_BOT = None
_PM = None

class command(object):
    """Decorator to register a command. The name of the command is the
       `__name__` attribute of the decorated function.
       Example::

           @command
           def heyiamacommand(user, channel, text):
               pass

       You can also pass a ``command`` parameter to overwrite the name of the
       command::

           @command("yetanothercommand")
           def command_with_a_really_stupid_or_insanely_long_name(user,
           channel, text):
               pass

    """
    def __init__(self, command=None):
        """docstring for __init__"""
        if isinstance(command, FunctionType):
            if _check_args(command):
                _PM.register_callback(command.__name__, command)
            else:
                raise TypeError(
                    "A callback function should take exactly 3 arguments")
        elif not (isinstance(command, str) or isinstance(command, unicode)):
            raise TypeError("The command should be either a str or unicode")
        else:
            self.cmd = command

    def __call__(self, func):
        _PM.register_callback(self.cmd, func)

def on_join(f):
    """Decorator for functions reacting to joins

    :param f: The function which should be called on joins."""
    _PM.register_join_callback(f)

class regex(object):
    """Decorator to register a regex. Example::

           regexp = re.compile("(https?://.+)\s?")
           @regex(regexp)
           def somefunc(user, channel, text, match_obj):
               pass

       ``match_obj`` is a :py:class:`re.MatchObject`.

       :param regex: A :py:class:`re.RegexObject`
    """
    def __init__(self, regex):
        """docstring for __init__"""
        self.re = regex

    def __call__(self, func):
        """docstring for __call__"""
        if _check_args(func):
            _PM.register_regex(self.re, func)
        else:
            raise TypeError(
                "A callback function should take exactly 3 arguments")

def initplz(f):
    """ Call ``f`` once. This can be used to set values of global variables or
    some other setup stuff."""
    if callable(f):
        f()
    else:
        raise TypeError("Expected a callable object")

def is_admin(user):
    """Check whether ``user`` is an admin"""
    return user in config._get("base", "admins")

def msg(target, message, log=True):
    """Send a message to a target.

    :param message: One or more messages to send
    :param log: Whether or not to log the message
    """
    try:
        if not isinstance(message, basestring):
            for _message in iter(message):
                if _message == u"":
                    continue
                message = _message.encode("utf-8")
                _BOT.msg(target, _message, log)
        else:
            _BOT.msg(target, message.encode("utf-8"), log)
    except TypeError:
        if message == u"":
            return
        _BOT.msg(target, message.encode("utf-8"), log)

def _check_args(f, count=3):
    args, varargs, varkw, defaults = getargspec(f)
    if defaults:
        args = args[:-defaults]
    return len(args) == count
