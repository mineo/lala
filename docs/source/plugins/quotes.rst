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

- ``searchquote <text>``

  Search for a quote containing ``text``.

Options
-------

- ``max_quotes``

  The maximum number of quotes to print while doing a search from
  ``searchquote``. Defaults to 5
