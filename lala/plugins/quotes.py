# coding: utf-8
from __future__ import division
import logging
import os

from collections import defaultdict
from functools import partial
from lala.util import command, msg, on_join
from lala.config import get, get_int, set_default_options
from twisted.enterprise import adbapi
from twisted.internet.defer import inlineCallbacks

set_default_options(database_path=os.path.join(os.path.expanduser("~/.lala"),
                                               "quotes.sqlite3"),
                    max_quotes="5")

MESSAGE_TEMPLATE = "[%s] %s"
MESSAGE_TEMPLATE_WITH_RATING = "[%s] %s (rating: %s, votes: %s)"


def _openfun(c):
    c.execute("PRAGMA foreign_keys = ON;")

db_connection = None
database_path = get("database_path")
db_connection = adbapi.ConnectionPool("sqlite3", database_path,
                                      check_same_thread=False,
                                      cp_openfun=_openfun,
                                      cp_min=1)


def run_query(query, values=[], callback=None):
    res = db_connection.runQuery(query, values)
    if callback is not None:
        res.addCallback(callback)
    return res


def run_interaction(func, callback=None, **kwargs):
    res = db_connection.runInteraction(func, kwargs)
    if callback is not None:
        res.addCallback(callback)
    return res


def setup_db():
    def f(txn, *args):
        txn.execute("""CREATE TABLE IF NOT EXISTS author(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE);""")
        txn.execute("""CREATE TABLE IF NOT EXISTS quote(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quote TEXT,
            author INTEGER NOT NULL REFERENCES author(id));""")
        txn.execute("""CREATE TABLE IF NOT EXISTS voter (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE);""")
        txn.execute("""CREATE TABLE IF NOT EXISTS vote (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vote INT NOT NULL,
            quote INTEGER NOT NULL REFERENCES quote(id),
            voter INTEGER NOT NULL REFERENCES voter(id),
            CONSTRAINT valid_vote CHECK (vote IN (-1, 1)),
            CONSTRAINT unique_quote_voter UNIQUE (quote, voter));""")
    return run_interaction(f)

setup_db()


@command(aliases=["qget"])
def getquote(user, channel, text):
    """Show the quote with a specified number"""
    def callback(quotes):
        if len(quotes) > 0 and quotes[0][0] is not None:
            msg(channel, MESSAGE_TEMPLATE_WITH_RATING % quotes[0])
        else:
            msg(channel, "%s: There's no quote #%s" % (user,
                                                       text))

    if text:
        logging.info("Trying to get quote number %s" % text)
        run_query("""SELECT q.id, q.quote, sum(v.vote) as rating, count(v.vote)
                            as votes
                    FROM quote q
                    LEFT JOIN vote v
                    ON v.quote = q.id
                    WHERE q.id = ?;""",
                  [text],
                  callback)


@command(aliases=["qadd"])
def addquote(user, channel, text):
    """Add a quote"""
    if text:

        def add(txn, *args):
            logging.info("Adding author %s" % user)
            txn.execute("INSERT OR IGNORE INTO author (name) values (?)",
                        [user])
            logging.info("Adding quote: %s" % text)
            txn.execute("INSERT INTO quote (quote, author)\
                            SELECT (?), rowid\
                            FROM author WHERE name = (?);",
                        [text, user])
            txn.execute("SELECT max(rowid) FROM quote;", [])
            num = txn.fetchone()
            msg(channel, "New quote: %s" % num)

        return run_interaction(add)

    else:
        msg(channel, "%s: You didn't give me any text to quote " % user)


@command(admin_only=True, aliases=["qdelete"])
def delquote(user, channel, text):
    """Delete a quote with a specified number"""
    if text:
        logging.debug("delquote: %s" % text)

        def interaction(txn, *args):
            logging.debug("Deleting quote %s" % text)
            txn.execute("DELETE FROM quote WHERE rowid = (?)", [text])
            txn.execute("SELECT changes()")
            res = txn.fetchone()
            logging.debug("%s changes" % res)
            return int(res[0])

        def callback(changes):
            if changes > 0:
                msg(channel, "Quote #%s has been deleted." % text)
                return
            else:
                msg(channel, "It doesn't look like quote #%s exists." %
                    text)

        return run_interaction(interaction, callback)


