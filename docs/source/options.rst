Configuration file options
==========================

Both the basic configuration and the plugin configuration of Lala takes place
in a central configuration file.

The basic options are:

- server
    The server to connect to.

- port
    The port on which the server listens.

- nick
    The nick of the bot.

- admins
    A comma-separated list of people allowed to issue admin-only commands
    (like reconnect or quit) to the bot.

- nickserv_password
    Optional.

    The password which is used to identify with Nickserv.

- channels
    Optional.

    A comma-separated list of channels which are joined
    automatically after connection to the server.

- fallback_encoding
    Optional.

    Lala assumes all messages received are UTF-8 encoded. If
    that's not the case, this is the second encoding to try.

- plugins
    Optional.

    A comma-separated list of plugins to load at startup. The plugin "base"
    is always loaded, it contains basic commands like "help" and
    "reconnect".
