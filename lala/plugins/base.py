import logging
import lala.config as config
import lala.util as util

from lala.util import command, msg, is_admin

#@command
#def load(user, channel, text):
    #if is_admin(user):
        #util._BOT.plugger.load_plugin(text.split()[1])

@command
def part(user, channel, text):
    if is_admin(user):
        logging.debug("Parting %s" % text.split()[1])
        util._BOT.part(text.split()[1])

@command
def join(user, channel, text):
    if is_admin(user):
        chan = text.split()[1]
        logging.debug("Joining %s" % chan)
        util._BOT.join_(chan)

@command
def quit(user, channel, text):
    if is_admin(user):
        logging.debug("Quitting")
        util._BOT.quit("leaving")

@command
def reconnect(user, channel, text):
    if is_admin(user):
        logging.debug("Reconnecting")
        util._BOT.quit("leaving")

@command
def server(user, channel, text):
    """Shows the server the util._BOT is connected to"""
    msg(user, util._BOT.server)

@command
def commands(user, channel, text):
    """Prints all available callbacks"""
    msg(channel, "I know the following commands:")
    s = "!" + " !".join(util._PM._callbacks)
    msg(channel, s)

@command
def addadmin(user, channel, text):
    """Add a user to the list of admins"""
    admin = text.split()[1]
    if is_admin(user):
        if admin in config.get("admins"):
            msg(channel, "%s already is an admin" % admin)
        else:
            config.set("admins", "%s,%s" % (config.get("admins"), admin))
            msg(channel,
                        "%s has been added to the list of admins" % admin)

@command
def admins(user, channel, text):
    """Print the list of admins"""
    if is_admin(user):
        msg(channel, config.get("admins"))

@command
def deladmin(user, channel, text):
    """Remove a user from the list of admins"""
    admin = text.split()[1]
    if is_admin(user):
        if admin in config.get("admins"):
            admins = config.get("admins").split(",")
            admins.remove(admin)
            config.set("admins", ",".join(admins))
            msg(channel,
                        "%s has been removed from the list of admins" %
                        admin)
        else:
            msg(channel, "Sorry, %s is not even an admin" % admin)

@command
def help(user, channel, text):
    """Show the help for a command"""
    cmd = text.split()[1]
    try:
        func = util._PM._callbacks[cmd]
    except KeyError, e:
        msg(channel, "%s is not a command I know" % cmd)
        return
    else:
        if func.__doc__ is not None:
            msg(channel, "%s: %s" % (cmd, func.__doc__))
        else:
            msg(channel, "There is no help available for %s" % cmd)