@command(aliases=["qlast"])
def lastquote(user, channel, text):
    """Show the last quote"""
    callback = partial(_single_quote_callback, channel)
    run_query("SELECT rowid, quote FROM quote ORDER BY rowid DESC\
    LIMIT 1;", [], callback)


@command(aliases=["qrandom"])
def randomquote(user, channel, text):
    """Show a random quote"""
    callback = partial(_single_quote_callback, channel)
    run_query("SELECT rowid, quote FROM quote ORDER BY random() DESC\
    LIMIT 1;", [], callback)


@command(aliases=["qsearch"])
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

    run_query(
        "SELECT rowid, quote FROM quote WHERE quote LIKE (?)",
        ["".join(("%", text, "%"))],
        callback
    )


@command(aliases=["qstats"])
@inlineCallbacks
def quotestats(user, channel, text):
    """Display statistics about all quotes."""
    result = yield run_query("SELECT count(quote) from quote;")
    quote_count = result[0][0]
    msg(channel, "There are a total of %i quotes." % quote_count)
    rows = yield run_query(
        """
        SELECT count(q.quote) AS c, a.name
        FROM quote q
        JOIN author a
        ON q.author = a.rowid
        GROUP BY a.rowid;
        """
    )
    count_author_dict = defaultdict(list)
    for count, author in rows:
        count_author_dict[count].append(author)
    for count, authors in sorted(count_author_dict.items(), reverse=True):
        percentage = (count * 100) / quote_count
        if len(authors) > 1:
            msg(channel, "%s each added %i quote(s) (%.2f%%)" %
                (", ".join(authors), count, percentage))
        else:
            msg(channel, "%s added %i quote(s) (%.2f%%)" %
                (authors[0], count, percentage))


def _like_impl(user, channel, text, votevalue):
    if not len(text):
        msg(channel,
            "%s: You need to specify the number of the quote you like!" % user)
        return

    quotenumber = int(text)

    def interaction(txn, *args):
        logging.debug("Adding 1 vote for %i by %s" % (quotenumber, user))
        txn.execute("""INSERT OR IGNORE INTO voter (name) VALUES (?);""", [user])
        txn.execute("""INSERT OR REPLACE INTO vote (vote, quote, voter)
                        SELECT ?, ?, voter.rowid
                        FROM voter
                        WHERE voter.name = ?;""", [votevalue, quotenumber, user])
        logging.debug("Added 1 vote for %i by %s" % (quotenumber, user))
        msg(channel, "%s: Your vote for quote #%i has been accepted!" % (user, quotenumber))

    return run_interaction(interaction)


@command
def qlike(user, channel, text):
    """`Likes` a quote.
    """
    return _like_impl(user, channel, text, 1)


@command
def qdislike(user, channel, text):
    """`Dislikes` a quote.
    """
    return _like_impl(user, channel, text, -1)


@inlineCallbacks
def _topflopimpl(channel, text, top=True):
    """Shows quotes with the best or worst rating.
    If ``top`` is True, the quotes with the best ratings will be shown,
    otherwise the ones with the worst.
    """
    if text:
        limit = int(text)
    else:
        limit = get("max_quotes")

    results = yield run_query(
        """
        SELECT quote.id, quote.quote, sum(vote) as rating, count(vote) as votes
        FROM vote
        JOIN quote
        ON vote.quote = quote.id
        GROUP BY vote.quote
        ORDER BY rating %s
        LIMIT (?);""" % ("DESC" if top else "ASC"),
        [limit])
    for row in results:
        msg(channel, MESSAGE_TEMPLATE_WITH_RATING % row)


@command
def qtop(user, channel, text):
    """Shows the quotes with the best rating.
    """
    return _topflopimpl(channel, text, True)


@command
def qflop(user, channel, text):
    """Shows the quotes with the worst rating.
    """
    return _topflopimpl(channel, text, False)


@on_join
def join(user, channel):
    def callback(quotes):
        try:
            _send_quote_to_channel(channel, quotes[0])
        except IndexError:
            return

    run_query("SELECT rowid, quote FROM quote where quote LIKE (?)\
    ORDER BY random() LIMIT 1;", ["".join(["%", user, "%"])], callback)


def _single_quote_callback(channel, quotes):
    try:
        _send_quote_to_channel(channel, quotes[0])
    except IndexError:
        return


def _send_quote_to_channel(channel, quote):
    (id, quote) = quote
    msg(channel, MESSAGE_TEMPLATE % (id, quote))
