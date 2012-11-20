import urllib2
import logging


from lala.util import msg, command
from twisted.web.client import getPage

DFEOOJM_URL = "http://www.downforeveryoneorjustme.com/%s"

@command
def isitdown(user, channel, text):
    def callback(content):
        if "It's just you" in content:
            msg(channel, "%s: It's just you!" % user)
        else:
            msg(channel, "%s: It's not just you!" % user)

    def errback(error):
        msg(channel, "%s: Sorry, something went wrong while processing your request." % user)
        logging.info(error)

    s_text = text.split()
    if len(s_text) <= 1:
        return
    website = DFEOOJM_URL % " ".join(s_text[1:])
    logging.debug("Trying to open %s" % website)
    getPage(str(website)).addCallbacks(callback, errback)
