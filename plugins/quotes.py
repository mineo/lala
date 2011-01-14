import sqlite3
import logging
import plugin

class Plugin(plugin.baseplugin):
    def __init__(self, bot):
        self._con = sqlite3.connect("quotes.sqlite3")
        self._con.execute("CREATE TABLE IF NOT EXISTS quotes(\
            quote TEXT);")
        self._con.commit()
        self._con.text_factory = sqlite3.OptimizedUnicode
        bot.register_callback("getquote", self.getquote)
        bot.register_callback("addquote", self.addquote)
        bot.register_callback("delquote", self.delquote)

    def getquote(self, bot, user, channel, text):
        s_text = text.split()
        if len(s_text) > 1:
            quotenumber = s_text[1]
            logging.debug("Trying to get quote number %s" % quotenumber)
            with self._con:
                q = self._con.execute("SELECT quote FROM quotes\
                    WHERE rowid = ?;", [quotenumber]).fetchall()
                if len(q) > 0:
                    bot.privmsg(channel, "[%s] %s" % (quotenumber, q[0][0]))
        else:
            bot.privmsg(channel, "%s: Bist du nur dumm, Junge?" % user)

    def addquote(self, bot, user, channel, text):
        s_text = text.split()
        if len(s_text) > 1:
            text = " ".join(s_text[1:])
            logging.debug("Adding quote: %s" % text)
            with self._con:
                c = self._con.execute("INSERT INTO quotes (quote) values (?);",
                        [text])
                bot.privmsg(channel, "New quote: %s" % c.lastrowid)
        else:
            bot.privmsg(channel, "%s: Bist du nur dumm, Junge?" % user)

    def delquote(self, bot, user, channel, text):
        s_text = text.split()
        if len(s_text) > 1:
            quotenumber = s_text[1]
            logging.debug("Deleting quote: %s" % quotenumber)
            with self._con:
                c = self._con.execute("DELETE FROM quotes where ROWID = (?);",
                    [quotenumber]).fetchall()
                self._con.commit()
        else:
            bot.privmsg(channel, "%s: Bist du nur dumm, Junge?" % user)
