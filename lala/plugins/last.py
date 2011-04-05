import codecs
import lala.config

from lurklib.exceptions import _Exceptions
from lala.util import _BOT, command, msg

@command("last")
def last(user, channel, text):
    max_lines = lala.config.get("max_lines", default=30)
    s_text = text.split()
    try:
        lines = min(max_lines, int(s_text[1]))
    except IndexError, e:
        lines = max_lines
    # TODO: Fix this, it's ugly
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
