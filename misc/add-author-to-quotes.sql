-- Create the author table
CREATE TABLE authors(
    name TEXT NOT NULL UNIQUE);
-- Insert an "unknown" author for old quotes
INSERT INTO authors VALUES ("unknown");
-- Rename quotes to quotes_backup, add an author column and make that point to
-- "unknown". Afterwards, copy everything from quotes_backup to a new quotes
-- table
ALTER TABLE quotes RENAME TO quotes_backup;
ALTER TABLE quotes_backup ADD COLUMN
    author INTEGER;
CREATE TABLE quotes(
    quote TEXT,
    author INTEGER NOT NULL REFERENCES authors(rowid));
UPDATE quotes_backup SET author = (
    SELECT rowid
    FROM authors
    WHERE name = "unknown")
    WHERE author IS NULL;
INSERT INTO quotes (rowid, quote, author)
    SELECT q2.rowid, q2.quote, q2.author
    FROM quotes_backup q2;
DROP TABLE quotes_backup;
