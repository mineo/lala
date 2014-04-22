Quotes
======

The ``quotes`` plugin can be used to capture quotes in a database. It will also
print a quote containg the name of the joining person on every join.

It provides the following commands:

- ``addquote <quote>``

  Adds a new quote to the database

- ``delquote <quote id>``

  Admin only.

  Deletes the quote with the specified ID.

- ``getquote <quote id>``

  Get the quote with the specified ID.

- ``lastquote``

  Get the last inserted quote.

- ``randomquote``

  Retrieve a random quote.

- ``qdislike <quote id>``

  Dislikes the quote.

- ``qlike <quote id>``

  Likes the quote.

- ``qtop <limit>``

  Shows the ``limit`` (default: ``max_quotes``) quotes with the best rating.

- ``qflop <limit>``

  Shows the ``limit`` (default: ``max_quotes``) quotes with the worst rating.

- ``quotestats``

  Display some stats about the quote database.
  This is currently limited to the total number of quotes and the percentage
  of quotes per author.

- ``searchquote <text>``

  Search for a quote containing ``text``.

Options
-------

- ``database_path``

  The path to the SQLite database file. Defaults to ``~/.lala/quotes.sqlite3``.

- ``max_quotes``

  The maximum number of quotes to print when using ``searchquote`` or
  ``qtop``/``qflop``. Defaults to 5.
