import codecs
import lala.config

from lala.util import command, msg
from os.path import join
from time import sleep

@command
def last(user, channel, text):
    """Show the last lines from the log"""
    max_lines = int(lala.config.get("max_lines", default=30))
    s_text = text.split()
    try:
        lines = min(max_lines, int(s_text[1]))
    except IndexError:
        lines = max_lines
    logfile = join(lala.config._get("base", "log_folder"), "lala.log")
    with codecs.open(logfile, "r", "utf-8") as _file:
        _lines = _file.readlines()
    lines = min(lines, len(_lines))
    for line in _lines[-lines:]:
        msg(user, line.replace("\n", ""), log=False)
        sleep(1)
