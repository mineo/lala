import logging
from lala import plugin


from random import choice

class Plugin(plugin.baseplugin):
    def __init__(self, bot):
        bot.register_callback("decide", self.decide)

    def decide(self, bot, user, channel, text):
        s_text = text.split("/")
        s_text[0] = " ".join(s_text[0].split()[1:])
        bot.privmsg(channel, "%s: %s" %(user, choice(s_text)))
