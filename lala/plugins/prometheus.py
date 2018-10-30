#!/usr/bin/env python
# coding: utf-8
# Copyright © 2018 Wieland Hoffmann
# License: MIT, see LICENSE for details
"""
Prometheus
==========

The prompetheus plugin exposes metrics for `Prometheus <https://prometheus.io/>`_.

Options
-------

- ``port``
    The port on which the web server exposes the metrics. Defaults to 9100.
"""  # noqa
import lala.config

from lala.util import on_join, regex
from prometheus_client import Counter
from prometheus_client.twisted import MetricsResource
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.resource import Resource

__all__ = ()

DEFAULT_OPTIONS = {"port": 9100}


messages = Counter("channel_messages_received",
                   "Number of messages seen",
                   ["channel"])

joins = Counter("joins",
                "Number of joins seen",
                ["channel"])


@on_join
def inc_join_counter(user, channel):
    joins.labels(channel=channel).inc()


@regex(".*")
def inc_message_counter(user, channel, text, match_obj):
    messages.labels(channel=channel).inc()


def init():
    root = Resource()
    root.putChild(b'metrics', MetricsResource())

    port = lala.config.get_int("port")

    factory = Site(root)
    reactor.listenTCP(port, factory)
