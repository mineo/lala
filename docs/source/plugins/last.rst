Last Messages
=============

The ``last`` plugin saves the last messages in memory. It provides a ``last``
command to retrieve them.

Options
-------

- ``max_lines``
    The maximum number of lines to message upon the ``last`` command. Defaults
    to 30

- ``datetime_format``
    The format used to format the timestamps in the log. Have a look at the
    `strftime documentation`_ for all possible options. The default is
    ``%Y-%m-%d %H:%M:%S``.

.. _strftime documentation: http://docs.python.org/2/library/datetime.html?highlight=datetime#strftime-strptime-behavior
