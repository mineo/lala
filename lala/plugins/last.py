"""
Last Messages
=============

The ``last`` plugin saves the last messages in memory. It provides a ``last``
command to retrieve them.

Options
-------

- ``max_lines``
    The maximum number of lines to message upon the ``last`` command. Defaults
    to 30

- ``datetime_format``
    The format used to format the timestamps in the log. Have a look at the
    `strftime documentation`_ for all possible options. The default is
    ``%Y-%m-%d %H:%M:%S``.

.. _strftime documentation: http://docs.python.org/2/library/datetime.html?highlight=datetime#strftime-strptime-behavior
"""
__all__ = []
import lala.config

from datetime import datetime
from lala.util import command, msg, regex


DEFAULT_OPTIONS = {"max_lines": "30",
                   "datetime_format": "%Y-%m-%d %H:%M:%S"}

_chatlog = None


class _LogEntryBuffer(list):
    """A list with a restricted length."""
    def __init__(self, maxentries):
        """
        :param maxentries: The amount of entries that can be stored in this list
        :type maxentries: Integer
        """
        list.__init__(self)
        self._maxentries = maxentries

    def __add__(self, *args, **kwargs):
        raise NotImplemented

    def __iadd__(self, *args, **kwargs):
        raise NotImplemented

    def append(self, item):
        if len(self) >= self._maxentries:
            self.pop(0)
        list.append(self, item)


@command
def last(user, channel, text):
    """Show the last lines from the log"""
    max_lines = lala.config.get_int("max_lines")
    s_text = text.split()
    try:
        num_lines = min(max_lines, int(s_text[0]))
    except IndexError:
        num_lines = max_lines
    num_lines = min(num_lines, len(_chatlog))
    msg(user, _chatlog[-num_lines:], log=False)


@regex(".*")
def chatlog(user, channel, text, match_obj):
    now = datetime.now().strftime(lala.config.get("datetime_format"))
    _chatlog.append("[%s] %s: %s" % (now, user, text))


def init():
    global _chatlog
    _chatlog = _LogEntryBuffer(lala.config.get_int("max_lines"))
