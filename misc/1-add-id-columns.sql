-- Create a new quotes table
ALTER TABLE quotes RENAME TO quotes_backup;
ALTER TABLE authors RENAME TO author_backup;
-- Add proper new tables

CREATE TABLE author(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE);

CREATE TABLE IF NOT EXISTS quote(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quote TEXT,
        author INTEGER NOT NULL REFERENCES author(id));

INSERT INTO author (id, name)
    SELECT rowid, name
    FROM author_backup;

INSERT INTO quote (id, quote, author)
    SELECT q2.rowid, q2.quote, q2.author
    FROM quotes_backup q2;

DROP TABLE quotes_backup;
DROP TABLE author_backup;
