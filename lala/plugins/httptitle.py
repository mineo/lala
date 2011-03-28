import urllib2
import logging
import re
import HTMLParser

from httplib import HTTPException
from lala.util import regex, msg

_regex = re.compile("(https?://.+)\s?")
_ua = "Mozilla/5.0 (X11; Linux x86_64; rv:2.0b8) Gecko/20100101 Firefox/4.0b8"

def unescape(s):
    p = HTMLParser.HTMLParser()
    return p.unescape(s)

@regex(_regex)
def title(user, channel, text, match_obj):
    url = match_obj.groups()[0]
    req = urllib2.Request(url)
    req.add_header("User-Agent", _ua)
    try:
        content = urllib2.urlopen(req).read()
    except (urllib2.URLError, HTTPException), e:
        logging.debug("%s - %s" % (e, url))
        return

    beg = content.find("<title>")
    if beg != -1:
        title = content[beg+7:content.find("</title>")].replace("\n","")
        try:
            title = unescape(title)
        except HTMLParser.HTMLParseError, e:
            logging.info("%s -  %s" % (e.msg, url))
        msg(channel, "Title: %s" % unicode(title, "utf-8"))
