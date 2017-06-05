#!/usr/bin/env python
# coding: utf-8
# Copyright © 2017 Wieland Hoffmann
# License: MIT, see LICENSE for details
"""
Web Socket
=============

The web socket plugin runs a web socket server on the configured port. Clients will be sent JSON messages of the following form for each message received by the bot::

    {"user": username, "text": message}


Options
-------

- ``port``
    The port on which the websocket server will listen. Defaults to 9000.

"""  # noqa
import lala.config
import logging

from autobahn.twisted.websocket import (WebSocketServerFactory,
                                        WebSocketServerProtocol)
from json import dumps
from lala.util import regex
from twisted.internet import reactor

__all__ = ()


DEFAULT_OPTIONS = {"port": 9000}

_CONNECTIONS = []


class LalaWebSocketProtocol(WebSocketServerProtocol):
    def onConnect(self, request):  # noqa: N802
        """
        :param self:
        :param request:
        """
        global _CONNECTIONS
        logging.debug("Client connecting from %s", request.peer)
        _CONNECTIONS.append(self)

    def onClose(self, wasClean, code, reason):  # noqa: N802, N803
        """
        :param self:
        :param wasClean:
        :param code:
        :param reason:
        """
        global _CONNECTIONS
        logging.debug("Client connection closed (cleanly: %s), reason %s",
                      wasClean, reason)
        _CONNECTIONS.remove(self)


@regex(".*")
def push(user, channel, text, match_obj):
    """
    :param user:
    :param channel:
    :param text:
    """
    payload = {"user": user,
               "message": text}
    formatted_payload = dumps(payload)
    for connection in _CONNECTIONS:
        connection.sendMessage(formatted_payload, False)


def init():
    factory = WebSocketServerFactory()
    factory.protocol = LalaWebSocketProtocol
    port = lala.config.get_int("port")
    logging.info("Starting websocket server on port %d", port)
    reactor.listenTCP(port, factory)
