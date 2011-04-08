"""Helpers to be used with plugins"""
import logging
import lala.config as config


_BOT = None

class command(object):
    """Decorator to register a command"""
    def __init__(self, command):
        """docstring for __init__"""
        self.cmd = command

    def __call__(self, func):
        _BOT.register_callback(self.cmd, func)

def on_join(f):
    """Decorator for functions reacting to joins"""
    _BOT.register_join_callback(f)

class regex(object):
    """Decorator to register a regex"""
    def __init__(self, regex):
        """docstring for __init__"""
        self.re = regex

    def __call__(self, func):
        """docstring for __call__"""
        _BOT.register_regex(self.re, func)

def initplz(f):
    f()

def is_admin(user):
    """docstring for is_admin"""
    return user in config._get("base", "admins")

def msg(target, message, log=True):
    """Send a message to a target"""
    _BOT.privmsg(target, message, log)
