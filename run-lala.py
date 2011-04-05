#!/usr/bin/python2
import ConfigParser
import sys
import os
import socket
import logging

from lala import Bot, config
from time import sleep
from os.path import join

def main():
    """Main method"""
    cfg = ConfigParser.SafeConfigParser()
    try:
        configfile = os.path.join(os.getenv("XDG_CONFIG_HOME"),"lala","config")
    except AttributeError:
        configfile = os.path.join(os.getenv("HOME"),".lala","config")
    cfg.read(configfile)
    lalaconfig = cfg._sections["base"]

    config._CFG = cfg
    config._FILENAME = configfile

    if "-d" in sys.argv:
        debug = True
    else:
        debug = False

    logfolder = os.path.expanduser("~/.lala/logs")
    logfile = join(logfolder, "lala.log")
    if not os.path.exists(logfolder):
        os.makedirs(logfolder)
    logger = logging.getLogger("MessageLog")
    handler = logging.handlers.TimedRotatingFileHandler(
            encoding="utf-8",
            filename=logfile,
            when="midnight")
    logger.setLevel(logging.INFO)
    handler.setFormatter(
            logging.Formatter("%(asctime)s %(message)s",
                              "%Y-%m-%d %H:%m"))
    logger.addHandler(handler)

    bot = Bot(
            server=lalaconfig["server"],
            port=int(lalaconfig["port"]),
            nick=lalaconfig["nick"],
            channels=get_conf_key(lalaconfig, "channels", []).split(","),
            debug=debug,
            plugins=get_conf_key(lalaconfig, "plugins", []).split(","),
            nickserv = get_conf_key(lalaconfig, "nickserv_password", None)
            )
    bot.mainloop()

def get_conf_key(conf, key, default):
    try:
        return conf[key]
    except KeyError:
        return default


if __name__ == '__main__':
    main()
