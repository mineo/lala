from lala import plugin
import logging

from lurklib.exceptions import _Exceptions

class Plugin(plugin.baseplugin):
    def __init__(self, bot):
        #bot.register_callback("load", self.load)
        bot.register_callback("addadmin", self.addadmin)
        bot.register_callback("quit", self.quit)
        bot.register_callback("part", self.part)
        bot.register_callback("join", self.join)
        bot.register_callback("commands", self.commands)
        bot.register_callback("server", self.server)

    def is_admin(self, bot, user):
        if user in bot._admins:
            logging.debug("%s is an admin" % user)
            return True
        else:
            logging.debug("%s is not an admin" % user)
            return False


    def load(self, bot, user, channel, text):
        if self.is_admin(bot, user):
            try:
                bot.plugger.load_plugin(text.split()[1])
            except exceptions.NoSuchPlugin:
                bot.privmsg(channel, "%s could not be found" % text[1])

    def part(self, bot, user, channel, text):
        if self.is_admin(bot, user):
            try:
                logging.debug("Parting %s" % text.split()[1])
                bot.part(text.split()[1])
            except _Exceptions.NotInChannel, e:
                bot.privmsg(channel, "Sorry, %s, I'm not in %s" % (user,
                    text.split()[1]))

    def join(self, bot, user, channel, text):
        if self.is_admin(bot, user):
            chan = text.split()[1]
            try:
                logging.debug("Joining %s" % chan)
                bot.join(chan)
            except _Exceptions.ChannelIsFull, e:
                bot.privmsg(channel, "Sorry, %s is full." % chan)
            except _Exceptions.NoSuchChannel, e:
                bot.privmsg(channel, "Sorry, %s doesn't exist." % chan)
            except _Exceptions.TooManyChannels, e:
                bot.privmsg(channel, "Sorry, I'm already in enough channels.")
            except _Exceptions.InviteOnlyChan, e:
                bot.privmsg(channel, "Sorry, invite only.")
            except _Exceptions.AlreadyInChannel, e:
                bot.privmsg(channel, "I'm already there!")

    def quit(self, bot, user, channel, text):
        if self.is_admin(bot, user):
            logging.debug("Quitting")
            bot.quit("leaving")

    def server(self, bot, user, channel, text):
        """Shows the server the bot is connected to"""
        bot.privmsg(user, bot.server)

    def commands(self, bot, user, channel, text):
        """Prints all available callbacks"""
        bot.privmsg(channel, "I know the following commands:")
        s = "!" + " !".join(bot._callbacks)
        bot.privmsg(channel, s)

    def addadmin(self, bot, user, channel, text):
        """Add a user to the list of admins"""
        if self.is_admin(bot, user):
            bot._admins.append(text)
            bot.privmsg("%s has been added to the list of admins" % text)
