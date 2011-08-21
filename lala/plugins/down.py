import urllib2
import logging

from lala.util import msg, command
from httplib import HTTPException

DFEOOJM_URL = "http://www.downforeveryoneorjustme.com/%s"

@command
def isitdown(user, channel, text):
    website = DFEOOJM_URL % " ".join(text.split()[1:])
    logging.debug("Trying to open %s" % website)
    try:
        content = urllib2.urlopen(website).read()
    except (urllib2.URLError, HTTPException), e:
        logging.debug(e)
        msg(channel,
        "%s: An error occured. Please check the log for more details" % user)
        return

    if "just you" in content:
        msg(channel, "%s: It's just you!" % user)
    else:
        msg(channel, "%s: It's not just you!" % user)
