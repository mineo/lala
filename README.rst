Lala IRC Bot
============

.. image:: https://travis-ci.org/mineo/lala.svg?branch=master
    :target: https://travis-ci.org/mineo/lala

Dependencies
------------

* twisted

Setup
-----
* Copy /usr/share/lala/config.example to either /etc/lala.config or
  $XDG_CONFIG_HOME/lala/config or (if and only if the latter is not set)
  $HOME/.lala/config
* Edit the file you just copied to your liking
* Use twistd to start the bot::

      twistd lala

* If you want to get more verbose output in the log file, add the ``--verbose``
  option.

For more information about the setup, the available plugins and the API, read
the `documentation`_.

.. _documentation: https://lala.readthedocs.org/en/latest/
