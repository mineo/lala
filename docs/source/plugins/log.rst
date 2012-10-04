Chatlogger
==========

The ``log`` plugin logs all received messages to a file. It also provides the
``last`` command that causes the bot to message the last few lines of the log.

Options
-------

- ``max_lines``
    The maximum number of lines to message upon the ``last`` command. Defaults
    to 30

- ``log_file``
    The location of the log file.

- ``max_log_days``
    The number of days for which logs are kept. Set this to zero to keep them
    indefinitely.
