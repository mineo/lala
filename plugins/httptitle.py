import plugin
import urllib2
import logging
import re

from httplib import HTTPException
from htmllib import HTMLParser

class Plugin(plugin.baseplugin):
    def __init__(self, bot):
        self._regex = re.compile("(https?://.+)\s?")
        self._ua = "Mozilla/5.0 (X11; Linux x86_64; rv:2.0b8) Gecko/20100101 Firefox/4.0b8"
        bot.register_regex(self._regex, self.title)

    def unescape(self, s):
        p = HTMLParser(None)
        p.save_bgn()
        p.feed(s)
        return p.save_end()

    def title(self, bot, user, channel, text, match_obj):
        url = match_obj.groups()[0]
        req = urllib2.Request(url)
        req.add_header("User-Agent", self._ua)
        try:
            content = urllib2.urlopen(req).read()
        except (urllib2.URLError, HTTPException), e:
            logging.debug("%s - %s" % (e, url))
            return
        beg = content.find("<title>")
        if beg != -1:
            title = content[beg+7:content.find("</title>")].replace("\n","")
            title = self.unescape(title)
            bot.privmsg(channel, "Title: %s" % unicode(title, "utf-8"))
