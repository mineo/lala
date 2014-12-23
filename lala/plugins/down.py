import logging


from lala.util import msg, command
from twisted.web.client import getPage
from twisted.internet.defer import inlineCallbacks

DFEOOJM_URL = "http://www.downforeveryoneorjustme.com/%s"


@command
@inlineCallbacks
def isitdown(user, channel, text):
    s_text = text.split()
    if len(s_text) <= 1:
        return
    website = DFEOOJM_URL % " ".join(s_text[1:])
    logging.debug("Trying to open %s" % website)
    content = yield getPage(str(website))
    if "It's just you" in content:
        msg(channel, "%s: It's just you!" % user)
    else:
        msg(channel, "%s: It's not just you!" % user)
