#!/usr/bin/env python
# coding: utf-8
# Copyright © 2017 Wieland Hoffmann
# License: MIT, see LICENSE for details
"""
Feinstaubalarm
==============

This plugin provides a single command, ``feinstaubalarm`` that checks if there's
currently a "Feinstaubalarm" in Stuttgart, Germany.

Options
-------

- None
"""
from lala.util import msg, command
from twisted.web.client import getPage
from twisted.internet.defer import inlineCallbacks

URL = "http://www.stuttgart.de/feinstaubalarm/widget/xtrasmall"


@command(aliases=["fsa"])
@inlineCallbacks
def feinstaubalarm(user, channel, text):
    content = yield getPage(str(URL))
    if "Aktuell kein" in content:
        msg(channel, "%s: Aktuell kein Feinstaubalarm!" % user)
    else:
        msg(channel, "%s: Feinstaubalarm!" % user)
