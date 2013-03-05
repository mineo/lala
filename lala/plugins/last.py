import lala.config

from lala.util import command, msg, regex


lala.config.set_default_options(max_lines="30")


class _LogEntryBuffer(list):
    """A list with a restricted length."""
    def __init__(self, maxentries=None):
        """
        :param maxentries: The amount of entries that can be stored in this list
        :type maxentries: Integer or None
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

_chatlog = _LogEntryBuffer(lala.config.get_int("max_lines"))


@command
def last(user, channel, text):
    """Show the last lines from the log"""
    max_lines = lala.config.get_int("max_lines")
    s_text = text.split()
    try:
        num_lines = min(max_lines, int(s_text[1]))
    except IndexError:
        num_lines = max_lines
    num_lines = min(num_lines, len(_chatlog))
    msg(user, _chatlog[-num_lines:], log=False)


@regex(".*")
def chatlog(user, channel, text, match_obj):
    _chatlog.append("%s: %s" % (user, text))
