import logging
import re
import HTMLParser

from lala.util import regex, msg
from twisted.web.client import getPage

_regex = re.compile("(https?://.+)\s?")
_ua = "Mozilla/5.0 (X11; Linux x86_64; rv:2.0b8) Gecko/20100101 Firefox/4.0b8"

def unescape(s):
    p = HTMLParser.HTMLParser()
    return p.unescape(s)

@regex(_regex)
def title(user, channel, text, match_obj):
    url = match_obj.groups()[0]
    def callback(content):
        beg = content.find("<title>")
        if beg != -1:
            title = content[beg+7:content.find("</title>")].replace("\n","")
            try:
                title = unescape(title)
            except HTMLParser.HTMLParseError, e:
                logging.exception("%s -  %s" % (e.msg, url))
            msg(channel, "Title: %s" % unicode(title, "utf-8"))

    def errback(error):
        msg(channel, "Sorry, I couldn't get the title for %s" % url)
        logging.exception(error)

    getPage(str(url)).addCallbacks(callback, errback)
