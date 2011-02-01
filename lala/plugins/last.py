from lala import plugin
import codecs

from lurklib.exceptions import _Exceptions

MAX_LINES = 30

class Plugin(plugin.baseplugin):
    def __init__(self, bot):
        bot.register_callback("last", self.last)

    def last(self, bot, user, channel, text):
        s_text = text.split()
        try:
            lines = min(MAX_LINES, int(s_text[1]))
        except IndexError, e:
            lines = MAX_LINES
        with codecs.open(bot._logfile, "r", "utf-8") as _file:
            _lines = _file.readlines()
        lines = min(lines, len(_lines))
        for line in _lines[-lines:]:
            try:
                bot.privmsg(user, line.replace("\n", ""))
            except (_Exceptions.ErrorneusNickname,
                    _Exceptions.NoSuchNick), e:
                # The user left, we shoulnd't try to send further lines
                return
