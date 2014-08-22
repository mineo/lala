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
MESSAGE_TEMPLATE_WITH_RATING = "[%s] %s (rating: %s, votes: %s)"


def _openfun(c):
    c.execute("PRAGMA foreign_keys = ON;")

db_connection = None
database_path = get("database_path")
db_connection = adbapi.ConnectionPool("sqlite3", database_path,
                                      check_same_thread=False,
                                      cp_openfun=_openfun,
                                      cp_min=1)


def setup_db():
    db_connection.runOperation("""CREATE TABLE IF NOT EXISTS author(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE);""")
    db_connection.runOperation("""CREATE TABLE IF NOT EXISTS quote(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quote TEXT,
        author INTEGER NOT NULL REFERENCES author(id));""")
    db_connection.runOperation("""CREATE TABLE IF NOT EXISTS voter (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE);""")
    db_connection.runOperation("""CREATE TABLE IF NOT EXISTS vote (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vote INT NOT NULL,
        quote INTEGER NOT NULL REFERENCES quote(id),
        voter INTEGER NOT NULL REFERENCES voter(id),
        CONSTRAINT valid_vote CHECK (vote IN (-1, 1)),
        CONSTRAINT unique_quote_voter UNIQUE (quote, voter));""")

setup_db()

def run_query(query, values, callback):
    res = db_connection.runQuery(query, values)
    if callback is not None:
        res.addCallback(callback)


def run_interaction(func, callback = None,  **kwargs):
    res = db_connection.runInteraction(func, kwargs)
    if callback is not None:
        res.addCallback(callback)


@command(aliases=["qget"])
def getquote(user, channel, text):
    """Show the quote with a specified number"""
    def callback(quotes):
        if len(quotes) > 0 and quotes[0][0] is not None:
            msg(channel, MESSAGE_TEMPLATE_WITH_RATING % quotes[0])
        else:
            msg(channel, "%s: There's no quote #%s" % (user,
                quotenumber))

    s_text = text.split()
    if len(s_text) > 1:
        quotenumber = s_text[1]
        logging.info("Trying to get quote number %s" % quotenumber)
        run_query("""SELECT q.id, q.quote, sum(v.vote) as rating, count(v.vote)
                            as votes
                    FROM quote q
                    LEFT JOIN vote v
                    ON v.quote = q.id
                    WHERE q.id = ?;""",
                  [quotenumber],
                  callback)


@command(aliases=["qadd"])
def addquote(user, channel, text):
    """Add a quote"""
    def msgcallback(c):
        msg(channel, "New quote: %s" % c[0])

    def addcallback(c):
        # TODO This might not be the rowid we're looking for in all cases…
        run_query("SELECT max(rowid) FROM quote;", [], msgcallback)

    s_text = text.split()
    if len(s_text) > 1:
        text = " ".join(s_text[1:])

        def add(c):
            logging.info("Adding quote: %s" % text)
            run_query("INSERT INTO quote (quote, author)\
                            SELECT (?), rowid\
                            FROM author WHERE name = (?);",
                      [text, user],
                      addcallback)

        logging.info("Adding author %s" % user)
        run_query("INSERT OR IGNORE INTO author (name) values (?)",
                [user],
                add)
    else:
        msg(channel, "%s: You didn't give me any text to quote " % user)


@command(admin_only=True, aliases=["qdelete"])
def delquote(user, channel, text):
    """Delete a quote with a specified number"""
    s_text = text.split()
    if len(s_text) > 1:
        quotenumber = s_text[1]
        logging.debug("delquote: %s" % quotenumber)

        def interaction(txn, *args):
            logging.debug("Deleting quote %s" % quotenumber)
            txn.execute("DELETE FROM quote WHERE rowid = (?)", [ quotenumber ])
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

    s_text = text.split()
    logging.debug(s_text[1:])

    run_query(
        "SELECT rowid, quote FROM quote WHERE quote LIKE (?)",
        ["".join(("%", " ".join(s_text[1:]), "%"))],
        callback
        )


@command(aliases=["qstats"])
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
            FROM quote q
            JOIN author a
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
            percentage = (count * 100) / num_quotes
            if len(authors) > 1:
                msg(channel, "%s each added %i quote(s) (%.2f%%)" %
                    (", ".join(authors), count, percentage))
            else:
                msg(channel, "%s added %i quote(s) (%.2f%%)" %
                    (authors[0], count, percentage))

    quote_count_callback = partial(quote_count_callback, channel)
    run_query("SELECT count(quote) from quote;", [], quote_count_callback)


def _like_impl(user, channel, text, votevalue):
    s_text = text.split()
    if not len(s_text) > 1:
        msg(channel,
            "%s: You need to specify the number of the quote you like!" % user)
        return

    quotenumber = int(s_text[1])

    def interaction(txn, *args):
        logging.debug("Adding 1 vote for %i by %s" % (quotenumber, user))
        txn.execute("""INSERT OR IGNORE INTO voter (name) VALUES (?);""", [user])
        txn.execute("""INSERT OR REPLACE INTO vote (vote, quote, voter)
                        SELECT ?, ?, voter.rowid
                        FROM voter
                        WHERE voter.name = ?;""", [votevalue, quotenumber, user])
        logging.debug("Added 1 vote for %i by %s" % (quotenumber, user))

    def callback(*args):
        msg(channel, "%s: Your vote for quote #%i has been accepted!" % (user, quotenumber))

    run_interaction(interaction, callback)


@command
def qlike(user, channel, text):
    """`Likes` a quote.
    """
    _like_impl(user, channel, text, 1)


@command
def qdislike(user, channel, text):
    """`Dislikes` a quote.
    """
    _like_impl(user, channel, text, -1)


def _topflopimpl(channel, text, top=True):
    """Shows quotes with the best or worst rating.
    If ``top`` is True, the quotes with the best ratings will be shown,
    otherwise the ones with the worst.
    """
    s_text = text.split()
    if len(s_text) == 2:
        limit = int(s_text[1])
    else:
        limit = get("max_quotes")

    def callback(result):
        for row in result:
            msg(channel, MESSAGE_TEMPLATE_WITH_RATING % row)

    run_query("""SELECT quote.id, quote.quote, sum(vote) as rating, count(vote) as votes
                 FROM vote
                 JOIN quote
                 ON vote.quote = quote.id
                 GROUP BY vote.quote
                 ORDER BY rating %s
                 LIMIT (?);""" % ("DESC" if top else "ASC"), [limit], callback)


@command
def qtop(user, channel, text):
    """Shows the quotes with the best rating.
    """
    _topflopimpl(channel, text, True)


@command
def qflop(user, channel, text):
    """Shows the quotes with the worst rating.
    """
    _topflopimpl(channel, text, False)


@on_join
def join(user, channel):
    def callback(quotes):
        try:
            _send_quote_to_channel(channel, quotes[0])
        except IndexError, e:
            return

    run_query("SELECT rowid, quote FROM quote where quote LIKE (?)\
    ORDER BY random() LIMIT 1;", ["".join(["%", user, "%"])], callback)


def _single_quote_callback(channel, quotes):
    try:
        _send_quote_to_channel(channel, quotes[0])
    except IndexError, e:
        return


def _send_quote_to_channel(channel, quote):
    (id, quote) = quote
    msg(channel, MESSAGE_TEMPLATE % (id, quote))
