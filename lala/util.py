"""Helpers to be used with plugins"""
import logging


_BOT = None

class command(object):
    """Decorator to register a command"""
    def __init__(self, command):
        """docstring for __init__"""
        self.cmd = command

    def __call__(self, func):
        _BOT.register_callback(self.cmd, func)

class regex(object):
    """Decorator to register a regex"""
    def __init__(self, regex):
        """docstring for __init__"""
        self.re = regex

    def __call__(self, func):
        """docstring for __call"""
        _BOT.register_regex(self.re, func)

def initplz(f):
    f()

def is_admin(user):
    """True if the user is an admin, false otherwise"""
    if user in _BOT._admins:
        logging.debug("%s is an admin" % user)
        return True
    else:
        logging.debug("%s is not an admin" % user)
        return False

def msg(target, message):
    """Send a message to a target"""
    _BOT.privmsg(target, message)
