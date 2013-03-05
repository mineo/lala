Fortune
=======

This plugin provides two commands, ``fortune`` and ``ofortune``, both of which
basically call the `fortune command <https://en.wikipedia.org/wiki/Fortune_(Unix)>`_
and post the result in the channel. In addition, ``ofortune`` supplies the
``-o`` option to ``fortune`` so that only offensive fortunes are chosen.

Options
-------

- ``fortune_files``

  The fortune file(s) to use. Defaults to ``fortunes``. This can be overridden
  when using either ``fortune`` or ``ofortune`` by adding the preferred fortune
  file after the command, like ``!fortune riddles``.

- ``fortune_path``

  The full path to the fortune binary. Defaults to ``/usr/bin/fortune``

