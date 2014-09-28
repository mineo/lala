Updating
========

Some commits require a manual update of the SQLite databse used for the quotes.

The following is a list of those commits and the commands to run the update,
where ``<sqlite-file>`` is the path to the quote database file. Newer commits
appear first.

* 410ccde58bf6f635b121c0a5349dce5fd643679a (part of release 0.4)

  ``sqlite3 <sqlite-file> misc/2-add-votes-to-quotes.sql``

* a602b32dfa8aeb0d89b18275fe9e371199f3fd7c (part of release 0.4)

  ``sqlite3 <sqlite-file> misc/1-add-id-columns.sql``


* 44f8b476a1e28af60b5e21704b5c1eafd2f9bb54 (part of release 0.3)

  ``sqlite3 <sqlite-file> misc/0-add-author-to-quotes.sql``
