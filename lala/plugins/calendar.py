"""
Calendar
========

This plugin provides one command, ``weeknum``, which simply echoes the current
week number in the channel.

Options
-------

- None
"""
from datetime import date
from lala.util import msg, command


@command
def weeknum(user, channel, text):
    """Echoes the current week number."""
    d = date.today()
    year, weeknum, weekday = d.isocalendar()
    msg(channel, "It's week #%i of the year %i." % (weeknum, year))
