#!/usr/bin/env python
# coding: utf-8
# Copyright © 2015 Wieland Hoffmann
# License: MIT, see LICENSE for details
"""Ilmenau weather
===============

This plugin can be used to display information about the weather in Ilmenau,
Germany.

It only provides one command:

- ``iweather``
  Displays weather information.

Options
-------

- None

"""
from lala.util import command, msg
from scrapy.crawler import Crawler
from scrapy import signals
from ilmwetter import settings as iw_settings
from ilmwetter.spiders.thedy import ThedySpider
from scrapy.settings import Settings
__all__ = ()


def item_scraped(item, response, spider):
    return msg(spider.lala_channel,
               u"It's %.2f°C in Ilmenau at a humidity of %.1f%%." % (
                   item["temperature"],
                   item["humidity"]))


@command(aliases=["iw"])
def iweather(user, channel, text):
    """Show the current weather in Ilmenau."""

    settings = Settings()
    settings.setmodule(iw_settings)
    spider = ThedySpider()
    spider.lala_channel = channel
    crawler = Crawler(settings)

    crawler.signals.connect(item_scraped,
                            signal=signals.item_scraped)
    crawler.configure()
    crawler.crawl(spider)
    return crawler.start()
