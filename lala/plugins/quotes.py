import logging
import os

from lala.util import command, msg, on_join, is_admin
from lala.config import get
from twisted.enterprise import adbapi

db_connection = None

db_connection = adbapi.ConnectionPool("sqlite3",
            os.path.join(os.path.expanduser("~/.lala"), "quotes.sqlite3"),
            check_same_thread=False)
db_connection.runOperation("CREATE TABLE IF NOT EXISTS quotes(\
    quote TEXT);")

def run_query(query, values, callback):
    res = db_connection.runQuery(query, values)
    if callback is not None:
        res.addCallback(callback)

@command
def getquote(user, channel, text):
    """Show the quote with a specified number"""
    def callback(quotes):
        if len(quotes) > 0:
            msg(channel, "[%s] %s" % (quotenumber, quotes[0][0]))
        else:
            msg(channel, "%s: There's no quote #%s" % (user,
                quotenumber))

    s_text = text.split()
    if len(s_text) > 1:
        quotenumber = s_text[1]
        logging.debug("Trying to get quote number %s" % quotenumber)
        run_query("SELECT quote FROM quotes WHERE rowid = ?;", 
                [quotenumber],
                callback)

@command
def addquote(user, channel, text):
    """Add a quote"""
    def callback(c):
        msg(channel, "New quote: %s" % c[0])

    s_text = text.split()
    if len(s_text) > 1:
        text = " ".join(s_text[1:])
        logging.debug("Adding quote: %s" % text)
        run_query("INSERT INTO quotes (quote) values (?);",
                  [text],
                  None)
        run_query("SELECT max(rowid) FROM quotes;", [], callback)
    else:
        msg(channel, "%s: You didn't give me any text to quote " % user)

@command
def delquote(user, channel, text):
    """Delete a quote with a specified number"""
    s_text = text.split()
    if is_admin(user):
        if len(s_text) > 1:
            quotenumber = s_text[1]
            logging.debug("Deleting quote: %s" % quotenumber)
            run_query("DELETE FROM quotes where ROWID = (?);",
                     [quotenumber], None)

@command
def lastquote(user, channel, text):
    """Show the last quote"""
    def callback(quotes):
        try:
            (id, quote) = quotes[0]
            msg(channel, "[%s] %s" % (id, quote))
        except IndexError, e:
            return
    with db_connection:
            run_query("SELECT rowid, quote FROM quotes ORDER BY rowid DESC\
            LIMIT 1;", [], callback)

@command
def randomquote(user, channel, text):
    """Show a random quote"""
    def callback(quotes):
        try:
            (id, quote) = quotes[0]
            msg(channel, "[%s] %s" % (id, quote))
        except IndexError, e:
            return

    run_query("SELECT rowid, quote FROM quotes ORDER BY random() DESC\
    LIMIT 1;", [], callback)

@command
def searchquote(user, channel, text):
    """Search for a quote"""
    def callback(quotes):
        max_quotes = int(get("max_quotes", 5))
        if len(quotes) > max_quotes:
            msg(channel, "Too many results, please refine your search")
        else:
            messages = ["[%s] %s" % (id, quote) for (id, quote) in quotes]
            msg(channel, messages)

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
            (id, quote) = quotes[0]
            msg(channel, "[%s] %s" % (id, quote), log=False)
        except IndexError, e:
            return

    run_query("SELECT rowid, quote FROM quotes where quote LIKE (?)\
    ORDER BY random() LIMIT 1;", ["".join(["%", user, "%"])], callback)
