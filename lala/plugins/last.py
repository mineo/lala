import codecs

from lurklib.exceptions import _Exceptions
from lala.util import _BOT, command, msg

MAX_LINES = 30

@command("last")
def last(user, channel, text):
    s_text = text.split()
    try:
        lines = min(MAX_LINES, int(s_text[1]))
    except IndexError, e:
        lines = MAX_LINES
    with codecs.open(_BOT._logfile, "r", "utf-8") as _file:
        _lines = _file.readlines()
    lines = min(lines, len(_lines))
    for line in _lines[-lines:]:
        try:
            msg(user, line.replace("\n", ""))
        except (_Exceptions.ErrorneusNickname,
                _Exceptions.NoSuchNick), e:
            # The user left, we shoulnd't try to send further lines
            return
