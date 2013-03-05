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
    _call_fortune(user, channel, _get_fortune_file_from_text(text))


@command
def ofortune(user, channel, text):
    """Show a random, hopefully interesting, offensive adage"""
    _call_fortune(user, channel, ["-o"] + _get_fortune_file_from_text(text))


def _call_fortune(user, channel, args=[]):
    """Call the ``fortune`` executable with ``args`` (a sequence of strings).
    """
    callback = partial(_send_output_to_channel, user, channel)
    errback = partial(_send_error_to_channel, user, channel)
    deferred = getProcessOutput(lala.config.get("fortune_path"), args)
    deferred.addCallback(callback)
    deferred.addErrback(errback)
    deferred.addErrback(logging.error)


def _get_fortune_file_from_text(text):
    s_text = text.split()
    if len(s_text) > 1:
        return s_text[1:]
    else:
        files = lala.config.get("fortune_files").split(lala.config._LIST_SEPARATOR)
        files = map(str.strip, files)
        return files


def _send_output_to_channel(user, channel, text):
    msg(channel, "%s: %s" %(user, text.replace("\n"," ")))


def _send_error_to_channel(user, channel, exception):
    msg(channel, "%s: Sorry, no fortune for you today! Details are in the log." % user)
    return exception
