# coding: utf-8
from __future__ import division
import logging
import os

from collections import defaultdict
from functools import partial
from lala.util import command, msg, on_join
from lala.config import get, get_int, set_default_options
from twisted.enterprise import adbapi

set_default_options(database_path=os.path.join(os.path.expanduser("~/.lala"),
                                               "quotes.sqlite3"),
                    max_quotes="5")

MESSAGE_TEMPLATE = "[%s] %s"

db_connection = None
database_path = get("database_path")
db_connection = adbapi.ConnectionPool("sqlite3", database_path,
                                      check_same_thread=False)

def setup_db():
    db_connection.runOperation("CREATE TABLE IF NOT EXISTS quotes(\
        quote TEXT,\
        author INTEGER NOT NULL REFERENCES authors(rowid));")
    db_connection.runOperation("CREATE TABLE IF NOT EXISTS authors(\
        name TEXT NOT NULL UNIQUE);")

setup_db()

def run_query(query, values, callback):
    res = db_connection.runQuery(query, values)
    if callback is not None:
        res.addCallback(callback)

def run_interaction(func, callback = None,  **kwargs):
    res = db_connection.runInteraction(func, kwargs)
    if callback is not None:
        res.addCallback(callback)

@command
def getquote(user, channel, text):
    """Show the quote with a specified number"""
    def callback(quotes):
        if len(quotes) > 0:
            _send_quote_to_channel(channel, quotes[0])
        else:
            msg(channel, "%s: There's no quote #%s" % (user,
                quotenumber))

    s_text = text.split()
    if len(s_text) > 1:
        quotenumber = s_text[1]
        logging.info("Trying to get quote number %s" % quotenumber)
        run_query("SELECT rowid, quote FROM quotes WHERE rowid = ?;",
                [quotenumber],
                callback)

@command
def addquote(user, channel, text):
    """Add a quote"""
    def msgcallback(c):
        msg(channel, "New quote: %s" % c[0])

    def addcallback(c):
        # TODO This might not be the rowid we're looking for in all cases…
        run_query("SELECT max(rowid) FROM quotes;", [], msgcallback)

    s_text = text.split()
    if len(s_text) > 1:
        text = " ".join(s_text[1:])

        def add(c):
            logging.info("Adding quote: %s" % text)
            run_query("INSERT INTO quotes (quote, author)\
                            SELECT (?), rowid\
                            FROM authors WHERE name = (?);",
                      [text , user],
                      addcallback)

        logging.info("Adding author %s" % user)
        run_query("INSERT OR IGNORE INTO authors (name) values (?)",
                [user],
                add)
    else:
        msg(channel, "%s: You didn't give me any text to quote " % user)

@command(admin_only=True)
def delquote(user, channel, text):
    """Delete a quote with a specified number"""
    s_text = text.split()
    if len(s_text) > 1:
        quotenumber = s_text[1]
        logging.debug("delquote: %s" % quotenumber)

        def interaction(txn, *args):
            logging.debug("Deleting quote %s" % quotenumber)
            txn.execute("DELETE FROM quotes WHERE rowid = (?)", [ quotenumber ])
            txn.execute("SELECT changes()")
            res = txn.fetchone()
            logging.debug("%s changes" % res)
            return int(res[0])

        def callback(changes):
            if changes > 0:
                msg(channel, "Quote #%s has been deleted." % quotenumber)
                return
            else:
                msg(channel, "It doesn't look like quote #%s exists." %
                        quotenumber)

        run_interaction(interaction, callback)

@command
def lastquote(user, channel, text):
    """Show the last quote"""
    callback = partial(_single_quote_callback, channel)
    run_query("SELECT rowid, quote FROM quotes ORDER BY rowid DESC\
    LIMIT 1;", [], callback)

@command
def randomquote(user, channel, text):
    """Show a random quote"""
    callback = partial(_single_quote_callback, channel)
    run_query("SELECT rowid, quote FROM quotes ORDER BY random() DESC\
    LIMIT 1;", [], callback)

@command
def searchquote(user, channel, text):
    """Search for a quote"""
    def callback(quotes):
        max_quotes = get_int("max_quotes")
        if len(quotes) > max_quotes:
            msg(channel, "Too many results, please refine your search")
        elif len(quotes) == 0:
            msg(channel, "No matching quotes found")
        else:
            for quote in quotes:
                _send_quote_to_channel(channel, quote)

    s_text = text.split()
    logging.debug(s_text[1:])

    run_query(
        "SELECT rowid, quote FROM quotes WHERE quote LIKE (?)",
        ["".join(("%", " ".join(s_text[1:]), "%"))],
        callback
        )

@command
def quotestats(user, channel, text):
    """Display statistics about all quotes."""
    def quote_count_callback(channel, result):
        quote_count = result[0][0]
        logging.debug(quote_count)
        msg(channel, "There are a total of %i quotes." % quote_count)
        callback = partial(author_stats_callback, channel, quote_count)
        run_query(
            """
            SELECT count(q.quote) AS c, a.name
            FROM quotes q
            JOIN authors a
            ON q.author = a.rowid
            GROUP BY a.rowid;
            """,
            [],
            callback)

    def author_stats_callback(channel, num_quotes, rows):
        count_author_dict = defaultdict(list)
        for count, author in rows:
            count_author_dict[count].append(author)
        for count, authors in sorted(count_author_dict.items(), reverse=True):
            percentage = (count * 100)/num_quotes
            if len(authors) > 1:
                msg(channel, "%s each added %i quote(s) (%.2f%%)" %
                    (", ".join(authors), count, percentage))
            else:
                msg(channel, "%s added %i quote(s) (%.2f%%)" %
                    (authors[0], count, percentage))

    quote_count_callback = partial(quote_count_callback, channel)
    run_query("SELECT count(quote) from quotes;", [], quote_count_callback)

@on_join
def join(user, channel):
    def callback(quotes):
        try:
            _send_quote_to_channel(channel, quotes[0])
        except IndexError, e:
            return

    run_query("SELECT rowid, quote FROM quotes where quote LIKE (?)\
    ORDER BY random() LIMIT 1;", ["".join(["%", user, "%"])], callback)

def _single_quote_callback(channel, quotes):
    try:
        _send_quote_to_channel(channel, quotes[0])
    except IndexError, e:
        return

def _send_quote_to_channel(channel, quote):
    (id, quote) = quote
    msg(channel, MESSAGE_TEMPLATE % (id, quote))
