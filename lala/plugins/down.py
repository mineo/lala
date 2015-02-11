"""
Downforeveryoneorjustme
=======================

This plugin provides a single command, ``isitdown`` that, given a URL checks its
availability on
`Downforeveryoneorjustme <http://www.downforeveryoneorjustme.com/>`_.

Options
-------

- None
"""
import logging


from lala.util import msg, command
from twisted.web.client import getPage
from twisted.internet.defer import inlineCallbacks

DFEOOJM_URL = "http://www.downforeveryoneorjustme.com/%s"


@command
@inlineCallbacks
def isitdown(user, channel, text):
    website = DFEOOJM_URL % text
    logging.debug("Trying to open %s" % website)
    content = yield getPage(str(website))
    if "It's just you" in content:
        msg(channel, "%s: It's just you!" % user)
    else:
        msg(channel, "%s: It's not just you!" % user)
