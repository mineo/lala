Installation
============


PyPI
----

Lala is available on the Python Package Index. This makes installing
it with `pip <https://pip.pypa.io/en/latest/>`_ as easy as::

    pip install lala

Git
---

If you want the latest code or even feel like contributing, the code is
available on `Github <https://github.com/mineo/lala>`_.

You can easily clone the code with git::

    git clone git://github.com/mineo/lala.git

Now you can start hacking on the code or install it system-wide::

    python2 setup.py install

Setup
-----

Setting up the bot is relatively easy: Simply copy the supplied example config
file from::

    /usr/share/lala/config.example

to either::

    /etc/lala.config

or::

    $XDG_CONFIG_HOME/lala/config

or (if the latter is not set)::

    $HOME/.lala/config

After that, you can modify the config file as you wish.

Starting the bot
----------------

Starting the bot is very easy as it installs a ``twistd`` plugin::

    twistd lala

For now, only a ``--verbose`` option is provided which makes the output written
to the log file more verbose.

Additionally, ``twistd`` itself offers a few options, use::

    twistd --help

to view them.
