lala bot
========

Dependencies
------------
Depends on lurklib, which can be found at https://github.com/mineo/lurklib
This includes some modifications / bugfixes by me

Setup
-----
* Copy *config.example* to *$XDG_CONFIG_HOME/lala/config*  or, if $XDG_CONFIG_HOME is not set, *$HOME/.lala/config* and edit it.
* Launch `run-lala.py` (takes an optional parameter `-d` for debugging purposes)
* Query the bot and send `!join #yourchannel` for it to actually join the
  channel (This can't be done atm on connecting because lurklib causes some
  weird errors)

TODO
----
* Implement settings for plugins
