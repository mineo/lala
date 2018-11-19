import logging

from lala import config
from lala.factory import LalaFactory
from twisted.application import service, internet
from twisted.python import log
from twisted.python.usage import Options


class LalaOptions(Options):
    optFlags = [
        ["verbose", "v", "Log debugging information"]
    ]


def getService(options):  # noqa: N802
    observer = log.PythonLoggingObserver(loggerName="")
    observer.start()

    # Set up the config
    config._initialize()

    # Set the default logging level so we can already log messages
    logging.getLogger("").setLevel(logging.INFO)

    # Set up logging
    handler = logging.FileHandler(filename=config._get("base", "log_file"),
                                  encoding="utf-8")
    if options["verbose"] or config._CFG.getboolean("base", "debug"):
        logging.getLogger("").setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s %(filename)s: %(funcName)s:%(lineno)d"
            " %(message)s"))
    else:
        handler.setFormatter(logging.Formatter("%(message)s"))
    logging.getLogger("").addHandler(handler)

    f = LalaFactory(config._get("base", "channels"),
                    config._get("base", "nick"))

    return internet.TCPClient(config._get("base", "server"),
                              int(config._get("base", "port")),
                              f)


def getApplication():  # noqa: N802
    application = service.Application("lala")

    _service = getService(LalaOptions())

    _service.setServiceParent(application)
    return application
