#!/usr/bin/python2
import ConfigParser
import os
import logging

from lala import Bot, config
from os.path import join
from sys import version_info

if version_info >= (2,7):
    import argparse
else:
    import optparse

CONFIG_DEFAULTS = {
        "channels": "",
        "plugins": "",
        "nickserv_password": None,
        "log_folder": os.path.expanduser("~/.lala/logs"),
        "encoding" : "utf-8",
        "fallback_encoding" : "utf-8"
        }

def main():
    """Main method"""
    if version_info >= (2,7):
        parser = argparse.ArgumentParser()
        parser.add_argument("-c", "--config", help="Configuration file location")
        parser.add_argument("-d", "--debug", help="Enable debugging",
                            action="store_true", default=False)
        args = parser.parse_args()
    else:
        parser = optparse.OptionParser()
        parser.add_option("-c", "--config", help="Configuration file location")
        parser.add_option("-d", "--debug", help="Enable debugging",
                            action="store_true", default=False)
        (args, options) = parser.parse_args()

    cfg = ConfigParser.SafeConfigParser()
    if args.config is None:
        try:
            configfile = os.path.join(os.getenv("XDG_CONFIG_HOME"),"lala","config")
        except AttributeError:
            configfile = os.path.join(os.getenv("HOME"),".lala","config")
        files = cfg.read([configfile, "/etc/lala.config"])
    else:
        files = cfg.read(args.config)

    config._CFG = cfg
    config._FILENAME = files[0]

    log_folder = get_conf_key(cfg, "log_folder")
    config._CFG.set("base","log_folder", log_folder)
    logfile = join(log_folder, "lala.log")
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
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
            server=get_conf_key(cfg,"server"),
            port=int(get_conf_key(cfg,"port")),
            nick=get_conf_key(cfg,"nick"),
            channels=get_conf_key(cfg, "channels").split(","),
            debug=args.debug,
            plugins=get_conf_key(cfg, "plugins").split(","),
            nickserv = get_conf_key(cfg, "nickserv_password"),
            encoding = get_conf_key(cfg, "encoding"),
            fallback_encoding = get_conf_key(cfg, "fallback_encoding")
            )
    bot.mainloop()

def get_conf_key(conf, key):
    try:
        return conf.get("base",key)
    except ConfigParser.NoOptionError:
        return CONFIG_DEFAULTS[key]

if __name__ == '__main__':
    main()
