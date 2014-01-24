"""Helpers to be used with plugins"""
import lala.pluginmanager


from types import FunctionType
from inspect import getargspec
from re import compile


_BOT = None


class command(object):
    """ Decorator to register a command. The name of the command is the
        `__name__` attribute of the decorated function.
        Example::

            @command
            def heyiamacommand(user, channel, text):
                pass

        You can also pass a ``command`` parameter to overwrite the name of the
        command::

            @command(command="yetanothercommand")
            def command_with_a_really_stupid_or_insanely_long_name(user,
            channel, text):
                pass


        An additional argument, ``admin_only`` can be used to make a function
        available to admins only::

            @command(admin_only=True)
            def give_me_the_one_ring(user, channel, text):
                pass
    """
    def __init__(self, command=None, admin_only=False):
        self.admin_only = admin_only
        if isinstance(command, FunctionType):
            if _check_args(command):
                lala.pluginmanager.register_callback(command.__name__, command,
                                                     self.admin_only)
            else:
                raise TypeError(
                    "A callback function should take exactly 3 arguments")
        elif command is None:
            # This happens when only admin_only is set when decorating a
            # function like
            # @command(admin_only=True)
            # def foo(user, channel, text):
            #   pass
            self.cmd = None
        elif not (isinstance(command, str) or isinstance(command, unicode)):
            raise TypeError(
                    "The command should be either a str or unicode but it's %s"
                    % type(command))
        else:
            self.cmd = command
            self.admin_only=admin_only

    def __call__(self, func):
        self.cmd = self.cmd or func.__name__
        lala.pluginmanager.register_callback(self.cmd, func, self.admin_only)


def on_join(f):
    """Decorator for functions reacting to joins

    :param f: The function which should be called on joins."""
    if _check_args(f, 2):
        lala.pluginmanager.register_join_callback(f)
    else:
        raise TypeError("A callback function should takes exactly 2 arguments")


class regex(object):
    """Decorator to register a regex. Example::

           @regex("(https?://.+)\s?")
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
            lala.pluginmanager.register_regex(self.re, func)
        else:
            raise TypeError(
                "A regex callback function should take exactly 4 arguments")


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
