import logging
import plugin


from random import randint

class Plugin(plugin.baseplugin):
    def __init__(self, bot):
        bot.register_callback("decide", self.decide)

    def decide(self, bot, user, channel, text):
        s_text = text.split("/")[1:]
        choice = randint(0, len(s_text)-1)
        bot.privmsg(channel, "%s: %s" %(user, s_text[choice]))
