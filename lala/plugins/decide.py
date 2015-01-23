"""
Decide
======

This plugin provides one command, ``decide``, which, given a list of options
separated by a slash (``/``) chooses one of them.

Options
-------

- None
"""
from random import choice
from lala.util import command, msg


@command
def decide(user, channel, text):
    """Pick one choice in an arbitrary list of choices separated by a slash"""
    s_text = text.split("/")
    msg(channel, "%s: %s" % (user, choice(s_text)))
