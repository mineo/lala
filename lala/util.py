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

def initplz(f):
    f()

def is_admin(user):
    if user in _BOT._admins:
        logging.debug("%s is an admin" % user)
        return True
    else:
        logging.debug("%s is not an admin" % user)
        return False

def msg(target, message):
    """Send a message to a target"""
    _BOT.privmsg(target, message)
