lala bot
========

Dependencies
------------
* lurklib - You'll need at least version 0.8
* python-daemon

Setup
-----
* Copy /usr/share/lala/config.example to either /etc/lala.config or
  $XDG_CONFIG_HOME/lala/config or (if and only if the latter is not set)
  $HOME/.lala/config
* Edit the file you just copied to your liking
* Use run-lala to start the bot
    * If you want debugging output, use **-d**

TODO
----
* Automatic reconnect on connection loss
