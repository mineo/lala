lala bot
========

Dependencies
------------
* twisted
* python-daemon (optional, use **-n** to not daemonize)

Setup
-----
* Copy /usr/share/lala/config.example to either /etc/lala.config or
  $XDG_CONFIG_HOME/lala/config or (if and only if the latter is not set)
  $HOME/.lala/config
* Edit the file you just copied to your liking
* Use run-lala to start the bot
    * If you want debugging output, use **-d**

Update notice for version 0.2
-----------------------------
In version 0.2 the quotes plugin will also record the author a quote. To update
your database use **sqlite3 quotes.sqlite3 < misc/add-author-to-quotes.sql**.
