import lala.config as config
import lala.util as util
import logging
import lala.pluginmanager

from lala.util import command, msg
from twisted.internet import reactor

#@command
#def load(user, channel, text):
    #if is_admin(user):
        #util._BOT.plugger.load_plugin(text.split()[1])


@command(admin_only=True)
def part(user, channel, text):
    """Part a channel"""
    logging.debug("Parting %s" % channel)
    util._BOT.part(channel.encode("utf-8"))


@command(admin_only=True)
def join(user, channel, chan):
    """Join a channel"""
    logging.debug("Joining %s" % chan)
    util._BOT.join(chan.encode("utf-8"))


@command(admin_only=True)
def quit(user, channel, text):
    logging.debug("Quitting")
    util._BOT.quit("leaving")
    reactor.stop()


@command(admin_only=True)
def reconnect(user, channel, text):
    logging.debug("Reconnecting")
    util._BOT.quit("leaving")


@command
def server(user, channel, text):
    """Shows the server the bot is connected to"""
    msg(user, util._BOT.server)


@command
def commands(user, channel, text):
    """Prints all available callbacks"""
    msg(channel, "I know the following commands:")
    s = "!" + " !".join(lala.pluginmanager._callbacks)
    msg(channel, s)


@command(admin_only=True)
def addadmin(user, channel, admin):
    """Add a user to the list of admins"""
    if admin in config.get("admins"):
        msg(channel, "%s already is an admin" % admin)
    else:
        config.set("admins", "%s,%s" % (config.get("admins"), admin))
        msg(channel,
                    "%s has been added to the list of admins" % admin)


@command
def admins(user, channel, text):
    """Show the list of admins"""
    msg(channel, config.get("admins"))


@command(admin_only=True)
def deladmin(user, channel, admin):
    """Remove a user from the list of admins"""
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
def help(user, channel, cmd):
    """Show the help for a command"""
    try:
        func = lala.pluginmanager._callbacks[cmd].func
    except KeyError:
        msg(channel, "%s is not a command I know" % cmd)
        return
    except IndexError:
        msg(channel, "Please specify a command")
        return
    else:
        if func.__doc__ is not None:
            msg(channel, "%s: %s" % (cmd, func.__doc__))
        else:
            msg(channel, "There is no help available for %s" % cmd)


@command(admin_only=True)
def enable(user, channel, command):
    """Enables a command or regular expression
    """
    logging.info("Enabling %s" % command)
    lala.pluginmanager.enable(command)


@command(admin_only=True)
def disable(user, channel, command):
    """disables a command.
    """
    logging.info("Disabling %s" % command)
    lala.pluginmanager.disable(command)


@command(admin_only=True)
def pluginupdate(user, channel, text):
    """Reloads all plugins. Plugins that are not enabled in the configuration
    file will be disabled by calling this!
    """
    lala.pluginmanager._reload()
    msg(channel, "All enabled plugins have been reloaded.")
