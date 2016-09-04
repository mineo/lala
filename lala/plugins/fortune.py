"""
Fortune
=======

This plugin provides two commands, ``fortune`` and ``ofortune``, both of which
basically call the
`fortune command <https://en.wikipedia.org/wiki/Fortune_(Unix)>`_
and post the result in the channel. In addition, ``ofortune`` supplies the
``-o`` option to ``fortune`` so that only offensive fortunes are chosen.

Options
-------

- ``fortune_files``

  The fortune file(s) to use. Defaults to ``fortunes``. This can be overridden
  when using either ``fortune`` or ``ofortune`` by adding the preferred fortune
  file after the command, like ``!fortune riddles``.

- ``fortune_path``

  The full path to the fortune binary. Defaults to ``/usr/bin/fortune``

"""
import lala.config

from lala.util import command, msg
from twisted.internet.defer import inlineCallbacks
from twisted.internet.utils import getProcessOutput

__all__ = ()


DEFAULT_OPTIONS = {"fortune_path": "/usr/bin/fortune",
                   "fortune_files": "fortunes"}


@command
def fortune(user, channel, text):
    """Show a random, hopefully interesting, adage"""
    return _call_fortune(user, channel, _get_fortune_file_from_text(text))


@command
def ofortune(user, channel, text):
    """Show a random, hopefully interesting, offensive adage"""
    return _call_fortune(user, channel, ["-o"] +
                         _get_fortune_file_from_text(text))


@inlineCallbacks
def _call_fortune(user, channel, args=[]):
    """Call the ``fortune`` executable with ``args`` (a sequence of strings).
    """
    fortune = yield getProcessOutput(lala.config.get("fortune_path"), args)
    _send_output_to_channel(user, channel, fortune)


def _get_fortune_file_from_text(text):
    s_text = text.split()
    if len(s_text) > 0:
        return s_text
    else:
        files = lala.config.get("fortune_files").split(
            lala.config._LIST_SEPARATOR)
        files = map(str.strip, files)
        return files


def _send_output_to_channel(user, channel, text):
    msg(channel, "%s: %s" % (user, text.replace("\n", " ")))
