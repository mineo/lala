"""
Decide
======

This plugin provides one command, ``decide``, which, given a list of options
separated by a slash (``/``) chooses one of them.

Options
-------

- None
"""
from collections import Counter
from random import choice
from lala.util import command, msg

TRIES = 5000


@command
def decide(user, channel, text):
    """Pick one choice in an arbitrary list of choices separated by a slash"""
    s_text = text.split("/")
    msg(channel, "%s: %s" % (user, choice(s_text)))


@command
def decide_real_hard(user, channel, text):
    """Pick one choice in an arbitrary list of choices separated by a slash,
    deluxe version"""
    s_text = text.split("/")
    element, count = Counter(choice(s_text) for i in range(TRIES)).most_common(1)[0]
    msg(channel, "%s: %s has been chosen %i out of %i times" %
        (user, element, count, TRIES))
