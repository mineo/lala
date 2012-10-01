"""Helpers to be used with plugins"""
import lala.config as config

from types import FunctionType
from inspect import getargspec
from re import compile


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
    if _check_args(f, 2):
        _PM.register_join_callback(f)
    else:
        raise TypeError("A callback function should takes exactly 2 arguments")


class regex(object):
    """Decorator to register a regex. Example::

           regexp = re.compile("(https?://.+)\s?")
           @regex(regexp)
           def somefunc(user, channel, text, match_obj):
               pass

       ``match_obj`` is a :py:class:`re.MatchObject`.

       :param regex: A :py:class:`re.RegexObject` or a string representing a
                     regular expression.
    """
    def __init__(self, regex):
        if not hasattr(regex, "match") and isinstance(regex, basestring):
            regex = compile(regex)
        self.re = regex

    def __call__(self, func):
        if _check_args(func, 4):
            _PM.register_regex(self.re, func)
        else:
            raise TypeError(
                "A regex callback function should take exactly 4 arguments")


def is_admin(user):
    """Check whether ``user`` is an admin"""
    return user in config._get("base", "admins")


def msg(target, message, log=True):
    """Send a message to a target.

    :param target: Target to send the message to. Can be a channel or user
    :param message: One or more messages to send
    :param log: Whether or not to log the message
    """
    try:
        if not isinstance(message, basestring):
            for _message in iter(message):
                if _message == "":
                    continue
                _BOT.msg(target, _message, log)
        else:
            if message == "":
                return
            _BOT.msg(target, message, log)
    except TypeError:
        if message == "":
            return
        _BOT.msg(target, message, log)


def _check_args(f, count=3):
    """ Checks whether the number of arguments ``f`` takes equals
    ``count``."""
    args, varargs, varkw, defaults = getargspec(f)
    if defaults:
        args = args[:-defaults]
    return len(args) == count
