# coding: utf-8
import logging
import os

from functools import partial
from lala.util import command, msg, on_join
from lala.config import get_int, set_default_options
from twisted.enterprise import adbapi

set_default_options(max_quotes="5")

MESSAGE_TEMPLATE = "[%s] %s"

db_connection = None

db_connection = adbapi.ConnectionPool("sqlite3",
            os.path.join(os.path.expanduser("~/.lala"), "quotes.sqlite3"),
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
        run_query("SELECT quote FROM quotes WHERE rowid = ?;",
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

@command
def delquote(user, channel, text):
    """Delete a quote with a specified number"""
    s_text = text.split()
    if is_admin(user):
        if len(s_text) > 1:
            quotenumber = s_text[1]
            logging.info("Deleting quote: %s" % quotenumber)
            run_query("DELETE FROM quotes where ROWID = (?);",
                     [quotenumber], None)

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
