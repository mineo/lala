from lala import plugin
import logging
import subprocess

class Plugin(plugin.baseplugin):
    def __init__(self, bot):
        bot.register_callback("fortune", self.fortune)

    def fortune(self, bot, user, channel, text):
        try:
            p = subprocess.Popen(["fortune", "fortunes"],
                    stdout=subprocess.PIPE)
            result = p.communicate()[0]
            bot.privmsg(channel,"%s: %s" % (user, result.replace("\n","")))
        except OSError, e:
            logging.error("Error while calling fortune: %s" % e)
