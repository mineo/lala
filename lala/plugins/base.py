import logging

from lurklib.exceptions import _Exceptions
from lala.util import _BOT, command, is_admin, msg

@command("load")
def load(user, channel, text):
    if is_admin(user):
        try:
            _BOT.plugger.load_plugin(text.split()[1])
        except exceptions.NoSuchPlugin:
            msg(channel, "%s could not be found" % text[1])

@command("part")
def part(user, channel, text):
    if is_admin(user):
        try:
            logging.debug("Parting %s" % text.split()[1])
            _BOT.part(text.split()[1])
        except _Exceptions.NotInChannel, e:
            msg(channel, "Sorry, %s, I'm not in %s" % (user,
                text.split()[1]))

@command("join")
def join(user, channel, text):
    if is_admin(user):
        chan = text.split()[1]
        try:
            logging.debug("Joining %s" % chan)
            _BOT.join(chan)
        except _Exceptions.ChannelIsFull, e:
            msg(channel, "Sorry, %s is full." % chan)
        except _Exceptions.NoSuchChannel, e:
            msg(channel, "Sorry, %s doesn't exist." % chan)
        except _Exceptions.TooManyChannels, e:
            msg(channel, "Sorry, I'm already in enough channels.")
        except _Exceptions.InviteOnlyChan, e:
            msg(channel, "Sorry, invite only.")
        except _Exceptions.AlreadyInChannel, e:
            msg(channel, "I'm already there!")

@command("quit")
def quit(user, channel, text):
    if is_admin(user):
        logging.debug("Quitting")
        _BOT.quit("leaving")

@command("server")
def server(user, channel, text):
    """Shows the server the _BOT is connected to"""
    msg(user, _BOT.server)

@command("commands")
def commands(user, channel, text):
    """Prints all available callbacks"""
    msg(channel, "I know the following commands:")
    s = "!" + " !".join(_BOT._callbacks)
    msg(channel, s)

@command("addadmin")
def addadmin(user, channel, text):
    """Add a user to the list of admins"""
    admin = text.split()[1]
    if is_admin(user):
        if admin in _BOT._admins:
            msg(channel, "%s already is an admin" % admin)
        else:
            _BOT._admins.append(admin)
            msg(channel,
                        "%s has been added to the list of admins" % admin)

@command("admins")
def admins(user, channel, text):
    """Print the list of admins"""
    if is_admin(user):
        msg(channel, " ".join(_BOT._admins))

@command("deladmin")
def deladmin(user, channel, text):
    """Remove a user from the list of admins"""
    admin = text.split()[1]
    if is_admin(user):
        if admin in _BOT._admins:
            _BOT._admins.remove(admin)
            msg(channel,
                        "%s has been removed from the list of admins" %
                        admin)
        else:
            msg(channel, "Sorry, %s is not even an admin" % text)
