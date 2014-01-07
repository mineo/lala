import ConfigParser
import logging
import os

from lala import config
from lala.factory import LalaFactory
from twisted.application import service, internet
from twisted.python import log
from twisted.python.usage import Options


CONFIG_DEFAULTS = {
    "channels": "",
    "plugins": "",
    "nickserv_password": None,
    "log_folder": os.path.expanduser("~/.lala/logs"),
    "log_file": os.path.expanduser("~/.lala/lala.log"),
    "encoding": "utf-8",
    "fallback_encoding": "utf-8",
    "max_log_days": 2,
}


class LalaOptions(Options):
    optFlags = [
        ["verbose", "v", "Log debugging information"]
    ]


def getService(options):
    observer = log.PythonLoggingObserver(loggerName="")
    observer.start()

    # Set up the config
    cfg = ConfigParser.RawConfigParser(CONFIG_DEFAULTS)
    try:
        configfile = os.path.join(os.getenv("XDG_CONFIG_HOME"), "lala", "config")
    except AttributeError:
        configfile = os.path.join(os.getenv("HOME"), ".lala", "config")
    files = cfg.read([configfile, "/etc/lala.config"])

    config._CFG = cfg
    config._FILENAME = files[0]

    # Set up logging
    handler = logging.FileHandler(filename=config._get("base", "log_file"),
                                  encoding="utf-8")
    if options["verbose"] or cfg.getboolean("base", "debug"):
        logging.getLogger("").setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s %(filename)s: %(funcName)s:%(lineno)d %(message)s"))
    else:
        logging.getLogger("").setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter("%(message)s"))
    logging.getLogger("").addHandler(handler)

    f = LalaFactory(cfg.get("base", "channels"),
                    cfg.get("base", "nick"))

    return internet.TCPClient(cfg.get("base", "server"),
                              int(cfg.get("base", "port")),
                              f)


def getApplication():
    application = service.Application("lala")

    _service = getService(LalaOptions())

    _service.setServiceParent(application)
    return application
