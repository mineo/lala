import lala.config
import logging

from functools import partial
from lala.util import command, msg
from twisted.internet.utils import getProcessOutput


lala.config.set_default_options(fortune_path="/usr/bin/fortune",
                                fortune_files="fortunes")


@command
def fortune(user, channel, text):
    """Show a random, hopefully interesting, adage"""
    return _call_fortune(user, channel, _get_fortune_file_from_text(text))


@command
def ofortune(user, channel, text):
    """Show a random, hopefully interesting, offensive adage"""
    return _call_fortune(user, channel, ["-o"] + _get_fortune_file_from_text(text))


def _call_fortune(user, channel, args=[]):
    """Call the ``fortune`` executable with ``args`` (a sequence of strings).
    """
    callback = partial(_send_output_to_channel, user, channel)
    deferred = getProcessOutput(lala.config.get("fortune_path"), args)
    deferred.addCallback(callback)
    return deferred


def _get_fortune_file_from_text(text):
    s_text = text.split()
    if len(s_text) > 0:
        return s_text
    else:
        files = lala.config.get("fortune_files").split(lala.config._LIST_SEPARATOR)
        files = map(str.strip, files)
        return files


def _send_output_to_channel(user, channel, text):
    msg(channel, "%s: %s" % (user, text.replace("\n", " ")))
