import ConfigParser
import os
import logging
import logging.handlers

from lala import config
from lala.factory import LalaFactory
from os.path import join
from sys import version_info, exit
from twisted.internet import reactor

import optparse

CONFIG_DEFAULTS = {
        "channels": "",
        "plugins": "",
        "nickserv_password": None,
        "log_folder": os.path.expanduser("~/.lala/logs"),
        "log_file": os.path.expanduser("~/.lala/lala.log"),
        "encoding": "utf-8",
        "fallback_encoding": "utf-8",
        "max_log_days": 2
        }


def main():
    """Main method"""
    parser = optparse.OptionParser()
    parser.add_option("-c", "--config", help="Configuration file location")
    parser.add_option("-d", "--debug", help="Enable debugging",
                        action="store_true", default=False)
    parser.add_option("-n", "--no-daemon", help="Do not daemonize",
                        action="store_true", default=False)
    parser.add_option("-s", "--stdout", help="Log to stdout",
                        action="store_true", default=False)
    (args, options) = parser.parse_args()

    if args.stdout and not args.no_daemon:
        exit("--stdout can not be used when daemonizing")

    if args.debug:
        args.no_daemon = True

    cfg = ConfigParser.SafeConfigParser()
    if args.config is None:
        try:
            configfile = os.path.join(os.getenv("XDG_CONFIG_HOME"), "lala", "config")
        except AttributeError:
            configfile = os.path.join(os.getenv("HOME"), ".lala", "config")
        files = cfg.read([configfile, "/etc/lala.config"])
    else:
        files = cfg.read(args.config)

    config._CFG = cfg
    config._FILENAME = files[0]

    log_folder = get_conf_key(cfg, "log_folder")
    config._CFG.set("base", "log_folder", log_folder)
    logfile = join(log_folder, "lala.log")
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    logger = logging.getLogger("MessageLog")
    chathandler = logging.handlers.TimedRotatingFileHandler(
            encoding="utf-8",
            filename=logfile,
            when="midnight",
            backupCount=int(get_conf_key(cfg, "max_log_days")))
    logger.setLevel(logging.INFO)
    chathandler.setFormatter(
            logging.Formatter("%(asctime)s %(message)s",
                              "%Y-%m-%d %H:%m"))
    logger.propagate = False
    logger.addHandler(chathandler)

    handler = None

    if not args.stdout:
        handler = logging.FileHandler(filename=get_conf_key(cfg,"log_file"),
                                          encoding="utf-8")
    else:
        handler = logging.StreamHandler()

    logging.getLogger("").addHandler(handler)

    debugformat=\
        "%(levelname)s %(filename)s: %(funcName)s: %(lineno)d %(message)s"
    handler.setFormatter(logging.Formatter(debugformat))

    if args.debug:
        logging.getLogger("").setLevel(logging.DEBUG)

    if not args.no_daemon:
        import daemon
        with daemon.DaemonContext(files_preserve=[handler.stream.fileno(),
                                  chathandler.stream.fileno()]):
            f = LalaFactory(get_conf_key(cfg, "channels"),
                    get_conf_key(cfg, "nick"),
                    get_conf_key(cfg, "plugins").split(","),
                    logger)
            reactor.connectTCP(get_conf_key(cfg, "server"),
                    int(get_conf_key(cfg, "port")),
                    f)
            reactor.run()
    else:
            f = LalaFactory(get_conf_key(cfg, "channels"),
                    get_conf_key(cfg, "nick"),
                    get_conf_key(cfg, "plugins").split(","),
                    logger)
            reactor.connectTCP(get_conf_key(cfg, "server"),
                    int(get_conf_key(cfg, "port")),
                    f)
            reactor.run()


def get_conf_key(conf, key):
    try:
        return conf.get("base", key)
    except ConfigParser.NoOptionError:
        return CONFIG_DEFAULTS[key]
