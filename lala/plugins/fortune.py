import logging

from functools import partial
from lala.util import command, msg
from twisted.internet.utils import getProcessOutput

@command
def fortune(user, channel, text):
    """Show a random, hopefully interesting, adage"""
    _call_fortune(user, channel)

@command
def ofortune(user, channel, text):
    """Show a random, hopefully interesting, offensive adage"""
    _call_fortune(user, channel, ["-o"])

def _call_fortune(user, channel, args=[]):
    """Call the ``fortune`` executable with ``args`` (a sequence of strings).
    """
    callback = partial(_send_output_to_channel, user, channel)
    errback = partial(_send_error_to_channel, user, channel)
    deferred = getProcessOutput("fortune", args)
    deferred.addCallback(callback)
    deferred.addErrback(errback)
    deferred.addErrback(logging.error)

def _send_output_to_channel(user, channel, text):
    msg(channel, "%s: %s" %(user, text.replace("\n"," ")))

def _send_error_to_channel(user, channel, exception):
    msg(channel, "%s: Sorry, no fortune for you today! Details are in the log." % user)
    return exception
