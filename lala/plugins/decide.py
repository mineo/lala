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

_NO_CHOICE_NECESSARY_TEMPLATE = u"{user}: I don't even have to think about that, it's {choice}"  # noqa
_REAL_HARD_TEMPLATE = u"{user}: {choice} has been chosen {count} out of {tries} times"  # noqa


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

    if len(s_text) == 1:
        msg(channel, _NO_CHOICE_NECESSARY_TEMPLATE.format(user=user,
                                                          choice=s_text[0]))
        return

    first_count = second_count = 0
    while first_count == second_count:
        c = Counter(choice(s_text) for i in range(TRIES)).most_common(2)
        # There might be more elements with the same count, but knowing two of
        # them have the same is enough.
        first_choice, first_count = c[0]
        if len(c) == 2:
            _, second_count = c[1]
        if first_count > second_count:
            msg(channel, _REAL_HARD_TEMPLATE.format(
                user=user, choice=first_choice, count=first_count, tries=TRIES))
