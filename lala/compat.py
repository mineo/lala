#!/usr/bin/env python
# coding: utf-8
# Copyright © 2017 Wieland Hoffmann
# License: MIT, see LICENSE for details
# flake8: noqa
import six

if six.PY3:
    from html import unescape as html_unescape

else:
    import HTMLParser as htmlparser

    def html_unescape(s):
        p = htmlparser.HTMLParser()
        return p.unescape(s)
